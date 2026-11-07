"""Part 8 integration dry run: driver, base tree, write boundary, reconciliation, outcome."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[3]
COLAB = ROOT / "colab"
sys.path.insert(0, str(COLAB))
import r1_integration_common as ic  # noqa: E402
import r1_part8_integration as drv  # noqa: E402

MODULES = ("r1_part8_integration.py", "r1_integration_common.py", "r1_integration_dependents.py",
           "r1_integration_validate.py", "r1_integration_claims.py")


# -- common helpers --------------------------------------------------------------------

def test_inside_refuses_paths_outside_the_work_folder(tmp_path):
    work = tmp_path / "work"
    assert ic.inside(work, work / "a" / "b") == (work / "a" / "b").resolve()
    for bad in (tmp_path / "x", work / ".." / "x", Path("/etc/passwd")):
        with pytest.raises(ic.IntegrationError, match="outside the work folder"):
            ic.inside(work, bad)


def test_same_cell_uses_the_pinned_tolerance():
    assert ic.same_cell("1.0", "1") and ic.same_cell("0.1", "0.1000000000001")
    assert not ic.same_cell("0.1", "0.1001") and not ic.same_cell("reject", "do not reject")
    assert ic.same_cell("nan", "nan") and not ic.same_cell("nan", "1")


def test_payload_digest_matches_the_audit_definition(tmp_path):
    fits = tmp_path / "fits"
    for name, text in (("ab/1.json", "{}"), ("00/2.json", '{"a": 1}')):
        (fits / name).parent.mkdir(parents=True, exist_ok=True)
        (fits / name).write_text(text)
    digest = hashlib.sha256()
    for name in sorted(["ab/1.json", "00/2.json"]):
        digest.update(f"{name} {hashlib.sha256((fits / name).read_bytes()).hexdigest()}\n".encode())
    assert ic.payload_digest(fits) == (2, digest.hexdigest())


def test_table_cell_changes_flags_decisions_and_ignores_provenance(tmp_path):
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    pd.DataFrame({"series": ["X", "Y"], "rmse": ["1.0", "2.0"], "decision_5pct": ["reject", "reject"],
                  "run_id": ["r0", "r0"]}).to_csv(a, index=False)
    pd.DataFrame({"series": ["X", "Y"], "rmse": ["1.0000000000001", "2.5"],
                  "decision_5pct": ["reject", "do not reject"], "run_id": ["r1", "r1"]}).to_csv(b, index=False)
    out = ic.table_cell_changes(a, b, "t.csv")
    got = {(c["row"], c["column"], c["decision_like"]) for c in out["cells"]}
    assert got == {(1, "rmse", False), (1, "decision_5pct", True)}


def test_tree_listing_detects_any_change(tmp_path):
    (tmp_path / "d").mkdir()
    (tmp_path / "d" / "f").write_text("1")
    before = ic.protected_listing({"d": tmp_path / "d"})
    (tmp_path / "d" / "f").write_text("2")
    assert ic.protected_listing({"d": tmp_path / "d"}) != before


# -- stage 1: base tree --------------------------------------------------------------------

def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _base_fixture(tmp_path: Path, *, damage: str | None = None) -> dict:
    published = tmp_path / "pinned" / "my-thesis" / "output"
    (published / "t").mkdir(parents=True)
    (published / "t" / "a.csv").write_text("x\n1\n")
    (published / "t" / "b.csv").write_text("x\n2\n")
    (published / "t" / "big.csv").write_text("x\n3\n")
    staged = tmp_path / "staged"
    (staged / "t").mkdir(parents=True)
    new_a, new_big = b"x\n10\n", b"x\n30\n"
    (staged / "t" / "a.csv").write_bytes(new_a)
    with open(staged / "t" / "big.csv.gz", "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as gz:
        gz.write(new_big)
    rows = [{"path": "t/a.csv", "stored_as": "t/a.csv", "bytes": len(new_a), "staged_sha256": _sha(new_a),
             "published_sha256": _sha(b"x\n1\n")},
            {"path": "t/big.csv", "stored_as": "t/big.csv.gz", "bytes": len(new_big),
             "staged_sha256": _sha(new_big), "published_sha256": _sha(b"x\n3\n")}]
    if damage == "staged_sha":
        rows[0]["staged_sha256"] = "0" * 64
    if damage == "published_sha":
        rows[1]["published_sha256"] = "0" * 64
    if damage == "extra_file":
        (staged / "t" / "extra.csv").write_text("x\n")
    if damage == "missing_file":
        (staged / "t" / "a.csv").unlink()
    with open(staged / "STAGED_FILES.csv", "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for name in ("README.md", "COUNTER_PROVENANCE_forecast_origin_audit.csv"):
        (staged / name).write_text("history,value\nx,1\n")
    work = tmp_path / "work"
    work.mkdir()
    return {"published": published, "staged": staged, "work": work}


def test_base_tree_is_published_plus_the_verified_overlay(tmp_path):
    p = _base_fixture(tmp_path)
    record = drv.stage_base(None, p)
    assert record["files"] == 3 and record["b1_staged"] == 2 and record["published"] == 1
    base = p["work"] / "base"
    assert (base / "t" / "a.csv").read_bytes() == b"x\n10\n"
    assert (base / "t" / "big.csv").read_bytes() == b"x\n30\n"         # decompressed
    assert (base / "t" / "b.csv").read_bytes() == b"x\n2\n"
    assert not (base / "STAGED_FILES.csv").exists()
    assert (p["published"] / "t" / "a.csv").read_bytes() == b"x\n1\n"   # input untouched


@pytest.mark.parametrize("damage, message", [
    ("staged_sha", "fails its sha256"), ("published_sha", "supersedes"),
    ("extra_file", "overlay files differ"), ("missing_file", "overlay files differ")])
def test_base_tree_refuses_a_damaged_overlay(tmp_path, damage, message):
    p = _base_fixture(tmp_path, damage=damage)
    with pytest.raises(ic.IntegrationError, match=message):
        drv.stage_base(None, p)


# -- stage 0: certificates and publication refusal ---------------------------------------

def _certificates(tmp_path: Path) -> tuple[Path, Path]:
    import r1_tierb as tb
    drive = tmp_path / "drive"
    rows = []
    for batch in tb.BATCHES:
        folder = tb.batch_root(drive, batch) / "certificates"
        folder.mkdir(parents=True)
        name = f"COMPLETE-20261105T000000Z-{batch}-s.json"
        (folder / name).write_text(json.dumps({"batch": batch}))
        rows.append({"batch": batch, "drive_file_id": "x", "file": name,
                     "sha256": _sha((folder / name).read_bytes()), "bytes": 1})
    manifest = tmp_path / "MANIFEST.csv"
    with open(manifest, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return drive, manifest


def test_certificates_must_be_the_reviewed_files(tmp_path):
    import r1_tierb as tb
    drive, manifest = _certificates(tmp_path)
    assert set(drv.check_certificates(drive, manifest)) == set(tb.BATCHES)
    later = tb.batch_root(drive, "B2") / "certificates" / "COMPLETE-20261107T000000Z-B2-t.json"
    later.write_text(json.dumps({"batch": "B2", "later": True}))
    with pytest.raises(ic.IntegrationError, match="B2: latest certificate"):
        drv.check_certificates(drive, manifest)


def test_preflight_refuses_when_publication_is_requested(tmp_path, monkeypatch):
    monkeypatch.setenv("CONFIRM_PUBLISH", "True")
    with pytest.raises(ic.IntegrationError, match="non-publishing"):
        drv.stage_preflight(None, {"work": tmp_path})


def test_the_dry_run_starts_only_in_an_empty_folder_apart_from_the_inputs(tmp_path):
    work = tmp_path / "work"
    work.mkdir()
    (work / "old").write_text("x")
    base = ["--repo", str(tmp_path / "repo"), "--code-dir", str(tmp_path / "pinned" / "code"),
            "--drive-root", "/content/drive/x", "--cache-root", str(tmp_path / "c"),
            "--tier-a-archive", str(tmp_path / "a.tar.gz"), "--orch-commit", "0" * 40]
    with pytest.raises(ic.IntegrationError, match="not empty"):
        drv.main(base + ["--work", str(work)])
    with pytest.raises(ic.IntegrationError, match="apart from"):
        drv.main(base + ["--work", str(tmp_path / "repo" / "work")])


def test_no_module_can_publish():
    """No push, commit, token read or Drive publication anywhere in the dry-run code."""
    for name in MODULES + ("make_r1_part8_integration_notebook.py",):
        source = (COLAB / name).read_text()
        assert not re.search(r"[\"']push[\"']|git push|[\"']commit[\"'],", source), name
        assert "GITHUB_TOKEN" not in source or name.startswith("make_"), name
    driver = (COLAB / "r1_part8_integration.py").read_text()
    assert "--publish" not in driver and "CONFIRM_PUBLISH" in driver


# -- stage 2: chain-aware reconciliation --------------------------------------------------

def _trees(tmp_path: Path, o, l, c) -> tuple[Path, Path, Path]:
    out = []
    for name, rows in (("o", o), ("l", l), ("c", c)):
        root = tmp_path / name / "robustness"
        root.mkdir(parents=True)
        pd.DataFrame(rows).to_csv(root / "T4.1_x.csv", index=False)
        out.append(tmp_path / name)
    return tuple(out)


def test_reconciliation_keeps_values_of_re_estimated_chains(tmp_path):
    """The pinned reconcile would restore the superseded base value where the legacy and
    corrected runs agree; with a non-reproducing re-estimated chain that is wrong."""
    pytest.importorskip("thesis")
    from thesis.correction import workflow as wf
    o = {"series": ["FEDFUNDS"] * 4, "metric": ["noise", "n_failed", "rmse", "both"],
         "value": ["0.123456789012", "52", "1.5", "7.0"], "run_id": ["base"] * 4}
    l = {**o, "value": ["0.1234567890121", "49", "1.5", "8.0"], "run_id": ["legacy"] * 4}
    c = {**o, "value": ["0.1234567890121", "49", "1.4", "9.0"], "run_id": ["corrected"] * 4}
    orig, legacy, corrected = _trees(tmp_path, o, l, c)
    files = ["robustness/T4.1_x.csv"]
    account, causes = drv.reconcile_chain_aware(orig, legacy, corrected, files)
    final = pd.read_csv(corrected / files[0], dtype=str, keep_default_na=False)["value"].tolist()
    assert final == ["0.123456789012", "49", "1.4", "9.0"]    # noise restored; 49 kept
    got = {(r["row"], r["cause"]) for r in causes}
    assert got == {(1, "reestimated_chain"), (2, "correction"), (3, "correction+reestimated_chain")}
    assert account[0]["cells_restored_to_base"] == 1
    # the pinned reconcile, for contrast, would print the superseded 52
    pinned = tmp_path / "pinned_c" / "robustness"
    pinned.mkdir(parents=True)
    pd.DataFrame(c).to_csv(pinned / "T4.1_x.csv", index=False)
    wf.reconcile(orig, legacy, tmp_path / "pinned_c", files)
    assert pd.read_csv(pinned / "T4.1_x.csv", dtype=str)["value"].tolist()[1] == "52"


# -- outcome ---------------------------------------------------------------------------

@pytest.mark.parametrize("accepted, status, code, line", [
    (True, "COMPUTATION_COMPLETE_REVIEW_REQUIRED", 4, "ACCEPTED_FOR_REVIEW_REVIEW_REQUIRED"),
    (True, "COMPUTATION_COMPLETE_REPRODUCED", 0, "ACCEPTED_FOR_REVIEW"),
    (False, "COMPUTATION_COMPLETE_REVIEW_REQUIRED", 1, "REFUSED")])
def test_exit_status(tmp_path, capsys, accepted, status, code, line):
    ic.write_json(tmp_path / "dryrun_report" / "acceptance.json",
                  {"accepted": accepted, "aggregation_status": status})
    assert drv.outcome(tmp_path) == code
    assert f"DRY_RUN_STATUS: {line}" in capsys.readouterr().out


def test_finalize_fails_a2_when_a_protected_input_changed(tmp_path, monkeypatch):
    protected = tmp_path / "protected"
    protected.mkdir()
    (protected / "f").write_text("1")
    monkeypatch.setattr(drv, "protected_paths", lambda p, extra: {"x": protected})
    work = tmp_path / "work"
    drv.finish_stage(work, "preflight", {"protected_before": ic.protected_listing({"x": protected})})
    drv.finish_stage(work, "claims", {"claims": 1, "transitions": {}, "jury_ids": 0,
                                      "jury_status": {}, "report_lines_flagged": 0, "problems": []})
    ic.write_json(work / "dryrun_report" / "acceptance_stage4.json",
                  {"run_id": "r", "aggregation_status": "S", "criteria": {"A1": {"pass": True, "detail": ""}}})

    class Args:
        protect, orch_commit = {}, "o"
    assert drv.finalize(Args, {"work": work})["accepted"] is True
    (protected / "f").write_text("2")
    result = drv.finalize(Args, {"work": work})
    assert result["accepted"] is False and result["failed_criteria"] == ["A2"]


def test_correction_flags_are_the_authorised_set_with_f8_off():
    pytest.importorskip("thesis")
    from thesis.correction.flags import CorrectionFlags
    assert set(ic.CORRECTION_FLAGS) == set(CorrectionFlags().as_dict())
    assert ic.CORRECTION_FLAGS["f8_readable_main_panel"] is False
    assert all(v for k, v in ic.CORRECTION_FLAGS.items() if k != "f8_readable_main_panel")


def test_t42_gate_accepts_only_floating_point_last_digit_differences(tmp_path):
    pytest.importorskip("thesis")
    name = "T4.2_cpi_lag_predictive_tests.csv"
    tier_a, release = tmp_path / "a" / "robustness", tmp_path / "b" / "robustness"
    tier_a.mkdir(parents=True)
    release.mkdir(parents=True)
    pd.DataFrame({"model": ["AR(p=3)"], "hlz_statistic": ["-2.685689803511075"]}).to_csv(tier_a / name, index=False)
    pd.DataFrame({"model": ["AR(p=3)"], "hlz_statistic": ["-2.6856898035110754"]}).to_csv(release / name, index=False)
    gates = {"problems": [f"{name} differs from the Tier A release", "other problem"]}
    drv.t42_tolerance(gates, tmp_path / "a", tmp_path / "b")
    assert gates["problems"] == ["other problem"]
    assert gates["t42_vs_tier_a_release"][name]["status"] == "equal_within_fp_tolerance"
    assert gates["t42_vs_tier_a_release"][name]["cells_differing_in_print"][0]["column"] == "hlz_statistic"
    pd.DataFrame({"model": ["AR(p=3)"], "hlz_statistic": ["-2.70"]}).to_csv(release / name, index=False)
    gates = {"problems": [f"{name} differs from the Tier A release"]}
    drv.t42_tolerance(gates, tmp_path / "a", tmp_path / "b")
    assert gates["problems"] == [f"{name} differs from the Tier A release"]


# -- cache integrity (stage 2 failure of integration-20261107T184004Z-93c0f8) -------------------

def _cache(root: Path, files: dict[str, str]) -> Path:
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    return root


def test_listing_diff_reports_every_added_removed_and_modified_file(tmp_path):
    root = _cache(tmp_path / "c", {"aa/1.json": "1", "bb/2.json": "2"})
    before = ic.tree_listing(root)
    (root / "aa" / "1.json").write_text("changed")
    (root / "bb" / "2.json").unlink()
    (root / "README_R1_REFIT_CACHE.txt").write_text("x")
    diff = ic.listing_diff(before, ic.tree_listing(root))
    assert [d["path"] for d in diff["added"]] == ["README_R1_REFIT_CACHE.txt"]
    assert [d["path"] for d in diff["removed"]] == ["bb/2.json"]
    assert [d["path"] for d in diff["modified"]] == ["aa/1.json"]
    assert diff["added"][0]["sha256"] == _sha(b"x")


def test_stage_cache_check_is_strict_for_every_file_and_records_the_diff(tmp_path):
    work = tmp_path / "work"
    merged = _cache(tmp_path / "merged", {"aa/1.json": "1"})
    original = _cache(tmp_path / "orig", {"cc/3.json": "3"})
    record = drv.record_cache_listings(work, merged, original)
    assert record["merged_files"] == 1 and record["original_files"] == 1
    ok = drv.check_cache_listings(work, merged, original, "during assembly")
    assert ok["merged_refit"]["unchanged"] and ok["original_cache"]["unchanged"]
    (merged / "README_R1_REFIT_CACHE.txt").write_text("not a payload, still a change")
    with pytest.raises(ic.IntegrationError, match="merged refit cache changed during assembly: 1 added"):
        drv.check_cache_listings(work, merged, original, "during assembly")
    report = json.loads((work / "dryrun_report" / "cache_integrity" /
                         "merged_refit_diff_during_assembly.json").read_text())
    assert report["added"][0]["path"] == "README_R1_REFIT_CACHE.txt" and not report["unchanged"]
    (merged / "README_R1_REFIT_CACHE.txt").unlink()
    (original / "cc" / "3.json").write_text("tampered")
    with pytest.raises(ic.IntegrationError, match="original fit cache changed"):
        drv.check_cache_listings(work, merged, original, "during validation")


def test_assembly_and_dependent_replay_use_only_the_read_only_adapter():
    driver = (COLAB / "r1_part8_integration.py").read_text()
    dependents = (COLAB / "r1_integration_dependents.py").read_text()
    assert "live_replay_in_pinned_workflow" not in driver and "readonly_refit_replay()" in driver
    assert "b1.replay" not in dependents and "readonly_refit_class()" in dependents
    assert "check_cache_listings" in dependents
    assert "check_cache_listings" in (COLAB / "r1_integration_validate.py").read_text()
