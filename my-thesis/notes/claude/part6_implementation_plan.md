# Part 6 — Implementation plan (for approval)

**Status:** PLAN ONLY. No research code written. Stops here until you approve (CLAUDE.md §13).
**Scope:** Part 6 only (build + validate). Part 7 (reproducibility demonstration) and Part 8 (final execution/analysis) are not started.
**Companion:** `part6_issues_and_decisions.md` (IDs such as M3, D8, T1 refer to it).
**Paths:** project root is `my-thesis/`; all paths below are relative to it.

---

## 0. What I did

- Read `CLAUDE.md` and every file in `approved-specs/part1/` … `part5/` (Part 5: 7 files; Parts 1–4: 12 files). `approved-specs/part9/` also exists (literature bank); it is outside the Part 1–5 reading scope and I did not use it.
- My local branch was 78 commits behind `origin/claude/trusting-feynman-871wks` (that is where your approved specs live). I fast-forwarded it; no conflicts, nothing overwritten.

## 1. Repository and environment inspection

| Item | Finding |
|---|---|
| Repo | Single git repo `academia7`; thesis project in `my-thesis/`. |
| `code/`, `data/`, `output/`, `reports/` | Empty (`.gitkeep` only). **No code exists**, as the spec assumes. |
| `approved-specs/` | part1 (2), part2 (2), part3 (4), part4 (4), part5 (7), part9 (1) files. |
| `source-materials/` | Does not exist (CLAUDE.md §10 mentions it; HLZ paper would go there — M3). |
| Python | 3.11.15. Installed: PyYAML, Jinja2, requests only. **numpy/pandas/scipy/statsmodels/matplotlib/pytest are not installed** (R2). A dry-run install resolves fine. |
| Machine | 4 cores, 15 GB RAM. |
| `FRED_API_KEY` | **Not set** (R1). The FRED host is reachable from the container. |
| Frozen data | None yet. `data/frozen/` does not exist. |

## 2. My understanding of the approved methodology

**Question.** When U.S. macro relationships are unstable, do state-dependent nonlinear models forecast better than appropriately specified classical benchmarks, in a way that survives threat-based robustness? An unfavourable answer is a valid result.

**Data (frozen).** FRED/ALFRED vintage **2026-10-05**, raw levels, SHA-256 manifest, no internet in the default run. Targets: GDPC1 (quarterly, 400·Δln), CPIAUCSL / INDPRO / M2SL (monthly, 1200·Δln), UNRATE and FEDFUNDS (level or first difference by a predeclared rule), USREC (evaluation only, never a regressor). Starts 1947Q1 / 1947M1 / 1948M1 / 1954M7 / 1959M1 / INDPRO truncated to 1947M1; monthly end 2026M8, GDP end 2026Q2; VAR 1959M1–2026M8.

**Transformation rule.** ADF (BIC, cap 12/4, intercept), KPSS (intercept), Zivot–Andrews (break in intercept+trend, trim 15%, BIC) on UNRATE/FEDFUNDS levels. The decision uses the **initial estimation window**; full-sample tests only confirm or trigger a mandatory robustness check, never retroactively change the baseline.

**Pre-estimation evidence.** Tsay (1986) on the AR residual structure; Luukkonen–Saikkonen–Teräsvirta / Teräsvirta (1994) delay and LSTAR/ESTAR sequence. No Markov-switching LR test (nonstandard). Nonlinearity evidence affects **interpretation only**, never which models enter the horse race.

**Models.** AR(p) (BIC then Ljung–Box screen; p ≤ 12 monthly / 4 quarterly), ARMA(p,q) (grid 0–4 monthly, 0–2 quarterly; BIC + whiteness; stationarity and invertibility), MSAR (Hamilton: regime-specific mean, common AR, common variance, K=2; lag = AR lag capped at 4), STAR (LSTAR/ESTAR, delay from the specification stage, lag capped 4 monthly / 2 quarterly). ARMA-GARCH(1,1) only as a variance **diagnostic** when ARCH-LM rejects. No polynomial trend model, no MSSTAR, no silent fallback.

**Experiment.** Rolling windows (240 monthly / 120 quarterly). **Discrete specification fixed once from the initial window; parameters re-estimated at every origin.** Iterated multi-step forecasts; h=1 baseline; robustness monthly 3/6/12, quarterly 2/4. Warm starts + caching + checkpointing + parallelism for speed only.

**Evaluation.** RMSE, MAE, OOS R² vs AR; **Harvey–Leybourne–Zu (2025) primary** pairwise test (squared and absolute loss; AR–ARMA, AR–MSAR, AR–STAR, ARMA–MSAR, ARMA–STAR); DM-HLN secondary (disagreement stays visible, HLZ prevails); Model Confidence Set (90%/95%); state-conditioned RMSE/MAE and Giacomini–White regression on `REC_t`, `TURN_t`; turning window ±3 months / ±1 quarter baseline with mandatory ±1/±6 and 0/±2 sensitivity.

**Adequacy and failure.** Every fit is classified Adequate / Fragile / Failed with fixed reason codes; failures are recorded and never replaced.

**Robustness.** UNRATE/FEDFUNDS alternative transformation; CPI lag 1/3/6/12; K=3 MSAR; horizons; monthly 5-variable VAR; ARMA-GARCH diagnostic; turning-window widths; failure-aware figures. Baseline and robustness kept strictly separate.

**Provenance.** Every artifact carries run ID, data-snapshot hash, code commit SHA, config hash, timestamp (+ cutoff date and vintage via the manifest).

## 3. Contradictions, ambiguities, missing detail, risks

Full register with options is in `part6_issues_and_decisions.md`. Summary:

- **No hard contradiction** between authoritative files requiring a stop. **Seven tensions/undefined terms** (T1–T7), of which the important ones are: CPI lag robustness vs the MSAR/STAR lag cap (T1); "initial estimation window" is never defined (T7); the raw UNRATE series extends one month beyond the 2026M8 endpoint (T5).
- **13 methodological issues** (M1–M13), of which the substantive ones are: Giacomini–White uses target-date states that are not known at the origin (M1); naive iteration of STAR is not the conditional mean (M2); **HLZ must follow the paper exactly and I do not have it (M3)**; the ARMA grid contains pure-AR and pure-MA models (M4); handling of failed origins in paired tests and MCS (M7).
- **20 missing implementation details** (D1–D20) with proposed defaults, including a table of numeric thresholds that Part 5 uses but never numbers (D8).
- **10 technical risks** (R1–R10), most importantly: no API key (R1), no libraries installed (R2), runtime (R3), library gaps for out-of-sample Markov forecasts and ARMA-GARCH (R4), path-dependent warm starts (R5).

## 4. Architecture

All code under `code/`, as Comp §4 prescribes.

```
code/
  run_all.py                 CLI: (default) baseline from frozen data | --initialize-frozen | --refresh-data
                             | --verify-vintage | --smoke-test | --stage NAME | --robustness | --resume
  pyproject.toml, requirements.lock
  configs/  baseline.yaml  smoke.yaml  series_catalog.yaml  thresholds.yaml  (all hashed into config_hash)
  src/thesis/
    core/           config.py  paths.py  provenance.py  seeds.py  schemas.py  cache.py
                    checkpoints.py  parallel.py  runtime.py  logging_utils.py
    data/           fred_client.py  frozen.py  manifest.py  loaders.py  vintage_audit.py  samples.py
    transforms/     growth.py  differences.py  level_reconstruction.py  lags.py
    diagnostics/    stationarity.py  decision_rule.py  nonlinearity.py  residual_tests.py  garch_diag.py
    specification/  ar_select.py  arma_select.py  star_spec.py  var_select.py  spec_registry.py
    models/         base.py  ar.py  arma.py  msar.py  star.py  var.py  arma_garch.py  status.py  flags.py
    forecasting/    windows.py  rolling.py  iterate.py  store.py
    evaluation/     losses.py  metrics.py  states.py  alignment.py  hlz.py  dm_hln.py  gw.py  mcs.py
                    tp_sensitivity.py
    robustness/     transformation.py  cpi_lags.py  k3.py  horizons.py  var_compare.py  garch_diag.py
    reporting/      tables.py  figures.py  test_registry.py  failure_registry.py  equations.py
                    claim_matrix_schema.py
  tests/  unit/  integration/  validation/ (seeded simulations)  fixtures/
```

**Core objects.** `TestResult` (name, H0, statistic, reference distribution/bootstrap, p-value, 5% decision, implication, tuning choices, provenance) is the one record every test returns — this is how the §7.2 standardized presentation (R1-13) is guaranteed. `FitRecord` (series, model, spec hash, window start/end, refit date, converged, loglik, AIC/BIC, parameters, SEs, start used, optimizer message, wall time, status, reason codes, raw diagnostics). `FailureEvent` (T4.7 row).

**Engineering rules.** Workers write only their own shard; one process merges (no concurrent writes to one path). Child seeds come from `SeedSequence` keyed by a stable hash of (series, model, spec), not by scheduling order. Single-threaded BLAS in workers. Cache entries stored as JSON/NPZ/Parquet (no pickle). Cache key = data-snapshot hash + series + transformation + model + spec hash + window start/end + refit date + code hash (D15) + config subtree hash + predecessor-solution hash (warm-start chain, R5). Checkpoints after each of the ten stages in Comp §5 as `cache/checkpoints/<stage>.json` (inputs hash, outputs hash, status), so a failed run resumes without repeating valid work.

## 5. Traceability: Part 5 requirement → implementation

Columns: **Code** (module/function) · **Model/procedure** · **Tests** · **Outputs**. Robustness and logs are called out where they apply.

### 5.1 Data, frozen vintage, samples (Spec §2; Comp §2; Rationale)

| Requirement | Code | Tests | Outputs |
|---|---|---|---|
| Programmatic FRED/ALFRED retrieval, `FRED_API_KEY` from env only, raw levels, vintage 2026-10-05 | `data/fred_client.py::fetch_series(series_id, realtime_start, realtime_end, units='lin')`; never logs the key | `test_fred_client_mocked` (request params, key never persisted), `test_vintage_date_is_2026_10_05` | `data/frozen/fred_vintage_2026-10-05/<ID>.csv` + `<ID>.meta.json` |
| Frozen files + per-file metadata (ID, params, source, title, frequency, units, SA, vintage, retrieval timestamp, first/last obs, row count, SHA-256) | `data/frozen.py::initialize_frozen()`, `data/manifest.py::write_manifest()` (refuses if manifest exists) | `test_initialize_refuses_overwrite`, `test_manifest_contains_all_hashes` | master manifest `data/frozen/.../MANIFEST.json`; `output/manifests/frozen_manifest.csv` (T2.0A) |
| Verify hashes before any estimation; no internet in default run | `data/frozen.py::verify_frozen()`; `run_all.py` guard that socket access is disabled in default mode | `test_hash_verification_detects_tamper`, `test_default_run_makes_no_network_calls` | `output/logs/hash_verification.csv` |
| Expected start/end dates; stop and save discrepancy | `data/samples.py::check_expected_ranges()` (expected table in config) | `test_expected_endpoints_pass`, `test_endpoint_mismatch_halts_and_writes_note` | `notes/claude/data_discrepancy_<date>.md` (on failure) |
| Start-date harmonization, INDPRO truncated 1947M1, common monthly end 2026M8, GDP end 2026Q2, VAR from 1959M1 | `data/samples.py::build_target_samples()`, `::var_common_sample()` | `test_sample_boundaries`, `test_var_sample_starts_1959M1`, `test_no_backfill_no_interpolation` | `output/data_audit/sample_audit.csv` (T2.1), F2.0 data |
| Local transformations, annualization 400/1200 | `transforms/growth.py::annualized_logdiff(x, k)`; `transforms/differences.py::first_diff` | `test_annualization_factors`, `test_logdiff_known_values`, `test_transform_from_frozen_is_deterministic` | `output/data_audit/transformed_series.parquet` |
| Concept→series table incl. excluded candidates | `reporting/tables.py::concept_to_series()` from `configs/series_catalog.yaml` | `test_catalog_covers_all_spec_exclusions` | T2.0 |
| USREC evaluation-only | import-boundary rule: `models/`, `forecasting/`, `specification/` may not import `evaluation.states` or load USREC | `test_usrec_not_imported_by_models` (static), `test_forecasts_invariant_to_usrec` (perturb USREC → byte-identical forecasts) | — |
| Optional audit reconstruction from ALFRED | `data/vintage_audit.py::verify_vintage()` (`--verify-vintage`): writes to `data/audit/<date>/`, compares hashes, never overwrites | `test_audit_writes_elsewhere` | `output/manifests/vintage_audit.csv` |
| Refresh | `run_all.py --refresh-data` → `data/refreshed/<date>/`, outputs to `output_refreshed/<date>/` | `test_refresh_never_touches_frozen_or_output` | separate namespace |

### 5.2 Stationarity and transformation decision (Spec §3)

| Requirement | Code | Tests | Outputs |
|---|---|---|---|
| ADF (BIC, cap 12/4, intercept, 5%) | `diagnostics/stationarity.py::adf()` → `TestResult` | validated on seeded random walk / AR(1); lag-cap test | T2.2 |
| KPSS (intercept, automatic bandwidth recorded, 5%) | `::kpss()`; flags truncated p-values (D9) | seeded stationary/non-stationary cases | T2.2 |
| Zivot–Andrews on UNRATE/FEDFUNDS levels (break in intercept+trend, trim 15%, BIC); break date reported | `::zivot_andrews()`; critical-value comparison in addition to library p-value | known-break simulation recovers break date within tolerance; statistic vs published critical value | T2.2; F2.1 break marker |
| ADF/KPSS on log level and on growth rate for GDP/CPI/INDPRO/M2 (§3.3) | `diagnostics/stationarity.py::transformation_verification()` | — | T2.2 |
| Decision rule on **initial window**, full-sample confirmation, no retroactive change, alternative retained as mandatory robustness | `diagnostics/decision_rule.py::decide_transformation(initial_window_results)` and `::full_sample_agreement()` | table-driven test of all ADF×KPSS×ZA combinations (rules 1–3), `test_decision_uses_only_initial_window`, `test_disagreement_sets_robustness_flag` | T2.2 (decision + reason), `output/diagnostics/transformation_decision.json` |
| Level forecasts reconstructed when modeled in differences | `transforms/level_reconstruction.py` | `test_level_reconstruction_roundtrip`, multi-step cumulative check | F2.1-style policy figures; T4.1 level metrics (M6) |

### 5.3 Nonlinearity evidence (Spec §4)

| Requirement | Code | Tests | Outputs |
|---|---|---|---|
| Tsay (1986) after fitting the selected AR on the initial window (D3) | `diagnostics/nonlinearity.py::tsay_test()` | size ≈ 5% under simulated linear AR; power against simulated LSTAR/bilinear | T2.3 |
| LST/Teräsvirta linearity per delay, delay selection, H04/H03/H02 LSTAR-vs-ESTAR (D4); monthly d∈1..6, quarterly 1..4; no multiplicity correction | `::lst_linearity_by_delay()`, `::select_delay_and_type()` | recovers delay/type on simulated LSTAR and ESTAR; deterministic tie-break | T2.4 |
| No naive MS chi-square LR test; limitation stated | no such function exists; `reporting/` note string attached to T2.4 | `test_no_ms_lr_function` (guards against accidental addition) | note in T2.4 |
| Nonlinearity result does not gate model entry | model registry lists all four models unconditionally | `test_star_msar_run_even_if_linearity_not_rejected` | interpretation field only |

### 5.4 Models (Spec §5, §6; D5–D7)

| Model | Code | Estimation / forecasting | Tests |
|---|---|---|---|
| **AR(p)** | `specification/ar_select.py`, `models/ar.py` | OLS with intercept; selection on initial window, common effective sample (D2), BIC rank, first candidate passing Ljung–Box (D1), else BIC minimum flagged "diagnostically weak"; order fixed; refit each origin; iterated forecast | equals statsmodels `AutoReg` on same sample; selection rule table-test incl. all-fail branch; companion-matrix stability |
| **ARMA(p,q)** | `specification/arma_select.py`, `models/arma.py` | Gaussian ML (statsmodels state space), stationarity+invertibility enforced, grid minus (0,0), BIC + whiteness; M4 flag; exact iterated forecast | recovers simulated ARMA orders/params; grid exclusion; q=0/p=0 flag |
| **MSAR (K=2)** | `models/msar.py` | **Own Hamilton filter** on the expanded state (s_t…s_{t−p}); regime means, common φ, common σ; logistic/log parameterization; deterministic multi-start (D6); warm start from previous successful vector, fallback to deterministic starts, winner recorded; regimes ordered by mean; smoothed probabilities, transition matrix, occupancy, expected durations; filtered probabilities at the origin; **exact h-step conditional mean** | log-likelihood equals statsmodels `MarkovAutoregression` at identical parameters; parameter recovery on simulated MS-AR; label-switching rule; h-step forecast equals Monte-Carlo benchmark; boundary and empty-regime flags |
| **STAR** | `specification/star_spec.py`, `models/star.py` | Conditional NLS: linear coefficients by OLS given (γ,c), grid then refinement, standardized transition variable, bounds per D5; delay and type fixed from initial window; warm start (γ,c); one-step exact; h>1 per M2; transition-function range/SD | parameter recovery on simulated LSTAR/ESTAR; G in [0,1]; flag logic; reduces to AR when G≡0 |
| **K=3 MSAR** | `models/msar.py` with `K=3` | same structure and lag as K=2 | simulated 3-state recovery; 243-state filter agrees with brute-force enumeration for small T |
| **VAR(p)** | `specification/var_select.py`, `models/var.py` | OLS, p∈{1,2,3} by BIC on a common sample, stability required, iterated forecasts | equals statsmodels VAR; stability via companion eigenvalues |
| **ARMA-GARCH(1,1) diagnostic** | `models/arma_garch.py`, `diagnostics/garch_diag.py` | custom Gaussian quasi-ML (R4); persistence α+β; standardized-residual LB, LB² and ARCH-LM | recovers simulated GARCH(1,1); stationarity constraint |
| Adequacy classification | `models/status.py`, `models/flags.py` | Adequate / Fragile / Failed with reason codes from D8 thresholds; one function, one table of rules | one test per reason code; `test_no_silent_fallback` (failed fit never replaced by another model) |

### 5.5 In-sample adequacy and credibility (Spec §7, §8)

| Requirement | Code | Tests | Outputs |
|---|---|---|---|
| loglik, AIC, BIC, in-sample RMSE/MAE, Ljung–Box (12/24; 4/8), ARCH-LM (12; 4), Jarque–Bera, per series/model/refit | `diagnostics/residual_tests.py` (statsmodels wrappers returning `TestResult`) | compared with statsmodels directly; df-adjustment test | T3.1 (`output/diagnostics/adequacy_by_refit.parquet` + summary CSV) |
| Standardized H0/statistic/distribution/p/decision/implication table | `reporting/test_registry.py` | schema test: every test row complete | `T-DIAG` (D17) |
| MSAR credibility (matrix, occupancy, durations, boundary flags) | `models/flags.py::msar_flags()` | threshold edge cases | T3.2 |
| STAR credibility (type, delay, γ, c, G min/max/SD, bound flags) | `models/flags.py::star_flags()` | edge cases | T3.2 |
| Policy-rate dedicated diagnostic (§8.1) | `reporting/tables.py::policy_rate_diagnostic()` assembling transformation status, convergence, transition probabilities, occupancy, coefficient magnitude, residual adequacy, forecast behaviour | schema test | `T3.2-FF` |
| Fitted-vs-observed, residual ACF (95% bands), regime/STAR plots | `reporting/figures.py` | smoke-render test; bands present | F3.1, F3.2, F3.3 |

### 5.6 Pseudo-out-of-sample design (Spec §9; Comp §3, §5–§8)

| Requirement | Code | Tests |
|---|---|---|
| Rolling windows 240/120; first origin; target alignment | `forecasting/windows.py::rolling_origins()` | `test_rolling_window_boundaries`, `test_forecast_target_alignment`, `test_window_length_constant` |
| No future data in predictors | `forecasting/rolling.py` takes only `y[:origin]` | property test: mutate all data after the origin → identical forecast |
| Every-origin re-estimation with spec fixed from the initial window | `forecasting/rolling.py::run_chain(series, model, spec)` | `test_params_refit_each_origin`, `test_spec_not_researched` |
| Iterated multi-step from one fit for h∈{1,3,6,12}/{1,2,4} | `forecasting/iterate.py` (AR/ARMA/VAR analytic; MSAR exact; STAR per M2) | iterated vs closed-form AR(1); MSAR exact vs simulation |
| Warm starts, cache, checkpoints, resume | `core/cache.py`, `core/checkpoints.py` | `test_cache_key_deterministic`, `test_cache_key_changes_with_each_element`, `test_resume_does_not_refit`, `test_warm_chain_invalidation` |
| Parallelism without shared writes; reproducible child seeds | `core/parallel.py`, `core/seeds.py` | `test_parallel_equals_serial`, `test_seed_independent_of_schedule` |
| Failure handling | `core/schemas.py::FailureEvent`, `reporting/failure_registry.py` | `test_failed_model_emits_record_and_others_continue` |
| Runtime summary | `core/runtime.py` (wall, CPU, fits attempted/cached/failed, peak memory) | schema test |

Outputs: `output/forecasts/forecasts_<series>_<model>.parquet` (origin, target date, horizon, forecast, actual, status, reason codes, provenance), `output/models/fits/…`, `output/logs/runtime_summary.csv`, `output/logs/fit_log.parquet`.

### 5.7 Forecast evaluation (Spec §10)

| Requirement | Code | Tests | Outputs |
|---|---|---|---|
| RMSE, MAE, OOS R² vs AR; N valid/failed | `evaluation/metrics.py` | hand-computed examples; R² identity | T3.3 |
| **HLZ (2025)** squared and absolute loss, five pairs, every tuning choice recorded | `evaluation/hlz.py` — **blocked on M3** | loss-differential construction (both losses); local demeaning and long-run variance matched to the paper; deterministic recording of bandwidth/smoothing; size/power Monte Carlo; paper worked example if one exists | T3.3 (columns), T3.3A |
| **DM-HLN** secondary, same pairs/losses, horizon-appropriate LRV, truncation recorded; kept separate | `evaluation/dm_hln.py` | known DM numbers; HLN factor; `test_dm_does_not_overwrite_hlz` | T3.3B (agreement flag vs HLZ) |
| **MCS** 90%/95%, both losses, common-date admissible loss matrix, elimination order | `evaluation/mcs.py` (wraps `arch.bootstrap.MCS`, D11) | `test_mcs_matrix_only_admissible_common_dates`; known-case MCS; seed determinism | T3.4 |
| States (expansion, recession, turning window, outside), per-state N/RMSE/MAE/mean loss diff | `evaluation/states.py`, `evaluation/metrics.py::by_state()` | mask tests below | T3.5 |
| **Giacomini–White** regression, HAC by horizon, coefficients/p-values, joint test, sign convention, availability flag (M1, M12, D10, D12) | `evaluation/gw.py` | `test_gw_conditioning_aligned_to_target_date`; HAC vs reference implementation; size under null | T3.5 |
| Peak vs trough detail, h=1, baseline window | `evaluation/states.py::peak_trough_split()` | N checks | T3.6 |
| Turning-window masks: monthly ±1/±3/±6, quarterly 0/±1/±2; union; baseline vs sensitivity separate | `evaluation/states.py::turning_masks()` | `test_monthly_masks_reproducible`, `test_quarterly_masks`, `test_overlap_union_counted_once`, `test_baseline_table_uses_pm3_pm1q` | T4.TP1 |
| TP-sensitivity classification (M13) | `evaluation/tp_sensitivity.py` | table-driven | T4.TP1 |

### 5.8 Robustness (Spec §11; Outputs §8) — all written under `output/robustness/`, never to baseline paths

| Threat | Code | Procedure | Output |
|---|---|---|---|
| UNRATE/FEDFUNDS transformation | `robustness/transformation.py` | re-run specification stage (initial window) + OOS chain on the non-baseline transformation; compare on modeled target and on common level-error (M6) | T4.1 |
| CPI lag | `robustness/cpi_lags.py` | AR p=1,3,6,12 under a common evaluation set; MSAR/STAR per T1 | T4.2 |
| Two regimes imposed | `robustness/k3.py` | K=3 MSAR, same structure/lag; BIC, convergence, occupancy, transitions, forecast metrics, retention decision encoded from the §11.1 rule (retain K=2 if empty/unstable/worse BIC/no OOS gain/indistinct third state) | T4.3 |
| h=1 only | `robustness/horizons.py` | tabulate stored multi-horizon forecasts through the same metric/test code | T4.4 |
| Omitted macro information | `robustness/var_compare.py` (M10) | VAR OOS vs AR on the common sample, difference from univariate ranking | T4.5 |
| Conditional variance | `robustness/garch_diag.py` (M9) | ARCH-LM trigger → ARMA-GARCH diagnostic | T4.6 |
| Failure misleads figures | `reporting/figures.py` (D19) | failure panels, no clipping | F3.4 |
| Turning window width | `evaluation/tp_sensitivity.py` | see §5.7 | T4.TP1 |
| Window length, U.S. sample | none implemented, by design | the spec states these are documented design assumptions; output notes carry the statement | note strings |

### 5.9 Failure registry (Spec §7.5, §8; Outputs §9)

`reporting/failure_registry.py` builds T4.7 from `FitRecord` flags: one row per event with series, model, refit date, horizon, category, reason code (`NONCONVERGENCE, NONFINITE, SINGULAR_COV, UNSTABLE_AR, EMPTY_REGIME, TRANSITION_BOUNDARY, STAR_GAMMA_BOUND, STAR_THRESHOLD_EXTREME, RESIDUAL_AUTOCORR, EXTREME_FORECAST`), raw diagnostic, whether the forecast was retained, whether the figure was separated. Tests: one synthetic trigger per code; all-codes-present schema test.

### 5.10 Figures and tables rules (Spec §13)

Figure helper enforces: unit labels, sample dates, model labels, NBER shading, no multi-series squeeze, failure panel separate, no clipping, ACF with 95% bands, significance convention in tables (`stars` column). `test_no_axis_clip`, `test_failure_panel_created`, `test_stars_thresholds`. Formats: PNG (300 dpi) + PDF with an embedded/sidecar provenance record.

### 5.11 Provenance, logs, reproducibility (CLAUDE.md §8–9; Outputs §1; Comp §9, §15)

`core/provenance.py` appends `run_id, data_snapshot_hash, code_commit_sha, config_hash, created_utc` (+ series/model/horizon where relevant) to every table; figures and non-tabular files get a sidecar `*.provenance.json`; `output/manifests/run_manifest.json` ties run ID to data cutoff 2026-10-05, vintage, manifest hash, commit SHA (and dirty flag), config, environment (`output/logs/environment.json`), timestamps. Logs: `output/logs/pipeline.jsonl` (structured stage events), `fit_log.parquet`, `runtime_summary.csv`, `warnings.log`.

## 6. Explicit implementation confirmations (your item 5)

- **AR:** OLS with intercept, p chosen on the initial window by BIC on a common sample then the first Ljung–Box-clean candidate; fixed order, parameters refit every origin; stability-checked; failures recorded.
- **ARMA:** Gaussian ML, grid 0–4 monthly / 0–2 quarterly minus (0,0), stationarity and invertibility required, BIC + whiteness, order fixed after the initial window. Pure-AR/pure-MA selections are allowed and flagged (M4).
- **MSAR:** Hamilton mean-switching with common AR and variance, K=2, lag = AR lag capped at 4; own filter, regimes ordered by mean, exact h-step means, all §5.5/§8.1 diagnostics and flags; no fallback parameterization.
- **STAR:** LSTAR/ESTAR from the Teräsvirta sequence on the initial window, delay from the specification stage, lag cap 4/2, conditional NLS with warm starts, all §5.6/§8.2 diagnostics and flags.
- **K=3 MSAR:** identical structure/lag, reported regardless of outcome, retention rule of §11.1 encoded (scope M8).
- **VAR:** five monthly variables with baseline transformations, 1959M1 start, p∈{1,2,3} by BIC, stability required, design per M10; a robustness model only.
- **Conditional ARMA-GARCH diagnostics:** ARCH-LM trigger → custom ARMA-GARCH(1,1); persistence and standardized-residual diagnostics; not in the horse race (M9).
- **Stationarity tests:** ADF, KPSS, Zivot–Andrews exactly as §3.2–3.4, initial-window decision, full-sample check, mandatory alternative-transformation robustness.
- **Nonlinearity tests:** Tsay + LST/Teräsvirta sequence; no MS LR test.
- **Pseudo-out-of-sample forecasting:** rolling 240/120, spec fixed once, parameters refit at every origin, iterated horizons from one fit per origin.
- **HLZ:** implemented only from the published paper/supplement (M3); every tuning choice stored in the output row. **Not started until M3 is settled.**
- **DM-HLN:** separate secondary test, same pairs/losses, never replaces HLZ.
- **Giacomini–White:** HAC regression on `REC_t`, `TURN_t` aligned to the target date, joint test, availability flag (M1, M12).
- **Model Confidence Set:** 90/95%, both losses, common-date admissible loss matrix (M7, D11).
- **Horizon robustness:** monthly 1/3/6/12, quarterly 1/2/4, from the same fits.
- **Turning-point-window robustness:** ±1/±3/±6 months, 0/±1/±2 quarters, union masks, baseline never replaced.
- **Failure handling:** structured `FailureEvent`, reason codes, other models continue, no silent fallback, failures visible in tables and figures.
- **Frozen-data provenance:** hash-verified frozen CSVs + manifest, no network in the default run, refresh to a dated separate namespace, provenance on every artifact.

## 7. Required outputs → generating code (your item 6)

All paths are under `output/` unless stated. "CSV" tables also get a Parquet twin when large.

| ID | Content | Generator | File(s) |
|---|---|---|---|
| T2.0 | Concept-to-series incl. exclusions | `reporting/tables.py::concept_to_series` | `data_audit/T2.0_concept_series.csv` |
| T2.0A | Frozen-data manifest + hash status | `data/manifest.py` + `reporting/tables.py` | `manifests/frozen_manifest.csv` |
| F2.0 | Sample-coverage timeline | `reporting/figures.py::sample_timeline` | `figures/F2.0_sample_timeline.{png,pdf}` |
| T2.1 | Data dictionary / sample audit | `data/samples.py` | `data_audit/T2.1_data_dictionary.csv` |
| T2.2 | Stationarity and decision table | `diagnostics/stationarity.py`, `decision_rule.py` | `diagnostics/T2.2_stationarity.csv` |
| F2.1 | Raw/transformed overview per target (NBER shading, ZA break) | `reporting/figures.py::series_overview` | `figures/F2.1_<target>.*` |
| T2.3 | Tsay | `diagnostics/nonlinearity.py` | `diagnostics/T2.3_tsay.csv` |
| T2.4 | LST by delay + selection + type | `diagnostics/nonlinearity.py` | `diagnostics/T2.4_star_linearity.csv` |
| T2.5 | Selected AR/ARMA specs | `specification/*` | `diagnostics/T2.5_selected_specs.csv` |
| T3.1 | Adequacy by series/model/refit | `diagnostics/residual_tests.py`, `models/status.py` | `diagnostics/T3.1_adequacy.csv` (+ per-refit Parquet in `models/`) |
| T3.2 | MSAR/STAR credibility | `models/flags.py` | `diagnostics/T3.2_credibility.csv` |
| T3.2-FF | Policy-rate diagnostic (provisional ID) | `reporting/tables.py::policy_rate_diagnostic` | `diagnostics/T3.2-FF_policy_rate.csv` |
| T-DIAG | Standardized test table (provisional ID) | `reporting/test_registry.py` | `diagnostics/T-DIAG_tests.csv` |
| F3.1–F3.3 | Fitted vs observed; residual ACF; regime/STAR plots | `reporting/figures.py` | `figures/F3.{1,2,3}_*` |
| T3.3 | Main h=1 table (with HLZ columns) | `evaluation/metrics.py`, `hlz.py` | `tables/T3.3_main_h1.csv` |
| T3.3A | Full HLZ pairwise | `evaluation/hlz.py` | `forecast_tests/T3.3A_hlz.csv` |
| T3.3B | DM-HLN + agreement | `evaluation/dm_hln.py` | `forecast_tests/T3.3B_dm_hln.csv` |
| T3.4 | MCS | `evaluation/mcs.py` | `forecast_tests/T3.4_mcs.csv` |
| F3.4 | Actual vs forecast (failure-aware) | `reporting/figures.py` | `figures/F3.4_<target>.*` |
| F3.5 | Cumulative squared-loss difference | `reporting/figures.py` | `figures/F3.5_<target>.*` |
| T3.5 | State performance + GW | `evaluation/states.py`, `gw.py` | `forecast_tests/T3.5_state_gw.csv` |
| T3.6 | Peak vs trough (h=1, baseline window) | `evaluation/states.py` | `tables/T3.6_peak_trough.csv` |
| T4.TP1 | Turning-window sensitivity | `evaluation/tp_sensitivity.py` | `robustness/T4.TP1_turning_sensitivity.csv` |
| F3.6 | State-conditioned RMSE/MAE differences (descriptive) | `reporting/figures.py` | `figures/F3.6_*` |
| T4.1 | Transformation robustness | `robustness/transformation.py` | `robustness/T4.1_*.csv` |
| T4.2 | CPI lag robustness | `robustness/cpi_lags.py` | `robustness/T4.2_*.csv` |
| T4.3 | K=2 vs K=3 | `robustness/k3.py` | `robustness/T4.3_*.csv` |
| T4.4 | Horizon robustness | `robustness/horizons.py` | `robustness/T4.4_*.csv` |
| T4.5 | VAR comparison | `robustness/var_compare.py` | `robustness/T4.5_*.csv` |
| T4.6 | ARMA-GARCH diagnostic | `robustness/garch_diag.py` | `robustness/T4.6_*.csv` |
| T4.7 | Failure/fragility registry | `reporting/failure_registry.py` | `diagnostics/T4.7_failure_registry.csv` |
| Claim matrix | `claim_evidence_matrix.csv` (Part 8) | `reporting/claim_matrix_schema.py` (schema + validator only in Part 6, D18) | `manifests/claim_evidence_matrix.csv` (empty template) |
| Logs | runtime, fits, pipeline | `core/runtime.py`, `logging_utils.py` | `logs/runtime_summary.csv`, `logs/fit_log.parquet`, `logs/pipeline.jsonl`, `logs/environment.json` |

## 8. Reproducibility tests (Comp §15) → test modules

| Spec §15 item | Test module |
|---|---|
| frozen hash verification; vintage = 2026-10-05; endpoints; no manual/silent substitution | `tests/unit/test_data_frozen.py` |
| transformations; annualization factors | `tests/unit/test_transforms.py` |
| lag construction; rolling boundaries; no future data; target alignment | `tests/unit/test_windows_alignment.py` |
| USREC used only for evaluation | `tests/unit/test_usrec_isolation.py` |
| every-origin re-estimation alignment | `tests/integration/test_rolling_reestimation.py` |
| deterministic cache key | `tests/unit/test_cache_keys.py` |
| level reconstruction from differences | `tests/unit/test_level_reconstruction.py` |
| HLZ loss differential, local demeaning, LRV vs paper, recorded bandwidths | `tests/validation/test_hlz.py` (blocked on M3) |
| DM-HLN separate from HLZ | `tests/unit/test_dm_hln.py` |
| GW conditioning variables aligned to target date | `tests/unit/test_gw.py` |
| turning masks ±1/±3/±6 and quarterly; union; baseline vs sensitivity separation | `tests/unit/test_turning_masks.py` |
| MCS loss matrix contains only admissible common-date forecasts | `tests/unit/test_mcs_inputs.py` |

**Scientific validation (my addition to guard model code, not a methodology change):** seeded simulations with known truth for AR, ARMA, MS-AR (K=2,3), LSTAR/ESTAR, GARCH(1,1), VAR; cross-checks of log-likelihood/estimates against statsmodels where an equivalent exists; test-size checks for Tsay, LST, DM, HLZ, GW under simulated nulls.

## 9. Build order and acceptance (all within Part 6)

| Step | Content | Gate |
|---|---|---|
| 0 | Environment, lock file, package skeleton, config/provenance/seed/cache core | core unit tests green |
| 1 | Data layer: FRED client (mocked), frozen init/verify, samples, transforms | data tests green. **Real initialization needs your key + approval (R1).** |
| 2 | Diagnostics: stationarity, decision rule, residual tests, Tsay, LST | validation sims green |
| 3 | Specification stage: AR, ARMA, STAR delay/type, VAR lag | selection-rule tests green |
| 4 | Models: AR, ARMA, MSAR (K=2,3), STAR, VAR, ARMA-GARCH; status/flags | recovery + cross-check tests green; **early runtime benchmark** |
| 5 | Forecasting engine: windows, chains, warm starts, cache, checkpoints, parallel | alignment/no-lookahead/resume tests green |
| 6 | Evaluation: metrics, states/masks, DM-HLN, GW, MCS; **HLZ once M3 is settled** | evaluation tests green |
| 7 | Robustness modules | integration tests green |
| 8 | Reporting: all tables/figures/registry, provenance, logs, `run_all.py` CLI incl. `--smoke-test` | schema + provenance tests green |
| 9 | Smoke test (one monthly + one quarterly target, short OOS block, all stages; the monthly VAR block needs all five monthly series loaded, only the target subset is forecast) | smoke run completes, outputs in `smoke_output/` only, every artifact has provenance; reviewed for completeness only (R8) |

**Part 6 is complete when:** all unit/integration/validation tests pass; every output ID in §7 has a generator that runs in the smoke test (HLZ included, if M3 is resolved — otherwise Part 6 is reported as *incomplete on HLZ*, not substituted); no full thesis-baseline run has been made. Then I stop and wait for your approval before Part 7.

## 10. What I will not do

Change variables, transforms, windows, lags, regimes, horizons, tests or robustness specs; add MSSTAR, Clark–West/McCracken, Amisano–Giacomini, polynomial models, or a nowcasting model; substitute a generic HAC estimator for HLZ; fall back silently after a failed fit; run the full baseline or any Part 7/8 task; choose anything because it improves results. Each change to an item above that I think is needed will come to you first with options.
