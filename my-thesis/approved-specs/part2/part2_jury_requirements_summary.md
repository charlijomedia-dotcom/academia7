# Part 2: Jury requirements summary

**Date:** 3 October 2026  
**Status:** PROPOSED FOR USER APPROVAL  
**Companion file:** `part2_jury_remark_registry.md`  
**Purpose:** Convert the detailed jury registry into a concise set of requirements that Parts 4 and 5 must satisfy.

## 1. Overall diagnosis

The two reports do not reject the research question itself. Their central concern is that the current manuscript does not yet provide a sufficiently transparent, verified, and well-delimited path from macroeconomic theory to the econometric evidence.

The revision therefore has to solve four problems at the same time:

1. make the thesis easier to read and formally self-contained;
2. verify that the data transformations and nonlinear models are statistically credible;
3. broaden the empirical design where the current univariate and one-horizon architecture is too restrictive;
4. narrow the claims so that conclusions do not exceed what the U.S. sample and chosen models can establish.

The reports should not be answered by adding complexity everywhere. They should be answered by making each scientific choice explicit, testable, and traceable.

---

## 2. Requirements for Part 4: thesis structure

### S-01. Build a clearer research architecture
**Related remarks:** R1-01, R1-21.

The revised thesis must be organized into identifiable research functions rather than a long theoretical survey followed by a dense econometric block. The final form can remain a coherent monograph, but the role of each major part and chapter must be obvious.

### S-02. Reduce general theory and keep necessary theory
**Related remarks:** R1-08, R1-10, R1-21.

The thesis should remove theoretical material that does not support the research question while retaining the equations, definitions, assumptions, and economic mechanisms required to understand the empirical work.

### S-03. Make the thesis self-contained
**Related remarks:** R1-03, R1-04, R1-05, R1-08, R1-11, R1-13.

The reader should not need to consult another source to know what the principal equations, models, variables, tests, states, transition probabilities, or symbols mean.

### S-04. Make the univariate scope explicit
**Related remarks:** R1-19, P-01.

The structure must explain why single-equation forecasting is used, what it can identify, and what it cannot identify about interactions and regime transmission across variables. Any approved multivariate response must be integrated into the logical flow rather than added as an unrelated appendix.

### S-05. Separate findings from claims of generality
**Related remarks:** R1-09, P-06.

The thesis structure must create a clear place to distinguish:
- sample-specific empirical results;
- methodological lessons;
- economic interpretation;
- limitations and external validity.

### S-06. Put decision-relevant evidence in the main text
**Related remarks:** R1-05, R1-13, R1-21, P-02.

Stationarity evidence, essential model equations, key diagnostics, and the results required to evaluate the thesis must not be hidden entirely in appendices.

---

## 3. Requirements for Part 5: methodology

### M-01. Freeze and document the data definition
**Related remarks:** R1-12, R1-23.

For every series, Part 5 must define:
- source;
- frequency;
- raw sample dates;
- transformation;
- final estimation dates;
- economic interpretation;
- reason for inclusion.

The M2 issue must be checked directly rather than accepted or dismissed from memory.

### M-02. Justify unemployment and policy-rate transformations formally
**Related remarks:** P-02, P-03.

The methodology must include full-sample stationarity/unit-root analysis for unemployment and the policy rate, including at least one procedure allowing a structural break. The exact tests are not yet fixed.

### M-03. Define nonlinearity before estimating nonlinear models
**Related remarks:** R1-10, R1-18.

Part 5 must state what kinds of nonlinearity are relevant and include an explicit nonlinearity-diagnostic/testing stage before or alongside the nonlinear specifications.

### M-04. Rebuild the Markov-switching specification transparently
**Related remarks:** R1-11, R1-17, P-03.

Part 5 must define the Markov process, transition probabilities, persistence, regime interpretation, convergence checks, and conditions under which an estimated regime model will be treated as credible or failed.

### M-05. Revisit lag selection, especially CPI
**Related remarks:** R1-15.

Lag length must follow a transparent selection rule and robustness process. CPI AR(12) cannot simply be inherited from the submitted thesis without verification.

### M-06. Broaden forecast comparison beyond one unexamined DM test
**Related remarks:** R1-14.

Part 5 must choose forecast-comparison procedures appropriate to the actual design. The reviewer names Clark-McCracken and Amisano-Giacomini as examples, not as automatic mandatory additions.

### M-07. Add a three-regime robustness check
**Related remarks:** P-04.

A K=3 version must be attempted as a robustness exercise. If the final baseline remains K=2, the thesis must explain why K=3 is not retained.

### M-08. Address the forecast-horizon concern
**Related remarks:** P-05.

At minimum, the thesis must explicitly delimit what h=1 can establish. Part 5 must decide whether longer-horizon forecasting should also be included.

### M-09. Respond substantively to the multivariate concern
**Related remarks:** R1-19, P-01.

Part 5 must decide how to address cross-variable relations. The jury does not prescribe one model. The methodological response may involve a focused multivariate extension or another justified design, but it cannot simply ignore the criticism.

### M-10. Address nowcasting/mixed-frequency work explicitly
**Related remarks:** R1-20.

Part 5 must decide whether nowcasting belongs:
- inside the empirical design;
- as a scoped literature/methodological boundary;
- or as a clearly justified future extension.

The omission must be acknowledged and reasoned through.

### M-11. Predefine model-failure and diagnostic rules
**Related remarks:** R1-06, R1-17, R1-22, P-03.

The methodology should define how convergence failures, implausible parameters, near-absorbing states, empty regimes, extreme forecasts, and misleading figures will be identified and reported.

### M-12. Design figures and statistical displays for interpretation
**Related remarks:** R1-06, R1-07, R1-16.

Part 5 should specify what uncertainty information belongs on figures, how failed-model scales are handled, and how statistical significance is presented consistently.

---

## 4. Requirements for Parts 6–8 implementation

Claude Code's later implementation must be able to demonstrate that:

1. all reported results are regenerated from the frozen thesis dataset;
2. stationarity and transformation diagnostics are stored as outputs;
3. lag selection is reproducible;
4. nonlinear tests are reproducible;
5. transition matrices and regime diagnostics are auditable;
6. K=3 robustness is actually attempted and not merely discussed;
7. suspicious policy-rate results are flagged rather than hidden;
8. figures cannot silently mask failed estimates;
9. all forecast-comparison outputs used in the thesis are traceable;
10. the Part 8 report distinguishes successful, fragile, failed, and inconclusive results.

These are implementation consequences of the jury requirements. They do not authorize Claude Code to alter the approved Part 5 methodology.

---

## 5. Requirements for Part 9 writing

The final thesis must:

- use one notation system throughout;
- include a list of acronyms and symbols;
- define every core model and test used;
- state criteria before saying one model is “better”;
- distinguish fit, forecast performance, statistical evidence, and economic interpretation;
- make adverse or failed results visible;
- use accurate terminology for variables and transformations;
- explain the policy-rate and M2 choices;
- keep essential evidence in the body;
- qualify the h=1 design if retained;
- delimit the univariate architecture;
- distinguish U.S.-specific findings from transferable methodology;
- state limitations without undermining valid results;
- avoid claiming that richer nonlinear models are superior unless the reproduced evidence supports that conclusion.

---

## 6. What the jury did NOT uniquely determine

The following remain decisions for Parts 4 and 5:

- the exact number of chapters;
- whether the thesis becomes paper-based or remains a monograph;
- the exact unit-root tests, except that a break-allowing test is required for the disputed level series;
- the exact nonlinearity tests;
- the exact multivariate model;
- whether a full nowcasting model is implemented;
- the exact longer forecast horizons, if any;
- whether Clark-McCracken, Amisano-Giacomini, or another modern forecast test is appropriate;
- whether M2 is retained after the data and economic rationale are verified;
- whether two or three regimes become the final baseline;
- what the final empirical ranking of models will be.

These choices must be made from the scientific evidence in Parts 3–5, not from a desire to obtain a particular empirical result.

---

## 7. Priority order for Parts 4 and 5

### Priority A: must be resolved before final empirical coding
- P-02 stationarity/transformation justification
- P-03 policy-rate instability diagnosis plan
- P-04 three-regime robustness
- R1-15 CPI lag verification
- R1-17 Markov-switching credibility checks
- R1-18 nonlinearity testing
- R1-19 / P-01 multivariate/univariate architecture
- R1-14 forecast-comparison design
- R1-23 M2 data-range verification

### Priority B: must shape the new thesis structure
- R1-01 research architecture
- R1-08 self-contained theory
- R1-10 definition of nonlinearity
- R1-21 lighter but more useful theory
- P-05 horizon scope
- P-06 external validity

### Priority C: must be enforced in final presentation
- R1-02 typographical cleanup
- R1-03 acronym definitions
- R1-04 notation consistency
- R1-05 status of theorems
- R1-06 figure readability
- R1-07 confidence bands
- R1-09 comparison criteria
- R1-13 test definitions
- R1-16 significance notation

---

## 8. Part 2 handoff to Part 3

Part 3 must now inspect the submitted May 2026 thesis and answer, for every high-priority jury ID:

1. What does the current thesis actually do?
2. Where in the thesis is the relevant material?
3. Is the jury concern still present in the submitted version?
4. What part of the current work can be retained?
5. What must be corrected, removed, re-estimated, or redesigned?
6. Which issues are structural and which are methodological?

Part 3 should not yet choose the final solution. Its job is to establish the factual baseline from which Parts 4 and 5 will work.
