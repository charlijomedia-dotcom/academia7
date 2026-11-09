"""Render F3.4 from a Part 8 candidate tree with the pinned plotting code, F8 off and on.

Usage: python f8_render.py CANDIDATE_RELEASE ARCHIVE_INVENTORY OUT_DIR

Presentation only. It reads the candidate's stored forecasts (forecasts/*.parquet) and its
transformation decisions; it estimates nothing, scores nothing and writes nothing into the
candidate. For each target it reproduces the pipeline's F3.4 call (pipeline.py, evaluation
stage, "figures" block) line for line:

  legacy/  F8 off: must reproduce the archived F3.4 PNG and PDF byte for byte (the check
           that the inputs and the renderer are the archived ones);
  f8/      F8 on (`f8_readable_main_panel`): the review figures.

The plotting function is `thesis.reporting.figures.actual_vs_forecast`, unchanged since
the scientific pin 8aaa4217 (verified by the caller with `git diff`).
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

CODE = Path(__file__).resolve().parents[5] / "code"
COLAB = CODE.parent / "colab"
sys.path.insert(0, str(CODE / "src"))
sys.path.insert(0, str(COLAB))
import r1_render_guard  # noqa: E402  (must precede the first matplotlib import)

r1_render_guard.pin_default_rc()

from thesis.core.config import load_config  # noqa: E402
from thesis.core.paths import CONFIG_DIR, FROZEN_DIR  # noqa: E402
from thesis.core.schemas import Status  # noqa: E402
from thesis.correction import flags as correction_flags  # noqa: E402
from thesis.data.canonical import to_panels  # noqa: E402
from thesis.data.store import load_bundle  # noqa: E402
from thesis.evaluation.scoring import FAILED_RAW_FORECAST  # noqa: E402
from thesis.models.registry import AR, ARMA, MSAR, STAR  # noqa: E402
from thesis.reporting import figures  # noqa: E402

TARGETS = ("GDPC1", "CPIAUCSL", "UNRATE", "INDPRO", "FEDFUNDS", "M2SL")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def units(config, decisions: dict, series_id: str) -> str:          # = Pipeline._units
    spec = config.get(f"targets.{series_id}")
    if spec["transform"]["kind"] == "logdiff_annualized":
        return "annualized percent"
    if decisions.get(series_id) == "difference":
        return "percentage-point change"
    return "percent"


def inputs(release: Path, series_id: str, config):
    frequency = config.get(f"targets.{series_id}")["frequency"]
    horizon = int(config.get(f"forecasting.horizons.primary.{frequency}"))   # = min(_horizons)
    window = int(config.get(f"forecasting.windows.{frequency}"))
    fc = pd.read_parquet(release / "forecasts" / f"forecasts_{series_id}.parquet")
    fc = fc[(fc["window_length"] == window) & (fc["horizon"] == horizon)]
    frames = {}
    for model in (AR, ARMA, MSAR, STAR):                                # = _horse_race
        subset = fc[fc["model"] == model]
        if not subset.empty:
            frames[model] = subset
    actual = frames[AR].set_index("target_date")["actual"]
    series_forecasts, flagged, failed_points = {}, {}, {}
    for model, frame in frames.items():                                 # = pipeline F3.4 block
        indexed = frame.set_index("target_date")
        series_forecasts[model] = indexed["forecast"]
        failed_fit = indexed["status"] == Status.FAILED.value
        shown = indexed["forecast"].where(~failed_fit,
                                          indexed.get(FAILED_RAW_FORECAST, indexed["forecast"]))
        extreme = indexed["reason_codes"].str.contains("EXTREME_FORECAST", na=False)
        raw_failed = shown[failed_fit].dropna()
        if not raw_failed.empty:
            failed_points[model] = raw_failed
        bad = shown[extreme & ~failed_fit]
        if not bad.empty:
            flagged[model] = bad
    return actual, series_forecasts, flagged, failed_points, horizon


def main(release, archive_inventory, out) -> int:
    release, out = Path(release), Path(out)
    render = r1_render_guard.check_default_rendering("3.11.2")   # DejaVu Sans, default rc
    archived = {r["path"]: r["sha256"] for r in csv.DictReader(open(archive_inventory))}
    config = load_config(names=("baseline", "series_catalog", "thresholds"), config_dir=CONFIG_DIR)
    bundle = load_bundle(FROZEN_DIR, config)
    usrec = to_panels(bundle.frame)["M"]["USREC"].dropna()
    decisions = {r["series_id"]: r["baseline_transformation"]
                 for r in csv.DictReader(open(release / "diagnostics/T2.2_transformation_decisions.csv"))}
    report = {"release": str(release), "render_guard": render, "targets": {}}
    for series_id in TARGETS:
        actual, fcs, flagged, failed, horizon = inputs(release, series_id, config)
        entry = {"horizon": horizon,
                 "flagged": {m: int(len(s)) for m, s in flagged.items()},
                 "failed": {m: int(len(s)) for m, s in failed.items()},
                 "flagged_max_abs": {m: float(s.abs().max()) for m, s in flagged.items()},
                 "failed_values": {m: {str(k.date()): float(v) for k, v in s.items()}
                                   for m, s in failed.items()},
                 "actual_max_abs": float(actual.abs().max()), "files": {}}
        for mode, on in (("legacy", False), ("f8", True)):
            with correction_flags.configured(f8_readable_main_panel=on):
                fig = figures.actual_vs_forecast(actual, fcs, usrec, series_id=series_id,
                                                 units=units(config, decisions, series_id),
                                                 flagged=flagged or None, failed=failed or None)
                written = figures.save(fig, out / mode / f"F3.4_{series_id}")
            for path in written:
                rel = f"figures/{path.name}"
                entry["files"][f"{mode}/{path.name}"] = {
                    "sha256": sha(path), "archived_sha256": archived.get(rel),
                    "equals_archived": sha(path) == archived.get(rel)}
        report["targets"][series_id] = entry
    (out / "render_report.json").write_text(json.dumps(report, indent=1))
    legacy_ok = all(v["equals_archived"] for e in report["targets"].values()
                    for k, v in e["files"].items() if k.startswith("legacy/"))
    print("legacy reproduces the archived F3.4 byte for byte:", legacy_ok)
    return 0 if legacy_ok else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
