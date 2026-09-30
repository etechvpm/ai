"""Module 02 - Variables, types & memory.  Student task sheet."""

from __future__ import annotations


# ------------------------------------------------------------------ tier: B
def alias_report(a, b) -> dict:
    """Describe how two objects relate.

    Returns {"same_object": bool, "equal": bool, "refcount_a": int}.
    refcount_a is sys.getrefcount(a) MINUS the one reference added by passing
    it as an argument.
    """
    raise NotImplementedError


def swap(a, b):
    """Return (b, a) using tuple unpacking, no temporary variable."""
    raise NotImplementedError


def safe_append(item, bag=None):
    """Append item to bag and return it.

    bag defaults to None so that every call without an explicit bag gets its
    OWN fresh list (the classic mutable-default trap).
    """
    raise NotImplementedError


# -------------------------------------------------------------- tier: I
def copy_matrix(matrix):
    """Return a copy of a 2-D list where rows are independent objects.

    Mutating copy[i] must not affect matrix[i]; the outer list must also be a
    new object. Inner *values* may be shared (they are immutable here).
    """
    raise NotImplementedError


def deep_equal(a, b) -> bool:
    """Value-compare nested structures of lists/dicts/scalars.

    Do NOT simply `return a == b`: walk the structures yourself, comparing
    dicts by key set and values, lists element-wise, everything else with ==.
    """
    raise NotImplementedError


def find_shared(original, copies) -> list[int]:
    """Indexes of copies that share ANY object with original.

    Two containers 'share' when some element of one `is` some element of the
    other (top-level elements are enough).
    """
    raise NotImplementedError


# -------------------------------------------------------------- tier: Ind
class MemoryLedger:
    """Track objects WITHOUT keeping them alive (weakref).

    track(obj) -> token (str, unique per call)
    alive(token) -> True while the tracked object still exists
    count() -> number of currently alive tracked objects
    Objects that cannot be weak-referenced (e.g. int, str) must raise
    TypeError from track().
    """

    def __init__(self):
        raise NotImplementedError

    def track(self, obj) -> str:
        raise NotImplementedError

    def alive(self, token) -> bool:
        raise NotImplementedError

    def count(self) -> int:
        raise NotImplementedError


def freeze(mapping):
    """Return a hashable, deeply-immutable representation of a nested
    dict/list/scalar structure, such that:

      freeze(x) == freeze(y)  whenever x and y are value-equal
      hash(freeze(x)) works
      the result can be used as a dict key

    Dicts become frozensets of (key, frozen_value) pairs; lists become tuples.
    """
    raise NotImplementedError
