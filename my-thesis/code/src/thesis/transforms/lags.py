"""Lag matrix construction.

Comp §15 requires an explicit test of lag construction and of the rule that no future
observation may enter a predictor. Both properties live here: `lag_matrix` only ever
looks backwards, and rows containing a missing value are reported rather than silently
dropped, so a data gap becomes visible instead of quietly shrinking the sample.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class LagDesign:
    """A dependent vector and its lag matrix, with the rows that could not be formed."""

    y: np.ndarray
    X: np.ndarray
    index: pd.DatetimeIndex
    incomplete_index: pd.DatetimeIndex
    n_lags: int

    @property
    def n_obs(self) -> int:
        return self.y.shape[0]


def lag_matrix(series: pd.Series, n_lags: int, *, include_const: bool = True) -> LagDesign:
    """Build y_t and [1, y_{t-1}, ..., y_{t-p}] for an autoregression.

    Rows whose dependent value or any required lag is missing are excluded from the
    design and returned in `incomplete_index`. Nothing is interpolated or filled.
    """
    if n_lags < 0:
        raise ValueError(f"n_lags must be non-negative, got {n_lags}")
    values = series.to_numpy(dtype=float)
    index = pd.DatetimeIndex(series.index)
    n = values.size
    if n <= n_lags:
        raise ValueError(f"series of length {n} is too short for {n_lags} lags")

    rows = np.arange(n_lags, n)
    y_all = values[rows]
    lags = np.column_stack([values[rows - j] for j in range(1, n_lags + 1)]) if n_lags else np.empty((rows.size, 0))

    complete = np.isfinite(y_all)
    if n_lags:
        complete &= np.isfinite(lags).all(axis=1)

    design = lags[complete]
    if include_const:
        design = np.column_stack([np.ones(design.shape[0]), design])

    return LagDesign(
        y=y_all[complete],
        X=design,
        index=index[rows][complete],
        incomplete_index=index[rows][~complete],
        n_lags=n_lags,
    )


def last_window_lags(series: pd.Series, n_lags: int) -> np.ndarray:
    """The most recent `n_lags` values, ordered [y_t, y_{t-1}, ..., y_{t-p+1}].

    This is the predictor vector used to forecast the next observation from a given
    forecast origin. It raises if any required value is missing, because a forecast
    cannot be formed from an incomplete information set and must be recorded as a data
    gap rather than silently approximated.
    """
    if n_lags <= 0:
        return np.empty(0)
    values = series.to_numpy(dtype=float)
    if values.size < n_lags:
        raise ValueError(f"need {n_lags} observations, have {values.size}")
    recent = values[-n_lags:][::-1]
    if not np.isfinite(recent).all():
        missing = pd.DatetimeIndex(series.index[-n_lags:])[~np.isfinite(values[-n_lags:])]
        raise MissingPredictorError(
            f"predictor vector contains missing observation(s) at "
            f"{[d.strftime('%Y-%m-%d') for d in missing]}"
        )
    return recent


class MissingPredictorError(ValueError):
    """Raised when a forecast cannot be formed because a required lag is missing."""
