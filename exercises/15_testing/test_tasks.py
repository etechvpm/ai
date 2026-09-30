"""Grader for module 15.  Run:  pytest exercises/15_testing -q"""

from __future__ import annotations

import types

import pytest

from _loader import load

tasks = load(__file__)


def make_module(**funcs):
    return types.SimpleNamespace(**funcs)


# ------------------------------------------------------------- beginner
def test_approx():
    assert tasks.approx(0.1 + 0.2, 0.3)
    assert tasks.approx(1_000_000.0, 1_000_000.0000001)
    assert not tasks.approx(1.0, 2.0)
    assert tasks.approx(0, 0)
    assert not tasks.approx(0.0, 1e-6, rel=1e-9, abs_tol=1e-12)


def test_raises_context_manager():
    with tasks.raises(ValueError) as ei:
        int("nope")
    assert isinstance(ei.value, ValueError)
    with pytest.raises(AssertionError):
        with tasks.raises(ValueError):
            pass
    with pytest.raises(KeyError):
        with tasks.raises(ValueError):
            raise KeyError("other type propagates")


def test_collect_order_and_filtering():
    def test_b(): pass
    def helper(): pass
    def test_a(): pass
    mod = make_module(test_b=test_b, helper=helper, test_a=test_a,
                      value=3)
    assert tasks.collect(mod) == [test_b, test_a]


# --------------------------------------------------------- intermediate
def test_spy_records_and_returns():
    spy = tasks.Spy(result=42)
    assert spy(1, k=2) == 42
    assert spy.calls == [((1,), {"k": 2})]
    assert spy.call_count == 1
    assert spy.called_with(1, k=2) and not spy.called_with(2)


def test_spy_side_effect_and_exhaustion():
    spy = tasks.Spy(side_effect=[1, ValueError("boom"), 3])
    assert spy() == 1
    with pytest.raises(ValueError):
        spy()
    assert spy() == 3
    with pytest.raises(tasks.ExhaustedSideEffect):
        spy()
    with pytest.raises(ValueError):
        tasks.Spy(result=1, side_effect=[2])


def test_run_reports_passed_failed_skipped():
    def test_ok(): assert True
    def test_bad(): raise RuntimeError("x")
    def test_skip(): raise tasks.SkipTest("later")
    mod = make_module(test_ok=test_ok, test_bad=test_bad,
                      test_skip=test_skip)
    report = tasks.run(mod)
    assert report["passed"] == ["test_ok"]
    assert report["skipped"] == ["test_skip"]
    assert set(report["failed"]) == {"test_bad"}
    assert isinstance(report["failed"]["test_bad"], RuntimeError)


# ------------------------------------------------------------ industry
def setup_module():
    tasks.FIXTURES.clear()


def test_fixtures_with_dependencies_and_teardown():
    tasks.FIXTURES.clear()
    events = []

    @tasks.fixture
    def base():
        events.append("base-setup")
        yield "B"
        events.append("base-teardown")

    @tasks.fixture
    def derived(base):
        events.append("derived-setup")
        return base + "D"

    def test_uses(derived):
        assert derived == "BD"
        events.append("test")

    mod = make_module(test_uses=test_uses)
    report = tasks.run_full(mod)
    assert report["passed"] == ["test_uses"], report
    assert events == ["base-setup", "derived-setup", "test",
                      "base-teardown"], "teardown must run after the test"


def test_teardown_runs_even_on_failure():
    tasks.FIXTURES.clear()
    events = []

    @tasks.fixture
    def res():
        events.append("setup")
        yield 1
        events.append("teardown")

    def test_fails(res):
        raise AssertionError("boom")

    report = tasks.run_full(make_module(test_fails=test_fails))
    assert set(report["failed"]) == {"test_fails"}
    assert events == ["setup", "teardown"]


def test_parametrize_expands_cases():
    tasks.FIXTURES.clear()

    @tasks.parametrize("value,expected", [(1, 1), (2, 4), (3, 99)])
    def test_square(value, expected):
        assert value * value == expected or value == 3 and expected == 99

    report = tasks.run_full(make_module(test_square=test_square))
    assert report["passed"] == ["test_square[case0]", "test_square[case1]",
                                "test_square[case2]"], report


def test_unknown_fixture_is_reported_not_fatal():
    tasks.FIXTURES.clear()

    def test_needs(ghost):
        pass

    report = tasks.run_full(make_module(test_needs=test_needs))
    assert set(report["errors"]) == {"test_needs"}
    assert isinstance(report["errors"]["test_needs"], tasks.FixtureError)
    assert report["passed"] == [] and report["failed"] == {}


def test_fixture_decorator_registers():
    tasks.FIXTURES.clear()

    @tasks.fixture
    def thing():
        return 1

    assert tasks.FIXTURES["thing"] is thing
