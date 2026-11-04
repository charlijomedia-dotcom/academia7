#!/usr/bin/env python3
"""R1 Tier B: checkpoint protocol check on the real Google Drive mount (no estimation).

Runs the exact checkpoint code the batches use (r1_tierb.commit_checkpoint and friends)
against a DISPOSABLE namespace on the mounted Drive,

    <DRIVE_ROOT>/baseline/r1_tierb_drive_check/<check_id>/

with a few synthetic, properly marked payloads (no model is fitted). It checks:

  1. checkpoint creation (folder, archive, manifest, completion marker);
  2. archive read-back from Drive, member by member, against the manifest;
  3. completion: a second, incremental checkpoint with the correct parent; plus a probe
     of directory and file renames on the mount (informational: the completion-marker
     protocol does not rely on renames);
  4. interrupted-write recovery: a write cut after the archive and one cut inside the
     marker are both ignored; the history is unchanged; the next commit succeeds;
  5. restore into a fresh local folder equals the source payloads;
  6. checksum verification: a corrupted archive and a tampered manifest are detected;
  7. namespace isolation: a listing of every protected namespace (all three batch
     namespaces, the Tier A checkpoint, the aggregation folder, the original cache
     archives) is identical before and after; nothing is written outside the check's
     own folder; the batch write guard refuses the check's folder.

`verify(...)`, run later from ANOTHER runtime with the same check_id, restores the same
checkpoints and confirms they persisted on Drive (not only in the first VM's cache).

The check never modifies, renames or deletes anything outside its own folder, and never
deletes its own folder (left for inspection; it is a few kilobytes).
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r1_tierb as tb  # noqa: E402

TASK = "DRIVE_CHECK:synthetic"
REPORT = "drive_check_report.json"
PHASE1 = "phase1_inventory.json"


def check_root(drive_root: Path | str, check_id: str) -> Path:
    if not check_id or "/" in check_id or check_id.startswith("."):
        raise tb.TierBError(f"invalid check id {check_id!r}")
    return Path(drive_root) / "baseline" / "r1_tierb_drive_check" / check_id


def protected_namespaces(drive_root: Path | str, extra: list[Path] | None = None) -> list[Path]:
    base = Path(drive_root) / "baseline"
    return [base / "r1_tierb_batches", base / "r1_tier_a_checkpoint",
            base / "r1_tierb_aggregation", *(extra or [])]


def snapshot(paths: list[Path]) -> dict[str, list]:
    """(size, mtime_ns) of every file under each protected path; absent paths recorded."""
    out: dict[str, list] = {}
    for root in paths:
        root = Path(root)
        if not root.exists():
            out[str(root)] = ["absent"]
            continue
        files = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file())
        for path in files:
            stat = path.stat()
            out[str(path)] = [stat.st_size, stat.st_mtime_ns]
    return out


def _payloads(fits: Path, start: int, count: int) -> None:
    for i in range(start, start + count):
        name = f"{i % 256:02x}/{i:064x}.json"
        path = fits / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"forecasts": {"1": float(i)}, "status": "adequate",
                                    "drive_check": True, tb.MARKER: tb.MARKER_VALUE}))


def _expect_error(function, *args, **kwargs) -> str | None:
    try:
        function(*args, **kwargs)
    except (tb.TierBError, OSError) as error:
        return f"{type(error).__name__}: {error}"
    return None


def run(drive_root: Path | str, check_id: str, *, protected_extra: list[Path] | None = None,
        payloads: int = 12) -> dict:
    """Run every check; return (and write to the check folder) the report."""
    root = check_root(drive_root, check_id)
    if root.exists():
        raise tb.TierBError(f"{root} already exists: use a new check id")
    protected = protected_namespaces(drive_root, protected_extra)
    for path in protected:
        if root == path or path in root.parents or root in Path(path).parents:
            raise tb.TierBError(f"check folder {root} overlaps protected {path}")
    before = snapshot(protected)
    root.mkdir(parents=True)
    task_dir = root / "checkpoints" / tb.slug(TASK)
    results: dict[str, dict] = {}

    def step(name: str, function) -> None:
        try:
            detail = function()
            results[name] = {"ok": True, "detail": detail}
        except Exception as error:  # noqa: BLE001 - every failure is reported, none hidden
            results[name] = {"ok": False, "error": f"{type(error).__name__}: {error}",
                             "trace": traceback.format_exc(limit=4)}

    with tempfile.TemporaryDirectory() as scratch:
        local = Path(scratch) / "local" / "fits"
        state: dict = {}

        def create():
            _payloads(local, 0, payloads // 2)
            manifest = tb.commit_checkpoint(local, task_dir, task=TASK, session=check_id)
            folder = task_dir / manifest["checkpoint_id"]
            assert (folder / tb.COMMIT_MARKER).is_file(), "no completion marker"
            assert [m["checkpoint_id"] for _, m in tb.committed_checkpoints(task_dir)] == \
                [manifest["checkpoint_id"]], "first checkpoint not listed as committed"
            state["first"] = manifest
            return {"checkpoint_id": manifest["checkpoint_id"],
                    "files": sorted(p.name for p in folder.iterdir())}
        step("1_checkpoint_creation", create)

        def readback():
            manifest = state["first"]
            folder = task_dir / manifest["checkpoint_id"]
            assert tb.sha256_file(folder / "payloads.tar.gz") == manifest["archive_sha256"]
            import tarfile
            with tarfile.open(folder / "payloads.tar.gz", "r:gz") as archive:
                got = {m.name: tb.sha256_bytes(archive.extractfile(m).read())
                       for m in archive.getmembers() if m.isfile()}
            assert got == manifest["members"], "archive members differ from the manifest"
            return {"members_verified": len(got)}
        step("2_archive_readback", readback)

        def promotion():
            _payloads(local, payloads // 2, payloads - payloads // 2)
            second = tb.commit_checkpoint(local, task_dir, task=TASK, session=check_id)
            assert second["parent"] == state["first"]["checkpoint_id"], "wrong parent"
            history = [m["checkpoint_id"] for _, m in tb.committed_checkpoints(task_dir)]
            assert history == [state["first"]["checkpoint_id"], second["checkpoint_id"]]
            state["second"] = second
            # informational probes of rename behaviour on this mount
            probe = root / "rename_probe"
            source = probe / "dir.src"
            source.mkdir(parents=True)
            for i in range(3):
                (source / f"f{i}").write_bytes(os.urandom(256))
            digests = {p.name: tb.sha256_file(p) for p in source.iterdir()}
            os.replace(source, probe / "dir.dst")
            dir_ok = (not source.exists()
                      and {p.name: tb.sha256_file(p) for p in (probe / "dir.dst").iterdir()}
                      == digests)
            file_ok = True
            for i in range(5):
                tb.write_json_atomic(probe / "replace.json", {"i": i})
                file_ok &= json.loads((probe / "replace.json").read_text())["i"] == i
            return {"second_checkpoint": second["checkpoint_id"],
                    "directory_rename_consistent": dir_ok, "file_replace_consistent": file_ok,
                    "protocol_relies_on_directory_rename": False}
        step("3_completed_checkpoint_promotion", promotion)

        def interrupted():
            committed = [m["checkpoint_id"] for _, m in tb.committed_checkpoints(task_dir)]
            _payloads(local, payloads, 3)
            cut_archive = _expect_error(tb.commit_checkpoint, local, task_dir, task=TASK,
                                        session=check_id, _fail_after_archive=True)
            cut_marker = _expect_error(tb.commit_checkpoint, local, task_dir, task=TASK,
                                       session=check_id, _fail_in_marker=True)
            assert cut_archive and cut_marker, "simulated interruptions did not raise"
            incomplete = tb.incomplete_checkpoints(task_dir)
            assert len(incomplete) == 2, f"incomplete writes listed: {incomplete}"
            assert [m["checkpoint_id"] for _, m in tb.committed_checkpoints(task_dir)] == committed
            retry = tb.commit_checkpoint(local, task_dir, task=TASK, session=check_id)
            assert retry["parent"] == committed[-1] and len(retry["members"]) == 3
            state["total"] = payloads + 3
            return {"ignored_incomplete_writes": incomplete,
                    "retry_checkpoint": retry["checkpoint_id"]}
        step("4_interrupted_write_recovery", interrupted)

        def restore():
            fresh = Path(scratch) / "fresh" / "fits"
            report = tb.restore_checkpoints(task_dir, fresh)
            assert tb.inventory(fresh) == tb.inventory(local), "restore differs from source"
            tb.write_json_atomic(root / PHASE1, {"inventory": tb.inventory(local),
                                                 "created_utc": tb.utc_stamp()})
            return {"payloads": report["payloads"], "checkpoints": report["checkpoints"]}
        step("5_restore", restore)

        def checksums():
            corrupt = root / "corruption_probe" / tb.slug(TASK)
            corrupt.mkdir(parents=True)
            source = task_dir / state["first"]["checkpoint_id"]
            shutil.copytree(source, corrupt / source.name)
            archive = corrupt / source.name / "payloads.tar.gz"
            data = bytearray(archive.read_bytes())
            data[len(data) // 2] ^= 0xFF
            archive.write_bytes(bytes(data))
            archive_error = _expect_error(tb.committed_checkpoints, corrupt)
            shutil.copyfile(source / "payloads.tar.gz", archive)        # repair the archive
            manifest = corrupt / source.name / "manifest.json"
            manifest.write_text(manifest.read_text().replace('"sequence": 1', '"sequence": 7'))
            manifest_error = _expect_error(tb.committed_checkpoints, corrupt)
            assert archive_error and "sha256" in archive_error, archive_error
            assert manifest_error and "sha256" in manifest_error, manifest_error
            return {"corrupted_archive": archive_error, "tampered_manifest": manifest_error}
        step("6_checksum_verification", checksums)

    def isolation():
        after = snapshot(protected)
        changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        assert not changed, f"protected namespaces changed: {changed[:5]}"
        refused = _expect_error(tb.assert_writable_path, root / "x", drive_root, "B1")
        assert refused, "the batch write guard accepted the check folder"
        return {"protected_paths": [str(p) for p in protected],
                "protected_files_listed": len(before), "changed": changed,
                "batch_guard_refuses_check_folder": refused}
    step("7_namespace_isolation", isolation)

    report = {"check_id": check_id, "folder": str(root), "created_utc": tb.utc_stamp(),
              "estimation": "none (synthetic payloads only)",
              "ok": all(r["ok"] for r in results.values()), "results": results,
              "cross_runtime_persistence": ("not yet verified: run verify() with this "
                                            "check_id from a new runtime")}
    tb.write_json_atomic(root / REPORT, report)
    return report


def verify(drive_root: Path | str, check_id: str) -> dict:
    """From a NEW runtime: the earlier check's checkpoints restore to the same payloads."""
    root = check_root(drive_root, check_id)
    expected = json.loads((root / PHASE1).read_text(encoding="utf-8"))["inventory"]
    with tempfile.TemporaryDirectory() as scratch:
        fresh = Path(scratch) / "fits"
        tb.restore_checkpoints(root / "checkpoints" / tb.slug(TASK), fresh)
        ok = tb.inventory(fresh) == expected
    result = {"check_id": check_id, "verified_utc": tb.utc_stamp(), "ok": ok,
              "payloads": len(expected), "host": os.uname().nodename}
    tb.write_json_atomic(root / f"cross_runtime_verify-{tb.utc_stamp()}.json", result)
    return result


def summary(report: dict) -> str:
    lines = [f"Drive checkpoint check {report['check_id']}: "
             + ("ALL CHECKS PASSED" if report["ok"] else "FAILED")]
    for name, result in report["results"].items():
        lines.append(f"  {'ok  ' if result['ok'] else 'FAIL'} {name}"
                     + ("" if result["ok"] else f": {result['error']}"))
    return "\n".join(lines)
