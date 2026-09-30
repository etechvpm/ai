#!/usr/bin/env python3
"""Build the course website from the Markdown notes.

    python tools/build_site.py            # rebuild site/ from notes/

Pipeline
--------
notes/*.md  --(front-matter + custom blocks)-->  HTML fragments
fragments   --(python-markdown + pygments)----->  content HTML
content     --(inline SVG figures)------------->  page HTML
pages       --(template: sidebar, TOC, search)--> site/*.html

Custom block syntax used inside the notes (deliberately NOT raw HTML, so the
Markdown sources stay clean and readable on GitHub):

    ::: kind "Title"
    indented body ...
    :::
        -> admonition (python-markdown ``admonition`` extension)

    [[exercise tier="Beginner" id="ex-02-01" file="exercises/02_basics.py"]]
    ...markdown...
    [[/exercise]]
        -> a styled exercise card with tier chip and auto-check hints

    [[solution]]
    ...markdown...
    [[/solution]]
        -> collapsible <details> with the worked solution

    [[tip]] ... [[/tip]]  [[warn]] ...  [[/warn]]  [[industry]] ...
        -> one-line-to-block shortcuts for callouts

Figures referenced as  ![caption](figures/x.svg)  are INLINED into the page so
they inherit the site theme (light + dark).
"""

from __future__ import annotations

import html
import json
import os
import re
import shutil
import sys

import markdown
from markdown.extensions.toc import TocExtension
from pygments.formatters import HtmlFormatter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES = os.path.join(ROOT, "notes")
OUT = os.path.join(ROOT, "site")
FIG = os.path.join(NOTES, "figures")

MD_EXTENSIONS = ["fenced_code", "tables", "attr_list", "admonition",
                 "sane_lists", "def_list", "codehilite", "md_in_html",
                 "smarty"]
MD_CONFIG = {
    "codehilite": {"guess_lang": False, "css_class": "codehilite",
                   "noclasses": False, "use_pygments": True},
    "toc": {"toc_depth": "2-3", "permalink": False},
}

# --------------------------------------------------------------------------
# front matter
# --------------------------------------------------------------------------
FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


def parse_front_matter(text: str) -> tuple[dict, str]:
    m = FM_RE.match(text)
    if not m:
        return {}, text
    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, text[m.end():]


# --------------------------------------------------------------------------
# custom blocks -> markdown/HTML the extensions understand
# --------------------------------------------------------------------------
def convert_blocks(md: str) -> str:
    # ::: kind "Title" ... :::  -> admonition
    def admon(m: re.Match) -> str:
        kind, title, body = m.group(1), m.group(2) or "", m.group(3)
        lines = [l[4:] if l.startswith("    ") else l
                 for l in body.splitlines()]
        head = f'!!! {kind}' + (f' "{title}"' if title else "")
        return head + "\n" + "\n".join("    " + l if l.strip() else ""
                                       for l in lines) + "\n"
    md = re.sub(r'^:::\s*(\w+)\s*(?:"([^"]*)")?\s*\n(.*?)^:::\s*$', admon,
                md, flags=re.S | re.M)

    # [[exercise ...]] ... [[/exercise]]
    def ex(m: re.Match) -> str:
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        tier = attrs.get("tier", "Practice")
        eid = attrs.get("id", "")
        fname = attrs.get("file", "")
        inner = render_inner(m.group(2))
        head = ('<div class="exercise tier-' + tier.lower() + '" '
                f'data-tier="{html.escape(tier)}">')
        meta = f'<div class="ex-head"><span class="ex-tier">{html.escape(tier)}</span>'
        if eid:
            meta += f'<span class="ex-id">{html.escape(eid)}</span>'
        meta += "</div>"
        foot = ""
        if fname:
            short = os.path.basename(fname)
            foot = (f'<div class="ex-file"><code>{html.escape(short)}</code>'
                    f' &middot; verify with <code>pytest {html.escape(fname)}</code></div>')
        return head + meta + inner + foot + "</div>"
    md = re.sub(r'^\[\[exercise([^\]]*)\]\]\s*\n(.*?)^\[\[/exercise\]\]\s*$',
                ex, md, flags=re.S | re.M)

    # [[solution]] ... [[/solution]]  -> collapsible
    def sol(m: re.Match) -> str:
        title = m.group(1).strip() or "Show worked solution"
        inner = render_inner(m.group(2))
        return (f'<details class="solution"><summary>{html.escape(title)}'
                f"</summary>{inner}</details>")
    md = re.sub(r'^\[\[solution([^\]]*)\]\]\s*\n(.*?)^\[\[/solution\]\]\s*$',
                sol, md, flags=re.S | re.M)

    # one-line callout shortcuts
    for kind, cls in (("tip", "tip"), ("warn", "warning"),
                      ("industry", "industry"), ("gotcha", "gotcha")):
        md = re.sub(rf'^\[\[{kind}\]\]\s*(.+?)\s*\[\[/{kind}\]\]\s*$',
                    lambda m, c=cls: f'<div class="callout {c}">'
                                     f"{render_inner(m.group(1))}</div>",
                    md, flags=re.S | re.M)
    return md


def render_inner(text: str) -> str:
    """Render a chunk of markdown to HTML on its own."""
    text = re.sub(r"!\[([^\]]*)\]\((figures/[^)]+)\)",
                  lambda m: inline_figure(m.group(2), m.group(1)), text)
    return markdown.markdown(text, extensions=MD_EXTENSIONS,
                             extension_configs=MD_CONFIG)


# --------------------------------------------------------------------------
# figures: inline the SVG so it inherits the theme
# --------------------------------------------------------------------------
def inline_figure(rel: str, alt: str) -> str:
    path = os.path.join(NOTES, rel)
    if not os.path.exists(path):
        return f'<p class="missing-figure">missing figure: {rel}</p>'
    with open(path, encoding="utf-8") as fh:
        svg = fh.read()
    svg = svg.replace("<svg ", '<svg class="dg" ', 1)
    cap = (f'<figcaption>{html.escape(alt)}</figcaption>' if alt else "")
    return f'<figure class="diagram">{svg}{cap}</figure>'


IMG_RE = re.compile(r'<img alt="([^"]*)" src="(figures/[^"]+)"[^>]*/?>')


def inline_figures(htmltext: str) -> str:
    return IMG_RE.sub(lambda m: inline_figure(m.group(2), m.group(1)),
                      htmltext)


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------
def build() -> None:
    shutil.rmtree(OUT, ignore_errors=True)
    for sub in ("assets/css", "assets/js", "assets/diagrams"):
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)

    files = sorted(f for f in os.listdir(NOTES)
                   if f.endswith(".md") and not f.startswith("_"))
    pages: list[dict] = []
    for fname in files:
        with open(os.path.join(NOTES, fname), encoding="utf-8") as fh:
            raw = fh.read()
        meta, body = parse_front_matter(raw)
        body = convert_blocks(body)
        body = re.sub(r"!\[([^\]]*)\]\((figures/[^)]+)\)",
                      lambda m: inline_figure(m.group(2), m.group(1)), body)
        md = markdown.Markdown(extensions=MD_EXTENSIONS + [TocExtension(
            permalink=False, toc_depth="2-3")],
            extension_configs=MD_CONFIG)
        content = md.convert(body)
        content = inline_figures(content)
        pages.append({
            "file": fname,
            "slug": meta.get("slug", fname[:-3]),
            "title": meta.get("title", fname[:-3]),
            "summary": meta.get("summary", ""),
            "order": int(meta.get("order", 999)),
            "read": meta.get("read", ""),
            "level": meta.get("level", ""),
            "tags": [t.strip() for t in meta.get("tags", "").split(",") if t],
            "content": content,
            "toc": getattr(md, "toc", ""),
        })
    pages.sort(key=lambda p: p["order"])

    for p in pages:
        shutil.copytree if False else None
    write_pages(pages)
    write_assets()
    write_search(pages)
    print(f"built {len(pages)} pages -> {OUT}")


def write_pages(pages: list[dict]) -> None:
    css = "assets/css/site.css"
    js = "assets/js/site.js"
    for i, p in enumerate(pages):
        prevp = pages[i - 1] if i else None
        nextp = pages[i + 1] if i + 1 < len(pages) else None
        nav = '<nav class="pager">'
        nav += (f'<a class="prev" href="{prevp["slug"]}.html">'
                f'<span>&larr; previous</span><strong>{prevp["title"]}</strong></a>'
                if prevp else '<span class="prev"></span>')
        nav += (f'<a class="next" href="{nextp["slug"]}.html">'
                f'<span>next &rarr;</span><strong>{nextp["title"]}</strong></a>'
                if nextp else '<span class="next"></span>')
        nav += "</nav>"

        sidebar = ['<div class="side-group"><a class="side-link home" '
                   f'href="index.html">Course home</a></div>',
                   '<div class="side-group"><div class="side-title">Modules</div>']
        for q in pages:
            if q["slug"] == "index":
                continue
            act = " active" if q["slug"] == p["slug"] else ""
            sidebar.append(
                f'<a class="side-link{act}" href="{q["slug"]}.html">'
                f'<span class="num">{q["order"]:02d}</span>'
                f'<span class="ttl">{html.escape(q["title"])}</span></a>')
        sidebar.append("</div>")

        doc = TEMPLATE.format(
            title=html.escape(p["title"]),
            css=css, js=js,
            sidebar="\n".join(sidebar),
            toc=p["toc"] or "",
            content=p["content"],
            nav=nav,
            meta_chips=chips(p),
            order=p["order"],
        )
        with open(os.path.join(OUT, p["slug"] + ".html"), "w",
                  encoding="utf-8") as fh:
            fh.write(doc)


def chips(p: dict) -> str:
    out = []
    if p["level"]:
        out.append(f'<span class="chip lvl">{html.escape(p["level"])}</span>')
    if p["read"]:
        out.append(f'<span class="chip read">{html.escape(p["read"])}</span>')
    for t in p["tags"]:
        out.append(f'<span class="chip tag">{html.escape(t)}</span>')
    return "".join(out)


def write_search(pages: list[dict]) -> None:
    idx = []
    for p in pages:
        text = re.sub(r"<[^>]+>", " ", p["content"])
        text = html.unescape(re.sub(r"\s+", " ", text))
        idx.append({"slug": p["slug"], "title": p["title"],
                    "order": p["order"], "body": text})
    with open(os.path.join(OUT, "assets", "search-index.json"), "w",
              encoding="utf-8") as fh:
        json.dump(idx, fh)


def write_assets() -> None:
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    for fn in ("site.css", "site.js"):
        src = os.path.join(here, fn)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(OUT, "assets",
                                          "css" if fn.endswith("css") else "js",
                                          fn))
    # pygments themes for both modes, scoped
    light = HtmlFormatter(style="default").get_style_defs(".codehilite")
    dark = HtmlFormatter(style="one-dark").get_style_defs(".codehilite")
    with open(os.path.join(OUT, "assets", "css", "pygments.css"), "w",
              encoding="utf-8") as fh:
        fh.write("/* light theme (default) */\n" + light + "\n\n")
        fh.write("/* dark theme */\n[data-theme=\"dark\"] {\n" + dark + "\n}\n")


TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} &middot; Python, From Zero to Industry</title>
<meta name="description" content="Deep, visual Python course notes: definitions, syntax, examples, industry-level detail, comparison tables, diagrams and auto-checked exercises.">
<link rel="stylesheet" href="{css}">
<link rel="stylesheet" href="assets/css/pygments.css">
</head>
<body>
<header class="topbar">
  <button class="icon-btn" id="menu-btn" aria-label="Toggle navigation">&#9776;</button>
  <a class="brand" href="index.html">
    <span class="logo">Py</span>
    <span class="brand-txt">Python&nbsp;&middot;&nbsp;From&nbsp;Zero&nbsp;to&nbsp;Industry</span>
  </a>
  <div class="spacer"></div>
  <div class="search-wrap">
    <input id="search" type="search" placeholder="Search the notes&hellip;  ( / )" autocomplete="off">
    <div id="search-results" hidden></div>
  </div>
  <button class="icon-btn" id="theme-btn" aria-label="Toggle dark mode">&#9790;</button>
</header>
<div class="layout">
  <aside class="sidebar" id="sidebar">{sidebar}</aside>
  <main class="main">
    <article class="page">
      <div class="page-meta">{meta_chips}</div>
      {content}
      {nav}
      <footer class="foot">Python, From Zero to Industry &middot; editable Markdown sources live in <code>notes/</code>, figures regenerate with <code>python tools/make_diagrams.py</code>, this site rebuilds with <code>python tools/build_site.py</code>.</footer>
    </article>
    <aside class="toc-col">
      <div class="toc-title">On this page</div>
      <div class="toc">{toc}</div>
    </aside>
  </main>
</div>
<script src="{js}"></script>
</body>
</html>
"""


if __name__ == "__main__":
    sys.exit(build())
