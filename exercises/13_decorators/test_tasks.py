"""Grader for module 13.  Run:  pytest exercises/13_decorators -q"""

from __future__ import annotations

import pytest

from _loader import load

tasks = load(__file__)


# ------------------------------------------------------------- beginner
def test_logged_records_call_and_return():
    @tasks.logged
    def add(a, b=0):
        return a + b

    assert add(1, b=2) == 3
    assert add.records == [
        ("call", "add", (1,), {"b": 2}),
        ("return", "add", 3),
    ]
    assert add.__name__ == "add", "functools.wraps required"


def test_double_and_count():
    @tasks.double_result
    def six():
        return 3

    assert six() == 6

    @tasks.count_calls
    def ping():
        return "pong"

    ping(); ping(); ping()
    assert ping.calls == 3
    assert ping.__name__ == "ping"


# --------------------------------------------------------- intermediate
def test_timed_uses_injected_clock():
    ticks = iter([100.0, 102.5])

    @tasks.timed(clock=lambda: next(ticks))
    def slow():
        return "done"

    assert slow.elapsed == 0.0
    assert slow() == "done"
    assert slow.elapsed == pytest.approx(2.5)


def test_retry_dec_attempts_and_validation():
    calls = {"n": 0}

    @tasks.retry_dec(3, exceptions=(ValueError,))
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("x")
        return "ok"

    assert flaky() == "ok" and calls["n"] == 3

    with pytest.raises(ValueError):
        @tasks.retry_dec(0)
        def never():
            pass


def test_retry_dec_does_not_retry_other_exceptions():
    calls = {"n": 0}

    @tasks.retry_dec(5, exceptions=(KeyError,))
    def boom():
        calls["n"] += 1
        raise TypeError("nope")

    with pytest.raises(TypeError):
        boom()
    assert calls["n"] == 1


def test_ttl_cache_expiry():
    now = {"t": 0.0}

    def clock():
        return now["t"]

    calls = {"n": 0}

    @tasks.ttl_cache(10.0, clock=clock)
    def expensive(x):
        calls["n"] += 1
        return x * 2

    assert expensive(2) == 4
    assert expensive(2) == 4
    assert calls["n"] == 1
    now["t"] = 9.9
    assert expensive(2) == 4 and calls["n"] == 1
    now["t"] = 10.0
    assert expensive(2) == 4 and calls["n"] == 2, "expired -> recompute"
    expensive.cache_clear()
    expensive(2)
    assert calls["n"] == 3


# ------------------------------------------------------------ industry
def test_routes_and_dispatch():
    tasks.ROUTES.clear()

    @tasks.route("get", "/users")
    def list_users(limit=10):
        return ["users", limit]

    assert tasks.dispatch("GET", "/users") == ["users", 10]
    assert tasks.dispatch("get", "/users", limit=2) == ["users", 2]
    with pytest.raises(KeyError):
        tasks.dispatch("POST", "/users")
    with pytest.raises(ValueError):
        @tasks.route("GET", "/users")
        def dup():
            pass


def test_validate_types_at_call_time():
    @tasks.validate(age=int, name=str)
    def profile(name, age):
        return f"{name}:{age}"

    assert profile("ada", 36) == "ada:36"
    assert profile(name="ada", age=36) == "ada:36"
    with pytest.raises(TypeError, match="age"):
        profile("ada", "thirty-six")
    with pytest.raises(TypeError, match="name"):
        profile(1, 2)
    assert profile.__name__ == "profile"


def test_singleton_identity_and_isinstance():
    @tasks.singleton
    class Config:
        def __init__(self, value=1):
            self.value = value

    a = Config(1)
    b = Config(2)
    assert a is b, "singleton must return the same instance"
    assert b.value == 1, "later constructor args are ignored"
    assert isinstance(a, Config.__wrapped_class__)
    assert Config.__name__ == "Config"
