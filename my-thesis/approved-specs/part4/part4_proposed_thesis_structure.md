# Part 4: Proposed thesis structure

**Project:** *Forecasting Macroeconomic Aggregates under Economic Instability: Theory, Nonlinearity, and Policy Implications*  
**Date:** 5 October 2026  
**Status:** PROPOSED FOR USER APPROVAL  
**Inputs:** approved Parts 1–3 and the user's Part 4 requirements  
**Purpose:** Define the scientific architecture of the revised monograph before Part 5 freezes the econometric methodology.

## 1. Governing design rule

The revised dissertation must make one chain visible from the table of contents onward:

**identify an economic problem → establish what the literature does and does not answer → state the bounded contribution → defend the assumptions and empirical design → specify what evidence would contradict the argument → present the evidence → test alternative explanations → state what can and cannot be concluded → explain why the result matters**

This is the operational application of Part 1. It combines:

- P1-01: one central research problem;
- P1-02: one distinct task per chapter;
- P1-03: technical choices motivated by the problem they solve;
- P1-04: literature retained only when it changes the argument;
- P1-05: originality matched to the actual contribution;
- P1-07: explicit theory-to-evidence link;
- P1-08: results organized around questions;
- P1-09: adverse and inconclusive evidence remains visible;
- P1-10: robustness answers a specific threat;
- P1-12: explicit chapter transitions;
- P1-14: a qualified integrated conclusion.

The structure is therefore not designed around “theory chapter / methodology chapter / results chapter” as independent containers. Each chapter exists because it resolves a question that the next chapter needs.

## 2. Central research problem

Macroeconomic forecasts are often produced with parsimonious linear models even though economic relationships may change across recessions, recoveries, inflation episodes, policy regimes, and turning points. Nonlinear and state-dependent models are designed to represent such changes, but additional flexibility can also create estimation instability, overfitting, implausible regimes, and forecast deterioration.

The economic problem is therefore not simply whether macroeconomic series are nonlinear.

The relevant problem is:

> **When macroeconomic conditions are unstable, does state-dependent nonlinear modelling provide forecast information that is sufficiently credible, robust, and economically meaningful to justify its additional complexity relative to a disciplined linear benchmark?**

This preserves the strongest idea of the submitted thesis while making the burden of proof clearer.

## 3. Central research question

### Main question

> **Under macroeconomic instability, when do nonlinear state-dependent forecasting models provide statistically credible and economically meaningful gains over a disciplined linear autoregressive benchmark, and when does their additional complexity fail to earn its place?**

### Supporting questions

1. **Data and diagnosis:** Do the selected macroeconomic aggregates contain statistical evidence consistent with instability, nonstationarity, structural breaks, or nonlinear/state-dependent dynamics?
2. **Forecast value:** Do nonlinear models improve genuine out-of-sample forecasts relative to the linear benchmark, overall and in economically important states?
3. **Model credibility:** Are any apparent gains supported by credible parameter estimates, stable regimes, acceptable diagnostics, and reproducible estimation?
4. **Alternative explanations:** Could apparent nonlinear gains instead be produced by transformation choices, lag structure, structural breaks, horizon choice, regime count, omitted cross-variable information, or other specification decisions?
5. **Economic meaning:** What can the forecasting evidence establish about macroeconomic instability, and what does it not establish about causal policy transmission?
6. **External validity:** Which findings are specific to the U.S. sample and which elements of the research design are transferable to other settings?

Part 5 will determine the exact tests, models, horizons, robustness specifications, and any multivariate implementation used to answer these questions.

## 4. What the thesis is adding

The revised dissertation must not claim invention of AR, Markov-switching, STAR, MSSTAR, forecast-comparison tests, or nonlinear macroeconomic forecasting.

Its defensible contribution is narrower:

> **The thesis develops and applies a common, benchmark-centred empirical framework in which evidence for instability and nonlinearity is examined before model interpretation, linear and state-dependent models are evaluated under the same forecasting conditions, model failures are treated as evidence rather than hidden, forecast gains are tested across economically relevant states and robustness threats, and the conclusions are explicitly bounded by single-equation, sample, and identification limits.**

The contribution has four layers:

1. **Empirical discipline:** the same data rules, forecast design, evaluation criteria, and failure standards are applied across competing models.
2. **Conditional model value:** the thesis asks where nonlinear complexity helps, not whether one nonlinear family is universally superior.
3. **Failure as evidence:** degenerate, unstable, or non-robust nonlinear estimates are part of the result because they reveal limits to usable state dependence.
4. **Economic interpretation under explicit limits:** forecast evidence is connected to macroeconomic instability and policy relevance without converting predictive associations into unsupported causal claims.

Part 5 must verify that each claimed contribution is supported by the literature and by the final empirical design.

## 5. What would contradict or materially weaken the thesis argument?

The revised thesis must state before the final results that its core proposition is not protected from adverse evidence.

Evidence would weaken the claim that nonlinear complexity is useful under instability if, for example:

- formal diagnostics provide little evidence of relevant nonlinearity or state dependence;
- nonlinear models improve in-sample fit but not out-of-sample forecasts;
- forecast gains are economically trivial or statistically indistinguishable from the benchmark;
- gains disappear when lag choice, transformation, regime count, forecast horizon, or other approved robustness checks change;
- nonlinear estimates repeatedly produce empty, near-absorbing, explosive, or otherwise non-credible regimes;
- gains appear only because the linear benchmark is misspecified;
- cross-variable information explains forecast improvements that were previously attributed to nonlinear own-history dynamics;
- findings depend on a narrow U.S. episode and cannot support broader model-ranking claims.

A result in which the AR benchmark remains dominant is therefore scientifically admissible. It would reject a broad claim of nonlinear superiority while still providing evidence about the conditions under which complexity fails.

## 6. Recommended monograph architecture

The revised dissertation should **remove the old Part I / Part II split** and use one continuous four-chapter monograph.

### Front matter

- Abstract
- Acknowledgements
- Table of contents
- List of tables
- List of figures
- **List of abbreviations and acronyms**
- **List of symbols and notation**

The final two items directly answer the notation and acronym concerns in R1-03 and R1-04.

---

# General Introduction
## The forecasting problem under macroeconomic instability

### Function

The General Introduction must allow an economist to understand the entire project before entering Chapter 1.

It must answer:

- What economic problem is being studied?
- Why should an economist care?
- Why does existing research not fully answer it?
- What exactly does the thesis add?
- What is the central research question?
- What kind of evidence could contradict the proposed argument?
- What is the empirical logic?
- What are the scope and identification limits?
- In the final Part 9 version, what are the verified headline findings?

### Required content

1. Economic motivation: forecast failure under instability.
2. Why linear discipline is still necessary.
3. Why state dependence is a testable hypothesis rather than an assumed fact.
4. Short statement of the literature gap.
5. Main research question and supporting questions.
6. Contribution statement with explicit non-contribution claims.
7. Empirical strategy in one concise overview.
8. Falsification / adverse-evidence conditions.
9. Scope: U.S. aggregates, forecasting rather than causal policy identification.
10. Explicit single-equation limitation and the role of any Part 5 multivariate response.
11. Explicit treatment of nowcasting/mixed-frequency forecasting as either inside or outside the approved scope.
12. Chapter roadmap.
13. In the final manuscript only, a concise preview of verified findings.

### Part 1 principles

P1-01, P1-03, P1-04, P1-05, P1-07, P1-12, P1-15.

---

# Chapter 1
## Economic instability, state dependence, and the unresolved forecasting problem

### Core question

> **Why is macroeconomic instability a reason to test state-dependent forecasts, and what does the existing literature still leave unresolved?**

### Scientific function

Chapter 1 replaces most of the current broad theoretical Part I.

It should contain only the economics and literature needed to understand the empirical question.

### Proposed sections

**1.1 Why forecast instability matters for macroeconomic decisions**  
Define the economic forecasting problem and distinguish forecast failure from ordinary noise.

**1.2 The minimum economic mechanisms needed for the thesis**  
Present the essential Fisher, Phillips/Phelps, and Okun relationships with explicit equations, defined notation, assumptions, and interpretation. The purpose is not to estimate these structural equations as the main thesis models. Their role is to show why inflation, interest rates, output, and unemployment are economically connected and why a purely own-history design has limits.

Money/M2 should appear only if Part 5 confirms its empirical role and data integrity.

**1.3 From structural instability to state-dependent dynamics**  
Define structural change, asymmetry, regime dependence, thresholds, smooth transitions, and latent switching. Give a concise taxonomy of relevant nonlinearities and state what the thesis models cannot represent.

**1.4 What linear and nonlinear forecasting research already establishes**  
Review only literature that affects the thesis argument: linear benchmarks, forecast instability, STAR, Markov switching, hybrid models, forecast evaluation under instability, multivariate nonlinear approaches, and mixed-frequency/nowcasting work.

**1.5 What remains unresolved**  
State the precise gap. The gap is not “nonlinear models have never been compared.” It is the need for a disciplined, common empirical assessment of whether state-dependent complexity produces robust forecast value across selected macroeconomic aggregates and economic states, while explicitly confronting model fragility and cross-variable limitations.

**1.6 Testable implications and competing explanations**  
Translate the literature into empirical implications. State what patterns would support or weaken the nonlinear interpretation and identify the principal competing explanations that Chapters 2–4 must address.

**1.7 Chapter Summary**

### Output

After Chapter 1 the reader should know:

- why the economic problem exists;
- what mechanisms motivate state dependence;
- what the literature already knows;
- what it does not know;
- what the dissertation is adding;
- what evidence could contradict that addition.

### Transition

Because Chapter 1 turns the research gap into testable implications, Chapter 2 must show whether the data and empirical design can actually distinguish those implications.

### Appendix boundary

General history of macroeconomic schools, extended textbook background, long derivations of standard macroeconomic equations, and secondary literature tables should not occupy the main chapter.

### Part 1 principles

P1-01, P1-02, P1-03, P1-04, P1-05, P1-06, P1-07, P1-12, P1-13.

---

# Chapter 2
## Data, empirical identification, and forecasting design

### Core question

> **Why can the selected data and empirical design answer the forecasting question, and what assumptions limit that answer?**

### Scientific function

Chapter 2 is the methodological contract of the thesis.

It must explain the data, transformations, diagnostic sequence, model hierarchy, forecast design, evaluation criteria, failure rules, and robustness logic without turning into a software manual.

### Proposed sections

**2.1 Research design and identification logic**  
Restate the empirical subquestions. Explain what a forecast comparison can identify and what it cannot identify. Distinguish predictive evidence from causal structural inference.

**2.2 Data, sample, and frozen-vintage policy**  
For every retained series report source, frequency, raw sample, usable sample, transformation, economic role, and reason for inclusion. Resolve the M2 date/definition question explicitly. Explain the frozen baseline dataset.

**2.3 Stationarity, persistence, and structural-break diagnostics**  
Place the decision-relevant stationarity evidence in the main text, especially for unemployment and the policy rate. Part 5 will specify the exact tests.

**2.4 Diagnosing nonlinearity before nonlinear interpretation**  
Present the approved nonlinearity tests and their decision rules. Explain what rejection or non-rejection implies and does not imply.

**2.5 A disciplined model hierarchy**  
Define the approved AR benchmark and nonlinear alternatives with only the equations necessary for interpretation. Define Markov states, transition probabilities, persistence, STAR transition functions, and any approved hybrid model clearly. Part 5 determines the exact final set.

**2.6 Cross-variable information and the single-equation boundary**  
Explain why the main design may retain single-equation forecasts, what this design misses, and how the approved Part 5 multivariate or cross-variable response addresses P-01/R1-19. This section must be substantive rather than a one-sentence limitation.

**2.7 Forecast experiment**  
Define forecast origins, estimation windows, re-estimation policy, horizons, information set, state classification, and benchmark equality. Part 5 must make the design both scientifically defensible and computationally efficient without changing the statistical meaning of the experiment.

**2.8 Forecast evaluation and model comparison**  
Define the primary loss measures, statistical forecast-comparison tests, state-conditioned evaluation, and the precise criterion for saying a model is “better.”

**2.9 Model admissibility and failure rules**  
Predefine convergence, regime occupancy, persistence, parameter plausibility, explosive forecast, and other credibility checks. Failed models remain visible.

**2.10 Robustness plan and alternative explanations**  
Map each planned robustness exercise to the threat it addresses: lag choice, transformations, regime count, horizon, cross-variable information, sample/state definitions, and any other Part 5-approved checks.

**2.11 Reproducibility boundary**  
Describe frozen data, traceable outputs, and reproducibility at a scientific level. Software object names, YAML internals, and long parameter inventories belong in appendices/repository documentation.

**2.12 Chapter Summary**

### Output

After Chapter 2 the reader should be able to answer:

- Why these data?
- Why these transformations?
- Why these models?
- Why this forecast experiment?
- What assumptions are required?
- What would count as model failure?
- What evidence would discriminate between the competing explanations?
- What cannot be learned from the design?

### Transition

Chapter 3 can now present the main evidence without interrupting the results to explain basic methodology.

### Appendix boundary

Detailed code configuration, full test formulas that are standard and not necessary for comprehension, software environment, full parameter grids, optimization traces, supplementary diagnostics, and full robustness output belong outside the main narrative. Essential hypotheses, equations, and decision rules remain in the chapter.

### Part 1 principles

P1-02, P1-03, P1-06, P1-07, P1-10, P1-11, P1-12, P1-13, P1-17.

---

# Chapter 3
## Main forecasting evidence: when does nonlinear complexity earn its place?

### Core question

> **Do state-dependent nonlinear models deliver credible out-of-sample forecast gains over the linear benchmark, and in which aggregates or economic states?**

### Scientific function

Chapter 3 contains the main empirical answer. It should be organized by research questions and evidence, not by a dump of model output.

### Proposed sections

**3.1 Pre-estimation evidence and model eligibility**  
Report the main stationarity, structural-break, nonlinearity, and data-quality evidence needed to interpret the model results. Do not repeat Chapter 2's methodological explanations.

**3.2 Estimation credibility before forecast ranking**  
Show whether models converged and whether regimes/transition parameters are credible. Flag failed or fragile specifications before comparing forecast performance.

**3.3 Full-sample out-of-sample forecasting results**  
Present the benchmarked forecast rankings using the primary metrics and statistical comparison tests.

**3.4 Performance under recessions, expansions, and turning points**  
Ask whether any nonlinear advantage is concentrated in the states that motivated the thesis.

**3.5 Evidence by macroeconomic aggregate**  
Synthesize heterogeneity across the retained variables. Avoid six disconnected mini-essays. Focus on what the cross-series pattern says about conditional model value.

**3.6 What the main results establish, and what they do not**  
Separate:
- evidence of nonlinearity;
- credible nonlinear estimation;
- forecast superiority;
- economic interpretation;
- causal claims that are not identified.

**3.7 Chapter Summary**

### Required presentation rule

Every main result must be linked to:
- the question being answered;
- the benchmark;
- the relevant uncertainty/statistical test;
- the model-credibility status;
- the economic implication;
- any qualification that Chapter 4 must test.

Explosive or failed models must not be allowed to make figures unreadable. Failure should be shown in separate or appropriately scaled displays.

### Output

Chapter 3 gives the baseline empirical answer to the central question.

### Transition

A baseline result is not the final thesis claim. Chapter 4 must ask whether the result survives the specific threats identified before the evidence was seen.

### Part 1 principles

P1-02, P1-07, P1-08, P1-09, P1-11, P1-12, P1-13, P1-17.

---

# Chapter 4
## Robustness, alternative explanations, cross-variable evidence, and economic meaning

### Core question

> **Which baseline conclusions survive plausible alternative explanations, and what can the surviving evidence mean for economics and policy?**

### Scientific function

Chapter 4 is not a miscellaneous robustness appendix. It is the chapter that tests the thesis's own strongest claims.

### Proposed sections

**4.1 Threat-based robustness framework**  
For each main conclusion, identify the threat, approved check, result, and implication.

**4.2 Transformation and persistence threats**  
Revisit conclusions sensitive to stationarity treatment, especially unemployment and the policy rate.

**4.3 Lag structure and seasonal-memory threats**  
Address the CPI lag concern and any other Part 5-approved lag robustness.

**4.4 Regime-number and nonlinear-specification threats**  
Report the required K=3 exercise and other approved checks. If a third regime is empty, unstable, redundant, or unhelpful, say so explicitly.

**4.5 Forecast-horizon and evaluation-design threats**  
Address the President's concern that h=1 may be unfavorable to nonlinear models. The exact horizons are a Part 5 decision.

**4.6 Cross-variable information and omitted-dynamics threat**  
Report the focused multivariate/cross-variable analysis approved in Part 5. Ask whether conclusions attributed to own-history state dependence change once economically linked variables are allowed to matter.

**4.7 Model fragility as substantive evidence**  
Revisit near-absorbing regimes, explosive estimates, empty regimes, failed convergence, and other credibility failures. Distinguish “nonlinear model not useful here” from “estimation procedure failed.”

**4.8 Relation to nowcasting and mixed-frequency forecasting**  
If nowcasting is outside the empirical scope, explain exactly why and what question it would answer instead. If Part 5 approves a limited mixed-frequency check, report it here. Do not blur native-frequency forecasting with nowcasting.

**4.9 Economic and policy interpretation**  
Explain what robust forecast evidence means for the use of model complexity in macroeconomic monitoring. Keep predictive usefulness separate from structural causal policy effects.

**4.10 External validity and transferability**  
Separate:
- results specific to the U.S. variables/sample;
- design principles that may transfer;
- hypotheses requiring validation in other economies.

**4.11 Chapter Summary**

### Output

After Chapter 4, the thesis should have a defensible set of claims divided into:
- supported;
- supported with qualification;
- not supported.

### Transition

The General Conclusion can now answer the central question without introducing new evidence.

### Part 1 principles

P1-08, P1-09, P1-10, P1-11, P1-12, P1-13, P1-14, P1-17.

---

# General Conclusion
## What nonlinear forecasting can and cannot establish under instability

### Function

The conclusion integrates the answer rather than repeating four chapter summaries.

It must answer directly:

1. What economic problem was studied?
2. Why did the literature leave the answer open?
3. What did the thesis add?
4. What did the evidence establish?
5. Which claims failed or required qualification?
6. How robust are the surviving findings?
7. What cannot be generalized?
8. Why does the result matter for macroeconomic forecasting and policy?
9. What is the most important next research step?

No new empirical evidence, literature, or robustness exercise should appear here.

## 7. The eight-question acceptance test for the final written thesis

Part 1 must remain an active acceptance standard after Part 9. A completed thesis should pass the following test without requiring the reader to reconstruct the answer.

| Question the final thesis must answer | Primary home |
|---|---|
| What economic problem is being studied? | General Introduction; Chapter 1 |
| Why does existing literature not fully answer it? | General Introduction; Chapter 1.4–1.5 |
| What exactly does this thesis add? | General Introduction; Chapter 1.5–1.6; General Conclusion |
| Why were these data and methods chosen? | Chapter 2 |
| What do the results actually establish? | Chapter 3; Chapter 4; General Conclusion |
| How robust are those results? | Chapter 4 |
| What can and cannot be generalized? | Chapter 4.10; General Conclusion |
| Why does the result matter for economics and policy? | Chapter 1; Chapter 4.9; General Conclusion |

A second, stricter audit should also be possible:

| Doctoral-quality question | Where the answer must be visible |
|---|---|
| What is the problem? | Introduction + Chapter 1 |
| Why do we not already know the answer? | Chapter 1 literature gap |
| What exactly is new here? | Introduction + Chapter 1 contribution statement |
| Why does the method identify the answer? | Chapter 2 identification logic |
| What alternative explanation could invalidate it? | Chapter 1.6 + Chapter 2.10 + Chapter 4 |
| What evidence would falsify or materially weaken the argument? | Introduction + Chapter 1.6 + Chapter 2.9–2.10 |
| Why should an economist care? | Introduction + Chapter 1 + Chapter 4.9 |

If any of these answers is absent, scattered, or only implied, the final manuscript has not yet met the Part 1 structural standard.

## 8. Why four chapters are recommended

Four chapters are recommended because each has one irreducible scientific task:

1. **Chapter 1:** establish the unresolved economic question.
2. **Chapter 2:** show how the question can be tested credibly.
3. **Chapter 3:** provide the main evidence.
4. **Chapter 4:** try to break the main conclusions and interpret what survives.

This is closer to the research logic observed in the Part 1 benchmark theses than the submitted structure, where broad theory and detailed implementation create a long distance between the question and the evidence.

The four-chapter recommendation does not impose equal chapter length. Length should follow the burden of the argument.

## 9. Decisions deliberately deferred to Part 5

Part 4 does not determine:

- the final retained variables;
- whether M2 remains;
- exact stationarity/unit-root tests;
- exact structural-break tests;
- exact nonlinearity tests;
- exact lag-selection rule;
- exact AR/MSAR/STAR/MSSTAR specification;
- whether all current nonlinear models remain;
- exact regime count in the baseline;
- exact K=3 implementation;
- exact forecast horizons;
- exact re-estimation frequency;
- exact forecast-comparison tests;
- exact multivariate/cross-variable model;
- whether a mixed-frequency/nowcasting empirical exercise is implemented;
- exact model-failure thresholds;
- final empirical rankings.

Those are Part 5 decisions and must be made before Claude Code begins Parts 6–8.
