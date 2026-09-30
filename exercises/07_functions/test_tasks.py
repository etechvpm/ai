"""Grader for module 07.  Run:  pytest exercises/07_functions -q"""

from __future__ import annotations

import pytest

from _loader import load

tasks = load(__file__)


# ------------------------------------------------------------- beginner
def test_repeat():
    assert tasks.repeat(lambda x: x * 2, 3, 1) == 8
    assert tasks.repeat(lambda x: x + 1, 0, 5) == 5
    assert tasks.repeat(str.upper, 1, "ab") == "AB"


def test_compose():
    inc = lambda x: x + 1          # noqa: E731 - test-local helper
    dbl = lambda x: x * 2          # noqa: E731
    assert tasks.compose(inc, dbl)(3) == 7      # inc(dbl(3))
    assert tasks.compose(dbl, inc)(3) == 8


def test_apply_all():
    assert tasks.apply_all([abs, lambda x: x * 2], -3) == 6
    assert tasks.apply_all([], 9) == 9


# --------------------------------------------------------- intermediate
def test_retry_succeeds_after_failures():
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("boom")
        return "ok"

    assert tasks.retry(flaky, 3) == "ok"
    assert calls["n"] == 3


def test_retry_exhausted_reraises_last():
    def always():
        raise KeyError("last-error")

    with pytest.raises(KeyError, match="last-error"):
        tasks.retry(always, 2)


def test_retry_respects_exception_filter():
    calls = {"n": 0}

    def wrong_kind():
        calls["n"] += 1
        raise TypeError("not retryable")

    with pytest.raises(TypeError):
        tasks.retry(wrong_kind, 5, exceptions=(ValueError,))
    assert calls["n"] == 1, "must not retry exceptions outside the filter"


def test_retry_validates_attempts():
    with pytest.raises(ValueError):
        tasks.retry(lambda: 1, 0)


def test_memoize_caches_and_counts():
    calls = {"n": 0}

    def slow(x, *, factor=1):
        calls["n"] += 1
        return x * factor

    m = tasks.memoize(slow)
    assert m(2, factor=3) == 6
    assert m(2, factor=3) == 6
    assert calls["n"] == 1
    assert m(2, factor=4) == 8
    assert calls["n"] == 2
    assert m.hits == 1 and m.misses == 2
    assert m.__name__ == "slow", "functools.wraps must preserve the name"
    assert len(m.cache) == 2


def test_pipeline():
    p = tasks.pipeline(lambda x: x + 1, lambda x: x * 10, str)
    assert p(4) == "50"
    assert tasks.pipeline()(7) == 7


# ------------------------------------------------------------ industry
def test_backoff_schedule_is_injected():
    delays = []
    calls = {"n": 0}

    def failing():
        calls["n"] += 1
        raise RuntimeError("down")

    with pytest.raises(RuntimeError):
        tasks.retry_with_backoff(failing, attempts=4, base_delay=0.5,
                                 sleep=delays.append)
    assert delays == [0.5, 1.0, 2.0], "no sleep after the final attempt"
    assert calls["n"] == 4


def test_backoff_success_skips_sleep():
    delays = []
    assert tasks.retry_with_backoff(lambda: "up", attempts=3,
                                    sleep=delays.append) == "up"
    assert delays == []


def test_registry_and_dispatch():
    tasks.REGISTRY.clear()

    @tasks.register("add")
    def add(a, b):
        return a + b

    assert tasks.REGISTRY["add"] is add, "register must return fn unchanged"
    assert tasks.dispatch("add", 2, 3) == 5
    with pytest.raises(KeyError):
        tasks.dispatch("nope")

    with pytest.raises(ValueError):
        @tasks.register("add")
        def add2(a, b):
            return a + b


def test_type_dispatcher_mro():
    d = tasks.TypeDispatcher()

    @d.register(int)
    def _(value):
        return f"int:{value}"

    @d.register(list)
    def _(value):
        return f"list:{len(value)}"

    class MyInt(int):
        pass

    assert d(3) == "int:3"
    assert d([1, 2]) == "list:2"
    assert d(MyInt(7)) == "int:7", "must walk the MRO to a base handler"
    with pytest.raises(TypeError):
        d("unhandled")
