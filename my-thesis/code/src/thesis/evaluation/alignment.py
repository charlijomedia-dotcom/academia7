"""Common-date alignment (decision M7).

No model-eligibility percentage is invented. Instead:

* descriptive metrics use each model's own valid observations, with N reported;
* every pairwise comparison uses the intersection of that pair's valid dates;
* the Model Confidence Set uses the intersection of finite-loss dates across all models in
  that set;
* `T_common` and the number of observations removed by alignment are always reported;
* a poorly behaving model is never silently dropped to enlarge the common sample.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Alignment:
    dates: pd.DatetimeIndex
    n_common: int
    removed: dict[str, int]

    @property
    def available(self) -> bool:
        return self.n_common > 0


def valid_dates(frame: pd.DataFrame) -> pd.DatetimeIndex:
    """Target dates where this model produced a finite forecast and error."""
    usable = frame[np.isfinite(frame["forecast"]) & np.isfinite(frame["actual"])]
    return pd.DatetimeIndex(sorted(usable["target_date"].unique()))


def pairwise(a: pd.DataFrame, b: pd.DataFrame) -> Alignment:
    """Intersection of two models' valid dates."""
    left, right = valid_dates(a), valid_dates(b)
    shared = pd.DatetimeIndex(sorted(set(left) & set(right)))
    return Alignment(
        dates=shared,
        n_common=len(shared),
        removed={"left": len(left) - len(shared), "right": len(right) - len(shared)},
    )


def across_models(frames: Mapping[str, pd.DataFrame]) -> Alignment:
    """Intersection of valid dates across every model entering an MCS."""
    if not frames:
        return Alignment(pd.DatetimeIndex([]), 0, {})
    per_model = {name: set(valid_dates(frame)) for name, frame in frames.items()}
    shared = set.intersection(*per_model.values()) if per_model else set()
    dates = pd.DatetimeIndex(sorted(shared))
    return Alignment(
        dates=dates,
        n_common=len(dates),
        removed={name: len(values) - len(dates) for name, values in per_model.items()},
    )


def restrict(frame: pd.DataFrame, dates: pd.DatetimeIndex) -> pd.DataFrame:
    return frame[frame["target_date"].isin(set(dates))].sort_values("target_date")


def aligned_errors(
    frames: Mapping[str, pd.DataFrame], dates: pd.DatetimeIndex
) -> dict[str, np.ndarray]:
    out: dict[str, np.ndarray] = {}
    for name, frame in frames.items():
        restricted = restrict(frame, dates)
        out[name] = restricted["error"].to_numpy(dtype=float)
    return out
