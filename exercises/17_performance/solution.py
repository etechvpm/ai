"""Module 17 - Performance.  Reference solutions."""

from __future__ import annotations

import heapq
import itertools
import threading
from collections import Counter, OrderedDict, deque

_KWARGS_MARK = object()          # module-level sentinel: kwargs never collide
                                 # with positional arguments in a cache key


# ------------------------------------------------------------------ tier: B
def find_duplicates(items) -> list:
    seen: set = set()
    repeated: set = set()
    out: list = []
    for item in items:
        if item in seen:
            if item not in repeated:
                repeated.add(item)
                out.append(item)
        else:
            seen.add(item)
    return out


def frequent(words, k: int) -> list:
    counts = Counter(words)
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return ordered[:k]


def join_lines(lines) -> str:
    return "\n".join(lines)


def flatten(pairs) -> list:
    return [x for pair in pairs for x in pair]


# -------------------------------------------------------------- tier: I
def moving_average(values, window: int) -> list:
    if window < 1:
        raise ValueError("window must be >= 1")
    values = list(values)
    if window > len(values):
        return []
    out: list = []
    run = deque()
    total = 0.0
    for value in values:
        run.append(value)
        total += value
        if len(run) > window:
            total -= run.popleft()
        if len(run) == window:
            out.append(total / window)
    return out


def top_k(numbers, k: int) -> list:
    if k <= 0:
        return []
    return heapq.nlargest(k, numbers)


class LRUCache:
    def __init__(self, capacity: int):
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity = capacity
        self._data: OrderedDict = OrderedDict()

    def get(self, key, default=None):
        if key not in self._data:
            return default
        self._data.move_to_end(key)          # mark as recently used
        return self._data[key]

    def put(self, key, value) -> None:
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = value
        while len(self._data) > self.capacity:
            self._data.popitem(last=False)   # evict least recently used

    def keys(self) -> list:
        return list(reversed(self._data))

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key) -> bool:
        return key in self._data


def chunked(it, n: int):
    if n < 1:
        raise ValueError("n must be >= 1")
    iterator = iter(it)
    while True:
        batch = list(itertools.islice(iterator, n))
        if not batch:
            return
        yield batch


# -------------------------------------------------------------- tier: Ind
def memoized(fn=None, *, maxsize: int = 128):
    def decorate(func):
        cache: OrderedDict = OrderedDict()
        lock = threading.Lock()
        stats = {"hits": 0, "misses": 0}

        def make_key(args, kwargs):
            key = args
            if kwargs:
                key += (_KWARGS_MARK,) + tuple(sorted(kwargs.items()))
            return key

        def wrapper(*args, **kwargs):
            key = make_key(args, kwargs)
            try:
                hash(key)
            except TypeError:
                return func(*args, **kwargs)      # unhashable: no caching
            with lock:
                if key in cache:
                    cache.move_to_end(key)
                    stats["hits"] += 1
                    return cache[key]
            result = func(*args, **kwargs)        # call outside the lock
            with lock:
                stats["misses"] += 1
                cache[key] = result
                cache.move_to_end(key)
                if maxsize is not None:
                    while len(cache) > maxsize:
                        cache.popitem(last=False)
            return result

        def cache_info() -> dict:
            with lock:
                return {"hits": stats["hits"], "misses": stats["misses"],
                        "maxsize": maxsize, "currsize": len(cache)}

        def cache_clear() -> None:
            with lock:
                cache.clear()
                stats["hits"] = 0
                stats["misses"] = 0

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        wrapper.maxsize = maxsize
        wrapper.__wrapped__ = func
        wrapper.__name__ = getattr(func, "__name__", "wrapper")
        wrapper.__doc__ = func.__doc__
        return wrapper

    if fn is None:
        return decorate
    return decorate(fn)


def enrich_orders(orders, fetch_customers) -> list:
    ids = sorted({order["customer_id"] for order in orders})
    customers = fetch_customers(ids) if ids else {}
    return [{**order, "customer": customers.get(order["customer_id"])}
            for order in orders]
