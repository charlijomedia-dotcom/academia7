"""First differences and level reconstruction for rate variables.

UNRATE and FEDFUNDS are already percentages, so Part 5 §2.3 does not log them. Their
level-versus-difference representation is decided by the predeclared stationarity rule
(§3.4). When the modelled target is a difference, policy-facing figures reconstruct the
level from the last observed level, while formal predictive tests stay on the modelled
stationary target (§3.4, decision M6).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def first_difference(series: pd.Series) -> pd.Series:
    """Delta x_t = x_t - x_{t-1}, with NaN propagated rather than filled."""
    values = series.to_numpy(dtype=float)
    out = np.full_like(values, np.nan, dtype=float)
    out[1:] = values[1:] - values[:-1]
    return pd.Series(out, index=series.index, name=series.name)


def reconstruct_level_path(last_level: float, difference_path: np.ndarray) -> np.ndarray:
    """Rebuild a level path from a last observed level and a path of differences.

    For an h-step forecast of a differenced target, the implied level forecast is the
    last observed level plus the cumulative sum of the forecast differences.
    """
    differences = np.asarray(difference_path, dtype=float)
    return float(last_level) + np.cumsum(differences)


def level_forecast_from_differences(
    last_level: float, difference_forecasts: np.ndarray, horizon: int
) -> float:
    """Level forecast at horizon h implied by h one-period difference forecasts."""
    path = reconstruct_level_path(last_level, difference_forecasts[:horizon])
    if path.size < horizon:
        raise ValueError(
            f"need {horizon} difference forecasts to reconstruct the level at h={horizon}, "
            f"got {difference_forecasts.size}"
        )
    return float(path[horizon - 1])
