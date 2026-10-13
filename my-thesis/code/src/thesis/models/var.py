"""Monthly VAR, the focused multivariate robustness block (Part 5 §6.1).

The jury's objection is that own-history models cannot show whether predictive
information is transmitted through other macro variables. The VAR answers that specific
alternative explanation; it is not a second central model family.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..core.schemas import FitRecord, ReasonCode, Status


@dataclass
class VARFit:
    order: int
    names: list[str]
    coefficients: np.ndarray      # (k, 1 + k*p): intercept then lag blocks
    residuals: np.ndarray
    n_obs: int
    loglik: float
    aic: float
    bic: float
    sigma: np.ndarray
    record: FitRecord
    _history: np.ndarray = None

    def companion_moduli(self) -> np.ndarray:
        k, p = len(self.names), self.order
        A = self.coefficients[:, 1:].reshape(k, p, k).transpose(0, 1, 2)
        companion = np.zeros((k * p, k * p))
        companion[:k] = np.hstack([A[:, j, :] for j in range(p)])
        if p > 1:
            companion[k:, : k * (p - 1)] = np.eye(k * (p - 1))
        return np.abs(np.linalg.eigvals(companion))

    @property
    def is_stable(self) -> bool:
        moduli = self.companion_moduli()
        return bool(moduli.size == 0 or moduli.max() < 1.0)

    def forecast(self, history: np.ndarray, horizon: int = 1) -> np.ndarray:
        """Iterated forecasts for every variable. Returns (horizon, k)."""
        k, p = len(self.names), self.order
        recent = [history[-(j + 1)] for j in range(p)]        # y_{t}, y_{t-1}, ...
        out = np.empty((horizon, k))
        for step in range(horizon):
            x = np.concatenate([[1.0]] + recent[:p])
            prediction = self.coefficients @ x
            out[step] = prediction
            recent.insert(0, prediction)
        return out


def fit_var(
    data: pd.DataFrame,
    order: int,
    *,
    refit_date: str = "",
    spec_hash: str = "",
) -> VARFit:
    """Estimate a VAR(p) by equation-by-equation OLS on the balanced sample."""
    started = time.perf_counter()
    names = list(data.columns)
    values = data.to_numpy(dtype=float)
    k = len(names)
    n = values.shape[0]
    rows = np.arange(order, n)
    X = np.column_stack([np.ones(rows.size)] + [values[rows - j] for j in range(1, order + 1)])
    Y = values[rows]

    record = FitRecord(
        series="+".join(names), model="VAR", spec_label=f"p={order}", spec_hash=spec_hash,
        window_start=str(pd.DatetimeIndex(data.index)[0].date()),
        window_end=str(pd.DatetimeIndex(data.index)[-1].date()),
        refit_date=refit_date, converged=True,
    )

    coefficients, *_ = np.linalg.lstsq(X, Y, rcond=None)
    coefficients = coefficients.T                                   # (k, 1 + k*p)
    residuals = Y - X @ coefficients.T
    n_obs = rows.size
    sigma = residuals.T @ residuals / n_obs
    sign, logdet = np.linalg.slogdet(sigma)
    loglik = float(-0.5 * n_obs * (k * (np.log(2 * np.pi) + 1) + logdet)) if sign > 0 else np.nan
    n_params = k * (1 + k * order)
    record.loglik = loglik
    record.aic = float(-2 * loglik + 2 * n_params) if np.isfinite(loglik) else np.nan
    record.bic = float(-2 * loglik + n_params * np.log(n_obs)) if np.isfinite(loglik) else np.nan
    record.n_obs = n_obs
    record.wall_seconds = time.perf_counter() - started

    fit = VARFit(order, names, coefficients, residuals, n_obs, loglik,
                 record.aic, record.bic, sigma, record, values)
    if not fit.is_stable:
        record.add_flag(ReasonCode.UNSTABLE_AR, Status.FAILED,
                        detail=float(fit.companion_moduli().max()))
    if not np.isfinite(coefficients).all():
        record.add_flag(ReasonCode.NONFINITE, Status.FAILED)
    return fit
