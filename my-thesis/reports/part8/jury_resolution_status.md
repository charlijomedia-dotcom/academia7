# Part 8 — Jury resolution status

**Remark IDs** are the permanent IDs from `approved-specs/part2/part2_jury_remark_registry.md`. Prof. Verne's constraints (V-04 to V-07) come from `approved-specs/part5/part5_methodology_vs_jury_matrix.md`.

> **Correction phase, 2 November 2026.** These statuses describe the *original* publication, the results commit `0662945`. Corrections F1–F4 are implemented and tested on branch `part8-corrections`, but the outputs have **not yet been regenerated**. Remarks whose evidence depends on an affected table are therefore classified as PARTIALLY ADDRESSED until the corrected outputs are produced and re-audited (see `corrections/correction_plan.md`). The classification was reconsidered at your request: R1-13, R1-15, R1-19, P-04 and P-05 moved from RESOLVED to PARTIALLY ADDRESSED.

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

**Rule (CLAUDE.md §12).** A remark is satisfied by properly performing and reporting the requested analysis, whatever the result.

**Categories**

- **RESOLVED** — the requested analysis was performed and reported completely.
- **PARTIALLY ADDRESSED** — the analysis was performed, but part of it is missing or affected by a documented defect.
- **UNRESOLVED** — not performed.
- **OUTSIDE EMPIRICAL SCOPE** — the remark concerns writing, structure or presentation, and is answered in Parts 4, 5 or 9 rather than by `output/`.

**Paths.** All are relative to `output/`. The correction references F1–F7 point to `notes/claude/part8_audit_findings_and_correction_proposals_2026-11-01.md`.

## Reviewer 1 (P. de Peretti)

**R1-01 — Research architecture**
- **Status:** OUTSIDE EMPIRICAL SCOPE.
- **Evidence:** Part 4 structure.
- **Remaining action:** Part 9.

**R1-02 — TeX and typographical errors, notation changes**
- **Status:** OUTSIDE EMPIRICAL SCOPE.
- **Remaining action:** Part 9.

**R1-03 — Acronyms**
- **Status:** OUTSIDE EMPIRICAL SCOPE.
- **Remaining action:** Part 9.

**R1-04 — Symbols and invariant notation**
- **Status:** OUTSIDE EMPIRICAL SCOPE.
- **Remaining action:** Part 9.

**R1-05 — Authorship of theorems**
- **Status:** OUTSIDE EMPIRICAL SCOPE.
- **Remaining action:** Part 9.

**R1-06 — Misleading figures**
- **Status:** PARTIALLY ADDRESSED.
- **Evidence:**
  - The failure-aware figure design exists. F3.4 has a separate diagnostic panel, and extreme forecasts are flagged (`figures/F3.4_*`).
  - Two defects remain:
    - the main UNRATE panel plots the FAILED AR forecast spike;
    - the diagnostic panel connects non-adjacent flagged points with lines (F7.2).
- **Remaining action:** approve F1 and F7.2, then regenerate the F3.x figures.

**R1-07 — Uncertainty on cross-correlation displays**
- **Status:** RESOLVED.
- **Evidence:** No cross-correlation figure is produced. Part 5 permits "95% bands … or no cross-correlation figure" (figure inventory in `figures/`).
- **Remaining action:** If Part 9 adds one, it must carry bands.

**R1-08 — Self-contained theory chapter**
- **Status:** OUTSIDE EMPIRICAL SCOPE.
- **Remaining action:** Part 9.

**R1-09 — Criterion behind "better"**
- **Status:** RESOLVED.
- **Evidence:**
  - "Better" is defined by RMSE, MAE and OOS R² against AR, plus HLZ (primary), DM-HLN and MCS (`forecast_tests/T3.3_main_forecast_table.csv`, `T3.3A`, `T3.3B`, `T3.4`).
  - The descriptive rank and formal support are reported separately.
- **Remaining action:** Part 9 must keep that distinction (`final_claims_allowed.md`).

**R1-10 — Define nonlinearity and its forms**
- **Status:** OUTSIDE EMPIRICAL SCOPE for the definitions.
- **Evidence:** The empirical support is that discrete MSAR and smooth STAR are estimated and diagnosed separately (`models/T3.2_nonlinear_credibility.csv`).
- **Remaining action:** Part 9.

**R1-11 — Markov-switching and Markov chain exposition**
- **Status:** PARTIALLY ADDRESSED; only the empirical part is in Part 8's scope.
- **Evidence:** Transition matrices, occupancy, expected durations, boundary flags and standard errors are reported for K=2 and K=3 (`models/T3.2_nonlinear_credibility.csv`, `robustness/T4.3_regime_count.csv`, `robustness/T4.3_regime_parameters.csv`).
- **Remaining action:** The textual rebuild belongs to Part 9.

**R1-12 — Variable definitions and data choices**
- **Status:** RESOLVED.
- **Evidence:**
  - `data_audit/T2.0_concept_series.csv`, `T2.1_data_dictionary.csv` and `manifests/T2.0A_frozen_manifest.csv`.
  - The canonical CSV hash `7e7dc769…`.
  - The T2.0B LOCF audit (`data_audit/october_2025_imputation_audit.csv`).
- **Remaining action:** Minor: T2.1 still shows "pending stationarity decision" for UNRATE and FEDFUNDS (F7.1). Use T2.2D for those transformations.

**R1-13 — Every test defined: H0, distribution, decision**
- **Status:** PARTIALLY ADDRESSED. Every test produced is fully defined, but the Part 5 §3.2 Zivot–Andrews test is missing from the original outputs (F4: implemented, awaiting regeneration).
- **Evidence:** Each diagnostic row carries the name, null hypothesis, statistic, reference distribution, p-value, 5% decision and implication (`diagnostics/all_test_results.csv`, 350 rows; T2.2, T2.3, T3.2 residual tests).
- **Remaining action:** The Zivot–Andrews test is absent (see P-02).

**R1-14 — Modern forecast-comparison testing**
- **Status:** PARTIALLY ADDRESSED.
- **Evidence:**
  - Performed:
    - HLZ (2025), the primary test: 230 rows, 4 unavailable (`forecast_tests/T3.3A_hlz_pairwise.csv`);
    - DM-HLN (T3.3B);
    - the ex-post state-dependent loss regression, deliberately not labelled Giacomini–White (decision M1): 67 of 69 rows available (`T3.5_state_loss_regression.csv`);
    - the MCS (T3.4).
  - Clark–McCracken and Amisano–Giacomini were excluded with the reasons given in Part 5 §10.6.
  - **Gaps:**
    - the MCS is unavailable in 11 of 34 baseline cells (CPIAUCSL and M2SL) and in 2 window-length cells (F2);
    - the T3.3A/T3.3B sign-convention label is reversed (F3);
    - UNRATE AR-relative tests are affected by F1.
- **Remaining action:** F1, F2 (guarded MCS, validated against `arch`) and F3 are implemented and tested. Regenerate and re-audit.

**R1-15 — CPI lag structure**
- **Status:** PARTIALLY ADDRESSED, pending regeneration. The substantive answer is not expected to change, but the AR(p=12) row scores one FAILED origin (1974-09; F1) and must be regenerated.
- **Evidence:**
  - BIC selects p=2 (`diagnostics/T2.5_selected_specs.csv`).
  - Under p=1, 3, 6 and 12 robustness (`robustness/T4.2_cpi_lag_robustness.csv`, `_predictive_tests.csv`), p=12 brings no gain: RMSE 2.969 against 2.967 for p=2.
  - F2.1 and F3.x show the CPI series and fits.
- **Remaining action:** Minor F1 effect on the p=12 row (one failed origin).

**R1-16 — Significance notation**
- **Status:** OUTSIDE EMPIRICAL SCOPE.
- **Evidence:** Outputs carry a `stars` column for 10/5/1%.
- **Remaining action:** Part 9 typesetting.

**R1-17 — Suspicious Markov-switching transition results**
- **Status:** RESOLVED.
- **Evidence:**
  - Reproduced and audited: convergence, occupancy, boundary flags, durations and covariance status (`models/T3.2_nonlinear_credibility.csv`, `robustness/T4.3_regime_count.csv`, `robustness/T4.7_failure_registry.csv`).
  - The finding **confirms** the jury's concern: near-absorbing or one-observation regimes for GDPC1, INDPRO, M2SL and UNRATE, and non-identification for FEDFUNDS. Only CPIAUCSL has a credible K=2.
- **Remaining action:** Optionally, F5: an identification flag for FEDFUNDS.

**R1-18 — Nonlinearity tests before nonlinear models**
- **Status:** RESOLVED.
- **Evidence:**
  - The Tsay test (`diagnostics/T2.3_tsay.csv`) and the LST/Teräsvirta sequence (`diagnostics/T2.4_star_linearity.csv`) were run before estimation.
  - Linearity is rejected for UNRATE (both tests), CPIAUCSL and FEDFUNDS (LST only). It is not rejected for GDPC1, INDPRO or M2SL.
  - No naive Markov-switching chi-square LR test is used (§4.3).
- **Remaining action:** none.

**R1-19 — Multivariate dimension**
- **Status:** PARTIALLY ADDRESSED, pending regeneration. The VAR exercise was performed; the UNRATE comparison uses the F1-affected AR benchmark.
- **Evidence:** A monthly five-variable VAR(1) robustness exercise (`robustness/T4.5_var_*`). The VAR never significantly beats AR, and is significantly worse for FEDFUNDS under absolute loss.
- **Remaining action:** The UNRATE AR benchmark row is affected by F1. The limits of a linear VAR must be stated in Part 9.

**R1-20 — Nowcasting and mixed frequency**
- **Status:** OUTSIDE EMPIRICAL SCOPE, as a declared scope boundary.
- **Evidence:** Part 5 §12. There are no real-time vintages, and GDP is not interpolated.
- **Remaining action:** Part 9 states the boundary.

**R1-21 — Lighten the theory**
- **Status:** OUTSIDE EMPIRICAL SCOPE.
- **Remaining action:** Part 9.

**R1-22 — Verify and broaden the econometric results**
- **Status:** PARTIALLY ADDRESSED.
- **Evidence:**
  - Full reproducible run from the frozen, hash-verified CSV (`manifests/run_manifest.json`; 0 checksum mismatches in `manifests/output_inventory.csv`).
  - Failures visible (`robustness/T4.7_failure_registry.csv`).
  - Robustness exercises T4.1–T4.9 and TP1 run.
  - **But** the Part 8 audit found defects that must be corrected before the evidence is final: F1 (material), F2 and F4.
- **Remaining action:** Approve and run the corrections, then re-audit the affected tables.

**R1-23 — M2 sample and relevance**
- **Status:** RESOLVED.
- **Evidence:**
  - M2SL raw sample 1959-01 to 2026-08, transformed 1959-02 to 2026-08 (`data_audit/T2.1_data_dictionary.csv`).
  - h=1 evaluation 1979-02 to 2026-08 with 571 origins (`forecast_tests/T3.3_main_forecast_table.csv`).
  - No model beats AR for M2SL.
- **Remaining action:** Part 9 gives the economic justification.

## President of the jury

**P-01 — Justify and delimit the single-equation architecture**
- **Status:** RESOLVED empirically.
- **Evidence:** The VAR robustness block (T4.5) is the alternative-explanation check. Univariate conclusions survive it.
- **Remaining action:** Part 9 states what single-equation models identify.

**P-02 — Stationarity of UNRATE and FEDFUNDS over the full sample, including a break-allowing test**
- **Status:** PARTIALLY ADDRESSED.
- **Evidence:**
  - ADF and KPSS were run on both the initial window and the full sample (`diagnostics/T2.2_stationarity.csv`).
    - UNRATE is level-stationary: full-sample ADF p = 0.0028 and KPSS p = 0.078.
    - FEDFUNDS has a unit root: ADF p = 0.129 and KPSS p ≤ 0.01.
    - The full sample agrees with the baseline rule (T2.2D).
  - **No Zivot–Andrews result or break date is reported.** ZA was coded only as the §3.4 tie-breaker and was never triggered (F4).
- **Remaining action:** F4 is implemented, and a read-only preview is in `corrections/f4_zivot_andrews_preview.csv`:
  - UNRATE: ZA does not reject a unit root (initial window p = 0.189, break 1957-08; full sample p = 0.169, break 2008-04).
  - FEDFUNDS: ZA does not reject a unit root (initial window p = 0.811, break 1970-10; full sample p = 0.320, break 1984-08).
  - The §3.4 transformations are unchanged, because ADF and KPSS agree.
  - For UNRATE the break-allowing test does *not* corroborate the ADF rejection, which weakens the level-stationarity reading. This must be reported.
  - Status becomes RESOLVED only after regeneration.

**P-03 — Diagnose the extreme policy-rate Markov-switching result**
- **Status:** RESOLVED.
- **Evidence:**
  - Under the approved differencing, the full-sample FEDFUNDS K=2 MSAR collapses to the linear AR(1):
    - identical regime means, 0.0025;
    - unidentified transition probabilities, with SE 18 and 38;
    - log-likelihood −518.894, the same as AR (`models/T3.2_nonlinear_credibility.csv`, `models/T3.1_in_sample_adequacy.csv`).
  - K=3 isolates a 2-observation regime and a 20-observation regime (`robustness/T4.3_regime_count.csv`).
  - In the level alternative, MSAR fails at 52 of 626 origins (`robustness/T4.1_transformation_robustness.csv`).
  - The audit therefore separates three things:
    - the transformation issue (levels are near-unit-root and numerically unstable);
    - the absence of a mean-switching signal in the differenced rate;
    - no numerical failure under the baseline.
  - The old extreme result is not reproduced.
- **Remaining action:** F5, optionally: label the K=2 fit as unidentified.

**P-04 — Three-regime robustness**
- **Status:** PARTIALLY ADDRESSED.
  - The exercise was performed for all six targets and K=3 is not credible for any of them.
  - The published UNRATE K=3 estimate is not a global maximum (log-likelihood below K=2's, although K=3 nests K=2), so the UNRATE in-sample comparison is INCONCLUSIVE.
  - The F6 numerical review is in `corrections/f6_k3_nesting_feasibility.csv`. Any modification of T4.3 needs your approval.
- **Evidence:**
  - Full-sample K=2 against K=3 for all six targets, per amended §11.1 (`robustness/T4.3_regime_count.csv`, `_conclusion.csv`, `T4.3_regime_parameters.csv`, `figures/F4.3_*`).
  - K=3 is not credible for any target.
  - The information criteria favour K=3 for five targets, through outlier regimes.
  - K=2 is retained as predeclared.
  - The UNRATE comparison is inconclusive (non-global K=3 optimum; F6).
  - "Useful" is judged in-sample only, by design: no K=3 forecasts were made.
- **Remaining action:** Decide whether to approve the nesting-informed K=3 start (F6). Until then, report UNRATE as inconclusive.

**P-05 — One-step horizon limitation**
- **Status:** PARTIALLY ADDRESSED, pending regeneration. Horizons were evaluated, but the UNRATE multi-step AR comparisons are dominated by the F1 failed forecast.
- **Evidence:** h = 3, 6 and 12 months and h = 2 and 4 quarters (`forecast_tests/T3.3_main_forecast_table.csv`, `robustness/T4.4_horizon_*`). Longer horizons give no systematic nonlinear gain; the exception is CPIAUCSL MSAR at h=12.
- **Remaining action:** UNRATE multi-step results are pending F1.

**P-06 — External validity and transferability**
- **Status:** OUTSIDE EMPIRICAL SCOPE, with a delimiting statement.
- **Evidence:** All results are U.S.-specific. The transferable part is the design: adequacy before forecasting, failure visibility, HLZ, MCS and threat-based robustness (`final_claims_allowed.md`).
- **Remaining action:** Part 9.

## Prof. Verne constraints

- **V-04 (AR and ARMA benchmarks; ARCH/GARCH where present):** RESOLVED.
  - Both benchmarks are in the horse race.
  - ARMA-GARCH ran where ARCH-LM rejected (CPIAUCSL, UNRATE, FEDFUNDS) and was legitimately skipped elsewhere (`robustness/T4.6_*`).
  - Caveat: "ARMA" is a pure AR for 5 of 6 targets (T2.5).
- **V-05 (recession, expansion and turning-point evaluation):** RESOLVED (T3.5, T3.6, TP1). There is no significant state dependence for the nonlinear models.
- **V-06 (adequacy before forecast ranking):** RESOLVED (T3.1, T3.2, then T3.3).
- **V-07 (outputs ready for Part 9 synthesis):** PARTIALLY ADDRESSED. The outputs are structured, but F1, F2 and F4 must be settled first.

## Summary count (29 Part 2 remarks)

| Status | Count | Remarks |
|---|---|---|
| RESOLVED | 8 | R1-07, R1-09, R1-12, R1-17, R1-18, R1-23, P-01, P-03 |
| PARTIALLY ADDRESSED | 10 | R1-06, R1-11 (empirical part only), R1-13, R1-14, R1-15, R1-19, R1-22, P-02, P-04, P-05 |
| UNRESOLVED | 0 | — |
| OUTSIDE EMPIRICAL SCOPE | 11 | R1-01, R1-02, R1-03, R1-04, R1-05, R1-08, R1-10, R1-16, R1-20, R1-21, P-06 |

After the approved targeted regeneration and re-audit, R1-06, R1-13, R1-14, R1-15, R1-19, R1-22, P-02 and P-05 are expected to become RESOLVED. P-04 depends on the F6 decision. R1-11 stays partial (its textual part is Part 9).
