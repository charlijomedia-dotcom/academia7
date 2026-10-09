"""Validation of the Harvey-Leybourne-Zu (2025) implementation.

Comp §15 requires tests of the loss-differential construction, of the local demeaning and
long-run variance calculation matching the published procedure, and of the deterministic
recording of every smoothing and bandwidth choice.

The strongest checks here reproduce claims made in the article itself:

* the simulation DGP's stated mean-variation value V_m = 0.867a² (article §5.1);
* Theorem 1, that the conventional estimator Ω̂ diverges with b under a time-varying mean
  while Theorem 4's Ω̂′ stays consistent for Ω;
* Theorem 2(i)(b), that the standard DM test's size collapses toward zero under a
  time-varying mean, whereas DM′ keeps its nominal size (Theorem 5).
"""

from __future__ import annotations

import numpy as np
import pytest

from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR
from thesis.evaluation.hlz import (
    HLZSettings,
    critical_values,
    dm_prime_statistic,
    gaussian_kernel,
    hlz_test,
    local_mean,
    mean_variation,
    modified_lrv,
    null_distribution,
    quadratic_spectral_kernel,
    smoothing_weights,
    standard_lrv,
)


def fast_settings(**overrides) -> HLZSettings:
    """Article kernels and bandwidths, with few replications so tests stay quick."""
    base = dict(
        lrv_kernel="quadratic_spectral",
        b0=1.5,
        demean_kernel="gaussian",
        h0=0.25,
        critical_value_replications=2000,
        critical_value_seed=20261005,
    )
    base.update(overrides)
    return HLZSettings(**base)


def logistic_mean(n: int, a: float, c: float = 0.5, g: float = 30.0) -> np.ndarray:
    """The article's mean function m_t = a·S_t^0 (article §5, eq. for S_t(c,g,δ1,δ2)).

    S_t(c, g, δ1, δ2) = (δ2 − δ1) / (1 + exp{−g((t−1)/(n−1) − c)}) + δ1, with δ1 = −1,
    δ2 = 1 and g = 30; S_t^0 is the case c = 0.5.
    """
    t = np.arange(1, n + 1)
    x = (t - 1) / (n - 1)
    return a * (2.0 / (1.0 + np.exp(-g * (x - c))) - 1.0)


class TestKernels:
    def test_qs_kernel_properties(self):
        # Supplement Assumption 3: symmetric, k(0) = 1, |k(x)| <= 1.
        x = np.linspace(-6, 6, 2401)
        k = quadratic_spectral_kernel(x)
        assert quadratic_spectral_kernel(np.array([0.0]))[0] == pytest.approx(1.0)
        np.testing.assert_allclose(k, quadratic_spectral_kernel(-x), atol=1e-12)
        assert np.all(np.abs(k) <= 1.0 + 1e-12)

    def test_qs_kernel_is_positive_semidefinite(self):
        # Guarantees a non-negative long-run variance estimate.
        lags = np.arange(60)[:, None] - np.arange(60)[None, :]
        matrix = quadratic_spectral_kernel(lags / 4.0)
        eigenvalues = np.linalg.eigvalsh(matrix)
        assert eigenvalues.min() > -1e-8

    def test_qs_kernel_known_value(self):
        # Direct evaluation of the Andrews (1991) formula at x = 1.
        z = 6.0 * np.pi / 5.0
        expected = (25.0 / (12.0 * np.pi**2)) * (np.sin(z) / z - np.cos(z))
        assert quadratic_spectral_kernel(np.array([1.0]))[0] == pytest.approx(expected)

    def test_gaussian_kernel_is_the_standard_normal_density(self):
        assert gaussian_kernel(np.array([0.0]))[0] == pytest.approx(1 / np.sqrt(2 * np.pi))
        assert gaussian_kernel(np.array([1.0]))[0] == pytest.approx(
            np.exp(-0.5) / np.sqrt(2 * np.pi)
        )


class TestBandwidths:
    def test_article_bandwidth_rules(self):
        settings = fast_settings()
        n = 1000
        assert settings.bandwidth_b(n) == pytest.approx(1.5 * n ** (1 / 3))
        assert settings.bandwidth_h(n) == pytest.approx(0.25 * n ** (-2 / 5))

    def test_bandwidth_rate_conditions_hold(self):
        # Assumption 4: b -> inf and n^(-1/2) b -> 0. Assumption 6: h -> 0, bh -> 0 and
        # b/(nh) -> 0. These are limits, so the test checks the sequences move the right
        # way rather than demanding small values at any particular n.
        settings = fast_settings()
        sizes = (100, 1000, 10000, 100000, 1000000)
        b = [settings.bandwidth_b(n) for n in sizes]
        h = [settings.bandwidth_h(n) for n in sizes]
        rate_b = [n**-0.5 * bi for n, bi in zip(sizes, b)]
        rate_bh = [bi * hi for bi, hi in zip(b, h)]
        rate_ratio = [bi / (n * hi) for n, bi, hi in zip(sizes, b, h)]
        assert b == sorted(b) and b[0] > 1                 # b increasing without bound
        assert h == sorted(h, reverse=True) and h[-1] > 0  # h decreasing to zero
        for sequence in (rate_b, rate_bh, rate_ratio):
            assert sequence == sorted(sequence, reverse=True)
            assert sequence[-1] < sequence[0]
        # bh = 0.375 n^(-1/15) declines especially slowly, which is worth pinning down
        # because it is part of why finite-sample critical values matter here.
        assert rate_bh[0] < 0.3 and rate_bh[-1] > 0.1

    def test_b_over_nh_is_near_one_at_realistic_sample_sizes(self):
        # b/(nh) = 6 n^(-4/15) converges very slowly, so at the sample sizes this thesis
        # evaluates it is of order one. That is the reason the authors require simulated
        # finite-sample critical values rather than standard normal ones.
        settings = fast_settings()
        for n in (150, 300, 700):
            ratio = settings.bandwidth_b(n) / (n * settings.bandwidth_h(n))
            assert 0.5 < ratio < 3.0

    def test_smoothing_weights_are_normalized(self):
        weights = smoothing_weights(50, fast_settings())
        np.testing.assert_allclose(weights.sum(axis=1), 1.0)

    def test_smoothing_weights_are_local_and_symmetric(self):
        weights = smoothing_weights(101, fast_settings())
        middle = weights[50]
        assert middle.argmax() == 50  # heaviest weight on the point itself
        np.testing.assert_allclose(middle[49], middle[51])

    def test_tuning_record_captures_every_choice(self):
        record = fast_settings().tuning_record(200)
        for key in ("lrv_kernel", "b", "b_rule", "demean_kernel", "h", "h_rule", "nh",
                    "cv_scheme", "cv_replications", "cv_seed", "two_sided"):
            assert key in record


class TestSettingsFromConfig:
    def test_article_values_are_loaded(self):
        config = load_config(config_dir=CONFIG_DIR)
        settings = HLZSettings.from_config(config)
        assert settings.lrv_kernel == "quadratic_spectral"
        assert settings.b0 == 1.5
        assert settings.demean_kernel == "gaussian"
        assert settings.h0 == 0.25
        assert settings.critical_value_replications == 50000
        assert settings.two_sided is True

    def test_unset_tuning_choice_refuses_to_run(self):
        config = load_config(config_dir=CONFIG_DIR).with_overrides(
            {"evaluation": {"hlz": {"lrv_kernel": None}}}, "unset"
        )
        with pytest.raises(KeyError):
            HLZSettings.from_config(config)

    def test_unknown_kernel_rejected(self):
        with pytest.raises(ValueError, match="quadratic spectral"):
            fast_settings(lrv_kernel="bartlett").lrv_kernel_fn()
        with pytest.raises(ValueError, match="Gaussian"):
            fast_settings(demean_kernel="epanechnikov").demean_kernel_fn()


class TestArticleDGP:
    def test_mean_function_has_zero_sample_mean(self):
        # Article §5.1: n^-1 sum S_t^0 = 0.
        assert logistic_mean(1000, a=1.0).mean() == pytest.approx(0.0, abs=1e-10)

    def test_mean_variation_matches_the_published_value(self):
        # Article §5.1: V_m = a^2 * integral m(x)^2 dx = 0.867 a^2.
        for a in (0.1, 0.3, 0.5):
            m = logistic_mean(20000, a=a)
            v_m = np.mean(m**2) - np.mean(m) ** 2
            assert v_m == pytest.approx(0.867 * a**2, rel=2e-3)

    def test_table1_mean_variation_values(self):
        # Table 1 column headings: a = 0.1, 0.3, 0.5 give V_m = 0.009, 0.078, 0.217.
        expected = {0.1: 0.009, 0.3: 0.078, 0.5: 0.217}
        for a, target in expected.items():
            m = logistic_mean(20000, a=a)
            v_m = np.mean(m**2) - np.mean(m) ** 2
            assert v_m == pytest.approx(target, abs=0.001)


class TestEstimators:
    def test_standard_lrv_recovers_the_variance_under_a_constant_mean(self):
        # With m(x) constant, Theorem 1 gives V_m = 0 and the conventional estimator is
        # consistent for Omega, which is 1 for iid standard normal data.
        rng = np.random.default_rng(1)
        estimates = [standard_lrv(rng.standard_normal(600), fast_settings()) for _ in range(20)]
        assert np.mean(estimates) == pytest.approx(1.0, rel=0.15)

    def test_modified_lrv_is_downward_biased_in_finite_samples(self):
        # A documented property of the estimator at realistic n, not a defect: because
        # b/(nh) is of order one, local demeaning removes variance at exactly the lags
        # the long-run-variance kernel weights. The authors handle this by simulating
        # finite-sample null critical values (supplement Appendix C) rather than using
        # standard normal ones, which is what this implementation does.
        rng = np.random.default_rng(31)
        settings = fast_settings()
        estimates = [modified_lrv(rng.standard_normal(600), settings) for _ in range(20)]
        assert 0.2 < np.mean(estimates) < 0.8

    def test_modified_lrv_bias_shrinks_as_the_sample_grows(self):
        # Theorem 4 states consistency; the bias must therefore fall with n.
        settings = fast_settings()
        rng = np.random.default_rng(32)
        means = []
        for n in (150, 600, 2400):
            means.append(
                np.mean([modified_lrv(rng.standard_normal(n), settings) for _ in range(12)])
            )
        assert means == sorted(means)
        assert means[-1] > 1.4 * means[0]

    def test_local_mean_tracks_a_time_varying_mean(self):
        rng = np.random.default_rng(2)
        n = 800
        m = logistic_mean(n, a=0.5)
        d = m + rng.standard_normal(n)
        m_hat = local_mean(d, fast_settings())
        # The smoother should recover the shape: strongly correlated with the truth and
        # closer to it than the full-sample mean is.
        assert np.corrcoef(m_hat, m)[0, 1] > 0.8
        assert np.mean((m_hat - m) ** 2) < np.mean((d.mean() - m) ** 2)

    def test_theorem_1_only_the_standard_lrv_inflates_with_a_time_varying_mean(self):
        # Theorem 1: Omega_hat = Omega + (1 + 2 b lambda_k) V_m + o_p(1), so adding mean
        # variation inflates the conventional estimator. Theorem 4: Omega_hat' is
        # consistent for Omega whether or not the mean varies, so adding the same mean
        # variation must leave it essentially unchanged. Comparing each estimator against
        # itself isolates the effect of the mean function from the finite-sample level.
        rng = np.random.default_rng(3)
        n = 800
        settings = fast_settings()
        flat_std, moving_std, flat_mod, moving_mod = [], [], [], []
        m = logistic_mean(n, a=0.5)
        for _ in range(15):
            noise = rng.standard_normal(n)
            flat_std.append(standard_lrv(noise, settings))
            moving_std.append(standard_lrv(m + noise, settings))
            flat_mod.append(modified_lrv(noise, settings))
            moving_mod.append(modified_lrv(m + noise, settings))
        # The conventional estimator inflates substantially.
        assert np.mean(moving_std) > 3.0 * np.mean(flat_std)
        # The modified estimator is barely affected.
        assert np.mean(moving_mod) == pytest.approx(np.mean(flat_mod), rel=0.25)

    def test_standard_lrv_inflation_grows_with_the_bandwidth(self):
        # The divergence term in Theorem 1 is proportional to b.
        rng = np.random.default_rng(4)
        n = 800
        d = logistic_mean(n, a=0.5) + rng.standard_normal(n)
        small_b = standard_lrv(d, fast_settings(b0=0.5))
        large_b = standard_lrv(d, fast_settings(b0=4.5))
        assert large_b > 2.0 * small_b

    def test_modified_lrv_is_insensitive_to_the_mean_at_every_bandwidth(self):
        # Whatever b is chosen, local demeaning must strip out the mean variation.
        rng = np.random.default_rng(5)
        n = 800
        noise = rng.standard_normal(n)
        m = logistic_mean(n, a=0.5)
        for b0 in (1.0, 1.5, 2.5):
            settings = fast_settings(b0=b0)
            flat = modified_lrv(noise, settings)
            moving = modified_lrv(m + noise, settings)
            assert moving == pytest.approx(flat, rel=0.3)

    def test_estimated_mean_variation_is_positive_only_when_the_mean_moves(self):
        rng = np.random.default_rng(6)
        n = 800
        settings = fast_settings()
        moving = mean_variation(logistic_mean(n, a=0.5) + rng.standard_normal(n), settings)
        flat = mean_variation(rng.standard_normal(n), settings)
        assert moving > 5 * flat


class TestStatistic:
    def test_sign_follows_the_loss_differential_convention(self):
        # d_t = loss(competitor) - loss(benchmark): negative mean favours the competitor.
        rng = np.random.default_rng(7)
        d = rng.standard_normal(400) - 0.5
        assert dm_prime_statistic(d, fast_settings()) < 0

    def test_zero_mean_gives_a_small_statistic(self):
        rng = np.random.default_rng(8)
        d = rng.standard_normal(400)
        assert abs(dm_prime_statistic(d, fast_settings())) < 3.0

    def test_statistic_is_deterministic(self):
        rng = np.random.default_rng(9)
        d = rng.standard_normal(300)
        settings = fast_settings()
        assert dm_prime_statistic(d, settings) == dm_prime_statistic(d, settings)


class TestCriticalValues:
    def test_simulated_null_is_approximately_symmetric_and_centred(self):
        simulated = null_distribution(120, fast_settings())
        assert abs(simulated.mean()) < 0.1
        assert abs(np.quantile(simulated, 0.05) + np.quantile(simulated, 0.95)) < 0.3

    def test_critical_values_increase_with_confidence(self):
        cv = critical_values(120, fast_settings())
        assert cv["0.10"] < cv["0.05"] < cv["0.01"]

    def test_critical_values_are_reproducible_for_a_seed(self):
        a = critical_values(120, fast_settings())
        b = critical_values(120, fast_settings())
        assert a == b

    def test_a_different_seed_changes_the_draw(self):
        a = critical_values(120, fast_settings(critical_value_seed=1))
        b = critical_values(120, fast_settings(critical_value_seed=2))
        assert a != b

    @pytest.mark.slow
    def test_finite_sample_critical_values_deliver_nominal_size(self):
        # Appendix C states the scheme is exact when d_t is iid normal with zero mean
        # variation, so applying the simulated critical values to fresh iid normal data
        # must reject about 5% of the time.
        n, reps = 120, 1500
        settings = fast_settings(critical_value_replications=4000)
        cv = critical_values(n, settings)["0.05"]
        rng = np.random.default_rng(11)
        rejections = sum(
            abs(dm_prime_statistic(rng.standard_normal(n), settings)) > cv
            for _ in range(reps)
        )
        assert 0.03 < rejections / reps < 0.075


class TestTestWrapper:
    def test_returns_standardized_result_with_all_tuning_recorded(self):
        rng = np.random.default_rng(12)
        d = rng.standard_normal(200)
        result, row = hlz_test(d, fast_settings(), series="CPIAUCSL", model_a="AR", model_b="MSAR")
        assert result is not None
        assert row.available
        assert row.model == "AR vs MSAR"
        assert row.tuning["lrv_kernel"] == "quadratic_spectral"
        assert row.tuning["cv_scheme"] == "appendix_C_iid_normal"
        assert "n^-1 sum_t E(d_t) = 0" in row.null_hypothesis
        assert 0.0 <= row.p_value <= 1.0

    def test_reports_both_tails_and_the_mean_variation_ratio(self):
        rng = np.random.default_rng(13)
        d = rng.standard_normal(200) - 0.3
        result, row = hlz_test(d, fast_settings())
        assert result.p_value_upper + result.p_value_lower == pytest.approx(
            1.0, abs=0.01
        )
        assert "mean_variation_ratio" in row.extra
        assert result.mean_variation_ratio >= 0.0

    def test_empty_sample_is_unavailable_not_fabricated(self):
        result, row = hlz_test(np.array([]), fast_settings())
        assert result is None
        assert not row.available
        assert row.statistic is None
        assert row.decision_5pct == "unavailable"

    def test_non_finite_sample_is_unavailable(self):
        result, row = hlz_test(np.array([1.0, np.nan, 2.0]), fast_settings())
        assert result is None
        assert not row.available

    def test_very_short_sample_is_unavailable(self):
        rng = np.random.default_rng(14)
        result, row = hlz_test(rng.standard_normal(5), fast_settings())
        assert result is None
        assert not row.available
        assert "5" in row.unavailable_reason

    def test_detects_a_genuine_average_difference(self):
        rng = np.random.default_rng(15)
        d = rng.standard_normal(300) - 0.4
        result, row = hlz_test(d, fast_settings())
        assert row.p_value < 0.05
        assert "competitor" in row.implication


@pytest.mark.slow
class TestReproducesArticleFindings:
    """The article's headline claim, reproduced on simulated data.

    Theorem 2(i)(b): under a time-varying loss-differential mean the standard DM test has
    asymptotic size zero. Theorem 5(i): DM′ retains the nominal size. This is precisely
    why Part 5 §10.2 makes HLZ the primary pairwise test for a thesis about forecasting
    under instability, so it is worth demonstrating rather than asserting.
    """

    def test_dm_undersized_while_dm_prime_is_correctly_sized(self):
        n, reps = 150, 600
        settings = fast_settings(critical_value_replications=3000)
        rng = np.random.default_rng(21)
        # Null is true: the mean function integrates to zero over the evaluation period.
        m = logistic_mean(n, a=0.5)
        cv_prime = critical_values(n, settings)["0.05"]

        dm_rejections = 0
        dm_prime_rejections = 0
        for _ in range(reps):
            d = m + rng.standard_normal(n)
            omega_std = standard_lrv(d, settings)
            dm = np.sqrt(n) * d.mean() / np.sqrt(omega_std)
            if abs(dm) > 1.96:
                dm_rejections += 1
            if abs(dm_prime_statistic(d, settings)) > cv_prime:
                dm_prime_rejections += 1

        dm_size = dm_rejections / reps
        dm_prime_size = dm_prime_rejections / reps
        # The standard test collapses well below nominal; the modified test does not.
        assert dm_size < 0.03
        assert 0.02 < dm_prime_size < 0.12
        assert dm_prime_size > dm_size
