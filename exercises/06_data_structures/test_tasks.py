"""Grader for module 06.  Run:  pytest exercises/06_data_structures -q"""

from __future__ import annotations

import pytest

from _loader import load

tasks = load(__file__)


# ------------------------------------------------------------- beginner
def test_frequency_first_appearance_order():
    out = tasks.frequency(["b", "a", "b", "c", "b", "a"])
    assert out == {"b": 3, "a": 2, "c": 1}
    assert list(out) == ["b", "a", "c"]
    assert tasks.frequency([]) == {}


def test_transpose():
    assert tasks.transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
    assert tasks.transpose([]) == []
    assert tasks.transpose([[7]]) == [[7]]
    with pytest.raises(ValueError):
        tasks.transpose([[1, 2], [3]])


def test_unique_preserve():
    assert tasks.unique_preserve([3, 1, 3, 2, 1]) == [3, 1, 2]
    assert tasks.unique_preserve("abacb") == ["a", "b", "c"]
    assert tasks.unique_preserve([]) == []


# --------------------------------------------------------- intermediate
def test_group_by_field_and_callable():
    rows = [{"d": "x", "v": 1}, {"d": "y", "v": 2}, {"d": "x", "v": 3}]
    g = tasks.group_by(rows, "d")
    assert list(g) == ["x", "y"]
    assert g["x"] == [rows[0], rows[2]]
    g2 = tasks.group_by([1, 2, 3, 4], lambda n: n % 2)
    assert g2 == {1: [1, 3], 0: [2, 4]}


def test_invert_collects_collisions():
    assert tasks.invert({"a": 1, "b": 2, "c": 1}) == {1: ["a", "c"], 2: ["b"]}
    assert tasks.invert({}) == {}


def test_merge_counts():
    assert tasks.merge_counts({"a": 1, "b": 2}, {"b": 3, "c": 4}) == {
        "a": 1, "b": 5, "c": 4}
    assert tasks.merge_counts({}, {}) == {}


def test_top_k_ordering():
    words = ["a", "b", "a", "c", "b", "a", "d", "d", "d", "d"]
    assert tasks.top_k(words, 3) == [("d", 4), ("a", 3), ("b", 2)]
    # tie on count -> alphabetical
    assert tasks.top_k(["z", "y", "z", "y"], 2) == [("y", 2), ("z", 2)]
    assert tasks.top_k(words, 0) == []


# ------------------------------------------------------------ industry
def test_lru_eviction_order():
    c = tasks.LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert c.get("a") == 1            # a becomes most recent
    c.put("c", 3)                     # evicts b
    assert c.get("b") is None
    assert c.get("c") == 3
    assert len(c) == 2


def test_lru_update_refreshes():
    c = tasks.LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("a", 10)                    # update refreshes a
    c.put("c", 3)                     # evicts b
    assert c.get("a") == 10 and c.get("b") is None


def test_lru_get_default():
    c = tasks.LRUCache(1)
    assert c.get("nope") is None
    assert c.get("nope", "fallback") == "fallback"


def test_inverted_index():
    ix = tasks.InvertedIndex()
    ix.add(1, "The quick brown fox")
    ix.add(2, "the quick hare")
    ix.add(3, "slow turtle")
    assert ix.search("the") == frozenset({1, 2})
    assert ix.search("turtle") == frozenset({3})
    assert ix.search("missing") == frozenset()
    assert ix.search_all(["quick", "hare"]) == frozenset({2})
    assert ix.search_all(["quick", "turtle"]) == frozenset()
    assert ix.search_any(["fox", "turtle"]) == frozenset({1, 3})
    assert ix.search_any([]) == frozenset()
    assert ix.search_all([]) == frozenset()


@pytest.mark.parametrize("nums,k,expected", [
    ([1, 3, -1, -3, 5, 3, 6, 7], 3, [3, 3, 5, 5, 6, 7]),
    ([1, -1, 1, -1], 1, [1, -1, 1, -1]),
    ([9, 8, 7], 3, [9]),
    ([], 2, []),
])
def test_sliding_window_max(nums, k, expected):
    assert tasks.sliding_window_max(nums, k) == expected


def test_sliding_window_max_rejects_bad_k():
    with pytest.raises(ValueError):
        tasks.sliding_window_max([1, 2], 0)
