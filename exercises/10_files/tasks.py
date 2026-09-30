"""Module 10 - Files & I/O.  Student task sheet."""

from __future__ import annotations


# ------------------------------------------------------------------ tier: B
def read_non_empty_lines(path) -> list[str]:
    """Stripped lines with blank/whitespace-only lines removed."""
    raise NotImplementedError


def count_words(path) -> int:
    """Total whitespace-separated words in the file."""
    raise NotImplementedError


def copy_in_chunks(src, dst, chunk_size: int = 64) -> int:
    """Binary copy in chunks of at most chunk_size bytes.

    Returns the total number of bytes written. Must not load the whole file.
    """
    raise NotImplementedError


# -------------------------------------------------------------- tier: I
def write_atomic(path, text: str) -> None:
    """Write text so readers never observe a partial file.

    Use a temporary file in the SAME directory, then os.replace. If writing
    fails midway, the previous target content must remain untouched and no
    temp file may be left behind.
    """
    raise NotImplementedError


def tail_lines(path, n: int) -> list[str]:
    """The last n lines (without trailing newline artefacts).

    n <= 0 -> []. Reading the whole file into a list is not acceptable for
    this exercise: use a bounded structure or end-seeking.
    """
    raise NotImplementedError


def deep_merge(a: dict, b: dict) -> dict:
    """Recursively merge: dicts merge, anything else b wins. Inputs unchanged."""
    raise NotImplementedError


# -------------------------------------------------------------- tier: Ind
class JsonlLog:
    """Context manager appending one JSON object per line.

    with JsonlLog(path) as log:
        log.log(event="start", n=1)      # flushed immediately
    Iterating JsonlLog(path) yields the parsed records, skipping blank and
    corrupt (torn) lines instead of raising.
    """

    def __init__(self, path):
        raise NotImplementedError

    def log(self, **record) -> None:
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, *exc_info):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError


def grep_file(path, pattern, *, case_sensitive: bool = False,
              encoding: str = "utf-8"):
    """Yield (lineno, line-without-newline) for lines matching pattern.

    pattern may be a str (compiled internally) or a compiled regex.
    Line numbers start at 1. Must stream (never read() the whole file).
    """
    raise NotImplementedError
