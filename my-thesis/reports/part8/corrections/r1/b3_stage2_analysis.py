"""Option B3 stage 2: analyse the verified Colab export (read-only; no estimation).

usage: stage2_analysis.py EXPORT_ROOT REPO_MYTHESIS OUT_DIR
"""
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

root, repo, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
ref_dir, cand_dir = root / "impact" / "reference_tables", root / "impact" / "candidate_tables"
KEYS = ["series", "model", "horizon", "loss", "model_a", "model_b", "window_length", "state",
        "window", "turning_window_width", "confidence_level", "exercise", "role", "frequency"]
DECISIONS = ["decision_5pct", "in_mcs", "rank_rmse", "rank_mae", "agrees_with_hlz", "stars",
             "model_status", "dominant_status", "rank_changed_by_var", "rank_with_var",
             "rank_univariate_only", "hlz_squared_decision_5pct", "hlz_absolute_decision_5pct",
             "inference_available"]
SKIP = {"run_id", "created_utc", "code_commit_sha", "data_snapshot_hash", "config_hash"}


def same(x, y):
    if pd.isna(x) and pd.isna(y):
        return True
    try:
        return float(x) == float(y)
    except (TypeError, ValueError):
        return str(x) == str(y)


cells, flips, tables = [], [], {}
for path in sorted(p.relative_to(ref_dir).as_posix() for p in ref_dir.rglob("*.csv")):
    a = pd.read_csv(ref_dir / path, low_memory=False, float_precision="round_trip")
    b = pd.read_csv(cand_dir / path, low_memory=False, float_precision="round_trip")
    info = {"rows": len(a), "shape_equal": a.shape == b.shape, "changed_cells": 0,
            "changed_rows": 0, "decision_flips": 0}
    if a.shape != b.shape or list(a.columns) != list(b.columns):
        tables[path] = info
        continue
    keys = [k for k in KEYS if k in a.columns]
    changed_rows = set()
    for column in a.columns:
        if column in SKIP:
            continue
        for i in range(len(a)):
            x, y = a.at[i, column], b.at[i, column]
            if same(x, y):
                continue
            key = {k: a.at[i, k] for k in keys}
            changed_rows.add(i)
            entry = {"table": path, "row": i, **{f"key_{k}": v for k, v in key.items()},
                     "column": column, "reference": x, "candidate": y}
            try:
                entry["difference"] = float(y) - float(x)
            except (TypeError, ValueError):
                entry["difference"] = ""
            cells.append(entry)
            if column in DECISIONS:
                flips.append(entry)
                info["decision_flips"] += 1
            info["changed_cells"] += 1
    info["changed_rows"] = len(changed_rows)
    tables[path] = info


def write(name, rows):
    fields = []
    for r in rows:
        fields += [k for k in r if k not in fields]
    with open(out / name, "w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields or ["empty"])
        w.writeheader()
        w.writerows(rows)


write("changed_cells_keyed.csv", cells)
write("decision_flips.csv", flips)

# -- forecasts: every UNRATE MSAR origin and horizon -------------------------------------
fa = pd.read_csv(ref_dir / "forecasts" / "forecasts_UNRATE.csv", float_precision="round_trip")
fb = pd.read_csv(cand_dir / "forecasts" / "forecasts_UNRATE.csv", float_precision="round_trip")
ma, mb = fa[fa.model == "MSAR"], fb[fb.model == "MSAR"]
m = ma.merge(mb, on=["origin_date", "horizon"], suffixes=("_ref", "_cand"), how="outer",
             indicator=True)
assert (m["_merge"] == "both").all()
_prov = [c for c in fa.columns if c not in SKIP]
others_same = fa[fa.model != "MSAR"][_prov].reset_index(drop=True).equals(fb[fb.model != "MSAR"][_prov].reset_index(drop=True))
m["status_changed"] = m.status_ref != m.status_cand
m["codes_changed"] = m.reason_codes_ref.fillna("") != m.reason_codes_cand.fillna("")
m["forecast_changed"] = ~((m.forecast_ref.isna() & m.forecast_cand.isna())
                          | (m.forecast_ref == m.forecast_cand))
m["abs_forecast_change"] = (m.forecast_cand - m.forecast_ref).abs()
ch = m[m.status_changed | m.codes_changed | m.forecast_changed]
ch[["origin_date", "horizon", "status_ref", "status_cand", "reason_codes_ref", "reason_codes_cand",
    "forecast_ref", "forecast_cand", "actual_ref", "error_ref", "error_cand"]].to_csv(
    out / "forecast_changes_unrate_msar.csv", index=False)
origins = sorted(ch.origin_date.unique())
forecasts = {
    "other_models_unchanged": bool(others_same), "rows": int(len(m)),
    "rows_changed": int(len(ch)), "origins_changed": len(origins), "origin_dates": origins,
    "status_changes": {f"{a}->{b}": int(n) for (a, b), n in
                       ch[ch.status_changed].groupby(["status_ref", "status_cand"]).size().items()},
    "forecast_rows_changed_by_horizon": {int(h): int(n) for h, n in
                                         ch[ch.forecast_changed].groupby("horizon").size().items()},
    "max_abs_forecast_change_where_both_finite": float(np.nanmax(ch.abs_forecast_change)) if ch.abs_forecast_change.notna().any() else None}

# -- origin-level fit comparison (published record vs candidate) ---------------------------
sys.path.insert(0, str(repo / "colab"))
import r1_tierb as tb  # noqa: E402
import r1_original_cache_audit as audit  # noqa: E402
tb.use_scientific_code(repo / "code")
jobs, identity, config = tb.build_jobs(repo / "output", repo / "code")
fr = pd.read_parquet(repo / "output" / "models" / "fit_records.parquet")
published, provenance = audit.stage_block(fr, jobs["forecasting:UNRATE|MSAR"])
t48, _ = audit.stage_block(fr, jobs["T4.8:UNRATE|240:MSAR"])
cand = pd.read_csv(root / "candidate" / "candidate_fit_records.csv", float_precision="round_trip")
cand["refit_date"] = cand.refit_date.astype(str).str[:10]
dates = sorted(published)
origin_rows = []
for i, d in enumerate(dates):
    p, c = published[d], cand[cand.refit_date == d].iloc[0]
    differs = not (p.status == c.status and audit.codes(p.reason_codes) == audit.codes(c.reason_codes)
                   and same(p.loglik, c.loglik))
    if not differs:
        continue
    prev_failed = i > 0 and published[dates[i - 1]].status == "failed"
    pub_starts = audit.start_set(p.diagnostics)
    warm_pub = "warm" in pub_starts
    if p.status == "failed" and c.status == "failed":
        category = "both failed (genuine failure in both); different failed optimum"
    elif not warm_pub and c.start_used == "warm":
        category = "implementation artifact: published fit had no warm start (D6) after a failed fit; candidate's best start is the warm start"
    elif not warm_pub:
        category = "implementation artifact: published fit had no warm start; candidate (warm start offered) chose another start"
    else:
        category = "inherited divergence: warm start offered in both, from a different previous fit"
    origin_rows.append({
        "refit_date": d, "previous_published_failed": prev_failed,
        "status_published": p.status, "status_candidate": c.status,
        "codes_published": audit.codes(p.reason_codes), "codes_candidate": c.reason_codes if isinstance(c.reason_codes, str) else "",
        "loglik_published": p.loglik, "loglik_candidate": c.loglik,
        "loglik_candidate_minus_published": (c.loglik - p.loglik) if pd.notna(c.loglik) and pd.notna(p.loglik) else "",
        "warm_start_offered_published": warm_pub, "start_published": p.start_used,
        "start_candidate": c.start_used,
        "t48_record_same_as_published": same(t48[d].loglik, p.loglik) and t48[d].status == p.status,
        "category": category})
write("origin_level_classification.csv", origin_rows)

# -- headline metrics ----------------------------------------------------------------------
def rows(path, **filt):
    a = pd.read_csv(ref_dir / path, low_memory=False, float_precision="round_trip")
    b = pd.read_csv(cand_dir / path, low_memory=False, float_precision="round_trip")
    mask = np.ones(len(a), bool)
    for k, v in filt.items():
        mask &= (a[k] == v).to_numpy()
    return a[mask], b[mask]

a, b = rows("forecast_tests/T3.3_main_forecast_table.csv", series="UNRATE")
cols = ["model", "horizon", "n_valid", "n_failed", "rmse", "mae", "oos_r2_vs_benchmark",
        "rank_rmse", "rank_mae", "hlz_squared_p_value", "hlz_squared_decision_5pct",
        "hlz_absolute_p_value", "hlz_absolute_decision_5pct"]
t33 = a[cols].merge(b[cols], on=["model", "horizon"], suffixes=("_ref", "_cand"))
t33.to_csv(out / "T3.3_unrate_reference_vs_candidate.csv", index=False)
a, b = rows("forecast_tests/T3.4_model_confidence_set.csv", series="UNRATE")
cols = ["horizon", "loss", "model", "in_mcs", "mcs_p_value"]
t34 = a[cols].merge(b[cols], on=["horizon", "loss", "model"], suffixes=("_ref", "_cand"))
t34.to_csv(out / "T3.4_unrate_mcs_reference_vs_candidate.csv", index=False)

summary = {
    "export_session": json.loads((root / "export_manifest.json").read_text())["session"],
    "tables_compared": len(tables), "tables": tables,
    "changed_cells": len(cells), "decision_flips": len(flips),
    "decision_flips_by_table": {k: v["decision_flips"] for k, v in tables.items() if v["decision_flips"]},
    "forecasts": forecasts, "published_block": provenance,
    "origin_level_differences": len(origin_rows),
    "origin_level_categories": pd.Series([r["category"] for r in origin_rows]).value_counts().to_dict(),
}
(out / "stage2_summary.json").write_text(json.dumps(summary, indent=1, default=str))
print(json.dumps({k: v for k, v in summary.items() if k != "tables"}, indent=1, default=str))
