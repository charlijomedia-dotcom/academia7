# Validation evidence: Part 8 report drafts and archive procedure (8 November 2026)

These are read-only checks. No estimation was run, and nothing was published or archived.

| File | What it is |
|---|---|
| `integrated_numbers.json` | The integrated values quoted in `reports/part8/drafts_integrated_20261108/`. Built by `../../integration_numbers.py` from the claims-reference release (`0573a8c`) and the audited `cells_vs_claims_reference.csv.gz` of session `integration-20261108T052245Z-9bba8e` |
| `rebuild_crosscheck_vs_local_rehearsal.json` | Differing cells between the rebuilt tables and the local rehearsal. The value is 0 for every table that does not depend on the Drive-only B1/B3 chains. The non-zero tables are the T4.1 and window-length tables, which the local rehearsal does not hold |
| `registry_reason_codes_local_rehearsal.json` | T4.7 reason-code counts from the local rehearsal: 34,122 rows, equal to the candidate's count. Not cross-checked cell by cell |
| `number_checks.csv` | 105 checks: each quoted fragment is present in its draft and equals the integrated value at the quoted precision. **105 / 105 pass** (`../../check_draft_numbers.py`) |
| `archive_gate_smoke_test_local_rehearsal.json` | The archive inventory gate run on the local partial rehearsal. It is **refused** as it should be, refusing exactly 3 files: F4.8_UNRATE.png and .pdf (source category differs) and `correction_file_comparison.csv`. 360 files are identical and 101 provenance-only |

## Tests

Run on 8 November 2026 with `python -m pytest -q -p no:cacheprovider tests/unit -m "not network"` in `my-thesis/code`.

| Run | Result |
|---|---|
| Full unit suite, before the notebook was generated | 611 passed, 1 skipped. The skip is the committed-notebook equality test, which needs the generated notebook |
| `tests/unit/test_r1_integration_archive.py` | 20 passed, 1 skipped before generation; **21 passed** after generating the notebook pinned to `d37f77f` |

## Revision of 9 November 2026

- **Archive.** `archive-20261109T080914Z-3c7d68` is verified in `../../archive_verification_20261109.md`, with evidence in `../archive_verification_20261109/`.
- **T4.7 reason codes.** The counts in `registry_reason_codes_local_rehearsal.json` equal the counts of the archived `T4.7_failure_registry.csv`: 34,122 rows; 512 failed and 33,610 fragile; all 17 category/reason-code counts. The independent review checked this on the archived file.
  - Row-by-row identity of the rehearsal file and the archived file is not established: the byte size is equal, but the sha256 differs because of run provenance.
- **`c16_ar2_common_sample_audit.json`.** The baseline AR(2) h=1 RMSE and MAE on the T4.2 common sample, an [audit] computation from stored forecasts with no estimation.
  - It presumes the dropped date is target 1974-10, the only failed p=12 fit. The T4.2 chain forecasts are not stored, so this is not verified date by date.
- **`number_checks.csv`.** 128 checks, now including the candidate claim matrix; **128 / 128 pass**.
