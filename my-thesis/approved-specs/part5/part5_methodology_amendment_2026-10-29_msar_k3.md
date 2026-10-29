# Part 5 methodology amendment — K=3 MSAR robustness (29 October 2026)

**Status:** APPROVED by the user on 29 October 2026.
**Affects:** methodology specification §11 and §11.1; required outputs T4.3 and new F4.3;
computational specification §3; decision log; methodology-versus-jury matrix (P-04);
literature justification §3.13. Every other approved element is unchanged.

## Decision

1. MSAR with **K=2** remains the baseline Markov-switching forecasting model.
2. MSAR with **K=3** remains a **mandatory robustness exercise** for all six approved
   forecasting targets, conducted **in-sample**: estimated once on the same full-sample
   observations as K=2, with the same MSAR structure and lag-order rule.
3. The requirement to re-estimate MSAR K=3 at every pseudo-out-of-sample rolling origin is
   **removed**. No K=3 out-of-sample forecasts are computed.
4. Every other methodology, model, diagnostic, robustness exercise, forecasting horizon,
   estimation window, output and scientific-integrity requirement is unchanged.

## Reasons

* **What the jury asked.** The President's remark P-04 asks whether the two-regime
  assumption is overly restrictive: a three-regime version, "even simply as a check",
  and an explanation if it is rejected. That question concerns the credibility of the
  regime specification and is answered by a properly documented in-sample comparison of
  K=2 and K=3. P-04 does not mandate a rolling K=3 forecasting exercise.
* **What the previous design added.** The original §11.1 (5 October 2026) included
  out-of-sample K=3 forecast performance among the retention criteria, which required
  re-estimating K=3 at every rolling origin (3,527 origins over six chains). That made it
  a far larger experiment than the robustness question requires.
* **Computation.** The Part 8 performance audit (28 October 2026) measured the rolling
  K=3 chains as the largest single block of the run's computation. It also found that
  some K=3 estimates are sensitive to floating-point detail: the K=3 likelihoods are
  multimodal, and weakly identified regimes are common.
* **Transparency.** This is an explicitly authorized, documented revision, made before
  the final production run has completed. It changes the design of the robustness
  exercise, not the treatment of any particular K=3 estimate. The full-sample K=3 fits
  are kept and reported in full, including every failure and fragility flag.

## Changed requirements

| | Before (5 October 2026) | After (29 October 2026) |
|---|---|---|
| K=3 estimation | Full sample **and** every rolling origin | Full sample only, same observations as K=2 |
| K=3 out-of-sample forecasts | Computed; RMSE/MAE/OOS R² and forecast metrics in T4.3 | Not computed; no K=3 forecast metric anywhere |
| T4.3 content | BIC, convergence, occupancy, transition summary, forecast metrics, retention decision | Full in-sample comparison: likelihood, AIC, BIC, convergence and status, means with SEs, occupancy and empty regimes, complete transition matrix with SEs, durations, covariance and boundary warnings, distinguishability, descriptive interpretability, credibility verdict and conclusion |
| Retention rule | Keep K=2 unless K=3 is substantively supported, including OOS evidence | K=2 retained as the predeclared baseline regardless; credible in-sample evidence for K=3 reported transparently |
| Figures | F3.3 regime probabilities (K=2) | Unchanged, plus F4.3 K=3 regime probabilities where the estimate did not fail, labelled with status and flags |
| Claim matrix | — | P-04 evidence route registered as the in-sample comparison, not a predictive-accuracy comparison |
| Rolling model set | AR, ARMA, MSAR(2), STAR, MSAR(3) | AR, ARMA, MSAR(2), STAR |

## Implications for interpretation

* The thesis can say whether a three-regime representation is **credible in-sample**
  (populated, distinguishable, numerically stable, interpretable) and whether in-sample
  criteria favour it. It cannot say whether K=3 would forecast better, and must not
  suggest it.
* Lower in-sample BIC or AIC for K=3 is not evidence of forecasting superiority. Where a
  credible K=3 is favoured in-sample, the thesis reports that the two-regime assumption
  may be restrictive for that target, and that K=2 is retained as the predeclared
  baseline.
* The comparison is descriptive with respect to the number of regimes: no LR test of K=2
  against K=3 with a standard reference distribution is reported (§4.3).
* Out-of-sample conclusions about Markov switching rest on the K=2 baseline only, as
  before.
* Part 2 phrases P-04's minimum response as reporting whether the third regime is
  "empirically meaningful, stable, and useful". Under this amendment, "useful" is
  assessed in-sample (fit, credibility and interpretability), not as forecasting value.
  The thesis should say so explicitly.

## Implementation consequences

* The rolling K=3 chains are removed: the planned rolling workload falls by 3,527
  origins (six chains). All other rolling chains are unchanged.
* The full-sample K=3 fits, their residual diagnostics, credibility flags, T3.1/T3.2 rows
  and failure-registry entries are unchanged.
* Output files that previously carried rolling K=3 rows (the per-series forecast files,
  the forecast-origin audit and horizon coverage, fit records, the failure registry and
  the T4.9 forecast-exposure table) no longer contain them, because those forecasts no
  longer exist. No requirement for any other model changes.
