"""Per-chain cache-replay assessment for the R1 pending chains (reads the cache only).

For each rolling chain that the published release does not contain, `classify_chain`
walks the chain origin by origin with the rolling engine's own cache-key function and
reports what the original fit cache holds:

* hit                 -- a payload exists for the exact key and covers the horizons;
* miss / horizon_miss -- no payload, or one for fewer horizons;
* unknown_after_miss  -- warm-started models only (MSAR, STAR): after the first miss the
                         next keys depend on the refit's parameters, so they cannot be
                         looked up (they would be served only if a refit reproduced the
                         original fit bit for bit, which is not assumed);
* refit_rejected      -- a payload carrying the R1 refit marker found in the original
                         cache (it is never accepted as an original estimate);
* gap                 -- missing data in the window (never fitted).

`verify_replay` then runs the real rolling engine over every chain classified complete,
with estimation disabled (`PublishedRescorer._replay_from_cache`), and confirms that it
returns the whole chain. Nothing is estimated and nothing is written to the cache.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass

import numpy as np

from ..core.cache import code_hash
from ..core.hashing import sha256_file
from ..forecasting.rolling import _cache_key, _covers
from ..forecasting.windows import estimation_origins
from .rescore import REFIT_MARKER

WARM_MODELS = {"MSAR", "MSAR3", "STAR"}

#: The chains whose published rows a correction changes but whose forecasts were never
#: published (r1_validation_report.md §4). Every other non-published chain is unaffected.
PENDING_RULES = (
    ("T4.1:", "T4.1 alternative transformation: AR chain has FAILED fits with finite "
              "forecasts that were scored (F1)"),
    ("T4.2:", "T4.2 CPI AR lags: the p=12 chain has a FAILED fit that was scored; the lag "
              "variants are compared on common dates (F1)"),
    ("T4.8:UNRATE|180:", "T4.8 UNRATE 180 months: the AR chain has a FAILED fit that was "
                         "scored (F1)"),
    ("T4.8:UNRATE|300:", "T4.8 UNRATE 300 months: the AR chain has a FAILED fit that was "
                         "scored (F1)"),
)


def pending_reason(task_id: str) -> str | None:
    for prefix, reason in PENDING_RULES:
        if task_id.startswith(prefix):
            return reason
    return None


def identity_string(config) -> str:
    """The 16-character identity naming the cache folder (as `colab.cache_identity`)."""
    from ..core.paths import FROZEN_DIR
    csv = FROZEN_DIR / "thesis_input_2026-10-05.csv"
    parts = {"code": code_hash(), "config": config.hash, "data": sha256_file(csv)}
    return hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:16]


@dataclass
class ChainAssessment:
    task_id: str
    series: str
    model: str
    spec: str
    transformation: str
    window_length: int
    horizons: list
    planned_origins: int
    hit: int = 0
    miss: int = 0
    horizon_miss: int = 0
    unknown_after_miss: int = 0
    refit_rejected: int = 0
    gap: int = 0
    first_miss: str | None = None

    @property
    def complete(self) -> bool:
        return self.hit + self.gap == self.planned_origins

    def as_dict(self) -> dict:
        out = dict(self.__dict__)
        out["complete_in_cache"] = self.complete
        out["missing_origins"] = self.miss + self.horizon_miss + self.refit_rejected
        return out


def classify_chain(job, cache, identity, config) -> ChainAssessment:
    """Walk one chain's keys through the cache; no fitting, no writing."""
    horizons = sorted(set(int(h) for h in job.horizons))
    origins = estimation_origins(job.y.index, job.window_length, horizons,
                                 max_origins=job.max_origins)
    use_warm = bool(config.get("forecasting.warm_starts", True))
    counts: Counter = Counter()
    first_miss, broken, predecessor = None, False, ""
    for origin in origins:
        window = job.y.iloc[origin.estimation_slice()]
        if not np.isfinite(window.to_numpy(dtype=float)).all():
            counts["gap"] += 1
            continue
        if broken:
            counts["unknown_after_miss"] += 1
            continue
        key = _cache_key(identity, job.series_name, job.transformation, job.spec, origin,
                         predecessor)
        path = cache.path_for(key)
        payload = None
        if path.exists():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                payload = None
        warm = None
        if payload is not None and REFIT_MARKER in payload:
            counts["refit_rejected"] += 1
            payload, rejected = None, True
        else:
            rejected = False
        if payload is not None and _covers(payload, horizons):
            counts["hit"] += 1
            if payload.get("warm_payload") is not None:
                warm = np.asarray(payload["warm_payload"], dtype=float)
        else:
            if not rejected:
                counts["horizon_miss" if payload is not None else "miss"] += 1
            first_miss = first_miss or origin.origin_date.strftime("%Y-%m-%d")
            if job.spec.model in WARM_MODELS and use_warm:
                broken = True
        predecessor = ""
        if use_warm and warm is not None:
            predecessor = f"{np.round(np.asarray(warm, float).ravel(), 10).tolist()}"
    return ChainAssessment(
        task_id=job.task_id, series=job.series_name, model=job.spec.model,
        spec=job.spec.label, transformation=job.transformation,
        window_length=int(job.window_length), horizons=horizons,
        planned_origins=len(origins), first_miss=first_miss,
        **{k: counts.get(k, 0) for k in ("hit", "miss", "horizon_miss",
                                         "unknown_after_miss", "refit_rejected", "gap")})


def verify_replay(rescorer, job) -> tuple[bool, int]:
    """Replay the whole chain through the rolling engine with estimation disabled.

    Returns (replayed, origins served from the cache). A chain that is not complete
    returns (False, 0): the engine stops at the first miss and nothing is used.
    """
    chain = rescorer._replay_from_cache(job)
    if chain is None:
        return False, 0
    return True, int(chain.from_cache)
