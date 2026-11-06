"""The supplementary recovery cell: read-only, verified against the export manifest."""

from __future__ import annotations

import gzip
import hashlib
import json
import re
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
CELL = ROOT / "colab" / "r1_b3_supplementary_recovery_cell.py"


def _layout(tmp_path: Path, parts: int = 5):
    drive = tmp_path / "drive"
    session = drive / "baseline" / "r1_original_cache_audit" / "audit-20261106T081950Z-9c9ba2"
    files = []
    for rel, n in (("audit/origins.csv", 400_000),
                   ("impact/reference_tables/data_audit/locf_forecast_exposure.csv", 900_000),
                   ("impact/candidate_tables/data_audit/locf_forecast_exposure.csv", 900_001)):
        data = (b"origin,value\n" + b"".join(b"%d,%d\n" % (i, i * 7 % 13) for i in range(n)))
        (session / rel).parent.mkdir(parents=True, exist_ok=True)
        (session / rel).write_bytes(data)
        files.append({"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    (session / "export_manifest.json").write_text(json.dumps({"session": "s", "files": files}))
    cache = drive / "baseline" / "fit_cache" / "3413465b508bb844"
    cache.mkdir(parents=True)
    total = 0
    for i in range(1, parts + 1):
        data = bytes([i]) * (1_000_000 + i)
        (cache / f"part-{i:05d}.tar.gz").write_bytes(data)
        total += len(data)
    return drive, session, cache, total


def _run(drive: Path, parts: int, total: int, chunk: int = 3_500_000):
    source = CELL.read_text()
    source = re.sub(r'^DRIVE_ROOT = .*$', f'DRIVE_ROOT = "{drive}"', source, flags=re.M)
    source = source.replace("EXPECTED_PARTS, EXPECTED_PART_BYTES = 143, 9_547_811",
                            f"EXPECTED_PARTS, EXPECTED_PART_BYTES = {parts}, {total}")
    source = source.replace("CHUNK = 3_500_000", f"CHUNK = {chunk}")
    exec(compile(source, "cell", "exec"), {"__name__": "cell"})


def test_cell_is_read_only_and_writes_one_new_folder():
    source = CELL.read_text()
    for forbidden in ("git push", "subprocess", "unlink", "rmtree", "estimat" + "e("):
        assert forbidden not in source
    writes = [line for line in source.splitlines() if "write_bytes(" in line or "write_text(" in line]
    assert writes and all("target." in w or "SUPP /" in w for w in writes), writes
    assert 'assert not SUPP.exists()' in source


def test_cell_recovers_verified_files_and_unchanged_cache_parts(tmp_path):
    drive, session, cache, total = _layout(tmp_path)
    before = {p: p.read_bytes() for p in drive.rglob("*") if p.is_file()}
    _run(drive, 5, total)
    supp = session.parent / f"{session.name}_supplementary"
    assert {p: p.read_bytes() for p in before} == before  # nothing existing changed
    manifest = json.loads((supp / "supplementary_manifest.json").read_text())
    for entry in manifest["recovered"]:
        chunks = sorted(f for f in manifest["files"] if f.get("chunk_of") == f"export/{entry['path']}.gz")
        packed = b"".join((supp / f["path"]).read_bytes() for f in sorted(chunks, key=lambda f: f["index"]))
        assert hashlib.sha256(gzip.decompress(packed)).hexdigest() == entry["sha256"]
        assert all(f["bytes"] <= 3_500_000 for f in chunks)
    restored = {}
    for f in manifest["files"]:
        if f["path"].endswith(".tar"):
            assert f["bytes"] <= 3_500_000
            with tarfile.open(supp / f["path"]) as tar:
                for member in tar.getmembers():
                    restored[member.name] = tar.extractfile(member).read()
    assert restored == {p.name: p.read_bytes() for p in cache.glob("part-*.tar.gz")}
    assert manifest["parts"] == 5 and manifest["part_bytes"] == total


def test_cell_refuses_a_mismatching_export_and_a_second_run(tmp_path):
    drive, session, cache, total = _layout(tmp_path)
    (session / "audit/origins.csv").write_bytes(b"tampered")
    with pytest.raises(AssertionError, match="bytes, manifest|sha256"):
        _run(drive, 5, total)
    drive2, session2, _c, total2 = _layout(tmp_path / "second")
    _run(drive2, 5, total2)
    with pytest.raises(AssertionError, match="exists"):
        _run(drive2, 5, total2)


def test_cell_points_at_the_audit_session_and_its_three_files():
    source = CELL.read_text()
    assert 'SESSION = "audit-20261106T081950Z-9c9ba2"' in source
    export = json.loads((ROOT / "reports/part8/corrections/r1/evidence/b3_stage2_20261106/export_manifest.json").read_text())
    big = sorted(f["path"] for f in export["files"] if f["bytes"] > 5_000_000)
    for rel in big:
        assert f'"{rel}"' in source
    assert len(big) == 3
