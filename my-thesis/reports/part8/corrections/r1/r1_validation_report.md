# R1 — correction from the published forecasts: implementation, validation and workload

Date: 1 November 2026. Authorisation: Option R1 (user, 1 November 2026). Part 9 is not started.

- **Original results.** Commit `066294544e8ff84f3c2c73ab647c8d13331dcac1`, run `baseline-20261030T173044-949fcd76`, code `46a53181`. Neither has been modified.
- **Implementation.** Branch `part8-r1-rescore`, commit `77df9d8`.
- **Corrected release.** Branch `part8-corrected-results/r1-20261101`, tree `output_corrected/`, run `correction-20261101T152213-949fcd76`. Every regenerated file carries `code_commit_sha = 77df9d8e8b78…`. The data snapshot hash `7e7dc769…` and the config hash `949fcd76…` are unchanged.

## 1. What the workflow does

`code/tools/correct_from_published.py` (package `thesis.correction`) runs the approved pipeline's evaluation and robustness stages. It does not run the estimation stage. Instead, it rebuilds every baseline forecast chain from the published sources:

- `forecasts/forecasts_*.parquet`;
- `forecasts/forecast_origin_audit.csv`;
- `diagnostics/T2.5_selected_specs.csv`, so that no specification is re-selected.

Stationarity tests are recomputed, because they are deterministic and F4 and F7.1 need them. No fit-critical file changed, so the fit-cache identity (`3413465b508bb844`) is unchanged.

Each robustness chain is taken whole from exactly one of four sources, in this order:

1. The published baseline-equivalent chain.
2. A complete fit-cache replay through `rolling.run_chain`, with estimation disabled. This needs `--cache-root`. A missing fit raises an error; it is never estimated.
3. Re-estimation, but only for a task ID passed with `--approve`. The result is labelled `re-estimated`.
4. Otherwise the chain is unavailable, and the original rows are kept with `correction_status = original_retained_pending_estimation`.

Sources are never mixed within a chain or within a compared set. Merged tables keep the original row order. Recomputed rows carry the new provenance; retained rows keep the original provenance and a `correction_status`.

## 2. Validation gate: the workflow reproduces the published tables (corrections off)

`--legacy` turns F1, F2, F3, F4 and F7.1 off. Result at `77df9d8` (`legacy_comparison.csv`):

| Files regenerated | Byte/text-identical | Equal within FP tolerance | Different |
|---|---|---|---|
| 92 | 83 | 9 | **0** |

"Equal within FP tolerance" means the relative difference is ≤ 1e-9 and every non-numeric cell is identical. The nine files, with their largest relative differences, are:

| File | Max rel. diff |
|---|---|
| T2.2 | 1.0e-11 |
| T3.3A | 3.1e-15 |
| T3.3B | 1.4e-15 |
| T3.3 | 1.6e-15 |
| T3.5 regression | 5.5e-13 |
| T4.4 tests | 1.6e-15 |
| T4.5 comparison | 6.9e-15 |
| T4.5 tests | 3.4e-14 |
| window-length tests | 1.4e-15 |

The comparison covers every series, horizon, model, comparison and statistic in the regenerated tables, plus their Parquet twins and the figures.

**Attribution of the last-digit differences.** I ran the original approved code (a worktree of `46a53181`) on this machine.

| Quantity | Original code, this machine | R1 workflow, this machine | Published (Colab) |
|---|---|---|---|
| HLZ, GDPC1 AR–MSAR h=1 | 1.9881017620480337 | 1.9881017620480337 | 1.9881017620480346 |
| ADF, GDPC1 log level | −2.46652878779216 | −2.46652878779216 | −2.466528787792159 |

The original code and the R1 workflow agree on this machine, and both differ from Colab in the same way. The differences therefore come from the platform (CPU/BLAS), not from the workflow.

The test `tests/unit/test_r1_correction.py::test_legacy_mode_reproduces_published_tables` repeats this gate.

**Re-estimation path.** I re-estimated the four T4.2 AR chains with corrections off. They reproduce the published T4.2 to within a relative difference of 1.2e-14. This is evidence that AR re-estimation does not depend on the platform.

## 3. Corrected release: what changed and why

The full account is in three files:

- `file_changes.csv`: one row per file, with the correction and the scientific reason;
- `cell_changes.csv`: 2,918 cells, each with its original and corrected text;
- `decision_changes.csv`: every changed decision, significance mark or support classification.

The release has 61 files that differ from the original. There are 56 regenerated files and 5 correction records: the run manifest, the summary, the per-file comparison, the new inventory, and a copy of the original inventory. The original inventory is kept as `manifests/original_output_inventory.csv`.

**No cell differs only at floating-point level.** The legacy run showed which cells the corrections leave untouched. Every such cell keeps the original printed text (`reconciliation.csv`). Every changed cell is a value, sign or text change caused by F1–F4 or F7.1:

- 2,196 value changes;
- 606 sign changes;
- 116 text changes.

### Changes by correction

**F1 (UNRATE AR benchmark): 46 files.**
- The published AR benchmark scored the UNSTABLE_AR forecasts of origin 2020-04: 31.6, 93.4, 304.2 and 2,063.6 at h = 1, 3, 6 and 12. These are now excluded, and the raw values are kept in `failed_raw_forecast`.
- Only AR failures had finite forecasts. Every other failed forecast row in the baseline was already missing: 60 ARMA and 44 MSAR rows for UNRATE, and 28 ARMA rows for FEDFUNDS. No other target is touched.

**F2: 24 MCS cells (22 in T3.4, 2 in the 240-month window MCS) that were "unavailable" now have sets.**
- These cells are CPI h = 1, 3, 6, 12 and M2SL h = 3, 6, 12.
- The procedure is the same; only the guarded `hln_mcs_r` implementation is used, and only where `arch` failed. The column `mcs_implementation` identifies it.
- MSAR and STAR are retained in every one of these cells. ARMA is excluded in five CPI cells (h = 3 absolute at 90% and 95%; h = 6 absolute at 90% and 95%; h = 6 squared at 90%).

**F3: 606 sign-only cells in T3.3A and T3.3B.**
- New `benchmark` and `competitor` columns.
- One-sided p-values swap where the published orientation was benchmark minus competitor.
- No two-sided p-value or decision changes through F3.

**F4.** Four Zivot–Andrews rows (UNRATE and FEDFUNDS levels; initial window and full sample) are added to T2.2 and `all_test_results`. ZA columns are added to the T2.2 decisions table, and the break dates are marked in the F2.1 figures. The §3.4 decisions are unchanged.

**F7.1.** T2.1 now shows the chosen transformation and its sample dates for the two decision-rule series.

### Substantive effect (UNRATE)

| | Published | Corrected |
|---|---|---|
| AR RMSE, h = 1 / 3 / 6 / 12 | 0.886 / 3.277 / 11.31 / 78.17 | 0.551 / 0.942 / 1.166 / 1.492 |
| h=1 OOS R² vs AR: ARMA / MSAR / STAR | 0.323 / 0.690 / 0.554 | 0.237 / 0.190 / −0.103 |
| h=1 RMSE rank: AR / ARMA / MSAR / STAR | 4 / 3 / 1 / 2 | 2 / 4 / 1 / 3 |
| AR rank, h = 3 / 6 / 12 | 3 / 3 / 3 | 1 / 1 / 2 |
| MSAR OOS R² vs AR, h = 3 / 6 / 12 | 0.894 / 0.985 / 0.999 | −0.128 / −0.538 / −0.959 |
| STAR vs AR, h = 1, absolute loss (HLZ) | −1.18, p = 0.47 | **+5.49, p = 0.0015 (STAR worse)** |

New rejections all go against the nonlinear model:

- STAR is worse than AR at h = 1 under absolute loss. This holds for HLZ and DM-HLN, in T3.3, T4.4, T4.5 and the 240-month window table.
- Under DM-HLN only, STAR is also worse at h = 3 absolute (HLZ p = 0.057).
- No nonlinear-over-AR rejection appears anywhere.

The MCS membership for UNRATE is unchanged; only the MCS p-values change.

## 4. Outputs that cannot be rebuilt from published files

The published release contains forecasts only for the baseline chains. The chains below would change under F1 but were never published, so their original rows are retained and marked pending.

All other non-baseline chains are unaffected by every correction, so their published rows stand as correct. In those chains:

- there is no AR failure;
- no MCS cell is unavailable;
- F3 does not apply.

Every failure in those chains (for example the 22 ARMA failures for UNRATE at 180 months, or the 7 ARMA failures for FEDFUNDS at 180 months) has a missing forecast, as in the baseline.

The cost per fit is the original run's mean `wall_seconds` for the same target and model (`estimation_workload.csv`, produced by `estimation_workload.py`).

| Exercise | Chains | Origins | CPU hours |
|---|---|---|---|
| T4.2 CPI AR p = 1, 3, 6, 12 | 4 AR | 2,860 | < 0.01 |
| T4.1 UNRATE, alternative transformation | AR, ARMA, MSAR, STAR | 4 × 703 | 18.3 (MSAR 12.6, ARMA 5.4) |
| T4.1 FEDFUNDS, alternative transformation | AR, ARMA, MSAR, STAR | 4 × 626 | 2.3 (MSAR 2.0) |
| T4.8 UNRATE, 180-month window | AR, ARMA, MSAR, STAR | 4 × 764 | 19.9 (MSAR 13.7, ARMA 5.9) |
| T4.8 UNRATE, 300-month window | AR, ARMA, MSAR, STAR | 4 × 644 | 16.8 (MSAR 11.5, ARMA 4.9) |
| **Total** | **20 chains (8 AR, 4 ARMA, 4 MSAR, 4 STAR)** | **13,808** | **≈ 57.4 CPU hours** |

**Why the MSAR and STAR chains cannot be avoided for T4.1 and T4.8 UNRATE.** Masking the failed AR origin removes that date from the common sample. That changes every AR-relative statistic of every competitor. Those statistics need the competitors' per-origin forecasts, which were not published.

The only alternative that avoids re-estimation is to recompute the AR-only accuracy rows (cheap) and leave the pairwise rows pending. I do not recommend it: it would make a table partly corrected.

**Wall-clock time.** MSAR and STAR chains are warm-started, so each chain runs sequentially. The shortest possible wall-clock time is the longest chain: about 13.7 hours (UNRATE MSAR, 180-month window), with at least 16 workers. On 2 workers it would take about 30 hours.

**Fit cache.** Some or all of these chains may already be fully cached in the restored Drive fit cache: the preflight found 22,358 hits, but the result is incomplete. `--cache-root` replays a chain only if every origin hits, so running R1 on Colab with the cache root first costs no estimation. That run would shrink this list before any refit is approved.

**Proposed approval tiers (nothing has been launched):**

- **Tier A: the eight AR chains, < 1 CPU minute.**
  - It covers T4.2 in full, and the AR chains of T4.1 and T4.8 UNRATE.
  - Preview, not in the release: re-estimated T4.2 under F1 has 714 common dates (was 715). RMSE for p = 1 / 3 / 6 / 12 is 3.075 / 2.958 / 2.969 / 2.967. As published, only p = 3 rejects against the p = 1 reference, under absolute loss (HLZ p = 0.013). The conclusion is unchanged.
  - T4.1 and T4.8 stay pending until Tier B, because those exercises are all-or-nothing per series.
- **Tier B: 4 ARMA, 4 MSAR and 4 STAR chains, ≈ 57 CPU hours.**
  - These would be labelled `re-estimated`. They are platform-dependent (F6), and would never be combined with original competitor chains within an exercise.

## 5. Remaining risks

1. **F6.** A re-estimated MSAR chain will not be bit-identical to the original Colab chain. Warm starts propagate any optimiser difference. The MSAR multistart guarantees no global optimum, which is the documented unresolved limitation. Any Tier B result must be reported as a re-estimate, separately from the original run.
2. **F1 and F2 are corrections by rule.** Claims that rest on the F1 masking rule or on the guarded MCS stay provisional (`claim_evidence_matrix_corrected.csv`) until you re-audit the corrected release.
3. **Pending rows.** C14, C15 and C16 still rest partly on original rows that F1 would change. They must not be quoted as corrected until Tier A and Tier B are resolved.
4. **Cache replay.** The replay path is implemented and unit-tested, but it has not run against the real Drive cache, because this container has no cache.
5. **Platform digits.** Changed cells carry values computed on this machine, not on Colab. The legacy gate bounds the platform effect at a relative difference of ≤ 1e-11.
6. **Figures.** The legacy figures are byte-identical to the originals. The corrected figures were checked for presence and provenance only, not compared visually against a reference.
7. **Holm.** The CPI h=12 Holm adjustment is unchanged at 0.204 (absolute) and 1.0 (squared). It remains an audit computation, not an approved table.
