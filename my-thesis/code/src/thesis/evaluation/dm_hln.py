"""Diebold-Mariano with the Harvey-Leybourne-Newbold correction (Part 5 §10.3).

Retained as the **secondary** conventional benchmark, never as the primary conclusion. It
is kept deliberately separate from the Harvey-Leybourne-Zu implementation: where the two
disagree, that disagreement is itself informative about sensitivity to instability, so it
is reported rather than reconciled (Part 5 §10.3).

    DM  = d_bar / sqrt(V_hat / n),  V_hat = Newey-West with truncation h - 1
    DM* = DM * sqrt((n + 1 - 2h + h(h-1)/n) / n),  compared with Student t(n-1)
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from ..core.schemas import TestResult
from .losses import SIGN_CONVENTION, loss_differential

SIGNIFICANCE = 0.05


def newey_west_variance(d: np.ndarray, truncation: int) -> float:
    """Bartlett-kernel long-run variance with the given truncation lag."""
    d = np.asarray(d, dtype=float)
    n = d.size
    centred = d - d.mean()
    variance = float(centred @ centred / n)
    for lag in range(1, max(truncation, 0) + 1):
        if lag >= n:
            break
        covariance = float(centred[lag:] @ centred[:-lag] / n)
        weight = 1.0 - lag / (truncation + 1)
        variance += 2.0 * weight * covariance
    return variance


def dm_hln_test(
    competitor_errors: np.ndarray,
    benchmark_errors: np.ndarray,
    horizon: int,
    loss_kind: str,
    *,
    series: str = "",
    model_a: str = "",
    model_b: str = "",
) -> TestResult:
    """Secondary pairwise equal-accuracy test on already-aligned errors."""
    d = loss_differential(competitor_errors, benchmark_errors, loss_kind)
    d = d[np.isfinite(d)]
    n = d.size
    label = f"{model_a} vs {model_b}" if model_a and model_b else "pair"
    base = {
        "name": f"Diebold-Mariano with Harvey-Leybourne-Newbold correction ({loss_kind} loss)",
        "null_hypothesis": "equal expected forecast loss",
        "reference": "Student t(n-1) after the finite-sample correction",
        "series": series,
        "model": label,
    }
    truncation = max(horizon - 1, 0)

    if n < 10:
        return TestResult(statistic=None, p_value=None, decision_5pct="unavailable",
                          implication="too few paired forecasts", available=False,
                          unavailable_reason=f"n={n}", tuning={"horizon": horizon}, **base)

    variance = newey_west_variance(d, truncation)
    if not np.isfinite(variance) or variance <= 0:
        return TestResult(statistic=None, p_value=None, decision_5pct="unavailable",
                          implication="non-positive long-run variance estimate",
                          available=False, unavailable_reason=f"variance={variance!r}",
                          tuning={"horizon": horizon, "truncation": truncation}, **base)

    dm = float(d.mean() / np.sqrt(variance / n))
    correction = np.sqrt((n + 1 - 2 * horizon + horizon * (horizon - 1) / n) / n)
    statistic = float(dm * correction)
    p_value = float(2 * stats.t.sf(abs(statistic), df=n - 1))
    reject = p_value < SIGNIFICANCE
    direction = "the competitor" if d.mean() < 0 else "the benchmark"
    return TestResult(
        statistic=statistic,
        p_value=p_value,
        decision_5pct="reject" if reject else "do not reject",
        implication=(
            f"reject equal accuracy at 5%: {direction} has lower expected loss"
            if reject else "no evidence against equal expected forecast loss at 5%"
        ),
        tuning={
            "horizon": horizon,
            "loss": loss_kind,
            "hac_kernel": "bartlett",
            "truncation": truncation,
            "truncation_rule": "h-1",
            "small_sample_correction": "harvey_leybourne_newbold",
            "correction_factor": float(correction),
            "n": n,
            "two_sided": True,
            "sign_convention": SIGN_CONVENTION,
        },
        extra={"mean_loss_differential": float(d.mean()), "dm_uncorrected": dm,
               "long_run_variance": variance},
        **base,
    )


def agrees_with(dm_result: TestResult, hlz_result: TestResult) -> str:
    """Whether the secondary test reaches the same 5% conclusion as the primary one."""
    if not dm_result.available or not hlz_result.available:
        return "unavailable"
    return "agree" if dm_result.decision_5pct == hlz_result.decision_5pct else "disagree"
