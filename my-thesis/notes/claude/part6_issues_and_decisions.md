# Part 6 — Decisions register

**Status:** DECIDED BY USER on 2026-10-09, before any empirical result existed. These are fixed Part 6 implementation decisions.
**Authority:** `approved-specs/part5/` remains frozen and unmodified. Nothing here amends it. Where an item resolves an ambiguity, silence or undefined term in frozen Part 5, it is tagged **[UAIC]** — *user-approved implementation clarification* — and must be cited as such in Part 8/Part 9 wording, never as a change of approved methodology.
**Result-blind rule (CLAUDE.md §6):** every value below was fixed before results were seen and may not be revised because it changes an empirical outcome.
**Companion:** `part6_implementation_plan.md`.
**Amendments:** Part 5 was amended by the user on 12 and 13 October 2026 (window-length robustness; October 2025 LOCF and the canonical CSV architecture). Those amendments are recorded in §G below and **supersede** the earlier N1 options. No blocker remains open.

---

## A. Approved resolutions of tensions in the authoritative texts

| ID | Decision | Notes |
|---|---|---|
| **T1** | **Option (a).** The p = 1, 3, 6, 12 exercise is an **AR-lag benchmark robustness check** (jury R1-15, suspicious CPI AR(12)). Re-estimate the **CPI AR benchmark only** at p = 1, 3, 6, 12. ARMA, MSAR and STAR stay at their approved baseline specifications and approved lag caps. Compare the nonlinear models against each alternative AR benchmark on **common forecast dates**. No duplicate p=6/p=12 nonlinear models capped back to 4. Caps are not lifted. | T4.2 must be labelled "CPI AR-lag benchmark robustness". **[UAIC]** |
| **T2** | Keep the **intercept-only** ADF/KPSS versions required by frozen Part 5 as the traceable baseline. **Additionally** run constant-plus-trend versions on the log levels as a clearly labelled extra diagnostic. The trend diagnostics may not change any predeclared baseline transformation or selection rule. | **[UAIC]** |
| **T3** | Report **both** the joint test over all regression coefficients **and** a slopes-only Wald test. Naming and interpretation follow **M1**. | superseded in naming by M1 |
| **T4** | Approved: **stricter superset cache key**. | — |
| **T5** | **Option (a).** Freeze raw official observations **exactly as returned**. UNRATE's 2026M9 observation is preserved in frozen raw data and truncated to the approved 2026M8 common endpoint only when the empirical sample is constructed. Report **both raw-last and usable-last** dates. | applies equally to FEDFUNDS (see N2). **[UAIC]** |
| **T6** | Use **`vintage_dates=2026-10-05`** as the primary historical-vintage request. Save exact API parameters. Use `realtime_start=realtime_end=2026-10-05` as an **audit cross-check**. On material discrepancy: **stop and document**, never choose silently. | Verified 2026-10-09: both forms return identical row counts and endpoints for all seven series (N3). **[UAIC]** |
| **T7** | **Option (a).** "Initial estimation window" = the **first approved rolling estimation window**: 240 observations (monthly targets), 120 observations (quarterly GDP). | **[UAIC]** |

## B. Approved methodological handling

| ID | Decision |
|---|---|
| **M1** | **Retain** the target-date `REC_t` / `TURN_t` analysis, but **do not call it a Giacomini–White conditional predictive-ability test**. Target-date NBER states are not measurable from the forecast-origin information set that Giacomini–White requires. Implement `d_t = α + β_rec REC_t + β_turn TURN_t + u_t` with horizon-appropriate HAC inference and name it an **ex-post state-dependent forecast-loss regression**. It tests whether *realized* relative forecast loss differs across recessions and turning-point neighbourhoods; it does **not** establish real-time conditional forecast selection. **Report:** α, β_rec, β_turn; individual p-values; joint Wald α = β_rec = β_turn = 0; separate state-dependence Wald β_rec = β_turn = 0; HAC rule; state sample sizes; descriptive state RMSE/MAE. Giacomini–White is preserved in the methodological discussion as the conditional-predictive-ability reference, without claiming our regression meets its information-set requirement. **[UAIC — naming and interpretation only; the regression specified in Part 5 §10.5 is implemented unchanged]** |
| **M2** | **STAR multi-step:** no naive/skeleton iteration as baseline. Use **residual-bootstrap simulation** of the iterated nonlinear conditional mean (Teräsvirta–van Dijk–Medeiros approach): at every origin resample **centred fitted STAR residuals from that estimation window**, propagate the nonlinear recursion, average simulated h-step forecasts. **5,000 paths per origin**, deterministic child seeds, record path count and seed logic. **h = 1 remains analytic.** Skeleton iteration retained only as a clearly labelled numerical diagnostic, never the headline. **MSAR multi-step:** exact state-probability recursion where technically valid. **[UAIC]** |
| **M3** | **Do not defer HLZ and do not wait for a user upload.** Retrieve the open-access Harvey–Leybourne–Zu (2025) JBES article (DOI `10.1080/07350015.2024.2418835`) **and** its official supplementary appendix, read both, and implement local demeaning, LRV construction, bandwidth/smoothing rules, reference distribution / finite-sample critical-value procedure and all other tuning choices **exactly as the authors state**. Generic Newey–West/HAC machinery may **never** be labelled HLZ. Record the article/supplement version or checksum used for validation. **RESOLVED 2026-10-09:** supplement downloaded from figshare; article supplied by the user after automated retrieval was blocked by Cloudflare on every open-access route. Both held with checksums in `source-materials/hlz2025/`. Implemented from the documents and validated against the article's own theorems and simulation DGP. |
| **M4** | **Option (a).** Preserve the approved ARMA grid literally. A selected q = 0 or p = 0 specification is allowed and must be **flagged transparently in T2.5**. Do not force p ≥ 1 and q ≥ 1. |
| **M5** | **Option (a).** No new structural-break-dummy forecasting model. The approved alternative level/difference exercise **is** the transformation robustness check. If ZA detects a break, report the break evidence and state that the robustness exercise does not identify a separate break-dummy model. |
| **M6** | **Option (a).** Formal predictive tests stay on the **modeled stationary target**. **Additionally** report common-scale reconstructed **level** forecast errors for baseline and alternative transformations where meaningful. Keep formal modeled-target inference and the additional level-error comparison clearly distinguished. **[UAIC]** |
| **M7** | **The proposed 90% valid-origin threshold is rejected. No model-eligibility percentage is invented.** Fixed rule: report each model's **attempted / valid / failed** origins; model-specific descriptive metrics on that model's valid observations with N shown; **every pairwise relative comparison uses the intersection of valid dates for that pair**; **MCS uses the intersection of finite-loss dates across all models in that MCS**; report `T_common` and the number of observations removed by common-date alignment; **never** silently drop a poorly behaving model to enlarge the common sample; if the common loss matrix is too small or MCS is numerically undefined, mark **MCS inference unavailable** and report why. No "≥90% valid" MCS variant unless separately approved later. **[UAIC]** |
| **M8** | **K=3 for all six targets and every approved forecast origin.** h = 1 is the mandatory headline K=3 robustness result; the approved longer horizons are also generated from those same fits. Execution is **not** conditional on whether K=3 results look favourable. |
| **M9** | **Trigger:** rejection of ARCH-LM on the **selected ARMA model's initial-window residuals**. For triggered series, run the ARMA-GARCH(1,1) diagnostic through the **same rolling pseudo-OOS chronology** and generate its mean forecasts. Explicitly diagnostic: **excluded from the main AR/ARMA/MSAR/STAR horse race and from MCS**. **[UAIC]** |
| **M10** | **Option (a).** VAR: 240-month rolling window; p ∈ {1,2,3} by BIC on the **initial VAR window**; lag fixed; parameters re-estimated at each origin; stability required; h = 1, 3, 6, 12; each component compared against the corresponding univariate forecasts on **identical common target dates**. **[UAIC]** |
| **M11** | Approved as proposed: states built only from **observed USREC transitions**; turning windows **clipped at sample boundaries**; **unions** so no observation is double-counted within the turning mask; recession and turning-window categories **may overlap** because they answer different state questions. Documented in output notes. **[UAIC]** |
| **M12** | **The "fewer than 5 observations" rule is rejected.** Always report state-cell N and flag **very small cells as weak evidence**. Formal regression inference is unavailable **only** when: the state variable has no variation; the design matrix is rank deficient; the covariance calculation is non-finite or singular; or the regression otherwise fails numerically. **[UAIC]** |
| **M13** | **The "magnitude halved" criterion is rejected.** Categories: **`unchanged`** = same direction and same substantive inferential conclusion as baseline; **`weakened`** = same direction but inferential support present under baseline is lost under the alternative window; **`reversed`** = sign of the relevant relative-loss comparison reverses; **`unavailable`** = required comparison/inference cannot be computed. Add a separate **`support_change`** field (plus notes) so a same-direction result that becomes statistically **stronger** is recorded as strengthened without inventing a fifth headline category. **[UAIC]** |

## C. Approved implementation details

| ID | Decision |
|---|---|
| **D1** | Primary Ljung–Box lag **12 monthly / 4 quarterly**; also report **24 monthly / 8 quarterly**. df correction: **AR → AR parameter df**; **ARMA → p+q**. **Do not** mechanically apply a p+q correction to MSAR/STAR — their Ljung–Box results are **diagnostic** and the exact nonlinear df convention must be **documented** in the output. **[UAIC]** |
| **D2** | Approved: **common effective sample** for BIC comparison across candidate AR orders. **[UAIC]** |
| **D3** | **Revised.** Implement the standard **Tsay (1986) quadratic nonlinearity test**: construct **all unique quadratic lag terms** for the working AR(p) and use the appropriate **nested / orthogonalized auxiliary-regression F test**. Validate against reference values from a recognized implementation (e.g. R `TSA::Tsay.test`) **and** against simulations. An informal residual-on-cross-products regression is **not** acceptable on its own. **[UAIC]** |
| **D4** | Approved standard LST/Teräsvirta procedure, with **H02/H03/H04 labels, auxiliary equations and the LSTAR-vs-ESTAR decision rule matching the published procedure exactly**. Store **all** delay-specific test results and the deterministic tie rule. **[UAIC]** |
| **D5** | **Scale-free transition parameterization.** Standardized transition distance `(z − c)/s_z`. **LSTAR:** logistic with γ multiplying the standardized distance. **ESTAR:** γ multiplying the **squared** standardized distance. (Equivalent to SD scaling for logistic, variance scaling for exponential.) **γ > 0**, numerical bound **[1e-3, 1e3]** for the dimensionless γ; **c ∈ [min(z), max(z)]**. These are **numerical optimization bounds, not economic thresholds**, and the parameterization must be recorded. **MSAR:** stable logistic/simplex parameterization for transition probabilities; positive transform (e.g. log σ) for the innovation SD. **[UAIC]** |
| **D6** | Approved **deterministic multi-starts**. Record **every** initial start, its convergence outcome, objective value, and the winning start. |
| **D7** | **Modified.** An estimate landing on a hard optimization bound does **not** by itself mean non-convergence. Convergence requires: optimizer success, finite objective and parameters, acceptable numerical termination. **Boundary contact is classified separately under the approved fragility rules** (frozen Part 5 treats a STAR γ on its bound as a fragility warning). **[UAIC]** |
| **D8** | **Not all proposed thresholds approved.** See §D8 table below. |
| **D9** | ADF with BIC and the approved monthly/quarterly caps. KPSS with the **pinned library's** automatic lag/bandwidth rule, recorded. ZA on UNRATE/FEDFUNDS: **intercept+trend break, trim 0.15, BIC, maximum lag 12** (monthly). Use critical values corresponding **exactly** to the implemented ZA specification/library or a published reference — **do not hard-code an approximate generic value such as −5.08**. **[UAIC]** |
| **D10** | Approved **Newey–West/Bartlett truncation h−1** for DM-HLN and for the ex-post state-loss regression, all choices recorded. The **HLZ variance estimator is kept completely separate** and implemented per Harvey–Leybourne–Zu. **[UAIC]** |
| **D11** | MCS: Hansen–Lunde–Nason, **method `R`**, **stationary bootstrap**, **fixed deterministic seed**, **5,000 replications**, block length **`ceil(sqrt(T_common))`**. Run separately for squared-error and absolute-error loss and for **90% and 95%** sets. Record `T_common`, block length, replications, seed and elimination results. **[UAIC]** |
| **D12** | Approved: **`d_t = loss_competitor − loss_benchmark`**; negative ⇒ competitor more accurate. Stated in every relevant table. **[UAIC]** |
| **D13** | Approved: frozen CSV + metadata JSON + SHA-256 + master manifest; **refusal to overwrite an existing frozen manifest**. Commit frozen thesis data to the repository only if repository size/policy permits; otherwise commit the **immutable manifest** and use the approved persistent storage arrangement. **Never silently replace the baseline snapshot.** *(Measured 2026-10-09: all seven raw series total well under 1 MB, so committing them is within normal repository policy.)* |
| **D14** | Approved provenance mechanics and **dirty-tree protection for thesis-facing runs**. |
| **D15** | Approved **dependency-aware code/config hashing** for caches; reporting-only changes do not invalidate econometric fits. |
| **D16** | Approved **separate smoke / refresh / robustness / baseline namespaces**. No smoke or refresh output may overwrite baseline output. |
| **D17** | Approved provisional IDs **`T3.2-FF`** (policy-rate diagnostic) and **`T-DIAG`** (standardized hypothesis-test table). |
| **D18** | Approved: Part 6 builds and validates the **claim-evidence schema**; Part 8 populates the substantive matrix from final results. |
| **D19** | Approved **failure-aware figures**: no clipping, separate failure/extreme panels. |
| **D20** | Approved numeric p-values **plus** a stars column at 10/5/1%. **No cross-correlation figure is required**; if one is later retained, the frozen 95% uncertainty-band rule applies. |

### D8 — approved flag and failure thresholds

**Preserved exactly as frozen in Part 5** (operational warning flags, never statistical critical values):

| Flag | Rule | Class |
|---|---|---|
| Low occupancy | occupancy < 5% **or** < 20 effective observations | fragile |
| Boundary behaviour | transition probability ≤ 0.005 **or** ≥ 0.995 | fragile |
| `STAR_THRESHOLD_EXTREME` | c outside the 5th–95th percentile of the transition variable | fragile |
| `RESIDUAL_AUTOCORR` | primary Ljung–Box rejects at 5% | fragile |
| `UNSTABLE_AR` | required AR/ARMA stationarity or invertibility condition violated | **failure** |

**Additional approved rules:**

| Item | Approved rule |
|---|---|
| `EMPTY_REGIME` | **Not** defined as occupancy < 2. Low occupancy alone is already *fragile* under Part 5. **Failure** requires effective non-identification or computational/statistical unusability: numerically zero posterior occupancy **together with** unidentified regime parameters, singular covariance, non-finite likelihood/parameters, or equivalent **documented** evidence. |
| `STAR_GAMMA_BOUND` | **Numerical contact with the actual optimizer bound within optimizer tolerance.** The proposed arbitrary "within 5% of the bound" rule is rejected. |
| Near-constant transition | `SD(G) < 0.05` **OR** `range(G) < 0.10` — transparent operational fragility warning, **explicitly labelled non-theoretical**. |
| Covariance | Non-finite / non-invertible / not positive definite when required for meaningful inference ⇒ **failure**. A very ill-conditioned but still computable covariance ⇒ **fragile**, with the condition-number rule recorded as an **engineering diagnostic**. |
| Parameter uncertainty | The proposed "SE > 10× series SD / > 5 dimensionless" rule is **removed**. **Report parameter uncertainty directly** instead. |
| Near-unit-root | The proposed 1.01 near-unit-root fragility threshold is **not added** to the methodology. |
| `EXTREME_FORECAST` | A forecast beyond **6 rolling-window standard deviations** from the rolling-window mean is a **transparent fragility/plotting warning only** — **not** an automatic failure and **not** a reason to delete the forecast from numerical results. |

## D. Approved risk handling

| ID | Decision |
|---|---|
| **R1** | **One-time `--initialize-frozen` approved** (key supplied 2026-10-09). Must use the approved 2026-10-05 vintage, preserve exact raw data, write hashes/metadata, and **stop on any unexplained discrepancy**. **If initialization fails, do not substitute another source or current data.** |
| **R2** | Install the required scientific Python environment and **pin exact tested versions** in the lock/environment record. *(Done 2026-10-09 — see plan §1.)* |
| **R3–R10** | Proposed engineering mitigations approved **where they do not alter the methodological decisions above**. |

**Key handling (my own operational note, not a user decision):** the FRED key was supplied in chat and is therefore exposed in the conversation transcript. It is stored only outside the repository (session scratchpad, mode 600), read from the environment by code, never hard-coded, never logged, and never committed. **Recommend rotating the key at fred.stlouisfed.org once the frozen snapshot exists**; the frozen data and manifest make the key unnecessary for every later baseline run.

---

## E. New findings from vintage verification (2026-10-09)

Verified directly against the FRED/ALFRED 2026-10-05 vintage before writing any pipeline code.

### N1 — October 2025 missing from CPIAUCSL and UNRATE — **RESOLVED by the 13 October 2026 amendment** (see §G2)

The 2026-10-05 vintage returns a **complete monthly grid with no gaps and no duplicates** for every series, but **CPIAUCSL and UNRATE each contain exactly one missing value, both at 2025-10-01**. This is not an API artifact and no later vintage will repair it: during the 2025 federal shutdown the BLS could not collect the October 2025 reference-period data, the October 2025 CPI release was cancelled, and the October 2025 household survey — the source of the unemployment rate — was never collected and **cannot be collected retroactively**.

The gap is real and permanent. **Options A–F in `data_discrepancy_2026-10-09.md` are SUPERSEDED and must not be reopened.** The approved resolution is the raw-level LOCF of §G2: September 2025 values are carried forward into the two October cells, in the derived canonical input only, with the official raw archive left untouched.

Unaffected: GDPC1, INDPRO, FEDFUNDS, M2SL, USREC are complete. The **initial estimation window** (1947/1948 onward) is decades away from the hole, so **no locked specification-selection or stationarity decision is affected**. The approved monthly endpoint 2026M8 is unaffected.

### N2 — FEDFUNDS raw series extends to 2026M9, not 2026M8

`part5_data_selection_retrieval_reproducibility_rationale.md` §6.3 states that CPI, INDPRO, FEDFUNDS and M2 were all available through August 2026. In the actual vintage **FEDFUNDS ends 2026-09-01** (as does UNRATE). The **operative endpoint rule is unaffected**: the latest month jointly available across the five monthly targets is still **2026M8**, because CPI, INDPRO and M2 end in August. So the approved endpoint stands and only the explanatory sentence in the rationale is factually off. Handled exactly like UNRATE under **T5(a)**: freeze 2026M9 as returned, truncate to 2026M8 when building the sample, report both dates. **No methodology change; recorded for Part 9 so the thesis does not repeat the inaccurate sentence.**

### N3 — T6 cross-check passes

For all seven series, `vintage_dates=2026-10-05` and `realtime_start=realtime_end=2026-10-05` returned **identical row counts, first dates, last dates and last values**. The initializer will additionally perform a **full value-by-value** comparison and halt on any material difference.

### N4 — Observed raw ranges (2026-10-05 vintage)

| Series | Raw first | Raw last | Rows | Interior missing | Approved usable range |
|---|---|---|---:|---|---|
| GDPC1 | 1947-01-01 | 2026-04-01 (2026Q2) | 318 | none | 1947Q1–2026Q2 |
| CPIAUCSL | 1947-01-01 | 2026-08-01 | 956 | **2025-10** | 1947M1–2026M8 |
| UNRATE | 1948-01-01 | **2026-09-01** | 945 | **2025-10** | 1948M1–2026M8 |
| INDPRO | 1919-01-01 | 2026-08-01 | 1292 | none | truncated to 1947M1–2026M8 |
| FEDFUNDS | 1954-07-01 | **2026-09-01** | 867 | none | 1954M7–2026M8 |
| M2SL | 1959-01-01 | 2026-08-01 | 812 | none | 1959M1–2026M8 |
| USREC | 1854-12-01 | 2026-09-01 | 2062 | none | clipped to each target's evaluation span |

All start dates match frozen Part 5. INDPRO's pre-1947 history exists as Part 5 anticipated and is truncated as specified.

---

## F. Items still open

| ID | Item | Status |
|---|---|---|
| **N1** | October 2025 handling | **CLOSED 2026-10-13.** Resolved by the approved amendment (§G2). Earlier options A–F superseded. |
| **M3** | HLZ article + supplementary appendix | **CLOSED 2026-10-09.** Both documents held with checksums; module implemented and validated (39 tests). |
| **H1** | HLZ two-sided vs one-sided reporting | **Confirmed by the user on 13 October 2026:** two-sided is the primary result, one-sided p-values reported separately. Implemented. |

Nothing is blocking.

## G. Part 5 amendments approved by the user (12 and 13 October 2026)

These were made directly in the seven `approved-specs/part5/` files and pulled into this
branch. They are approved methodology, not implementation clarifications, so they are
recorded separately from the register above.

### G1 — Mandatory estimation-window-length robustness (12 October 2026)

**Authority:** `part5_methodology_specification.md` §9.5 amendment; Outputs **T4.8/F4.8**;
Comp §13; decision log and literature justification §3.18.

| Element | Approved value |
|---|---|
| Monthly lengths | **180 / 240 (baseline) / 300** observations (15 / 20 / 25 years) |
| Quarterly lengths | **90 / 120 (baseline) / 150** observations (22.5 / 30 / 37.5 years) |
| Models | AR, ARMA, MSAR(2), STAR |
| Horizon | **h = 1 only** |
| Targets | all six |
| Discrete specifications | **reused from the baseline initial window**; never re-searched per length, never reselected on ex-post performance |
| Parameters | re-estimated at every eligible origin from that origin's trailing window |
| Evaluation calendar | **common calendar starting when the longest candidate window is available**; pairwise intersections and MCS common-loss dates as per M7 |
| Inference | same HLZ (primary), DM-HLN (secondary) and MCS conventions as the baseline |
| Reporting | RMSE, MAE, OOS R² vs AR, ranks, mean loss differential, adequacy/fragility/failure incidence, N and dropped-date counts |
| Classification | unchanged / weakened / reversed / unavailable, plus a `support_change` field for strengthened evidence |
| Outputs | `output/robustness/window_length_comparison.csv`, `window_length_predictive_tests.csv`, `window_length_origin_audit.csv`, and figure F4.8 |
| Constraints | separate run ids and cache keys including window length; **never overwrite baseline artifacts**; no mandatory factorial cross-product with other robustness dimensions; never choose a length after seeing its result |

### G2 — October 2025 LOCF and the canonical CSV architecture (13 October 2026)

**Authority:** `part5_methodology_specification.md` §2.2A; rationale §5.4; Comp §2, §5, §6, §11, §15;
Outputs **T2.0A/T2.0B/T2.1/T4.9**; decision log; literature justification §3.42.

**The imputation.** Exactly two cells, applied at the **raw level**, once, **before** any
difference, log change, transformation, lag construction or estimation, and **only** in the
derived canonical input:

| Series | Date | Official value | Model-input value | Source |
|---|---|---|---|---|
| CPIAUCSL | 2025-10-01 | missing (unreported) | September 2025 level | 2025-09-01 |
| UNRATE | 2025-10-01 | missing (unreported) | September 2025 level | 2025-09-01 |

The official raw archive keeps its missing-value markers and its post-endpoint observations
(UNRATE and FEDFUNDS 2026M9). The imputed values are **never** described as official
observations. No other missing value anywhere may be imputed. Halt conditions, each a
documented stop rather than a silent substitution: an October value that is actually
present, a missing September predecessor, unexpected missing values elsewhere, duplicate
dates, or inconsistent vintage values.

**Disclosed artifacts** (must be stated in the thesis): October 2025 CPI inflation is
**exactly zero** by construction; the observed September-to-November index change loads
entirely on November; if UNRATE is differenced its October change is **exactly zero** by
construction. These are modelling artifacts, not observed economic outcomes, and may affect
rolling estimates, state identification, realized losses and inference.

**Unchanged:** the 2026-10-05 vintage, the 2026M8 monthly endpoint, the 2026Q2 GDP endpoint,
all start dates, model families, transformations, tests and other robustness specifications.

**The canonical input.** One immutable long-format file
`data/frozen/thesis_input_2026-10-05.csv` with columns
`series_id,date,frequency,value,source_value,observation_status,imputation_method,imputation_source_date`,
covering the six targets plus USREC at their true frequencies over the approved study
ranges. Deterministic bytes: values written verbatim from source, stable row order
(series then date), fixed column order, ISO dates, UTF-8, LF. No transformed values,
forecasts or future data. Companions: metadata JSON, researcher README/data dictionary,
two-row imputation audit, and a supplemental manifest linked to the untouched raw manifest.

**CSV-first execution contract.** Every normal run verifies hashes, loads the canonical CSV
**first** into a fresh DataFrame, derives monthly and quarterly panels in memory, and then
computes everything downstream. **No FRED request on a validated repeat run.** Store rules:
an entirely absent store may initialize once from FRED at the approved vintage; a complete
hash-verified **raw-only** snapshot may build the canonical CSV **once, locally, without
network**, leaving the raw manifest untouched; a registered-but-missing, corrupt,
hash-mismatched, or partial store is a **failure**, never a re-download or overwrite.
The canonical CSV hash is the **data input identity** of every Part 6 result and is recorded
in every run manifest; it also enters the model-fit cache key together with its parent
source-manifest hash.

### G3 — New required outputs

| ID | Content |
|---|---|
| **T2.0B** | canonical CSV, metadata JSON, README/data dictionary, `output/data_audit/october_2025_imputation_audit.csv`, and the cross-referencing master manifest |
| **T2.0A** | extended with an original-source vs author-processed indicator, parent snapshot hash and imputation-audit hash |
| **T2.1** | extended with raw/derived provenance and LOCF status for the two October cells |
| **T4.8/F4.8** | estimation-window-length robustness (G1) |
| **T4.9** | `output/data_audit/locf_forecast_exposure.csv`: per series/model/horizon/origin, whether the realized target is imputed or its transformation uses the imputed predecessor, whether the predictor lag vector contains an imputed observation, and whether the rolling estimation window does; plus descriptive accuracy on (a) the full approved dates and (b) unaffected pre-gap dates with N and ranges. **Headline inference stays on the full sample**; the subsample is descriptive and must document its power limitations. Not grounds for changing the endpoint or the LOCF assumption after seeing results. |


---

## H. Implementation record (13 October 2026) — pipeline completion

This section records implementation facts and corrections from the final Part 6 build. It
contains no methodological changes; everything below is either a programming decision
inside the approved design or a correction of my own coding error, as CLAUDE.md §6A
requires.

### H1 — Canonical CSV path discrepancy resolved without touching the dataset

Part 5 §2.2A places the canonical input at `data/frozen/thesis_input_2026-10-05.csv`. My
first build had written it inside the vintage subdirectory. The file was moved with
`git mv`, so the bytes were never rewritten: the SHA-256 is unchanged at
`7e7dc769bd63ca4951ef55430180f413de62c9dc53a275af50ad277a715b832a`, which is also the
recorded data-input identity. `core/paths.py` now defines `CANONICAL_DIR = FROZEN_DIR`
with the reason, and the store layout tests assert the two-level arrangement: untouched
official raw files in `data/frozen/fred_vintage_2026-10-05/`, derived canonical input one
level above.

### H2 — `run_all.py` now reproduces the complete analysis

The entry point previously stopped after verifying and summarizing the frozen input. It
now runs `thesis.pipeline.Pipeline`, which executes every stage of the approved
methodology in order and writes every required output, manifest, figure and log.
`--data-only` preserves the old quick provenance check, `--smoke-test` selects the smoke
namespace, and `--no-cache` forces re-estimation.

### H3 — Corrected coding error: figure identifiers were being truncated

`reporting/figures.save` used `Path.with_suffix` to attach the output format. The required
figure identifiers contain dots (`F2.0`, `F3.1`, `F4.8`), so `with_suffix` read
`.0_sample_timeline` as the file extension and replaced it: every `F2.x` figure collapsed
onto `F2.png` and overwrote the previous one, and likewise for `F3.x`.

- **Cause:** misuse of `with_suffix` on stems that legitimately contain dots.
- **Code changed:** `reporting/figures.save` now appends the format to the whole name.
- **Outputs affected:** all figures in any run made before the fix. None of those runs
  were thesis-facing; the first affected run was a smoke run, whose namespace is
  separate from baseline output by construction.
- **Action:** the smoke output tree was deleted and regenerated from scratch, so no
  superseded figure survives alongside a corrected one.
- **Regression test:** `tests/unit/test_reporting.py::TestFigureConventions::`
  `test_figure_identifiers_containing_dots_are_not_truncated`.

### H4 — Corrected coding error: a failed fit reached the residual battery

A failed ARMA fit returns an empty residual array, which the §7.3 battery then passed to
`acorr_ljungbox`, producing a `RuntimeWarning` and a meaningless statistic. The adequacy
stage now detects the absence of usable residuals, records the fit as `FAILED` with
reason code `NONFINITE`, writes the row to the failure registry, and emits an adequacy row
carrying `unavailable_reason` instead of a fabricated diagnostic. No diagnostic is
invented where the model did not fit (CLAUDE.md §7).

### H5 — MSAR residuals added so the regime models face the same battery

`MSARFit` had no residual series, which would have exempted the Markov-switching models
from the §7.3 adequacy battery that AR, ARMA and STAR all face. `one_step_residuals()`
now returns genuine one-step prediction errors, formed from the state probabilities
implied by information through *t−1* rather than from smoothed values, and
`fitted_values()` is their complement. Verified: residuals plus fitted values reconstruct
the series exactly, and the one-step RMSE exceeds the within-regime σ, as it must when
the regime is uncertain.

### H6 — Numerically stable transition function

The LSTAR logistic was evaluated as `1/(1+exp(-x))`, which overflows for large |x| during
optimization at high gamma and emitted a stream of warnings. It is now
`scipy.special.expit`, and the ESTAR form uses `-expm1`. Both are the same functions
computed stably: the values agree to the last bit wherever the naive form is safe, and the
limits 0 and 1 are the correct answers where it is not. No model, parameter or bound
changed.

### H7 — Parallelism (Comp §8), with determinism asserted rather than assumed

`forecasting/parallel.py` runs independent rolling chains across worker processes.
Parallelism is applied at the level of a whole chain — one (series, model, window length)
triple — and never inside one, because warm starts make a chain path dependent. Each fit
draws randomness from a seed derived from the series, model, specification and origin
date, never from a shared stream, so a fit's result cannot depend on how many other fits
preceded it. `tests/integration/test_parallel.py` asserts that a four-worker run returns
byte-identical forecasts, fit records, failure events, data gaps, estimated parameters and
log-likelihoods to a serial run; only the measured wall time differs. Each worker is held
to one BLAS thread, since four workers each spawning four BLAS threads on a four-core
container contend rather than compute.

### H8 — Runtime finding for Part 8 scheduling (not a methodological issue)

Measured on this four-core container, one MSAR fit costs:

| specification | n = 240 | n = 480 | n = 955 |
|---|---:|---:|---:|
| K = 2, p = 4 | 6.2 s | 7.9 s | 20.4 s |
| K = 3, p = 4 | 25.5 s | 69.7 s | 110.5 s |

The K = 3 expansion is intrinsic to the model as specified: switching is mean-only with
common AR coefficients, so the Hamilton filter still needs the lagged regime labels to
know which means to subtract, giving K^(p+1) = 243 expanded states. With roughly 700
monthly origins per target, the K = 3 robustness chains dominate the budget, so a complete
baseline run is a multi-hour job even with the fit cache, warm starts and four workers.

**Nothing was changed to make this faster.** No approved lag cap, regime count, window
length or horizon was altered, and the smoke namespace's reduced settings are never
thesis-facing. This is recorded as a Part 8 scheduling matter: the final run will need an
uninterrupted window, and the fit cache means an interrupted run resumes rather than
restarts.

### H9 — Decision D3 satisfied: Tsay validated against R `TSA::Tsay.test`

D3 requires the quadratic Tsay test to be validated "against reference values from a
recognized implementation such as R `TSA::Tsay.test` and against simulations". My first
attempt reported this as a gap because R was absent from the container. That was premature:
R 4.3.3 installs here once its build dependencies are present (`libcurl4-openssl-dev`,
`gfortran`, `libblas-dev`, `liblapack-dev` and `r-cran-mgcv`), and TSA 1.3.1 then builds
from source. **The cross-validation has been run and D3 is satisfied. No waiver is
needed.**

`TSA::Tsay.test` was run on six series, with both implementations reading the identical
stored arrays so they see the same inputs to the last bit:

| case | order | n | Python F | R F | Python p | R p |
|---|---:|---:|---:|---:|---:|---:|
| linear AR(2) | 2 | 250 | 1.655129 | 1.655 | 0.177353 | 0.1774 |
| linear AR(4) | 4 | 340 | 1.556422 | 1.556 | 0.118586 | 0.1186 |
| threshold AR(1) | 1 | 250 | 30.627872 | 30.63 | 7.992e-08 | 7.992e-08 |
| quadratic AR(2) | 2 | 250 | 1.081293 | 1.081 | 0.357652 | 0.3577 |
| **INDPRO growth, initial window** | 3 | 240 | 2.025393 | 2.025 | 0.063280 | 0.06328 |
| **GDPC1 growth, initial window** | 2 | 120 | 0.988630 | 0.9886 | 0.400923 | 0.4009 |

`TSA::Tsay.test` stores its statistic and p-value rounded to **four significant figures**,
so four significant figures is the finest agreement that can be asserted. The agreement is
exact at that precision on every case: the worst relative difference in the statistic is
2.7e-4, which is the rounding alone, and the 5% decision agrees on all six. Two of the six
cases are the real frozen INDPRO and GDPC1 growth series on their initial estimation
windows, so the agreement is established on the actual inputs the thesis uses and not only
on synthetic data.

The R reference values are stored in `tests/fixtures/tsay_reference_cases.json` together
with the R and TSA versions that produced them, so
`tests/validation/test_tsay_vs_r.py` (18 tests) runs in any container without R present.
The simulation half of D3 remains in `tests/validation/test_nonlinearity.py`, and the
Frisch–Waugh–Lovell algebraic equivalence check is retained as a third, independent
confirmation rather than as a substitute.

### H10 — Coverage matrix is generated, not asserted

`code/tools/coverage_matrix.py` holds the requirement register and verifies each row
mechanically: the named source file and symbol must exist in the codebase, the named
output artifact must exist and be non-empty under the evidence root, and the named test
node must actually be collected by pytest. It writes
`notes/claude/part5_coverage_matrix.csv`, `part5_coverage_summary.json` and
`part6_coverage_matrix.md`. Prose in the markdown is generated from the same verification
that produced the CSV, so the two cannot drift apart.

### H11 — Dependencies pinned (approved decision R2)

R2 approved "install and pin". `pyproject.toml` declared the dependencies but pinned
none of them, which leaves a recorded result untraceable to the library versions that
produced it. `code/requirements.lock.txt` now pins the exact set the Part 6 results were
produced with:

```
numpy 2.4.6        scipy 1.17.1       pandas 3.0.6
statsmodels 0.15.0 arch 8.0.0         matplotlib 3.11.2
pyarrow 26.0.0     psutil 7.2.2       joblib 1.6.0
PyYAML 6.0.1       tabulate 0.10.0    pytest 9.1.1
```

on Python 3.11.15. `environment_record()` now also records the lock file's SHA-256 beside
the versions actually loaded, so a drift between the pinned set and the running
environment appears in every run manifest instead of passing silently.
`tests/unit/test_dependencies.py` (18 tests) asserts the lock file exists, pins concrete
versions, covers every declared runtime dependency, and still matches what is installed.

R and TSA are recorded in the lock file as external and are needed only to regenerate the
Tsay reference values; the test that consumes them reads the stored fixture and needs
neither. The apt and CRAN commands to reproduce that environment are in the lock file.

### H12 — Corrected methodological implementation error: horizon-dependent origin truncation

**Found by the user in independent review of the pushed Part 6 code, 14 October 2026.**
This was the most consequential defect in Part 6 and it was mine, not a specification
ambiguity.

**The defect.** `forecasting/rolling.run_chain` built its origin set with
`rolling_origins(index, window_length, horizon=max(horizons))`. One fitted model serves
every requested horizon, so bounding the origin set by the **longest** horizon discarded
the late-sample origins at which a **shorter** horizon still had a realized target. With
the approved monthly horizons [1,3,6,12] and quarterly [1,2,4], every horizon inherited
the longest horizon's last origin.

**Verified impact on the approved sample**, measured directly from the frozen data:

| target | freq | h | last h-step target, before | after | forecasts lost |
|---|---|---:|---|---|---:|
| CPIAUCSL, UNRATE, INDPRO, FEDFUNDS, M2SL | M | 1 | 2025-09 | **2026-08** | 11 each |
| the same five | M | 3 | 2025-11 | 2026-08 | 9 each |
| the same five | M | 6 | 2026-02 | 2026-08 | 6 each |
| the same five | M | 12 | 2026-08 | 2026-08 | 0 |
| GDPC1 | Q | 1 | 2025Q3 | **2026Q2** | 3 |
| GDPC1 | Q | 2 | 2025Q4 | 2026Q2 | 2 |
| GDPC1 | Q | 4 | 2026Q2 | 2026Q2 | 0 |

**135 h-step forecasts were lost in total, 58 of them at the primary horizon.** This
contradicted Part 5 §9.4, which makes h=1 the primary exercise and the longer horizons
separate robustness analyses, and it silently undid the approved decision to retain the
2026M8 and 2026Q2 endpoints.

**Worst consequence: T4.9 was vacuous at the primary horizon.** The amendment created
T4.9 to quantify exposure to the two approved October 2025 LOCF cells. The CPI growth
observations that depend on the imputed October level are 2025-10 and 2025-11. Monthly
h=1 stopped at 2025-09, one month short, so **every target-side exposure flag was
necessarily false**: the diagnostic reported zero affected realized targets where the
correct answer is two. Verified numerically before and after.

**The fix.** `windows.estimation_origins` bounds the origin set by the **shortest**
requested horizon; `windows.targets_for` resolves each horizon's target, omitting only
those past the sample end; `windows.horizon_coverage` reports each horizon's own reach.
`run_chain` uses these, and `ChainResult.coverage_rows()` feeds a new per-horizon audit,
`output/forecasts/forecast_horizon_coverage.csv`, so a truncation at any horizon is
visible in the output rather than having to be inferred.

**Preserved, and asserted by test, not assumed:** rolling-window boundaries
(`window_end == origin_date`, `window_start` exactly `window_length-1` observations
earlier); no look-ahead; warm starts and their predecessor-hash cache keys; deterministic
STAR seeds keyed on series, model, specification and origin date; and horizon-specific
alignment (`target_position == origin_position + horizon`, with the actual value read from
that target date).

**Cache correctness, which the user also flagged.** The cache key identifies a fit by
data, specification, window and warm-start predecessor — deliberately not by the horizon
set, so decision T4's superset reuse works. But a payload written for a narrower horizon
set was being read for a wider request, and the missing horizon became a silent NaN. The
payload now records the horizons it covers and `_covers` refits when coverage is
insufficient; `cache_horizon_misses` is reported in the origin audit. Superset reuse is
numerically sound because a forecast at horizon h does not depend on which other horizons
were requested beside it: AR, ARMA and MSAR iterate or recurse deterministically, and the
STAR residual bootstrap draws one block of shocks per step from a seeded stream, so its
first h means are identical whether 3 or 12 steps were simulated. That prefix stability is
asserted directly, and a further test checks that a reused forecast equals a freshly
computed one to zero tolerance for all four model families.

**Other downstream effects.** T3.3, T3.3A (HLZ), T3.3B (DM-HLN), T3.4 (MCS), T3.5, T3.6,
T4.TP1 and T4.3 are all computed from the forecast rows, so they gain the recovered dates
automatically; no logic in them needed changing. T4.1, T4.2, T4.5, T4.6 and T4.8 each
request a single horizon, so they were never affected. T4.4 now records each horizon's own
evaluation span with an explicit note, because the horizons genuinely end on different
dates and a reader must not take the comparison for a common-sample one. T3.3 rows carry
their own first and last target date for the same reason.

**Regression tests added:** `test_horizon_coverage.py` (19),
`test_cache_horizons.py` (11), `test_locf_exposure_reach.py` (11).

