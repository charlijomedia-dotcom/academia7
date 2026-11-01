# Part 8 correction phase — implementation, cache evidence and targeted execution plan

- **Branch:** `part8-corrections`, based on `part8-final-audit` at `337b84be1aafe5d85f554a39a4ae69a7e0ec8961`.
- **Original publication (unchanged):** branch `part8-results/baseline-20261030T173044-949fcd76`, commit `066294544e8ff84f3c2c73ab647c8d13331dcac1`.
- **Approval:** user instruction of 2 November 2026 approves F1, F3 and F4, conditionally approves F2, authorises F5 as interpretation only, and authorises F6 as a numerical review only.
- **Status: implemented and tested; no output regenerated; no Colab run launched.**

## 1. Exact files changed

All paths are under `my-thesis/`.

| File | Correction | Change |
|---|---|---|
| `code/src/thesis/evaluation/scoring.py` (new) | F1 | `scoreable()` and `mask_failed()`. A row is scoreable only if its fit is not `failed` and its forecast and actual are finite. A failed fit's forecast moves to `failed_raw_forecast`. |
| `code/src/thesis/pipeline.py` | F1, F3, F4 | `_chains()` masks every returned chain's forecasts. The F3.4 diagnostic panel uses the preserved raw failed forecast. The T3.3A/T3.3B pair loop computes `loss(model_b) − loss(model_a)` and adds `benchmark`/`competitor` columns. The stationarity stage calls `report_zivot_andrews` and passes both break dates to F2.1. |
| `code/src/thesis/evaluation/alignment.py` | F1 | `valid_dates` uses `scoreable`, a defensive second barrier for HLZ, DM-HLN, MCS and every pairwise alignment. |
| `code/src/thesis/evaluation/metrics.py` | F1 | `accuracy_table` scores only `scoreable` rows (defensive). |
| `code/src/thesis/evaluation/mcs.py` | F2 | `hln_mcs_r`, a guarded re-implementation of `arch`'s HLN R-method. It is used only when `arch` raises or its variance overflows, and every row records `mcs_implementation`. |
| `code/src/thesis/diagnostics/decision_rule.py` | F4 | `report_zivot_andrews` reports ZA on the initial window and the full sample (§3.2, P-02) and never changes the §3.4 decision. Decision rows gain the ZA statistic, p-value, break date and role columns. |
| `code/src/thesis/reporting/figures.py` | F1, F4 | Flagged forecasts in F3.4 are drawn as markers, not lines that join non-adjacent dates (R1-06). F2.1 marks both ZA break dates. |
| `code/tests/unit/test_part8_corrections.py` (new) | F1–F4 | 22 regression tests (§3). |
| `colab/run_thesis_colab.ipynb` | run preparation | Default `BRANCH = "part8-corrections"`, as the notebook's own test requires. `RESULTS_BRANCH_PREFIX = "part8-corrected-results"`, so a corrected release can never be pushed under the original `part8-results/` namespace. No run was launched. |
| `reports/part8/corrections/*` (new) | evidence | Validation and feasibility scripts, their CSV/JSON results, and this plan. |
| `reports/part8/*.md`, `claim_evidence_matrix_adjudicated.csv` | reporting | Provisional marking, multiplicity qualification, the F5 statement, F4 preview, reclassified jury statuses. |

**Not changed:**
- every fit-critical file (`core/cache._FIT_CRITICAL`: `models/*.py`, `transforms/*.py`, `forecasting/windows.py`, `forecasting/rolling.py`, `forecasting/simulate.py`);
- `core/cache.py`;
- the three configuration files whose merged hash enters every cache key (`configs/baseline.yaml`, `series_catalog.yaml`, `thresholds.yaml`);
- `approved-specs/`, `data/` and `output/`.

## 2. Fit-cache identity and reuse — evidence

The evidence comes from `cache_compatibility_check.py`, with results in `cache_compatibility_check.json`, re-run on the committed branch head.

| Check | Result |
|---|---|
| `git diff 46a53181..HEAD` on all 13 fit-critical files | empty |
| `git diff 46a53181..HEAD` on the 3 cache-relevant configs | empty |
| `code_hash()` on HEAD | `93ca1685fda15e4b…` — equals the published run |
| `config.hash` on HEAD | `949fcd76769048e3…` — equals `output/manifests/run_manifest.json` |
| Colab `cache_identity` on HEAD | **`3413465b508bb844`** — equals the Google Drive cache identity |

**End-to-end reuse.** A real chain was run twice against one fresh cache:

- **Chain:** UNRATE, AR(6), 240-month window, h = 1, 3, 6 and 12, 23 origins from 2019-10 to 2021-08. The run includes the FAILED 2020-04 `UNSTABLE_AR` fit.
- **First run, approved code** (a `git worktree` of `46a53181`): 23 fits estimated, 23 cache misses, cache written.
- **Second run, corrected code, same cache:**
  - **23 of 23 fits served from the cache, 0 misses**;
  - **raw forecasts bit-identical**;
  - the failed fit's 4 forecast rows are masked from scoring, with the raw values preserved (`failed_raw_forecast`).

The existing cache-fidelity tests (`tests/integration/test_cache_fidelity.py`, `test_cache_horizons.py`) also pass on this branch (§3).

## 3. Tests

- **New: `tests/unit/test_part8_corrections.py`, 22 tests, all passing.**
  - **F1:**
    - a failed-but-finite forecast is excluded from RMSE, MAE, OOS R², pairwise alignment, HLZ/DM inputs and the MCS loss matrix;
    - masked and unmasked frames give identical metrics;
    - adequate and fragile forecasts, including extreme fragile ones, stay scored, as §7.5 requires;
    - `Pipeline._chains` masks every chain it collects;
    - masking is idempotent and preserves the raw value.
  - **F2:**
    - the guarded MCS is bit-identical to `arch` in 6 random designs at 90% and 95%;
    - on the tie condition `arch` raises `IndexError` and the guarded version completes with all four models judged;
    - the overflow condition is rescaled rather than zeroed;
    - ambiguous ties (different row models) are reported unavailable;
    - the implementation used is recorded in every row.
  - **F3:** reversing d leaves the HLZ two-sided p-value exactly unchanged and negates the statistic, and the pipeline uses competitor − benchmark.
  - **F4:** ZA is reported on both samples, the decision, rule branch and break field are unchanged, and a tie-break result is reused.
  - **Cache safety:** none of the corrected modules is in `_FIT_CRITICAL`.
- **Full suite** (`pytest -q`, this container, 41 min): **887 passed and 1 failed**.
  - The failure was `test_colab_notebook.py::test_the_default_branch_is_the_one_holding_this_notebook`. This guard requires the notebook's default `BRANCH` to be the branch it lives on, and the notebook still named `claude/msar3-in-sample-amendment`.
  - After the notebook defaults were updated (row added to §1), the notebook test files pass (33/33). **Result: 888/888.**
  - The suite includes the existing cache tests (`test_cache_fidelity.py`, `test_cache_horizons.py`), the parallel and scheduler equivalence tests, and the end-to-end pipeline integration test.

## 4. F2 validation (conditionally approved correction)

**Root cause.** `arch` 8.0.0 `MCS._compute_r` fails on two conditions:

1. **Ties.** When one model's losses are many orders of magnitude larger, its standardised differences against several models are bit-identical. `np.argwhere(sub == max)` returns several rows, and `loc.squeeze()[0]` returns an index *pair*, which crashes the p-value formatting.
2. **Overflow.** At h=12 squared loss, squaring the recentred bootstrap differences (about 1e199) overflows the variance.

**Guarded implementation.** It performs the same operations on the same `arch` stationary-bootstrap index stream, with the same block length ⌈√T⌉, 5,000 replications, seed 20261005, the same `+I` variance guard, max-t elimination statistic, p-value rule and monotone accumulation. Only two cases are handled differently:

- a variance entry that is non-finite in plain arithmetic is computed through a per-pair scale factor, which is mathematically identical;
- a tie is resolved only when all maximising cells share the same eliminated (row) model. Otherwise the cell is reported unavailable.

**Validation** (`f2_mcs_validation.py`, results in `f2_mcs_validation.csv`; 184 cell-levels across 6 targets, all horizons, 2 losses and 2 confidence levels, on the published frames and on the F1-masked frames):

- **Where `arch` succeeds (138 cell-levels):** the guarded result is **identical**, with maximum |Δp| = 0.0.
- **Harness fidelity:** `arch` in the harness reproduces **all 70** published available cell-levels exactly, so the harness rebuilds the pipeline's loss matrices.
- **Where `arch` fails (22 published cell-levels; 24 after F1, including the new UNRATE h=12 squared cell):** the guarded version completes every cell.
  - These cells involve 1 tied elimination step, or 6 rescaled variance cells at h=12 squared loss.
  - No cell fell into the "ambiguous tie, unavailable" case.
- **Independent check of the overflow cells** (`f2_scale_invariance_check.csv`). HLN statistics are invariant to multiplying the whole loss matrix by a constant. With losses × 1e-150 no rescaling is needed, and the result is identical (|Δp| = 0.0, same elimination order) for CPIAUCSL and M2SL h=12 squared loss, at 90% and 95%.
- **Previews from the published forecasts** (authoritative only after regeneration):
  - CPIAUCSL h=3 and h=6 absolute loss: ARMA leaves the 90% set (MCS p = 0.044 and 0.026).
  - CPIAUCSL h=1 squared: all four models are retained.
  - STAR is never eliminated through the tie path alone; it is judged by the same statistic as every model.

**Conclusion.** Equivalence is demonstrated wherever `arch` works. In the failing cells the computation is the identical procedure with documented numerical guards. Nothing was dropped, truncated or winsorised.

## 5. F3 — what changes

- Only T3.3A and T3.3B change: `mean_loss_differential`, `statistic`, `p_value_upper`/`p_value_lower` and the DM statistic now follow the stated convention, so a negative value favours `model_b`, the competitor.
- New `benchmark`/`competitor` columns make the roles explicit.
- **Two-sided p-values and all 5% decisions are unchanged.** For HLZ, the p-value is the share of simulated draws with |T*| ≥ |t|, which is invariant to the sign of t. DM-HLN's two-sided p-value comes from a symmetric reference distribution.
- The one-sided p-values come from a simulated, not exactly symmetric, null distribution. They are recomputed under the correct orientation rather than merely swapped.

## 6. F4 — preview

From `f4_zivot_andrews_preview.csv`, using the corrected stationarity code on the frozen CSV.

| Series | Sample | ZA statistic | p-value | Break | Role |
|---|---|---|---|---|---|
| UNRATE | initial window 1948-01 to 1967-12 | −4.556 | 0.189 | 1957-08 | reported (§3.2), not used by the §3.4 rule |
| UNRATE | full sample 1948-01 to 2026-08 | −4.606 | 0.169 | 2008-04 | reported |
| FEDFUNDS | initial window 1954-07 to 1974-06 | −3.500 | 0.811 | 1970-10 | reported |
| FEDFUNDS | full sample 1954-07 to 2026-08 | −4.290 | 0.320 | 1984-08 | reported |

- The baseline transformations are unchanged: UNRATE in levels (branch 1), FEDFUNDS in differences (branch 2).
- **Interpretive consequence:** for UNRATE the break-allowing test does not corroborate the ADF rejection. The level treatment rests on ADF and KPSS, as the predeclared rule specifies.

## 7. F6 — numerical review of a nesting-informed K=3 start (not implemented)

**Feasibility study.** `f6_k3_nesting_feasibility.py`, with results in `f6_k3_nesting_feasibility.csv`. It is read-only and does not touch T4.3.

**Construction.**
- Take the K=2 optimum: two means, AR coefficients and σ.
- Add a third mean at the midpoint of the two K=2 means.
- Set transitions into the new regime to 1e-4, keep the K=2 transition probabilities for the rest, and give the new regime a persistent row (0.90 stay).
- Pass this vector through the **existing** `warm_start` argument of `fit_msar`. **No fit-critical file would change.**
- The two approved deterministic starts still run, and the unchanged rule picks the best converged start.

**Results** (`f6_k3_nesting_feasibility.csv`, refits on this container; log-likelihoods):

| Target | Published K=2 | Published K=3 | Refit K=2 | Refit K=3, approved starts | K=3 with nesting start (selected start) | Nesting K3 − refit K2 |
|---|---|---|---|---|---|---|
| GDPC1 | −870.253 | −840.685 | −870.253 | −840.685 | −840.685 (deterministic) | +29.57 |
| CPIAUCSL | −2415.560 | −2370.506 | −2415.560 | −2370.506 | −2370.506 (deterministic) | +45.05 |
| INDPRO | −3614.104 | −3563.274 | **−3627.969** | −3563.273 | **−3550.313 (nesting)** | +77.66 |
| M2SL | −2203.647 | −2151.519 | **−2185.268** | −2151.519 | −2151.519 (deterministic) | +33.75 |
| UNRATE | 102.037 | 13.881 | **101.627** | **22.059** | **101.527 (nesting)** | **−0.10** |
| FEDFUNDS | −518.894 | −253.411 | −518.894 | −253.410 | −253.410 (deterministic) | +265.48 |

**Findings**

1. **UNRATE.**
   - The nesting start moves K=3 from about 80 log-likelihood points *below* K=2 to −0.10 below it.
   - Its third regime ends essentially empty (occupancy 0.0000): the optimiser stops in the flat direction of an unvisited regime, so the result is still marginally inconsistent with nesting.
   - It therefore restores approximate, not exact, nesting consistency. It also implies that the information criteria would favour K=2 only because K=3 adds parameters to an empty regime, which is not credible either way.
2. **INDPRO.** The nesting start finds a higher K=3 optimum, 12.96 log-likelihood points above both the published K=3 and the approved starts. **The published INDPRO K=3 was not a global maximum either.**
3. **Platform sensitivity (new finding).**
   - Refits of the *unchanged* code reproduce the published log-likelihoods to about 1e-6 for GDPC1, CPIAUCSL and FEDFUNDS.
   - They do **not** reproduce them for INDPRO K=2 (−13.9), M2SL K=2 (+18.4) or UNRATE K=2 (−0.41) and K=3 (+8.2).
   - With 2 deterministic starts, the full-sample MSAR optimum reached depends on platform-level floating-point detail. Colab produced the published values; this container uses a different CPU and BLAS.
   - Consequences:
     - T3.1, T3.2 and T4.3 MSAR numbers are reproducible on the publication's platform class, not across platforms;
     - for M2SL, a better K=2 optimum exists than the published one;
     - the corrected release must run on the same Colab platform class for its MSAR full-sample numbers to remain comparable;
     - the R1-17 and P-04 reports should state this sensitivity.
   - Whether the *qualitative* regime conclusions (outlier and boundary regimes) survive at the alternative optima was not examined in this study.
4. **Cost.** The extra K=3 start takes about one more K=3 optimisation per target. Measured here, the extra wall time ranges from roughly 0 to 100 seconds, and the total K=3 time from 17 seconds (GDPC1) to 334 seconds (UNRATE), while other jobs were running.

**Numerical limitations**
- L-BFGS-B from a start whose objective is about the K=2 value can only *descend*, so a converged nesting start ends with log-likelihood ≥ about K=2's. That restores nesting consistency.
- It does **not** guarantee a global maximum. The K=3 likelihood is multimodal, and the audit already showed rounding-level sensitivity, for example at INDPRO origin 500.
- The flat direction of an unvisited regime can stop the optimiser at the start, with an essentially empty regime. That estimate would be flagged low-occupancy or empty, not "credible".
- The result depends on where the extra mean is placed. The midpoint is one deterministic choice, not a search.

**Consistency with Part 5 §11.1**
- §11.1 requires "the same deterministic multi-start and optimizer rules" for K=2 and K=3.
- Adding a K=3-only start would be a change to that rule, so it needs your approval.
- A symmetric alternative is to warm-start K=2 from the AR(p) estimate with equal means. That is the analogous "nesting" start for K=2 against K=1, and it would keep the start rules parallel.
- **Cost:** one extra full-sample K=3 optimisation per target. Measured wall times in the CSV, run on this container while other jobs were running, range from about 7 seconds (GDPC1, p=1) to minutes (p=4 targets, with 3⁵ expanded states). There is no effect on any rolling chain.

**Recommendation.** Keep the UNRATE comparison INCONCLUSIVE in the current corrected release. If you approve the nesting start, apply it to all six targets symmetrically as a documented §11.1 implementation amendment, and keep the published T4.3 alongside it.

## 8. Outputs to regenerate

The baseline run is not re-estimated: every rolling fit is served from the cache.

| Output (under `output/`) | Why | Expected change |
|---|---|---|
| `forecasts/forecasts_*.csv/.parquet` | F1 | New `failed_raw_forecast` column. UNRATE: 4 failed AR rows become unscored. FEDFUNDS failed rows were already NaN. |
| `forecast_tests/T3.3_main_forecast_table.csv` | F1 | UNRATE rows (AR benchmark and every R²/HLZ against AR) |
| `forecast_tests/T3.3A_hlz_pairwise.csv`, `T3.3B_dm_hln_pairwise.csv` | F1, F3 | All rows: sign of the differential and statistic, one-sided p-values, role columns. UNRATE AR rows: values. Two-sided p and decisions are otherwise unchanged. |
| `forecast_tests/T3.4_model_confidence_set.csv` | F1, F2 | 11 unavailable cells (22 cell-levels) become available. UNRATE cells change under F1. New implementation columns. |
| `forecast_tests/T3.5_state_*.csv`, `T3.6_peak_trough_detail.csv` | F1 | UNRATE rows |
| `robustness/T4.4_*`, `T4.TP1_turning_window_sensitivity.csv` | F1 | UNRATE rows |
| `robustness/T4.1_*` | F1 | UNRATE (both transformations), FEDFUNDS-level AR |
| `robustness/T4.2_*` | F1 | the AR(p=12) row |
| `robustness/T4.5_var_comparison.csv`, `T4.5_var_predictive_tests.csv` | F1 | UNRATE rows |
| `robustness/window_length_*` | F1, F2 | UNRATE rows; 2 MCS cells |
| `data_audit/T4.9_locf_sample_comparison.csv`, `locf_forecast_exposure.*` | F1 | UNRATE rows; `forecast_valid` on the failed rows |
| `diagnostics/T2.2_stationarity.csv`, `T2.2_transformation_decisions.csv`, `all_test_results.csv` | F4 | 4 new ZA rows and new ZA columns |
| `figures/F2.1_UNRATE`, `F2.1_FEDFUNDS` | F4 | ZA break lines |
| `figures/F3.3`–`F3.6` (UNRATE) and `F3.4_*` (all targets) | F1, F7.2 | UNRATE content; flagged-forecast markers |
| `figures/F4.8_UNRATE` | F1 | UNRATE content |
| `manifests/*`, `logs/*` | release | New run ID, code SHA, inventory, claim-matrix reconciliation (§10) |

**Expected unchanged** (verified by `tools/compare_runs.py`; any difference is a stop signal):

- T2.0, T2.0A, T2.1, T2.3, T2.4, T2.5;
- T3.1, T3.2, `models/fit_records.*`;
- T4.3 (all three tables) and F4.3;
- T4.6 (all files);
- T4.7 failure registry and status counts;
- `T4.5_var_forecasts.csv`, `T4.5_var_selection.csv`;
- F2.0, F3.1, F3.2;
- every non-UNRATE row of the evaluation and robustness tables, apart from the F2 and F3 columns listed above.

## 9. Targeted execution plan (requires your approval; no run launched)

> **Superseded in part (2 November 2026, cache audit).** The statement below that all rolling fits would be served from the cache was an *assumption*, not a verified fact. It is **withdrawn**.
>
> - The production run estimated 34,300 fits that may never have reached Drive.
> - Completeness is now measured, not assumed: the notebook's preflight runs `code/tools/cache_completeness.py` and stops.
> - The run is refused unless every planned origin is a hit.
> - See `cache_recovery_report.md` for the current strategy (R0, R1 or R2).

**Recommended: Option A, a full entry-point run with the restored compatible cache.**

1. **Code.** Check out `part8-corrections` at the pushed SHA in Colab, from the same notebook (Python 3.11 venv with the exact lock, 4 workers).
2. **Gate before computing.** The notebook computes `cache_identity`; it must print `3413465b508bb844`. If it differs, stop.
3. **Cache.** Restore the Drive fit cache with that identity. The notebook restores only a matching identity.
4. **Run.** Run `run_all.py` as approved.
   - **Rolling chains, baseline and robustness (67,223 origins):** served from the cache **only if** the preflight completeness report shows every origin as a hit. That is unverified, and doubtful given the backup gap (see `cache_recovery_report.md`).
   - **Re-estimated deterministically, because these steps are not cached:**
     - the full-sample adequacy fits, including MSAR K=3 (about 60 min in the original run);
     - ARMA-GARCH, the VAR, the T4.3 tables and evaluation and robustness scoring (about 55 min).
   - **Estimated wall time:** about 2–2.5 hours. This is an estimate from the original stage timings, not a measurement.
5. **Cache-hit gate.** `forecast_origin_audit.csv`'s `origins_from_cache` must equal `attempted_origins` for all 24 baseline chains. The equivalent must hold for every window-length chain in `window_length_origin_audit.csv`. The monitor's "from cache" counts show this live, so any miss is visible within minutes; stop the run if misses appear.
6. **Verification.** Run `python code/tools/compare_runs.py <original output> <corrected output>`. Every difference must be in the §8 regenerate list. Any other difference is a stop signal and is reported, not explained away.
7. **Publication.**
   - Push to a **new** branch `part8-corrected-results/<new run_id>`.
   - Commit, with:
     - the new `run_manifest.json` (new run ID, code SHA = the correction commit, unchanged config and data hashes);
     - a fresh `output_inventory.csv`;
     - a `CORRECTIONS.md` that maps each changed file to F1–F4 and records the original results commit `0662945` as superseded only for those files.
   - The original branch and commit are never modified.
8. **Re-audit.** Update the Part 8 reports from the corrected outputs, re-adjudicate the provisional claims and the jury statuses, and resubmit Part 8 for approval.

**Option B, not recommended.** An evaluation-only entry point that skips the adequacy, GARCH and VAR stages would save about an hour. It would add a new, untested code path to the release and complicate provenance. The rolling estimation, which was 24 hours of the original run, is already avoided by Option A.

## 10. Claim matrix

- During this phase the adjudicated matrix stays in `reports/part8/claim_evidence_matrix_adjudicated.csv`, with the new `provisional` column.
- **Reconciliation during the corrected release** (part of the release, subject to the same approval):
  1. After the corrected run, re-adjudicate.
  2. Write the adjudicated rows into `output/manifests/claim_evidence_matrix.csv` (the Part 5 §12 location and columns).
  3. Validate with `reporting.tables.validate_claim_matrix`.
  4. Regenerate `output_inventory.csv`, and record the pipeline-written hash and the adjudicated hash in `CORRECTIONS.md`.
- The original publication's claim matrix (`62d5ec1e…`) remains in commit `0662945`.

## 11. Decisions still needed from you

1. Approve the targeted execution plan (Option A) and the publication route (§9, steps 7–8).
2. Accept or reject the F2 guarded MCS on the basis of §4.
3. F6: approve or decline the nesting-informed K=3 start (§7). If approved, choose between a K=3-only start and the symmetric variant. The study shows the start fixes the gross UNRATE violation (−88 → −0.1) and improves INDPRO, but cannot guarantee exact nesting or a global maximum.
5. **New, from F6: full-sample MSAR optima are platform-sensitive under the 2-start rule** (INDPRO, M2SL and UNRATE K=2 differ between Colab and this container). Should the reports carry this only as a stated limitation of T3.1, T3.2 and T4.3 (my recommendation for the current release), or would you like a separate methodological proposal on the MSAR multi-start rule? That proposal would be a Part 5 matter needing your approval.
4. F7.1, the stale "pending stationarity decision" in T2.1: approve fixing it in the same release (a one-line reporting change), or leave it documented.
