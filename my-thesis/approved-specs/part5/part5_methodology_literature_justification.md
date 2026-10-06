# Part 5: Literature justification for the methodology

**Project:** *Forecasting Macroeconomic Aggregates under Economic Instability: Theory, Nonlinearity, and Policy Implications*  
**Date:** 5 October 2026  
**Status:** PROPOSED FOR USER APPROVAL  
**Purpose:** Provide a defense-ready academic justification for every important Part 5 methodological choice. This file distinguishes choices directly supported by high-level literature from transparent design conventions and records choices that were changed or removed after the literature audit.

---

# 1. Source-quality rule used in this audit

The audit prioritizes:

1. peer-reviewed articles in leading economics, econometrics, statistics, and forecasting journals;
2. journals currently ranked Q1 in the relevant SCImago category, using Scopus-based SJR data;
3. original methodological articles rather than secondary summaries;
4. publisher pages, DOI records, and institutional bibliographic records for verification.

Important qualification:

**“Q1” below refers to the journal's current SCImago/Scopus-based standing checked for this audit. It does not claim that the journal had the same quartile in the year when an older article was published.**

Current Q1 venues used heavily in this methodology include Econometrica, Review of Economic Studies, Journal of Econometrics, Journal of Business & Economic Statistics, Journal of the American Statistical Association, Biometrika, Annals of Statistics, International Journal of Forecasting, Journal of Monetary Economics, and Journal of Money, Credit and Banking.

SCImago states that its current journal metrics are based on Scopus data. The economics/econometrics ranking lists Econometrica and Journal of Econometrics as Q1. The statistics ranking lists Journal of Business & Economic Statistics, Journal of the American Statistical Association, Biometrika, and Annals of Statistics as Q1.

---

# 2. Audit result

The methodology now follows this rule:

> **No important method is retained merely because it appeared in the previous thesis or because it sounds sophisticated. Each choice must be either supported by strong academic literature or defended as a transparent, predeclared design convention. If neither condition is met, the choice is removed or revised.**

After this audit, four earlier Part 5 choices were materially changed:

1. **Scheduled parameter refitting was removed.**  
   The baseline now re-estimates parameters at every forecast origin. This is more consistent with pseudo-out-of-sample macroeconomic forecasting practice. Computational savings instead come from fixing discrete specification choices, removing MSSTAR, simplifying MSAR, warm starts, caching, checkpointing, and parallelization.

2. **The proposed simple bootstrap LR test for one versus two Markov regimes was removed.**  
   The regime-switching testing problem is nonstandard. Recent top-journal theory shows that nuisance parameters are unidentified under the null and that some bootstrap procedures can be inconsistent. The thesis will not manufacture a simple p-value from an inadequately justified test.

3. **Ad hoc block-bootstrap confidence intervals for recession/turning-point comparisons were removed.**  
   Formal state dependence is now tested with the Giacomini-White conditional predictive ability framework.

4. **The MSAR baseline was simplified to a Hamilton-style regime-dependent mean with common AR dynamics and common innovation variance.**  
   This is much easier to identify and defend than switching every intercept, AR coefficient, and variance simultaneously.

These revisions make the methodology more defensible and simpler.

---

# 3. Decision-by-decision literature justification

## 3.1 Stationarity before dynamic forecasting

### Methodological choice

Use:

- Augmented Dickey-Fuller logic for a unit-root null;
- KPSS for the complementary stationarity null;
- Zivot-Andrews for UNRATE and FEDFUNDS because the jury explicitly requires a break-sensitive test.

### Academic support

**Dickey and Fuller (1979)** develop the unit-root testing framework for autoregressive time series.

**Kwiatkowski, Phillips, Schmidt, and Shin (1992)** explicitly reverse the null and test stationarity against a unit-root alternative. Using ADF and KPSS together is therefore useful because the tests ask complementary questions rather than duplicating the same null.

**Zivot and Andrews (1992)** develop a unit-root test in which the breakpoint is estimated rather than imposed exogenously. This directly supports the jury's concern that a level series may appear nonstationary because of a structural break.

### Defense sentence

> We do not choose the unemployment-rate or policy-rate transformation from visual inspection. We use complementary unit-root/stationarity evidence and a structural-break test because the statistical representation of persistent macroeconomic rates can change materially once breaks are allowed.

### Status

**Strong literature support.**

---

## 3.2 Initial-window transformation decision and full-sample verification

### Methodological choice

The baseline pseudo-out-of-sample transformation of UNRATE and FEDFUNDS is determined from the **initial estimation window**. Full-sample stationarity tests are still reported because the jury asked for them, but they do not retroactively alter the historical forecast experiment.

### Academic and logical basis

Pseudo-out-of-sample forecasting is designed to approximate the information that would have been available at the forecast date. Marcellino, Stock, and Watson (2006) explicitly describe pseudo-out-of-sample forecasts as being based only on data available before the forecast period.

Using a transformation chosen from the future full sample would contaminate that chronology.

The full-sample test serves a different purpose: it checks whether the baseline transformation remains defensible over the complete dissertation sample.

### Defense sentence

> The initial-window decision prevents look-ahead. The full-sample test answers the jury's stationarity question, while the alternative transformation becomes a robustness check if the two samples imply different conclusions.

### Status

**Literature-supported forecasting logic plus a necessary no-look-ahead design rule.**

---

## 3.3 Log growth and annualized percentage transformations

### Methodological choice

Use log differences for GDP, CPI, industrial production, and M2, with annualizing factors 400 for quarterly GDP and 1200 for monthly series.

### Academic and logical basis

Log changes are standard in empirical macroeconomic forecasting when the object of interest is growth or inflation. Large macroeconomic forecasting studies such as Marcellino, Stock, and Watson (2006), Stock and Watson (2007), and Teräsvirta, van Dijk, and Medeiros (2005) model transformed macroeconomic growth/inflation series rather than mechanically forecasting trending price/output levels.

The factors 400 and 1200 only change the unit in which the one-period log change is reported. They do not create a different stochastic process.

### Defense sentence

> We model economically interpretable growth and inflation rates rather than trending levels. Annualization is a reporting scale, not a source of predictive content.

### Status

**Strong macroeconomic convention plus straightforward mathematical logic.**

---

## 3.4 BIC for parsimonious lag/order selection

### Methodological choice

Use BIC as the primary information criterion, followed by a residual-whiteness check.

### Academic support

**Schwarz (1978)** derives the criterion now commonly called BIC for selecting among models of different dimensions.

Macroeconomic forecasting studies, including Marcellino, Stock, and Watson (2006), explicitly compare data-dependent AR specifications selected by AIC or BIC.

The thesis favors BIC because the nonlinear stage already adds parameters and the jury has raised concerns about long CPI lags and unstable nonlinear fits. A stronger complexity penalty is therefore coherent with the research problem.

### Defense sentence

> BIC is used to keep the benchmark disciplined and to reduce unnecessary parameterization before nonlinear complexity is introduced. Residual whiteness is then checked because a parsimonious model is not useful if it leaves systematic serial dependence.

### Status

**Strong literature support.**

### What is not claimed

The exact grids `p=1,...,12` monthly, `p=1,...,4` quarterly, and the finite ARMA grids are **transparent search bounds**, not values dictated by theory. They are chosen to cover economically plausible short-run dynamics without creating an unbounded specification search.

---

## 3.5 AR as the primary classical benchmark

### Methodological choice

Retain a parsimonious AR model as the primary benchmark.

### Academic support

Linear autoregressions are standard macroeconomic forecasting benchmarks. Teräsvirta, van Dijk, and Medeiros (2005) explicitly compare STAR forecasts with linear AR forecasts across 47 monthly G7 macroeconomic series. Marcellino, Stock, and Watson (2006) conduct a large macroeconomic forecasting exercise built around AR and VAR forecasts.

### Defense sentence

> The AR model is not a straw man. It is the cleanest own-history linear benchmark and makes the incremental value of state dependence directly measurable.

### Status

**Strong literature support.**

---

## 3.6 ARMA as a stronger classical benchmark

### Methodological choice

Add ARMA to the main comparison so nonlinear models do not win simply because the linear benchmark omits moving-average dynamics.

### Academic and logical basis

ARMA models are foundational time-series models, and Stock and Watson (2007) show that U.S. inflation dynamics can be represented by an integrated moving-average process with time-varying features. ARMA is therefore a legitimate stronger classical comparator for macroeconomic point forecasting.

### Defense sentence

> AR is the transparent baseline; ARMA is a stronger classical alternative. If a nonlinear gain disappears once ordinary linear serial-correlation dynamics are modeled more flexibly, the nonlinear interpretation should be weakened.

### Status

**Strong time-series literature support and direct logical relevance to the thesis claim.**

---

## 3.7 ARCH/GARCH as conditional-variance diagnostics, not automatic mean-forecast rivals

### Methodological choice

Use ARCH-LM and, when indicated, a GARCH(1,1) diagnostic layer. Do not automatically place GARCH in the point-forecast horse race.

### Academic support

**Engle (1982)** introduced ARCH to model conditional heteroskedasticity. **Bollerslev (1986)** generalized this to GARCH by allowing lagged conditional variances.

These models primarily enrich the conditional variance equation. That is not the same scientific object as adding a different conditional-mean mechanism.

### Defense sentence

> We address ARCH/GARCH because the advisor asked for classical alternatives and because forecast uncertainty can be time-varying. But we do not pretend that a variance model is automatically a distinct mean-forecast model.

### Status

**Strong literature support.**

---

## 3.8 Excluding polynomial trend models from the main horse race

### Methodological choice

Do not include deterministic polynomial trend extrapolation as a core competitor unless the stationarity stage leaves a retained deterministic trend that requires it.

### Basis

This is primarily a **logical scope decision**, not a claim that polynomial forecasting is invalid.

The principal targets are transformed growth, inflation, unemployment/rate representations, and other dynamic stationary objects. The research question concerns autoregressive and state-dependent dynamics under instability, not fitting deterministic long-run polynomial curves.

### Defense sentence

> Polynomial trends answer a different forecasting question. Once the targets are represented as stationary macroeconomic growth/rate processes, deterministic polynomial extrapolation does not provide a like-for-like dynamic benchmark. If the stationarity evidence indicates a remaining deterministic trend, we would revisit the exclusion.

### Status

**Logic-supported design choice.**

### Audit decision

**Retained**, because it has a clear statistical scope justification. It is not presented as literature-mandated.

---

## 3.9 Testing nonlinearity before interpreting nonlinear models

### Methodological choice

Use a general Tsay test plus the Luukkonen-Saikkonen-Teräsvirta / Teräsvirta STAR testing and specification sequence.

### Academic support

**Tsay (1986)** develops formal tests of nonlinearity for stationary time series.

**Luukkonen, Saikkonen, and Teräsvirta (1988)** develop tests of linearity against STAR alternatives.

**Teräsvirta (1994)** gives an integrated procedure for STAR specification, including testing linearity, selecting the delay parameter, and choosing between LSTAR and ESTAR.

### Defense sentence

> We do not infer nonlinearity merely because a nonlinear model can be fitted. We first test whether linear autoregressive dynamics are rejected and then use the established STAR specification sequence before interpreting thresholds or smooth transitions.

### Status

**Very strong literature support.**

---

## 3.10 STAR as the smooth state-dependence model

### Methodological choice

Use STAR to represent gradual transitions and select LSTAR versus ESTAR through the Teräsvirta specification procedure.

### Academic support

Teräsvirta (1994) provides the core specification, estimation, and evaluation framework.

Teräsvirta, van Dijk, and Medeiros (2005) compare linear AR and STAR forecasts for 47 monthly macroeconomic variables from the G7 and conclude that careful nonlinear specification is crucial. Their results also show why nonlinear superiority should be tested rather than assumed.

### Defense sentence

> STAR is included because the economic transition between states need not be instantaneous. It offers a well-established way to test smooth state dependence against a linear benchmark.

### Status

**Strong Q1 forecasting/statistical literature support.**

---

## 3.11 Markov-switching AR as the discrete-state model

### Methodological choice

Use a parsimonious two-state Hamilton-style MSAR with regime-dependent mean and common AR dynamics as the baseline discrete-state nonlinear model.

### Academic support

**Hamilton (1989)** models occasional discrete shifts using a latent Markov state and applies the framework to the U.S. business cycle. The paper explicitly links recurrent regime shifts to recession dynamics and forecasting.

The simplified baseline deliberately stays close to that canonical logic instead of allowing every AR coefficient and variance to switch at once.

### Defense sentence

> MSAR is included because recessions and expansions can be represented as latent recurring states. The baseline is intentionally parsimonious because the jury's concern is credible regime identification, not maximal parameter switching.

### Status

**Very strong economics literature support.**

---

## 3.12 Why the thesis does not use a naive one-regime versus two-regime chi-square LR test

### Methodological choice

Do not report a conventional chi-square likelihood-ratio p-value for one versus two Markov regimes. Do not use the earlier proposed simple parametric-bootstrap LR procedure.

### Academic support

**Cho and White (2007)** show that regime-switching tests are nonstandard because nuisance parameters can lie on boundaries or be identified only under the alternative.

**Qu and Zhuo (2021)** establish likelihood-ratio theory for Markov regime switching and emphasize unidentified nuisance parameters, local optima, recursively defined probabilities, and the possibility that some bootstrap procedures are inconsistent.

### Defense sentence

> A conventional LR test would give the appearance of rigor while using the wrong reference theory. We therefore avoid a naive p-value and judge the predeclared MSAR through convergence, regime occupancy, transition behavior, adequacy, forecast performance, and K=3 robustness. We also explicitly limit structural regime claims.

### Status

**Strong top-journal support for the exclusion.**

---

## 3.13 K=2 baseline and K=3 robustness

### Methodological choice

Use two regimes as the interpretable baseline and make three regimes a mandatory robustness exercise.

### Academic and logical basis

Hamilton's classic business-cycle application establishes the relevance of a low-dimensional latent-state representation. The jury specifically requested a three-regime attempt.

There is no universal theorem that says a macroeconomic forecasting problem must contain exactly two or three regimes. Regime number is therefore an empirical specification issue.

### Defense sentence

> Two regimes provide the parsimonious baseline that maps naturally to low/high or expansion/recession dynamics. We then estimate three regimes because the jury correctly asks whether the two-state representation is imposed too strongly. K=3 is retained only if the additional state is populated, stable, distinct, and useful for forecasting.

### Status

**Literature-supported baseline plus jury-mandated robustness.**

---

## 3.14 Why MSSTAR is removed from the core design

### Methodological choice

Remove MSSTAR from the baseline comparison.

### Basis

This is a **parsimony and identification decision**, informed by the nonlinear forecasting literature rather than a claim that MSSTAR is invalid.

Teräsvirta, van Dijk, and Medeiros (2005) show that nonlinear macroeconomic forecasting performance depends strongly on careful specification, and that nonlinear models do not automatically dominate linear ones.

The revised thesis already compares:

- linear own-history dynamics;
- richer linear ARMA dynamics;
- discrete latent state dependence;
- smooth transition state dependence.

Combining discrete and smooth mechanisms before either simple nonlinear mechanism earns empirical support would increase estimation risk and computational burden without answering a distinct primary research question.

### Defense sentence

> MSSTAR is not removed because hybrid models are illegitimate. It is removed because the revised thesis asks a cleaner identification question: does discrete or smooth state dependence add robust forecast value beyond strong classical benchmarks? A hybrid layer would make that answer harder to interpret.

### Status

**Strong logical justification supported by the nonlinear-specification literature.**

---

## 3.15 In-sample adequacy before forecast interpretation

### Methodological choice

Report fit and diagnostic adequacy before presenting out-of-sample rankings, while treating out-of-sample evidence as the decisive forecast test.

### Academic support

Teräsvirta, van Dijk, and Medeiros (2005) explicitly note that careful nonlinear model specification and evaluation matter and discuss the potential cost of insufficient in-sample model evaluation.

Forecasting literature simultaneously distinguishes in-sample fit from genuine out-of-sample predictive performance.

### Defense sentence

> A model that does not credibly represent the observed process should not receive an economic regime interpretation. But good fit is only a prerequisite; it does not establish forecast superiority.

### Status

**Strong literature support and direct response to Prof. Verne.**

---

## 3.16 Removing MAPE

### Methodological choice

Do not use MAPE for targets such as inflation and growth that can be zero, near zero, or negative.

### Academic support

**Hyndman and Koehler (2006)** show that several commonly used forecast-accuracy measures can become degenerate in commonly occurring situations.

For macroeconomic rates near zero, percentage denominators can make MAPE unstable or misleading.

### Defense sentence

> RMSE and MAE remain well defined when inflation or growth crosses zero; MAPE does not. Removing MAPE improves interpretability rather than deleting unfavorable evidence.

### Status

**Strong forecasting-literature support.**

---

## 3.17 Rolling pseudo-out-of-sample evaluation

### Methodological choice

Use fixed-length rolling windows and re-estimate model parameters at every forecast origin.

### Academic support

**West (1996)** develops inference for predictive ability with out-of-sample predictions from estimated models.

**Giacomini and White (2006)** explicitly develop predictive-ability tests for realistic, potentially misspecified forecasting models and use fixed estimation windows.

**Pesaran and Timmermann (2007)** analyze estimation-window selection in the presence of structural breaks and show the bias-versus-variance trade-off in using older observations.

**Rossi and Inoue (2012)** show that forecast inference can be sensitive to window-size choice and develop procedures robust to the window dimension.

**Teräsvirta, van Dijk, and Medeiros (2005)** describe recursive forecast exercises in which model parameters are re-estimated as new observations become available.

### Defense sentence

> Rolling windows are aligned with the thesis's instability premise because they allow old observations to drop out, while every-origin re-estimation preserves the pseudo-real-time chronology. We reduce computation through simpler models and code engineering, not by freezing parameters between forecast dates.

### Status

**Very strong literature support.**

---

## 3.18 Exact rolling-window lengths: 240 monthly and 120 quarterly observations

### Methodological choice

Retain 240 monthly observations and 120 quarterly observations.

### Academic evidence and limitation

The literature strongly supports the **importance** of window choice but does not supply a universal optimal length.

Pesaran and Timmermann (2007) explicitly characterize window selection as a bias-variance problem under breaks. Rossi and Inoue (2012) show that conclusions can depend on window size.

Therefore 240/120 cannot honestly be presented as theoretically optimal.

The rationale is:

- 240 months = 20 years, long enough to estimate nonlinear models with meaningful regime occupancy while still allowing structural adaptation;
- 120 quarters = 30 years, needed because quarterly data are much sparser and the nonlinear models require sufficient observations;
- both are fixed ex ante rather than chosen after seeing which window produces the preferred result.

### Defense sentence

> There is no universally correct rolling-window length under structural change. We predeclare 240 monthly and 120 quarterly observations as a bias-variance compromise that preserves enough observations for nonlinear estimation. We do not claim these values are optimal.

### Status

**Logic-supported convention informed by strong window-selection literature.**

### Important limitation

If the jury specifically asks whether the ranking is robust to window size, the current design does not claim to answer that question. The thesis must say so rather than imply robustness that was not tested.

---

## 3.19 Fixing discrete specification choices but re-estimating parameters every origin

### Methodological choice

Choose lag/order and STAR type/delay using the initial training sample and keep those discrete choices fixed in the baseline pseudo-out-of-sample exercise. Re-estimate continuous parameters every forecast origin.

### Academic and logical basis

Teräsvirta, van Dijk, and Medeiros (2005) explain the computational burden of repeatedly specifying and estimating nonlinear macroeconomic models. They discuss designs where specifications are held fixed for intervals while parameters are repeatedly re-estimated.

Fixing the discrete baseline specification has two advantages:

1. it prevents future observations from repeatedly changing the definition of the model being compared;
2. it makes the forecast horse race interpretable because AR, ARMA, MSAR, and STAR retain stable identities.

### Defense sentence

> We separate model selection from parameter updating. The model definition is chosen from the training information set, while its parameters are re-estimated as information arrives. This avoids repeated data-mining while preserving pseudo-out-of-sample updating.

### Status

**Literature-informed and strongly logic-supported.**

---

## 3.20 Primary h=1 and longer-horizon robustness

### Methodological choice

Use h=1 as the primary forecast horizon, then monthly h=3,6,12 and quarterly h=2,4 as robustness.

### Academic support

**Marcellino, Stock, and Watson (2006)** compare macroeconomic forecasts over multiple horizons and show that forecasting method performance can change with horizon.

Teräsvirta, van Dijk, and Medeiros (2005) also examine nonlinear macroeconomic forecasting at multiple horizons.

### Defense sentence

> One-step forecasting gives the cleanest baseline, but the President is correct that nonlinear propagation can matter more at longer horizons. We therefore treat model ranking as horizon-dependent rather than universal.

### Status

**Strong literature support and direct jury response.**

---

## 3.21 Iterated multi-step forecasts

### Methodological choice

Generate longer-horizon forecasts by iterating the one-step dynamic specification.

### Academic support

Marcellino, Stock, and Watson (2006) compare direct and iterated multi-step AR forecasts for 170 U.S. macroeconomic series. They find that iterated forecasts typically perform well, particularly when the one-step model is adequately specified, while also emphasizing that direct versus iterated performance is an empirical question.

### Defense sentence

> The thesis estimates one coherent dynamic model and asks how its state dependence propagates forward. Iterated forecasts therefore preserve the model's estimated dynamics rather than estimating a new equation for every horizon.

### Status

**Strong literature support.**

---

## 3.22 RMSE and MAE as primary forecast losses

### Methodological choice

Report RMSE and MAE.

### Academic basis

Diebold and Mariano (1995) explicitly allow forecast comparison under general loss functions, not only quadratic loss.

Using both squared-error and absolute-error criteria prevents the conclusion from depending on one loss function. RMSE penalizes large misses more strongly; MAE is less dominated by extreme errors.

### Defense sentence

> A nonlinear model is not called superior because it wins under one arbitrary loss function. We report both squared-error-sensitive and absolute-error-sensitive performance.

### Status

**Strong literature support.**

---

## 3.23 Out-of-sample R²

### Methodological choice

Report OOS R² relative to AR as a descriptive relative-performance measure.

### Basis

This statistic is an algebraic rescaling of relative squared forecast loss:

`R²_OOS = 1 - SSE_model / SSE_AR`.

It does not provide a separate inferential test and is not used alone to claim statistical superiority.

### Defense sentence

> OOS R² is included because it translates the squared-error gain into an intuitive relative benchmark measure. Formal inference comes from the forecast-comparison tests, not from the sign of OOS R² alone.

### Status

**Logic-supported descriptive statistic.**

---

## 3.24 Diebold-Mariano with Harvey-Leybourne-Newbold finite-sample correction

### Methodological choice

Retain DM for pairwise point-forecast comparison and use the Harvey-Leybourne-Newbold small-sample modification.

### Academic support

**Diebold and Mariano (1995)** propose tests of equal predictive accuracy under broad loss functions and allow forecast errors to be non-Gaussian and serially/contemporaneously correlated.

**Harvey, Leybourne, and Newbold (1997)** study finite-sample shortcomings and propose modifications for practical forecast comparison.

### Defense sentence

> DM remains because the thesis asks whether two point forecasts have equal predictive accuracy. The finite-sample correction addresses the reviewer's concern that an old unmodified DM implementation is not enough.

### Status

**Strong Q1 forecasting/econometrics support.**

---

## 3.25 Giacomini-White for recession and turning-point dependence

### Methodological choice

Use conditional predictive ability regression to test whether relative forecast performance changes with recession and turning-point indicators.

### Academic support

**Giacomini and White (2006)** develop a conditional predictive-ability framework designed for realistic forecasting models that may be misspecified.

This is a direct match to the thesis question: not only “which model wins on average?” but “does the relative loss change with the economic state?”

### Defense sentence

> Recession and turning-point comparisons are conditional forecast questions. Giacomini-White is therefore more appropriate than attaching an arbitrary confidence interval to small state-specific subsamples.

### Status

**Very strong top-journal support.**

---

## 3.26 Model Confidence Set

### Methodological choice

Use the Hansen-Lunde-Nason Model Confidence Set in addition to pairwise tests.

### Academic support

**Hansen, Lunde, and Nason (2011)** develop the MCS as a set of models that contains the best model at a chosen confidence level. It explicitly recognizes that the data may not be informative enough to identify a unique winner.

### Defense sentence

> With four competing model classes, forcing a unique winner from a table of pairwise p-values would overstate precision. MCS lets the evidence say that several models are statistically indistinguishable when that is what the sample supports.

### Status

**Very strong top-journal support.**

---

## 3.27 Why Clark-West is not a baseline test

### Methodological choice

Do not mechanically add Clark-West to AR versus MSAR/STAR comparisons.

### Academic support

**Clark and West (2007)** explicitly develop their adjustment for comparisons in which a larger forecasting model **nests** the parsimonious null model.

The thesis's main AR-versus-MSAR and AR-versus-STAR comparisons are not the simple nested linear setting for which the test was designed.

### Defense sentence

> We did not omit Clark-West because it is unimportant. We omit it from the baseline because its central justification is nested-model forecast comparison, whereas the main nonlinear models are structurally different model classes.

### Status

**Strong literature-based exclusion.**

---

## 3.28 Why Amisano-Giacomini is not a baseline test

### Methodological choice

Do not use Amisano-Giacomini unless the thesis is redesigned to compare predictive densities.

### Academic support

**Amisano and Giacomini (2007)** explicitly propose tests for comparing **density forecasts** using weighted likelihood scoring.

The revised thesis's primary object is point forecast accuracy.

### Defense sentence

> Adding a density-forecast test without constructing and validating comparable predictive densities would be methodologically decorative rather than rigorous.

### Status

**Strong literature-based exclusion.**

---

## 3.29 Monthly VAR as the focused multivariate robustness model

### Methodological choice

Add a parsimonious VAR for the common monthly system as a robustness check, not as a second dissertation.

### Academic support

**Sims (1980)** is the foundational macroeconomic VAR reference.

The jury's objection is that single-equation own-history dynamics cannot reveal whether predictive information is transmitted through other macro variables. A VAR directly addresses that alternative explanation.

### Defense sentence

> The VAR is not added to maximize model count. It tests the specific omitted-information criticism: does the apparent value of nonlinear own-history dynamics survive once linked macroeconomic variables can help predict one another?

### Status

**Very strong economics literature support and direct jury relevance.**

---

## 3.30 Why GDP is not mechanically interpolated into the monthly VAR

### Methodological choice

Keep GDP at quarterly frequency rather than creating artificial monthly GDP observations.

### Basis

Interpolation would create model-generated information that was not observed monthly.

A genuine mixed-frequency design requires a dedicated framework and information-release structure.

### Defense sentence

> We prefer an honest common-frequency VAR to pseudo-monthly GDP generated by interpolation. If monthly and quarterly information are to be combined formally, that becomes a mixed-frequency/nowcasting problem and should be modeled as such.

### Status

**Strong logic, reinforced by the mixed-frequency literature.**

---

## 3.31 Why full nowcasting is outside the core design

### Methodological choice

Address nowcasting in the literature/scope discussion but do not add a full nowcasting model.

### Academic support

**Giannone, Reichlin, and Small (2008)** model nowcasting using intra-monthly data releases, large data sets, unsynchronized publication dates, and a jagged-edge real-time information set.

That is materially different from comparing model forms on aligned monthly/quarterly target histories.

### Defense sentence

> Nowcasting would not be one more robustness model. It would change the information set, data architecture, publication chronology, and research question. We therefore delimit it explicitly instead of implementing an incomplete version and calling it nowcasting.

### Status

**Strong Q1 macroeconomic literature support for the boundary.**

---

## 3.32 Recession, expansion, peak, and trough evaluation

### Methodological choice

Use NBER/FRED recession chronology only for ex post evaluation of forecast errors, not as a contemporaneous model regressor.

### Academic and logical basis

Hamilton (1989) directly connects regime switching to recurring business-cycle recessions.

Using the official chronology to classify realized forecast targets answers Prof. Verne's policy timing question while preventing look-ahead leakage into the forecast model.

### Defense sentence

> The recession chronology is used to ask where errors occurred, not to give the model information that was unavailable when the forecast was made.

### Status

**Strong literature support plus no-look-ahead logic.**

---

## 3.33 Model-failure rules

### Methodological choice

Distinguish adequate, fragile, and failed estimation, preserve failure output, and prohibit silent fallback to a different model.

### Literature and logical basis

Teräsvirta, van Dijk, and Medeiros (2005) explicitly discuss the need to detect implausible/explosive nonlinear forecasts and emphasize careful nonlinear model construction.

The jury also specifically criticized extreme Markov transition probabilities and visually destructive forecasts.

### Defense sentence

> A nonlinear failure is part of the evidence about whether complexity is usable. Silently changing the model after a failure would make the comparison irreproducible and could bias the conclusion in favor of the nonlinear model.

### Status

**Literature-supported research-integrity rule.**

### Operational warning thresholds

The following are **not theoretical critical values**:

- occupancy below 5%;
- fewer than 20 effective regime observations;
- transition probability ≤0.005 or ≥0.995;
- STAR threshold outside the 5th–95th percentile;
- STAR smoothness at an optimization bound.

They are transparent warning flags for closer inspection.

### Defense sentence

> These cutoffs do not determine statistical significance. They are operational audit flags. A model is not automatically rejected simply because a warning threshold is crossed.

### Status

**Logic-based audit convention.**

---

## 3.34 Why the United States is the empirical case

### Methodological choice

Use the United States as the single-country empirical environment for the core dissertation.

### Academic and economic support

Several of the methodological references that motivate this thesis are themselves grounded in U.S. macroeconomic forecasting and business-cycle applications.

**Hamilton (1989)** develops the canonical Markov-switching business-cycle application using U.S. output dynamics.

**Stock and Watson (1999, 2007)** study U.S. inflation forecasting and changing inflation dynamics.

**Marcellino, Stock, and Watson (2006)** use a large set of U.S. macroeconomic time series to study multi-step forecasting.

These precedents do not prove that the United States is the only valid country. They show that the U.S. provides a well-established empirical environment for exactly the kind of macroeconomic forecasting questions studied here.

The additional design rationale is:

- repeated postwar expansions and recessions;
- long monthly and quarterly official series;
- a clear Federal Reserve policy institution;
- stable machine-readable data identifiers;
- ALFRED historical-vintage reconstruction;
- no need to introduce cross-country measurement and institutional heterogeneity before the model-form question has been answered cleanly.

### Defense sentence

> The United States is not selected merely because its data are convenient. It provides the combination of macroeconomic relevance, repeated regime changes, long official histories, and historical-vintage reproducibility required by a state-dependent forecasting study. The model ranking remains U.S.-specific, while the research design can be replicated internationally.

### Status

**Strong empirical-precedent support plus economic and reproducibility logic.**

---

## 3.35 Why these macroeconomic series and not an unrestricted list

### Methodological choice

Use six core forecast targets:

- real GDP;
- CPI inflation;
- unemployment;
- industrial production;
- federal funds rate;
- M2 growth;

with USREC used only for ex post business-cycle classification.

### Academic and economic support

The selection follows the economic mechanisms retained in Part 4 rather than an unrestricted data-mining search.

**Stock and Watson (1999)** study U.S. inflation forecasting using unemployment, broader real-activity indicators, interest rates, money, and commodity prices. Their results demonstrate that inflation forecasting is naturally connected to labour-market slack and real activity rather than being an isolated univariate question.

**Bernanke, Boivin, and Eliasz (2005)** emphasize that monetary-policy analysis involves a broad information set and that choosing a specific series to represent a general concept such as real activity is itself a substantive empirical decision. This supports the thesis's explicit distinction between quarterly GDP as comprehensive real output and monthly industrial production as a higher-frequency cyclical activity measure.

The final target set maps one-to-one onto the theory retained at Prof. Verne's request:

- Fisher: inflation and interest rates;
- Phillips/Phelps: inflation and unemployment;
- Okun: output/activity and unemployment;
- monetarist/money-supply discussion: M2;
- monetary-policy implementation: federal funds rate;
- business-cycle timing: GDP/INDPRO/UNRATE plus external recession chronology.

### Defense sentence

> We did not begin with all downloadable FRED series and search for variables that make nonlinear models look good. We began with the economic mechanisms in Part 4 and selected the minimum official series needed to observe those concepts.

### Status

**Strong economic-theory and macroeconometric support.**

---

## 3.36 Why CPI is the core inflation target rather than PCEPI

### Methodological choice

Keep CPIAUCSL as the core inflation target while explicitly acknowledging PCEPI as the Federal Reserve's preferred inflation measure.

### Official evidence and logic

FRED records CPIAUCSL from January 1947, while PCEPI begins in January 1959. PCEPI is explicitly described by FRED/BEA as the Federal Reserve's preferred inflation measure.

The thesis chooses CPI because:

1. it gives twelve additional years of postwar monthly history;
2. it preserves a longer sequence of inflation regimes and business cycles;
3. the thesis compares model forms across macroeconomic aggregates, not competing inflation indexes;
4. adding both CPI and PCE as core targets would give inflation disproportionate weight relative to labour, output, money, and policy rates.

### Defense sentence

> PCE is highly relevant for Federal Reserve policy and is acknowledged as such. CPI is retained as the core forecasting target because it provides the longer postwar sample required for the cross-regime comparison and avoids duplicating one macroeconomic concept in the core horse race.

### Status

**Official-data and logical design justification.**

---

## 3.37 Why GDP and industrial production are both retained

### Methodological choice

Keep quarterly real GDP and monthly industrial production.

### Official and economic support

GDP is the comprehensive real-output aggregate.

FRED's documentation for INDPRO states that industrial production and related sectors account for a large share of variation in national output over the business cycle. INDPRO therefore supplies a monthly cyclical activity measure when GDP itself is only observed quarterly.

### Defense sentence

> GDP and industrial production do not duplicate the same empirical role. GDP provides comprehensive quarterly growth; industrial production provides monthly real-activity information needed for turning-point and recession analysis without fabricating monthly GDP.

### Status

**Official-measurement and frequency-based logic.**

---

## 3.38 Why the sample begins in the postwar period

### Methodological choice

Use the earliest defensible postwar observation for each univariate target and truncate INDPRO to January 1947.

### Economic and statistical basis

This is an ex ante economic comparability rule.

The thesis studies modern U.S. macroeconomic forecasting and policy. Extending industrial production back through the Great Depression and World War II would introduce monetary, fiscal, production-control, and institutional regimes that are absent from the other target histories.

At the same time, using the earliest postwar observation available for each series maximizes the number of recessions, expansions, and forecast observations available for nonlinear estimation.

### Defense sentence

> The start date is not chosen around a favorable result. It is the earliest coherent postwar U.S. policy sample supported by the official series, with INDPRO deliberately truncated so that one variable does not import prewar and wartime regimes that the other targets cannot share.

### Status

**Economic and logical design justification.**

---

## 3.39 Why the sample ends at 2026M8 / 2026Q2

### Methodological choice

Freeze the information set on 5 October 2026.

Use:

- August 2026 as the common monthly endpoint;
- 2026Q2 as the GDP endpoint.

### Official evidence and logic

As of the frozen information date, UNRATE already contained September 2026, while CPIAUCSL, INDPRO, FEDFUNDS, and M2SL were all available through August 2026. Therefore August is the latest month jointly observable across the monthly core targets.

Real GDP for 2026Q2 was available, while the next quarterly release was scheduled later in October.

### Defense sentence

> The terminal date is determined mechanically by what was jointly observable on the predeclared vintage date. We do not stop the sample at a recession, policy event, or point that improves forecast performance.

### Status

**Official release-calendar and no-selection-bias logic.**

---

## 3.40 Why the data are frozen and why ALFRED vintage retrieval matters

### Methodological choice

Build one immutable thesis snapshot corresponding to 2026-10-05, save raw files and hashes, and make normal reruns read only those files.

### Official support

The Federal Reserve Bank of St. Louis explicitly distinguishes FRED's current historical data from ALFRED's real-time historical vintages. Its API documentation states that `vintage_dates` can retrieve observations as they existed on a specified historical date.

This matters because GDP, industrial production, monetary aggregates, and price indexes can be revised after initial publication.

### Defense sentence

> A dissertation result must not change simply because the statistical agency revises history after submission. We therefore freeze the exact vintage used for the thesis and keep ALFRED as an independent web-based reconstruction route.

### Status

**Strong official reproducibility justification.**

---

## 3.41 Why raw levels are retrieved and transformations are computed locally

### Methodological choice

Download raw official series values, freeze them, and compute every transformation in the thesis code.

### Logical basis

If the remote provider performs transformations, a future change in provider defaults, aggregation conventions, or historical values can make the transformation harder to audit.

Local transformation gives one explicit formula and one immutable input.

### Defense sentence

> We separate data acquisition from statistical transformation. The raw official observations are frozen first, then every growth rate and difference is produced transparently by the thesis code.

### Status

**Strong reproducibility logic.**

---

# 4. Choices for which no unique Q1 paper dictates the exact number

Several details are necessary to implement a reproducible dissertation but are not uniquely determined by high-level literature.

They are retained only because they are transparent, predeclared, and logically connected to the design.

| Choice | Why it is retained | What must NOT be claimed |
|---|---|---|
| 240 monthly rolling observations | 20-year adaptive window with enough observations for nonlinear estimation | Not “the optimal window” |
| 120 quarterly rolling observations | Quarterly models need a larger calendar span to supply enough observations | Not “the optimal quarterly window” |
| Monthly AR maximum lag 12 | Covers up to one year of monthly dynamics and directly permits the CPI p=12 challenge | Not “the theoretically correct maximum” |
| Quarterly AR maximum lag 4 | Covers up to one year of quarterly own-history dynamics | Not “the theoretically correct maximum” |
| ARMA finite grid | Keeps specification search bounded and reproducible | Not “the unique ARMA search space” |
| MS warning thresholds | Make degenerate regimes auditable | Not statistical critical values |
| STAR optimization bounds | Necessary numerical constraints | Not economically meaningful thresholds |
| Frozen endpoint | Reproducibility requirement | Not an economically privileged terminal date |
| USREC ±3-month / ±1-quarter turning window | Transparent operational definition around peaks/troughs | Not a universal business-cycle theorem |

If the final empirical conclusion turns out to be highly sensitive to one of these conventions, the Part 8 report must classify the relevant claim as **qualified** rather than hide the sensitivity.

---

# 5. Choices removed or changed because this audit did not support them strongly enough

## 5.1 Scheduled re-estimation every three months / four quarters

**Previous proposal:** update model parameters only periodically to reduce runtime.

**Audit result:** removed as the baseline.

**Reason:** the literature gives much cleaner precedent for pseudo-out-of-sample re-estimation as information arrives. Runtime is an implementation problem, not a sufficient reason to weaken the forecast experiment.

## 5.2 Simple parametric-bootstrap LR test for AR versus two-state MSAR

**Previous proposal:** create a bootstrap p-value for one versus two regimes.

**Audit result:** removed.

**Reason:** regime-switching tests have nonstandard nuisance/boundary problems, and Qu and Zhuo (2021) explicitly show why some bootstrap procedures can be inconsistent. A casual bootstrap implementation would not be defense-ready.

## 5.3 Ad hoc state-specific block-bootstrap confidence intervals

**Previous proposal:** use fixed monthly/quarterly block lengths for loss differences.

**Audit result:** replaced by Giacomini-White conditional predictive ability.

**Reason:** the exact block lengths had no strong thesis-specific academic justification, while Giacomini-White directly addresses conditional predictive performance.

## 5.4 Switching every MSAR coefficient and variance in the baseline

**Previous proposal:** fully switching intercept, AR slopes, and variance.

**Audit result:** simplified.

**Reason:** the previous thesis already produced unstable/degenerate regime estimates. A Hamilton-style mean-switching baseline has a much clearer economic precedent and reduces identification burden.

## 5.5 Holm correction across STAR delay candidates

**Previous proposal:** treat the delay scan as a generic family of multiple tests and impose Holm correction.

**Audit result:** removed.

**Reason:** Teräsvirta (1994) provides a purpose-built STAR specification sequence for linearity, delay, and transition-form selection. The thesis should follow the established econometric specification procedure rather than graft on an unrelated generic correction without a specific literature basis.

---

# 6. Defense-ready answers to likely jury questions

## “Why not just use the model with the lowest in-sample AIC?”

Because the thesis asks a **forecasting** question. In-sample information criteria help specification, but genuine predictive value must be evaluated out of sample. West (1996), Diebold and Mariano (1995), and Giacomini and White (2006) provide the inferential forecasting framework.

## “Why BIC rather than AIC?”

BIC has a stronger complexity penalty and is consistent with the thesis's objective of giving simple benchmarks a fair chance before nonlinear parameters are added. Schwarz (1978) provides the formal criterion. We then require residual adequacy so parsimony does not come at the cost of obvious misspecification.

## “Why test nonlinearity before fitting STAR?”

Because fitting a nonlinear function does not prove the data require nonlinearity. Tsay (1986), Luukkonen et al. (1988), and Teräsvirta (1994) provide formal pre-estimation procedures.

## “Why estimate STAR even if linearity is not rejected?”

Because the forecast comparison is predeclared. Dropping competitors after seeing a specification-test result can create a selected horse race. Failure to reject limits **structural interpretation** of STAR; it does not make its forecast errors scientifically uninteresting.

## “Why no formal p-value saying two Markov regimes are better than one?”

Because this is not a regular LR problem. Cho and White (2007) and Qu and Zhuo (2021) document nuisance parameters, boundary issues, and nonstandard asymptotics. We prefer an honest limitation to an incorrectly calibrated test.

## “Why two regimes?”

It is the parsimonious business-cycle baseline motivated by Hamilton (1989). The President's requested K=3 model is then estimated as robustness.

## “Why not keep MSSTAR?”

Because it would combine two mechanisms before discrete and smooth state dependence separately demonstrate value. The revised thesis prioritizes identification and interpretability over maximum model complexity.

## “Why rolling windows?”

Because the thesis is about instability. Pesaran and Timmermann (2007) show the forecast-window bias-variance issue in the presence of breaks. Rolling windows allow stale pre-break observations to leave the estimation sample.

## “Why exactly 20 years monthly?”

There is no universally optimal length. It is a predeclared compromise between adaptation and enough observations for nonlinear estimation. The literature itself shows that window choice is an empirical trade-off. We therefore do not claim 240 months is theoretically optimal.

## “Why re-estimate every period if it is computationally expensive?”

Because the statistical experiment should not be weakened merely to save runtime. Pseudo-out-of-sample forecasting is designed to recreate sequential information sets. We solve runtime through simpler model architecture and efficient code.

## “Why multiple horizons?”

Because model rankings can be horizon-dependent. Marcellino et al. (2006) provide large-scale macroeconomic evidence on multi-horizon forecasting, and the President specifically questioned h=1.

## “Why Giacomini-White?”

Because the thesis asks whether relative model performance changes **conditional on recession and turning-point states**. That is precisely a conditional predictive-ability question.

## “Why the Model Confidence Set?”

Because with several models the data may not statistically identify one unique winner. Hansen et al. (2011) provide a framework that reports the set of models consistent with best performance at a confidence level.

## “Why no Clark-West?”

Because Clark-West is specifically motivated by nested-model forecast comparisons. AR versus MSAR/STAR is not the simple nested setting for which it was designed.

## “Why no Amisano-Giacomini?”

Because it compares predictive **densities**. The core thesis compares point forecasts. Using it without a common density-forecast design would answer a question the thesis did not estimate.

## “Why a VAR?”

Because Fisher/Phillips/Okun logic implies relationships across variables, and the jury correctly notes that a univariate model can miss transmitted information. Sims (1980) gives the canonical multivariate framework. The VAR is a focused robustness check, not a replacement for the core question.

## “Why no nowcasting?”

Because Giannone et al. (2008) show that nowcasting is built around staggered intra-period releases, jagged-edge data, and real-time information updates. Adding it would materially change the information set and research question.

---

# 7. Current-Q1 / Scopus-based journal-quality verification used in this audit

Checked against current SCImago SJR information based on Scopus data.

| Journal | Current status used in audit | Examples used here |
|---|---|---|
| Econometrica | Q1 | Hamilton (1989); West (1996); Giacomini & White (2006); Cho & White (2007); Hansen et al. (2011) |
| Review of Economic Studies | Q1 | Qu & Zhuo (2021) |
| Journal of Econometrics | Q1 | KPSS (1992); Bollerslev (1986); Pesaran & Timmermann (2007); Marcellino et al. (2006); Clark & West (2007) |
| Journal of Business & Economic Statistics | Q1 | Zivot & Andrews (1992); Diebold & Mariano (1995); Amisano & Giacomini (2007); Rossi & Inoue (2012) |
| Journal of the American Statistical Association | Q1 | Dickey & Fuller (1979); Teräsvirta (1994) |
| Biometrika | Q1 | Tsay (1986); Luukkonen et al. (1988) |
| Annals of Statistics | Q1 | Schwarz (1978) |
| International Journal of Forecasting | Q1 | Harvey et al. (1997); Hyndman & Koehler (2006); Teräsvirta et al. (2005) |
| Journal of Monetary Economics | Q1 | Giannone et al. (2008) |
| Journal of Money, Credit and Banking | Q1 | Stock & Watson (2007) |

This table verifies the present quality of the venues. It is not a claim about historical quartile labels in the publication year.

---

# 8. Core references in APA style

Bernanke, B. S., Boivin, J., & Eliasz, P. (2005). Measuring the effects of monetary policy: A factor-augmented vector autoregressive (FAVAR) approach. *The Quarterly Journal of Economics, 120*(1), 387–422. https://doi.org/10.1162/0033553053327452

Stock, J. H., & Watson, M. W. (1999). Forecasting inflation. *Journal of Monetary Economics, 44*(2), 293–335. https://doi.org/10.1016/S0304-3932(99)00027-6

Amisano, G., & Giacomini, R. (2007). Comparing density forecasts via weighted likelihood ratio tests. *Journal of Business & Economic Statistics, 25*(2), 177–190. https://doi.org/10.1198/073500106000000332

Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics, 31*(3), 307–327. https://doi.org/10.1016/0304-4076(86)90063-1

Cho, J. S., & White, H. (2007). Testing for regime switching. *Econometrica, 75*(6), 1671–1720. https://doi.org/10.1111/j.1468-0262.2007.00809.x

Clark, T. E., & West, K. D. (2007). Approximately normal tests for equal predictive accuracy in nested models. *Journal of Econometrics, 138*(1), 291–311. https://doi.org/10.1016/j.jeconom.2006.05.023

Dickey, D. A., & Fuller, W. A. (1979). Distribution of the estimators for autoregressive time series with a unit root. *Journal of the American Statistical Association, 74*(366), 427–431. https://doi.org/10.1080/01621459.1979.10482531

Diebold, F. X., & Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business & Economic Statistics, 13*(3), 253–263. https://doi.org/10.1080/07350015.1995.10524599

Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica, 50*(4), 987–1007. https://doi.org/10.2307/1912773

Giacomini, R., & White, H. (2006). Tests of conditional predictive ability. *Econometrica, 74*(6), 1545–1578. https://doi.org/10.1111/j.1468-0262.2006.00718.x

Giannone, D., Reichlin, L., & Small, D. (2008). Nowcasting: The real-time informational content of macroeconomic data. *Journal of Monetary Economics, 55*(4), 665–676. https://doi.org/10.1016/j.jmoneco.2008.05.010

Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica, 57*(2), 357–384. https://doi.org/10.2307/1912559

Hansen, P. R., Lunde, A., & Nason, J. M. (2011). The model confidence set. *Econometrica, 79*(2), 453–497. https://doi.org/10.3982/ECTA5771

Harvey, D., Leybourne, S., & Newbold, P. (1997). Testing the equality of prediction mean squared errors. *International Journal of Forecasting, 13*(2), 281–291. https://doi.org/10.1016/S0169-2070(96)00719-4

Hyndman, R. J., & Koehler, A. B. (2006). Another look at measures of forecast accuracy. *International Journal of Forecasting, 22*(4), 679–688. https://doi.org/10.1016/j.ijforecast.2006.03.001

Kwiatkowski, D., Phillips, P. C. B., Schmidt, P., & Shin, Y. (1992). Testing the null hypothesis of stationarity against the alternative of a unit root: How sure are we that economic time series have a unit root? *Journal of Econometrics, 54*(1–3), 159–178. https://doi.org/10.1016/0304-4076(92)90104-Y

Luukkonen, R., Saikkonen, P., & Teräsvirta, T. (1988). Testing linearity against smooth transition autoregressive models. *Biometrika, 75*(3), 491–499. https://doi.org/10.1093/biomet/75.3.491

Marcellino, M., Stock, J. H., & Watson, M. W. (2006). A comparison of direct and iterated multistep AR methods for forecasting macroeconomic time series. *Journal of Econometrics, 135*(1–2), 499–526. https://doi.org/10.1016/j.jeconom.2005.07.020

Pesaran, M. H., & Timmermann, A. (2007). Selection of estimation window in the presence of breaks. *Journal of Econometrics, 137*(1), 134–161. https://doi.org/10.1016/j.jeconom.2006.03.010

Qu, Z., & Zhuo, F. (2021). Likelihood ratio-based tests for Markov regime switching. *The Review of Economic Studies, 88*(2), 937–968. https://doi.org/10.1093/restud/rdaa035

Rossi, B., & Inoue, A. (2012). Out-of-sample forecast tests robust to the choice of window size. *Journal of Business & Economic Statistics, 30*(3), 432–453. https://doi.org/10.1080/07350015.2012.693850

Schwarz, G. (1978). Estimating the dimension of a model. *The Annals of Statistics, 6*(2), 461–464. https://doi.org/10.1214/aos/1176344136

Sims, C. A. (1980). Macroeconomics and reality. *Econometrica, 48*(1), 1–48. https://doi.org/10.2307/1912017

Stock, J. H., & Watson, M. W. (2007). Why has U.S. inflation become harder to forecast? *Journal of Money, Credit and Banking, 39*(s1), 3–33. https://doi.org/10.1111/j.1538-4616.2007.00014.x

Teräsvirta, T. (1994). Specification, estimation, and evaluation of smooth transition autoregressive models. *Journal of the American Statistical Association, 89*(425), 208–218. https://doi.org/10.1080/01621459.1994.10476462

Teräsvirta, T., van Dijk, D., & Medeiros, M. C. (2005). Linear models, smooth transition autoregressions, and neural networks for forecasting macroeconomic time series: A re-examination. *International Journal of Forecasting, 21*(4), 755–774. https://doi.org/10.1016/j.ijforecast.2005.04.010

Tsay, R. S. (1986). Nonlinearity tests for time series. *Biometrika, 73*(2), 461–466. https://doi.org/10.1093/biomet/73.2.461

West, K. D. (1996). Asymptotic inference about predictive ability. *Econometrica, 64*(5), 1067–1084. https://doi.org/10.2307/2171956

Zivot, E., & Andrews, D. W. K. (1992). Further evidence on the Great Crash, the oil-price shock, and the unit-root hypothesis. *Journal of Business & Economic Statistics, 10*(3), 251–270. https://doi.org/10.1080/07350015.1992.10509904

---

# 9. Final methodological audit rule

Before Part 5 is marked APPROVED and handed to Claude Code, use this literature file as a defense checklist.

For every line in the final methodology ask:

1. **What research problem does this choice solve?**
2. **Which high-level source supports the method or the principle?**
3. **If no paper dictates the exact implementation, is the choice transparently predeclared and logically defensible?**
4. **Does the thesis avoid presenting an operational convention as a statistical theorem?**
5. **Would changing this choice after seeing the results create researcher discretion or data mining?**
6. **Is the output required to demonstrate the choice visible in Part 5's output specification?**

If the answer to Questions 2 and 3 is “no,” the choice should not remain in the approved methodology.
