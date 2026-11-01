"""Orchestration of the R1 correction workflow (see `correction/rescore.py`).

`run(...)` builds a `PublishedRescorer`, runs every exercise that can be recomputed from
published forecasts (or from whole cached / approved chains), and writes the results to a
staging tree. Tables that can only be partly recomputed are merged into the original
table *in its original row order*: each recomputed group replaces exactly the original
rows of that group, and every retained row keeps the original provenance columns plus a
`correction_status` saying why it was kept.

`assemble(...)` builds the corrected release: a byte copy of the original output tree,
with the regenerated and merged files replacing their originals, plus the correction
manifest, the per-file before/after comparison and a fresh inventory.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from contextlib import nullcontext
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd

from ..core.config import load_config
from ..core.hashing import sha256_file
from ..core.paths import CONFIG_DIR, FROZEN_DIR, Namespace, OutputLayout
from ..core.provenance import PROVENANCE_COLUMNS, RunContext
from ..data.store import load_bundle
from ..pipeline import StageOutputs
from ..reporting import tables
from . import flags as correction_flags
from .compare import compare_trees
from .rescore import (ORIGINAL_COMMIT, ORIGINAL_RUN_ID, ChainUnavailable, PublishedRescorer,
                      summarise)

PENDING = "original_retained_pending_estimation"
UNAFFECTED = "original_retained_unaffected"


def _read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def merge_groups(original: pd.DataFrame, recomputed: pd.DataFrame, group: Sequence[str],
                 context, retained_status) -> pd.DataFrame:
    """Replace each recomputed group's original rows, in place; mark retained rows.

    `retained_status(row) -> str` classifies every row that was not replaced.
    """
    # Formatted by the same CSV writer as every pipeline table, then read back as text,
    # so a recomputed value prints exactly as the pipeline would have printed it.
    import io
    buffer = io.StringIO()
    context.stamp(recomputed).to_csv(buffer, index=False)
    buffer.seek(0)
    stamped = (pd.read_csv(buffer, dtype=str, keep_default_na=False) if len(recomputed)
               else pd.DataFrame(columns=list(original.columns)))
    stamped["correction_status"] = "recomputed_from_published"
    key = lambda frame: frame[list(group)].astype(str).agg("|".join, axis=1)  # noqa: E731
    new_keys = key(stamped) if len(stamped) else pd.Series(dtype=str)
    old_keys = key(original)
    # Where a recomputed group has as many rows as the original group, its rows take the
    # original rows' positions one for one (the pipeline emits them in the same order),
    # so an interleaved table keeps its order; otherwise the group is inserted whole at
    # its first original position.
    counts_old, counts_new = old_keys.value_counts(), new_keys.value_counts()
    taken: dict[str, int] = {}
    pieces, placed = [], set()
    for position, k in enumerate(old_keys):
        if k in counts_new.index:
            if counts_new[k] == counts_old[k]:
                i = taken.get(k, 0)
                pieces.append(stamped[new_keys == k].iloc[[i]])
                taken[k] = i + 1
            elif k not in placed:
                pieces.append(stamped[new_keys == k])
            placed.add(k)
            continue
        row = original.iloc[[position]].copy()
        row["correction_status"] = retained_status(row.iloc[0])
        pieces.append(row)
    for k in new_keys.unique():
        if k not in placed:
            pieces.append(stamped[new_keys == k])
    columns = list(original.columns) + [c for c in stamped.columns
                                        if c not in original.columns]
    merged = pd.concat(pieces, ignore_index=True, sort=False)
    return merged.reindex(columns=columns).fillna("")


def run(original: Path, staging: Path, *, legacy: bool, cache_root: Path | None = None,
        approved_estimation: Iterable[str] = ()) -> dict:
    """Run the R1 workflow into `staging` (an output-tree layout). Returns a summary."""
    config = load_config(names=("baseline", "series_catalog", "thresholds"),
                         config_dir=CONFIG_DIR)
    bundle = load_bundle(FROZEN_DIR, config)
    context = RunContext(namespace=Namespace.CORRECTION, config_hash=config.hash,
                         data_snapshot_hash=bundle.data_input_identity,
                         data_cutoff=config.get("samples.monthly_end"),
                         vintage_date=config.get("run.vintage_date"),
                         notes={"workflow": "R1 correction from published forecasts",
                                "original_run_id": ORIGINAL_RUN_ID,
                                "original_results_commit": ORIGINAL_COMMIT,
                                "mode": "legacy-validation" if legacy else "corrected",
                                "corrections": ("none (legacy validation)" if legacy
                                                else "F1, F2, F3, F4, F7.1")})
    scratch = Path(tempfile.mkdtemp(prefix="r1_cache_"))
    layout = OutputLayout(root=Path(staging), cache=Path(cache_root) if cache_root else scratch)
    switches = correction_flags.legacy() if legacy else nullcontext()
    with switches:
        rescorer = PublishedRescorer(config, context, layout, bundle, original=original,
                                     approved_estimation=approved_estimation,
                                     use_cache=cache_root is not None)
        layout.create()
        rescorer.prepare_data()
        rescorer.stationarity_stage()
        rescorer.load_specifications()
        rescorer.load_baseline_chains()
        rescorer.write_forecast_files()
        rescorer.evaluation_stage()
        merged = _robustness(rescorer, original, staging, context)
        za_tests = [t for t in rescorer.all_tests
                    if t.name.startswith("Zivot-Andrews") and "not used by the §3.4" in t.name]
        if za_tests:
            base = _read(original / "diagnostics" / "all_test_results.csv")
            added = context.stamp(tables.test_table(za_tests)).astype(str)
            out = pd.concat([base, added], ignore_index=True, sort=False).fillna("")
            target = Path(staging) / "diagnostics" / "all_test_results.csv"
            out.to_csv(target, index=False)
            merged.append("diagnostics/all_test_results.csv")
    files = {f for s in rescorer.stage_outputs for f in s.files} | set(merged)
    # binary twins written next to a table (forecasts_*.parquet, ...) travel with it
    files |= {str(Path(f).with_suffix(".parquet")) for f in files if f.endswith(".csv")
              and (Path(staging) / f).with_suffix(".parquet").exists()}
    files = sorted(files)
    summary = {"run_id": context.run_id, "legacy": legacy, "regenerated_files": files,
               "merged_files": sorted(set(merged)), **summarise(rescorer.record),
               "flags": correction_flags.ACTIVE.as_dict() if not legacy else "all off"}
    (Path(staging) / "r1_summary.json").write_text(json.dumps(summary, indent=2, default=str),
                                                   encoding="utf-8")
    context.write_run_manifest(layout)
    return summary


def _robustness(r: PublishedRescorer, original: Path, staging: Path, context) -> list[str]:
    """Every robustness exercise the corrections can affect; returns merged file paths."""
    stage = StageOutputs("robustness")
    benchmark = str(r.config.get("evaluation.benchmark"))
    merged: list[str] = []
    rob = Path(staging) / "robustness"
    rob.mkdir(parents=True, exist_ok=True)

    # T4.1 -- per series; an unavailable alternative chain keeps the original rows.
    rows, tests, partial = [], [], False
    applies = [s for s in r.config.get("robustness.transformation.applies_to") if s in r.targets]
    for series_id in applies:
        try:
            produced = r._t41_series(series_id, benchmark)
        except ChainUnavailable as exc:
            partial = True
            r.record.retained.append({"exercise": "T4.1", "series": series_id,
                                      "missing_chains": exc.task_ids})
            produced = _t41_baseline_only(r, series_id, benchmark)
        if produced is not None:
            rows.extend(produced[0])
            tests.extend(produced[1])
    if partial:
        for name, frame, group in (("T4.1_transformation_robustness.csv", rows,
                                    ("series", "role")),
                                   ("T4.1_transformation_predictive_tests.csv", tests,
                                    ("series", "role"))):
            out = merge_groups(_read(original / "robustness" / name), pd.DataFrame(frame),
                               group, context, lambda row: PENDING)
            out.to_csv(rob / name, index=False)
            merged.append(f"robustness/{name}")
    else:
        r._write(pd.DataFrame(rows), r.layout.robustness,
                 "T4.1_transformation_robustness.csv", stage)
        r._write(pd.DataFrame(tests), r.layout.robustness,
                 "T4.1_transformation_predictive_tests.csv", stage)

    # T4.2 -- all four CPI AR-lag chains share one common date set: all or nothing.
    try:
        r._t42_cpi_lags(stage, benchmark)
    except ChainUnavailable as exc:
        r.record.retained.append({"exercise": "T4.2", "series": "CPIAUCSL",
                                  "missing_chains": exc.task_ids})
        for name in ("T4.2_cpi_lag_robustness.csv", "T4.2_cpi_lag_predictive_tests.csv"):
            out = _read(original / "robustness" / name).assign(correction_status=PENDING)
            out.to_csv(rob / name, index=False)
            merged.append(f"robustness/{name}")

    r._t44_horizons(stage, benchmark)
    _t45_from_published(r, original, stage, benchmark)

    # T4.8 -- per series; without the non-baseline chains only the baseline length is
    # rescored and the other lengths are retained (unaffected or pending, see below).
    audit = pd.read_csv(original / "robustness" / "window_length_origin_audit.csv")
    parts = {k: [] for k in ("comparison", "tests", "audit", "mcs")}
    partial_series: list[str] = []
    for series_id in r._selected_targets():
        try:
            produced = r._t48_series(series_id, stage, benchmark)
        except ChainUnavailable as exc:
            r.record.retained.append({"exercise": "T4.8", "series": series_id,
                                      "missing_chains": exc.task_ids})
            partial_series.append(series_id)
            produced = r._t48_series(series_id, stage, benchmark, lengths_to_score=[],
                                     make_figure=False)
        if produced is None:
            continue
        for key, part in zip(parts, produced):
            parts[key].extend(part)
    outputs = r.config.require("robustness.window_lengths")["outputs"]
    names = {"comparison": str(outputs["comparison"]),
             "tests": str(outputs["predictive_tests"]),
             "audit": str(outputs["origin_audit"]), "mcs": "window_length_mcs.csv"}
    if partial_series:
        baseline_changed = _baseline_length_changed(r, original, parts, names)
        failed_ar = {(row.series, int(row.window_length)) for row in audit.itertuples()
                     if row.model == "AR" and int(row.n_failed) > 0}

        def status(row) -> str:
            series_id = row["series"]
            if series_id not in partial_series:
                return UNAFFECTED
            if series_id in baseline_changed or (series_id, int(float(row["window_length"]))) \
                    in failed_ar:
                return PENDING
            return UNAFFECTED

        for key, name in names.items():
            out = merge_groups(_read(original / "robustness" / name), pd.DataFrame(parts[key]),
                               ("series", "window_length"), context, status)
            out.to_csv(rob / name, index=False)
            merged.append(f"robustness/{name}")
    else:
        for key, name in names.items():
            r._write(pd.DataFrame(parts[key]), r.layout.robustness, name, stage)

    r._t49_locf_exposure(stage)
    r.stage_outputs.append(stage)
    return merged


def _t41_baseline_only(r: PublishedRescorer, series_id: str, benchmark: str):
    """The baseline-transformation rows of T4.1, which need only published forecasts.

    Mirrors the baseline part of `Pipeline._t41_series` (accuracy rows and level-space
    rows); validated against the original rows by the legacy run.
    """
    import numpy as np
    from ..evaluation import metrics

    inputs = r._t41_inputs(series_id)
    if inputs is None:
        return None
    horizon, level = inputs["horizon"], inputs["level"]
    baseline_kind = inputs["baseline_kind"]
    baseline_frames = r._horse_race(series_id, horizon)
    extra = {"series_frequency": inputs["frequency"], "baseline_transformation": baseline_kind,
             "exercise": "T4.1 transformation robustness"}
    rows = r._accuracy_rows(baseline_frames, benchmark, series_id, horizon,
                            {**extra, "transformation": baseline_kind, "role": "baseline",
                             "units": r._units(series_id)})
    if r.config.get("robustness.transformation.report_level_errors", True):
        for model, frame in baseline_frames.items():
            indexed = frame.set_index("target_date")
            if baseline_kind == "difference":
                level_forecast = level.shift(1).reindex(indexed.index) + indexed["forecast"]
            else:
                level_forecast = indexed["forecast"]
            error = (level.reindex(indexed.index) - level_forecast).to_numpy(dtype=float)
            rows.append({"series": series_id, "model": model, "horizon": horizon,
                         "exercise": "T4.1 transformation robustness",
                         "role": "baseline_in_level_units", "transformation": baseline_kind,
                         "units": "percent (level space)", "n": int(np.isfinite(error).sum()),
                         "rmse": metrics.rmse(error), "mae": metrics.mae(error)})
    return rows, []


def _baseline_length_changed(r, original: Path, parts: dict, names: dict) -> set[str]:
    """Series whose recomputed baseline-length T4.8 rows differ from the original."""
    from .compare import compare_file

    changed = set()
    with tempfile.TemporaryDirectory() as tmp:
        # Only the predictive tests feed the classification of the other window lengths
        # (their verdict is relative to the baseline length's differential and support).
        for key, name in (("tests", names["tests"]),):
            new = pd.DataFrame(parts[key])
            if new.empty:
                continue
            old = pd.read_csv(original / "robustness" / name, dtype=str, keep_default_na=False)
            for series_id in new["series"].unique():
                lengths = set(new[new["series"] == series_id]["window_length"].astype(int))
                a = old[(old["series"] == series_id)
                        & old["window_length"].astype(float).astype(int).isin(lengths)]
                b = r.context.stamp(new[new["series"] == series_id])
                pa, pb = Path(tmp) / "a.csv", Path(tmp) / "b.csv"
                a.to_csv(pa, index=False)
                b.to_csv(pb, index=False)
                if not compare_file(pa, pb)["identical"]:
                    changed.add(series_id)
    return changed


def _t45_from_published(r: PublishedRescorer, original: Path, stage, benchmark: str) -> None:
    """T4.5 comparison from the published VAR forecasts (no VAR re-estimation)."""
    var = pd.read_csv(original / "robustness" / "T4.5_var_forecasts.csv")
    var = var.drop(columns=[c for c in PROVENANCE_COLUMNS if c in var.columns])
    for column in ("origin_date", "target_date"):
        var[column] = pd.to_datetime(var[column])
    var["reason_codes"] = var["reason_codes"].fillna("")
    selection = pd.read_csv(original / "robustness" / "T4.5_var_selection.csv")
    comparison = pd.read_csv(original / "robustness" / "T4.5_var_comparison.csv")
    best = int(selection[selection["selected"].astype(str) == "True"]["candidate_lag"].iloc[0])
    first = comparison.iloc[0]
    names = list(r._var_panel(record=False).columns)
    horizon = int(r.config.get("forecasting.horizons.primary.M"))
    rows, tests = r._t45_compare(var, names, best, bool(first["var_stability_required"]),
                                 int(first["var_unstable_origins"]),
                                 int(first["var_attempted_origins"]), horizon, benchmark)
    r._write(pd.DataFrame(rows), r.layout.robustness, "T4.5_var_comparison.csv", stage)
    r._write(pd.DataFrame(tests), r.layout.robustness, "T4.5_var_predictive_tests.csv", stage)


# -- assembling the corrected release -------------------------------------------------

#: Files in the staging tree that are workflow records, not outputs.
WORKFLOW_FILES = {"r1_summary.json", "manifests/run_manifest.json"}


def assemble(original: Path, staging: Path, release: Path, summary: dict) -> pd.DataFrame:
    """Original tree + regenerated files -> `release`; returns the per-file comparison."""
    if release.exists():
        shutil.rmtree(release)
    shutil.copytree(original, release)
    regenerated = [f for f in summary["regenerated_files"] if f not in WORKFLOW_FILES]
    for relative in regenerated:
        source = Path(staging) / relative
        target = release / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        sidecar = source.with_suffix(source.suffix + ".provenance.json")
        if sidecar.exists():
            shutil.copy2(sidecar, target.with_suffix(target.suffix + ".provenance.json"))
    manifests = release / "manifests"
    shutil.copy2(Path(staging) / "manifests" / "run_manifest.json",
                 manifests / "correction_run_manifest.json")
    shutil.copy2(Path(staging) / "r1_summary.json", manifests / "correction_summary.json")
    comparison = compare_trees(original, release)
    comparison["regenerated_by_r1"] = comparison["path"].isin(set(regenerated))
    comparison.to_csv(manifests / "correction_file_comparison.csv", index=False)
    inventory = []
    for path in sorted(p for p in release.rglob("*") if p.is_file()):
        relative = path.relative_to(release).as_posix()
        if relative == "manifests/output_inventory.csv":
            continue
        origin = original / relative
        inventory.append({
            "path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path),
            "source": ("regenerated_r1" if relative in set(regenerated) else
                       "correction_record" if relative.startswith("manifests/correction_") else
                       "original_unchanged"),
            "original_sha256": sha256_file(origin) if origin.exists() else "",
        })
    original_inventory = original / "manifests" / "output_inventory.csv"
    shutil.copy2(original_inventory, manifests / "original_output_inventory.csv")
    pd.DataFrame(inventory).to_csv(manifests / "output_inventory.csv", index=False)
    return comparison


# -- reconciliation: unaffected cells keep the original published text ---------------

#: Row keys for tables whose row count a correction can change (e.g. an MCS cell that
#: was "unavailable" in one row becomes four model rows). Other tables align by position.
ROW_KEYS = {
    "forecast_tests/T3.4_model_confidence_set.csv":
        ["series", "horizon", "loss", "confidence_level", "model"],
    "robustness/window_length_mcs.csv":
        ["series", "horizon", "loss", "confidence_level", "model", "window_length"],
    "diagnostics/T2.2_stationarity.csv": ["series", "name"],
}
_SKIP = set(PROVENANCE_COLUMNS) | {"correction_status"}


def _match_rows(legacy: pd.DataFrame, corrected: pd.DataFrame, relative: str) -> dict[int, int]:
    """corrected row index -> legacy row index for rows describing the same quantity."""
    if len(legacy) == len(corrected) and relative not in ROW_KEYS:
        return {i: i for i in range(len(corrected))}
    keys = ROW_KEYS.get(relative)
    if keys is None:                      # rows appended at the end (all_test_results)
        return {i: i for i in range(min(len(legacy), len(corrected)))}
    lookup: dict[str, list[int]] = {}
    for i, k in enumerate(legacy[keys].agg("|".join, axis=1)):
        lookup.setdefault(k, []).append(i)
    mapping = {}
    for i, k in enumerate(corrected[keys].agg("|".join, axis=1)):
        if lookup.get(k):
            mapping[i] = lookup[k].pop(0)
    return mapping


def reconcile(original: Path, legacy: Path, corrected: Path, files: Sequence[str]) -> pd.DataFrame:
    """Restore the original printed value in every cell the corrections did not change.

    The legacy run (corrections off) and the corrected run are produced by the same code
    on the same machine. A cell whose text is identical in both was not touched by any
    correction, so the value the original publication printed is kept there; a cell that
    differs between legacy and corrected runs was changed by a correction and keeps the
    corrected value. This removes platform-level last-digit noise (a different CPU/BLAS
    than the original Colab run) from every unaffected number. The legacy run itself
    must first have reproduced the original (identical or within 1e-9 relative).
    Returns a per-file account of how many cells were restored and how many changed.
    """
    rows = []
    for relative in files:
        if not relative.endswith(".csv"):
            continue
        paths = [original / relative, legacy / relative, corrected / relative]
        if not all(p.exists() for p in paths):
            continue
        o, l, c = (pd.read_csv(p, dtype=str, keep_default_na=False) for p in paths)
        if len(o) != len(l):
            rows.append({"path": relative, "reconciled": False,
                         "reason": "legacy run does not align with the original"})
            continue
        mapping = _match_rows(l, c, relative)
        restored = changed = 0
        for column in c.columns:
            if column in _SKIP or column not in l.columns or column not in o.columns:
                continue
            for ci, li in mapping.items():
                if _same_value(c.at[ci, column], l.at[li, column]):
                    if c.at[ci, column] != o.at[li, column]:
                        c.at[ci, column] = o.at[li, column]
                        restored += 1
                else:
                    changed += 1
        _match_integer_format(c, l, [i for i in range(len(c)) if i not in mapping])
        c.to_csv(corrected / relative, index=False)
        rows.append({"path": relative, "reconciled": True, "cells_restored_to_original": restored,
                     "cells_changed_by_corrections": changed,
                     "rows_without_legacy_counterpart": len(c) - len(mapping)})
    return pd.DataFrame(rows)


def _same_value(a: str, b: str) -> bool:
    """Identical text, or the same number printed differently ("0" and "0.0": a column
    that held a missing value in one run and none in the other changes dtype)."""
    if a == b:
        return True
    try:
        return float(a) == float(b)
    except ValueError:
        return False


def _match_integer_format(corrected: pd.DataFrame, legacy: pd.DataFrame, new_rows) -> None:
    """New rows print whole numbers the way the column already does ("4.0", not "4")."""
    for column in corrected.columns:
        if column in _SKIP or column not in legacy.columns:
            continue
        filled = legacy[column][legacy[column] != ""]
        if filled.empty or not filled.str.fullmatch(r"-?\d+\.0").all():
            continue
        for i in new_rows:
            if corrected.at[i, column].lstrip("-").isdigit():
                corrected.at[i, column] += ".0"
