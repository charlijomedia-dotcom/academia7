# Academic review memorandum: Chapters 3 and 4

**Review date:** 14 November 2026  
**Status:** Substantive manuscript review completed; **working drafts, not certified submission-ready**.  
**Manuscript branch:** `part9-thesis-writing`  
**Authoritative final outputs:** `9817daf91ac4cb4aaa42c2bef5deaff5b674841b`  
**Controlling writing documents reviewed:** `WRITING_BLUEPRINT.md`, `SECTION_EVIDENCE_MAP.md`, `APA_SOURCE_REGISTER.md`, Part 4 structure and detailed plan, and `final_claims_allowed.md`.

This memorandum is an internal academic quality-control record and is not part of the dissertation body.

## 1. Review verdict

**Substantive conclusion: supported as a bounded claim.** Neither MSAR nor STAR establishes general one-step superiority over AR for the six U.S. targets under the primary reported test. The nominal CPI MSAR twelve-month exception is kept distinct from the primary result and is explicitly qualified by the supplementary Holm multiplicity sensitivity. A non-rejection is not described as statistical equivalence. The thesis appropriately distinguishes empirical prediction from structural causality, historical state labels from forecasting-time information, and in-sample fit from prediction.

**Fitted equations: consistent with the source specifications.** The CPI AR(2) coefficient reconstruction matches the final BIC to approximately 1.82e-12. The initial VAR(1) numerical coefficient matrix reproduces its published BIC to approximately 9.09e-13 and now uses the actual variable order. The two- and three-state CPI MSAR parameterizations match the mean-adjusted latent-state autoregression implemented in the research code. Their parameters and available uncertainty estimates were cross-checked with the final regime-parameter output. They are properly described as full-sample/in-sample estimates, not fixed rolling-forecast coefficients.

**Empirical tables: verified to the extent tested.** A systematic recheck of 132 Chapter 3 numerical entries against the final output files found no substantive numerical disagreement; three first-pass string mismatches came from a Unicode minus sign and rounding of displayed state means. Earlier precision checks of 124 Chapter 4 numerical cells were also confirmed against the final evidence, and no scientific-value edits have been made since. The audit does not assert that every sentence or every coefficient in every archived file has been independently recomputed.

**Scope and inference: generally aligned with the approved claims.** The K=3 check remains in-sample only, the unemployment K=3 numerical comparison remains inconclusive rather than validating K=2, the recession/turning analysis is explicitly retrospective, and explosive STAR forecasts are not mischaracterized as ordinary evidence of equal accuracy.

## 2. Corrections made during this review

1. Added an interpretable CPI two-state smoothed-regime probability figure to Chapter 3, with shaded NBER recession dates and an explicit warning that smoothed state probabilities are not available at historical forecast origins. The figure bytes on the thesis branch agree with the final release.
2. Clarified the Chapter 3 recession/turning loss-regression interpretation. Ex-post recession and turning indicators are not necessarily measurable at the forecast origin; the regression is an analysis of historical state-associated loss, **not** a formally implementable Giacomini–White conditional forecast-selection rule.
3. Condensed Chapter 3's chapter-ending synthesis from approximately 737 to 413 words, removing repeated evidence while retaining the baseline inference, target-specific exceptions, numerical fragility and handoff to Chapter 4.
4. Condensed Chapter 4's chapter-ending synthesis from approximately 846 to 434 words, consistent with the instruction to give one concise integration rather than a second catalogue of results.
5. Standardized the three-author Harvey–Leybourne–Zu (2025) narrative citation to **Harvey et al. (2025)** under APA 7.
6. Kept all scientific results, underlying data, research code, numerical tables and fitted coefficients unchanged.

## 3. Guideline compliance checklist

| Requirement | Review status | Note |
|---|---|---|
| European two-part, four-chapter monograph | Conforms | Chapters 3 and 4 occupy Part II and follow the approved empirical sequence |
| Numbered sections 3.1–3.9 and 4.1–4.11 | Conforms | All mandated main sections present |
| Adequacy before predictive ranking | Conforms | Chapter 3 pretests and fit diagnostics precede forecast comparisons |
| Fitted parameters explained and uncertainty disclosed | Conforms within reported models | AR(2), K2/K3 CPI MSAR and initial-window VAR(1) are all bounded correctly |
| Distinguish in-sample BIC, own-valid RMSE, paired OOS R2 and HLZ | Conforms | Evaluation-calendar differences stated repeatedly where material |
| No false inference from nonsignificance | Conforms | Non-rejection not equated with forecast equivalence |
| K3 regime-count assessment | Conforms | Unemployment comparison explicitly inconclusive; no K3 OOS claim |
| GW-style state test and business-cycle timing | Clarified during review | Ex-post states are not forecast-time instruments |
| Extreme STAR predictions and invalid tests | Conforms | Extreme finite losses retained and degeneracy disclosed |
| Causal, international and real-time scope limits | Conforms | No optimal policy or international model rankings claimed |
| Chapter-ending synthesis limited to one page | Substantially improved | Conclusions now approximately 413 and 434 words; physical page count still needs typesetting |
| No internal workflow/jury/GitHub references in thesis prose | Conforms | No such internal language found in the manuscript bodies |
| Scholarly citations and APA 7 | Working-draft compliant | Key foundational records checked with publisher metadata; full bibliography/citation pass still needed during assembly |
| Equation numbering, syntax and cross-references | Conforms structurally | 10 displayed equations total; cross-references to included chapters resolve, including 2.17 |
| Selected empirical figures | Improved | Chapter 3 now has one CPI state-probability figure and Chapter 4 one corrected separate-scale STAR figure |
| Body pages 26–30 per chapter | **Not yet certified** | Each body is approximately 16,700 words. Exact page count depends on final formatting, tables and figures |
| Appendices and front matter | **Pending** | The appendices and global symbols/acronyms list must be assembled and verified before submission |

## 4. Outstanding issues that cannot be certified solely by copyediting

**A. Page length and final typography (author clarified 14 November 2026).** The initial 26–30-page-per-chapter figures were provisional editing targets and are **not binding**. Scientific meaning, coherent argumentation, and Reviewer 1 compliance now override those estimates. The chapters should not be shortened merely to meet a page quota. A final paginated Word/PDF still requires review for legible equations, tables, figures, footnotes and the relationship between main text and appendices, with only genuinely duplicative discussion trimmed.

**B. Appendix architecture (resolved after this review on 14 November 2026).** A uniform four-part structure now exists: Appendix A (data and diagnostics), B (estimation and forecast evaluation), C (robustness and numerical fragility), D (reproducibility and corrections). The writing blueprint was updated, the chapter references now identify actual tables, and Reviewer 1's separate front-matter notation list has been created. Remaining production work is to assemble and paginate the appendices with the whole dissertation, verify the rendered tables and graphics, and recheck cross-references.

**C. Final bibliography and first-use notation (editorial gate).** The current working files each contain their own APA references. Assemble a deduplicated global bibliography for the monograph (subject to institutional guidance), audit every in-text citation against it, and prepare the global acronym/symbol list with first-use definitions. Publisher checks during this review confirmed the identity of several core records (Harvey et al., 2025; Giacomini & White, 2006; Cho & White, 2007; Qu & Zhuo, 2021; Stock & Watson, 2007; Odendahl et al., 2023). This was not an independent full-text audit of every cited source. Stock and Watson (2007) has a published erratum concerning some original numerical figures and tables; any future numerical quotation from that paper should be checked against the correction.

**D. Economic-argument depth (doctoral discussion gate).** The empirical conclusions are appropriately bounded, but the discussions of policy relevance and external validity include generic statements that could be made about many forecasting papers. Before final submission, strengthen specific comparisons with the most relevant prior studies (without expanding the literature into unrelated surveys), and trim duplicated limitations rather than restating them across every subsection.

**E. Scientific verification scope (independent-review gate).** Checks against the final release establish faithful reporting of the approved empirical outputs and consistency with the documented model specification. They do not independently prove that every statistical test implementation has the correct finite-sample calibration, that MSAR global likelihood optima exist, or that the results generalize to fresh data. The MSAR optimization limitation remains open; no fit should be presented as a certified global maximum. The Holm figures are supplementary/audit-based multiplicity sensitivity, not part of the original formally approved baseline testing procedure.

## 5. Next acceptance gate

The chapters are credible **substantive working drafts** and no change to their main empirical verdict is indicated by the checks performed. They should become submission candidates only after (1) consistent appendix organization and global bibliography; (2) final paginated manuscript plus figure/equation inspection; (3) a final source-to-claim review of all core literature; and (4) independent methodological scrutiny of sensitive nonlinear estimates and test calibration. Numerical data and research code were not changed during this review.
