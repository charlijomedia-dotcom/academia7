#!/usr/bin/env python3
"""Before/after account of the R1 corrected release (file, cell and decision level).

Usage (from my-thesis/):
  python reports/part8/corrections/r1/r1_change_summary.py ORIGINAL_OUTPUT CORRECTED_RELEASE

Writes, next to this script:
  file_changes.csv      one row per file that differs, with the correction(s) and reason
  cell_changes.csv      every changed table cell (original text, corrected text, kind)
  decision_changes.csv  every changed test decision, significance mark, MCS membership
                        or support classification
Tables are compared as text with provenance and run-time columns removed
(thesis.correction.compare conventions); rows are aligned by position, or by key for
the MCS tables and T2.2, whose row count the corrections change.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "code" / "src"))

from thesis.correction.compare import (CORRECTION_COLUMNS, RUNTIME_COLUMNS,  # noqa: E402
                                       compare_trees)
from thesis.correction.workflow import ROW_KEYS  # noqa: E402
from thesis.core.provenance import PROVENANCE_COLUMNS  # noqa: E402

IGNORE = set(PROVENANCE_COLUMNS) | RUNTIME_COLUMNS | CORRECTION_COLUMNS

F1 = ("F1: forecasts from FAILED fits are excluded from scoring (raw value kept in "
      "failed_raw_forecast). The published UNRATE AR benchmark scored the UNSTABLE_AR "
      "forecasts of origin 2020-04 (31.6 / 93.4 / 304.2 / 2063.6 at h=1/3/6/12)")
F2 = ("F2: MCS cells where the arch implementation failed (ties, variance overflow) are "
      "computed with the guarded hln_mcs_r implementation of the same procedure "
      "(same loss, alpha, block length, replications, seed) instead of being reported as "
      "unavailable")
F3 = ("F3: pairwise tests are oriented competitor minus benchmark (AR, or ARMA when AR is "
      "not in the pair), with explicit benchmark/competitor columns; statistic and mean "
      "differential change sign and the one-sided p-values swap where the published "
      "orientation was benchmark minus competitor; two-sided p-values and decisions do not "
      "change through F3")
F4 = ("F4: Zivot-Andrews unit-root tests with one endogenous break are reported for the "
      "level of UNRATE and FEDFUNDS (initial window and full sample), as Part 5 §3.2 / P-02 "
      "requires; they do not enter the §3.4 transformation rule, which is unchanged")
F71 = ("F7.1: the data dictionary reports the transformation actually chosen by the §3.4 "
       "decision rule and the resulting sample dates, instead of the catalogue default")

RULES = [
    ("forecasts/forecasts_", [F1], "column failed_raw_forecast added; UNRATE AR 2020-04 "
                                   "forecasts set to missing"),
    ("forecasts/forecast_horizon_coverage", [F1], "finite-forecast counts exclude failed fits"),
    ("forecast_tests/T3.3A_", [F1, F3], ""),
    ("forecast_tests/T3.3B_", [F1, F3], ""),
    ("forecast_tests/T3.3_main", [F1], "UNRATE rows; HLZ statistics of other targets keep "
                                       "their published value"),
    ("forecast_tests/T3.4_", [F1, F2], ""),
    ("forecast_tests/T3.5_", [F1], "UNRATE rows"),
    ("forecast_tests/T3.6_", [F1], "UNRATE AR rows"),
    ("robustness/window_length_mcs", [F1, F2], "baseline window length only; other lengths "
                                               "retained (see correction_status)"),
    ("robustness/window_length_", [F1], "baseline window length only; other lengths "
                                        "retained (see correction_status)"),
    ("robustness/T4.1_", [F1], "UNRATE baseline-transformation rows; alternative-"
                               "transformation rows retained pending estimation"),
    ("robustness/T4.4_", [F1], "UNRATE rows"),
    ("robustness/T4.5_", [F1], "UNRATE rows of the published VAR comparison"),
    ("robustness/T4.TP1_", [F1], "UNRATE rows"),
    ("data_audit/T4.9_", [F1], "UNRATE rows"),
    ("data_audit/locf_forecast_exposure", [F1], "UNRATE AR rows of the failed origin"),
    ("data_audit/T2.1_", [F71], ""),
    ("diagnostics/T2.2_stationarity", [F4], "four Zivot-Andrews rows added"),
    ("diagnostics/T2.2_transformation_decisions", [F4], "Zivot-Andrews columns added"),
    ("diagnostics/all_test_results", [F4], "four Zivot-Andrews rows appended"),
    ("figures/F2.1_", [F4], "Zivot-Andrews break dates marked"),
    ("figures/F3.4_", [F1], "failed forecasts drawn as markers, not joined into the line"),
    ("figures/F3.5_UNRATE", [F1], ""),
    ("figures/F3.6_UNRATE", [F1], ""),
    ("manifests/correction_", [], "correction record (new)"),
    ("manifests/original_output_inventory", [], "copy of the original inventory (new)"),
    ("manifests/output_inventory", [], "inventory of the corrected release (source, sha256, original_sha256)"),
]


def _read(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        frame = pd.read_parquet(path)
        frame = frame.astype(object).where(frame.notna(), "").astype(str)
    else:
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    return frame


def _align(o: pd.DataFrame, c: pd.DataFrame, relative: str) -> list[tuple[int, int]]:
    keys = ROW_KEYS.get(relative)
    if keys is None:
        return [(i, i) for i in range(min(len(o), len(c)))]
    lookup: dict[str, list[int]] = {}
    for i, k in enumerate(o[keys].agg("|".join, axis=1)):
        lookup.setdefault(k, []).append(i)
    pairs = []
    for i, k in enumerate(c[keys].agg("|".join, axis=1)):
        if lookup.get(k):
            pairs.append((lookup[k].pop(0), i))
    return pairs


def _kind(a: str, b: str) -> str:
    try:
        x, y = float(a), float(b)
    except ValueError:
        return "text"
    if not (np.isfinite(x) and np.isfinite(y)):
        return "missing/non-finite"
    scale = max(abs(x), abs(y), 1e-300)
    if abs(x - y) / scale <= 1e-9:
        return "floating-point"
    if abs(x + y) / scale <= 1e-9:
        return "sign"
    return "value"


DECISION_COLUMNS = ("decision", "stars", "in_mcs", "support_change", "agrees_with_hlz",
                    "direction", "conclusion_vs_baseline")
CONTEXT = ("series", "role", "model", "model_a", "model_b", "benchmark", "competitor",
           "horizon", "loss", "confidence_level", "window_length")


def main(original: Path, release: Path) -> None:
    comparison = compare_trees(original, release)
    changed = comparison[comparison["status"] != "identical"].copy()
    cells, decisions = [], []
    for relative in changed["path"]:
        if not relative.endswith((".csv", ".parquet")) or relative.startswith("manifests/"):
            continue
        if not (original / relative).exists():
            continue
        o, c = _read(original / relative), _read(release / relative)
        for oi, ci in _align(o, c, relative):
            context = {k: c.at[ci, k] for k in CONTEXT if k in c.columns}
            for column in c.columns:
                if column in IGNORE or column not in o.columns:
                    continue
                a, b = o.at[oi, column], c.at[ci, column]
                if a == b:
                    continue
                kind = _kind(a, b)
                if relative.endswith(".csv"):
                    cells.append({"path": relative, "row": ci, **context, "column": column,
                                  "original": a, "corrected": b, "kind": kind})
                if any(token in column for token in DECISION_COLUMNS):
                    decisions.append({"path": relative, **context, "column": column,
                                      "original": a, "corrected": b})
    cells = pd.DataFrame(cells)
    rows = []
    for record in changed.itertuples():
        rule = next(((corrections, note) for prefix, corrections, note in RULES
                     if record.path.startswith(prefix)), None)
        corrections, note = rule if rule else ([], "UNEXPLAINED")
        mine = cells[cells["path"] == record.path] if len(cells) else cells
        rows.append({
            "path": record.path, "status": record.status,
            "corrections": "; ".join(c.split(":")[0] for c in corrections),
            "rows_original": getattr(record, "rows_original", ""),
            "rows_corrected": getattr(record, "rows_corrected", ""),
            "columns_added": getattr(record, "columns_added", ""),
            "cells_changed": len(mine),
            "series_with_value_changes": ";".join(sorted(set(
                mine.loc[mine["kind"].isin(["value", "missing/non-finite", "text"]),
                         "series"].dropna()))) if len(mine) and "series" in mine else "",
            "sign_only_cells": int((mine["kind"] == "sign").sum()) if len(mine) else 0,
            "note": note,
            "scientific_reason": " | ".join(corrections),
        })
    files = pd.DataFrame(rows)
    files.to_csv(HERE / "file_changes.csv", index=False)
    cells.to_csv(HERE / "cell_changes.csv", index=False)
    pd.DataFrame(decisions).to_csv(HERE / "decision_changes.csv", index=False)
    unexplained = files[files["note"] == "UNEXPLAINED"]
    print(json.dumps({"files_changed": len(files), "cells_changed": len(cells),
                      "decision_cells_changed": len(decisions),
                      "unexplained_files": unexplained["path"].tolist()}, indent=1))


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
