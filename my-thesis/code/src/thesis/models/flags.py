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


def _non_identification_evidence(fit, config: Config) -> str:
    """Independent evidence that a regime is effectively unidentified, or an empty string.

    This is the second half of the D8 empty-regime conjunction. It became checkable only
    once the observed-information covariance was computed; before that the conjunction
    could not be evaluated at all.
    """
    reasons = []
    covariance = getattr(fit, "covariance", None)
    if covariance is not None and np.size(covariance):
        condition, detail = covariance_condition(covariance, config)
        if condition == UNUSABLE:
            reasons.append(f"an unusable covariance ({detail})")
    if not np.isfinite(getattr(fit, "loglik", np.nan)):
        reasons.append("a non-finite log likelihood")
    for name in ("mu", "phi"):
        values = np.asarray(getattr(fit, name, np.empty(0)), dtype=float)
        if values.size and not np.isfinite(values).all():
            reasons.append(f"non-finite {name}")
    return " and ".join(reasons)


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
        # Decision D8 and Part 5 §8.1: failure requires numerically zero posterior
        # occupancy **together with** independent evidence of non-identification — an
        # unusable covariance, or a non-finite likelihood or parameter vector. Zero
        # occupancy on its own is already covered as low occupancy, which is fragile.
        if count <= 0.0 or share <= 0.0:
            corroborating = _non_identification_evidence(fit, config)
            if corroborating:
                record.add_flag(
                    ReasonCode.EMPTY_REGIME, Status.FAILED,
                    detail=(f"regime {k + 1} has numerically zero posterior occupancy, "
                            f"with {corroborating}"),
                )
            else:
                record.add_flag(
                    ReasonCode.LOW_OCCUPANCY, Status.FRAGILE,
                    detail=(f"regime {k + 1} has numerically zero posterior occupancy; "
                            "no corroborating evidence of non-identification, so this is "
                            "fragility rather than failure (D8)"),
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
        # Part 5 §8.2 compares the estimated threshold with the 5th-95th percentile of the
        # **transition variable** y_{t-d} on the estimation rows, which is the scale c
        # lives on. Using the dependent variable instead compares c against a different
        # series whenever the delay is non-zero, and against a different sample in any
        # case. Teräsvirta (1994) §5 makes the same point in words: a threshold "far
        # outside the observed range" of the transition variable means the fitted model is
        # not satisfactory.
        transition_values = getattr(fit, "z", None)
        if transition_values is None or not np.size(transition_values):
            transition_values = fit.y
        low = (np.percentile(transition_values, thresholds["threshold_percentile_low"])
               if np.size(transition_values) else np.nan)
        high = (np.percentile(transition_values, thresholds["threshold_percentile_high"])
                if np.size(transition_values) else np.nan)
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


UNUSABLE = "unusable"
ILL_CONDITIONED = "ill_conditioned"
USABLE = "usable"


def covariance_condition(covariance: np.ndarray, config: Config) -> tuple[str, str]:
    """Classify a parameter covariance matrix. Returns (condition, detail)."""
    if covariance is None or not np.size(covariance):
        return USABLE, "no covariance supplied"
    if not np.isfinite(covariance).all():
        return UNUSABLE, "non-finite covariance"
    try:
        condition_number = float(np.linalg.cond(covariance))
    except np.linalg.LinAlgError:
        return UNUSABLE, "covariance not invertible"
    eigenvalues = np.linalg.eigvalsh((covariance + covariance.T) / 2)
    if eigenvalues.min() <= 0:
        return UNUSABLE, "covariance not positive definite"
    if condition_number > float(
        config.get("thresholds.covariance.ill_conditioned_condition_number")
    ):
        return ILL_CONDITIONED, f"condition number={condition_number:.3g}"
    return USABLE, f"condition number={condition_number:.3g}"


def apply_covariance_flags(
    record: FitRecord,
    covariance: np.ndarray,
    config: Config,
    *,
    required_for_inference: bool = False,
) -> FitRecord:
    """Covariance credibility, per Part 5 §8.1-§8.2 and decision D8.

    D8 makes an unusable covariance a **failure** only "when required for meaningful
    inference"; Part 5 §8.2 lists a singular or unstable nonlinear Hessian/covariance
    among the conditions that make a STAR model **fragile**, not failed; and §8.1 reserves
    MSAR failure for non-convergence, non-finite quantities, or an effectively
    unidentified regime, with a singular covariance being one *ingredient* of the
    empty-regime conjunction rather than a failure on its own.

    So the default here is fragility: the point estimates and the forecasts built from
    them stand, and what is unreliable is the asymptotic inference. A caller that genuinely
    depends on the covariance for a reported inference passes
    `required_for_inference=True` and gets the failure branch. Nothing in Part 6 reports
    an inference that rests on these matrices, so nothing passes it.
    """
    condition, detail = covariance_condition(covariance, config)
    if condition == UNUSABLE:
        record.add_flag(
            ReasonCode.SINGULAR_COV,
            Status.FAILED if required_for_inference else Status.FRAGILE,
            detail=detail,
        )
    elif condition == ILL_CONDITIONED:
        record.add_flag(ReasonCode.ILL_CONDITIONED_COV, Status.FRAGILE, detail=detail)
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
