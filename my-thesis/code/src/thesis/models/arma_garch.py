"""ARMA(p,q)-GARCH(1,1), the conditional-variance diagnostic (Part 5 §5.3).

Prof. Verne raised ARCH/GARCH as a classical family, so it is addressed empirically rather
than dismissed. It is **not** a point-forecast competitor: GARCH enriches the variance
equation, which is a different scientific object from a new conditional-mean mechanism.
Decision M9 therefore keeps it out of the horse race and out of the Model Confidence Set
while still running it through the same rolling chronology.

Estimated jointly by Gaussian quasi-maximum likelihood, because a two-step fit would leave
the mean forecast identical to plain ARMA by construction and could not answer whether the
mean forecast actually changes.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from ..core.schemas import FitRecord, ReasonCode, Status


def _recursions(theta, y, p, q):
    """ARMA residual recursion and GARCH(1,1) variance recursion."""
    c = theta[0]
    ar = theta[1 : 1 + p]
    ma = theta[1 + p : 1 + p + q]
    omega, alpha, beta = theta[1 + p + q :]
    n = y.size
    e = np.zeros(n)
    for t in range(n):
        mean = c
        for j in range(1, p + 1):
            mean += ar[j - 1] * (y[t - j] if t - j >= 0 else c)
        for j in range(1, q + 1):
            mean += ma[j - 1] * (e[t - j] if t - j >= 0 else 0.0)
        e[t] = y[t] - mean
    h = np.empty(n)
    h[0] = max(np.var(e), 1e-10)
    for t in range(1, n):
        h[t] = omega + alpha * e[t - 1] ** 2 + beta * h[t - 1]
        if not np.isfinite(h[t]) or h[t] <= 0:
            h[t] = 1e-10
    return e, h


def _negative_loglik(theta, y, p, q):
    omega, alpha, beta = theta[1 + p + q :]
    if omega <= 0 or alpha < 0 or beta < 0 or alpha + beta >= 0.999:
        return 1e12
    e, h = _recursions(theta, y, p, q)
    if not np.isfinite(e).all() or not np.isfinite(h).all():
        return 1e12
    return float(0.5 * np.sum(np.log(2 * np.pi * h) + e**2 / h))


@dataclass
class ARMAGARCHFit:
    order: tuple[int, int]
    params: dict[str, float]
    residuals: np.ndarray
    conditional_variance: np.ndarray
    standardized_residuals: np.ndarray
    persistence: float
    loglik: float
    aic: float
    bic: float
    n_obs: int
    record: FitRecord
    _y: np.ndarray = None

    def forecast_mean(self, horizon: int = 1) -> np.ndarray:
        """Iterated conditional-mean forecast, for the M9 'did the mean change?' check."""
        p, q = self.order
        c = self.params["const"]
        ar = np.array([self.params[f"ar{j}"] for j in range(1, p + 1)])
        ma = np.array([self.params[f"ma{j}"] for j in range(1, q + 1)])
        y = list(self._y)
        e = list(self.residuals)
        out = np.empty(horizon)
        for step in range(horizon):
            mean = c
            for j in range(1, p + 1):
                mean += ar[j - 1] * y[-j]
            for j in range(1, q + 1):
                mean += ma[j - 1] * (e[-j] if step < q else 0.0)
            out[step] = mean
            y.append(mean)
            e.append(0.0)
        return out


def fit_arma_garch(
    y: pd.Series, order: tuple[int, int] = (1, 1), *, series: str = "", refit_date: str = ""
) -> ARMAGARCHFit:
    """Joint Gaussian QML estimation of ARMA(p,q)-GARCH(1,1)."""
    started = time.perf_counter()
    p, q = order
    values = y.to_numpy(dtype=float)
    record = FitRecord(
        series=series or (y.name or ""), model="ARMA-GARCH",
        spec_label=f"ARMA({p},{q})-GARCH(1,1)", spec_hash="",
        window_start=str(pd.DatetimeIndex(y.index)[0].date()),
        window_end=str(pd.DatetimeIndex(y.index)[-1].date()),
        refit_date=refit_date, converged=False,
    )

    variance = float(np.var(values, ddof=1))
    theta0 = np.concatenate([
        [float(values.mean())], np.full(p, 0.2), np.full(q, 0.2),
        [variance * 0.1, 0.1, 0.8],
    ])
    bounds = ([(None, None)] + [(-0.99, 0.99)] * (p + q)
              + [(1e-10, None), (0.0, 0.999), (0.0, 0.999)])
    try:
        result = minimize(_negative_loglik, theta0, args=(values, p, q),
                          method="L-BFGS-B", bounds=bounds, options={"maxiter": 500})
    except Exception as exc:
        record.add_flag(ReasonCode.NONCONVERGENCE, Status.FAILED, detail=repr(exc)[:150])
        record.wall_seconds = time.perf_counter() - started
        return ARMAGARCHFit(order, {}, np.empty(0), np.empty(0), np.empty(0), np.nan,
                            np.nan, np.nan, np.nan, 0, record, values)

    e, h = _recursions(result.x, values, p, q)
    omega, alpha, beta = result.x[1 + p + q :]
    params = {
        "const": float(result.x[0]),
        **{f"ar{j}": float(result.x[j]) for j in range(1, p + 1)},
        **{f"ma{j}": float(result.x[p + j]) for j in range(1, q + 1)},
        "omega": float(omega), "alpha": float(alpha), "beta": float(beta),
    }
    n_params = result.x.size
    loglik = float(-result.fun)
    record.converged = bool(result.success)
    record.optimizer_message = str(result.message)[:200]
    record.loglik = loglik
    record.aic = float(-2 * loglik + 2 * n_params)
    record.bic = float(-2 * loglik + n_params * np.log(values.size))
    record.n_obs = int(values.size)
    record.params = params
    record.diagnostics["variance_persistence"] = float(alpha + beta)
    record.wall_seconds = time.perf_counter() - started
    if not result.success:
        record.add_flag(ReasonCode.NONCONVERGENCE, Status.FAILED, detail=str(result.message)[:120])

    return ARMAGARCHFit(
        order=order, params=params, residuals=e, conditional_variance=h,
        standardized_residuals=e / np.sqrt(h), persistence=float(alpha + beta),
        loglik=loglik, aic=record.aic, bic=record.bic, n_obs=int(values.size),
        record=record, _y=values,
    )
