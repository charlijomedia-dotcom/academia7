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

