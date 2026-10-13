"""Validation of the model estimators against data with known properties.

Each estimator is checked by recovering parameters from its own simulated process, and
where an independent implementation exists the results are cross-checked against it.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import pytest

from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR
from thesis.core.schemas import ReasonCode, Status
from thesis.models.arma import fit_arma
from thesis.models.arma_garch import fit_arma_garch
from thesis.models.flags import (
    apply_covariance_flags,
    apply_msar_flags,
    apply_star_flags,
    flag_extreme_forecast,
)
from thesis.models.msar import (
    _expanded_states,
    _expanded_transition,
    _filter,
    fit_msar,
)
from thesis.models.star import ESTAR, LSTAR, fit_star, transition
from thesis.models.var import fit_var


@pytest.fixture(scope="module")
def config():
    return load_config(config_dir=CONFIG_DIR)


def monthly(values, start="1960-01-01"):
    index = pd.date_range(start, periods=len(values), freq="MS")
    return pd.Series(np.asarray(values, dtype=float), index=index, name="SIM")


def simulate_msar(n, mu, phi, sigma, P, seed=0):
    rng = np.random.default_rng(seed)
    k, p = len(mu), len(phi)
    states = np.zeros(n, int)
    for t in range(1, n):
        states[t] = rng.choice(k, p=P[states[t - 1]])
    x = np.zeros(n)
    e = rng.standard_normal(n) * sigma
    for t in range(p, n):
        x[t] = phi @ x[t - p : t][::-1] + e[t]
    return monthly(np.asarray(mu)[states] + x)


def simulate_star(n, kind, gamma, c, phi, theta, sigma=1.0, seed=0, delay=1):
    rng = np.random.default_rng(seed)
    y = np.zeros(n)
    e = rng.standard_normal(n) * sigma
    scale = 1.0
    for t in range(2, n):
        x = np.array([1.0, y[t - 1]])
        g = float(transition(np.array([y[t - delay]]), gamma, c, scale, kind)[0])
        y[t] = x @ phi + g * (x @ theta) + e[t]
    return monthly(y)


class TestARMA:
    def test_recovers_a_simulated_arma_1_1(self):
        rng = np.random.default_rng(0)
        n = 800
        e = rng.standard_normal(n)
        y = np.zeros(n)
        for t in range(1, n):
            y[t] = 0.6 * y[t - 1] + e[t] + 0.4 * e[t - 1]
        fit = fit_arma(monthly(y), (1, 1))
        assert fit.record.converged
        assert fit.params["ar.L1"] == pytest.approx(0.6, abs=0.12)
        assert fit.params["ma.L1"] == pytest.approx(0.4, abs=0.12)

    def test_forecast_is_finite_and_sized(self):
        rng = np.random.default_rng(1)
        fit = fit_arma(monthly(rng.standard_normal(300)), (1, 1))
        prediction = fit.forecast(4)
        assert prediction.shape == (4,)
        assert np.isfinite(prediction).all()

    def test_pure_ar_selection_is_flagged(self):
        rng = np.random.default_rng(2)
        fit = fit_arma(monthly(rng.standard_normal(300)), (2, 0))
        assert fit.is_pure_ar
        assert fit.record.diagnostics["degenerate_arma"] == "pure AR"

    def test_pure_ma_is_flagged(self):
        rng = np.random.default_rng(3)
        fit = fit_arma(monthly(rng.standard_normal(300)), (0, 2))
        assert fit.is_pure_ma
        assert fit.record.diagnostics["degenerate_arma"] == "pure MA"


class TestMSAR:
    """The critical estimator: a bespoke Hamilton filter, so it is checked hard."""

    MU = [-1.5, 1.5]
    PHI = [0.5]
    SIGMA = 1.0
    P = np.array([[0.95, 0.05], [0.08, 0.92]])

    def test_loglikelihood_matches_statsmodels_at_identical_parameters(self):
        from statsmodels.tsa.regime_switching.markov_autoregression import (
            MarkovAutoregression,
        )

        y = simulate_msar(500, self.MU, self.PHI, self.SIGMA, self.P, seed=1)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            reference = MarkovAutoregression(
                y.to_numpy(), k_regimes=2, order=1, switching_ar=False, trend="c"
            )
            expected = reference.loglike(
                np.array([self.P[0, 0], self.P[1, 0], self.MU[0], self.MU[1],
                          self.SIGMA**2, self.PHI[0]])
            )
        states = _expanded_states(2, 1)
        actual, _, _ = _filter(
            y.to_numpy(), np.array(self.MU), np.array(self.PHI), self.SIGMA,
            self.P, states, _expanded_transition(self.P, states),
        )
        assert actual == pytest.approx(expected, abs=1e-8)

    @pytest.mark.slow
    def test_recovers_simulated_parameters(self):
        y = simulate_msar(600, self.MU, self.PHI, self.SIGMA, self.P, seed=1)
        fit = fit_msar(y, order=1, k_regimes=2)
        assert fit.record.converged
        assert fit.mu[0] == pytest.approx(self.MU[0], abs=0.4)
        assert fit.mu[1] == pytest.approx(self.MU[1], abs=0.4)
        assert fit.phi[0] == pytest.approx(self.PHI[0], abs=0.15)
        assert fit.sigma == pytest.approx(self.SIGMA, abs=0.2)
        assert fit.P[0, 0] == pytest.approx(self.P[0, 0], abs=0.08)

    @pytest.mark.slow
    def test_exact_forecast_matches_monte_carlo(self):
        y = simulate_msar(500, self.MU, self.PHI, self.SIGMA, self.P, seed=2)
        fit = fit_msar(y, order=1, k_regimes=2)
        rng = np.random.default_rng(7)
        draws = 40000
        probabilities = fit.filtered[-1]
        chosen = rng.choice(len(probabilities), size=draws, p=probabilities / probabilities.sum())
        for horizon in (1, 3):
            simulated = np.empty(draws)
            for d in range(draws):
                state = fit.states[chosen[d]]
                history = list(fit._y[-fit.order:][::-1] - fit.mu[list(state[: fit.order])])
                regime = state[0]
                for _ in range(horizon):
                    regime = rng.choice(fit.k_regimes, p=fit.P[regime])
                    nxt = float(fit.phi @ np.array(history[: fit.order])) + rng.standard_normal() * fit.sigma
                    history.insert(0, nxt)
                simulated[d] = history[0] + fit.mu[regime]
            assert fit.forecast(horizon)[-1] == pytest.approx(simulated.mean(), abs=0.05)

    @pytest.mark.slow
    def test_regimes_are_ordered_by_mean(self):
        y = simulate_msar(400, self.MU, self.PHI, self.SIGMA, self.P, seed=3)
        fit = fit_msar(y, order=1, k_regimes=2)
        assert list(fit.mu) == sorted(fit.mu)

    def test_transition_matrix_rows_sum_to_one(self):
        y = simulate_msar(200, self.MU, self.PHI, self.SIGMA, self.P, seed=4)
        fit = fit_msar(y, order=1, k_regimes=2, maxiter=20)
        np.testing.assert_allclose(fit.P.sum(axis=1), 1.0, atol=1e-10)

    def test_expanded_state_space_size(self):
        assert len(_expanded_states(2, 1)) == 4
        assert len(_expanded_states(3, 4)) == 243

    def test_expanded_transition_is_row_stochastic(self):
        states = _expanded_states(3, 2)
        P = np.array([[0.8, 0.1, 0.1], [0.1, 0.8, 0.1], [0.2, 0.2, 0.6]])
        T = _expanded_transition(P, states)
        np.testing.assert_allclose(T.sum(axis=1), 1.0)

    def test_smoothed_probabilities_sum_to_one(self):
        y = simulate_msar(200, self.MU, self.PHI, self.SIGMA, self.P, seed=5)
        fit = fit_msar(y, order=1, k_regimes=2, maxiter=20)
        np.testing.assert_allclose(fit.smoothed_regime.sum(axis=1), 1.0, atol=1e-8)


class TestSTAR:
    def test_transition_bounds(self):
        z = np.linspace(-5, 5, 101)
        for kind in (LSTAR, ESTAR):
            g = transition(z, gamma=5.0, c=0.0, scale=1.0, kind=kind)
            assert g.min() >= 0.0 and g.max() <= 1.0

    def test_logistic_is_monotone_and_half_at_the_threshold(self):
        z = np.linspace(-5, 5, 101)
        g = transition(z, gamma=5.0, c=0.0, scale=1.0, kind=LSTAR)
        assert np.all(np.diff(g) > 0)
        assert transition(np.array([0.0]), 5.0, 0.0, 1.0, LSTAR)[0] == pytest.approx(0.5)

    def test_exponential_is_symmetric_and_zero_at_the_threshold(self):
        assert transition(np.array([0.0]), 5.0, 0.0, 1.0, ESTAR)[0] == pytest.approx(0.0)
        left = transition(np.array([-2.0]), 5.0, 0.0, 1.0, ESTAR)[0]
        right = transition(np.array([2.0]), 5.0, 0.0, 1.0, ESTAR)[0]
        assert left == pytest.approx(right)

    def test_unknown_transition_rejected(self):
        with pytest.raises(ValueError):
            transition(np.array([0.0]), 1.0, 0.0, 1.0, "TANH")

    @pytest.mark.slow
    def test_recovers_a_simulated_lstar(self, config):
        y = simulate_star(1200, LSTAR, gamma=8.0, c=0.0,
                          phi=np.array([0.2, 0.5]), theta=np.array([-0.4, -0.9]), seed=4)
        fit = fit_star(y, order=1, delay=1, kind=LSTAR, config=config)
        assert fit.record.converged
        assert fit.G.min() >= 0.0 and fit.G.max() <= 1.0
        # The transition must actually move across the sample.
        assert fit.G.std() > 0.05
        assert fit.gamma > 0

    def test_fit_records_transition_diagnostics(self, config):
        y = simulate_star(400, LSTAR, 5.0, 0.0, np.array([0.1, 0.4]), np.array([0.0, -0.7]), seed=5)
        fit = fit_star(y, order=1, delay=1, kind=LSTAR, config=config)
        for key in ("G_min", "G_max", "G_sd", "transition_scale"):
            assert key in fit.record.diagnostics

    def test_one_step_forecast_matches_the_explicit_formula(self, config):
        y = simulate_star(400, LSTAR, 5.0, 0.0, np.array([0.1, 0.4]), np.array([0.0, -0.7]), seed=6)
        fit = fit_star(y, order=1, delay=1, kind=LSTAR, config=config)
        history = y.to_numpy()
        x = np.array([1.0, history[-1]])
        g = float(transition(np.array([history[-1]]), fit.gamma, fit.c, fit.scale, fit.kind)[0])
        assert fit.forecast_one(history) == pytest.approx(x @ fit.linear + g * (x @ fit.nonlinear))


class TestVAR:
    def test_matches_statsmodels(self):
        rng = np.random.default_rng(10)
        n = 400
        data = np.zeros((n, 2))
        A = np.array([[0.5, 0.1], [0.2, 0.4]])
        for t in range(1, n):
            data[t] = A @ data[t - 1] + rng.standard_normal(2) * 0.5
        frame = pd.DataFrame(data, columns=["a", "b"],
                             index=pd.date_range("1960-01-01", periods=n, freq="MS"))
        fit = fit_var(frame, order=1)
        from statsmodels.tsa.api import VAR as SMVAR

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            reference = SMVAR(frame).fit(1, trend="c")
        np.testing.assert_allclose(fit.coefficients[:, 0], reference.params.to_numpy()[0], atol=1e-8)
        np.testing.assert_allclose(
            fit.coefficients[:, 1:], reference.params.to_numpy()[1:].T, atol=1e-8
        )

    def test_stability_is_checked(self):
        rng = np.random.default_rng(11)
        n = 300
        data = np.cumsum(rng.standard_normal((n, 2)), axis=0) * 10
        frame = pd.DataFrame(data, columns=["a", "b"],
                             index=pd.date_range("1960-01-01", periods=n, freq="MS"))
        fit = fit_var(frame, order=1)
        if not fit.is_stable:
            assert ReasonCode.UNSTABLE_AR in fit.record.reason_codes
            assert fit.record.status is Status.FAILED

    def test_forecast_shape_and_recursion(self):
        rng = np.random.default_rng(12)
        n = 300
        data = np.zeros((n, 2))
        for t in range(1, n):
            data[t] = np.array([[0.5, 0.0], [0.0, 0.3]]) @ data[t - 1] + rng.standard_normal(2)
        frame = pd.DataFrame(data, columns=["a", "b"],
                             index=pd.date_range("1960-01-01", periods=n, freq="MS"))
        fit = fit_var(frame, order=1)
        prediction = fit.forecast(frame.to_numpy(), horizon=3)
        assert prediction.shape == (3, 2)
        assert np.isfinite(prediction).all()


class TestARMAGARCH:
    @pytest.mark.slow
    def test_recovers_garch_persistence(self):
        rng = np.random.default_rng(20)
        n = 1500
        omega, alpha, beta = 0.05, 0.1, 0.85
        h = np.zeros(n)
        e = np.zeros(n)
        h[0] = omega / (1 - alpha - beta)
        for t in range(1, n):
            h[t] = omega + alpha * e[t - 1] ** 2 + beta * h[t - 1]
            e[t] = rng.standard_normal() * np.sqrt(h[t])
        y = np.zeros(n)
        for t in range(1, n):
            y[t] = 0.3 * y[t - 1] + e[t]
        fit = fit_arma_garch(monthly(y), order=(1, 0))
        assert fit.record.converged
        assert fit.persistence == pytest.approx(alpha + beta, abs=0.15)
        assert 0 < fit.persistence < 1

    def test_standardized_residuals_have_unit_scale(self):
        rng = np.random.default_rng(21)
        fit = fit_arma_garch(monthly(rng.standard_normal(500)), order=(1, 0))
        assert np.std(fit.standardized_residuals) == pytest.approx(1.0, abs=0.35)

    def test_mean_forecast_is_finite(self):
        rng = np.random.default_rng(22)
        fit = fit_arma_garch(monthly(rng.standard_normal(400)), order=(1, 1))
        assert np.isfinite(fit.forecast_mean(3)).all()


class TestFlags:
    def _record(self):
        from thesis.core.schemas import FitRecord

        return FitRecord(series="X", model="MSAR2", spec_label="", spec_hash="",
                         window_start="", window_end="", refit_date="", converged=True)

    def test_low_occupancy_is_fragile_not_failed(self, config):
        class Fit:
            occupancy = np.array([0.98, 0.02])
            smoothed_regime = np.zeros((300, 2))
            P = np.array([[0.9, 0.1], [0.1, 0.9]])

        record = apply_msar_flags(self._record(), Fit(), config)
        assert ReasonCode.LOW_OCCUPANCY in record.reason_codes
        assert record.status is Status.FRAGILE          # not FAILED

    def test_zero_occupancy_is_failure(self, config):
        class Fit:
            occupancy = np.array([1.0, 0.0])
            smoothed_regime = np.zeros((300, 2))
            P = np.array([[0.9, 0.1], [0.1, 0.9]])

        record = apply_msar_flags(self._record(), Fit(), config)
        assert ReasonCode.EMPTY_REGIME in record.reason_codes
        assert record.status is Status.FAILED

    def test_boundary_transition_is_fragile(self, config):
        class Fit:
            occupancy = np.array([0.5, 0.5])
            smoothed_regime = np.zeros((300, 2))
            P = np.array([[0.999, 0.001], [0.1, 0.9]])

        record = apply_msar_flags(self._record(), Fit(), config)
        assert ReasonCode.TRANSITION_BOUNDARY in record.reason_codes
        assert record.status is Status.FRAGILE

    def test_gamma_at_the_optimizer_bound_is_fragile(self, config):
        class Fit:
            gamma = 1000.0
            c = 0.0
            G = np.linspace(0, 1, 100)
            y = np.linspace(-3, 3, 100)

        record = apply_star_flags(self._record(), Fit(), config)
        assert ReasonCode.STAR_GAMMA_BOUND in record.reason_codes

    def test_near_constant_transition_is_fragile(self, config):
        class Fit:
            gamma = 5.0
            c = 0.0
            G = np.full(100, 0.5)
            y = np.linspace(-3, 3, 100)

        record = apply_star_flags(self._record(), Fit(), config)
        assert ReasonCode.NEAR_CONSTANT_TRANSITION in record.reason_codes

    def test_threshold_outside_the_percentile_range_is_fragile(self, config):
        class Fit:
            gamma = 5.0
            c = 99.0
            G = np.linspace(0, 1, 100)
            y = np.linspace(-3, 3, 100)

        record = apply_star_flags(self._record(), Fit(), config)
        assert ReasonCode.STAR_THRESHOLD_EXTREME in record.reason_codes

    def test_singular_covariance_is_failure(self, config):
        record = apply_covariance_flags(self._record(), np.array([[1.0, 1.0], [1.0, 1.0]]), config)
        assert ReasonCode.SINGULAR_COV in record.reason_codes
        assert record.status is Status.FAILED

    def test_extreme_forecast_is_a_warning_only(self, config):
        record = self._record()
        window = np.random.default_rng(0).standard_normal(240)
        flagged = flag_extreme_forecast(record, forecast=100.0, window=window, config=config)
        assert flagged
        assert ReasonCode.EXTREME_FORECAST in record.reason_codes
        assert record.status is Status.FRAGILE      # never FAILED, never deleted

    def test_non_finite_forecast_is_failure(self, config):
        record = self._record()
        window = np.random.default_rng(0).standard_normal(240)
        flag_extreme_forecast(record, forecast=np.inf, window=window, config=config)
        assert record.status is Status.FAILED
