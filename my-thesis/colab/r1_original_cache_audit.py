#!/usr/bin/env python3
"""R1 audit of the ORIGINAL fit cache: chain availability under both replay rules (read-only).

No estimation, nothing written outside --out. For every warm-started (MSAR, STAR) and ARMA
job of the R1 workflow it walks a local copy of the original fit cache

* by the pinned CACHE-HIT rule (what `rolling.run_chain` and the R1 replay
  `_replay_from_cache` use: the warm start is reset from each stored payload), and
* by the pinned LIVE rule (what an uninterrupted estimation writes: a failed fit keeps the
  previous usable warm start),

and, origin by origin along the longer walk, compares the cached payload with the PUBLISHED
fit record (status, reason codes, log-likelihood, whether a warm start was among the
starts tried, start used). At every origin that follows a failed fit it also records
whether the key each rule asks for exists in the cache.

Usage (in Colab, after a batch notebook's restore cell has filled ORIGINAL_CACHE):

    python r1_original_cache_audit.py --cache-fits /content/r1tierb_B1/original_cache/fits \\
        --code-dir <pinned>/my-thesis/code --original <original output> \\
        --chain-sources <corrected_r1_summary.json> --out /content/original_cache_audit
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r1_tierb as tb  # noqa: E402


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


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cache-fits", type=Path, required=True)
    parser.add_argument("--code-dir", type=Path, required=True)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--chain-sources", type=Path, default=None,
                        help="an R1 r1_summary.json, to report each chain's R1 source")
    parser.add_argument("--models", default="MSAR,MSAR3,STAR,ARMA")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    tb.use_scientific_code(args.code_dir)
    import pandas as pd
    from thesis.core.cache import FitCache
    from thesis.forecasting.rolling import _cache_key
    from thesis.forecasting.windows import estimation_origins

    jobs, identity, config = tb.build_jobs(args.original, args.code_dir)
    fit_records = pd.read_parquet(args.original / "models" / "fit_records.parquet")
    sources = {}
    if args.chain_sources:
        for source, tasks in json.loads(args.chain_sources.read_text())["chain_sources"].items():
            for task in tasks:
                sources[task] = source
    cache = FitCache(args.cache_fits, enabled=True)
    use_warm = bool(config.get("forecasting.warm_starts", True))
    models = set(args.models.split(","))
    chains, origins_rows = [], []
    for task, job in sorted(jobs.items()):
        if job.spec.model not in models:
            continue
        live = tb.walk_chain(job, args.cache_fits, identity, config, require_marker=False,
                             semantics="live")
        hit = tb.walk_chain(job, args.cache_fits, identity, config, require_marker=False,
                            semantics="cache_hit")
        try:
            published = tb.original_chain_records(fit_records, task, job)
        except tb.TierBError:
            published = {}
        origin_of = {o.origin_date.strftime("%Y-%m-%d"): o for o in estimation_origins(
            job.y.index, job.window_length, sorted(set(int(h) for h in job.horizons)),
            max_origins=job.max_origins)}
        counts = {"identical_to_published": 0, "differs_from_published": 0,
                  "no_published_record": 0}
        post_failure = {"origins": 0, "live_key_present": 0, "hit_key_present": 0}
        warm, previous = None, None
        for position, (date, relative) in enumerate(live["sequence"], start=1):
            payload = json.loads((args.cache_fits / relative).read_text())
            record = published.get(date)
            cached_starts = start_set((payload.get("record_detail") or {}).get("diagnostics"))
            row = {"task": task, "origin": position, "refit_date": date,
                   "status_cache": payload.get("status"),
                   "codes_cache": codes(payload.get("reason_codes")),
                   "loglik_cache": payload.get("loglik"),
                   "warm_tried_cache": "warm" in cached_starts,
                   "start_cache": payload.get("start_used")}
            if record is None:
                counts["no_published_record"] += 1
                row["comparison"] = "no published record"
            else:
                published_starts = start_set(record.diagnostics)
                same = (payload.get("status") == record.status
                        and codes(payload.get("reason_codes")) == codes(record.reason_codes)
                        and payload.get("loglik") == record.loglik)
                counts["identical_to_published" if same else "differs_from_published"] += 1
                row.update(status_published=record.status,
                           codes_published=codes(record.reason_codes),
                           loglik_published=record.loglik,
                           warm_tried_published="warm" in published_starts,
                           start_published=record.start_used,
                           comparison="identical" if same else "differs")
            if previous is not None and previous.get("status") == "failed":
                post_failure["origins"] += 1
                origin = origin_of[date]
                live_key = _cache_key(identity, job.series_name, job.transformation, job.spec,
                                      origin, tb.predecessor_hash(warm, use_warm))
                hit_key = _cache_key(identity, job.series_name, job.transformation, job.spec,
                                     origin, tb.predecessor_hash(previous.get("warm_payload"),
                                                                 use_warm))
                row["after_failed_fit"] = True
                row["live_key_present"] = cache.path_for(live_key).is_file()
                row["hit_key_present"] = cache.path_for(hit_key).is_file()
                post_failure["live_key_present"] += row["live_key_present"]
                post_failure["hit_key_present"] += row["hit_key_present"]
            origins_rows.append(row)
            warm = tb.live_warm_after(warm, payload)
            previous = payload
        failed_published = sum(1 for r in published.values() if r.status == "failed")
        chains.append({
            "task": task, "model": job.spec.model, "r1_source": sources.get(task, ""),
            "planned": live["planned"], "published_failed": failed_published,
            "cache_hit_completed": hit["completed"], "live_completed": live["completed"],
            "live_complete": live["complete"], "cache_hit_complete": hit["complete"],
            "rules_differ": live["completed"] != hit["completed"],
            "live_first_missing": live["first_missing"],
            "cache_hit_first_missing": hit["first_missing"],
            **counts, **{f"post_failure_{k}": v for k, v in post_failure.items()}})
    args.out.mkdir(parents=True, exist_ok=True)
    for name, rows in (("chains.csv", chains), ("origins.csv", origins_rows)):
        fields = sorted({k for r in rows for k in r}, key=lambda k: list(rows[0]).index(k)
                        if k in rows[0] else 99)
        with open(args.out / name, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    payloads = len(tb.payload_files(args.cache_fits))
    (args.out / "summary.json").write_text(json.dumps(
        {"cache_payloads": payloads, "chains": len(chains), "estimation": "none"}, indent=1))
    for c in chains:
        print(f"{c['task']:<26}{c['r1_source']:<13} planned {c['planned']:>4} "
              f"hit {c['cache_hit_completed']:>4} live {c['live_completed']:>4} "
              f"pub_failed {c['published_failed']:>3} identical {c['identical_to_published']:>4} "
              f"differs {c['differs_from_published']:>3}")
    print(f"{payloads} cached payloads examined; no estimation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
