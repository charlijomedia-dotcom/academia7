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

- No file under `output/`, `data/`, `code/`, `approved-specs/` or `source-materials/` was modified on this branch.
- To check, run `git diff 0662945 --stat`. It lists only `reports/part8/` and the note under `notes/claude/`.
