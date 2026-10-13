"""Data-store lifecycle: what exists locally, and what the code is allowed to do about it.

Comp §2 (amended 13 October 2026) defines three permitted situations and one forbidden
one, and this module is where that rule is enforced so no other code has to remember it:

* **absent store** - a first run may retrieve the approved 2026-10-05 vintage from
  FRED/ALFRED and atomically save the raw files, the canonical CSV and the manifests;
* **verified raw-only snapshot** predating the amendment - the canonical CSV may be built
  **once, locally, without any network request**, leaving the original raw manifest
  untouched and adding a linked supplemental manifest;
* **complete store** - verify hashes and load; never download;
* **anything partial, corrupt or hash-mismatched** - stop. Never silently re-download,
  overwrite, reset or invent data.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import pandas as pd

from ..core.config import Config
from ..core.hashing import sha256_file, sha256_obj
from ..core.paths import CANONICAL_DIR, FROZEN_DIR, MANIFEST_NAME, VINTAGE_DIRNAME
from .canonical import (
    CANONICAL_COLUMNS,
    ImputationHalt,
    ImputationRecord,
    StoreState,
    build_canonical_frame,
    build_input_manifest,
    build_metadata,
    build_readme,
    load_canonical,
    read_raw_strings,
    write_canonical_csv,
)
from .fred_client import FredClient
from .frozen import SeriesSpec, initialize_frozen, load_manifest, verify_frozen
from .manifest import FrozenDataError, FrozenManifest


@dataclass(frozen=True)
class CanonicalBundle:
    """The verified canonical input and everything identifying it."""

    frame: pd.DataFrame
    csv_path: Path
    csv_sha256: str
    metadata: dict[str, Any]
    input_manifest: dict[str, Any]
    source_manifest: FrozenManifest

    @property
    def data_input_identity(self) -> str:
        """The hash that identifies the data behind every Part 6 result (S §2.2A)."""
        return self.csv_sha256

    @property
    def parent_source_hash(self) -> str:
        return self.source_manifest.snapshot_hash


def vintage_dir(frozen_root: str | Path) -> Path:
    """The official raw snapshot lives in its own vintage subdirectory."""
    return Path(frozen_root) / VINTAGE_DIRNAME


def _paths(frozen_root: str | Path, config: Config) -> dict[str, Path]:
    """Resolve every store artifact.

    The canonical input sits directly under the frozen root, as Part 5 §2.2A specifies,
    while the untouched official raw files and their manifest stay in the vintage
    subdirectory. Keeping them apart on disk mirrors the fact that they are two distinct
    immutable datasets.
    """
    base = Path(frozen_root)
    return {
        "csv": base / config.get("canonical_input.csv"),
        "metadata": base / config.get("canonical_input.metadata"),
        "readme": base / config.get("canonical_input.readme"),
        "manifest": base / config.get("canonical_input.manifest"),
        "source_manifest": vintage_dir(base) / MANIFEST_NAME,
    }


def detect_state(frozen_root: str | Path = FROZEN_DIR, config: Config | None = None) -> StoreState:
    """Classify the local store without modifying anything."""
    if config is None:
        raise ValueError("a configuration is required to locate the canonical artifacts")
    paths = _paths(frozen_root, config)
    source_exists = paths["source_manifest"].exists()
    canonical_files = {k: paths[k].exists() for k in ("csv", "metadata", "readme", "manifest")}

    if not source_exists and not any(canonical_files.values()):
        return StoreState.ABSENT

    if not source_exists:
        # Canonical artifacts without their official parent cannot be trusted.
        return StoreState.UNUSABLE

    try:
        manifest, _ = verify_frozen(vintage_dir(frozen_root))
    except FrozenDataError:
        return StoreState.UNUSABLE

    if not any(canonical_files.values()):
        return StoreState.RAW_ONLY
    if not all(canonical_files.values()):
        # A canonical input was registered at some point but is now incomplete.
        return StoreState.UNUSABLE
    try:
        verify_canonical(frozen_root, config)
    except FrozenDataError:
        return StoreState.UNUSABLE
    return StoreState.COMPLETE


def verify_canonical(
    frozen_root: str | Path = FROZEN_DIR, config: Config | None = None
) -> dict[str, Any]:
    """Check every canonical artifact against the recorded hashes in its manifest."""
    if config is None:
        raise ValueError("a configuration is required to verify the canonical input")
    paths = _paths(frozen_root, config)
    if not paths["manifest"].exists():
        raise FrozenDataError(f"no canonical input manifest at {paths['manifest']}")
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    for label, entry in manifest["files"].items():
        path = Path(frozen_root) / entry["file_name"]
        if not path.exists():
            raise FrozenDataError(
                f"canonical artifact {entry['file_name']} is registered but missing. The "
                f"run must fail rather than re-download or overwrite (Comp section 2)."
            )
        actual = sha256_file(path)
        if actual != entry["sha256"]:
            raise FrozenDataError(
                f"canonical artifact {entry['file_name']} does not match its recorded "
                f"hash ({actual} != {entry['sha256']}). The run must fail rather than "
                f"silently replace the published dataset."
            )
    return manifest


def _write_bundle(
    raw_strings: dict[str, pd.DataFrame],
    source_manifest: FrozenManifest,
    frozen_root: Path,
    config: Config,
) -> tuple[list[ImputationRecord], dict[str, Path]]:
    """Construct and write the canonical CSV, metadata, README and linked manifest.

    Comp §2 requires the canonical artifacts to be saved atomically. Everything is built
    and written to temporary files first, then moved into place; a failure at any point
    leaves no half-written dataset behind, so a crashed build can never be mistaken for a
    registered one.
    """
    frame, records = build_canonical_frame(raw_strings, config)
    paths = _paths(frozen_root, config)
    temporary = {label: path.with_suffix(path.suffix + ".tmp") for label, path in paths.items()
                 if label != "source_manifest"}
    written: list[Path] = []

    try:
        write_canonical_csv(frame, temporary["csv"])
        # The metadata records the CSV hash, so it is computed from the staged file.
        metadata = build_metadata(frame, records, source_manifest, config, temporary["csv"])
        metadata["csv_file"] = paths["csv"].name
        temporary["metadata"].write_text(
            json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8"
        )
        temporary["readme"].write_text(build_readme(metadata, config), encoding="utf-8")
        input_manifest = build_input_manifest(
            metadata,
            {label: temporary[label] for label in ("csv", "metadata", "readme")},
            source_manifest,
        )
        # Record the final file names rather than the staging ones.
        for label in ("csv", "metadata", "readme"):
            input_manifest["files"][label]["file_name"] = paths[label].name
        input_manifest["manifest_content_hash"] = sha256_obj(
            {k: v for k, v in input_manifest.items() if k != "manifest_content_hash"}
        )
        temporary["manifest"].write_text(
            json.dumps(input_manifest, indent=2, sort_keys=True), encoding="utf-8"
        )

        # Move into place. The manifest goes last, so the dataset is only ever considered
        # registered once every file it points at is already there.
        for label in ("csv", "metadata", "readme", "manifest"):
            temporary[label].replace(paths[label])
            written.append(paths[label])
    except BaseException:
        for path in list(temporary.values()) + written:
            path.unlink(missing_ok=True)
        raise
    return records, paths


def build_canonical_from_raw(
    frozen_root: str | Path = FROZEN_DIR, config: Config | None = None
) -> CanonicalBundle:
    """Build the canonical input once from an existing verified raw-only snapshot.

    No network request is made and the original raw manifest is not altered; the canonical
    artifacts get their own linked supplemental manifest (Comp §2).
    """
    if config is None:
        raise ValueError("a configuration is required")
    frozen_root = Path(frozen_root)
    vintage = vintage_dir(frozen_root)
    source_manifest, _ = verify_frozen(vintage)
    raw_strings = {
        entry.series_id: read_raw_strings(vintage / entry.file_name)
        for entry in source_manifest.entries
    }
    _write_bundle(raw_strings, source_manifest, frozen_root, config)
    return load_bundle(frozen_root, config)


def initialize_store(
    client: FredClient,
    specs: Sequence[SeriesSpec],
    *,
    frozen_root: str | Path = FROZEN_DIR,
    config: Config,
    vintage_date: str | None = None,
) -> CanonicalBundle:
    """First-run initialization of an entirely absent store.

    Retrieves the approved historical vintage, saves the untouched official raw files and
    their manifest, then builds the canonical input from those same local files.
    """
    frozen_root = Path(frozen_root)
    vintage = vintage_dir(frozen_root)
    stamp = vintage_date or config.get("run.vintage_date")
    source_manifest = initialize_frozen(
        client, specs, vintage_date=stamp, directory=vintage
    )
    raw_strings = {
        entry.series_id: read_raw_strings(vintage / entry.file_name)
        for entry in source_manifest.entries
    }
    _write_bundle(raw_strings, source_manifest, frozen_root, config)
    return load_bundle(frozen_root, config)


def load_bundle(
    frozen_root: str | Path = FROZEN_DIR, config: Config | None = None
) -> CanonicalBundle:
    """Verify and load the canonical input. This is the start of every normal run."""
    if config is None:
        raise ValueError("a configuration is required")
    frozen_root = Path(frozen_root)
    input_manifest = verify_canonical(frozen_root, config)
    source_manifest, _ = verify_frozen(vintage_dir(frozen_root))
    paths = _paths(frozen_root, config)
    frame = load_canonical(frozen_root, config)
    metadata = json.loads(paths["metadata"].read_text(encoding="utf-8"))
    return CanonicalBundle(
        frame=frame,
        csv_path=paths["csv"],
        csv_sha256=sha256_file(paths["csv"]),
        metadata=metadata,
        input_manifest=input_manifest,
        source_manifest=source_manifest,
    )


def write_imputation_audit(records: Sequence[ImputationRecord], path: str | Path) -> Path:
    """Write the T2.0B two-row October 2025 imputation audit."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame([record.to_row() for record in records])
    frame.to_csv(target, index=False)
    return target
