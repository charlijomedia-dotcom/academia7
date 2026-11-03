#!/usr/bin/env python3
"""Tier B workload from the original run's own fit records (static; nothing is estimated).

Usage (from my-thesis/):
  python reports/part8/corrections/r1/tier_b_workload.py REPLAY_REPORT_CSV

REPLAY_REPORT_CSV is the Tier A evidence file
`replay_20261103T063749Z/replay_report/replay_report.csv` (branch
part8-r1-replay/20261103T063749Z, commit c5324b2). The nine Tier B chains are the non-AR
chains that report could not replay.

The original run estimated exactly these chains, so `models/fit_records.parquet` holds
their per-origin wall times (Colab, under 4 concurrent workers). A chain's records are
identified by series, model and window span; at the 240-month span the T4.1 chain is
separated from the baseline chain and its T4.8 duplicate, which carry identical
parameters at each origin, whereas the T4.1 fit (other transformation) does not.

Writes tier_b_workload.csv (per chain) and prints CPU hours, the longest chain and the
wall-clock schedule (longest-processing-time first) for 1-8 workers. CPU hours are the sum
of fit times; wall-clock is bounded below by the longest chain, because a warm-started
chain is sequential (each origin starts from the previous fit) and cannot be split.
"""

from __future__ import annotations

import heapq
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUTPUT = HERE.parents[3] / "output"


def chain_records(fits: pd.DataFrame, series: str, model: str, span: int,
                  t41: bool) -> pd.DataFrame:
    g = fits[(fits["series"] == series) & (fits["model"] == model) & (fits["span"] == span)]
    if span == 240:
        repeats = g.groupby(["refit_date", "params"])["params"].transform("size")
        g = g[repeats == 1] if t41 else g
    return g.sort_values("refit_date")


def schedule(hours: list[float], workers: int) -> float:
    loads = [0.0] * workers
    heapq.heapify(loads)
    for h in sorted(hours, reverse=True):
        heapq.heappush(loads, heapq.heappop(loads) + h)
    return max(loads)


def main(replay_csv: Path) -> pd.DataFrame:
    replay = pd.read_csv(replay_csv)
    tier_b = replay[(replay["model"] != "AR") & (~replay["replay_verified"])]
    fits = pd.read_parquet(OUTPUT / "models" / "fit_records.parquet",
                           columns=["series", "model", "window_start", "window_end",
                                    "refit_date", "params", "wall_seconds", "status"])
    start, end = pd.to_datetime(fits["window_start"]), pd.to_datetime(fits["window_end"])
    fits["span"] = (end.dt.year - start.dt.year) * 12 + (end.dt.month - start.dt.month) + 1
    rows = []
    for r in tier_b.itertuples():
        records = chain_records(fits, r.series, r.model, int(r.window_length),
                                t41=r.task_id.startswith("T4.1:"))
        if len(records) != r.planned_origins:
            raise SystemExit(f"{r.task_id}: {len(records)} original records, "
                             f"{r.planned_origins} planned origins")
        seconds = records["wall_seconds"].to_numpy(float)
        prefix = int(r.hit)               # original fits the cache holds before the first miss
        rows.append({
            "task_id": r.task_id, "series": r.series, "model": r.model, "spec": r.spec,
            "transformation": r.transformation, "window_length": int(r.window_length),
            "planned_origins": int(r.planned_origins), "cache_hits_before_first_miss": prefix,
            "cache_unknown_after_miss": int(r.unknown_after_miss),
            "original_failed_fits": int((records["status"] == "failed").sum()),
            "cpu_hours_whole_chain": seconds.sum() / 3600,
            "cpu_hours_replay_report_estimate": float(r.cpu_hours_residual),
            "cpu_hours_if_cached_prefix_reused": seconds[prefix:].sum() / 3600,
            "seconds_per_fit_mean": seconds.mean(),
        })
    table = pd.DataFrame(rows).sort_values("cpu_hours_whole_chain", ascending=False)
    table.to_csv(HERE / "tier_b_workload.csv", index=False)
    return table


if __name__ == "__main__":
    t = main(Path(sys.argv[1]))
    pd.set_option("display.width", 200)
    print(t[["task_id", "planned_origins", "original_failed_fits", "cpu_hours_whole_chain",
             "cpu_hours_replay_report_estimate", "cpu_hours_if_cached_prefix_reused"]]
          .round(2).to_string(index=False))
    whole = t["cpu_hours_whole_chain"].tolist()
    prefix = t["cpu_hours_if_cached_prefix_reused"].tolist()
    print(f"\nwhole-chain rule: {sum(whole):.1f} CPU hours, {t['planned_origins'].sum()} "
          f"origins; longest chain {max(whole):.1f} h")
    print(f"prefix-reuse alternative (NOT approved): {sum(prefix):.1f} CPU hours; "
          f"longest {max(prefix):.1f} h")
    for w in (1, 2, 3, 4, 6, 8):
        print(f"  {w} workers: wall-clock ~{schedule(whole, w):.1f} h (whole chains)")
