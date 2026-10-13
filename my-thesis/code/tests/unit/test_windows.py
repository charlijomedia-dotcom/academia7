"""Rolling-window boundaries, origin alignment and the T4.8 common calendar."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR
from thesis.forecasting.windows import (
    baseline_window,
    common_calendar,
    describe_coverage,
    initial_window,
    restrict_to_calendar,
    rolling_origins,
    window_lengths_for,
)


def monthly_index(n: int, start: str = "1947-01-01") -> pd.DatetimeIndex:
    return pd.date_range(start, periods=n, freq="MS")


class TestRollingOrigins:
    def test_first_origin_has_a_full_window(self):
        index = monthly_index(300)
        origins = rolling_origins(index, 240, horizon=1)
        first = origins[0]
        assert first.position == 239
        assert first.window_start == index[0]
        assert first.window_end == index[239]
        assert first.target_date == index[240]

    def test_last_origin_leaves_room_for_the_target(self):
        index = monthly_index(300)
        origins = rolling_origins(index, 240, horizon=1)
        assert origins[-1].target_position == 299
        assert origins[-1].target_date == index[-1]

    def test_origin_count(self):
        index = monthly_index(300)
        assert len(rolling_origins(index, 240, horizon=1)) == 60
        assert len(rolling_origins(index, 180, horizon=1)) == 120
        assert len(rolling_origins(index, 300, horizon=1)) == 0

    def test_window_length_is_constant(self):
        index = monthly_index(400)
        for origin in rolling_origins(index, 240):
            sample = index[origin.estimation_slice()]
            assert len(sample) == 240
            assert sample[0] == origin.window_start
            assert sample[-1] == origin.window_end

    def test_window_never_reaches_past_the_origin(self):
        index = monthly_index(400)
        for origin in rolling_origins(index, 240):
            assert index[origin.estimation_slice()][-1] <= origin.origin_date
            assert origin.target_date > origin.origin_date

    def test_horizon_shifts_only_the_target(self):
        index = monthly_index(300)
        base = rolling_origins(index, 240, horizon=1)[0]
        far = rolling_origins(index, 240, horizon=12)[0]
        assert far.window_start == base.window_start
        assert far.window_end == base.window_end
        assert far.target_position == base.target_position + 11

    def test_quarterly_baseline(self):
        index = pd.date_range("1947-01-01", periods=318, freq="QS")
        origins = rolling_origins(index, 120, horizon=1)
        assert origins[0].window_start == index[0]
        assert origins[0].target_date == index[120]
        assert len(origins) == 318 - 120

    def test_invalid_arguments_rejected(self):
        index = monthly_index(50)
        with pytest.raises(ValueError):
            rolling_origins(index, 0)
        with pytest.raises(ValueError):
            rolling_origins(index, 10, horizon=0)

    def test_max_origins_keeps_the_most_recent(self):
        index = monthly_index(300)
        full = rolling_origins(index, 240)
        limited = rolling_origins(index, 240, max_origins=5)
        assert limited == full[-5:]


class TestInitialWindow:
    def test_initial_window_is_the_first_full_window(self):
        index = monthly_index(400)
        window = initial_window(index, 240)
        assert len(window) == 240
        assert window[0] == index[0]
        assert window[-1] == index[239]

    def test_too_short_series_rejected(self):
        with pytest.raises(ValueError):
            initial_window(monthly_index(100), 240)


class TestCommonCalendar:
    """T4.8: every window length is scored on identical target dates."""

    def test_calendar_starts_when_the_longest_window_is_available(self):
        index = monthly_index(500)
        calendar = common_calendar(index, [180, 240, 300], horizon=1)
        assert calendar[0] == index[300]
        assert calendar[-1] == index[-1]
        assert len(calendar) == 200

    def test_each_length_contributes_the_same_targets(self):
        index = monthly_index(500)
        calendar = common_calendar(index, [180, 240, 300])
        for length in (180, 240, 300):
            origins = restrict_to_calendar(rolling_origins(index, length), calendar)
            assert [o.target_date for o in origins] == list(calendar)

    def test_quarterly_calendar(self):
        index = pd.date_range("1947-01-01", periods=318, freq="QS")
        calendar = common_calendar(index, [90, 120, 150], horizon=1)
        assert calendar[0] == index[150]
        assert len(calendar) == 318 - 150

    def test_baseline_alone_gives_its_own_calendar(self):
        index = monthly_index(500)
        calendar = common_calendar(index, [240])
        assert calendar[0] == index[240]

    def test_empty_lengths_rejected(self):
        with pytest.raises(ValueError):
            common_calendar(monthly_index(100), [])

    def test_coverage_audit_reports_dropped_dates(self):
        index = monthly_index(500)
        coverage = describe_coverage(index, [180, 240, 300])
        assert coverage[300]["n_dropped_by_alignment"] == 0
        assert coverage[180]["n_dropped_by_alignment"] == 120
        assert coverage[240]["n_dropped_by_alignment"] == 60
        for length in (180, 240, 300):
            assert coverage[length]["n_on_common_calendar"] == 200


class TestApprovedLengths:
    def test_config_lengths_match_the_amendment(self):
        config = load_config(config_dir=CONFIG_DIR)
        assert window_lengths_for("M", config) == [180, 240, 300]
        assert window_lengths_for("Q", config) == [90, 120, 150]
        assert baseline_window("M", config) == 240
        assert baseline_window("Q", config) == 120

    def test_alternatives_are_plus_minus_25_percent(self):
        config = load_config(config_dir=CONFIG_DIR)
        for frequency in ("M", "Q"):
            shorter, baseline, longer = window_lengths_for(frequency, config)
            assert shorter == pytest.approx(0.75 * baseline)
            assert longer == pytest.approx(1.25 * baseline)
            assert baseline == baseline_window(frequency, config)

    def test_window_length_robustness_settings(self):
        config = load_config(config_dir=CONFIG_DIR)
        assert config.get("robustness.window_lengths.models") == ["AR", "ARMA", "MSAR", "STAR"]
        assert config.get("robustness.window_lengths.horizon") == 1
        assert config.get("robustness.window_lengths.reuse_baseline_discrete_specs") is True
        assert config.get("robustness.window_lengths.research_specs_per_length") is False
        assert config.get("robustness.window_lengths.never_overwrite_baseline") is True
        assert config.get("robustness.window_lengths.common_calendar_from") == "longest_window"
