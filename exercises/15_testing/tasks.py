"""Module 15 - Testing.  Student task sheet: build a miniature pytest."""

from __future__ import annotations


# ------------------------------------------------------------------ tier: B
def approx(a, b, rel: float = 1e-9, abs_tol: float = 1e-12) -> bool:
    """True when a and b are equal within rel/abs tolerance (like
    pytest.approx semantics: |a-b| <= max(abs_tol, rel * max(|a|, |b|)))."""
    raise NotImplementedError


class SkipTest(Exception):
    pass


class raises:
    """Context manager: assert the block raises exc_type.

    Exposes .value afterwards; if nothing raises -> AssertionError.
    If a DIFFERENT exception type raises, let it propagate.
    """

    def __init__(self, exc_type):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc, tb):
        raise NotImplementedError


def collect(module) -> list:
    """The callables in *module* whose names start with 'test_', in
    definition order (use the module's __dict__ order)."""
    raise NotImplementedError


# -------------------------------------------------------------- tier: I
class ExhaustedSideEffect(Exception):
    pass


class Spy:
    """Callable test double.

    Spy(result=None) or Spy(side_effect=[...]).
    .calls -> list of (args, kwargs); .call_count; .called_with(*a, **kw)
    bool. side_effect items that are exceptions are RAISED; when the list is
    exhausted raise ExhaustedSideEffect. result and side_effect together ->
    ValueError at construction.
    """

    def __init__(self, result=None, side_effect=None):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


def run(module) -> dict:
    """Execute collect(module); each test takes no arguments.

    Returns {"passed": [names], "failed": {name: exception},
             "skipped": [names]}
    A test raising SkipTest is skipped; any other exception is a failure.
    """
    raise NotImplementedError


# -------------------------------------------------------------- tier: Ind
class FixtureError(Exception):
    pass


FIXTURES: dict = {}


def fixture(fn):
    """Register fn in FIXTURES under fn.__name__; return fn."""
    raise NotImplementedError


def parametrize(argnames: str, cases):
    """Decorator storing expansion metadata on the test function
    (attribute .parametrize = (argnames, list(cases))) for run() to use."""
    raise NotImplementedError


def run_full(module) -> dict:
    """Like run() but:
      * tests may declare fixture parameters (by name); fixtures come from
        FIXTURES, may themselves request fixtures, and generator fixtures get
        their teardown executed (after yield) once the test finishes - even
        on failure;
      * tests decorated with parametrize expand to one entry per case named
        'test_name[case0]', 'test_name[case1]', ... (str(case) if no ids);
      * unknown fixture -> FixtureError recorded in report["errors"] for that
        test (not a crash of the whole run).
    Returns {"passed": [...], "failed": {...}, "skipped": [...],
             "errors": {...}}.
    """
    raise NotImplementedError
