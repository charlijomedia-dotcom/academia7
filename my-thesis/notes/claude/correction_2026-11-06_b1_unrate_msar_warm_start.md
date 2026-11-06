# Correction note (CLAUDE.md §6A): baseline UNRATE MSAR warm-start artifact, Option B1 (staged)

Date: 6 November 2026. Status: **staged, awaiting independent review**. Nothing is published.

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
