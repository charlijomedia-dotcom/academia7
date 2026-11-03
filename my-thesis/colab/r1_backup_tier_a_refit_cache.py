# R1: back up the Tier A refit cache to Google Drive (no estimation; dry run by default).
#
# Paste into a NEW cell of the Colab session that ran Tier A (run 20261103T063749Z), if that
# runtime is still alive. The eight re-estimated Tier A AR chains exist only on that VM's
# local disk (WORK_DIR/refit_cache/fits); without them a Tier B release must re-derive them.
#
# What it does:
#   1. inventories every payload (sha256) and checks each one carries the R1 refit marker;
#   2. with DO_BACKUP = True only: writes them, by name, as compressed parts to a NEW Drive
#      folder  DRIVE_ROOT/r1_refit_cache/<identity>/tier_a_<stamp>/  (never into fit_cache/);
#   3. restores those parts into a temporary directory and requires every sha256 to match.
# It reads nothing but the refit cache and writes nothing but the new Drive folder.
# Needs only WORK_DIR, DRIVE_ROOT and tc (thesis_colab) from the session.
import hashlib as _hashlib
import json as _json
import tempfile as _tempfile
import time as _time
from pathlib import Path as _Path

DO_BACKUP = bool(globals().get("DO_BACKUP", False))
EXPECTED_TIER_A_PAYLOADS = 5597      # 703 + 626 + 4 x 715 + 764 + 644 origins
_IDENTITY = globals().get("IDENTITY") or "3413465b508bb844"
_MARKER = "r1_provenance"


def _sha256(path):
    return _hashlib.sha256(_Path(path).read_bytes()).hexdigest()


def inventory_refit_cache(fits):
    fits = _Path(fits)
    entries, unmarked = {}, []
    for path in sorted(fits.rglob("*.json")):
        relative = path.relative_to(fits).as_posix()
        payload = _json.loads(path.read_text(encoding="utf-8"))
        if payload.get(_MARKER) != "re-estimated":
            unmarked.append(relative)
        entries[relative] = _sha256(path)
    return entries, unmarked


def backup_tier_a_refit_cache(work_dir, drive_root, archive_cls, *, do_backup, stamp=None):
    fits = _Path(work_dir) / "refit_cache" / "fits"
    if not fits.is_dir():
        return {"status": "absent", "detail": f"{fits} does not exist: this runtime no longer "
                "holds the Tier A refit cache (see the Tier B preflight, section 7)"}
    entries, unmarked = inventory_refit_cache(fits)
    if unmarked:
        raise RuntimeError(f"{len(unmarked)} payloads lack the R1 refit marker, e.g. "
                           f"{unmarked[:3]}; this is not a pure refit cache; nothing backed up")
    stamp = stamp or _time.strftime("%Y%m%dT%H%M%SZ", _time.gmtime())
    destination = _Path(drive_root) / "r1_refit_cache" / _IDENTITY / f"tier_a_{stamp}"
    if "fit_cache" in destination.parts:
        raise RuntimeError("refusing to write under a fit_cache folder")
    report = {"status": "dry-run", "payloads": len(entries),
              "expected_payloads": EXPECTED_TIER_A_PAYLOADS, "destination": str(destination)}
    if len(entries) != EXPECTED_TIER_A_PAYLOADS:
        report["warning"] = "payload count differs from the eight Tier A chains' origins"
    if not do_backup:
        return report
    if destination.exists():
        raise RuntimeError(f"{destination} already exists; nothing overwritten")
    archive = archive_cls(fits, destination, by_name=True, max_files_per_part=2000)
    archive.sync()
    with _tempfile.TemporaryDirectory() as scratch:
        restored = _Path(scratch) / "fits"
        archive_cls(restored, destination).restore(restored)
        mismatched = [name for name, digest in entries.items()
                      if not (restored / name).is_file() or _sha256(restored / name) != digest]
    report.update(status="backed-up" if not mismatched else "VERIFICATION-FAILED",
                  mismatched=mismatched[:20], parts=len(list(destination.glob("part-*.tar.gz"))))
    (destination / "inventory_sha256.json").write_text(_json.dumps(entries, indent=0))
    (destination / "backup_report.json").write_text(_json.dumps(report, indent=2))
    if mismatched:
        raise RuntimeError(f"backup verification failed for {len(mismatched)} payloads")
    return report


TIER_A_REFIT_BACKUP = backup_tier_a_refit_cache(WORK_DIR, DRIVE_ROOT, tc.IncrementalArchive,
                                                do_backup=DO_BACKUP)
print(_json.dumps(TIER_A_REFIT_BACKUP, indent=1))
if not DO_BACKUP and TIER_A_REFIT_BACKUP["status"] == "dry-run":
    print("DRY RUN: set DO_BACKUP = True in this session and run again to write the backup.")
