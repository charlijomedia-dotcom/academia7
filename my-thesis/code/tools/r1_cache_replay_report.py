#!/usr/bin/env python3
"""R1: which pending chains can be replayed whole from the restored original fit cache.

Reads the cache only. Nothing is estimated: the whole run executes under
`guard.estimation_forbidden()`, and the replay check additionally refuses estimation at
the rolling engine, so a cache miss makes a chain "not replayable", never a refit.

For each of the 20 pending chains (r1_validation_report.md §4) it reports the planned
origins, hits, misses, warm-start-dependent unknown origins, whether the real rolling
engine replays the whole chain, and the residual estimation workload if it does not
(cost per fit = the original run's mean wall time for that target and model).

Usage (from my-thesis/code; --cache-root is the directory that holds `fits/`):

  python tools/r1_cache_replay_report.py --original ../output \\
         --cache-root /content/r1_cache --out /content/r1_replay_report

Writes <out>/replay_report.json and <out>/replay_report.csv. Exit status 0 always when
the check ran (completeness is reported, not enforced); 2 on an identity mismatch.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

from thesis.core.config import load_config  # noqa: E402
from thesis.core.paths import CONFIG_DIR, FROZEN_DIR, Namespace, OutputLayout  # noqa: E402
from thesis.core.provenance import RunContext, git_commit_sha, git_dirty_paths  # noqa: E402
from thesis.correction import guard  # noqa: E402
from thesis.correction.replay import (WARM_MODELS, classify_chain, identity_string,  # noqa: E402
                                      pending_reason, verify_replay)
from thesis.correction.rescore import PublishedRescorer  # noqa: E402
from thesis.data.store import load_bundle  # noqa: E402

EXPECTED_IDENTITY = "3413465b508bb844"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--cache-root", type=Path, required=True,
                        help="directory holding the restored fits/ tree (read only)")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--all", action="store_true",
                        help="also assess the non-published chains no correction affects")
    parser.add_argument("--expected-identity", default=EXPECTED_IDENTITY)
    args = parser.parse_args(argv)
    fits = args.cache_root / "fits"
    if not fits.is_dir():
        parser.error(f"{fits} is not a directory")
    args.out.mkdir(parents=True, exist_ok=True)

    config = load_config(names=("baseline", "series_catalog", "thresholds"),
                         config_dir=CONFIG_DIR)
    identity = identity_string(config)
    if identity != args.expected_identity:
        print(f"IDENTITY MISMATCH: this checkout gives {identity}, the cache is "
              f"{args.expected_identity}. Nothing was checked.", file=sys.stderr)
        return 2
    payloads = sum(1 for _ in fits.rglob("*.json"))

    with guard.estimation_forbidden() as state:
        bundle = load_bundle(FROZEN_DIR, config)
        context = RunContext(namespace=Namespace.CORRECTION, config_hash=config.hash,
                             data_snapshot_hash=bundle.data_input_identity)
        scratch = Path(tempfile.mkdtemp(prefix="r1_replay_report_"))
        layout = OutputLayout(root=scratch / "output", cache=args.cache_root)
        rescorer = PublishedRescorer(config, context, layout, bundle,
                                     original=args.original.resolve(), use_cache=True)
        layout.create()
        rescorer.prepare_data()
        rescorer.stationarity_stage()
        rescorer.load_specifications()
        rescorer.load_baseline_chains()

        fit_records = pd.read_parquet(args.original / "models" / "fit_records.parquet",
                                      columns=["series", "model", "wall_seconds"])
        per_fit = fit_records.groupby(["series", "model"])["wall_seconds"].mean()

        rows = []
        for job, _batch, stage, exercise, _role in rescorer._rolling_jobs():
            if stage != "robustness" or rescorer._baseline_equivalent(job) is not None:
                continue                      # published: needs neither cache nor refit
            reason = pending_reason(job.task_id)
            if reason is None and not args.all:
                continue
            assessment = classify_chain(job, rescorer.cache, rescorer.identity, config)
            replayed, served = (verify_replay(rescorer, job) if assessment.complete
                                else (False, 0))
            row = assessment.as_dict()
            seconds = float(per_fit.get((job.series_name, job.spec.model), float("nan")))
            fitted = row["planned_origins"] - row["gap"]
            row.update({
                "exercise": exercise, "pending": reason is not None,
                "pending_reason": reason or "unaffected by F1-F4/F7.1",
                "warm_started": job.spec.model in WARM_MODELS,
                "replay_verified": replayed, "origins_served_by_replay": served,
                # The approved rule: an incomplete chain is re-estimated whole.
                "origins_to_estimate_whole_chain": 0 if replayed else fitted,
                # Information only (not approved): exact-key misses alone, AR/ARMA.
                "origins_missing_exact_keys": (row["missing_origins"]
                                               if job.spec.model not in WARM_MODELS
                                               else None),
                "mean_seconds_per_fit": seconds,
            })
            row["cpu_hours_residual"] = row["origins_to_estimate_whole_chain"] * seconds / 3600
            rows.append(row)
            print(f"{row['task_id']:<28} planned {row['planned_origins']:>4} "
                  f"hit {row['hit']:>4} miss {row['missing_origins']:>4} "
                  f"unknown {row['unknown_after_miss']:>4} "
                  f"replay {'YES' if replayed else 'no ':<3} "
                  f"to-estimate {row['origins_to_estimate_whole_chain']:>4} "
                  f"cpu-h {row['cpu_hours_residual']:.2f}", flush=True)
        estimations = dict(state.permitted)

    table = pd.DataFrame(rows)
    pending = table[table["pending"]]
    residual = pending[~pending["replay_verified"]]
    report = {
        "checkout_commit": git_commit_sha(),
        "uncommitted_paths": list(git_dirty_paths() or ()),
        "cache_identity": identity,
        "payload_files_present": payloads,
        "estimations_performed": estimations or "none",
        "pending_chains": len(pending),
        "pending_replayed_whole": int(pending["replay_verified"].sum()),
        "pending_requiring_estimation": len(residual),
        "residual_origins": int(residual["origins_to_estimate_whole_chain"].sum()),
        "residual_cpu_hours": float(residual["cpu_hours_residual"].sum()),
        "longest_residual_chain_hours": float(residual["cpu_hours_residual"].max()
                                              if len(residual) else 0.0),
        "residual_by_model": residual.groupby("model")["cpu_hours_residual"].sum()
                                     .round(3).to_dict(),
        "tier_a_ar_chains_to_estimate": residual.loc[residual["model"] == "AR",
                                                     "task_id"].tolist(),
        "tier_b_chains_to_estimate": residual.loc[residual["model"] != "AR",
                                                  "task_id"].tolist(),
        "per_chain": rows,
    }
    (args.out / "replay_report.json").write_text(json.dumps(report, indent=2, default=str),
                                                 encoding="utf-8")
    table.to_csv(args.out / "replay_report.csv", index=False)
    print(json.dumps({k: v for k, v in report.items() if k != "per_chain"}, indent=1,
                     default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
