# Part 6 — Decisions register

**Status:** DECIDED BY USER on 2026-10-09, before any empirical result existed. These are fixed Part 6 implementation decisions.
**Authority:** `approved-specs/part5/` remains frozen and unmodified. Nothing here amends it. Where an item resolves an ambiguity, silence or undefined term in frozen Part 5, it is tagged **[UAIC]** — *user-approved implementation clarification* — and must be cited as such in Part 8/Part 9 wording, never as a change of approved methodology.
**Result-blind rule (CLAUDE.md §6):** every value below was fixed before results were seen and may not be revised because it changes an empirical outcome.
**Companion:** `part6_implementation_plan.md`. **Open blocker:** see §E (N1) and `data_discrepancy_2026-10-09.md`.

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
| **M3** | **Do not defer HLZ and do not wait for a user upload.** Retrieve the open-access Harvey–Leybourne–Zu (2025) JBES article (DOI `10.1080/07350015.2024.2418835`) **and** its official supplementary appendix, read both, and implement local demeaning, LRV construction, bandwidth/smoothing rules, reference distribution / finite-sample critical-value procedure and all other tuning choices **exactly as the authors state**. Generic Newey–West/HAC machinery may **never** be labelled HLZ. Record the article/supplement version or checksum used for validation. |
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

### N1 — BLOCKER: October 2025 is permanently missing from CPIAUCSL and UNRATE

The 2026-10-05 vintage returns a **complete monthly grid with no gaps and no duplicates** for every series, but **CPIAUCSL and UNRATE each contain exactly one missing value, both at 2025-10-01**. This is not an API artifact and no later vintage will repair it: during the 2025 federal shutdown the BLS could not collect the October 2025 reference-period data, the October 2025 CPI release was cancelled, and the October 2025 household survey — the source of the unemployment rate — was never collected and **cannot be collected retroactively**.

Frozen Part 5 assumes contiguous monthly series. It forbids backfilling and artificial interpolation (§2.1 criterion 6, §2.4) and it does not define how a permanent interior hole is handled. **The affected analysis is stopped and awaiting your decision** (CLAUDE.md §4). Full impact analysis and the options are in `data_discrepancy_2026-10-09.md`.

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
| **N1** | Handling of the permanent 2025-10 hole in CPIAUCSL and UNRATE | **Awaiting your decision.** Affected analysis stopped. Options in `data_discrepancy_2026-10-09.md`. Unblocked work continues meanwhile. |
| **M3** | HLZ article + supplementary appendix retrieval | **In progress.** Confirmed open access (CC-BY-NC-ND). The publisher and the Nottingham repository both sit behind a Cloudflare bot challenge that automated retrieval cannot pass; aggregator mirrors resolve to those same two URLs. Retrying alternative routes. HLZ will not be implemented from memory and no generic HAC substitute will be labelled HLZ. |
