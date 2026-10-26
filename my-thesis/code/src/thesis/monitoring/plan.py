"""The planned workload of a run.

Three different units are kept apart throughout, because conflating them is what makes a
progress bar lie:

* a **chain** is one (series, model, specification, window length) rolling exercise;
* a **forecast origin** is one estimation of that chain on one window, i.e. one model
  fit (or one fit served from the cache);
* a **forecast record** is one horizon-specific forecast. A single fit at an origin
  produces one record per horizon that still has a realized target.

Origin totals are exact: they are computed with the same `estimation_origins` the rolling
engine uses. A total that cannot be known yet (the GARCH chains run only where the ARCH
screen rejects, and the VAR only if a stable lag order exists) is marked provisional and
revised when the stage that decides it runs.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class StageSpec:
    """One execution stage of `Pipeline.run`, in order.

    `number`/`name` describe the *execution* order of the program. `checkpoint` is the
    Comp §5 checkpoint the stage records, and `methodology` the Part 5 section(s) it
    implements; the three are reported as separate fields because they are different
    numbering systems.
    """

    number: int
    key: str
    name: str
    checkpoint: str
    methodology: str
    operations: str


#: Every stage `Pipeline.run` executes, in its actual order. The specification stage runs
#: twice (the nonlinearity probe needs the BIC AR order; the STAR choice needs the probe),
#: so it appears twice with distinct keys.
STAGES: tuple[StageSpec, ...] = (
    StageSpec(1, "data", "Canonical input and modelling targets", "canonical_input",
              "Part 5 §2",
              "build monthly/quarterly panels, NBER chronology, data-audit tables T2.0-T2.1, "
              "growth targets, figure F2.0"),
    StageSpec(2, "stationarity", "Transformation and stationarity decisions",
              "stationarity_decisions", "Part 5 §3",
              "unit-root and stationarity batteries, §3.4 level/difference rule for the rate "
              "series, table T2.2, figures F2.1"),
    StageSpec(3, "specification_preliminary", "Preliminary specification (AR/ARMA orders)",
              "selected_specifications", "Part 5 §5.1-5.2, §9.2",
              "BIC AR and ARMA order selection on the initial window (probe order for "
              "stage 4)"),
    StageSpec(4, "nonlinearity", "Pre-estimation nonlinearity evidence",
              "nonlinearity_diagnostics", "Part 5 §4.1-4.2",
              "Tsay test, Teräsvirta STAR linearity and delay/type sequence, tables "
              "T2.3-T2.4"),
    StageSpec(5, "specification", "Final specification (MSAR and STAR fixed)",
              "selected_specifications", "Part 5 §5, §9.2",
              "fix AR, ARMA, MSAR (K=2), MSAR3 (K=3), STAR specifications; table T2.5"),
    StageSpec(6, "adequacy", "Full-sample in-sample adequacy and credibility",
              "model_fits", "Part 5 §7, §8",
              "full-sample AR, ARMA, MSAR, STAR, MSAR3 fits, residual battery, Hessian "
              "standard errors, credibility flags, tables T3.1-T3.2, figures F3.1-F3.3"),
    StageSpec(7, "forecasting", "Pseudo-out-of-sample rolling forecasts",
              "forecasts", "Part 5 §9",
              "re-estimate every model at every forecast origin on the rolling window and "
              "forecast the approved horizons"),
    StageSpec(8, "evaluation", "Forecast evaluation", "evaluation", "Part 5 §10",
              "accuracy, HLZ (primary), DM-HLN (secondary), model confidence set, "
              "state-conditioned losses and regressions, T3.3-T3.5"),
    StageSpec(9, "robustness", "Robustness exercises", "robustness", "Part 5 §11",
              "T4.1 transformation, T4.2 CPI lags, T4.3 K=3, T4.4 horizons, T4.5 VAR, "
              "T4.6 ARMA-GARCH, T4.8 window lengths, T4.9 LOCF exposure"),
    StageSpec(10, "finalize", "Registries, manifests and logs", "tables_and_figures",
              "Part 5 §13; Comp §5, §9",
              "failure registry T4.7, fit records, test table, claim matrix schema, run "
              "manifest, output inventory"),
)

STAGE_BY_KEY = {stage.key: stage for stage in STAGES}


@dataclass
class ChainPlan:
    """One planned rolling chain."""

    task_id: str
    batch: str
    stage: str                 # execution-stage key it runs in
    exercise: str              # "baseline", "T4.3 K=3", "T4.8 window length", ...
    role: str                  # "baseline" or "robustness"
    series: str
    model: str
    spec_label: str
    k_regimes: int | None
    window_length: int
    frequency: str
    horizons: tuple[int, ...]
    n_origins: int
    provisional: bool = False  # total not yet certain (see module docstring)
    expect_cached: bool = False  # an identical earlier chain will have filled the cache
    runs_in: str = "pool"      # "pool" (worker process) or "parent" (serial loop)

    def to_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["horizons"] = list(self.horizons)
        return out


@dataclass
class BatchPlan:
    """Chains launched together (one `_chains` call): they run concurrently."""

    batch: str
    stage: str
    chains: list[ChainPlan] = field(default_factory=list)
