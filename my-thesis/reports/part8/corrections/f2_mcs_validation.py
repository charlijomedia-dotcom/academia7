"""F2 validation: the guarded HLN MCS (`hln_mcs_r`) against `arch` (read-only).

For every baseline MCS cell (6 targets x horizons x {squared, absolute} x {90%, 95%})
this script rebuilds the loss matrix from the stored forecasts of run
baseline-20261030T173044-949fcd76 exactly as `model_confidence_set` does (horse-race
models at that horizon, intersection of scoreable dates, decision D11 settings), then:

* runs `arch.bootstrap.MCS` directly;
* runs `hln_mcs_r` directly (bypassing the arch-first dispatch);
* where `arch` succeeds, checks that both give identical p-values and membership;
* on the published (pre-F1) frames, also checks that `arch` reproduces the published
  `output/forecast_tests/T3.4_model_confidence_set.csv` membership and p-values, which
  confirms the harness rebuilds the same loss matrices as the pipeline.

Two frame variants are validated: `published` (forecasts exactly as stored, failed rows
scored as in the original run) and `f1_masked` (failed rows unscored, as after F1).

Run from `my-thesis/`:  python reports/part8/corrections/f2_mcs_validation.py
Writes `reports/part8/corrections/f2_mcs_validation.csv`.
"""

from __future__ import annotations

import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "src"))

from thesis.core.config import load_config  # noqa: E402
from thesis.core.paths import CONFIG_DIR  # noqa: E402
from thesis.evaluation import alignment  # noqa: E402
from thesis.evaluation.losses import loss  # noqa: E402
from thesis.evaluation.mcs import MCSNumericalError, hln_mcs_r  # noqa: E402
from thesis.evaluation.scoring import mask_failed  # noqa: E402

OUT = ROOT / "output"
DEST = Path(__file__).resolve().parent / "f2_mcs_validation.csv"
MODELS = ("AR", "ARMA", "MSAR", "STAR")


def main() -> None:
    config = load_config(names=("baseline", "series_catalog", "thresholds"), config_dir=CONFIG_DIR)
    settings = config.get("evaluation.mcs")
    reps, seed = int(settings["replications"]), int(settings["seed"])
    published = pd.read_csv(OUT / "forecast_tests" / "T3.4_model_confidence_set.csv")
    rows = []
    for series in ("GDPC1", "CPIAUCSL", "UNRATE", "INDPRO", "FEDFUNDS", "M2SL"):
        forecasts = pd.read_csv(OUT / "forecasts" / f"forecasts_{series}.csv",
                                parse_dates=["origin_date", "target_date"])
        for variant in ("published", "f1_masked"):
            frame_all = forecasts if variant == "published" else mask_failed(forecasts)
            for horizon in sorted(frame_all.horizon.unique()):
                frames = {m: frame_all[(frame_all.model == m) & (frame_all.horizon == horizon)]
                          for m in MODELS}
                if variant == "published":
                    # The original run aligned on finite forecasts only.
                    def valid(f):
                        return set(f[np.isfinite(f.forecast) & np.isfinite(f.actual)].target_date)
                    dates = sorted(set.intersection(*(valid(f) for f in frames.values())))
                    dates = pd.DatetimeIndex(dates)
                else:
                    dates = alignment.across_models(frames).dates
                for loss_kind in ("squared", "absolute"):
                    errors = {m: alignment.restrict(f, dates)["error"].to_numpy(float)
                              for m, f in frames.items()}
                    losses = pd.DataFrame({m: loss(e, loss_kind) for m, e in errors.items()},
                                          index=dates)
                    block = max(1, int(math.ceil(math.sqrt(len(dates)))))
                    for confidence in (0.9, 0.95):
                        size = 1.0 - confidence
                        row = {"variant": variant, "series": series, "horizon": int(horizon),
                               "loss": loss_kind, "confidence": confidence,
                               "t_common": len(dates), "block_length": block}
                        try:
                            from arch.bootstrap import MCS
                            with warnings.catch_warnings():
                                warnings.simplefilter("ignore")
                                proc = MCS(losses, size=size, reps=reps, block_size=block,
                                           method="R", bootstrap="stationary", seed=seed)
                                proc.compute()
                            arch_p = {str(k): float(v.iloc[0]) for k, v in proc.pvalues.iterrows()}
                            arch_var_finite = bool(np.isfinite(proc._variances).all())
                            row.update(arch_status="ok" if arch_var_finite else "ok_but_overflow",
                                       arch_included=",".join(map(str, proc.included)))
                        except Exception as exc:  # noqa: BLE001
                            arch_p, arch_var_finite = None, None
                            row.update(arch_status=f"failed: {type(exc).__name__}",
                                       arch_included="")
                        try:
                            p, inc, exc_, diag = hln_mcs_r(losses, size, reps, block, seed)
                            guarded_p = {str(k): float(v) for k, v in p.items()}
                            row.update(guarded_status="ok", guarded_included=",".join(inc),
                                       rescaled_variance_cells=diag["rescaled_variance_cells"],
                                       tied_elimination_steps=diag["tied_elimination_steps"],
                                       guarded_p_values="; ".join(
                                           f"{m}={guarded_p[m]:.4f}" for m in sorted(guarded_p)))
                        except MCSNumericalError as exc:
                            guarded_p = None
                            row.update(guarded_status=f"unavailable: {exc}", guarded_included="")
                        if arch_p is not None and guarded_p is not None and arch_var_finite:
                            row["identical_to_arch"] = (
                                set(arch_p) == set(guarded_p)
                                and all(arch_p[m] == guarded_p[m] for m in arch_p)
                                and row["arch_included"] == row["guarded_included"])
                            row["max_abs_p_difference"] = max(abs(arch_p[m] - guarded_p[m])
                                                              for m in arch_p)
                        if variant == "published":
                            pub = published[(published.series == series)
                                            & (published.horizon == horizon)
                                            & (published["loss"] == loss_kind)
                                            & (np.isclose(published.confidence_level, confidence))]
                            available = pub.inference_available.astype(bool).all() and len(pub)
                            row["published_available"] = bool(available)
                            if available and arch_p is not None:
                                pub_p = dict(zip(pub.model.astype(str), pub.mcs_p_value.astype(float)))
                                pub_inc = ",".join(sorted(pub[pub.in_mcs.astype(bool)].model.astype(str)))
                                row["arch_reproduces_publication"] = (
                                    pub_inc == row["arch_included"]
                                    and all(abs(pub_p[m] - arch_p[m]) < 1e-12 for m in arch_p))
                        rows.append(row)
                        print({k: row.get(k) for k in ("variant", "series", "horizon", "loss",
                                                        "confidence", "arch_status",
                                                        "guarded_status", "identical_to_arch",
                                                        "arch_reproduces_publication")},
                              flush=True)
    table = pd.DataFrame(rows)
    table.to_csv(DEST, index=False)
    ok = table[table.arch_status == "ok"]
    print("\ncells:", len(table), "| arch ok:", len(ok),
          "| guarded identical where arch ok:", int(ok.identical_to_arch.sum()), "/", len(ok))
    pub = table[(table.variant == "published") & table.published_available.fillna(False).astype(bool)]
    print("published cells reproduced by arch:",
          int(pub.arch_reproduces_publication.fillna(False).sum()), "/", len(pub))


if __name__ == "__main__":
    main()
