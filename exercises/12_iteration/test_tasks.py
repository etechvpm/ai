"""Grader for module 12.  Run:  pytest exercises/12_iteration -q"""

from __future__ import annotations

import pytest

from _loader import load

tasks = load(__file__)


# ------------------------------------------------------------- beginner
def test_comprehensions():
    assert tasks.squares_map(4) == {0: 0, 1: 1, 2: 4, 3: 9}
    assert tasks.even_squares([1, 2, 3, 4]) == [4, 16]
    assert tasks.word_lengths([" hi ", "", "bye"]) == {"hi": 2, "bye": 3}
    assert tasks.flatten([[1, 2], [], [3]]) == [1, 2, 3]


# --------------------------------------------------------- intermediate
def test_take_and_chunked():
    assert list(tasks.take(3, range(10))) == [0, 1, 2]
    assert list(tasks.take(10, [1, 2])) == [1, 2]
    assert list(tasks.chunked(range(7), 3)) == [[0, 1, 2], [3, 4, 5], [6]]
    assert list(tasks.chunked([], 3)) == []
    assert list(tasks.chunked(range(6), 2)) == [[0, 1], [2, 3], [4, 5]]


def test_running_average():
    assert list(tasks.running_average([1, 3, 5])) == [1.0, 2.0, 3.0]
    assert list(tasks.running_average([])) == []


def test_dedupe_with_key():
    assert list(tasks.dedupe([1, 2, 1, 3, 2])) == [1, 2, 3]
    assert list(tasks.dedupe(["a", "A", "b"], key=str.lower)) == ["a", "b"]
    assert list(tasks.dedupe([])) == []


def test_pipeline_composes():
    double = lambda xs: (x * 2 for x in xs)          # noqa: E731
    as_text = lambda xs: (str(x) for x in xs)        # noqa: E731
    run = tasks.pipeline(double, as_text)
    assert list(run([1, 2, 3])) == ["2", "4", "6"]
    assert list(tasks.pipeline()(range(3))) == [0, 1, 2]


def test_pipeline_never_materialises():
    seen = []

    def spy(xs):
        for x in xs:
            seen.append(x)
            yield x

    run = tasks.pipeline(spy, spy)
    gen = run(iter(range(5)))
    assert seen == [], "nothing may run before consumption"
    next(gen)
    assert seen == [0, 0], "each stage observed exactly the first item"
    next(gen)
    assert seen == [0, 0, 1, 1]


# ------------------------------------------------------------ industry
LINES = ["id,name,age\n", "1,ada,36\n", "\n", "2,grace\n",
         "3,alan,41\n", "4,turing,41,extra\n"]


def test_row_parser_skips_and_counts():
    p = tasks.RowParser()
    rows = list(p.parse(iter(LINES)))
    assert rows == [{"id": "1", "name": "ada", "age": "36"},
                    {"id": "3", "name": "alan", "age": "41"}]
    assert p.skipped == 2


def test_row_parser_is_lazy():
    p = tasks.RowParser()

    def source():
        for line in LINES:
            yield line

    gen = p.parse(source())
    assert next(gen)["name"] == "ada"
    assert p.skipped == 0, "must not look ahead beyond what was consumed"


def test_validator_rules_and_rejects():
    v = tasks.Validator({"age": lambda a: a is not None and int(a) >= 40,
                         "name": lambda n: bool(n)})
    rows = [{"name": "ada", "age": "36"}, {"name": "alan", "age": "41"},
            {"name": "", "age": "50"}]
    good = list(v.check(iter(rows)))
    assert good == [{"name": "alan", "age": "41"}]
    assert len(v.rejected) == 2
    assert v.rejected[0][1] == "age" and v.rejected[1][1] == "name"


def test_window():
    assert list(tasks.Window([1, 2, 3, 4], 3)) == [(1, 2, 3), (2, 3, 4)]
    assert list(tasks.Window([1, 2], 3)) == []
    assert list(tasks.Window([1], 1)) == [(1,)]
    w = tasks.Window(range(4), 2)
    assert list(w) == list(w), "must be re-iterable"
    with pytest.raises(ValueError):
        tasks.Window([1], 0)
