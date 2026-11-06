#!/usr/bin/env python3
"""R1: complete read-only audit of the ORIGINAL fit cache and a baseline-impact assessment.

NO MODEL IS ESTIMATED. Every stage runs with the pinned estimators refused (`guard`
plus `r1_tierb.no_estimation_allowed`): an estimator call raises instead of fitting.
Nothing is written outside --out. Stages (run all, or one with --stage):

verify     the local copy of the original cache against the committed inventory
           (all 18,964 payload names and sizes) and the cache identity; a manifest of
           every payload's sha256 is written.
audit      every MSAR, STAR and ARMA job of the pipeline walked through the cache under the
           pinned CACHE-HIT rule and the pinned LIVE warm-start rule; per origin: key
           presence under each rule, horizon coverage, status, reason codes, starts tried,
           and agreement with the PUBLISHED fit record (records identified by their
           pipeline stage block, never guessed) and, for baseline chains, the published
           forecasts.
candidate  for one baseline chain (default forecasting:UNRATE|MSAR): the chain replayed
           from the original cache by the LIVE rule through the pinned `rolling.run_chain`
           (r1_tierb.live_replay_class over a read-only view), estimation refused. If any
           origin or horizon is missing, the stage stops and lists exactly what is missing.
impact     the pinned R1 workflow in LEGACY mode, twice, identically: on the published
           outputs (reference) and on a staging copy in which only that chain's rows of
           forecasts_<series> (and its origin-audit counts) are the candidate's. Every
           differing output file, and every differing cell of the tables, is listed; the
           reference is also compared with the published outputs (reproduction check).

Usage (Colab, from the audit notebook; locally on a partial cache for testing):
    python r1_original_cache_audit.py --cache-fits <original_cache/fits> \\
        --code-dir <pinned>/my-thesis/code --original <original output> \\
        --inventory <repo>/.../original_fit_cache_inventory.csv.gz \\
        --chain-sources <repo>/.../corrected_r1_summary.json --out <dir> [--stage S]
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r1_tierb as tb  # noqa: E402

STAGES = ("verify", "audit", "candidate", "impact")


# -- helpers -----------------------------------------------------------------------------

def start_set(diagnostics) -> dict[str, float]:
    """{start label: objective} from a payload's or a fit record's diagnostics."""
    if isinstance(diagnostics, dict):
        text = str(diagnostics.get("starts", ""))
    else:
        found = re.search(r"(?:^|; )starts=(.*?)(?:; [a-z_]+=|$)", str(diagnostics) + "; end=")
        text = found.group(1) if found else ""
    out = {}
    for part in text.split("; "):
        found = re.match(r"([\w.]+):obj=([^,]+)", part.strip())
        if found:
            try:
                out[found.group(1)] = float(found.group(2))
            except ValueError:
                out[found.group(1)] = float("nan")
    return out


def codes(value) -> str:
    if isinstance(value, (list, tuple)):
        return ";".join(sorted(str(v) for v in value))
    return ";".join(sorted(c for c in str(value or "").split(";") if c and c != "nan"))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        fields += [k for k in row if k not in fields]
    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or ["empty"])
        writer.writeheader()
        writer.writerows(rows)


def stage_block(fit_records, job):
    """The published fit records of exactly this job's chain, by pipeline-stage block.

    Records of one series, model and window span are written in contiguous blocks, one
    per pipeline stage that ran the chain (forecasting first, then the robustness
    exercises). Returns (records by date, provenance string) or (None, reason).
    """
    import numpy as np
    import pandas as pd
    f = fit_records[(fit_records["series"] == job.series_name)
                    & (fit_records["model"] == job.spec.model)]
    start, end = pd.to_datetime(f["window_start"]), pd.to_datetime(f["window_end"])
    step = 3 if job.frequency == "Q" else 1
    span = ((end.dt.year - start.dt.year) * 12 + end.dt.month - start.dt.month) // step + 1
    f = f[span == int(job.window_length)].sort_index()
    if f.empty:
        return None, "no published records with this window span"
    index = f.index.to_numpy()
    blocks = [f.loc[b] for b in np.split(index, np.where(np.diff(index) > 1)[0] + 1)]
    if len(blocks) == 1:
        chosen, rule = blocks[0], "single block"
    elif job.task_id.startswith("forecasting:"):
        chosen, rule = blocks[0], "first block (forecasting stage)"
    elif job.task_id.startswith("T4.1:"):
        shared = set(map(tuple, pd.concat([b for b in blocks])[["refit_date", "params"]]
                         .value_counts().loc[lambda s: s > 1].index))
        unique = [b for b in blocks
                  if not any((r.refit_date, r.params) in shared for r in b.itertuples())]
        if len(unique) != 1:
            return None, f"{len(blocks)} blocks, T4.1 block not unique"
        chosen, rule = unique[0], "block sharing no record with the others (T4.1)"
    elif job.task_id.startswith("T4.8:"):
        chosen, rule = blocks[-1], "last block (robustness T4.8 stage)"
    else:
        return None, f"{len(blocks)} blocks, no rule for {job.task_id}"
    if chosen["refit_date"].duplicated().any():
        return None, "duplicate origins inside the chosen block"
    records = {str(r.refit_date)[:10]: r for r in chosen.itertuples()}
    return records, f"{rule}; rows {chosen.index.min()}-{chosen.index.max()} of {len(blocks)} block(s)"


# -- stage: verify -----------------------------------------------------------------------

def verify(args) -> dict:
    expected = {}
    with gzip.open(args.inventory, "rt") as handle:
        for row in csv.DictReader(handle):
            expected[row["payload"]] = int(row["size"])
    present = {p.relative_to(args.cache_fits).as_posix(): p
               for p in Path(args.cache_fits).glob("*/*.json")}
    missing = sorted(set(expected) - set(present))
    extra = sorted(set(present) - set(expected))
    size_mismatch = [n for n in set(expected) & set(present)
                     if present[n].stat().st_size != expected[n]]
    digest, manifest = hashlib.sha256(), []
    for name in sorted(present):
        h = tb.sha256_file(present[name])
        manifest.append({"payload": name, "sha256": h})
        digest.update(f"{name} {h}\n".encode())
    write_csv(args.out / "verify" / "payload_sha256.csv", manifest)
    marked = sum(1 for n in sorted(present)[:200]
                 if tb.MARKER in json.loads(present[n].read_text()))
    result = {"expected_payloads": len(expected), "present_payloads": len(present),
              "missing": len(missing), "extra": len(extra), "size_mismatch": len(size_mismatch),
              "missing_sample": missing[:20], "extra_sample": extra[:20],
              "refit_marker_in_first_200": marked,
              "manifest_sha256": digest.hexdigest(),
              "complete": not missing and not extra and not size_mismatch}
    tb.write_json_atomic(args.out / "verify" / "verify.json", result)
    return result


# -- stage: audit ------------------------------------------------------------------------

def walk_both(job, fits: Path, identity, config):
    """Per-origin walk under both rules, recording key presence and horizon coverage.

    Never raises on a missing or non-covering payload: the walk of a rule stops there and
    the reason is recorded. Returns per-origin rows (along the LIVE path) and summaries.
    """
    import numpy as np
    from thesis.core.cache import FitCache
    from thesis.forecasting.rolling import _cache_key, _covers
    from thesis.forecasting.windows import estimation_origins
    cache = FitCache(fits, enabled=True)
    horizons = sorted(set(int(h) for h in job.horizons))
    use_warm = bool(config.get("forecasting.warm_starts", True))
    origins = estimation_origins(job.y.index, job.window_length, horizons,
                                 max_origins=job.max_origins)
    rows, summary = [], {}
    for rule in ("cache_hit", "live"):
        warm, completed, stop = None, 0, None
        for position, origin in enumerate(origins, start=1):
            window = job.y.iloc[origin.estimation_slice()]
            if not np.isfinite(window.to_numpy(dtype=float)).all():
                continue
            key = _cache_key(identity, job.series_name, job.transformation, job.spec,
                             origin, tb.predecessor_hash(warm, use_warm))
            path = cache.path_for(key)
            date = origin.origin_date.strftime("%Y-%m-%d")
            if not path.is_file():
                stop = {"origin": position, "refit_date": date, "reason": "key absent"}
                break
            payload = json.loads(path.read_text())
            if rule == "live":
                rows.append({"origin": position, "refit_date": date,
                             "payload": path.relative_to(fits).as_posix(),
                             "covers_horizons": _covers(payload, horizons),
                             "payload_horizons": ";".join(map(str, payload.get("horizons") or [])),
                             "_payload": payload})
            if not _covers(payload, horizons):
                stop = {"origin": position, "refit_date": date,
                        "reason": f"payload horizons {payload.get('horizons')} do not cover "
                                  f"{horizons}"}
                if rule == "cache_hit":
                    break
            completed += 1
            warm = (tb.live_warm_after(warm, payload) if rule == "live"
                    else payload.get("warm_payload"))
        summary[rule] = {"completed": completed, "planned": len(origins), "stop": stop}
    return rows, summary


def audit(args, jobs, identity, config, fit_records) -> dict:
    import pandas as pd
    from thesis.core.cache import FitCache
    from thesis.forecasting.rolling import _cache_key
    from thesis.forecasting.windows import estimation_origins
    sources = {}
    if args.chain_sources:
        for source, tasks in json.loads(Path(args.chain_sources).read_text())["chain_sources"].items():
            for task in tasks:
                sources[task] = source
    cache = FitCache(args.cache_fits, enabled=True)
    use_warm = bool(config.get("forecasting.warm_starts", True))
    published_forecasts = {}
    chains, origin_rows = [], []
    for task, job in sorted(jobs.items()):
        if job.spec.model not in ("MSAR", "MSAR3", "STAR", "ARMA"):
            continue
        rows, summary = walk_both(job, args.cache_fits, identity, config)
        records, provenance = stage_block(fit_records, job)
        forecasts = None
        if task.startswith("forecasting:"):
            series = job.series_name
            if series not in published_forecasts:
                published_forecasts[series] = pd.read_parquet(
                    Path(args.original) / "forecasts" / f"forecasts_{series}.parquet")
            pf = published_forecasts[series]
            forecasts = pf[pf["model"] == job.spec.model]
        origin_of = {o.origin_date.strftime("%Y-%m-%d"): o for o in estimation_origins(
            job.y.index, job.window_length, sorted(set(int(h) for h in job.horizons)),
            max_origins=job.max_origins)}
        counts = {"identical": 0, "differs": 0, "no_record": 0, "forecast_h1_differs": 0}
        previous = None
        warm = None
        for row in rows:
            payload = row.pop("_payload")
            record = (records or {}).get(row["refit_date"])
            cached = start_set((payload.get("record_detail") or {}).get("diagnostics"))
            row.update(task=task, status_cache=payload.get("status"),
                       codes_cache=codes(payload.get("reason_codes")),
                       loglik_cache=payload.get("loglik"), start_cache=payload.get("start_used"),
                       warm_tried_cache="warm" in cached,
                       n_starts_cache=len(cached),
                       forecast_h1_cache=(payload.get("forecasts") or {}).get("1"))
            if record is None:
                counts["no_record"] += 1
                row["record_comparison"] = "no published record"
            else:
                published_starts = start_set(record.diagnostics)
                same = (payload.get("status") == record.status
                        and codes(payload.get("reason_codes")) == codes(record.reason_codes)
                        and payload.get("loglik") == record.loglik)
                counts["identical" if same else "differs"] += 1
                row.update(status_published=record.status,
                           codes_published=codes(record.reason_codes),
                           loglik_published=record.loglik, start_published=record.start_used,
                           warm_tried_published="warm" in published_starts,
                           n_starts_published=len(published_starts),
                           record_comparison="identical" if same else "differs")
            if forecasts is not None:
                h1 = forecasts[(forecasts["horizon"] == 1)
                               & (forecasts["origin_date"].astype(str).str[:10] == row["refit_date"])]
                if len(h1):
                    pub = h1["forecast"].iloc[0]
                    cache_value = row["forecast_h1_cache"]
                    row["forecast_h1_published"] = pub
                    both_nan = pd.isna(pub) and (cache_value is None or pd.isna(cache_value))
                    if not both_nan and (cache_value is None or pd.isna(pub)
                                         or float(cache_value) != float(pub)):
                        counts["forecast_h1_differs"] += 1
            if previous is not None and previous.get("status") == "failed":
                origin = origin_of[row["refit_date"]]
                hit_key = _cache_key(identity, job.series_name, job.transformation, job.spec,
                                     origin, tb.predecessor_hash(previous.get("warm_payload"),
                                                                 use_warm))
                row["after_failed_fit"] = True
                row["cache_hit_key_present"] = cache.path_for(hit_key).is_file()
            warm = tb.live_warm_after(warm, payload)
            previous = payload
            origin_rows.append(row)
        published_failed = sum(1 for r in (records or {}).values() if r.status == "failed")
        chains.append({
            "task": task, "model": job.spec.model, "r1_source": sources.get(task, ""),
            "planned": summary["live"]["planned"],
            "cache_hit_completed": summary["cache_hit"]["completed"],
            "live_completed": summary["live"]["completed"],
            "live_complete_and_covering": (summary["live"]["completed"]
                                           == summary["live"]["planned"]
                                           and summary["live"]["stop"] is None),
            "cache_hit_stop": json.dumps(summary["cache_hit"]["stop"]),
            "live_stop": json.dumps(summary["live"]["stop"]),
            "rules_differ": summary["live"]["completed"] != summary["cache_hit"]["completed"],
            "published_records": len(records or {}), "published_block": provenance,
            "published_failed": published_failed,
            "cache_identical_to_published": counts["identical"],
            "cache_differs_from_published": counts["differs"],
            "no_published_record": counts["no_record"],
            "forecast_h1_differs_from_published": counts["forecast_h1_differs"]})
    write_csv(args.out / "audit" / "chains.csv", chains)
    write_csv(args.out / "audit" / "origins.csv", origin_rows)
    result = {"chains": len(chains),
              "chains_where_rules_differ": [c["task"] for c in chains if c["rules_differ"]],
              "live_complete": [c["task"] for c in chains if c["live_complete_and_covering"]]}
    tb.write_json_atomic(args.out / "audit" / "audit.json", result)
    return result


# -- stage: candidate --------------------------------------------------------------------

class ReadOnlyView:
    """The original cache as the pinned FitCache sees it, refusing every write."""

    def __init__(self, fits: Path):
        from thesis.core.cache import FitCache
        self._cache = FitCache(fits, enabled=True)
        self.enabled, self.directory = True, self._cache.directory

    def path_for(self, key):
        return self._cache.path_for(key)

    def get(self, key):
        return self._cache.get(key)

    def put(self, key, payload):
        raise tb.TierBError("read-only view of the ORIGINAL cache: write refused")


def candidate(args, jobs, identity, config) -> dict:
    from thesis.correction import guard
    from thesis.forecasting import rolling
    task = args.candidate_task
    job = jobs[task]
    rows, summary = walk_both(job, args.cache_fits, identity, config)
    out = args.out / "candidate"
    out.mkdir(parents=True, exist_ok=True)
    live = summary["live"]
    uncovered = [r for r in rows if not r["covers_horizons"]]
    if live["stop"] is not None or live["completed"] != live["planned"] or uncovered:
        result = {"task": task, "available": False, "live_completed": live["completed"],
                  "planned": live["planned"], "stop": live["stop"],
                  "origins_not_covering_horizons": [
                      {"refit_date": r["refit_date"], "payload_horizons": r["payload_horizons"]}
                      for r in uncovered],
                  "minimal_additional_computation": (
                      "for each listed origin: the fitted model's forecasts at the missing "
                      "horizons (or, for an absent key, the fit itself), which requires "
                      "authorised estimation or authorised forecast reconstruction")}
        tb.write_json_atomic(out / "candidate.json", result)
        return result

    class LiveReadOnly(tb.live_replay_class(ReadOnlyView)):
        pass
    cache = LiveReadOnly(args.cache_fits)
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
        raise tb.TierBError(f"candidate replay estimated {calls['n']} times")
    chain.forecasts.to_parquet(out / "candidate_forecasts.parquet", index=False)
    records = [{"refit_date": r.refit_date, "status": r.status.value,
                "reason_codes": ";".join(c.value for c in r.reason_codes), "loglik": r.loglik,
                "start_used": r.start_used, "params": json.dumps(r.params, sort_keys=True)}
               for r in chain.fit_records]
    write_csv(out / "candidate_fit_records.csv", records)
    result = {"task": task, "available": True, "origins": chain.attempted,
              "from_cache": chain.from_cache, "estimations": calls["n"],
              "valid": chain.valid, "failed": chain.failed,
              "forecast_rows": len(chain.forecasts),
              "forecasts_sha256": tb.sha256_file(out / "candidate_forecasts.parquet")}
    tb.write_json_atomic(out / "candidate.json", result)
    return result


# -- stage: impact -----------------------------------------------------------------------

def impact(args, jobs) -> dict:
    import pandas as pd
    from thesis.correction import workflow
    from thesis.correction.compare import compare_trees
    cand = args.out / "candidate"
    info = json.loads((cand / "candidate.json").read_text())
    if not info.get("available"):
        result = {"performed": False, "reason": "no complete candidate chain"}
        tb.write_json_atomic(args.out / "impact" / "impact.json", result)
        return result
    job = jobs[args.candidate_task]
    series, model = job.series_name, job.spec.model
    out = args.out / "impact"
    staging_input = out / "candidate_input"
    if staging_input.exists():
        shutil.rmtree(staging_input)
    shutil.copytree(args.original, staging_input)
    published = pd.read_parquet(Path(args.original) / "forecasts" / f"forecasts_{series}.parquet")
    new = pd.read_parquet(cand / "candidate_forecasts.parquet")
    provenance = [c for c in published.columns if c not in new.columns]
    template = published[published["model"] == model].iloc[0]
    for column in provenance:
        new[column] = template[column]
    new = new[published.columns]
    replaced = pd.concat([published[published["model"] != model], new], ignore_index=True)
    replaced = replaced.sort_values(["model", "origin_date", "horizon"]).reset_index(drop=True)
    replaced.to_parquet(staging_input / "forecasts" / f"forecasts_{series}.parquet", index=False)
    replaced.to_csv(staging_input / "forecasts" / f"forecasts_{series}.csv", index=False)
    audit_path = staging_input / "forecasts" / "forecast_origin_audit.csv"
    audit_table = pd.read_csv(audit_path)
    mask = (audit_table["series"] == series) & (audit_table["model"] == model)
    before = audit_table.loc[mask, ["attempted_origins", "valid_origins", "failed_origins"]].to_dict("records")
    audit_table.loc[mask, "valid_origins"] = info["valid"]
    audit_table.loc[mask, "failed_origins"] = info["failed"]
    audit_table.to_csv(audit_path, index=False)
    cache_root = Path(args.cache_fits).parent if args.impact_with_cache else None
    runs = {}
    with tb.no_estimation_allowed():
        for name, source in (("reference", Path(args.original)), ("candidate", staging_input)):
            started = time.time()
            summary = workflow.run(source, out / name, legacy=True, cache_root=cache_root)
            if summary.get("estimations_performed"):
                raise tb.TierBError(f"{name}: estimations performed {summary['estimations_performed']}")
            runs[name] = {"seconds": round(time.time() - started, 1),
                          "files": len(summary["regenerated_files"]),
                          "chain_sources": {k: len(v) for k, v in summary["chain_sources"].items()}}
    files = sorted(set(json.loads((out / "reference" / "r1_summary.json").read_text())["regenerated_files"])
                   - workflow.WORKFLOW_FILES)
    reproduction = compare_trees(Path(args.original), out / "reference", files=files)
    effect = compare_trees(out / "reference", out / "candidate", files=files)
    reproduction.to_csv(out / "reference_vs_published.csv", index=False)
    effect.to_csv(out / "candidate_vs_reference.csv", index=False)
    cells = []
    for path in effect[effect["status"] != "identical"]["path"]:
        if not path.endswith(".csv"):
            continue
        a = pd.read_csv(out / "reference" / path)
        b = pd.read_csv(out / "candidate" / path)
        if list(a.columns) != list(b.columns) or len(a) != len(b):
            cells.append({"path": path, "row": "", "column": "", "reference": f"shape {a.shape}",
                          "candidate": f"shape {b.shape}"})
            continue
        for column in a.columns:
            if column in ("run_id", "created_utc", "code_commit_sha"):
                continue
            for i in range(len(a)):
                x, y = a.at[i, column], b.at[i, column]
                if not (pd.isna(x) and pd.isna(y)) and x != y:
                    key = {k: a.at[i, k] for k in ("series", "model", "horizon", "model_a",
                                                   "model_b", "window_length") if k in a.columns}
                    cells.append({"path": path, "row": i, "column": column,
                                  "reference": x, "candidate": y,
                                  "row_key": json.dumps(key, default=str)})
    write_csv(out / "changed_cells.csv", cells)
    result = {"performed": True, "task": args.candidate_task, "runs": runs,
              "audit_row_before": before,
              "audit_row_after": {"valid_origins": info["valid"], "failed_origins": info["failed"]},
              "reference_reproduces_published": {
                  s: int((reproduction["status"] == s).sum()) for s in reproduction["status"].unique()},
              "files_compared": len(files),
              "files_changed_by_candidate": sorted(effect[effect["status"] != "identical"]["path"]),
              "changed_cells": len(cells)}
    tb.write_json_atomic(out / "impact.json", result)
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cache-fits", type=Path, required=True)
    parser.add_argument("--code-dir", type=Path, required=True)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--chain-sources", type=Path)
    parser.add_argument("--candidate-task", default="forecasting:UNRATE|MSAR")
    parser.add_argument("--impact-with-cache", action="store_true",
                        help="give the workflow the original cache (as the Tier A replay)")
    parser.add_argument("--stage", choices=STAGES + ("all",), default="all")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    tb.use_scientific_code(args.code_dir)
    stages = STAGES if args.stage == "all" else (args.stage,)
    report = {"estimation": "none (refused)", "scientific_commit": tb.SCIENTIFIC_PIN,
              "started_utc": tb.utc_stamp()}
    if "verify" in stages:
        report["verify"] = verify(args)
        print(json.dumps(report["verify"], indent=1, default=str))
    if set(stages) & {"audit", "candidate", "impact"}:
        import pandas as pd
        from thesis.correction import guard
        with guard.estimation_forbidden(), tb.no_estimation_allowed():
            jobs, identity, config = tb.build_jobs(args.original, args.code_dir)
        if "audit" in stages:
            fit_records = pd.read_parquet(Path(args.original) / "models" / "fit_records.parquet")
            report["audit"] = audit(args, jobs, identity, config, fit_records)
            print(json.dumps(report["audit"], indent=1, default=str))
        if "candidate" in stages:
            report["candidate"] = candidate(args, jobs, identity, config)
            print(json.dumps(report["candidate"], indent=1, default=str))
        if "impact" in stages:
            report["impact"] = impact(args, jobs)
            print(json.dumps({k: v for k, v in report["impact"].items()
                              if k != "files_changed_by_candidate"}, indent=1, default=str))
    report["finished_utc"] = tb.utc_stamp()
    tb.write_json_atomic(args.out / f"report-{args.stage}.json", report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
