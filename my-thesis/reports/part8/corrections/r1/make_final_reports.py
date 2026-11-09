"""Build reports/part8/final/ from the accepted drafts (drafts_integrated_20261108/).

    python make_final_reports.py            (writes ../../final/; refuses if it exists)

Only the banner, the path wording and the passages that depend on publication change. Every
publication-dependent passage is wrapped in an HTML comment marker
`<!--PUB:key-->pending text<!--/PUB:key-->` (invisible when rendered). `final/finalize_reports.py`
replaces the marked passages after, and only after, the release has been published and
verified at both destinations. All scientific content, limitations and numbers are the
accepted drafts' (commit 258a907, with the F8/F6 updates of 9c873a1).
"""
from __future__ import annotations

import csv
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PART8 = HERE.parents[1]
DRAFTS = PART8 / "drafts_integrated_20261108"
FINAL = PART8 / "final"
REPORTS = ("main_findings.md", "robustness_findings.md", "full_empirical_analysis_report.md",
           "jury_resolution_status.md", "final_claims_allowed.md")
RELEASE_ID = "part8-final-20261109"
BRANCH = "part8-corrected-results/final-20261109"


def pub(key: str, text: str) -> str:
    return f"<!--PUB:{key}-->{text}<!--/PUB:{key}-->"


BANNER = f"""> **FINAL PART 8 REPORT — release `{RELEASE_ID}`.** {pub("status", "**Not yet published.** The release commit and Drive folder do not exist yet. Until `finalize_reports.py` records the verified publication, these reports and their numbers are not citable (CLAUDE.md §9).")}
>
> - **Authoritative numbers.** `my-thesis/output/` in the release commit on branch `{BRANCH}`: 465 files, listed with sha256 in `my-thesis/release/part8_final/release_inventory.csv`. See `SOURCE_OF_TRUTH.md` in this directory.
>   - `output/` in any other commit or branch holds superseded or provisional values. That includes `part8-r1-rescore`, the pin `8aaa4217` and the results commit `0662945`, which hold the original baseline. **Do not use it.**
> - **Numbers identity.** Run `correction-20261109T080220-949fcd76` (archive `archive-20261109T080914Z-3c7d68`), equivalent to the audited run `correction-20261108T053328-949fcd76`. Scientific code `8aaa4217`, unchanged. No model was estimated in the integration or the release. B2 was accepted on 8 November 2026 (`corrections/r1/b2_scientific_adjudication.md`).
> - **Number checks.** Every quoted number is checked against the integrated tables, whose cell content the archive's equivalence gate ties to the release: `corrections/r1/evidence/part8_drafts_20261108/number_checks.csv`.
> - **F3.4 figures.** {pub("f8", "The approved F8 versions (presentation only, 9 November 2026) are prepared in `corrections/r1/f8_review/` and become the release's `figures/F3.4_*` on publication.")}
> - **Not changed.** The superseded reports in `reports/part8/*.md` and the drafts in `drafts_integrated_20261108/`; results commit `0662945`; the provisional releases `0573a8c`, `3bd24c4` and `292227e`; certificates; `approved-specs/`.
> - **Changes from the published (1 November) reports and from the drafts:** `CHANGELOG.md`."""

COMMON = [
    ("(integrated candidate, draft)", "(final)"),
    ("All paths below are the `output/`-relative paths of the candidate tree.",
     "All paths below are relative to `my-thesis/output/` in the release commit (see the banner)."),
    ("All paths are `output/`-relative paths of the candidate tree.",
     "All paths are relative to `my-thesis/output/` in the release commit (see the banner)."),
    ("All are `output/`-relative paths of the candidate tree.",
     "All are relative to `my-thesis/output/` in the release commit (see the banner)."),
]

SPECIFIC = {
    "full_empirical_analysis_report.md": [
        ("**Integrated candidate (the subject of this draft)**",
         "**Integrated candidate (the source of the release)**"),
        ("**Date of this draft:** 8 November 2026.", "**Date of this final report:** 9 November 2026."),
        ("- **Numbers.** Every number is quoted from a table of the integrated candidate, identified by its `output/`-relative path (see the banner).",
         "- **Numbers.** Every number is quoted from a table of the release, identified by its path relative to `my-thesis/output/` in the release commit (see the banner)."),
        ("- **F7.2 / F8 — prepared.** Flagged forecasts are drawn as markers (F1). F8, the readable F3.4 main panel, was approved on 9 November 2026 as presentation only. Its figures are prepared for the release (`corrections/r1/f8_review/`), and the archived candidate holds the pre-F8 F3.4.",
         "- **F7.2 / F8.** Flagged forecasts are drawn as markers (F1). F8, the readable F3.4 main panel, was approved on 9 November 2026 as presentation only. "
         + pub("f8_full", "Its figures are prepared for the release (`corrections/r1/f8_review/`); until publication the only stored F3.4 are the pre-F8 archived figures.")),
        ("- **Resolved, conditional on publishing the F8 figures:** R1-06.\n- **Partially addressed:** R1-11 (empirical part only) and P-04 (UNRATE K=3 inconclusive, F6).",
         pub("r106_full", "- **Partially addressed until the release is published with the F8 figures:** R1-06.\n- **Partially addressed:** R1-11 (empirical part only) and P-04 (UNRATE K=3 inconclusive, F6).")),
        ("F8 (readable F3.4 main panel) is approved and its figures are prepared, but the archived candidate still holds the pre-F8 F3.4, in which an exploding STAR forecast compresses the CPI main panel. The release plan replaces them. The candidate is archived (`archive-20261109T080914Z-3c7d68`) but not yet approved or published.",
         "F8 (readable F3.4 main panel) is approved. "
         + pub("f8_limit", "Its figures replace the pre-F8 F3.4 only on publication of the release; the archived candidate (`archive-20261109T080914Z-3c7d68`) keeps the pre-F8 figures, in which an exploding STAR forecast compresses the CPI main panel.")
         + " The residual M2SL diagnostic-panel overlap is an accepted presentation limitation."),
    ],
    "jury_resolution_status.md": [
        ("- **Status:** RESOLVED, conditional on the F8 figures being the ones published (was PARTIALLY ADDRESSED). The archived candidate still holds the pre-F8 F3.4.",
         pub("r106_status", "- **Status:** PARTIALLY ADDRESSED until the release is published. It becomes RESOLVED only when the published release contains the approved F8 figures; until then the only stored F3.4 are the pre-F8 archived figures.")),
        ("- **Remaining action:** publish the F8 figures with the release (`corrections/r1/part8_d3_release_plan.md`).",
         pub("r106_action", "- **Remaining action:** publish the release with the F8 figures (`corrections/r1/part8_d3_release_plan.md`).")),
        ("| RESOLVED | 16 | R1-06 (conditional on publishing the F8 figures), R1-07, R1-09, R1-12, R1-13, R1-14, R1-15, R1-17, R1-18, R1-19, R1-22, R1-23, P-01, P-02, P-03, P-05 |\n| PARTIALLY ADDRESSED | 2 | R1-11 (empirical part only), P-04 (F6) |",
         pub("r106_table", "| RESOLVED | 15 | R1-07, R1-09, R1-12, R1-13, R1-14, R1-15, R1-17, R1-18, R1-19, R1-22, R1-23, P-01, P-02, P-03, P-05 |\n| PARTIALLY ADDRESSED | 3 | R1-06 (until the release with the F8 figures is published), R1-11 (empirical part only), P-04 (F6) |")),
        ("**R1-06** moves to RESOLVED only with F8, approved on 9 November 2026, and only once the F8 figures are published. P-04 stays partial (F6, final disposition). R1-11 stays partial (its textual part is Part 9). All RESOLVED statuses are final only after the archived candidate is approved and published.",
         pub("r106_text", "**R1-06** moves to RESOLVED only when the release containing the approved F8 figures is published and verified.")
         + " P-04 stays partial (F6, final disposition). R1-11 stays partial (its textual part is Part 9). "
         + pub("final_text", "All RESOLVED statuses take effect when the release is published.")),
    ],
    "final_claims_allowed.md": [
        ("It gives the exact claims the **integrated candidate** permits (see the banner), with the wording allowed, the status, the supporting files (`output/`-relative paths of the candidate tree) and the jury IDs.",
         "It gives the exact claims the **final release** permits (see the banner), with the wording allowed, the status, the supporting files (relative to `my-thesis/output/` in the release commit) and the jury IDs."),
        ("Neither matrix is changed by this draft (§4).",
         "The final machine-readable matrix is `claim_evidence_matrix_final.csv` in this directory; the earlier matrices are unchanged (§4)."),
        ("- **Integrated candidate.** This draft does not edit either matrix. If the drafts are approved, the claim matrix should be refreshed from the approved candidate and these wordings (C07, C08, C14, C15, C21 and the restriction on C12), as a separate, reviewed step.",
         "- **Final matrix.** `claim_evidence_matrix_final.csv` in this directory carries the final statuses, evidence and required limitations of all 24 claims. The pipeline-registered `output/manifests/claim_evidence_matrix.csv` (one empty P04 row) is not a source of claim statuses."),
    ],
}


def build_report(name: str) -> str:
    text = (DRAFTS / name).read_text(encoding="utf-8")
    lines = text.split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith("> **DRAFT FOR INDEPENDENT REVIEW"))
    end = start
    while end < len(lines) and lines[end].startswith(">"):
        end += 1
    text = "\n".join(lines[:start] + [BANNER] + lines[end:])
    for old, new in COMMON:
        text = text.replace(old, new)
    for old, new in SPECIFIC.get(name, []):
        if text.count(old) != 1:
            raise SystemExit(f"{name}: expected exactly one {old[:80]!r}")
        text = text.replace(old, new)
    if "DRAFT" in text or "this draft" in text:
        raise SystemExit(f"{name}: draft wording left")
    return text


def build_matrix() -> None:
    with open(DRAFTS / "claim_evidence_matrix_candidate.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        row["candidate_source"] = (f"release {RELEASE_ID}: my-thesis/output/ in the release commit on {BRANCH} "
                                   "(numbers run correction-20261109T080220-949fcd76, archive "
                                   "archive-20261109T080914Z-3c7d68)")
        due = f"publication of release {RELEASE_ID}"
        if row["claim_id"] in ("P04-regime-count", "C18"):
            due += "; F6 (final disposition: UNRATE K=3 inconclusive)"
        row["provisional"], row["provisional_due_to"] = "True", due
    with open(FINAL / "claim_evidence_matrix_final.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    if FINAL.exists() and any(p.suffix == ".md" and p.name in REPORTS for p in FINAL.iterdir()):
        print(f"{FINAL} already holds final reports; refusing to overwrite")
        return 1
    FINAL.mkdir(exist_ok=True)
    for name in REPORTS:
        (FINAL / name).write_text(build_report(name), encoding="utf-8")
    build_matrix()
    shutil.copyfile(DRAFTS / "CHANGELOG.md", FINAL / "CHANGELOG_drafts.md")
    print("wrote", FINAL)
    return 0


if __name__ == "__main__":
    sys.exit(main())
