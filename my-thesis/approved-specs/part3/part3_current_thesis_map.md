# Part 3: Current thesis map

**Date:** 3 October 2026  
**Status:** APPROVED
**Source:** `CHARLIJO TANNOURY PHD THESIS May 2026.pdf`  
**Purpose:** Describe what the submitted thesis actually does before Parts 4 and 5 redesign its structure and methodology.

## 1. Thesis identity

**Title:** *Forecasting Macroeconomic Aggregates under Economic Instability: Theory, Nonlinearity, and Policy Implications*

The submitted manuscript is a coherent monograph rather than a three-paper dissertation. Its central research question is stated in the introduction:

> whether nonlinear state-dependent models, compared with a carefully specified autoregressive benchmark evaluated under the same rolling forecasting conditions, improve the prediction and economic interpretation of major U.S. macroeconomic aggregates during unstable periods, recessions, expansions, and turning-point episodes.

The manuscript therefore places the substantive economic problem first: macroeconomic forecasting becomes harder when the economy is unstable and state dependent. Nonlinear models are treated as candidate representations of that instability rather than as an end in themselves.

**Main source location:** PDF pp. 17–21.

---

## 2. Current argument of the thesis

The argument proceeds in five broad moves:

1. Major macroeconomic aggregates matter because they are central to economic theory and policy.
2. Instability, asymmetry, structural change, and regime dependence can make globally linear representations unreliable.
3. A disciplined empirical comparison should begin with a linear AR benchmark and then add discrete and hybrid nonlinear structures.
4. The models should be compared under common rolling forecasting rules and evaluated both globally and across recessions, expansions, and turning points.
5. The empirical conclusion should be selective rather than universal: nonlinear complexity is useful only when it produces stable and interpretable gains relative to the benchmark.

The submitted thesis does not argue that nonlinear models must dominate. It repeatedly states that richer models have to “earn” their complexity through empirical performance.

**Main source locations:** PDF pp. 17–21, 66–71, 138–163, 169–180.

---

## 3. Current table-of-contents architecture

### General Introduction
**PDF pp. 11–22**

Function:
- motivate forecasting as a policy problem;
- frame instability as the central forecasting difficulty;
- connect theory to forecasting;
- state the main research question;
- explain the benchmark-centered empirical strategy;
- preview the two-part structure.

The introduction is substantial and argumentative. It begins with a historical forecasting-policy analogy, then moves to modern macroeconomic forecasting, instability, policy timing, theory, and the research question.

### Part I: Theoretical Foundations of Macroeconomic Forecasting
**PDF pp. 23–71**

#### Chapter 1. Macroeconomic Aggregates, Theory, and Policy Anticipation
**PDF pp. 25–41**

Current sections:
- 1.1 Macroeconomic aggregates as central objects of economic analysis
- 1.2 Money, inflation, and interest rates
- 1.3 Output, unemployment, and cyclical adjustment
- 1.4 Innovation and macroeconomic turning points
- 1.5 Keynesian, Monetarist, and Neoclassical perspectives
- 1.6 Why forecasting aggregates is indispensable for policy
- 1.7 From theoretical relationships to empirical forecasting problems

Function:
- justify the economic relevance of the six aggregates;
- connect inflation, rates, money, output, and unemployment to Fisher, Friedman, Phillips/Phelps, Okun, Keynesian, monetarist, neoclassical, and policy-rule traditions;
- establish forecasting as an economic rather than purely statistical problem.

Observed structural issue:
The chapter contains substantial verbal theory but comparatively little formalization of the core macroeconomic relations. For example, the Fisher relation is discussed at length in prose, but the chapter does not present a central displayed Fisher equation in the extracted text. The same applies to Phillips- and Okun-type mechanisms.

#### Chapter 2. Why Macroeconomic Forecasting Requires a Nonlinear Perspective
**PDF pp. 42–71**

Current sections:
- 2.1 Economic instability as a source of forecasting breakdown
- 2.2 Business-cycle asymmetries
- 2.3 Structural change, regime dependence, parameter instability
- 2.4 Empirical limits of linear forecasting
- 2.5 Economic justification for nonlinear models
- 2.6 Nonlinearity as an economic hypothesis
- 2.7 Research gap and contribution

Function:
- provide the theoretical/econometric rationale for nonlinear forecasting;
- distinguish threshold, smooth-transition, and Markov-switching reasoning;
- review literature on nonlinear forecasting and instability;
- position the contribution as a unified comparison of linear, discrete-regime, and hybrid nonlinear models under one forecasting protocol.

The research-gap section claims originality primarily from integration: linking macroeconomic theory, nonlinear time-series modeling, and instability-aware forecast evaluation across several U.S. macroeconomic aggregates.

### Part II: Empirical Assessment of Linear and Nonlinear Forecasting under Economic Instability
**PDF pp. 72–167**

#### Chapter 3. Forecasting Design under Macroeconomic Instability
**PDF pp. 74–137**

Current sections:
- 3.1 variable choice and economic justification;
- 3.2 data construction and transformations;
- 3.3 forecasting design and horizon;
- 3.4 AR benchmark;
- 3.5 MSAR;
- 3.6 STAR/MSSTAR;
- 3.7 comparative architecture;
- 3.8 in-sample adequacy;
- 3.9 out-of-sample evaluation;
- 3.10 state-conditioned evaluation;
- 3.11 turning points and state partitions;
- 3.12 strengths, constraints, and identification limits;
- concluding synthesis.

Function:
- define the data and transformations;
- describe the code/configuration logic;
- define the three model classes;
- explain lag selection, estimation, rolling forecasts, diagnostics, forecast metrics, DM tests, conditional predictive ability, recession/expansion partitions, and turning-point windows;
- state methodological limitations.

This is the operational core of the current thesis.

#### Chapter 4. Empirical Evidence, Economic Interpretation, and Policy Meaning under Instability
**PDF pp. 138–167**

Current sections:
- 4.1 overall model performance;
- 4.2 inflation, money, and policy-rate results;
- 4.3 real GDP, industrial production, and unemployment;
- 4.4 turning points and regime dependence;
- 4.5 comparison with nonlinear literature;
- 4.6 fragility and overflexibility;
- 4.7 oil-augmented inflation application;
- 4.8 policy implications;
- 4.9 synthesis.

Function:
- report the main comparative forecast findings;
- display selected estimated equations and transition matrices;
- interpret model behavior economically;
- highlight model failures;
- add a focused oil-price application;
- derive policy-oriented implications.

The headline result is “selective nonlinearity”: MSAR is useful mainly for CPI inflation and some real-activity cases, MSSTAR is most useful for unemployment, while AR remains a serious or preferred benchmark for policy rate and M2 growth. Several nonlinear models fail badly.

---

## 4. General conclusion

**PDF pp. 168–180**

Current blocks:
- restatement of the central problem;
- main theoretical lessons;
- main empirical lessons;
- policy implications;
- limits;
- future research.

The conclusion already contains several important qualifications:
- the main design is single-equation and aggregate-by-aggregate;
- the oil application remains a single-equation extension;
- nonlinear identification can be fragile;
- the empirical ranking is U.S.-specific;
- real-time vintages are not fully used;
- multivariate systems are proposed for future research;
- longer forecast horizons are proposed for future research.

The conclusion therefore recognizes many of the limitations raised by the jury, but recognition in the conclusion does not by itself resolve them empirically.

---

## 5. Appendices

### Appendix A
**PDF pp. 181–189**

Contains a theorem, proof, corollary, and predictive variance decomposition for the probability-weighted MSSTAR forecast.

Current issue:
The theorem is presented as “Theorem A.1” and proved from standard probability arguments, but the manuscript does not clearly label in the visible text whether it is an original theorem, an author-derived proposition from standard results, or a restatement/adaptation of an existing result.

### Appendices B and B'
**PDF pp. 190–200**

Supplementary empirical tables, including:
- model specifications;
- forecast rankings;
- transition matrices;
- fragility cases;
- coefficient support;
- oil-application tables.

### Appendices C and C'
**PDF pp. 201–226**

Supplementary figures, including:
- forecast overlays;
- regime probabilities;
- transition functions;
- turning-point forecast errors;
- oil-application figures.

### Appendix D
**PDF pp. 227–229**

Computational environment and pipeline implementation.

### Appendix E
**PDF pp. 230–234**

Configuration and pipeline parameters, including the YAML parameter inventory.

---

## 6. Current research chain

The submitted manuscript can be summarized as:

**Economic relevance of aggregates**  
→ **instability may create nonlinear dynamics**  
→ **AR as benchmark**  
→ **MSAR as discrete-state alternative**  
→ **MSSTAR as discrete + smooth alternative**  
→ **rolling one-step-ahead comparison**  
→ **full-sample and state-specific evaluation**  
→ **selective nonlinear gains + substantial fragility**  
→ **policy interpretation and limitations**

This chain is coherent. The main issue for Parts 4 and 5 is not that the thesis lacks a research idea. It is that the current architecture is longer and more diffuse than necessary in theory, while several empirical choices still need stronger verification.

---

## 7. What Part 3 does not decide

This map does not decide:
- the final number of chapters;
- whether Chapter 1 or Chapter 2 should be merged or shortened;
- whether M2 should remain;
- whether unemployment or the policy rate should remain in levels;
- which stationarity tests should be used;
- whether a multivariate block should be added;
- whether longer forecast horizons should be added;
- whether two or three regimes should become baseline;
- which forecast-comparison tests should be retained.

Those are Parts 4 and 5 decisions.
