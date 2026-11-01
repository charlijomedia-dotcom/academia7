"""F6 feasibility study: a nesting-informed initialisation for full-sample MSAR K=3.

READ-ONLY numerical review (approved as a study, NOT as a modification). It writes only
`f6_k3_nesting_feasibility.csv` next to this file; it never writes `output/` and never
changes T4.3.

Question. K=3 nests K=2 (a third regime that is never entered reproduces the K=2
likelihood), so the maximised K=3 log-likelihood cannot be below K=2's. The published
UNRATE K=3 estimate violates this (13.88 < 102.04), which shows that the two approved
deterministic starts did not reach the K=2-nesting region. Can one additional
deterministic start built from the K=2 optimum repair this?

Construction of the nesting-informed start (theta in `models/msar.py` parameterisation):
* the two K=2 regime means, AR coefficients and sigma are copied from the K=2 optimum;
* a third regime mean is placed at the midpoint of the two K=2 means (deterministic);
* transitions into the new regime from the K=2 regimes are set to 1e-4, the K=2
  transition probabilities are kept for the rest, and the new regime's own row is
  persistent (0.90 stay, the rest split equally).
It is passed through the existing `warm_start` argument of `fit_msar`, so no fit-critical
file would need to change; the approved two deterministic starts are still run, and the
best converged start is selected by the unchanged rule.

The script refits K=2 and K=3 with the published code path (to confirm it reproduces the
published T4.3 log-likelihoods), then K=3 with the extra start, and records log-likelihood,
convergence, the start selected, occupancies and wall time for all six targets.

Run from `my-thesis/`:  python reports/part8/corrections/f6_k3_nesting_feasibility.py [SERIES ...]
(with series names, only those targets are refitted and merged into the existing CSV)
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "src"))

from thesis.core.config import load_config  # noqa: E402
from thesis.core.paths import CONFIG_DIR  # noqa: E402
from thesis.models.msar import _pack, _unpack, fit_msar  # noqa: E402

DEST = Path(__file__).with_suffix(".csv")
T43 = pd.read_csv(ROOT / "output" / "robustness" / "T4.3_regime_count.csv")


def targets() -> dict[str, pd.Series]:
    frame = pd.read_csv(ROOT / "data" / "frozen" / "thesis_input_2026-10-05.csv",
                        parse_dates=["date"])
    out = {}
    for series, scale, kind in (("GDPC1", 400, "dlog"), ("CPIAUCSL", 1200, "dlog"),
                                ("INDPRO", 1200, "dlog"), ("M2SL", 1200, "dlog"),
                                ("UNRATE", 1, "level"), ("FEDFUNDS", 1, "diff")):
        level = frame[frame.series_id == series].set_index("date")["value"].astype(float).dropna()
        level.index = pd.DatetimeIndex(level.index)
        if kind == "dlog":
            y = scale * np.log(level).diff().dropna()
        elif kind == "diff":
            y = level.diff().dropna()
        else:
            y = level
        row = T43[(T43.series == series) & (T43.k_regimes == 2)].iloc[0]
        y = y[(y.index >= pd.Timestamp(row.sample_start)) & (y.index <= pd.Timestamp(row.sample_end))]
        y.name = series
        out[series] = y
    return out


def nesting_start(fit2) -> np.ndarray:
    mu2, phi, sigma, P2 = _unpack(fit2.theta, 2, fit2.order)
    mu = np.array([mu2[0], mu2[1], 0.5 * (mu2[0] + mu2[1])])
    eps = 1e-4
    P = np.zeros((3, 3))
    P[:2, :2] = P2 * (1 - eps)
    P[0, 2] = P[1, 2] = eps
    P[2] = [0.05, 0.05, 0.90]
    return _pack(mu, phi, sigma, P)


def main() -> None:
    config = load_config(names=("baseline", "series_catalog", "thresholds"), config_dir=CONFIG_DIR)
    wanted = set(sys.argv[1:])
    rows = (pd.read_csv(DEST).to_dict("records") if DEST.exists() and wanted else [])
    rows = [r for r in rows if r["series"] not in wanted]
    for series, y in targets().items():
        if wanted and series not in wanted:
            continue
        order = int(T43[(T43.series == series) & (T43.k_regimes == 2)].iloc[0].ar_order)
        published = T43[T43.series == series].set_index("k_regimes")
        t0 = time.perf_counter()
        fit2 = fit_msar(y, order, 2, config=config, series=series, compute_covariance=False)
        t2 = time.perf_counter() - t0
        t0 = time.perf_counter()
        fit3 = fit_msar(y, order, 3, config=config, series=series, compute_covariance=False)
        t3 = time.perf_counter() - t0
        t0 = time.perf_counter()
        fit3n = fit_msar(y, order, 3, config=config, series=series, compute_covariance=False,
                         warm_start=nesting_start(fit2))
        t3n = time.perf_counter() - t0
        rows.append({
            "series": series, "ar_order": order, "n_obs": len(y),
            "published_loglik_k2": float(published.loc[2, "loglik"]),
            "published_loglik_k3": float(published.loc[3, "loglik"]),
            "refit_loglik_k2": fit2.loglik, "refit_loglik_k3": fit3.loglik,
            "reproduces_published_k2": bool(abs(fit2.loglik - published.loc[2, "loglik"]) < 1e-6),
            "reproduces_published_k3": bool(abs(fit3.loglik - published.loc[3, "loglik"]) < 1e-6),
            "nesting_start_loglik_k3": fit3n.loglik,
            "nesting_start_selected": fit3n.record.start_used,
            "nesting_start_converged": bool(fit3n.record.converged),
            "nesting_k3_minus_k2": fit3n.loglik - fit2.loglik,
            "nesting_k3_minus_published_k3": fit3n.loglik - float(published.loc[3, "loglik"]),
            "nesting_k3_status": fit3n.record.status.value,
            "nesting_k3_reason_codes": ";".join(c.value for c in fit3n.record.reason_codes),
            "nesting_k3_occupancy": "; ".join(f"{v:.4f}" for v in np.sort(fit3n.occupancy))
            if getattr(fit3n, "occupancy", None) is not None and len(fit3n.occupancy) else "",
            "seconds_k2": round(t2, 1), "seconds_k3_published_starts": round(t3, 1),
            "seconds_k3_with_nesting_start": round(t3n, 1),
        })
        print(rows[-1], flush=True)
        pd.DataFrame(rows).to_csv(DEST, index=False)   # after every target


if __name__ == "__main__":
    main()
