"""Which forecasts may enter a loss calculation (Part 5 §7.5; Part 8 correction F1).

Part 5 §7.5 classifies a fit as **failed** when, among other things, a required AR/ARMA
stability condition is violated, and failed models are "reported as failures rather than"
used. Some failed fits still return a *finite* point forecast — an AR with an explosive
root does (`UNSTABLE_AR`). Before this correction the evaluation layer dropped only
non-finite errors, so such a forecast was scored as if it were valid
(`notes/claude/part8_audit_findings_and_correction_proposals_2026-11-01.md`, F1).

The rule implemented here is deliberately narrow:

* a forecast row is **scoreable** when its originating fit is *not* `failed` and both the
  forecast and the realised value are finite;
* adequate and fragile fits stay scoreable exactly as before (§7.5: fragile models "may
  still have forecast metrics");
* a failed fit's raw forecast is kept, unscored, in the diagnostic column
  `failed_raw_forecast`, so the failure stays visible in the forecast files and figures.

The masking is applied in `pipeline.py` to every rolling chain's forecast frame when the
chain returns, and the evaluation functions apply `scoreable` again defensively. No
estimation code is touched: `forecasting/rolling.py` and the model files are part of the
fit-cache identity (`core/cache._FIT_CRITICAL`) and are unchanged, so cached fits remain
valid.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

#: Diagnostic column holding the unscored forecast of a failed fit (NaN otherwise).
FAILED_RAW_FORECAST = "failed_raw_forecast"
FAILED = "failed"


def failed_rows(frame: pd.DataFrame) -> pd.Series:
    """Boolean mask of rows whose originating fit has status `failed`."""
    if "status" not in frame.columns:
        return pd.Series(False, index=frame.index)
    return frame["status"].astype(str).str.lower().eq(FAILED)


def scoreable(frame: pd.DataFrame) -> pd.Series:
    """Rows that may enter any loss: finite forecast and actual, fit not failed."""
    forecast = pd.to_numeric(frame["forecast"], errors="coerce").to_numpy(dtype=float)
    actual = pd.to_numeric(frame["actual"], errors="coerce").to_numpy(dtype=float)
    finite = np.isfinite(forecast) & np.isfinite(actual)
    return pd.Series(finite, index=frame.index) & ~failed_rows(frame)


def mask_failed(frame: pd.DataFrame) -> pd.DataFrame:
    """Copy of a forecast frame in which failed fits carry no scoreable forecast.

    `forecast` and `error` become NaN on failed rows; the original forecast is preserved in
    `failed_raw_forecast`. Every other row is returned unchanged. Idempotent.
    """
    out = frame.copy()
    if out.empty or "forecast" not in out.columns:
        if FAILED_RAW_FORECAST not in out.columns:
            out[FAILED_RAW_FORECAST] = pd.Series(dtype=float)
        return out
    failed = failed_rows(out)
    if FAILED_RAW_FORECAST not in out.columns:
        out[FAILED_RAW_FORECAST] = np.nan
    raw = pd.to_numeric(out["forecast"], errors="coerce")
    keep_existing = out[FAILED_RAW_FORECAST].notna()
    out.loc[failed & ~keep_existing, FAILED_RAW_FORECAST] = raw[failed & ~keep_existing]
    out.loc[failed, "forecast"] = np.nan
    if "error" in out.columns:
        out.loc[failed, "error"] = np.nan
    return out
