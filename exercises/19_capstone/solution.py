"""Module 19 - Capstone reference implementation."""

from __future__ import annotations

import csv
import datetime as dt
import functools
import io
import time
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


# ------------------------------------------------------- error hierarchy
class ReportError(Exception):
    """Base class for every error in this module."""


class ParseError(ReportError):
    """Input could not be parsed."""


class ValidationError(ReportError):
    """Parsed data violated a business rule."""


# ------------------------------------------------------------- data model
@dataclass(frozen=True, slots=True)
class Order:
    id: str
    region: str
    customer: str
    amount: Decimal
    date: dt.date


@dataclass(frozen=True, slots=True)
class Summary:
    count: int
    total: Decimal
    by_region: dict
    top_customer: str | None
    average: Decimal


# ------------------------------------------------------------- primitives
_CENTS = Decimal("0.01")


def _money(value) -> Decimal:
    return Decimal(value).quantize(_CENTS, rounding=ROUND_HALF_UP)


def parse_money(text) -> Decimal:
    if isinstance(text, Decimal):
        return _money(text)
    if isinstance(text, (int, float)):
        return _money(Decimal(str(text)))
    if not isinstance(text, str) or not text.strip():
        raise ParseError(f"cannot parse money from {text!r}")
    cleaned = text.strip().replace(",", "").replace(" ", "")
    if cleaned[:1] in "+-":
        cleaned = cleaned[1:]
    if not cleaned.replace(".", "", 1).isdigit():
        raise ParseError(f"cannot parse money from {text!r}")
    try:
        return _money(Decimal(text.strip().replace(",", "")))
    except InvalidOperation as exc:
        raise ParseError(f"cannot parse money from {text!r}") from exc


def retry(times: int = 3, delay: float = 0.0, sleep=None):
    if times < 1:
        raise ValueError("times must be >= 1")
    do_sleep = sleep or time.sleep

    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last: BaseException | None = None
            for attempt in range(1, times + 1):
                wrapper.attempts = attempt
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:            # noqa: BLE001 - retried
                    last = exc
                    if attempt < times:
                        do_sleep(delay)
            assert last is not None
            raise last

        wrapper.attempts = 0
        return wrapper

    return decorate


# --------------------------------------------------------------- pipeline
CSV_COLUMNS = ("id", "region", "customer", "amount", "date")


def _parse_row(row: dict, line_no: int) -> Order:
    if any(not (row.get(col) or "").strip() for col in CSV_COLUMNS):
        raise ValidationError(f"line {line_no}: missing field")
    amount = parse_money(row["amount"])
    if amount <= 0:
        raise ValidationError(f"line {line_no}: amount must be positive")
    try:
        date = dt.date.fromisoformat(row["date"].strip())
    except ValueError as exc:
        raise ValidationError(f"line {line_no}: bad date") from exc
    return Order(id=row["id"].strip(), region=row["region"].strip(),
                 customer=row["customer"].strip(), amount=amount, date=date)


def load_orders(text, strict: bool = False):
    reader = csv.DictReader(io.StringIO(text))
    for line_no, row in enumerate(reader, start=2):
        try:
            yield _parse_row(row, line_no)
        except (ValidationError, ParseError):
            if strict:
                raise
            continue                     # lenient: skip the bad row


def summarise(orders) -> Summary:
    count = 0
    total = Decimal("0.00")
    per_region: dict[str, Decimal] = {}
    per_customer: dict[str, Decimal] = {}
    for order in orders:                 # single pass, generator friendly
        count += 1
        total += order.amount
        per_region[order.region] = per_region.get(order.region,
                                                  Decimal("0")) + order.amount
        per_customer[order.customer] = per_customer.get(
            order.customer, Decimal("0")) + order.amount
    by_region = dict(sorted(per_region.items(),
                            key=lambda kv: (-kv[1], kv[0])))
    top_customer = None
    if per_customer:
        top_customer = sorted(per_customer.items(),
                              key=lambda kv: (-kv[1], kv[0]))[0][0]
    average = _money(total / count) if count else Decimal("0.00")
    return Summary(count=count, total=_money(total), by_region=by_region,
                   top_customer=top_customer, average=average)


def render_markdown(summary) -> str:
    lines = [
        "# Sales summary",
        "",
        "| metric | value |",
        "| --- | --- |",
        f"| orders | {summary.count} |",
        f"| total | {summary.total} |",
        f"| average | {summary.average} |",
        f"| top customer | {summary.top_customer or '-'} |",
        "",
        "## By region",
        "",
        "| region | total |",
        "| --- | --- |",
    ]
    lines += [f"| {region} | {total} |"
              for region, total in summary.by_region.items()]
    return "\n".join(lines) + "\n"


def run_report(csv_text, strict: bool = False) -> str:
    return render_markdown(summarise(load_orders(csv_text, strict=strict)))
