"""ARMA(p,q), the stronger classical benchmark (Part 5 §5.2).

Prof. Verne asked for a classical comparison that is not artificially weak, so a nonlinear
gain cannot be an artefact of omitting moving-average dynamics. Estimated by Gaussian
maximum likelihood with stationarity and invertibility enforced.
"""

from __future__ import annotations

import time
import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

from ..core.schemas import FitRecord, ReasonCode, Status


@dataclass
class ARMAFit:
    order: tuple[int, int]
    params: dict[str, float]
    residuals: np.ndarray
    fitted: np.ndarray
    n_obs: int
    loglik: float
    aic: float
    bic: float
    sigma2: float
    record: FitRecord
    _results: object = None

    @property
    def is_pure_ar(self) -> bool:
        return self.order[1] == 0

    @property
    def is_pure_ma(self) -> bool:
        return self.order[0] == 0

    def forecast(self, horizon: int = 1) -> np.ndarray:
        """Exact conditional mean forecast from the fitted state-space model."""
        return np.asarray(self._results.forecast(steps=horizon), dtype=float)


def fit_arma(
    y: pd.Series,
    order: tuple[int, int],
    *,
    series: str = "",
    refit_date: str = "",
    spec_hash: str = "",
) -> ARMAFit:
    """Estimate ARMA(p,q) with an intercept.

    Stationarity and invertibility are enforced during estimation, as Part 5 §5.2
    requires, so a fitted model that violates them cannot be produced silently.
    """
    started = time.perf_counter()
    p, q = order
    values = y.to_numpy(dtype=float)
    record = FitRecord(
        series=series or (y.name or ""),
        model="ARMA",
        spec_label=f"p={p},q={q}",
        spec_hash=spec_hash,
        window_start=str(pd.DatetimeIndex(y.index)[0].date()),
        window_end=str(pd.DatetimeIndex(y.index)[-1].date()),
        refit_date=refit_date,
        converged=False,
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = SARIMAX(
            values,
            order=(p, 0, q),
            trend="c",
            enforce_stationarity=True,
            enforce_invertibility=True,
        )
        try:
            results = model.fit(disp=False, maxiter=500)
        except Exception as exc:  # estimation genuinely failed
            record.add_flag(ReasonCode.NONCONVERGENCE, Status.FAILED, detail=repr(exc)[:200])
            record.optimizer_message = repr(exc)[:200]
            record.wall_seconds = time.perf_counter() - started
            return ARMAFit(order, {}, np.empty(0), np.empty(0), 0, np.nan, np.nan,
                           np.nan, np.nan, record)

    params = {name: float(value) for name, value in zip(results.param_names, results.params)}
    residuals = np.asarray(results.resid, dtype=float)
    record.converged = bool(results.mle_retvals.get("converged", True))
    record.loglik = float(results.llf)
    record.aic = float(results.aic)
    record.bic = float(results.bic)
    record.n_obs = int(results.nobs)
    record.params = params
    record.optimizer_message = str(results.mle_retvals.get("message", ""))[:200]
    record.wall_seconds = time.perf_counter() - started
    try:
        record.std_errors = {
            name: float(value) for name, value in zip(results.param_names, results.bse)
        }
    except Exception:
        record.add_flag(ReasonCode.SINGULAR_COV, Status.FRAGILE, detail="standard errors unavailable")

    if not record.converged:
        record.add_flag(ReasonCode.NONCONVERGENCE, Status.FAILED)
    if not np.isfinite(results.params).all():
        record.add_flag(ReasonCode.NONFINITE, Status.FAILED)
    # Decision M4: a selected pure-AR or pure-MA specification is allowed but flagged,
    # because it makes the "AR vs ARMA" comparison less of a contrast.
    if q == 0 or p == 0:
        record.diagnostics["degenerate_arma"] = "pure AR" if q == 0 else "pure MA"

    return ARMAFit(
        order=order,
        params=params,
        residuals=residuals,
        fitted=values - residuals,
        n_obs=int(results.nobs),
        loglik=float(results.llf),
        aic=float(results.aic),
        bic=float(results.bic),
        sigma2=float(params.get("sigma2", np.nan)),
        record=record,
        _results=results,
    )
