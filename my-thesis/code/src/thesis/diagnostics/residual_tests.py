"""In-sample residual diagnostics (Part 5 §7.1-§7.3).

Ljung-Box, ARCH-LM and Jarque-Bera, each returned in the standardized `TestResult` form so
the null, reference distribution and decision rule travel with the statistic (R1-13).

Degrees of freedom follow decision D1: the AR parameter count for AR, p+q for ARMA, and
**no mechanical correction** for the nonlinear models, whose Ljung-Box results are
diagnostic and whose df convention is documented on the row rather than assumed.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch

from ..core.config import Config
from ..core.schemas import TestResult

SIGNIFICANCE = 0.05


def ljung_box(
    residuals: np.ndarray,
    lag: int,
    *,
    model_dof: int = 0,
    dof_convention: str = "none_documented",
    series: str = "",
    model: str = "",
) -> TestResult:
    """Ljung-Box test for residual autocorrelation. H0: no autocorrelation up to `lag`."""
    values = np.asarray(residuals, dtype=float)
    values = values[np.isfinite(values)]
    usable_dof = model_dof if lag > model_dof else 0
    table = acorr_ljungbox(values, lags=[lag], model_df=usable_dof, return_df=True)
    statistic = float(table["lb_stat"].iloc[0])
    p_value = float(table["lb_pvalue"].iloc[0])
    reject = p_value < SIGNIFICANCE
    return TestResult(
        name=f"Ljung-Box({lag})",
        null_hypothesis=f"no residual autocorrelation up to lag {lag}",
        statistic=statistic,
        p_value=p_value,
        reference=f"chi-squared({max(lag - usable_dof, 1)})",
        decision_5pct="reject" if reject else "do not reject",
        implication=(
            "residual autocorrelation remains, so the specification is diagnostically weak"
            if reject
            else "no evidence of remaining residual autocorrelation"
        ),
        series=series,
        model=model,
        tuning={
            "lag": lag,
            "model_df": usable_dof,
            "df_convention": dof_convention,
            "significance": SIGNIFICANCE,
        },
    )


def arch_lm(
    residuals: np.ndarray, lag: int, *, series: str = "", model: str = ""
) -> TestResult:
    """Engle's ARCH-LM test. H0: homoskedastic residuals (no ARCH up to `lag`)."""
    values = np.asarray(residuals, dtype=float)
    values = values[np.isfinite(values)]
    # Return shape pinned explicitly for reproducibility across statsmodels versions.
    statistic, p_value, _, _ = het_arch(values, nlags=lag, result_object=False)
    reject = p_value < SIGNIFICANCE
    return TestResult(
        name=f"ARCH-LM({lag})",
        null_hypothesis=f"no autoregressive conditional heteroskedasticity up to lag {lag}",
        statistic=float(statistic),
        p_value=float(p_value),
        reference=f"chi-squared({lag})",
        decision_5pct="reject" if reject else "do not reject",
        implication=(
            "conditional heteroskedasticity is present, which triggers the "
            "ARMA-GARCH(1,1) variance diagnostic"
            if reject
            else "no evidence of conditional heteroskedasticity"
        ),
        series=series,
        model=model,
        tuning={"lag": lag, "significance": SIGNIFICANCE},
    )


def jarque_bera(residuals: np.ndarray, *, series: str = "", model: str = "") -> TestResult:
    """Jarque-Bera normality test.

    Reported because the reviewer asked for clear diagnostics, but Part 5 §7.4 is explicit
    that non-normal residuals alone do not disqualify a point-forecast model.
    """
    values = np.asarray(residuals, dtype=float)
    values = values[np.isfinite(values)]
    statistic, p_value = stats.jarque_bera(values)
    reject = p_value < SIGNIFICANCE
    return TestResult(
        name="Jarque-Bera",
        null_hypothesis="residuals are normally distributed",
        statistic=float(statistic),
        p_value=float(p_value),
        reference="chi-squared(2)",
        decision_5pct="reject" if reject else "do not reject",
        implication=(
            "residuals are non-normal; descriptive only, and not a disqualification for "
            "point forecasting (Part 5 §7.4)"
            if reject
            else "normality is not rejected"
        ),
        series=series,
        model=model,
        tuning={"significance": SIGNIFICANCE},
    )


def _dof_for(model: str, config: Config, order: int, ma_order: int = 0) -> tuple[int, str]:
    """Decision D1 degrees-of-freedom convention by model family."""
    conventions = config.get("diagnostics.ljung_box_df")
    if model.startswith("AR") and not model.startswith("ARMA"):
        return order, conventions["ar"]
    if model.startswith("ARMA"):
        return order + ma_order, conventions["arma"]
    return 0, conventions["nonlinear"]


def adequacy_suite(
    residuals: np.ndarray,
    frequency: str,
    config: Config,
    *,
    model: str,
    series: str = "",
    order: int = 0,
    ma_order: int = 0,
) -> list[TestResult]:
    """The full §7.3 residual battery for one fitted model."""
    lags = config.get(f"diagnostics.ljung_box_lags.{frequency}")
    arch_lag = int(config.get(f"diagnostics.arch_lm_lags.{frequency}"))
    model_dof, convention = _dof_for(model, config, order, ma_order)
    results = [
        ljung_box(residuals, int(lag), model_dof=model_dof, dof_convention=convention,
                  series=series, model=model)
        for lag in lags
    ]
    results.append(arch_lm(residuals, arch_lag, series=series, model=model))
    if config.get("diagnostics.jarque_bera", True):
        results.append(jarque_bera(residuals, series=series, model=model))
    return results


def primary_ljung_box(results: list[TestResult], frequency: str, config: Config) -> TestResult:
    """The primary Ljung-Box result used by the selection and adequacy rules (D1)."""
    primary_lag = int(config.get(f"specification.residual_screen.primary_lag.{frequency}"))
    for result in results:
        if result.name == f"Ljung-Box({primary_lag})":
            return result
    raise KeyError(f"no Ljung-Box result at the primary lag {primary_lag}")
