# Correction note (CLAUDE.md §6A): baseline UNRATE MSAR warm-start artifact, Option B1 (staged)

Date: 6 November 2026. Status: **staged; approved as the selected implementation correction (6 November), not approved for publication or final aggregation**. Nothing is published.

## 1. Error and cause

**The error.** The published baseline chain `forecasting:UNRATE|MSAR` (MSAR p=4, K=2, 240-month rolling window) contains three fits made directly after a failed fit (1982-10-01, 1982-11-01, 1982-12-01) **without the approved D6 warm start**. The approved rule keeps the last usable fit's warm start after a failure.

**How it propagates.** Each fit warm-starts the next. The published estimates therefore differ at 9 consecutive origins, 1982-10 to 1983-06, until the paths rejoin.

**Cause** (plausible, not proven). When the final run resumed, it replayed the cache under the pinned cache-hit rule. That rule resets the warm start from a failed fit's payload, which stores none. The result was a cold start where an uninterrupted run would have used the warm start (`tier_b_warm_start_continuity.md`).

**The methodology is unchanged.** D6 warm starts are part of the approved implementation. The correction restores them and changes no locked element of Part 5.

## 2. Code changed

**No scientific code changed.** The pin `8aaa4217…` is untouched.

**New orchestration code** (non-estimating):
- `colab/r1_b1_staged_correction.py`: builds the staged tree;
- `colab/r1_b1_validate_staged.py`: independent validation;
- `reports/part8/corrections/r1/b2_scientific_review.py`: the B2 comparison.

**Fixed analysis code:** `reports/part8/corrections/r1/b3_stage2_analysis.py` (keyed MCS merge).

## 3. Affected outputs

38 content files. The list is `reports/part8/corrections/r1/evidence/b1_staged_20261106/baseline_unrate_msar_dependency_map_v3.csv`.

## 4. Regeneration

All 38 files were regenerated in staging (`output_staging/r1_b1_unrate_msar_20261106/`) and validated (`evidence/b1_staged_20261106/validation/validation.json`, all checks passed).

## 5. Superseded and corrected outputs are distinguishable

- The published `output/` is unchanged.
- Every changed row carries `run_id = b1-staged-20261106T154902Z`.
- Every changed figure has an updated sidecar with a `b1_correction` field.
- `STAGED_FILES.csv` maps each staged file to the published sha256 it supersedes.
- Cell-level before/after: `evidence/b1_staged_20261106/validation/staged_vs_published_cells.csv.gz`.

## 6. Revision, 6 November 2026 (integration preparation)

**Counter provenance.** The staged origin-audit row's `origins_from_cache = 704` and `cache_horizon_misses = 0` describe the corrected replay. The historical execution's 691 and 13 are kept in `output_staging/r1_b1_unrate_msar_20261106/COUNTER_PROVENANCE_forecast_origin_audit.csv`, and the published table still carries them.

**Rendering reproducibility.**
- *Changed (orchestration and tests only):* `colab/r1_render_guard.py`, `colab/matplotlibrc.default`, the builder, the validator and `code/tests/conftest.py`.
- *Not changed:* no scientific code.
- *Check:* a deterministic rerun of the builder reproduced all 461 staged files byte for byte.

**Further implementation error found: F4.8 not re-rendered by the R1 workflow (§6A).**
- *Error:* the pinned R1 workflow regenerates `robustness/window_length_comparison.csv` but not F4.8.
- *Affected:* F4.8_UNRATE (png, pdf) in the provisional releases `0573a8c`, `3bd24c4` and `292227e`. Its plotted inputs changed under F1, but the figure did not.
- *Code:* none changed yet. The checker is `reports/part8/corrections/r1/f48_staleness_check.py`.
- *Regeneration:* planned in the final integration (stage 3 of `part8_final_integration_plan.md`).
- *Distinguishing superseded outputs:* the releases are not edited; the stale files are listed in `evidence/integration_prep_20261106/f48_staleness/`.

## 7. Further findings while implementing the integration dry run (6 November 2026)

Full detail: `reports/part8/corrections/r1/part8_integration_dryrun_implementation.md` §5.

**(a) Stale Wald rows in `diagnostics/all_test_results.csv` (§6A).**
- *Error:* the pinned R1 workflow regenerates T3.5 but copies the state-dependence and joint Wald rows of `all_test_results.csv` unchanged.
- *Affected:* in releases `0573a8c`, `3bd24c4` and `292227e`, all 24 UNRATE Wald rows still carry the published values, while T3.5 changed under F1.
- *Code:* `colab/r1_integration_dependents.rebuild_wald` (orchestration; reproduces all 134 base rows first).
- *Regeneration:* stage 3 of the integration dry run.
- *Distinguishing superseded outputs:* the releases are not edited.

**(b) Reconciliation with non-reproducing re-estimated chains (orchestration).**
- *Error:* the pinned `workflow.reconcile` restores the base value wherever the legacy and corrected runs agree. With B2's chains this would print superseded values (for example FEDFUNDS T4.1 MSAR `n_failed` 52 instead of 49).
- *Prevented by:* `reconcile_chain_aware`, used only in the dry run.
- *Effect on existing outputs:* no published output was affected. The Tier A release used closed-form AR chains, which reproduce exactly.

**(c) F8 authorisation.** F8 was never confirmed, but the pinned flag is on by default, so it was active in `3bd24c4` and `292227e`. The dry run switches it off.

## 8. Integration dry-run stage-2 refusal (7 November 2026): orchestration error

**Error.** The dry run's replay hook subclassed the pinned `RefitCache`, whose constructor writes `README_R1_REFIT_CACHE.txt` into the cache folder. The strict check then found the merged refit cache changed (Colab session `integration-20261107T184004Z-93c0f8`).

**Scope of the error:**
- *Payloads:* no payload was changed.
- *Estimation:* none took place.
- *Outputs:* no output was affected, because the run stopped.

**Code changed (orchestration only):**
- `colab/r1_integration_common.readonly_refit_class` and `readonly_refit_replay`;
- the strict, file-level cache checks in stages 2–4.

**Pinned code:** unchanged.

**Report:** `reports/part8/corrections/r1/part8_integration_stage2_cache_fix.md`.
