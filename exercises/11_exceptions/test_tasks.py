"""Grader for module 11.  Run:  pytest exercises/11_exceptions -q"""

from __future__ import annotations

import pytest

from _loader import load

tasks = load(__file__)


# ------------------------------------------------------------- beginner
def test_safe_int():
    assert tasks.safe_int("42") == 42
    assert tasks.safe_int("nope") is None
    assert tasks.safe_int("nope", -1) == -1
    assert tasks.safe_int(None, 0) == 0
    assert tasks.safe_int(3.9) == 3


def test_divide():
    assert tasks.divide(10, 4) == 2.5
    with pytest.raises(tasks.DivisionError):
        tasks.divide(1, 0)
    with pytest.raises(TypeError):
        tasks.divide("1", 2)
    assert issubclass(tasks.DivisionError, ZeroDivisionError)


def test_first_existing(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    b.write_text("x", encoding="utf-8")
    assert tasks.first_existing([a, b]) == b
    with pytest.raises(FileNotFoundError) as ei:
        tasks.first_existing([a, tmp_path / "c.txt"])
    assert "a.txt" in str(ei.value) and "c.txt" in str(ei.value)


# --------------------------------------------------------- intermediate
def test_parse_config_ok():
    text = "# comment\n\nhost = localhost\nport=5432\n"
    assert tasks.parse_config(text) == {"host": "localhost", "port": "5432"}
    assert tasks.parse_config("") == {}


def test_parse_config_errors_carry_line_numbers():
    with pytest.raises(tasks.ConfigError) as ei:
        tasks.parse_config("ok=1\nbroken\n")
    assert ei.value.line_number == 2
    with pytest.raises(tasks.ConfigError) as ei2:
        tasks.parse_config("a=1\na=2\n")
    assert ei2.value.line_number == 2 and "duplicate" in ei2.value.reason
    assert issubclass(tasks.ConfigError, ValueError)


def test_retry_on_decorator():
    calls = {"n": 0}

    @tasks.retry_on((ValueError,), 3)
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("x")
        return "done"

    assert flaky() == "done" and calls["n"] == 3

    @tasks.retry_on((KeyError,), 2)
    def wrong():
        raise TypeError("not retried")

    with pytest.raises(TypeError):
        wrong()


def test_guarded_get_chains_cause():
    def to_int(v):
        return int(v)

    assert tasks.guarded_get({"n": "7"}, "n", to_int) == 7
    with pytest.raises(tasks.TransformError) as ei:
        tasks.guarded_get({"n": "x"}, "n", to_int)
    assert ei.value.__cause__ is not None, "must chain with `from`"
    assert isinstance(ei.value.__cause__, ValueError)
    assert ei.value.key == "n"
    with pytest.raises(KeyError):
        tasks.guarded_get({}, "n", to_int)


# ------------------------------------------------------------ industry
def test_error_mapper_most_specific_wins():
    mapper = tasks.ErrorMapper()
    mapper.map(ValueError, lambda e: "value-handled")
    mapper.map(KeyError, lambda e: "key-handled")

    def raise_key():
        raise KeyError("k")

    def raise_value():
        raise ValueError("v")

    def raise_other():
        raise RuntimeError("r")

    assert mapper.run(raise_key) == "key-handled"
    assert mapper.run(raise_value) == "value-handled"
    with pytest.raises(RuntimeError):
        mapper.run(raise_other)
    assert mapper.run(lambda: 5) == 5


def test_error_mapper_walks_mro_for_unregistered_subclass():
    mapper = tasks.ErrorMapper()
    mapper.map(OSError, lambda e: "os-handled")

    def raise_sub():
        raise FileNotFoundError("gone")

    assert mapper.run(raise_sub) == "os-handled"


def test_suppressed_records_and_limits():
    seen = []
    with tasks.suppressed(ValueError, KeyError, on_suppressed=seen.append) as s:
        raise ValueError("gone")
    assert s.suppressed == [(ValueError, "gone")]
    assert len(seen) == 1

    with pytest.raises(RuntimeError):
        with tasks.suppressed(ValueError):
            raise RuntimeError("must propagate")

    with tasks.suppressed(ValueError) as s2:
        pass
    assert s2.suppressed == []
