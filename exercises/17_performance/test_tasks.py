"""Grader for module 17.  Run:  pytest exercises/17_performance -q"""

from __future__ import annotations

import itertools
import threading
import time

import pytest

from _loader import load

tasks = load(__file__)


# ------------------------------------------------------------- beginner
def test_find_duplicates():
    assert tasks.find_duplicates([1, 2, 3, 2, 1, 4]) == [2, 1]
    assert tasks.find_duplicates([]) == []
    assert tasks.find_duplicates(["a", "b"]) == []
    assert tasks.find_duplicates("abca") == ["a"]


def test_find_duplicates_is_linear():
    data = list(range(200_000)) + [1, 2]
    t0 = time.perf_counter()
    out = tasks.find_duplicates(data)
    dt = time.perf_counter() - t0
    assert out == [1, 2]
    assert dt < 1.5, f"looks quadratic: {dt:.2f}s for 200k items"


def test_frequent():
    words = "the cat the dog the cat bird".split()
    assert tasks.frequent(words, 2) == [("the", 3), ("cat", 2)]
    assert tasks.frequent(["b", "a", "b", "a"], 2) == [("a", 2), ("b", 2)]
    assert tasks.frequent([], 3) == []


def test_join_and_flatten():
    assert tasks.join_lines(["a", "b"]) == "a\nb"
    assert tasks.join_lines([]) == ""
    assert tasks.flatten([[1, 2], [3], []]) == [1, 2, 3]
    assert tasks.flatten([]) == []


def test_join_lines_is_linear():
    lines = [f"line {i}" for i in range(100_000)]
    t0 = time.perf_counter()
    out = tasks.join_lines(lines)
    assert time.perf_counter() - t0 < 1.0
    assert out.count("\n") == 99_999


# --------------------------------------------------------- intermediate
def test_moving_average():
    assert tasks.moving_average([1, 2, 3, 4], 2) == [1.5, 2.5, 3.5]
    assert tasks.moving_average([1, 2, 3], 5) == []
    assert tasks.moving_average([5], 1) == [5.0]
    with pytest.raises(ValueError):
        tasks.moving_average([1], 0)


def test_moving_average_is_linear():
    data = range(200_000)
    t0 = time.perf_counter()
    out = tasks.moving_average(data, 50)
    dt = time.perf_counter() - t0
    assert len(out) == 199_951
    assert dt < 2.0, f"window sum not running-total: {dt:.2f}s"


def test_top_k():
    assert tasks.top_k([3, 1, 9, 7], 2) == [9, 7]
    assert tasks.top_k([1, 2, 3], 10) == [3, 2, 1]
    assert tasks.top_k([1], 0) == []


def test_lru_cache_eviction_order():
    cache = tasks.LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1              # 'a' now most recent
    cache.put("c", 3)                       # evicts 'b'
    assert cache.get("b") is None
    assert cache.get("a") == 1 and cache.get("c") == 3
    assert len(cache) == 2
    cache.put("a", 99)                      # update, no eviction
    assert cache.get("a") == 99 and len(cache) == 2
    assert cache.keys()[0] == "a"
    with pytest.raises(ValueError):
        tasks.LRUCache(0)


def test_chunked_is_lazy():
    assert list(tasks.chunked([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]
    assert list(tasks.chunked([], 3)) == []
    infinite = itertools.count(1)
    first_two = list(itertools.islice(tasks.chunked(infinite, 3), 2))
    assert first_two == [[1, 2, 3], [4, 5, 6]]
    with pytest.raises(ValueError):
        list(tasks.chunked([1], 0))


# ------------------------------------------------------------ industry
def test_memoized_caches_and_reports_stats():
    calls = []

    @tasks.memoized
    def slow_square(x):
        calls.append(x)
        return x * x

    assert slow_square(3) == 9 and slow_square(3) == 9
    assert calls == [3], "second call must be a cache hit"
    info = slow_square.cache_info()
    assert info["hits"] == 1 and info["misses"] == 1 and info["currsize"] == 1
    slow_square.cache_clear()
    assert slow_square.cache_info()["currsize"] == 0
    assert slow_square(3) == 9 and calls == [3, 3]


def test_memoized_kwargs_order_and_maxsize():
    @tasks.memoized(maxsize=2)
    def pair(a=0, b=0):
        return a + b

    assert pair(a=1, b=2) == 3
    assert pair(b=2, a=1) == 3
    assert pair.cache_info()["misses"] == 1, "same kwargs in any order = 1 entry"
    pair(1), pair(2), pair(3)
    assert pair.cache_info()["currsize"] <= 2


def test_memoized_is_thread_safe():
    calls = []
    lock = threading.Lock()

    @tasks.memoized
    def slow(x):
        with lock:
            calls.append(x)
        time.sleep(0.001)
        return x * 2

    threads = [threading.Thread(target=slow, args=(5,)) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    info = slow.cache_info()
    assert info["hits"] + info["misses"] == 8
    assert info["currsize"] == 1


def test_enrich_orders_calls_batch_once():
    calls = []

    def fetch_customers(ids):
        calls.append(list(ids))
        return {i: {"name": f"c{i}"} for i in ids}

    orders = [{"id": 1, "customer_id": 7, "total": 10},
              {"id": 2, "customer_id": 8, "total": 20},
              {"id": 3, "customer_id": 7, "total": 30}]
    out = tasks.enrich_orders(orders, fetch_customers)
    assert len(calls) == 1, f"N+1 not fixed: {len(calls)} calls"
    assert sorted(calls[0]) == [7, 8]
    assert out[0]["customer"] == {"name": "c7"}
    assert out[2]["customer"] == {"name": "c7"}
    assert out[1]["id"] == 2 and out[1]["total"] == 20


def test_enrich_orders_handles_empty_and_missing():
    calls = []
    out = tasks.enrich_orders([], lambda ids: calls.append(ids) or {})
    assert out == [] and calls == []
    out2 = tasks.enrich_orders([{"id": 1, "customer_id": 9}], lambda ids: {})
    assert out2[0]["customer"] is None
