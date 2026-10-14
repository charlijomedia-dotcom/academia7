"""T4.9 must actually see the October 2025 imputations it exists to measure.

The approved amendment created T4.9 to quantify how far the two user-approved October 2025
LOCF cells reach into the forecasting results. Under the horizon-bounded origin set the
primary h=1 evaluation stopped at September 2025, one month before the imputed cell, so
every target-side exposure flag was necessarily false and the diagnostic was vacuous at
the horizon that matters most.

These tests assert the corrected engine reaches those dates, and that each exposure flag
fires exactly where the transformation arithmetic says it should: 1200*dlog(CPI) at t uses
the levels at t and t-1, so an imputed October level contaminates both the October and the
November growth observations, and no others.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR, FROZEN_DIR
from thesis.data.canonical import STATUS_IMPUTED, to_panels
from thesis.data.store import load_bundle
from thesis.forecasting.rolling import run_chain
from thesis.models.registry import AR, ModelSpec
from thesis.transforms.growth import annualized_logdiff

IMPUTED_RAW = pd.Timestamp("2025-10-01")
AFFECTED_GROWTH = {pd.Timestamp("2025-10-01"), pd.Timestamp("2025-11-01")}


@pytest.fixture(scope="module")
def config():
    return load_config(names=("baseline", "series_catalog", "thresholds"),
                       config_dir=CONFIG_DIR)


@pytest.fixture(scope="module")
def bundle(config):
    return load_bundle(FROZEN_DIR, config)


@pytest.fixture(scope="module")
def cpi_growth(bundle):
    panels = to_panels(bundle.frame)
    return annualized_logdiff(panels["M"]["CPIAUCSL"].dropna(), 1200).dropna()


@pytest.fixture(scope="module")
def chain(config, cpi_growth):
    return run_chain("CPIAUCSL", cpi_growth, ModelSpec(AR, order=1), [1, 3, 6, 12], 240,
                     config, frequency="M")


class TestTheImputedCellsAreWhereTheAmendmentSaid:
    def test_exactly_one_imputed_cell_per_affected_series(self, bundle):
        frame = bundle.frame
        imputed = frame[frame["observation_status"] == STATUS_IMPUTED]
        assert len(imputed) == 2
        assert set(imputed["series_id"]) == {"CPIAUCSL", "UNRATE"}
        assert set(pd.DatetimeIndex(imputed["date"])) == {IMPUTED_RAW}

    def test_the_october_cpi_inflation_is_exactly_zero(self, cpi_growth):
        # September's level carried forward means no price change in October, by
        # construction. This is the artefact the amendment accepted and T4.9 discloses.
        assert cpi_growth.loc[IMPUTED_RAW] == pytest.approx(0.0, abs=1e-12)

    def test_november_carries_the_two_month_change(self, cpi_growth, bundle):
        panels = to_panels(bundle.frame)
        level = panels["M"]["CPIAUCSL"].dropna()
        expected = 1200.0 * np.log(float(level.loc["2025-11-01"])
                                   / float(level.loc["2025-09-01"]))
        assert cpi_growth.loc["2025-11-01"] == pytest.approx(expected, rel=1e-12)


class TestTheEvaluationReachesThoseDates:
    def test_h1_targets_include_both_affected_growth_observations(self, chain):
        h1 = chain.forecasts[chain.forecasts["horizon"] == 1]
        assert AFFECTED_GROWTH <= set(h1["target_date"])

    def test_h1_runs_past_them_to_the_approved_endpoint(self, chain):
        h1 = chain.forecasts[chain.forecasts["horizon"] == 1]
        assert h1["target_date"].max() == pd.Timestamp("2026-08-01")

    def test_the_affected_targets_carry_finite_forecasts_and_errors(self, chain):
        h1 = chain.forecasts[chain.forecasts["horizon"] == 1]
        affected = h1[h1["target_date"].isin(AFFECTED_GROWTH)]
        assert len(affected) == 2
        assert np.isfinite(affected["forecast"]).all()
        assert np.isfinite(affected["error"]).all()

    def test_the_horizon_bounded_origin_set_would_have_missed_them(self, chain, cpi_growth):
        # The defect, pinned so it cannot return: had origins been bounded by the longest
        # horizon, the last h=1 origin would have been twelve observations from the end
        # and no affected target would have been evaluated at the primary horizon.
        index = pd.DatetimeIndex(cpi_growth.index)
        last_origin_under_old_rule = index[len(index) - 1 - 12]
        h1 = chain.forecasts[chain.forecasts["horizon"] == 1]
        truncated = h1[h1["origin_date"] <= last_origin_under_old_rule]
        assert truncated["target_date"].max() == pd.Timestamp("2025-09-01")
        assert not AFFECTED_GROWTH & set(truncated["target_date"])
        # And the corrected set recovers exactly the eleven months that were lost.
        assert len(h1) - len(truncated) == 11


class TestExposureFlagsFireExactlyWhereTheyShould:
    def test_only_the_october_target_is_flagged_as_imputed(self, chain):
        h1 = chain.forecasts[chain.forecasts["horizon"] == 1]
        flagged = {d for d in h1["target_date"] if d == IMPUTED_RAW}
        assert flagged == {IMPUTED_RAW}

    def test_november_is_flagged_through_its_predecessor_not_as_imputed_itself(self,
                                                                               bundle):
        # The distinction T4.9 requires: November's own level is official, but its growth
        # rate is computed from the imputed October level.
        frame = bundle.frame
        november = frame[(frame["series_id"] == "CPIAUCSL")
                         & (frame["date"] == pd.Timestamp("2025-11-01"))]
        assert november["observation_status"].iloc[0] != STATUS_IMPUTED

    def test_no_other_growth_observation_depends_on_the_imputed_level(self, cpi_growth):
        index = pd.DatetimeIndex(cpi_growth.index)
        position = {date: i for i, date in enumerate(index)}
        derived = {IMPUTED_RAW, index[position[IMPUTED_RAW] + 1]}
        assert derived == AFFECTED_GROWTH

    def test_the_official_raw_value_is_preserved_as_missing(self, bundle):
        frame = bundle.frame
        cell = frame[(frame["series_id"] == "CPIAUCSL") & (frame["date"] == IMPUTED_RAW)]
        assert str(cell["source_value"].iloc[0]).strip() in ("", "nan", ".")
        assert cell["imputation_source_date"].iloc[0] == "2025-09-01"
