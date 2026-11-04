#!/usr/bin/env python3
"""R1 Tier B worker: re-estimate ONE authorised chain (or only check, in preflight mode).

Runs under the approved environment with the pinned scientific code on its path
(`--code-dir` = the pinned checkout's `my-thesis/code`). The chain is estimated by the
pinned `rolling.run_chain` with exactly the arguments of the pinned approved path
(`correction/rescore.py`, `_chains`): same job, same config, same identity, the pinned
RefitCache semantics (marker, atomic write). Everything runs inside the pinned
`guard.estimation_forbidden()`; estimation is allowed only around that one call, and
only for a task of this worker's batch.

Modes
  preflight  build every job, walk the given refit caches, write a JSON report; no fit.
  run        estimate one task into its own refit cache until complete, stopped by the
             budget (exit 3, graceful) or failed (exit 1). Resumes automatically from
             the payloads already in that cache.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r1_tierb as tb  # noqa: E402


def preflight(args) -> int:
    jobs, identity, config = tb.build_jobs(args.original, args.code_dir)
    report = {"batch": args.batch, "tier_a": {}, "batch_chains": {}, "problems": []}
    frozen = Path(args.code_dir).parent / "data" / "frozen" / "thesis_input_2026-10-05.csv"
    report["cache_identity"] = tb.cache_identity_string(config, frozen)
    if report["cache_identity"] != tb.CACHE_IDENTITY:
        report["problems"].append(f"cache identity {report['cache_identity']}")
    if args.tier_a_fits:
        for task, (planned, failed) in tb.TIER_A_CHAINS.items():
            walk = tb.walk_chain(jobs[task], args.tier_a_fits, identity, config)
            walk_failed = walk["statuses"].get("failed", 0)
            report["tier_a"][task] = {k: walk[k] for k in ("planned", "completed", "complete",
                                                          "statuses")}
            if not walk["complete"] or walk["planned"] != planned or walk_failed != failed:
                report["problems"].append(f"Tier A {task}: {walk['completed']}/{planned} "
                                          f"origins, {walk_failed} failed (expected {failed})")
        reached = sum(report["tier_a"][t]["completed"] for t in tb.TIER_A_CHAINS)
        present = len(tb.payload_files(args.tier_a_fits))
        if reached != tb.TIER_A_PAYLOADS or present != tb.TIER_A_PAYLOADS:
            report["problems"].append(f"Tier A: {present} payloads, {reached} reached by the "
                                      f"eight chains, expected {tb.TIER_A_PAYLOADS}")
    for task in tb.batch_tasks(args.batch):
        planned = tb.TIER_B_CHAINS[task][0]
        fits = Path(args.batch_fits) / tb.slug(task) / "fits"
        fits.mkdir(parents=True, exist_ok=True)
        walk = tb.walk_chain(jobs[task], fits, identity, config)
        report["batch_chains"][task] = {k: walk[k] for k in
                                        ("planned", "completed", "complete", "first_missing",
                                         "statuses")}
        report["batch_chains"][task]["unreachable"] = len(walk["unreachable"])
        if walk["planned"] != planned:
            report["problems"].append(f"{task}: {walk['planned']} origins, expected {planned}")
        if walk["unreachable"]:
            report["problems"].append(f"{task}: {len(walk['unreachable'])} unreachable payloads")
        spec = jobs[task].spec
        if spec.model == "MSAR3" or (spec.model == "MSAR" and spec.k_regimes != 2):
            report["problems"].append(f"{task}: not a K=2 specification (Tier B has no K=3)")
    tb.write_json_atomic(args.report, report)
    print(json.dumps({k: report[k] for k in ("cache_identity", "problems")}, indent=1))
    return 0 if not report["problems"] else 1


def run(args) -> int:
    if args.task not in tb.batch_tasks(args.batch):
        raise tb.TierBError(f"{args.task} is not authorised for batch {args.batch}")
    jobs, identity, config = tb.build_jobs(args.original, args.code_dir)
    job = jobs[args.task]
    from thesis.correction import guard
    from thesis.forecasting import rolling

    fits = Path(args.batch_fits) / tb.slug(args.task) / "fits"
    budget = tb.Budget(args.start_epoch, args.budget_hours, args.reserve_minutes)
    cache = tb.stoppable_refit_cache(
        fits, task=args.task, budget=budget,
        historical_seconds=tb.TIER_B_CHAINS[args.task][1], stop_file=args.stop_file,
        progress=Path(args.batch_fits) / tb.slug(args.task) / "progress.jsonl")
    result = {"task": args.task, "batch": args.batch, "started_utc": tb.utc_stamp(),
              "outcome": None}
    began = time.time()
    with guard.estimation_forbidden() as state:
        try:
            with guard.allowed():
                chain = rolling.run_chain(
                    job.series_name, job.y, job.spec, job.horizons, job.window_length,
                    config, frequency=job.frequency, transformation=job.transformation,
                    identity=identity, cache=cache, max_origins=job.max_origins,
                    task_id=job.task_id)
            result.update(outcome="complete", origins=chain.attempted,
                          served_from_checkpoint=chain.from_cache, failed=chain.failed)
        except tb.GracefulStop as stop:
            result.update(outcome="stopped", reason=str(stop))
        result["estimations"] = dict(state.permitted)
    walk = tb.walk_chain(job, fits, identity, config)
    result.update(walk={k: walk[k] for k in ("planned", "completed", "complete", "statuses",
                                             "first_missing")},
                  unreachable=len(walk["unreachable"]),
                  seconds=round(time.time() - began, 1), finished_utc=tb.utc_stamp())
    tb.write_json_atomic(args.result, result)
    print(json.dumps(result, indent=1))
    if walk["unreachable"]:
        return 1
    return 0 if result["outcome"] == "complete" and walk["complete"] else 3


def certify(args) -> int:
    """Certify the batch from what is COMMITTED ON DRIVE (restored afresh), not local state."""
    import pandas as pd
    import tempfile
    jobs, identity, config = tb.build_jobs(args.original, args.code_dir)
    root = tb.batch_root(args.drive_root, args.batch)
    fit_records = pd.read_parquet(Path(args.original) / "models" / "fit_records.parquet",
                                  columns=["series", "model", "window_start", "window_end",
                                           "refit_date", "params", "loglik", "status"])
    walks, checkpoints, agreements, problems = {}, {}, {}, []
    with tempfile.TemporaryDirectory() as scratch:
        for task in tb.batch_tasks(args.batch):
            task_dir = root / "checkpoints" / tb.slug(task)
            fits = Path(scratch) / tb.slug(task) / "fits"
            tb.restore_checkpoints(task_dir, fits)
            walk = tb.walk_chain(jobs[task], fits, identity, config)
            walks[task] = walk
            checkpoints[task] = [{"checkpoint_id": m["checkpoint_id"],
                                  "archive_sha256": m["archive_sha256"],
                                  "payloads": len(m["members"])}
                                 for _, m in tb.committed_checkpoints(task_dir)]
            if not walk["complete"] or walk["unreachable"]:
                problems.append(f"{task}: {walk['completed']}/{walk['planned']} committed, "
                                f"{len(walk['unreachable'])} unreachable")
                continue
            agreements[task] = tb.agreement(task, jobs[task], walk, fits, fit_records)
    sessions, estimations = [], {}
    for summary in sorted((root / "sessions").glob("*/session_summary.json")):
        data = json.loads(summary.read_text(encoding="utf-8"))
        sessions.append({k: data.get(k) for k in ("session", "started_utc", "finished_utc",
                                                  "elapsed_hours", "outcomes")})
        for task, counts in (data.get("estimations") or {}).items():
            for name, n in counts.items():
                estimations.setdefault(task, {}).setdefault(name, 0)
                estimations[task][name] += n
    report = {"batch": args.batch, "complete": not problems, "problems": problems,
              "walks": {t: {k: w[k] for k in ("planned", "completed", "complete", "statuses",
                                              "first_missing")} for t, w in walks.items()},
              "agreement": {t: {k: v for k, v in a.items() if k != "rows"}
                            for t, a in agreements.items()}}
    tb.write_json_atomic(args.report, report)
    if problems:
        print(json.dumps(report, indent=1))
        print("NOT COMPLETE: no certificate written")
        return 3
    provenance = json.loads(Path(args.provenance).read_text(encoding="utf-8"))
    agreement_summary = {"warnings": [w for a in agreements.values() for w in a["warnings"]],
                         "requires_review": sorted(t for t, a in agreements.items()
                                                   if a["requires_review"]),
                         "chains": report["agreement"]}
    cert = tb.certificate(args.batch, walks, checkpoints, provenance=provenance,
                          sessions=sessions, estimations=estimations,
                          agreement=agreement_summary)
    target = root / "certificates" / f"COMPLETE-{tb.utc_stamp()}-{args.session}.json"
    tb.assert_writable_path(target, args.drive_root, args.batch)
    tb.write_json_atomic(target, cert)
    rows = Path(args.report).with_name(f"agreement_{args.batch}.csv")
    pd.DataFrame([dict(task=t, **r) for t, a in agreements.items() for r in a["rows"]]) \
        .to_csv(rows, index=False)
    shutil_copy(rows, root / "certificates" / f"agreement-{args.session}.csv")
    print(json.dumps({k: cert[k] for k in ("batch", "complete", "expected_origins",
                                           "completed_origins", "warnings")}, indent=1))
    print("certificate:", target)
    return 0


def shutil_copy(source: Path, target: Path) -> None:
    import shutil
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    shutil.copyfile(source, temporary)
    temporary.replace(target)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=("preflight", "run", "certify"))
    parser.add_argument("--batch", required=True, choices=sorted(tb.BATCHES))
    parser.add_argument("--code-dir", type=Path, required=True)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--batch-fits", type=Path, required=True)
    parser.add_argument("--tier-a-fits", type=Path, default=None)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--task")
    parser.add_argument("--start-epoch", type=float)
    parser.add_argument("--budget-hours", type=float)
    parser.add_argument("--reserve-minutes", type=float, default=30.0)
    parser.add_argument("--stop-file", type=Path)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--drive-root", type=Path)
    parser.add_argument("--session")
    parser.add_argument("--provenance", type=Path)
    args = parser.parse_args(argv)
    tb.use_scientific_code(args.code_dir)
    return {"preflight": preflight, "run": run, "certify": certify}[args.mode](args)


if __name__ == "__main__":
    raise SystemExit(main())
