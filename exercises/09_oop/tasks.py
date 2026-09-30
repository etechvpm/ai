"""Module 09 - Object-oriented Python.  Student task sheet."""

from __future__ import annotations


# ------------------------------------------------------------------ tier: B
class TemperatureError(ValueError):
    pass


class Temperature:
    """Stores Celsius internally.

    .celsius and .fahrenheit are readable AND settable properties.
    Setting either converts appropriately. Values below -273.15 C raise
    TemperatureError (a ValueError subclass).
    """

    def __init__(self, celsius: float = 0.0):
        raise NotImplementedError

    # add the properties here


class EmptyStack(Exception):
    pass


class Stack:
    """push(item), pop() -> item, peek() -> item without removing,
    __len__, and `bool(stack)` True when non-empty. pop/peek on empty raise
    EmptyStack."""

    def __init__(self):
        raise NotImplementedError


# -------------------------------------------------------------- tier: I
class Overdrawn(Exception):
    pass


class BankAccount:
    """owner, number, balance.

    deposit(amount>0) / withdraw(amount>0) raising Overdrawn when the balance
    would go negative. .history is a tuple of ("deposit"|"withdraw", amount).
    __repr__ -> BankAccount('ada', 'A-1', 150.0)
    __eq__ compares by account number only.
    from_dict({"owner":…, "number":…, "balance":…}) classmethod.
    """

    def __init__(self, owner: str, number: str, balance: float = 0.0):
        raise NotImplementedError


class SortedCollection:
    """Holds items always sorted.

    add(item), __len__, __iter__ (sorted), __contains__, __getitem__
    supporting ints AND slices. Initial items via constructor argument.
    """

    def __init__(self, items=()):
        raise NotImplementedError


# -------------------------------------------------------------- tier: Ind
class Plugin:
    """Base class whose subclasses auto-register.

    class MyPlugin(Plugin, name="mine"): ...  registers under "mine"
    class Other(Plugin): ...                  registers under "Other"
    Duplicate names raise ValueError at class-creation time.
    Plugin.get(name) -> the class (KeyError when unknown).
    Plugin.registry -> mapping view. Subclasses must implement run(self).
    """

    _registry: dict = {}

    def run(self):
        raise NotImplementedError


class Validated:
    """Descriptor validating every assignment.

    Validated(type_, predicate=None, message="invalid value")
    Assignment of a wrong type or failing predicate raises ValueError whose
    message contains the field name. Reading returns the stored value.
    Access on the class returns the descriptor itself.
    """

    def __init__(self, type_, predicate=None, message="invalid value"):
        raise NotImplementedError


class EventBus:
    """subscribe(event, handler) / unsubscribe(event, handler) /
    emit(event, payload) -> list of results in subscription order.

    Handlers are any callable. An exception in one handler is collected into
    the returned... no: exceptions are stored on bus.errors as
    (handler, exception) and do NOT stop later handlers; successful results
    are still returned. Emitting an unknown event returns [].
    """

    def __init__(self):
        raise NotImplementedError
