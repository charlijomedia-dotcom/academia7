# Verification of fitted numerical equations in Chapters 3 and 4

This is an editorial and reproducibility note **outside the formal dissertation**. It records how the displayed fitted coefficients were checked against the frozen historical dataset and the final archived model outputs. It does not alter empirical data, model code, configuration or forecast inference.

## Data and implementation

The source is my-thesis/data/frozen/thesis_input_2026-10-05.csv (author-processed 2026-10-05 FRED/ALFRED vintage, including the two explicitly marked October 2025 carried-forward values). Monthly growth is 1200 times the first log difference. Unemployment is modelled in levels; FEDFUNDS as a first difference. The authoritative final output version is commit 9817daf91ac4cb4aaa42c2bef5deaff5b674841b.

## Chapter 3 fitted equations

**Equation (3.2): CPI AR(2), full sample.** OLS with 953 effective observations produced:

| Coefficient | Estimate | Conventional SE |
|---|---:|---:|
| Intercept | 1.31836117782480 | 0.14761616538589 |
| Lag 1 | 0.50484324329491 | 0.03192333650250 |
| Lag 2 | 0.10704368743355 | 0.03191087776045 |

Estimated residual innovation s.d. = 3.29152138904612. Reproduced Gaussian log-likelihood = -2487.604863665749. Reproduced BIC = 4995.788572042460 versus published T3.1 BIC = 4995.788572042462; absolute difference approximately 1.82e-12.

**Equation (3.3): CPI two-regime MSAR with two common lags.** Parameters and available standard errors were copied from my-thesis/output/robustness/T4.3_regime_parameters.csv (two-regime CPI rows), rounded to four decimals. The actual Hamilton-style equation is mean-adjusted for current and lagged states: y_t = mu_{S_t} + phi_1(y_{t-1} - mu_{S_{t-1}}) + phi_2(y_{t-2} - mu_{S_{t-2}}) + epsilon_t. It is not an uncentered AR with a switching intercept.

## Chapter 4 fitted equations

**Equation (4.3): CPI three-regime MSAR.** All displayed regime means, common lag coefficients, common innovation s.d., transition probabilities and standard errors were taken from the three-regime CPI rows of T4.3_regime_parameters.csv. This is an in-sample robustness fit only; the smallest state has 2.24% occupancy, and no three-state out-of-sample forecast is asserted.

**Equation (4.5): Initial-window five-variable VAR(1).** The coefficient matrix was recomputed using exactly the frozen input transformations and equation-by-equation OLS model specification from my-thesis/code/src/thesis/models/var.py. The variable order is CPI inflation, industrial production growth, unemployment in levels, federal funds rate change, M2 growth. It is not CPI, unemployment, industrial production, rates, M2. The original Chapter 4 symbolic equation was corrected to match the actual data order.

The initial balanced panel contains 240 monthly observations from February 1959 through January 1979. After one lag there are 239 effective observations. The conventional equation-by-equation OLS standard errors use residual variance divided by n minus the number of regressors and the inverse regressor cross-product.

Reproduced initial VAR log-likelihood = -2015.6331432584604 and BIC = 4195.560193074866. The published selected VAR(1) BIC in my-thesis/output/robustness/T4.5_var_selection.csv is 4195.560193074865; absolute discrepancy approximately 9.09e-13. Thus the numerical VAR estimates reproduce the published lag-selection fit to numerical precision.

## Scope

All displayed AR and MSAR full-sample coefficients are *retrospective estimates*, not coefficients fixed across rolling forecast origins. The numerical VAR matrix corresponds solely to the initial lag-selection window, whereas subsequent rolling VAR forecasts re-estimate coefficients. The estimated equations have no causal structural interpretation, and adding them does not create new forecast-accuracy tests, significant results or global-likelihood-optimum claims. Four numerical fitted equations were added to Chapters 3 and 4, and equation numbering was kept consecutive.
