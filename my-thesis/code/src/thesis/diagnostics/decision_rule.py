"""The predeclared transformation decision for UNRATE and FEDFUNDS (Part 5 §3.4).

The rule is fixed before results are seen, and it is applied to the **initial estimation
window** so the pseudo-out-of-sample experiment is not contaminated by future data
(decision T7 defines that window as the first 240 monthly or 120 quarterly observations).

    1. ADF rejects and KPSS does not reject      -> level
    2. ADF does not reject and KPSS rejects      -> first difference
    3. the two disagree                          -> Zivot-Andrews decides:
         rejects    -> level, and carry a break-sensitive robustness check
         does not   -> first difference

The full-sample tests are then reported as the jury asked, but they **never** retroactively
change the baseline: a disagreement sets a mandatory Chapter 4 robustness flag instead.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from ..core.config import Config
from ..core.schemas import TestResult
from .stationarity import adf_test, kpss_test, zivot_andrews_test

LEVEL = "level"
DIFFERENCE = "difference"


@dataclass
class TransformationDecision:
    """The baseline transformation for a disputed level series, and why."""

    series_id: str
    decision: str
    rule_branch: str
    reason: str
    initial_window_results: list[TestResult] = field(default_factory=list)
    full_sample_results: list[TestResult] = field(default_factory=list)
    break_date: str | None = None
    break_sensitive_robustness: bool = False
    full_sample_agrees: bool | None = None
    robustness_required: bool = True   # the alternative is always a Chapter 4 check

    def to_row(self) -> dict[str, Any]:
        return {
            "series_id": self.series_id,
            "baseline_transformation": self.decision,
            "rule_branch": self.rule_branch,
            "reason": self.reason,
            "break_date": self.break_date or "",
            "break_sensitive_robustness": self.break_sensitive_robustness,
            "full_sample_agrees": (
                "" if self.full_sample_agrees is None else self.full_sample_agrees
            ),
            "alternative_transformation_robustness_required": self.robustness_required,
        }


def _rejects(result: TestResult) -> bool:
    return result.decision_5pct == "reject"


def decide_transformation(
    series_id: str,
    initial_window: pd.Series,
    frequency: str,
    config: Config,
) -> TransformationDecision:
    """Apply the §3.4 rule to the initial estimation window."""
    adf = adf_test(initial_window, frequency, config, label="initial window, level")
    kpss_result = kpss_test(initial_window, frequency, config, label="initial window, level")
    results = [adf, kpss_result]

    adf_rejects = _rejects(adf)
    kpss_rejects = _rejects(kpss_result)

    if adf_rejects and not kpss_rejects:
        return TransformationDecision(
            series_id=series_id,
            decision=LEVEL,
            rule_branch="1: clear level stationarity",
            reason="ADF rejects the unit root and KPSS does not reject stationarity",
            initial_window_results=results,
        )

    if not adf_rejects and kpss_rejects:
        return TransformationDecision(
            series_id=series_id,
            decision=DIFFERENCE,
            rule_branch="2: clear nonstationarity",
            reason="ADF does not reject the unit root and KPSS rejects stationarity",
            initial_window_results=results,
        )

    # Branch 3: the two tests disagree, so the break-allowing test is the tie-breaker.
    za = zivot_andrews_test(initial_window, frequency, config, label="initial window, level")
    results.append(za)
    if _rejects(za):
        return TransformationDecision(
            series_id=series_id,
            decision=LEVEL,
            rule_branch="3a: ADF/KPSS disagree, Zivot-Andrews rejects",
            reason=(
                "ADF and KPSS disagree; allowing one endogenous break rejects the unit "
                "root, so the level is retained with a break-sensitive robustness check"
            ),
            initial_window_results=results,
            break_date=str(za.extra.get("break_date", "")),
            break_sensitive_robustness=True,
        )
    return TransformationDecision(
        series_id=series_id,
        decision=DIFFERENCE,
        rule_branch="3b: ADF/KPSS disagree, Zivot-Andrews does not reject",
        reason=(
            "ADF and KPSS disagree and the unit root is not rejected even when one "
            "endogenous break is allowed"
        ),
        initial_window_results=results,
        break_date=str(za.extra.get("break_date", "")),
    )


def confirm_on_full_sample(
    decision: TransformationDecision,
    full_sample: pd.Series,
    frequency: str,
    config: Config,
) -> TransformationDecision:
    """Report the full-sample evidence the jury asked for, without changing the baseline.

    Part 5 §3.4 is explicit: if the full sample disagrees, **do not** retrospectively change
    the baseline pseudo-out-of-sample transformation. Flag it and make the alternative a
    mandatory Chapter 4 robustness check.
    """
    adf = adf_test(full_sample, frequency, config, label="full sample, level")
    kpss_result = kpss_test(full_sample, frequency, config, label="full sample, level")
    results = [adf, kpss_result]

    adf_rejects = _rejects(adf)
    kpss_rejects = _rejects(kpss_result)
    if adf_rejects and not kpss_rejects:
        implied = LEVEL
    elif not adf_rejects and kpss_rejects:
        implied = DIFFERENCE
    else:
        za = zivot_andrews_test(full_sample, frequency, config, label="full sample, level")
        results.append(za)
        implied = LEVEL if _rejects(za) else DIFFERENCE

    decision.full_sample_results = results
    decision.full_sample_agrees = implied == decision.decision
    return decision
