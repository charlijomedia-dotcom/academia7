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
from scipy.special import expit
import pandas as pd
from scipy.optimize import minimize

from ..core.schemas import FitRecord, ReasonCode, Status
from .flags import apply_covariance_flags
from .optimize import (StartAttempt, covariance_from_hessian,
                       numerical_jacobian, select_best, standard_errors)

LSTAR = "LSTAR"
ESTAR = "ESTAR"


def transition(z: np.ndarray, gamma: float, c: float, scale: float, kind: str) -> np.ndarray:
    """Transition function on the standardized distance (z - c) / s_z.

    The logistic is evaluated with `scipy.special.expit`, which is the same function
    computed without the overflow that `1/(1+exp(-x))` hits for large |x|. The limiting
    values 0 and 1 are the right answers there, so the only thing the naive form adds is
    a stream of overflow warnings during optimization at large gamma.
    """
    standardized = (z - c) / scale
    if kind == LSTAR:
        return expit(gamma * standardized)
    if kind == ESTAR:
        return -np.expm1(-gamma * standardized**2)
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
    #: The transition variable y_{t-d} on exactly the estimation rows. The threshold c
    #: lives on this scale, so the §8.2 range check must use it and not the raw series.
    z: np.ndarray = field(default_factory=lambda: np.empty(0))
    covariance: np.ndarray = field(default_factory=lambda: np.empty((0, 0)))

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

    attempts: list[StartAttempt] = []
    for start in starts:
        label = f"gamma0={start[0]},c0={start[1]:.6g}"
        try:
            result = minimize(
                lambda params: _sse(params, dep, X, z, scale, kind)[0],
                x0=np.array(start, dtype=float),
                method="L-BFGS-B",
                bounds=[bounds_gamma, (c_low, c_high)],
            )
        except Exception as exc:
            attempts.append(StartAttempt(label, float("inf"), False, repr(exc)[:200], None))
            continue
        attempts.append(StartAttempt(
            label, float(result.fun), bool(result.success), str(result.message), result.x))

    # Teräsvirta (1994) §5 treats non-convergence as a reason to change the estimation
    # strategy, not as licence to adopt the lowest point reached. So the selection prefers
    # the best start that actually converged, and every attempt is kept for the audit.
    outcome = select_best(attempts)
    record.diagnostics.update(outcome.summary())
    best = outcome.chosen
    if best is not None:
        record.start_used = best.label

    if best is None:
        record.add_flag(ReasonCode.NONCONVERGENCE, Status.FAILED, detail="no start converged")
        record.wall_seconds = time.perf_counter() - started
        return STARFit(kind=kind, order=order, delay=delay, gamma=np.nan, c=np.nan,
                       scale=scale, linear=np.empty(0), nonlinear=np.empty(0),
                       residuals=np.empty(0), fitted=np.empty(0), G=np.empty(0),
                       n_obs=0, sigma2=np.nan, loglik=np.nan, aic=np.nan, bic=np.nan,
                       record=record, z=z)

    gamma, c = float(best.x[0]), float(best.x[1])
    sse, coef, g = _sse(best.x, dep, X, z, scale, kind)
    k = coef.size
    n = dep.size
    residuals = dep - np.column_stack([X, X * g[:, None]]) @ coef
    sigma2 = float(sse / n)
    loglik = float(-0.5 * n * (np.log(2 * np.pi) + np.log(sigma2) + 1.0))

    record.converged = bool(best.converged)
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
    if not best.converged:
        record.add_flag(ReasonCode.NONCONVERGENCE, Status.FAILED, detail=str(best.message)[:120])

    # Parameter uncertainty for the conditional least-squares estimator. Teräsvirta
    # (1994) §5 reads the estimated standard deviations as a credibility signal —
    # "excessively large standard deviation estimates for coefficient estimators (other
    # than gamma) suggest that the model contains redundant parameters" — and Part 5 §8.2
    # requires singular or ill-conditioned nonlinear covariance matrices to be flagged.
    # The covariance is the Gauss-Newton form sigma^2 (J'J)^-1 over the **full** parameter
    # vector (gamma, c, and the concentrated linear coefficients), because concentrating
    # the linear part out is an estimation device, not a claim that it is known.
    covariance = np.empty((0, 0))
    full_theta = np.concatenate([[gamma, c], coef])
    n_params_full = full_theta.size

    def _residual_vector(theta: np.ndarray) -> np.ndarray:
        g_local = transition(z, float(theta[0]), float(theta[1]), scale, kind)
        design = np.column_stack([X, X * g_local[:, None]])
        return dep - design @ theta[2:]

    if n > n_params_full:
        jacobian = numerical_jacobian(_residual_vector, full_theta)
        gram = jacobian.T @ jacobian
        residual_variance = float(sse / (n - n_params_full))
        inverse, reason = covariance_from_hessian(gram)
        if reason:
            record.diagnostics["covariance_status"] = reason
            record.add_flag(ReasonCode.SINGULAR_COV, Status.FRAGILE, detail=reason)
        else:
            covariance = residual_variance * inverse
            names = (["gamma", "c"]
                     + [f"phi{i}" for i in range(X.shape[1])]
                     + [f"theta{i}" for i in range(X.shape[1])])
            errors = standard_errors(covariance)
            record.std_errors = {name: float(value)
                                 for name, value in zip(names, errors)}
            record.diagnostics["covariance_status"] = "ok"
            apply_covariance_flags(record, covariance, config)
    else:
        record.diagnostics["covariance_status"] = (
            f"only {n} observations for {n_params_full} parameters")

    return STARFit(
        kind=kind, order=order, delay=delay, gamma=gamma, c=c, scale=scale,
        linear=coef[: X.shape[1]], nonlinear=coef[X.shape[1]:],
        residuals=residuals, fitted=dep - residuals, G=g, n_obs=n, sigma2=sigma2,
        loglik=loglik, aic=record.aic, bic=record.bic, record=record,
        design=X, y=dep, z=z, covariance=covariance,
    )
