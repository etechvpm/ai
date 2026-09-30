#!/usr/bin/env python3
"""Build offline bundles of the course.

    python tools/build_offline.py               # rebuild site/ + offline bundles
    python tools/build_offline.py --no-site     # reuse the existing site/ build

Outputs (into ``dist/``, which is NOT committed):

    dist/python-course-offline.html   one self-contained file: every module,
                                      every figure, CSS/JS/search index
                                      inlined.  Double-click it - no server,
                                      no network, works from file://.
    dist/python-course-site.zip       the multi-page site/ + the single file
    dist/python-course-full.zip       everything: notes, exercises, tools,
                                      site, single file, docs

The single-file build reuses tools/build_site.py for rendering, then patches
tools/assets/site.js so search reads the embedded index instead of fetching
``assets/search-index.json`` (fetch is blocked on file:// in most browsers),
and so search results link to in-page anchors.
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import markdown                                        # noqa: E402
from markdown.extensions.toc import TocExtension       # noqa: E402
from pygments.formatters import HtmlFormatter          # noqa: E402

import build_site as bs                                # noqa: E402

ROOT = bs.ROOT
NOTES = bs.NOTES
SITE = bs.OUT
DIST = os.path.join(ROOT, "dist")
ASSETS = os.path.join(HERE, "assets")

SKIP_DIRS = {"__pycache__", ".pytest_cache", ".venv", ".git", ".mypy_cache",
             ".ruff_cache", "dist"}


# --------------------------------------------------------------------------
# render every module exactly the way build_site.py does
# --------------------------------------------------------------------------
def render_pages() -> list[dict]:
    files = sorted(f for f in os.listdir(NOTES)
                   if f.endswith(".md") and not f.startswith("_"))
    pages: list[dict] = []
    for fname in files:
        with open(os.path.join(NOTES, fname), encoding="utf-8") as fh:
            raw = fh.read()
        meta, body = bs.parse_front_matter(raw)
        body = bs.convert_blocks(body)
        body = re.sub(r"!\[([^\]]*)\]\((figures/[^)]+)\)",
                      lambda m: bs.inline_figure(m.group(2), m.group(1)), body)
        md = markdown.Markdown(
            extensions=bs.MD_EXTENSIONS + [TocExtension(permalink=False,
                                                        toc_depth="2-3")],
            extension_configs=bs.MD_CONFIG)
        content = bs.inline_figures(md.convert(body))
        pages.append({
            "slug": meta.get("slug", fname[:-3]),
            "title": meta.get("title", fname[:-3]),
            "summary": meta.get("summary", ""),
            "order": int(meta.get("order", 999)),
            "level": meta.get("level", ""),
            "read": meta.get("read", ""),
            "tags": [t.strip() for t in meta.get("tags", "").split(",") if t],
            "content": content,
            "toc": getattr(md, "toc", ""),
        })
    pages.sort(key=lambda p: p["order"])
    return pages


def prefix_heading_ids(content: str, toc: str, prefix: str) -> tuple[str, str]:
    """Make heading ids unique across the whole single-file document.

    Only ids the page's own TOC points at are rewritten, so ids inside the
    inlined SVGs (markers, filters, gradients) keep working.
    """
    for hid in dict.fromkeys(re.findall(r'href="#([^"]+)"', toc)):
        content = re.sub(r'\bid="%s"' % re.escape(hid),
                         'id="%s--%s"' % (prefix, hid), content)
        toc = toc.replace('href="#%s"' % hid, 'href="#%s--%s"' % (prefix, hid))
    return content, toc


# --------------------------------------------------------------------------
# the single-file document
# --------------------------------------------------------------------------
EXTRA_CSS = """
/* ---- offline bundle extras ---- */
.offline-note { max-width: 860px; margin: 0 0 18px; padding: 10px 14px;
  border: 1px solid var(--line); border-left: 4px solid var(--accent);
  border-radius: 10px; background: var(--bg-elev); color: var(--ink-2);
  font-size: 13px; }
.offline-note code { font-size: 12px; }
article.page + article.page { margin-top: 44px; padding-top: 26px;
  border-top: 2px solid var(--line); }
details.page-toc { margin: 0 0 18px; padding: 8px 14px; border: 1px solid
  var(--line); border-radius: 10px; background: var(--bg-sunk); }
details.page-toc > summary { cursor: pointer; font-weight: 600; font-size:
  13px; color: var(--ink-2); }
details.page-toc .toc { margin-top: 8px; }
.pager a[href^="#"] { text-decoration: none; }
@media print {
  .topbar, .sidebar, .offline-note, .copy-btn, .pager { display: none !important; }
  .layout { display: block; }
  article.page { max-width: none; border: 0; margin: 0; padding: 0; }
  details.page-toc { display: none; }
  pre { white-space: pre-wrap; }
}
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Python, From Zero to Industry &middot; complete offline edition</title>
<meta name="description" content="All {n} modules of the course in one self-contained file: notes, diagrams, tables and exercises. No network needed.">
<style>
{css}
{pygments}
{extra}
</style>
</head>
<body>
<header class="topbar">
  <button class="icon-btn" id="menu-btn" aria-label="Toggle navigation">&#9776;</button>
  <a class="brand" href="#index">
    <span class="logo">Py</span>
    <span class="brand-txt">Python&nbsp;&middot;&nbsp;From&nbsp;Zero&nbsp;to&nbsp;Industry</span>
  </a>
  <div class="spacer"></div>
  <div class="search-wrap">
    <input id="search" type="search" placeholder="Search all modules&hellip;  ( / )" autocomplete="off">
    <div id="search-results" hidden></div>
  </div>
  <button class="icon-btn" id="theme-btn" aria-label="Toggle dark mode">&#9790;</button>
</header>
<div class="layout">
  <aside class="sidebar" id="sidebar">{sidebar}</aside>
  <main class="main">
    <div class="offline-note">
      Offline edition &middot; every module in one file &middot; search, dark mode
      and copy buttons work without a network. Print or <em>Save as PDF</em>
      (Ctrl/Cmd&nbsp;P) for a paper copy. Sources, exercises and the multi-page
      site live in the repository: <code>notes/</code>, <code>exercises/</code>,
      <code>site/</code>.
    </div>
{sections}
  </main>
</div>
<script id="search-data" type="application/json">{index}</script>
<script>
{js}
</script>
</body>
</html>
"""


def build_sidebar(pages: list[dict]) -> str:
    out = ['<div class="side-group"><a class="side-link home" '
           'href="#index">Course home</a></div>',
           '<div class="side-group"><div class="side-title">Modules</div>']
    for p in pages:
        if p["slug"] == "index":
            continue
        out.append(f'<a class="side-link" href="#{p["slug"]}">'
                   f'<span class="num">{p["order"]:02d}</span>'
                   f'<span class="ttl">{html.escape(p["title"])}</span></a>')
    out.append("</div>")
    return "\n".join(out)


def build_sections(pages: list[dict]) -> str:
    parts = []
    for i, p in enumerate(pages):
        prevp = pages[i - 1] if i else None
        nextp = pages[i + 1] if i + 1 < len(pages) else None
        content, toc = prefix_heading_ids(p["content"], p["toc"], p["slug"])
        # cross-page links (e.g. the module map on the home page) become anchors
        content = re.sub(r'href="([A-Za-z0-9_-]+)\.html"', r'href="#\1"',
                         content)
        nav = '<nav class="pager">'
        nav += (f'<a class="prev" href="#{prevp["slug"]}"><span>&larr; previous'
                f'</span><strong>{html.escape(prevp["title"])}</strong></a>'
                if prevp else '<span class="prev"></span>')
        nav += (f'<a class="next" href="#{nextp["slug"]}"><span>next &rarr;'
                f'</span><strong>{html.escape(nextp["title"])}</strong></a>'
                if nextp else '<span class="next"></span>')
        nav += "</nav>"
        toc_block = (f'<details class="page-toc"><summary>On this page'
                     f'</summary>{toc}</details>' if toc else "")
        parts.append(
            f'    <article class="page" id="{p["slug"]}">\n'
            f'      <div class="page-meta">{bs.chips(p)}</div>\n'
            f'      {toc_block}\n'
            f'      {content}\n'
            f'      {nav}\n'
            f'    </article>')
    return "\n".join(parts)


def patched_js() -> str:
    with open(os.path.join(ASSETS, "site.js"), encoding="utf-8") as fh:
        js = fh.read()
    fetch_src = 'fetch("assets/search-index.json")'
    fetch_new = ('Promise.resolve({ json: function () {'
                 ' return JSON.parse(document.getElementById("search-data")'
                 '.textContent); } })')
    link_src = """'<a href="' + h.slug + '.html">"""
    link_new = """'<a href="#' + h.slug + '">"""
    for src, new in ((fetch_src, fetch_new), (link_src, link_new)):
        if src not in js:
            raise SystemExit(f"build_offline: site.js changed - cannot patch "
                             f"{src!r}; update tools/build_offline.py")
        js = js.replace(src, new)
    return js


def pygments_css() -> str:
    light = HtmlFormatter(style="default").get_style_defs(".codehilite")
    dark = HtmlFormatter(style="one-dark").get_style_defs(".codehilite")
    return (light + '\n[data-theme="dark"] {\n' + dark + "\n}")


def build_single_file(pages: list[dict], path: str) -> None:
    with open(os.path.join(ASSETS, "site.css"), encoding="utf-8") as fh:
        css = fh.read()
    idx = []
    for p in pages:
        text = re.sub(r"<[^>]+>", " ", p["content"])
        text = html.unescape(re.sub(r"\s+", " ", text))
        idx.append({"slug": p["slug"], "title": p["title"],
                    "order": p["order"], "body": text})
    payload = json.dumps(idx).replace("<", "\\u003c")
    doc = TEMPLATE.format(n=len(pages), css=css, pygments=pygments_css(),
                          extra=EXTRA_CSS, sidebar=build_sidebar(pages),
                          sections=build_sections(pages), index=payload,
                          js=patched_js())
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(doc)


# --------------------------------------------------------------------------
# zips
# --------------------------------------------------------------------------
def _add_tree(zf: zipfile.ZipFile, src: str, arc: str) -> int:
    added = 0
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if fn.endswith((".pyc", ".pyo")):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, src)
            zf.write(full, os.path.join(arc, rel))
            added += 1
    return added


def make_zips(single_html: str, offline_md: str) -> list[str]:
    out = []
    site_zip = os.path.join(DIST, "python-course-site.zip")
    with zipfile.ZipFile(site_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        _add_tree(zf, SITE, "site")
        zf.write(single_html, "python-course-offline.html")
        zf.write(offline_md, "OFFLINE.md")
    out.append(site_zip)

    full_zip = os.path.join(DIST, "python-course-full.zip")
    with zipfile.ZipFile(full_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for top in ("notes", "exercises", "tools", "site"):
            _add_tree(zf, os.path.join(ROOT, top), top)
        for fn in ("README.md", "OFFLINE.md", "pyproject.toml", ".gitignore"):
            src = os.path.join(ROOT, fn)
            if os.path.exists(src):
                zf.write(src, fn)
        zf.write(single_html, "python-course-offline.html")
    out.append(full_zip)
    return out


def main(argv: list[str]) -> int:
    if "--no-site" not in argv:
        bs.build()
    os.makedirs(DIST, exist_ok=True)
    pages = render_pages()
    single = os.path.join(DIST, "python-course-offline.html")
    build_single_file(pages, single)
    offline_md = os.path.join(ROOT, "OFFLINE.md")
    zips = make_zips(single, offline_md)

    def mb(p: str) -> str:
        return f"{os.path.getsize(p) / 1024 / 1024:5.2f} MiB"

    print(f"offline edition: {len(pages)} modules in one file")
    print(f"  {mb(single)}  {os.path.relpath(single, ROOT)}")
    for z in zips:
        print(f"  {mb(z)}  {os.path.relpath(z, ROOT)}")
    print("open the HTML directly (double-click), or unzip and serve site/:")
    print("  python3 -m http.server 8000 --directory site")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
