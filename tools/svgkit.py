"""
svgkit -- a tiny, dependency-free SVG drawing kit.

Used by tools/make_diagrams.py to generate every figure in the course.

Design rules
------------
1.  Every colour is emitted as ``var(--token, <light fallback>)`` so the *same*
    file looks right in three contexts:
      * inlined into the course website (light + dark theme, vars supplied),
      * rendered by GitHub / any Markdown viewer (fallbacks used),
      * opened standalone in a browser.
2.  Text is drawn with a font stack that exists everywhere; no external fonts,
    so diagrams never render with broken glyphs offline.
3.  Coordinates are in a "logical" space; the root <svg> carries a viewBox and
    width:100% so figures scale to any container.
"""

from __future__ import annotations

import html
from dataclasses import dataclass, field

FONT = ("'Segoe UI', 'Inter', system-ui, -apple-system, Roboto, "
        "'Helvetica Neue', Arial, sans-serif")
MONO = ("'JetBrains Mono', 'Cascadia Code', 'Fira Code', Consolas, "
        "'SF Mono', Menlo, monospace")

# ---------------------------------------------------------------------------
# Palette.  key -> (css-variable-name, light-mode fallback)
# ---------------------------------------------------------------------------
PALETTE: dict[str, tuple[str, str]] = {
    # surfaces
    "bg":        ("--dg-bg",        "#ffffff"),
    "panel":     ("--dg-panel",     "#f8fafc"),
    "panel2":    ("--dg-panel2",    "#eef2f7"),
    "line":      ("--dg-line",      "#cbd5e1"),
    "ink":       ("--dg-ink",       "#0f172a"),
    "muted":     ("--dg-muted",     "#64748b"),
    # accents
    "blue":      ("--dg-blue",      "#2563eb"),
    "bluebg":    ("--dg-bluebg",    "#dbeafe"),
    "green":     ("--dg-green",     "#059669"),
    "greenbg":   ("--dg-greenbg",   "#d1fae5"),
    "amber":     ("--dg-amber",     "#d97706"),
    "amberbg":   ("--dg-amberbg",   "#fef3c7"),
    "red":       ("--dg-red",       "#dc2626"),
    "redbg":     ("--dg-redbg",     "#fee2e2"),
    "violet":    ("--dg-violet",    "#7c3aed"),
    "violetbg":  ("--dg-violetbg",  "#ede9fe"),
    "slate":     ("--dg-slate",     "#475569"),
    "slatebg":   ("--dg-slatebg",   "#e2e8f0"),
    "cyan":      ("--dg-cyan",      "#0891b2"),
    "cyanbg":    ("--dg-cyanbg",    "#cffafe"),
}


def c(name: str | None) -> str:
    """Resolve a palette key to a CSS colour value.

    Accepts a palette key ('blue'), the literal 'none', None, or any raw CSS
    colour, so callers can never produce an invalid fill/stroke.
    """
    if name is None or name == "none":
        return "none"
    if name in PALETTE:
        var, fallback = PALETTE[name]
        return f"var({var}, {fallback})"
    return name


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


@dataclass
class TextOpts:
    size: int = 13
    weight: str = "400"
    anchor: str = "middle"        # start | middle | end
    color: str = "ink"
    mono: bool = False
    italic: bool = False
    spacing: float | None = None


@dataclass
class BoxOpts:
    fill: str = "panel"
    stroke: str = "line"
    text_color: str = "ink"
    rx: int = 8
    sw: float = 1.6
    dashed: bool = False
    size: int = 13
    weight: str = "600"
    mono: bool = False
    shadow: bool = True


class SVG:
    """Accumulates SVG elements and renders a complete document."""

    def __init__(self, w: int, h: int, *, title: str = "", pad: int = 0):
        self.w = w
        self.h = h
        self.title = title
        self.body: list[str] = []
        self.defs: list[str] = []
        self._markers: set[str] = set()
        self._gradients: set[str] = set()
        if pad:
            self.body.append(
                f'<rect x="0" y="0" width="{w}" height="{h}" rx="14" '
                f'fill="{c("bg")}"/>')

    # -- low level ---------------------------------------------------------
    def raw(self, s: str) -> None:
        self.body.append(s)

    def group(self, s: str) -> None:
        """Alias kept for readability at call sites."""
        self.body.append(s)

    # -- markers -----------------------------------------------------------
    def _marker(self, color: str, mid: str) -> str:
        if mid in self._markers:
            return mid
        self._markers.add(mid)
        self.defs.append(
            f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{c(color)}"/></marker>')
        return mid

    def _shadow(self) -> str:
        if "dgShadow" not in self._gradients:
            self._gradients.add("dgShadow")
            self.defs.append(
                '<filter id="dgShadow" x="-20%" y="-20%" width="140%" '
                'height="140%"><feDropShadow dx="0" dy="1.5" stdDeviation="2" '
                f'flood-color="#0f172a" flood-opacity="0.13"/></filter>')
        return "dgShadow"

    # -- primitives --------------------------------------------------------
    def text(self, x: float, y: float, s: str, o: TextOpts | None = None,
             *, opacity: float | None = None) -> None:
        o = o or TextOpts()
        fam = MONO if o.mono else FONT
        extra = f' opacity="{opacity}"' if opacity else ""
        ls = (f' letter-spacing="{o.spacing}"' if o.spacing is not None
              else "")
        style = "italic" if o.italic else "normal"
        self.body.append(
            f'<text x="{x}" y="{y}" text-anchor="{o.anchor}" '
            f'font-family="{fam}" font-size="{o.size}" '
            f'font-weight="{o.weight}" font-style="{style}" '
            f'fill="{c(o.color)}"{extra}{ls}>{esc(s)}</text>')

    def mtext(self, x: float, y: float, lines: list[str],
              o: TextOpts | None = None, *, lh: int | None = None) -> None:
        """Multi-line text; y is the baseline of the FIRST line."""
        o = o or TextOpts()
        lh = lh or int(round(o.size * 1.32))
        for i, line in enumerate(lines):
            self.text(x, y + i * lh, line, o)

    def rect(self, x: float, y: float, w: float, h: float, *,
             fill: str | None = "panel", stroke: str | None = "line",
             rx: int = 8, sw: float = 1.6, dashed: bool = False,
             shadow: bool = False, opacity: float | None = None) -> None:
        d = ' stroke-dasharray="6 4"' if dashed else ""
        st = f' stroke="{c(stroke)}" stroke-width="{sw}"' if stroke else ""
        op = f' opacity="{opacity}"' if opacity else ""
        sh = f' filter="url(#{self._shadow()})"' if shadow else ""
        fl = 'fill="none"' if fill is None else f'fill="{c(fill)}"'
        self.body.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'{fl}{st}{d}{op}{sh}/>')

    def circle(self, cx: float, cy: float, r: float, *, fill: str = "blue",
               stroke: str | None = None, sw: float = 1.5) -> None:
        st = f' stroke="{c(stroke)}" stroke-width="{sw}"' if stroke else ""
        self.body.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c(fill)}"{st}/>')

    def line(self, x1: float, y1: float, x2: float, y2: float, *,
             color: str = "line", sw: float = 1.8, dashed: bool = False,
             arrow: bool = False, arrow_start: bool = False) -> None:
        d = ' stroke-dasharray="5 4"' if dashed else ""
        mk = ""
        if arrow:
            mk += f' marker-end="url(#{self._marker(color, "ar" + color)})"'
        if arrow_start:
            mk += f' marker-start="url(#{self._marker(color, "ar" + color)})"'
        self.body.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{c(color)}" stroke-width="{sw}"{d}{mk}/>')

    def path(self, d: str, *, color: str = "line", sw: float = 1.8,
             fill: str | None = None, dashed: bool = False,
             arrow: bool = False) -> None:
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        mk = (f' marker-end="url(#{self._marker(color, "ar" + color)})"'
              if arrow else "")
        f = f' fill="{c(fill)}"' if fill else ' fill="none"'
        self.body.append(
            f'<path d="{d}" stroke="{c(color)}" stroke-width="{sw}"'
            f'{dash}{f}{mk} stroke-linecap="round"/>')

    def poly(self, pts: list[tuple[float, float]], *, color: str = "line",
             sw: float = 1.8, arrow: bool = False, dashed: bool = False,
             fill: str | None = None, rounded: bool = True) -> None:
        d = "M " + " L ".join(f"{x},{y}" for x, y in pts)
        self.path(d, color=color, sw=sw, fill=fill, dashed=dashed,
                  arrow=arrow)

    def elbow(self, x1: float, y1: float, x2: float, y2: float, *,
              color: str = "line", sw: float = 1.8, arrow: bool = True,
              bend: str = "h", dashed: bool = False) -> None:
        """Right-angled connector. bend='h' -> horizontal first."""
        if bend == "h":
            pts = [(x1, y1), (x2, y1), (x2, y2)]
        else:
            pts = [(x1, y1), (x1, y2), (x2, y2)]
        self.poly(pts, color=color, sw=sw, arrow=arrow, dashed=dashed)

    # -- composites --------------------------------------------------------
    def box(self, x: float, y: float, w: float, h: float,
            label: str | list[str] = "", sub: str | list[str] = "", *,
            o: BoxOpts | None = None, valign: str = "center") -> None:
        """Rounded rect with a centred label and optional sub-caption."""
        o = o or BoxOpts()
        self.rect(x, y, w, h, fill=o.fill, stroke=o.stroke, rx=o.rx,
                  sw=o.sw, dashed=o.dashed, shadow=o.shadow)
        lines = [label] if isinstance(label, str) else list(label)
        subs = [sub] if isinstance(sub, str) else list(sub)
        lines = [l for l in lines if l != ""]
        subs = [s for s in subs if s != ""]
        to = TextOpts(size=o.size, weight=o.weight, color=o.text_color,
                      mono=o.mono)
        so = TextOpts(size=max(9, o.size - 3), weight="400",
                      color="muted", mono=False)
        lh_t = int(round(to.size * 1.32))
        lh_s = int(round(so.size * 1.35))
        total = len(lines) * lh_t + len(subs) * lh_s
        if valign == "center":
            top = y + (h - total) / 2 + to.size
        else:
            top = y + 10 + to.size
        for i, l in enumerate(lines):
            self.text(x + w / 2, top + i * lh_t, l, to)
        sy = top + len(lines) * lh_t - (lh_t - so.size) * 0.35
        for i, s in enumerate(subs):
            self.text(x + w / 2, sy + i * lh_s + 2, s, so)

    def chip(self, x: float, y: float, label: str, *, fill: str = "bluebg",
             text: str = "blue", size: int = 11, pad: float = 8.0,
             h: int = 22) -> float:
        """Pill-shaped label. Returns the width it occupied."""
        w = max(28, len(label) * size * 0.60 + pad * 2)
        self.rect(x, y, w, h, fill=fill, stroke=None, rx=h / 2)
        self.text(x + w / 2, y + h / 2 + size * 0.36, label,
                  TextOpts(size=size, weight="600", color=text))
        return w

    def badge(self, x: float, y: float, label: str, *, fill: str = "blue",
              text: str = "bg", size: int = 10) -> float:
        return self.chip(x, y, label, fill=fill, text=text, size=size, h=19)

    def panel(self, x: float, y: float, w: float, h: float, title: str = "",
              *, fill: str = "panel", stroke: str = "line",
              title_color: str = "slate", dashed: bool = False) -> None:
        self.rect(x, y, w, h, fill=fill, stroke=stroke, rx=10,
                  dashed=dashed)
        if title:
            self.text(x + 14, y + 20, title,
                      TextOpts(size=11.5, weight="700", anchor="start",
                               color=title_color, spacing=0.6))

    def heading(self, x: float, y: float, s: str, *, size: int = 17,
                anchor: str = "middle", color: str = "ink") -> None:
        self.text(x, y, s, TextOpts(size=size, weight="700", anchor=anchor,
                                    color=color))

    def caption(self, x: float, y: float, s: str, *, anchor: str = "middle",
                size: int = 11.5) -> None:
        self.text(x, y, s, TextOpts(size=size, anchor=anchor, color="muted",
                                    italic=True))

    def arrowlabel(self, x: float, y: float, s: str, *, color: str = "slate",
                   size: int = 11, anchor: str = "middle",
                   bg: bool = True) -> None:
        if bg:
            w = len(s) * size * 0.58 + 8
            self.rect(x - w / 2 if anchor == "middle" else x - 4,
                      y - size * 0.95, w, size * 1.5, fill="bg",
                      stroke=None, rx=4)
        self.text(x, y, s, TextOpts(size=size, weight="600", anchor=anchor,
                                    color=color))

    # -- render ------------------------------------------------------------
    def render(self) -> str:
        defs = ("\n  <defs>\n    " + "\n    ".join(self.defs) + "\n  </defs>"
                if self.defs else "")
        t = (f"<title>{esc(self.title)}</title>" if self.title else "")
        style = (
            "<style>"
            f"text {{ font-family: {FONT}; }}"
            "svg { color-scheme: light dark; }"
            "</style>")
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} '
            f'{self.h}" width="{self.w}" height="{self.h}" role="img" '
            f'preserveAspectRatio="xMidYMid meet" '
            f'style="max-width:100%;height:auto">{t}{style}{defs}\n'
            + "\n".join(self.body)
            + "\n</svg>\n")

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.render())


# ---------------------------------------------------------------------------
# Reusable layout helpers for the specific diagram families used in the course
# ---------------------------------------------------------------------------
def flowchart_step(svg: SVG, x: float, y: float, w: float, h: float,
                   label: str, sub: str = "", *, kind: str = "blue",
                   shape: str = "rect", size: int = 13) -> None:
    styles = {
        "blue":   BoxOpts(fill="bluebg",   stroke="blue",   text_color="ink"),
        "green":  BoxOpts(fill="greenbg",  stroke="green",  text_color="ink"),
        "amber":  BoxOpts(fill="amberbg",  stroke="amber",  text_color="ink"),
        "red":    BoxOpts(fill="redbg",    stroke="red",    text_color="ink"),
        "violet": BoxOpts(fill="violetbg", stroke="violet", text_color="ink"),
        "slate":  BoxOpts(fill="slatebg",  stroke="slate",  text_color="ink"),
        "cyan":   BoxOpts(fill="cyanbg",   stroke="cyan",   text_color="ink"),
        "plain":  BoxOpts(fill="panel",    stroke="line",   text_color="ink"),
    }
    o = styles[kind]
    o = BoxOpts(**{**o.__dict__, "size": size})
    if shape == "diamond":
        cx, cy = x + w / 2, y + h / 2
        pts = [(cx, y), (x + w, cy), (cx, y + h), (x, cy)]
        svg.poly(pts, color=o.stroke, sw=1.8, fill=o.fill, arrow=False)
        svg.mtext(cx, cy - (5 if sub else -4), [label],
                  TextOpts(size=12, weight="700"))
        if sub:
            svg.text(cx, cy + 13, sub, TextOpts(size=10, color="muted"))
        return
    if shape == "terminal":
        o = BoxOpts(**{**o.__dict__, "rx": int(h / 2)})
    svg.box(x, y, w, h, label, sub, o=o)


def table(svg: SVG, x: float, y: float, headers: list[str],
          rows: list[list[str]], colw: list[int], *, rowh: int = 30,
          headh: int = 32, size: int = 12, align: str = "start",
          mono_cols: tuple[int, ...] = ()) -> float:
    """Draw a simple comparison table. Returns the bottom y."""
    total = sum(colw)
    svg.rect(x, y, total, headh, fill="slate", stroke=None, rx=6)
    svg.rect(x, y + headh - 6, total, 6, fill="slate", stroke=None, rx=0)
    cx = x
    for htxt, w in zip(headers, colw):
        a = "middle" if align == "middle" else "start"
        tx = cx + w / 2 if a == "middle" else cx + 10
        svg.text(tx, y + headh / 2 + 4, htxt,
                 TextOpts(size=size, weight="700", color="bg", anchor=a))
        cx += w
    yy = y + headh
    for i, row in enumerate(rows):
        fill = "panel" if i % 2 == 0 else "bg"
        svg.rect(x, yy, total, rowh, fill=fill, stroke=None, rx=0)
        cx = x
        for j, cell in enumerate(row):
            w = colw[j]
            col, bold, txt = "ink", "400", cell
            if cell.startswith("**") and cell.endswith("**"):
                col, bold, txt = "ink", "700", cell[2:-2]
            elif cell.startswith("~"):          # muted / de-emphasised
                col, txt = "muted", cell[1:]
            elif cell.startswith("+"):          # good
                col, bold, txt = "green", "600", cell[1:]
            elif cell.startswith("-"):          # bad
                col, bold, txt = "red", "600", cell[1:]
            elif cell.startswith("!"):          # warn
                col, bold, txt = "amber", "600", cell[1:]
            a = "middle" if align == "middle" else "start"
            tx = cx + w / 2 if a == "middle" else cx + 10
            svg.text(tx, yy + rowh / 2 + 4, txt,
                     TextOpts(size=size, weight=bold, color=col, anchor=a,
                              mono=j in mono_cols))
            cx += w
        yy += rowh
    svg.rect(x, y, total, yy - y, fill=None, stroke="line", rx=6, sw=1.4)
    for cxo in range(len(colw) - 1):
        lx = x + sum(colw[:cxo + 1])
        svg.line(lx, y + headh, lx, yy, color="line", sw=1)
    return yy
