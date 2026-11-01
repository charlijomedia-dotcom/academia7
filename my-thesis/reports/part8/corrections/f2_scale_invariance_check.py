"""F2 independent check for the overflow-guarded MCS cells (read-only).

The HLN R-method statistics are invariant to multiplying the whole loss matrix by a
positive constant c: loss differences, their bootstrap means and their root-mean-square
all scale by c, so every standardised statistic, the elimination order and the p-values
are unchanged. Multiplying by c = 1e-150 removes the overflow, so the plain arithmetic
(no rescaling guard) can be compared with the guarded computation on the original scale.

Cells checked: every published-run MCS cell where the guarded implementation needed the
overflow guard (CPIAUCSL h=12 squared, M2SL h=12 squared; 90% and 95%), on the F1-masked
frames. Writes `f2_scale_invariance_check.csv`.

Run from `my-thesis/`:  python reports/part8/corrections/f2_scale_invariance_check.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "src"))
from thesis.evaluation import alignment  # noqa: E402
from thesis.evaluation.losses import loss  # noqa: E402
from thesis.evaluation.mcs import hln_mcs_r  # noqa: E402
from thesis.evaluation.scoring import mask_failed  # noqa: E402

rows = []
for series in ("CPIAUCSL", "M2SL"):
    f = mask_failed(pd.read_csv(ROOT / "output" / "forecasts" / f"forecasts_{series}.csv",
                                parse_dates=["origin_date", "target_date"]))
    frames = {m: f[(f.model == m) & (f.horizon == 12)] for m in ("AR", "ARMA", "MSAR", "STAR")}
    dates = alignment.across_models(frames).dates
    losses = pd.DataFrame({m: loss(alignment.restrict(fr, dates)["error"].to_numpy(float),
                                   "squared") for m, fr in frames.items()}, index=dates)
    block = int(math.ceil(math.sqrt(len(dates))))
    for confidence in (0.9, 0.95):
        p_orig, inc_orig, _, d_orig = hln_mcs_r(losses, 1 - confidence, 5000, block, 20261005)
        p_scaled, inc_scaled, _, d_scaled = hln_mcs_r(losses * 1e-150, 1 - confidence, 5000,
                                                      block, 20261005)
        rows.append({
            "series": series, "horizon": 12, "loss": "squared", "confidence": confidence,
            "rescaled_cells_original": d_orig["rescaled_variance_cells"],
            "rescaled_cells_scaled": d_scaled["rescaled_variance_cells"],
            "included_original": ",".join(inc_orig), "included_scaled": ",".join(inc_scaled),
            "p_original": "; ".join(f"{m}={p_orig[m]:.4f}" for m in sorted(p_orig.index)),
            "p_scaled": "; ".join(f"{m}={p_scaled[m]:.4f}" for m in sorted(p_scaled.index)),
            "max_abs_p_difference": max(abs(p_orig[m] - p_scaled[m]) for m in p_orig.index),
            "same_elimination_order": list(p_orig.index) == list(p_scaled.index),
        })
        print(rows[-1])
pd.DataFrame(rows).to_csv(Path(__file__).with_suffix(".csv"), index=False)
