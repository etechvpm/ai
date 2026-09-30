"""Module 07 - reference solutions."""

from __future__ import annotations

import functools
import time

# ------------------------------------------------------------------ tier: B


def repeat(fn, n: int, value):
    for _ in range(n):
        value = fn(value)
    return value


def compose(f, g):
    @functools.wraps(f)
    def composed(x):
        return f(g(x))
    return composed


def apply_all(fns, value):
    for fn in fns:
        value = fn(value)
    return value


# -------------------------------------------------------------- tier: I
def retry(fn, attempts: int, exceptions=(Exception,)):
    if attempts < 1:
        raise ValueError("attempts must be >= 1")
    last = None
    for _ in range(attempts):
        try:
            return fn()
        except exceptions as exc:
            last = exc
    raise last


def memoize(fn):
    cache: dict = {}

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key in cache:
            wrapper.hits += 1
            return cache[key]
        wrapper.misses += 1
        cache[key] = fn(*args, **kwargs)
        return cache[key]

    wrapper.cache = cache
    wrapper.hits = 0
    wrapper.misses = 0
    return wrapper


def pipeline(*stages):
    def run(value):
        for stage in stages:
            value = stage(value)
        return value
    return run


# -------------------------------------------------------------- tier: Ind
def retry_with_backoff(fn, *, attempts: int = 3, base_delay: float = 0.1,
                       sleep=time.sleep, exceptions=(Exception,)):
    if attempts < 1:
        raise ValueError("attempts must be >= 1")
    last = None
    for attempt in range(attempts):
        try:
            return fn()
        except exceptions as exc:
            last = exc
            if attempt < attempts - 1:
                sleep(base_delay * 2 ** attempt)
    raise last


REGISTRY: dict = {}


def register(name: str):
    def decorator(fn):
        if name in REGISTRY:
            raise ValueError(f"duplicate registration: {name!r}")
        REGISTRY[name] = fn
        return fn
    return decorator


def dispatch(name: str, *args, **kwargs):
    try:
        fn = REGISTRY[name]
    except KeyError:
        raise KeyError(f"no handler registered as {name!r}") from None
    return fn(*args, **kwargs)


class TypeDispatcher:
    def __init__(self):
        self._handlers: dict[type, object] = {}

    def register(self, cls):
        def decorator(fn):
            self._handlers[cls] = fn
            return fn
        return decorator

    def _resolve(self, value):
        for cls in type(value).__mro__:
            if cls in self._handlers:
                return self._handlers[cls]
        return None

    def __call__(self, value, *args, **kwargs):
        handler = self._resolve(value)
        if handler is None:
            raise TypeError(
                f"no handler for {type(value).__name__}")
        return handler(value, *args, **kwargs)
