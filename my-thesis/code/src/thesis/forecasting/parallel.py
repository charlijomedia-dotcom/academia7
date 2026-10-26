"""Run independent rolling-forecast chains concurrently.

Parallelism is applied at the level of a whole chain — one (series, model, window
length) triple — and never inside one. That boundary matters for reproducibility:

* every fit draws its randomness from a seed derived from the series, model,
  specification and origin date (`core.seeds`), never from a shared stream, so a fit's
  result does not depend on how many other fits ran before it;
* warm starts make a chain path dependent, so a chain is executed start to finish inside
  a single worker and its origins are never reordered.

Together these mean a parallel run and a serial run produce identical numbers. That is
asserted by a test rather than assumed.

Progress monitoring rides alongside without touching that boundary: each worker sends its
progress events to the parent on a queue (`monitoring.monitor.Monitor.worker_channel`),
and a liveness thread in the worker reports its CPU time while a fit is running. Only the
parent writes to the console or a log, so workers can never interleave messages.
"""

from __future__ import annotations

import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Any, Sequence

import pandas as pd

from ..core.cache import FitCache
from ..core.config import Config
from ..models.registry import ModelSpec
from ..monitoring import probe
from .rolling import ChainResult, DataIdentity, run_chain


@dataclass(frozen=True)
class ChainJob:
    """One chain to run. `tag` is the caller's label, returned untouched."""

    tag: Any
    series_name: str
    y: pd.Series
    spec: ModelSpec
    horizons: tuple[int, ...]
    window_length: int
    frequency: str
    transformation: str
    max_origins: int | None = None
    task_id: str = ""             # progress-reporting label only; never read by a fit


def _single_threaded_blas() -> None:
    """Keep each worker to one BLAS thread.

    Without this, four worker processes each spawn four BLAS threads on a four-core box
    and spend more time contending than computing.
    """
    for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                     "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[variable] = "1"


_WORKER_STATE: dict[str, Any] = {}


def _initializer(config: Config, identity: DataIdentity, cache_directory, cache_enabled: bool,
                 progress_queue=None, heartbeat_seconds: float = 30.0):
    _single_threaded_blas()
    _WORKER_STATE["config"] = config
    _WORKER_STATE["identity"] = identity
    _WORKER_STATE["cache"] = FitCache(cache_directory, enabled=cache_enabled)
    if progress_queue is not None:
        probe.install(probe.queue_sink(progress_queue))
        probe.start_worker_heartbeat(heartbeat_seconds)
    else:
        # A forked worker inherits the parent's module state; a parent-side sink must
        # not be called from a child process.
        probe.uninstall()


def _execute(job: ChainJob) -> tuple[Any, ChainResult]:
    return job.tag, run_chain(
        job.series_name, job.y, job.spec, list(job.horizons), job.window_length,
        _WORKER_STATE["config"], frequency=job.frequency,
        transformation=job.transformation, identity=_WORKER_STATE["identity"],
        cache=_WORKER_STATE["cache"], max_origins=job.max_origins,
        task_id=job.task_id or None)


def run_chains(
    jobs: Sequence[ChainJob],
    config: Config,
    identity: DataIdentity,
    cache: FitCache,
    *,
    workers: int | None = None,
    monitor=None,
) -> list[tuple[Any, ChainResult]]:
    """Run every job and return (tag, result) pairs in the order the jobs were given.

    With one worker the jobs run in this process, which keeps debugging and profiling
    straightforward and is the behaviour the tests compare against.

    `monitor`, when given, receives every chain's progress events and the authoritative
    counts of each returned result. It has no influence on what is computed.
    """
    if not jobs:
        return []
    workers = int(config.get("execution.parallel_workers", 1)) if workers is None else workers
    workers = max(1, min(workers, len(jobs)))
    report = monitor is not None and getattr(monitor, "enabled", False)

    def finished(job: ChainJob, result: ChainResult) -> None:
        if report and job.task_id:
            monitor.chain_result(job.task_id, result)

    def errored(job: ChainJob, exc: BaseException) -> None:
        if report and job.task_id:
            monitor.chain_error(job.task_id, f"{type(exc).__name__}: {exc}")

    if workers == 1:
        out = []
        for job in jobs:
            try:
                result = run_chain(
                    job.series_name, job.y, job.spec, list(job.horizons), job.window_length,
                    config, frequency=job.frequency, transformation=job.transformation,
                    identity=identity, cache=cache, max_origins=job.max_origins,
                    task_id=job.task_id or None)
            except BaseException as exc:
                errored(job, exc)
                raise
            finished(job, result)
            out.append((job.tag, result))
        return out

    queue = monitor.worker_channel() if report else None
    heartbeat = float(getattr(monitor, "worker_heartbeat_seconds", 30.0)) if report else 30.0
    results: dict[int, tuple[Any, ChainResult]] = {}
    try:
        with ProcessPoolExecutor(
            max_workers=workers,
            mp_context=multiprocessing.get_context(),
            initializer=_initializer,
            initargs=(config, identity, cache.directory, cache.enabled, queue, heartbeat),
        ) as pool:
            futures = {pool.submit(_execute, job): position
                       for position, job in enumerate(jobs)}
            for future in futures:
                job = jobs[futures[future]]
                try:
                    results[futures[future]] = future.result()
                except BaseException as exc:
                    errored(job, exc)
                    raise
    finally:
        if queue is not None:
            monitor.close_channel(queue)
    for position, job in enumerate(jobs):
        finished(job, results[position][1])
    return [results[position] for position in range(len(jobs))]
