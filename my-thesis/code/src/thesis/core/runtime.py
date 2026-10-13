"""Runtime accounting (Comp §9).

Every stage logs wall-clock and CPU time, how many fits were attempted, reused from cache
or failed, and peak memory where available. The purpose is to find the real bottlenecks
rather than assume the nonlinear models are the slow part.
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

try:
    import psutil
except ImportError:                                    # pragma: no cover
    psutil = None


@dataclass
class StageTiming:
    stage: str
    wall_seconds: float = 0.0
    cpu_seconds: float = 0.0
    fits_attempted: int = 0
    fits_from_cache: int = 0
    failures: int = 0
    peak_memory_mb: float | None = None
    notes: str = ""

    def to_row(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "wall_seconds": round(self.wall_seconds, 3),
            "cpu_seconds": round(self.cpu_seconds, 3),
            "fits_attempted": self.fits_attempted,
            "fits_from_cache": self.fits_from_cache,
            "failures": self.failures,
            "peak_memory_mb": None if self.peak_memory_mb is None else round(self.peak_memory_mb, 1),
            "notes": self.notes,
        }


@dataclass
class RuntimeLog:
    timings: list[StageTiming] = field(default_factory=list)

    @contextmanager
    def stage(self, name: str):
        timing = StageTiming(stage=name)
        wall0, cpu0 = time.perf_counter(), time.process_time()
        try:
            yield timing
        finally:
            timing.wall_seconds = time.perf_counter() - wall0
            timing.cpu_seconds = time.process_time() - cpu0
            if psutil is not None:
                try:
                    timing.peak_memory_mb = psutil.Process(os.getpid()).memory_info().rss / 1e6
                except Exception:
                    timing.peak_memory_mb = None
            self.timings.append(timing)

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame([t.to_row() for t in self.timings])
