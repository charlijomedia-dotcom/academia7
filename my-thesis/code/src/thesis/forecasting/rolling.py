"""The pseudo-out-of-sample engine (Part 5 §9, Comp §3).

One chain = one (series, model, specification, window length). For every forecast origin
the parameters are re-estimated on that origin's trailing window and forecasts are produced
at the approved horizons. The discrete specification is **not** re-searched: it was fixed
on the initial estimation window and stays fixed (Part 5 §9.2).

Three properties are structural rather than conventional:

* a window never reaches past its origin, so no future observation can enter an estimate;
* a failed fit produces a record and the chain continues, with no silent substitution
  (Part 5 §8.3);
* a missing required input produces a `DataGapEvent`, which is a property of the data and
  is deliberately kept out of the model failure registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

import numpy as np
import pandas as pd

from ..core.cache import CacheKey, FitCache
from ..core.config import Config
from ..core.schemas import DataGapEvent, FailureEvent, FitRecord, ReasonCode, Status
from ..models.registry import FitOutcome, ModelSpec, fit_and_forecast
from ..monitoring.probe import ChainReporter
from .windows import Origin, estimation_origins, horizon_coverage, targets_for


@dataclass
class DataIdentity:
    """What the cache key needs to know about the data behind a fit."""

    canonical_hash: str
    source_manifest_hash: str
    code_hash: str
    config_hash: str


@dataclass
class ChainResult:
    series: str
    spec: ModelSpec
    window_length: int
    forecasts: pd.DataFrame
    fit_records: list[FitRecord] = field(default_factory=list)
    failures: list[FailureEvent] = field(default_factory=list)
    data_gaps: list[DataGapEvent] = field(default_factory=list)
    attempted: int = 0
    valid: int = 0
    failed: int = 0
    from_cache: int = 0
    cache_horizon_misses: int = 0
    coverage: dict[int, dict] = field(default_factory=dict)

    def counts(self) -> dict[str, int]:
        return {
            "attempted_origins": self.attempted,
            "valid_origins": self.valid,
            "failed_origins": self.failed,
            "origins_from_cache": self.from_cache,
            "cache_horizon_misses": self.cache_horizon_misses,
        }

    def coverage_rows(self) -> list[dict[str, Any]]:
        """One row per horizon, so the audit shows each horizon's own reach."""
        rows = []
        for horizon in sorted(self.coverage):
            entry = self.coverage[horizon]
            realized = (self.forecasts[self.forecasts["horizon"] == horizon]
                        if not self.forecasts.empty else self.forecasts)
            rows.append({
                "series": self.series, "model": self.spec.model,
                "spec_label": self.spec.label, "window_length": self.window_length,
                "horizon": horizon,
                "n_eligible_origins": entry["n_origins"],
                "first_origin": entry["first_origin"],
                "last_origin": entry["last_origin"],
                "first_target": entry["first_target"],
                "last_target": entry["last_target"],
                "n_rows_emitted": len(realized),
                "n_finite_forecasts": (
                    int(realized["forecast"].notna().sum()) if len(realized) else 0),
            })
        return rows


def _cache_key(
    identity: DataIdentity,
    series: str,
    transformation: str,
    spec: ModelSpec,
    origin: Origin,
    predecessor_hash: str,
) -> CacheKey:
    return CacheKey(
        data_input_hash=identity.canonical_hash,
        source_manifest_hash=identity.source_manifest_hash,
        series=series,
        transformation=transformation,
        model=spec.model,
        specification=spec.as_dict(),
        window_start=origin.window_start.strftime("%Y-%m-%d"),
        window_end=origin.window_end.strftime("%Y-%m-%d"),
        refit_date=origin.origin_date.strftime("%Y-%m-%d"),
        code_hash=identity.code_hash,
        config_hash=identity.config_hash,
        predecessor_hash=predecessor_hash,
    )


def _payload(outcome: FitOutcome, horizons: Sequence[int]) -> dict[str, Any]:
    return {
        # The horizons this payload was produced for. A later run asking for a horizon
        # the payload does not carry must refit rather than silently read a missing
        # forecast as NaN; `_covers` enforces that on the way in.
        "horizons": sorted(int(h) for h in horizons),
        "forecasts": {str(h): v for h, v in outcome.forecasts.items()},
        "skeleton": {str(h): v for h, v in outcome.skeleton_forecasts.items()},
        "status": outcome.record.status.value,
        "reason_codes": [c.value for c in outcome.record.reason_codes],
        "converged": outcome.record.converged,
        "loglik": outcome.record.loglik,
        "aic": outcome.record.aic,
        "bic": outcome.record.bic,
        "n_obs": outcome.record.n_obs,
        "params": outcome.record.params,
        "start_used": outcome.record.start_used,
        "wall_seconds": outcome.record.wall_seconds,
        "warm_payload": (
            list(np.asarray(outcome.warm_payload, dtype=float).ravel())
            if outcome.warm_payload is not None else None
        ),
    }


def _covers(payload: dict, horizons: Sequence[int]) -> bool:
    """Whether a cached payload can serve every requested horizon.

    Reuse across horizon sets is sound because a forecast at horizon h does not depend on
    which other horizons were requested alongside it: AR, ARMA and MSAR iterate or
    recurse deterministically, and the STAR residual bootstrap draws one block of shocks
    per step from a seeded stream, so its first h means are identical whether 3 or 12
    steps were simulated. That prefix stability is asserted by a test rather than assumed.

    A payload written before this field existed carries no horizon list and is treated as
    not covering anything, so it is refitted instead of trusted.
    """
    stored = payload.get("horizons")
    if not isinstance(stored, list):
        return False
    return set(int(h) for h in horizons) <= set(int(h) for h in stored)


def _record_from_payload(payload: dict, spec: ModelSpec, series: str, origin: Origin) -> FitRecord:
    record = FitRecord(
        series=series, model=spec.model, spec_label=spec.label, spec_hash="",
        window_start=origin.window_start.strftime("%Y-%m-%d"),
        window_end=origin.window_end.strftime("%Y-%m-%d"),
        refit_date=origin.origin_date.strftime("%Y-%m-%d"),
        converged=bool(payload.get("converged", False)),
        loglik=payload.get("loglik"), aic=payload.get("aic"), bic=payload.get("bic"),
        n_obs=payload.get("n_obs"), params=payload.get("params", {}),
        start_used=payload.get("start_used"), wall_seconds=payload.get("wall_seconds"),
    )
    record.status = Status(payload.get("status", "adequate"))
    record.reason_codes = [ReasonCode(c) for c in payload.get("reason_codes", [])]
    return record


def run_chain(
    series_name: str,
    y: pd.Series,
    spec: ModelSpec,
    horizons: Sequence[int],
    window_length: int,
    config: Config,
    *,
    frequency: str = "M",
    transformation: str = "",
    identity: DataIdentity | None = None,
    cache: FitCache | None = None,
    max_origins: int | None = None,
    warm_starts: bool | None = None,
    task_id: str | None = None,
) -> ChainResult:
    """Run every forecast origin for one model on one window length.

    `task_id` only labels progress events (`monitoring.probe`). The reporter reads values
    the loop has already computed and never feeds anything back, so the numbers are the
    same with or without a monitor (asserted by a test).
    """
    horizons = sorted(set(int(h) for h in horizons))
    index = pd.DatetimeIndex(y.index)
    # Bounded by the SHORTEST horizon, not the longest: one fit serves every horizon, so
    # requesting h=12 alongside h=1 must not discard the late origins at which h=1 still
    # has a realized target (Part 5 §9.4 makes h=1 the primary exercise).
    origins = estimation_origins(index, window_length, horizons, max_origins=max_origins)
    use_warm = config.get("forecasting.warm_starts", True) if warm_starts is None else warm_starts

    rows: list[dict[str, Any]] = []
    records: list[FitRecord] = []
    failures: list[FailureEvent] = []
    gaps: list[DataGapEvent] = []
    result = ChainResult(series_name, spec, window_length, pd.DataFrame())
    warm_payload: Any = None
    predecessor_hash = ""

    reporter = ChainReporter(
        task_id or f"{series_name}|{spec.model}|w{window_length}", len(origins),
        series=series_name, model=spec.model, spec_label=spec.label,
        window_length=int(window_length), horizons=list(horizons),
        plan={"task_id": task_id or f"{series_name}|{spec.model}|w{window_length}",
              "batch": "unplanned", "stage": "", "exercise": "unplanned",
              "role": "baseline", "series": series_name, "model": spec.model,
              "spec_label": spec.label, "k_regimes": spec.k_regimes,
              "window_length": int(window_length), "frequency": frequency,
              "horizons": list(horizons), "n_origins": len(origins)})
    reporter.start()
    for position, origin in enumerate(origins, start=1):
        window = y.iloc[origin.estimation_slice()]
        result.attempted += 1
        reporter.origin_start(position, origin.origin_date, origin.window_start,
                              origin.window_end)

        # A gap in the estimation window or in a required target is a data condition,
        # recorded separately so no model is charged for it.
        if not np.isfinite(window.to_numpy(dtype=float)).all():
            missing = [d.strftime("%Y-%m-%d")
                       for d in pd.DatetimeIndex(window.index)[~np.isfinite(window.to_numpy(float))]]
            gaps.append(DataGapEvent(series_name, spec.model,
                                     origin.origin_date.strftime("%Y-%m-%d"), None,
                                     tuple(missing), "estimation_window",
                                     "required observations missing from the window"))
            reporter.origin_end("gap")
            continue

        key = None
        payload = None
        if cache is not None and identity is not None:
            key = _cache_key(identity, series_name, transformation, spec, origin, predecessor_hash)
            payload = cache.get(key)
            if payload is not None and not _covers(payload, horizons):
                # The cached fit is for this window but was produced for a narrower set
                # of horizons. Refit rather than report a missing horizon as NaN.
                payload = None
                result.cache_horizon_misses += 1

        if payload is not None:
            record = _record_from_payload(payload, spec, series_name, origin)
            forecasts = {int(h): v for h, v in payload["forecasts"].items()}
            skeleton = {int(h): v for h, v in payload.get("skeleton", {}).items()}
            warm_payload = (np.asarray(payload["warm_payload"], dtype=float)
                            if payload.get("warm_payload") is not None else None)
            result.from_cache += 1
        else:
            outcome = fit_and_forecast(
                spec, window, horizons, config, frequency=frequency, series=series_name,
                refit_date=origin.origin_date.strftime("%Y-%m-%d"),
                warm_start=warm_payload if use_warm else None,
                seed_key={"series": series_name, "model": spec.model,
                          "spec": spec.label, "origin": origin.origin_date.strftime("%Y-%m-%d")},
            )
            record = outcome.record
            forecasts = outcome.forecasts
            skeleton = outcome.skeleton_forecasts
            if outcome.usable and outcome.warm_payload is not None:
                warm_payload = outcome.warm_payload
            if key is not None and cache is not None:
                cache.put(key, _payload(outcome, horizons))

        records.append(record)
        if record.status is Status.FAILED:
            result.failed += 1
            for code in record.reason_codes or [ReasonCode.NONCONVERGENCE]:
                failures.append(FailureEvent(
                    series=series_name, model=spec.model,
                    refit_date=origin.origin_date.strftime("%Y-%m-%d"), horizon=None,
                    category=Status.FAILED, reason_code=code,
                    raw_diagnostic=str(record.diagnostics.get(f"flag_{code.value}",
                                                              record.optimizer_message or ""))[:200],
                    forecast_retained=False, figure_separated=True,
                ))
        else:
            result.valid += 1
            for code in record.reason_codes:
                failures.append(FailureEvent(
                    series=series_name, model=spec.model,
                    refit_date=origin.origin_date.strftime("%Y-%m-%d"), horizon=None,
                    category=Status.FRAGILE, reason_code=code,
                    raw_diagnostic=str(record.diagnostics.get(f"flag_{code.value}", ""))[:200],
                    forecast_retained=True,
                    figure_separated=code is ReasonCode.EXTREME_FORECAST,
                ))

        # Warm starts make the chain path dependent, so the successor's cache key records
        # which predecessor it started from (risk R5).
        predecessor_hash = ""
        if use_warm and warm_payload is not None:
            predecessor_hash = f"{np.round(np.asarray(warm_payload, float).ravel(), 10).tolist()}"

        rows_before = len(rows)
        for horizon, target_position, _ in targets_for(origin, horizons, index):
            actual = float(y.iloc[target_position])
            forecast = forecasts.get(horizon, np.nan)
            rows.append({
                "series": series_name,
                "model": spec.model,
                "spec_label": spec.label,
                "window_length": window_length,
                "origin_date": origin.origin_date,
                "target_date": index[target_position],
                "horizon": horizon,
                "forecast": float(forecast) if forecast is not None else np.nan,
                "actual": actual,
                "error": (actual - float(forecast)) if np.isfinite(forecast) else np.nan,
                "status": record.status.value,
                "reason_codes": ";".join(c.value for c in record.reason_codes),
                "skeleton_forecast": skeleton.get(horizon, np.nan),
            })
        reporter.origin_end("failed" if record.status is Status.FAILED else "valid",
                            from_cache=payload is not None, n_records=len(rows) - rows_before)

    result.forecasts = pd.DataFrame(rows)
    result.coverage = horizon_coverage(index, window_length, horizons,
                                       max_origins=max_origins)
    result.fit_records = records
    result.failures = failures
    result.data_gaps = gaps
    reporter.end(attempted=result.attempted, valid=result.valid, failed=result.failed,
                 from_cache=result.from_cache, n_records=len(rows), gaps=len(gaps))
    return result
