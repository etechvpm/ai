"""Grader for module 03.  Run:  pytest exercises/03_operators -q"""

from __future__ import annotations

import pytest

from _loader import load

tasks = load(__file__)
Money = tasks.Money


# ------------------------------------------------------------- beginner
def test_describe_division():
    assert tasks.describe_division(7, 2) == {
        "true": 3.5, "floor": 3, "mod": 1, "divmod": (3, 1)}
    assert tasks.describe_division(-7, 2)["floor"] == -4
    assert tasks.describe_division(-7, 2)["mod"] == 1


@pytest.mark.parametrize("score,letter", [
    (100, "A"), (90, "A"), (89.9, "B"), (80, "B"), (70, "C"),
    (60, "D"), (59.9, "F"), (0, "F")])
def test_grade(score, letter):
    assert tasks.grade(score) == letter


@pytest.mark.parametrize("bad", [-0.1, 100.1, -5])
def test_grade_out_of_range(bad):
    with pytest.raises(ValueError):
        tasks.grade(bad)


def test_bit_summary():
    s = tasks.bit_summary(12)
    assert s == {"binary": "0b1100", "bit_length": 4, "is_even": True,
                 "halved": 6, "low_bit_set": False}
    assert tasks.bit_summary(7)["low_bit_set"] is True
    assert tasks.bit_summary(7)["halved"] == 3


# --------------------------------------------------------- intermediate
def test_first_truthy_or_semantics():
    assert tasks.first_truthy(0, "", "x", 3) == "x"
    assert tasks.first_truthy(0, "", []) == []
    assert tasks.first_truthy(None, False) is False
    assert tasks.first_truthy() is None
    assert tasks.first_truthy(5) == 5


@pytest.mark.parametrize("v,lo,hi,exp", [
    (5, 0, 10, 5), (-3, 0, 10, 0), (42, 0, 10, 10), (0, 0, 10, 0),
    (10, 0, 10, 10)])
def test_clip(v, lo, hi, exp):
    assert tasks.clip(v, lo, hi) == exp


@pytest.mark.parametrize("name,a,b,exp", [
    ("+", 2, 3, 5), ("-", 2, 3, -1), ("*", 2, 3, 6), ("/", 7, 2, 3.5),
    ("//", 7, 2, 3), ("%", 7, 2, 1), ("**", 2, 5, 32)])
def test_apply_op(name, a, b, exp):
    assert tasks.apply_op(name, a, b) == exp


@pytest.mark.parametrize("bad", ["&", "|", "^", "<<", "and", ""])
def test_apply_op_rejects(bad):
    with pytest.raises(ValueError):
        tasks.apply_op(bad, 1, 2)


def test_permission_bitmask():
    flags = tasks.encode_permissions(["read", "execute", "read"])
    assert flags == 0b101
    assert tasks.has_permission(flags, "read") is True
    assert tasks.has_permission(flags, "write") is False
    assert tasks.has_permission(flags, "nope") is False
    assert tasks.encode_permissions([]) == 0
    assert tasks.encode_permissions(["read", "write", "execute"]) == 0b111


# ------------------------------------------------------------ industry
def test_money_str_format():
    assert str(Money(1234, "EUR")) == "12.34 EUR"
    assert str(Money(-5, "USD")) == "-0.05 USD"
    assert str(Money(0, "INR")) == "0.00 INR"
    assert str(Money(100005, "GBP")) == "1000.05 GBP"


def test_money_rejects_float():
    with pytest.raises(TypeError):
        Money(12.5, "EUR")


def test_money_arithmetic_and_mismatch():
    a, b = Money(100, "EUR"), Money(250, "EUR")
    assert (a + b) == Money(350, "EUR")
    assert (b - a) == Money(150, "EUR")
    assert abs(Money(-99, "EUR")) == Money(99, "EUR")
    assert -a == Money(-100, "EUR")
    with pytest.raises(ValueError):
        a + Money(1, "USD")
    with pytest.raises(ValueError):
        a < Money(1, "USD")


def test_money_int_identity_only():
    assert Money(50, "EUR") + 0 == Money(50, "EUR")
    assert 0 + Money(50, "EUR") == Money(50, "EUR")     # reflected
    with pytest.raises(TypeError):
        Money(50, "EUR") + 5


def test_money_equality_and_hash():
    assert Money(10, "EUR") == Money(10, "EUR")
    assert (Money(10, "EUR") == Money(10, "USD")) is False   # no raise
    assert (Money(10, "EUR") == "10.00 EUR") is False
    assert len({Money(10, "EUR"), Money(10, "EUR"), Money(10, "USD")}) == 2


def test_money_ordering():
    xs = [Money(300, "EUR"), Money(100, "EUR"), Money(200, "EUR")]
    assert sorted(xs) == [Money(100, "EUR"), Money(200, "EUR"),
                          Money(300, "EUR")]


def test_sort_transactions():
    txns = [Money(500, "USD"), Money(100, "EUR"), Money(200, "USD"),
            Money(50, "EUR")]
    out = tasks.sort_transactions(txns)
    assert [(t.currency, t.minor) for t in out] == [
        ("EUR", 50), ("EUR", 100), ("USD", 200), ("USD", 500)]
