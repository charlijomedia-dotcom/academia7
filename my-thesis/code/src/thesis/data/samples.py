"""Sample construction and range verification.

Two Part 5 rules are enforced structurally here.

*Range verification (§2.4).* The frozen initialization must verify the expected start and
terminal observations and stop on an unexplained discrepancy. `check_expected_ranges`
compares against the ranges actually verified in the approved vintage and treats a
deviation as a halt condition, not a warning.

*No silent sample alteration.* A series with a known permanent interior gap cannot be
turned into a modelling target until the user has chosen a missing-data rule. The open
N1 decision is therefore enforced in code: building a sample for CPIAUCSL or UNRATE
raises until `missing_data_policy` is set in the configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

import numpy as np
import pandas as pd

from ..core.config import Config
from ..transforms.differences import first_difference
from ..transforms.growth import annualized_logdiff
from .frozen import VintageDiscrepancy


class OpenDecisionError(RuntimeError):
    """Raised when work would require a methodological decision the user has not made.

    CLAUDE.md §4: stop the affected analysis, document, propose, and wait for approval.
    """


@dataclass
class RangeCheck:
    series_id: str
    expected_first: str
    expected_last: str
    expected_rows: int
    actual_first: str | None
    actual_last: str | None
    actual_rows: int
    missing_dates: list[str] = field(default_factory=list)
    note: str = ""

    @property
    def ok(self) -> bool:
        return (
            self.actual_first == self.expected_first
            and self.actual_last == self.expected_last
            and self.actual_rows == self.expected_rows
        )

    def to_row(self) -> dict[str, Any]:
        return {
            "series_id": self.series_id,
            "expected_first": self.expected_first,
            "expected_last": self.expected_last,
            "expected_rows": self.expected_rows,
            "actual_first": self.actual_first or "",
            "actual_last": self.actual_last or "",
            "actual_rows": self.actual_rows,
            "n_missing_values": len(self.missing_dates),
            "missing_dates": ";".join(self.missing_dates),
            "status": "ok" if self.ok else "DISCREPANCY",
            "note": self.note,
        }


def check_expected_ranges(
    raw: Mapping[str, pd.Series], config: Config, *, raise_on_discrepancy: bool = True
) -> list[RangeCheck]:
    """Verify every frozen series against the ranges verified in the approved vintage."""
    verified = config.get("samples.verified_raw")
    accepted = config.get("samples.accepted_raw_deviations", {}) or {}
    checks: list[RangeCheck] = []
    for series_id, series in raw.items():
        expected = verified.get(series_id)
        if expected is None:
            raise VintageDiscrepancy(
                f"{series_id}: no verified raw range is recorded in the configuration, "
                f"so the retrieved data cannot be checked against the approved vintage.",
                {"series_id": series_id},
            )
        index = pd.DatetimeIndex(series.index)
        missing = [
            d.strftime("%Y-%m-%d")
            for d in index[~np.isfinite(series.to_numpy(dtype=float))]
        ]
        checks.append(
            RangeCheck(
                series_id=series_id,
                expected_first=expected["first"],
                expected_last=expected["last"],
                expected_rows=int(expected["rows"]),
                actual_first=index[0].strftime("%Y-%m-%d") if len(index) else None,
                actual_last=index[-1].strftime("%Y-%m-%d") if len(index) else None,
                actual_rows=len(index),
                missing_dates=missing,
                note=(accepted.get(series_id) or {}).get("note", ""),
            )
        )

    bad = [check for check in checks if not check.ok]
    if bad and raise_on_discrepancy:
        detail = {
            check.series_id: {
                "expected": [check.expected_first, check.expected_last, check.expected_rows],
                "actual": [check.actual_first, check.actual_last, check.actual_rows],
            }
            for check in bad
        }
        raise VintageDiscrepancy(
            "the retrieved vintage does not match the verified ranges for: "
            f"{', '.join(c.series_id for c in bad)}. Part 5 §2.4 requires the run to stop "
            "and the discrepancy to be documented rather than the sample altered.",
            detail,
        )
    return checks


def _approved_end(frequency: str, config: Config) -> pd.Timestamp:
    key = "samples.monthly_end" if frequency == "M" else "samples.quarterly_end"
    return pd.Timestamp(config.get(key))


def clip_to_approved_range(
    series: pd.Series, series_id: str, config: Config
) -> pd.Series:
    """Clip a raw series to its approved start and the approved common endpoint.

    Decision T5: the frozen file keeps every observation the provider returned, including
    the 2026M9 values for UNRATE and FEDFUNDS; truncation to the approved 2026M8 endpoint
    happens only here, when the empirical sample is built.
    """
    spec = config.get(f"targets.{series_id}")
    start = pd.Timestamp(spec["start"])
    end = _approved_end(spec["frequency"], config)
    clipped = series.loc[(series.index >= start) & (series.index <= end)]
    clipped.name = series_id
    return clipped


def known_missing(series_id: str, config: Config) -> list[str]:
    return list((config.get("samples.known_missing", {}) or {}).get(series_id, []))


def _require_missing_data_policy(series_id: str, config: Config) -> None:
    """Enforce the open N1 decision.

    CPIAUCSL and UNRATE are permanently missing 2025-10 in the approved vintage. Part 5
    assumes contiguous monthly series, forbids backfilling and interpolation, and defines
    no rule for a permanent interior hole, so no sample may be built for these series
    until the user chooses a rule.
    """
    gaps = known_missing(series_id, config)
    if not gaps:
        return
    policy = config.get("missing_data_policy", None)
    if policy:
        return
    raise OpenDecisionError(
        f"{series_id} has a permanent interior data gap at {', '.join(gaps)} and "
        f"`missing_data_policy` is unset. The approved methodology assumes contiguous "
        f"monthly series and forbids backfilling and interpolation, so the handling rule "
        f"is a user decision. See notes/claude/data_discrepancy_2026-10-09.md (issue N1). "
        f"Work on unaffected series continues; this one is stopped."
    )


def build_target(series_id: str, raw: pd.Series, config: Config) -> pd.Series:
    """Transform one raw frozen series into its approved modelling target.

    The level/difference choice for UNRATE and FEDFUNDS is not made here: it comes from
    the predeclared §3.4 stationarity rule, so this function requires the decision to be
    supplied by the caller through `apply_decided_transform`.
    """
    _require_missing_data_policy(series_id, config)
    spec = config.get(f"targets.{series_id}")
    transform = spec["transform"]
    kind = transform["kind"]
    clipped = clip_to_approved_range(raw, series_id, config)

    if kind == "none":
        return clipped
    if kind == "logdiff_annualized":
        return annualized_logdiff(clipped, float(transform["k"])).dropna()
    if kind == "decided_by_stationarity_rule":
        raise ValueError(
            f"{series_id}: the baseline transformation is decided by the Part 5 §3.4 "
            f"stationarity rule on the initial estimation window. Call "
            f"apply_decided_transform() with that decision."
        )
    raise ValueError(f"{series_id}: unknown transformation kind {kind!r}")


def apply_decided_transform(
    series_id: str, raw: pd.Series, decision: str, config: Config
) -> pd.Series:
    """Apply the level-or-difference decision produced by the §3.4 rule."""
    _require_missing_data_policy(series_id, config)
    clipped = clip_to_approved_range(raw, series_id, config)
    if decision == "level":
        return clipped.dropna() if clipped.isna().any() else clipped
    if decision == "difference":
        return first_difference(clipped).dropna()
    raise ValueError(
        f"{series_id}: transformation decision must be 'level' or 'difference', "
        f"got {decision!r}"
    )


def var_common_sample(
    targets: Mapping[str, pd.Series], config: Config
) -> pd.DataFrame:
    """Balanced monthly system for the VAR block (Part 5 §2.4, §6.1).

    No earlier observation is backfilled and quarterly GDP is never interpolated. Rows
    that cannot be balanced are dropped and reported by the caller.
    """
    variables = config.get("models.var.variables")
    missing = [name for name in variables if name not in targets]
    if missing:
        raise KeyError(f"VAR requires {variables}; missing {missing}")
    frame = pd.DataFrame({name: targets[name] for name in variables})
    start = pd.Timestamp(config.get("samples.var_start"))
    end = pd.Timestamp(config.get("samples.var_end"))
    frame = frame.loc[(frame.index >= start) & (frame.index <= end)]
    return frame
