"""Pre-estimation nonlinearity evidence (Part 5 §4).

Nonlinearity is treated as an empirical hypothesis, not a label attached after a nonlinear
model happens to fit. Two established procedures are used:

* **Tsay (1986)** quadratic nonlinearity test, a general check for departure from linear
  autoregressive dynamics (decision D3: all unique quadratic lag terms, orthogonalized
  against the linear design, assessed by the nested F test);
* the **Luukkonen-Saikkonen-Teräsvirta / Teräsvirta (1994)** sequence, which tests
  linearity against STAR alternatives, selects the delay, and chooses LSTAR versus ESTAR
  (decision D4).

Part 5 §4.4 is explicit that these results affect *interpretation* only. A failure to
reject linearity does not remove STAR or MSAR from the predeclared forecast comparison; it
limits what a later transition can be claimed to prove.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats

from ..core.config import Config
from ..core.schemas import TestResult

SIGNIFICANCE = 0.05


def _ar_design(y: np.ndarray, order: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows = np.arange(order, y.size)
    X = np.column_stack([np.ones(rows.size)] + [y[rows - j] for j in range(1, order + 1)])
    return y[rows], X, rows


def _ols_residuals(y: np.ndarray, X: np.ndarray) -> np.ndarray:
    coefficients, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ coefficients


def tsay_test(y: pd.Series, order: int, *, series: str = "") -> TestResult:
    """Tsay (1986) test for quadratic nonlinearity. H0: linear autoregression.

    The m = p(p+1)/2 unique cross-products of the lagged values are regressed on the
    linear design and their residuals retained, so the added regressors are orthogonal to
    the linear part. The nested F statistic then compares the residual sums of squares.
    """
    values = y.to_numpy(dtype=float)
    dependent, X, rows = _ar_design(values, order)
    n = dependent.size

    # All unique quadratic terms y_{t-i} * y_{t-j}, 1 <= i <= j <= p.
    quadratic = []
    for i in range(1, order + 1):
        for j in range(i, order + 1):
            quadratic.append(values[rows - i] * values[rows - j])
    Z = np.column_stack(quadratic)
    m = Z.shape[1]

    residual = _ols_residuals(dependent, X)                       # AR residuals
    orthogonal = np.column_stack([_ols_residuals(Z[:, c], X) for c in range(m)])

    ssr0 = float(residual @ residual)
    second_stage = _ols_residuals(residual, orthogonal)
    ssr1 = float(second_stage @ second_stage)
    df_denominator = n - m - order - 1
    if df_denominator <= 0 or ssr1 <= 0:
        return TestResult(
            name="Tsay (1986) nonlinearity", null_hypothesis="linear autoregression",
            statistic=None, p_value=None, reference=f"F({m}, {df_denominator})",
            decision_5pct="unavailable", implication="too few observations for the test",
            series=series, available=False,
            unavailable_reason=f"denominator degrees of freedom = {df_denominator}",
            tuning={"order": order, "n_quadratic_terms": m},
        )

    statistic = ((ssr0 - ssr1) / m) / (ssr1 / df_denominator)
    p_value = float(stats.f.sf(statistic, m, df_denominator))
    reject = p_value < SIGNIFICANCE
    return TestResult(
        name="Tsay (1986) nonlinearity",
        null_hypothesis="the series follows a linear autoregression",
        statistic=float(statistic),
        p_value=p_value,
        reference=f"F({m}, {df_denominator})",
        decision_5pct="reject" if reject else "do not reject",
        implication=(
            "evidence against linear autoregressive dynamics"
            if reject
            else "no general evidence against linear autoregressive dynamics"
        ),
        series=series,
        tuning={
            "order": order,
            "n_quadratic_terms": m,
            "n_obs": n,
            "significance": SIGNIFICANCE,
            "variant": "quadratic, orthogonalized nested F",
        },
    )


def _lst_auxiliary(y: np.ndarray, order: int, delay: int):
    """The Teräsvirta (1994) auxiliary regression, equations (3.10) and (3.12).

    The artificial model (3.12) is

        y_t = g_0 + g_1' w_t + g_2'(w_t y_{t-d}) + g_3'(w_t y²_{t-d})
                  + g_4'(w_t y³_{t-d}) + v_t,

    where w_t = (y_{t-1}, ..., y_{t-p})'. The cross-product blocks multiply **w_t**, not
    the full design (1, w_t)': each g_j is a p-vector, and the null (3.11) is
    g_2 = g_3 = g_4 = 0, which is 3p restrictions — the χ²(3p) of the paper.

    Multiplying the intercept column as well would add the standalone terms y^k_{t-d}.
    When d ≤ p those are exactly collinear with existing columns (y_{t-d} is already in
    w_t, y²_{t-d} is the j=d element of the first block, y³_{t-d} the j=d element of the
    second), so they inflate the column count without adding a restriction. That is the
    defect this construction removes; see `_f_test` for the matching degrees of freedom.
    """
    start = max(order, delay)
    rows = np.arange(start, y.size)
    lags = [y[rows - j] for j in range(1, order + 1)]          # w_t
    intercept = np.ones(rows.size)
    X = np.column_stack([intercept] + lags)                     # (1, w_t)'
    W = np.column_stack(lags)                                   # w_t, no intercept
    z = y[rows - delay]                                         # y_{t-d}
    blocks = [W * (z**power)[:, None] for power in (1, 2, 3)]
    return y[rows], X, blocks


def _f_test(dependent: np.ndarray, restricted: np.ndarray, unrestricted: np.ndarray):
    """Nested F test with degrees of freedom taken from the ranks, not the column counts.

    The number of restrictions is the number of **linearly independent** ones,
    rank(unrestricted) − rank(restricted), and the denominator degrees of freedom are
    n − rank(unrestricted). For the auxiliary regressions of Teräsvirta (1994) these
    coincide with the paper's 3p and p, because the design above is generically of full
    column rank. Using the rank rather than the shape keeps the test exact if a
    particular sample does turn out to be collinear, instead of silently reporting an F
    against the wrong reference distribution.
    """
    e0 = _ols_residuals(dependent, restricted)
    e1 = _ols_residuals(dependent, unrestricted)
    ssr0, ssr1 = float(e0 @ e0), float(e1 @ e1)
    rank_restricted = int(np.linalg.matrix_rank(restricted))
    rank_unrestricted = int(np.linalg.matrix_rank(unrestricted))
    q = rank_unrestricted - rank_restricted
    df = dependent.size - rank_unrestricted
    if q <= 0 or df <= 0 or ssr1 <= 0:
        return np.nan, np.nan, q, df
    statistic = ((ssr0 - ssr1) / q) / (ssr1 / df)
    return float(statistic), float(stats.f.sf(statistic, q, df)), q, df


def lst_linearity(y: pd.Series, order: int, delay: int, *, series: str = "") -> TestResult:
    """LST joint linearity test against a STAR alternative, for one delay."""
    values = y.to_numpy(dtype=float)
    dependent, X, blocks = _lst_auxiliary(values, order, delay)
    unrestricted = np.column_stack([X] + blocks)
    statistic, p_value, q, df = _f_test(dependent, X, unrestricted)
    available = np.isfinite(statistic)
    reject = available and p_value < SIGNIFICANCE
    return TestResult(
        name=f"LST linearity (d={delay})",
        null_hypothesis="linearity against a smooth-transition autoregressive alternative",
        statistic=statistic if available else None,
        p_value=p_value if available else None,
        reference=f"F({q}, {df})",
        decision_5pct=("reject" if reject else "do not reject") if available else "unavailable",
        implication=(
            "evidence of smooth-transition nonlinearity at this delay"
            if reject
            else "linearity is not rejected at this delay"
        ),
        series=series,
        available=bool(available),
        tuning={"order": order, "delay": delay, "variant": "third-order Taylor, F form",
                "significance": SIGNIFICANCE},
    )


@dataclass
class STARSpecification:
    """Selected delay and transition type from the Teräsvirta (1994) sequence."""

    series: str
    order: int
    delay: int
    kind: str
    delay_results: list[TestResult] = field(default_factory=list)
    sequence_results: list[TestResult] = field(default_factory=list)
    linearity_rejected: bool = False
    tie_break_used: bool = False

    def to_row(self) -> dict:
        return {
            "series_id": self.series,
            "order": self.order,
            "selected_delay": self.delay,
            "transition_type": self.kind,
            "linearity_rejected_at_selected_delay": self.linearity_rejected,
            "tie_break_used": self.tie_break_used,
            "delay_p_values": ";".join(
                f"d={r.tuning['delay']}:{r.p_value:.6g}" if r.p_value is not None else
                f"d={r.tuning['delay']}:na" for r in self.delay_results
            ),
            "sequence_p_values": ";".join(
                f"{r.name}:{r.p_value:.6g}" if r.p_value is not None else f"{r.name}:na"
                for r in self.sequence_results
            ),
        }


def select_delay_and_type(
    y: pd.Series, order: int, frequency: str, config: Config, *, series: str = ""
) -> STARSpecification:
    """The Teräsvirta (1994) specification sequence (decision D4).

    The delay minimizing the joint linearity p-value is selected, ties broken toward the
    smaller delay so the choice is deterministic. The transition type then follows the
    nested sequence H04, H03, H02: ESTAR when H03 has the smallest p-value, otherwise
    LSTAR.
    """
    delays = config.get(f"nonlinearity.lst.delays.{frequency}")
    values = y.to_numpy(dtype=float)

    delay_results = [lst_linearity(y, order, int(d), series=series) for d in delays]
    usable = [r for r in delay_results if r.p_value is not None]
    if not usable:
        return STARSpecification(series, order, int(delays[0]), "LSTAR", delay_results, [])

    best = min(usable, key=lambda r: (r.p_value, r.tuning["delay"]))
    chosen = int(best.tuning["delay"])
    ties = [r for r in usable if r.p_value == best.p_value]

    dependent, X, blocks = _lst_auxiliary(values, order, chosen)
    first, second, third = blocks
    full = np.column_stack([X, first, second, third])
    # H04: third-order terms are zero.
    s4, p4, q4, df4 = _f_test(dependent, np.column_stack([X, first, second]), full)
    # H03: second-order terms are zero, given the third-order terms are.
    s3, p3, q3, df3 = _f_test(dependent, np.column_stack([X, first]),
                              np.column_stack([X, first, second]))
    # H02: first-order terms are zero, given the higher-order terms are.
    s2, p2, q2, df2 = _f_test(dependent, X, np.column_stack([X, first]))

    def result(name, statistic, p_value, q, df, hypothesis):
        finite = np.isfinite(statistic)
        return TestResult(
            name=name, null_hypothesis=hypothesis,
            statistic=float(statistic) if finite else None,
            p_value=float(p_value) if finite else None,
            reference=f"F({q}, {df})",
            decision_5pct=("reject" if finite and p_value < SIGNIFICANCE else "do not reject")
            if finite else "unavailable",
            implication="part of the Teräsvirta (1994) LSTAR/ESTAR selection sequence",
            series=series, available=bool(finite),
            tuning={"order": order, "delay": chosen, "significance": SIGNIFICANCE},
        )

    sequence = [
        result("H04", s4, p4, q4, df4, "coefficients on the third-order terms are zero"),
        result("H03", s3, p3, q3, df3, "coefficients on the second-order terms are zero"),
        result("H02", s2, p2, q2, df2, "coefficients on the first-order terms are zero"),
    ]
    p_values = {r.name: (r.p_value if r.p_value is not None else np.inf) for r in sequence}
    kind = "ESTAR" if p_values["H03"] < min(p_values["H04"], p_values["H02"]) else "LSTAR"

    return STARSpecification(
        series=series, order=order, delay=chosen, kind=kind,
        delay_results=delay_results, sequence_results=sequence,
        linearity_rejected=bool(best.p_value < SIGNIFICANCE),
        tie_break_used=len(ties) > 1,
    )
