"""Grader for module 02.  Run:  pytest exercises/02_memory -q"""

from __future__ import annotations

import gc

import pytest

from _loader import load

tasks = load(__file__)


# ------------------------------------------------------------- beginner
def test_alias_report():
    a = [1, 2]
    b = a
    rep = tasks.alias_report(a, b)
    assert rep == {"same_object": True, "equal": True,
                   "refcount_a": rep["refcount_a"]}
    assert rep["refcount_a"] >= 1
    c = [1, 2]
    rep2 = tasks.alias_report(a, c)
    assert rep2["same_object"] is False and rep2["equal"] is True


def test_swap():
    assert tasks.swap(1, 2) == (2, 1)
    x, y = [], {}
    a, b = tasks.swap(x, y)
    assert a is y and b is x


def test_safe_append_no_shared_default():
    first = tasks.safe_append(1)
    second = tasks.safe_append(2)
    assert first == [1] and second == [2]
    assert first is not second
    bag = [0]
    assert tasks.safe_append(9, bag) is bag and bag == [0, 9]


# --------------------------------------------------------- intermediate
def test_copy_matrix_independent_rows():
    m = [[1, 2], [3, 4]]
    c = tasks.copy_matrix(m)
    assert c == m and c is not m
    c[0].append(99)
    c[1][0] = 0
    assert m == [[1, 2], [3, 4]]


@pytest.mark.parametrize("a,b,expected", [
    ({"x": [1, {"y": 2}]}, {"x": [1, {"y": 2}]}, True),
    ({"x": [1, {"y": 2}]}, {"x": [1, {"y": 3}]}, False),
    ([1, [2, [3]]], [1, [2, [3]]], True),
    ([1, [2, [3]]], [1, [2, 3]], False),
    ({"a": 1}, ["a"], False),
    (1, 1.0, False),
    (None, None, True),
])
def test_deep_equal(a, b, expected):
    assert tasks.deep_equal(a, b) is expected


def test_find_shared():
    inner = {"k": 1}
    other = {"only": object()}          # never interned: identity is unique
    original = [inner, other]
    shared = [inner]
    cloned = [{"k": 1}, {"only": "equal but distinct"}]
    assert tasks.find_shared(original, [shared, cloned, []]) == [0]
    assert tasks.find_shared(original, [cloned, [other]]) == [1]


# ------------------------------------------------------------ industry
def test_memory_ledger_does_not_keep_alive():
    led = tasks.MemoryLedger()

    class Box:
        pass

    box = Box()
    token = led.track(box)
    assert led.alive(token) is True
    assert led.count() == 1
    del box
    gc.collect()
    assert led.alive(token) is False
    assert led.count() == 0


def test_memory_ledger_rejects_unweakrefable():
    led = tasks.MemoryLedger()
    with pytest.raises(TypeError):
        led.track(42)
    with pytest.raises(TypeError):
        led.track("text")


def test_freeze_is_hashable_and_stable():
    a = {"b": [1, 2], "c": {"d": None}}
    b = {"c": {"d": None}, "b": [1, 2]}
    fa, fb = tasks.freeze(a), tasks.freeze(b)
    assert fa == fb
    assert hash(fa) == hash(fb)
    table = {fa: "hit"}
    assert table[fb] == "hit"
    assert tasks.freeze([1, [2, 3]]) == tasks.freeze([1, [2, 3]])
    assert tasks.freeze([1, 2]) != tasks.freeze([2, 1])
