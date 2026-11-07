"""Stage 3 of the Part 8 integration dry run: outputs the R1 workflow does not rebuild.

The pinned R1 workflow regenerates 93 files. Outputs derived from re-estimated chains or
from regenerated tables, but not rebuilt by the workflow, are rebuilt here. Each builder
first reproduces the BASE tree's values from the base inputs (refusing otherwise), then
builds from the release inputs. No model is estimated: chains are replayed from the
merged refit cache with every estimator refused and fit calls counted.

  3a fit records       blocks of the 17 re-estimated chains; a record is replaced only
                       where the re-estimate does not reproduce it (status, reason codes,
                       loglik <= 1e-6, parameters <= 1e-8 scaled, regime labels aligned)
  3b T4.7 registry     failure events of every chain whose records changed
  3c T4.7 counts       recounted from the final fit records
  3d Wald rows         the state-dependence and joint Wald rows of all_test_results,
                       rebuilt from the release T3.5 (stale in the provisional releases)
  3e T4.6 summary      ARMA comparison columns, recomputed from the release ARMA forecasts
  3f F4.8              re-rendered for every series whose plotted inputs changed (D2)
  3g records           inventory and file comparison against the base tree
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r1_integration_common as ic  # noqa: E402

PROV = tuple(sorted(ic.PROVENANCE))
WALD_NAMES = ("joint", "slopes")


class Stamp:
    def __init__(self, values: dict):
        self.values = dict(values)

    def apply(self, frame, rows=None):
        for column, value in self.values.items():
            if rows is None:
                frame[column] = value
            elif column in frame.columns:
                frame.loc[list(rows), column] = value
        return frame


def assert_roundtrip(path: Path) -> None:
    import io
    buffer = io.StringIO()
    ic.read_table(path).to_csv(buffer, index=False)
    if buffer.getvalue().encode() != path.read_bytes():
        raise ic.IntegrationError(f"{path}: text round trip is not byte-identical")


def text_rows(frame):
    import io
    import pandas as pd
    buffer = io.StringIO()
    frame.to_csv(buffer, index=False)
    buffer.seek(0)
    return pd.read_csv(buffer, dtype=str, keep_default_na=False)


def match_number_format(new, published):
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


# -- 3a fit records ----------------------------------------------------------------------

def record_reproduced(new_row, old_row, model: str) -> tuple[bool, str]:
    """The Tier B agreement rule (`r1_tierb.agreement`) for one record."""
    import r1_tierb as tb
    if str(new_row["status"]) != str(old_row["status"]):
        return False, "classification_changed"
    if tb._codes(new_row["reason_codes"]) != tb._codes(old_row["reason_codes"]):
        return False, "classification_changed"
    mine, theirs = tb._parse_params(new_row["params"]), tb._parse_params(old_row["params"])
    if set(mine) != set(theirs):
        return False, "parameter_names_differ"
    l_ok = tb._scaled_diff(new_row["loglik"], old_row["loglik"]) <= tb.LOGLIK_TOLERANCE
    p_diff, _ = tb.aligned_param_diff(mine, theirs, model)
    if l_ok and p_diff <= tb.PARAM_TOLERANCE:
        return True, "reproduced"
    return False, "optimizer_sensitivity" if model in tb.WARM_STARTED else "reproduction_failure"


def candidate_runs(fit_records, job, spec_label: str | None = None) -> list[list[int]]:
    """Contiguous runs of one series' and model's records, each a separate chain.

    A run breaks at a gap in the row index or where the refit date does not increase (a
    new chain starts). Window spans are not used: for AR models the recorded window is the
    effective sample after the lags, so it is not the chain's window length.
    """
    import numpy as np
    f = fit_records[(fit_records["series"] == job.series_name)
                    & (fit_records["model"] == job.spec.model)]
    if spec_label is not None:
        f = f[f["spec_label"] == spec_label]
    runs, current, last_index, last_date = [], [], None, None
    dates = f["refit_date"].astype(str).str[:10].to_numpy()
    for index, date in zip(f.index.to_numpy(), dates):
        if current and (index != last_index + 1 or date <= last_date):
            runs.append(current)
            current = []
        current.append(int(index))
        last_index, last_date = index, date
    if current:
        runs.append(current)
    return runs


def locate_block(fit_records, job, new, model: str, used: set[int] = frozenset()) -> tuple[dict, str]:
    """The published records of exactly this chain: same specification and refit dates.

    First the B1 rule (`stage_block`), if its block has the chain's specification and refit
    dates; otherwise the contiguous runs with the chain's specification label and refit-date
    sequence, not already assigned to another chain. Several such runs (a robustness chain
    that duplicates the baseline chain, e.g. T4.2 at the baseline lag) are acceptable only
    if the chain reproduces every record of each of them: then no record is replaced and the
    latest run (robustness stages are written after the forecasting stage) is recorded.
    Otherwise the dry run refuses.
    """
    import r1_original_cache_audit as audit
    dates = [str(d)[:10] for d in new["refit_date"]]
    label = str(new["spec_label"].iloc[0])
    block, provenance = audit.stage_block(fit_records, job)
    if block is not None and sorted(block) == dates and \
            {str(r.spec_label) for r in block.values()} == {label} and \
            not used & {int(r.Index) for r in block.values()}:
        return block, provenance
    candidates = [run for run in candidate_runs(fit_records, job, label)
                  if list(fit_records.loc[run, "refit_date"].astype(str).str[:10]) == dates
                  and not used & set(run)]
    if not candidates:
        raise ic.IntegrationError(f"{job.task_id}: no published block with the chain's "
                                  f"specification {label!r} and {len(dates)} refit dates")
    note = ""
    if len(candidates) > 1:
        complete = [run for run in candidates
                    if all(record_reproduced(new.iloc[i], fit_records.loc[pos], model)[0]
                           for i, pos in enumerate(run))]
        if len(complete) != len(candidates):
            raise ic.IntegrationError(f"{job.task_id}: {len(candidates)} published blocks with the "
                                      "chain's refit dates, not all reproduced: ambiguous")
        note = f"; {len(candidates)} identical blocks, every record reproduced, none replaced"
    run = candidates[-1]
    chosen = fit_records.loc[run]
    return ({str(r.refit_date)[:10]: r for r in chosen.itertuples()},
            f"run with the chain's specification and refit dates; rows {run[0]}-{run[-1]}{note}")


def replay(job, fits: Path, identity, config):
    """One chain through the pinned `rolling.run_chain`, served by the read-only live replay
    of the merged refit cache (`ic.readonly_refit_class`): every estimator refused, fit calls
    counted (must be 0), every origin served from the cache, nothing written."""
    import r1_tierb as tb
    from thesis.correction import guard
    from thesis.forecasting import rolling
    cache = ic.readonly_refit_class()(fits)
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
        raise ic.IntegrationError(f"{job.task_id}: replay called the estimator {calls['n']} times "
                                  f"({chain.from_cache} of {chain.attempted} origins from the cache)")
    return chain


def replay_chains(jobs, tasks, fits: Path, identity, config) -> dict:
    """Each chain replayed through the pinned run_chain from the merged refit cache."""
    return {task: replay(jobs[task], fits, identity, config) for task in tasks}


def patch_fit_records(base: Path, release: Path, chains: dict, jobs, stamp: Stamp) -> dict:
    import pandas as pd
    import r1_original_cache_audit as audit
    from thesis.reporting import tables
    fr_csv, fr_pq = base / "models" / "fit_records.csv", base / "models" / "fit_records.parquet"
    assert_roundtrip(fr_csv)
    base_typed = pd.read_parquet(fr_pq)
    fr_text = ic.read_table(fr_csv)
    if len(fr_text) != len(base_typed):
        raise ic.IntegrationError("fit_records csv and parquet differ in length")
    fr_typed = base_typed.copy()
    report, used, blocks = {}, set(), {}
    for task, chain in chains.items():
        job = jobs[task]
        new = tables.fit_records_table(chain.fit_records)
        block, provenance = locate_block(base_typed, job, new, job.spec.model, used)
        positions = sorted(r.Index for r in block.values())
        if used & set(positions):
            raise ic.IntegrationError(f"{task}: its fit-record block overlaps another chain's")
        used |= set(positions)
        dates = sorted(block)
        new_dates = [str(d)[:10] for d in new["refit_date"]]
        if new_dates != dates:
            raise ic.IntegrationError(f"{task}: re-estimated origins differ from the published "
                                      f"block ({len(new_dates)} vs {len(dates)})")
        new_text = match_number_format(text_rows(stamp.apply(new.copy())), fr_text)
        replaced, categories = [], {}
        for i, date in enumerate(dates):
            pos = block[date].Index
            ok, category = record_reproduced(new.iloc[i], base_typed.iloc[pos], job.spec.model)
            categories[category] = categories.get(category, 0) + 1
            if ok:
                continue
            replaced.append(date)
            fr_text.iloc[pos] = new_text.iloc[i][fr_text.columns].to_numpy()
            for j, column in enumerate(fr_typed.columns):
                value = stamp.values[column] if column in stamp.values else new.iloc[i][column]
                fr_typed.iat[pos, j] = value
        statuses = pd.Series([r.status.value for r in chain.fit_records]).value_counts().to_dict()
        report[task] = {"block": provenance, "records": len(dates), "categories": categories,
                        "replaced_origins": replaced,
                        "replaced_positions": [int(block[d].Index) for d in replaced],
                        "block_positions": [int(positions[0]), int(positions[-1])],
                        "statuses": statuses, "from_cache": chain.from_cache, "estimations": 0}
        blocks[task] = block
    fr_text.to_csv(release / "models" / "fit_records.csv", index=False)
    if list(fr_typed.dtypes) != list(base_typed.dtypes):
        raise ic.IntegrationError("fit_records.parquet: column dtypes changed while patching")
    fr_typed.to_parquet(release / "models" / "fit_records.parquet", index=False)
    return {"chains": report, "blocks": blocks, "base_typed": base_typed, "final_typed": fr_typed}


# -- 3b/3c T4.7 ------------------------------------------------------------------------

def failure_signature(rows) -> list[tuple]:
    import r1_b1_staged_correction as b1
    return b1.failure_signature(rows)


def patch_registry(base: Path, release: Path, chains: dict, jobs, fit: dict, stamp: Stamp) -> dict:
    import pandas as pd
    import r1_b1_staged_correction as b1
    import r1_original_cache_audit as audit
    from thesis.reporting import tables
    path = "robustness/T4.7_failure_registry.csv"
    registry = ic.read_table(base / path)
    assert_roundtrip(base / path)
    report, starts, used = {}, [], set()
    for task, chain in chains.items():
        if not fit["chains"][task]["replaced_origins"]:
            continue                       # records unchanged: their events are unchanged
        block = fit["blocks"][task]
        signature = failure_signature([block[d] for d in sorted(block)])
        new_events = match_number_format(text_rows(stamp.apply(
            tables.failure_registry_table(chain.failures))), registry)
        if not signature:
            raise ic.IntegrationError(f"{task}: no published failure events to locate the block "
                                      "(insertion position undefined)")
        found = [s for s in b1.find_blocks(registry, signature) if s not in used]
        if not found:
            raise ic.IntegrationError(f"{task}: failure events not found in {path}")
        used.add(found[0])
        starts.append((found[0], len(signature), task, len(found), new_events))
    pieces, cursor = [], 0
    for start, n, task, n_found, new_events in sorted(starts, key=lambda s: s[0]):
        if start < cursor:
            raise ic.IntegrationError(f"{path}: overlapping event blocks")
        old = registry.iloc[start:start + n]
        columns = [c for c in new_events.columns if c not in ic.PROVENANCE]
        old_keyed = {tuple(old.iloc[j][columns]): old.iloc[j] for j in range(len(old))}
        rows = [old_keyed.get(tuple(new_events.iloc[j][columns]), new_events.iloc[j])
                for j in range(len(new_events))]
        kept = sum(1 for j in range(len(new_events)) if tuple(new_events.iloc[j][columns]) in old_keyed)
        pieces += [registry.iloc[cursor:start], pd.DataFrame(rows)[registry.columns]]
        cursor = start + n
        report[task] = {"published_rows": f"{start}-{start + n - 1}", "events_before": n,
                        "events_after": len(new_events), "kept_verbatim": kept,
                        "candidate_blocks_with_same_signature": n_found}
    pieces.append(registry.iloc[cursor:])
    out = pd.concat(pieces, ignore_index=True) if starts else registry
    out.to_csv(release / path, index=False)
    return report


def recount(frame) -> dict:
    g = frame.groupby(["series", "model", "status"]).size()
    return {k: int(v) for k, v in g.items()}


def patch_status_counts(base: Path, release: Path, fit: dict, stamp: Stamp) -> dict:
    path = "robustness/T4.7_status_counts.csv"
    counts = ic.read_table(base / path)
    table = {(r.series, r.model, r.status): int(float(r.n)) for r in counts.itertuples()}
    if recount(fit["base_typed"]) != table:
        raise ic.IntegrationError(f"{path}: recount of the base fit records does not reproduce it")
    final = recount(fit["final_typed"])
    if set(final) != set(table):
        raise ic.IntegrationError(f"{path}: the set of (series, model, status) changed: "
                                  f"{sorted(set(final) ^ set(table))}")
    changed = []
    for j, r in enumerate(counts.itertuples()):
        n = final[(r.series, r.model, r.status)]
        if n != int(float(r.n)):
            counts.at[j, "n"] = str(n)
            changed.append({"row": j, "series": r.series, "model": r.model, "status": r.status,
                            "before": r.n, "after": str(n)})
    stamp.apply(counts, [c["row"] for c in changed])
    counts.to_csv(release / path, index=False)
    return {"rows_changed": changed}


# -- 3d Wald rows ------------------------------------------------------------------------

def wald_values(t35) -> dict:
    """(series, model) -> [(kind, statistic, p)] in T3.5 order, inference available only."""
    out: dict = {}
    for r in t35.itertuples():
        if str(getattr(r, "inference_available", "True")) != "True":
            continue
        for kind, stat, p in (("joint", r.joint_wald_statistic, r.joint_wald_p),
                              ("slopes", r.slopes_wald_statistic, r.slopes_wald_p)):
            out.setdefault((r.series, r.model), []).append((kind, float(stat), float(p)))
    return out


def rebuild_wald(base: Path, release: Path, stamp: Stamp) -> dict:
    import pandas as pd
    from thesis.core.schemas import TestResult
    from thesis.evaluation.state_loss_regression import SIGNIFICANCE
    from thesis.reporting import tables
    path, t35 = "diagnostics/all_test_results.csv", "forecast_tests/T3.5_state_loss_regression.csv"
    tests = ic.read_table(release / path)          # the workflow's merged file (ZA rows added)
    base_tests = ic.read_table(base / path)
    head = tests.iloc[:len(base_tests)][list(base_tests.columns)].reset_index(drop=True)
    if list(tests.columns[:len(base_tests.columns)]) != list(base_tests.columns) or \
            not head.equals(base_tests):
        raise ic.IntegrationError(f"{path}: the workflow changed rows of the base file")
    is_wald = tests["name"].str.contains("Wald")
    groups: dict = {}
    for pos in is_wald.to_numpy().nonzero()[0]:
        groups.setdefault((tests.at[pos, "series"], tests.at[pos, "model"]), []).append(int(pos))
    check = ["name", "null_hypothesis", "statistic", "p_value", "reference", "decision_5pct",
             "implication", "series", "model", "tuning", "stars"]

    def build(template, series, model, stat, p):
        reject = p < SIGNIFICANCE
        result = TestResult(
            name=template["name"], null_hypothesis=template["null_hypothesis"], statistic=stat,
            p_value=p, reference=template["reference"],
            decision_5pct="reject" if reject else "do not reject",
            implication=("realized relative loss differs across the predeclared states" if reject
                         else "no evidence that realized relative loss differs across states"),
            series=series, model=model, tuning={"significance": SIGNIFICANCE})
        return text_rows(tables.test_table([result])).iloc[0]

    def expected(t35_frame):
        values = wald_values(t35_frame)
        if set(values) != set(groups):
            raise ic.IntegrationError(f"{path}: Wald groups {sorted(set(values) ^ set(groups))[:4]} "
                                      "differ between T3.5 and all_test_results")
        out = {}
        for key, positions in groups.items():
            if len(values[key]) != len(positions):
                raise ic.IntegrationError(f"{path}: {key}: {len(positions)} Wald rows, "
                                          f"{len(values[key])} in T3.5")
            for pos, (kind, stat, p) in zip(positions, values[key]):
                if not tests.at[pos, "name"].lower().startswith(
                        "joint" if kind == "joint" else "state-dependence"):
                    raise ic.IntegrationError(f"{path}: row {pos} is not a {kind} Wald row")
                out[pos] = build(tests.iloc[pos], key[0], key[1], stat, p)
        return out

    reproduced = expected(pd.read_csv(base / t35, float_precision="round_trip"))
    for pos, row in reproduced.items():
        bad = [c for c in check if not ic.same_cell(str(row[c]), str(base_tests.at[pos, c]))]
        if bad:
            raise ic.IntegrationError(f"{path}: Wald row {pos} not reproduced from the base T3.5: {bad}")
    changed = []
    for pos, row in expected(pd.read_csv(release / t35, float_precision="round_trip")).items():
        diff = [c for c in check if not ic.same_cell(str(row[c]), str(tests.at[pos, c]))]
        if diff:
            for c in check:
                tests.at[pos, c] = str(row[c])
            changed.append({"row": pos, "series": tests.at[pos, "series"],
                            "model": tests.at[pos, "model"], "columns": diff})
    stamp.apply(tests, [c["row"] for c in changed])
    tests.to_csv(release / path, index=False)
    return {"wald_rows": int(is_wald.sum()), "validated_against_base_t35": True,
            "rows_changed": changed}


# -- 3e T4.6 summary ---------------------------------------------------------------------

T46_COLUMNS = ("n_common", "mean_absolute_mean_forecast_change",
               "max_absolute_mean_forecast_change", "arma_rmse", "garch_rmse")


def t46_comparison(tree: Path, series: str) -> dict | None:
    """The pinned `_t46_arma_garch` comparison block from a tree's own files."""
    import numpy as np
    import pandas as pd
    from thesis.evaluation import metrics
    garch = pd.read_csv(tree / "robustness" / f"T4.6_arma_garch_{series}.csv",
                        float_precision="round_trip")
    if garch.empty:
        return None
    horizons = garch["horizon"].unique()
    if len(horizons) != 1:
        raise ic.IntegrationError(f"T4.6 {series}: several horizons")
    forecasts = pd.read_csv(tree / "forecasts" / f"forecasts_{series}.csv",
                            float_precision="round_trip")
    arma = forecasts[(forecasts["model"] == "ARMA") & (forecasts["horizon"] == horizons[0])]
    if arma.empty:
        return None
    garch = garch.assign(target_date=pd.to_datetime(garch["target_date"]))
    arma = arma.assign(target_date=pd.to_datetime(arma["target_date"])).set_index("target_date")
    joined = garch.set_index("target_date").join(arma["forecast"].rename("arma_forecast"),
                                                 how="inner")
    difference = (joined["forecast"] - joined["arma_forecast"]).to_numpy(dtype=float)
    return {"n_common": int(np.isfinite(difference).sum()),
            "mean_absolute_mean_forecast_change": float(np.nanmean(np.abs(difference))),
            "max_absolute_mean_forecast_change": float(np.nanmax(np.abs(difference)))
            if difference.size else float("nan"),
            "arma_rmse": metrics.rmse((joined["actual"] - joined["arma_forecast"]).to_numpy(dtype=float)),
            "garch_rmse": metrics.rmse(joined["error"].to_numpy())}


def patch_t46(base: Path, release: Path, stamp: Stamp) -> dict:
    path = "robustness/T4.6_arma_garch_summary.csv"
    summary = ic.read_table(base / path)
    assert_roundtrip(base / path)
    changed = []
    for j, row in summary.iterrows():
        series = row["series"]
        if not (base / "robustness" / f"T4.6_arma_garch_{series}.csv").exists():
            continue
        if (release / "robustness" / f"T4.6_arma_garch_{series}.csv").read_bytes() != \
                (base / "robustness" / f"T4.6_arma_garch_{series}.csv").read_bytes():
            raise ic.IntegrationError(f"T4.6 {series}: the per-origin file changed")
        before = t46_comparison(base, series)
        if before is None:
            continue
        bad = [c for c in T46_COLUMNS if not ic.same_cell(str(before[c]), str(row[c]))]
        if bad:
            raise ic.IntegrationError(f"{path}: {series} not reproduced from the base files: {bad}")
        after = t46_comparison(release, series)
        cells = [c for c in T46_COLUMNS if not ic.same_cell(str(after[c]), str(row[c]))]
        for c in cells:
            summary.at[j, c] = str(after[c])
        if cells:
            changed.append({"row": j, "series": series, "columns": cells})
    stamp.apply(summary, [c["row"] for c in changed])
    summary.to_csv(release / path, index=False)
    return {"rows_changed": changed, "validated_against_base": True}


# -- 3f F4.8 -----------------------------------------------------------------------------

F48_PLOTTED = ("model", "window_length", "oos_r2_vs_benchmark", "n_valid")


def f48_inputs(table_path: Path, series: str) -> list[tuple]:
    rows = ic.read_rows(table_path)
    return sorted(tuple(r[c] for c in F48_PLOTTED) for r in rows
                  if r["series"] == series and r["horizon"] == "1")


def render_f48(table_path: Path, series: str, stem: Path, config) -> list[Path]:
    import pandas as pd
    from thesis.reporting import figures
    benchmark = str(config.get("evaluation.benchmark"))
    t = pd.read_csv(table_path, float_precision="round_trip")
    t = t[t["series"] == series].drop(columns=[c for c in (*PROV, "correction_status")
                                               if c in t.columns])
    lengths = t["baseline_window_length"].dropna().unique()
    if len(lengths) != 1:
        raise ic.IntegrationError(f"F4.8_{series}: baseline window length not unique: {lengths}")
    baseline_length = int(lengths[0])
    fig = figures.window_length_sensitivity(t, series_id=series, baseline_length=baseline_length,
                                            benchmark=benchmark)
    return figures.save(fig, stem, None, None)


def patch_f48(base: Path, release: Path, scratch: Path, config, stamp: Stamp) -> dict:
    table = "robustness/window_length_comparison.csv"
    series_all = sorted({r["series"] for r in ic.read_rows(base / table)})
    report = {"reproduced_from_base": {}, "re_rendered": [], "inputs_changed": []}
    for series in series_all:
        written = render_f48(base / table, series, scratch / f"F4.8_{series}", config)
        same = {p.name: p.read_bytes() == (base / "figures" / p.name).read_bytes() for p in written}
        report["reproduced_from_base"][series] = same
        if not all(same.values()):
            raise ic.IntegrationError(f"F4.8_{series}: the base figure is not reproduced from the "
                                      f"base table: {same}")
        if f48_inputs(base / table, series) == f48_inputs(release / table, series):
            continue
        report["inputs_changed"].append(series)
        for path in render_f48(release / table, series, release / "figures" / f"F4.8_{series}",
                               config):
            side = json.loads((base / "figures" / (path.name + ".provenance.json")).read_text())
            side.update(stamp.values)
            side["integration_dry_run"] = ("re-rendered by the pinned code from the integrated "
                                           "window-length table (decision D2)")
            (release / "figures" / (path.name + ".provenance.json")).write_text(
                json.dumps(side, indent=2, sort_keys=True))
            report["re_rendered"].append(path.name)
    shutil.rmtree(scratch, ignore_errors=True)
    return report


# -- 3g records --------------------------------------------------------------------------

def rewrite_records(base: Path, release: Path, regenerated: set[str], dependents: set[str]) -> dict:
    """Inventory and file comparison against the base tree, after stage 3."""
    import pandas as pd
    from thesis.correction.compare import compare_trees
    manifests = release / "manifests"
    comparison = compare_trees(base, release)
    comparison["regenerated_by_r1"] = comparison["path"].isin(regenerated)
    comparison["regenerated_by_integration_dependents"] = comparison["path"].isin(dependents)
    comparison.to_csv(manifests / "correction_file_comparison.csv", index=False)
    inventory = []
    for path in sorted(p for p in release.rglob("*") if p.is_file()):
        relative = path.relative_to(release).as_posix()
        if relative == "manifests/output_inventory.csv":
            continue
        origin = base / relative
        source = ("regenerated_r1" if relative in regenerated else
                  "regenerated_integration_dependents" if relative in dependents else
                  "correction_record" if relative.startswith("manifests/correction_") else
                  "original_unchanged")
        inventory.append({"path": relative, "bytes": path.stat().st_size,
                          "sha256": ic.sha256_file(path), "source": source,
                          "original_sha256": ic.sha256_file(origin) if origin.exists() else ""})
    pd.DataFrame(inventory).to_csv(manifests / "output_inventory.csv", index=False)
    return {"files": len(inventory),
            "by_source": pd.Series([r["source"] for r in inventory]).value_counts().to_dict()}


# -- stage driver --------------------------------------------------------------------------

def run(p: dict, run_id: str, tasks: list[str] | None = None) -> dict:
    """Stage 3. `tasks` defaults to the 17 re-estimated chains (a subset only in rehearsals)."""
    import pandas as pd
    import r1_tierb as tb
    from thesis.correction import guard
    work = p["work"]
    base, pre = work / "base", work / "assembly" / "release"
    release = ic.inside(work, work / "release")
    if release.exists():
        raise ic.IntegrationError(f"{release} exists; use a new work folder")
    shutil.copytree(pre, release)
    regenerated = set(json.loads((work / "assembly" / "corrected" / "r1_summary.json").read_text())
                      ["regenerated_files"])
    sample = ic.read_table(release / "forecast_tests" / "T3.3_main_forecast_table.csv").iloc[0]
    if sample["run_id"] != run_id:
        raise ic.IntegrationError("the release does not carry the corrected run's ID")
    stamp = Stamp({"run_id": run_id, "data_snapshot_hash": sample["data_snapshot_hash"],
                   "code_commit_sha": ic.SCIENTIFIC_PIN, "config_hash": sample["config_hash"],
                   "created_utc": sample["created_utc"]})
    with guard.estimation_forbidden(), tb.no_estimation_allowed():
        jobs, identity, config = tb.build_jobs(base, p["code"])
    tasks = sorted(tasks or (list(tb.TIER_A_CHAINS) + list(tb.TIER_B_CHAINS)))
    import r1_part8_integration as drv
    fits = work / "merged_refit" / "fits"
    integrity = {"before_replay": drv.check_cache_listings(work, fits, p["cache_root"] / "fits",
                                                           "before the dependent-output replay")}
    chains = replay_chains(jobs, tasks, fits, identity, config)
    integrity["after_replay"] = drv.check_cache_listings(work, fits, p["cache_root"] / "fits",
                                                         "during the dependent-output replay")
    report: dict = {"run_id": run_id, "estimation": "none (estimators refused; fit calls counted)",
                    "cache_integrity": integrity}
    fit = patch_fit_records(base, release, chains, jobs, stamp)
    report["fit_records"] = fit["chains"]
    report["t47_registry"] = patch_registry(base, release, chains, jobs, fit, stamp)
    report["t47_status_counts"] = patch_status_counts(base, release, fit, stamp)
    report["wald_rows"] = rebuild_wald(base, release, stamp)
    report["t46_summary"] = patch_t46(base, release, stamp)
    report["f48"] = patch_f48(base, release, ic.inside(work, work / "scratch_f48"), config, stamp)
    dependents = {"models/fit_records.csv", "models/fit_records.parquet",
                  "robustness/T4.7_failure_registry.csv", "robustness/T4.7_status_counts.csv",
                  "diagnostics/all_test_results.csv", "robustness/T4.6_arma_garch_summary.csv"}
    dependents |= {f"figures/{n}" for n in report["f48"]["re_rendered"]}
    dependents |= {f"figures/{n}.provenance.json" for n in report["f48"]["re_rendered"]}
    report["records"] = rewrite_records(base, release, regenerated, dependents)
    report["dependent_files"] = sorted(dependents)
    ic.write_json(work / "dryrun_report" / "dependents_report.json", report)
    # every replayed chain's per-origin categories, for the validation and the report
    rows = []
    for task, info in fit["chains"].items():
        rows.append({"task": task, "records": info["records"],
                     "replaced": len(info["replaced_origins"]),
                     "replaced_origins": ";".join(info["replaced_origins"]),
                     **{f"n_{k}": v for k, v in sorted(info["categories"].items())},
                     **{f"status_{k}": v for k, v in sorted(info["statuses"].items())}})
    ic.write_rows(work / "dryrun_report" / "reestimated_chain_records.csv",
                  sorted(rows, key=lambda r: r["task"]))
    return {k: v for k, v in report.items() if k not in ("fit_records",)} | {
        "fit_records_replaced": {t: len(v["replaced_origins"]) for t, v in fit["chains"].items()}}
