"""The empirical pipeline: every Part 5 stage, in order, from the canonical input.

The sequence is the one Part 5 §1 fixes:

    frozen data -> transformation and stationarity decisions -> pre-estimation
    nonlinearity evidence -> classical benchmarks -> parsimonious nonlinear alternatives
    -> in-sample adequacy -> pseudo-out-of-sample forecasts -> state-conditioned
    evaluation -> threat-based robustness

Each stage writes its required outputs and records a checkpoint, so a failure late in the
run does not invalidate the earlier work (Comp §5).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from .core.cache import FitCache, code_hash
from .core.hashing import sha256_file
from .core.checkpoints import CheckpointStore
from .core.config import Config
from .core.paths import OutputLayout
from .core.provenance import RunContext
from .core.runtime import RuntimeLog
from .core.schemas import (DataGapEvent, FailureEvent, FitRecord, ReasonCode,
                           Status, TestResult)
from .data.canonical import STATUS_IMPUTED, to_panels
from .diagnostics import nonlinearity, residual_tests, stationarity
from .diagnostics.decision_rule import confirm_on_full_sample, decide_transformation
from .evaluation import alignment, metrics, states, tp_sensitivity
from .evaluation.dm_hln import agrees_with, dm_hln_test
from .evaluation.hlz import HLZSettings, hlz_test
from .evaluation.losses import ABSOLUTE, SIGN_CONVENTION, SQUARED, loss_differential
from .evaluation.mcs import model_confidence_set
from .evaluation.state_loss_regression import state_loss_regression
from .forecasting.parallel import ChainJob, run_chains
from .forecasting.rolling import DataIdentity
from .forecasting.windows import common_calendar, describe_coverage, rolling_origins
from .models import flags
from .models.ar import fit_ar
from .models.arma import fit_arma
from .models.arma_garch import fit_arma_garch
from .models.msar import fit_msar
from .models.registry import AR, ARMA, MSAR, MSAR3, STAR, ModelSpec
from .models.star import fit_star
from .models.var import fit_var
from .reporting import figures, tables
from .transforms.growth import annualized_logdiff

def _supported(result) -> bool:
    """Whether a state-loss regression gives 5% support for state dependence.

    Support means the regression could be estimated and the turning-window coefficient
    is significant at 5%. This is the reading used to classify a T4.TP1 alternative
    window as unchanged, weakened or reversed relative to the baseline width; it is a
    reporting rule for the sensitivity table, not a new inferential procedure.
    """
    if not getattr(result, "available", False):
        return False
    p_value = result.p_values.get("beta_turn")
    return bool(p_value is not None and np.isfinite(p_value) and p_value < 0.05)


PAIRS = (("AR", "ARMA"), ("AR", "MSAR"), ("AR", "STAR"), ("ARMA", "MSAR"), ("ARMA", "STAR"))


@dataclass
class StageOutputs:
    """What one stage produced, for the checkpoint and the final summary."""

    name: str
    files: list[str] = field(default_factory=list)
    notes: dict[str, Any] = field(default_factory=dict)


class Pipeline:
    """Runs the approved methodology end to end from the canonical input."""

    def __init__(self, config: Config, context: RunContext, layout: OutputLayout,
                 bundle, *, smoke: bool = False):
        self.config = config
        self.context = context
        self.layout = layout
        self.bundle = bundle
        self.smoke = smoke
        self.runtime = RuntimeLog()
        self.checkpoints = CheckpointStore(layout.cache / "checkpoints",
                                           enabled=bool(config.get("execution.checkpoint", True)))
        self.cache = FitCache(layout.cache / "fits",
                              enabled=bool(config.get("execution.cache", True)))
        self.identity = DataIdentity(
            canonical_hash=bundle.csv_sha256,
            source_manifest_hash=bundle.parent_source_hash,
            code_hash=code_hash(),
            config_hash=config.hash,
        )
        self.stage_outputs: list[StageOutputs] = []
        self.all_tests: list[TestResult] = []
        self.all_fit_records: list[FitRecord] = []
        self.all_failures: list[FailureEvent] = []
        self.all_gaps: list[DataGapEvent] = []

        # State carried between stages.
        self.panels: dict[str, pd.DataFrame] = {}
        self.targets: dict[str, pd.Series] = {}
        self.frequency: dict[str, str] = {}
        self.decisions: dict[str, Any] = {}
        self.specs: dict[str, dict[str, ModelSpec]] = {}
        self.star_specs: dict[str, Any] = {}
        self.forecasts: dict[str, dict[str, pd.DataFrame]] = {}
        self.chronologies: dict[str, states.Chronology] = {}

    # -- helpers ----------------------------------------------------------

    def _write(self, frame: pd.DataFrame, directory: Path, name: str,
               stage: StageOutputs, *, parquet: bool = False) -> Path:
        path = self.context.write_table(frame, directory / name, also_parquet=parquet)
        stage.files.append(str(path.relative_to(self.layout.root)))
        return path

    def _save_figure(self, fig, directory: Path, name: str, stage: StageOutputs,
                     extra: dict | None = None) -> None:
        written = figures.save(fig, directory / name, self.context, extra)
        stage.files.extend(str(p.relative_to(self.layout.root)) for p in written)

    def _chains(self, jobs: Sequence[ChainJob]) -> list[tuple[Any, Any]]:
        """Run a batch of independent chains, recording everything each one produced."""
        results = run_chains(jobs, self.config, self.identity, self.cache)
        for _, chain in results:
            self.all_fit_records.extend(chain.fit_records)
            self.all_failures.extend(chain.failures)
            self.all_gaps.extend(chain.data_gaps)
        return results

    def _job(self, series_id: str, model_or_spec, horizons: Sequence[int],
             window_length: int, *, tag=None, transformation: str | None = None,
             series: pd.Series | None = None) -> ChainJob:
        spec = (model_or_spec if isinstance(model_or_spec, ModelSpec)
                else self.specs[series_id][model_or_spec])
        frequency = self.frequency[series_id]
        return ChainJob(
            tag=tag if tag is not None else spec.model,
            series_name=series_id,
            y=self.targets[series_id] if series is None else series,
            spec=spec,
            horizons=tuple(int(h) for h in horizons),
            window_length=int(window_length),
            frequency=frequency,
            transformation=(self._units(series_id) if transformation is None
                            else transformation),
            max_origins=self._max_origins())

    def _selected_targets(self) -> list[str]:
        catalog = [row["series_id"] for row in self.config.get("catalog")
                   if row.get("retained") and row["series_id"] != "USREC"]
        if self.smoke:
            chosen = self.config.get("smoke.targets", catalog)
            return [s for s in catalog if s in chosen]
        return catalog

    def _horizons(self, frequency: str) -> list[int]:
        primary = int(self.config.get(f"forecasting.horizons.primary.{frequency}"))
        robustness = self.config.get(f"forecasting.horizons.robustness.{frequency}")
        return sorted({primary, *[int(h) for h in robustness]})

    def _window(self, frequency: str) -> int:
        return int(self.config.get(f"forecasting.windows.{frequency}"))

    def _max_origins(self) -> int | None:
        """The short out-of-sample block of a smoke run (Comp §10), else no cap.

        The key is optional: a smoke run whose configuration does not set one simply uses
        every origin. A baseline run never consults it, so the approved design can never
        be silently truncated.
        """
        if not self.smoke:
            return None
        cap = self.config.get("smoke.max_origins", None)
        return None if cap is None else int(cap)

    # -- stage 1: data ----------------------------------------------------

    def prepare_data(self) -> StageOutputs:
        stage = StageOutputs("canonical_input")
        with self.runtime.stage("data") as timing:
            self.panels = to_panels(self.bundle.frame)
            usrec = self.panels["M"]["USREC"].dropna()
            self.chronologies["M"] = states.monthly_chronology(usrec)
            self.chronologies["Q"] = states.quarterly_chronology(usrec)

            # T2.0 concept-to-series selection
            self._write(tables.concept_to_series_table(self.config.get("catalog")),
                        self.layout.data_audit, "T2.0_concept_series.csv", stage)

            # T2.0A frozen-data manifest, including the derived canonical input
            canonical = dict(self.bundle.metadata)
            canonical["parent_source_snapshot_hash"] = self.bundle.parent_source_hash
            self._write(tables.frozen_manifest_table(self.bundle.source_manifest, canonical),
                        self.layout.manifests, "T2.0A_frozen_manifest.csv", stage)

            # T2.0B imputation audit
            imputed = self.bundle.frame[self.bundle.frame["observation_status"] == STATUS_IMPUTED]
            audit_rows = []
            for row in imputed.itertuples():
                block = self.bundle.frame[
                    (self.bundle.frame["series_id"] == row.series_id)
                    & (self.bundle.frame["date"] == pd.Timestamp(row.imputation_source_date))
                ]
                audit_rows.append({
                    "series_id": row.series_id,
                    "date": row.date.strftime("%Y-%m-%d"),
                    "source_value": row.source_value,
                    "official_value_missing": True,
                    "previous_observed_date": row.imputation_source_date,
                    "previous_observed_value": block["value"].iloc[0] if len(block) else "",
                    "derived_value": row.value,
                    "imputation_method": row.imputation_method,
                    "observation_status": row.observation_status,
                    "is_official_observation": False,
                    "reason": "official October 2025 release cancelled during the 2025 "
                              "federal shutdown; user-approved raw-level LOCF (Part 5 §2.2A)",
                })
            self._write(pd.DataFrame(audit_rows), self.layout.data_audit,
                        "october_2025_imputation_audit.csv", stage)

            # Build modelling targets. The rate series wait for the §3.4 decision.
            dictionary_rows = []
            for series_id in self._selected_targets():
                spec = self.config.get(f"targets.{series_id}")
                frequency = spec["frequency"]
                panel = self.panels[frequency]
                level = panel[series_id].dropna()
                self.frequency[series_id] = frequency
                kind = spec["transform"]["kind"]
                if kind == "logdiff_annualized":
                    target = annualized_logdiff(level, float(spec["transform"]["k"])).dropna()
                    self.targets[series_id] = target
                    transformation = f"{int(spec['transform']['k'])} x dlog"
                else:
                    target = None
                    transformation = "pending stationarity decision"
                series_imputed = imputed[imputed["series_id"] == series_id]
                dictionary_rows.append({
                    "target": series_id,
                    "fred_id": series_id,
                    "raw_units": self.bundle.source_manifest.entry(series_id).units,
                    "seasonal_adjustment": self.bundle.source_manifest.entry(series_id).seasonal_adjustment,
                    "raw_first_date": self.bundle.source_manifest.entry(series_id).first_observation_date,
                    "raw_last_date": self.bundle.source_manifest.entry(series_id).last_observation_date,
                    "usable_first_date": level.index.min().strftime("%Y-%m-%d"),
                    "usable_last_date": level.index.max().strftime("%Y-%m-%d"),
                    "transformed_first_date": target.index.min().strftime("%Y-%m-%d") if target is not None else "",
                    "transformed_last_date": target.index.max().strftime("%Y-%m-%d") if target is not None else "",
                    "transformation": transformation,
                    "provenance": "author-processed canonical input derived from the frozen official snapshot",
                    "locf_status": ("IMPUTED_LOCF at " + ";".join(
                        d.strftime("%Y-%m-%d") for d in series_imputed["date"])) if len(series_imputed) else "none",
                    "role": spec.get("role", "baseline"),
                    "source_institution": self.bundle.source_manifest.entry(series_id).source_institution,
                    "frequency": frequency,
                })
            self._write(tables.data_dictionary_table(dictionary_rows),
                        self.layout.data_audit, "T2.1_data_dictionary.csv", stage)

            # F2.0 sample coverage
            spans = {sid: (self.panels[self.frequency[sid]][sid].dropna().index.min(),
                           self.panels[self.frequency[sid]][sid].dropna().index.max())
                     for sid in self._selected_targets()}
            self._save_figure(
                figures.sample_coverage_timeline(
                    spans, pd.Timestamp(self.config.get("samples.monthly_end")),
                    pd.Timestamp(self.config.get("samples.var_start"))),
                self.layout.figures, "F2.0_sample_timeline", stage, {"figure_id": "F2.0"})

            timing.notes = f"{len(self.targets)} growth targets built"
        self.checkpoints.record("canonical_input", {"csv": self.identity.canonical_hash},
                                {"targets": sorted(self.targets)})
        self.stage_outputs.append(stage)
        return stage

    # -- stage 2: stationarity -------------------------------------------

    def stationarity_stage(self) -> StageOutputs:
        stage = StageOutputs("stationarity_decisions")
        results: list[TestResult] = []
        decision_rows = []
        with self.runtime.stage("stationarity"):
            for series_id in self._selected_targets():
                frequency = self.frequency[series_id]
                spec = self.config.get(f"targets.{series_id}")
                level = self.panels[frequency][series_id].dropna()
                window_length = self._window(frequency)

                if spec["transform"]["kind"] == "decided_by_stationarity_rule":
                    initial = level.iloc[:window_length]
                    decision = decide_transformation(series_id, initial, frequency, self.config)
                    decision = confirm_on_full_sample(decision, level, frequency, self.config)
                    self.decisions[series_id] = decision
                    results.extend(decision.initial_window_results)
                    results.extend(decision.full_sample_results)
                    decision_rows.append(decision.to_row())
                    if decision.decision == "level":
                        self.targets[series_id] = level
                    else:
                        self.targets[series_id] = level.diff().dropna()
                else:
                    # §3.3: demonstrate rather than assume the growth transformation.
                    log_level = np.log(level)
                    log_level.name = series_id
                    results.extend(stationarity.transformation_verification(
                        log_level, self.targets[series_id], frequency, self.config))

            frame = stationarity.results_to_frame(results)
            self._write(frame, self.layout.diagnostics, "T2.2_stationarity.csv", stage)
            if decision_rows:
                self._write(pd.DataFrame(decision_rows), self.layout.diagnostics,
                            "T2.2_transformation_decisions.csv", stage)
            self.all_tests.extend(results)

            # F2.1 per-target overview
            usrec = self.panels["M"]["USREC"].dropna()
            for series_id in self._selected_targets():
                frequency = self.frequency[series_id]
                entry = self.bundle.source_manifest.entry(series_id)
                decision = self.decisions.get(series_id)
                break_date = None
                if decision is not None and decision.break_date:
                    break_date = pd.Timestamp(decision.break_date)
                imputed = [pd.Timestamp(d) for d in self.bundle.frame[
                    (self.bundle.frame["series_id"] == series_id)
                    & (self.bundle.frame["observation_status"] == STATUS_IMPUTED)]["date"]]
                self._save_figure(
                    figures.series_overview(
                        self.panels[frequency][series_id].dropna(), self.targets[series_id],
                        usrec, series_id=series_id, level_units=entry.units,
                        transformed_units=self._units(series_id), break_date=break_date,
                        imputed_dates=imputed),
                    self.layout.figures, f"F2.1_{series_id}", stage,
                    {"figure_id": "F2.1", "series": series_id})
        self.checkpoints.record("stationarity_decisions", {"targets": sorted(self.targets)},
                                {"decisions": {k: v.decision for k, v in self.decisions.items()}})
        self.stage_outputs.append(stage)
        return stage

    def _units(self, series_id: str) -> str:
        spec = self.config.get(f"targets.{series_id}")
        if spec["transform"]["kind"] == "logdiff_annualized":
            return "annualized percent"
        decision = self.decisions.get(series_id)
        if decision is not None and decision.decision == "difference":
            return "percentage-point change"
        return "percent"

    # -- stage 3: nonlinearity -------------------------------------------

    def nonlinearity_stage(self) -> StageOutputs:
        stage = StageOutputs("nonlinearity_diagnostics")
        tsay_rows, star_rows = [], []
        with self.runtime.stage("nonlinearity"):
            for series_id in self._selected_targets():
                frequency = self.frequency[series_id]
                target = self.targets[series_id]
                initial = target.iloc[: self._window(frequency)]
                order = self.specs.get(series_id, {}).get(AR)
                probe_order = order.order if order else 1

                result = nonlinearity.tsay_test(initial, probe_order, series=series_id)
                self.all_tests.append(result)
                tsay_rows.append(result.to_row())

                spec = nonlinearity.select_delay_and_type(
                    initial, probe_order, frequency, self.config, series=series_id)
                self.star_specs[series_id] = spec
                self.all_tests.extend(spec.delay_results + spec.sequence_results)
                star_rows.append(spec.to_row())

            self._write(tables.with_stars(pd.DataFrame(tsay_rows)), self.layout.diagnostics,
                        "T2.3_tsay.csv", stage)
            self._write(pd.DataFrame(star_rows), self.layout.diagnostics,
                        "T2.4_star_linearity.csv", stage)
        self.checkpoints.record("nonlinearity_diagnostics", {"targets": sorted(self.targets)},
                                {"delays": {k: v.delay for k, v in self.star_specs.items()}})
        self.stage_outputs.append(stage)
        return stage

    # -- stage 4: specification ------------------------------------------

    def specification_stage(self, *, final: bool = True) -> StageOutputs:
        """Fix every discrete specification from the initial estimation window.

        Called twice: once before the nonlinearity diagnostics, which need the BIC-selected
        AR order as their probe order, and once after, when the STAR delay and type are
        known. Only the second call writes T2.5.
        """
        from .specification.ar_select import select_ar_order, select_arma_order

        stage = StageOutputs("selected_specifications")
        rows = []
        with self.runtime.stage("specification"):
            for series_id in self._selected_targets():
                frequency = self.frequency[series_id]
                initial = self.targets[series_id].iloc[: self._window(frequency)]
                ar_choice = select_ar_order(initial, frequency, self.config, series=series_id)
                arma_choice = select_arma_order(initial, frequency, self.config, series=series_id)
                star_spec = self.star_specs.get(series_id)

                msar_cap = int(self.config.get(f"models.msar.lag_cap.{frequency}"))
                star_cap = int(self.config.get(f"models.star.lag_cap.{frequency}"))
                self.specs[series_id] = {
                    AR: ModelSpec(AR, order=ar_choice.order),
                    ARMA: ModelSpec(ARMA, order=arma_choice.order[0],
                                    ma_order=arma_choice.order[1]),
                    MSAR: ModelSpec(MSAR, order=min(ar_choice.order, msar_cap), k_regimes=2),
                    MSAR3: ModelSpec(MSAR3, order=min(ar_choice.order, msar_cap), k_regimes=3),
                    STAR: ModelSpec(
                        STAR, order=min(ar_choice.order, star_cap),
                        kind=star_spec.kind if star_spec else "LSTAR",
                        delay=star_spec.delay if star_spec else 1),
                }
                rows.append({
                    "series_id": series_id,
                    "ar_lag": ar_choice.order,
                    "ar_bic": ar_choice.bic,
                    "ar_residuals_white": ar_choice.residuals_white,
                    "ar_diagnostically_weak": ar_choice.diagnostically_weak,
                    "ar_note": ar_choice.note,
                    "arma_order": f"({arma_choice.order[0]},{arma_choice.order[1]})",
                    "arma_bic": arma_choice.bic,
                    "arma_residuals_white": arma_choice.residuals_white,
                    "arma_note": arma_choice.note,
                    "msar_lag_after_cap": self.specs[series_id][MSAR].order,
                    "star_lag_after_cap": self.specs[series_id][STAR].order,
                    "star_type": star_spec.kind if star_spec else "",
                    "star_delay": star_spec.delay if star_spec else "",
                    "star_linearity_rejected": (star_spec.linearity_rejected
                                                if star_spec else ""),
                    "star_tie_break_used": (star_spec.tie_break_used if star_spec else ""),
                    "fixed_from": "initial estimation window",
                })
            if final:
                self._write(pd.DataFrame(rows), self.layout.diagnostics,
                            "T2.5_selected_specs.csv", stage)
        self.checkpoints.record("selected_specifications", {"targets": sorted(self.targets)},
                                {s: {m: spec.label for m, spec in v.items()}
                                 for s, v in self.specs.items()})
        self.stage_outputs.append(stage)
        return stage

    # -- stage 5: in-sample adequacy --------------------------------------

    def adequacy_stage(self) -> StageOutputs:
        stage = StageOutputs("model_fits")
        adequacy_rows, credibility_rows = [], []
        diagnostics: list[TestResult] = []
        self.full_sample_fits: dict[str, dict[str, Any]] = {}
        with self.runtime.stage("adequacy"):
            usrec = self.panels["M"]["USREC"].dropna()
            for series_id in self._selected_targets():
                frequency = self.frequency[series_id]
                target = self.targets[series_id]
                specs = self.specs[series_id]
                fits: dict[str, Any] = {}

                for model in (AR, ARMA, MSAR, STAR, MSAR3):
                    spec = specs[model]
                    try:
                        if model == AR:
                            fit = fit_ar(target, spec.order, series=series_id,
                                         refit_date=str(target.index[-1].date()))
                            residuals, fitted = fit.residuals, fit.fitted
                        elif model == ARMA:
                            fit = fit_arma(target, (spec.order, spec.ma_order), series=series_id,
                                           refit_date=str(target.index[-1].date()))
                            residuals, fitted = fit.residuals, fit.fitted
                        elif model in (MSAR, MSAR3):
                            fit = fit_msar(target, spec.order, spec.k_regimes, series=series_id,
                                           refit_date=str(target.index[-1].date()))
                            flags.apply_msar_flags(fit.record, fit, self.config)
                            residuals = fit.one_step_residuals()
                            fitted = fit.fitted_values()
                        else:
                            fit = fit_star(target, spec.order, spec.delay, spec.kind, self.config,
                                           series=series_id, refit_date=str(target.index[-1].date()))
                            flags.apply_star_flags(fit.record, fit, self.config)
                            residuals, fitted = fit.residuals, fit.fitted
                    except Exception as exc:                      # recorded, never hidden
                        record = FitRecord(series=series_id, model=model, spec_label=spec.label,
                                           spec_hash="", window_start=str(target.index[0].date()),
                                           window_end=str(target.index[-1].date()),
                                           refit_date=str(target.index[-1].date()),
                                           converged=False, optimizer_message=repr(exc)[:200])
                        record.add_flag(ReasonCode.NONCONVERGENCE, Status.FAILED,
                                        detail=repr(exc)[:150])
                        self.all_fit_records.append(record)
                        self.all_failures.append(FailureEvent(
                            series=series_id, model=model,
                            refit_date=str(target.index[-1].date()), horizon=None,
                            category=Status.FAILED, reason_code=ReasonCode.NONCONVERGENCE,
                            raw_diagnostic=repr(exc)[:200], forecast_retained=False,
                            figure_separated=True))
                        adequacy_rows.append({
                            "series": series_id, "model": model, "spec_label": spec.label,
                            "refit_date": str(target.index[-1].date()), "sample": "full",
                            "converged": False, "status": Status.FAILED.value,
                            "unavailable_reason": repr(exc)[:150],
                        })
                        continue

                    residuals = np.asarray(residuals, dtype=float)
                    if residuals[np.isfinite(residuals)].size < 2:
                        # A failed fit leaves no residuals. That is recorded, not patched
                        # over with a fabricated diagnostic (CLAUDE.md section 7).
                        if fit.record.status is not Status.FAILED:
                            fit.record.add_flag(ReasonCode.NONFINITE, Status.FAILED,
                                                detail="no usable residuals")
                        self.all_fit_records.append(fit.record)
                        self.all_failures.append(FailureEvent(
                            series=series_id, model=model,
                            refit_date=str(target.index[-1].date()), horizon=None,
                            category=Status.FAILED, reason_code=ReasonCode.NONFINITE,
                            raw_diagnostic="the full-sample fit produced no usable residuals",
                            forecast_retained=False, figure_separated=True))
                        adequacy_rows.append({
                            "series": series_id, "model": model, "spec_label": spec.label,
                            "refit_date": str(target.index[-1].date()), "sample": "full",
                            "converged": fit.record.converged,
                            "status": Status.FAILED.value,
                            "reason_codes": ";".join(c.value for c in fit.record.reason_codes),
                            "unavailable_reason": "no usable residuals for the §7.3 battery",
                        })
                        continue

                    battery = residual_tests.adequacy_suite(
                        residuals, frequency, self.config, model=model, series=series_id,
                        order=spec.order, ma_order=spec.ma_order)
                    flags.apply_residual_flags(
                        fit.record,
                        residual_tests.primary_ljung_box(battery, frequency, self.config),
                        self.config)
                    diagnostics.extend(battery)
                    fits[model] = (fit, residuals, fitted)
                    self.all_fit_records.append(fit.record)
                    for code in fit.record.reason_codes:
                        self.all_failures.append(FailureEvent(
                            series=series_id, model=model,
                            refit_date=str(target.index[-1].date()), horizon=None,
                            category=fit.record.status, reason_code=code,
                            raw_diagnostic=str(fit.record.diagnostics.get(
                                f"flag_{code.value}", ""))[:200],
                            forecast_retained=fit.record.status is not Status.FAILED,
                            figure_separated=fit.record.status is Status.FAILED))

                    row = {
                        "series": series_id, "model": model, "spec_label": spec.label,
                        "refit_date": str(target.index[-1].date()), "sample": "full",
                        "converged": fit.record.converged,
                        "loglik": fit.record.loglik, "aic": fit.record.aic, "bic": fit.record.bic,
                        "n_obs": fit.record.n_obs,
                        "rmse": metrics.rmse(residuals), "mae": metrics.mae(residuals),
                        "status": fit.record.status.value,
                        "reason_codes": ";".join(c.value for c in fit.record.reason_codes),
                    }
                    for result in battery:
                        key = result.name.replace("-", "_").replace("(", "_").replace(")", "")
                        row[f"{key}_stat"] = result.statistic
                        row[f"{key}_p"] = result.p_value
                    adequacy_rows.append(row)

                    if model in (MSAR, MSAR3):
                        credibility_rows.append({
                            "series": series_id, "model": model, "spec_label": spec.label,
                            "family": "MSAR", "k_regimes": fit.k_regimes, "order": fit.order,
                            "transition_matrix": "; ".join(
                                f"p{i+1}{j+1}={fit.P[i, j]:.4f}"
                                for i in range(fit.k_regimes) for j in range(fit.k_regimes)),
                            "occupancy": "; ".join(f"regime{i+1}={v:.4f}"
                                                   for i, v in enumerate(fit.occupancy)),
                            "expected_durations": "; ".join(
                                f"regime{i+1}={v:.2f}" for i, v in enumerate(fit.expected_duration)),
                            "means": "; ".join(f"mu{i+1}={v:.4f}" for i, v in enumerate(fit.mu)),
                            "sigma": fit.sigma,
                            "min_diagonal": float(np.min(np.diag(fit.P))),
                            "max_diagonal": float(np.max(np.diag(fit.P))),
                            "transition_boundary_flag": any(
                                c.value in ("TRANSITION_BOUNDARY", "EMPTY_REGIME")
                                for c in fit.record.reason_codes),
                            "status": fit.record.status.value,
                            "reason_codes": ";".join(c.value for c in fit.record.reason_codes),
                        })
                    if model == STAR:
                        g = np.asarray(fit.G, dtype=float)
                        credibility_rows.append({
                            "series": series_id, "model": model, "spec_label": spec.label,
                            "family": "STAR", "star_type": fit.kind, "delay": fit.delay,
                            "order": fit.order, "gamma": fit.gamma, "threshold_c": fit.c,
                            "transition_scale": fit.scale,
                            "G_min": float(g.min()) if g.size else float("nan"),
                            "G_max": float(g.max()) if g.size else float("nan"),
                            "G_sd": float(g.std(ddof=1)) if g.size > 1 else float("nan"),
                            "G_mean": float(g.mean()) if g.size else float("nan"),
                            "parameter_boundary_flag": any(
                                c.value in ("STAR_GAMMA_BOUND", "STAR_THRESHOLD_EXTREME")
                                for c in fit.record.reason_codes),
                            "status": fit.record.status.value,
                            "reason_codes": ";".join(c.value for c in fit.record.reason_codes),
                        })

                self.full_sample_fits[series_id] = fits

                # Figures. One model per panel or figure, per the readability rule.
                units = self._units(series_id)
                for model, (fit, residuals, fitted) in fits.items():
                    if model == MSAR3:
                        continue
                    index = target.index[-len(fitted):] if len(fitted) else target.index[:0]
                    self._save_figure(
                        figures.fitted_vs_observed(target, pd.Series(fitted, index=index), usrec,
                                                   series_id=series_id, model=model, units=units),
                        self.layout.figures, f"F3.1_{series_id}_{model}", stage,
                        {"figure_id": "F3.1", "series": series_id, "model": model})
                    self._save_figure(
                        figures.residual_acf(residuals, series_id=series_id, model=model),
                        self.layout.figures, f"F3.2_{series_id}_{model}", stage,
                        {"figure_id": "F3.2", "series": series_id, "model": model})
                if MSAR in fits:
                    fit = fits[MSAR][0]
                    dates = target.index[-fit.smoothed_regime.shape[0]:]
                    self._save_figure(
                        figures.regime_probabilities(dates, fit.smoothed_regime, usrec,
                                                     series_id=series_id, model=MSAR),
                        self.layout.figures, f"F3.3_{series_id}_MSAR", stage,
                        {"figure_id": "F3.3", "series": series_id, "model": MSAR})
                if STAR in fits:
                    fit = fits[STAR][0]
                    zed = fit.y[max(fit.order, fit.delay) - fit.delay:][: fit.G.size] \
                        if fit.y.size else np.empty(0)
                    self._save_figure(
                        figures.star_transition(zed, fit.G, series_id=series_id, kind=fit.kind,
                                                gamma=fit.gamma, c=fit.c),
                        self.layout.figures, f"F3.3_{series_id}_STAR", stage,
                        {"figure_id": "F3.3", "series": series_id, "model": STAR})

            self.all_tests.extend(diagnostics)
            self._write(pd.DataFrame(adequacy_rows), self.layout.models,
                        "T3.1_in_sample_adequacy.csv", stage)
            self._write(pd.DataFrame(credibility_rows), self.layout.models,
                        "T3.2_nonlinear_credibility.csv", stage)
            self._write(tables.test_table(diagnostics), self.layout.diagnostics,
                        "T3.2_residual_tests.csv", stage)
        self.checkpoints.record("model_fits", {"targets": sorted(self.targets)},
                                {"n_rows": len(adequacy_rows)})
        self.stage_outputs.append(stage)
        return stage

    # -- stage 6: pseudo-out-of-sample forecasts --------------------------

    def forecasting_stage(self) -> StageOutputs:
        stage = StageOutputs("forecasts")
        audit_rows = []
        self.chain_results: dict[str, dict[str, Any]] = {}
        with self.runtime.stage("forecasting") as timing:
            for series_id in self._selected_targets():
                frequency = self.frequency[series_id]
                target = self.targets[series_id]
                horizons = self._horizons(frequency)
                window_length = self._window(frequency)
                self.forecasts[series_id] = {}
                self.chain_results[series_id] = {}

                jobs = [self._job(series_id, model, horizons, window_length, tag=model)
                        for model in (AR, ARMA, MSAR, STAR, MSAR3)]
                for model, chain in self._chains(jobs):
                    spec = self.specs[series_id][model]
                    self.forecasts[series_id][model] = chain.forecasts
                    self.chain_results[series_id][model] = chain
                    audit_rows.append({
                        "series": series_id, "model": model, "spec_label": spec.label,
                        "window_length": window_length, "role": "baseline",
                        "horizons": ";".join(str(h) for h in horizons),
                        **chain.counts(),
                        "n_data_gaps": len(chain.data_gaps),
                        "first_target": (chain.forecasts["target_date"].min()
                                         if not chain.forecasts.empty else None),
                        "last_target": (chain.forecasts["target_date"].max()
                                        if not chain.forecasts.empty else None),
                    })

                combined = pd.concat([f for f in self.forecasts[series_id].values() if not f.empty],
                                     ignore_index=True) if self.forecasts[series_id] else pd.DataFrame()
                self._write(combined, self.layout.forecasts, f"forecasts_{series_id}.csv",
                            stage, parquet=True)

            self._write(pd.DataFrame(audit_rows), self.layout.forecasts,
                        "forecast_origin_audit.csv", stage)
            timing.notes = f"{len(audit_rows)} rolling chains"
        self.checkpoints.record("forecasts", {"targets": sorted(self.targets)},
                                {"chains": len(audit_rows)})
        self.stage_outputs.append(stage)
        return stage

    # -- stage 7: forecast evaluation -------------------------------------

    def _hlz_settings(self) -> HLZSettings:
        settings = self.config.require("evaluation.hlz")
        return HLZSettings(
            lrv_kernel=settings["lrv_kernel"], b0=float(settings["lrv_bandwidth"]["b0"]),
            demean_kernel=settings["demean_kernel"],
            h0=float(settings["demean_bandwidth"]["h0"]),
            critical_value_replications=int(settings["critical_value_replications"]),
            critical_value_seed=int(settings["critical_value_seed"]),
            two_sided=bool(settings["two_sided"]),
            report_one_sided=bool(settings["report_one_sided"]),
            source=settings["source"])

    def _horse_race(self, series_id: str, horizon: int) -> dict[str, pd.DataFrame]:
        """Admissible baseline competitors at one horizon, keyed by model."""
        out = {}
        for model in (AR, ARMA, MSAR, STAR):
            frame = self.forecasts[series_id].get(model)
            if frame is None or frame.empty:
                continue
            subset = frame[frame["horizon"] == horizon]
            if not subset.empty:
                out[model] = subset
        return out

    def evaluation_stage(self) -> StageOutputs:
        stage = StageOutputs("evaluation")
        settings = self._hlz_settings()
        benchmark = str(self.config.get("evaluation.benchmark"))
        losses = list(self.config.get("evaluation.losses"))
        pairs = [tuple(p) for p in self.config.get("evaluation.pairs")]
        confidences = [float(c) for c in self.config.get("evaluation.mcs.confidence_levels")]

        main_rows, hlz_rows, dm_rows, mcs_rows = [], [], [], []
        state_rows, slr_rows, peak_rows, tp_rows = [], [], [], []
        usrec = self.panels["M"]["USREC"].dropna()

        with self.runtime.stage("evaluation"):
            for series_id in self._selected_targets():
                frequency = self.frequency[series_id]
                chronology = self.chronologies[frequency]
                baseline_width = int(self.config.get(
                    f"evaluation.states.turning_window_baseline.{frequency}"))

                for horizon in self._horizons(frequency):
                    frames = self._horse_race(series_id, horizon)
                    if benchmark not in frames:
                        continue

                    # --- T3.3 / T3.3A / T3.3B -------------------------------
                    accuracy = metrics.accuracy_table(
                        frames, benchmark, series=series_id, horizon=horizon,
                        window_length=self._window(frequency))

                    for model, frame in frames.items():
                        chain = self.chain_results[series_id][model]
                        row = accuracy[accuracy["model"] == model].iloc[0].to_dict()
                        row.update({
                            "attempted_origins": chain.attempted, "valid_origins": chain.valid,
                            "failed_origins": chain.failed,
                            "n_fragile_events": sum(
                                1 for e in chain.failures if e.category is Status.FRAGILE),
                            "model_status": ("benchmark" if model == benchmark else "competitor"),
                        })
                        if model != benchmark:
                            errors = alignment.aligned_errors(
                                {model: frame, benchmark: frames[benchmark]},
                                alignment.pairwise(frame, frames[benchmark]).dates)
                            for loss_kind in losses:
                                d = loss_differential(errors[model], errors[benchmark], loss_kind)
                                numeric, result = hlz_test(
                                    d[np.isfinite(d)], settings, series=series_id,
                                    model_a=model, model_b=benchmark)
                                row[f"hlz_{loss_kind}_statistic"] = result.statistic
                                row[f"hlz_{loss_kind}_p_value"] = result.p_value
                                row[f"hlz_{loss_kind}_decision_5pct"] = result.decision_5pct
                        main_rows.append(row)

                    for model_a, model_b in pairs:
                        if model_a not in frames or model_b not in frames:
                            continue
                        aligned = alignment.pairwise(frames[model_a], frames[model_b])
                        errors = alignment.aligned_errors(
                            {model_a: frames[model_a], model_b: frames[model_b]}, aligned.dates)
                        for loss_kind in losses:
                            # Sign convention: competitor minus benchmark, where the
                            # second-named model is the benchmark of the pair.
                            d = loss_differential(errors[model_a], errors[model_b], loss_kind)
                            d = d[np.isfinite(d)]
                            numeric, hlz_result = hlz_test(
                                d, settings, series=series_id, model_a=model_a, model_b=model_b)
                            dm_result = dm_hln_test(
                                errors[model_a], errors[model_b], horizon, loss_kind,
                                series=series_id, model_a=model_a, model_b=model_b)
                            common = {
                                "series": series_id, "horizon": horizon, "loss": loss_kind,
                                "model_a": model_a, "model_b": model_b,
                                "sign_convention": SIGN_CONVENTION,
                                "n_common": aligned.n_common,
                                "n_removed_a": aligned.removed.get("left", 0),
                                "n_removed_b": aligned.removed.get("right", 0),
                            }
                            hlz_rows.append({
                                **common, "n": d.size,
                                "mean_loss_differential": (
                                    numeric.mean_loss_differential if numeric else float("nan")),
                                "statistic": hlz_result.statistic,
                                "p_value_two_sided": hlz_result.p_value,
                                "p_value_upper": (numeric.p_value_upper if numeric else float("nan")),
                                "p_value_lower": (numeric.p_value_lower if numeric else float("nan")),
                                "omega_modified": (numeric.omega_modified if numeric else float("nan")),
                                "omega_standard": (numeric.omega_standard if numeric else float("nan")),
                                "mean_variation": (numeric.mean_variation if numeric else float("nan")),
                                "mean_variation_ratio": (
                                    numeric.mean_variation_ratio if numeric else float("nan")),
                                "decision_5pct": hlz_result.decision_5pct,
                                "inference_available": hlz_result.available,
                                "unavailable_reason": hlz_result.unavailable_reason,
                                "tuning": "; ".join(f"{k}={v}" for k, v in
                                                    sorted(hlz_result.tuning.items())),
                                "role": "primary",
                            })
                            dm_rows.append({
                                **common, "statistic": dm_result.statistic,
                                "p_value": dm_result.p_value,
                                "decision_5pct": dm_result.decision_5pct,
                                "inference_available": dm_result.available,
                                "unavailable_reason": dm_result.unavailable_reason,
                                "lrv_rule": "Bartlett kernel, truncation h-1",
                                "small_sample_correction": "Harvey-Leybourne-Newbold",
                                "agrees_with_hlz": agrees_with(dm_result, hlz_result),
                                "role": "secondary",
                            })

                    # --- T3.4 Model Confidence Set --------------------------
                    for loss_kind in losses:
                        for confidence in confidences:
                            result = model_confidence_set(
                                frames, loss_kind, confidence, self.config,
                                series=series_id, horizon=horizon)
                            mcs_rows.extend(result.to_rows())

                    # --- T3.5 / T3.6 / T4.TP1 state-conditioned -------------
                    state_table = states.state_frame(chronology, baseline_width)
                    per_state_losses: dict[str, dict[str, float]] = {}
                    # Baseline-width inferential support, so T4.TP1 can report
                    # "weakened" rather than only a change of sign.
                    baseline_support: dict[str, tuple[bool, str]] = {}
                    for model, frame in frames.items():
                        attached = states.attach_states(frame, state_table)
                        subsets = states.state_subsets(attached)
                        benchmark_attached = states.attach_states(frames[benchmark], state_table)
                        for state_name, subset in subsets.items():
                            errors = subset["error"].to_numpy(dtype=float)
                            row = {
                                "series": series_id, "model": model, "horizon": horizon,
                                "state": state_name, "turning_window_width": baseline_width,
                                "n": int(np.isfinite(errors).sum()),
                                "rmse": metrics.rmse(errors), "mae": metrics.mae(errors),
                            }
                            if model != benchmark:
                                aligned = alignment.pairwise(subset, benchmark_attached)
                                paired = alignment.aligned_errors(
                                    {model: subset, benchmark: benchmark_attached}, aligned.dates)
                                d = loss_differential(paired[model], paired[benchmark], SQUARED)
                                row["n_paired"] = aligned.n_common
                                row["mean_loss_differential_squared"] = (
                                    float(np.nanmean(d)) if d.size else float("nan"))
                                d_abs = loss_differential(paired[model], paired[benchmark], ABSOLUTE)
                                row["mean_loss_differential_absolute"] = (
                                    float(np.nanmean(d_abs)) if d_abs.size else float("nan"))
                                per_state_losses.setdefault(model, {})[state_name] = row[
                                    "mean_loss_differential_squared"]
                            row["sign_convention"] = SIGN_CONVENTION
                            row["interpretation"] = "descriptive"
                            state_rows.append(row)

                        # Peak versus trough detail, baseline width, h=1 only.
                        if horizon == min(self._horizons(frequency)):
                            for window_name in ("peak_window", "trough_window"):
                                subset = attached[attached[window_name] == 1]
                                errors = subset["error"].to_numpy(dtype=float)
                                n = int(np.isfinite(errors).sum())
                                peak_rows.append({
                                    "series": series_id, "model": model, "horizon": horizon,
                                    "window": window_name,
                                    "turning_window_width": baseline_width,
                                    "n": n, "rmse": metrics.rmse(errors),
                                    "mae": metrics.mae(errors),
                                    "reporting": ("descriptive only: cell too small for inference"
                                                  if n < 10 else "descriptive"),
                                })

                        # Ex-post state-dependent forecast-loss regression (M1).
                        if model != benchmark:
                            aligned = alignment.pairwise(attached, benchmark_attached)
                            paired_model = alignment.restrict(attached, aligned.dates)
                            paired_bench = alignment.restrict(benchmark_attached, aligned.dates)
                            d = loss_differential(
                                paired_model["error"].to_numpy(float),
                                paired_bench["error"].to_numpy(float), SQUARED)
                            result = state_loss_regression(
                                d, paired_model["recession"].to_numpy(float),
                                paired_model["turning_window"].to_numpy(float), horizon,
                                series=series_id, model=f"{model} vs {benchmark}")
                            row = result.to_row()
                            row["turning_window_width"] = baseline_width
                            row["loss"] = SQUARED
                            row["state_dependence_supported_5pct"] = _supported(result)
                            slr_rows.append(row)
                            baseline_support[model] = (_supported(result),
                                                       result.unavailable_reason)
                            for wald in (result.joint_wald, result.slopes_wald):
                                if wald is not None:
                                    self.all_tests.append(wald)

                    # Turning-window sensitivity (T4.TP1).
                    widths = [int(w) for w in self.config.get(
                        f"evaluation.states.turning_window_sensitivity.{frequency}")]
                    for width in widths:
                        table = states.state_frame(chronology, width)
                        benchmark_attached = states.attach_states(frames[benchmark], table)
                        for model, frame in frames.items():
                            attached = states.attach_states(frame, table)
                            for state_name in ("turning_window", "outside_turning_window"):
                                subset = attached[attached[state_name] == 1]
                                errors = subset["error"].to_numpy(dtype=float)
                                row = {
                                    "series": series_id, "model": model, "horizon": horizon,
                                    "turning_window_width": width,
                                    "is_baseline_width": width == baseline_width,
                                    "state": state_name,
                                    "n": int(np.isfinite(errors).sum()),
                                    "rmse": metrics.rmse(errors), "mae": metrics.mae(errors),
                                    "convention_note": (
                                        "the baseline width is a predeclared choice whose "
                                        "arbitrariness this table tests; it is not an "
                                        "established universal convention"),
                                }
                                if model != benchmark and state_name == "turning_window":
                                    aligned = alignment.pairwise(subset, benchmark_attached)
                                    paired_model = alignment.restrict(subset, aligned.dates)
                                    paired_bench = alignment.restrict(
                                        benchmark_attached, aligned.dates)
                                    d = loss_differential(
                                        paired_model["error"].to_numpy(float),
                                        paired_bench["error"].to_numpy(float), SQUARED)
                                    mean_d = float(np.nanmean(d)) if d.size else float("nan")
                                    row["n_paired"] = aligned.n_common
                                    row["mean_loss_differential_squared"] = mean_d
                                    row["direction"] = (
                                        "nonlinear/competitor better" if mean_d < 0
                                        else "classical benchmark better" if mean_d > 0
                                        else "tie")
                                    regression = state_loss_regression(
                                        d, paired_model["recession"].to_numpy(float),
                                        paired_model["turning_window"].to_numpy(float), horizon,
                                        series=series_id, model=f"{model} vs {benchmark}")
                                    row["inference_available"] = regression.available
                                    row["inference_unavailable_reason"] = (
                                        regression.unavailable_reason)
                                    baseline_mean = per_state_losses.get(model, {}).get(
                                        "turning_window", float("nan"))
                                    supported_base, base_reason = baseline_support.get(
                                        model, (False, "baseline-width regression not run"))
                                    row["baseline_support_5pct"] = supported_base
                                    row["alternative_support_5pct"] = _supported(regression)
                                    verdict = tp_sensitivity.classify(
                                        baseline_mean, supported_base,
                                        mean_d, _supported(regression),
                                        baseline_available=(np.isfinite(baseline_mean)
                                                            and not base_reason),
                                        alternative_available=regression.available)
                                    row.update(verdict.to_row())
                                tp_rows.append(row)

                # --- figures ------------------------------------------------
                primary = min(self._horizons(frequency))
                frames = self._horse_race(series_id, primary)
                if frames:
                    actual = (frames[benchmark].set_index("target_date")["actual"]
                              if benchmark in frames else pd.Series(dtype=float))
                    series_forecasts, flagged = {}, {}
                    for model, frame in frames.items():
                        indexed = frame.set_index("target_date")
                        series_forecasts[model] = indexed["forecast"]
                        bad = indexed[(indexed["status"] == Status.FAILED.value)
                                      | indexed["reason_codes"].str.contains(
                                          "EXTREME_FORECAST", na=False)]["forecast"]
                        if not bad.empty:
                            flagged[model] = bad
                    self._save_figure(
                        figures.actual_vs_forecast(actual, series_forecasts, usrec,
                                                   series_id=series_id,
                                                   units=self._units(series_id),
                                                   flagged=flagged or None),
                        self.layout.figures, f"F3.4_{series_id}", stage,
                        {"figure_id": "F3.4", "series": series_id, "horizon": primary})

                    aligned = alignment.across_models(frames)
                    if aligned.n_common:
                        errors = alignment.aligned_errors(frames, aligned.dates)
                        differences = {
                            model: np.cumsum(loss_differential(
                                errors[model], errors[benchmark], SQUARED))
                            for model in frames if model != benchmark}
                        self._save_figure(
                            figures.cumulative_loss_difference(
                                aligned.dates, differences, usrec, series_id=series_id,
                                benchmark=benchmark),
                            self.layout.figures, f"F3.5_{series_id}", stage,
                            {"figure_id": "F3.5", "series": series_id})

                    subset = pd.DataFrame([r for r in state_rows
                                           if r["series"] == series_id and r["horizon"] == primary])
                    if not subset.empty:
                        self._save_figure(
                            figures.state_comparison(subset, series_id=series_id,
                                                     benchmark=benchmark),
                            self.layout.figures, f"F3.6_{series_id}", stage,
                            {"figure_id": "F3.6", "series": series_id,
                             "interpretation": "descriptive"})

            self._write(pd.DataFrame(main_rows), self.layout.forecast_tests,
                        "T3.3_main_forecast_table.csv", stage)
            self._write(tables.with_stars(pd.DataFrame(hlz_rows), "p_value_two_sided"),
                        self.layout.forecast_tests, "T3.3A_hlz_pairwise.csv", stage)
            self._write(tables.with_stars(pd.DataFrame(dm_rows)), self.layout.forecast_tests,
                        "T3.3B_dm_hln_pairwise.csv", stage)
            self._write(pd.DataFrame(mcs_rows), self.layout.forecast_tests,
                        "T3.4_model_confidence_set.csv", stage)
            self._write(pd.DataFrame(state_rows), self.layout.forecast_tests,
                        "T3.5_state_performance.csv", stage)
            self._write(pd.DataFrame(slr_rows), self.layout.forecast_tests,
                        "T3.5_state_loss_regression.csv", stage)
            self._write(pd.DataFrame(peak_rows), self.layout.forecast_tests,
                        "T3.6_peak_trough_detail.csv", stage)
            self._write(pd.DataFrame(tp_rows), self.layout.robustness,
                        "T4.TP1_turning_window_sensitivity.csv", stage)
        self.checkpoints.record("evaluation", {"targets": sorted(self.targets)},
                                {"n_pairwise_tests": len(hlz_rows)})
        self.stage_outputs.append(stage)
        return stage

    # -- stage 8: robustness ----------------------------------------------

    def _accuracy_rows(self, frames: Mapping[str, pd.DataFrame], benchmark: str,
                       series_id: str, horizon: int, extra: Mapping[str, Any]) -> list[dict]:
        if benchmark not in frames:
            return []
        table = metrics.accuracy_table(frames, benchmark, series=series_id, horizon=horizon)
        rows = []
        for record in table.to_dict("records"):
            record.update(extra)
            rows.append(record)
        return rows

    def _predictive_rows(self, frames: Mapping[str, pd.DataFrame], benchmark: str,
                         series_id: str, horizon: int, extra: Mapping[str, Any]) -> list[dict]:
        """HLZ (primary) and DM-HLN (secondary) for every competitor against a benchmark."""
        settings = self._hlz_settings()
        rows = []
        for model, frame in frames.items():
            if model == benchmark or benchmark not in frames:
                continue
            aligned = alignment.pairwise(frame, frames[benchmark])
            errors = alignment.aligned_errors(
                {model: frame, benchmark: frames[benchmark]}, aligned.dates)
            for loss_kind in self.config.get("evaluation.losses"):
                d = loss_differential(errors[model], errors[benchmark], loss_kind)
                d = d[np.isfinite(d)]
                numeric, hlz_result = hlz_test(d, settings, series=series_id,
                                               model_a=model, model_b=benchmark)
                dm_result = dm_hln_test(errors[model], errors[benchmark], horizon, loss_kind,
                                        series=series_id, model_a=model, model_b=benchmark)
                rows.append({
                    "series": series_id, "model": model, "benchmark": benchmark,
                    "horizon": horizon, "loss": loss_kind, "n": int(d.size),
                    "n_aligned": aligned.n_common,
                    "sign_convention": SIGN_CONVENTION,
                    "mean_loss_differential": (float(np.mean(d)) if d.size else float("nan")),
                    "hlz_statistic": hlz_result.statistic,
                    "hlz_p_value_two_sided": hlz_result.p_value,
                    "hlz_p_value_upper": (numeric.p_value_upper if numeric else float("nan")),
                    "hlz_p_value_lower": (numeric.p_value_lower if numeric else float("nan")),
                    "hlz_decision_5pct": hlz_result.decision_5pct,
                    "hlz_available": hlz_result.available,
                    "hlz_unavailable_reason": hlz_result.unavailable_reason,
                    "dm_hln_statistic": dm_result.statistic,
                    "dm_hln_p_value": dm_result.p_value,
                    "dm_hln_decision_5pct": dm_result.decision_5pct,
                    "dm_hln_available": dm_result.available,
                    "agrees_with_hlz": agrees_with(dm_result, hlz_result),
                    **extra,
                })
        return rows

    def robustness_stage(self) -> StageOutputs:
        stage = StageOutputs("robustness")
        benchmark = str(self.config.get("evaluation.benchmark"))
        with self.runtime.stage("robustness"):
            self._t41_transformation(stage, benchmark)
            self._t42_cpi_lags(stage, benchmark)
            self._t43_regime_count(stage, benchmark)
            self._t44_horizons(stage, benchmark)
            self._t45_var(stage, benchmark)
            self._t46_arma_garch(stage)
            self._t48_window_lengths(stage, benchmark)
            self._t49_locf_exposure(stage)
        self.checkpoints.record("robustness", {"targets": sorted(self.targets)},
                                {"files": len(stage.files)})
        self.stage_outputs.append(stage)
        return stage

    def _t41_transformation(self, stage: StageOutputs, benchmark: str) -> None:
        """T4.1: baseline versus alternative transformation for the two rate series."""
        rows, tests = [], []
        applies = [s for s in self.config.get("robustness.transformation.applies_to")
                   if s in self.targets]
        for series_id in applies:
            frequency = self.frequency[series_id]
            decision = self.decisions.get(series_id)
            if decision is None:
                continue
            level = self.panels[frequency][series_id].dropna()
            baseline_kind = decision.decision
            alternative_kind = "difference" if baseline_kind == "level" else "level"
            alternative = level.diff().dropna() if alternative_kind == "difference" else level
            horizon = int(self.config.get(f"forecasting.horizons.primary.{frequency}"))
            window_length = self._window(frequency)

            jobs = [self._job(series_id, model, [horizon], window_length, tag=model,
                              series=alternative,
                              transformation=f"alternative:{alternative_kind}")
                    for model in (AR, ARMA, MSAR, STAR)]
            frames = {model: chain.forecasts[chain.forecasts["horizon"] == horizon]
                      for model, chain in self._chains(jobs)}

            baseline_frames = self._horse_race(series_id, horizon)
            extra_common = {"series_frequency": frequency, "baseline_transformation": baseline_kind,
                            "exercise": "T4.1 transformation robustness"}
            rows.extend(self._accuracy_rows(baseline_frames, benchmark, series_id, horizon,
                                            {**extra_common, "transformation": baseline_kind,
                                             "role": "baseline", "units": self._units(series_id)}))
            rows.extend(self._accuracy_rows(frames, benchmark, series_id, horizon,
                                            {**extra_common, "transformation": alternative_kind,
                                             "role": "alternative",
                                             "units": ("percent" if alternative_kind == "level"
                                                       else "percentage-point change")}))
            tests.extend(self._predictive_rows(frames, benchmark, series_id, horizon,
                                              {**extra_common, "transformation": alternative_kind,
                                               "role": "alternative"}))

            # Level-space comparison, so the two transformations are scored in one metric.
            if self.config.get("robustness.transformation.report_level_errors", True):
                for model in frames:
                    for kind, frame in (("baseline", baseline_frames.get(model)),
                                        ("alternative", frames.get(model))):
                        if frame is None or frame.empty:
                            continue
                        indexed = frame.set_index("target_date")
                        if ((kind == "baseline" and baseline_kind == "difference")
                                or (kind == "alternative" and alternative_kind == "difference")):
                            previous = level.shift(1).reindex(indexed.index)
                            level_forecast = previous + indexed["forecast"]
                        else:
                            level_forecast = indexed["forecast"]
                        actual_level = level.reindex(indexed.index)
                        error = (actual_level - level_forecast).to_numpy(dtype=float)
                        rows.append({
                            "series": series_id, "model": model, "horizon": horizon,
                            "exercise": "T4.1 transformation robustness",
                            "role": f"{kind}_in_level_units",
                            "transformation": (baseline_kind if kind == "baseline"
                                               else alternative_kind),
                            "units": "percent (level space)",
                            "n": int(np.isfinite(error).sum()),
                            "rmse": metrics.rmse(error), "mae": metrics.mae(error),
                        })
        self._write(pd.DataFrame(rows), self.layout.robustness,
                    "T4.1_transformation_robustness.csv", stage)
        self._write(pd.DataFrame(tests), self.layout.robustness,
                    "T4.1_transformation_predictive_tests.csv", stage)

    def _t42_cpi_lags(self, stage: StageOutputs, benchmark: str) -> None:
        """T4.2: the CPI AR-lag benchmark, p in {1,3,6,12}, on common forecast dates."""
        settings = self.config.get("robustness.cpi_lags")
        series_id = str(settings["series"])
        rows, tests = [], []
        if series_id in self.targets:
            frequency = self.frequency[series_id]
            target = self.targets[series_id]
            horizon = int(self.config.get(f"forecasting.horizons.primary.{frequency}"))
            window_length = self._window(frequency)
            jobs = [self._job(series_id, ModelSpec(AR, order=int(order)), [horizon],
                              window_length, tag=f"AR(p={int(order)})")
                    for order in settings["ar_orders"]]
            frames = {}
            for name, chain in self._chains(jobs):
                frame = chain.forecasts[chain.forecasts["horizon"] == horizon].copy()
                frame["model"] = name
                frames[name] = frame

            # Common forecast dates across all four lag variants, as the exercise requires.
            aligned = alignment.across_models(frames)
            restricted = {name: alignment.restrict(frame, aligned.dates)
                          for name, frame in frames.items()}
            baseline_order = self.specs[series_id][AR].order
            baseline_name = f"AR(p={baseline_order})"
            reference = baseline_name if baseline_name in restricted else sorted(restricted)[0]
            extra = {"exercise": "T4.2 CPI AR-lag robustness", "varied": "AR lag only",
                     "common_dates": aligned.n_common,
                     "baseline_ar_lag": baseline_order,
                     "common_first_target": (aligned.dates.min() if aligned.n_common else None),
                     "common_last_target": (aligned.dates.max() if aligned.n_common else None)}
            rows.extend(self._accuracy_rows(restricted, reference, series_id, horizon, extra))
            tests.extend(self._predictive_rows(restricted, reference, series_id, horizon, extra))
        self._write(pd.DataFrame(rows), self.layout.robustness, "T4.2_cpi_lag_robustness.csv", stage)
        self._write(pd.DataFrame(tests), self.layout.robustness,
                    "T4.2_cpi_lag_predictive_tests.csv", stage)

    def _t43_regime_count(self, stage: StageOutputs, benchmark: str) -> None:
        """T4.3: K=2 against K=3, including the explicit retention decision."""
        rows = []
        for series_id in self._selected_targets():
            frequency = self.frequency[series_id]
            fits = getattr(self, "full_sample_fits", {}).get(series_id, {})
            for horizon in self._horizons(frequency):
                frames = self._horse_race(series_id, horizon)
                k3 = self.forecasts[series_id].get(MSAR3)
                if k3 is not None and not k3.empty:
                    frames = {**frames, MSAR3: k3[k3["horizon"] == horizon]}
                accuracy = metrics.accuracy_table(frames, benchmark, series=series_id,
                                                  horizon=horizon)
                for model in (MSAR, MSAR3):
                    if model not in frames:
                        continue
                    match = accuracy[accuracy["model"] == model]
                    chain = self.chain_results[series_id][model]
                    fit = fits.get(model, (None,))[0]
                    row = {
                        "series": series_id, "horizon": horizon, "model": model,
                        "k_regimes": self.specs[series_id][model].k_regimes,
                        "role": "baseline" if model == MSAR else "robustness",
                        "spec_label": self.specs[series_id][model].label,
                        "full_sample_bic": getattr(fit, "bic", float("nan")) if fit else float("nan"),
                        "full_sample_converged": (fit.record.converged if fit else False),
                        "full_sample_status": (fit.record.status.value if fit else "failed"),
                        "occupancy": ("; ".join(f"regime{i+1}={v:.4f}"
                                                for i, v in enumerate(fit.occupancy))
                                      if fit else ""),
                        "transition_diagonal": ("; ".join(f"p{i+1}{i+1}={fit.P[i, i]:.4f}"
                                                          for i in range(fit.k_regimes))
                                                if fit else ""),
                        "min_expected_duration": (float(np.min(fit.expected_duration))
                                                  if fit else float("nan")),
                        "attempted_origins": chain.attempted, "valid_origins": chain.valid,
                        "failed_origins": chain.failed,
                    }
                    if not match.empty:
                        row.update({k: v for k, v in match.iloc[0].to_dict().items()
                                    if k not in ("series", "model", "horizon")})
                    rows.append(row)
        frame = pd.DataFrame(rows)
        if not frame.empty:
            # The retention decision is mechanical and predeclared: K=2 remains the
            # baseline regardless of which fits better, because Part 5 fixes the baseline
            # regime count. K=3 is reported as a robustness check only, and the field
            # records what the comparison showed (Part 5 §11.3, decision D13).
            decisions = {}
            for (series_id, horizon), group in frame.groupby(["series", "horizon"]):
                two = group[group["model"] == MSAR]
                three = group[group["model"] == MSAR3]
                if two.empty or three.empty:
                    verdict = "K=2 retained as baseline; K=3 unavailable"
                elif (str(three.iloc[0]["full_sample_status"]) == Status.FAILED.value
                      or not bool(three.iloc[0]["full_sample_converged"])):
                    verdict = "K=2 retained as baseline; K=3 did not fit adequately"
                else:
                    bic3 = float(three.iloc[0]["full_sample_bic"])
                    bic2 = float(two.iloc[0]["full_sample_bic"])
                    verdict = ("K=2 retained as baseline; K=3 improves full-sample BIC "
                               f"({bic3:.2f} vs {bic2:.2f}) and is reported as robustness only"
                               if bic3 < bic2 else
                               "K=2 retained as baseline; K=3 does not improve full-sample BIC "
                               f"({bic3:.2f} vs {bic2:.2f})")
                decisions[(series_id, horizon)] = verdict
            frame["retention_decision"] = [
                decisions.get((r.series, r.horizon), "") for r in frame.itertuples()]
        self._write(frame, self.layout.robustness, "T4.3_regime_count.csv", stage)

    def _t44_horizons(self, stage: StageOutputs, benchmark: str) -> None:
        """T4.4: horizon robustness from the stored forecasts (no re-estimation)."""
        rows, tests = [], []
        for series_id in self._selected_targets():
            frequency = self.frequency[series_id]
            primary = int(self.config.get(f"forecasting.horizons.primary.{frequency}"))
            for horizon in self._horizons(frequency):
                frames = self._horse_race(series_id, horizon)
                extra = {"exercise": "T4.4 horizon robustness", "frequency": frequency,
                         "role": "baseline" if horizon == primary else "robustness",
                         "source": "stored baseline forecasts, no re-estimation"}
                rows.extend(self._accuracy_rows(frames, benchmark, series_id, horizon, extra))
                tests.extend(self._predictive_rows(frames, benchmark, series_id, horizon, extra))
        self._write(pd.DataFrame(rows), self.layout.robustness, "T4.4_horizon_robustness.csv", stage)
        self._write(pd.DataFrame(tests), self.layout.robustness,
                    "T4.4_horizon_predictive_tests.csv", stage)

    def _transformed(self, series_id: str) -> pd.Series:
        """The modelling transformation of one series, computed on demand.

        The VAR needs all five monthly variables even when the run evaluates a subset of
        targets, so a variable outside the current target set is transformed here by the
        same approved rules rather than being dropped.
        """
        if series_id in self.targets:
            return self.targets[series_id]
        spec = self.config.get(f"targets.{series_id}")
        frequency = spec["frequency"]
        level = self.panels[frequency][series_id].dropna()
        if spec["transform"]["kind"] == "logdiff_annualized":
            return annualized_logdiff(level, float(spec["transform"]["k"])).dropna()
        decision = self.decisions.get(series_id)
        if decision is None:
            initial = level.iloc[: self._window(frequency)]
            decision = decide_transformation(series_id, initial, frequency, self.config)
            decision = confirm_on_full_sample(decision, level, frequency, self.config)
            self.decisions[series_id] = decision
            self.all_tests.extend(decision.initial_window_results)
            self.all_tests.extend(decision.full_sample_results)
        return level if decision.decision == "level" else level.diff().dropna()

    def _var_panel(self) -> pd.DataFrame:
        """The balanced five-variable monthly system on the approved VAR sample."""
        names = list(self.config.get("models.var.variables"))
        frame = pd.DataFrame({name: self._transformed(name) for name in names}).dropna()
        start = pd.Timestamp(self.config.get("samples.var_start"))
        end = pd.Timestamp(self.config.get("samples.var_end"))
        return frame.loc[(frame.index >= start) & (frame.index <= end)]

    def _t45_var(self, stage: StageOutputs, benchmark: str) -> None:
        """T4.5: the monthly VAR against the univariate benchmark on identical dates."""
        panel = self._var_panel()
        rows, tests, selection_rows = [], [], []
        if panel.empty or len(panel) <= self._window("M"):
            self._write(pd.DataFrame(rows), self.layout.robustness,
                        "T4.5_var_comparison.csv", stage)
            self._write(pd.DataFrame([{
                "exercise": "T4.5 monthly VAR", "available": False,
                "reason": ("the five-variable monthly system has "
                           f"{len(panel)} balanced rows, which is not enough for a "
                           f"{self._window('M')}-observation rolling window")}]),
                self.layout.robustness, "T4.5_var_selection.csv", stage)
            return

        window_length = self._window("M")
        horizon = int(self.config.get("forecasting.horizons.primary.M"))
        candidates = [int(p) for p in self.config.get("models.var.lags")]
        require_stability = bool(self.config.get("models.var.require_stability"))

        # Lag order is selected once, on the initial estimation window, exactly as the
        # univariate discrete specifications are (Part 5 §9.2).
        initial = panel.iloc[:window_length]
        best_order, best_bic, candidate_notes = None, np.inf, []
        for order in candidates:
            fit = fit_var(initial, order, refit_date=str(initial.index[-1].date()))
            stable = fit.is_stable
            candidate_notes.append({
                "exercise": "T4.5 monthly VAR", "candidate_lag": order, "bic": fit.bic,
                "aic": fit.aic, "stable": stable,
                "max_companion_modulus": float(fit.companion_moduli().max()),
                "eligible": bool(stable or not require_stability),
                "selected": False,
            })
            if (stable or not require_stability) and np.isfinite(fit.bic) and fit.bic < best_bic:
                best_order, best_bic = order, fit.bic
        if best_order is None:
            for note in candidate_notes:
                note["selected"] = False
            self._write(pd.DataFrame(candidate_notes), self.layout.robustness,
                        "T4.5_var_selection.csv", stage)
            self._write(pd.DataFrame([{
                "exercise": "T4.5 monthly VAR", "available": False,
                "reason": "no candidate VAR lag order produced a stable system"}]),
                self.layout.robustness, "T4.5_var_comparison.csv", stage)
            return
        for note in candidate_notes:
            note["selected"] = note["candidate_lag"] == best_order
        selection_rows.extend(candidate_notes)

        origins = rolling_origins(pd.DatetimeIndex(panel.index), window_length, horizon,
                                  max_origins=self._max_origins())
        records: list[dict[str, Any]] = []
        unstable, attempted = 0, 0
        for origin in origins:
            attempted += 1
            window = panel.iloc[origin.estimation_slice()]
            fit = fit_var(window, best_order, refit_date=str(origin.origin_date.date()))
            self.all_fit_records.append(fit.record)
            if fit.record.status is Status.FAILED:
                unstable += 1
                for code in fit.record.reason_codes:
                    self.all_failures.append(FailureEvent(
                        series="+".join(panel.columns), model="VAR",
                        refit_date=str(origin.origin_date.date()), horizon=horizon,
                        category=Status.FAILED, reason_code=code,
                        raw_diagnostic=str(fit.record.diagnostics.get(
                            f"flag_{code.value}", ""))[:200],
                        forecast_retained=False, figure_separated=True))
                continue
            prediction = fit.forecast(window.to_numpy(dtype=float), horizon)[horizon - 1]
            for position, name in enumerate(panel.columns):
                actual = float(panel.iloc[origin.target_position, position])
                records.append({
                    "series": name, "model": "VAR", "spec_label": f"VAR(p={best_order})",
                    "window_length": window_length, "origin_date": origin.origin_date,
                    "target_date": origin.target_date, "horizon": horizon,
                    "forecast": float(prediction[position]), "actual": actual,
                    "error": actual - float(prediction[position]),
                    "status": fit.record.status.value,
                    "reason_codes": ";".join(c.value for c in fit.record.reason_codes),
                })
        var_frame = pd.DataFrame(records)
        self._write(var_frame, self.layout.robustness, "T4.5_var_forecasts.csv", stage)

        for name in panel.columns:
            if name not in self.forecasts:
                continue
            univariate = self._horse_race(name, horizon)
            if benchmark not in univariate:
                continue
            frames = dict(univariate)
            subset = var_frame[var_frame["series"] == name]
            if not subset.empty:
                frames["VAR"] = subset
            aligned = alignment.across_models(frames)
            restricted = {model: alignment.restrict(frame, aligned.dates)
                          for model, frame in frames.items()}
            extra = {"exercise": "T4.5 monthly VAR cross-variable comparison",
                     "var_lag": best_order, "var_stability_required": require_stability,
                     "var_unstable_origins": unstable, "var_attempted_origins": attempted,
                     "common_dates": aligned.n_common,
                     "comparison_rule": "identical common target dates across all models"}
            accuracy = self._accuracy_rows(restricted, benchmark, name, horizon, extra)
            ranked = sorted([r for r in accuracy if np.isfinite(r.get("rmse", np.nan))],
                            key=lambda r: r["rmse"])
            order_map = {r["model"]: position + 1 for position, r in enumerate(ranked)}
            univariate_only = sorted(
                [r for r in accuracy
                 if r["model"] != "VAR" and np.isfinite(r.get("rmse", np.nan))],
                key=lambda r: r["rmse"])
            univariate_rank = {r["model"]: position + 1
                               for position, r in enumerate(univariate_only)}
            for row in accuracy:
                row["rank_with_var"] = order_map.get(row["model"])
                row["rank_univariate_only"] = univariate_rank.get(row["model"])
                row["rank_changed_by_var"] = (
                    row["rank_with_var"] != row["rank_univariate_only"]
                    if row["rank_with_var"] and row["rank_univariate_only"] else None)
            rows.extend(accuracy)
            tests.extend(self._predictive_rows(restricted, benchmark, name, horizon, extra))

        self._write(pd.DataFrame(selection_rows), self.layout.robustness,
                    "T4.5_var_selection.csv", stage)
        self._write(pd.DataFrame(rows), self.layout.robustness, "T4.5_var_comparison.csv", stage)
        self._write(pd.DataFrame(tests), self.layout.robustness,
                    "T4.5_var_predictive_tests.csv", stage)

    def _t46_arma_garch(self, stage: StageOutputs) -> None:
        """T4.6: the conditional-variance diagnostic, triggered by the initial-window ARCH-LM.

        Decision M9: where triggered, the full rolling out-of-sample chain is run so the
        'did the mean forecast change?' question is answered on the same origins, but the
        model never enters the horse race or the MCS.
        """
        rows, trigger_rows = [], []
        for series_id in self._selected_targets():
            frequency = self.frequency[series_id]
            target = self.targets[series_id]
            window_length = self._window(frequency)
            spec = self.specs[series_id][ARMA]
            initial = target.iloc[:window_length]
            arma = fit_arma(initial, (spec.order, spec.ma_order), series=series_id,
                            refit_date=str(initial.index[-1].date()))
            arch_lag = int(self.config.get(f"diagnostics.arch_lm_lags.{frequency}"))
            screen = residual_tests.arch_lm(arma.residuals, arch_lag, series=series_id,
                                            model=f"ARMA{spec.order},{spec.ma_order}")
            self.all_tests.append(screen)
            triggered = screen.decision_5pct == "reject"
            trigger_rows.append({
                "series": series_id, "arma_order": f"({spec.order},{spec.ma_order})",
                "arch_lm_lags": arch_lag, "arch_lm_statistic": screen.statistic,
                "arch_lm_p_value": screen.p_value, "decision_5pct": screen.decision_5pct,
                "triggered": triggered,
                "trigger_rule": str(self.config.get("models.arma_garch.trigger")),
                "in_horse_race": bool(self.config.get("models.arma_garch.in_horse_race")),
                "in_mcs": bool(self.config.get("models.arma_garch.in_mcs")),
                "window": "initial estimation window",
            })
            if not triggered:
                continue

            horizon = int(self.config.get(f"forecasting.horizons.primary.{frequency}"))
            origins = rolling_origins(pd.DatetimeIndex(target.index), window_length, horizon,
                                      max_origins=self._max_origins())
            garch_records, mean_records = [], []
            for origin in origins:
                window = target.iloc[origin.estimation_slice()]
                fit = fit_arma_garch(window, (1, 1), series=series_id,
                                     refit_date=str(origin.origin_date.date()))
                self.all_fit_records.append(fit.record)
                if fit.record.status is Status.FAILED:
                    for code in fit.record.reason_codes:
                        self.all_failures.append(FailureEvent(
                            series=series_id, model="ARMA-GARCH",
                            refit_date=str(origin.origin_date.date()), horizon=horizon,
                            category=Status.FAILED, reason_code=code,
                            raw_diagnostic=str(fit.record.optimizer_message or "")[:200],
                            forecast_retained=False, figure_separated=True))
                    continue
                prediction = float(fit.forecast_mean(horizon)[horizon - 1])
                actual = float(target.iloc[origin.target_position])
                standardized = fit.standardized_residuals
                battery = residual_tests.adequacy_suite(
                    standardized, frequency, self.config, model="ARMA-GARCH-std",
                    series=series_id, order=1, ma_order=1)
                primary_lb = residual_tests.primary_ljung_box(battery, frequency, self.config)
                arch_on_std = next(r for r in battery if r.name.startswith("ARCH-LM"))
                garch_records.append({
                    "series": series_id, "model": "ARMA-GARCH",
                    "origin_date": origin.origin_date, "target_date": origin.target_date,
                    "horizon": horizon, "forecast": prediction, "actual": actual,
                    "error": actual - prediction,
                    "omega": fit.params.get("omega"), "alpha": fit.params.get("alpha"),
                    "beta": fit.params.get("beta"), "persistence": fit.persistence,
                    "loglik": fit.loglik, "aic": fit.aic, "bic": fit.bic,
                    "converged": fit.record.converged, "status": fit.record.status.value,
                    "std_resid_ljung_box_p": primary_lb.p_value,
                    "std_resid_arch_lm_p": arch_on_std.p_value,
                    "excluded_from_horse_race": True, "excluded_from_mcs": True,
                })
                mean_records.append((origin.target_date, prediction))

            garch_frame = pd.DataFrame(garch_records)
            self._write(garch_frame, self.layout.robustness,
                        f"T4.6_arma_garch_{series_id}.csv", stage)
            if garch_frame.empty:
                continue
            arma_frame = self.forecasts[series_id].get(ARMA)
            comparison = None
            if arma_frame is not None and not arma_frame.empty:
                arma_h = arma_frame[arma_frame["horizon"] == horizon].set_index("target_date")
                joined = garch_frame.set_index("target_date").join(
                    arma_h["forecast"].rename("arma_forecast"), how="inner")
                difference = (joined["forecast"] - joined["arma_forecast"]).to_numpy(dtype=float)
                comparison = {
                    "n_common": int(np.isfinite(difference).sum()),
                    "mean_absolute_mean_forecast_change": float(np.nanmean(np.abs(difference))),
                    "max_absolute_mean_forecast_change": float(np.nanmax(np.abs(difference)))
                    if difference.size else float("nan"),
                    "arma_rmse": metrics.rmse(
                        (joined["actual"] - joined["arma_forecast"]).to_numpy(dtype=float)),
                    "garch_rmse": metrics.rmse(joined["error"].to_numpy()),
                }
            rows.append({
                "series": series_id, "exercise": "T4.6 ARCH/GARCH diagnostic",
                "triggered": True, "n_origins": len(garch_frame),
                "n_converged": int(garch_frame["converged"].sum()),
                "mean_persistence": float(garch_frame["persistence"].mean()),
                "max_persistence": float(garch_frame["persistence"].max()),
                "mean_alpha": float(garch_frame["alpha"].mean()),
                "mean_beta": float(garch_frame["beta"].mean()),
                "std_resid_arch_lm_rejection_rate": float(
                    (garch_frame["std_resid_arch_lm_p"] < 0.05).mean()),
                "std_resid_ljung_box_rejection_rate": float(
                    (garch_frame["std_resid_ljung_box_p"] < 0.05).mean()),
                "rmse": metrics.rmse(garch_frame["error"].to_numpy(dtype=float)),
                "mae": metrics.mae(garch_frame["error"].to_numpy(dtype=float)),
                "excluded_from_horse_race": True, "excluded_from_mcs": True,
                "mean_forecast_changed_note": (
                    "conditional-variance modelling leaves the conditional mean forecast "
                    "numerically different but is a diagnostic only; see the per-origin file"),
                **(comparison or {}),
            })
        self._write(pd.DataFrame(trigger_rows), self.layout.robustness,
                    "T4.6_arch_trigger.csv", stage)
        self._write(pd.DataFrame(rows), self.layout.robustness,
                    "T4.6_arma_garch_summary.csv", stage)

    def _t48_window_lengths(self, stage: StageOutputs, benchmark: str) -> None:
        """T4.8: the mandatory estimation-window-length sensitivity exercise.

        The discrete baseline specifications are reused unchanged at every length; only
        the rolling-window length varies, and every length is scored on the common
        calendar implied by the longest window.
        """
        settings = self.config.require("robustness.window_lengths")
        models = [str(m) for m in settings["models"]]
        comparison_rows, test_rows, audit_rows, mcs_rows = [], [], [], []
        confidences = [float(c) for c in self.config.get("evaluation.mcs.confidence_levels")]

        for series_id in self._selected_targets():
            frequency = self.frequency[series_id]
            target = self.targets[series_id]
            horizon = int(settings["horizon"])
            lengths = [int(length) for length in settings["lengths"][frequency]]
            baseline_length = int(settings["baseline"][frequency])
            index = pd.DatetimeIndex(target.index)
            usable = [length for length in lengths if len(index) > length + horizon]
            if not usable:
                continue
            calendar = common_calendar(index, usable, horizon)
            coverage = describe_coverage(index, usable, horizon)

            jobs = [self._job(series_id, model, [horizon], length, tag=(length, model))
                    for length in usable for model in models]
            chains = dict(self._chains(jobs))

            per_length: dict[int, dict[str, pd.DataFrame]] = {}
            for length in usable:
                frames: dict[str, pd.DataFrame] = {}
                for model in models:
                    spec = self.specs[series_id][model]
                    chain = chains[(length, model)]
                    frame = chain.forecasts
                    frame = frame[frame["horizon"] == horizon] if not frame.empty else frame
                    restricted = (alignment.restrict(frame, calendar)
                                  if not frame.empty else frame)
                    frames[model] = restricted
                    status_counts = {status.value: 0 for status in Status}
                    for record in chain.fit_records:
                        status_counts[record.status.value] += 1
                    reasons: dict[str, int] = {}
                    for event in chain.failures:
                        reasons[event.reason_code.value] = reasons.get(
                            event.reason_code.value, 0) + 1
                    audit_rows.append({
                        "series": series_id, "frequency": frequency, "model": model,
                        "horizon": horizon, "window_length": length,
                        "role": ("baseline" if length == baseline_length
                                 else "shorter" if length < baseline_length else "longer"),
                        "baseline_specification_id": spec.label,
                        "spec_fixed_from": "initial baseline estimation window",
                        "reselected_specification": bool(
                            settings.get("research_specs_per_length", False)),
                        "attempted_origins": chain.attempted,
                        "valid_origins": chain.valid, "failed_origins": chain.failed,
                        "n_data_gaps": len(chain.data_gaps),
                        "from_cache": chain.from_cache,
                        "n_on_common_calendar": len(restricted),
                        "n_adequate": status_counts[Status.ADEQUATE.value],
                        "n_fragile": status_counts[Status.FRAGILE.value],
                        "n_failed": status_counts[Status.FAILED.value],
                        "rate_adequate": (status_counts[Status.ADEQUATE.value]
                                          / max(len(chain.fit_records), 1)),
                        "rate_fragile": (status_counts[Status.FRAGILE.value]
                                         / max(len(chain.fit_records), 1)),
                        "rate_failed": (status_counts[Status.FAILED.value]
                                        / max(len(chain.fit_records), 1)),
                        "reason_codes": "; ".join(f"{k}={v}" for k, v in sorted(reasons.items())),
                        "first_eligible_common_target": (calendar.min() if len(calendar) else None),
                        "last_eligible_common_target": (calendar.max() if len(calendar) else None),
                        "own_first_target": coverage[length]["first_target"],
                        "own_last_target": coverage[length]["last_target"],
                        "n_origins_all": coverage[length]["n_origins"],
                        "matched_date_rule": "common calendar from the longest candidate window",
                        "master_seed": int(self.config.get("run.master_seed")),
                        "config_hash": self.config.hash,
                    })
                per_length[length] = frames

            # Scoring, ranks and inference per length. The baseline length is scored
            # first so every other length has a reference to be compared against; the
            # shorter window would otherwise be classified "unavailable" purely because
            # of the order of the list.
            baseline_support: dict[tuple[str, str], tuple[float, bool]] = {}
            ordered = ([baseline_length] if baseline_length in usable else []) + \
                [length for length in usable if length != baseline_length]
            for length in ordered:
                frames = {m: f for m, f in per_length[length].items() if not f.empty}
                if benchmark not in frames:
                    continue
                role = ("baseline" if length == baseline_length
                        else "shorter" if length < baseline_length else "longer")
                extra = {"window_length": length, "role": role, "frequency": frequency,
                         "baseline_window_length": baseline_length,
                         "baseline_specification_id": self.specs[series_id][AR].label,
                         "exercise": "T4.8 estimation-window-length robustness",
                         "matched_date_rule": "common calendar from the longest window",
                         "n_common_calendar": len(calendar),
                         "first_common_target": (calendar.min() if len(calendar) else None),
                         "last_common_target": (calendar.max() if len(calendar) else None)}
                accuracy = self._accuracy_rows(frames, benchmark, series_id, horizon, extra)
                for loss_kind in self.config.get("evaluation.losses"):
                    ranked = sorted(
                        [r for r in accuracy if np.isfinite(r.get("rmse", np.nan))],
                        key=lambda r: r["rmse" if loss_kind == SQUARED else "mae"])
                    for position, row in enumerate(ranked):
                        row[f"rank_{loss_kind}"] = position + 1
                comparison_rows.extend(accuracy)

                predictive = self._predictive_rows(frames, benchmark, series_id, horizon, extra)
                for row in predictive:
                    key = (row["model"], row["loss"])
                    mean_d = row["mean_loss_differential"]
                    supported = bool(row["hlz_available"]
                                     and row["hlz_decision_5pct"] == "reject")
                    if length == baseline_length:
                        baseline_support[key] = (mean_d, supported)
                    reference = baseline_support.get(key)
                    if reference is None:
                        row["conclusion_vs_baseline"] = "unavailable"
                        row["support_change"] = "no_change"
                        row["notes"] = "the baseline window result is not available for this pair"
                    else:
                        verdict = tp_sensitivity.classify(
                            reference[0], reference[1], mean_d, supported,
                            baseline_available=np.isfinite(reference[0]),
                            alternative_available=np.isfinite(mean_d))
                        row.update(verdict.to_row())
                    if length == baseline_length:
                        row["conclusion_vs_baseline"] = "unchanged"
                        row["notes"] = "this is the baseline window"
                test_rows.extend(predictive)

                for loss_kind in self.config.get("evaluation.losses"):
                    for confidence in confidences:
                        result = model_confidence_set(frames, loss_kind, confidence,
                                                      self.config, series=series_id,
                                                      horizon=horizon)
                        for row in result.to_rows():
                            row.update({"window_length": length, "role": role,
                                        "exercise": "T4.8 estimation-window-length robustness"})
                            mcs_rows.append(row)

            frame = pd.DataFrame([r for r in comparison_rows if r.get("series") == series_id])
            if not frame.empty and "oos_r2_vs_benchmark" in frame.columns:
                self._save_figure(
                    figures.window_length_sensitivity(frame, series_id=series_id,
                                                      baseline_length=baseline_length,
                                                      benchmark=benchmark),
                    self.layout.figures, f"F4.8_{series_id}", stage,
                    {"figure_id": "F4.8", "series": series_id,
                     "baseline_window_length": baseline_length})

        outputs = settings["outputs"]
        self._write(pd.DataFrame(comparison_rows), self.layout.robustness,
                    str(outputs["comparison"]), stage)
        self._write(pd.DataFrame(test_rows), self.layout.robustness,
                    str(outputs["predictive_tests"]), stage)
        self._write(pd.DataFrame(audit_rows), self.layout.robustness,
                    str(outputs["origin_audit"]), stage)
        self._write(pd.DataFrame(mcs_rows), self.layout.robustness,
                    "window_length_mcs.csv", stage)

    def _imputed_dates(self, series_id: str) -> list[pd.Timestamp]:
        frame = self.bundle.frame
        subset = frame[(frame["series_id"] == series_id)
                       & (frame["observation_status"] == STATUS_IMPUTED)]
        return [pd.Timestamp(d) for d in subset["date"]]

    def _affected_transformed_dates(self, series_id: str) -> set[pd.Timestamp]:
        """Transformed observations whose value depends on an imputed raw level."""
        raw = self._imputed_dates(series_id)
        if not raw:
            return set()
        index = pd.DatetimeIndex(self.targets[series_id].index)
        positions = {date: position for position, date in enumerate(index)}
        affected: set[pd.Timestamp] = set()
        spec = self.config.get(f"targets.{series_id}")
        uses_predecessor = (spec["transform"]["kind"] == "logdiff_annualized"
                            or (self.decisions.get(series_id) is not None
                                and self.decisions[series_id].decision == "difference"))
        for date in raw:
            if date in positions:
                affected.add(date)
                if uses_predecessor:
                    successor = positions[date] + 1
                    if successor < len(index):
                        affected.add(index[successor])
            elif uses_predecessor:
                # The imputed level itself may precede the first transformed observation.
                later = index[index > date]
                if len(later):
                    affected.add(later[0])
        return affected

    def _t49_locf_exposure(self, stage: StageOutputs) -> None:
        """T4.9: per-origin exposure of each forecast to the approved October 2025 LOCF."""
        settings = self.config.require("robustness.locf_exposure")
        benchmark = str(self.config.get("evaluation.benchmark"))
        rows, summary_rows = [], []
        for series_id in self._selected_targets():
            frequency = self.frequency[series_id]
            affected = self._affected_transformed_dates(series_id)
            raw_imputed = self._imputed_dates(series_id)
            target = self.targets[series_id]
            index = pd.DatetimeIndex(target.index)
            positions = {date: position for position, date in enumerate(index)}
            window_length = self._window(frequency)

            for model, frame in self.forecasts[series_id].items():
                if frame.empty:
                    continue
                spec = self.specs[series_id][model]
                lag_depth = max(spec.order, spec.delay if model == STAR else 0, 1)
                for row in frame.to_dict("records"):
                    origin_position = positions.get(pd.Timestamp(row["origin_date"]))
                    target_date = pd.Timestamp(row["target_date"])
                    if origin_position is None:
                        continue
                    lag_dates = set(index[max(0, origin_position - lag_depth + 1):
                                          origin_position + 1])
                    window_dates = set(index[max(0, origin_position - window_length + 1):
                                             origin_position + 1])
                    target_imputed = target_date in {d for d in raw_imputed}
                    rows.append({
                        "series": series_id, "model": model, "spec_label": spec.label,
                        "horizon": row["horizon"], "origin_date": row["origin_date"],
                        "target_date": row["target_date"],
                        "target_imputed": target_imputed,
                        "target_transformation_uses_imputed_predecessor": bool(
                            target_date in affected and not target_imputed),
                        "predictor_lag_contains_imputed": bool(lag_dates & affected),
                        "estimation_window_contains_imputed": bool(window_dates & affected),
                        "lag_depth_used": lag_depth,
                        "window_length": row["window_length"],
                        "forecast": row["forecast"], "actual": row["actual"],
                        "error": row["error"],
                        "squared_loss": (row["error"] ** 2
                                         if np.isfinite(row["error"]) else float("nan")),
                        "absolute_loss": (abs(row["error"])
                                          if np.isfinite(row["error"]) else float("nan")),
                        "forecast_status": row["status"],
                        "forecast_valid": bool(np.isfinite(row["forecast"])),
                        "reason_codes": row["reason_codes"],
                        "imputed_raw_dates": ";".join(d.strftime("%Y-%m-%d") for d in raw_imputed),
                    })

            # Descriptive accuracy on the full approved sample and on the unaffected
            # pre-gap dates, for the primary horizon only.
            horizon = int(self.config.get(f"forecasting.horizons.primary.{frequency}"))
            frames = self._horse_race(series_id, horizon)
            if benchmark not in frames:
                continue
            earliest_affected = min(affected) if affected else None
            for sample in settings["comparison_samples"]:
                if sample == "full_approved":
                    subset = frames
                else:
                    if earliest_affected is None:
                        continue
                    subset = {model: frame[pd.DatetimeIndex(frame["target_date"])
                                           < earliest_affected]
                              for model, frame in frames.items()}
                    subset = {m: f for m, f in subset.items() if not f.empty}
                if benchmark not in subset:
                    continue
                accuracy = self._accuracy_rows(
                    subset, benchmark, series_id, horizon,
                    {"exercise": "T4.9 LOCF forecast-exposure diagnostic",
                     "sample": sample,
                     "headline_inference_sample": str(settings["headline_inference_sample"]),
                     "inference_role": ("headline inference, unchanged"
                                        if sample == settings["headline_inference_sample"]
                                        else "descriptive diagnostic only"),
                     "n_imputed_raw_cells": len(raw_imputed),
                     "n_affected_transformed_dates": len(affected),
                     "first_target": min((pd.Timestamp(f["target_date"].min())
                                          for f in subset.values()), default=None),
                     "last_target": max((pd.Timestamp(f["target_date"].max())
                                         for f in subset.values()), default=None),
                     "caveat": (
                         "dropping the directly affected realized target dates does not "
                         "remove indirect exposure through the estimation window or the "
                         "predictor lag vector; power on the shorter sample is lower and "
                         "no baseline endpoint or LOCF assumption is reconsidered here")})
                ranked = sorted([r for r in accuracy if np.isfinite(r.get("rmse", np.nan))],
                                key=lambda r: r["rmse"])
                for position, row in enumerate(ranked):
                    row["rank_rmse"] = position + 1
                summary_rows.extend(accuracy)

        self._write(pd.DataFrame(rows), self.layout.data_audit,
                    str(settings["output"]), stage, parquet=True)
        self._write(pd.DataFrame(summary_rows), self.layout.data_audit,
                    "T4.9_locf_sample_comparison.csv", stage)

    # -- stage 9: registries, claim matrix, logs ---------------------------

    def finalize(self) -> StageOutputs:
        stage = StageOutputs("tables_and_figures")
        with self.runtime.stage("finalize"):
            # T4.7 failure and fragility registry, plus the separate data-gap register.
            self._write(tables.failure_registry_table(self.all_failures),
                        self.layout.robustness, "T4.7_failure_registry.csv", stage)
            self._write(tables.data_gap_table(self.all_gaps), self.layout.data_audit,
                        "data_gap_register.csv", stage)
            self._write(tables.fit_records_table(self.all_fit_records), self.layout.models,
                        "fit_records.csv", stage, parquet=True)
            self._write(tables.test_table(self.all_tests), self.layout.diagnostics,
                        "all_test_results.csv", stage)

            counts = {}
            for record in self.all_fit_records:
                key = (record.series, record.model, record.status.value)
                counts[key] = counts.get(key, 0) + 1
            self._write(pd.DataFrame(
                [{"series": s, "model": m, "status": st, "n": n}
                 for (s, m, st), n in sorted(counts.items())]),
                self.layout.robustness, "T4.7_status_counts.csv", stage)

            # Part 8 claim matrix: the schema is created here with its rows left for
            # Part 8, which is where claims are adjudicated. Claude must not fill the
            # status column during Part 6 (CLAUDE.md §6, result-blind rule).
            matrix = tables.empty_claim_matrix()
            problems = tables.validate_claim_matrix(matrix)
            if problems:
                raise RuntimeError(f"claim matrix schema is invalid: {problems}")
            self._write(matrix, self.layout.manifests, "claim_evidence_matrix.csv", stage)

            self.context.write_run_manifest(self.layout)

        # The execution log, the checkpoint summary and the output inventory are written
        # after the timing context closes, so the log covers the finalize stage too and
        # the inventory covers every file the run produced, itself included.
        self.checkpoints.record("tables_and_figures",
                                {"stages": [s.name for s in self.stage_outputs]},
                                {"n_files": len(stage.files)})
        self._write(self.runtime.to_frame(), self.layout.logs, "runtime_log.csv", stage)
        self._write(pd.DataFrame(list(self.checkpoints.entries.values())),
                    self.layout.logs, "stage_checkpoints.csv", stage)
        inventory = []
        for produced in self.stage_outputs + [stage]:
            for relative in produced.files:
                path = self.layout.root / relative
                inventory.append({
                    "stage": produced.name, "path": relative,
                    "bytes": path.stat().st_size if path.exists() else 0,
                    "sha256": sha256_file(path) if path.exists() else "",
                })
        self._write(pd.DataFrame(inventory), self.layout.manifests,
                    "output_inventory.csv", stage)
        self.stage_outputs.append(stage)
        return stage

    # -- orchestration ----------------------------------------------------

    def run(self) -> dict[str, Any]:
        """Run every stage of the approved methodology, in order."""
        self.layout.create()
        self.prepare_data()
        self.stationarity_stage()
        self.specification_stage(final=False)   # AR/ARMA orders for the probe
        self.nonlinearity_stage()
        self.specification_stage()              # STAR delay/type now known; writes T2.5
        self.adequacy_stage()
        self.forecasting_stage()
        self.evaluation_stage()
        self.robustness_stage()
        self.finalize()
        return {
            "run_id": self.context.run_id,
            "namespace": self.context.namespace.value,
            "canonical_csv_sha256": self.identity.canonical_hash,
            "config_hash": self.config.hash,
            "stages": [s.name for s in self.stage_outputs],
            "n_files": sum(len(s.files) for s in self.stage_outputs),
            "n_fit_records": len(self.all_fit_records),
            "n_failure_events": len(self.all_failures),
            "n_data_gap_events": len(self.all_gaps),
            "n_test_results": len(self.all_tests),
            "runtime": self.runtime.to_frame().to_dict("records"),
        }
