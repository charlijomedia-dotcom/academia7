#!/usr/bin/env python3
"""Builds colab/r1_cache_replay.ipynb (run once after editing the cells below)."""

import json
from pathlib import Path

MD_INTRO = """# R1 correction — real-cache replay (no new estimation)

Approved step 1 of the R1 continuation (user decision, 2 November 2026). Open this
notebook in Colab, choose **Runtime → Change runtime type → CPU, High-RAM**, then
**Runtime → Run all**.

What it does, in order:

1. mounts Drive, clones `part8-r1-rescore` and checks out the **pinned commit** (`PIN_COMMIT`), refusing a dirty tree;
2. builds the approved Python 3.11 environment and verifies the frozen data;
3. restores the original fit cache for identity `3413465b508bb844` from Drive into the VM's local disk, **read only** (no backup daemon runs; nothing is written to the Drive `fit_cache/` folders);
4. writes the per-chain replay report for the 20 pending chains (`code/tools/r1_cache_replay_report.py`);
5. runs the R1 workflow with `--cache-root` and **no `--approve`**: first in legacy mode (the validation gate, which now also covers every chain the cache replays), then in corrected mode with the release assembled from the clean, pinned tree;
6. only if `RUN_TIER_A = True` (off by default): re-estimates the Tier A AR chains that the cache could **not** replay, after validating the AR estimator against the published results;
7. copies every report to a **new** Drive folder `r1_replay/<stamp>/`. Step 8 selects the release to publish **from the files the completed steps wrote**: the Tier A release (`r1_tier_a_release`) when Tier A ran, otherwise the step-6 release. It cross-checks run ID, commit, re-estimated chains and validation, refuses on any mismatch or missing output, and is a **dry run unless `CONFIRM_PUBLISH = True`**. Pushes go to **new** GitHub branches only.

**No estimation can happen in steps 4–5.** The R1 workflow runs under `guard.estimation_forbidden()`: every model-estimation function of the package raises if called outside an approved chain, and the cache replay itself turns a cache miss into "chain unavailable". Each step asserts `estimations_performed == none`.

Nothing under `output/`, the existing provisional release (`part8-corrected-results/r1-20261101`), the original results branch, or the Drive fit-cache folders is modified."""

SETTINGS = '''# @title Settings
REPOSITORY = "charlijomedia-dotcom/academia7"  # @param {type:"string"}
BRANCH = "part8-r1-rescore"  # @param {type:"string"}
# The exact commit the replay must run from (the code reviewed on GitHub).
PIN_COMMIT = "__PIN__"  # @param {type:"string"}
DRIVE_ROOT = "/content/drive/MyDrive/KillyPhD/Part8_K3_InSample_2026-10-29"  # @param {type:"string"}
EXPECTED_IDENTITY = "3413465b508bb844"  # @param {type:"string"}
EXPECTED_PAYLOADS = 18964  # @param {type:"integer"}
# Step 6 (Tier A, eight AR chains at most, under a CPU-minute) runs only when True,
# and then only for AR chains the cache could not replay.
RUN_TIER_A = False  # @param {type:"boolean"}
PUSH_EVIDENCE = True  # @param {type:"boolean"}
# Step 8 pushes only when this is True (after the evidence has been reviewed).
CONFIRM_PUBLISH = False  # @param {type:"boolean"}
EVIDENCE_BRANCH_PREFIX = "part8-r1-replay"  # @param {type:"string"}
RELEASE_BRANCH_PREFIX = "part8-corrected-results"  # @param {type:"string"}
USE_CONSTRAINTS = True  # @param {type:"boolean"}
WORK = "/content/r1work"
SOURCE_URL = ""'''

SETUP = '''import os, re, sys, json, time, shutil, subprocess, importlib.util
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
PIN_COMMIT = str(PIN_COMMIT).strip().lower()
assert re.fullmatch(r"[0-9a-f]{40}", PIN_COMMIT), f"PIN_COMMIT must be a full 40-character commit SHA, got {PIN_COMMIT!r}"
DRIVE = Path(DRIVE_ROOT) / "baseline"
STAMP = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
EVIDENCE = Path(DRIVE_ROOT) / "r1_replay" / STAMP          # a new folder, never reused
WORK_DIR = Path(WORK)
WORK_DIR.mkdir(parents=True, exist_ok=True)
print("GitHub token:", "found in Colab secrets" if GITHUB_TOKEN else "not set (no push)")
print("Drive cache folder (read only):", DRIVE / "fit_cache" / EXPECTED_IDENTITY)
print("evidence folder:", EVIDENCE)'''

CLONE = '''# Credentials come from GIT_ASKPASS reading an environment variable; the URL never has them.
SECRETS = WORK_DIR / "secrets"
SECRETS.mkdir(exist_ok=True)
GIT_ENV = dict(os.environ, GIT_TERMINAL_PROMPT="0")
if GITHUB_TOKEN:
    askpass = SECRETS / "git_askpass.sh"
    askpass.write_text('#!/bin/sh\\ncase "$1" in\\n  Username*) echo "x-access-token" ;;\\n'
                       '  *) echo "$THESIS_GIT_TOKEN" ;;\\nesac\\n')
    askpass.chmod(0o700)
    GIT_ENV.update(GIT_ASKPASS=str(askpass), THESIS_GIT_TOKEN=GITHUB_TOKEN)

REPO = WORK_DIR / "academia7"
url = SOURCE_URL or f"https://github.com/{REPOSITORY}.git"
assert "@" not in url.split("//", 1)[-1].split("/", 1)[0], "no credentials in URLs"
if not (REPO / ".git").exists():
    subprocess.run(["git", "clone", "--branch", BRANCH, url, str(REPO)], check=True, env=GIT_ENV)
subprocess.run(["git", "fetch", "origin", BRANCH], cwd=REPO, check=True, env=GIT_ENV)
subprocess.run(["git", "checkout", "--detach", PIN_COMMIT], cwd=REPO, check=True)
COMMIT = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                        text=True, check=True).stdout.strip()
assert COMMIT == PIN_COMMIT, (COMMIT, PIN_COMMIT)
dirty = subprocess.run(["git", "status", "--porcelain"], cwd=REPO, capture_output=True,
                       text=True, check=True).stdout.strip()
assert not dirty, f"the checkout is not clean: {dirty[:500]}"
PROJECT = REPO / "my-thesis"
CODE = PROJECT / "code"
ORIGINAL = PROJECT / "output"
print("pinned commit:", COMMIT, "(clean)")
spec = importlib.util.spec_from_file_location("thesis_colab", PROJECT / "colab" / "thesis_colab.py")
tc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tc)'''

ENV = '''VENV = WORK_DIR / "venv311"
LOCK = CODE / "requirements.lock.txt"
CONSTRAINTS = CODE / "requirements.constraints.txt" if USE_CONSTRAINTS else None
PY = VENV / "bin" / "python"
try:
    tc.verify_environment(PY, LOCK, constraints=CONSTRAINTS)
    print("existing environment verified")
except Exception:
    PY = tc.create_environment(VENV, LOCK, constraints=CONSTRAINTS)
found = tc.verify_environment(PY, LOCK, constraints=CONSTRAINTS)
print(f"Python {found['python']}; {len(found['packages'])} pinned packages verified exactly")
RUN_ENV = dict(os.environ, PYTHONUNBUFFERED="1", MPLBACKEND="Agg")
RUN_ENV.pop("THESIS_GIT_TOKEN", None)                 # the analysis never sees the token
check = subprocess.run([str(PY), "-u", "code/run_all.py", "--data-only"], cwd=PROJECT,
                       env=RUN_ENV, capture_output=True, text=True)
print(check.stdout[-1500:], check.stderr[-1500:])
assert check.returncode == 0, "frozen-data verification failed; nothing was started"
FROZEN_SHA = tc.sha256(PROJECT / "data" / "frozen" / "thesis_input_2026-10-05.csv")
print("frozen input sha256:", FROZEN_SHA)'''

RESTORE = '''IDENTITY = tc.cache_identity(PY, CODE, "baseline")
print("cache identity of the pinned code:", IDENTITY)
assert IDENTITY == EXPECTED_IDENTITY, f"identity {IDENTITY} != {EXPECTED_IDENTITY}: wrong code/config/data"

# Restore onto the VM's local disk, OUTSIDE the repository; the Drive folders are only read.
CACHE_ROOT = WORK_DIR / "r1_cache"
CACHE_DIR = CACHE_ROOT / "fits"
if CACHE_DIR.exists():
    shutil.rmtree(CACHE_DIR)
restored = 0
for folder in tc.archive_folders(DRIVE, IDENTITY):
    count = tc.IncrementalArchive(CACHE_DIR, folder).restore(folder=folder)
    print(f"read {count} archived files from {folder}")
    restored += count
payloads = sum(1 for _ in CACHE_DIR.rglob("*.json"))
print(f"archived files read: {restored}; unique payloads on disk: {payloads}")
if payloads != EXPECTED_PAYLOADS:
    print(f"NOTE: {payloads} unique payloads, expected {EXPECTED_PAYLOADS} (recorded in the report)")
EVIDENCE.mkdir(parents=True, exist_ok=True)
(EVIDENCE / "restore.json").write_text(json.dumps(
    {"commit": COMMIT, "identity": IDENTITY, "archived_files_read": restored,
     "unique_payloads": payloads, "expected_payloads": EXPECTED_PAYLOADS}, indent=2))'''

REPORT = '''REPLAY_OUT = WORK_DIR / "replay_report"
run = subprocess.run([str(PY), "tools/r1_cache_replay_report.py", "--original", str(ORIGINAL),
                      "--cache-root", str(CACHE_ROOT), "--out", str(REPLAY_OUT),
                      "--expected-identity", EXPECTED_IDENTITY],
                     cwd=CODE, env=RUN_ENV, capture_output=True, text=True)
print(run.stdout[-6000:], run.stderr[-3000:])
assert run.returncode == 0, "replay report failed"
REPLAY = json.loads((REPLAY_OUT / "replay_report.json").read_text())
assert REPLAY["estimations_performed"] == "none"
shutil.copytree(REPLAY_OUT, EVIDENCE / "replay_report", dirs_exist_ok=True)
print(json.dumps({k: v for k, v in REPLAY.items() if k != "per_chain"}, indent=1))'''

R1RUN = '''def r1(staging, *extra):
    """One R1 workflow run with the restored cache and NO --approve."""
    command = [str(PY), "tools/correct_from_published.py", "--original", str(ORIGINAL),
               "--staging", str(staging), "--cache-root", str(CACHE_ROOT), *extra]
    assert "--approve" not in command
    if Path(staging).exists():
        shutil.rmtree(staging)
    done = subprocess.run(command, cwd=CODE, env=RUN_ENV, capture_output=True, text=True)
    print(done.stdout[-5000:], done.stderr[-3000:])
    summary = json.loads((Path(staging) / "r1_summary.json").read_text())
    assert not summary.get("estimations_performed"), summary.get("estimations_performed")
    return done.returncode, summary

LEGACY = WORK_DIR / "r1_legacy"
CORRECTED = WORK_DIR / "r1_corrected"
RELEASE = WORK_DIR / "r1_release"
code, legacy = r1(LEGACY, "--legacy")
assert code == 0, "legacy validation gate FAILED: a regenerated table differs from the original"
code, corrected = r1(CORRECTED, "--legacy-staging", str(LEGACY), "--release", str(RELEASE))
assert code == 0
for name, folder in (("legacy", LEGACY), ("corrected", CORRECTED)):
    for item in ("r1_summary.json", "r1_comparison.csv", "r1_reconciliation.csv"):
        if (folder / item).exists():
            shutil.copy2(folder / item, EVIDENCE / f"{name}_{item}")
shutil.copytree(RELEASE / "manifests", EVIDENCE / "release_manifests", dirs_exist_ok=True)
print("chain sources (corrected run):",
      {source: len(tasks) for source, tasks in corrected["chain_sources"].items()})
print("replayed from the cache:", corrected["chain_sources"].get("cache", []))
print("retained (still pending):", json.dumps(corrected.get("retained"), indent=1)[:3000])'''

TIER_A = '''if not RUN_TIER_A:
    print("RUN_TIER_A is False: no estimation. Review the replay report first.")
else:
    TASKS = REPLAY["tier_a_ar_chains_to_estimate"]          # AR chains the cache cannot replay
    print("Tier A chains to re-estimate:", TASKS or "none (all replayed from the cache)")
    if TASKS:
        validation = WORK_DIR / "tier_a_validation"
        check = subprocess.run([str(PY), "tools/r1_validate_ar_refit.py", "--original",
                                str(ORIGINAL), "--cache-root", str(CACHE_ROOT), "--out",
                                str(validation), *[a for t in TASKS for a in ("--task", t)]],
                               cwd=CODE, env=RUN_ENV, capture_output=True, text=True)
        print(check.stdout[-4000:], check.stderr[-2000:])
        shutil.copytree(validation, EVIDENCE / "tier_a_validation", dirs_exist_ok=True)
        assert check.returncode == 0, "AR refit validation FAILED: nothing re-estimated is used"
        approve = [a for t in TASKS for a in ("--approve", t)]
        refit = WORK_DIR / "refit_cache"
        for staging, extra in ((WORK_DIR / "r1_tier_a_legacy", ["--legacy"]),
                               (WORK_DIR / "r1_tier_a", ["--legacy-staging",
                                                         str(WORK_DIR / "r1_tier_a_legacy"),
                                                         "--release",
                                                         str(WORK_DIR / "r1_tier_a_release")])):
            if staging.exists():
                shutil.rmtree(staging)
            done = subprocess.run([str(PY), "tools/correct_from_published.py", "--original",
                                   str(ORIGINAL), "--staging", str(staging), "--cache-root",
                                   str(CACHE_ROOT), "--refit-cache", str(refit), *approve,
                                   *extra], cwd=CODE, env=RUN_ENV, capture_output=True,
                                  text=True)
            print(done.stdout[-4000:], done.stderr[-2000:])
            assert done.returncode == 0, f"Tier A run failed: {staging}"
            summary = json.loads((staging / "r1_summary.json").read_text())
            print("estimations performed:", summary.get("estimations_performed"))
            shutil.copy2(staging / "r1_summary.json", EVIDENCE / f"{staging.name}_summary.json")
            shutil.copy2(staging / "r1_comparison.csv", EVIDENCE / f"{staging.name}_comparison.csv")'''

PUBLISH = """# Step 8: choose WHAT to publish only from the files the completed steps wrote, never from
# variables left over from earlier cells (a stale RELEASE / corrected from step 6 would
# publish the wrong release after Tier A). Self-contained: it can be pasted into a session
# that ran the older notebook (it needs only WORK_DIR, EVIDENCE, REPO, PROJECT, PIN_COMMIT,
# COMMIT, STAMP, GIT_ENV, GITHUB_TOKEN, RUN_TIER_A and the branch prefixes).
# Nothing is pushed unless CONFIRM_PUBLISH is True; otherwise this is a dry run.
import json as _json, shutil as _shutil, subprocess as _subprocess
from pathlib import Path as _Path


def _load(path):
    path = _Path(path)
    if not path.is_file():
        raise RuntimeError(f"required output missing: {path}")
    return _json.loads(path.read_text())


def select_publication(work_dir, run_tier_a, pin_commit):
    \"\"\"The release to publish, with its run ID and evidence; fails rather than guesses.\"\"\"
    work_dir = _Path(work_dir)
    tier_a_dirs = [work_dir / n for n in ("r1_tier_a", "r1_tier_a_release",
                                          "r1_tier_a_legacy", "tier_a_validation")]
    replay = _load(work_dir / "replay_report" / "replay_report.json")
    tasks = sorted(replay["tier_a_ar_chains_to_estimate"])
    if run_tier_a and tasks:
        label, staging, release = "tier-a", work_dir / "r1_tier_a", work_dir / "r1_tier_a_release"
        validation = _load(work_dir / "tier_a_validation" / "ar_refit_validation.json")
        if validation.get("ok") is not True:
            raise RuntimeError("Tier A AR validation did not pass; nothing is published")
        legacy = work_dir / "r1_tier_a_legacy" / "r1_comparison.csv"
        if not legacy.is_file():
            raise RuntimeError(f"required output missing: {legacy}")
        import csv
        with open(legacy, newline="") as handle:
            bad = [r["path"] for r in csv.DictReader(handle)
                   if r["status"] not in ("identical", "equal_within_fp_tolerance")]
        if bad:
            raise RuntimeError(f"Tier A legacy gate failed for {bad[:5]}; nothing is published")
    elif run_tier_a:
        raise RuntimeError("RUN_TIER_A is True but the replay left no AR chain to re-estimate; "
                           "there is no Tier A release to publish (publish step 6 with "
                           "RUN_TIER_A = False)")
    else:
        present = [str(d) for d in tier_a_dirs if d.exists()]
        if present:
            raise RuntimeError("RUN_TIER_A is False but Tier A outputs exist "
                               f"({present}); refusing to guess which release to publish")
        label, staging, release = "replay", work_dir / "r1_corrected", work_dir / "r1_release"
    summary = _load(staging / "r1_summary.json")
    manifest = _load(release / "manifests" / "correction_run_manifest.json")
    released = _load(release / "manifests" / "correction_summary.json")
    problems = []
    if manifest.get("run_id") != summary.get("run_id"):
        problems.append(f"release run_id {manifest.get('run_id')} != staging {summary.get('run_id')}")
    if released.get("run_id") != summary.get("run_id"):
        problems.append("release correction_summary.json is not the staging summary")
    if manifest.get("code_commit_sha") != pin_commit:
        problems.append(f"release built from {manifest.get('code_commit_sha')}, not {pin_commit}")
    if manifest.get("code_tree_dirty"):
        problems.append("release built from a dirty tree")
    reestimated = sorted(summary.get("chain_sources", {}).get("re-estimated", []))
    if label == "tier-a" and reestimated != tasks:
        problems.append(f"re-estimated chains {reestimated} != Tier A tasks {tasks}")
    if label == "replay" and reestimated:
        problems.append(f"step-6 release unexpectedly contains re-estimated chains {reestimated}")
    if problems:
        raise RuntimeError("publication refused: " + "; ".join(problems))
    return {"label": label, "release": str(release), "staging": str(staging),
            "run_id": summary["run_id"], "re_estimated": reestimated,
            "estimations_performed": summary.get("estimations_performed") or {},
            "chain_sources": {k: len(v) for k, v in summary.get("chain_sources", {}).items()}}


PLAN = select_publication(WORK_DIR, RUN_TIER_A, PIN_COMMIT)
_Path(EVIDENCE).mkdir(parents=True, exist_ok=True)
(_Path(EVIDENCE) / "publication_plan.json").write_text(_json.dumps(PLAN, indent=2))
_shutil.copytree(_Path(PLAN["release"]) / "manifests", _Path(EVIDENCE) / "published_release_manifests",
                 dirs_exist_ok=True)
print("publication plan:", _json.dumps(PLAN, indent=1))
CONFIRM = bool(globals().get("CONFIRM_PUBLISH", False))
if not CONFIRM:
    print("DRY RUN: CONFIRM_PUBLISH is not True; nothing pushed. Evidence is on Drive:", EVIDENCE)
elif not PUSH_EVIDENCE:
    print("PUSH_EVIDENCE is off; evidence is on Drive:", EVIDENCE)
elif not GITHUB_TOKEN:
    print("no GITHUB_TOKEN secret; evidence is on Drive only:", EVIDENCE)
else:
    def push(branch, paths, message):
        _subprocess.run(["git", "checkout", "-q", "-B", branch, PIN_COMMIT], cwd=REPO, check=True)
        _subprocess.run(["git", "add", "--", *paths], cwd=REPO, check=True)
        _subprocess.run(["git", "-c", "user.name=Thesis pipeline (Colab)", "-c",
                         "user.email=thesis-pipeline@users.noreply.github.com", "commit", "-q",
                         "-m", message], cwd=REPO, check=True)
        _subprocess.run(["git", "push", "-u", "origin", branch], cwd=REPO, check=True, env=GIT_ENV)
        return _subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                               text=True, check=True).stdout.strip()
    what = ("Tier A: AR chains re-estimated (" + ", ".join(PLAN["re_estimated"]) + ")"
            if PLAN["label"] == "tier-a" else "cache replay; no estimation")
    target = _Path(PROJECT) / "reports" / "part8" / "corrections" / "r1" / f"replay_{STAMP}"
    _shutil.copytree(EVIDENCE, target)
    sha = push(f"{EVIDENCE_BRANCH_PREFIX}/{STAMP}", [str(target.relative_to(REPO))],
               f"R1 evidence {STAMP} ({what}; run {PLAN['run_id']}; code {COMMIT[:12]})")
    print("evidence branch:", f"{EVIDENCE_BRANCH_PREFIX}/{STAMP}", sha)
    release_target = _Path(PROJECT) / "output_corrected"
    if release_target.exists():
        _shutil.rmtree(release_target)
    _shutil.copytree(PLAN["release"], release_target)
    branch = f"{RELEASE_BRANCH_PREFIX}/r1-{PLAN['label']}-{STAMP}"
    sha = push(branch, [str(release_target.relative_to(REPO))],
               f"Part 8 corrected release (provisional) {PLAN['run_id']}: {what}; "
               f"code {COMMIT[:12]}")
    print("release branch:", branch, sha)"""

STEP8_PASTE_HEADER = """# R1 Step 8 (fixed), for a Colab session that is ALREADY OPEN and ran the older notebook.
# Paste this whole file into a NEW cell of that session and run it INSTEAD of the old step-8
# cell (never run the old one: it publishes the step-6 release). It reads only what the
# completed steps wrote to disk. Set CONFIRM_PUBLISH = True in the session only after the
# dry run has been reviewed and publication authorised.
# Generated by make_r1_replay_notebook.py; identical to the notebook's step-8 cell.

"""

PIN_DEFAULT_LINE = 'PIN_COMMIT = "__PIN__"'

CELLS = [
    ("markdown", MD_INTRO),
    ("code", SETTINGS),
    ("markdown", "## 1. Drive, secret, and a new evidence folder"),
    ("code", SETUP),
    ("markdown", "## 2. Clone and check out the pinned, clean commit"),
    ("code", CLONE),
    ("markdown", "## 3. Approved Python 3.11 environment and frozen-data check"),
    ("code", ENV),
    ("markdown", "## 4. Restore the original fit cache (read only) and check its identity"),
    ("code", RESTORE),
    ("markdown", "## 5. Per-chain replay report for the 20 pending chains (reads only)"),
    ("code", REPORT),
    ("markdown", "## 6. R1 workflow with the cache and no `--approve`: legacy gate, then "
                 "corrected release"),
    ("code", R1RUN),
    ("markdown", "## 7. Optional, approved in principle: Tier A (AR chains not in the cache)"),
    ("code", TIER_A),
    ("markdown", "## 8. Evidence to Drive and to new GitHub branches"),
    ("code", PUBLISH),
]


def build(pin: str) -> dict:
    cells = []
    for kind, text in CELLS:
        # Substitute the pin ONLY in the default assignment. A blanket replace once also
        # rewrote the setup cell's guard, which then rejected the intended pinned SHA.
        text = text.replace(PIN_DEFAULT_LINE, f'PIN_COMMIT = "{pin}"')
        lines = text.splitlines(keepends=True)
        cell = {"cell_type": kind, "metadata": {}, "source": lines}
        if kind == "code":
            cell.update(execution_count=None, outputs=[])
        cells.append(cell)
    return {"cells": cells, "metadata": {"colab": {"provenance": []},
                                         "kernelspec": {"display_name": "Python 3",
                                                        "name": "python3"},
                                         "language_info": {"name": "python"}},
            "nbformat": 4, "nbformat_minor": 0}


if __name__ == "__main__":
    import sys
    pin = sys.argv[1] if len(sys.argv) > 1 else "__PIN__"
    target = Path(__file__).with_name("r1_cache_replay.ipynb")
    target.write_text(json.dumps(build(pin), indent=1) + "\n", encoding="utf-8")
    print("wrote", target)
    paste = Path(__file__).with_name("r1_step8_publish_cell.py")
    paste.write_text(STEP8_PASTE_HEADER + PUBLISH + "\n", encoding="utf-8")
    print("wrote", paste)
