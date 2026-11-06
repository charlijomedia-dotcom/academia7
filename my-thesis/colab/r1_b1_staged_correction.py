#!/usr/bin/env python3
"""R1 Option B1 (STAGED): correct the baseline forecasting:UNRATE|MSAR chain.

The established implementation error: in the published run, three fits after a failed fit
(1982-10/11/12) were made without the approved D6 warm start; the error propagated through
the warm-start path to 1983-06. The correction replaces the chain by the ORIGINAL-cache
payloads under the approved LIVE warm-start rule (`r1_tierb.live_replay_class` over a
read-only view of the original cache, through the pinned `rolling.run_chain`). NO MODEL IS
ESTIMATED: the pinned estimators are refused and the fit calls are counted (must be 0).

Nothing is written outside --out. The published tree (--original) is only read; the staged
tree is a copy of it in which exactly the affected values are replaced:

1. Workflow-regenerated outputs. The pinned R1 workflow (legacy mode, original cache) was
   run on the published tree (REFERENCE) and on a copy carrying only the corrected chain
   (CANDIDATE) by `r1_original_cache_audit.py --stage impact`. A table cell changes in the
   staged tree only where CANDIDATE differs from REFERENCE (the same rule as the R1
   `reconcile`); every other cell keeps the published text byte for byte. Rows with a
   changed cell carry this correction's provenance. Parquet twins are patched the same way.
   Figures whose reference and candidate renderings differ take the candidate rendering.
2. Dependent outputs the workflow does not regenerate, built with the pinned builders:
   fit records (both blocks of this chain: the forecasting stage and its T4.8 240-month
   twin, which uses the same cache keys), the forecast origin audit row, the T4.7 failure
   registry blocks and status counts, the 8 state-dependence Wald rows of
   all_test_results, figure F4.8_UNRATE, and the output inventory. Every builder is first
   validated by reproducing the PUBLISHED values from the published inputs.

usage: r1_b1_staged_correction.py --cache-fits F --code-dir C --original OUT
       --impact DIR (the audit's impact folder) --out DIR
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r1_tierb as tb  # noqa: E402

TASKS = ("forecasting:UNRATE|MSAR", "T4.8:UNRATE|240:MSAR")
SERIES, MODEL = "UNRATE", "MSAR"
PROV = ("run_id", "data_snapshot_hash", "code_commit_sha", "config_hash", "created_utc")
KEYS = ("series", "model", "horizon", "loss", "model_a", "model_b", "window_length", "state",
        "window", "turning_window_width", "confidence_level", "exercise", "role", "frequency")


class StagingError(RuntimeError):
    pass


def sha(path: Path) -> str:
    return tb.sha256_file(path)


def same_value(a: str, b: str) -> bool:
    if a == b:
        return True
    try:
        return float(a) == float(b)
    except ValueError:
        return False


def read_text_table(path: Path):
    import pandas as pd
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def write_text_table(frame, path: Path) -> None:
    frame.to_csv(path, index=False)


def text_rows(frame) -> "pd.DataFrame":
    """Rows formatted exactly as the pipeline's CSV writer prints them."""
    import pandas as pd
    buffer = io.StringIO()
    frame.to_csv(buffer, index=False)
    buffer.seek(0)
    return pd.read_csv(buffer, dtype=str, keep_default_na=False)


def match_number_format(new, published) -> "pd.DataFrame":
    """Whole numbers print the way the published column prints them ("236.0", not "236"),
    as the R1 workflow does for new rows (`_match_integer_format`)."""
    import re
    out = new.copy()
    for column in out.columns:
        if column not in published.columns or column in PROV:
            continue
        filled = published[column][published[column] != ""]
        if filled.empty or not filled.str.fullmatch(r"-?\d+\.0").all():
            continue
        out[column] = [v + ".0" if re.fullmatch(r"-?\d+", v) else v for v in out[column]]
    return out


def assert_roundtrip(path: Path) -> None:
    """The text reader/writer pair reproduces the published file byte for byte."""
    buffer = io.StringIO()
    read_text_table(path).to_csv(buffer, index=False)
    if buffer.getvalue().encode() != path.read_bytes():
        raise StagingError(f"{path}: text round trip is not byte-identical; refusing to patch")


class Stamp:
    def __init__(self, run_id: str, data_hash: str, config_hash: str, code: str):
        self.values = {"run_id": run_id, "data_snapshot_hash": data_hash,
                       "code_commit_sha": code, "config_hash": config_hash,
                       "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    def apply(self, frame, rows=None):
        for column, value in self.values.items():
            if rows is None:                     # a newly built table: add the columns
                frame[column] = value
            elif column in frame.columns:
                frame.loc[rows, column] = value
        return frame


# -- 1. workflow-regenerated outputs ---------------------------------------------------

def patch_csv(original: Path, reference: Path, candidate: Path, target: Path, stamp: Stamp,
              relative: str) -> list[dict]:
    o, r, c = read_text_table(original), read_text_table(reference), read_text_table(candidate)
    if not (len(o) == len(r) == len(c)):
        raise StagingError(f"{relative}: row counts differ {len(o)}/{len(r)}/{len(c)}")
    for k in KEYS:
        if k in o.columns:
            for x, y, z in zip(o[k], r.get(k, o[k]), c.get(k, o[k])):
                if not (same_value(x, y) and same_value(y, z)):
                    raise StagingError(f"{relative}: key column {k} not aligned")
    assert_roundtrip(original)
    changes, rows = [], set()
    for column in o.columns:
        if column in PROV:
            continue
        if column not in r.columns or column not in c.columns:
            raise StagingError(f"{relative}: column {column} missing from a regeneration")
        rv, cv = r[column].to_numpy(), c[column].to_numpy()
        for i in (rv != cv).nonzero()[0]:
            if same_value(rv[i], cv[i]):
                continue
            changes.append({"path": relative, "row": int(i), "column": column,
                            **{f"key_{k}": o.at[i, k] for k in KEYS if k in o.columns},
                            "published": o.at[i, column], "reference": rv[i],
                            "corrected": cv[i]})
            o.at[i, column] = cv[i]
            rows.add(int(i))
    if rows:
        stamp.apply(o, sorted(rows))
    write_text_table(o, target)
    return changes


def patch_parquet(original: Path, reference: Path, candidate: Path, target: Path,
                  stamp: Stamp, relative: str) -> int:
    import pandas as pd
    o, r, c = (pd.read_parquet(p) for p in (original, reference, candidate))
    if not (len(o) == len(r) == len(c)):
        raise StagingError(f"{relative}: row counts differ")
    rows = set()
    for column in o.columns:
        if column in PROV:
            continue
        a, b = r[column], c[column]
        equal = (a == b) | (a.isna() & b.isna())
        if a.dtype.kind == "f" and b.dtype.kind == "f":
            equal |= (a - b).abs() == 0
        idx = (~equal.fillna(False)).to_numpy().nonzero()[0]
        if len(idx):
            o.loc[idx, column] = c.loc[idx, column].to_numpy()
            rows.update(int(i) for i in idx)
    if rows:
        stamp.apply(o, sorted(rows))
    o.to_parquet(target, index=False)
    return len(rows)


# -- 2. the corrected chain (no estimation) --------------------------------------------

def replay(job, cache_fits: Path, identity, config):
    from thesis.correction import guard
    from thesis.forecasting import rolling
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import r1_original_cache_audit as audit

    class LiveReadOnly(tb.live_replay_class(audit.ReadOnlyView)):
        pass
    cache = LiveReadOnly(cache_fits)
    calls = {"n": 0}
    real = rolling.fit_and_forecast

    def counting(*a, **k):
        calls["n"] += 1
        return real(*a, **k)
    rolling.fit_and_forecast = counting
    try:
        with guard.estimation_forbidden(), tb.no_estimation_allowed(), guard.allowed():
            chain = rolling.run_chain(job.series_name, job.y, job.spec, job.horizons,
                                      job.window_length, config, frequency=job.frequency,
                                      transformation=job.transformation, identity=identity,
                                      cache=cache, max_origins=job.max_origins,
                                      task_id=job.task_id)
    finally:
        rolling.fit_and_forecast = real
    if calls["n"] or chain.from_cache != chain.attempted:
        raise StagingError(f"{job.task_id}: replay estimated {calls['n']} times")
    return chain


def failure_signature(rows) -> list[tuple]:
    """(refit_date, category, reason_code) per event, by the pinned rolling.run_chain rule."""
    out = []
    for r in rows:
        codes = [c for c in str(r.reason_codes or "").split(";") if c]
        if r.status == "failed":
            for code in codes or ["NONCONVERGENCE"]:
                out.append((str(r.refit_date)[:10], "failed", code))
        else:
            for code in codes:
                out.append((str(r.refit_date)[:10], "fragile", code))
    return out


def find_blocks(registry, signature) -> list[int]:
    keys = list(zip(registry["refit_date"].str[:10], registry["category"], registry["reason_code"]))
    n, first = len(signature), signature[0]
    return [i for i in range(len(keys) - n + 1)
            if keys[i] == first and keys[i:i + n] == signature]


def main(argv=None) -> dict:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache-fits", type=Path, required=True)
    ap.add_argument("--code-dir", type=Path, required=True)
    ap.add_argument("--original", type=Path, required=True)
    ap.add_argument("--impact", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    tb.use_scientific_code(args.code_dir)
    import numpy as np
    import pandas as pd
    from thesis.correction import guard
    from thesis.correction.workflow import WORKFLOW_FILES
    from thesis.reporting import figures, tables
    from thesis.core.schemas import TestResult
    from thesis.evaluation.state_loss_regression import SIGNIFICANCE
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import r1_original_cache_audit as audit

    original, impact = args.original.resolve(), args.impact.resolve()
    ref_tree, cand_tree = impact / "reference", impact / "candidate"
    staged = args.out / "staged_output"
    if args.out.exists():
        raise StagingError(f"{args.out} exists; use a new folder")
    args.out.mkdir(parents=True)
    published_hashes = {p.relative_to(original).as_posix(): sha(p)
                        for p in sorted(original.rglob("*")) if p.is_file()}
    shutil.copytree(original, staged)
    report: dict = {"estimation": "none (estimators refused; fit calls counted)",
                    "scientific_commit": tb.SCIENTIFIC_PIN, "started_utc": tb.utc_stamp(),
                    "tasks": list(TASKS)}
    impact_info = json.loads((impact / "impact.json").read_text())
    if impact_info.get("task") != TASKS[0] or not impact_info.get("performed"):
        raise StagingError("the impact folder is not a performed impact run of the baseline chain")
    report["reference_reproduces_published"] = impact_info["reference_reproduces_published"]

    with guard.estimation_forbidden(), tb.no_estimation_allowed():
        jobs, identity, config = tb.build_jobs(original, args.code_dir)
    chains = {task: replay(jobs[task], args.cache_fits, identity, config) for task in TASKS}
    fc = chains[TASKS[0]]
    cand_forecasts = pd.read_parquet(impact.parent / "candidate" / "candidate_forecasts.parquet")
    if not fc.forecasts.reset_index(drop=True).equals(cand_forecasts.reset_index(drop=True)):
        raise StagingError("the replayed chain differs from the impact run's candidate")
    a_rows = tables.fit_records_table(chains[TASKS[0]].fit_records)
    b_rows = tables.fit_records_table(chains[TASKS[1]].fit_records)
    if not a_rows.equals(b_rows):
        raise StagingError("the forecasting and T4.8-240 replays do not give identical records")
    report["chain"] = {"origins": fc.attempted, "from_cache": fc.from_cache, "estimations": 0,
                       "valid": fc.valid, "failed": fc.failed,
                       "statuses": pd.Series([r.status.value for r in fc.fit_records]).value_counts().to_dict(),
                       "t48_240_records_identical": True}

    sample = read_text_table(cand_tree / "forecast_tests" / "T3.3_main_forecast_table.csv").iloc[0]
    run_id = f"b1-staged-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"
    stamp = Stamp(run_id, sample["data_snapshot_hash"], sample["config_hash"], tb.SCIENTIFIC_PIN)
    report["provenance"] = {**stamp.values, "note": "rows/files changed by this correction carry "
                            "this provenance; every other row keeps the published provenance"}

    # -- 1. workflow-regenerated files -----------------------------------------------
    summary = json.loads((ref_tree / "r1_summary.json").read_text())
    files = sorted(set(summary["regenerated_files"]) - WORKFLOW_FILES)
    cell_changes, file_rows, parquet_rows = [], [], {}
    figure_checks = []
    for relative in files:
        r, c, o = ref_tree / relative, cand_tree / relative, original / relative
        if r.read_bytes() == c.read_bytes():
            continue
        if relative.endswith(".csv"):
            cell_changes += patch_csv(o, r, c, staged / relative, stamp, relative)
        elif relative.endswith(".parquet"):
            parquet_rows[relative] = patch_parquet(o, r, c, staged / relative, stamp, relative)
        elif relative.endswith((".png", ".pdf")):
            shutil.copy2(c, staged / relative)
            side = json.loads((original / (relative + ".provenance.json")).read_text())
            side.update(stamp.values)
            side["b1_correction"] = "re-rendered by the pinned code from the corrected chain"
            (staged / (relative + ".provenance.json")).write_text(json.dumps(side, indent=2, sort_keys=True))
            figure_checks.append({"path": relative,
                                  "reference_rendering_equals_published": r.read_bytes() == o.read_bytes()})
        else:
            raise StagingError(f"unexpected changed file type: {relative}")

    # -- 2a. fit records (both blocks) -------------------------------------------------
    fr_csv, fr_pq = original / "models" / "fit_records.csv", original / "models" / "fit_records.parquet"
    published_fr = pd.read_parquet(fr_pq)
    new_rows = stamp.apply(a_rows.copy())
    fr_text = read_text_table(fr_csv)
    assert_roundtrip(fr_csv)
    new_text = match_number_format(text_rows(new_rows), fr_text)
    fr_typed = published_fr.copy()
    fit_report = {}
    compare_cols = [c for c in a_rows.columns if c not in PROV]
    for task in TASKS:
        block, provenance = audit.stage_block(published_fr, jobs[task])
        dates = sorted(block)
        if len(dates) != len(a_rows):
            raise StagingError(f"{task}: {len(dates)} published records, {len(a_rows)} corrected")
        replaced, unchanged_mismatch = [], []
        for i, d in enumerate(dates):
            pos = block[d].Index
            if str(a_rows.at[i, "refit_date"])[:10] != d:
                raise StagingError(f"{task}: origin order differs at {d}")
            new_t = new_text.iloc[i]
            old_t = fr_text.iloc[pos]
            same = all(same_value(str(old_t[c]), str(new_t[c])) for c in compare_cols)
            if same:
                continue
            replaced.append(d)
            fr_text.iloc[pos] = new_t[fr_text.columns].to_numpy()
            for j, column in enumerate(fr_typed.columns):
                fr_typed.iat[pos, j] = new_rows.at[i, column]
        fit_report[task] = {"published_block": provenance, "records": len(dates),
                            "records_replaced": len(replaced), "replaced_origins": replaced}
    write_text_table(fr_text, staged / "models" / "fit_records.csv")
    if list(fr_typed.dtypes) != list(published_fr.dtypes):
        raise StagingError("fit_records.parquet: column dtypes changed while patching")
    fr_typed.to_parquet(staged / "models" / "fit_records.parquet", index=False)
    report["fit_records"] = fit_report

    # -- 2b. forecast origin audit -------------------------------------------------------
    path = "forecasts/forecast_origin_audit.csv"
    audit_tab = read_text_table(original / path)
    mask = ((audit_tab["series"] == SERIES) & (audit_tab["model"] == MODEL)).to_numpy()
    if mask.sum() != 1:
        raise StagingError(f"{path}: {mask.sum()} rows for the chain")
    i = int(mask.nonzero()[0][0])
    before = audit_tab.iloc[i].to_dict()
    for column, value in fc.counts().items():
        if column in audit_tab.columns and not same_value(audit_tab.at[i, column], str(value)):
            cell_changes.append({"path": path, "row": i, "column": column, "key_series": SERIES,
                                 "key_model": MODEL, "published": audit_tab.at[i, column],
                                 "reference": audit_tab.at[i, column], "corrected": str(value)})
            audit_tab.at[i, column] = str(value)
    stamp.apply(audit_tab, [i])
    write_text_table(audit_tab, staged / path)
    report["forecast_origin_audit"] = {"before": {k: before[k] for k in fc.counts() if k in before},
                                       "after": fc.counts()}

    # -- 2c. T4.7 failure registry -------------------------------------------------------
    path = "robustness/T4.7_failure_registry.csv"
    registry = read_text_table(original / path)
    assert_roundtrip(original / path)
    new_events = match_number_format(text_rows(stamp.apply(tables.failure_registry_table(fc.failures))), registry)
    pieces, cursor, reg_report = [], 0, {}
    starts = []
    used: set[int] = set()
    for task in TASKS:
        block, _ = audit.stage_block(published_fr, jobs[task])
        signature = failure_signature([block[d] for d in sorted(block)])
        found = [s for s in find_blocks(registry, signature) if s not in used]
        if not found:
            raise StagingError(f"{task}: its failure events were not found in {path}")
        start = found[0]
        used.add(start)
        starts.append((start, len(signature), task, len(found)))
    ev_cols = [c for c in new_events.columns if c not in PROV]
    for start, n, task, n_found in sorted(starts):
        old = registry.iloc[start:start + n]
        old_keyed = {tuple(old.iloc[j][ev_cols]): old.iloc[j] for j in range(len(old))}
        block_rows = [old_keyed.get(tuple(new_events.iloc[j][ev_cols]), new_events.iloc[j])
                      for j in range(len(new_events))]
        kept = sum(1 for j in range(len(new_events)) if tuple(new_events.iloc[j][ev_cols]) in old_keyed)
        pieces.append(registry.iloc[cursor:start])
        pieces.append(pd.DataFrame(block_rows)[registry.columns])
        cursor = start + n
        reg_report[task] = {"published_rows": f"{start}-{start + n - 1}", "published_events": n,
                            "corrected_events": len(new_events), "events_kept_verbatim": kept,
                            "events_removed": n - kept, "events_added": len(new_events) - kept,
                            "candidate_blocks_with_same_signature": n_found}
    pieces.append(registry.iloc[cursor:])
    new_registry = pd.concat(pieces, ignore_index=True)
    write_text_table(new_registry, staged / path)
    report["t47_failure_registry"] = reg_report

    # -- 2d. T4.7 status counts (validated by reproducing the published table) ----------
    path = "robustness/T4.7_status_counts.csv"
    counts_pub = read_text_table(original / path)

    def recount(frame):
        g = frame.groupby(["series", "model", "status"]).size()
        return {k: int(v) for k, v in g.items()}
    published_counts = recount(published_fr)
    table_counts = {(r.series, r.model, r.status): int(float(r.n)) for r in counts_pub.itertuples()}
    if published_counts != table_counts:
        raise StagingError(f"{path}: recount of the published fit records does not reproduce it")
    staged_counts = recount(fr_typed)
    changed_rows = []
    for j, r in enumerate(counts_pub.itertuples()):
        new_n = staged_counts.get((r.series, r.model, r.status), 0)
        if new_n != int(float(r.n)):
            cell_changes.append({"path": path, "row": j, "column": "n", "key_series": r.series,
                                 "key_model": r.model, "key_status": r.status,
                                 "published": r.n, "reference": r.n, "corrected": str(new_n)})
            counts_pub.at[j, "n"] = str(new_n)
            changed_rows.append(j)
    if set(staged_counts) != set(table_counts):
        raise StagingError(f"{path}: the set of (series, model, status) changed")
    stamp.apply(counts_pub, changed_rows)
    write_text_table(counts_pub, staged / path)

    # -- 2e. the 8 state-dependence Wald rows of all_test_results -------------------------
    path = "diagnostics/all_test_results.csv"
    tests = read_text_table(original / path)
    assert_roundtrip(original / path)
    is_wald = tests["name"].str.contains("Wald") & (tests["series"] == SERIES) \
        & (tests["model"] == f"{MODEL} vs AR")
    positions = list(is_wald.to_numpy().nonzero()[0])
    if len(positions) != 8:
        raise StagingError(f"{path}: {len(positions)} UNRATE MSAR vs AR Wald rows, expected 8")

    def wald_rows(t35):
        rows = t35[(t35["series"] == SERIES) & (t35["model"] == f"{MODEL} vs AR")]
        out = []
        for r in rows.itertuples():
            for kind, stat, p in (("joint", r.joint_wald_statistic, r.joint_wald_p),
                                  ("slopes", r.slopes_wald_statistic, r.slopes_wald_p)):
                out.append((kind, float(stat), float(p)))
        return out

    def build(template, stat, p):
        reject = p < SIGNIFICANCE
        result = TestResult(
            name=template["name"], null_hypothesis=template["null_hypothesis"],
            statistic=stat, p_value=p, reference=template["reference"],
            decision_5pct="reject" if reject else "do not reject",
            implication=("realized relative loss differs across the predeclared states" if reject
                         else "no evidence that realized relative loss differs across states"),
            series=SERIES, model=f"{MODEL} vs AR", tuning={"significance": SIGNIFICANCE})
        return text_rows(tables.test_table([result])).iloc[0]

    t35_path = "forecast_tests/T3.5_state_loss_regression.csv"
    pub_w = wald_rows(pd.read_csv(original / t35_path, float_precision="round_trip"))
    new_w = wald_rows(pd.read_csv(staged / t35_path, float_precision="round_trip"))
    check_cols = ["name", "null_hypothesis", "statistic", "p_value", "reference",
                  "decision_5pct", "implication", "series", "model", "tuning", "stars"]
    for pos, (kind, stat, p) in zip(positions, pub_w):
        rebuilt = build(tests.iloc[pos], stat, p)
        bad = [c for c in check_cols if not same_value(str(rebuilt[c]), str(tests.at[pos, c]))]
        if bad:
            raise StagingError(f"{path}: Wald row {pos} not reproduced from published T3.5: {bad}")
    wald_changed = []
    for pos, (kind, stat, p) in zip(positions, new_w):
        rebuilt = build(tests.iloc[pos], stat, p)
        changed = False
        for column in check_cols:
            if not same_value(str(rebuilt[column]), str(tests.at[pos, column])):
                cell_changes.append({"path": path, "row": int(pos), "column": column,
                                     "key_series": SERIES, "key_model": f"{MODEL} vs AR",
                                     "key_name": tests.at[pos, "name"],
                                     "published": tests.at[pos, column], "reference": tests.at[pos, column],
                                     "corrected": str(rebuilt[column])})
                tests.at[pos, column] = str(rebuilt[column])
                changed = True
        if changed:
            wald_changed.append(int(pos))
    stamp.apply(tests, wald_changed)
    write_text_table(tests, staged / path)
    report["all_test_results_wald"] = {"rows": [int(p) for p in positions],
                                       "validated_against_published_t35": True,
                                       "rows_changed": wald_changed}

    # -- 2f. F4.8_UNRATE ------------------------------------------------------------------
    comp_path = "robustness/window_length_comparison.csv"
    baseline_length = int(config.require("robustness.window_lengths")["baseline"]["M"])
    benchmark = str(config.get("evaluation.benchmark"))

    def render(table_path, target_stem):
        t = pd.read_csv(table_path, float_precision="round_trip")
        t = t[t["series"] == SERIES].drop(columns=[c for c in PROV + ("correction_status",) if c in t.columns])
        fig = figures.window_length_sensitivity(t, series_id=SERIES, baseline_length=baseline_length,
                                                benchmark=benchmark)
        return figures.save(fig, target_stem, None, None)
    check_dir = args.out / "f48_reproduction_check"
    written = render(original / comp_path, check_dir / f"F4.8_{SERIES}")
    reproduced = {p.name: p.read_bytes() == (original / "figures" / p.name).read_bytes() for p in written}
    f48 = {"published_reproduced_from_published_table": reproduced}
    if not all(reproduced.values()):
        raise StagingError(f"F4.8_{SERIES}: the published figure is not reproduced: {reproduced}")
    if (staged / comp_path).read_bytes() != (original / comp_path).read_bytes():
        new = render(staged / comp_path, staged / "figures" / f"F4.8_{SERIES}")
        for p in new:
            side = json.loads((original / "figures" / (p.name + ".provenance.json")).read_text())
            side.update(stamp.values)
            side["b1_correction"] = "re-rendered by the pinned code from the corrected window-length table"
            (staged / "figures" / (p.name + ".provenance.json")).write_text(json.dumps(side, indent=2, sort_keys=True))
        f48["re_rendered"] = [p.name for p in new]
        f48["changed"] = {p.name: p.read_bytes() != (original / "figures" / p.name).read_bytes() for p in new}
    report["f48"] = f48
    shutil.rmtree(check_dir)

    # -- 2g. output inventory ---------------------------------------------------------------
    path = "manifests/output_inventory.csv"
    inventory = read_text_table(original / path)
    assert_roundtrip(original / path)
    changed_files = sorted(p.relative_to(staged).as_posix() for p in staged.rglob("*")
                           if p.is_file() and published_hashes.get(p.relative_to(staged).as_posix()) != sha(p))
    inv_rows = []
    for j, rel in enumerate(inventory["path"]):
        if rel in changed_files and rel != path:
            target = staged / rel
            inventory.at[j, "bytes"] = str(target.stat().st_size)
            inventory.at[j, "sha256"] = sha(target)
            inv_rows.append(j)
    stamp.apply(inventory, inv_rows)
    not_inventoried = [f for f in changed_files if f not in set(inventory["path"])
                       and not f.endswith(".provenance.json")]
    write_text_table(inventory, staged / path)
    report["inventory"] = {"rows_updated": len(inv_rows), "changed_files_not_in_inventory": not_inventoried}

    # -- records -------------------------------------------------------------------------------
    changed_files = sorted(p.relative_to(staged).as_posix() for p in staged.rglob("*")
                           if p.is_file() and published_hashes.get(p.relative_to(staged).as_posix()) != sha(p))
    new_files = [f for f in changed_files if f not in published_hashes]
    comparison = [{"path": f, "published_sha256": published_hashes.get(f, ""),
                   "staged_sha256": sha(staged / f), "bytes": (staged / f).stat().st_size}
                  for f in changed_files]
    pd.DataFrame(comparison).to_csv(args.out / "b1_changed_files.csv", index=False)
    pd.DataFrame(cell_changes).to_csv(args.out / "b1_cell_changes.csv", index=False)
    report.update({
        "files_total": len(published_hashes), "files_changed": len(changed_files),
        "files_added": new_files, "files_unchanged_byte_identical": len(published_hashes) - len(set(changed_files) - set(new_files)),
        "cell_changes": len(cell_changes), "parquet_rows_patched": parquet_rows,
        "figures": figure_checks, "finished_utc": tb.utc_stamp()})
    if new_files:
        raise StagingError(f"the staged tree gained files: {new_files}")
    after = {p.relative_to(original).as_posix(): sha(p) for p in sorted(original.rglob("*")) if p.is_file()}
    if after != published_hashes:
        raise StagingError("the published tree changed during staging")
    report["published_tree_unchanged"] = True
    tb.write_json_atomic(args.out / "b1_staging_report.json", report)
    return report


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))
