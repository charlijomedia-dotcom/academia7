"""Run provenance.

CLAUDE.md §8 requires every final empirical output to record the run ID, the data
snapshot used, the frozen-data hash, the data cutoff, the code commit, the configuration
hash and the execution timestamp. This module is the single place that produces those
fields and the only sanctioned way to write a table or a figure, so an output without
provenance cannot be produced by accident.
"""

from __future__ import annotations

import datetime as _dt
import json
import platform
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

import pandas as pd

from .hashing import sha256_file, sha256_obj
from .paths import CODE_ROOT, PROJECT_ROOT, Namespace, OutputLayout

PROVENANCE_COLUMNS = (
    "run_id",
    "data_snapshot_hash",
    "code_commit_sha",
    "config_hash",
    "created_utc",
)


def _git(*args: str, strip: bool = True) -> str | None:
    """Run a git command. `strip=False` preserves leading whitespace, which the
    porcelain status format uses as part of its fixed-width status field."""
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip() if strip else out.stdout


def git_commit_sha() -> str:
    return _git("rev-parse", "HEAD") or "unknown"


def git_dirty_paths() -> tuple[str, ...] | None:
    """Repository-relative paths with uncommitted changes, or None if git cannot answer.

    Git collapses an untracked directory to a single entry ending in "/", which is kept
    as-is: prefix matching against it still works for the output roots below.
    """
    # Not stripped: the porcelain status field is two fixed-width characters followed by
    # a space, and the first of those is often a space itself. Stripping the output would
    # remove it and shift the path by one character.
    status = _git("status", "--porcelain", strip=False)
    if status is None:
        return None
    paths = []
    for line in status.splitlines():
        if not line.strip():
            continue
        entry = line[3:].strip() if len(line) > 3 else ""
        # A rename reads "old -> new"; the destination is the one that matters.
        if " -> " in entry:
            entry = entry.split(" -> ", 1)[1]
        paths.append(entry.strip('"'))
    return tuple(paths)


def git_tree_dirty() -> bool:
    paths = git_dirty_paths()
    if paths is None:
        return True  # cannot prove the tree is clean, so assume it is not
    return bool(paths)


def _relative_to_repository(path: Path) -> str:
    """A path as git would name it, relative to the repository root."""
    repository_root = _git("rev-parse", "--show-toplevel")
    base = Path(repository_root) if repository_root else PROJECT_ROOT
    try:
        return Path(path).resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return Path(path).resolve().as_posix()


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def environment_record() -> dict[str, Any]:
    """Library versions and platform, written to output/logs/environment.json."""
    versions: dict[str, str] = {}
    for name in (
        "numpy",
        "scipy",
        "pandas",
        "statsmodels",
        "arch",
        "matplotlib",
        "pyarrow",
        "psutil",
        "joblib",
        "yaml",
        "tabulate",
    ):
        try:
            module = __import__(name)
            versions[name] = getattr(module, "__version__", "unknown")
        except ImportError:
            versions[name] = "not installed"
    lock = CODE_ROOT / "requirements.lock.txt"
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": versions,
        # Approved decision R2: the pinned set is part of the provenance of a result,
        # so the lock file's hash is recorded beside the versions actually loaded. A
        # mismatch between the two is then visible rather than silent.
        "requirements_lock_sha256": sha256_file(lock) if lock.exists() else "absent",
    }


class DirtyTreeError(RuntimeError):
    """Raised when a thesis-facing run is attempted from a modified working tree."""


@dataclass
class RunContext:
    """Identity of one pipeline run."""

    namespace: Namespace
    config_hash: str
    data_snapshot_hash: str = "uninitialized"
    data_cutoff: str | None = None
    vintage_date: str | None = None
    code_commit_sha: str = field(default_factory=git_commit_sha)
    #: Whether the tree was modified at all when the run started. Recorded in the manifest
    #: as provenance; it does **not** drive `require_clean_tree`, which asks git for the
    #: dirty *paths* so it can distinguish the run's own outputs from a change that would
    #: alter the result.
    tree_dirty: bool = field(default_factory=git_tree_dirty)
    started_utc: str = field(default_factory=utc_now)
    run_id: str = field(default="")
    notes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.run_id:
            stamp = self.started_utc.replace("-", "").replace(":", "").replace("Z", "")
            self.run_id = f"{self.namespace.value}-{stamp}-{self.config_hash[:8]}"

    def require_clean_tree(self, *, produced_by_the_run: Sequence[Path] = ()) -> None:
        """Thesis-facing runs refuse to proceed from a modified working tree (D14).

        What decision D14 protects is the claim that a baseline result can be reproduced
        from the commit recorded beside it. That claim depends on the **inputs** —
        the code, the configuration, the frozen data and the approved specifications.
        It does not depend on the run's own artifacts, which are the result rather than
        an input, and which land inside the repository because Part 5 requires every
        thesis-facing number to be traceable to a file under `output/`.

        Treating those artifacts as a dirty tree makes the baseline run refuse to run a
        second time: the first run writes `output/`, and every later run then fails. So
        paths under the directories this run itself writes are excluded, and a change
        anywhere else still stops the run and is named in the error. The safeguard is
        narrower in scope and no weaker: nothing that determines the result may be
        uncommitted.
        """
        if self.namespace is not Namespace.BASELINE:
            return
        paths = git_dirty_paths()
        if paths is None:
            raise DirtyTreeError(
                "git could not report the state of the working tree, so a thesis-facing "
                "baseline run cannot certify which commit produced it."
            )
        generated = tuple(_relative_to_repository(path) for path in produced_by_the_run)
        offending = [
            path for path in paths
            if not any(path == root or path.startswith(root.rstrip("/") + "/")
                       for root in generated)
        ]
        if offending:
            shown = ", ".join(sorted(offending)[:10])
            more = "" if len(offending) <= 10 else f" (and {len(offending) - 10} more)"
            raise DirtyTreeError(
                "the working tree has uncommitted changes outside the run's own output "
                f"directories, so a thesis-facing baseline run would not be reproducible "
                f"from its recorded commit: {shown}{more}. Commit or stash them, or run "
                "with a non-baseline namespace."
            )

    def fields(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "data_snapshot_hash": self.data_snapshot_hash,
            "code_commit_sha": self.code_commit_sha,
            "config_hash": self.config_hash,
            "created_utc": utc_now(),
        }

    def manifest(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "namespace": self.namespace.value,
            "started_utc": self.started_utc,
            "code_commit_sha": self.code_commit_sha,
            "code_tree_dirty": self.tree_dirty,
            "config_hash": self.config_hash,
            "data_snapshot_hash": self.data_snapshot_hash,
            "data_cutoff": self.data_cutoff,
            "vintage_date": self.vintage_date,
            "environment": environment_record(),
            "notes": self.notes,
        }

    def stamp(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Append the provenance columns to a results table."""
        stamped = frame.copy()
        for key, value in self.fields().items():
            stamped[key] = value
        return stamped

    def write_table(
        self,
        frame: pd.DataFrame,
        path: str | Path,
        *,
        also_parquet: bool = False,
        index: bool = False,
    ) -> Path:
        """Write a results table with provenance columns attached.

        Every table the thesis cites must exist as CSV or Parquet (Outputs §1) and must
        carry its provenance, so this is the only sanctioned table writer.
        """
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        stamped = self.stamp(frame)
        stamped.to_csv(target, index=index)
        if also_parquet:
            stamped.to_parquet(target.with_suffix(".parquet"), index=index)
        return target

    def write_sidecar(self, path: str | Path, extra: dict[str, Any] | None = None) -> Path:
        """Provenance sidecar for a non-tabular artifact such as a figure."""
        target = Path(path)
        sidecar = target.with_suffix(target.suffix + ".provenance.json")
        sidecar.parent.mkdir(parents=True, exist_ok=True)
        payload = self.fields()
        payload["artifact"] = target.name
        if extra:
            payload.update(extra)
        sidecar.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return sidecar

    def write_run_manifest(self, layout: OutputLayout) -> Path:
        target = layout.manifests / "run_manifest.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(self.manifest(), indent=2, sort_keys=True), encoding="utf-8"
        )
        env_target = layout.logs / "environment.json"
        env_target.parent.mkdir(parents=True, exist_ok=True)
        env_target.write_text(
            json.dumps(environment_record(), indent=2, sort_keys=True), encoding="utf-8"
        )
        return target


def spec_hash(spec: dict[str, Any]) -> str:
    """Stable hash of a model specification."""
    return sha256_obj(spec)
