"""Model Confidence Set (Part 5 §10.4, decision D11).

With four competing model classes, forcing a unique winner out of a table of pairwise
p-values would overstate what the data support. The MCS instead reports the set of models
that cannot be distinguished from the best at a chosen confidence level.

Settings are fixed by decision D11: Hansen-Lunde-Nason, method `R`, stationary bootstrap,
5,000 replications, block length ceil(sqrt(T_common)), fixed seed, run separately for
squared and absolute loss and for the 90% and 95% sets.

The loss matrix contains only admissible models on their common finite-loss dates
(decision M7), and `T_common` and the number of dates removed by alignment are reported.
When the procedure is numerically undefined the result is marked **unavailable** rather
than being filled in.
"""

from __future__ import annotations

import math
import warnings
from dataclasses import dataclass, field
from typing import Any, Mapping

import numpy as np
import pandas as pd

from ..core.config import Config
from . import alignment
from .losses import loss


@dataclass
class MCSResult:
    series: str
    horizon: int
    loss_kind: str
    confidence: float
    available: bool
    included: list[str] = field(default_factory=list)
    excluded: list[str] = field(default_factory=list)
    p_values: dict[str, float] = field(default_factory=dict)
    t_common: int = 0
    removed_by_alignment: dict[str, int] = field(default_factory=dict)
    block_length: int | None = None
    replications: int | None = None
    seed: int | None = None
    unavailable_reason: str = ""

    def to_rows(self) -> list[dict[str, Any]]:
        rows = []
        for model in sorted(set(self.included) | set(self.excluded) | set(self.p_values)):
            rows.append({
                "series": self.series,
                "horizon": self.horizon,
                "loss": self.loss_kind,
                "confidence_level": self.confidence,
                "model": model,
                "in_mcs": model in self.included,
                "mcs_p_value": self.p_values.get(model, float("nan")),
                "t_common": self.t_common,
                "n_removed_by_alignment": self.removed_by_alignment.get(model, 0),
                "block_length": self.block_length,
                "replications": self.replications,
                "seed": self.seed,
                "method": "R",
                "bootstrap": "stationary",
                "inference_available": self.available,
                "unavailable_reason": self.unavailable_reason,
            })
        if not rows:
            rows.append({
                "series": self.series, "horizon": self.horizon, "loss": self.loss_kind,
                "confidence_level": self.confidence, "model": "", "in_mcs": False,
                "mcs_p_value": float("nan"), "t_common": self.t_common,
                "inference_available": False, "unavailable_reason": self.unavailable_reason,
            })
        return rows


def model_confidence_set(
    frames: Mapping[str, pd.DataFrame],
    loss_kind: str,
    confidence: float,
    config: Config,
    *,
    series: str = "",
    horizon: int = 1,
) -> MCSResult:
    """Compute the MCS for one series, horizon, loss function and confidence level."""
    settings = config.get("evaluation.mcs")
    aligned = alignment.across_models(frames)
    result = MCSResult(series=series, horizon=horizon, loss_kind=loss_kind,
                       confidence=confidence, available=False,
                       t_common=aligned.n_common,
                       removed_by_alignment=aligned.removed,
                       replications=int(settings["replications"]),
                       seed=int(settings["seed"]))

    if len(frames) < 2:
        result.unavailable_reason = "fewer than two admissible models"
        return result
    if aligned.n_common < 20:
        result.unavailable_reason = (
            f"only {aligned.n_common} common finite-loss dates across the admissible models"
        )
        return result

    errors = alignment.aligned_errors(frames, aligned.dates)
    losses = pd.DataFrame({name: loss(values, loss_kind) for name, values in errors.items()},
                          index=aligned.dates)
    if not np.isfinite(losses.to_numpy()).all():
        result.unavailable_reason = "non-finite losses on the common dates"
        return result

    block_length = max(1, int(math.ceil(math.sqrt(aligned.n_common))))
    result.block_length = block_length
    try:
        from arch.bootstrap import MCS

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            procedure = MCS(
                losses,
                size=1.0 - confidence,
                reps=int(settings["replications"]),
                block_size=block_length,
                method=str(settings["method"]),
                bootstrap=str(settings["bootstrap"]),
                seed=int(settings["seed"]),
            )
            procedure.compute()
        result.included = [str(m) for m in procedure.included]
        result.excluded = [str(m) for m in procedure.excluded]
        p_values = procedure.pvalues
        result.p_values = {str(idx): float(row.iloc[0]) for idx, row in p_values.iterrows()}
        result.available = True
    except Exception as exc:
        result.unavailable_reason = f"MCS procedure failed: {exc!r}"[:200]
    return result
