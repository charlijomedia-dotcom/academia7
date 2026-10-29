"""The 29 October 2026 amendment: K=3 MSAR is an in-sample robustness model only.

Part 5 §11.1 (amended): K=2 remains the baseline; K=3 is estimated once on the full
sample for every target and compared in-sample (T4.3); K=3 is never a rolling forecast
chain, and no K=3 forecast metric exists. These tests pin the structural guarantees on
the real frozen data and all six targets, the T4.3 builder on real, failed and fragile
fits, and the fact that the change left every fit-cache key, and so every cached K=2
result, valid.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import pytest

from thesis.core.cache import code_hash
from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR, FROZEN_DIR, Namespace, output_layout
from thesis.core.provenance import RunContext
from thesis.core.schemas import FitRecord, ReasonCode, Status
from thesis.data.store import load_bundle
from thesis.models.msar import fit_msar
from thesis.models import flags
from thesis.pipeline import FULL_SAMPLE_MODELS, ROLLING_MODELS, Pipeline
from thesis.models.registry import AR, ARMA, MSAR, MSAR3, STAR, ModelSpec
from thesis.reporting import regime_count, tables

TARGETS = {"GDPC1", "CPIAUCSL", "UNRATE", "INDPRO", "FEDFUNDS", "M2SL"}

#: The fit-critical code hash at the approved commit 77b4c74, before the amendment. The
#: amendment changed no fit-critical file, so it must be unchanged: every cache key, and
#: so every cached AR, ARMA, MSAR (K=2) and STAR fit, stays valid. If a later change
#: legitimately alters a fit-critical file, update this pin and record that the cache is
#: invalidated.
PRE_AMENDMENT_CODE_HASH = "93ca1685fda15e4b28ee81f7addf9608c6ed70575e2439eb7ee204f4f10fef87"


@pytest.fixture(scope="module")
def specified():
    """The real baseline configuration on all six targets, through stage 5."""
    config = load_config(names=("baseline", "series_catalog", "thresholds"),
                         config_dir=CONFIG_DIR)
    bundle = load_bundle(FROZEN_DIR, config)
    root = Path(tempfile.mkdtemp())
    layout = type(output_layout(Namespace.SMOKE))(root=root / "out", cache=root / "cache")
    context = RunContext(namespace=Namespace.SMOKE, config_hash=config.hash,
                         data_snapshot_hash=bundle.data_input_identity,
                         data_cutoff=config.get("samples.monthly_end"),
                         vintage_date=config.get("run.vintage_date"))
    pipeline = Pipeline(config, context, layout, bundle, smoke=False, workers=4)
    layout.create()
    pipeline.prepare_data()
    pipeline.stationarity_stage()
    pipeline.specification_stage(final=False)
    pipeline.nonlinearity_stage()
    pipeline.specification_stage()
    return pipeline


class TestDesign:
    def test_k3_is_estimated_on_the_full_sample_and_never_rolled(self):
        assert MSAR3 in FULL_SAMPLE_MODELS
        assert MSAR3 not in ROLLING_MODELS
        assert ROLLING_MODELS == (AR, ARMA, MSAR, STAR)

    def test_every_target_has_a_k3_specification_with_the_k2_lag_order(self, specified):
        assert set(specified.specs) == TARGETS
        for series, specs in specified.specs.items():
            assert specs[MSAR3].k_regimes == 3 and specs[MSAR].k_regimes == 2
            assert specs[MSAR3].order == specs[MSAR].order, series

    def test_no_rolling_job_or_planned_chain_is_k3(self, specified):
        jobs = specified._rolling_jobs()
        assert not [job for job, *_ in jobs if job.spec.model == MSAR3]
        assert not [plan for plan in specified.rolling_plan() if plan.model == MSAR3]
        for series in TARGETS:
            batch, forecast_jobs = specified._forecast_jobs(series)
            assert [job.spec.model for job in forecast_jobs] == list(ROLLING_MODELS)

    def test_a_k3_rolling_job_is_refused(self, specified, monkeypatch):
        original = specified._forecast_jobs

        def with_k3(series_id):
            batch, jobs = original(series_id)
            frequency = specified.frequency[series_id]
            return batch, jobs + [specified._job(
                series_id, MSAR3, specified._horizons(frequency),
                specified._window(frequency), tag=MSAR3, batch=batch)]

        monkeypatch.setattr(specified, "_forecast_jobs", with_k3)
        with pytest.raises(RuntimeError, match="K=3 MSAR must not be a rolling chain"):
            specified._rolling_jobs()

    def test_the_exact_rolling_workload(self, specified):
        plans = specified.rolling_plan()
        assert len(plans) == 115                     # was 121 with six K=3 chains
        assert sum(p.n_origins for p in plans) == 68706          # was 72,233
        assert sum(p.n_origins for p in plans if not p.expect_cached) == 54598  # 58,125

    def test_k2_rolling_chains_are_unchanged(self, specified):
        for series in TARGETS:
            _, jobs = specified._forecast_jobs(series)
            msar = next(j for j in jobs if j.spec.model == MSAR)
            frequency = specified.frequency[series]
            assert msar.spec == specified.specs[series][MSAR]
            assert msar.horizons == tuple(specified._horizons(frequency))
            assert msar.window_length == specified._window(frequency)
            assert msar.task_id == f"forecasting:{series}|MSAR"


class TestCacheReuse:
    def test_no_fit_critical_code_changed(self):
        assert code_hash() == PRE_AMENDMENT_CODE_HASH


# -- the T4.3 builder on real, failed and fragile fits ---------------------------------

THRESHOLDS = {"low_occupancy_fraction": 0.05, "low_occupancy_effective_obs": 20,
              "transition_boundary_low": 0.005, "transition_boundary_high": 0.995}
FORECAST_METRICS = {"rmse", "mae", "oos_r2", "hlz_stat", "hlz_p", "dm_stat", "dm_p",
                    "n_forecasts", "attempted_origins", "valid_origins", "failed_origins",
                    "horizon", "mcs_included"}


@pytest.fixture(scope="module")
def synthetic():
    rng = np.random.default_rng(3)
    n, regime, y = 260, 0, np.zeros(260)
    for t in range(1, n):
        if rng.random() < 0.03:
            regime = 1 - regime
        y[t] = (3.0 if regime else -1.0) + 0.3 * (y[t - 1] - (3.0 if regime else -1.0)) \
            + rng.normal(0, 0.8)
    return pd.Series(y, index=pd.date_range("1960-01-01", periods=n, freq="MS"))


@pytest.fixture(scope="module")
def config():
    return load_config(names=("baseline", "series_catalog", "thresholds"),
                       config_dir=CONFIG_DIR)


@pytest.fixture(scope="module")
def fitted(synthetic, config):
    out = {}
    for model, k in ((MSAR, 2), (MSAR3, 3)):
        fit = fit_msar(synthetic, 1, k, config=config, series="S")
        flags.apply_msar_flags(fit.record, fit, config)
        fit.record.model = model
        out[model] = {"fit": fit, "record": fit.record}
    return out


def recession(index):
    flags_ = np.zeros(len(index))
    flags_[40:60] = 1
    return pd.Series(flags_, index=index)


def build(synthetic, attempts):
    return regime_count.regime_rows(
        "S", "M", synthetic, 1, attempts, {MSAR: "MSAR(p=1,K=2)", MSAR3: "MSAR(p=1,K=3)"},
        recession(synthetic.index), THRESHOLDS, {MSAR: "produced as F3.3",
                                                 MSAR3: "produced as F4.3"})


class TestRegimeCountTable:
    def test_rows_hold_the_required_in_sample_comparison(self, synthetic, fitted):
        rows, parameters = build(synthetic, fitted)
        assert [r["k_regimes"] for r in rows] == [2, 3]
        for row in rows:
            for column in ("sample_start", "effective_sample_start", "sample_end", "n_obs",
                           "n_params", "loglik", "aic", "bic", "converged",
                           "optimizer_message", "n_starts", "start_used", "status",
                           "reason_codes", "covariance_status", "regime_means",
                           "regime_mean_std_errors", "occupancy", "min_effective_obs",
                           "expected_durations", "means_distinguishable",
                           "recession_expansion_profile", "interpretability_note"):
                assert column in row, column
        k3 = [p for p in parameters if p["k_regimes"] == 3]
        assert len([p for p in k3 if p["kind"] == "transition probability"]) == 9
        assert len([p for p in k3 if p["kind"] == "regime mean"]) == 3

    def test_no_forecast_metric_appears(self, synthetic, fitted):
        rows, parameters = build(synthetic, fitted)
        conclusion = regime_count.conclusion_row("S", rows)
        for record in rows + parameters + [conclusion]:
            assert not FORECAST_METRICS & set(record), set(record) & FORECAST_METRICS
        assert "not evidence about forecasting performance" in conclusion["scope_note"]

    def test_no_economic_label_is_assigned(self, synthetic, fitted):
        rows, _ = build(synthetic, fitted)
        for row in rows:
            assert "no economic label" in row["interpretability_note"]
            assert "recession=" in row["recession_expansion_profile"]

    def test_k2_is_the_maintained_baseline_whatever_the_criteria(self, synthetic, fitted):
        rows, _ = build(synthetic, fitted)
        assert regime_count.conclusion_row("S", rows)["maintained_baseline"].startswith("K=2")

    def test_a_failed_k3_estimate_is_reported_not_skipped(self, synthetic, fitted):
        record = FitRecord(series="S", model=MSAR3, spec_label="x", spec_hash="",
                           window_start="", window_end="", refit_date="", converged=False)
        record.add_flag(ReasonCode.NONCONVERGENCE, Status.FAILED, detail="no start converged")
        rows, parameters = build(synthetic, {MSAR: fitted[MSAR],
                                             MSAR3: {"fit": None, "record": record}})
        k3 = rows[1]
        assert k3["status"] == "failed" and "NONCONVERGENCE" in k3["reason_codes"]
        assert not [p for p in parameters if p["k_regimes"] == 3]
        conclusion = regime_count.conclusion_row("S", rows)
        assert conclusion["k3_credible"] is False
        assert conclusion["conclusion"].startswith("K=3 not credible: estimation failed")

    def test_a_fragile_k3_estimate_is_not_credible_and_says_why(self, synthetic, fitted):
        rows, _ = build(synthetic, fitted)
        fragile = dict(rows[1], low_occupancy_regimes="3", transition_boundary=True)
        conclusion = regime_count.conclusion_row("S", [rows[0], fragile])
        assert conclusion["k3_credible"] is False
        assert "low-occupancy regime(s) 3" in conclusion["k3_credibility_problems"]
        assert "boundary" in conclusion["k3_credibility_problems"]

    def test_unusable_covariance_makes_distinguishability_not_assessable(self, fitted):
        fit = fitted[MSAR3]["fit"]
        status = fit.record.diagnostics["covariance_status"]
        try:
            fit.record.diagnostics["covariance_status"] = "observed information is singular"
            ratio, verdict = regime_count.distinguishability(fit)
            assert np.isnan(ratio) and verdict.startswith("not assessable")
        finally:
            fit.record.diagnostics["covariance_status"] = status


def _row(model, k, **kw):
    base = {"model": model, "k_regimes": k, "status": "adequate", "converged": True,
            "loglik": -100.0, "aic": 210.0, "bic": 220.0, "covariance_status": "ok",
            "means_distinguishable": "distinguishable", "low_occupancy_regimes": "",
            "empty_regime": False, "transition_boundary": False,
            "singular_covariance": False, "ill_conditioned_covariance": False,
            "reason_codes": ""}
    base.update(kw)
    return base


class TestConclusionRule:
    def test_credible_and_favoured_by_bic(self):
        out = regime_count.conclusion_row("S", [
            _row(MSAR, 2), _row(MSAR3, 3, loglik=-90.0, aic=200.0, bic=215.0)])
        assert out["k3_credible"] and out["bic_favours"] == "K=3"
        assert "may be restrictive" in out["implication_for_k2"]
        assert "not evidence about forecasting performance" in out["implication_for_k2"]

    def test_credible_but_only_aic_favours_k3(self):
        out = regime_count.conclusion_row("S", [
            _row(MSAR, 2), _row(MSAR3, 3, aic=205.0, bic=230.0)])
        assert out["aic_favours"] == "K=3" and out["bic_favours"] == "K=2"
        assert out["conclusion"].startswith("K=3 credible; BIC favours K=2")

    def test_credible_but_favoured_by_neither(self):
        out = regime_count.conclusion_row("S", [
            _row(MSAR, 2), _row(MSAR3, 3, aic=215.0, bic=230.0)])
        assert out["conclusion"].startswith("K=3 credible but favoured by neither")

    def test_criteria_favouring_a_non_credible_k3_are_reported_not_adopted(self):
        out = regime_count.conclusion_row("S", [
            _row(MSAR, 2),
            _row(MSAR3, 3, aic=190.0, bic=200.0, means_distinguishable="not distinguishable")])
        assert out["k3_credible"] is False and out["bic_favours"] == "K=3"
        assert "not taken as support for K=3" in out["implication_for_k2"]

    def test_a_failed_baseline_makes_the_comparison_incomplete(self):
        out = regime_count.conclusion_row("S", [
            _row(MSAR, 2, status="failed", converged=False), _row(MSAR3, 3)])
        assert out["conclusion"].startswith("Comparison incomplete")


class TestClaimRegistration:
    def test_p04_is_routed_to_the_in_sample_comparison_and_left_unadjudicated(self):
        frame = tables.claim_matrix_with_registrations()
        assert tables.validate_claim_matrix(frame) == []
        row = frame.set_index("claim_id").loc["P04-regime-count"]
        assert row["jury_ids_addressed"] == "P-04"
        assert "in-sample" in row["claim_text_stub"]
        assert "not by a predictive-accuracy comparison" in row["claim_text_stub"]
        assert "T4.3_regime_count" in row["supporting_output_files"]
        for column in tables.CLAIM_RESULT_COLUMNS:
            assert pd.isna(row[column])
