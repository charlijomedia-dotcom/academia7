# Appendix D. Reproducibility, Forecast Availability, and Methodological Corrections

This appendix explains how the historical forecast exercise can be checked without incorporating software implementation details into the economic argument. It is concerned with the distinction between an attempted estimate, a retained forecast, a fragile fit, a failed fit, and an available inferential comparison. The main chapters state the statistical methods and conclusions; this appendix records the practical methodological boundaries that affect reproducibility and scientific interpretation.

## D.1 Reproducible information set and evaluation calendar

The empirical exercise uses a historical data collection frozen as of 5 October 2026. The six series and their transformations are detailed in Appendix A; the two author-constructed October 2025 values and their methodological rationale are specified directly in Chapter 2, Section 2.2. The principal rolling estimation windows contain 240 monthly or 120 quarterly observations. Model orders are selected on the initial window and not reselected after inspecting the main comparison. Forecast dates are restricted so realized target values are not used in fitting the forecast that predicts them. The outcomes, however, are measured against the chosen **later fixed historical data vintage**, not against each initial publication vintage as it was available in real time.

A forecast row is eligible for loss computation only if its forecast value and target are available and the model's fit is not classified as failed. A *fragile* but finite forecast remains in the scored results, preserving the evidence about real-world numerical vulnerability. A failed fit is disclosed and **not** silently replaced by a competitor or imputed prediction. Pairwise loss tests use the target-date intersection of a competitor's retained forecasts and the benchmark's available retained forecasts; multiple-model procedures use their own all-candidate common-date intersection. Consequently, own-valid-date RMSE, matched AR-relative out-of-sample $R^2$, and formal paired test results can have different observation counts.

The regression-oriented baseline covers monthly CPI, unemployment, industrial production, the effective funds rate and M2, while GDP remains quarterly. The multivariate robustness comparison uses only five monthly aggregates with an explicit balanced sample and stability requirement. Turning-period labels use NBER dates assigned retrospectively. Neither a smoothed MSAR state probability nor a retrospective recession dummy is assumed observable at the forecast origin.

## D.2 Failure and model-credibility classifications

**Table D.1. Model-fit and forecast-scoring dispositions**

| Category | Operational meaning | Effect on descriptive scoring | Effect on inferential comparisons |
|---|---|---|---|
| Adequate fitted model | Retained estimate meeting the specified numerical and diagnostic rules | Score finite forecasts when targets are observed | Enter a test only on the appropriate common dates |
| Fragile fitted model | An estimate with warnings such as low state occupancy, transition boundary, ill-conditioned covariance or extreme transition parameters | Retain and score its finite forecasts | Include unless the formal test is numerically uninformative |
| Failed fitted model | Fit violates retention rule or cannot provide an admissible forecast | Do not score a missing or invalid forecast as successful | Remove that pairwise date or all-candidate date; disclose resulting sample |
| Extreme finite forecast | Numerically finite output with implausibly large loss | Retain in RMSE/MAE, without winsorizing | Test may be degenerate; report unavailability of meaningful inference where documented |
| Numerical test unavailability | Loss-test statistic cannot be meaningfully calibrated or determined | Does not change scored forecast losses | Do not interpret its p-value as a substantive non-rejection or as proof of equality |

*Source: Author's methodological definitions and empirical classifications.* *Note:* A fit can have multiple warnings, but it receives one status in the fit-status table (Appendix C, Table C.7). The associated reason-code event count is a different object. These rules prevent a favorable sample of successfully fitted models from being mistaken for the full performance of the estimation method.

The archived estimation register contains **67,253 classified model-fit records** across the principal forecasting families and the supplementary ARMA–GARCH, VAR and three-state MSAR exercises. Their exact model-by-model reconciliation is provided in Table D.4. A separate diagnostic registry contains **34,122 reason-code events** in the corrected released analysis, comprising **512 failed-category and 33,610 fragile-category events**. These 34,122 entries are warning/failure *events*, not unique failed or fragile fits; several events may arise from one fit. The counts are therefore not interchangeable with totals in Table C.7, which aggregates classified fit records for the four named model families and target chains. A zero in the recorded failed-fit column of one family does not imply an absence of fragility or outlying finite forecasts.

## D.3 Regime-count and likelihood limitations

The baseline comparison predeclares the two-state Markov-switching model. A three-state alternative is estimated once on each complete transformed sample to probe **in-sample** model credibility. A rolling K=3 forecast evaluation would have added 3,527 attempted origin-level fits to six full-sample fits, for 3,533 planned calls. The final restricted exercise retains six full-sample fits, avoiding 3,527 planned K=3 calls, approximately **99.83% of those planned fit calls**. This is not a measured 99.83% CPU-time saving, because fit durations are heterogeneous.

The K=3 assessment is not a regular nested likelihood-ratio test of regime count, and no three-state forecasting superiority is inferred from its information criteria. For unemployment, the obtained three-state likelihood is worse than that for two states, despite additional parameters. This indicates optimization or numerical identification failure and leaves the regime-count comparison inconclusive rather than proving the two-state assumption. More generally, convergence to a local solution does not guarantee that a global likelihood maximum has been found for any MSAR fit.

Model covariance matrices, effective state counts and transition probabilities are evaluated together. A state fitted to one extreme observation can improve likelihood while failing a credible recurrence or occupancy criterion. The full-sample probability plot for the three-state unemployment model is given in Appendix C, Figure C.1; the directly interpretable CPI two-state example remains in Chapter 3.

## D.4 Numerical safeguards and corrected presentation

**Table D.2. Relevant methodological distinctions and controlled corrections**

| Scientific issue | Treatment retained in the final analysis | Interpretive consequence |
|---|---|---|
| Failed model forecasts | Exclude failed-fit predictions from accuracy scoring; preserve their counts and reasons | No artificial forecast improvement through invalid output substitution |
| Multiple-model confidence set under exceptional losses | Apply documented numerical safeguards without replacing the declared statistical method | Do not infer model equality simply because the set retains an unstable competitor |
| Pairwise loss orientation | Use competitor loss minus AR loss consistently | The sign of the average differential and the p-value refer to the same hypothesis |
| Break-sensitive unit-root diagnostics | Make Zivot–Andrews results visible alongside ADF and KPSS | Do not claim break-sensitive non-rejection establishes stationarity |
| Alternative-transformation labels | Preserve precise baseline and alternative economic representation | Forecast losses are not compared across unlike target scales |
| Extreme forecast plots | Place ordinary and flagged/extreme cases in separate, labelled figure panels | A readable main panel does not hide the extreme forecast's contribution to scored loss |
| Latent-state optimization | Disclose sensitivity to initialization and inability to certify global optima | Do not present fragile regimes as uniquely identified economic mechanisms |
| Missing 2025 observations | Explicitly distinguish author-processed carry-forward levels from official measurements | The full endpoint is maintained with a visible sensitivity and information limitation |

*Source: Author's methodological record and final computation evidence.* *Note:* These are scientific safeguards and documented changes relevant to interpreting the reported results. They are not evidence that an optimizer converges globally, that excluded dates are missing at random, or that unreported alternative models have been tested.

The main model specification is not silently changed to obtain a more favorable result. Unresolved cases are recorded as such. In particular, the unemployment K=3 likelihood comparison is inconclusive, the CPI h=12 multiple-testing adjustment is supplementary rather than a new principal test, and some STAR loss tests are numerically uninformative because of huge finite forecast errors.

## D.5 Computing environment and documented workload

The recorded execution environment used Python 3.11.18 on a Linux x86-64 platform, including NumPy 2.4.6, pandas 3.0.6, SciPy 1.17.1, statsmodels 0.15.0 and the other numerical dependencies required by the selected estimation and resampling routines. Hardware characteristics or total machine-time consumption beyond the archived records are not inferred.

**Table D.3. Selected stage-level recorded resource use**

| Recorded stage | Wall-clock duration (s) | Reported CPU duration (s) | Recorded peak memory (MB) |
|---|---:|---:|---:|
| data | 1.0 | 1.0 | 292.3 |
| stationarity | 3.9 | 4.3 | 369.2 |
| nonlinearity | 0.1 | 0.4 | 374.4 |
| adequacy | 3624.7 | 2159.9 | 598.9 |
| forecasting | 25531.5 | 31.5 | 730.0 |
| evaluation | 268.8 | 505.5 | 759.0 |
| robustness | 3133.7 | 7369.9 | 854.5 |
| finalize | 7.1 | 7.1 | 933.2 |

*Source: Author's recorded environment and stage summaries.* *Note:* This is a **record for one baseline run**, not a sum of all historical calculations or of later correction and robustness runs. The separate wall and CPU stage columns may reflect parallel execution or child processes and cannot be naively added across stages to recover the entire project's CPU-time expense. “Fits attempted” fields in this selected log are not populated with reliable nonzero per-stage totals; model-attempt and classification counts instead come from the dedicated records used in Appendix C. Recorded peak resident memory is a stage-level observation, not a hardware limit.

The total number of recorded model fits can be reconciled exactly by retaining the distinction between the four principal univariate forecasting families and the additional models examined for robustness. Table C.7 summarizes the four main families by target, giving **64,632** records. That subtotal does not include the triggered conditional-variance exercise, the monthly multivariate comparison or the six in-sample three-regime estimates. The corresponding supplementary totals are 2,044, 571 and 6 records, respectively. Table D.4 brings these categories together. All entries are counts of **classified fit records**, not counts of distinct numerical starting values or an independently measured number of processor-level operations.

**Table D.4. Reconciliation of the complete recorded model-fit inventory**

| Estimation family or robustness component | Adequate fits | Fragile fits | Failed fits | Total classified fits |
|---|---:|---:|---:|---:|
| AR, primary benchmark | 18,204 | 21 | 78 | 18,303 |
| ARMA, secondary classical comparator | 15,317 | 27 | 99 | 15,443 |
| Two-state MSAR, principal nonlinear competitor | 5,128 | 10,246 | 69 | 15,443 |
| STAR, principal nonlinear competitor | 2,741 | 12,702 | 0 | 15,443 |
| **Four-family subtotal** | **41,390** | **22,996** | **246** | **64,632** |
| ARMA–GARCH, conditional-variance robustness | 1,882 | 0 | 162 | 2,044 |
| Five-variable monthly VAR, multivariate robustness | 544 | 0 | 27 | 571 |
| Three-state MSAR, full-sample regime-count check only | 0 | 6 | 0 | 6 |
| **All recorded model fits** | **43,816** | **23,002** | **435** | **67,253** |

*Source: Author's computations.* *Note:* The inventory is exhaustive **for the classified model-fit records** used in the completed experiment, including the supplementary families omitted from Table C.7. Each record has one status; a fragile fit is not necessarily an unusable forecast. Summing the four-family subtotal and the three supplementary categories gives exactly 67,253. The six three-state records are full-sample estimates, **not rolling forecasts**. Repeated numerical starting values, diagnostic events, forecast horizons and statistical-test replications are not separate fit records in this table.

The number of fitted-model records also must not be confused with the number of forecasts or statistical tests. A rolling fitted model can supply forecasts at several horizons; forecasts may be omitted from a particular loss comparison because the target is unavailable or the fit has failed. Conversely, one fitted model can generate more than one diagnostic warning. Table D.5 distinguishes the principal observable counts by the unit being counted.

**Table D.5. Supplementary accounting of forecasts, diagnostics and inferential records**

| Workstream and unit of counting | Documented count | Interpretation and boundary |
|---|---:|---|
| Principal AR, ARMA, two-state MSAR and STAR model–target chains | 24 | Six targets for each of four forecasting families |
| Attempted baseline rolling model–origin combinations | 14,108 | 3,527 attempted origins in each of the four families; not additional fit records beyond Table D.4 |
| Attempted baseline forecast–target–horizon observations | 55,268 | 92 distinct model–target–horizon summary cells; some estimates support several horizons |
| Retained baseline forecast–target–horizon observations | 55,152 | Of the 55,268 attempted observations, 116 are not retained for scoring |
| Stationarity and break-sensitive test records | 36 | Augmented Dickey–Fuller, KPSS and Zivot–Andrews entries |
| Tsay nonlinearity test records | 6 | One reported target-level test for each aggregate |
| Smooth-transition linearity and associated selection-test entries | 52 | Delay-specific linearity entries and associated test components; not 52 independent model fits |
| Residual autocorrelation, conditional-variance and distributional diagnostic entries | 126 | Ljung–Box, ARCH–LM and Jarque–Bera tests |
| State-conditioned loss-regression Wald test entries | 134 | Joint and state-slope restrictions attached to the conditional-loss analysis |
| **All five categories of registered diagnostic and conditional-test results** | **354** | 36 + 6 + 52 + 126 + 134; the corresponding 69 state-loss regression rows are a related output, not an additional disjoint test population |
| Primary Harvey–Leybourne–Zu pairwise test rows | 230 | 115 squared-loss and 115 absolute-loss comparisons across eligible targets, horizons and candidates |
| Secondary modified Diebold–Mariano pairwise test rows | 230 | Same squared/absolute-loss output units under the declared secondary method |
| Model confidence set membership records | 368 | Four model-membership entries in each of 92 target–horizon–loss–confidence combinations; **not** 368 independent model confidence set procedures |
| Recorded diagnostic reason-code events | 34,122 | 512 failure-category and 33,610 fragility-category **events**; warnings may repeat within a fit |

*Source: Author's computations.* *Note:* The rows describe **different measurement units** and **must not be added** into a single number of “computations.” The 67,253 total in Table D.4 is the uniquely reconciled count of classified *model-fit records*. Baseline origin and target–horizon counts are descriptive forecast-accounting units; the study also performed the additional robustness exercises already represented in the model-fit register. The 354 registered diagnostic and conditional-test entries do not exhaust the separately tabulated pairwise tests or resampling work. Model-confidence-set membership rows are outcomes of grouped procedures, not the number of distinct bootstrap calculations. The 34,122 reason-code events count diagnostic flags rather than unique fitted models. None of these output counts is a defensible estimate of total floating-point operations, optimizer evaluations, bootstrap replications or cumulative CPU time.

The full proposed three-state rolling extension is deliberately kept outside the reported experiment. As calculated in Section D.3, the proposed extension would require 3,527 further rolling model-origin fits beyond the six in-sample K=3 fits already classified in Table D.4. Those 3,527 **unperformed** fits must never be added to either the 67,253 completed fit records or the 55,268 baseline forecast–target–horizon observations. A future predictive comparison would also require its own forecast scoring, common-date alignment, formal inference and independent numerical-credibility assessment.

## D.6 Auditability and remaining boundaries

The transformed historical input, source-vintage description, final numerical tables, retained/failed forecast rows, estimator specifications, diagnostics and mathematical equations provide multiple avenues for reproducing the published comparisons. The full six-target diagnostics and the key family-specific credibility measures are summarized in Appendices A–C. The main chapters remain self-contained, including definitions of the models, statistical nulls and essential empirical results.

The essential restrictions are substantive: the model comparison is based on one fixed historical data vintage; economic-state labels are retrospective; the estimated regime probabilities do not identify structural monetary or business-cycle shocks; full-sample and selected initial-window parameter estimates are not the sequence of rolling estimates; some loss-test results are numerically degenerate; and global optimality of the nonlinear likelihood is not proven.

No historical cross-correlation figure without uncertainty bands is included in the revised dissertation. The discontinued cross-correlation presentation is not used as inferential evidence. Should a cross-correlation display be introduced during final typesetting, it must have a justified uncertainty representation and properly specified sampling assumptions rather than an unqualified visual reading.

These boundaries ensure that the study can be examined as a transparent econometric forecasting exercise, rather than relying on an unverifiable model ranking or a claim of real-time policy effectiveness.
