"""Part 8 audit-derived diagnostics (read-only; NOT thesis-facing results).

This script reads the immutable outputs of run baseline-20261030T173044-949fcd76 under
`output/` and recomputes the handful of audit diagnostics quoted in `reports/part8/`.
It writes nothing under `output/`. Its numbers are audit evidence about the published
outputs (CLAUDE.md §9): they are not approved-methodology results and must not be cited
in the thesis as results. Where a correction is approved, the regenerated `output/`
files supersede every number printed here.

Run from `my-thesis/`:

    python reports/part8/audit_derived_diagnostics.py

It writes `reports/part8/audit_derived_diagnostics.csv` and prints the same rows.
"""

from __future__ import annotations

import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output"
DEST = Path(__file__).resolve().parent / "audit_derived_diagnostics.csv"
COVID = ("2020-01-01", "2021-06-01")

rows: list[dict] = []


def add(check: str, series: str, model: str, horizon, metric: str, value, source: str, note: str = ""):
    rows.append({"check": check, "series": series, "model": model, "horizon": horizon,
                 "metric": metric, "value": value, "source_file": source, "note": note})


def forecasts(series: str) -> pd.DataFrame:
    frame = pd.read_csv(OUT / "forecasts" / f"forecasts_{series}.csv",
                        parse_dates=["origin_date", "target_date"])
    return frame


# A1. FAILED fits whose forecasts are finite (they enter the evaluation tables).
for series in ("GDPC1", "CPIAUCSL", "UNRATE", "INDPRO", "FEDFUNDS", "M2SL"):
    frame = forecasts(series)
    failed = frame[frame["status"] == "failed"]
    finite = failed[np.isfinite(failed["forecast"])]
    add("A1 failed-but-finite forecasts", series, "all", "all", "n_rows", int(len(finite)),
        f"forecasts/forecasts_{series}.csv",
        "; ".join(sorted({f"{m} origin {d:%Y-%m}" for m, d in zip(finite.model, finite.origin_date)})))

# A2. UNRATE AR benchmark with and without the FAILED origin (2020-04, UNSTABLE_AR).
unrate = forecasts("UNRATE")
valid = unrate[np.isfinite(unrate["error"])]
for h in (1, 3, 6, 12):
    ar_all = valid[(valid.model == "AR") & (valid.horizon == h)]
    ar_ok = ar_all[ar_all.status != "failed"]
    add("A2 UNRATE AR RMSE", "UNRATE", "AR", h, "rmse_as_published",
        float(np.sqrt((ar_all.error ** 2).mean())), "forecasts/forecasts_UNRATE.csv")
    add("A2 UNRATE AR RMSE", "UNRATE", "AR", h, "rmse_excluding_failed",
        float(np.sqrt((ar_ok.error ** 2).mean())), "forecasts/forecasts_UNRATE.csv",
        "audit recomputation; excludes the FAILED (UNSTABLE_AR) origin only")
    for model in ("ARMA", "MSAR", "STAR"):
        comp = valid[(valid.model == model) & (valid.horizon == h) & (valid.status != "failed")]
        joined = comp.merge(ar_ok, on="target_date", suffixes=("", "_ar"))
        r2 = 1.0 - (joined.error ** 2).sum() / (joined.error_ar ** 2).sum()
        add("A2 UNRATE OOS R2 vs AR excluding failed", "UNRATE", model, h, "oos_r2",
            float(r2), "forecasts/forecasts_UNRATE.csv", f"n_common={len(joined)}")

# A3. Influence of 2020-01..2021-06 target dates on OOS R2 (descriptive sensitivity).
for series, h in (("GDPC1", 1), ("INDPRO", 1), ("INDPRO", 3), ("UNRATE", 1),
                  ("CPIAUCSL", 1), ("CPIAUCSL", 12), ("M2SL", 1), ("FEDFUNDS", 1)):
    frame = forecasts(series)
    frame = frame[(frame.horizon == h) & (frame.status != "failed")]
    wide = frame.pivot_table(index="target_date", columns="model", values="error")
    for model in ("ARMA", "MSAR"):
        pair = wide[["AR", model]].dropna()
        covid = (pair.index >= COVID[0]) & (pair.index <= COVID[1])
        r2_all = 1 - (pair[model] ** 2).sum() / (pair.AR ** 2).sum()
        r2_ex = 1 - (pair[model][~covid] ** 2).sum() / (pair.AR[~covid] ** 2).sum()
        gain = (pair[model] ** 2 - pair.AR ** 2)
        share = float(gain[covid].sum() / gain.sum()) if gain.sum() != 0 else float("nan")
        add("A3 COVID-window sensitivity", series, model, h, "oos_r2_all_dates", float(r2_all),
            f"forecasts/forecasts_{series}.csv", "failed rows excluded")
        add("A3 COVID-window sensitivity", series, model, h, "oos_r2_excluding_2020-01_to_2021-06",
            float(r2_ex), f"forecasts/forecasts_{series}.csv", f"n_excluded={int(covid.sum())}")
        add("A3 COVID-window sensitivity", series, model, h,
            "share_of_squared_loss_difference_from_2020-01_to_2021-06", share,
            f"forecasts/forecasts_{series}.csv",
            "negative loss difference = competitor better; share near 1 means the window drives the total")

# A4. Count of HLZ p-values in [0.30, 0.34] for pairs involving STAR (single-spike signature).
hlz = pd.read_csv(OUT / "forecast_tests" / "T3.3A_hlz_pairwise.csv")
star = hlz[hlz.model_b == "STAR"]
add("A4 STAR HLZ p-value clustering", "all", "STAR pairs", "all", "n_p_in_[0.30,0.34]",
    int(((star.p_value_two_sided > 0.30) & (star.p_value_two_sided < 0.34)).sum()),
    "forecast_tests/T3.3A_hlz_pairwise.csv",
    f"of {int(star.p_value_two_sided.notna().sum())} available STAR-pair tests")

# A5. Sign of mean_loss_differential in T3.3A versus forecasts (pair order check).
gdp = forecasts("GDPC1")
gdp = gdp[gdp.horizon == 1].pivot_table(index="target_date", columns="model", values="error")
add("A5 T3.3A sign check", "GDPC1", "AR vs ARMA", 1, "mean(loss_AR - loss_ARMA) from forecasts",
    float((gdp.AR ** 2 - gdp.ARMA ** 2).mean()), "forecasts/forecasts_GDPC1.csv",
    "equals T3.3A mean_loss_differential (+0.404), i.e. loss(model_a) - loss(model_b)")

# A6. Reproduce the MCS failure for CPIAUCSL h=1 squared loss (cause diagnosis only).
try:
    from arch.bootstrap import MCS

    cpi = forecasts("CPIAUCSL")
    cpi = cpi[cpi.horizon == 1].pivot_table(index="target_date", columns="model", values="error").dropna()
    losses = cpi ** 2
    block = int(math.ceil(math.sqrt(len(losses))))
    for cols in (["AR", "ARMA", "MSAR", "STAR"], ["AR", "ARMA", "MSAR"]):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                proc = MCS(losses[cols], size=0.10, reps=5000, block_size=block, method="R",
                           bootstrap="stationary", seed=20261005)
                proc.compute()
                outcome = "ran; included=" + ",".join(map(str, proc.included))
            except Exception as exc:  # noqa: BLE001 - diagnosis of the published failure
                outcome = f"failed: {exc!r}"
        add("A6 MCS failure reproduction", "CPIAUCSL", "+".join(cols), 1, "outcome_90pct_squared",
            outcome, "forecasts/forecasts_CPIAUCSL.csv",
            "cause diagnosis only; dropping STAR is NOT the approved model set")
except ImportError:
    add("A6 MCS failure reproduction", "CPIAUCSL", "n/a", 1, "outcome", "arch not installed", "", "")

# A7. Locally optimal K=3 likelihood below K=2 (nesting violation).
t43 = pd.read_csv(OUT / "robustness" / "T4.3_regime_count.csv")
for series, grp in t43.groupby("series"):
    k2 = float(grp[grp.k_regimes == 2].loglik.iloc[0])
    k3 = float(grp[grp.k_regimes == 3].loglik.iloc[0])
    add("A7 K=3 nests K=2 check", series, "MSAR3-MSAR", "in-sample", "loglik_k3_minus_k2", k3 - k2,
        "robustness/T4.3_regime_count.csv",
        "negative is impossible at a global maximum because K=3 nests K=2" if k3 < k2 else "")

table = pd.DataFrame(rows)
table.to_csv(DEST, index=False)
with pd.option_context("display.width", 220, "display.max_rows", 500, "display.max_colwidth", 90):
    print(table.to_string(index=False))
