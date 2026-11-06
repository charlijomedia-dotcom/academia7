# R1 Option B3/B1: supplementary recovery cell (READ-ONLY; no estimation, no git, no push).
#
# Paste this whole file into ONE Colab cell and run it. It needs only Google Drive.
#
#   A. The three exported files of audit session audit-20261106T081950Z-9c9ba2 that the
#      Drive connector could not download (over its size limit). Each is read from the
#      session folder, its sha256 checked against that session's export_manifest.json,
#      and written as a reproducible gzip (mtime 0), split into chunks of at most 3.5 MB.
#   B. The ORIGINAL fit cache archive parts (fit_cache/3413465b508bb844, 143 parts,
#      9,547,811 bytes), unchanged, packed into a few uncompressed tar bundles of at most
#      3.5 MB so that they can be downloaded through the connector. Every part's sha256 is
#      recorded; the parts are not unpacked or modified.
#
# Reads: the audit session folder and the original cache folder. Writes ONLY the new folder
# <session>_supplementary next to the session folder; it refuses to run if that folder
# exists (delete it yourself to re-run). Nothing else on Drive is touched.

import gzip
import hashlib
import io
import json
import tarfile
import time
from pathlib import Path

DRIVE_ROOT = "/content/drive/MyDrive/KillyPhD/Part8_K3_InSample_2026-10-29"  # @param {type:"string"}
SESSION = "audit-20261106T081950Z-9c9ba2"
OVERSIZED = ["audit/origins.csv",
             "impact/reference_tables/data_audit/locf_forecast_exposure.csv",
             "impact/candidate_tables/data_audit/locf_forecast_exposure.csv"]
CACHE_IDENTITY = "3413465b508bb844"
EXPECTED_PARTS, EXPECTED_PART_BYTES = 143, 9_547_811
CHUNK = 3_500_000

if DRIVE_ROOT.startswith("/content/drive/") and not Path("/content/drive/MyDrive").exists():
    from google.colab import drive  # noqa: E402
    drive.mount("/content/drive")
AUDIT_ROOT = Path(DRIVE_ROOT) / "baseline" / "r1_original_cache_audit"
SESSION_DIR = AUDIT_ROOT / SESSION
CACHE_DIR = Path(DRIVE_ROOT) / "baseline" / "fit_cache" / CACHE_IDENTITY
SUPP = AUDIT_ROOT / f"{SESSION}_supplementary"  # the ONLY Drive write
assert SESSION_DIR.is_dir(), f"session folder not found: {SESSION_DIR}"
assert CACHE_DIR.is_dir(), f"original cache folder not found: {CACHE_DIR}"
assert not SUPP.exists(), f"{SUPP} exists; delete it to re-run (nothing was written)"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _chunks(name: str, data: bytes, files: list) -> None:
    for i in range(0, max(len(data), 1), CHUNK):
        piece = data[i:i + CHUNK]
        target = SUPP / f"{name}.part-{i // CHUNK:02d}"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(piece)
        assert _sha(target.read_bytes()) == _sha(piece), f"write check failed: {target}"
        files.append({"path": target.relative_to(SUPP).as_posix(), "bytes": len(piece),
                      "sha256": _sha(piece), "chunk_of": name, "index": i // CHUNK})


manifest = json.loads((SESSION_DIR / "export_manifest.json").read_text())
listed = {f["path"]: f for f in manifest["files"]}
SUPP.mkdir(parents=True)
files, recovered = [], []

# -- A. the three oversized export files ---------------------------------------------------
for rel in OVERSIZED:
    entry = listed[rel]
    data = (SESSION_DIR / rel).read_bytes()
    assert len(data) == entry["bytes"], f"{rel}: {len(data)} bytes, manifest {entry['bytes']}"
    assert _sha(data) == entry["sha256"], f"{rel}: sha256 differs from the export manifest"
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=buffer, mtime=0) as h:
        h.write(data)
    packed = buffer.getvalue()
    assert gzip.decompress(packed) == data
    _chunks(f"export/{rel}.gz", packed, files)
    recovered.append({"path": rel, "bytes": len(data), "sha256": entry["sha256"],
                      "manifest_sha256_verified": True, "gzip_bytes": len(packed),
                      "gzip_sha256": _sha(packed)})
    print(f"A  {rel}: sha256 verified, gzip {len(packed):,} bytes")

# -- B. the original cache archive parts, unchanged, in tar bundles -------------------------
parts = sorted(CACHE_DIR.glob("part-*.tar.gz"))
part_rows = [{"part": p.name, "bytes": p.stat().st_size, "sha256": _sha(p.read_bytes())}
             for p in parts]
assert len(parts) == EXPECTED_PARTS, f"{len(parts)} parts, expected {EXPECTED_PARTS}"
assert sum(r["bytes"] for r in part_rows) == EXPECTED_PART_BYTES, "part bytes differ"
bundles, current, size = [], [], 0
for p, row in zip(parts, part_rows):
    if current and size + row["bytes"] + 1024 > CHUNK:
        bundles.append(current)
        current, size = [], 0
    current.append((p, row))
    size += row["bytes"] + 1024
bundles.append(current)
for b, members in enumerate(bundles):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.USTAR_FORMAT) as tar:
        for p, row in members:
            data = p.read_bytes()
            assert _sha(data) == row["sha256"], f"{p.name} changed while bundling"
            info = tarfile.TarInfo(name=p.name)
            info.size, info.mtime, info.mode = len(data), 0, 0o644
            tar.addfile(info, io.BytesIO(data))
    data = buffer.getvalue()
    target = SUPP / "original_cache" / f"bundle-{b:02d}.tar"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    assert _sha(target.read_bytes()) == _sha(data)
    files.append({"path": target.relative_to(SUPP).as_posix(), "bytes": len(data),
                  "sha256": _sha(data), "parts": [row["part"] for _, row in members]})
    print(f"B  bundle-{b:02d}.tar: {len(members)} parts, {len(data):,} bytes")
(SUPP / "original_cache" / "parts.json").write_text(json.dumps(part_rows, indent=1))

summary = {"session": SESSION, "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "estimation": "none", "reads": [str(SESSION_DIR), str(CACHE_DIR)], "writes": str(SUPP),
           "export_manifest_sha256": _sha((SESSION_DIR / "export_manifest.json").read_bytes()),
           "recovered": recovered, "cache_identity": CACHE_IDENTITY, "parts": len(part_rows),
           "part_bytes": sum(r["bytes"] for r in part_rows),
           "parts_sha256_digest": _sha("\n".join(f"{r['part']} {r['sha256']}" for r in part_rows).encode()),
           "files": files}
(SUPP / "supplementary_manifest.json").write_text(json.dumps(summary, indent=1))
print(json.dumps({k: v for k, v in summary.items() if k != "files"}, indent=1))
print(f"DONE: {len(files)} files in {SUPP}")
