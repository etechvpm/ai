"""Grader for module 10.  Run:  pytest exercises/10_files -q"""

from __future__ import annotations

import json

import pytest

from _loader import load

tasks = load(__file__)


# ------------------------------------------------------------- beginner
def test_read_non_empty_lines(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("one\n\n  \n  two  \nthree\n", encoding="utf-8")
    assert tasks.read_non_empty_lines(p) == ["one", "two", "three"]


def test_count_words(tmp_path):
    p = tmp_path / "w.txt"
    p.write_text("the quick brown\nfox\n\njumps\n", encoding="utf-8")
    assert tasks.count_words(p) == 5
    empty = tmp_path / "e.txt"
    empty.write_text("", encoding="utf-8")
    assert tasks.count_words(empty) == 0


def test_copy_in_chunks(tmp_path):
    src = tmp_path / "src.bin"
    data = bytes(range(256)) * 3
    src.write_bytes(data)
    dst = tmp_path / "dst.bin"
    assert tasks.copy_in_chunks(src, dst, chunk_size=64) == len(data)
    assert dst.read_bytes() == data
    assert tasks.copy_in_chunks(src, tmp_path / "d2.bin", chunk_size=100000) \
        == len(data)


# --------------------------------------------------------- intermediate
def test_write_atomic_basic(tmp_path):
    p = tmp_path / "cfg.txt"
    tasks.write_atomic(p, "first\n")
    assert p.read_text(encoding="utf-8") == "first\n"
    tasks.write_atomic(p, "second\n")
    assert p.read_text(encoding="utf-8") == "second\n"
    assert not list(tmp_path.glob("*.tmp")), "no temp files left behind"


def test_write_atomic_preserves_on_failure(tmp_path, monkeypatch):
    p = tmp_path / "cfg.txt"
    p.write_text("original\n", encoding="utf-8")

    def boom(*a, **kw):
        raise OSError("disk on fire")

    monkeypatch.setattr(tasks.os, "replace", boom)
    with pytest.raises(OSError):
        tasks.write_atomic(p, "new content")
    assert p.read_text(encoding="utf-8") == "original\n"
    assert not list(tmp_path.glob("*.tmp"))


def test_tail_lines(tmp_path):
    p = tmp_path / "log.txt"
    p.write_text("\n".join(f"line{i}" for i in range(1, 101)) + "\n",
                 encoding="utf-8")
    assert tasks.tail_lines(p, 3) == ["line98", "line99", "line100"]
    assert tasks.tail_lines(p, 500) == [f"line{i}" for i in range(1, 101)]
    assert tasks.tail_lines(p, 0) == []
    empty = tmp_path / "empty.txt"
    empty.write_text("", encoding="utf-8")
    assert tasks.tail_lines(empty, 5) == []


def test_deep_merge():
    a = {"x": 1, "nested": {"p": 1, "q": 2}, "keep": [1]}
    b = {"y": 2, "nested": {"q": 20, "r": 30}, "keep": [2]}
    merged = tasks.deep_merge(a, b)
    assert merged == {"x": 1, "y": 2, "keep": [2],
                      "nested": {"p": 1, "q": 20, "r": 30}}
    assert a == {"x": 1, "nested": {"p": 1, "q": 2}, "keep": [1]}, \
        "inputs must not be mutated"
    assert tasks.deep_merge({}, {"a": 1}) == {"a": 1}


# ------------------------------------------------------------ industry
def test_jsonl_log_roundtrip(tmp_path):
    p = tmp_path / "events.jsonl"
    with tasks.JsonlLog(p) as log:
        log.log(event="start", n=1)
        log.log(event="end", n=2, note="ünïcode")
    lines = p.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0]) == {"event": "start", "n": 1}
    assert list(tasks.JsonlLog(p)) == [
        {"event": "start", "n": 1},
        {"event": "end", "n": 2, "note": "ünïcode"}]


def test_jsonl_log_appends_and_survives_torn_tail(tmp_path):
    p = tmp_path / "events.jsonl"
    with tasks.JsonlLog(p) as log:
        log.log(a=1)
    with tasks.JsonlLog(p) as log:
        log.log(a=2)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write('{"a": 3, "bro\n')        # torn final record
    assert [r["a"] for r in tasks.JsonlLog(p)] == [1, 2]


def test_grep_file(tmp_path):
    p = tmp_path / "app.log"
    p.write_text("INFO start\nERROR disk full\ninfo again\n"
                 "ERROR net down\n", encoding="utf-8")
    assert list(tasks.grep_file(p, "error")) == [
        (2, "ERROR disk full"), (4, "ERROR net down")]
    assert list(tasks.grep_file(p, "error", case_sensitive=True)) == []
    assert list(tasks.grep_file(p, r"ERR\w+ net")) == [(4, "ERROR net down")]
    import re
    assert list(tasks.grep_file(p, re.compile("^INFO"))) == [(1, "INFO start")]
    assert list(tasks.grep_file(p, "nothing")) == []
