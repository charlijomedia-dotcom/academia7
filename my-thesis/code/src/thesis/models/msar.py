"""Markov-switching autoregression, Hamilton-style (Part 5 §5.5).

    y_t = mu_{s_t} + sum_j phi_j (y_{t-j} - mu_{s_{t-j}}) + e_t,   e_t ~ N(0, sigma^2)

with s_t a first-order K-state Markov chain. Regime-specific means, **common** AR
coefficients and a **common** innovation variance: deliberately close to Hamilton's
canonical business-cycle specification, so the question is whether discrete shifts in the
conditional mean add forecasting information, not whether an unrestricted switching model
can be made to fit.

Written from scratch rather than wrapped around a library because the thesis needs exact
out-of-sample conditional means at every forecast origin, which the standard
implementations do not expose.

The mean-adjusted series x_t = y_t - mu_{s_t} follows a *linear* AR(p). That identity is
what makes the h-step conditional mean exact:

    E[y_{t+h} | I_t] = sum_z P(z_t | I_t) * AR_iterate_h(x(z)) + sum_k P(s_{t+h}=k | I_t) * mu_k

The filter runs over the expanded state z_t = (s_t, ..., s_{t-p}), which is what makes the
lagged means in the equation well defined.
"""

from __future__ import annotations

import itertools
import time
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from ..core.schemas import FitRecord, ReasonCode, Status

_LOG_2PI = float(np.log(2.0 * np.pi))


def _expanded_states(k_regimes: int, order: int) -> list[tuple[int, ...]]:
    return list(itertools.product(range(k_regimes), repeat=order + 1))


def _expanded_transition(P: np.ndarray, states: list[tuple[int, ...]]) -> np.ndarray:
    """Transition matrix over expanded states, zero where the lag history is inconsistent."""
    n = len(states)
    index = {state: i for i, state in enumerate(states)}
    T = np.zeros((n, n))
    for i, state in enumerate(states):
        for k in range(P.shape[0]):
            successor = (k,) + state[:-1]
            T[i, index[successor]] = P[state[0], k]
    return T


def _stationary(T: np.ndarray, iterations: int = 2000) -> np.ndarray:
    """Stationary distribution by power iteration: robust and dependency-free."""
    probabilities = np.full(T.shape[0], 1.0 / T.shape[0])
    for _ in range(iterations):
        updated = probabilities @ T
        total = updated.sum()
        if total <= 0 or not np.isfinite(total):
            return np.full(T.shape[0], 1.0 / T.shape[0])
        updated = updated / total
        if np.max(np.abs(updated - probabilities)) < 1e-14:
            return updated
        probabilities = updated
    return probabilities


def _unpack(theta: np.ndarray, k_regimes: int, order: int):
    mu = theta[:k_regimes]
    phi = theta[k_regimes : k_regimes + order]
    sigma = float(np.exp(theta[k_regimes + order]))
    logits = theta[k_regimes + order + 1 :].reshape(k_regimes, k_regimes - 1)
    P = np.empty((k_regimes, k_regimes))
    for k in range(k_regimes):
        exponentials = np.exp(np.clip(logits[k], -30.0, 30.0))
        denominator = 1.0 + exponentials.sum()
        off = exponentials / denominator
        column = 0
        for j in range(k_regimes):
            if j == k:
                P[k, j] = 1.0 / denominator
            else:
                P[k, j] = off[column]
                column += 1
    return mu, phi, sigma, P


def _pack(mu, phi, sigma, P) -> np.ndarray:
    k_regimes = len(mu)
    logits = []
    for k in range(k_regimes):
        diagonal = max(P[k, k], 1e-8)
        for j in range(k_regimes):
            if j != k:
                logits.append(np.log(max(P[k, j], 1e-8) / diagonal))
    return np.concatenate([np.asarray(mu, float), np.asarray(phi, float),
                           [np.log(max(sigma, 1e-8))], np.asarray(logits, float)])


def _state_constants(mu: np.ndarray, phi: np.ndarray, states: list[tuple[int, ...]]) -> np.ndarray:
    """The part of each expanded state's conditional mean that does not depend on t.

    Because the AR coefficients are common across regimes, the conditional mean splits:

        E[y_t | z] = mu_{s_t} - phi'mu_{lags(z)}  +  phi' y_{t-1:t-p}

    Only the first term depends on the state, and only the second depends on time.
    Precomputing the state-dependent constant turns the filter's inner loop over
    K^(p+1) states into one vector addition.
    """
    order = len(phi)
    lag_means = np.array([[mu[k] for k in state[1:]] for state in states], dtype=float)
    head = np.array([mu[state[0]] for state in states], dtype=float)
    return head - (lag_means @ phi if order else 0.0)


def _filter(y: np.ndarray, mu, phi, sigma, P, states, T):
    """Hamilton filter over the expanded state. Returns (loglik, filtered probabilities)."""
    order = len(phi)
    n = y.size
    filtered = np.zeros((n - order, len(states)))
    probabilities = _stationary(T)
    loglik = 0.0
    variance = sigma**2
    normalizer = np.sqrt(2 * np.pi * variance)

    mu_array = np.asarray(mu, float)
    constants = _state_constants(mu_array, np.asarray(phi, float), states)

    for position, t in enumerate(range(order, n)):
        ar_term = float(phi @ y[t - order : t][::-1]) if order else 0.0
        means = constants + ar_term
        predicted = probabilities @ T
        density = np.exp(-0.5 * ((y[t] - means) ** 2) / variance) / normalizer
        joint = predicted * density
        total = joint.sum()
        if not np.isfinite(total) or total <= 0:
            return -np.inf, filtered, None
        loglik += float(np.log(total))
        probabilities = joint / total
        filtered[position] = probabilities
    return loglik, filtered, None


def _negative_loglik(theta, y, k_regimes, order, states):
    mu, phi, sigma, P = _unpack(theta, k_regimes, order)
    if sigma <= 0 or not np.isfinite(sigma):
        return 1e12
    if order and np.max(np.abs(np.roots(np.r_[1.0, -phi]))) >= 1.0:
        return 1e12          # keep the mean-adjusted AR stationary
    T = _expanded_transition(P, states)
    loglik, _, _ = _filter(y, mu, phi, sigma, P, states, T)
    return -loglik if np.isfinite(loglik) else 1e12


def _smooth(filtered: np.ndarray, T: np.ndarray) -> np.ndarray:
    """Kim smoother over expanded states."""
    n, n_states = filtered.shape
    smoothed = np.zeros_like(filtered)
    smoothed[-1] = filtered[-1]
    for t in range(n - 2, -1, -1):
        predicted = filtered[t] @ T
        safe = np.where(predicted > 0, predicted, 1.0)
        smoothed[t] = filtered[t] * ((smoothed[t + 1] / safe) @ T.T)
        total = smoothed[t].sum()
        if total > 0:
            smoothed[t] /= total
    return smoothed


@dataclass
class MSARFit:
    k_regimes: int
    order: int
    mu: np.ndarray
    phi: np.ndarray
    sigma: float
    P: np.ndarray
    loglik: float
    aic: float
    bic: float
    n_obs: int
    filtered: np.ndarray
    smoothed_regime: np.ndarray        # (T, K) marginal smoothed probabilities
    occupancy: np.ndarray
    expected_duration: np.ndarray
    record: FitRecord
    states: list[tuple[int, ...]] = field(default_factory=list)
    _y: np.ndarray = field(default_factory=lambda: np.empty(0))

    @property
    def theta(self) -> np.ndarray:
        return _pack(self.mu, self.phi, self.sigma, self.P)

    def one_step_residuals(self) -> np.ndarray:
        """In-sample one-step prediction errors, for the §7.3 residual battery.

        The prediction at t uses the state probabilities implied by information through
        t-1, so these are genuine one-step-ahead errors rather than smoothed fitted
        values. Length is n - p, aligned on y[p:].
        """
        order, y = self.order, self._y
        T = _expanded_transition(self.P, self.states)
        constants = _state_constants(np.asarray(self.mu, float),
                                     np.asarray(self.phi, float), self.states)
        probabilities = _stationary(T)
        out = np.empty(y.size - order)
        for position, t in enumerate(range(order, y.size)):
            ar_term = float(self.phi @ y[t - order : t][::-1]) if order else 0.0
            predicted_states = probabilities @ T
            out[position] = y[t] - float(predicted_states @ (constants + ar_term))
            probabilities = self.filtered[position]
        return out

    def fitted_values(self) -> np.ndarray:
        """One-step-ahead conditional means, aligned on y[p:]."""
        return self._y[self.order:] - self.one_step_residuals()

    def forecast(self, horizon: int = 1) -> np.ndarray:
        """Exact h-step conditional means via the state-probability recursion.

        Uses the mean-adjusted linear AR identity, so no simulation is needed and the
        answer is the true conditional expectation rather than an approximation.
        """
        order, k = self.order, self.k_regimes
        T = _expanded_transition(self.P, self.states)
        probabilities = self.filtered[-1]
        y = self._y

        # Mean-adjusted history for each expanded state: x_T, ..., x_{T-p+1}.
        lagged = y[-order:][::-1] if order else np.empty(0)
        out = np.empty(horizon)
        # Regime probabilities h steps ahead, marginalized from the expanded chain.
        state_probabilities = probabilities.copy()
        for step in range(1, horizon + 1):
            state_probabilities = state_probabilities @ T
            regime = np.zeros(k)
            for i, state in enumerate(self.states):
                regime[state[0]] += state_probabilities[i]

            if order:
                # x_t, ..., x_{t-p+1} for every expanded state, then iterate the linear
                # AR forward `step` times, vectorized across states.
                state_means = np.array(
                    [[self.mu[k] for k in state[:order]] for state in self.states], dtype=float
                )
                history = lagged[None, :] - state_means          # (n_states, order)
                for _ in range(step):
                    nxt = history @ self.phi
                    history = np.column_stack([nxt, history[:, :-1]])
                expected_x = float(probabilities @ history[:, 0])
            else:
                expected_x = 0.0
            out[step - 1] = expected_x + float(regime @ self.mu)
        return out


def fit_msar(
    y: pd.Series,
    order: int,
    k_regimes: int,
    *,
    series: str = "",
    refit_date: str = "",
    spec_hash: str = "",
    warm_start: np.ndarray | None = None,
    maxiter: int = 400,
) -> MSARFit:
    """Estimate the mean-switching MSAR by maximum likelihood.

    Deterministic multi-starts (decision D6); the warm start from the previous successful
    refit is tried first when supplied, with the deterministic starts as fallback, and the
    start that won is recorded (Comp §7).
    """
    started = time.perf_counter()
    values = y.to_numpy(dtype=float)
    states = _expanded_states(k_regimes, order)
    record = FitRecord(
        series=series or (y.name or ""),
        model=f"MSAR{k_regimes}",
        spec_label=f"p={order},K={k_regimes}",
        spec_hash=spec_hash,
        window_start=str(pd.DatetimeIndex(y.index)[0].date()),
        window_end=str(pd.DatetimeIndex(y.index)[-1].date()),
        refit_date=refit_date,
        converged=False,
    )

    # Deterministic starts: regime means at spread percentiles, AR from OLS on the
    # demeaned series, two levels of persistence.
    percentiles = np.linspace(100.0 / (k_regimes + 1), 100.0 - 100.0 / (k_regimes + 1), k_regimes)
    mu0 = np.percentile(values, percentiles)
    demeaned = values - values.mean()
    if order:
        design = np.column_stack([demeaned[order - j - 1 : -j - 1] for j in range(order)])
        phi0, *_ = np.linalg.lstsq(design, demeaned[order:], rcond=None)
        phi0 = np.clip(phi0, -0.95, 0.95)
    else:
        phi0 = np.empty(0)
    sigma0 = float(np.std(values, ddof=1))

    starts: list[tuple[str, np.ndarray]] = []
    if warm_start is not None and warm_start.size == k_regimes + order + 1 + k_regimes * (k_regimes - 1):
        starts.append(("warm", np.asarray(warm_start, float)))
    for diagonal in (0.90, 0.95):
        P0 = np.full((k_regimes, k_regimes), (1 - diagonal) / (k_regimes - 1))
        np.fill_diagonal(P0, diagonal)
        starts.append((f"deterministic_p{diagonal}", _pack(mu0, phi0, sigma0, P0)))

    best, best_label = None, ""
    for label, theta0 in starts:
        try:
            result = minimize(
                _negative_loglik, theta0, args=(values, k_regimes, order, states),
                method="L-BFGS-B", options={"maxiter": maxiter},
            )
        except Exception:
            continue
        if not np.isfinite(result.fun):
            continue
        if best is None or result.fun < best.fun:
            best, best_label = result, label

    if best is None:
        record.add_flag(ReasonCode.NONCONVERGENCE, Status.FAILED, detail="no start converged")
        record.wall_seconds = time.perf_counter() - started
        return MSARFit(k_regimes, order, np.empty(0), np.empty(0), np.nan,
                       np.empty((0, 0)), np.nan, np.nan, np.nan, 0,
                       np.empty((0, 0)), np.empty((0, 0)), np.empty(0), np.empty(0),
                       record, states, values)

    mu, phi, sigma, P = _unpack(best.x, k_regimes, order)
    # Label switching is resolved by one fixed documented rule: order by regime mean
    # (Part 5 §8.1).
    ordering = np.argsort(mu)
    mu = mu[ordering]
    P = P[np.ix_(ordering, ordering)]

    T = _expanded_transition(P, states)
    loglik, filtered, _ = _filter(values, mu, phi, sigma, P, states, T)
    smoothed = _smooth(filtered, T)
    regime_smoothed = np.zeros((smoothed.shape[0], k_regimes))
    for i, state in enumerate(states):
        regime_smoothed[:, state[0]] += smoothed[:, i]

    occupancy = regime_smoothed.mean(axis=0)
    with np.errstate(divide="ignore"):
        duration = 1.0 / np.clip(1.0 - np.diag(P), 1e-12, None)

    n_params = k_regimes + order + 1 + k_regimes * (k_regimes - 1)
    n_obs = values.size - order
    record.converged = bool(best.success)
    record.optimizer_message = str(best.message)[:200]
    record.start_used = best_label
    record.loglik = float(loglik)
    record.aic = float(-2 * loglik + 2 * n_params)
    record.bic = float(-2 * loglik + n_params * np.log(n_obs))
    record.n_obs = n_obs
    record.params = {
        **{f"mu{k+1}": float(mu[k]) for k in range(k_regimes)},
        **{f"phi{j+1}": float(phi[j]) for j in range(order)},
        "sigma": float(sigma),
        **{f"p{i+1}{j+1}": float(P[i, j]) for i in range(k_regimes) for j in range(k_regimes)},
    }
    record.diagnostics.update(
        {
            "occupancy": ";".join(f"{v:.4f}" for v in occupancy),
            "expected_duration": ";".join(f"{v:.2f}" for v in duration),
            "n_params": n_params,
        }
    )
    record.wall_seconds = time.perf_counter() - started
    if not best.success:
        record.add_flag(ReasonCode.NONCONVERGENCE, Status.FAILED, detail=str(best.message)[:120])
    if not np.isfinite(loglik):
        record.add_flag(ReasonCode.NONFINITE, Status.FAILED)

    return MSARFit(
        k_regimes=k_regimes, order=order, mu=mu, phi=phi, sigma=sigma, P=P,
        loglik=float(loglik), aic=record.aic, bic=record.bic, n_obs=n_obs,
        filtered=filtered, smoothed_regime=regime_smoothed, occupancy=occupancy,
        expected_duration=duration, record=record, states=states, _y=values,
    )
