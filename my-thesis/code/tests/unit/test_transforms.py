"""Transformations, annualization factors, lag construction and level reconstruction.

These are the Comp §15 checks for transformations, annualization factors, lag
construction, the no-future-data rule, and the reconstructed level forecast when a rate
is modelled in differences.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from thesis.transforms.differences import (
    first_difference,
    level_forecast_from_differences,
    reconstruct_level_path,
)
from thesis.transforms.growth import (
    ANNUALIZATION,
    TransformError,
    annualization_factor,
    annualized_logdiff,
    log_level,
)
from thesis.transforms.lags import MissingPredictorError, lag_matrix, last_window_lags


def monthly(values, start="2000-01-01"):
    index = pd.date_range(start, periods=len(values), freq="MS")
    return pd.Series(np.asarray(values, dtype=float), index=index, name="X")


class TestAnnualization:
    def test_approved_factors(self):
        # Part 5 §2.3: 400 for quarterly GDP, 1200 for the monthly series.
        assert ANNUALIZATION["Q"] == 400.0
        assert ANNUALIZATION["M"] == 1200.0
        assert annualization_factor("M") == 1200.0
        assert annualization_factor("Q") == 400.0

    def test_unknown_frequency_rejected(self):
        with pytest.raises(TransformError):
            annualization_factor("W")


class TestLogDifference:
    def test_known_value(self):
        # A doubling in one month is 1200 * ln(2) annualized.
        series = monthly([100.0, 200.0])
        out = annualized_logdiff(series, 1200.0)
        assert np.isnan(out.iloc[0])
        assert out.iloc[1] == pytest.approx(1200.0 * np.log(2.0))

    def test_constant_series_gives_zero_growth(self):
        out = annualized_logdiff(monthly([50.0] * 5), 1200.0)
        assert np.allclose(out.iloc[1:].to_numpy(), 0.0)

    def test_first_observation_is_lost_not_invented(self):
        out = annualized_logdiff(monthly([1.0, 2.0, 3.0]), 400.0)
        assert np.isnan(out.iloc[0])
        assert out.notna().sum() == 2

    def test_gap_propagates_and_is_not_filled(self):
        # The 2025-10 hole must produce two missing inflation observations, not one
        # interpolated value (Part 5 §2.4 forbids backfilling and interpolation).
        series = monthly([100.0, 101.0, np.nan, 103.0, 104.0])
        out = annualized_logdiff(series, 1200.0)
        assert np.isnan(out.iloc[2])  # the gap itself
        assert np.isnan(out.iloc[3])  # and the change that needs the gap
        assert np.isfinite(out.iloc[1])
        assert np.isfinite(out.iloc[4])

    def test_non_positive_level_rejected(self):
        with pytest.raises(TransformError):
            annualized_logdiff(monthly([1.0, 0.0, 2.0]), 1200.0)

    def test_negative_factor_rejected(self):
        with pytest.raises(TransformError):
            annualized_logdiff(monthly([1.0, 2.0]), -1200.0)

    def test_log_level_requires_complete_series(self):
        with pytest.raises(TransformError):
            log_level(monthly([1.0, np.nan, 3.0]))

    def test_deterministic(self):
        series = monthly(np.linspace(100, 200, 50))
        a = annualized_logdiff(series, 1200.0)
        b = annualized_logdiff(series, 1200.0)
        pd.testing.assert_series_equal(a, b)


class TestFirstDifference:
    def test_known_values(self):
        out = first_difference(monthly([4.0, 4.5, 4.2]))
        assert np.isnan(out.iloc[0])
        assert out.iloc[1] == pytest.approx(0.5)
        assert out.iloc[2] == pytest.approx(-0.3)

    def test_gap_propagates_to_two_observations(self):
        out = first_difference(monthly([4.0, np.nan, 4.4]))
        assert np.isnan(out.iloc[1])
        assert np.isnan(out.iloc[2])


class TestLevelReconstruction:
    def test_round_trip(self):
        levels = np.array([4.0, 4.3, 4.1, 4.6])
        diffs = np.diff(levels)
        rebuilt = reconstruct_level_path(levels[0], diffs)
        np.testing.assert_allclose(rebuilt, levels[1:])

    def test_multi_step_is_cumulative(self):
        diffs = np.array([0.2, 0.3, -0.1])
        assert level_forecast_from_differences(5.0, diffs, 1) == pytest.approx(5.2)
        assert level_forecast_from_differences(5.0, diffs, 2) == pytest.approx(5.5)
        assert level_forecast_from_differences(5.0, diffs, 3) == pytest.approx(5.4)

    def test_too_few_differences_rejected(self):
        with pytest.raises(ValueError):
            level_forecast_from_differences(5.0, np.array([0.1]), 3)


class TestLagMatrix:
    def test_shapes_and_alignment(self):
        series = monthly([1.0, 2.0, 3.0, 4.0, 5.0])
        design = lag_matrix(series, 2)
        assert design.n_obs == 3
        assert design.X.shape == (3, 3)  # constant + 2 lags
        np.testing.assert_allclose(design.y, [3.0, 4.0, 5.0])
        np.testing.assert_allclose(design.X[:, 1], [2.0, 3.0, 4.0])  # y_{t-1}
        np.testing.assert_allclose(design.X[:, 2], [1.0, 2.0, 3.0])  # y_{t-2}
        assert design.index[0] == pd.Timestamp("2000-03-01")

    def test_lags_only_look_backwards(self):
        # Changing a future value must not change any earlier design row.
        series = monthly([1.0, 2.0, 3.0, 4.0, 5.0])
        base = lag_matrix(series, 2)
        altered = series.copy()
        altered.iloc[-1] = 99.0
        changed = lag_matrix(altered, 2)
        np.testing.assert_allclose(base.X[:-1], changed.X[:-1])
        np.testing.assert_allclose(base.y[:-1], changed.y[:-1])

    def test_incomplete_rows_are_excluded_and_reported(self):
        series = monthly([1.0, 2.0, np.nan, 4.0, 5.0, 6.0])
        design = lag_matrix(series, 2)
        # Rows for 2000-03 (y missing), 2000-04 and 2000-05 (a lag missing) cannot form.
        assert [d.strftime("%Y-%m") for d in design.incomplete_index] == [
            "2000-03",
            "2000-04",
            "2000-05",
        ]
        assert design.n_obs == 1
        assert np.isfinite(design.X).all()

    def test_no_constant_option(self):
        design = lag_matrix(monthly([1.0, 2.0, 3.0]), 1, include_const=False)
        assert design.X.shape == (2, 1)

    def test_too_short_series_rejected(self):
        with pytest.raises(ValueError):
            lag_matrix(monthly([1.0, 2.0]), 5)


class TestPredictorVector:
    def test_most_recent_values_in_descending_lag_order(self):
        series = monthly([1.0, 2.0, 3.0, 4.0])
        np.testing.assert_allclose(last_window_lags(series, 2), [4.0, 3.0])

    def test_missing_predictor_raises_rather_than_approximating(self):
        series = monthly([1.0, np.nan, 3.0, 4.0])
        with pytest.raises(MissingPredictorError):
            last_window_lags(series, 4)

    def test_zero_lags(self):
        assert last_window_lags(monthly([1.0]), 0).size == 0
