"""T4.3: in-sample K=2 versus K=3 MSAR regime-count comparison (Part 5 §11.1, amended
29 October 2026).

Built only from the full-sample fits of the adequacy stage. No rolling K=3 fit and no
forecast enters here, and no column is a forecast metric: the comparison concerns the
credibility of the regime specification (P-04), not predictive accuracy.

Three tables:

* one row per target and regime count, with likelihood, criteria, convergence, status,
  covariance, occupancy, boundary, distinguishability and descriptive interpretability;
* one row per target, regime count and parameter, with its standard error and the
  warning that concerns it;
* one conclusion row per target, applying the predeclared §11.1 credibility rule.

K=2 is the maintained baseline in every conclusion, whatever the criteria show.
"""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

#: Reference value for the descriptive distinguishability of adjacent regime means.
DISTINGUISHABLE_Z = 1.96

SCOPE_NOTE = ("In-sample comparison of full-sample fits only (Part 5 §11.1); not evidence "
              "about forecasting performance. No likelihood-ratio test of K=2 against K=3 "
              "is reported (§4.3).")
INTERPRETABILITY_NOTE = ("Regimes are statistical states numbered in increasing order of "
                         "their estimated mean. The recession/expansion probabilities are "
                         "descriptive; no economic label is assigned to a state.")
BASELINE = "K=2 (predeclared baseline, Part 5 §11.1)"

_COV_CODES = ("SINGULAR_COV", "ILL_CONDITIONED_COV")


def _codes(record) -> list[str]:
    return [code.value for code in getattr(record, "reason_codes", [])]


def _finite(value) -> bool:
    try:
        return value is not None and bool(np.isfinite(float(value)))
    except (TypeError, ValueError):
        return False


def _usable_fit(fit) -> bool:
    return fit is not None and getattr(fit, "mu", np.empty(0)).size > 0


def distinguishability(fit) -> tuple[float, str]:
    """Smallest |mu_{k+1} - mu_k| / SE over adjacent ordered regimes.

    The covariance is the observed-information covariance in the estimation
    parameterization, whose first K coordinates are the (mean-ordered) regime means
    themselves, so the standard error of a difference uses their covariance directly.
    """
    if not _usable_fit(fit):
        return float("nan"), "not assessable: no estimate"
    status = str(fit.record.diagnostics.get("covariance_status", ""))
    covariance = np.asarray(getattr(fit, "covariance", np.empty((0, 0))), dtype=float)
    k = fit.k_regimes
    if status != "ok" or covariance.shape[0] < k or not np.isfinite(covariance[:k, :k]).all():
        return float("nan"), f"not assessable: covariance {status or 'not computed'}"
    ratios = []
    for i in range(k - 1):
        variance = covariance[i, i] + covariance[i + 1, i + 1] - 2 * covariance[i, i + 1]
        if not variance > 0:
            return float("nan"), "not assessable: non-positive variance of a mean difference"
        ratios.append(abs(fit.mu[i + 1] - fit.mu[i]) / np.sqrt(variance))
    smallest = float(min(ratios))
    return smallest, ("distinguishable" if smallest > DISTINGUISHABLE_Z
                      else "not distinguishable")


def _recession_profile(fit, dates: pd.DatetimeIndex, recession: pd.Series) -> str:
    if not _usable_fit(fit) or fit.smoothed_regime.size == 0:
        return ""
    aligned = recession.reindex(dates)
    mask = aligned.notna().to_numpy()
    if not mask.any():
        return "no NBER dates on the estimation sample"
    flags = aligned.to_numpy()[mask].astype(float)
    smoothed = fit.smoothed_regime[mask]
    parts = []
    for k in range(fit.k_regimes):
        rec = smoothed[flags == 1, k].mean() if (flags == 1).any() else float("nan")
        exp = smoothed[flags == 0, k].mean() if (flags == 0).any() else float("nan")
        parts.append(f"regime{k + 1}: recession={rec:.3f}, expansion={exp:.3f}")
    return "; ".join(parts)


def regime_rows(series: str, frequency: str, target: pd.Series, order: int,
                attempts: Mapping[str, Mapping[str, Any]], labels: Mapping[str, str],
                recession: pd.Series, thresholds: Mapping[str, float],
                figure_notes: Mapping[str, str]) -> tuple[list[dict], list[dict]]:
    """Comparison rows and parameter rows for one target.

    `attempts` maps "MSAR" (K=2) and "MSAR3" (K=3) to {"fit", "record"}; a failed
    attempt may have no fit. `figure_notes` says, per model, whether a regime-probability
    figure was produced.
    """
    rows, parameters = [], []
    index = pd.DatetimeIndex(target.index)
    for model, k in (("MSAR", 2), ("MSAR3", 3)):
        attempt = attempts.get(model)
        record = attempt.get("record") if attempt else None
        fit = attempt.get("fit") if attempt else None
        codes = _codes(record) if record is not None else []
        row: dict[str, Any] = {
            "series": series, "frequency": frequency, "model": model, "k_regimes": k,
            "role": "baseline" if k == 2 else "robustness (in-sample only)",
            "spec_label": labels.get(model, ""), "ar_order": order,
            "sample_start": index[0].date().isoformat() if len(index) else "",
            "effective_sample_start": (index[order].date().isoformat()
                                       if len(index) > order else ""),
            "sample_end": index[-1].date().isoformat() if len(index) else "",
        }
        if record is None:
            row.update({"status": "failed", "reason_codes": "NOT_ESTIMATED",
                        "figure_produced": False,
                        "figure_note": "not produced: no estimate"})
            rows.append(row)
            continue
        diagnostics = record.diagnostics
        n_params = diagnostics.get("n_params")
        row.update({
            "n_obs": record.n_obs, "n_params": n_params,
            "loglik": record.loglik, "aic": record.aic, "bic": record.bic,
            "converged": record.converged,
            "optimizer_message": record.optimizer_message,
            "n_starts": diagnostics.get("n_starts"),
            "n_converged_starts": diagnostics.get("n_converged"),
            "start_used": record.start_used,
            "selection_rule": diagnostics.get("selection_rule"),
            "status": record.status.value,
            "reason_codes": ";".join(codes),
            "covariance_status": diagnostics.get("covariance_status", "not computed"),
            "singular_covariance": "SINGULAR_COV" in codes,
            "ill_conditioned_covariance": "ILL_CONDITIONED_COV" in codes,
            "transition_boundary": "TRANSITION_BOUNDARY" in codes,
            "empty_regime": "EMPTY_REGIME" in codes,
            "interpretability_note": INTERPRETABILITY_NOTE,
            "figure_produced": figure_notes.get(model, "").startswith("produced"),
            "figure_note": figure_notes.get(model, ""),
        })
        if _usable_fit(fit):
            occupancy = np.asarray(fit.occupancy, dtype=float)
            effective = occupancy * fit.smoothed_regime.shape[0]
            low = [k_ + 1 for k_, (share, count) in enumerate(zip(occupancy, effective))
                   if share < thresholds["low_occupancy_fraction"]
                   or count < thresholds["low_occupancy_effective_obs"]]
            ratio, verdict = distinguishability(fit)
            low_t = thresholds["transition_boundary_low"]
            high_t = thresholds["transition_boundary_high"]
            boundary = [f"p{i + 1}{j + 1}={fit.P[i, j]:.6f}" for i in range(k) for j in range(k)
                        if fit.P[i, j] <= low_t or fit.P[i, j] >= high_t]
            dates = index[order:order + fit.smoothed_regime.shape[0]]
            row.update({
                "boundary_entries": "; ".join(boundary),
                "regime_means": "; ".join(f"mu{i + 1}={v:.6g}" for i, v in enumerate(fit.mu)),
                "regime_mean_std_errors": "; ".join(
                    f"mu{i + 1}={record.std_errors.get(f'mu{i + 1}', float('nan')):.6g}"
                    for i in range(k)),
                "sigma": fit.sigma,
                "occupancy": "; ".join(f"regime{i + 1}={v:.4f}" for i, v in enumerate(occupancy)),
                "effective_obs": "; ".join(f"regime{i + 1}={v:.1f}"
                                           for i, v in enumerate(effective)),
                "min_occupancy": float(occupancy.min()),
                "min_effective_obs": float(effective.min()),
                "low_occupancy_regimes": ";".join(str(r) for r in low),
                "expected_durations": "; ".join(f"regime{i + 1}={v:.2f}"
                                                for i, v in enumerate(fit.expected_duration)),
                "min_mean_separation_z": ratio,
                "means_distinguishable": verdict,
                "recession_expansion_profile": _recession_profile(fit, dates, recession),
            })
            parameters.extend(_parameter_rows(series, model, k, fit, record, thresholds,
                                              occupancy, effective))
        else:
            row.update({"means_distinguishable": "not assessable: no estimate"})
        rows.append(row)
    return rows, parameters


def _parameter_rows(series, model, k, fit, record, thresholds, occupancy, effective):
    low_t, high_t = thresholds["transition_boundary_low"], thresholds["transition_boundary_high"]
    out = []

    def add(name, kind, value, regime="", se=None, warning=""):
        out.append({"series": series, "model": model, "k_regimes": k, "parameter": name,
                    "kind": kind, "regime": regime, "estimate": float(value),
                    "std_error": (float(se) if _finite(se) else float("nan")),
                    "warning": warning})

    for i in range(k):
        add(f"mu{i + 1}", "regime mean", fit.mu[i], i + 1, record.std_errors.get(f"mu{i + 1}"))
    for j, value in enumerate(fit.phi):
        add(f"phi{j + 1}", "AR coefficient (common)", value, "", record.std_errors.get(f"phi{j + 1}"))
    add("sigma", "innovation s.d. (common)", fit.sigma, "", record.std_errors.get("sigma"))
    for i in range(k):
        for j in range(k):
            value = float(fit.P[i, j])
            add(f"p{i + 1}{j + 1}", "transition probability", value, i + 1,
                record.std_errors.get(f"p{i + 1}{j + 1}"),
                "TRANSITION_BOUNDARY" if (value <= low_t or value >= high_t) else "")
    for i in range(k):
        add(f"duration{i + 1}", "expected duration (periods)", fit.expected_duration[i], i + 1)
        low = (occupancy[i] < thresholds["low_occupancy_fraction"]
               or effective[i] < thresholds["low_occupancy_effective_obs"])
        add(f"occupancy{i + 1}", "smoothed occupancy share", occupancy[i], i + 1, None,
            "LOW_OCCUPANCY" if low else "")
        add(f"effective_obs{i + 1}", "effective observations", effective[i], i + 1, None,
            "LOW_OCCUPANCY" if low else "")
    return out


def credibility_problems(row: Mapping[str, Any]) -> list[str]:
    """The §11.1 conditions a K=3 estimate fails; empty when it is credible."""
    problems = []
    if row.get("status") == "failed" or not row.get("converged", False):
        codes = row.get("reason_codes") or "not converged"
        return [f"estimation failed ({codes})"]
    if row.get("low_occupancy_regimes"):
        problems.append(f"low-occupancy regime(s) {row['low_occupancy_regimes']}")
    if row.get("empty_regime"):
        problems.append("empty regime")
    if row.get("transition_boundary"):
        problems.append("transition probability at the boundary")
    if row.get("singular_covariance") or row.get("ill_conditioned_covariance") \
            or str(row.get("covariance_status", "")) != "ok":
        problems.append(f"covariance not usable ({row.get('covariance_status')})")
    if row.get("means_distinguishable") != "distinguishable":
        problems.append(f"regime means {row.get('means_distinguishable')}")
    return problems


def _favours(delta) -> str:
    if not _finite(delta):
        return "not available"
    return "K=3" if float(delta) < 0 else "K=2"


def conclusion_row(series: str, rows: list[dict]) -> dict:
    """Apply the predeclared §11.1 rule to one target's K=2 and K=3 rows."""
    by_model = {row["model"]: row for row in rows}
    two, three = by_model.get("MSAR", {}), by_model.get("MSAR3", {})
    out: dict[str, Any] = {"series": series, "maintained_baseline": BASELINE,
                           "scope_note": SCOPE_NOTE}
    deltas = {}
    for name in ("loglik", "aic", "bic"):
        a, b = three.get(name), two.get(name)
        deltas[name] = float(a) - float(b) if _finite(a) and _finite(b) else float("nan")
        out[f"delta_{name}_k3_minus_k2"] = deltas[name]
    out["aic_favours"] = _favours(deltas["aic"])
    out["bic_favours"] = _favours(deltas["bic"])

    baseline_failed = two.get("status") == "failed" or not two.get("converged", False)
    problems = credibility_problems(three) if three else ["not estimated"]
    out["k3_credible"] = not problems
    out["k3_credibility_problems"] = "; ".join(problems)
    criteria = (f"In-sample criteria: BIC favours {out['bic_favours']} "
                f"(ΔBIC={deltas['bic']:.3f}), AIC favours {out['aic_favours']} "
                f"(ΔAIC={deltas['aic']:.3f}).")
    if baseline_failed:
        out["conclusion"] = ("Comparison incomplete: the K=2 baseline full-sample estimate "
                             f"did not converge or failed ({two.get('reason_codes', '')}). "
                             + ("K=3 credible. " if not problems else
                                f"K=3 not credible: {'; '.join(problems)}. ") + criteria)
        out["implication_for_k2"] = ("No in-sample regime-count conclusion can be drawn "
                                     "while the baseline estimate itself is unusable.")
    elif problems and problems[0].startswith(("estimation failed", "not estimated")):
        out["conclusion"] = f"K=3 not credible: {problems[0]}."
        out["implication_for_k2"] = (
            "The three-regime model could not be estimated reliably on this sample; the "
            "exercise gives no evidence that the two-regime assumption is overly "
            "restrictive.")
    elif problems:
        out["conclusion"] = f"K=3 not credible: {'; '.join(problems)}. {criteria}"
        out["implication_for_k2"] = (
            "The additional regime is not supported as a distinct, adequately identified "
            "state, so the exercise gives no credible evidence that the two-regime "
            "assumption is overly restrictive"
            + (", although the in-sample criteria favour K=3; that is reported "
               "transparently and is not taken as support for K=3."
               if out["bic_favours"] == "K=3" or out["aic_favours"] == "K=3" else "."))
    elif out["bic_favours"] == "K=3":
        out["conclusion"] = f"K=3 credible and favoured by BIC. {criteria}"
        out["implication_for_k2"] = (
            "Credible in-sample evidence that the two-regime representation may be "
            "restrictive for this target. It is reported transparently; K=2 remains the "
            "predeclared baseline, and this is not evidence about forecasting performance.")
    elif out["aic_favours"] == "K=3":
        out["conclusion"] = f"K=3 credible; BIC favours K=2 and AIC favours K=3. {criteria}"
        out["implication_for_k2"] = (
            "Mixed in-sample evidence: the parsimony-weighted criterion (BIC) supports the "
            "two-regime representation, the less parsimonious one (AIC) does not.")
    else:
        out["conclusion"] = f"K=3 credible but favoured by neither AIC nor BIC. {criteria}"
        out["implication_for_k2"] = ("No in-sample evidence that the two-regime assumption "
                                     "is overly restrictive for this target.")
    return out
