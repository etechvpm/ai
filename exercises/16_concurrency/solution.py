"""Module 16 - Concurrency.  Reference solutions."""

from __future__ import annotations

import asyncio
import pickle
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from queue import Queue


# ------------------------------------------------------------------ tier: B
def parallel_map(fn, items, workers: int = 4) -> list:
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(fn, items))


def safe_counter(n_threads: int, per_thread: int) -> int:
    counter = {"value": 0}
    lock = threading.Lock()

    def bump() -> None:
        for _ in range(per_thread):
            with lock:                       # tiny critical section
                counter["value"] += 1

    threads = [threading.Thread(target=bump, name=f"bump-{i}")
               for i in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return counter["value"]


def _sum_chunk(chunk) -> int:
    """Module level: multiprocessing pickles callables by reference."""
    return sum(chunk)


def chunk_sums(numbers, procs: int = 2) -> int:
    numbers = list(numbers)
    if not numbers:
        return 0
    procs = max(1, min(procs, len(numbers)))
    size = -(-len(numbers) // procs)             # ceiling division
    chunks = [numbers[i:i + size] for i in range(0, len(numbers), size)]
    try:
        with ProcessPoolExecutor(max_workers=procs) as ex:
            return sum(ex.map(_sum_chunk, chunks))
    except (BrokenProcessPool, pickle.PicklingError, OSError,
            RuntimeError, NotImplementedError):
        # spawn-based platforms / sandboxes without process support
        with ThreadPoolExecutor(max_workers=procs) as ex:
            return sum(ex.map(_sum_chunk, chunks))


# -------------------------------------------------------------- tier: I
class TokenBucket:
    def __init__(self, rate: float, capacity: float, clock=None):
        self.rate = float(rate)
        self.capacity = float(capacity)
        self._clock = clock or time.monotonic
        self._tokens = float(capacity)
        self._last = self._clock()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = self._clock()
        elapsed = max(0.0, now - self._last)
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._last = now

    @property
    def tokens(self) -> float:
        with self._lock:
            self._refill()
            return self._tokens

    def acquire(self, n: int = 1) -> bool:
        with self._lock:
            self._refill()
            if self._tokens >= n:
                self._tokens -= n
                return True
            return False


def run_pipeline(items, worker, n_workers: int = 2) -> list:
    items = list(items)
    results: list = [None] * len(items)
    q: Queue = Queue()

    def consume() -> None:
        while True:
            job = q.get()
            try:
                if job is None:
                    return
                index, item = job
                results[index] = worker(item)
            finally:
                q.task_done()

    threads = [threading.Thread(target=consume, name=f"worker-{i}",
                                daemon=True) for i in range(n_workers)]
    for t in threads:
        t.start()
    for index, item in enumerate(items):
        q.put((index, item))
    q.join()                                   # wait for real work
    for _ in threads:
        q.put(None)                            # poison pills
    for t in threads:
        t.join()
    return results


async def fetch_all(fetcher, urls, limit: int = 3) -> list:
    sem = asyncio.Semaphore(limit)

    async def guarded(url):
        async with sem:
            return await fetcher(url)

    return await asyncio.gather(*(guarded(u) for u in urls))


# -------------------------------------------------------------- tier: Ind
class JobError(Exception):
    pass


async def run_jobs(jobs, *, timeout: float, max_concurrent: int) -> list:
    sem = asyncio.Semaphore(max_concurrent)
    report: list = [None] * len(jobs)

    async def one(index, factory):
        async with sem:
            try:
                async with asyncio.timeout(timeout):
                    value = await factory()
            except (asyncio.TimeoutError, TimeoutError):
                report[index] = ("error", JobError(f"job {index} timed out"))
            except asyncio.CancelledError:
                report[index] = ("error", JobError(f"job {index} cancelled"))
                raise
            except Exception as exc:              # noqa: BLE001
                report[index] = ("error",
                                 JobError(f"job {index} failed: {exc}"))
            else:
                report[index] = ("ok", value)

    await asyncio.gather(*(one(i, f) for i, f in enumerate(jobs)))
    return report


class WorkerPool:
    def __init__(self, n_workers: int = 2):
        self.n_workers = n_workers
        self._executor: ThreadPoolExecutor | None = None

    def __enter__(self) -> "WorkerPool":
        self._executor = ThreadPoolExecutor(
            max_workers=self.n_workers, thread_name_prefix="workerpool")
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.shutdown(drain=True)
        return False

    def submit(self, fn, *args, **kwargs):
        if self._executor is None:
            raise RuntimeError("use WorkerPool as a context manager")
        return self._executor.submit(fn, *args, **kwargs)

    def shutdown(self, drain: bool = True) -> None:
        if self._executor is None:
            return
        self._executor.shutdown(wait=drain, cancel_futures=not drain)
        self._executor = None
