#!/usr/bin/env python3
"""Which non-published robustness chains a correction actually needs (static; no estimation).

Usage (from my-thesis/):  python reports/part8/corrections/r1/classify_nonpublished_chains.py

Reads only the original release (`output/`). For each of the 60 rolling chains the
published release does not contain (T4.1 alternative transformations: 8; T4.2 CPI AR lags:
4; T4.8 non-baseline window lengths: 48), it records the evidence that decides whether
any approved correction (F1, F2, F3, F4, F7.1, F8) changes the chain's published rows:

* F1 changes a row only through a FAILED fit whose forecast was finite and scored. In
  `models/registry.fit_and_forecast` a FAILED ARMA, MSAR or STAR fit returns no forecast
  (NaN), so their failures were never scored; only AR fits forecast despite failing
  (UNSTABLE_AR). The decisive evidence is therefore the AR chain's failed-origin count
  (from the T4.8 origin audit, or from the T4.7 registry for T4.1/T4.2).
* F2 changes a row only where the original MCS was unavailable.
* F3 touches only T3.3A/B; F4 and F7.1 touch only T2.x; F8 only F3.4 figures.

Writes nonpublished_chain_classification.csv next to this script.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[3] / "output"
MODELS = ("AR", "ARMA", "MSAR", "STAR")


def main() -> pd.DataFrame:
    audit = pd.read_csv(OUT / "robustness" / "window_length_origin_audit.csv")
    mcs = pd.read_csv(OUT / "robustness" / "window_length_mcs.csv")
    registry = pd.read_csv(OUT / "robustness" / "T4.7_failure_registry.csv")
    failed_ar = registry[(registry["model"] == "AR") & (registry["category"] == "failed")
                         & (registry["reason_code"] == "UNSTABLE_AR")]
    rows = []

    # T4.1 alternative transformation chains (UNRATE: difference; FEDFUNDS: level)
    t41_ar_failures = {
        # UNRATE: of the 6 failed AR fits, the two whose window is the differenced series
        # (window mean ~0, see raw_diagnostic) are the T4.1 chain: 2020-04 and 2020-08.
        "UNRATE": int(registry[(registry["series"] == "UNRATE") & (registry["model"] == "AR")
                               & (registry["reason_code"] == "EXTREME_FORECAST")
                               & (registry["category"] == "failed")
                               & registry["raw_diagnostic"].str.contains(r"window mean=0\.0",
                                                                         regex=True)].shape[0]),
        # FEDFUNDS: the baseline (difference) and T4.8 AR chains have no failure, so every
        # failed FEDFUNDS AR fit belongs to the T4.1 level chain.
        "FEDFUNDS": int(failed_ar[failed_ar["series"] == "FEDFUNDS"]["refit_date"].nunique()),
    }
    for series, failures in t41_ar_failures.items():
        for model in MODELS:
            rows.append({"task_id": f"T4.1:{series}|{model}", "exercise": "T4.1",
                         "series": series, "model": model, "window_length": "",
                         "ar_failed_origins_in_exercise": failures,
                         "mcs_unavailable_cells": 0,
                         "affected_by_correction": failures > 0,
                         "reason": "F1: the exercise's AR chain has failed fits whose finite "
                                   "forecasts were scored; every AR-relative row of every "
                                   "model changes"})
    for order in (1, 3, 6, 12):
        failures = 1  # the p=12 chain fails at 1974-09; variants share common dates
        rows.append({"task_id": f"T4.2:CPIAUCSL|AR(p={order})", "exercise": "T4.2",
                     "series": "CPIAUCSL", "model": f"AR(p={order})", "window_length": "",
                     "ar_failed_origins_in_exercise": failures, "mcs_unavailable_cells": 0,
                     "affected_by_correction": True,
                     "reason": "F1: the p=12 fit at 1974-09 failed and was scored; the four "
                               "variants are compared on common dates"})
    # T4.8 non-baseline window lengths
    for (series, length), group in audit[audit["role"] != "baseline"].groupby(
            ["series", "window_length"]):
        ar = group[group["model"] == "AR"]
        failures = int(ar["failed_origins"].sum()) if len(ar) else 0
        cells = mcs[(mcs["series"] == series) & (mcs["window_length"] == length)]
        unavailable = int((cells["inference_available"].astype(str) != "True").sum())
        for model in MODELS:
            affected = failures > 0 or unavailable > 0
            rows.append({"task_id": f"T4.8:{series}|{length}:{model}", "exercise": "T4.8",
                         "series": series, "model": model, "window_length": int(length),
                         "ar_failed_origins_in_exercise": failures,
                         "mcs_unavailable_cells": unavailable,
                         "affected_by_correction": affected,
                         "reason": ("F1: the AR chain at this length has a failed fit that "
                                    "was scored" if failures else
                                    "F2: an MCS cell was unavailable" if unavailable else
                                    "unaffected: no AR failure, every MCS cell available, "
                                    "F3/F4/F7.1/F8 do not apply; the published rows stand")})
    table = pd.DataFrame(rows)
    table["decision"] = table.apply(
        lambda r: ("resolved by Tier A (AR re-estimated)" if r["exercise"] == "T4.2" else
                   "AR resolved by Tier A; exercise still needs this series' ARMA/MSAR/STAR"
                   if r["affected_by_correction"] and r["model"] == "AR" else
                   "needed for correction (cache replay or Tier B)"
                   if r["affected_by_correction"] else
                   "retain original (legitimately unaffected)"), axis=1)
    table.to_csv(HERE / "nonpublished_chain_classification.csv", index=False)
    return table


if __name__ == "__main__":
    t = main()
    print(t.groupby(["exercise", "decision"]).size().to_string())
    print("total", len(t))
