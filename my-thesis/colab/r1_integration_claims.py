"""Stage 5 of the Part 8 integration dry run: claims and jury-resolution reassessment.

For every claim in `claim_evidence_matrix_corrected.csv` (written against the R1 release
0573a8c, run correction-20261101T152213-949fcd76):

  * its supporting output files are compared, cell by cell, between that reference release
    and the dry-run release (provenance, run-time and record columns ignored; the pinned
    floating-point tolerance applies);
  * every number quoted in the claim's corrected evidence is looked up, at its printed
    precision, in the supporting files of both releases (a located number that disappears
    is flagged; this lookup is a heuristic aid, labelled as such);
  * the claim gets a mechanical transition. A status is never upgraded or confirmed
    automatically: any change of evidence makes the claim REVIEW_REQUIRED.

Every jury ID (Part 2 registry) is then mapped to its claims and their transitions.
Numbers quoted in the Part 8 reports that may be affected are listed for review.
Nothing is edited: no report, no claim matrix.
"""

from __future__ import annotations

import fnmatch
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r1_integration_common as ic  # noqa: E402

NUMBER = re.compile(r"(?<![\w.])-?\d+\.\d+(?![\w.])")
JURY_ID = re.compile(r"\b(?:R\d-\d{2}|[PV]-\d{2})\b")


def supporting_files(spec: str, tree_files: dict) -> list[str]:
    out = []
    for pattern in (s.strip() for s in spec.split(";")):
        if not pattern:
            continue
        matches = sorted(f for f in tree_files if fnmatch.fnmatch(f, pattern))
        out += matches or [pattern]
    return list(dict.fromkeys(out))


def numbers_in(text: str) -> list[str]:
    return list(dict.fromkeys(NUMBER.findall(text or "")))


def locate(number: str, tables: list) -> bool:
    """A quoted number is located if some numeric cell rounds to it at its printed decimals."""
    decimals = len(number.split(".")[1])
    target = float(number)
    for frame in tables:
        for column in frame.columns:
            values = frame[column]
            for value in values:
                try:
                    x = float(value)
                except (TypeError, ValueError):
                    continue
                if x == x and (round(x, decimals) == target or round(abs(x), decimals) == abs(target)):
                    return True
    return False


def load_tables(root: Path, files: list[str]) -> list:
    out = []
    for relative in files:
        path = root / relative
        if path.suffix == ".csv" and path.exists():
            out.append(ic.read_table(path))
    return out


def claim_rows(matrix_csv: Path, reference: Path, release: Path) -> list[dict]:
    ref_files, rel_files = ic.tree_files(reference), ic.tree_files(release)
    rows = []
    for claim in ic.read_rows(matrix_csv):
        spec = claim.get("supporting_output_files", "")
        if not any("/" in part for part in spec.split(";")):
            rows.append({"claim_id": claim["claim_id"], "target": claim.get("target", ""),
                         "status_before": claim.get("corrected_status", ""),
                         "status_after": f"REVIEW_REQUIRED (was {claim.get('corrected_status', '')})",
                         "transition": "REVIEW_REQUIRED: supporting files not machine-checkable "
                                       f"({spec!r}); assess manually",
                         "jury_ids": claim.get("jury_ids_addressed", ""), "supporting_files": spec})
            continue
        files = supporting_files(spec, rel_files)
        changed_cells = decision_cells = 0
        missing, changed_files = [], []
        for relative in files:
            if relative not in rel_files or relative not in ref_files:
                missing.append(relative)
                continue
            if ic.sha256_file(rel_files[relative]) == ic.sha256_file(ref_files[relative]):
                continue
            if relative.endswith(".csv"):
                result = ic.table_cell_changes(ref_files[relative], rel_files[relative], relative)
                if not result["alignable"]:
                    changed_files.append(relative + " (rows not alignable)")
                    decision_cells += 1
                    continue
                if result["cells"] or result.get("rows_added") or result.get("rows_removed"):
                    changed_files.append(relative)
                changed_cells += len(result["cells"])
                decision_cells += sum(c["decision_like"] for c in result["cells"])
            elif not relative.endswith(".provenance.json"):
                changed_files.append(relative)
        quoted = numbers_in(claim.get("corrected_evidence", ""))
        ref_tables, rel_tables = load_tables(reference, files), load_tables(release, files)
        lost = [n for n in quoted if locate(n, ref_tables) and not locate(n, rel_tables)]
        if decision_cells:
            transition = "REVIEW_REQUIRED: decision-like evidence changed"
        elif lost:
            transition = "REVIEW_REQUIRED: quoted numbers no longer located"
        elif changed_cells or changed_files:
            transition = "REVIEW_REQUIRED: evidence values changed (no decision-like change)"
        elif missing:
            transition = "REVIEW_REQUIRED: supporting file missing"
        else:
            transition = "EVIDENCE_UNCHANGED"
        status_before = claim.get("corrected_status", "")
        rows.append({"claim_id": claim["claim_id"], "target": claim.get("target", ""),
                     "status_before": status_before,
                     "status_after": (status_before if transition == "EVIDENCE_UNCHANGED"
                                      else f"REVIEW_REQUIRED (was {status_before})"),
                     "transition": transition, "jury_ids": claim.get("jury_ids_addressed", ""),
                     "supporting_files": "; ".join(files), "files_changed": "; ".join(changed_files),
                     "cells_changed": changed_cells, "decision_cells_changed": decision_cells,
                     "quoted_numbers": "; ".join(quoted),
                     "quoted_numbers_no_longer_located (heuristic)": "; ".join(lost),
                     "supporting_files_missing": "; ".join(missing)})
    return rows


def jury_rows(claims: list[dict], registry_md: Path, status_md: Path | None) -> list[dict]:
    registry = set(JURY_ID.findall(registry_md.read_text(encoding="utf-8")))
    listed = set(JURY_ID.findall(status_md.read_text(encoding="utf-8"))) if status_md and \
        status_md.exists() else set()
    by_id: dict[str, list[dict]] = {}
    for claim in claims:
        for jury in JURY_ID.findall(claim["jury_ids"]):
            by_id.setdefault(jury, []).append(claim)
    rows = []
    for jury in sorted(registry | listed | set(by_id)):
        mapped = by_id.get(jury, [])
        if not mapped:
            status = "NOT_MAPPED_TO_A_CLAIM: assess manually from jury_resolution_status.md"
        elif all(c["transition"] == "EVIDENCE_UNCHANGED" for c in mapped):
            status = "EVIDENCE_UNCHANGED"
        else:
            status = "REVIEW_REQUIRED"
        rows.append({"jury_id": jury, "in_part2_registry": jury in registry,
                     "in_jury_resolution_status": jury in listed,
                     "claims": "; ".join(c["claim_id"] for c in mapped),
                     "claim_transitions": "; ".join(f"{c['claim_id']}: {c['transition']}" for c in mapped),
                     "status": status})
    return rows


def report_numbers(reports: Path, cell_rows: list[dict]) -> list[dict]:
    """Report lines quoting an old value of a changed cell (heuristic; for human review)."""
    olds: dict[str, list[dict]] = {}
    for cell in cell_rows:
        try:
            value = float(cell["old"])
        except (TypeError, ValueError):
            continue
        if value != value or value == int(value):
            continue
        for decimals in (2, 3, 4):
            olds.setdefault(f"{value:.{decimals}f}", []).append(cell)
    out = []
    for md in sorted(reports.glob("*.md")):
        for line, text in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            for number in NUMBER.findall(text):
                for cell in olds.get(number, []):
                    series = cell.get("key_series", "")
                    if series and series not in text:
                        continue
                    out.append({"report": md.name, "line": line, "number": number,
                                "path": cell["path"], "column": cell["column"],
                                "key_series": series, "key_model": cell.get("key_model", ""),
                                "old": cell["old"], "new": cell["new"]})
                    break
    return out


def run(p: dict) -> dict:
    work = p["work"]
    report_dir = work / "dryrun_report"
    reference, release = work / "references" / "claims_reference", work / "release"
    claims = claim_rows(p["claim_matrix"], reference, release)
    ic.write_rows(report_dir / "claims_recheck.csv", claims)
    jury = jury_rows(claims, p["jury_registry"], p["reports"] / "jury_resolution_status.md")
    ic.write_rows(report_dir / "jury_recheck.csv", jury)
    files, cells = ic.tree_changes(reference, release)
    ic.write_rows(report_dir / "files_vs_claims_reference.csv", files)
    ic.write_rows(report_dir / "cells_vs_claims_reference.csv.gz", cells)
    numbers = report_numbers(p["reports"], cells)
    ic.write_rows(report_dir / "report_numbers_changed.csv", numbers)
    transitions: dict[str, int] = {}
    for claim in claims:
        transitions[claim["transition"]] = transitions.get(claim["transition"], 0) + 1
    problems = []
    matrix_ids = [r["claim_id"] for r in ic.read_rows(p["claim_matrix"])]
    if sorted(matrix_ids) != sorted(c["claim_id"] for c in claims):
        problems.append("not every claim was reassessed")
    if any(c["transition"] != "EVIDENCE_UNCHANGED" and not c["status_after"].startswith("REVIEW_REQUIRED")
           for c in claims):
        problems.append("a claim with changed evidence was not marked REVIEW_REQUIRED")
    if any(not j["status"] for j in jury):
        problems.append("a jury ID has no status")
    return {"claims": len(claims), "transitions": transitions, "jury_ids": len(jury),
            "jury_status": {s: sum(j["status"] == s for j in jury) for s in {j["status"] for j in jury}},
            "report_lines_flagged": len(numbers), "problems": problems}
