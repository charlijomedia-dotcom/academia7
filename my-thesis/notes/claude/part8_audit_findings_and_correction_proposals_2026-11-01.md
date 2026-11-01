# Part 8 audit: implementation findings and correction proposals (awaiting approval)

**Date:** 1 November 2026
**Run audited:** `baseline-20261030T173044-949fcd76` (results commit `066294544e8f`, code commit `46a53181e5e9`)
**Status:** documented under CLAUDE.md §6A step 1. **No code has been changed and no output has been regenerated.** Every correction below waits for explicit user approval.

The audit-derived numbers quoted here come from `reports/part8/audit_derived_diagnostics.py` and its output `reports/part8/audit_derived_diagnostics.csv`. That script only reads `output/`. Its numbers are audit evidence, not thesis results (CLAUDE.md §9).

---

## F1 (MATERIAL): FAILED fits with finite forecasts enter the forecast evaluation

**What happens.** Part 5 §7.5 classes an AR whose stability condition is violated as **failed**, and failed models are "reported as failures rather than" used. `models/ar.py` flags `UNSTABLE_AR` as `Status.FAILED`, but still returns the explosive point forecasts. `forecasting/rolling.py` writes those forecasts to the forecast frame with `status="failed"`. The evaluation layer drops only **non-finite** errors:

- `evaluation/metrics.accuracy_table` uses `np.isfinite(frame["error"])`;
- `evaluation/alignment.valid_dates` uses `np.isfinite(forecast) & np.isfinite(actual)`.

So a failed fit whose forecast is finite is scored as if it were valid. Non-converged ARMA/MSAR fits are unaffected, because their forecasts are NaN. The failure registry itself is internally contradictory: it records these events with `forecast_retained=False` (`robustness/T4.7_failure_registry.csv`).

**Where it bites.**

- **Baseline.** One fit is affected: UNRATE AR, origin 2020-04, `UNSTABLE_AR` with root modulus 1.313. Its forecasts are 31.6 (h=1), 93.4 (h=3), 304.2 (h=6) and 2,063.6 (h=12), against actuals 13.2, 10.2, 6.9 and 6.1 (`forecasts/forecasts_UNRATE.csv`).
- **Robustness: UNRATE.**
  - Window-length chains 180 and 300 (origin 2020-04), from `models/fit_records.csv` with n_obs 174 and 294.
  - The T4.1 UNRATE first-difference alternative (origins 2020-04 and 2020-08).
- **Robustness: other targets.**
  - The T4.1 FEDFUNDS level alternative: 71 `UNSTABLE_AR` fits, with origins 1974-06 to 2024-12.
  - The T4.2 CPI AR(p=12) chain: 1 fit, origin 1974-09.
- For the robustness chains the forecast-level files are not stored, so the size of the effect can be confirmed only by regeneration.

**Magnitude (baseline UNRATE, audit recomputation that excludes only the failed origin):**

| h | AR RMSE published | AR RMSE excluding failed | MSAR OOS R² published | MSAR OOS R² excluding failed |
|---|---|---|---|---|
| 1 | 0.886 | 0.551 | 0.690 | 0.190 |
| 3 | 3.277 | 0.942 | 0.894 | −0.128 |
| 6 | 11.306 | 1.165 | 0.985 | −0.538 |
| 12 | 78.174 | 1.492 | 0.999 | −0.959 |

The published UNRATE OOS R² values at h ≥ 3 reverse sign. Ranks and HLZ/DM statistics against AR are also distorted: a single spike pins the HLZ p-value near 0.32.

**Affected outputs (to regenerate):**

- **Evaluation tables, UNRATE rows involving AR:**
  - T3.3, T3.3A, T3.3B, T3.4;
  - T3.5 (both tables), T3.6;
  - T4.4 (both tables), T4.TP1.
- **Robustness tables:**
  - `window_length_comparison.csv`, `window_length_predictive_tests.csv` and `window_length_mcs.csv` (UNRATE rows);
  - T4.1, both tables (UNRATE, plus the FEDFUNDS level-alternative AR rows);
  - T4.2, both tables (the p=12 row);
  - T4.5 comparison and tests (UNRATE AR benchmark rows);
  - T4.9 (UNRATE rows).
- **Figures:** F3.3 to F3.6 and F4.8 for UNRATE.
- **Manifests:** the claim matrix and output inventory.

**Proposed correction (implementation only; no methodological change).** Mask the forecasts of every record with `status == failed`, setting forecast and error to NaN, in `rolling.py`, where rows are appended. Keep the raw failed forecast in a separate diagnostic column, e.g. `failed_raw_forecast`, so the failure stays visible. Then regenerate:

1. the evaluation stage;
2. the robustness chains for T4.1, T4.2 and T4.8 (the cache serves the fits; only the scoring changes);
3. the dependent manifests.

Add a regression test: a FAILED AR with finite forecasts must not change any metric. Also record the correction under §6A in a `correction_<date>_failed_forecast_scoring.md` note.

---

## F2 (MATERIAL for completeness of R1-14): MCS unavailable in 11 of 34 baseline cells, and 2 window-length cells

**What happens.**

- `forecast_tests/T3.4_model_confidence_set.csv` reports "MCS procedure failed: IndexError(...)" for:
  - CPIAUCSL: h=1 squared; h=3 and h=6 squared and absolute; h=12 squared;
  - M2SL: h=3 squared; h=6 and h=12 squared and absolute.
- `window_length_mcs.csv` has two further failed cells.
- I reproduced the failure with `arch` 8.0.0 on the stored CPIAUCSL h=1 losses (check A6). With all four models the library raises the IndexError; without STAR it runs.
- **Cause:** the STAR squared losses (up to about 2×10²² at h=1 and 10²⁰⁰ at h=12) make the library's internal elimination statistics numerically degenerate.

**Proposed correction (decision needed).** The approved set is "all admissible forecast models", and STAR is admissible as *fragile*, so dropping STAR is not an option without approval. Options:

- **(a)** Keep the result as "inference unavailable" and report it as such. This is the current state and is honest, but R1-14 is then only partially delivered for CPI and M2.
- **(b)** Implement a numerically guarded MCS. It would run the same Hansen–Lunde–Nason R-statistic elimination with the same stationary bootstrap, block length, replications and seed. In the cells where `arch` breaks, it would compute the elimination statistics in a way that tolerates extreme losses, then cross-validate against `arch` on every cell where `arch` succeeds. This needs approval because it replaces a library call.
- **(c)** Approve a predeclared rule that excludes from the MCS any model whose losses are non-finite or numerically overflow, recorded as an MCS-specific admissibility rule. This is methodological; the user decides.

---

## F3 (LABELLING, not material to decisions): sign convention text in T3.3A / T3.3B

**What happens.**

- The evaluation pairs are configured as `[AR, ARMA]`, `[AR, MSAR]` and so on (`configs/baseline.yaml`). `pipeline.py` computes `d = loss(model_a) − loss(model_b)`.
- The rows still state "d_t = loss(competitor) − loss(benchmark); negative favours the competitor".
- Treating AR, or ARMA in the ARMA pairs, as the benchmark, the stored differential is benchmark minus competitor, so **positive favours `model_b`**. Check A5 confirms this: GDPC1 h=1 mean(loss_AR − loss_ARMA) = +0.404 equals the stored value, while T3.3 reports −0.404 for ARMA versus AR, correctly signed.

Two-sided HLZ and DM-HLN p-values and the 5% decisions are unaffected. The statistic signs and `p_value_upper/lower` must be read with the convention reversed. T3.3, T3.5, T4.1, T4.2, T4.4, T4.5 and the T4.8 tests use the correct competitor − benchmark orientation.

**Proposed correction.** Pass `(competitor, benchmark) = (model_b, model_a)` to `loss_differential`, `hlz_test` and `dm_hln_test` in the pairwise loop, so the stored values match the stated convention, then regenerate T3.3A and T3.3B. The alternative is to change the label only. The reports in `reports/part8/` already read the tables with the correct orientation.

---

## F4 (SPECIFICATION GAP, P-02): Zivot–Andrews never reported

**What happens.**

- Part 5 §3.2 says Zivot–Andrews is "**Applied to UNRATE and FEDFUNDS in levels**", and that "the break date must be reported and plotted on the level series".
- P-02 requires "at least one break-allowing procedure" to be reported.
- `diagnostics/decision_rule.py` runs ZA only as the §3.4 tie-breaker when ADF and KPSS disagree. Both series gave clear branches on the initial window and the full sample, so ZA never ran:
  - UNRATE: branch 1, level;
  - FEDFUNDS: branch 2, difference.
- There is therefore no ZA statistic, break date or plotted break in `diagnostics/T2.2_stationarity.csv` or `figures/F2.1_*`.

**Proposed correction.** Run the already-implemented `zivot_andrews_test` (intercept+trend break, trim 0.15, BIC, max lag 12) unconditionally on the initial-window and full-sample levels of UNRATE and FEDFUNDS. Report it in T2.2 and mark the break on F2.1. Under §3.4 the transformation decision cannot change, because ZA enters the rule only when ADF and KPSS disagree. This is a reporting addition that takes seconds to compute.

---

## F5 (CLASSIFICATION, interpretive): full-sample FEDFUNDS MSAR(K=2) is effectively unidentified but labelled *fragile* only for residual autocorrelation

`models/T3.2_nonlinear_credibility.csv` shows the following for this fit:

- μ1 = μ2 = 0.0025;
- transition-probability standard errors of 18.06 and 38.26;
- a log-likelihood identical to the AR(1) at −518.894 (`models/T3.1_in_sample_adequacy.csv`);
- T4.3 marks the K=2 means "not distinguishable" (z ≈ 2×10⁻⁶).

Part 5 §8.1 reserves *failure* for, among other cases, "an effectively unidentified regime". The pipeline has no detector for indistinguishable K=2 regimes: D8 requires empty occupancy plus corroboration, and occupancy here is 50/50. The forecast numbers are unaffected, because the forecasts equal the AR's. The status label and the P-03 interpretation are affected.

**Proposal (decision needed).** Either:

- leave the automatic status unchanged and treat this fit as non-identified in interpretation, which is what the Part 8 reports do; or
- approve a predeclared detector, for example adjacent regime means not distinguishable together with unidentified transition probabilities, implying FAILED with `UNIDENTIFIED_REGIME`. That would change statuses in the rolling FEDFUNDS chain and possibly others, so it is a methodological classification decision.

---

## F6 (NUMERICAL, T4.3): UNRATE K=3 estimate is not a global maximum

**What happens.**

- K=3 nests K=2: a third regime that is never entered reproduces the K=2 likelihood in the limit. So the maximised K=3 log-likelihood cannot be below the K=2 value.
- For UNRATE, `robustness/T4.3_regime_count.csv` gives K=3 log-likelihood 13.88 against K=2 102.04 (Δ = −88.16, check A7).
- The K=3 search used 2 deterministic starts (`n_starts = 2`).
- The published "BIC favours K=2 (ΔBIC=210.542)" for UNRATE is therefore an optimisation artefact, not evidence.
- The "K=3 not credible" verdict still stands for the estimate that was obtained, which has a singular covariance and low occupancy.
- The FEDFUNDS K=2 solution (F5) is also plausibly a degenerate local optimum. Its K=3 gain of +265.48 is consistent with that.

**Proposal (decision needed).** The approved rule is "the same deterministic multi-start and optimizer rules" as K=2, so adding starts would change an approved computational setting. Options:

- **(a)** Report UNRATE's K=2/K=3 information-criterion comparison as INCONCLUSIVE. The Part 8 reports do this.
- **(b)** Approve a nesting-consistent extra start for K=3: K=2 optimum plus an empty third regime. This guarantees log-likelihood(K=3) ≥ log-likelihood(K=2), and the run would be repeated for all six targets for symmetry. It is cheap, because it is full-sample only.

---

## F7 (MINOR, presentation)

1. In `data_audit/T2.1_data_dictionary.csv`, UNRATE and FEDFUNDS still show `transformation = "pending stationarity decision"` and empty transformed dates. The table is written before the stationarity stage and never refreshed. The decisions themselves are in `diagnostics/T2.2_transformation_decisions.csv`. Proposal: fill the field from the decision.
2. In `figures/F3.4_*` (R1-06):
   - the main panel plots the FAILED UNRATE AR forecast (spike to 31.6);
   - the diagnostic panel draws lines between non-adjacent flagged points (for example a dotted STAR line from about 1970 to 2020).
   - Proposal: exclude FAILED forecasts from the main panel (this follows from F1) and draw flagged points as markers, not connected lines.
3. The production `run_logs/` were not committed to the results branch; only smoke logs are present. The three skipped chains are confirmed from the outputs instead (`robustness/T4.6_arch_trigger.csv`).
4. About 207 provenance sidecars and Parquet companions are outside `output/manifests/output_inventory.csv`, so they are not checksum-covered.

---

## What is **not** a defect (checked)

- **STAR explosive forecasts.** STAR RMSE values range up to about 2×10⁹⁹ (CPIAUCSL h=12).
- **Cause.** These are genuine near-non-identification:
  - the threshold c lies outside the 5–95% range of the transition variable;
  - only a handful of observations identify the outer-regime coefficients, for example θ0 = −1.5×10¹¹ at CPIAUCSL origin 1974-01 (`models/fit_records.csv`);
  - the observed information is singular.
- **Classification.** Part 5 §8.2 and decision D8/P-2 (`notes/claude/part6_issues_and_decisions.md`) make singular or unstable covariance and extreme-but-finite forecasts *fragile*, not failed. The forecasts are therefore retained in the metrics, as the approved methodology requires.
- **Interpretive consequence.** STAR RMSE and the STAR pairwise tests are dominated by a few explosive forecasts. HLZ/DM statistics then converge to about ±1, so p ≈ 0.32 in 51 of the 88 available STAR-pair HLZ tests (check A4). Those tests carry no information about typical STAR accuracy. Changing the treatment, for example to "extreme forecast implies failed", would be a methodological decision.
- **Three skipped chains.** These are the ARMA-GARCH chains for GDPC1, INDPRO and M2SL. ARCH-LM on the initial-window ARMA residuals did not reject (p = 0.485, 0.990 and 0.369, `robustness/T4.6_arch_trigger.csv`), so §5.3 and decision M9 correctly screened them out.
- **Failure-registry count.** The 34,153 registry rows are reason-code events, not failed fits: 540 FAILED events and 33,613 FRAGILE flags. They come from 67,253 fits, of which 448 are FAILED, 23,008 FRAGILE and 43,797 ADEQUATE (`models/fit_records.csv`).
