"""Creating, verifying and reading the frozen thesis snapshot.

Part 5 §2.2 and Comp §2 fix the behaviour implemented here:

* initialization retrieves the approved series at the 2026-10-05 vintage, saves the raw
  observations exactly as returned, records metadata, request parameters and SHA-256
  hashes, writes one immutable master manifest, and stops on any unexplained discrepancy;
* the normal run never contacts the internet: it verifies the frozen hashes and reads the
  local files;
* the frozen snapshot is never silently replaced.
"""

from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd

from ..core.hashing import sha256_file
from ..core.paths import FROZEN_VINTAGE_DIR, MANIFEST_NAME
from .fred_client import FredClient, SeriesResponse, compare_responses
from .manifest import (
    FrozenDataError,
    FrozenManifest,
    SeriesManifestEntry,
    VerificationResult,
    verify_files,
)

CSV_HEADER = ("date", "value")


class VintageDiscrepancy(RuntimeError):
    """Raised when the vintage cross-check or an expected range check fails.

    Part 5 §2.4 requires the run to stop and the discrepancy to be saved rather than the
    sample to be altered silently.
    """

    def __init__(self, message: str, details: dict[str, Any]):
        super().__init__(message)
        self.details = details


def write_series_csv(path: str | Path, response: SeriesResponse) -> Path:
    """Write one raw series as deterministic CSV.

    The provider's value string is written verbatim, including "." for a missing
    observation, so the frozen file is a faithful copy of the official record and the
    hash is stable across platforms (LF line endings, no locale-dependent formatting).
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(CSV_HEADER)
        for obs in response.observations:
            writer.writerow([obs.date, obs.raw_value])
    return target


def read_series_csv(path: str | Path) -> pd.Series:
    """Read a frozen CSV into a float Series indexed by date, with NaN for missing."""
    frame = pd.read_csv(path, dtype={"date": str, "value": str}, keep_default_na=False)
    values = [np.nan if raw in (".", "") else float(raw) for raw in frame["value"]]
    index = pd.to_datetime(frame["date"])
    series = pd.Series(values, index=pd.DatetimeIndex(index), dtype=float)
    series.index.name = "date"
    return series


@dataclass
class SeriesSpec:
    """What to retrieve for one series."""

    series_id: str
    source_institution: str = ""


def _entry_from_response(
    response: SeriesResponse,
    metadata: dict[str, Any],
    file_name: str,
    file_path: Path,
    vintage_date: str,
    source_institution: str,
) -> SeriesManifestEntry:
    first = response.observations[0] if response.observations else None
    last = response.observations[-1] if response.observations else None
    return SeriesManifestEntry(
        series_id=response.series_id,
        file_name=file_name,
        source_institution=source_institution,
        title=metadata.get("title", ""),
        frequency=metadata.get("frequency_short", metadata.get("frequency", "")),
        units=metadata.get("units", ""),
        seasonal_adjustment=metadata.get(
            "seasonal_adjustment_short", metadata.get("seasonal_adjustment", "")
        ),
        vintage_date=vintage_date,
        request_params=response.request_params,
        request_url_redacted=response.request_url_redacted,
        retrieval_timestamp_utc=response.retrieved_utc,
        first_observation_date=first.date if first else None,
        last_observation_date=last.date if last else None,
        first_observation_value=first.raw_value if first else None,
        last_observation_value=last.raw_value if last else None,
        row_count=response.n_rows,
        missing_value_dates=response.missing_dates,
        sha256=sha256_file(file_path),
    )


def initialize_frozen(
    client: FredClient,
    specs: Sequence[SeriesSpec],
    *,
    vintage_date: str,
    directory: str | Path = FROZEN_VINTAGE_DIR,
    audit_cross_check: bool = True,
    provider: str = "FRED/ALFRED",
    notes: dict[str, Any] | None = None,
) -> FrozenManifest:
    """Create the immutable frozen snapshot. Runs once, by explicit approval only.

    Decision T6: the `vintage_dates` form is the primary request and the
    `realtime_start = realtime_end` form is an audit cross-check; a material discrepancy
    stops the run instead of being resolved silently.
    """
    base = Path(directory)
    manifest_path = base / MANIFEST_NAME
    if manifest_path.exists():
        raise FileExistsError(
            f"{manifest_path} already exists. The frozen baseline is immutable and is "
            f"never regenerated in place (Part 5 §2.2). Use the refresh command, which "
            f"writes to a separate dated namespace."
        )

    entries: list[SeriesManifestEntry] = []
    cross_checks: list[dict[str, Any]] = []
    for spec in specs:
        response = client.fetch(spec.series_id, vintage_date=vintage_date)
        if audit_cross_check:
            audit = client.fetch(spec.series_id, realtime=vintage_date)
            comparison = compare_responses(response, audit)
            cross_checks.append(comparison)
            if not comparison["identical"]:
                raise VintageDiscrepancy(
                    f"{spec.series_id}: the vintage_dates and realtime request forms "
                    f"returned different data. Part 5 §2.2 and decision T6 require the "
                    f"run to stop and the discrepancy to be documented.",
                    comparison,
                )
        metadata = client.fetch_metadata(spec.series_id)
        file_name = f"{spec.series_id}.csv"
        file_path = write_series_csv(base / file_name, response)
        _write_series_metadata(base / f"{spec.series_id}.meta.json", response, metadata)
        entries.append(
            _entry_from_response(
                response,
                metadata,
                file_name,
                file_path,
                vintage_date,
                spec.source_institution,
            )
        )

    manifest = FrozenManifest(
        vintage_date=vintage_date,
        created_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        provider=provider,
        entries=entries,
        notes={**(notes or {}), "vintage_cross_checks": cross_checks},
    )
    manifest.write(manifest_path)
    return manifest


def _write_series_metadata(
    path: Path, response: SeriesResponse, metadata: dict[str, Any]
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "series_id": response.series_id,
        "provider_metadata": metadata,
        "request_params": response.request_params,
        "request_url_redacted": response.request_url_redacted,
        "retrieved_utc": response.retrieved_utc,
        "row_count": response.n_rows,
        "first_observation_date": response.first_date,
        "last_observation_date": response.last_date,
        "missing_value_dates": response.missing_dates,
        "response_metadata": response.raw_payload,
    }
    path.write_text(json.dumps(document, indent=2, sort_keys=True), encoding="utf-8")
    return path


def load_manifest(directory: str | Path = FROZEN_VINTAGE_DIR) -> FrozenManifest:
    path = Path(directory) / MANIFEST_NAME
    if not path.exists():
        raise FrozenDataError(
            f"no frozen manifest at {path}. The baseline run reads only frozen data; "
            f"run the approved initialization first."
        )
    return FrozenManifest.read(path)


def verify_frozen(
    directory: str | Path = FROZEN_VINTAGE_DIR,
) -> tuple[FrozenManifest, list[VerificationResult]]:
    """Verify every frozen file against the manifest before any estimation (Comp §2)."""
    manifest = load_manifest(directory)
    results = verify_files(manifest, directory)
    bad = [r for r in results if not r.ok]
    if bad:
        detail = ", ".join(f"{r.series_id} ({'missing' if not r.present else 'altered'})" for r in bad)
        raise FrozenDataError(
            f"frozen-data verification failed for: {detail}. The snapshot must match the "
            f"manifest exactly; it is never silently replaced."
        )
    return manifest, results


def load_frozen_series(
    series_id: str, directory: str | Path = FROZEN_VINTAGE_DIR
) -> pd.Series:
    """Read one verified frozen series as raw levels."""
    path = Path(directory) / f"{series_id}.csv"
    if not path.exists():
        raise FrozenDataError(f"frozen file not found for {series_id}: {path}")
    series = read_series_csv(path)
    series.name = series_id
    return series


def load_all_frozen(
    series_ids: Iterable[str], directory: str | Path = FROZEN_VINTAGE_DIR
) -> dict[str, pd.Series]:
    return {sid: load_frozen_series(sid, directory) for sid in series_ids}
