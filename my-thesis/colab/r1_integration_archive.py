"""Non-publishing archive of the audited Part 8 integration candidate (465-file release tree).

Two modes, chosen by what the Colab runtime still holds:

PRESERVE     the audited session's own release tree still exists on the runtime
             (`<WORK>/dryrun/<AUDITED_SESSION>/release`). Every file must equal the audited
             `manifests/output_inventory.csv` by sha256 and size, the inventory itself must equal
             the sha256 recorded in the audited export manifest, and no file may be missing or
             extra. Nothing is recomputed.

RECONSTRUCT  the tree is gone. The unchanged dry run (orchestration a2c3171, pin 8aaa4217, no
             estimation) is run again in a new session, and `equivalence_gate` compares it with
             the audited session's exported machine reports:
               - acceptance: every criterion passes, nothing unexplained, exit 4;
               - every exported report is identical: CSVs byte for byte (cell-level changes
                 against all four references, decisions, chain statuses, chain sources, claim and
                 jury rechecks), JSON reports after removing ONLY the provenance keys listed in
                 VOLATILE_KEYS, gzip files after decompression;
               - the release inventory: same 465 paths; a file may differ in sha256 only if it is
                 one of the explicitly identified provenance carriers (PROVENANCE_ALLOWED) -
                 figure provenance sidecars, the correction run records, and regenerated tables
                 that carry provenance columns (their cell content is fixed by the identical
                 cell-level reports); figures, original files and everything else must be
                 byte-identical.
             Any other difference refuses the archive.

`write_archive` then writes, to a NEW Drive folder only: release.tar.gz (deterministic), its
file inventory with sha256, acceptance_report.json (the gate), and archive_manifest.json (mode, gate report, run identity, exact
scientific and orchestration commits), and re-reads the written archive to verify every member.
Nothing is published, pushed, or written anywhere else. No model is estimated.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import os
import tarfile
from pathlib import Path

AUDITED_SESSION = "integration-20261108T052245Z-9bba8e"
AUDITED_RUN_ID = "correction-20261108T053328-949fcd76"
AUDITED_ORCHESTRATION = "a2c3171dbadc80f8821fdb91877d82622a1ff171"
SCIENTIFIC_PIN = "8aaa4217536ab3cb942dd248dd19ece7838a8d60"
AUDITED_EXPORT_MANIFEST_SHA256 = "b7e585f3824e8ef01388f5ea1bd7674cf004097fa84e04bf682adff5f9f57612"
AUDITED_INVENTORY_SHA256 = "d55721d3798ae52d57de0f193bf97953f1ac49633d4d35a85cdcbe2d70827089"
AUDITED_EXPORT_FILES = 45
RELEASE_FILES = 465
INVENTORY = "manifests/output_inventory.csv"
ARCHIVE_PARENT = "baseline/r1_part8_candidate_archive"
EXPECTED_EXIT = 4                       # accepted for review, review required (B2 items open)

# Report layout of the integration notebook's export cell (relative path -> path in the dry run).
EXPORT_SOURCES = (("dryrun_report", ""), ("stages", "stages/"),
                  ("base_manifest.csv", "base_manifest.csv"),
                  ("assembly/reconcile_cell_causes.csv.gz", "assembly/reconcile_cell_causes.csv.gz"),
                  ("assembly/legacy/r1_comparison.csv", "assembly/legacy_r1_comparison.csv"),
                  ("assembly/corrected/r1_comparison.csv", "assembly/corrected_r1_comparison.csv"),
                  ("assembly/corrected/r1_reconciliation.csv", "assembly/r1_reconciliation.csv"),
                  ("assembly/corrected/r1_summary.json", "assembly/corrected_r1_summary.json"),
                  ("assembly/legacy/r1_summary.json", "assembly/legacy_r1_summary.json"),
                  ("release/manifests", "release_manifests/"))

# Provenance that legitimately differs between two executions of the same computation.
VOLATILE_KEYS = frozenset({"run_id", "session", "started_utc", "finished_utc", "created_utc",
                           "recorded_utc"})
PROVENANCE_COLUMNS = frozenset({"run_id", "created_utc"})
NOT_COMPARED = {"console.log": "run log (timings and paths)"}
# Release files that may differ in sha256, and why. Everything else must be byte-identical.
PROVENANCE_RECORDS = {
    "manifests/correction_run_manifest.json": "run record: run_id and started_utc",
    "manifests/correction_summary.json": "run record: run_id",
    "manifests/T2.0A_frozen_manifest.csv": "frozen-data manifest: run_id and created_utc columns",
}
BINARY_STRICT = (".png", ".pdf", ".svg")
# A figure provenance sidecar is rewritten by every run, even for an unchanged figure; it may
# differ from the published original only in these keys (and must name the scientific pin).
SIDECAR_KEYS = frozenset({"run_id", "created_utc", "code_commit_sha"})
# The one annotation the integration adds to a re-rendered F4.8 sidecar (exact text required).
SIDECAR_ANNOTATIONS = {"integration_dry_run": "re-rendered by the pinned code from the integrated "
                                              "window-length table (decision D2)"}


class ArchiveRefused(RuntimeError):
    """The candidate cannot be archived: it is not provably the audited computation."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def listing(root: Path | str) -> dict[str, str]:
    root = Path(root)
    return {p.relative_to(root).as_posix(): sha256_file(p)
            for p in sorted(root.rglob("*")) if p.is_file()}


def read_inventory(path: Path | str) -> dict[str, dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return {row["path"]: row for row in csv.DictReader(fh)}


# -- the audited export ------------------------------------------------------------------

def verify_audited_export(export_dir: Path | str) -> dict:
    """Check the audited session's Drive export against its pinned manifest; return the manifest."""
    export_dir = Path(export_dir)
    manifest_path = export_dir / "export_manifest.json"
    if sha256_file(manifest_path) != AUDITED_EXPORT_MANIFEST_SHA256:
        raise ArchiveRefused(f"{manifest_path} is not the audited export manifest")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("session") != AUDITED_SESSION or len(manifest["files"]) != AUDITED_EXPORT_FILES:
        raise ArchiveRefused("the export manifest does not describe the audited session")
    bad = [f["path"] for f in manifest["files"]
           if not (export_dir / f["path"]).is_file()
           or sha256_file(export_dir / f["path"]) != f["sha256"]
           or (export_dir / f["path"]).stat().st_size != f["bytes"]]
    if bad:
        raise ArchiveRefused(f"audited export files missing or altered: {bad}")
    inventory = export_dir / "release_manifests" / "output_inventory.csv"
    if sha256_file(inventory) != AUDITED_INVENTORY_SHA256:
        raise ArchiveRefused("the audited output inventory has an unexpected sha256")
    return manifest


# -- PRESERVE ----------------------------------------------------------------------------

def preserve_check(release_dir: Path | str, audited_export: Path | str) -> dict:
    """Exact-file verification of the original release tree against the audited inventory."""
    release_dir = Path(release_dir)
    verify_audited_export(audited_export)
    expected = read_inventory(Path(audited_export) / "release_manifests" / "output_inventory.csv")
    found = listing(release_dir)
    expected_paths = set(expected) | {INVENTORY}
    report = {"mode": "preserve", "release_dir": str(release_dir), "files": len(found),
              "missing": sorted(expected_paths - set(found)),
              "extra": sorted(set(found) - expected_paths), "altered": []}
    for path, row in expected.items():
        if path in found and (found[path] != row["sha256"]
                              or (release_dir / path).stat().st_size != int(row["bytes"])):
            report["altered"].append(path)
    if found.get(INVENTORY) != AUDITED_INVENTORY_SHA256:
        report["altered"].append(INVENTORY)
    report["ok"] = (not report["missing"] and not report["extra"] and not report["altered"]
                    and len(found) == RELEASE_FILES)
    if not report["ok"]:
        raise ArchiveRefused(f"the release tree is not the audited one: {json.dumps(report)[:2000]}")
    return report


# -- RECONSTRUCT: equivalence gate --------------------------------------------------------

def export_layout(dryrun: Path | str) -> dict[str, Path]:
    """Relative export path -> file of a dry-run work folder (the notebook's export layout)."""
    dryrun = Path(dryrun)
    out = {}
    for source, prefix in EXPORT_SOURCES:
        path = dryrun / source
        if path.is_file():
            out[prefix] = path
        elif path.is_dir():
            for p in sorted(path.rglob("*")):
                if p.is_file():
                    out[prefix + p.relative_to(path).as_posix()] = p
    return out


def normalise(obj, tokens: dict[str, str]):
    """Drop VOLATILE_KEYS and replace run-specific tokens (sessions, run ids) by placeholders."""
    if isinstance(obj, dict):
        return {k: normalise(v, tokens) for k, v in obj.items() if k not in VOLATILE_KEYS}
    if isinstance(obj, list):
        return [normalise(v, tokens) for v in obj]
    if isinstance(obj, str):
        for token, placeholder in tokens.items():
            obj = obj.replace(token, placeholder)
        return obj
    return obj


def _csv_without(data: bytes, drop: frozenset) -> list[list[str]]:
    rows = list(csv.reader(io.StringIO(data.decode("utf-8"))))
    if not rows:
        return rows
    keep = [i for i, c in enumerate(rows[0]) if c not in drop]
    return [[r[i] if i < len(r) else "" for i in keep] for r in rows]


def compare_report(relative: str, new: bytes, audited: bytes, tokens: dict[str, str]) -> str | None:
    """None if equivalent; otherwise the reason."""
    if relative.endswith(".gz"):
        new, audited = gzip.decompress(new), gzip.decompress(audited)
        relative = relative[:-3]
    if relative.endswith(".json"):
        a, b = normalise(json.loads(new), tokens), normalise(json.loads(audited), tokens)
        return None if a == b else "JSON content differs beyond the identified provenance keys"
    if relative == "release_manifests/output_inventory.csv":
        return None                     # compared file by file in compare_inventory
    if relative == "release_manifests/T2.0A_frozen_manifest.csv":
        same = _csv_without(new, PROVENANCE_COLUMNS) == _csv_without(audited, PROVENANCE_COLUMNS)
        return None if same else "frozen-data manifest differs beyond run_id/created_utc"
    return None if new == audited else "content differs (byte comparison)"


def compare_inventory(new_release: Path | str, audited_export: Path | str,
                      reference_dirs: tuple = ()) -> dict:
    new_release = Path(new_release)
    new = read_inventory(new_release / INVENTORY)
    old = read_inventory(Path(audited_export) / "release_manifests" / "output_inventory.csv")
    with open(Path(audited_export) / "files_vs_published.csv", newline="", encoding="utf-8") as fh:
        compared_tables = {row["path"] for row in csv.DictReader(fh)}
    out = {"paths_new": len(new), "paths_audited": len(old),
           "missing": sorted(set(old) - set(new)), "extra": sorted(set(new) - set(old)),
           "identical": 0, "provenance_only": {}, "refused": {}}
    for path in sorted(set(old) & set(new)):
        a, b = new[path], old[path]
        if a["sha256"] == b["sha256"] and a["bytes"] == b["bytes"]:
            out["identical"] += 1
            continue
        reason = None
        if path.endswith(".provenance.json") and a["source"] == b["source"]:
            reason = _sidecar_problem(new_release / path, [Path(d) / path for d in reference_dirs])
            if reason:
                out["refused"][path] = reason
            else:
                out["provenance_only"][path] = "figure provenance sidecar (run_id, created_utc, code commit)"
            continue
        if a["source"] != b["source"]:
            reason = f"source changed {b['source']} -> {a['source']}"
        elif b["source"] == "original_unchanged":
            reason = "original file must be byte-identical"
        elif path.endswith(BINARY_STRICT):
            reason = "figure must be byte-identical"
        if reason:
            out["refused"][path] = reason
            continue
        if path in PROVENANCE_RECORDS:
            out["provenance_only"][path] = PROVENANCE_RECORDS[path]
        elif path.endswith((".csv", ".parquet")) and _has_provenance_columns(new_release / path):
            if path not in compared_tables:
                out["refused"][path] = "table differs but is outside the audited cell comparison"
            else:
                out["provenance_only"][path] = (
                    "regenerated table with provenance columns; every other cell is fixed by the "
                    "identical cells_vs_*/files_vs_* reports (pinned compare, rel. tol. 1e-9)")
        else:
            out["refused"][path] = "differs and is not an identified provenance carrier"
    disk = listing(new_release)
    out["files_on_disk"] = len(disk)
    out["inventory_vs_disk"] = sorted(p for p, row in new.items() if disk.get(p) != row["sha256"])
    out["ok"] = (not out["missing"] and not out["extra"] and not out["refused"]
                 and not out["inventory_vs_disk"] and len(disk) == RELEASE_FILES)
    return out


def _sidecar_problem(new: Path, references: list[Path]) -> str | None:
    """None if the sidecar is a valid re-issue: it names the scientific pin and, outside
    SIDECAR_KEYS, equals one of the reference sidecars (the published original or the base
    tree's), allowing only the exact SIDECAR_ANNOTATIONS."""
    try:
        data = json.loads(new.read_text())
    except ValueError:
        return "sidecar is not valid JSON"
    if data.get("code_commit_sha") != SCIENTIFIC_PIN:
        return "sidecar does not name the scientific pin"
    for key, text in SIDECAR_ANNOTATIONS.items():
        if key in data and data[key] != text:
            return f"sidecar annotation {key} has unexpected text"
    existing = [p for p in references if p.is_file()]
    if not existing:
        return None
    strip = lambda d: {k: v for k, v in d.items() if k not in SIDECAR_KEYS}  # noqa: E731
    for ref in existing:
        old = json.loads(ref.read_text())
        for key, text in SIDECAR_ANNOTATIONS.items():
            if key in data and key not in old:
                old = dict(old, **{key: text})
        if strip(data) == strip(old):
            return None
    return "sidecar differs from the published and base sidecars beyond run_id/created_utc/code commit"


def _has_provenance_columns(path: Path) -> bool:
    if path.suffix == ".parquet":
        import pyarrow.parquet as pq
        names = set(pq.read_schema(path).names)
    else:
        with open(path, newline="", encoding="utf-8") as fh:
            names = set(next(csv.reader(fh), []))
    return bool(names & PROVENANCE_COLUMNS)


def equivalence_gate(new_dryrun: Path | str, audited_export: Path | str, *, exit_code: int,
                     new_session: str, new_run_id: str, published_dir: Path | str) -> dict:
    """Refuses unless the reconstructed candidate is the audited computation up to provenance."""
    new_dryrun, audited_export = Path(new_dryrun), Path(audited_export)
    manifest = verify_audited_export(audited_export)
    tokens = {new_session: "<session>", AUDITED_SESSION: "<session>",
              new_run_id: "<run_id>", AUDITED_RUN_ID: "<run_id>"}
    layout = export_layout(new_dryrun)
    reports = {"compared": 0, "not_compared": {}, "missing": [], "differs": {}}
    for entry in manifest["files"]:
        rel = entry["path"]
        if rel in NOT_COMPARED:
            reports["not_compared"][rel] = NOT_COMPARED[rel]
            continue
        if entry.get("gzip_of"):
            continue                    # the uncompressed original is compared
        if rel not in layout:
            reports["missing"].append(rel)
            continue
        reason = compare_report(rel, layout[rel].read_bytes(), (audited_export / rel).read_bytes(),
                                tokens)
        reports["compared"] += 1
        if reason:
            reports["differs"][rel] = reason
    acceptance = json.loads((new_dryrun / "dryrun_report" / "acceptance.json").read_text())
    unexplained = (new_dryrun / "dryrun_report" / "unexplained_differences.csv").read_text().split()
    checks = {
        "exit_code": exit_code == EXPECTED_EXIT,
        "accepted": acceptance.get("accepted") is True and not acceptance.get("failed_criteria"),
        "all_criteria_pass": all(c.get("pass") for c in acceptance.get("criteria", {}).values()),
        "nothing_unexplained": unexplained in ([], ["empty"]),
        "not_published": acceptance.get("published") is False,
        "orchestration_commit": acceptance.get("orchestration_commit") == AUDITED_ORCHESTRATION,
        "scientific_commit": acceptance.get("scientific_commit") == SCIENTIFIC_PIN,
        "reports_identical": not reports["missing"] and not reports["differs"],
    }
    inventory = compare_inventory(new_dryrun / "release", audited_export,
                                  (Path(published_dir), new_dryrun / "base"))
    checks["release_inventory"] = inventory["ok"]
    report = {"mode": "reconstruct", "audited_session": AUDITED_SESSION,
              "audited_run_id": AUDITED_RUN_ID, "new_session": new_session, "new_run_id": new_run_id,
              "checks": checks, "reports": reports, "inventory": inventory,
              "allowed_differences": {"json_keys": sorted(VOLATILE_KEYS),
                                      "csv_columns": sorted(PROVENANCE_COLUMNS),
                                      "sidecar_keys": sorted(SIDECAR_KEYS),
                                      "sidecar_annotations": SIDECAR_ANNOTATIONS,
                                      "release_records": PROVENANCE_RECORDS,
                                      "tables": "differ only outside the pinned cell comparison, "
                                                "which excludes provenance (run_id, created_utc, "
                                                "data_snapshot_hash, code_commit_sha, config_hash), "
                                                "runtime (wall/cpu seconds, peak memory, recorded_utc) "
                                                "and correction_status columns",
                                      "not_compared": NOT_COMPARED},
              "ok": all(checks.values())}
    if not report["ok"]:
        raise ArchiveRefused("the reconstruction is not equivalent to the audited session: "
                             + json.dumps({k: v for k, v in checks.items() if not v}))
    return report


# -- the archive -------------------------------------------------------------------------

def _tar_bytes(release_dir: Path, files: list[str]) -> bytes:
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb", compresslevel=9, mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
            for rel in files:
                data = (release_dir / rel).read_bytes()
                info = tarfile.TarInfo(f"release/{rel}")
                info.size, info.mtime, info.mode = len(data), 0, 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                tar.addfile(info, io.BytesIO(data))
    return buffer.getvalue()


def write_archive(release_dir: Path | str, drive_root: Path | str, archive_session: str,
                  identity: dict, gate: dict) -> dict:
    """Write the archive to <drive_root>/ARCHIVE_PARENT/<archive_session>/ (must not exist)."""
    release_dir = Path(release_dir)
    if not gate.get("ok"):
        raise ArchiveRefused("the gate did not pass")
    parent = (Path(drive_root) / ARCHIVE_PARENT).resolve()
    dest = (parent / archive_session).resolve()
    if dest.parent != parent or dest.exists():
        raise ArchiveRefused(f"{dest} exists or is outside {parent}")
    files = sorted(listing(release_dir))
    if len(files) != RELEASE_FILES:
        raise ArchiveRefused(f"{len(files)} release files, expected {RELEASE_FILES}")
    shas = {rel: sha256_file(release_dir / rel) for rel in files}
    archive = _tar_bytes(release_dir, files)
    dest.mkdir(parents=True)
    (dest / "release.tar.gz").write_bytes(archive)
    with open(dest / "archive_inventory.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["path", "bytes", "sha256"])
        for rel in files:
            writer.writerow([rel, (release_dir / rel).stat().st_size, shas[rel]])
    (dest / "acceptance_report.json").write_text(json.dumps(gate, indent=1))
    manifest = {"archive_session": archive_session, "published": False, "estimation": "none",
                "acceptance_report_sha256": sha256_file(dest / "acceptance_report.json"),
                "files": len(files), "release_tar_sha256": sha256_bytes(archive),
                "archive_inventory_sha256": sha256_file(dest / "archive_inventory.csv"),
                "release_inventory_sha256": shas[INVENTORY], "identity": identity, "gate": gate}
    (dest / "archive_manifest.json").write_text(json.dumps(manifest, indent=1))
    verify_archive(dest)
    return manifest


def verify_archive(dest: Path | str) -> dict:
    """Re-read the written archive: tar sha256, and every member against the inventory."""
    dest = Path(dest)
    manifest = json.loads((dest / "archive_manifest.json").read_text())
    if sha256_file(dest / "release.tar.gz") != manifest["release_tar_sha256"]:
        raise ArchiveRefused("release.tar.gz does not match its manifest")
    if sha256_file(dest / "archive_inventory.csv") != manifest["archive_inventory_sha256"]:
        raise ArchiveRefused("archive_inventory.csv does not match its manifest")
    if sha256_file(dest / "acceptance_report.json") != manifest["acceptance_report_sha256"]:
        raise ArchiveRefused("acceptance_report.json does not match its manifest")
    inventory = {r["path"]: r["sha256"] for r in csv.DictReader(open(dest / "archive_inventory.csv"))}
    seen = {}
    with tarfile.open(dest / "release.tar.gz", "r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile() or not member.name.startswith("release/"):
                raise ArchiveRefused(f"unexpected archive member {member.name}")
            seen[member.name[len("release/"):]] = sha256_bytes(tar.extractfile(member).read())
    if seen != inventory or len(seen) != RELEASE_FILES:
        raise ArchiveRefused("archive members do not match the inventory")
    return {"verified_members": len(seen), "release_tar_sha256": manifest["release_tar_sha256"]}


def run_identity(*, mode: str, archive_session: str, archive_tool_commit: str,
                 orchestration_commit: str, scientific_commit: str, run_id: str,
                 source_session: str) -> dict:
    return {"mode": mode, "archive_session": archive_session,
            "archive_tool_commit": archive_tool_commit,
            "orchestration_commit": orchestration_commit, "scientific_commit": scientific_commit,
            "source_session": source_session, "source_run_id": run_id,
            "audited_session": AUDITED_SESSION, "audited_run_id": AUDITED_RUN_ID,
            "audited_export_manifest_sha256": AUDITED_EXPORT_MANIFEST_SHA256,
            "python": os.sys.version.split()[0]}
