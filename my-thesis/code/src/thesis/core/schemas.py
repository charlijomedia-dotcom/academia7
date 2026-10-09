"""Record types shared across the pipeline.

Three of these exist to make methodological requirements structural rather than a matter
of remembering to do the right thing:

* `TestResult` carries the fields Part 5 §7.2 requires of every hypothesis test
  (jury R1-13), so a test cannot be reported without its null, reference distribution,
  decision rule and tuning choices.
* `FitRecord` / `FailureEvent` make failure visible (Part 5 §8.3): a failed estimation
  produces a record, never a silent substitution.
* `DataGapEvent` is deliberately *not* a failure. An external data outage is a property
  of the data, not of a model, and must never be counted against a model.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, ClassVar


class Status(str, Enum):
    """Adequacy classification of a single estimation (Part 5 §7.5)."""

    ADEQUATE = "adequate"
    FRAGILE = "fragile"
    FAILED = "failed"


class ReasonCode(str, Enum):
    """Fixed reason codes for the failure and fragility registry (Outputs §9).

    The list is closed: the outputs specification fixes these codes, so a new code may
    not be invented without a methodology revision.
    """

    NONCONVERGENCE = "NONCONVERGENCE"
    NONFINITE = "NONFINITE"
    SINGULAR_COV = "SINGULAR_COV"
    UNSTABLE_AR = "UNSTABLE_AR"
    EMPTY_REGIME = "EMPTY_REGIME"
    TRANSITION_BOUNDARY = "TRANSITION_BOUNDARY"
    STAR_GAMMA_BOUND = "STAR_GAMMA_BOUND"
    STAR_THRESHOLD_EXTREME = "STAR_THRESHOLD_EXTREME"
    RESIDUAL_AUTOCORR = "RESIDUAL_AUTOCORR"
    EXTREME_FORECAST = "EXTREME_FORECAST"
    LOW_OCCUPANCY = "LOW_OCCUPANCY"
    NEAR_CONSTANT_TRANSITION = "NEAR_CONSTANT_TRANSITION"
    ILL_CONDITIONED_COV = "ILL_CONDITIONED_COV"


#: Codes that, on their own, make an estimation unusable (Part 5 §7.5 "Failed").
FAILURE_CODES: frozenset[ReasonCode] = frozenset(
    {
        ReasonCode.NONCONVERGENCE,
        ReasonCode.NONFINITE,
        ReasonCode.SINGULAR_COV,
        ReasonCode.UNSTABLE_AR,
        ReasonCode.EMPTY_REGIME,
    }
)


@dataclass(frozen=True)
class TestResult:
    """One hypothesis test, reported in the standardized Part 5 §7.2 form."""

    #: This is a result record, not a pytest test class.
    __test__: ClassVar[bool] = False

    name: str
    null_hypothesis: str
    statistic: float | None
    p_value: float | None
    reference: str
    decision_5pct: str
    implication: str
    series: str | None = None
    model: str | None = None
    tuning: dict[str, Any] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)
    available: bool = True
    unavailable_reason: str | None = None

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row["tuning"] = _flatten_mapping(self.tuning)
        row["extra"] = _flatten_mapping(self.extra)
        return row


@dataclass
class FitRecord:
    """The outcome of estimating one model on one estimation window."""

    series: str
    model: str
    spec_label: str
    spec_hash: str
    window_start: str
    window_end: str
    refit_date: str
    converged: bool
    status: Status = Status.ADEQUATE
    reason_codes: list[ReasonCode] = field(default_factory=list)
    loglik: float | None = None
    aic: float | None = None
    bic: float | None = None
    n_obs: int | None = None
    params: dict[str, float] = field(default_factory=dict)
    std_errors: dict[str, float] = field(default_factory=dict)
    start_used: str | None = None
    optimizer_message: str | None = None
    wall_seconds: float | None = None
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def add_flag(self, code: ReasonCode, status: Status, detail: Any = None) -> None:
        """Attach a flag and escalate the status.

        Status only ever moves towards `FAILED`; a later adequate-looking check can
        never clear an earlier failure.
        """
        if code not in self.reason_codes:
            self.reason_codes.append(code)
        if detail is not None:
            self.diagnostics[f"flag_{code.value}"] = detail
        order = {Status.ADEQUATE: 0, Status.FRAGILE: 1, Status.FAILED: 2}
        if order[status] > order[self.status]:
            self.status = status

    @property
    def usable(self) -> bool:
        return self.status is not Status.FAILED

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row["status"] = self.status.value
        row["reason_codes"] = ";".join(code.value for code in self.reason_codes)
        row["params"] = _flatten_mapping(self.params)
        row["std_errors"] = _flatten_mapping(self.std_errors)
        row["diagnostics"] = _flatten_mapping(self.diagnostics)
        return row


@dataclass(frozen=True)
class FailureEvent:
    """One row of the T4.7 failure and fragility registry."""

    series: str
    model: str
    refit_date: str
    horizon: int | None
    category: Status
    reason_code: ReasonCode
    raw_diagnostic: str
    forecast_retained: bool
    figure_separated: bool

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row["category"] = self.category.value
        row["reason_code"] = self.reason_code.value
        return row


@dataclass(frozen=True)
class DataGapEvent:
    """A forecast or estimation row that could not be formed because data are missing.

    This is an external data condition, not a model failure, and is reported separately
    so that no model is penalised for it.
    """

    series: str
    model: str
    refit_date: str
    horizon: int | None
    missing_dates: tuple[str, ...]
    stage: str
    detail: str

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        row["missing_dates"] = ";".join(self.missing_dates)
        return row


def _flatten_mapping(mapping: dict[str, Any]) -> str:
    """Render a small mapping as a stable, human-readable cell value."""
    if not mapping:
        return ""
    parts = []
    for key in sorted(mapping):
        value = mapping[key]
        if isinstance(value, float):
            parts.append(f"{key}={value:.10g}")
        else:
            parts.append(f"{key}={value}")
    return "; ".join(parts)
