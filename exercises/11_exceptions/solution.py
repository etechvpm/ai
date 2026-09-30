"""Module 11 - reference solutions."""

from __future__ import annotations

import functools
import time
from pathlib import Path


# ------------------------------------------------------------------ tier: B
class DivisionError(ZeroDivisionError):
    pass


def safe_int(text, default=None):
    try:
        return int(text)
    except (ValueError, TypeError):
        return default


def divide(a, b):
    if b == 0:
        raise DivisionError("division by zero")
    return a / b


def first_existing(paths):
    tried = []
    for p in paths:
        path = Path(p)
        tried.append(str(path))
        if path.is_file():
            return path
    raise FileNotFoundError(f"none of these exist: {', '.join(tried)}")


# -------------------------------------------------------------- tier: I
class ConfigError(ValueError):
    def __init__(self, line_number: int, reason: str):
        super().__init__(f"line {line_number}: {reason}")
        self.line_number = line_number
        self.reason = reason


def parse_config(text: str) -> dict:
    out: dict = {}
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigError(lineno, "expected key=value")
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if not key:
            raise ConfigError(lineno, "empty key")
        if key in out:
            raise ConfigError(lineno, f"duplicate key {key!r}")
        out[key] = value
    return out


def retry_on(exc_types, attempts: int, delay: float = 0.0):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last = None
            for attempt in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except exc_types as exc:
                    last = exc
                    if attempt < attempts - 1 and delay:
                        time.sleep(delay)
            raise last
        return wrapper
    return decorator


class TransformError(Exception):
    def __init__(self, key, original):
        super().__init__(f"transform failed for key {key!r}: {original}")
        self.key = key
        self.original = original


def guarded_get(mapping, key, transform):
    value = mapping[key]
    try:
        return transform(value)
    except Exception as exc:
        raise TransformError(key, exc) from exc


# -------------------------------------------------------------- tier: Ind
class ErrorMapper:
    def __init__(self):
        self._handlers: dict = {}

    def map(self, exc_type, handler):
        self._handlers[exc_type] = handler
        return handler

    def run(self, fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            for cls in type(exc).__mro__:
                handler = self._handlers.get(cls)
                if handler is not None:
                    return handler(exc)
            raise


class suppressed:
    def __init__(self, *exc_types, on_suppressed=None):
        self.exc_types = exc_types
        self.on_suppressed = on_suppressed
        self.suppressed: list = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None and issubclass(exc_type, self.exc_types):
            record = (exc_type, str(exc))
            self.suppressed.append(record)
            if self.on_suppressed is not None:
                self.on_suppressed(record)
            return True
        return False
