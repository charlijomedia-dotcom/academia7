"""Business-cycle states for forecast evaluation (Part 5 §2.5, decision M11).

USREC is used **only** after forecasts exist, to classify realized target dates. It is
never a regressor, which is what keeps the official recession chronology from leaking
future information into a model.

States:

* recession: USREC = 1 at the target date;
* expansion: USREC = 0;
* peak: the month immediately preceding a 0 -> 1 transition;
* trough: the month immediately preceding a 1 -> 0 transition;
* turning window: +/- w months around each peak or trough (baseline w = 3), or
  +/- w quarters around the turning quarter for quarterly GDP (baseline w = 1).

Decision M11 fixes the edge cases: windows are built only from observed transitions,
clipped at the sample boundaries, and taken as a **union** so an observation inside two
overlapping windows is counted once. Recession and turning-window categories may overlap,
because they answer different questions.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

EXPANSION = "expansion"
RECESSION = "recession"
TURNING = "turning_window"
OUTSIDE_TURNING = "outside_turning_window"
PEAK = "peak_window"
TROUGH = "trough_window"


@dataclass(frozen=True)
class Chronology:
    """Aligned recession indicator and derived turning points for one frequency."""

    index: pd.DatetimeIndex
    recession: np.ndarray            # 0/1
    peaks: pd.DatetimeIndex
    troughs: pd.DatetimeIndex

    @property
    def has_transitions(self) -> bool:
        return len(self.peaks) + len(self.troughs) > 0


def monthly_chronology(usrec: pd.Series) -> Chronology:
    """Peaks and troughs from observed transitions in the monthly indicator."""
    clean = usrec.dropna()
    index = pd.DatetimeIndex(clean.index)
    values = clean.to_numpy(dtype=float)
    peaks, troughs = [], []
    for position in range(len(values) - 1):
        if values[position] == 0 and values[position + 1] == 1:
            peaks.append(index[position])        # month before the recession starts
        elif values[position] == 1 and values[position + 1] == 0:
            troughs.append(index[position])      # month before the expansion resumes
    return Chronology(index, values, pd.DatetimeIndex(peaks), pd.DatetimeIndex(troughs))


def to_quarterly(usrec: pd.Series) -> pd.Series:
    """A quarter is recession-affected if any month in it has USREC = 1 (Part 5 §2.5)."""
    clean = usrec.dropna()
    grouped = clean.groupby(pd.PeriodIndex(clean.index, freq="Q")).max()
    grouped.index = grouped.index.to_timestamp(how="start")
    grouped.index.name = "date"
    return grouped


def quarterly_chronology(usrec: pd.Series) -> Chronology:
    return monthly_chronology(to_quarterly(usrec))


def _window_mask(index: pd.DatetimeIndex, centres: pd.DatetimeIndex, width: int) -> np.ndarray:
    """Union of +/- `width` periods around each centre, clipped to the sample."""
    mask = np.zeros(len(index), dtype=bool)
    positions = {date: i for i, date in enumerate(index)}
    for centre in centres:
        if centre not in positions:
            continue
        centre_position = positions[centre]
        low = max(0, centre_position - width)
        high = min(len(index) - 1, centre_position + width)
        mask[low : high + 1] = True
    return mask


def turning_masks(
    chronology: Chronology, width: int
) -> dict[str, np.ndarray]:
    """Turning-window masks at a given half-width, as a union over peaks and troughs."""
    peak_mask = _window_mask(chronology.index, chronology.peaks, width)
    trough_mask = _window_mask(chronology.index, chronology.troughs, width)
    union = peak_mask | trough_mask
    return {
        PEAK: peak_mask,
        TROUGH: trough_mask,
        TURNING: union,
        OUTSIDE_TURNING: ~union,
    }


def state_frame(chronology: Chronology, width: int) -> pd.DataFrame:
    """One row per date with every state indicator, for joining onto forecasts."""
    masks = turning_masks(chronology, width)
    return pd.DataFrame(
        {
            "target_date": chronology.index,
            "recession": chronology.recession.astype(int),
            "expansion": (1 - chronology.recession).astype(int),
            "turning_window": masks[TURNING].astype(int),
            "outside_turning_window": masks[OUTSIDE_TURNING].astype(int),
            "peak_window": masks[PEAK].astype(int),
            "trough_window": masks[TROUGH].astype(int),
        }
    )


def attach_states(forecasts: pd.DataFrame, states: pd.DataFrame) -> pd.DataFrame:
    """Join state indicators onto forecasts by **target** date (Part 5 §2.5)."""
    return forecasts.merge(states, on="target_date", how="left")


def state_subsets(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """The four evaluation states of Part 5 §10.5."""
    return {
        EXPANSION: frame[frame["expansion"] == 1],
        RECESSION: frame[frame["recession"] == 1],
        TURNING: frame[frame["turning_window"] == 1],
        OUTSIDE_TURNING: frame[frame["outside_turning_window"] == 1],
    }
