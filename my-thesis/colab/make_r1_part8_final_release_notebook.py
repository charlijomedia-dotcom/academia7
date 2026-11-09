#!/usr/bin/env python3
"""Generate the D3 final-release notebook for Colab (it is not run here).

    python make_r1_part8_final_release_notebook.py <RELEASE_TOOL_COMMIT>

The notebook assembles the final Part 8 release from the verified candidate archive plus the
approved F8 figures, verifies it completely, stages the GitHub commit and the Drive payload
locally, and publishes ONLY if AUTHORIZE_PUBLICATION is set to True (default False). The tool
and the renderer are fetched from RELEASE_TOOL_COMMIT and checked against pinned sha256.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r1_part8_final_release as rel  # noqa: E402

NOTEBOOK = "r1_part8_final_release.ipynb"
TOOL_SHA256 = hashlib.sha256((HERE / "r1_part8_final_release.py").read_bytes()).hexdigest()
ARCHIVE_TOOL_SHA256 = hashlib.sha256((HERE / "r1_integration_archive.py").read_bytes()).hexdigest()

INTRO = f"""# Part 8 final release (D3): assembly, verification and guarded publication

Builds release `{rel.RELEASE_ID}` from the verified candidate archive `{rel.ARCHIVE_SESSION}` plus
the approved F8 figures. **No estimation.** Exactly 25 paths may differ from the archive (the 12
F3.4 figures, their 12 provenance sidecars, `manifests/output_inventory.csv`); the other 440 files
must be byte-identical.

1. Settings: leave `AUTHORIZE_PUBLICATION = False` for the verification run.
2. Run all cells. Everything up to section 6 is local: the archive is verified and extracted, F3.4
   is rendered with F8 off (must equal the archive) and on (must equal the approved figures),
   the release is assembled and verified, the GitHub commit is staged in this runtime, and the
   Drive payload is built and verified.
3. Only with `AUTHORIZE_PUBLICATION = True` does section 7 publish: Drive
   `{rel.DRIVE_RELEASE_PARENT}/{rel.RELEASE_ID}.partial` -> new GitHub branch `{rel.RELEASE_BRANCH}`
   (never forced; refused if it exists) -> Drive renamed to `{rel.RELEASE_ID}` -> status. A failure
   leaves a recorded status and never overwrites anything.

The GitHub write credential is read from Colab Secrets (`GITHUB_TOKEN`) and is never printed.
"""

SETTINGS = f'''# @title Settings
REPOSITORY = "charlijomedia-dotcom/academia7"  # @param {{type:"string"}}
SOURCE_BRANCH = "part8-r1-rescore"
RELEASE_TOOL_COMMIT = "__TOOL__"
RELEASE_TOOL_SHA256 = "{TOOL_SHA256}"
ARCHIVE_TOOL_SHA256 = "{ARCHIVE_TOOL_SHA256}"
DRIVE_ROOT = "/content/drive/MyDrive/KillyPhD/Part8_K3_InSample_2026-10-29"  # @param {{type:"string"}}
AUTHORIZE_PUBLICATION = False  # @param {{type:"boolean"}}
USE_CONSTRAINTS = True
WORK = "/content/r1_part8_final_release"'''

SETUP = '''import os, re, sys, json, time, shutil, secrets, hashlib, subprocess, importlib
from pathlib import Path
try:
    from google.colab import drive, userdata
    drive.mount("/content/drive")
    try:
        GITHUB_TOKEN = userdata.get("GITHUB_TOKEN")
    except Exception:
        GITHUB_TOKEN = None
except ImportError:                       # outside Colab (used only to test this notebook)
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
assert isinstance(AUTHORIZE_PUBLICATION, bool), "AUTHORIZE_PUBLICATION must be True or False"
assert re.fullmatch(r"[0-9a-f]{40}", RELEASE_TOOL_COMMIT), "RELEASE_TOOL_COMMIT must be a full SHA"
DRIVE_ROOT = str(DRIVE_ROOT).strip().rstrip("/")
assert DRIVE_ROOT.startswith("/content/drive/"), "DRIVE_ROOT must be under /content/drive/"
WORK_DIR = Path(WORK)
assert not (WORK_DIR / "tree").exists(), "this runtime already assembled a release; use a fresh runtime"
WORK_DIR.mkdir(parents=True, exist_ok=True)
SECRETS_DIR = WORK_DIR / "secrets"
SECRETS_DIR.mkdir(exist_ok=True)
GIT_ENV = dict(os.environ, GIT_TERMINAL_PROMPT="0")
if GITHUB_TOKEN:
    askpass = SECRETS_DIR / "git_askpass.sh"
    askpass.write_text('#!/bin/sh\\ncase "$1" in\\n  Username*) echo "x-access-token" ;;\\n'
                       '  *) echo "$THESIS_GIT_TOKEN" ;;\\nesac\\n')
    askpass.chmod(0o700)
    GIT_ENV.update(GIT_ASKPASS=str(askpass), THESIS_GIT_TOKEN=GITHUB_TOKEN)
if AUTHORIZE_PUBLICATION:
    assert GITHUB_TOKEN, "publication needs the GITHUB_TOKEN Colab secret"
print("authorize publication:", AUTHORIZE_PUBLICATION, "| GitHub token:", "found" if GITHUB_TOKEN else "not set")'''

CLONE = '''REPO = WORK_DIR / "repo"
url = f"https://github.com/{REPOSITORY}.git"
if not (REPO / ".git").exists():
    subprocess.run(["git", "clone", "-q", "--branch", SOURCE_BRANCH, url, str(REPO)], check=True, env=GIT_ENV)
subprocess.run(["git", "fetch", "-q", "origin", SOURCE_BRANCH], cwd=REPO, check=True, env=GIT_ENV)
subprocess.run(["git", "checkout", "-q", "--detach", RELEASE_TOOL_COMMIT], cwd=REPO, check=True)
assert not subprocess.run(["git", "status", "--porcelain"], cwd=REPO, capture_output=True,
                          text=True, check=True).stdout.strip(), "checkout is dirty"
COLAB_DIR = REPO / "my-thesis" / "colab"
assert hashlib.sha256((COLAB_DIR / "r1_part8_final_release.py").read_bytes()).hexdigest() == RELEASE_TOOL_SHA256
assert hashlib.sha256((COLAB_DIR / "r1_integration_archive.py").read_bytes()).hexdigest() == ARCHIVE_TOOL_SHA256
sys.path.insert(0, str(COLAB_DIR))
import r1_part8_final_release as rel
importlib.reload(rel)
rel.verify_code_at_pin(REPO, RELEASE_TOOL_COMMIT)          # scientific code = pin; guard = a2c3171
RENDERER = REPO / rel.RENDERER
assert hashlib.sha256(RENDERER.read_bytes()).hexdigest() == rel.RENDERER_SHA256
subprocess.run(["git", "fetch", "-q", "origin", rel.SCIENTIFIC_PIN], cwd=REPO, env=GIT_ENV)
subprocess.run(["git", "cat-file", "-e", rel.SCIENTIFIC_PIN + "^{commit}"], cwd=REPO, check=True)
existing = rel.remote_branch_head(REPO, rel.RELEASE_BRANCH, GIT_ENV)
assert existing is None, f"remote branch {rel.RELEASE_BRANCH} already exists at {existing}; nothing is overwritten"
assert not (Path(DRIVE_ROOT) / rel.DRIVE_RELEASE_PARENT / rel.RELEASE_ID).exists(), "the Drive release folder exists"
print("release tool", RELEASE_TOOL_COMMIT[:12], "verified; release branch and Drive folder are free")'''

ENV = '''spec = importlib.util.spec_from_file_location("thesis_colab", COLAB_DIR / "thesis_colab.py")
tc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tc)
CODE = REPO / "my-thesis" / "code"
LOCK = CODE / "requirements.lock.txt"
CONSTRAINTS = CODE / "requirements.constraints.txt" if USE_CONSTRAINTS else None
VENV = WORK_DIR / "venv311"
PY = VENV / "bin" / "python"
try:
    tc.verify_environment(PY, LOCK, constraints=CONSTRAINTS)
except Exception:
    PY = tc.create_environment(VENV, LOCK, constraints=CONSTRAINTS)
FOUND = tc.verify_environment(PY, LOCK, constraints=CONSTRAINTS)
RUN_ENV = dict(os.environ, PYTHONUNBUFFERED="1", MPLBACKEND="Agg")
for _key in ("THESIS_GIT_TOKEN", "GITHUB_TOKEN", "GIT_ASKPASS"):
    RUN_ENV.pop(_key, None)
check = subprocess.run([str(PY), "-u", "code/run_all.py", "--data-only"], cwd=REPO / "my-thesis",
                       env=RUN_ENV, capture_output=True, text=True)
assert check.returncode == 0, "frozen-data verification failed: " + check.stderr[-800:]
print(f"Python {FOUND['python']}; {len(FOUND['packages'])} packages verified; frozen data verified")'''

ARCHIVE = '''ARCHIVE_DIR = Path(DRIVE_ROOT) / rel.ARCHIVE_PARENT / rel.ARCHIVE_SESSION
ARCHIVE_CHECK = rel.verify_archive_folder(ARCHIVE_DIR)         # hashes, identity, all 465 members
LOCAL_ARCHIVE = WORK_DIR / "archive"
LOCAL_ARCHIVE.mkdir(exist_ok=True)
for _name in ("release.tar.gz", "archive_inventory.csv"):
    shutil.copyfile(ARCHIVE_DIR / _name, LOCAL_ARCHIVE / _name)
assert rel.sha256_file(LOCAL_ARCHIVE / "release.tar.gz") == rel.ARCHIVE_TAR_SHA256
ARCH_TREE = rel.safe_extract(LOCAL_ARCHIVE / "release.tar.gz", WORK_DIR / "archive_tree")
rel.check_tree_against_archive_inventory(ARCH_TREE, LOCAL_ARCHIVE / "archive_inventory.csv")
print(json.dumps(ARCHIVE_CHECK))'''

RENDER = '''RENDER_DIR = WORK_DIR / "render"
RENDER_ID = rel.new_operation_id("f8render")
RENDERED_UTC = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
result = subprocess.run([str(PY), str(COLAB_DIR / "r1_part8_final_release.py"), "render",
                         str(ARCH_TREE), str(LOCAL_ARCHIVE / "archive_inventory.csv"),
                         str(RENDER_DIR), str(RENDERER)],
                        cwd=CODE, env=RUN_ENV, capture_output=True, text=True)
print(result.stdout[-1500:], result.stderr[-1500:])
assert result.returncode == 0, "rendering refused"
RENDER_CHECK = rel.check_render(RENDER_DIR, ARCH_TREE)     # F8 off = archive; F8 on = approved
OPERATION = rel.render_operation(RENDER_ID, RENDERED_UTC, RELEASE_TOOL_COMMIT)
print(RENDER_ID, json.dumps(RENDER_CHECK))'''

ASSEMBLE = '''TREE = WORK_DIR / "tree"
RECORD = WORK_DIR / "record"
PUBLICATION_ID = rel.new_operation_id("publish")
ASSEMBLY = rel.assemble(ARCH_TREE, RENDER_DIR, TREE, OPERATION)       # verifies independently
MANIFEST = rel.build_record(TREE, ARCH_TREE, RECORD,
                            identity={"publication_id": PUBLICATION_ID,
                                      "release_tool_commit": RELEASE_TOOL_COMMIT,
                                      "release_branch": rel.RELEASE_BRANCH,
                                      "drive_folder": f"{rel.DRIVE_RELEASE_PARENT}/{rel.RELEASE_ID}"},
                            assembly=ASSEMBLY, render={"operation": OPERATION, "check": RENDER_CHECK},
                            archive=ARCHIVE_CHECK)
print(ASSEMBLY["files"], "files;", ASSEMBLY["identical_to_archive"], "identical to the archive;",
      len(ASSEMBLY["changed"]), "changed (the 25 allowed paths)")'''

STAGE = '''STAGE_DIR = WORK_DIR / "stage"
MESSAGE = (f"Part 8 final corrected release {rel.RELEASE_ID}\\n\\n"
           f"Numbers: run {rel.NUMBERS_RUN_ID} (archive {rel.ARCHIVE_SESSION}), equivalent to the "
           f"audited run {rel.AUDITED_RUN_ID}; scientific code {rel.SCIENTIFIC_PIN}.\\n"
           f"F3.4 figures: F8 re-render {RENDER_ID} (presentation only, approved {rel.F8_APPROVED}).\\n"
           f"Publication: {PUBLICATION_ID}. Canonical numbers: {rel.OUTPUT_PREFIX}/ in this commit.\\n"
           f"Release record: {rel.RECORD_PREFIX}/. No estimation.\\n")
COMMIT = rel.stage_git(REPO, STAGE_DIR, TREE, RECORD, MESSAGE)
GIT_CHECK = rel.verify_git_commit(REPO, COMMIT, TREE, RECORD)
PAYLOAD = WORK_DIR / "drive_payload"
PAYLOAD_CHECK = rel.build_drive_payload(TREE, RECORD, PAYLOAD)
print("staged commit", COMMIT, json.dumps(GIT_CHECK))
print("Drive payload:", json.dumps(PAYLOAD_CHECK["files"]))
print("Everything is staged and verified locally. Nothing has been published.")'''

PUBLISH = '''STATUS_PATH = WORK_DIR / "publication_status.json"
try:
    STATUS = rel.publish(authorized=AUTHORIZE_PUBLICATION, payload_dir=PAYLOAD,
                         drive_root=Path(DRIVE_ROOT), repo=REPO, commit=COMMIT, tree=TREE,
                         record_dir=RECORD, status_path=STATUS_PATH, git_env=GIT_ENV)
finally:
    print(STATUS_PATH.read_text() if STATUS_PATH.exists() else "no status written")
if STATUS["state"] == "published":
    print("PUBLISHED and verified at both destinations. Send this status to Claude.")
else:
    print("Not published (", STATUS["state"], "). Send the output above to Claude.")'''


def cells(tool_commit: str) -> list[tuple[str, str]]:
    return [("markdown", INTRO), ("code", SETTINGS.replace("__TOOL__", tool_commit)),
            ("markdown", "## 1. Drive and credentials"), ("code", SETUP),
            ("markdown", "## 2. Release tool at the pinned commit; destinations free"), ("code", CLONE),
            ("markdown", "## 3. Approved environment and frozen data"), ("code", ENV),
            ("markdown", "## 4. Verify and extract the candidate archive"), ("code", ARCHIVE),
            ("markdown", "## 5. Render F3.4 (F8 off = archive; F8 on = approved), no estimation"),
            ("code", RENDER),
            ("markdown", "## 6a. Assemble and verify the release (25-path allowlist)"), ("code", ASSEMBLE),
            ("markdown", "## 6b. Stage the GitHub commit and the Drive payload locally"), ("code", STAGE),
            ("markdown", "## 7. Publish (only if AUTHORIZE_PUBLICATION is True)"), ("code", PUBLISH)]


def build(tool_commit: str) -> dict:
    out = []
    for kind, source in cells(tool_commit):
        cell = {"cell_type": kind, "metadata": {}, "source": source.splitlines(keepends=True)}
        if kind == "code":
            cell.update(execution_count=None, outputs=[])
        out.append(cell)
    return {"cells": out, "metadata": {"colab": {"provenance": []},
                                       "kernelspec": {"display_name": "Python 3", "name": "python3"},
                                       "language_info": {"name": "python"}},
            "nbformat": 4, "nbformat_minor": 0}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1 or len(argv[0]) != 40:
        print(__doc__)
        return 2
    (HERE / NOTEBOOK).write_text(json.dumps(build(argv[0]), indent=1) + "\n", encoding="utf-8")
    print("wrote", HERE / NOTEBOOK)
    return 0


if __name__ == "__main__":
    sys.exit(main())
