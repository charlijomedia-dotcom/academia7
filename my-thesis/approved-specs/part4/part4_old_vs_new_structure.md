# Part 4: Old versus new thesis structure

**Date:** 5 October 2026  
**Status:** PROPOSED FOR USER APPROVAL

## 1. Structural diagnosis

The May 2026 manuscript has a coherent question, but the route from question to evidence is longer than necessary.

### Submitted architecture

**General Introduction**

**Part I: Theoretical Foundations**
- Chapter 1: broad macroeconomic aggregates, theory, and policy anticipation
- Chapter 2: instability, asymmetry, nonlinearity, literature, research gap

**Part II: Empirical Assessment**
- Chapter 3: large methodology chapter containing data, transformations, models, diagnostics, forecasting design, evaluation, state partitions, limitations, and implementation detail
- Chapter 4: empirical evidence, interpretation, oil extension, policy implications

**General Conclusion**

The problem is not the existence of four chapters. The problem is the allocation of scientific functions.

Broad theory occupies substantial space before the thesis reaches its testable empirical question. The methods chapter then carries too many tasks at once, including software-level detail. Robustness and threats to interpretation are distributed across methodology, results, appendices, and conclusion rather than being organized as a deliberate attempt to challenge the baseline claims.

## 2. Proposed architecture

**General Introduction: The forecasting problem under macroeconomic instability**

**Chapter 1: Economic instability, state dependence, and the unresolved forecasting problem**
- economic problem
- minimum necessary macroeconomic mechanisms
- nonlinearity/state-dependence taxonomy
- focused literature
- research gap
- competing explanations and falsification conditions

**Chapter 2: Data, empirical identification, and forecasting design**
- data and frozen sample
- stationarity and break diagnostics
- nonlinearity diagnostics
- model hierarchy
- single-equation/multivariate boundary
- forecast experiment
- forecast-comparison criteria
- model-failure rules
- robustness plan
- reproducibility

**Chapter 3: Main forecasting evidence: when does nonlinear complexity earn its place?**
- pre-estimation evidence
- estimation credibility
- full-test forecast evidence
- recession/expansion/turning-point evidence
- cross-aggregate synthesis
- narrow baseline conclusions

**Chapter 4: Robustness, alternative explanations, cross-variable evidence, and economic meaning**
- transformation/persistence robustness
- lag robustness
- regime-count robustness
- horizon robustness
- cross-variable response
- model fragility
- nowcasting/mixed-frequency scope
- policy interpretation
- external validity

**General Conclusion: What nonlinear forecasting can and cannot establish under instability**

## 3. What changes

| Submitted thesis | Revised thesis | Reason |
|---|---|---|
| Long broad theory before empirical question | One focused theory/literature chapter | Part 1 relevance rule; R1-21 |
| Fisher/Phillips/Okun largely verbal | Few essential equations with defined notation | R1-08; P-01 |
| General history of macro schools | Retain only mechanisms used by empirical argument | P1-04 |
| Research gap appears late | Gap and contribution visible in Introduction + Ch. 1 | P1-01, P1-05 |
| “Nonlinearity” spread across many pages | Concise taxonomy + testable implications | R1-10, R1-18 |
| Data/method/code mixed together | Scientific design in Ch. 2; software details outside main narrative | P1-03, P1-11 |
| Open-ended data endpoint | Frozen baseline dataset | Reproducibility safeguard |
| Stationarity concern mostly implicit | Main-text pre-estimation decision evidence | P-02 |
| Model credibility often discussed after results | Failure/admissibility rules defined before results | R1-17, P-03 |
| Main results and robustness partially interwoven | Baseline evidence in Ch. 3; threat-based robustness in Ch. 4 | P1-08, P1-10 |
| K=2 only | K=3 has explicit robustness home | P-04 |
| h=1 mostly left as limitation | Horizon issue has explicit design + robustness home | P-05 |
| Oil-X used as partial response to cross-variable concern | Cross-variable response must be designed explicitly, not assumed solved | R1-19, P-01 |
| Nowcasting absent | Explicit literature/scope treatment | R1-20 |
| Policy interpretation can approach prescription | Predictive evidence separated from causal policy claims | P1-05; P-06 |
| Many decisive tables in appendices | Decision-relevant evidence moves to main text | R1-21; S-06 |
| Failed models can distort figures | Failure shown explicitly with readable visual design | R1-06 |
| External validity mainly near end | External validity built into Ch. 4 and Conclusion | P-06 |

## 4. What is deliberately preserved

The revision should preserve the strongest elements of the submitted thesis:

- the central question of whether nonlinear complexity adds value under instability;
- the AR model as a disciplined benchmark;
- genuine out-of-sample evaluation;
- state-conditioned analysis around recessions and turning points;
- willingness to report model failure;
- distinction between fit and forecasting;
- conditional rather than universal claims about nonlinear usefulness;
- reduced-form forecasting interpretation;
- reproducibility as a core standard.

Part 4 changes the architecture around these strengths. It does not assume that every old methodological choice survives Part 5.

## 5. How the new structure uses the Part 1 reference theses

### Bernanke lesson
Start with the economic mechanism and state what assumptions accomplish.  
**Applied here:** Chapter 1 explains the economic difficulty before the econometric models.

### Shiller lesson
Make the dependency between theory, method, evidence, and refinements explicit.  
**Applied here:** Chapter 1 defines the question; Chapter 2 defines the test; Chapter 3 provides the evidence; Chapter 4 investigates weaknesses and refinements.

### Akerlof lesson
Let the unresolved issue from one stage create the next stage.  
**Applied here:** each chapter ends by identifying exactly why the next chapter is necessary.

### Del Campo lesson
Use the General Introduction and Conclusion to explain the whole monograph, questions, findings, limits, and implications.  
**Applied here:** the Introduction states the complete research logic and the final Conclusion gives one qualified integrated answer.

The proposed structure therefore borrows research logic, not historical formatting or essay packaging.

## 6. After-the-fact doctoral-quality audit

Once Part 9 is written, an external reader should be able to answer all of the following without searching across unrelated sections:

1. What is the problem?
2. Why do we not already know the answer?
3. What exactly is new?
4. What assumptions does the answer depend on?
5. Why does the method identify the relevant forecasting answer?
6. What evidence would have contradicted the main claim?
7. What alternative explanation could invalidate the interpretation?
8. What do the results establish?
9. How robust are they?
10. What cannot be generalized?
11. Why should an economist care?
12. What follows for policy use, without claiming unsupported causality?

If the thesis cannot answer these twelve questions clearly, the structure has not achieved its purpose.
