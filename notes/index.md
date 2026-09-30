---
order: 0
slug: index
title: "Course home & how to use these notes"
summary: "What this course is, how it is organised, and the loop you should follow for every module."
level: "Orientation"
read: "8 min"
tags: orientation, how-to
---

<div class="hero">
<h1>Python, From Zero to Industry</h1>
<p>A visual, depth-first Python course. Every module takes one concept and
pushes it from a one-line definition all the way to the questions a senior
engineer gets asked in code review — with diagrams, comparison tables,
worked examples and exercises your machine grades for you.</p>
</div>

## How each module is built

Every module follows the same ladder, so you always know where you are:

1. **Definition** — one honest sentence, then the precise version.
2. **Syntax** — the grammar, annotated, with the smallest example that runs.
3. **First examples** — three tiny programs with their exact output.
4. **The picture** — a diagram of what is really happening in memory / the
   interpreter / the network.
5. **Going deeper** — the mechanics under the syntax: how CPython implements
   it, what it costs, where it surprises you.
6. **Industry level** — how this appears in a real codebase: patterns,
   trade-offs, review comments, library choices.
7. **Comparison tables** — the decision-making view.
8. **Mistakes & gotchas** — the bugs everyone writes once.
9. **Interview questions** — with the answers interviewers actually want.
10. **Exercises** — three tiers, auto-checked by `pytest`.
11. **Cheatsheet** — the one screen to re-read before an exam or interview.

## The loop you should follow

Do not read a module top to bottom and move on. For each module:

```text
read 1-4          understand the shape of the idea
type out 3        typing beats reading; your fingers learn the syntax
read 5-7          now the depth will stick, because you have a handle for it
do the exercises  beginner -> intermediate -> industry, in that order
run pytest        green is the only acceptable outcome
re-read 8-9       the gotchas now read like your own mistakes
```

## Running the exercises

Each module ships an exercise pack in `exercises/`:

```bash
# from the repository root, inside your virtualenv
pip install pytest                      # once
pytest exercises/06_data_structures -q  # check one module's pack
pytest exercises -q                     # check everything you've done

# want to see the reference answers pass first?
PYCOURSE_SOLUTION=1 pytest exercises -q
```

Every exercise is a small set of functions with `TODO` markers in
`exercises/<pack>/tasks.py`. The matching `test_tasks.py` grades them.
`exercises/<pack>/solution.py` holds a reference answer — read it only after
you have a green (or a genuinely stuck) attempt of your own.

## Regenerating this site and the figures

The notes are plain Markdown in `notes/`; every diagram is generated code in
`tools/`. Nothing here is a hand-exported binary:

```bash
python tools/make_diagrams.py   # redraw all 44 SVG figures
python tools/build_site.py      # rebuild this website into site/
```

## Module map

| # | Module | You will be able to |
|---|--------|---------------------|
| 01 | [How Python runs](01-python-and-how-it-runs.html) | explain compilation, bytecode, the VM, and set up a professional environment |
| 02 | [Variables, types & memory](02-variables-types-memory.html) | reason about names vs objects, mutability, aliasing and garbage collection |
| 03 | [Operators & expressions](03-operators-expressions.html) | choose operators deliberately and read any expression correctly |
| 04 | [Strings & text](04-strings-text.html) | slice, format, encode and process text without mojibake or O(n²) bugs |
| 05 | [Control flow](05-control-flow.html) | branch and loop idiomatically, including `match` and `for…else` |
| 06 | [Data structures](06-data-structures.html) | pick the right container and know its complexity by heart |
| 07 | [Functions](07-functions.html) | design signatures, scopes and closures like a library author |
| 08 | [Modules & packages](08-modules-packages.html) | structure an importable, installable project and debug import errors |
| 09 | [Object-oriented Python](09-oop.html) | model domains with classes, MRO, protocols and dataclasses |
| 10 | [Files & I/O](10-files-io.html) | read/write any file safely with encodings and context managers |
| 11 | [Exceptions](11-exceptions.html) | design error handling and a clean exception hierarchy |
| 12 | [Iteration, comprehensions & generators](12-iteration-generators.html) | write lazy pipelines that process data bigger than RAM |
| 13 | [Closures & decorators](13-decorators-closures.html) | build cross-cutting behaviour: retries, caching, timing, auth |
| 14 | [Type hints & static analysis](14-type-hints.html) | annotate a codebase so mypy and your editor catch bugs pre-run |
| 15 | [Testing](15-testing.html) | write pytest suites with fixtures, parametrisation and mocks |
| 16 | [Concurrency](16-concurrency.html) | choose threads, processes or asyncio correctly and explain the GIL |
| 17 | [Performance](17-performance.html) | profile first, then optimise the hotspot with the right tool |
| 18 | [Packaging, tooling & CI](18-packaging-ci.html) | ship an installable package with lint, types, tests and CI |
| 19 | [Cheatsheets](19-cheatsheets.html) | revise everything from dense one-screen summaries |

::: tip "A promise"
Nothing in these notes is hand-waved. When a sentence says "O(1)" or "the GIL
is released", the module shows you the mechanism. If a claim feels wrong,
test it — every claim here is something you can verify in a REPL in under a
minute.
:::
