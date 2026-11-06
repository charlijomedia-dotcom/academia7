"""Stage 5 (claims and jury reassessment) and the dry-run notebook."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[3]
COLAB = ROOT / "colab"
sys.path.insert(0, str(COLAB))
import r1_integration_claims as cl  # noqa: E402


def _write(root: Path, relative: str, frame: pd.DataFrame) -> None:
    (root / relative).parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(root / relative, index=False)


def _fixture(tmp_path: Path, *, p_new="0.36", decision_new="do not reject", rmse_new="0.512"):
    ref, rel = tmp_path / "ref", tmp_path / "rel"
    t = "forecast_tests/T3.3A_hlz_pairwise.csv"
    _write(ref, t, pd.DataFrame({"series": ["UNRATE"], "p_value": ["0.3611"],
                                 "decision_5pct": ["do not reject"], "run_id": ["a"]}))
    _write(rel, t, pd.DataFrame({"series": ["UNRATE"], "p_value": [p_new + "11"],
                                 "decision_5pct": [decision_new], "run_id": ["b"]}))
    m = "forecast_tests/T3.3_main_forecast_table.csv"
    _write(ref, m, pd.DataFrame({"series": ["CPIAUCSL"], "rmse": ["0.512"]}))
    _write(rel, m, pd.DataFrame({"series": ["CPIAUCSL"], "rmse": [rmse_new]}))
    matrix = tmp_path / "matrix.csv"
    pd.DataFrame([
        {"claim_id": "C01", "target": "UNRATE", "corrected_status": "SUPPORTED",
         "corrected_evidence": "MSAR p 0.36 (no rejection)", "supporting_output_files": t,
         "jury_ids_addressed": "R1-09; R1-14"},
        {"claim_id": "C02", "target": "CPIAUCSL", "corrected_status": "QUALIFIED",
         "corrected_evidence": "RMSE 0.512", "supporting_output_files": "forecast_tests/T3.3_*.csv",
         "jury_ids_addressed": "P-05"}]).to_csv(matrix, index=False)
    return matrix, ref, rel


def test_claims_unchanged_and_changed(tmp_path):
    matrix, ref, rel = _fixture(tmp_path)
    rows = {r["claim_id"]: r for r in cl.claim_rows(matrix, ref, rel)}
    assert rows["C01"]["transition"] == "EVIDENCE_UNCHANGED"
    assert rows["C01"]["status_after"] == "SUPPORTED"
    assert rows["C02"]["supporting_files"] == "forecast_tests/T3.3_main_forecast_table.csv"
    matrix, ref, rel = _fixture(tmp_path / "2", decision_new="reject", p_new="0.01")
    rows = {r["claim_id"]: r for r in cl.claim_rows(matrix, ref, rel)}
    assert rows["C01"]["transition"].startswith("REVIEW_REQUIRED: decision-like")
    assert rows["C01"]["status_after"] == "REVIEW_REQUIRED (was SUPPORTED)"


def test_quoted_number_that_disappears_requires_review(tmp_path):
    matrix, ref, rel = _fixture(tmp_path, rmse_new="0.498")
    rows = {r["claim_id"]: r for r in cl.claim_rows(matrix, ref, rel)}
    assert rows["C02"]["transition"] == "REVIEW_REQUIRED: quoted numbers no longer located"
    assert rows["C02"]["quoted_numbers_no_longer_located (heuristic)"] == "0.512"


def test_every_jury_id_gets_a_status(tmp_path):
    matrix, ref, rel = _fixture(tmp_path, rmse_new="0.498")
    claims = cl.claim_rows(matrix, ref, rel)
    registry = tmp_path / "registry.md"
    registry.write_text("| R1-09 | ... |\n| R1-14 | ... |\n| P-05 | ... |\n| V-07 | ... |\n")
    rows = {r["jury_id"]: r for r in cl.jury_rows(claims, registry, None)}
    assert rows["R1-09"]["status"] == "EVIDENCE_UNCHANGED"
    assert rows["P-05"]["status"] == "REVIEW_REQUIRED"
    assert rows["V-07"]["status"].startswith("NOT_MAPPED_TO_A_CLAIM")


def test_report_lines_quoting_a_changed_value_are_listed(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "main_findings.md").write_text("UNRATE MSAR h=1 RMSE 0.63 is lower.\nGDPC1 0.63\n")
    cells = [{"path": "t.csv", "column": "rmse", "old": "0.6312", "new": "0.66", "key_series": "UNRATE"}]
    rows = cl.report_numbers(reports, cells)
    assert [(r["line"], r["number"]) for r in rows] == [(1, "0.63")]


# -- the notebook --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def notebook():
    import make_r1_part8_integration_notebook as nb
    return nb.build("a" * 40)


def test_notebook_cells_compile_and_carry_the_commit(notebook):
    code = ["".join(c["source"]) for c in notebook["cells"] if c["cell_type"] == "code"]
    for source in code:
        ast.parse(source)
    assert any('ORCH_COMMIT = "' + "a" * 40 + '"' in s for s in code)
    assert not any("__ORCH__" in s for s in code)


def test_notebook_never_publishes_and_writes_one_new_drive_folder(notebook):
    text = "\n".join("".join(c["source"]) for c in notebook["cells"])
    assert "git push" not in text and '"push"' not in text
    assert "CONFIRM_PUBLISH = False" in text and "assert CONFIRM_PUBLISH is False" in text
    assert "baseline/r1_part8_integration_dryrun" in text and "not EXPORT.exists()" in text
    assert "r1_part8_integration.py" in text


def test_notebook_passes_only_arguments_the_driver_accepts(notebook):
    import r1_part8_integration as drv
    text = "\n".join("".join(c["source"]) for c in notebook["cells"] if c["cell_type"] == "code")
    run = text[text.index('command = [str(PY), "-u", str(ORCH / "r1_part8_integration.py")'):]
    flags = {f for f in ("--repo", "--code-dir", "--drive-root", "--cache-root", "--tier-a-archive",
                         "--orch-commit", "--work", "--protect") if f'"{f}"' in run}
    args = drv.parse(["--repo", "r", "--code-dir", "c", "--drive-root", "d", "--cache-root", "x",
                      "--tier-a-archive", "t", "--orch-commit", "o", "--work", "w",
                      "--protect", "a=b"])
    assert flags == {"--repo", "--code-dir", "--drive-root", "--cache-root", "--tier-a-archive",
                     "--orch-commit", "--work", "--protect"} and args.protect == {"a": "b"}


def test_committed_notebook_is_the_generated_one():
    import make_r1_part8_integration_notebook as nb
    path = COLAB / nb.NOTEBOOK
    if not path.exists():
        pytest.skip("notebook not generated yet")
    data = json.loads(path.read_text())
    code = "".join("".join(c["source"]) for c in data["cells"] if c["cell_type"] == "code")
    orch = code.split('ORCH_COMMIT = "', 1)[1][:40]
    assert data == nb.build(orch)


def test_a_claim_without_file_patterns_is_left_for_manual_assessment(tmp_path):
    matrix, ref, rel = _fixture(tmp_path)
    frame = pd.read_csv(matrix)
    frame.loc[1, "supporting_output_files"] = "(all)"
    frame.to_csv(matrix, index=False)
    rows = {r["claim_id"]: r for r in cl.claim_rows(matrix, ref, rel)}
    assert "not machine-checkable" in rows["C02"]["transition"]
    assert rows["C02"]["status_after"] == "REVIEW_REQUIRED (was QUALIFIED)"
