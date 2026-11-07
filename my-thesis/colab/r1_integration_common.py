"""Shared definitions for the Part 8 integration dry run (`r1_part8_integration.py`).

Orchestration only: no estimation, no publication. Every scientific computation is done by
the pinned code (`8aaa4217…`). This module holds the fixed identities the dry run checks,
the write boundary, protected-input listings and the cell-level table comparison that
stages 4 and 5 use.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import os
import re
from pathlib import Path
from typing import Iterable

# -- fixed identities (each one is checked; none is trusted) ---------------------------

SCIENTIFIC_PIN = "8aaa4217536ab3cb942dd248dd19ece7838a8d60"
FROZEN_DATA_SHA256 = "7e7dc769bd63ca4951ef55430180f413de62c9dc53a275af50ad277a715b832a"
FROZEN_DATA_RELATIVE = "data/frozen/thesis_input_2026-10-05.csv"
CONFIG_HASH = "949fcd76769048e3322f1595cd9bfb26006f8dcb692c17d16d3a9e5dab61db8e"
ORIGINAL_CACHE_IDENTITY = "3413465b508bb844"
ORIGINAL_CACHE_PAYLOADS = 18964
#: sha256 over the sorted lines "<payload path> <sha256>\n" of the 18,964 original payloads
#: (`r1_original_cache_audit.verify`; Colab and local restore agree).
ORIGINAL_CACHE_DIGEST = "7e283de334a0b879120f300c3a169a37f9a4ca1cecf3e73168d7bdf43716b2a0"
B1_STAGED_RUN_ID = "b1-staged-20261106T154902Z"
B1_STAGED_TASKS = ("forecasting:UNRATE|MSAR", "T4.8:UNRATE|240:MSAR")
#: Releases (read only, fetched with `git archive`): Tier A, and the R1 release the claim
#: matrix was written against.
TIER_A_RELEASE_COMMIT = "292227e0904bb9a857c76d633031c39fbd463eae"
CLAIMS_REFERENCE_COMMIT = "0573a8c"
CLAIMS_REFERENCE_RUN_ID = "correction-20261101T152213-949fcd76"
#: The chains whose cache-hit and live warm-start rules differ (B3 stage-2 audit).
RULE_SENSITIVE_CHAINS = ("T4.1:FEDFUNDS|MSAR", "T4.8:UNRATE|180:MSAR", "T4.8:UNRATE|240:MSAR",
                         "T4.8:UNRATE|300:MSAR", "forecasting:UNRATE|MSAR")

#: Repository paths (relative to my-thesis/) the dry run reads.
REL = {
    "staged_overlay": "output_staging/r1_b1_unrate_msar_20261106",
    "certificate_manifest": ("reports/part8/corrections/r1/evidence/integration_prep_20261106/"
                             "certificates/MANIFEST.csv"),
    "b2_by_origin": ("reports/part8/corrections/r1/evidence/integration_prep_20261106/"
                     "b2_direct_review/b2_vs_original_cache_by_origin.csv.gz"),
    "chain_classification": "reports/part8/corrections/r1/nonpublished_chain_classification.csv",
    "claim_matrix": "reports/part8/corrections/r1/claim_evidence_matrix_corrected.csv",
    "jury_registry": "approved-specs/part2/part2_jury_remark_registry.md",
    "reports": "reports/part8",
}

# -- the authorised scope of this dry run (decisions of 6 November 2026) -----------------

#: R1 corrections applied. F8 (F3.4 main-panel presentation) was raised for confirmation on
#: 2 November and never confirmed, so it is switched OFF: only authorised corrections apply.
CORRECTION_FLAGS = {"f1_failed_forecast_masking": True, "f2_guarded_mcs": True,
                    "f3_pairwise_orientation": True, "f4_zivot_andrews_reporting": True,
                    "f71_data_dictionary_decision": True, "f8_readable_main_panel": False}
DECISIONS = {
    "B1_staged": "approved as the selected implementation correction (not for publication)",
    "D1": ("approved for CANDIDATE integration in this dry run: both B2 MSAR chains under the "
           "approved live warm-start rule; their classification changes and optimiser "
           "sensitivities stay review items. Not scientific approval."),
    "D2": "approved: re-render every F4.8 whose underlying corrected table changes",
    "D3": "deferred: no publication destination; nothing is published",
    "F8": "not confirmed: switched off in this dry run",
}

APPROVAL_NOT_GRANTED = ("not granted: a completed or internally consistent computation is "
                        "not a scientifically approved result")


class IntegrationError(RuntimeError):
    """Any failed check: the dry run stops; nothing is assumed."""


# -- write boundary ----------------------------------------------------------------------

def inside(root: Path | str, path: Path | str) -> Path:
    """`path`, resolved, if it lies inside `root`; otherwise refuse."""
    root, path = Path(root).resolve(), Path(path).resolve()
    if path != root and root not in path.parents:
        raise IntegrationError(f"refusing to write outside the work folder: {path}")
    return path


def sha256_file(path: Path | str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_listing(root: Path | str, *, skip_dirs: Iterable[str] = (".git",)) -> dict[str, str]:
    """relative path -> sha256 of every file under `root` (a missing root lists empty)."""
    root = Path(root)
    out: dict[str, str] = {}
    if not root.exists():
        return out
    if root.is_file():
        return {root.name: sha256_file(root)}
    skip = set(skip_dirs)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in skip)
        for name in sorted(filenames):
            path = Path(dirpath) / name
            out[path.relative_to(root).as_posix()] = sha256_file(path)
    return out


def listing_digest(listing: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for name in sorted(listing):
        digest.update(f"{name} {listing[name]}\n".encode())
    return digest.hexdigest()


def protected_listing(paths: dict[str, Path | str]) -> dict[str, dict]:
    """name -> {path, files, digest} for every protected input (read before and after)."""
    out = {}
    for name, path in sorted(paths.items()):
        listing = tree_listing(path)
        out[name] = {"path": str(path), "files": len(listing), "digest": listing_digest(listing)}
    return out


def payload_digest(fits: Path | str) -> tuple[int, str]:
    """(payload count, digest) exactly as `r1_original_cache_audit.verify` computes it."""
    fits = Path(fits)
    digest, count = hashlib.sha256(), 0
    for path in sorted(fits.glob("*/*.json"), key=lambda p: p.relative_to(fits).as_posix()):
        digest.update(f"{path.relative_to(fits).as_posix()} {sha256_file(path)}\n".encode())
        count += 1
    return count, digest.hexdigest()


def write_json(path: Path | str, data) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, default=str, sort_keys=False), encoding="utf-8")
    os.replace(tmp, path)


def write_rows(path: Path | str, rows: list[dict], fields: list[str] | None = None) -> None:
    """CSV (gzip-compressed with mtime 0 when the name ends in .gz)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = []
        for row in rows:
            fields += [k for k in row if k not in fields]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields or ["empty"], extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    data = buffer.getvalue().encode("utf-8")
    if path.suffix == ".gz":
        with open(path, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as gz:
            gz.write(data)
    else:
        path.write_bytes(data)


def read_rows(path: Path | str) -> list[dict]:
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


# -- cell-level comparison of tables ---------------------------------------------------

PROVENANCE = {"run_id", "data_snapshot_hash", "code_commit_sha", "config_hash", "created_utc"}
RUNTIME = {"wall_seconds", "cpu_seconds", "peak_memory_mb", "recorded_utc"}
RECORD_COLUMNS = {"correction_status"}
RELATIVE_TOLERANCE = 1e-9          # the pinned compare's floating-point tolerance
ABSOLUTE_TOLERANCE = 1e-12
#: Columns whose change is a change of decision, classification or ranking.
DECISION_COLUMN = re.compile(
    r"(decision|^status$|_status$|^rank|in_mcs|excluded_from_mcs|conclusion|support|"
    r"rejected|^selected$|credib|is_model_failure|stars$|changed_by)", re.I)
KEY_COLUMNS = ("series", "model", "horizon", "loss", "model_a", "model_b", "benchmark",
               "competitor", "window_length", "state", "window", "turning_window_width",
               "confidence_level", "exercise", "role", "frequency", "transformation", "name",
               "refit_date", "status", "category", "reason_code", "path")
#: Tables to which rows are appended (the pinned reconcile aligns their first rows by position).
APPEND_TABLES = {"diagnostics/all_test_results.csv"}
ROW_KEYS = {
    "forecast_tests/T3.4_model_confidence_set.csv":
        ["series", "horizon", "loss", "confidence_level", "model"],
    "robustness/window_length_mcs.csv":
        ["series", "horizon", "loss", "confidence_level", "model", "window_length"],
    "diagnostics/T2.2_stationarity.csv": ["series", "name"],
}


def is_decision_column(column: str) -> bool:
    return column not in RECORD_COLUMNS and bool(DECISION_COLUMN.search(column))


def same_cell(a: str, b: str) -> bool:
    """Identical text, the same number printed differently, or equal within the pinned
    floating-point tolerance (rel 1e-9 / abs 1e-12)."""
    if a == b:
        return True
    try:
        x, y = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if x != x or y != y:
        return x != x and y != y
    diff = abs(x - y)
    return diff <= ABSOLUTE_TOLERANCE or diff <= RELATIVE_TOLERANCE * max(abs(x), abs(y))


def read_table(path: Path | str):
    import pandas as pd
    path = Path(path)
    if path.suffix == ".parquet":
        frame = pd.read_parquet(path)
        return frame.astype(object).where(frame.notna(), "").astype(str)
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def align_rows(a, b, relative: str) -> dict[int, int] | None:
    """b row -> a row for rows describing the same quantity; None when not alignable."""
    keys = ROW_KEYS.get(relative)
    if keys and all(k in a.columns and k in b.columns for k in keys):
        lookup: dict[str, list[int]] = {}
        for i, k in enumerate(a[keys].astype(str).agg("|".join, axis=1)):
            lookup.setdefault(k, []).append(i)
        mapping = {}
        for i, k in enumerate(b[keys].astype(str).agg("|".join, axis=1)):
            if lookup.get(k):
                mapping[i] = lookup[k].pop(0)
        return mapping
    if len(a) == len(b):
        return {i: i for i in range(len(b))}
    if relative in APPEND_TABLES and len(b) > len(a):
        return {i: i for i in range(len(a))}
    return None


def table_cell_changes(old: Path, new: Path, relative: str, *,
                       ignore: Iterable[str] = ()) -> dict:
    """Every cell of `new` that differs from `old` beyond the floating-point tolerance.

    Provenance, run-time and record columns are not compared. Returns {"alignable",
    "cells": [...], "rows_added", "rows_removed", "columns_added", "columns_removed"}.
    """
    a, b = read_table(old), read_table(new)
    skip = PROVENANCE | RUNTIME | RECORD_COLUMNS | set(ignore)
    out = {"alignable": True, "cells": [], "rows_old": len(a), "rows_new": len(b),
           "columns_added": [c for c in b.columns if c not in a.columns and c not in skip],
           "columns_removed": [c for c in a.columns if c not in b.columns and c not in skip]}
    mapping = align_rows(a, b, relative)
    if mapping is None:
        out["alignable"] = False
        return out
    out["rows_added"] = len(b) - len(mapping)
    out["rows_removed"] = len(a) - len(set(mapping.values()))
    out["added_rows"] = [i for i in range(len(b)) if i not in mapping]
    kept = set(mapping.values())
    out["removed_rows"] = [{"row": i, **{k: a.at[i, k] for k in a.columns if k not in PROVENANCE}}
                           for i in range(len(a)) if i not in kept]
    keys = [k for k in KEY_COLUMNS if k in b.columns]
    columns = [c for c in b.columns if c in a.columns and c not in skip]
    import numpy as np
    b_index = np.fromiter(mapping.keys(), dtype=np.int64, count=len(mapping))
    a_index = np.fromiter(mapping.values(), dtype=np.int64, count=len(mapping))
    for column in columns:
        av, bv = a[column].to_numpy()[a_index], b[column].to_numpy()[b_index]
        for j in np.nonzero(av != bv)[0]:
            ai, bi = int(a_index[j]), int(b_index[j])
            if not same_cell(av[j], bv[j]):
                out["cells"].append({"path": relative, "row": bi, "column": column,
                                     "old_row": ai, "old": av[j], "new": bv[j],
                                     "decision_like": is_decision_column(column),
                                     **{f"key_{k}": b.at[bi, k] for k in keys}})
    return out


def tree_files(root: Path | str) -> dict[str, Path]:
    root = Path(root)
    return {p.relative_to(root).as_posix(): p for p in root.rglob("*") if p.is_file()}


def tree_changes(old_root: Path | str, new_root: Path | str) -> tuple[list[dict], list[dict]]:
    """(file rows, cell rows) for every file that differs between two output trees."""
    old, new = tree_files(old_root), tree_files(new_root)
    files, cells = [], []
    for relative in sorted(set(old) | set(new)):
        if relative not in old or relative not in new:
            files.append({"path": relative, "status": "added" if relative in new else "removed"})
            continue
        if sha256_file(old[relative]) == sha256_file(new[relative]):
            continue
        row = {"path": relative, "status": "changed", "cells_changed": "",
               "decision_cells_changed": ""}
        if relative.endswith((".csv", ".parquet")):
            result = table_cell_changes(old[relative], new[relative], relative)
            if not result["alignable"]:
                row["status"] = "changed_rows_not_alignable"
            else:
                row["cells_changed"] = len(result["cells"])
                row["decision_cells_changed"] = sum(c["decision_like"] for c in result["cells"])
                row["columns_added"] = ";".join(result["columns_added"])
                row["columns_removed"] = ";".join(result["columns_removed"])
                if not result["cells"] and not result["columns_added"] and \
                        not result["columns_removed"] and not result.get("rows_added") and \
                        not result.get("rows_removed"):
                    row["status"] = "provenance_or_fp_only"
                cells.extend(c for c in result["cells"] if relative.endswith(".csv"))
        files.append(row)
    return files, cells


# -- read-only refit-cache replay and cache integrity ----------------------------------------

def readonly_refit_class():
    """The pinned `RefitCache`, made genuinely read-only for replay (orchestration only).

    Built on `r1_tierb.live_replay_class` (served payloads and the live warm-start state are
    exactly those of the live replay used before). Two pinned side effects are removed:

    * `RefitCache.__post_init__` writes `README_R1_REFIT_CACHE.txt` into the cache folder
      (and `FitCache.__post_init__` creates the folder if missing). Here the constructor only
      records the folder and refuses one that does not exist: nothing is written.
    * `put` stores a payload. Here it refuses: in a replay a write can only follow an
      estimation, which is itself refused.

    `get` and `path_for` are the pinned ones, unchanged.
    """
    import r1_tierb as tb
    from thesis.correction import rescore

    live = tb.live_replay_class(rescore.RefitCache)

    class ReadOnlyLiveReplayRefitCache(live):
        def __post_init__(self) -> None:
            self.directory = Path(self.directory)
            if not self.enabled or not self.directory.is_dir():
                raise IntegrationError(f"read-only replay: {self.directory} is not an existing "
                                       "enabled cache folder")

        def put(self, key, payload):
            raise IntegrationError(f"read-only replay: write to {self.directory} refused "
                                   f"({key.series} {key.model} {key.refit_date})")

    return ReadOnlyLiveReplayRefitCache


def readonly_refit_replay():
    """Context: the pinned workflow's `rescore.RefitCache` is the read-only live replay."""
    from contextlib import contextmanager
    from thesis.correction import rescore

    @contextmanager
    def patched():
        original = rescore.RefitCache
        rescore.RefitCache = readonly_refit_class()
        try:
            yield rescore.RefitCache
        finally:
            rescore.RefitCache = original
    return patched()


def listing_diff(before: dict[str, str], after: dict[str, str]) -> dict:
    """Every added, removed or modified file, with its sha256 values."""
    return {"added": [{"path": k, "sha256": after[k]} for k in sorted(after.keys() - before.keys())],
            "removed": [{"path": k, "sha256": before[k]} for k in sorted(before.keys() - after.keys())],
            "modified": [{"path": k, "sha256_before": before[k], "sha256_after": after[k]}
                         for k in sorted(before.keys() & after.keys()) if before[k] != after[k]]}


def save_listing(path: Path | str, listing: dict[str, str]) -> None:
    write_rows(path, [{"path": k, "sha256": v} for k, v in sorted(listing.items())],
               ["path", "sha256"])


def load_listing(path: Path | str) -> dict[str, str]:
    return {r["path"]: r["sha256"] for r in read_rows(path)}


def require_unchanged(name: str, root: Path | str, before: dict[str, str], when: str,
                      report: Path | str) -> dict:
    """Refuse unless the folder holds exactly `before`, byte for byte (strict: every file,
    including non-payload files). On a difference the full file-level diff is written to
    `report` before the run stops."""
    after = tree_listing(root)
    diff = listing_diff(before, after)
    record = {"name": name, "when": when, "files": len(after),
              "digest_before": listing_digest(before), "digest_after": listing_digest(after),
              "unchanged": not any(diff.values()), **diff}
    if not record["unchanged"]:
        write_json(report, record)
        raise IntegrationError(
            f"{name} changed {when}: {len(diff['added'])} added, {len(diff['removed'])} removed, "
            f"{len(diff['modified'])} modified (first: "
            f"{(diff['added'] + diff['removed'] + diff['modified'])[0]}); see {Path(report).name}")
    return {k: record[k] for k in ("name", "when", "files", "digest_after", "unchanged")}
