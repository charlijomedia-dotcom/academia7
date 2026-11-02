# Part 8 — Full empirical analysis and audit report

> **Correction phase (2 November 2026).** This report audits the **original publication**: results commit `066294544e8f`, run `baseline-20261030T173044-949fcd76`. Every number cited from `output/` refers to that publication.
>
> - Corrections F1 (failed-forecast scoring), F2 (guarded MCS), F3 (pairwise sign convention) and F4 (Zivot–Andrews reporting) are implemented and tested on branch `part8-corrections`. They have **not** yet been applied to `output/`.
> - Findings that depend on affected tables are **provisional**; see `corrections/correction_plan.md` and the `provisional` column of `claim_evidence_matrix_adjudicated.csv`.
> - A corrected publication will be released separately, with its own run ID and manifests. It will not overwrite the original results commit.

> **R1 status (2 November 2026; provisional, not yet authoritative).** Corrections F1, F2, F3, F4 and F7.1 have been applied by recomputing from the published forecasts. No model was estimated.
>
> - Implementation: branch `part8-r1-rescore`.
> - Provisional corrected release: `part8-corrected-results/r1-20261101`. A release regenerated from a clean, pinned commit has identical tables.
> - Evidence: `corrections/r1/`.
>
> The text below is unchanged and still describes the original publication. Until you approve the corrected release, the original numbers stand where they differ, as follows:
>
> - **UNRATE AR benchmark (F1).** The published version scored a failed fit. Corrected AR RMSE at h=1 is 0.551, not 0.886. Corrected OOS R² against AR is 0.24 for ARMA, 0.19 for MSAR and −0.10 for STAR. No nonlinear-over-AR rejection appears anywhere.
> - **New nominal HLZ rejection against STAR** (UNRATE h=1, absolute loss, p = 0.0015). It is not robust to multiplicity: Holm-adjusted p is 0.066 across the 44 STAR-vs-AR tests, and STAR stays in the 90% and 95% MCS. See `corrections/r1/multiplicity_unrate_star.md`.
> - **F2 MCS cells.** The 24 previously unavailable cells (CPI and M2SL) now have sets, and MSAR and STAR are retained in all of them.
> - **Still pending, and kept provisional:** T4.1 alternative transformations, T4.2, and T4.8 UNRATE at 180 and 300 months. These await the approved cache replay and, where needed, Tier A or Tier B estimation.
> - **Corrected claim statuses** are in `corrections/r1/claim_evidence_matrix_corrected.csv`.
> - **F6** (MSAR global optimum) remains an unresolved limitation.


**Run audited:** `baseline-20261030T173044-949fcd76`

- **Code:** commit `46a53181e5e9d23c415f1c7fe11c0da93d9c3964`, tree clean.
- **Results:** commit `066294544e8ff84f3c2c73ab647c8d13331dcac1`, on branch `part8-results/baseline-20261030T173044-949fcd76`. This branch is kept unchanged as the immutable computational baseline.
- **Frozen input:** `data/frozen/thesis_input_2026-10-05.csv`, SHA-256 `7e7dc769…5b832a`.
- **Configuration hash:** `949fcd76…61db8e`.
- **Report branch:** `part8-final-audit`, created from the results commit. No file under `output/`, `data/`, `code/` or `approved-specs/` was modified.
- **Date of audit:** 1 November 2026.

## 0. How to read this report

### Authority and labels

- **Numbers.** Every number is quoted from a file under `output/` (CLAUDE.md §9). Citations use the short keys below plus the row identifiers: series, model, horizon h, and loss where relevant.
- **Audit-derived numbers.** A few numbers are labelled **[audit]**. They come from `reports/part8/audit_derived_diagnostics.py`, which reads `output/` only, and its output `reports/part8/audit_derived_diagnostics.csv`.
  - They are audit evidence about the published outputs, not approved-methodology results.
  - They must not be cited as thesis results.
  - If the proposed corrections are approved, the regenerated files under `output/` supersede them.
- **Labels.** Results are labelled *baseline*, *robustness*, *diagnostic* or *failed specification* (CLAUDE.md §5).
- **Claim statuses.** Claims use SUPPORTED, QUALIFIED, NOT_SUPPORTED or INCONCLUSIVE.

### Source keys

All paths are relative to `output/`.

| Key | File |
|---|---|
| RS | `manifests/run_summary.json` |
| RM | `manifests/run_manifest.json` |
| INV | `manifests/output_inventory.csv` |
| T2.1 | `data_audit/T2.1_data_dictionary.csv` |
| T2.2 | `diagnostics/T2.2_stationarity.csv` |
| T2.2D | `diagnostics/T2.2_transformation_decisions.csv` |
| T2.3 | `diagnostics/T2.3_tsay.csv` |
| T2.4 | `diagnostics/T2.4_star_linearity.csv` |
| T2.5 | `diagnostics/T2.5_selected_specs.csv` |
| T3.1 | `models/T3.1_in_sample_adequacy.csv` |
| T3.2 | `models/T3.2_nonlinear_credibility.csv` |
| FR | `models/fit_records.csv` |
| T3.3 | `forecast_tests/T3.3_main_forecast_table.csv` |
| T3.3A | `forecast_tests/T3.3A_hlz_pairwise.csv` |
| T3.3B | `forecast_tests/T3.3B_dm_hln_pairwise.csv` |
| T3.4 | `forecast_tests/T3.4_model_confidence_set.csv` |
| T3.5R | `forecast_tests/T3.5_state_loss_regression.csv` |
| T3.5S | `forecast_tests/T3.5_state_performance.csv` |
| T3.6 | `forecast_tests/T3.6_peak_trough_detail.csv` |
| FC-x | `forecasts/forecasts_<x>.csv` |
| FOA | `forecasts/forecast_origin_audit.csv` |
| T4.1 / T4.1P | `robustness/T4.1_transformation_robustness.csv` / `_predictive_tests.csv` |
| T4.2 / T4.2P | `robustness/T4.2_cpi_lag_robustness.csv` / `T4.2_cpi_lag_predictive_tests.csv` |
| T4.3 / T4.3C / T4.3P | `robustness/T4.3_regime_count.csv` / `_conclusion.csv` / `T4.3_regime_parameters.csv` |
| T4.4 / T4.4P | `robustness/T4.4_horizon_robustness.csv` / `T4.4_horizon_predictive_tests.csv` |
| T4.5C / T4.5P / T4.5S | `robustness/T4.5_var_comparison.csv` / `_predictive_tests.csv` / `_selection.csv` |
| T4.6T / T4.6S | `robustness/T4.6_arch_trigger.csv` / `T4.6_arma_garch_summary.csv` |
| T4.7 | `robustness/T4.7_failure_registry.csv` |
| T4.8C / T4.8P / T4.8M / T4.8A | `robustness/window_length_comparison.csv` / `_predictive_tests.csv` / `_mcs.csv` / `_origin_audit.csv` |
| T4.9 / EXP | `data_audit/T4.9_locf_sample_comparison.csv` / `data_audit/locf_forecast_exposure.parquet` |
| TP1 | `robustness/T4.TP1_turning_window_sensitivity.csv` |

---

## Executive summary

### 1. Reproducibility and provenance are sound

- The results commit changes only files under `output/` relative to the approved code commit.
- The data hash and code SHA match:
  - data hash `7e7dc769…` (RM);
  - code SHA `46a53181…`, `code_tree_dirty=false` (RM).
- All 254 inventoried files pass checksum verification against INV.

### 2. Three implementation defects affect part of the reported evidence

They are documented in `notes/claude/part8_audit_findings_and_correction_proposals_2026-11-01.md`, and approval is requested before any change.

- **F1, material.** A FAILED fit with finite forecasts is scored in the evaluation. In the baseline this is UNRATE AR, origin 2020-04, `UNSTABLE_AR`.
  - It inflates UNRATE's AR benchmark RMSE: at h=12, 78.17 published against 1.49 excluding that origin [audit].
  - It reverses the sign of UNRATE's OOS R² for MSAR at h ≥ 3.
  - All UNRATE results that involve AR are therefore **provisional**.
- **F2.** The MCS is unavailable in 11 of 34 baseline cells (CPIAUCSL and M2SL), because extreme STAR losses break the library routine.
- **F4.** The break-allowing Zivot–Andrews test required for P-02 was never run.

Lesser issues:

- **F3.** The sign-convention label in T3.3A/T3.3B is reversed. The two-sided decisions are unaffected.
- **F5.** The FEDFUNDS K=2 MSAR is unidentified but is labelled fragile.
- **F6.** The UNRATE K=3 fit is not a global maximum.
- **F7.** Presentation issues.

### 3. Forecasting: no approved nonlinear model gives formally supported, robust gains over AR at the baseline horizon h=1

- Under the primary HLZ test, no MSAR-versus-AR or STAR-versus-AR comparison at h=1 rejects equal accuracy at 5% in the favour of the nonlinear model, for any target (T3.3A). UNRATE is pending F1.
- **One exception, at a robustness horizon.** CPIAUCSL MSAR at h=12 beats AR:
  - OOS R² = 0.042;
  - HLZ p = 0.033 for squared loss and 0.004 for absolute loss.
  - It is a small gain, and it does not depend on the 2020–21 observations [audit].
- **Descriptive, not formal.** MSAR has the lowest h=1 RMSE for GDPC1 (OOS R² 0.292) and INDPRO (0.236). Both gains are almost entirely attributable to the 2020-01 to 2021-06 target dates [audit]:
  - excluding them gives R² −0.051 for GDPC1;
  - and 0.021 for INDPRO.

### 4. STAR is not a credible forecasting model in this design

- Rolling STAR fits frequently put the threshold outside the data and have singular information matrices.
- This produces explosive iterated forecasts, for example CPIAUCSL h=12 RMSE 2.2×10⁹⁹ (T3.3).
- Under the approved rules these forecasts are fragile, not failed, so they remain in the metrics.

### 5. Regime-switching credibility (R1-17, P-03, P-04)

- Full-sample K=2 MSAR is interpretable only for CPIAUCSL.
  - For GDPC1, INDPRO and M2SL, the second regime captures one to three pandemic observations with boundary transitions.
  - For FEDFUNDS the two regimes are identical (T3.2, T4.3).
- K=3 is not credible for any target under the §11.1 rule (T4.3C). The information criteria favour K=3 for five targets, but only through low-occupancy, outlier-type regimes.

### 6. Robustness

The (largely null) forecasting conclusions are stable across:

- transformations;
- CPI lags;
- horizons;
- the VAR;
- estimation windows, where 97 of 108 window-test conclusions are "unchanged" and none gains support for a nonlinear model;
- the October 2025 LOCF imputation.

The VAR never significantly improves on AR.

### Overall answer to the central research question (Part 4 §4)

In this U.S. sample and design, nonlinear state-dependent models do **not** provide statistically credible forecast gains over the AR benchmark at the baseline horizon. Their apparent descriptive gains concentrate in the pandemic episode, and their estimates are mostly fragile. The single robust exception is a modest h=12 MSAR gain for CPI inflation.

---

## A. Numerical and reproducibility audit

### A.1 Provenance

| Item | Value | Source |
|---|---|---|
| Run ID | `baseline-20261030T173044-949fcd76` | RM |
| Code commit / dirty | `46a53181e5e9…` / false | RM |
| Config hash | `949fcd76769048e3…` | RM |
| Data snapshot hash | `7e7dc769bd63ca49…5b832a` (canonical CSV) | RM |
| Parent official snapshot | `7523966b3fb365c8…e576e994` | RM |
| Vintage / cutoff | 2026-10-05 / 2026-08-01 | RM |
| Started | 2026-10-30T17:30:44Z | RM |
| Workers / scheduler | 4 / shared pool | RS |
| Python / platform | 3.11.18 / Linux-6.6.159+ x86_64 glibc 2.39 | `logs/environment.json` |

`git diff 46a5318 0662945` touches only `my-thesis/output/` (460 files).

The run provenance columns (`run_id`, `data_snapshot_hash`, `code_commit_sha`, `config_hash`) are present and constant in every CSV examined.

### A.2 Completeness and integrity

- RS reports 255 files, 67,253 fit records, 34,153 failure events, 0 data-gap events and 350 test results.
- All ten stages completed. Runtimes from RS:
  - forecasting 25,531 s;
  - adequacy 3,625 s;
  - robustness 3,134 s;
  - evaluation 269 s.
- INV has 254 rows and 0 checksum mismatches. INV, `run_summary.json` and `run_manifest.json` do not list themselves. The one-file difference from RS `n_files` was not reconciled further.
- **Limitation.** About 207 companion files are not inventoried, so they are not checksum-covered: provenance sidecars, Parquet twins and `.gitkeep`.
- Every table and figure required by `approved-specs/part5/part5_required_outputs_specification.md` exists. That covers the tables T2.0–T2.5, T3.1–T3.6, T4.1–T4.9 and T4.TP1, and the figures F2.0, F2.1, F3.1–F3.6, F4.3 and F4.8.
- The production `run_logs/` were not committed; only smoke logs are present.

### A.3 Missing values, sample sizes, alignment

**Data gaps and coverage**

- `data_audit/data_gap_register.csv` has 0 rows, and `n_data_gaps = 0` for all 24 baseline chains (FOA).
- The two October 2025 gaps (CPIAUCSL, UNRATE) are filled by the approved raw-level LOCF.
  - They are disclosed row by row in `data_audit/october_2025_imputation_audit.csv`.
  - Exposure (EXP): CPIAUCSL 120 of 11,368 forecast rows, UNRATE 108 of 11,192, and 16 imputed target rows for each.

**Evaluation sample sizes at h=1** (`n_attempted` in T3.3)

| Target | Origins | First target | Last target |
|---|---|---|---|
| GDPC1 | 197 | 1977Q2 | 2026Q2 |
| CPIAUCSL | 715 | 1967-02 | 2026-08 |
| INDPRO | 715 | 1967-02 | 2026-08 |
| UNRATE | 704 | 1968-01 | 2026-08 |
| FEDFUNDS | 625 | 1974-08 | 2026-08 |
| M2SL | 571 | 1979-02 | 2026-08 |

Pairwise comparisons use the intersection of valid dates (decision M7). For example, UNRATE MSAR loses 11 origins to non-convergence (`n_common_with_benchmark` 693, T3.3).

**Estimation windows**

- Windows are 240 monthly observations and 120 quarterly ones. Specifications are fixed on the initial window (T2.5 `fixed_from`).
- In cache-served AR fit records, `window_start` in FR is recorded as the window start, whereas freshly fitted records give the post-lag start. This is a cosmetic inconsistency that predates the run.

**Concern for interpretation: the ARMA specifications**

The ARMA "stronger benchmark" is a genuine ARMA only for UNRATE, ARMA(3,4). For the other five targets the BIC-plus-whiteness rule selected a pure AR (T2.5):

| Target | ARMA selected | AR benchmark | What the ARMA amounts to |
|---|---|---|---|
| CPIAUCSL | (1,0) | AR(2) | an AR(1), a *weaker* model than the benchmark |
| INDPRO | (1,0) | AR(12) | an AR(1), a *weaker* model than the benchmark |
| GDPC1 | (1,0) | AR(1) | the same model re-estimated by ML |
| FEDFUNDS | (1,0) | AR(1) | the same model re-estimated by ML |
| M2SL | (3,0) | AR(3) | the same model re-estimated by ML |

This follows the approved grid: monthly p,q ≤ 4 against an AR search up to p=12 (Part 5 §5.2). It must be stated whenever "ARMA" results are interpreted.

---

## B. Model credibility and convergence

### B.1 Fit-status totals (all 67,253 fits)

| Model family | Adequate | Fragile | Failed |
|---|---|---|---|
| AR | 18,204 | 21 | 78 |
| ARMA | 15,317 | 27 | 99 |
| MSAR (K=2) | 5,109 | 10,252 | 82 |
| STAR | 2,741 | 12,702 | 0 |

These totals are computed from FR and include all baseline and robustness chains; the overall totals are 43,797 adequate, 23,008 fragile and 448 failed.

Baseline per-chain status (T3.3 `n_fragile`, `n_failed`, h=1 row):

| Target | MSAR fragile / failed | STAR fragile / failed |
|---|---|---|
| GDPC1 | 136/197, 0 | 192/197, 0 |
| CPIAUCSL | 431/715, 0 | 569/715, 0 |
| UNRATE | 260/704, 11 | 644/704, 0 |
| INDPRO | 428/715, 0 | 406/715, 0 |
| FEDFUNDS | 474/625, 0 | 474/625, 0 |
| M2SL | 568/571, 0 | 544/571, 0 |

Under §7.5, nonlinear rolling estimates are predominantly fragile. Only UNRATE MSAR has a majority-adequate chain.

### B.2 Full-sample in-sample adequacy (T3.1)

| Target | AR | ARMA | MSAR | STAR |
|---|---|---|---|---|
| GDPC1 | adequate | adequate | fragile (LOW_OCCUPANCY, TRANSITION_BOUNDARY, RESIDUAL_AUTOCORR) | fragile (ILL_CONDITIONED_COV) |
| CPIAUCSL | fragile (RESIDUAL_AUTOCORR) | fragile (RESIDUAL_AUTOCORR) | fragile (RESIDUAL_AUTOCORR) | fragile (RESIDUAL_AUTOCORR) |
| UNRATE | adequate | adequate | fragile (TRANSITION_BOUNDARY, RESIDUAL_AUTOCORR) | fragile (SINGULAR_COV, STAR_THRESHOLD_EXTREME, NEAR_CONSTANT_TRANSITION) |
| INDPRO | adequate | fragile (RESIDUAL_AUTOCORR) | fragile (SINGULAR_COV, LOW_OCCUPANCY, TRANSITION_BOUNDARY, RESIDUAL_AUTOCORR) | fragile (STAR_GAMMA_BOUND, RESIDUAL_AUTOCORR) |
| FEDFUNDS | fragile (RESIDUAL_AUTOCORR) | fragile (RESIDUAL_AUTOCORR) | fragile (RESIDUAL_AUTOCORR) | fragile (STAR_GAMMA_BOUND, RESIDUAL_AUTOCORR) |
| M2SL | fragile (RESIDUAL_AUTOCORR) | fragile (RESIDUAL_AUTOCORR) | fragile (LOW_OCCUPANCY, TRANSITION_BOUNDARY, RESIDUAL_AUTOCORR) | fragile (STAR_GAMMA_BOUND, RESIDUAL_AUTOCORR) |

**Information criteria (T3.1, BIC).**

- MSAR has the lowest BIC against AR for:
  - GDPC1: 1775.0 against 1840.4;
  - CPIAUCSL: 4879.1 against 4995.8;
  - UNRATE: −142.5 against 1029.0;
  - INDPRO: 7289.9 against 7456.2;
  - M2SL: 4460.8 against 4618.3.
- For FEDFUNDS, MSAR's BIC is higher (1078.4 against 1051.3), and its log-likelihood is identical to AR's (−518.894).
- STAR's BIC is lower than AR's for GDPC1, CPIAUCSL, UNRATE, FEDFUNDS and M2SL, but higher for INDPRO (7463.9 against 7456.2).
- Two caveats:
  - effective `n_obs` differs slightly across models because of different lag orders;
  - an in-sample IC improvement driven by a one-observation regime is not evidence of a recurrent nonlinear mechanism.

**Residual diagnostics.**

- Jarque–Bera rejects everywhere (T3.1). Per §7.4 this does not disqualify a point-forecast model.
- ARCH-LM rejects for most models. This motivates T4.6.

### B.3 Markov-switching credibility (T3.2, T4.3; R1-17)

**GDPC1, K=2**

- Regime 1 has μ1 = −38.14, occupancy 0.32%, and effective observations 1.0.
- p11 = 0.0000 and p22 = 0.9968, with expected duration 1.00 quarter for regime 1.
- **Reading:** a single-observation pandemic regime (an outlier dummy), not a business-cycle regime. Status fragile.

**CPIAUCSL, K=2**

- Regime 2 has μ2 = 12.49 (SE 0.64), occupancy 8.6% and 82 effective observations.
- Expected durations are 63.1 and 6.3 months, and the covariance is ok.
- **Reading:** the only interpretable K=2 model, a high-inflation regime. It is fragile only through residual autocorrelation.

**UNRATE, K=2**

- μ1 = −0.14 and μ2 = 10.96, both with SE ≈ 12.1, so the means are poorly identified in levels.
- p11 = 0.9991, which is a transition boundary.
- Regime 2's average smoothed probability is 0.008 in recessions and 0.093 in expansions (T4.3 `recession_expansion_profile`).
- **Reading:** fragile.

**INDPRO, K=2**

- μ1 = −167.80 with 1.0 effective observation.
- The information matrix has a non-positive variance on its diagonal.
- **Reading:** an outlier regime; fragile.

**FEDFUNDS, K=2**

- μ1 = μ2 = 0.0025, so the means are not distinguishable (z ≈ 2×10⁻⁶).
- The transition-probability SEs are 18.06 and 38.26, and the log-likelihood equals AR's.
- **Reading:** an **effectively unidentified** switching model, which under Part 5 §8.1 should be read as a failure. The automatic label is fragile; see F5.

**M2SL, K=2**

- μ2 = 53.72 with 3.0 effective observations, a pandemic-era surge.
- p11 = 1.0000, an absorbing boundary.
- **Reading:** fragile.

**Conclusion on R1-17.** The jury's suspicion of near-absorbing or degenerate transition matrices is **confirmed** for four of six targets in the full-sample K=2 fits. The audit separates:

- genuine but rare episodes (CPI high inflation);
- outlier capture (GDPC1, INDPRO, M2SL);
- poor identification in levels (UNRATE);
- non-identification (FEDFUNDS).

These are statistical-credibility findings, not numerical failures. All fits converged (T4.3 `converged=True`) under a 2-start deterministic search.

### B.4 STAR credibility (T3.2, FR)

Full-sample STAR fits:

| Target | Type | What the fit shows | Covariance |
|---|---|---|---|
| CPIAUCSL | LSTAR | γ = 2.58, c = 3.93 inside the data range | usable |
| GDPC1 | LSTAR | γ = 765.5, an almost abrupt threshold | ill-conditioned, condition number 2.8×10¹⁶ |
| UNRATE | LSTAR | c = 14.8, the sample maximum; G_mean = 0.0005 | singular |
| INDPRO | ESTAR | γ at the bound of 1000; φ ≈ θ (φ0 = 48.46, θ0 = 48.47, SE ≈ 48), the classic ESTAR non-identification | — |
| FEDFUNDS | ESTAR | γ at the bound of 1000 | — |
| M2SL | LSTAR | γ at the bound of 1000 | — |

Only the CPIAUCSL fit is well-behaved (status fragile through residual autocorrelation only).

**Rolling estimates.** STAR_THRESHOLD_EXTREME, SINGULAR_COV and STAR_GAMMA_BOUND are pervasive (T4.8A reason-code counts for the 240-window chains). For example, the M2SL chain has 248 gamma-bound and 129 threshold-extreme flags.

**Mechanism of the explosive forecasts.** At CPIAUCSL origin 1974-01:

- c = 8.88 lies above the 95th percentile of the window (6.96);
- θ0 = −1.5×10¹¹;
- the observed information is singular.

The h=1 forecast is 1.4×10¹¹ against an actual 12.75, and the h=12 forecast is 5.8×10¹⁰⁰ (FR row CPIAUCSL STAR refit 1974-01-01 at window 1954-02 to 1974-01; FC-CPIAUCSL).

This is genuine local non-identification. The regime-2 coefficients are identified by a few extreme observations, and they are extrapolated when a new observation activates the regime. It is **not a coding error**. Part 5 §8.2 and decision D8 classify such fits as fragile, so their forecasts stay in the metrics.

STAR extreme-forecast flags in the baseline 240/120 chains (T4.8A, EXTREME_FORECAST):

| Target | Flags |
|---|---|
| GDPC1 | 1 |
| CPIAUCSL | 15 |
| UNRATE | 85 |
| INDPRO | 72 |
| FEDFUNDS | 23 |
| M2SL | 87 |

### B.5 Genuine nonlinearity versus numerical failure

| Evidence | Targets |
|---|---|
| Pre-estimation nonlinearity: Tsay | UNRATE only (p = 0.0013); all others p ≥ 0.142 (T2.3) |
| Pre-estimation nonlinearity: LST linearity rejected at the selected delay | CPIAUCSL (d=6, p = 2.4×10⁻⁹), UNRATE (d=1, p = 3.2×10⁻⁵), FEDFUNDS (d=1, p = 0.043) (T2.4) |
| Not rejected at the selected delay | GDPC1 (p = 0.454), INDPRO (p = 0.078), M2SL (p = 0.127) (T2.4) |
| Interpretable full-sample nonlinear structure | CPIAUCSL (MSAR and STAR) |
| Outlier capture or non-identification | GDPC1, INDPRO, M2SL, FEDFUNDS |
| Pretest evidence present but estimates degenerate | UNRATE (levels) |

For GDPC1, INDPRO and M2SL the STAR transition is therefore not independently validated (Part 5 §4.2, §4.4).

**Reading.** Genuine, interpretable nonlinearity is supported **for CPI inflation**. Elsewhere, the "nonlinearity" detected by the estimated nonlinear models is predominantly a reaction to the 2020 pandemic outliers or a numerical identification failure.

---

## C. Failures and fragility

### C.1 The 34,153 failure-registry events (T4.7)

The registry has **one row per reason code per fit**. It counts flags, not failed estimations: FRAGILE rows carry `forecast_retained=True`, FAILED rows carry `forecast_retained=False`.

- **540 FAILED-category events.** These come from 448 failed fits (FR):
  - NONCONVERGENCE: 342;
  - UNSTABLE_AR: 105;
  - SINGULAR_COV: 66, attached to non-converged fits;
  - LOW_OCCUPANCY: 10;
  - TRANSITION_BOUNDARY: 9;
  - EXTREME_FORECAST: 6;
  - EMPTY_REGIME: 1;
  - ILL_CONDITIONED_COV: 1.
- **33,613 FRAGILE-category events:**
  - LOW_OCCUPANCY: 8,833;
  - ILL_CONDITIONED_COV: 5,938;
  - STAR_GAMMA_BOUND: 4,941;
  - STAR_THRESHOLD_EXTREME: 4,262;
  - SINGULAR_COV: 4,069;
  - TRANSITION_BOUNDARY: 3,846;
  - NEAR_CONSTANT_TRANSITION: 1,040;
  - EXTREME_FORECAST: 662;
  - RESIDUAL_AUTOCORR: 22.

**Failed fits by model and target (FR status = failed):**

| Model and target | Failed fits | Where they occur |
|---|---|---|
| UNRATE ARMA | 72 | 15 baseline; the rest in window and transformation chains |
| FEDFUNDS AR | 71 | all in the T4.1 *level* alternative, a near-unit root (`UNSTABLE_AR`, root about 1.00) |
| FEDFUNDS MSAR | 52 | all in the T4.1 level alternative |
| UNRATE MSAR | 30 | |
| FEDFUNDS ARMA | 27 | |
| CPIAUCSL ARMA-GARCH | 27 | |
| VAR | 27 | unstable origins, excluded |
| FEDFUNDS ARMA-GARCH | 120 | 19% of 625 origins non-converged |
| UNRATE ARMA-GARCH | 15 | |
| UNRATE AR | 6 | |
| CPIAUCSL AR(p=12) | 1 | T4.2 chain |

The baseline horse-race failures are 34 fits (T3.3, FOA):

- UNRATE: AR 1, ARMA 15, MSAR 11;
- FEDFUNDS: ARMA 7.

No baseline failure occurs for GDPC1, CPIAUCSL, INDPRO or M2SL.

**F1 caveat.** The UNRATE AR failure (2020-04) is scored in the metrics, as are the robustness failures listed in the correction note. Non-converged fits are correctly excluded, because their forecasts are NaN.

**Limitation.** T4.7 has no `exercise` column. Event attribution to an exercise has to be inferred from FR window lengths and specification labels, as done above.

### C.2 The three skipped chains

These are the T4.6 ARMA-GARCH chains for **GDPC1, INDPRO and M2SL**. ARCH-LM on the initial-window residuals of the selected ARMA did not reject at 5% (T4.6T):

| Target | ARCH-LM statistic | Lags | p-value |
|---|---|---|---|
| GDPC1 | 3.456 | 4 | 0.485 |
| INDPRO | 3.602 | 12 | 0.990 |
| M2SL | 12.998 | 12 | 0.369 |

Part 5 §5.3 and decision M9 make ARMA-GARCH conditional on rejection, so the skips are legitimate. They are not failures and appear in no metric.

### C.3 Fragility relevant to interpretation

- FEDFUNDS ARMA-GARCH fails to converge at 120 of 625 origins (T4.6S: 505 converged).
- Per §7.5, fragile nonlinear estimates "cannot support strong economic regime interpretation". This applies to the majority of rolling MSAR and STAR fits (B.1).

---

## D. Forecast performance (baseline, then horizons)

### D.0 Inferential reading rules

- HLZ governs pairwise conclusions (Part 5 §10.2).
- DM-HLN is secondary; disagreements are reported. 11 of 230 comparisons disagree (T3.3B `agrees_with_hlz`).
- **T3.3A/T3.3B sign.** The stored differential is loss(model_a) − loss(model_b), with model_a = AR (or ARMA). A **positive** value therefore favours the second-named model; see F3.
- **Multiple testing.** 18 of 226 available HLZ tests reject at 5% (T3.3A). That is about 11 rejections expected under a global null if the tests were independent; they are not.
  - 15 of the 18 concern CPIAUCSL and mostly reflect the weak CPI "ARMA".
  - No family-wise correction is part of the approved design, so isolated rejections are treated as weak evidence.
- **STAR tests are uninformative.**
  - In 51 of 88 available STAR-pair HLZ tests the p-value lies in [0.30, 0.34] [audit A4]. This is the signature of a loss differential dominated by one or two explosive forecasts: the studentised mean tends to about ±1.
  - 4 STAR squared-loss tests are unavailable because Ω̂′ is non-finite (CPIAUCSL h=12; M2SL h=12).
  - STAR pairwise p-values therefore carry no information about typical STAR accuracy.

### D.1 Baseline h=1 accuracy (T3.3; RMSE, OOS R² against AR, HLZ two-sided p for squared and absolute loss)

| Target | AR RMSE | ARMA RMSE (R²; HLZ p sq/abs) | MSAR RMSE (R²; HLZ p) | STAR RMSE (R²; HLZ p) |
|---|---|---|---|---|
| GDPC1 | 5.284 | 5.246 (0.014; 0.368/0.758) | **4.447** (0.292; 0.357/0.626) | 5.123 (0.060; 0.584/0.328) |
| CPIAUCSL | 2.967 | 3.075 (−0.074; 0.099/**0.010**, AR better) | **2.966** (0.0003; 0.975/0.398) | 5.38×10⁹ (−3.3×10¹⁸; 0.325/0.325) |
| UNRATE ⚠F1 | 0.886* | 0.737 (0.323*; 0.310/0.414) | **0.492** (0.690*; 0.319/0.286) | 0.592 (0.554*; 0.390/0.469) |
| INDPRO | 13.311 | 11.974 (0.191; 0.266/0.247) | **11.638** (0.236; 0.232/0.121) | 7.17×10⁶ (−2.9×10¹¹; 0.325/0.325) |
| FEDFUNDS | **0.4753** | 0.4770 (0.000; 0.969/0.335) | 0.4799 (−0.019; 0.499/0.987) | 0.6125 (−0.661; 0.122/**0.029**, AR better) |
| M2SL | **5.078** | 5.083 (−0.002; 0.426/0.828) | 5.127 (−0.020; 0.236/0.871) | 82.75 (−264.6; 0.327/0.300) |

\* Affected by F1. Excluding only the failed AR origin [audit A2]:

- UNRATE AR RMSE is 0.551;
- the OOS R² values become ARMA 0.237, MSAR 0.190 and STAR −0.103.

**Formal evidence at h=1**

- No HLZ rejection favours MSAR or STAR over AR, or over ARMA, for any target.
- **CPIAUCSL:**
  - AR beats ARMA under absolute loss (p = 0.010);
  - MSAR beats ARMA under absolute loss (p = 0.027, T3.3A ARMA–MSAR row).
- **FEDFUNDS:** AR and ARMA beat STAR under absolute loss (p = 0.029 and 0.030).
- **UNRATE:** ARMA beats STAR under absolute loss (p = 0.042). This comparison is not affected by F1.
- **DM-HLN alone** rejects for INDPRO in favour of MSAR (squared p = 0.018, absolute p = 0.0024) and ARMA (absolute p = 0.017). HLZ does not (p = 0.23, 0.12 and 0.25). Per §10.3 the principal conclusion follows HLZ. The disagreement is consistent with a time-varying loss differential, which is exactly the case HLZ is designed for.

**Model Confidence Set, h=1** (T3.4)

- At 90% and 95%, all available cells retain AR, ARMA and MSAR. STAR is retained everywhere except FEDFUNDS absolute loss, at both 90% and 95% (MCS p = 0.045).
- **CPIAUCSL absolute loss at 90%:** ARMA is excluded (p = 0.075).
- **CPIAUCSL squared loss:** the MCS is **unavailable** (F2).
- No target's MCS reduces to a nonlinear model alone.

**Descriptive ranking versus formal superiority**

- MSAR has the lowest h=1 RMSE for GDPC1, CPIAUCSL (by 0.0005), UNRATE (pending F1) and INDPRO.
- It is formally superior for none.
- **Sensitivity [audit A3].** Removing target dates 2020-01 to 2021-06, i.e. 6 quarters or about 18 months, changes the OOS R²:

  | Target and model | OOS R², all dates | OOS R², without 2020-01 to 2021-06 |
  |---|---|---|
  | GDPC1 MSAR | 0.292 | −0.051 |
  | GDPC1 ARMA | 0.014 | −0.004 |
  | INDPRO MSAR | 0.236 | 0.021 |
  | INDPRO ARMA | 0.191 | −0.005 |
  | UNRATE MSAR (excluding failed AR) | 0.190 | −0.001 |

- About 97–106% of the total squared-loss advantage lies in that window.
- This sensitivity is **not** an approved test. It is reported because it determines how any descriptive gain may be worded.

### D.2 Longer horizons (T3.3, T3.3A, T4.4P; P-05)

**GDPC1**

- MSAR has the lowest RMSE at h=2 (4.393) and h=4 (4.348). The OOS R² values are 0.088 and 0.049.
- No HLZ rejection.
- STAR is worst at h=4 (R² −0.400).

**CPIAUCSL**

- ARMA (an AR(1)) is significantly worse than AR at every horizon under HLZ:
  - h=3: squared p = 0.031, absolute p = 0.0013;
  - h=6: 0.0022 and < 0.0001;
  - h=12: 0.0013 and 0.0020.
- MSAR is significantly better than ARMA at h=3 (absolute), h=6 and h=12.
- **MSAR is significantly better than AR only at h=12:**
  - OOS R² 0.042;
  - HLZ squared p = 0.033, absolute p = 0.0044;
  - DM-HLN squared p = 0.108, absolute p = 0.031 (T3.3A/T3.3B AR–MSAR rows; T4.4P).
- At h=12 the 90% absolute-loss MCS excludes only ARMA (p = 0.042, T3.4).
- The gain does not depend on 2020–21: R² excluding that window is 0.044 [audit A3].
- **This is the one nonlinear-over-AR rejection in the baseline horse race.** It is small, at one robustness horizon, and one of many tests.

**INDPRO**

- ARMA, here an AR(1), ranks first by RMSE at h=3, 6 and 12. MSAR is second or third.
- No HLZ rejection.
- At h=12 the 90% absolute-loss MCS excludes AR and MSAR (both p = 0.09) and keeps ARMA and STAR.

**FEDFUNDS**

- Differences across AR, ARMA and MSAR are below 1% of RMSE at every horizon.
- No rejection.

**M2SL**

- AR or ARMA ranks first at every horizon. MSAR is worse (R² between −0.020 and −0.108).
- No rejection.

**UNRATE** (F1 affects every AR-relative number)

- Published AR RMSE is 3.28, 11.31 and 78.17 at h=3, 6 and 12. Excluding the failed origin it is 0.94, 1.17 and 1.49 [audit A2].
- MSAR's corrected OOS R² is negative at h=3, 6 and 12 (−0.128, −0.538, −0.959) [audit].
- ARMA's corrected R² is 0.056, −0.137 and 0.093.
- No conclusion is drawn until regeneration.

**STAR** iterated forecasts explode at h ≥ 3 for every monthly target (T3.3).

**Reading for P-05.** Longer horizons do not reveal a systematic nonlinear advantage. The CPI h=12 MSAR gain is the only formally supported improvement over AR.

### D.3 State-conditioned evaluation (T3.5S, T3.5R, T3.6, TP1)

**Descriptive (T3.5S, h=1)**

- GDPC1 MSAR has the lowest RMSE in expansions (3.666 against AR 4.725) and in the turning-point window (8.870 against 11.256).
- It is narrowly lowest in recessions (8.231 against AR 8.382), but not outside turning windows (2.656 against AR 2.566).
- With 23 recession and 35 turning-window quarters, these cells are dominated by 2020.
- For CPIAUCSL, INDPRO, FEDFUNDS and M2SL, the state-specific RMSE ordering of AR, ARMA and MSAR is close, with no consistent nonlinear advantage in recessions.

**Inferential (T3.5R)** — the ex-post state-dependent forecast-loss regression, deliberately not labelled Giacomini–White (decision M1)

- 67 of 69 regressions are estimable. CPIAUCSL STAR h=12 and M2SL STAR h=12 are unavailable because the HAC covariance is non-finite.
- The turning-point coefficient is significant at 5% only for FEDFUNDS ARMA versus AR at h=6 (β_turn p = 0.031).
- Joint tests reject for CPIAUCSL ARMA at h=3, 6 and 12 (p = 0.0025, 0.0005 and 0.026). These rejections come from the intercept (ARMA uniformly worse), not from the state terms: slopes p = 0.22, 0.34 and 0.39.
- The state slopes are jointly significant only for:
  - INDPRO ARMA h=3 (p = 0.022);
  - FEDFUNDS MSAR h=6 (p = 0.043).
- **No MSAR- or STAR-versus-AR turning-point or recession coefficient supports a nonlinear gain concentrated in bad times.** UNRATE rows involving AR are affected by F1.

**Turning-window sensitivity (TP1)**

- The only baseline-width support (FEDFUNDS ARMA h=6) is lost at ±1 and ±6 months.
- `alternative_support_5pct` is False in all 207 rows.

---

## E. Do MSAR and STAR improve credibly on AR and ARMA?

| Dimension | MSAR | STAR |
|---|---|---|
| In-sample fit (T3.1 BIC) | Better than AR for 5 of 6 targets; for GDPC1, INDPRO and M2SL through one-to-three-observation regimes | Better than AR for 5 of 6 targets; INDPRO worse |
| Credibility (T3.2, B.3–B.4) | Interpretable only for CPIAUCSL; FEDFUNDS unidentified; the rest are outlier or boundary regimes | Interpretable only for CPIAUCSL; widespread non-identification |
| OOS accuracy h=1 (T3.3) | Lowest RMSE for 4 targets, gains concentrated in 2020–21 [audit] | Worst or explosive for 5 of 6 targets; UNRATE STAR beats the F1-inflated AR only |
| Significance (HLZ) | None at h=1; CPIAUCSL h=12 against AR (p = 0.033/0.004) | None in its favour; significantly worse for FEDFUNDS h=1 absolute loss |
| Economic interpretation | CPI high-inflation regime (μ = 12.5% annualised, 6.3-month duration) is descriptive only; no economic labels per §11.1 | None credible |
| Causal | None (CLAUDE.md §11) | None |

**Verdict**

- **MSAR**: QUALIFIED for CPI inflation at the 12-month horizon. INCONCLUSIVE to NOT_SUPPORTED elsewhere. UNRATE is INCONCLUSIVE pending F1.
- **STAR**: NOT_SUPPORTED as a forecasting improvement for any target. The genuinely credible finding about STAR is its *fragility* under rolling re-estimation.

---

## F. Robustness (detail in `robustness_findings.md`)

| Exercise | Threat (Part 5 §11) | Result | Effect on conclusions |
|---|---|---|---|
| T4.1 transformations (UNRATE in differences, FEDFUNDS in levels) | Transformation drives the ranking | No HLZ rejection in 12 tests (T4.1P). UNRATE STAR in differences explodes (RMSE 20.75). FEDFUNDS level MSAR fails 52 of 626 fits (T4.1) | Unchanged (F1 affects the AR rows) |
| T4.2 CPI lags (R1-15) | The p=12 lag drives the result | p=1 RMSE 3.073; p=3 2.958; p=6 2.969; p=12 2.969 (T4.2) against baseline p=2 2.967 (T3.3). Only p=3 beats p=1 under HLZ, absolute loss, p = 0.012 (T4.2P) | p=12 is unnecessary; BIC p=2 is adequate |
| T4.3 regime count (P-04) | Two regimes are too restrictive | K=3 is not credible for any target; ICs favour K=3 for 5 targets through outlier regimes; the UNRATE comparison is invalid (F6) | K=2 retained; but K=2 itself is weak for 4 targets |
| T4.4 horizons (P-05) | Gains appear only at h=1 | See D.2; 10 of 138 HLZ rejections, all CPIAUCSL ARMA or MSAR versus AR, plus FEDFUNDS STAR (T4.4P) | No systematic nonlinear advantage at longer horizons |
| T4.5 VAR(1) (R1-19, P-01) | Omitted cross-variable information | VAR never significantly better than AR; significantly worse for FEDFUNDS under absolute loss (HLZ p = 0.0036, T4.5P) | Univariate conclusions stand |
| T4.6 ARMA-GARCH | Ignored conditional variance | ARCH effects in CPIAUCSL, UNRATE and FEDFUNDS; persistence 0.83, 0.55 and 0.97 (T4.6S) | Diagnostic only |
| T4.8 windows 180/240/300 and 90/120/150 | Window choice drives the ranking | 97 of 108 conclusions unchanged, 10 "reversed" (insignificant sign flips), 1 weakened, none newly supporting a nonlinear model (T4.8P) | Conclusions are window-robust |
| T4.9 LOCF exposure | Imputation distorts the results | Pre-gap metrics almost identical: for example CPIAUCSL AR RMSE 2.950 against 2.967 (T4.9) | Negligible |
| T4.TP1 turning windows | Turning-window width | No support at any alternative width | No turning-point claim |

**Regime count, answered explicitly (P-04).** The question is whether a third regime is credible and whether it challenges K=2.

- **Not credible for any target** (T4.3C `k3_credible = False`, all six).
- **CPIAUCSL is the near miss.** K=3 fails only the 5% occupancy threshold:
  - regime 1 has occupancy 2.24% and 21.4 effective observations, a deflation-spike regime (μ1 = −6.65);
  - the covariance is usable, and the means are distinguishable (minimum z = 10.99).
- **What this means for K=2.** The third regime does not challenge K=2 as a *credible alternative*. But the exercise shows the real limitation lies elsewhere: for four targets, K=2 already spends its second regime on outliers or is unidentified.
- **No forecasting claim** is made for K=3 (§11.1). No ordinary chi-square likelihood-ratio test is reported (§4.3).

---

## G. Jury resolution

See `jury_resolution_status.md`. In summary, for the empirically testable remarks:

- **Resolved:** R1-07, R1-09, R1-12, R1-13, R1-15, R1-17, R1-18, R1-19, R1-23, P-01, P-03, P-04 and P-05.
- **Partially addressed pending corrections:** R1-06, R1-14, R1-22 and P-02.
- **Outside empirical scope:** R1-01 to R1-05, R1-08, R1-10, R1-11 (textual part), R1-16, R1-20, R1-21 and P-06.

---

## H0. Correction-phase addenda (2 November 2026)

**CPI h=12 and multiplicity.**
- Within the 46 MSAR-versus-AR HLZ tests (T3.3A), Holm-adjusted p-values for CPIAUCSL h=12 are 0.204 (absolute loss) and 1.0 (squared loss). This is a Part 8 audit computation.
- The result is an unadjusted 5% rejection. It is not evidence of a systematic nonlinear advantage.
- Throughout this report, non-rejection means "no evidence of a difference", not "equal accuracy".

**FEDFUNDS K=2 (F5, interpretation only).**
- The full-sample FEDFUNDS two-regime MSAR is **effectively unidentified**:
  - its regime means are equal (0.0025);
  - the transition-probability SEs are 18.06 and 38.26;
  - its log-likelihood equals AR(1)'s (−518.894; T3.1, T3.2, T4.3).
- Its automatic status remains *fragile*. No new automatic classification rule is introduced.

**F4 preview.** Zivot–Andrews on the levels, intercept-and-trend break, from `corrections/f4_zivot_andrews_preview.csv`. This is not an `output/` file until regeneration.

| Series | Sample | Statistic | p-value | Break |
|---|---|---|---|---|
| UNRATE | initial window | −4.556 | 0.189 | 1957-08 |
| UNRATE | full sample | −4.606 | 0.169 | 2008-04 |
| FEDFUNDS | initial window | −3.500 | 0.811 | 1970-10 |
| FEDFUNDS | full sample | −4.290 | 0.320 | 1984-08 |

- The baseline transformations are unchanged (§3.4: ADF and KPSS agree).
- For UNRATE, the break-allowing test does not reject a unit root, so the level-stationarity conclusion rests on ADF and KPSS alone.

**F6.** The UNRATE K=2/K=3 information-criterion comparison is INCONCLUSIVE; see `corrections/correction_plan.md` §F6.

## H. Limitations

1. **F1–F6.** These are described in the correction note. UNRATE AR-relative evidence is provisional.
2. **Single country.** The design covers one country (P-06) and uses a pseudo-out-of-sample evaluation on revised data, so it says nothing about real-time nowcasting (R1-20).
3. **Few episodes.** There are 23 recession quarters for GDPC1 and 58 to 85 recession months for the monthly targets (T3.5R `n_recession`). State-specific inference has low power, and the 2020 episode dominates squared-error metrics.
4. **Search depth.** MSAR used 2 deterministic starts, and the likelihoods are multimodal (F6). Different local optima are plausible across rolling origins.
5. **Machine dependence.** Most results depend on the machine only at the last digits (OpenBLAS kernel selection).
   - **Not so for the full-sample MSAR optima.** The correction-phase F6 study refitted them on a different platform with the unchanged code:
     - INDPRO K=2 log-likelihood: −3627.97 here against −3614.10 published;
     - M2SL K=2: −2185.27 against −2203.65;
     - UNRATE K=2 and K=3 also differ.
     - Source: `corrections/f6_k3_nesting_feasibility.csv`.
   - Under the 2-start rule the MSAR likelihood optimum reached is platform-sensitive. T3.1, T3.2 and T4.3 MSAR numbers are therefore reproducible on the publication's platform class only.
   - The published INDPRO K=3 is also not a global maximum: a nesting-informed start reaches −3550.31 against −3563.27.
6. **No multiple-testing correction.** None is part of the approved design. Isolated 5% rejections among 226 or more tests must be worded cautiously.
7. **No STAR robustness measure.** STAR metrics are dominated by retained extreme forecasts, as the approved rules require. Any trimmed or robust-loss reading would be a new, unapproved procedure, and none is reported.
