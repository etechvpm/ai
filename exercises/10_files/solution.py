"""Module 10 - reference solutions."""

from __future__ import annotations

import json
import os
import re
import tempfile
from collections import deque
from pathlib import Path

# ------------------------------------------------------------------ tier: B


def read_non_empty_lines(path) -> list[str]:
    with open(path, encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip()]


def count_words(path) -> int:
    total = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            total += len(line.split())
    return total


def copy_in_chunks(src, dst, chunk_size: int = 64) -> int:
    written = 0
    with open(src, "rb") as fin, open(dst, "wb") as fout:
        while chunk := fin.read(chunk_size):
            fout.write(chunk)
            written += len(chunk)
    return written


# -------------------------------------------------------------- tier: I
def write_atomic(path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name,
                               suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def tail_lines(path, n: int) -> list[str]:
    if n <= 0:
        return []
    recent: deque = deque(maxlen=n)
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            recent.append(line.rstrip("\n"))
    return list(recent)


def deep_merge(a: dict, b: dict) -> dict:
    out = dict(a)
    for key, value in b.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


# -------------------------------------------------------------- tier: Ind
class JsonlLog:
    def __init__(self, path):
        self.path = Path(path)
        self._fh = None

    def __enter__(self):
        self._fh = open(self.path, "a", encoding="utf-8")
        return self

    def log(self, **record) -> None:
        if self._fh is None:
            raise ValueError("JsonlLog must be used as a context manager")
        self._fh.write(json.dumps(record, ensure_ascii=False,
                                  default=str) + "\n")
        self._fh.flush()

    def __exit__(self, *exc_info):
        self._fh.close()
        self._fh = None
        return False

    def __iter__(self):
        with open(self.path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def grep_file(path, pattern, *, case_sensitive: bool = False,
              encoding: str = "utf-8"):
    if isinstance(pattern, str):
        flags = 0 if case_sensitive else re.IGNORECASE
        regex = re.compile(pattern, flags)
    else:
        regex = pattern
    with open(path, encoding=encoding, errors="replace") as fh:
        for lineno, line in enumerate(fh, 1):
            if regex.search(line):
                yield lineno, line.rstrip("\n")
