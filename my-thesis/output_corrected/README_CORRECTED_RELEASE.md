# Corrected release R1 (provisional)

- **Correction run:** `correction-20261101T152213-949fcd76`.
- **Correction code:** branch `part8-r1-rescore`, commit `77df9d8`.
- **Source:** the original release `../output/`, run `baseline-20261030T173044-949fcd76`, results commit `066294544e8ff84f3c2c73ab647c8d13331dcac1`.
- **No model was estimated.** Every regenerated number is recomputed from the published forecasts and origin audits.
- **Cells the corrections do not change** keep the original printed text.

Read these files first:

- `manifests/correction_file_comparison.csv`: every file against the original;
- `manifests/output_inventory.csv`: the `source` and `original_sha256` of each file;
- `manifests/correction_run_manifest.json` and `manifests/correction_summary.json`;
- `reports/part8/corrections/r1/` on branch `part8-r1-rescore`: the correction log, validation report, cell-level changes and the corrected claim matrix.

Rows that F1 would change, but whose chains were never published, carry `correction_status = original_retained_pending_estimation`. They must not be quoted as corrected. They are:

- T4.1 alternative transformations (UNRATE, FEDFUNDS);
- T4.2 (CPI AR lags);
- T4.8 UNRATE at the 180- and 300-month windows.

This release is provisional until it is re-audited and approved. The F6 MSAR optimisation limitation is unresolved.
