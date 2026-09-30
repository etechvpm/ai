"""Module 09 - reference solutions."""

from __future__ import annotations

import bisect

ABSOLUTE_ZERO = -273.15


# ------------------------------------------------------------------ tier: B
class TemperatureError(ValueError):
    pass


class Temperature:
    def __init__(self, celsius: float = 0.0):
        self.celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float):
        value = float(value)
        if value < ABSOLUTE_ZERO:
            raise TemperatureError(
                f"below absolute zero: {value}")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value: float):
        self.celsius = (float(value) - 32) * 5 / 9

    def __repr__(self):
        return f"Temperature({self._celsius!r})"


class EmptyStack(Exception):
    pass


class Stack:
    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if not self._items:
            raise EmptyStack("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise EmptyStack("peek at empty stack")
        return self._items[-1]

    def __len__(self):
        return len(self._items)

    def __bool__(self):
        return bool(self._items)


# -------------------------------------------------------------- tier: I
class Overdrawn(Exception):
    pass


class BankAccount:
    def __init__(self, owner: str, number: str, balance: float = 0.0):
        self.owner = owner
        self.number = number
        self.balance = float(balance)
        self._history = []

    @property
    def history(self):
        return tuple(self._history)

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount
        self._history.append(("deposit", amount))

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self.balance:
            raise Overdrawn(
                f"cannot withdraw {amount} from {self.balance}")
        self.balance -= amount
        self._history.append(("withdraw", amount))

    @classmethod
    def from_dict(cls, data: dict) -> "BankAccount":
        return cls(data["owner"], data["number"], data.get("balance", 0.0))

    def __repr__(self):
        return (f"BankAccount({self.owner!r}, {self.number!r}, "
                f"{self.balance!r})")

    def __eq__(self, other):
        if not isinstance(other, BankAccount):
            return NotImplemented
        return self.number == other.number

    def __hash__(self):
        return hash(self.number)


class SortedCollection:
    def __init__(self, items=()):
        self._items = sorted(items)

    def add(self, item):
        bisect.insort(self._items, item)

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __contains__(self, item):
        i = bisect.bisect_left(self._items, item)
        return i < len(self._items) and self._items[i] == item

    def __getitem__(self, index):
        return self._items[index]

    def __repr__(self):
        return f"SortedCollection({self._items!r})"


# -------------------------------------------------------------- tier: Ind
class Plugin:
    _registry: dict = {}

    def __init_subclass__(cls, *, name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        key = name or cls.__name__
        if key in Plugin._registry:
            raise ValueError(f"duplicate plugin name: {key!r}")
        Plugin._registry[key] = cls

    @classmethod
    def get(cls, name: str):
        try:
            return cls._registry[name]
        except KeyError:
            raise KeyError(f"unknown plugin: {name!r}") from None

    @classmethod
    def registry(cls):
        return dict(cls._registry)

    def run(self):
        raise NotImplementedError


class Validated:
    def __init__(self, type_, predicate=None, message="invalid value"):
        self.type_ = type_
        self.predicate = predicate
        self.message = message

    def __set_name__(self, owner, name):
        self.public = name
        self.storage = f"_{owner.__name__}_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.storage, None)

    def __set__(self, obj, value):
        # type first: a predicate may assume the type and must not see garbage
        if not isinstance(value, self.type_):
            raise ValueError(
                f"{self.public}: expected {self.type_.__name__}, "
                f"{self.message} (got {value!r})")
        if self.predicate is not None and not self.predicate(value):
            raise ValueError(
                f"{self.public}: {self.message} (got {value!r})")
        setattr(obj, self.storage, value)


class EventBus:
    def __init__(self):
        self._handlers: dict = {}
        self.errors: list = []

    def subscribe(self, event, handler):
        self._handlers.setdefault(event, []).append(handler)

    def unsubscribe(self, event, handler):
        handlers = self._handlers.get(event, [])
        if handler in handlers:
            handlers.remove(handler)

    def emit(self, event, payload=None):
        results = []
        for handler in list(self._handlers.get(event, [])):
            try:
                results.append(handler(payload))
            except Exception as exc:        # noqa: BLE001 - isolated by design
                self.errors.append((handler, exc))
        return results
