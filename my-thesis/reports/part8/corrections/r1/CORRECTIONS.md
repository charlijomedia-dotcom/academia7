# Correction log: R1 corrected release of the Part 8 evidence

Original run: `baseline-20261030T173044-949fcd76`. Original code: `46a53181`. Original results commit: `066294544e8ff84f3c2c73ab647c8d13331dcac1` (unchanged).
Correction code: branch `part8-r1-rescore`, commit `77df9d8`. The correction run ID is recorded in `manifests/correction_run_manifest.json` of the release.

The original output tree is not modified. The corrected release is a copy of that tree. Each regenerated file replaces its original, and every replacement is listed in `manifests/correction_file_comparison.csv` and `manifests/output_inventory.csv` (columns `source` and `original_sha256`).

## Corrections applied (all approved; methodology unchanged)

| ID | Kind | What changed in the code | Outputs affected |
|---|---|---|---|
| F1 | implementation error | A forecast from a FAILED fit is excluded from every score and test. The raw value is kept in the `failed_raw_forecast` column. | Every UNRATE AR-relative number. Forecast files gain the `failed_raw_forecast` column. |
| F2 | implementation error | When the `arch` MCS fails (ties; variance overflow), the guarded `hln_mcs_r` runs the same procedure (same loss, alpha, block length, replications, seed). The admissible set is not changed and no observation is dropped. | 22 CPI and M2SL cells of T3.4 that were "unavailable", and 2 CPI cells of the 240-month window MCS |
| F3 | reporting error | Pairwise tests are oriented competitor minus benchmark, with explicit `benchmark` and `competitor` columns. | Signs and one-sided p-values in T3.3A and T3.3B. Two-sided p-values and decisions change only through F1. |
| F4 | omitted required output | Zivot–Andrews tests for UNRATE and FEDFUNDS levels are reported (Part 5 §3.2 / P-02). They are not used by the §3.4 rule. | T2.2, T2.2 decisions, `all_test_results`, F2.1 figures |
| F7.1 | reporting error | The data dictionary shows the transformation chosen by the §3.4 rule. | T2.1 |
| F8 | presentation error (found in the R1 figure review, 2 November 2026; **awaiting your confirmation**) | F3.4's main panel omits flagged values, and the title says so. The diagnostic panel uses a labelled symmetric-log axis when flagged values exceed 100 times the data range. Nothing is clipped (Part 5 §13.1) | F3.4 figures only; no number changes |

F5: interpretation only, so no code change. F6: not implemented. UNRATE K=3 remains inconclusive, and see the unresolved limitation below.

## How each number was obtained

- **recomputed_from_published**: recomputed from the published forecasts and origin audits. No model was estimated.
- **original_retained_unaffected**: a published row that no correction touches. It keeps its original provenance.
- **original_retained_pending_estimation**: a published row that a correction would change, but whose forecasts were never published. It is kept unchanged and marked, and is not to be quoted as corrected. The exact list and cost are in `estimation_workload.csv`.
- Every cell that the corrections do not change keeps the original published text, including its last digits. This was established by a legacy run (all corrections off) on the same machine, which reproduced the published tables (`legacy_comparison.csv`). Changed cells carry values computed on this machine.

## Unresolved limitations carried into the corrected release

1. **F6 (numerical optimisation).** The approved MSAR multistart does not guarantee the global maximum. UNRATE K=3 (log-likelihood 13.88 < K=2 102.04, although K=3 nests K=2) is inconclusive. INDPRO has an alternative K=3 optimum, and the optimum is sensitive to the platform. No claim of a global maximum is made. The multistart specification is unchanged.
2. **Pending estimation.** T4.1 alternative-transformation rows (UNRATE, FEDFUNDS), T4.2 (CPI AR lags) and T4.8 UNRATE at 180 and 300 months keep their original values. Those values are marked `original_retained_pending_estimation`.
   *Status update, 6 November 2026:* the estimation for these rows has since been done in Tier A and in Tier B batches B1, B2 and B3, all certified. It has **not yet been aggregated** into the release. The integration plan is `part8_final_integration_plan.md`.
3. **F1 and F2 dependence.** Findings that rest on the F1 masking rule or on the guarded MCS are marked provisional in the claim matrix.
4. **Multiplicity.** The Holm qualification of CPI h=12 is retained.
5. **Platform.** Re-estimated MSAR or STAR chains would not be bit-identical to the original Colab estimates. They would be labelled `re-estimated` and never mixed with original chains within an exercise.
