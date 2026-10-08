# Part 3: Current methodology map

**Date:** 3 October 2026  
**Status:** APPROVED
**Source:** `CHARLIJO TANNOURY PHD THESIS May 2026.pdf`  
**Purpose:** Record the methodology currently implemented and described in the submitted thesis, without yet approving it as the final Part 5 methodology.

## 1. Empirical scope

The core empirical design is **univariate / single-equation by aggregate**.

Six U.S. macroeconomic targets are analyzed separately:

| Internal series | Source ID | Frequency | Current transformation | Economic role |
|---|---|---:|---|---|
| US_RGDP_GR | GDPC1 | Quarterly | 100 × log difference | Real GDP growth |
| US_CPI_INF | CPIAUCSL | Monthly | 100 × log difference | CPI inflation |
| US_UNRATE | UNRATE | Monthly | Level | Unemployment rate |
| US_INDPRO_GR | INDPRO | Monthly | 100 × log difference | Industrial production growth |
| US_POLICY_RATE | FEDFUNDS | Monthly | Level | Effective federal funds rate |
| US_M2_GR | M2SL | Monthly | 100 × log difference | M2 growth |

USREC is used as an external recession/expansion chronology for evaluation.

**Source:** Chapter 3.1, PDF pp. 76–81.

---

## 2. Data retrieval and sample construction

Current pipeline:
- retrieves FRED series through `pandas_datareader`;
- fixes the nominal start date at 1 January 1947;
- leaves the terminal date open;
- downloads observations through the latest value available when the code is executed;
- applies transformations after numerical cleaning;
- keeps quarterly GDP at quarterly frequency and monthly series at monthly frequency;
- aligns USREC to each target frequency.

For quarterly series, the monthly recession indicator is grouped to quarter and the within-quarter maximum is used.

The thesis describes this as reproducible, but because the end date is open, repeated execution at different dates can change the sample. This is precisely the issue later solved by the frozen-data rule adopted for the revised project.

**Source:** Chapter 3.2, PDF pp. 81–88.

---

## 3. Current transformation logic

The current deterministic transformation set is:

- `level`
- `diff`
- `logdiff`

with:

- level for unemployment and policy rate;
- log differences for GDP, CPI, industrial production, and M2;
- no baseline first-difference specification.

The justification for unemployment and the policy rate is primarily economic interpretability. The thesis describes unemployment as a “stationary-looking percentage rate” and argues that the absolute policy-rate level is economically meaningful.

The current manuscript does **not** contain a formal full-sample unit-root/stationarity testing block for these two level series, and no ADF/KPSS/Zivot-Andrews-type results were found in the manuscript.

**Source:** Chapter 3.1–3.2, PDF pp. 78–84.

---

## 4. Sample sufficiency and rolling windows

A series is processed only if it contains enough usable observations for the chosen rolling window, forecast horizon, and buffer.

Current fixed windows:
- monthly: 240 observations;
- quarterly: 120 observations.

Current buffers:
- monthly: 24;
- quarterly: 8.

The initial split uses a chronological training share of 0.50, subject to the window and terminal constraints.

**Source:** Chapter 3.2–3.3, PDF pp. 84–90; Appendix E.

---

## 5. Forecast horizons

Current baseline:
- monthly horizons = `[1]`;
- quarterly horizons = `[1]`.

Thus, the submitted empirical application is one-step-ahead only.

The code is described as capable of recursive multi-step forecasting, but longer horizons are not part of the reported core empirical evidence.

**Source:** Chapter 3.4 and 3.7–3.9, PDF pp. 95, 109–120.

---

## 6. Linear benchmark: AR(p)

Model:
- autoregression with intercept;
- OLS estimation;
- recursive forecasting.

Lag selection:
1. scan p = 1 to p_max;
2. monthly p_max = 12;
3. quarterly p_max = 8;
4. choose the AIC-minimizing candidate;
5. apply a Ljung-Box residual check;
6. if residual autocorrelation remains significant at 5%, increase the lag until the residual check is acceptable or p_max is reached.

This procedure is repeated in rolling estimation.

Important current result:
CPI can select p = 12, which is one of the specific jury concerns and is not independently stress-tested in the submitted thesis through an explicit alternative-lag robustness block.

**Source:** Chapter 3.4, PDF pp. 91–96.

---

## 7. MSAR specification

Current baseline:
- `k_regimes = 2`;
- statsmodels MarkovRegression-type implementation;
- switching exogenous coefficients preferred;
- switching variance enabled;
- lag order inherited from the AR benchmark.

Current intended model:
- regime-specific intercept;
- regime-specific AR coefficients;
- regime-specific variance;
- first-order Markov chain.

The thesis defines:
- transition probabilities;
- row-stochastic transition matrix;
- stationary/ergodic distribution;
- expected regime duration;
- filtered regime probabilities;
- probability-weighted fitted values.

Current fallback:
If the fully switching coefficient specification fails, the code can automatically re-estimate with `switching_exog = False`, retaining regime-switching variance and transitions.

This fallback changes the effective parameterization across failed and successful fits and must be explicitly controlled in the revised methodology if retained.

**Source:** Chapter 3.5, PDF pp. 96–102.

---

## 8. STAR / MSSTAR specification

The current hybrid model combines:
- an MSAR regime clock;
- smoothed regime probabilities;
- regime-specific STAR components;
- weighted nonlinear least squares.

Transition functions:
- LSTAR;
- ESTAR.

Current delay search:
- monthly delays {1,2,3,4,5,6};
- quarterly delays {1,2,3,4}.

Current nonlinearity / delay procedure:
- uses a Luukkonen-Saikkonen-Teräsvirta auxiliary regression;
- augments the linear design with terms in z, z², z³;
- computes a joint F test against linearity;
- selects the delay minimizing the joint p-value;
- chooses LSTAR versus ESTAR using nested p-value logic.

Current nonlinear-estimation controls include:
- gamma bounds [10^-3, 10^3];
- multiple gamma starts [1,5,10];
- median initialization for c;
- standardized transition variable;
- high nonlinear least-squares function-evaluation limit.

Important observation:
The submitted thesis **does contain** a STAR-related formal linearity test in Chapter 3.6. Therefore the jury statement that no nonlinearity test exists is not literally true of this PDF as currently supplied. However, the test is embedded mainly inside the MSSTAR delay/type selection procedure. The results of the linearity tests are not elevated into a clear cross-series diagnostic table in the main empirical chapter, and the test does not by itself justify the separate MSAR specification.

**Source:** Chapter 3.6, PDF pp. 102–108.

---

## 9. In-sample adequacy

Current diagnostics include:
- Ljung-Box;
- ARCH-LM;
- Jarque-Bera;
- R²;
- MAPE;
- AIC;
- BIC;
- log-likelihood where comparable;
- residual variance proxies.

The manuscript gives formulas and interpretations for the main tests.

Remaining presentation issue:
The reviewer asked for explicit null hypotheses and null distributions. The current chapter explains the tests but does not consistently present each one in a standardized “H0 / statistic / distribution / rejection rule / interpretation” format.

**Source:** Chapter 3.8, PDF pp. 112–117.

---

## 10. Out-of-sample forecast evaluation

Current metrics:
- RMSE;
- MAE;
- MAPE;
- out-of-sample R².

Current pairwise model comparisons:
- AR vs MSAR;
- AR vs MSSTAR;
- MSAR vs MSSTAR.

Current formal test:
- Diebold-Mariano under squared loss;
- two-sided alternative;
- Newey-West variance with lag h−1.

The manuscript does not implement Clark-McCracken or Amisano-Giacomini.

**Source:** Chapter 3.9, PDF pp. 117–121.

---

## 11. Conditional predictive ability

The submitted thesis adds a Giacomini-White-type conditional predictive ability regression:

loss differential = intercept + recession indicator + turning-point indicator + error.

Current logic:
- detect whether relative predictive performance changes in recessions or near turning points;
- HAC standard errors;
- minimum 30 observations for the richer CPA regression;
- fallback to a simpler recession-only specification if the full state regression is unstable.

This is a meaningful extension beyond a DM-only design.

**Source:** Chapter 3.9, PDF pp. 119–120.

---

## 12. State-conditioned evaluation

Forecast errors are assigned to the state at the **realized target date**, not the forecast origin.

Current subsets:
- full test;
- recession;
- expansion;
- turning-point windows;
- outside turning-point windows.

Turning point:
- change in aligned USREC;
- monthly window = ±3 months;
- quarterly window = ±1 quarter.

This evaluation chronology is external to the model-implied regimes, which preserves a common benchmark across AR, MSAR, and MSSTAR.

**Source:** Chapter 3.10–3.11, PDF pp. 121–130.

---

## 13. Model-failure treatment in the current thesis

The thesis explicitly discusses severe failures rather than hiding them.

Examples:
- policy-rate MSAR with coefficients in the hundreds, variance above 90,000, and near-absorbing transition probabilities;
- several MSSTAR specifications with severe out-of-sample deterioration;
- GDP MSAR with a nearly zero diagonal persistence probability for one regime;
- unemployment MSAR described as unreliable.

The manuscript treats fragility as part of the substantive result.

What is still missing:
There is no fully predeclared model-failure decision rule in the methodology that specifies when a fit is:
- converged but inadmissible;
- numerically degenerate;
- substantively uninterpretable;
- excluded from forecast comparison;
- shown only as a failure case.

**Source:** Chapter 4.6, PDF pp. 152–154.

---

## 14. Oil-price application

The oil application adds lagged Brent oil-price growth to CPI inflation.

Current models:
- ARX;
- MSAR-X;
- MSSTAR-X.

Current oil transformation:
100 × [ln(Oil_t) − ln(Oil_{t−1})], lagged one month.

Current evaluation:
- final 30 monthly observations;
- one-step-ahead rolling re-estimation.

Current finding:
- ARX has the lowest OOS RMSE and MAE;
- nonlinear models improve in-sample fit but not the final OOS ranking.

Critical scope point:
The manuscript explicitly states that this remains a **single-equation inflation forecasting exercise, not a VAR system**. It therefore adds a cross-variable predictor but does not solve the jury's broader multivariate-system concern.

**Source:** Chapter 4.7, PDF pp. 155–159.

---

## 15. Current reproducibility design

Strengths:
- parameterized configuration;
- series audit files;
- scripted data retrieval;
- explicit windows, lags, diagnostics, and model controls;
- Appendices D and E expose computational details.

Current weakness:
The final date is open, so the thesis dataset is not frozen. The same code can retrieve later observations and potentially revised historical data on a later run.

The revised project has already decided to correct this with a frozen thesis dataset and an explicit refresh mode.

---

## 16. Methodology issues already acknowledged by the thesis

Chapter 3.12 and the conclusion explicitly recognize:
- single-equation limitations;
- reduced-form rather than structural interpretation;
- parameter fragility;
- finite-sample uncertainty;
- lack of full real-time data vintages;
- need for multivariate extensions;
- need for international validation;
- need for longer horizons.

This is important: Parts 4 and 5 are not starting from a thesis that is unaware of its limitations. They are starting from a thesis that often identifies the limitation correctly but does not always resolve it inside the empirical design.
