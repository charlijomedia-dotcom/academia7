"""Option B3 stage 2: analyse the verified Colab export (read-only; no estimation).

usage: b3_stage2_analysis.py EXPORT_ROOT REPO_MYTHESIS OUT_DIR

Revision 2 (B1 preparation): every keyed comparison now goes through `keyed_merge`, which
refuses duplicate keys and many-to-many joins. Revision 1 merged the T3.4 model-confidence-set
rows on (horizon, loss, model) without `confidence_level`, so each row was paired with both
confidence levels (128 rows instead of 64). The cell-level comparison (positional, with the
key columns now asserted identical row by row) was not affected; the extract was.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KEYS = ["series", "model", "horizon", "loss", "model_a", "model_b", "window_length", "state",
        "window", "turning_window_width", "confidence_level", "exercise", "role", "frequency"]
DECISIONS = ["decision_5pct", "in_mcs", "rank_rmse", "rank_mae", "agrees_with_hlz", "stars",
             "model_status", "dominant_status", "rank_changed_by_var", "rank_with_var",
             "rank_univariate_only", "hlz_squared_decision_5pct", "hlz_absolute_decision_5pct",
             "inference_available"]
SKIP = {"run_id", "created_utc", "code_commit_sha", "data_snapshot_hash", "config_hash"}
# The identifying keys of the two extracts written for the review.
T33_KEYS = ["series", "model", "horizon"]
T34_KEYS = ["series", "horizon", "loss", "confidence_level", "model"]
WL_MCS_KEYS = ["series", "window_length", "horizon", "loss", "confidence_level", "model"]


class ComparisonError(AssertionError):
    pass


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False, float_precision="round_trip")


def same(x, y) -> bool:
    if pd.isna(x) and pd.isna(y):
        return True
    try:
        return float(x) == float(y)
    except (TypeError, ValueError):
        return str(x) == str(y)


def assert_unique(frame: pd.DataFrame, keys: list[str], label: str) -> None:
    missing = [k for k in keys if k not in frame.columns]
    if missing:
        raise ComparisonError(f"{label}: key columns missing {missing}")
    dup = frame.duplicated(keys, keep=False)
    if dup.any():
        raise ComparisonError(f"{label}: {int(dup.sum())} rows share a key {keys}")


def keyed_merge(a: pd.DataFrame, b: pd.DataFrame, keys: list[str], columns: list[str],
                label: str = "") -> pd.DataFrame:
    """One-to-one merge of reference (a) and candidate (b) on unique, identical key sets."""
    assert_unique(a, keys, f"{label} reference")
    assert_unique(b, keys, f"{label} candidate")
    ka = set(map(tuple, a[keys].astype(str).to_numpy()))
    kb = set(map(tuple, b[keys].astype(str).to_numpy()))
    if ka != kb:
        raise ComparisonError(f"{label}: key sets differ ({len(ka - kb)} only in reference, "
                              f"{len(kb - ka)} only in candidate)")
    cols = keys + [c for c in columns if c not in keys]
    merged = a[cols].merge(b[cols], on=keys, suffixes=("_ref", "_cand"), validate="one_to_one")
    if len(merged) != len(a):
        raise ComparisonError(f"{label}: merged {len(merged)} rows from {len(a)}")
    return merged


def compare_table(a: pd.DataFrame, b: pd.DataFrame, path: str):
    """Cell-level comparison of two regenerations of one table (same row order)."""
    info = {"rows": len(a), "shape_equal": a.shape == b.shape, "changed_cells": 0,
            "changed_rows": 0, "decision_flips": 0}
    cells, flips = [], []
    if a.shape != b.shape or list(a.columns) != list(b.columns):
        return info, cells, flips
    keys = [k for k in KEYS if k in a.columns]
    for k in keys:  # positional alignment must be key alignment
        if not all(same(x, y) for x, y in zip(a[k], b[k])):
            raise ComparisonError(f"{path}: key column {k} not aligned row by row")
    info["keys"] = keys
    info["keys_unique"] = bool(keys) and not a.duplicated(keys).any()
    changed_rows = set()
    for column in a.columns:
        if column in SKIP:
            continue
        for i in range(len(a)):
            x, y = a.at[i, column], b.at[i, column]
            if same(x, y):
                continue
            changed_rows.add(i)
            entry = {"table": path, "row": i, **{f"key_{k}": a.at[i, k] for k in keys},
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
    return info, cells, flips


def mcs_extract(a: pd.DataFrame, b: pd.DataFrame, series: str = "UNRATE",
                keys: list[str] = T34_KEYS, label: str = "T3.4") -> pd.DataFrame:
    a, b = a[a.series == series], b[b.series == series]
    merged = keyed_merge(a, b, keys, ["in_mcs", "mcs_p_value"], label)
    merged["membership_changed"] = merged.in_mcs_ref.astype(str) != merged.in_mcs_cand.astype(str)
    return merged


def mcs_summary(merged: pd.DataFrame, keys: list[str] = T34_KEYS) -> dict:
    p = (merged.mcs_p_value_cand - merged.mcs_p_value_ref).abs()
    worst = merged.loc[p.idxmax()]
    return {"rows": int(len(merged)), "membership_changes": int(merged.membership_changed.sum()),
            "in_mcs_reference": int(merged.in_mcs_ref.astype(str).eq("True").sum()),
            "in_mcs_candidate": int(merged.in_mcs_cand.astype(str).eq("True").sum()),
            "max_abs_p_value_change": float(p.max()),
            "max_at": {k: (worst[k].item() if hasattr(worst[k], "item") else worst[k])
                       for k in keys + ["mcs_p_value_ref", "mcs_p_value_cand"]}}


def write(path: Path, rows: list[dict]) -> None:
    fields = []
    for r in rows:
        fields += [k for k in r if k not in fields]
    with open(path, "w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields or ["empty"])
        w.writeheader()
        w.writerows(rows)


def main(root: Path, repo: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    ref_dir, cand_dir = root / "impact" / "reference_tables", root / "impact" / "candidate_tables"
    cells, flips, tables = [], [], {}
    for path in sorted(p.relative_to(ref_dir).as_posix() for p in ref_dir.rglob("*.csv")):
        info, c, f = compare_table(read(ref_dir / path), read(cand_dir / path), path)
        tables[path] = info
        cells += c
        flips += f
    write(out / "changed_cells_keyed.csv", cells)
    write(out / "decision_flips.csv", flips)

    # -- forecasts: every UNRATE MSAR origin and horizon --------------------------------
    fa = read(ref_dir / "forecasts" / "forecasts_UNRATE.csv")
    fb = read(cand_dir / "forecasts" / "forecasts_UNRATE.csv")
    m = keyed_merge(fa[fa.model == "MSAR"], fb[fb.model == "MSAR"], ["origin_date", "horizon"],
                    [c for c in fa.columns if c not in SKIP], "forecasts_UNRATE MSAR")
    prov = [c for c in fa.columns if c not in SKIP]
    others_same = fa[fa.model != "MSAR"][prov].reset_index(drop=True).equals(
        fb[fb.model != "MSAR"][prov].reset_index(drop=True))
    m["status_changed"] = m.status_ref != m.status_cand
    m["codes_changed"] = m.reason_codes_ref.fillna("") != m.reason_codes_cand.fillna("")
    m["forecast_changed"] = ~((m.forecast_ref.isna() & m.forecast_cand.isna())
                              | (m.forecast_ref == m.forecast_cand))
    m["abs_forecast_change"] = (m.forecast_cand - m.forecast_ref).abs()
    ch = m[m.status_changed | m.codes_changed | m.forecast_changed]
    ch[["origin_date", "horizon", "status_ref", "status_cand", "reason_codes_ref",
        "reason_codes_cand", "forecast_ref", "forecast_cand", "actual_ref", "error_ref",
        "error_cand"]].to_csv(out / "forecast_changes_unrate_msar.csv", index=False)
    origins = sorted(ch.origin_date.unique())
    forecasts = {
        "other_models_unchanged": bool(others_same), "rows": int(len(m)),
        "rows_changed": int(len(ch)), "origins_changed": len(origins), "origin_dates": origins,
        "status_changes": {f"{a}->{b}": int(n) for (a, b), n in
                           ch[ch.status_changed].groupby(["status_ref", "status_cand"]).size().items()},
        "forecast_rows_changed_by_horizon": {int(h): int(n) for h, n in
                                             ch[ch.forecast_changed].groupby("horizon").size().items()},
        "max_abs_forecast_change_where_both_finite": float(np.nanmax(ch.abs_forecast_change))
        if ch.abs_forecast_change.notna().any() else None}

    # -- origin-level fit comparison (published record vs candidate) -------------------
    sys.path.insert(0, str(repo / "colab"))
    import r1_original_cache_audit as audit
    import r1_tierb as tb
    tb.use_scientific_code(repo / "code")
    jobs, _identity, _config = tb.build_jobs(repo / "output", repo / "code")
    fr = pd.read_parquet(repo / "output" / "models" / "fit_records.parquet")
    published, provenance = audit.stage_block(fr, jobs["forecasting:UNRATE|MSAR"])
    t48, _ = audit.stage_block(fr, jobs["T4.8:UNRATE|240:MSAR"])
    cand = read(root / "candidate" / "candidate_fit_records.csv")
    cand["refit_date"] = cand.refit_date.astype(str).str[:10]
    assert_unique(cand, ["refit_date"], "candidate fit records")
    dates = sorted(published)
    origin_rows = []
    for i, d in enumerate(dates):
        p, c = published[d], cand[cand.refit_date == d].iloc[0]
        if (p.status == c.status and audit.codes(p.reason_codes) == audit.codes(c.reason_codes)
                and same(p.loglik, c.loglik)):
            continue
        warm_pub = "warm" in audit.start_set(p.diagnostics)
        if p.status == "failed" and c.status == "failed":
            category = "both failed (genuine failure in both); different failed optimum"
        elif not warm_pub and c.start_used == "warm":
            category = ("implementation artifact: published fit had no warm start (D6) after a "
                        "failed fit; candidate's best start is the warm start")
        elif not warm_pub:
            category = ("implementation artifact: published fit had no warm start; candidate "
                        "(warm start offered) chose another start")
        else:
            category = "inherited divergence: warm start offered in both, from a different previous fit"
        origin_rows.append({
            "refit_date": d, "previous_published_failed": i > 0 and published[dates[i - 1]].status == "failed",
            "status_published": p.status, "status_candidate": c.status,
            "codes_published": audit.codes(p.reason_codes),
            "codes_candidate": c.reason_codes if isinstance(c.reason_codes, str) else "",
            "loglik_published": p.loglik, "loglik_candidate": c.loglik,
            "loglik_candidate_minus_published": (c.loglik - p.loglik)
            if pd.notna(c.loglik) and pd.notna(p.loglik) else "",
            "warm_start_offered_published": warm_pub, "start_published": p.start_used,
            "start_candidate": c.start_used,
            "t48_record_same_as_published": same(t48[d].loglik, p.loglik) and t48[d].status == p.status,
            "category": category})
    write(out / "origin_level_classification.csv", origin_rows)

    # -- headline extracts (keyed, one-to-one) ------------------------------------------
    a, b = read(ref_dir / "forecast_tests/T3.3_main_forecast_table.csv"), read(cand_dir / "forecast_tests/T3.3_main_forecast_table.csv")
    t33 = keyed_merge(a[a.series == "UNRATE"], b[b.series == "UNRATE"], T33_KEYS,
                      ["n_valid", "n_failed", "rmse", "mae", "oos_r2_vs_benchmark", "rank_rmse",
                       "rank_mae", "hlz_squared_p_value", "hlz_squared_decision_5pct",
                       "hlz_absolute_p_value", "hlz_absolute_decision_5pct"], "T3.3")
    t33.to_csv(out / "T3.3_unrate_reference_vs_candidate.csv", index=False)
    t34 = mcs_extract(read(ref_dir / "forecast_tests/T3.4_model_confidence_set.csv"),
                      read(cand_dir / "forecast_tests/T3.4_model_confidence_set.csv"))
    t34.to_csv(out / "T3.4_unrate_mcs_reference_vs_candidate.csv", index=False)
    wl = mcs_extract(read(ref_dir / "robustness/window_length_mcs.csv"),
                     read(cand_dir / "robustness/window_length_mcs.csv"), keys=WL_MCS_KEYS,
                     label="window_length_mcs")
    wl.to_csv(out / "window_length_mcs_unrate_reference_vs_candidate.csv", index=False)

    summary = {
        "analysis_revision": 2,
        "export_session": json.loads((root / "export_manifest.json").read_text())["session"],
        "tables_compared": len(tables), "tables": tables,
        "changed_cells": len(cells), "decision_flips": len(flips),
        "decision_flips_by_table": {k: v["decision_flips"] for k, v in tables.items() if v["decision_flips"]},
        "forecasts": forecasts, "published_block": provenance,
        "origin_level_differences": len(origin_rows),
        "origin_level_categories": pd.Series([r["category"] for r in origin_rows]).value_counts().to_dict(),
        "t3_3_unrate_rows": int(len(t33)),
        "t3_4_unrate_mcs": mcs_summary(t34),
        "window_length_mcs_unrate": mcs_summary(wl, WL_MCS_KEYS),
    }
    (out / "stage2_summary.json").write_text(json.dumps(summary, indent=1, default=str))
    return summary


if __name__ == "__main__":
    result = main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
    print(json.dumps({k: v for k, v in result.items() if k != "tables"}, indent=1, default=str))
