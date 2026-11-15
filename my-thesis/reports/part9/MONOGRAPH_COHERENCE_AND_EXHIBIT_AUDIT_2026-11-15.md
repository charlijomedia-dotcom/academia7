# Monograph-wide coherence, evidence and prose audit

**Date:** 15 November 2026  
**Working branch:** `part9-thesis-writing`  
**Scope:** General Introduction v2; Chapters 1, 2, 3 and 4; General Conclusion; Appendices A–D. The separate front-matter abbreviation register and consolidated monograph bibliography were also consulted.  
**Empirical release controlling numerical evidence:** Part 8 final commit `9817daf91ac4cb4aaa42c2bef5deaff5b674841b`.  
**Document status:** Scientific and editorial working-draft review. No single paginated examination PDF or Word manuscript has been compiled or proofed.

## 1. Reading the dissertation as one argument

The General Introduction motivates the economic value of forecasting under uncertainty, introduces the classical-versus-nonlinear research question and declares the historical information set. Chapter 1 explains the economic mechanisms that could change forecast relationships: Fisherian expectations, Phillips–Phelps inflation dynamics, Okun's activity–employment relation, monetary transmission, innovation, structural change and business-cycle timing. These mechanisms motivate statistical alternatives; their causal interpretation is distinguished from the reduced-form forecasts.

Chapter 2 operationalizes the question using fixed data transformations, benchmark selection, initial-window diagnostics, two-state MSAR and STAR specifications, a five-variable monthly VAR robustness design, rolling estimation, matched forecast dates and the declared primary HLZ test. Chapter 3 reports screening, adequacy, regime identification, fitted numerical examples, one-step forecast losses and retrospective business-cycle comparisons. Chapter 4 challenges the baseline through transformations, lags, state count, horizons, multivariate information, variance specifications, windows, numerical instability and information-set limitations. The General Conclusion integrates the statistical findings and identifies their economic implications and future research boundaries.

**Continuity verdict:** The sequence from economic theory to forecasting design to observed evidence and robustness to qualified economic implications is coherent. The revised prose strengthens these transitions by replacing repetitive formulaic oppositions with direct affirmative exposition. Negative sentences that express scientifically necessary findings, null-hypothesis non-rejections, design restrictions or unresolved identification problems remain explicit.

## 2. Research findings and economic interpretation

- **One-step forecast comparison:** The primary HLZ comparisons do not establish statistically supported MSAR or STAR superiority over AR for any of the six U.S. targets. This is a failure to establish gains under specified testing procedures, **not** a statistical equivalence finding.
- **Economic versus statistical nonlinearity:** Fisher, Phillips–Phelps, Okun and monetary mechanisms establish economic reasons for possible instability. Estimated regimes and STAR transitions describe features of fitted conditional distributions and require independent evidence for structural or recession interpretations.
- **Full-sample fit versus prediction:** Lower MSAR or STAR BIC values describe reported penalized in-sample fit. Effective sample lengths differ in some model comparisons. Stronger in-sample fit does not substitute for paired forecast-loss inference.
- **Two-state CPI description:** The approximate 2.563 and 12.494 annualized monthly inflation-mean estimates, 8.6% high-state occupancy and approximately 6.28-month high-state expected duration describe a comparatively interpretable fitted inflation process. Residual autocorrelation remains, while one-step AR and MSAR forecast RMSEs are nearly identical.
- **Real activity:** GDP and industrial production have meaningful descriptive MSAR reductions in sample mean squared error, but no significant general primary one-step gain; rare states and observations during the pandemic challenge the durability of their economic interpretation.
- **Unemployment:** Own-valid and common-date performance differ; a missing May 2020 AR forecast affects raw rankings. The K=3 unemployment likelihood is inferior to K=2 despite the larger specification, which signals unreliable optimization rather than selecting a true regime count.
- **STAR numerical behavior:** Extreme finite CPI and industrial production predictions remain scored. Their affected squared-loss testing statistics can be numerically degenerate; these are treated as uninformative formal comparisons, with extreme behavior visible in figures.
- **Horizon qualification:** Monthly CPI's 12-month-ahead target is the annualized monthly change observed at a later date. The nominal MSAR comparison is favorable at that horizon; supplementary family-wise multiplicity sensitivity does not retain significance.
- **Multivariate scope:** The specified five-variable monthly VAR checks whether lagged cross-variable information changes point forecasting. Its coefficients and forecast rankings identify neither monetary-policy shocks nor nonlinear multivariate economic mechanisms.
- **Information set and data:** The chosen frozen 5 October 2026 historical vintage supports pseudo-out-of-sample comparison. October 2025 LOCF values are constructed research inputs; they are disclosed in Chapter 2, §2.2. The pre-gap sensitivity is a calendar restriction and does not isolate the causal contribution of imputation. Alternative imputation procedures remain beyond scope.
- **Global optimization:** **No global MSAR likelihood optimum has been certified.** Convergence and multiple starting values leave unresolved local-solution sensitivity; no manuscript sentence may recast that limitation as solved.

## 3. Exhibit existence, content and cross-reference validation

| Item | Present and checked | Validation |
|---|---:|---|
| Numbered displayed equations | **39** | Sequential Chapters 1–4; equation references resolve, math display braces and nested environments structurally checked |
| Numbered tables | **47** | Chapter 2: 5; Chapter 3: 9; Chapter 4: 7; Appendix A: 4; B: 7; C: 10; D: 5 |
| Embedded figures | **5** | Three main-chapter figures plus Appendices A and C; all five relative asset paths resolve in the writing branch and the image content was visually inspected |
| Explicitly detected numbered cross-references | **86** | No unresolved equation, figure, table or section identifier in the current ten manuscript files |
| Consolidated cited-work entries | **66** | Exact deduplication of 152 chapter-level bibliography entries into one alphabetically ordered working reference list; 86 repeated entries removed |

**Numerical content cross-check:** Cross-table comparisons covered the central in-sample BICs, baseline forecast RMSEs and valid sample counts, recession/expansion RMSEs, pre-estimation nonlinearity tests, CPI and K=3 regime parameters, primary loss-test p-values, ex-post state-slope tests, turning-neighborhood errors, lag-order alternatives, horizon effects, VAR common-date results, and classified fit counts. In successive checking passes, approximately **406 numerical-cell comparisons** were evaluated, with deliberate overlap where the same measure appeared in multiple exhibits. Apparent parser discrepancies were traced to scientific notation and an initial automatic column-position mapping; the corrected comparisons revealed no genuine inconsistent number at the stated table precision. This is a manuscript/output consistency check rather than a fresh rerun of estimation.

**Figure-to-claim check:** Figure 3.1 shows retrospectively smoothed CPI two-state probabilities. Figure 3.2 displays unemployment forecasts and isolated failed or extreme observations on a separate panel, with the failed AR observation expressly unscored. Figure 4.1 separates the ordinary-scale CPI forecast curves from numerically extreme STAR predictions on a labeled diagnostic scale. Figure A.1 shows the CPI level, constructed October 2025 input marker and annualized monthly inflation rate. Figure C.1 shows the fragile, near-degenerate three-state unemployment probabilities and warns that the state assignments are historically smoothed.

**Material citation error corrected:** Appendix C, Table C.8 formerly cited Appendix A, Table A.2 as the location of imputed October 2025 values. Removal of the earlier imputation appendix section changed Table A.2 into a stationarity-diagnostics exhibit. The caption now cites **Chapter 2, Section 2.2**, where the two constructed values and LOCF rationale actually appear. No stale missing-data reference to A.2 remains in the checked manuscript.

**Misleading numerical presentation corrected:** Appendix B, Table B.2 originally printed the M2 state-1 implied duration as `1000000000000.00` periods. It now reports **at least `10^{12}` periods, numerical cap**, together with the implemented truncation of the duration denominator at `10^{-12}`. This makes near-absorbing numerical behavior evident without implying an economically measured trillion-month cycle.

## 4. Prose quality, repetition and document architecture

Targeted sentence and paragraph revisions were applied across the General Introduction, all four chapters, General Conclusion and Appendices A–D. The editing priority was to make propositions affirmative and precise, favoring economic meaning and observed evidence over rhetorical disclaimers. Examples include:

- Describing annualized log growth directly as the one-period continuously compounded growth rate in annualized percentage units.
- Explaining the measurement role of CPI, industrial production, M2 and FEDFUNDS affirmatively in Appendix A.
- Reframing Chapter 2's model-family comparison table as **Interpretive scope** instead of a repetitive catalogue of what each model fails to identify.
- Recasting Chapter 3's findings table to report the **Condition on interpretation** of each empirical claim.
- Confining the general conclusion to integrated economic meaning and bounded findings instead of repeated strings of argumentative negatives.

A cross-chapter near-duplication pass found four related narrative paragraph pairs after removing the formerly repeated reference lists. These involve the necessary recap of the six variables and the declared stationarity choices at the openings of the relevant chapters, plus continuity between diagnostics and robustness. The repetition remains justified insofar as each chapter introduces a different inferential task. No extensive duplicated exposition survived the automated near-paragraph comparison.

The consolidated working bibliography is at `my-thesis/reports/part9/REFERENCES_CONSOLIDATED_DRAFT.md`. The original five chapter-level reference lists were removed, and the single list should be placed after the General Conclusion and before the appendices in the final monograph. It retains the original source metadata; **independent source-by-source bibliographic verification and final APA7 styling remain distinct production checks**.

## 5. Final scope and production limitations

This is a comprehensive **source-manuscript and supporting-output audit** of approximately 77,700 words of introduction, chapter, conclusion and appendix text. The checks combine close contextual reading, targeted substantive editing, automated numbering and syntax validation, numerical cross-table consistency, examination of five actual figures, and citation-path verification. They do **not** certify every typographic glyph or citation in an unassembled PDF; neither every external source's independent bibliographic accuracy nor the global optimum of a hidden-state likelihood has been newly verified.

Final deposition still requires assembling the correct current versions of all chapters, incorporating the consolidated bibliography and front matter, applying academic typesetting, and inspecting the rendered equations, captions, tables, figures, source citations and page-break consistency. An independent rerun with additional MSAR global-search controls would be a separate scientific exercise; the existing dissertation explicitly documents the limitation in its absence.

**Result:** The scientific argument and exhibit references have been checked as one monograph, substantive cross-reference/presentation errors identified here have been corrected, and the prose has been tightened while retaining the qualifications required for a defensible econometric thesis.
