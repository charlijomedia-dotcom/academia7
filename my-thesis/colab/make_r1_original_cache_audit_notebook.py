#!/usr/bin/env python3
"""Generate colab/r1_original_cache_audit.ipynb: the read-only original-cache audit (B3).

The notebook estimates nothing and pushes nothing. It checks out the orchestration commit
and the pinned scientific code (both verified), builds the approved environment, verifies
the frozen data and the cache identity, restores the COMPLETE original fit cache from
Drive (read only; 18,964 payloads asserted), runs `r1_original_cache_audit.py` (verify,
audit, candidate, impact) with every estimator refused, and copies the machine-readable
results to a new Drive folder, `baseline/r1_original_cache_audit/<session>/`, the only
place it writes on Drive.

    python make_r1_original_cache_audit_notebook.py [ORCH_COMMIT]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_r1_tier_b_notebooks as tbn  # noqa: E402
import r1_tierb as tb  # noqa: E402

NOTEBOOK = "r1_original_cache_audit.ipynb"
ORCH_DEFAULT_LINE = 'ORCH_COMMIT = "__ORCH__"'

INTRO = f"""# R1 original-cache audit and baseline-impact assessment (read-only, Option B3)

**Authorised scope:** a complete, read-only audit of the original fit cache and an
isolated, non-publishing impact assessment. **No model is estimated**: every estimator is
refused for the whole run (an estimator call raises). Nothing is pushed. The published
results, Tier A, the Tier B checkpoints and certificates, the pins and the approved
specifications are only read.

What it does, in order:
1. verifies both checkouts, the approved environment, the frozen data and the cache
   identity `{tb.CACHE_IDENTITY}`;
2. restores the **complete** original fit cache from Drive (read only) and asserts
   {tb.ORIGINAL_PAYLOADS:,} payloads; records the sha256 of every archive part;
3. `verify`: every payload name and size against the committed inventory;
4. `audit`: every MSAR, STAR and ARMA chain under the cache-hit and the live warm-start
   rules, against the published fit records and forecasts;
5. `candidate`: `forecasting:UNRATE|MSAR` replayed from the cache by the live rule,
   estimation refused; if anything is missing it stops and lists it;
6. `impact`: the pinned R1 workflow in legacy mode on the published outputs and on an
   isolated copy carrying only the candidate chain; every differing output and cell;
7. copies the results to `baseline/r1_original_cache_audit/<session>/` on Drive.

Runtime: about 1–2 hours on a standard CPU runtime (two legacy workflow passes).
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
CANDIDATE_TASK = "forecasting:UNRATE|MSAR"  # @param {{type:"string"}}
# Give the legacy workflow the original cache, as the Tier A replay did (complete tables).
IMPACT_WITH_CACHE = True  # @param {{type:"boolean"}}
RUN_AUDIT = True  # @param {{type:"boolean"}}
USE_CONSTRAINTS = True  # @param {{type:"boolean"}}
WORK = "/content/r1_cache_audit"'''


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

DRIVE_ROOT = str(DRIVE_ROOT).strip().strip('"').strip("'").strip().rstrip("/")
assert DRIVE_ROOT.startswith("/content/drive/"), f"DRIVE_ROOT must be under /content/drive/: {DRIVE_ROOT!r}"
ORCH_COMMIT, PIN_COMMIT = str(ORCH_COMMIT).strip().lower(), str(PIN_COMMIT).strip().lower()
for _name, _sha in (("ORCH_COMMIT", ORCH_COMMIT), ("PIN_COMMIT", PIN_COMMIT)):
    assert re.fullmatch(r"[0-9a-f]{40}", _sha), f"{_name} must be a full 40-character SHA"
SESSION = f"audit-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{secrets.token_hex(3)}"
WORK_DIR = Path(WORK)
WORK_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_DRIVE = Path(DRIVE_ROOT) / "baseline" / "r1_original_cache_audit" / SESSION  # the ONLY Drive write
print("session:", SESSION, "| GitHub token:", "found" if GITHUB_TOKEN else "not set")'''

CLONE = (tbn.CLONE
         .replace('TASKS = list(tb.batch_tasks(BATCH_ID))\n', '')
         .replace('print(json.dumps(tb.validate_partition(), indent=1))\n', '')
         .replace('print("this batch:", TASKS)\n', ''))

RESTORE = '''# The complete ORIGINAL fit cache, read only, onto local disk (nothing is written on Drive).
DRIVE = Path(DRIVE_ROOT) / "baseline"
ORIGINAL_CACHE = WORK_DIR / "original_cache"
FOLDERS = list(tc.archive_folders(DRIVE, IDENTITY))
if not (ORIGINAL_CACHE / "fits").exists():
    for folder in FOLDERS:
        tc.IncrementalArchive(ORIGINAL_CACHE / "fits", folder).restore(folder=folder)
PAYLOADS = sum(1 for _ in (ORIGINAL_CACHE / "fits").glob("*/*.json"))
assert PAYLOADS == EXPECTED_ORIGINAL_PAYLOADS, f"{PAYLOADS} original payloads, expected {EXPECTED_ORIGINAL_PAYLOADS}"
PARTS = []
for folder in FOLDERS:
    for part in sorted(folder.glob("part-*.tar.gz")):
        PARTS.append({"folder": str(folder), "part": part.name, "bytes": part.stat().st_size,
                      "sha256": tc.sha256(part)})
(WORK_DIR / "audit_out").mkdir(exist_ok=True)
(WORK_DIR / "audit_out" / "original_cache_parts.json").write_text(json.dumps(PARTS, indent=1))
print(f"{PAYLOADS} payloads restored from {len(FOLDERS)} archive folder(s), {len(PARTS)} parts")'''

# The R1 chain sources (which chains R1 served from the cache) live only on the evidence
# branch, not on the orchestration branch: fetched read-only and verified by sha256.
CHAIN_SOURCES_BRANCH = "part8-r1-replay/20261103T063749Z"
CHAIN_SOURCES_COMMIT = tb.TIER_A_EVIDENCE_COMMIT
CHAIN_SOURCES_PATH = ("my-thesis/reports/part8/corrections/r1/replay_20261103T063749Z/"
                      "corrected_r1_summary.json")
CHAIN_SOURCES_SHA256 = "f3b7c1fb53b153cc89cdc657b548749a9760d4f7e5d5ee2fd64d4c723a8e2ff3"

RUN = f'''# Read-only and non-estimating: every estimator is refused inside the audit script.
OUT = WORK_DIR / "audit_out"
# R1 chain sources: only on the evidence branch, so fetched from its commit and verified.
CHAIN_SOURCES = WORK_DIR / "corrected_r1_summary.json"
if not CHAIN_SOURCES.exists():
    subprocess.run(["git", "fetch", "origin", "{CHAIN_SOURCES_BRANCH}"], cwd=REPO, check=True, env=GIT_ENV)
    blob = subprocess.run(["git", "show", "{CHAIN_SOURCES_COMMIT}:{CHAIN_SOURCES_PATH}"],
                          cwd=REPO, check=True, capture_output=True).stdout
    CHAIN_SOURCES.write_bytes(blob)
assert tc.sha256(CHAIN_SOURCES) == "{CHAIN_SOURCES_SHA256}", "R1 chain sources do not match the evidence commit"
INVENTORY = REPO / "my-thesis" / "reports" / "part8" / "corrections" / "r1" / "evidence" / "original_cache_audit_20261105" / "original_fit_cache_inventory.csv.gz"
assert INVENTORY.is_file(), f"missing {{INVENTORY}}"
if not RUN_AUDIT:
    print("RUN_AUDIT is False")
else:
    command = [str(PY), "-u", str(ORCH / "r1_original_cache_audit.py"),
               "--cache-fits", str(ORIGINAL_CACHE / "fits"), "--code-dir", str(CODE),
               "--original", str(ORIGINAL),
               "--inventory", str(INVENTORY), "--chain-sources", str(CHAIN_SOURCES),
               "--candidate-task", CANDIDATE_TASK, "--out", str(OUT), "--stage", "all"]
    if IMPACT_WITH_CACHE:
        command.append("--impact-with-cache")
    started = time.time()
    audit = subprocess.run(command, cwd=str(CODE), env=RUN_ENV, capture_output=True, text=True)
    (OUT / "audit_console.log").write_text(audit.stdout + "\\n--- stderr ---\\n" + audit.stderr)
    print(audit.stdout[-6000:], audit.stderr[-3000:])
    print(f"audit exit {{audit.returncode}} after {{(time.time() - started) / 60:.1f}} min")
    assert audit.returncode == 0, "the audit failed; see audit_console.log"'''

EXPORT = '''# Copy the machine-readable results (not the full regenerated output trees) to Drive.
# Files over 5 MB are also written gzip-compressed (the Drive connector cannot fetch them).
import gzip
KEEP = ("verify/", "audit/", "candidate/", "impact/impact.json", "impact/reference_vs_published.csv",
        "impact/candidate_vs_reference.csv", "impact/changed_cells.csv", "report-", "original_cache_parts",
        "audit_console")
assert str(AUDIT_DRIVE).startswith(str(Path(DRIVE_ROOT) / "baseline" / "r1_original_cache_audit") + "/")
assert not AUDIT_DRIVE.exists(), f"{AUDIT_DRIVE} exists already"
exported = []
for path in sorted(OUT.rglob("*")):
    relative = path.relative_to(OUT).as_posix()
    if path.is_file() and relative.startswith(KEEP):
        target = AUDIT_DRIVE / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        assert tc.sha256(target) == tc.sha256(path)
        exported.append({"path": relative, "bytes": path.stat().st_size, "sha256": tc.sha256(path)})
        if path.stat().st_size > 5_000_000:      # retrievable through the Drive connector
            packed = target.with_name(target.name + ".gz")
            with open(path, "rb") as raw, gzip.GzipFile(packed, "wb", 9, mtime=0) as gz:
                shutil.copyfileobj(raw, gz)
            exported.append({"path": relative + ".gz", "bytes": packed.stat().st_size,
                             "sha256": tc.sha256(packed), "gzip_of": relative})
# the changed files of both legacy passes, for inspection (tables only)
impact = OUT / "impact" / "impact.json"
if impact.exists() and json.loads(impact.read_text()).get("performed"):
    for relative in json.loads(impact.read_text())["files_changed_by_candidate"]:
        if relative.endswith(".csv"):
            for side in ("reference", "candidate"):
                source = OUT / "impact" / side / relative
                target = AUDIT_DRIVE / "impact" / f"{side}_tables" / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
                exported.append({"path": f"impact/{side}_tables/{relative}",
                                 "bytes": source.stat().st_size, "sha256": tc.sha256(source)})
                if source.stat().st_size > 5_000_000:
                    packed = target.with_name(target.name + ".gz")
                    with open(source, "rb") as raw, gzip.GzipFile(packed, "wb", 9, mtime=0) as gz:
                        shutil.copyfileobj(raw, gz)
                    exported.append({"path": f"impact/{side}_tables/{relative}.gz",
                                     "bytes": packed.stat().st_size, "sha256": tc.sha256(packed),
                                     "gzip_of": f"impact/{side}_tables/{relative}"})
manifest = {"session": SESSION, "orchestration_commit": ORCH_COMMIT, "scientific_commit": PIN_COMMIT,
            "cache_identity": IDENTITY, "original_payloads": PAYLOADS, "frozen_data_sha256": FROZEN_SHA,
            "python": FOUND["python"], "estimation": "none (refused)", "files": exported}
(AUDIT_DRIVE / "export_manifest.json").write_text(json.dumps(manifest, indent=1))
print(f"{len(exported)} files exported to {AUDIT_DRIVE}")
print("Please send this folder name to Claude:", SESSION)'''


def cells() -> list[tuple[str, str]]:
    return [("markdown", INTRO), ("code", settings()),
            ("markdown", "## 1. Drive and settings"), ("code", SETUP),
            ("markdown", "## 2. Orchestration and pinned scientific code, both verified"),
            ("code", CLONE),
            ("markdown", "## 3. Approved environment, frozen data, cache identity"),
            ("code", tbn.ENV),
            ("markdown", "## 4. The complete original fit cache (read only)"), ("code", RESTORE),
            ("markdown", "## 5. Audit, candidate and impact (no estimation)"), ("code", RUN),
            ("markdown", "## 6. Export the results to Drive"), ("code", EXPORT)]


def build(orch: str) -> dict:
    out = []
    for kind, source in cells():
        if kind == "code":
            source = source.replace(f'{ORCH_DEFAULT_LINE}', f'ORCH_COMMIT = "{orch}"', 1)
        lines = source.splitlines(keepends=True)
        cell = {"cell_type": kind, "metadata": {}, "source": lines}
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
