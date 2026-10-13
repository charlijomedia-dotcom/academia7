"""AR and ARMA order selection (Part 5 §5.1-§5.2).

The selection rule is BIC first, then a residual-whiteness screen:

    1. rank candidates by BIC;
    2. among those whose residuals do not reject the primary Ljung-Box check at 5%,
       take the lowest BIC;
    3. if every candidate fails, keep the BIC minimum and mark the benchmark
       **diagnostically weak** rather than quietly accepting it.

Candidates are compared on a **common effective sample** (decision D2), because fitting
each order on all the observations it happens to allow would compare BIC values computed
from different numbers of observations.

The chosen order is fixed from the initial estimation window and is not re-searched at
later forecast origins (Part 5 §9.2).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from ..core.config import Config
from ..core.schemas import TestResult
from ..diagnostics.residual_tests import ljung_box
from ..models.ar import fit_ar
from ..models.arma import fit_arma


@dataclass
class SpecificationChoice:
    """A selected discrete specification and the evidence behind it."""

    series: str
    model: str
    order: Any
    bic: float
    residuals_white: bool
    diagnostically_weak: bool
    candidates: list[dict] = field(default_factory=list)
    note: str = ""

    def to_row(self) -> dict[str, Any]:
        return {
            "series_id": self.series,
            "model": self.model,
            "selected_order": str(self.order),
            "bic": self.bic,
            "primary_ljung_box_passes": self.residuals_white,
            "diagnostically_weak": self.diagnostically_weak,
            "note": self.note,
            "n_candidates": len(self.candidates),
        }


def select_ar_order(
    y: pd.Series, frequency: str, config: Config, *, series: str = ""
) -> SpecificationChoice:
    """Choose the AR lag order on the initial estimation window."""
    max_lag = int(config.get(f"specification.ar.max_lag.{frequency}"))
    primary_lag = int(config.get(f"specification.residual_screen.primary_lag.{frequency}"))
    # Common effective sample: every candidate is scored on the rows an AR(max_lag) allows.
    common = y.iloc[max_lag:]
    candidates = []

    for order in range(1, max_lag + 1):
        sample = y.iloc[max_lag - order :]
        try:
            fit = fit_ar(sample, order, series=series)
        except Exception as exc:
            candidates.append({"order": order, "bic": np.inf, "white": False,
                               "error": repr(exc)[:120]})
            continue
        if fit.n_obs != len(common):
            # Guard the common-sample invariant rather than trusting the slicing.
            raise AssertionError(
                f"AR({order}) scored on {fit.n_obs} observations, expected {len(common)}"
            )
        test = ljung_box(fit.residuals, primary_lag, model_dof=order,
                         dof_convention="ar_params", series=series, model="AR")
        candidates.append({
            "order": order, "bic": float(fit.bic),
            "white": test.decision_5pct == "do not reject",
            "ljung_box_p": test.p_value,
        })

    ranked = sorted(candidates, key=lambda c: (c["bic"], c["order"]))
    passing = [c for c in ranked if c.get("white")]
    if passing:
        chosen = passing[0]
        return SpecificationChoice(
            series=series, model="AR", order=chosen["order"], bic=chosen["bic"],
            residuals_white=True, diagnostically_weak=False, candidates=candidates,
            note="lowest BIC among candidates passing the primary Ljung-Box check",
        )
    chosen = ranked[0]
    return SpecificationChoice(
        series=series, model="AR", order=chosen["order"], bic=chosen["bic"],
        residuals_white=False, diagnostically_weak=True, candidates=candidates,
        note="every candidate failed the primary Ljung-Box check; BIC minimum retained and "
             "the linear benchmark is classified diagnostically weak (Part 5 §5.1)",
    )


def select_arma_order(
    y: pd.Series, frequency: str, config: Config, *, series: str = ""
) -> SpecificationChoice:
    """Choose the ARMA(p,q) order on the initial estimation window."""
    grid = config.get(f"specification.arma.grid.{frequency}")
    p_max, q_max = grid["p"][1], grid["q"][1]
    primary_lag = int(config.get(f"specification.residual_screen.primary_lag.{frequency}"))
    candidates = []

    for p in range(0, p_max + 1):
        for q in range(0, q_max + 1):
            if p == 0 and q == 0:
                continue                      # ARMA(0,0) is excluded by Part 5 §5.2
            try:
                fit = fit_arma(y, (p, q), series=series)
            except Exception as exc:
                candidates.append({"order": (p, q), "bic": np.inf, "white": False,
                                   "error": repr(exc)[:120]})
                continue
            if not np.isfinite(fit.bic) or not fit.record.converged:
                candidates.append({"order": (p, q), "bic": np.inf, "white": False,
                                   "error": "did not converge"})
                continue
            test = ljung_box(fit.residuals, primary_lag, model_dof=p + q,
                             dof_convention="p_plus_q", series=series, model="ARMA")
            candidates.append({
                "order": (p, q), "bic": float(fit.bic),
                "white": test.decision_5pct == "do not reject",
                "ljung_box_p": test.p_value,
                "degenerate": "pure AR" if q == 0 else ("pure MA" if p == 0 else ""),
            })

    ranked = sorted(candidates, key=lambda c: (c["bic"], sum(c["order"])))
    passing = [c for c in ranked if c.get("white")]
    chosen = passing[0] if passing else ranked[0]
    degenerate = chosen.get("degenerate", "")
    note = ("lowest BIC among candidates passing the primary Ljung-Box check"
            if passing else
            "every candidate failed the primary Ljung-Box check; BIC minimum retained")
    if degenerate:
        # Decision M4: allowed, but it must be visible in T2.5 that the "stronger
        # classical benchmark" collapsed to a pure AR or pure MA.
        note += f"; selected specification is {degenerate}"
    return SpecificationChoice(
        series=series, model="ARMA", order=chosen["order"], bic=chosen["bic"],
        residuals_white=bool(passing), diagnostically_weak=not passing,
        candidates=candidates, note=note,
    )
