"""R1 Tier B checkpoints: committed only when verified; interruptions never damage history."""

from __future__ import annotations

import json
import sys
import tarfile
import threading
from pathlib import Path

import pytest

COLAB = Path(__file__).resolve().parents[3] / "colab"
sys.path.insert(0, str(COLAB))
import r1_tierb as tb  # noqa: E402


def _payload(fits: Path, i: int, *, marked: bool = True, value: float | None = None) -> str:
    name = f"{i % 256:02x}/{i:064x}.json"
    path = fits / name
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"forecasts": {"1": float(i if value is None else value)}, "status": "adequate"}
    if marked:
        data[tb.MARKER] = tb.MARKER_VALUE
    path.write_text(json.dumps(data))
    return name


def _commit(local, task_dir, session="S1", **kw):
    return tb.commit_checkpoint(local, task_dir, task="T", session=session, **kw)


def test_partition_is_exactly_the_nine_chains():
    info = tb.validate_partition()
    assert info["origins_by_batch"] == {"B1": 644, "B2": 1390, "B3": 4007}
    assert sum(info["origins_by_batch"].values()) == 6041
    assert sorted(info["tasks"]) == sorted(tb.TIER_B_CHAINS) and len(info["tasks"]) == 9
    assert info["cpu_hours_by_batch"] == {"B1": 17.87, "B2": 15.93, "B3": 15.62}
    assert not any("MSAR3" in t for t in info["tasks"])


def test_commit_restore_round_trip_is_incremental(tmp_path):
    local, drive = tmp_path / "local", tmp_path / "drive" / "T"
    for i in range(3):
        _payload(local, i)
    first = _commit(local, drive)
    assert first["sequence"] == 1 and len(first["members"]) == 3 and first["parent"] is None
    assert _commit(local, drive) is None                       # nothing new
    for i in range(3, 5):
        _payload(local, i)
    second = _commit(local, drive)
    assert second["parent"] == first["checkpoint_id"] and len(second["members"]) == 2
    report = tb.restore_checkpoints(drive, tmp_path / "fresh")
    assert report["payloads"] == 5 and report["checkpoints"] == 2
    assert tb.inventory(tmp_path / "fresh") == tb.inventory(local)


def test_tmp_files_of_a_payload_being_written_are_never_committed(tmp_path):
    local, drive = tmp_path / "local", tmp_path / "drive" / "T"
    _payload(local, 1)
    (local / "01" / ("f" * 64 + ".tmp")).write_text("half written")
    manifest = _commit(local, drive)
    assert list(manifest["members"]) == [f"01/{1:064x}.json"]


def test_interrupted_backup_preserves_the_previous_verified_checkpoint(tmp_path):
    local, drive = tmp_path / "local", tmp_path / "drive" / "T"
    for i in range(3):
        _payload(local, i)
    first = _commit(local, drive)
    for i in range(3, 6):
        _payload(local, i)
    with pytest.raises(OSError, match="simulated"):
        _commit(local, drive, _fail_after_archive=True)
    assert len(list(drive.glob("*.partial"))) == 1              # the abandoned write
    history = tb.committed_checkpoints(drive)
    assert [m["checkpoint_id"] for _, m in history] == [first["checkpoint_id"]]
    restored = tb.restore_checkpoints(drive, tmp_path / "after_crash")
    assert restored["payloads"] == 3 and restored["ignored_partial_writes"]
    retry = _commit(local, drive)                                # next commit carries them
    assert len(retry["members"]) == 3 and retry["parent"] == first["checkpoint_id"]
    assert tb.restore_checkpoints(drive, tmp_path / "final")["payloads"] == 6


def test_corrupted_archive_is_detected(tmp_path):
    local, drive = tmp_path / "local", tmp_path / "drive" / "T"
    _payload(local, 1)
    manifest = _commit(local, drive)
    archive = drive / manifest["checkpoint_id"] / "payloads.tar.gz"
    data = bytearray(archive.read_bytes())
    data[len(data) // 2] ^= 0xFF
    archive.write_bytes(bytes(data))
    with pytest.raises(tb.TierBError, match="sha256"):
        tb.restore_checkpoints(drive, tmp_path / "fresh")


def test_missing_archive_is_detected(tmp_path):
    local, drive = tmp_path / "local", tmp_path / "drive" / "T"
    _payload(local, 1)
    manifest = _commit(local, drive)
    (drive / manifest["checkpoint_id"] / "payloads.tar.gz").unlink()
    with pytest.raises(tb.TierBError):
        tb.committed_checkpoints(drive)


def test_conflicting_payload_across_checkpoints_is_refused(tmp_path):
    local, drive = tmp_path / "local", tmp_path / "drive" / "T"
    name = _payload(local, 1)
    _commit(local, drive)
    _payload(local, 1, value=99.0)                               # same key, other content
    with pytest.raises(tb.TierBError, match="differ from committed"):
        _commit(local, drive)


def test_forked_history_from_two_sessions_is_refused(tmp_path):
    drive = tmp_path / "drive" / "T"
    a, b = tmp_path / "a", tmp_path / "b"
    _payload(a, 1)
    _payload(b, 2)
    _commit(a, drive, session="SA")
    # a second session that started from the same (empty) history: simulate by committing
    # into a copy and moving its checkpoint next to the first one
    other = tmp_path / "other" / "T"
    moved = _commit(b, other, session="SB")
    (other / moved["checkpoint_id"]).rename(drive / moved["checkpoint_id"])
    with pytest.raises(tb.TierBError, match="forked"):
        tb.committed_checkpoints(drive)


def test_improperly_marked_payload_is_never_committed(tmp_path):
    local, drive = tmp_path / "local", tmp_path / "drive" / "T"
    _payload(local, 1, marked=False)
    with pytest.raises(tb.TierBError, match="marker"):
        _commit(local, drive)
    assert not drive.exists() or not any(drive.iterdir())


def test_unsafe_archive_members_are_refused(tmp_path):
    archive = tmp_path / "evil.tar.gz"
    with tarfile.open(archive, "w:gz") as handle:
        info = tarfile.TarInfo("../escape.json")
        handle.addfile(info, fileobj=None)
    with tarfile.open(archive) as handle, pytest.raises(tb.TierBError, match="unsafe"):
        tb._safe_members(handle)


def test_concurrent_batches_and_chains_never_collide(tmp_path):
    drive_root = tmp_path / "drive"
    errors, results = [], {}

    def run(batch, task, offset):
        try:
            local = tmp_path / batch / tb.slug(task)
            for i in range(offset, offset + 40):
                _payload(local, i)
            root = tb.batch_root(drive_root, batch) / "checkpoints" / tb.slug(task)
            tb.assert_writable_path(root, drive_root, batch)
            for _ in range(3):
                tb.commit_checkpoint(local, root, task=task, session=f"{batch}-s")
            results[(batch, task)] = tb.restore_checkpoints(root, tmp_path / "r" / batch / tb.slug(task))
        except Exception as error:                               # noqa: BLE001
            errors.append(error)

    threads = [threading.Thread(target=run, args=(b, t, 1000 * k))
               for k, (b, t) in enumerate((b, t) for b, ts in tb.BATCHES.items() for t in ts)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert not errors and len(results) == 9
    assert all(r["payloads"] == 40 for r in results.values())
    roots = {tb.batch_root(drive_root, b) for b in tb.BATCHES}
    assert len(roots) == 3


def test_write_paths_are_confined_to_the_batch(tmp_path):
    root = tmp_path / "drive"
    tb.assert_writable_path(tb.batch_root(root, "B2") / "sessions" / "x", root, "B2")
    for elsewhere in (tb.batch_root(root, "B1") / "checkpoints",
                      root / "baseline" / "fit_cache" / tb.CACHE_IDENTITY,
                      root / "baseline" / "r1_tier_a_checkpoint"):
        with pytest.raises(tb.TierBError, match="outside"):
            tb.assert_writable_path(elsewhere, root, "B2")


def test_one_active_session_per_batch(tmp_path):
    root = tmp_path / "B1"
    lease = tb.acquire_lease(root, "S1")
    with pytest.raises(tb.TierBError, match="already active"):
        tb.acquire_lease(root, "S2")
    tb.release_lease(lease)
    tb.acquire_lease(root, "S2")                                 # released: allowed


def test_tier_a_restore_checks_sha_marker_and_count(tmp_path, monkeypatch):
    fits = tmp_path / "src" / "refit_cache" / "fits"
    for i in range(4):
        _payload(fits, i)
    archive = tmp_path / "tier_a.tar.gz"
    with tarfile.open(archive, "w:gz") as handle:
        handle.add(tmp_path / "src" / "refit_cache", arcname="refit_cache")
    monkeypatch.setattr(tb, "TIER_A_PAYLOADS", 4)
    digest = tb.sha256_file(archive)
    assert tb.restore_tier_a(archive, tmp_path / "ok", expected_sha256=digest)["payloads"] == 4
    with pytest.raises(tb.TierBError, match="sha256"):
        tb.restore_tier_a(archive, tmp_path / "bad", expected_sha256="0" * 64)
    monkeypatch.setattr(tb, "TIER_A_PAYLOADS", 5)
    with pytest.raises(tb.TierBError, match="expected 5"):
        tb.restore_tier_a(archive, tmp_path / "count", expected_sha256=digest)


def test_budget_stops_scheduling_before_the_reserve():
    budget = tb.Budget(start_epoch=0.0, budget_hours=1.0, reserve_minutes=10.0)
    # scheduling stops at 3000 s (60 min budget - 10 min reserve)
    assert budget.can_start(600.0, now=2000.0)                  # 1000 s left
    assert not budget.can_start(600.0, now=2500.0)               # 500 s left < 600 s
    assert budget.remaining(now=3000.0) == pytest.approx(0.0)
