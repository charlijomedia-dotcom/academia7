"""File-level comparison of an original and a corrected output tree (R1 workflow).

Tables are compared as text, cell by cell, after removing the provenance columns and the
run-time columns (`tools/compare_runs.py` conventions), so "identical" means every
printed number is identical. For each file the result says whether it is unchanged,
which columns were added or removed, and how many rows and cells differ.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ..core.provenance import PROVENANCE_COLUMNS

RUNTIME_COLUMNS = {"wall_seconds", "cpu_seconds", "peak_memory_mb", "recorded_utc",
                   "origins_from_cache", "from_cache", "cache_horizon_misses"}
CORRECTION_COLUMNS = {"correction_status"}
RUNTIME_KEYS = set(PROVENANCE_COLUMNS) | {"recorded_utc", "created_utc", "run_id",
                                          "execution_timestamp", "code_commit_sha"}


def _table(path: Path, ignore: set[str]) -> pd.DataFrame:
    frame = (pd.read_parquet(path) if path.suffix == ".parquet"
             else pd.read_csv(path, dtype=str, keep_default_na=False))
    frame = frame.drop(columns=[c for c in frame.columns if c in ignore])
    if path.suffix == ".parquet":
        # missing values print as "" (NaN != NaN would otherwise count as a difference)
        frame = frame.astype(object).where(frame.notna(), "").astype(str)
    return frame.reset_index(drop=True)


def _strip(value):
    if isinstance(value, dict):
        return {k: _strip(v) for k, v in value.items() if k not in RUNTIME_KEYS}
    if isinstance(value, list):
        return [_strip(v) for v in value]
    return value


#: Two printed numbers whose relative difference is below this are "equal within
#: floating-point tolerance": the level of last-digit differences produced when the same
#: code runs on a different CPU/BLAS (summation order, vector instructions). Reported
#: separately from exact identity, never merged into it.
RELATIVE_TOLERANCE = 1e-9
ABSOLUTE_TOLERANCE = 1e-12


def _numeric_close(a: pd.Series, b: pd.Series) -> tuple[bool, float]:
    x = pd.to_numeric(a, errors="coerce")
    y = pd.to_numeric(b, errors="coerce")
    if x.isna().any() or y.isna().any():
        return False, float("nan")
    diff = (x - y).abs()
    scale = pd.concat([x.abs(), y.abs()], axis=1).max(axis=1)
    relative = (diff / scale.where(scale > 0, 1.0))
    close = ((diff <= ABSOLUTE_TOLERANCE) | (relative <= RELATIVE_TOLERANCE)).all()
    return bool(close), float(relative.max()) if len(relative) else 0.0


def compare_file(original: Path, corrected: Path) -> dict:
    """One file: identical, or how it differs."""
    ignore = set(PROVENANCE_COLUMNS) | RUNTIME_COLUMNS | CORRECTION_COLUMNS
    suffix = original.suffix.lower()
    out = {"identical": False, "kind": "table" if suffix in (".csv", ".parquet")
           else "json" if suffix == ".json" else "binary"}
    if original.read_bytes() == corrected.read_bytes():
        out["identical"] = True
        return out
    if suffix in (".csv", ".parquet"):
        a, b = _table(original, ignore), _table(corrected, ignore)
        added = [c for c in b.columns if c not in a.columns]
        removed = [c for c in a.columns if c not in b.columns]
        out.update(columns_added=added, columns_removed=removed,
                   rows_original=len(a), rows_corrected=len(b))
        common = [c for c in a.columns if c in b.columns]
        if len(a) == len(b):
            diff = (a[common] != b[common])
            out["rows_differing"] = int(diff.any(axis=1).sum())
            out["cells_differing"] = int(diff.to_numpy().sum())
            out["columns_differing"] = [c for c in common if diff[c].any()]
            out["identical"] = (not added and not removed and out["cells_differing"] == 0)
            close, worst = True, 0.0
            for column in out["columns_differing"]:
                mask = diff[column]
                ok, rel = _numeric_close(a.loc[mask, column], b.loc[mask, column])
                close = close and ok
                worst = max(worst, rel) if rel == rel else worst
            out["within_tolerance"] = bool(not added and not removed and close)
            out["max_relative_difference"] = worst
        else:
            out["rows_differing"] = None
            out["cells_differing"] = None
            out["columns_differing"] = None
    elif suffix == ".json":
        a = _strip(json.loads(original.read_text(encoding="utf-8")))
        b = _strip(json.loads(corrected.read_text(encoding="utf-8")))
        out["identical"] = a == b
    else:
        out["identical"] = original.read_bytes() == corrected.read_bytes()
    return out


def compare_trees(original: Path, corrected: Path, files: list[str] | None = None) -> pd.DataFrame:
    """A row per file (all files of either tree, or only `files`)."""
    if files is None:
        names = ({p.relative_to(original).as_posix() for p in original.rglob("*") if p.is_file()}
                 | {p.relative_to(corrected).as_posix() for p in corrected.rglob("*")
                    if p.is_file()})
    else:
        names = set(files)
    rows = []
    for name in sorted(names):
        a, b = original / name, corrected / name
        if not a.exists() or not b.exists():
            rows.append({"path": name, "status": "added" if b.exists() else "removed"})
            continue
        result = compare_file(a, b)
        status = ("identical" if result["identical"] else
                  "equal_within_fp_tolerance" if result.get("within_tolerance") else "changed")
        rows.append({"path": name, "status": status,
                     **{k: (json.dumps(v) if isinstance(v, list) else v)
                        for k, v in result.items() if k != "identical"}})
    return pd.DataFrame(rows)
