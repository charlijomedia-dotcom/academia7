"""One interface over the model families, so the forecasting engine stays simple.

Each family is fitted on an estimation window and asked for forecasts at the approved
horizons. The multi-step rule differs by family and is fixed by the methodology, not by
convenience:

* AR, ARMA, VAR: iterated from the estimated dynamics (Part 5 §9.4);
* MSAR: the exact state-probability recursion;
* STAR: residual-bootstrap conditional mean, analytic at h=1 (decision M2).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from ..core.config import Config
from ..core.schemas import FitRecord, Status
from ..models import flags
from ..models.ar import fit_ar
from ..models.arma import fit_arma
from ..models.msar import fit_msar
from ..models.star import fit_star
from ..forecasting.simulate import star_bootstrap_forecast, star_skeleton_forecast

AR = "AR"
ARMA = "ARMA"
MSAR = "MSAR"
MSAR3 = "MSAR3"
STAR = "STAR"
CORE_MODELS = (AR, ARMA, MSAR, STAR)


@dataclass(frozen=True)
class ModelSpec:
    """A discrete specification, fixed from the initial window and then held constant."""

    model: str
    order: int = 0
    ma_order: int = 0
    k_regimes: int = 2
    kind: str = "LSTAR"
    delay: int = 1

    @property
    def label(self) -> str:
        if self.model == AR:
            return f"AR(p={self.order})"
        if self.model == ARMA:
            return f"ARMA(p={self.order},q={self.ma_order})"
        if self.model in (MSAR, MSAR3):
            return f"MSAR(p={self.order},K={self.k_regimes})"
        if self.model == STAR:
            return f"STAR({self.kind},p={self.order},d={self.delay})"
        return self.model

    def as_dict(self) -> dict[str, Any]:
        return {
            "model": self.model, "order": self.order, "ma_order": self.ma_order,
            "k_regimes": self.k_regimes, "kind": self.kind, "delay": self.delay,
        }


@dataclass
class FitOutcome:
    """A fitted model, its forecasts, and everything needed to audit both."""

    spec: ModelSpec
    record: FitRecord
    forecasts: dict[int, float] = field(default_factory=dict)
    warm_payload: Any = None
    seed_provenance: dict[str, Any] = field(default_factory=dict)
    skeleton_forecasts: dict[int, float] = field(default_factory=dict)
    fit: Any = None

    @property
    def usable(self) -> bool:
        return self.record.status is not Status.FAILED


def fit_and_forecast(
    spec: ModelSpec,
    window: pd.Series,
    horizons: list[int],
    config: Config,
    *,
    frequency: str = "M",
    series: str = "",
    refit_date: str = "",
    warm_start: Any = None,
    seed_key: Any = None,
) -> FitOutcome:
    """Fit one model on one window and produce the approved forecasts."""
    horizons = sorted(set(int(h) for h in horizons))
    longest = max(horizons)
    master_seed = int(config.get("run.master_seed"))
    values = window.to_numpy(dtype=float)

    if spec.model == AR:
        fit = fit_ar(window, spec.order, series=series, refit_date=refit_date)
        path = fit.forecast(window, longest)
        outcome = FitOutcome(spec, fit.record, {h: float(path[h - 1]) for h in horizons}, fit=fit)

    elif spec.model == ARMA:
        fit = fit_arma(window, (spec.order, spec.ma_order), series=series, refit_date=refit_date)
        if fit.record.status is Status.FAILED:
            outcome = FitOutcome(spec, fit.record, {}, fit=fit)
        else:
            path = fit.forecast(longest)
            outcome = FitOutcome(spec, fit.record, {h: float(path[h - 1]) for h in horizons}, fit=fit)

    elif spec.model in (MSAR, MSAR3):
        fit = fit_msar(window, spec.order, spec.k_regimes, series=series,
                       refit_date=refit_date, warm_start=warm_start)
        flags.apply_msar_flags(fit.record, fit, config)
        if fit.record.status is Status.FAILED:
            outcome = FitOutcome(spec, fit.record, {}, fit=fit)
        else:
            path = fit.forecast(longest)
            outcome = FitOutcome(spec, fit.record, {h: float(path[h - 1]) for h in horizons},
                                 warm_payload=fit.theta, fit=fit)

    elif spec.model == STAR:
        fit = fit_star(window, spec.order, spec.delay, spec.kind, config,
                       series=series, refit_date=refit_date, warm_start=warm_start)
        flags.apply_star_flags(fit.record, fit, config)
        if fit.record.status is Status.FAILED:
            outcome = FitOutcome(spec, fit.record, {}, fit=fit)
        else:
            settings = config.get("forecasting.star_multistep")
            forecasts: dict[int, float] = {}
            provenance: dict[str, Any] = {}
            if 1 in horizons and settings.get("analytic_at_h1", True):
                forecasts[1] = float(fit.forecast_one(values))
            longer = [h for h in horizons if h > 1]
            if longer:
                means, provenance = star_bootstrap_forecast(
                    fit, values, max(longer),
                    paths=int(settings["paths"]),
                    seed_key=seed_key or {"series": series, "model": STAR, "origin": refit_date},
                    master_seed=master_seed,
                )
                for h in longer:
                    forecasts[h] = float(means[h - 1])
            skeleton = {}
            if settings.get("skeleton_diagnostic", False):
                path = star_skeleton_forecast(fit, values, longest)
                skeleton = {h: float(path[h - 1]) for h in horizons}
            outcome = FitOutcome(spec, fit.record, forecasts, warm_payload=(fit.gamma, fit.c),
                                 seed_provenance=provenance, skeleton_forecasts=skeleton, fit=fit)
    else:
        raise ValueError(f"unknown model {spec.model!r}")

    # The specification is the single source of a model's identity across every table.
    # An estimator that labelled itself differently (MSAR2 for the K=2 baseline, say)
    # would make MSAR and MSAR2 appear as two models in the registries and break the
    # cross-table joins Part 8 depends on. The regime count is carried by spec_label.
    outcome.record.model = spec.model

    # An extreme but finite forecast is a warning for the figures and registry; it is
    # never deleted and never turns the fit into a failure (decision D8).
    for horizon, value in outcome.forecasts.items():
        flags.flag_extreme_forecast(outcome.record, value, values, config)
    return outcome
