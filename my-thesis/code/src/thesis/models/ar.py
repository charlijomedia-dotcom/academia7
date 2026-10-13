"""AR(p), the primary classical benchmark (Part 5 §5.1).

    y_t = c + sum_{j=1}^p phi_j y_{t-j} + e_t

Estimated by OLS with an intercept. The model is deliberately plain: it is the benchmark
against which every nonlinear gain is measured, so it must be transparent and must not
quietly acquire features the methodology did not approve.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..core.schemas import FitRecord, ReasonCode, Status
from ..transforms.lags import LagDesign, lag_matrix


@dataclass
class ARFit:
    """A fitted AR(p)."""

    order: int
    params: np.ndarray            # [const, phi_1, ..., phi_p]
    residuals: np.ndarray
    fitted: np.ndarray
    n_obs: int
    loglik: float
    aic: float
    bic: float
    sigma2: float
    std_errors: np.ndarray
    design: LagDesign
    record: FitRecord

    @property
    def intercept(self) -> float:
        return float(self.params[0])

    @property
    def phi(self) -> np.ndarray:
        return self.params[1:]

    def companion_roots(self) -> np.ndarray:
        """Roots of the AR characteristic polynomial, as moduli of companion eigenvalues."""
        if self.order == 0:
            return np.empty(0)
        companion = np.zeros((self.order, self.order))
        companion[0] = self.phi
        if self.order > 1:
            companion[1:, :-1] = np.eye(self.order - 1)
        return np.abs(np.linalg.eigvals(companion))

    @property
    def is_stable(self) -> bool:
        roots = self.companion_roots()
        return bool(roots.size == 0 or roots.max() < 1.0)

    def forecast(self, history: pd.Series | np.ndarray, horizon: int = 1) -> np.ndarray:
        """Iterated multi-step forecast from the end of `history`.

        `history` must end at the forecast origin. Forecasts are produced by iterating the
        estimated dynamics, which is the approved multi-step method (Part 5 §9.4).
        """
        values = np.asarray(
            history.to_numpy(dtype=float) if isinstance(history, pd.Series) else history,
            dtype=float,
        )
        if self.order and values.size < self.order:
            raise ValueError(f"need at least {self.order} observations to forecast")
        recent = list(values[-self.order :]) if self.order else []
        out = np.empty(horizon, dtype=float)
        for step in range(horizon):
            prediction = self.intercept
            for j in range(self.order):
                prediction += self.phi[j] * recent[-(j + 1)]
            out[step] = prediction
            recent.append(prediction)
        return out


def fit_ar(
    y: pd.Series,
    order: int,
    *,
    series: str = "",
    refit_date: str = "",
    spec_hash: str = "",
) -> ARFit:
    """Estimate AR(p) by OLS on the supplied sample.

    Rows whose dependent value or any required lag is missing are excluded by
    `lag_matrix` and reported, so a data gap shrinks the estimation sample visibly instead
    of being filled in.
    """
    started = time.perf_counter()
    design = lag_matrix(y, order, include_const=True)
    n, k = design.X.shape
    if n <= k:
        raise ValueError(f"AR({order}) needs more than {k} usable observations, has {n}")

    params, *_ = np.linalg.lstsq(design.X, design.y, rcond=None)
    fitted = design.X @ params
    residuals = design.y - fitted
    sigma2 = float(residuals @ residuals / n)
    loglik = float(-0.5 * n * (np.log(2 * np.pi) + np.log(sigma2) + 1.0))
    aic = float(-2 * loglik + 2 * k)
    bic = float(-2 * loglik + k * np.log(n))

    xtx_inv = np.linalg.pinv(design.X.T @ design.X)
    std_errors = np.sqrt(np.clip(np.diag(xtx_inv) * sigma2 * n / max(n - k, 1), 0.0, None))

    record = FitRecord(
        series=series or (y.name or ""),
        model="AR",
        spec_label=f"p={order}",
        spec_hash=spec_hash,
        window_start=str(design.index[0].date()) if len(design.index) else "",
        window_end=str(design.index[-1].date()) if len(design.index) else "",
        refit_date=refit_date,
        converged=True,
        loglik=loglik,
        aic=aic,
        bic=bic,
        n_obs=n,
        params={"const": float(params[0]), **{f"ar{j}": float(params[j]) for j in range(1, order + 1)}},
        std_errors={"const": float(std_errors[0]),
                    **{f"ar{j}": float(std_errors[j]) for j in range(1, order + 1)}},
        wall_seconds=time.perf_counter() - started,
        diagnostics={"n_rows_dropped_incomplete": int(len(design.incomplete_index))},
    )

    fit = ARFit(
        order=order,
        params=params,
        residuals=residuals,
        fitted=fitted,
        n_obs=n,
        loglik=loglik,
        aic=aic,
        bic=bic,
        sigma2=sigma2,
        std_errors=std_errors,
        design=design,
        record=record,
    )
    if not fit.is_stable:
        record.add_flag(
            ReasonCode.UNSTABLE_AR,
            Status.FAILED,
            detail=float(fit.companion_roots().max()),
        )
    if not np.isfinite(params).all():
        record.add_flag(ReasonCode.NONFINITE, Status.FAILED)
    return fit
