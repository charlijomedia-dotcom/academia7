# Part 8 reports — index

These reports cover audited run `baseline-20261030T173044-949fcd76`.

- **Results commit:** `066294544e8f`, on branch `part8-results/baseline-20261030T173044-949fcd76`. The commit is unchanged.
- **Code commit:** `46a53181e5e9`.

## Files

| File | Content |
|---|---|
| `full_empirical_analysis_report.md` | The complete audit (sections A–G), with a source-key table and limitations |
| `main_findings.md` | The principal findings and their claim statuses |
| `robustness_findings.md` | Each robustness exercise: T4.1–T4.9, T4.TP1 and T4.8 |
| `jury_resolution_status.md` | The status of every Part 2 remark ID and of V-04 to V-07 |
| `final_claims_allowed.md` | The permitted wording for Part 9, and the claim-matrix handling |
| `claim_evidence_matrix_adjudicated.csv` | The adjudicated claim matrix: the P-04 row plus C01–C23 |
| `audit_derived_diagnostics.py` / `.csv` | Read-only audit recomputations, marked **[audit]** in the reports. They are not thesis results. |

The related correction proposals, which are awaiting approval, are in `notes/claude/part8_audit_findings_and_correction_proposals_2026-11-01.md`.

## Integrity

- On `part8-final-audit` (commit `337b84b`), no file under `output/`, `data/`, `code/`, `approved-specs/` or `source-materials/` was modified.
- On `part8-corrections`, only non-fit-critical code under `code/src/thesis/` and `code/tests/` changed (listed in `corrections/correction_plan.md` §1). `output/`, `data/`, `approved-specs/`, `source-materials/`, the configuration files and every fit-critical file are unchanged.

## Correction phase (2 November 2026)

Branch `part8-corrections` implements the approved corrections F1–F4 and the F6 numerical review. **No output has been regenerated.** The reports above therefore audit the *original* publication, commit `0662945`, with provisional findings marked.

The evidence is in `corrections/`:

| File | Content |
|---|---|
| `correction_plan.md` | Files changed, cache evidence, tests, outputs to regenerate, targeted execution plan, decisions needed |
| `cache_compatibility_check.py` / `.json` | Fit-cache identity `3413465b508bb844` unchanged; cached fits reused 23/23 with bit-identical raw forecasts |
| `f2_mcs_validation.py` / `.csv` | Guarded MCS identical to `arch` in 138/138 cells where `arch` works; completes the cells where `arch` fails |
| `f2_scale_invariance_check.py` / `.csv` | Independent check of the overflow-guarded cells |
| `f4_zivot_andrews_preview.py` / `.csv` | Zivot–Andrews on UNRATE and FEDFUNDS levels; decisions unchanged |
| `f6_k3_nesting_feasibility.py` / `.csv` | Nesting-informed K=3 start, as a study only (T4.3 is not modified) |

These files are audit evidence, not thesis outputs (CLAUDE.md §9).
