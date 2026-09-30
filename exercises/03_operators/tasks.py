"""Module 03 - Operators & expressions.  Student task sheet."""

from __future__ import annotations


# ------------------------------------------------------------------ tier: B
def describe_division(a: int, b: int) -> dict:
    """{"true": a/b, "floor": a//b, "mod": a%b, "divmod": divmod(a, b)}"""
    raise NotImplementedError


def grade(score: float) -> str:
    """Map a score to a letter using CHAINED comparisons only.

    >=90 "A", >=80 "B", >=70 "C", >=60 "D", else "F".
    Out-of-range (score < 0 or score > 100) -> raise ValueError.
    """
    raise NotImplementedError


def bit_summary(n: int) -> dict:
    """{"binary": bin(n), "bit_length": n.bit_length(),
    "is_even": bool, "halved": n >> 1, "low_bit_set": bool(n & 1)}"""
    raise NotImplementedError


# -------------------------------------------------------------- tier: I
def first_truthy(*values):
    """Exact `or` semantics over the arguments.

    Returns the first truthy value, or the LAST value if none is truthy.
    first_truthy() with no arguments -> None.
    """
    raise NotImplementedError


def clip(value, lo, hi):
    """Clamp value into [lo, hi] using only min/max (no if statements)."""
    raise NotImplementedError


def apply_op(name: str, a, b):
    """Dispatch through the operator module.

    Supported names: "+", "-", "*", "/", "//", "%", "**".
    Anything else raises ValueError (not KeyError!).
    """
    raise NotImplementedError


PERMISSION_BITS = {"read": 1, "write": 2, "execute": 4}


def encode_permissions(names) -> int:
    """Combine permission names into one bitmask (ignore duplicates)."""
    raise NotImplementedError


def has_permission(flags: int, name: str) -> bool:
    """True when the bit for *name* is set in *flags*. Unknown name -> False."""
    raise NotImplementedError


# -------------------------------------------------------------- tier: Ind
class Money:
    """Immutable value object: integer minor units + currency code.

    Supports: +, - (binary and unary), ==, <, abs(), str() as e.g. 'EUR 12.34'
    rendered as '12.34 EUR'?  Use exactly: f"{sign}{major}.{minor:02d} {code}"
    e.g. Money(1234, "EUR") -> "12.34 EUR", Money(-5, "USD") -> "-0.05 USD".

    Rules:
      * float amounts raise TypeError
      * mismatched currencies on +/-/comparison raise ValueError
      * adding a plain int means "that many minor units"? NO - it means zero:
        Money + int is only allowed when the int is 0 (identity element),
        otherwise TypeError.  int + Money must work too (reflected).
      * equality across currencies is False (never raise from __eq__)
    """

    def __init__(self, minor: int, currency: str):
        raise NotImplementedError

    # implement the dunders yourself below


def sort_transactions(txns) -> list:
    """Return txns sorted by (currency, amount) using operator.attrgetter."""
    raise NotImplementedError
