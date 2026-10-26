#!/usr/bin/env python3
"""Compare the research outputs of two runs, separating results from run-time metadata.

Two runs of the same code, configuration and data must produce the same research
results. They legitimately differ only in run-time metadata: the run ID and creation
time stamped on every table, measured wall and CPU times, and the timestamps of
checkpoints and manifests. This tool compares everything else, exactly:

* every CSV and Parquet table, cell by cell as text, after removing the provenance
  columns and the columns that measure elapsed time;
* every figure, byte for byte (figures are byte-reproducible since Part 7);
* every figure sidecar and checkpoint JSON, after removing provenance and timestamp keys;
* the set of files present.

The run manifests (`manifests/run_manifest.json`, `manifests/run_summary.json`) and the
output inventory's checksums describe the run rather than its results, so they are
listed as metadata rather than compared. Usage:

    python tools/compare_runs.py OUTPUT_A OUTPUT_B [--cache-a CACHE_A --cache-b CACHE_B]

Exit status 0 means identical results; 1 lists every difference.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from thesis.core.provenance import PROVENANCE_COLUMNS  # noqa: E402

#: Columns that measure the run rather than the research result.
RUNTIME_COLUMNS = {"wall_seconds", "cpu_seconds", "peak_memory_mb", "recorded_utc"}
#: Keys of JSON sidecars and checkpoints that are run-time metadata.
RUNTIME_KEYS = set(PROVENANCE_COLUMNS) | {"recorded_utc", "created_utc", "run_id",
                                          "execution_timestamp", "code_commit_sha"}
METADATA_FILES = {"manifests/run_manifest.json", "manifests/run_summary.json"}
#: The inventory's per-file checksums cover the provenance columns, so only its list of
#: paths is a result.
INVENTORY = "manifests/output_inventory.csv"


def _strip(value):
    if isinstance(value, dict):
        return {k: _strip(v) for k, v in value.items() if k not in RUNTIME_KEYS}
    if isinstance(value, list):
        return [_strip(v) for v in value]
    return value


def _table(path: Path) -> pd.DataFrame:
    frame = (pd.read_parquet(path) if path.suffix == ".parquet"
             else pd.read_csv(path, dtype=str, keep_default_na=False))
    drop = [c for c in frame.columns if c in PROVENANCE_COLUMNS or c in RUNTIME_COLUMNS]
    frame = frame.drop(columns=drop)
    if path.suffix == ".parquet":
        frame = frame.astype(str)
    return frame


def compare_trees(a: Path, b: Path) -> tuple[list[str], dict[str, int]]:
    differences: list[str] = []
    counts = {"tables": 0, "figures": 0, "json": 0, "metadata_skipped": 0}
    files_a = {p.relative_to(a).as_posix() for p in a.rglob("*") if p.is_file()}
    files_b = {p.relative_to(b).as_posix() for p in b.rglob("*") if p.is_file()}
    for missing in sorted(files_a ^ files_b):
        differences.append(f"present in only one run: {missing}")
    for relative in sorted(files_a & files_b):
        left, right = a / relative, b / relative
        if relative in METADATA_FILES:
            counts["metadata_skipped"] += 1
            continue
        suffix = left.suffix.lower()
        if relative == INVENTORY:
            paths_a = pd.read_csv(left, dtype=str)["path"].tolist()
            paths_b = pd.read_csv(right, dtype=str)["path"].tolist()
            if paths_a != paths_b:
                differences.append(f"{relative}: different file lists")
            counts["tables"] += 1
        elif suffix in (".csv", ".parquet"):
            ta, tb = _table(left), _table(right)
            if list(ta.columns) != list(tb.columns) or ta.shape != tb.shape:
                differences.append(f"{relative}: shape/columns {ta.shape} vs {tb.shape}")
            elif not ta.equals(tb):
                mask = (ta != tb).any(axis=1)
                differences.append(f"{relative}: {int(mask.sum())} rows differ "
                                   f"(first at row {int(mask.idxmax())})")
            counts["tables"] += 1
        elif suffix == ".json":
            ja = _strip(json.loads(left.read_text(encoding="utf-8")))
            jb = _strip(json.loads(right.read_text(encoding="utf-8")))
            if ja != jb:
                differences.append(f"{relative}: JSON content differs")
            counts["json"] += 1
        else:
            if left.read_bytes() != right.read_bytes():
                differences.append(f"{relative}: bytes differ")
            counts["figures"] += 1
    return differences, counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("output_a", type=Path)
    parser.add_argument("output_b", type=Path)
    parser.add_argument("--cache-a", type=Path)
    parser.add_argument("--cache-b", type=Path)
    args = parser.parse_args(argv)

    differences, counts = compare_trees(args.output_a, args.output_b)
    if args.cache_a and args.cache_b:
        more, extra = compare_trees(args.cache_a / "checkpoints", args.cache_b / "checkpoints")
        differences += [f"checkpoints/{d}" for d in more]
        counts["checkpoints"] = extra["json"]
    print(json.dumps(counts))
    if differences:
        print(f"{len(differences)} difference(s):")
        for difference in differences:
            print(f"  {difference}")
        return 1
    print("identical research outputs (run-time metadata excluded as documented)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
