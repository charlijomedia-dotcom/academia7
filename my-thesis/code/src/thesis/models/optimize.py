"""Shared optimizer bookkeeping: multistart selection and numerical derivatives.

Two things the nonlinear estimators need and must do identically.

**Multistart selection.** A start that reports failure may still end at the lowest
objective of all the starts tried, and simply taking the lowest objective then reports a
non-converged point as the estimate. Hamilton (1989, footnote 7) is explicit that the
estimates he reports come from a routine whose "convergence to the global maximum proved
relatively robust with respect to a broad range of start-up values", and Teräsvirta
(1994, sec. 5) says that if the algorithm does not converge the estimation should be
carried out using a grid, not that the best non-converged point should be adopted. So the
rule here is: prefer the best admissible **converged** solution; fall back to a
non-converged one only when nothing converged, and say so in the record rather than
letting it pass as an estimate.

**Numerical derivatives.** Hamilton (1989, Table I and footnote 7) obtains asymptotic
standard errors from numerical second derivatives of the log-likelihood. The Hessian here
is a central-difference approximation, symmetrized, with a step scaled to each parameter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

import numpy as np

#: Chosen because the objective is a sum of log densities evaluated in double precision:
#: the central-difference truncation error falls as h² while the rounding error grows as
#: 1/h², so h ~ eps^(1/4) balances them for a second derivative.
DEFAULT_STEP = float(np.finfo(float).eps ** 0.25)


@dataclass(frozen=True)
class StartAttempt:
    """One optimizer start, kept whether it succeeded or not (Part 5 §8.3)."""

    label: str
    objective: float
    converged: bool
    message: str
    x: np.ndarray | None = None

    @property
    def admissible(self) -> bool:
        return self.x is not None and np.isfinite(self.objective)

    def to_row(self) -> dict[str, Any]:
        return {
            "start": self.label,
            "objective": self.objective,
            "converged": self.converged,
            "message": self.message[:200],
        }


@dataclass
class MultistartOutcome:
    """The chosen solution and the complete audit trail of what was tried."""

    attempts: list[StartAttempt] = field(default_factory=list)
    chosen: StartAttempt | None = None
    used_unconverged: bool = False

    @property
    def any_converged(self) -> bool:
        return any(a.converged and a.admissible for a in self.attempts)

    @property
    def selection_rule(self) -> str:
        if self.chosen is None:
            return "no admissible solution"
        if self.used_unconverged:
            return "lowest objective among admissible starts; none reported convergence"
        return "lowest objective among admissible starts that reported convergence"

    def summary(self) -> dict[str, Any]:
        return {
            "n_starts": len(self.attempts),
            "n_admissible": sum(1 for a in self.attempts if a.admissible),
            "n_converged": sum(1 for a in self.attempts if a.converged and a.admissible),
            "selection_rule": self.selection_rule,
            "starts": "; ".join(
                f"{a.label}:obj={a.objective:.6g},conv={a.converged}"
                if np.isfinite(a.objective) else f"{a.label}:obj=nonfinite"
                for a in self.attempts
            )[:1000],
        }


def select_best(attempts: Sequence[StartAttempt]) -> MultistartOutcome:
    """Prefer the best converged admissible start; fall back only if none converged."""
    outcome = MultistartOutcome(attempts=list(attempts))
    admissible = [a for a in attempts if a.admissible]
    if not admissible:
        return outcome
    converged = [a for a in admissible if a.converged]
    if converged:
        outcome.chosen = min(converged, key=lambda a: a.objective)
    else:
        outcome.chosen = min(admissible, key=lambda a: a.objective)
        outcome.used_unconverged = True
    return outcome


def numerical_hessian(
    function: Callable[[np.ndarray], float],
    x: np.ndarray,
    *,
    step: float = DEFAULT_STEP,
) -> np.ndarray:
    """Central-difference Hessian of `function` at `x`, symmetrized.

    The per-parameter step is `step * max(|x_i|, 1)`, so a parameter of order 100 and one
    of order 0.01 are both differenced on their own scale.
    """
    x = np.asarray(x, dtype=float)
    n = x.size
    h = step * np.maximum(np.abs(x), 1.0)
    hessian = np.empty((n, n), dtype=float)
    f0 = float(function(x))
    if not np.isfinite(f0):
        return np.full((n, n), np.nan)

    for i in range(n):
        for j in range(i, n):
            if i == j:
                step_i = np.zeros(n)
                step_i[i] = h[i]
                forward = float(function(x + step_i))
                backward = float(function(x - step_i))
                value = (forward - 2.0 * f0 + backward) / (h[i] ** 2)
            else:
                step_i = np.zeros(n)
                step_j = np.zeros(n)
                step_i[i] = h[i]
                step_j[j] = h[j]
                plus_plus = float(function(x + step_i + step_j))
                plus_minus = float(function(x + step_i - step_j))
                minus_plus = float(function(x - step_i + step_j))
                minus_minus = float(function(x - step_i - step_j))
                value = (plus_plus - plus_minus - minus_plus + minus_minus) / (
                    4.0 * h[i] * h[j]
                )
            hessian[i, j] = hessian[j, i] = value
    return hessian


def numerical_jacobian(
    function: Callable[[np.ndarray], np.ndarray],
    x: np.ndarray,
    *,
    step: float = float(np.finfo(float).eps ** (1.0 / 3.0)),
) -> np.ndarray:
    """Central-difference Jacobian of a vector-valued `function` at `x`.

    A first derivative balances truncation against rounding at h ~ eps^(1/3), which is
    why the default step differs from the Hessian's.
    """
    x = np.asarray(x, dtype=float)
    base = np.asarray(function(x), dtype=float)
    jacobian = np.empty((base.size, x.size), dtype=float)
    h = step * np.maximum(np.abs(x), 1.0)
    for i in range(x.size):
        offset = np.zeros(x.size)
        offset[i] = h[i]
        forward = np.asarray(function(x + offset), dtype=float)
        backward = np.asarray(function(x - offset), dtype=float)
        jacobian[:, i] = (forward - backward) / (2.0 * h[i])
    return jacobian


def covariance_from_hessian(hessian: np.ndarray) -> tuple[np.ndarray, str]:
    """Invert an observed-information matrix, reporting why if it cannot be used.

    Returns the covariance and a reason string, empty when the inversion succeeded. A
    matrix that cannot be inverted, or whose inverse has a non-positive diagonal, is an
    unreliable-inference condition, not an estimation failure: the point estimates stand
    and the standard errors do not. Part 5 §7.5 keeps those two apart.
    """
    hessian = np.asarray(hessian, dtype=float)
    if hessian.size == 0 or not np.isfinite(hessian).all():
        return np.full_like(hessian, np.nan), "non-finite observed information"
    symmetric = (hessian + hessian.T) / 2.0
    try:
        covariance = np.linalg.inv(symmetric)
    except np.linalg.LinAlgError:
        return np.full_like(symmetric, np.nan), "observed information is singular"
    if not np.isfinite(covariance).all():
        return covariance, "non-finite covariance"
    if np.any(np.diag(covariance) <= 0):
        return covariance, "non-positive variance on the diagonal"
    return covariance, ""


def standard_errors(covariance: np.ndarray) -> np.ndarray:
    """Square roots of the covariance diagonal, NaN where the variance is not positive."""
    diagonal = np.diag(np.asarray(covariance, dtype=float)).astype(float)
    out = np.full(diagonal.shape, np.nan)
    positive = np.isfinite(diagonal) & (diagonal > 0)
    out[positive] = np.sqrt(diagonal[positive])
    return out


def delta_method(jacobian: np.ndarray, covariance: np.ndarray) -> np.ndarray:
    """Covariance of g(theta) from the Jacobian of g and the covariance of theta."""
    jacobian = np.asarray(jacobian, dtype=float)
    covariance = np.asarray(covariance, dtype=float)
    return jacobian @ covariance @ jacobian.T
