"""Support code for running the thesis pipeline on Google Colab.

Standard library only, so it runs under Colab's own Python before the pinned
environment exists. The notebook `run_thesis_colab.ipynb` calls these functions; they
live here so they can be tested outside Colab.

Nothing here touches a calculation. It prepares an isolated Python 3.11 environment
from the approved lock, starts `code/run_all.py`, streams its console, backs up new
files incrementally to Google Drive, restores a compatible fit cache after a runtime
loss, verifies the finished outputs against the run's own inventory, and can push the
results to a dedicated branch with a token read from a Colab secret.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path
from typing import Iterable

LOCK_LINE = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s*==\s*([^\s#;]+)")
STAGES = ["canonical_input", "stationarity_decisions", "selected_specifications",
          "nonlinearity_diagnostics", "selected_specifications", "model_fits", "forecasts",
          "evaluation", "robustness", "tables_and_figures"]
GITHUB_FILE_LIMIT = 95 * 1024 * 1024        # GitHub refuses files over 100 MB


def sh(command: list[str], *, cwd: Path | None = None, env: dict | None = None,
       check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a command, echoing it (never echo a secret: none is ever on a command line)."""
    print("$", " ".join(command), flush=True)
    return subprocess.run(command, cwd=cwd, env=env, check=check, text=True,
                          capture_output=capture)


# -- 1. isolated Python 3.11 environment ---------------------------------------------

def lock_pins(lock: Path) -> dict[str, str]:
    pins = {}
    for line in Path(lock).read_text(encoding="utf-8").splitlines():
        match = LOCK_LINE.match(line)
        if match:
            pins[match.group(1).lower().replace("_", "-")] = match.group(2)
    return pins


def create_environment(venv: Path, lock: Path, *, python_version: str = "3.11",
                       constraints: Path | None = None) -> Path:
    """A fresh virtual environment on Python 3.11 with exactly the locked versions.

    `uv` provides a standalone CPython 3.11 independent of Colab's system Python, so the
    run does not depend on whichever Python the Colab image currently ships. With
    `constraints`, the packages the lock does not name (its transitive dependencies) are
    held at the validated versions too.
    """
    venv = Path(venv)
    sh([sys.executable, "-m", "pip", "install", "-q", "uv"])
    uv = [sys.executable, "-m", "uv"]
    sh(uv + ["python", "install", python_version])
    if venv.exists():
        shutil.rmtree(venv)
    sh(uv + ["venv", "--python", python_version, str(venv)])
    python = venv / "bin" / "python"
    command = uv + ["pip", "install", "--python", str(python), "-r", str(lock)]
    if constraints is not None:
        command += ["-c", str(constraints)]
    sh(command)
    return python


def verify_environment(python: Path, lock: Path, *, python_version: str = "3.11",
                       constraints: Path | None = None) -> dict:
    """Check the interpreter version and every pinned package version exactly."""
    pins = lock_pins(lock)
    if constraints is not None:
        pins.update(lock_pins(constraints))
    probe = ("import json, sys, importlib.metadata as m\n"
             "names = json.loads(sys.argv[1])\n"
             "out = {'python': '%d.%d.%d' % sys.version_info[:3], 'packages': {}}\n"
             "for n in names:\n"
             "    try: out['packages'][n] = m.version(n)\n"
             "    except m.PackageNotFoundError: out['packages'][n] = None\n"
             "print(json.dumps(out))\n")
    result = subprocess.run([str(python), "-c", probe, json.dumps(sorted(pins))],
                            check=True, text=True, capture_output=True)
    found = json.loads(result.stdout)
    problems = []
    if not found["python"].startswith(python_version + "."):
        problems.append(f"python {found['python']} is not {python_version}")
    for name, wanted in sorted(pins.items()):
        have = found["packages"].get(name)
        if have != wanted:
            problems.append(f"{name}: installed {have}, locked {wanted}")
    if problems:
        raise RuntimeError("environment does not match the lock:\n  " + "\n  ".join(problems))
    return found


# -- 2. git without credentials in any URL ---------------------------------------------

def askpass_environment(token: str | None, directory: Path) -> dict[str, str]:
    """Environment for git that answers HTTPS prompts from an environment variable.

    The token lives only in this process environment and is read by a helper script
    that contains no secret itself. It never appears in a remote URL, in .git/config,
    on a command line or in the notebook source.
    """
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    if not token:
        return env
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    script = directory / "git_askpass.sh"
    script.write_text('#!/bin/sh\ncase "$1" in\n  Username*) echo "x-access-token" ;;\n'
                      '  *) echo "$THESIS_GIT_TOKEN" ;;\nesac\n', encoding="utf-8")
    script.chmod(stat.S_IRWXU)
    env["GIT_ASKPASS"] = str(script)
    env["THESIS_GIT_TOKEN"] = token
    return env


def assert_no_credentials(url: str) -> None:
    if re.match(r"^https?://[^/]*@", url):
        raise ValueError("refusing a remote URL that embeds credentials")


def clone_or_update(repository: str, branch: str, destination: Path, env: dict) -> str:
    url = f"https://github.com/{repository}.git"
    assert_no_credentials(url)
    destination = Path(destination)
    if not (destination / ".git").exists():
        sh(["git", "clone", "--branch", branch, url, str(destination)], env=env)
    else:
        sh(["git", "fetch", "origin", branch], cwd=destination, env=env)
        sh(["git", "checkout", branch], cwd=destination, env=env)
        sh(["git", "merge", "--ff-only", f"origin/{branch}"], cwd=destination, env=env)
    return sh(["git", "rev-parse", "HEAD"], cwd=destination, capture=True).stdout.strip()


# -- 3. which cached fits are compatible -------------------------------------------------

def cache_identity(python: Path, code_dir: Path, namespace: str = "baseline") -> str:
    """Code hash, configuration hash and data hash: the parts of every cache key that
    are fixed for a run. A cache backed up under another identity is never restored."""
    names = '("baseline", "series_catalog", "thresholds")' if namespace == "baseline" \
        else '("baseline", "series_catalog", "thresholds", "smoke")'
    program = (
        "import sys, json, hashlib\n"
        "sys.path.insert(0, 'src')\n"
        "from thesis.core.cache import code_hash\n"
        "from thesis.core.config import load_config\n"
        "from thesis.core.paths import CONFIG_DIR, FROZEN_DIR\n"
        "from thesis.core.hashing import sha256_file\n"
        f"config = load_config(names={names}, config_dir=CONFIG_DIR)\n"
        "csv = FROZEN_DIR / 'thesis_input_2026-10-05.csv'\n"
        "parts = {'code': code_hash(), 'config': config.hash, 'data': sha256_file(csv)}\n"
        "print(hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:16])\n")
    return subprocess.run([str(python), "-c", program], cwd=code_dir, check=True,
                          text=True, capture_output=True).stdout.strip()


# -- 4. incremental backups to Drive ------------------------------------------------------

class IncrementalArchive:
    """Back up a directory to `destination` as a growing series of compressed parts.

    Each sync packs only the files that are new or changed since the last part into one
    `part-NNNNN.tar.gz`, plus a small `part-NNNNN.json` listing them. Drive therefore
    receives one archive per sync rather than thousands of small files, and nothing
    unchanged is copied twice. Parts are written under a temporary name and renamed, so
    a backup interrupted mid-copy is never mistaken for a complete one. Files still
    being written (`*.tmp`) are skipped. `restore` extracts the parts in order.
    """

    def __init__(self, source: Path, destination: Path, *, skip_suffixes=(".tmp",)):
        self.source = Path(source)
        self.destination = Path(destination)
        self.skip_suffixes = tuple(skip_suffixes)
        self.known: dict[str, list[int]] = {}
        self._load_lists()

    def _parts(self) -> list[Path]:
        if not self.destination.exists():
            return []
        return sorted(self.destination.glob("part-*.tar.gz"))

    def _load_lists(self) -> None:
        for part in self._parts():
            listing = part.with_name(part.name.replace(".tar.gz", ".json"))
            if listing.exists():
                self.known.update(json.loads(listing.read_text(encoding="utf-8")))

    def pending(self) -> dict[str, list[int]]:
        changed = {}
        if not self.source.exists():
            return changed
        for path in self.source.rglob("*"):
            if not path.is_file() or path.name.endswith(self.skip_suffixes):
                continue
            info = path.stat()
            relative = path.relative_to(self.source).as_posix()
            signature = [info.st_size, info.st_mtime_ns]
            if self.known.get(relative) != signature:
                changed[relative] = signature
        return changed

    def sync(self) -> Path | None:
        changed = self.pending()
        if not changed:
            return None
        self.destination.mkdir(parents=True, exist_ok=True)
        number = len(self._parts()) + 1
        name = f"part-{number:05d}"
        with tempfile.TemporaryDirectory() as scratch:
            local = Path(scratch) / f"{name}.tar.gz"
            with tarfile.open(local, "w:gz") as archive:
                for relative in sorted(changed):
                    archive.add(self.source / relative, arcname=relative)
            target = self.destination / f"{name}.tar.gz"
            shutil.copyfile(local, target.with_name(target.name + ".partial"))
            os.replace(target.with_name(target.name + ".partial"), target)
        listing = self.destination / f"{name}.json"
        listing.with_name(listing.name + ".partial").write_text(json.dumps(changed),
                                                                 encoding="utf-8")
        os.replace(listing.with_name(listing.name + ".partial"), listing)
        self.known.update(changed)
        return target

    def restore(self, target: Path | None = None) -> int:
        target = Path(target) if target is not None else self.source
        target.mkdir(parents=True, exist_ok=True)
        count = 0
        root = target.resolve()
        for part in self._parts():
            with tarfile.open(part, "r:gz") as archive:
                members = archive.getmembers()
                for member in members:
                    destination = (target / member.name).resolve()
                    if not member.isfile() or root not in destination.parents:
                        raise ValueError(f"unsafe member {member.name!r} in {part.name}")
                archive.extractall(target, members=members)
                count += len(members)
        # What was restored is already backed up: record it so it is not uploaded again.
        if target == self.source:
            for path in self.source.rglob("*"):
                if path.is_file():
                    relative = path.relative_to(self.source).as_posix()
                    if relative in self.known:
                        info = path.stat()
                        self.known[relative] = [info.st_size, info.st_mtime_ns]
        return count


def backup_daemon(pid: int, pairs: list[tuple[Path, Path]], interval: float,
                  log: Path | None = None) -> None:
    """Sync every (source, destination) pair every `interval` seconds while `pid` lives,
    then once more after it exits, so the last fits and outputs are not lost."""
    archives = [IncrementalArchive(source, destination) for source, destination in pairs]

    def note(message: str) -> None:
        line = f"[{time.strftime('%H:%M:%S', time.gmtime())}] backup: {message}"
        print(line, flush=True)
        if log is not None:
            with open(log, "a", encoding="utf-8") as handle:
                handle.write(line + "\n")

    def sync_all() -> None:
        for archive in archives:
            try:
                written = archive.sync()
                if written is not None:
                    note(f"{archive.source.name}: wrote {written.name} "
                         f"({written.stat().st_size / 1e6:.1f} MB)")
            except Exception as exc:                     # a backup never stops the run
                note(f"{archive.source} failed: {exc!r}")

    while process_alive(pid):
        deadline = time.time() + interval
        while time.time() < deadline and process_alive(pid):
            time.sleep(min(5.0, interval))
        sync_all()
    sync_all()
    note("final sync complete")


# -- 5. starting and watching the run ---------------------------------------------------

def process_alive(pid: int) -> bool:
    try:
        os.kill(int(pid), 0)
    except (OSError, ValueError):
        return False
    try:                                    # a zombie is finished, not alive
        with open(f"/proc/{int(pid)}/stat", encoding="utf-8") as handle:
            return handle.read().split()[2] != "Z"
    except OSError:
        return True


def launch_background(command: list[str], *, cwd: Path, console: Path, exit_file: Path,
                      pid_file: Path, env: dict | None = None) -> int:
    """Start `command` detached (it survives a notebook disconnect); record pid and exit."""
    if pid_file.exists() and process_alive(int(pid_file.read_text().strip() or 0)):
        pid = int(pid_file.read_text().strip())
        print(f"already running (pid {pid}); not starting a second copy")
        return pid
    exit_file.unlink(missing_ok=True)
    quoted = " ".join(_quote(part) for part in command)
    script = f"{quoted} > {_quote(str(console))} 2>&1; echo $? > {_quote(str(exit_file))}"
    process = subprocess.Popen(["nohup", "sh", "-c", script], cwd=cwd, env=env,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               start_new_session=True)
    pid_file.write_text(str(process.pid))
    return process.pid


def _quote(text: str) -> str:
    return "'" + text.replace("'", "'\"'\"'") + "'"


def watch(console: Path, pid_file: Path, exit_file: Path, *, poll: float = 5.0,
          snapshot_root: Path | None = None, snapshot_every: float = 300.0,
          out=sys.stdout) -> int | None:
    """Stream the console as it grows until the run exits; return its exit status.

    Interrupting this stops the watching, not the run; call it again to reattach (it
    starts from the beginning of the log).
    """
    offset, last_snapshot = 0, 0.0
    pid = int(pid_file.read_text().strip()) if pid_file.exists() else -1
    while True:
        if console.exists():
            with open(console, "r", encoding="utf-8", errors="replace") as handle:
                handle.seek(offset)
                chunk = handle.read()
                offset = handle.tell()
            if chunk:
                out.write(chunk)
                out.flush()
        if snapshot_root is not None and time.time() - last_snapshot > snapshot_every:
            last_snapshot = time.time()
            snapshot = latest_snapshot(snapshot_root)
            if snapshot:
                stage = snapshot.get("current_stage") or {}
                out.write(f"\n[snapshot {snapshot.get('updated_utc')}] status="
                          f"{snapshot.get('status')} stage={stage.get('number')}/10 "
                          f"remaining origins={snapshot['origins']['all']['remaining']}\n")
                out.flush()
        if exit_file.exists() and exit_file.read_text().strip():
            time.sleep(0.5)
            continue_reading = console.exists() and console.stat().st_size > offset
            if not continue_reading:
                return int(exit_file.read_text().strip())
        elif not process_alive(pid):
            return None
        time.sleep(poll)


def latest_snapshot(root: Path) -> dict | None:
    pointer = Path(root) / "LATEST"
    if not pointer.exists():
        return None
    try:
        return json.loads((Path(root) / pointer.read_text().strip() / "progress.json")
                          .read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


# -- 6. verification and publication --------------------------------------------------------

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_outputs(project: Path, *, namespace: str = "baseline") -> dict:
    """Check a finished run's outputs before anything is published.

    * every file in the output inventory exists with the checksum recorded at write time;
    * the run summary lists all ten stages;
    * the run's progress snapshot says `complete`;
    * the working tree has no change outside the output directory, so the commit the
      outputs record is the code that produced them.
    """
    project = Path(project)
    output = project / ("output" if namespace == "baseline" else "smoke_output")
    problems: list[str] = []
    inventory = output / "manifests" / "output_inventory.csv"
    checked = 0
    if not inventory.exists():
        problems.append("output inventory missing")
    else:
        import csv
        with open(inventory, encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                path = output / row["path"]
                if not path.exists():
                    problems.append(f"missing: {row['path']}")
                elif row.get("sha256") and sha256(path) != row["sha256"]:
                    problems.append(f"checksum differs: {row['path']}")
                checked += 1
    summary_path = output / "manifests" / "run_summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    if summary.get("stages") != STAGES:
        problems.append(f"run summary stages are {summary.get('stages')}")
    snapshot = latest_snapshot(project / "run_logs" / namespace)
    if snapshot is None or snapshot.get("status") != "complete":
        problems.append("progress snapshot does not say complete")
    status = subprocess.run(["git", "status", "--porcelain"], cwd=project, text=True,
                            capture_output=True).stdout.splitlines()
    outside = [line for line in status
               if not line[3:].lstrip('"').startswith(
                   (f"{output.name}/", f"my-thesis/{output.name}/"))]
    if outside:
        problems.append("working tree changed outside the outputs: " + "; ".join(outside[:5]))
    return {"ok": not problems, "problems": problems, "files_checked": checked,
            "run_id": summary.get("run_id")}


def large_files(directory: Path, limit: int | None = None) -> list[str]:
    limit = GITHUB_FILE_LIMIT if limit is None else limit
    return [p.relative_to(directory).as_posix() for p in Path(directory).rglob("*")
            if p.is_file() and p.stat().st_size > limit]


def push_results(repo_root: Path, project: Path, branch: str, env: dict, *,
                 message: str, author: tuple[str, str]) -> str:
    """Commit the thesis-facing outputs to a new branch and push it.

    Authentication comes from `env` (see `askpass_environment`); the remote URL is
    checked to carry no credentials before anything is pushed.
    """
    repo_root, project = Path(repo_root), Path(project)
    url = sh(["git", "remote", "get-url", "origin"], cwd=repo_root, capture=True).stdout.strip()
    assert_no_credentials(url)
    output = project / "output"
    too_big = large_files(output)
    if too_big:
        raise RuntimeError(f"files over GitHub's size limit, not pushed: {too_big}")
    relative = output.relative_to(repo_root).as_posix()
    sh(["git", "checkout", "-B", branch], cwd=repo_root)
    sh(["git", "add", "--", relative], cwd=repo_root)
    sh(["git", "-c", f"user.name={author[0]}", "-c", f"user.email={author[1]}",
        "commit", "-q", "-m", message], cwd=repo_root)
    sh(["git", "push", "-u", "origin", branch], cwd=repo_root, env=env)
    return sh(["git", "rev-parse", "HEAD"], cwd=repo_root, capture=True).stdout.strip()


# -- command line (used for the background backup process) --------------------------------

def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    daemon = sub.add_parser("backup-daemon")
    daemon.add_argument("--pid", type=int, required=True)
    daemon.add_argument("--interval", type=float, default=600.0)
    daemon.add_argument("--pair", nargs=2, action="append", metavar=("SOURCE", "DEST"),
                        required=True)
    daemon.add_argument("--log", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command == "backup-daemon":
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        backup_daemon(args.pid, [(Path(s), Path(d)) for s, d in args.pair], args.interval,
                      args.log)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
