# Part 5: Methodology decision log

**Date:** 5 October 2026  
**Status:** APPROVED AND FROZEN
**Purpose:** Record the main methodological choices, why they were made, and what from the previous thesis is not carried forward automatically.

| Decision | Part 5 choice | Why |
|---|---|---|
| Core targets | Retain GDP, CPI, unemployment, industrial production, FEDFUNDS, M2; use USREC only for ex post state classification | Minimum non-redundant coverage of Part 4's prices, real activity, labour, monetary policy, money, and business-cycle concepts |
| M2 | Retain M2SL and call it the M2 monetary aggregate | Required by the money-supply dimension retained at Verne's request; official monthly FRED history begins in 1959 |
| Growth transforms | Annualized local log differences computed from frozen raw GDP/CPI/INDPRO/M2 levels | Interpretable proportional growth/inflation, less trend persistence, and exact reproducibility from immutable raw values |
| UNRATE/FEDFUNDS | Baseline level/difference determined by the predeclared ADF + KPSS + ZA rule on the initial estimation window; full-sample tests validate/trigger robustness but do not retrospectively change the baseline | Direct response to P-02/P-03 without forecast look-ahead |
| Stationarity tests | ADF + KPSS; Zivot-Andrews for disputed level targets | Opposing nulls plus structural-break allowance |
| Primary classical model | AR(p) | Transparent own-history benchmark |
| Stronger classical model | ARMA(p,q) | Prevent nonlinear gains from depending on an artificially weak benchmark |
| ARCH/GARCH | Conditional-variance diagnostic when ARCH-LM rejects, not automatic point-forecast competitor | GARCH primarily models conditional variance |
| Polynomial model | Excluded from main horse race | Stationary transformed targets do not require deterministic polynomial trend extrapolation |
| Nonlinear models | MSAR(2) + STAR | Clean discrete-versus-smooth state-dependence comparison |
| MSSTAR | Removed from core | Too parameter-heavy for the question; increases identification/runtime burden before simpler nonlinear models earn credibility |
| MSAR parameterization | Hamilton-style regime-specific mean, common AR coefficients, common variance; lag cap 4 monthly / 4 quarterly | Strong canonical precedent, clearer interpretation, and lower identification risk than switching every coefficient |
| STAR type | LSTAR or ESTAR selected by standard Teräsvirta sequence | Established specification logic |
| Nonlinearity evidence | Tsay general nonlinearity test + Luukkonen-Saikkonen-Teräsvirta / Teräsvirta STAR specification tests; no naive one-vs-two MS chi-square LR | Strong published pre-estimation diagnostics while respecting the nonstandard nature of regime-switching tests |
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
| Primary pairwise forecast test | Harvey-Leybourne-Zu (2025) instability-robust equal-average-accuracy test | Recent Q1 procedure directly designed for forecast-loss differentials whose mean may vary over time, matching the thesis instability setting |
| Secondary pairwise test | DM with Harvey-Leybourne-Newbold correction | Retained as a familiar conventional benchmark and for transparent comparison with the submitted thesis; not the primary inferential result |
| Multiple-model test | Model Confidence Set | Stronger than choosing a winner from many pairwise p-values |
| State comparison | State-specific RMSE/MAE + Giacomini-White conditional predictive ability regression | Top-journal framework for testing whether relative forecast performance changes in predeclared recessions/turning points; recent Odendahl-Rossi-Sekhposyan evidence supports state-dependent evaluation |
| Turning-point window | Monthly ±3 months baseline; quarterly ±1 quarter baseline | Predeclared short transition neighborhood informed by Q1 business-cycle dating literature; not claimed to be a universal theorem |
| Turning-window robustness | Monthly ±1 / ±3 / ±6 months; quarterly 0 / ±1 / ±2 quarters | Prevent any peak/trough conclusion from depending on the arbitrary baseline width |
| Clark-McCracken / Clark-West | Not baseline | Designed for regular nested comparisons; main AR-vs-MSAR/STAR comparisons are not regular nested linear settings |
| Amisano-Giacomini | Not baseline | Thesis evaluates point forecasts, not a common validated set of predictive densities |
| Baseline horizon | h=1 | Preserves main question and direct interpretation |
| Horizon robustness | monthly h=3,6,12; quarterly h=2,4 | Direct P-05 response |
| Rolling windows | 240 monthly; 120 quarterly | Ex ante bias-variance compromise under instability; literature supports rolling windows but does not uniquely dictate these exact lengths, so the thesis will state them as design assumptions rather than optimal values |
| Model specification search | Initial estimation window only | Prevents repeated search and reduces computational waste |
| Parameter refit | Every forecast origin on the rolling window | Standard pseudo-out-of-sample logic; runtime is controlled by fixed specifications, simpler models, warm starts, caching, checkpointing, and parallelization rather than by holding parameters fixed |
| Silent fallback after nonlinear failure | Prohibited | Failure is evidence and must remain visible |
| Figure scaling | Failure-aware separate panels | Direct R1-06 response |
| Cross-correlation uncertainty | 95% bands if any such figure survives | Direct R1-07 response |
| Data provider | FRED/ALFRED official series IDs only; no manual CSV construction | Open, machine-retrievable U.S. macro data from official underlying agencies |
| Thesis vintage | 2026-10-05 historical vintage, frozen locally with hashes | Prevent future data revisions from changing the thesis results |
| Monthly endpoint | 2026M8 | Latest month jointly available across the five monthly core targets in the frozen information set |
| GDP endpoint | 2026Q2 | Latest released quarterly GDP observation available by the thesis vintage |
| Start dates | Earliest defensible postwar observation for each univariate target; INDPRO truncated to 1947 | Maximize usable history and cycle episodes without importing Great Depression/WWII regimes not shared across targets |
| VAR sample | 1959M1–2026M8 | Common sample dictated by latest-starting component, M2; no interpolation/backfilling |
| PCEPI | Not added as a core target | Fed-preferred inflation measure is acknowledged, but it duplicates inflation and begins later than CPI; CPI preserves longer postwar history |
| Additional debt/deficit/oil/exchange-rate targets | Not added to core | Policy-relevant but would broaden the question beyond the minimum Part 4 concepts and introduce separate frequency/measurement problems |
| Data refresh | Explicit only; never overwrite frozen baseline | Reproducibility |
