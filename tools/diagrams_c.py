"""Figures for modules 13-18."""

from __future__ import annotations

from svgkit import SVG, TextOpts, c, flowchart_step, table


# ---------------------------------------------------------------------------
# 13 -- decorators
# ---------------------------------------------------------------------------
def d_decorator_layers(path):
    s = SVG(990, 452, title="Stacked decorators")
    s.heading(495, 28, "Decorators wrap: the one closest to the function runs first")
    s.caption(495, 46, "@a  @b  @c  def f()  ==  f = a(b(c(f)))   -   but at CALL time the outer layer executes first")

    layers = [("a - logging", "red", 40, "outermost: applied last, entered first"),
              ("b - timing", "amber", 76, "middle"),
              ("c - retry", "green", 112, "innermost: applied first, closest to the code"),
              ("def f()  ->  your actual logic", "blue", 148, "the wrapped function")]
    for i, (lab, k, inset, note) in enumerate(layers):
        y = 76 + i * 44
        w = 520 - inset * 2
        s.rect(120 + inset, y, w, 40, fill=f"{k}bg", stroke=k, rx=10,
               sw=1.8 if i == 3 else 1.5)
        s.text(120 + inset + w / 2, y + 25, lab,
               TextOpts(size=12, weight="700", color=k, mono=True))
        s.text(680, y + 25, note, TextOpts(size=10.5, anchor="start",
                                           color="muted"))

    s.line(96, 96, 96, 240, color="slate", arrow=True, sw=2)
    s.arrowlabel(96, 262, "call goes IN", color="slate", size=10.5)
    s.line(660, 240, 660, 96, color="violet", arrow=True, sw=2)
    s.arrowlabel(660, 262, "result comes OUT", color="violet", size=10.5)

    s.panel(120, 286, 380, 148, "", fill="panel2", stroke="line")
    s.text(136, 308, "The template you should memorise",
           TextOpts(size=12, weight="700", anchor="start", color="slate"))
    s.mtext(136, 332,
            ["def deco(fn):",
             "    @functools.wraps(fn)      # keep __name__/__doc__",
             "    def wrapper(*a, **kw):",
             "        ...before...",
             "        result = fn(*a, **kw)",
             "        ...after...",
             "        return result",
             "    return wrapper"],
            TextOpts(size=10, mono=True, anchor="start", color="ink"), lh=13)

    s.panel(520, 286, 440, 148, "", fill="redbg", stroke="red")
    s.text(536, 308, "Forgetting functools.wraps is a real bug",
           TextOpts(size=12, weight="700", anchor="start", color="red"))
    s.mtext(536, 332,
            ["Without it the decorated function is named 'wrapper':",
             "* help(f) and stack traces show the wrong name",
             "* pytest cannot discover test_* functions any more",
             "* FastAPI/inspect cannot read the signature, so",
             "  dependency injection and OpenAPI docs break"],
            TextOpts(size=10.5, anchor="start", color="ink"), lh=17)
    s.save(path)


def d_decorator_uses(path):
    s = SVG(990, 434, title="Decorators in the wild")
    s.heading(495, 28, "Where you will actually meet decorators")
    uses = [("@staticmethod\n@classmethod", "no instance / class-bound behaviour", "blue"),
            ("@property", "computed attribute with a getter/setter", "blue"),
            ("@dataclass", "generates __init__, __repr__, __eq__", "violet"),
            ("@functools.lru_cache", "memoisation - free speed-up", "green"),
            ("@functools.wraps", "preserves metadata of the wrapped fn", "green"),
            ("@app.get('/users')", "route registration - Flask / FastAPI", "amber"),
            ("@pytest.fixture\n@pytest.mark.parametrize", "test setup and data-driven tests", "amber"),
            ("@retry(times=3)", "resilience: backoff around flaky I/O", "red"),
            ("@require_auth", "cross-cutting policy: authz, rate limits", "red"),
            ("@timeit / @log_call", "observability without touching business code", "cyan"),
            ("@abstractmethod", "forces subclasses to implement", "cyan"),
            ("@deprecated", "warns callers, keeps old code working", "slate")]
    w, h, gap = 300, 62, 12
    x0 = (990 - (3 * w + 2 * gap)) / 2
    for i, (nm, desc, k) in enumerate(uses):
        r, cc = divmod(i, 3)
        bx, by = x0 + cc * (w + gap), 58 + r * (h + gap)
        s.panel(bx, by, w, h, "", fill="bg", stroke=k)
        s.rect(bx, by, 5, h, fill=k, stroke=None, rx=2)
        s.mtext(bx + 16, by + 22, nm.split("\n"),
                TextOpts(size=11.5, mono=True, weight="700",
                         anchor="start", color=k), lh=15)
        s.text(bx + 16, by + (44 if "\n" not in nm else 54), desc,
               TextOpts(size=10.5, anchor="start", color="muted"))
    yy = 58 + 4 * (h + gap) + 4
    s.panel(x0, yy, 3 * w + 2 * gap, 56, "", fill="greenbg", stroke="green")
    s.text(495, yy + 24, "The unifying idea: a decorator adds CROSS-CUTTING behaviour (logging, caching, security, retries)",
           TextOpts(size=11.5, color="ink"))
    s.text(495, yy + 42, "to many functions at once, without editing a single line of their bodies. That is the whole point.",
           TextOpts(size=11.5, color="ink"))
    s.save(path)


# ---------------------------------------------------------------------------
# 14 -- typing
# ---------------------------------------------------------------------------
def d_typing(path):
    s = SVG(990, 512, title="Dynamic vs static typing")
    s.heading(495, 28, "Type hints are documentation that a machine can check")
    s.caption(495, 46, "Python never enforces annotations at runtime - mypy / pyright do, before the code ever runs.")

    s.panel(22, 68, 468, 200, "", fill="bg", stroke="amber")
    s.rect(22, 68, 468, 30, fill="amber", stroke=None, rx=10)
    s.rect(22, 86, 468, 12, fill="amber", stroke=None, rx=0)
    s.text(256, 88, "WITHOUT hints - discovered in production",
           TextOpts(size=12, weight="700", color="bg"))
    s.mtext(42, 120,
            ["def discount(price, pct):",
             "    return price - price * pct",
             "",
             "discount('100', 0.1)   # TypeError at runtime,",
             "                       # after the deploy"],
            TextOpts(size=11.5, mono=True, anchor="start", color="ink"), lh=18)
    s.text(42, 232, "The editor can only guess; autocomplete is blind.",
           TextOpts(size=11, anchor="start", color="red"))
    s.text(42, 252, "Bugs surface in the logs, at 2 a.m.",
           TextOpts(size=11, anchor="start", color="red"))

    s.panel(500, 68, 468, 200, "", fill="bg", stroke="green")
    s.rect(500, 68, 468, 30, fill="green", stroke=None, rx=10)
    s.rect(500, 86, 468, 12, fill="green", stroke=None, rx=0)
    s.text(734, 88, "WITH hints - caught on your laptop",
           TextOpts(size=12, weight="700", color="bg"))
    s.mtext(520, 120,
            ["def discount(price: Decimal, pct: float) -> Decimal:",
             "    return price * (Decimal(1) - Decimal(str(pct)))",
             "",
             "discount('100', 0.1)",
             "# mypy: Argument 1 has incompatible type \"str\""],
            TextOpts(size=11, mono=True, anchor="start", color="ink"), lh=18)
    s.text(520, 232, "Editors get real completion, go-to-def, refactors.",
           TextOpts(size=11, anchor="start", color="green"))
    s.text(520, 252, "CI fails the pull request before merge.",
           TextOpts(size=11, anchor="start", color="green"))

    yy = table(s, 22, 288, ["concept", "example", "when to reach for it"],
               [["Optional / union", "str | None", "a value that may be absent (3.10+ syntax)"],
                ["container generics", "list[int], dict[str, User]", "everywhere - collections are the common case"],
                ["Callable", "Callable[[int], str]", "callbacks, strategies, decorators"],
                ["Protocol", "class Sized(Protocol): ...", "structural typing - 'duck typing, checked'"],
                ["TypeVar / Generic", "def first(xs: Sequence[T]) -> T", "reusable algorithms that preserve types"],
                ["Literal", "Literal['fast', 'slow']", "replaces stringly-typed parameters"],
                ["TypedDict", "class Row(TypedDict): id: int", "dicts with a fixed shape (JSON payloads)"]],
               [176, 300, 460], rowh=25, headh=28, size=11, mono_cols=(1,))
    s.save(path)


# ---------------------------------------------------------------------------
# 15 -- testing
# ---------------------------------------------------------------------------
def d_pyramid(path):
    s = SVG(990, 400, title="The test pyramid")
    s.heading(495, 28, "The test pyramid - and why the shape matters")
    tiers = [("E2E / UI", 180, "red", "few, slow, brittle, expensive",
              "selenium, playwright - a handful of critical journeys"),
             ("Integration", 380, "amber", "some, moderate speed",
              "real database / HTTP client against a test server"),
             ("Unit", 620, "green", "many, milliseconds, precise",
              "one function or class; no I/O, no network")]
    y = 66
    for i, (nm, w, k, cost, ex) in enumerate(tiers):
        x = (990 - w) / 2 - 140
        hgt = 62
        pts = [(x + (60 if i else 0), y), (x + w - (60 if i else 0), y),
               (x + w, y + hgt), (x, y + hgt)] if i == 0 else \
              [(x, y), (x + w, y), (x + w + 40, y + hgt), (x - 40, y + hgt)]
        s.poly(pts, color=k, sw=2, fill=f"{k}bg", arrow=False)
        s.text(x + w / 2, y + 28, nm, TextOpts(size=15, weight="700",
                                               color=k))
        s.text(x + w / 2, y + 48, cost, TextOpts(size=10.5, color="slate"))
        s.text(x + w + 78, y + 34, ex, TextOpts(size=11, anchor="start",
                                                color="muted"))
        y += hgt + 8

    s.panel(40, 292, 440, 92, "", fill="greenbg", stroke="green")
    s.text(56, 314, "The 80/15/5 shape", TextOpts(size=12, weight="700",
                                                  anchor="start",
                                                  color="green"))
    s.mtext(56, 336,
            ["Mostly unit tests: fast feedback, they tell you WHERE it broke.",
             "A thin integration layer proves the seams really connect.",
             "A few E2E tests prove the product works for a real user."],
            TextOpts(size=10.5, anchor="start", color="ink"), lh=16)
    s.panel(500, 292, 450, 92, "", fill="redbg", stroke="red")
    s.text(516, 314, "The ice-cream anti-pattern",
           TextOpts(size=12, weight="700", anchor="start", color="red"))
    s.mtext(516, 336,
            ["Teams that invert the pyramid end up with thousands of slow,",
             "flaky E2E tests, a 40-minute CI run and no trust in green.",
             "If a test needs a database to test arithmetic, it is misplaced."],
            TextOpts(size=10.5, anchor="start", color="ink"), lh=16)
    s.save(path)


def d_pytest_flow(path):
    s = SVG(990, 372, title="How pytest runs a test")
    s.heading(495, 28, "Anatomy of a pytest run")
    steps = [("collect", "find test_*.py and\ntest_* functions", "blue"),
             ("setup fixtures", "resolve the dependency\ngraph, run yields' head", "violet"),
             ("run test", "call the function,\nassert statements", "green"),
             ("teardown", "run code after yield,\nclose resources", "amber"),
             ("report", "pass / fail / xfail,\ncoverage, durations", "cyan")]
    w, gap, y, h = 168, 16, 70, 100
    x = (990 - (5 * w + 4 * gap)) / 2
    for i, (nm, desc, k) in enumerate(steps):
        bx = x + i * (w + gap)
        s.panel(bx, y, w, h, "", fill="bg", stroke=k)
        s.rect(bx, y, w, 28, fill=k, stroke=None, rx=10)
        s.rect(bx, y + 18, w, 10, fill=k, stroke=None, rx=0)
        s.text(bx + w / 2, y + 19, f"{i + 1}. {nm}",
               TextOpts(size=11.5, weight="700", color="bg"))
        s.mtext(bx + w / 2, y + 56, desc.split("\n"),
                TextOpts(size=10.5, color="slate"), lh=15)
        if i:
            s.line(bx - gap, y + h / 2, bx, y + h / 2, color="line",
                   arrow=True, sw=1.6)

    s.panel(x, 196, 442, 152, "", fill="panel2", stroke="line")
    s.text(x + 16, 218, "Fixtures are dependency injection",
           TextOpts(size=12, weight="700", anchor="start", color="slate"))
    s.mtext(x + 16, 242,
            ["@pytest.fixture",
             "def db(tmp_path):            # fixture using a fixture",
             "    conn = sqlite3.connect(tmp_path / 't.db')",
             "    yield conn               # value handed to the test",
             "    conn.close()             # teardown, always runs"],
            TextOpts(size=10.5, mono=True, anchor="start", color="ink"), lh=17)

    s.panel(x + 458, 196, 442, 152, "", fill="greenbg", stroke="green")
    s.text(x + 474, 218, "Scopes control how often a fixture runs",
           TextOpts(size=12, weight="700", anchor="start", color="green"))
    for i, (sc, d) in enumerate([("function", "default - fresh per test"),
                                 ("class / module", "shared within a group"),
                                 ("session", "once per pytest run"),
                                 ("package", "once per package")]):
        yy = 240 + i * 24
        s.badge(x + 474, yy, sc, fill="green", size=10)
        s.text(x + 588, yy + 14, d, TextOpts(size=11, anchor="start",
                                             color="ink"))
    s.save(path)


# ---------------------------------------------------------------------------
# 16 -- concurrency
# ---------------------------------------------------------------------------
def d_gil(path):
    s = SVG(990, 470, title="The GIL")
    s.heading(495, 28, "The Global Interpreter Lock: one thread runs bytecode at a time")
    s.caption(495, 46, "Threads still help enormously - they release the GIL while waiting on I/O.")

    y0, w, h, xt = 96, 560, 34, 210
    lanes = [("single thread", [("run", 0, 100, "blue")]),
             ("2 threads - CPU bound", [("A", 0, 50, "blue"), ("B", 50, 50, "violet")]),
             ("2 threads - I/O bound", [("A run", 0, 20, "blue"), ("A waits (GIL released)", 20, 30, "slate"),
                                        ("A run", 50, 12, "blue"), ("waits", 62, 20, "slate"),
                                        ("B run", 20, 30, "violet"), ("B run", 82, 18, "violet")])]
    for i, (lab, segs) in enumerate(lanes):
        yy = y0 + i * 62
        s.text(xt - 18, yy + 22, lab, TextOpts(size=11.5, weight="700",
                                               anchor="end", color="slate"))
        s.rect(xt, yy, w, h, fill="panel", stroke="line", rx=6)
        for name, st, ln, k in segs:
            sx = xt + st / 100 * w
            sw = ln / 100 * w
            s.rect(sx, yy, sw, h, fill=f"{k}bg" if k != "slate" else "slatebg",
                   stroke=k, rx=4, sw=1.2)
            if sw > 60:
                s.text(sx + sw / 2, yy + h / 2 + 4, name,
                       TextOpts(size=10, weight="600", color=k))
        s.text(xt + w + 14, yy + 22, ["1.0x", "~1.0x - no speedup",
                                      "up to Nx - waits overlap"][i],
               TextOpts(size=11, weight="700", anchor="start",
                        color=["slate", "red", "green"][i]))

    yy = table(s, 60, y0 + 3 * 62 + 8, ["workload", "best tool", "why"],
               [["CPU-heavy (math, images, parsing)", "+multiprocessing / ProcessPool", "separate interpreters, separate GILs, real parallelism on N cores"],
                ["Many slow network calls", "+asyncio (or ThreadPoolExecutor)", "the thread/task is idle while waiting - the GIL is released"],
                ["Reading lots of files", "+threads", "file I/O releases the GIL"],
                ["Simple script, one job", "-plain synchronous code", "concurrency is a cost; only pay it when it buys something"]],
               [260, 250, 400], rowh=26, headh=28, size=11)
    s.caption(495, yy + 18, "PEP 703 (free-threaded CPython, 3.13+) makes a no-GIL build available - it is optional and not yet the default.")
    s.save(path)


def d_concurrency_models(path):
    s = SVG(990, 478, title="Three concurrency models")
    s.heading(495, 28, "threading  vs  multiprocessing  vs  asyncio")
    cards = [("threading", "blue", ["OS threads in ONE process",
                                     "share memory (need Lock)",
                                     "concurrent, NOT parallel",
                                     "cheap: ~8 MB stack each",
                                     "pre-emptive switching"],
              "I/O bound work, GUIs,\ntalking to many services"),
             ("multiprocessing", "green", ["separate processes + interpreters",
                                           "NO shared memory (use Queue/pipe)",
                                           "true parallelism on N cores",
                                           "expensive: ~MBs + startup cost",
                                           "no GIL contention"],
              "CPU bound work: images,\nML features, data crunching"),
             ("asyncio", "violet", ["ONE thread, cooperative tasks",
                                    "switch only at await points",
                                    "10k+ concurrent connections",
                                    "cheapest: ~KBs per task",
                                    "one blocking call freezes all"],
              "high-fanout network servers,\nwebsockets, scraping at scale")]
    w, gap = 306, 14
    x0 = (990 - (3 * w + 2 * gap)) / 2
    for i, (nm, k, pts, use) in enumerate(cards):
        bx = x0 + i * (w + gap)
        s.panel(bx, 62, w, 250, "", fill="bg", stroke=k)
        s.rect(bx, 62, w, 34, fill=k, stroke=None, rx=10)
        s.rect(bx, 84, w, 12, fill=k, stroke=None, rx=0)
        s.text(bx + w / 2, 84, nm, TextOpts(size=13.5, weight="700",
                                            color="bg", mono=True))
        s.mtext(bx + 16, 120, ["* " + p for p in pts],
                TextOpts(size=11, anchor="start", color="ink"), lh=19)
        s.rect(bx + 12, 232, w - 24, 66, fill=f"{k}bg", stroke=None, rx=8)
        s.mtext(bx + w / 2, 254, ["best for:", *use.split("\n")],
                TextOpts(size=10.5, weight="600", color=k), lh=16)
    yy = table(s, x0, 330, ["", "threading", "multiprocessing", "asyncio"],
               [["parallel on many cores?", "-no (GIL)", "+yes", "-no"],
                ["handles 10k connections?", "!hard (memory)", "-very expensive", "+yes"],
                ["shares objects freely?", "+yes", "-no, must pickle", "+yes"],
                ["needs async/await syntax?", "-no", "-no", "+yes, all the way down"]],
               [240, 210, 230, 236], rowh=24, headh=26, size=11)
    s.save(path)


def d_event_loop(path):
    s = SVG(990, 400, title="The asyncio event loop")
    s.heading(495, 28, "One thread, many tasks: the event loop")

    cx, cy, r = 300, 210, 118
    s.circle(cx, cy, r, fill="panel", stroke="violet", sw=2.4)
    s.text(cx, cy - 14, "event loop", TextOpts(size=15, weight="700",
                                               color="violet"))
    s.text(cx, cy + 8, "ready queue", TextOpts(size=11, color="slate"))
    s.text(cx, cy + 26, "await -> park -> resume", TextOpts(size=10.5,
                                                            color="muted",
                                                            mono=True))
    tasks = [("task A  fetch /users", 0), ("task B  fetch /orders", 1),
             ("task C  sleep(1)", 2)]
    for i, (nm, idx) in enumerate(tasks):
        ang = -90 + idx * 120
        import math
        tx = cx + (r + 96) * math.cos(math.radians(ang))
        ty = cy + (r + 70) * math.sin(math.radians(ang))
        s.rect(tx - 92, ty - 16, 184, 32, fill="greenbg", stroke="green",
               rx=8)
        s.text(tx, ty + 5, nm, TextOpts(size=11, weight="600", color="green",
                                        mono=True))
        s.line(tx - (92 if tx > cx else -92), ty, cx, cy, color="line",
               sw=1.4, dashed=True)

    s.panel(560, 62, 402, 160, "", fill="amberbg", stroke="amber")
    s.text(576, 86, "The one rule that breaks everything",
           TextOpts(size=12.5, weight="700", anchor="start", color="amber"))
    s.mtext(576, 110,
            ["NEVER call blocking code inside a coroutine.",
             "time.sleep(5), requests.get(), a synchronous DB driver",
             "or heavy CPU work will freeze EVERY other task, because",
             "they all share this single thread.",
             "Escape hatches: asyncio.to_thread(fn, ...) or",
             "loop.run_in_executor(None, fn) - or use an async driver."],
            TextOpts(size=10.5, anchor="start", color="ink"), lh=17)

    s.panel(560, 238, 402, 140, "", fill="panel2", stroke="line")
    s.text(576, 260, "Concurrency is NOT parallelism",
           TextOpts(size=12.5, weight="700", anchor="start", color="slate"))
    s.mtext(576, 284,
            ["3 tasks x 1 s of network wait  ->  ~1 s total.",
             "asyncio.gather() runs them CONCURRENTLY.",
             "3 tasks x 1 s of pure CPU  ->  still ~3 s total.",
             "Use run_in_executor / ProcessPool for that."],
            TextOpts(size=11, anchor="start", color="ink"), lh=18)
    s.save(path)


# ---------------------------------------------------------------------------
# 17 -- performance
# ---------------------------------------------------------------------------
def d_perf_flow(path):
    s = SVG(990, 448, title="A professional optimisation workflow")
    s.heading(495, 28, "Make it work \u2192 make it right \u2192 make it fast")
    steps = [("1. measure first", "time.perf_counter, cProfile,\npy-spy, tracemalloc", "blue"),
             ("2. find the hotspot", "usually ONE function holds\n80% of the time", "violet"),
             ("3. fix the algorithm", "O(n\u00b2) -> O(n) with a set\nor dict beats any micro-tuning", "green"),
             ("4. change the data", "right container, right layout,\ngenerators instead of lists", "amber"),
             ("5. micro-optimise", "local vars, avoid attribute\nlookups in hot loops", "cyan"),
             ("6. parallelise / C", "numpy, Cython, Rust ext,\nmultiprocessing, cache", "red")]
    w, gap, y, h = 148, 12, 66, 116
    x = (990 - (6 * w + 5 * gap)) / 2
    for i, (nm, desc, k) in enumerate(steps):
        bx = x + i * (w + gap)
        s.panel(bx, y, w, h, "", fill="bg", stroke=k)
        s.rect(bx, y, w, 30, fill=k, stroke=None, rx=10)
        s.rect(bx, y + 20, w, 10, fill=k, stroke=None, rx=0)
        s.text(bx + w / 2, y + 20, nm, TextOpts(size=11, weight="700",
                                                color="bg"))
        s.mtext(bx + w / 2, y + 58, desc.split("\n"),
                TextOpts(size=10, color="slate"), lh=15)
        if i:
            s.line(bx - gap, y + h / 2, bx, y + h / 2, color="line",
                   arrow=True, sw=1.6)
    s.line(x, y + h + 24, x + 6 * w + 5 * gap, y + h + 24, color="line",
           sw=1.4, dashed=True)
    s.text(495, y + h + 18, "each step must be re-measured - and the benchmark must live in the test suite",
           TextOpts(size=10.5, italic=True, color="muted"))

    rows = [["swap `x in list` for `x in set`", "+10x - 1000x", "algorithm / data structure"],
            ["build with a comprehension, not += in a loop", "+20 - 40%", "avoid repeated allocation"],
            ["str.join(parts) instead of s += part", "+huge for many parts", "strings are immutable"],
            ["@lru_cache on a pure, repeated function", "+100x on hits", "trading memory for time"],
            ["hoist attribute lookup out of a tight loop", "+5 - 15%", "LOAD_ATTR is slower than LOAD_FAST"],
            ["numpy vectorised op instead of a Python loop", "+50 - 200x", "C loop, no interpreter overhead"],
            ["generators for large/streaming data", "+massive memory saving", "never materialise what you scan once"]]
    yy = table(s, x, y + h + 44, ["change", "typical gain", "why it works"],
               rows, [380, 200, 320], rowh=25, headh=28, size=11)
    s.save(path)


# ---------------------------------------------------------------------------
# 18 -- packaging / CI
# ---------------------------------------------------------------------------
def d_ci(path):
    s = SVG(990, 396, title="The CI pipeline")
    s.heading(495, 28, "What happens between `git push` and production")
    steps = [("git push / PR", "developer", "slate"),
             ("install deps", "pip install -e .[dev]\nfrom a lockfile", "blue"),
             ("format + lint", "ruff format\nruff check", "cyan"),
             ("type check", "mypy --strict\npyright", "violet"),
             ("tests + coverage", "pytest --cov\nfail below 90%", "green"),
             ("build", "python -m build\nwheel + sdist", "amber"),
             ("deploy", "container / PyPI\nstaging then prod", "red")]
    w, gap, y, h = 126, 10, 68, 104
    x = (990 - (7 * w + 6 * gap)) / 2
    for i, (nm, desc, k) in enumerate(steps):
        bx = x + i * (w + gap)
        s.panel(bx, y, w, h, "", fill="bg", stroke=k)
        s.rect(bx, y, w, 28, fill=k, stroke=None, rx=10)
        s.rect(bx, y + 18, w, 10, fill=k, stroke=None, rx=0)
        s.text(bx + w / 2, y + 19, nm, TextOpts(size=10.5, weight="700",
                                                color="bg"))
        s.mtext(bx + w / 2, y + 56, desc.split("\n"),
                TextOpts(size=9.5, color="slate"), lh=14)
        if i:
            s.line(bx - gap, y + h / 2, bx, y + h / 2, color="line",
                   arrow=True, sw=1.5)
    s.line(x + w / 2, y + h, x + w / 2, y + h + 20, color="red", arrow=True,
           sw=1.8)
    s.arrowlabel(x + w / 2 + 120, y + h + 14,
                 "any red step blocks the merge - no exceptions",
                 color="red", size=11)

    s.panel(x, 208, 452, 160, "", fill="panel2", stroke="line")
    s.text(x + 16, 230, "A minimal pyproject.toml",
           TextOpts(size=12, weight="700", anchor="start", color="slate"))
    s.mtext(x + 16, 254,
            ["[project]",
             "name = 'myproject'",
             "version = '1.0.0'",
             "requires-python = '>=3.11'",
             "dependencies = ['httpx>=0.27', 'pydantic>=2']",
             "[project.optional-dependencies]",
             "dev = ['pytest', 'ruff', 'mypy']"],
            TextOpts(size=10.5, mono=True, anchor="start", color="ink"), lh=16)
    s.panel(x + 468, 208, 452, 160, "", fill="greenbg", stroke="green")
    s.text(x + 484, 230, "Why teams insist on this",
           TextOpts(size=12, weight="700", anchor="start", color="green"))
    s.mtext(x + 484, 254,
            ["* 'works on my machine' disappears - CI IS the machine",
             "* a broken change is caught in minutes, not in prod",
             "* reviewers read a diff with green checks, not hope",
             "* releases become boring and repeatable,",
             "  which is exactly what you want them to be"],
            TextOpts(size=11, anchor="start", color="ink"), lh=18)
    s.save(path)


def d_project_env(path):
    s = SVG(990, 400, title="Environments and dependencies")
    s.heading(495, 28, "One virtualenv per project - always")
    s.caption(495, 46, "A virtualenv is a private site-packages folder. Without it, two projects needing different versions of the same library cannot coexist.")

    s.panel(22, 66, 300, 240, "", fill="redbg", stroke="red")
    s.text(172, 92, "WITHOUT venvs", TextOpts(size=12.5, weight="700",
                                               color="red"))
    s.rect(52, 108, 240, 84, fill="bg", stroke="red", rx=10)
    s.text(172, 130, "system Python", TextOpts(size=11.5, weight="700",
                                               color="ink"))
    s.mtext(172, 152, ["projectA needs requests 2.20",
                       "projectB needs requests 2.31"],
            TextOpts(size=10.5, mono=True, color="slate"), lh=16)
    s.text(172, 216, "-> only one can be installed",
           TextOpts(size=11.5, weight="700", color="red"))
    s.mtext(172, 240, ["* sudo pip install breaks the OS",
                       "* upgrades silently break projects",
                       "* nobody can reproduce the setup"],
            TextOpts(size=10.5, anchor="start", color="ink"), lh=17)
    s.text(52, 292, "This is the #1 beginner environment mistake.",
           TextOpts(size=10.5, italic=True, anchor="start", color="muted"))

    for i, (nm, k, pkgs) in enumerate([("projectA / .venv", "green",
                                        ["requests 2.20", "flask 2.0"]),
                                       ("projectB / .venv", "blue",
                                        ["requests 2.31", "fastapi 0.111"]),
                                       ("course / .venv", "violet",
                                        ["pytest 9.1", "markdown"])]):
        x = 356 + i * 0
        y = 66 + i * 84
        s.panel(356, y, 612, 72, "", fill="bg", stroke=k)
        s.rect(356, y, 200, 72, fill=f"{k}bg", stroke=k, rx=10)
        s.text(456, y + 30, nm, TextOpts(size=12, weight="700", color=k,
                                         mono=True))
        s.text(456, y + 52, "isolated site-packages",
               TextOpts(size=10, color="slate"))
        for j, p in enumerate(pkgs):
            s.rect(576 + j * 190, y + 20, 176, 32, fill="panel2",
                   stroke="line", rx=6)
            s.text(664 + j * 190, y + 40, p, TextOpts(size=11, mono=True,
                                                      color="ink"))

    s.panel(22, 316, 946, 66, "", fill="greenbg", stroke="green")
    s.mtext(40, 340,
            ["python -m venv .venv  ->  source .venv/bin/activate  ->  pip install -e '.[dev]'",
             "Commit the REQUIREMENTS (pyproject.toml / lockfile). Never commit the .venv folder itself."],
            TextOpts(size=11.5, mono=True, anchor="start", color="ink"), lh=20)
    s.save(path)


DIAGRAMS = {
    "decorator-layers.svg": d_decorator_layers,
    "decorator-in-practice.svg": d_decorator_uses,
    "typing-value.svg": d_typing,
    "test-pyramid.svg": d_pyramid,
    "pytest-run.svg": d_pytest_flow,
    "gil.svg": d_gil,
    "concurrency-models.svg": d_concurrency_models,
    "event-loop.svg": d_event_loop,
    "optimisation-workflow.svg": d_perf_flow,
    "ci-pipeline.svg": d_ci,
    "virtualenvs.svg": d_project_env,
}
