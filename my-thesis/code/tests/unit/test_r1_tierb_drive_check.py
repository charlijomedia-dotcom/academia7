"""The Drive checkpoint check: runs the real protocol in a disposable namespace only.

Here the "Drive" is a local folder; in Colab the same code runs on the mounted Drive
(notebook section 3b). No estimation anywhere.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

COLAB = Path(__file__).resolve().parents[3] / "colab"
sys.path.insert(0, str(COLAB))
import r1_tierb as tb  # noqa: E402
import r1_tierb_drive_check as dc  # noqa: E402


def _drive(tmp: Path) -> tuple[Path, list[Path]]:
    drive = tmp / "drive"
    base = drive / "baseline"
    (base / "r1_tier_a_checkpoint" / "x").mkdir(parents=True)
    (base / "r1_tier_a_checkpoint" / "x" / "refit_cache.tar.gz").write_bytes(b"tier a")
    (base / "r1_tierb_batches" / "B1" / "checkpoints").mkdir(parents=True)
    (base / "r1_tierb_batches" / "B1" / "checkpoints" / "keep.txt").write_text("b1")
    original = base / "fit_cache" / "3413465b508bb844"
    original.mkdir(parents=True)
    (original / "part-0001.tar.gz").write_bytes(b"original cache")
    return drive, [original]


def test_every_check_passes_and_only_the_check_folder_is_written(tmp_path):
    drive, extra = _drive(tmp_path)
    before = dc.snapshot([drive / "baseline"])
    report = dc.run(drive, "B1-20261104T000000Z-abc", protected_extra=extra)
    assert report["ok"], dc.summary(report)
    assert set(report["results"]) == {
        "1_checkpoint_creation", "2_archive_readback", "3_completed_checkpoint_promotion",
        "4_interrupted_write_recovery", "5_restore", "6_checksum_verification",
        "7_namespace_isolation"}
    assert report["results"]["3_completed_checkpoint_promotion"]["detail"][
        "protocol_relies_on_directory_rename"] is False
    after = dc.snapshot([drive / "baseline"])
    new = {k for k in after if k not in before}
    root = str(dc.check_root(drive, "B1-20261104T000000Z-abc"))
    assert new and all(k.startswith(root + "/") for k in new)        # nothing else written
    assert all(after[k] == v for k, v in before.items())               # nothing else changed
    assert (Path(root) / dc.REPORT).is_file()


def test_cross_runtime_verification_restores_the_same_payloads(tmp_path):
    drive, extra = _drive(tmp_path)
    dc.run(drive, "first-runtime", protected_extra=extra)
    assert dc.verify(drive, "first-runtime")["ok"]


def test_a_change_to_a_protected_namespace_fails_the_check(tmp_path, monkeypatch):
    drive, extra = _drive(tmp_path)
    real = tb.restore_checkpoints

    def meddling(*args, **kwargs):                       # something else writes meanwhile
        (extra[0] / "part-0002.tar.gz").write_bytes(b"x")
        return real(*args, **kwargs)
    monkeypatch.setattr(tb, "restore_checkpoints", meddling)
    report = dc.run(drive, "meddled", protected_extra=extra)
    assert not report["ok"]
    assert not report["results"]["7_namespace_isolation"]["ok"]
    assert "part-0002" in report["results"]["7_namespace_isolation"]["error"]


def test_a_broken_completion_step_is_reported_not_hidden(tmp_path, monkeypatch):
    drive, extra = _drive(tmp_path)
    monkeypatch.setattr(tb, "_marker", lambda folder: None)   # marker never readable
    report = dc.run(drive, "broken", protected_extra=extra)
    assert not report["ok"] and not report["results"]["1_checkpoint_creation"]["ok"]


def test_the_check_refuses_to_reuse_or_overlap_a_namespace(tmp_path):
    drive, extra = _drive(tmp_path)
    dc.run(drive, "once", protected_extra=extra)
    with pytest.raises(tb.TierBError, match="already exists"):
        dc.run(drive, "once", protected_extra=extra)
    for bad in ("", "../x", ".hidden"):
        with pytest.raises(tb.TierBError):
            dc.check_root(drive, bad)
