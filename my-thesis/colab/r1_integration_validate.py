"""Stage 4 of the Part 8 integration dry run: acceptance criteria and attribution.

Every criterion is evaluated independently of the stage that produced the data; a failed
criterion makes the dry run REFUSED (exit 1). A12 attributes EVERY changed scientific
cell of the dry-run release, against the base tree (published + B1 staged), to a cause:

  correction                     changed by an authorised R1 correction (corrected run
                                 differs from the legacy run; the legacy run reproduces
                                 the base)
  reestimated_chain              changed by a re-estimated chain (the legacy run, with
                                 every correction off, already differs from the base);
                                 allowed only in the exercises those chains feed
  correction+reestimated_chain   both
  correction_new_row             a row the corrections add (F2 MCS rows, F4 ZA rows)
  dependent:<builder>            rebuilt in stage 3 from changed inputs

Any changed cell, row or file without a cause is UNEXPLAINED and stops the dry run.
A2 (protected inputs) and A14 (claims) are added by the driver after stage 5.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r1_integration_common as ic  # noqa: E402

#: Exercise files a re-estimated chain feeds, and the series whose chains were re-estimated.
CHAIN_EFFECT_SCOPE = {
    "robustness/T4.1_": {"UNRATE", "FEDFUNDS"},
    "robustness/T4.2_": {"CPIAUCSL"},
    "robustness/window_length_": {"UNRATE"},
}
RECORD_FILES = ("manifests/correction_file_comparison.csv", "manifests/output_inventory.csv",
                "manifests/correction_run_manifest.json", "manifests/correction_summary.json",
                "manifests/original_output_inventory.csv")
EXPECTED_SOURCES = {"re-estimated": 17, "cache": 17, "unavailable": 26, "published": 48}


def criterion(ok: bool, detail) -> dict:
    return {"pass": bool(ok), "detail": detail}


def chain_scope(path: str, series: str) -> bool:
    for prefix, allowed in CHAIN_EFFECT_SCOPE.items():
        if path.startswith(prefix):
            return series in allowed
    return False


# -- A3 chain sources ----------------------------------------------------------------------

def check_sources(summary: dict, classification_csv: Path) -> dict:
    import r1_tierb as tb
    sources = summary["chain_sources"]
    counts = {k: len(v) for k, v in sources.items()}
    problems = []
    expected = sorted(list(tb.TIER_A_CHAINS) + list(tb.TIER_B_CHAINS))
    if sorted(sources.get("re-estimated", [])) != expected:
        problems.append("re-estimated chains are not exactly the 17 of the plan")
    if counts != EXPECTED_SOURCES:
        problems.append(f"source counts {counts} != {EXPECTED_SOURCES}")
    sensitive = set(sources.get("cache", [])) & set(ic.RULE_SENSITIVE_CHAINS)
    if sensitive:
        problems.append(f"rule-sensitive chains served from the cache: {sorted(sensitive)}")
    unaffected = {r["task_id"] for r in ic.read_rows(classification_csv)
                  if r["affected_by_correction"] == "False"}
    affected_unavailable = sorted(set(sources.get("unavailable", [])) - unaffected)
    if affected_unavailable:
        problems.append(f"unavailable chains affected by a correction: {affected_unavailable}")
    missing_b1 = [t for t in ic.B1_STAGED_TASKS if t not in sources.get("published", [])]
    if missing_b1:
        problems.append(f"B1-staged chains not re-read from the base tree: {missing_b1}")
    return {"counts": counts, "problems": problems}


def chain_table(summary: dict, certificates: dict, dependents: dict, classification_csv: Path) -> list[dict]:
    import r1_tierb as tb
    classes = {r["task_id"]: r for r in ic.read_rows(classification_csv)}
    batch_of = {t: b for b, ts in tb.BATCHES.items() for t in ts}
    rows = []
    for source, tasks in sorted(summary["chain_sources"].items()):
        for task in sorted(tasks):
            row = {"task_id": task, "source": source}
            if source == "published":
                row["provenance"] = ("base tree: B1-staged correction " + ic.B1_STAGED_RUN_ID
                                     if task in ic.B1_STAGED_TASKS else "base tree: published run")
            elif source == "cache":
                row["provenance"] = f"original fit cache {ic.ORIGINAL_CACHE_IDENTITY} (cache-hit replay)"
            elif source == "re-estimated":
                batch = batch_of.get(task)
                if batch:
                    chain = certificates[batch]["chains"][task]
                    row.update(provenance=f"Tier B {batch}, certificate {certificates[batch]['created_utc']}",
                               agreement_status=chain.get("agreement_status", ""),
                               agreement_categories=json.dumps(chain.get("agreement", {}).get("categories", {})))
                else:
                    row.update(provenance=f"Tier A archive {tb.TIER_A_ARCHIVE_SHA256[:12]}",
                               agreement_status="closed form (reproduces published records)")
                info = dependents.get("fit_records", {}).get(task, {})
                row["fit_records_replaced"] = len(info.get("replaced_origins", []))
                row["statuses"] = json.dumps(info.get("statuses", {}), sort_keys=True)
            else:
                row["provenance"] = "original values retained (no correction affects the chain)"
                row["classification"] = classes.get(task, {}).get("decision", "")
            rows.append(row)
    return rows


# -- A7 cache chains -----------------------------------------------------------------------

def check_cache_chains(tasks, jobs, identity, config, cache_fits: Path, fit_records) -> dict:
    import r1_tierb as tb
    import r1_original_cache_audit as audit
    out, problems = {}, []
    for task in sorted(tasks):
        walk = tb.walk_chain(jobs[task], cache_fits, identity, config, require_marker=False,
                             semantics="cache_hit")
        import r1_integration_dependents as dep
        dates = [d for d, _ in walk["sequence"]]
        if not walk["complete"]:
            problems.append(f"{task}: cache walk incomplete ({walk['completed']}/{walk['planned']})")
        block, provenance = audit.stage_block(fit_records, jobs[task])
        blocks = [block] if block is not None and sorted(block) == dates else [
            {str(r.refit_date)[:10]: r for r in fit_records.loc[run].itertuples()}
            for run in dep.candidate_runs(fit_records, jobs[task])
            if list(fit_records.loc[run, "refit_date"].astype(str).str[:10]) == dates]
        if not blocks:
            problems.append(f"{task}: no published records with the chain's refit dates ({provenance})")
            continue
        payloads = [(d, tb.read_payload(cache_fits / rel, require_marker=False))
                    for d, rel in walk["sequence"]]

        def differing(candidate):
            return [d for d, payload in payloads
                    if candidate.get(d) is None
                    or payload.get("status") != candidate[d].status
                    or tb._codes(payload.get("reason_codes")) != tb._codes(candidate[d].reason_codes)
                    or tb._scaled_diff(payload.get("loglik"), candidate[d].loglik) > tb.LOGLIK_TOLERANCE]
        mismatches = min((differing(b) for b in blocks), key=len)
        if mismatches:
            problems.append(f"{task}: {len(mismatches)} origins differ from the published records")
        out[task] = {"origins": walk["completed"], "mismatches": len(mismatches)}
    return {"chains": out, "problems": problems}


# -- A8 re-estimated chains ------------------------------------------------------------------

def expected_replacements(b2_by_origin: Path) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for row in ic.read_rows(b2_by_origin):
        if row["b2_agreement_category_vs_published"] not in ("reproduced",
                                                             "reproduced_regime_labels_permuted"):
            out.setdefault(row["task"], set()).add(row["refit_date"][:10])
    return out


def check_reestimated(dependents: dict, certificates: dict, b2_by_origin: Path) -> dict:
    import r1_tierb as tb
    fit = dependents["fit_records"]
    expected = expected_replacements(b2_by_origin)
    problems, rows = [], {}
    for task in sorted(list(tb.TIER_A_CHAINS) + list(tb.TIER_B_CHAINS)):
        info = fit.get(task)
        if info is None:
            problems.append(f"{task}: not replayed in stage 3")
            continue
        statuses = info["statuses"]
        replaced = set(info["replaced_origins"])
        if task in tb.TIER_A_CHAINS:
            planned, failed = tb.TIER_A_CHAINS[task]
            want = {"records": planned, "failed": failed}
            got = {"records": info["records"], "failed": statuses.get("failed", 0)}
        else:
            batch = next(b for b, ts in tb.BATCHES.items() if task in ts)
            chain = certificates[batch]["chains"][task]
            want = {k: chain[k] for k in ("adequate", "fragile", "failed")}
            got = {k: statuses.get(k, 0) for k in want}
        if want != got:
            problems.append(f"{task}: statuses {got} != certificate {want}")
        want_replaced = expected.get(task, set())
        if replaced != want_replaced:
            problems.append(f"{task}: replaced {len(replaced)} records, expected "
                            f"{len(want_replaced)} (extra {sorted(replaced - want_replaced)[:3]}, "
                            f"missing {sorted(want_replaced - replaced)[:3]})")
        rows[task] = {"statuses": statuses, "certificate": want, "replaced": len(replaced),
                      "expected_replaced": len(want_replaced)}
    return {"chains": rows, "problems": problems}


# -- A9 baseline B1 --------------------------------------------------------------------------

def check_b1(base: Path, release: Path, jobs, summary: dict) -> dict:
    import pandas as pd
    import r1_original_cache_audit as audit
    problems, info = [], {}
    base_fr = pd.read_parquet(base / "models" / "fit_records.parquet")
    rel_fr = pd.read_parquet(release / "models" / "fit_records.parquet")
    for task in ic.B1_STAGED_TASKS:
        a, _ = audit.stage_block(base_fr, jobs[task])
        b, _ = audit.stage_block(rel_fr, jobs[task])
        if a is None or b is None:
            problems.append(f"{task}: block not found")
            continue
        rows_a = base_fr.loc[sorted(r.Index for r in a.values())].reset_index(drop=True)
        rows_b = rel_fr.loc[sorted(r.Index for r in b.values())].reset_index(drop=True)
        if not rows_a.astype(str).equals(rows_b.astype(str)):
            problems.append(f"{task}: release records differ from the B1-staged records")
        statuses = rows_b["status"].value_counts().to_dict()
        if statuses != {"adequate": 440, "fragile": 258, "failed": 6}:
            problems.append(f"{task}: statuses {statuses}")
        if not (rows_b["run_id"] == ic.B1_STAGED_RUN_ID).any():
            problems.append(f"{task}: no record carries the B1 provenance")
        info[task] = {"records": len(rows_b), "statuses": statuses,
                      "b1_rows": int((rows_b["run_id"] == ic.B1_STAGED_RUN_ID).sum())}
    audit_path = "forecasts/forecast_origin_audit.csv"
    if (base / audit_path).read_bytes() != (release / audit_path).read_bytes():
        problems.append(f"{audit_path} differs from the base")
    return {"chains": info, "problems": problems}


# -- A10/A11 dependents and figures ------------------------------------------------------

def check_dependents(release: Path, dependents_report: dict) -> dict:
    import pandas as pd
    problems = []
    final = pd.read_parquet(release / "models" / "fit_records.parquet")
    g = final.groupby(["series", "model", "status"]).size()
    counts = {(r["series"], r["model"], r["status"]): int(float(r["n"]))
              for r in ic.read_rows(release / "robustness" / "T4.7_status_counts.csv")}
    if {k: int(v) for k, v in g.items()} != counts:
        problems.append("T4.7 status counts differ from a recount of the final fit records")
    if not dependents_report["wald_rows"].get("validated_against_base_t35"):
        problems.append("Wald rows were not validated against the base")
    if not dependents_report["t46_summary"].get("validated_against_base"):
        problems.append("T4.6 summary was not validated against the base")
    if not all(all(v.values()) for v in dependents_report["f48"]["reproduced_from_base"].values()):
        problems.append("F4.8 was not reproduced from the base tables")
    inventory = ic.read_rows(release / "manifests" / "output_inventory.csv")
    files = ic.tree_files(release)
    wrong = [r["path"] for r in inventory if r["path"] not in files
             or ic.sha256_file(files[r["path"]]) != r["sha256"]]
    missing = sorted(set(files) - {r["path"] for r in inventory} - {"manifests/output_inventory.csv"})
    if wrong or missing:
        problems.append(f"inventory: {len(wrong)} wrong hashes, {len(missing)} files missing")
    return {"problems": problems}


def check_figures(base: Path, release: Path, regenerated: set[str], dependents_report: dict,
                  scratch: Path, config) -> dict:
    import r1_integration_dependents as dep
    problems, re_rendered = [], set(dependents_report["f48"]["re_rendered"])
    table = release / "robustness" / "window_length_comparison.csv"
    validated = {}
    for series in sorted({r["series"] for r in ic.read_rows(table)}):
        for path in dep.render_f48(table, series, scratch / f"F4.8_{series}", config):
            same = path.read_bytes() == (release / "figures" / path.name).read_bytes()
            validated[path.name] = same
            if not same:
                problems.append(f"{path.name} is not the rendering of the integrated table")
    shutil.rmtree(scratch, ignore_errors=True)
    for relative, path in sorted(ic.tree_files(release).items()):
        if not relative.startswith("figures/") or relative.endswith(".provenance.json"):
            continue
        if path.read_bytes() == (base / relative).read_bytes():
            continue
        name = relative.split("/", 1)[1]
        if relative in regenerated or name in re_rendered:
            if not (release / (relative + ".provenance.json")).exists():
                problems.append(f"{relative}: changed without a provenance sidecar")
            continue
        problems.append(f"{relative}: changed but neither regenerated nor re-rendered")
    stale = [n for n in validated if not n.startswith("F4.8_") or False]
    return {"f48_validated_against_integrated_table": validated, "problems": problems,
            "unexpected": stale}


# -- A12 attribution -------------------------------------------------------------------

def attribute(base: Path, release: Path, work: Path, regenerated: set[str],
              dependents_report: dict, fit_positions: dict[str, set[int]]) -> dict:
    """Every changed file and cell of the release against the base, with its cause."""
    causes = {(r["path"], int(r["row"]), r["column"]): r
              for r in ic.read_rows(work / "assembly" / "reconcile_cell_causes.csv.gz")}
    new_rows = {(r["path"], int(r["row"])) for r in causes.values() if r["column"] == "*"}
    legacy_cmp = {r["path"]: r["status"] for r in ic.read_rows(work / "assembly" / "legacy" / "r1_comparison.csv")}
    dependent_files = set(dependents_report["dependent_files"])
    wald_rows = {int(r["row"]) for r in dependents_report["wald_rows"]["rows_changed"]}
    t46_cells = {(int(r["row"]), c) for r in dependents_report["t46_summary"]["rows_changed"]
                 for c in r["columns"]}
    counts_rows = {int(r["row"]) for r in dependents_report["t47_status_counts"]["rows_changed"]}
    files_out, cells_out, unexplained = [], [], []
    base_files, rel_files = ic.tree_files(base), ic.tree_files(release)
    for relative in sorted(set(base_files) | set(rel_files)):
        if relative in RECORD_FILES:
            files_out.append({"path": relative, "cause": "record"})
            continue
        if relative not in base_files or relative not in rel_files:
            unexplained.append({"path": relative, "reason": "file added or removed"})
            continue
        if ic.sha256_file(base_files[relative]) == ic.sha256_file(rel_files[relative]):
            continue
        cause = None
        if relative == "robustness/T4.7_failure_registry.csv" and relative in dependent_files:
            files_out.append({"path": relative, "cause": "dependent:T4.7 events of the chains whose "
                              "records changed (block structure verified in A10)",
                              "regenerated_by_r1": False, "regenerated_by_dependents": True})
            continue
        if relative.endswith(".csv"):
            result = ic.table_cell_changes(base_files[relative], rel_files[relative], relative)
            if not result["alignable"]:
                unexplained.append({"path": relative, "reason": "rows not alignable"})
                continue
            explained_cells = 0
            for cell in result["cells"]:
                why = cell_cause(relative, cell, causes, new_rows, regenerated, dependent_files,
                                 wald_rows, t46_cells, counts_rows, fit_positions, base, release)
                cell["cause"] = why or "UNEXPLAINED"
                cells_out.append(cell)
                if why is None:
                    unexplained.append({"path": relative, "row": cell["row"], "column": cell["column"],
                                        "reason": "changed cell without a cause"})
                else:
                    explained_cells += 1
            rows_added = result.get("rows_added", 0)
            for i in result.get("added_rows", []):
                if relative == "diagnostics/all_test_results.csv" and relative in regenerated:
                    continue                      # F4: Zivot-Andrews rows appended by the workflow
                if (relative, i) not in new_rows:
                    unexplained.append({"path": relative, "row": i, "reason": "row added without cause"})
            for removed in result.get("removed_rows", []):
                if not f2_placeholder_replaced(relative, removed, rel_files[relative], new_rows):
                    unexplained.append({"path": relative, "row": removed["row"],
                                        "reason": "row removed without cause"})
            cause = "cells" if result["cells"] or rows_added or result["columns_added"] else \
                "provenance_or_fp_only"
            if result["columns_removed"]:
                unexplained.append({"path": relative, "reason": f"columns removed {result['columns_removed']}"})
            if result["columns_added"] and relative not in regenerated:
                unexplained.append({"path": relative, "reason": f"columns added {result['columns_added']}"})
        elif relative.endswith(".parquet"):
            twin = relative[:-len(".parquet")] + ".csv"
            if relative in regenerated or relative in dependent_files:
                cause = "parquet twin of " + twin
            if twin not in rel_files:
                cause = None
        elif relative.startswith("figures/"):
            if relative.endswith(".provenance.json"):
                cause = "figure sidecar"
            elif relative in regenerated and legacy_cmp.get(relative) in ("identical", "equal_within_fp_tolerance"):
                cause = "correction (figure re-rendered by the workflow; legacy reproduces the base)"
            elif relative in dependent_files:
                cause = "dependent:F4.8 (D2)"
        elif relative.endswith(".json") and relative in regenerated:
            cause = "workflow record"
        if cause is None:
            unexplained.append({"path": relative, "reason": "changed file without a cause"})
            cause = "UNEXPLAINED"
        files_out.append({"path": relative, "cause": cause,
                          "regenerated_by_r1": relative in regenerated,
                          "regenerated_by_dependents": relative in dependent_files})
    return {"files": files_out, "cells": cells_out, "unexplained": unexplained}


def f2_placeholder_replaced(relative: str, removed: dict, release_file: Path, new_rows: set) -> bool:
    """An MCS row removed by F2: the 'unavailable' placeholder of a cell (no model, no
    inference) whose cell now holds model rows that the corrections added."""
    keys = ic.ROW_KEYS.get(relative)
    if not keys or "model" not in keys or removed.get("model", "") != "" or \
            str(removed.get("inference_available", "")) != "False":
        return False
    group = [k for k in keys if k != "model"]
    table = ic.read_table(release_file)
    match = table.index[(table[group].astype(str) == [str(removed[k]) for k in group]).all(axis=1)]
    return len(match) > 0 and all((relative, int(i)) in new_rows for i in match)


def cell_cause(relative, cell, causes, new_rows, regenerated, dependent_files, wald_rows,
               t46_cells, counts_rows, fit_positions, base, release) -> str | None:
    row, column = int(cell["row"]), cell["column"]
    if relative in regenerated and relative != "diagnostics/all_test_results.csv":
        record = causes.get((relative, row, column))
        if (relative, row) in new_rows:
            return "correction_new_row"
        if record is None:
            return None
        if "reestimated_chain" in record["cause"] and not chain_scope(relative, cell.get("key_series", "")):
            return None
        return record["cause"]
    if relative == "diagnostics/all_test_results.csv":
        return "dependent:Wald rows rebuilt from the release T3.5" if row in wald_rows else None
    if relative in ("models/fit_records.csv",):
        return "dependent:re-estimated chain record" if row in fit_positions.get("rows", set()) else None
    if relative == "robustness/T4.7_failure_registry.csv":
        return "dependent:T4.7 events of a chain whose records changed"
    if relative == "robustness/T4.7_status_counts.csv":
        return "dependent:T4.7 recount" if row in counts_rows and column == "n" else None
    if relative == "robustness/T4.6_arma_garch_summary.csv":
        return "dependent:T4.6 ARMA comparison" if (row, column) in t46_cells else None
    return None


def check_registry(base: Path, release: Path, dependents_report: dict) -> list[str]:
    """T4.7 registry: rows outside the patched chains' blocks are unchanged, in order."""
    a = ic.read_table(base / "robustness" / "T4.7_failure_registry.csv")
    b = ic.read_table(release / "robustness" / "T4.7_failure_registry.csv")
    blocks = []
    for task, info in dependents_report["t47_registry"].items():
        start, end = (int(x) for x in info["published_rows"].split("-"))
        blocks.append((start, end, info["events_after"]))
    expected_len = len(a) + sum(after - (end - start + 1) for start, end, after in blocks)
    problems = [] if len(b) == expected_len else [f"T4.7 registry has {len(b)} rows, expected {expected_len}"]
    cursor_a, cursor_b = 0, 0
    for start, end, after in sorted(blocks):
        if not a.iloc[cursor_a:start].reset_index(drop=True).equals(
                b.iloc[cursor_b:cursor_b + (start - cursor_a)].reset_index(drop=True)):
            problems.append(f"T4.7 registry rows before {start} changed")
        cursor_b += (start - cursor_a) + after
        cursor_a = end + 1
    if not a.iloc[cursor_a:].reset_index(drop=True).equals(b.iloc[cursor_b:].reset_index(drop=True)):
        problems.append("T4.7 registry rows after the patched blocks changed")
    return problems


def fit_record_rows(base: Path, release: Path, dependents_report: dict, jobs) -> dict:
    """Positions of the fit records replaced in stage 3 (as recorded by stage 3)."""
    rows = set()
    for task, info in dependents_report["fit_records"].items():
        if len(info.get("replaced_positions", [])) != len(info["replaced_origins"]):
            raise ic.IntegrationError(f"{task}: replaced positions not recorded")
        rows |= {int(x) for x in info["replaced_positions"]}
    return {"rows": rows}


# -- A13 provenance -------------------------------------------------------------------------

def check_provenance(release: Path, cells: list[dict], run_id: str) -> dict:
    problems, checked = [], 0
    rows_by_path: dict[str, set[int]] = {}
    for cell in cells:
        rows_by_path.setdefault(cell["path"], set()).add(int(cell["row"]))
    for relative, rows in sorted(rows_by_path.items()):
        table = ic.read_table(release / relative)
        if "run_id" not in table.columns:
            continue
        wrong = [r for r in rows if table.at[r, "run_id"] != run_id]
        checked += len(rows)
        if wrong:
            problems.append(f"{relative}: {len(wrong)} changed rows without the dry-run run ID")
    manifest = json.loads((release / "manifests" / "correction_run_manifest.json").read_text())
    for key, want in (("code_commit_sha", ic.SCIENTIFIC_PIN), ("config_hash", ic.CONFIG_HASH),
                      ("run_id", run_id)):
        if manifest.get(key) != want:
            problems.append(f"release manifest {key} = {manifest.get(key)!r}, expected {want!r}")
    if manifest.get("code_tree_dirty"):
        problems.append("release manifest records a dirty code tree")
    if not manifest.get("data_snapshot_hash"):
        problems.append("release manifest lacks the data snapshot hash")
    if not (manifest.get("started_utc") or manifest.get("created_utc")):
        problems.append("release manifest lacks the execution timestamp")
    return {"rows_checked": checked, "problems": problems,
            "manifest": {k: manifest.get(k) for k in ("run_id", "code_commit_sha", "config_hash",
                                                      "data_snapshot_hash", "code_tree_dirty")}}


# -- A15 status ----------------------------------------------------------------------------

def check_status(plan: dict, certificates: dict) -> dict:
    """The status follows mechanically from the certificates and gates; B2's review items
    (and every other certificate's) stay reportable after D1: candidate integration is not
    scientific approval, and an internally consistent computation is not either."""
    import r1_tierb as tb
    import r1_tierb_aggregate as agg
    recomputed = agg.aggregation_status(certificates, plan["gates"])
    review = [f"{b}: {r}" for b, c in sorted(certificates.items()) for r in c.get("review_items", [])]
    sensitivity = [f"{b}: {r}" for b, c in sorted(certificates.items())
                   for r in c.get("sensitivity_reported", [])]
    problems = []
    if recomputed["aggregation_status"] != plan["aggregation_status"]:
        problems.append("the plan's status does not follow from the certificates and gates")
    if review and plan["aggregation_status"] not in (tb.STATUS_REVIEW_REQUIRED, "AGGREGATION_REFUSED"):
        problems.append("review items exist but the status is not REVIEW_REQUIRED")
    if not set(review) <= set(plan.get("review_items", [])):
        problems.append("certificate review items are missing from the plan")
    if not set(sensitivity) <= set(plan.get("sensitivity_reported", [])):
        problems.append("reported sensitivities are missing from the plan")
    if plan.get("scientific_approval") != tb.APPROVAL_NOT_GRANTED:
        problems.append("the plan claims scientific approval")
    return criterion(not problems, {"aggregation_status": plan["aggregation_status"],
                                    "review_items": plan.get("review_items", []),
                                    "sensitivity_reported": plan.get("sensitivity_reported", []),
                                    "problems": problems,
                                    "note": "D1 authorises candidate integration only; B2's "
                                            "review items remain review items"})


# -- driver ----------------------------------------------------------------------------------

def run(p: dict, protected: dict | None = None, certificates: dict | None = None) -> dict:
    """Stage 4. Certificates are read from Drive (`discover`) unless given (rehearsals)."""
    import pandas as pd
    import r1_tierb as tb
    import r1_tierb_aggregate as agg
    from thesis.correction import guard
    work = p["work"]
    base, release, report_dir = work / "base", work / "release", work / "dryrun_report"
    plan = json.loads((report_dir / "aggregation_plan.json").read_text())
    dependents = json.loads((report_dir / "dependents_report.json").read_text())
    legacy = json.loads((work / "assembly" / "legacy" / "r1_summary.json").read_text())
    corrected = json.loads((work / "assembly" / "corrected" / "r1_summary.json").read_text())
    run_id = corrected["run_id"]
    regenerated = set(corrected["regenerated_files"])
    certificates = certificates if certificates is not None else agg.discover(p["drive"])
    with guard.estimation_forbidden(), tb.no_estimation_allowed():
        jobs, identity, config = tb.build_jobs(base, p["code"])
    crit: dict[str, dict] = {}
    estimations = {"legacy": legacy.get("estimations_performed"),
                   "corrected": corrected.get("estimations_performed"),
                   "dependents": dependents.get("estimation")}
    crit["A1"] = criterion(not legacy.get("estimations_performed")
                           and not corrected.get("estimations_performed")
                           and str(dependents.get("estimation", "")).startswith("none"), estimations)
    sources = check_sources(corrected, p["classification"])
    legacy_sources = check_sources(legacy, p["classification"])
    crit["A3"] = criterion(not sources["problems"] and legacy["chain_sources"] == corrected["chain_sources"],
                           {"corrected": sources, "legacy_equal": legacy["chain_sources"] == corrected["chain_sources"],
                            "legacy_problems": legacy_sources["problems"]})
    pending = [f for f in ic.tree_files(release) if f.endswith(".csv") and any(
        r.get("correction_status") == "original_retained_pending_estimation"
        for r in ic.read_rows(release / f))]
    crit["A4"] = criterion(not pending, {"files_with_pending_rows": pending})
    legacy_cmp = ic.read_rows(work / "assembly" / "legacy" / "r1_comparison.csv")
    not_reproduced = [r["path"] for r in legacy_cmp
                      if r["status"] not in ("identical", "equal_within_fp_tolerance")
                      and not r["path"].startswith(agg.REESTIMATION_DEPENDENT)]
    crit["A5"] = criterion(not not_reproduced and not any("legacy reproduction" in x for x in plan["gates"]["problems"]),
                           {"files_not_reproduced": not_reproduced,
                            "chain_dependent_differences": plan["gates"].get("legacy_differences_from_reestimated_chains")})
    t42 = [x for x in plan["gates"]["problems"] if "Tier A release" in x]
    crit["A6"] = criterion(not t42, t42 or plan["gates"].get("t42_vs_tier_a_release",
                                                             "T4.2 identical to the Tier A release"))
    base_fr = pd.read_parquet(base / "models" / "fit_records.parquet")
    cache = check_cache_chains(corrected["chain_sources"].get("cache", []), jobs, identity, config,
                               p["cache_root"] / "fits", base_fr)
    crit["A7"] = criterion(not cache["problems"], cache)
    reest = check_reestimated(dependents, certificates, p["b2_by_origin"])
    crit["A8"] = criterion(not reest["problems"], reest)
    b1 = check_b1(base, release, jobs, corrected)
    crit["A9"] = criterion(not b1["problems"], b1)
    dep = check_dependents(release, dependents)
    registry_problems = check_registry(base, release, dependents)
    crit["A10"] = criterion(not dep["problems"] and not registry_problems,
                            {"problems": dep["problems"] + registry_problems})
    figs = check_figures(base, release, regenerated, dependents, ic.inside(work, work / "scratch_validate"), config)
    crit["A11"] = criterion(not figs["problems"], figs)
    fit_rows = fit_record_rows(base, release, dependents, jobs)
    attribution = attribute(base, release, work, regenerated, dependents, fit_rows)
    ic.write_rows(report_dir / "cells_vs_b1_staged.csv.gz", attribution["cells"])
    ic.write_rows(report_dir / "files_vs_b1_staged.csv", attribution["files"])
    decision = [c for c in attribution["cells"] if c["decision_like"] in (True, "True")]
    ic.write_rows(report_dir / "decision_changes.csv", decision)
    ic.write_rows(report_dir / "unexplained_differences.csv", attribution["unexplained"])
    files_pub, cells_pub = ic.tree_changes(p["published"], release)
    ic.write_rows(report_dir / "files_vs_published.csv", files_pub)
    ic.write_rows(report_dir / "cells_vs_published.csv.gz", cells_pub)
    files_ta, cells_ta = ic.tree_changes(work / "references" / "tier_a_release", release)
    ic.write_rows(report_dir / "files_vs_tier_a.csv", files_ta)
    ic.write_rows(report_dir / "cells_vs_tier_a.csv.gz", cells_ta)
    crit["A12"] = criterion(not attribution["unexplained"],
                            {"files_changed_vs_base": len(attribution["files"]),
                             "cells_changed_vs_base": len(attribution["cells"]),
                             "decision_like_changes": len(decision),
                             "unexplained": attribution["unexplained"][:50],
                             "unexplained_total": len(attribution["unexplained"]),
                             "files_changed_vs_published": len(files_pub),
                             "files_changed_vs_tier_a": len(files_ta)})
    prov = check_provenance(release, attribution["cells"], run_id)
    crit["A13"] = criterion(not prov["problems"], prov)
    crit["A15"] = check_status(plan, certificates)
    ic.write_rows(report_dir / "chain_sources.csv",
                  chain_table(corrected, certificates, dependents, p["classification"]))
    ic.write_json(report_dir / "acceptance_stage4.json",
                  {"run_id": run_id, "aggregation_status": plan["aggregation_status"],
                   "criteria": crit})
    return {"run_id": run_id, "criteria": {k: v["pass"] for k, v in crit.items()},
            "unexplained": len(attribution["unexplained"])}
