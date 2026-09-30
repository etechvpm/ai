# Python, From Zero to Industry

A visual, depth-first Python course: **19 modules** of Markdown notes, **44 generated
SVG diagrams**, and **19 exercise packs (270 pytest checks)** that grade your work
automatically.

Every module takes one concept and walks it from a one-line definition to the
questions a senior engineer gets asked in code review:

```text
definition → syntax → first examples → diagram → mechanics → industry practice
→ comparison tables → mistakes & gotchas → interview questions → exercises → cheatsheet
```

## Quick start

```bash
python3 -m venv .venv                 # Python 3.11+
source .venv/bin/activate             # Windows: .venv\Scripts\activate
pip install pytest markdown pygments

# read the course as a website
python tools/build_site.py            # notes/*.md  ->  site/*.html
python -m http.server 8123 --bind 0.0.0.0 --directory site

# take it offline: one self-contained HTML file + downloadable zips
python tools/build_offline.py     # -> dist/python-course-offline.html, dist/*.zip

# do the exercises
pytest exercises/06_data_structures -q      # grade one module
pytest exercises -q                         # grade everything you've written
PYCOURSE_SOLUTION=1 pytest exercises -q     # watch the reference answers pass
```

Everything is plain text and generated code — no binary artifacts. The Markdown
sources under `notes/` read fine on GitHub; the website is a rebuild away.

## Repository layout

| Path | Contents |
|------|----------|
| `notes/` | the course: `index.md` + one Markdown file per module |
| `notes/figures/` | 44 SVG diagrams, inlined into the site (theme-aware) |
| `exercises/<NN_slug>/` | `tasks.py` (yours), `test_tasks.py` (grader), `solution.py` (reference) |
| `tools/svgkit.py` | dependency-free SVG drawing kit used by all figures |
| `tools/diagrams_[a-d].py` | figure definitions, one function per diagram |
| `tools/make_diagrams.py` | regenerate every figure (`python tools/make_diagrams.py gil`) |
| `tools/build_site.py` | Markdown → HTML site with sidebar, TOC, search index |
| `tools/check_figures.py` | validates figure XML and text overflow |
| `tools/build_offline.py` | single-file offline edition + zip bundles in `dist/` |
| `OFFLINE.md` | how to download, read and study the course without a network |

## The modules

| # | Module | You will be able to |
|---|--------|---------------------|
| 01 | How Python runs | explain compilation, bytecode and the VM; set up a professional environment |
| 02 | Variables, types & memory | reason about names vs objects, mutability, aliasing, garbage collection |
| 03 | Operators & expressions | choose operators deliberately and read any expression correctly |
| 04 | Strings & text | slice, format, encode and process text without mojibake or O(n²) bugs |
| 05 | Control flow | branch and loop idiomatically, including `match` and `for…else` |
| 06 | Data structures | pick the right container and know its complexity by heart |
| 07 | Functions | design signatures, scopes and closures like a library author |
| 08 | Modules & packages | structure an importable project and debug import errors |
| 09 | Object-oriented Python | model domains with classes, MRO, protocols and dataclasses |
| 10 | Files & I/O | read and write any file safely, with encodings and context managers |
| 11 | Exceptions | design error handling and a clean exception hierarchy |
| 12 | Iteration & generators | write lazy pipelines for data bigger than RAM |
| 13 | Closures & decorators | build cross-cutting behaviour: retries, caching, timing, auth |
| 14 | Type hints & static analysis | annotate a codebase so mypy catches bugs before it runs |
| 15 | Testing | write pytest suites with fixtures, parametrisation and mocks |
| 16 | Concurrency | choose threads, processes or asyncio correctly and explain the GIL |
| 17 | Performance | profile first, then fix the hotspot with the right tool |
| 18 | Packaging & CI/CD | ship an installable package with lint, types, tests and releases |
| 19 | Cheatsheets & capstone | revise everything from dense one-screen summaries, then build the report pipeline |

## How the exercises work

Each pack is three files:

- **`tasks.py`** — the spec. Functions raise `NotImplementedError`; docstrings say
  exactly what to build. Exercises are tiered **Beginner → Intermediate → Industry**.
- **`test_tasks.py`** — the grader. `pytest` is the only dependency; run it any time.
- **`solution.py`** — a reference answer. The grader loads it instead of your file
  when `PYCOURSE_SOLUTION=1` is set, so you can always see a green run.

Read the reference only after a genuine attempt — the struggle is where the learning
happens.

## Regenerating figures and the site

```bash
python tools/make_diagrams.py         # all 44 figures (or pass a name filter)
python tools/check_figures.py         # XML validity + text-overflow checks
python tools/build_site.py            # rebuild site/ from notes/
```
