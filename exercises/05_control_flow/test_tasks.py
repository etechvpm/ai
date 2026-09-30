"""Grader for module 05.  Run:  pytest exercises/05_control_flow -q"""

from __future__ import annotations


import pytest

from _loader import load

tasks = load(__file__)


# ------------------------------------------------------------- beginner
def test_fizzbuzz():
    assert tasks.fizzbuzz(5) == ["1", "2", "Fizz", "4", "Buzz"]
    assert tasks.fizzbuzz(15) == [
        "1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz",
        "11", "Fizz", "13", "14", "FizzBuzz"]
    assert tasks.fizzbuzz(0) == []


def test_classify():
    assert tasks.classify([-3, 0, 4, 10, 99]) == [
        "negative", "zero", "small", "large", "large"]


def test_sum_evens():
    assert tasks.sum_evens([[1, 2, 3], [4, 5, 6]]) == 12
    assert tasks.sum_evens([[], [1, 3]]) == 0
    assert tasks.sum_evens([[2]]) == 2


def test_sum_evens_uses_continue():
    import inspect
    assert "continue" in inspect.getsource(tasks.sum_evens), \
        "the exercise requires the continue keyword"


# --------------------------------------------------------- intermediate
def test_first_admin_without_flag_variable():
    users = [{"name": "a"}, {"name": "b", "admin": True},
             {"name": "c", "admin": True}]
    assert tasks.first_admin(users)["name"] == "b"
    assert tasks.first_admin([]) is None
    assert tasks.first_admin([{"name": "x"}]) is None
    import inspect
    text = inspect.getsource(tasks.first_admin)
    assert "else" in text, "expected a for...else construct"
    assert "found" not in text, "flag variables are forbidden here"


def test_run_length_encode():
    assert tasks.run_length_encode("aaabbc") == [("a", 3), ("b", 2), ("c", 1)]
    assert tasks.run_length_encode([]) == []
    assert tasks.run_length_encode([1, 1, 1]) == [(1, 3)]
    assert tasks.run_length_encode([1, 2, 1]) == [(1, 1), (2, 1), (1, 1)]


def test_parse_sections():
    lines = ["intro", "", "[db]", "host=localhost", "port=5432",
             "[ui]", "theme=dark", "   ", "[db]", "extra=1"]
    out = tasks.parse_sections(lines)
    assert out[""] == ["intro"]
    assert out["db"] == ["host=localhost", "port=5432", "extra=1"]
    assert out["ui"] == ["theme=dark"]


# ------------------------------------------------------------ industry
def test_transitions_table_complete():
    assert set(tasks.TRANSITIONS) == set(tasks.OrderState)


def test_advance_legal_and_illegal():
    o = tasks.Order()
    tasks.advance(o, tasks.OrderState.SUBMITTED)
    tasks.advance(o, tasks.OrderState.PAID)
    assert o.state is tasks.OrderState.PAID
    with pytest.raises(tasks.InvalidTransition):
        tasks.advance(o, tasks.OrderState.DRAFT)
    with pytest.raises(tasks.InvalidTransition):
        tasks.advance(tasks.Order(), tasks.OrderState.DELIVERED)


def test_terminal_states_have_no_exits():
    for terminal in (tasks.OrderState.DELIVERED, tasks.OrderState.CANCELLED):
        assert tasks.TRANSITIONS[terminal] == set()
        with pytest.raises(tasks.InvalidTransition):
            tasks.advance(tasks.Order(terminal), tasks.OrderState.DRAFT)


@pytest.mark.parametrize("start,target,expected_len", [
    ("DRAFT", "DELIVERED", 5),
    ("DRAFT", "CANCELLED", 2),
    ("SUBMITTED", "DELIVERED", 4),
    ("PAID", "CANCELLED", 2),
])
def test_shortest_path_lengths(start, target, expected_len):
    s = getattr(tasks.OrderState, start)
    t = getattr(tasks.OrderState, target)
    path = tasks.shortest_path(s, t)
    assert path is not None and len(path) == expected_len
    assert path[0] is s and path[-1] is t
    for a, b in zip(path, path[1:]):
        assert b in tasks.TRANSITIONS[a], f"{a}->{b} not a legal edge"


def test_shortest_path_unreachable_and_identity():
    assert tasks.shortest_path(tasks.OrderState.DELIVERED,
                               tasks.OrderState.DRAFT) is None
    assert tasks.shortest_path(tasks.OrderState.PAID,
                               tasks.OrderState.PAID) == [tasks.OrderState.PAID]


def test_chunk_while():
    assert tasks.chunk_while(lambda a, b: b - a == 1,
                             [1, 2, 3, 7, 8, 10]) == [[1, 2, 3], [7, 8], [10]]
    assert tasks.chunk_while(lambda a, b: b - a == 1, []) == []
    assert tasks.chunk_while(lambda a, b: a == b, "aabb") == [
        ["a", "a"], ["b", "b"]]
