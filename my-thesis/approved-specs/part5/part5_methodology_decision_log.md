# Part 5: Methodology decision log

**Date:** 5 October 2026  
**Status:** APPROVED baseline with explicit user amendments; 13 October 2026 LOCF/canonical CSV amendment supersedes unsent alternative gap-handling proposals.
**Purpose:** Record the main methodological choices, why they were made, and what from the previous thesis is not carried forward automatically.

**User-approved amendment — 12 October 2026:** Mandatory estimation-window-length robustness has been added (monthly 180/240/300, quarterly 90/120/150). The 240-month / 120-quarter baseline and all unrelated frozen Part 5 choices remain unchanged.

**User-approved amendment — 29 October 2026:** The K=3 MSAR robustness exercise (P-04) is an **in-sample** regime-count comparison of full-sample K=2 and K=3 fits. K=3 is no longer re-estimated at every pseudo-out-of-sample origin, and no K=3 out-of-sample forecasts are computed or used in any ranking, model confidence set or predictive-ability test. K=2 remains the baseline. Every other approved choice is unchanged. Full record: `part5_methodology_amendment_2026-10-29_msar_k3.md`.

**User-approved amendment — 13 October 2026:** Keep August 2026 / 2026Q2 endpoints and the October 5, 2026 historical vintage. Preserve FRED/ALFRED source observations including genuine missing values. In the **separate derived research input**, replace only October 2025 CPIAUCSL and UNRATE levels with their respective September 2025 levels (LOCF). Generate/lock/share a single fully documented seven-series long-format CSV. Part 6 loads this CSV first as a new DataFrame and performs all modeling locally without re-download on ordinary reruns. This overrides earlier *unsent* no-imputation and sample-truncation prompt drafts. Results must not be used to select a new baseline window.

| Decision | Part 5 choice | Why |
|---|---|---|
| Core targets | Retain GDP, CPI, unemployment, industrial production, FEDFUNDS, M2; use USREC only for ex post state classification | Minimum non-redundant coverage of Part 4's prices, real activity, labour, monetary policy, money, and business-cycle concepts |
| M2 | Retain M2SL and call it the M2 monetary aggregate | Required by the money-supply dimension retained at Verne's request; official monthly FRED history begins in 1959 |
| Growth transforms | Annualized local log differences computed from the frozen **canonical model-input raw levels** (official unchanged values, except disclosed CPIAUCSL/UNRATE 2025-10 LOCF) | Interpretable proportional growth/inflation, with transformed values reproducible from an immutable author-processed input CSV and the untouched source archive |
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
| K=3 | Mandatory **in-sample** robustness: full-sample K=3 compared with full-sample K=2 (amended 29 October 2026; no rolling K=3 forecasts) | Direct P-04 response: tests whether the two-regime assumption is overly restrictive through regime credibility, not out-of-sample predictive superiority |
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
| Rolling windows | Baseline 240 monthly; 120 quarterly | Ex ante bias-variance compromise under instability; literature supports rolling windows but does not uniquely dictate these exact lengths, so the thesis will state them as design assumptions rather than optimal values |
| Estimation-window-length robustness (user-approved 12 October 2026) | Monthly 180/240/300; quarterly 90/120/150, all main AR/ARMA/MSAR(2)/STAR families at h=1, fixed baseline discrete specifications, every-origin refitting, common eligible evaluation calendar and baseline predictive tests/MCS | Predeclared ±25% sensitivity to window dimension; test whether linear-versus-nonlinear ranking, inference and model fragility change without choosing a favorable baseline ex post |
| Model specification search | Initial estimation window only | Prevents repeated search and reduces computational waste |
| Parameter refit | Every forecast origin on the rolling window | Standard pseudo-out-of-sample logic; runtime is controlled by fixed specifications, simpler models, warm starts, caching, checkpointing, and parallelization rather than by holding parameters fixed |
| Silent fallback after nonlinear failure | Prohibited | Failure is evidence and must remain visible |
| Figure scaling | Failure-aware separate panels | Direct R1-06 response |
| Cross-correlation uncertainty | 95% bands if any such figure survives | Direct R1-07 response |
| Data provider | FRED/ALFRED official series IDs only; no manually edited CSV | Open machine-retrievable official source data are archived unchanged; the distinct distributable derived CSV is generated by code with transparent imputation provenance |
| Thesis vintage | 2026-10-05 historical vintage; original raw per-series archive and derived canonical input both frozen with hashes | Prevent future data revisions from changing the thesis results and allow auditing the user-approved imputations |
| Monthly endpoint | 2026M8 unchanged, including August 2026 | Latest month jointly available across the five monthly core targets in the frozen information set; October 2025 gaps repaired **only in derived input** as explicitly approved |
| GDP endpoint | 2026Q2 | Latest released quarterly GDP observation available by the thesis vintage |
| Start dates | Earliest defensible postwar observation for each univariate target; INDPRO truncated to 1947 | Maximize usable history and cycle episodes without importing Great Depression/WWII regimes not shared across targets |
| VAR sample | 1959M1–2026M8 | Common sample dictated by latest-starting component, M2; **no general interpolation/backfilling**, only two explicitly authorized 2025M10 raw-level LOCF replacements in the derived input |
| October 2025 missingness | Carry September 2025 CPIAUCSL and UNRATE raw levels into their missing October 2025 cells **only in the derived research input**; original source missingness is preserved and clearly marked | Keeps the August 2026 sample and fixed-calendar model implementation at the cost of transparent, artificial zero changes and possible downstream forecast distortions; T2.0B/T4.9 record this limitation |
| Canonical CSV input for Part 6 | One immutable, long-format `data/frozen/thesis_input_2026-10-05.csv` with all six targets + USREC, original/imputed flags, manifest/hash; later runs verify and load this file before any transformations | Exact third-party replication and no repeated API dependency, without mislabeling imputed values as official observations |
| Download-once rule | A completely empty local store may initialize from FRED/ALFRED at the frozen vintage; an existing complete hash-verified **raw-only** Part 6 snapshot may produce its canonical CSV locally once; a corrupt/partial/hash-mismatched or formerly registered-but-lost canonical input fails | Avoids unnecessary data retrieval and accidental mixing or silent replacement of the published thesis dataset |
| PCEPI | Not added as a core target | Fed-preferred inflation measure is acknowledged, but it duplicates inflation and begins later than CPI; CPI preserves longer postwar history |
| Additional debt/deficit/oil/exchange-rate targets | Not added to core | Policy-relevant but would broaden the question beyond the minimum Part 4 concepts and introduce separate frequency/measurement problems |
| Data refresh | Explicit only; never overwrite frozen baseline | Reproducibility |
