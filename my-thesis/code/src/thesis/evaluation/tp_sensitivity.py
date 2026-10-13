"""Turning-point-window sensitivity classification (decision M13, Outputs T4.TP1).

The baseline window width is a predeclared operational convention, not a theorem, so Part 5
requires the turning-point analysis to be repeated at narrower and wider definitions and
the conclusion to be classified against the baseline.

Decision M13 fixes the categories. The "magnitude halved" rule I had proposed was rejected
in favour of an inferential-support criterion:

* **unchanged**  - same direction and the same substantive inferential conclusion;
* **weakened**   - same direction, but inferential support present at the baseline is lost;
* **reversed**   - the sign of the relevant relative-loss comparison reverses;
* **unavailable**- the comparison or its inference cannot be computed.

A same-direction result that becomes *stronger* is recorded in a separate
`support_change` field rather than inventing a fifth headline category.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

UNCHANGED = "unchanged"
WEAKENED = "weakened"
REVERSED = "reversed"
UNAVAILABLE = "unavailable"

STRENGTHENED = "strengthened"
NO_CHANGE = "no_change"
LOST = "support_lost"
STILL_ABSENT = "support_absent_in_both"


@dataclass(frozen=True)
class SensitivityVerdict:
    classification: str
    support_change: str
    notes: str

    def to_row(self) -> dict[str, Any]:
        return {
            "conclusion_vs_baseline": self.classification,
            "support_change": self.support_change,
            "notes": self.notes,
        }


def classify(
    baseline_differential: float,
    baseline_supported: bool,
    alternative_differential: float,
    alternative_supported: bool,
    *,
    baseline_available: bool = True,
    alternative_available: bool = True,
) -> SensitivityVerdict:
    """Compare an alternative window against the baseline window."""
    if not (baseline_available and alternative_available):
        return SensitivityVerdict(UNAVAILABLE, NO_CHANGE,
                                  "comparison or inference could not be computed")
    if not np.isfinite(baseline_differential) or not np.isfinite(alternative_differential):
        return SensitivityVerdict(UNAVAILABLE, NO_CHANGE,
                                  "non-finite mean loss differential")

    same_direction = np.sign(baseline_differential) == np.sign(alternative_differential)
    if not same_direction and baseline_differential != 0 and alternative_differential != 0:
        return SensitivityVerdict(
            REVERSED,
            NO_CHANGE,
            f"mean loss differential changed sign: {baseline_differential:+.6g} "
            f"-> {alternative_differential:+.6g}",
        )

    if baseline_supported and not alternative_supported:
        return SensitivityVerdict(
            WEAKENED, LOST,
            "same direction, but the inferential support present at the baseline window "
            "is absent at this window",
        )
    if alternative_supported and not baseline_supported:
        return SensitivityVerdict(
            UNCHANGED, STRENGTHENED,
            "same direction and the evidence is statistically stronger than at the "
            "baseline window",
        )
    support = NO_CHANGE if baseline_supported else STILL_ABSENT
    return SensitivityVerdict(
        UNCHANGED, support,
        "same direction and the same substantive inferential conclusion",
    )
