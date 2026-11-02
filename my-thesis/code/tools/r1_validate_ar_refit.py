#!/usr/bin/env python3
"""R1 Tier A validation: re-estimated AR chains reproduce the original estimates.

Two checks, both with every correction switched off (legacy mode) and estimation allowed
only inside this tool's explicit blocks:

1. Baseline AR chains (all targets): re-estimate each published baseline AR chain and
   compare every forecast with the published `forecasts_<series>.parquet`. This shows the
   AR estimator reproduces the original run on this machine. These refits are
   validation only; they never enter a release.
2. Tier A chains (`--task` ...): re-estimate each and compare, origin by origin, with
   every original fit-cache payload that exists for the same exact key (AR keys carry no
   warm start, so they are exact even when other origins of the chain are missing).

Writes <out>/ar_refit_validation.json. Exit status 1 if any compared forecast differs by
more than 1e-9 relative (the R1 floating-point tolerance).

Usage (from my-thesis/code):
  python tools/r1_validate_ar_refit.py --original ../output --cache-root /content/r1_cache \\
         --task "T4.2:CPIAUCSL|AR(p=1)" ... --out /content/r1_tier_a
  python tools/r1_validate_ar_refit.py ... --dry-run     # list what would be estimated
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from thesis.core.config import load_config  # noqa: E402
from thesis.core.paths import CONFIG_DIR, FROZEN_DIR, Namespace, OutputLayout  # noqa: E402
from thesis.core.provenance import RunContext, git_commit_sha  # noqa: E402
from thesis.correction import flags, guard  # noqa: E402
from thesis.correction.rescore import REFIT_MARKER, PublishedRescorer  # noqa: E402
from thesis.data.store import load_bundle  # noqa: E402
from thesis.forecasting import rolling  # noqa: E402
from thesis.forecasting.windows import estimation_origins  # noqa: E402
from thesis.models.registry import AR  # noqa: E402

TOLERANCE = 1e-9


def _relative(a: np.ndarray, b: np.ndarray) -> float:
    both = np.isfinite(a) & np.isfinite(b)
    if (np.isfinite(a) != np.isfinite(b)).any():
        return float("inf")
    if not both.any():
        return 0.0
    scale = np.maximum(np.maximum(np.abs(a[both]), np.abs(b[both])), 1e-300)
    return float(np.max(np.abs(a[both] - b[both]) / scale))


def _refit(rescorer, job):
    with guard.allowed():
        return rolling.run_chain(job.series_name, job.y, job.spec, job.horizons,
                                 job.window_length, rescorer.config, frequency=job.frequency,
                                 transformation=job.transformation, identity=None, cache=None,
                                 max_origins=job.max_origins, task_id=job.task_id)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--cache-root", type=Path, default=None)
    parser.add_argument("--task", action="append", default=[], help="Tier A task id")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    config = load_config(names=("baseline", "series_catalog", "thresholds"),
                         config_dir=CONFIG_DIR)
    report = {"commit": git_commit_sha(), "baseline_ar": [], "tier_a": [], "ok": True}
    with guard.estimation_forbidden() as state, flags.legacy():
        bundle = load_bundle(FROZEN_DIR, config)
        context = RunContext(namespace=Namespace.CORRECTION, config_hash=config.hash,
                             data_snapshot_hash=bundle.data_input_identity)
        scratch = Path(tempfile.mkdtemp(prefix="r1_ar_validation_"))
        layout = OutputLayout(root=scratch / "output",
                              cache=args.cache_root if args.cache_root else scratch / "cache")
        rescorer = PublishedRescorer(config, context, layout, bundle,
                                     original=args.original.resolve(),
                                     use_cache=args.cache_root is not None)
        layout.create()
        rescorer.prepare_data()
        rescorer.stationarity_stage()
        rescorer.load_specifications()
        jobs = {job.task_id: job for job, *_ in rescorer._rolling_jobs()}
        unknown = [t for t in args.task if t not in jobs]
        not_ar = [t for t in args.task if t in jobs and jobs[t].spec.model != AR]
        if unknown or not_ar:
            parser.error(f"not Tier A AR tasks: unknown {unknown}, not AR {not_ar}")
        baseline = [jobs[f"forecasting:{s}|AR"] for s in rescorer._selected_targets()]
        if args.dry_run:
            print(json.dumps({"would_estimate_baseline_ar": [j.task_id for j in baseline],
                              "would_estimate_tier_a": args.task}, indent=1))
            return 0

        # 1. baseline AR chains against the published forecasts
        for job in baseline:
            chain = _refit(rescorer, job)
            published = rescorer._forecasts(job.series_name)
            published = published[published["model"] == AR]
            key = ["origin_date", "horizon"]
            merged = chain.forecasts.merge(published[key + ["forecast", "status"]], on=key,
                                           suffixes=("_refit", "_published"))
            rel = _relative(merged["forecast_refit"].to_numpy(float),
                            merged["forecast_published"].to_numpy(float))
            row = {"task_id": job.task_id, "rows_compared": len(merged),
                   "rows_published": len(published),
                   "status_identical": bool((merged["status_refit"]
                                             == merged["status_published"]).all()),
                   "max_relative_difference": rel}
            row["ok"] = (row["rows_compared"] == row["rows_published"]
                         and row["status_identical"] and rel <= TOLERANCE)
            report["baseline_ar"].append(row)
            report["ok"] &= row["ok"]
            print(row, flush=True)

        # 2. Tier A chains against every original cache payload with the same key
        for task in args.task:
            job = jobs[task]
            chain = _refit(rescorer, job)
            compared, worst, rejected = 0, 0.0, 0
            if args.cache_root is not None:
                horizons = sorted(set(int(h) for h in job.horizons))
                for origin in estimation_origins(job.y.index, job.window_length, horizons,
                                                 max_origins=job.max_origins):
                    key = rolling._cache_key(rescorer.identity, job.series_name,
                                             job.transformation, job.spec, origin, "")
                    path = rescorer.cache.path_for(key)
                    if not path.exists():
                        continue
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    if REFIT_MARKER in payload:
                        rejected += 1
                        continue
                    mine = chain.forecasts[chain.forecasts["origin_date"]
                                           == origin.origin_date]
                    for _, r in mine.iterrows():
                        cached = payload["forecasts"].get(str(int(r["horizon"])))
                        if cached is None:
                            continue
                        compared += 1
                        worst = max(worst, _relative(np.array([r["forecast"]], float),
                                                     np.array([cached], float)))
            row = {"task_id": task, "origins": chain.attempted, "failed": chain.failed,
                   "forecasts_compared_with_original_cache": compared,
                   "refit_payloads_rejected": rejected,
                   "max_relative_difference": worst,
                   "ok": worst <= TOLERANCE}
            report["tier_a"].append(row)
            report["ok"] &= row["ok"]
            print(row, flush=True)
        report["estimations_performed"] = dict(state.permitted)
    (args.out / "ar_refit_validation.json").write_text(json.dumps(report, indent=2,
                                                                  default=str))
    print("AR refit validation:", "PASSED" if report["ok"] else "FAILED")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
