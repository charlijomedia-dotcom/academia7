# Part 5: Methodology specification

**Project:** *Forecasting Macroeconomic Aggregates under Economic Instability: Theory, Nonlinearity, and Policy Implications*  
**Date:** 5 October 2026  
**Status:** PROPOSED FOR USER APPROVAL  
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

---

# 2. Empirical targets and frozen data

## 2.1 Baseline frozen snapshot

The baseline thesis dataset must be created once and then frozen.

**Snapshot date:** 2026-10-05  
**Data source:** Federal Reserve Economic Data (FRED), exact raw observations saved locally.  
**Default pipeline behavior:** read only from `data/frozen/`.  
**Refresh behavior:** explicit `--refresh-data` only, writing to `data/refreshed/YYYY-MM-DD/`.  
**Never overwrite the baseline snapshot.**

Every raw file must record:

- FRED series ID;
- series title;
- source institution;
- frequency;
- units;
- seasonal-adjustment status;
- retrieval date/time;
- first and last raw observation;
- SHA-256 hash of the saved file.

The final dissertation must report the exact usable sample dates generated from this frozen snapshot.

## 2.2 Core target series

| Target | FRED ID | Frequency | Raw form | Baseline target transformation | Main economic role |
|---|---|---:|---|---|---|
| Real GDP growth | GDPC1 | Quarterly | Real GDP, SAAR | (400Deltaln(GDPC1_t)) | Aggregate real activity |
| CPI inflation | CPIAUCSL | Monthly | CPI-U, seasonally adjusted | (1200Deltaln(CPI_t)) | Inflation |
| Unemployment | UNRATE | Monthly | Percent, seasonally adjusted | Level or first difference by predeclared stationarity rule in §3.4 | Labour-market slack |
| Industrial production growth | INDPRO | Monthly | Index, seasonally adjusted | (1200Deltaln(INDPRO_t)) | Monthly real activity |
| Federal funds rate | FEDFUNDS | Monthly | Percent, monthly average | Level or first difference by predeclared stationarity rule in §3.4 | Monetary-policy stance |
| M2 growth | M2SL | Monthly | Billions of dollars, seasonally adjusted | (1200Deltaln(M2_t)) | Monetary aggregate growth |

Notes:

1. The factors 400 and 1200 express one-period log changes at annualized percentage rates. Scaling does not change the underlying serial dependence, but it improves macroeconomic interpretation.
2. The final thesis must call M2 **the M2 monetary aggregate**, not generically “broad money.”
3. Current FRED metadata confirms that M2SL is a monthly seasonally adjusted series beginning in January 1959 and continuing through the present frozen period. The old suggestion that the usable M2 history ended in 1992 is therefore not carried forward. The pipeline must still print the exact raw and transformed dates from the frozen file.
4. The policy-rate series remains FEDFUNDS because it is a long monthly U.S. effective federal funds rate series consistent with the thesis's Federal Reserve policy focus.
5. INDPRO is retained because it provides monthly real-activity information and a useful business-cycle counterpart to quarterly GDP.
6. All series are U.S. series. The thesis must not generalize the resulting model ranking to other countries.

## 2.3 Baseline sample rules

The processed sample begins at the earliest postwar observation available for each target, subject to the minimum rolling estimation window.

For interpretability and consistency:

- INDPRO is truncated to January 1947 even though a longer historical series exists.
- GDP uses 1947Q1 onward.
- CPI uses 1947M1 onward.
- unemployment uses its available postwar history beginning in 1948.
- FEDFUNDS begins with its available monthly history in 1954.
- M2 begins in January 1959.

The monthly core endpoint is **August 2026** so that the monthly targets share a common terminal month in the frozen snapshot. The quarterly GDP endpoint is **2026Q2**.

If the frozen raw files contradict an expected date above, Claude must stop and document the discrepancy instead of silently changing the sample.

## 2.4 Business-cycle chronology

Use FRED `USREC` only as an **ex post evaluation chronology**, not as a contemporaneous forecasting regressor.

For monthly data:

- recession = USREC = 1 at the forecast target date;
- expansion = USREC = 0;
- peak = month immediately preceding a 0→1 transition;
- trough = month immediately preceding a 1→0 transition;
- turning-point window = ±3 months around each peak or trough.

For quarterly GDP:

- a quarter is recession-affected if at least one month in the quarter has USREC = 1;
- quarterly peak/trough windows are ±1 quarter around the quarter containing the monthly peak/trough date.

This chronology must never leak into model estimation unless a future approved methodology explicitly adds it as a lagged predictor.

---

# 3. Transformation and stationarity protocol

## 3.1 Why stationarity is tested before model fitting

The jury specifically questioned unemployment and the policy rate in levels. The revised thesis will not justify a level specification by appearance or economic convenience alone.

## 3.2 Tests used

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

For each disputed level series:

1. **Clear level stationarity:** ADF rejects unit root and KPSS does not reject stationarity → keep the level as baseline.
2. **Clear nonstationarity:** ADF does not reject and KPSS rejects → use first difference as baseline.
3. **ADF/KPSS disagreement:** use Zivot-Andrews as tie-breaker:
   - ZA rejects unit root with break → retain level as baseline and carry a break-sensitive robustness check;
   - ZA does not reject → use first difference as baseline.

If differenced:

[
Delta x_t=x_t-x_{t-1}
]

is the modeled target. Level forecasts are reconstructed from the last observed level for policy-facing figures, while formal predictive tests are conducted on the stationary modeled target.

The non-baseline transformation is retained as an explicit Chapter 4 robustness check.

This rule is fixed before results are seen.

---

# 4. Pre-estimation evidence for nonlinearity

Nonlinearity is treated as an empirical hypothesis, not as a label attached after a nonlinear model fits.

## 4.1 Smooth-transition linearity test

For each target, after fitting the baseline linear AR structure, apply the Luukkonen-Saikkonen-Teräsvirta / Teräsvirta linearity-testing procedure against STAR alternatives.

Monthly candidate delays: (d=1,ldots,6).  
Quarterly candidate delays: (d=1,ldots,4).

Because scanning several delays creates multiple testing, adjust delay-specific p-values using Holm's method.

Report:

- raw p-values;
- Holm-adjusted p-values;
- selected delay if any;
- LSTAR/ESTAR indication from the Teräsvirta specification sequence.

A failure to reject linearity does **not** prevent the pre-approved STAR model from being estimated for comparison. It does prevent the thesis from treating any later STAR regime interpretation as independently validated evidence of nonlinear structure.

## 4.2 Markov-switching evidence

Testing one regime against two regimes has nonstandard nuisance-parameter problems. Therefore a standard chi-square likelihood-ratio p-value must **not** be used.

Use a **parametric bootstrap likelihood-ratio test** comparing the fitted linear AR benchmark with the two-regime MSAR on the initial estimation window.

Computational rule:

- begin with 199 bootstrap replications;
- if the provisional p-value lies in [0.025, 0.10], extend to 999 replications;
- use a fixed random seed;
- record all failures during bootstrap fitting.

This test is performed once per target for structural evidence. It is not repeated at every forecast origin.

## 4.3 Interpretation rule

The nonlinear tests affect **interpretation**, not whether the model is allowed into a predeclared forecast horse race.

This avoids a post-selection forecast comparison while still answering the jury's request to test nonlinearity explicitly.

---

# 5. Forecasting model hierarchy

The final model set is intentionally smaller than in the submitted thesis.

## 5.1 Classical benchmark 1: AR(p)

[
y_t=c+sum_{j=1}^{p}phi_j y_{t-j}+arepsilon_t
]

This remains the primary benchmark because it is transparent, parsimonious, and directly tests whether nonlinear structure adds information beyond own-history linear dynamics.

### Lag selection

Monthly: (pin{1,ldots,12}).  
Quarterly: (pin{1,ldots,4}).

Primary criterion: BIC.

Selection rule:

1. rank candidates by BIC;
2. among candidates whose residuals do not reject the primary Ljung-Box adequacy check at 5%, choose the lowest-BIC candidate;
3. if every candidate fails the Ljung-Box check, retain the BIC minimum but classify the linear benchmark as diagnostically weak.

The selected order is fixed from the initial estimation window and is not re-searched at every forecast origin.

## 5.2 Classical benchmark 2: ARMA(p,q)

This strengthens the classical comparison requested by Prof. Verne.

Monthly search grid:

- (p,qin{0,ldots,4});
- exclude ARMA(0,0);
- require stationarity and invertibility.

Quarterly search grid:

- (p,qin{0,ldots,2});
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

Baseline equation:

[
y_t=c_{s_t}+sum_{j=1}^{p}phi_j y_{t-j}+arepsilon_t,qquad
arepsilon_tsim N(0,sigma^2_{s_t})
]

where (s_tin{1,2}) follows a first-order Markov chain.

The baseline allows:

- regime-specific intercepts;
- regime-specific innovation variances;
- common AR slopes.

This parsimonious form is chosen deliberately. It tests discrete latent state shifts without doubling every AR coefficient inside relatively short rolling windows.

The AR lag order is inherited from the selected AR benchmark, capped at:

- 4 lags monthly;
- 2 lags quarterly.

The thesis must report:

- transition matrix;
- smoothed regime probabilities;
- regime occupancy;
- expected duration;
- regime-specific means/variances where interpretable;
- convergence status.

## 5.6 Nonlinear model 2: STAR

Use a standard smooth-transition autoregression:

[
y_t=oldsymbol{phi}'x_t+
G(z_{t-d};gamma,c)oldsymbol{	heta}'x_t+arepsilon_t
]

with (G) selected as LSTAR or ESTAR using the Teräsvirta specification sequence.

The AR lag order is inherited from the selected AR benchmark, capped at:

- 4 lags monthly;
- 2 lags quarterly.

Transition-variable delay follows the pre-estimation procedure in §4.1.

Report:

- transition type;
- delay;
- threshold (c);
- smoothness (gamma);
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

- (pin{1,2,3});
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

- effective smoothed-probability occupancy must be at least 5% of observations **and** at least 20 observations;
- transition probabilities (le 0.005) or (ge 0.995) are flagged as boundary behavior;
- expected durations are reported;
- label switching is resolved by ordering regimes by unconditional/regime mean or variance using a fixed documented rule.

A boundary transition probability is a **fragility flag**, not automatic proof of failure. An effectively empty regime is failure.

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

- (gamma) lands on its optimization bound;
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
Parameters are re-estimated on the rolling window according to the scheduled refit rule below.

This prevents repeated specification search at every forecast origin and sharply reduces unnecessary computation.

## 9.3 Scheduled re-estimation

Baseline:

- monthly models: re-estimate every **3 months**;
- quarterly models: re-estimate every **4 quarters**.

At intermediate forecast origins:

- update observed lags/state variables;
- retain the most recently estimated parameters.

All competing univariate models use the same refit calendar.

This is a predeclared forecast method, not a runtime shortcut applied only to expensive nonlinear models.

## 9.4 Warm starts and cached estimation

After the first nonlinear fit, use the previous successful refit's parameters as starting values when technically appropriate.

Every fit is cached by:

- series;
- model;
- refit date;
- specification;
- data-window hash.

A rerun must reuse valid cached results unless the relevant input changed.

## 9.5 Forecast horizons

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

## 9.6 Every-origin re-estimation robustness

To verify that the scheduled refit rule does not create the ranking:

- rerun h=1 with **every-origin parameter re-estimation**;
- use the final 120 monthly forecast origins and final 40 quarterly forecast origins;
- keep model specifications fixed;
- compare rankings and loss differentials with the scheduled-refit results over exactly the same recent block.

This gives the jury a direct sensitivity check without recreating the old full-sample nine-hour design as the baseline.

---

# 10. Forecast evaluation

## 10.1 Primary accuracy measures

For every model, series, horizon, and evaluation state:

- RMSE;
- MAE;
- out-of-sample (R^2) relative to the AR benchmark.

[
R^2_{OOS}=1-rac{sum e^2_{model}}{sum e^2_{AR}}
]

A positive value indicates improvement over AR under squared-error loss.

## 10.2 Pairwise predictive-accuracy test

Use the Diebold-Mariano test with the Harvey-Leybourne-Newbold small-sample correction.

Report comparisons:

- AR vs ARMA;
- AR vs MSAR;
- AR vs STAR;
- ARMA vs MSAR;
- ARMA vs STAR.

Use:

- squared-error loss;
- absolute-error loss;
- HAC variance appropriate to horizon, with minimum truncation lag (h-1).

The null is equal predictive accuracy.

DM is retained as a familiar pairwise test but is no longer the only formal comparison.

## 10.3 Multiple-model comparison

Use the Hansen-Lunde-Nason **Model Confidence Set (MCS)** across all admissible forecast models.

Report:

- 90% MCS;
- 95% MCS;
- squared-error loss;
- absolute-error loss.

This avoids interpreting a large table of pairwise p-values as if one model must be uniquely best.

## 10.4 State-conditioned evaluation

Compute the same forecast losses separately for:

- expansion;
- recession;
- peak/trough turning-point window;
- outside turning-point window.

For each state, report the difference in mean loss relative to AR with a moving-block bootstrap confidence interval.

Block lengths:

- monthly: 12 observations;
- quarterly: 4 observations.

Minimum observations for formal state-specific inference: 20 forecast errors.

If a state/horizon cell has fewer than 20 observations, report descriptive RMSE/MAE only and label inference as unavailable.

## 10.5 Why Clark-West and Amisano-Giacomini are not baseline tests

### Clark-West
Designed for nested forecast comparisons. The principal nonlinear models here are not simple nested linear expansions of AR, so Clark-West is not the main test.

It may be used for a specifically nested robustness comparison if Part 8 identifies one, but Claude may not add it automatically.

### Amisano-Giacomini
Primarily a predictive-density comparison. The thesis evaluates point forecasts, not a common set of calibrated predictive densities.

Therefore it is not appropriate merely because the reviewer listed it as an example.

This is an explicit methodological answer to R1-14 rather than a checklist response.

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
| Scheduled refit changes ranking | Every-origin recent-block robustness | Computational/design sensitivity |
| Classical benchmark too weak | ARMA in main horse race | Test whether nonlinear gain survives stronger linear dynamics |
| Conditional variance ignored | ARMA-GARCH(1,1) diagnostic when ARCH-LM rejects | Separate mean forecast from variance dynamics |
| Model failure creates misleading figures | Failure-aware plotting rules | Protect interpretation |
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
- Diebold, F. X., & Mariano, R. S. (1995) on predictive-accuracy comparison.
- Harvey, D., Leybourne, S., & Newbold, P. on small-sample correction to forecast-comparison tests.
- Giacomini, R., & White, H. (2006) as relevant conditional-predictive-ability literature, even though it is not the primary final test.
- Clark, T. E., & West, K. D. (2007) for nested-model forecast comparison and the reason it is not applied mechanically.
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
