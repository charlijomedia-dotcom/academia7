# Source of truth for Part 8 numbers (decision of 9 November 2026)

## Decision

The canonical thesis-facing numbers are the files in **`my-thesis/output/` of the release commit** on branch **`part8-corrected-results/final-20261109`**.
- There are 465 files.
- Each is listed with its sha256 in `my-thesis/release/part8_final/release_inventory.csv` of the same commit.
- The release commit SHA is recorded in `PUBLICATION.md` here once the release is published and verified.

Part 9 may quote a number only from that commit. Before quoting, it checks the file against `release_inventory.csv` (§4).

## Why `output/` and not `output_corrected/`

1. **CLAUDE.md §9** requires that every exact empirical number used in the thesis be traceable to a file under `output/`. **Part 5** (`part5_required_outputs_specification.md`) also names every required output by its `output/` path.
   - Placing the final release in `output_corrected/` would leave §9 pointing at the superseded baseline.
   - That arrangement was right for the three **provisional** releases (`0573a8c`, `3bd24c4`, `292227e`), which were not thesis-facing. It is not right for the final one.
2. **Superseded values stay out of the canonical path.**
   - The release commit's parent is the scientific pin `8aaa4217`. There, `my-thesis/output/` holds the original baseline (`0662945`, 461 files).
   - In the release commit **every one of those 461 files is replaced** by its final version (identical where the corrections did not change it), and the four correction manifests are added.
   - No baseline file is left beside a corrected one, and nothing is deleted. This was checked: the 461 baseline paths are a subset of the 465 release paths.
3. **The baseline is preserved, not overwritten.**
   - The original publication stays unchanged at `0662945` (branch `part8-results/baseline-20261030T173044-949fcd76`) and in the pin's history.
   - The release is a **new** commit on a **new** branch; no history is rewritten.
   - CLAUDE.md §6A.5 asks that superseded and corrected outputs stay distinguishable. They are, by commit and branch, by the inventory's `source` column, and by the release record.
4. **Provenance.** Each file keeps its run identity, as the CLAUDE.md §8 provenance fields require.
   - Regenerated tables carry run `correction-20261109T080220-949fcd76` in their provenance columns. That is the archived reconstruction, equivalent to the audited run `correction-20261108T053328-949fcd76`.
   - Unchanged original files keep `baseline-20261030T173044-949fcd76`.
   - The 12 F8 figures' sidecars name both the numbers' run and the F8 re-render operation.

## What is NOT a source of truth

| Location | Why not |
|---|---|
| `my-thesis/output/` on `part8-r1-rescore`, the pin `8aaa4217`, `0662945`, or any branch other than the release branch | the **superseded** original baseline (for example, UNRATE AR RMSE 0.886 instead of 0.551) |
| `my-thesis/output_corrected/` on the three provisional release branches | provisional, superseded |
| The candidate archive `archive-20261109T080914Z-3c7d68` | the same numbers as the release, but the pre-F8 F3.4 figures; kept as the audit record |
| Report prose and `[audit]` numbers in `reports/` and `notes/` | not results (CLAUDE.md §9). The `[audit]` sensitivities, such as the C16 714-date AR(2) comparison, are not citable as thesis numbers |
| `output/manifests/claim_evidence_matrix.csv` in the release | the pipeline-registered single P04 row with empty fields; the claim statuses are in `claim_evidence_matrix_final.csv` here |

## How Part 9 checks a number

```bash
git fetch origin part8-corrected-results/final-20261109
C=<release commit from PUBLICATION.md>
git show $C:my-thesis/output/forecast_tests/T3.3_main_forecast_table.csv | sha256sum
grep '^forecast_tests/T3.3_main_forecast_table.csv,' <(git show $C:my-thesis/release/part8_final/release_inventory.csv)
```

The two sha256 values must be equal. The allowed wording and statuses are in `final_claims_allowed.md` and `claim_evidence_matrix_final.csv` in this directory.
