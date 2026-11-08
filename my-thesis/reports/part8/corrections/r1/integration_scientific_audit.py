"""Read-only scientific-impact audit of the Part 8 integration dry run (8 November 2026).

    python integration_scientific_audit.py EXPORT_DIR CLAIMS_REFERENCE_DIR PUBLISHED_OUTPUT_DIR OUT_DIR

EXPORT_DIR            the 45 exported files of session integration-20261108T052245Z-9bba8e
                      (paths as in its export_manifest.json)
CLAIMS_REFERENCE_DIR  output_corrected/ of the claims-reference release 0573a8c
PUBLISHED_OUTPUT_DIR  the published output/ (results commit 0662945)

Estimates nothing. Integrated-release tables are rebuilt as "claims-reference file + every
changed cell exported in cells_vs_claims_reference.csv.gz"; unchanged cells keep the
reference text. Writes the derived CSV/JSON files used in part8_integration_scientific_audit.md.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

EXPORT, REF, PUB, OUT = (Path(a) for a in sys.argv[1:5])
OUT.mkdir(parents=True, exist_ok=True)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# 1. export integrity --------------------------------------------------------------------
man = json.loads((EXPORT / "export_manifest.json").read_text())
bad = [f["path"] for f in man["files"]
       if sha(EXPORT / f["path"]) != f["sha256"] or (EXPORT / f["path"]).stat().st_size != f["bytes"]]
integrity = {"files_in_manifest": len(man["files"]), "verified": len(man["files"]) - len(bad),
             "mismatches": bad, "export_manifest_sha256": sha(EXPORT / "export_manifest.json"),
             **{k: man[k] for k in man if k != "files"}}
(OUT / "export_verification.json").write_text(json.dumps(integrity, indent=1))

# 2. decision-like changes by category and reference ------------------------------------------
def category(c: str) -> str:
    if c in ("status", "model_status", "forecast_status"):
        return "D status classification"
    if "decision" in c:
        return "A 5% test decision"
    if c == "stars":
        return "B significance stars"
    if c.startswith("rank"):
        return "C descriptive rank"
    if c in ("conclusion_vs_baseline", "support_change"):
        return "E derived robustness label"
    return "F other"


cells = {name: pd.read_csv(EXPORT / f, low_memory=False) for name, f in [
    ("vs_b1_staged_base", "cells_vs_b1_staged.csv.gz"),
    ("vs_claims_reference_0573a8c", "cells_vs_claims_reference.csv.gz"),
    ("vs_tier_a_292227e", "cells_vs_tier_a.csv.gz"),
    ("vs_published_0662945", "cells_vs_published.csv.gz")]}
tab = {}
for name, d in cells.items():
    dd = d[d.decision_like == True]  # noqa: E712
    tab[name] = dd.column.map(category).value_counts()
cat = pd.DataFrame(tab).fillna(0).astype(int).sort_index()
cat.loc["TOTAL"] = cat.sum()
cat.to_csv(OUT / "decision_change_categories.csv")
base = cells["vs_b1_staged_base"]
b = base[base.decision_like == True].copy()  # noqa: E712
b["category"] = b.column.map(category)
pd.crosstab(b.category, b.cause).to_csv(OUT / "decision_changes_vs_base_by_cause.csv")

# 3. every 5% test-decision change against the published output, with its p-values ----------
P, C = cells["vs_published_0662945"], cells["vs_claims_reference_0573a8c"]
rows = []
for _, r in P[(P.decision_like == True) & P.column.str.contains("decision")].iterrows():  # noqa: E712
    same = P[(P.path == r.path) & (P.row == r.row)]
    pv = {c.column: (c.old, c.new) for _, c in same.iterrows()
          if any(k in c.column for k in ("p_value", "statistic", "mean_loss"))}
    rows.append({"path": r.path, "row": r.row, "column": r.column, "old": r.old, "new": r.new,
                 "series": r.key_series, "model": r.key_model, "horizon": r.key_horizon,
                 "window": r.key_window_length, "loss": r.key_loss, "role": r.key_role,
                 "transformation": r.key_transformation, "name": r.key_name,
                 "new_relative_to_claims_reference": bool(((C.path == r.path) & (C.row == r.row)
                                                           & (C.column == r.column)).any()),
                 "values_old_new": json.dumps(pv)})
pd.DataFrame(rows).to_csv(OUT / "test_decision_changes_vs_published.csv", index=False)


# 4. rebuilt integrated tables ------------------------------------------------------------
def rebuild(path: str) -> pd.DataFrame:
    ref = pd.read_csv(REF / path, low_memory=False).astype(object)
    for _, c in C[C.path == path].iterrows():
        if c.row >= len(ref):
            raise SystemExit(f"{path}: changed row {c.row} beyond the reference table")
        ref.at[c.row, c.column] = c.new
    return ref


rebuilt = OUT / "rebuilt_integrated_tables"
for path in ("robustness/T4.1_transformation_robustness.csv",
             "robustness/T4.1_transformation_predictive_tests.csv",
             "robustness/window_length_comparison.csv",
             "robustness/window_length_predictive_tests.csv",
             "robustness/T4.2_cpi_lag_robustness.csv",
             "robustness/T4.2_cpi_lag_predictive_tests.csv",
             "forecast_tests/T3.3_main_forecast_table.csv",
             "forecast_tests/T3.5_state_loss_regression.csv",
             "diagnostics/all_test_results.csv",
             "data_audit/T4.9_locf_sample_comparison.csv",
             "forecasts/forecasts_UNRATE.csv"):
    t = rebuild(path)
    (rebuilt / path).parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(rebuilt / path, index=False)

# 5. Wald rows of all_test_results: published vs integrated ------------------------------
pub = pd.read_csv(PUB / "diagnostics/all_test_results.csv")
ref = pd.read_csv(REF / "diagnostics/all_test_results.csv")
new = pd.read_csv(rebuilt / "diagnostics/all_test_results.csv")
w = sorted(set(C[C.path == "diagnostics/all_test_results.csv"].row) |
           set(P[P.path == "diagnostics/all_test_results.csv"].row))
pd.DataFrame({"row": w, "series": new.loc[w, "series"].values, "model": new.loc[w, "model"].values,
              "name": new.loc[w, "name"].values,
              "p_published": pub.loc[w, "p_value"].values,
              "p_claims_reference": ref.loc[w, "p_value"].values,
              "p_integrated": new.loc[w, "p_value"].astype(float).values,
              "decision_published": pub.loc[w, "decision_5pct"].values,
              "decision_integrated": new.loc[w, "decision_5pct"].values}).to_csv(
    OUT / "wald_rows_published_vs_integrated.csv", index=False)
t35 = {k: pd.read_csv(r / "forecast_tests/T3.5_state_loss_regression.csv")
       for k, r in (("published", PUB), ("claims_reference", REF), ("integrated", rebuilt))}
keep = ["series", "model", "horizon", "loss", "n", "n_recession", "n_turning_window", "alpha", "alpha_p",
        "beta_rec", "beta_rec_p", "beta_turn", "beta_turn_p", "joint_wald_statistic", "joint_wald_p",
        "slopes_wald_statistic", "slopes_wald_p"]
pd.concat([v.loc[(v.series == "UNRATE") & (v.model == "ARMA vs AR") & (v.horizon == 1), keep].assign(release=k)
           for k, v in t35.items()]).to_csv(OUT / "unrate_arma_vs_ar_state_regression_h1.csv", index=False)

# 6. UNRATE h=1: own-sample RMSE vs the common sample (the May 2020 target) ------------------
f = pd.read_csv(rebuilt / "forecasts/forecasts_UNRATE.csv")
f = f[pd.to_numeric(f.horizon) == 1]
f["error"] = pd.to_numeric(f.error, errors="coerce")
common = set.intersection(*(set(f[(f.model == m) & f.error.notna()].target_date)
                            for m in ("AR", "ARMA", "MSAR", "STAR")))
out = []
for m in ("AR", "ARMA", "MSAR", "STAR"):
    e = f[(f.model == m) & f.error.notna()]
    c = e[e.target_date.isin(common)]
    may = f[(f.model == m) & (f.target_date == "2020-05-01")]
    out.append({"model": m, "n_own": len(e), "rmse_own": float(np.sqrt((e.error ** 2).mean())),
                "n_common_all_four": len(c), "rmse_common_all_four": float(np.sqrt((c.error ** 2).mean())),
                "status_2020_05": may.status.iloc[0], "error_2020_05": may.error.iloc[0]})
pd.DataFrame(out).to_csv(OUT / "unrate_h1_own_vs_common_sample.csv", index=False)

# 7. report lines flagged by A14 ---------------------------------------------------------
pd.read_csv(EXPORT / "report_numbers_changed.csv").groupby(["report"]).size().to_csv(
    OUT / "report_lines_flagged_by_report.csv")
print(json.dumps({"verified": integrity["verified"], "mismatches": len(bad),
                  "decision_like_vs_base": int(cat.loc["TOTAL", "vs_b1_staged_base"])}))
