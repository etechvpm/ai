"""Grader for module 19 (capstone).  Run:  pytest exercises/19_capstone -q"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

import pytest

from _loader import load

tasks = load(__file__)

CSV = """id,region,customer,amount,date
A1,north,ada,"1,200.50",2024-01-05
A2,south,lin,300.00,2024-01-06
A3,north,ada,450.25,2024-02-01
"""

DIRTY = """id,region,customer,amount,date
B1,north,ada,100.00,2024-01-05
B2,south,,50.00,2024-01-06
B3,east,kim,not-a-number,2024-01-07
B4,west,zoe,-5.00,2024-01-08
B5,north,ada,25.00,31/12/2024
B6,south,lin,10.00,2024-03-01
"""


# ------------------------------------------------------------ exceptions
def test_exception_hierarchy():
    assert issubclass(tasks.ParseError, tasks.ReportError)
    assert issubclass(tasks.ValidationError, tasks.ReportError)
    assert issubclass(tasks.ReportError, Exception)


# ------------------------------------------------------------- data model
def test_dataclasses_are_frozen_records():
    order = tasks.Order(id="A1", region="north", customer="ada",
                        amount=Decimal("1.00"), date=dt.date(2024, 1, 1))
    assert order.region == "north"
    with pytest.raises(Exception):
        order.region = "south"                     # frozen
    assert hasattr(order, "__slots__") or "slots" in type(order).__dict__ \
        or not hasattr(order, "__dict__"), "should use slots=True"


# ------------------------------------------------------------- primitives
def test_parse_money():
    assert tasks.parse_money("1,234.56") == Decimal("1234.56")
    assert tasks.parse_money(" 12.5 ") == Decimal("12.50")
    assert tasks.parse_money(7) == Decimal("7.00")
    assert tasks.parse_money(Decimal("0.005")) == Decimal("0.01")  # HALF_UP
    for bad in ["abc", "", None, "1.2.3"]:
        with pytest.raises(tasks.ParseError):
            tasks.parse_money(bad)


def test_retry_decorator_retries_and_reports_attempts():
    sleeps = []
    calls = []

    @tasks.retry(times=4, delay=0.5, sleep=sleeps.append)
    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise ConnectionError("transient")
        return "ok"

    assert flaky() == "ok"
    assert len(calls) == 3
    assert sleeps == [0.5, 0.5], "sleep between attempts, not after success"
    assert flaky.attempts == 3
    assert flaky.__name__ == "flaky", "functools.wraps required"


def test_retry_reraises_last_exception():
    @tasks.retry(times=3, delay=0, sleep=lambda _s: None)
    def always_fails():
        raise ValueError("permanent")

    with pytest.raises(ValueError, match="permanent"):
        always_fails()


# --------------------------------------------------------------- pipeline
def test_load_orders_is_lazy_and_parses():
    orders = tasks.load_orders(CSV)
    first = next(iter(orders))
    assert first.id == "A1"
    assert first.amount == Decimal("1200.50")
    assert first.date == dt.date(2024, 1, 5)
    assert [o.id for o in orders] == ["A2", "A3"], "lazy: resumes where it stopped"
    rest = list(tasks.load_orders(CSV))
    assert [o.id for o in rest] == ["A1", "A2", "A3"]


def test_load_orders_lenient_skips_bad_rows():
    rows = list(tasks.load_orders(DIRTY))
    assert [r.id for r in rows] == ["B1", "B6"]


def test_load_orders_strict_raises():
    gen = tasks.load_orders(DIRTY, strict=True)
    assert next(gen).id == "B1"
    with pytest.raises(tasks.ValidationError):
        next(gen)


def test_summarise_aggregates():
    summary = tasks.summarise(tasks.load_orders(CSV))
    assert summary.count == 3
    assert summary.total == Decimal("1950.75")
    assert summary.average == Decimal("650.25")
    assert list(summary.by_region) == ["north", "south"]
    assert summary.by_region["north"] == Decimal("1650.75")
    assert summary.top_customer == "ada"


def test_summarise_handles_empty_and_single_pass():
    empty = tasks.summarise(iter([]))
    assert empty.count == 0 and empty.total == Decimal("0.00")
    assert empty.average == Decimal("0.00") and empty.top_customer is None

    consumed = {"n": 0}

    def counting():
        for order in tasks.load_orders(CSV):
            consumed["n"] += 1
            yield order

    summary = tasks.summarise(counting())
    assert summary.count == 3 and consumed["n"] == 3, "single pass only"


def test_render_markdown_is_stable():
    out = tasks.render_markdown(tasks.summarise(tasks.load_orders(CSV)))
    assert out.startswith("# Sales summary\n")
    assert "| orders | 3 |" in out
    assert "| total | 1950.75 |" in out
    assert "| average | 650.25 |" in out
    assert "| top customer | ada |" in out
    assert "## By region" in out
    assert out.index("| north | 1650.75 |") < out.index("| south | 300.00 |")
    assert out.endswith("\n")
    assert out == tasks.render_markdown(
        tasks.summarise(tasks.load_orders(CSV))), "deterministic"


def test_render_markdown_empty_summary():
    out = tasks.render_markdown(tasks.summarise([]))
    assert "| top customer | - |" in out
    assert "| orders | 0 |" in out


def test_run_report_end_to_end():
    report = tasks.run_report(DIRTY)
    assert "| orders | 2 |" in report
    assert "| total | 110.00 |" in report
    with pytest.raises(tasks.ValidationError):
        tasks.run_report(DIRTY, strict=True)
