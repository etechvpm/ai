# Using this course offline

Everything here is plain text — Markdown notes, generated SVG figures, Python
exercise packs and a static website. There is no server, database or account
involved, so "offline" just means "the files are on your machine".

Three ways to take it with you, easiest first.

---

## 1. One HTML file (no install, no server)

**`python-course-offline.html`** — all 20 pages (course home + 19 modules)
merged into a single self-contained file: CSS, JavaScript, all 44 diagrams and
the full-text search index are inlined. Nothing is fetched from the network.

```text
double-click it          -> opens in your browser
Ctrl/Cmd + P             -> print or Save as PDF (print styles included)
copy it to your phone    -> works in any mobile browser
```

Search (press `/`), dark mode and the copy buttons on code blocks all work.
Because it is one file, links jump to anchors inside it rather than to other
files.

Rebuild it any time:

```bash
python3 tools/build_offline.py            # -> dist/python-course-offline.html
```

---

## 2. The multi-page website

`python-course-site.zip` contains the generated site in `site/` plus the single
file above. Unzip, then serve it:

```bash
cd python-course-site
python3 -m http.server 8000 --bind 0.0.0.0 --directory site
# open http://localhost:8000
```

Any static file server works too (`npx serve site`, Caddy, nginx, or your
editor's live-preview).

> You *can* double-click `site/index.html` and read it — every page, figure and
> style is local. Only the search box needs `http://`, because browsers block
> `fetch()` on `file://`. Use option 1 if you want search without a server.

Regenerate the site from the Markdown sources:

```bash
python3 tools/build_site.py               # notes/*.md -> site/*.html
python3 tools/make_diagrams.py            # redraw all 44 SVG figures
python3 tools/check_figures.py            # validate them
```

---

## 3. The full source: notes + exercises + tools

`python-course-full.zip` is the whole repository: `notes/`, `exercises/`,
`tools/`, `site/`, the offline HTML, `README.md` and this file. This is the one
to download if you want to **do the exercises**.

```bash
cd python-course-full
python3 -m venv .venv
source .venv/bin/activate                 # Windows: .venv\Scripts\activate
pip install pytest markdown pygments      # the only dependencies
```

Then the study loop for each module:

```bash
# 1. read the notes (either the website or notes/13-decorators-closures.md)
# 2. open the exercise pack and fill in the TODOs
$EDITOR exercises/13_decorators/tasks.py

# 3. grade yourself - red means keep going
pytest exercises/13_decorators -q

# 4. everything you have done so far
pytest exercises -q

# 5. see the reference answers pass (or read them when genuinely stuck)
PYCOURSE_SOLUTION=1 pytest exercises -q
$EDITOR exercises/13_decorators/solution.py
```

Each pack has three files:

| File | What it is |
|------|-----------|
| `tasks.py` | the spec — functions raising `NotImplementedError`, with docstrings; **you edit this** |
| `test_tasks.py` | the grader — plain pytest, no network, no fixtures outside the pack |
| `solution.py` | a reference answer; the grader loads it when `PYCOURSE_SOLUTION=1` |

Exercises are tiered **Beginner → Intermediate → Industry** inside each pack;
do them in that order.

Requirements: **Python 3.11+** (the notes use `match`, `tomllib`, `X | None`,
`asyncio.timeout`, `dataclass(slots=True)`). `pytest` is the only test
dependency; nothing in the course needs a C compiler or a network connection.

---

## Getting the files from GitHub instead

The course lives in the repository `etechvpm/ai` on the branch
`arena/01a0cc5f-ai`:

```bash
git clone -b arena/01a0cc5f-ai https://github.com/etechvpm/ai.git python-course
```

or download a snapshot without git:

```text
https://github.com/etechvpm/ai/archive/refs/heads/arena/01a0cc5f-ai.zip
```

Then follow option 2 or 3 above. `dist/` (the zips and the single-file build) is
generated, not committed — run `python3 tools/build_offline.py` to recreate it.

---

## Making your own bundles

```bash
python3 tools/build_offline.py             # site/ + dist/*.html + dist/*.zip
python3 tools/build_offline.py --no-site   # reuse the existing site/ build
```

Outputs, all in `dist/`:

| File | Contains |
|------|----------|
| `python-course-offline.html` | the whole course in one file |
| `python-course-site.zip` | `site/` + the single file + this doc |
| `python-course-full.zip` | notes, exercises, tools, site, single file, docs |
