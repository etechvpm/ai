"""Module 14 - Type hints.  Student task sheet.

The tests inspect your ANNOTATIONS with typing.get_type_hints as well as the
runtime behaviour, so signatures must match the specification exactly.
"""

from __future__ import annotations


# ------------------------------------------------------------------ tier: B
def normalize(texts):
    """list[str] -> list[str]: stripped, lower-cased, blanks dropped.

    Annotate: (texts: Sequence[str]) -> list[str]
    """
    raise NotImplementedError


def stats(numbers):
    """Sequence of ints/floats -> dict with 'count', 'total', 'mean'.

    Annotate: (numbers: Sequence[float]) -> dict[str, float]
    """
    raise NotImplementedError


def lookup(mapping, key, default=None):
    """Mapping[K, V] get with default.

    Annotate: (mapping: Mapping[K, V], key: K, default: V | None = None)
    -> V | None   (module-level TypeVar K, V)
    """
    raise NotImplementedError


# -------------------------------------------------------------- tier: I
# from typing/collections.abc as needed: TypeVar, Generic, Protocol,
# runtime_checkable, TypedDict, Iterator, Sequence, Iterable, Literal, NoReturn

def first(seq):
    """First item or None.  Annotate (seq: Sequence[T]) -> T | None."""
    raise NotImplementedError


def pairwise(it):
    """Yield (a, b), (b, c), ...  Annotate
    (it: Iterable[T]) -> Iterator[tuple[T, T]]."""
    raise NotImplementedError


class Renderable:
    """Replace with a @runtime_checkable Protocol requiring render() -> str."""


def render_all(docs):
    """[doc.render() for doc in docs]; annotate Iterable[Renderable]."""
    raise NotImplementedError


class UserPayload:
    """Replace with a TypedDict: id: int, name: str, tags: list[str]."""


def validate_payload(data):
    """Validate an unknown object into a UserPayload.

    Raises ValueError whose message names the first offending field
    ('id', 'name' or 'tags'). Annotate (data: object) -> UserPayload.
    """
    raise NotImplementedError


# -------------------------------------------------------------- tier: Ind
EntityId = int          # replace with NewType("EntityId", int)


class Ok:
    """Ok(Generic[T]): .value, .is_ok() True, .unwrap() -> value,
    .map(fn) -> Ok(fn(value)), .tag == "ok" (Literal)."""


class Err:
    """Err(Generic[E]): .error, .is_ok() False, .unwrap() raises ValueError,
    .map(fn) returns self, .tag == "err"."""


class Repository:
    """Replace with a Generic Protocol: save(entity_id, entity) -> None,
    get(entity_id) -> T, list_all() -> list[T]."""


class InMemoryRepository:
    """dict-backed Repository[T]; get on missing id raises KeyError whose
    args contain the id."""
