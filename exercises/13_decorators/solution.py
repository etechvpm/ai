"""Module 13 - reference solutions."""

from __future__ import annotations

import functools
import time

# ------------------------------------------------------------------ tier: B


def logged(fn=None, *, sink=None):
    def decorator(func):
        records = sink if sink is not None else []

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            records.append(("call", func.__name__, args, kwargs))
            result = func(*args, **kwargs)
            records.append(("return", func.__name__, result))
            return result

        wrapper.records = records
        return wrapper

    return decorator(fn) if fn is not None else decorator


def double_result(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs) * 2
    return wrapper


def count_calls(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return fn(*args, **kwargs)
    wrapper.calls = 0
    return wrapper


# -------------------------------------------------------------- tier: I
def timed(clock=time.monotonic):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            start = clock()
            try:
                return fn(*args, **kwargs)
            finally:
                wrapper.elapsed = clock() - start
        wrapper.elapsed = 0.0
        return wrapper
    return decorator


def retry_dec(attempts: int, exceptions=(Exception,), sleep=time.sleep):
    def decorator(fn):
        if attempts < 1:
            raise ValueError("attempts must be >= 1")

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last = None
            for attempt in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:
                    last = exc
                    if attempt < attempts - 1:
                        sleep(0)
            raise last
        return wrapper
    return decorator


def ttl_cache(seconds: float, clock=time.monotonic):
    def decorator(fn):
        store: dict = {}

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = clock()
            hit = store.get(key)
            if hit is not None and now - hit[0] < seconds:
                return hit[1]
            value = fn(*args, **kwargs)
            store[key] = (now, value)
            return value

        wrapper.cache_clear = store.clear
        return wrapper
    return decorator


# -------------------------------------------------------------- tier: Ind
ROUTES: dict = {}


def route(method: str, path: str):
    def decorator(fn):
        key = (method.upper(), path)
        if key in ROUTES:
            raise ValueError(f"duplicate route: {key}")
        ROUTES[key] = fn
        return fn
    return decorator


def dispatch(method: str, path: str, **params):
    try:
        handler = ROUTES[(method.upper(), path)]
    except KeyError:
        raise KeyError(f"no route: {method} {path}") from None
    return handler(**params)


def validate(**specs):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            import inspect
            bound = inspect.signature(fn).bind(*args, **kwargs)
            bound.apply_defaults()
            for name, expected in specs.items():
                if name in bound.arguments:
                    value = bound.arguments[name]
                    if not isinstance(value, expected):
                        raise TypeError(
                            f"parameter {name!r} expected "
                            f"{getattr(expected, '__name__', expected)}, "
                            f"got {type(value).__name__}")
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def singleton(cls):
    instances: dict = {}

    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if not instances:
            instances["it"] = cls(*args, **kwargs)
        return instances["it"]

    get_instance.__wrapped_class__ = cls
    return get_instance
