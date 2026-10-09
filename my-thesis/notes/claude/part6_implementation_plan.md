# Part 6 — Implementation plan

**Status:** **APPROVED by the user on 2026-10-09**, subject to the decisions recorded in `part6_issues_and_decisions.md`. Coding has begun on all components not blocked by §3.1.
**Scope:** Part 6 only (build + validate). Part 7 (reproducibility demonstration) and Part 8 (final execution and analysis) are **not** started. When Part 6 is complete I stop and wait for approval (CLAUDE.md §13).
**Companions:** `part6_issues_and_decisions.md` (all approved decisions; IDs T1–T7, M1–M13, D1–D20, R1–R10, N1–N4) and `data_discrepancy_2026-10-09.md` (open blocker).
**Paths:** project root is `my-thesis/`; paths below are relative to it.
**Frozen Part 5 is unmodified.** Decisions tagged **[UAIC]** in the register are user-approved implementation clarifications of Part 5 ambiguities, not amendments.

---

## 0. What was read

- `CLAUDE.md` and every file in `approved-specs/part1/` … `part5/` (Part 5: 7 files; Parts 1–4: 12 files). `approved-specs/part9/` (recent-literature bank) exists but is outside the Parts 1–5 reading scope and was not used.
- The local branch was 78 commits behind `origin/claude/trusting-feynman-871wks`; fast-forwarded, no conflicts.

## 1. Repository and environment

| Item | State |
|---|---|
| Repo | `academia7`; thesis project in `my-thesis/`. Branch `claude/trusting-feynman-871wks`. |
| `code/`, `data/`, `output/`, `reports/` | Empty at plan time (`.gitkeep` only). No pre-existing code, as Comp §1 assumes. |
| `approved-specs/` | part1 (2), part2 (2), part3 (4), part4 (4), part5 (7), part9 (1). |
| `source-materials/` | Did not exist; created for the HLZ article when retrieved (CLAUDE.md §10: originals never modified). |
| Python | 3.11.15 |
| Installed and pinned (R2) | numpy 2.4.6, scipy 1.17.1, pandas 3.0.6, statsmodels 0.15.0, arch 8.0.0, matplotlib 3.11.2, pyarrow 26.0.0, plus pytest, pytest-cov, psutil, joblib, tabulate. Exact versions go into `code/requirements.lock` and into `output/logs/environment.json` on every run. |
| Machine | 4 cores, 15 GB RAM. |
| `FRED_API_KEY` | Supplied 2026-10-09. Stored **outside the repository** (session scratchpad, mode 600), read from the environment, never hard-coded, never logged, never committed. **Rotation recommended** once the frozen snapshot exists. |
| Frozen data | Not yet created. `--initialize-frozen` is approved (R1) and runs once the N1 decision is in, so the first frozen build is not immediately followed by a sample-rule change. |

## 2. Vintage verification performed before writing code

Direct read-only probes of the 2026-10-05 vintage (details and the full table in the register, N1–N4):

- **T6 cross-check passes (N3):** `vintage_dates=2026-10-05` and `realtime_start=realtime_end=2026-10-05` return identical row counts, first dates, last dates and last values for all seven series. The initializer additionally performs a full value-by-value comparison and halts on any material difference.
- **All approved start dates confirmed (N4).** INDPRO's pre-1947 history exists (from 1919M1) and is truncated to 1947M1 as specified.
- **FEDFUNDS raw last = 2026M9 (N2)**, not 2026M8 as the rationale text states. The operative endpoint rule still yields **2026M8**, so the approved endpoint stands; handled under T5(a) like UNRATE. Recorded so Part 9 does not repeat the inaccurate sentence.
- **Blocker found (N1):** CPIAUCSL and UNRATE are each permanently missing **2025-10**.

## 3. Contradictions, ambiguities, missing detail, risks — resolved

All seven tensions (T1–T7), thirteen methodological issues (M1–M13), twenty implementation details (D1–D20) and ten risks (R1–R10) are now decided; see the register. No contradiction between two authoritative files was found that would require the CLAUDE.md §3 stop.

### 3.1 Open blocker (work stopped on the affected components)

**N1 — October 2025 permanently missing from CPIAUCSL and UNRATE** (2025 shutdown; BLS cancelled the October CPI and never collected the October household survey, which cannot be collected retroactively). Frozen Part 5 assumes contiguous monthly series and prohibits backfilling and interpolation, but defines no rule for a permanent interior hole. Impact, options A–F and the four questions are in `data_discrepancy_2026-10-09.md`.

**Blocked until decided:** transformation and sample construction for CPI and UNRATE; their full-sample KPSS/ZA; the balanced monthly VAR sample; the CPI AR-lag robustness date set; anything consuming those.
**Not blocked:** everything else, because GDPC1, INDPRO, FEDFUNDS, M2SL and USREC are complete and the initial estimation window predates the hole by ~60 years, so no locked specification or stationarity decision is affected.

### 3.2 Closed dependency

**M3 — HLZ article and supplementary appendix: resolved 2026-10-09.** The supplement was downloaded from figshare; the article was supplied by the user after automated retrieval failed on every open-access route (Cloudflare bot challenge on both the publisher page and the Nottingham repository; all aggregators resolve to those two URLs). Both documents are held with checksums in `source-materials/hlz2025/`, and `PROVENANCE.md` there records every equation, kernel, bandwidth and critical-value rule used, with its page reference. The module is implemented and validated (§5.7). Nothing was taken from memory and no generic HAC estimator is labelled HLZ.

## 4. Architecture

```
code/
  run_all.py                 CLI: (default) baseline from frozen data | --initialize-frozen | --verify-vintage
                             | --refresh-data | --smoke-test | --stage NAME | --robustness | --resume
  pyproject.toml, requirements.lock
  configs/  baseline.yaml  smoke.yaml  series_catalog.yaml  thresholds.yaml   (all hashed into config_hash)
  src/thesis/
    core/           config.py  paths.py  provenance.py  seeds.py  schemas.py  cache.py
                    checkpoints.py  parallel.py  runtime.py  logging_utils.py
    data/           fred_client.py  frozen.py  manifest.py  loaders.py  vintage_audit.py  samples.py
    transforms/     growth.py  differences.py  level_reconstruction.py  lags.py
    diagnostics/    stationarity.py  decision_rule.py  nonlinearity.py  residual_tests.py  garch_diag.py
    specification/  ar_select.py  arma_select.py  star_spec.py  var_select.py  spec_registry.py
    models/         base.py  ar.py  arma.py  msar.py  star.py  var.py  arma_garch.py  status.py  flags.py
    forecasting/    windows.py  rolling.py  iterate.py  simulate.py  store.py
    evaluation/     losses.py  metrics.py  states.py  alignment.py  hlz.py  dm_hln.py
                    state_loss_regression.py  mcs.py  tp_sensitivity.py
    robustness/     transformation.py  cpi_lags.py  k3.py  horizons.py  var_compare.py  garch_diag.py
    reporting/      tables.py  figures.py  test_registry.py  failure_registry.py  equations.py
                    claim_matrix_schema.py
  tests/  unit/  integration/  validation/  fixtures/
```

Note `evaluation/state_loss_regression.py`, not `gw.py`: per **M1** the module and every output label name it an **ex-post state-dependent forecast-loss regression**.

**Core records.** `TestResult` (name, H0, statistic, reference distribution or bootstrap, p-value, 5% decision, implication, all tuning choices, provenance) is what every test returns, which is how the Part 5 §7.2 standardized presentation (jury R1-13) is guaranteed structurally. `FitRecord` (series, model, spec hash, window bounds, refit date, convergence, loglik, AIC/BIC, parameters, standard errors, start used, optimizer message, wall time, status, reason codes, raw diagnostics). `FailureEvent` (one T4.7 row). `DataGapEvent` — separate from `FailureEvent` per the N1 options, so no model is penalised for an external data outage.

**Engineering rules.** Workers write only their own shard; one process merges. Child seeds from `SeedSequence` keyed by a stable hash of (series, model, spec, origin), never by scheduling order. Single-threaded BLAS in workers. Cache entries as JSON/NPZ/Parquet, never pickle. Cache key (T4 superset): data-snapshot hash + series + transformation + model + spec hash + window start/end + refit date + dependency-aware code hash (D15) + config subtree hash + predecessor-solution hash for warm-start chains (R5). Checkpoints after each of the ten Comp §5 stages.

## 5. Traceability: Part 5 requirement → implementation

### 5.1 Data, frozen vintage, samples (Spec §2; Comp §2)

| Requirement | Code | Tests | Outputs |
|---|---|---|---|
| Programmatic retrieval; key from env only; raw levels; `vintage_dates=2026-10-05` primary with realtime cross-check (T6) | `data/fred_client.py::fetch_series` | mocked-request params; key never persisted or logged; vintage equals 2026-10-05; both request forms compared value-by-value | `data/frozen/fred_vintage_2026-10-05/<ID>.csv` + `<ID>.meta.json` |
| Per-file metadata and SHA-256; one immutable master manifest; refuse overwrite (D13) | `data/frozen.py::initialize_frozen`, `data/manifest.py` | refuses when a manifest exists; manifest covers every file | `MANIFEST.json`; T2.0A |
| Preserve raw exactly, truncate only when building the sample; report raw-last and usable-last (T5) | `data/frozen.py`, `data/samples.py` | UNRATE/FEDFUNDS 2026M9 preserved raw, excluded from the sample | T2.0A, T2.1 |
| Hash verification before estimation; no internet in the default run | `data/frozen.py::verify_frozen`; network guard in `run_all.py` | tamper detection; default run makes no network call | `output/logs/hash_verification.csv` |
| Expected ranges; stop on unexplained discrepancy | `data/samples.py::check_expected_ranges` | mismatch halts and writes a note | `notes/claude/data_discrepancy_<date>.md` |
| Start dates, INDPRO truncation, endpoint 2026M8, GDP 2026Q2, VAR from 1959M1 | `data/samples.py` | boundary tests; no backfill; no interpolation | `output/data_audit/sample_audit.csv` |
| Local transformations, 400/1200 annualization | `transforms/growth.py`, `transforms/differences.py` | known values; annualization factors; determinism from frozen input | `output/data_audit/transformed_series.parquet` |
| Concept→series incl. exclusions | `reporting/tables.py::concept_to_series` from `configs/series_catalog.yaml` | catalog covers every Part 5 exclusion | T2.0 |
| USREC evaluation-only | import boundary: `models/`, `forecasting/`, `specification/` may not import `evaluation.states` or load USREC | static import test; perturbing USREC leaves forecasts byte-identical | — |
| Audit reconstruction; refresh namespace (D16) | `data/vintage_audit.py`; `run_all.py --refresh-data` | audit writes to `data/audit/<date>/`; refresh never touches frozen or `output/` | `output/manifests/vintage_audit.csv` |

### 5.2 Stationarity and transformation decision (Spec §3; T2, T7, D9)

| Requirement | Code | Tests | Outputs |
|---|---|---|---|
| ADF (BIC, cap 12/4, intercept, 5%) | `diagnostics/stationarity.py::adf` → `TestResult` | seeded random-walk vs AR(1); lag cap honoured | T2.2 |
| KPSS (intercept, library auto bandwidth recorded) | `::kpss`; truncated-p flag | seeded stationary/nonstationary | T2.2 |
| ZA on UNRATE/FEDFUNDS levels: intercept+trend, trim 0.15, BIC, **max lag 12**; critical values matching the implemented specification, **never a hard-coded −5.08** (D9) | `::zivot_andrews` | known-break recovery; critical-value source recorded | T2.2; F2.1 break marker |
| ADF/KPSS on log level and on the growth rate (§3.3), **plus labelled constant+trend diagnostics** (T2) | `::transformation_verification` | trend variants cannot alter any baseline decision | T2.2 |
| Decision rule on the **initial window** = first 240/120 observations (T7); full-sample confirmation; no retroactive change; alternative becomes mandatory robustness (M5) | `diagnostics/decision_rule.py` | table-driven over all ADF×KPSS×ZA branches; decision uses only the initial window; disagreement sets the robustness flag | T2.2; `output/diagnostics/transformation_decision.json` |
| Level reconstruction when modeled in differences; common-scale level errors (M6) | `transforms/level_reconstruction.py` | round-trip; multi-step cumulation | T4.1 level columns |

### 5.3 Nonlinearity evidence (Spec §4; D3, D4)

| Requirement | Code | Tests | Outputs |
|---|---|---|---|
| **Tsay (1986) quadratic test** with all unique quadratic lag terms and the nested/orthogonalized auxiliary F test (D3) | `diagnostics/nonlinearity.py::tsay_test` | validated against R `TSA::Tsay.test` reference values **and** simulations; size ≈ 5% under linear AR; power against LSTAR/bilinear | T2.3 |
| LST/Teräsvirta sequence with **H02/H03/H04 labels, auxiliary equations and the LSTAR/ESTAR rule exactly as published** (D4); monthly d ∈ 1..6, quarterly 1..4; no multiplicity correction | `::lst_linearity_by_delay`, `::select_delay_and_type` | recovers delay and type on simulated LSTAR/ESTAR; deterministic tie rule; all delay results stored | T2.4 |
| No naive MS chi-square LR test | no such function; guard test forbids adding one | `test_no_ms_lr_function` | note in T2.4 |
| Nonlinearity result does not gate model entry (§4.4) | registry lists all four models unconditionally | MSAR/STAR run even when linearity is not rejected | interpretation field only |

### 5.4 Models (Spec §5–§6; D5–D8, M4, M8–M10)

| Model | Implementation | Validation |
|---|---|---|
| **AR(p)** | OLS with intercept; order chosen on the initial window by BIC on a **common effective sample** (D2), then the lowest-BIC candidate passing the **primary Ljung–Box** check (D1), else BIC minimum flagged "diagnostically weak"; order fixed; parameters refit every origin | matches statsmodels `AutoReg`; selection-rule table test incl. the all-fail branch; companion-matrix stability |
| **ARMA(p,q)** | Gaussian ML (state space); stationarity and invertibility enforced; grid minus (0,0); BIC + whiteness; **q=0 / p=0 allowed and flagged** (M4) | recovers simulated orders and parameters; grid exclusion; flag logic |
| **MSAR (K=2)** | Own Hamilton filter over the expanded state; regime means, common AR, common variance; **logistic/simplex transition probabilities, log σ** (D5); deterministic multi-starts with every start recorded (D6); warm start then deterministic fallback; regimes ordered by mean; transition matrix, smoothed probabilities, occupancy, expected durations; **exact h-step conditional mean** | log-likelihood equals statsmodels `MarkovAutoregression` at identical parameters; parameter recovery; label-switching; h-step equals Monte-Carlo benchmark |
| **STAR** | Conditional NLS (linear coefficients by OLS given γ, c); **scale-free parameterization on `(z−c)/s_z`, logistic for LSTAR and squared distance for ESTAR, γ > 0 in [1e-3, 1e3], c ∈ [min z, max z]** (D5); delay and type fixed from the initial window; warm starts; transition-function range/SD recorded | recovers simulated LSTAR/ESTAR; G ∈ [0,1]; reduces to AR when G is constant; flag logic |
| **K=3 MSAR** | Same structure and lag; **all six targets, every origin, h=1 headline plus approved longer horizons from the same fits** (M8) | simulated 3-state recovery; filter agrees with brute-force enumeration at small T |
| **VAR(p)** | 240-month rolling; p ∈ {1,2,3} by BIC on the **initial VAR window**; lag fixed; refit each origin; stability required; h = 1, 3, 6, 12; compared on **identical common target dates** (M10) | matches statsmodels VAR; companion-eigenvalue stability |
| **ARMA-GARCH(1,1)** | Custom Gaussian quasi-ML; trigger = ARCH-LM rejection on the **selected ARMA's initial-window residuals**; **full rolling OOS chain with mean forecasts**; **excluded from the horse race and from MCS** (M9) | recovers simulated GARCH(1,1); stationarity constraint |
| Status classification | `models/status.py` + `models/flags.py`: Adequate / Fragile / Failed from the **D8-approved** rules only. Convergence per **D7** (bound contact is fragility, not non-convergence). Parameter uncertainty **reported directly**, no invented SE threshold. `EXTREME_FORECAST` is a plotting/fragility warning that never deletes a forecast. | one test per reason code; `test_no_silent_fallback` |

### 5.5 In-sample adequacy and credibility (Spec §7–§8)

| Requirement | Code | Outputs |
|---|---|---|
| loglik, AIC, BIC, in-sample RMSE/MAE, Ljung–Box **12/24 monthly, 4/8 quarterly with D1 df conventions**, ARCH-LM (12/4), Jarque–Bera, per series/model/refit | `diagnostics/residual_tests.py` | T3.1 |
| Standardized H0/statistic/distribution/p/decision/implication for every test | `reporting/test_registry.py` | `T-DIAG` (D17) |
| MSAR credibility; STAR credibility | `models/flags.py` | T3.2 |
| Policy-rate dedicated diagnostic (§8.1, jury P-03) | `reporting/tables.py::policy_rate_diagnostic` | `T3.2-FF` (D17) |
| Fitted-vs-observed; residual ACF with 95% bands; regime and transition plots | `reporting/figures.py` | F3.1, F3.2, F3.3 |

### 5.6 Pseudo-out-of-sample design (Spec §9; Comp §3, §5–§8; M2)

| Requirement | Code | Tests |
|---|---|---|
| Rolling 240/120; origins; target alignment | `forecasting/windows.py` | window boundaries; target alignment; constant window length |
| No future data in predictors | `forecasting/rolling.py` sees only `y[:origin]` | property test: mutate everything after the origin → identical forecast |
| Every-origin re-estimation, discrete spec fixed from the initial window | `forecasting/rolling.py::run_chain` | params refit each origin; spec never re-searched |
| Iterated multi-step from one fit. AR/ARMA/VAR analytic; **MSAR exact recursion**; **STAR residual-bootstrap conditional mean, 5,000 paths, deterministic child seeds, h=1 analytic, skeleton only as a labelled diagnostic** (M2) | `forecasting/iterate.py`, `forecasting/simulate.py` | AR(1) closed form; MSAR exact vs simulation; STAR bootstrap convergence and seed determinism; path count recorded |
| Warm starts, cache, checkpoints, resume | `core/cache.py`, `core/checkpoints.py` | key determinism; key changes with each element; resume refits nothing valid; warm-chain invalidation |
| Parallelism without shared writes; schedule-independent seeds | `core/parallel.py`, `core/seeds.py` | parallel equals serial; seeds independent of schedule |
| Failure and data-gap handling | `core/schemas.py`, `reporting/failure_registry.py` | failed fit emits a record and other models continue; `DataGapEvent` never counted as model failure |
| Runtime reporting | `core/runtime.py` | wall/CPU time, fits attempted, cache reuse, failures, peak memory |

### 5.7 Forecast evaluation (Spec §10; M1, M7, D10–D12)

| Requirement | Code | Outputs |
|---|---|---|
| RMSE, MAE, OOS R² vs AR; attempted/valid/failed origins; `T_common` and observations removed by alignment (M7) | `evaluation/metrics.py`, `evaluation/alignment.py` | T3.3 |
| **HLZ** squared and absolute loss, five pairs, every tuning choice recorded — implemented strictly from the article and supplement (M3) | `evaluation/hlz.py` | T3.3 columns, T3.3A |
| **DM-HLN** secondary, Newey–West/Bartlett truncation h−1 (D10), kept separate from HLZ | `evaluation/dm_hln.py` | T3.3B incl. agreement flag |
| **MCS** method `R`, stationary bootstrap, 5,000 reps, block length `ceil(sqrt(T_common))`, fixed seed, both losses, 90% and 95%; intersection of finite-loss dates across included models; **"unavailable" when undefined**; ARMA-GARCH excluded (D11, M7, M9) | `evaluation/mcs.py` | T3.4 |
| State RMSE/MAE/mean loss difference for expansion, recession, turning window, outside | `evaluation/states.py` | T3.5 |
| **Ex-post state-dependent forecast-loss regression** (M1): α, β_rec, β_turn, individual p-values, joint Wald over all three, separate state-dependence Wald over the two slopes, HAC rule, state cell N, descriptive state RMSE/MAE, availability flag per **M12** | `evaluation/state_loss_regression.py` | T3.5 |
| Peak vs trough at h=1 under the baseline window | `evaluation/states.py::peak_trough_split` | T3.6 |
| Turning masks monthly ±1/±3/±6 and quarterly 0/±1/±2; unions; boundary clipping; overlap across categories permitted (M11); baseline never replaced | `evaluation/states.py::turning_masks` | T4.TP1 |
| Sensitivity classification `unchanged`/`weakened`/`reversed`/`unavailable` plus `support_change` (M13) | `evaluation/tp_sensitivity.py` | T4.TP1 |

### 5.8 Robustness (Spec §11) — written only under `output/robustness/`

| Threat | Code | Design |
|---|---|---|
| UNRATE/FEDFUNDS transformation | `robustness/transformation.py` | alternative transformation through the full chain; modeled-target inference plus common-scale level errors (M6); no break-dummy model (M5) |
| CPI AR-lag benchmark | `robustness/cpi_lags.py` | **AR only** at p = 1, 3, 6, 12; ARMA/MSAR/STAR at approved baseline specs and caps; nonlinear models compared against each alternative AR benchmark on common dates (T1) |
| Two regimes imposed | `robustness/k3.py` | K=3 for all six targets, every origin (M8); §11.1 retention rule encoded |
| Horizon | `robustness/horizons.py` | monthly 1/3/6/12, quarterly 1/2/4 from stored forecasts |
| Omitted macro information | `robustness/var_compare.py` | per M10 |
| Conditional variance | `robustness/garch_diag.py` | per M9 |
| Failure misleads figures | `reporting/figures.py` | failure panels, no clipping (D19) |
| Turning-window width | `evaluation/tp_sensitivity.py` | per §5.7 |
| Window length, U.S. sample | not implemented by design | Part 5 states these are documented design assumptions; note strings carry the statement |

### 5.9 Failure registry (Outputs §9)

`reporting/failure_registry.py` builds T4.7 from `FitRecord` flags: series, model, refit date, horizon, category, reason code from the fixed list (`NONCONVERGENCE, NONFINITE, SINGULAR_COV, UNSTABLE_AR, EMPTY_REGIME, TRANSITION_BOUNDARY, STAR_GAMMA_BOUND, STAR_THRESHOLD_EXTREME, RESIDUAL_AUTOCORR, EXTREME_FORECAST`), raw diagnostic, whether the forecast was retained, whether the figure was separated. Data gaps are recorded separately and are not model failures.

### 5.10 Figures, tables, provenance, logs

Figure helper enforces unit labels, sample dates, model labels, NBER shading, no multi-series squeeze, separate failure panels, no clipping, 95% ACF bands. Tables carry numeric p-values plus a stars column at 10/5/1% (D20). No cross-correlation figure is produced. `core/provenance.py` appends run ID, data-snapshot hash, code commit SHA, config hash and creation timestamp to every table, with sidecar provenance JSON for figures; `output/manifests/run_manifest.json` ties the run to the 2026-10-05 vintage, manifest hash, commit SHA and dirty flag, config and environment. Thesis-facing runs refuse to proceed with a dirty tree (D14).

## 6. Implementation confirmations

As in the approved plan, with these decision-driven changes: the state regression is an **ex-post state-dependent forecast-loss regression**, not a Giacomini–White conditional predictive-ability test (M1); **STAR h > 1 uses residual-bootstrap simulation** (M2); **MSAR h-step uses the exact recursion**; **HLZ comes strictly from the article and supplement** (M3); **ARMA-GARCH runs the full rolling chain but stays out of the horse race and MCS** (M9); **MCS uses method R, stationary bootstrap, `ceil(sqrt(T_common))`** (D11); **CPI lag robustness varies the AR benchmark only** (T1); **no invented eligibility percentage, no invented small-cell cutoff, no invented SE or near-unit-root thresholds** (M7, M12, D8).

## 7. Required outputs → generating code

Unchanged from the approved plan, with T3.5's regression relabelled per M1 and T4.2 relabelled "CPI AR-lag benchmark robustness" per T1. Every ID in `part5_required_outputs_specification.md` (T2.0, T2.0A, F2.0, T2.1, T2.2, F2.1, T2.3, T2.4, T2.5, T3.1, T3.2, F3.1–F3.3, T3.3, T3.3A, T3.3B, T3.4, F3.4, F3.5, T3.5, T3.6, T4.TP1, F3.6, T4.1–T4.7, claim matrix, logs) plus provisional `T3.2-FF` and `T-DIAG` has a named generator and output path.

## 8. Reproducibility tests (Comp §15) → test modules

Unchanged from the approved plan: `test_data_frozen.py`, `test_transforms.py`, `test_windows_alignment.py`, `test_usrec_isolation.py`, `test_rolling_reestimation.py`, `test_cache_keys.py`, `test_level_reconstruction.py`, `test_hlz.py` (blocked on M3 retrieval), `test_dm_hln.py`, `test_state_loss_regression.py`, `test_turning_masks.py`, `test_mcs_inputs.py`. Scientific validation uses seeded simulations with known truth for AR, ARMA, MS-AR (K=2,3), LSTAR/ESTAR, GARCH(1,1) and VAR, cross-checks against statsmodels where an equivalent exists, the R `TSA::Tsay.test` reference comparison (D3), and test-size checks under simulated nulls.

## 9. Build order

| Step | Content | Gate | State |
|---|---|---|---|
| 0 | Environment, lock file, package skeleton, config/provenance/seeds/cache/checkpoints core | core unit tests | in progress |
| 1 | Data layer: FRED client, frozen init/verify, manifest, samples, transforms | data tests on mocked and seeded data | not blocked except CPI/UNRATE sample rules (N1) |
| 2 | Diagnostics: ADF/KPSS/ZA, decision rule, residual tests, Tsay, LST | validation simulations plus the R reference comparison | not blocked |
| 3 | Specification: AR, ARMA, STAR delay/type, VAR lag | selection-rule tests | not blocked |
| 4 | Models: AR, ARMA, MSAR (K=2,3), STAR, VAR, ARMA-GARCH; status/flags | recovery and cross-check tests; early runtime benchmark | not blocked |
| 5 | Forecasting engine: windows, chains, warm starts, cache, checkpoints, parallel, STAR bootstrap | alignment, no-look-ahead, resume, seed tests | not blocked |
| 6 | Evaluation: metrics, alignment, states/masks, DM-HLN, state-loss regression, MCS; **HLZ done** | evaluation tests | HLZ complete (39 tests); rest not started |
| 7 | Robustness modules | integration tests | CPI-lag date set pending N1 |
| 8 | Reporting: tables, figures, registries, provenance, logs, full CLI | schema and provenance tests | not blocked |
| 9 | Smoke test on **INDPRO** (monthly, complete) and **GDPC1** (quarterly, complete) | all stages run; outputs only in `smoke_output/`; every artifact carries provenance; reviewed for completeness only, never for ranking (R8) | needs frozen data |

**Smoke-test target choice:** Comp §10 requires one monthly and one quarterly target. INDPRO and GDPC1 are used because both are complete, so the smoke test neither depends on nor prejudges the N1 decision. The monthly VAR block loads all five monthly series but forecasts only the smoke subset.

**Part 6 is complete when** all unit, integration and validation tests pass; every output ID has a generator exercised by the smoke test; and the N1 decision is implemented. HLZ is done. No full thesis-baseline run is performed in Part 6. Then I stop for approval before Part 7.

## 10. What I will not do

Change variables, transformations, windows, lags, regimes, horizons, tests or robustness specifications; add MSSTAR, Clark–West/Clark–McCracken, Amisano–Giacomini, polynomial models or nowcasting; substitute a generic HAC estimator for HLZ; label the ex-post state regression as Giacomini–White; fall back silently after a failed fit; interpolate or backfill the 2025-10 hole; invent an eligibility percentage, small-cell cutoff or threshold that the register rejected; run the full baseline or any Part 7/8 task; choose anything because it improves a result. Any further change I judge necessary comes to you first with options.
