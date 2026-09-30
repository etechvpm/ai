"""Grader for module 09.  Run:  pytest exercises/09_oop -q"""

from __future__ import annotations

import pytest

from _loader import load

tasks = load(__file__)


# ------------------------------------------------------------- beginner
@pytest.mark.parametrize("c,f", [(0, 32), (100, 212), (-40, -40), (37, 98.6)])
def test_temperature_conversions(c, f):
    t = tasks.Temperature(c)
    assert t.fahrenheit == pytest.approx(f)
    t.fahrenheit = f
    assert t.celsius == pytest.approx(c)


def test_temperature_validation():
    with pytest.raises(tasks.TemperatureError):
        tasks.Temperature(-273.16)
    t = tasks.Temperature(20)
    with pytest.raises(ValueError):       # TemperatureError IS a ValueError
        t.fahrenheit = -460


def test_stack_protocol():
    s = tasks.Stack()
    assert len(s) == 0 and not s
    with pytest.raises(tasks.EmptyStack):
        s.pop()
    s.push(1)
    s.push(2)
    assert bool(s) and len(s) == 2
    assert s.peek() == 2 and len(s) == 2
    assert s.pop() == 2 and s.pop() == 1
    with pytest.raises(tasks.EmptyStack):
        s.peek()


# --------------------------------------------------------- intermediate
def test_bank_account_operations_and_history():
    a = tasks.BankAccount("ada", "A-1", 100)
    a.deposit(50)
    a.withdraw(30)
    assert a.balance == 120
    assert a.history == (("deposit", 50), ("withdraw", 30))
    with pytest.raises(tasks.Overdrawn):
        a.withdraw(1000)
    with pytest.raises(ValueError):
        a.deposit(-1)


def test_bank_account_repr_eq_from_dict():
    a = tasks.BankAccount("ada", "A-1", 150.0)
    assert repr(a) == "BankAccount('ada', 'A-1', 150.0)"
    b = tasks.BankAccount("someone else", "A-1", 0)
    assert a == b, "equality is by account number"
    assert a != tasks.BankAccount("ada", "A-2")
    assert (a == "A-1") is False
    c = tasks.BankAccount.from_dict({"owner": "x", "number": "N", "balance": 5})
    assert (c.owner, c.number, c.balance) == ("x", "N", 5)
    d = tasks.BankAccount.from_dict({"owner": "x", "number": "N"})
    assert d.balance == 0


def test_sorted_collection_protocol():
    sc = tasks.SortedCollection([5, 1, 3])
    assert len(sc) == 3
    assert list(sc) == [1, 3, 5]
    assert 3 in sc and 4 not in sc
    sc.add(2)
    assert list(sc) == [1, 2, 3, 5]
    assert sc[0] == 1 and sc[-1] == 5
    assert sc[1:3] == [2, 3], "slices must work"
    assert list(tasks.SortedCollection()) == []


# ------------------------------------------------------------ industry
def test_plugin_registration_and_lookup():
    tasks.Plugin._registry.clear()

    class Alpha(tasks.Plugin, name="alpha"):
        def run(self):
            return "A"

    class Beta(tasks.Plugin):
        def run(self):
            return "B"

    assert tasks.Plugin.get("alpha") is Alpha
    assert tasks.Plugin.get("Beta") is Beta
    assert Alpha().run() == "A"
    with pytest.raises(KeyError):
        tasks.Plugin.get("nope")

    with pytest.raises(ValueError):
        class Duplicate(tasks.Plugin, name="alpha"):
            def run(self):
                return "dup"


def test_plugin_base_run_is_abstract():
    tasks.Plugin._registry.clear()
    with pytest.raises(NotImplementedError):
        tasks.Plugin().run()


def test_validated_descriptor():
    class User:
        name = tasks.Validated(str, lambda v: len(v) >= 2,
                               message="too short")
        age = tasks.Validated(int, lambda v: 0 <= v < 150,
                              message="implausible age")

    u = User()
    u.name = "ada"
    u.age = 36
    assert u.name == "ada" and u.age == 36
    assert User.name.__class__ is tasks.Validated, "class access -> descriptor"

    with pytest.raises(ValueError, match="name"):
        u.name = "a"
    with pytest.raises(ValueError, match="age"):
        u.age = "thirty"
    with pytest.raises(ValueError):
        u.age = 900
    assert u.name == "ada", "failed assignment must not mutate"


def test_event_bus_isolates_failures_and_keeps_order():
    bus = tasks.EventBus()
    calls = []

    def ok(payload):
        calls.append("ok")
        return payload * 2

    class CallableHandler:
        def __call__(self, payload):
            calls.append("obj")
            return payload + 1

    def bad(payload):
        raise RuntimeError("handler exploded")

    bus.subscribe("evt", ok)
    bus.subscribe("evt", bad)
    bus.subscribe("evt", CallableHandler())
    results = bus.emit("evt", 5)
    assert results == [10, 6], "good handlers still report results"
    assert calls == ["ok", "obj"]
    assert len(bus.errors) == 1
    handler, exc = bus.errors[0]
    assert handler is bad and isinstance(exc, RuntimeError)
    assert bus.emit("unknown", 1) == []


def test_event_bus_unsubscribe():
    bus = tasks.EventBus()
    seen = []

    def record(payload):
        seen.append(payload)

    bus.subscribe("e", record)
    bus.emit("e", 1)
    bus.unsubscribe("e", record)
    bus.emit("e", 2)
    assert seen == [1], "unsubscribe must stop further deliveries"
