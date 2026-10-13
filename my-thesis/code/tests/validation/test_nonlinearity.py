"""Pre-estimation nonlinearity evidence: Tsay and the Teräsvirta sequence.

Decision D3 asked for validation against a recognized implementation (R `TSA::Tsay.test`)
and against simulations. R is not available in this container, so the implementation is
cross-validated algebraically instead: the orthogonalized form must equal the direct nested
F test by the Frisch-Waugh-Lovell theorem. That is an exact identity, not an approximation,
and it pins the statistic independently of how it is computed. The simulation checks on
size and power are done as specified.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR
from thesis.diagnostics.nonlinearity import (
    _ar_design,
    _ols_residuals,
    lst_linearity,
    select_delay_and_type,
    tsay_test,
)
from thesis.models.star import ESTAR, LSTAR, transition


@pytest.fixture(scope="module")
def config():
    return load_config(config_dir=CONFIG_DIR)


def monthly(values):
    return pd.Series(np.asarray(values, float),
                     index=pd.date_range("1960-01-01", periods=len(values), freq="MS"),
                     name="SIM")


def linear_ar(n, phi=(0.5,), seed=0):
    rng = np.random.default_rng(seed)
    p = len(phi)
    y = np.zeros(n)
    e = rng.standard_normal(n)
    for t in range(p, n):
        y[t] = np.dot(phi, y[t - p : t][::-1]) + e[t]
    return monthly(y)


def lstar_process(n, gamma=10.0, c=0.0, seed=0, delay=1):
    rng = np.random.default_rng(seed)
    y = np.zeros(n)
    e = rng.standard_normal(n)
    for t in range(2, n):
        g = 1.0 / (1.0 + np.exp(-gamma * (y[t - delay] - c)))
        y[t] = 0.6 * y[t - 1] - 1.2 * g * y[t - 1] + e[t]
    return monthly(y)


def estar_process(n, gamma=0.5, c=0.0, seed=0, delay=1):
    """An ESTAR process whose transition actually varies over the observed range.

    A large gamma saturates the exponential transition at 1 almost everywhere, which
    leaves a nearly linear AR(1) and nothing for a linearity test to find. The smoothness
    here keeps G spread across (0, 1).
    """
    rng = np.random.default_rng(seed)
    y = np.zeros(n)
    e = rng.standard_normal(n)
    for t in range(2, n):
        g = 1.0 - np.exp(-gamma * (y[t - delay] - c) ** 2)
        y[t] = 0.9 * y[t - 1] - 1.6 * g * y[t - 1] + e[t]
    return monthly(y)


class TestTsayAlgebra:
    def test_equals_the_direct_nested_f_test(self):
        """Frisch-Waugh-Lovell: orthogonalizing the quadratic terms must not change the F.

        This is an exact algebraic identity, so it validates the implementation against an
        independently computed statistic rather than against itself.
        """
        y = lstar_process(400, seed=1)
        order = 2
        values = y.to_numpy()
        dependent, X, rows = _ar_design(values, order)

        quadratic = []
        for i in range(1, order + 1):
            for j in range(i, order + 1):
                quadratic.append(values[rows - i] * values[rows - j])
        Z = np.column_stack(quadratic)

        e0 = _ols_residuals(dependent, X)
        e1 = _ols_residuals(dependent, np.column_stack([X, Z]))
        ssr0, ssr1 = float(e0 @ e0), float(e1 @ e1)
        m = Z.shape[1]
        df = dependent.size - X.shape[1] - m
        direct = ((ssr0 - ssr1) / m) / (ssr1 / df)
        direct_p = float(stats.f.sf(direct, m, df))

        result = tsay_test(y, order)
        assert result.statistic == pytest.approx(direct, rel=1e-10)
        assert result.p_value == pytest.approx(direct_p, rel=1e-10)

    def test_number_of_quadratic_terms(self):
        for order in (1, 2, 4, 12):
            result = tsay_test(linear_ar(400, seed=2), order)
            assert result.tuning["n_quadratic_terms"] == order * (order + 1) // 2

    def test_reference_distribution_is_reported(self):
        result = tsay_test(linear_ar(300, seed=3), 2)
        assert result.reference.startswith("F(")
        assert "linear autoregression" in result.null_hypothesis


class TestTsayBehaviour:
    @pytest.mark.slow
    def test_size_is_near_nominal_under_linearity(self):
        rejections = sum(
            tsay_test(linear_ar(300, seed=s), 2).p_value < 0.05 for s in range(200)
        )
        assert 0.01 < rejections / 200 < 0.12

    def test_has_power_against_a_nonlinear_process(self):
        rejections = sum(
            tsay_test(lstar_process(400, seed=s), 2).p_value < 0.05 for s in range(20)
        )
        assert rejections >= 15

    def test_does_not_reject_a_long_linear_series(self):
        assert tsay_test(linear_ar(1000, seed=99), 2).p_value > 0.05

    def test_unavailable_when_too_short(self):
        result = tsay_test(linear_ar(20, seed=4), 12)
        assert not result.available
        assert result.statistic is None


class TestLSTLinearity:
    def test_rejects_for_an_lstar_process(self):
        assert lst_linearity(lstar_process(500, seed=5), order=1, delay=1).p_value < 0.01

    def test_does_not_reject_for_a_linear_process(self):
        assert lst_linearity(linear_ar(500, seed=6), order=1, delay=1).p_value > 0.05

    def test_reports_the_f_reference(self):
        result = lst_linearity(lstar_process(300, seed=7), 1, 1)
        assert result.reference.startswith("F(")
        assert result.tuning["variant"] == "third-order Taylor, F form"


class TestTerasvirtaSequence:
    def test_recovers_the_delay(self, config):
        for true_delay in (1, 2, 3):
            y = lstar_process(900, gamma=12.0, seed=10 + true_delay, delay=true_delay)
            spec = select_delay_and_type(y, order=3, frequency="M", config=config, series="SIM")
            assert spec.delay == true_delay, f"true delay {true_delay}, selected {spec.delay}"

    def test_identifies_lstar(self, config):
        spec = select_delay_and_type(lstar_process(900, gamma=12.0, seed=21),
                                     order=1, frequency="M", config=config)
        assert spec.linearity_rejected
        assert spec.kind == LSTAR

    def test_identifies_estar(self, config):
        spec = select_delay_and_type(estar_process(900, gamma=0.5, seed=22),
                                     order=1, frequency="M", config=config)
        assert spec.linearity_rejected
        assert spec.kind == ESTAR

    def test_all_candidate_delays_are_stored(self, config):
        spec = select_delay_and_type(lstar_process(400, seed=23), 1, "M", config)
        assert len(spec.delay_results) == len(config.get("nonlinearity.lst.delays.M"))
        row = spec.to_row()
        assert row["delay_p_values"].count(";") == len(spec.delay_results) - 1

    def test_sequence_results_are_recorded(self, config):
        spec = select_delay_and_type(lstar_process(400, seed=24), 1, "M", config)
        assert [r.name for r in spec.sequence_results] == ["H04", "H03", "H02"]

    def test_quarterly_delay_set(self, config):
        y = lstar_process(400, seed=25)
        spec = select_delay_and_type(y, 1, "Q", config)
        assert spec.delay in config.get("nonlinearity.lst.delays.Q")

    def test_specification_is_produced_even_when_linearity_is_not_rejected(self, config):
        # Part 5 §4.4: a non-rejection limits interpretation, it does not remove STAR
        # from the predeclared comparison, so a usable specification must still emerge.
        spec = select_delay_and_type(linear_ar(500, seed=26), 1, "M", config)
        assert not spec.linearity_rejected
        assert spec.kind in (LSTAR, ESTAR)
        assert spec.delay in config.get("nonlinearity.lst.delays.M")

    def test_selection_is_deterministic(self, config):
        y = lstar_process(500, seed=27)
        first = select_delay_and_type(y, 1, "M", config)
        second = select_delay_and_type(y, 1, "M", config)
        assert (first.delay, first.kind) == (second.delay, second.kind)
