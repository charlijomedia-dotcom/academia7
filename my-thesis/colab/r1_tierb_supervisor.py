#!/usr/bin/env python3
"""R1 Tier B supervisor for ONE batch: workers, verified checkpoints, budget, final commit.

* Holds a lease on the batch's Drive namespace (one active session per batch).
* Launches up to --max-workers worker processes, one per unfinished chain of the batch,
  longest first; each warm-started chain stays in a single process (never split).
  Each worker writes only to its own chain folder on the VM's local disk; workers use
  single-threaded BLAS, as in the original parallel runner.
* Every --backup-minutes, commits each chain's new payloads as a verified checkpoint
  in the batch's own Drive namespace (r1_tierb.commit_checkpoint). A failed Drive write
  stops the session: workers are told to stop and the supervisor exits non-zero.
* Stops scheduling when the runtime budget is nearly used; running workers stop between
  origins (r1_tierb.StoppableRefitCache). Then a final commit, then a verification that
  Drive holds exactly the local payloads, then a session summary.

Exit status: 0 = every chain of the batch complete and committed; 3 = stopped by the
budget with work remaining (resume in a new runtime); 2 = an error (nothing is assumed).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r1_tierb as tb  # noqa: E402

BLAS_SINGLE_THREAD = {name: "1" for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                                              "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
                                              "NUMEXPR_NUM_THREADS")}


def log(path: Path, message: str) -> None:
    line = f"[{tb.utc_stamp()}] {message}"
    print(line, flush=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def commit_all(args, tasks, root: Path, logfile: Path, session_info: dict) -> dict:
    committed = {}
    for task in tasks:
        local = args.work / "chains" / tb.slug(task) / "fits"
        if not local.exists():
            continue
        task_dir = tb.assert_writable_path(root / "checkpoints" / tb.slug(task),
                                           args.drive_root, args.batch)
        manifest = tb.commit_checkpoint(local, task_dir, task=task, session=args.session,
                                        extra={"session_record": session_info})
        if manifest:
            committed[task] = manifest["checkpoint_id"]
            log(logfile, f"committed {manifest['checkpoint_id']} ({len(manifest['members'])} "
                         f"new, {manifest['cumulative_payloads']} total) for {task}")
    return committed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--batch", required=True, choices=sorted(tb.BATCHES))
    parser.add_argument("--python", required=True)
    parser.add_argument("--code-dir", type=Path, required=True)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--drive-root", type=Path, required=True)
    parser.add_argument("--session", required=True)
    parser.add_argument("--start-epoch", type=float, required=True)
    parser.add_argument("--budget-hours", type=float, required=True)
    parser.add_argument("--reserve-minutes", type=float, default=30.0)
    parser.add_argument("--backup-minutes", type=float, default=10.0)
    parser.add_argument("--max-workers", type=int, required=True)
    parser.add_argument("--skip-complete", type=Path, default=None,
                        help="preflight report: chains already complete are not launched")
    parser.add_argument("--poll-seconds", type=float, default=15.0)
    parser.add_argument("--provenance", type=Path, default=None,
                        help="provenance.json written by the notebook's preflight cell")
    args = parser.parse_args(argv)

    tasks = list(tb.batch_tasks(args.batch))
    root = tb.batch_root(args.drive_root, args.batch)
    session_dir = tb.assert_writable_path(root / "sessions" / f"{tb.utc_stamp()}-{args.session}",
                                          args.drive_root, args.batch)
    local_logs = args.work / "logs"
    local_logs.mkdir(parents=True, exist_ok=True)
    logfile = local_logs / "supervisor.log"
    stop_file = args.work / "STOP"
    if stop_file.exists():
        stop_file.unlink()
    budget = tb.Budget(args.start_epoch, args.budget_hours, args.reserve_minutes)
    lease = tb.acquire_lease(root, args.session)   # refused: nothing of this session written
    session_dir.mkdir(parents=True, exist_ok=False)
    started = time.time()
    provenance = (json.loads(args.provenance.read_text(encoding="utf-8"))
                  if args.provenance and args.provenance.exists() else {})
    # Written first, so a session that is hard-killed before any summary is still on
    # record; every checkpoint manifest of this session repeats it (traceable from the
    # checkpoints alone, even if this folder were lost).
    session_info = {"batch": args.batch, "session": args.session,
                    "session_dir": session_dir.name, "started_utc": tb.utc_stamp(),
                    "vm_start_epoch": args.start_epoch, "budget_hours": args.budget_hours,
                    "max_workers": args.max_workers, "host": os.uname().nodename,
                    "scientific_commit": provenance.get("scientific_commit"),
                    "orchestration_commit": provenance.get("orchestration_commit"),
                    "cache_identity": provenance.get("cache_identity")}
    tb.write_json_atomic(session_dir / tb.SESSION_START, session_info)
    summary = {"batch": args.batch, "session": args.session, "started_utc": tb.utc_stamp(),
               "budget_hours": args.budget_hours, "vm_start_epoch": args.start_epoch,
               "outcomes": {}, "estimations": {}, "commits": [], "error": None}
    pending = list(tasks)
    if args.skip_complete and args.skip_complete.exists():
        done = json.loads(args.skip_complete.read_text(encoding="utf-8"))["batch_chains"]
        pending = [t for t in tasks if not done.get(t, {}).get("complete")]
        for t in tasks:
            if t not in pending:
                summary["outcomes"][t] = "complete (already committed)"
    running: dict[str, subprocess.Popen] = {}
    env = dict(os.environ, **BLAS_SINGLE_THREAD, PYTHONUNBUFFERED="1", MPLBACKEND="Agg")
    env.pop("THESIS_GIT_TOKEN", None)
    last_backup = time.time()
    exit_code = 0
    try:
        while pending or running:
            # launch while there are free workers and time for at least one origin
            while pending and len(running) < args.max_workers:
                task = pending[0]
                expected = 3.0 * tb.TIER_B_CHAINS[task][1] + 600.0   # + job building
                if not budget.can_start(expected):
                    log(logfile, f"budget: not starting {pending}")
                    for t in pending:
                        summary["outcomes"][t] = "not started (budget)"
                    pending = []
                    break
                pending.pop(0)
                chain_dir = args.work / "chains" / tb.slug(task)
                chain_dir.mkdir(parents=True, exist_ok=True)
                command = [args.python, "-u", str(Path(__file__).with_name("r1_tierb_worker.py")),
                           "run", "--batch", args.batch, "--task", task,
                           "--code-dir", str(args.code_dir), "--original", str(args.original),
                           "--batch-fits", str(args.work / "chains"),
                           "--start-epoch", str(args.start_epoch),
                           "--budget-hours", str(args.budget_hours),
                           "--reserve-minutes", str(args.reserve_minutes),
                           "--stop-file", str(stop_file),
                           "--result", str(chain_dir / f"result-{args.session}.json")]
                handle = open(local_logs / f"{tb.slug(task)}.log", "a", encoding="utf-8")
                running[task] = subprocess.Popen(command, stdout=handle, stderr=subprocess.STDOUT,
                                                 env=env, cwd=str(args.work))
                log(logfile, f"started {task} (pid {running[task].pid})")
            time.sleep(args.poll_seconds)
            for task, process in list(running.items()):
                code = process.poll()
                if code is None:
                    continue
                running.pop(task)
                result_file = args.work / "chains" / tb.slug(task) / f"result-{args.session}.json"
                result = json.loads(result_file.read_text()) if result_file.exists() else {}
                summary["outcomes"][task] = {0: "complete", 3: "stopped (budget)"}.get(code, f"error {code}")
                if result.get("estimations"):
                    summary["estimations"][task] = result["estimations"]
                log(logfile, f"{task} finished: {summary['outcomes'][task]} "
                             f"{result.get('walk', {}).get('completed')}/"
                             f"{result.get('walk', {}).get('planned')}")
                if code not in (0, 3):
                    raise tb.TierBError(f"worker for {task} failed with exit {code}")
            if time.time() - last_backup >= args.backup_minutes * 60:
                summary["commits"].append(commit_all(args, tasks, root, logfile, session_info))
                tb.heartbeat(lease)
                tb.write_json_atomic(session_dir / "progress.json",
                                     {**summary, "running": sorted(running),
                                      "pending": pending,
                                      "budget_remaining_hours": budget.remaining() / 3600})
                last_backup = time.time()
    except Exception as error:                     # noqa: BLE001 - report, stop, fail
        summary["error"] = f"{type(error).__name__}: {error}"
        log(logfile, f"ERROR {summary['error']}; telling workers to stop")
        stop_file.write_text("supervisor error")
        for process in running.values():
            try:
                process.wait(timeout=6 * 3600)
            except subprocess.TimeoutExpired:
                process.terminate()
        exit_code = 2
    # final commit and verification: Drive must hold exactly the local payloads
    try:
        summary["commits"].append(commit_all(args, tasks, root, logfile, session_info))
        for task in tasks:
            local = args.work / "chains" / tb.slug(task) / "fits"
            if not local.exists():
                continue
            drive = tb.committed_inventory(root / "checkpoints" / tb.slug(task))
            if drive != tb.inventory(local):
                raise tb.TierBError(f"{task}: Drive checkpoints do not match local payloads")
        summary["final_verification"] = "Drive checkpoints equal local payloads"
    except Exception as error:                     # noqa: BLE001
        summary["error"] = (summary["error"] or "") + f" | final commit: {error}"
        summary["final_verification"] = "FAILED"
        exit_code = 2
    if exit_code == 0 and any(v != "complete" and not str(v).startswith("complete")
                              for v in summary["outcomes"].values()):
        exit_code = 3
    summary.update(finished_utc=tb.utc_stamp(),
                   elapsed_hours=round((time.time() - started) / 3600, 3),
                   vm_elapsed_hours=round((time.time() - args.start_epoch) / 3600, 3),
                   exit_code=exit_code)
    tb.write_json_atomic(session_dir / "session_summary.json", summary)
    for item in local_logs.glob("*.log"):
        target = session_dir / "logs" / item.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(item.read_bytes())
    tb.release_lease(lease)
    log(logfile, f"session finished with exit {exit_code}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
