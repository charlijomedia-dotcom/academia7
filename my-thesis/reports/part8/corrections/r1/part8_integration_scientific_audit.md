# Part 8 integration dry run: scientific-impact audit of the integrated results

Date: 8 November 2026.
Session audited: `integration-20261108T052245Z-9bba8e`.
Orchestration: `a2c3171`. Scientific pin: `8aaa4217` (unchanged).

**Status of the candidate:**

| Item | Status |
|---|---|
| Dry-run outcome | `ACCEPTED_FOR_REVIEW_REVIEW_REQUIRED`, exit 4 |
| Acceptance criteria | A1–A15 pass |
| Unexplained differences | 0 |
| Estimations | none |
| Original and merged caches | unchanged at every checkpoint |

This is a **read-only scientific review of a non-published candidate**:
- no model was estimated;
- nothing was published or overwritten;
- the methodology, the pins, the original results and the Tier A/B checkpoints are unchanged;
- Part 9 was not started.

**Scientific approval of Part 8 is not granted by this document.** It is a recommendation (§10).

**Labels:**
- **[C]** confirmed from data in this round;
- **[P]** plausible interpretation;
- **[U]** unresolved.

**Evidence and reproduction:**
- Evidence folder: `evidence/integration_dryrun_audit_20261108/`, holding `colab_export/` (the 45 files), `derived/` and `f48_check/`.
- Analysis script: `integration_scientific_audit.py`.

**Release names used below:**

| Name | What it is |
|---|---|
| *base* | the published tree plus the B1-staged overlay (461 files) |
| *claims reference* | the provisional corrected release `0573a8c`, on which the R1 claim matrix was assessed |
| *published* | the original results commit `0662945` |

## 0. Summary

1. **Export integrity [C].**
   - All 45 exported files equal `export_manifest.json` in sha256 and size: 45/45, 0 mismatches.
   - The manifest's own sha256 is `b7e585f3…7612`.
2. **No new nonlinear advantage anywhere [C].**
   - Every 5% test decision that changes relative to the published output is a rejection **against** a nonlinear model or ARMA. The one exception is the ARMA-vs-AR joint Wald test (§3).
   - **No test anywhere rejects in favour of MSAR or STAR over AR, except the already known CPI h=12 MSAR result (C02).**
3. **The 175 decision-like cell changes are mostly descriptive [C].**
   - Of the 175:
     - 118 are rank changes;
     - 25 are derived robustness labels;
     - 8 are fit-status classifications;
     - 7 are significance stars;
     - **17 are 5%-level test-decision cells.**
   - The 17 test-decision cells reduce to **6 distinct statistical findings** (§2.3).
   - **150 of the 175 come from the approved corrections F1–F4**, which were already in the reviewed claims reference.
   - Of the 127 decision-like cells that differ from the claims reference, **6 are test decisions**.
4. **The UNRATE ARMA-vs-AR joint Wald "reversal" is not new evidence [C].**
   - It is the derived `all_test_results.csv` row catching up with T3.5. T3.5 already carried the F1-corrected value (χ² = 8.65, p = 0.034) in the claims reference.
   - It is a linear-versus-linear comparison.
   - The state-dependence test does not reject (p = 0.28), and no single coefficient is significant.
   - **It changes no claim.** The auto-generated "implication" text overstates it (§3).
5. **B2's 20 classification changes and 29 optimiser sensitivities [C]/[P].**
   - They are differences between the **approved live warm-start rule** and the **published post-failure artefact**. B2 equals the original cache under the approved rule at all 1,390 origins.
   - Their scientific effect is confined to one secondary-test decision (FEDFUNDS level, MSAR, DM-HLN, against MSAR), plus status counts. **No claim changes** (§4).
6. **Claims [C]/[P].**
   - All 24 claims keep their status.
   - Four need **updated wording or added qualifications**: C14, C15, C21 and C08.
   - One pre-existing **ranking-sample issue** affects how C21 may be worded (§6.3).
   - Verdicts: `derived/claim_verdicts_integration.csv`, and §6.
7. **Numerical warnings [C].**
   - They come from STAR forecasts that explode at specific horizons and targets: mean loss differentials reach 10¹⁹ to 10⁹⁷.
   - At those horizons the HLZ, DM-HLN and state-regression results carry **no usable inference**.
   - They are inadmissible as evidence either way, but they cannot hide a nonlinear gain, because STAR is the loser there.
   - The rank-deficiency warning affects only the state-dependence Wald tests of those same rows (§7).
8. **F4.8_UNRATE [C].**
   - Re-rendered locally from the rebuilt integrated table with the pinned code. The result is **byte-identical** to the Colab release (PNG `4ba7266b…`, PDF `78eb1b0d…`, as listed in `output_inventory.csv`).
   - It shows the integrated values correctly (§8).
9. **Archive: yes, needed (§9).**
   - The 465-file candidate tree existed only in the Colab VM.
   - A minimal non-publishing export procedure is specified. It is **not run and not implemented**; it awaits your authorisation.
10. **Recommendation (§10).**
    - The integrated candidate is **scientifically acceptable for Part 8 approval**, subject to:
      - the claim-wording changes in §6;
      - the archive of §9;
      - your decisions on four open items, in §10.
    - **No result requires a methodological change.**

## 1. Provenance and verification [C]

| Item | Value |
|---|---|
| Drive folder | `KillyPhD/Part8_K3_InSample_2026-10-29/baseline/r1_part8_integration_dryrun/integration-20261108T052245Z-9bba8e` (`1F907UZe…`) |
| Files | 45 listed in `export_manifest.json`, plus the manifest itself; **45/45 verified (sha256 and bytes)** |
| Orchestration / scientific commit | `a2c3171…` / `8aaa4217…`, both recorded clean (A13: `code_tree_dirty: false`) |
| Correction run | `correction-20261108T053328-949fcd76`; config hash `949fcd76…`; frozen data `7e7dc769…` |
| Certificates | B1 `de5a6fec…`, B2 `c8c90ba0…`, B3 `43bba772…` (preflight) |
| Statuses | B1 and B3 `…_REPRODUCED`; B2 `…_REVIEW_REQUIRED` |
| Caches | merged refit 11,638 files, `b403274d…`; original 18,964 files, `7e283de3…` |
| Cache checkpoints | unchanged at all four (stage 2, stage 3 before and after, stage 4) |
| Estimations | `estimations_performed` empty in both passes; the dependent replay counted 0 fits |
| Protected inputs | identical before and after (A2, `protected_inputs_after.json`) |

**Independent reproduction [C].**
- The local rehearsal (10 of 17 chains) reproduces **all 51** changed Wald cells bit for bit.
- The F4.8_UNRATE figure, rebuilt from the exported cells, is byte-identical to the Colab release.

### 1.1 The 17 corrected chains and their sources [C]

From `chain_sources.csv`, `reestimated_chain_records.csv` and A8:

| Source | Chains | Fit records replaced | Classification |
|---|---|---|---|
| Tier A archive `df73c295…` (closed form) | T4.1 FEDFUNDS AR, T4.1 UNRATE AR, T4.2 CPI AR(1/3/6/12), T4.8 UNRATE 180 AR, T4.8 UNRATE 300 AR (8) | 0 | reproduces the published records |
| Tier B B3 (`…072545Z`) | T4.1 FEDFUNDS ARMA and STAR, T4.1 UNRATE ARMA, T4.8 UNRATE 180 ARMA, T4.8 UNRATE 300 ARMA and STAR (6) | 0 | `COMPUTATION_COMPLETE_REPRODUCED`: 626/626, 626/626, 703/703, 764/764, 644/644, 644/644 |
| Tier B B1 (`…070356Z`) | T4.8 UNRATE 300 MSAR (1) | 0 | `…_REPRODUCED` 644/644 |
| Tier B B2 (`…151645Z`) | T4.1 FEDFUNDS MSAR, T4.8 UNRATE 180 MSAR (2) | 43 + 6 | `…_REVIEW_REQUIRED` (§4) |

**Other chain sources:**
- 17 chains are cache-hit replays of the original fit cache.
- 48 are published unchanged, including the B1-staged baseline UNRATE MSAR.
- 26 are unaffected and retained.

**Verification.** Each re-estimated chain's status counts equal its certificate (A8). Fit records were replaced only where expected: 43 and 6.

## 2. The 3,885 changed cells and the 175 decision-like changes [C]

### 2.1 Where the changes come from

**All 3,885 cells changed relative to the base**, by cause (from `cells_vs_b1_staged.csv.gz`):

| Cause | Cells | Of which decision-like |
|---|---|---|
| `correction` (F1–F4, F7.1 recomputation) | 3,433 | 164 |
| `correction+reestimated_chain` | 41 | 0 |
| `reestimated_chain` | 23 | 1 |
| `dependent:re-estimated chain record` (fit records) | 333 | 8 |
| `dependent:Wald rows rebuilt from the release T3.5` | 51 | 2 |
| `dependent:T4.7 recount` | 4 | 0 |

**The decision-like changes, by kind and by reference release** (`derived/decision_change_categories.csv`):

| Kind | vs base (A12) | vs claims reference `0573a8c` | vs Tier A `292227e` | vs published `0662945` |
|---|---|---|---|---|
| A. 5% test decision | 17 | **6** | 6 | 17 |
| B. significance stars | 7 | 1 | 1 | 7 |
| C. descriptive rank | 118 | 32 | 32 | 118 |
| D. fit/forecast status classification | 8 | 82 | 82 | 82 |
| E. derived robustness label | 25 | 6 | 6 | 25 |
| **Total** | **175** | 127 | 127 | 249 |

- Against the claims reference, the 82 status cells come from the B1-staged baseline (28 + 28 + 4 + 14) and B2 (8).
- They are already in the base, which is why only 8 status cells appear against the base.

### 2.2 Reversal versus description

- **Descriptive (no inference):**
  - ranks (118);
  - derived labels: `conclusion_vs_baseline` and `support_change` compare signs and decisions across windows (25);
  - stars (7), which move with the p-values listed below;
  - status classifications (8).
- **Statistical-decision cells:** 17. They reduce to the 6 findings below.

### 2.3 The six distinct statistical findings behind the 17 decision cells

All p-values are from the exported cells (`derived/test_decision_changes_vs_published.csv`).

**Sign convention.** d = loss(competitor) − loss(benchmark). A positive d means the benchmark is better.

**Findings 1–3 come from F1 and were already in the reviewed claims reference:**

1. **UNRATE, STAR vs AR, h=1, absolute loss** (cause F1).
   - Values:
     - HLZ statistic 5.49, two-sided p 0.0015;
     - DM-HLN statistic 2.86, p 0.0043;
     - d > 0, so **AR is better**.
   - The same comparison appears in T3.3A, T3.3B, T3.3 (`hlz_absolute_decision_5pct`), T4.4 (baseline row), T4.5 (VAR common sample: HLZ p 0.0088) and the 240-month window row. That accounts for 9 of the 17 cells.
   - Already documented: Holm 0.066 across the 44 STAR-vs-AR tests, and STAR stays in the 90% and 95% MCS (`multiplicity_unrate_star.md`).
2. **UNRATE, STAR vs AR, h=3, absolute loss, DM-HLN only** (cause F1).
   - DM-HLN p 0.030, with d > 0. HLZ, the primary test, gives p 0.057 and does not reject.
   - Appears in T3.3B and T4.4: 2 cells.
3. **UNRATE, ARMA vs AR, joint Wald, h=1** (§3): 1 decision cell and 1 star.

**Findings 4–6 are new relative to the claims reference** (they come from the re-estimated chains):

4. **UNRATE, STAR vs AR, h=1, absolute loss, 180-month window.**
   - HLZ p 0.046 and DM-HLN p 0.020, with d > 0 (AR better). 2 cells.
   - Previously `original_retained_pending_estimation`.
5. **UNRATE, STAR vs AR, h=1, absolute loss, 300-month window.**
   - HLZ p 0.0017 and DM-HLN p 0.0060, with d > 0 (AR better). 2 cells.
   - Findings 4 and 5 **replicate finding 1 at both alternative windows**.
6. **FEDFUNDS level, MSAR vs AR, h=1, absolute loss, DM-HLN only** (T4.1 alternative transformation).
   - DM-HLN p 0.053 → 0.029, with d > 0 (AR better).
   - **HLZ, the primary test, does not reject:** p 0.145 (0.130 before).
   - `agrees_with_hlz` therefore becomes `disagree`.
   - Cause: F1 now applies to the re-estimated AR and MSAR chains (71 and 49 failed fits masked, n 574 → 540), together with B2 (§4).

**Conclusion [C].**
- No decision change favours a nonlinear model.
- Findings 1, 4 and 5 are one result: **STAR is nominally worse than AR for UNRATE at h=1 under absolute loss, at all three window lengths.**
- Findings 2 and 6 are secondary-test-only rejections. Under the approved design (Part 5: HLZ primary, DM-HLN secondary), they do not change an inference.

### 2.4 Rank changes that move the top rank [C]

44 rank cells involve rank 1. **The new ones** (relative to the claims reference) are three, all at h=1:

| Table | Series and setting | Top rank: before → after |
|---|---|---|
| T4.1 | UNRATE in differences | MSAR → **AR** (MSAR now 3rd by RMSE, 2nd by MAE) |
| T4.1 | FEDFUNDS in levels | MSAR → **AR** (MSAR 2nd) |
| Window length | UNRATE, 300 months | STAR (RMSE) / ARMA (MAE) → **AR**; MSAR falls to 4th (OOS R² −1.10) |

**Cause [C].**
- The MSAR 300 forecasts are the published ones: the RMSE cell is unchanged.
- The change is entirely the corrected AR benchmark: F1 masks the AR forecast from a failed fit. Previously that forecast inflated AR's loss.

**Already in the claims reference** (from F1): the UNRATE baseline ranks at h=3, 6 and 12 (AR first), and the T4.5 VAR-sample ranks (VAR first at h=1, MSAR third).

## 3. The UNRATE ARMA-versus-AR joint Wald test [C]

**The test.**
- Source: `diagnostics/all_test_results.csv` row 250 ← `forecast_tests/T3.5_state_loss_regression.csv` (UNRATE, ARMA vs AR, h=1, squared loss).
- Regression: d_t = α + β_rec·REC_t + β_turn·TURN_t + u_t, with d_t = loss(ARMA) − loss(AR). The HAC rule is Newey–West with truncation h−1 = 0, i.e. White.
- Joint Wald null: α = β_rec = β_turn = 0, i.e. "equal average loss and no state dependence"; χ²(3).
- State-dependence Wald null: β_rec = β_turn = 0; χ²(2).

| | Published (`0662945`) | Claims reference T3.5 | Claims reference `all_test_results` | Integrated |
|---|---|---|---|---|
| n (turning-window obs.) | 689 (105) | 688 (104) | stale | 688 (104) |
| α (p) | −0.145 (0.115) | −0.084 (0.224) | — | −0.084 (0.224) |
| β_rec (p) | 1.102 (0.276) | 0.091 (0.117) | — | 0.091 (0.117) |
| β_turn (p) | −1.629 (0.315) | 0.0002 (0.998) | — | 0.0002 (0.998) |
| **Joint Wald χ²(3), p** | 2.49, 0.476 | **8.65, 0.034** | 2.49, 0.476 | **8.65, 0.034** (reject, `**`) |
| State-dependence χ²(2), p | 1.70, 0.428 | 2.53, 0.282 | 1.70, 0.428 | 2.53, 0.282 (do not reject) |

**Cause.**
- F1 removes the one AR forecast made from a failed fit: origin 2020-04, target 2020-05. Its raw value was 31.6, against an actual rate of 13.2.
- That single observation dominated the published loss differential and its standard errors.
- The claims-reference T3.5 already held the corrected value. Its derived `all_test_results.csv` still held the stale published row.
- The integration rebuilds the Wald rows from T3.5 (the dependent "Wald rows rebuilt from the release T3.5"), so 24 rows change and only this one crosses 5%.
- The local rehearsal reproduces all 51 changed cells exactly. The full table is `derived/wald_rows_published_vs_integrated.csv`.

**Original interpretation.** "No evidence that realized relative loss differs across states."

**Corrected interpretation [C]/[P]:**
- The joint null of zero average loss differential *and* no state effect is rejected at the nominal 5% level.
- The rejection comes from the *combination* of a small, insignificant ARMA advantage outside recessions (α = −0.084, p 0.22) and a small, insignificant ARMA disadvantage in recessions (β_rec = +0.091, p 0.12).
- The **state-dependence test does not reject** (p 0.28), and no single coefficient is significant at 10%.
- **What is wrong in the row.** Its auto-generated `implication` text ("realized relative loss differs across the predeclared states") overstates the result. A joint rejection with an insignificant slope test is not evidence of state dependence. This is a wording issue in the pinned report template, not a numerical error. Part 9 must not reuse that sentence.
- **Multiplicity.** This is one of 69 joint tests (138 Wald rows in T3.5; 134 rows in `all_test_results`) with no predeclared family. A single p = 0.034 is a nominal result.

**Affected claims.**
- **None changes status.**
- C12 ("no state-dependent nonlinear gain") concerns MSAR and STAR. For UNRATE h=1, MSAR vs AR gives joint 0.25 and slopes 0.16, and STAR vs AR gives 0.57 and 0.38.
- The R1 matrix already recorded the ARMA value (C12, corrected evidence).
- The report line that cites the joint Wald results (full report, "Joint tests reject for CPIAUCSL ARMA at h=3, 6 and 12") must add UNRATE ARMA h=1 (p 0.034; slopes 0.28) when the reports are rewritten.

**The other 23 changed Wald rows [C].**
- They are all UNRATE: ARMA, MSAR and STAR vs AR, at h=1, 3, 6 and 12, joint and slopes.
- They change through F1 (the AR loss series) and, for MSAR h=1, through the B1-staged baseline (n 692 → 697).
- None crosses 5%.
- The STAR h=6 and h=12 rows sit on explosive losses (§7) and carry no inference.

## 4. B2: 20 classification changes and 29 optimiser sensitivities [C]/[P]

**What they are [C].**
- B2's 1,390 estimates equal the original fit cache under the **approved live warm-start rule** at every origin:
  - 626/626 FEDFUNDS;
  - 764/764 UNRATE 180;
  - Δloglik, Δparameters and Δforecasts all 0 (`part8_integration_preparation_report.md` §2).
- The 20 + 29 differences are against the **published** records. Those records came from the cache-hit replay, which after a failed fit warm-starts differently from the approved rule (the post-failure artefact, `tier_b_b3_stage2_scientific_impact.md`).
- They are therefore **implementation corrections, not optimiser noise in B2**.

**T4.1 FEDFUNDS MSAR** (difference-baseline exercise; alternative level transformation):
- 14 classification changes:
  - failed → fragile: 3 (1980-01, 1981-05, 1981-06);
  - failed → failed with other reason codes: 5;
  - fragile → fragile with other codes: 6.
- 29 sensitivities: same status, B2 log-likelihood higher by 0.04 to 275 (median 24.4).
- At **all 43** differing origins, B2's log-likelihood is ≥ the published one. 33 of them follow a published failed fit directly.

**T4.8 UNRATE 180 MSAR:**
- 6 changes, 1982-01 to 1982-06: fragile → adequate 5; failed → failed with other codes 1.
- Log-likelihood lower at 5 origins (−0.01 to −0.21) and higher at 1 (+0.24).

**Scientific assessment [P]:**
- **Where they occur.** These are local optima of the MSAR(p, K=2) likelihood in regime-poor windows: FEDFUNDS around the 1980–81 Volcker disinflation, UNRATE around the 1982 recession.
- **What a higher likelihood does and does not show.** It does not make an estimate "more correct" for forecasting; it only shows the approved rule found a better local optimum. Where the approved rule finds a slightly *lower* likelihood (UNRATE 1982), that is also legitimate: the rule, not the likelihood, defines the estimator. The approved estimator is "MSAR estimated by the approved multistart with live warm start". B2 is that estimator, and the published records are not.
- **Effect on the outputs [C]:**

| Effect | Size |
|---|---|
| T4.7 status counts | FEDFUNDS MSAR failed 52 → 49 and fragile 2,410 → 2,413; UNRATE MSAR adequate 2,115 → 2,120 and fragile 1,385 → 1,380 |
| T4.7 registry events | FEDFUNDS 732 → 741; UNRATE 180: 663 → 651 |
| T4.1 FEDFUNDS level, MSAR vs AR | HLZ p 0.130 → 0.145 (no decision change); DM-HLN p 0.053 → 0.029 (secondary test now rejects **against** MSAR) |
| UNRATE 180 MSAR vs AR | HLZ p 0.39 (squared) / 0.77 (absolute); no decision change; MSAR stays first at h=1 at 180 months |

  F1 and B2 enter the FEDFUNDS DM-HLN change jointly. They are not separated here, because separating them would need the chain forecasts, which the export does not hold. **[U]**, minor.
- **Claims.** No claim depends on these chains in a direction the changes affect:
  - C07 (fragility) holds;
  - C15 is assessed on HLZ, which does not change;
  - C14 has no MSAR decision at 180 months.
- **Recommendation.** Accept B2 as the approved-rule computation. Report:
  - the 20 classification changes and 29 sensitivities in the robustness appendix, as optimiser sensitivity of MSAR in regime-poor windows (C07 and C08 already say this);
  - the F6 limitation (no global maximum claimed) as unchanged.
  
  B2's status `REVIEW_REQUIRED` can be closed by your decision. It does not need further computation.

## 5. Jury IDs (33), unmapped IDs (14) and report lines (70)

### 5.1 The 14 jury IDs not mapped to a claim [C]

Source: `jury_recheck.csv` and `jury_resolution_status.md`.

| IDs | Previous status | Effect of the integration | Status after integration |
|---|---|---|---|
| R1-01, R1-02, R1-03, R1-04, R1-05, R1-08, R1-10, R1-16, R1-20, R1-21 | outside empirical scope (structure, notation, theory, typesetting, nowcasting) | none; no empirical output involved | unchanged: outside empirical scope (Part 9) |
| R1-07 (cross-correlation uncertainty) | resolved: no cross-correlation figure produced | none | resolved |
| R1-13 (every test defined) | partial: Zivot–Andrews missing (F4) | F4 present (T2.2 +4 rows, `all_test_results` 350 → 354); every row carries H0, distribution, p and decision | **resolved**, with one caveat: the joint-Wald `implication` text (§3) must not be quoted |
| R1-23 (M2 sample) | resolved | M2SL outputs unaffected except provenance | resolved |
| V-07 (outputs ready for Part 9) | partial: F1, F2 and F4 to settle | F1, F2 and F4 applied; all pending estimation aggregated | **ready subject to your Part 8 approval and the archive (§9)** |

**The other 19 IDs** follow their claims (§6):
- 14 are `REVIEW_REQUIRED`;
- 5 are `EVIDENCE_UNCHANGED`.

**After this review:**
- none changes status adversely;
- R1-06, R1-14, R1-15, R1-19, R1-22, P-02 and P-05 can move to RESOLVED once the reports are rewritten on the approved release;
- P-04 stays tied to F6, and R1-11 stays partial (its textual part is Part 9).

### 5.2 The 70 flagged report lines [C]

`report_numbers_changed.csv` breaks down as:

| Report | Lines |
|---|---|
| full report | 22 |
| robustness findings | 30 |
| main findings | 9 |
| jury status | 5 |
| final claims | 4 |

**These reports state at their head that they describe the original publication.** A flag means a number on that line no longer equals the integrated release.

**False positives.** The matching is heuristic (A14), and about 20 flags are coincidental matches. For example:
- every report's line 17 is the R1 status banner, whose 0.551, 0.24, 0.19 and 0.10 are the *corrected* values and still correct;
- main findings line 83 (p11 = 0.9991) is a transition probability, not the Wald statistic it matched.

**Substantive lines to rewrite** when the reports are revised on the approved release:

| Report and line | Topic | What changes |
|---|---|---|
| robustness findings 54–57; full report 485, 627 | T4.1 table | UNRATE AR in differences: RMSE 0.935 → 0.563. FEDFUNDS AR in levels: 0.527 → 0.426. FEDFUNDS level MSAR: failed fits 52 → 49 (n 574 → 540 after masking). "Transformation drives the ranking" stays true, but AR is now first in both alternatives |
| robustness findings 62 | T4.1 closest p-values | FEDFUNDS level ARMA: 0.081/0.084 → 0.808/0.146. STAR absolute: 0.097 → 0.102 |
| robustness findings 268 | window length, UNRATE MSAR OOS R² | 180 / 240 / 300: 0.746 / 0.692 / 0.016 → 0.240 / 0.190 / −1.102 |
| robustness findings 277–279 | window-length summary counts | unchanged (97 unchanged / 10 reversed / 1 weakened); the composition changes (§6, C14) |
| full report 592 | joint-Wald sentence | add UNRATE ARMA h=1 (§3) |
| C21 numbers | UNRATE h=1 | MSAR RMSE 0.492 → 0.491; OOS R² 0.190 → 0.189 (B1 staged) |

## 6. Claim-by-claim verdict (24 claims) [C]/[P]

Machine-readable: `derived/claim_verdicts_integration.csv`.

**Transitions reported by the dry run (A14):**
- 9 `EVIDENCE_UNCHANGED`;
- 10 decision-like evidence changed;
- 4 values changed;
- 1 manual.

**Statuses compared:**
- *R1 status*: the corrected matrix `claim_evidence_matrix_corrected.csv`;
- *Integrated status*: my verdict on the integrated candidate.

| Claim | R1 status | Integrated status | Basis |
|---|---|---|---|
| P04 regime count | QUALIFIED | **QUALIFIED** (unchanged) | In-sample K=2/K=3 outputs untouched; F6 limitation stands |
| C01 no nonlinear gain at h=1 | SUPPORTED | **SUPPORTED** | No HLZ rejection favours MSAR or STAR at h=1 for any target. The only h=1 change is a nominal rejection *against* STAR for UNRATE (absolute loss), now replicated at 180 and 300 months (§2.3) |
| C02 CPI h=12 MSAR | QUALIFIED | **QUALIFIED** (unchanged) | CPI unaffected; Holm 0.204/1.0 retained; guarded MCS (F2) as in R1 |
| C03 MSAR lowest h=1 RMSE for GDPC1/INDPRO | QUALIFIED | **QUALIFIED** (unchanged) | GDPC1 and INDPRO cells unchanged. The 4 flagged decision cells are UNRATE rows of the shared files |
| C04 nonlinear outperform (general) | NOT_SUPPORTED | **NOT_SUPPORTED** (strengthened) | Every new rejection is against a nonlinear model |
| C05 better in-sample fit | SUPPORTED | **SUPPORTED** (unchanged) | T3.1 untouched |
| C06 regimes credible only for CPI | SUPPORTED | **SUPPORTED** (unchanged) | T3.2 and T4.3 untouched |
| C07 rolling estimates predominantly fragile | SUPPORTED | **SUPPORTED** | Status changes are small (FEDFUNDS MSAR 3 failed → fragile; UNRATE 180 MSAR 5 fragile → adequate). Pre-existing note: UNRATE MSAR is mostly *adequate* (2,120 vs 1,380 fragile in T4.7), so "predominantly" must be stated across models and targets, not per target |
| C08 STAR unstable, explosive | SUPPORTED | **SUPPORTED** + qualification | Reinforced: UNRATE STAR in differences RMSE 20.7. **Add:** STAR comparisons at explosive horizons carry no usable inference (§7; `star_test_degeneracy.csv`) |
| C09 STAR credible transition | NOT_SUPPORTED | **NOT_SUPPORTED** (unchanged) | untouched |
| C10 CPI high-inflation regime | QUALIFIED | **QUALIFIED** (unchanged) | untouched |
| C11 pre-test evidence target-specific | SUPPORTED | **SUPPORTED** (unchanged) | untouched |
| C12 no state-dependent nonlinear gain | NOT_SUPPORTED (negative finding) | **NOT_SUPPORTED** (negative finding stands) | MSAR and STAR state tests do not reject. The ARMA joint Wald (§3) is linear vs linear, with no state dependence (slopes p 0.28). TP1 identical to the claims reference |
| C13 no systematic gain at longer horizons | QUALIFIED | **QUALIFIED** (unchanged) | CPI h=12 exception. UNRATE: AR first at h=3 and h=6; STAR rejections against it (h=1; h=3 DM-HLN only) |
| C14 window-length insensitivity | SUPPORTED (UNRATE 180/300 pending) | **SUPPORTED, with a new qualification** | All 108 rows are now computed: 97 unchanged, 10 reversed, 1 weakened (same counts; rows 46 and 50 swap). No nonlinear model gains HLZ support at any length, and the UNRATE STAR rejection replicates at 180, 240 and 300. **Qualification:** UNRATE MSAR's *descriptive* h=1 advantage is not window-robust (OOS R² 0.240 / 0.190 / −1.102; rank 4 at 300 months; HLZ p 0.32 / 0.30, n.s.) |
| C15 transformation insensitivity | SUPPORTED (alternatives pending) | **SUPPORTED, with a qualification** | All 12 alternative-transformation tests computed; **no HLZ rejection** (min two-sided p 0.10). Allowed wording stands. **Qualifications:** (i) point rankings depend on the transformation: AR first for UNRATE in differences and FEDFUNDS in levels; (ii) the secondary DM-HLN rejects for FEDFUNDS level MSAR (against MSAR, p 0.029) and ARMA (in ARMA's favour, p 0.008; pre-existing) |
| C16 CPI 12 lags unnecessary | SUPPORTED (T4.2 pending) | **SUPPORTED** (now final) | T4.2 re-estimated (Tier A) equals the R1 preview: RMSE 3.075 / 2.958 / 2.969 / 2.967, common dates 714. Only p=3 under absolute loss rejects against p=1 (HLZ p 0.013); the decisions equal the claims reference |
| C17 VAR does not overturn | SUPPORTED | **SUPPORTED** (unchanged vs claims reference) | VAR vs AR UNRATE HLZ p 0.34/0.80. On the VAR common sample the VAR ranks first by h=1 RMSE for UNRATE (descriptive) and STAR is nominally worse than AR (finding 1) |
| C18 no credible third regime | QUALIFIED | **QUALIFIED** (unchanged) | F6 |
| C19 conditional heteroskedasticity | SUPPORTED | **SUPPORTED** (unchanged) | T4.6 rows unchanged (validated against the base) |
| C20 October 2025 LOCF | SUPPORTED | **SUPPORTED** | T4.9 UNRATE: identical ranks with and without LOCF-exposed dates (MSAR, AR, STAR, ARMA); OOS R² 0.189 vs 0.191. The 28 status changes are the B1-staged baseline |
| C21 UNRATE rankings | SUPPORTED (corrected) | **SUPPORTED, with a required wording change** | Numbers: AR RMSE h=1/3/6/12 = 0.551 / 0.942 / 1.165 / 1.492; MSAR h=1 RMSE 0.491, OOS R² 0.189; ARMA 0.237; STAR −0.103. **But see §6.3:** the h=1 RMSE rank (MSAR 1st) compares models on different samples |
| C22 policy-rate MSAR collapses to AR | SUPPORTED | **SUPPORTED** (unchanged) | untouched |
| C23 transferability | QUALIFIED | **QUALIFIED** (unchanged) | design claim; manual check: no output involved |

**Claims flagged `REVIEW_REQUIRED` and their outcome:**

| Group | Claims | Outcome |
|---|---|---|
| Decision-like evidence changed | C01, C02, C03, C04, C07, C08, C13, C14, C15, C21 | All reviewed. C02 and C03 flags come from UNRATE cells in shared files. C14, C15 and C21 need wording changes; C08 needs a qualification |
| Values changed | C12, C16, C17, C20 | Reviewed: no change |
| Manual | C23 | Reviewed: no change |

### 6.1 C14: wording for Part 9

> "Across the predeclared 180/240/300-month and 90/120/150-quarter windows, 97 of 108 test conclusions are unchanged and no nonlinear model gains inferential support at any length. For unemployment, STAR is nominally less accurate than AR at h=1 under absolute loss at all three lengths. The descriptive h=1 advantage of MSAR for unemployment is not robust to the window length."

### 6.2 C15: wording for Part 9

> "Modelling unemployment in differences or the federal funds rate in levels yields no significant forecast differences against AR under HLZ. Point rankings, however, depend on the transformation: AR has the lowest h=1 RMSE under both alternative transformations."

### 6.3 C21 and the ranking-sample issue: pre-existing, surfaced by this audit [C]

**The issue.**
- `rank_rmse` ranks each model by RMSE over its *own* valid forecasts.
- `oos_r2_vs_benchmark` uses the sample common with AR.
- For UNRATE at h=1 the two disagree because of **one target date, 2020-05**, the pandemic jump to 13.2%:

| Model | Own n | Own RMSE | Status at 2020-05 | Error at 2020-05 | RMSE on the 682 dates common to all four |
|---|---|---|---|---|---|
| AR | 703 | 0.551 | failed (masked by F1) | — | 0.546 |
| ARMA | 689 | 0.737 | fragile | −14.53 | **0.482** |
| MSAR | 698 | 0.491 | fragile | −1.83 | 0.492 |
| STAR | 704 | 0.592 | fragile | −3.37 | 0.556 |

**What follows.**
- On the common sample, **ARMA and MSAR are essentially tied** (0.482 vs 0.492), both ahead of AR.
- MSAR's "rank 1" depends on AR being masked and ARMA being scored at that one date.
- This is the approved metric definition. **Nothing is to be recomputed or changed.** But the C21 wording must not imply that MSAR is the most accurate unemployment forecaster at h=1.
- **Proposed C21 wording:**

  > "At h=1, MSAR and ARMA have the highest out-of-sample R² against AR (0.19 and 0.24 on the common sample), and none of the h=1 differences against AR is significant except STAR's nominal underperformance under absolute loss. AR is the most accurate model at h=3 and h=6."

- **Where else it appears.** The same caution applies to every `rank_*` column where models fail at different origins (T4.1, T4.4, T4.8, T4.9). Part 9 should rank on the common sample (OOS R², `rmse_common`) where available.
- **Decision for you.** This is a presentation and interpretation point under CLAUDE.md §4. It is raised for your decision, not changed.

## 7. HLZ, DM-HLN and state-regression warnings [C]

**Source.** `console.log` contains 156 warning lines, the same set as in the earlier runs:
- HLZ: `hlz.py:206/219/225`, overflow or invalid in matmul, power and subtract;
- DM-HLN: `dm_hln.py:28/32`;
- statsmodels sandwich covariance;
- `linear_model.py:2121`, sqrt of a negative;
- 28 × `state_loss_regression.py:90` ValueWarning: "covariance of constraints does not have full rank (2 constraints, rank 1)".

**The rows behind them** (integrated tables):

| Table | Rows | Description |
|---|---|---|
| T3.3A | 58 of 230 | Mean loss differential beyond 10³, up to 8×10⁹⁷: STAR vs AR for CPIAUCSL (h=1–12), UNRATE (h=6, 12), INDPRO (h=1–12), FEDFUNDS (h=3–12, squared), M2SL (h=1–12) |
| T3.3A | 4 | Statistics unavailable (CPI and M2 STAR h=12, squared loss) |
| T3.5 | 15 | STAR vs AR regressions with |α| between 10³ and 10⁸⁰ |

**Admissibility.**
- At these rows a few exploding STAR forecasts dominate Σd². HLZ statistics settle near 1.59–1.69 with p ≈ 0.31–0.33, whatever the size of the loss differential.
- These are **degenerate, non-informative tests**. They must be read as "no usable inference: the STAR forecasts exploded", **not** as "no significant difference" (`tier_a_review.md` §6; `star_test_degeneracy.csv`).
- The rank-deficient Wald warnings are the state-dependence tests of the same explosive STAR rows. One state coefficient is numerically unidentified, so those slope tests are also non-informative.

**Inference and conclusions.**
- **C01, C04, C12, C13, C14 and C17 are unaffected.** In every degenerate row STAR is the loser by orders of magnitude, so a degenerate non-rejection cannot conceal a nonlinear gain.
- **C08 is strengthened.** It must carry the qualification in §6.
- The UNRATE h=1 STAR result is *not* degenerate (largest single share of Σd²: 0.28 absolute, 0.41 squared).
- **What is unchanged.** These warnings come from the pinned procedures and the unchanged baseline STAR chains. The integration neither causes nor removes them. No warning is suppressed, and the methodology is unchanged.

**Pre-existing observation, unchanged [U].**
- T3.5 FEDFUNDS ARMA vs AR, h=6: `state_dependence_supported_5pct = True` although the slopes Wald p is 0.082. The flag appears to follow β_turn's individual p (0.031).
- The row is unchanged from the publication and unrelated to the integration. It is noted for the report rewrite.

## 8. F4.8_UNRATE, robustness findings, rankings and economic conclusions [C]

**F4.8_UNRATE.**
- A11 validated the re-rendered figure against the integrated table in Colab.
- I rebuilt the integrated `window_length_comparison.csv` (claims reference plus exported cells) and rendered it with the pinned code. The result is byte-identical to the Colab release (`f48_check/`). The same renderer reproduces the published F4.8_UNRATE.png byte for byte.

**What the figure shows** (h=1 OOS R² against AR; 180 / 240 / 300 months):

| Model | 180 | 240 | 300 |
|---|---|---|---|
| ARMA | 0.302 | 0.238 | 0.202 |
| MSAR | 0.240 | 0.190 | −1.102 |
| STAR | −2.714 | −0.104 | −0.075 |

The published values were:

| Model | 180 | 240 | 300 |
|---|---|---|---|
| ARMA | 0.411 | 0.324 | 0.252 |
| MSAR | 0.746 | 0.692 | 0.016 |
| STAR | −0.284 | 0.555 | 0.490 |

**Defects.**
- None in content.
- Cosmetic: the N labels of ARMA and MSAR overlap at 180 and 240 months. This is a pinned plotting layout; it is not changed (F8-like presentation changes need your approval).

**Robustness findings.**
- Across T4.1, T4.2, T4.4, T4.5, T4.8 and TP1, no robustness exercise produces a nonlinear-over-AR rejection.
- The only nonlinear-over-AR rejection anywhere remains CPI h=12 MSAR (C02, not family-wise robust).

**Model rankings.**
- AR or ARMA is first in most UNRATE and FEDFUNDS settings after F1.
- MSAR's UNRATE h=1 point advantage is sample-dependent (§6.3) and window-dependent (§6.1).

**Main economic conclusions.** Unchanged in substance:
- no systematic forecasting gain from MSAR or STAR over linear benchmarks for these six U.S. targets;
- in-sample nonlinearity that is mostly not credible (C05, C06);
- STAR unstable as a rolling forecaster;
- one small, non-robust CPI h=12 MSAR gain.

The integration removes the last "pending estimation" caveats and makes the negative conclusion *more* robust.

## 9. Does the full candidate release need to be archived? Yes [C]

**What exists today:**
- The integrated tree (465 files) existed only in the ephemeral Colab VM.
- The 45 exported files are audit evidence: reports, diffs and manifests. `release_manifests/output_inventory.csv` records the sha256 of every release file.

**Why that is not enough.**
- Independent review needs the files themselves.
- A re-run would not be byte-identical in the provenance-carrying files: run ID and timestamps change.
- So the inventory alone cannot certify a re-generated tree.

**Minimal, safe, non-publishing export procedure** (proposed; **not implemented and not run**):

1. **Pins.** Same orchestration `a2c3171` and scientific pin `8aaa4217`. No code change to the stages.
2. **New session.** Re-run stages 0–5 exactly as before. Estimation stays refused, the caches are read-only, and the strict cache-integrity checks stay on.
3. **Equivalence gate.** Before export, compare the new session's machine reports with the audited session's 45 exported files. The run refuses to export unless all of the following hold:
   - `acceptance.json` criteria pass;
   - `unexplained_differences.csv` is empty;
   - the four `cells_vs_*.csv.gz` files are identical in path, row, column, old and new;
   - `decision_changes.csv` is identical;
   - every `output_inventory.csv` row whose file carries no provenance field has the same sha256.

   This ties the archive to the audited computation without relying on provenance bytes.
4. **Export.** Write `release.tar.gz` (the 465-file candidate tree), its own sha256 inventory, and `equivalence_report.json` to a **new** Drive folder: `baseline/r1_part8_integration_candidate_archive/<session>/`.
   - It never writes to `output/`, `output_staging/`, releases, certificates or checkpoints.
   - There is no git push and no publication flag.
5. **Cost.** About 20 minutes of Colab time; no estimation.

Implementing it means adding an archive stage and an equivalence gate to the driver, with tests, plus regenerating the notebook. **I have not done this. It awaits your authorisation.**

## 10. Assessment, limitations and recommendation

### 10.1 Limitations and unresolved items

1. **[U] F6.** No global MSAR maximum is claimed. UNRATE K=3 is inconclusive. Unchanged.
2. **[U] B2 versus F1 decomposition** of the FEDFUNDS-level DM-HLN change (§4). It is minor and involves a secondary test only.
3. **[U] Ranking-sample definition** (§6.3). Pre-existing; needs your decision on how Part 9 states rankings.
4. **[U] Template wording.** The joint-Wald `implication` text (§3) and the T3.5 `state_dependence_supported_5pct` flag (§7) are not to be quoted without qualification.
5. **Not verified here.** The figures other than F4.8_UNRATE and the 465 files themselves are not in the export. A11 checked them in Colab. Independent file-level review needs the archive (§9).
6. **Multiplicity.** All p-values are nominal (no predeclared family). The Holm figures are audit sensitivities, not approved outputs.

### 10.2 Recommendation

- **Scientific acceptability.** The integrated, non-published candidate is scientifically acceptable as the basis of the final Part 8 results, because:
  - every change is attributable;
  - no estimation was performed;
  - no decision reverses in favour of a nonlinear model;
  - the remaining changes either correct implementation errors (F1–F4, B1, B2) or complete previously pending robustness rows;
  - all 24 claims keep their status.
- **Before you approve Part 8, please decide:**
  1. **B2.** Accept B2 as the approved-rule computation and close its `REVIEW_REQUIRED` status (§4).
  2. **Claim wording.** Approve the wording changes for C14, C15 and C21 and the qualification for C08 (§6), including how rankings are stated (§6.3).
  3. **Archive.** Authorise the non-publishing archive export (§9), or decline it.
  4. **F8 and D3.** F8 stays off unless you confirm it. D3 (publication destination) stays deferred.
- **After those decisions:**
  - the Part 8 reports (`main_findings.md`, `robustness_findings.md`, `full_empirical_analysis_report.md`, `jury_resolution_status.md`, `final_claims_allowed.md`) would be rewritten on the approved candidate;
  - publication would follow only on your explicit instruction.
- **Not done:** no publication, no Part 9.
