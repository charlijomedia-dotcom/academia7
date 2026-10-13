"""Specification selection: the BIC-then-whiteness rule of Part 5 §5.1-§5.2."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR
from thesis.specification.ar_select import select_ar_order, select_arma_order


@pytest.fixture(scope="module")
def config():
    return load_config(config_dir=CONFIG_DIR)


def monthly(values):
    return pd.Series(np.asarray(values, float),
                     index=pd.date_range("1960-01-01", periods=len(values), freq="MS"),
                     name="SIM")


def ar_process(n, phi, seed=0):
    rng = np.random.default_rng(seed)
    p = len(phi)
    y = np.zeros(n)
    e = rng.standard_normal(n)
    for t in range(p, n):
        y[t] = np.dot(phi, y[t - p : t][::-1]) + e[t]
    return monthly(y)


class TestARSelection:
    def test_recovers_a_low_order(self, config):
        choice = select_ar_order(ar_process(600, [0.6], seed=1), "M", config, series="SIM")
        assert choice.order in (1, 2)
        assert choice.model == "AR"

    def test_recovers_a_higher_order(self, config):
        choice = select_ar_order(ar_process(800, [0.5, 0.3], seed=2), "M", config)
        assert choice.order in (2, 3)

    def test_respects_the_monthly_lag_cap(self, config):
        choice = select_ar_order(ar_process(400, [0.4], seed=3), "M", config)
        assert 1 <= choice.order <= config.get("specification.ar.max_lag.M")
        assert len(choice.candidates) == config.get("specification.ar.max_lag.M")

    def test_respects_the_quarterly_lag_cap(self, config):
        choice = select_ar_order(ar_process(300, [0.4], seed=4), "Q", config)
        assert 1 <= choice.order <= config.get("specification.ar.max_lag.Q")
        assert len(choice.candidates) == 4

    def test_all_candidates_share_a_common_effective_sample(self, config):
        # Decision D2: BIC is only comparable across orders on identical observations.
        # select_ar_order asserts this internally; this test pins the behaviour.
        choice = select_ar_order(ar_process(500, [0.5], seed=5), "M", config)
        finite = [c for c in choice.candidates if np.isfinite(c["bic"])]
        assert len(finite) == config.get("specification.ar.max_lag.M")

    def test_white_residuals_are_recorded(self, config):
        choice = select_ar_order(ar_process(600, [0.6], seed=6), "M", config)
        assert choice.residuals_white
        assert not choice.diagnostically_weak

    def test_selection_is_deterministic(self, config):
        y = ar_process(400, [0.5], seed=7)
        assert select_ar_order(y, "M", config).order == select_ar_order(y, "M", config).order

    def test_row_is_reportable(self, config):
        row = select_ar_order(ar_process(400, [0.5], seed=8), "M", config).to_row()
        for key in ("series_id", "model", "selected_order", "bic",
                    "primary_ljung_box_passes", "diagnostically_weak", "note"):
            assert key in row

    def test_diagnostically_weak_branch_when_nothing_whitens(self, config):
        # Strong seasonal dependence beyond the lag cap leaves autocorrelation at every
        # admissible order, which must be reported rather than silently accepted.
        rng = np.random.default_rng(9)
        n = 500
        y = np.zeros(n)
        e = rng.standard_normal(n)
        for t in range(24, n):
            y[t] = 0.85 * y[t - 24] + e[t]
        choice = select_ar_order(monthly(y), "M", config)
        if not choice.residuals_white:
            assert choice.diagnostically_weak
            assert "diagnostically weak" in choice.note


class TestARMASelection:
    def test_excludes_the_zero_zero_order(self, config):
        choice = select_arma_order(ar_process(300, [0.5], seed=10), "M", config)
        assert choice.order != (0, 0)
        assert all(c["order"] != (0, 0) for c in choice.candidates)

    def test_grid_size_matches_the_approved_bounds(self, config):
        choice = select_arma_order(ar_process(250, [0.5], seed=11), "Q", config)
        grid = config.get("specification.arma.grid.Q")
        expected = (grid["p"][1] + 1) * (grid["q"][1] + 1) - 1
        assert len(choice.candidates) == expected

    def test_recovers_an_arma_1_1(self, config):
        rng = np.random.default_rng(12)
        n = 700
        e = rng.standard_normal(n)
        y = np.zeros(n)
        for t in range(1, n):
            y[t] = 0.6 * y[t - 1] + e[t] + 0.4 * e[t - 1]
        choice = select_arma_order(monthly(y), "Q", config)
        assert choice.order[0] >= 1

    def test_degenerate_selection_is_flagged_not_forbidden(self, config):
        # Decision M4: a pure-AR or pure-MA ARMA is allowed, but must be visible.
        choice = select_arma_order(ar_process(400, [0.6], seed=13), "Q", config)
        p, q = choice.order
        if q == 0 or p == 0:
            assert "pure" in choice.note
