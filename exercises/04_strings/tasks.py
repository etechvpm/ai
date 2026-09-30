"""Module 04 - Strings & text.  Student task sheet."""

from __future__ import annotations


# ------------------------------------------------------------------ tier: B
def stats(text: str) -> dict:
    """{"chars": len(text), "words": word count, "lines": line count,
    "reversed": the string reversed}.

    Words = s.split(); lines = s.splitlines() (empty string -> 0 lines).
    """
    raise NotImplementedError


def initials(full_name: str) -> str:
    """'ada lovelace' -> 'A.L.'  (extra whitespace tolerated; each part's
    first letter upper-cased, joined by '.', trailing dot included)."""
    raise NotImplementedError


def caesar(text: str, shift: int) -> str:
    """Shift ASCII letters by *shift* (may be negative or > 26), wrapping.

    Case preserved; every other character untouched.
    """
    raise NotImplementedError


# -------------------------------------------------------------- tier: I
def slugify(text: str) -> str:
    """URL slug: NFC-normalise, drop accents, casefold, replace runs of
    non-alphanumerics with a single '-', strip leading/trailing '-'.

    'Crème Brûlée — SO good!' -> 'creme-brulee-so-good'
    """
    raise NotImplementedError


def parse_query(query_string: str) -> dict:
    """Parse 'a=1&b=2&b=3&c=' into {'a': ['1'], 'b': ['2', '3'], 'c': ['']}.

    Percent-decode keys and values (e.g. 'na%20me' -> 'na me'), keep blank
    values, keep repeated keys as a list in order. A leading '?' is allowed.
    """
    raise NotImplementedError


def mask_email(address: str) -> str:
    """Keep the first and last character of the local part, mask the rest
    with '*'; domain unchanged.  'jane.doe@corp.io' -> 'j******e@corp.io'.
    Local parts of length <= 2 are returned unchanged (nothing to mask).
    """
    raise NotImplementedError


# -------------------------------------------------------------- tier: Ind
def render_template(template: str, mapping: dict) -> str:
    """Substitute placeholders in *template* from *mapping*.

    Supported: {key}, {key!r}, {key!s}, {key:spec}, and {{ }} for literal
    braces.  Unknown key -> KeyError.  A '{' or '}' that is not a valid
    placeholder or escaped brace -> ValueError.
    """
    raise NotImplementedError


def decode_stream(chunks):
    """Decode an iterable of bytes chunks split at ARBITRARY boundaries.

    Yield str pieces using an incremental UTF-8 decoder so that a multi-byte
    character split across two chunks decodes exactly once, correctly.
    The final chunk must flush the decoder (final=True).
    """
    raise NotImplementedError
