# Part 4: Old versus new thesis structure

**Date:** 5 October 2026  
**Status:** REVISED PROPOSAL FOR USER APPROVAL

## 1. Why the first Part 4 draft was revised

The first Part 4 draft identified four useful scientific functions but removed the visible Part I / Part II hierarchy.

That was not fully aligned with Prof. Verne's earlier instruction that the thesis should produce a **plan in two parts and two subdivisions** reflecting a clear and precise problématique.

The revised structure therefore keeps the four strong chapter functions but nests them inside **two explicit Parts, each containing two chapters**.

## 2. Submitted May 2026 architecture

**General Introduction**

**Part I: Theoretical Foundations**
- Chapter 1: broad macroeconomic aggregates, theory, and policy anticipation
- Chapter 2: instability, asymmetry, nonlinearity, literature, research gap

**Part II: Empirical Assessment**
- Chapter 3: data, models, diagnostics, forecast design, evaluation, implementation
- Chapter 4: results, oil extension, interpretation, policy implications

**General Conclusion**

The main weakness was not the number of chapters. It was the allocation of functions: theory was broad, methodology mixed scientific and software detail, fit/forecast logic was not prominent enough, and robustness/alternative explanations were not organized as a deliberate challenge to the main conclusions.

## 3. Revised architecture

### General Introduction
**Forecasting macroeconomic aggregates when economic relationships become unstable**

### PART I
**Why unstable macroeconomic relationships make forecasting a policy problem**

**Chapter 1**  
*From Fisher, Phillips and Okun to regime change: why inflation, activity and monetary conditions become hard to forecast*

**Chapter 2**  
*From classical benchmarks to state-dependent models: how to test forecast value without confusing fit, complexity and instability*

### PART II
**When nonlinear complexity improves macroeconomic forecasts, and when it fails**

**Chapter 3**  
*From fitted adequacy to forecast performance: evidence across expansions, recessions and turning points*

**Chapter 4**  
*Do nonlinear forecast gains survive? Regime robustness, cross-variable dynamics and policy meaning*

### General Conclusion
**What nonlinear forecasting can and cannot contribute to policy under macroeconomic instability**

## 4. What changes and why

| Previous feature | Revised treatment | Reason |
|---|---|---|
| Broad Part I theory | Focused theory tied to forecast instability and policy relevance | Verne V-02; R1-21; P1-04 |
| Fisher/Phillips/Okun mostly verbal | Explicit equations, assumptions, and forecast relevance | Verne V-02; R1-08 |
| Schumpeter/general schools broad | Retained only where they explain structural change or policy interpretation | Verne V-02; P1-04 |
| Classical comparison mostly AR | Dedicated benchmark-family section considering ARMA and other Verne-named classical approaches where appropriate | Verne V-04 |
| Fit and forecasting not structurally separated enough | Fit/admissibility becomes a visible gate before OOS evidence | Verne V-06 |
| Recession/turning-point evaluation secondary to general results | Expansions, recessions, peaks, and troughs become visible main sections | Verne V-05 |
| Data/method/code mixed | Scientific design remains in Ch. 2; software internals move outside main narrative | R1-21; P1-11 |
| Stationarity concern insufficiently central | Main-text diagnostic stage before model estimation | P-02 |
| Nonlinearity test not central enough | Diagnostic stage before nonlinear interpretation | R1-18 |
| K=2 treated as baseline without requested K=3 check | Dedicated regime-count robustness | P-04 |
| h=1 mainly a limitation | Dedicated horizon robustness | P-05 |
| Oil-X treated as partial multivariate response | Explicit cross-variable analysis designed in Part 5 | R1-19; P-01 |
| Nowcasting absent | Explicit literature/scope section | R1-20 |
| Policy interpretation close to prescription | Predictive usefulness separated from causal policy claims | P-06 |
| Generic chapter summaries | One-page chapter-specific concluding syntheses with unique titles | User requirement; Part 1 P1-13 |
| Generic headings risk | Parts/chapters state the scientific claim or question they resolve | Verne V-08 |

## 5. What is deliberately preserved

The revised structure keeps the strongest elements of the submitted thesis:

- one central forecasting problem;
- a disciplined classical benchmark;
- nonlinear complexity treated as a hypothesis, not a predetermined winner;
- genuine out-of-sample evaluation;
- recession/expansion and turning-point analysis;
- visible model failure;
- distinction between in-sample fit and out-of-sample prediction;
- reduced-form rather than causal interpretation;
- reproducibility and frozen-data discipline.

## 6. How the Part 1 benchmark theses shape the revised two-part plan

### Bernanke
Start from the economic mechanism and explain assumptions.  
**Application:** Chapter 1 starts from the policy/forecast problem and uses economic theory only to explain the mechanisms that matter.

### Shiller
Make model → method → evidence → weakness/refinement dependencies explicit.  
**Application:** Part I formulates the problem and empirical contract; Part II presents evidence and then challenges it.

### Akerlof
Let each unresolved issue create the next chapter.  
**Application:** every chapter ends with a chapter-specific concluding synthesis explaining why the next chapter is necessary.

### Del Campo
Use a coherent general introduction/conclusion around a formally organized monograph.  
**Application:** the thesis has a visible two-Part architecture and a General Conclusion that answers the central problématique.

## 7. After-the-fact doctoral-quality audit

Once Part 9 is written, a reader must be able to answer:

1. What economic problem is being studied?
2. Why does the literature not already answer it?
3. What exactly is added?
4. Why do the models first fit the observed data credibly?
5. Why does the forecast design identify the relevant predictive answer?
6. What evidence would contradict the nonlinear interpretation?
7. Could a better classical benchmark explain the apparent gain?
8. Could structural breaks, lags, regime count, horizon, or omitted cross-variable dynamics explain it?
9. What do the results establish?
10. How robust are they?
11. What can and cannot be generalized?
12. Why does the result matter for macroeconomic policy?

If these answers are not explicit, the final thesis has not satisfied Part 1, the jury, and Prof. Verne simultaneously.
