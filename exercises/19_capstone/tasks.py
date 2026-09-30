"""Module 19 - Capstone.  Student task sheet: build a small report pipeline.

This is the course in miniature: exceptions, dataclasses, generators, Decimal
money, a decorator with dependency injection, aggregation and rendering.
"""

from __future__ import annotations


# ------------------------------------------------------- error hierarchy
class ReportError(Exception):
    """Base class for every error in this module."""


class ParseError(ReportError):
    """Input text/number could not be parsed."""


class ValidationError(ReportError):
    """Parsed data violated a business rule."""


# ------------------------------------------------------------- data model
class Order:
    """Frozen, slots dataclass: id: str, region: str, customer: str,
    amount: Decimal, date: datetime.date."""


class Summary:
    """Frozen, slots dataclass: count: int, total: Decimal,
    by_region: dict[str, Decimal], top_customer: str | None,
    average: Decimal (0 when count == 0)."""


# ------------------------------------------------------------- primitives
def parse_money(text):
    """'1,234.56' / '1234.56' / 1234.56 -> Decimal('1234.56').

    Raises ParseError for junk ('abc', '', None) and for anything that is not
    a number. Quantise to 2 decimal places (ROUND_HALF_UP).
    """
    raise NotImplementedError


def retry(times: int = 3, delay: float = 0.0, sleep=None):
    """Decorator factory: call the wrapped function up to `times` attempts.

    * sleep defaults to time.sleep but MUST be injectable for tests;
    * sleep(delay) between attempts, never after the last one;
    * if all attempts fail, re-raise the LAST exception;
    * the wrapper keeps the original name/docstring (functools.wraps) and
      exposes .attempts (attempts made by the last call).
    """
    raise NotImplementedError


# --------------------------------------------------------------- pipeline
CSV_COLUMNS = ("id", "region", "customer", "amount", "date")


def load_orders(text, strict: bool = False):
    """LAZY generator over CSV text with a header row.

    Yields Order objects. A row is invalid when: a field is missing, the
    amount does not parse, the date is not ISO (YYYY-MM-DD), or the amount is
    <= 0.
      strict=False -> skip invalid rows (never raise)
      strict=True  -> raise ValidationError naming the row id/line
    Must not materialise the whole file: consuming one row must not read all.
    """
    raise NotImplementedError


def summarise(orders) -> "Summary":
    """Aggregate an iterable of Orders (works on a generator, single pass).

    total/average quantised to 2dp; by_region sorted by descending total then
    region name; top_customer = customer with the highest summed amount
    (alphabetical tie-break), None when there are no orders.
    """
    raise NotImplementedError


def render_markdown(summary) -> str:
    """Deterministic Markdown:

    # Sales summary

    | metric | value |
    | --- | --- |
    | orders | <count> |
    | total | <total> |
    | average | <average> |
    | top customer | <name or '-'> |

    ## By region

    | region | total |
    | --- | --- |
    | <region> | <total> |          (one row per region, in summary order)
    """
    raise NotImplementedError


def run_report(csv_text, strict: bool = False) -> str:
    """End-to-end: parse -> summarise -> render. One lazy pass."""
    raise NotImplementedError
