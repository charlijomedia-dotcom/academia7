# Part 3: Current thesis strengths and weaknesses

**Date:** 3 October 2026  
**Status:** PROPOSED FOR USER APPROVAL  
**Source:** `CHARLIJO TANNOURY PHD THESIS May 2026.pdf`  
**Purpose:** Identify what should be preserved, what should be simplified, and what must be re-verified before the Part 4 structure and Part 5 methodology are approved.

## 1. Main strengths to preserve

### S1. The thesis has a real economic question
The manuscript is not merely “AR versus nonlinear models.” It asks whether state-dependent representations improve forecasting under instability and whether gains are robust enough to matter economically.

This is a strong foundation and should survive the redesign.

### S2. The benchmark-centered logic is disciplined
The AR model is treated as a serious benchmark rather than a straw man. Lag order is selected systematically, diagnostics are applied, and nonlinear models are evaluated under the same forecast window and horizon.

This aligns well with the Part 1 benchmark principle that richer methods must solve a defined problem.

### S3. The thesis does not assume nonlinear superiority
The manuscript repeatedly states that complexity must earn its place. Chapter 4 reports both successful and failed nonlinear cases.

This is scientifically valuable and should be preserved.

### S4. The rolling out-of-sample framework is conceptually strong
The thesis separates in-sample adequacy from pseudo-out-of-sample forecast evaluation and re-estimates models over rolling windows.

The distinction between fit and forecasting is one of the strongest parts of the current research design.

### S5. State-conditioned evaluation is well motivated
The thesis evaluates full-sample, recession, expansion, turning-point, and non-turning-point performance and assigns state at the forecast target date.

This directly operationalizes the thesis question about instability.

### S6. The current manuscript already goes beyond DM alone
The Giacomini-White-type conditional predictive ability regression is a useful addition because it tests whether relative forecast performance changes with recession or turning-point states.

### S7. Markov-switching mechanics are substantially explained
The current Chapter 3 defines transition probabilities, the transition matrix, stationary probabilities, filtered probabilities, and expected durations.

This material can be simplified and standardized rather than rebuilt from zero.

### S8. The manuscript contains a STAR linearity-testing procedure
The Luukkonen-Saikkonen-Teräsvirta auxiliary regression is already used for delay and transition-type selection in the MSSTAR stage.

This is an important existing asset, although the role and reporting of the test need to be strengthened.

### S9. The manuscript exposes fragile models
The policy-rate MSAR failure is not hidden. The thesis shows the extreme coefficients, very large regime variance, and near-absorbing transition matrix and explicitly calls the result economically unusable.

This transparency should be preserved in the revised dissertation.

### S10. The conclusion already contains responsible scope limitations
The manuscript states that:
- the design is single-equation;
- the oil application is not a VAR;
- the U.S. ranking is not universal;
- real-time vintages are limited;
- longer horizons and multivariate systems are natural extensions.

These admissions provide a good starting point for a cleaner final argument.

---

## 2. Structural weaknesses

### W1. The distance between research question and empirical evidence is too long
The current manuscript contains:
- a long introduction;
- a broad theory chapter;
- a second broad nonlinearity chapter;
- a very long methodology chapter;
before reaching the main empirical evidence.

Part 1 benchmarks suggest that the final structure should shorten this distance.

### W2. Chapter 1 is broader than the empirical design needs
The chapter discusses:
- Fisher and monetary theory;
- Phillips/Phelps and Okun;
- Schumpeterian innovation;
- Keynesian, monetarist, and neoclassical schools;
- policy forecasting.

Not all of these strands are used with equal force later. The theoretical burden is large relative to the actual single-equation forecasting experiment.

### W3. Core theory is often verbal when the jury wants formal objects
The manuscript discusses Fisher, Phillips, and Okun mechanisms largely in prose. The relevant equations are not consistently displayed in the theoretical chapter.

This creates the paradox identified by Reviewer 1: the theory is long, yet some key formal content is still missing.

### W4. Chapter 3 mixes economic methodology with software implementation detail
YAML configuration, internal object names, code flags, fallback switches, and implementation details appear in the main methodology chapter.

Some of this improves reproducibility, but too much of it interrupts the economic logic. The final thesis needs a clearer boundary between:
- scientific design;
- econometric specification;
- implementation documentation.

### W5. Essential evidence is often pushed to appendices
Many core tables and figures used to establish model credibility appear in Appendices B and C. The body refers to them, but the reviewer explicitly wants more of the decisive material visible in the main text.

---

## 3. Methodological weaknesses requiring re-verification

### W6. Unemployment and policy-rate levels are justified mainly by interpretation, not formal stationarity evidence
The current text calls unemployment “stationary-looking” and prefers policy-rate levels because the absolute stance is meaningful.

That is not enough to answer the President's stationarity concern.

### W7. The data are not frozen
The end date is open in the configuration. A later rerun can change the sample.

This must be corrected for final thesis reproducibility.

### W8. CPI AR(12) remains insufficiently challenged
The lag-selection procedure can choose 12 monthly lags, but the final manuscript does not show a focused robustness analysis explaining whether CPI p=12 is:
- genuine persistence;
- annual/seasonal structure;
- lag-selection artifact;
- a symptom of regime change.

### W9. The two-regime baseline is imposed
The thesis explains why K=2 is parsimonious and interpretable, but it does not report the K=3 robustness requested by the President.

### W10. The policy-rate MSAR failure is diagnosed descriptively, not resolved causally
The thesis correctly flags the model as degenerate, but it does not determine whether the failure is driven primarily by:
- the level transformation;
- near nonstationarity;
- model specification;
- optimizer behavior;
- insufficient regime identification.

The President explicitly leaves these explanations open.

### W11. Model-failure criteria are not fully predefined
The manuscript discusses fragility after seeing the results, but the methodology lacks a strict predeclared classification rule for unstable or degenerate nonlinear fits.

### W12. Forecast horizons are restricted to h=1
The code is multi-step capable, but the thesis evidence is one-step-ahead only. This remains a direct jury concern.

### W13. Forecast-comparison testing still needs a Part 5 review
DM and Giacomini-White-type CPA are present. The reviewer nevertheless asked for broader modern comparison methods.

The correct final response is not yet known, but the current framework should not be treated as final.

### W14. The nonlinearity test is present but not fully integrated into model eligibility
The Luukkonen-Saikkonen-Teräsvirta test is used mainly to select delay/type within the STAR layer.

The current design does not state a simple ex ante rule such as:
- when linearity is not rejected, what happens to STAR/MSSTAR?
- what evidence justifies estimating MSAR?
- whether a failed nonlinearity test affects model interpretation.

### W15. The multivariate concern is not solved
The oil extension introduces one exogenous predictor into inflation but explicitly remains single-equation.

This is not equivalent to modeling interactions among inflation, output, unemployment, money, and policy rates.

### W16. Nowcasting is absent
No explicit nowcasting or mixed-frequency nowcasting section was found. The thesis preserves native frequencies, but that is not the same thing as a nowcasting framework.

---

## 4. Presentation and notation weaknesses

### W17. No front-matter acronym list was found
The reviewer explicitly asked for one.

### W18. No global symbol/notation list was found
Notation is defined locally, but there is no clear unified symbol inventory before the main text.

### W19. Theorem authorship/status remains unclear
Appendix A states “Theorem A.1” and proves it using standard conditional-expectation logic, but the manuscript does not clearly label whether it is:
- original;
- author-derived from standard probability identities;
- adapted from prior literature.

### W20. Statistical-test reporting is not standardized enough
Formulas and purposes are given, but the null hypothesis, reference distribution, decision rule, and interpretation are not consistently presented in a uniform format.

### W21. Some displayed notation/formatting remains awkward
Examples include:
- raw code/configuration names inside prose;
- duplicated formatting such as `d=1d = 1d=1` in the oil section;
- mixed symbol styles and implementation names.

This supports Reviewer 1's broader complaint about polish and readability.

### W22. Figure design can allow failed models to distort visual scale
The unemployment figure C4_9 is intended as a forecast overlay, while the reviewer reported an extreme scale. The current text explains what the figure should show, but the final pipeline must explicitly prevent failed-model values from making the informative series unreadable.

### W23. Oil cross-correlation figure lacks an explicit confidence-band statement
The oil section refers to cross-correlation evidence, but the figure note only explains lag interpretation. The reviewer explicitly asked for confidence intervals on such displays.

---

## 5. Claim weaknesses

### W24. The current contribution statement is broader than the safest literature-supported claim
The thesis says its originality lies in reconnecting theory, nonlinear traditions, and forecast evaluation in a unified framework across several aggregates.

That may be a legitimate contribution, but Part 5/literature review must avoid implying that:
- AR/MSAR/STAR comparison itself is new;
- hybrid Markov-STAR modeling itself is new;
- state-dependent forecast comparison itself is new.

The safest contribution is likely empirical/design integration, not invention of the model classes.

### W25. Policy interpretation sometimes moves close to policy prescription
The models are reduced-form forecasting tools. The thesis generally acknowledges this, but some language about what policymakers “should” do risks sounding stronger than what forecast ranking alone can establish.

The final manuscript should keep forecasting usefulness separate from structural causal policy evaluation.

---

## 6. Overall Part 3 diagnosis

The current thesis is **not conceptually empty or methodologically primitive**. It already contains:

- a coherent research question;
- a benchmark-centered model hierarchy;
- rolling out-of-sample evaluation;
- state-conditioned forecast analysis;
- DM and conditional predictive ability tests;
- a STAR linearity scan;
- explicit discussion of fragile nonlinear models;
- a focused oil application;
- a serious limitations section.

The main revision problem is therefore **not to replace everything**.

The real task is to:

1. compress the theoretical path;
2. formalize only the economic mechanisms that directly support the empirical question;
3. re-verify the contested transformations and nonlinear results;
4. add the missing robustness demanded by the jury;
5. address the univariate/multivariate mismatch;
6. tighten model-failure rules;
7. freeze the data;
8. bring decisive evidence into the main text;
9. make the contribution narrower and more defensible.

This diagnosis should guide Part 4 and Part 5.
