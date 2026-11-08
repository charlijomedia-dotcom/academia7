"""Tests for the non-publishing archive of the audited Part 8 integration candidate."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
from pathlib import Path

import pytest

COLAB = Path(__file__).resolve().parents[3] / "colab"
sys.path.insert(0, str(COLAB))
import r1_integration_archive as arc  # noqa: E402

AUDITED = arc.AUDITED_SESSION
NEW = "integration-20991231T000000Z-abcdef"
NEW_RUN = "correction-20991231T000001-949fcd76"
NEW_LEGACY = "correction-20991231T000000-949fcd76"
REAL_EXPORT = (Path(__file__).resolve().parents[3] / "reports/part8/corrections/r1/evidence"
               / "integration_dryrun_audit_20261108/colab_export")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write(path: Path, data: bytes | str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data.encode() if isinstance(data, str) else data)
    return path


def make_release(root: Path, run_id: str, *, n_files: int = 6) -> Path:
    """A miniature release: original files, a figure, a table with provenance, sidecars, records."""
    rel = root / "release"
    write(rel / "models/T3.1_in_sample_adequacy.csv", "series,bic\nCPI,1.0\n")       # original
    write(rel / "figures/F4.8_UNRATE.png", b"\x89PNG-identical-bytes")                  # regenerated
    write(rel / "figures/F4.8_UNRATE.png.provenance.json",
          json.dumps({"figure": "F4.8", "run_id": run_id, "code_commit_sha": arc.SCIENTIFIC_PIN,
                      "created_utc": run_id[-25:]}))
    write(rel / "robustness/window_length_comparison.csv",
          f"series,rmse,run_id,created_utc\nUNRATE,0.5,{run_id},2099\n")
    write(rel / "manifests/correction_run_manifest.json", json.dumps({"run_id": run_id}))
    for i in range(n_files):
        write(rel / f"original/file_{i}.txt", f"unchanged {i}")
    sources = {"models/T3.1_in_sample_adequacy.csv": "original_unchanged",
               "figures/F4.8_UNRATE.png": "regenerated_r1",
               "figures/F4.8_UNRATE.png.provenance.json": "regenerated_integration_dependents",
               "robustness/window_length_comparison.csv": "regenerated_r1",
               "manifests/correction_run_manifest.json": "correction_record"}
    rows = []
    for p in sorted(x for x in rel.rglob("*") if x.is_file()):
        r = p.relative_to(rel).as_posix()
        rows.append({"path": r, "bytes": p.stat().st_size, "sha256": sha(p.read_bytes()),
                     "source": sources.get(r, "original_unchanged"), "original_sha256": ""})
    with open(write(rel / arc.INVENTORY, ""), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return rel


def make_dryrun(root: Path, session: str, run_id: str, *, wald_p: str = "0.034") -> Path:
    d = root / "dryrun" / session
    make_release(d, run_id)
    write(d / "dryrun_report/acceptance.json", json.dumps({
        "dry_run": True, "published": False, "run_id": run_id, "accepted": True, "failed_criteria": [],
        "orchestration_commit": arc.AUDITED_ORCHESTRATION, "scientific_commit": arc.SCIENTIFIC_PIN,
        "criteria": {"A1": {"pass": True, "detail": {"note": f"{session}/x"}},
                     "A13": {"pass": True, "detail": {"manifest": {"run_id": run_id}}}}}))
    write(d / "dryrun_report/unexplained_differences.csv", "empty\r\n")
    legacy = arc.AUDITED_LEGACY_RUN_ID if run_id == arc.AUDITED_RUN_ID else NEW_LEGACY
    write(d / "dryrun_report/aggregation_plan.json", json.dumps({
        "run_id": run_id, "assembly": {"legacy_run_id": legacy, "corrected_run_id": run_id,
                                       "regenerated_files": 95}}))
    write(d / "dryrun_report/decision_changes.csv", f"path,row,old,new\nall_test_results,250,0.476,{wald_p}\n")
    write(d / "dryrun_report/cells_vs_published.csv.gz", gzip.compress(b"path,row,new\nx,1,2\n", mtime=1))
    write(d / "dryrun_report/console.log", f"started {session} at some time")
    write(d / "stages/validate.json", json.dumps({"stage": "validate", "finished_utc": "2099",
                                                  "run_id": run_id, "unexplained": 0}))
    write(d / "base_manifest.csv", "path,sha256\na,b\n")
    write(d / "dryrun_report/files_vs_published.csv",
          "path,status\nrobustness/window_length_comparison.csv,changed\n")
    write(d / "base/figures/F4.8_UNRATE.png.provenance.json",
          json.dumps({"figure": "F4.8", "run_id": "baseline-x", "code_commit_sha": "46a5",
                      "created_utc": "2026-10-30"}))
    return d


def make_export(root: Path, dryrun: Path, monkeypatch) -> Path:
    """Export a dry run as the notebook does, and pin the test manifest/inventory hashes."""
    export = root / "export"
    files = []
    for rel, path in arc.export_layout(dryrun).items():
        write(export / rel, path.read_bytes())
        files.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha(path.read_bytes())})
    write(export / "export_manifest.json", json.dumps({"session": AUDITED, "files": files}))
    monkeypatch.setattr(arc, "AUDITED_EXPORT_MANIFEST_SHA256", sha((export / "export_manifest.json").read_bytes()))
    monkeypatch.setattr(arc, "AUDITED_EXPORT_FILES", len(files))
    monkeypatch.setattr(arc, "AUDITED_INVENTORY_SHA256",
                        sha((export / "release_manifests/output_inventory.csv").read_bytes()))
    monkeypatch.setattr(arc, "RELEASE_FILES", len(arc.listing(dryrun / "release")))
    return export


@pytest.fixture
def audited(tmp_path, monkeypatch):
    dry = make_dryrun(tmp_path / "audited", AUDITED, arc.AUDITED_RUN_ID)
    return dry, make_export(tmp_path, dry, monkeypatch)


# -- export verification --------------------------------------------------------------------

def test_audited_export_is_verified_and_tampering_refused(audited):
    _, export = audited
    assert arc.verify_audited_export(export)["session"] == AUDITED
    (export / "decision_changes.csv").write_text("tampered")
    with pytest.raises(arc.ArchiveRefused, match="missing or altered"):
        arc.verify_audited_export(export)


def test_export_layout_matches_the_integration_notebook():
    import make_r1_part8_integration_notebook as nb
    for source, prefix in arc.EXPORT_SOURCES:
        parts = source.split("/")
        expr = "DRYRUN / " + " / ".join(f'"{p}"' for p in parts)
        assert f'({expr}, "{prefix}")' in nb.EXPORT_CELL, source


# -- PRESERVE -------------------------------------------------------------------------------

def test_preserve_accepts_the_exact_tree(audited):
    dry, export = audited
    report = arc.preserve_check(dry / "release", export)
    assert report["ok"] and not report["altered"]


@pytest.mark.parametrize("change", ["alter", "extra", "missing"])
def test_preserve_refuses_any_file_difference(audited, change):
    dry, export = audited
    rel = dry / "release"
    if change == "alter":
        (rel / "original/file_0.txt").write_text("changed")
    elif change == "extra":
        write(rel / "stray.txt", "x")
    else:
        (rel / "original/file_1.txt").unlink()
    with pytest.raises(arc.ArchiveRefused):
        arc.preserve_check(rel, export)


# -- RECONSTRUCT ---------------------------------------------------------------------------

def test_gate_accepts_a_reconstruction_differing_only_in_provenance(audited, tmp_path):
    _, export = audited
    new = make_dryrun(tmp_path / "new", NEW, NEW_RUN)
    report = arc.equivalence_gate(new, export, exit_code=4, new_session=NEW, new_run_id=NEW_RUN,
                                published_dir=tmp_path / "published")
    assert report["ok"]
    assert set(report["inventory"]["provenance_only"]) == {
        "figures/F4.8_UNRATE.png.provenance.json", "robustness/window_length_comparison.csv",
        "manifests/correction_run_manifest.json"}
    assert report["reports"]["not_compared"] == {"console.log": "run log (timings and paths)"}


def test_gate_refuses_a_changed_numerical_result(audited, tmp_path):
    _, export = audited
    new = make_dryrun(tmp_path / "new", NEW, NEW_RUN, wald_p="0.035")
    with pytest.raises(arc.ArchiveRefused, match="reports_identical"):
        arc.equivalence_gate(new, export, exit_code=4, new_session=NEW, new_run_id=NEW_RUN,
                                published_dir=tmp_path / "published")


def test_gate_refuses_a_changed_figure_or_original_file(audited, tmp_path):
    _, export = audited
    new = make_dryrun(tmp_path / "new", NEW, NEW_RUN)
    rel = new / "release"
    (rel / "figures/F4.8_UNRATE.png").write_bytes(b"\x89PNG-different")
    (rel / "original/file_2.txt").write_text("different")
    _reinventory(rel)
    with pytest.raises(arc.ArchiveRefused, match="release_inventory"):
        arc.equivalence_gate(new, export, exit_code=4, new_session=NEW, new_run_id=NEW_RUN,
                                published_dir=tmp_path / "published")
    inv = arc.compare_inventory(rel, export, (new / "base",))
    assert inv["refused"] == {"figures/F4.8_UNRATE.png": "figure must be byte-identical",
                              "original/file_2.txt": "original file must be byte-identical"}


def test_gate_refuses_non_provenance_json_change_and_wrong_exit(audited, tmp_path):
    _, export = audited
    new = make_dryrun(tmp_path / "new", NEW, NEW_RUN)
    write(new / "stages/validate.json", json.dumps({"stage": "validate", "finished_utc": "x",
                                                    "run_id": NEW_RUN, "unexplained": 1}))
    with pytest.raises(arc.ArchiveRefused):
        arc.equivalence_gate(new, export, exit_code=4, new_session=NEW, new_run_id=NEW_RUN,
                                published_dir=tmp_path / "published")
    new2 = make_dryrun(tmp_path / "new2", NEW, NEW_RUN)
    with pytest.raises(arc.ArchiveRefused, match="exit_code"):
        arc.equivalence_gate(new2, export, exit_code=0, new_session=NEW, new_run_id=NEW_RUN,
                                published_dir=tmp_path / "published")


def test_table_without_provenance_columns_may_not_differ(audited, tmp_path):
    _, export = audited
    new = make_dryrun(tmp_path / "new", NEW, NEW_RUN)
    rel = new / "release"
    write(rel / "robustness/window_length_comparison.csv", "series,rmse\nUNRATE,0.6\n")
    _reinventory(rel)
    assert "robustness/window_length_comparison.csv" in arc.compare_inventory(rel, export)["refused"]


def test_table_outside_the_audited_cell_comparison_may_not_differ(audited, tmp_path):
    _, export = audited
    (export / "files_vs_published.csv").write_text("path,status\n")   # (only read, not hashed here)
    new = make_dryrun(tmp_path / "new", NEW, NEW_RUN)
    inv = arc.compare_inventory(new / "release", export, (new / "base",))
    assert inv["refused"]["robustness/window_length_comparison.csv"].startswith("table differs but")


@pytest.mark.parametrize("sidecar, reason", [
    ({"figure": "F4.8", "run_id": "r", "code_commit_sha": "46a5"}, "does not name the scientific pin"),
    ({"figure": "F9.9", "run_id": "r", "code_commit_sha": arc.SCIENTIFIC_PIN}, "differs from"),
    ({"figure": "F4.8", "run_id": "r", "code_commit_sha": arc.SCIENTIFIC_PIN,
      "integration_dry_run": "something else"}, "unexpected text"),
])
def test_sidecars_may_differ_only_in_provenance(audited, tmp_path, sidecar, reason):
    _, export = audited
    new = make_dryrun(tmp_path / "new", NEW, NEW_RUN)
    write(new / "release/figures/F4.8_UNRATE.png.provenance.json", json.dumps(sidecar))
    _reinventory(new / "release")
    inv = arc.compare_inventory(new / "release", export, (new / "base",))
    assert reason in inv["refused"]["figures/F4.8_UNRATE.png.provenance.json"]


def test_sidecar_with_the_exact_integration_annotation_is_accepted(audited, tmp_path):
    _, export = audited
    new = make_dryrun(tmp_path / "new", NEW, NEW_RUN)
    write(new / "release/figures/F4.8_UNRATE.png.provenance.json", json.dumps(
        {"figure": "F4.8", "run_id": "r", "code_commit_sha": arc.SCIENTIFIC_PIN, "created_utc": "t",
         "integration_dry_run": arc.SIDECAR_ANNOTATIONS["integration_dry_run"]}))
    _reinventory(new / "release")
    inv = arc.compare_inventory(new / "release", export, (new / "base",))
    assert "figures/F4.8_UNRATE.png.provenance.json" in inv["provenance_only"]


def _reinventory(rel: Path) -> None:
    inv = arc.read_inventory(rel / arc.INVENTORY)
    for p, row in inv.items():
        row["sha256"] = sha((rel / p).read_bytes())
        row["bytes"] = str((rel / p).stat().st_size)
    with open(rel / arc.INVENTORY, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(next(iter(inv.values()))))
        w.writeheader()
        w.writerows(inv.values())


# -- the archive ---------------------------------------------------------------------------

def test_archive_is_deterministic_verified_and_never_overwrites(audited, tmp_path):
    dry, export = audited
    gate = arc.preserve_check(dry / "release", export)
    ident = arc.run_identity(mode="preserve", archive_session="archive-1", archive_tool_commit="t",
                             orchestration_commit=arc.AUDITED_ORCHESTRATION,
                             scientific_commit=arc.SCIENTIFIC_PIN, run_id=arc.AUDITED_RUN_ID,
                             source_session=AUDITED)
    drive = tmp_path / "drive"
    m1 = arc.write_archive(dry / "release", drive, "archive-1", ident, gate)
    m2 = arc.write_archive(dry / "release", drive, "archive-2", ident, gate)
    assert m1["release_tar_sha256"] == m2["release_tar_sha256"]
    assert arc.verify_archive(drive / arc.ARCHIVE_PARENT / "archive-1")["verified_members"] == m1["files"]
    with pytest.raises(arc.ArchiveRefused, match="exists"):
        arc.write_archive(dry / "release", drive, "archive-1", ident, gate)
    with pytest.raises(arc.ArchiveRefused, match="outside"):
        arc.write_archive(dry / "release", drive, "../escape", ident, gate)
    with pytest.raises(arc.ArchiveRefused, match="gate"):
        arc.write_archive(dry / "release", drive, "archive-3", ident, {"ok": False})


def test_tampered_archive_is_detected(audited, tmp_path):
    dry, export = audited
    gate = arc.preserve_check(dry / "release", export)
    drive = tmp_path / "drive"
    arc.write_archive(dry / "release", drive, "a", {"mode": "preserve"}, gate)
    dest = drive / arc.ARCHIVE_PARENT / "a"
    rows = (dest / "archive_inventory.csv").read_text().replace(",", ";", 1)
    (dest / "archive_inventory.csv").write_text(rows)
    with pytest.raises(arc.ArchiveRefused):
        arc.verify_archive(dest)


def test_real_audited_export_constants_match_the_committed_evidence():
    """The pinned hashes equal the audited export committed in the evidence folder."""
    ev = (Path(__file__).resolve().parents[3] / "reports/part8/corrections/r1/evidence"
          / "integration_dryrun_audit_20261108/colab_export")
    if not ev.exists():
        pytest.skip("evidence folder not present")
    assert arc.verify_audited_export(ev)["session"] == arc.AUDITED_SESSION
    inv = arc.read_inventory(ev / "release_manifests/output_inventory.csv")
    assert len(inv) + 1 == arc.RELEASE_FILES


# -- the generated notebook and preserve cell -------------------------------------------------

def test_archive_notebook_and_preserve_cell_are_safe_and_pinned(tmp_path):
    import ast
    import make_r1_part8_archive_notebook as mk
    nb = mk.build("f" * 40)
    code = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
    for src in code + [mk.preserve_cell("f" * 40)]:
        tree = ast.parse(src)
        for node in ast.walk(tree):          # the exec'd reconstruction cells parse too
            if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "compile":
                ast.parse(node.args[0].value)
    joined = "\n".join(code)
    assert f'ORCH_COMMIT = "{arc.AUDITED_ORCHESTRATION}"' in joined
    assert f'PIN_COMMIT = "{arc.SCIENTIFIC_PIN}"' in joined
    assert "CONFIRM_PUBLISH = False" in joined and "ALLOW_RECONSTRUCTION = False" in joined
    assert mk.TOOL_SHA256 == hashlib.sha256((COLAB / "r1_integration_archive.py").read_bytes()).hexdigest()
    assert f'ARCHIVE_TOOL_SHA256 = "{mk.TOOL_SHA256}"' in joined
    for forbidden in ("git push", "git commit", "publish_release", "output_corrected", "CONFIRM_PUBLISH = True"):
        assert forbidden not in joined and forbidden not in mk.preserve_cell("f" * 40)
    assert "arc.write_archive(RELEASE_DIR, DRIVE_ROOT" in joined


def test_committed_notebook_matches_the_generator():
    import make_r1_part8_archive_notebook as mk
    path = COLAB / mk.NOTEBOOK
    if not path.exists():
        pytest.skip("notebook not generated yet")
    nb = json.loads(path.read_text())
    tool = next(l for c in nb["cells"] for l in c["source"] if l.startswith("ARCHIVE_TOOL_COMMIT"))
    commit = tool.split('"')[1]
    assert nb == mk.build(commit)
    assert (COLAB / mk.PRESERVE_CELL_FILE).read_text() == mk.preserve_cell(commit)


# -- the legacy workflow pass's run id (aggregation_plan.json assembly.legacy_run_id) ----------

RECONSTRUCTED_LEGACY = "correction-20261108T103110-949fcd76"   # observed in the reconstruction
PLAN = "aggregation_plan.json"


def _real_plan() -> dict:
    return json.loads((REAL_EXPORT / PLAN).read_text())


def _tokens(new_run: str = NEW_RUN) -> dict:
    return {NEW: "<session>", AUDITED: "<session>", new_run: "<run_id>", arc.AUDITED_RUN_ID: "<run_id>"}


def _reconstructed_plan(**assembly) -> dict:
    plan = _real_plan()
    plan["run_id"] = NEW_RUN
    plan["assembly"] = dict(plan["assembly"], legacy_run_id=RECONSTRUCTED_LEGACY,
                            corrected_run_id=NEW_RUN, **assembly)
    return plan


def _compare(new: dict, audited: dict | None = None, relative: str = PLAN):
    audited = _real_plan() if audited is None else audited
    return arc.compare_report(relative, json.dumps(new).encode(), json.dumps(audited).encode(),
                              _tokens())


def test_real_audited_and_reconstructed_plans_pass_after_the_narrow_normalisation():
    audited = _real_plan()
    assert audited["assembly"]["legacy_run_id"] == arc.AUDITED_LEGACY_RUN_ID
    assert arc.sha256_file(REAL_EXPORT / PLAN) == next(
        f["sha256"] for f in json.loads((REAL_EXPORT / "export_manifest.json").read_text())["files"]
        if f["path"] == PLAN)                       # the committed audited evidence, unmodified
    assert _compare(_reconstructed_plan()) is None
    # Without the field-specific rule the same pair is refused (the failure seen in Colab).
    assert _compare(_reconstructed_plan(), relative="other_plan.json") is not None


@pytest.mark.parametrize("change", [
    lambda p: p["assembly"].update(regenerated_files=94),
    lambda p: p["assembly"]["flags"].update(f8_readable_main_panel=True),
    lambda p: p["assembly"]["estimations_performed"]["legacy"].update(T41=1),
    lambda p: p["assembly"]["reconciliation"][1].update(cells_changed_by_corrections=7),
    lambda p: p["assembly"].update(corrected_run_id="correction-20261108T999999-949fcd76"),
    lambda p: p.update(publish=True),
    lambda p: p.pop("cache_integrity"),
], ids=["regenerated_files", "flag", "estimation", "reconciliation_cells", "corrected_run_id",
        "publish", "dropped_section"])
def test_any_substantive_change_in_the_plan_is_still_refused(change):
    plan = _reconstructed_plan()
    change(plan)
    assert _compare(plan) == "JSON content differs beyond the identified provenance keys"


@pytest.mark.parametrize("value", [None, "", "baseline-20261108T103110-949fcd76",
                                   "correction-20261108T103110-deadbeef",
                                   "correction-2026-11-08T10:31:10-949fcd76",
                                   " correction-20261108T103110-949fcd76", 7])
def test_malformed_or_missing_legacy_run_id_is_refused(value):
    plan = _reconstructed_plan()
    if value is None:
        plan["assembly"].pop("legacy_run_id")
    else:
        plan["assembly"]["legacy_run_id"] = value
    assert "missing or not a run id" in _compare(plan)


def test_unexpected_run_identification_fields_remain_detectable():
    # The reconstructed legacy run id appearing in any other field is still a difference.
    plan = _reconstructed_plan()
    plan["merge"] = dict(plan["merge"], source_run=RECONSTRUCTED_LEGACY)
    audited = _real_plan()
    audited["merge"] = dict(audited["merge"], source_run=arc.AUDITED_LEGACY_RUN_ID)
    assert _compare(plan, audited) is not None
    # A new run-identification key, even next to the admitted one, is not normalised.
    plan = _reconstructed_plan(legacy_run_id_retry=RECONSTRUCTED_LEGACY)
    assert _compare(plan, dict(_real_plan(), assembly=dict(
        _real_plan()["assembly"], legacy_run_id_retry=arc.AUDITED_LEGACY_RUN_ID))) is not None
    # The same field name in another report is not normalised.
    other = {"assembly": {"legacy_run_id": RECONSTRUCTED_LEGACY}}
    assert _compare(other, {"assembly": {"legacy_run_id": arc.AUDITED_LEGACY_RUN_ID}},
                    relative="stages/aggregate.json") is not None
    # The audited side must carry the audited session's legacy run id.
    assert "audited assembly.legacy_run_id" in _compare(
        _reconstructed_plan(), dict(_real_plan(), assembly=dict(
            _real_plan()["assembly"], legacy_run_id=RECONSTRUCTED_LEGACY)))


def test_gate_accepts_a_reconstruction_whose_legacy_run_id_differs(audited, tmp_path):
    _, export = audited
    new = make_dryrun(tmp_path / "new", NEW, NEW_RUN)
    plan = json.loads((new / "dryrun_report" / PLAN).read_text())
    assert plan["assembly"]["legacy_run_id"] == NEW_LEGACY != arc.AUDITED_LEGACY_RUN_ID
    report = arc.equivalence_gate(new, export, exit_code=4, new_session=NEW, new_run_id=NEW_RUN,
                                  published_dir=tmp_path / "published")
    assert report["ok"] and PLAN in report["allowed_differences"]["json_fields"]
    # ...and refuses when anything else in the plan changes as well.
    plan["assembly"]["regenerated_files"] = 96
    write(new / "dryrun_report" / PLAN, json.dumps(plan))
    with pytest.raises(arc.ArchiveRefused, match="reports_identical"):
        arc.equivalence_gate(new, export, exit_code=4, new_session=NEW, new_run_id=NEW_RUN,
                             published_dir=tmp_path / "published")
