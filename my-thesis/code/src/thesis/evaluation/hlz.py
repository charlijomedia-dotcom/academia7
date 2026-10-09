"""Harvey, Leybourne and Zu (2025) test for equal average forecast accuracy.

The primary pairwise inferential test of the thesis (Part 5 §10.2). Implemented strictly
from the published article and its supplementary appendix, both held with checksums in
`source-materials/hlz2025/`. Part 5 §10.2 and Comp §15 forbid substituting a generic HAC
estimator and calling the result Harvey-Leybourne-Zu, so every quantity below traces to a
specific equation in those documents:

    local mean          m̂_t = Σ_s w_{t,s} d_s,  w_{t,s} = K((s−t)/(nh)) / Σ_s K((s−t)/(nh))
    modified LRV        Ω̂′ = n⁻¹ Σ_t Σ_s (d_t − m̂_t)(d_s − m̂_s) k((t−s)/b)   (article eq. 4)
    statistic           DM′ = √n · d̄ / √Ω̂′                                    (article p.648)
    mean variation      V̂_m = n⁻¹ Σ m̂_t² − (n⁻¹ Σ m̂_t)²                       (article eq. 5)
    standard LRV        Ω̂  = n⁻¹ Σ_t Σ_s (d_t − d̄)(d_s − d̄) k((t−s)/b)        (article eq. 2)

with k(·) the quadratic spectral kernel, b = 1.5·n^(1/3), K(·) the Gaussian kernel and
h = 0.25·n^(−2/5) (article §5, p.649, adopted throughout the article including its
empirical applications).

Critical values follow the supplement's Appendix C: simulate iid N(0,1) series of the
actual length n, recompute DM′ with the same kernels and bandwidths, and read off
empirical quantiles. The authors note these are exact when d_t is iid normal with zero
mean variation and serve as approximations otherwise.

Sign convention (decision D12): d_t = loss(competitor) − loss(benchmark), so a negative
statistic means the competitor is the more accurate forecast.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import numpy as np

from ..core.config import Config
from ..core.schemas import TestResult

_SQRT_2PI = np.sqrt(2.0 * np.pi)


# ---------------------------------------------------------------------------
# Kernels
# ---------------------------------------------------------------------------


def quadratic_spectral_kernel(x: np.ndarray) -> np.ndarray:
    """Quadratic spectral kernel (Andrews 1991), the k(·) of the article.

    k(0) = 1, symmetric, |k(x)| ≤ 1, and positive semidefinite, which guarantees the
    resulting long-run variance estimate is non-negative (supplement Assumption 3).
    """
    x = np.asarray(x, dtype=float)
    out = np.ones_like(x)
    nonzero = x != 0.0
    z = 6.0 * np.pi * x[nonzero] / 5.0
    out[nonzero] = (25.0 / (12.0 * np.pi**2 * x[nonzero] ** 2)) * (
        np.sin(z) / z - np.cos(z)
    )
    return out


def gaussian_kernel(u: np.ndarray) -> np.ndarray:
    """Standard normal density, the K(·) of the article.

    Only relative weights matter because the local-mean weights are normalized, but the
    density form is used so the bandwidth has its usual interpretation.
    """
    u = np.asarray(u, dtype=float)
    return np.exp(-0.5 * u**2) / _SQRT_2PI


_LRV_KERNELS = {"quadratic_spectral": quadratic_spectral_kernel}
_DEMEAN_KERNELS = {"gaussian": gaussian_kernel}


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HLZSettings:
    """Tuning choices, all of which must come from the published article."""

    lrv_kernel: str
    b0: float
    demean_kernel: str
    h0: float
    critical_value_replications: int
    critical_value_seed: int
    two_sided: bool = True
    report_one_sided: bool = True
    b_exponent: float = 1.0 / 3.0
    h_exponent: float = -2.0 / 5.0
    source: str = ""

    @classmethod
    def from_config(cls, config: Config) -> "HLZSettings":
        """Build settings from configuration, refusing any unset tuning choice.

        `Config.require` raises on a null value, so an incomplete configuration stops the
        test rather than letting it fall back on a default that the authors never
        specified.
        """
        return cls(
            lrv_kernel=config.require("evaluation.hlz.lrv_kernel"),
            b0=float(config.require("evaluation.hlz.lrv_bandwidth.b0")),
            demean_kernel=config.require("evaluation.hlz.demean_kernel"),
            h0=float(config.require("evaluation.hlz.demean_bandwidth.h0")),
            critical_value_replications=int(
                config.require("evaluation.hlz.critical_value_replications")
            ),
            critical_value_seed=int(config.require("evaluation.hlz.critical_value_seed")),
            two_sided=bool(config.require("evaluation.hlz.two_sided")),
            report_one_sided=bool(config.get("evaluation.hlz.report_one_sided", True)),
            source=config.get("evaluation.hlz.source", ""),
        )

    def bandwidth_b(self, n: int) -> float:
        """LRV bandwidth b = b0 · n^(1/3) (article §5)."""
        return float(self.b0 * n**self.b_exponent)

    def bandwidth_h(self, n: int) -> float:
        """Local-mean bandwidth h = h0 · n^(−2/5) (article §5)."""
        return float(self.h0 * n**self.h_exponent)

    def lrv_kernel_fn(self):
        try:
            return _LRV_KERNELS[self.lrv_kernel]
        except KeyError as exc:
            raise ValueError(
                f"unknown HLZ long-run-variance kernel {self.lrv_kernel!r}; the article "
                f"specifies the quadratic spectral kernel"
            ) from exc

    def demean_kernel_fn(self):
        try:
            return _DEMEAN_KERNELS[self.demean_kernel]
        except KeyError as exc:
            raise ValueError(
                f"unknown HLZ local-demeaning kernel {self.demean_kernel!r}; the article "
                f"specifies the Gaussian kernel"
            ) from exc

    def tuning_record(self, n: int) -> dict[str, Any]:
        """Every tuning choice, recorded on the output row as Part 5 §10.2 requires."""
        return {
            "n": n,
            "lrv_kernel": self.lrv_kernel,
            "b": round(self.bandwidth_b(n), 6),
            "b_rule": f"{self.b0} * n**(1/3)",
            "demean_kernel": self.demean_kernel,
            "h": round(self.bandwidth_h(n), 8),
            "h_rule": f"{self.h0} * n**(-2/5)",
            "nh": round(n * self.bandwidth_h(n), 6),
            "cv_scheme": "appendix_C_iid_normal",
            "cv_replications": self.critical_value_replications,
            "cv_seed": self.critical_value_seed,
            "two_sided": self.two_sided,
            "source": self.source,
        }


# ---------------------------------------------------------------------------
# Estimator components
# ---------------------------------------------------------------------------


def smoothing_weights(n: int, settings: HLZSettings) -> np.ndarray:
    """Row-normalized local-mean weights w_{t,s} = K((s−t)/(nh)) / Σ_s K((s−t)/(nh)).

    Note the argument is scaled by `nh`, not `h`: with h = h0·n^(−2/5) the effective
    smoothing span is nh = h0·n^(3/5) observations.
    """
    kernel = settings.demean_kernel_fn()
    nh = n * settings.bandwidth_h(n)
    if nh <= 0:
        raise ValueError(f"local-mean bandwidth nh must be positive, got {nh}")
    offsets = np.arange(n)[None, :] - np.arange(n)[:, None]  # s - t
    weights = kernel(offsets / nh)
    row_sums = weights.sum(axis=1, keepdims=True)
    return weights / row_sums


def lrv_kernel_matrix(n: int, settings: HLZSettings) -> np.ndarray:
    """Matrix of k((t−s)/b) used by both long-run-variance estimators."""
    kernel = settings.lrv_kernel_fn()
    lags = np.arange(n)[:, None] - np.arange(n)[None, :]
    return kernel(lags / settings.bandwidth_b(n))


def local_mean(d: np.ndarray, settings: HLZSettings) -> np.ndarray:
    """The nonparametric estimate m̂_t of the time-varying loss-differential mean."""
    d = np.asarray(d, dtype=float)
    return smoothing_weights(d.size, settings) @ d


def modified_lrv(d: np.ndarray, settings: HLZSettings) -> float:
    """Ω̂′, the locally demeaned long-run variance (article eq. 4)."""
    d = np.asarray(d, dtype=float)
    n = d.size
    residual = d - local_mean(d, settings)
    kernel_matrix = lrv_kernel_matrix(n, settings)
    return float(residual @ kernel_matrix @ residual / n)


def standard_lrv(d: np.ndarray, settings: HLZSettings) -> float:
    """Ω̂, the conventional full-sample demeaned long-run variance (article eq. 2).

    Reported alongside Ω̂′ because the article's whole point is that Ω̂ diverges when the
    loss-differential mean varies over time, which is exactly the thesis's setting.
    """
    d = np.asarray(d, dtype=float)
    n = d.size
    residual = d - d.mean()
    kernel_matrix = lrv_kernel_matrix(n, settings)
    return float(residual @ kernel_matrix @ residual / n)


def mean_variation(d: np.ndarray, settings: HLZSettings) -> float:
    """V̂_m, the estimated variation in the mean function (article eq. 5)."""
    m_hat = local_mean(d, settings)
    return float(np.mean(m_hat**2) - np.mean(m_hat) ** 2)


def dm_prime_statistic(d: np.ndarray, settings: HLZSettings) -> float:
    """DM′ = √n · d̄ / √Ω̂′."""
    d = np.asarray(d, dtype=float)
    omega = modified_lrv(d, settings)
    if not np.isfinite(omega) or omega <= 0:
        return float("nan")
    return float(np.sqrt(d.size) * d.mean() / np.sqrt(omega))


# ---------------------------------------------------------------------------
# Finite-sample null distribution (supplement Appendix C)
# ---------------------------------------------------------------------------


def _simulate_null(n: int, settings: HLZSettings, chunk: int = 2000) -> np.ndarray:
    """Simulated null distribution of DM′ for sample size n.

    Appendix C: draw iid N(0,1) series of length n, compute DM′ with the same kernels and
    bandwidths as the actual statistic, and repeat B times. Vectorized over replications
    and processed in chunks to bound memory.
    """
    rng = np.random.default_rng(settings.critical_value_seed)
    weights = smoothing_weights(n, settings)
    kernel_matrix = lrv_kernel_matrix(n, settings)
    sqrt_n = np.sqrt(n)
    total = settings.critical_value_replications
    out = np.empty(total, dtype=float)
    done = 0
    while done < total:
        size = min(chunk, total - done)
        draws = rng.standard_normal((size, n))
        residual = draws - draws @ weights.T
        omega = np.einsum("ij,ij->i", residual @ kernel_matrix, residual) / n
        with np.errstate(invalid="ignore", divide="ignore"):
            out[done : done + size] = sqrt_n * draws.mean(axis=1) / np.sqrt(omega)
        done += size
    return out


@lru_cache(maxsize=64)
def _null_distribution_cached(
    n: int,
    lrv_kernel: str,
    b0: float,
    demean_kernel: str,
    h0: float,
    replications: int,
    seed: int,
) -> tuple[float, ...]:
    settings = HLZSettings(
        lrv_kernel=lrv_kernel,
        b0=b0,
        demean_kernel=demean_kernel,
        h0=h0,
        critical_value_replications=replications,
        critical_value_seed=seed,
    )
    return tuple(_simulate_null(n, settings))


def null_distribution(n: int, settings: HLZSettings) -> np.ndarray:
    """Cached simulated null distribution. Depends only on n and the tuning choices."""
    return np.asarray(
        _null_distribution_cached(
            n,
            settings.lrv_kernel,
            settings.b0,
            settings.demean_kernel,
            settings.h0,
            settings.critical_value_replications,
            settings.critical_value_seed,
        )
    )


def critical_values(
    n: int, settings: HLZSettings, levels: tuple[float, ...] = (0.10, 0.05, 0.01)
) -> dict[str, float]:
    """Two-sided finite-sample critical values from the simulated null distribution."""
    simulated = np.abs(null_distribution(n, settings))
    return {f"{level:.2f}": float(np.quantile(simulated, 1.0 - level)) for level in levels}


# ---------------------------------------------------------------------------
# The test
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HLZResult:
    n: int
    mean_loss_differential: float
    statistic: float
    omega_modified: float
    omega_standard: float
    mean_variation: float
    mean_variation_ratio: float
    p_value_two_sided: float
    p_value_upper: float
    p_value_lower: float
    tuning: dict[str, Any]

    @property
    def p_value(self) -> float:
        return self.p_value_two_sided


def hlz_test(
    d: np.ndarray,
    settings: HLZSettings,
    *,
    series: str | None = None,
    model_a: str | None = None,
    model_b: str | None = None,
) -> tuple[HLZResult | None, TestResult]:
    """Run the HLZ test on a loss-differential series.

    Returns the numeric result and the standardized `TestResult` row required by
    Part 5 §7.2. An unusable sample yields an explicitly unavailable `TestResult` rather
    than a fabricated number.
    """
    d = np.asarray(d, dtype=float)
    label = f"{model_a} vs {model_b}" if model_a and model_b else "pair"
    base = {
        "name": "Harvey-Leybourne-Zu (2025) equal average forecast accuracy",
        "null_hypothesis": (
            "equal average forecast accuracy over the evaluation period: "
            "n^-1 sum_t E(d_t) = 0"
        ),
        "reference": (
            "finite-sample null distribution simulated under the supplement's "
            "Appendix C scheme (iid N(0,1), same kernels and bandwidths)"
        ),
        "series": series,
        "model": label,
    }

    if d.size == 0 or not np.isfinite(d).all():
        return None, TestResult(
            statistic=None,
            p_value=None,
            decision_5pct="unavailable",
            implication="no finite loss differentials on the common evaluation dates",
            available=False,
            unavailable_reason="empty or non-finite loss differential series",
            tuning={},
            **base,
        )

    n = d.size
    tuning = settings.tuning_record(n)

    if n < 10:
        return None, TestResult(
            statistic=None,
            p_value=None,
            decision_5pct="unavailable",
            implication="too few forecast observations for a meaningful test",
            available=False,
            unavailable_reason=f"only {n} loss differentials",
            tuning=tuning,
            **base,
        )

    omega_prime = modified_lrv(d, settings)
    omega_std = standard_lrv(d, settings)
    v_m = mean_variation(d, settings)

    if not np.isfinite(omega_prime) or omega_prime <= 0:
        return None, TestResult(
            statistic=None,
            p_value=None,
            decision_5pct="unavailable",
            implication="the modified long-run variance estimate is not positive",
            available=False,
            unavailable_reason=f"Omega_hat_prime = {omega_prime!r}",
            tuning=tuning,
            **base,
        )

    statistic = float(np.sqrt(n) * d.mean() / np.sqrt(omega_prime))
    simulated = null_distribution(n, settings)
    p_two = float(np.mean(np.abs(simulated) >= abs(statistic)))
    p_upper = float(np.mean(simulated >= statistic))
    p_lower = float(np.mean(simulated <= statistic))
    p_value = p_two if settings.two_sided else min(p_upper, p_lower)

    result = HLZResult(
        n=n,
        mean_loss_differential=float(d.mean()),
        statistic=statistic,
        omega_modified=omega_prime,
        omega_standard=omega_std,
        mean_variation=v_m,
        mean_variation_ratio=float(v_m / omega_prime),
        p_value_two_sided=p_two,
        p_value_upper=p_upper,
        p_value_lower=p_lower,
        tuning=tuning,
    )

    # d_t = loss(competitor) - loss(benchmark), so a negative mean favours the competitor.
    if p_value < 0.05:
        direction = "the competitor" if d.mean() < 0 else "the benchmark"
        implication = (
            f"reject equal average accuracy at 5%: {direction} is more accurate on "
            f"average over the evaluation period"
        )
    else:
        implication = "no evidence against equal average forecast accuracy at 5%"

    return result, TestResult(
        statistic=statistic,
        p_value=p_value,
        decision_5pct="reject" if p_value < 0.05 else "do not reject",
        implication=implication,
        tuning=tuning,
        extra={
            "mean_loss_differential": result.mean_loss_differential,
            "omega_modified": omega_prime,
            "omega_standard": omega_std,
            "mean_variation": v_m,
            "mean_variation_ratio": result.mean_variation_ratio,
            "p_value_two_sided": p_two,
            "p_value_upper": p_upper,
            "p_value_lower": p_lower,
        },
        **base,
    )
