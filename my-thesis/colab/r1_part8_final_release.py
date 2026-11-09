"""D3: assembly and guarded publication of the final corrected Part 8 release.

Non-estimating. The release is the verified candidate archive
`archive-20261109T080914Z-3c7d68` with exactly one approved presentation amendment, F8
(readable F3.4 main panel, approved 9 November 2026).

Exactly 25 paths may differ from the archive: the 12 F3.4 PNG/PDF figures, their 12
provenance sidecars and `manifests/output_inventory.csv`. The other 440 files must be
byte-identical to the archive. Anything else refuses the release.

Canonical location (CLAUDE.md §9; decision in `reports/part8/final/SOURCE_OF_TRUTH.md`):
the release commit, on the new branch `part8-corrected-results/final-20261109` whose parent
is the scientific pin, holds the 465 files under `my-thesis/output/`. Every path the pin
already has there is updated in place, and four manifest files are added. Nothing is
deleted. The release record goes under `my-thesis/release/part8_final/`.

Three identities are kept apart:
  * numbers   - the run that computed every number: the archived reconstruction
                `correction-20261109T080220-949fcd76`, equivalent to the audited run
                `correction-20261108T053328-949fcd76`;
  * figure    - the F8 re-render operation (`f8render-...`), recorded in each F3.4 sidecar;
  * publication - the publication run (`publish-...`), recorded in the release manifest.

Publication runs only with AUTHORIZE_PUBLICATION. Its order: stage and verify everything
locally; Drive `<release>.partial`; verify; push the new GitHub branch (never forced) and
verify the remote; rename the Drive folder to its final name; verify; write the status.
`published` is recorded only after both destinations are verified.

CLI (run with the approved environment's Python, in a checkout whose scientific code
equals the pin):
    python r1_part8_final_release.py render TREE ARCHIVE_INVENTORY OUT RENDERER
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r1_integration_archive as arc  # noqa: E402

# -- identities -------------------------------------------------------------------------
SCIENTIFIC_PIN = "8aaa4217536ab3cb942dd248dd19ece7838a8d60"
ARCHIVE_SESSION = "archive-20261109T080914Z-3c7d68"
ARCHIVE_PARENT = arc.ARCHIVE_PARENT                     # baseline/r1_part8_candidate_archive
ARCHIVE_TAR_SHA256 = "54b61285a732f44d9ef9f1a5e97e6a04f45f287f49dbcf044e6d2574d1d7b4ee"
ARCHIVE_INVENTORY_SHA256 = "24ee8bee0ca0aca3850c2bffdb1e842e7576275c741d38ba7c09841886209a58"
ARCHIVE_RELEASE_INVENTORY_SHA256 = "72c8530f6c1a5c7515f1088b3fecead33c065f06509404f2dd0aeea20d0f24da"
ARCHIVE_TOOL_COMMIT = "878d9289986e48bcf40c8ff4e32f22f620cf0937"
NUMBERS_RUN_ID = "correction-20261109T080220-949fcd76"            # the archived reconstruction
NUMBERS_SESSION = "integration-20261109T075322Z-16749b"
AUDITED_RUN_ID = arc.AUDITED_RUN_ID                               # correction-20261108T053328-...
AUDITED_SESSION = arc.AUDITED_SESSION
ORCHESTRATION_COMMIT = arc.AUDITED_ORCHESTRATION

RELEASE_ID = "part8-final-20261109"
RELEASE_BRANCH = "part8-corrected-results/final-20261109"
DRIVE_RELEASE_PARENT = "baseline/r1_part8_final_release"
OUTPUT_PREFIX = "my-thesis/output"
RECORD_PREFIX = "my-thesis/release/part8_final"
RELEASE_FILES = 465
INVENTORY = "manifests/output_inventory.csv"
F8_APPROVED = "2026-11-09"
F8_TEXT = ("F8 readable main panel (Part 5 §13.1), approved 9 November 2026: flagged "
           "forecasts are omitted from the main panel and shown in the diagnostic panel; "
           "presentation only, no number changed")
RENDERER = "my-thesis/reports/part8/corrections/r1/f8_review/f8_render.py"
RENDERER_SHA256 = "6a8e4eeb54af3b39c66068aa4c19e253eb9983b6863a660e9ea77b579633947f"
INVENTORY_SOURCE_F8 = "presentation_amendment_f8"

TARGETS = ("GDPC1", "CPIAUCSL", "UNRATE", "INDPRO", "FEDFUNDS", "M2SL")
F34 = tuple(f"figures/F3.4_{t}.{ext}" for t in TARGETS for ext in ("png", "pdf"))
SIDECARS = tuple(f"{p}.provenance.json" for p in F34)
ALLOWED_CHANGES = frozenset(F34 + SIDECARS + (INVENTORY,))          # exactly 25 paths
# The reviewed F8 figures (commit 9c873a1, f8_review/f8_figure_hashes.csv), approved 9 Nov 2026.
APPROVED_F8 = {
    "figures/F3.4_GDPC1.png": "d91573f66636124c852fec263a2fe64544150c50e2e773dfd2e2c744d4cf0b0f",
    "figures/F3.4_GDPC1.pdf": "4c283f200cbcef318397975e839d9b6a9fdee03be2d5ab6b0c14d2535f61ee80",
    "figures/F3.4_CPIAUCSL.png": "9ef97dd5f98389cb72a91b42f52760e3f3608646152eab320bc015e4b60dfd07",
    "figures/F3.4_CPIAUCSL.pdf": "51f709bf598d551b143142fd7322fcc1e12db3cac7058e72d97d3b15eb99f088",
    "figures/F3.4_UNRATE.png": "d50c36008bb96c8467ff34b830b10e21693e7ef87c446b39929a926bddc93d13",
    "figures/F3.4_UNRATE.pdf": "8a50e282229ad9a23fef9868a00b9c6d5204d9d5fb8aad6e7099a24473836cf1",
    "figures/F3.4_INDPRO.png": "6d6f58694382fb2287b0aff74d182616b9927cdb9234960e86dedbef9bb6aa3f",
    "figures/F3.4_INDPRO.pdf": "195f3403c135f0f03350e63e5eabb44e34f39d6423e8e81bacb9358a96f27e7f",
    "figures/F3.4_FEDFUNDS.png": "ad961b1fb6829459c006737f68660967596d3464308e5018fdb56cb10125290a",
    "figures/F3.4_FEDFUNDS.pdf": "ae2e7e32d19a3b0c0541968e9c7867c26e68bd5c1d789e7d8e4868d2677a8a14",
    "figures/F3.4_M2SL.png": "b08e0baaa145c0168b2a56e21b269fee3fa3a242e1e15e7c6efdeab286d58a2d",
    "figures/F3.4_M2SL.pdf": "5f173c934ce04ca8805c4abc3d83554e6f67280db7afce7a8e466e41ce16acc5",
}
SIDECAR_REQUIRED = ("artifact", "code_commit_sha", "config_hash", "created_utc",
                    "data_snapshot_hash", "figure_id", "horizon", "run_id", "series",
                    "numbers_run_id", "numbers_audited_run_id", "figure_operation",
                    "figure_sha256", "presentation_amendment")
# Paths that must equal the scientific pin in the rendering checkout (scientific code,
# configuration, environment lock and frozen data) ...
CODE_AT_PIN = ("my-thesis/code/src", "my-thesis/code/configs",
               "my-thesis/code/requirements.lock.txt", "my-thesis/code/requirements.constraints.txt",
               "my-thesis/data/frozen")
# ... and the rendering guard, which is orchestration tooling added after the pin: it must
# equal the audited orchestration commit that rendered the archived figures.
GUARD_AT_ORCHESTRATION = ("my-thesis/colab/r1_render_guard.py", "my-thesis/colab/matplotlibrc.default")
PLACEHOLDER = re.compile(r"<[^<>\n]*(release|run id|time|todo|placeholder)[^<>\n]*>", re.I)


class ReleaseRefused(RuntimeError):
    """The release cannot be assembled or published as specified."""


sha256_file = arc.sha256_file
sha256_bytes = arc.sha256_bytes
listing = arc.listing


def utc_stamp() -> str:
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())


def new_operation_id(kind: str) -> str:
    return f"{kind}-{utc_stamp()}-{secrets.token_hex(3)}"


# -- 1. the archive ------------------------------------------------------------------------

def verify_archive_folder(folder: Path | str) -> dict:
    """The candidate archive on Drive: hashes, manifest identity and every tar member."""
    folder = Path(folder)
    if folder.name != ARCHIVE_SESSION:
        raise ReleaseRefused(f"not the approved archive: {folder}")
    if sha256_file(folder / "release.tar.gz") != ARCHIVE_TAR_SHA256:
        raise ReleaseRefused("release.tar.gz is not the verified archive")
    if sha256_file(folder / "archive_inventory.csv") != ARCHIVE_INVENTORY_SHA256:
        raise ReleaseRefused("archive_inventory.csv is not the verified inventory")
    manifest = json.loads((folder / "archive_manifest.json").read_text())
    identity = manifest.get("identity", {})
    expected = {"published": False, "estimation": "none", "files": RELEASE_FILES,
                "release_tar_sha256": ARCHIVE_TAR_SHA256,
                "archive_inventory_sha256": ARCHIVE_INVENTORY_SHA256,
                "release_inventory_sha256": ARCHIVE_RELEASE_INVENTORY_SHA256}
    wrong = {k: manifest.get(k) for k, v in expected.items() if manifest.get(k) != v}
    ident = {"scientific_commit": SCIENTIFIC_PIN, "orchestration_commit": ORCHESTRATION_COMMIT,
             "archive_tool_commit": ARCHIVE_TOOL_COMMIT, "source_run_id": NUMBERS_RUN_ID,
             "audited_run_id": AUDITED_RUN_ID, "archive_session": ARCHIVE_SESSION}
    wrong.update({f"identity.{k}": identity.get(k) for k, v in ident.items() if identity.get(k) != v})
    if not manifest.get("gate", {}).get("ok") or not all(manifest["gate"]["checks"].values()):
        wrong["gate"] = "not passed"
    if wrong:
        raise ReleaseRefused(f"archive manifest differs from the verified archive: {wrong}")
    members = arc.verify_archive(folder)          # tar, inventory and acceptance-report hashes
    return {"archive": ARCHIVE_SESSION, "members": members["verified_members"],
            "release_tar_sha256": ARCHIVE_TAR_SHA256, "numbers_run_id": NUMBERS_RUN_ID}


def safe_extract(tar_path: Path | str, dest: Path | str) -> Path:
    """Extract the 465 `release/` members into dest (refuses links, escapes, a used dest)."""
    dest = Path(dest)
    if dest.exists() and any(dest.iterdir()):
        raise ReleaseRefused(f"{dest} is not empty")
    dest.mkdir(parents=True, exist_ok=True)
    root = dest.resolve()
    with tarfile.open(tar_path, "r:gz") as tar:
        members = tar.getmembers()
        for member in members:
            name = member.name
            if not member.isfile() or not name.startswith("release/") or ".." in Path(name).parts:
                raise ReleaseRefused(f"unexpected archive member {name!r}")
            target = (root / name[len("release/"):]).resolve()
            if root not in target.parents:
                raise ReleaseRefused(f"archive member escapes the destination: {name!r}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(tar.extractfile(member).read())
    if len(listing(dest)) != RELEASE_FILES:
        raise ReleaseRefused(f"{len(listing(dest))} files extracted, expected {RELEASE_FILES}")
    return dest


def read_csv_inventory(path: Path | str) -> dict[str, dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return {row["path"]: row for row in csv.DictReader(fh)}


def check_tree_against_archive_inventory(tree: Path, archive_inventory: Path) -> None:
    expected = {p: r["sha256"] for p, r in read_csv_inventory(archive_inventory).items()}
    found = listing(tree)
    if found != expected:
        bad = sorted(p for p in set(found) | set(expected) if found.get(p) != expected.get(p))
        raise ReleaseRefused(f"extracted tree differs from the archive inventory: {bad[:10]}")


# -- 2. rendering (CLI, approved environment) ----------------------------------------------

def load_renderer(path: Path | str):
    """The reviewed F8 renderer, sha256-pinned. Importing it pins the default matplotlib rc."""
    path = Path(path)
    if sha256_file(path) != RENDERER_SHA256:
        raise ReleaseRefused("f8_render.py is not the reviewed renderer")
    spec = importlib.util.spec_from_file_location("f8_render", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render_cli(tree: str, archive_inventory: str, out: str, renderer: str) -> int:
    """Render F3.4 with F8 off and on, under the estimation guard. Never estimates."""
    module = load_renderer(renderer)              # before any matplotlib import
    from thesis.correction import guard           # noqa: E402  (path set by the renderer)
    with guard.estimation_forbidden() as state:
        code = module.main(tree, archive_inventory, out)
        permitted = dict(state.permitted)
    if permitted:
        raise ReleaseRefused(f"an estimation was permitted during rendering: {permitted}")
    report = json.loads((Path(out) / "render_report.json").read_text())
    report["estimations_permitted"] = permitted
    report["renderer_sha256"] = RENDERER_SHA256
    (Path(out) / "render_report.json").write_text(json.dumps(report, indent=1))
    return code


def check_render(render_dir: Path | str, archive_tree: Path | str) -> dict:
    """F8 off must reproduce the archived figures; F8 on must equal the approved figures."""
    render_dir, archive_tree = Path(render_dir), Path(archive_tree)
    report = json.loads((render_dir / "render_report.json").read_text())
    if not report.get("render_guard", {}).get("ok"):
        raise ReleaseRefused("render guard did not pass")
    if report.get("estimations_permitted"):
        raise ReleaseRefused("estimation during rendering")
    problems = []
    for rel in F34:
        name = Path(rel).name
        legacy = sha256_file(render_dir / "legacy" / name)
        if legacy != sha256_file(archive_tree / rel):
            problems.append(f"F8-off render of {name} differs from the archive")
        if sha256_file(render_dir / "f8" / name) != APPROVED_F8[rel]:
            problems.append(f"F8 render of {name} differs from the approved figure")
    if problems:
        raise ReleaseRefused("; ".join(problems))
    return {"legacy_equals_archive": len(F34), "f8_equals_approved": len(F34),
            "render_guard": report["render_guard"]}


# -- 3. assembly ---------------------------------------------------------------------------

def make_sidecar(archived: dict, artifact: str, figure_sha256: str, archived_figure_sha256: str,
                 archived_sidecar_sha256: str, operation: dict) -> dict:
    """Release sidecar: the numbers' run stays the archived run; the figure names its re-render."""
    if archived.get("run_id") != NUMBERS_RUN_ID:
        raise ReleaseRefused(f"{artifact}: archived sidecar run_id {archived.get('run_id')!r} "
                             f"is not the numbers run {NUMBERS_RUN_ID}")
    if archived.get("code_commit_sha") != SCIENTIFIC_PIN or archived.get("artifact") != artifact:
        raise ReleaseRefused(f"{artifact}: archived sidecar does not name the pin or the artifact")
    sidecar = dict(archived)
    sidecar.update({
        "numbers_run_id": NUMBERS_RUN_ID,
        "numbers_audited_run_id": AUDITED_RUN_ID,
        "created_utc": operation["rendered_utc"],
        "figure_operation": {**operation,
                             "archived_figure_created_utc": archived.get("created_utc"),
                             "archived_figure_sha256": archived_figure_sha256,
                             "archived_sidecar_sha256": archived_sidecar_sha256},
        "figure_sha256": figure_sha256,
        "presentation_amendment": F8_TEXT,
    })
    return sidecar


def render_operation(operation_id: str, rendered_utc: str, tool_commit: str) -> dict:
    if not re.fullmatch(r"f8render-\d{8}T\d{6}Z-[0-9a-f]{6}", operation_id):
        raise ReleaseRefused(f"bad render operation id {operation_id!r}")
    if not re.fullmatch(r"[0-9a-f]{40}", tool_commit):
        raise ReleaseRefused("the release tool commit must be a full SHA")
    return {"operation": "F8 presentation re-render of F3.4 (no number changed)",
            "operation_id": operation_id, "rendered_utc": rendered_utc,
            "switch": "f8_readable_main_panel=true", "approved": F8_APPROVED,
            "plotting_code_commit": SCIENTIFIC_PIN, "renderer": RENDERER,
            "renderer_sha256": RENDERER_SHA256, "release_tool_commit": tool_commit,
            "rendered_from_archive": ARCHIVE_SESSION}


def rewrite_inventory(archived: bytes, updates: dict[str, tuple[int, str]]) -> bytes:
    """Change only the rows of `updates` (bytes, sha256; source F8); keep every other line."""
    lines = archived.decode("utf-8").split("\n")
    header = lines[0].split(",")
    if header != ["path", "bytes", "sha256", "source", "original_sha256"]:
        raise ReleaseRefused(f"unexpected inventory header {header}")
    seen, out = set(), [lines[0]]
    for line in lines[1:]:
        fields = line.split(",")
        if line and fields[0] in updates:
            if len(fields) != 5:
                raise ReleaseRefused(f"unexpected inventory row {line!r}")
            size, digest = updates[fields[0]]
            line = ",".join([fields[0], str(size), digest, INVENTORY_SOURCE_F8, fields[4]])
            seen.add(fields[0])
        out.append(line)
    if seen != set(updates):
        raise ReleaseRefused(f"inventory rows not found: {sorted(set(updates) - seen)}")
    return "\n".join(out).encode("utf-8")


def assemble(archive_tree: Path | str, render_dir: Path | str, out_tree: Path | str,
             operation: dict) -> dict:
    """Copy the archive, apply exactly the 25 allowed changes, then verify independently."""
    archive_tree, render_dir, out_tree = Path(archive_tree), Path(render_dir), Path(out_tree)
    if out_tree.exists():
        raise ReleaseRefused(f"{out_tree} exists")
    shutil.copytree(archive_tree, out_tree)
    updates = {}
    for rel in F34:
        name = Path(rel).name
        figure = (render_dir / "f8" / name).read_bytes()
        (out_tree / rel).write_bytes(figure)
        updates[rel] = (len(figure), sha256_bytes(figure))
        archived_sidecar = archive_tree / f"{rel}.provenance.json"
        sidecar = make_sidecar(json.loads(archived_sidecar.read_text()), name,
                               sha256_bytes(figure), sha256_file(archive_tree / rel),
                               sha256_file(archived_sidecar), operation)
        data = json.dumps(sidecar, indent=2, sort_keys=True).encode("utf-8")
        (out_tree / f"{rel}.provenance.json").write_bytes(data)
        updates[f"{rel}.provenance.json"] = (len(data), sha256_bytes(data))
    inventory = rewrite_inventory((archive_tree / INVENTORY).read_bytes(), updates)
    (out_tree / INVENTORY).write_bytes(inventory)
    return verify_release_tree(out_tree, archive_tree, operation["operation_id"])


def verify_release_tree(tree: Path | str, archive_tree: Path | str,
                        operation_id: str | None = None) -> dict:
    """Independent check of an assembled release against the archive (refuses on anything)."""
    tree, archive_tree = Path(tree), Path(archive_tree)
    new, old = listing(tree), listing(archive_tree)
    problems = []
    if len(new) != RELEASE_FILES or set(new) != set(old):
        problems.append(f"file set differs from the archive: missing "
                        f"{sorted(set(old) - set(new))[:5]}, extra {sorted(set(new) - set(old))[:5]}")
    changed = sorted(p for p in set(new) & set(old) if new[p] != old[p])
    unexpected = sorted(set(changed) - ALLOWED_CHANGES)
    if unexpected:
        problems.append(f"unexpected changes: {unexpected[:10]}")
    if set(changed) != ALLOWED_CHANGES:
        problems.append(f"allowed paths unchanged: {sorted(ALLOWED_CHANGES - set(changed))}")
    for rel in F34:
        if new.get(rel) != APPROVED_F8[rel]:
            problems.append(f"{rel} is not the approved F8 figure")
        problems.extend(_sidecar_problems(tree, rel, new.get(rel), old, operation_id))
    problems.extend(_inventory_problems(tree, archive_tree, new))
    if problems:
        raise ReleaseRefused("release verification failed: " + "; ".join(problems))
    return {"files": len(new), "identical_to_archive": len(new) - len(changed),
            "changed": changed, "approved_f8": len(F34), "ok": True}


def _sidecar_problems(tree, rel, figure_sha, archived_listing, operation_id) -> list[str]:
    path = tree / f"{rel}.provenance.json"
    try:
        side = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        return [f"{rel}: provenance sidecar missing or unreadable ({exc})"]
    out = [f"{rel}: sidecar lacks {k}" for k in SIDECAR_REQUIRED if k not in side]
    op = side.get("figure_operation", {})
    checks = {"run_id": NUMBERS_RUN_ID, "numbers_run_id": NUMBERS_RUN_ID,
              "numbers_audited_run_id": AUDITED_RUN_ID, "code_commit_sha": SCIENTIFIC_PIN,
              "artifact": Path(rel).name, "figure_id": "F3.4", "figure_sha256": figure_sha,
              "presentation_amendment": F8_TEXT}
    out += [f"{rel}: sidecar {k} = {side.get(k)!r}" for k, v in checks.items() if side.get(k) != v]
    if op.get("plotting_code_commit") != SCIENTIFIC_PIN or op.get("renderer_sha256") != RENDERER_SHA256:
        out.append(f"{rel}: figure_operation does not name the pin and the reviewed renderer")
    if op.get("archived_figure_sha256") != archived_listing.get(rel):
        out.append(f"{rel}: figure_operation does not name the archived figure")
    if operation_id is not None and op.get("operation_id") != operation_id:
        out.append(f"{rel}: figure_operation id differs")
    if PLACEHOLDER.search(path.read_text()):
        out.append(f"{rel}: sidecar contains a placeholder")
    return out


def _inventory_problems(tree: Path, archive_tree: Path, new: dict) -> list[str]:
    out = []
    old_lines = (archive_tree / INVENTORY).read_bytes().decode("utf-8").split("\n")
    new_lines = (tree / INVENTORY).read_bytes().decode("utf-8").split("\n")
    if len(old_lines) != len(new_lines):
        return ["inventory row count changed"]
    rows = read_csv_inventory(tree / INVENTORY)
    if len(rows) != RELEASE_FILES - 1 or set(rows) != set(new) - {INVENTORY}:
        out.append("inventory does not list exactly the 464 other files")
    for a, b in zip(old_lines, new_lines):
        path = b.split(",")[0]
        if path in ALLOWED_CHANGES:
            if not b.endswith("," + a.split(",")[4]) or f",{INVENTORY_SOURCE_F8}," not in b:
                out.append(f"inventory row for {path} not rewritten as specified")
        elif a != b:
            out.append(f"inventory row changed for {path}")
    for path, row in rows.items():
        if new.get(path) != row["sha256"] or (tree / path).stat().st_size != int(row["bytes"]):
            out.append(f"inventory does not match the file on disk: {path}")
    return out


# -- 4. release record ---------------------------------------------------------------------

def release_inventory_bytes(tree: Path) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["path", "bytes", "sha256"])
    for rel, digest in sorted(listing(tree).items()):
        writer.writerow([rel, (tree / rel).stat().st_size, digest])
    return buffer.getvalue().encode("utf-8")


def build_record(tree: Path, archive_tree: Path, record_dir: Path, *, identity: dict,
                 assembly: dict, render: dict, archive: dict) -> dict:
    """my-thesis/release/part8_final/: manifest, inventories, diff and README."""
    if record_dir.exists():
        raise ReleaseRefused(f"{record_dir} exists")
    if not re.fullmatch(r"publish-\d{8}T\d{6}Z-[0-9a-f]{6}", str(identity.get("publication_id", ""))):
        raise ReleaseRefused(f"bad publication id {identity.get('publication_id')!r}")
    record_dir.mkdir(parents=True)
    inventory = release_inventory_bytes(tree)
    (record_dir / "release_inventory.csv").write_bytes(inventory)
    new, old = listing(tree), listing(archive_tree)
    diff = io.StringIO()
    writer = csv.writer(diff, lineterminator="\n")
    writer.writerow(["path", "archived_sha256", "release_sha256", "reason"])
    for rel in sorted(ALLOWED_CHANGES):
        reason = ("F8 figure (approved)" if rel in F34 else
                  "F8 figure provenance sidecar" if rel in SIDECARS else
                  "inventory rows of the 24 amended files")
        writer.writerow([rel, old[rel], new[rel], reason])
    (record_dir / "archive_to_release_diff.csv").write_text(diff.getvalue(), encoding="utf-8")
    manifest = {
        "release_id": RELEASE_ID, "release_branch": RELEASE_BRANCH,
        "canonical_path": OUTPUT_PREFIX, "files": RELEASE_FILES,
        "release_inventory_sha256": sha256_bytes(inventory),
        "output_inventory_sha256": new[INVENTORY],
        "changed_paths_vs_archive": sorted(ALLOWED_CHANGES),
        "identities": {
            "numbers": {"run_id": NUMBERS_RUN_ID, "session": NUMBERS_SESSION,
                        "equivalent_audited_run_id": AUDITED_RUN_ID,
                        "audited_session": AUDITED_SESSION,
                        "orchestration_commit": ORCHESTRATION_COMMIT,
                        "scientific_commit": SCIENTIFIC_PIN},
            "archive": {"session": ARCHIVE_SESSION, "release_tar_sha256": ARCHIVE_TAR_SHA256,
                        "archive_inventory_sha256": ARCHIVE_INVENTORY_SHA256,
                        "archive_tool_commit": ARCHIVE_TOOL_COMMIT},
            "figure": render["operation"],
            "publication": identity,
        },
        "verification": {"archive": archive, "render": render["check"], "assembly": assembly},
        "estimation": "none", "methodology_changed": False,
    }
    text = json.dumps(manifest, indent=1, sort_keys=True)
    if PLACEHOLDER.search(text):
        raise ReleaseRefused("release manifest contains a placeholder")
    (record_dir / "release_manifest.json").write_text(text, encoding="utf-8")
    (record_dir / "RELEASE.md").write_text(release_readme(manifest), encoding="utf-8")
    return manifest


def release_readme(manifest: dict) -> str:
    ids = manifest["identities"]
    return f"""# Final corrected Part 8 release `{RELEASE_ID}`

**Canonical thesis-facing numbers:** `{OUTPUT_PREFIX}/` in this commit ({RELEASE_FILES} files).
Any number used in the thesis must equal a file listed in `release_inventory.csv`
(sha256 `{manifest['release_inventory_sha256']}`). Files under `output/` in any other commit
are superseded or provisional.

| Identity | Value |
|---|---|
| Numbers (every table, forecast and fit) | run `{ids['numbers']['run_id']}` (archived reconstruction), equivalent to audited run `{ids['numbers']['equivalent_audited_run_id']}`; scientific code `{SCIENTIFIC_PIN}` |
| Candidate archive | `{ARCHIVE_SESSION}` (tar sha256 `{ARCHIVE_TAR_SHA256}`) |
| F3.4 figures | F8 re-render `{ids['figure']['operation_id']}` ({ids['figure']['rendered_utc']}); presentation only |
| Publication | `{ids['publication']['publication_id']}` |

**Differences from the archive:** exactly 25 paths (`archive_to_release_diff.csv`): the
12 F3.4 figures (F8, approved {F8_APPROVED}), their 12 provenance sidecars and
`manifests/output_inventory.csv`. All other 440 files are byte-identical to the archive.

**Limitations carried by the release** (see `reports/part8/final/`): F6 (no global MSAR
maximum; UNRATE K=3 inconclusive), MSAR optimiser sensitivity (B2), nominal p-values
without a predeclared multiple-testing family, degenerate STAR tests, sample- and
window-dependent rankings, the C16 audit sensitivity, and the M2SL diagnostic-panel overlap
in F3.4 (presentation).
"""


# -- 5. GitHub staging and verification ----------------------------------------------------

def _git(args, cwd, env=None, check=True) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise ReleaseRefused(f"git {' '.join(args[:2])} failed: {result.stderr.strip()[:400]}")
    return result.stdout.strip()


def verify_code_at_pin(repo: Path, commit: str) -> None:
    """The rendering checkout holds the pinned scientific code and the audited render guard."""
    if subprocess.run(["git", "diff", "--quiet", SCIENTIFIC_PIN, commit, "--", *CODE_AT_PIN],
                      cwd=repo).returncode != 0:
        raise ReleaseRefused(f"scientific code at {commit} differs from the pin {SCIENTIFIC_PIN}")
    if subprocess.run(["git", "diff", "--quiet", ORCHESTRATION_COMMIT, commit, "--",
                       *GUARD_AT_ORCHESTRATION], cwd=repo).returncode != 0:
        raise ReleaseRefused(f"render guard at {commit} differs from {ORCHESTRATION_COMMIT}")


def remote_branch_head(repo: Path, branch: str, env=None) -> str | None:
    out = _git(["ls-remote", "--heads", "origin", f"refs/heads/{branch}"], repo, env)
    return out.split()[0] if out else None


def stage_git(repo: Path, stage_dir: Path, tree: Path, record_dir: Path, message: str,
              author: tuple[str, str] = ("Thesis pipeline (Colab)",
                                         "thesis-pipeline@users.noreply.github.com")) -> str:
    """A local commit on the pin: tree -> my-thesis/output/, record -> my-thesis/release/part8_final/."""
    if stage_dir.exists():
        raise ReleaseRefused(f"{stage_dir} exists")
    if _git(["branch", "--list", RELEASE_BRANCH], repo):
        raise ReleaseRefused(f"local branch {RELEASE_BRANCH} exists")
    _git(["worktree", "add", "-q", "--detach", str(stage_dir), SCIENTIFIC_PIN], repo)
    output = stage_dir / OUTPUT_PREFIX
    pin_files = set(listing(output))
    for rel in listing(tree):
        target = output / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(tree / rel, target)
    if set(listing(output)) != set(listing(tree)) or not pin_files <= set(listing(tree)):
        raise ReleaseRefused("the release tree would leave or remove files under output/")
    shutil.copytree(record_dir, stage_dir / RECORD_PREFIX)
    _git(["add", "-A", "-f", "--", OUTPUT_PREFIX, RECORD_PREFIX], stage_dir)
    name, email = author
    env = dict(os.environ, GIT_AUTHOR_NAME=name, GIT_AUTHOR_EMAIL=email,
               GIT_COMMITTER_NAME=name, GIT_COMMITTER_EMAIL=email)
    _git(["commit", "-q", "-m", message], stage_dir, env)
    commit = _git(["rev-parse", "HEAD"], stage_dir)
    _git(["branch", RELEASE_BRANCH, commit], repo)
    return commit


def verify_git_commit(repo: Path, commit: str, tree: Path, record_dir: Path) -> dict:
    """The commit is the pin plus exactly the release files; every blob equals the tree."""
    parents = _git(["rev-list", "--parents", "-n", "1", commit], repo).split()[1:]
    if parents != [SCIENTIFIC_PIN]:
        raise ReleaseRefused(f"release commit parent is {parents}, not the scientific pin")
    changes = [line.split("\t") for line in
               _git(["diff", "--name-status", "--no-renames", SCIENTIFIC_PIN, commit], repo).splitlines()]
    bad = [c for c in changes if c[0] not in ("M", "A")
           or not (c[1].startswith(OUTPUT_PREFIX + "/") or c[1].startswith(RECORD_PREFIX + "/"))]
    if bad:
        raise ReleaseRefused(f"release commit changes other paths or deletes files: {bad[:5]}")
    expected = {f"{OUTPUT_PREFIX}/{p}": d for p, d in listing(tree).items()}
    expected.update({f"{RECORD_PREFIX}/{p}": d for p, d in listing(record_dir).items()})
    tracked = set(_git(["ls-tree", "-r", "--name-only", commit, "--", OUTPUT_PREFIX, RECORD_PREFIX],
                       repo).splitlines())
    if tracked != set(expected):
        raise ReleaseRefused("committed files under output/ and release/ differ from the release")
    mismatched = []
    for path, digest in expected.items():
        blob = subprocess.run(["git", "cat-file", "blob", f"{commit}:{path}"], cwd=repo,
                              capture_output=True, check=True).stdout
        if sha256_bytes(blob) != digest:
            mismatched.append(path)
    if mismatched:
        raise ReleaseRefused(f"committed blobs differ from the release: {mismatched[:5]}")
    return {"commit": commit, "parent": SCIENTIFIC_PIN, "files_verified": len(expected),
            "changes": len(changes)}


# -- 6. Drive payload ----------------------------------------------------------------------

def build_drive_payload(tree: Path, record_dir: Path, payload_dir: Path) -> dict:
    if payload_dir.exists():
        raise ReleaseRefused(f"{payload_dir} exists")
    payload_dir.mkdir(parents=True)
    files = sorted(listing(tree))
    (payload_dir / "release.tar.gz").write_bytes(arc._tar_bytes(tree, files))
    for name in ("release_inventory.csv", "release_manifest.json", "RELEASE.md",
                 "archive_to_release_diff.csv"):
        shutil.copyfile(record_dir / name, payload_dir / name)
    return verify_drive_payload(payload_dir)


def verify_drive_payload(folder: Path) -> dict:
    """Every tar member against release_inventory.csv; the manifest against the inventory."""
    inventory = {r["path"]: r["sha256"] for r in
                 csv.DictReader(open(folder / "release_inventory.csv", newline=""))}
    manifest = json.loads((folder / "release_manifest.json").read_text())
    if sha256_file(folder / "release_inventory.csv") != manifest["release_inventory_sha256"]:
        raise ReleaseRefused("release_inventory.csv does not match the manifest")
    seen = {}
    with tarfile.open(folder / "release.tar.gz", "r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile() or not member.name.startswith("release/"):
                raise ReleaseRefused(f"unexpected member {member.name}")
            seen[member.name[len("release/"):]] = sha256_bytes(tar.extractfile(member).read())
    if seen != inventory or len(seen) != RELEASE_FILES:
        raise ReleaseRefused("release.tar.gz members do not match release_inventory.csv")
    return {"members": len(seen), "release_tar_sha256": sha256_file(folder / "release.tar.gz"),
            "files": {p.name: sha256_file(p) for p in sorted(folder.iterdir()) if p.is_file()}}


def _same_payload(a: Path, b: Path) -> bool:
    names = sorted(p.name for p in a.iterdir() if p.is_file())
    return names == sorted(p.name for p in b.iterdir() if p.is_file()) and all(
        sha256_file(a / n) == sha256_file(b / n) for n in names)


# -- 7. publication (only with authorization) ----------------------------------------------

def publish(*, authorized: bool, payload_dir: Path, drive_root: Path, repo: Path, commit: str,
            tree: Path, record_dir: Path, status_path: Path, git_env: dict | None,
            push: Callable[[Path, str, str, dict | None], None] | None = None,
            remote_head: Callable[[Path, str, dict | None], str | None] | None = None,
            rename: Callable[[Path, Path], None] | None = None) -> dict:
    """Drive partial -> GitHub branch -> Drive final -> status. Refuses to overwrite anything.

    The status is appended to `status_path` after every step. `published` is written, and
    `publication_status.json` placed in the final Drive folder, only after both
    destinations verify. On any failure the status names the step and what exists, and
    nothing that exists is deleted or overwritten.
    """
    push = push or _push_branch
    remote_head = remote_head or (lambda r, b, e: remote_branch_head(r, b, e))
    rename = rename or (lambda src, dst: os.rename(src, dst))
    parent = Path(drive_root) / DRIVE_RELEASE_PARENT
    partial, final = parent / f"{RELEASE_ID}.partial", parent / RELEASE_ID
    status = {"release_id": RELEASE_ID, "branch": RELEASE_BRANCH, "commit": commit,
              "drive_partial": str(partial), "drive_final": str(final), "steps": [],
              "state": "staged"}

    def record(state: str, **detail):
        status["state"] = state
        status["steps"].append({"state": state, "utc": utc_stamp(), **detail})
        status_path.write_text(json.dumps(status, indent=1), encoding="utf-8")

    if not authorized:
        record("not_authorized", note="AUTHORIZE_PUBLICATION is False; nothing published")
        return status
    try:
        verify_release_tree_record(tree, record_dir)
        verify_git_commit(repo, commit, tree, record_dir)
        if final.exists():
            raise ReleaseRefused(f"{final} exists; a release is never overwritten")
        existing = remote_head(repo, RELEASE_BRANCH, git_env)
        if existing is not None and existing != commit:
            raise ReleaseRefused(f"remote branch {RELEASE_BRANCH} exists at {existing}")
        # Drive, staged under a name that cannot be mistaken for the release.
        if partial.exists():
            if not _same_payload(partial, payload_dir):
                raise ReleaseRefused(f"{partial} exists with different content")
        else:
            parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(payload_dir, partial)
        drive = verify_drive_payload(partial)
        if not _same_payload(partial, payload_dir):
            raise ReleaseRefused("Drive copy differs from the staged payload")
        record("drive_staged", tar_sha256=drive["release_tar_sha256"])
        # GitHub: a new branch only; a push to an existing branch is never forced.
        if existing is None:
            push(repo, commit, RELEASE_BRANCH, git_env)
        head = remote_head(repo, RELEASE_BRANCH, git_env)
        if head != commit:
            raise ReleaseRefused(f"remote branch head {head} is not the release commit")
        record("github_verified", remote_head=head)
        # Drive, final name; then the status, last.
        rename(partial, final)
        drive_final = verify_drive_payload(final)
        if drive_final["release_tar_sha256"] != drive["release_tar_sha256"]:
            raise ReleaseRefused("final Drive folder differs from the staged copy")
        status["published_utc"] = utc_stamp()
        record("published", tar_sha256=drive_final["release_tar_sha256"])
        (final / "publication_status.json").write_text(json.dumps(status, indent=1), encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 - every failure is recorded, then re-raised
        record("failed", step=status["state"], error=f"{type(exc).__name__}: {exc}"[:600],
               github_branch_exists=_safe(lambda: remote_head(repo, RELEASE_BRANCH, git_env)),
               drive_partial_exists=partial.exists(), drive_final_exists=final.exists())
        raise
    return status


def _safe(fn):
    try:
        return fn()
    except Exception:  # noqa: BLE001
        return "unknown"


def _push_branch(repo: Path, commit: str, branch: str, env: dict | None) -> None:
    """Create the remote branch. No --force; a push to an existing ref is rejected by git."""
    _git(["push", "origin", f"{commit}:refs/heads/{branch}"], repo, env)


def verify_release_tree_record(tree: Path, record_dir: Path) -> None:
    manifest = json.loads((record_dir / "release_manifest.json").read_text())
    if sha256_file(record_dir / "release_inventory.csv") != manifest["release_inventory_sha256"]:
        raise ReleaseRefused("release record inventory does not match its manifest")
    if release_inventory_bytes(tree) != (record_dir / "release_inventory.csv").read_bytes():
        raise ReleaseRefused("release tree changed after the record was written")


if __name__ == "__main__":
    if len(sys.argv) == 6 and sys.argv[1] == "render":
        sys.exit(render_cli(*sys.argv[2:6]))
    print(__doc__)
    sys.exit(2)
