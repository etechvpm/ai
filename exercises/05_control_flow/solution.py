"""Module 05 - reference solutions."""

from __future__ import annotations

from collections import deque
from enum import Enum, auto


# ------------------------------------------------------------------ tier: B
def fizzbuzz(n: int) -> list[str]:
    out = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            out.append("FizzBuzz")
        elif i % 3 == 0:
            out.append("Fizz")
        elif i % 5 == 0:
            out.append("Buzz")
        else:
            out.append(str(i))
    return out


def classify(values) -> list[str]:
    out = []
    for v in values:
        if v < 0:
            out.append("negative")
        elif v == 0:
            out.append("zero")
        elif v < 10:
            out.append("small")
        else:
            out.append("large")
    return out


def sum_evens(matrix) -> int:
    total = 0
    for row in matrix:
        for value in row:
            if value % 2:
                continue
            total += value
    return total


# -------------------------------------------------------------- tier: I
def first_admin(users):
    for user in users:
        if user.get("admin"):
            return user
    else:
        return None


def run_length_encode(seq) -> list:
    out: list = []
    for item in seq:
        if out and out[-1][0] == item:
            out[-1][1] += 1
        else:
            out.append([item, 1])
    return [(item, n) for item, n in out]


def parse_sections(lines) -> dict:
    sections: dict[str, list[str]] = {"": []}
    current = ""
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            current = stripped[1:-1]
            sections.setdefault(current, [])
        else:
            sections[current].append(stripped)
    return sections


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


TRANSITIONS: dict = {
    OrderState.DRAFT: {OrderState.SUBMITTED, OrderState.CANCELLED},
    OrderState.SUBMITTED: {OrderState.PAID, OrderState.CANCELLED},
    OrderState.PAID: {OrderState.SHIPPED, OrderState.CANCELLED},
    OrderState.SHIPPED: {OrderState.DELIVERED},
    OrderState.DELIVERED: set(),
    OrderState.CANCELLED: set(),
}


class Order:
    def __init__(self, state=OrderState.DRAFT):
        self.state = state


def advance(order, target) -> None:
    if target not in TRANSITIONS[order.state]:
        raise InvalidTransition(
            f"cannot move {order.state.name} -> {target.name}")
    order.state = target


def shortest_path(start, target):
    if start is target:
        return [start]
    seen = {start}
    queue = deque([(start, [start])])
    while queue:
        state, path = queue.popleft()
        for nxt in sorted(TRANSITIONS[state], key=lambda s: s.name):
            if nxt in seen:
                continue
            seen.add(nxt)
            new_path = path + [nxt]
            if nxt is target:
                return new_path
            queue.append((nxt, new_path))
    return None


def chunk_while(predicate, iterable):
    chunks: list[list] = []
    for item in iterable:
        if chunks and predicate(chunks[-1][-1], item):
            chunks[-1].append(item)
        else:
            chunks.append([item])
    return chunks
