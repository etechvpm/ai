"""Module 04 - reference solutions."""

from __future__ import annotations

import codecs
import re
import unicodedata
from urllib.parse import parse_qsl, unquote

# ------------------------------------------------------------------ tier: B


def stats(text: str) -> dict:
    return {
        "chars": len(text),
        "words": len(text.split()),
        "lines": len(text.splitlines()),
        "reversed": text[::-1],
    }


def initials(full_name: str) -> str:
    parts = full_name.split()
    return "".join(p[0].upper() + "." for p in parts)


def caesar(text: str, shift: int) -> str:
    shift %= 26
    out = []
    for ch in text:
        if "a" <= ch <= "z":
            out.append(chr((ord(ch) - ord("a") + shift) % 26 + ord("a")))
        elif "A" <= ch <= "Z":
            out.append(chr((ord(ch) - ord("A") + shift) % 26 + ord("A")))
        else:
            out.append(ch)
    return "".join(out)


# -------------------------------------------------------------- tier: I
def slugify(text: str) -> str:
    norm = unicodedata.normalize("NFC", text)
    decomposed = unicodedata.normalize("NFD", norm)
    no_accents = "".join(c for c in decomposed
                         if not unicodedata.combining(c))
    folded = no_accents.casefold()
    return re.sub(r"[^a-z0-9]+", "-", folded).strip("-")


def parse_query(query_string: str) -> dict:
    qs = query_string.lstrip("?")
    out: dict[str, list[str]] = {}
    for key, value in parse_qsl(qs, keep_blank_values=True):
        out.setdefault(unquote(key), []).append(value)
    return out


def mask_email(address: str) -> str:
    local, _, domain = address.partition("@")
    if len(local) <= 2:
        masked = local
    else:
        masked = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{masked}@{domain}"


# -------------------------------------------------------------- tier: Ind
_PLACEHOLDER = re.compile(
    r"\{(?P<key>[A-Za-z_]\w*)(?P<conv>![rs])?(?::(?P<spec>[^{}]*))?\}")


_LBRACE, _RBRACE = "\x00", "\x01"


def render_template(template: str, mapping: dict) -> str:
    # protect escaped braces FIRST, otherwise '{{x}}' looks like a placeholder
    work = template.replace("{{", _LBRACE).replace("}}", _RBRACE)
    stripped = _PLACEHOLDER.sub("", work)
    if "{" in stripped or "}" in stripped:
        raise ValueError(f"malformed placeholder in template: {template!r}")

    def sub(match: re.Match) -> str:
        key = match.group("key")
        if key not in mapping:
            raise KeyError(key)
        value = mapping[key]
        conv = match.group("conv")
        spec = match.group("spec")
        if conv == "!r":
            text = repr(value)
        elif conv == "!s":
            text = str(value)
        else:
            text = value
        if spec:
            # numeric specs ('>10.2f') need the RAW value, not its str form
            return format(text, spec)
        return text if isinstance(text, str) else format(text)

    result = _PLACEHOLDER.sub(sub, work)
    return result.replace(_LBRACE, "{").replace(_RBRACE, "}")


def decode_stream(chunks):
    chunks = list(chunks)
    decoder = codecs.getincrementaldecoder("utf-8")()
    last = len(chunks) - 1
    for i, chunk in enumerate(chunks):
        piece = decoder.decode(chunk, i == last)
        if piece:
            yield piece
