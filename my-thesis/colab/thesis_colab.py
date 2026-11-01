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

    def __init__(self, source: Path, destination: Path, *, skip_suffixes=(".tmp",),
                 by_name: bool = False, also_known: Iterable[Path] = (),
                 max_files_per_part: int | None = None):
        """`by_name=True` is for content-addressed, write-once trees such as the fit cache:
        a file already listed in any part is never uploaded again, whatever its mtime. A
        restored file's mtime cannot match the one recorded at backup time (tar keeps
        less precision than `st_mtime_ns`), so the signature test would re-upload the
        whole restored cache in one huge part (Part 8 cache audit, 2 November 2026).
        `also_known` adds other archive folders whose listings count as already backed up
        (a recovery archive next to the original). `max_files_per_part` bounds each part,
        so a sync is a series of small copies, each logged, rather than one large copy.
        """
        self.source = Path(source)
        self.destination = Path(destination)
        self.skip_suffixes = tuple(skip_suffixes)
        self.by_name = by_name
        self.max_files_per_part = max_files_per_part
        self.known: dict[str, list[int]] = {}
        for folder in also_known:
            self._load_lists(Path(folder))
        self._load_lists()

    def _parts(self, folder: Path | None = None) -> list[Path]:
        folder = self.destination if folder is None else folder
        if not folder.exists():
            return []
        return sorted(folder.glob("part-*.tar.gz"))

    def _load_lists(self, folder: Path | None = None) -> None:
        for part in self._parts(folder):
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
            if self.by_name:
                if relative not in self.known:
                    changed[relative] = signature
            elif self.known.get(relative) != signature:
                changed[relative] = signature
        return changed

    def sync(self, note=None) -> Path | None:
        """Write the pending files as one or more new parts; return the last part.

        Existing parts are never modified. With `max_files_per_part`, the pending files
        are written in bounded chunks, each copied and renamed before the next starts,
        and `note` (if given) is called before and after every copy, so a stalled copy
        is visible in the log instead of silent.
        """
        changed = self.pending()
        if not changed:
            return None
        self.destination.mkdir(parents=True, exist_ok=True)
        names = sorted(changed)
        size = self.max_files_per_part or len(names)
        last = None
        for start in range(0, len(names), size):
            chunk = {name: changed[name] for name in names[start:start + size]}
            number = len(self._parts()) + 1
            name = f"part-{number:05d}"
            if note is not None:
                note(f"{self.source.name}: writing {name} ({len(chunk)} files; "
                     f"{len(names) - start} pending)")
            with tempfile.TemporaryDirectory() as scratch:
                local = Path(scratch) / f"{name}.tar.gz"
                with tarfile.open(local, "w:gz") as archive:
                    for relative in sorted(chunk):
                        archive.add(self.source / relative, arcname=relative)
                target = self.destination / f"{name}.tar.gz"
                shutil.copyfile(local, target.with_name(target.name + ".partial"))
                os.replace(target.with_name(target.name + ".partial"), target)
            listing = self.destination / f"{name}.json"
            listing.with_name(listing.name + ".partial").write_text(json.dumps(chunk),
                                                                     encoding="utf-8")
            os.replace(listing.with_name(listing.name + ".partial"), listing)
            self.known.update(chunk)
            last = target
        return last

    def restore(self, target: Path | None = None, *, folder: Path | None = None) -> int:
        """Extract every part of `folder` (default: the destination) into `target`."""
        target = Path(target) if target is not None else self.source
        target.mkdir(parents=True, exist_ok=True)
        count = 0
        root = target.resolve()
        for part in self._parts(folder):
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
                  log: Path | None = None, *, by_name_pairs: list[tuple[Path, Path]] = (),
                  also_known: Iterable[Path] = (), max_files_per_part: int | None = 2000
                  ) -> None:
    """Sync every (source, destination) pair every `interval` seconds while `pid` lives,
    then once more after it exits, so the last fits and outputs are not lost.

    `by_name_pairs` are content-addressed trees (the fit cache): archived by file name,
    with `also_known` archive folders counted as already backed up. Every sync logs its
    start, each part it writes and any failure, and a heartbeat line is written when a
    sync finds nothing new, so the log shows the daemon is alive.
    """
    archives = [IncrementalArchive(source, destination, max_files_per_part=max_files_per_part)
                for source, destination in pairs]
    archives += [IncrementalArchive(source, destination, by_name=True,
                                    also_known=also_known,
                                    max_files_per_part=max_files_per_part)
                 for source, destination in by_name_pairs]

    def note(message: str) -> None:
        line = f"[{time.strftime('%H:%M:%S', time.gmtime())}] backup: {message}"
        print(line, flush=True)
        if log is not None:
            with open(log, "a", encoding="utf-8") as handle:
                handle.write(line + "\n")

    def sync_all() -> None:
        for archive in archives:
            try:
                written = archive.sync(note=note)
                if written is not None:
                    note(f"{archive.source.name}: wrote up to {written.name} "
                         f"({len(archive.known)} files known in total)")
                else:
                    note(f"{archive.source.name}: nothing new ({len(archive.known)} known)")
            except Exception as exc:                     # a backup never stops the run
                note(f"{archive.source} failed: {exc!r}")

    note(f"daemon started for pid {pid}; interval {interval:.0f} s; "
         f"{sum(len(a.known) for a in archives)} files already archived")
    while process_alive(pid):
        deadline = time.time() + interval
        while time.time() < deadline and process_alive(pid):
            time.sleep(min(5.0, interval))
        sync_all()
    sync_all()
    note("final sync complete")


# -- 4b. cache audit and recovery (Part 8 correction phase) -----------------------------

def clean_drive_root(value: str) -> str:
    """A Drive folder typed into a Colab form, without stray quotes or whitespace.

    A form field pasted as `"/content/drive/..."` would otherwise carry the quotation marks
    into the path and silently create a new folder. Only absolute paths under
    /content/drive are accepted.
    """
    text = str(value).strip().strip('"').strip("'").strip()
    if not text.startswith("/content/drive/"):
        raise ValueError(f"DRIVE_ROOT must be an absolute path under /content/drive/: {value!r}")
    return text.rstrip("/")


def archive_folders(drive: Path, identity: str) -> list[Path]:
    """Every archive folder holding fits for `identity`: the main one, then recoveries."""
    folders = [drive / "fit_cache" / identity]
    recovered = drive / "fit_cache_recovered"
    if recovered.exists():
        folders += sorted(p / identity for p in recovered.iterdir() if (p / identity).is_dir())
    return folders


def archive_summary(folder: Path) -> dict:
    """Read-only summary of one archive folder: parts, listed files, times, leftovers."""
    parts = sorted(folder.glob("part-*.tar.gz")) if folder.exists() else []
    names: set[str] = set()
    missing_lists = []
    for part in parts:
        listing = part.with_name(part.name.replace(".tar.gz", ".json"))
        if listing.exists():
            names.update(json.loads(listing.read_text(encoding="utf-8")))
        else:
            missing_lists.append(part.name)
    stamps = [p.stat().st_mtime for p in parts]
    return {
        "folder": str(folder),
        "parts": len(parts),
        "unique_files_listed": len(names),
        "first_part_utc": (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(min(stamps)))
                           if stamps else None),
        "last_part_utc": (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(max(stamps)))
                          if stamps else None),
        "parts_without_listing": missing_lists,
        "partial_leftovers": sorted(p.name for p in folder.glob("*.partial"))
        if folder.exists() else [],
        "bytes": sum(p.stat().st_size for p in parts),
    }


def audit_drive(roots: Iterable[Path], namespace: str = "baseline") -> dict:
    """Read-only inventory of candidate Drive backup roots (nothing is written).

    For each root: every fit-cache identity with its part count, unique listed files,
    part time range and any `.partial` leftover (an interrupted copy); recovered
    archives; the last lines of `backup.log`; the run folders under `results/`; and the
    output-increment folders. Together these say which session backed up what, and
    when, and the union of listed names is the number of unique fit payloads that can be
    restored.
    """
    report = {}
    for root in roots:
        base = Path(root) / namespace
        entry: dict = {"exists": base.exists()}
        if base.exists():
            caches = {}
            union: set[str] = set()
            for folder in sorted((base / "fit_cache").glob("*")) if (base / "fit_cache").exists() else []:
                caches[folder.name] = archive_summary(folder)
            recovered = base / "fit_cache_recovered"
            recoveries = {}
            if recovered.exists():
                for stamp in sorted(recovered.iterdir()):
                    for folder in sorted(stamp.glob("*")):
                        recoveries[f"{stamp.name}/{folder.name}"] = archive_summary(folder)
            for identity in {c for c in caches} | {k.split("/")[1] for k in recoveries}:
                for folder in archive_folders(base, identity):
                    for part in sorted(folder.glob("part-*.tar.gz")):
                        listing = part.with_name(part.name.replace(".tar.gz", ".json"))
                        if listing.exists():
                            union.update(f"{identity}:{n}" for n in
                                         json.loads(listing.read_text(encoding="utf-8")))
            log = base / "backup.log"
            entry.update(
                fit_cache=caches, fit_cache_recovered=recoveries,
                unique_fit_payloads_by_identity={
                    identity: sum(1 for n in union if n.startswith(identity + ":"))
                    for identity in {n.split(":", 1)[0] for n in union}},
                backup_log_tail=(log.read_text(encoding="utf-8").splitlines()[-15:]
                                 if log.exists() else None),
                results_runs=sorted(p.name for p in (base / "results").glob("*"))
                if (base / "results").exists() else [],
                output_increments={p.name: archive_summary(p)
                                   for p in sorted((base / "output_increments").glob("*"))}
                if (base / "output_increments").exists() else {},
            )
        report[str(root)] = entry
    return report


def recover_local_cache(cache_dir: Path, drive: Path, identity: str, *,
                        stamp: str | None = None, max_files_per_part: int = 2000) -> dict:
    """Back up a VM's local fit cache to a NEW recovery folder, never touching old parts.

    Only files not already listed in any existing archive folder for `identity` are
    written, to `<drive>/fit_cache_recovered/<stamp>/<identity>/`. Each part is then read
    back from Drive and every member's SHA-256 is compared with the local file, so the
    recovery is verified rather than assumed. Returns a summary for the record.
    """
    stamp = stamp or time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    destination = drive / "fit_cache_recovered" / stamp / identity
    existing = [f for f in archive_folders(drive, identity) if f != destination]
    archive = IncrementalArchive(cache_dir, destination, by_name=True, also_known=existing,
                                 max_files_per_part=max_files_per_part)
    pending = archive.pending()
    before = len(archive.known)
    archive.sync()
    verified, mismatched = 0, []
    for part in archive._parts():
        with tarfile.open(part, "r:gz") as tar:
            for member in tar.getmembers():
                if not member.isfile():
                    continue
                data = tar.extractfile(member).read()
                local = (Path(cache_dir) / member.name).read_bytes()
                if hashlib.sha256(data).digest() == hashlib.sha256(local).digest():
                    verified += 1
                else:
                    mismatched.append(member.name)
    return {"destination": str(destination), "already_archived": before,
            "newly_archived": len(pending), "verified": verified, "mismatched": mismatched,
            "local_files": sum(1 for p in Path(cache_dir).rglob("*.json"))}


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
                        default=[])
    daemon.add_argument("--pair-by-name", nargs=2, action="append", metavar=("SOURCE", "DEST"),
                        default=[], help="content-addressed tree (the fit cache)")
    daemon.add_argument("--also-known", action="append", type=Path, default=[],
                        help="other archive folders whose files count as backed up")
    daemon.add_argument("--max-files-per-part", type=int, default=2000)
    daemon.add_argument("--log", type=Path)
    audit = sub.add_parser("audit-drive", help="read-only inventory of Drive backup roots")
    audit.add_argument("roots", nargs="+", type=Path)
    audit.add_argument("--json", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command == "backup-daemon":
        if not args.pair and not args.pair_by_name:
            parser.error("give at least one --pair or --pair-by-name")
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        backup_daemon(args.pid, [(Path(s), Path(d)) for s, d in args.pair], args.interval,
                      args.log, by_name_pairs=[(Path(s), Path(d)) for s, d in args.pair_by_name],
                      also_known=args.also_known, max_files_per_part=args.max_files_per_part)
    elif args.command == "audit-drive":
        report = audit_drive(args.roots)
        text = json.dumps(report, indent=2, default=str)
        print(text)
        if args.json:
            args.json.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
