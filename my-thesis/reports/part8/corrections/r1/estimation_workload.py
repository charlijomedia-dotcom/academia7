#!/usr/bin/env python3
"""Exact list and cost of the rolling chains R1 cannot rebuild from published files.

Usage (from my-thesis/):  python reports/part8/corrections/r1/estimation_workload.py

Origins come from the published origin audits and robustness tables; the cost per fit is
the mean `wall_seconds` the original run recorded for the same target and model class
(models/fit_records.parquet, all window lengths). Writes estimation_workload.csv.

Which chains are listed, and why (see r1_validation_report.md, section 4):
  * T4.2 CPI AR lags: the p=12 chain has a FAILED fit (1974-09) whose finite forecast was
    scored, and the four lag variants are compared on common dates, so all four rows change.
  * T4.1 alternative transformations (UNRATE, FEDFUNDS): their AR chains contain FAILED
    (UNSTABLE_AR) fits whose finite forecasts were scored; every AR-relative row changes.
  * T4.8 UNRATE at 180 and 300 months: the AR chain has one FAILED fit at each length.
  Every other non-baseline chain is unaffected by F1-F4/F7.1 (no AR failure, no
  unavailable MCS cell, F3 orientation not involved), so its published rows stand.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUTPUT = HERE.parents[3] / "output"


def main() -> pd.DataFrame:
    fits = pd.read_parquet(OUTPUT / "models" / "fit_records.parquet",
                           columns=["series", "model", "wall_seconds"])
    per_fit = fits.groupby(["series", "model"])["wall_seconds"].mean()
    rows = []

    t42 = pd.read_csv(OUTPUT / "robustness" / "T4.2_cpi_lag_robustness.csv")
    for r in t42.itertuples():
        rows.append(("T4.2", f"T4.2:CPIAUCSL|{r.model}", "CPIAUCSL", "AR", "baseline (240)",
                     int(r.n_attempted)))

    t41 = pd.read_csv(OUTPUT / "robustness" / "T4.1_transformation_robustness.csv")
    alternative = t41[t41["n_attempted"].notna()].groupby(["series", "model"]).nth(1)
    for r in alternative.itertuples():
        rows.append(("T4.1", f"T4.1:{r.series}|{r.model}", r.series, r.model,
                     "alternative transformation", int(r.n_attempted)))

    audit = pd.read_csv(OUTPUT / "robustness" / "window_length_origin_audit.csv")
    unrate = audit[(audit["series"] == "UNRATE") & (audit["role"] != "baseline")]
    for r in unrate.drop_duplicates(["model", "window_length"]).itertuples():
        rows.append(("T4.8", f"T4.8:UNRATE|{r.window_length}:{r.model}", "UNRATE", r.model,
                     f"window {r.window_length}", int(r.attempted_origins)))

    frame = pd.DataFrame(rows, columns=["exercise", "task_id", "series", "model", "variant",
                                        "origins"])
    frame["mean_seconds_per_fit"] = [per_fit[(s, m)] for s, m in
                                     zip(frame["series"], frame["model"])]
    frame["cpu_hours"] = frame["origins"] * frame["mean_seconds_per_fit"] / 3600
    frame["warm_started"] = frame["model"].isin(["MSAR", "STAR"])
    frame["platform_sensitivity"] = frame["model"].map({
        "AR": "none observed (closed form; re-estimated T4.2 reproduces published to 1e-14)",
        "ARMA": "low (numerical optimiser, no warm start)",
        "MSAR": "high (EM/BFGS multistart, warm-started chain; F6)",
        "STAR": "moderate (nonlinear optimiser, warm-started chain)"})
    frame["tier"] = frame["model"].map({"AR": "A (cheap)", "ARMA": "B", "MSAR": "B",
                                        "STAR": "B"})
    frame.to_csv(HERE / "estimation_workload.csv", index=False)
    return frame


if __name__ == "__main__":
    table = main()
    print(table.to_string(index=False))
    print(table.groupby("tier")[["origins", "cpu_hours"]].sum())
    print("total CPU hours:", round(table["cpu_hours"].sum(), 1),
          "| longest single chain (h):", round(table["cpu_hours"].max(), 1))
