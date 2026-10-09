"""Central path registry.

One place decides where anything is written, so the namespace separation required by
the computational spec (Comp §12, §13 and approved decision D16) cannot be violated by
accident: smoke, refresh and robustness output can never land on baseline output.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# The project root is my-thesis/, two levels above code/src/thesis/core/paths.py -> up 4.
PROJECT_ROOT = Path(__file__).resolve().parents[4]
CODE_ROOT = PROJECT_ROOT / "code"
CONFIG_DIR = CODE_ROOT / "configs"

DATA_DIR = PROJECT_ROOT / "data"
FROZEN_DIR = DATA_DIR / "frozen"
VINTAGE_DIRNAME = "fred_vintage_2026-10-05"
FROZEN_VINTAGE_DIR = FROZEN_DIR / VINTAGE_DIRNAME
MANIFEST_NAME = "MANIFEST.json"

NOTES_DIR = PROJECT_ROOT / "notes" / "claude"
SOURCE_MATERIALS_DIR = PROJECT_ROOT / "source-materials"


class Namespace(str, Enum):
    """Output namespaces. Baseline is the only thesis-facing one."""

    BASELINE = "baseline"
    SMOKE = "smoke"
    REFRESH = "refresh"


@dataclass(frozen=True)
class OutputLayout:
    """Resolved output directories for one namespace.

    `robustness` is a subdirectory rather than a namespace: Comp §13 requires robustness
    output to be stored separately from baseline output, but within the same run.
    """

    root: Path
    cache: Path

    @property
    def manifests(self) -> Path:
        return self.root / "manifests"

    @property
    def data_audit(self) -> Path:
        return self.root / "data_audit"

    @property
    def diagnostics(self) -> Path:
        return self.root / "diagnostics"

    @property
    def models(self) -> Path:
        return self.root / "models"

    @property
    def forecasts(self) -> Path:
        return self.root / "forecasts"

    @property
    def forecast_tests(self) -> Path:
        return self.root / "forecast_tests"

    @property
    def robustness(self) -> Path:
        return self.root / "robustness"

    @property
    def tables(self) -> Path:
        return self.root / "tables"

    @property
    def figures(self) -> Path:
        return self.root / "figures"

    @property
    def logs(self) -> Path:
        return self.root / "logs"

    def all_dirs(self) -> list[Path]:
        return [
            self.manifests,
            self.data_audit,
            self.diagnostics,
            self.models,
            self.forecasts,
            self.forecast_tests,
            self.robustness,
            self.tables,
            self.figures,
            self.logs,
        ]

    def create(self) -> None:
        for directory in self.all_dirs():
            directory.mkdir(parents=True, exist_ok=True)
        self.cache.mkdir(parents=True, exist_ok=True)


def output_layout(namespace: Namespace, stamp: str | None = None) -> OutputLayout:
    """Resolve the output layout for a namespace.

    `stamp` is required for the refresh namespace (the dated snapshot directory of
    Part 5 §2.2) and is used to keep smoke runs of different runs apart.
    """
    namespace = Namespace(namespace)
    if namespace is Namespace.BASELINE:
        return OutputLayout(root=PROJECT_ROOT / "output", cache=PROJECT_ROOT / "cache")
    if namespace is Namespace.SMOKE:
        root = PROJECT_ROOT / "smoke_output"
        if stamp:
            root = root / stamp
        return OutputLayout(root=root, cache=PROJECT_ROOT / "smoke_cache")
    if namespace is Namespace.REFRESH:
        if not stamp:
            raise ValueError("the refresh namespace requires a dated stamp (YYYY-MM-DD)")
        return OutputLayout(
            root=PROJECT_ROOT / "output_refreshed" / stamp,
            cache=PROJECT_ROOT / "cache_refreshed" / stamp,
        )
    raise ValueError(f"unknown namespace: {namespace}")


def refreshed_data_dir(stamp: str) -> Path:
    """Fresh downloads live under data/refreshed/<date>/ and never touch data/frozen/."""
    if not stamp:
        raise ValueError("a refresh snapshot requires a dated stamp (YYYY-MM-DD)")
    return DATA_DIR / "refreshed" / stamp


def audit_data_dir(stamp: str) -> Path:
    """Independent ALFRED reconstruction for audit only (Comp §2)."""
    return DATA_DIR / "audit" / stamp
