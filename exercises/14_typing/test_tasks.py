"""Grader for module 14.  Run:  pytest exercises/14_typing -q"""

from __future__ import annotations

import typing

import pytest

from _loader import load

tasks = load(__file__)


def hints(obj):
    return typing.get_type_hints(obj)


# ------------------------------------------------------------- beginner
def test_normalize_annotation_and_behaviour():
    h = hints(tasks.normalize)
    assert h["return"] == list[str]
    param = h["texts"]
    assert getattr(param, "__origin__", None) in (
        list, typing.Sequence) or "Sequence" in str(param) or param == list[str]
    assert tasks.normalize([" A ", "b", "  "]) == ["a", "b"]


def test_stats_annotation_and_behaviour():
    h = hints(tasks.stats)
    assert h["return"] == dict[str, float]
    out = tasks.stats([1, 2, 3])
    assert out == {"count": 3.0, "total": 6.0, "mean": 2.0}
    assert tasks.stats([]) ["mean"] == 0.0


def test_lookup_annotation_and_behaviour():
    h = hints(tasks.lookup)
    assert "mapping" in h and "key" in h and "return" in h
    assert tasks.lookup({"a": 1}, "a") == 1
    assert tasks.lookup({"a": 1}, "z") is None
    assert tasks.lookup({"a": 1}, "z", 9) == 9


# --------------------------------------------------------- intermediate
def test_first_generic_annotation():
    h = hints(tasks.first)
    ret = str(h["return"])
    assert "None" in ret or "Optional" in ret, f"return must be optional: {ret}"
    assert tasks.first([3, 4]) == 3
    assert tasks.first([]) is None


def test_pairwise():
    assert list(tasks.pairwise([1, 2, 3, 4])) == [(1, 2), (2, 3), (3, 4)]
    assert list(tasks.pairwise([])) == []
    assert list(tasks.pairwise(iter("ab"))) == [("a", "b")]


def test_renderable_protocol_is_runtime_checkable():
    class Good:
        def render(self) -> str:
            return "good"

    class Bad:
        pass

    assert isinstance(Good(), tasks.Renderable)
    assert not isinstance(Bad(), tasks.Renderable)
    assert tasks.render_all([Good(), Good()]) == ["good", "good"]


def test_typeddict_and_validation():
    assert set(tasks.UserPayload.__annotations__) == {"id", "name", "tags"}
    ok = tasks.validate_payload({"id": 1, "name": "ada", "tags": ["x"]})
    assert ok == {"id": 1, "name": "ada", "tags": ["x"]}
    for bad, field in [({"id": "1", "name": "a", "tags": []}, "id"),
                       ({"id": 1, "name": 2, "tags": []}, "name"),
                       ({"id": 1, "name": "a", "tags": "x"}, "tags"),
                       ({"id": 1, "name": "a"}, "tags")]:
        with pytest.raises(ValueError, match=field):
            tasks.validate_payload(bad)


# ------------------------------------------------------------ industry
def test_result_types():
    ok = tasks.Ok(5)
    err = tasks.Err("boom")
    assert ok.is_ok() and not err.is_ok()
    assert ok.unwrap() == 5
    assert ok.map(lambda v: v * 2).unwrap() == 10
    assert err.map(lambda v: v * 2) is err
    with pytest.raises(ValueError):
        err.unwrap()
    assert ok.tag == "ok" and err.tag == "err"


def test_result_generic_annotations():
    h = hints(tasks.Ok.__init__)
    assert "value" in h
    assert str(hints(tasks.Ok.unwrap)["return"]) not in ("", "None")


def test_repository_protocol_and_implementation():
    repo = tasks.InMemoryRepository()
    uid = tasks.EntityId(7)
    repo.save(uid, {"name": "ada"})
    assert repo.get(uid) == {"name": "ada"}
    assert repo.list_all() == [{"name": "ada"}]
    with pytest.raises(KeyError) as ei:
        repo.get(tasks.EntityId(99))
    assert ei.value.args[0] == 99
    assert isinstance(repo, tasks.Repository) or hasattr(
        tasks.Repository, "get"), "Repository must be a Protocol-like interface"


def test_entity_id_is_distinct_type():
    raw = tasks.EntityId(3)
    assert raw == 3, "NewType is transparent at runtime"
    assert tasks.EntityId is not int, "must be a NewType, not plain int"
