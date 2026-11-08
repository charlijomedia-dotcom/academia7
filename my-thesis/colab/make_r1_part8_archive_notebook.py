#!/usr/bin/env python3
"""Generate the non-publishing archive workflow for the audited Part 8 integration candidate.

    python make_r1_part8_archive_notebook.py <ARCHIVE_TOOL_COMMIT>

Writes two artefacts (neither is run here):

1. r1_part8_preserve_cell.py - a single cell to paste into the ORIGINAL integration notebook,
   in the runtime of session integration-20261108T052245Z-9bba8e, if that runtime is still
   connected. It checks whether the exact 465-file release tree still exists; if it does, it
   verifies every file against the audited inventory (sha256) and archives it. If the tree is
   gone, it says so and stops; nothing is written.

2. r1_part8_candidate_archive.ipynb - a new notebook for when the tree is gone: it re-runs the
   unchanged dry run (orchestration a2c3171, pin 8aaa4217; estimation refused) only if
   ALLOW_RECONSTRUCTION is set, applies the strict equivalence gate against the audited
   session's Drive export, and archives only if the gate passes.

Both write exclusively to a NEW Drive folder baseline/r1_part8_candidate_archive/<archive session>/.
Nothing is published, pushed or overwritten. The archive tool is fetched from ARCHIVE_TOOL_COMMIT
with `git show` (the checkouts stay at their commits) and must match the sha256 pinned here.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_r1_original_cache_audit_notebook as audit_nb  # noqa: E402
import make_r1_part8_integration_notebook as integ  # noqa: E402
import make_r1_tier_b_notebooks as tbn  # noqa: E402
import r1_integration_archive as arc  # noqa: E402
import r1_tierb as tb  # noqa: E402

NOTEBOOK = "r1_part8_candidate_archive.ipynb"
PRESERVE_CELL_FILE = "r1_part8_preserve_cell.py"
TOOL = "my-thesis/colab/r1_integration_archive.py"
TOOL_SHA256 = hashlib.sha256((HERE / "r1_integration_archive.py").read_bytes()).hexdigest()
AUDITED_EXPORT_RELATIVE = f"{integ.EXPORT_PARENT}/{arc.AUDITED_SESSION}"

FETCH_TOOL = '''# The archive tool, fetched read-only from ARCHIVE_TOOL_COMMIT and checked against its pinned sha256.
TOOL_DIR = Path(WORK) / "archive_tool" / ARCHIVE_TOOL_COMMIT[:12]
TOOL_DIR.mkdir(parents=True, exist_ok=True)
_tool_repo = Path(WORK) / "archive_tool" / "repo"
_env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
if "GIT_ENV" in globals():
    _env = dict(GIT_ENV)
if not (_tool_repo / ".git").exists():
    subprocess.run(["git", "clone", "--no-checkout", "--filter=blob:none",
                    f"https://github.com/{REPOSITORY}.git", str(_tool_repo)], check=True, env=_env)
subprocess.run(["git", "fetch", "origin", BRANCH], cwd=_tool_repo, check=True, env=_env)
_src = subprocess.run(["git", "show", f"{ARCHIVE_TOOL_COMMIT}:''' + TOOL + '''"], cwd=_tool_repo,
                      check=True, capture_output=True, env=_env).stdout
assert hashlib.sha256(_src).hexdigest() == ARCHIVE_TOOL_SHA256, "archive tool does not match its pinned sha256"
(TOOL_DIR / "r1_integration_archive.py").write_bytes(_src)
sys.path.insert(0, str(TOOL_DIR))
import r1_integration_archive as arc
importlib.reload(arc)
AUDITED_EXPORT = Path(DRIVE_ROOT) / "''' + AUDITED_EXPORT_RELATIVE + '''"
arc.verify_audited_export(AUDITED_EXPORT)
print("archive tool", ARCHIVE_TOOL_COMMIT[:12], "verified; audited export verified:", AUDITED_EXPORT)'''

ARCHIVE = '''# Write the archive to a NEW Drive folder (refuses if it exists), then re-read and verify it.
ARCHIVE_SESSION = f"archive-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{secrets.token_hex(3)}"
IDENTITY = arc.run_identity(mode=GATE["mode"], archive_session=ARCHIVE_SESSION,
                            archive_tool_commit=ARCHIVE_TOOL_COMMIT,
                            orchestration_commit=SOURCE_ORCHESTRATION, scientific_commit=arc.SCIENTIFIC_PIN,
                            run_id=SOURCE_RUN_ID, source_session=SOURCE_SESSION)
if not WRITE_ARCHIVE:
    print("WRITE_ARCHIVE is False; gate report:", json.dumps(GATE)[:2000])
else:
    MANIFEST = arc.write_archive(RELEASE_DIR, DRIVE_ROOT, ARCHIVE_SESSION, IDENTITY, GATE)
    DEST = Path(DRIVE_ROOT) / arc.ARCHIVE_PARENT / ARCHIVE_SESSION
    print(json.dumps(arc.verify_archive(DEST)))
    print(f"archived {MANIFEST['files']} files to {DEST}; release.tar.gz sha256 {MANIFEST['release_tar_sha256']}")
    print("Nothing was published. Please send this folder name to Claude:", ARCHIVE_SESSION)'''


def settings() -> str:
    return f'''# @title Settings
REPOSITORY = "charlijomedia-dotcom/academia7"  # @param {{type:"string"}}
BRANCH = "part8-r1-rescore"  # @param {{type:"string"}}
ARCHIVE_TOOL_COMMIT = "__TOOL__"  # @param {{type:"string"}}
ARCHIVE_TOOL_SHA256 = "{TOOL_SHA256}"
ORCH_COMMIT = "{arc.AUDITED_ORCHESTRATION}"  # the audited orchestration; do not change
PIN_COMMIT = "{tb.SCIENTIFIC_PIN}"  # the scientific pin; do not change
DRIVE_ROOT = "/content/drive/MyDrive/KillyPhD/Part8_K3_InSample_2026-10-29"  # @param {{type:"string"}}
EXPECTED_IDENTITY = "{tb.CACHE_IDENTITY}"
EXPECTED_ORIGINAL_PAYLOADS = {tb.ORIGINAL_PAYLOADS}
ALLOW_RECONSTRUCTION = False  # @param {{type:"boolean"}}
WRITE_ARCHIVE = True  # @param {{type:"boolean"}}
USE_CONSTRAINTS = True
RUN_DRY_RUN = False           # set by the mode cell; True only for an authorised reconstruction
EXPORT_TO_DRIVE = False       # the dry run's report export is not used here
CONFIRM_PUBLISH = False       # there is no publication in this notebook; must stay False
WORK = "/content/r1_part8_integration"'''


INTRO = f"""# Part 8 integration candidate: non-publishing archive

Preserves the **exact** release tree of the audited integration dry run
`{arc.AUDITED_SESSION}` (run `{arc.AUDITED_RUN_ID}`; orchestration `{arc.AUDITED_ORCHESTRATION[:7]}`;
pin `{tb.SCIENTIFIC_PIN[:7]}`), or, if it is gone, reconstructs it and archives it **only if** a
strict scientific-equivalence gate passes against that audited session.

- **Preferred:** if the original runtime of that session is still connected, paste
  `colab/r1_part8_preserve_cell.py` into the ORIGINAL notebook and run it there instead.
- **This notebook** handles the case where the tree is gone. The reconstruction re-runs the
  unchanged, non-estimating dry run, so it requires `ALLOW_RECONSTRUCTION = True` (your decision).
- **Gate:** every exported machine report identical (CSVs byte for byte; JSON reports after
  removing only run_id/session/timestamps; gzip after decompression); acceptance A1–A15 passing,
  nothing unexplained, exit 4; the 465-file inventory identical except explicitly identified
  provenance carriers (figure sidecars, run records, regenerated tables' provenance columns);
  every figure and original file byte-identical. Anything else refuses the archive.
- **Writes only** `{arc.ARCHIVE_PARENT}/<archive session>/` on Drive: `release.tar.gz`,
  `archive_inventory.csv`, `acceptance_report.json`, `archive_manifest.json`.
- No estimation, no publication, no push, no change to results, caches, certificates or releases.
"""

MODE = '''# Which mode: the audited tree on this runtime (preserve), or a reconstruction.
ORIGINAL_RELEASE = Path(WORK) / "dryrun" / arc.AUDITED_SESSION / "release"
if ORIGINAL_RELEASE.is_dir():
    MODE_RESOLVED = "preserve"
else:
    MODE_RESOLVED = "reconstruct"
    assert ALLOW_RECONSTRUCTION, ("the audited release tree is not on this runtime; a reconstruction "
                                  "re-runs the non-estimating dry run and needs ALLOW_RECONSTRUCTION = True")
    RUN_DRY_RUN = True
print("mode:", MODE_RESOLVED)'''

PRESERVE = '''# PRESERVE: exact verification of the audited tree (465 files) against the audited inventory.
if MODE_RESOLVED == "preserve":
    GATE = arc.preserve_check(ORIGINAL_RELEASE, AUDITED_EXPORT)
    RELEASE_DIR, SOURCE_SESSION, SOURCE_RUN_ID = ORIGINAL_RELEASE, arc.AUDITED_SESSION, arc.AUDITED_RUN_ID
    SOURCE_ORCHESTRATION = arc.AUDITED_ORCHESTRATION
    print("preserve check passed:", GATE["files"], "files, all identical to the audited inventory")'''

GATE = '''# RECONSTRUCT: the strict equivalence gate against the audited session (refuses on any other difference).
if MODE_RESOLVED == "reconstruct":
    assert DRY_EXIT is not None, "the reconstruction did not run"
    _acc = json.loads((DRYRUN / "dryrun_report" / "acceptance.json").read_text())
    GATE = arc.equivalence_gate(DRYRUN, AUDITED_EXPORT, exit_code=DRY_EXIT, new_session=SESSION,
                                new_run_id=_acc["run_id"], published_dir=ORIGINAL)
    RELEASE_DIR, SOURCE_SESSION, SOURCE_RUN_ID = DRYRUN / "release", SESSION, _acc["run_id"]
    SOURCE_ORCHESTRATION = ORCH_COMMIT
    print(json.dumps(GATE["checks"]), "| provenance-only files:", len(GATE["inventory"]["provenance_only"]))'''


def _only_if_reconstruct(source: str) -> str:
    return ('if MODE_RESOLVED == "reconstruct":\n'
            f'    exec(compile({source!r}, "<reconstruction>", "exec"), globals())\n'
            'else:\n    print("preserve mode: not needed")')


def cells(tool_commit: str) -> list[tuple[str, str]]:
    return [("markdown", INTRO), ("code", settings().replace("__TOOL__", tool_commit)),
            ("markdown", "## 1. Drive"), ("code", integ.SETUP),
            ("markdown", "## 2. The archive tool and the audited export (both verified)"),
            ("code", FETCH_TOOL),
            ("markdown", "## 3. Mode"), ("code", MODE),
            ("markdown", "## 4a. Preserve (exact files)"), ("code", PRESERVE),
            ("markdown", "## 4b. Reconstruct: checkouts at the audited commits"),
            ("code", _only_if_reconstruct(integ.CLONE)),
            ("markdown", "## 4c. Reconstruct: approved environment, frozen data, cache identity"),
            ("code", _only_if_reconstruct(tbn.ENV)),
            ("markdown", "## 4d. Reconstruct: the original fit cache (read only)"),
            ("code", _only_if_reconstruct(integ.RESTORE)),
            ("markdown", "## 4e. Reconstruct: the unchanged dry run (no estimation, no publication)"),
            ("code", "DRY_EXIT = None\n" + _only_if_reconstruct(integ.RUN)),
            ("markdown", "## 4f. Reconstruct: the equivalence gate"), ("code", GATE),
            ("markdown", "## 5. Archive to a new Drive folder"), ("code", ARCHIVE)]


def preserve_cell(tool_commit: str) -> str:
    return f'''# Part 8 candidate: PRESERVE cell. Paste into the ORIGINAL integration notebook and run it in the
# runtime of session {arc.AUDITED_SESSION}. Read-only on the release tree; writes only a NEW folder
# {arc.ARCHIVE_PARENT}/<archive session>/ on Drive. No estimation, no publication.
import os, sys, json, time, secrets, hashlib, importlib, subprocess
from pathlib import Path
ARCHIVE_TOOL_COMMIT = "{tool_commit}"
ARCHIVE_TOOL_SHA256 = "{TOOL_SHA256}"
REPOSITORY = globals().get("REPOSITORY", "charlijomedia-dotcom/academia7")
BRANCH = globals().get("BRANCH", "part8-r1-rescore")
WORK = globals().get("WORK", "/content/r1_part8_integration")
DRIVE_ROOT = globals().get("DRIVE_ROOT", "/content/drive/MyDrive/KillyPhD/Part8_K3_InSample_2026-10-29")
WRITE_ARCHIVE = True
ORIGINAL_RELEASE = Path(WORK) / "dryrun" / "{arc.AUDITED_SESSION}" / "release"
if not ORIGINAL_RELEASE.is_dir():
    print("NOT FOUND:", ORIGINAL_RELEASE, "- the audited tree is gone; use r1_part8_candidate_archive.ipynb.")
else:
    if not Path("/content/drive/MyDrive").exists():
        from google.colab import drive
        drive.mount("/content/drive")
{_indent(FETCH_TOOL)}
    MODE_RESOLVED = "preserve"
{_indent(PRESERVE)}
{_indent(ARCHIVE)}
'''


def _indent(source: str) -> str:
    return "\n".join(("    " + line) if line else line for line in source.splitlines())


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
    commit = argv[0] if argv else "__TOOL__"
    (HERE / NOTEBOOK).write_text(json.dumps(build(commit), indent=1) + "\n", encoding="utf-8")
    (HERE / PRESERVE_CELL_FILE).write_text(preserve_cell(commit), encoding="utf-8")
    print("wrote", HERE / NOTEBOOK, "and", HERE / PRESERVE_CELL_FILE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
