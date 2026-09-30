"""Module 02 - reference solutions."""

from __future__ import annotations

import sys
import weakref


# ------------------------------------------------------------------ tier: B
def alias_report(a, b) -> dict:
    return {
        "same_object": a is b,
        "equal": a == b,
        "refcount_a": sys.getrefcount(a) - 1,
    }


def swap(a, b):
    a, b = b, a
    return a, b


def safe_append(item, bag=None):
    if bag is None:
        bag = []
    bag.append(item)
    return bag


# -------------------------------------------------------------- tier: I
def copy_matrix(matrix):
    return [row[:] for row in matrix]


def deep_equal(a, b) -> bool:
    if isinstance(a, dict) or isinstance(b, dict):
        if not (isinstance(a, dict) and isinstance(b, dict)):
            return False
        if set(a) != set(b):
            return False
        return all(deep_equal(a[k], b[k]) for k in a)
    if isinstance(a, list) or isinstance(b, list):
        if not (isinstance(a, list) and isinstance(b, list)):
            return False
        if len(a) != len(b):
            return False
        return all(deep_equal(x, y) for x, y in zip(a, b))
    if type(a) is not type(b):
        return False
    return a == b


def find_shared(original, copies) -> list[int]:
    ids = {id(item) for item in original}
    out = []
    for i, c in enumerate(copies):
        if any(id(item) in ids for item in c):
            out.append(i)
    return out


# -------------------------------------------------------------- tier: Ind
class MemoryLedger:
    def __init__(self):
        self._refs: dict[str, weakref.ReferenceType] = {}
        self._next = 0

    def track(self, obj) -> str:
        self._next += 1
        token = f"obj-{self._next}"
        self._refs[token] = weakref.ref(obj)
        return token

    def alive(self, token) -> bool:
        ref = self._refs.get(token)
        return ref is not None and ref() is not None

    def count(self) -> int:
        return sum(1 for t in self._refs if self.alive(t))


def freeze(mapping):
    if isinstance(mapping, dict):
        return frozenset((k, freeze(v)) for k, v in mapping.items())
    if isinstance(mapping, (list, tuple)):
        return tuple(freeze(v) for v in mapping)
    if isinstance(mapping, set):
        return frozenset(freeze(v) for v in mapping)
    return mapping
