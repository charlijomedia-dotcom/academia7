"""Local transformations of frozen raw levels.

Part 5 §2.3 fixes the transformation and the annualization factor for each target, and
Part 5 §2.2 requires every transformation to be computed locally from the frozen raw
levels so that the same frozen files always reproduce the same model inputs.

    g_t = k * [ln(X_t) - ln(X_{t-1})],  k = 400 quarterly, k = 1200 monthly

The factor only restates a one-period continuously compounded change as an annualized
percentage rate. It adds no predictive information (Part 5 §2.3).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

#: Approved annualization factors (Part 5 §2.3). Keyed by frequency code.
ANNUALIZATION = {"M": 1200.0, "Q": 400.0}


class TransformError(ValueError):
    """Raised when a transformation cannot be applied to the data as given."""


def log_level(series: pd.Series) -> pd.Series:
    """Natural log of a strictly positive level series.

    Used for the §3.3 verification that reports ADF and KPSS on the log level before and
    after differencing.
    """
    _require_positive(series)
    return pd.Series(np.log(series.to_numpy(dtype=float)), index=series.index, name=series.name)


def annualized_logdiff(series: pd.Series, k: float) -> pd.Series:
    """Annualized one-period log difference.

    A missing input value propagates to NaN rather than being skipped or filled: the
    approved methodology forbids backfilling and interpolation (Part 5 §2.4), so a gap in
    the levels must remain visible as a gap in the transformed target.
    """
    if k <= 0:
        raise TransformError(f"annualization factor must be positive, got {k}")
    _require_positive(series, allow_missing=True)
    values = series.to_numpy(dtype=float)
    logs = np.full_like(values, np.nan, dtype=float)
    observed = ~np.isnan(values)
    logs[observed] = np.log(values[observed])
    out = np.full_like(values, np.nan, dtype=float)
    out[1:] = k * (logs[1:] - logs[:-1])
    result = pd.Series(out, index=series.index, name=series.name)
    return result


def annualization_factor(frequency: str) -> float:
    try:
        return ANNUALIZATION[frequency]
    except KeyError as exc:
        raise TransformError(
            f"no approved annualization factor for frequency {frequency!r}; "
            f"Part 5 §2.3 defines only {sorted(ANNUALIZATION)}"
        ) from exc


def _require_positive(series: pd.Series, allow_missing: bool = False) -> None:
    values = series.to_numpy(dtype=float)
    missing = np.isnan(values)
    if missing.any() and not allow_missing:
        raise TransformError(
            f"{series.name}: contains {int(missing.sum())} missing observation(s); "
            f"a log transformation of a gapped series needs an approved missing-data rule"
        )
    finite = values[~missing]
    if finite.size and (finite <= 0).any():
        raise TransformError(
            f"{series.name}: log transformation requires strictly positive levels"
        )
