# Part II: Testing the Forecast Value of Nonlinear State Dependence

# Chapter 3: From Model Adequacy to Forecast Performance: Evidence Across Expansions, Recessions, Peaks and Troughs

The preceding chapters established two distinct propositions. Economic relations involving inflation, employment, output, interest rates and money may change as shocks, expectations and policy conditions evolve. Yet this possibility does not imply that a nonlinear statistical model will forecast their future values more accurately than a simpler model. Chapter 2 converted that distinction into a testable comparison between autoregressive (AR), autoregressive moving-average (ARMA), two-state Markov-switching autoregressive (MSAR) and smooth transition autoregressive (STAR) forecasts. The models share specified targets and forecast horizons, but differ in how they represent persistence and state dependence.

This chapter evaluates the empirical evidence in the order required by the research question. First, it examines whether the data contain statistical features that justify considering nonlinear conditional means. Second, it assesses whether the fitted models describe the observed data adequately. Third, it asks whether the additional regimes and transition functions are statistically identifiable and economically interpretable. Only after these assessments does it compare forecasts formed outside each estimation window. Later sections of the chapter examine realized forecasting errors during expansions, recessions and periods surrounding business-cycle peaks and troughs. The distinction between in-sample description and out-of-sample prediction governs the interpretation throughout.

The six U.S. targets are quarterly real GDP growth; monthly consumer price inflation, industrial production growth and M2 growth; the monthly unemployment rate; and monthly changes in the effective federal funds rate. Growth rates are annualized log changes, while unemployment is modelled in levels. The sample ends in 2026Q2 for GDP and August 2026 for the monthly series. The historical data vintage and the limited treatment of two missing October 2025 observations are defined in Section 2.2. All reported numerical results are conditional on those data and transformations.

The central issue is not whether a nonlinear model can attain a lower fitted error or information criterion. It is whether nonlinear dependence can be estimated credibly and whether its forecasts improve prediction on comparable future target dates. A model may pass one of these tests and fail another. In particular, a statistically detectable departure from linearity does not determine the size, sign or reliability of a subsequent forecasting gain. Nor does failure to reject a linearity hypothesis establish that a series is truly linear. The evidence is therefore interpreted without treating any individual diagnostic as a verdict on the whole forecasting question.

## 3.1 Pre-estimation Evidence and Model Eligibility

### 3.1.1 Stationarity and the interpretation of the forecast targets

The first requirement is that the fitted equation has an interpretable statistical target. The choice between a level, a log difference and a first difference changes what a forecast represents. An unemployment forecast in percentage-point levels answers a different question from a forecast of the monthly change in unemployment. Likewise, forecasting the change in the federal funds rate is not equivalent to forecasting its level. These representations cannot be exchanged after observing which model yields the smallest error.

The initial-window stationarity evidence, evaluated through the ADF and KPSS procedures of Dickey and Fuller (1979) and Kwiatkowski et al. (1992) under the rules in Section 2.3, determines the baseline representations. For quarterly GDP, CPI, industrial production and M2, the log-level ADF tests do not reject a unit root at the 5% level, whereas the corresponding KPSS tests reject level stationarity. Annualized log differences are therefore used as forecasting targets. For unemployment, the initial-window ADF test rejects the unit-root null ($p=0.0251$), while KPSS does not reject level stationarity (reported $p\geq0.100$). The unemployment rate is consequently retained in levels. The federal funds rate displays the opposite pattern: ADF does not reject a unit root ($p=0.9530$), and KPSS rejects the level-stationarity null (reported $p\leq0.010$). Its first difference is retained.

These choices are not claims that the series have identical persistence across all historical periods. They describe the evidence available in the initial estimation windows and specify the conditional-mean objects subsequently forecast. An aggregate may display changing means or variances even after a transformation removes much of its low-frequency trend. In particular, the full-sample stationarity tests do not uniformly support a stable stationary distribution for every transformed series.

For the four log-growth targets, the full-sample ADF tests reject the unit-root null at 5%. KPSS does not reject stationarity for GDP growth ($p=0.0529$) or M2 growth ($p=0.0766$), but it rejects for CPI inflation ($p=0.0494$) and industrial production growth ($p=0.0355$). CPI lies close to the conventional threshold; industrial production offers somewhat stronger evidence against the KPSS stationarity null. A rejection of that null does not by itself identify the reason for instability. Changes in volatility, unusual observations, breaks in the conditional mean and remaining persistence are possible explanations requiring different empirical tests. Accordingly, the transformed inflation and industrial production series are used in the stated forecasting exercise, but the full-sample disagreement is treated as a qualification rather than suppressed.

The full-sample evidence for the two rate variables is more consistent with their initial choices. Unemployment in levels again rejects the ADF unit-root null ($p=0.0028$) without rejecting the KPSS stationarity null ($p=0.0783$). The federal funds rate in levels again fails to reject the ADF null ($p=0.1285$) while rejecting KPSS stationarity (reported $p\leq0.010$). Thus the treatment of these two variables is not selected by looking at later forecast accuracy. It follows an explicit diagnostic distinction between a rate that is represented in levels and a policy-rate series whose changes constitute the forecast target.

### 3.1.2 Break-sensitive tests do not replace the transformation decision

A unit-root test can have difficulty distinguishing persistent stochastic movement from a stationary process affected by a structural break. Conversely, the ability to estimate an apparent break does not establish a particular historical economic mechanism. The Zivot–Andrews procedure permits an endogenously located break under a stationary alternative while retaining a unit-root null (Zivot & Andrews, 1992). Its role here is to assess the sensitivity of the stationarity interpretation, not to date a monetary-policy intervention or business-cycle turning point.

For unemployment in levels, the initial-window Zivot–Andrews statistic is $-4.556$ with $p=0.1887$; the full-sample statistic is $-4.606$ with $p=0.1691$. Neither test rejects its unit-root null at 5%. The corresponding statistics for the federal funds rate are $-3.500$ ($p=0.8113$) and $-4.290$ ($p=0.3203$). These non-rejections do not demonstrate the absence of structural breaks. Nor do they overturn the explicit ADF–KPSS decision rule used to select the baseline target representation. The two tests use different alternatives and need not agree in a finite sample.

### 3.1.3 Tests of nonlinearity and their evidential scope

Stationarity tests do not answer whether past information enters the conditional mean linearly. That issue is examined separately. The Tsay (1986) procedure tests departures from a selected linear autoregressive representation using an auxiliary quadratic specification. The smooth-transition linearity test follows the approach of Luukkonen et al. (1988) and Teräsvirta (1994), searching for evidence against a linear conditional mean over candidate transition delays. The procedures emphasize different departures, so their results need not coincide.

**Table 3.1. Initial-window nonlinearity diagnostics for the six forecasting targets**

| Forecast target | Tsay $p$ | STAR linearity $p$ at selected delay | Selected transition | Conclusion at 5% |
|---|---:|---:|---|---|
| Real GDP growth, quarterly | 0.2242 | 0.4541 | LSTAR, $d=3$ quarters | Neither test rejects |
| CPI inflation | 0.6213 | $2.43\times10^{-9}$ | LSTAR, $d=6$ months | STAR test rejects |
| Unemployment rate, level | 0.0013 | $3.18\times10^{-5}$ | LSTAR, $d=1$ month | Both tests reject |
| Industrial production growth | 0.7011 | 0.0778 | ESTAR, $d=4$ months | Neither test rejects |
| Federal funds rate change | 0.8206 | 0.0432 | ESTAR, $d=1$ month | STAR test rejects |
| M2 growth | 0.1422 | 0.1271 | LSTAR, $d=5$ months | Neither test rejects |

*Source: Author's computations.* *Note:* The STAR column records the linearity-test p-value at the delay selected by the specified testing and selection sequence. It is not an out-of-sample forecast test. The 5% conclusions are nominal results for the stated procedures; selection across candidate delays affects how they should be interpreted.

The results indicate that the empirical case for nonlinear conditional-mean dynamics is target-specific. Unemployment provides the broadest evidence because both tests reject the relevant linear null. CPI inflation and changes in the federal funds rate reject the smooth-transition null but not the Tsay null. For GDP growth, industrial production growth and M2 growth, neither procedure rejects at 5%. These patterns cannot be summarized as a general rejection of linearity for all macroeconomic aggregates.

The discrepancy between the CPI results is especially informative. The Tsay test with the selected linear AR order yields $p=0.6213$, while the smooth-transition test at a six-month delay yields a much smaller p-value. This does not establish a logical contradiction. A linearity test responds to the form of the alternative against which its null is examined; an alternative involving a delayed transition need not be well represented by every quadratic approximation. Nonetheless, the very small STAR linearity p-value is not an estimate of forecast improvement. The later forecast experiment must determine whether the identified feature survives parameter estimation and contributes information not already contained in a linear benchmark.

The policy-rate result requires similar restraint. The smooth-transition test rejects at the selected one-month delay ($p=0.0432$), only modestly below 5%. It is therefore sensitive to conventional inferential thresholds and to specification selection. More importantly, the observed rate change may respond to effective-lower-bound episodes, monetary-policy decisions and irregular adjustments. A statistically significant smooth-transition test is not evidence that any one of those mechanisms has been identified. Its implication is limited to a departure from the tested linear specification.

The unemployment result has a different interpretation. Both procedures reject, with a Tsay p-value of approximately $0.0013$. It is reasonable to ask whether unemployment dynamics differ across persistent labor-market conditions or recession episodes. It is not reasonable to infer in advance that a latent-state likelihood will be globally identified, that a STAR threshold will be meaningful, or that either model will improve the next month's forecast. Those are separate propositions tested below.

### 3.1.4 Model eligibility is not a prediction of model success

The pre-estimation evidence supports three decisions. First, it identifies what each model must forecast. Second, it determines the initial linear specification and the orders inherited by nonlinear alternatives, subject to the maximum lag restrictions explained in Chapter 2. Third, it identifies which targets exhibit the strongest initial statistical motivation for nonlinear conditional means. These decisions establish a common empirical question, not a preferred winner.

The selected baseline AR orders are 1 for quarterly GDP, 2 for CPI inflation, 6 for unemployment, 12 for industrial production, 1 for the federal funds rate change and 3 for M2 growth. The corresponding MSAR and STAR lag orders are capped at 4 for monthly targets and 2 for GDP. Consequently, unemployment and industrial production use more own-history lags in their AR benchmarks than in the nonlinear alternatives. That difference is part of the specification design and must be kept visible when interpreting subsequent performance. It avoids adding unrestricted nonlinear lag coefficients to already demanding likelihoods, but it also means the four families are not identical except for a transition function.

The ARMA family also requires a qualification. Its initial-window selection produces $q=0$ for GDP, CPI, industrial production, the federal funds rate and M2. Only unemployment selects a nonzero moving-average order, ARMA(3,4). For five targets, therefore, the selected ARMA candidate is itself a pure autoregression, generally with an order different from the primary AR benchmark. The ARMA label describes the larger specification search, not a claim that every fitted member contains moving-average dynamics.

All four model families proceed to the estimation assessment. The absence of a nominal nonlinearity rejection is not used to delete a pre-specified nonlinear comparison. Equally, a rejection does not exempt its corresponding model from residual diagnostics, stability restrictions or forecast-loss tests. The next section therefore examines the actual fitted models before considering their predictive rankings.

## 3.2 In-Sample Model Adequacy and Residual Diagnostics

### 3.2.1 Why a better likelihood is an incomplete result

In-sample estimation evaluates how well a statistical representation accounts for observations already available to the fitted model. Likelihood and information criteria summarize different aspects of that task. A nonlinear conditional mean can fit an unusual event particularly well by assigning it to a distinct regime or by changing the effective coefficients around a threshold. Such a fit may raise the likelihood substantially. It may also rely on a state represented by only one or two observations, a transition probability at the edge of its admissible range, or an imprecise parameter estimate. In those cases, the apparent fit improvement does not have a clear interpretation as a recurrent economic mechanism.

The Bayesian information criterion (BIC) penalizes the number of estimated parameters, but it cannot determine whether a rare state is economically meaningful. Nor does a lower BIC establish that the model's forecasts of subsequent observations are more accurate. Its evidence is conditional on the fitted likelihood, the sample used and the statistical model being compared (Schwarz, 1978). The distinction is particularly important for macroeconomic samples containing large shocks, because flexible models may improve their historical fit by reproducing those shocks more closely without learning a relation that repeats.

**Table 3.2. Full-sample BIC and diagnostic classification of the baseline models**

| Forecast target | AR BIC | ARMA BIC | MSAR(2) BIC | STAR BIC | Main adequacy qualification |
|---|---:|---:|---:|---:|---|
| Real GDP growth | 1,840.39 | 1,851.83 | 1,775.04 | 1,836.19 | MSAR: low occupancy and boundary transition; STAR: ill-conditioned covariance |
| CPI inflation | 4,995.79 | 5,037.37 | 4,879.14 | 4,918.72 | All four fitted models retain residual autocorrelation |
| Unemployment rate | 1,029.02 | 1,049.40 | −142.46 | 958.87 | MSAR: boundary transition; STAR: singular covariance and extreme threshold |
| Industrial production growth | 7,456.22 | 7,501.02 | 7,289.93 | 7,463.85 | MSAR: sparse state and singular covariance; STAR: transition-scale boundary |
| Federal funds rate change | 1,051.31 | 1,059.20 | 1,078.36 | 998.08 | MSAR regimes have indistinguishable means; residual dependence persists |
| M2 growth | 4,618.27 | 4,640.19 | 4,460.85 | 4,603.11 | MSAR: sparse state; STAR: transition-scale boundary |

*Source: Author's computations.* *Note:* Smaller BIC values describe better penalized in-sample fit within each estimation exercise. Models have differing effective observation counts because likelihood initialization and lag orders differ; direct BIC contrasts across such samples are descriptive and should not be interpreted as perfectly sample-matched model-selection tests. The listed warnings refer to the full-sample fitted models, not to the distribution of rolling-forecast statuses.

The full-sample comparisons show why assessing model fit alone would be misleading. The two-state MSAR has a numerically lower BIC than the AR model for five targets: GDP, CPI, unemployment, industrial production and M2. It does not improve on the AR BIC for the differenced federal funds rate. STAR also has a lower reported BIC than AR for five targets, with industrial production as the exception. These patterns establish that additional flexibility can improve the penalized historical likelihood in many instances. They do not establish five cases of credible nonlinear forecasting improvement.

### 3.2.2 Residual serial dependence

Residual autocorrelation tests examine whether the fitted mean equation has left systematic linear dependence in its errors. Under the Ljung–Box null, residual correlations through specified positive lags are zero (Ljung & Box, 1978). Rejection is evidence that the model has not removed all the tested dependence. Non-rejection does not prove that the model is structurally correct, and it does not guarantee out-of-sample forecast accuracy.

For quarterly GDP, the full-sample AR(1) residuals do not reject the Ljung–Box null at four or eight quarters ($p=0.210$ and $0.508$). The selected ARMA representation gives similar results ($p=0.219$ and $0.537$). By contrast, the two-state MSAR residuals reject at four quarters ($p=0.0179$), although not at eight ($p=0.111$). Thus the lower MSAR BIC does not correspond to uniformly more satisfactory residual behavior. The GDP STAR fit does not reject at either selected lag, but its information-matrix conditioning remains problematic. Different dimensions of model adequacy point in different directions.

CPI inflation displays a broader residual-mean problem. At the 12- and 24-month lags, the Ljung–Box null is rejected for all four baseline families. For the selected AR(2), the p-values are approximately $2.53\times10^{-16}$ and $8.97\times10^{-19}$. For MSAR, they are approximately $9.56\times10^{-11}$ and $2.95\times10^{-11}$. STAR also rejects at both horizons. This means that even the more flexible fitted mean equations retain detectable residual dependence over the full historical sample. The result is relevant for interpretation: improved likelihood does not imply that nonlinear transition terms have exhausted the predictable structure of inflation.

For unemployment, the linear AR and ARMA pass the reported full-sample Ljung–Box checks at 12 and 24 months. Their p-values are high, exceeding $0.82$ at the shorter lag and $0.99$ at the longer one. The two-state MSAR, in contrast, rejects at 12 months ($p=0.0018$) but not at 24 months ($p=0.0761$). The STAR residuals do not reject at either lag. Yet, as Section 3.3 shows, the STAR fit uses a transition threshold outside the central range of the observations and has an unusable covariance estimate. Passing a residual-autocorrelation test therefore cannot validate the transition function.

Industrial production offers another example of the comparison between a strong linear specification and more flexible alternatives. The twelve-lag AR passes the stated residual-whiteness checks at the selected lags. The ARMA, MSAR and STAR full-sample fits all reject at at least one reported lag. A lower MSAR BIC therefore coexists with stronger evidence of remaining serial dependence. For changes in the federal funds rate and for M2 growth, the full-sample residual-whiteness null is rejected for each of the four model families. This weakens any claim that one particular nonlinear specification has resolved the principal serial-dependence problem in those variables.

The full-sample residual results must not be confused with initial-window model selection. Lag orders were selected from the first estimation window and remained fixed as the historical sample extended. The fact that a model passed a whiteness screen initially but failed it over the longer sample is consistent with changes in persistence or dependence over time. It is not evidence that the original choice should be retroactively replaced by an order selected from later data. The CPI lag sensitivity and the general question of temporal stability are assessed in Chapter 4.

### 3.2.3 Conditional variance and distributional departures

Residual independence in the conditional mean and stability of the conditional variance are different requirements. Even when an autoregressive equation removes serial correlation, large innovations can occur in clusters. Engle's (1982) ARCH framework formalizes this dependence in conditional variance. A rejection of an ARCH–LM test indicates that squared residuals retain serial structure; it does not establish that another conditional-mean equation forecasts the next target value better.

In the full-sample GDP results, the four baseline model families reject the reported ARCH–LM null at four quarters. For the AR(1), the p-value is approximately $1.00\times10^{-21}$. For CPI inflation, all four models reject the ARCH–LM null at twelve months; the AR(2) p-value is approximately $2.95\times10^{-19}$. Industrial production, the federal funds rate change and M2 growth likewise show strongly significant conditional-variance diagnostics in several fitted models. These findings indicate that changes in volatility remain an important feature of the data even where the main research question concerns conditional-mean forecasts.

The unemployment results illustrate why evidence must be target-specific. The selected unemployment AR and ARMA do not reject the ARCH–LM null at the reported twelve-month lag, whereas the same series rejects the normality hypothesis under the Jarque–Bera diagnostic. A nonnormal residual distribution can coexist with an absence of detected conditional heteroskedasticity. It does not follow that an MSAR or STAR mean specification is required. Similarly, the highly significant Jarque–Bera results for many models register departures from Gaussian residuals, especially during extreme observations, but they are not an automatic disqualification of point forecasting (Jarque & Bera, 1987).

Where the selected classical-mean residuals display ARCH effects, a conditional-variance specification provides a separate robustness question. Chapter 4 evaluates whether the variance process can be better described by ARMA–GARCH(1,1) and whether that finding changes the interpretation of the mean comparison. The present chapter does not infer a forecasting gain in the conditional mean from a better-fitting variance equation.

### 3.2.4 Adequate, fragile and failed are distinct evidential categories

The model evaluation applies three classifications, whose definitions were stated in Section 2.11. An *adequate* fit satisfies the numerical conditions and does not trigger the specified adequacy warnings. A *fragile* fit produces a usable estimate or finite forecast but violates at least one diagnostic or credibility condition. A *failed* fit does not provide an admissible prediction and is not included in forecast accuracy calculations. These categories are not posterior probabilities that a model is correct, nor are their warning thresholds formal hypothesis tests.

The distinction matters because a forecast can be finite even when an estimated regime has little empirical support. A model with a low-occupancy state may still deliver an accurate prediction on the next observation. Excluding every finite forecast from a fragile model would conceal how the fitted procedure actually behaves. Conversely, replacing a failed nonlinear forecast with a linear prediction while continuing to label it nonlinear would artificially improve its apparent reliability. The analysis therefore retains valid finite forecasts, records their adequacy status and excludes only failed forecasts from scoring. Pairwise loss comparisons use common valid target dates, and comparisons across all four families use the dates available to every model.

For the full historical sample, the classical AR and ARMA models are classified as adequate for GDP and unemployment. The AR is also adequate for industrial production. CPI inflation, the federal funds rate change and M2 growth present full-sample residual-autocorrelation warnings even for the classical benchmarks. The two-state MSAR and STAR fits are classified as fragile for every target, but the reasons differ sharply across variables. The latter fact is crucial. Fragility due to residual serial dependence is not statistically identical to fragility due to a nearly empty latent state, a transition probability at its boundary or a singular information matrix.

The full-sample labels are also not sufficient to describe numerical behavior at each rolling forecast origin. A model that appears fragile on the full sample can be adequate in some shorter estimation windows and unstable in others. That time variation is itself relevant to the forecasting question. The detailed rolling incidence is examined alongside the forecast comparisons in Section 3.4 and challenged more fully in Section 4.7.

## 3.3 Regime and Parameter Credibility for Nonlinear Models

### 3.3.1 What an estimated state can and cannot establish

The defining feature of an MSAR model is that an unobserved Markov state changes part of the conditional distribution. In the specification used here, regime-dependent means are combined with common autoregressive coefficients and a common innovation variance. A distinct estimated mean is not sufficient to establish a distinct recurring economic state. The regime must also be represented by enough observations to support estimation, have transition probabilities away from problematic boundaries and yield parameter estimates with usable uncertainty measures. Otherwise, the likelihood may describe a rare disturbance by treating it as a separate distribution rather than uncovering a recurrent feature of macroeconomic dynamics.

Hamilton (1989) showed why latent-state models can be valuable for describing changes in U.S. output dynamics. That contribution does not imply that the state variable of every two-regime estimate is interchangeable with recession status. The mapping between an estimated state and an economic episode requires evidence. A high-inflation state, for example, need not be a recession state; monetary and real-activity conditions can differ within the same NBER-dated expansion or contraction. Accordingly, the regimes in this section are described by their estimated means, persistence and occupancy. They are not assigned causal labels.

For a two-state Markov process with estimated stay probability $\widehat p_{kk}$, the expected duration of an uninterrupted spell in state $k$, conditional on the estimated constant transition probability, is

**Equation (3.1): Expected duration of an estimated Markov state**

```math
\widehat D_k=\frac{1}{1-\widehat p_{kk}},
\qquad k\in\{1,2\}.
```

This quantity is expressed in quarters for GDP and months for the remaining series. When a transition probability approaches one, the implied duration becomes large. Such a result might describe persistence, but it can also indicate weak identification in a finite sample. Expected duration should therefore be read alongside effective occupancy, parameter uncertainty and the observed history rather than as an independently verified economic cycle length.

A separate difficulty arises when a fitted state absorbs only an extreme observation. The state may acquire a very different estimated mean and sharply improve the likelihood while containing too little information to estimate transition dynamics reliably. The usual regularity conditions for comparing one- and two-state likelihoods are not automatic because parameters can be unidentified under a one-state null and probabilities may lie on boundaries (Cho & White, 2007; Qu & Zhuo, 2021). For this reason, a large likelihood difference is not presented as a conventional likelihood-ratio rejection with an assumed chi-square reference distribution.

The STAR family presents an analogous but distinct credibility problem. Its transition function is based on an observed lagged variable rather than an unobserved state. The relevant questions are whether the fitted threshold lies in a part of the sample containing enough observations, whether the transition moves meaningfully between its limiting values, and whether the transition slope and autoregressive parameters are estimated with reasonable precision. A threshold outside the observed central range can make the transition nearly constant. An estimated slope at its admissible limit can approximate a discontinuous change even when the model was intended to represent smooth adjustment (Teräsvirta, 1994). A numerical minimum of the objective function need not resolve these identification problems.

### 3.3.2 Contrasting the two-state estimates across aggregates

**Table 3.3. Full-sample MSAR regime estimates and principal STAR credibility warnings**

| Forecast target | MSAR regime means | Occupancy of less-populated state | Principal MSAR qualification | Principal STAR qualification |
|---|---|---:|---|---|
| Real GDP growth | −38.14; 3.20 | 0.32% | Essentially one-observation state; transition boundary | Ill-conditioned parameter covariance |
| CPI inflation | 2.56; 12.49 | 8.60% | Distinct estimated means, but residual autocorrelation | Residual autocorrelation |
| Unemployment rate | −0.14; 10.96 | 8.19% | Near-absorbing transitions; imprecise state means | Threshold outside central data range; singular covariance |
| Industrial production growth | −167.80; 2.72 | 0.11% | Essentially one-observation state; singular covariance | Transition slope at bound; residual autocorrelation |
| Federal funds rate change | 0.0025; 0.0025 | 49.95% | Means coincide; states not separately identified | Transition slope at bound; residual autocorrelation |
| M2 growth | 6.35; 53.72 | 0.37% | Approximately three-observation state; transition boundary | Transition slope at bound; residual autocorrelation |

*Source: Author's computations.* *Note:* Regime means use the units of the transformed targets in Table 2.1: annualized percentage growth rates, unemployment in percent and federal funds rate changes in percentage points. Occupancy refers to smoothed full-sample state probabilities. A numerically lower BIC is not sufficient to override low occupancy, boundary transitions, singular covariance or residual-autocorrelation warnings. STAR qualifications describe its own fitted transition mechanism; its threshold is not an MSAR state.

For GDP, the less-populated state has an estimated mean of approximately $-38.14$ in annualized quarterly-growth units, compared with approximately $3.20$ in the other state. Its occupancy share is $0.0032$. With roughly 316 observations contributing to the fitted autoregression, this corresponds to approximately one effective observation. The transition probability associated with leaving the rare state is effectively at its boundary. These features are consistent with the model isolating a very large contraction rather than identifying a regularly recurring state with estimable transition behavior.

This distinction is important in the historical setting of 2020. Large movements in activity around the pandemic can exert exceptional influence on macroeconomic likelihoods. Lenza and Primiceri (2022) explain why those observations complicate conventional VAR estimation. Here, the question is different but the statistical concern is related: a very large disturbance can dominate the flexible likelihood of a single-equation model. A sharp reduction in BIC is therefore not enough to conclude that the GDP series has two economically stable and repeatedly observed growth regimes. The sparse-state diagnosis is an empirical limitation on that interpretation.

Industrial production presents an even more extreme contrast. One state has an estimated mean near $-167.80$ in annualized monthly log-growth units and an occupancy share of approximately $0.0011$. The implied number of effectively assigned observations is about one. The fitted transition matrix also contains probabilities at or near its boundaries, while the parameter covariance estimate is unusable. The result is a strong example of the difference between matching a historical outlier and estimating a stable nonlinear mechanism. Industrial production responds strongly to sudden disruptions in goods production, but the model does not establish that the unusual observation belongs to a recurrent economic state.

M2 is less extreme in numerical magnitude but similar in statistical structure. Its estimated second mean is approximately $53.72$, against $6.35$ in the more prevalent state, and its smaller state has occupancy of only $0.37\%$. This is equivalent to approximately three observations over the fitted sample. The main state's stay probability is effectively one, producing an exceedingly long mechanical expected duration. Such a value should not be interpreted as a forecast that a monetary state will literally last for many centuries. It indicates that the estimated transition dynamics are close to a boundary and that the rare state provides little repeated evidence about switching probabilities.

### 3.3.3 CPI inflation is the clearest regime example, but not a complete model-adequacy success

The CPI model has the most interpretable two-state mean structure of the six targets. The lower estimated mean is $2.56\%$ annualized and the higher mean is $12.49\%$ annualized. The higher-mean state accounts for approximately $8.6\%$ of the fitted sample. Its estimated probability of remaining in that state is approximately $0.8407$, implying an expected duration of $6.28$ months under Equation (3.1). The lower-mean state has an estimated stay probability near $0.9842$, corresponding to approximately $63.1$ months. These figures show a distinguishable high-inflation statistical state that is represented by more than a handful of observations.

This is a descriptive interpretation, not a structural explanation of the causes of inflation. The estimated high-mean state may reflect periods of sustained price pressure, but the model does not identify whether those pressures came from monetary policy, supply constraints, demand conditions or changes in expectations. Neither the sign nor the timing of its state probability is sufficient to identify a causal economic mechanism. The model is useful here because it offers the clearest example of a recurrent difference in fitted means, not because it resolves the structural debate about inflation.

The credibility of the state distinction also does not make the complete CPI forecasting equation adequate on every criterion. The full-sample MSAR residuals reject the Ljung–Box null at both twelve and twenty-four months. This means that, despite the regime-dependent means, detectable dependence remains in the errors. The CPI MSAR fit is accordingly classified as fragile on the full sample because of residual autocorrelation, even though its regime parameters are considerably more interpretable than those for several other targets.

### 3.3.4 Estimated CPI equations: classical persistence and state-dependent means

The preceding analysis identifies CPI inflation as the clearest example of an interpretable nonlinear state structure. To connect that assessment to the estimated dynamics, this subsection reports the numerical coefficients of the classical AR(2) and two-state MSAR(2). Both are estimated from the full transformed CPI history, with 953 usable observations after constructing two lags. These are **retrospective full-sample estimates**, not the parameter vectors used at every rolling forecast origin; the forecasting experiment re-estimates the models separately on the information available at each origin.

For the classical AR(2), estimated by ordinary least squares with an intercept, the fitted one-step conditional mean is

**Equation (3.2): Full-sample estimated AR(2) for monthly CPI inflation**

```math
\widehat{\pi}_{t}^{\,\mathrm{AR}}
=
1.3184
+0.5048\,\pi_{t-1}
+0.1070\,\pi_{t-2}.
```

The values are annualized percentage-point inflation units, with approximate conventional standard errors of $0.1476$, $0.0319$ and $0.0319$ for the intercept and the two lag coefficients, respectively. The estimated innovation standard deviation is $3.2915$ in the same inflation units. The full-sample BIC is $4{,}995.79$. These numerical coefficients reproduce the reported AR log-likelihood and BIC when the specified linear model is fitted to the frozen historical input.

The corresponding two-state MSAR specification has state-dependent means but **common** autoregressive coefficients. Because it is formulated around the means of both the current and lagged latent states, its conditional-mean equation is not a conventional AR(2) with a switching intercept added to uncentered lags. The estimated state-conditional mean and transition matrix are

**Equation (3.3): Full-sample estimated two-state MSAR(2) for CPI inflation**

```math
\begin{aligned}
\widehat m_t(\mathbf S)
&=\widehat\mu_{S_t}
 +0.4573\bigl(\pi_{t-1}-\widehat\mu_{S_{t-1}}\bigr)\\
&\quad+0.0502\bigl(\pi_{t-2}-\widehat\mu_{S_{t-2}}\bigr),\\[4pt]
(\widehat\mu_1,\widehat\mu_2)
&=(2.5630,\;12.4941),\\[4pt]
\widehat P
&=\begin{pmatrix}
0.9842&0.0158\\
0.1593&0.8407
\end{pmatrix},
\qquad \widehat\sigma=2.7720.
\end{aligned}
```

Here $\mathbf S=(S_t,S_{t-1},S_{t-2})$ denotes the unobserved state path and $\widehat m_t$ is conditional on that path. The approximate standard errors are $0.1965$ and $0.6387$ for the two means; $0.0380$ and $0.0388$ for the common autoregressive coefficients; and $0.0726$ for the common innovation standard deviation. The transition-probability standard errors are approximately $0.0050$ for $\widehat p_{11}$ and $0.0480$ for $\widehat p_{22}$. The rows of $\widehat P$ give transitions from the current state to the next state. The historical regime interpretation is descriptive. Forecast-time predictions integrate over uncertainty in the latent states rather than treating the future state path as observed.

The full-sample MSAR BIC of $4{,}879.14$ is below the AR(2) BIC of $4{,}995.79$, establishing the direction of the penalized in-sample fit comparison. This numerical improvement is consistent with the descriptive high-inflation state discussed in Section 3.3.3, but it does not establish greater predictive accuracy. As Section 3.4 shows, the one-step AR and MSAR forecast RMSEs are almost identical, while residual autocorrelation remains in the fitted MSAR. The reported standard errors quantify approximate conditional parameter uncertainty; they do not account for model-family selection, the economic identity of a state or uncertainty over future state realizations.

### 3.3.5 Unemployment and the policy rate: two forms of weak identification

The unemployment MSAR model assigns approximately $91.8\%$ of observations to one state and $8.2\%$ to the other. Occupancy alone would not necessarily rule out this division. The difficulty lies in its estimated transitions and parameter uncertainty. The two stay probabilities are approximately $0.9991$ and $0.9966$, which imply expected durations of roughly 1,092 and 295 months. These durations are exceptionally long relative to the recurring expansions and contractions that a reader might be tempted to associate with unemployment regimes. In addition, the estimated standard errors of the regime means are large relative to their differences in economically plausible unemployment ranges.

The fitted means, approximately $-0.14$ and $10.96$ in unemployment-rate units, should not be read as two precisely identified natural unemployment rates. The negative value and extreme persistence underline the danger of imposing a literal labor-market interpretation on parameters of a difficult nonlinear likelihood. An optimizer can return a high likelihood while portions of the parameter space remain poorly identified. In this case, the MSAR fit also retains residual autocorrelation. It is therefore not justified to interpret the estimated process as a verified model of recurring employment regimes.

The unemployment STAR result is problematic for a different reason. Its estimated logistic threshold is approximately $14.8\%$, outside the central range of historical unemployment observations. The fitted transition is nearly constant over much of the sample, with a reported transition-function standard deviation of approximately $0.0163$. Its parameter covariance is singular. A model with an essentially inactive or poorly located transition cannot provide persuasive evidence that a meaningful change in autoregressive dynamics has been identified, even if a preliminary linearity test rejected the linear null. The disagreement between pretesting and full-sample parameter credibility is thus empirically substantive.

The policy-rate MSAR illustrates a near-complete collapse of the state distinction. The transformed target is the monthly first difference of the effective federal funds rate. The fitted two-state means both round to $0.0025$ percentage points. The transition probabilities describe switching between two labels that have no distinguishable conditional-mean content in this specification. A model that duplicates the same mean across states cannot be interpreted as having uncovered economically distinct monetary-policy regimes merely because it contains a Markov chain.

This result does not disprove the existence of occasionally binding lower bounds or changes in monetary-policy behavior. It shows that a two-state common-variance autoregression of the **change** in the federal funds rate fails to identify those mechanisms through distinct state means in this sample. A shadow-rate model and a regime-switching mean model impose different restrictions and answer different questions. The weak regime diagnosis is therefore a statement about the fitted model, not a universal conclusion about monetary policy.

### 3.3.6 The credibility of smooth transitions

The STAR estimates also differ substantially across targets. For quarterly GDP, the logistic specification has an ill-conditioned covariance matrix, with a reported condition number of approximately $2.79\times10^{16}$. This means that small perturbations can make conventional parameter-uncertainty calculations unreliable. The estimated transition may vary over the observations, but its slope and threshold cannot be regarded as precisely estimated solely because a numerical fit exists.

For unemployment, as noted above, the threshold is outside the central data range and the covariance is singular. Industrial production and the policy-rate change both place the exponential-transition slope at its upper parameter bound. M2 places the logistic-transition slope at its upper bound as well. These outcomes weaken the claim that the observations identify a stable and economically meaningful smooth transition. A parameter at its imposed limit may reflect an abrupt threshold, a nearly constant transition or a flat likelihood in the direction of the slope, depending on the fitted values and the location of observations. Its interpretation requires the behavior of the transition function itself rather than its numerical magnitude alone.

CPI is again the relatively more interpretable case. Its logistic transition is estimated with a six-month delay, a threshold near $3.93$ in the transformed inflation series and a finite transition slope around $2.58$. The parameter covariance is usable. Yet residual autocorrelation remains significant in the full-sample fit, so even this more credible transition should not be treated as a fully adequate forecasting model. The role of this evidence is to motivate a test of predictive value, not to announce a gain before that test occurs.

Together, the full-sample nonlinear estimates lead to a limited conclusion. CPI provides the strongest evidence of a recognizable two-state inflation process. GDP, industrial production and M2 exhibit states built around very few extreme observations. Unemployment and the federal funds rate show different identification problems, including near-absorbing transitions and indistinguishable means. Several STAR thresholds or slopes are poorly identified. These findings do not make every nonlinear forecast invalid. They show that an attractive in-sample criterion often measures something other than a stable state-dependent forecasting mechanism. The actual out-of-sample comparison is therefore decisive.

## 3.4 Out-of-Sample Forecast Performance Against Classical Benchmarks

### 3.4.1 Forecast dates, losses and the appropriate comparison

The forecasting experiment re-estimates each model at every historical origin using 240 monthly or 120 quarterly observations. The primary evaluation horizon is one month for the five monthly targets and one quarter for GDP. The rolling estimation window is held fixed in length, while each model's lag order and other discrete specification choices follow the initial-window selection described in Chapter 2. The target to be predicted is not included in the estimation window at its forecast origin.

A model is evaluated only when its forecast is finite and the corresponding fit satisfies the criteria for retention. An unsuccessful estimate is not silently replaced with a prediction from another family. As a result, a model's own valid forecast dates can differ from those of its competitors. The comparison requires two different pieces of information: the error achieved on the model's own valid dates, and the error difference measured on dates for which the relevant models both have admissible forecasts.

Let $\mathcal I_{m,b,h}$ denote the set of forecast origins at which competitor $m$ and benchmark $b$ both provide retained $h$-step forecasts and share an observed target outcome. The paired loss comparison evaluates the differential $L(e_{m,t+h\mid t})-L(e_{b,t+h\mid t})$ only for origins in that set. An own-valid-sample RMSE is not numerically interchangeable with a paired-sample RMSE if their target dates differ. This distinction is particularly important for unemployment, where a few failed fits and an extreme pandemic observation alter descriptive rankings.

### 3.4.2 One-step forecast accuracy on each model's valid dates

**Table 3.4. Baseline one-step out-of-sample RMSE by forecasting family**

| Forecast target | AR RMSE ($n$) | ARMA RMSE ($n$) | MSAR RMSE ($n$) | STAR RMSE ($n$) | MSAR $R^2_{\mathrm{OOS}}$ vs AR |
|---|---:|---:|---:|---:|---:|
| Real GDP growth | 5.284 (197) | 5.246 (197) | **4.447 (197)** | 5.123 (197) | 0.292 |
| CPI inflation | 2.967 (715) | 3.075 (715) | **2.966 (715)** | $5.38\times10^{9}$ (715) | 0.0003 |
| Unemployment rate | 0.551 (703) | 0.737 (689) | **0.491 (698)** | 0.592 (704) | 0.189 |
| Industrial production growth | 13.311 (715) | 11.974 (715) | **11.638 (715)** | $7.17\times10^{6}$ (715) | 0.236 |
| Federal funds rate change | **0.475 (625)** | 0.477 (618) | 0.480 (625) | 0.613 (625) | −0.019 |
| M2 growth | **5.078 (571)** | 5.083 (571) | 5.127 (571) | 82.745 (571) | −0.020 |

*Source: Author's computations.* *Note:* Bold identifies the smallest RMSE on each model's **own valid forecast dates**, not a significance result or a ranking on a universal common sample. The $n$ in parentheses is the number of retained forecasts. The final column is computed on each MSAR–AR matched date set using Equation (2.17), so it is not obtained by dividing the own-sample RMSEs when those samples differ. Extremely large but finite STAR errors are displayed without truncation. Values are rounded for presentation.

The first pattern is that MSAR attains the smallest own-sample RMSE for GDP, CPI, unemployment and industrial production. But the economic meaning of these rankings differs considerably. For CPI, the MSAR and AR RMSEs are virtually identical, and the matched out-of-sample $R^2$ is only about $0.0003$. For unemployment, the sample sizes differ across models and the ranking changes under date alignment. GDP and industrial production show larger numerical MSAR gains against AR, but they are strongly influenced by observations around the pandemic shock. The apparent scope of nonlinear improvement therefore becomes narrower once the magnitude, sample and reliability of each comparison are considered.

For GDP, the MSAR RMSE of $4.447$ is below the AR RMSE of $5.284$, and both methods have 197 valid target dates. The corresponding matched $R^2_{\mathrm{OOS}}$ is approximately $0.292$. This is a substantial descriptive reduction in squared forecast loss within the reported sample. It is not, however, evidence of a statistically reliable gain without considering the variability of the loss differential. The concern is particularly acute because the GDP MSAR fit assigns roughly one historical observation to a distinct state and the extreme period surrounding 2020 contributes heavily to the observed accuracy difference. A procedure that handles one shock well in retrospectively selected rolling windows may not be robust in a different episode.

Industrial production shows a related pattern. MSAR has RMSE $11.638$, compared with $13.311$ for AR, yielding a matched out-of-sample $R^2$ near $0.236$ over 715 dates. ARMA also improves the descriptive RMSE to $11.974$. These are economically meaningful magnitudes in the scale of the transformed series, but the interpretation is conditional on the highly volatile historical sample. The full-sample MSAR regime diagnosis is weak, with one effective observation in its rare state and a singular covariance estimate. It would therefore be premature to treat the smaller RMSE as evidence that the model has learned a recurrent industrial-cycle mechanism.

Inflation offers a more direct test of the difference between model interpretation and predictive value. The two-regime MSAR identifies a relatively clear high-inflation state in-sample, yet its one-step RMSE of $2.966$ is almost indistinguishable descriptively from the AR benchmark's $2.967$. The matched out-of-sample $R^2$ is approximately $0.0003$, a reduction in squared error too small to support any substantial forecast-value claim on its own. A coherent state interpretation need not translate into additional one-period-ahead information after the benchmark's persistence has been considered.

The policy-rate and money-growth targets provide still less descriptive support for MSAR. For changes in the federal funds rate, AR has the lowest RMSE, $0.475$, compared with $0.480$ for MSAR. The MSAR matched $R^2_{\mathrm{OOS}}$ is negative, approximately $-0.019$. For M2 growth, AR has RMSE $5.078$, compared with $5.127$ for MSAR, and the matched $R^2_{\mathrm{OOS}}$ is about $-0.020$. A negative value indicates that the competitor incurs greater squared forecast loss than AR on its matched dates. These results are consistent with the weak MSAR state diagnoses for the two monetary targets, although they cannot by themselves establish why the forecasts differ.

### 3.4.3 Unemployment shows why the evaluation sample cannot be ignored

The unemployment results require separate treatment because the number and composition of valid forecasts differ. AR supplies 703 retained one-step forecasts, ARMA 689, MSAR 698 and STAR 704. On each model's own valid dates, MSAR has the smallest RMSE at $0.491$, AR has $0.551$ and ARMA has the largest at $0.737$. Reading only those entries would suggest that MSAR is plainly superior and ARMA plainly inferior.

That conclusion would be incorrect. One unusually large unemployment forecast error occurs on a pandemic target date for which not all models have a valid paired forecast. In particular, a very large ARMA error contributes to its own-valid-sample RMSE while the AR benchmark is unavailable on that date. When ARMA is compared with AR on their 688 common valid target dates, ARMA's RMSE is approximately $0.486$, and its AR-relative out-of-sample $R^2$ is about $0.237$. MSAR's comparable figures, on a **different** set of 697 paired dates, are RMSE $0.487$ and $R^2_{\mathrm{OOS}}$ $0.189$. The positive AR-relative values do not establish that ARMA and MSAR have been compared directly on the same calendar.

The results therefore contain three different objects: the model's loss on its own dates, its loss relative to AR on a matched pairwise calendar, and its ranking on a calendar shared by all four families. The first two are reported directly here; the final common-calendar comparison is used as a supplementary consistency check but does not introduce a new formal test of model equivalence. Treating these objects as interchangeable can reverse a descriptive claim without changing a single forecast.

### 3.4.4 Numerical instability of STAR forecasts

The STAR forecast results are markedly different from the moderate MSAR results. For CPI inflation and industrial production, the reported STAR RMSEs are approximately $5.38\times10^{9}$ and $7.17\times10^{6}$ respectively. They are not typographical errors or truncated axes. They arise from extremely large but finite iterated forecasts produced by unstable fitted parameter combinations at some rolling origins. For M2, STAR's RMSE is $82.745$, against approximately $5.1$ for the linear and MSAR forecasts. These outcomes must remain visible because numerical fragility is part of the performance of the specified forecasting procedure.

A very large RMSE is a descriptive result: it says that squared errors became enormous over the evaluated dates. It is not automatically accompanied by a valid hypothesis-test p-value. When a few loss differentials are many orders of magnitude larger than the others, procedures that estimate a long-run variance or calibrate a reference distribution can become numerically degenerate. In such cases, a reported non-rejection must not be used to claim equal forecast accuracy, and even a formally returned p-value may be uninformative.

These outcomes also show that an in-sample transition function can be misleading as a predictor. A fitted STAR coefficient combination may behave reasonably over the observations used to estimate it, yet its iterated recursion can move toward values rarely represented in that window. This risk becomes more important as the horizon grows, but the one-step results already show that unstable predictions cannot be dismissed as a purely distant-horizon phenomenon. Section 4.7 returns to their sensitivity to estimation and numerical constraints.

### 3.4.5 Formal inference: apparent gains versus statistically supported gains

The primary inferential comparison uses the average-loss test of Harvey, Leybourne and Zu (2025). The test is designed to address possibly time-varying mean forecast-loss differentials, a relevant concern in samples covering crises, major policy changes and periods of unusually high volatility. Its application is defined in Section 2.10. The reported sign convention is competitor loss minus benchmark loss: a negative average differential favors the competitor, while a positive differential favors the benchmark.

**Table 3.5. Primary one-step forecast-accuracy tests against AR**

| Forecast target | MSAR vs AR: squared-loss $p$ | MSAR vs AR: absolute-loss $p$ | ARMA vs AR: squared-loss $p$ | ARMA vs AR: absolute-loss $p$ |
|---|---:|---:|---:|---:|
| Real GDP growth | 0.3566 | 0.6261 | 0.3684 | 0.7580 |
| CPI inflation | 0.9750 | 0.3980 | 0.0986 | **0.0104** |
| Unemployment rate | 0.3669 | 0.3217 | 0.3356 | 0.5182 |
| Industrial production growth | 0.2317 | 0.1212 | 0.2658 | 0.2469 |
| Federal funds rate change | 0.4989 | 0.9868 | 0.9694 | 0.3354 |
| M2 growth | 0.2364 | 0.8711 | 0.4263 | 0.8275 |

*Source: Author's computations.* *Note:* Two-sided Harvey–Leybourne–Zu p-values are calculated on the valid dates shared by each pair. Bold denotes a nominal 5% rejection. For CPI inflation, the significant ARMA–AR difference in absolute loss favors **AR**, not ARMA; a small p-value does not indicate which direction the difference takes. These are unadjusted pairwise results, not family-wise multiplicity-adjusted conclusions. Numerically degenerate STAR tests are discussed separately and not interpreted as evidence of equal accuracy.

The central result is unambiguous within the stated test: **MSAR does not significantly outperform AR at the one-step horizon for any of the six U.S. targets under either squared or absolute loss.** For GDP, the $29.2\%$ descriptive AR-relative reduction in squared error corresponds to a squared-loss HLZ p-value of $0.3566$. For industrial production, the $23.6\%$ reduction corresponds to $p=0.2317$. Neither rejection threshold is met. Thus even comparatively large descriptive error reductions do not establish a reliably positive average forecasting advantage over the selected sample.

The ARMA comparisons reinforce the need to distinguish the direction of a loss difference from its p-value. For CPI inflation, the absolute-loss comparison rejects at $p=0.0104$, but the mean competitor-minus-AR differential is positive. The evidence favors the AR benchmark over ARMA under this loss definition; it is not evidence that a richer classical family beats AR. Across the other targets, the stated ARMA–AR tests do not reject at 5%. The relative performance of linear alternatives therefore remains target- and loss-specific.

For STAR, the inferential record is more uneven. Where comparisons remain informative, there is no credible general gain over AR. On unemployment at the one-step horizon, STAR is nominally **worse** than AR under absolute loss ($p=0.0015$). For changes in the federal funds rate, the absolute-loss test also favors AR ($p=0.0292$). Both findings concern individual unadjusted comparisons. They should not be inflated into a universal ranking across all targets, horizons and losses.

Other STAR comparisons are compromised by extreme forecasts. In the CPI and industrial production squared-loss results, the enormous loss differences produce numerically degenerate test behavior. The corresponding nominal p-values cannot be interpreted as ordinary evidence of no difference. More generally, the fact that a testing routine returns a number does not prove that its finite-sample calibration remains informative under extreme numerical concentration. The correct conclusion separates an observed catastrophic forecast outcome from the inability to obtain reliable average-accuracy inference in that cell.

### 3.4.6 Multiple-model uncertainty and the meaning of a winner

Pairwise testing is supplemented by the Model Confidence Set (MCS) of Hansen et al. (2011), which assesses sets of models without selecting the smallest sample RMSE as a definitive winner. In the one-step squared-loss exercise, the 90% MCS retains AR, ARMA and MSAR for both GDP and industrial production, despite the numerical MSAR advantage in their respective own-sample RMSEs. That result is consistent with the primary HLZ comparisons: the apparent improvements are not enough to eliminate the classical competitors from the reported set.

The MCS is not an equivalence test. Inclusion of two models does not prove equal predictive ability, and inclusion of a numerically unstable model should not be treated as evidence that its very large errors are harmless. This caution matters because the one-step squared-loss MCS also retains STAR for several targets where STAR's forecast errors are extremely large. The interaction of unusual losses, resampling variability and common-date selection can make formal set membership less discriminating than a simple ranking suggests. The set is therefore read as a supplementary measure of model-selection uncertainty, not as a certificate of adequate numerical behavior.

The secondary Diebold–Mariano/Harvey–Leybourne–Newbold comparison is retained as a sensitivity assessment, not substituted for the primary instability-aware procedure whenever its p-value is more favorable. Diebold and Mariano (1995) established the general loss-differential framework; the choice of variance estimator and finite-sample treatment matters when loss relationships vary through time. Using a fixed primary procedure avoids selecting an inferential rule after observing the direction of its conclusion.

### 3.4.7 What the primary forecast experiment establishes

The baseline evidence supports a bounded answer to the chapter's central question. Two-state MSAR models can describe certain historical observations more closely than classical autoregressions, and their one-step RMSEs are descriptively lower for GDP and industrial production. Yet none of the six MSAR–AR comparisons establishes a significant one-step gain under the primary test. CPI supplies the clearest example of a distinguishable inflation regime without a corresponding one-step forecasting advantage. The federal funds rate and M2 provide cases in which the extra Markov state has weak meaning and no descriptive gain over AR. Unemployment demonstrates why an apparent model ranking must be tied to a clearly stated evaluation calendar.

These results do not imply that linearity is the true data-generating law for the six targets. The pretests show departures from some linear nulls, especially for unemployment and CPI inflation. The regime diagnostics show that some nonlinear structures are detectable in-sample. What fails to emerge is a general, statistically credible improvement in one-step prediction. Forecast performance must therefore be kept distinct from the existence of nonlinear behavior in the observed series.

A further question remains. The overall averages can conceal performance concentrated in recessions, expansions or neighborhoods of peaks and troughs. It is possible for a model to offer useful gains in a narrow state without reducing its average loss enough to yield a significant whole-sample result. It is equally possible for a model to appear superior in a retrospectively selected episode because extreme observations dominate the losses. Sections 3.5 and 3.6 examine these possibilities using the state definitions and formal conditional comparisons established in Chapter 2. The subsequent cross-aggregate synthesis and robustness analysis assess whether any state-specific interpretation survives changes in the relevant assumptions.

## 3.5 Forecast Performance in Expansions and Recessions

### 3.5.1 Economic phases as an ex-post evaluation of forecast difficulty

A forecast model can be more accurate on average without being more useful during periods when policy decisions are especially difficult. Recessions, for example, can involve unusually large changes in production, employment, financing conditions and monetary policy. A model that predicts ordinary monthly movements accurately may nevertheless miss an abrupt contraction. Conversely, a model with relatively large errors during expansions may forecast a crisis observation unusually well and achieve a lower full-sample squared-error average. For this reason, the overall forecast comparisons in Section 3.4 are supplemented by a phase-specific evaluation.

The state definitions are external to the competing AR, ARMA, MSAR and STAR models. Monthly target dates are classified using the U.S. recession chronology underlying the USREC indicator, which reflects the business-cycle dates established by the National Bureau of Economic Research (NBER, n.d.). For quarterly GDP, a quarter is classified as recession-affected when at least one of its constituent months is dated as a recession. All other evaluation dates are classified as expansions. The labels refer to the realized forecast **target date**, not to the information available when a forecast was made.

This distinction is fundamental. The NBER business-cycle chronology is retrospective. An individual observation can eventually be assigned to a recession even when that classification had not been announced at the forecast origin. In the present exercise, the label is a device for evaluating realized errors conditional on the historical phase. It is not an additional predictor supplied to the models. The estimated latent state of MSAR is also a different object: it is inferred from a statistical likelihood and does not inherit an NBER label merely because its probability rises near a recession.

On the baseline one-step evaluation dates of the AR benchmark, the recession cells contain 23 observations for quarterly GDP, 85 each for CPI inflation, unemployment and industrial production, 66 for the federal funds rate change, and 58 for M2 growth. Their corresponding expansion counts are 174, 630, 618, 630, 559 and 513. The exact counts differ when a competing method has failed at particular forecast origins. These sample sizes are large enough to provide descriptive comparisons, but the recession subsamples remain much smaller than the expansion subsamples. One exceptional observation can therefore have considerable influence on a recession-specific RMSE.

When observations are partitioned into disjoint recession and expansion sets, their squared-error averages satisfy the following identity for a given model and its own valid evaluation calendar.

**Equation (3.4): Decomposition of overall squared forecast loss by economic phase**

```math
\begin{aligned}
\mathrm{RMSE}_{m}^{2}
&= \frac{N_{\mathrm{rec},m}}{N_m}\,
   \mathrm{RMSE}_{\mathrm{rec},m}^{2}\\
&\quad + \frac{N_{\mathrm{exp},m}}{N_m}\,
   \mathrm{RMSE}_{\mathrm{exp},m}^{2},\\[4pt]
N_m &= N_{\mathrm{rec},m}+N_{\mathrm{exp},m}.
\end{aligned}
```

The identity demonstrates why a small recession subsample can contribute disproportionately to full-sample squared forecast loss. Its effect depends both on the number of dates and on the scale of the errors. It does not imply that recession errors are statistically independent, that model differences are significant, or that competing models necessarily have the same valid dates. Those matters require matched-date comparisons and formal uncertainty assessment.

### 3.5.2 Error magnitudes across the six macroeconomic targets

**Table 3.6. One-step forecast RMSE in expansions and recessions**

| Forecast target | AR: expansion RMSE ($n$) | AR: recession RMSE ($n$) | MSAR: expansion RMSE ($n$) | MSAR: recession RMSE ($n$) |
|---|---:|---:|---:|---:|
| Real GDP growth | 4.725 (174) | 8.382 (23) | 3.666 (174) | 8.231 (23) |
| CPI inflation | 2.678 (630) | 4.570 (85) | 2.683 (630) | 4.546 (85) |
| Unemployment rate | 0.404 (618) | 1.150 (85) | 0.266 (615) | 1.227 (83) |
| Industrial production growth | 11.355 (630) | 23.127 (85) | 9.294 (630) | 22.343 (85) |
| Federal funds rate change | 0.325 (559) | 1.115 (66) | 0.334 (559) | 1.112 (66) |
| M2 growth | 3.838 (513) | 11.113 (58) | 3.953 (513) | 10.983 (58) |

*Source: Author's computations.* *Note:* Phases are dated retrospectively from the NBER chronology. The quarterly GDP classification includes quarters with at least one recession month. The sample count is the number of retained forecasts in the specified phase, not necessarily a common sample across models. A lower conditional RMSE is descriptive only. The complete phase-specific results for ARMA and STAR, including MAE and paired loss differentials, are reported in Appendix B.

For each target, the AR model's recession RMSE is higher than its expansion RMSE. The difference is especially striking for the federal funds rate change, unemployment and M2 growth. The policy-rate benchmark rises from approximately 0.325 percentage points in expansions to 1.115 in recessions. The unemployment benchmark increases from 0.404 to 1.150 percentage points, while the RMSE of M2 growth rises from 3.838 to 11.113 annualized percentage points. These contrasts are consistent with abrupt rate adjustments, labor-market disturbances and changes in monetary balances during turbulent periods. They do not identify the causes of individual shocks, since the models use past observations rather than structural instruments.

For quarterly real GDP, the recession AR RMSE is 8.382 compared with 4.725 in expansions. MSAR produces a lower descriptive RMSE in both groups, 8.231 and 3.666 respectively. The recession difference is small relative to the scale of those errors. Moreover, the GDP recession cell contains only 23 target quarters. A handful of exceptionally large contractions and recoveries can determine the comparison. The full-sample MSAR improvement in Table 3.4 should therefore not be reinterpreted as proof of superior recession forecasting on the basis of the phase-specific RMSE alone.

Industrial production offers a similar but not identical pattern. The MSAR expansion RMSE is 9.294 against AR's 11.355, while its recession RMSE is 22.343 against 23.127. The apparent improvement is numerically larger in ordinary expansions than the difference in recession RMSE. This does not establish that the model has greater predictive skill in one phase: squared-error differentials vary considerably across dates, and the recession and expansion cells have different lengths. The large size of industrial production shocks also means that RMSE can respond sharply to a small number of observations.

CPI inflation illustrates the relative absence of a phase-specific one-step gain despite the more interpretable two-state inflation fit described in Section 3.3. In expansions, the AR and MSAR RMSEs are 2.678 and 2.683. In recessions they are 4.570 and 4.546. These differences are minor when compared with the variation in inflation errors over the historical sample. They are not evidence that the high-inflation MSAR state provides a dependable signal for recessions. High inflation and NBER recessions are not synonymous economic states, and the fitted CPI regime uses inflation dynamics rather than business-cycle labels.

The unemployment comparison is more complicated because the number of available forecasts differs across models. In expansions, MSAR has a smaller own-valid-sample RMSE than AR, 0.266 against 0.404, but the counts are 615 and 618 respectively. In recessions, MSAR has a **larger** descriptive RMSE, 1.227 against AR's 1.150, on 83 rather than 85 dates. The divergent ranking between phases is compatible with the possibility that MSAR smooths comparatively ordinary unemployment movements while struggling with rapid labor-market changes. It does not demonstrate that explanation, because the samples are not identical and the state-dependent tests must account for variation in loss differences.

For changes in the federal funds rate and for M2 growth, the phase-specific MSAR gains are small or inconsistent. In recessions the rate-change RMSE moves from 1.115 under AR to 1.112 under MSAR, while in expansions the corresponding figures are 0.325 and 0.334. M2 exhibits a recession RMSE of 11.113 for AR and 10.983 for MSAR, but the expansion RMSE rises from 3.838 to 3.953. These observations provide no persuasive descriptive case for a substantial and stable state-conditioned advantage. Nor does the weak identification of the full-sample MSAR monetary regimes support a strong economic interpretation.

The STAR forecasts raise a separate issue. Some recession-conditioned errors are extraordinarily large: for CPI inflation the STAR recession RMSE is about $1.56\times10^{10}$, and for industrial production it is about $2.08\times10^{7}$. Their size reflects extreme finite forecasts, not ordinary variation in predictive accuracy. Presenting these alongside moderate AR and MSAR numbers in a common linear-scale graph would obscure the informative comparisons. The full numerical values are therefore retained in the detailed results, while the main text emphasizes that numerical instability cannot be turned into a positive inference about recession-specific forecasting ability.

### 3.5.3 Conditional loss regressions: which hypothesis is actually tested?

Separate recession and expansion RMSEs show how errors are distributed, but they do not establish whether a model's *relative* forecasting advantage depends on economic state. The relevant test concerns the signed loss differential between a competitor and the AR benchmark on their shared valid target dates. Section 2.10 specifies a Giacomini–White-style regression that relates this differential to the retrospective recession indicator and to the turning-neighborhood indicator (Giacomini & White, 2006). Odendahl et al. (2023) provide a complementary framework for state-dependent forecast evaluation; the present analysis instead uses explicitly dated, ex-post business-cycle phases and does not estimate unknown state thresholds.

These indicators overlap in time. A target date near a trough can be classified both as a recession date and as part of a turning neighborhood. The regression therefore estimates each slope **conditional on the other indicator**. The coefficient of the recession dummy is not simply the difference between the two unconditional RMSEs in Table 3.6. In addition, its dependent variable is the squared-error difference, not the square root of that difference. A comparison based on the sign of two reported RMSEs is consequently not equivalent to a significance test of the recession coefficient.

For clarity, three null hypotheses have different meanings. The recession-specific null is $\beta_{\mathrm{rec}}=0$; the turning-neighborhood null is $\beta_{\mathrm{turn}}=0$. A third hypothesis jointly restricts both slopes to zero. These are tests of *state dependence* in the relative loss. By contrast, the joint Wald test that constrains the intercept **and** both slopes to zero, $(\alpha,\beta_{\mathrm{rec}},\beta_{\mathrm{turn}})=(0,0,0)$, is broader. It may reject because average relative accuracy differs from zero, without any slope being distinguishable from zero.

**Table 3.7. One-step squared-loss regression tests of MSAR performance relative to AR**

| Forecast target | Paired dates ($N$) | Recession dates ($N$) | $p(\beta_{\mathrm{rec}}=0)$ | $p(\beta_{\mathrm{turn}}=0)$ | Joint slope test $p$ |
|---|---:|---:|---:|---:|---:|
| Real GDP growth | 197 | 23 | 0.3484 | 0.3149 | 0.5334 |
| CPI inflation | 715 | 85 | 0.7740 | 0.9447 | 0.9174 |
| Unemployment rate | 697 | 83 | 0.9744 | 0.1326 | 0.1620 |
| Industrial production growth | 715 | 85 | 0.3600 | 0.2718 | 0.5437 |
| Federal funds rate change | 625 | 66 | 0.5688 | 0.8136 | 0.8501 |
| M2 growth | 571 | 58 | 0.2775 | 0.4900 | 0.5312 |

*Source: Author's computations.* *Note:* The dependent variable is MSAR squared forecast loss minus AR squared forecast loss, with negative values favoring MSAR. The regression contains an intercept and simultaneous recession and turning-neighborhood indicators. The final column tests only the two state slopes jointly, not the intercept; the baseline turning neighborhoods are $\pm3$ months or $\pm1$ quarter. P-values are nominal, based on the stated horizon-specific covariance convention, and do not demonstrate equivalence when the null is not rejected.

No recession coefficient in Table 3.7 is significant at 5%. No turning-neighborhood coefficient is significant at that level, either. The joint slope tests also do not reject for any of the six targets. Accordingly, the signed loss regressions provide no statistically supported basis for claiming that the relative performance of MSAR against AR changes systematically during recessions or near turning points.

This conclusion is stronger and more precise than saying that MSAR never has a smaller recession RMSE. It sometimes does. The distinction is that a smaller observed error does not provide sufficient evidence of a reproducible state-conditioned improvement. Even for GDP and industrial production, whose full-sample descriptive RMSE gains are notable, the recession and turning coefficients remain imprecise. The results thus fail to establish the hypothesis that MSAR earns its extra complexity specifically when macroeconomic conditions are unstable.

The same caution applies to STAR. At the one-step horizon, the separate state slopes and their joint tests do not establish a positive nonlinear advantage over AR for any target. For CPI and industrial production, the regression coefficients involve enormous loss differentials arising from explosive forecast errors. Their associated p-values must be interpreted in light of numerical degeneracy rather than as ordinary evidence of either equality or superior performance. A large estimated coefficient with an uninformative standard error cannot identify reliable recession sensitivity.

An important qualification arises in the **classical ARMA comparison for unemployment**. At the one-step horizon, the joint Wald test of $(\alpha,\beta_{\mathrm{rec}},\beta_{\mathrm{turn}})=(0,0,0)$ rejects with $p=0.0343$. However, the separate test that restricts only the two state slopes does not reject ($p=0.2820$). The recession coefficient has $p=0.1169$, and the turning coefficient has $p=0.9983$. The joint result therefore cannot be reported as evidence that relative ARMA accuracy changes significantly in recessions or around turning points. It concerns a broader null that includes the regression intercept, and its apparent significance must be reported separately from state dependence.

This example shows why state-conditioned interpretation requires more than an automated decision to reject one omnibus null. Economic claims must correspond to the actual parameter restrictions tested. The present evidence does not establish a recurrent nonlinear forecasting advantage conditional on an ex-post recession label; nor does the unemployment ARMA joint rejection supply such evidence for a classical model.

### 3.5.4 What economic conclusions follow from the phase-specific evidence?

The phase-specific analysis suggests a consistent descriptive fact: predicting the six transformed U.S. aggregates is generally harder during historically dated recessions than during expansions, at least under the AR benchmark and the stated RMSE measure. This is unsurprising from an economic perspective. Aggregate shocks and policy responses can be unusually large during recessions. What is less obvious, and more relevant to the thesis, is that the additional state-dependent structure has not produced a formally supported relative advantage in those periods.

There are limits to this interpretation. The number of recessions in a fixed historical sample is small even when the monthly number of recession observations is reasonably large. Adjacent months in a recession are not independent replications of a new economic regime. The pandemic can dominate squared forecast loss. The analysis also uses a fixed data vintage, while retrospective recession dating may differ sharply from what policymakers knew in real time. Orphanides (2001) demonstrates why data available at the decision date may lead to different conclusions from later-revised observations. These features limit claims of general applicability to a future recession whose shocks and publication patterns may differ.

The distinction between detecting a recession and forecasting an aggregate during a period later identified as recession is especially important. Chauvet and Piger (2008) examine the real-time performance of business-cycle dating methods. Their work illustrates that classification accuracy depends on information timing. The present exercise does not estimate the probability of a recession at each historical forecast origin. It tests whether forecast errors, computed without the future target observation, differ across subsequently assigned phases. The two questions should not be confused.

The evidence therefore supports a narrow interpretation of instability: historical recession dates are associated with greater forecast difficulty, but they do not identify an empirically reliable comparative advantage for the MSAR or STAR conditional-mean specifications tested here. The next section examines the sharper question of whether relative forecast performance changes near the transitions between expansions and recessions.

## 3.6 Peaks, Troughs and Turning-Point Forecasting

### 3.6.1 Why turning points warrant separate analysis

A recession is a period, but a turning point is a boundary between phases. The difference matters for forecasting. Models can fail to anticipate the first contraction even when they predict the later recession months reasonably well. They can also miss the rebound after a trough while remaining accurate through a prolonged expansion. Averaging the entire recession may conceal these short episodes. A state-dependent model could, in principle, earn its complexity by adjusting more rapidly when the economy changes direction rather than by minimizing its average error during all recession observations.

The analysis therefore distinguishes neighborhoods of NBER-dated business-cycle peaks and troughs from recession intervals as a whole. For monthly series, the peak and trough dates are determined from the transitions of the historical recession chronology, with the reference date taken immediately before the observed change in the indicator. The baseline neighborhood contains the reference month plus three months on each side. For quarterly GDP, the quarter containing the corresponding monthly date and the adjacent quarter on each side define the baseline neighborhood.

A turning neighborhood may include both recession and expansion observations. It is not an alternative mutually exclusive recession classification. Moreover, the union of windows around different turning dates can overlap. Each target observation is counted only once in the overall turning-window RMSE, although a date can be represented in the separate peak and trough descriptive subsets when their neighborhoods overlap. Hence the peak and trough sample counts do not necessarily add to the number of observations in the union of all turning neighborhoods.

The choice of a three-month or one-quarter neighborhood is an operational sensitivity definition, not an estimate of the economically optimal warning horizon. Turning points may be recognized with delay, and the timing of GDP, unemployment and interest-rate responses can differ (Chauvet & Piger, 2008). The robustness analysis therefore considers narrower and wider neighborhoods. A model whose apparent gain disappears or reverses under small changes to the width should not be described as robustly superior around turning points.

### 3.6.2 The distribution of forecast errors near turning points

At the one-step horizon, turning-neighborhood errors are typically much larger than errors outside those neighborhoods. For the GDP AR benchmark, RMSE is $11.256$ within the baseline turning union and $2.566$ outside it, with 35 and 162 respective target quarters. For industrial production, the corresponding figures are $25.721$ and $9.637$ over 106 and 609 months. The unemployment AR benchmark has RMSE $1.080$ near turning points and $0.390$ outside. These contrasts reflect the concentration of large movements around changes in economic activity; they do not indicate that a model could have identified those turns beforehand.

**Table 3.8. One-step RMSE near historically dated peaks and troughs**

| Forecast target | AR: peak window | MSAR: peak window | AR: trough window | MSAR: trough window |
|---|---:|---:|---:|---:|
| Real GDP growth | 3.424 (18) | 3.520 (18) | 15.430 (18) | 12.003 (18) |
| CPI inflation | 3.802 (56) | 3.853 (56) | 3.616 (56) | 3.549 (56) |
| Unemployment rate | 1.414 (55) | 1.500 (56) | 1.483 (55) | 1.695 (52) |
| Industrial production growth | 29.158 (56) | 26.908 (56) | 34.835 (56) | 31.105 (56) |
| Federal funds rate change | 0.868 (42) | 0.854 (42) | 1.116 (49) | 1.118 (49) |
| M2 growth | 11.995 (42) | 11.740 (42) | 13.661 (42) | 13.809 (42) |

*Source: Author's computations.* *Note:* Parentheses give each model's number of retained forecasts in the indicated historical neighborhood. The windows are $\pm3$ months or $\pm1$ quarter around reference peak and trough dates. These are descriptive RMSEs, not paired inferential comparisons. Peak and trough neighborhoods can overlap, and recession and turning indicators are distinct. Detailed dates, MAEs and the complete four-family comparison appear in Appendix B.

The GDP figures illustrate how forecast difficulty can differ between the onset of a downturn and its aftermath. Around the selected peaks, the AR and MSAR errors are relatively close, with AR slightly lower. Around troughs, the MSAR RMSE is 12.003 compared with 15.430 for AR. This is a noticeable descriptive difference, but it occurs within 18 selected target-quarter observations that include exceptional historical events. It does not establish that the model would have recognized a trough in advance or that its apparent improvement represents a recurring nonlinear recovery mechanism.

Industrial production has higher errors near troughs than near peaks for both AR and MSAR. Its MSAR RMSE is lower than AR's in both types of neighborhood, yet the difference is not sufficient to establish the state-dependent regression effect reported in Table 3.7. In particular, the recession and turning slopes are tested jointly with their uncertainties rather than inferred from two separate RMSE columns. The direct predictive interpretation is therefore narrower than the descriptive comparison suggests.

The unemployment estimates show the opposite ordering in the baseline peak and trough subsets: MSAR's own-valid RMSE is larger than AR's in both. The counts are also unequal, especially near troughs, where MSAR retains 52 observations against AR's 55. These differences can arise from failed or inadmissible forecasts near the periods of rapid unemployment adjustment. A purported turning-point ranking that ignores those missing dates would be difficult to interpret. The result strengthens the need for common-date comparison and an explicit account of numerical coverage.

For CPI inflation, MSAR is slightly worse near peaks and slightly better near troughs; neither difference is large relative to the forecast errors. The effective federal funds rate exhibits nearly identical AR and MSAR RMSEs in both types of neighborhood. M2 changes its descriptive ordering between peaks and troughs. There is consequently no uniform pattern in which the nonlinear model outperforms the classical benchmark at both transition types across the six targets.

The STAR results provide further evidence of why turning-point interpretation cannot rely solely on a model's nonlinear form. In the CPI data, the extreme forecast errors are concentrated in the peak-neighborhood subset, whose STAR RMSE is approximately $1.92\times10^{10}$. For industrial production, the trough-neighborhood STAR RMSE reaches approximately $2.56\times10^{7}$. These are failures of numerical forecasting performance at dates later identified as economically important. They are not evidence that the transition model anticipates those turning points; nor should an uninformative p-value calculated from such extreme losses be used to claim equal accuracy.

### 3.6.3 Sensitivity to the width of a turning neighborhood

The conclusions should not depend on treating a specific calendar width as a natural economic constant. A narrow window concentrates on the most immediate transition months, where shock magnitudes are often largest and observations are few. A wide window includes more of the surrounding expansion and recession, increasing the sample while reducing the precision of the phrase *near a turning point*. Both definitions are useful as sensitivity checks, but neither is a universal identification rule.

For quarterly GDP, the analysis contrasts the turning quarter alone, the baseline $\pm1$ quarter and a wider $\pm2$ quarters. For the five monthly targets, it contrasts $\pm1$, $\pm3$ and $\pm6$ months. Changing the width changes the observations included and can alter both the sign and magnitude of an estimated model-minus-AR loss differential. It does not generate new forecasts; it changes the retrospective subset on which already-computed forecast errors are evaluated.

The GDP MSAR comparison is a useful example. Its mean squared-loss differential near turning dates is approximately $-4.71$ when only the turning quarter is included, $-48.03$ under the baseline $\pm1$-quarter neighborhood and $-32.95$ under $\pm2$ quarters. Each negative value indicates lower observed MSAR squared loss on the corresponding paired subset. The differences in magnitude show that a few observations can strongly influence the estimated benefit. None of these neighborhoods yields statistically supported turning-specific superiority under the corresponding conditional criterion.

For unemployment, the direction is less stable. The MSAR mean loss differential near turning points is approximately $+0.345$ with a three-month neighborhood, favoring AR, but falls to approximately $-0.227$ under a six-month neighborhood, favoring MSAR. The narrower one-month neighborhood also favors AR. The result shows a change of descriptive ranking when the episode definition changes. Neither direction is statistically supported as a reliable turning-specific effect. This is a direct reason not to generalize an unemployment ranking from a single chosen window.

The federal funds rate and M2 likewise display changes in the sign of some turning-window differentials as the neighborhood varies. For the policy rate, the MSAR-minus-AR mean squared-loss differential is slightly negative under the baseline three-month window, but positive under the one-month and six-month alternatives. For M2, it is positive under the baseline and wider six-month windows but negative under the narrow one-month window. CPI's baseline differential is slightly negative, becomes approximately zero and positive in the narrowest window, and remains negative in the wider window. These sign changes need not be economically large, but they show that the ranking is sensitive to how transition dates are grouped.

Industrial production retains a negative descriptive MSAR-minus-AR differential in all three selected windows. Even there, the conditional tests do not establish a statistically significant nonlinear gain near turning points. Sign stability is weaker evidence than a well-calibrated rejection of the relevant null. A positive conclusion would require both a substantively meaningful reduction in loss and statistical support that survives the declared changes in the definition of the state.

Across the specified window-width exercises, **no MSAR or STAR turning-window advantage acquires robust statistical support**. The evidence therefore provides no basis for declaring the baseline three-month or one-quarter definition uniquely favorable. The detailed alternative-window results are reported in Chapter 4, where their sensitivity is assessed alongside horizon, estimation-window and specification robustness.

### 3.6.4 Economic interpretation of the turning-point evidence

The peak–trough results provide evidence about *where forecasting becomes difficult*, not proof that any of the models can foresee the change of phase itself. An AR forecast can be wrong because the latest shock differs from historical innovations, while an MSAR forecast can be wrong because its latent-state probabilities have not yet shifted enough to reflect the new environment. STAR can be wrong because an estimated threshold or transition slope poorly represents the observations at the relevant origin. The observed losses do not, by themselves, identify which of these mechanisms caused a particular error.

The distinction between forecast-time and retrospective information is especially important near a trough. Once the recovery has occurred, it may be straightforward to identify the historical lowest point of a contraction. Before that point, output, employment and financial conditions may supply conflicting signals. A model that has a relatively low RMSE on dates surrounding a known trough has not necessarily predicted the trough date. Such a claim would require a separate real-time classification or event-prediction experiment, including its own loss measure and timely information set.

The evidence also does not validate an economic interpretation of a model's latent state solely because its filtered or smoothed probability changes near NBER dates. Smoothed probabilities incorporate later observations, and the estimated Markov state may respond to inflation or a statistical outlier rather than the cycle of aggregate activity. Relating the state path to historical peaks and troughs can be informative descriptively, but it is not sufficient for causal identification or operational recession forecasting.

The combined implication of Sections 3.5 and 3.6 is consequently precise. Recessions and turning neighborhoods are periods of relatively high forecast difficulty, but the comparison offers **no statistically established evidence of an MSAR or STAR advantage concentrated in those states**. Some numerical rankings depend on the particular dates and neighborhood widths, while several STAR regressions are affected by extreme forecast losses. The next task is to relate these results to the economic functions of each aggregate without collapsing six different targets into one universal model ranking.

## 3.7 Cross-Aggregate Synthesis: Inflation, Activity, Labor-Market and Monetary Evidence

### 3.7.1 Why the six targets do not imply a single economic forecast ranking

The empirical comparison holds the broad evaluation principles constant across six targets, but the targets differ in their economic meaning, frequency, persistence, volatility and response to shocks. A model that improves annualized industrial production growth forecasts does not thereby improve predictions of unemployment levels. Even where the same loss measure is used, the numerical scales are different, so comparing RMSE levels across target variables would have no sensible interpretation. The relevant comparison concerns a model's performance **relative to its benchmark for the same target, horizon and dates**.

The four economic groups therefore require different interpretations. Inflation concerns the persistence and variation of price changes; GDP and industrial production capture distinct dimensions and frequencies of activity; unemployment is a slowly adjusting stock-related rate that can change abruptly during crises; and the policy rate and M2 describe monetary conditions through quite different statistical transformations. Their separate results are more informative than a pooled statement that one model family is the winner.

The common finding is limited but important. The nonlinear models can generate better in-sample likelihoods for several transformed series, and the initial diagnostic tests identify evidence of nonlinear conditional-mean dynamics in some targets. Nevertheless, the out-of-sample evidence does not establish a general one-step predictive gain over AR. This distinction holds across multiple economic functions, although the reasons differ in ways that matter for the interpretation of each result.

### 3.7.2 Inflation: interpretable regime means without a one-step gain

CPI inflation presents the strongest case for interpreting an estimated two-state mean process. Its full-sample MSAR fit identifies a higher inflation mean, a substantial occupancy share relative to the sparse states found elsewhere, and finite expected state durations. The smooth-transition diagnostic also rejects its linear null at the selected delay. Thus the data provide reasons to study nonlinear dependence rather than assuming that a constant-parameter autoregression is the only plausible historical description.

The forecasting result is much less favorable to a claim of additional predictive value. The one-step MSAR and AR RMSEs are nearly identical, and neither squared nor absolute loss supports a significant MSAR advantage under the primary comparison. The recession and turning-point subsamples do not reveal a reliable conditional advantage either. The full-sample CPI residuals still display serial dependence under both classical and nonlinear specifications. Thus an interpretable inflation state does not, by itself, eliminate predictable residual structure or improve the next month's forecast.

This finding is consistent with the broader point that inflation dynamics can change without a particular nonlinear forecasting specification being the best representation for near-term prediction. Stock and Watson (2007) documented the difficulty of forecasting U.S. inflation under changing dynamics. Their work helps explain the relevance of instability but does not determine the outcome of the present MSAR–AR comparison. The question tested here is narrower: whether the estimated two-state or smooth-transition function produces an incremental predictive gain once historical own-lag dependence has been accounted for.

The relation between in-sample nonlinearity and forecast value also depends on the horizon. The primary conclusion in this chapter concerns one-step forecasts. Chapter 4 examines longer horizons and the isolated CPI MSAR result at twelve months. That finding must remain horizon-specific and qualified by the number of comparisons examined; it cannot be used to revise the baseline one-month conclusion after the fact.

### 3.7.3 Economic activity: large descriptive gains, but weak identification and uncertain inference

Quarterly GDP and monthly industrial production provide the largest descriptive reductions in one-step squared-error loss associated with MSAR. Both series were strongly affected by the exceptional output movements surrounding 2020, and both full-sample MSAR fits isolate approximately one effective observation in a distinct state. This correspondence between extreme economic observations and sparse likelihood states explains why fit and forecast evidence must be interpreted together. It does not show that the same latent mechanism will be available to improve prediction during an unrelated downturn.

The baseline AR-relative out-of-sample $R^2$ figures are approximately $0.292$ for GDP and $0.236$ for industrial production. Their magnitudes should be acknowledged, not dismissed because the primary HLZ tests fail to reject. A descriptive reduction of this scale is potentially economically relevant for a forecasting system. Yet statistical uncertainty remains substantial, and the inference does not establish superiority under either loss. Moreover, the regime identification and covariance warnings prevent a strong interpretation of the fitted extra state as a stable, recurrent mechanism.

The recession and turning analyses reinforce the distinction. MSAR produces lower descriptive errors at some economically important GDP and industrial production dates, including near GDP troughs. But these differences are not supported by the recession or turning coefficients in the conditional loss regressions. Changing the width of the turning neighborhood also changes the magnitude of the estimated benefit. Consequently, a model's capacity to accommodate an exceptional activity shock is not equivalent to a demonstrated ability to forecast future business-cycle transitions.

GDP and industrial production should also not be treated as two frequency versions of an identical series. Quarterly real GDP includes the broader economy, while monthly industrial production measures a narrower production sector. The distinct data frequency means that GDP turning neighborhoods comprise quarters whereas industrial production neighborhoods comprise months. The results have a common interpretive theme, but the numerical RMSE scales, the number of forecast origins and the mapping from economic events to observations are not interchangeable.

### 3.7.4 Unemployment: informative nonlinear diagnostics and sample-sensitive rankings

The unemployment rate has the strongest initial evidence against linear autoregressive dynamics because both the Tsay and smooth-transition tests reject. A reader might therefore expect nonlinear models to perform particularly well for this variable. Yet the full-sample MSAR estimate features near-absorbing transitions, while the STAR specification has a threshold far from the central range of observed unemployment and a singular covariance matrix. The diagnostic rejection and the parameter-identification problem can coexist: detecting a departure from a specified linear null does not guarantee that a particular nonlinear alternative can estimate that departure reliably.

The forecast comparisons also resist a simple winner claim. MSAR has the smallest one-step RMSE on its own valid dates. ARMA achieves a stronger AR-relative out-of-sample $R^2$ on its own AR-matched date intersection. The two paired comparisons use different observation sets, and neither competitor is established as significantly superior to AR under the primary test. Treating the numerical closeness of ARMA and MSAR on selected dates as statistical equivalence would require a distinct test with an explicit equivalence criterion, which is not part of this experiment.

The phase-specific unemployment results supply an additional qualification. MSAR has lower descriptive RMSE during expansion dates but a higher one during recession dates, and the number of valid forecasts differs. The conditional state regressions do not reject a nonlinear recession or turning effect. The isolated ARMA-versus-AR joint rejection includes the intercept and does not establish significance of the state slopes. These findings limit the claim that nonlinear flexibility is most useful precisely when unemployment changes rapidly.

This example has a more general implication for macroeconomic forecasting. Persistent rates can appear easy to predict over extended periods while rare and abrupt disturbances dominate squared losses. A small difference in which observations are included can then reverse a model ranking. Model evaluation must disclose the valid target calendar before assigning economic meaning to a numerical reduction in error.

### 3.7.5 Monetary variables: structural mechanisms are not necessarily identified by a switching mean

The monetary variables provide a useful contrast to the inflation and real-activity results. Under the baseline transformation, the effective federal funds rate is modelled as a monthly change rather than a level. The corresponding two-state MSAR fit produces indistinguishable regime means. This is not evidence that monetary-policy behavior is constant over time; it is evidence that this specification does not identify separate mean-change regimes in the historical sample. An occasionally binding policy-rate constraint and a fitted Markov-switching mean are different statistical mechanisms.

For M2 growth, the second state is represented by only a few effective observations, with boundary transition behavior. This limits its interpretation as a recurrent monetary state. In both variables, the AR benchmark attains the lowest own-valid one-step RMSE, and the primary MSAR comparison does not support nonlinear superiority. Their phase-specific results show little stable descriptive benefit, while STAR introduces additional estimation or forecasting fragility.

It would be inappropriate to conclude that monetary aggregates or interest rates have no nonlinear economic relationships. Money demand, policy responses, expectations and financial conditions can vary over time, as discussed in Chapter 1. The empirical conclusion is instead tied to the defined forecast target and conditional-mean models. Economic theory motivates plausible sources of instability, while the evidence determines whether those sources are captured by an admissible predictive specification.

The cross-aggregate result is therefore asymmetrical rather than universal. CPI offers the strongest case for an interpretable nonlinear *description*; GDP and industrial production offer the largest descriptive MSAR *forecast-error reductions*; unemployment offers the strongest initial nonlinearity *diagnostics* but the greatest sample-alignment ambiguity in its one-step ranking; and the monetary variables show weak state identification and little predictive support. None of these differences overturns the common conclusion that a general one-step nonlinear advantage has not been statistically established.

## 3.8 What the Baseline Evidence Establishes, and What Remains Vulnerable

The purpose of the baseline chapter is to state what follows from the primary experiment before changing its assumptions. Not every number carries the same inferential weight. A parameter estimate describes the fitted sample; a diagnostic rejection concerns one null hypothesis; a smaller observed forecast loss is descriptive; and a properly calibrated rejection of a forecast-loss null supports an inferential claim within a defined target, horizon and sample. These categories cannot be combined into a generic assertion that nonlinear forecasting succeeds or fails everywhere.

**Table 3.9. Status and limits of the baseline empirical findings**

| Empirical finding | What the evidence establishes | What it does not establish |
|---|---|---|
| Nonlinearity diagnostics reject for selected targets | Unemployment, CPI inflation and the federal funds rate exhibit specified departures from linearity | All six processes are nonlinear, or the fitted nonlinear forecasts are superior |
| Full-sample nonlinear BIC is frequently lower | Flexible specifications improve penalized historical likelihood in many cases | Statistically identified recurrent regimes or predictive superiority |
| CPI has interpretable MSAR regime means | A distinguishable higher-mean inflation state is present in the fitted description | A causal inflation mechanism or reliable one-step forecast gain |
| GDP and industrial production have lower MSAR one-step RMSE | Descriptive squared-loss reductions of approximately 29% and 24% against AR on the paired dates | A significant average forecast gain under the primary test |
| No significant MSAR improvement over AR at $h=1$ | The primary test does not establish nonlinear superiority for any of the six targets | Equal forecast accuracy or universal superiority of AR |
| Recession and turning-window MSAR effects are not significant | No supported concentration of nonlinear gains in the retrospectively identified states | Model-independent predictability of recessions or irrelevance of turning points |
| STAR exhibits severe forecast instability in selected targets | Extreme finite forecast errors and limitations of associated statistical inference | A valid claim of equal forecast accuracy from degenerate tests |
| Unemployment model rankings depend on forecast dates | Own-valid and matched-date descriptive comparisons answer different questions | A unique or statistically equivalent ARMA/MSAR ranking |

*Source: Author's synthesis of the empirical results in Sections 3.1–3.6.* *Note:* The table separates descriptive evidence, tests of specified null hypotheses and claims that remain unsupported. A failed rejection is not an equivalence finding; numerical degeneracy is not a hypothesis-test decision.

Three types of vulnerability remain particularly important. The first concerns **specification**. The target transformations and lag orders were selected according to explicit rules, but those rules do not guarantee that the chosen linear AR is the strongest admissible benchmark in every historical environment. In particular, a higher-order AR can absorb persistence that a nonlinear model might otherwise capture. The CPI lag exercise in Section 4.3 addresses this possibility. Alternative level and difference representations for unemployment and the policy rate address a related concern: an apparent nonlinear gain may depend on how persistence is transformed.

The second vulnerability concerns **sample and forecast horizon**. A descriptive gain dominated by a small number of pandemic observations may not survive different estimation-window lengths. A model that cannot improve one-step forecasts might nevertheless have different performance several months or quarters ahead, particularly if its nonlinear dynamics accumulate under iteration. Conversely, increasing the horizon may magnify estimation errors and instability. Chapter 4 therefore examines longer horizons and alternative rolling-window lengths without using them to replace the baseline after the results have been observed. The isolated twelve-month CPI MSAR result is considered with explicit attention to the multiplicity of model, target, horizon and loss comparisons.

The third vulnerability concerns **identification and information**. Two regimes need not be the appropriate number, but adding a third state also need not solve the problem of low occupancy, boundary transitions and local likelihood maxima. Section 4.4 treats the three-state comparison as an in-sample credibility exercise, not as an additional forecasting competitor or proof that the two-state specification is correct. Section 4.6 examines whether a five-variable monthly VAR captures information absent from single-equation autoregressions. This is a test of cross-variable predictive information, not a claim about causal monetary transmission. Quarterly GDP is not interpolated into that monthly system.

Further limits arise from conditional variance, numerical estimation and the historical information set. Volatility clustering can coexist with weak evidence for nonlinear conditional-mean forecasts. A numerical optimizer can return a finite estimate without establishing a globally optimal likelihood. A model whose predictions become extreme at some origins should not be assessed only on attractive surviving dates. Finally, the use of a fixed historical data vintage does not reconstruct the publications and revisions visible at each past origin. These qualifications restrict what can be inferred for operational real-time forecasting.

The scope of generalization must also remain explicit. The six targets come from the United States, and the sample covers its particular inflation episodes, recessions, monetary-policy settings and major shocks. The results are not direct estimates of performance in Lebanon, France or any other economy. Nor do they measure the effect of adopting one model on central-bank decisions or public welfare. What may be transferable is a disciplined approach to forecast evaluation: maintain a credible benchmark, assess residual and regime adequacy, disclose fragile estimates and unavailable forecasts, compare losses on matched dates, and challenge numerical improvements against explicit alternative explanations (Pesaran & Timmermann, 2007; Rossi & Inoue, 2012).

At this stage the baseline question has a defensible answer. The historical sample offers evidence of nonlinear dynamics and occasional descriptive advantages for particular model–target combinations. It does not establish that greater conditional-mean complexity generally improves one-step prediction, including during recessions and around turning points. Chapter 4 tests whether this absence of a general gain is stable to the most consequential alternatives rather than treating the negative result as beyond further examination.

## 3.9 Chapter 3 Concluding Synthesis: Where Nonlinear Complexity Earns Its Place, If Anywhere

This chapter has moved from macroeconomic explanations of instability to evidence about the models proposed to forecast through it. The order of evaluation is important. Before comparing forecast errors, the analysis examined target transformations, stationarity and nonlinearity tests, residual adequacy and the identification of nonlinear parameters. These stages distinguish a plausible statistical departure from linearity from a model that can be estimated and forecast with sufficient credibility. The resulting evidence is more nuanced than a simple ranking of four model names.

The initial tests show target-specific departures from linear autoregressive dynamics. Unemployment rejects under both the Tsay and smooth-transition procedures, while CPI inflation and changes in the federal funds rate reject under the selected smooth-transition test. This is evidence worth examining, not proof that a nonlinear family will forecast better. The tests do not reject for quarterly GDP growth, industrial production growth and M2 growth at the stated significance level. Moreover, the stationarity diagnostics show that the choice of transformation remains a substantive part of the question, especially for inflation and industrial production.

Full-sample estimation often favors the nonlinear specifications in terms of penalized likelihood. Yet the additional parameters are not uniformly credible. The clearest two-state interpretation occurs for CPI inflation, where the model estimates distinguishable lower- and higher-mean states with nontrivial occupancy. For GDP, industrial production and M2, a rare regime is built around very few observations, limiting its interpretation as a recurrent economic process. Unemployment displays extreme state persistence, and the federal funds rate has indistinguishable estimated regime means. Several STAR estimates exhibit poorly located thresholds, transition slopes at parameter bounds or unusable covariance information. Thus a better in-sample fit is not sufficient evidence of a better economic representation.

The primary one-step forecast comparison gives the chapter's central answer. Two-state MSAR does not significantly outperform AR under the Harvey–Leybourne–Zu procedure for any of the six U.S. targets. GDP and industrial production show important descriptive reductions in RMSE, but those advantages are not established statistically and are concentrated in a historically exceptional period. CPI offers an interpretable nonlinear regime without a material one-step improvement. Unemployment's descriptive ordering changes with the alignment of valid forecast dates. The two monetary targets do not exhibit a compelling incremental gain from the fitted Markov structure. A failure to reject equal average forecast accuracy is an absence of evidence of superiority, not evidence of exact equivalence.

STAR does not supply a reliable general alternative. For some targets its iterated forecasts become extraordinarily large. Those observations reveal serious numerical forecasting risk, but the resulting degenerate statistical tests cannot be interpreted as ordinary support for equal predictive ability. Model fragility, observed forecast error and formal statistical inference are separate empirical findings. All three must remain visible when assessing whether a model is a credible candidate for practical use.

The economic-state comparisons further restrict the case for nonlinear forecasting. The AR benchmark's errors are generally larger during historically classified recessions than expansions, and substantial forecast errors accumulate around peaks and troughs. Nevertheless, the conditional loss regressions do not establish that MSAR or STAR gains concentrate in those states. The result survives the distinction between recession and turning indicators, the separation of a joint all-coefficient test from a state-slope test, and sensitivity to different turning-neighborhood widths. These statements concern retrospective evaluation of aggregate forecasts, not the real-time identification or prediction of recession dates.

The findings support a limited general principle: additional complexity earns a role in forecasting only when its fitted mechanism is sufficiently identified, its predictions are admissible, and its relative loss improvement is credible under a stated evaluation procedure. The existence of a nonlinear historical pattern satisfies none of these conditions automatically. Nor does the lack of a general significant gain establish that the simplest model is universally optimal. The contribution of the chapter is to make these distinctions observable for six policy-relevant macroeconomic targets.

The remaining task is to challenge that conclusion. Chapter 4 considers whether alternative transformations, lag structures, estimation windows and forecast horizons change the evidence. It also evaluates the limited three-regime specification, cross-variable information, conditional variance and numerical sensitivity. Those exercises determine whether the baseline absence of general nonlinear superiority is robust or whether a narrowly defined gain survives once competing explanations are considered. The final economic interpretation must remain bounded by the historical U.S. sample and the distinction between predictive accuracy and policy effectiveness.

---

## References

Chauvet, M., & Piger, J. (2008). A comparison of the real-time performance of business cycle dating methods. *Journal of Business & Economic Statistics, 26*(1), 42–49. https://doi.org/10.1198/073500107000000296

Cho, J. S., & White, H. (2007). Testing for regime switching. *Econometrica, 75*(6), 1671–1720. https://doi.org/10.1111/j.1468-0262.2007.00809.x

Dickey, D. A., & Fuller, W. A. (1979). Distribution of the estimators for autoregressive time series with a unit root. *Journal of the American Statistical Association, 74*(366a), 427–431. https://doi.org/10.1080/01621459.1979.10482531

Diebold, F. X., & Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business & Economic Statistics, 13*(3), 253–263. https://doi.org/10.1080/07350015.1995.10524599

Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica, 50*(4), 987–1007. https://doi.org/10.2307/1912773

Giacomini, R., & White, H. (2006). Tests of conditional predictive ability. *Econometrica, 74*(6), 1545–1578. https://doi.org/10.1111/j.1468-0262.2006.00718.x

Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica, 57*(2), 357–384. https://doi.org/10.2307/1912559

Hansen, P. R., Lunde, A., & Nason, J. M. (2011). The model confidence set. *Econometrica, 79*(2), 453–497. https://doi.org/10.3982/ECTA5771

Harvey, D. I., Leybourne, S. J., & Zu, Y. (2025). Testing for equal average forecast accuracy in possibly unstable environments. *Journal of Business & Economic Statistics, 43*(3), 643–656. https://doi.org/10.1080/07350015.2024.2418835

Jarque, C. M., & Bera, A. K. (1987). A test for normality of observations and regression residuals. *International Statistical Review, 55*(2), 163–172. https://doi.org/10.2307/1403192

Kwiatkowski, D., Phillips, P. C. B., Schmidt, P., & Shin, Y. (1992). Testing the null hypothesis of stationarity against the alternative of a unit root: How sure are we that economic time series have a unit root? *Journal of Econometrics, 54*(1–3), 159–178. https://doi.org/10.1016/0304-4076(92)90104-Y

Lenza, M., & Primiceri, G. E. (2022). How to estimate a vector autoregression after March 2020. *Journal of Applied Econometrics, 37*(4), 688–699. https://doi.org/10.1002/jae.2895

Ljung, G. M., & Box, G. E. P. (1978). On a measure of lack of fit in time series models. *Biometrika, 65*(2), 297–303. https://doi.org/10.1093/biomet/65.2.297

Luukkonen, R., Saikkonen, P., & Teräsvirta, T. (1988). Testing linearity against smooth transition autoregressive models. *Biometrika, 75*(3), 491–499. https://doi.org/10.1093/biomet/75.3.491

National Bureau of Economic Research. (n.d.). *Business cycle dating*. https://www.nber.org/research/business-cycle-dating

Odendahl, F., Rossi, B., & Sekhposyan, T. (2023). Evaluating forecast performance with state dependence. *Journal of Econometrics, 237*(2), Article 105220. https://doi.org/10.1016/j.jeconom.2021.07.015

Orphanides, A. (2001). Monetary policy rules based on real-time data. *American Economic Review, 91*(4), 964–985. https://doi.org/10.1257/aer.91.4.964

Pesaran, M. H., & Timmermann, A. (2007). Selection of estimation window in the presence of breaks. *Journal of Econometrics, 137*(1), 134–161. https://doi.org/10.1016/j.jeconom.2006.03.010

Qu, Z., & Zhuo, F. (2021). Likelihood ratio-based tests for Markov regime switching. *The Review of Economic Studies, 88*(2), 937–968. https://doi.org/10.1093/restud/rdaa035

Rossi, B., & Inoue, A. (2012). Out-of-sample forecast tests robust to the choice of window size. *Journal of Business & Economic Statistics, 30*(3), 432–453. https://doi.org/10.1080/07350015.2012.693850

Schwarz, G. (1978). Estimating the dimension of a model. *The Annals of Statistics, 6*(2), 461–464. https://doi.org/10.1214/aos/1176344136

Stock, J. H., & Watson, M. W. (2007). Why has U.S. inflation become harder to forecast? *Journal of Money, Credit and Banking, 39*(s1), 3–33. https://doi.org/10.1111/j.1538-4616.2007.00014.x

Teräsvirta, T. (1994). Specification, estimation, and evaluation of smooth transition autoregressive models. *Journal of the American Statistical Association, 89*(425), 208–218. https://doi.org/10.1080/01621459.1994.10476462

Tsay, R. S. (1986). Nonlinearity tests for time series. *Biometrika, 73*(2), 461–466. https://doi.org/10.1093/biomet/73.2.461

Zivot, E., & Andrews, D. W. K. (1992). Further evidence on the great crash, the oil-price shock, and the unit-root hypothesis. *Journal of Business & Economic Statistics, 10*(3), 251–270. https://doi.org/10.1080/07350015.1992.10509904
