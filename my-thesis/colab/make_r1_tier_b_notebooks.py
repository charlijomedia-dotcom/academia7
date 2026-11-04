#!/usr/bin/env python3
"""Builds the three independent Tier B batch notebooks from one source.

  python colab/make_r1_tier_b_notebooks.py <ORCHESTRATION_COMMIT_SHA>

writes colab/r1_tier_b1_msar_300.ipynb, colab/r1_tier_b2_msar_remaining.ipynb and
colab/r1_tier_b3_arma_star.ipynb. Each is self-contained: from its first cell it mounts
Drive, checks out the orchestration commit and, separately, the pinned scientific commit,
builds the approved environment, restores the original cache, the Tier A cache and ITS OWN
batch checkpoints, and runs (only when RUN_TIER_B = True) ITS OWN chains.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r1_tierb as tb  # noqa: E402

NOTEBOOKS = {"B1": "r1_tier_b1_msar_300.ipynb", "B2": "r1_tier_b2_msar_remaining.ipynb",
             "B3": "r1_tier_b3_arma_star.ipynb"}
ORCH_DEFAULT_LINE = 'ORCH_COMMIT = "__ORCH__"'


def intro(batch: str) -> str:
    tasks = tb.BATCHES[batch]
    rows = "\n".join(f"| `{t}` | {tb.TIER_B_CHAINS[t][0]} | "
                     f"{tb.TIER_B_CHAINS[t][0] * tb.TIER_B_CHAINS[t][1] / 3600:.2f} |"
                     for t in tasks)
    origins = sum(tb.TIER_B_CHAINS[t][0] for t in tasks)
    hours = sum(tb.TIER_B_CHAINS[t][0] * tb.TIER_B_CHAINS[t][1] for t in tasks) / 3600
    return f"""# R1 Tier B — batch {batch} (independent notebook)

This notebook re-estimates **only** these chains (whole chains, the pinned code, no K=3):

| Task | Origins | Historical fitting hours |
|---|---|---|
{rows}
| **Total** | **{origins}** | **{hours:.2f}** |

It is independent of the other two batch notebooks: run it in a fresh Colab runtime,
before, after or at the same time as them. Batch work is written on Drive only under
`baseline/r1_tierb_batches/{batch}/`; the Drive checkpoint check (section 3b) writes only
under its own disposable `baseline/r1_tierb_drive_check/<session>/`.

**Defaults are safe.** `RUN_TIER_B = False`: *Run all* only checks and restores; it
estimates nothing. `RUN_AGGREGATION = False` and nothing in this notebook pushes to GitHub.

**A certificate is not an approval.** A completed batch is certified as
`COMPUTATION_COMPLETE_REVIEW_REQUIRED`, `..._SENSITIVITY_REPORTED` or `..._REPRODUCED`;
every certificate says `scientific_approval: not granted`.

**Runtime.** No managed Colab runtime can guarantee 24 hours; plan for interruption.
Set `RUNTIME_BUDGET_HOURS` below the limit of your plan (for Colab Pro+ use 20). When the
budget is nearly used, no new origin is started, running origins finish, everything is
checkpointed and verified, and the session ends with the remaining work reported. Run all
again in a new runtime to resume from the last verified checkpoint.
"""


def settings(batch: str) -> str:
    return f'''# @title Settings for batch {batch}
BATCH_ID = "{batch}"  # fixed for this notebook
REPOSITORY = "charlijomedia-dotcom/academia7"  # @param {{type:"string"}}
BRANCH = "part8-r1-rescore"  # @param {{type:"string"}}
# Orchestration code (this notebook's helpers) and the pinned scientific code are checked
# out separately and both verified.
{ORCH_DEFAULT_LINE}  # @param {{type:"string"}}
PIN_COMMIT = "{tb.SCIENTIFIC_PIN}"  # @param {{type:"string"}}
DRIVE_ROOT = "/content/drive/MyDrive/KillyPhD/Part8_K3_InSample_2026-10-29"  # @param {{type:"string"}}
EXPECTED_IDENTITY = "{tb.CACHE_IDENTITY}"  # @param {{type:"string"}}
EXPECTED_ORIGINAL_PAYLOADS = {tb.ORIGINAL_PAYLOADS}  # @param {{type:"integer"}}
TIER_A_ARCHIVE_SHA256 = "{tb.TIER_A_ARCHIVE_SHA256}"  # @param {{type:"string"}}
# Runtime budget from the start of this Colab VM. Conservative default; Colab Pro+: 20.
RUNTIME_BUDGET_HOURS = 11.0  # @param {{type:"number"}}
RESERVE_MINUTES = 30  # @param {{type:"integer"}}
BACKUP_MINUTES = 10  # @param {{type:"integer"}}
MAX_WORKERS = {tb.DEFAULT_WORKERS[batch]}  # @param {{type:"integer"}}
# Safety switches: estimation and aggregation run only when explicitly set to True.
RUN_TIER_B = False  # @param {{type:"boolean"}}
RUN_AGGREGATION = False  # @param {{type:"boolean"}}
# Non-estimating check of the checkpoint protocol on the mounted Drive, in a disposable
# namespace baseline/r1_tierb_drive_check/<session>/ (synthetic payloads only).
RUN_DRIVE_CHECK = True  # @param {{type:"boolean"}}
# To confirm persistence across runtimes: the check id printed by an EARLIER runtime.
DRIVE_CHECK_VERIFY_ID = ""  # @param {{type:"string"}}
CONFIRM_PUBLISH = False  # publication is not implemented in these notebooks
USE_CONSTRAINTS = True  # @param {{type:"boolean"}}
WORK = "/content/r1tierb_{batch}"'''


SETUP = '''import os, re, sys, json, time, shutil, secrets, subprocess, importlib.util
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
assert BATCH_ID in ("B1", "B2", "B3")
assert 0 < float(RUNTIME_BUDGET_HOURS) <= 23.5, "RUNTIME_BUDGET_HOURS must be in (0, 23.5]"
assert 5 <= int(BACKUP_MINUTES) <= 30 and int(MAX_WORKERS) >= 1
SESSION = f"{BATCH_ID}-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{secrets.token_hex(3)}"
WORK_DIR = Path(WORK)
WORK_DIR.mkdir(parents=True, exist_ok=True)
print("session:", SESSION, "| GitHub token:", "found" if GITHUB_TOKEN else "not set")'''

CLONE = '''SECRETS = WORK_DIR / "secrets"
SECRETS.mkdir(exist_ok=True)
GIT_ENV = dict(os.environ, GIT_TERMINAL_PROMPT="0")
if GITHUB_TOKEN:                          # read access only; nothing here pushes
    askpass = SECRETS / "git_askpass.sh"
    askpass.write_text('#!/bin/sh\\ncase "$1" in\\n  Username*) echo "x-access-token" ;;\\n'
                       '  *) echo "$THESIS_GIT_TOKEN" ;;\\nesac\\n')
    askpass.chmod(0o700)
    GIT_ENV.update(GIT_ASKPASS=str(askpass), THESIS_GIT_TOKEN=GITHUB_TOKEN)
REPO = WORK_DIR / "repo"                  # orchestration checkout
PINNED = WORK_DIR / "pinned"              # scientific-code checkout (worktree)
url = f"https://github.com/{REPOSITORY}.git"
if not (REPO / ".git").exists():
    subprocess.run(["git", "clone", "--branch", BRANCH, url, str(REPO)], check=True, env=GIT_ENV)
subprocess.run(["git", "fetch", "origin", BRANCH], cwd=REPO, check=True, env=GIT_ENV)
subprocess.run(["git", "checkout", "-q", "--detach", ORCH_COMMIT], cwd=REPO, check=True)
if not PINNED.exists():
    subprocess.run(["git", "worktree", "add", "-q", "--detach", str(PINNED), PIN_COMMIT],
                   cwd=REPO, check=True)
def _head(path):
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=path, capture_output=True,
                          text=True, check=True).stdout.strip()
def _clean(path):
    return not subprocess.run(["git", "status", "--porcelain"], cwd=path, capture_output=True,
                              text=True, check=True).stdout.strip()
assert _head(REPO) == ORCH_COMMIT and _clean(REPO), "orchestration checkout not at ORCH_COMMIT or dirty"
assert _head(PINNED) == PIN_COMMIT and _clean(PINNED), "scientific checkout not at PIN_COMMIT or dirty"
subprocess.run(["git", "merge-base", "--is-ancestor", PIN_COMMIT, ORCH_COMMIT], cwd=REPO, check=True)
CODE = PINNED / "my-thesis" / "code"      # every estimation and table comes from here
ORIGINAL = PINNED / "my-thesis" / "output"
ORCH = REPO / "my-thesis" / "colab"       # orchestration helpers only
assert (ORCH / "thesis_colab.py").read_bytes() == (PINNED / "my-thesis" / "colab" / "thesis_colab.py").read_bytes()
sys.path.insert(0, str(ORCH))
import r1_tierb as tb
spec = importlib.util.spec_from_file_location("thesis_colab", ORCH / "thesis_colab.py")
tc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tc)
TASKS = list(tb.batch_tasks(BATCH_ID))
print(json.dumps(tb.validate_partition(), indent=1))
print("this batch:", TASKS)
print("orchestration", ORCH_COMMIT[:12], "| scientific code", PIN_COMMIT[:12])'''

ENV = '''VENV = WORK_DIR / "venv311"
LOCK = CODE / "requirements.lock.txt"
CONSTRAINTS = CODE / "requirements.constraints.txt" if USE_CONSTRAINTS else None
PY = VENV / "bin" / "python"
try:
    tc.verify_environment(PY, LOCK, constraints=CONSTRAINTS)
except Exception:
    PY = tc.create_environment(VENV, LOCK, constraints=CONSTRAINTS)
FOUND = tc.verify_environment(PY, LOCK, constraints=CONSTRAINTS)
RUN_ENV = dict(os.environ, PYTHONUNBUFFERED="1", MPLBACKEND="Agg")
RUN_ENV.pop("THESIS_GIT_TOKEN", None)
check = subprocess.run([str(PY), "-u", "code/run_all.py", "--data-only"], cwd=PINNED / "my-thesis",
                       env=RUN_ENV, capture_output=True, text=True)
print(check.stdout[-1200:], check.stderr[-1200:])
assert check.returncode == 0, "frozen-data verification failed; nothing was started"
FROZEN_SHA = tc.sha256(PINNED / "my-thesis" / "data" / "frozen" / "thesis_input_2026-10-05.csv")
IDENTITY = tc.cache_identity(PY, CODE, "baseline")
assert IDENTITY == EXPECTED_IDENTITY, f"cache identity {IDENTITY} != {EXPECTED_IDENTITY}"
print(f"Python {FOUND['python']}; {len(FOUND['packages'])} packages verified; identity {IDENTITY}")'''

DRIVE_CHECK = '''# Synthetic payloads only: no model is fitted. Writes only under
# baseline/r1_tierb_drive_check/<SESSION>/ and verifies that nothing else changed.
import r1_tierb_drive_check as dc
if DRIVE_CHECK_VERIFY_ID:
    persisted = dc.verify(DRIVE_ROOT, DRIVE_CHECK_VERIFY_ID.strip())
    print("cross-runtime persistence of", persisted["check_id"], "OK" if persisted["ok"] else "FAILED")
    assert persisted["ok"], "checkpoints written by an earlier runtime did not restore identically"
if not RUN_DRIVE_CHECK:
    print("RUN_DRIVE_CHECK is False: Drive checkpoint check skipped")
else:
    ORIGINAL_ARCHIVES = list(tc.archive_folders(Path(DRIVE_ROOT) / "baseline", IDENTITY))
    DRIVE_REPORT = dc.run(DRIVE_ROOT, SESSION, protected_extra=ORIGINAL_ARCHIVES)
    print(dc.summary(DRIVE_REPORT))
    print("folder:", DRIVE_REPORT["folder"])
    print("To confirm persistence, set DRIVE_CHECK_VERIFY_ID =", repr(SESSION),
          "in a NEW runtime and run up to this cell.")
    assert DRIVE_REPORT["ok"], "the Drive checkpoint check failed: do not run this batch"'''

RESTORE = '''DRIVE = Path(DRIVE_ROOT) / "baseline"
BATCH_ROOT = tb.batch_root(DRIVE_ROOT, BATCH_ID)  # the only place batch work is written on Drive
# 1. original cache, read only, onto local disk
ORIGINAL_CACHE = WORK_DIR / "original_cache"
if not (ORIGINAL_CACHE / "fits").exists():
    for folder in tc.archive_folders(DRIVE, IDENTITY):
        tc.IncrementalArchive(ORIGINAL_CACHE / "fits", folder).restore(folder=folder)
ORIGINAL_PAYLOADS = sum(1 for _ in (ORIGINAL_CACHE / "fits").rglob("*.json"))
assert ORIGINAL_PAYLOADS == EXPECTED_ORIGINAL_PAYLOADS, f"{ORIGINAL_PAYLOADS} original payloads"
# 2. Tier A refit cache, read only, verified (sha256, 5,597 marked payloads)
TIER_A_ARCHIVE = Path(DRIVE_ROOT) / tb.TIER_A_ARCHIVE_RELATIVE
TIER_A_FITS = WORK_DIR / "tier_a" / "fits"
if TIER_A_FITS.exists():
    shutil.rmtree(TIER_A_FITS)
TIER_A = tb.restore_tier_a(TIER_A_ARCHIVE, TIER_A_FITS, expected_sha256=TIER_A_ARCHIVE_SHA256)
# 3. this batch's own committed checkpoints
CHAINS = WORK_DIR / "chains"
RESTORED = {}
for task in TASKS:
    RESTORED[task] = tb.restore_checkpoints(BATCH_ROOT / "checkpoints" / tb.slug(task),
                                            CHAINS / tb.slug(task) / "fits")
print(json.dumps({"original_payloads": ORIGINAL_PAYLOADS, "tier_a": TIER_A,
                  "batch_checkpoints": RESTORED}, indent=1))'''

PREFLIGHT = '''PREFLIGHT = WORK_DIR / f"preflight-{SESSION}.json"
pre = subprocess.run([str(PY), str(ORCH / "r1_tierb_worker.py"), "preflight", "--batch", BATCH_ID,
                      "--code-dir", str(CODE), "--original", str(ORIGINAL),
                      "--batch-fits", str(CHAINS), "--tier-a-fits", str(TIER_A_FITS),
                      "--report", str(PREFLIGHT)], env=RUN_ENV, capture_output=True, text=True)
print(pre.stdout[-3000:], pre.stderr[-2000:])
REPORT = json.loads(PREFLIGHT.read_text())
assert pre.returncode == 0 and not REPORT["problems"], f"preflight failed: {REPORT['problems']}"
for task, chain in REPORT["batch_chains"].items():
    print(f"{task:<24} {chain['completed']:>4}/{chain['planned']} origins committed"
          + (" (complete)" if chain["complete"] else ""))
PROVENANCE = {"batch": BATCH_ID, "scientific_commit": PIN_COMMIT, "orchestration_commit": ORCH_COMMIT,
              "cache_identity": IDENTITY, "frozen_data_sha256": FROZEN_SHA,
              "python": FOUND["python"], "packages": FOUND["packages"],
              "tier_a_archive_sha256": TIER_A["archive_sha256"]}
(WORK_DIR / "provenance.json").write_text(json.dumps(PROVENANCE, indent=1, default=str))'''

RUN = '''SUPERVISOR_PID = WORK_DIR / "supervisor.pid"
SUPERVISOR_EXIT = WORK_DIR / "supervisor.exit"
SUPERVISOR_LOG = WORK_DIR / "supervisor_console.log"
if not RUN_TIER_B:
    print("RUN_TIER_B is False: no estimation. Checks and restores are complete.")
elif all(c["complete"] for c in REPORT["batch_chains"].values()):
    print("every chain of this batch is already complete: nothing to estimate")
elif SUPERVISOR_PID.exists() and tc.process_alive(int(SUPERVISOR_PID.read_text())):
    print("a supervisor is already running in this runtime; re-run the next cell to watch it")
else:
    START_EPOCH = tb.vm_start_epoch()     # the budget counts from this VM's start
    command = [str(PY), "-u", str(ORCH / "r1_tierb_supervisor.py"), "--batch", BATCH_ID,
               "--python", str(PY), "--code-dir", str(CODE), "--original", str(ORIGINAL),
               "--work", str(WORK_DIR), "--drive-root", DRIVE_ROOT, "--session", SESSION,
               "--start-epoch", str(START_EPOCH), "--budget-hours", str(RUNTIME_BUDGET_HOURS),
               "--reserve-minutes", str(RESERVE_MINUTES), "--backup-minutes", str(BACKUP_MINUTES),
               "--max-workers", str(min(int(MAX_WORKERS), os.cpu_count() or 1)),
               "--skip-complete", str(PREFLIGHT),
               "--provenance", str(WORK_DIR / "provenance.json")]
    pid = tc.launch_background(command, cwd=WORK_DIR, console=SUPERVISOR_LOG,
                               exit_file=SUPERVISOR_EXIT, pid_file=SUPERVISOR_PID, env=RUN_ENV)
    print(f"supervisor started (pid {pid}); budget {RUNTIME_BUDGET_HOURS} h from VM start, "
          f"{(time.time() - START_EPOCH) / 3600:.2f} h already used")'''

WATCH = '''# Re-run this cell to re-attach after a browser disconnect; stopping it stops only the watching.
if not SUPERVISOR_PID.exists():
    print("no supervisor was started in this runtime")
else:
    while tc.process_alive(int(SUPERVISOR_PID.read_text())):
        lines = SUPERVISOR_LOG.read_text().splitlines() if SUPERVISOR_LOG.exists() else []
        done = {t: sum(1 for _ in open(CHAINS / tb.slug(t) / "progress.jsonl"))
                if (CHAINS / tb.slug(t) / "progress.jsonl").exists() else 0 for t in TASKS}
        print(time.strftime("%H:%M:%S"), "| origins estimated this batch:", done,
              "|", lines[-1] if lines else "")
        time.sleep(300)
    print("supervisor exit:", SUPERVISOR_EXIT.read_text().strip() if SUPERVISOR_EXIT.exists() else "?")'''

FINALIZE = '''# Certify only what is committed on Drive (restored afresh), never local state alone.
if not RUN_TIER_B and not all(c["complete"] for c in REPORT["batch_chains"].values()):
    print("RUN_TIER_B is False and the batch is not complete: nothing to certify")
else:
    code = SUPERVISOR_EXIT.read_text().strip() if SUPERVISOR_EXIT.exists() else "none"
    if code == "2":
        raise SystemExit("the session ended with an error; see the session folder on Drive")
    cert = subprocess.run([str(PY), str(ORCH / "r1_tierb_worker.py"), "certify", "--batch", BATCH_ID,
                           "--code-dir", str(CODE), "--original", str(ORIGINAL),
                           "--batch-fits", str(CHAINS), "--drive-root", DRIVE_ROOT,
                           "--session", SESSION, "--provenance", str(WORK_DIR / "provenance.json"),
                           "--report", str(WORK_DIR / f"certify-{SESSION}.json")],
                          env=RUN_ENV, capture_output=True, text=True)
    print(cert.stdout[-4000:], cert.stderr[-1500:])
    if cert.returncode == 3:
        print("NOT COMPLETE. Remaining work is listed above; open this notebook in a new "
              "runtime and Run all with RUN_TIER_B = True to resume.")
    elif cert.returncode != 0:
        raise SystemExit("certification failed")'''

AGGREGATE = '''# Optional, from any one batch notebook, after B1, B2 and B3 are all certified.
# It never estimates and never pushes; it writes a dry-run plan to
# baseline/r1_tierb_aggregation/<stamp>/ on Drive.
if not RUN_AGGREGATION:
    print("RUN_AGGREGATION is False")
else:
    TIER_A_RELEASE = WORK_DIR / "tier_a_release"
    if not TIER_A_RELEASE.exists():
        subprocess.run(["git", "fetch", "origin", "part8-corrected-results/r1-tier-a-20261103T063749Z"],
                       cwd=REPO, check=True, env=GIT_ENV)
        TIER_A_RELEASE.mkdir(parents=True)
        archive = subprocess.run(["git", "archive", tb.TIER_A_RELEASE_COMMIT, "my-thesis/output_corrected"],
                                 cwd=REPO, check=True, capture_output=True).stdout
        subprocess.run(["tar", "-x", "-C", str(TIER_A_RELEASE)], input=archive, check=True)
    agg = subprocess.run([str(PY), str(ORCH / "r1_tierb_aggregate.py"), "--drive-root", DRIVE_ROOT,
                          "--code-dir", str(CODE), "--original", str(ORIGINAL),
                          "--cache-root", str(ORIGINAL_CACHE), "--tier-a-archive", str(TIER_A_ARCHIVE),
                          "--tier-a-release", str(TIER_A_RELEASE / "my-thesis" / "output_corrected"),
                          "--unaffected-csv", str(REPO / "my-thesis" / "reports" / "part8" / "corrections"
                                                  / "r1" / "nonpublished_chain_classification.csv"),
                          "--work", str(WORK_DIR / "aggregation")],
                         cwd=PINNED / "my-thesis" / "code", env=RUN_ENV, capture_output=True, text=True)
    print(agg.stdout[-6000:], agg.stderr[-2000:])
    status = [l for l in agg.stdout.splitlines() if l.startswith("AGGREGATION_STATUS: ")]
    print(status[-1] if status else "AGGREGATION_STATUS: unknown (see the output above)")
    print("This is a dry run. A completed computation is NOT a scientifically approved result; "
          "nothing was published.")'''


def cells(batch: str) -> list[tuple[str, str]]:
    return [("markdown", intro(batch)), ("code", settings(batch)),
            ("markdown", "## 1. Drive and settings check"), ("code", SETUP),
            ("markdown", "## 2. Orchestration and pinned scientific code, both verified"),
            ("code", CLONE),
            ("markdown", "## 3. Approved environment, frozen data, cache identity"), ("code", ENV),
            ("markdown", "## 3b. Google Drive checkpoint check (disposable namespace; no estimation)"),
            ("code", DRIVE_CHECK),
            ("markdown", "## 4. Restore: original cache, Tier A cache, this batch's checkpoints"),
            ("code", RESTORE),
            ("markdown", "## 5. Preflight (no estimation): Tier A chains, this batch's progress"),
            ("code", PREFLIGHT),
            ("markdown", "## 6. Run this batch — only when `RUN_TIER_B = True`"), ("code", RUN),
            ("markdown", "## 7. Watch (re-attach after a disconnect)"), ("code", WATCH),
            ("markdown", "## 8. Certify from the verified Drive checkpoints"), ("code", FINALIZE),
            ("markdown", "## 9. Optional: aggregate B1+B2+B3 (dry run; `RUN_AGGREGATION`)"),
            ("code", AGGREGATE)]


def build(batch: str, orch: str) -> dict:
    out = []
    for kind, text in cells(batch):
        text = text.replace(ORCH_DEFAULT_LINE, f'ORCH_COMMIT = "{orch}"')
        cell = {"cell_type": kind, "metadata": {}, "source": text.splitlines(keepends=True)}
        if kind == "code":
            cell.update(execution_count=None, outputs=[])
        out.append(cell)
    return {"cells": out, "metadata": {"colab": {"provenance": []},
                                       "kernelspec": {"display_name": "Python 3", "name": "python3"},
                                       "language_info": {"name": "python"}},
            "nbformat": 4, "nbformat_minor": 0}


if __name__ == "__main__":
    orch = sys.argv[1] if len(sys.argv) > 1 else "__ORCH__"
    for batch, name in NOTEBOOKS.items():
        (HERE / name).write_text(json.dumps(build(batch, orch), indent=1) + "\n", encoding="utf-8")
        print("wrote", HERE / name)
