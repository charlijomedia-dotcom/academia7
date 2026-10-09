"""Sample construction, approved ranges, and enforcement of the open N1 decision."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from thesis.data.samples import (
    OpenDecisionError,
    apply_decided_transform,
    build_target,
    clip_to_approved_range,
    known_missing,
    var_common_sample,
)


def monthly(values, start="2000-01-01"):
    index = pd.date_range(start, periods=len(values), freq="MS")
    return pd.Series(np.asarray(values, dtype=float), index=index)


def quarterly(values, start="2000-01-01"):
    index = pd.date_range(start, periods=len(values), freq="QS")
    return pd.Series(np.asarray(values, dtype=float), index=index)


class TestApprovedRanges:
    def test_monthly_series_truncated_to_the_approved_endpoint(self, config):
        # FEDFUNDS carries 2026-09 in the vintage; the approved endpoint is 2026-08.
        index = pd.date_range("1954-07-01", "2026-09-01", freq="MS")
        raw = pd.Series(np.arange(len(index), dtype=float), index=index)
        clipped = clip_to_approved_range(raw, "FEDFUNDS", config)
        assert clipped.index[0] == pd.Timestamp("1954-07-01")
        assert clipped.index[-1] == pd.Timestamp("2026-08-01")

    def test_indpro_truncated_to_1947(self, config):
        index = pd.date_range("1919-01-01", "2026-08-01", freq="MS")
        raw = pd.Series(np.arange(len(index), dtype=float) + 1.0, index=index)
        clipped = clip_to_approved_range(raw, "INDPRO", config)
        assert clipped.index[0] == pd.Timestamp("1947-01-01")
        assert clipped.index[-1] == pd.Timestamp("2026-08-01")

    def test_gdp_truncated_to_2026q2(self, config):
        index = pd.date_range("1947-01-01", "2026-10-01", freq="QS")
        raw = pd.Series(np.arange(len(index), dtype=float) + 1.0, index=index)
        clipped = clip_to_approved_range(raw, "GDPC1", config)
        assert clipped.index[-1] == pd.Timestamp("2026-04-01")


class TestTargetConstruction:
    def test_indpro_growth_is_annualized_at_1200(self, config):
        index = pd.date_range("1947-01-01", periods=6, freq="MS")
        raw = pd.Series(100.0 * np.exp(np.arange(6) * 0.01), index=index)
        target = build_target("INDPRO", raw, config)
        assert target.iloc[0] == pytest.approx(1200.0 * 0.01)
        assert len(target) == 5  # the first observation is lost to differencing

    def test_gdp_growth_is_annualized_at_400(self, config):
        index = pd.date_range("1947-01-01", periods=4, freq="QS")
        raw = pd.Series(100.0 * np.exp(np.arange(4) * 0.02), index=index)
        target = build_target("GDPC1", raw, config)
        assert target.iloc[0] == pytest.approx(400.0 * 0.02)

    def test_usrec_is_not_transformed(self, config):
        index = pd.date_range("1947-01-01", periods=6, freq="MS")
        raw = pd.Series([0, 0, 1, 1, 0, 0], index=index, dtype=float)
        out = build_target("USREC", raw, config)
        np.testing.assert_allclose(out.to_numpy(), raw.to_numpy())

    def test_rate_series_requires_the_stationarity_decision(self, config):
        index = pd.date_range("1954-07-01", periods=10, freq="MS")
        raw = pd.Series(np.linspace(1.0, 2.0, 10), index=index)
        with pytest.raises(ValueError, match="stationarity rule"):
            build_target("FEDFUNDS", raw, config)

    def test_decided_transform_level_and_difference(self, config):
        index = pd.date_range("1954-07-01", periods=5, freq="MS")
        raw = pd.Series([1.0, 1.5, 2.0, 2.5, 3.0], index=index)
        level = apply_decided_transform("FEDFUNDS", raw, "level", config)
        assert len(level) == 5
        diff = apply_decided_transform("FEDFUNDS", raw, "difference", config)
        assert len(diff) == 4
        assert np.allclose(diff.to_numpy(), 0.5)

    def test_unknown_decision_rejected(self, config):
        index = pd.date_range("1954-07-01", periods=3, freq="MS")
        raw = pd.Series([1.0, 2.0, 3.0], index=index)
        with pytest.raises(ValueError):
            apply_decided_transform("FEDFUNDS", raw, "logdiff", config)


class TestOpenDecisionBlocker:
    """The permanent 2025-10 gap must stop work on the affected series, not be guessed.

    CLAUDE.md §4 requires the affected analysis to stop until the user decides. The two
    series with a known gap therefore refuse to produce a modelling target while
    `missing_data_policy` is unset, and the four complete series are unaffected.
    """

    def test_known_missing_recorded_for_the_affected_series(self, config):
        assert known_missing("CPIAUCSL", config) == ["2025-10-01"]
        assert known_missing("UNRATE", config) == ["2025-10-01"]
        assert known_missing("INDPRO", config) == []
        assert known_missing("GDPC1", config) == []

    def test_policy_is_unset_so_cpi_is_blocked(self, config):
        assert config.get("missing_data_policy") is None
        index = pd.date_range("1947-01-01", periods=12, freq="MS")
        raw = pd.Series(np.arange(12, dtype=float) + 100.0, index=index)
        with pytest.raises(OpenDecisionError, match="N1"):
            build_target("CPIAUCSL", raw, config)

    def test_unrate_is_blocked_too(self, config):
        index = pd.date_range("1948-01-01", periods=12, freq="MS")
        raw = pd.Series(np.linspace(4.0, 5.0, 12), index=index)
        with pytest.raises(OpenDecisionError):
            apply_decided_transform("UNRATE", raw, "level", config)

    def test_complete_series_are_not_blocked(self, config):
        index = pd.date_range("1947-01-01", periods=12, freq="MS")
        raw = pd.Series(100.0 * np.exp(np.arange(12) * 0.005), index=index)
        build_target("INDPRO", raw, config)  # must not raise

    def test_setting_a_policy_unblocks(self, config):
        decided = config.with_overrides(
            {"missing_data_policy": {"rule": "complete_case"}}, "test-decision"
        )
        index = pd.date_range("1947-01-01", periods=12, freq="MS")
        raw = pd.Series(np.arange(12, dtype=float) + 100.0, index=index)
        target = build_target("CPIAUCSL", raw, decided)
        assert len(target) == 11


class TestVarSample:
    def test_common_sample_respects_approved_bounds(self, config):
        index = pd.date_range("1947-01-01", "2026-08-01", freq="MS")
        targets = {
            name: pd.Series(np.arange(len(index), dtype=float), index=index)
            for name in config.get("models.var.variables")
        }
        frame = var_common_sample(targets, config)
        assert frame.index[0] == pd.Timestamp("1959-01-01")
        assert frame.index[-1] == pd.Timestamp("2026-08-01")
        assert list(frame.columns) == config.get("models.var.variables")

    def test_missing_variable_is_an_error_not_a_silent_drop(self, config):
        index = pd.date_range("1959-01-01", periods=10, freq="MS")
        targets = {"CPIAUCSL": pd.Series(np.arange(10, dtype=float), index=index)}
        with pytest.raises(KeyError):
            var_common_sample(targets, config)
