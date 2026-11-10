"""Recovery of an interrupted D3 publication of release `part8-final-20261109`.

A Colab runtime can be lost between the external steps of `r1_part8_final_release.publish`:
  Drive `<release>.partial` written -> GitHub branch pushed -> Drive renamed -> status.
A new runtime cannot simply re-run the release, because it would render, assemble and
commit again with new operation IDs. Recovery therefore **never creates a new identity**.
It reads the identity of the interrupted publication from what was already written, proves
that this is the approved release, and finishes only the steps that are missing.

External state (`inspect_state`), and what recovery may do with explicit authorization
(AUTHORIZE_RECOVERY, separate from AUTHORIZE_PUBLICATION):

  not_started          no branch, no partial, no final   -> refuse: use the normal run
  drive_partial_only   partial only (the push never landed) -> rebuild the SAME release
                       from the verified partial payload (its tar and record), commit it
                       locally, push the new branch, finalize Drive, record the status
  github_drive_partial branch + partial                -> finalize Drive, record the status
  complete_no_status   branch + final, no status file   -> record the status only
  published            branch + final + status          -> verify only; change nothing
  conflict             anything else                    -> refuse

Before any action, everything that exists is verified cryptographically against the
verified candidate archive and the approved release:
  * the Drive payload: every tar member against `release_inventory.csv`; the manifest
    against the inventory; the manifest's identities (release id, branch, numbers run,
    scientific pin, archive, F8 operation id, publication id);
  * the release tree rebuilt from the payload's tar, against the extracted archive: exactly
    the 25 allowed paths differ, the 12 F3.4 figures equal the approved F8 hashes, and every
    sidecar carries complete provenance naming the manifest's F8 operation;
  * the GitHub commit, if it exists: its parent is the pin, it changes only
    `my-thesis/output/` and `my-thesis/release/part8_final/`, and every blob equals the
    payload's tree and record. GitHub and Drive therefore hold the same release.
Any conflict refuses. Nothing is overwritten, deleted or force-pushed. An incomplete or
unverifiable partial folder is left untouched; deciding what to do with it is a human
decision.
"""
from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r1_part8_final_release as rel  # noqa: E402

RECORD_FILES = ("release_inventory.csv", "release_manifest.json", "RELEASE.md",
                "archive_to_release_diff.csv")
STATES = ("not_started", "drive_partial_only", "github_drive_partial", "complete_no_status",
          "published", "conflict")


class RecoveryRefused(RuntimeError):
    """The interrupted publication cannot be recovered safely; nothing was changed."""


def drive_paths(drive_root: Path) -> tuple[Path, Path]:
    parent = Path(drive_root) / rel.DRIVE_RELEASE_PARENT
    return parent / f"{rel.RELEASE_ID}.partial", parent / rel.RELEASE_ID


def inspect_state(repo: Path, drive_root: Path, git_env: dict | None = None,
                  remote_head: Callable | None = None) -> dict:
    """Classify the external state. Reads only."""
    remote_head = remote_head or rel.remote_branch_head
    partial, final = drive_paths(drive_root)
    head = remote_head(repo, rel.RELEASE_BRANCH, git_env)
    status_file = final / "publication_status.json"
    facts = {"remote_head": head, "partial_exists": partial.exists(), "final_exists": final.exists(),
             "status_exists": status_file.exists(), "partial": str(partial), "final": str(final)}
    key = (head is not None, facts["partial_exists"], facts["final_exists"], facts["status_exists"])
    state = {(False, False, False, False): "not_started",
             (False, True, False, False): "drive_partial_only",
             (True, True, False, False): "github_drive_partial",
             (True, False, True, False): "complete_no_status",
             (True, False, True, True): "published"}.get(key, "conflict")
    facts["state"] = state
    if state == "conflict":
        facts["reason"] = _conflict_reason(*key)
    return facts


def _conflict_reason(remote, partial, final, status) -> str:
    if final and not remote:
        return "the final Drive folder exists but the release branch does not"
    if remote and not partial and not final:
        return "the release branch exists but no Drive copy does"
    if partial and final:
        return "both the partial and the final Drive folders exist"
    if status and not final:
        return "a status file exists without the final folder"
    return "unexpected combination"


# -- verification of what exists --------------------------------------------------------------

def verify_payload_identity(folder: Path) -> dict:
    """Payload members and manifest; returns the interrupted publication's manifest."""
    missing = [n for n in ("release.tar.gz", *RECORD_FILES) if not (folder / n).is_file()]
    if missing:
        raise RecoveryRefused(f"{folder} is incomplete (missing {missing}); left untouched")
    try:
        rel.verify_drive_payload(folder)
    except (rel.ReleaseRefused, OSError, EOFError, ValueError, KeyError) as exc:
        raise RecoveryRefused(f"{folder} does not verify ({exc}); left untouched") from exc
    manifest = json.loads((folder / "release_manifest.json").read_text())
    ids = manifest.get("identities", {})
    expected = {
        "release_id": (manifest.get("release_id"), rel.RELEASE_ID),
        "release_branch": (manifest.get("release_branch"), rel.RELEASE_BRANCH),
        "canonical_path": (manifest.get("canonical_path"), rel.OUTPUT_PREFIX),
        "files": (manifest.get("files"), rel.RELEASE_FILES),
        "numbers.run_id": (ids.get("numbers", {}).get("run_id"), rel.NUMBERS_RUN_ID),
        "numbers.scientific_commit": (ids.get("numbers", {}).get("scientific_commit"), rel.SCIENTIFIC_PIN),
        "archive.session": (ids.get("archive", {}).get("session"), rel.ARCHIVE_SESSION),
        "archive.release_tar_sha256": (ids.get("archive", {}).get("release_tar_sha256"),
                                       rel.ARCHIVE_TAR_SHA256),
        "figure.plotting_code_commit": (ids.get("figure", {}).get("plotting_code_commit"),
                                        rel.SCIENTIFIC_PIN),
        "figure.renderer_sha256": (ids.get("figure", {}).get("renderer_sha256"), rel.RENDERER_SHA256),
        "estimation": (manifest.get("estimation"), "none"),
    }
    wrong = {k: v[0] for k, v in expected.items() if v[0] != v[1]}
    import re
    if not re.fullmatch(r"f8render-\d{8}T\d{6}Z-[0-9a-f]{6}", str(ids.get("figure", {}).get("operation_id"))):
        wrong["figure.operation_id"] = ids.get("figure", {}).get("operation_id")
    if not re.fullmatch(r"publish-\d{8}T\d{6}Z-[0-9a-f]{6}",
                        str(ids.get("publication", {}).get("publication_id"))):
        wrong["publication.publication_id"] = ids.get("publication", {}).get("publication_id")
    if sorted(manifest.get("changed_paths_vs_archive", [])) != sorted(rel.ALLOWED_CHANGES):
        wrong["changed_paths_vs_archive"] = "not the 25 allowed paths"
    if rel.PLACEHOLDER.search(json.dumps(manifest)):
        wrong["placeholder"] = True
    if wrong:
        raise RecoveryRefused(f"the payload's identity is not the approved release: {wrong}")
    return manifest


def rebuild_from_payload(folder: Path, work: Path, archive_tree: Path, manifest: dict) -> tuple[Path, Path]:
    """The release tree and record exactly as published, re-verified against the archive."""
    tree, record = work / "recovered_tree", work / "recovered_record"
    if tree.exists() or record.exists():
        raise RecoveryRefused(f"{work} already holds a recovered release")
    try:
        rel.safe_extract(folder / "release.tar.gz", tree)
        record.mkdir(parents=True)
        for name in RECORD_FILES:
            shutil.copyfile(folder / name, record / name)
        rel.verify_release_tree(tree, archive_tree, manifest["identities"]["figure"]["operation_id"])
        rel.verify_release_tree_record(tree, record)
        _check_diff_record(tree, archive_tree, record)
    except rel.ReleaseRefused as exc:
        raise RecoveryRefused(f"the payload is not the approved release: {exc}") from exc
    return tree, record


def _check_diff_record(tree: Path, archive_tree: Path, record: Path) -> None:
    new, old = rel.listing(tree), rel.listing(archive_tree)
    rows = list(csv.DictReader(open(record / "archive_to_release_diff.csv", newline="")))
    got = {r["path"]: (r["archived_sha256"], r["release_sha256"]) for r in rows}
    want = {p: (old[p], new[p]) for p in rel.ALLOWED_CHANGES}
    if got != want:
        raise rel.ReleaseRefused("archive_to_release_diff.csv does not match the release")


def verify_remote_commit(repo: Path, commit: str, tree: Path, record: Path, git_env=None,
                         fetch: Callable | None = None) -> dict:
    """The published GitHub commit holds exactly the payload's tree and record."""
    if fetch is None:
        subprocess.run(["git", "fetch", "-q", "origin", rel.RELEASE_BRANCH], cwd=repo, env=git_env,
                       check=True)
    else:
        fetch()
    try:
        return rel.verify_git_commit(repo, commit, tree, record)
    except (rel.ReleaseRefused, subprocess.CalledProcessError) as exc:
        raise RecoveryRefused(f"the GitHub commit {commit} does not match the Drive payload: {exc}") from exc


def verify_published_status(status: dict, *, commit: str, final: Path, publication_id: str,
                            tar_sha256: str) -> None:
    """An existing `published` status must describe exactly the independently verified release.

    `commit` is the remote branch head, already verified blob by blob against the Drive payload;
    `publication_id` and `tar_sha256` come from that verified payload. A status written by the
    normal publication does not record the publication ID: there it is bound by the verified
    commit, whose release_manifest.json equals the payload's. A status that records one (every
    recovered status does) must record exactly this one.
    """
    problems = []
    if not isinstance(status, dict):
        raise RecoveryRefused("the existing status file is not a JSON object")
    if status.get("state") != "published":
        problems.append(f"state {status.get('state')!r}")
    if status.get("release_id") != rel.RELEASE_ID:
        problems.append(f"release_id {status.get('release_id')!r}")
    if status.get("branch") != rel.RELEASE_BRANCH:
        problems.append(f"branch {status.get('branch')!r}")
    if status.get("commit") != commit:
        problems.append(f"commit {status.get('commit')!r} is not the verified branch head {commit}")
    if "publication_id" in status or status.get("recovered"):
        if status.get("publication_id") != publication_id:
            problems.append(f"publication_id {status.get('publication_id')!r} is not {publication_id}")
    if status.get("drive_final") != str(final):
        problems.append(f"drive_final {status.get('drive_final')!r} is not {final}")
    steps = status.get("steps") if isinstance(status.get("steps"), list) else []
    states = [step.get("state") for step in steps if isinstance(step, dict)]
    if states[-3:] != ["drive_staged", "github_verified", "published"]:
        problems.append(f"steps {states} do not end drive_staged, github_verified, published")
    for step in steps:
        if isinstance(step, dict) and step.get("state") in ("drive_staged", "published") \
                and step.get("tar_sha256") != tar_sha256:
            problems.append(f"{step.get('state')} tar_sha256 {step.get('tar_sha256')!r} is not {tar_sha256}")
        if isinstance(step, dict) and step.get("state") == "github_verified" \
                and step.get("remote_head") != commit:
            problems.append(f"github_verified remote_head {step.get('remote_head')!r} is not {commit}")
    if not any(isinstance(s, dict) and s.get("state") == "published" and s.get("tar_sha256")
               for s in steps):
        problems.append("no recorded tar sha256 for the published step")
    if not str(status.get("published_utc", "")):
        problems.append("published_utc missing")
    if problems:
        raise RecoveryRefused("the existing status file does not match the verified release: "
                              + "; ".join(problems))


# -- recovery ---------------------------------------------------------------------------------

def recover(*, authorized: bool, repo: Path, drive_root: Path, archive_tree: Path, work: Path,
            status_path: Path, git_env: dict | None = None, push: Callable | None = None,
            remote_head: Callable | None = None, rename: Callable | None = None,
            fetch: Callable | None = None) -> dict:
    """Verify, then (only if authorized) finish the missing steps of the interrupted publication."""
    push = push or rel._push_branch
    remote_head = remote_head or rel.remote_branch_head
    rename = rename or (lambda src, dst: __import__("os").rename(src, dst))
    facts = inspect_state(repo, drive_root, git_env, remote_head)
    state = facts["state"]
    partial, final = drive_paths(drive_root)
    log = {"mode": "recovery", "inspected": facts, "steps": []}

    def note(step: str, **detail):
        log["steps"].append({"step": step, "utc": rel.utc_stamp(), **detail})
        status_path.write_text(json.dumps(log, indent=1), encoding="utf-8")

    if state == "not_started":
        raise RecoveryRefused("nothing was published: use the normal release run, not recovery")
    if state == "conflict":
        raise RecoveryRefused(f"conflicting external state: {facts['reason']}; nothing changed")

    folder = final if state in ("complete_no_status", "published") else partial
    manifest = verify_payload_identity(folder)
    tree, record = rebuild_from_payload(folder, work, archive_tree, manifest)
    payload = rel.verify_drive_payload(folder)
    identity = {"publication_id": manifest["identities"]["publication"]["publication_id"],
                "figure_operation_id": manifest["identities"]["figure"]["operation_id"],
                "release_tar_sha256": payload["release_tar_sha256"]}
    note("verified_payload", folder=str(folder), **identity)

    if state != "drive_partial_only":
        commit = facts["remote_head"]
        verify_remote_commit(repo, commit, tree, record, git_env, fetch)
        note("verified_github", commit=commit)
    if state == "published":
        try:
            existing = json.loads((final / "publication_status.json").read_text())
        except ValueError as exc:
            raise RecoveryRefused(f"the existing status file is not valid JSON: {exc}") from exc
        verify_published_status(existing, commit=facts["remote_head"], final=final,
                                publication_id=identity["publication_id"],
                                tar_sha256=identity["release_tar_sha256"])
        note("already_published", commit=facts["remote_head"])
        log["result"] = "already_published"
        return log
    if not authorized:
        note("not_authorized", would="finish " + {"drive_partial_only": "push, Drive finalization, status",
                                                  "github_drive_partial": "Drive finalization, status",
                                                  "complete_no_status": "status"}[state])
        log["result"] = "not_authorized"
        return log

    if state == "drive_partial_only":
        message = (f"Part 8 final corrected release {rel.RELEASE_ID}\n\n"
                   f"Publication {identity['publication_id']} (recovered after a lost runtime; "
                   f"same release as the verified Drive payload, tar sha256 {identity['release_tar_sha256']}).\n"
                   f"Numbers: run {rel.NUMBERS_RUN_ID}; scientific code {rel.SCIENTIFIC_PIN}. "
                   f"F3.4: F8 re-render {identity['figure_operation_id']}. No estimation.\n")
        try:
            commit = rel.stage_git(repo, work / "recovered_stage", tree, record, message)
            rel.verify_git_commit(repo, commit, tree, record)
        except rel.ReleaseRefused as exc:
            raise RecoveryRefused(f"could not stage the recovered commit: {exc}") from exc
        if remote_head(repo, rel.RELEASE_BRANCH, git_env) is not None:
            raise RecoveryRefused("the release branch appeared during recovery; nothing pushed")
        push(repo, commit, rel.RELEASE_BRANCH, git_env)
        if remote_head(repo, rel.RELEASE_BRANCH, git_env) != commit:
            raise RecoveryRefused("the pushed branch is not at the recovered commit")
        note("github_verified", commit=commit, pushed=True)
    else:
        commit = facts["remote_head"]

    if state in ("drive_partial_only", "github_drive_partial"):
        if final.exists():
            raise RecoveryRefused(f"{final} appeared during recovery; nothing renamed")
        rename(partial, final)
        if rel.verify_drive_payload(final)["release_tar_sha256"] != identity["release_tar_sha256"]:
            raise RecoveryRefused("the finalized Drive folder differs from the verified payload")
        note("drive_finalized", final=str(final))

    status_file = final / "publication_status.json"
    if status_file.exists():
        raise RecoveryRefused("a status file appeared during recovery; it is not overwritten")
    status = {"release_id": rel.RELEASE_ID, "branch": rel.RELEASE_BRANCH, "commit": commit,
              "drive_partial": str(partial), "drive_final": str(final), "state": "published",
              "published_utc": rel.utc_stamp(), "recovered": True,
              "recovery": {"from_state": state, "steps": log["steps"]},
              "steps": [{"state": "drive_staged", "tar_sha256": identity["release_tar_sha256"],
                         "verified_in_recovery": True},
                        {"state": "github_verified", "remote_head": commit, "verified_in_recovery": True},
                        {"state": "published", "tar_sha256": identity["release_tar_sha256"],
                         "utc": rel.utc_stamp()}],
              "publication_id": identity["publication_id"]}
    status_file.write_text(json.dumps(status, indent=1), encoding="utf-8")
    note("published", commit=commit)
    log["result"] = "published"
    log["status"] = status
    return log
