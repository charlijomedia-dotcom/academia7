# Change log: Part 8 report drafts on the integrated candidate (8 November 2026)

## Scope and sources

**Scope.** These five drafts revise the published Part 8 reports (`reports/part8/*.md`, unchanged) onto the integrated candidate:
- session `integration-20261108T052245Z-9bba8e`;
- run `correction-20261108T053328-949fcd76`;
- orchestration `a2c3171`;
- pin `8aaa4217`.

They are **drafts for independent review**. They are not approved, not published and not in `output/`.

**Sources**

| Source | What it holds |
|---|---|
| `corrections/r1/evidence/part8_drafts_20261108/integrated_numbers.json` | Integrated values. Built by `corrections/r1/integration_numbers.py` from the claims-reference release (`0573a8c`) and the audited `cells_vs_claims_reference.csv.gz` |
| `rebuild_crosscheck_vs_local_rehearsal.json` | Cross-check of the rebuilt tables against the local rehearsal. 0 differences for every table, except the B1/B3 chain tables (T4.1 and window length), which exist only on Drive |
| `registry_reason_codes_local_rehearsal.json` | T4.7 reason-code counts, taken from the local rehearsal (34,122 rows, equal to the candidate's count) |
| `number_checks.csv` | 105 quoted fragments checked against those values. All pass (`corrections/r1/check_draft_numbers.py`) |
| `corrections/r1/part8_integration_scientific_audit.md` | Cause attribution and claim verdicts (commit `3da0e71`) |
| `corrections/r1/b2_scientific_adjudication.md` | B2 acceptance |

**Numbers not invented.** Every new number comes from the sources above or from the integration audit. Values the drafts do not recompute are kept as published only where the candidate leaves them unchanged:
- T3.1, T3.2, T4.3 and T4.6;
- non-UNRATE baseline rows;
- A3 for GDPC1 and INDPRO.

The integration audit verified these as unchanged. Where a source could not be fully verified, the draft says so (the T4.7 reason codes).

## Changes common to all five files

1. **Banners.** The "Correction phase" and "R1 status" banners are replaced by one draft banner. It states:
   - the candidate's identity;
   - the B2 acceptance;
   - that the numbers are not yet citable under CLAUDE.md §9;
   - what is unchanged;
   - that F8 is disabled and D3 deferred.
2. **Paths.** "relative to `output/`" now reads "`output/`-relative paths of the candidate tree".
3. **Provisional markers removed.** "⚠F1", "pending F1" and "provisional" are removed, because F1 and F2 are applied and every pending chain is computed. The limitations that remain (F5, F6, F8, B2 optimiser sensitivity, multiplicity, failures, degenerate tests, significance versus ranking) are stated explicitly instead.

## `main_findings.md`

| § | Change | Source |
|---|---|---|
| Header | "Run" line becomes "Provenance" (original estimation run plus integrated candidate). A paragraph on inference language is added | banner |
| 1 | "UNRATE is pending F1" is dropped; C01 holds for all six targets. Added: every decision change goes against a nonlinear model. "PROVISIONAL for UNRATE" is dropped from the status | T3.3A; audit §2.3 |
| 3 | Rolling MSAR fragility 10,252 → 10,246 of 15,443. Added the C07 clarification ("predominantly" means pooled; UNRATE MSAR is majority-adequate: 2,120 / 1,380; baseline chain 258 of 704) and the B2 optimiser-sensitivity paragraph (20 / 29; F6) | FR; T4.7 status counts; B2 record |
| 4 | UNRATE row: 0.690 published / 0.190 [audit] → 0.189, with a pointer to the note. **New table of the three C21 metrics** (own-sample RMSE; OOS R² on the AR-matched sample; RMSE on the 682 common dates) and the 2020-05 explanation. No equivalence claim; MSAR not called most accurate; ARMA vs MSAR HLZ 0.32 / 0.22 | T3.3; T3.3A; audit §6.3 |
| 4 | MCS: the "unavailable" sentence is replaced. All 92 cells are available; at h=1 ARMA is excluded only for CPI absolute 90% and STAR only for FEDFUNDS absolute 90% and 95% | T3.4 |
| 4 | A3 table: UNRATE MSAR 0.190 / −0.001 → 0.189 / −0.010; row added for UNRATE ARMA (0.237 / −0.051). Status now mentions the dependence on the evaluation sample | integrated A3 [audit] |
| 5 | Added UNRATE STAR worse (p 0.0015; Holm 0.066; in the MCS; replicates at 180 and 300). STAR p-value clustering 51 → 50 of 88. **New paragraph on degenerate tests**: numerical instability versus inference; 58 rows; no affirmative claim | T3.3A; T4.8P; `star_test_degeneracy.csv` |
| 6 | **New:** the UNRATE ARMA-vs-AR joint Wald (8.65, p 0.034) reported separately from the state-dependence test (2.53, p 0.282), with all coefficients; not read as state dependence. FEDFUNDS ARMA h=6: slopes p 0.082 added | T3.5R; audit §3, §7 |
| 8 | Robustness list rewritten: T4.1 (no HLZ rejection; AR first under both alternatives), T4.2 (714 dates; p=3 HLZ 0.013), T4.4 (11 of 138), T4.8 (UNRATE STAR at all lengths; UNRATE MSAR not window-robust: 0.240 / 0.190 / −1.102) | T4.1, T4.2, T4.4P, T4.8C/P |
| 9 | FR 448 / 23,008 / 43,797 → 435 / 23,002 / 43,816. Registry 34,153 (540 / 33,613) → 34,122 (512 / 33,610). Baseline failures 34 → 29 (UNRATE MSAR 11 → 6). B2 sensitivity added | FR; T4.7; T3.3 |
| 10 | "Any UNRATE AR-relative number until F1" removed. Added: MSAR most accurate for UNRATE or equal to ARMA; the joint Wald as state dependence; degenerate tests; a global MSAR maximum | — |

## `robustness_findings.md`

| Section | Change | Source |
|---|---|---|
| Labels | ⚠F1 definition replaced by "F1 applied; pending chains computed". Paragraph added on ranking versus significance | — |
| T4.1 table | UNRATE levels: AR 0.886 → 0.551; ARMA R² 0.323 → 0.237; MSAR 0.492 (0.690) → 0.491 (0.189); STAR R² 0.554 → −0.103. UNRATE differences: AR 0.935 → 0.563; R² 0.365 / 0.311 / −491.1 → 0.419 / 0.330 / −0.202. FEDFUNDS levels: AR 0.527 → 0.426 (n 555); ARMA R² 0.033 → 0.003 (n 550); MSAR 0.442 (−0.273, n 574) → 0.456 (−0.307; 577 valid, 540 matched); STAR R² −2.418 → −4.180. New sentence: AR ranks first under both alternatives | T4.1 |
| T4.1 inference | Closest p: ARMA 0.081 / 0.084 → 0.808 / 0.146; STAR 0.097 → 0.102 (minimum). DM-HLN: ARMA abs 0.017 → 0.0076; **new** MSAR abs p 0.029 against MSAR (HLZ 0.145), attributed jointly to F1 and B2 | T4.1P; B2 record |
| T4.1 failures | MSAR failed 52 → 49 (B2: 3 failed → fragile). AR failures noted as not scored. The UNRATE STAR differences explosion is explained by the two excluded dates | T4.1; FR |
| T4.1 conclusion | "Inference unchanged; rankings depend on the transformation"; status QUALIFIED for rankings (C15) | audit §6.2 |
| T4.2 | All four rows recomputed: RMSE 3.073 / 2.958 / 2.969 / 2.969 → 3.075 / 2.958 / 2.969 / 2.967; R², HLZ and DM-HLN p updated (p=3 abs HLZ 0.012 → 0.013); common dates 715 → 714. F1 caveat replaced by the Tier A note; the p=2 row is labelled own-sample | T4.2, T4.2P |
| T4.4 | 10 → 11 rejections; row added for UNRATE STAR h=1 abs (p 0.0015, Holm 0.066). UNRATE multi-step paragraph replaced with integrated values | T4.4P; T3.3 |
| T4.5 | UNRATE common dates 525 → 527. UNRATE row 0.626 / 1.011 / 0.616 / rank 2 → 0.493 / 0.613 / 0.353 / rank 1 (descriptive). Added UNRATE STAR abs reject (p 0.0088) and VAR vs AR UNRATE non-significance (0.346 / 0.811) | T4.5C, T4.5P |
| T4.8 | UNRATE MSAR 0.746 / 0.692 / 0.016 → 0.240 / 0.190 / −1.102; ARMA and STAR UNRATE rows added. Added: UNRATE STAR rejections at 180 / 240 / 300 (0.046 / 0.0012 / 0.0017); MSAR rank 4 at 300; support-change composition (90 / 15 → 87 / 18). MCS: "2 of 282 unavailable" → all 288 rows (72 cells) available. Status QUALIFIED for the UNRATE ranking (C14) | T4.8C/P/M |
| T4.9 | UNRATE MSAR R² 0.691 / 0.690 → 0.191 / 0.189 | T4.9 |
| TP1 | "207 rows" → 552 rows (207 comparisons); 174 / 24 / 3 / 6 (published 175 / 23); 9 UNRATE rows change label | TP1 |
| New sections | "Optimiser sensitivity of rolling MSAR (B2; C07)" and "Degenerate STAR tests" | B2 record; audit §7 |
| Overall verdict | The two "pending" items are replaced by the ranking qualification and a list of remaining limitations | — |

## `full_empirical_analysis_report.md`

| Section | Change |
|---|---|
| Header | Integrated-candidate identity added; original run kept as "original estimation run"; date of draft |
| §0 | Number sources and [audit] rule updated for the candidate |
| Exec. 1–2 | Candidate provenance bullet. "Three implementation defects" rewritten as "defects and their correction": F1–F4 and F7.1 corrected; B1 / B2 / B3 recomputed; F5, F6 and F7.2/F8 open |
| Exec. 3 | UNRATE pending removed; new nominal STAR-worse result; UNRATE descriptive-winner caveat (C21) |
| Exec. 6 | Added: point rankings are less robust than inference |
| A.1–A.2 | Labelled "original run" |
| A.3 | UNRATE MSAR 11 failed / 693 common → 6 / 697 |
| B.1 | MSAR row 5,109 / 10,252 / 82 → 5,128 / 10,246 / 69; totals updated; UNRATE baseline 260 / 11 → 258 / 6; C07 clarification; B2 paragraph |
| C.1 | Registry 34,153 → 34,122, failed and fragile reason codes updated from the local-rehearsal registry (source stated); failed fits FEDFUNDS MSAR 52 → 49, UNRATE MSAR 30 → 20; baseline failures 34 → 29; F1 caveat replaced by the scoring rule |
| D.0 | Disagreements 11 → 12 (new: UNRATE STAR h=3 abs, DM only); sign convention rewritten for the corrected label (F3); rejections 18 → 19 with composition; STAR clustering 51 → 50; degenerate-test paragraph (58 rows; non-informative; not "no difference") |
| D.1 | UNRATE row recomputed (0.551; 0.237 / 0.336 / 0.518; 0.491 / 0.189 / 0.367 / 0.322; 0.592 / −0.103 / 0.587 / **0.0015**); footnote replaced; UNRATE AR–STAR rejection; MCS without unavailable cells; **C21 three-metric table**; A3 UNRATE rows updated |
| D.2 | UNRATE paragraph replaced with integrated multi-step values (AR first at h=3 and 6; ARMA at h=12 by RMSE; MSAR R² −0.129 / −0.538 / −0.952) |
| D.3 | **Joint versus state-dependence Wald for UNRATE ARMA h=1**; FEDFUNDS ARMA h=6 flag caveat; individual β_rec rejections; UNRATE MSAR / STAR Wald p; degenerate STAR regressions; TP1 counts |
| E | UNRATE STAR and MSAR cells rewritten; MSAR verdict for UNRATE |
| F | T4.1, T4.2, T4.4 and T4.8 rows updated as in the robustness file |
| G | Jury summary aligned with the jury draft (15 / 3 / 11) |
| H0 | F4 now in T2.2; B2 paragraph; rankings-versus-samples paragraph |
| H | Limitation 1 rewritten (open items; F8 disabled); 4 adds B2; 6 adds the Holm figures; new 8 (degenerate tests, template wording) and 9 (significance versus rankings) |

## `jury_resolution_status.md`

| Remark | Published → draft | Basis |
|---|---|---|
| R1-06 | PARTIAL → **PARTIAL** (unchanged) | F1 removes the UNRATE spike, but F8 is disabled, so the CPI F3.4 main panel is still compressed. **This departs from the integration audit**, which listed R1-06 as able to move; that assumed F3.4 presentation would be settled |
| R1-12 | RESOLVED (minor F7.1 note) → RESOLVED, note removed | F7.1 applied |
| R1-13 | PARTIAL → RESOLVED | ZA in `all_test_results` (354 rows); caveat on joint-Wald implication text |
| R1-14 | PARTIAL → RESOLVED | MCS all cells; F3 corrected; F1 applied; degenerate rows reported |
| R1-15 | PARTIAL → RESOLVED | T4.2 recomputed, 714 dates |
| R1-19 | PARTIAL → RESOLVED | UNRATE VAR row computed |
| R1-22 | PARTIAL → RESOLVED on the candidate | Corrections applied; failures and B2 sensitivity visible; final after archive, approval and publication |
| P-02 | PARTIAL → RESOLVED | ZA in outputs; UNRATE caveat kept |
| P-03 | RESOLVED | MSAR level failures 52 → 49 |
| P-05 | PARTIAL → RESOLVED | UNRATE multi-step computed |
| V-05 | RESOLVED | Wald caveat added |
| V-07 | PARTIAL → READY SUBJECT TO APPROVAL | — |
| Summary | 8 / 10 / 0 / 11 → 15 / 3 / 0 / 11 | — |

## `final_claims_allowed.md`

| Claim | Change |
|---|---|
| Purpose | Integrated candidate; points to the integration claim verdicts; the matrices are not edited |
| General restrictions | Added: significance versus ranking; degenerate tests; joint tests |
| Provisional table | Replaced by the lifted-flags paragraph. Status changes: against R1, none; against the published report, C21 INCONCLUSIVE → SUPPORTED as revised |
| C01 | Provisional note removed; note on rejections against STAR |
| **C07** | Wording names the pooled counts (10,246 / 12,702 of 15,443), the per-chain variation and the B2 sensitivity; **clarification of "predominantly"** (not to be applied to UNRATE MSAR); F6 limitation; evidence adds T4.7 status counts and the B2 items file |
| **C08** | Wording adds degenerate tests. **Required distinction:** numerical instability versus statistical inference; degenerate tests support no affirmative claim; only non-degenerate STAR tests support inference |
| C12 | Restriction: report the UNRATE ARMA joint Wald (p 0.034) separately from the slopes test (p 0.282); not evidence of state dependence; do not quote the implication text or the FEDFUNDS flag unqualified |
| C13 | UNRATE pending removed; wording added (AR lowest RMSE at h=3 and 6) |
| **C14** | New wording (audit §6.1) with supporting numbers |
| **C15** | New wording (audit §6.2) plus DM-HLN disclosure (F1 + B2) |
| C16 | Marked final. Wording changed from "forecasts as accurately as AR(12)" to RMSE equality to three decimals, plus a restriction that no direct p=2-vs-p=12 test exists. **Proposed, not requested; please confirm** |
| C17 | Restriction on the UNRATE VAR rank (descriptive; HLZ 0.346 / 0.811) |
| **C21** | Rewritten. The three metrics are kept separate (table), with the approximate common-sample values 0.48 / 0.49. No equivalence claim; no unequivocal MSAR superiority; metric definitions unchanged; window and pandemic dependence |
| §4 | Note that the matrix is to be refreshed only as a separate, reviewed step |

## What is deliberately unchanged

- T3.1, T3.2, T4.3 and T4.6 content, and every non-UNRATE baseline number. The integration leaves them untouched.
- `claim_evidence_matrix_adjudicated.csv` and `corrections/r1/claim_evidence_matrix_corrected.csv`.
- No metric definition, test, threshold or methodology choice.
