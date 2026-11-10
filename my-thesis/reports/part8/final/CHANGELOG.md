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

## Publication (10 November 2026)

| Where | Change | How |
|---|---|---|
| All five reports and the matrix | Publication markers replaced. The banner now names the published commit `9817daf91ac4cb4aaa42c2bef5deaff5b674841b`, the Drive folder and the tar sha256. **R1-06 RESOLVED** (jury: 16 resolved / 2 partial / 0 / 11). The matrix is non-provisional, with F6 kept for P04-regime-count and C18 | `finalize_reports.py`, with its remote check enabled, on the `publication_status.json` read from the final Drive folder |
| `jury_resolution_status.md` | "Basis of the statuses", R1-22 and V-07 describe the published release (they lay outside the markers). Formal Part 8 approval is stated as pending the closure review | manual, recorded here |
| `full_empirical_analysis_report.md` G | "Resolved on the integrated candidate (subject to approval and publication)" → "Resolved (in the published release …; formal Part 8 approval pending the closure review)" | manual, recorded here |
| `SOURCE_OF_TRUTH.md` | The published commit is named, including in the Part 9 check | manual |
| New | `PUBLICATION.md` (identities and verification) and `publication_status.json` (a byte copy of the Drive file) | finalizer, then the provenance section appended |

**Unchanged.** No number or claim status changed apart from R1-06. P-04 stays PARTIALLY ADDRESSED (UNRATE K=3 INCONCLUSIVE, F6). C16 stays QUALIFIED. All other limitations are retained.

**Validation** (`corrections/r1/evidence/part8_final_publication_20261110/`):
- the published commit verifies against its inventory and the archive;
- the integrated tables equal the published files in all 2,665,073 cells;
- all cited `output/` paths exist at the commit;
- number checks pass 128 / 128.

## Closure corrections (10 November 2026; documentation only)

These follow from the closure review of `b1fcc77`.

| Where | Change |
|---|---|
| `claim_evidence_matrix_final.csv` | All 24 `allowed_wording_ref` entries now point to the claim sections of `reports/part8/final/final_claims_allowed.md`, as `§n, Cxx`. P04-regime-count points to §3 C18, its P-04 claim; until now they pointed to the drafts. **No other column changed:** statuses (13 / 8 / 3), evidence, limitations and provisional flags are as before |
| `final_claims_allowed.md`, purpose | `claim_evidence_matrix_final.csv` is named as the authoritative final matrix. The earlier matrices are listed as historical and superseded |
| `final_claims_allowed.md`, general restrictions | "from the candidate once it is published" → "from `my-thesis/output/` at the published release commit `9817daf…`" |
| `final_claims_allowed.md`, provisional-flags paragraph | "All claims remain drafts until the archived candidate is approved and published" is removed. All 24 claims are final and non-provisional for the published release. "Published report" is clarified as the original report of 1 November |
| `final_claims_allowed.md` §4 | Rewritten as "the final release and their history". The published outputs at `9817daf…` are final, and no correction or publication is pending. The pipeline-registered `output/manifests/claim_evidence_matrix.csv` is carried unchanged in the release (sha256 `62d5ec1e…`) and is not a source of claim statuses. The original-baseline reasoning (immutable `0662945`, regeneration still to come) is kept, explicitly as superseded history |

**Validation.**
- The matrix differs from `b1fcc77` only in `allowed_wording_ref`.
- All 24 references resolve to their claim's section of the final report.
- The release commit is cited correctly in all seven final documents.
- Number checks pass 128 / 128 (output unchanged), and the release, recovery and final-report tests pass 98 / 98.
