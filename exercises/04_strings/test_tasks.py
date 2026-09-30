"""Grader for module 04.  Run:  pytest exercises/04_strings -q"""

from __future__ import annotations

import pytest

from _loader import load

tasks = load(__file__)


# ------------------------------------------------------------- beginner
def test_stats():
    assert tasks.stats("one two\nthree") == {
        "chars": 13, "words": 3, "lines": 2,
        "reversed": "eerht\nowt eno"}
    assert tasks.stats("") == {"chars": 0, "words": 0, "lines": 0,
                               "reversed": ""}


def test_initials():
    assert tasks.initials("ada lovelace") == "A.L."
    assert tasks.initials("  grace   brewster   hopper ") == "G.B.H."
    assert tasks.initials("plato") == "P."


@pytest.mark.parametrize("text,shift,expected", [
    ("abc", 1, "bcd"), ("xyz", 3, "abc"), ("Hello, World!", 13,
                                           "Uryyb, Jbeyq!"),
    ("MiXeD", -1, "LhWdC"), ("abc", 26, "abc"), ("123 !", 5, "123 !")])
def test_caesar(text, shift, expected):
    assert tasks.caesar(text, shift) == expected


def test_caesar_roundtrip():
    s = "The quick brown fox jumps over 13 lazy dogs!"
    assert tasks.caesar(tasks.caesar(s, 7), -7) == s


# --------------------------------------------------------- intermediate
@pytest.mark.parametrize("text,expected", [
    ("Crème Brûlée — SO good!", "creme-brulee-so-good"),
    ("  Hello,   World!  ", "hello-world"),
    ("Ünïcödé ✓ works", "unicode-works"),
    ("---already---slugged---", "already-slugged"),
    ("", "")])
def test_slugify(text, expected):
    assert tasks.slugify(text) == expected


def test_parse_query():
    assert tasks.parse_query("a=1&b=2&b=3&c=") == {
        "a": ["1"], "b": ["2", "3"], "c": [""]}
    assert tasks.parse_query("?na%20me=Jo%26hn") == {"na me": ["Jo&hn"]}
    assert tasks.parse_query("") == {}


def test_mask_email():
    assert tasks.mask_email("jane.doe@corp.io") == "j******e@corp.io"
    assert tasks.mask_email("ab@x.com") == "ab@x.com"
    assert tasks.mask_email("a@x.com") == "a@x.com"
    assert tasks.mask_email("abc@x.com") == "a*c@x.com"


# ------------------------------------------------------------ industry
def test_render_template_basic_and_spec():
    tpl = "Hi {name}, you owe {amount:>10.2f} ({name!r})."
    out = tasks.render_template(tpl, {"name": "Ada", "amount": 42})
    assert out == f"Hi Ada, you owe {42:>10.2f} ('Ada')."


def test_render_template_conversions_and_escapes():
    assert tasks.render_template("{v!s} and {{literal}}", {"v": 7}) == \
        "7 and {literal}"
    assert tasks.render_template("{v!r}", {"v": "x"}) == "'x'"


def test_render_template_errors():
    with pytest.raises(KeyError):
        tasks.render_template("{missing}", {})
    with pytest.raises(ValueError):
        tasks.render_template("broken { here", {"x": 1})
    with pytest.raises(ValueError):
        tasks.render_template("stray } brace", {"x": 1})


def test_decode_stream_handles_split_multibyte():
    euro = "€".encode("utf-8")            # 3 bytes
    rocket = "🚀".encode("utf-8")         # 4 bytes
    text = "price: €42 🚀 done"
    raw = text.encode("utf-8")
    # split at every possible boundary and require identical results
    for cut in range(1, len(raw)):
        chunks = [raw[:cut], raw[cut:]]
        assert "".join(tasks.decode_stream(chunks)) == text
    pieces = [raw[i:i + 1] for i in range(len(raw))]
    assert "".join(tasks.decode_stream(pieces)) == text


def test_decode_stream_empty_and_ascii():
    assert list(tasks.decode_stream([])) == []
    assert "".join(tasks.decode_stream([b"plain", b" ascii"])) == "plain ascii"
