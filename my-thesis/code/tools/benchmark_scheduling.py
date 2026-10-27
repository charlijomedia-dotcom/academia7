#!/usr/bin/env python3
"""Measure the shared-pool scheduler against the previous one-pool-per-batch design.

Runs the real rolling workload of the run (every baseline, rolling K=3, T4.1, T4.2 and
T4.8 chain, on all six frozen series and the approved windows, horizons and
specifications) twice from a cold cache, with the same number of workers:

* **per-batch** — the previous design: each `_chains` call (one series' five chains, one
  T4.1/T4.2/T4.8 batch) gets its own pool, and the next starts when it is done;
* **pooled** — every chain on one shared pool (`forecasting.scheduler`).

The number of origins per chain is capped (`--max-origins`) so both arms finish in
reasonable time; the cap applies identically to both. Every chain result of the two arms
is compared exactly, and wall time and worker utilization (busy chain-seconds divided by
wall time x workers) are reported. Usage:

    python tools/benchmark_scheduling.py --max-origins 6 --workers 4 --out results.json
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import pandas as pd  # noqa: E402

from thesis.core.cache import FitCache  # noqa: E402
from thesis.core.config import load_config  # noqa: E402
from thesis.core.paths import CONFIG_DIR, FROZEN_DIR, Namespace, output_layout  # noqa: E402
from thesis.core.provenance import RunContext  # noqa: E402
from thesis.data.store import load_bundle  # noqa: E402
from thesis.forecasting.parallel import run_chains  # noqa: E402
from thesis.forecasting.scheduler import ChainScheduler  # noqa: E402
from thesis.monitoring import Monitor  # noqa: E402
from thesis.pipeline import Pipeline  # noqa: E402


def prepared_pipeline(max_origins: int, root: Path) -> Pipeline:
    config = load_config(names=("baseline", "series_catalog", "thresholds"),
                         config_dir=CONFIG_DIR).with_overrides(
        {"smoke": {"max_origins": max_origins}}, "scheduling-benchmark")
    bundle = load_bundle(FROZEN_DIR, config)
    layout = type(output_layout(Namespace.SMOKE))(root=root / "out", cache=root / "cache")
    context = RunContext(namespace=Namespace.SMOKE, config_hash=config.hash,
                         data_snapshot_hash=bundle.data_input_identity,
                         data_cutoff=config.get("samples.monthly_end"),
                         vintage_date=config.get("run.vintage_date"))
    pipeline = Pipeline(config, context, layout, bundle, smoke=True)
    layout.create()
    pipeline.prepare_data()
    pipeline.stationarity_stage()
    pipeline.specification_stage(final=False)
    pipeline.nonlinearity_stage()
    pipeline.specification_stage()
    return pipeline


def batches(pipeline: Pipeline) -> list[list]:
    """The jobs grouped exactly as the stages group them into `_chains` calls."""
    groups: dict[str, list] = {}
    for job, batch, *_ in pipeline._rolling_jobs():
        groups.setdefault(batch, []).append(job)
    return list(groups.values())


def chain_seconds(monitor: Monitor) -> dict[str, float]:
    starts, ends = {}, {}
    for line in monitor.paths["events"].read_text().splitlines():
        event = json.loads(line)
        if event["kind"] == "chain_start":
            starts[event["task_id"]] = event["t"]
        elif event["kind"] == "chain_end":
            ends[event["task_id"]] = event["t"]
    return {task: ends[task] - starts[task] for task in starts if task in ends}


def run_arm(name: str, pipeline: Pipeline, groups: list[list], workers: int,
            root: Path) -> tuple[dict, dict]:
    cache = FitCache(root / f"cache-{name}", enabled=True)
    monitor = Monitor(root / f"logs-{name}" / name, run_id=name, namespace="smoke",
                      workers=workers, stream=io.StringIO(), heartbeat_seconds=3600,
                      summary_seconds=3600).start()
    began = time.time()
    results = []
    if name == "pooled":
        scheduler = ChainScheduler(pipeline.config, pipeline.identity, cache, workers=workers,
                                   monitor=monitor).start([j for g in groups for j in g])
        for group in groups:
            results.extend(zip([j.task_id for j in group], scheduler.results(group)))
        scheduler.close()
    else:
        for group in groups:
            out = run_chains(group, pipeline.config, pipeline.identity, cache,
                             workers=workers, monitor=monitor)
            results.extend(zip([j.task_id for j in group], out))
    wall = time.time() - began
    monitor.close()
    busy = chain_seconds(monitor)
    by_model: dict[str, float] = {}
    for task, seconds in busy.items():
        model = task.split("|")[1].split(":")[-1]
        by_model[model] = by_model.get(model, 0.0) + seconds
    summary = {"arm": name, "workers": workers, "wall_seconds": round(wall, 1),
               "busy_chain_seconds": round(sum(busy.values()), 1),
               "utilization": round(sum(busy.values()) / (wall * workers), 4),
               "busy_seconds_by_model": {k: round(v, 1) for k, v in sorted(by_model.items())},
               "chains": len(results)}
    return summary, dict(results)


def compare(a: dict, b: dict) -> list[str]:
    problems = []
    for task in a:
        (tag_a, ra), (tag_b, rb) = a[task], b[task]
        try:
            pd.testing.assert_frame_equal(ra.forecasts, rb.forecasts)
        except AssertionError as exc:
            problems.append(f"{task}: forecasts differ: {str(exc)[:120]}")
        if ra.counts() != rb.counts():
            problems.append(f"{task}: counts {ra.counts()} vs {rb.counts()}")
        if [r.params for r in ra.fit_records] != [r.params for r in rb.fit_records]:
            problems.append(f"{task}: fitted parameters differ")
        if [r.status for r in ra.fit_records] != [r.status for r in rb.fit_records]:
            problems.append(f"{task}: statuses differ")
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--max-origins", type=int, default=6)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)

    root = Path(tempfile.mkdtemp(prefix="sched-bench-"))
    began = time.time()
    pipeline = prepared_pipeline(args.max_origins, root)
    groups = batches(pipeline)
    print(f"stages 1-5 prepared in {time.time() - began:.0f}s; {len(groups)} batches, "
          f"{sum(len(g) for g in groups)} chains", flush=True)
    summaries, results = [], {}
    for name in ("per-batch", "pooled"):
        summary, results[name] = run_arm(name, pipeline, groups, args.workers, root)
        summaries.append(summary)
        print(json.dumps(summary), flush=True)
    problems = compare(results["per-batch"], results["pooled"])
    report = {"max_origins": args.max_origins, "workers": args.workers, "arms": summaries,
              "speedup": round(summaries[0]["wall_seconds"] / summaries[1]["wall_seconds"], 3),
              "identical_results": not problems, "differences": problems,
              "chains_compared": len(results["pooled"]),
              "forecast_rows_compared": int(sum(len(r.forecasts)
                                                for _, r in results["pooled"].values()))}
    print(json.dumps({k: v for k, v in report.items() if k != "arms"}, indent=2))
    if args.out:
        args.out.write_text(json.dumps(report, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
