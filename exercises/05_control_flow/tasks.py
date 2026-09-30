"""Module 05 - Control flow.  Student task sheet."""

from __future__ import annotations

from enum import Enum, auto


# ------------------------------------------------------------------ tier: B
def fizzbuzz(n: int) -> list[str]:
    """Labels for 1..n: 'Fizz' (mult of 3), 'Buzz' (5), 'FizzBuzz' (both),
    else str(number)."""
    raise NotImplementedError


def classify(values) -> list[str]:
    """Each number -> 'negative' | 'zero' | 'small' (<10) | 'large'."""
    raise NotImplementedError


def sum_evens(matrix) -> int:
    """Sum only even numbers of a 2-D list, using `continue` to skip odds."""
    raise NotImplementedError


# -------------------------------------------------------------- tier: I
def first_admin(users):
    """Return the first dict with a truthy 'admin' key, else None.

    Must use a for...else construct and NO flag variable.
    """
    raise NotImplementedError


def run_length_encode(seq) -> list:
    """[(item, run_length), ...] for consecutive equal items.

    'aaabbc' -> [('a', 3), ('b', 2), ('c', 1)]
    """
    raise NotImplementedError


def parse_sections(lines) -> dict:
    """Group lines under '[header]' markers.

    Lines before any header belong to key "". Header lines themselves are not
    content. Blank lines are ignored entirely.
    """
    raise NotImplementedError


# -------------------------------------------------------------- tier: Ind
class OrderState(Enum):
    DRAFT = auto()
    SUBMITTED = auto()
    PAID = auto()
    SHIPPED = auto()
    DELIVERED = auto()
    CANCELLED = auto()


class InvalidTransition(ValueError):
    pass


# The legal transition graph. Fill it in.
TRANSITIONS: dict = {}


class Order:
    def __init__(self, state=OrderState.DRAFT):
        self.state = state


def advance(order, target) -> None:
    """Move order.state to target if legal, else raise InvalidTransition."""
    raise NotImplementedError


def shortest_path(start, target):
    """List of states forming a legal transition sequence start -> target
    (inclusive), or None when unreachable. Breadth-first over TRANSITIONS.
    shortest_path(s, s) -> [s]."""
    raise NotImplementedError


def chunk_while(predicate, iterable):
    """Split iterable into lists of consecutive items while
    predicate(prev, current) holds between neighbours.

    chunk_while(lambda a, b: b - a == 1, [1, 2, 3, 7, 8]) -> [[1, 2, 3], [7, 8]]
    """
    raise NotImplementedError
