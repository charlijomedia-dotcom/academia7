"""Model credibility flags and the adequate/fragile/failed classification.

Part 5 §7.5 and §8 define the categories; decision D8 fixes exactly which numeric rules
apply and, just as importantly, which proposed rules were rejected. The thresholds here
are transparent operational warning flags, never statistical critical values
(literature justification §3.33).

The asymmetry matters: low regime occupancy makes a model *fragile*, not failed. Failure is
reserved for estimation that is computationally or statistically unusable.
"""

from __future__ import annotations

import numpy as np

from ..core.config import Config
from ..core.schemas import FitRecord, ReasonCode, Status, TestResult


def apply_msar_flags(record: FitRecord, fit, config: Config) -> FitRecord:
    """Part 5 §8.1 regime-credibility rules."""
    thresholds = config.get("thresholds.msar")
    occupancy = np.asarray(fit.occupancy, dtype=float)
    n_obs = fit.smoothed_regime.shape[0] if fit.smoothed_regime.size else 0
    effective = occupancy * n_obs

    for k, (share, count) in enumerate(zip(occupancy, effective)):
        if share < thresholds["low_occupancy_fraction"] or count < thresholds["low_occupancy_effective_obs"]:
            record.add_flag(
                ReasonCode.LOW_OCCUPANCY, Status.FRAGILE,
                detail=f"regime {k + 1}: occupancy={share:.4f}, effective obs={count:.1f}",
            )
        # Decision D8: failure needs evidence of effective non-identification, which is
        # numerically zero occupancy, not merely a small share.
        if count <= 0.0 or share <= 0.0:
            record.add_flag(
                ReasonCode.EMPTY_REGIME, Status.FAILED,
                detail=f"regime {k + 1} has numerically zero posterior occupancy",
            )

    P = np.asarray(fit.P, dtype=float)
    if P.size:
        low, high = thresholds["transition_boundary_low"], thresholds["transition_boundary_high"]
        for i in range(P.shape[0]):
            for j in range(P.shape[1]):
                if P[i, j] <= low or P[i, j] >= high:
                    record.add_flag(
                        ReasonCode.TRANSITION_BOUNDARY, Status.FRAGILE,
                        detail=f"p[{i + 1},{j + 1}]={P[i, j]:.6f}",
                    )
    return record


def apply_star_flags(record: FitRecord, fit, config: Config) -> FitRecord:
    """Part 5 §8.2 STAR credibility rules."""
    thresholds = config.get("thresholds.star")
    bounds = config.get("models.star.gamma_bounds")
    tolerance = float(thresholds["gamma_bound_tolerance"])

    # Decision D8: contact with the actual optimizer bound within tolerance, not an
    # arbitrary proportional margin.
    if np.isfinite(fit.gamma) and (
        abs(fit.gamma - bounds[0]) <= tolerance or abs(fit.gamma - bounds[1]) <= tolerance
    ):
        record.add_flag(ReasonCode.STAR_GAMMA_BOUND, Status.FRAGILE, detail=float(fit.gamma))

    if fit.G.size:
        low = np.percentile(fit.y, thresholds["threshold_percentile_low"]) if fit.y.size else np.nan
        high = np.percentile(fit.y, thresholds["threshold_percentile_high"]) if fit.y.size else np.nan
        if np.isfinite(low) and np.isfinite(high) and not (low <= fit.c <= high):
            record.add_flag(
                ReasonCode.STAR_THRESHOLD_EXTREME, Status.FRAGILE,
                detail=f"c={fit.c:.6g} outside [{low:.6g}, {high:.6g}]",
            )
        spread = float(fit.G.max() - fit.G.min())
        if fit.G.std() < thresholds["near_constant_transition_sd"] or spread < thresholds["near_constant_transition_range"]:
            record.add_flag(
                ReasonCode.NEAR_CONSTANT_TRANSITION, Status.FRAGILE,
                detail=f"sd={fit.G.std():.4f}, range={spread:.4f}",
            )
    return record


def apply_residual_flags(
    record: FitRecord, primary_ljung_box: TestResult, config: Config
) -> FitRecord:
    """Primary Ljung-Box rejection makes a model fragile (Part 5 §7.5)."""
    if primary_ljung_box.decision_5pct == "reject":
        record.add_flag(
            ReasonCode.RESIDUAL_AUTOCORR, Status.FRAGILE,
            detail=f"{primary_ljung_box.name} p={primary_ljung_box.p_value:.4g}",
        )
    return record


def apply_covariance_flags(record: FitRecord, covariance: np.ndarray, config: Config) -> FitRecord:
    """Decision D8 covariance rules: unusable is failure, ill-conditioned is fragile."""
    if covariance is None or not np.size(covariance):
        return record
    if not np.isfinite(covariance).all():
        record.add_flag(ReasonCode.SINGULAR_COV, Status.FAILED, detail="non-finite covariance")
        return record
    try:
        condition = float(np.linalg.cond(covariance))
    except np.linalg.LinAlgError:
        record.add_flag(ReasonCode.SINGULAR_COV, Status.FAILED, detail="covariance not invertible")
        return record
    eigenvalues = np.linalg.eigvalsh((covariance + covariance.T) / 2)
    if eigenvalues.min() <= 0:
        record.add_flag(ReasonCode.SINGULAR_COV, Status.FAILED, detail="covariance not positive definite")
    elif condition > float(config.get("thresholds.covariance.ill_conditioned_condition_number")):
        record.add_flag(
            ReasonCode.ILL_CONDITIONED_COV, Status.FRAGILE,
            detail=f"condition number={condition:.3g}",
        )
    return record


def flag_extreme_forecast(
    record: FitRecord, forecast: float, window: np.ndarray, config: Config
) -> bool:
    """Decision D8: a warning only.

    An extreme forecast is flagged for the figures and the registry, but it is never an
    automatic failure and the value is never deleted from the numerical results.
    """
    if not np.isfinite(forecast):
        record.add_flag(ReasonCode.NONFINITE, Status.FAILED, detail="non-finite forecast")
        return True
    sds = float(config.get("thresholds.forecasts.extreme_forecast_window_sds"))
    mean, sd = float(np.mean(window)), float(np.std(window, ddof=1))
    if sd > 0 and abs(forecast - mean) > sds * sd:
        record.add_flag(
            ReasonCode.EXTREME_FORECAST, Status.FRAGILE,
            detail=f"forecast={forecast:.6g}, window mean={mean:.6g}, sd={sd:.6g}",
        )
        return True
    return False
