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

Correction F2 (Part 8 audit). `arch` 8.0.0's `MCS._compute_r` fails on two numerical
conditions that arise when one admissible model (here: a fragile STAR with explosive
forecasts) has losses many orders of magnitude larger than the others:

1. **ties in the elimination statistic** -- when the dominant model's mean loss swamps
   every other model's in floating point, its standardised differences against several
   models are bit-identical, `np.argwhere(... == max)` returns several rows, and
   `loc.squeeze()[0]` then yields a *pair* of indices instead of the row model, which
   crashes the p-value formatting (`IndexError`);
2. **overflow of the bootstrap variance** -- squaring recentred bootstrap mean differences
   of order 1e200 overflows to `inf`, which silently zeroes the standardised statistics.

`hln_mcs_r` below re-implements the *identical* HLN R-method (same loss matrix, same
`arch` stationary-bootstrap index stream with the same block length, replications and
seed, same recentring, the same `+ I` variance guard, same max-t elimination statistic,
same p-value rule and the same monotone p-value accumulation) with exactly two numerical
changes, each active only when the `arch` arithmetic would break:

* a variance entry that is non-finite in the plain computation is recomputed with a
  per-pair scale factor (mathematically identical: mean((b/s)^2) * s^2);
* when the maximum standardised difference is attained at several cells, the eliminated
  model is the row model if all maximising cells share it; if they do not, the result is
  reported **unavailable** (no tie-breaking rule is invented).

`model_confidence_set` calls `arch` first and uses `hln_mcs_r` only when `arch` fails or
when its variances are non-finite; the implementation used is recorded in every row.
Equivalence with `arch` on every cell where `arch` succeeds is verified by tests and by
`reports/part8/corrections/f2_mcs_validation.csv`.
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
    implementation: str = "arch"
    implementation_note: str = ""

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
                "mcs_implementation": self.implementation,
                "mcs_implementation_note": self.implementation_note,
            })
        if not rows:
            rows.append({
                "series": self.series, "horizon": self.horizon, "loss": self.loss_kind,
                "confidence_level": self.confidence, "model": "", "in_mcs": False,
                "mcs_p_value": float("nan"), "t_common": self.t_common,
                "inference_available": False, "unavailable_reason": self.unavailable_reason,
                "mcs_implementation": self.implementation,
                "mcs_implementation_note": self.implementation_note,
            })
        return rows


class MCSNumericalError(RuntimeError):
    """The HLN elimination is numerically undefined for this loss matrix."""


def _bootstrap_indices(t: int, reps: int, block_size: int, seed: int) -> list[np.ndarray]:
    """The exact index stream `arch.bootstrap.MCS` uses for the stationary bootstrap."""
    from arch.bootstrap import StationaryBootstrap

    bootstrap = StationaryBootstrap(block_size, np.arange(t), seed=seed)
    # arch yields (positional, keyword) pairs; the first positional array is the index.
    return [np.asarray(data[0][0], dtype=int) for data in bootstrap.bootstrap(reps)]


def hln_mcs_r(losses: pd.DataFrame, size: float, reps: int, block_size: int,
              seed: int) -> tuple[pd.Series, list[str], list[str], dict[str, Any]]:
    """Hansen-Lunde-Nason MCS, method R, stationary bootstrap -- numerically guarded.

    Follows `arch.bootstrap.MCS._compute_r` (arch 8.0.0) operation for operation; see the
    module docstring for the two guarded conditions. Returns the MCS p-values indexed by
    model name, the included and excluded models (p > size included, as in `arch`), and
    diagnostics recording whether either guard was needed.
    """
    arr = np.asarray(losses, dtype=float)
    t, k = arr.shape
    if k < 2:
        raise ValueError("losses must have at least two columns")
    names = list(losses.columns)
    mean_losses = arr.mean(0)[:, None]
    loss_diffs = mean_losses - mean_losses.T
    boot = np.zeros((reps, k, k))
    with np.errstate(over="ignore", invalid="ignore"):
        for j, index in enumerate(_bootstrap_indices(t, reps, block_size, seed)):
            star = arr[index].mean(0)[:, None]
            boot[j] = star - star.T
        boot -= loss_diffs
        variances = (boot**2).mean(0)
    variances = variances + np.eye(k)          # arch's guard against division by zero
    with np.errstate(over="ignore", invalid="ignore"):
        scales = np.sqrt(variances)
    # Overflow guard: where the plain variance overflowed, compute its square root with a
    # per-pair scale s: sqrt(mean(b^2)) = sqrt(mean((b/s)^2)) * s. Identical mathematics,
    # and only cells that are non-finite in the plain arithmetic are touched, so every
    # cell arch computes finitely keeps arch's exact floating-point value.
    rescaled = ~np.isfinite(scales)
    for a, b in zip(*np.nonzero(rescaled)):
        column = boot[:, a, b]
        scale = float(np.max(np.abs(column)))
        if not np.isfinite(scale):
            raise MCSNumericalError("non-finite bootstrap mean differences")
        extra = 1.0 if a == b else 0.0
        scales[a, b] = math.sqrt(float(np.mean((column / scale) ** 2)) + (extra / scale) / scale) * scale
    if not np.isfinite(scales).all() or not np.isfinite(loss_diffs).all():
        raise MCSNumericalError("non-finite loss differences or variances after rescaling")
    with np.errstate(divide="ignore", invalid="ignore"):
        std_loss_diffs = loss_diffs / scales
        std_boot = boot / scales
    if np.isnan(std_loss_diffs).any() or np.isnan(std_boot).any():
        raise MCSNumericalError("undefined standardised loss differences (0/0)")

    included = np.ones(k, dtype=bool)
    eliminated: list[tuple[int, float]] = []
    ties = 0
    while included.sum() > 1:
        indices = np.argwhere(included)
        sub = std_loss_diffs[indices, indices.T]
        test_stat = np.max(sub)
        simulated = np.max(np.max(std_boot[:, indices, indices.T], 2), 1)
        p_value = float((test_stat < simulated).mean())
        loc = np.argwhere(sub == test_stat)
        rows = set(int(r) for r in loc[:, 0])
        if len(rows) > 1:
            raise MCSNumericalError(
                "maximum standardised difference attained by several different models; "
                "the elimination is not uniquely defined")
        if loc.shape[0] > 1:
            ties += 1
        i = int(loc[0, 0])
        eliminated.append((int(indices.flat[i]), p_value))
        included[indices.flat[i]] = False
    eliminated.extend((int(ind), 1.0) for ind in np.argwhere(included).flatten())

    order = [names[i] for i, _ in eliminated]
    running, values = -np.inf, []
    for _, p in eliminated:
        running = max(running, p)
        values.append(running)
    p_values = pd.Series(values, index=order, name="Pvalue")
    inc = sorted(p_values.index[p_values > size])
    exc = sorted(p_values.index[p_values <= size])
    diagnostics = {"rescaled_variance_cells": int(rescaled.sum()),
                   "tied_elimination_steps": ties}
    return p_values, inc, exc, diagnostics


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
    arch_error = ""
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
        variances = getattr(procedure, "_variances", None)
        if variances is not None and not np.isfinite(np.asarray(variances)).all():
            # arch completed, but on an overflowed variance its statistics are invalid.
            raise MCSNumericalError("arch bootstrap variance overflowed")
        result.available = True
        return result
    except Exception as exc:  # noqa: BLE001 - recorded, then the guarded implementation
        arch_error = f"{exc!r}"[:160]
        result.included, result.excluded, result.p_values = [], [], {}

    try:
        p_values, included, excluded, diagnostics = hln_mcs_r(
            losses, 1.0 - confidence, int(settings["replications"]), block_length,
            int(settings["seed"]))
    except MCSNumericalError as exc:
        result.implementation = "unavailable"
        result.unavailable_reason = (f"MCS procedure failed: arch {arch_error}; "
                                     f"guarded HLN R-method: {exc}")[:300]
        return result
    result.included = [str(m) for m in included]
    result.excluded = [str(m) for m in excluded]
    result.p_values = {str(m): float(v) for m, v in p_values.items()}
    result.available = True
    result.implementation = "hln_mcs_r (guarded; arch failed)"
    result.implementation_note = (
        f"arch error: {arch_error}; rescaled variance cells: "
        f"{diagnostics['rescaled_variance_cells']}; tied elimination steps resolved by the "
        f"common row model: {diagnostics['tied_elimination_steps']}")[:300]
    return result
