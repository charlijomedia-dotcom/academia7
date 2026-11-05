#!/usr/bin/env python3
"""R1 Tier B: warm-start continuity check of committed checkpoints (read-only, no estimation).

For every chain of one batch: verify and restore its committed checkpoints (completion
marker, manifest, archive and member sha256) into a LOCAL work folder; walk the chain by
the pinned LIVE warm-start rule and by the cache-hit rule, reporting the exact first
mismatch (keys, preceding statuses, stored warm payloads, live warm state); replay the
committed prefix through the pinned `rolling.run_chain` with the live-replay cache and
estimation refused (any estimator call raises), confirming every origin is served from
the checkpoints with records equal to the stored payloads and no payload changed; and
compare with the original fit records (G7 agreement, including the failed-fit counts).

Nothing on Drive is written: checkpoints are only read; everything else goes to --work
and --report. Usage (in a batch notebook, after the restore cell):

    python r1_tierb_continuity_check.py --batch B2 --drive-root DRIVE_ROOT \
        --code-dir <pinned>/my-thesis/code --original <original output> \
        --work /content/continuity --report /content/continuity/B2.json
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r1_tierb as tb  # noqa: E402

parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--batch", required=True, choices=sorted(tb.BATCHES))
parser.add_argument("--drive-root", type=Path, help="DRIVE_ROOT of the batch notebooks")
parser.add_argument("--batch-root", type=Path, help="or the batch folder itself")
parser.add_argument("--code-dir", type=Path, required=True, help="pinned my-thesis/code")
parser.add_argument("--original", type=Path, required=True, help="original output/")
parser.add_argument("--work", type=Path, required=True, help="local scratch (not Drive)")
parser.add_argument("--report", type=Path, required=True)
args = parser.parse_args()
batch = args.batch
batch_root = args.batch_root or tb.batch_root(args.drive_root, batch)
work = args.work
tb.use_scientific_code(args.code_dir)
from thesis.correction import guard  # noqa: E402
from thesis.forecasting import rolling  # noqa: E402

jobs, identity, config = tb.build_jobs(args.original, args.code_dir)
import pandas as pd  # noqa: E402
fit_records = pd.read_parquet(Path(args.original) / "models" / "fit_records.parquet")
report = {"batch": batch, "batch_root": str(batch_root), "created_utc": tb.utc_stamp(),
          "estimation": "none (refused by the guard)", "chains": {}}
for task_dir in sorted(p for p in (batch_root / "checkpoints").iterdir() if p.is_dir()):
    task = next(t for t in tb.batch_tasks(batch) if tb.slug(t) == task_dir.name)
    job = jobs[task]
    history = tb.committed_checkpoints(task_dir)          # marker + manifest + archive sha
    fits = work / "restored" / task_dir.name / "fits"
    if fits.exists():
        shutil.rmtree(fits)
    restored = tb.restore_checkpoints(task_dir, fits)     # every member sha256
    entry = {"checkpoints": len(history), "restored": restored,
             "sessions": sorted({m["session"] for _, m in history}),
             "continuity": tb.continuity_report(job, fits, identity, config)}
    live = tb.walk_chain(job, fits, identity, config)
    n = live["completed"]
    # replay exactly the committed prefix: max_origins keeps the LAST origins, so for a
    # partial chain shorten the series to end at the first missing origin's target
    from thesis.forecasting.windows import estimation_origins
    horizons = sorted(set(int(h) for h in job.horizons))
    all_origins = estimation_origins(job.y.index, job.window_length, horizons,
                                     max_origins=job.max_origins)
    y = job.y
    if n < len(all_origins):
        # origins run from position window_length-1 to len(y)-min(h)-1 (windows.py)
        y = job.y.iloc[: int(job.window_length) - 1 + n + min(horizons)]
        prefix = estimation_origins(y.index, job.window_length, horizons)
        assert [o.origin_date for o in prefix] == [o.origin_date for o in all_origins[:n]] and \
            [(o.window_start, o.window_end) for o in prefix] == \
            [(o.window_start, o.window_end) for o in all_origins[:n]], "prefix origins differ"
    # 2. replay through the pinned engine, estimation forbidden, live-replay layer
    calls = {"n": 0}
    real = rolling.fit_and_forecast

    def counting(*a, **k):
        calls["n"] += 1
        return real(*a, **k)
    rolling.fit_and_forecast = counting
    try:
        before = {p: tb.sha256_file(p) for p in tb.payload_files(fits)}
        with guard.estimation_forbidden(), tb.no_estimation_allowed(), guard.allowed():
            chain = rolling.run_chain(job.series_name, y, job.spec, job.horizons,
                                      job.window_length, config, frequency=job.frequency,
                                      transformation=job.transformation, identity=identity,
                                      cache=tb.live_replay_class()(fits),
                                      max_origins=job.max_origins, task_id=job.task_id)
        unchanged = before == {p: tb.sha256_file(p) for p in tb.payload_files(fits)}
        # served records equal the stored payloads, origin by origin
        mismatched = []
        for record, (date, rel) in zip(chain.fit_records, live["sequence"]):
            p = json.loads((fits / rel).read_text())
            if (record.status.value != p["status"] or record.params != p["params"]
                    or [c.value for c in record.reason_codes] != p["reason_codes"]
                    or record.refit_date != date):
                mismatched.append(date)
        entry["replay"] = {"origins": n, "from_cache": chain.from_cache,
                           "estimations": calls["n"], "failed": chain.failed,
                           "valid": chain.valid, "payloads_unchanged": unchanged,
                           "records_differing_from_payloads": mismatched}
    finally:
        rolling.fit_and_forecast = real
    # 3. agreement with the original records (origins re-estimated so far)
    agreement = tb.agreement(task, job, live, fits, fit_records)
    entry["agreement"] = {k: v for k, v in agreement.items() if k != "rows"}
    original = tb.original_chain_records(fit_records, task, job)
    dates = [d for d, _ in live["sequence"]]
    entry["original_failed_over_same_origins"] = sum(
        1 for d in dates if d in original and original[d].status == "failed")
    entry["original_failed_whole_chain"] = sum(1 for r in original.values() if r.status == "failed")
    changed = [r for r in agreement["rows"] if r.get("category") == "classification_changed"]
    entry["classification_changes"] = [
        {k: r.get(k) for k in ("refit_date", "status_original", "status_new",
                               "reason_codes_original", "reason_codes_new")} for r in changed]
    report["chains"][task] = entry
Path(args.report).parent.mkdir(parents=True, exist_ok=True)
Path(args.report).write_text(json.dumps(report, indent=1, default=str))
print(json.dumps({t: {"checkpoints": e["checkpoints"], "payloads": e["restored"]["payloads"],
                      "live": e["continuity"]["live"], "cache_hit": e["continuity"]["cache_hit"],
                      "replay": e["replay"]} for t, e in report["chains"].items()},
                 indent=1, default=str))
