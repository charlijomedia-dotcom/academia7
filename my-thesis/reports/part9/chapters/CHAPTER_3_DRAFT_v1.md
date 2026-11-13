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

This distinction matters economically. The unemployment rate may revert over some periods while its typical level and adjustment speed vary with labor-market institutions and the business cycle. The nominal policy rate is shaped by inflation expectations, reaction functions and lower-bound constraints. A model can therefore face an unstable conditional mean even when a particular unit-root diagnostic favors one conventional transformation. Section 4.2 evaluates alternative representations of unemployment and the federal funds rate as robustness exercises rather than replacing the baseline after seeing the forecasting results.

The chosen data vintage also places a narrower limit on the evidence. Although each rolling forecast omits its later realized target from estimation, the underlying historical observations belong to a fixed information set rather than to the changing publication vintages available at every past forecast origin. The results below identify historical pseudo-out-of-sample performance under that fixed vintage. They are not direct measurements of accuracy achievable by a forecaster operating with each contemporaneous release calendar (Orphanides, 2001).

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

For industrial production, a STAR linearity p-value of $0.0778$ is above the 5% threshold, although smaller than those of several other non-rejecting series. Treating this as a rejection would change the stated decision rule after observing the result. For GDP and M2, the absence of a detected departure is likewise not proof of linearity. Both model classes remain available in the controlled comparison, which permits the predictive contribution of a flexible alternative to be assessed even where a particular preliminary test has limited power.

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

Some raw BIC differences are large. For unemployment, for example, the two-state MSAR has a BIC well below that of the classical specifications, although the fitted state dynamics will be shown to be poorly identified. The correct conclusion is not that the employment process has been proven to follow two stable economic regimes. It is that the particular flexible likelihood captures historical variation much more effectively under its own parameterization. Structural interpretation requires additional evidence about the transition matrix, regime occupancy, parameter uncertainty and the recurrence of estimated states.

The comparison also requires care over effective samples. The reported full-sample AR and ARMA likelihoods do not always use exactly the same number of observations as the MSAR or STAR likelihoods. This difference partly reflects lag orders and likelihood initialization. A single numerical BIC ranking is therefore not a substitute for a common-target forecast comparison. The latter uses matched valid target dates and is the principal basis for the predictive conclusions in Section 3.4.

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

The in-sample assessment therefore yields a constrained conclusion. Nonlinear specifications frequently improve recorded full-sample fit, but they do not uniformly improve residual diagnostics or satisfy all credibility conditions. This leaves open the question of whether their estimated states and transition functions have substantive meaning. The next section examines that issue directly, before the forecasts are ranked.

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

The table reveals several qualitatively different forms of nonlinear fit. The GDP and industrial production MSAR models assign an extremely small proportion of observations to one state. CPI inflation displays a more substantial second state, with distinct estimated mean levels. Unemployment has appreciable state occupancy but exceptionally persistent transitions and imprecise regime means. The federal funds rate produces nearly identical regime means. M2 exhibits a sparse high-growth state. These differences prevent the same substantive explanation from being assigned to every reduction in the nonlinear BIC.

For GDP, the less-populated state has an estimated mean of approximately $-38.14$ in annualized quarterly-growth units, compared with approximately $3.20$ in the other state. Its occupancy share is $0.0032$. With roughly 316 observations contributing to the fitted autoregression, this corresponds to approximately one effective observation. The transition probability associated with leaving the rare state is effectively at its boundary. These features are consistent with the model isolating a very large contraction rather than identifying a regularly recurring state with estimable transition behavior.

This distinction is important in the historical setting of 2020. Large movements in activity around the pandemic can exert exceptional influence on macroeconomic likelihoods. Lenza and Primiceri (2022) explain why those observations complicate conventional VAR estimation. Here, the question is different but the statistical concern is related: a very large disturbance can dominate the flexible likelihood of a single-equation model. A sharp reduction in BIC is therefore not enough to conclude that the GDP series has two economically stable and repeatedly observed growth regimes. The sparse-state diagnosis is an empirical limitation on that interpretation.

Industrial production presents an even more extreme contrast. One state has an estimated mean near $-167.80$ in annualized monthly log-growth units and an occupancy share of approximately $0.0011$. The implied number of effectively assigned observations is about one. The fitted transition matrix also contains probabilities at or near its boundaries, while the parameter covariance estimate is unusable. The result is a strong example of the difference between matching a historical outlier and estimating a stable nonlinear mechanism. Industrial production responds strongly to sudden disruptions in goods production, but the model does not establish that the unusual observation belongs to a recurrent economic state.

M2 is less extreme in numerical magnitude but similar in statistical structure. Its estimated second mean is approximately $53.72$, against $6.35$ in the more prevalent state, and its smaller state has occupancy of only $0.37\%$. This is equivalent to approximately three observations over the fitted sample. The main state's stay probability is effectively one, producing an exceedingly long mechanical expected duration. Such a value should not be interpreted as a forecast that a monetary state will literally last for many centuries. It indicates that the estimated transition dynamics are close to a boundary and that the rare state provides little repeated evidence about switching probabilities.

### 3.3.3 CPI inflation is the clearest regime example, but not a complete model-adequacy success

The CPI model has the most interpretable two-state mean structure of the six targets. The lower estimated mean is $2.56\%$ annualized and the higher mean is $12.49\%$ annualized. The higher-mean state accounts for approximately $8.6\%$ of the fitted sample. Its estimated probability of remaining in that state is approximately $0.8407$, implying an expected duration of $6.28$ months under Equation (3.1). The lower-mean state has an estimated stay probability near $0.9842$, corresponding to approximately $63.1$ months. These figures show a distinguishable high-inflation statistical state that is represented by more than a handful of observations.

This is a descriptive interpretation, not a structural explanation of the causes of inflation. The estimated high-mean state may reflect periods of sustained price pressure, but the model does not identify whether those pressures came from monetary policy, supply constraints, demand conditions or changes in expectations. Neither the sign nor the timing of its state probability is sufficient to identify a causal economic mechanism. The model is useful here because it offers the clearest example of a recurrent difference in fitted means, not because it resolves the structural debate about inflation.

The credibility of the state distinction also does not make the complete CPI forecasting equation adequate on every criterion. The full-sample MSAR residuals reject the Ljung–Box null at both twelve and twenty-four months. This means that, despite the regime-dependent means, detectable dependence remains in the errors. The CPI MSAR fit is accordingly classified as fragile on the full sample because of residual autocorrelation, even though its regime parameters are considerably more interpretable than those for several other targets.

That combination is central to the dissertation's question. A state-dependent description can be statistically interesting and still fail to remove all the conditional-mean dependence relevant for prediction. Moreover, the existence of a high-mean state does not specify how well it can be recognized at the moment a forecast is formed. Smoothed state probabilities use observations after the date being classified; forecast-time probabilities cannot. The distinction between retrospective state interpretation and predictive use is therefore maintained when the rolling forecasts are evaluated.

### 3.3.4 Unemployment and the policy rate: two forms of weak identification

The unemployment MSAR model assigns approximately $91.8\%$ of observations to one state and $8.2\%$ to the other. Occupancy alone would not necessarily rule out this division. The difficulty lies in its estimated transitions and parameter uncertainty. The two stay probabilities are approximately $0.9991$ and $0.9966$, which imply expected durations of roughly 1,092 and 295 months. These durations are exceptionally long relative to the recurring expansions and contractions that a reader might be tempted to associate with unemployment regimes. In addition, the estimated standard errors of the regime means are large relative to their differences in economically plausible unemployment ranges.

The fitted means, approximately $-0.14$ and $10.96$ in unemployment-rate units, should not be read as two precisely identified natural unemployment rates. The negative value and extreme persistence underline the danger of imposing a literal labor-market interpretation on parameters of a difficult nonlinear likelihood. An optimizer can return a high likelihood while portions of the parameter space remain poorly identified. In this case, the MSAR fit also retains residual autocorrelation. It is therefore not justified to interpret the estimated process as a verified model of recurring employment regimes.

The unemployment STAR result is problematic for a different reason. Its estimated logistic threshold is approximately $14.8\%$, outside the central range of historical unemployment observations. The fitted transition is nearly constant over much of the sample, with a reported transition-function standard deviation of approximately $0.0163$. Its parameter covariance is singular. A model with an essentially inactive or poorly located transition cannot provide persuasive evidence that a meaningful change in autoregressive dynamics has been identified, even if a preliminary linearity test rejected the linear null. The disagreement between pretesting and full-sample parameter credibility is thus empirically substantive.

The policy-rate MSAR illustrates a near-complete collapse of the state distinction. The transformed target is the monthly first difference of the effective federal funds rate. The fitted two-state means both round to $0.0025$ percentage points. The transition probabilities describe switching between two labels that have no distinguishable conditional-mean content in this specification. A model that duplicates the same mean across states cannot be interpreted as having uncovered economically distinct monetary-policy regimes merely because it contains a Markov chain.

This result does not disprove the existence of occasionally binding lower bounds or changes in monetary-policy behavior. It shows that a two-state common-variance autoregression of the **change** in the federal funds rate fails to identify those mechanisms through distinct state means in this sample. A shadow-rate model and a regime-switching mean model impose different restrictions and answer different questions. The weak regime diagnosis is therefore a statement about the fitted model, not a universal conclusion about monetary policy.

### 3.3.5 The credibility of smooth transitions

The STAR estimates also differ substantially across targets. For quarterly GDP, the logistic specification has an ill-conditioned covariance matrix, with a reported condition number of approximately $2.79\times10^{16}$. This means that small perturbations can make conventional parameter-uncertainty calculations unreliable. The estimated transition may vary over the observations, but its slope and threshold cannot be regarded as precisely estimated solely because a numerical fit exists.

For unemployment, as noted above, the threshold is outside the central data range and the covariance is singular. Industrial production and the policy-rate change both place the exponential-transition slope at its upper parameter bound. M2 places the logistic-transition slope at its upper bound as well. These outcomes weaken the claim that the observations identify a stable and economically meaningful smooth transition. A parameter at its imposed limit may reflect an abrupt threshold, a nearly constant transition or a flat likelihood in the direction of the slope, depending on the fitted values and the location of observations. Its interpretation requires the behavior of the transition function itself rather than its numerical magnitude alone.

CPI is again the relatively more interpretable case. Its logistic transition is estimated with a six-month delay, a threshold near $3.93$ in the transformed inflation series and a finite transition slope around $2.58$. The parameter covariance is usable. Yet residual autocorrelation remains significant in the full-sample fit, so even this more credible transition should not be treated as a fully adequate forecasting model. The role of this evidence is to motivate a test of predictive value, not to announce a gain before that test occurs.

Together, the full-sample nonlinear estimates lead to a limited conclusion. CPI provides the strongest evidence of a recognizable two-state inflation process. GDP, industrial production and M2 exhibit states built around very few extreme observations. Unemployment and the federal funds rate show different identification problems, including near-absorbing transitions and indistinguishable means. Several STAR thresholds or slopes are poorly identified. These findings do not make every nonlinear forecast invalid. They show that an attractive in-sample criterion often measures something other than a stable state-dependent forecasting mechanism. The actual out-of-sample comparison is therefore decisive.

## 3.4 Out-of-Sample Forecast Performance Against Classical Benchmarks

### 3.4.1 Forecast dates, losses and the appropriate comparison

The forecasting experiment re-estimates each model at every historical origin using 240 monthly or 120 quarterly observations. The primary evaluation horizon is one month for the five monthly targets and one quarter for GDP. The rolling estimation window is held fixed in length, while each model's lag order and other discrete specification choices follow the initial-window selection described in Chapter 2. The target to be predicted is not included in the estimation window at its forecast origin.

A model is evaluated only when its forecast is finite and the corresponding fit satisfies the criteria for retention. An unsuccessful estimate is not silently replaced with a prediction from another family. As a result, a model's own valid forecast dates can differ from those of its competitors. The comparison requires two different pieces of information: the error achieved on the model's own valid dates, and the error difference measured on dates for which the relevant models both have admissible forecasts.

Let $\mathcal I_{m,b,h}$ denote the set of forecast origins at which competitor $m$ and benchmark $b$ both provide retained $h$-step forecasts and share an observed target outcome. The paired loss comparison evaluates the differential $L(e_{m,t+h\mid t})-L(e_{b,t+h\mid t})$ only for origins in that set. An own-valid-sample RMSE is not numerically interchangeable with a paired-sample RMSE if their target dates differ. This distinction is particularly important for unemployment, where a few failed fits and an extreme pandemic observation alter descriptive rankings.

The classical AR forecast is the principal reference because it provides a parsimonious test of whether added complexity improves on own-history persistence. ARMA is retained as a second classical family, testing whether a more general linear innovation structure provides a useful alternative. MSAR and STAR are evaluated both descriptively and through formal loss comparisons. No favorable numerical result is interpreted as statistically established unless the relevant inferential procedure supports it.

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

This sensitivity also has an economic interpretation. The unemployment rate moved abruptly during the pandemic and then adjusted during the recovery. A single observation with a large forecast error can dominate a squared-loss average, particularly for an otherwise stable and persistent rate series. Excluding that observation solely because it is inconvenient would create selection bias. But comparing models on incompatible calendars without disclosure is equally problematic. The analysis therefore reports both own-valid and AR-matched sample sizes, and it does not claim unequivocal MSAR superiority in unemployment forecasting.

At the one-step horizon, STAR's own-sample RMSE is $0.592$ and its mean absolute error is $0.216$, compared with AR's $0.169$ in absolute-error units. This difference is formally assessed below. Although the STAR model can fit unemployment levels closely in-sample, its threshold and covariance problems reduce confidence that its fitted transition has stable predictive meaning.

### 3.4.4 Numerical instability of STAR forecasts

The STAR forecast results are markedly different from the moderate MSAR results. For CPI inflation and industrial production, the reported STAR RMSEs are approximately $5.38\times10^{9}$ and $7.17\times10^{6}$ respectively. They are not typographical errors or truncated axes. They arise from extremely large but finite iterated forecasts produced by unstable fitted parameter combinations at some rolling origins. For M2, STAR's RMSE is $82.745$, against approximately $5.1$ for the linear and MSAR forecasts. These outcomes must remain visible because numerical fragility is part of the performance of the specified forecasting procedure.

A very large RMSE is a descriptive result: it says that squared errors became enormous over the evaluated dates. It is not automatically accompanied by a valid hypothesis-test p-value. When a few loss differentials are many orders of magnitude larger than the others, procedures that estimate a long-run variance or calibrate a reference distribution can become numerically degenerate. In such cases, a reported non-rejection must not be used to claim equal forecast accuracy, and even a formally returned p-value may be uninformative.

This is particularly important for CPI and industrial production STAR comparisons, where the numerical instability of forecasts overwhelms an ordinary presentation of model accuracy. The absence of a reliable formal test conclusion in these comparisons does not erase the enormous observed errors. Equally, the enormity of those errors does not validate an inference procedure whose numerical assumptions have broken down. The dissertation therefore separates the description of the forecasts from the formal assessment of their relative predictive ability.

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

For CPI inflation, the squared-loss p-value is $0.9750$, consistent with the almost identical RMSEs. The absolute-loss test likewise does not reject ($p=0.3980$). For unemployment, the corresponding p-values are $0.3669$ and $0.3217$. Changes in the federal funds rate and M2 growth also yield no rejection in favor of MSAR. A non-rejection does not demonstrate that AR and MSAR have equal predictive ability. It means the data and the chosen procedure do not provide sufficient evidence of a difference at the nominal significance level.

The ARMA comparisons reinforce the need to distinguish the direction of a loss difference from its p-value. For CPI inflation, the absolute-loss comparison rejects at $p=0.0104$, but the mean competitor-minus-AR differential is positive. The evidence favors the AR benchmark over ARMA under this loss definition; it is not evidence that a richer classical family beats AR. Across the other targets, the stated ARMA–AR tests do not reject at 5%. The relative performance of linear alternatives therefore remains target- and loss-specific.

For STAR, the inferential record is more uneven. Where comparisons remain informative, there is no credible general gain over AR. On unemployment at the one-step horizon, STAR is nominally **worse** than AR under absolute loss ($p=0.0015$). For changes in the federal funds rate, the absolute-loss test also favors AR ($p=0.0292$). Both findings concern individual unadjusted comparisons. They should not be inflated into a universal ranking across all targets, horizons and losses.

Other STAR comparisons are compromised by extreme forecasts. In the CPI and industrial production squared-loss results, the enormous loss differences produce numerically degenerate test behavior. The corresponding nominal p-values cannot be interpreted as ordinary evidence of no difference. More generally, the fact that a testing routine returns a number does not prove that its finite-sample calibration remains informative under extreme numerical concentration. The correct conclusion separates an observed catastrophic forecast outcome from the inability to obtain reliable average-accuracy inference in that cell.

The distinction is relevant to the study's broader methodological argument. One may observe a model with a lower historical BIC, a model with a lower descriptive RMSE, a model with a nominally significant average-loss difference, or a model whose numerical failures make the intended test uninformative. These are different evidential states. None should be substituted for another merely to produce a simple claim that nonlinear models either always win or always fail.

### 3.4.6 Multiple-model uncertainty and the meaning of a winner

Pairwise testing is supplemented by the Model Confidence Set (MCS) of Hansen et al. (2011), which assesses sets of models without selecting the smallest sample RMSE as a definitive winner. In the one-step squared-loss exercise, the 90% MCS retains AR, ARMA and MSAR for both GDP and industrial production, despite the numerical MSAR advantage in their respective own-sample RMSEs. That result is consistent with the primary HLZ comparisons: the apparent improvements are not enough to eliminate the classical competitors from the reported set.

The MCS is not an equivalence test. Inclusion of two models does not prove equal predictive ability, and inclusion of a numerically unstable model should not be treated as evidence that its very large errors are harmless. This caution matters because the one-step squared-loss MCS also retains STAR for several targets where STAR's forecast errors are extremely large. The interaction of unusual losses, resampling variability and common-date selection can make formal set membership less discriminating than a simple ranking suggests. The set is therefore read as a supplementary measure of model-selection uncertainty, not as a certificate of adequate numerical behavior.

The unemployment MCS likewise illustrates the sample issue. The four-model exercise uses the intersection of dates available to all members, which is smaller than the dates used for some pairwise comparisons. It therefore addresses a different empirical sample from the own-valid RMSE rankings in Table 3.4. A retained model on the common calendar is not necessarily the lowest-error model on its own larger or smaller calendar. The differences in these comparisons are reported rather than hidden by presenting one universal order.

The secondary Diebold–Mariano/Harvey–Leybourne–Newbold comparison is retained as a sensitivity assessment, not substituted for the primary instability-aware procedure whenever its p-value is more favorable. Diebold and Mariano (1995) established the general loss-differential framework; the choice of variance estimator and finite-sample treatment matters when loss relationships vary through time. Using a fixed primary procedure avoids selecting an inferential rule after observing the direction of its conclusion.

### 3.4.7 What the primary forecast experiment establishes

The baseline evidence supports a bounded answer to the chapter's central question. Two-state MSAR models can describe certain historical observations more closely than classical autoregressions, and their one-step RMSEs are descriptively lower for GDP and industrial production. Yet none of the six MSAR–AR comparisons establishes a significant one-step gain under the primary test. CPI supplies the clearest example of a distinguishable inflation regime without a corresponding one-step forecasting advantage. The federal funds rate and M2 provide cases in which the extra Markov state has weak meaning and no descriptive gain over AR. Unemployment demonstrates why an apparent model ranking must be tied to a clearly stated evaluation calendar.

STAR provides no general positive counterexample. Its one-step forecasts are sometimes less accurate than AR under an informative formal test and sometimes so extreme that the formal comparison itself becomes numerically unreliable. This is not evidence that all smooth-transition methods are incapable of forecasting macroeconomic variables. It is evidence that the selected STAR parameterizations, estimated under the stated protocol, do not establish a dependable advantage in this historical exercise.

Neither result implies that linearity is the true data-generating law for the six targets. The pretests show departures from some linear nulls, especially for unemployment and CPI inflation. The regime diagnostics show that some nonlinear structures are detectable in-sample. What fails to emerge is a general, statistically credible improvement in one-step prediction. Forecast performance must therefore be kept distinct from the existence of nonlinear behavior in the observed series.

A further question remains. The overall averages can conceal performance concentrated in recessions, expansions or neighborhoods of peaks and troughs. It is possible for a model to offer useful gains in a narrow state without reducing its average loss enough to yield a significant whole-sample result. It is equally possible for a model to appear superior in a retrospectively selected episode because extreme observations dominate the losses. Sections 3.5 and 3.6 examine these possibilities using the state definitions and formal conditional comparisons established in Chapter 2. The subsequent cross-aggregate synthesis and robustness analysis assess whether any state-specific interpretation survives changes in the relevant assumptions.

---

## References

Cho, J. S., & White, H. (2007). Testing for regime switching. *Econometrica, 75*(6), 1671–1720. https://doi.org/10.1111/j.1468-0262.2007.00809.x

Dickey, D. A., & Fuller, W. A. (1979). Distribution of the estimators for autoregressive time series with a unit root. *Journal of the American Statistical Association, 74*(366a), 427–431. https://doi.org/10.1080/01621459.1979.10482531

Diebold, F. X., & Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business & Economic Statistics, 13*(3), 253–263. https://doi.org/10.1080/07350015.1995.10524599

Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica, 50*(4), 987–1007. https://doi.org/10.2307/1912773

Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica, 57*(2), 357–384. https://doi.org/10.2307/1912559

Hansen, P. R., Lunde, A., & Nason, J. M. (2011). The model confidence set. *Econometrica, 79*(2), 453–497. https://doi.org/10.3982/ECTA5771

Harvey, D. I., Leybourne, S. J., & Zu, Y. (2025). Testing for equal average forecast accuracy in possibly unstable environments. *Journal of Business & Economic Statistics, 43*(3), 643–656. https://doi.org/10.1080/07350015.2024.2418835

Jarque, C. M., & Bera, A. K. (1987). A test for normality of observations and regression residuals. *International Statistical Review, 55*(2), 163–172. https://doi.org/10.2307/1403192

Kwiatkowski, D., Phillips, P. C. B., Schmidt, P., & Shin, Y. (1992). Testing the null hypothesis of stationarity against the alternative of a unit root: How sure are we that economic time series have a unit root? *Journal of Econometrics, 54*(1–3), 159–178. https://doi.org/10.1016/0304-4076(92)90104-Y

Lenza, M., & Primiceri, G. E. (2022). How to estimate a vector autoregression after March 2020. *Journal of Applied Econometrics, 37*(4), 688–699. https://doi.org/10.1002/jae.2895

Ljung, G. M., & Box, G. E. P. (1978). On a measure of lack of fit in time series models. *Biometrika, 65*(2), 297–303. https://doi.org/10.1093/biomet/65.2.297

Luukkonen, R., Saikkonen, P., & Teräsvirta, T. (1988). Testing linearity against smooth transition autoregressive models. *Biometrika, 75*(3), 491–499. https://doi.org/10.1093/biomet/75.3.491

Orphanides, A. (2001). Monetary policy rules based on real-time data. *American Economic Review, 91*(4), 964–985. https://doi.org/10.1257/aer.91.4.964

Qu, Z., & Zhuo, F. (2021). Likelihood ratio-based tests for Markov regime switching. *The Review of Economic Studies, 88*(2), 937–968. https://doi.org/10.1093/restud/rdaa035

Schwarz, G. (1978). Estimating the dimension of a model. *The Annals of Statistics, 6*(2), 461–464. https://doi.org/10.1214/aos/1176344136

Teräsvirta, T. (1994). Specification, estimation, and evaluation of smooth transition autoregressive models. *Journal of the American Statistical Association, 89*(425), 208–218. https://doi.org/10.1080/01621459.1994.10476462

Tsay, R. S. (1986). Nonlinearity tests for time series. *Biometrika, 73*(2), 461–466. https://doi.org/10.1093/biomet/73.2.461

Zivot, E., & Andrews, D. W. K. (1992). Further evidence on the great crash, the oil-price shock, and the unit-root hypothesis. *Journal of Business & Economic Statistics, 10*(3), 251–270. https://doi.org/10.1080/07350015.1992.10509904
