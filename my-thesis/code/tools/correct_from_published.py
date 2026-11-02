#!/usr/bin/env python3
"""R1 correction workflow: correct the Part 8 evidence from the published forecasts.

Two modes, run in this order:

  --legacy     every correction switched off; the regenerated tables must equal the
               original published tables (validation gate). Writes the per-file
               comparison and exits 1 if any regenerated file differs.
  (default)    corrections F1, F2, F3, F4 and F7.1 on; with --release, assembles the
               corrected release (original tree + regenerated files + manifests).

Nothing under the original output tree is written. No rolling chain is estimated
unless its task id is passed with --approve (each approved chain is re-estimated whole
and labelled `re-estimated`); with --cache-root, chains that the restored fit cache
holds completely are replayed through the rolling engine with estimation disabled.

Examples (from my-thesis/code):

  python tools/correct_from_published.py --original ../output --staging /tmp/r1_legacy --legacy
  python tools/correct_from_published.py --original ../output --staging /tmp/r1_corr \\
         --release ../output_corrected
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from thesis.correction import workflow  # noqa: E402
from thesis.correction.compare import compare_trees  # noqa: E402
from thesis.core.provenance import git_commit_sha, git_dirty_paths  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--original", type=Path, required=True,
                        help="the original published output tree (read only)")
    parser.add_argument("--staging", type=Path, required=True,
                        help="empty directory for the regenerated files")
    parser.add_argument("--legacy", action="store_true",
                        help="all corrections off: must reproduce the original tables")
    parser.add_argument("--cache-root", type=Path, default=None,
                        help="restored fit cache root (holding fits/); enables replay")
    parser.add_argument("--approve", action="append", default=[],
                        help="chain task id approved for new estimation (repeatable)")
    parser.add_argument("--refit-cache", type=Path, default=None,
                        help="checkpoint store for --approve'd chains (a directory apart "
                             "from the original cache; lets an interrupted refit resume)")
    parser.add_argument("--release", type=Path, default=None,
                        help="assemble the corrected release here (not with --legacy)")
    parser.add_argument("--legacy-staging", type=Path, default=None,
                        help="a passed --legacy staging tree from the same machine; cells "
                             "the corrections did not change keep the original text")
    args = parser.parse_args(argv)
    if args.staging.exists() and any(args.staging.iterdir()):
        parser.error(f"{args.staging} is not empty")
    if args.legacy and args.release:
        parser.error("--release is only for the corrected mode")
    if args.release or args.legacy_staging:
        # A release is reproducible from its recorded commit only if nothing that
        # determines it was uncommitted; the legacy tree used for reconciliation must come
        # from the same commit.
        dirty = git_dirty_paths()
        if dirty is None or dirty:
            parser.error("a release must be built from a clean, committed tree; "
                         f"uncommitted: {list(dirty or ['<git unavailable>'])[:10]}")
    if args.legacy_staging:
        manifest = json.loads((args.legacy_staging / "manifests" / "run_manifest.json")
                              .read_text(encoding="utf-8"))
        if manifest.get("code_commit_sha") != git_commit_sha() or manifest.get(
                "code_tree_dirty"):
            parser.error("--legacy-staging was produced by a different or dirty commit "
                         f"({manifest.get('code_commit_sha')}, dirty="
                         f"{manifest.get('code_tree_dirty')}); rerun --legacy first")

    summary = workflow.run(args.original.resolve(), args.staging.resolve(), legacy=args.legacy,
                           cache_root=args.cache_root, approved_estimation=args.approve,
                           refit_cache=args.refit_cache)
    files = [f for f in summary["regenerated_files"] if f not in workflow.WORKFLOW_FILES]
    comparison = compare_trees(args.original.resolve(), args.staging.resolve(), files=files)
    comparison.to_csv(args.staging / "r1_comparison.csv", index=False)
    changed = comparison[~comparison["status"].isin(["identical", "equal_within_fp_tolerance"])]
    tolerance = comparison[comparison["status"] == "equal_within_fp_tolerance"]
    print(f"regenerated {len(files)} files; identical: "
          f"{int((comparison['status'] == 'identical').sum())}; equal within floating-point "
          f"tolerance (rel <= 1e-9, every non-numeric cell identical): {len(tolerance)}; "
          f"differing: {len(changed)}")
    for row in tolerance.itertuples():
        print(f"  fp-level  {row.path}  max rel diff {row.max_relative_difference:.2e}")
    for row in changed.itertuples():
        print(f"  {row.status:<9} {row.path}  {getattr(row, 'columns_differing', '')}")
    print("estimations performed:", summary.get("estimations_performed") or "none")
    print(json.dumps({k: summary[k] for k in ("chain_sources", "retained")}, indent=1,
                     default=str)[:4000])
    if args.legacy:
        return 0 if changed.empty else 1
    if args.legacy_staging:
        account = workflow.reconcile(args.original.resolve(), args.legacy_staging.resolve(),
                                     args.staging.resolve(), files)
        account.to_csv(args.staging / "r1_reconciliation.csv", index=False)
        print(account.to_string(index=False))
        comparison = compare_trees(args.original.resolve(), args.staging.resolve(), files=files)
        comparison.to_csv(args.staging / "r1_comparison.csv", index=False)
    if args.release:
        release = workflow.assemble(args.original.resolve(), args.staging.resolve(),
                                    args.release.resolve(), summary)
        print(f"release assembled at {args.release}: "
              f"{int((release['status'] != 'identical').sum())} files differ from the original")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
