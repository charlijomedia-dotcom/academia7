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

Finally, forecast evaluation is historical and pseudo-out-of-sample. Past observations are divided into rolling estimation windows and subsequent target dates. Parameters are estimated without using the target that will be forecast. However, the stored series all come from the fixed historical-vintage information set described next, not from the sequence of data releases available on every earlier forecasting date. This distinction limits claims about genuine real-time performance (Orphanides, 2001; Federal Reserve Bank of St. Louis, n.d.).

## 2.2 Data, Aggregate Selection, Exact Samples, and Frozen-Vintage Policy

### Six targets, five economic blocks, and one external chronology

The empirical design keeps the six targets motivated in Chapter 1. They cover five related but distinct blocks: inflation, real activity, unemployment, monetary policy and the money stock. Each target has an official U.S. source, an established FRED/ALFRED series identifier and a sufficiently long history for repeated rolling forecasts. The selection rule is conceptual rather than opportunistic: a variable is included because the thesis can explain its economic role, measure it reproducibly and evaluate it under the approved forecasting design. No extra target is added because it happens to produce a favorable result.

**Table 2.1. Approved U.S. forecast targets and exact usable samples**

| Block and target (FRED ID) | Official underlying source | Frequency | Usable raw levels | Modelled target and first modelled date |
|---|---|---|---|---|
| Prices: CPI inflation (CPIAUCSL) | Bureau of Labor Statistics | Monthly | Jan. 1947–Aug. 2026 | $1200\Delta\ln(\mathrm{CPI})$; Feb. 1947 |
| Labour market: unemployment (UNRATE) | Bureau of Labor Statistics | Monthly | Jan. 1948–Aug. 2026 | Rate in percent, level; Jan. 1948 |
| Real activity: industrial production (INDPRO) | Federal Reserve Board | Monthly | Jan. 1947–Aug. 2026 | $1200\Delta\ln(\mathrm{IP})$; Feb. 1947 |
| Monetary policy: effective federal funds rate (FEDFUNDS) | Federal Reserve Board | Monthly | July 1954–Aug. 2026 | First difference in percentage points; Aug. 1954 |
| Money: M2 stock (M2SL) | Federal Reserve Board | Monthly | Jan. 1959–Aug. 2026 | $1200\Delta\ln(\mathrm{M2})$; Feb. 1959 |
| Real activity: real GDP (GDPC1) | Bureau of Economic Analysis | Quarterly | 1947 Q1–2026 Q2 | $400\Delta\ln(\mathrm{GDP})$; 1947 Q2 |

*Source:* Author-processed frozen historical-vintage data dictionary, released in [T2.1](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/data_audit/T2.1_data_dictionary.csv). Dates refer to calendar observations, not to the date on which the underlying statistical agency published them. The official raw data remain unchanged in the source archive. The two October 2025 exceptions affect only the derived research input, as explained below.

CPIAUCSL is a direct measure of U.S. consumer prices. It is not identical to the Federal Reserve's preferred personal consumption expenditures inflation measure, but its longer postwar history supports the intended analysis of changing inflation dynamics. Industrial production begins earlier than the postwar period, but the study deliberately starts its usable series in January 1947 to avoid importing prewar and wartime industrial regimes absent from most other targets. Quarterly real GDP represents comprehensive real production; monthly industrial production provides more frequent but narrower cyclical information. The two are not converted to an artificial common monthly frequency. UNRATE and FEDFUNDS are already rates, so their modelled representations are determined by stationarity diagnostics rather than automatic logarithms. M2SL is explicitly a monetary aggregate, not a claim that the money supply determines inflation proportionally.

The monthly system has a common usable endpoint of August 2026. September 2026 observations were already available for some series in the historical archive, but not for every monthly target. Extending only those series would change the endpoint unevenly. Quarterly real GDP ends in the second quarter of 2026, the last GDP quarter available in the specified vintage. The full historical reach differs across series because the economic variables were not all recorded over identical periods. The common monthly VAR sample begins in January 1959, when M2 becomes available. These choices were fixed by measurement and information rules, not by a search for favorable forecast results.

The U.S. recession indicator (USREC) is a seventh series with a different function. It follows the National Bureau of Economic Research (NBER) business-cycle chronology as distributed by FRED. It is not a forecast target and is not supplied to the univariate forecasting models as a contemporaneous regressor. It is used after outcomes are realized to classify forecast performance in expansions, recessions and neighborhoods of peaks and troughs. Its later-dated historical labels must not be confused with the information available to a forecaster when a recession was beginning (National Bureau of Economic Research, n.d.; Chauvet & Piger, 2008).

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

All inputs originate from the frozen FRED/ALFRED historical information set dated **5 October 2026**. ALFRED permits retrieval of series values as they appeared at a declared vintage date (Federal Reserve Bank of St. Louis, n.d.). The source snapshot preserves the original official observations and missing markers. A single canonical research-input CSV is then generated from that frozen snapshot, with the series identifier, date, frequency, value, original source value, observation status and any imputation metadata recorded on each row. Data files and manifests carry checksums so a later researcher can distinguish a verified rerun from a changed data input.

Freezing the data prevents later official revisions from silently altering an otherwise identical estimation. It does not solve real-time information uncertainty. In a true historical release-by-release evaluation, a forecast formed in an earlier year might have had access to a different version of GDP or inflation, and some indicators would not yet have been published. The present experiment does not reconstruct those earlier ragged-edge datasets. Results are therefore evidence about forecasting procedures conditional on the fixed vintage, not about the exact decisions possible with the original information on each historical origin (Orphanides, 2001).

### The two missing October 2025 observations

The frozen 5 October 2026 source has a missing observation at **1 October 2025** for CPIAUCSL and UNRATE. The approved data procedure retains the missing markers in the unmodified source. In the separate derived input, and only there, the September 2025 raw level is carried forward to the October 2025 raw-level cell for each of the two series. The method is last observation carried forward (LOCF). No other data gaps are filled by this rule; the amendment is not permission to impute unexpected observations.

The consequences differ across targets. CPI inflation is calculated from log differences. Since the carried-forward October CPI level equals September's level, computed October 2025 inflation equals zero by construction. The November 2025 growth transformation then compares November with the carried-forward September-level value, so the missing interval is not distributed across October and November. For UNRATE, the October rate is repeated in levels; the observed outcome is replaced by a modelling assumption, not a measured period of unchanged unemployment. These values may influence not only the directly affected target dates, but also later lag vectors, fitted rolling-window parameters, latent-state probabilities and model comparisons.

The canonical file marks the two entries as imputed and records the predecessor month. The original raw data are never represented as though the observations existed. The finalized imputation audit and exposure sensitivity are preserved in [the published imputation audit](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/data_audit/october_2025_imputation_audit.csv) and [T4.9](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/data_audit/T4.9_locf_sample_comparison.csv). The local imputation does not revise the frozen official snapshot or the approved final study endpoint.

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

*Source:* [T2.2 stationarity test output](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/diagnostics/T2.2_stationarity.csv) and [locked transformation decisions](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/diagnostics/T2.2_transformation_decisions.csv). *The KPSS implementation reports p-values at the edge of its critical-value table; inequalities and the word 'bound' indicate a tabulated limit rather than an exact tail probability.* All decisions use 5%.

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

The alternative in an actual test is narrower than all conceivable nonlinear processes. Tsay's auxiliary form and the STAR-specific sequence can respond to different features. A non-rejection in one test and rejection in another is therefore not automatically a contradiction. The output records the statistic, test reference distribution or algorithm, p-value, 5% decision, delay and, for STAR, the chosen transition type. Detailed target-specific evidence is examined in Chapter 3 from [T2.3](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/diagnostics/T2.3_tsay.csv) and [T2.4](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/diagnostics/T2.4_star_linearity.csv). No post hoc filter removes a predeclared nonlinear competitor merely because its specification test did not reject.

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

ARMA is a broader candidate class, but its selected realization need not have $q>0$. A pure autoregression can be the most defensible choice within the ARMA grid. This is precisely what occurs for several selected targets in the released specification table. The label ARMA therefore identifies the comparison family and its selection rule; it does not guarantee that a nonzero moving-average component has been selected or that it will outperform the primary AR benchmark.

### The actual selected classical specifications

The published selection record gives the following baseline orders. These are initial-window choices, not orders selected from subsequent forecast performance.

**Table 2.3. Fixed baseline linear specifications and inherited nonlinear lag orders**

| Target | AR order | Selected ARMA $(p,q)$ | MSAR lag order | STAR lag order |
|---|---:|---|---:|---:|
| Real GDP growth, quarterly | 1 | (1, 0) | 1 | 1 |
| CPI inflation | 2 | (1, 0) | 2 | 2 |
| Unemployment level | 6 | (3, 4) | 4 | 4 |
| Industrial production growth | 12 | (1, 0) | 4 | 4 |
| Federal funds rate change | 1 | (1, 0) | 1 | 1 |
| M2 growth | 3 | (3, 0) | 3 | 3 |

*Source:* [T2.5 selected specifications](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/diagnostics/T2.5_selected_specs.csv). The nonlinear lag orders inherit the baseline AR order subject to the predeclared caps; they are not newly optimized for the nonlinear models.

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

The final initial-window STAR selections were LSTAR with delays 3 for GDP, 6 for CPI, 1 for unemployment and 5 for M2; and ESTAR with delays 4 for industrial production and 1 for the federal funds rate. They follow the published specification record. The preliminary STAR linearity screen rejected at the chosen delay for CPI, unemployment and the federal funds rate, but not for GDP, industrial production or M2. These outcomes describe a pre-estimation diagnostic under one specific test. Chapter 3 assesses what subsequently happened to fit and forecast quality.

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

*Note:* This table summarizes the declared comparison, not in-sample or out-of-sample rankings. The released specification choices are documented in T2.5. Detailed optimization constraints and complete parameter outputs remain in the evidence appendices.

The earlier hybrid MSSTAR has been removed from the revised methodology. Combining latent-state switching with a smooth transition would introduce two nonlinear mechanisms before either has established independent forecast value. The present four-family comparison can test the more basic question directly. Excluding the hybrid is not an empirical assertion that it never works; it is a proportionality decision to keep the scientific question and numerical evidence manageable.

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

The common descriptive measures are maximized log-likelihood where meaningful, Akaike and Bayesian information criteria, in-sample RMSE, and in-sample MAE. They answer different questions. Likelihood and information criteria describe a fitted probability model and its parameter penalty; RMSE gives relatively more weight to large residuals; MAE describes average absolute deviation. None is an independent out-of-sample forecast. Across different target units or nonmatching samples, raw magnitudes are not directly comparable.

The diagnostic tests include Ljung–Box for residual serial correlation, ARCH–LM for remaining dependence in squared innovations, and Jarque–Bera for distributional normality. The primary Ljung–Box residual-screen horizons are 12 and 24 lags for monthly targets and four and eight lags for quarterly GDP. ARCH–LM is applied at 12 monthly or four quarterly lags. The significance level is 5%. Jarque–Bera is reported because distributional shape matters to likelihood-based inference, but rejection of normality alone is not treated as a fatal failure for a point-forecast model. During rare shocks, a useful mean forecast can coexist with heavy-tailed residuals.

A general residual-autocorrelation null can be written as

**Equation (2.14): Primary residual-whiteness null**

```math
H_0:\operatorname{Cov}(\widehat\varepsilon_t,
\widehat\varepsilon_{t-k})=0
\quad\text{for the tested positive lags }k.
```

Rejection means that the fitted residuals retain evidence of serial dependence over those lags. Non-rejection does not prove that innovations are independent or that the model is structurally correct. The reported test tables must include the null, statistic, reference distribution, p-value, 5% decision and its practical implication. Applying these tests consistently gives a common adequacy language even though the models have different internal state mechanisms.

A second adequacy layer is model-specific. AR and ARMA must satisfy their stability and invertibility requirements. An MSAR fit needs meaningful occupancy and transition behavior; a STAR fit needs an identifiable transition and finite parameters. A model may have residual autocorrelation but a converged, usable forecast, in which case it is classified as fragile. A failed optimization or non-finite prediction is not treated as an ordinary forecast observation.

The classification follows three categories. An *adequate* fit has converged, contains finite parameters, satisfies mandatory stability restrictions, has no fatal structural warning and passes the primary residual-whiteness screen. A *fragile* fit converges but carries warnings such as residual autocorrelation, low regime occupancy, near-boundary probabilities, uncertain covariance or extreme but finite forecast behavior. A *failed* fit is unusable because of nonconvergence, non-finite likelihood or parameters, invalid essential covariance, violated mandatory stability, an effectively empty regime or a non-finite forecast path. The numerical thresholds behind these categories are operational flags explained in the next section, not confidence levels from a statistical theorem.

The separation is essential for scientific interpretation. A fragile forecast can still be evaluated if the value is finite and the common-date rule permits it, but its regimes should not receive strong economic names. A failed forecast remains visible in the estimation audit and is not quietly replaced by an AR forecast under its original model label. The effect of excluded failed origins on the matched comparison is disclosed. This lets the reader distinguish a model that forecasts poorly, a model that has insufficient statistical evidence of an advantage, and a model that cannot reliably supply a forecast at all.

Chapters 3 and 4 use these categories in different ways. Chapter 3 first examines full-sample adequacy and credibility before presenting the baseline horse race. Chapter 4 asks whether warning rates, alternative specifications and numerical fragility undermine any forecast advantage. Neither chapter treats a lower BIC as a sufficient forecasting result. The methodological distinction between representation and prediction remains binding.

