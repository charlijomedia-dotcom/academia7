# Part 5: Methodology decision log

**Date:** 5 October 2026  
**Status:** PROPOSED FOR USER APPROVAL  
**Purpose:** Record the main methodological choices, why they were made, and what from the previous thesis is not carried forward automatically.

| Decision | Part 5 choice | Why |
|---|---|---|
| Core targets | Retain GDP, CPI, unemployment, industrial production, FEDFUNDS, M2 | Preserves the thesis's macroeconomic scope and Verne's theory/policy motivation |
| M2 | Retain M2SL and call it the M2 monetary aggregate | Current FRED metadata shows monthly history from 1959; old 1992 concern must be resolved with exact output dates |
| Growth transforms | Annualized log differences for GDP/CPI/INDPRO/M2 | Standard interpretable stationary growth/inflation targets |
| UNRATE/FEDFUNDS | Baseline level/difference determined by the predeclared ADF + KPSS + ZA rule on the initial estimation window; full-sample tests validate/trigger robustness but do not retrospectively change the baseline | Direct response to P-02/P-03 without forecast look-ahead |
| Stationarity tests | ADF + KPSS; Zivot-Andrews for disputed level targets | Opposing nulls plus structural-break allowance |
| Primary classical model | AR(p) | Transparent own-history benchmark |
| Stronger classical model | ARMA(p,q) | Prevent nonlinear gains from depending on an artificially weak benchmark |
| ARCH/GARCH | Conditional-variance diagnostic when ARCH-LM rejects, not automatic point-forecast competitor | GARCH primarily models conditional variance |
| Polynomial model | Excluded from main horse race | Stationary transformed targets do not require deterministic polynomial trend extrapolation |
| Nonlinear models | MSAR(2) + STAR | Clean discrete-versus-smooth state-dependence comparison |
| MSSTAR | Removed from core | Too parameter-heavy for the question; increases identification/runtime burden before simpler nonlinear models earn credibility |
| MSAR parameterization | Regime-specific intercept, AR coefficients, and variance, with nonlinear lag cap 4 monthly / 2 quarterly | Directly tests discrete state-dependent dynamics while keeping parameter count controlled |
| STAR type | LSTAR or ESTAR selected by standard Teräsvirta sequence | Established specification logic |
| Nonlinearity evidence | STAR linearity test + bootstrap AR-vs-MSAR LR | Addresses R1-18 while respecting nonstandard MS inference |
| Lag criterion | BIC, then residual-whiteness screen | More parsimonious than old AIC-first procedure and directly addresses CPI over-lagging |
| CPI robustness | p = 1, 3, 6, 12 | Direct jury response |
| Main regime count | K=2 | Interpretability and parsimony |
| K=3 | Mandatory robustness | Direct P-04 response |
| Univariate core | Retained | It is the thesis's central forecast-comparison architecture |
| Multivariate response | Monthly 5-variable VAR robustness | Genuine response to cross-variable criticism without turning thesis into a VAR dissertation |
| GDP in VAR | Not interpolated to monthly | Avoid artificial mixed-frequency construction |
| Nowcasting | Literature/scope boundary, not empirical core | A full nowcasting design requires a different information architecture and real-time vintages |
| Old oil-X application | Removed from core | It was still single-equation and did not solve the multivariate critique |
| Model adequacy | Formal gate before forecast interpretation | Implements Verne's fit-before-forecast point |
| MAPE | Removed | Unstable for zero/negative growth and inflation observations |
| Forecast metric | RMSE, MAE, OOS R² | Simple, interpretable point-forecast metrics |
| Formal pairwise test | DM with HLN correction | Familiar global comparison, improved finite-sample treatment |
| Multiple-model test | Model Confidence Set | Stronger than choosing a winner from many pairwise p-values |
| State comparison | RMSE/MAE + block-bootstrap loss-difference CI | Directly tests recession/turning-point relevance |
| Clark-West | Not baseline | Main nonlinear comparisons are not simple nested linear models |
| Amisano-Giacomini | Not baseline | Thesis evaluates point forecasts, not comparable predictive densities |
| Baseline horizon | h=1 | Preserves main question and direct interpretation |
| Horizon robustness | monthly h=3,6,12; quarterly h=2,4 | Direct P-05 response |
| Rolling windows | 240 monthly; 120 quarterly | Adequate nonlinear sample size while allowing changing macro dynamics |
| Model specification search | Initial estimation window only | Prevents repeated search and reduces computational waste |
| Parameter refit | Every 3 months monthly; every 4 quarters quarterly | Fair scheduled refit for all models, much cheaper than every-origin refit |
| Every-origin refit | Final 120 months / 40 quarters at h=1 as robustness | Tests whether the efficient baseline refit schedule drives results |
| Silent fallback after nonlinear failure | Prohibited | Failure is evidence and must remain visible |
| Figure scaling | Failure-aware separate panels | Direct R1-06 response |
| Cross-correlation uncertainty | 95% bands if any such figure survives | Direct R1-07 response |
| Data refresh | Explicit only; never overwrite frozen baseline | Reproducibility |
