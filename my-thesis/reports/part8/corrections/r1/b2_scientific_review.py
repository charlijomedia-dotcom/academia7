"""B2 scientific review: B2 re-estimated payloads against the ORIGINAL cache (live rule).

Read-only; NO model is estimated (payloads are only read). For each B2 chain
(T4.1:FEDFUNDS|MSAR, T4.8:UNRATE|180:MSAR) both payload stores are walked by the pinned
LIVE warm-start rule (`r1_tierb.walk_chain`), and at every origin the B2 payload is
compared with the original-cache payload: cache key (same key = same window, same
specification and same predecessor warm start), status, reason codes, log-likelihood,
parameters (minimised over MSAR regime relabellings), forecasts at every horizon, start
and warm-start vector. The published fit record (`origins.csv` of the audit, and the
original fit records) is joined, as is the B2 session's own agreement table.

Where a B2 payload is not available locally (UNRATE 180 origins committed by the second
B2 session), the comparison is TRANSITIVE and labelled so: B2 vs published (the B2
agreement table: loglik and parameter tolerances) combined with original cache vs
published (computed here from the original payloads).

usage: b2_scientific_review.py --cache-fits F --b2 TASK=DIR [--b2 ...] --agreement CSV
       --origins CSV --code-dir C --original OUT --out DIR
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

LOGLIK_TOL, PARAM_TOL, FORECAST_TOL = 1e-6, 1e-8, 1e-8


def load(path):
    return json.loads(Path(path).read_text())


def codes(value) -> str:
    if isinstance(value, list):
        return ";".join(sorted(str(v) for v in value))
    if value is None or (isinstance(value, float) and value != value):
        return ""
    return ";".join(sorted(c.strip() for c in str(value).split(";") if c.strip()))


def fnum(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return float("nan")
    return x


def compare_payloads(tb, b2: dict, cache: dict, model: str) -> dict:
    pdiff, perm = tb.aligned_param_diff(b2.get("params", {}), cache.get("params", {}), model) \
        if set(b2.get("params", {})) == set(cache.get("params", {})) else (float("inf"), "names differ")
    common = sorted(set(b2.get("forecasts", {})) & set(cache.get("forecasts", {})), key=int)
    fdiff = max((abs(fnum(b2["forecasts"][h]) - fnum(cache["forecasts"][h])) for h in common),
                default=0.0)
    lb, lc = fnum(b2.get("loglik")), fnum(cache.get("loglik"))
    dl = lb - lc if math.isfinite(lb) and math.isfinite(lc) else (0.0 if lb == lc or (lb != lb and lc != lc) else float("inf"))
    same_class = b2.get("status") == cache.get("status") and codes(b2.get("reason_codes")) == codes(cache.get("reason_codes"))
    if same_class and abs(dl) <= LOGLIK_TOL and pdiff <= PARAM_TOL:
        category = "identical_estimate"
    elif same_class:
        category = "optimizer_sensitivity"
    else:
        category = "classification_changed"
    return {"status_b2": b2.get("status"), "status_cache": cache.get("status"),
            "codes_b2": codes(b2.get("reason_codes")), "codes_cache": codes(cache.get("reason_codes")),
            "loglik_b2": lb, "loglik_cache": lc, "loglik_b2_minus_cache": dl,
            "params_max_scaled_diff": pdiff, "regime_permutation": perm,
            "forecast_max_abs_diff": fdiff, "horizons_compared": ";".join(common),
            "start_b2": b2.get("start_used"), "start_cache": cache.get("start_used"),
            "category_b2_vs_cache": category}


def main(argv=None) -> dict:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-fits", type=Path, required=True)
    ap.add_argument("--b2", action="append", required=True, help="TASK=DIR")
    ap.add_argument("--agreement", type=Path, required=True)
    ap.add_argument("--origins", type=Path, required=True)
    ap.add_argument("--code-dir", type=Path, required=True)
    ap.add_argument("--original", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    sys.path.insert(0, str(args.code_dir.parent / "colab"))
    import pandas as pd
    import r1_tierb as tb
    tb.use_scientific_code(args.code_dir)
    from thesis.correction import guard
    with guard.estimation_forbidden(), tb.no_estimation_allowed():
        jobs, identity, config = tb.build_jobs(args.original, args.code_dir)
    fit_records = pd.read_parquet(args.original / "models" / "fit_records.parquet")
    agreement = {(r["task"], r["refit_date"]): r for r in csv.DictReader(open(args.agreement))}
    origins = {(r["task"], r["refit_date"]): r for r in csv.DictReader(open(args.origins))}
    args.out.mkdir(parents=True, exist_ok=True)
    rows, summary = [], {"estimation": "none (payloads read only)",
                         "tolerances": {"loglik": LOGLIK_TOL, "params_scaled": PARAM_TOL,
                                        "forecast_abs": FORECAST_TOL}, "chains": {}}
    for spec in args.b2:
        task, folder = spec.split("=", 1)
        job = jobs[task]
        model = job.spec.model
        with guard.estimation_forbidden(), tb.no_estimation_allowed():
            walk_cache = tb.walk_chain(job, args.cache_fits, identity, config,
                                       require_marker=False, semantics="live")
            walk_b2 = tb.walk_chain(job, Path(folder), identity, config,
                                    require_marker=True, semantics="live")
        cache_seq, b2_seq = dict(walk_cache["sequence"]), dict(walk_b2["sequence"])
        published = tb.original_chain_records(fit_records, task, job)
        dates = [d for d, _ in walk_cache["sequence"]]
        counts: dict[str, int] = {}
        for i, date in enumerate(dates):
            cache_payload = load(args.cache_fits / cache_seq[date])
            pub = published.get(date)
            pub_params = tb._parse_params(pub.params) if pub is not None else {}
            cache_vs_pub_params = (tb.aligned_param_diff(cache_payload.get("params", {}), pub_params, model)[0]
                                   if pub is not None and set(pub_params) == set(cache_payload.get("params", {}))
                                   else float("nan"))
            o = origins.get((task, date), {})
            a = agreement.get((task, date), {})
            row = {"task": task, "origin": i + 1, "refit_date": date,
                   "status_published": o.get("status_published", ""),
                   "codes_published": o.get("codes_published", ""),
                   "loglik_published": o.get("loglik_published", ""),
                   "cache_vs_published": o.get("record_comparison", ""),
                   "cache_vs_published_params_max_scaled_diff": cache_vs_pub_params,
                   "after_failed_fit": o.get("after_failed_fit", ""),
                   "b2_agreement_category_vs_published": a.get("category", ""),
                   "b2_vs_published_loglik_diff": a.get("loglik_new_minus_original", ""),
                   "b2_vs_published_params_max_scaled_diff": a.get("params_max_scaled_diff", "")}
            if date in b2_seq:
                b2_payload = load(Path(folder) / b2_seq[date])
                row.update({"comparison": "direct (both payloads)",
                            "same_cache_key": b2_seq[date] == cache_seq[date]})
                row.update(compare_payloads(tb, b2_payload, cache_payload, model))
                # the B2 agreement table must agree with the payload itself
                if a:
                    row["agreement_table_consistent_with_b2_payload"] = (
                        a["status_new"] == b2_payload.get("status")
                        and abs(fnum(a["loglik_new"]) - fnum(b2_payload.get("loglik"))) <= 1e-12)
            else:
                same_pub_b2 = a.get("category") == "reproduced"
                same_pub_cache = (o.get("record_comparison") == "identical"
                                  and cache_vs_pub_params <= PARAM_TOL)
                row.update({"comparison": "transitive (B2 payload not retrieved; B2 agreement table + original cache vs published)",
                            "same_cache_key": "",
                            "status_cache": cache_payload.get("status"),
                            "codes_cache": codes(cache_payload.get("reason_codes")),
                            "loglik_cache": cache_payload.get("loglik"),
                            "status_b2": a.get("status_new", ""),
                            "codes_b2": codes(a.get("reason_codes_new", "")),
                            "loglik_b2": a.get("loglik_new", ""),
                            "category_b2_vs_cache": ("identical_estimate (transitive)"
                                                     if same_pub_b2 and same_pub_cache else
                                                     "not established transitively")})
            counts[row["category_b2_vs_cache"]] = counts.get(row["category_b2_vs_cache"], 0) + 1
            rows.append(row)
        chain_rows = [r for r in rows if r["task"] == task]
        summary["chains"][task] = {
            "original_cache_live": {k: walk_cache[k] for k in ("planned", "completed", "complete", "statuses")},
            "b2_live": {k: walk_b2[k] for k in ("planned", "completed", "complete", "statuses")},
            "b2_unreachable_payloads": len(walk_b2["unreachable"]),
            "compared_directly": sum(1 for r in chain_rows if r["comparison"].startswith("direct")),
            "compared_transitively": sum(1 for r in chain_rows if r["comparison"].startswith("transitive")),
            "same_cache_key_direct": sum(1 for r in chain_rows if r.get("same_cache_key") is True),
            "categories_b2_vs_cache": counts,
            "b2_vs_published": _count(chain_rows, "b2_agreement_category_vs_published"),
            "cache_vs_published": _count(chain_rows, "cache_vs_published"),
            "agreement_table_consistent_with_payloads": all(
                r.get("agreement_table_consistent_with_b2_payload", True) for r in chain_rows),
            "max_forecast_abs_diff_direct": max((r["forecast_max_abs_diff"] for r in chain_rows
                                                 if "forecast_max_abs_diff" in r), default=None),
            "status_counts_b2_vs_cache": _status(chain_rows),
        }
    fields = []
    for r in rows:
        fields += [k for k in r if k not in fields]
    with open(args.out / "b2_vs_original_cache_by_origin.csv", "w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    (args.out / "b2_vs_original_cache_summary.json").write_text(json.dumps(summary, indent=1, default=str))
    return summary


def _count(rows, key):
    out: dict[str, int] = {}
    for r in rows:
        out[str(r.get(key))] = out.get(str(r.get(key)), 0) + 1
    return out


def _status(rows):
    b2, cache, pub = {}, {}, {}
    for r in rows:
        for store, k in ((b2, "status_b2"), (cache, "status_cache"), (pub, "status_published")):
            store[str(r.get(k))] = store.get(str(r.get(k)), 0) + 1
    return {"b2": b2, "original_cache_live": cache, "published": pub}


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, default=str))
