"""Figures for modules 01-06.  Run via tools/make_diagrams.py."""

from __future__ import annotations

from svgkit import SVG, TextOpts, BoxOpts, c, flowchart_step, table


def _grid(svg, x, y, items, cols, cw, ch=28, gap=10, *, fill="bluebg",
          text="blue", size=12):
    for i, it in enumerate(items):
        r, cc = divmod(i, cols)
        svg.rect(x + cc * (cw + gap), y + r * (ch + gap), cw, ch,
                 fill=fill, stroke=None, rx=6)
        svg.text(x + cc * (cw + gap) + cw / 2,
                 y + r * (ch + gap) + ch / 2 + size * 0.36, it,
                 TextOpts(size=size, weight="600", color=text, mono=True))
    rows = (len(items) + cols - 1) // cols
    return y + rows * (ch + gap)


# ---------------------------------------------------------------------------
# 01 -- how Python runs
# ---------------------------------------------------------------------------
def d_execution(path):
    s = SVG(990, 372, title="How Python runs your code")
    s.heading(495, 30, "From source file to running program")
    s.caption(495, 48, "Python is compiled to bytecode and then interpreted by a virtual machine")

    row1 = [("main.py", ["your source code", "plain text"]),
            ("Parser", ["tokenises + parses", "builds the AST"]),
            ("AST", ["Abstract Syntax Tree", "structure of the code"]),
            ("Compiler", ["AST -> bytecode", "CPython's compile()"]),
            ("__pycache__/", ["main.cpython-311.pyc", "cached bytecode"])]
    y, h, w, gap = 68, 82, 154, 42
    x = (990 - (5 * w + 4 * gap)) / 2
    kinds = ["plain", "blue", "violet", "blue", "amber"]
    for i, (lab, sub) in enumerate(row1):
        bx = x + i * (w + gap)
        flowchart_step(s, bx, y, w, h, lab, sub, kind=kinds[i])
        if i:
            s.line(bx - gap, y + h / 2, bx, y + h / 2, color="slate",
                   arrow=True)
        s.badge(bx + w / 2 - 8, y - 12, str(i + 1), fill=kinds[i] if kinds[i] != "plain" else "slate")

    s.line(x + 4 * (w + gap) + w / 2, y + h, x + 4 * (w + gap) + w / 2,
           y + h + 40, color="slate", arrow=True)
    s.arrowlabel(x + 4 * (w + gap) + w / 2 + 46, y + h + 24,
                 "written to disk", color="muted", size=10)

    y2 = y + h + 44
    flowchart_step(s, x + 4 * (w + gap), y2, w, h, "PVM",
                   ["Python Virtual Machine", "runs opcodes in a loop"],
                   kind="green")
    s.line(x + 4 * (w + gap), y2 + h / 2, x + 3 * (w + gap) + w, y2 + h / 2,
           color="green", arrow=True)
    flowchart_step(s, x + 3 * (w + gap), y2, w, h, "Output",
                   ["your program runs", "prints / returns"], kind="green")

    s.panel(x, y2 - 4, 3 * w + 2 * gap - 20, h + 8, "",
            fill="panel2", stroke="line")
    s.text(x + 16, y2 + 20, "Three things worth remembering",
           TextOpts(size=12, weight="700", anchor="start", color="slate"))
    s.mtext(x + 16, y2 + 40,
            ["1.  Deleting __pycache__ is always safe - it is rebuilt.",
             "2.  The .pyc cache speeds up START-UP, never execution.",
             "3.  The GIL lives inside the PVM (see module 16)."],
            TextOpts(size=11, anchor="start", color="ink"), lh=16)
    s.caption(495, 362, "CPython 3.11: about 25% faster than 3.10 thanks to an adaptive specialised interpreter")
    s.save(path)


def d_toolchain(path):
    s = SVG(990, 306, title="The everyday Python toolchain")
    s.heading(495, 30, "The seven tools you will touch every day")
    steps = [("Editor / IDE", ["VS Code, PyCharm", "or Neovim"], "code ."),
             ("Virtual env", ["isolated deps", "per project"], "python -m venv .venv"),
             ("Interpreter", ["runs your code", "3.11+ recommended"], "python app.py"),
             ("Tests", ["pytest", "safety net"], "pytest -q"),
             ("Lint / Types", ["ruff, black", "mypy"], "ruff check ."),
             ("Git", ["history", "collaboration"], "git commit -am 'fix'"),
             ("CI / CD", ["GitHub Actions", "runs on push"], "gh pr create")]
    w, gap, y, h = 120, 20, 62, 92
    x = (990 - (7 * w + 6 * gap)) / 2
    kinds = ["slate", "violet", "blue", "green", "amber", "cyan", "red"]
    for i, (lab, sub, cmd) in enumerate(steps):
        bx = x + i * (w + gap)
        flowchart_step(s, bx, y, w, h, lab, sub, kind=kinds[i], size=12)
        if i:
            s.line(bx - gap, y + h / 2, bx, y + h / 2, color="line",
                   arrow=True, sw=1.6)
        s.rect(bx, y + h + 12, w, 24, fill="panel2", stroke="line", rx=5)
        s.text(bx + w / 2, y + h + 28, cmd,
               TextOpts(size=9, mono=True, color="slate"))
    s.panel(x, y + h + 52, 7 * w + 6 * gap, 54, "", fill="greenbg",
            stroke="green")
    s.mtext(x + 18, y + h + 74,
            ["Industry reality: nobody 'just runs python'.  Code is formatted, linted, type-checked,",
             "tested and reviewed automatically before it reaches production."],
            TextOpts(size=11.5, anchor="start", color="ink"), lh=17)
    s.save(path)


# ---------------------------------------------------------------------------
# 02 -- memory model
# ---------------------------------------------------------------------------
def d_memory(path):
    s = SVG(990, 486, title="Names point at objects")
    s.heading(495, 28, "Variables are name tags, not boxes")
    s.caption(495, 46, "Assignment binds a name to an object. Two names can bind to the SAME object.")

    def scene(px, pw, title, accent, sub):
        s.panel(px, 64, pw, 336, "", fill="bg", stroke=accent)
        s.rect(px, 64, pw, 30, fill=accent, stroke=None, rx=10)
        s.rect(px, 82, pw, 12, fill=accent, stroke=None, rx=0)
        s.text(px + pw / 2, 84, title,
               TextOpts(size=12, weight="700", color="bg"))
        s.text(px + pw / 2, 112, sub,
               TextOpts(size=11, mono=True, color="slate"))

    # --- Scene A : mutation ------------------------------------------------
    scene(22, 468, "A.  MUTATING the shared object", "blue",
          "b = a ; b.append(4)")
    for i, nm in enumerate("ab"):
        yy = 160 + i * 92
        s.rect(56, yy, 66, 44, fill="bluebg", stroke="blue", rx=8)
        s.text(89, yy + 29, nm, TextOpts(size=17, weight="700", color="blue",
                                         mono=True))
    s.rect(232, 178, 232, 96, fill="panel", stroke="blue", rx=10, shadow=True)
    s.text(348, 198, "list   id=0x7f3a21   refcount=2",
           TextOpts(size=10.5, color="muted", mono=True))
    _grid(s, 248, 212, ["1", "2", "3", "4"], 4, 46, 40, 8, fill="bluebg",
          text="blue", size=14)
    s.line(122, 182, 232, 214, color="blue", arrow=True, sw=1.8)
    s.line(122, 274, 232, 242, color="blue", arrow=True, sw=1.8)
    s.panel(56, 300, 408, 84, "", fill="panel2", stroke="line")
    s.mtext(72, 322,
            ["a is b            -> True   (one object, two names)",
             "print(a)          -> [1, 2, 3, 4]   a CHANGED too",
             "This is the #1 source of 'impossible' beginner bugs."],
            TextOpts(size=11, mono=True, anchor="start", color="ink"), lh=18)

    # --- Scene B : rebinding ----------------------------------------------
    scene(500, 468, "B.  REBINDING to a new object", "green",
          "b = a ; b = b + [4]")
    for i, nm in enumerate("ab"):
        yy = 160 + i * 92
        col = "green" if i else "violet"
        s.rect(534, yy, 66, 44, fill="greenbg" if i else "violetbg",
               stroke=col, rx=8)
        s.text(567, yy + 29, nm, TextOpts(size=17, weight="700", color=col,
                                          mono=True))
    s.rect(716, 150, 206, 60, fill="panel", stroke="violet", rx=10,
           shadow=True)
    s.text(819, 170, "list  id=0x7f3a21", TextOpts(size=10.5,
                                                    color="muted", mono=True))
    _grid(s, 732, 178, ["1", "2", "3"], 3, 46, 24, 6, fill="violetbg",
          text="violet", size=12)
    s.rect(716, 254, 236, 60, fill="panel", stroke="green", rx=10,
           shadow=True)
    s.text(834, 274, "list  id=0x9c11b8  NEW",
           TextOpts(size=10.5, color="muted", mono=True))
    _grid(s, 732, 282, ["1", "2", "3", "4"], 4, 46, 24, 6, fill="greenbg",
          text="green", size=12)
    s.line(600, 182, 716, 180, color="violet", arrow=True, sw=1.8)
    s.line(600, 274, 716, 284, color="green", arrow=True, sw=1.8)
    s.panel(534, 330, 418, 54, "", fill="panel2", stroke="line")
    s.mtext(550, 350,
            ["a is b  -> False      print(a) -> [1, 2, 3]  unchanged",
             "b + [4] builds a brand-new list and rebinds b to it."],
            TextOpts(size=11, mono=True, anchor="start", color="ink"), lh=18)

    s.caption(495, 424, "Rule:  `=` never copies an object.  It binds a name.  Use copy.copy() / copy.deepcopy() to duplicate.")
    s.save(path)


def d_mutability(path):
    s = SVG(990, 452, title="Mutable vs immutable")
    s.heading(495, 30, "Two families of objects")

    s.panel(22, 56, 468, 244, "", fill="bg", stroke="violet")
    s.rect(22, 56, 468, 30, fill="violet", stroke=None, rx=10)
    s.rect(22, 74, 468, 12, fill="violet", stroke=None, rx=0)
    s.text(256, 76, "IMMUTABLE  -  value can never change",
           TextOpts(size=12, weight="700", color="bg"))
    _grid(s, 44, 104, ["int", "float", "complex", "bool", "str", "tuple",
                       "frozenset", "bytes", "None"], 3, 138, 30, 10,
          fill="violetbg", text="violet", size=13)
    s.mtext(44, 232,
            ["x = 10 ; x += 1     # a NEW int object is created",
             "s = 'hi' ; s += '!' # a NEW str object is created"],
            TextOpts(size=11, mono=True, anchor="start", color="slate"), lh=17)
    s.text(44, 284, "hashable -> can be dict keys / set members",
           TextOpts(size=11.5, weight="700", anchor="start", color="violet"))

    s.panel(500, 56, 468, 244, "", fill="bg", stroke="green")
    s.rect(500, 56, 468, 30, fill="green", stroke=None, rx=10)
    s.rect(500, 74, 468, 12, fill="green", stroke=None, rx=0)
    s.text(734, 76, "MUTABLE  -  value can change in place",
           TextOpts(size=12, weight="700", color="bg"))
    _grid(s, 522, 104, ["list", "dict", "set", "bytearray", "MyClass()",
                        "deque"], 3, 138, 30, 10, fill="greenbg",
          text="green", size=13)
    s.mtext(522, 232,
            ["a = [1,2] ; a.append(3)  # SAME object, grown",
             "d = {}    ; d['k'] = 1     # SAME object, new entry"],
            TextOpts(size=11, mono=True, anchor="start", color="slate"), lh=17)
    s.text(522, 284, "unhashable -> TypeError if used as a dict key",
           TextOpts(size=11.5, weight="700", anchor="start", color="green"))

    y = 322
    for i, (t, d, k) in enumerate([
            ("Why it matters #1", "Only immutable objects can be dictionary keys or live inside a set.", "violet"),
            ("Why it matters #2", "Immutable objects are safe to share across threads - no locks needed.", "blue"),
            ("Why it matters #3", "A tuple of mutable items is NOT truly immutable: (1, [2]) can change.", "amber")]):
        bx = 22 + i * 320
        s.panel(bx, y, 306, 82, "", fill="panel2", stroke=k)
        s.text(bx + 14, y + 22, t, TextOpts(size=11.5, weight="700",
                                            anchor="start", color=k))
        s.mtext(bx + 14, y + 44, [d[:44], d[44:]] if len(d) > 44 else [d],
                TextOpts(size=11, anchor="start", color="ink"), lh=16)
    s.caption(495, 436, "Mental model: immutable = a value you read; mutable = a container you edit.")
    s.save(path)


def d_refcount(path):
    s = SVG(990, 352, title="Reference counting and garbage collection")
    s.heading(495, 28, "How Python frees memory")
    s.caption(495, 46, "Every object stores a reference count. When it hits zero the memory is reclaimed instantly.")

    stages = [("a = [1,2,3]", 1, "one owner"),
              ("b = a", 2, "two owners"),
              ("del a", 1, "one owner left"),
              ("del b", 0, "refcount 0 -> freed")]
    w, gap = 218, 18
    x = (990 - (4 * w + 3 * gap)) / 2
    for i, (code, rc, note) in enumerate(stages):
        bx = x + i * (w + gap)
        dead = rc == 0
        s.panel(bx, 68, w, 190, "", fill="bg",
                stroke="red" if dead else "line")
        s.rect(bx, 68, w, 26, fill="red" if dead else "slate", stroke=None,
               rx=10)
        s.rect(bx, 84, w, 10, fill="red" if dead else "slate", stroke=None)
        s.text(bx + w / 2, 86, f"stage {i + 1}",
               TextOpts(size=10.5, weight="700", color="bg"))
        s.text(bx + w / 2, 114, code, TextOpts(size=12, mono=True,
                                               weight="600",
                                               color="red" if dead else "ink"))
        s.rect(bx + 34, 132, w - 68, 58, fill="redbg" if dead else "bluebg",
               stroke="red" if dead else "blue", rx=8,
               dashed=dead)
        s.mtext(bx + w / 2, 154, ["[1, 2, 3]", f"ob_refcnt = {rc}"],
                TextOpts(size=11, mono=True, weight="600",
                         color="muted" if dead else "blue"), lh=17)
        s.text(bx + w / 2, 214, note,
               TextOpts(size=11, weight="600",
                        color="red" if dead else "slate"))
        s.text(bx + w / 2, 236, "memory reclaimed" if dead else "alive",
               TextOpts(size=10, italic=True, color="muted"))
        if i:
            s.line(bx - gap, 163, bx, 163, color="slate", arrow=True, sw=1.6)

    s.panel(x, 276, 4 * w + 3 * gap, 62, "", fill="amberbg", stroke="amber")
    s.mtext(x + 16, 298,
            ["Reference counting alone cannot collect CYCLES (a.ref = b; b.ref = a), so CPython also runs a",
             "generational cyclic collector - gc.collect().  Weak references (weakref) break cycles on purpose."],
            TextOpts(size=11.5, anchor="start", color="ink"), lh=18)
    s.save(path)


# ---------------------------------------------------------------------------
# 03 -- operator precedence
# ---------------------------------------------------------------------------
def d_precedence(path):
    rows = [
        ("( )  [ ]  .  ( )call", "grouping, subscript, attribute, call", "f(x).y[0]"),
        ("**", "exponent (right associative!)", "2 ** 3 ** 2 == 512"),
        ("+x   -x   ~x", "unary plus / minus / bitwise not", "-2 ** 2 == -4"),
        ("*   @   /   //   %", "multiply, matmul, divide, floor-div, mod", "7 // 2 == 3   7 % 2 == 1"),
        ("+   -", "addition, subtraction", "1 + 2 - 3"),
        ("<<   >>", "bit shifts", "1 << 4 == 16"),
        ("&", "bitwise AND", "0b1100 & 0b1010"),
        ("^", "bitwise XOR", "5 ^ 3 == 6"),
        ("|", "bitwise OR", "0b1100 | 0b1010"),
        ("==  !=  <  >  <=  >=  is  in", "comparisons (chainable!)", "1 < x < 10"),
        ("not", "boolean NOT", "not done"),
        ("and", "boolean AND (short-circuits)", "a and a.b"),
        ("or", "boolean OR (short-circuits)", "name or 'anon'"),
        (":=", "walrus - assign inside expression", "while (n := f.readline()):"),
        ("=   +=   -=   *=  ...", "assignment (lowest, right to left)", "total += price"),
    ]
    h = 74 + len(rows) * 27 + 92
    s = SVG(990, h, title="Operator precedence")
    s.heading(495, 28, "Operator precedence - strongest at the top")
    s.caption(495, 46, "Python evaluates the highest-precedence operator first. Ties go left-to-right (except ** and assignment).")

    x, y = 40, 66
    cw = [56, 300, 336, 218]
    # strength bar
    s.rect(x, y, 14, len(rows) * 27, fill="none", stroke="line", rx=7)
    for i, (op, mean, ex) in enumerate(rows):
        yy = y + i * 27
        t = i / (len(rows) - 1)
        col = "green" if t < 0.25 else ("blue" if t < 0.55 else
                                        ("amber" if t < 0.8 else "red"))
        s.rect(x, yy, 910, 27, fill="panel" if i % 2 == 0 else "bg",
               stroke=None, rx=0)
        s.badge(x + 18, yy + 4, str(i + 1), fill=col, size=10)
        s.text(x + 78, yy + 18, op, TextOpts(size=12.5, mono=True,
                                             weight="700", anchor="start",
                                             color=col))
        s.text(x + 366, yy + 18, mean, TextOpts(size=11.5, anchor="start",
                                                color="slate"))
        s.text(x + 706, yy + 18, ex, TextOpts(size=11, mono=True,
                                              anchor="start", color="muted"))
    s.rect(x, y, 910, len(rows) * 27, fill=None, stroke="line", rx=6, sw=1.4)
    s.arrowlabel(x + 22, y - 6, "STRONGEST", color="green", size=10)
    s.arrowlabel(x + 890, y + len(rows) * 27 + 10, "WEAKEST", color="red",
                 size=10)

    by = y + len(rows) * 27 + 26
    s.panel(x, by, 910, 50, "", fill="greenbg", stroke="green")
    s.text(x + 18, by + 31,
           "Professional advice: never memorise this table. If you have to think about precedence, add parentheses - "
           "readability beats cleverness.",
           TextOpts(size=11.5, anchor="start", color="ink"))
    s.save(path)


# ---------------------------------------------------------------------------
# 04 -- string slicing
# ---------------------------------------------------------------------------
def d_slicing(path):
    s = SVG(990, 500, title="String indexing and slicing")
    word = "PYTHONISTA"
    n = len(word)
    cw, y, h = 60, 132, 62
    x = (990 - n * cw) / 2
    s.heading(495, 28, "Indexing and slicing")
    s.caption(495, 46, "s[start : stop : step]   -   stop is EXCLUSIVE, negative indices count from the right")

    s.text(x - 40, y + h / 2 + 6, "s", TextOpts(size=22, weight="700",
                                                color="blue", mono=True))
    hi = set(range(2, 6))
    for i, ch in enumerate(word):
        bx = x + i * cw
        on = i in hi
        s.rect(bx, y, cw - 4, h, fill="bluebg" if on else "panel",
               stroke="blue" if on else "line", rx=6, sw=2 if on else 1.4)
        s.text(bx + (cw - 4) / 2, y + h / 2 + 8, ch,
               TextOpts(size=21, weight="700", color="blue" if on else "ink",
                        mono=True))
        s.text(bx + (cw - 4) / 2, y - 12, str(i),
               TextOpts(size=12, weight="600", color="slate", mono=True))
        s.text(bx + (cw - 4) / 2, y + h + 22, str(i - n),
               TextOpts(size=12, weight="600", color="muted", mono=True))

    s.text(x - 6, y - 12, "+index", TextOpts(size=10, anchor="end",
                                             color="slate", italic=True))
    s.text(x - 6, y + h + 22, "-index", TextOpts(size=10, anchor="end",
                                                 color="muted", italic=True))

    # slice boundary markers
    for pos, lab, col in [(2, "start = 2", "green"), (6, "stop = 6", "red")]:
        lx = x + pos * cw - 2
        s.line(lx, y - 34, lx, y + h + 34, color=col, sw=2, dashed=True)
        s.arrowlabel(lx, y - 42, lab, color=col, size=11)
    s.poly([(x + 2 * cw - 2, y + h + 46), (x + 6 * cw - 2, y + h + 46)],
           color="blue", sw=2.4)
    s.text(x + 4 * cw, y + h + 66, "s[2:6]  ->  'THON'   (indices 2,3,4,5 - stop excluded)",
           TextOpts(size=12.5, weight="700", color="blue", mono=True))

    ex = [("s[0]", "'P'", "first character"),
          ("s[-1]", "'A'", "last character"),
          ("s[2:]", "'THONISTA'", "from 2 to the end"),
          ("s[:4]", "'PYTH'", "up to (not incl.) 4"),
          ("s[::2]", "'PTOSIA'", "every second char"),
          ("s[::-1]", "'ATSINOHTYP'", "reversed - classic idiom")]
    yy = table(s, 60, y + h + 92, ["expression", "result", "meaning"],
               [[e[0], e[1], e[2]] for e in ex], [170, 220, 440],
               rowh=26, headh=28, size=11.5, mono_cols=(0, 1))
    s.caption(495, yy + 16, "Slicing never raises IndexError - out-of-range bounds are simply clamped.")
    s.save(path)


def d_encoding(path):
    s = SVG(990, 336, title="str vs bytes")
    s.heading(495, 28, "Text is str, storage is bytes")
    s.caption(495, 46, "Encoding turns characters into bytes; decoding turns bytes back into characters.")

    s.rect(60, 84, 340, 110, fill="violetbg", stroke="violet", rx=12,
           shadow=True)
    s.text(230, 110, "str  (unicode text)",
           TextOpts(size=13, weight="700", color="violet"))
    s.text(230, 142, "'caf\u00e9  \u09a8\u09ae\u09b8\u09cd\u09a4\u09c7  \U0001F600'",
           TextOpts(size=19, weight="600", color="ink", mono=True))
    s.text(230, 172, "len('caf\u00e9') == 4  characters",
           TextOpts(size=11, color="slate", mono=True))

    s.rect(590, 84, 340, 110, fill="greenbg", stroke="green", rx=12,
           shadow=True)
    s.text(760, 110, "bytes  (raw 0-255 values)",
           TextOpts(size=13, weight="700", color="green"))
    s.text(760, 142, "b'caf\\xc3\\xa9'", TextOpts(size=17, weight="600",
                                                 color="ink", mono=True))
    s.text(760, 172, "len('caf\u00e9'.encode()) == 5  bytes",
           TextOpts(size=11, color="slate", mono=True))

    s.line(400, 118, 590, 118, color="violet", sw=2.4, arrow=True)
    s.arrowlabel(495, 108, ".encode('utf-8')", color="violet", size=11.5)
    s.line(590, 162, 400, 162, color="green", sw=2.4, arrow=True)
    s.arrowlabel(495, 184, ".decode('utf-8')", color="green", size=11.5)

    s.panel(60, 214, 870, 96, "", fill="redbg", stroke="red")
    s.text(78, 238, "The golden rule of I/O",
           TextOpts(size=12.5, weight="700", anchor="start", color="red"))
    s.mtext(78, 260,
            ["DECODE on the way IN (bytes -> str as early as possible)  and  ENCODE on the way OUT (str -> bytes as late as possible).",
             "Always name the encoding explicitly: open(path, encoding='utf-8').  Never rely on the platform default -",
             "that is exactly how a file written on Linux becomes mojibake when opened on Windows."],
            TextOpts(size=11.5, anchor="start", color="ink"), lh=17)
    s.save(path)


# ---------------------------------------------------------------------------
# 05 -- control flow
# ---------------------------------------------------------------------------
def d_if_flow(path):
    s = SVG(760, 512, title="if / elif / else")
    s.heading(380, 28, "Branching: if / elif / else")
    flowchart_step(s, 290, 52, 180, 36, "start", kind="slate", shape="terminal")
    s.line(380, 88, 380, 112, color="slate", arrow=True)
    flowchart_step(s, 300, 112, 160, 84, "condition 1?", kind="blue",
                   shape="diamond")
    s.line(380, 196, 380, 220, color="slate", arrow=True)
    s.arrowlabel(398, 210, "False", color="red", size=11)
    s.line(460, 154, 600, 154, color="green", arrow=True, sw=2)
    s.arrowlabel(530, 144, "True", color="green", size=11)
    flowchart_step(s, 600, 126, 140, 56, "block A", "runs, then skips rest",
                   kind="green")
    flowchart_step(s, 300, 220, 160, 84, "condition 2?", kind="blue",
                   shape="diamond")
    s.line(460, 262, 600, 262, color="green", arrow=True, sw=2)
    s.arrowlabel(530, 252, "True", color="green", size=11)
    flowchart_step(s, 600, 234, 140, 56, "block B", "elif branch",
                   kind="green")
    s.line(380, 304, 380, 330, color="slate", arrow=True)
    s.arrowlabel(398, 322, "False", color="red", size=11)
    flowchart_step(s, 600, 330, 140, 56, "block C", "else - the fallback",
                   kind="amber")
    s.elbow(380, 330, 600, 358, color="slate", arrow=True, bend="h")
    s.poly([(740, 154), (752, 154), (752, 448), (470, 448)], color="slate",
           sw=1.8)
    s.poly([(740, 262), (752, 262)], color="slate", sw=1.8)
    s.poly([(740, 358), (752, 358)], color="slate", sw=1.8)
    s.line(470, 448, 380, 448, color="slate", arrow=True, sw=1.8)
    flowchart_step(s, 290, 430, 180, 36, "continue after", kind="slate",
                   shape="terminal")
    s.panel(30, 336, 300, 128, "", fill="panel2", stroke="line")
    s.text(46, 358, "How Python sees it",
           TextOpts(size=11.5, weight="700", anchor="start", color="slate"))
    s.mtext(46, 380,
            ["elif is not a keyword - the parser",
             "reads it as `else: if ...`.",
             "Exactly ONE branch runs, or none",
             "if there is no else at all."],
            TextOpts(size=11, anchor="start", color="ink"), lh=17)
    s.save(path)


def d_loop_else(path):
    s = SVG(990, 486, title="for / while ... else")
    s.heading(495, 28, "Loops, break, and the rarely-known `else` clause")
    flowchart_step(s, 70, 46, 150, 34, "start", kind="slate", shape="terminal")
    s.line(145, 80, 145, 104, color="slate", arrow=True)
    flowchart_step(s, 55, 104, 180, 52, "for / while", "loop header",
                   kind="blue")
    s.line(145, 156, 145, 186, color="slate", arrow=True)
    flowchart_step(s, 75, 186, 140, 86, "more items?", kind="blue",
                   shape="diamond")
    s.line(215, 229, 310, 229, color="green", arrow=True, sw=2)
    s.arrowlabel(262, 219, "yes", color="green", size=11)
    flowchart_step(s, 310, 200, 190, 58, "loop body", "your statements",
                   kind="green")
    s.line(405, 258, 405, 298, color="slate", arrow=True)
    flowchart_step(s, 325, 298, 160, 82, "break hit?", kind="amber",
                   shape="diamond")
    s.poly([(325, 339), (272, 339), (272, 130), (235, 130)], color="slate",
           sw=1.8, arrow=True)
    s.arrowlabel(292, 300, "no", color="slate", size=11)
    s.poly([(485, 339), (770, 339), (770, 366)], color="red", sw=2, arrow=True)
    s.arrowlabel(600, 329, "yes -> jump straight out, SKIPPING else",
                 color="red", size=11)
    s.line(145, 272, 145, 356, color="violet", arrow=True, sw=2)
    s.arrowlabel(150, 316, "exhausted", color="violet", size=11)
    flowchart_step(s, 45, 356, 200, 62, "else: block",
                   "ONLY if no break happened", kind="violet")
    s.elbow(245, 387, 770, 387, color="slate", arrow=True, bend="h")
    flowchart_step(s, 690, 366, 160, 42, "after the loop", kind="slate",
                   shape="terminal")

    s.panel(560, 62, 408, 200, "", fill="violetbg", stroke="violet")
    s.text(576, 86, "The search idiom this enables",
           TextOpts(size=12, weight="700", anchor="start", color="violet"))
    s.mtext(576, 110,
            ["for user in users:",
             "    if user.is_admin:",
             "        print(user)",
             "        break",
             "else:",
             "    print('no admin found')"],
            TextOpts(size=11.5, mono=True, anchor="start", color="ink"), lh=18)
    s.text(576, 240, "No flag variable needed - the else IS the 'not found' branch.",
           TextOpts(size=10.5, italic=True, anchor="start", color="slate"))
    s.caption(495, 468, "`while ... else` behaves identically: else runs when the condition becomes false, not on break.")
    s.save(path)


def d_match(path):
    s = SVG(990, 478, title="match / structural pattern matching")
    s.heading(495, 28, "match: structural pattern matching (3.10+)")
    s.caption(495, 46, "Not a switch statement - it DESTRUCTURES values against patterns.")

    pats = [("Literal", "case 404:", "matches an exact value", "blue"),
            ("Capture", "case name:", "binds anything to a name", "blue"),
            ("Wildcard", "case _:", "matches everything, binds nothing", "slate"),
            ("Sequence", "case [x, y]:", "list/tuple of that shape", "green"),
            ("Sequence *", "case [first, *rest]:", "captures the tail", "green"),
            ("Mapping", "case {'id': i}:", "dict having that key", "amber"),
            ("Class", "case Point(x=0, y=y):", "instance + attribute test", "violet"),
            ("OR", "case 'a' | 'b':", "either pattern", "cyan"),
            ("Guard", "case n if n > 0:", "pattern + boolean condition", "red")]
    w, h, gap = 300, 92, 14
    x0 = (990 - (3 * w + 2 * gap)) / 2
    for i, (nm, code, mean, k) in enumerate(pats):
        r, cc = divmod(i, 3)
        bx, by = x0 + cc * (w + gap), 70 + r * (h + gap)
        s.panel(bx, by, w, h, "", fill="bg", stroke=k)
        s.rect(bx, by, 5, h, fill=k, stroke=None, rx=2)
        s.text(bx + 18, by + 22, nm, TextOpts(size=12, weight="700",
                                              anchor="start", color=k))
        s.text(bx + 18, by + 48, code, TextOpts(size=12.5, mono=True,
                                                weight="600", anchor="start",
                                                color="ink"))
        s.text(bx + 18, by + 72, mean, TextOpts(size=10.5, anchor="start",
                                                color="muted"))
    yy = 70 + 3 * (h + gap) + 6
    s.panel(x0, yy, 3 * w + 2 * gap, 62, "", fill="amberbg", stroke="amber")
    s.mtext(x0 + 16, yy + 24,
            ["Careful: `case Point(x=0)` matches only keyword-style fields declared in __match_args__.",
             "A bare `case x:` shadows everything below it - always put the wildcard/capture case LAST."],
            TextOpts(size=11.5, anchor="start", color="ink"), lh=18)
    s.save(path)


# ---------------------------------------------------------------------------
# 06 -- data structures
# ---------------------------------------------------------------------------
def d_ds_choice(path):
    s = SVG(990, 596, title="Choosing a data structure")
    s.heading(495, 28, "Which container should I use?")
    flowchart_step(s, 375, 52, 240, 46, "What do you need?", kind="slate",
                   shape="diamond")

    branches = [
        (30, "Ordered collection\nyou will change", "list", "[1, 2, 3]",
         "append O(1), index O(1), search O(n)", "blue"),
        (222, "Fixed record\nheterogeneous fields", "tuple /\nnamedtuple", "(3, 'ada')",
         "immutable, hashable, unpackable", "violet"),
        (414, "Key -> value\nlookups", "dict", "{'id': 7}",
         "get O(1), insertion-ordered since 3.7", "green"),
        (606, "Uniqueness or\nfast membership", "set", "{1, 2, 3}",
         "in O(1), union/intersect/difference", "amber"),
        (798, "Frequent inserts at\nBOTH ends", "collections.deque", "deque([1,2])",
         "appendleft/pop O(1) - list is O(n)", "cyan"),
    ]
    y, h, w = 168, 132, 172
    for bx, need, name, ex, note, k in branches:
        s.line(495, 98, bx + w / 2, 140, color="line", sw=1.6, arrow=True)
        s.panel(bx, y, w, h, "", fill="bg", stroke=k)
        s.mtext(bx + w / 2, y + 24, need.split("\n"),
                TextOpts(size=10.5, color="muted"), lh=13)
        s.mtext(bx + w / 2, y + 62, name.split("\n"),
                TextOpts(size=13, weight="700", color=k, mono=True), lh=16)
        s.rect(bx + 12, y + 78, w - 24, 20, fill="panel2", stroke=None, rx=4)
        s.text(bx + w / 2, y + 92, ex, TextOpts(size=10, mono=True,
                                                color="slate"))
        s.mtext(bx + 10, y + 114, [note[:26], note[26:]],
                TextOpts(size=9.5, anchor="start", color="ink"), lh=12)

    yy = table(s, 60, y + h + 34,
               ["operation", "list", "tuple", "dict", "set", "deque"],
               [["index  a[i]", "+O(1)", "+O(1)", "+O(1) by key", "-none", "+O(1) at ends"],
                ["search  x in a", "-O(n)", "-O(n)", "+O(1) keys", "+O(1)", "-O(n)"],
                ["append at end", "+O(1)*", "!fixed size", "+O(1)", "+O(1)", "+O(1)"],
                ["insert at front", "-O(n)", "!fixed size", "-n/a", "-n/a", "+O(1)"],
                ["delete by value", "-O(n)", "!immutable", "+O(1) by key", "+O(1)", "-O(n)"],
                ["sort", "+built-in", "-no (immutable)", "-no", "-no", "-no"],
                ["hashable (dict key)?", "-no", "+yes", "-no", "-no", "-no"]],
               [186, 128, 128, 150, 118, 160], rowh=27, headh=30, size=11.5)
    s.caption(495, yy + 18,
              "* O(1) amortised: a list over-allocates capacity so most appends never copy the whole array.")
    s.save(path)


def d_list_memory(path):
    s = SVG(990, 372, title="How a list is stored")
    s.heading(495, 28, "A list is an array of POINTERS, not of values")
    s.caption(495, 46, "That single fact explains mixed types, aliasing, and why `a[i] = x` is O(1) but `x in a` is O(n).")

    s.rect(48, 96, 250, 150, fill="panel", stroke="blue", rx=10, shadow=True)
    s.text(173, 120, "list object", TextOpts(size=12.5, weight="700",
                                             color="blue"))
    for i, (f, v) in enumerate([("ob_refcnt", "1"), ("ob_type", "list"),
                                ("ob_size", "4"), ("ob_item", "->")]):
        yy = 134 + i * 26
        s.text(64, yy + 12, f, TextOpts(size=11, mono=True, anchor="start",
                                        color="slate"))
        s.text(282, yy + 12, v, TextOpts(size=11, mono=True, anchor="end",
                                         weight="700", color="ink"))

    cells = ["1", "'two'", "3.0", "[4]"]
    kinds = ["violet", "amber", "green", "cyan"]
    x0, y0, cw, ch = 380, 150, 66, 44
    for i in range(4):
        s.rect(x0 + i * (cw + 6), y0, cw, ch, fill="bluebg", stroke="blue",
               rx=6)
        s.text(x0 + i * (cw + 6) + cw / 2, y0 - 10, f"[{i}]",
               TextOpts(size=10, mono=True, color="muted"))
    s.line(298, 226, 380, 172, color="blue", arrow=True, sw=1.8)
    s.arrowlabel(338, 216, "ob_item", color="blue", size=10)

    for i, (val, k) in enumerate(zip(cells, kinds)):
        ex, ey = 380 + i * (cw + 6), 250
        s.line(ex + cw / 2, y0 + ch, ex + cw / 2, ey, color=k, arrow=True,
               sw=1.6)
        s.rect(ex - 8, ey, cw + 16, 44, fill=f"{k}bg", stroke=k, rx=8)
        s.text(ex + cw / 2, ey + 28, val, TextOpts(size=12, mono=True,
                                                   weight="700", color=k))
        s.text(ex + cw / 2, ey + 62, "separate object",
               TextOpts(size=9, color="muted", italic=True))

    s.panel(700, 96, 262, 218, "", fill="panel2", stroke="line")
    s.text(716, 120, "Consequences", TextOpts(size=12, weight="700",
                                               anchor="start", color="slate"))
    s.mtext(716, 144,
            ["* each slot holds a reference,",
             "  so types can differ",
             "* copying a list copies the",
             "  POINTERS, not the objects",
             "* a[1] is a pointer chase:",
             "  ~2-3x slower than a C array",
             "* over-allocation makes",
             "  append amortised O(1)"],
            TextOpts(size=10.5, anchor="start", color="ink", mono=False),
            lh=17)
    s.caption(495, 348, "Shallow copy a[:], list(a), a.copy() all duplicate pointers. Deep-copy nested data with copy.deepcopy().")
    s.save(path)


def d_dict_hash(path):
    s = SVG(990, 452, title="How a dict works")
    s.heading(495, 28, "Inside a dictionary: hash -> index -> entry")

    s.rect(40, 96, 220, 56, fill="greenbg", stroke="green", rx=10,
           shadow=True)
    s.text(150, 120, "key: 'name'", TextOpts(size=12.5, mono=True,
                                             weight="700"))
    s.text(150, 140, "hash('name')", TextOpts(size=10, color="slate",
                                              mono=True))
    s.line(260, 124, 330, 124, color="green", arrow=True, sw=2)
    s.arrowlabel(296, 112, "hash()", color="green", size=11)

    s.rect(330, 96, 180, 56, fill="amberbg", stroke="amber", rx=10,
           shadow=True)
    s.text(420, 120, "0x9f31c2a4...", TextOpts(size=12, mono=True,
                                                weight="700"))
    s.text(420, 140, "-> % table_size", TextOpts(size=10, color="slate",
                                                 mono=True))
    s.line(510, 124, 580, 124, color="amber", arrow=True, sw=2)
    s.arrowlabel(546, 112, "slot 3", color="amber", size=11)

    s.panel(580, 66, 382, 250, "", fill="bg", stroke="blue")
    s.text(596, 88, "hash table (sparse indices -> dense entries)",
           TextOpts(size=11, weight="700", anchor="start", color="blue"))
    hdr = ["idx", "-> entry"]
    rows = [["0", "~empty"], ["1", "~empty"], ["2", "~empty"],
            ["3", "**entry 0"], ["4", "~empty"], ["5", "**entry 1"]]
    yy = table(s, 596, 100, hdr, rows, [70, 110], rowh=24, headh=26,
               size=11, mono_cols=(0, 1))
    s.rect(796, 100, 150, 26, fill="slate", stroke=None, rx=6)
    s.rect(796, 120, 150, 6, fill="slate", stroke=None, rx=0)
    s.text(871, 117, "entries (dense)", TextOpts(size=11, weight="700",
                                                  color="bg"))
    for i, (hsh, k, v) in enumerate([("hash", "key", "value"),
                                     ("h0", "'name'", "'ada'"),
                                     ("h1", "'age'", "36")]):
        ry = 126 + i * 26
        s.rect(796, ry, 150, 26, fill="panel" if i else "slatebg",
               stroke="line", rx=0, sw=1)
        s.text(871, ry + 17, f"{hsh} | {k} | {v}",
               TextOpts(size=10, mono=True,
                        color="bg" if i == 0 else "ink",
                        weight="700" if i == 0 else "400"))

    s.panel(40, 190, 500, 126, "", fill="panel2", stroke="line")
    s.text(56, 212, "Why dicts are so fast - and so ordered",
           TextOpts(size=12, weight="700", anchor="start", color="slate"))
    s.mtext(56, 236,
            ["* lookup does not scan: it jumps straight to a slot  ->  O(1)",
             "* since 3.6 the table is split: a sparse index array + a dense",
             "  entry array, which is ~25% smaller AND keeps insertion order",
             "* collisions are resolved by probing, then the table is resized"],
            TextOpts(size=11, anchor="start", color="ink"), lh=18)

    s.panel(40, 336, 922, 76, "", fill="redbg", stroke="red")
    s.text(56, 358, "The contract you must keep",
           TextOpts(size=12, weight="700", anchor="start", color="red"))
    s.mtext(56, 380,
            ["A key must be HASHABLE: __hash__() must stay constant and equal keys must have equal hashes.",
             "Mutating a key after inserting it corrupts the table silently - which is why lists can never be keys."],
            TextOpts(size=11.5, anchor="start", color="ink"), lh=18)
    s.save(path)


def d_bigO(path):
    s = SVG(990, 472, title="Growth of complexity classes")
    s.heading(495, 28, "How cost grows with input size n")
    s.caption(495, 46, "Same algorithm, different n. The gap between O(n) and O(n\u00b2) is what turns 1 s into 3 hours.")

    ox, oy, w, h = 90, 330, 520, 230
    s.line(ox, oy, ox + w, oy, color="ink", sw=1.8, arrow=True)
    s.line(ox, oy, ox, oy - h, color="ink", sw=1.8, arrow=True)
    s.text(ox + w + 14, oy + 5, "n", TextOpts(size=12, weight="700",
                                              anchor="start", color="ink"))
    s.text(ox - 12, oy - h - 10, "work", TextOpts(size=12, weight="700",
                                                  anchor="end", color="ink"))
    import math
    curves = [("O(1)", "green", lambda t: 0.06),
              ("O(log n)", "cyan", lambda t: 0.10 + 0.16 * math.log(1 + 9 * t)),
              ("O(n)", "blue", lambda t: 0.06 + 0.42 * t),
              ("O(n log n)", "amber", lambda t: 0.06 + 0.55 * t * math.log(1 + 9 * t) / math.log(10) / 1.05),
              ("O(n\u00b2)", "red", lambda t: 0.06 + 0.95 * t * t),
              ("O(2\u207f)", "violet", lambda t: 0.02 + 1.0 * (math.pow(2, 6 * t) - 1) / 63)]
    for lab, col, fn in curves:
        pts = []
        for i in range(61):
            t = i / 60
            v = min(fn(t), 1.0)
            pts.append((ox + t * w, oy - v * h))
        s.poly(pts, color=col, sw=2.2, arrow=False, rounded=True)
    leg = [(l, cc) for l, cc, _ in curves]
    for i, (lab, col) in enumerate(leg):
        lx, ly = ox + w + 46, oy - h + 20 + i * 26
        s.rect(lx, ly - 12, 26, 4, fill=col, stroke=None, rx=2)
        s.text(lx + 36, ly - 4, lab, TextOpts(size=12, weight="700",
                                              anchor="start", color=col,
                                              mono=True))
    ex = {"O(1)": "dict lookup, list index",
          "O(log n)": "binary search, sortedcontainers",
          "O(n)": "sum(), linear scan",
          "O(n log n)": "sorted(), merge sort",
          "O(n\u00b2)": "nested loops, bubble sort",
          "O(2\u207f)": "naive subsets, recursive fib"}
    for i, (lab, col) in enumerate(leg):
        lx, ly = ox + w + 46, oy - h + 34 + i * 26
        s.text(lx + 36, ly + 10, ex[lab], TextOpts(size=9.5, anchor="start",
                                                   color="muted",
                                                   italic=True))
    yy = table(s, 90, 348, ["n", "O(n)", "O(n\u00b2)", "O(2\u207f)"],
               [["10", "10 ops", "100 ops", "1,024 ops"],
                ["1,000", "1,000 ops", "1,000,000 ops", "~10\u00b3\u2070\u2070 ops"],
                ["1,000,000", "10\u2076 ops", "10\u00b9\u00b2 ops (~31 years)", "~heat death of the universe"]],
               [150, 150, 240, 260], rowh=26, headh=28, size=11)
    s.save(path)


DIAGRAMS = {
    "python-execution.svg": d_execution,
    "dev-toolchain.svg": d_toolchain,
    "memory-model.svg": d_memory,
    "mutable-vs-immutable.svg": d_mutability,
    "reference-counting.svg": d_refcount,
    "operator-precedence.svg": d_precedence,
    "string-slicing.svg": d_slicing,
    "string-encoding.svg": d_encoding,
    "if-elif-else.svg": d_if_flow,
    "loop-break-else.svg": d_loop_else,
    "match-patterns.svg": d_match,
    "choosing-containers.svg": d_ds_choice,
    "list-memory-layout.svg": d_list_memory,
    "dict-hash-table.svg": d_dict_hash,
    "complexity-growth.svg": d_bigO,
}
