#!/usr/bin/env python3
"""How far one forecast dominates each STAR-vs-AR loss differential (static; original release).

Usage (from my-thesis/): python reports/part8/corrections/r1/star_test_degeneracy.py
For every series, horizon and loss: the largest single observation's share of sum(d^2),
where d = loss(STAR) - loss(AR) on common dates (failed fits excluded, as under F1), and
STAR's largest absolute error. A share near 1 means HLZ/DM-HLN statistics are degenerate
(determined by one exploded forecast); a non-finite share means the variance overflowed.
Writes star_test_degeneracy.csv next to this script.
"""
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[3] / "output"
rows = []
for series in ("GDPC1", "CPIAUCSL", "UNRATE", "INDPRO", "FEDFUNDS", "M2SL"):
    f = pd.read_parquet(OUT / "forecasts" / f"forecasts_{series}.parquet")
    f = f[f["status"] != "failed"]
    for h in sorted(f["horizon"].unique()):
        w = f[f["horizon"] == h].pivot_table(index="target_date", columns="model", values="error")
        for loss in ("absolute", "squared"):
            losses = w.abs() if loss == "absolute" else w ** 2
            d = (losses["STAR"] - losses["AR"]).dropna().to_numpy(float)
            with np.errstate(all="ignore"):
                total = float(np.sum(d ** 2))
                share = float(np.max(d ** 2) / total) if np.isfinite(total) and total > 0 \
                    else float("nan")
            rows.append({"series": series, "horizon": int(h), "loss": loss, "n": len(d),
                         "max_single_share_of_sum_d2": share,
                         "star_max_abs_error": float(w["STAR"].abs().max()),
                         "degenerate": (not np.isfinite(share)) or share >= 0.95})
table = pd.DataFrame(rows)
table.to_csv(HERE / "star_test_degeneracy.csv", index=False)
print(table[table["degenerate"]][["series", "horizon", "loss", "max_single_share_of_sum_d2",
                                  "star_max_abs_error"]].to_string(index=False))
