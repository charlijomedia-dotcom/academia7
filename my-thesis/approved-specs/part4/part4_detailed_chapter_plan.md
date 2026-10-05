# Part 4: Detailed chapter plan

**Date:** 5 October 2026  
**Status:** PROPOSED FOR USER APPROVAL  
**Companion:** `part4_proposed_thesis_structure.md`

## 1. Purpose

This file applies the Part 1 chapter-mapping requirement to the proposed four-chapter monograph. Each chapter is defined by a question, a scientific output, and a transition. The purpose is to prevent the final manuscript from becoming a sequence of disconnected literature, methods, and tables.

## 2. General Introduction

| Field | Required entry |
|---|---|
| Working title | The forecasting problem under macroeconomic instability |
| Question | What is the economic problem, why is it unresolved, what does the thesis add, and how will it be tested? |
| Input | Part 1 structural principles; Part 2 jury requirements; Part 3 diagnosis |
| Contribution | Defines the project as one research problem and establishes the burden of proof |
| Evidence or analysis | Concise literature gap; research questions; contribution; empirical logic; falsification conditions; scope |
| Jury requirements | R1-01, R1-09, R1-19, R1-20, R1-21, P-01, P-05, P-06 |
| Part 1 principles | P1-01, P1-03, P1-04, P1-05, P1-07, P1-12, P1-15 |
| Output and transition | Reader knows the problem and the testable claim; Chapter 1 establishes the economic and literature basis |
| Appendix boundary | None. The introduction must stay concise and non-technical |

### Required final-manuscript answers

The introduction must make the following explicit, not implicit:

- the problem;
- the gap;
- the bounded contribution;
- the main question;
- what would count against the thesis argument;
- why the problem matters.

## 3. Chapter 1: Economic instability, state dependence, and the unresolved forecasting problem

| Field | Required entry |
|---|---|
| Question | Why is instability a reason to test state-dependent forecasts, and what remains unresolved? |
| Input | General Introduction |
| Contribution | Converts broad macroeconomic motivation into a precise, literature-grounded empirical problem |
| Evidence or analysis | Essential Fisher/Phillips-Phelps/Okun equations; concise taxonomy of instability/nonlinearity; focused forecasting literature; research gap; competing explanations |
| Jury requirements | R1-08, R1-10, R1-19, R1-20, R1-21, P-01, P-06 |
| Part 1 principles | P1-01 to P1-07, P1-12, P1-13 |
| Output and transition | Reader knows what must be tested and why; Chapter 2 defines the empirical test |
| Appendix boundary | Broad history of schools, textbook background, long standard derivations, supplementary literature tables |

### Section-level logic

| Section | Question it answers | Must produce |
|---|---|---|
| 1.1 Forecast instability | Why is this an economic problem? | Clear motivation tied to forecast decisions |
| 1.2 Core mechanisms | Why are the variables economically linked? | Explicit equations and assumptions |
| 1.3 State dependence | What does “nonlinear” mean here? | Taxonomy and model scope |
| 1.4 Literature | What do we already know? | Focused evidence, not survey |
| 1.5 Gap | Why do we not already know the thesis answer? | Precise unresolved question |
| 1.6 Competing explanations | What else could create the observed pattern? | Pre-results threat list |
| 1.7 Chapter Summary | What is established? | No new content; transition to design |

## 4. Chapter 2: Data, empirical identification, and forecasting design

| Field | Required entry |
|---|---|
| Question | Why can these data and this design answer the forecasting question, and under what assumptions? |
| Input | Chapter 1's testable implications and threats |
| Contribution | Creates an auditable empirical contract before the results |
| Evidence or analysis | Data definitions; stationarity/break evidence; nonlinearity diagnostics; model equations; cross-variable boundary; forecast design; comparison tests; failure rules; robustness plan |
| Jury requirements | R1-03, R1-04, R1-05, R1-08, R1-09, R1-11 to R1-15, R1-17 to R1-20, R1-23, P-01 to P-05 |
| Part 1 principles | P1-02, P1-03, P1-06, P1-07, P1-10, P1-11, P1-12, P1-13, P1-17 |
| Output and transition | Reader knows exactly what is being tested and how evidence will be judged; Chapter 3 reports the baseline answer |
| Appendix boundary | Code internals, configuration names, full optimization grids, software environment, repetitive diagnostics |

### Section-level logic

| Section | Question it answers | Must produce |
|---|---|---|
| 2.1 Identification logic | What can a forecast comparison identify? | Predictive vs causal boundary |
| 2.2 Data | Why these series and dates? | Data table with exact raw/usable samples |
| 2.3 Stationarity/breaks | Are transformations defensible? | Main-text decision evidence |
| 2.4 Nonlinearity | Is nonlinear modelling empirically motivated? | Pre-estimation evidence + limits |
| 2.5 Model hierarchy | What is being compared? | Essential equations + assumptions |
| 2.6 Cross-variable boundary | What does single-equation analysis miss? | Explicit response to P-01/R1-19 |
| 2.7 Forecast experiment | What information is available at each forecast? | Origins, windows, re-estimation, horizons |
| 2.8 Evaluation | What counts as “better”? | Primary metrics and statistical tests |
| 2.9 Failure rules | When is a model not credible? | Predeclared admissibility criteria |
| 2.10 Robustness plan | What could invalidate each conclusion? | Threat-to-check map |
| 2.11 Reproducibility | Can the evidence be regenerated? | Frozen-data/output traceability |
| 2.12 Chapter Summary | What is fixed before results? | No new content |

## 5. Chapter 3: Main forecasting evidence

| Field | Required entry |
|---|---|
| Question | Do nonlinear models deliver credible out-of-sample gains, and where? |
| Input | Chapter 2's frozen empirical contract |
| Contribution | Provides the baseline empirical answer |
| Evidence or analysis | Pre-estimation evidence; model credibility; full-test forecasts; state-conditioned forecasts; cross-aggregate synthesis |
| Jury requirements | R1-06, R1-09, R1-15, R1-17, R1-18, R1-22, P-03 |
| Part 1 principles | P1-02, P1-07, P1-08, P1-09, P1-11, P1-12, P1-13, P1-17 |
| Output and transition | Baseline claims and qualifications; Chapter 4 attempts to invalidate them |
| Appendix boundary | Full coefficient dumps, all rolling estimates, secondary plots, exhaustive diagnostics |

### Results-order rule

Results should appear in this order:

1. **Is the series/model eligible for interpretation?**
2. **Did the model estimate credibly?**
3. **Did it forecast better?**
4. **Was the difference statistically/economically meaningful?**
5. **Did the advantage occur in the states that motivated the nonlinear model?**
6. **What is the narrowest defensible conclusion?**

This prevents a low RMSE from being interpreted as proof of a meaningful nonlinear economic regime when the model itself is unstable.

## 6. Chapter 4: Robustness, alternative explanations, cross-variable evidence, and economic meaning

| Field | Required entry |
|---|---|
| Question | Which baseline claims survive plausible alternative explanations, and what can the survivors mean economically? |
| Input | Chapter 3 baseline findings and Chapter 2 predeclared threats |
| Contribution | Converts baseline results into defensible thesis claims |
| Evidence or analysis | Transformation, lag, regime, horizon, cross-variable, model-fragility, and scope checks; policy interpretation; external validity |
| Jury requirements | R1-06, R1-07, R1-14, R1-15, R1-17, R1-19, R1-20, R1-22, P-01 to P-06 |
| Part 1 principles | P1-08, P1-09, P1-10, P1-11, P1-12, P1-13, P1-14, P1-17 |
| Output and transition | Supported / qualified / unsupported claims; General Conclusion integrates them |
| Appendix boundary | Secondary robustness variants and supplementary tables not needed to change the conclusion |

### Threat-based organization

Chapter 4 should not say “we ran additional tests.” Every subsection should follow:

**baseline claim → threat → robustness check → result → implication for claim**

This directly implements P1-10.

## 7. General Conclusion

| Field | Required entry |
|---|---|
| Question | What is the integrated answer to the thesis question? |
| Input | Only evidence already established in Chapters 3–4 |
| Contribution | States the final bounded answer and why it matters |
| Evidence or analysis | Synthesis only |
| Jury requirements | R1-09, R1-19, P-01, P-05, P-06 |
| Part 1 principles | P1-14, P1-15, P1-16, P1-17 |
| Output and transition | Final thesis claim; future research follows only from identified limits |
| Appendix boundary | None |

## 8. Whole-thesis traceability matrix

The final Part 9 manuscript should permit this trace for every major conclusion:

**claim → Chapter 3 baseline result → Chapter 4 robustness result → Chapter 2 design/assumption → Chapter 1 literature gap → central research question**

If the chain breaks, the claim should be revised or removed.

## 9. Chapter-opening rule

Every substantive chapter should begin by stating:

1. the question it answers;
2. why the previous chapter makes this question necessary;
3. the approach used;
4. what the reader will know by the end.

## 10. Chapter-summary rule

Every substantive chapter ends with approximately one page titled **Chapter Summary**.

It must:

- restate the chapter question;
- summarize only established material;
- state the main takeaway and qualification;
- explain why the next chapter follows;
- contain no new result, citation-driven literature review, or argument.
