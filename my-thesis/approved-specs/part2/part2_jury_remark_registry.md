# Part 2: Jury remark registry

**Date:** 3 October 2026  
**Status:** PROPOSED FOR USER APPROVAL  
**Purpose:** Record the jury remarks exactly enough that Parts 4 and 5 can answer them without confusing the jury's requests with later methodological choices.  
**Source documents:**  
1. Philippe de Peretti, *Rapport du référé #1*, 3 pages.  
2. *Remarque du Président du Jury*, 1 page.

## 1. Reading rule

This registry separates four things:

1. **What the jury actually said.**
2. **What problem the remark identifies.**
3. **What a satisfactory response must demonstrate later.**
4. **What remains open for Parts 4 and 5.**

The registry does **not** yet choose the final thesis structure, model set, stationarity tests, multivariate specification, forecast horizons, or robustness design.

The jury's examples are preserved as examples unless the wording clearly makes them an explicit request.

---

## 2. Reviewer 1: Philippe de Peretti

### R1-01. Reconsider the overall research architecture

**Source:** Reviewer 1, p. 1.

**Remark:** The thesis would benefit from being written around research articles, submitted or not.

**Issue identified:** The current manuscript is difficult to read as a research contribution and its scientific units are not sufficiently clear.

**Minimum response required later:** Part 4 must explicitly decide how to organize the revised monograph into clear research units, even if it does not adopt a three-paper format.

**Not yet decided:** Whether the final thesis should literally be paper-based. The remark is a structural suggestion, not proof that a three-essay format is mandatory.

**Main stage:** Part 4.

---

### R1-02. Remove TeX errors, typographical errors, and notation changes

**Source:** Reviewer 1, pp. 1–3.

**Remark:** The manuscript contains many TeX errors, typographical errors, and changes in notation.

**Issue identified:** Formal presentation is not sufficiently controlled for a doctoral manuscript.

**Minimum response required later:** The final thesis must use one stable notation system and undergo a complete notation and typography audit.

**Main stage:** Parts 4 and 9.

---

### R1-03. Define acronyms rigorously at the beginning of the thesis

**Source:** Reviewer 1, pp. 1–2.

**Remark:** Acronyms such as GDP should be defined rigorously, preferably at the beginning of the thesis.

**Issue identified:** The reader cannot assume the meaning of abbreviations.

**Minimum response required later:** Include a controlled list of abbreviations/acronyms and define each term at first use.

**Main stage:** Parts 4 and 9.

---

### R1-04. Define every symbol and keep notation invariant

**Source:** Reviewer 1, pp. 1–2.

**Remark:** Symbols must be defined and invariant. The report notes inconsistent expectation notation, epsilon/var-epsilon, `o`, `t`, `tau`, `pi`, `pi1`, `pi2`, and undefined variables.

**Issue identified:** Mathematical notation changes meaning or form across the manuscript.

**Minimum response required later:** Create a notation convention and symbol list. Every displayed equation must define its objects, indexes, parameters, operators, and error terms consistently.

**Main stage:** Parts 4, 5, and 9.

---

### R1-05. Clarify authorship/status of theorems and keep essential mathematics in the main text

**Source:** Reviewer 1, p. 1.

**Remark:** The reviewer asks whether the theorems are the author's and states that equations and mathematical results should be inserted in the body of the thesis.

**Issue identified:** The status and relevance of formal results are unclear.

**Minimum response required later:** For every theorem/proposition, state whether it is original, adapted, or standard. Keep the mathematical objects needed to understand the argument in the main text.

**Main stage:** Parts 4 and 9.

---

### R1-06. Correct misleading or implausible figures

**Source:** Reviewer 1, p. 1.

**Remark:** Figure C4_9 has a surprising unemployment scale of roughly -20,000 to 20,000.

**Issue identified:** A failed or explosive model output appears to dominate the visual scale and makes the figure misleading or unreadable.

**Minimum response required later:** Reproduce and audit the figure. If the scale results from model failure, show that failure clearly without allowing it to destroy the readability of the meaningful series.

**Main stage:** Parts 5, 6–8, and 9.

---

### R1-07. Add uncertainty to cross-correlation displays

**Source:** Reviewer 1, p. 1.

**Remark:** Cross-correlations are shown without confidence intervals.

**Issue identified:** The reader cannot assess sampling uncertainty from the figure.

**Minimum response required later:** If cross-correlation figures remain in the thesis, report appropriate confidence bands or another explicit uncertainty measure and explain the interpretation.

**Main stage:** Parts 5 and 6–8.

---

### R1-08. Make the theoretical chapter self-contained with key equations and definitions

**Source:** Reviewer 1, pp. 1–2.

**Remark:** Key equations are absent or only partially shown. The reviewer explicitly asks what a STAR model is, what a regime-switching model is, and what the Fisher equation is. The reader should not have to consult the literature to understand the theoretical chapter.

**Issue identified:** Theory is discussed verbally without enough formal content.

**Minimum response required later:** Present the essential equations, definitions, assumptions, and economic interpretations for every core concept used later.

**Main stage:** Parts 4 and 9.

---

### R1-09. State the criterion behind claims that one model is “better”

**Source:** Reviewer 1, p. 2.

**Remark:** When the manuscript says a model behaves better, the reviewer asks whether the criterion is explanatory power or forecasting performance.

**Issue identified:** Evaluative claims are not tied to a defined metric or research objective.

**Minimum response required later:** Every model comparison must identify the criterion being used, such as fit, forecast loss, density performance, diagnostics, or economic interpretation.

**Main stage:** Parts 5 and 9.

---

### R1-10. Define “nonlinearity” and distinguish its forms

**Source:** Reviewer 1, p. 2.

**Remark:** Nonlinearity is used frequently but not explained. The reviewer notes discrete recurrent breaks and smooth transitions, while stressing that other nonlinearities also exist.

**Issue identified:** The thesis treats “nonlinearity” as if it were a single object.

**Minimum response required later:** Give a precise taxonomy of the nonlinearities relevant to the thesis and delimit which forms the empirical models can and cannot represent.

**Main stage:** Parts 4 and 5.

---

### R1-11. Rebuild the explanation of Markov-switching models and Markov chains

**Source:** Reviewer 1, p. 2.

**Remark:** The three equations are insufficient to define a Markov-switching model; the Markov-chain section and notation such as `pi` need to be reworked.

**Issue identified:** The current explanation does not provide enough probabilistic structure for the reader to understand the model.

**Minimum response required later:** Define states, transition probabilities, transition matrix, regime probabilities, persistence, and the conditional model clearly and consistently.

**Main stage:** Parts 4, 5, and 9.

---

### R1-12. Define variables and justify data choices

**Source:** Reviewer 1, p. 2.

**Remark:** The report questions the meanings of `g` and `pi`, asks why the effective interest rate is used and how it compares with a three-month rate, questions the description and usefulness of M2, and asks what YAML is.

**Issue identified:** Data definitions, economic meanings, and implementation terminology are insufficiently explained.

**Minimum response required later:** Define every variable and transformation, identify each data source and measurement concept, justify the selected policy-rate proxy, use accurate monetary-aggregate terminology, and keep software/configuration terms out of the economic argument unless they are explained and necessary.

**Main stage:** Parts 3, 4, 5, and 9.

**Important:** Part 2 records the reviewer's statements about M2. Whether those statements are factually correct and how the data should be described must be verified later rather than assumed here.

---

### R1-13. Define all statistical tests, including null hypotheses and distributions

**Source:** Reviewer 1, p. 2.

**Remark:** Tests such as ARCH-LM and Jarque-Bera must be defined in the body and their distributions under the null hypothesis stated.

**Issue identified:** Diagnostic tests are reported without enough statistical explanation.

**Minimum response required later:** For each retained diagnostic or inferential test, state its purpose, null hypothesis, relevant statistic/distribution or reference result, decision rule, and interpretation.

**Main stage:** Parts 5 and 9.

---

### R1-14. Update and broaden forecast-comparison testing

**Source:** Reviewer 1, p. 2.

**Remark:** Diebold-Mariano is described as old. The reviewer suggests looking at newer developments such as Clark-McCracken and Amisano-Giacomini, including density-based comparisons.

**Issue identified:** The forecast evaluation framework may rely too heavily on one comparison test.

**Minimum response required later:** Part 5 must review modern forecast-comparison methods and select tests that match the actual forecasting design and hypotheses.

**Not yet decided:** The reviewer named Clark-McCracken and Amisano-Giacomini as examples. Part 2 does not treat every named test as mandatory irrespective of model nesting, loss function, or density availability.

**Main stage:** Part 5.

---

### R1-15. Re-examine the CPI lag structure

**Source:** Reviewer 1, p. 2.

**Remark:** The inflation equation has an unusually long lag of 12 months. The reviewer questions whether this reflects seasonality or regime change rather than genuine 12-month dependence and notes the absence of an associated graph.

**Issue identified:** The lag choice may be economically or statistically implausible.

**Minimum response required later:** Re-estimate and justify the CPI lag order under a transparent lag-selection and robustness procedure. Show the relevant series/model evidence needed to understand the choice.

**Main stage:** Parts 5 and 6–8.

---

### R1-16. Standardize significance notation

**Source:** Reviewer 1, p. 2.

**Remark:** Significance stars should be in superscript.

**Issue identified:** Presentation of statistical significance is inconsistent with the reviewer's expected academic format.

**Minimum response required later:** Use one significance convention consistently in final equations/tables and define it once.

**Main stage:** Part 9.

---

### R1-17. Verify suspicious Markov-switching transition results

**Source:** Reviewer 1, pp. 2–3.

**Remark:** Several transition matrices appear to contain absorbing or nearly absorbing states. One model has a second-regime probability near one, and another has a zero diagonal transition probability. The reviewer questions whether these results are compatible with the intended recurrent Markov-switching interpretation.

**Issue identified:** Some estimated regime models may be numerically unstable, misspecified, or substantively inconsistent with the model's intended interpretation.

**Minimum response required later:** Reproduce the estimates, audit convergence and parameterization, inspect regime occupancy/persistence, and determine whether each model is credible, fragile, or unsuitable for the relevant series.

**Main stage:** Parts 5 and 6–8.

---

### R1-18. Test for nonlinearity before imposing nonlinear models

**Source:** Reviewer 1, p. 3.

**Remark:** The econometric section lacks tests of nonlinearity on which Markov-switching or STAR approaches should be based.

**Issue identified:** Nonlinear specifications are introduced without an explicit empirical pretest or diagnostic basis.

**Minimum response required later:** Part 5 must define an appropriate nonlinearity-testing stage and explain what the test can and cannot justify about the subsequent model choice.

**Main stage:** Part 5.

---

### R1-19. Add a multivariate dimension

**Source:** Reviewer 1, p. 3.

**Remark:** The econometric section lacks multivariate approaches. The reviewer argues that the important question is not only whether one series is nonlinear, but why and how this relates to other variables, noting multivariate STAR and cointegrated settings.

**Issue identified:** The univariate design does not capture cross-variable transmission or joint macroeconomic relationships.

**Minimum response required later:** Parts 4 and 5 must give a substantive response to the multivariate concern, either through an approved multivariate empirical block or another clearly justified design that directly addresses the limitation.

**Not yet decided:** Part 2 does not choose VAR, VECM, STAR multivariate, MS-VAR, FAVAR, or another model.

**Main stage:** Parts 4 and 5.

---

### R1-20. Address the nowcasting and mixed-frequency literature

**Source:** Reviewer 1, p. 3.

**Remark:** The thesis ignores the nowcasting literature, which allows multiple frequencies to be mixed.

**Issue identified:** A relevant branch of modern macroeconomic forecasting is absent.

**Minimum response required later:** Parts 4 and 5 must decide how the revised thesis will address this omission, whether through the literature, scope justification, a methodological extension, or another explicit treatment.

**Not yet decided:** The reviewer identifies the omission but does not prescribe a specific nowcasting model.

**Main stage:** Parts 4 and 5.

---

### R1-21. Lighten the theoretical part while moving essential material into the body

**Source:** Reviewer 1, p. 3.

**Remark:** The theoretical part can be shortened, while many appendix elements and every mathematical/statistical notion needed for comprehension should appear in the main text.

**Issue identified:** The manuscript is simultaneously too long in general theory and too sparse in essential formal explanation.

**Minimum response required later:** Part 4 must reduce nonessential theoretical survey material and reserve main-text space for definitions, equations, assumptions, diagnostics, and results that are necessary to assess the thesis.

**Main stage:** Part 4.

---

### R1-22. Verify and broaden the econometric results

**Source:** Reviewer 1, p. 3.

**Remark:** Many econometric results raise questions and should be verified and broadened.

**Issue identified:** The existing empirical results cannot simply be carried into the revised thesis.

**Minimum response required later:** The final empirical pipeline must reproduce the analysis from controlled data and document estimation failures, diagnostics, robustness, and any material changes from the submitted results.

**Main stage:** Parts 5–8.

---

### R1-23. Resolve the M2 sample/relevance problem

**Source:** Reviewer 1, p. 3.

**Remark:** The reviewer questions the usefulness of forecasting a series whose history appears to stop in 1992.

**Issue identified:** Either the data range, description, source, or displayed sample is unclear or incorrect.

**Minimum response required later:** Verify the actual M2 source, raw sample dates, transformed sample dates, forecast evaluation dates, and economic justification. Correct the manuscript if the previous presentation was wrong.

**Main stage:** Parts 3, 5, and 6–8.

---

## 3. President of the Jury

### P-01. Justify and delimit the single-equation architecture

**Source:** President's remarks, p. 1.

**Remark:** Treating variables one by one needs stronger justification because Fisher, Phillips, and Okun mechanisms involve interactions. The thesis should state that its framework cannot detect a regime change transmitted through another variable and should delimit what the method demonstrates.

**Issue identified:** The theoretical narrative is multivariate, while the empirical architecture is mainly univariate.

**Minimum response required later:** The revised thesis must explicitly define what the single-equation analysis identifies, what it cannot identify, and how the final research design responds to cross-variable interactions.

**Main stage:** Parts 4 and 5.

---

### P-02. Test stationarity of unemployment and the policy rate over the full sample, including a break-allowing test

**Source:** President's remarks, p. 1.

**Remark:** Four variables are log-differenced, while unemployment and the policy rate remain in levels. The President requests unit-root testing over the full period, including a test that allows a structural break, and recommends placing the evidence in the main text rather than the appendix.

**Issue identified:** The level transformations of the two most disputed series need formal justification.

**Minimum response required later:** Part 5 must specify formal stationarity/unit-root diagnostics for these series, including at least one break-allowing procedure. The main thesis must report the evidence needed to justify the chosen transformations.

**Not yet decided:** The President does not name a specific test. The exact test family is a Part 5 decision.

**Main stage:** Part 5.

---

### P-03. Diagnose the extreme policy-rate Markov-switching result

**Source:** President's remarks, p. 1.

**Remark:** Coefficients in the hundreds, variance above 90,000, and a transition probability of 0.999995 may indicate that regime switching is unsuitable for the policy rate, or may reflect an estimation problem caused by the nearly nonstationary level series. Both explanations remain possible.

**Issue identified:** The current result cannot be interpreted until data transformation and estimation validity are resolved.

**Minimum response required later:** Reproduce the result under the approved stationarity treatment and estimation protocol, then distinguish model inadequacy from numerical/specification failure as far as the evidence allows.

**Main stage:** Parts 5 and 6–8.

---

### P-04. Test a three-regime specification as robustness

**Source:** President's remarks, p. 1.

**Remark:** Two regimes are conventional but cannot distinguish recovery from established growth. The President asks for a three-regime version, even simply as a check, and an explanation if it is rejected.

**Issue identified:** The imposed two-state structure may be too restrictive.

**Minimum response required later:** Include an approved three-regime robustness exercise and report whether the third regime is empirically meaningful, stable, and useful. If the final thesis retains two regimes, explain why.

**Main stage:** Part 5 and Parts 6–8.

---

### P-05. Address the one-step forecast-horizon limitation

**Source:** President's remarks, p. 1.

**Remark:** Nonlinear models often show usefulness over longer horizons. Restricting the analysis to one month may test them where they have the least chance to perform well. The President says this should at least be acknowledged.

**Issue identified:** The chosen horizon may condition the comparative result.

**Minimum response required later:** The revised thesis must explicitly discuss the horizon limitation.

**Not yet decided:** The President does not explicitly require a complete multi-horizon rerun. Whether to add longer-horizon forecasts is a Part 5 decision.

**Main stage:** Parts 4 and 5.

---

### P-06. Clarify external validity and transferability

**Source:** President's remarks, p. 1.

**Remark:** The model-selection rule is derived from six U.S. variables over a particular period. The thesis should state whether the result is U.S.-specific or whether the method can be applied elsewhere, such as an emerging economy with volatile inflation or a small open economy.

**Issue identified:** The thesis risks presenting a sample-specific ranking as a general rule.

**Minimum response required later:** Distinguish clearly between sample-specific empirical findings and any transferable research design or methodology.

**Main stage:** Parts 4 and 9.

---

## 4. Cross-jury convergence

Several issues are independently reinforced by both reviewers:

| Cross-jury issue | Reviewer 1 | President |
|---|---|---|
| Univariate limitation / cross-variable relations | R1-19 | P-01 |
| Questionable policy-rate MS results | R1-17, R1-22 | P-03 |
| Need to justify transformations/stationarity | R1-12, R1-23 | P-02 |
| Need for broader robustness | R1-14, R1-15, R1-18, R1-22 | P-04, P-05 |
| Scope of claims | R1-09, R1-22 | P-06 |
| Main-text transparency | R1-05, R1-08, R1-13, R1-21 | P-02 |

These convergences should receive high priority in Parts 4 and 5 because they are not isolated presentation comments.

---

## 5. Part 2 completion rule

Part 2 is complete only when:

- every substantive remark from both source documents has an ID;
- no later proposal is described as a jury requirement unless the source actually supports it;
- Parts 4 and 5 can cite these IDs directly;
- unresolved choices remain explicitly unresolved until the appropriate stage.

