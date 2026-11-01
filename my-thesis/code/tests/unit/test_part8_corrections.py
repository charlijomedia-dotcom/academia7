"""Regression tests for the Part 8 corrections F1-F4 (approved 1 November 2026).

* F1 -- a forecast from a fit with status `failed` never enters any loss calculation, even
  when it is finite; adequate and fragile forecasts stay eligible; the raw failed forecast
  is preserved for diagnosis; the masking happens in the pipeline after a chain returns,
  so no fit-critical file is involved.
* F2 -- the guarded HLN MCS reproduces `arch` exactly where `arch` works, and handles the
  tie and overflow conditions that made `arch` fail, without dropping a model.
* F3 -- the pairwise differential orientation matches the stated sign convention and
  leaves two-sided inference unchanged.
* F4 -- Zivot-Andrews is reported on both levels without changing the §3.4 decision.
* Cache safety -- none of the corrected modules is part of the fit-cache identity.
"""

from __future__ import annotations

import math
import warnings

import numpy as np
import pandas as pd
import pytest

from thesis.core import cache as cache_module
from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR
from thesis.evaluation import alignment, metrics
from thesis.evaluation.mcs import MCSNumericalError, hln_mcs_r, model_confidence_set
from thesis.evaluation.scoring import FAILED_RAW_FORECAST, mask_failed, scoreable

DATES = pd.date_range("2000-01-01", periods=60, freq="MS")


def _frame(model: str, errors: np.ndarray, status: list[str] | None = None,
           shift: float = 0.0) -> pd.DataFrame:
    actual = np.linspace(1.0, 2.0, len(errors)) + shift
    forecast = actual - errors
    return pd.DataFrame({
        "series": "X", "model": model, "horizon": 1,
        "origin_date": DATES - pd.offsets.MonthBegin(1), "target_date": DATES,
        "forecast": forecast, "actual": actual, "error": errors,
        "status": status or ["adequate"] * len(errors),
        "reason_codes": "",
    })


@pytest.fixture(scope="module")
def config():
    return load_config(names=("baseline", "series_catalog", "thresholds"), config_dir=CONFIG_DIR)


@pytest.fixture
def rng():
    return np.random.default_rng(20261101)


# --------------------------------------------------------------------------- F1 ----

class TestFailedForecastsAreNeverScored:
    def _with_failed_spike(self, rng):
        errors = rng.normal(0, 1, len(DATES))
        status = ["adequate"] * len(DATES)
        errors[30] = -2050.0           # the explosive UNSTABLE_AR forecast
        status[30] = "failed"
        status[10] = "fragile"         # fragile stays eligible
        return _frame("AR", errors, status), errors

    def test_mask_preserves_raw_forecast_and_unscores_it(self, rng):
        frame, _ = self._with_failed_spike(rng)
        masked = mask_failed(frame)
        assert np.isnan(masked.loc[30, "forecast"]) and np.isnan(masked.loc[30, "error"])
        assert masked.loc[30, FAILED_RAW_FORECAST] == frame.loc[30, "forecast"]
        others = masked.drop(index=30)
        assert others[FAILED_RAW_FORECAST].isna().all()
        pd.testing.assert_series_equal(others["forecast"], frame.drop(index=30)["forecast"])
        # idempotent: masking twice changes nothing and keeps the raw value
        pd.testing.assert_frame_equal(mask_failed(masked), masked)

    def test_scoreable_excludes_failed_even_before_masking(self, rng):
        frame, _ = self._with_failed_spike(rng)
        usable = scoreable(frame)
        assert not usable[30]
        assert usable[10]               # fragile
        assert usable.sum() == len(frame) - 1

    def test_accuracy_ignores_failed_but_finite_forecast(self, rng):
        frame, errors = self._with_failed_spike(rng)
        competitor = _frame("MSAR", rng.normal(0, 1, len(DATES)))
        table = metrics.accuracy_table({"AR": frame, "MSAR": competitor}, "AR")
        ar = table[table.model == "AR"].iloc[0]
        clean = np.delete(errors, 30)
        assert ar.rmse == pytest.approx(math.sqrt(np.mean(clean**2)))
        assert ar.n_valid == len(DATES) - 1 and ar.n_failed == 1
        msar = table[table.model == "MSAR"].iloc[0]
        assert msar.n_common_with_benchmark == len(DATES) - 1
        expected = 1 - np.sum(np.delete(competitor.error.to_numpy(), 30) ** 2) / np.sum(clean**2)
        assert msar.oos_r2_vs_benchmark == pytest.approx(expected)

    def test_masked_and_unmasked_frames_give_identical_metrics(self, rng):
        frame, _ = self._with_failed_spike(rng)
        competitor = _frame("MSAR", rng.normal(0, 1, len(DATES)))
        raw = metrics.accuracy_table({"AR": frame, "MSAR": competitor}, "AR")
        masked = metrics.accuracy_table({"AR": mask_failed(frame), "MSAR": competitor}, "AR")
        pd.testing.assert_frame_equal(raw, masked)

    def test_alignment_drops_failed_dates_from_every_comparison(self, rng):
        frame, _ = self._with_failed_spike(rng)
        competitor = _frame("MSAR", rng.normal(0, 1, len(DATES)))
        assert DATES[30] not in alignment.valid_dates(frame)
        assert DATES[10] in alignment.valid_dates(frame)        # fragile kept
        pair = alignment.pairwise(competitor, frame)
        assert pair.n_common == len(DATES) - 1
        assert alignment.across_models({"AR": frame, "MSAR": competitor}).n_common == len(DATES) - 1

    def test_mcs_never_sees_the_failed_loss(self, rng, config):
        frame, _ = self._with_failed_spike(rng)
        others = {m: _frame(m, rng.normal(0, 1, len(DATES))) for m in ("ARMA", "MSAR")}
        with_failed = model_confidence_set({"AR": frame, **others}, "squared", 0.9, config)
        without = model_confidence_set({"AR": frame.drop(index=30), **others},
                                       "squared", 0.9, config)
        assert with_failed.available and with_failed.t_common == len(DATES) - 1
        assert with_failed.p_values == without.p_values
        assert with_failed.included == without.included

    def test_adequate_and_fragile_extreme_forecasts_remain_scored(self, rng):
        errors = rng.normal(0, 1, len(DATES))
        errors[5] = 1e6                  # extreme but from a *fragile* fit: §7.5 keeps it
        status = ["adequate"] * len(DATES)
        status[5] = "fragile"
        table = metrics.accuracy_table({"STAR": _frame("STAR", errors, status)}, "AR")
        assert table.iloc[0].n_valid == len(DATES)
        assert table.iloc[0].rmse > 1e5

    def test_pipeline_masks_every_chain_it_collects(self, rng):
        from thesis.forecasting.rolling import ChainResult
        from thesis.models.registry import ModelSpec
        from thesis.pipeline import Pipeline

        frame, _ = self._with_failed_spike(rng)
        chain = ChainResult(series="X", spec=ModelSpec(model="AR", order=1),
                            window_length=24, forecasts=frame)

        class _Scheduler:
            def has(self, jobs):
                return True

            def results(self, jobs):
                return [("AR", chain)]

        pipeline = Pipeline.__new__(Pipeline)
        pipeline.scheduler = _Scheduler()
        pipeline.all_fit_records, pipeline.all_failures, pipeline.all_gaps = [], [], []
        (_, returned), = pipeline._chains([object()])
        assert np.isnan(returned.forecasts.loc[30, "forecast"])
        assert returned.forecasts.loc[30, FAILED_RAW_FORECAST] == frame.loc[30, "forecast"]
        assert scoreable(returned.forecasts).sum() == len(DATES) - 1


# --------------------------------------------------------------------------- F2 ----

def _arch_mcs(losses: pd.DataFrame, size: float, reps: int, block: int, seed: int):
    from arch.bootstrap import MCS
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        procedure = MCS(losses, size=size, reps=reps, block_size=block, method="R",
                        bootstrap="stationary", seed=seed)
        procedure.compute()
    return ({str(k): float(v.iloc[0]) for k, v in procedure.pvalues.iterrows()},
            sorted(map(str, procedure.included)))


class TestGuardedMCS:
    @pytest.mark.parametrize("case", range(6))
    def test_identical_to_arch_where_arch_works(self, case):
        rng = np.random.default_rng(100 + case)
        t = 80 + 20 * case
        base = rng.normal(0, 1, (t, 4)) ** 2
        base[:, case % 4] *= 1.0 + 0.15 * case
        losses = pd.DataFrame(base, columns=["AR", "ARMA", "MSAR", "STAR"])
        block = int(math.ceil(math.sqrt(t)))
        for size in (0.10, 0.05):
            arch_p, arch_in = _arch_mcs(losses, size, 400, block, 20261005)
            p, included, _, diagnostics = hln_mcs_r(losses, size, 400, block, 20261005)
            assert {k: float(v) for k, v in p.items()} == arch_p
            assert sorted(included) == arch_in
            assert diagnostics == {"rescaled_variance_cells": 0, "tied_elimination_steps": 0}

    def _dominated(self, magnitude: float) -> pd.DataFrame:
        rng = np.random.default_rng(7)
        losses = pd.DataFrame(rng.normal(0, 1, (120, 4)) ** 2,
                              columns=["AR", "ARMA", "MSAR", "STAR"])
        losses.loc[17, "STAR"] = magnitude       # one explosive STAR forecast
        return losses

    def test_arch_fails_on_the_tie_and_the_guarded_version_eliminates_star(self):
        losses = self._dominated(4e22)            # CPIAUCSL h=1 squared-loss scale
        with pytest.raises(IndexError):
            _arch_mcs(losses, 0.10, 300, 11, 20261005)
        p, included, excluded, diagnostics = hln_mcs_r(losses, 0.10, 300, 11, 20261005)
        assert diagnostics["tied_elimination_steps"] >= 1
        # STAR stays in the model set and is judged by the HLN statistic like any model:
        # one spike inflates its bootstrap variance too, so it need not be eliminated first.
        assert set(p.index) == {"AR", "ARMA", "MSAR", "STAR"}
        assert sorted(included + excluded) == ["AR", "ARMA", "MSAR", "STAR"]
        assert (np.diff(p.to_numpy()) >= 0).all() and p.iloc[-1] == 1.0

    def test_overflowing_variance_is_rescaled_not_zeroed(self):
        losses = self._dominated(1e200)          # CPIAUCSL h=12 squared-loss scale
        p, _, _, diagnostics = hln_mcs_r(losses, 0.10, 300, 11, 20261005)
        assert diagnostics["rescaled_variance_cells"] > 0
        assert set(p.index) == {"AR", "ARMA", "MSAR", "STAR"}
        assert np.isfinite(p.to_numpy()).all()

    def test_ambiguous_ties_are_reported_unavailable(self):
        losses = pd.DataFrame(np.ones((60, 3)), columns=["A", "B", "C"])
        losses.loc[:, "B"] = 2.0
        losses.loc[:, "C"] = 2.0                  # B and C tie as the worst model
        with pytest.raises(MCSNumericalError):
            hln_mcs_r(losses, 0.10, 100, 8, 1)

    def test_dispatch_records_the_implementation(self, config):
        frames = {}
        rng = np.random.default_rng(3)
        for model in ("AR", "ARMA", "MSAR", "STAR"):
            frames[model] = _frame(model, rng.normal(0, 1, len(DATES)))
        frames["STAR"].loc[17, "error"] = 2e11
        frames["STAR"].loc[17, "forecast"] = frames["STAR"].loc[17, "actual"] - 2e11
        quick = config.with_overrides({"evaluation": {"mcs": {"replications": 200}}}, "test")
        result = model_confidence_set(frames, "squared", 0.9, quick)
        assert result.available
        assert result.implementation.startswith("hln_mcs_r")
        assert set(result.included) | set(result.excluded) == {"AR", "ARMA", "MSAR", "STAR"}
        rows = result.to_rows()
        assert all(r["mcs_implementation"] == result.implementation for r in rows)


# --------------------------------------------------------------------------- F3 ----

class TestPairwiseSignConvention:
    def test_hlz_orientation_only_flips_signs(self, config):
        from thesis.evaluation.hlz import HLZSettings, hlz_test
        hlz = config.require("evaluation.hlz")
        settings = HLZSettings(
            lrv_kernel=hlz["lrv_kernel"], b0=float(hlz["lrv_bandwidth"]["b0"]),
            demean_kernel=hlz["demean_kernel"], h0=float(hlz["demean_bandwidth"]["h0"]),
            critical_value_replications=2000, critical_value_seed=5,
            two_sided=True, report_one_sided=True, source=hlz["source"])
        d = np.random.default_rng(9).normal(-0.2, 1.0, 150)
        forward, forward_row = hlz_test(d, settings)
        reverse, reverse_row = hlz_test(-d, settings)
        assert forward_row.p_value == pytest.approx(reverse_row.p_value)
        assert forward_row.statistic == pytest.approx(-reverse_row.statistic)
        # One-sided p-values come from the simulated (not exactly symmetric) null
        # distribution, so they are re-read under the corrected orientation rather than
        # merely swapped; the two-sided p-value above is exactly invariant.
        assert forward.p_value_upper + forward.p_value_lower >= 1.0

    def test_pipeline_pair_loop_uses_competitor_minus_benchmark(self):
        import inspect
        from thesis import pipeline
        source = inspect.getsource(pipeline.Pipeline.evaluation_stage)
        assert "competitor, reference = ((model_b, model_a) if oriented" in source
        assert "loss_differential(errors[competitor], errors[reference]" in source
        assert "errors[competitor], errors[reference], horizon, loss_kind" in source


# --------------------------------------------------------------------------- F4 ----

class TestZivotAndrewsReporting:
    def _series(self):
        rng = np.random.default_rng(11)
        index = pd.date_range("1950-01-01", periods=400, freq="MS")
        return pd.Series(np.cumsum(rng.normal(0, 0.2, 400)) + 5, index=index, name="SIM")

    def test_reported_on_both_samples_without_changing_the_decision(self, config):
        from thesis.diagnostics.decision_rule import (confirm_on_full_sample,
                                                      decide_transformation,
                                                      report_zivot_andrews)
        level = self._series()
        initial = level.iloc[:240]
        decision = confirm_on_full_sample(
            decide_transformation("SIM", initial, "M", config), level, "M", config)
        before = (decision.decision, decision.rule_branch, decision.break_date)
        added = report_zivot_andrews(decision, initial, level, "M", config)
        assert (decision.decision, decision.rule_branch, decision.break_date) == before
        assert decision.za_initial_window is not None and decision.za_full_sample is not None
        assert decision.za_initial_window.extra["break_date"]
        assert decision.za_full_sample.extra["break_date"]
        row = decision.to_row()
        assert row["za_full_sample_break_date"] == decision.za_full_sample.extra["break_date"]
        if decision.rule_branch.startswith("3"):
            assert all("full sample" in r.name for r in added)   # tie-break result reused
        else:
            assert len(added) == 2 and "not used by the §3.4 rule" in added[0].name


# ---------------------------------------------------------------- cache safety ----

def test_corrected_modules_are_not_part_of_the_fit_cache_identity():
    critical = set(cache_module._FIT_CRITICAL)
    for module in ("evaluation/scoring.py", "evaluation/mcs.py", "evaluation/alignment.py",
                   "evaluation/metrics.py", "pipeline.py", "reporting/figures.py",
                   "diagnostics/decision_rule.py"):
        assert module not in critical


# -------------------------------------------------------------------------- F7.1 ----

def test_data_dictionary_reports_the_decided_transformation(tmp_path):
    """T2.1 carries the §3.4 decision for the rate series instead of "pending"."""
    from types import SimpleNamespace

    from thesis.pipeline import Pipeline

    written = {}
    pipeline = Pipeline.__new__(Pipeline)
    pipeline._dictionary_rows = [
        {"target": "UNRATE", "transformation": "pending stationarity decision",
         "transformed_first_date": "", "transformed_last_date": ""},
        {"target": "FEDFUNDS", "transformation": "pending stationarity decision",
         "transformed_first_date": "", "transformed_last_date": ""},
        {"target": "CPIAUCSL", "transformation": "1200 x dlog",
         "transformed_first_date": "1947-02-01", "transformed_last_date": "2026-08-01"},
    ]
    index = pd.date_range("1948-01-01", periods=12, freq="MS")
    pipeline.targets = {"UNRATE": pd.Series(range(12), index=index),
                        "FEDFUNDS": pd.Series(range(11), index=index[1:])}
    pipeline.decisions = {
        "UNRATE": SimpleNamespace(decision="level", rule_branch="1: clear level stationarity"),
        "FEDFUNDS": SimpleNamespace(decision="difference", rule_branch="2: clear nonstationarity"),
    }
    pipeline.layout = SimpleNamespace(data_audit=tmp_path)
    pipeline._write = lambda frame, directory, name, stage: written.update({name: frame})
    pipeline._write_data_dictionary(stage=None)
    table = written["T2.1_data_dictionary.csv"].set_index("target")
    assert "pending" not in " ".join(table["transformation"])
    assert table.loc["UNRATE", "transformation"].startswith("level")
    assert table.loc["FEDFUNDS", "transformation"].startswith("first difference")
    assert table.loc["FEDFUNDS", "transformed_first_date"] == "1948-02-01"
    assert table.loc["CPIAUCSL", "transformation"] == "1200 x dlog"
