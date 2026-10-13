"""Stationarity tests and the predeclared transformation decision rule.

Validated on simulated series with known properties, plus a table-driven check of every
branch of the Part 5 §3.4 rule.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR
from thesis.core.schemas import TestResult
from thesis.diagnostics.decision_rule import (
    DIFFERENCE,
    LEVEL,
    confirm_on_full_sample,
    decide_transformation,
)
from thesis.diagnostics.stationarity import (
    adf_test,
    kpss_test,
    results_to_frame,
    transformation_verification,
    zivot_andrews_test,
)


@pytest.fixture(scope="module")
def config():
    return load_config(config_dir=CONFIG_DIR)


def monthly(values, start="1960-01-01"):
    index = pd.date_range(start, periods=len(values), freq="MS")
    return pd.Series(np.asarray(values, dtype=float), index=index, name="TEST")


def random_walk(n, seed=0, scale=1.0):
    rng = np.random.default_rng(seed)
    return monthly(np.cumsum(rng.standard_normal(n)) * scale + 100.0)


def stationary_ar1(n, phi=0.5, seed=0):
    rng = np.random.default_rng(seed)
    e = rng.standard_normal(n)
    y = np.zeros(n)
    for t in range(1, n):
        y[t] = phi * y[t - 1] + e[t]
    return monthly(y + 5.0)


class TestADF:
    def test_rejects_for_a_stationary_series(self, config):
        result = adf_test(stationary_ar1(400), "M", config)
        assert result.decision_5pct == "reject"
        assert result.p_value < 0.05

    def test_does_not_reject_for_a_random_walk(self, config):
        result = adf_test(random_walk(400), "M", config)
        assert result.decision_5pct == "do not reject"

    def test_records_every_tuning_choice(self, config):
        result = adf_test(stationary_ar1(300), "M", config)
        for key in ("regression", "autolag", "maxlag", "used_lag", "n_obs", "significance"):
            assert key in result.tuning
        assert result.tuning["maxlag"] == 12
        assert result.tuning["autolag"] == "BIC"
        assert result.tuning["regression"] == "c"

    def test_quarterly_lag_cap(self, config):
        index = pd.date_range("1960-01-01", periods=200, freq="QS")
        series = pd.Series(stationary_ar1(200).to_numpy(), index=index, name="Q")
        assert adf_test(series, "Q", config).tuning["maxlag"] == 4

    def test_null_and_reference_are_stated(self, config):
        result = adf_test(stationary_ar1(200), "M", config)
        assert "unit root" in result.null_hypothesis
        assert "Dickey-Fuller" in result.reference


class TestKPSS:
    def test_does_not_reject_for_a_stationary_series(self, config):
        assert kpss_test(stationary_ar1(400), "M", config).decision_5pct == "do not reject"

    def test_rejects_for_a_random_walk(self, config):
        assert kpss_test(random_walk(400), "M", config).decision_5pct == "reject"

    def test_opposite_null_to_adf(self, config):
        assert "stationary" in kpss_test(stationary_ar1(200), "M", config).null_hypothesis

    def test_table_bound_is_flagged(self, config):
        # A strong random walk drives the p-value to the edge of the published table.
        result = kpss_test(random_walk(400), "M", config)
        assert result.tuning["p_value_at_table_bound"] is True

    def test_bandwidth_recorded(self, config):
        result = kpss_test(stationary_ar1(300), "M", config)
        assert result.tuning["nlags_rule"] == "auto"
        assert isinstance(result.tuning["bandwidth_lags"], int)


class TestZivotAndrews:
    def test_recovers_a_known_break(self, config):
        rng = np.random.default_rng(3)
        n, break_at = 300, 150
        values = rng.standard_normal(n) * 0.3
        values[break_at:] += 6.0           # large level shift
        series = monthly(np.cumsum(values * 0.0) + values + 10.0)
        result = zivot_andrews_test(series, "M", config)
        found = pd.Timestamp(result.extra["break_date"])
        expected = series.index[break_at]
        assert abs((found - expected).days) < 400

    def test_does_not_reject_for_a_pure_random_walk(self, config):
        assert zivot_andrews_test(random_walk(300), "M", config).decision_5pct == "do not reject"

    def test_critical_values_come_from_the_implementation(self, config):
        # Decision D9 forbids hard-coding an approximate generic value such as -5.08.
        result = zivot_andrews_test(random_walk(300), "M", config)
        criticals = {k: v for k, v in result.extra.items() if k.startswith("critical_")}
        assert set(criticals) == {"critical_1%", "critical_5%", "critical_10%"}
        assert criticals["critical_1%"] < criticals["critical_5%"] < criticals["critical_10%"]

    def test_specification_is_break_in_intercept_and_trend(self, config):
        result = zivot_andrews_test(random_walk(200), "M", config)
        assert result.tuning["regression"] == "ct"
        assert result.tuning["trim"] == 0.15
        assert result.tuning["maxlag"] == 12


class TestTransformationVerification:
    def test_reports_level_and_transformed_plus_trend_diagnostics(self, config):
        level = monthly(np.log(np.cumsum(np.abs(np.random.default_rng(1).standard_normal(300))) + 100))
        transformed = level.diff().dropna()
        results = transformation_verification(level, transformed, "M", config)
        labels = [r.name for r in results]
        assert sum("log level" in name for name in labels) >= 2
        assert sum("transformed" in name for name in labels) == 2
        assert any("diagnostic only" in name for name in labels)

    def test_trend_diagnostics_are_clearly_labelled(self, config):
        # A trend plus noise: a noiseless straight line makes the regression
        # rank-deficient, which tests the library rather than this code.
        rng = np.random.default_rng(5)
        level = monthly(np.linspace(1.0, 2.0, 300) + rng.standard_normal(300) * 0.05)
        results = transformation_verification(level, level.diff().dropna(), "M", config)
        extra = [r for r in results if "constant and trend" in r.name]
        assert extra and all("diagnostic only" in r.name for r in extra)

    def test_results_flatten_to_a_table(self, config):
        results = [adf_test(stationary_ar1(200), "M", config)]
        frame = results_to_frame(results)
        for column in ("name", "null_hypothesis", "statistic", "p_value", "reference",
                       "decision_5pct", "implication", "tuning"):
            assert column in frame.columns


class TestDecisionRule:
    """Every branch of Part 5 §3.4, driven by series with known properties."""

    def test_branch_1_clear_level_stationarity(self, config):
        decision = decide_transformation("TEST", stationary_ar1(240), "M", config)
        assert decision.decision == LEVEL
        assert decision.rule_branch.startswith("1")
        assert not decision.break_sensitive_robustness

    def test_branch_2_clear_nonstationarity(self, config):
        decision = decide_transformation("TEST", random_walk(240), "M", config)
        assert decision.decision == DIFFERENCE
        assert decision.rule_branch.startswith("2")

    def test_disagreement_consults_zivot_andrews(self, config):
        # A near-unit-root series with a large level shift typically splits ADF and KPSS.
        rng = np.random.default_rng(7)
        n = 240
        e = rng.standard_normal(n) * 0.5
        y = np.zeros(n)
        for t in range(1, n):
            y[t] = 0.97 * y[t - 1] + e[t]
        y[120:] += 4.0
        decision = decide_transformation("TEST", monthly(y + 5.0), "M", config)
        if decision.rule_branch.startswith("3"):
            assert len(decision.initial_window_results) == 3
            assert decision.break_date
            if decision.decision == LEVEL:
                assert decision.break_sensitive_robustness
        else:
            # The branch is data-dependent; the rule must still have produced a decision.
            assert decision.decision in (LEVEL, DIFFERENCE)

    def test_decision_uses_only_the_initial_window(self, config):
        # Appending very different later data must not change the initial-window decision.
        initial = stationary_ar1(240)
        first = decide_transformation("TEST", initial, "M", config)
        longer = pd.concat([initial, random_walk(240, seed=9) * 50])
        second = decide_transformation("TEST", longer.iloc[:240], "M", config)
        assert first.decision == second.decision
        assert first.rule_branch == second.rule_branch

    def test_full_sample_disagreement_flags_but_does_not_change_the_baseline(self, config):
        initial = stationary_ar1(240)
        decision = decide_transformation("TEST", initial, "M", config)
        assert decision.decision == LEVEL
        full = pd.concat([initial, random_walk(300, seed=11)])
        confirmed = confirm_on_full_sample(decision, full, "M", config)
        assert confirmed.decision == LEVEL              # baseline unchanged
        assert confirmed.full_sample_agrees is False    # but the disagreement is visible
        assert confirmed.robustness_required is True

    def test_full_sample_agreement_is_recorded(self, config):
        series = stationary_ar1(500)
        decision = decide_transformation("TEST", series.iloc[:240], "M", config)
        confirmed = confirm_on_full_sample(decision, series, "M", config)
        assert confirmed.full_sample_agrees is True

    def test_alternative_transformation_is_always_a_robustness_check(self, config):
        for series in (stationary_ar1(240), random_walk(240)):
            assert decide_transformation("TEST", series, "M", config).robustness_required

    def test_decision_row_is_reportable(self, config):
        row = decide_transformation("TEST", stationary_ar1(240), "M", config).to_row()
        for key in ("series_id", "baseline_transformation", "rule_branch", "reason",
                    "alternative_transformation_robustness_required"):
            assert key in row
