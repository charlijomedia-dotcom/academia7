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
    # Correction F4: the Zivot-Andrews results reported under Part 5 §3.2 / P-02 for the
    # initial window and the full sample, whether or not the §3.4 tie-break needed them.
    za_initial_window: TestResult | None = None
    za_full_sample: TestResult | None = None

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
            **(self._za_columns() if self._za_reported() else {}),
        }

    def _za_reported(self) -> bool:
        from ..correction.flags import ACTIVE
        return ACTIVE.f4_zivot_andrews_reporting

    def _za_columns(self) -> dict[str, Any]:
        return {
            "za_initial_window_statistic": _za(self.za_initial_window, "statistic"),
            "za_initial_window_p_value": _za(self.za_initial_window, "p_value"),
            "za_initial_window_break_date": _za(self.za_initial_window, "break_date"),
            "za_full_sample_statistic": _za(self.za_full_sample, "statistic"),
            "za_full_sample_p_value": _za(self.za_full_sample, "p_value"),
            "za_full_sample_break_date": _za(self.za_full_sample, "break_date"),
            "za_role": ("§3.4 tie-break" if self.rule_branch.startswith("3")
                        else "reported under §3.2 / P-02; not used by the §3.4 decision "
                             "because ADF and KPSS agree"),
        }


def _za(result: TestResult | None, field_name: str) -> Any:
    if result is None:
        return ""
    if field_name == "break_date":
        return str(result.extra.get("break_date", ""))
    return getattr(result, field_name)


def report_zivot_andrews(
    decision: TransformationDecision,
    initial_window: pd.Series,
    full_sample: pd.Series,
    frequency: str,
    config: Config,
) -> list[TestResult]:
    """Zivot-Andrews on both levels, as Part 5 §3.2 requires (correction F4).

    §3.2 applies Zivot-Andrews to UNRATE and FEDFUNDS in levels and requires the break
    date to be reported and plotted; P-02 requires a break-allowing test. §3.4 uses the
    same test as a tie-breaker only when ADF and KPSS disagree. This function reports the
    test on the initial window and on the full sample in every case, reusing a result the
    tie-break already produced. It never changes `decision.decision`: the §3.4 rule is
    evaluated exactly as before, and a test that did not enter the rule is labelled so.
    Returns only the newly computed results (to be added to T2.2).
    """
    def existing(results: list[TestResult]) -> TestResult | None:
        return next((r for r in results if r.name.startswith("Zivot-Andrews")), None)

    added: list[TestResult] = []
    note = "reported under Part 5 §3.2 / P-02; not used by the §3.4 rule"
    za_initial = existing(decision.initial_window_results)
    if za_initial is None:
        za_initial = zivot_andrews_test(initial_window, frequency, config,
                                        label=f"initial window, level; {note}")
        added.append(za_initial)
    za_full = existing(decision.full_sample_results)
    if za_full is None:
        za_full = zivot_andrews_test(full_sample, frequency, config,
                                     label=f"full sample, level; {note}")
        added.append(za_full)
    decision.za_initial_window = za_initial
    decision.za_full_sample = za_full
    return added


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
