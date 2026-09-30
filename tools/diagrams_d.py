"""Figures for modules 17-19 (memory layout, packaging anatomy, release flow,
course map).

Generated into notes/figures/ by tools/make_diagrams.py.
"""

from __future__ import annotations

from svgkit import SVG, TextOpts, c, flowchart_step


# ---------------------------------------------------------------------------
# 17 -- memory vs speed
# ---------------------------------------------------------------------------
def d_memory_vs_speed(path):
    s = SVG(990, 500, title="Storing a million numbers, four ways")
    s.heading(495, 30, "The same 1,000,000 floats, stored four ways")
    s.caption(495, 50, "Every Python object pays a boxing tax - the container you choose is a memory decision")

    rows = [
        ("[x for x in data]", "list of float objects", 40, "O(1) index, mutate anywhere",
         "blue", "general purpose; 8 B pointer + 32 B boxed float"),
        ("[(x, y) for ...]", "list of tuples", 64, "O(1) index, immutable items",
         "cyan", "records without attribute access"),
        ("Point(x=..., y=...)", "objects with __dict__", 184, "attribute access, mutable",
         "amber", "readable, but the dict costs ~104 B each"),
        ("@dataclass(slots=True)", "__slots__ objects", 64, "attribute access, no dict",
         "green", "same ergonomics, ~2/3 less memory"),
        ("array.array('d') / np.array", "unboxed C doubles", 8, "vectorised, no per-item objects",
         "violet", "numerics: 5x smaller AND far faster to loop in C"),
    ]
    top = 78
    rowh = 62
    max_bytes = 184
    bar_max = 300
    for i, (code, what, nbytes, access, kind, note) in enumerate(rows):
        y = top + i * rowh
        s.rect(24, y, 942, rowh - 10, fill="panel", stroke="line", rx=8)
        s.text(40, y + 22, code, TextOpts(size=11.5, weight="700", anchor="start",
                                          color=kind, mono=True))
        s.text(40, y + 40, what, TextOpts(size=10.5, anchor="start", color="muted"))
        # proportional memory bar
        bw = max(10, int(bar_max * nbytes / max_bytes))
        s.rect(330, y + 12, bw, 18, fill=f"{kind}bg", stroke=kind, rx=4, sw=1.3)
        s.text(336 + bw, y + 26, f"~{nbytes} B/item", TextOpts(
            size=10.5, weight="700", anchor="start", color=kind, mono=True))
        total = nbytes * 1_000_000 / 1e6
        s.text(336 + bw + 92, y + 26, f"{total:.0f} MB for 1M", TextOpts(
            size=10, anchor="start", color="slate"))
        s.text(330, y + 44, access, TextOpts(size=10, anchor="start", color="ink"))
        s.text(700, y + 26, note, TextOpts(size=9.8, anchor="start", color="muted"))

    s.panel(24, 396, 942, 84, "", fill="greenbg", stroke="green")
    s.text(40, 418, "How to use this", TextOpts(size=12, weight="700",
                                                anchor="start", color="green"))
    s.mtext(40, 440,
            ["* millions of small objects is where memory goes, not the data itself "
             "(sys.getsizeof shows only the shallow size)",
             "* __slots__ / dataclass(slots=True) drops the instance __dict__; "
             "array / NumPy drops the boxing entirely",
             "* speed follows memory: fewer bytes per item means fewer cache misses "
             "and, for NumPy, loops executed in C"],
            TextOpts(size=10.5, anchor="start", color="ink"), lh=16)
    s.save(path)


# ---------------------------------------------------------------------------
# 18 -- anatomy of pyproject.toml
# ---------------------------------------------------------------------------
def d_pyproject_anatomy(path):
    s = SVG(990, 596, title="Anatomy of pyproject.toml")
    s.heading(495, 30, "One file describes the build, the metadata and the tools")
    s.caption(495, 50, "PEP 517/518 build system + PEP 621 project metadata + [tool.*] configuration")

    # left: the file
    lines = [
        ("[build-system]", "blue", 0),
        ('requires = ["hatchling"]', "ink", 1),
        ('build-backend = "hatchling.build"', "ink", 1),
        ("", "ink", 0),
        ("[project]", "green", 0),
        ('name = "acme-reports"', "ink", 1),
        ('version = "1.4.2"', "ink", 1),
        ('requires-python = ">=3.11"', "ink", 1),
        ('dependencies = ["httpx>=0.27", "pydantic>=2.7"]', "ink", 1),
        ("", "ink", 0),
        ("[project.optional-dependencies]", "amber", 0),
        ('dev = ["pytest>=8", "ruff", "mypy"]', "ink", 1),
        ("", "ink", 0),
        ("[project.scripts]", "violet", 0),
        ('acme-report = "acme_reports.cli:main"', "ink", 1),
        ("", "ink", 0),
        ("[tool.ruff]  line-length = 100", "cyan", 0),
        ("[tool.mypy]  strict = true", "cyan", 0),
        ("[tool.pytest.ini_options]  testpaths = ['tests']", "cyan", 0),
    ]
    x0, y0, lh = 24, 76, 21
    s.rect(x0, y0, 520, len(lines) * lh + 22, fill="panel", stroke="line", rx=10)
    s.text(x0 + 14, y0 + 17, "pyproject.toml", TextOpts(size=10.5, weight="700",
                                                         anchor="start",
                                                         color="muted", mono=True))
    marks = {}
    for i, (text, colour, indent) in enumerate(lines):
        y = y0 + 34 + i * lh
        if text.startswith("["):
            marks[text.split("]")[0] + "]"] = (x0 + 6, y - 12, colour)
            s.rect(x0 + 6, y - 12, 508, lh - 3, fill=f"{colour}bg", stroke=None,
                   rx=4, opacity=0.55)
        s.text(x0 + 16 + indent * 16, y, text,
               TextOpts(size=10.5, anchor="start", color=colour, mono=True,
                        weight="700" if text.startswith("[") else "400"))

    # right: annotations
    notes = [
        ("[build-system]", "blue",
         ["which backend builds the artifact",
          "python -m build isolates, installs it,",
          "then calls it -> dist/*.whl + *.tar.gz"]),
        ("[project]", "green",
         ["PEP 621 metadata shown on PyPI",
          "version = single source of truth",
          "libraries use RANGES, apps use locks"]),
        ("[project.optional-dependencies]", "amber",
         ["extras: pip install '.[dev]'",
          "keeps dev tooling out of the runtime",
          "install for your users"]),
        ("[project.scripts]", "violet",
         ["console entry points",
          "creates an executable on PATH that",
          "calls acme_reports.cli:main()"]),
        ("[tool.*]", "cyan",
         ["ruff / mypy / pytest / coverage config",
          "one file the whole toolchain reads -",
          "no setup.cfg, no .flake8, no pytest.ini"]),
    ]
    y = 84
    for section, colour, body in notes:
        key = section
        hgt = 22 + len(body) * 15
        s.rect(568, y, 398, hgt, fill="panel", stroke=colour, rx=8)
        s.text(582, y + 18, key, TextOpts(size=11, weight="700", anchor="start",
                                          color=colour, mono=True))
        s.mtext(582, y + 36, body, TextOpts(size=10, anchor="start",
                                            color="ink"), lh=15)
        if key in marks:
            mx, my, _ = marks[key]
            s.line(mx + 512, my + 8, 566, y + hgt / 2, color=colour, sw=1.3,
                   dashed=True, arrow=True)
        y += hgt + 12

    s.panel(24, 512, 942, 66, "", fill="slatebg", stroke="slate")
    s.mtext(42, 536,
            ["python -m venv .venv  ->  pip install -e '.[dev]'  ->  ruff check .  ->  mypy src/  ->  pytest",
             "python -m build  ->  twine check dist/*  ->  (on tag v*)  publish with OIDC trusted publishing"],
            TextOpts(size=11.5, mono=True, anchor="start", color="ink"), lh=20)
    s.save(path)


# ---------------------------------------------------------------------------
# 18 -- release flow
# ---------------------------------------------------------------------------
def d_release_flow(path):
    s = SVG(990, 470, title="From commit to published release")
    s.heading(495, 30, "A release is a pipeline, not a hero")
    s.caption(495, 50, "Conventional Commits make the version and the changelog derivable - CI does the rest")

    steps = [
        ("commit", "feat: / fix: / feat!:", "green", 24),
        ("pull request", "review + green CI", "blue", 214),
        ("gates", "ruff, mypy, pytest, cov", "blue", 404),
        ("merge to main", "squash, changelog entry", "blue", 594),
        ("tag v1.5.0", "version bump by rule", "amber", 784),
    ]
    for label, sub, kind, x in steps:
        flowchart_step(s, x, 84, 176, 56, label, sub, kind=kind)
    for x in (200, 390, 580, 770):
        s.line(x, 112, x + 14, 112, color="slate", sw=2, arrow=True)

    # gate failure loop
    s.path("M 492 140 L 492 176 L 302 176 L 302 140", color="red", sw=1.8,
           dashed=True, arrow=True)
    s.arrowlabel(397, 172, "any gate red -> back to the PR", color="red", size=10.5)

    # second row: publish side
    row2 = [
        ("build", "python -m build\nwheel + sdist", "violet", 24),
        ("publish", "PyPI via OIDC\nno long-lived token", "violet", 214),
        ("release notes", "GitHub Release\nCHANGELOG.md", "cyan", 404),
        ("consumers", "Renovate / Dependabot\nbump + their CI", "cyan", 594),
        ("rollback", "reinstall previous\npinned version", "red", 784),
    ]
    for label, sub, kind, x in row2:
        first, _, rest = sub.partition("\n")
        flowchart_step(s, x, 224, 176, 56, label, [first, rest], kind=kind)
    for x in (200, 390, 580, 770):
        s.line(x, 252, x + 14, 252, color="slate", sw=2, arrow=True)
    s.path("M 872 140 L 872 196 L 112 196 L 112 224", color="slate", sw=1.8,
           arrow=True)
    s.arrowlabel(492, 194, "only on refs/tags/v*, after the test jobs",
                 color="slate", size=10.5)

    s.panel(24, 306, 452, 140, "", fill="panel2", stroke="line")
    s.text(40, 328, "Version rule (semver on PEP 440)",
           TextOpts(size=12, weight="700", anchor="start", color="slate"))
    s.mtext(40, 352,
            ["feat!: or BREAKING CHANGE  ->  MAJOR  (2.0.0)",
             "feat:                      ->  MINOR  (1.5.0)",
             "fix: / docs: / chore:      ->  PATCH  (1.4.3)",
             "nothing user visible       ->  no release"],
            TextOpts(size=10.5, mono=True, anchor="start", color="ink"), lh=17)

    s.panel(514, 306, 452, 140, "", fill="amberbg", stroke="amber")
    s.text(530, 328, "Non-negotiables", TextOpts(size=12, weight="700",
                                                  anchor="start", color="amber"))
    s.mtext(530, 352,
            ["* a published version is immutable - never re-upload, use .post1",
             "* yank broken releases, do not delete them",
             "* the release job needs: the test jobs, and least-privilege",
             "  permissions (id-token: write) - nothing else",
             "* deprecate for one minor release before removing anything"],
            TextOpts(size=10.3, anchor="start", color="ink"), lh=16)
    s.save(path)


# ---------------------------------------------------------------------------
# 19 -- course map
# ---------------------------------------------------------------------------
def d_course_map(path):
    s = SVG(990, 664, title="Course map")
    s.heading(495, 30, "How the 19 modules build on each other")
    s.caption(495, 50, "Read in order the first time; after that, use the map to find the module that owns your question")

    bands = [
        ("FOUNDATIONS", "green", [
            ("01", "How Python runs"), ("02", "Variables & memory"),
            ("03", "Operators"), ("04", "Strings & text")]),
        ("STRUCTURE", "blue", [
            ("05", "Control flow"), ("06", "Data structures"),
            ("07", "Functions"), ("08", "Modules & packages"),
            ("09", "OOP")]),
        ("DATA & INTERFACES", "amber", [
            ("10", "Files & I/O"), ("11", "Exceptions"),
            ("12", "Iteration & generators"), ("13", "Decorators")]),
        ("ENGINEERING", "violet", [
            ("14", "Type hints"), ("15", "Testing"),
            ("16", "Concurrency"), ("17", "Performance"),
            ("18", "Packaging & CI")]),
    ]
    y = 78
    for title, colour, mods in bands:
        s.rect(24, y, 942, 88, fill="panel", stroke=colour, rx=10)
        s.rect(24, y, 8, 88, fill=colour, stroke=None, rx=3)
        s.text(48, y + 24, title, TextOpts(size=11.5, weight="700",
                                           anchor="start", color=colour,
                                           spacing=1.0))
        n = len(mods)
        gap = 14
        width = (942 - 40 - gap * (n - 1)) / n
        for i, (num, name) in enumerate(mods):
            bx = 44 + i * (width + gap)
            s.rect(bx, y + 34, width, 42, fill=f"{colour}bg", stroke=colour,
                   rx=8, sw=1.4)
            s.text(bx + 14, y + 60, num, TextOpts(size=13, weight="700",
                                                  anchor="start", color=colour,
                                                  mono=True))
            s.text(bx + 40, y + 60, name, TextOpts(size=10.8, weight="600",
                                                   anchor="start", color="ink"))
        y += 104

    # the revision band
    s.rect(24, y, 942, 44, fill="slatebg", stroke="slate", rx=10)
    s.text(48, y + 28, "REVISION", TextOpts(size=11.5, weight="700",
                                            anchor="start", color="slate",
                                            spacing=1.0))
    s.rect(180, y + 8, 300, 28, fill="bg", stroke="slate", rx=8, sw=1.3)
    s.text(196, y + 27, "19  Cheatsheets & capstone", TextOpts(
        size=10.8, weight="600", anchor="start", color="ink"))
    s.text(500, y + 27, "every module compressed to one screen, plus the "
                        "pipeline project that uses them all",
           TextOpts(size=10.5, anchor="start", color="muted"))

    s.panel(24, y + 58, 942, 74, "", fill="bluebg", stroke="blue")
    s.mtext(42, y + 82,
            ["Each module: definition -> syntax -> examples -> diagram -> mechanics -> "
             "industry practice -> tables -> gotchas -> interview -> exercises -> cheatsheet.",
             "Each exercise pack: tasks.py (yours), test_tasks.py (the grader), "
             "solution.py (reference). Run  pytest exercises -q  and keep it green."],
            TextOpts(size=10.8, anchor="start", color="ink"), lh=18)
    s.save(path)


DIAGRAMS = {
    "memory-vs-speed.svg": d_memory_vs_speed,
    "pyproject-anatomy.svg": d_pyproject_anatomy,
    "release-flow.svg": d_release_flow,
    "course-map.svg": d_course_map,
}
