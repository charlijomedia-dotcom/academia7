# Part 8 — Final claims allowed

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


**Purpose.** This file is the bridge to Part 9. It gives the exact claims the frozen outputs of run `baseline-20261030T173044-949fcd76` permit, with the wording allowed, the status, the supporting files (relative to `output/`) and the jury IDs.

The machine-readable version is `reports/part8/claim_evidence_matrix_adjudicated.csv` (see §4 for why it is a derived report file).

**Statuses**

- **SUPPORTED** — the evidence directly supports the claim as worded.
- **QUALIFIED** — the claim may be made only with the stated qualification.
- **NOT_SUPPORTED** — the evidence does not support the claim; the claim must not be made, or must be stated as a negative finding.
- **INCONCLUSIVE** — the evidence cannot decide; it is pending correction or is underpowered.

**General restrictions**

- These apply to every claim (CLAUDE.md §11; Part 5 §14):
  - no causal or policy-effect claims;
  - no universal model ranking;
  - no claims about other countries or real-time nowcasting;
  - no economic labels on statistical regimes.
- Every number used in Part 9 must be quoted from `output/`. The **[audit]** numbers in these reports are not citable as results.

**Provisional claims (correction phase, 2 November 2026).** These rest on outputs that the approved corrections will regenerate. Until the corrected release is re-audited, they are **PROVISIONAL** and must not be used in Part 9 in final form.

| Claims | Correction | Reason |
|---|---|---|
| C01, C04, C12, C13, C14, C15, C17, C21 | F1 | They depend on UNRATE comparisons against AR, or on robustness rows that score a failed fit |
| C16 | F1 | One failed CPI p=12 origin |
| C02 | F2 | The completeness of the CPI and M2 MCS cells |
| P04-regime-count and C18 | F6 | UNRATE K=3 is a non-global optimum |

The machine-readable matrix carries a `provisional` column.

**Inference language.** In every claim, a non-rejection is reported as "no significant difference" or "no evidence of superiority". It is never reported as "equal forecasting ability".

---

## 1. Claims on the central question

**C01 — No general nonlinear forecasting advantage at the baseline horizon**
- **Status:** SUPPORTED. For UNRATE this is provisional pending F1.
- **Allowed wording:** "At the one-step baseline horizon, neither MSAR nor STAR forecasts were significantly more accurate than the AR benchmark under the Harvey–Leybourne–Zu test for any of the six U.S. targets. This is an absence of evidence of superiority, not a demonstration of equal accuracy."
- **Evidence:** `forecast_tests/T3.3A_hlz_pairwise.csv` (h=1, AR–MSAR and AR–STAR rows); `forecast_tests/T3.3_main_forecast_table.csv`.
- **Jury IDs:** R1-09, R1-14, R1-22.

**C02 — The one formally supported nonlinear gain is small and occurs at a robustness horizon**
- **Status:** QUALIFIED.
- **Allowed wording:** "The only nonlinear-over-AR rejection at the 5% level is MSAR for CPI inflation at the 12-month horizon (OOS R² = 0.042; HLZ p = 0.033 under squared and 0.004 under absolute loss). It is an unadjusted result at one robustness horizon: within the 46 MSAR-versus-AR tests it does not survive a Holm family-wise adjustment (adjusted p = 0.20 and 1.0), so it is not evidence of a systematic advantage."
- **Source of the adjustment:** the Holm figures are a Part 8 audit computation on `forecast_tests/T3.3A_hlz_pairwise.csv`. They are not an approved procedure output. Part 9 should present them as a sensitivity remark, or recompute them as an approved table.
- **Evidence:** T3.3 (CPIAUCSL MSAR h=12); T3.3A (CPIAUCSL h=12 AR–MSAR); T3.3B; `forecast_tests/T3.4_model_confidence_set.csv` (CPIAUCSL h=12 absolute, 90%: only ARMA excluded).
- **Jury IDs:** P-05, R1-14.

**C03 — Lower descriptive RMSE for MSAR, not formally supported**
- **Status:** QUALIFIED.
- **Allowed wording:** "MSAR attains the lowest one-step RMSE for GDP and industrial production (OOS R² 0.292 and 0.236), but these differences are not statistically significant under HLZ and the MCS retains AR, ARMA and MSAR."
- **Required qualification:** "The descriptive gains are concentrated in the 2020–21 pandemic observations." This must be stated as an observation, citing the forecast files, without quoting the [audit] R² as a thesis number unless the user approves that sensitivity.
- **Evidence:** T3.3; T3.3A; T3.4; `forecasts/forecasts_GDPC1.csv`, `forecasts/forecasts_INDPRO.csv`.
- **Jury IDs:** R1-09.

**C04 — "Nonlinear models outperform classical benchmarks"**
- **Status:** NOT_SUPPORTED. Must not be claimed.
- **Evidence:** T3.3A; T3.4; T4.4P; T4.8P.
- **Jury IDs:** R1-09, R1-22.

## 2. Model adequacy and credibility

**C05 — Better in-sample fit**
- **Status:** SUPPORTED, but only as a fit statement.
- **Allowed wording:** "Full-sample MSAR and STAR achieve lower BIC than AR for five of six targets."
- **Required qualification:** For GDP, industrial production and M2, the MSAR improvement comes from a one-to-three-observation regime around 2020.
- **Evidence:** `models/T3.1_in_sample_adequacy.csv`; `models/T3.2_nonlinear_credibility.csv`.
- **Jury IDs:** V-06.

**C06 — Regime estimates are mostly not credible (R1-17)**
- **Status:** SUPPORTED.
- **Allowed wording:** "Under the predeclared credibility rules, the full-sample two-regime MSAR is interpretable only for CPI inflation. For GDP, industrial production and M2 the second regime captures one to three pandemic observations with boundary transition probabilities; for the federal funds rate the two regimes are statistically indistinguishable; for unemployment the transition probability is at the persistence boundary."
- **Evidence:** T3.2; `robustness/T4.3_regime_count.csv`.
- **Jury IDs:** R1-17, R1-11, P-03.

**C07 — Rolling nonlinear estimates are predominantly fragile**
- **Status:** SUPPORTED.
- **Allowed wording:** "Most rolling MSAR and STAR estimates are classified as fragile (low occupancy, boundary transitions, ill-conditioned or singular covariance, γ at its bound, extreme threshold)."
- **Evidence:** `models/fit_records.csv`; `robustness/T4.7_failure_registry.csv`; T3.3 `n_fragile`.
- **Jury IDs:** R1-17, R1-22.

**C08 — STAR is unstable as a rolling forecaster**
- **Status:** SUPPORTED.
- **Allowed wording:** "Rolling STAR estimates frequently place the transition threshold outside the bulk of the data with a singular information matrix; the resulting iterated forecasts can be explosive, and STAR has the highest RMSE for most targets and horizons."
- **Evidence:** T3.3; `models/fit_records.csv`; `forecasts/forecasts_*.csv` (EXTREME_FORECAST rows).
- **Jury IDs:** R1-06, R1-22.

**C09 — "STAR captures a credible smooth-transition mechanism"**
- **Status:** NOT_SUPPORTED, except as an in-sample description for CPI only.
- **Evidence:** T3.2; `diagnostics/T2.4_star_linearity.csv`.
- **Jury IDs:** R1-18.

**C10 — CPI high-inflation regime**
- **Status:** QUALIFIED (descriptive).
- **Allowed wording:** "For CPI inflation, the two-regime model identifies a high-inflation state (regime mean 12.5% annualised, 8.6% occupancy, expected duration 6.3 months)."
- **Restriction:** No causal or policy interpretation, and no economic label beyond the statistical description.
- **Evidence:** T3.2 (CPIAUCSL MSAR).
- **Jury IDs:** R1-17.

## 3. Pre-tests, states, robustness

**C11 — Nonlinearity pre-test evidence is target-specific**
- **Status:** SUPPORTED.
- **Allowed wording:** "Linearity is rejected for unemployment (Tsay and LST), CPI inflation and the federal funds rate (LST), but not for GDP, industrial production or M2."
- **Evidence:** `diagnostics/T2.3_tsay.csv`; T2.4.
- **Jury IDs:** R1-18.

**C12 — No state-dependent nonlinear gain**
- **Status:** NOT_SUPPORTED for the positive claim, so it is stated as a negative finding.
- **Allowed wording:** "The state-dependent loss regressions provide no evidence that MSAR or STAR gains concentrate in recessions or turning-point windows, and no turning-window result survives the alternative window widths."
- **Evidence:** `forecast_tests/T3.5_state_loss_regression.csv`; `T3.5_state_performance.csv`; `robustness/T4.TP1_turning_window_sensitivity.csv`.
- **Jury IDs:** V-05, R1-14.

**C13 — Longer horizons do not reveal systematic nonlinear gains (P-05)**
- **Status:** QUALIFIED. The CPI h=12 exception applies, and UNRATE is pending F1.
- **Evidence:** T3.3; `robustness/T4.4_horizon_*`.
- **Jury IDs:** P-05.

**C14 — The conclusions are insensitive to the predeclared window lengths**
- **Status:** SUPPORTED. UNRATE rows are pending F1.
- **Allowed wording:** "Across 180/240/300-month and 90/120/150-quarter windows, 97 of 108 test conclusions are unchanged and no nonlinear model gains inferential support."
- **Evidence:** `robustness/window_length_predictive_tests.csv`; `window_length_comparison.csv`.
- **Jury IDs:** (window amendment).

**C15 — Insensitivity to transformations**
- **Status:** SUPPORTED, with the F1 caveat.
- **Allowed wording:** "Modelling unemployment in differences or the federal funds rate in levels yields no significant forecast differences under HLZ."
- **Evidence:** `robustness/T4.1_*`.
- **Jury IDs:** P-02, P-03.

**C16 — The CPI 12-lag structure is unnecessary**
- **Status:** SUPPORTED.
- **Allowed wording:** "The BIC-selected AR(2) for CPI inflation forecasts as accurately as AR(12); lags beyond two add no accuracy."
- **Evidence:** `robustness/T4.2_*`; T3.3.
- **Jury IDs:** R1-15.

**C17 — A VAR does not overturn the univariate conclusions**
- **Status:** SUPPORTED.
- **Allowed wording:** "A monthly five-variable VAR(1) never forecasts significantly better than AR and is significantly worse for the federal funds rate under absolute loss."
- **Evidence:** `robustness/T4.5_*`.
- **Jury IDs:** R1-19, P-01.

**C18 — No credible third regime (P-04)**
- **Status:** QUALIFIED. UNRATE is inconclusive.
- **Allowed wording:** "A three-regime MSAR is not credible for any target under the predeclared criteria, although information criteria favour it in-sample for five targets through low-occupancy, extreme-observation regimes; the two-regime baseline is retained. This is an in-sample assessment and implies nothing about forecasting."
- **Restriction:** Must not claim that K=2 is "validated". K=2 is itself weak for four targets.
- **Evidence:** `robustness/T4.3_*`; `figures/F4.3_*`.
- **Jury IDs:** P-04.

**C19 — Persistent conditional heteroskedasticity**
- **Status:** SUPPORTED (diagnostic).
- **Allowed wording:** "ARCH effects are present for CPI inflation, unemployment and the federal funds rate; ARMA-GARCH(1,1) variance persistence averages 0.83, 0.55 and 0.97."
- **Restriction:** No claim about mean-forecast gains.
- **Evidence:** `robustness/T4.6_*`.
- **Jury IDs:** V-04.

**C20 — The October 2025 LOCF does not drive the results**
- **Status:** SUPPORTED.
- **Evidence:** `data_audit/T4.9_locf_sample_comparison.csv`; `locf_forecast_exposure.parquet`.
- **Jury IDs:** R1-12, R1-22.

**C21 — Unemployment-specific forecast rankings**
- **Status:** INCONCLUSIVE until F1 is corrected.
- **Restriction:** Do not quote any UNRATE OOS R², rank or AR-relative test until regeneration.
- **Evidence:** T3.3 (UNRATE rows); `notes/claude/part8_audit_findings_and_correction_proposals_2026-11-01.md`.
- **Jury IDs:** R1-22.

**C22 — The policy-rate regime diagnosis (P-03)**
- **Status:** SUPPORTED.
- **Allowed wording:** "Under the approved first-difference treatment, the two-regime model for the federal funds rate collapses to the linear AR(1): the regime means coincide and the transition probabilities are not identified. The extreme regime result of the submitted thesis is not reproduced."
- **Evidence:** T3.2; T3.1 (FEDFUNDS); T4.3.
- **Jury IDs:** P-03.

**C23 — Transferability (P-06)**
- **Status:** QUALIFIED; the claim concerns the design only.
- **Allowed wording:** "The rankings are specific to this U.S. sample; what transfers is the evaluation design (adequacy before forecasting, visible failures, instability-robust tests, threat-based robustness)."
- **Evidence:** (all).
- **Jury IDs:** P-06.

---

## 4. Claim matrix: derived report versus immutable output

- Part 5 requires `output/manifests/claim_evidence_matrix.csv`. The pipeline registered it before Part 8 with one row, `P04-regime-count`, whose result and status fields were empty. The file has SHA-256 `62d5ec1e797aab3318fcc26071a416bdaf9f93b26a7b00daa6021f4cc96ed89a` and is listed in `output/manifests/output_inventory.csv`.
- **Decision.** The adjudication is written to **`reports/part8/claim_evidence_matrix_adjudicated.csv`**. **`output/` is not modified.** The reasons:
  1. It keeps every file under `output/` byte-identical to the immutable results commit `0662945`, so the inventory checksums still verify.
  2. The statuses are Part 8 *judgements*, not computed numbers. CLAUDE.md §9 places judgements in `reports/`.
  3. F1 requires regeneration anyway. The pipeline-written matrix should be refreshed after the approved re-run, not hand-edited now.
- **The adjudicated CSV**
  - uses the exact Part 5 §12 columns;
  - adds `adjudication_basis`, `provisional_due_to` and `adjudicated_in`;
  - adjudicates the P-04 row and adds every major claim above (C01–C23).
- If the user prefers the adjudication to live in `output/manifests/claim_evidence_matrix.csv`, that is a deliberate change to an inventoried file. It needs:
  - the inventory regenerated;
  - the old hash (`62d5ec1e…`) and the new hash recorded in a note.
