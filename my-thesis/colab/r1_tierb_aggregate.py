#!/usr/bin/env python3
"""R1 Tier B aggregation: validate B1+B2+B3, merge, assemble with NO estimation, dry run.

Callable from an optional cell of any batch notebook, once all three batches carry a
completion certificate. It never estimates and never pushes:

 1. discover each batch's latest certificate; refuse if any is missing, incomplete, for
    other tasks, other code, or contradicted by the checkpoints now on Drive;
 2. restore the Tier A archive and every certified Tier B checkpoint into ONE merged
    refit cache, refusing any conflicting payload; walk all 17 chains (complete, every
    payload reached);
 3. run the pinned R1 workflow (legacy, then corrected + release) with --approve for the
    17 chains, --refit-cache = the merged cache, --cache-root = the original cache, inside
    `no_estimation_allowed()`: an estimator call would raise instead of fitting;
 4. gates: estimations_performed empty; 17 re-estimated + 17 cache + exactly the 26
    unaffected unavailable chains; no `original_retained_pending_estimation` row left;
    legacy reproduction of every file not built from a re-estimated Tier B chain; T4.2
    identical to the Tier A release; the batches' origin-level agreement reports;
 5. write a dry-run publication plan to DRIVE_ROOT/baseline/r1_tierb_aggregation/<stamp>/.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r1_tierb as tb  # noqa: E402

PENDING = "original_retained_pending_estimation"
#: Files a re-estimated Tier B chain feeds; in legacy mode they are compared to the
#: original as numerical agreement, not as reproduction.
REESTIMATION_DEPENDENT = ("robustness/T4.1_", "robustness/window_length_", "figures/F4.1",
                          "figures/F4.8")


def discover(drive_root: Path) -> dict[str, dict]:
    """Each batch's latest certificate, validated against the checkpoints now on Drive."""
    certificates, problems = {}, []
    for batch in sorted(tb.BATCHES):
        root = tb.batch_root(drive_root, batch)
        cert = tb.latest_certificate(root)
        if cert is None:
            problems.append(f"{batch}: no completion certificate")
            continue
        if not cert.get("complete") or cert.get("batch") != batch:
            problems.append(f"{batch}: certificate not complete")
        if list(cert.get("authorized_tasks", [])) != list(tb.BATCHES[batch]):
            problems.append(f"{batch}: certificate tasks {cert.get('authorized_tasks')}")
        if cert.get("completed_origins") != cert.get("expected_origins"):
            problems.append(f"{batch}: {cert.get('completed_origins')} of "
                            f"{cert.get('expected_origins')} origins")
        prov = cert.get("provenance", {})
        if prov.get("scientific_commit") != tb.SCIENTIFIC_PIN or \
                prov.get("cache_identity") != tb.CACHE_IDENTITY:
            problems.append(f"{batch}: certificate provenance {prov.get('scientific_commit')}, "
                            f"{prov.get('cache_identity')}")
        for task, chain in cert.get("chains", {}).items():
            listed = [c["checkpoint_id"] for c in chain.get("checkpoints", [])]
            try:
                on_drive = [m["checkpoint_id"] for _, m in
                            tb.committed_checkpoints(root / "checkpoints" / tb.slug(task))]
            except tb.TierBError as error:
                problems.append(f"{batch} {task}: {error}")
                continue
            if listed != on_drive:
                problems.append(f"{batch} {task}: Drive checkpoints {on_drive} differ from "
                                f"the certified {listed}")
        certificates[batch] = cert
    tasks = [t for c in certificates.values() for t in c.get("authorized_tasks", [])]
    if len(tasks) != len(set(tasks)):
        problems.append("a task is certified by two batches")
    if not problems and set(tasks) != set(tb.TIER_B_CHAINS):
        problems.append(f"certified tasks {sorted(tasks)} are not the nine Tier B chains")
    if problems:
        raise tb.TierBError("aggregation refused: " + "; ".join(problems))
    return certificates


def merge(drive_root: Path, tier_a_archive: Path, merged_fits: Path) -> dict:
    """Tier A + certified Tier B checkpoints into one refit cache; conflicts refuse."""
    if merged_fits.exists() and any(merged_fits.rglob("*.json")):
        raise tb.TierBError(f"{merged_fits} is not empty")
    report = {"tier_a": tb.restore_tier_a(tier_a_archive, merged_fits,
                                          expected_sha256=tb.TIER_A_ARCHIVE_SHA256),
              "batches": {}}
    for batch, tasks in sorted(tb.BATCHES.items()):
        root = tb.batch_root(drive_root, batch)
        for task in tasks:
            report["batches"][task] = tb.restore_checkpoints(root / "checkpoints" / tb.slug(task),
                                                             merged_fits)
    report["payloads"] = len(tb.payload_files(merged_fits))
    return report


def walk_all(jobs, identity, config, merged_fits: Path) -> dict:
    walks, reached = {}, set()
    for task in list(tb.TIER_A_CHAINS) + list(tb.TIER_B_CHAINS):
        walk = tb.walk_chain(jobs[task], merged_fits, identity, config)
        if not walk["complete"]:
            raise tb.TierBError(f"{task}: {walk['completed']}/{walk['planned']} in the merged cache")
        reached |= set(walk["reached"])
        walks[task] = {k: walk[k] for k in ("planned", "completed", "statuses")}
    present = {p.relative_to(merged_fits).as_posix() for p in tb.payload_files(merged_fits)}
    if present - reached:
        raise tb.TierBError(f"{len(present - reached)} merged payloads belong to no chain")
    return walks


def assemble(code_dir: Path, original: Path, cache_root: Path, refit_root: Path,
             out: Path) -> dict:
    """The pinned R1 workflow, legacy then corrected + release, with estimation refused."""
    spec = importlib.util.spec_from_file_location(
        "correct_from_published", code_dir / "tools" / "correct_from_published.py")
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    approve = [a for t in list(tb.TIER_A_CHAINS) + list(tb.TIER_B_CHAINS)
               for a in ("--approve", t)]
    common = ["--original", str(original), "--cache-root", str(cache_root),
              "--refit-cache", str(refit_root), *approve]
    with tb.no_estimation_allowed():
        legacy_code = cli.main([*common, "--staging", str(out / "legacy"), "--legacy"])
        corrected_code = cli.main([*common, "--staging", str(out / "corrected"),
                                   "--legacy-staging", str(out / "legacy"),
                                   "--release", str(out / "release")])
    return {"legacy_exit": legacy_code, "corrected_exit": corrected_code}


def gates(out: Path, tier_a_release: Path, unaffected_csv: Path) -> dict:
    problems, report = [], {}
    legacy = json.loads((out / "legacy" / "r1_summary.json").read_text())
    corrected = json.loads((out / "corrected" / "r1_summary.json").read_text())
    for name, summary in (("legacy", legacy), ("corrected", corrected)):
        if summary.get("estimations_performed"):
            problems.append(f"{name}: estimations performed {summary['estimations_performed']}")
    sources = corrected["chain_sources"]
    expected = sorted(list(tb.TIER_A_CHAINS) + list(tb.TIER_B_CHAINS))
    if sorted(sources.get("re-estimated", [])) != expected:
        problems.append(f"re-estimated chains {sources.get('re-estimated')}")
    with open(unaffected_csv, newline="") as handle:
        unaffected = sorted(r["task_id"] for r in csv.DictReader(handle)
                            if r["affected_by_correction"] == "False")
    unavailable = sorted(sources.get("unavailable", []))
    if not set(unavailable) <= set(unaffected) or len(unavailable) != 26:
        problems.append(f"unavailable chains are not exactly 26 unaffected ones: {unavailable}")
    report["chain_sources"] = {k: len(v) for k, v in sources.items()}
    pending = []
    for path in (out / "release").rglob("*.csv"):
        with open(path, newline="") as handle:
            reader = csv.DictReader(handle)
            if "correction_status" in (reader.fieldnames or []):
                if any(row["correction_status"] == PENDING for row in reader):
                    pending.append(path.relative_to(out / "release").as_posix())
    if pending:
        problems.append(f"pending rows remain in {pending}")
    # reproduction (legacy) kept apart from agreement of re-estimated chains
    reproduction, dependent = [], []
    with open(out / "legacy" / "r1_comparison.csv", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["status"] in ("identical", "equal_within_fp_tolerance"):
                continue
            (dependent if row["path"].startswith(REESTIMATION_DEPENDENT) else reproduction) \
                .append(row["path"])
    if reproduction:
        problems.append(f"legacy reproduction failed for {reproduction}")
    report["legacy_differences_from_reestimated_chains"] = dependent
    from thesis.correction.compare import compare_file      # the pinned checkout's
    for name in ("T4.2_cpi_lag_robustness.csv", "T4.2_cpi_lag_predictive_tests.csv"):
        result = compare_file(tier_a_release / "robustness" / name,
                              out / "release" / "robustness" / name)
        if not result["identical"]:
            problems.append(f"{name} differs from the Tier A release")
    report["problems"] = problems
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--drive-root", type=Path, required=True)
    parser.add_argument("--code-dir", type=Path, required=True, help="pinned my-thesis/code")
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--cache-root", type=Path, required=True, help="holds original fits/")
    parser.add_argument("--tier-a-archive", type=Path, required=True)
    parser.add_argument("--tier-a-release", type=Path, required=True,
                        help="output_corrected/ of the Tier A release 292227e")
    parser.add_argument("--unaffected-csv", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args(argv)
    tb.use_scientific_code(args.code_dir)
    certificates = discover(args.drive_root)
    merged_root = args.work / "merged_refit"
    merge_report = merge(args.drive_root, args.tier_a_archive, merged_root / "fits")
    jobs, identity, config = tb.build_jobs(args.original, args.code_dir)
    walks = walk_all(jobs, identity, config, merged_root / "fits")
    exits = assemble(args.code_dir, args.original, args.cache_root, merged_root,
                     args.work / "assembly")
    report = gates(args.work / "assembly", args.tier_a_release, args.unaffected_csv)
    plan = {"dry_run": True, "release": str(args.work / "assembly" / "release"),
            "run_id": json.loads((args.work / "assembly" / "corrected" / "r1_summary.json")
                                 .read_text())["run_id"],
            "certificates": {b: c["created_utc"] for b, c in certificates.items()},
            "agreement_warnings": [w for c in certificates.values() for w in c["warnings"]],
            "requires_review": [t for c in certificates.values()
                                for t in c.get("agreement", {}).get("requires_review", [])],
            "merge": {k: v for k, v in merge_report.items() if k != "batches"},
            "walks": walks, "assembly": exits, "gates": report,
            "publish": "NOT PERFORMED: final publication requires separate authorisation"}
    target = args.drive_root / "baseline" / "r1_tierb_aggregation" / tb.utc_stamp()
    tb.write_json_atomic(target / "aggregation_plan.json", plan)
    print(json.dumps({k: plan[k] for k in ("run_id", "requires_review", "gates")}, indent=1))
    # In legacy mode the pinned CLI exits 1 whenever any file differs; files fed by the
    # re-estimated chains are expected to differ, so the gate above decides, not that code.
    ok = not report["problems"] and exits["corrected_exit"] == 0 and exits["legacy_exit"] in (0, 1)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
