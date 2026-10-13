"""End-to-end compatibility: canonical CSV -> panels -> transformations -> windows -> AR.

This is the "model compatibility" check: the data produced by the new CSV-first
architecture must flow through the approved transformations into real estimation windows
and produce usable model fits at every predeclared window length, including the T4.8
sensitivity lengths.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR, FROZEN_VINTAGE_DIR
from thesis.core.schemas import Status
from thesis.data.canonical import to_panels
from thesis.data.store import load_bundle
from thesis.forecasting.windows import common_calendar, restrict_to_calendar, rolling_origins
from thesis.models.ar import fit_ar
from thesis.transforms.growth import annualized_logdiff
from thesis.transforms.lags import lag_matrix

pytestmark = pytest.mark.skipif(
    not (FROZEN_VINTAGE_DIR / "MANIFEST.json").exists(),
    reason="frozen store not present",
)


@pytest.fixture(scope="module")
def config():
    return load_config(config_dir=CONFIG_DIR)


@pytest.fixture(scope="module")
def targets(config):
    """Transformed modelling targets built from the canonical input, as the pipeline does."""
    panels = to_panels(load_bundle(FROZEN_VINTAGE_DIR, config).frame)
    return {
        "CPIAUCSL": annualized_logdiff(panels["M"]["CPIAUCSL"], 1200.0).dropna(),
        "INDPRO": annualized_logdiff(panels["M"]["INDPRO"], 1200.0).dropna(),
        "M2SL": annualized_logdiff(panels["M"]["M2SL"], 1200.0).dropna(),
        "GDPC1": annualized_logdiff(panels["Q"]["GDPC1"], 400.0).dropna(),
    }


class TestTargetsAreModelReady:
    def test_targets_are_complete_and_finite(self, targets):
        for name, series in targets.items():
            assert np.isfinite(series.to_numpy()).all(), name
            assert series.index.is_monotonic_increasing

    def test_monthly_targets_have_contiguous_calendar_spacing(self, targets):
        # After the approved LOCF there are no interior gaps, so a window of N
        # observations is also N calendar months.
        for name in ("CPIAUCSL", "INDPRO", "M2SL"):
            index = pd.DatetimeIndex(targets[name].index)
            ordinals = index.to_period("M").astype("int64").to_numpy()
            assert set(np.diff(ordinals)) == {1}, name

    def test_monthly_targets_end_at_the_approved_endpoint(self, targets, config):
        end = pd.Timestamp(config.get("samples.monthly_end"))
        for name in ("CPIAUCSL", "INDPRO", "M2SL"):
            assert targets[name].index[-1] == end, name

    def test_enough_observations_for_the_longest_window(self, targets, config):
        for name in ("CPIAUCSL", "INDPRO", "M2SL"):
            assert len(targets[name]) > 300, name
        assert len(targets["GDPC1"]) > 150


class TestARFitsFromCanonicalData:
    def test_ar_fits_on_the_baseline_initial_window(self, targets):
        series = targets["INDPRO"].iloc[:240]
        fit = fit_ar(series, order=4, series="INDPRO")
        assert fit.record.converged
        assert fit.record.status is Status.ADEQUATE
        assert fit.n_obs == 240 - 4
        assert np.isfinite(fit.params).all()
        assert fit.is_stable

    def test_ar_fits_at_every_predeclared_window_length(self, targets, config):
        for frequency, name in (("M", "CPIAUCSL"), ("Q", "GDPC1")):
            series = targets[name]
            for length in config.get(f"robustness.window_lengths.lengths.{frequency}"):
                fit = fit_ar(series.iloc[:length], order=2, series=name)
                assert fit.record.converged, (name, length)
                assert fit.n_obs == length - 2
                assert np.isfinite(fit.params).all(), (name, length)

    def test_forecasts_are_finite_at_every_origin_of_a_short_block(self, targets):
        series = targets["INDPRO"]
        origins = rolling_origins(pd.DatetimeIndex(series.index), 240, horizon=1)[-12:]
        for origin in origins:
            window = series.iloc[origin.estimation_slice()]
            fit = fit_ar(window, order=4, series="INDPRO", refit_date=str(origin.origin_date.date()))
            prediction = fit.forecast(window, horizon=1)
            assert prediction.shape == (1,)
            assert np.isfinite(prediction).all()

    def test_one_step_forecast_matches_the_explicit_ar_recursion(self, targets):
        window = targets["INDPRO"].iloc[:240]
        fit = fit_ar(window, order=3)
        manual = fit.intercept + float(
            fit.phi @ window.to_numpy()[-3:][::-1]
        )
        assert fit.forecast(window, 1)[0] == pytest.approx(manual)

    def test_iterated_multistep_feeds_its_own_forecasts_forward(self, targets):
        window = targets["INDPRO"].iloc[:240]
        fit = fit_ar(window, order=2)
        path = fit.forecast(window, horizon=3)
        assert path.shape == (3,)
        assert np.isfinite(path).all()
        step2 = fit.intercept + fit.phi[0] * path[0] + fit.phi[1] * window.to_numpy()[-1]
        assert path[1] == pytest.approx(step2)

    def test_design_matrix_has_no_dropped_rows_after_imputation(self, targets):
        # The LOCF removed the only interior gap, so no estimation row is lost to
        # missing data anywhere in the monthly sample.
        design = lag_matrix(targets["CPIAUCSL"], 12)
        assert len(design.incomplete_index) == 0
        assert design.n_obs == len(targets["CPIAUCSL"]) - 12


class TestWindowLengthComparabilityOnRealData:
    def test_common_calendar_aligns_all_three_lengths(self, targets, config):
        series = targets["CPIAUCSL"]
        index = pd.DatetimeIndex(series.index)
        lengths = config.get("robustness.window_lengths.lengths.M")
        calendar = common_calendar(index, lengths, horizon=1)
        assert calendar[0] == index[max(lengths)]
        for length in lengths:
            origins = restrict_to_calendar(rolling_origins(index, length), calendar)
            assert [o.target_date for o in origins] == list(calendar)

    def test_the_same_target_date_uses_different_windows_per_length(self, targets, config):
        series = targets["CPIAUCSL"]
        index = pd.DatetimeIndex(series.index)
        lengths = config.get("robustness.window_lengths.lengths.M")
        calendar = common_calendar(index, lengths, horizon=1)
        chosen = calendar[0]
        starts = {}
        for length in lengths:
            origin = next(
                o for o in rolling_origins(index, length) if o.target_date == chosen
            )
            assert o_end_matches(origin, index)
            starts[length] = origin.window_start
        # Same origin and target, trailing windows of different lengths.
        assert len(set(starts.values())) == 3
        assert starts[180] > starts[240] > starts[300]


def o_end_matches(origin, index) -> bool:
    """The origin is the same calendar date whatever the window length."""
    return index[origin.position] == origin.origin_date
