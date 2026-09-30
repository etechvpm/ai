"""Module 06 - reference solutions."""

from __future__ import annotations

from collections import Counter, defaultdict, deque


# ------------------------------------------------------------------ tier: B
def frequency(words) -> dict:
    counts: dict = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    return counts


def transpose(matrix) -> list:
    if not matrix:
        return []
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("ragged matrix cannot be transposed")
    return [list(row) for row in zip(*matrix)]


def unique_preserve(seq) -> list:
    seen = set()
    out = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


# -------------------------------------------------------------- tier: I
def group_by(records, key) -> dict:
    getter = (lambda r: r[key]) if isinstance(key, str) else key
    groups: dict = defaultdict(list)
    for record in records:
        groups[getter(record)].append(record)
    return dict(groups)


def invert(mapping) -> dict:
    out: dict = defaultdict(list)
    for k, v in mapping.items():
        out[v].append(k)
    return {v: sorted(ks) for v, ks in out.items()}


def merge_counts(a: dict, b: dict) -> dict:
    total = Counter(a)
    total.update(b)
    return dict(total)


def top_k(words, k: int) -> list:
    counts = Counter(words)
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]


# -------------------------------------------------------------- tier: Ind
class LRUCache:
    def __init__(self, capacity: int):
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity = capacity
        self._data: dict = {}

    def get(self, key, default=None):
        if key not in self._data:
            return default
        self._data[key] = self._data.pop(key)
        return self._data[key]

    def put(self, key, value) -> None:
        if key in self._data:
            self._data.pop(key)
        elif len(self._data) >= self.capacity:
            self._data.pop(next(iter(self._data)))
        self._data[key] = value

    def __len__(self) -> int:
        return len(self._data)


class InvertedIndex:
    def __init__(self):
        self._postings: dict[str, set] = defaultdict(set)

    def add(self, doc_id, text: str) -> None:
        for token in text.lower().split():
            self._postings[token].add(doc_id)

    def search(self, term: str):
        return frozenset(self._postings.get(term.lower(), ()))

    def search_all(self, terms):
        terms = list(terms)
        if not terms:
            return frozenset()
        sets = [set(self.search(t)) for t in terms]
        return frozenset(set.intersection(*sets))

    def search_any(self, terms):
        terms = list(terms)
        if not terms:
            return frozenset()
        return frozenset(set().union(*(set(self.search(t)) for t in terms)))


def sliding_window_max(nums, k: int) -> list:
    if k <= 0:
        raise ValueError("window size must be positive")
    dq: deque = deque()
    out = []
    for i, value in enumerate(nums):
        while dq and nums[dq[-1]] <= value:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out
