# R1 Option B3: complete original-cache audit and baseline-impact assessment (stage 1)

Date: 6 November 2026. Authorised scope: **Option B3 only**, a complete read-only original-cache audit and baseline-impact assessment.

- **No model was estimated.** Every stage refuses estimators (`guard` plus `no_estimation_allowed`).
- **Nothing was changed:** the published results, Tier A, Tier B checkpoints and certificates, the pins, the approved specifications and the releases are untouched.
- **Not done:** aggregation, publication and Part 9.

**Status: stage 1 of 2.**

| Task | Status |
|---|---|
| Task 2 (UNRATE MSAR 240 reconciliation) | complete |
| Task 6 (dependency map) | complete |
| Tooling for tasks 1, 3, 4 and 5 | built and validated |
| Tasks 1, 3, 4 and 5 themselves | need the **complete** cache, which is available only in Colab: you run the read-only notebook `colab/r1_original_cache_audit.ipynb`, after which I fetch its outputs from Drive and complete the report (stage 2) |
| Task 7 | partly answered from the earlier audit (§5) |

I cannot execute in Colab myself. Downloading the remaining 127 cache parts through the Drive connector is technically possible but would cost several million tokens, because most parts return inline.

Labels: **[C]** confirmed by data; **[P]** plausible, not shown; **[U]** unresolved.

## 1. Task 2: `forecasting:UNRATE|MSAR` and `T4.8:UNRATE|240:MSAR`

Evidence: `evidence/b3_original_cache_audit_20261106/unrate_msar_240_reconciliation.json`.

| Property | forecasting:UNRATE\|MSAR | T4.8:UNRATE\|240:MSAR | |
|---|---|---|---|
| Specification | MSAR(p=4, K=2) | identical | [C] |
| Data, transformation (`percent`), frequency (M) | — | identical (`y` equal element by element) | [C] |
| Window length | 240 | 240 | [C] |
| Origins | 704 | 704, the same origin dates and estimation windows | [C] |
| Cache keys | — | **identical at every origin**; they share cache payloads | [C] |
| Horizons requested | 1, 3, 6, 12 | **1 only** | [C] |
| Intended outputs | baseline tables T3.3–T3.6, F3.4–F3.6, T4.4, T4.TP1, T4.9 | window-length robustness (240-month row of `window_length_*`) | [C] |
| Published fit records (stage block) | rows 5086–5789, **704** records, 11 failed | rows 40337–41040, **704** records, 11 failed | [C] |

**The 701-versus-704 distinction is resolved [C].** Both chains have 704 records. The 701 came from my earlier deduplication of identical (date, parameters) pairs across the two blocks: at 3 dates the two blocks hold **different** fits, so they were not duplicates.

Records are now identified by **pipeline-stage block**: contiguous record ranges, one per stage that ran the chain (forecasting first, then the robustness exercises), with the T4.1 alternative-transformation chain in its own block (rows 15544–16246, 703 records, 0 failed). A test asserts these ranges.

**The three conflicting origins, April–June 1983 [C].** The same chain was estimated **twice** in the original final run: once in the forecasting stage, once in the T4.8 robustness stage. The two runs differ exactly at 1983-04-01, 1983-05-01 and 1983-06-01:

| Date | Forecasting stage (baseline) | T4.8 stage (240) |
|---|---|---|
| 1983-04-01 | failed (SINGULAR_COV;NONCONVERGENCE), **warm start offered**, loglik 54.375 | failed (same codes), **no warm start**, loglik −299.996 |
| 1983-05-01 | failed, warm offered, 54.483 | failed, no warm, −302.815 |
| 1983-06-01 | failed, warm offered, 54.481 | failed, no warm, −305.373 |

- All six fits are **failed**, so the published forecasts at these dates are masked (NaN) in both runs. These records therefore change **no** published forecast or score. [C]
- Across the whole chain, the **baseline run** withheld the warm start at **6 of its 11** post-failure origins: 1982-10/11/12, 1989-11, 2017-03 and 2020-07. [C]
- The **T4.8 run** withheld it at **all 11**. The extra five (1983-02, 04, 05, 06, 07) are where the two runs took different paths. [C]
- The pinned code is identical for both. A data or specification difference is excluded above, and the only remaining difference between the runs is their horizon sets. **[P]** The divergence came from each run's own cache-replay path through failed origins, including horizon-coverage misses: the final run's baseline audit records 13 `cache_horizon_misses` for this chain, consistent with payloads written for h=1 only by the T4.8 run sharing the same keys. The full-cache audit's per-origin horizon coverage settles this.

## 2. Task 6: downstream dependencies of the baseline UNRATE MSAR chain

Evidence: `baseline_unrate_msar_dependency_map.csv` (39 outputs) and `impact_stage_validation.json`.

The map is **empirical**: the pinned R1 workflow in legacy mode was run on the published outputs and on copies in which only this chain's forecast rows were changed. Validation of the impact machinery:

| Synthetic candidate | Files changed (of 92 regenerated) | Cells changed |
|---|---|---|
| Identical to the published chain | **0** | **0** |
| One h=1 forecast changed by +0.5 | 24 | 177 |
| One failed origin made fragile with a forecast | 27 | 954 |

In every case the reference pass reproduced every published table exactly or within floating-point tolerance; only figure bytes differ in this sandbox.

**Outputs that depend on the chain and that the pinned workflow regenerates without estimation (27):**
- `forecasts/forecasts_UNRATE.{csv,parquet}` and `forecasts/forecast_horizon_coverage.csv`;
- `forecast_tests/`: T3.3 main table, T3.3A HLZ, T3.3B DM/HLN, T3.4 MCS, T3.5 state performance and state-loss regression, T3.6 peak/trough detail;
- `robustness/`: T4.1 transformation robustness (the baseline is the comparator), T4.4 horizon robustness and tests, T4.TP1 turning-window sensitivity;
- `robustness/`: `window_length_comparison`, `_mcs`, `_predictive_tests` and `_origin_audit`, where the 240 row is the baseline chain re-read;
- `data_audit/`: T4.9 LOCF comparison and LOCF forecast exposure;
- figures: F3.4, F3.5 and F3.6 for UNRATE (PNG and PDF).

**Outputs that depend on the chain but are not regenerated by the workflow (7).** These need new code but no estimation, if a correction is ever approved:
- `forecast_origin_audit.csv`;
- `models/fit_records.{csv,parquet}`;
- `T4.7_failure_registry.csv` and `T4.7_status_counts.csv`;
- the 8 state-dependence Wald rows of `diagnostics/all_test_results.csv`;
- the output inventory.

**Outputs that mention UNRATE MSAR but do not depend on the rolling chain:** T3.1, T3.2, the residual tests and T4.3. These are full-sample fits from `pipeline.adequacy_stage`. [C]

**Baseline results reused in robustness tables [C]:**
- T4.1 compares against the baseline;
- T4.4 is the baseline at longer horizons;
- the window-length 240 row is the baseline chain re-read by the R1 workflow, whereas the original pipeline used its own T4.8 run, with the April–June 1983 difference above;
- T4.TP1 and T4.9 use the baseline forecasts.

## 3. Tooling for tasks 1, 3, 4 and 5 (built and validated; awaiting the Colab run)

`colab/r1_original_cache_audit.py` has four stages. Each refuses estimation and writes only to its output folder.

1. **verify:** every one of the 18,964 payload names and sizes against the committed inventory; a sha256 manifest of every payload; the archive-part hashes, recorded by the notebook.
2. **audit:** every MSAR, STAR and ARMA job (78 chains) under the cache-hit and live rules. Per origin it records:
   - whether each rule's key is present, and horizon coverage;
   - status, codes, starts tried and log-likelihood;
   - agreement with the stage-identified published record and, for baseline chains, with the published h=1 forecast;
   - the cache-hit key after every failed fit.
3. **candidate:** `forecasting:UNRATE|MSAR` replayed by the live rule through the pinned `run_chain`, using the live-replay layer over a **read-only** view of the original cache that refuses writes. Estimation is refused, and any estimator call aborts.
   - If any origin is absent, or any payload lacks the horizons 1, 3, 6 and 12, it **stops** (task 9). It then lists the missing origins and horizons and the minimal additional computation that would supply them.
4. **impact:** the pinned workflow in legacy mode twice, identically: on the published outputs (the reference) and on an isolated copy carrying only the candidate chain and its audit counts. It records every changed file and cell, and the reference's reproduction of the published outputs.

`colab/r1_original_cache_audit.ipynb`, a separate read-only audit notebook rather than a Tier B batch notebook:
- verifies both checkouts, the environment, the frozen data and the identity;
- restores the complete cache and asserts 18,964 payloads;
- runs all stages;
- copies the machine-readable results to `baseline/r1_original_cache_audit/<session>/`, its only Drive write, with an sha256 manifest.

**Tests:**
- `test_r1_original_cache_audit.py` (5): notebook safety; stage-block identification of the three UNRATE MSAR(240) chains, including the 1983 conflict; the read-only view; start-set parsing.
- The Tier B notebook tests still pass.
- On the partial local cache, the tool ran end to end, and `candidate` stopped cleanly at the first absent key.

## 4. What the Colab run will answer, and what may stop it

| Task | Answered by | Possible stop (task 9) |
|---|---|---|
| 1. Completeness, counts, missing keys, duplicates, provenance and agreement for every MSAR/STAR chain | `verify` and `audit` (`audit/chains.csv`, `audit/origins.csv`) | none (read-only) |
| 3. Candidate baseline chain under the live rule | `candidate` | **an origin whose live key is absent**, or **a payload written for h=1 only** (the shared T4.8 keys make this plausible) |
| 4. Forecasts, statuses, RMSE and relative RMSE, DM/HLN, HLZ, MCS, rankings, state tables, figures | `impact` (`changed_cells.csv` and both table versions) | only if `candidate` stopped |
| 5. Optimizer sensitivity, implementation artifact and genuine failure | per-origin start sets, statuses and codes of cache, candidate and published records | none |

**If `candidate` stops,** the smallest additional computations are as follows. Each needs a separate authorisation:
- **(a) Missing multi-step forecasts only:** compute the h=3, 6 and 12 forecasts of the **already cached fitted parameters**, a deterministic forecast that fits nothing. That needs new code calling the pinned forecast routines.
- **(b) An absent key:** re-estimate exactly those origins under the live rule. That is estimation.

## 5. Task 7: the 17-chain plan and the original-cache classification (no change made)

From the 5 November audit (`tier_b_original_divergence_and_cache_audit.md`), now stated with the requested distinction:

| Chain | In the cache under the live rule | Cache reproduces the **published** chain | R1 class (unchanged) |
|---|---|---|---|
| T4.1:FEDFUNDS\|MSAR | **yes, 626/626** | **no**: 39 published post-failure fits have no warm start and exist nowhere in the cache | unavailable, so Tier B (B2 done; numbers equal to the cached live chain) |
| T4.8:UNRATE\|180:MSAR | 257/257 checked; rest from the Colab run | no at checked post-failure origins | unavailable, so Tier B |
| T4.8:UNRATE\|300:MSAR | 86/86 checked; rest from the Colab run | to be determined | unavailable, so Tier B |
| forecasting:UNRATE\|MSAR (published, not R1-replayed) | from the Colab run | known not to, at 6 post-failure origins | published |
| Zero-failure MSAR/STAR chains | rules identical | yes where present (all compared STAR origins identical) | unchanged |

The classification is **not** changed. A change needs the B1 decision and independent approval.

## 6. Procedure for the Colab run (read-only, no estimation)

1. Open `colab/r1_original_cache_audit.ipynb` at the commit given in the final message: a fresh CPU runtime, with the `GITHUB_TOKEN` secret.
2. Leave the defaults and run all. It takes about 1–2 hours and prints `Please send this folder name to Claude: audit-…`.
3. Send me that folder name. I will read the exported results from Drive (read-only), complete tasks 1, 3, 4 and 5, and commit the machine-readable audit report and the academic scientific-impact report.

The notebook writes only to `baseline/r1_original_cache_audit/<session>/` and pushes nothing. It does not interfere with B1, because it runs in its own runtime.

## 7. Files

- `colab/r1_original_cache_audit.py`: the four-stage audit tool, superseding the 5 November version.
- `colab/make_r1_original_cache_audit_notebook.py` and `colab/r1_original_cache_audit.ipynb`.
- `code/tests/unit/test_r1_original_cache_audit.py`.
- `reports/part8/corrections/r1/evidence/b3_original_cache_audit_20261106/`:
  - `unrate_msar_240_reconciliation.json`
  - `baseline_unrate_msar_dependency_map.csv`
  - `impact_stage_validation.json`
