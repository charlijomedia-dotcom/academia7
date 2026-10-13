"""The canonical author-processed research input.

Part 5 §2.2A (user amendment of 13 October 2026) splits the data layer into two distinct
immutable artifacts:

1. the **official raw snapshot**, preserved exactly as the provider returned it, including
   its missing-value markers and any observations later than the usable study endpoint;
2. the **canonical model input** `data/frozen/thesis_input_2026-10-05.csv`, an
   author-processed long-format dataset that differs from the raw archive in exactly two
   cells and is the data input identity for every Part 6 result.

The two permitted differences are the October 2025 last-observation-carried-forward
replacements for CPIAUCSL and UNRATE, applied at the raw level before any transformation.
They are not official observations and are never described as such: every row carries an
`observation_status`, and the two imputed rows keep their genuinely missing `source_value`.

Every later run verifies hashes, loads this CSV first into a fresh DataFrame, derives the
monthly and quarterly panels in memory, and makes no network request.
"""

from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np
import pandas as pd

from ..core.config import Config
from ..core.hashing import sha256_file, sha256_obj
from ..core.paths import FROZEN_VINTAGE_DIR, MANIFEST_NAME
from .manifest import FrozenDataError, FrozenManifest

CANONICAL_COLUMNS = (
    "series_id",
    "date",
    "frequency",
    "value",
    "source_value",
    "observation_status",
    "imputation_method",
    "imputation_source_date",
)

STATUS_OBSERVED = "OBSERVED"
STATUS_IMPUTED = "IMPUTED_LOCF"
METHOD_LOCF = "LOCF"


class ImputationHalt(RuntimeError):
    """Raised when the data do not match the exact approved imputation situation.

    Part 5 §2.2A lists the halt conditions explicitly: an October value that is actually
    present, a missing September predecessor, unexpected missing values elsewhere,
    duplicate dates, or inconsistent vintage values. Each is a documented stop, never a
    silent substitution.
    """


class StoreState(str, Enum):
    """What the local data store currently holds."""

    ABSENT = "absent"              # nothing at all: first-run initialization permitted
    RAW_ONLY = "raw_only"          # verified raw snapshot, canonical never registered
    COMPLETE = "complete"          # raw snapshot and canonical input both registered
    UNUSABLE = "unusable"          # partial, corrupt or hash-mismatched: must stop


@dataclass(frozen=True)
class ImputationRecord:
    """One row of the T2.0B two-cell imputation audit."""

    series_id: str
    date: str
    source_value: str                 # the official value: empty, because it is missing
    previous_observed_date: str
    previous_observed_value: str
    derived_value: str
    method: str = METHOD_LOCF
    reason: str = (
        "official October 2025 release cancelled during the 2025 federal shutdown; "
        "user-approved raw-level LOCF under Part 5 section 2.2A"
    )
    official_value_missing: bool = True
    is_official_observation: bool = False

    def to_row(self) -> dict[str, Any]:
        return {
            "series_id": self.series_id,
            "date": self.date,
            "source_value": self.source_value,
            "official_value_missing": self.official_value_missing,
            "previous_observed_date": self.previous_observed_date,
            "previous_observed_value": self.previous_observed_value,
            "derived_value": self.derived_value,
            "imputation_method": self.method,
            "observation_status": STATUS_IMPUTED,
            "is_official_observation": self.is_official_observation,
            "reason": self.reason,
        }


def read_raw_strings(path: str | Path) -> pd.DataFrame:
    """Read a frozen raw CSV without touching the provider's value strings.

    Numerical precision is preserved exactly by never parsing and re-formatting the
    value, which also keeps the canonical CSV's bytes deterministic.
    """
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    if list(frame.columns) != ["date", "value"]:
        raise FrozenDataError(f"unexpected frozen raw schema in {path}: {list(frame.columns)}")
    return frame


def _usable_range(series_id: str, config: Config) -> tuple[pd.Timestamp, pd.Timestamp]:
    spec = config.get(f"targets.{series_id}")
    start = pd.Timestamp(spec.get("canonical_start") or spec["start"])
    end = pd.Timestamp(
        config.get("samples.monthly_end")
        if spec["frequency"] == "M"
        else config.get("samples.quarterly_end")
    )
    return start, end


def _approved_imputations(config: Config) -> dict[tuple[str, str], str]:
    """Map (series_id, date) -> source_date for the approved cells, and nothing else."""
    policy = config.get("missing_data_policy")
    if not policy or policy.get("rule") != "locf_raw_level":
        raise ImputationHalt(
            "missing_data_policy is not the approved raw-level LOCF rule; refusing to "
            "construct a canonical input"
        )
    return {
        (cell["series_id"], cell["date"]): cell["source_date"]
        for cell in policy["applies_only_to"]
    }


def build_canonical_frame(
    raw: Mapping[str, pd.DataFrame], config: Config
) -> tuple[pd.DataFrame, list[ImputationRecord]]:
    """Assemble the long-format canonical input and the imputation audit records.

    `raw` maps series id to the untouched two-column frame returned by `read_raw_strings`.
    Exactly the approved cells may be imputed; everything else must already be observed
    over the approved usable range, or the build stops.
    """
    approved = _approved_imputations(config)
    rows: list[dict[str, Any]] = []
    records: list[ImputationRecord] = []
    applied: set[tuple[str, str]] = set()

    for series_id in sorted(raw):
        spec = config.get(f"targets.{series_id}")
        frequency = spec["frequency"]
        frame = raw[series_id]
        if frame["date"].duplicated().any():
            raise ImputationHalt(f"{series_id}: duplicate dates in the frozen raw file")

        dates = pd.to_datetime(frame["date"])
        values = list(frame["value"])
        lookup = dict(zip(frame["date"], values))
        start, end = _usable_range(series_id, config)
        in_range = (dates >= start) & (dates <= end)

        for position, keep in enumerate(in_range):
            if not keep:
                continue
            date_str = frame["date"].iloc[position]
            raw_value = values[position]
            observed = raw_value not in (".", "")
            key = (series_id, date_str)

            if observed:
                rows.append(
                    {
                        "series_id": series_id,
                        "date": date_str,
                        "frequency": frequency,
                        "value": raw_value,
                        "source_value": raw_value,
                        "observation_status": STATUS_OBSERVED,
                        "imputation_method": "",
                        "imputation_source_date": "",
                    }
                )
                continue

            # Missing. It may be filled only if it is one of the two approved cells.
            if key not in approved:
                raise ImputationHalt(
                    f"{series_id}: unexpected missing observation at {date_str}. Only "
                    f"{sorted(approved)} may be imputed under Part 5 section 2.2A. This "
                    f"is a documented stop, not a silent substitution."
                )
            source_date = approved[key]
            source_value = lookup.get(source_date, "")
            if source_value in (".", ""):
                raise ImputationHalt(
                    f"{series_id}: the LOCF predecessor {source_date} is itself missing, "
                    f"so the approved carry-forward cannot be applied"
                )
            rows.append(
                {
                    "series_id": series_id,
                    "date": date_str,
                    "frequency": frequency,
                    "value": source_value,          # carried forward unchanged
                    "source_value": "",             # the official value is genuinely absent
                    "observation_status": STATUS_IMPUTED,
                    "imputation_method": METHOD_LOCF,
                    "imputation_source_date": source_date,
                }
            )
            records.append(
                ImputationRecord(
                    series_id=series_id,
                    date=date_str,
                    source_value="",
                    previous_observed_date=source_date,
                    previous_observed_value=source_value,
                    derived_value=source_value,
                )
            )
            applied.add(key)

    missing_cells = set(approved) - applied
    if missing_cells:
        raise ImputationHalt(
            f"the approved imputation cells {sorted(missing_cells)} were not applied: the "
            f"official October value is present, or the date is outside the usable range. "
            f"Part 5 section 2.2A requires a stop and investigation."
        )

    frame = pd.DataFrame(rows, columns=list(CANONICAL_COLUMNS))
    sort_by = config.get("canonical_input.sort_by")
    frame = frame.sort_values(sort_by, kind="mergesort").reset_index(drop=True)
    return frame, records


def write_canonical_csv(frame: pd.DataFrame, path: str | Path) -> Path:
    """Write the canonical CSV with deterministic bytes.

    Values are written as the strings they were read as, so the file reproduces exactly
    on any platform and its SHA-256 is a stable identity for the dataset.
    """
    target = Path(path)
    if list(frame.columns) != list(CANONICAL_COLUMNS):
        raise ValueError(f"canonical column order must be {CANONICAL_COLUMNS}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(CANONICAL_COLUMNS)
        for row in frame.itertuples(index=False):
            writer.writerow(list(row))
    return target


def load_canonical(
    directory: str | Path = FROZEN_VINTAGE_DIR, config: Config | None = None
) -> pd.DataFrame:
    """Load the canonical CSV into a fresh DataFrame with an explicit schema.

    This is the CSV-first contract of Comp §2: every normal run begins here, with no
    network request, and all transformations are computed downstream from this frame.
    """
    name = config.get("canonical_input.csv") if config else "thesis_input_2026-10-05.csv"
    path = Path(directory) / name
    if not path.exists():
        raise FrozenDataError(
            f"canonical input not found at {path}. The default run loads the canonical "
            f"CSV first and never downloads data."
        )
    frame = pd.read_csv(
        path,
        dtype={column: str for column in CANONICAL_COLUMNS},
        keep_default_na=False,
    )
    if list(frame.columns) != list(CANONICAL_COLUMNS):
        raise FrozenDataError(
            f"canonical input schema mismatch: expected {CANONICAL_COLUMNS}, "
            f"got {tuple(frame.columns)}"
        )
    frame["date"] = pd.to_datetime(frame["date"], format="%Y-%m-%d")
    frame["value_float"] = frame["value"].astype(float)
    return frame


def to_panels(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Derive correctly dated monthly and quarterly panels in memory.

    Quarterly GDP is never spread onto a monthly grid: each frequency gets its own panel,
    which is what keeps Part 5 §6.2's refusal to interpolate structurally true.
    """
    panels: dict[str, pd.DataFrame] = {}
    for frequency, block in frame.groupby("frequency", sort=True):
        panel = block.pivot(index="date", columns="series_id", values="value_float")
        panel.index = pd.DatetimeIndex(panel.index, name="date")
        panels[str(frequency)] = panel.sort_index()
    return panels


def imputed_dates(frame: pd.DataFrame) -> dict[str, list[pd.Timestamp]]:
    """Imputed observation dates by series, for the T4.9 exposure diagnostic."""
    imputed = frame[frame["observation_status"] == STATUS_IMPUTED]
    return {
        str(series_id): sorted(block["date"])
        for series_id, block in imputed.groupby("series_id", sort=True)
    }


# ---------------------------------------------------------------------------
# Companion artifacts (Outputs T2.0B)
# ---------------------------------------------------------------------------


def build_metadata(
    frame: pd.DataFrame,
    records: Iterable[ImputationRecord],
    source_manifest: FrozenManifest,
    config: Config,
    csv_path: Path,
) -> dict[str, Any]:
    series_block = []
    for series_id, block in frame.groupby("series_id", sort=True):
        entry = source_manifest.entry(str(series_id))
        series_block.append(
            {
                "series_id": str(series_id),
                "title": entry.title,
                "source_institution": entry.source_institution,
                "frequency": block["frequency"].iloc[0],
                "units": entry.units,
                "seasonal_adjustment": entry.seasonal_adjustment,
                # Dates are ISO strings at build time, which sort chronologically.
                "usable_first_date": str(block["date"].min()),
                "usable_last_date": str(block["date"].max()),
                "row_count": int(len(block)),
                "n_observed": int((block["observation_status"] == STATUS_OBSERVED).sum()),
                "n_imputed": int((block["observation_status"] == STATUS_IMPUTED).sum()),
                "raw_source_sha256": entry.sha256,
                "raw_first_date": entry.first_observation_date,
                "raw_last_date": entry.last_observation_date,
                "raw_row_count": entry.row_count,
                "raw_missing_dates": entry.missing_value_dates,
            }
        )
    return {
        "dataset": "author-processed canonical research input",
        "not_an_official_fred_release": True,
        "vintage_date": source_manifest.vintage_date,
        "provider": source_manifest.provider,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "csv_file": csv_path.name,
        "csv_sha256": sha256_file(csv_path),
        "row_count": int(len(frame)),
        "schema": list(CANONICAL_COLUMNS),
        "serialization": {
            "encoding": "utf-8",
            "line_terminator": "\\n",
            "date_format": "%Y-%m-%d",
            "sort_by": config.get("canonical_input.sort_by"),
            "values_written_verbatim_from_source": True,
        },
        "approved_endpoints": {
            "monthly": config.get("samples.monthly_end"),
            "quarterly": config.get("samples.quarterly_end"),
        },
        "model_input_construction_rules": {
            "transformations_applied": "none; all transformations are computed in code after loading",
            "imputation_rule": "raw-level LOCF, Part 5 section 2.2A",
            "imputation_authority": config.get("missing_data_policy.authority"),
            "imputed_cells": [record.to_row() for record in records],
        },
        "parent_source_manifest_sha256": source_manifest.content_hash,
        "parent_source_snapshot_hash": source_manifest.snapshot_hash,
        "series": series_block,
        "attribution": (
            "Federal Reserve Economic Data (FRED) / ALFRED, Federal Reserve Bank of "
            "St. Louis, and the underlying official agencies: U.S. Bureau of Economic "
            "Analysis (GDPC1), U.S. Bureau of Labor Statistics (CPIAUCSL, UNRATE), "
            "Board of Governors of the Federal Reserve System (INDPRO, FEDFUNDS, M2SL), "
            "and the NBER business-cycle chronology distributed by FRED (USREC)."
        ),
        "redistribution_note": (
            "Derived dataset for research replication, subject to the original providers' "
            "terms. Two cells are author-imputed and are not official statistics."
        ),
    }


README_TEMPLATE = """# Canonical thesis research input — {csv_name}

**This file is an author-processed research dataset. It is NOT an unmodified official FRED extract.**
Two values in it are imputed by the author and are not official statistical observations.
See "October 2025 imputation" below.

- Historical vintage: **{vintage}** (FRED/ALFRED real-time vintage)
- Rows: **{rows}** | Series: **{n_series}** | SHA-256: `{sha256}`
- Approved study endpoints: monthly **{monthly_end}**, quarterly GDP **{quarterly_end}**

## What this file is for

Every result in Parts 6 to 8 of the thesis is computed from this file. The pipeline loads
it first into a pandas DataFrame, derives monthly and quarterly panels in memory, and then
applies all transformations, diagnostics, estimation, forecasting and tests. No data are
downloaded again once this file exists and verifies against its recorded hash.

## Format

Long (tidy) format: one row per series per observation date. Quarterly GDP keeps its true
quarterly spacing and is never expanded onto a monthly grid.

| Column | Meaning |
|---|---|
| `series_id` | FRED series identifier |
| `date` | observation period start, ISO `YYYY-MM-DD`, provider's period convention |
| `frequency` | `M` (monthly) or `Q` (quarterly) |
| `value` | the raw-level modelling input used by the thesis |
| `source_value` | the official downloaded raw value; blank where the official value is genuinely unreported |
| `observation_status` | `OBSERVED` or `IMPUTED_LOCF` |
| `imputation_method` | `LOCF` for imputed rows, blank otherwise |
| `imputation_source_date` | the date the value was carried forward from, blank otherwise |

Values are written verbatim as returned by the provider, so numerical precision is
preserved and the file's bytes are reproducible. No transformed growth rates, forecasts
or future data appear in this file.

## Series

{series_table}

## October 2025 imputation

During the 2025 United States federal government shutdown the Bureau of Labor Statistics
could not collect October 2025 reference-period data. The October 2025 CPI release was
cancelled, and the October 2025 household survey, the source of the unemployment rate, was
never collected and cannot be collected retroactively. Those two official observations are
therefore permanently missing.

Under a documented, user-approved research-design decision (Part 5 §2.2A), exactly two
cells carry the previous month's raw level forward:

{imputation_table}

This is last observation carried forward at the raw level, applied once before any
transformation. It is **not** an official release, a real-time estimate, or a claim that
economic conditions were unchanged. No other value in this file is imputed.

**Known artifacts of this choice**, which users of the data must take into account:

{artifacts}

The untouched official raw files, including their missing-value markers, are archived
separately alongside this file, so anyone can inspect the genuine gaps or apply a
different method.

## Reproducing the thesis inputs

1. Verify this file against the SHA-256 above and against `{metadata_name}`.
2. Load it as a DataFrame; do not edit it by hand.
3. Split by `frequency` and pivot on `series_id` to obtain the monthly and quarterly panels.
4. Apply the transformations defined in the approved methodology. They are computed in
   code after loading, never stored here.

## Attribution and reuse

{attribution}

{redistribution}
"""


def build_readme(metadata: dict[str, Any], config: Config) -> str:
    series_rows = [
        "| Series | Frequency | Units | Range in this file | Rows | Imputed |",
        "|---|---|---|---|---:|---:|",
    ]
    for entry in metadata["series"]:
        series_rows.append(
            f"| `{entry['series_id']}` ({entry['title']}) | {entry['frequency']} | "
            f"{entry['units']} | {entry['usable_first_date']} to {entry['usable_last_date']} | "
            f"{entry['row_count']} | {entry['n_imputed']} |"
        )
    imputation_rows = [
        "| Series | Date | Official value | Value used | Carried forward from |",
        "|---|---|---|---|---|",
    ]
    for cell in metadata["model_input_construction_rules"]["imputed_cells"]:
        imputation_rows.append(
            f"| `{cell['series_id']}` | {cell['date']} | missing (unreported) | "
            f"{cell['derived_value']} | {cell['previous_observed_date']} |"
        )
    artifacts = "\n".join(
        f"- {item}" for item in config.get("missing_data_policy.known_artifacts")
    )
    return README_TEMPLATE.format(
        csv_name=metadata["csv_file"],
        vintage=metadata["vintage_date"],
        rows=metadata["row_count"],
        n_series=len(metadata["series"]),
        sha256=metadata["csv_sha256"],
        monthly_end=metadata["approved_endpoints"]["monthly"],
        quarterly_end=metadata["approved_endpoints"]["quarterly"],
        series_table="\n".join(series_rows),
        imputation_table="\n".join(imputation_rows),
        artifacts=artifacts,
        metadata_name=config.get("canonical_input.metadata"),
        attribution=metadata["attribution"],
        redistribution=metadata["redistribution_note"],
    )


def build_input_manifest(
    metadata: dict[str, Any], paths: Mapping[str, Path], source_manifest: FrozenManifest
) -> dict[str, Any]:
    """Supplemental manifest linking the canonical input to its official raw parent.

    Kept separate from the original raw manifest, which is never altered (Comp §2).
    """
    files = {}
    for label, path in sorted(paths.items()):
        files[label] = {"file_name": path.name, "sha256": sha256_file(path)}
    document = {
        "manifest_kind": "author_processed_canonical_input",
        "created_utc": metadata["created_utc"],
        "vintage_date": metadata["vintage_date"],
        "is_original_source": False,
        "parent_source_manifest_sha256": source_manifest.content_hash,
        "parent_source_snapshot_hash": source_manifest.snapshot_hash,
        "files": files,
        "imputed_cells": [
            {"series_id": cell["series_id"], "date": cell["date"], "method": cell["imputation_method"]}
            for cell in metadata["model_input_construction_rules"]["imputed_cells"]
        ],
    }
    document["manifest_content_hash"] = sha256_obj(document)
    return document
