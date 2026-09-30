"""Grader for module 16.  Run:  pytest exercises/16_concurrency -q"""

from __future__ import annotations

import asyncio
import threading
import time

import pytest

from _loader import load

tasks = load(__file__)


# ------------------------------------------------------------- beginner
def test_parallel_map_preserves_order():
    def slow_square(x):
        time.sleep(0.01)
        return x * x

    assert tasks.parallel_map(slow_square, range(8), workers=4) == \
        [0, 1, 4, 9, 16, 25, 36, 49]
    assert tasks.parallel_map(str, []) == []


def test_parallel_map_is_actually_concurrent():
    started = time.perf_counter()
    tasks.parallel_map(lambda _x: time.sleep(0.05), range(6), workers=6)
    assert time.perf_counter() - started < 0.4


def test_safe_counter_has_no_lost_updates():
    for _ in range(3):
        assert tasks.safe_counter(4, 5_000) == 20_000


def test_chunk_sums_matches_builtin_sum():
    data = list(range(1_000))
    assert tasks.chunk_sums(data, procs=4) == sum(data)
    assert tasks.chunk_sums([], procs=2) == 0
    assert tasks.chunk_sums([7], procs=4) == 7


# --------------------------------------------------------- intermediate
def test_token_bucket_blocks_when_empty():
    now = [100.0]
    clock = lambda: now[0]                                   # noqa: E731
    bucket = tasks.TokenBucket(rate=2.0, capacity=4.0, clock=clock)
    assert bucket.tokens == 4.0
    assert all(bucket.acquire() for _ in range(4))
    assert bucket.acquire() is False
    now[0] += 1.0                                            # +2 tokens
    assert bucket.acquire(2) is True
    assert bucket.acquire(1) is False
    now[0] += 100.0                                          # capped
    assert bucket.tokens == pytest.approx(4.0)


def test_token_bucket_is_thread_safe():
    bucket = tasks.TokenBucket(rate=0.0, capacity=100)
    granted = []
    lock = threading.Lock()

    def hammer():
        for _ in range(50):
            if bucket.acquire():
                with lock:
                    granted.append(1)

    threads = [threading.Thread(target=hammer) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(granted) == 100, "exactly the capacity, no more, no less"


def test_run_pipeline_returns_input_order():
    assert tasks.run_pipeline([1, 2, 3, 4, 5], lambda x: x * 10,
                              n_workers=3) == [10, 20, 30, 40, 50]
    assert tasks.run_pipeline([], lambda x: x) == []
    out = tasks.run_pipeline(range(20), lambda i: i + 1, n_workers=4)
    assert out == list(range(1, 21))


def test_fetch_all_respects_limit_and_order():
    peak = {"now": 0, "max": 0}

    async def fake_fetch(url):
        peak["now"] += 1
        peak["max"] = max(peak["max"], peak["now"])
        await asyncio.sleep(0)                # yield without real delay
        await asyncio.sleep(0)
        peak["now"] -= 1
        return url.upper()

    urls = [f"u{i}" for i in range(10)]
    got = asyncio.run(tasks.fetch_all(fake_fetch, urls, limit=3))
    assert got == [u.upper() for u in urls]
    assert peak["max"] <= 3, f"limit violated: {peak['max']}"
    assert peak["max"] >= 2, "should overlap, not serialise"


# ------------------------------------------------------------ industry
def test_run_jobs_collects_ok_and_errors():
    async def ok_job():
        return "fine"

    async def bad_job():
        raise ValueError("nope")

    async def slow_job():
        await asyncio.sleep(5)
        return "never"

    report = asyncio.run(tasks.run_jobs(
        [ok_job, bad_job, slow_job], timeout=0.05, max_concurrent=2))
    assert len(report) == 3
    assert report[0] == ("ok", "fine")
    kind, err = report[1]
    assert kind == "error" and isinstance(err, tasks.JobError)
    assert "nope" in str(err)
    kind2, err2 = report[2]
    assert kind2 == "error" and isinstance(err2, tasks.JobError)
    assert "timed out" in str(err2)


def test_run_jobs_limits_concurrency():
    peak = {"now": 0, "max": 0}

    async def job():
        peak["now"] += 1
        peak["max"] = max(peak["max"], peak["now"])
        await asyncio.sleep(0.01)
        peak["now"] -= 1
        return 1

    report = asyncio.run(tasks.run_jobs([job] * 12, timeout=2,
                                        max_concurrent=3))
    assert [r[0] for r in report] == ["ok"] * 12
    assert peak["max"] <= 3


def test_worker_pool_runs_and_shuts_down():
    results = []
    with tasks.WorkerPool(n_workers=3) as pool:
        futures = [pool.submit(lambda i=i: i * 2) for i in range(9)]
        results = [f.result(timeout=5) for f in futures]
    assert results == [i * 2 for i in range(9)]
    assert threading.active_count() < 8, "no thread leaks"


def test_worker_pool_drain_false_and_errors():
    with tasks.WorkerPool(n_workers=1) as pool:
        fut = pool.submit(lambda: 1 / 0)
        with pytest.raises(ZeroDivisionError):
            fut.result(timeout=5)
        pool.shutdown(drain=False)
    with pytest.raises(RuntimeError):
        tasks.WorkerPool().submit(lambda: 1)
