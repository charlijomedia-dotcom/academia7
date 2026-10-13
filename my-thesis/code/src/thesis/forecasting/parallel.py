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
"""

from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Any, Sequence

import pandas as pd

from ..core.cache import FitCache
from ..core.config import Config
from ..models.registry import ModelSpec
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


def _single_threaded_blas() -> None:
    """Keep each worker to one BLAS thread.

    Without this, four worker processes each spawn four BLAS threads on a four-core box
    and spend more time contending than computing.
    """
    for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                     "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[variable] = "1"


_WORKER_STATE: dict[str, Any] = {}


def _initializer(config: Config, identity: DataIdentity, cache_directory, cache_enabled: bool):
    _single_threaded_blas()
    _WORKER_STATE["config"] = config
    _WORKER_STATE["identity"] = identity
    _WORKER_STATE["cache"] = FitCache(cache_directory, enabled=cache_enabled)


def _execute(job: ChainJob) -> tuple[Any, ChainResult]:
    return job.tag, run_chain(
        job.series_name, job.y, job.spec, list(job.horizons), job.window_length,
        _WORKER_STATE["config"], frequency=job.frequency,
        transformation=job.transformation, identity=_WORKER_STATE["identity"],
        cache=_WORKER_STATE["cache"], max_origins=job.max_origins)


def run_chains(
    jobs: Sequence[ChainJob],
    config: Config,
    identity: DataIdentity,
    cache: FitCache,
    *,
    workers: int | None = None,
) -> list[tuple[Any, ChainResult]]:
    """Run every job and return (tag, result) pairs in the order the jobs were given.

    With one worker the jobs run in this process, which keeps debugging and profiling
    straightforward and is the behaviour the tests compare against.
    """
    if not jobs:
        return []
    workers = int(config.get("execution.parallel_workers", 1)) if workers is None else workers
    workers = max(1, min(workers, len(jobs)))

    if workers == 1:
        return [(job.tag, run_chain(
            job.series_name, job.y, job.spec, list(job.horizons), job.window_length,
            config, frequency=job.frequency, transformation=job.transformation,
            identity=identity, cache=cache, max_origins=job.max_origins)) for job in jobs]

    results: dict[int, tuple[Any, ChainResult]] = {}
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=_initializer,
        initargs=(config, identity, cache.directory, cache.enabled),
    ) as pool:
        futures = {pool.submit(_execute, job): position for position, job in enumerate(jobs)}
        for future in futures:
            results[futures[future]] = future.result()
    return [results[position] for position in range(len(jobs))]
