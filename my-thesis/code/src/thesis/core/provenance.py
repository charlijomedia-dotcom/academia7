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
from typing import Any

import pandas as pd

from .hashing import sha256_obj
from .paths import PROJECT_ROOT, Namespace, OutputLayout

PROVENANCE_COLUMNS = (
    "run_id",
    "data_snapshot_hash",
    "code_commit_sha",
    "config_hash",
    "created_utc",
)


def _git(*args: str) -> str | None:
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
    return out.stdout.strip() if out.returncode == 0 else None


def git_commit_sha() -> str:
    return _git("rev-parse", "HEAD") or "unknown"


def git_tree_dirty() -> bool:
    status = _git("status", "--porcelain")
    if status is None:
        return True  # cannot prove the tree is clean, so assume it is not
    return bool(status.strip())


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
        "yaml",
    ):
        try:
            module = __import__(name)
            versions[name] = getattr(module, "__version__", "unknown")
        except ImportError:
            versions[name] = "not installed"
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": versions,
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
    tree_dirty: bool = field(default_factory=git_tree_dirty)
    started_utc: str = field(default_factory=utc_now)
    run_id: str = field(default="")
    notes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.run_id:
            stamp = self.started_utc.replace("-", "").replace(":", "").replace("Z", "")
            self.run_id = f"{self.namespace.value}-{stamp}-{self.config_hash[:8]}"

    def require_clean_tree(self) -> None:
        """Thesis-facing runs refuse to proceed from a modified working tree (D14)."""
        if self.namespace is Namespace.BASELINE and self.tree_dirty:
            raise DirtyTreeError(
                "the working tree has uncommitted changes, so a thesis-facing baseline "
                "run would not be reproducible from its recorded commit. Commit or stash "
                "the changes, or run with a non-baseline namespace."
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
