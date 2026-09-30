"""Module 06 - Data structures.  Student task sheet."""

from __future__ import annotations


# ------------------------------------------------------------------ tier: B
def frequency(words) -> dict:
    """Count occurrences; keys appear in FIRST-appearance order."""
    raise NotImplementedError


def transpose(matrix) -> list:
    """Rows -> columns.  Ragged input (rows of differing lengths) must raise
    ValueError."""
    raise NotImplementedError


def unique_preserve(seq) -> list:
    """Deduplicate keeping first-occurrence order."""
    raise NotImplementedError


# -------------------------------------------------------------- tier: I
def group_by(records, key) -> dict:
    """Group record dicts by record[key] -> list of records (stable order).

    key may be a string (record field) or a callable.
    """
    raise NotImplementedError


def invert(mapping) -> dict:
    """value -> sorted list of keys having that value."""
    raise NotImplementedError


def merge_counts(a: dict, b: dict) -> dict:
    """Sum counts per key across both dicts."""
    raise NotImplementedError


def top_k(words, k: int) -> list:
    """The k most common words as [(word, count)], count desc then word asc."""
    raise NotImplementedError


# -------------------------------------------------------------- tier: Ind
class LRUCache:
    """get(key, default=None) / put(key, value), both O(1).

    Evicts the least-recently-used entry when capacity is exceeded.
    Updating or reading an entry makes it most-recently-used.
    """

    def __init__(self, capacity: int):
        raise NotImplementedError

    def get(self, key, default=None):
        raise NotImplementedError

    def put(self, key, value) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


class InvertedIndex:
    """add(doc_id, text) tokenises on whitespace (lower-cased).

    search(term)      -> frozenset of doc ids containing term
    search_all(terms) -> ids containing EVERY term (AND)
    search_any(terms) -> ids containing SOME term (OR); empty terms -> empty
    """

    def __init__(self):
        raise NotImplementedError

    def add(self, doc_id, text: str) -> None:
        raise NotImplementedError

    def search(self, term: str):
        raise NotImplementedError

    def search_all(self, terms):
        raise NotImplementedError

    def search_any(self, terms):
        raise NotImplementedError


def sliding_window_max(nums, k: int) -> list:
    """Maximum of every contiguous window of size k, in O(n).

    Use a monotonic deque of indexes. k <= 0 -> ValueError.
    """
    raise NotImplementedError
