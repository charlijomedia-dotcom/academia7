"""Rolling estimation windows and forecast origins.

Part 5 §9.1 fixes the baseline windows at 240 monthly and 120 quarterly observations, and
the amendment of 12 October 2026 adds the predeclared sensitivity lengths 180/300 monthly
and 90/150 quarterly (Outputs T4.8).

Two properties matter and are enforced here rather than left to each caller:

* a window never reaches past its origin, so no future observation can enter an estimate;
* when several window lengths are compared, they are evaluated on a **common calendar**
  that begins only when the longest candidate window is available, so the comparison is
  not contaminated by differing evaluation samples (T4.8).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

import pandas as pd


@dataclass(frozen=True)
class Origin:
    """One forecast origin and the estimation window that ends at it."""

    position: int                    # index position of the origin observation
    origin_date: pd.Timestamp
    window_start: pd.Timestamp
    window_end: pd.Timestamp         # equals origin_date
    target_position: int
    target_date: pd.Timestamp
    horizon: int
    window_length: int

    def estimation_slice(self) -> slice:
        """Positions of the estimation sample, inclusive of the origin."""
        return slice(self.position - self.window_length + 1, self.position + 1)


def rolling_origins(
    index: pd.DatetimeIndex,
    window_length: int,
    horizon: int = 1,
    *,
    max_origins: int | None = None,
) -> list[Origin]:
    """Every forecast origin for a fixed-length rolling window.

    The first origin is the earliest date at which a full window of `window_length`
    observations exists; the last is the one whose target still falls inside the sample.
    """
    if window_length <= 0:
        raise ValueError(f"window_length must be positive, got {window_length}")
    if horizon <= 0:
        raise ValueError(f"horizon must be positive, got {horizon}")
    index = pd.DatetimeIndex(index)
    n = len(index)
    origins: list[Origin] = []
    for position in range(window_length - 1, n - horizon):
        target_position = position + horizon
        origins.append(
            Origin(
                position=position,
                origin_date=index[position],
                window_start=index[position - window_length + 1],
                window_end=index[position],
                target_position=target_position,
                target_date=index[target_position],
                horizon=horizon,
                window_length=window_length,
            )
        )
    if max_origins is not None:
        origins = origins[-max_origins:]
    return origins


def estimation_origins(
    index: pd.DatetimeIndex,
    window_length: int,
    horizons: Sequence[int],
    *,
    max_origins: int | None = None,
) -> list[Origin]:
    """Every origin with a full estimation window and at least one realizable target.

    One fitted model serves all requested horizons, so the origin set must not be
    restricted by the **longest** horizon: doing so throws away the late-sample origins
    at which a shorter horizon still has a realized target. Part 5 §9.4 makes h=1 the
    primary exercise and the longer horizons separate robustness analyses, so h=1 must
    run to the approved sample endpoint whether or not h=12 was also requested.

    The origin set is therefore bounded by the **shortest** requested horizon, and each
    horizon's targets are taken only where they fall inside the sample. The returned
    `Origin` carries the shortest horizon as its anchor; the per-horizon target dates are
    resolved by `targets_for`.
    """
    horizons = sorted({int(h) for h in horizons})
    if not horizons:
        raise ValueError("at least one horizon is required")
    return rolling_origins(index, window_length, horizon=min(horizons),
                           max_origins=max_origins)


def targets_for(
    origin: Origin, horizons: Sequence[int], index: pd.DatetimeIndex
) -> list[tuple[int, int, pd.Timestamp]]:
    """The (horizon, target position, target date) triples realizable from one origin.

    A horizon whose target would fall past the end of the sample is omitted rather than
    producing a forecast with no realized value to score it against.
    """
    index = pd.DatetimeIndex(index)
    out = []
    for horizon in sorted({int(h) for h in horizons}):
        target_position = origin.position + horizon
        if 0 <= target_position < len(index):
            out.append((horizon, target_position, index[target_position]))
    return out


def horizon_coverage(
    index: pd.DatetimeIndex,
    window_length: int,
    horizons: Sequence[int],
    *,
    max_origins: int | None = None,
) -> dict[int, dict]:
    """Per-horizon origin and target coverage, for the forecast-origin audit."""
    origins = estimation_origins(index, window_length, horizons, max_origins=max_origins)
    index = pd.DatetimeIndex(index)
    summary: dict[int, dict] = {}
    for horizon in sorted({int(h) for h in horizons}):
        realizable = [o for o in origins if o.position + horizon < len(index)]
        summary[horizon] = {
            "n_origins": len(realizable),
            "first_origin": realizable[0].origin_date if realizable else None,
            "last_origin": realizable[-1].origin_date if realizable else None,
            "first_target": (index[realizable[0].position + horizon]
                             if realizable else None),
            "last_target": (index[realizable[-1].position + horizon]
                            if realizable else None),
        }
    return summary


def initial_window(index: pd.DatetimeIndex, window_length: int) -> pd.DatetimeIndex:
    """The initial estimation window: the first `window_length` observations.

    Decision T7 defines this as the first approved rolling window, and it is where every
    discrete specification choice is made (Part 5 §9.2).
    """
    index = pd.DatetimeIndex(index)
    if len(index) < window_length:
        raise ValueError(
            f"series has {len(index)} observations, fewer than the window length {window_length}"
        )
    return index[:window_length]


def common_calendar(
    index: pd.DatetimeIndex,
    window_lengths: Sequence[int],
    horizon: int = 1,
) -> pd.DatetimeIndex:
    """Target dates on which every candidate window length can be evaluated.

    T4.8 requires the comparison calendar to begin only when the **longest** candidate
    window is available, so each length is scored on identical target dates.
    """
    if not window_lengths:
        raise ValueError("at least one window length is required")
    index = pd.DatetimeIndex(index)
    per_length = [
        {origin.target_date for origin in rolling_origins(index, length, horizon)}
        for length in window_lengths
    ]
    shared = set.intersection(*per_length)
    return pd.DatetimeIndex(sorted(shared))


def restrict_to_calendar(origins: Iterable[Origin], calendar: pd.DatetimeIndex) -> list[Origin]:
    """Keep only the origins whose target date lies on the shared calendar."""
    allowed = set(pd.DatetimeIndex(calendar))
    return [origin for origin in origins if origin.target_date in allowed]


def window_lengths_for(frequency: str, config) -> list[int]:
    """The predeclared sensitivity lengths for a frequency (T4.8)."""
    lengths = config.get(f"robustness.window_lengths.lengths.{frequency}")
    return [int(length) for length in lengths]


def baseline_window(frequency: str, config) -> int:
    return int(config.get(f"forecasting.windows.{frequency}"))


def describe_coverage(
    index: pd.DatetimeIndex, window_lengths: Sequence[int], horizon: int = 1
) -> Mapping[int, dict]:
    """Per-length origin counts and date ranges, for the T4.8 origin audit."""
    calendar = common_calendar(index, window_lengths, horizon)
    summary = {}
    for length in window_lengths:
        origins = rolling_origins(index, length, horizon)
        shared = restrict_to_calendar(origins, calendar)
        summary[length] = {
            "n_origins": len(origins),
            "n_on_common_calendar": len(shared),
            "first_target": origins[0].target_date if origins else None,
            "last_target": origins[-1].target_date if origins else None,
            "common_first_target": calendar[0] if len(calendar) else None,
            "common_last_target": calendar[-1] if len(calendar) else None,
            "n_dropped_by_alignment": len(origins) - len(shared),
        }
    return summary
