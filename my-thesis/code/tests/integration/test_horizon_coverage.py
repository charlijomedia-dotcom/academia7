"""Every horizon must reach its own last eligible target date.

One fitted model serves all requested horizons, so the origin set must not be bounded by
the *longest* horizon. Doing so silently discarded the late-sample origins at which a
shorter horizon still had a realized target: with horizons [1,3,6,12] the monthly h=1
forecasts stopped at September 2025 instead of August 2026, losing eleven target dates per
series, and quarterly h=1 stopped at 2025Q3 instead of 2026Q2. Part 5 §9.4 makes h=1 the
primary exercise and the longer horizons separate robustness analyses, so h=1 must run to
the approved endpoint whether or not h=12 was also requested.

These tests pin the corrected behaviour on the real frozen data, at the approved window
lengths and horizons, using the cheapest model so they stay fast.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR, FROZEN_DIR
from thesis.data.canonical import to_panels
from thesis.data.store import load_bundle
from thesis.diagnostics.decision_rule import confirm_on_full_sample, decide_transformation
from thesis.forecasting.rolling import run_chain
from thesis.forecasting.windows import (estimation_origins, horizon_coverage,
                                        rolling_origins, targets_for)
from thesis.models.registry import AR, ModelSpec
from thesis.transforms.growth import annualized_logdiff

MONTHLY_END = pd.Timestamp("2026-08-01")
QUARTERLY_END = pd.Timestamp("2026-04-01")      # 2026Q2


@pytest.fixture(scope="module")
def config():
    return load_config(names=("baseline", "series_catalog", "thresholds"),
                       config_dir=CONFIG_DIR)


@pytest.fixture(scope="module")
def panels(config):
    return to_panels(load_bundle(FROZEN_DIR, config).frame)


@pytest.fixture(scope="module")
def targets(config, panels):
    """Every approved target in its approved modelling transformation."""
    out = {}
    for row in config.get("catalog"):
        series_id = row["series_id"]
        if not row.get("retained") or series_id == "USREC":
            continue
        spec = config.get(f"targets.{series_id}")
        frequency = spec["frequency"]
        level = panels[frequency][series_id].dropna()
        if spec["transform"]["kind"] == "logdiff_annualized":
            series = annualized_logdiff(level, float(spec["transform"]["k"])).dropna()
        else:
            window = int(config.get(f"forecasting.windows.{frequency}"))
            decision = confirm_on_full_sample(
                decide_transformation(series_id, level.iloc[:window], frequency, config),
                level, frequency, config)
            series = level if decision.decision == "level" else level.diff().dropna()
        out[series_id] = (frequency, series)
    return out


def _horizons(config, frequency):
    return sorted({int(config.get(f"forecasting.horizons.primary.{frequency}")),
                   *[int(h) for h in config.get(f"forecasting.horizons.robustness.{frequency}")]})


class TestOriginSetIsNotBoundedByTheLongestHorizon:
    def test_origins_are_bounded_by_the_shortest_requested_horizon(self):
        index = pd.date_range("2000-01-01", periods=60, freq="MS")
        origins = estimation_origins(index, 24, [1, 3, 6, 12])
        # The last origin must be the one whose h=1 target is the final observation.
        assert origins[-1].position == len(index) - 2
        assert origins[-1].target_date == index[-1]

    def test_the_longest_horizon_alone_gives_a_shorter_origin_set(self):
        index = pd.date_range("2000-01-01", periods=60, freq="MS")
        assert len(estimation_origins(index, 24, [12])) < len(
            estimation_origins(index, 24, [1, 12]))

    def test_requesting_extra_horizons_never_removes_an_origin(self):
        index = pd.date_range("2000-01-01", periods=80, freq="MS")
        base = estimation_origins(index, 24, [1])
        widened = estimation_origins(index, 24, [1, 3, 6, 12])
        assert [o.position for o in base] == [o.position for o in widened]

    def test_targets_for_omits_only_horizons_past_the_sample_end(self):
        index = pd.date_range("2000-01-01", periods=30, freq="MS")
        origins = estimation_origins(index, 24, [1, 3, 6])
        last = origins[-1]
        realizable = {h for h, _, _ in targets_for(last, [1, 3, 6], index)}
        assert realizable == {1}, "only h=1 is realizable from the final origin"
        first = origins[0]
        assert {h for h, _, _ in targets_for(first, [1, 3, 6], index)} == {1, 3, 6}

    def test_target_dates_are_the_origin_date_shifted_by_the_horizon(self):
        index = pd.date_range("2000-01-01", periods=60, freq="MS")
        origin = estimation_origins(index, 24, [1, 3])[10]
        for horizon, position, date in targets_for(origin, [1, 3], index):
            assert position == origin.position + horizon
            assert date == index[origin.position + horizon]


class TestEveryTargetReachesTheApprovedEndpoint:
    def test_monthly_h1_reaches_august_2026(self, config, targets):
        for series_id, (frequency, series) in targets.items():
            if frequency != "M":
                continue
            coverage = horizon_coverage(pd.DatetimeIndex(series.index),
                                        int(config.get("forecasting.windows.M")),
                                        _horizons(config, "M"))
            assert coverage[1]["last_target"] == MONTHLY_END, series_id

    def test_quarterly_h1_reaches_2026q2(self, config, targets):
        frequency, series = targets["GDPC1"]
        assert frequency == "Q"
        coverage = horizon_coverage(pd.DatetimeIndex(series.index),
                                    int(config.get("forecasting.windows.Q")),
                                    _horizons(config, "Q"))
        assert coverage[1]["last_target"] == QUARTERLY_END

    def test_every_horizon_reaches_its_own_last_eligible_target(self, config, targets):
        # The last eligible target for any horizon is the final observation: the origin
        # h steps earlier always has a full estimation window on these samples.
        for series_id, (frequency, series) in targets.items():
            index = pd.DatetimeIndex(series.index)
            window = int(config.get(f"forecasting.windows.{frequency}"))
            coverage = horizon_coverage(index, window, _horizons(config, frequency))
            for horizon, entry in coverage.items():
                assert entry["last_target"] == index[-1], f"{series_id} h={horizon}"
                assert entry["last_origin"] == index[-1 - horizon], f"{series_id} h={horizon}"

    def test_shorter_horizons_have_at_least_as_many_origins_as_longer_ones(self, config,
                                                                           targets):
        for series_id, (frequency, series) in targets.items():
            coverage = horizon_coverage(pd.DatetimeIndex(series.index),
                                        int(config.get(f"forecasting.windows.{frequency}")),
                                        _horizons(config, frequency))
            counts = [coverage[h]["n_origins"] for h in sorted(coverage)]
            assert counts == sorted(counts, reverse=True), series_id

    def test_the_monthly_targets_lost_before_the_fix_are_now_present(self, config, targets):
        # The eleven months October 2025 to August 2026, which the longest-horizon bound
        # had removed from every monthly h=1 series.
        expected = pd.date_range("2025-10-01", "2026-08-01", freq="MS")
        for series_id, (frequency, series) in targets.items():
            if frequency != "M":
                continue
            origins = estimation_origins(pd.DatetimeIndex(series.index),
                                         int(config.get("forecasting.windows.M")),
                                         _horizons(config, "M"))
            h1_targets = {o.target_date for o in origins}
            assert set(expected) <= h1_targets, series_id

    def test_the_quarterly_targets_lost_before_the_fix_are_now_present(self, config, targets):
        expected = pd.DatetimeIndex(["2025-10-01", "2026-01-01", "2026-04-01"])
        _, series = targets["GDPC1"]
        origins = estimation_origins(pd.DatetimeIndex(series.index),
                                     int(config.get("forecasting.windows.Q")),
                                     _horizons(config, "Q"))
        assert set(expected) <= {o.target_date for o in origins}


@pytest.fixture(scope="module")
def indpro_chain(config, targets):
    _, series = targets["INDPRO"]
    return run_chain("INDPRO", series, ModelSpec(AR, order=1), [1, 3, 6, 12], 240,
                     config, frequency="M")


@pytest.fixture(scope="module")
def gdp_chain(config, targets):
    _, series = targets["GDPC1"]
    return run_chain("GDPC1", series, ModelSpec(AR, order=1), [1, 2, 4], 120,
                     config, frequency="Q")


class TestTheEngineEmitsThoseRows:
    def test_monthly_h1_forecast_rows_reach_august_2026(self, indpro_chain):
        rows = indpro_chain.forecasts
        h1 = rows[rows["horizon"] == 1]
        assert h1["target_date"].max() == MONTHLY_END
        assert np.isfinite(h1[h1["target_date"] == MONTHLY_END]["forecast"]).all()

    def test_quarterly_h1_forecast_rows_reach_2026q2(self, gdp_chain):
        rows = gdp_chain.forecasts
        h1 = rows[rows["horizon"] == 1]
        assert h1["target_date"].max() == QUARTERLY_END

    def test_every_horizon_reaches_the_sample_end_in_the_emitted_rows(self, indpro_chain,
                                                                      gdp_chain):
        for chain, end in ((indpro_chain, MONTHLY_END), (gdp_chain, QUARTERLY_END)):
            for horizon in sorted(chain.forecasts["horizon"].unique()):
                subset = chain.forecasts[chain.forecasts["horizon"] == horizon]
                assert subset["target_date"].max() == end, horizon

    def test_each_row_has_the_actual_value_for_its_own_target_date(self, indpro_chain,
                                                                   config, targets):
        _, series = targets["INDPRO"]
        lookup = series.to_dict()
        sample = indpro_chain.forecasts.sample(200, random_state=0)
        for row in sample.itertuples():
            assert row.actual == pytest.approx(lookup[row.target_date]), row.target_date

    def test_the_target_date_is_the_origin_shifted_by_the_horizon(self, indpro_chain,
                                                                  targets):
        _, series = targets["INDPRO"]
        position = {date: i for i, date in enumerate(pd.DatetimeIndex(series.index))}
        for row in indpro_chain.forecasts.sample(200, random_state=1).itertuples():
            assert position[row.target_date] == position[row.origin_date] + row.horizon

    def test_no_predictor_comes_from_after_the_origin(self, config, targets):
        # No look-ahead: the estimation window ends at the origin, never later.
        _, series = targets["INDPRO"]
        index = pd.DatetimeIndex(series.index)
        for origin in estimation_origins(index, 240, [1, 3, 6, 12])[-50:]:
            assert origin.window_end == origin.origin_date
            assert origin.window_start == index[origin.position - 239]
            assert origin.window_end <= origin.origin_date

    def test_the_coverage_audit_matches_the_emitted_rows(self, indpro_chain):
        for row in indpro_chain.coverage_rows():
            assert row["n_rows_emitted"] == row["n_eligible_origins"], row["horizon"]
            assert row["n_finite_forecasts"] == row["n_rows_emitted"], row["horizon"]

    def test_h1_gained_exactly_the_eleven_previously_lost_months(self, indpro_chain):
        h1 = indpro_chain.forecasts[indpro_chain.forecasts["horizon"] == 1]
        h12 = indpro_chain.forecasts[indpro_chain.forecasts["horizon"] == 12]
        assert len(h1) - len(h12) == 11
