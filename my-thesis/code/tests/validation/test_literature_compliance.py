"""Compliance of the nonlinear econometrics with the papers it claims to implement.

Each test names the paper and the equation or section it checks. Where a published
numerical example is reproducible it is used; where it is not, the check is against an
independent implementation (statsmodels), an analytical identity, or Monte Carlo.

References
----------
Hamilton, J. D. (1989). "A New Approach to the Economic Analysis of Nonstationary Time
    Series and the Business Cycle." Econometrica 57(2), 357-384.
Luukkonen, R., Saikkonen, P. & Teräsvirta, T. (1988). "Testing Linearity in Univariate
    Time Series Models." Scandinavian Journal of Statistics 15(3), 161-175.
Teräsvirta, T. (1994). "Specification, Estimation, and Evaluation of Smooth Transition
    Autoregressive Models." JASA 89(425), 208-218.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import pytest

from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR
from thesis.core.schemas import ReasonCode, Status
from thesis.diagnostics.nonlinearity import (_f_test, _lst_auxiliary, _ols_residuals,
                                             lst_linearity, select_delay_and_type,
                                             tsay_test)
from thesis.models import flags
from thesis.models.msar import (_expanded_states, _expanded_transition, _filter,
                                _stationary, fit_msar)
from thesis.models.optimize import StartAttempt, select_best
from thesis.models.star import fit_star, transition


@pytest.fixture(scope="module")
def config():
    return load_config(names=("baseline", "series_catalog", "thresholds"),
                       config_dir=CONFIG_DIR)


def _ar_series(n: int, coefficients, seed: int, sigma: float = 1.0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    p = len(coefficients)
    y = np.zeros(n + 200)
    for t in range(p, n + 200):
        y[t] = sum(c * y[t - j - 1] for j, c in enumerate(coefficients)) + rng.normal(0, sigma)
    return y[200:]


# =====================================================================================
# Teräsvirta (1994) section 3: the LM-type linearity tests
# =====================================================================================


class TestTerasvirtaAuxiliaryRegression:
    """Equations (3.10)-(3.12): the artificial regression and its null (3.11)."""

    @pytest.mark.parametrize("order,delay", [(1, 1), (2, 1), (2, 2), (3, 2), (4, 1),
                                             (1, 4), (2, 5), (3, 6)])
    def test_each_block_has_exactly_p_columns(self, order, delay):
        # (3.12): y_t = g0 + g1'w_t + g2'(w_t y_{t-d}) + g3'(w_t y²_{t-d})
        #              + g4'(w_t y³_{t-d}), with each g_j a p-vector.
        y = _ar_series(400, [0.4], seed=order * 10 + delay)
        _, X, blocks = _lst_auxiliary(y, order, delay)
        assert X.shape[1] == order + 1, "the linear part is (1, w_t)"
        assert [b.shape[1] for b in blocks] == [order] * 3

    @pytest.mark.parametrize("order,delay", [(1, 1), (2, 1), (2, 2), (3, 3), (4, 2),
                                             (1, 4), (2, 6), (3, 5)])
    def test_the_null_imposes_exactly_three_p_restrictions(self, order, delay):
        # (3.11): H0: beta_2j = beta_3j = beta_4j = 0, j = 1..p, so LM is chi²(3p).
        y = _ar_series(500, [0.3, 0.2][:max(order, 1)], seed=order * 7 + delay)
        _, X, blocks = _lst_auxiliary(y, order, delay)
        full = np.column_stack([X] + list(blocks))
        restrictions = (int(np.linalg.matrix_rank(full))
                        - int(np.linalg.matrix_rank(X)))
        assert restrictions == 3 * order

    @pytest.mark.parametrize("order,delay", [(1, 1), (2, 2), (3, 1), (4, 4), (2, 5)])
    def test_the_auxiliary_design_is_of_full_column_rank(self, order, delay):
        # The defect this replaced multiplied the intercept by the powers of the
        # transition variable, which duplicates existing columns whenever d <= p.
        y = _ar_series(500, [0.3], seed=99 + order + delay)
        _, X, blocks = _lst_auxiliary(y, order, delay)
        full = np.column_stack([X] + list(blocks))
        assert np.linalg.matrix_rank(full) == full.shape[1]

    def test_the_restriction_count_no_longer_depends_on_whether_the_delay_exceeds_p(self):
        # Teräsvirta states chi²(3p) with no dependence on d, and applies the test at
        # delays well beyond p (his Table 3 runs d = 1..9 for an AR(2)). Comparing
        # p values across the delay grid is only meaningful if the reference
        # distribution is the same at every delay.
        y = _ar_series(600, [0.3, 0.2], seed=5)
        references = set()
        for delay in range(1, 7):
            result = lst_linearity(pd.Series(y), 2, delay)
            references.add(result.reference.split(",")[0])
        assert len(references) == 1, f"reference distribution varies with delay: {references}"

    def test_the_f_test_uses_ranks_not_column_counts(self):
        # A deliberately collinear design: the F must be referred to the distribution
        # implied by the rank, not by the number of columns.
        y = _ar_series(300, [0.5], seed=3)
        dependent, X, blocks = _lst_auxiliary(y, 2, 1)
        full = np.column_stack([X] + list(blocks))
        padded = np.column_stack([full, full[:, -1]])          # exact duplicate column
        statistic_full, p_full, q_full, df_full = _f_test(dependent, X, full)
        statistic_pad, p_pad, q_pad, df_pad = _f_test(dependent, X, padded)
        assert (q_full, df_full) == (q_pad, df_pad)
        assert statistic_full == pytest.approx(statistic_pad, rel=1e-10)
        assert p_full == pytest.approx(p_pad, rel=1e-10)


class TestTerasvirtaFStatisticAgainstAnIndependentComputation:
    """The F is recomputed from first principles and from statsmodels."""

    def test_matches_an_explicit_ssr_based_f(self):
        y = _ar_series(400, [0.4, -0.2], seed=11)
        dependent, X, blocks = _lst_auxiliary(y, 2, 1)
        full = np.column_stack([X] + list(blocks))
        statistic, p_value, q, df = _f_test(dependent, X, full)

        e0 = _ols_residuals(dependent, X)
        e1 = _ols_residuals(dependent, full)
        ssr0, ssr1 = float(e0 @ e0), float(e1 @ e1)
        expected = ((ssr0 - ssr1) / (3 * 2)) / (ssr1 / (dependent.size - full.shape[1]))
        assert statistic == pytest.approx(expected, rel=1e-12)
        assert q == 6 and df == dependent.size - full.shape[1]

    def test_matches_the_statsmodels_wald_f_for_the_same_restrictions(self):
        import statsmodels.api as sm

        y = _ar_series(400, [0.4, -0.2], seed=12)
        dependent, X, blocks = _lst_auxiliary(y, 2, 1)
        full = np.column_stack([X] + list(blocks))
        statistic, p_value, q, df = _f_test(dependent, X, full)

        fitted = sm.OLS(dependent, full).fit()
        restriction = np.zeros((3 * 2, full.shape[1]))
        for row, column in enumerate(range(X.shape[1], full.shape[1])):
            restriction[row, column] = 1.0
        wald = fitted.f_test(restriction)
        assert statistic == pytest.approx(float(np.asarray(wald.fvalue).ravel()[0]), rel=1e-8)
        assert p_value == pytest.approx(float(np.asarray(wald.pvalue).ravel()[0]), rel=1e-6)

    def test_size_is_near_nominal_under_a_linear_null(self):
        rejections = 0
        trials = 300
        for seed in range(trials):
            y = _ar_series(250, [0.5, -0.25], seed=20_000 + seed)
            result = lst_linearity(pd.Series(y), 2, 1)
            if result.p_value is not None and result.p_value < 0.05:
                rejections += 1
        rate = rejections / trials
        # Binomial(300, .05) has sd .0126; a correctly sized test lands well inside this.
        assert 0.02 <= rate <= 0.10, f"empirical size {rate:.3f}"

    def test_has_power_against_an_lstar_alternative(self):
        rejections = 0
        trials = 60
        for seed in range(trials):
            rng = np.random.default_rng(700 + seed)
            n = 300
            y = np.zeros(n)
            for t in range(2, n):
                g = 1.0 / (1.0 + np.exp(-5.0 * (y[t - 1] - 0.0)))
                y[t] = 0.7 * y[t - 1] - 1.3 * g * y[t - 1] + rng.normal(0, 1.0)
            result = lst_linearity(pd.Series(y), 2, 1)
            if result.p_value is not None and result.p_value < 0.05:
                rejections += 1
        assert rejections / trials > 0.5


class TestTerasvirtaNestedSequence:
    """Section 4.3, equations (4.3)-(4.5), and the minimum-p-value decision rule."""

    def test_each_nested_test_imposes_p_restrictions(self, config):
        y = _ar_series(500, [0.4, -0.2], seed=31)
        spec = select_delay_and_type(pd.Series(y), 2, "M", config)
        for result in spec.sequence_results:
            assert result.reference.startswith("F(2,"), result.reference

    def test_the_sequence_is_properly_nested(self):
        # H01: g4 = 0 within the full model; H02: g3 = 0 given g4 = 0; H03: g2 = 0 given
        # g3 = g4 = 0. Each unrestricted model is the previous restricted one.
        y = _ar_series(400, [0.4], seed=32)
        dependent, X, blocks = _lst_auxiliary(y, 1, 1)
        first, second, third = blocks
        levels = [X,
                  np.column_stack([X, first]),
                  np.column_stack([X, first, second]),
                  np.column_stack([X, first, second, third])]
        for lower, higher in zip(levels, levels[1:]):
            assert higher.shape[1] > lower.shape[1]
            np.testing.assert_allclose(higher[:, : lower.shape[1]], lower)

    def test_estar_is_chosen_when_the_middle_test_is_strongest(self, config):
        # Teräsvirta's rule: "If the p value of F_3 (the test of H_02) is the smallest of
        # the three, select an ESTAR model; if not, choose a LSTAR model."
        rng = np.random.default_rng(55)
        n = 700
        y = np.zeros(n)
        for t in range(2, n):
            g = 1.0 - np.exp(-3.0 * (y[t - 1] ** 2))
            y[t] = 0.8 * y[t - 1] - 1.5 * g * y[t - 1] + rng.normal(0, 1.0)
        spec = select_delay_and_type(pd.Series(y), 1, "M", config, series="estar")
        p_values = {r.name: r.p_value for r in spec.sequence_results}
        if p_values["H03"] is not None and all(v is not None for v in p_values.values()):
            smallest = min(p_values, key=lambda k: p_values[k])
            assert (spec.kind == "ESTAR") == (smallest == "H03")

    def test_the_delay_minimising_the_linearity_p_value_is_selected(self, config):
        # Section 4.2: "I choose the delay parameter d such that p(d) = min_d p(d)."
        y = _ar_series(500, [0.4, -0.2], seed=33)
        spec = select_delay_and_type(pd.Series(y), 2, "M", config)
        usable = {int(r.tuning["delay"]): r.p_value
                  for r in spec.delay_results if r.p_value is not None}
        assert spec.delay == min(usable, key=lambda d: (usable[d], d))


# =====================================================================================
# Luukkonen, Saikkonen & Teräsvirta (1988) section 2.5: the general linearity test
# =====================================================================================


class TestLuukkonenGeneralLinearityTest:
    @pytest.mark.parametrize("order", [1, 2, 3, 4, 6])
    def test_the_statistic_uses_the_p_p_plus_one_over_two_unique_products(self, order):
        # Section 2.5: the LM test of H04 in (2.12) uses z_1t = [y²_{t-1}, y_{t-1}y_{t-2},
        # ..., y²_{t-p}]' and is asymptotically chi²_{p(p+1)/2}.
        y = _ar_series(500, [0.4], seed=40 + order)
        result = tsay_test(pd.Series(y), order)
        expected = order * (order + 1) // 2
        assert result.tuning["n_quadratic_terms"] == expected
        assert result.reference.startswith(f"F({expected},")

    def test_for_p_equals_one_there_is_a_single_quadratic_term(self):
        # "When p = 1, Tsay's statistic F_2 is identical to Keenan's F_1."
        y = _ar_series(400, [0.5], seed=41)
        result = tsay_test(pd.Series(y), 1)
        assert result.tuning["n_quadratic_terms"] == 1
        assert result.reference.startswith("F(1,")

    def test_the_f_form_is_the_finite_sample_approximation_the_paper_describes(self):
        # Keenan "suggests an F distribution as an approximation in finite samples";
        # the implementation records which variant it reports.
        y = _ar_series(400, [0.5], seed=42)
        result = tsay_test(pd.Series(y), 2)
        assert "F(" in result.reference
        assert result.tuning["variant"].startswith("quadratic")

    def test_failure_to_reject_is_not_reported_as_evidence_of_linearity(self):
        # Section 3: against some alternatives an incorrect LM test has local power no
        # higher than its size, so "do not reject" cannot mean "the process is linear".
        y = _ar_series(400, [0.5], seed=43)
        result = tsay_test(pd.Series(y), 2)
        if result.decision_5pct == "do not reject":
            text = result.implication.lower()
            assert "no general evidence against" in text
            assert "linear" in text
            assert "is linear" not in text.replace("evidence against linear", "")


# =====================================================================================
# Hamilton (1989) section 4: filtering, likelihood, smoothing, estimation
# =====================================================================================


class TestHamiltonFilter:
    MU = [-1.2, 1.4]
    PHI = [0.5, -0.2]
    SIGMA = 0.9
    P = np.array([[0.93, 0.07], [0.10, 0.90]])

    def _simulate(self, n: int, seed: int) -> np.ndarray:
        rng = np.random.default_rng(seed)
        mu, phi, P = np.array(self.MU), np.array(self.PHI), self.P
        order = len(phi)
        states = np.zeros(n, dtype=int)
        for t in range(1, n):
            states[t] = rng.choice(2, p=P[states[t - 1]])
        y = np.zeros(n)
        for t in range(order, n):
            adjusted = sum(phi[j] * (y[t - j - 1] - mu[states[t - j - 1]])
                           for j in range(order))
            y[t] = mu[states[t]] + adjusted + rng.normal(0, self.SIGMA)
        return y

    @pytest.mark.parametrize("order", [1, 2, 3])
    def test_loglikelihood_matches_statsmodels_at_identical_parameters(self, order):
        # Independent implementation, at higher autoregressive orders than the original
        # two-regime AR(1) check.
        from statsmodels.tsa.regime_switching.markov_autoregression import (
            MarkovAutoregression,
        )

        phi = [0.5, -0.2, 0.1][:order]
        rng = np.random.default_rng(300 + order)
        n = 400
        states = np.zeros(n, dtype=int)
        for t in range(1, n):
            states[t] = rng.choice(2, p=self.P[states[t - 1]])
        y = np.zeros(n)
        for t in range(order, n):
            adjusted = sum(phi[j] * (y[t - j - 1] - self.MU[states[t - j - 1]])
                           for j in range(order))
            y[t] = self.MU[states[t]] + adjusted + rng.normal(0, self.SIGMA)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            reference = MarkovAutoregression(y, k_regimes=2, order=order,
                                             switching_ar=False, trend="c")
            expected = reference.loglike(np.array(
                [self.P[0, 0], self.P[1, 0], self.MU[0], self.MU[1],
                 self.SIGMA ** 2, *phi]))
        states_list = _expanded_states(2, order)
        actual, _, _ = _filter(y, np.array(self.MU), np.array(phi), self.SIGMA,
                               self.P, states_list,
                               _expanded_transition(self.P, states_list))
        assert actual == pytest.approx(expected, abs=1e-8)

    def test_filtered_probabilities_are_a_distribution_at_every_date(self):
        y = self._simulate(300, seed=4)
        states = _expanded_states(2, 2)
        _, filtered, _ = _filter(y, np.array(self.MU), np.array(self.PHI), self.SIGMA,
                                 self.P, states, _expanded_transition(self.P, states))
        assert (filtered >= 0).all()
        np.testing.assert_allclose(filtered.sum(axis=1), 1.0, atol=1e-12)

    def test_smoothed_regime_probabilities_are_a_distribution(self, config):
        y = pd.Series(self._simulate(300, seed=5))
        fit = fit_msar(y, order=1, k_regimes=2, config=config)
        assert (fit.smoothed_regime >= -1e-12).all()
        np.testing.assert_allclose(fit.smoothed_regime.sum(axis=1), 1.0, atol=1e-10)

    def test_the_filter_starts_from_the_ergodic_distribution(self):
        # Section 4.2: the filter is started from the unconditional probability of the
        # expanded state, built from the limiting probability pi of (2.7).
        states = _expanded_states(2, 1)
        T = _expanded_transition(self.P, states)
        initial = _stationary(T)
        np.testing.assert_allclose(initial @ T, initial, atol=1e-10)
        assert initial.sum() == pytest.approx(1.0)
        # The implied marginal matches pi = (1-q)/(2-p-q) from (2.7).
        marginal = np.zeros(2)
        for i, state in enumerate(states):
            marginal[state[0]] += initial[i]
        p11, p22 = self.P[0, 0], self.P[1, 1]
        expected_first = (1 - p22) / (2 - p11 - p22)
        assert marginal[0] == pytest.approx(expected_first, abs=1e-10)

    def test_expected_durations_follow_hamiltons_identity(self, config):
        # Section 6: the expected duration of a regime is (1 - p_ii)^-1.
        y = pd.Series(self._simulate(400, seed=6))
        fit = fit_msar(y, order=1, k_regimes=2, config=config)
        for regime in range(fit.k_regimes):
            expected = 1.0 / (1.0 - fit.P[regime, regime])
            assert fit.expected_duration[regime] == pytest.approx(expected, rel=1e-9)

    def test_regimes_are_ordered_by_mean(self, config):
        y = pd.Series(self._simulate(400, seed=7))
        fit = fit_msar(y, order=1, k_regimes=2, config=config)
        assert list(fit.mu) == sorted(fit.mu)


class TestHamiltonNumericalStability:
    """The log-domain rescaling of the conditional density."""

    def _direct(self, y, mu, phi, sigma, P, states, T):
        """The previous linear-domain filter, kept here as the comparison baseline."""
        from thesis.models.msar import _state_constants, _stationary as stationary

        order = len(phi)
        probabilities = stationary(T)
        loglik = 0.0
        variance = sigma ** 2
        normalizer = np.sqrt(2 * np.pi * variance)
        constants = _state_constants(np.asarray(mu, float), np.asarray(phi, float), states)
        for t in range(order, y.size):
            ar = float(phi @ y[t - order:t][::-1]) if order else 0.0
            predicted = probabilities @ T
            density = np.exp(-0.5 * ((y[t] - (constants + ar)) ** 2) / variance) / normalizer
            joint = predicted * density
            total = joint.sum()
            if not np.isfinite(total) or total <= 0:
                return -np.inf
            loglik += float(np.log(total))
            probabilities = joint / total
        return loglik

    def test_equivalent_to_the_direct_form_on_well_behaved_data(self):
        rng = np.random.default_rng(8)
        y = rng.normal(0, 1, 400)
        mu, phi, P = np.array([-1.0, 1.0]), np.array([0.4]), np.array([[0.9, 0.1], [0.1, 0.9]])
        states = _expanded_states(2, 1)
        T = _expanded_transition(P, states)
        new, _, _ = _filter(y, mu, phi, 1.0, P, states, T)
        old = self._direct(y, mu, phi, 1.0, P, states, T)
        assert new == pytest.approx(old, rel=1e-12)

    def test_survives_an_outlier_that_underflows_the_direct_form(self):
        rng = np.random.default_rng(9)
        y = rng.normal(0, 1, 300)
        y[150] = 60.0                       # far from every state's conditional mean
        mu, phi, P = np.array([-1.0, 2.0]), np.array([0.5]), np.array([[0.9, 0.1], [0.2, 0.8]])
        states = _expanded_states(2, 1)
        T = _expanded_transition(P, states)
        stable, _, _ = _filter(y, mu, phi, 0.8, P, states, T)
        direct = self._direct(y, mu, phi, 0.8, P, states, T)
        assert np.isfinite(stable), "the rescaled filter must stay finite"
        assert not np.isfinite(direct), "the direct form is expected to underflow here"

    def test_survives_a_small_innovation_variance(self):
        rng = np.random.default_rng(10)
        y = rng.normal(0, 1, 250)
        mu, phi, P = np.array([-1.0, 1.0]), np.array([0.3]), np.array([[0.9, 0.1], [0.1, 0.9]])
        states = _expanded_states(2, 1)
        T = _expanded_transition(P, states)
        assert np.isfinite(_filter(y, mu, phi, 0.05, P, states, T)[0])


@pytest.fixture(scope="module")
def fitted(config):
    """A converged two-regime fit used for the standard-error checks."""
    rng = np.random.default_rng(12)
    n = 500
    P = np.array([[0.94, 0.06], [0.09, 0.91]])
    states = np.zeros(n, dtype=int)
    for t in range(1, n):
        states[t] = rng.choice(2, p=P[states[t - 1]])
    mu = np.array([-1.0, 1.5])
    y = np.zeros(n)
    for t in range(1, n):
        y[t] = mu[states[t]] + 0.5 * (y[t - 1] - mu[states[t - 1]]) + rng.normal(0, 0.8)
    return fit_msar(pd.Series(y), order=1, k_regimes=2, config=config)


class TestHamiltonParameterUncertainty:
    """Table I and footnote 7: asymptotic standard errors from numerical second
    derivatives of the log likelihood."""

    def test_standard_errors_are_reported_for_every_natural_parameter(self, fitted):
        assert fitted.record.std_errors
        for name in fitted.record.params:
            assert name in fitted.record.std_errors, name

    def test_standard_errors_are_positive_and_finite(self, fitted):
        values = np.array(list(fitted.record.std_errors.values()))
        assert np.isfinite(values).all()
        assert (values > 0).all()

    def test_transition_probabilities_in_a_row_share_a_standard_error(self, fitted):
        # With two regimes p_i1 + p_i2 = 1, so the two have identical variance.
        assert fitted.record.std_errors["p11"] == pytest.approx(
            fitted.record.std_errors["p12"], rel=1e-6)

    def test_the_covariance_matrix_is_symmetric_and_positive_definite(self, fitted):
        covariance = fitted.covariance
        assert covariance.size
        np.testing.assert_allclose(covariance, covariance.T, atol=1e-8)
        assert np.linalg.eigvalsh((covariance + covariance.T) / 2).min() > 0

    def test_the_estimates_lie_within_a_few_standard_errors_of_the_truth(self, fitted):
        # A coarse but genuine check that the reported uncertainty has the right scale.
        for name, truth in (("mu1", -1.0), ("mu2", 1.5), ("phi1", 0.5), ("sigma", 0.8)):
            error = abs(fitted.record.params[name] - truth)
            assert error < 5 * fitted.record.std_errors[name], name

    def test_covariance_status_is_recorded(self, fitted):
        assert fitted.record.diagnostics["covariance_status"] == "ok"


class TestConvergenceSelection:
    """The multistart rule shared by both nonlinear estimators."""

    def test_a_converged_start_is_preferred_over_a_lower_unconverged_one(self):
        attempts = [
            StartAttempt("a", objective=10.0, converged=True, message="ok", x=np.array([1.0])),
            StartAttempt("b", objective=1.0, converged=False, message="maxiter",
                         x=np.array([2.0])),
        ]
        outcome = select_best(attempts)
        assert outcome.chosen.label == "a"
        assert not outcome.used_unconverged
        assert "reported convergence" in outcome.selection_rule

    def test_the_lowest_objective_wins_among_converged_starts(self):
        attempts = [
            StartAttempt("a", 10.0, True, "ok", np.array([1.0])),
            StartAttempt("b", 2.0, True, "ok", np.array([2.0])),
        ]
        assert select_best(attempts).chosen.label == "b"

    def test_an_unconverged_start_is_used_only_when_nothing_converged(self):
        attempts = [
            StartAttempt("a", 10.0, False, "maxiter", np.array([1.0])),
            StartAttempt("b", 2.0, False, "maxiter", np.array([2.0])),
        ]
        outcome = select_best(attempts)
        assert outcome.chosen.label == "b"
        assert outcome.used_unconverged
        assert "none reported convergence" in outcome.selection_rule

    def test_nonfinite_objectives_are_inadmissible(self):
        attempts = [
            StartAttempt("a", float("inf"), True, "ok", np.array([1.0])),
            StartAttempt("b", float("nan"), True, "ok", np.array([2.0])),
        ]
        assert select_best(attempts).chosen is None

    def test_a_start_that_raised_is_recorded_rather_than_dropped(self):
        attempts = [StartAttempt("boom", float("inf"), False, "ValueError()", None)]
        outcome = select_best(attempts)
        assert outcome.chosen is None
        assert outcome.summary()["n_starts"] == 1

    def test_every_attempt_is_preserved_in_the_fit_record(self, config):
        rng = np.random.default_rng(13)
        y = pd.Series(rng.normal(0, 1, 200))
        fit = fit_msar(y, order=1, k_regimes=2, config=config)
        diagnostics = fit.record.diagnostics
        assert diagnostics["n_starts"] >= 2
        assert "starts" in diagnostics
        assert diagnostics["n_converged"] <= diagnostics["n_starts"]


# =====================================================================================
# Teräsvirta (1994) section 5: estimation and evaluation
# =====================================================================================


class TestStarEstimation:
    def test_the_lstar_exponent_is_divided_by_the_transition_standard_deviation(self):
        # Section 5: "it is natural to divide the exponent by sigma-hat(y)".
        z = np.linspace(-3, 3, 101)
        scale = 2.0
        direct = 1.0 / (1.0 + np.exp(-1.5 * (z - 0.25) / scale))
        np.testing.assert_allclose(transition(z, 1.5, 0.25, scale, "LSTAR"), direct, atol=1e-12)

    def test_the_estar_exponent_is_divided_by_the_transition_variance(self):
        # Section 5: "standardize the exponent of F by dividing it by sigma-hat²(y)".
        z = np.linspace(-3, 3, 101)
        scale = 2.0
        direct = 1.0 - np.exp(-1.5 * (z - 0.25) ** 2 / scale ** 2)
        np.testing.assert_allclose(transition(z, 1.5, 0.25, scale, "ESTAR"), direct, atol=1e-12)

    def test_the_transition_function_stays_within_the_unit_interval(self):
        z = np.linspace(-50, 50, 501)
        for kind in ("LSTAR", "ESTAR"):
            for gamma in (0.001, 1.0, 1000.0):
                g = transition(z, gamma, 0.0, 1.0, kind)
                assert g.min() >= 0.0 and g.max() <= 1.0

    def test_concentrating_the_linear_coefficients_reproduces_the_joint_minimum(self, config):
        # The concentrated objective must equal the full least-squares objective at the
        # same (gamma, c), which is what makes conditional least squares exact.
        from thesis.models.star import _design, _sse

        rng = np.random.default_rng(14)
        n = 300
        y = np.zeros(n)
        for t in range(1, n):
            g = 1.0 / (1.0 + np.exp(-3.0 * y[t - 1]))
            y[t] = 0.6 * y[t - 1] - 1.0 * g * y[t - 1] + rng.normal(0, 1.0)
        series = pd.Series(y)
        dep, X, z = _design(y, 1, 1)
        scale = float(np.std(z, ddof=1))
        gamma, c = 2.0, 0.1
        sse, coef, g = _sse(np.array([gamma, c]), dep, X, z, scale, "LSTAR")
        design = np.column_stack([X, X * g[:, None]])
        explicit, *_ = np.linalg.lstsq(design, dep, rcond=None)
        np.testing.assert_allclose(coef, explicit, atol=1e-10)
        residuals = dep - design @ explicit
        assert sse == pytest.approx(float(residuals @ residuals), rel=1e-12)

    @pytest.mark.slow
    def test_recovers_lstar_threshold_and_coefficients(self, config):
        rng = np.random.default_rng(15)
        n = 1200
        y = np.zeros(n)
        for t in range(1, n):
            g = 1.0 / (1.0 + np.exp(-4.0 * (y[t - 1] - 0.4)))
            y[t] = 0.7 * y[t - 1] - 1.4 * g * y[t - 1] + rng.normal(0, 1.0)
        fit = fit_star(pd.Series(y), 1, 1, "LSTAR", config, series="recovery")
        assert fit.record.converged
        assert fit.c == pytest.approx(0.4, abs=0.6)
        assert fit.gamma > 0

    @pytest.mark.slow
    def test_recovers_an_estar_transition(self, config):
        rng = np.random.default_rng(16)
        n = 1200
        y = np.zeros(n)
        for t in range(1, n):
            g = 1.0 - np.exp(-0.5 * (y[t - 1] - 0.0) ** 2)
            y[t] = 0.8 * y[t - 1] - 1.5 * g * y[t - 1] + rng.normal(0, 1.0)
        fit = fit_star(pd.Series(y), 1, 1, "ESTAR", config, series="recovery")
        assert fit.record.converged
        assert abs(fit.c) < 1.0
        assert fit.G.std() > 0.01, "the fitted transition must actually vary"


@pytest.fixture(scope="module")
def star_fit(config):
    """A STAR fit with delay 3, so the transition variable differs from the dependent."""
    rng = np.random.default_rng(17)
    n = 600
    y = np.zeros(n)
    for t in range(3, n):
        g = 1.0 / (1.0 + np.exp(-3.0 * (y[t - 3] - 0.2)))
        y[t] = 0.6 * y[t - 1] - 1.1 * g * y[t - 1] + rng.normal(0, 1.0)
    return fit_star(pd.Series(y), 2, 3, "LSTAR", config, series="cred")


class TestStarCredibilityDiagnostics:
    """Part 5 §8.2, informed by Teräsvirta (1994) §5."""

    def test_the_transition_variable_is_kept_on_the_fit(self, star_fit):
        assert star_fit.z.size == star_fit.y.size
        assert star_fit.z.size == star_fit.G.size

    def test_the_transition_variable_is_the_delayed_series_not_the_dependent(self, star_fit):
        # With d = 3 the two differ, which is exactly when the old check went wrong.
        assert not np.allclose(star_fit.z, star_fit.y)

    def test_the_threshold_check_uses_the_transition_variable_percentiles(self, star_fit,
                                                                          config):
        thresholds = config.get("thresholds.star")
        low = np.percentile(star_fit.z, thresholds["threshold_percentile_low"])
        high = np.percentile(star_fit.z, thresholds["threshold_percentile_high"])
        record = flags.apply_star_flags(star_fit.record, star_fit, config)
        flagged = ReasonCode.STAR_THRESHOLD_EXTREME in record.reason_codes
        assert flagged == (not (low <= star_fit.c <= high))

    def test_an_extreme_threshold_is_flagged(self, star_fit, config):
        from copy import deepcopy

        fit = deepcopy(star_fit)
        fit.c = float(np.max(fit.z) + 10.0)
        fit.record.reason_codes = []
        fit.record.status = Status.ADEQUATE
        flags.apply_star_flags(fit.record, fit, config)
        assert ReasonCode.STAR_THRESHOLD_EXTREME in fit.record.reason_codes

    def test_standard_errors_and_covariance_are_produced(self, star_fit):
        assert star_fit.covariance.size
        assert star_fit.record.std_errors
        assert set(star_fit.record.std_errors) >= {"gamma", "c"}
        assert star_fit.record.diagnostics["covariance_status"] == "ok"

    def test_the_covariance_is_symmetric_positive_definite(self, star_fit):
        covariance = star_fit.covariance
        np.testing.assert_allclose(covariance, covariance.T, atol=1e-8)
        assert np.linalg.eigvalsh((covariance + covariance.T) / 2).min() > 0

    def test_a_singular_covariance_makes_the_model_fragile(self, config):
        # Teräsvirta (1994) §5 reads implausible parameter uncertainty as a sign the model
        # "contains redundant parameters", and Part 5 §8.2 classifies a singular or
        # unstable nonlinear Hessian/covariance as fragile. The estimates stand; the
        # asymptotic inference is what cannot be relied on.
        from thesis.core.schemas import FitRecord

        record = FitRecord(series="s", model="STAR", spec_label="x", spec_hash="",
                           window_start="2000-01-01", window_end="2010-01-01",
                           refit_date="2010-01-01", converged=True)
        flags.apply_covariance_flags(record, np.array([[1.0, 1.0], [1.0, 1.0]]), config)
        assert ReasonCode.SINGULAR_COV in record.reason_codes
        assert record.status is Status.FRAGILE

    def test_an_empty_regime_needs_corroborating_evidence_to_be_a_failure(self, config):
        # D8: failure requires numerically zero posterior occupancy **together with**
        # independent evidence of non-identification. Zero occupancy alone is fragility.
        from types import SimpleNamespace

        from thesis.core.schemas import FitRecord

        def _record():
            return FitRecord(series="s", model="MSAR", spec_label="x", spec_hash="",
                             window_start="2000-01-01", window_end="2010-01-01",
                             refit_date="2010-01-01", converged=True)

        healthy = SimpleNamespace(
            occupancy=np.array([0.0, 1.0]), smoothed_regime=np.ones((100, 2)),
            P=np.array([[0.5, 0.5], [0.5, 0.5]]), covariance=np.eye(2),
            loglik=-100.0, mu=np.array([0.0, 1.0]), phi=np.array([0.3]))
        record = flags.apply_msar_flags(_record(), healthy, config)
        assert ReasonCode.EMPTY_REGIME not in record.reason_codes
        assert record.status is Status.FRAGILE

        unidentified = SimpleNamespace(
            occupancy=np.array([0.0, 1.0]), smoothed_regime=np.ones((100, 2)),
            P=np.array([[0.5, 0.5], [0.5, 0.5]]),
            covariance=np.array([[1.0, 1.0], [1.0, 1.0]]),
            loglik=-100.0, mu=np.array([0.0, 1.0]), phi=np.array([0.3]))
        record = flags.apply_msar_flags(_record(), unidentified, config)
        assert ReasonCode.EMPTY_REGIME in record.reason_codes
        assert record.status is Status.FAILED
