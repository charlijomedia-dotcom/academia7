# Part 8 — Jury resolution status (final)

**Remark IDs** are the permanent IDs from `approved-specs/part2/part2_jury_remark_registry.md`. Prof. Verne's constraints (V-04 to V-07) come from `approved-specs/part5/part5_methodology_vs_jury_matrix.md`.

> **FINAL PART 8 REPORT — release `part8-final-20261109`.** <!--PUB:status-->**Not yet published.** The release commit and Drive folder do not exist yet. Until `finalize_reports.py` records the verified publication, these reports and their numbers are not citable (CLAUDE.md §9).<!--/PUB:status-->
>
> - **Authoritative numbers.** `my-thesis/output/` in the release commit on branch `part8-corrected-results/final-20261109`: 465 files, listed with sha256 in `my-thesis/release/part8_final/release_inventory.csv`. See `SOURCE_OF_TRUTH.md` in this directory.
>   - `output/` in any other commit or branch holds superseded or provisional values. That includes `part8-r1-rescore`, the pin `8aaa4217` and the results commit `0662945`, which hold the original baseline. **Do not use it.**
> - **Numbers identity.** Run `correction-20261109T080220-949fcd76` (archive `archive-20261109T080914Z-3c7d68`), equivalent to the audited run `correction-20261108T053328-949fcd76`. Scientific code `8aaa4217`, unchanged. No model was estimated in the integration or the release. B2 was accepted on 8 November 2026 (`corrections/r1/b2_scientific_adjudication.md`).
> - **Number checks.** Every quoted number is checked against the integrated tables, whose cell content the archive's equivalence gate ties to the release: `corrections/r1/evidence/part8_drafts_20261108/number_checks.csv`.
> - **F3.4 figures.** <!--PUB:f8-->The approved F8 versions (presentation only, 9 November 2026) are prepared in `corrections/r1/f8_review/` and become the release's `figures/F3.4_*` on publication.<!--/PUB:f8-->
> - **Not changed.** The superseded reports in `reports/part8/*.md` and the drafts in `drafts_integrated_20261108/`; results commit `0662945`; the provisional releases `0573a8c`, `3bd24c4` and `292227e`; certificates; `approved-specs/`.
> - **Changes from the published (1 November) reports and from the drafts:** `CHANGELOG.md`.

**Basis of the statuses.** They are assessed on the integrated candidate. A status of RESOLVED means the requested analysis is performed and reported in the candidate; it becomes final only when the candidate is archived, approved and published. Changes from the published statuses are marked "(was …)".

**Rule (CLAUDE.md §12).** A remark is satisfied by properly performing and reporting the requested analysis, whatever the result.

**Categories**

- **RESOLVED** — the requested analysis was performed and reported completely.
- **PARTIALLY ADDRESSED** — the analysis was performed, but part of it is missing or affected by a documented defect.
- **UNRESOLVED** — not performed.
- **OUTSIDE EMPIRICAL SCOPE** — the remark concerns writing, structure or presentation, and is answered in Parts 4, 5 or 9 rather than by `output/`.

**Paths.** All are relative to `my-thesis/output/` in the release commit (see the banner). The correction references F1–F7 point to `notes/claude/part8_audit_findings_and_correction_proposals_2026-11-01.md`.

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
<!--PUB:r106_status-->- **Status:** PARTIALLY ADDRESSED until the release is published. It becomes RESOLVED only when the published release contains the approved F8 figures; until then the only stored F3.4 are the pre-F8 archived figures.<!--/PUB:r106_status-->
- **Evidence:** the three defects behind the partial status are addressed in the actual figures (`corrections/r1/f8_review/f8_figure_review.md`):
  - **F1.** The UNRATE main panel no longer plots the failed AR forecast. Failed fits appear in the diagnostic panel as hollow markers labelled "failed fit (raw value, not scored)".
  - **F1 marker rule.** Flagged forecasts are unconnected markers, not lines joining non-adjacent dates.
  - **F8 (approved 9 November 2026).** The CPI main panel is no longer compressed by the STAR forecast of 1.4×10¹¹. It now shows actual inflation and all models readably. The 15 STAR extremes appear in the diagnostic panel on a labelled symmetric-log axis; the INDPRO extremes, down to −1.9×10⁸, are shown the same way.
  - The omission from the main panel is stated in each title. Nothing is clipped.
  - With F8 off, the renderer reproduces all 12 archived F3.4 files byte for byte, so the F8 figures use exactly the archived inputs.
- **Residual presentation points (not §13.1 defects):** the M2SL diagnostic panel stays linear, so its dense STAR markers overlap. There is an empty pre-sample span from 1945 to the first forecast.
<!--PUB:r106_action-->- **Remaining action:** publish the release with the F8 figures (`corrections/r1/part8_d3_release_plan.md`).<!--/PUB:r106_action-->

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
- **Remaining action:** none. F7.1 is applied: T2.1 shows the final transformations of UNRATE and FEDFUNDS.

**R1-13 — Every test defined: H0, distribution, decision**
- **Status:** RESOLVED (was PARTIALLY ADDRESSED).
- **Evidence:** Each diagnostic row carries the name, null hypothesis, statistic, reference distribution, p-value, 5% decision and implication (`diagnostics/all_test_results.csv`, 354 rows, including the four Zivot–Andrews rows of F4; T2.2, T2.3, T3.2 residual tests).
- **Caveat:** the auto-generated `implication` text of the joint-Wald rows overstates a joint rejection (UNRATE ARMA vs AR, h=1: joint p = 0.034, state-dependence p = 0.282). Part 9 must not quote that text (`full_empirical_analysis_report.md` D.3).

**R1-14 — Modern forecast-comparison testing**
- **Status:** RESOLVED (was PARTIALLY ADDRESSED).
- **Evidence:**
  - Performed:
    - HLZ (2025), the primary test: 230 rows, 4 unavailable (`forecast_tests/T3.3A_hlz_pairwise.csv`); 58 rows are degenerate because of exploding STAR forecasts and are reported as carrying no inference;
    - DM-HLN (T3.3B);
    - the ex-post state-dependent loss regression, deliberately not labelled Giacomini–White (decision M1): 67 of 69 rows available (`T3.5_state_loss_regression.csv`);
    - the MCS (T3.4), all 92 cells available, and the window-length MCS, all 72 cells available (guarded procedure F2, validated against `arch`).
  - Clark–McCracken and Amisano–Giacomini were excluded with the reasons given in Part 5 §10.6.
  - The sign-convention label is corrected (F3), and forecasts from failed fits are not scored (F1).
- **Remaining action:** none empirically. Part 9 keeps the multiplicity caution (all p-values nominal).

**R1-15 — CPI lag structure**
- **Status:** RESOLVED (was PARTIALLY ADDRESSED).
- **Evidence:**
  - BIC selects p=2 (`diagnostics/T2.5_selected_specs.csv`).
  - Under p=1, 3, 6 and 12 robustness on 714 common dates (`robustness/T4.2_cpi_lag_robustness.csv`, `_predictive_tests.csv`; the p=12 chain recomputed under Tier A, its failed 1974-09 fit not scored), there is no evidence that 12 lags improve on the BIC-selected AR(2). AR(12) has RMSE 2.967 on the 714 common dates, against 2.967 for the baseline p=2 on its own 715-date sample (T3.3). AR(12) does not significantly beat AR(1); only p=3 does, under absolute loss (HLZ p = 0.013). No direct AR(2)-versus-AR(12) test or equivalence test exists, so the claim is QUALIFIED (C16). The remark is resolved because the analysis is performed and reported (CLAUDE.md §12), whatever its result.
  - F2.1 and F3.x show the CPI series and fits.
- **Remaining action:** none.

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
- **Status:** RESOLVED (was PARTIALLY ADDRESSED).
- **Evidence:** A monthly five-variable VAR(1) robustness exercise (`robustness/T4.5_var_*`). The VAR never significantly beats AR, and is significantly worse for FEDFUNDS under absolute loss. For UNRATE (527 common dates, corrected AR benchmark) it has the lowest RMSE (0.493 against AR 0.613), but the difference is not significant (HLZ p = 0.346 and 0.811); the rank is descriptive.
- **Remaining action:** The limits of a linear VAR must be stated in Part 9.

**R1-20 — Nowcasting and mixed frequency**
- **Status:** OUTSIDE EMPIRICAL SCOPE, as a declared scope boundary.
- **Evidence:** Part 5 §12. There are no real-time vintages, and GDP is not interpolated.
- **Remaining action:** Part 9 states the boundary.

**R1-21 — Lighten the theory**
- **Status:** OUTSIDE EMPIRICAL SCOPE.
- **Remaining action:** Part 9.

**R1-22 — Verify and broaden the econometric results**
- **Status:** RESOLVED on the integrated candidate (was PARTIALLY ADDRESSED); final after archive, approval and publication.
- **Evidence:**
  - Full reproducible run from the frozen, hash-verified CSV (`manifests/run_manifest.json`).
  - The audit's defects are corrected in the candidate (F1, F2, F3, F4, F7.1), and every chain that needed recomputation is computed (Tier A; Tier B B1, B2, B3). No estimation was performed in the integration.
  - Failures visible: 435 failed fits and 34,122 registry events (`models/fit_records.csv`, `robustness/T4.7_failure_registry.csv`), plus the MSAR optimiser sensitivity recorded under B2 (20 classification changes, 29 sensitivities; `corrections/r1/b2_scientific_adjudication.md`).
  - Robustness exercises T4.1–T4.9 and TP1 complete.
- **Remaining action:** your Part 8 approval and publication of the archived candidate (`archive-20261109T080914Z-3c7d68`, verified in `corrections/r1/archive_verification_20261109.md`); F6 stays a stated limitation.

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
- **Status:** RESOLVED (was PARTIALLY ADDRESSED).
- **Evidence:**
  - ADF and KPSS were run on both the initial window and the full sample (`diagnostics/T2.2_stationarity.csv`).
    - UNRATE is level-stationary: full-sample ADF p = 0.0028 and KPSS p = 0.078.
    - FEDFUNDS has a unit root: ADF p = 0.129 and KPSS p ≤ 0.01.
    - The full sample agrees with the baseline rule (T2.2D).
  - The Zivot–Andrews test with a break in intercept and trend is now reported (F4; T2.2 and `diagnostics/all_test_results.csv`):
    - UNRATE: ZA does not reject a unit root (initial window statistic −4.556, p = 0.189, break 1957-08; full sample −4.606, p = 0.169, break 2008-04).
    - FEDFUNDS: ZA does not reject a unit root (initial window −3.500, p = 0.811, break 1970-10; full sample −4.290, p = 0.320, break 1984-08).
  - The §3.4 transformations are unchanged, because ADF and KPSS agree.
- **Remaining action:** Part 9 must report that for UNRATE the break-allowing test does *not* corroborate the ADF rejection, which weakens the level-stationarity reading; the transformation-robustness check (T4.1) shows no significant forecast difference when UNRATE is differenced.

**P-03 — Diagnose the extreme policy-rate Markov-switching result**
- **Status:** RESOLVED.
- **Evidence:**
  - Under the approved differencing, the full-sample FEDFUNDS K=2 MSAR collapses to the linear AR(1):
    - identical regime means, 0.0025;
    - unidentified transition probabilities, with SE 18 and 38;
    - log-likelihood −518.894, the same as AR (`models/T3.2_nonlinear_credibility.csv`, `models/T3.1_in_sample_adequacy.csv`).
  - K=3 isolates a 2-observation regime and a 20-observation regime (`robustness/T4.3_regime_count.csv`).
  - In the level alternative, MSAR fails at 49 of 626 origins (`robustness/T4.1_transformation_robustness.csv`; 52 published, B2).
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
  - The F6 numerical review is in `corrections/f6_k3_nesting_feasibility.csv`. The final disposition, retaining the result as inconclusive with no re-optimisation, is `corrections/r1/f6_scientific_disposition.md`.
- **Evidence:**
  - Full-sample K=2 against K=3 for all six targets, per amended §11.1 (`robustness/T4.3_regime_count.csv`, `_conclusion.csv`, `T4.3_regime_parameters.csv`, `figures/F4.3_*`).
  - K=3 is not credible for any target.
  - The information criteria favour K=3 for five targets, through outlier regimes.
  - K=2 is retained as predeclared.
  - The UNRATE comparison is inconclusive (non-global K=3 optimum; F6).
  - "Useful" is judged in-sample only, by design: no K=3 forecasts were made.
- **Remaining action:** none in Part 8. By your decision of 9 November 2026 the nesting-informed start is not adopted and the approved multistart is unchanged. The UNRATE K=3 comparison stays INCONCLUSIVE, so P-04 stays PARTIALLY ADDRESSED. Part 9 states the limitation (`corrections/r1/f6_scientific_disposition.md`).

**P-05 — One-step horizon limitation**
- **Status:** RESOLVED (was PARTIALLY ADDRESSED).
- **Evidence:** h = 3, 6 and 12 months and h = 2 and 4 quarters (`forecast_tests/T3.3_main_forecast_table.csv`, `robustness/T4.4_horizon_*`). Longer horizons give no systematic nonlinear gain; the exception is CPIAUCSL MSAR at h=12 (unadjusted; not robust to a Holm adjustment). For UNRATE, with F1 applied, AR ranks first by RMSE at h=3 and 6, and MSAR's OOS R² is negative at every longer horizon.
- **Remaining action:** none.

**P-06 — External validity and transferability**
- **Status:** OUTSIDE EMPIRICAL SCOPE, with a delimiting statement.
- **Evidence:** All results are U.S.-specific. The transferable part is the design: adequacy before forecasting, failure visibility, HLZ, MCS and threat-based robustness (`final_claims_allowed.md`).
- **Remaining action:** Part 9.

## Prof. Verne constraints

- **V-04 (AR and ARMA benchmarks; ARCH/GARCH where present):** RESOLVED.
  - Both benchmarks are in the horse race.
  - ARMA-GARCH ran where ARCH-LM rejected (CPIAUCSL, UNRATE, FEDFUNDS) and was legitimately skipped elsewhere (`robustness/T4.6_*`).
  - Caveat: "ARMA" is a pure AR for 5 of 6 targets (T2.5).
- **V-05 (recession, expansion and turning-point evaluation):** RESOLVED (T3.5, T3.6, TP1). There is no significant state dependence for the nonlinear models. The UNRATE ARMA-versus-AR joint Wald rejection (p = 0.034) is not evidence of state dependence: its state-dependence test gives p = 0.282.
- **V-06 (adequacy before forecast ranking):** RESOLVED (T3.1, T3.2, then T3.3).
- **V-07 (outputs ready for Part 9 synthesis):** READY SUBJECT TO APPROVAL (was PARTIALLY ADDRESSED). F1, F2 and F4 are applied in the candidate, and all pending estimation is integrated. The candidate is archived (`archive-20261109T080914Z-3c7d68`); the status becomes final after your Part 8 approval and publication.

## Summary count (29 Part 2 remarks)

| Status | Count | Remarks |
|---|---|---|
<!--PUB:r106_table-->| RESOLVED | 15 | R1-07, R1-09, R1-12, R1-13, R1-14, R1-15, R1-17, R1-18, R1-19, R1-22, R1-23, P-01, P-02, P-03, P-05 |
| PARTIALLY ADDRESSED | 3 | R1-06 (until the release with the F8 figures is published), R1-11 (empirical part only), P-04 (F6) |<!--/PUB:r106_table-->
| UNRESOLVED | 0 | — |
| OUTSIDE EMPIRICAL SCOPE | 11 | R1-01, R1-02, R1-03, R1-04, R1-05, R1-08, R1-10, R1-16, R1-20, R1-21, P-06 |

Seven remarks move from PARTIALLY ADDRESSED to RESOLVED on the integrated candidate: R1-13, R1-14, R1-15, R1-19, R1-22, P-02 and P-05. <!--PUB:r106_text-->**R1-06** moves to RESOLVED only when the release containing the approved F8 figures is published and verified.<!--/PUB:r106_text--> P-04 stays partial (F6, final disposition). R1-11 stays partial (its textual part is Part 9). <!--PUB:final_text-->All RESOLVED statuses take effect when the release is published.<!--/PUB:final_text-->
