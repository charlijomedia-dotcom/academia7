#!/usr/bin/env python3
"""Independent validation of the staged B1 correction (read-only; no estimation).

Checks the staged tree against the published tree from first principles, not from the
builder's own report:

  files        every file byte-identical except an explicit, expected set (dependency map);
  cells        every changed non-provenance cell, keyed; every changed decision-like cell;
  consistency  forecasts <-> fit records <-> T3.3 counts <-> origin audit <-> T4.7 registry
               and status counts <-> Wald rows <-> T3.5; parquet twins <-> CSVs; the
               inventory hashes <-> the files;
  platform     the staged changed values against the Colab candidate regeneration (another
               machine), within 1e-9 relative.

usage: r1_b1_validate_staged.py --published OUT --staged DIR --colab-candidate DIR
       --code-dir C --out DIR
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

PROV = {"run_id", "data_snapshot_hash", "code_commit_sha", "config_hash", "created_utc"}
SERIES, MODEL = "UNRATE", "MSAR"
EXPECTED_CHANGED = {
    # workflow-regenerated (29)
    "data_audit/T4.9_locf_sample_comparison.csv", "data_audit/locf_forecast_exposure.csv",
    "data_audit/locf_forecast_exposure.parquet",
    "figures/F3.4_UNRATE.pdf", "figures/F3.4_UNRATE.png", "figures/F3.5_UNRATE.pdf",
    "figures/F3.5_UNRATE.png", "figures/F3.6_UNRATE.pdf", "figures/F3.6_UNRATE.png",
    "forecast_tests/T3.3A_hlz_pairwise.csv", "forecast_tests/T3.3B_dm_hln_pairwise.csv",
    "forecast_tests/T3.3_main_forecast_table.csv", "forecast_tests/T3.4_model_confidence_set.csv",
    "forecast_tests/T3.5_state_loss_regression.csv", "forecast_tests/T3.5_state_performance.csv",
    "forecast_tests/T3.6_peak_trough_detail.csv", "forecasts/forecast_horizon_coverage.csv",
    "forecasts/forecasts_UNRATE.csv", "forecasts/forecasts_UNRATE.parquet",
    "robustness/T4.1_transformation_robustness.csv", "robustness/T4.4_horizon_predictive_tests.csv",
    "robustness/T4.4_horizon_robustness.csv", "robustness/T4.5_var_comparison.csv",
    "robustness/T4.5_var_predictive_tests.csv", "robustness/T4.TP1_turning_window_sensitivity.csv",
    "robustness/window_length_comparison.csv", "robustness/window_length_mcs.csv",
    "robustness/window_length_origin_audit.csv", "robustness/window_length_predictive_tests.csv",
    # dependent outputs built by the staging code
    "models/fit_records.csv", "models/fit_records.parquet", "forecasts/forecast_origin_audit.csv",
    "robustness/T4.7_failure_registry.csv", "robustness/T4.7_status_counts.csv",
    "diagnostics/all_test_results.csv", "figures/F4.8_UNRATE.pdf", "figures/F4.8_UNRATE.png",
    "manifests/output_inventory.csv",
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def check_counter_provenance(path: Path, published: Path, staged: Path) -> dict:
    """Both histories of the origin-audit counters match the published and staged rows."""
    import pandas as pd
    record = pd.read_csv(path, dtype=str, keep_default_na=False)
    result: dict[str, object] = {"rows": len(record)}
    ok = len(record) == 4
    for history, tree in (("historical_original_execution", published),
                          ("corrected_replay", staged)):
        audit = pd.read_csv(tree / "forecasts" / "forecast_origin_audit.csv", dtype=str,
                            keep_default_na=False)
        row = audit[(audit["series"] == SERIES) & (audit["model"] == MODEL)].iloc[0]
        part = record[record["history"] == history]
        for _, r in part.iterrows():
            same = (int(float(row[r["counter"]])) == int(r["value"])
                    and row["run_id"] == r["run_id"] and row["created_utc"] == r["created_utc"]
                    and row["code_commit_sha"] == r["code_commit_sha"])
            result[f"{history}:{r['counter']}"] = {"value": int(r["value"]), "matches_table": same}
            ok = ok and same
        ok = ok and len(part) == 2
    result["ok"] = bool(ok)
    return result


def main(argv=None) -> dict:
    ap = argparse.ArgumentParser()
    ap.add_argument("--published", type=Path, required=True)
    ap.add_argument("--staged", type=Path, required=True)
    ap.add_argument("--colab-candidate", type=Path, required=True)
    ap.add_argument("--code-dir", type=Path, required=True)
    ap.add_argument("--analysis", type=Path, required=True, help="b3_stage2_analysis.py")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--counter-provenance", type=Path,
                    help="the builder's forecast_origin_audit_counter_provenance.csv")
    args = ap.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import r1_render_guard as render_guard
    render_guard.pin_default_rc()
    import numpy as np
    import pandas as pd
    spec = importlib.util.spec_from_file_location("analysis", args.analysis)
    an = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(an)
    pub, stg = args.published, args.staged
    args.out.mkdir(parents=True, exist_ok=True)
    checks: dict[str, object] = {}
    try:
        checks["rendering"] = render_guard.check_default_rendering(
            render_guard.expected_version_from(args.published))
    except render_guard.RenderGuardError as error:
        checks["rendering"] = {"ok": False, "error": str(error)}

    # -- files -------------------------------------------------------------------------
    pub_files = {p.relative_to(pub).as_posix() for p in pub.rglob("*") if p.is_file()}
    stg_files = {p.relative_to(stg).as_posix() for p in stg.rglob("*") if p.is_file()}
    changed = sorted(f for f in pub_files & stg_files if sha(pub / f) != sha(stg / f))
    sidecars = {f for f in changed if f.endswith(".provenance.json")}
    content_changed = sorted(set(changed) - sidecars)
    checks["same_file_set"] = pub_files == stg_files
    checks["files_published"] = len(pub_files)
    checks["files_byte_identical"] = len(pub_files) - len(changed)
    checks["files_changed"] = len(content_changed)
    checks["figure_sidecars_changed"] = sorted(sidecars)
    checks["unexpected_changes"] = sorted(set(content_changed) - EXPECTED_CHANGED)
    checks["expected_but_unchanged"] = sorted(EXPECTED_CHANGED - set(content_changed))
    checks["sidecars_only_for_changed_figures"] = all(
        s[: -len(".provenance.json")] in content_changed for s in sidecars)

    # -- cells ---------------------------------------------------------------------------
    cells, flips, per_file = [], [], {}
    for f in content_changed:
        if not f.endswith(".csv"):
            continue
        a, b = an.read(pub / f), an.read(stg / f)
        if a.shape != b.shape:
            per_file[f] = {"rows_published": len(a), "rows_staged": len(b), "shape_changed": True}
            continue
        info, c, fl = an.compare_table(a, b, f)
        per_file[f] = {k: v for k, v in info.items() if k != "keys"}
        cells += c
        flips += fl
    pd.DataFrame(cells).to_csv(args.out / "staged_vs_published_cells.csv.gz", index=False,
                               compression={"method": "gzip", "mtime": 0})
    pd.DataFrame(flips).to_csv(args.out / "staged_vs_published_decision_cells.csv", index=False)
    checks["changed_cells_non_provenance"] = len(cells)
    checks["decision_like_cells_changed"] = len(flips)
    checks["decision_like_changes_by_column"] = pd.Series([x["column"] for x in flips]).value_counts().to_dict() if flips else {}
    checks["per_file"] = per_file

    # -- consistency --------------------------------------------------------------------
    fr = an.read(stg / "models/fit_records.csv")
    frp = pd.read_parquet(stg / "models/fit_records.parquet")
    cons = {}
    cons["fit_records_csv_equals_parquet_status_loglik"] = bool(
        (fr["status"].to_numpy() == frp["status"].to_numpy()).all()
        and np.allclose(fr["loglik"].astype(float), frp["loglik"].astype(float), equal_nan=True, rtol=0, atol=0))
    block = fr.iloc[5086:5790]
    twin = fr.iloc[40337:41041]
    cons["blocks_are_unrate_msar"] = bool((block.series == SERIES).all() and (block.model == MODEL).all()
                                         and (twin.series == SERIES).all() and (twin.model == MODEL).all())
    cons["forecasting_and_t48_blocks_identical_records"] = bool(
        block.drop(columns=list(PROV)).reset_index(drop=True).equals(twin.drop(columns=list(PROV)).reset_index(drop=True)))
    status = block.status.value_counts().to_dict()
    cons["chain_statuses"] = status
    fc = an.read(stg / "forecasts/forecasts_UNRATE.csv")
    m = fc[fc.model == MODEL]
    by_origin = dict(zip(block.refit_date.str[:10], block.status))
    cons["forecast_status_equals_fit_record_status"] = bool(
        all(by_origin[str(o)[:10]] == s for o, s in zip(m.origin_date, m.status)))
    fcp = pd.read_parquet(stg / "forecasts/forecasts_UNRATE.parquet")
    mp = fcp[fcp.model == MODEL].reset_index(drop=True)
    cons["forecasts_csv_equals_parquet"] = bool(
        np.allclose(m.forecast.to_numpy(float), mp.forecast.to_numpy(float), equal_nan=True, rtol=0, atol=0)
        and (m.status.to_numpy() == mp.status.to_numpy()).all())
    t33 = an.read(stg / "forecast_tests/T3.3_main_forecast_table.csv")
    row = t33[(t33.series == SERIES) & (t33.model == MODEL)]
    cons["t33_counts_equal_fit_records"] = bool(
        (row.n_adequate.astype(int) == status.get("adequate", 0)).all()
        and (row.n_fragile.astype(int) == status.get("fragile", 0)).all()
        and (row.n_failed.astype(int) == status.get("failed", 0)).all()) if "n_adequate" in row else "columns absent"
    audit = an.read(stg / "forecasts/forecast_origin_audit.csv")
    ar = audit[(audit.series == SERIES) & (audit.model == MODEL)].iloc[0]
    cons["origin_audit_equals_fit_records"] = bool(
        int(ar.valid_origins) == len(block) - status.get("failed", 0)
        and int(ar.failed_origins) == status.get("failed", 0)
        and int(ar.valid_origins) + int(ar.failed_origins) == int(ar.attempted_origins))
    counts = an.read(stg / "robustness/T4.7_status_counts.csv")
    recount = fr.groupby(["series", "model", "status"]).size()
    cons["t47_status_counts_equal_fit_records"] = bool(all(
        int(r.n) == int(recount.get((r.series, r.model, r.status), 0)) for r in counts.itertuples()))
    reg = an.read(stg / "robustness/T4.7_failure_registry.csv")
    failed_origins = set(block[block.status == "failed"].refit_date.str[:10])
    regu = reg[(reg.series == SERIES) & (reg.model == MODEL) & (reg.category == "failed")]
    cons["registry_failed_origins_in_chain_blocks"] = sorted(
        set(regu.refit_date.str[:10]) & failed_origins) == sorted(failed_origins)
    tests = an.read(stg / "diagnostics/all_test_results.csv")
    t35 = an.read(stg / "forecast_tests/T3.5_state_loss_regression.csv")
    w = tests[tests.name.str.contains("Wald") & (tests.series == SERIES) & (tests.model == f"{MODEL} vs AR")]
    s = t35[(t35.series == SERIES) & (t35.model == f"{MODEL} vs AR")]
    expect = [v for r in s.itertuples() for v in (r.joint_wald_statistic, r.slopes_wald_statistic)]
    cons["wald_rows_equal_t35"] = bool(len(w) == 8 and all(float(a) == float(b) for a, b in zip(w.statistic, expect)))
    inv = an.read(stg / "manifests/output_inventory.csv")
    bad = [r.path for r in inv.itertuples() if r.path != "manifests/output_inventory.csv"
           and (stg / r.path).exists() and sha(stg / r.path) != r.sha256]
    pub_inv = an.read(pub / "manifests/output_inventory.csv")
    pub_bad = [r.path for r in pub_inv.itertuples() if r.path != "manifests/output_inventory.csv"
               and (pub / r.path).exists() and sha(pub / r.path) != r.sha256]
    cons["inventory_hashes_match_staged_files"] = not bad
    cons["inventory_mismatches_staged"] = bad
    cons["inventory_mismatches_in_published_tree_for_reference"] = pub_bad
    checks["consistency"] = cons

    # -- platform: staged changed values vs the Colab candidate regeneration -------------
    worst, compared = 0.0, 0
    for c in cells:
        colab = args.colab_candidate / c["table"]
        if not colab.exists() or c["difference"] == "":
            continue
        frame = an.read(colab)
        try:
            v = float(frame.at[c["row"], c["column"]])
        except (KeyError, ValueError, TypeError):
            continue
        y = float(c["candidate"])
        if np.isfinite(v) and np.isfinite(y):
            worst = max(worst, abs(v - y) / max(1.0, abs(v)))
            compared += 1
    checks["colab_candidate_agreement"] = {"numeric_cells_compared": compared,
                                           "max_relative_difference": worst,
                                           "within_1e-9": worst <= 1e-9}
    if args.counter_provenance is not None:
        checks["counter_provenance"] = check_counter_provenance(args.counter_provenance, pub, stg)
    ok = (checks["rendering"].get("ok") is True
          and checks.get("counter_provenance", {}).get("ok", True) is True
          and checks["same_file_set"] and not checks["unexpected_changes"]
          and checks["sidecars_only_for_changed_figures"]
          and all(v is True for k, v in cons.items() if isinstance(v, bool))
          and checks["colab_candidate_agreement"]["within_1e-9"])
    checks["all_checks_passed"] = bool(ok)
    (args.out / "validation.json").write_text(json.dumps(checks, indent=1, default=str))
    return checks


if __name__ == "__main__":
    result = main()
    print(json.dumps({k: v for k, v in result.items() if k != "per_file"}, indent=1, default=str))
