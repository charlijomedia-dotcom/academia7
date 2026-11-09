# Part 8 — Final claims allowed (final)

> **FINAL PART 8 REPORT — release `part8-final-20261109`.** <!--PUB:status-->**Not yet published.** The release commit and Drive folder do not exist yet. Until `finalize_reports.py` records the verified publication, these reports and their numbers are not citable (CLAUDE.md §9).<!--/PUB:status-->
>
> - **Authoritative numbers.** `my-thesis/output/` in the release commit on branch `part8-corrected-results/final-20261109`: 465 files, listed with sha256 in `my-thesis/release/part8_final/release_inventory.csv`. See `SOURCE_OF_TRUTH.md` in this directory.
>   - `output/` in any other commit or branch holds superseded or provisional values. That includes `part8-r1-rescore`, the pin `8aaa4217` and the results commit `0662945`, which hold the original baseline. **Do not use it.**
> - **Numbers identity.** Run `correction-20261109T080220-949fcd76` (archive `archive-20261109T080914Z-3c7d68`), equivalent to the audited run `correction-20261108T053328-949fcd76`. Scientific code `8aaa4217`, unchanged. No model was estimated in the integration or the release. B2 was accepted on 8 November 2026 (`corrections/r1/b2_scientific_adjudication.md`).
> - **Number checks.** Every quoted number is checked against the integrated tables, whose cell content the archive's equivalence gate ties to the release: `corrections/r1/evidence/part8_drafts_20261108/number_checks.csv`.
> - **F3.4 figures.** <!--PUB:f8-->The approved F8 versions (presentation only, 9 November 2026) are prepared in `corrections/r1/f8_review/` and become the release's `figures/F3.4_*` on publication.<!--/PUB:f8-->
> - **Not changed.** The superseded reports in `reports/part8/*.md` and the drafts in `drafts_integrated_20261108/`; results commit `0662945`; the provisional releases `0573a8c`, `3bd24c4` and `292227e`; certificates; `approved-specs/`.
> - **Changes from the published (1 November) reports and from the drafts:** `CHANGELOG.md`.

**Purpose.** This file is the bridge to Part 9. It gives the exact claims the **final release** permits (see the banner), with the wording allowed, the status, the supporting files (relative to `my-thesis/output/` in the release commit) and the jury IDs.

The machine-readable version for the published release is `reports/part8/claim_evidence_matrix_adjudicated.csv`, and the R1 version is `corrections/r1/claim_evidence_matrix_corrected.csv`. The claim-by-claim verdicts on the integrated candidate are in `corrections/r1/evidence/integration_dryrun_audit_20261108/derived/claim_verdicts_integration.csv`. The final machine-readable matrix is `claim_evidence_matrix_final.csv` in this directory; the earlier matrices are unchanged (§4).

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
- Every number used in Part 9 must be quoted from `output/`, i.e. from the candidate once it is published. The **[audit]** numbers in these reports are not citable as results.
- **Significance versus ranking.** A descriptive ranking (lowest RMSE, rank) is never stated as a statistical conclusion. A ranking is stated with the sample it uses.
- **Degenerate tests.** A test on exploding STAR losses (T3.3A mean differential beyond 10³; p ≈ 0.31–0.33) carries no usable inference. It supports no affirmative inferential claim, including "no significant difference".
- **Joint tests.** A joint Wald rejection is reported separately from its state-dependence test and is not read as state dependence.

**Status of the earlier provisional flags.** The published report marked C01, C02, C04, C12–C17 and C21 as provisional pending F1 or F2. In the integrated candidate F1 and F2 are applied and every pending chain is computed, so those flags are lifted. Against the R1 corrected matrix, 23 claims keep their status and **C16 moves from SUPPORTED to QUALIFIED** (revision of 9 November 2026: equal accuracy of AR(2) and AR(12) is not established). Against the published report, C21 also changes (INCONCLUSIVE → SUPPORTED as revised). C08, C14, C15, C16 and C21 have revised wording and C07 a clarification; C12, C13 and C17 carry smaller additions. All are listed in `CHANGELOG.md`. The candidate matrix is `claim_evidence_matrix_candidate.csv` in this directory. **All claims remain drafts until the archived candidate is approved and published.** P04-regime-count and C18 remain qualified by F6 (UNRATE K=3 is a non-global optimum).

**Inference language.** In every claim, a non-rejection is reported as "no significant difference" or "no evidence of superiority". It is never reported as "equal forecasting ability".

---

## 1. Claims on the central question

**C01 — No general nonlinear forecasting advantage at the baseline horizon**
- **Status:** SUPPORTED.
- **Allowed wording:** "At the one-step baseline horizon, neither MSAR nor STAR forecasts were significantly more accurate than the AR benchmark under the Harvey–Leybourne–Zu test for any of the six U.S. targets. This is an absence of evidence of superiority, not a demonstration of equal accuracy."
- **Note:** the only h=1 decision changes from the corrections are rejections *against* STAR (UNRATE, absolute loss, nominal).
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
- **Status:** SUPPORTED, with a clarification of "predominantly".
- **Allowed wording:** "Pooled across targets, most rolling MSAR and STAR estimates are classified as fragile (low occupancy, boundary transitions, ill-conditioned or singular covariance, γ at its bound, extreme threshold): 10,246 of 15,443 MSAR fits and 12,702 of 15,443 STAR fits. Fragility varies by chain; the unemployment MSAR chains are mostly adequate. Re-estimating two MSAR chains under the approved warm-start rule changed 20 fit classifications and moved 29 further fits to a different local optimum, which shows that rolling MSAR estimates are sensitive to the optimiser and are not guaranteed global maxima."
- **Clarification:** "predominantly" refers to the pooled rolling estimates, not to every target. It must not be applied to UNRATE MSAR (2,120 adequate, 1,380 fragile in T4.7 status counts; baseline chain 258 fragile of 704).
- **Required limitation:** F6 — no global likelihood maximum is claimed for any MSAR estimate (`corrections/r1/b2_scientific_adjudication.md`).
- **Evidence:** `models/fit_records.csv`; `robustness/T4.7_failure_registry.csv`; `robustness/T4.7_status_counts.csv`; T3.3 `n_fragile`; `corrections/r1/evidence/b2_adjudication_20261108/b2_adjudicated_items.csv`.
- **Jury IDs:** R1-17, R1-22.

**C08 — STAR is unstable as a rolling forecaster**
- **Status:** SUPPORTED.
- **Allowed wording:** "Rolling STAR estimates frequently place the transition threshold outside the bulk of the data with a singular information matrix; the resulting iterated forecasts can be explosive, and STAR has the highest RMSE for most targets and horizons. Where STAR forecasts explode, the pairwise forecast-accuracy tests are numerically degenerate and provide no usable inference; they are reported as such, not as evidence of equal accuracy."
- **Required distinction:** numerical instability (exploding forecasts, degenerate test statistics) is not a statistical result. A degenerate test supports no affirmative inferential claim in either direction. Only non-degenerate STAR tests support inference, for example STAR worse than AR at h=1 under absolute loss for FEDFUNDS (HLZ p = 0.029) and, nominally, UNRATE (p = 0.0015; Holm 0.066 [audit]).
- **Evidence:** T3.3; T3.3A; `models/fit_records.csv`; `forecasts/forecasts_*.csv` (EXTREME_FORECAST rows); `corrections/r1/star_test_degeneracy.csv` (58 degenerate T3.3A rows).
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
- **Restriction (linear benchmarks).** For unemployment at h=1, ARMA versus AR, the joint Wald test of zero average loss differential and no state effects rejects at the nominal 5% level (p = 0.034), but the state-dependence test does not (p = 0.282) and no coefficient is significant at 10%. Report the two separately; the joint rejection is not evidence of state dependence. Do not quote the row's auto-generated `implication` text, nor the FEDFUNDS ARMA h=6 `state_dependence_supported_5pct` flag (slopes p = 0.082) without that qualification.
- **Evidence:** `forecast_tests/T3.5_state_loss_regression.csv`; `T3.5_state_performance.csv`; `robustness/T4.TP1_turning_window_sensitivity.csv`.
- **Jury IDs:** V-05, R1-14.

**C13 — Longer horizons do not reveal systematic nonlinear gains (P-05)**
- **Status:** QUALIFIED. The CPI h=12 exception applies.
- **Allowed wording:** "Longer horizons do not reveal a systematic nonlinear advantage; the only exception is MSAR for CPI inflation at 12 months, which is not robust to a family-wise adjustment. For unemployment, AR has the lowest RMSE at 3 and 6 months."
- **Evidence:** T3.3; `robustness/T4.4_horizon_*`.
- **Jury IDs:** P-05.

**C14 — The conclusions are insensitive to the predeclared window lengths**
- **Status:** SUPPORTED, with a qualification on the unemployment ranking.
- **Allowed wording:** "Across the predeclared 180/240/300-month and 90/120/150-quarter windows, 97 of 108 test conclusions are unchanged and no nonlinear model gains inferential support at any length. For unemployment, STAR is nominally less accurate than AR at h=1 under absolute loss at all three lengths. The descriptive h=1 advantage of MSAR for unemployment is not robust to the window length."
- **Supporting numbers:** UNRATE MSAR h=1 OOS R² 0.240, 0.190 and −1.102 at 180, 240 and 300 months (rank 4 of 4 at 300); HLZ p against AR between 0.30 and 0.77 at every length (T4.8C, T4.8P).
- **Evidence:** `robustness/window_length_predictive_tests.csv`; `window_length_comparison.csv`.
- **Jury IDs:** (window amendment).

**C15 — Insensitivity to transformations**
- **Status:** SUPPORTED, with a qualification on rankings.
- **Allowed wording:** "Modelling unemployment in differences or the federal funds rate in levels yields no significant forecast differences against AR under HLZ. Point rankings, however, depend on the transformation: AR has the lowest h=1 RMSE under both alternative transformations."
- **Additional disclosure:** the secondary DM-HLN test rejects for the federal funds rate in levels under absolute loss, for ARMA (in ARMA's favour, p = 0.0076) and for MSAR (against MSAR, p = 0.029); HLZ governs (p = 0.146 and 0.145). The MSAR change is attributable jointly to F1 and B2.
- **Evidence:** `robustness/T4.1_*`.
- **Jury IDs:** P-02, P-03.

**C16 — No evidence that the CPI 12-lag structure improves forecasts**
- **Status:** QUALIFIED (was SUPPORTED). The p=12 chain is recomputed and its failed fit is not scored.
- **Allowed wording:** "The robustness exercise provides no evidence that a 12-lag autoregression improves one-step CPI-inflation forecasts over the BIC-selected AR(2). The two models have one-step RMSEs within about 0.002 of each other (2.967 for AR(12) on the 714 common dates; 2.967 for AR(2) on its own 715 dates), and AR(12) is not significantly more accurate than AR(1) under HLZ. No direct test of AR(12) against AR(2), and no equivalence test, was performed."
- **Econometric justification for QUALIFIED.**
  1. **Different samples.** AR(2)'s 2.967 is on 715 dates and AR(12)'s on 714: the failed p=12 fit at origin 1974-09 is not scored. On the 714 dates AR(2) has RMSE 2.966 but MAE 2.084, against AR(12)'s 2.967 and 2.080. This is an **[audit] sensitivity**: the 714-date alignment is inferred (the only failed AR(12) fit, target 1974-10), not verified against stored T4.2 forecasts. The ordering depends on the loss function.
  2. **No direct test.** T4.2 tests each lag order only against AR(1). A "no gain" statement about p=12 relative to p=2 therefore rests on point estimates, not on inference.
  3. **Non-rejection is not equivalence.** Even a direct HLZ non-rejection would not establish equal accuracy. That needs an equivalence test with a pre-set margin, which the approved design does not contain.
  4. **Nested models.** AR(2) is nested in AR(12). Under a fixed 240-month rolling window, the ten extra coefficients add estimation noise even if their population values are zero. Equal RMSE therefore neither proves that the extra lags are uninformative nor that they help. The approved design contains no nested-model adjustment (Clark–McCracken was excluded, Part 5 §10.6), so the comparison stays descriptive.
- **Restrictions:** do not write "unnecessary", "as accurately as", "adds no accuracy" or "no benefit" as established results. State the absence of evidence of improvement, with the sample sizes.
- **Jury:** R1-15 is still RESOLVED. The requested lag-robustness analysis is performed and reported (CLAUDE.md §12).
- **Evidence:** `robustness/T4.2_*`; T3.3.
- **Jury IDs:** R1-15.

**C17 — A VAR does not overturn the univariate conclusions**
- **Status:** SUPPORTED.
- **Allowed wording:** "A monthly five-variable VAR(1) never forecasts significantly better than AR and is significantly worse for the federal funds rate under absolute loss."
- **Restriction:** for unemployment the VAR has the lowest RMSE on the VAR common sample (0.493 against AR 0.613), but the difference is not significant (HLZ p = 0.346 and 0.811). It may be stated only as a descriptive ranking.
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
- **Status:** SUPPORTED as revised below; the ranking is QUALIFIED by its sample.
- **Allowed wording:** "At the one-step horizon no model forecasts unemployment significantly better than the AR benchmark; STAR is nominally worse under absolute loss. The descriptive accuracy ranking depends on the evaluation sample. On each model's own valid forecasts, MSAR has the lowest RMSE (0.491) and ARMA the highest (0.737). Against AR on each competitor's AR-matched sample, ARMA and MSAR have the highest out-of-sample R² (0.237 and 0.189). On the 682 target dates common to all four models, ARMA and MSAR have numerically close RMSEs (about 0.48 and 0.49), both below AR (0.55); their difference was not tested for equivalence. At three and six months, AR has the lowest RMSE."
- **Three metrics, never merged:**

  | Metric | Definition | AR | ARMA | MSAR | STAR |
  |---|---|---|---|---|---|
  | RMSE, own valid sample | T3.3 `rmse` (n) | 0.551 (703) | 0.737 (689) | 0.491 (698) | 0.592 (704) |
  | OOS R² vs AR | T3.3 `oos_r2_vs_benchmark`, competitor's AR-matched sample (n) | — | 0.237 (688) | 0.189 (697) | −0.103 (703) |
  | RMSE, four-model common sample | 682 dates [audit] | 0.546 | 0.482 | 0.492 | 0.556 |

- **Restrictions:**
  - Do not claim unequivocal MSAR superiority for unemployment at h=1. MSAR's own-sample rank 1 depends on one target date (2020-05), at which the AR fit failed and is not scored and ARMA's error is −14.53.
  - Do not assert that ARMA and MSAR are statistically equivalent: no formal test of equivalence was run (HLZ ARMA versus MSAR p = 0.32 squared and 0.22 absolute is a non-rejection, not equivalence).
  - The approved metric definitions are unchanged. The common-sample RMSE is an audit computation and is not citable as a thesis number unless the user approves it as a sensitivity.
  - The descriptive MSAR advantage is also not window-robust (C14) and depends on the pandemic window (OOS R² −0.010 without 2020-01 to 2021-06 [audit]).
- **Evidence:** T3.3 and T3.3A (UNRATE rows); `forecasts/forecasts_UNRATE.csv`; `corrections/r1/part8_integration_scientific_audit.md` §6.3.
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
  3. F1 required regeneration anyway (at the time of the published report). The pipeline-written matrix should be refreshed after the approved re-run, not hand-edited now.
- **The adjudicated CSV**
  - uses the exact Part 5 §12 columns;
  - adds `adjudication_basis`, `provisional_due_to` and `adjudicated_in`;
  - adjudicates the P-04 row and adds every major claim above (C01–C23).
- **Final matrix.** `claim_evidence_matrix_final.csv` in this directory carries the final statuses, evidence and required limitations of all 24 claims. The pipeline-registered `output/manifests/claim_evidence_matrix.csv` (one empty P04 row) is not a source of claim statuses.
- If the user prefers the adjudication to live in `output/manifests/claim_evidence_matrix.csv`, that is a deliberate change to an inventoried file. It needs:
  - the inventory regenerated;
  - the old hash (`62d5ec1e…`) and the new hash recorded in a note.
