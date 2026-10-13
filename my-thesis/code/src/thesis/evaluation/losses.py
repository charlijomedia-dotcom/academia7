"""Forecast loss functions and loss differentials.

Part 5 §10.1 uses squared-error and absolute-error loss, so no conclusion rests on one
arbitrary loss. Decision D12 fixes the sign convention once:

    d_t = loss(competitor) - loss(benchmark)

so a **negative** differential means the competitor is more accurate. Every table that
reports a differential states this.
"""

from __future__ import annotations

import numpy as np

SQUARED = "squared"
ABSOLUTE = "absolute"
LOSSES = (SQUARED, ABSOLUTE)

#: Stated on every output that carries a loss differential.
SIGN_CONVENTION = (
    "d_t = loss(competitor) - loss(benchmark); negative favours the competitor"
)


def loss(errors: np.ndarray, kind: str) -> np.ndarray:
    errors = np.asarray(errors, dtype=float)
    if kind == SQUARED:
        return errors**2
    if kind == ABSOLUTE:
        return np.abs(errors)
    raise ValueError(f"unknown loss {kind!r}; Part 5 §10.1 defines {LOSSES}")


def loss_differential(
    competitor_errors: np.ndarray, benchmark_errors: np.ndarray, kind: str
) -> np.ndarray:
    return loss(competitor_errors, kind) - loss(benchmark_errors, kind)
