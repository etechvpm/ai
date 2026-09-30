"""Figures for modules 07-12."""

from __future__ import annotations

import math

from svgkit import SVG, TextOpts, BoxOpts, c, flowchart_step, table


# ---------------------------------------------------------------------------
# 07 -- functions
# ---------------------------------------------------------------------------
def d_argkinds(path):
    s = SVG(990, 400, title="The five kinds of parameter")
    s.heading(495, 28, "Anatomy of a Python signature")
    s.caption(495, 46, "def f(pos_only, /, pos_or_kw, *, kw_only, **kwargs) - the / and * are the dividers")

    s.rect(60, 80, 870, 74, fill="panel", stroke="line", rx=12)
    parts = [("def process(", "ink", None), ("user_id", "blue", "bluebg"),
             (", /, ", "muted", None), ("mode", "violet", "violetbg"),
             ("=\"fast\", ", "muted", None), ("*", "red", "redbg"),
             (", retries", "green", "greenbg"), ("=3, ", "muted", None),
             ("**options", "amber", "amberbg"), ("):", "ink", None)]
    x = 78
    for txt, col, bg in parts:
        w = len(txt) * 11.6 + 6
        if bg:
            s.rect(x - 4, 100, w + 6, 34, fill=bg, stroke=col, rx=7)
        s.text(x + w / 2 - 2, 123, txt, TextOpts(size=15, mono=True,
                                                 weight="700", color=col))
        x += w + 4

    cards = [("positional-only", "blue", "before the /",
              ["process(42)", "callers cannot use the name -",
               "protects your API when a", "parameter name is meaningless"]),
             ("positional or keyword", "violet", "the default",
              ["process(42, 'slow')", "process(42, mode='slow')",
               "most parameters live here;", "keywords self-document calls"]),
             ("keyword-only", "green", "after the *",
              ["process(42, retries=5)", "cannot be passed positionally -",
               "forces readable call sites", "and lets you reorder later"]),
             ("**kwargs", "amber", "catch-all dict",
              ["process(42, debug=True)", "options == {'debug': True}",
               "great for wrappers and", "forwarding to super()"])]
    w, gap = 213, 14
    x0 = (990 - (4 * w + 3 * gap)) / 2
    for i, (nm, k, pos, lines) in enumerate(cards):
        bx = x0 + i * (w + gap)
        s.panel(bx, 186, w, 156, "", fill="bg", stroke=k)
        s.rect(bx, 186, w, 4, fill=k, stroke=None, rx=2)
        s.text(bx + w / 2, 210, nm, TextOpts(size=12, weight="700",
                                             color=k))
        s.text(bx + w / 2, 228, pos, TextOpts(size=10, italic=True,
                                              color="muted"))
        s.mtext(bx + 14, 254, lines,
                TextOpts(size=10.5, anchor="start", color="ink",
                         mono=True), lh=17)
    s.panel(x0, 356, 4 * w + 3 * gap, 34, "", fill="greenbg", stroke="green")
    s.text(495, 378, "*args (positional var-args) collects extra positional arguments into a tuple - "
                     "def total(*nums) -> int: return sum(nums)",
           TextOpts(size=11.5, color="ink"))
    s.save(path)


def d_call_stack(path):
    s = SVG(990, 452, title="The call stack")
    s.heading(495, 28, "The call stack: who called whom, and what is still alive")
    s.caption(495, 46, "Each call pushes a frame holding its local variables. Returning pops it - locals disappear.")

    frames = [("main / <module>", "total = None", "slate", 62),
              ("calculate_total(items)", "items = [...]   subtotal = 240", "blue", 152),
              ("apply_tax(subtotal, 0.18)", "subtotal = 240   rate = 0.18", "green", 242),
              ("round(value, 2)", "value = 283.2   ndigits = 2", "amber", 332)]
    for i, (fn, locs, k, y) in enumerate(frames):
        x = 120 + i * 40
        s.panel(x, y, 460, 78, "", fill="bg", stroke=k)
        s.rect(x, y, 6, 78, fill=k, stroke=None, rx=3)
        s.text(x + 22, y + 26, fn, TextOpts(size=13, weight="700",
                                            anchor="start", color=k,
                                            mono=True))
        s.text(x + 22, y + 52, locs, TextOpts(size=11.5, anchor="start",
                                              color="slate", mono=True))
        s.text(x + 470, y + 44, f"frame {i}",
               TextOpts(size=10, color="muted", anchor="start", italic=True))
        if i:
            s.line(x - 26, y - 10, x + 20, y, color="slate", arrow=True,
                   sw=1.8)

    s.line(700, 84, 700, 400, color="line", sw=1.6, dashed=True)
    s.text(712, 80, "stack top", TextOpts(size=11, anchor="start",
                                          color="muted", italic=True))
    s.panel(726, 100, 244, 150, "", fill="redbg", stroke="red")
    s.text(742, 124, "RecursionError", TextOpts(size=12.5, weight="700",
                                                anchor="start", color="red"))
    s.mtext(742, 148,
            ["The stack is finite: CPython",
             "defaults to 1000 frames",
             "(sys.getrecursionlimit()).",
             "Deep recursion blows up -",
             "prefer iteration or an",
             "explicit worklist."],
            TextOpts(size=11, anchor="start", color="ink"), lh=17)
    s.panel(726, 268, 244, 132, "", fill="panel2", stroke="line")
    s.text(742, 292, "Why you care", TextOpts(size=12, weight="700",
                                              anchor="start", color="slate"))
    s.mtext(742, 314,
            ["* a traceback IS this stack,",
             "  printed newest-first",
             "* closures keep a frame's",
             "  variables alive after return",
             "* profilers count time per frame"],
            TextOpts(size=10.5, anchor="start", color="ink"), lh=17)
    s.save(path)


def d_scope(path):
    s = SVG(990, 430, title="LEGB name resolution")
    s.heading(495, 28, "Name lookup: L \u2192 E \u2192 G \u2192 B")
    s.caption(495, 46, "Python searches four scopes in order and stops at the FIRST match.")

    rings = [("B - Builtins", "len, print, range, sum, TypeError ...", "red", 26, 66, 938, 300),
             ("G - Global (module)", "names defined at the top level of the file; lives as long as the process", "amber", 56, 96, 878, 240),
             ("E - Enclosing (outer functions)", "locals of any function that contains this one - kept alive by a closure", "violet", 86, 126, 818, 180),
             ("L - Local", "assigned inside the current function; created on call, destroyed on return", "blue", 116, 156, 758, 120)]
    for nm, desc, k, x, y, w, h in rings:
        s.rect(x, y, w, h, fill="bg", stroke=k, rx=14, sw=2)
        s.text(x + 18, y + 24, nm, TextOpts(size=12.5, weight="700",
                                            anchor="start", color=k))
        s.text(x + 18, y + 44, desc, TextOpts(size=10.5, anchor="start",
                                              color="muted"))
    s.mtext(495, 224,
            ["count = 0",
             "def outer():",
             "    def inner():",
             "        return count      # found in G (no local assignment)",
             "    return inner()"],
            TextOpts(size=11.5, mono=True, color="ink"), lh=17)

    s.panel(26, 370, 938, 54, "", fill="amberbg", stroke="amber")
    s.mtext(42, 390,
            ["Assignment creates a LOCAL. Inside a function `count += 1` raises UnboundLocalError unless you",
             "declare `global count` (module scope) or `nonlocal count` (an enclosing function's scope)."],
            TextOpts(size=11.5, anchor="start", color="ink"), lh=18)
    s.save(path)


def d_closure(path):
    s = SVG(990, 400, title="Closures")
    s.heading(495, 28, "A closure is a function plus the variables it captured")
    s.caption(495, 46, "make_counter() has already returned - yet `count` is still alive inside the returned function.")

    s.panel(40, 76, 400, 200, "", fill="bg", stroke="slate", dashed=True)
    s.text(56, 98, "make_counter() - FINISHED, frame popped",
           TextOpts(size=11.5, weight="700", anchor="start", color="slate"))
    s.mtext(56, 122,
            ["def make_counter():",
             "    count = 0",
             "    def inc():",
             "        nonlocal count",
             "        count += 1",
             "        return count",
             "    return inc"],
            TextOpts(size=11.5, mono=True, anchor="start", color="ink"), lh=18)

    s.line(440, 176, 540, 176, color="violet", arrow=True, sw=2.2)
    s.arrowlabel(490, 164, "returns", color="violet", size=11)

    s.panel(540, 76, 410, 200, "", fill="bg", stroke="violet")
    s.text(556, 98, "the closure object (still callable)",
           TextOpts(size=11.5, weight="700", anchor="start", color="violet"))
    s.rect(556, 112, 378, 60, fill="violetbg", stroke="violet", rx=8)
    s.text(745, 134, "inc  <function>", TextOpts(size=12.5, weight="700",
                                                  color="violet", mono=True))
    s.text(745, 156, "__code__  +  __closure__",
           TextOpts(size=11, color="slate", mono=True))
    s.rect(556, 190, 378, 66, fill="amberbg", stroke="amber", rx=8)
    s.text(572, 212, "captured cell (shared, mutable):",
           TextOpts(size=11, weight="700", anchor="start", color="amber"))
    s.text(572, 236, "count -> cell_contents = 3",
           TextOpts(size=12, mono=True, anchor="start", color="ink"))

    s.panel(40, 292, 910, 92, "", fill="panel2", stroke="line")
    s.text(56, 314, "Two traps every team eventually hits",
           TextOpts(size=12, weight="700", anchor="start", color="slate"))
    s.mtext(56, 338,
            ["1.  Late binding in loops:  [lambda: i for i in range(3)]  ->  all three return 2.  The closure captures the VARIABLE, not its value.",
             "    Fix with a default argument:  [lambda i=i: i for i in range(3)].",
             "2.  Writing to a captured name needs `nonlocal` (or `global`); reading it does not."],
            TextOpts(size=11, anchor="start", color="ink"), lh=17)
    s.save(path)


# ---------------------------------------------------------------------------
# 08 -- modules and packages
# ---------------------------------------------------------------------------
def d_import(path):
    s = SVG(990, 404, title="What happens on import")
    s.heading(495, 28, "The import machinery")
    steps = [("import reports", "the statement", "slate"),
             ("sys.modules", "cache checked FIRST -\nalready imported?", "violet"),
             ("sys.path", "list of directories\nsearched in order", "blue"),
             ("Finder", "locates the module:\n.py, package, zip, C ext", "green"),
             ("Loader", "executes the module\ntop-to-bottom ONCE", "amber"),
             ("module object", "bound to the name\nin your namespace", "cyan")]
    w, gap, y, h = 142, 16, 74, 104
    x = (990 - (6 * w + 5 * gap)) / 2
    for i, (nm, desc, k) in enumerate(steps):
        bx = x + i * (w + gap)
        s.panel(bx, y, w, h, "", fill="bg", stroke=k)
        s.rect(bx, y, w, 26, fill=k, stroke=None, rx=10)
        s.rect(bx, y + 16, w, 10, fill=k, stroke=None, rx=0)
        s.text(bx + w / 2, y + 18, nm, TextOpts(size=11, weight="700",
                                                color="bg"))
        s.mtext(bx + w / 2, y + 52, desc.split("\n"),
                TextOpts(size=10, color="slate"), lh=14)
        if i:
            s.line(bx - gap, y + h / 2, bx, y + h / 2, color="line",
                   arrow=True, sw=1.6)
    s.line(x + w + gap / 2, y + h, x + w + gap / 2, y + h + 34,
           color="violet", arrow=True)
    s.elbow(x + w + gap / 2, y + h + 34, x + w / 2, y + h + 34,
            color="violet", arrow=True, bend="h")
    s.arrowlabel(x + w + gap / 2 + 100, y + h + 26, "hit -> done instantly",
                 color="violet", size=10.5)

    yy = y + h + 52
    s.panel(x, yy, 452, 150, "", fill="panel2", stroke="line")
    s.text(x + 16, yy + 22, "sys.path order (first match wins)",
           TextOpts(size=12, weight="700", anchor="start", color="slate"))
    s.mtext(x + 16, yy + 46,
            ["1.  directory of the running script (or cwd)",
             "2.  PYTHONPATH entries",
             "3.  installation-dependent defaults",
             "4.  site-packages of the ACTIVE virtualenv"],
            TextOpts(size=11, mono=True, anchor="start", color="ink"), lh=18)

    s.panel(x + 468, yy, 452, 150, "", fill="redbg", stroke="red")
    s.text(x + 484, yy + 22, "Circular imports",
           TextOpts(size=12, weight="700", anchor="start", color="red"))
    s.mtext(x + 484, yy + 46,
            ["a.py imports b.py, b.py imports a.py -> one of",
             "them sees a HALF-INITIALISED module and you get",
             "ImportError / AttributeError. Fix by moving the",
             "shared code into a third module, importing inside",
             "the function, or restructuring with Protocols."],
            TextOpts(size=10.5, anchor="start", color="ink"), lh=18)
    s.save(path)


def d_package(path):
    s = SVG(990, 470, title="Package layout")
    s.heading(495, 28, "From a folder of scripts to an installable package")
    tree = [
        (0, "myproject/", "dir", "the repository root"),
        (1, "pyproject.toml", "file", "metadata, deps, tool config - the modern standard"),
        (1, "src/", "dir", "src-layout keeps the package out of the cwd"),
        (2, "myproject/", "dir", "the importable package"),
        (3, "__init__.py", "file", "makes it a package; re-export the public API"),
        (3, "py.typed", "file", "marker telling mypy this package ships type hints"),
        (3, "models.py", "file", "domain objects"),
        (3, "service.py", "file", "business logic"),
        (3, "cli.py", "file", "entry point: def main() -> int"),
        (4, "utils/", "dir", "subpackage"),
        (5, "__init__.py", "file", ""),
        (5, "text.py", "file", "from myproject.utils.text import slugify"),
        (1, "tests/", "dir", "mirrors src/ ; never shipped to users"),
        (2, "test_service.py", "file", "pytest discovers test_*.py automatically"),
        (1, "README.md", "file", "the PyPI landing page"),
        (1, ".venv/", "dir", "local virtualenv - ALWAYS gitignored"),
    ]
    y = 62
    for depth, name, kind, note in tree:
        x = 40 + depth * 26
        col = "blue" if kind == "dir" else "ink"
        if depth:
            s.line(x - 14, y + 9, x - 2, y + 9, color="line", sw=1.4)
        s.text(x + 4, y + 14, ("\U0001F4C1 " if kind == "dir" else "\U0001F4C4 ") + name,
               TextOpts(size=12.5, mono=True, weight="700" if kind == "dir" else "400",
                        anchor="start", color=col))
        if note:
            s.text(470, y + 14, note, TextOpts(size=11, anchor="start",
                                               color="muted"))
        y += 23
    s.line(40, 62, 40, y - 14, color="line", sw=1.4)

    s.panel(500, 210, 462, 120, "", fill="greenbg", stroke="green")
    s.text(516, 234, "Why src-layout?",
           TextOpts(size=12.5, weight="700", anchor="start", color="green"))
    s.mtext(516, 258,
            ["With a flat layout `import myproject` silently picks up the",
             "folder in your cwd, so tests can pass while the INSTALLED",
             "package is broken. src-layout forces you to install first -",
             "pip install -e . - and catches that class of bug for free."],
            TextOpts(size=11, anchor="start", color="ink"), lh=17)
    s.panel(500, 344, 462, 96, "", fill="amberbg", stroke="amber")
    s.text(516, 368, "Relative vs absolute imports",
           TextOpts(size=12.5, weight="700", anchor="start", color="amber"))
    s.mtext(516, 390,
            ["from .models import User      # relative, inside a package",
             "from myproject.models import User   # absolute",
             "Industry default: absolute imports everywhere - they are",
             "unambiguous and survive refactors."],
            TextOpts(size=10.5, mono=True, anchor="start", color="ink"), lh=16)
    s.save(path)


# ---------------------------------------------------------------------------
# 09 -- OOP
# ---------------------------------------------------------------------------
def d_object_model(path):
    s = SVG(990, 430, title="Instance, class, and base class")
    s.heading(495, 28, "Three objects, two dictionaries")
    s.caption(495, 46, "Attribute lookup: instance __dict__  ->  class __dict__  ->  base classes  ->  AttributeError")

    s.panel(40, 74, 280, 150, "", fill="bg", stroke="green")
    s.text(180, 96, "instance", TextOpts(size=12, weight="700",
                                         color="green"))
    s.text(180, 118, "emp = Employee('ada', 90000)",
           TextOpts(size=10.5, mono=True, color="slate"))
    s.rect(56, 132, 248, 76, fill="greenbg", stroke="green", rx=8)
    s.text(180, 152, "__dict__", TextOpts(size=11, weight="700",
                                          color="green", mono=True))
    s.mtext(180, 172, ["{'name': 'ada',", " 'salary': 90000}"],
            TextOpts(size=11.5, mono=True, color="ink"), lh=17)

    s.panel(355, 74, 280, 220, "", fill="bg", stroke="blue")
    s.text(495, 96, "class", TextOpts(size=12, weight="700", color="blue"))
    s.text(495, 118, "Employee.__dict__", TextOpts(size=10.5, mono=True,
                                                    color="slate"))
    s.rect(371, 132, 248, 146, fill="bluebg", stroke="blue", rx=8)
    s.mtext(495, 154, ["__init__  (function)", "raise_salary  (function)",
                       "department = 'Eng'", "TAX = 0.30",
                       "__doc__", "__module__"],
            TextOpts(size=11.5, mono=True, color="ink"), lh=19)

    s.panel(670, 74, 280, 150, "", fill="bg", stroke="violet")
    s.text(810, 96, "base class", TextOpts(size=12, weight="700",
                                           color="violet"))
    s.text(810, 118, "object.__dict__", TextOpts(size=10.5, mono=True,
                                                 color="slate"))
    s.rect(686, 132, 248, 76, fill="violetbg", stroke="violet", rx=8)
    s.mtext(810, 156, ["__str__  __repr__  __eq__", "__hash__  __class__"],
            TextOpts(size=11.5, mono=True, color="ink"), lh=18)

    s.line(320, 149, 355, 149, color="green", arrow=True, sw=2)
    s.arrowlabel(337, 138, "__class__", color="green", size=10)
    s.line(635, 149, 670, 149, color="blue", arrow=True, sw=2)
    s.arrowlabel(652, 138, "__bases__", color="blue", size=10)

    s.panel(355, 312, 595, 100, "", fill="amberbg", stroke="amber")
    s.text(371, 336, "emp.department finds the CLASS attribute - emp.TAX too",
           TextOpts(size=11.5, weight="700", anchor="start", color="amber"))
    s.mtext(371, 360,
            ["Reading walks the chain upwards; assignment writes to the INSTANCE and shadows the class attribute.",
             "Classic bug: `emp.TAX = 0.2` changes only emp. `Employee.TAX = 0.2` changes every instance."],
            TextOpts(size=11, anchor="start", color="ink"), lh=17)
    s.panel(40, 246, 280, 166, "", fill="panel2", stroke="line")
    s.text(56, 268, "Lookup algorithm", TextOpts(size=12, weight="700",
                                                 anchor="start",
                                                 color="slate"))
    s.mtext(56, 292,
            ["1. data descriptors on the type",
             "2. instance __dict__",
             "3. non-data descriptors /",
             "   class attributes (MRO order)",
             "4. __getattr__ if defined",
             "5. AttributeError"],
            TextOpts(size=10.5, mono=True, anchor="start", color="ink"), lh=17)
    s.save(path)


def d_mro(path):
    s = SVG(990, 430, title="Multiple inheritance and MRO")
    s.heading(495, 28, "The diamond problem, solved by C3 linearisation")

    def klass(x, y, name, k, w=170, h=54):
        s.panel(x, y, w, h, "", fill="bg", stroke=k)
        s.text(x + w / 2, y + h / 2 + 5, name,
               TextOpts(size=13, weight="700", color=k, mono=True))
        return (x + w / 2, y, y + h)

    d = klass(410, 66, "D", "red")
    b = klass(200, 176, "B", "blue")
    cc = klass(620, 176, "C", "green")
    a = klass(410, 288, "A", "violet")
    o = klass(410, 372, "object", "slate", w=170, h=44)
    s.line(d[0] - 60, d[2], b[0], b[1], color="blue", sw=2, arrow=True)
    s.line(d[0] + 60, d[2], cc[0], cc[1], color="green", sw=2, arrow=True)
    s.line(b[0] - 20, b[2], a[0] - 60, a[1], color="violet", sw=2, arrow=True)
    s.line(cc[0] + 20, cc[2], a[0] + 60, a[1], color="violet", sw=2,
           arrow=True)
    s.line(a[0], a[2], o[0], o[1], color="slate", sw=2, arrow=True)

    s.panel(40, 66, 140, 54, "", fill="redbg", stroke="red")
    s.text(110, 88, "class D(B, C)", TextOpts(size=11, mono=True,
                                               weight="700", color="red"))
    s.text(110, 106, "A defined once", TextOpts(size=9.5, color="slate"))

    mro = ["D", "B", "C", "A", "object"]
    cols = ["red", "blue", "green", "violet", "slate"]
    x0 = 660
    s.text(x0, 84, "D.__mro__", TextOpts(size=12, weight="700",
                                         anchor="start", color="ink",
                                         mono=True))
    for i, (m, k) in enumerate(zip(mro, cols)):
        bx = x0 + i * 60
        s.rect(bx, 96, 52, 30, fill=f"{k}bg", stroke=k, rx=6)
        s.text(bx + 26, 116, m, TextOpts(size=11.5, weight="700", color=k,
                                         mono=True))
        if i:
            s.line(bx - 8, 111, bx, 111, color="line", arrow=True, sw=1.4)
    s.panel(x0 - 20, 146, 330, 116, "", fill="panel2", stroke="line")
    s.mtext(x0 - 4, 168,
            ["super() follows the MRO, not 'my parent'.",
             "In D().hello() the call order is",
             "D -> B -> C -> A -> object, and A runs",
             "exactly ONCE even though B and C both",
             "inherit from it."],
            TextOpts(size=11, anchor="start", color="ink"), lh=17)
    s.panel(40, 156, 500, 246, "", fill="amberbg", stroke="amber")
    s.text(56, 180, "Cooperative multiple inheritance",
           TextOpts(size=12.5, weight="700", anchor="start", color="amber"))
    s.mtext(56, 204,
            ["class A:",
             "    def hello(self):",
             "        print('A')",
             "class B(A):",
             "    def hello(self):",
             "        print('B'); super().hello()",
             "class C(A):",
             "    def hello(self):",
             "        print('C'); super().hello()",
             "class D(B, C):",
             "    def hello(self):",
             "        print('D'); super().hello()"],
            TextOpts(size=11, mono=True, anchor="start", color="ink"), lh=17)
    s.text(56, 392, "D().hello()  ->  D B C A   (not D B A C A)",
           TextOpts(size=11.5, weight="700", anchor="start", color="red",
                    mono=True))
    s.save(path)


def d_comp_vs_inh(path):
    s = SVG(990, 400, title="Inheritance vs composition")
    s.heading(495, 28, "Inheritance vs composition")
    s.caption(495, 46, "\"Favour composition over inheritance\" - Design Patterns, 1994. It is still the best advice in OOP.")

    s.panel(22, 66, 468, 250, "", fill="bg", stroke="amber")
    s.rect(22, 66, 468, 30, fill="amber", stroke=None, rx=10)
    s.rect(22, 84, 468, 12, fill="amber", stroke=None, rx=0)
    s.text(256, 86, "INHERITANCE  -  'is a'", TextOpts(size=12, weight="700",
                                                        color="bg"))
    s.mtext(42, 118,
            ["class SqlLogger(Logger):",
             "    def log(self, msg):",
             "        self.conn.execute(...)"],
            TextOpts(size=11.5, mono=True, anchor="start", color="ink"), lh=18)
    s.mtext(42, 184,
            ["- tight coupling: child knows parent's internals",
             "- parent changes silently break every child",
             "- deep hierarchies become unreadable",
             "- the fragile base class problem"],
            TextOpts(size=11, anchor="start", color="red"), lh=17)
    s.text(42, 268, "Use it for genuine subtypes + polymorphism.",
           TextOpts(size=11, weight="700", anchor="start", color="amber"))
    s.text(42, 292, "Keep hierarchies to 2-3 levels.",
           TextOpts(size=11, anchor="start", color="slate"))

    s.panel(500, 66, 468, 250, "", fill="bg", stroke="green")
    s.rect(500, 66, 468, 30, fill="green", stroke=None, rx=10)
    s.rect(500, 84, 468, 12, fill="green", stroke=None, rx=0)
    s.text(734, 86, "COMPOSITION  -  'has a'", TextOpts(size=12, weight="700",
                                                         color="bg"))
    s.mtext(520, 118,
            ["class OrderService:",
             "    def __init__(self, logger: Logger):",
             "        self._logger = logger   # injected"],
            TextOpts(size=11.5, mono=True, anchor="start", color="ink"), lh=18)
    s.mtext(520, 184,
            ["+ swap the collaborator without touching the class",
             "+ trivially testable: pass a fake/stub logger",
             "+ no hidden parent state, no MRO surprises",
             "+ smaller, focused classes (Single Responsibility)"],
            TextOpts(size=11, anchor="start", color="green"), lh=17)
    s.text(520, 268, "This is what Dependency Injection means.",
           TextOpts(size=11, weight="700", anchor="start", color="green"))
    s.text(520, 292, "Frameworks (FastAPI, Django) are built on it.",
           TextOpts(size=11, anchor="start", color="slate"))

    s.panel(22, 330, 946, 56, "", fill="bluebg", stroke="blue")
    s.text(40, 354, "Rule of thumb", TextOpts(size=12, weight="700",
                                              anchor="start", color="blue"))
    s.text(40, 374, "Inherit to BE something (a subtype users will treat polymorphically). "
                    "Compose to USE something (a collaborator you might replace).",
           TextOpts(size=11.5, anchor="start", color="ink"))
    s.save(path)


# ---------------------------------------------------------------------------
# 10 -- files
# ---------------------------------------------------------------------------
def d_with(path):
    s = SVG(990, 372, title="The with statement")
    s.heading(495, 28, "with: guaranteed cleanup, even on exceptions")
    s.caption(495, 46, "A context manager's __enter__ runs on the way in and __exit__ always runs on the way out.")

    steps = [("with open(...) as f:", "__enter__() returns f", "blue", 62),
             ("body executes", "your read / write work", "green", 246),
             ("__exit__(exc_type, exc_val, tb)", "close / rollback / unlock", "amber", 470)]
    for i, (lab, sub, k, x) in enumerate(steps):
        w = 200 if i != 2 else 250
        s.panel(x, 84, w, 96, "", fill="bg", stroke=k)
        s.text(x + w / 2, 118, lab, TextOpts(size=12, weight="700", color=k,
                                             mono=True))
        s.text(x + w / 2, 146, sub, TextOpts(size=11, color="slate"))
    s.line(262, 132, 246 + 0, 132, color="slate", arrow=True)
    s.line(262, 132, 246, 132, color="slate", arrow=True, sw=1.8)
    s.line(446, 132, 470, 132, color="slate", arrow=True, sw=1.8)

    s.panel(62, 208, 658, 128, "", fill="redbg", stroke="red")
    s.text(78, 232, "If the body raises, __exit__ STILL runs",
           TextOpts(size=12.5, weight="700", anchor="start", color="red"))
    s.mtext(78, 258,
            ["The exception is passed to __exit__. Returning True from __exit__ SWALLOWS it; returning False (the",
             "normal choice) re-raises it after cleanup. open()'s __exit__ calls f.close() and returns False.",
             "Manual try/finally gets this wrong constantly - the with statement makes it structurally impossible."],
            TextOpts(size=11, anchor="start", color="ink"), lh=18)

    s.panel(742, 84, 220, 252, "", fill="greenbg", stroke="green")
    s.text(758, 108, "Write your own", TextOpts(size=12, weight="700",
                                                 anchor="start",
                                                 color="green"))
    s.mtext(758, 132,
            ["from contextlib",
             "import contextmanager",
             "",
             "@contextmanager",
             "def timer(label):",
             "    t = time.perf_counter()",
             "    try:",
             "        yield",
             "    finally:",
             "        print(label,",
             "              time.perf_counter()",
             "              - t)"],
            TextOpts(size=10, mono=True, anchor="start", color="ink"), lh=15)
    s.save(path)


# ---------------------------------------------------------------------------
# 11 -- exceptions
# ---------------------------------------------------------------------------
def d_exc_hierarchy(path):
    s = SVG(990, 500, title="The exception hierarchy")
    s.heading(495, 28, "Exception hierarchy - catch specific, not broad")

    def node(x, y, w, h, label, k, sub=""):
        s.panel(x, y, w, h, "", fill=f"{k}bg", stroke=k)
        s.text(x + w / 2, y + h / 2 + (2 if not sub else -3), label,
               TextOpts(size=12, weight="700", color=k, mono=True))
        if sub:
            s.text(x + w / 2, y + h / 2 + 14, sub,
                   TextOpts(size=9.5, color="slate"))

    node(390, 58, 210, 40, "BaseException", "slate")
    node(60, 136, 190, 40, "SystemExit", "slate")
    node(270, 136, 190, 40, "KeyboardInterrupt", "slate")
    node(480, 136, 190, 40, "GeneratorExit", "slate")
    node(700, 136, 210, 44, "Exception", "blue", "catch THIS family")
    for x in (155, 365, 575, 805):
        s.line(495, 98, x, 136, color="line", sw=1.5, arrow=True)

    lvl2 = [("ArithmeticError", 40, "violet"), ("LookupError", 218, "violet"),
            ("OSError", 396, "violet"), ("ValueError", 574, "violet"),
            ("TypeError", 706, "violet"), ("AttributeError", 828, "violet")]
    for nm, x, k in lvl2:
        node(x, 222, 128, 36, nm, k)
        s.line(805, 180, x + 64, 222, color="line", sw=1.4, arrow=True)

    lvl3 = [("ZeroDivisionError", "ArithmeticError"),
            ("OverflowError", "ArithmeticError"),
            ("IndexError", "LookupError"),
            ("KeyError", "LookupError"),
            ("FileNotFoundError", "OSError"),
            ("PermissionError", "OSError"),
            ("ConnectionError", "OSError"),
            ("TimeoutError", "OSError")]
    parents = {nm: x for nm, x, _ in lvl2}
    for i, (nm, par) in enumerate(lvl3):
        px = parents[par]
        col = i % 2
        x = px + col * 116 - (58 if par in ("OSError",) else 0)
        node(x, 296, 112, 32, nm, "cyan")
        s.line(px + 64, 258, x + 56, 296, color="line", sw=1.2, arrow=True)

    s.panel(40, 356, 450, 128, "", fill="greenbg", stroke="green")
    s.text(56, 380, "GOOD", TextOpts(size=12.5, weight="700",
                                      anchor="start", color="green"))
    s.mtext(56, 402,
            ["try:",
             "    data = json.loads(raw)",
             "except json.JSONDecodeError as exc:",
             "    logger.warning('bad payload', exc_info=exc)"],
            TextOpts(size=11, mono=True, anchor="start", color="ink"), lh=17)

    s.panel(510, 356, 440, 128, "", fill="redbg", stroke="red")
    s.text(526, 380, "AVOID", TextOpts(size=12.5, weight="700",
                                       anchor="start", color="red"))
    s.mtext(526, 402,
            ["try:",
             "    data = json.loads(raw)",
             "except:            # catches SystemExit too!",
             "    pass             # the silent bug factory"],
            TextOpts(size=11, mono=True, anchor="start", color="ink"), lh=17)
    s.save(path)


def d_try_flow(path):
    s = SVG(990, 452, title="try / except / else / finally")
    s.heading(495, 28, "Which block actually runs?")
    flowchart_step(s, 395, 50, 200, 40, "try: block", "the risky work",
                   kind="blue")
    s.line(495, 90, 495, 118, color="slate", arrow=True)
    flowchart_step(s, 415, 118, 160, 80, "exception?", kind="amber",
                   shape="diamond")
    s.line(415, 158, 250, 158, color="red", arrow=True, sw=2)
    s.arrowlabel(330, 148, "yes", color="red", size=11)
    flowchart_step(s, 90, 130, 160, 58, "except:", "handle it here",
                   kind="red")
    s.line(575, 158, 720, 158, color="green", arrow=True, sw=2)
    s.arrowlabel(648, 148, "no", color="green", size=11)
    flowchart_step(s, 720, 130, 170, 58, "else:", "ONLY if try succeeded",
                   kind="green")
    s.poly([(170, 188), (170, 250), (400, 250)], color="slate", sw=1.8)
    s.poly([(805, 188), (805, 250), (600, 250)], color="slate", sw=1.8)
    s.line(495, 198, 495, 228, color="slate", arrow=True, sw=1.8)
    flowchart_step(s, 380, 228, 230, 46, "finally:", "ALWAYS runs - cleanup",
                   kind="violet")
    s.line(495, 274, 495, 306, color="slate", arrow=True)
    flowchart_step(s, 400, 306, 190, 38, "continue / propagate", kind="slate",
                   shape="terminal")

    s.panel(60, 300, 300, 128, "", fill="panel2", stroke="line")
    s.text(76, 322, "Ordering guarantees",
           TextOpts(size=12, weight="700", anchor="start", color="slate"))
    s.mtext(76, 346,
            ["try -> except|else -> finally",
             "finally runs even if a `return`,",
             "`break` or `continue` sits in try,",
             "and even if except re-raises.",
             "Never put business logic in finally."],
            TextOpts(size=10.5, mono=True, anchor="start", color="ink"), lh=17)
    s.panel(660, 300, 300, 128, "", fill="amberbg", stroke="amber")
    s.text(676, 322, "Why else exists",
           TextOpts(size=12, weight="700", anchor="start", color="amber"))
    s.mtext(676, 346,
            ["Keep the try block SMALL: only the",
             "line that can fail. Put the code that",
             "must NOT be protected in else, so it",
             "cannot be accidentally swallowed by",
             "your own except clause."],
            TextOpts(size=10.5, anchor="start", color="ink"), lh=17)
    s.save(path)


# ---------------------------------------------------------------------------
# 12 -- iteration
# ---------------------------------------------------------------------------
def d_iterator(path):
    s = SVG(990, 400, title="The iterator protocol")
    s.heading(495, 28, "for loops are just iter() + next() + StopIteration")

    s.mtext(40, 88,
            ["for item in seq:",
             "    use(item)"],
            TextOpts(size=12.5, mono=True, anchor="start", color="ink"), lh=20)
    s.text(40, 140, "is exactly equivalent to:", TextOpts(size=11,
                                                           anchor="start",
                                                           color="muted",
                                                           italic=True))
    s.mtext(40, 164,
            ["it = iter(seq)            # calls seq.__iter__()",
             "while True:",
             "    try:",
             "        item = next(it)   # calls it.__next__()",
             "    except StopIteration:",
             "        break",
             "    use(item)"],
            TextOpts(size=12, mono=True, anchor="start", color="blue"), lh=19)

    seq = ["iter()", "next()", "next()", "next()", "StopIteration"]
    outs = ["<iterator>", "10", "20", "30", "loop ends"]
    x0, w, gap = 400, 106, 14
    for i, (a, b) in enumerate(zip(seq, outs)):
        bx = x0 + i * (w + gap)
        k = "red" if i == 4 else ("violet" if i == 0 else "green")
        s.panel(bx, 84, w, 46, "", fill=f"{k}bg", stroke=k)
        s.text(bx + w / 2, 112, a, TextOpts(size=11.5, weight="700",
                                            color=k, mono=True))
        s.panel(bx, 150, w, 40, "", fill="panel", stroke="line")
        s.text(bx + w / 2, 175, b, TextOpts(size=11, color="ink",
                                            mono=True))
        s.line(bx + w / 2, 130, bx + w / 2, 150, color="line", arrow=True,
               sw=1.5)
        if i:
            s.line(bx - gap, 107, bx, 107, color="line", arrow=True, sw=1.5)
    s.text(x0, 216, "numbers = [10, 20, 30]",
           TextOpts(size=11.5, anchor="start", color="slate", mono=True))

    s.panel(40, 244, 440, 128, "", fill="bluebg", stroke="blue")
    s.text(56, 268, "ITERABLE vs ITERATOR", TextOpts(size=12.5, weight="700",
                                                     anchor="start",
                                                     color="blue"))
    s.mtext(56, 292,
            ["Iterable: has __iter__  (list, str, dict, file, range)",
             "Iterator: has __iter__ AND __next__, and is stateful -",
             "          it remembers where it stopped.",
             "Every iterator is iterable; not every iterable is an",
             "iterator. iter(list) gives a fresh one each call."],
            TextOpts(size=11, anchor="start", color="ink"), lh=17)
    s.panel(500, 244, 450, 128, "", fill="greenbg", stroke="green")
    s.text(516, 268, "Generators are iterators you write with yield",
           TextOpts(size=12, weight="700", anchor="start", color="green"))
    s.mtext(516, 292,
            ["def squares(n):",
             "    for i in range(n):",
             "        yield i * i      # pauses, keeps state, resumes"],
            TextOpts(size=11, mono=True, anchor="start", color="ink"), lh=18)
    s.text(516, 356, "One-shot: exhausting a generator leaves it empty.",
           TextOpts(size=11, italic=True, anchor="start", color="slate"))
    s.save(path)


def d_lazy_memory(path):
    s = SVG(990, 486, title="Eager vs lazy memory use")
    s.heading(495, 28, "Same result, 10,000x less memory")
    s.caption(495, 46, "Reading 10 million lines: the list version must hold everything at once, the generator never does.")

    bars = [("[x*2 for x in range(10_000_000)]", "list - eager", 380, "red",
             "~800 MB in RAM, 4.1 s"),
            ("(x*2 for x in range(10_000_000))", "generator - lazy", 8,
             "green", "~200 BYTES, starts instantly"),
            ("map(lambda x: x*2, range(10**7))", "map - lazy", 8, "blue",
             "~200 bytes")]
    y = 86
    for code, lab, w, k, note in bars:
        s.text(60, y + 14, code, TextOpts(size=11.5, mono=True,
                                          anchor="start", color="ink"))
        s.rect(60, y + 24, max(w, 6), 26, fill=f"{k}bg", stroke=k, rx=5)
        s.text(60 + max(w, 6) + 14, y + 42, note,
               TextOpts(size=11.5, weight="700", anchor="start", color=k))
        y += 76

    s.panel(60, y + 6, 420, 130, "", fill="panel2", stroke="line")
    s.text(76, y + 30, "The pipeline pattern",
           TextOpts(size=12.5, weight="700", anchor="start", color="slate"))
    s.mtext(76, y + 52,
            ["rows   = read_csv(path)        # generator",
             "clean  = (strip(r) for r in rows)",
             "valid  = (r for r in clean if ok(r))",
             "report = Counter(k for k in valid)"],
            TextOpts(size=11, mono=True, anchor="start", color="ink"), lh=18)
    s.text(76, y + 124, "Nothing is materialised until the final step consumes it.",
           TextOpts(size=10.5, italic=True, anchor="start", color="muted"))

    s.panel(500, y + 6, 430, 130, "", fill="amberbg", stroke="amber")
    s.text(516, y + 30, "Trade-offs you must know",
           TextOpts(size=12.5, weight="700", anchor="start", color="amber"))
    s.mtext(516, y + 52,
            ["- one-shot: a second `for` loop yields nothing",
             "- no len(), no indexing, no reuse",
             "- exceptions surface late, at consumption time",
             "- per-item overhead: a list can be FASTER for small n"],
            TextOpts(size=11, anchor="start", color="ink"), lh=18)
    s.save(path)


DIAGRAMS = {
    "argument-kinds.svg": d_argkinds,
    "call-stack.svg": d_call_stack,
    "scope-legb.svg": d_scope,
    "closure.svg": d_closure,
    "import-machinery.svg": d_import,
    "package-layout.svg": d_package,
    "object-model.svg": d_object_model,
    "inheritance-mro.svg": d_mro,
    "composition-vs-inheritance.svg": d_comp_vs_inh,
    "with-context-manager.svg": d_with,
    "exception-hierarchy.svg": d_exc_hierarchy,
    "try-except-flow.svg": d_try_flow,
    "iterator-protocol.svg": d_iterator,
    "lazy-vs-eager.svg": d_lazy_memory,
}
