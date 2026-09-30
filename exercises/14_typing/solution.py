"""Module 14 - reference solutions."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, Sequence
from typing import (Generic, NewType, NoReturn, Protocol, TypedDict,
                    TypeVar, runtime_checkable)

T = TypeVar("T")
E = TypeVar("E")
K = TypeVar("K")
V = TypeVar("V")
EntityT = TypeVar("EntityT")

EntityId = NewType("EntityId", int)


# ------------------------------------------------------------------ tier: B
def normalize(texts: Sequence[str]) -> list[str]:
    return [t.strip().lower() for t in texts if t.strip()]


def stats(numbers: Sequence[float]) -> dict[str, float]:
    total = float(sum(numbers))
    return {"count": float(len(numbers)), "total": total,
            "mean": total / len(numbers) if numbers else 0.0}


def lookup(mapping: Mapping[K, V], key: K, default: V | None = None) -> V | None:
    return mapping.get(key, default)


# -------------------------------------------------------------- tier: I
def first(seq: Sequence[T]) -> T | None:
    return seq[0] if seq else None


def pairwise(it: Iterable[T]) -> Iterator[tuple[T, T]]:
    iterator = iter(it)
    sentinel = object()
    prev = next(iterator, sentinel)
    if prev is sentinel:
        return
    for current in iterator:
        yield prev, current      # type: ignore[misc]
        prev = current


@runtime_checkable
class Renderable(Protocol):
    def render(self) -> str: ...


def render_all(docs: Iterable[Renderable]) -> list[str]:
    return [doc.render() for doc in docs]


class UserPayload(TypedDict):
    id: int
    name: str
    tags: list[str]


def validate_payload(data: object) -> UserPayload:
    if not isinstance(data, dict):
        raise ValueError("payload must be an object")
    if not isinstance(data.get("id"), int):
        raise ValueError("id: expected int")
    if not isinstance(data.get("name"), str):
        raise ValueError("name: expected str")
    tags = data.get("tags")
    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        raise ValueError("tags: expected list[str]")
    return UserPayload(id=data["id"], name=data["name"], tags=list(tags))


# -------------------------------------------------------------- tier: Ind
class Ok(Generic[T]):
    tag: str = "ok"

    def __init__(self, value: T) -> None:
        self.value = value

    def is_ok(self) -> bool:
        return True

    def unwrap(self) -> T:
        return self.value

    def map(self, fn) -> "Ok":
        return Ok(fn(self.value))

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"


class Err(Generic[E]):
    tag: str = "err"

    def __init__(self, error: E) -> None:
        self.error = error

    def is_ok(self) -> bool:
        return False

    def unwrap(self) -> NoReturn:
        raise ValueError(f"unwrap of Err: {self.error!r}")

    def map(self, fn) -> "Err":
        return self

    def __repr__(self) -> str:
        return f"Err({self.error!r})"


@runtime_checkable
class Repository(Protocol[EntityT]):
    def save(self, entity_id: EntityId, entity: EntityT) -> None: ...
    def get(self, entity_id: EntityId) -> EntityT: ...
    def list_all(self) -> list[EntityT]: ...


class InMemoryRepository(Generic[EntityT]):
    def __init__(self) -> None:
        self._store: dict[EntityId, EntityT] = {}

    def save(self, entity_id: EntityId, entity: EntityT) -> None:
        self._store[entity_id] = entity

    def get(self, entity_id: EntityId) -> EntityT:
        try:
            return self._store[entity_id]
        except KeyError:
            raise KeyError(entity_id) from None

    def list_all(self) -> list[EntityT]:
        return list(self._store.values())
