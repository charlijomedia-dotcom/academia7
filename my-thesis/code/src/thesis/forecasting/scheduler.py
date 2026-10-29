"""Run-wide scheduling of independent rolling chains on one shared worker pool.

Before this module, each `_chains` call made its own pool: the five chains of one series
ran together, and the next series started only when the slowest of the five (a K=3
Markov-switching chain) had finished, leaving the other workers idle for hours. Here every
rolling chain of the run is handed to **one** pool as soon as the specification stage has
fixed it, and a dispatcher keeps exactly `workers` chains in flight, always starting the
most expensive chain that is ready.

What does not change, and why:

* a chain still runs start to finish inside one worker, in chronological origin order,
  so warm starts and their cache keys are exactly as before (`parallel.py`);
* every fit draws randomness from a seed derived from series, model, specification and
  origin, never from a shared stream, so results do not depend on scheduling;
* a chain the serial design would serve from the fit cache (an identical chain run
  earlier for a superset of horizons, such as the T4.8 baseline-length chains) is started
  only after the chain that fills those cache entries has finished, so it is served from
  the cache exactly as before and the workload is unchanged;
* the pipeline still *consumes* results in its original order, so every registry and
  table is appended in the same order.

Parallel = serial is asserted by tests on synthetic and on the frozen data.
"""

from __future__ import annotations

import heapq
import json
import threading
import time
from concurrent.futures import FIRST_COMPLETED, Future, ProcessPoolExecutor, wait
from dataclasses import dataclass, field
from typing import Any, Sequence

import multiprocessing
import pandas as pd

from ..core.cache import FitCache
from ..core.config import Config
from .parallel import ChainJob, _execute, _initializer
from .rolling import ChainResult, DataIdentity
from .windows import estimation_origins

#: Relative cost of one origin, used only to decide which ready chain starts first.
#: Ordering cannot change a result (see the module docstring); it only shortens the run.
#: The values are the measured relative fit times of the reduced run. MSAR3 keeps an entry
#: so the scheduler can cost any job it is given, but the pipeline no longer submits K=3
#: rolling chains (Part 5 §11.1, amended 29 October 2026).
COST_PER_ORIGIN = {"MSAR3": 50.0, "MSAR": 20.0, "STAR": 1.5, "ARMA": 0.2, "AR": 0.01}


class PrerequisiteFailed(RuntimeError):
    """A chain was not run because the chain it depends on failed."""


def chain_signature(job: ChainJob) -> tuple:
    """Everything that makes two chains compute the same fits (the cache key, minus
    the horizons, which a cached payload may cover as a superset)."""
    return (job.series_name, job.transformation,
            json.dumps(job.spec.as_dict(), sort_keys=True, default=str),
            job.window_length, job.max_origins, job.frequency)


def n_origins(job: ChainJob) -> int:
    return len(estimation_origins(pd.DatetimeIndex(job.y.index), job.window_length,
                                  list(job.horizons), max_origins=job.max_origins))


def expected_cost(job: ChainJob) -> float:
    return COST_PER_ORIGIN.get(job.spec.model, 1.0) * n_origins(job)


def cache_dependencies(jobs: Sequence[ChainJob], cache_enabled: bool) -> dict[str, str]:
    """For each job the serial design serves from the cache, the job that fills it.

    In consumption order, a job whose signature equals an earlier job's and whose
    horizons are a subset of that job's reads every fit from the cache the earlier job
    wrote. It must therefore start after that job has finished.
    """
    if not cache_enabled:
        return {}
    seen: dict[tuple, list[tuple[str, set[int]]]] = {}
    out: dict[str, str] = {}
    for job in jobs:
        signature = chain_signature(job)
        for task_id, horizons in seen.get(signature, []):
            if set(job.horizons) <= horizons:
                out[job.task_id] = task_id
                break
        seen.setdefault(signature, []).append((job.task_id, set(job.horizons)))
    return out


@dataclass
class _Entry:
    job: ChainJob
    position: int
    cost: float
    depends_on: str | None
    done: threading.Event = field(default_factory=threading.Event)
    result: Any = None
    error: BaseException | None = None
    submitted: float | None = None
    finished: float | None = None


class ChainScheduler:
    """One pool for every rolling chain of a run; results handed out in any order."""

    def __init__(self, config: Config, identity: DataIdentity, cache: FitCache, *,
                 workers: int, monitor=None, reconcile_grace: float = 30.0) -> None:
        self.config = config
        self.identity = identity
        self.cache = cache
        self.workers = max(1, int(workers))
        self.monitor = monitor if (monitor is not None and getattr(monitor, "enabled", False)) \
            else None
        self.reconcile_grace = reconcile_grace
        self.entries: dict[str, _Entry] = {}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._pool: ProcessPoolExecutor | None = None
        self._queue = None
        self.started: float | None = None
        self.finished: float | None = None

    # -- lifecycle ---------------------------------------------------------

    def start(self, jobs: Sequence[ChainJob]) -> "ChainScheduler":
        missing = [j for j in jobs if not j.task_id]
        if missing:
            raise ValueError("every scheduled job needs a task_id")
        if len({j.task_id for j in jobs}) != len(jobs):
            raise ValueError("task_ids must be unique")
        dependencies = cache_dependencies(jobs, self.cache.enabled)
        for position, job in enumerate(jobs):
            self.entries[job.task_id] = _Entry(job, position, expected_cost(job),
                                               dependencies.get(job.task_id))
        if self.monitor is not None:
            self._queue = self.monitor.worker_channel()
            self.monitor.emit("batch_start", batch="pool", task_ids=[j.task_id for j in jobs])
        heartbeat = float(getattr(self.monitor, "worker_heartbeat_seconds", 30.0)) \
            if self.monitor is not None else 30.0
        self._pool = ProcessPoolExecutor(
            max_workers=self.workers, mp_context=multiprocessing.get_context(),
            initializer=_initializer,
            initargs=(self.config, self.identity, self.cache.directory, self.cache.enabled,
                      self._queue, heartbeat))
        self.started = time.time()
        self._thread = threading.Thread(target=self._dispatch, name="chain-dispatcher",
                                        daemon=True)
        self._thread.start()
        return self

    def close(self, *, cancel: bool = False) -> None:
        """Stop dispatching, shut the pool down and drain the progress channel.

        Normally called once every result has been consumed. With `cancel=True` (the run
        is failing or was interrupted) chains still running are terminated rather than
        waited for, since one can take hours.
        """
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=30)
        if self._pool is not None:
            if cancel:
                for process in list(getattr(self._pool, "_processes", {}).values()):
                    try:
                        process.terminate()
                    except Exception:
                        pass
            try:
                self._pool.shutdown(wait=True, cancel_futures=True)
            except Exception:
                pass
            self._pool = None
        if self.monitor is not None and self._queue is not None:
            self.monitor.close_channel(self._queue)
            self._queue = None
            self._reconcile(force=True)
            self.monitor.emit("batch_end", batch="pool")
        if self.finished is None:
            self.finished = time.time()

    # -- results -------------------------------------------------------------

    def has(self, jobs: Sequence[ChainJob]) -> bool:
        return bool(jobs) and all(j.task_id in self.entries for j in jobs)

    def results(self, jobs: Sequence[ChainJob]) -> list[tuple[Any, ChainResult]]:
        """The results of `jobs`, in the order given, waiting for any still running.

        The jobs must be the ones scheduled under those task ids: a mismatch is a
        programming error and is refused rather than silently answered with another
        chain's result.
        """
        out = []
        for job in jobs:
            entry = self.entries[job.task_id]
            if chain_signature(entry.job) != chain_signature(job) or \
                    tuple(entry.job.horizons) != tuple(job.horizons) or \
                    entry.job.tag != job.tag or not entry.job.y.equals(job.y):
                raise RuntimeError(f"job {job.task_id} differs from the scheduled one")
            while not entry.done.wait(timeout=1.0):
                if self._stop.is_set() and self._thread is not None \
                        and not self._thread.is_alive():
                    raise RuntimeError(f"scheduler stopped before {job.task_id} finished")
            if entry.error is not None:
                raise entry.error
            out.append(entry.result)
        return out

    # -- dispatcher ------------------------------------------------------------

    def _ready(self, entry: _Entry) -> bool:
        if entry.depends_on is None:
            return True
        prerequisite = self.entries[entry.depends_on]
        return prerequisite.done.is_set()

    def _dispatch(self) -> None:
        waiting = dict(self.entries)              # not yet submitted
        ready: list[tuple[float, int, str]] = []
        inflight: dict[Future, str] = {}
        self._pending_reconcile: list[tuple[str, float]] = []

        def promote() -> None:
            for task_id in list(waiting):
                entry = waiting[task_id]
                if not self._ready(entry):
                    continue
                prerequisite = self.entries.get(entry.depends_on) if entry.depends_on else None
                del waiting[task_id]
                if prerequisite is not None and prerequisite.error is not None:
                    entry.error = PrerequisiteFailed(
                        f"{task_id} not run: prerequisite {prerequisite.job.task_id} failed")
                    entry.finished = time.time()
                    entry.done.set()
                    continue
                # Most expensive first; consumption order breaks ties.
                heapq.heappush(ready, (-entry.cost, entry.position, task_id))

        promote()
        while not self._stop.is_set():
            while ready and len(inflight) < self.workers:
                _, _, task_id = heapq.heappop(ready)
                entry = self.entries[task_id]
                entry.submitted = time.time()
                try:
                    inflight[self._pool.submit(_execute, entry.job)] = task_id
                except Exception as exc:          # pool broken or shut down
                    entry.error, entry.finished = exc, time.time()
                    entry.done.set()
            if not inflight and not ready and not waiting:
                break
            if not inflight:
                promote()
                if not ready and waiting:
                    # Dependencies on chains that can never finish: fail them clearly.
                    for task_id, entry in list(waiting.items()):
                        entry.error = PrerequisiteFailed(f"{task_id}: prerequisite unavailable")
                        entry.done.set()
                        del waiting[task_id]
                continue
            done, _ = wait(list(inflight), timeout=0.5, return_when=FIRST_COMPLETED)
            for future in done:
                task_id = inflight.pop(future)
                entry = self.entries[task_id]
                entry.finished = time.time()
                try:
                    entry.result = future.result()
                    self._pending_reconcile.append((task_id, entry.finished))
                except BaseException as exc:
                    entry.error = exc
                    if self.monitor is not None:
                        self.monitor.chain_error(task_id, f"{type(exc).__name__}: {exc}")
                entry.done.set()
            promote()
            self._reconcile()
        self._reconcile(force=self._queue is None)
        self.finished = time.time()

    def _reconcile(self, force: bool = False) -> None:
        """Send each finished chain's authoritative counts to the monitor.

        A chain's own progress events travel on the queue and can arrive just after its
        result. The comparison waits until the chain's end event has been applied (or a
        grace period has passed), so a late event is never mistaken for a disagreement.
        """
        if self.monitor is None:
            return
        keep = []
        now = time.time()
        for task_id, finished in getattr(self, "_pending_reconcile", []):
            seen = self.monitor.chain_status(task_id) in ("done", "failed")
            if seen or force or now - finished > self.reconcile_grace:
                self.monitor.chain_result(task_id, self.entries[task_id].result[1])
            else:
                keep.append((task_id, finished))
        self._pending_reconcile = keep

    # -- measurement -----------------------------------------------------------

    def timings(self) -> list[dict[str, Any]]:
        rows = []
        for entry in self.entries.values():
            rows.append({"task_id": entry.job.task_id, "model": entry.job.spec.model,
                         "series": entry.job.series_name,
                         "window_length": entry.job.window_length,
                         "expected_cost": entry.cost, "depends_on": entry.depends_on,
                         "submitted": entry.submitted, "finished": entry.finished,
                         "seconds": (entry.finished - entry.submitted)
                         if entry.submitted and entry.finished else None,
                         "error": repr(entry.error) if entry.error else None})
        return rows
