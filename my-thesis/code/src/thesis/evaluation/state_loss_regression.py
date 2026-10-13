"""Ex-post state-dependent forecast-loss regression (decision M1).

    d_t = alpha + beta_rec * REC_t + beta_turn * TURN_t + u_t

with horizon-appropriate HAC inference. This tests whether **realized** relative forecast
loss differs across recessions and turning-point neighbourhoods.

It is deliberately **not** called a Giacomini-White conditional predictive-ability test.
Giacomini-White requires a test function measurable from the forecast-origin information
set; the NBER states used here are target-dated and were not knowable at the origin, and
NBER dates arrive with a long delay. Running the regression and calling it something it is
not would overstate what the design identifies, so the naming is kept honest and
Giacomini-White is cited in the methodology as the conditional-predictive-ability
reference rather than claimed as implemented.

Decision M12 fixes availability: inference is unavailable only on genuine numerical
failure, never because a state cell is merely small. Small cells are reported and flagged
as weak evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm

from ..core.schemas import TestResult
from .losses import SIGN_CONVENTION

SIGNIFICANCE = 0.05
LABEL = "ex-post state-dependent forecast-loss regression"


@dataclass
class StateLossResult:
    series: str
    model: str
    horizon: int
    available: bool
    n: int
    n_recession: int
    n_turning: int
    coefficients: dict[str, float] = field(default_factory=dict)
    std_errors: dict[str, float] = field(default_factory=dict)
    p_values: dict[str, float] = field(default_factory=dict)
    joint_wald: TestResult | None = None
    slopes_wald: TestResult | None = None
    hac_rule: str = ""
    unavailable_reason: str = ""
    weak_evidence: bool = False

    def to_row(self) -> dict[str, Any]:
        row = {
            "series": self.series,
            "model": self.model,
            "horizon": self.horizon,
            "label": LABEL,
            "inference_available": self.available,
            "unavailable_reason": self.unavailable_reason,
            "n": self.n,
            "n_recession": self.n_recession,
            "n_turning_window": self.n_turning,
            "weak_evidence_small_cells": self.weak_evidence,
            "hac_rule": self.hac_rule,
            "sign_convention": SIGN_CONVENTION,
        }
        for name in ("alpha", "beta_rec", "beta_turn"):
            row[name] = self.coefficients.get(name, float("nan"))
            row[f"{name}_se"] = self.std_errors.get(name, float("nan"))
            row[f"{name}_p"] = self.p_values.get(name, float("nan"))
        if self.joint_wald is not None:
            row["joint_wald_statistic"] = self.joint_wald.statistic
            row["joint_wald_p"] = self.joint_wald.p_value
        if self.slopes_wald is not None:
            row["slopes_wald_statistic"] = self.slopes_wald.statistic
            row["slopes_wald_p"] = self.slopes_wald.p_value
        return row


def _wald(results, restriction: np.ndarray, name: str, hypothesis: str, series: str,
          model: str) -> TestResult:
    """Wald test from an explicit restriction matrix.

    A matrix is used rather than a formula string because the design is a plain array, so
    parameter names would depend on statsmodels' naming conventions.
    """
    test = results.wald_test(restriction, use_f=False, scalar=True)
    statistic = float(np.asarray(test.statistic).ravel()[0])
    p_value = float(np.asarray(test.pvalue).ravel()[0])
    reject = p_value < SIGNIFICANCE
    return TestResult(
        name=name,
        null_hypothesis=hypothesis,
        statistic=statistic,
        p_value=p_value,
        reference="chi-squared Wald test with HAC covariance",
        decision_5pct="reject" if reject else "do not reject",
        implication=(
            "realized relative loss differs across the predeclared states"
            if reject else "no evidence that realized relative loss differs across states"
        ),
        series=series,
        model=model,
        tuning={"significance": SIGNIFICANCE},
    )


def state_loss_regression(
    differential: np.ndarray,
    recession: np.ndarray,
    turning: np.ndarray,
    horizon: int,
    *,
    series: str = "",
    model: str = "",
    small_cell_threshold: int = 10,
) -> StateLossResult:
    """Run the regression with Newey-West standard errors truncated at h-1."""
    d = np.asarray(differential, dtype=float)
    rec = np.asarray(recession, dtype=float)
    turn = np.asarray(turning, dtype=float)
    usable = np.isfinite(d) & np.isfinite(rec) & np.isfinite(turn)
    d, rec, turn = d[usable], rec[usable], turn[usable]
    n = d.size
    n_rec, n_turn = int(rec.sum()), int(turn.sum())
    hac_rule = f"Newey-West, Bartlett kernel, truncation h-1 = {max(horizon - 1, 0)}"

    result = StateLossResult(series=series, model=model, horizon=horizon, available=False,
                             n=n, n_recession=n_rec, n_turning=n_turn, hac_rule=hac_rule)
    # Decision M12: small cells are weak evidence, flagged but still estimated.
    result.weak_evidence = min(n_rec, n - n_rec, n_turn, n - n_turn) < small_cell_threshold

    if n < 5:
        result.unavailable_reason = f"only {n} paired observations"
        return result
    if rec.std() == 0 and turn.std() == 0:
        result.unavailable_reason = "neither state indicator varies in this sample"
        return result

    design = np.column_stack([np.ones(n), rec, turn])
    names = ["alpha", "beta_rec", "beta_turn"]
    keep = [0] + [i for i in (1, 2) if np.std(design[:, i]) > 0]
    if len(keep) < 3:
        dropped = [names[i] for i in (1, 2) if i not in keep]
        result.unavailable_reason = f"state indicator(s) without variation: {dropped}"
    design = design[:, keep]
    kept_names = [names[i] for i in keep]

    if np.linalg.matrix_rank(design) < design.shape[1]:
        result.unavailable_reason = "design matrix is rank deficient"
        return result

    try:
        fitted = sm.OLS(d, design).fit(cov_type="HAC",
                                       cov_kwds={"maxlags": max(horizon - 1, 0), "use_correction": True})
    except Exception as exc:
        result.unavailable_reason = f"estimation failed: {exc!r}"[:150]
        return result

    covariance = np.asarray(fitted.cov_params(), dtype=float)
    if not np.isfinite(covariance).all():
        result.unavailable_reason = "non-finite HAC covariance"
        return result

    result.coefficients = {name: float(v) for name, v in zip(kept_names, fitted.params)}
    result.std_errors = {name: float(v) for name, v in zip(kept_names, fitted.bse)}
    result.p_values = {name: float(v) for name, v in zip(kept_names, fitted.pvalues)}
    result.available = True

    try:
        k = len(kept_names)
        result.joint_wald = _wald(
            fitted, np.eye(k), "joint Wald (alpha = beta_rec = beta_turn = 0)",
            "equal average loss and no state dependence", series, model)
        slope_indices = [i for i, name in enumerate(kept_names) if name != "alpha"]
        if slope_indices:
            restriction = np.zeros((len(slope_indices), k))
            for row, column in enumerate(slope_indices):
                restriction[row, column] = 1.0
            result.slopes_wald = _wald(
                fitted, restriction, "state-dependence Wald (beta_rec = beta_turn = 0)",
                "realized relative loss does not depend on the states", series, model)
    except Exception as exc:
        result.unavailable_reason = f"Wald test failed: {exc!r}"[:150]
    return result
