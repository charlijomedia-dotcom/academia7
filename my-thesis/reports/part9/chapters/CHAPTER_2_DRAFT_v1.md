# Part I: From Macroeconomic Instability to a Testable Forecasting Problem

# Chapter 2: Testing Nonlinear Forecast Value Against Classical Benchmarks: Model Adequacy and Forecast Design

Chapter 1 developed the economic reasons why the relations among inflation, production, unemployment, interest rates and money may change. It also showed why the existence of changing economic conditions does not establish that a nonlinear statistical model will forecast better. This chapter turns that argument into an empirical design. It defines exactly what is forecast, which observations and information are permitted, how classical and nonlinear models compete, when a fitted model is credible, and what evidence can support a claim of forecast improvement.

The purpose is an auditable comparison, not a demonstration that complexity is useful by construction. AR and ARMA models must receive a fair opportunity to represent linear persistence and innovation dynamics. Markov-switching autoregressions (MSAR) and smooth transition autoregressions (STAR) are then asked to improve prediction beyond those competitors. Fit quality, numerical viability, forecast error and statistical significance are assessed separately. The experiment has a limited but useful scope: U.S. historical pseudo-out-of-sample point forecasting from a fixed, reproducible data vintage. No model in this chapter identifies a causal policy intervention, reconstructs every historical real-time data release, or claims an optimal economic policy.

## 2.1 From the Chapter 1 Mechanisms to an Empirical Identification Strategy

The Fisher, Phillips–Phelps, Okun and monetary mechanisms suggest that economic time series can be persistent, asymmetric and state-dependent. They also imply interactions among prices, real activity, unemployment and short-term rates. Yet those mechanisms alone cannot determine which forecasting model will be successful. A theoretical relation may be unstable without being predictable from the series' own lagged observations. Alternatively, a linear statistical model may provide a good forecast even when the underlying economy is structurally complicated. The empirical task is therefore to test a limited predictive proposition rather than infer a complete structural macroeconomic model.

Let $y_{i,t}$ denote one of the six approved forecasting targets, expressed in its selected transformation. A model $m$ issues a forecast at origin $t$ for a target at $t+h$, written $\widehat y^{(m)}_{i,t+h\mid t}$. The relevant object is its predictive error on a target date that was not used for estimating the forecast parameters at that origin.

**Equation (2.1): Forecast error**

```math
e^{(m)}_{i,t+h\mid t}=y_{i,t+h}-\widehat y^{(m)}_{i,t+h\mid t}.
```

The comparison is between errors produced by alternative forecasting procedures under matched target dates and declared information rules. It does not require the fitted statistical model to reproduce all economic mechanisms in Chapter 1. Instead, it asks whether adding particular types of conditional-mean flexibility to a benchmark improves the forecast of an observable target. The model family, horizon, estimation window, target transformation and loss function form part of the research question. A model cannot be described as superior without specifying all of them.

There are three levels of evidence. First, diagnostic tests examine whether simple distributional and dependence assumptions appear defensible. Second, in-sample model adequacy checks whether each candidate can represent observed dynamics without fatal computational or statistical problems. Third, out-of-sample evaluation assesses the forecasts themselves. These stages are related, but they are not interchangeable. Rejecting a linearity test does not demonstrate a useful nonlinear forecast. Finding a lower in-sample Bayesian information criterion (BIC) does not establish predictive superiority. A lower RMSE does not automatically imply a statistically credible gain.

The experimental contrast is also asymmetric in its burden of proof. The AR benchmark is deliberately parsimonious. MSAR and STAR are more flexible, but their flexibility introduces parameters, state estimates, nonlinear optimization and possible forecast failure. Their additional complexity earns a place only when it produces reliable predictive evidence after the same timing and evaluation rules have been applied. Conversely, when a nonlinear method fails to improve a forecast, the experiment does not prove that economic relationships are linear. It shows that the tested type of nonlinearity has not supplied a demonstrable gain under the specified conditions.

The study is predictive rather than causal. It does not identify monetary-policy shocks, estimate structural Phillips-curve slopes, or measure the welfare effects of forecast errors. A regression including only a target's own history cannot distinguish a change in expectations from a changing policy reaction or an exceptional external shock. The limited multivariate robustness exercise in Section 2.7 investigates an omitted-information explanation, but it is not a structural vector autoregression. The advantage of defining these boundaries before viewing the model rankings is that both favorable and unfavorable findings can be interpreted consistently.

Finally, forecast evaluation is historical and pseudo-out-of-sample. Past observations are divided into rolling estimation windows and subsequent target dates. Parameters are estimated without using the target that will be forecast. However, the stored series all come from the fixed historical-vintage information set described next, not from the sequence of data releases available on every earlier forecasting date. This distinction limits claims about genuine real-time performance (Federal Reserve Bank of St. Louis, n.d.; Orphanides, 2001).

## 2.2 Data, Aggregate Selection, Exact Samples, and Frozen-Vintage Policy

### Six targets, five economic blocks, and one external chronology

The empirical design keeps the six targets motivated in Chapter 1. They cover five related but distinct blocks: inflation, real activity, unemployment, monetary policy and the money stock. Each target has an official U.S. source, an established FRED/ALFRED series identifier and a sufficiently long history for repeated rolling forecasts. The selection rule is conceptual rather than opportunistic: a variable is included because the thesis can explain its economic role, measure it reproducibly and evaluate it under the approved forecasting design. No extra target is added because it happens to produce a favorable result.

**Table 2.1. U.S. forecasting variables and usable samples**

| Block and target (FRED ID) | Official underlying source | Frequency | Usable raw levels | Modelled target and first modelled date |
|---|---|---|---|---|
| Prices: CPI inflation (CPIAUCSL) | Bureau of Labor Statistics | Monthly | Jan. 1947–Aug. 2026 | $1200\Delta\ln(\mathrm{CPI})$; Feb. 1947 |
| Labour market: unemployment (UNRATE) | Bureau of Labor Statistics | Monthly | Jan. 1948–Aug. 2026 | Rate in percent, level; Jan. 1948 |
| Real activity: industrial production (INDPRO) | Federal Reserve Board | Monthly | Jan. 1947–Aug. 2026 | $1200\Delta\ln(\mathrm{IP})$; Feb. 1947 |
| Monetary policy: effective federal funds rate (FEDFUNDS) | Federal Reserve Board | Monthly | July 1954–Aug. 2026 | First difference in percentage points; Aug. 1954 |
| Money: M2 stock (M2SL) | Federal Reserve Board | Monthly | Jan. 1959–Aug. 2026 | $1200\Delta\ln(\mathrm{M2})$; Feb. 1959 |
| Real activity: real GDP (GDPC1) | Bureau of Economic Analysis | Quarterly | 1947 Q1–2026 Q2 | $400\Delta\ln(\mathrm{GDP})$; 1947 Q2 |

*Source: Author's computations using official U.S. data from the Bureau of Labor Statistics, Bureau of Economic Analysis and Federal Reserve Board (FRED/ALFRED historical vintage of 5 October 2026).* *Note:* The dates refer to observation periods, not publication dates. The treatment of the two missing October 2025 observations is explained below.

CPIAUCSL is a direct measure of U.S. consumer prices. It is not identical to the Federal Reserve's preferred personal consumption expenditures inflation measure, but its longer postwar history supports the intended analysis of changing inflation dynamics. Industrial production begins earlier than the postwar period, but the study deliberately starts its usable series in January 1947 to avoid importing prewar and wartime industrial regimes absent from most other targets. Quarterly real GDP represents comprehensive real production; monthly industrial production provides more frequent but narrower cyclical information. The two are not converted to an artificial common monthly frequency. UNRATE and FEDFUNDS are already rates, so their modelled representations are determined by stationarity diagnostics rather than automatic logarithms. M2SL is explicitly a monetary aggregate, not a claim that the money supply determines inflation proportionally.

The monthly system has a common usable endpoint of August 2026. September 2026 observations were already available for some series in the historical archive, but not for every monthly target. Extending only those series would change the endpoint unevenly. Quarterly real GDP ends in the second quarter of 2026, the last GDP quarter available in the specified vintage. The full historical reach differs across series because the economic variables were not all recorded over identical periods. The common monthly VAR sample begins in January 1959, when M2 becomes available. These choices were fixed by measurement and information rules, not by a search for favorable forecast results.

The U.S. recession indicator (USREC) is a seventh series with a different function. It follows the National Bureau of Economic Research (NBER) business-cycle chronology as distributed by FRED. It is not a forecast target and is not supplied to the univariate forecasting models as a contemporaneous regressor. It is used after outcomes are realized to classify forecast performance in expansions, recessions and neighborhoods of peaks and troughs. Its later-dated historical labels must not be confused with the information available to a forecaster when a recession was beginning (Chauvet & Piger, 2008; National Bureau of Economic Research, n.d.).

### From official levels to comparable targets

For each positive-valued level series $X_t$ selected for growth-rate modelling, the target is a one-period log change scaled to an annualized percentage rate.

**Equation (2.2): Approved log-growth transformation**

```math
g_t^{(f)}=a_f\bigl(\ln X_t-\ln X_{t-1}\bigr),
\qquad a_M=1200,\quad a_Q=400.
```

Here $a_M$ is the scale for a monthly observation and $a_Q$ is the scale for a quarterly observation. Because the log change is for one native-frequency interval, annualization changes the unit but does not create an annual observation. The transformed monthly CPI, INDPRO and M2 series are expressed in annualized percentage points of continuous growth, as is quarterly real GDP growth. The scaled rates are not year-on-year growth rates and should not be described as twelve-month or four-quarter cumulative growth. This distinction is important when comparing a one-month-ahead target with a twelve-month-ahead forecast horizon.

UNRATE remains in percent in the baseline, because the prescribed initial-window stationarity test supports a level representation. For the federal funds rate, the baseline target is the change in the monthly average rate, $\Delta i_t=i_t-i_{t-1}$, measured in percentage points. It is not a change in the level expressed as an annualized growth rate. The decision rule that produced these two representations is documented in Section 2.3. Alternative level/difference choices are addressed as robustness checks rather than substituted after observing forecast accuracy.

Transformed dates begin one period after the first usable raw level for the four log-growth targets and for differenced FEDFUNDS. The unemployment series is different because its baseline value is the observed rate. All of these targets are compared within their own units. A one-percentage-point error in the unemployment rate is not economically interchangeable with one unit of annualized monthly CPI inflation, so RMSE and MAE must be interpreted within targets rather than used as unscaled cross-target rankings.

### Historical vintage and research-input identity

All inputs originate from the frozen FRED/ALFRED historical information set dated **5 October 2026**. ALFRED permits retrieval of series values as they appeared at a declared vintage date (Federal Reserve Bank of St. Louis, n.d.). The official series and their missing observations are kept distinct from the transformed research data. The transformations and the two documented missing-value treatments determine the estimation sample. This makes the treatment of missing observations explicit and reproducible.

Freezing the data prevents later official revisions from silently altering an otherwise identical estimation. It does not solve real-time information uncertainty. In a true historical release-by-release evaluation, a forecast formed in an earlier year might have had access to a different version of GDP or inflation, and some indicators would not yet have been published. The present experiment does not reconstruct those earlier ragged-edge datasets. Results are therefore evidence about forecasting procedures conditional on the fixed vintage, not about the exact decisions possible with the original information on each historical origin (Orphanides, 2001).

### The two missing October 2025 observations

The frozen 5 October 2026 source has a missing observation at **1 October 2025** for CPIAUCSL and UNRATE. The approved data procedure retains the missing markers in the unmodified source. In the separate derived input, and only there, the September 2025 raw level is carried forward to the October 2025 raw-level cell for each of the two series. The method is last observation carried forward (LOCF). No other data gaps are filled by this rule; the amendment is not permission to impute unexpected observations.

The consequences differ across targets. CPI inflation is calculated from log differences. Since the carried-forward October CPI level equals September's level, computed October 2025 inflation equals zero by construction. The November 2025 growth transformation then compares November with the carried-forward September-level value, so the missing interval is not distributed across October and November. For UNRATE, the October rate is repeated in levels; the observed outcome is replaced by a modelling assumption, not a measured period of unchanged unemployment. These values may influence not only the directly affected target dates, but also later lag vectors, fitted rolling-window parameters, latent-state probabilities and model comparisons.

These two October entries are treated as imputed observations, with September 2025 as the reference month. The original raw data are never represented as though the observations existed. The data treatment is documented in Appendix A, while the sensitivity of the forecast comparisons to these observations is examined in Section 4.2 and Appendix C. The local imputation does not revise the frozen official snapshot or the approved final study endpoint.

This disclosure matters for interpretation. Carry-forward is a pragmatic, traceable way to retain a declared study calendar, but it creates artificial stability at a specific date and may affect surrounding observations. Any inference using those observations is conditional on the authorized choice. Chapter 4 treats their direct and indirect exposure as a robustness threat rather than a factual description of U.S. inflation or unemployment in October 2025.

## 2.3 Stationarity, Persistence, and Structural-Break Evidence Before Model Specification

### Why a transformation decision is necessary

Many macroeconomic levels contain persistent movements that can obscure the meaning of an autoregressive forecast. A model estimated on an integrated series can show very high apparent persistence while its parameters and usual inference have different properties from those of a stationary autoregression. On the other hand, unnecessary differencing can remove useful low-frequency information and make the forecast target more volatile. Chapter 1 distinguished deterministic trends, stochastic trends and structural change. The empirical implementation must now decide which representation is defensible for each variable without choosing it after observing forecast performance.

For positive levels, annualized log differences are the approved baseline targets, and the log levels and transformations are separately tested. The main unresolved decisions involve the unemployment and federal funds rates, both of which can appear persistent in levels. The protocol combines tests with different null hypotheses. It is fixed on the initial estimation window so that future sample information does not determine the representation used for earlier pseudo-out-of-sample forecasts.

### Complementary tests and their null hypotheses

The augmented Dickey–Fuller (ADF) regression tests the null hypothesis that the series contains a unit root. A common regression with an intercept is

**Equation (2.3): ADF regression**

```math
\Delta y_t=\alpha+\rho y_{t-1}
+\sum_{j=1}^{k}\psi_j\Delta y_{t-j}+v_t,
\qquad H_0:\rho=0.
```

The lagged differences reduce residual serial correlation, and the distribution of the test statistic under the unit-root null is nonstandard. The thesis uses an intercept, a BIC-selected augmentation order and a maximum of 12 monthly or four quarterly lags. The 5% decision is based on the appropriate Dickey–Fuller reference distribution, not a standard regression $t$ critical value (Dickey & Fuller, 1979).

The Kwiatkowski–Phillips–Schmidt–Shin (KPSS) test reverses the null: the series is stationary around the included deterministic component. Under the approved intercept specification, it tests level stationarity, allowing a stationary stochastic component. A rejection challenges that null. This contrast is useful because an ADF non-rejection and a KPSS non-rejection do not mean the same thing. Nor does an ADF rejection prove that every feature of the sample distribution is stable over time (Kwiatkowski et al., 1992).

For UNRATE and FEDFUNDS in levels, the Zivot–Andrews (ZA) procedure adds a break-sensitive perspective. It tests the unit-root null against a stationary alternative that permits one endogenous break in the intercept and trend. The implementation uses 15% trimming, BIC lag selection and a 5% decision (Zivot & Andrews, 1992). A dated break chosen by this algorithm is a candidate statistical break, not an identified economic-policy intervention or the NBER date of a recession. Equally, non-rejection does not prove the absence of all breaks. Tests that permit only one break can miss more complicated historical changes.

The decision rules form a hierarchy. If the initial-window ADF rejects a unit root and KPSS does not reject stationarity, the level is retained. If ADF does not reject and KPSS rejects, the first difference is selected. When the two tests disagree, ZA serves as the declared tie-breaker: rejection of its unit-root null permits a level specification with break-sensitive robustness; otherwise the baseline is the first difference. The same tests are then presented for the full sample as corroboration, never as permission to alter the historical baseline retrospectively.

### What the released diagnostics actually select

**Table 2.2. Decision-relevant evidence for UNRATE and FEDFUNDS levels**

| Series and tested sample | ADF p-value ($H_0$: unit root) | KPSS p-value ($H_0$: stationary) | ZA p-value ($H_0$: unit root allowing a break in the alternative) | Implication |
|---|---:|---:|---:|---|
| UNRATE: initial 240 observations | 0.0251 | ≥0.1000 (bound) | 0.1887 | Clear level stationarity under the ADF/KPSS rule; ZA is reported but not the tie-breaker |
| UNRATE: full sample | 0.0028 | 0.0783 | 0.1691 | Full-sample ADF/KPSS agrees with retaining levels |
| FEDFUNDS: initial 240 observations | 0.9530 | ≤0.0100 (bound) | 0.8113 | Clear nonstationarity under the ADF/KPSS rule; first difference selected |
| FEDFUNDS: full sample | 0.1285 | ≤0.0100 (bound) | 0.3203 | Full-sample ADF/KPSS supports the original difference decision |

*Source: Author's computations.* *Note:* KPSS p-values reported as inequalities are bounds of the reference table, rather than exact tail probabilities. All decisions use 5%.

The initial-window evidence resolves the disputed target forms without looking at the later forecast errors. UNRATE is forecast in levels, and FEDFUNDS is forecast in first differences. Both initial- and full-sample ZA tests fail to reject their unit-root nulls even allowing one endogenous break. This does not overturn the declared ADF/KPSS decision because ZA was specified as a tie-breaker only if those two tests disagreed. It does limit any claim that the tested level series has been shown stationary around a single estimated break.

The full frozen-sample tests for the four annualized log-change targets are also informative. ADF rejects the unit-root null for all four transformed series at 5%. KPSS does not reject for GDP growth ($p=0.0529$) and M2 growth ($p=0.0766$), but it narrowly rejects for CPI inflation ($p=0.0494$) and rejects for industrial production growth ($p=0.0355$). These conflicting results should not be concealed behind a blanket statement that all transformed series are stationary. Their existence is consistent with caution about stable moments, level shifts, changing variance or other forms of instability. They do not, by themselves, prove a unit root, a particular break or a STAR-type conditional mean. The approved transformations are retained, with robustness and adequacy checks providing further information.

For comparison, the log levels of GDP, CPI, industrial production and M2 show the opposite general pattern: the ADF unit-root null is not rejected at 5%, while the KPSS stationarity null is rejected. Those tests support the use of log changes for the core point-forecast comparison but do not make the annualization factor or the exact differencing choice a discovered statistical optimum. The stated model definitions are fixed by the scientific design.

Two wider limitations remain. First, unit-root and stationarity tests have finite-sample power, and long U.S. macroeconomic histories contain important changes in policy and volatility. Second, the full-sample results are calculated after the final observations are known. Their job is to challenge or corroborate a rule selected on the initial window, not to provide foreknowledge to the forecast procedure. Chapter 4 revisits transformations and break sensitivity as competing explanations for any apparent nonlinear gains.

## 2.4 Testing for Nonlinearity Before Nonlinear Interpretation

The tests in Section 2.3 concern persistence and the stability of basic distributional features. They do not directly test whether the conditional mean depends nonlinearly on the past. A separate pre-estimation stage is therefore necessary. This responds to the jury's criticism that nonlinear models must not be justified solely because they can be fitted. The stage is diagnostic: it evaluates evidence against specified linear autoregressive dynamics before assigning economic meaning to nonlinear states.

For each target, the selected initial-window AR provides the linear reference. The Tsay (1986) test examines departures from linear autoregression using an auxiliary regression. The operative null is that the conditional autoregressive relation is linear within the tested form. The final implementation uses the documented quadratic, orthogonalized nested-$F$ diagnostic variant. Rejection at 5% indicates evidence against that null; non-rejection means the particular test has not established departure from linearity. Neither conclusion establishes whether MSAR or STAR will produce a more accurate forecast.

The second stage uses the Luukkonen–Saikkonen–Teräsvirta and Teräsvirta specification procedure to assess linearity against STAR-type alternatives (Luukkonen et al., 1988; Teräsvirta, 1994). It compares candidate transition delays of one to six months for monthly series and one to four quarters for GDP. The selected delay is determined by the smallest prescribed linearity-test p-value, with documented tie-breaking, and the established nested-testing sequence selects a logistic or exponential transition. These selections use the initial estimation window, not the future forecasting sample. The test sequence is a model-specification device, not a claim that economic relationships must have a logistic or exponential structure.

The formal distinction can be expressed as follows:

**Equation (2.4): Diagnostic linearity question**

```math
H_0:\ E(y_t\mid\mathcal F_{t-1})\text{ has the selected linear AR form};
\quad
H_1:\ \text{the conditional mean departs from that form.}
```

The alternative in an actual test is narrower than all conceivable nonlinear processes. Tsay's auxiliary form and the STAR-specific sequence can respond to different features. A non-rejection in one test and rejection in another is therefore not automatically a contradiction. Results are reported with the test statistic, reference distribution, p-value, 5% decision and, for STAR, the selected delay and transition function. The target-specific findings are examined in Section 3.1; full diagnostics are presented in Appendix A. No post hoc filter removes a predeclared nonlinear competitor merely because its specification test did not reject.

Markov switching raises a separate testing problem. Under a one-state null, parameters associated with the second state may be unidentified, and some probabilities lie on boundaries. A conventional likelihood-ratio statistic cannot simply be assigned a standard chi-square distribution. Cho and White (2007) and Qu and Zhuo (2021) address these nonregular features. The approved design does not produce an unverified one-state-versus-two-state p-value. MSAR is retained as a theory-motivated forecasting alternative, while its regimes are assessed by occupancy, transition behavior, estimation quality and prediction. The full-sample three-state check is an additional credibility exercise, not a substitute for a valid regime-number hypothesis test.

The governing interpretation rule is simple. A nonlinearity diagnostic is evidence about a specific null and test power; a fitted nonlinear model is evidence about representation; and a subsequent forecast comparison is evidence about prediction. Only the last, when validly conducted, can establish forecast gains. Even then, no statistical state is assigned a structural economic identity without separate evidence.


## 2.5 Classical Forecasting Benchmarks and What Each Benchmark Tests

A nonlinear model can claim added predictive value only relative to a competent classical model. The thesis therefore does not compare a highly tuned nonlinear specification with a deliberately weak AR(1). It uses two classical families, selected on the initial estimation window and then held fixed in their discrete structure. The first captures dependence on the target's own past. The second allows additional dependence on earlier forecast innovations. Conditional-variance and deterministic-trend models are addressed, but their role is determined by the forecasting question rather than by the number of alternatives the study can list.

### Autoregression as the primary reference

For a stationary target $y_t$, an autoregression of order $p$ is

**Equation (2.5): Classical AR model**

```math
y_t=c+\sum_{j=1}^{p}\phi_j y_{t-j}+\varepsilon_t,
\qquad E(\varepsilon_t\mid\mathcal F_{t-1})=0.
```

The intercept $c$ and lag coefficients $\phi_j$ are constant over a given estimation window. An AR is a legitimate forecast model even if economic theory includes other variables: the procedure asks how far information in the target's own history can go. It can represent persistence, delayed adjustment and serial correlation when a sufficient number of lags is used. It does not, by itself, identify the cause of a change in inflation or unemployment.

Monthly AR candidates have lag orders $p\in\{1,\ldots,12\}$, while quarterly GDP candidates have $p\in\{1,\ldots,4\}$. These different grids respect observation frequency and avoid treating 12 quarters as the same statistical adjustment span as 12 months. Within the declared grid, candidates are ranked by the Bayesian information criterion (BIC). A residual-whiteness screen prevents a low BIC from being accepted without checking whether systematic lag dependence remains. Among candidates passing the primary 5% Ljung–Box test, the lowest-BIC model is selected. If every candidate fails, the BIC minimum is retained, but the benchmark is labelled diagnostically weak rather than silently replaced.

BIC balances maximized likelihood against the number of estimated parameters (Schwarz, 1978).

**Equation (2.6): Bayesian information criterion**

```math
\mathrm{BIC}_m=-2\ell_m(\widehat\vartheta_m)+k_m\ln n,
```

where $\ell_m$ is the maximized log-likelihood, $k_m$ the number of estimated parameters and $n$ the estimation-sample size. Smaller BIC values favor models after this complexity penalty, provided the likelihoods concern comparable data and estimands. BIC is an in-sample model-selection device. It does not measure forecast error at future dates and should not be presented as proof that the selected model will win out-of-sample.

The selected AR lag order is fixed from the initial window. At later forecast origins, the same model structure is re-estimated on new rolling observations, as Section 2.9 explains. This prevents a researcher from using later outcomes to select a favorable historical lag order. It also allows estimated coefficients to change as old observations leave and new ones enter the rolling window.

### ARMA as a second classical competitor

The autoregressive moving-average model permits past innovations to influence the current observation in addition to past values.

**Equation (2.7): Classical ARMA model**

```math
y_t=c+\sum_{j=1}^{p}\phi_j y_{t-j}
+\varepsilon_t+\sum_{k=1}^{q}\theta_k\varepsilon_{t-k}.
```

The moving-average coefficients $\theta_k$ describe how recent innovations affect the target within the maintained invertible representation. Under stationarity and invertibility, an ARMA process can capture some serial-dependence patterns parsimoniously that a short AR might otherwise miss (Box et al., 2015). That makes ARMA a serious additional benchmark. A nonlinear model should not be declared useful merely because the initial AR had insufficient innovation dynamics.

For monthly targets, the approved search covers $p,q\in\{0,\ldots,4\}$ excluding the white-noise model $(0,0)$. For quarterly GDP, each order is in $\{0,1,2\}$, again excluding $(0,0)$. The same BIC and residual-screen principle applies, with valid stationarity and invertibility required. Selection is conducted on the initial estimation window and held fixed throughout the baseline forecast evaluation.

ARMA is a broader candidate class, but its selected realization need not have $q>0$. A pure autoregression can be the most defensible choice within the ARMA grid. This occurs for several targets in Table 2.3. The label ARMA therefore identifies the comparison family and its selection rule; it does not guarantee that a nonzero moving-average component has been selected or that it will outperform the primary AR benchmark.

### The actual selected classical specifications

The initial-window estimation gives the following orders. These are initial-window choices, not orders selected from subsequent forecast performance.

**Table 2.3. Fixed baseline linear specifications and inherited nonlinear lag orders**

| Target | AR order | Selected ARMA $(p,q)$ | MSAR lag order | STAR lag order |
|---|---:|---|---:|---:|
| Real GDP growth, quarterly | 1 | (1, 0) | 1 | 1 |
| CPI inflation | 2 | (1, 0) | 2 | 2 |
| Unemployment level | 6 | (3, 4) | 4 | 4 |
| Industrial production growth | 12 | (1, 0) | 4 | 4 |
| Federal funds rate change | 1 | (1, 0) | 1 | 1 |
| M2 growth | 3 | (3, 0) | 3 | 3 |

*Source: Author's computations.* *Note:* MSAR and STAR inherit the selected AR lag orders subject to the limits specified in Section 2.6.

Two features merit explicit notice. UNRATE requires six linear AR lags, and INDPRO requires twelve, while the nonlinear competitors use four. This is an intentional complexity control, not evidence that an unrestricted nonlinear model has been given the same lag span. It makes the baseline AR a demanding own-history competitor and prevents the nonlinear models from multiplying too many state-dependent terms. Second, the selected ARMA for CPI, unemployment and industrial production did not pass the primary residual-whiteness screen even though its BIC-minimizing order was retained. Those weak diagnostic cases remain reported as such. A selected specification is not automatically adequate.

### Conditional variance and polynomial trends

ARCH and GARCH provide an explicit treatment of changing conditional variance. Engle (1982) developed ARCH to represent innovation variance dependent on past squared errors; Bollerslev (1986) extended the model to include past conditional variance. A standard GARCH(1,1) component is

**Equation (2.8): Conditional-variance diagnostic**

```math
\sigma_t^2=\omega+\alpha\varepsilon_{t-1}^2
+\beta\sigma_{t-1}^2,\qquad \omega>0,\quad\alpha,\beta\geq0.
```

This equation concerns the conditional spread of innovations, not necessarily their expected value. The approved design applies ARCH–LM to the selected classical-mean residuals. Where the 5% test rejects constant conditional variance, an ARMA–GARCH(1,1) diagnostic is estimated and its volatility persistence and standardized residuals are reported. A variance model is not credited with point-forecast superiority simply because it fits the variance better. A separate point-forecast comparison would be necessary to make that claim, and it is not the role assigned to GARCH here.

A deterministic polynomial trend, for instance $a+bt+ct^2$, models the level's path as an explicit function of calendar time. It answers a different question from whether shocks and state transitions alter the conditional mean of an approved growth or rate target. Chapter 1 established that deterministic and stochastic trends need not be confused. The baseline transformation protocol removes or addresses the trending levels before fitting the main forecast families. Polynomial extrapolation is therefore excluded from the primary horse race for a scientific reason: it is not an appropriate like-for-like alternative to the specified dynamic forecasts of the transformed targets. If significant deterministic trends persisted in a final target, the approved methodology would require reconsideration before adding such a competitor. No polynomial specification was selected retrospectively to favor or disfavor a model.

This hierarchy directly addresses the jury's concern about classical alternatives. AR provides the primary loss denominator and the transparent benchmark. ARMA tests whether richer linear innovation dynamics alter that conclusion. GARCH examines conditional variance when indicated by evidence. Polynomial trends are excluded from the central transformed-target contest with an explicit rationale. The nonlinear candidates must now justify the additional complexity they introduce.

## 2.6 State-Dependent Alternatives and Their Economic Interpretation

The thesis retains two nonlinear conditional-mean families. MSAR permits discrete changes among latent statistical states, while STAR permits a smooth change in autoregressive coefficients according to an observed transition variable. They express different hypotheses about the form of nonlinearity. Neither is automatically a structural model of economic recessions, and neither should be judged solely by its full-sample likelihood.

### A two-state Markov-switching autoregression

The baseline MSAR follows the parsimonious Hamilton-style idea of a state-dependent mean with common autoregressive coefficients and a common innovation variance (Hamilton, 1989). Let $s_t\in\{1,2\}$ be an unobserved state at date $t$. The model is

**Equation (2.9): Baseline two-state MSAR**

```math
y_t=\mu_{s_t}
+\sum_{j=1}^{p}\phi_j\bigl(y_{t-j}-\mu_{s_{t-j}}\bigr)
+\varepsilon_t,\qquad
\varepsilon_t\sim N(0,\sigma^2).
```

The regime means $\mu_1$ and $\mu_2$ may differ; the autoregressive coefficients $\phi_j$ and innovation variance $\sigma^2$ do not switch in this baseline. Lagged deviations are centered on the state belonging to each lagged observation. This detail matters because a simpler expression with only one common lagged mean would define a different parameterization. The nonlinear term here arises from the sequence of unobserved states, not from an observed unemployment or output threshold.

The state process follows a first-order Markov chain. Define $p_{ij}=\Pr(s_t=j\mid s_{t-1}=i)$ for $i,j\in\{1,2\}$. Each row of the transition matrix sums to one:

**Equation (2.10): Markov transition matrix**

```math
P=
\begin{pmatrix}
p_{11} & 1-p_{11}\\
1-p_{22} & p_{22}
\end{pmatrix},
\qquad
p_{ij}\in[0,1].
```

The parameter $p_{11}$ is the probability of remaining in state 1 for one period, and $p_{22}$ is the probability of remaining in state 2. Conditional on a homogeneous transition process, the expected duration of state $i$ is $1/(1-p_{ii})$ periods when $p_{ii}<1$. This is a property of the estimated Markov chain. It is not an estimate of the average length of U.S. recessions unless an additional empirical identification exercise establishes that the state corresponds to recessions.

Because $s_t$ is hidden, the model estimates probabilities of being in each state rather than observing the state directly. Filtered probabilities condition on information available up to a date; smoothed probabilities also use subsequent observations. Smoothed probabilities can describe the historical allocation of observations to states, but they must not leak into a forecast from an earlier origin. A pseudo-out-of-sample forecast requires a distribution over future paths based on information available at that origin. State uncertainty is integrated into the forecast, not resolved by looking at the realized future path.

A two-state model may distinguish periods with different average inflation, output growth or rate changes. It cannot be assumed to distinguish recession from expansion. The same NBER recession can contain different monetary conditions, and a high-inflation or policy-rate state can occur in either phase of the business cycle. Ordering states by their estimated means provides a stable way to avoid purely nominal label switching across reported tables. Economic labels are withheld until occupancy, persistence and historical correspondence have been inspected.

The lag order $p$ is inherited from the initially selected AR, with a cap of four lags for both monthly and quarterly series. The cap limits proliferation of parameters in the nonlinear estimation. Under this design, the statistical difference from an AR concerns regime-dependent means and the implied state history rather than an unrestricted collection of regime-dependent slopes and variances. This makes the comparison more interpretable and computationally manageable, while also excluding potentially useful state-dependent variances or coefficients. Such exclusions are part of the model's stated scope.

The full-sample regime display reports ordered means, transition probabilities, expected durations, smoothed occupancy and estimation status. Occupancy is the effective number of observations allocated to a regime, calculated from the sum of its smoothed probabilities. A state receiving almost no effective observations cannot support precise statements about a recurring economic regime. A transition probability close to one may indicate extreme persistence, but it may also indicate weak identification near a numerical boundary. Section 2.11 defines the operational warnings used to separate these cases from credible inference.

The issue of regime-count selection is deliberately postponed to a bounded robustness exercise. A one-state versus two-state likelihood-ratio test does not have an ordinary chi-square null distribution because of unidentified nuisance parameters and boundary complications (Cho & White, 2007; Qu & Zhuo, 2021). The thesis does not add a naive significance claim. The baseline retains two states for the forecast comparison. A three-state version is assessed on the full sample only, with no K=3 rolling forecast exercise. Its precise conditions appear in Section 2.12.

### A smooth transition autoregression

STAR describes a different process. The conditional mean changes smoothly as an observable transition variable moves through part of its range. Let $x_t=(1,y_{t-1},\ldots,y_{t-p})'$ contain an intercept and lagged values, and let $z_{t-d}$ denote the lagged transition variable selected at delay $d$. A generic STAR model is

**Equation (2.11): Smooth transition autoregression**

```math
y_t=\boldsymbol\phi'x_t
+G(z_{t-d};\gamma,c)\boldsymbol\theta'x_t+\varepsilon_t.
```

The coefficients $\boldsymbol\phi$ describe one limiting dynamic relation; the incremental coefficients $\boldsymbol\theta$ describe how that relation changes as the transition function $G$ moves from near zero toward one. Parameter $c$ is a transition location and $\gamma>0$ controls transition speed under the conventional normalization. The delay $d$ identifies which lagged observed condition governs the transition. Unlike the Markov model, the transition is conditional on a specified observed variable rather than an unobserved probabilistic state.

The two admissible functions are logistic STAR (LSTAR) and exponential STAR (ESTAR). Conventional definitions, before any equivalent numerical scaling used for optimization, are

**Equation (2.12): Logistic and exponential transition functions**

```math
\begin{aligned}
G_{\mathrm{L}}(z;\gamma,c)
&=\left[1+\exp\{-\gamma(z-c)\}\right]^{-1},\\
G_{\mathrm{E}}(z;\gamma,c)
&=1-\exp\{-\gamma(z-c)^2\}.
\end{aligned}
```

The logistic function distinguishes observations below and above a location in an asymmetric way. The exponential function instead depends on the squared distance from that location and can distinguish normal middle observations from both types of extreme departures. These are statistical patterns, not evidence that the economy switches between identified demand and supply shocks. The transition type and delay come from the initial-window Teräsvirta procedure, not from a later examination of which forecast model wins (Luukkonen et al., 1988; Teräsvirta, 1994).

The distinction also exposes an estimation risk. An estimated transition can be nearly constant across the observed data, so the nominally nonlinear terms are weakly identified. A very large estimated smoothness coefficient can make a smooth transition function approximate a sharp threshold. A threshold far outside the observed central range may leave the model effectively on one side of the transition. These cases can have an acceptable likelihood but supply little credible evidence of a meaningful economic state. They receive explicit fragility flags.

The STAR lag order is inherited from the initial AR, capped at four lags monthly and two quarters for GDP. The permitted delays are one to six months or one to four quarters. These restrictions limit the size of the nonlinear estimation problem and maintain a transparent comparison. They also mean that STAR may use fewer own-history lags than the primary AR for some targets; that difference is disclosed in Table 2.3 rather than treated as a hidden advantage or ignored limitation.

The final initial-window STAR selections were LSTAR with delays 3 for GDP, 6 for CPI, 1 for unemployment and 5 for M2; and ESTAR with delays 4 for industrial production and 1 for the federal funds rate. They follow the specification procedure described above. The preliminary STAR linearity screen rejected at the chosen delay for CPI, unemployment and the federal funds rate, but not for GDP, industrial production or M2. These outcomes describe a pre-estimation diagnostic under one specific test. Chapter 3 assesses what subsequently happened to fit and forecast quality.

### Comparing the two nonlinear hypotheses

MSAR and STAR should not be merged conceptually. The former allows an unobserved discrete state to change a model's conditional mean, with transition probabilities that must be estimated. The latter modifies autoregressive coefficients through a continuous function of an observed lagged transition variable. MSAR may be useful if changes recur in distinct statistical regimes; STAR may be more suitable when adjustment varies smoothly with a measurable condition. Both can fit an episode unusually well and fail to forecast the next one. Both are vulnerable to limited observations in unusual states, nonlinear optimization and historical breaks that do not repeat.

**Table 2.4. Model families, additional flexibility and their diagnostic burden**

| Family | Conditional-mean mechanism | Main added estimation burden | What it does not identify |
|---|---|---|---|
| AR | Constant coefficients on past target values | Lag order, stability, residual dependence | Causal macroeconomic relationships |
| ARMA | AR plus past innovations | Moving-average order, invertibility, residual dependence | Structural shocks merely from innovations |
| MSAR(2) | Two latent-state means, common slopes and variance | State probabilities, transition matrix, occupancy, numerical maxima | NBER phases or structural policy regimes |
| STAR | Smooth coefficient transition using observed lagged state | Threshold, smoothness, transition delay/type, nonlinear identification | A causal threshold or unique economic state |
| VAR (robustness) | Lagged cross-variable information in a linear system | Common data calendar, joint lags, stability | Causal transmission absent structural restrictions |

*Note:* This table summarizes the declared comparison, not in-sample or out-of-sample rankings. Complete specification details and parameter estimates are presented in Appendices A and B.

A hybrid model combining Markov switching and smooth transition is not included. Its simultaneous use of two distinct nonlinear mechanisms would increase the identification burden and complicate the interpretation of any forecast difference. The separate MSAR and STAR specifications provide a clearer comparison of discrete and smooth state dependence within the stated research question.

## 2.7 Cross-Variable Information and the Boundary of Single-Equation Forecasting

The main AR, ARMA, MSAR and STAR forecasts are single-equation exercises. Each target is forecast from its own history and, where applicable, its state-dependent dynamics. Chapter 1 nevertheless described economic interactions among prices, interest rates, output, employment and money. An apparent nonlinear pattern may therefore be a proxy for information missing from the single-equation information set. This is a legitimate competing explanation and requires a focused multivariate response.

The approved robustness model is a five-variable monthly vector autoregression (VAR), following the general multivariate forecasting framework of Sims (1980). Define the vector of monthly transformed targets as $Y_t=(\pi_t,\;g_t^{IP},\;u_t,\;\Delta i_t,\;g_t^{M2})'$, where the unemployment rate is in levels and the federal funds rate is in first differences. The VAR is

**Equation (2.13): Five-variable monthly VAR**

```math
Y_t=a+\sum_{j=1}^{p}A_jY_{t-j}+v_t,
\qquad p\in\{1,2,3\}.
```

The matrices $A_j$ allow one variable's past to contribute to forecasts of the others. The lag order is selected by BIC within the approved range, and estimated roots must satisfy the VAR stability condition. All five official series are available in raw form from January 1959; log-difference transformations and lag requirements shorten the fully aligned estimation sample. The system respects native monthly spacing and the approved October 2025 input rule.

This check asks whether cross-variable information changes model rankings or explains some failures of own-history forecasting. It does not estimate a structural Phillips relationship, identify a monetary-policy shock, or distinguish demand from supply shocks. Without identifying restrictions, the VAR innovations are reduced-form residuals, not a set of independently interpreted economic disturbances. A better VAR forecast would therefore support a bounded omitted-information explanation, not prove which channel caused the gain.

Quarterly GDP remains quarterly. It is not duplicated, interpolated or mechanically repeated across three months to insert it into the monthly VAR. A mixed-frequency VAR, MIDAS model or true release-calendar nowcast would have different information sets and additional research demands. Giannone et al. (2008) illustrate how the publication timing of mixed-frequency indicators matters for nowcasting. Carriero et al. (2025) show that explicit rate constraints can also be represented in a VAR. Those methods are serious alternatives, but neither is silently substituted for this thesis's declared, narrower robustness system.

The multivariate experiment therefore has a clear interpretation. If it changes a target's forecast ranking, information omitted from the univariate models may help explain the earlier result. If it does not, the thesis cannot claim that cross-variable interactions are unimportant under all specifications; the VAR is small, linear, monthly and constrained to the five selected indicators. Its purpose is to challenge one explanation, not to settle the broader literature on macroeconomic forecast systems.

## 2.8 In-Sample Model Adequacy as a Prerequisite for Forecast Interpretation

An econometric model can yield a plausible forecast even if its fitted residuals show important weaknesses. It can also obtain a strong likelihood while relying on nearly unobserved regimes or parameters at numerical boundaries. The revised design therefore uses in-sample adequacy as a distinct stage before presenting forecast rankings. This follows the jury's requirement that models must first earn the right to be interpreted as credible descriptions of the data. It does not imply that good historical fit is enough to establish predictive usefulness.

The common descriptive measures are maximized log-likelihood where meaningful, Akaike and Bayesian information criteria (Akaike, 1974; Schwarz, 1978), in-sample RMSE, and in-sample MAE. They answer different questions. Likelihood and information criteria describe a fitted probability model and its parameter penalty; RMSE gives relatively more weight to large residuals; MAE describes average absolute deviation. None is an independent out-of-sample forecast. Across different target units or nonmatching samples, raw magnitudes are not directly comparable.

The diagnostic tests include Ljung–Box for residual serial correlation, ARCH–LM for remaining dependence in squared innovations, and Jarque–Bera for distributional normality (Jarque & Bera, 1987). The primary Ljung–Box residual-screen horizons are 12 and 24 lags for monthly targets and four and eight lags for quarterly GDP (Ljung & Box, 1978). ARCH–LM is applied at 12 monthly or four quarterly lags. The significance level is 5%. Jarque–Bera is reported because distributional shape matters to likelihood-based inference, but rejection of normality alone is not treated as a fatal failure for a point-forecast model. During rare shocks, a useful mean forecast can coexist with heavy-tailed residuals.

A general residual-autocorrelation null can be written as

**Equation (2.14): Primary residual-whiteness null**

```math
H_0:\;\rho_{\varepsilon}(1)=\rho_{\varepsilon}(2)=\cdots=\rho_{\varepsilon}(K)=0.
```

Rejection means that the fitted residuals retain evidence of serial dependence over those lags. Non-rejection does not prove that innovations are independent or that the model is structurally correct. The reported test tables must include the null, statistic, reference distribution, p-value, 5% decision and its practical implication. Applying these tests consistently gives a common adequacy language even though the models have different internal state mechanisms.

A second adequacy layer is model-specific. AR and ARMA must satisfy their stability and invertibility requirements. An MSAR fit needs meaningful occupancy and transition behavior; a STAR fit needs an identifiable transition and finite parameters. A model may have residual autocorrelation but a converged, usable forecast, in which case it is classified as fragile. A failed optimization or non-finite prediction is not treated as an ordinary forecast observation.

The classification follows three categories. An adequate fit has converged, contains finite parameters, satisfies mandatory stability restrictions, has no fatal structural warning and passes the primary residual-whiteness screen. A fragile fit converges but carries warnings such as residual autocorrelation, low regime occupancy, near-boundary probabilities, uncertain covariance or extreme but finite forecast behavior. A failed fit is unusable because of nonconvergence, non-finite likelihood or parameters, invalid essential covariance, violated mandatory stability, an effectively empty regime or a non-finite forecast path. The numerical thresholds behind these categories are operational flags explained in the next section, not confidence levels from a statistical theorem.

The separation is essential for scientific interpretation. A fragile forecast can still be evaluated if the value is finite and the common-date rule permits it, but its regimes should not receive strong economic names. A failed forecast remains visible in the estimation audit and is not quietly replaced by an AR forecast under its original model label. The effect of excluded failed origins on the matched comparison is disclosed. This lets the reader distinguish a model that forecasts poorly, a model that has insufficient statistical evidence of an advantage, and a model that cannot reliably supply a forecast at all.

Chapters 3 and 4 use these categories in different ways. Chapter 3 first examines full-sample adequacy and credibility before presenting the baseline horse race. Chapter 4 asks whether warning rates, alternative specifications and numerical fragility undermine any forecast advantage. Neither chapter treats a lower BIC as a sufficient forecasting result. The methodological distinction between representation and prediction remains binding.


## 2.9 Forecast Experiment: Origins, Windows, Horizons, and Re-estimation Policy

### Rolling estimation as a response to instability

A historical forecast comparison needs a rule for when estimation ends and evaluation begins. Fitting a model to the complete sample and then reporting its fitted values as forecasts would allow future information to influence earlier predictions. The approved design instead creates a sequence of forecasts at historical origins. At each origin, each model is estimated from a fixed number of preceding observations, produces a prediction for a later target date, and is then assessed against the realized target when it becomes part of the evaluation record.

The baseline estimation-window lengths are 240 observations for monthly targets and 120 observations for quarterly GDP. These represent 20 years of monthly data or 30 years of quarterly data. They were selected as a compromise among parameter precision, the need to observe more than one economic episode, and adaptation to possible change. They are not mathematically optimal window lengths. A shorter window can respond more rapidly to a break but leaves fewer observations to identify nonlinear parameters. A longer window can estimate a stable model more precisely but may mix distinct historical relationships. Pesaran and Timmermann (2007) and Rossi and Inoue (2012) explain why estimation-window choice matters for forecast performance and its inference.

Let $w_f$ be the baseline number of observations at frequency $f$, and let $t$ denote a valid forecast origin on the native monthly or quarterly calendar. The rolling window is

**Equation (2.15): Fixed-length rolling sample**

```math
\mathcal W_t^{(w_f)}
=\{y_{t-w_f+1},y_{t-w_f+2},\ldots,y_t\},
\qquad w_M=240,\quad w_Q=120.
```

Every model for a given target uses the same chronological definition of the estimation window. The earliest eligible origin depends on the target's first transformed observation and the needed lag structure. The evaluation series therefore begin on different dates across targets. It would be misleading to treat those dates as evidence that one variable is easier to predict than another; differences in history, units and available forecasts must be acknowledged.

The design is intentionally not a single fixed-parameter exercise. Estimated parameters are refitted at every valid forecast origin using the trailing rolling window. At the next origin, the oldest observation leaves and the newest eligible observation enters. Forecasting procedures are therefore allowed to update their parameters without observing the target outcome they are trying to predict. This is particularly important for MSAR and STAR because regime probabilities and nonlinear parameters may change as new episodes enter the estimation record.

### Fixed specifications, updated parameters

There is a distinction between selecting a model's discrete structure and estimating its parameters. AR lag orders, ARMA orders, STAR type and delay, and the related nonlinear lag caps are selected once from the initial baseline estimation window. They are then kept fixed in the main experiment. The coefficients, regime means, transition probabilities and other estimable quantities are updated at each forecast origin. This avoids an enormous repeated specification search, but it does not freeze the statistical model at its first fit.

The rule prevents an important kind of look-ahead bias. If lag order were chosen after evaluating all future forecast losses, it could reflect information unavailable at the early forecast origins. Fixing the structure from the initial window avoids that retrospective selection. It also creates a limitation: the initially selected structure may no longer be ideal after a major break. The approved sensitivity exercises assess some such threats, but the baseline does not change its selection rule to improve results after they are known.

The practical workflow is: select the discrete model structure on the initial window; refit each model on the current rolling data; check the fit and any forecast failure; issue the horizon-specific forecast using only eligible information; store the prediction and its provenance; advance to the next origin. This sequence is applied under the same date and admissibility conventions for all four core families. The detailed calendars, cache keys and optimizer settings are recorded outside the main body.

### Forecast horizons and their interpretation

The primary question uses **one-step-ahead forecasts**: one month for each monthly target and one quarter for GDP. The horizon is measured in native observation periods, not in a shared number of calendar days. A one-quarter-ahead GDP forecast is therefore not the same time span as a one-month-ahead CPI forecast, although each is one step for its own series.

The longer-horizon robustness choices are $h\in\{3,6,12\}$ months for monthly targets and $h\in\{2,4\}$ quarters for GDP. They are obtained through iterated forecasts from the fitted dynamic model. For a general nonlinear model, this requires propagation of the state-dependent dynamics and, where relevant, state probabilities, rather than substituting the one-step forecast into an unrelated formula. Longer horizons test whether the relative value of nonlinear structure changes with the forecast distance. They do not replace the baseline $h=1$ answer.

At $h>1$, forecast errors can overlap across origins, even with a correctly specified model. Consecutive forecasts of distant target dates may share underlying shocks, so an evaluation test cannot treat all loss differences as independent observations. Horizon-appropriate long-run variance or correction procedures are therefore part of the formal comparison in Section 2.10. The number of valid matched target dates must also be reported separately by horizon, because changing the horizon changes both forecast availability and the statistical evidence.

Warm starts and caching improve the feasibility of the exercise without changing its scientific definition. A previous successful nonlinear parameter vector can serve as a starting value for the next rolling fit when technically appropriate. Fitted results are keyed by series, model, origin, specification and input-window identity. A valid repeat uses the stored result rather than re-estimating the same problem unnecessarily. Yet a warm start does not prove that the optimizer found a global likelihood maximum. Numerical uncertainty remains part of the assessment.

### Comparability across procedures

The essential requirement is that competing models face the same prediction problem. They must use the approved transformed target, comparable historical dates, the same horizon definition, and the same baseline rolling-window length. A method that cannot produce a valid forecast at an origin does not receive an invented substitute forecast. Its missing outcome is recorded; pairwise comparisons are then formed on the shared valid dates for the two models, and multiple-model comparisons use the intersection valid for their members. This creates a trade-off between a fair matched comparison and the number of usable dates. Both the matched sample size and the dates lost to failures remain visible.

The baseline thus represents a controlled historical forecasting exercise. It is credible as a pseudo-out-of-sample comparison because later target outcomes are excluded from each origin's estimation. It is not equivalent to a full real-time experiment that preserves each information release and later data revision (Orphanides, 2001; West, 1996). That limitation is held constant across the competing model families and revisited in the dissertation's interpretation.

## 2.10 Forecast Evaluation Across Normal Periods, Recessions, Expansions, Peaks, and Troughs

### Common loss measures

Forecasting performance is evaluated through observable prediction errors, not by selecting a model from in-sample information criteria. Three principal descriptive measures are reported: root mean squared error (RMSE), mean absolute error (MAE), and out-of-sample $R^2$ relative to the AR benchmark. For a model $m$ with $N$ valid evaluation dates, they are

**Equation (2.16): Point-forecast accuracy measures**

```math
\begin{aligned}
\mathrm{RMSE}_m
&=\left(N^{-1}\sum_{t=1}^{N}e_{m,t}^{\,2}\right)^{1/2},\\
\mathrm{MAE}_m
&=N^{-1}\sum_{t=1}^{N}|e_{m,t}|.
\end{aligned}
```

RMSE penalizes very large errors more strongly than MAE. This is relevant when the evaluation period contains pandemic observations, sharp monetary-policy changes or an unstable nonlinear forecast. Neither measure estimates the welfare cost of making an error. Each must be reported with the units and target of the forecast, so a large number for annualized industrial production growth is not mechanically compared with the numerical level of an unemployment-rate error.

Out-of-sample $R^2$ is defined against the declared AR forecast over identical target dates:

**Equation (2.17): AR-relative out-of-sample performance**

```math
R^2_{\mathrm{OOS},m\mid AR}
=1-
\frac{\sum_{t\in\mathcal I_{m,AR}}e_{m,t}^{\,2}}
{\sum_{t\in\mathcal I_{m,AR}}e_{AR,t}^{\,2}}.
```

The set $\mathcal I_{m,AR}$ contains only dates on which both model $m$ and AR have valid observed outcomes and forecasts. A positive value means that the competitor's total squared error is lower on those shared dates; a negative value means it is higher. The denominator can be small or unstable for a highly predictable target or a small evaluation subsample. The statistic is descriptive, not itself a hypothesis test. When the benchmark denominator or shared sample is unusable, the comparison must be marked unavailable rather than treated as zero.

Mean absolute percentage error (MAPE) is not reported. Several modelled targets, including changes in interest rates and annualized monthly growth, can be negative or close to zero. Dividing forecast errors by such realized values can create unbounded or economically misleading percentages. Hyndman and Koehler (2006) provide a general critique of these accuracy measures. RMSE, MAE and AR-relative $R^2$ better serve the present target transformations.

### Pairwise tests and the primary inferential rule

Descriptive accuracy differences can arise by chance. The core inferential object is the loss differential between a competitor $m$ and benchmark $b$ at the same forecast target date.

**Equation (2.18): Signed paired loss differential**

```math
d_t^{(m,b)}
=L(e_{m,t})-L(e_{b,t}),
\qquad
L(e)\in\{e^2,|e|\}.
```

A negative mean loss differential favors the competitor, because it has lower loss; a positive mean favors the benchmark. The five approved pairwise comparisons are AR versus ARMA, AR versus MSAR, AR versus STAR, ARMA versus MSAR, and ARMA versus STAR. Both squared-error and absolute-error losses are tested. The model-pair names do not erase the explicit sign convention, which must be stated in every inference table.

The **primary test** is Harvey, Leybourne and Zu (2025), abbreviated HLZ. It addresses the null of equal average forecast accuracy when the expected loss differential may vary over the evaluation period. The basic average-null question is

**Equation (2.19): Equal average predictive accuracy**

```math
H_0:\frac{1}{N}\sum_{t=1}^{N}E(d_t^{(m,b)})=0,
\qquad
H_1:\frac{1}{N}\sum_{t=1}^{N}E(d_t^{(m,b)})\neq0.
```

This formulation deliberately concerns average accuracy. It does not require the relative advantage to be identical in every recession, expansion or subperiod. Harvey et al. (2025) show that the conventional Diebold–Mariano long-run variance estimate can behave poorly when the mean loss differential varies through time. Their modification uses local nonparametric demeaning in the variance construction. The test uses the prescribed local-demeaning kernel, bandwidth choice and critical-value calibration rather than a generic heteroskedasticity- and autocorrelation-consistent approximation. The paper supplies a direct justification for the predeclared test under possible instability.

The primary interpretation uses two-sided inference at the 5% level. A rejection, together with a negative estimated mean differential, supports a claim of lower average loss for the competitor in that pair, target, horizon and sample under the specified test. A positive mean differential after rejection supports the reverse directional comparison. A non-rejection means that equality of average loss was not rejected; it is not evidence that the forecasts have exactly the same skill. If the long-run variance or reference calculation is not numerically valid, no p-value is invented and the inference is recorded as unavailable.

The conventional Diebold–Mariano test (Diebold & Mariano, 1995), with the Harvey–Leybourne–Newbold small-sample modification (Harvey et al., 1997), is retained as a **secondary** analysis. Its comparison set and losses match the primary test, and the long-run variance treatment accounts for overlapping multi-step forecasts. Differences between DM–HLN and HLZ conclusions are reported rather than resolved by choosing whichever test favors a particular model. The primary decision follows HLZ because instability in relative forecast loss is part of the thesis's economic motivation.

A further issue is multiplicity. Many models, targets, losses, states and horizons generate multiple opportunities to observe a small p-value. A nominal 5% rejection in one isolated cell should not be presented as a general law of nonlinear superiority. The approved analysis preserves the declared primary and secondary tests, reports the family of comparisons, and treats broader multiplicity checks as an explicit limitation or audit rather than changing the primary inferential rule after the fact.

### Comparing several admissible models

Pairwise tests do not answer whether a model is uniquely superior among all admissible competitors. The Hansen–Lunde–Nason Model Confidence Set (MCS) procedure provides a complementary multiple-model assessment (Hansen et al., 2011). It sequentially evaluates a set of models under a chosen loss and reports those retained at the declared confidence level. The thesis reports 90% and 95% MCS results under squared and absolute losses.

For a valid MCS calculation, all included models must have loss observations on a common target-date intersection. That intersection may be smaller than the date set for any particular pair. If too few valid observations or an unusable variance calculation prevents meaningful inference, the procedure is marked unavailable. MCS membership is not proof that all retained models are equally accurate, nor does exclusion automatically identify a uniquely best causal forecasting mechanism. It is an inferential complement to the pairwise and descriptive evidence.

Clark and West (2007) develop tests for certain nested forecast comparisons. The central AR/MSAR and AR/STAR cases here involve nonregular nonlinear restrictions and hidden or weakly identified parameters under linearity, so their framework is not mechanically inserted as an additional baseline test. Amisano and Giacomini (2007) address density forecasts using weighted likelihood scores. The present study compares point forecasts and does not build a common validated predictive-density system. These are explicit scientific exclusions, not omissions of relevant statistical vocabulary.

### Recession and expansion evaluation

Overall average loss may conceal economically meaningful differences across phases. The thesis therefore evaluates RMSE and MAE separately for observations that are retrospectively classified as recession or expansion dates. It uses USREC, based on NBER business-cycle dates, at the forecast target date. For a monthly target, USREC equal to one defines recession and zero defines expansion. A quarterly GDP target is classified as recession-affected when any of its three calendar months is dated as a recession. These choices are reproducible rules for descriptive evaluation; they are not claims that the state was known when the forecast was issued.

State-conditioned comparisons use a Giacomini–White-style loss regression for each competitor versus AR (Giacomini & White, 2006). With a competitor-minus-AR sign convention, the approved regression is

**Equation (2.20): Ex-post state-dependent loss regression**

```math
d_t=\alpha+\beta_{\mathrm{rec}}REC_t
+\beta_{\mathrm{turn}}TURN_t+u_t.
```

Here $REC_t$ equals one for an ex-post recession target date, and $TURN_t$ equals one when the target falls within the declared turning-point neighborhood. $\alpha$ is the average differential in the omitted reference state, while the two slopes indicate shifts associated with recession and turning-neighborhood indicators in this regression. HAC standard errors are used with a horizon-appropriate rule. The tables report individual coefficient estimates and p-values, a joint test involving all coefficients, and a separate test of the state slopes. A significant joint Wald test does not, by itself, imply that $\beta_{\mathrm{rec}}$ or $\beta_{\mathrm{turn}}$ is significant.

A central conceptual limit follows from the time at which states are known. The original conditional predictive ability framework asks whether information available for forecasting helps predict relative future model performance. Here, recession and turning indicators use retrospective target-date classifications. They are not necessarily in the forecaster's information set. Consequently, the regression is best interpreted as an **ex-post state association of loss differentials**, not a feasible real-time rule for choosing a model during a recession that has not yet been announced. Odendahl et al. (2023) provide broader context for state-dependent forecast evaluation, but the thesis does not adopt their full unknown-threshold method.

If a state cell has very few observations, an indicator has no variation, or a regression is numerically unidentified, conditional inference is reported as unavailable. State-specific RMSE and MAE can still be presented with their sample counts. Recession-specific evidence must not be inferred from the sign of a coefficient without its uncertainty, and the sign convention must remain the same as in the overall forecast comparison.

### Peaks, troughs and turning-point neighborhoods

A recession is an interval; a peak or trough is a dated transition. For monthly USREC, the baseline peak is the month immediately preceding a change from expansion to recession, and the baseline trough is the month immediately preceding a change from recession to expansion. A symmetric **±3-month** window around each such date defines the primary monthly turning neighborhood. For GDP, the quarter containing the relevant monthly peak or trough is used with a baseline **±1-quarter** window. If neighborhoods overlap, an observation is counted once in their union.

Neither the economic theory nor the business-cycle literature identifies the number three as an optimal universal width. Chauvet and Piger (2008) emphasize delays in identifying changes of business-cycle phase. The selected neighborhoods provide a transparent way to examine the errors near transitions without pretending that a single exact month fully captures the adjustment period. Chapter 4 therefore repeats the analysis with ±1 and ±6 months and with the turning quarter alone or ±2 quarters for GDP. A state-dependent finding that appears only under one arbitrary window definition receives a weaker interpretation.

Peak/trough analysis complements the recession/expansion comparison. A model might predict relatively well in long expansions but fail at the first sharp downturn. Another could fit the crisis itself but miss the subsequent recovery. Both outcomes matter for the thesis question. The analysis always keeps distinct the observable historical forecast, the realized ex-post business-cycle phase, and the unobserved regime estimated by an econometric model.

The evaluation design therefore defines several questions, not one interchangeable statistic. RMSE and MAE measure errors; AR-relative $R^2$ summarizes descriptive squared-loss differences; HLZ assesses average differences under possible time variation; DM–HLN supplies a conventional secondary comparison; MCS considers multiple admissible candidates; state regressions and turning windows describe where losses concentrate. Each conclusion is reported with its sample, horizon, test role and availability.

## 2.11 Model Admissibility and Failure Rules

Model failure is an empirical outcome, not a reason to conceal a forecast date. Nonlinear estimation can be sensitive to starting values, parameter boundaries and the small number of observations belonging to an unusual regime. An accurate-looking subset of surviving predictions may therefore tell a misleading story if other origins were silently discarded. The revised protocol defines adequacy, fragility and failure before looking at the final rankings, and it retains an audit trail of every relevant warning.

For an MSAR fit, the main credibility checks concern numerical convergence, finite likelihood and parameters, covariance usability, regime occupancy, transition probabilities and the resulting forecast path. Occupancy is calculated from the summed smoothed probabilities for each ordered regime. Occupancy below **5%** of observations or below **20 effective observations** receives a low-occupancy warning. Transition probabilities at or below **0.005** or at or above **0.995** receive boundary warnings. These values are explicit operational thresholds. They are not asymptotic 5% hypothesis tests and must not be interpreted as statistical critical values.

Low occupancy or a boundary transition is ordinarily a fragility flag, not an automatic failed fit. A state may legitimately be rare. The concern is that a rare state offers little information for stable parameter estimation or economic labeling. Failure is reserved for unusable cases such as nonconvergence, non-finite likelihood or parameters, an effectively empty/unidentified state, invalid covariance needed for meaningful inference, violated stability conditions or a non-finite forecast. Where covariance is ill-conditioned or near-singular rather than definitively unusable, the warning and its effect on the interpretation are made explicit.

STAR has corresponding diagnostic flags. A smoothness estimate at its optimizer bound is fragile; a threshold outside the **5th–95th percentile** of the observed transition variable is fragile; and a transition function nearly constant across the sample provides weak evidence of a meaningful smooth change. Singular or unstable nonlinear Hessian and covariance calculations are documented. Non-finite estimation results or non-finite forecasts are failures. A STAR fit with extreme but finite predictions is not automatically erased: its score and economic scale remain visible, and its figure may be placed in a separate failure or extreme-behavior panel to prevent an unreadable plot of the other models.

Classical models also have admissibility rules. An AR must satisfy the required stability restrictions; an ARMA must additionally satisfy invertibility. Residual whiteness and conditional variance are assessed as diagnostic issues rather than silently used to change the model's identity. A method with poor residual diagnostics can be fragile while still issuing a finite forecast. The distinction prevents the nonlinear models from receiving a harsher or more favorable scoring convention without disclosure.

The implementation records model, target, origin, horizon, convergence, parameter warnings, covariance status, forecast availability, exclusion reason and whether a forecast was retained for scoring. A failed prediction cannot be replaced by another model's forecast and still be labelled MSAR or STAR. If an algorithm is retried under an authorized deterministic multi-start or warm-start rule, those attempts belong to the same declared fitting process and remain traceable. A new, unapproved model parameterization is not a permissible silent fallback.

These rules imply different meanings for three empirical findings. Poor forecast accuracy indicates an observed loss disadvantage on valid target dates. Fragility indicates that even a favorable forecast may rest on weak statistical identification or numerical sensitivity. Failure indicates that a forecast or valid inference could not be supplied under the prescribed procedure. A non-rejection by a valid loss test is none of these. Separating the four concepts is necessary to avoid turning missing or unusable evidence into a false result about comparative predictive ability.

A matched-date rule protects against one form of selection bias but cannot remove every issue. Pairwise tests use dates valid for the two compared methods; the MCS uses the intersection of dates valid for all included models. If failures cluster in recessions, the matched subset may omit precisely the periods in which nonlinear models are difficult to use. The study therefore reports how many origins were eligible, how many failed, and which comparisons lost dates. Overall conclusions must be read alongside that coverage, not just the surviving RMSE.

## 2.12 Threat-Based Robustness Plan

A robustness check is useful only when it challenges a named alternative explanation. Testing many arbitrary specifications until a preferred result appears would weaken the design. The approved plan therefore maps each test to a threat raised by economic theory, the literature or the jury. The baseline question remains the $h=1$ four-family forecast comparison; the supplementary analyses assess whether its interpretation is stable under specified changes.

**Table 2.5. Prespecified alternative explanations and corresponding checks**

| Threat to the baseline interpretation | Declared robustness exercise | What the check can establish |
|---|---|---|
| UNRATE or FEDFUNDS representation determines the ranking | Alternative level/first-difference specification | Sensitivity to persistence and transformation choices |
| CPI or another target is undermodelled by the chosen AR lag structure | CPI AR lag choices $p=1,3,6,12$; compare on declared common dates | Whether apparent nonlinear value survives a stronger or altered classical lag representation |
| Two latent states are too restrictive | Six full-sample MSAR(3) fits compared with full-sample MSAR(2) | In-sample regime-count credibility; no K=3 predictive ranking |
| Gains depend on forecast distance | Monthly $h=3,6,12$; GDP $h=2,4$ | Horizon-specific changes under iterated forecasting |
| Rolling history length drives rankings | Monthly $w=180,240,300$; GDP $w=90,120,150$ at $h=1$ | Sensitivity to three declared estimation-window lengths |
| Historical phase labels or transition widths select favorable dates | Recession/expansion and turning neighborhoods: ±1/±3/±6 months, quarterly 0/±1/±2 quarters | Whether state results survive alternative short windows |
| Own-history nonlinearity proxies for other macroeconomic variables | Five-variable monthly VAR, with native quarterly GDP excluded | A limited cross-variable forecasting explanation |
| Changing variance is mistaken for nonlinear mean dynamics | ARCH–LM and triggered ARMA–GARCH(1,1) diagnostic | Evidence about conditional volatility rather than automatic point-forecast superiority |
| October 2025 carry-forward changes outcomes | Directly affected dates plus later lag/rolling-window exposure audit | Conditionality of findings on the LOCF research input |
| Optimizer behavior or failed forecasts favors survivors | Multi-start and warning records, common-date tests, status summaries and non-clipped figures | Numerical credibility and sample-selection limitations |
| Many tested model-horizon cells produce a nominal small p-value | Clearly separated primary tests, full p-value family and multiplicity-sensitive audit | Whether isolated nominal findings justify a broader statement |

*Note:* The threats are assessed one at a time under the approved design; the study does not estimate every possible cross-product of horizons, transformations, state widths and window lengths. Results and their qualifications are examined in Chapter 4, with supporting tables in Appendix C.

### Transformations, benchmark lags and horizons

The alternate level/difference exercise is especially important for UNRATE and FEDFUNDS. A change in the target representation alters its persistence, scale and interpretation. The exercise asks whether a ranking reflects genuine forecast information or the way a unit root was handled. It does not allow an ex-post change in the official baseline transformation. CPI lag sensitivity answers a different criticism: a nonlinear model may appear attractive only because the linear comparator omits a useful seasonal or autoregressive dependence. The approved test compares the specified lag alternatives, not every conceivable AR order, and keeps its common-date and inference rules visible.

Longer forecast horizons test whether nonlinear dynamics matter at distances beyond one observation. The monthly $3$, $6$ and $12$-month and quarterly $2$- and $4$-quarter horizons may produce different rankings. A gain at a longer horizon would still be a horizon-specific result, not a retroactive change to the baseline. In the same way, the variance diagnostic checks a different model property than the main conditional-mean comparison. These results must not be combined into one undifferentiated claim that "nonlinear forecasting wins."

### Why the three-regime test is in-sample only

The baseline Markov-switching model has two states. To test the sensitivity of this restriction, a three-state MSAR is estimated once for each of the six targets on the same full-sample observations used for the corresponding two-state fit. Both specifications use regime-dependent means, common autoregressive coefficients and a common innovation variance. The comparison concerns the statistical credibility of an additional latent state. It does not add a fifth competitor to the out-of-sample forecasting experiment.

An extra state is informative only if it represents an identifiable part of the observed sample. Effective occupancy measures the number and proportion of observations assigned to a state using smoothed probabilities.

**Equation (2.21): Effective regime occupancy**

```math
\begin{aligned}
\widehat p_{t,k} &= \Pr(s_t=k\mid y_{1:T};\widehat\theta),\\
\widehat n_k &= \sum_{t=1}^{T}\widehat p_{t,k},
\qquad \widehat\omega_k=\frac{\widehat n_k}{T}.
\end{aligned}
```

Here $\widehat p_{t,k}$ is the estimated smoothed probability of state $k$ at date $t$, $\widehat n_k$ its effective observation count, and $\widehat\omega_k$ its sample occupancy share. The same regime-occupancy warnings used for the two-state model apply to the three-state comparison. A credible additional state also requires usable covariance estimates, no boundary transition behavior and distinguishable adjacent ordered means. Differences in log-likelihood, AIC and BIC are interpreted jointly with those credibility conditions, not as proof that the additional regime is economically meaningful.

The three-state results are strictly in-sample. No rolling three-state forecasts, forecast-loss tests or additional model rankings are implied. Even a more favorable information criterion cannot establish improved predictive accuracy. If numerical solutions are unstable or no defensible comparison can be drawn, the result remains inconclusive. The empirical consequences of this limited regime-count check are assessed in Section 4.4.

### Window-length and state sensitivity

For the window exercise, monthly lengths are 180, 240 and 300 observations; quarterly GDP lengths are 90, 120 and 150 observations. The two alternatives are 25% below and above the baseline. Every four-family $h=1$ comparison is made on an aligned target-date calendar beginning only when the longest candidate window is available. Discrete model choices remain those selected from the original baseline initial window, and parameters are re-estimated at every origin under the alternative trailing length. This prevents a longer-window model from gaining extra tuning discretion simply because more history is available.

The outputs report RMSE, MAE, AR-relative out-of-sample $R^2$, pairwise tests, MCS membership, sample sizes and fit-status incidence, with the original primary inference procedure unchanged. Conclusions are labelled unchanged, weakened, reversed or unavailable, with strengthened support recorded separately where warranted. These labels describe sensitivity to three chosen lengths rather than invariance to every possible window. They also force numerical fragility to remain visible: a shorter estimation history may leave insufficient evidence for a stable nonlinear regime.

Turning-window sensitivity follows the same principle. A claim concentrated at peaks or troughs is weaker if it disappears when the neighborhood changes by a few months or quarters. Recession classifications remain external and retrospective; no realized future recession label enters the forecasting model. The sensitivity analysis tests the description of where errors occurred, not the feasibility of a real-time state-dependent trading or policy rule.

### Robustness is a test of the claim, not a route to a new baseline

A result survives a robustness exercise only with the correct inferential status, comparison sample and magnitude. Some robustness tables are descriptive; others can supply valid pairwise inference. If a sensitivity test loses validity because one model fails, it is not evidence of equal performance. If a model appears stronger only when particular dates are removed, the selection of those dates must be justified by the declared threat. If an effect occurs only at one horizon or under one transformation, the conclusion is qualified accordingly.

The original hypothesis is not revised in response to these outcomes. Every unfavorable and inconclusive exercise remains part of the evidence. This makes the threat map useful for a doctoral dissertation: it exposes where a seemingly attractive model result is fragile and where a negative finding remains robust, without claiming that a fixed list of checks proves universal validity.

## 2.13 Reproducibility and Numerical Traceability

The empirical analysis is designed to be reproducible from its stated data definitions, sample periods, transformations, estimation rules and forecast-evaluation procedures. The six official time series are taken from the historical FRED/ALFRED vintage of 5 October 2026. Their observation frequencies, sample limits and transformations are reported in Table 2.1. Two missing observations, for CPI and unemployment in October 2025, are treated through the explicitly stated carry-forward convention. Appendix A provides the detailed definitions, treatment of missing observations and supplementary stationarity and nonlinearity diagnostics.

For each target, discrete model choices are determined from the initial estimation window. The same choices are maintained during the baseline rolling experiment, while model parameters are re-estimated at each valid forecast origin. The specification grids, required stability restrictions, numerical convergence conditions and residual tests are defined in Sections 2.3–2.11. Full estimated coefficients, diagnostic statistics and additional model adequacy results are presented in Appendix B. Reporting these choices permits another researcher to distinguish an alternative specification from a replication of the model studied here.

The numerical assessment distinguishes a converged and adequately diagnosed estimate from a fragile estimate or an unusable one. Failed forecasts are not assigned hypothetical values or included in accuracy scores, but their occurrence and its effect on the available comparison sample are reported. The forecast tables identify the horizon, loss function, sample size and matched observations used for each comparison. Appendix C contains the additional robustness results, estimation-status information and relevant cases of numerical instability, including extreme but finite nonlinear forecasts.

These conventions make the empirical conclusions verifiable without implying that every optimizer has located a global maximum. They also preserve the central information-set limitation: all historical pseudo-out-of-sample forecasts use one fixed data vintage, rather than the changing releases that were available in real time. Reproducibility of the chosen experiment does not remove that limitation or establish that the forecast rankings would hold under other historical data vintages or in other economies.

## 2.14 Chapter 2 Concluding Synthesis: From Diagnostic Evidence to a Credible Forecast Experiment

Chapter 1 established the economic possibility of unstable relations among inflation, output, unemployment, interest rates and money. The task of this chapter was to determine how that possibility could be tested without treating complexity as an answer in advance. The resulting empirical design uses six officially measured U.S. forecast targets, an external business-cycle chronology and one declared historical-vintage information set. It keeps quarterly GDP at its true frequency and documents the two exceptional October 2025 input replacements rather than representing them as observed data.

The model comparison follows a controlled sequence. Pre-estimation stationarity and nonlinearity diagnostics define what can be said about persistence, transformations and possible state dependence. AR and ARMA provide serious classical competitors. MSAR and STAR test two distinct forms of nonlinear conditional-mean flexibility under fixed and interpretable specifications. A monthly five-variable VAR asks whether omitted cross-variable information helps explain results from the univariate systems. Conditional-variance diagnostics and the explicit exclusion of a deterministic polynomial baseline keep related but different statistical questions in their proper place.

The experiment separates specification choice from parameter estimation. Discrete model forms are selected on the initial rolling window. Parameters are re-estimated at every eligible historical forecast origin, and each model faces the same target transformation, horizon and date-matching principles. Baseline windows contain 240 monthly or 120 quarterly observations. The primary forecast is one step ahead, while additional horizons, window lengths, transformations and state definitions challenge specific vulnerabilities. This sequence permits meaningful comparisons without using future forecast errors to choose a preferred specification.

No model earns predictive authority from a good likelihood alone. Residual diagnostics, stability, convergence, regime occupancy, transition behavior and forecast availability determine whether a fit is adequate, fragile or failed. Failed predictions remain in the record but do not enter valid loss calculations. Fragility is reported even when a finite forecast is scored. RMSE, MAE and AR-relative out-of-sample $R^2$ describe losses, while the instability-aware HLZ test provides the primary formal average comparison. Conventional DM–HLN, MCS and ex-post state-loss analysis address distinct supporting questions and cannot be substituted for one another.

The design can establish bounded claims about historical predictive performance under a frozen U.S. dataset. It cannot identify the structural causes of macroeconomic outcomes, validate authentic release-by-release forecasting, infer an optimal policy or guarantee international model rankings. Those limits do not weaken the validity of the declared comparison; they define what the evidence is allowed to mean.

Chapter 3 can now examine the empirical evidence in the required order: initial diagnostics, in-sample model adequacy, credibility of estimated states, baseline forecasts and their formal comparisons, and performance around recessions and turning points. Only after those results are visible can Chapter 4 challenge their robustness and assess where, if anywhere, nonlinear complexity has supplied a credible forecasting advantage.


---

## References

Akaike, H. (1974). A new look at the statistical model identification. *IEEE Transactions on Automatic Control, 19*(6), 716–723. https://doi.org/10.1109/TAC.1974.1100705

Amisano, G., & Giacomini, R. (2007). Comparing density forecasts via weighted likelihood ratio tests. *Journal of Business & Economic Statistics, 25*(2), 177–190. https://doi.org/10.1198/073500106000000332

Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics, 31*(3), 307–327. https://doi.org/10.1016/0304-4076(86)90063-1

Box, G. E. P., Jenkins, G. M., Reinsel, G. C., & Ljung, G. M. (2015). *Time series analysis: Forecasting and control* (5th ed.). Wiley.

Carriero, A., Clark, T. E., Marcellino, M., & Mertens, E. (2025). Forecasting with shadow rate VARs. *Quantitative Economics, 16*(3), 795–822. https://doi.org/10.3982/QE2547

Chauvet, M., & Piger, J. (2008). A comparison of the real-time performance of business cycle dating methods. *Journal of Business & Economic Statistics, 26*(1), 42–49. https://doi.org/10.1198/073500107000000296

Cho, J. S., & White, H. (2007). Testing for regime switching. *Econometrica, 75*(6), 1671–1720. https://doi.org/10.1111/j.1468-0262.2007.00809.x

Clark, T. E., & West, K. D. (2007). Approximately normal tests for equal predictive accuracy in nested models. *Journal of Econometrics, 138*(1), 291–311. https://doi.org/10.1016/j.jeconom.2006.05.023

Dickey, D. A., & Fuller, W. A. (1979). Distribution of the estimators for autoregressive time series with a unit root. *Journal of the American Statistical Association, 74*(366a), 427–431. https://doi.org/10.1080/01621459.1979.10482531

Diebold, F. X., & Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business & Economic Statistics, 13*(3), 253–263. https://doi.org/10.1080/07350015.1995.10524599

Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica, 50*(4), 987–1007. https://doi.org/10.2307/1912773

Federal Reserve Bank of St. Louis. (n.d.). *FRED API real-time periods*. https://fred.stlouisfed.org/docs/api/fred/realtime_period.html

Giacomini, R., & White, H. (2006). Tests of conditional predictive ability. *Econometrica, 74*(6), 1545–1578. https://doi.org/10.1111/j.1468-0262.2006.00718.x

Giannone, D., Reichlin, L., & Small, D. (2008). Nowcasting: The real-time informational content of macroeconomic data. *Journal of Monetary Economics, 55*(4), 665–676. https://doi.org/10.1016/j.jmoneco.2008.05.010

Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica, 57*(2), 357–384. https://doi.org/10.2307/1912559

Hansen, P. R., Lunde, A., & Nason, J. M. (2011). The model confidence set. *Econometrica, 79*(2), 453–497. https://doi.org/10.3982/ECTA5771

Harvey, D. I., Leybourne, S. J., & Zu, Y. (2025). Testing for equal average forecast accuracy in possibly unstable environments. *Journal of Business & Economic Statistics, 43*(3), 643–656. https://doi.org/10.1080/07350015.2024.2418835

Harvey, D., Leybourne, S., & Newbold, P. (1997). Testing the equality of prediction mean squared errors. *International Journal of Forecasting, 13*(2), 281–291. https://doi.org/10.1016/S0169-2070(96)00719-4

Hyndman, R. J., & Koehler, A. B. (2006). Another look at measures of forecast accuracy. *International Journal of Forecasting, 22*(4), 679–688. https://doi.org/10.1016/j.ijforecast.2006.03.001

Jarque, C. M., & Bera, A. K. (1987). A test for normality of observations and regression residuals. *International Statistical Review, 55*(2), 163–172. https://doi.org/10.2307/1403192

Kwiatkowski, D., Phillips, P. C. B., Schmidt, P., & Shin, Y. (1992). Testing the null hypothesis of stationarity against the alternative of a unit root: How sure are we that economic time series have a unit root? *Journal of Econometrics, 54*(1–3), 159–178. https://doi.org/10.1016/0304-4076(92)90104-Y

Ljung, G. M., & Box, G. E. P. (1978). On a measure of lack of fit in time series models. *Biometrika, 65*(2), 297–303. https://doi.org/10.1093/biomet/65.2.297

Luukkonen, R., Saikkonen, P., & Teräsvirta, T. (1988). Testing linearity against smooth transition autoregressive models. *Biometrika, 75*(3), 491–499. https://doi.org/10.1093/biomet/75.3.491

National Bureau of Economic Research. (n.d.). *Business cycle dating*. https://www.nber.org/research/business-cycle-dating

Odendahl, F., Rossi, B., & Sekhposyan, T. (2023). Evaluating forecast performance with state dependence. *Journal of Econometrics, 237*(2), Article 105220. https://doi.org/10.1016/j.jeconom.2021.07.015

Orphanides, A. (2001). Monetary policy rules based on real-time data. *American Economic Review, 91*(4), 964–985. https://doi.org/10.1257/aer.91.4.964

Pesaran, M. H., & Timmermann, A. (2007). Selection of estimation window in the presence of breaks. *Journal of Econometrics, 137*(1), 134–161. https://doi.org/10.1016/j.jeconom.2006.03.010

Qu, Z., & Zhuo, F. (2021). Likelihood ratio-based tests for Markov regime switching. *The Review of Economic Studies, 88*(2), 937–968. https://doi.org/10.1093/restud/rdaa035

Rossi, B., & Inoue, A. (2012). Out-of-sample forecast tests robust to the choice of window size. *Journal of Business & Economic Statistics, 30*(3), 432–453. https://doi.org/10.1080/07350015.2012.693850

Schwarz, G. (1978). Estimating the dimension of a model. *The Annals of Statistics, 6*(2), 461–464. https://doi.org/10.1214/aos/1176344136

Sims, C. A. (1980). Macroeconomics and reality. *Econometrica, 48*(1), 1–48. https://doi.org/10.2307/1912017

Teräsvirta, T. (1994). Specification, estimation, and evaluation of smooth transition autoregressive models. *Journal of the American Statistical Association, 89*(425), 208–218. https://doi.org/10.1080/01621459.1994.10476462

Tsay, R. S. (1986). Nonlinearity tests for time series. *Biometrika, 73*(2), 461–466. https://doi.org/10.1093/biomet/73.2.461

West, K. D. (1996). Asymptotic inference about predictive ability. *Econometrica, 64*(5), 1067–1084. https://doi.org/10.2307/2171956

Zivot, E., & Andrews, D. W. K. (1992). Further evidence on the great crash, the oil-price shock, and the unit-root hypothesis. *Journal of Business & Economic Statistics, 10*(3), 251–270. https://doi.org/10.1080/07350015.1992.10509904
