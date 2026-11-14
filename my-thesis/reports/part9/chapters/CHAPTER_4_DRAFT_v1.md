# Part II: Testing the Forecast Value of Nonlinear State Dependence

# Chapter 4: Do Nonlinear Forecast Gains Survive? Specification Robustness, Cross-Variable Dynamics and Policy Relevance

Chapter 3 established an important tension between the statistical description of macroeconomic instability and its practical value for forecasting. Nonlinear models sometimes fit the observed history more closely, and initial tests reject selected linear conditional-mean restrictions for unemployment, CPI inflation and changes in the federal funds rate. Yet no two-state Markov-switching autoregression (MSAR) significantly improves on the corresponding autoregressive (AR) benchmark at the one-step horizon under the primary Harvey–Leybourne–Zu test across the six U.S. targets. The most visible reductions in root mean squared error (RMSE), for real GDP and industrial production, occur in samples heavily affected by extraordinary pandemic observations. Other nonlinear estimates display sparse regimes, ill-conditioned parameter covariance matrices, nearly indistinguishable states or unstable forecasts.

These findings do not settle whether the negative general conclusion is robust. A forecasting comparison is conditional on its variable transformations, lag structure, estimation window, forecast distance, information set and treatment of numerical failures. If the linear benchmark is misspecified, nonlinear flexibility might appear to capture dependence that a better linear model would already use. If a rate is differenced unnecessarily, persistence might be lost; if it is retained in levels despite a unit root, apparent regimes could reflect stochastic trends. If a state-switching model is too restrictive, adding another state could reveal a credible process. Conversely, the extra parameters can multiply identification problems without delivering useful forecasts.

The purpose of this chapter is therefore not to search for a configuration that produces a preferred positive or negative answer. It is to confront the baseline inference with named alternative explanations and record whether its interpretation survives. The first six sections examine transformations, lag selection, regime count, horizon and cross-variable information. The second half addresses estimation-window choice, numerical fragility, the boundaries of real-time and mixed-frequency forecasting, and the economic and policy implications of the full evidence.

## 4.1 From Baseline Result to Falsification Test: The Threat-Based Robustness Framework

### 4.1.1 The baseline conclusion as a proposition open to challenge

The baseline experiment provides an observed statistical conclusion, not a proof about the true data-generating process. The null of equal average forecast accuracy was not rejected in favor of MSAR at the one-step horizon for any of the six targets under the declared primary test. It follows that a general nonlinear forecasting advantage has not been established. It does not follow that AR is always optimal, that the models have identical accuracy or that nonlinear macroeconomic mechanisms do not exist. A failure to reject an accuracy null may reflect small effects, volatile loss differentials, weak statistical power or an unsuitable model family.

A useful robustness exercise therefore challenges a precise alternative explanation. This chapter follows five questions in sequence: what the baseline claims, what could make that claim misleading, which specified comparison addresses the threat, what the resulting evidence shows, and how the conclusion changes. The final step is essential. If a model ranking changes but formal inference does not, the finding is *rank-sensitive*, not a statistically supported reversal. If a numerical optimizer returns a likelihood below that of a nested restricted model, the result is *inconclusive*, not evidence that the restricted specification is true. If a p-value changes after modifying the evaluation sample, the change must be associated with the new sample and not silently substituted for the original one.

A distinction is also required between the *robustness of an inference* and the *robustness of a model ranking*. Two specifications can have different RMSE orderings but yield the same non-rejection of equal average loss. A model can likewise rank first on its own valid dates while falling in a pairwise common-date comparison. The relevant objects are respectively the observed sample loss, the paired loss differential and the uncertainty attached to that differential. Their relationship was developed in Section 2.10 and demonstrated for unemployment in Section 3.4. An assertion about forecasting ability must identify which one supports it.

**Table 4.1. Empirical threats to the baseline interpretation and corresponding checks**

| Baseline concern | Alternative explanation | Robustness comparison | Evidential boundary |
|---|---|---|---|
| Nonlinear performance depends on transformation | Unemployment or policy-rate persistence is misrepresented | Levels versus first differences; break-sensitive evidence | Different statistical targets and valid dates must be disclosed |
| A weak classical benchmark creates artificial gains | CPI inflation has omitted own-history lags or volatility effects | AR lag orders 1, 3, 6 and 12; conditional-variance diagnostic | No unperformed direct AR(2)–AR(12) equivalence test |
| Two regimes misrepresent instability | A third recurring state is needed | Full-sample MSAR with two and three states | In-sample identification only, not predictive accuracy |
| A one-step test misses delayed effects | Nonlinear transition matters farther ahead | Monthly horizons 3, 6 and 12; quarterly horizons 2 and 4 | Each horizon is a separate evaluation and significance family |
| Nonlinear forecasts proxy for information in other variables | Own-history models omit cross-variable predictors | Five-variable monthly VAR compared on matched dates | Predictive association, not a structural causal effect |
| Results depend on extraordinary observations or numerical choices | Window choice, extreme forecasts and unstable estimates drive rankings | Alternate windows, coverage and estimation-credibility analyses | Failure and fragility are not equivalent to ordinary forecast loss |

*Source: Author's construction.* *Note:* Each exercise addresses a restricted threat. The comparison of two state counts is not a fifth competitor in the rolling forecasting experiment; conditional-variance diagnostics are not automatically evidence of better conditional-mean forecasts. The second-half robustness checks are presented in Sections 4.7–4.10.

The evidence remains subject to the research design in Chapter 2. The data use the frozen historical vintage described there. The baseline target and model specifications are not redefined after observing their errors. The AR benchmark remains the common reference for formal forecasting comparisons; the Harvey–Leybourne–Zu (HLZ) test remains the primary test when its inference is numerically informative (Harvey et al., 2025). Conventional comparisons can supplement this evidence but do not replace the primary decision merely because they return a smaller p-value.

The role of robustness should be understood conservatively. A positive result in one alternative specification may justify a narrower finding, particularly if it is tied to a specific horizon or transformation. It cannot by itself establish general superiority across aggregate types and economic episodes. Equally, an isolated failure of an alternative test does not validate every baseline assumption. The following sections therefore classify the evidence as supported, qualified or insufficient rather than forcing a single verdict on every model family.

## 4.2 Transformation, Persistence and Structural-Break Threats

### 4.2.1 Economic meaning of the level–difference decision

Transformation is not a cosmetic preprocessing choice. A forecast of the unemployment rate in levels concerns the future level of labor-market slack, while a forecast of its first difference concerns the next change in that rate. An AR model in levels can exploit persistence toward a conditional mean, whereas differencing may place more weight on recent increments and suppress longer-run information. For a variable that is strongly persistent or affected by changes in its typical level, the choice may alter both the apparent need for a nonlinear threshold and the variance of future forecast errors.

The effective federal funds rate raises the converse concern. Its nominal level reflects the policy regime and the historical level of interest rates; its monthly change reflects adjustments made over successive observation dates. Holding the rate in levels when its initial-window diagnostics favor a difference may expose a forecasting equation to persistence that resembles a unit root. Differencing may avoid this difficulty but can discard economically meaningful information about policy-rate levels or the effective lower bound. Neither representation should be declared correct by the ex-post forecast ranking alone.

The baseline decisions reflect the augmented Dickey–Fuller and KPSS evidence summarized in Chapter 3. For unemployment, the initial-window ADF test rejects the unit-root null while KPSS does not reject stationarity; the rate is therefore modelled in levels. For the federal funds rate, ADF does not reject a unit root and KPSS rejects level stationarity; its first difference is used. The Zivot–Andrews tests do not reject their unit-root null for either variable over the initial and full samples, despite the ADF–KPSS evidence for unemployment. These apparently conflicting outcomes concern different hypotheses and alternatives. A break-sensitive test is not a mechanism for reversing a specified target choice solely to obtain better forecasts (Zivot & Andrews, 1992).

To assess the implication of this choice, the models are also fitted to unemployment changes and to the federal funds rate in levels. The resulting forecasts are expressed in level units for comparison of one-step errors. If the transformed model forecasts a first difference, its one-step level prediction is reconstructed by adding the predicted change to the level observed at the forecast origin.

**Equation (4.1): One-step level reconstruction from a difference forecast**

```math
\widehat{x}_{t+1\mid t}^{\,\mathrm{level}}
=
x_t+\widehat{\Delta x}_{t+1\mid t}.
```

For a first-difference representation, this transformation is an identity, not an additional estimated relation. For a level representation, the model forecasts the level directly. Both approaches can be evaluated in the same physical units, but their errors must still be compared on the same target dates. A lower RMSE computed over a different valid sample is not evidence that a transformation is economically superior.

### 4.2.2 Unemployment in differences

**Table 4.2. Alternative one-step transformations: RMSE and primary tests against AR**

| Alternative forecast target | AR RMSE ($n$) | ARMA RMSE ($n$) | MSAR RMSE ($n$) | STAR RMSE ($n$) | MSAR–AR HLZ $p$: squared / absolute |
|---|---:|---:|---:|---:|---|
| Unemployment reconstructed from first differences | 0.563 (701) | 0.680 (696) | 0.776 (703) | 20.747 (703) | 0.3200 / 0.2620 |
| Federal funds rate forecast in levels | 0.426 (555) | 0.520 (620) | 0.456 (577) | 0.974 (626) | 0.2369 / 0.1452 |

*Source: Author's computations.* *Note:* RMSE entries use each model's own valid target dates, which differ substantially for some alternatives. They are therefore not a direct within-row common-date ranking test. HLZ p-values use the model-specific AR-matched intersection, with 701 unemployment and 540 federal funds rate paired observations for MSAR. Errors are measured in percentage-point levels after reconstructing forecasts when needed. Non-rejection is not evidence of equal skill.

Under unemployment differencing, AR produces a one-step level-unit RMSE of 0.563 on 701 valid dates. The corresponding own-valid-sample RMSEs are 0.680 for ARMA, 0.776 for MSAR and 20.747 for STAR. The STAR result is an example of numerical instability rather than a normal increase in forecast error. The baseline unemployment-level comparison in Chapter 3 had placed MSAR first on its own valid sample. The alternative transformation therefore alters the descriptive rankings and weakens any claim that the nonlinear advantage is invariant to the statistical representation of unemployment.

The matched-date results require a further qualification. In the differenced exercise, the MSAR AR-relative out-of-sample $R^2$ is positive on its own pairwise dates, despite the larger own-sample MSAR RMSE. That seeming contradiction is a sample-composition effect, not a mathematical inconsistency. The AR benchmark loses two attempted origins under the differenced specification, while MSAR supplies 703 finite forecasts. The point forecast whose own-valid RMSE is reported for each model is not necessarily evaluated on the same calendar. Therefore, a reader should not infer a pairwise loss ranking by dividing the two own-sample RMSEs.

The primary HLZ comparisons address the paired question directly. For MSAR against AR, the two-sided p-values are 0.3200 under squared loss and 0.2620 under absolute loss. For ARMA they are 0.3470 and 0.7080, while STAR yields 0.4611 and 0.6921. None of these alternatives establishes superior one-step average accuracy against AR. The transformation changes some numerical rankings but not the central lack of inferential support for nonlinear superiority.

The result has a substantive interpretation for the economics of labor markets. An unemployment rate can move slowly in expansions and very rapidly during crises. Differencing changes how a model represents these movements, but it does not make a poorly identified transition or latent regime an automatically better predictor. A successful unemployment model must account both for persistence in ordinary periods and for the possibility of large changes. The present alternatives do not establish that nonlinear flexibility solves this problem.

### 4.2.3 The policy rate in levels

The federal funds rate alternative produces a different pattern. The AR level-model RMSE is 0.426 on 555 valid dates, while MSAR yields 0.456 on 577 dates, ARMA 0.520 on 620 dates and STAR 0.974 on 626 dates. The sample sizes are strikingly uneven, with 71 attempted AR level fits and 49 MSAR level fits failing to produce retained forecasts. A comparison based on raw own-valid RMSE is therefore subject to a stronger selection qualification than the main policy-rate analysis.

On matched dates, MSAR does not outperform AR significantly under HLZ. Its squared-loss p-value is 0.2369, and its absolute-loss p-value is 0.1452. The mean MSAR-minus-AR loss differential is positive for both losses. Thus the available matched evidence provides no support for MSAR superiority; it also fails to establish a statistically significant inferiority under the primary test.

The secondary conventional test illustrates why the distinction between primary and supporting inference matters. Under absolute loss for the federal funds rate in levels, the Diebold–Mariano test with its small-sample modification rejects for ARMA in ARMA's favor ($p=0.0076$), and rejects against MSAR ($p=0.0286$). The corresponding HLZ p-values are 0.1461 and 0.1452, respectively. Those disagreements are reported rather than resolved by changing the chosen test. The instability-aware HLZ comparisons do not establish a significant difference in those pairs under the stated decision rule.

The exercise also constrains the economic interpretation of policy-rate regimes. In the baseline first-difference MSAR, the estimated regime means are indistinguishable. That result does not prove the absence of policy regimes in an economic sense. The level alternative changes the target and produces substantial numerical attrition, yet still provides no robust forecasting advantage against the matched AR benchmark. Together, these findings support treating a switching mean of observed rate changes as an inadequate basis for inferring operationally distinct monetary-policy states.

### 4.2.4 Structural breaks and the limits of stationarity tests

A competing explanation for unstable forecasts is that structural breaks alter the coefficients or mean of an otherwise linear process. In such cases, a switching model may approximate discrete changes without identifying the underlying causes. The problem is particularly relevant for unemployment and interest rates, whose behavior depends on demographic, institutional and policy conditions. A unit-root test and a break-sensitive alternative can disagree over finite samples even when both are calculated correctly. The disagreement motivates robust inference and sensitivity analysis, not an unrestricted search for the transformation that minimizes the final loss.

The Zivot–Andrews results discussed in Section 3.1 do not provide a basis for replacing the selected baseline targets. The unemployment initial- and full-sample statistics have p-values 0.1887 and 0.1691; the federal funds rate counterparts have p-values 0.8113 and 0.3203. Each fails to reject a unit-root null under the procedure's break specification. These non-rejections cannot be interpreted as proof that the series has a stochastic trend, as proof that no break occurred, or as evidence of the best future forecasting transformation. They have a narrower methodological role: the baseline decisions remain conditional on the stated initial-window tests, while the alternatives measure the consequences of relaxing those decisions.

The role of estimation windows is related but not identical. A fixed-length rolling history limits how much earlier information influences a forecast. If coefficients vary over time, a shorter window may adapt more quickly but estimate parameters less precisely. A longer window may reduce estimation variance at the cost of including obsolete relationships. Pesaran and Timmermann (2007) and Rossi and Inoue (2012) show why window choices matter in unstable forecasting environments. Their implication here is to evaluate different declared window lengths in Section 4.7, not to interpret a structural break as established from an apparent change in forecast rankings.

### 4.2.5 October 2025 missing observations and sensitivity of the endpoint

An additional threat is neither a model specification nor a structural break. The frozen historical data vintage lacks the October 2025 observations for the CPI and unemployment series. Chapter 2 specifies last-observation-carried-forward replacement for those two raw levels within the research input, without altering the original source records. Because monthly CPI inflation is formed from a difference of log levels, one missing level affects two consecutive transformed growth observations. The unemployment-level target has one directly affected target observation. Other values can be affected indirectly if imputed observations enter a later lag vector or a rolling estimation window.

The sensitivity exercise therefore distinguishes direct contamination of realized target dates from indirect exposure through estimation histories. A forecast of November 2025 inflation, for example, may be affected by the October carry-forward in the constructed inflation series even though its forecast origin or subsequent regressors are not identical to the directly affected month. Simply deleting the affected observation from a final scoring column cannot remove every path through which the imputation enters a fitted parameter.

On the selected shorter evaluation samples ending before the gap, CPI AR has RMSE 2.950 over 704 dates, compared with the 2.967 on 715 dates in the full selected evaluation. CPI MSAR has 2.951 over the shorter dates and 2.966 in the full sample. These descriptive scores are nearly identical in the relevant scale, although they do not arise from the same collection of observations. For unemployment the corresponding AR RMSEs are 0.555 (692 dates) and 0.551 (703 dates), while MSAR has 0.495 (687 dates) and 0.491 (698 dates). The ordering is unchanged on these own-valid summaries.

These observations support a limited sensitivity conclusion: the two carry-forward values do not plausibly account for the main reported absence of a general nonlinear advantage. They do not establish that imputation has zero effect on every coefficient or forecast, and they do not justify recoding the missing values as original observations. The shortened samples also contain fewer evaluation dates and may have different statistical power. The headline forecasts therefore retain the full specified endpoint while the narrower comparisons are reported as a check on the data limitation.

A different treatment of the missing observations could be justified in another research design, but it would constitute a different historical-input construction. The present exercise evaluates the sensitivity of the stated design without selectively discarding an observation merely because it produces a favorable or unfavorable model result. This conclusion is conditional on the selected historical vintage, not a claim about all possible publication vintages or real-time data availability (Orphanides, 2001).

## 4.3 Lag Structure, Seasonality and Classical-Benchmark Misspecification

### 4.3.1 The risk of attributing omitted linear dynamics to nonlinear regimes

A nonlinear model can appear to improve forecasting because it uses flexibility unavailable to a weakly specified benchmark. If the AR comparator omits meaningful lags, additional state-dependent parameters may partly compensate for that omission. The resulting improvement might reflect a difference in the information used by the conditional means rather than a genuine need for regime changes. This possibility is especially important for inflation, where persistence, policy changes and seasonal patterns may coexist.

The baseline CPI autoregression is AR(2), selected through the initial-window information-criterion and residual-diagnostic procedure described in Chapter 2. Two lags are parsimonious, but parsimony is not proof that a longer autoregression cannot improve a future forecast. Conversely, twelve monthly lags do not automatically capture a stable seasonal mechanism. A seasonal pattern in price changes might be altered by the seasonal adjustment of the underlying CPI index, by changing consumption baskets or by policy shocks. Adding lags raises the number of parameters and may increase estimation variance in fixed-length windows.

The issue is therefore empirical. If a longer classical autoregression consistently improves forecasting, the incremental value attributed to the nonlinear model may be overstated. If the longer autoregression provides no significant advantage, that non-rejection still does not prove that its additional lags are useless. A direct test of the appropriate pair and a sufficiently precise interval estimate would be necessary for stronger conclusions. The robustness exercise is designed to reveal whether an obvious lag-order omission is a plausible explanation, not to prove the optimality of AR(2) against every alternative.

### 4.3.2 CPI AR(1), AR(3), AR(6) and AR(12)

The lag sensitivity comparison evaluates four fixed CPI autoregressive orders, 1, 3, 6 and 12, under the same historical forecast setup. The constructed comparison uses 714 dates common to the four reported candidate specifications, from February 1967 through August 2026. The AR(12) model has an unsuccessful fit at one earlier eligible origin; that failed forecast is not included in the scored 714-date panel. The baseline AR(2) instead has 715 valid dates in its main comparison. Those two calendars differ and their raw RMSEs should not be presented as if they formed one perfect matched test.

**Table 4.3. CPI inflation one-step sensitivity to autoregressive lag order**

| Classical model | RMSE on candidate common dates | MAE on candidate common dates | Valid dates |
|---|---:|---:|---:|
| AR(1) | 3.0752 | 2.1938 | 714 |
| AR(3) | 2.9580 | 2.0725 | 714 |
| AR(6) | 2.9690 | 2.0934 | 714 |
| AR(12) | 2.9675 | 2.0796 | 714 |

*Source: Author's computations.* *Note:* The table reports four candidate AR orders on a common 714-date evaluation calendar. The baseline AR(2), with RMSE approximately 2.967 on its own 715 dates, is not part of the four-model matched table. These differences are descriptive; no direct AR(12) versus AR(2) test of predictive superiority or equivalence was conducted.

The observed RMSE ranking within this four-candidate panel favors AR(3), which has RMSE 2.9580. AR(6) and AR(12) have very similar RMSEs of 2.9690 and 2.9675, while AR(1) is less accurate in squared-error terms. Their MAEs produce a similar but not identical ordering: AR(3) is lowest at 2.0725, and AR(12) follows at 2.0796. The numerical differences between the longer AR alternatives are small compared with the historical variation in CPI inflation errors.

The main AR(2) model has a one-step own-valid RMSE of approximately 2.967 over 715 observations. The descriptive proximity between that value and the AR(12) value of 2.9675 is suggestive but not a matched-date finding. The distinction matters for an exact methodological claim. Without a direct AR(2)–AR(12) loss differential on the same 714 dates, neither its estimated mean difference nor its uncertainty has been formally established within this exercise. Therefore, the appropriate conclusion is that **the available robustness evidence does not establish a forecasting benefit from adopting twelve lags**, not that twelve lags are unnecessary or that AR(2) and AR(12) have equal accuracy.

The candidate-versus-AR(1) comparisons provide a more limited inferential check. Under the primary HLZ test for squared loss, the two-sided p-values are 0.1009 for AR(3), 0.2567 for AR(6) and 0.3274 for AR(12). None rejects at the nominal 5% level. Under absolute loss, however, AR(3) improves significantly on AR(1), with HLZ $p=0.0129$ and a negative mean loss differential. AR(6) and AR(12) have absolute-loss p-values 0.1004 and 0.1012. This result confirms that lag selection and the loss function can change the inferential conclusion. It does **not** test the main AR(2) against AR(12).

The secondary conventional test also differs from HLZ. For AR(3) against AR(1) under squared loss, the conventional modified test rejects with a p-value near 0.0116, while HLZ yields 0.1009. Such disagreement is compatible with instability in relative forecast-loss means. The primary HLZ decision is retained because the study seeks inference robust to that concern. One cannot claim stronger evidence for a preferred lag order by switching between available tests after observing their significance.

### 4.3.3 A seasonal lag is not a seasonality test

Twelve months is an intuitive lag choice for a monthly variable, but an AR(12) forecast comparison is not a formal test of seasonal integration or deterministic seasonality. The input CPI is already a seasonally adjusted official series. The presence of lag twelve in an unrestricted autoregression would not, by itself, establish an annual seasonal economic mechanism. Nor would the absence of improved RMSE prove that all forms of seasonal dependence are absent.

Seasonality may enter through changing measurement conventions, recurring administrative price changes, seasonal adjustment errors or time-varying economic responses. These mechanisms require different model restrictions and, in some cases, different data. The present analysis tests whether an extended own-history approximation helps one-step CPI forecasts under the fixed rolling-window design. It is appropriately narrower than a comprehensive empirical investigation of seasonal inflation dynamics.

The fixed-window dimension is also relevant. Adding ten coefficients to move from AR(2) to AR(12) consumes estimation degrees of freedom. Even if some population coefficients were nonzero, their finite-sample estimation noise might offset a potential bias reduction. A small or absent forecast gain therefore has at least two possible explanations: little additional predictive information, or information too difficult to estimate precisely in the chosen window. Distinguishing the two would require further evidence. The results support neither a claim of statistical equivalence nor a universal rejection of longer autoregressions.

### 4.3.4 Conditional heteroskedasticity is a different challenge

An omitted conditional-variance process may also distort the interpretation of nonlinear mean dynamics. Time-varying forecast uncertainty can produce large innovations in clusters. A switching mean may then isolate periods of high volatility as if they were distinct average-growth or average-inflation regimes. Engle's (1982) ARCH framework and Bollerslev's (1986) generalized specification show how conditional variance can change independently of the conditional-mean equation.

The initial-window ARCH–LM screens on the selected ARMA residuals trigger a separate variance diagnostic for CPI inflation, unemployment and the federal funds rate change. Their p-values are approximately $1.36\times10^{-12}$, $1.82\times10^{-6}$ and $0.0209$, respectively. They do not trigger the same diagnostic for GDP, industrial production or M2 under the initial-window rule. This distinction is not in conflict with Chapter 3, which reports full-sample conditional-variance tests across fitted model families. An initial-window trigger and a full-sample residual test use different samples and can yield different rejections.

In the triggered ARMA–GARCH(1,1) exercise, the average estimated volatility persistence, measured as the sum of the ARCH and GARCH coefficients, is approximately 0.83 for CPI, 0.55 for unemployment and 0.97 for the policy-rate target. These figures describe the conditional-variance component, not the persistence of the conditional mean and not the probability of an economic recession. For the policy rate, a persistence value close to one is a reminder that conditional variance may respond slowly after a large innovation even when the mean target is a first difference.

The fitted GARCH exercise also yields conditional-mean forecasts numerically different from those of the selected ARMA. This distinction should not be concealed: estimating a variance process jointly can alter the estimated mean parameters and hence the point forecast. Nevertheless, the GARCH specifications were not included as an additional competitor in the primary four-family forecast comparison or in its model confidence sets. Their role is to evaluate whether conditional heteroskedasticity is substantively present and whether a mean-only interpretation of nonlinear regimes is incomplete. They do not provide an independently established forecast-accuracy victory over AR or MSAR.

For CPI, the mean point forecasts from the ARMA–GARCH exercise have an RMSE of approximately 2.817 on its 688 valid origins, compared with about 2.970 for the selected ARMA forecast on those same reported origins. That descriptive difference suggests the variance specification may matter for some point estimates. It does not support a formal predictive-superiority claim within the main experiment because the relevant inference against the declared benchmark was not performed as part of this exercise. For unemployment the corresponding RMSEs are approximately 0.457 and 0.449, and for the policy rate approximately 0.3234 and 0.3232. These comparisons remain supplementary descriptions of a different model exercise, not modifications of the primary model ranking.

The broader implication is that nonlinear dependence in the conditional mean, conditional variance and state-transition probabilities are not interchangeable phenomena. A residual ARCH rejection does not establish that MSAR or STAR can improve the expected level or growth rate. Conversely, a fragile MSAR mean model does not demonstrate that a GARCH variance model is the correct structural explanation of an economic shock. Chapter 4 separates these dimensions to avoid explaining all instability through one statistical mechanism.

## 4.4 Two Regimes or More? Testing the Economic Meaning of Latent-State Structure

### 4.4.1 Why a third state is a substantive hypothesis

The two-regime Markov-switching autoregression is a deliberately restricted representation of changes in the conditional mean. A two-state process distinguishes two distributions, but the macroeconomic environment may contain more than two recurring configurations. Inflation may have periods of low and moderate inflation in addition to a high-inflation episode. Output can display ordinary expansion, severe contraction and rapid recovery. Monetary variables may behave differently during effective-lower-bound periods, disinflations and normal policy adjustments. These possibilities are economically plausible, but they do not establish that three distinct regimes can be identified from the observed sample.

A third state adds flexibility in regime means and the transition matrix. It also adds parameters, starting-value sensitivity and the possibility of partitioning a rare extreme observation into its own state. A lower information criterion may arise because this extra state isolates a small group of observations rather than representing a recurrent economic process. The credibility of a three-state fit must consequently be assessed alongside its likelihood improvement.

The regime-count exercise is restricted to one full-sample fit of MSAR(2) and MSAR(3) for each of the six targets. Both representations share the same conditional-mean family, a common set of autoregressive coefficients and the maintained common-variance assumption; the larger model permits three rather than two regime means. No rolling MSAR(3) forecasts are estimated, so no three-state out-of-sample RMSE, forecast-ranking conclusion or predictive-accuracy test follows from this exercise.

The comparison uses an information-criterion difference defined in a consistent direction:

**Equation (4.2): In-sample BIC difference between three- and two-state models**

```math
\Delta\mathrm{BIC}_{3-2}
=
\mathrm{BIC}_{K=3}
-
\mathrm{BIC}_{K=2}.
```

A negative value favors three regimes in terms of the reported penalized likelihood; a positive value favors two. The sign is not a likelihood-ratio test, a measure of structural truth or evidence of forecast superiority. Furthermore, the usual regular chi-square approximation to a regime-count likelihood-ratio statistic is not justified automatically because transition probabilities and regime parameters can be unidentified or lie on a boundary under the restricted model (Cho & White, 2007; Qu & Zhuo, 2021).

### 4.4.2 What the additional state achieves statistically

**Table 4.4. Full-sample MSAR regime-count comparison and credibility assessment**

| Forecast target | BIC, two states | BIC, three states | $\Delta\mathrm{BIC}_{3-2}$ | Three-state credibility qualification |
|---|---:|---:|---:|---|
| Real GDP growth | 1,775.04 | 1,744.68 | −30.36 | Two states contain approximately one effective observation each; boundary transitions and unusable covariance |
| CPI inflation | 4,879.14 | 4,823.33 | −55.81 | A 2.24% occupancy state falls below the credibility threshold |
| Unemployment rate | −142.46 | 68.08 | +210.54 | Inconclusive likelihood comparison; sparse states, boundary transitions and singular covariance |
| Industrial production growth | 7,289.93 | 7,222.55 | −67.37 | Rare states, boundary transitions and unusable covariance |
| Federal funds rate change | 1,078.36 | 581.20 | −497.16 | Two rare states, one with approximately two effective observations, and boundary transitions |
| M2 growth | 4,460.85 | 4,390.07 | −70.78 | One state contains fewer than eight effective observations; boundary transitions |

*Source: Author's computations.* *Note:* All figures describe full-sample in-sample estimation. A negative difference favors three states under BIC only; it does not demonstrate a credible additional economic state. The unemployment three-state likelihood is below the two-state likelihood despite nesting, indicating that its numerical solution cannot be used as a valid global optimum for regime-count inference. No three-state out-of-sample forecasts were estimated.

The table offers a paradox that is only apparent. For five targets, BIC favors the estimated three-state fit. Nevertheless, none of the six three-state solutions satisfies the specified credibility conditions for an interpretable additional regime. Thus the reported penalized likelihood improvement cannot be equated with identification of a recurrent third macroeconomic state. The exception in the BIC sign, unemployment, is not evidence that two states are definitively superior; it reflects an unresolved numerical likelihood problem discussed below.

For GDP, the three-state fit divides the sample into one dominant state and two states each accounting for approximately one effective observation. Its transition estimates are on problematic boundaries, and its covariance matrix does not permit reliable uncertainty assessment. Adding a third regime therefore does not repair the sparse-state concern documented for the two-state model in Chapter 3. It partitions the history more finely around very unusual observations while making the state interpretation harder to defend.

Industrial production behaves similarly. The three-state solution assigns approximately five effective observations to one state and about twenty-one to another, with nearly all remaining observations in the dominant state. Even the state with slightly more than twenty effective observations remains below the minimum 5% occupancy requirement, and the fit contains boundary and covariance warnings. Its lower BIC cannot support an assertion that two distinct, recurrent exceptional production states have been identified.

For M2 growth, one additional state contains fewer than eight effective observations, accompanied by boundary transition behavior. The model may describe major shifts in money growth, but the evidence is too concentrated to estimate the dynamics of another recurring state reliably. The result does not warrant a causal label such as a separate money-demand, monetary-expansion or liquidity regime. Such interpretations require economic restrictions or independent identification evidence not provided by the present likelihood.

The federal funds rate produces the largest raw BIC improvement, yet its three-state fit allocates approximately two effective observations to one state and fewer than twenty to another. This result is instructive precisely because the magnitude of a BIC difference can be misleading when viewed without state credibility. A flexible latent-state likelihood may capture unusual rate changes more closely while offering no stable estimates of recurrent transition probabilities. The original two-state change-rate model already collapses to indistinguishable regime means. The third state does not transform that specification into a credible, economically distinct policy-state model.

### 4.4.3 The qualified inflation result

CPI inflation is the most interesting counterexample to the claim that all extra states merely isolate single extreme observations. The three-state solution has effective observation counts of approximately 21, 848 and 84, corresponding to occupancy shares near 2.24%, 88.97% and 8.79%. Its covariance calculation is usable, and the estimated regime means are more readily distinguishable than in several of the other targets. The additional state therefore reflects more than one isolated observation.

Nevertheless, the smallest occupancy share fails the stated 5% criterion. Twenty-one effective observations in a sample of approximately 953 observations are not sufficient by themselves to establish a well-populated recurrent third state. This is a threshold-based credibility judgment, not a formal hypothesis test that the third state does not exist. The analysis remains cautious because the estimated likelihood can improve by assigning a relatively small group of unusual inflation observations to another conditional mean.

This qualified result should be read alongside the two-state CPI model. Chapter 3 found that its lower- and higher-mean regimes were more interpretable than the corresponding regimes for most other targets. The three-state fit does not disprove that descriptive finding. Rather, it asks whether a third regime is necessary and reliably identified. The present criteria do not support that stronger conclusion. Thus the two-state CPI description can remain informative while its regime count remains a maintained modelling restriction rather than an empirically certified truth.

### 4.4.4 Unemployment: why an apparently favorable two-state BIC is not decisive

The unemployment comparison is a distinct identification issue. The estimated two-state log-likelihood is approximately 102.04, while the obtained three-state log-likelihood is only 13.88. The latter is lower by about 88.16 likelihood units. A larger unconstrained model should be capable of reproducing the restricted model's likelihood in principle when the parameter spaces are nested or can approach the restricted solution. Obtaining a substantially inferior value in the larger specification therefore signals a local optimum or an unsuccessful search over the larger parameter space, not that the data establish the restricted model as superior.

Consequently, the positive unemployment $\Delta\mathrm{BIC}_{3-2}$ in Table 4.4 cannot be interpreted as a meaningful comparison of correctly maximized likelihoods. The reported three-state fit also has a singular covariance estimate, boundary transition probabilities and two sparsely occupied states. These warnings reinforce the conclusion that the three-state unemployment estimate is not credible. But they do not repair the global-optimization uncertainty.

The correct classification for unemployment is **inconclusive**, not “two regimes validated.” The two-state fit itself is fragile, with near-absorbing transitions described in Chapter 3. One weak candidate and one unreliable larger-model solution cannot establish an optimal number of economic states. Nor can the researcher improve the evidential status merely by treating an optimizer's convergence flag as proof of a global maximum. For hidden-state likelihoods, the shape of the likelihood and dependence on starting values are part of the scientific limitation.

This qualification matters for the thesis's broader conclusion. The failure to identify a credible third state does not prove that a true unemployment process has precisely two regimes. It means the available full-sample exercise does not supply sufficiently reliable evidence for increasing the maintained state count. The forecasting comparison in Chapter 3 therefore retains the originally specified two-state MSAR without making a stronger claim about the true number of regimes.

### 4.4.5 What can be concluded about the regime-count restriction?

The six comparisons support three propositions. First, information criteria alone are insufficient for assessing an extra state when its occupancy or transition probabilities are close to problematic boundaries. Second, the case for a credible three-state description is not established for any target under the stated requirements, with unemployment additionally constrained by a non-global likelihood solution. Third, **failure to justify three states is not validation of two states**, especially where the two-state estimate is itself fragile.

The exercise provides an in-sample check of whether the two-state assumption is overly restrictive. It does not assess whether three regimes would generate better forecasts, because no rolling three-state forecasts were estimated. It also does not settle whether other forms of nonlinear dependence, alternative state-transition structures or economic switching variables could be more identifiable. The question answered is intentionally narrower: does this three-state version of the stated MSAR family produce a credible additional historical state? The available evidence does not establish one.

This conclusion is especially important for economic interpretation. A regression regime is a property of a fitted conditional distribution. It cannot be given a policy, recession or structural label without independent evidence. The presence of three estimated mean levels does not identify three policy regimes, three monetary environments or three stages of the business cycle. Preserving that distinction prevents statistical flexibility from becoming unsupported causal storytelling.

## 4.5 Does Model Ranking Change with the Forecast Horizon?

### 4.5.1 Why forecast distance may change the value of nonlinear dynamics

One-step accuracy is a natural primary objective, but it is not the only horizon that matters for economic planning. Budget decisions, monetary-policy transmission, labor-market expectations and investment choices can depend on forecasts several months or quarters ahead. A nonlinear model may identify a state transition that has little effect on the immediately following observation but accumulates into a larger difference under repeated forecasting. Conversely, a small parameter error can propagate over several iterations and make a complex model increasingly unstable. It is therefore possible for a model's comparative performance to change with the forecast horizon.

The robustness horizons are 3, 6 and 12 months for CPI inflation, unemployment, industrial production, changes in the federal funds rate and M2 growth; for quarterly GDP they are 2 and 4 quarters. The baseline remains one month or one quarter respectively. Models are re-estimated under their specified rolling windows, and the selected nonlinear transition structure is iterated to the required horizon. The procedure evaluates the same transformed target definitions rather than replacing a growth-rate target with an accumulated level change.

A critical comparability issue arises from the evaluation calendar. A twelve-month-ahead forecast issued at origin $t$ has a target date later than a three-month-ahead forecast issued at the same origin. Because the historical sample has a fixed final date, the number of valid target observations also changes with horizon. The horizon-specific RMSE values are therefore not directly comparable as if each used the same realized targets. Within each horizon, however, a competitor and AR can be compared on their common valid target dates.

The inferential rule remains the two-sided HLZ test of average accuracy for each pair and loss. A small p-value at one horizon can support a horizon-specific finding if the inference is usable. It cannot be read automatically as a finding about all horizons or as a reason to rewrite the one-step baseline. Moreover, testing many horizons, targets and loss functions increases the chance of nominally significant results. That concern is addressed explicitly after the numerical comparisons.

### 4.5.2 The pattern across the six targets

**Table 4.5. Selected longer-horizon MSAR forecasts relative to AR**

| Forecast target | Horizon | AR RMSE | MSAR RMSE | AR-relative $R^2_{\mathrm{OOS}}$ | HLZ $p$, squared loss |
|---|---:|---:|---:|---:|---:|
| Real GDP growth | 2 quarters | 4.601 | 4.393 | 0.088 | 0.3727 |
| Real GDP growth | 4 quarters | 4.459 | 4.348 | 0.049 | 0.4253 |
| CPI inflation | 3 months | 3.460 | 3.473 | −0.007 | 0.7065 |
| CPI inflation | 6 months | 3.656 | 3.628 | 0.015 | 0.3564 |
| CPI inflation | 12 months | 3.949 | 3.865 | 0.042 | **0.0329** |
| Unemployment rate | 3 months | 0.942 | 1.064 | −0.129 | 0.3773 |
| Unemployment rate | 6 months | 1.165 | 1.410 | −0.538 | 0.3158 |
| Industrial production growth | 3 months | 13.273 | 12.126 | 0.165 | 0.2677 |
| Industrial production growth | 6 months | 12.663 | 12.111 | 0.085 | 0.2939 |
| Federal funds rate change | 6 months | 0.512 | 0.511 | 0.003 | 0.1878 |
| M2 growth | 12 months | 6.216 | 6.311 | −0.031 | 0.2904 |

*Source: Author's computations.* *Note:* RMSEs use each model's own valid dates; the AR-relative $R^2$ and HLZ tests use the paired dates appropriate to the stated horizon. Bold is a nominal 5% rejection; it is not adjusted for multiple comparisons. The full matrix, including all omitted horizons, absolute-loss tests, ARMA and STAR, is reported in Appendix C. Each horizon has a distinct set of eligible target dates.

The results are heterogeneous. For GDP, MSAR preserves a descriptive squared-error advantage at two and four quarters, with out-of-sample $R^2$ of 0.088 and 0.049. These figures are smaller than the one-quarter baseline value near 0.292, and the primary squared-loss tests do not reject at either longer horizon. Thus increasing the horizon does not create formally established GDP forecast superiority. It also does not imply that a state-dependent model can predict the timing of a recession several quarters in advance.

For industrial production, the MSAR descriptive advantage persists at three and six months but diminishes with horizon. At twelve months, the AR-relative squared-error improvement is approximately zero and slightly negative in the reported results. None of the corresponding HLZ tests establishes a gain. This pattern is consistent with a model that captures some short-run unusual movements but does not generate a stable long-run advantage. That interpretation is descriptive, not a structural account of industrial production dynamics.

Unemployment moves in the opposite direction. Its own-valid AR RMSE is lower than MSAR at three and six months, and the matched MSAR AR-relative $R^2$ is negative, approximately −0.129 and −0.538. At twelve months the matched $R^2$ is still more negative, approximately −0.952. The longer-horizon performance therefore weakens any argument based on MSAR's smallest own-sample one-step RMSE. Yet even these larger numerical disadvantages should not be confused with a formal rejection without the corresponding test. The primary tests at these horizons do not establish a statistically significant difference under the stated squared-loss procedure.

The two monetary targets show very limited positive evidence. Changes in the federal funds rate are forecast almost equally in descriptive RMSE terms by AR and MSAR at three and six months, and the matched out-of-sample $R^2$ is close to zero. M2 growth generally shows negative MSAR AR-relative values at longer horizons, including approximately −0.031 at twelve months. Neither case supports a robust benefit of the estimated switching mean under the primary inference. This is consistent with the weak regime identification noted in the full-sample fits, but it remains a forecast-performance result conditional on the chosen transformations.

### 4.5.3 The isolated twelve-month CPI inflation finding

CPI inflation contains the one meaningful exception to the general lack of nonlinear-over-AR rejection. At the twelve-month forecast horizon, MSAR has an RMSE of approximately 3.865 compared with AR's 3.949 on 704 common forecast dates. The matched out-of-sample $R^2$ is approximately 0.042, indicating a 4.2% reduction in mean squared forecast loss relative to AR on that calendar. Under the primary HLZ test, the two-sided squared-loss p-value is 0.03288. Under absolute loss, the p-value is 0.00444 and the competitor-minus-AR loss differential is negative. Both are nominally significant at 5%, and both favor MSAR for that target and horizon.

This finding should neither be ignored nor exaggerated. The reduction in RMSE is modest in absolute terms, and it occurs at a robustness horizon rather than the one-month baseline. The result offers some evidence that a two-state description can matter more for medium-term CPI inflation than for the next monthly observation. It does not establish that nonlinear dynamics generally improve CPI forecasts or that the estimated high-inflation state identifies a policy mechanism.

The distinction between squared and absolute loss is also useful. The nominal rejection appears under both, so it does not depend entirely on a single loss function. Nevertheless, the broader empirical exercise includes six targets, multiple horizons, several models and two losses. Even without changing the primary test, the family of comparisons raises a multiple-testing problem. An isolated p-value below 0.05 is more likely to occur somewhere in a large test family than in a single predeclared comparison.

A transparent sensitivity calculation applies Holm's (1979) step-down family-wise correction to the 46 available MSAR-versus-AR HLZ comparisons spanning the six targets, their eligible horizons and both loss functions. This is a **supplementary multiplicity sensitivity**, not a replacement for the nominal primary testing convention. Under this adjustment, the CPI twelve-month absolute-loss p-value rises from 0.00444 to approximately 0.204, and the squared-loss p-value rises from 0.03288 to 1.000. Neither survives a 5% family-wise criterion. The adjustment does not prove the horizon-specific effect is zero. It shows that the nominal significance does not remain robust when the stated family of related comparisons is considered.

The distinction is scientific rather than rhetorical. The unadjusted primary result is a valid description of the particular pairwise test. The step-down sensitivity asks a different question: would the same result remain significant while controlling the family-wise chance of at least one false rejection across the 46 tested hypotheses? Because it does not, the appropriate conclusion is **qualified horizon-specific evidence**, not a systematic nonlinear forecasting advantage.

The associated CPI MSAR has a relatively interpretable two-state fitted distribution, as discussed in Chapter 3. This gives the twelve-month result economic interest, but it does not eliminate the multiplicity concern or the need for future independent validation. A model that records a modest gain in one historical horizon could still fail when the inflation process, policy response or publication vintage changes. Thus the relevant proposition to carry forward is narrow: the twelve-month CPI result is a nominal positive exception that does not survive the broader multiple-testing sensitivity.

### 4.5.4 Why the horizon exercise does not revise the primary question

The horizon analysis clarifies the scope of the baseline result. One-step forecasting is not a universal proxy for all planning horizons. The relative performance of MSAR changes with distance, sometimes improving and sometimes deteriorating. A broad negative claim that *no* nonlinear model ever improves any forecast would therefore be too strong. Yet the evidence also does not support the opposite claim that longer horizons reveal a systematic advantage. The only nominally supported nonlinear-over-AR finding is confined to CPI at twelve months and is weakened by multiplicity.

The distinction between selecting a horizon and evaluating a horizon is consequential. A policymaker may need a particular lead time because of transmission lags, budgeting cycles or institutional decisions. The research can evaluate that lead time, but it should not choose the lead time after seeing where a model performs best and then present it as if it were selected independently. The declared horizon grid permits a disciplined comparison. The subsequent interpretation must preserve the nominal versus multiplicity-sensitive distinction.

Finally, horizon dependence does not reveal causality. An MSAR model may show lower CPI forecast loss at twelve months because its estimated persistence and state probabilities improve statistical prediction over that distance. This does not show that manipulating monetary policy would change inflation in the manner predicted by its transition equation. Causal policy inference requires identification of policy shocks, counterfactual responses and a decision criterion not supplied by a point-forecast loss comparison.

## 4.6 Does Cross-Variable Information Explain Apparent Nonlinear Gains?

### 4.6.1 Why a univariate model may be missing relevant information

The baseline AR, ARMA, MSAR and STAR models forecast each target primarily from its own history. That design isolates the contribution of alternative functional forms. It does not imply that inflation, unemployment, output, interest rates and money are economically independent. An autoregression can miss predictive information contained in other aggregates, while a nonlinear state process may partly proxy for their joint evolution. A test of cross-variable information is therefore a natural challenge to the claim that greater own-history nonlinearity is what matters most.

A vector autoregression (VAR) provides a parsimonious way to introduce lagged values of other variables without imposing a fully specified structural model. It represents the conditional mean of each variable as a linear function of its own past and the past of the other variables. The basic first-order monthly system used for the robustness comparison can be written as follows.

**Equation (4.3): Five-variable monthly first-order vector autoregression**

```math
\begin{aligned}
\mathbf y_t
&=\mathbf c+\mathbf A_1\mathbf y_{t-1}
+\mathbf u_t,\\
\mathbf y_t
&=\begin{pmatrix}
\pi_t & u_t & g_t^{IP} & \Delta i_t & g_t^{M2}
\end{pmatrix}^{\!\top}.
\end{aligned}
```

Here $\pi_t$ is CPI inflation, $u_t$ the unemployment rate, $g_t^{IP}$ industrial production growth, $\Delta i_t$ the federal funds rate change and $g_t^{M2}$ M2 growth, all at monthly frequency under their baseline transformations. The vector of innovations $\mathbf u_t$ is not an identified structural economic shock. The unrestricted coefficients in $\mathbf A_1$ describe lagged conditional associations, not causal policy multipliers.

Quarterly GDP is not interpolated to monthly observations for this exercise. Replacing observed GDP with a mechanical monthly interpolation would introduce constructed variation and mix forecast-information questions with an arbitrary frequency-conversion assumption. The VAR therefore covers only the five native monthly targets, preserving the baseline GDP analysis as a separate univariate comparison.

### 4.6.2 VAR selection, stability and the common evaluation calendar

The linear VAR lag order is selected from candidate orders one through three, subject to the stated stability conditions. The first-order model has the lowest initial-window BIC, approximately 4,195.56, compared with 4,197.21 for two lags and 4,256.67 for three. Its estimated companion-matrix maximum modulus is approximately 0.978, below one in the selected initial window. This supports using VAR(1) for the specified robustness comparison. It does not establish that its coefficients remain constant over the entire historical sample.

The common-date construction is essential. A multivariate system requires each of the five relevant lagged variables to be available and its estimated dynamics to satisfy the stability rule. Of the 571 attempted VAR forecast origins in the relevant evaluation, 27 are excluded because the VAR stability condition is not satisfied. Additional missing model forecasts lead to target-specific intersections when the VAR is compared with all four univariate families. The common-date count is 544 for CPI, industrial production and M2, 527 for unemployment and 538 for the federal funds rate.

These intersections must be used to avoid a misleading comparison. For example, the unemployment AR baseline has a one-step own-valid RMSE around 0.551 over 703 dates in Chapter 3. Its RMSE on the smaller five-model VAR common sample is approximately 0.613. The change does not mean that re-estimating AR within the VAR exercise has inherently worsened the model; it reflects a different selection of dates and, in some instances, the more constrained common evaluation calendar. Similarly, a VAR RMSE should not be set against an unrelated AR score and read as a causal performance gain.

### 4.6.3 Forecast evidence when the five model families share dates

**Table 4.6. One-step five-variable VAR comparison on target-specific common dates**

| Monthly target | Common dates | AR RMSE | MSAR RMSE | VAR RMSE | VAR–AR HLZ $p$: squared / absolute |
|---|---:|---:|---:|---:|---|
| CPI inflation | 544 | 2.925 | 2.936 | 3.011 | 0.1470 / 0.0662 |
| Unemployment rate | 527 | 0.613 | 0.550 | 0.493 | 0.3464 / 0.8107 |
| Industrial production growth | 544 | 14.207 | 12.196 | 12.983 | 0.3460 / 0.5569 |
| Federal funds rate change | 538 | 0.484 | 0.491 | 0.498 | 0.4549 / **0.0036** |
| M2 growth | 544 | 5.052 | 5.084 | 4.820 | 0.4755 / 0.4072 |

*Source: Author's computations.* *Note:* All descriptive columns within a row use dates common to AR, ARMA, MSAR, STAR and VAR. The reported HLZ p-values compare VAR against AR under squared and absolute loss. Bold identifies a nominal 5% rejection; in the federal funds rate row, the positive VAR-minus-AR absolute-loss differential favors AR. No reported p-value supports VAR forecast superiority over AR.

The VAR comparison does not provide a general alternative explanation for the nonlinear results. For CPI inflation, VAR has a higher RMSE than AR on their 544 common dates. The squared-loss HLZ test does not reject, while the absolute-loss p-value of 0.0662 remains above the 5% threshold. The available evidence therefore does not support a gain from lagged cross-variable predictors for next-month inflation under this simple linear specification.

Industrial production shows a more favorable descriptive VAR outcome than AR: RMSE falls from approximately 14.207 to 12.983. Yet the MSAR RMSE on the same common calendar is lower still, approximately 12.196, and the VAR–AR squared-loss HLZ p-value is 0.3460. This is a useful example of why a strong descriptive improvement is not a significant result. It also shows that introducing cross-variable information does not necessarily remove the descriptive advantage observed for MSAR, even though neither advantage is established by the relevant primary test.

For unemployment, the VAR has the lowest descriptive RMSE among the five families on the 527 target dates common to the exercise, approximately 0.493. The corresponding AR RMSE is 0.613, and MSAR's is 0.550. The VAR's AR-relative out-of-sample $R^2$ is approximately 0.353, suggesting a noticeable squared-error reduction on that specific calendar. However, the primary squared-loss p-value is 0.3464, and the absolute-loss p-value is 0.8107. Thus the numerical gain does not establish significant superiority. It must also not be compared directly with the own-valid unemployment rankings from Chapter 3, which use different dates and numbers of retained forecasts.

M2 growth also favors VAR descriptively on the common calendar, with RMSE 4.820 compared with AR's 5.052. The squared-loss HLZ p-value is 0.4755, and the absolute-loss p-value is 0.4072. There is therefore no formal evidence that the added linear predictors deliver a significant improvement for M2. The result does, however, indicate that a more complete information set can alter a ranking even when none of the models meets the inferential threshold.

The federal funds rate provides the clearest inferential result in the opposite direction. Under absolute loss, the VAR–AR comparison rejects at $p=0.0036$ and the positive mean loss differential favors the AR benchmark. Its squared-loss comparison does not reject ($p=0.4549$). Thus the VAR is significantly worse than AR under one nominal loss criterion, not significantly better. This loss-specific finding reinforces the point that added information is not costless: more coefficients and cross-variable forecasts can increase estimation variance or incorporate relationships that do not remain stable.

### 4.6.4 What the VAR evidence can and cannot explain

The VAR results address an informational alternative to the baseline univariate comparison. If MSAR appeared useful only because it captured information from other macroeconomic variables, a five-variable linear VAR might have performed consistently better than the AR and perhaps removed the apparent nonlinear descriptive advantage. The evidence does not support such a simple explanation. In some targets the VAR improves the descriptive RMSE, but it does not provide statistically established superiority over AR, and for the policy rate it is nominally worse under absolute loss.

This does not prove that cross-variable information has no predictive content. A VAR(1) is one finite-dimensional linear specification selected from a short candidate grid. It cannot exhaust all possible factor, Bayesian, time-varying-parameter or nonlinear multivariate relationships. It is also estimated under the historical data vintage and the fixed rolling-window constraints. More flexible multivariate approaches may behave differently; testing them would require a separate empirical design and further protection against data mining.

The causal interpretation is narrower still. A coefficient linking the lagged federal funds rate to inflation, for example, is not a monetary-policy treatment effect. A forecast reduction when an additional lagged variable is included does not establish the effect of an exogenous intervention in that variable. The VAR innovations need not be structural shocks, and contemporaneous economic responses are not identified through the unrestricted predictive equations. Consequently, the present results inform model-selection discipline but cannot determine optimal interest-rate decisions or estimate the welfare benefits of policy intervention.

The five-variable robustness exercise also does not turn this dissertation into a nowcasting study. The forecasts use lagged monthly observations in a fixed historical vintage. They do not reproduce each historical release calendar, forecast missing current-quarter GDP, or update predictions as economic releases arrive within the month. The distinction between predicting a future target and constructing a timely estimate of the present state is examined in Section 4.8.

Together, Sections 4.2–4.6 establish the main robustness finding of the first half of this chapter. Alternative unemployment and interest-rate transformations do not reveal a supported nonlinear advantage. The CPI lag exercise shows sensitivity to specification and loss but provides no direct evidence that AR(12) improves on the declared AR(2). Three-state MSAR fits offer better penalized historical likelihoods for most targets without identifying credible additional regimes; unemployment remains inconclusive because the larger likelihood is unreliable. Longer forecast horizons reveal one nominal MSAR gain for twelve-month CPI inflation that does not survive the family-wise sensitivity. A five-variable VAR does not outperform AR significantly under the primary test. These results do not eliminate every alternative explanation, but they progressively narrow the circumstances in which extra nonlinear complexity could be claimed to improve prediction.

The remaining sections examine the factors most difficult to summarize through a conventional model-comparison table: numerical fragility, failures, estimation-window sensitivity, the limits of the historical information set, and the economic scope of the conclusions. The purpose is to determine whether the absence of general nonlinear superiority is a robust scientific finding rather than an artifact of one estimation procedure or unusually favorable historical episode.
---

## References

Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics, 31*(3), 307–327. https://doi.org/10.1016/0304-4076(86)90063-1

Cho, J. S., & White, H. (2007). Testing for regime switching. *Econometrica, 75*(6), 1671–1720. https://doi.org/10.1111/j.1468-0262.2007.00809.x

Dickey, D. A., & Fuller, W. A. (1979). Distribution of the estimators for autoregressive time series with a unit root. *Journal of the American Statistical Association, 74*(366a), 427–431. https://doi.org/10.1080/01621459.1979.10482531

Diebold, F. X., & Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business & Economic Statistics, 13*(3), 253–263. https://doi.org/10.1080/07350015.1995.10524599

Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica, 50*(4), 987–1007. https://doi.org/10.2307/1912773

Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica, 57*(2), 357–384. https://doi.org/10.2307/1912559

Harvey, D. I., Leybourne, S. J., & Zu, Y. (2025). Testing for equal average forecast accuracy in possibly unstable environments. *Journal of Business & Economic Statistics, 43*(3), 643–656. https://doi.org/10.1080/07350015.2024.2418835

Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics, 6*(2), 65–70. https://www.jstor.org/stable/4615733

Kwiatkowski, D., Phillips, P. C. B., Schmidt, P., & Shin, Y. (1992). Testing the null hypothesis of stationarity against the alternative of a unit root: How sure are we that economic time series have a unit root? *Journal of Econometrics, 54*(1–3), 159–178. https://doi.org/10.1016/0304-4076(92)90104-Y

Lenza, M., & Primiceri, G. E. (2022). How to estimate a vector autoregression after March 2020. *Journal of Applied Econometrics, 37*(4), 688–699. https://doi.org/10.1002/jae.2895

Orphanides, A. (2001). Monetary policy rules based on real-time data. *American Economic Review, 91*(4), 964–985. https://doi.org/10.1257/aer.91.4.964

Pesaran, M. H., & Timmermann, A. (2007). Selection of estimation window in the presence of breaks. *Journal of Econometrics, 137*(1), 134–161. https://doi.org/10.1016/j.jeconom.2006.03.010

Qu, Z., & Zhuo, F. (2021). Likelihood ratio-based tests for Markov regime switching. *The Review of Economic Studies, 88*(2), 937–968. https://doi.org/10.1093/restud/rdaa035

Rossi, B., & Inoue, A. (2012). Out-of-sample forecast tests robust to the choice of window size. *Journal of Business & Economic Statistics, 30*(3), 432–453. https://doi.org/10.1080/07350015.2012.693850

Stock, J. H., & Watson, M. W. (2007). Why has U.S. inflation become harder to forecast? *Journal of Money, Credit and Banking, 39*(s1), 3–33. https://doi.org/10.1111/j.1538-4616.2007.00014.x

Teräsvirta, T. (1994). Specification, estimation, and evaluation of smooth transition autoregressive models. *Journal of the American Statistical Association, 89*(425), 208–218. https://doi.org/10.1080/01621459.1994.10476462

Zivot, E., & Andrews, D. W. K. (1992). Further evidence on the great crash, the oil-price shock, and the unit-root hypothesis. *Journal of Business & Economic Statistics, 10*(3), 251–270. https://doi.org/10.1080/07350015.1992.10509904
