"""Module 12 - Iteration, comprehensions & generators.  Student task sheet."""

from __future__ import annotations


# ------------------------------------------------------------------ tier: B
def squares_map(n: int) -> dict:
    """{i: i*i for i in range(n)} - written as a dict comprehension."""
    raise NotImplementedError


def even_squares(nums) -> list:
    """Squares of only the even numbers, as a list comprehension."""
    raise NotImplementedError


def word_lengths(words) -> dict:
    """{word: len(word)} skipping blank/whitespace words (stripped keys)."""
    raise NotImplementedError


def flatten(matrix) -> list:
    """One list comprehension with two for clauses."""
    raise NotImplementedError


# -------------------------------------------------------------- tier: I
def take(n: int, it):
    """Generator: first n items of it (fewer if it is shorter)."""
    raise NotImplementedError


def chunked(it, size: int):
    """Generator of lists of at most *size* items; no empty final chunk."""
    raise NotImplementedError


def running_average(it):
    """Generator yielding the mean of all items seen so far."""
    raise NotImplementedError


def dedupe(it, key=None):
    """Generator: first occurrence order preserved; key(item) decides
    identity (default the item itself)."""
    raise NotImplementedError


def pipeline(*stages):
    """Compose callables (each iterable -> iterable) left to right and
    RETURN A CALLABLE taking the initial iterable."""
    raise NotImplementedError


# -------------------------------------------------------------- tier: Ind
class RowParser:
    """parse(lines) -> generator of dicts from 'a,b,c' lines with a header.

    The first non-empty line is the header. Malformed rows (wrong field
    count) are skipped and counted on parser.skipped. Blank lines ignored.
    """

    def __init__(self):
        raise NotImplementedError

    def parse(self, lines):
        raise NotImplementedError


class Validator:
    """__init__(rules) with rules = {field: predicate}.

    check(rows) -> generator of rows passing ALL rules; failures appended to
    validator.rejected as (row, field) tuples.
    """

    def __init__(self, rules: dict):
        raise NotImplementedError

    def check(self, rows):
        raise NotImplementedError


class Window:
    """Window(iterable, size): iterating yields successive overlapping
    tuples of length size: (1,2,3),(2,3,4),...  size < 1 -> ValueError.
    Re-iterable (fresh iterator each time)."""

    def __init__(self, it, size: int):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError
