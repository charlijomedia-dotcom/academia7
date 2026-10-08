# Part 5: Required empirical outputs specification

**Date:** 5 October 2026  
**Status:** APPROVED AND FROZEN
**Purpose:** Tell Claude Code exactly what tables, figures, diagnostics, manifests, and result files must exist so Part 8 and Part 9 can be written without manually reconstructing evidence.

# 1. Mandatory machine-readable outputs

Every table shown in the thesis must also exist as CSV or Parquet.

Minimum directories:

```
output/
  manifests/
  data_audit/
  diagnostics/
  models/
  forecasts/
  forecast_tests/
  robustness/
  tables/
  figures/
  logs/
```

Every output must carry:

- run ID;
- data snapshot hash;
- code commit SHA;
- configuration hash;
- creation timestamp;
- series/model/horizon identifiers where relevant.

# 2. Data selection, retrieval, sample, and transformation outputs

## T2.0 Concept-to-series selection table

For every retained or explicitly excluded candidate:

- Part 4 economic concept;
- candidate series;
- FRED ID if applicable;
- retained yes/no;
- economic justification;
- statistical/frequency justification;
- open-access retrieval status;
- reason for exclusion if not retained.

## T2.0A Frozen-data manifest

For every baseline file:

- series ID;
- source;
- vintage date;
- exact request parameters;
- raw first date;
- raw last date;
- row count;
- retrieval timestamp;
- SHA-256 hash;
- hash verification status.

## F2.0 Sample-coverage timeline

One horizontal timeline showing the raw/usable sample coverage of every target, the common monthly endpoint, and the VAR common sample.

Purpose: make the date choices visually auditable for the jury.

# 3. Data and transformation outputs

## T2.1 Data dictionary and sample audit

Columns:

- target name;
- FRED ID;
- raw units;
- seasonal adjustment;
- raw first date;
- raw last date;
- transformed first date;
- transformed last date;
- transformation;
- baseline/robustness role;
- source institution.

## T2.2 Stationarity and transformation decision table

For each relevant raw and transformed series:

- ADF statistic/p-value/lag/decision;
- KPSS statistic/p-value/bandwidth/decision;
- ZA statistic/p-value or critical-value decision/break date for UNRATE/FEDFUNDS;
- final baseline transformation;
- reason.

## F2.1 Raw/transformed series overview

One readable figure per target.

Requirements:

- NBER recession shading;
- break date marker for UNRATE/FEDFUNDS where ZA identifies one;
- no multi-series scaling that makes a target unreadable.

# 4. Nonlinearity outputs

## T2.3 General nonlinearity diagnostic

For each target:

- Tsay test statistic;
- p-value;
- 5% decision;
- interpretation.

## T2.4 STAR linearity and specification diagnostic

- series;
- candidate delay;
- delay-specific p-value;
- selected delay;
- LSTAR/ESTAR indication from the Teräsvirta sequence;
- interpretation.

No naive chi-square one-regime versus two-regime MS likelihood-ratio p-value is reported. The reason must be stated in the methodology text.

# 5. Model-selection and adequacy outputs

## T2.5 Selected classical specifications

- AR lag;
- AR BIC;
- ARMA order;
- ARMA BIC;
- residual adequacy status;
- fixed baseline specification.

## T3.1 In-sample adequacy summary

By series/model/refit date:

- convergence;
- log-likelihood;
- AIC;
- BIC;
- RMSE;
- MAE;
- Ljung-Box 12/24 or 4/8;
- ARCH-LM;
- Jarque-Bera;
- adequate/fragile/failed classification.

## T3.2 Nonlinear credibility summary

MSAR:

- transition matrix;
- occupancy;
- expected durations;
- transition-boundary flags.

STAR:

- type;
- delay;
- gamma;
- threshold;
- transition-function minimum/maximum/SD;
- parameter-boundary flags.

## F3.1 Representative fitted-vs-observed plots

Show:

- actual series;
- fitted values;
- model name;
- sample;
- recession shading.

Do not overlay every model if readability suffers.

## F3.2 Residual ACF diagnostics

95% confidence bands.

## F3.3 Regime-probability / STAR-transition plots

Readable, one model per panel or figure.

# 6. Baseline forecast outputs

## T3.3 Main h=1 forecast table

By target and model:

- N forecasts;
- RMSE;
- MAE;
- OOS R² vs AR;
- Harvey-Leybourne-Zu squared-loss statistic/p-value vs AR;
- Harvey-Leybourne-Zu absolute-loss statistic/p-value vs AR;
- model status.

## T3.3A Complete Harvey-Leybourne-Zu pairwise table

For each approved pair, target, horizon, and loss:

- model A;
- model B;
- N;
- mean loss differential;
- Harvey-Leybourne-Zu statistic;
- p-value;
- local-demeaning/bandwidth configuration;
- 5% decision.

Pairs:

- AR vs ARMA;
- AR vs MSAR;
- AR vs STAR;
- ARMA vs MSAR;
- ARMA vs STAR.

## T3.3B Secondary conventional DM-HLN table

For the same model pairs and losses:

- DM-HLN statistic;
- p-value;
- long-run variance/truncation rule;
- whether the DM-HLN conclusion agrees with Harvey-Leybourne-Zu.

This table is secondary. If the two procedures disagree, the disagreement must remain visible.

## T3.4 Model Confidence Set

By target/horizon/loss:

- 90% MCS membership;
- 95% MCS membership;
- elimination order/statistic where available.

## F3.4 Actual versus forecast

One target per figure.

Rules:

- AR and ARMA always shown;
- nonlinear models shown only if valid;
- failed/extreme models moved to separate diagnostic panel;
- no silent axis clipping.

## F3.5 Cumulative loss difference

Cumulative squared-error difference versus AR for each valid competitor.

Purpose: show when relative performance accumulates or reverses over time without claiming causal timing.

# 7. State-conditioned outputs

## T3.5 State forecast performance and conditional predictive ability

For each target/model/horizon and state:

- N;
- RMSE;
- MAE;
- mean loss difference vs AR.

States:

- expansion;
- recession;
- turning-point window;
- outside turning-point window.

In the same output family, report the Giacomini-White conditional predictive ability regression for each valid competitor versus AR:

- intercept;
- recession coefficient;
- turning-point coefficient;
- HAC standard errors;
- p-values;
- joint conditional-equality test;
- sign convention for the loss differential;
- inference-available flag.

## T3.6 Peak-versus-trough detail

At h=1 under the **baseline** turning-window definition:

- peak window;
- trough window;
- RMSE/MAE and N.

Use descriptive reporting if cell size is too small for formal inference.

## T4.TP1 Turning-point-window sensitivity

For each target/model/horizon, repeat the turning-point classification under:

- monthly ±1 month;
- monthly **±3 months baseline**;
- monthly ±6 months;
- quarterly turning quarter only;
- quarterly **±1 quarter baseline**;
- quarterly ±2 quarters.

Report:

- N observations in each window;
- RMSE;
- MAE;
- mean loss difference vs AR;
- direction of the nonlinear-versus-classical ranking;
- whether the substantive turning-point conclusion is unchanged, weakened, reversed, or unavailable.

Where Giacomini-White inference is numerically feasible, re-estimate the conditional predictive-ability regression with the alternative `TURN_t` definition. If the state becomes too broad or collinear for reliable inference, retain descriptive sensitivity results and mark inference unavailable.

The output must never describe ±3 months as an established universal convention. It is the predeclared baseline whose arbitrariness is tested by this table.

## F3.6 State-conditioned forecast comparison plot

Plot state-specific RMSE or MAE differences relative to AR, clearly labeled as descriptive. Formal state dependence is reported through the Giacomini-White conditional predictive ability table rather than an ad hoc bootstrap confidence interval.

# 8. Mandatory robustness outputs

## T4.1 UNRATE/FEDFUNDS transformation robustness

Baseline transformation vs alternative.

## T4.2 CPI lag robustness

p = 1, 3, 6, 12.

## T4.3 K=2 versus K=3 MSAR

- BIC;
- convergence;
- occupancy;
- transition matrix summary;
- forecast metrics;
- final retention decision.

## T4.4 Horizon robustness

Monthly h=1/3/6/12; quarterly h=1/2/4.

## T4.5 Monthly VAR cross-variable comparison

For CPI, INDPRO, UNRATE, FEDFUNDS, M2 on common sample:

- VAR lag;
- stability;
- RMSE/MAE;
- OOS R² vs AR;
- difference from univariate ranking.

## T4.6 ARCH/GARCH diagnostic where triggered

- ARCH-LM result;
- GARCH parameters;
- persistence;
- standardized-residual diagnostics;
- note on whether mean forecast changed.

# 9. Failure registry

## T4.7 Model failure and fragility registry

One row per event:

- series;
- model;
- refit date;
- horizon;
- category adequate/fragile/failed;
- reason code;
- raw diagnostic;
- whether forecast retained;
- whether figure separated.

Reason codes should include at minimum:

- NONCONVERGENCE
- NONFINITE
- SINGULAR_COV
- UNSTABLE_AR
- EMPTY_REGIME
- TRANSITION_BOUNDARY
- STAR_GAMMA_BOUND
- STAR_THRESHOLD_EXTREME
- RESIDUAL_AUTOCORR
- EXTREME_FORECAST

# 10. Main-text figure rule

The main dissertation should use only figures that answer a research question.

Do not include:

- optimizer traces;
- every residual plot;
- every transition probability;
- giant multi-model overlays;
- code/config screenshots.

Those belong in appendices or repository documentation.

# 11. Significance and confidence display

- exact p-values where space permits;
- superscript *, **, *** only for 10/5/1%;
- 95% confidence intervals only where a published inferential procedure supplies them;
- 95% bands for ACF/cross-correlation displays.

# 12. Part 8 claim-ready outputs

Claude must create a machine-readable claim matrix:

`output/manifests/claim_evidence_matrix.csv`

Columns:

- claim_id;
- claim_text_stub;
- target;
- supporting_output_files;
- baseline_result;
- robustness_result;
- status: SUPPORTED / QUALIFIED / NOT_SUPPORTED / INCONCLUSIVE;
- jury_ids_addressed.

This matrix is the bridge from empirical execution to Part 9 writing.
