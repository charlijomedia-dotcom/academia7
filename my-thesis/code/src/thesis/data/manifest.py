"""Frozen-data manifest.

Part 5 §2.2 fixes exactly what must be stored for every raw series and requires one
master manifest holding the hash of every frozen file. The manifest is what makes the
thesis reproducible without the network and without the API key, so it is written once
and never rewritten in place (decision D13).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ..core.hashing import combine, sha256_file, sha256_obj

MANIFEST_VERSION = 1


@dataclass
class SeriesManifestEntry:
    """Everything Part 5 §2.2 requires to be saved for one raw series."""

    series_id: str
    file_name: str
    source_institution: str
    title: str
    frequency: str
    units: str
    seasonal_adjustment: str
    vintage_date: str
    request_params: dict[str, Any]      # API key already redacted
    request_url_redacted: str
    retrieval_timestamp_utc: str
    first_observation_date: str | None
    last_observation_date: str | None
    first_observation_value: str | None
    last_observation_value: str | None
    row_count: int
    missing_value_dates: list[str] = field(default_factory=list)
    sha256: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FrozenManifest:
    vintage_date: str
    created_utc: str
    provider: str
    entries: list[SeriesManifestEntry] = field(default_factory=list)
    manifest_version: int = MANIFEST_VERSION
    notes: dict[str, Any] = field(default_factory=dict)

    @property
    def snapshot_hash(self) -> str:
        """One hash standing for the whole frozen snapshot.

        Order-independent combination of the individual file hashes, so it identifies the
        data content regardless of the order in which the series were written. Recorded on
        every downstream output as `data_snapshot_hash`.
        """
        return combine(entry.sha256 for entry in self.entries)

    def to_dict(self) -> dict[str, Any]:
        return {
            "manifest_version": self.manifest_version,
            "vintage_date": self.vintage_date,
            "created_utc": self.created_utc,
            "provider": self.provider,
            "snapshot_hash": self.snapshot_hash,
            "n_series": len(self.entries),
            "series": [entry.to_dict() for entry in self.entries],
            "notes": self.notes,
        }

    @property
    def content_hash(self) -> str:
        """Hash of the manifest document itself."""
        return sha256_obj(self.to_dict())

    def write(self, path: str | Path) -> Path:
        target = Path(path)
        if target.exists():
            raise FileExistsError(
                f"a frozen manifest already exists at {target}. The baseline snapshot is "
                f"immutable (Part 5 §2.2); it may never be silently replaced."
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        document = self.to_dict()
        document["manifest_content_hash"] = sha256_obj(document)
        target.write_text(json.dumps(document, indent=2, sort_keys=True), encoding="utf-8")
        return target

    @classmethod
    def read(cls, path: str | Path) -> "FrozenManifest":
        document = json.loads(Path(path).read_text(encoding="utf-8"))
        entries = [SeriesManifestEntry(**row) for row in document["series"]]
        manifest = cls(
            vintage_date=document["vintage_date"],
            created_utc=document["created_utc"],
            provider=document.get("provider", "FRED/ALFRED"),
            entries=entries,
            manifest_version=document.get("manifest_version", MANIFEST_VERSION),
            notes=document.get("notes", {}),
        )
        recorded = document.get("snapshot_hash")
        if recorded and recorded != manifest.snapshot_hash:
            raise ValueError(
                f"manifest at {path} is internally inconsistent: recorded snapshot hash "
                f"{recorded} does not match the hash of its own file hashes"
            )
        return manifest

    def entry(self, series_id: str) -> SeriesManifestEntry:
        for item in self.entries:
            if item.series_id == series_id:
                return item
        raise KeyError(f"series {series_id!r} is not in the frozen manifest")


@dataclass
class VerificationResult:
    series_id: str
    file_name: str
    expected_sha256: str
    actual_sha256: str | None
    present: bool

    @property
    def ok(self) -> bool:
        return self.present and self.expected_sha256 == self.actual_sha256

    def to_row(self) -> dict[str, Any]:
        return {
            "series_id": self.series_id,
            "file_name": self.file_name,
            "expected_sha256": self.expected_sha256,
            "actual_sha256": self.actual_sha256 or "",
            "present": self.present,
            "status": "ok" if self.ok else "MISMATCH",
        }


class FrozenDataError(RuntimeError):
    """Raised when frozen data are missing, altered, or inconsistent with the manifest."""


def verify_files(manifest: FrozenManifest, directory: str | Path) -> list[VerificationResult]:
    """Recompute and compare the hash of every frozen file."""
    base = Path(directory)
    results = []
    for entry in manifest.entries:
        path = base / entry.file_name
        if not path.exists():
            results.append(
                VerificationResult(entry.series_id, entry.file_name, entry.sha256, None, False)
            )
            continue
        results.append(
            VerificationResult(
                entry.series_id, entry.file_name, entry.sha256, sha256_file(path), True
            )
        )
    return results
