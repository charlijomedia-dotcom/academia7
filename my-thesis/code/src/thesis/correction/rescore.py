"""R1 correction workflow: correct the Part 8 evidence from the published forecasts.

Approved 2 November 2026 (Option R1). The completed rolling experiment of run
`baseline-20261030T173044-949fcd76` is **not** repeated. The workflow:

1. reads the original published outputs (the immutable results commit
   `066294544e8ff84f3c2c73ab647c8d13331dcac1`, `my-thesis/output/`) -- never writes them;
2. rebuilds the pipeline's in-memory state from them: the stationarity decisions are
   recomputed (deterministic tests, needed for F4/F7.1), the discrete specifications are
   **read** from the published T2.4/T2.5 (no re-selection), and every baseline rolling
   chain is rebuilt from the published forecast Parquet files and origin audit (no
   re-estimation);
3. runs the pipeline's own evaluation and robustness code on that state -- the same
   functions that produced the original tables, so a legacy run (every correction
   switched off, `correction.flags.legacy`) must reproduce the original tables exactly,
   which is the validation gate before any correction is activated;
4. for a robustness chain whose forecasts were never published (T4.1 alternative
   transformations, T4.2 CPI lags, T4.8 non-baseline window lengths) it uses, in order:
   the restored fit cache, replayed through the rolling engine with estimation disabled
   (an *original* estimate, served whole or not at all); a new estimation only if that
   chain was explicitly approved (provenance `re-estimated`); otherwise the original
   rows are retained and marked, never silently mixed;
5. leaves every output the corrections cannot change byte-identical to the original.

Chain provenance is recorded per chain (`published`, `cache`, `re-estimated`), and a
chain is never assembled from a mixture of original and re-estimated fits.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable

import numpy as np
import pandas as pd

from ..core.provenance import PROVENANCE_COLUMNS
from ..core.schemas import ReasonCode, Status
from ..evaluation.scoring import mask_failed
from ..forecasting import rolling
from ..forecasting.rolling import ChainResult
from ..forecasting.windows import horizon_coverage
from ..models.registry import AR, ARMA, MSAR, MSAR3, STAR, ModelSpec
from ..pipeline import StageOutputs, Pipeline

ORIGINAL_RUN_ID = "baseline-20261030T173044-949fcd76"
ORIGINAL_COMMIT = "066294544e8ff84f3c2c73ab647c8d13331dcac1"

#: Tables the R1 workflow regenerates (relative to the output root). Everything else is
#: copied byte-for-byte from the original publication.
EVALUATION_TABLES = (
    "forecast_tests/T3.3_main_forecast_table.csv",
    "forecast_tests/T3.3A_hlz_pairwise.csv",
    "forecast_tests/T3.3B_dm_hln_pairwise.csv",
    "forecast_tests/T3.4_model_confidence_set.csv",
    "forecast_tests/T3.5_state_performance.csv",
    "forecast_tests/T3.5_state_loss_regression.csv",
    "forecast_tests/T3.6_peak_trough_detail.csv",
    "robustness/T4.TP1_turning_window_sensitivity.csv",
)


class ChainUnavailable(RuntimeError):
    """A chain needed by an exercise has no published, cached or approved source."""

    def __init__(self, task_ids: list[str]):
        super().__init__("no source for chain(s): " + ", ".join(task_ids))
        self.task_ids = task_ids


class _NoEstimation(RuntimeError):
    """Raised inside the rolling engine when a cache replay would have to fit."""


def _strip(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.drop(columns=[c for c in PROVENANCE_COLUMNS if c in frame.columns])


@dataclass
class ChainSource:
    task_id: str
    source: str                 # published | cache | re-estimated | unavailable
    detail: str = ""


@dataclass
class RescoreRecord:
    chain_sources: list[ChainSource] = field(default_factory=list)
    retained: list[dict[str, Any]] = field(default_factory=list)   # rows kept from original
    notes: list[str] = field(default_factory=list)


def chain_from_published(series: str, spec: ModelSpec, window_length: int,
                         forecasts: pd.DataFrame, audit_row: pd.Series,
                         horizons: Iterable[int], frequency_index: pd.DatetimeIndex,
                         from_cache: int | None = None) -> ChainResult:
    """A ChainResult equivalent to the one the original run held in memory.

    Forecast rows come from the published Parquet file (provenance columns removed).
    Per-origin fit status and reason codes are those printed on the forecast rows; the
    failure events are rebuilt exactly as `rolling.run_chain` emits them (one event per
    reason code; a failed fit without codes counts as NONCONVERGENCE). Counts come from
    the published origin audit.
    """
    horizons = sorted(int(h) for h in horizons)
    frame = _strip(forecasts)
    frame = frame[(frame["model"] == spec.model) & (frame["horizon"].isin(horizons))]
    frame = frame.reset_index(drop=True)
    per_origin = (frame.sort_values(["origin_date", "horizon"])
                  .drop_duplicates("origin_date")[["origin_date", "status", "reason_codes"]])
    records, failures = [], []
    for _, row in per_origin.iterrows():
        status = Status(str(row["status"]))
        codes = [ReasonCode(c) for c in str(row["reason_codes"] or "").split(";") if c]
        records.append(SimpleNamespace(status=status, reason_codes=codes))
        if status is Status.FAILED:
            for code in codes or [ReasonCode.NONCONVERGENCE]:
                failures.append(SimpleNamespace(category=Status.FAILED, reason_code=code))
        else:
            for code in codes:
                failures.append(SimpleNamespace(category=Status.FRAGILE, reason_code=code))
    result = ChainResult(series=series, spec=spec, window_length=window_length,
                         forecasts=frame)
    result.fit_records = records
    result.failures = failures
    result.attempted = int(audit_row["attempted_origins"])
    result.valid = int(audit_row["valid_origins"])
    result.failed = int(audit_row["failed_origins"])
    result.from_cache = int(audit_row["origins_from_cache"] if from_cache is None
                            else from_cache)
    result.cache_horizon_misses = int(audit_row.get("cache_horizon_misses", 0) or 0)
    result.coverage = horizon_coverage(frequency_index, window_length, horizons)
    return result


class PublishedRescorer(Pipeline):
    """The pipeline, fed from the published outputs instead of re-estimating."""

    def __init__(self, config, context, layout, bundle, *, original: Path,
                 approved_estimation: Iterable[str] = (), use_cache: bool = True,
                 monitor=None):
        super().__init__(config, context, layout, bundle, monitor=monitor, workers=1)
        self.original = Path(original)
        self.approved_estimation = set(approved_estimation)
        self.use_cache = use_cache
        self.record = RescoreRecord()
        self.regenerated: list[str] = []
        self._published: dict[str, pd.DataFrame] = {}

    # -- published state ---------------------------------------------------

    def _original_table(self, relative: str) -> pd.DataFrame:
        path = self.original / relative
        if path.suffix == ".parquet":
            return pd.read_parquet(path)
        return pd.read_csv(path)

    def load_specifications(self) -> None:
        """Discrete specifications exactly as published in T2.4/T2.5 (no re-selection)."""
        t25 = self._original_table("diagnostics/T2.5_selected_specs.csv")
        for _, row in t25.iterrows():
            series_id = row["series_id"]
            if series_id not in self.targets:
                continue
            p, q = (int(v) for v in re.findall(r"-?\d+", str(row["arma_order"])))
            msar_order = int(row["msar_lag_after_cap"])
            self.specs[series_id] = {
                AR: ModelSpec(AR, order=int(row["ar_lag"])),
                ARMA: ModelSpec(ARMA, order=p, ma_order=q),
                MSAR: ModelSpec(MSAR, order=msar_order, k_regimes=2),
                MSAR3: ModelSpec(MSAR3, order=msar_order, k_regimes=3),
                STAR: ModelSpec(STAR, order=int(row["star_lag_after_cap"]),
                                kind=str(row["star_type"]), delay=int(row["star_delay"])),
            }

    def _forecasts(self, series_id: str) -> pd.DataFrame:
        if series_id not in self._published:
            frame = self._original_table(f"forecasts/forecasts_{series_id}.parquet")
            for column in ("origin_date", "target_date"):
                frame[column] = pd.to_datetime(frame[column]).astype("datetime64[ns]")
            frame["reason_codes"] = frame["reason_codes"].fillna("")
            self._published[series_id] = frame
        return self._published[series_id]

    def load_baseline_chains(self) -> None:
        """Every baseline rolling chain, rebuilt from the published forecasts."""
        audit = self._original_table("forecasts/forecast_origin_audit.csv")
        self.forecasts, self.chain_results = {}, {}
        for series_id in self._selected_targets():
            frequency = self.frequency[series_id]
            self.forecasts[series_id], self.chain_results[series_id] = {}, {}
            for model in (AR, ARMA, MSAR, STAR):
                spec = self.specs[series_id][model]
                row = audit[(audit["series"] == series_id) & (audit["model"] == model)].iloc[0]
                if str(row["spec_label"]) != spec.label:
                    raise RuntimeError(f"{series_id} {model}: published spec "
                                       f"{row['spec_label']} differs from {spec.label}")
                chain = chain_from_published(
                    series_id, spec, self._window(frequency), self._forecasts(series_id), row,
                    self._horizons(frequency), pd.DatetimeIndex(self.targets[series_id].index))
                chain.forecasts = mask_failed(chain.forecasts)
                self.forecasts[series_id][model] = chain.forecasts
                self.chain_results[series_id][model] = chain
                self.record.chain_sources.append(ChainSource(
                    f"forecasting:{series_id}|{model}", "published",
                    f"forecasts/forecasts_{series_id}.parquet"))

    def write_forecast_files(self) -> StageOutputs:
        """forecasts_*.csv/.parquet and the horizon coverage, from the rebuilt chains."""
        stage = StageOutputs("forecasts")
        coverage = []
        for series_id in self._selected_targets():
            combined = pd.concat([f for f in self.forecasts[series_id].values() if not f.empty],
                                 ignore_index=True)
            self._write(combined, self.layout.forecasts, f"forecasts_{series_id}.csv",
                        stage, parquet=True)
            for chain in self.chain_results[series_id].values():
                coverage.extend(chain.coverage_rows())
        self._write(pd.DataFrame(coverage), self.layout.forecasts,
                    "forecast_horizon_coverage.csv", stage)
        self.stage_outputs.append(stage)
        return stage

    # -- chains for the robustness exercises --------------------------------

    def _baseline_equivalent(self, job) -> ChainResult | None:
        """The published chain a robustness job re-reads (same series, data, spec, window)."""
        series_id = job.series_name
        if series_id not in self.chain_results:
            return None
        frequency = self.frequency[series_id]
        if (job.window_length != self._window(frequency)
                or job.transformation != self._units(series_id)):
            return None
        for chain in self.chain_results[series_id].values():
            if chain.spec == job.spec and set(job.horizons) <= set(self._horizons(frequency)):
                if not job.y.equals(self.targets[series_id]):
                    return None
                return chain
        return None

    def _replay_from_cache(self, job) -> ChainResult | None:
        """The whole chain from the fit cache through the rolling engine, or None.

        Estimation is disabled for the duration of the replay: if any origin is missing
        from the cache the replay stops and nothing from it is used, so a chain is never
        a mixture of original and new fits.
        """
        if not self.use_cache or not self.cache.enabled:
            return None
        original = rolling.fit_and_forecast

        def refuse(*args, **kwargs):
            raise _NoEstimation()

        rolling.fit_and_forecast = refuse
        try:
            return rolling.run_chain(
                job.series_name, job.y, job.spec, job.horizons, job.window_length,
                self.config, frequency=job.frequency, transformation=job.transformation,
                identity=self.identity, cache=self.cache, max_origins=job.max_origins,
                task_id=job.task_id)
        except _NoEstimation:
            return None
        finally:
            rolling.fit_and_forecast = original

    def _chains(self, jobs, batch: str = ""):
        results, missing = [], []
        window_audit = None
        for job in jobs:
            chain, source, detail = None, "", ""
            published = self._baseline_equivalent(job)
            if published is not None:
                if window_audit is None:
                    window_audit = self._original_table(
                        "robustness/window_length_origin_audit.csv")
                match = window_audit[(window_audit["series"] == job.series_name)
                                     & (window_audit["model"] == job.spec.model)
                                     & (window_audit["window_length"] == job.window_length)]
                chain = ChainResult(published.series, published.spec, published.window_length,
                                    published.forecasts.copy())
                chain.__dict__.update({k: v for k, v in published.__dict__.items()
                                       if k not in ("forecasts",)})
                chain.forecasts = published.forecasts[
                    published.forecasts["horizon"].isin(job.horizons)].reset_index(drop=True)
                if task_is_window(job) and len(match):
                    chain.from_cache = int(match.iloc[0]["from_cache"])
                source, detail = "published", "baseline chain re-read"
            if chain is None:
                chain = self._replay_from_cache(job)
                if chain is not None:
                    source, detail = "cache", "original estimate served whole from the fit cache"
            if chain is None and job.task_id in self.approved_estimation:
                chain = rolling.run_chain(
                    job.series_name, job.y, job.spec, job.horizons, job.window_length,
                    self.config, frequency=job.frequency, transformation=job.transformation,
                    identity=None, cache=None, max_origins=job.max_origins,
                    task_id=job.task_id)
                chain.forecasts = chain.forecasts.assign(forecast_provenance="re-estimated")
                source, detail = "re-estimated", "approved new estimation (platform-dependent)"
            if chain is None:
                missing.append(job.task_id)
                continue
            chain.forecasts = mask_failed(chain.forecasts)
            self.record.chain_sources.append(ChainSource(job.task_id, source, detail))
            results.append((job.tag, chain))
        if missing:
            for task_id in missing:
                self.record.chain_sources.append(ChainSource(task_id, "unavailable",
                                                             "not published, not cached, "
                                                             "not approved for estimation"))
            raise ChainUnavailable(missing)
        return results


def task_is_window(job) -> bool:
    return job.task_id.startswith("T4.8:")


def write_merged(context, path: Path, recomputed: pd.DataFrame, retained: pd.DataFrame,
                 retained_status: str) -> None:
    """A table whose recomputed rows carry the correction run's provenance and whose
    retained rows keep the original publication's provenance, with a status column."""
    new = context.stamp(recomputed).assign(correction_status="recomputed_from_published")
    old = retained.assign(correction_status=retained_status)
    merged = pd.concat([new, old], ignore_index=True, sort=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(path, index=False)


def summarise(record: RescoreRecord) -> dict:
    sources = {}
    for item in record.chain_sources:
        sources.setdefault(item.source, []).append(item.task_id)
    return {"chain_sources": {k: sorted(set(v)) for k, v in sources.items()},
            "retained": record.retained, "notes": record.notes}


def dump(record: RescoreRecord, path: Path) -> None:
    path.write_text(json.dumps(summarise(record), indent=2, default=str), encoding="utf-8")
