#!/usr/bin/env python3
"""Dry-run completeness check of a fit cache against the full rolling-chain plan.

Nothing is estimated and nothing under `output/` or the cache is changed. The tool
rebuilds the run's rolling-chain plan exactly as `run_all.py` would (same configuration,
frozen data, stationarity decisions and fixed specifications, through the same
`Pipeline` job builders), then walks every chain origin by origin with the rolling
engine's own cache-key function, reading the cache but never fitting:

* **hit** -- a payload exists for the key and covers the chain's horizons;
* **horizon_miss** -- a payload exists but for fewer horizons (the run would refit);
* **miss** -- no payload for the key (the run would refit);
* **unknown_after_miss** -- for warm-started models (MSAR, STAR) the key of every later
  origin includes a hash of the previous fit's parameters. After a miss that hash is
  unknown until the missing fit is re-estimated, so those origins are counted separately:
  they are served from the cache only if the refit reproduces the original fit bit for
  bit, which is not guaranteed on another machine (Part 8 correction plan, F6 finding).
  AR and ARMA carry no warm start, so their later keys stay exact.
* **gap** -- the window contains missing data (never fitted).

This is the completeness test the cache-identity check cannot give: identical identity
proves the cache is *compatible*, not that it is *complete*.

Usage (from `my-thesis/code`, after restoring the archives into a directory):

    python tools/cache_completeness.py --fits ../cache/fits --out completeness.json

Exit status: 0 when every planned origin is a hit or a data gap, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from thesis.core.config import load_config  # noqa: E402
from thesis.core.paths import CONFIG_DIR, FROZEN_DIR, Namespace, OutputLayout  # noqa: E402
from thesis.core.provenance import RunContext  # noqa: E402
from thesis.data.store import load_bundle  # noqa: E402
from thesis.forecasting.rolling import _cache_key, _covers  # noqa: E402
from thesis.forecasting.scheduler import cache_dependencies  # noqa: E402
from thesis.forecasting.windows import estimation_origins  # noqa: E402
from thesis.pipeline import Pipeline  # noqa: E402

WARM_MODELS = {"MSAR", "MSAR3", "STAR"}


def build_plan(fits: Path, smoke: bool = False):
    """The run's rolling jobs, built by the pipeline's own job builders (no fitting)."""
    names = ("baseline", "series_catalog", "thresholds") + (("smoke",) if smoke else ())
    config = load_config(names=names, config_dir=CONFIG_DIR)
    bundle = load_bundle(FROZEN_DIR, config)
    scratch = Path(tempfile.mkdtemp(prefix="completeness_"))
    # The pipeline's FitCache lives at <cache>/fits; point it at the directory checked.
    layout = OutputLayout(root=scratch / "output", cache=fits.parent)
    if fits.name != "fits":
        link = scratch / "cache" / "fits"
        link.parent.mkdir(parents=True)
        link.symlink_to(fits.resolve(), target_is_directory=True)
        layout = OutputLayout(root=scratch / "output", cache=link.parent)
    layout.create()
    context = RunContext(namespace=Namespace.SMOKE if smoke else Namespace.BASELINE,
                         config_hash=config.hash, data_snapshot_hash=bundle.data_input_identity,
                         data_cutoff=config.get("samples.monthly_end"),
                         vintage_date=config.get("run.vintage_date"))
    pipeline = Pipeline(config, context, layout, bundle, smoke=smoke, workers=1)
    pipeline.prepare_data()
    pipeline.stationarity_stage()
    pipeline.specification_stage(final=False)
    pipeline.nonlinearity_stage()
    pipeline.specification_stage()
    return pipeline, config


def walk(job, pipeline, config) -> dict:
    """Classify every origin of one chain without estimating anything."""
    cache, identity = pipeline.cache, pipeline.identity
    y = job.y
    horizons = sorted(set(int(h) for h in job.horizons))
    origins = estimation_origins(y.index, job.window_length, horizons,
                                 max_origins=job.max_origins)
    use_warm = bool(config.get("forecasting.warm_starts", True))
    counts: Counter = Counter()
    first_miss = None
    broken = False
    predecessor = ""
    for origin in origins:
        window = y.iloc[origin.estimation_slice()]
        if not np.isfinite(window.to_numpy(dtype=float)).all():
            counts["gap"] += 1
            continue
        if broken:
            counts["unknown_after_miss"] += 1
            continue
        key = _cache_key(identity, job.series_name, job.transformation, job.spec, origin,
                         predecessor)
        path = cache.path_for(key)
        payload = None
        if path.exists():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                payload = None
        if payload is not None and _covers(payload, horizons):
            counts["hit"] += 1
            warm = (np.asarray(payload["warm_payload"], dtype=float)
                    if payload.get("warm_payload") is not None else None)
        else:
            counts["horizon_miss" if payload is not None else "miss"] += 1
            first_miss = first_miss or origin.origin_date.strftime("%Y-%m-%d")
            if job.spec.model in WARM_MODELS and use_warm:
                broken = True          # the next key needs the refit's parameters
            warm = None
        predecessor = ""
        if use_warm and warm is not None:
            predecessor = f"{np.round(np.asarray(warm, float).ravel(), 10).tolist()}"
    return {"task_id": job.task_id, "series": job.series_name, "model": job.spec.model,
            "spec": job.spec.label, "window_length": job.window_length,
            "transformation": job.transformation, "horizons": horizons,
            "n_origins": len(origins), **{k: counts.get(k, 0) for k in
                                          ("hit", "miss", "horizon_miss",
                                           "unknown_after_miss", "gap")},
            "first_miss": first_miss}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fits", type=Path, required=True,
                        help="directory holding the restored fit payloads (<xx>/<digest>.json)")
    parser.add_argument("--out", type=Path, required=True, help="JSON report to write")
    parser.add_argument("--smoke", action="store_true", help="check a smoke-run cache")
    args = parser.parse_args(argv)
    if not args.fits.is_dir():
        parser.error(f"{args.fits} is not a directory")

    pipeline, config = build_plan(args.fits, smoke=args.smoke)
    jobs = [job for job, *_ in pipeline._rolling_jobs()]
    duplicates = cache_dependencies(jobs, True)
    chains = []
    for job in jobs:
        row = walk(job, pipeline, config)
        row["reads_cache_of"] = duplicates.get(job.task_id)
        chains.append(row)
        print(f"{row['task_id']:<45} origins {row['n_origins']:>4}  hit {row['hit']:>4}  "
              f"miss {row['miss'] + row['horizon_miss']:>4}  "
              f"unknown {row['unknown_after_miss']:>4}", flush=True)
    totals = Counter()
    for row in chains:
        for key in ("n_origins", "hit", "miss", "horizon_miss", "unknown_after_miss", "gap"):
            totals[key] += row[key]
    files = sum(1 for _ in args.fits.rglob("*.json"))
    report = {
        "fits_directory": str(args.fits),
        "payload_files_present": files,
        "code_hash": pipeline.identity.code_hash,
        "config_hash": pipeline.identity.config_hash,
        "data_hash": pipeline.identity.canonical_hash,
        "chains": len(chains),
        "totals": dict(totals),
        "complete": totals["hit"] + totals["gap"] == totals["n_origins"],
        "chains_with_misses": [r["task_id"] for r in chains
                               if r["miss"] or r["horizon_miss"] or r["unknown_after_miss"]],
        "per_chain": chains,
    }
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("payload_files_present", "chains", "totals",
                                             "complete")}, indent=2))
    return 0 if report["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
