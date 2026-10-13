"""Forecast evaluation: losses, alignment, metrics, states, DM-HLN, state regression, MCS."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR
from thesis.evaluation import alignment, metrics, states
from thesis.evaluation.dm_hln import agrees_with, dm_hln_test, newey_west_variance
from thesis.evaluation.losses import ABSOLUTE, SIGN_CONVENTION, SQUARED, loss, loss_differential
from thesis.evaluation.mcs import model_confidence_set
from thesis.evaluation.state_loss_regression import LABEL, state_loss_regression


@pytest.fixture(scope="module")
def config():
    return load_config(config_dir=CONFIG_DIR)


def forecast_frame(errors, start="2000-01-01", model="M"):
    index = pd.date_range(start, periods=len(errors), freq="MS")
    return pd.DataFrame({
        "target_date": index,
        "model": model,
        "forecast": np.zeros(len(errors)),
        "actual": np.asarray(errors, dtype=float),
        "error": np.asarray(errors, dtype=float),
    })


class TestLosses:
    def test_squared_and_absolute(self):
        e = np.array([-2.0, 3.0])
        np.testing.assert_allclose(loss(e, SQUARED), [4.0, 9.0])
        np.testing.assert_allclose(loss(e, ABSOLUTE), [2.0, 3.0])

    def test_unknown_loss_rejected(self):
        with pytest.raises(ValueError):
            loss(np.array([1.0]), "huber")

    def test_sign_convention_is_competitor_minus_benchmark(self):
        competitor = np.array([1.0, 1.0])     # smaller errors
        benchmark = np.array([2.0, 2.0])
        d = loss_differential(competitor, benchmark, SQUARED)
        assert d.mean() < 0                    # negative favours the competitor
        assert "negative favours the competitor" in SIGN_CONVENTION


class TestAlignment:
    def test_pairwise_intersection(self):
        a = forecast_frame([1.0, 2.0, 3.0, 4.0])
        b = forecast_frame([1.0, 2.0, 3.0, 4.0])
        b.loc[1, "error"] = np.nan
        b.loc[1, "forecast"] = np.nan
        pair = alignment.pairwise(a, b)
        assert pair.n_common == 3
        assert pair.removed["left"] == 1

    def test_across_models_intersection(self):
        frames = {"a": forecast_frame([1.0, 2.0, 3.0]), "b": forecast_frame([1.0, 2.0, 3.0])}
        frames["b"].loc[2, "forecast"] = np.nan
        aligned = alignment.across_models(frames)
        assert aligned.n_common == 2
        assert aligned.removed["a"] == 1

    def test_no_common_dates_is_unavailable(self):
        a = forecast_frame([1.0, 2.0], start="2000-01-01")
        b = forecast_frame([1.0, 2.0], start="2010-01-01")
        assert not alignment.across_models({"a": a, "b": b}).available

    def test_restrict_and_aligned_errors(self):
        a = forecast_frame([1.0, 2.0, 3.0])
        dates = pd.DatetimeIndex(["2000-01-01", "2000-03-01"])
        errors = alignment.aligned_errors({"a": a}, dates)
        np.testing.assert_allclose(errors["a"], [1.0, 3.0])


class TestMetrics:
    def test_rmse_and_mae(self):
        assert metrics.rmse(np.array([3.0, 4.0])) == pytest.approx(3.5355339)
        assert metrics.mae(np.array([3.0, -4.0])) == pytest.approx(3.5)

    def test_oos_r2_identity(self):
        benchmark = np.array([2.0, 2.0])
        model = np.array([1.0, 1.0])
        assert metrics.oos_r2(model, benchmark) == pytest.approx(0.75)

    def test_oos_r2_zero_when_identical(self):
        e = np.array([1.0, 2.0])
        assert metrics.oos_r2(e, e) == pytest.approx(0.0)

    def test_accuracy_table_reports_counts_and_ranks(self):
        frames = {
            "AR": forecast_frame([1.0, -1.0, 1.0, -1.0], model="AR"),
            "X": forecast_frame([0.5, -0.5, 0.5, -0.5], model="X"),
        }
        table = metrics.accuracy_table(frames, benchmark="AR", series="S", horizon=1)
        assert set(table["model"]) == {"AR", "X"}
        competitor = table[table["model"] == "X"].iloc[0]
        assert competitor["n_valid"] == 4
        assert competitor["oos_r2_vs_benchmark"] == pytest.approx(0.75)
        assert competitor["rank_rmse"] == 1

    def test_failed_forecasts_are_counted_not_hidden(self):
        frame = forecast_frame([1.0, np.nan, 1.0])
        table = metrics.accuracy_table({"X": frame}, benchmark="X")
        row = table.iloc[0]
        assert row["n_attempted"] == 3
        assert row["n_valid"] == 2
        assert row["n_failed"] == 1


class TestStates:
    def _usrec(self):
        index = pd.date_range("2000-01-01", periods=36, freq="MS")
        values = [0] * 6 + [1] * 6 + [0] * 24
        return pd.Series(values, index=index, dtype=float)

    def test_peak_and_trough_from_transitions(self):
        chronology = states.monthly_chronology(self._usrec())
        assert list(chronology.peaks.strftime("%Y-%m")) == ["2000-06"]
        assert list(chronology.troughs.strftime("%Y-%m")) == ["2000-12"]

    def test_turning_window_is_a_union_not_a_double_count(self):
        chronology = states.monthly_chronology(self._usrec())
        masks = states.turning_masks(chronology, 3)
        # Peak window 2000-03..2000-09 and trough window 2000-09..2001-03 overlap at
        # 2000-09, which must be counted once.
        assert masks[states.PEAK].sum() == 7
        assert masks[states.TROUGH].sum() == 7
        assert masks[states.TURNING].sum() == 13

    def test_windows_are_clipped_at_the_sample_boundary(self):
        index = pd.date_range("2000-01-01", periods=8, freq="MS")
        usrec = pd.Series([0, 1, 1, 0, 0, 0, 0, 0], index=index, dtype=float)
        chronology = states.monthly_chronology(usrec)
        masks = states.turning_masks(chronology, 6)
        assert masks[states.TURNING].sum() == len(index)      # clipped, never out of range

    def test_states_partition_turning_and_outside(self):
        chronology = states.monthly_chronology(self._usrec())
        masks = states.turning_masks(chronology, 3)
        assert (masks[states.TURNING] | masks[states.OUTSIDE_TURNING]).all()
        assert not (masks[states.TURNING] & masks[states.OUTSIDE_TURNING]).any()

    def test_quarterly_aggregation_uses_the_within_quarter_maximum(self):
        index = pd.date_range("2000-01-01", periods=12, freq="MS")
        usrec = pd.Series([0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], index=index, dtype=float)
        quarterly = states.to_quarterly(usrec)
        assert quarterly.iloc[0] == 1.0        # Q1 contains a recession month
        assert quarterly.iloc[1] == 0.0

    def test_recession_and_turning_categories_may_overlap(self):
        chronology = states.monthly_chronology(self._usrec())
        frame = states.state_frame(chronology, 3)
        overlap = frame[(frame["recession"] == 1) & (frame["turning_window"] == 1)]
        assert len(overlap) > 0                 # decision M11 permits this

    def test_attach_states_joins_on_target_date(self):
        chronology = states.monthly_chronology(self._usrec())
        frame = states.state_frame(chronology, 3)
        forecasts = forecast_frame([1.0] * 36)
        joined = states.attach_states(forecasts, frame)
        assert "recession" in joined.columns
        assert joined["recession"].notna().all()

    def test_no_transitions_gives_empty_turning_window(self):
        index = pd.date_range("2000-01-01", periods=24, freq="MS")
        chronology = states.monthly_chronology(pd.Series(np.zeros(24), index=index))
        assert not chronology.has_transitions
        assert states.turning_masks(chronology, 3)[states.TURNING].sum() == 0


class TestDMHLN:
    def test_newey_west_matches_the_sample_variance_at_zero_truncation(self):
        rng = np.random.default_rng(0)
        d = rng.standard_normal(200)
        assert newey_west_variance(d, 0) == pytest.approx(np.var(d), rel=1e-12)

    def test_detects_a_genuine_accuracy_difference(self):
        rng = np.random.default_rng(1)
        competitor = rng.standard_normal(300) * 0.5
        benchmark = rng.standard_normal(300) * 1.5
        result = dm_hln_test(competitor, benchmark, 1, SQUARED)
        assert result.p_value < 0.01
        assert "competitor" in result.implication

    def test_equal_accuracy_is_not_rejected(self):
        rng = np.random.default_rng(2)
        result = dm_hln_test(rng.standard_normal(300), rng.standard_normal(300), 1, SQUARED)
        assert result.p_value > 0.05

    def test_records_the_truncation_rule_and_correction(self):
        rng = np.random.default_rng(3)
        result = dm_hln_test(rng.standard_normal(200), rng.standard_normal(200), 6, SQUARED)
        assert result.tuning["truncation"] == 5
        assert result.tuning["truncation_rule"] == "h-1"
        assert result.tuning["small_sample_correction"] == "harvey_leybourne_newbold"
        assert 0 < result.tuning["correction_factor"] < 2

    def test_short_sample_is_unavailable(self):
        result = dm_hln_test(np.ones(5), np.ones(5) * 2, 1, SQUARED)
        assert not result.available

    def test_agreement_helper(self):
        rng = np.random.default_rng(4)
        a = dm_hln_test(rng.standard_normal(200), rng.standard_normal(200), 1, SQUARED)
        assert agrees_with(a, a) == "agree"


class TestStateLossRegression:
    def test_is_not_labelled_giacomini_white(self):
        assert "giacomini" not in LABEL.lower()
        assert "ex-post" in LABEL

    def test_recovers_a_known_state_effect(self):
        rng = np.random.default_rng(5)
        n = 400
        recession = (rng.random(n) < 0.25).astype(float)
        turning = (rng.random(n) < 0.3).astype(float)
        d = rng.standard_normal(n) * 0.2 - 1.2 * recession
        result = state_loss_regression(d, recession, turning, 1)
        assert result.available
        assert result.coefficients["beta_rec"] == pytest.approx(-1.2, abs=0.15)
        assert result.slopes_wald.p_value < 0.01

    def test_no_state_effect_is_not_detected(self):
        rng = np.random.default_rng(6)
        n = 400
        recession = (rng.random(n) < 0.25).astype(float)
        turning = (rng.random(n) < 0.3).astype(float)
        result = state_loss_regression(rng.standard_normal(n), recession, turning, 1)
        assert result.slopes_wald.p_value > 0.05

    def test_reports_both_wald_tests(self):
        rng = np.random.default_rng(7)
        n = 300
        result = state_loss_regression(rng.standard_normal(n) - 0.5,
                                       (rng.random(n) < 0.3).astype(float),
                                       (rng.random(n) < 0.3).astype(float), 1)
        assert result.joint_wald is not None and result.slopes_wald is not None
        row = result.to_row()
        assert "joint_wald_p" in row and "slopes_wald_p" in row

    def test_constant_state_indicator_is_unavailable(self):
        rng = np.random.default_rng(8)
        n = 100
        result = state_loss_regression(rng.standard_normal(n), np.zeros(n), np.zeros(n), 1)
        assert not result.available
        assert "varies" in result.unavailable_reason

    def test_small_cells_are_weak_evidence_not_unavailable(self):
        # Decision M12: a small cell is flagged, not a reason to refuse inference.
        rng = np.random.default_rng(9)
        n = 200
        recession = np.zeros(n)
        recession[:3] = 1.0
        turning = (rng.random(n) < 0.3).astype(float)
        result = state_loss_regression(rng.standard_normal(n), recession, turning, 1)
        assert result.available
        assert result.weak_evidence

    def test_hac_rule_is_recorded(self):
        rng = np.random.default_rng(10)
        n = 200
        result = state_loss_regression(rng.standard_normal(n),
                                       (rng.random(n) < 0.3).astype(float),
                                       (rng.random(n) < 0.3).astype(float), 6)
        assert "truncation h-1 = 5" in result.hac_rule


class TestMCS:
    def _frames(self, seed=0, n=120):
        rng = np.random.default_rng(seed)
        return {
            "AR": forecast_frame(rng.standard_normal(n) * 1.0, model="AR"),
            "B": forecast_frame(rng.standard_normal(n) * 1.02, model="B"),
            "C": forecast_frame(rng.standard_normal(n) * 3.0, model="C"),
        }

    def test_identifies_a_clearly_worse_model(self, config):
        fast = config.with_overrides({"evaluation": {"mcs": {"replications": 200}}}, "fast")
        result = model_confidence_set(self._frames(), SQUARED, 0.90, fast, series="S")
        assert result.available
        assert "C" not in result.included
        assert result.t_common == 120

    def test_records_every_tuning_choice(self, config):
        fast = config.with_overrides({"evaluation": {"mcs": {"replications": 200}}}, "fast")
        result = model_confidence_set(self._frames(), SQUARED, 0.95, fast)
        rows = result.to_rows()
        row = rows[0]
        assert row["method"] == "R"
        assert row["bootstrap"] == "stationary"
        assert row["block_length"] == 11            # ceil(sqrt(120))
        assert row["seed"] == config.get("evaluation.mcs.seed")

    def test_too_few_common_dates_is_unavailable(self, config):
        frames = self._frames(n=10)
        result = model_confidence_set(frames, SQUARED, 0.90, config)
        assert not result.available
        assert "common finite-loss dates" in result.unavailable_reason

    def test_single_model_is_unavailable(self, config):
        result = model_confidence_set({"AR": forecast_frame(np.ones(50))}, SQUARED, 0.9, config)
        assert not result.available
        assert "fewer than two" in result.unavailable_reason
