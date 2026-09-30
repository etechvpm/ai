"""Module 12 - reference solutions."""

from __future__ import annotations

import collections
import itertools


# ------------------------------------------------------------------ tier: B
def squares_map(n: int) -> dict:
    return {i: i * i for i in range(n)}


def even_squares(nums) -> list:
    return [x * x for x in nums if x % 2 == 0]


def word_lengths(words) -> dict:
    return {w.strip(): len(w.strip()) for w in words if w.strip()}


def flatten(matrix) -> list:
    return [value for row in matrix for value in row]


# -------------------------------------------------------------- tier: I
def take(n: int, it):
    yield from itertools.islice(it, n)


def chunked(it, size: int):
    if size < 1:
        raise ValueError("size must be >= 1")
    source = iter(it)
    while True:
        head = list(itertools.islice(source, size))
        if not head:
            return
        yield head


def running_average(it):
    total = 0
    count = 0
    for value in it:
        total += value
        count += 1
        yield total / count


def dedupe(it, key=None):
    key = key or (lambda v: v)
    seen = set()
    for item in it:
        k = key(item)
        if k not in seen:
            seen.add(k)
            yield item


def pipeline(*stages):
    def run(source):
        current = source
        for stage in stages:
            current = stage(current)
        return current
    return run


# -------------------------------------------------------------- tier: Ind
class RowParser:
    def __init__(self):
        self.skipped = 0

    def parse(self, lines):
        header = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if header is None:
                header = [h.strip() for h in line.split(",")]
                continue
            fields = [f.strip() for f in line.split(",")]
            if len(fields) != len(header):
                self.skipped += 1
                continue
            yield dict(zip(header, fields))


class Validator:
    def __init__(self, rules: dict):
        self.rules = rules
        self.rejected: list = []

    def check(self, rows):
        for row in rows:
            for field, predicate in self.rules.items():
                if not predicate(row.get(field)):
                    self.rejected.append((row, field))
                    break
            else:
                yield row


class Window:
    def __init__(self, it, size: int):
        if size < 1:
            raise ValueError("window size must be >= 1")
        self.it = it
        self.size = size

    def __iter__(self):
        source = iter(self.it)
        buf = collections.deque(itertools.islice(source, self.size),
                                maxlen=self.size)
        if len(buf) == self.size:
            yield tuple(buf)
        for item in source:
            buf.append(item)
            yield tuple(buf)
