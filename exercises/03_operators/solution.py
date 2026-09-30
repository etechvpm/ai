"""Module 03 - reference solutions."""

from __future__ import annotations

import operator

# ------------------------------------------------------------------ tier: B


def describe_division(a: int, b: int) -> dict:
    return {"true": a / b, "floor": a // b, "mod": a % b,
            "divmod": divmod(a, b)}


def grade(score: float) -> str:
    if not 0 <= score <= 100:
        raise ValueError(f"score out of range: {score}")
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def bit_summary(n: int) -> dict:
    return {"binary": bin(n), "bit_length": n.bit_length(),
            "is_even": not n & 1, "halved": n >> 1, "low_bit_set": bool(n & 1)}


# -------------------------------------------------------------- tier: I
def first_truthy(*values):
    if not values:
        return None
    for v in values:
        if v:
            return v
    return values[-1]


def clip(value, lo, hi):
    return min(max(value, lo), hi)


_OPS = {
    "+": operator.add, "-": operator.sub, "*": operator.mul,
    "/": operator.truediv, "//": operator.floordiv, "%": operator.mod,
    "**": operator.pow,
}


def apply_op(name: str, a, b):
    fn = _OPS.get(name)
    if fn is None:
        raise ValueError(f"unsupported operator: {name!r}")
    return fn(a, b)


PERMISSION_BITS = {"read": 1, "write": 2, "execute": 4}


def encode_permissions(names) -> int:
    flags = 0
    for name in names:
        flags |= PERMISSION_BITS[name]
    return flags


def has_permission(flags: int, name: str) -> bool:
    bit = PERMISSION_BITS.get(name)
    if bit is None:
        return False
    return bool(flags & bit)


# -------------------------------------------------------------- tier: Ind
class Money:
    __slots__ = ("minor", "currency")

    def __init__(self, minor: int, currency: str):
        if isinstance(minor, float):
            raise TypeError("Money amounts must be integer minor units, "
                            f"got float {minor!r}")
        if not isinstance(minor, int):
            raise TypeError(f"minor units must be int, got {type(minor).__name__}")
        self.minor = minor
        self.currency = str(currency).upper()

    # -- helpers -----------------------------------------------------
    def _same(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(
                f"currency mismatch: {self.currency} vs {other.currency}")
        return other

    def _as_int(self, other):
        """int operand: only 0 is a legal identity element."""
        if isinstance(other, bool):
            return NotImplemented
        if isinstance(other, int):
            if other != 0:
                raise TypeError(
                    "cannot add a non-zero plain int to Money "
                    "(ambiguous currency); construct Money explicitly")
            return Money(0, self.currency)
        return NotImplemented

    # -- arithmetic ----------------------------------------------------
    def __add__(self, other):
        o = self._same(other)
        if o is NotImplemented:
            o = self._as_int(other)
        if o is NotImplemented:
            return NotImplemented
        return Money(self.minor + o.minor, self.currency)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        o = self._same(other)
        if o is NotImplemented:
            o = self._as_int(other)
        if o is NotImplemented:
            return NotImplemented
        return Money(self.minor - o.minor, self.currency)

    def __neg__(self):
        return Money(-self.minor, self.currency)

    def __abs__(self):
        return Money(abs(self.minor), self.currency)

    # -- comparison ------------------------------------------------------
    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return (self.currency == other.currency
                and self.minor == other.minor)

    def __lt__(self, other):
        o = self._same(other)
        if o is NotImplemented:
            return NotImplemented
        return self.minor < o.minor

    def __hash__(self):
        return hash((self.minor, self.currency))

    # -- presentation ----------------------------------------------------
    def __str__(self):
        sign = "-" if self.minor < 0 else ""
        major, rest = divmod(abs(self.minor), 100)
        return f"{sign}{major}.{rest:02d} {self.currency}"

    def __repr__(self):
        return f"Money({self.minor}, {self.currency!r})"


def sort_transactions(txns) -> list:
    return sorted(txns, key=operator.attrgetter("currency", "minor"))
