# Part 5: Data selection, retrieval, sample, transformation, and frozen-reproducibility rationale

**Date:** 6 October 2026  
**Status:** PROPOSED FOR USER APPROVAL  
**Companion files:** `part5_methodology_specification.md`, `part5_methodology_literature_justification.md`  
**Purpose:** Give a defense-ready answer to five questions: why these macroeconomic series, why not others, how they are retrieved, why the sample dates are chosen, and how exact future reproducibility is guaranteed.

# 1. Alignment with Part 4

The data architecture follows the approved Part 4 argument.

Part 4 retains Fisher, Phillips/Phelps, Okun, monetary-policy, money-supply, and business-cycle mechanisms. The empirical series are therefore selected to represent the minimum set of observable U.S. macroeconomic concepts required by those mechanisms:

| Part 4 concept | Empirical representation | Reason |
|---|---|---|
| Price dynamics / inflation | CPIAUCSL | Long monthly postwar consumer-price history |
| Aggregate real growth | GDPC1 | Comprehensive real output measure |
| Monthly cyclical real activity | INDPRO | Monthly real-activity indicator without interpolating GDP |
| Labour-market slack | UNRATE | Direct unemployment measure |
| Monetary-policy stance | FEDFUNDS | Long monthly effective federal funds rate |
| Monetary aggregate | M2SL | Gives empirical content to the money-supply discussion retained at Prof. Verne's request |
| Expansion/recession/turning points | USREC | External NBER-based chronology used only for evaluation |

The data set is therefore generated from the thesis logic, not chosen because the series happen to be easy to download.

# 2. Why the United States rather than another country?

The United States is a deliberate empirical case selection, not a default chosen only because FRED is convenient.

The choice combines economic, statistical, and reproducibility arguments.

## 2.1 Economic reason

The thesis is explicitly concerned with inflation, output growth, unemployment, monetary conditions, interest rates, recessions, and policy response. The United States provides a coherent setting in which all of these mechanisms are economically important and where the Federal Reserve gives the monetary-policy dimension a clear institutional interpretation.

The U.S. postwar record also contains multiple forms of instability relevant to the thesis question: inflation and disinflation episodes, recessions and recoveries, financial stress, prolonged low-rate conditions, rapid tightening cycles, and the pandemic shock.

This makes the country suitable for asking whether linear relationships remain adequate across changing macroeconomic states.

## 2.2 Statistical reason

The nonlinear models require long histories and repeated state changes.

The U.S. offers:

- long monthly and quarterly official series;
- repeated NBER-dated recessions and expansions;
- enough observations for rolling estimation;
- enough variation to examine peaks, troughs, structural breaks, and regime behavior;
- a common institutional setting, avoiding the cross-country heterogeneity that would arise if different countries with different monetary frameworks, definitions, currencies, and statistical systems were pooled.

A multi-country design would answer an additional external-validity question, but it would also require harmonization and country-specific institutional controls beyond the central thesis question.

## 2.3 Data and reproducibility reason

The U.S. is especially suitable because the required official series are accessible through FRED/ALFRED with:

- stable series identifiers;
- simple Python retrieval;
- historical vintages;
- consistent metadata;
- no manual spreadsheet construction.

This is not merely a convenience. It materially strengthens reproducibility.

## 2.4 What the U.S. choice does not imply

The thesis does **not** claim that a model ranking obtained for U.S. macroeconomic series is universal.

The correct conclusion is:

> the United States provides a rich, long, reproducible empirical environment in which to test whether nonlinear state dependence adds forecast value under instability; international generalization requires separate evidence.

Accordingly:

- **country-specific result:** which model forecasts a U.S. aggregate better in this sample;
- **potentially transferable contribution:** the benchmark-centred comparative design, diagnostic sequence, failure rules, and robustness logic;
- **future external-validity test:** replication on other economies with sufficiently long and harmonized data.

### Defense-ready answer

> We chose the United States because it combines high economic relevance with an unusually long and reproducible postwar macroeconomic database containing repeated recessions, inflation regimes, and monetary-policy changes. These characteristics are particularly important for nonlinear and state-dependent forecasting. We deliberately avoid a cross-country panel because that would add institutional and measurement heterogeneity to a thesis whose central question is model-form robustness. Our model rankings are therefore U.S.-specific, while the research design can later be replicated internationally.

# 3. Selection criteria

A core series must satisfy all seven criteria:

1. direct connection to Part 4 theory or policy motivation;
2. distinct economic concept, with minimum redundancy;
3. official U.S. source;
4. long enough postwar history for repeated expansion/recession episodes;
5. monthly or quarterly frequency;
6. automatic retrieval from an open internet source using a stable identifier;
7. no manual construction required.

FRED satisfies the retrieval criterion because it distributes official series from the BEA, BLS, Federal Reserve Board, and other authorities and exposes observations programmatically.

# 4. Why each target is retained

## 3.1 Real GDP, GDPC1

**Why:** GDP is the broadest standard measure of real aggregate production and therefore the natural quarterly growth target. It connects directly to the thesis's growth discussion and to Okun-style output-labour relations.

**Why real rather than nominal GDP:** the thesis is interested in real activity. Using real GDP prevents price-level movements from being mechanically embedded in the output target.

**Why quarterly:** GDP is officially observed quarterly. The thesis does not fabricate monthly GDP through interpolation.

**Transformation:**  
`400 × Δln(GDPC1)`

This produces an annualized continuously compounded quarter-over-quarter real-growth rate.

**Expected frozen range:** 1947Q1 to 2026Q2 in raw levels, subject to vintage verification.

## 3.2 CPI, CPIAUCSL

**Why:** CPI gives a long official monthly consumer-price series beginning in 1947. Inflation is central to Fisher, Phillips/Phelps, and stabilization-policy reasoning.

**Why CPI rather than making PCEPI the core target:** PCEPI is highly relevant and is the Federal Reserve's preferred inflation measure, but it begins in 1959. Using CPI preserves twelve additional years of postwar history and avoids giving inflation two core targets while other macro concepts receive one. The thesis studies model-form robustness across macro aggregates, not the choice of inflation index.

**Transformation:**  
`1200 × Δln(CPIAUCSL)`

This converts the price index into annualized one-month continuously compounded inflation.

**Expected frozen range:** 1947M1 to 2026M8 in raw levels.

## 3.3 Unemployment, UNRATE

**Why:** UNRATE is the direct U.S. labour-market slack variable in Phillips/Phelps and Okun reasoning. It is monthly, official, and begins in 1948.

**Why not log it automatically:** unemployment is already a rate and can approach low values. A log transformation has no necessary economic interpretation here.

**Transformation:** level or first difference according to the predeclared ADF/KPSS/Zivot-Andrews rule.

**Expected frozen range:** 1948M1 to 2026M8 for the common monthly endpoint.

## 3.4 Industrial production, INDPRO

**Why:** GDP is quarterly, but the thesis also needs a monthly real-activity target to evaluate state dependence around recessions and turning points. INDPRO is an official Federal Reserve index and is strongly tied to cyclical fluctuations.

**Why not use its full pre-1919 history:** the thesis is a postwar U.S. macroeconomic forecasting study. Great Depression and wartime observations would create institutional regimes not shared by the other core series.

**Transformation:**  
`1200 × Δln(INDPRO)`

**Sample:** deliberately truncated to 1947M1 through 2026M8.

## 3.5 Federal funds rate, FEDFUNDS

**Why:** it is the long monthly effective federal funds rate and the most direct policy-rate series for the thesis's Federal Reserve focus.

**Why not replace it with a Treasury yield:** Treasury yields include term-premium and maturity effects. The thesis needs a monetary-policy stance variable, not a market yield curve target.

**Transformation:** level or first difference according to the stationarity/break rule.

**Expected frozen range:** 1954M7 to 2026M8.

## 3.6 M2 monetary aggregate, M2SL

**Why:** Prof. Verne explicitly asked the thesis to retain the money-supply/monetary-aggregate dimension. M2 supplies empirical content to that discussion and gives the monthly VAR a monetary-conditions variable.

**Why call it M2 monetary aggregate rather than 'broad money':** the official object is M2SL, and precise terminology avoids implying equivalence with every international broad-money definition.

**Transformation:**  
`1200 × Δln(M2SL)`

**Expected frozen range:** 1959M1 to 2026M8.

## 3.7 USREC

**Why:** Prof. Verne and the jury require visible analysis of recessions, expansions, peaks, and troughs.

**Role:** USREC is used only after forecasts are produced to classify realized target dates. It is not a contemporaneous predictor. This prevents the official recession chronology from leaking future information into the forecasting model.

# 5. Why more core targets are not added

The methodology is deliberately parsimonious.

| Candidate | Why it is not a seventh core target |
|---|---|
| PCEPI | Important, but duplicates inflation and starts later than CPI. Explicitly acknowledged as the Fed-preferred inflation measure. |
| Core CPI / core PCE | Alternative inflation measurement question, not necessary to answer the model-form question. |
| Public debt / fiscal deficit | Important motivation, but introduces different accounting frequencies and a separate fiscal-dynamics research problem. |
| Exchange rate | Important for open-economy analysis but not required for the U.S.-aggregate core question. |
| Oil / commodity prices | Useful shock variables but would turn the old policy application back into a separate branch rather than resolve the central comparison. |
| Stock prices / credit spreads | Financial predictors, not core macro aggregates in the approved Part 4 question. |
| Additional interest rates | Would duplicate the policy-rate concept and introduce term-structure questions outside the core design. |

This is not a claim that these variables are unimportant. It is a claim that adding them would reduce focus without improving identification of the thesis's central question.

# 6. Open-access and automatic retrieval architecture

## 5.1 Primary provider

Use FRED/ALFRED from the Federal Reserve Bank of St. Louis.

The underlying sources remain the official agencies:

- GDPC1: U.S. Bureau of Economic Analysis;
- CPIAUCSL and UNRATE: U.S. Bureau of Labor Statistics;
- INDPRO, FEDFUNDS, and M2SL: Board of Governors of the Federal Reserve System;
- USREC: NBER chronology distributed by the St. Louis Fed.

## 5.2 Python retrieval

No manual CSV editing is permitted.

The first frozen initialization must use Python `requests`, `fredapi`, or an equivalent simple FRED client with the official FRED API.

The FRED API key must be read from:

`FRED_API_KEY`

It must never be hard-coded into the repository.

The API request must specify the historical thesis vintage:

`vintage_dates=2026-10-05`

or the equivalent real-time arguments.

This is preferable to simply downloading today's FRED history because macroeconomic series can be revised.

## 5.3 Why the baseline uses a historical vintage

The FRED/ALFRED documentation explicitly distinguishes current FRED data from historical real-time information and allows a vintage date to retrieve data as known on a chosen historical date.

Therefore the baseline can be reconstructed later from the web even if FRED's current historical values have changed.

The saved local frozen files remain the primary reproducibility source. The historical-vintage API is an independent reconstruction route.

# 7. Sample-period justification

## 6.1 Why the start dates differ across targets

For univariate forecasting, there is no statistical requirement that every series begin on the same date.

Using the earliest defensible postwar observation for each series:

- maximizes observations;
- increases the number of recession/expansion episodes;
- improves nonlinear estimation;
- avoids discarding useful history merely because another variable begins later.

A common start date is imposed only when variables must enter the same multivariate VAR.

## 6.2 Why postwar rather than the full historical record

The thesis asks about modern U.S. macroeconomic forecasting and policy.

Pre-1947 data would bring in the Great Depression, wartime controls, and monetary/fiscal institutions fundamentally different from the postwar period. Those regimes are also not available across the complete target set.

The chosen start rule is therefore an economic comparability rule, not a result-driven cutoff.

## 6.3 Why the monthly endpoint is 2026M8

The thesis vintage date is 5 October 2026.

As of that information set:

- UNRATE already has September 2026;
- CPI, INDPRO, FEDFUNDS, and M2 are available through August 2026;
- therefore August 2026 is the latest month jointly available across all monthly targets.

Using a common monthly terminal date prevents the monthly model comparisons from ending in different information sets.

## 6.4 Why GDP ends in 2026Q2

Q2 2026 is the latest released quarterly real-GDP observation available by the thesis vintage date. Q3 was not yet part of the information set.

Thus the final date is determined mechanically by publication availability.

## 6.5 Why the VAR starts in 1959M1

The VAR needs all monthly variables in the same row.

M2 is the latest-starting monthly component, so the common multivariate sample begins in January 1959.

No series is artificially extended backward.

# 8. Transformation justification

## 7.1 Log differences

For positive trending level variables, use:

`Δln(X_t) = ln(X_t) - ln(X_{t-1})`

because it:

- approximates proportional growth;
- has an additive interpretation over short intervals;
- reduces stochastic/deterministic trend behavior;
- creates a target compatible with stationary time-series methods.

## 7.2 Annualization factors

Quarterly GDP:

`400 × Δln(GDP_t)`

Monthly CPI, INDPRO, M2:

`1200 × Δln(X_t)`

The factors only scale the one-period continuously compounded change into an annualized percentage rate. They do not add predictive information.

## 7.3 Rate variables

UNRATE and FEDFUNDS are already percentages.

Their level/difference representation is determined by the stationarity protocol because differencing a rate changes the economic question from 'what is the level?' to 'how much did the rate change?'

If differencing is required statistically, policy-facing figures reconstruct the level from the last observed value, while formal forecast evaluation remains on the modeled stationary target.

# 9. Test justification

| Test | Why it exists in the design |
|---|---|
| ADF | Tests the unit-root null |
| KPSS | Uses stationarity as the null, complementing ADF |
| Zivot-Andrews | Addresses the possibility that a structural break explains apparent nonstationarity in UNRATE/FEDFUNDS |
| Tsay | General pre-estimation evidence against linear autoregressive dynamics |
| Luukkonen-Saikkonen-Teräsvirta / Teräsvirta | Tests/specifies STAR-type smooth-transition nonlinearity |
| Ljung-Box | Checks remaining serial dependence after model fitting |
| ARCH-LM | Detects conditional heteroskedasticity and determines whether a GARCH diagnostic is relevant |
| Jarque-Bera | Describes residual non-normality; it is not a standalone rejection rule for point forecasts |
| BIC | Penalized model-order selection that discourages unnecessary parameters |
| DM-HLN | Pairwise out-of-sample predictive-accuracy comparison |
| Giacomini-White | Tests whether relative predictive ability changes with recession/turning-point information |
| Model Confidence Set | Allows the evidence to identify a set of statistically competitive models rather than forcing a unique winner |

Each test therefore answers a named methodological question. None is included only because it is conventional.

# 10. Frozen-data reproducibility protocol

Exact future reproduction requires more than remembering the series IDs.

The baseline workflow is:

1. retrieve the 2026-10-05 ALFRED/FRED vintage programmatically;
2. save the raw untransformed observations;
3. save metadata and exact API parameters;
4. hash every file;
5. save one master manifest;
6. calculate all transformations locally;
7. make the normal pipeline read only the frozen files;
8. verify hashes before estimation;
9. block any silent internet refresh;
10. store future refreshes under a different dated directory.

Therefore a rerun years later does not depend on whatever FRED happens to report at that future date.

# 11. Defense-ready answers

**Why these six series?**  
Because together they give the minimum non-redundant representation of the macroeconomic concepts explicitly used in Part 4: inflation, real growth, monthly cyclical activity, labour slack, monetary policy, and the monetary aggregate.

**Why not more?**  
Because the thesis is testing model-form robustness, not building an exhaustive macroeconomic database. Extra targets must add a distinct identification role, not simply more columns.

**Why CPI rather than PCE as the core inflation target?**  
CPI provides a longer postwar monthly history from 1947. PCE is explicitly acknowledged as the Fed-preferred inflation measure, but adding both would overweight one economic concept in the cross-aggregate model comparison.

**Why start in 1947 for some series?**  
That is the beginning of the modern postwar sample available for GDP/CPI and creates a coherent policy regime while avoiding Great Depression/WWII observations.

**Why not force every target to start in 1959?**  
That would throw away valid univariate history solely because M2 begins later. The common 1959 start is used only where a multivariate model mathematically requires common observations.

**Why end in August 2026?**  
It is the latest month jointly available across all monthly core targets as of the frozen 5 October 2026 information set.

**Why freeze a vintage?**  
Because macroeconomic data are revised. A frozen local snapshot plus an ALFRED historical-vintage reconstruction route ensures the thesis remains exactly reproducible.

**Why transform locally rather than request FRED growth rates?**  
Because local transformations make the exact formula auditable and guarantee that the same raw frozen values always generate the same model inputs.
