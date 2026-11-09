# Final Part 8 reports: change log

**Source.** These reports are the accepted drafts of `drafts_integrated_20261108/`, built by `corrections/r1/make_final_reports.py`. The drafts' history is in `CHANGELOG_drafts.md`.

## Changes from the drafts

These change presentation and status only. No number, claim status (apart from R1-06, handled below) or limitation changes.

| Where | Change |
|---|---|
| Titles | "(integrated candidate, draft)" → "(final)" |
| Banners | The draft banner is replaced by the final banner: release `part8-final-20261109`; authoritative numbers in `my-thesis/output/` of the release commit; superseded locations named; three identities (numbers run, archive, F8); a **publication status**, pending until `finalize_reports.py` records the verified publication |
| Path wording | "`output/`-relative paths of the candidate tree" → "relative to `my-thesis/output/` in the release commit" |
| R1-06 and F8 passages | Wrapped in `<!--PUB:…-->` markers. **Pending state:** R1-06 is PARTIALLY ADDRESSED until the release containing the F8 figures is published, so the jury counts are 15 / 3 / 0 / 11. **After verified publication** (`finalize_reports.py` only): RESOLVED, 16 / 2 / 0 / 11 |
| Claims §4 | The final machine-readable matrix is `claim_evidence_matrix_final.csv`. The pipeline-registered `output/manifests/claim_evidence_matrix.csv` is not a source of claim statuses |
| Matrix | `claim_evidence_matrix_final.csv`: the candidate matrix with `candidate_source` = the release, and `provisional = True` pending publication. The finalizer sets `False`, keeping F6 for P04-regime-count and C18 |
| New | `SOURCE_OF_TRUTH.md` (the canonical-path decision); `finalize_reports.py` |

## Retained limitations

All are retained unchanged:
- F6 (UNRATE K=3 inconclusive; no global MSAR maximum);
- B2 optimiser sensitivity;
- multiple testing (nominal p-values; Holm figures as audit sensitivities);
- degenerate STAR tests (numerical instability is not inference);
- sample-, window- and transformation-dependent rankings (C21, C14, C15);
- C16 QUALIFIED, with the 714-date AR(2) comparison an [audit] sensitivity whose alignment is inferred;
- the M2SL diagnostic-panel overlap (accepted presentation limitation).

**Validation.** `corrections/r1/evidence/part8_drafts_20261108/number_checks_final.csv`: 128 / 128 pass on these reports.
