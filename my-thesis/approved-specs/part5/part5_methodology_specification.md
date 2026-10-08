# Part 5: Methodology specification

**Project:** *Forecasting Macroeconomic Aggregates under Economic Instability: Theory, Nonlinearity, and Policy Implications*  
**Date:** 5 October 2026  
**Status:** APPROVED AND FROZEN
**Inputs:** Parts 1–4, Part 2 jury registry, Prof. Verne requirements recorded in Part 4, and external econometric literature used only to choose appropriate procedures  
**Purpose:** Freeze the empirical methodology that Claude Code must implement in Parts 6–8.

## 1. Governing methodological principle

The revised empirical design must be stronger without becoming larger for its own sake.

The sequence is:

**economic question → frozen data → transformation/stationarity decisions → pre-estimation nonlinearity evidence → classical benchmarks → parsimonious nonlinear alternatives → in-sample adequacy → pseudo-out-of-sample forecasts → state-conditioned evaluation → threat-based robustness → bounded economic interpretation**

The methodology is deliberately designed so that:

- model complexity must earn its place;
- fit is checked before forecast claims;
- good fit is not treated as proof of forecast superiority;
- nonlinearity is diagnosed before it is interpreted economically;
- failed nonlinear models remain visible;
- the univariate core is supplemented by a focused multivariate test;
- no method is added merely because it is fashionable or because it may improve the desired result.

This follows Part 1, especially P1-03, P1-07, P1-09, P1-10, and P1-17.

## 1.1 Alignment with the approved Part 4 structure

Part 5 is not a separate econometric exercise. It is the empirical implementation of the Part 4 argument.

| Part 4 block | Methodological role in Part 5 | Main empirical output |
|---|---|---|
| General Introduction | Define one forecasting problem under instability and the burden of proof | Research-question and claim map |
| Part I, Chapter 1 | Economic theory identifies the macroeconomic concepts that must be represented: prices, real activity, labour-market slack, monetary policy, monetary conditions, and the business cycle | Series-selection rationale |
| Part I, Chapter 2 | Convert those concepts into observable time series, transformations, diagnostics, classical benchmarks, nonlinear alternatives, and a pseudo-OOS experiment | Data audit, transformation decisions, model specification |
| Part II, Chapter 3 | Require credible in-sample representation before comparing real forecasts, then evaluate expansions, recessions, peaks, and troughs | Adequacy tables, main OOS tables, state-conditioned evidence |
| Part II, Chapter 4 | Challenge the baseline conclusions with transformations, lag choices, regime count, horizons, cross-variable information, and model fragility | Robustness tables, VAR block, failure registry |
| General Conclusion | Use only verified Part 8 outputs to state what survives and what can or cannot be generalized | Claim-evidence matrix |

This mapping is mandatory. Claude Code must not produce empirical analyses that have no identifiable home in Part 4 unless the user explicitly approves a methodology revision.

---

# 2. Empirical targets, data selection, retrieval, and frozen reproducibility

## 2.1 Why the United States is the empirical case

The country choice is part of the research design and must be defended before individual series are selected.

The United States is chosen because it jointly satisfies five requirements that are unusually important for this thesis:

1. **Economic and policy relevance.** The thesis studies inflation, output, unemployment, money, and interest-rate dynamics in a major monetary economy where Federal Reserve policy is central to the interpretation developed in Part 4.
2. **Long postwar history.** Official U.S. series provide several decades of monthly and quarterly observations, covering repeated recessions, expansions, inflation episodes, disinflation, low-rate periods, tightening cycles, financial stress, and the pandemic period. This is especially valuable for MSAR, STAR, rolling estimation, and turning-point evaluation.
3. **Measurement breadth and consistency.** The required concepts can be represented with official series from BEA, BLS, and the Federal Reserve without constructing synthetic proxies.
4. **Machine-retrievable open data.** FRED/ALFRED exposes the required series through stable identifiers and Python-accessible web services, satisfying the thesis's requirement that the database be reproducible without manual CSV construction.
5. **Historical-vintage reproducibility.** ALFRED allows the thesis to reconstruct the 2026-10-05 information set even after future revisions to U.S. macroeconomic history.

The United States is therefore selected because it is a particularly strong empirical environment for the thesis question, **not because the methodology is assumed to be U.S.-specific by construction**.

The external-validity rule remains strict:

- empirical rankings are conclusions about the U.S. sample studied;
- the comparative research design may be transferable;
- superiority of a specific model family may not be generalized internationally without separate country evidence.

This country-selection rationale belongs in the General Introduction and Chapter 1 in Part 4, while the exact data implementation belongs in Chapter 2.

## 2.1 Data-selection rule

A series is retained in the core thesis only if it satisfies all of the following:

1. **Economic necessity:** it represents a macroeconomic concept used explicitly in Part 4's Fisher, Phillips/Phelps, Okun, monetary-policy, monetary-aggregate, or business-cycle discussion.
2. **Forecasting relevance:** it is a meaningful target for macroeconomic monitoring or policy analysis rather than a decorative control.
3. **Official measurement:** the underlying source is an official U.S. statistical authority or the Federal Reserve.
4. **Machine accessibility:** observations can be retrieved automatically from FRED/ALFRED using a stable series ID and Python code. No manual spreadsheet construction is permitted.
5. **Sufficient history:** the series has enough postwar observations for the approved rolling forecast design and for recurrent recession/expansion episodes.
6. **Frequency compatibility:** the series is monthly or quarterly and can be used without artificial interpolation.
7. **Parsimony:** a second series measuring the same concept is not added to the core unless it answers a distinct methodological question.

This rule makes the data set a consequence of the thesis argument rather than an arbitrary collection of variables.

## 2.2 Baseline frozen snapshot and online retrieval

The baseline thesis dataset must be created once and then frozen.

**Thesis vintage date:** 2026-10-05.  
**Primary provider:** Federal Reserve Economic Data / ALFRED, Federal Reserve Bank of St. Louis.  
**Default pipeline behavior after initialization:** read only from `data/frozen/`.  
**Refresh behavior:** explicit `--refresh-data` only, writing to `data/refreshed/YYYY-MM-DD/`.  
**Never overwrite the baseline snapshot.**

### Programmatic retrieval rule

No thesis series may require manual CSV construction.

The initialization code must retrieve each raw series from FRED/ALFRED by its series ID. The preferred reproducibility path is the official FRED web service with:

- the series ID;
- `vintage_dates=2026-10-05` or an equivalent real-time setting;
- raw units, with no FRED-side transformation;
- a free FRED API key read from the environment variable `FRED_API_KEY`.

The FRED API explicitly supports historical vintage dates, allowing data to be requested as they existed on a specified historical date. This provides an independent reconstruction route if the local frozen files are ever lost.

A simple no-manual-download alternative such as `pandas_datareader.get_data_fred()` may be used for exploratory or refreshed current data. It may **not** silently replace the thesis vintage because current FRED history can be revised.

### Frozen-file rule

At the first approved initialization, save the exact returned raw observations under:

`data/frozen/fred_vintage_2026-10-05/`

For every raw series, save:

- raw CSV or Parquet file;
- series ID;
- exact API request parameters;
- source institution;
- title;
- frequency;
- units;
- seasonal-adjustment status;
- vintage date;
- retrieval timestamp;
- first and last raw observation;
- row count;
- SHA-256 file hash.

Also save a master manifest containing the hash of every frozen file.

All transformations must be calculated locally from the frozen raw levels. Do not rely on a remotely transformed series for the baseline. This guarantees that rerunning the same code on the same frozen files reproduces the same transformed observations and model inputs.

The normal `python code/run_all.py` command must not contact the internet. It must first verify the frozen-file hashes and then reproduce the thesis outputs from those local files.

## 2.3 Core target series and why these variables are selected

| Target | FRED ID | Frequency | Raw form | Baseline target transformation | Why it is in this thesis |
|---|---|---:|---|---|---|
| Real GDP growth | GDPC1 | Quarterly | Real GDP, SAAR | 400 × [ln(GDPC1_t) - ln(GDPC1_{t-1})] | The comprehensive real-output aggregate. It gives the thesis a direct measure of economic growth and links to Okun-style output-labour dynamics. |
| CPI inflation | CPIAUCSL | Monthly | CPI-U, seasonally adjusted | 1200 × [ln(CPI_t) - ln(CPI_{t-1})] | Direct consumer-price inflation measure with a long postwar history. It is central to Fisher/Phillips reasoning and price-stability policy. |
| Unemployment | UNRATE | Monthly | Percent, seasonally adjusted | Level or first difference by predeclared stationarity rule in §3.4 | Direct labour-market slack measure. It is required by Phillips/Phelps and Okun mechanisms and by recession-policy interpretation. |
| Industrial production growth | INDPRO | Monthly | Index, seasonally adjusted | 1200 × [ln(INDPRO_t) - ln(INDPRO_{t-1})] | Monthly real-activity measure. It complements quarterly GDP and gives the monthly forecast system a cyclical activity target without interpolating GDP. |
| Federal funds rate | FEDFUNDS | Monthly | Percent, monthly average | Level or first difference by predeclared stationarity rule in §3.4 | Long monthly U.S. monetary-policy rate. It links Fisherian interest-rate reasoning to the Federal Reserve policy focus of Part 4. |
| M2 growth | M2SL | Monthly | Billions of dollars, seasonally adjusted | 1200 × [ln(M2_t) - ln(M2_{t-1})] | Monetary aggregate required to give empirical content to the monetarist/money-supply discussion retained at Prof. Verne's request. |
| Business-cycle state | USREC | Monthly | 0/1 recession indicator | No transformation; evaluation only | External NBER-based chronology used to classify realized forecast errors in expansions, recessions, peaks, and troughs. It is not a forecast target and not a contemporaneous regressor. |

### Economic coverage

The six forecast targets deliberately cover five distinct macroeconomic blocks:

- **prices:** CPI;
- **real activity:** real GDP and industrial production;
- **labour market:** unemployment;
- **monetary policy:** federal funds rate;
- **monetary conditions:** M2.

GDP and INDPRO are not treated as duplicate targets. GDP is the comprehensive quarterly output measure; INDPRO provides a monthly cyclical real-activity measure. This frequency distinction is essential because the thesis refuses to create artificial monthly GDP observations.

### Why no additional core targets are added

The baseline does **not** add more variables merely to make the thesis look broader.

- **PCE price index (PCEPI):** economically important and the Federal Reserve's preferred inflation measure, but it begins in 1959 and largely duplicates the inflation concept already represented by CPI. CPI is retained because it provides a longer postwar history beginning in 1947 and preserves one inflation target rather than overweighting inflation in the cross-series comparison.
- **Public debt and fiscal deficit:** important to the policy motivation in Part 4, but they are not necessary to identify the thesis's model-form forecasting question and would introduce additional frequency, accounting, and persistence issues.
- **Exchange rates and commodity/oil prices:** economically relevant sources of shocks, but making them additional core targets would broaden the thesis beyond the selected U.S. aggregate-policy system. The previous Brent exercise is therefore not a core block.
- **Core inflation, alternative unemployment measures, additional interest rates, and financial-market variables:** potentially useful extensions, but they represent robustness to measurement choice rather than a new element of the central research question.

The methodological principle is therefore **conceptual coverage with minimum redundancy**.

### Transformation rationale

For GDPC1, CPIAUCSL, INDPRO, and M2SL, the raw level is positive and strongly trending. The log-difference transformation:

`g_t = k × [ln(X_t) - ln(X_{t-1})]`

has three roles:

1. it converts multiplicative level changes into approximately percentage growth rates;
2. it reduces deterministic/stochastic trend behavior that can create spurious autoregressive persistence;
3. it produces economically interpretable growth/inflation targets suitable for AR, ARMA, MSAR, and STAR comparison.

Use `k=400` for quarterly GDP and `k=1200` for monthly CPI, INDPRO, and M2 so one-period continuously compounded changes are expressed at annualized percentage rates.

UNRATE and FEDFUNDS are already rates. Logging them is neither necessary nor always economically meaningful, especially around low values. Their baseline level/difference representation is therefore decided by the stationarity protocol rather than imposed mechanically.

The thesis must state that transformation is chosen to create a defensible dynamic target, not to improve a model's forecast ranking after results are observed.

## 2.4 Baseline sample rules and date justification

The sample dates are chosen by an explicit rule, not by searching for a favorable result.

### Start-date rule

The univariate analysis uses the earliest available **post-World War II official observation** for each retained target, with one deliberate harmonization:

- GDPC1: 1947Q1 onward;
- CPIAUCSL: 1947M1 onward;
- UNRATE: 1948M1 onward;
- FEDFUNDS: 1954M7 onward;
- M2SL: 1959M1 onward;
- INDPRO: truncated to 1947M1 even though the official series begins earlier.

The 1947 truncation of INDPRO is intentional. The thesis studies modern postwar U.S. macroeconomic forecasting and policy regimes. Including Great Depression and World War II industrial-production observations would introduce institutional and wartime regimes that are not observed for the other core targets and would make the cross-series historical scope less comparable.

Using the earliest defensible postwar observation maximizes the number of business-cycle episodes and observations available for nonlinear estimation without choosing the start date after looking at forecast performance.

### End-date rule

The thesis vintage is fixed at **2026-10-05**.

The monthly core endpoint is **2026M8** because August 2026 is the latest month available for **all** five monthly core targets in the 2026-10-05 information set. Some series already contain September, but using September selectively would create unequal end dates across the monthly comparison.

The quarterly GDP endpoint is **2026Q2**, the latest released quarterly real-GDP observation available by the thesis vintage date.

Thus the endpoint is determined by the information set, not by an economic event or a favorable forecast result.

### VAR common-sample rule

The monthly VAR begins in **1959M1**, because M2 is the latest-starting variable in the five-variable monthly system. The VAR ends in 2026M8, the common monthly endpoint.

No missing earlier observations are backfilled and quarterly GDP is not interpolated.

### Reproducibility check

The frozen-data initialization must verify these expected ranges against the 2026-10-05 vintage. If the historical-vintage API returns a different start or terminal observation, Claude must stop, save the discrepancy, and request approval rather than silently alter the sample.

## 2.5 Business-cycle chronology

Use FRED `USREC` only as an **ex post evaluation chronology**, not as a contemporaneous forecasting regressor.

For monthly data:

- recession = USREC = 1 at the forecast target date;
- expansion = USREC = 0;
- peak = month immediately preceding a 0→1 transition;
- trough = month immediately preceding a 1→0 transition;
- **baseline turning-point window = ±3 months** around each peak or trough.

For quarterly GDP:

- a quarter is recession-affected if at least one month in the quarter has USREC = 1;
- **baseline quarterly peak/trough window = ±1 quarter** around the quarter containing the monthly peak/trough date.

### Why ±3 months is the baseline monthly window

The literature does **not** establish a universal theorem saying that a business-cycle turning-point neighborhood must be exactly ±3 months. The thesis therefore treats ±3 months as a **predeclared operational choice**, not as an estimated or theoretically privileged constant.

The choice is nevertheless informed by high-level business-cycle research:

- **Chauvet and Piger (2008, Journal of Business & Economic Statistics)** use a conservative real-time dating rule in which recession probabilities must remain on the new side of a threshold for **three consecutive months** before a new phase is confirmed.
- **Li, Sheng, and Yang (2021, International Journal of Forecasting)** describe turning-point identifications occurring **within three months of the NBER date** as reasonably accurate, and report that CFNAI recession signals under benchmark thresholds occurred within three months of NBER dates.
- **Stock and Watson (2014, Journal of Econometrics)** treat an aggregate turning-point date as an estimated object with a sampling distribution and standard error, supporting the general principle that a turning point should not be interpreted as a perfectly measured single month.
- **Hamilton (2011, International Journal of Forecasting)** emphasizes the accuracy-versus-timeliness problem in real-time business-cycle dating and the difficulty created by data revisions and changing economic relationships.
- **Berge and Jordà (2011, American Economic Journal: Macroeconomics)** formally evaluate recession/expansion classification and the horizons at which indicators predict future turning points.

Taken together, these papers support treating the immediate neighborhood of an NBER peak or trough as economically special, and they provide precedent for a short three-month scale. They do **not** establish the exact symmetric ±3-month window used here.

### Mandatory turning-window sensitivity

To prevent the result from depending on the arbitrary number 3, Chapter 4 must repeat the turning-point analysis using:

- **monthly:** ±1 month, **±3 months baseline**, and ±6 months;
- **quarterly GDP:** turning quarter only, **±1 quarter baseline**, and ±2 quarters.

The sensitivity exercise uses the union of all months/quarters falling within the relevant windows. An observation is counted once even if peak and trough windows overlap. The baseline claim is considered robust only if its substantive interpretation does not depend solely on the ±3-month / ±1-quarter definition.

This chronology must never leak into model estimation unless a future approved methodology explicitly adds it as a lagged predictor.

---

# 3. Transformation and stationarity protocol

## 3.1 Why stationarity is tested before model fitting

The jury specifically questioned unemployment and the policy rate in levels. The revised thesis will not justify a level specification by appearance or economic convenience alone.

## 3.2 Tests used

For every final target series, report the required tests on the **full frozen sample**.

For UNRATE and FEDFUNDS, the same ADF/KPSS/Zivot-Andrews protocol is also run on the **initial estimation window**. The initial-window evidence determines the baseline forecasting transformation. The full-sample evidence is used to assess whether that transformation remains defensible over the complete thesis sample. This avoids choosing the pseudo-out-of-sample transformation using future observations.

For every final target series, report:

### Augmented Dickey-Fuller (ADF)

- **H0:** unit root.
- **H1:** stationarity around the included deterministic terms.
- deterministic term: intercept for transformed targets;
- lag length: BIC-selected, capped at 12 monthly lags or 4 quarterly lags;
- significance level: 5%.

### KPSS

- **H0:** level stationarity.
- **H1:** unit root / nonstationarity.
- deterministic term: intercept;
- bandwidth: automatic data-dependent rule implemented by the chosen library and recorded in output;
- significance level: 5%.

### Zivot-Andrews for disputed level series

Applied to **UNRATE and FEDFUNDS in levels**.

- **H0:** unit root without an endogenous break.
- **H1:** trend/level stationarity allowing one endogenous structural break;
- specification: break in intercept and trend;
- trim: 15%;
- lag selection: BIC;
- significance level: 5%.

The break date must be reported and plotted on the level series.

## 3.3 Additional transformation verification

For GDPC1, CPIAUCSL, INDPRO, and M2SL:

- report ADF and KPSS on the log level;
- report ADF and KPSS again after the specified log-difference transformation.

This demonstrates rather than assumes why the growth/inflation transformation is used.

## 3.4 Predeclared decision rule for unemployment and policy rate

Apply this rule first to the **initial estimation window** for each disputed level series:

1. **Clear level stationarity:** ADF rejects unit root and KPSS does not reject stationarity → keep the level as baseline.
2. **Clear nonstationarity:** ADF does not reject and KPSS rejects → use first difference as baseline.
3. **ADF/KPSS disagreement:** use Zivot-Andrews as tie-breaker:
   - ZA rejects unit root with break → retain level as baseline and carry a break-sensitive robustness check;
   - ZA does not reject → use first difference as baseline.

Then apply the same tests to the full frozen sample as required by the jury.

- If full-sample evidence agrees, the baseline transformation is confirmed.
- If full-sample evidence disagrees, **do not retrospectively change the baseline pseudo-OOS transformation**. Flag the disagreement and make the alternative transformation a mandatory Chapter 4 robustness check.

If differenced:

`Δx_t = x_t - x_{t-1}`

is the modeled target. Level forecasts are reconstructed from the last observed level for policy-facing figures, while formal predictive tests are conducted on the stationary modeled target.

The non-baseline transformation is retained as an explicit Chapter 4 robustness check.

This rule is fixed before results are seen.

---

# 4. Pre-estimation evidence for nonlinearity

Nonlinearity is treated as an empirical hypothesis, not as a label attached after a nonlinear model fits.

## 4.1 General nonlinearity test

For each target, first fit the selected linear AR benchmark on the initial estimation window and apply the **Tsay (1986) nonlinearity test** to the stationary target/residual structure.

Report:

- test statistic;
- p-value;
- 5% decision;
- interpretation.

This supplies a general pre-estimation test of departure from linear autoregressive dynamics.

## 4.2 Smooth-transition linearity and STAR specification

After the general test, apply the Luukkonen-Saikkonen-Teräsvirta / Teräsvirta linearity-testing and specification procedure against STAR alternatives.

Monthly candidate delays: `d ∈ {1, 2, 3, 4, 5, 6}`.  
Quarterly candidate delays: `d ∈ {1, 2, 3, 4}`.

Follow the standard Teräsvirta specification sequence:

- report the delay-specific linearity-test p-values;
- select the delay that gives the strongest evidence against linearity, subject to a clear and reproducible rule;
- use the standard nested-test sequence to choose LSTAR versus ESTAR.

No ad hoc multiple-testing correction is imposed on this established specification sequence.

A failure to reject linearity does **not** remove STAR from the predeclared forecast comparison. It does prevent the thesis from treating a later STAR transition as independently validated structural evidence.

## 4.3 Markov-switching testing caveat

A conventional one-regime versus two-regime likelihood-ratio test is **not** used with an ordinary chi-square reference distribution.

The regime-switching literature shows that this testing problem is nonstandard because transition probabilities and other nuisance parameters are not identified under the one-regime null and parameters can lie on boundaries.

The revised thesis therefore does **not** add a simplistic bootstrap LR test merely to create a p-value. MSAR is a predeclared forecasting alternative motivated by the business-cycle/regime-switching literature. Its empirical credibility is judged through:

- convergence;
- regime occupancy;
- transition behavior;
- in-sample adequacy;
- out-of-sample forecast performance;
- K=3 robustness.

The thesis must state explicitly that absence of a formal one-versus-two-regime test limits structural regime claims.

## 4.4 Interpretation rule

The pre-estimation nonlinearity tests affect **interpretation**, not whether a predeclared nonlinear model is allowed into the forecast horse race.

This avoids post-selection bias while still answering the jury's request to test nonlinearity before interpreting nonlinear models.

---

# 5. Forecasting model hierarchy

The final model set is intentionally smaller than in the submitted thesis.

## 5.1 Classical benchmark 1: AR(p)

`y_t = c + Σ_{j=1}^p φ_j y_{t-j} + ε_t`

This remains the primary benchmark because it is transparent, parsimonious, and directly tests whether nonlinear structure adds information beyond own-history linear dynamics.

### Lag selection

Monthly: `p ∈ {1, ..., 12}`.  
Quarterly: `p ∈ {1, ..., 4}`.

Primary criterion: BIC.

Selection rule:

1. rank candidates by BIC;
2. among candidates whose residuals do not reject the primary Ljung-Box adequacy check at 5%, choose the lowest-BIC candidate;
3. if every candidate fails the Ljung-Box check, retain the BIC minimum but classify the linear benchmark as diagnostically weak.

The selected order is fixed from the initial estimation window and is not re-searched at every forecast origin.

## 5.2 Classical benchmark 2: ARMA(p,q)

This strengthens the classical comparison requested by Prof. Verne.

Monthly search grid:

- `p,q ∈ {0, ..., 4}`;
- exclude ARMA(0,0);
- require stationarity and invertibility.

Quarterly search grid:

- `p,q ∈ {0, ..., 2}`;
- exclude ARMA(0,0).

Selection uses BIC plus the same residual-whiteness rule.

The ARMA specification is fixed after the initial estimation window.

## 5.3 ARCH/GARCH treatment

ARCH/GARCH models are not used as primary point-forecast competitors because their main role is conditional-variance dynamics rather than a distinct conditional-mean forecast mechanism.

However, Prof. Verne explicitly raised ARCH/GARCH as a classical forecasting family, so they are addressed empirically:

- apply ARCH-LM to residuals of the selected classical mean model;
- when ARCH-LM rejects homoskedasticity at 5%, estimate an ARMA-GARCH(1,1) diagnostic specification;
- report variance persistence and standardized-residual diagnostics;
- do not treat a better variance model as evidence of better mean forecasting unless its point forecast is actually different and evaluated under the same OOS rules.

This makes the inclusion scientifically relevant rather than ceremonial.

## 5.4 Polynomial models

Deterministic polynomial trend models are **not** included in the main horse race because the principal targets are stationary growth/rate transformations and the thesis question concerns dynamic forecast instability, not deterministic trend extrapolation.

This exclusion must be stated explicitly in Chapter 2 because Prof. Verne mentioned polynomial models as an example.

If a final target retains a statistically significant deterministic trend after the stationarity protocol, Part 5 must be revisited before coding.

## 5.5 Nonlinear model 1: parsimonious two-regime MSAR

Baseline Hamilton-style equation:

`y_t = μ_{s_t} + Σ_{j=1}^p φ_j (y_{t-j} - μ_{s_{t-j}}) + ε_t`, with `ε_t ~ N(0, σ²)`.

where `s_t ∈ {1,2}` follows a first-order Markov chain.

The baseline allows:

- regime-specific conditional means;
- common AR coefficients across regimes;
- a common innovation variance.

This is deliberately close to Hamilton's canonical business-cycle specification. The purpose is to test whether discrete shifts in the conditional mean add useful forecasting information without first allowing every dynamic coefficient and variance to switch.

The AR lag order is inherited from the selected AR benchmark, capped at:

- 4 lags monthly;
- 4 lags quarterly.

The thesis must report:

- transition matrix;
- smoothed regime probabilities;
- regime occupancy;
- expected duration;
- regime-specific means/variances where interpretable;
- convergence status.

## 5.6 Nonlinear model 2: STAR

Use a standard smooth-transition autoregression:

`y_t = φ'x_t + G(z_{t-d}; γ, c) θ'x_t + ε_t`

with `G` selected as LSTAR or ESTAR using the Teräsvirta specification sequence.

The AR lag order is inherited from the selected AR benchmark, capped at:

- 4 lags monthly;
- 2 lags quarterly.

Transition-variable delay follows the pre-estimation procedure in §4.1.

Report:

- transition type;
- delay;
- threshold (c);
- smoothness `γ`;
- transition-function range and dispersion;
- convergence;
- regime-side coefficient interpretation.

## 5.7 MSSTAR is removed from the baseline methodology

The submitted hybrid MSSTAR is **not** retained in the revised core design.

Reason:

- it combines two nonlinear mechanisms before either mechanism has earned empirical credibility;
- it materially increases parameter and optimization burden;
- the jury's central concern is credibility, not maximum complexity;
- Part 1 argues that methods should be proportional to the scientific problem;
- the thesis can test discrete versus smooth state dependence more transparently with MSAR and STAR separately.

MSSTAR may not be reintroduced by Claude without explicit user approval.

---

# 6. Focused multivariate response

The revised thesis adds a genuine multivariate forecasting block rather than treating the old oil-X single equation as a multivariate answer.

## 6.1 Monthly VAR

Estimate a monthly VAR using the common transformed monthly system:

[
(pi_t,; ip_t,; u_t,; i_t,; m2_t)'
]

where the unemployment and policy-rate entries use the baseline transformation determined by §3.4.

Common sample begins when all five series are available, therefore from the M2 start in 1959 onward.

Lag order:

- `p ∈ {1,2,3}`;
- BIC selection;
- require VAR stability.

Purpose:

- test whether cross-variable information changes the forecast ranking that appears in the univariate analysis;
- assess whether own-history nonlinearity may be proxying for omitted macroeconomic interactions.

The VAR is a **robustness / alternative-explanation model**, not a new central model family.

## 6.2 GDP and mixed frequency

Quarterly GDP is not forced into the monthly VAR by interpolation.

A full mixed-frequency VAR/MIDAS/nowcasting system would answer a related but larger research question involving publication timing and mixed-frequency information.

Therefore:

- no interpolation of quarterly GDP to monthly frequency;
- no full nowcasting model in the core thesis;
- nowcasting/mixed-frequency forecasting is explicitly delimited in Chapter 1 and Chapter 4 as outside the principal empirical design.

This is the substantive response to R1-20.

## 6.3 Old oil application

The old Brent-X inflation application is removed from the core empirical methodology because it remained a single-equation extension and did not resolve the jury's multivariate criticism.

It may be restored only as a clearly secondary policy application after the core Part 8 results are complete and only with explicit user approval.

---

# 7. In-sample model adequacy before forecast interpretation

Prof. Verne's fit-before-forecast point is implemented as a formal adequacy stage.

## 7.1 Metrics and tests

For each fitted model report:

- log-likelihood where meaningful;
- AIC;
- BIC;
- in-sample RMSE;
- in-sample MAE;
- Ljung-Box residual autocorrelation test;
- ARCH-LM;
- Jarque-Bera;
- model-specific structural diagnostics.

MAPE is removed because growth and inflation targets can be near zero or negative, making percentage errors unstable and difficult to interpret.

## 7.2 Standardized hypothesis-test presentation

Every test table must include:

- test name;
- null hypothesis;
- statistic;
- reference distribution or bootstrap method;
- p-value;
- decision at 5%;
- implication for model adequacy.

## 7.3 Primary residual-diagnostic lags

Monthly:

- Ljung-Box at 12 and 24 lags;
- ARCH-LM at 12 lags.

Quarterly:

- Ljung-Box at 4 and 8 lags;
- ARCH-LM at 4 lags.

## 7.4 Role of normality

Jarque-Bera is reported because the reviewer requested clear diagnostics, but non-normal residuals alone do not disqualify a point-forecast model.

## 7.5 Adequacy categories

Each estimation is classified:

### Adequate
- optimizer converged;
- parameters finite;
- required stationarity/invertibility conditions satisfied;
- no fatal structural warning;
- primary Ljung-Box check does not reject at 5%.

### Fragile
Converged but one or more warnings occur, such as:

- residual autocorrelation;
- near-boundary nonlinear parameter;
- near-empty regime;
- near-absorbing or near-alternating transition probability;
- unusually large parameter uncertainty;
- extreme but finite forecast behavior.

### Failed
Any of:

- non-convergence;
- non-finite parameter or likelihood;
- singular/invalid covariance preventing meaningful inference;
- required AR/ARMA stability condition violated;
- effectively empty Markov regime;
- non-finite forecast path.

Fragile models remain visible and may still have forecast metrics, but they cannot support strong economic regime interpretation.

Failed models are reported as failures rather than silently replaced by a simpler fallback.

---

# 8. Nonlinear-model credibility rules

## 8.1 Markov-switching rules

For each regime:

- report effective smoothed-probability occupancy;
- flag occupancy below 5% of observations or below 20 effective observations as **low occupancy**;
- flag transition probabilities ≤ 0.005 or ≥ 0.995 as **boundary behavior**;
- report expected durations;
- resolve label switching by ordering regimes by the estimated regime mean using one fixed documented rule.

The 5%, 20-observation, and 0.005/0.995 values are transparent operational warning thresholds, not theoretical critical values. Low occupancy or boundary persistence makes a model **fragile**, not automatically failed. Failure is reserved for computationally or statistically unusable estimation such as non-convergence, non-finite likelihood/parameters, or an effectively unidentified regime.

The policy-rate case receives a dedicated diagnostic table separating:

- transformation/stationarity status;
- convergence;
- transition probabilities;
- regime occupancy;
- coefficient magnitude;
- residual adequacy;
- forecast behavior.

## 8.2 STAR rules

Flag as fragile if:

- `γ` lands on its optimization bound;
- (c) lies outside the 5th–95th percentile of the transition variable;
- the fitted transition function is nearly constant over the sample;
- the nonlinear Hessian/covariance is singular or unstable.

A non-finite optimization or forecast is failure.

## 8.3 No silent fallback

The submitted thesis could change the MSAR parameterization after a fit failure.

That behavior is removed.

If a specification fails, record the failure. Do not silently switch to a different model and continue under the same label.

---

# 9. Pseudo-out-of-sample forecasting design

## 9.1 Estimation windows

Baseline fixed rolling windows:

- monthly targets: 240 observations;
- quarterly GDP: 120 observations.

These windows balance:

- enough observations for nonlinear estimation;
- sensitivity to long-run structural change;
- comparability with the previous design;
- computational feasibility.

## 9.2 Specification selection versus parameter re-estimation

A major simplification is deliberate.

### Model specification
Lag orders, ARMA orders, STAR type/delay, and other discrete specification choices are selected from the **initial estimation window** and then fixed through the baseline OOS experiment.

### Parameters
Parameters are re-estimated at **every forecast origin** using the current rolling estimation window.

The efficiency gain therefore comes from fixing the discrete specification choices once, dropping the old MSSTAR layer, using warm starts, caching, checkpointing, and parallel execution. It does **not** come from holding estimated parameters fixed between forecast origins.

This every-origin pseudo-out-of-sample design is the academically cleaner baseline because each historical forecast uses parameters estimated from the information set available at that date.

## 9.3 Warm starts and cached estimation

After the first nonlinear fit, use the previous successful refit's parameters as starting values when technically appropriate.

Every fit is cached by:

- series;
- model;
- refit date;
- specification;
- data-window hash.

A rerun must reuse valid cached results unless the relevant input changed.

## 9.4 Forecast horizons

### Primary horizon
- monthly: h = 1 month;
- quarterly: h = 1 quarter.

### Horizon robustness
Monthly:
- h = 3, 6, 12 months.

Quarterly:
- h = 2, 4 quarters.

Use iterated multi-step forecasts from the estimated dynamic model.

The h=1 evidence remains the baseline answer; longer horizons test whether the model ranking changes when nonlinear dynamics have more time to matter.

## 9.5 Estimation-window interpretation

The baseline rolling windows remain:

- 240 observations for monthly targets;
- 120 observations for quarterly GDP.

These exact lengths are an ex ante design compromise, not values claimed to be theoretically optimal. A rolling window is appropriate to the thesis because structural change makes very old observations potentially less representative, while nonlinear models still require enough data for stable estimation.

The methodology therefore treats window length as a documented design assumption. The literature justification file records the bias-variance and structural-break rationale.

---

# 10. Forecast evaluation

## 10.1 Primary accuracy measures

For every model, series, horizon, and evaluation state:

- RMSE;
- MAE;
- out-of-sample (R^2) relative to the AR benchmark.

`R²_OOS = 1 - [Σ e²_model / Σ e²_AR]`

A positive value indicates improvement over AR under squared-error loss.

## 10.2 Primary pairwise test: Harvey-Leybourne-Zu under instability

The primary pairwise test of average point-forecast accuracy is **Harvey, Leybourne, and Zu (2025)**.

The test is chosen because the thesis explicitly studies forecasting under instability. Harvey-Leybourne-Zu show that the conventional Diebold-Mariano long-run variance estimator can become inconsistent when the mean forecast-loss differential changes over time. Their modification replaces full-sample demeaning with nonparametric local demeaning and is designed to test equal **average** forecast accuracy while allowing the relative performance of the forecasts to vary through time.

Report comparisons:

- AR vs ARMA;
- AR vs MSAR;
- AR vs STAR;
- ARMA vs MSAR;
- ARMA vs STAR.

Use:

- squared-error loss;
- absolute-error loss;
- the Harvey-Leybourne-Zu long-run variance construction and local-demeaning procedure exactly as defined in the published paper and supplementary material.

The null is equal average forecast accuracy over the evaluation period.

Implementation must record every tuning choice required by the published procedure, including the local-smoothing/bandwidth rule. Claude may not substitute a generic HAC estimator or an undocumented approximation and still label the result Harvey-Leybourne-Zu.

This is the **primary pairwise inferential test** for the thesis.

## 10.3 Secondary conventional comparison: DM-HLN

Retain the Diebold-Mariano test with the Harvey-Leybourne-Newbold finite-sample correction as a **secondary conventional benchmark**.

Use the same five model pairs and the same squared- and absolute-error losses.

For multi-step horizons, use a horizon-appropriate long-run variance treatment and document the truncation/bandwidth rule.

DM-HLN is retained because:

- it makes the revision from the submitted thesis transparent;
- it is familiar to the reviewer and wider forecasting literature;
- disagreement between DM-HLN and Harvey-Leybourne-Zu is itself informative about sensitivity to instability.

If DM-HLN and Harvey-Leybourne-Zu disagree, the thesis's principal pairwise inferential conclusion follows **Harvey-Leybourne-Zu**, with the discrepancy reported rather than hidden.

## 10.4 Multiple-model comparison

Use the Hansen-Lunde-Nason **Model Confidence Set (MCS)** across all admissible forecast models.

Report:

- 90% MCS;
- 95% MCS;
- squared-error loss;
- absolute-error loss.

This avoids interpreting a large table of pairwise p-values as if one model must be uniquely best.

## 10.5 State-conditioned evaluation and conditional predictive ability

Compute descriptive RMSE and MAE separately for:

- expansion;
- recession;
- peak/trough turning-point window;
- outside turning-point window.

For formal inference about whether relative predictive performance changes with the economic state, use a **Giacomini-White conditional predictive ability regression** for each competitor versus AR.

Baseline test function:

`d_t = α + β_rec REC_t + β_turn TURN_t + u_t`

where:

- `d_t` is the loss differential between the competitor and AR;
- `REC_t` is the target-date recession indicator;
- `TURN_t` is the target-date turning-point-window indicator.

Use HAC standard errors appropriate to the forecast horizon.

Report:

- joint test of conditional equal predictive ability;
- coefficient estimates and p-values for recession and turning-point terms;
- the sign convention for the loss differential;
- descriptive state-specific RMSE/MAE.

If a state indicator has no variation or the regression is numerically unidentified, report descriptive state results only and mark conditional inference unavailable.

**Odendahl, Rossi, and Sekhposyan (2023)** provides recent Q1 support for the broader principle that forecast performance may be state-dependent. Their full hard/smooth unknown-threshold procedure is not a core test here because the economically relevant states are predeclared as NBER recession/expansion and peak/trough windows rather than estimated from an unknown threshold.

## 10.6 Why Clark-McCracken / Clark-West and Amisano-Giacomini are not baseline tests

### Clark-McCracken / Clark-West
These procedures are designed for nested forecast-model comparisons. The principal nonlinear comparisons here, especially AR versus MSAR and AR versus STAR, are not regular nested linear comparisons; under linearity, the nonlinear models also raise nuisance/identification complications.

They therefore are not added mechanically merely because the reviewer named Clark-McCracken as an example of modern forecast-comparison work.

A nested-model test may be used only if a deliberately nested robustness comparison is separately defined and approved.

### Amisano-Giacomini
Amisano-Giacomini is designed for predictive-density comparison using weighted likelihood scores. The thesis evaluates point forecasts and does not construct one common, validated predictive-density system across AR, ARMA, MSAR, and STAR.

It is therefore not appropriate to add the test merely as a checklist response.

This combination of Harvey-Leybourne-Zu, Giacomini-White, MCS, and secondary DM-HLN is the explicit methodological response to **R1-14**.

---

# 11. Required robustness design

Each robustness exercise has a named threat.

| Threat | Required check | Effect on claim |
|---|---|---|
| UNRATE/FEDFUNDS transformation drives result | Alternative level/difference specification | Confirm, qualify, or reject ranking |
| CPI p=12 or lag choice drives result | Re-run CPI with p = 1, 3, 6, 12 under common comparison | Address R1-15 directly |
| Two regimes imposed too strongly | Fit K=3 MSAR | Retain K=2 only if K=3 is not substantively supported |
| Nonlinear value only at h=1 | h=3/6/12 monthly; h=2/4 quarterly | Address P-05 |
| Own-history nonlinearity proxies omitted macro information | Monthly VAR | Address R1-19/P-01 |
| Classical benchmark too weak | ARMA in main horse race | Test whether nonlinear gain survives stronger linear dynamics |
| Conditional variance ignored | ARMA-GARCH(1,1) diagnostic when ARCH-LM rejects | Separate mean forecast from variance dynamics |
| Model failure creates misleading figures | Failure-aware plotting rules | Protect interpretation |
| Estimation-window choice affects ranking | Document 240-month / 120-quarter rolling-window rationale; interpret as a design assumption rather than an optimal window | Prevent overclaiming robustness to window choice |
| Turning-point result depends on the arbitrary window width | Monthly ±1 / ±3 / ±6 months; quarterly 0 / ±1 / ±2 quarters | Confirm, qualify, or reject any claim that nonlinear gains are concentrated around peaks/troughs |
| U.S. sample drives general claim | No false external-validity claim; common-sample/state reporting | Delimit, not “fix,” P-06 |

## 11.1 K=3 decision rule

Fit a three-regime version using the same MSAR structure and lag order.

Do not retain K=3 as the main model merely because its likelihood is larger.

Evaluate:

- BIC;
- convergence;
- regime occupancy;
- transition probabilities;
- economic distinctness of regimes;
- OOS forecast performance.

Keep K=2 as baseline if K=3:

- has an empty/near-empty regime;
- is unstable or non-convergent;
- has materially worse BIC;
- does not improve OOS evidence;
- creates a third state with no stable economic/statistical distinction.

Report the K=3 attempt regardless of outcome.

---

# 12. Nowcasting and mixed-frequency boundary

Nowcasting is **not** implemented in the core thesis.

Reason:

- the central question is model-form robustness under macroeconomic instability;
- nowcasting requires publication calendars, ragged-edge data, mixed-frequency information, and usually real-time vintages;
- adding a full nowcasting architecture would answer a different information-set question and materially expand the thesis.

The final literature chapter must nevertheless explain this boundary and cite mixed-frequency/nowcasting work.

The conclusion may identify real-time nowcasting as a future extension.

This satisfies R1-20 without pretending that native-frequency forecasting is nowcasting.

---

# 13. Figure and table rules

## 13.1 Figures

Every figure must have:

- readable axis units;
- sample dates;
- model labels;
- recession shading where relevant;
- uncertainty bands where the figure represents an estimated relation or correlation and uncertainty is meaningful.

No figure may silently compress the economically relevant series because one model exploded.

For failed/extreme forecast cases:

- show the valid models on a readable main panel;
- show the failed/extreme model in a separate failure panel or diagnostic figure;
- never winsorize or clip a forecast without an explicit label.

If any cross-correlation figure is retained, add 95% confidence bands.

## 13.2 Statistical significance

Tables use one convention:

- * p < 0.10
- ** p < 0.05
- *** p < 0.01

Stars must appear as superscripts in the final typeset thesis, and exact p-values should be reported when space permits.

## 13.3 Main text versus appendix

Main text must include:

- data/sample table;
- stationarity decision table;
- nonlinearity evidence;
- selected model specifications;
- adequacy summary;
- transition/regime credibility summary;
- main h=1 forecast table;
- key horizon/state results;
- K=3 conclusion;
- multivariate conclusion;
- model-failure cases relevant to claims.

Appendices contain:

- full coefficient tables;
- all residual plots;
- all robustness cells;
- optimizer logs;
- bootstrap detail;
- software environment and manifests.

---

# 14. Claims that this methodology can and cannot identify

## It can establish

- whether approved nonlinear models forecast better than classical benchmarks in this U.S. sample;
- whether gains are concentrated in recessions, expansions, or turning points;
- whether gains survive specific transformation, lag, regime, horizon, and cross-variable threats;
- whether nonlinear models are empirically credible or fragile under the declared rules.

## It cannot establish

- causal structural effects of monetary policy;
- an optimal policy rule;
- universal superiority of a model family;
- the same model ranking in other countries;
- true real-time nowcast performance without real-time vintages and ragged-edge information;
- structural regime transmission across variables beyond the limited VAR robustness block.

These limits must be stated before policy interpretation.

---

# 15. Methodological references used to choose the design

The final thesis bibliography should verify and include the methodological works actually used, including:

- Box, G. E. P., Jenkins, G. M., Reinsel, G. C., & Ljung, G. M. on ARMA time-series modeling.
- Dickey, D. A., & Fuller, W. A. on unit-root testing.
- Kwiatkowski, D., Phillips, P. C. B., Schmidt, P., & Shin, Y. (1992) on the stationarity-null KPSS test.
- Zivot, E., & Andrews, D. W. K. (1992) on unit-root testing with an endogenous structural break.
- Hamilton, J. D. (1989) on Markov-switching macroeconomic dynamics.
- Luukkonen, R., Saikkonen, P., & Teräsvirta, T. (1988) on linearity testing against STAR.
- Teräsvirta, T. (1994) on specification, estimation, and evaluation of STAR models.
- Harvey, D. I., Leybourne, S. J., & Zu, Y. (2025) on equal average forecast accuracy in possibly unstable environments; this is the primary pairwise test.
- Diebold, F. X., & Mariano, R. S. (1995) on predictive-accuracy comparison.
- Harvey, D., Leybourne, S., & Newbold, P. (1997) on the finite-sample modification retained as a secondary conventional comparison.
- Giacomini, R., & White, H. (2006) on conditional predictive ability for the predeclared recession/turning-point states.
- Odendahl, F., Rossi, B., & Sekhposyan, T. (2023) on state-dependent forecast evaluation.
- Clark, T. E., & McCracken, M. W. and Clark, T. E., & West, K. D. on nested-model forecast comparison and why those tests are not applied mechanically.
- Hansen, P. R., Lunde, A., & Nason, J. M. (2011) on the Model Confidence Set.
- Sims, C. A. on VAR methodology.

Exact APA entries and page/DOI details belong in Part 9's verified bibliography.

---

# 16. Methodology lock after approval

After the user approves Part 5, Claude Code may not silently change:

- variables;
- transformations or transformation decision rules;
- sample endpoints;
- window lengths;
- model families;
- lag-search grids;
- regime count;
- horizon set;
- refit schedule;
- accuracy metrics;
- statistical tests;
- robustness exercises;
- model-failure rules.

If implementation shows that an approved element cannot be executed correctly, Claude must stop, document the issue, propose alternatives, and wait for approval.
