"""Smooth-transition autoregression (Part 5 §5.6).

    y_t = phi'x_t + G(z_{t-d}; gamma, c) theta'x_t + e_t,     x_t = (1, y_{t-1}, ..., y_{t-p})'

G is logistic (LSTAR) or exponential (ESTAR), selected by the Teräsvirta sequence. The
transition argument is standardized, so gamma is dimensionless and comparable across
series (decision D5):

    LSTAR: G = 1 / (1 + exp(-gamma * (z - c) / s_z))
    ESTAR: G = 1 - exp(-gamma * ((z - c) / s_z)^2)

Estimation is conditional least squares: given (gamma, c) the model is linear in
(phi, theta), so the linear block is solved exactly by OLS and only two parameters are
searched numerically. That is both faster and far more stable than optimizing everything
at once.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from ..core.schemas import FitRecord, ReasonCode, Status

LSTAR = "LSTAR"
ESTAR = "ESTAR"


def transition(z: np.ndarray, gamma: float, c: float, scale: float, kind: str) -> np.ndarray:
    """Transition function on the standardized distance (z - c) / s_z."""
    standardized = (z - c) / scale
    if kind == LSTAR:
        return 1.0 / (1.0 + np.exp(-gamma * standardized))
    if kind == ESTAR:
        return 1.0 - np.exp(-gamma * standardized**2)
    raise ValueError(f"unknown transition type {kind!r}")


@dataclass
class STARFit:
    kind: str
    order: int
    delay: int
    gamma: float
    c: float
    scale: float
    linear: np.ndarray           # phi
    nonlinear: np.ndarray        # theta
    residuals: np.ndarray
    fitted: np.ndarray
    G: np.ndarray
    n_obs: int
    sigma2: float
    loglik: float
    aic: float
    bic: float
    record: FitRecord
    design: np.ndarray = field(default_factory=lambda: np.empty((0, 0)))
    y: np.ndarray = field(default_factory=lambda: np.empty(0))

    def forecast_one(self, history: np.ndarray) -> float:
        """One-step forecast given history ending at the forecast origin."""
        lags = history[-self.order:][::-1]
        x = np.concatenate([[1.0], lags])
        z = history[-self.delay]
        g = float(transition(np.array([z]), self.gamma, self.c, self.scale, self.kind)[0])
        return float(x @ self.linear + g * (x @ self.nonlinear))


def _design(y: np.ndarray, order: int, delay: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build (dependent, regressors, transition variable) aligned on common rows."""
    start = max(order, delay)
    n = y.size
    rows = np.arange(start, n)
    X = np.column_stack([np.ones(rows.size)] + [y[rows - j] for j in range(1, order + 1)])
    z = y[rows - delay]
    return y[rows], X, z


def _sse(params: np.ndarray, y: np.ndarray, X: np.ndarray, z: np.ndarray,
         scale: float, kind: str) -> tuple[float, np.ndarray, np.ndarray]:
    gamma, c = params
    if gamma <= 0:
        return np.inf, np.empty(0), np.empty(0)
    g = transition(z, gamma, c, scale, kind)
    W = np.column_stack([X, X * g[:, None]])
    coef, *_ = np.linalg.lstsq(W, y, rcond=None)
    residuals = y - W @ coef
    return float(residuals @ residuals), coef, g


def fit_star(
    y: pd.Series,
    order: int,
    delay: int,
    kind: str,
    config,
    *,
    series: str = "",
    refit_date: str = "",
    spec_hash: str = "",
    warm_start: tuple[float, float] | None = None,
) -> STARFit:
    """Estimate a STAR model by conditional least squares over (gamma, c)."""
    started = time.perf_counter()
    values = y.to_numpy(dtype=float)
    dep, X, z = _design(values, order, delay)
    scale = float(np.std(z, ddof=1)) or 1.0
    bounds_gamma = tuple(config.get("models.star.gamma_bounds"))
    c_low, c_high = float(np.min(z)), float(np.max(z))

    record = FitRecord(
        series=series or (y.name or ""),
        model="STAR",
        spec_label=f"{kind},p={order},d={delay}",
        spec_hash=spec_hash,
        window_start=str(pd.DatetimeIndex(y.index)[0].date()),
        window_end=str(pd.DatetimeIndex(y.index)[-1].date()),
        refit_date=refit_date,
        converged=False,
    )

    # Deterministic multi-start grid, plus the warm start when one is supplied (Comp §7).
    starts: list[tuple[float, float]] = []
    if warm_start is not None:
        starts.append((float(np.clip(warm_start[0], *bounds_gamma)),
                       float(np.clip(warm_start[1], c_low, c_high))))
    for gamma0 in (1.0, 5.0, 10.0, 50.0):
        for quantile in (0.25, 0.5, 0.75):
            starts.append((gamma0, float(np.quantile(z, quantile))))

    best = None
    for start in starts:
        try:
            result = minimize(
                lambda params: _sse(params, dep, X, z, scale, kind)[0],
                x0=np.array(start, dtype=float),
                method="L-BFGS-B",
                bounds=[bounds_gamma, (c_low, c_high)],
            )
        except Exception:
            continue
        if not np.isfinite(result.fun):
            continue
        if best is None or result.fun < best.fun:
            best = result
            record.start_used = f"gamma0={start[0]},c0={start[1]:.6g}"

    if best is None:
        record.add_flag(ReasonCode.NONCONVERGENCE, Status.FAILED, detail="no start converged")
        record.wall_seconds = time.perf_counter() - started
        return STARFit(kind, order, delay, np.nan, np.nan, scale, np.empty(0), np.empty(0),
                       np.empty(0), np.empty(0), np.empty(0), 0, np.nan, np.nan, np.nan,
                       np.nan, record)

    gamma, c = float(best.x[0]), float(best.x[1])
    sse, coef, g = _sse(best.x, dep, X, z, scale, kind)
    k = coef.size
    n = dep.size
    residuals = dep - np.column_stack([X, X * g[:, None]]) @ coef
    sigma2 = float(sse / n)
    loglik = float(-0.5 * n * (np.log(2 * np.pi) + np.log(sigma2) + 1.0))

    record.converged = bool(best.success)
    record.optimizer_message = str(best.message)[:200]
    record.loglik = loglik
    record.aic = float(-2 * loglik + 2 * (k + 2))
    record.bic = float(-2 * loglik + (k + 2) * np.log(n))
    record.n_obs = n
    record.params = {
        "gamma": gamma,
        "c": c,
        **{f"phi{i}": float(v) for i, v in enumerate(coef[: X.shape[1]])},
        **{f"theta{i}": float(v) for i, v in enumerate(coef[X.shape[1]:])},
    }
    record.wall_seconds = time.perf_counter() - started
    record.diagnostics.update(
        {"G_min": float(g.min()), "G_max": float(g.max()), "G_sd": float(g.std()),
         "transition_scale": scale}
    )
    if not best.success:
        record.add_flag(ReasonCode.NONCONVERGENCE, Status.FAILED, detail=str(best.message)[:120])

    return STARFit(
        kind=kind, order=order, delay=delay, gamma=gamma, c=c, scale=scale,
        linear=coef[: X.shape[1]], nonlinear=coef[X.shape[1]:],
        residuals=residuals, fitted=dep - residuals, G=g, n_obs=n, sigma2=sigma2,
        loglik=loglik, aic=record.aic, bic=record.bic, record=record,
        design=X, y=dep,
    )
