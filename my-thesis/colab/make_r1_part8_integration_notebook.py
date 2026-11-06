#!/usr/bin/env python3
"""Generate colab/r1_part8_integration_dryrun.ipynb: the NON-PUBLISHING integration dry run.

    python make_r1_part8_integration_notebook.py <ORCH_COMMIT>

The notebook estimates nothing and publishes nothing. It checks out the orchestration
commit and, separately, the pinned scientific commit (both verified clean), builds the
approved environment, verifies the frozen data and the cache identity, restores the
complete original fit cache from Drive (read only), runs `r1_part8_integration.py`
(stages 0-5: preflight, base tree, aggregation, dependent outputs, validation A1-A15,
claims and jury reassessment), and copies the machine-readable reports to a NEW Drive
folder, `baseline/r1_part8_integration_dryrun/<session>/`, the only place it writes on Drive.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_r1_original_cache_audit_notebook as audit_nb  # noqa: E402
import make_r1_tier_b_notebooks as tbn  # noqa: E402
import r1_tierb as tb  # noqa: E402

NOTEBOOK = "r1_part8_integration_dryrun.ipynb"
ORCH_DEFAULT_LINE = 'ORCH_COMMIT = "__ORCH__"'
EXPORT_PARENT = "baseline/r1_part8_integration_dryrun"
RELEASE_BRANCHES = ("part8-corrected-results/r1-tier-a-20261103T063749Z",
                    "part8-corrected-results/r1-20261101")

INTRO = f"""# Part 8 final integration — NON-PUBLISHING dry run

**Authorised scope (6 November 2026):** a dry run of the final Part 8 integration. **No model is
estimated** (every estimator is refused; fit calls are counted). **Nothing is published:** there
is no publication code, nothing is committed or pushed, and the run refuses if `CONFIRM_PUBLISH`
is set. No final release; no Part 9.

**Decisions applied**
- **B1 staged baseline correction** (UNRATE MSAR, run `b1-staged-20261106T154902Z`): approved as
  the selected implementation correction; used as the base tree.
- **D1** — both B2 MSAR chains integrated as *candidates* under the approved live warm-start rule.
  Their 20 classification changes and 29 optimiser sensitivities **stay review items**. Not
  scientific approval.
- **D2** — every F4.8 figure whose corrected table changes is re-rendered and validated against
  the integrated table.
- **D3** — deferred: no publication destination.
- **F8** (F3.4 main-panel presentation) was never confirmed: it is **switched off**. Only the
  authorised corrections F1, F2, F3, F4 and F7.1 apply.

**What it does** (`colab/r1_part8_integration.py`, stages 0–5):
0. preflight — both checkouts at their commits and clean, frozen data, configuration and cache
   identity, rendering (matplotlib defaults), the three certificates against the reviewed
   sha256 manifest, original-cache payload digest, Tier A archive, reference releases; a hash
   listing of every protected input;
1. base tree — published output + the B1-staged overlay, all 461 files verified;
2. aggregation — Tier A + certified Tier B payloads merged; the pinned R1 workflow (legacy, then
   corrected), estimation refused; chain-aware reconciliation; the aggregator's gates;
3. dependent outputs the workflow does not rebuild — fit records, T4.7 registry and counts,
   all_test_results Wald rows, T4.6 summary, F4.8, inventory;
4. validation — acceptance criteria A1–A15; every changed scientific cell attributed to a
   cause; **any unexplained difference stops the run (REFUSED)**;
5. claims and jury-resolution reassessment (nothing is edited).

**Writes:** only under `WORK` on the Colab disk and, in the last cell, a new Drive folder
`{EXPORT_PARENT}/<session>/` holding the machine-readable reports (not the release tree).

**Expected outcome:** `DRY_RUN_STATUS: ACCEPTED_FOR_REVIEW_REVIEW_REQUIRED` (exit 4), because B2's
review items remain open. `REFUSED` (exit 1) lists every failed criterion. Runtime: about
1–2 hours on a standard CPU runtime.
"""


def settings() -> str:
    return f'''# @title Settings
REPOSITORY = "charlijomedia-dotcom/academia7"  # @param {{type:"string"}}
BRANCH = "part8-r1-rescore"  # @param {{type:"string"}}
{ORCH_DEFAULT_LINE}  # @param {{type:"string"}}
PIN_COMMIT = "{tb.SCIENTIFIC_PIN}"  # @param {{type:"string"}}
DRIVE_ROOT = "/content/drive/MyDrive/KillyPhD/Part8_K3_InSample_2026-10-29"  # @param {{type:"string"}}
EXPECTED_IDENTITY = "{tb.CACHE_IDENTITY}"  # @param {{type:"string"}}
EXPECTED_ORIGINAL_PAYLOADS = {tb.ORIGINAL_PAYLOADS}  # @param {{type:"integer"}}
RUN_DRY_RUN = True  # @param {{type:"boolean"}}
EXPORT_TO_DRIVE = True  # @param {{type:"boolean"}}
USE_CONSTRAINTS = True  # @param {{type:"boolean"}}
CONFIRM_PUBLISH = False  # there is no publication in this notebook; must stay False
WORK = "/content/r1_part8_integration"'''


SETUP = '''import os, re, sys, json, time, shutil, secrets, subprocess, importlib.util, hashlib
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

assert CONFIRM_PUBLISH is False, "this notebook never publishes; CONFIRM_PUBLISH must be False"
DRIVE_ROOT = str(DRIVE_ROOT).strip().strip('"').strip("'").strip().rstrip("/")
assert DRIVE_ROOT.startswith("/content/drive/"), f"DRIVE_ROOT must be under /content/drive/: {DRIVE_ROOT!r}"
ORCH_COMMIT, PIN_COMMIT = str(ORCH_COMMIT).strip().lower(), str(PIN_COMMIT).strip().lower()
for _name, _sha in (("ORCH_COMMIT", ORCH_COMMIT), ("PIN_COMMIT", PIN_COMMIT)):
    assert re.fullmatch(r"[0-9a-f]{40}", _sha), f"{_name} must be a full 40-character SHA"
SESSION = f"integration-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{secrets.token_hex(3)}"
WORK_DIR = Path(WORK)
WORK_DIR.mkdir(parents=True, exist_ok=True)
DRYRUN = WORK_DIR / "dryrun" / SESSION     # the driver's work folder (new for every session)
EXPORT = Path(DRIVE_ROOT) / "''' + EXPORT_PARENT + '''" / SESSION   # the ONLY Drive write
os.environ.pop("CONFIRM_PUBLISH", None)
print("session:", SESSION, "| GitHub token:", "found" if GITHUB_TOKEN else "not set")'''

CLONE = audit_nb.CLONE + '''
# Reference releases (read only, as git objects): Tier A (292227e) and the R1 release the claim
# matrix was written against (0573a8c).
for _branch in ''' + repr(RELEASE_BRANCHES) + ''':
    subprocess.run(["git", "fetch", "origin", _branch], cwd=REPO, check=True, env=GIT_ENV)
for _commit in ("''' + tb.TIER_A_RELEASE_COMMIT + '''", "0573a8c"):
    subprocess.run(["git", "cat-file", "-e", _commit + "^{commit}"], cwd=REPO, check=True)
assert _clean(REPO) and _clean(PINNED), "a checkout became dirty"
print("reference releases available")'''

RESTORE = '''# The complete ORIGINAL fit cache, read only, onto local disk (nothing is written on Drive).
DRIVE = Path(DRIVE_ROOT) / "baseline"
ORIGINAL_CACHE = WORK_DIR / "original_cache"
FOLDERS = list(tc.archive_folders(DRIVE, IDENTITY))
if not (ORIGINAL_CACHE / "fits").exists():
    for folder in FOLDERS:
        tc.IncrementalArchive(ORIGINAL_CACHE / "fits", folder).restore(folder=folder)
PAYLOADS = sum(1 for _ in (ORIGINAL_CACHE / "fits").glob("*/*.json"))
assert PAYLOADS == EXPECTED_ORIGINAL_PAYLOADS, f"{PAYLOADS} original payloads, expected {EXPECTED_ORIGINAL_PAYLOADS}"
TIER_A_ARCHIVE = Path(DRIVE_ROOT) / tb.TIER_A_ARCHIVE_RELATIVE
assert TIER_A_ARCHIVE.is_file(), f"missing {TIER_A_ARCHIVE}"
print(f"{PAYLOADS} original payloads restored from {len(FOLDERS)} archive folder(s); Tier A archive found")'''

RUN = '''# Non-estimating and non-publishing. Exit 0 = accepted; 4 = accepted, REVIEW REQUIRED; 1 = REFUSED.
if not RUN_DRY_RUN:
    print("RUN_DRY_RUN is False")
else:
    assert not DRYRUN.exists(), f"{DRYRUN} exists"
    command = [str(PY), "-u", str(ORCH / "r1_part8_integration.py"), "--repo", str(REPO),
               "--code-dir", str(CODE), "--drive-root", DRIVE_ROOT,
               "--cache-root", str(ORIGINAL_CACHE), "--tier-a-archive", str(TIER_A_ARCHIVE),
               "--orch-commit", ORCH_COMMIT, "--work", str(DRYRUN)]
    for _i, _folder in enumerate(FOLDERS):     # the original-cache archives on Drive stay unchanged
        command += ["--protect", f"original_cache_archive_{_i}={_folder}"]
    RUN_ENV_DRY = dict(RUN_ENV)
    RUN_ENV_DRY.pop("CONFIRM_PUBLISH", None)
    started = time.time()
    dry = subprocess.run(command, cwd=str(CODE), env=RUN_ENV_DRY, capture_output=True, text=True)
    (DRYRUN / "dryrun_report").mkdir(parents=True, exist_ok=True)
    (DRYRUN / "dryrun_report" / "console.log").write_text(dry.stdout + "\\n--- stderr ---\\n" + dry.stderr)
    print(dry.stdout[-8000:])
    print(dry.stderr[-3000:])
    DRY_EXIT = dry.returncode
    print(f"dry run exit {DRY_EXIT} after {(time.time() - started) / 60:.1f} min")
    status = [l for l in dry.stdout.splitlines() if l.startswith("DRY_RUN_STATUS: ")]
    print(status[-1] if status else "DRY_RUN_STATUS: unknown (see console.log)")
    print("A completed or accepted dry run is NOT a scientifically approved result; nothing was published.")'''

EXPORT_CELL = '''# Machine-readable reports only (not the release tree), to a NEW Drive folder.
# Files over 5 MB are also written gzip-compressed (the Drive connector cannot fetch them).
import gzip
if not EXPORT_TO_DRIVE:
    print("EXPORT_TO_DRIVE is False")
else:
    parent = Path(DRIVE_ROOT) / "''' + EXPORT_PARENT + '''"
    assert str(EXPORT).startswith(str(parent) + "/") and not EXPORT.exists(), f"{EXPORT} exists or is outside {parent}"
    exported = []
    sources = [(DRYRUN / "dryrun_report", ""), (DRYRUN / "stages", "stages/"),
               (DRYRUN / "base_manifest.csv", "base_manifest.csv"),
               (DRYRUN / "assembly" / "reconcile_cell_causes.csv.gz", "assembly/reconcile_cell_causes.csv.gz"),
               (DRYRUN / "assembly" / "legacy" / "r1_comparison.csv", "assembly/legacy_r1_comparison.csv"),
               (DRYRUN / "assembly" / "corrected" / "r1_comparison.csv", "assembly/corrected_r1_comparison.csv"),
               (DRYRUN / "assembly" / "corrected" / "r1_reconciliation.csv", "assembly/r1_reconciliation.csv"),
               (DRYRUN / "assembly" / "corrected" / "r1_summary.json", "assembly/corrected_r1_summary.json"),
               (DRYRUN / "assembly" / "legacy" / "r1_summary.json", "assembly/legacy_r1_summary.json"),
               (DRYRUN / "release" / "manifests", "release_manifests/")]
    for source, prefix in sources:
        if not source.exists():
            continue
        files = [source] if source.is_file() else sorted(p for p in source.rglob("*") if p.is_file())
        for path in files:
            relative = prefix if source.is_file() else prefix + path.relative_to(source).as_posix()
            target = EXPORT / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            assert tc.sha256(target) == tc.sha256(path)
            exported.append({"path": relative, "bytes": path.stat().st_size, "sha256": tc.sha256(path)})
            if path.stat().st_size > 5_000_000 and not relative.endswith(".gz"):
                packed = target.with_name(target.name + ".gz")
                with open(path, "rb") as raw, gzip.GzipFile(packed, "wb", 9, mtime=0) as gz:
                    shutil.copyfileobj(raw, gz)
                exported.append({"path": relative + ".gz", "bytes": packed.stat().st_size,
                                 "sha256": tc.sha256(packed), "gzip_of": relative})
    manifest = {"session": SESSION, "orchestration_commit": ORCH_COMMIT, "scientific_commit": PIN_COMMIT,
                "cache_identity": IDENTITY, "original_payloads": PAYLOADS, "frozen_data_sha256": FROZEN_SHA,
                "python": FOUND["python"], "estimation": "none (refused)", "published": False,
                "dry_run_exit": globals().get("DRY_EXIT"), "files": exported}
    (EXPORT / "export_manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"{len(exported)} files exported to {EXPORT}")
    print("Please send this folder name to Claude:", SESSION)'''


def cells() -> list[tuple[str, str]]:
    return [("markdown", INTRO), ("code", settings()),
            ("markdown", "## 1. Drive and settings"), ("code", SETUP),
            ("markdown", "## 2. Orchestration and pinned scientific code, both verified; "
                         "reference releases"), ("code", CLONE),
            ("markdown", "## 3. Approved environment, frozen data, cache identity"),
            ("code", tbn.ENV),
            ("markdown", "## 4. The complete original fit cache (read only)"), ("code", RESTORE),
            ("markdown", "## 5. The dry run: stages 0–5 (no estimation, no publication)"),
            ("code", RUN),
            ("markdown", "## 6. Export the machine-readable reports to a new Drive folder"),
            ("code", EXPORT_CELL)]


def build(orch: str) -> dict:
    out = []
    for kind, source in cells():
        if kind == "code":
            source = source.replace(ORCH_DEFAULT_LINE, f'ORCH_COMMIT = "{orch}"', 1)
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
    orch = argv[0] if argv else "__ORCH__"
    path = HERE / NOTEBOOK
    path.write_text(json.dumps(build(orch), indent=1) + "\n", encoding="utf-8")
    print("wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
