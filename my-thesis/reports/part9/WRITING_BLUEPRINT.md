# PART 9 | DISSERTATION WRITING BLUEPRINT

**Project:** Forecasting Macroeconomic Aggregates under Economic Instability: Theory, Nonlinearity, and Policy Implications  
**Version:** 1.1 | 12 November 2026 (expanded dissertation-length instruction)  
**Purpose:** The controlling writing blueprint for the European-style economics monograph. This is a writing plan, not an amendment to the approved methodology and not the dissertation manuscript.  
**Status:** Ready for Part 9 drafting, subject to normal checking of each citation and manuscript statement.

## 0. Source-of-truth lock

Part 9 will use two different, fixed GitHub commits:

1. **Approved structure and methodology, plus final reports:** `charlijomedia-dotcom/academia7`, documentation commit `00564283fe861468f4e67e0a3b77425b260d56f9` on `part8-r1-rescore`. Structure: `my-thesis/approved-specs/part4/`. Methodology: `my-thesis/approved-specs/part5/`. Jury: `my-thesis/approved-specs/part2/`. Interpretations: `my-thesis/reports/part8/final/`.
2. **Numbers, figures, tests and results:** release commit `9817daf91ac4cb4aaa42c2bef5deaff5b674841b` on `part8-corrected-results/final-20261109`, specifically `my-thesis/output/`, with hashes in `my-thesis/release/part8_final/release_inventory.csv`.

The verified release has 465 inventoried files. Its 12 F3.4 figures reflect the authorized F8 presentation correction. The 440 other files unchanged from the approved archive remain unchanged. **Do not quote numerical values from `output/` on the documentation branch, old release branches, draft reports or audit-only sensitivity calculations.**

**Evidence vocabulary:** distinguish an observed outcome, a model estimate, in-sample fit, out-of-sample forecast performance, a formal forecast test, a descriptive ranking, a diagnostic flag, and an audit-only computation. Never convert one into another.

## 1. What this dissertation must answer

**Approved central question (Part 4):** “Under macroeconomic instability, when do nonlinear state-dependent forecasting models provide statistically credible and economically meaningful gains over classical forecasting benchmarks, and when does their additional complexity fail to improve prediction?”

The manuscript must make eight answers easy to find:

1. Which economic problem is studied?
2. Why does the existing literature not settle this question?
3. What is the thesis's bounded contribution?
4. Why were these data and these methods selected?
5. What does the final evidence establish?
6. Which claims survive the specified robustness checks?
7. Which conclusions are U.S.-specific, and what may transfer elsewhere?
8. Why do these results matter for economics and the use of forecasts in policy?

**Boundary:** The thesis assesses forecast credibility and accuracy. It does **not** estimate the causal effects of a forecast error on households, find an optimal policy rule, choose the best fiscal/monetary policy, validate a true real-time nowcast, or prove general model rankings across countries.

**Actual answer to preview, not a promised result:** At the baseline one-step horizon, neither MSAR nor STAR shows statistically established superiority over AR under the approved primary test across the six U.S. targets (C01). The CPI MSAR 12-month finding is nominal and qualified by multiplicity (C02). Fit, forecast quality, numerical credibility, target, horizon, evaluation sample and window length must be kept separate. Failures and negative results are findings, not inconveniences to conceal.

## 2. Writing and page-count contract

**Priority:** a substantive European economics doctoral monograph, not a journal-length article. The user's revised editing target is **120–140 main-body pages**. The body must be comprehensive, self-contained, mathematically precise, empirically defensible and compliant with every jury remark. This is an authorial target, not an asserted Sorbonne regulatory requirement. Front matter, bibliography and appendices are excluded. Do not inflate pages with repetition: use the greater space to deepen original theory, pre-existing evidence, hypothesis logic, methodology justification, contrasts with literature, and empirical interpretation.

| Manuscript component | Editing budget, pages | Scientific job |
|---|---:|---|
| General Introduction | 10–12 | Problem, real-world stakes, gap, bounded contribution, question, design, headline answer |
| Chapter 1 | 24–27 | Theory and prior knowledge lead to a testable unresolved problem |
| Chapter 2 | 28–32 | Complete but efficient empirical contract, equations and justified methods |
| Chapter 3 | 26–30 | Adequacy first, then primary forecast evidence and conditional states |
| Chapter 4 | 26–30 | Challenge the evidence, limitations, credibility and economic implications |
| General Conclusion | 6–9 | Direct qualified answer; no new results |

**Editing test:** every paragraph must define a relevant object, establish an economic mechanism, identify a gap, justify a method, report evidence, assess an alternative explanation, or delimit a claim. Remove paragraphs that do none of these. Tables should replace repetitive prose, but essential test results and model definitions must stay in the body. Each chapter has **one page of concluding synthesis within its budget**, with no new result, study or argument.

**Language:** short, direct, objective sentences; simple grammar accessible to a grade-six reader while retaining correct economics and econometrics terms; no em dashes; no AI filler; no inflated novelty language; no needless repetition; no assumed causal links. Target information density, not arbitrary sentence-length compliance. Use only APA 7 author–date citations and a matched APA reference list. Every citation must support its actual sentence. Prefer original peer-reviewed research in leading journals, authoritative books and primary official data. A Q1 journal rank is a quality screen, not proof of relevance or validity.

**Strict manuscript-facing style separation (author instruction, 13 November 2026):** Thesis chapters are self-contained academic prose. Do not mention GitHub, file paths, commits, pipelines, run IDs, data file extensions, coding workflow, unpublished planning parts (such as Parts 5/8/9), or the private author-assistant revision process in the reader-facing manuscript. Never include repository links in tables, notes, or body passages. Numerical exhibit attributions should read *Source: Author's computations* (add official data institutions when useful); conceptual exhibit attributions may read *Source: Author's construction/synthesis*. In-text references to internal results are expressed only as thesis tables, figures, sections and appendices; external scholarly support is cited using the APA bibliography. Preserve numeric provenance and computational audit references in private evidence maps and technical project documentation, not in the dissertation narrative. Present methodological limitations substantively without telling a software-execution story. Equations must use verified GitHub-compatible `math` blocks for working Markdown, be numbered consecutively, and be professionally typeset in the final manuscript.

## 3. General Introduction | Proposed sequence and writing evidence

**Approved Part 4 job:** Contemporary economic problem, importance of the U.S. case, prior work, gap, contribution, question, falsification conditions, empirical strategy, scope, concise preview, and map of the monograph. Retain the Part 4 introduction rather than creating an extra chapter.

| Paragraph block | Exact purpose and evidence |
|---|---|
| A. Joseph and Pharaoh | Open with the Douay-Rheims *Genesis* 41:25–36 and 41:53–57. The narrative describes the forecast of seven abundant years followed by seven years of famine and the storage and use of grain. Use “an early narrative of forecast-informed public reserves,” **not** “the first historical macroeconomic policy ever implemented.” Do not present the biblical narrative as independent historical proof of a correctly predicted 14-year sequence. The economic lesson is that advance information can support preparation, **not** that a forecast alone guarantees good policy. |
| B. Modern evidence of forecast error | A focused bridge to three verified records: Bernanke's 2024 Bank of England review (one-year-ahead inflation RMSE 0.64 percentage points in 2015–19 versus 4.60 in 2021 Q2–2023 Q3); An, Jalles and Loungani (2018), 63-country recession forecasts; and the OBR's June 2026 evaluation of U.K. 2024–25 borrowing (March 2023 forecast £85bn, observed around £152bn, stated difference £66bn after rounding). Quote dates, horizons and units precisely. |
| C. Economic stakes | Explain how surprise inflation, recessions and interest-rate changes create stakes for wages, budgets, investment and household welfare. Cite separate empirical studies or official evidence for each welfare outcome. **Never claim these harms were caused by forecast errors unless causal evidence exists.** |
| D. Scientific question | Move from the need for better forecasts to unstable relations, breaks, nonlinear states and why added complexity may help or fail. The study assesses forecasting methods rather than choosing policy actions. |
| E. Previously available answers and gap | Summarize AR/ARMA forecast benchmarks; Hamilton's Markov switching; Teräsvirta's smooth transition; conditional predictive ability; window selection; multivariate and nowcasting methods. The gap is a *bounded joint evaluation* for six U.S. macro targets under adequacy, failures and robustness, not the unstudied existence of nonlinear forecasting. |
| F. Contribution and design | State the six targets, the frozen information set, AR/ARMA versus MSAR/STAR, adequacy before performance, primary instability-robust test, regimes/turning points, VAR and robustness. Explain why the United States is an informative case and why this does not imply global generality. |
| G. Verified answer and map | Preview the negative/qualified baseline conclusion from C01/C02 and visible failures without exhaustive numbers. Name the four chapters and the single research chain. |

**Biblical reference rule:** use a specific accessible Douay-Rheims, Challoner-revision edition, verify its title, update/publication year and APA treatment before final text. Record the exact verses. Project Gutenberg's Genesis text: https://www.gutenberg.org/files/8300/8300-h/8300-h.htm. Avoid invented historical priority.

**Contemporary source leads, verified at source-page level:** An et al. (2018), *International Finance*, https://doi.org/10.1111/infi.12130; Bernanke (2024), Bank of England review, https://www.bankofengland.co.uk/independent-evaluation-office/forecasting-for-monetary-policy-making-and-communication-at-the-bank-of-england-a-review/forecasting-for-monetary-policy-making-and-communication-at-the-bank-of-england-a-review; OBR (2026), https://www.gov.uk/government/publications/forecast-evaluation-report-june-2026. These are a **starting evidence set**, not the finished citation library.

## 4. PART I: From Macroeconomic Instability to a Testable Forecasting Problem

### Chapter 1 | Why Macroeconomic Relationships Become Unstable: Fisher, Phillips, Okun and the Forecasting Problem

**Chapter question:** Which economic mechanisms make the selected aggregates policy-relevant, and why can their relations change enough to make them difficult to forecast?

**Approved sections and drafting instructions:**

- **1.1 Forecasting as a policy problem under inflation, conflict, debt pressure, and cyclical instability.** Connect introductory evidence to the U.S. postwar case, official data and its policy relevance. Do not repeat the full Joseph story.
- **1.2 Fisherian relations between inflation, nominal rates, real rates, and expectations.** Show and define the Fisher relation; discuss how changing inflation expectations affect forecasts. Original economic sources and appropriate later literature.
- **1.3 Phillips-Phelps and Okun mechanisms linking inflation, unemployment, and output.** State the key equations, variable definitions and limitations. Explain when stable empirical relations might break.
- **1.4 Money, monetary transmission, and competing macroeconomic traditions.** Link M2, policy rate and price/activity mechanisms to forecast targets, without creating a survey of schools of thought.
- **1.5 Schumpeterian disruption, structural change, and turning points.** Explain why transitions and structural change are relevant to prediction; do not make the latent model state an observed business-cycle state.
- **1.6 From economic instability to statistical state dependence.** Distinguish structural breaks, nonstationarity, thresholds, smooth transitions, latent regimes and asymmetry. Define “nonlinear” precisely (R1-10).
- **1.7 What the theoretical and empirical literature already knows, and what remains unresolved.** Classical, nonlinear, multivariate and mixed-frequency forecasts, including results where simple models match or beat complex models. Identify the precise unresolved comparison rather than claiming novelty for existing models.
- **1.8 Testable implications, competing explanations, and evidence that would contradict the argument.** State how overfitting, a misspecified AR benchmark, a break, omitted cross-variable dynamics or numerical failure could explain apparent gains.
- **1.9 Chapter 1 Concluding Synthesis.** One page only: economic mechanisms, unresolved question, plausible alternatives and why Chapter 2's experiment is necessary.

**Primary jury map:** R1-08, R1-10, R1-19, R1-20, R1-21; P-01, P-06; Verne V-02/V-03/V-05/V-08.

**Literature anchor pool:** Fisher, Phillips, Phelps, Okun and Schumpeter in the approved Part 4; Hamilton (1989); Stock and Watson; Teräsvirta et al. (2005); Giannone, Reichlin and Small (2008); Giacomini and White (2006). Check original editions and exact supporting claims before insertion.

### Chapter 2 | Testing Nonlinear Forecast Value Against Classical Benchmarks: Model Adequacy and Forecast Design

**Chapter question:** How can the thesis test nonlinear predictive value fairly, with transparent information, defensible competitors and observed failures?

- **2.1 From Chapter 1 mechanisms to an empirical identification strategy.** What a comparative pseudo-out-of-sample design can test; no causal policy-effect claim.
- **2.2 Data, aggregate selection, exact samples, and frozen-vintage policy.** Six targets CPIAUCSL, UNRATE, INDPRO, FEDFUNDS, M2SL, GDPC1; USREC ex post for states. Discuss monthly/quarterly frequencies, frozen 5 October 2026 data vintage, targets through August 2026 and 2026 Q2, transformed series and relevant exact samples. State two October 2025 level LOCF replacements in *derived* CPI and unemployment input, not in the untouched downloaded source (T2.0, T2.1, T4.9).
- **2.3 Stationarity, persistence, and structural-break evidence before model specification.** ADF, KPSS, Zivot-Andrews for UNRATE/FEDFUNDS, initial-window decision rule and full-sample corroboration. Distinguish conflicting nulls and failed corroboration; key T2.2 result belongs in the body.
- **2.4 Testing for nonlinearity before nonlinear interpretation.** Tsay and Luukkonen-Saikkonen-Teräsvirta/Teräsvirta tests. State nulls, interpretation and why non-rejection does not automatically bar a predeclared model from forecast testing.
- **2.5 Classical forecasting benchmarks and what each benchmark tests.** AR/BIC and residual screen; ARMA as a stronger alternative. Explain GARCH as variance diagnostic if ARCH-LM warrants it. Explain why polynomial trends are not a baseline point-forecast challenger for the approved transformed targets.
- **2.6 State-dependent alternatives and their economic interpretation.** Define MSAR(2) and STAR with essential equations, latent states, transition matrices, occupancy and LSTAR/ESTAR choice. **Do not include the dropped MSSTAR model or its obsolete proposition.** Do not imply regimes were structurally identified.
- **2.7 Cross-variable information and the boundary of single-equation forecasting.** Monthly five-variable VAR robustness; GDP stays quarterly. Distinguish omitted information from estimated causality.
- **2.8 In-sample model adequacy as a prerequisite for forecast interpretation.** Residual tests; adequate, fragile and failed categories; fit is a gate, never proof of forecast value.
- **2.9 Forecast experiment: origins, windows, horizons, and re-estimation policy.** Fixed monthly 240 / quarterly 120 baseline rolling lengths; h=1 core; longer h and window-length robustness. Selection on the initial window, estimation at every origin, documented warm starts and valid forecast-time information.
- **2.10 Forecast evaluation across normal periods, recessions, expansions, peaks, and troughs.** RMSE, MAE, AR-relative out-of-sample R-squared, HLZ primary, DM-HLN secondary, MCS, Giacomini-White state comparison; matched sample rules; NBER states ex post and ±3 month / ±1 quarter turning windows plus sensitivity. Give decision rules and essential nulls.
- **2.11 Model admissibility and failure rules.** Nonconvergence, unstable AR, low occupancy, transition boundaries, ill-conditioned/singular covariance, extreme forecasts, implausible STAR transition thresholds; do not call operational flags formal significance thresholds. Failed forecasts are retained in the registry but not scored.
- **2.12 Threat-based robustness plan.** Transformation, lag, K=3 full-sample-only check, horizons, window lengths, turning neighborhoods, VAR, conditional variance and missing-data sensitivity. Explain **K=3 workload calculation** below and the difference between in-sample regime credibility and predictive value.
- **2.13 Reproducibility and numerical traceability.** One concise reproducibility paragraph. Distinguish original Part 5 design, the user-authorized amendments and corrections after execution. Mention the essential failure-treatment paragraph below. Put details in appendices; no execution diary.
- **2.14 Chapter 2 Concluding Synthesis.** One page only: fair benchmark, adequacy and failure gate, information-set limits, forecast test and why Chapter 3 can now examine results.

**Primary jury map:** R1-03 to R1-05, R1-08, R1-09, R1-11 to R1-15, R1-17 to R1-20, R1-23; P-01 to P-05; Verne V-04/V-05/V-06/V-08. Essential equations and definitions go in the body; long derivations/optimizer logs in appendices.

**Methods and references:** exact choices are locked in `approved-specs/part5/part5_methodology_specification.md`, the decision log, the K=3 amendment and `part5_methodology_literature_justification.md`. Original methodological sources include Dickey and Fuller; Kwiatkowski et al.; Zivot and Andrews; Tsay; Luukkonen et al.; Teräsvirta; Hamilton; Sims; West; Pesaran and Timmermann; Giacomini and White; Harvey, Leybourne and Zu; Diebold and Mariano; Harvey, Leybourne and Newbold; Hansen, Lunde and Nason; Rossi and Inoue; Giannone, Reichlin and Small. **Each APA record and source-to-claim match is verified before writing.**

**Calculation to print briefly in §2.12:** The 29 October amendment removed 3,527 rolling K=3 origins across six target chains but retained six full-sample K=3 fits. Planned fit calls fall from `3,527 + 6 = 3,533` to `6`, a reduction of `3,527 / 3,533 × 100 = 99.83%`. This is a *count of planned K=3 fits avoided*, **not measured CPU time saved**. The jury sought an in-sample regime-count credibility check, not K=3 rolling forecast accuracy. Report K=3's inconclusive UNRATE numerical limitation in Chapter 4, not as proof that K=2 is structurally correct.

**Concise execution-disclosure paragraph, working text:** “The empirical method was defined before the final estimation. Approved amendments addressed the frozen missing observations, estimation-window sensitivity and the scope of the three-regime check. During execution, forecasts from failed fits were removed from accuracy scores but kept in the audit files. Numerical safeguards completed Model Confidence Set calculations without changing the approved test. Incorrect test signs, missing diagnostics and transformation labels were corrected. Extreme STAR forecasts remained in separate figure panels. MSAR estimates remained sensitive to optimization, and the unemployment three-regime comparison was inconclusive. Appendix B records the corrections and the validation evidence.” This is *draft narrative* and must be cross-checked against the final reports. No additional source-level line-by-line code review is required.

## 5. PART II: Testing the Forecast Value of Nonlinear State Dependence

### Chapter 3 | From Model Adequacy to Forecast Performance: Evidence Across Expansions, Recessions, Peaks and Troughs

**Chapter question:** When models pass the allowed interpretation tests, do nonlinear models produce better forecasts, especially in economically unstable states?

- **3.1 Pre-estimation evidence and model eligibility.** Table T2.2 and nonlinearity diagnostics. Just enough to judge how models enter the analysis; do not repeat Chapter 2's derivations.
- **3.2 In-sample model adequacy and residual diagnostics.** T3.1; what adequate, fragile and failed mean before discussing accuracy. This answers Verne's fit-first remark.
- **3.3 Regime and parameter credibility for nonlinear models.** T3.2 and regime-probability figures. Near-absorbing/empty states and optimization cautions are evidence, not inconvenient exceptions.
- **3.4 Full-sample out-of-sample forecast performance against classical benchmarks.** T3.3, T3.3A (HLZ), T3.3B (secondary), T3.4 (MCS), and F3.4. Separate own-valid-date RMSE, AR-matched OOS R-squared and any all-four-common-date audit. **C01, C02, C03, C08, C21** govern interpretation.
- **3.5 Forecast performance in expansions and recessions.** State-specific RMSE/MAE, T3.5 regression. Do not interpret a joint Wald rejection as state dependence if the state-slope test is not significant (UNRATE ARMA-vs-AR, joint p=.034; state-slope p=.282).
- **3.6 Peaks, troughs, and turning-point forecasting.** T3.6 and predeclared turning windows; distinguish ex post classification from real-time turning-point forecasting.
- **3.7 Cross-aggregate synthesis.** Compare the six targets by economic function rather than repeating six mini-papers.
- **3.8 What baseline evidence establishes, and what remains vulnerable.** A short claim/qualification table. Baseline h=1 has no general HLZ-supported nonlinear-over-AR gain; isolated h=12 CPI result requires qualification; STAR extremes and sample dependence remain visible.
- **3.9 Chapter 3 Concluding Synthesis.** One page: baseline answer, significance versus descriptive ranks, failures and questions that Chapter 4 must challenge. No new evidence.

**Primary jury map:** R1-06, R1-09, R1-15, R1-17, R1-18, R1-22, P-03; Verne V-05/V-06/V-08.

**Main text display budget:** prioritize a compact adequacy table, a compact main forecast/inference table, one interpretable figure, and a concise states/turning-points exhibit. Full per-series and per-origin data remain in Appendix A and the immutable release.

### Chapter 4 | Do Nonlinear Forecast Gains Survive? Specification Robustness, Cross-Variable Dynamics and Policy Relevance

**Chapter question:** Which apparent forecast gains survive credible alternatives, and what policy-related interpretation is justified?

Each robustness subsection follows **baseline claim → threat → approved check → finding → consequence**.

- **4.1 From baseline result to falsification test.** Short map of threats; no new methodological theory.
- **4.2 Transformation, persistence, and structural-break threats.** T4.1; UNRATE/FEDFUNDS unit-root and break-test disagreement; alternative transformations and T4.9 missing-input sensitivity. Tie back to P-02/P-03.
- **4.3 Lag structure, seasonality, and classical-benchmark misspecification.** T4.2 CPI AR(1/3/6/12) versus BIC-selected AR(2), and T4.6 conditional variance where relevant. **C16 remains QUALIFIED:** no direct AR(2)-versus-AR(12) significance or equivalence test.
- **4.4 Two regimes or more?** T4.3, F4.3, K=3 credibility flags. K=3 is **in-sample only**. UNRATE comparison is **INCONCLUSIVE** because an obtained K=3 local optimum has likelihood below K=2 despite nesting; P-04 remains partially addressed. State why K=2 was predeclared, not why it is proved universally best.
- **4.5 Does model ranking change with the horizon?** T4.4; the isolated CPI MSAR h=12 result and the multiple-testing caveat. Do not present audit-only Holm calculations as predeclared primary inference.
- **4.6 Does cross-variable information explain apparent gains?** T4.5 monthly VAR; discuss predictive-information omission, not causality. GDP is not interpolated into a monthly series.
- **4.7 Model fragility as evidence.** T4.7 failure/status tables, F1/F2/B2 corrections, STAR forecast degeneracy and MSAR optimizer uncertainty. Focus on consequence for model credibility, not a programming chronology.
- **4.8 What nowcasting and mixed-frequency methods could answer.** Explicitly outside the empirical core; no false claim to true real-time nowcasting.
- **4.9 What the robust evidence means for policy.** Better evaluation discipline can inform how forecasters select, test and monitor models. No claim that one model caused a better policy or that forecast accuracy alone determines policy success.
- **4.10 U.S.-specific versus transferable elements.** U.S. rankings and period dependence are not international evidence; methods for credible evaluation may transfer (C23).
- **4.11 Chapter 4 Concluding Synthesis.** One page: classify surviving, weakened and unsupported claims, state generalizability and policy scope, and hand off the final answer to the General Conclusion.

**Primary jury map:** R1-06, R1-07, R1-14, R1-15, R1-17, R1-19, R1-20, R1-22; P-01 to P-06; Verne V-03 to V-08.

**Main-text display budget:** a single threat-by-threat table; a selective, clearly labelled regime diagnostic; one visual or table showing the most consequential fragility; a short cross-variable comparison. Leave the complete 34,122-event T4.7 registry outside the body. The registry contains **512 FAILED reason-code events and 33,610 FRAGILE reason-code events across 17 category/reason combinations**, **not** 34,122 distinct failed fits.

## 6. General Conclusion | One integrated answer

Follow Part 4's title: *What Nonlinear Forecasting Can and Cannot Contribute to Macroeconomic Policy Under Instability*.

In roughly 6–9 pages, answer the eight research questions without new data, citations that introduce new arguments, models or tests. State the measured absence of systematic nonlinear forecast superiority, isolated conditional gains, estimation weaknesses, limitations of U.S. historical pseudo-OOS evidence, and the value of failure-aware forecasting discipline. This dissertation offers a **credible evaluation and bounded findings**, not a universal cure for forecasting error.

## 7. Appendices | Compact, referenced and outside body page budget

- **Appendix A. Data, auxiliary estimation results and robustness tables.** Exact variable definitions, transformations, data dates, key diagnostic tables, supplementary regime parameters and forecasts. Refer to each appendix table where relevant rather than reproducing raw dumps.
- **Appendix B. Estimation failures, approved changes and corrections.** A compact classification and disposition table: problem; scope/series; Part 5 rule; observed failure; action; approval/effect; source. Group **approved methodology amendments**, **implemented numerical safeguards**, **post-run corrections**, and **unresolved limits** separately. Include F1 failed forecasts, F2 MCS safeguards, F3 test orientation, F4 omitted Zivot-Andrews reporting, F7.1 transformation labels, F8 figure scaling, B2 optimizer sensitivity, F6 non-global optimum, LOCF/T4.9. Do not present this as an execution diary.
- **Appendix C. Computational workload and reproducibility.** A table with actual attempted/valid/fragile/failed fits by target/model; origin counts and frequencies; measured runtime, hardware and software environment if recorded; caching/checkpointing; numeric burden; the **3,527 K=3 rolling-origin fit calls avoided**; exact scientific source and release commits, manifest hash and independent verification. Clearly separate *planned fits*, *executed fits*, *flagged reason-code events* and *measured CPU hours*. Do not invent a total CPU-hour figure where only estimates are available.
- **Appendix D. Supplementary mathematical and literature detail (only if needed).** Derivations and ancillary comparisons that actually support retained AR/ARMA, MSAR, STAR and VAR models. Exclude the obsolete MSSTAR proposition and proof unless an independently necessary point survives and is explicitly attributed. The core model equations, Markov-chain definitions, test hypotheses and parameter interpretation stay in the body because R1-05/R1-08/R1-11 require self-containment.

## 8. Jury acceptance gates for Part 9

**Before accepting a draft chapter**, cross-check the entire Part 2 registry, but track particularly:

| Requirement | Where it must be visibly satisfied |
|---|---|
| R1-02/03/04 | Correct language, notation, acronyms and symbol list; chapter-wide consistency |
| R1-05 | No unattributed theorem or obsolete MSSTAR proposition; essential mathematical results retained in body |
| R1-08/10/11 | Fisher relation, definitions of nonlinearity, Markov chains, probabilities and transition matrices |
| R1-09/13/14/16 | Forecast ‘better’ criterion, null hypotheses, correct p-value/test orientation and significance style |
| R1-06/07/17 | Accurate, unclipped figures, uncertainty where applicable, and credible regime interpretation |
| R1-12/15/23, P-02/P-03 | Variables/M2, CPI lags, policy rate, unemployment stationarity and structural-break caveats |
| R1-18/19/20 | Nonlinearity diagnostics, VAR and nowcasting/mixed-frequency boundary |
| R1-21/22 | Light theory, essential evidence in body, complete verification and visible adverse results |
| P-01/P-04/P-05/P-06 | Univariate limit, K=3 check and its inconclusiveness, multiple horizons, and external validity |
| Verne V-01 to V-08 | Two Parts, two substantive chapters each; policy relevance; fit first; turning points; clear conclusion and meaningful titles |

**Part 8 jury state on entry to Part 9:** 16 resolved, 2 partially addressed (R1-11 textual portion; P-04/F6), 11 outside empirical scope. These are **not** 11 already satisfied Part 9 writing requirements; they must be addressed in the manuscript.

## 9. Citation and evidence-control procedure

Before drafting each section, maintain one record per statement requiring support:

`claim → chapter/section → exact source and page/verse/table → source type → APA author/date → DOI or official URL → verified support → wording limitation`.

For methods, first consult the approved Part 5 literature-justification file; verify every bibliographic field and whether the cited work actually supports the precise choice. Some exact operating choices (e.g., 240-month baseline, ±3-month turning window, a numerical occupancy flag) are declared **design conventions**, not universally established academic constants. For published data numbers, consult the release commit plus its inventory and final Part 8 report. For quotations use precise APA locators. Never manufacture citations, impact factors, journal quartiles, page numbers or causal findings.

**Initial reference targets to verify and use selectively:** Hamilton (1989); Teräsvirta (1994); Teräsvirta, van Dijk and Medeiros (2005); Giacomini and White (2006); West (1996); Sims (1980); Hansen, Lunde and Nason (2011); Rossi and Inoue (2012); Harvey, Leybourne and Zu (2025); An, Jalles and Loungani (2018); Bernanke (2024 Bank of England review); OBR (2026). A bibliography is assembled **only from sources actually cited in the written dissertation**.

## 10. Writing workflow and next concrete action

1. **Blueprint established (this file).** It controls the chapter organization and writing standards. Do not ask Claude Code to write Part 9; the approved project instructions assign that task to ChatGPT.
2. **Next deliverable: the General Introduction evidence sheet.** Verify the precise Douay-Rheims edition/APA reference, 2–3 official or peer-reviewed modern forecast-error examples and their limits, the welfare evidence, earlier literature and the permitted main Part 8 claims. Mark each proposed sentence as sourced, qualified or unsupported. No additional modelling or broad code review.
3. **Revise General Introduction v2** (target 10–12 pages), starting with Joseph; tight transition to forecasting mistakes and real stakes; exact question; U.S. choice; existing answers and gap; bounded contribution; preview of the verified negative/conditional results; chapter map. Audit for every jury concern and factual citation before moving on.
4. **Draft Chapter 1** from the approved 1.1–1.9 structure, then Chapter 2 from 2.1–2.14, inserting the brief methodology-amendment/failure paragraph and K=3 calculation.
5. **Draft Chapter 3 and Chapter 4** with exact referenced figures, tables and formal inferential limits. Draft each appendix only when its body citation requires it, avoiding duplication.
6. **Write the General Conclusion last.** Validate the eight answers, jury matrix, APA bibliography, exact data hashes and body page count. Run a compression pass on the complete manuscript.

**Control gate for every new written section:** (a) faithful to Part 4; (b) allowed by Part 5; (c) numbers/claims verified against Part 8; (d) jury remark addressed; (e) APA references checked; (f) simplest possible wording without sacrificing meaning; (g) no repeated content.

---

**Part 9 revision (12 November 2026):** The author rejected the shorter 55–65-page editing budget in favor of 120–140 body pages, to give doctoral-level depth and address jury concerns about a paper-like manuscript. Preserve exact Part 4 structure, four one-page chapter conclusions, empirical source locks and all scientific limits. General Introduction v1 remains an archive; write and review v2 before Chapter 1. No new Colab execution or empirical re-estimation is required.