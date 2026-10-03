# Part 3: Gap map versus jury remarks

**Date:** 3 October 2026  
**Status:** PROPOSED FOR USER APPROVAL  
**Sources:**  
- `CHARLIJO TANNOURY PHD THESIS May 2026.pdf`  
- Part 2 jury registry (`R1-*`, `P-*`)

**Purpose:** Determine, for each jury issue, what the current thesis already contains and what remains unresolved. This file diagnoses gaps. It does not choose the final Part 4/5 solution.

## Status labels

- **ADDRESSED** = the current thesis materially answers the remark.
- **PARTIAL** = the current thesis contains relevant material, but the jury concern is not fully resolved.
- **OPEN** = the concern remains substantively unresolved.
- **PRESENTATION** = mainly a final-writing/formatting correction rather than a new empirical design.

---

| Jury ID | Current thesis evidence | Status | What remains for Parts 4–5 / Part 9 |
|---|---|---|---|
| R1-01 | Thesis is a two-part monograph with four chapters, not research-paper blocks. It has clearer functional chapters than the reviewer's summary suggests. | PARTIAL | Part 4 must decide whether to preserve monograph form while making each chapter function more research-like and compact. |
| R1-02 | Typographical/notation issues remain, including implementation names and malformed strings such as `d=1d = 1d=1`. | PRESENTATION | Full notation/typography audit in Part 9. |
| R1-03 | No front-matter list of abbreviations was found. Acronyms are sometimes defined locally or in footnotes. | OPEN | Add controlled abbreviation list and first-use definitions. |
| R1-04 | Many symbols are defined locally in Chapter 3, but there is no global symbol list and multiple notation styles remain. | PARTIAL | Standardize global notation before Part 9. |
| R1-05 | Appendix A contains “Theorem A.1” and a proof, but authorship/status is not clearly declared. | OPEN | Part 4/9 must label the result accurately, possibly as author-derived proposition if that is what it is. |
| R1-06 | Chapter 4 discusses fragile model forecasts and C4_9, but no explicit visual-failure rule exists. | PARTIAL | Part 5 must define figure handling for explosive/failed forecasts. |
| R1-07 | Oil cross-correlation figure is used, but no explicit confidence-band statement appears in the figure note. | OPEN | Part 5 must require uncertainty bands if cross-correlation remains. |
| R1-08 | Core econometric models are formally defined in Chapter 3, but Chapter 1's Fisher/Phillips/Okun discussion remains largely verbal. | PARTIAL | Part 4 should shorten general theory and add the few essential equations directly in the theoretical argument. |
| R1-09 | Current thesis now distinguishes fit, RMSE/MAE, DM, CPA, and state-specific ranking. | ADDRESSED/PARTIAL | Part 9 must keep comparison criteria explicit every time “better” is used. |
| R1-10 | Chapter 2 distinguishes thresholds, STAR, and Markov switching and discusses different types of state dependence. | PARTIAL | Part 4 should turn this into a concise taxonomy and state what forms the empirical models do not cover. |
| R1-11 | Chapter 3.5 now defines a first-order Markov chain, transition matrix, stationary probabilities, filtering, and expected duration. | SUBSTANTIALLY ADDRESSED | Simplify and standardize rather than rebuild. |
| R1-12 | Variables and transforms are defined in Chapter 3.1. FEDFUNDS and M2SL are named; YAML is footnoted. Economic justification is given. | PARTIAL | Still verify policy-rate proxy choice, correct M2 terminology, and make dates/measurement clearer. |
| R1-13 | Ljung-Box, ARCH-LM, and Jarque-Bera formulas and purposes are shown. | PARTIAL | Add standardized H0, null distribution/reference, rejection rule, and interpretation. |
| R1-14 | Thesis uses DM plus Giacomini-White-type CPA. It does not use Clark-McCracken or Amisano-Giacomini. | PARTIAL | Part 5 must decide which modern comparison tests fit the final design. |
| R1-15 | CPI lag is selected through AIC + residual diagnostic and can reach p=12. The final CPI AR uses p=12. | OPEN | Need focused lag robustness and interpretation. |
| R1-16 | Stars are used and defined in Chapter 4. | PRESENTATION | Standardize superscript/table convention in Part 9. |
| R1-17 | Thesis explicitly displays suspicious transition matrices, including GDP p00≈0 and policy-rate near-absorbing probabilities. | PARTIAL | Need reproducibility/convergence/regime-occupancy diagnostics and predeclared credibility rules. |
| R1-18 | A Luukkonen-Saikkonen-Teräsvirta auxiliary linearity test is used in Chapter 3.6 for STAR delay/type selection. | PARTIAL | Elevate results visibly and define how they affect model eligibility; determine how MSAR is justified. |
| R1-19 | Main design is still single-equation. Oil adds one exogenous regressor but is explicitly not a VAR. | OPEN | Part 4/5 must make a substantive multivariate response. |
| R1-20 | No nowcasting section or implementation was found. Preserving native frequencies is not nowcasting. | OPEN | Part 4/5 must explicitly address nowcasting/mixed-frequency scope. |
| R1-21 | Theory remains extensive; essential methodology is formalized in Chapter 3; many decisive tables remain in appendices. | PARTIAL | Part 4 must compress theory and move only essential evidence into the main text. |
| R1-22 | Thesis openly discusses fragility and model failure. | PARTIAL | Final results must be fully regenerated under the revised methodology and frozen data. |
| R1-23 | Thesis identifies M2SL and explains log-growth, but does not prominently resolve the reviewer's apparent 1992 sample concern with an explicit raw/usable date table. | OPEN | Verify raw and transformed dates and explain them in the main data section. |
| P-01 | Chapter 3.12 and conclusion explicitly acknowledge the single-equation limitation and inability to model joint feedbacks. | PARTIAL | Recognition is present, but Part 4/5 must decide whether to add a focused multivariate block rather than leave it only as a limitation. |
| P-02 | Unemployment and policy rate remain in levels based mainly on economic interpretability. No formal full-sample unit-root block with a structural-break test was found. | OPEN | Mandatory methodological response in Part 5. |
| P-03 | Extreme policy-rate MSAR result is displayed and called degenerate/unusable. | PARTIAL | Need to distinguish model inadequacy from transformation/estimation failure after stationarity analysis. |
| P-04 | Baseline uses K=2 only. No K=3 robustness result is reported. | OPEN | Mandatory K=3 robustness attempt in Part 5/6–8. |
| P-05 | Core application remains h=1. The conclusion acknowledges longer horizons as future research. | PARTIAL/OPEN | At minimum delimit h=1; Part 5 decides whether to add longer horizons now. |
| P-06 | Conclusion explicitly says the U.S. ranking is not universal and discusses smaller open/high-inflation economies. | SUBSTANTIALLY ADDRESSED | Final manuscript should keep the empirical ranking sample-specific and describe only the design as potentially transferable. |

---

## 2. High-priority unresolved empirical gaps

The most consequential open items before Claude Code can build the new final pipeline are:

1. **Stationarity and transformation of unemployment and policy rate**  
   Related IDs: P-02, P-03.

2. **Policy-rate nonlinear degeneracy**  
   Related IDs: R1-17, R1-22, P-03.

3. **Three-regime robustness**  
   Related ID: P-04.

4. **CPI lag-order robustness**  
   Related ID: R1-15.

5. **Nonlinearity evidence as a formal model-selection input**  
   Related ID: R1-18.

6. **Modern forecast-comparison design**  
   Related ID: R1-14.

7. **Multivariate response to cross-variable theory**  
   Related IDs: R1-19, P-01.

8. **Nowcasting/mixed-frequency scope**  
   Related ID: R1-20.

9. **M2 sample-date clarification and terminology**  
   Related IDs: R1-12, R1-23.

10. **One-step horizon limitation**  
    Related ID: P-05.

11. **Predeclared failure/fragility rules**  
    Related IDs: R1-06, R1-17, R1-22, P-03.

12. **Frozen dataset**  
    Project safeguard adopted after review of the submitted thesis.

---

## 3. High-priority structural gaps

Part 4 must particularly resolve:

- how much of Chapters 1 and 2 is genuinely needed;
- where the core Fisher/Phillips/Okun equations should appear;
- how to make the univariate limitation and any multivariate response visible in the table of contents;
- how to bring stationarity, diagnostics, and critical robustness into the main text;
- how to separate scientific methodology from code/configuration documentation;
- how to make the chapter sequence resemble the Part 1 benchmark logic:
  problem → question → necessary mechanisms → design → evidence → robustness → qualified interpretation.

---

## 4. What can be retained with relatively little conceptual change

The following parts of the current thesis are strong enough to serve as building blocks:

- the central research question, after wording is tightened;
- AR as the disciplined benchmark;
- rolling fixed-window pseudo-out-of-sample evaluation;
- target-date recession/turning-point classification;
- RMSE/MAE/OOS-R² reporting;
- explicit comparison of successful and failed nonlinear models;
- Markov transition-matrix interpretation;
- Luukkonen-Saikkonen-Teräsvirta STAR linearity scan, subject to stronger reporting;
- conditional predictive ability logic, subject to Part 5 verification;
- oil application as a practical single-equation extension, if it retains a clear role;
- explicit external-validity and single-equation limitations.

---

## 5. What should not be carried forward automatically

The following current choices should be treated as provisional until Part 5:

- level unemployment;
- level policy rate;
- p=12 CPI;
- K=2 as the only regime count;
- h=1 as the only forecast horizon;
- the current exact MSAR fallback behavior;
- current exact MSSTAR selection rule;
- current open-ended online data endpoint;
- M2 inclusion and terminology;
- current forecast-comparison test set;
- all current numerical model rankings.

Part 3 records these as the current design, not as approved final design.

---

## 6. Part 3 handoff to Part 4 and Part 5

Part 4 should now redesign the thesis so that every major chapter has a direct purpose and every major jury issue has a visible home.

Part 5 should then make the empirical decisions needed to close the open gaps before Claude Code implements anything.

The final design should preserve the current thesis's strongest idea: **nonlinear complexity is a hypothesis to be tested against a disciplined benchmark, not a result to be assumed.**
