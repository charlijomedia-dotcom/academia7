# Part I: From Macroeconomic Instability to a Testable Forecasting Problem

# Chapter 2: Testing Nonlinear Forecast Value Against Classical Benchmarks: Model Adequacy and Forecast Design

Chapter 1 developed the economic reasons why the relations among inflation, production, unemployment, interest rates and money may change. It also showed why the existence of changing economic conditions does not establish that a nonlinear statistical model will forecast better. This chapter turns that argument into an empirical design. It defines exactly what is forecast, which observations and information are permitted, how classical and nonlinear models compete, when a fitted model is credible, and what evidence can support a claim of forecast improvement.

The purpose is an auditable comparison, not a demonstration that complexity is useful by construction. AR and ARMA models must receive a fair opportunity to represent linear persistence and innovation dynamics. Markov-switching autoregressions (MSAR) and smooth transition autoregressions (STAR) are then asked to improve prediction beyond those competitors. Fit quality, numerical viability, forecast error and statistical significance are assessed separately. The experiment has a limited but useful scope: U.S. historical pseudo-out-of-sample point forecasting from a fixed, reproducible data vintage. No model in this chapter identifies a causal policy intervention, reconstructs every historical real-time data release, or claims an optimal economic policy.

## 2.1 From the Chapter 1 Mechanisms to an Empirical Identification Strategy

The Fisher, Phillips–Phelps, Okun and monetary mechanisms suggest that economic time series can be persistent, asymmetric and state-dependent. They also imply interactions among prices, real activity, unemployment and short-term rates. Yet those mechanisms alone cannot determine which forecasting model will be successful. A theoretical relation may be unstable without being predictable from the series' own lagged observations. Alternatively, a linear statistical model may provide a good forecast even when the underlying economy is structurally complicated. The empirical task is therefore to test a limited predictive proposition rather than infer a complete structural macroeconomic model.

Let $y_{i,t}$ denote one of the six approved forecasting targets, expressed in its selected transformation. A model $m$ issues a forecast at origin $t$ for a target at $t+h$, written $\widehat y^{(m)}_{i,t+h\mid t}$. The relevant object is its predictive error on a target date that was not used for estimating the forecast parameters at that origin.

**Equation (2.1): Forecast error**

\`\`\`math
e^{(m)}_{i,t+h\mid t}=y_{i,t+h}-\widehat y^{(m)}_{i,t+h\mid t}.
\`\`\`

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

\`\`\`math
g_t^{(f)}=a_f\bigl(\ln X_t-\ln X_{t-1}\bigr),
\qquad a_M=1200,\quad a_Q=400.
\`\`\`

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

\`\`\`math
\Delta y_t=\alpha+\rho y_{t-1}
+\sum_{j=1}^{k}\psi_j\Delta y_{t-j}+v_t,
\qquad H_0:\rho=0.
\`\`\`

The lagged differences reduce residual serial correlation, and the distribution of the test statistic under the unit-root null is nonstandard. The thesis uses an intercept, a BIC-selected augmentation order and a maximum of 12 monthly or four quarterly lags. The 5% decision is based on the appropriate Dickey–Fuller reference distribution, not a standard regression $t$ critical value (Dickey & Fuller, 1979).

The Kwiatkowski–Phillips–Schmidt–Shin (KPSS) test reverses the null: the series is stationary around the included deterministic component. Under the approved intercept specification, it tests level stationarity, allowing a stationary stochastic component. A rejection challenges that null. This contrast is useful because an ADF non-rejection and a KPSS non-rejection do not mean the same thing. Nor does an ADF rejection prove that every feature of the sample distribution is stable over time (Kwiatkowski et al., 1992).

For UNRATE and FEDFUNDS in levels, the Zivot–Andrews (ZA) procedure adds a break-sensitive perspective. It tests the unit-root null against a stationary alternative that permits one endogenous break in the intercept and trend. The implementation uses 15% trimming, BIC lag selection and a 5% decision (Zivot & Andrews, 1992). A dated break chosen by this algorithm is a candidate statistical break, not an identified economic-policy intervention or the NBER date of a recession. Equally, non-rejection does not prove the absence of all breaks. Tests that permit only one break can miss more complicated historical changes.

The decision rules form a hierarchy. If the initial-window ADF rejects a unit root and KPSS does not reject stationarity, the level is retained. If ADF does not reject and KPSS rejects, the first difference is selected. When the two tests disagree, ZA serves as the declared tie-breaker: rejection of its unit-root null permits a level specification with break-sensitive robustness; otherwise the baseline is the first difference. The same tests are then presented for the full sample as corroboration, never as permission to alter the historical baseline retrospectively.

### What the released diagnostics actually select

**Table 2.2. Decision-relevant evidence for UNRATE and FEDFUNDS levels**

| Series and tested sample | ADF p-value ($H_0$: unit root) | KPSS p-value ($H_0$: stationary) | ZA p-value ($H_0$: unit root allowing a break in the alternative) | Implication |
|---|---:|---:|---:|---|
| UNRATE: initial 240 observations | 0.0251 | ≥0.1000* | 0.1887 | Clear level stationarity under the ADF/KPSS rule; ZA is reported but not the tie-breaker |
| UNRATE: full sample | 0.0028 | 0.0783 | 0.1691 | Full-sample ADF/KPSS agrees with retaining levels |
| FEDFUNDS: initial 240 observations | 0.9530 | ≤0.0100* | 0.8113 | Clear nonstationarity under the ADF/KPSS rule; first difference selected |
| FEDFUNDS: full sample | 0.1285 | ≤0.0100* | 0.3203 | Full-sample ADF/KPSS supports the original difference decision |

*Source:* [T2.2 stationarity test output](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/diagnostics/T2.2_stationarity.csv) and [locked transformation decisions](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/diagnostics/T2.2_transformation_decisions.csv). *The KPSS implementation reports p-values at the edge of its critical-value table; inequalities indicate a tabulated bound rather than exact tail probabilities.* All decisions use 5%.

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

\`\`\`math
H_0:\ E(y_t\mid\mathcal F_{t-1})\text{ has the selected linear AR form};
\quad
H_1:\ \text{the conditional mean departs from that form.}
\`\`\`

The alternative in an actual test is narrower than all conceivable nonlinear processes. Tsay's auxiliary form and the STAR-specific sequence can respond to different features. A non-rejection in one test and rejection in another is therefore not automatically a contradiction. The output records the statistic, test reference distribution or algorithm, p-value, 5% decision, delay and, for STAR, the chosen transition type. Detailed target-specific evidence is examined in Chapter 3 from [T2.3](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/diagnostics/T2.3_tsay.csv) and [T2.4](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/diagnostics/T2.4_star_linearity.csv). No post hoc filter removes a predeclared nonlinear competitor merely because its specification test did not reject.

Markov switching raises a separate testing problem. Under a one-state null, parameters associated with the second state may be unidentified, and some probabilities lie on boundaries. A conventional likelihood-ratio statistic cannot simply be assigned a standard chi-square distribution. Cho and White (2007) and Qu and Zhuo (2021) address these nonregular features. The approved design does not produce an unverified one-state-versus-two-state p-value. MSAR is retained as a theory-motivated forecasting alternative, while its regimes are assessed by occupancy, transition behavior, estimation quality and prediction. The full-sample three-state check is an additional credibility exercise, not a substitute for a valid regime-number hypothesis test.

The governing interpretation rule is simple. A nonlinearity diagnostic is evidence about a specific null and test power; a fitted nonlinear model is evidence about representation; and a subsequent forecast comparison is evidence about prediction. Only the last, when validly conducted, can establish forecast gains. Even then, no statistical state is assigned a structural economic identity without separate evidence.

