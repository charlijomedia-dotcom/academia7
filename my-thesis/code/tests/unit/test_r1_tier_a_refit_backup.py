"""The Tier A refit-cache backup cell: dry run by default, verified copy, never fit_cache."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

COLAB = Path(__file__).resolve().parents[3] / "colab"
CELL = (COLAB / "r1_backup_tier_a_refit_cache.py").read_text()


def _thesis_colab():
    spec = importlib.util.spec_from_file_location("thesis_colab", COLAB / "thesis_colab.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fits(work: Path, n: int = 5, marked: bool = True) -> Path:
    fits = work / "refit_cache" / "fits"
    for i in range(n):
        path = fits / f"{i:02d}" / f"{i:064d}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"forecasts": {"1": float(i)}}
        if marked:
            payload["r1_provenance"] = "re-estimated"
        path.write_text(json.dumps(payload))
    return fits


def _run(work, drive, **extra):
    namespace = {"WORK_DIR": work, "DRIVE_ROOT": drive, "tc": _thesis_colab(), **extra}
    exec(compile(CELL, "backup", "exec"), namespace)
    return namespace


def test_dry_run_by_default_writes_nothing(tmp_path):
    _fits(tmp_path / "work")
    ns = _run(tmp_path / "work", tmp_path / "drive")
    assert ns["TIER_A_REFIT_BACKUP"]["status"] == "dry-run"
    assert ns["TIER_A_REFIT_BACKUP"]["payloads"] == 5
    assert not (tmp_path / "drive").exists()


def test_backup_is_verified_by_restoring_and_never_under_fit_cache(tmp_path):
    _fits(tmp_path / "work")
    ns = _run(tmp_path / "work", tmp_path / "drive", DO_BACKUP=True)
    report = ns["TIER_A_REFIT_BACKUP"]
    assert report["status"] == "backed-up" and report["mismatched"] == []
    destination = Path(report["destination"])
    assert destination.parent.parent.name == "r1_refit_cache"
    assert "fit_cache" not in destination.parts
    assert len(json.loads((destination / "inventory_sha256.json").read_text())) == 5


def test_unmarked_payloads_are_refused(tmp_path):
    _fits(tmp_path / "work", marked=False)
    with pytest.raises(RuntimeError, match="refit marker"):
        _run(tmp_path / "work", tmp_path / "drive", DO_BACKUP=True)
    assert not (tmp_path / "drive").exists()


def test_absent_cache_is_reported_not_raised(tmp_path):
    ns = _run(tmp_path / "work", tmp_path / "drive", DO_BACKUP=True)
    assert ns["TIER_A_REFIT_BACKUP"]["status"] == "absent"
