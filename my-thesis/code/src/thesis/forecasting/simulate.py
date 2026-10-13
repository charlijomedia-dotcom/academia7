"""Simulation-based multi-step forecasts for STAR (decision M2).

Naive iteration of a nonlinear model (plugging point forecasts back in and setting future
shocks to zero) is the "skeleton" path, and it is **not** the conditional mean. Decision M2
therefore requires the Teräsvirta-van Dijk-Medeiros approach: resample centred residuals
from the estimation window, propagate the nonlinear recursion, and average.

The skeleton remains available as an explicitly labelled diagnostic, never as the headline
longer-horizon forecast.
"""

from __future__ import annotations

import numpy as np

from ..core import seeds
from ..models.star import transition


def star_skeleton_forecast(fit, history: np.ndarray, horizon: int) -> np.ndarray:
    """Deterministic iteration with future shocks set to zero. Diagnostic only."""
    values = list(np.asarray(history, dtype=float))
    out = np.empty(horizon)
    for step in range(horizon):
        prediction = fit.forecast_one(np.asarray(values))
        out[step] = prediction
        values.append(prediction)
    return out


def star_bootstrap_forecast(
    fit,
    history: np.ndarray,
    horizon: int,
    *,
    paths: int,
    seed_key,
    master_seed: int,
) -> tuple[np.ndarray, dict]:
    """Residual-bootstrap approximation to the iterated conditional mean.

    Returns the h-step means and the seed provenance, so a reported forecast can always be
    traced to the exact random stream that produced it.
    """
    values = np.asarray(history, dtype=float)
    residuals = np.asarray(fit.residuals, dtype=float)
    residuals = residuals[np.isfinite(residuals)]
    if residuals.size == 0:
        return np.full(horizon, np.nan), {"paths": paths, "error": "no usable residuals"}
    centred = residuals - residuals.mean()

    rng = seeds.generator(seed_key, master_seed)
    order, delay = fit.order, fit.delay
    needed = max(order, delay)
    # One row per simulated path, holding the tail of history each path needs.
    state = np.tile(values[-needed:], (paths, 1))

    means = np.empty(horizon)
    for step in range(horizon):
        lags = state[:, -order:][:, ::-1]                       # y_{t-1}, ..., y_{t-p}
        design = np.column_stack([np.ones(paths), lags])
        z = state[:, -delay]
        g = transition(z, fit.gamma, fit.c, fit.scale, fit.kind)
        deterministic = design @ fit.linear + g * (design @ fit.nonlinear)
        shocks = rng.choice(centred, size=paths, replace=True)
        draws = deterministic + shocks
        means[step] = float(np.mean(draws))
        state = np.column_stack([state, draws])

    provenance = seeds.describe(seed_key, master_seed)
    provenance.update({"paths": paths, "method": "residual_bootstrap"})
    return means, provenance
