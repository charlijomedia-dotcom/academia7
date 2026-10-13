"""Table construction and presentation conventions (Part 5 §13.2, Outputs §1, §11).

Every table the thesis shows must also exist as a machine-readable file carrying its
provenance, so a number in the manuscript can always be traced to the run that produced it
(CLAUDE.md §9). Significance is displayed one way only: exact p-values plus stars at
10/5/1% (decision D20).
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from ..core.schemas import FailureEvent, FitRecord, TestResult

STAR_LEVELS = ((0.01, "***"), (0.05, "**"), (0.10, "*"))


def stars(p_value: float | None) -> str:
    """Significance stars at the single approved convention."""
    if p_value is None or not np.isfinite(p_value):
        return ""
    for threshold, mark in STAR_LEVELS:
        if p_value < threshold:
            return mark
    return ""


def with_stars(frame: pd.DataFrame, p_column: str = "p_value",
               target: str = "stars") -> pd.DataFrame:
    out = frame.copy()
    if p_column in out.columns:
        out[target] = [stars(p) for p in out[p_column]]
    return out


def test_table(results: Iterable[TestResult]) -> pd.DataFrame:
    """The standardized hypothesis-test table (T-DIAG).

    Part 5 §7.2 requires every test to state its name, null, statistic, reference
    distribution, p-value, 5% decision and implication. Building the table from
    `TestResult` makes that structural: a test cannot reach a table without them.
    """
    rows = [result.to_row() for result in results]
    frame = pd.DataFrame(rows)
    return with_stars(frame) if not frame.empty else frame


def concept_to_series_table(catalog: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    """T2.0: every retained and explicitly excluded candidate, with its justification."""
    rows = []
    for entry in catalog:
        rows.append({
            "part4_concept": entry.get("concept", ""),
            "candidate_series": entry.get("title", entry["series_id"]),
            "fred_id": entry["series_id"],
            "retained": bool(entry.get("retained", False)),
            "role": entry.get("role", "forecast_target" if entry.get("retained") else ""),
            "economic_justification": entry.get("economic_justification", ""),
            "statistical_justification": entry.get("statistical_justification", ""),
            "open_access_retrieval": entry.get("retrieval", ""),
            "source_institution": entry.get("source", ""),
            "frequency": entry.get("frequency", ""),
            "exclusion_reason": entry.get("exclusion_reason", ""),
        })
    return pd.DataFrame(rows)


def frozen_manifest_table(manifest, canonical: Mapping[str, Any] | None = None) -> pd.DataFrame:
    """T2.0A: the frozen-data manifest.

    The amendment requires the derived canonical input to be listed here too, clearly
    distinguished from the unmodified official sources it was built from.
    """
    rows = []
    for entry in manifest.entries:
        rows.append({
            "artifact": entry.file_name,
            "series_id": entry.series_id,
            "source": entry.source_institution,
            "input_kind": "original_source",
            "vintage_date": entry.vintage_date,
            "request_parameters": str(entry.request_params),
            "raw_first_date": entry.first_observation_date,
            "raw_last_date": entry.last_observation_date,
            "row_count": entry.row_count,
            "missing_value_dates": ";".join(entry.missing_value_dates),
            "retrieval_timestamp": entry.retrieval_timestamp_utc,
            "sha256": entry.sha256,
            "hash_verification_status": "verified",
            "parent_source_snapshot_hash": "",
            "imputation_audit_hash": "",
        })
    if canonical:
        rows.append({
            "artifact": canonical["csv_file"],
            "series_id": "ALL (7 series)",
            "source": "author-processed from the frozen official snapshot",
            "input_kind": "author_processed_canonical_input",
            "vintage_date": canonical["vintage_date"],
            "request_parameters": "not applicable: derived locally, no request",
            "raw_first_date": "",
            "raw_last_date": "",
            "row_count": canonical["row_count"],
            "missing_value_dates": "",
            "retrieval_timestamp": canonical["created_utc"],
            "sha256": canonical["csv_sha256"],
            "hash_verification_status": "verified",
            "parent_source_snapshot_hash": canonical["parent_source_snapshot_hash"],
            "imputation_audit_hash": canonical.get("imputation_audit_sha256", ""),
        })
    return pd.DataFrame(rows)


def data_dictionary_table(entries: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    """T2.1: data dictionary and sample audit, including LOCF provenance."""
    return pd.DataFrame(entries)


def fit_records_table(records: Iterable[FitRecord]) -> pd.DataFrame:
    rows = [record.to_row() for record in records]
    return pd.DataFrame(rows)


def failure_registry_table(events: Iterable[FailureEvent]) -> pd.DataFrame:
    """T4.7: one row per failure or fragility event."""
    rows = [event.to_row() for event in events]
    frame = pd.DataFrame(rows)
    if frame.empty:
        frame = pd.DataFrame(columns=[
            "series", "model", "refit_date", "horizon", "category", "reason_code",
            "raw_diagnostic", "forecast_retained", "figure_separated",
        ])
    return frame


DATA_GAP_COLUMNS = (
    "series", "model", "refit_date", "horizon", "missing_dates", "stage", "detail",
    "is_model_failure", "counted_against_model",
)


def data_gap_table(events: Iterable[Any]) -> pd.DataFrame:
    """Data gaps, kept strictly separate from the model failure registry.

    The two boolean columns are constant by construction: a gap is an external data
    condition, so it is never a model failure and is never counted against a model
    (Part 5 §2.2A and the approved N1 handling). They are written explicitly so a reader
    of the CSV alone cannot mistake this register for T4.7.
    """
    rows = []
    for event in events:
        row = event.to_row()
        row["is_model_failure"] = False
        row["counted_against_model"] = False
        rows.append(row)
    frame = pd.DataFrame(rows)
    if frame.empty:
        frame = pd.DataFrame(columns=list(DATA_GAP_COLUMNS))
    return frame


CLAIM_MATRIX_COLUMNS = (
    "claim_id",
    "claim_text_stub",
    "target",
    "supporting_output_files",
    "baseline_result",
    "robustness_result",
    "status",
    "jury_ids_addressed",
)
CLAIM_STATUSES = ("SUPPORTED", "QUALIFIED", "NOT_SUPPORTED", "INCONCLUSIVE")


def empty_claim_matrix() -> pd.DataFrame:
    """The Part 8 claim-evidence matrix schema (Outputs §12, decision D18).

    Part 6 builds and validates the schema; Part 8 populates it from final results.
    """
    return pd.DataFrame(columns=list(CLAIM_MATRIX_COLUMNS))


def validate_claim_matrix(frame: pd.DataFrame) -> list[str]:
    """Return the problems with a claim matrix, empty when it is valid."""
    problems = []
    missing = [c for c in CLAIM_MATRIX_COLUMNS if c not in frame.columns]
    if missing:
        problems.append(f"missing columns: {missing}")
    if "status" in frame.columns:
        bad = sorted(set(frame["status"].dropna()) - set(CLAIM_STATUSES))
        if bad:
            problems.append(f"invalid status values: {bad}")
    return problems
