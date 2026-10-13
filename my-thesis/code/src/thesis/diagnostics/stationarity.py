"""Stationarity and structural-break tests (Part 5 §3.2, decision D9).

The jury asked specifically why unemployment and the policy rate were modelled in levels
(P-02), so these tests are decision-relevant rather than decorative. Three complementary
procedures are used:

* **ADF** with a unit-root null;
* **KPSS** with the opposite, stationarity null, so the two tests ask complementary
  questions rather than duplicating one;
* **Zivot-Andrews** for the two disputed level series, allowing one endogenously estimated
  break, because a level series can look non-stationary purely because of a break.

Every result is returned as a `TestResult`, which forces the null, the reference
distribution, the decision rule and all tuning choices to travel with the number
(Part 5 §7.2, jury R1-13).
"""

from __future__ import annotations

import warnings
from typing import Any

import numpy as np
import pandas as pd
from statsmodels.tools.sm_exceptions import InterpolationWarning
from statsmodels.tsa.stattools import adfuller, kpss, zivot_andrews

from ..core.config import Config
from ..core.schemas import TestResult

SIGNIFICANCE = 0.05


def _maxlag(frequency: str, config: Config, test: str) -> int:
    return int(config.get(f"stationarity.{test}.maxlag.{frequency}"))


def adf_test(
    series: pd.Series,
    frequency: str,
    config: Config,
    *,
    regression: str | None = None,
    label: str = "",
) -> TestResult:
    """Augmented Dickey-Fuller test. H0: unit root."""
    settings = config.get("stationarity.adf")
    regression = regression or settings["regression"]
    maxlag = _maxlag(frequency, config, "adf")
    values = series.dropna().to_numpy(dtype=float)

    # The return shape is pinned explicitly: statsmodels plans to change its default,
    # and a reproducible pipeline must not depend on which version is installed.
    statistic, p_value, used_lag, n_obs, critical, *_ = adfuller(
        values,
        regression=regression,
        autolag=settings["autolag"],
        maxlag=maxlag,
        result_object=False,
    )
    reject = p_value < SIGNIFICANCE
    return TestResult(
        name=f"Augmented Dickey-Fuller{f' ({label})' if label else ''}",
        null_hypothesis="the series has a unit root",
        statistic=float(statistic),
        p_value=float(p_value),
        reference="Dickey-Fuller distribution (MacKinnon approximate p-value)",
        decision_5pct="reject" if reject else "do not reject",
        implication=(
            "stationary around the included deterministic terms"
            if reject
            else "a unit root cannot be rejected"
        ),
        series=str(series.name or ""),
        tuning={
            "regression": regression,
            "autolag": settings["autolag"],
            "maxlag": maxlag,
            "used_lag": int(used_lag),
            "n_obs": int(n_obs),
            "significance": SIGNIFICANCE,
        },
        extra={f"critical_{k}": float(v) for k, v in critical.items()},
    )


def kpss_test(
    series: pd.Series,
    frequency: str,
    config: Config,
    *,
    regression: str | None = None,
    label: str = "",
) -> TestResult:
    """KPSS test. H0: stationarity.

    The library returns p-values interpolated from a finite table, so a result at the
    table edge is flagged: reporting "p = 0.01" without saying it is a bound would
    overstate precision.
    """
    settings = config.get("stationarity.kpss")
    regression = regression or settings["regression"]
    values = series.dropna().to_numpy(dtype=float)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", InterpolationWarning)
        statistic, p_value, lags, critical = kpss(
            values, regression=regression, nlags=settings["nlags"], result_object=False
        )
    truncated = any(issubclass(w.category, InterpolationWarning) for w in caught)
    reject = p_value < SIGNIFICANCE
    return TestResult(
        name=f"KPSS{f' ({label})' if label else ''}",
        null_hypothesis="the series is stationary around the included deterministic terms",
        statistic=float(statistic),
        p_value=float(p_value),
        reference="Kwiatkowski-Phillips-Schmidt-Shin table (interpolated p-value)",
        decision_5pct="reject" if reject else "do not reject",
        implication=(
            "stationarity is rejected, which is evidence of a unit root"
            if reject
            else "stationarity is not rejected"
        ),
        series=str(series.name or ""),
        tuning={
            "regression": regression,
            "nlags_rule": settings["nlags"],
            "bandwidth_lags": int(lags),
            "significance": SIGNIFICANCE,
            "p_value_at_table_bound": truncated,
        },
        extra={f"critical_{k}": float(v) for k, v in critical.items()},
    )


def zivot_andrews_test(
    series: pd.Series, frequency: str, config: Config, *, label: str = ""
) -> TestResult:
    """Zivot-Andrews test. H0: unit root without an endogenous break.

    Critical values come from the implementation for the specification actually used
    (decision D9 forbids hard-coding an approximate generic value). The estimated break
    date is reported and plotted on the level series.
    """
    settings = config.get("stationarity.zivot_andrews")
    clean = series.dropna()
    values = clean.to_numpy(dtype=float)

    statistic, p_value, critical, used_lag, break_index = zivot_andrews(
        values,
        trim=float(settings["trim"]),
        maxlag=_maxlag(frequency, config, "zivot_andrews"),
        regression=settings["regression"],
        autolag=settings["autolag"],
    )
    break_date = pd.DatetimeIndex(clean.index)[int(break_index)]
    reject = p_value < SIGNIFICANCE
    return TestResult(
        name=f"Zivot-Andrews{f' ({label})' if label else ''}",
        null_hypothesis="the series has a unit root with no structural break",
        statistic=float(statistic),
        p_value=float(p_value),
        reference=(
            "Zivot-Andrews distribution for the break-in-intercept-and-trend "
            "specification, critical values from the implementation used"
        ),
        decision_5pct="reject" if reject else "do not reject",
        implication=(
            "trend/level stationary once one endogenous break is allowed"
            if reject
            else "a unit root cannot be rejected even allowing one break"
        ),
        series=str(series.name or ""),
        tuning={
            "regression": settings["regression"],
            "trim": float(settings["trim"]),
            "autolag": settings["autolag"],
            "maxlag": _maxlag(frequency, config, "zivot_andrews"),
            "used_lag": int(used_lag),
            "significance": SIGNIFICANCE,
        },
        extra={
            "break_date": break_date.strftime("%Y-%m-%d"),
            "break_index": int(break_index),
            **{f"critical_{k}": float(v) for k, v in critical.items()},
        },
    )


def transformation_verification(
    level: pd.Series, transformed: pd.Series, frequency: str, config: Config
) -> list[TestResult]:
    """Part 5 §3.3: show, rather than assume, why the growth transformation is used.

    ADF and KPSS are reported on the log level and again on the transformed series. When
    the configuration enables it (decision T2), constant-plus-trend variants are added for
    the log level as a clearly labelled extra diagnostic; they may not change any
    predeclared baseline decision.
    """
    results = [
        adf_test(level, frequency, config, label="log level"),
        kpss_test(level, frequency, config, label="log level"),
        adf_test(transformed, frequency, config, label="transformed"),
        kpss_test(transformed, frequency, config, label="transformed"),
    ]
    if config.get("stationarity.extra_trend_diagnostic", False):
        results.extend(
            [
                adf_test(
                    level, frequency, config, regression="ct",
                    label="log level, constant and trend; diagnostic only",
                ),
                kpss_test(
                    level, frequency, config, regression="ct",
                    label="log level, constant and trend; diagnostic only",
                ),
            ]
        )
    return results


def results_to_frame(results: list[TestResult]) -> pd.DataFrame:
    """Flatten test results into the standardized T2.2 table shape."""
    return pd.DataFrame([result.to_row() for result in results])
