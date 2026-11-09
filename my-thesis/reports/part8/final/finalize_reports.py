"""Record the verified publication in the final Part 8 reports (run ONLY after publication).

    python finalize_reports.py PUBLICATION_STATUS_JSON [--no-remote-check]

PUBLICATION_STATUS_JSON is `publication_status.json` from the final Drive folder
`baseline/r1_part8_final_release/part8-final-20261109/`. The script refuses unless:
  * the status is `published`, with the GitHub branch and the Drive copy both verified;
  * the release branch and commit are the expected ones; and
  * (unless --no-remote-check, which is used only in tests) `git ls-remote` shows the
    branch at that commit and the commit's release manifest names this release.

It then replaces every `<!--PUB:key-->…<!--/PUB:key-->` passage of the five reports with
its published text, marks the final claim matrix non-provisional (F6 kept where it
applies), and writes PUBLICATION.md. It never runs twice: it refuses if no marker is left.
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

FINAL = Path(__file__).resolve().parent
REPORTS = ("main_findings.md", "robustness_findings.md", "full_empirical_analysis_report.md",
           "jury_resolution_status.md", "final_claims_allowed.md")
RELEASE_ID = "part8-final-20261109"
BRANCH = "part8-corrected-results/final-20261109"
DRIVE_FOLDER = f"baseline/r1_part8_final_release/{RELEASE_ID}"
MARKER = re.compile(r"<!--PUB:([a-z0-9_]+)-->(.*?)<!--/PUB:\1-->", re.S)


class NotPublished(RuntimeError):
    pass


def check_status(status: dict) -> dict:
    states = [s.get("state") for s in status.get("steps", [])]
    tar = next((s.get("tar_sha256") for s in status.get("steps", []) if s.get("state") == "published"), None)
    problems = []
    if status.get("state") != "published" or states[-1:] != ["published"]:
        problems.append(f"state is {status.get('state')!r}")
    for required in ("drive_staged", "github_verified", "published"):
        if required not in states:
            problems.append(f"step {required} missing")
    if status.get("release_id") != RELEASE_ID or status.get("branch") != BRANCH:
        problems.append("not this release")
    if not re.fullmatch(r"[0-9a-f]{40}", str(status.get("commit", ""))):
        problems.append("commit is not a full SHA")
    if not tar or not re.fullmatch(r"[0-9a-f]{64}", tar):
        problems.append("no verified Drive tar sha256")
    if not str(status.get("drive_final", "")).endswith(DRIVE_FOLDER):
        problems.append("Drive folder is not the release folder")
    if problems:
        raise NotPublished("; ".join(problems))
    return {"commit": status["commit"], "tar": tar,
            "date": str(status.get("published_utc", ""))[:8]}


def check_remote(commit: str, repo: Path) -> None:
    head = subprocess.run(["git", "ls-remote", "--heads", "origin", f"refs/heads/{BRANCH}"],
                          cwd=repo, capture_output=True, text=True, check=True).stdout.split()
    if not head or head[0] != commit:
        raise NotPublished(f"remote {BRANCH} is at {head[:1]}, not {commit}")
    subprocess.run(["git", "fetch", "-q", "origin", BRANCH], cwd=repo, check=True)
    manifest = json.loads(subprocess.run(
        ["git", "show", f"{commit}:my-thesis/release/part8_final/release_manifest.json"],
        cwd=repo, capture_output=True, text=True, check=True).stdout)
    if manifest.get("release_id") != RELEASE_ID:
        raise NotPublished("the release commit does not carry this release's manifest")


def published_texts(v: dict) -> dict[str, str]:
    date = f"{v['date'][:4]}-{v['date'][4:6]}-{v['date'][6:8]}" if len(v["date"]) == 8 else v["date"]
    c = v["commit"]
    return {
        "status": (f"**Published on {date}:** commit `{c}` on `{BRANCH}`; Drive `{DRIVE_FOLDER}/` "
                   f"(release.tar.gz sha256 `{v['tar']}`), verified at both destinations (`PUBLICATION.md`)."),
        "f8": ("The release's `figures/F3.4_*` are the approved F8 versions (presentation only, approved "
               "9 November 2026; sha256 in `release_inventory.csv`)."),
        "f8_full": f"Its figures are the release's `figures/F3.4_*` (commit `{c}`).",
        "r106_full": ("- **Resolved:** R1-06 (the published release contains the approved F8 figures).\n"
                      "- **Partially addressed:** R1-11 (empirical part only) and P-04 (UNRATE K=3 inconclusive, F6)."),
        "f8_limit": (f"Its figures are the release's F3.4 (commit `{c}`); the archived candidate keeps the "
                     "pre-F8 figures for the record."),
        "r106_status": (f"- **Status:** RESOLVED (was PARTIALLY ADDRESSED). The published release (commit `{c}`) "
                        "contains the approved F8 figures."),
        "r106_action": "- **Remaining action:** none.",
        "r106_table": ("| RESOLVED | 16 | R1-06, R1-07, R1-09, R1-12, R1-13, R1-14, R1-15, R1-17, R1-18, R1-19, "
                       "R1-22, R1-23, P-01, P-02, P-03, P-05 |\n"
                       "| PARTIALLY ADDRESSED | 2 | R1-11 (empirical part only), P-04 (F6) |"),
        "r106_text": "**R1-06** is RESOLVED: the published release contains the approved F8 figures.",
        "final_text": f"All RESOLVED statuses take effect with the published release (commit `{c}`).",
    }


def finalize_text(text: str, texts: dict[str, str]) -> str:
    unknown = {m.group(1) for m in MARKER.finditer(text)} - set(texts)
    if unknown:
        raise NotPublished(f"no published text for markers {sorted(unknown)}")
    return MARKER.sub(lambda m: texts[m.group(1)], text)


def finalize(status_path: Path, final: Path = FINAL, *, remote_check: bool = True,
             repo: Path | None = None) -> dict:
    values = check_status(json.loads(Path(status_path).read_text()))
    if remote_check:
        check_remote(values["commit"], repo or final.parents[3])
    texts = published_texts(values)
    reports = {name: (final / name).read_text(encoding="utf-8") for name in REPORTS}
    if not any(MARKER.search(t) for t in reports.values()):
        raise NotPublished("no publication marker left: the reports are already finalized")
    for name, text in reports.items():
        out = finalize_text(text, texts)
        if "<!--PUB:" in out or "Not yet published" in out:
            raise NotPublished(f"{name}: pending text left after finalization")
        (final / name).write_text(out, encoding="utf-8")
    matrix = final / "claim_evidence_matrix_final.csv"
    with open(matrix, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        f6 = row["claim_id"] in ("P04-regime-count", "C18")
        row["provisional"] = "False"
        row["provisional_due_to"] = "F6 (final disposition: UNRATE K=3 inconclusive)" if f6 else ""
    with open(matrix, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (final / "PUBLICATION.md").write_text(
        f"# Publication of `{RELEASE_ID}`\n\n- Branch: `{BRANCH}`\n- Commit: `{values['commit']}`\n"
        f"- Drive: `{DRIVE_FOLDER}/`, release.tar.gz sha256 `{values['tar']}`\n"
        f"- Published (UTC date): {values['date']}\n- Status file: `publication_status.json` "
        "(copied from the Drive folder)\n", encoding="utf-8")
    (final / "publication_status.json").write_text(Path(status_path).read_text(), encoding="utf-8")
    return values


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        sys.exit(2)
    print(finalize(Path(sys.argv[1]), remote_check="--no-remote-check" not in sys.argv))
