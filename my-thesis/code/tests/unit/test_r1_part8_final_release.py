"""D3 final release: assembly, 25-path allowlist, provenance, identity, publication guards."""
from __future__ import annotations

import ast
import csv
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
COLAB = ROOT / "colab"
sys.path.insert(0, str(COLAB))
import r1_part8_final_release as rel  # noqa: E402

FINAL = ROOT / "reports" / "part8" / "final"
PUB = "publish-20261109T120500Z-123456"
OTHER = ("forecasts/forecasts_UNRATE.parquet", "forecast_tests/T3.3_main_forecast_table.csv",
         "models/fit_records.csv", "robustness/T4.7_failure_registry.csv", ".gitkeep")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write(path: Path, data) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data.encode() if isinstance(data, str) else data)
    return path


def make_archive_tree(root: Path) -> Path:
    tree = root / "archive_tree"
    for i, rel_path in enumerate(OTHER):
        write(tree / rel_path, f"protected content {i}\n")
    for rel_path in rel.F34:
        write(tree / rel_path, f"pre-F8 figure {rel_path}".encode())
        name = Path(rel_path).name
        write(tree / f"{rel_path}.provenance.json", json.dumps(
            {"artifact": name, "code_commit_sha": rel.SCIENTIFIC_PIN, "config_hash": "949fcd76",
             "created_utc": "2026-11-09T08:05:00Z", "data_snapshot_hash": "7e7dc769",
             "figure_id": "F3.4", "horizon": 1, "run_id": rel.NUMBERS_RUN_ID,
             "series": name.split("_")[1].split(".")[0]}, indent=2, sort_keys=True))
    rows = ["path,bytes,sha256,source,original_sha256"]
    for path, digest in sorted(rel.listing(tree).items()):
        size = (tree / path).stat().st_size
        rows.append(f"{path},{size},{digest},regenerated_r1,{'0' * 64}")
    write(tree / rel.INVENTORY, "\n".join(rows))
    return tree


def make_render(root: Path, tree: Path) -> Path:
    render = root / "render"
    for rel_path in rel.F34:
        name = Path(rel_path).name
        write(render / "legacy" / name, (tree / rel_path).read_bytes())
        write(render / "f8" / name, f"F8 figure {rel_path}".encode())
    write(render / "render_report.json", json.dumps(
        {"render_guard": {"ok": True}, "estimations_permitted": {}}))
    return render


@pytest.fixture
def setup(tmp_path, monkeypatch):
    tree = make_archive_tree(tmp_path)
    render = make_render(tmp_path, tree)
    monkeypatch.setattr(rel, "RELEASE_FILES", len(rel.listing(tree)))
    monkeypatch.setattr(rel, "APPROVED_F8", {p: sha(f"F8 figure {p}".encode()) for p in rel.F34})
    op = rel.render_operation("f8render-20261109T120000Z-abcdef", "2026-11-09T12:00:00Z", "a" * 40)
    return tmp_path, tree, render, op


def assembled(setup_):
    tmp, tree, render, op = setup_
    report = rel.assemble(tree, render, tmp / "release_tree", op)
    return tmp, tree, render, op, report


# -- assembly and the 25-path allowlist -------------------------------------------------------

def test_assembly_changes_exactly_the_25_allowed_paths(setup):
    tmp, tree, render, op, report = assembled(setup)
    assert len(rel.ALLOWED_CHANGES) == 25
    assert set(report["changed"]) == rel.ALLOWED_CHANGES
    new, old = rel.listing(tmp / "release_tree"), rel.listing(tree)
    for path in OTHER:                                  # protected inputs byte-identical
        assert new[path] == old[path]
    for path in rel.F34:
        assert new[path] == rel.APPROVED_F8[path]


def test_inventory_rewrites_only_the_24_rows(setup):
    tmp, tree, *_ = assembled(setup)
    old = (tree / rel.INVENTORY).read_text().split("\n")
    new = (tmp / "release_tree" / rel.INVENTORY).read_text().split("\n")
    changed = [b.split(",")[0] for a, b in zip(old, new) if a != b]
    assert sorted(changed) == sorted(rel.F34 + rel.SIDECARS)
    for line in new[1:]:
        path, size, digest, source, original = line.split(",")
        assert digest == rel.listing(tmp / "release_tree")[path]
        if path in rel.ALLOWED_CHANGES:
            assert source == rel.INVENTORY_SOURCE_F8 and original == "0" * 64


@pytest.mark.parametrize("tamper", ["protected", "extra", "missing", "unamended"])
def test_any_other_difference_refuses(setup, tamper):
    tmp, tree, render, op, _ = assembled(setup)
    out = tmp / "release_tree"
    if tamper == "protected":
        (out / "forecasts/forecasts_UNRATE.parquet").write_text("changed number\n")
    elif tamper == "extra":
        write(out / "forecasts/new.csv", "x")
    elif tamper == "missing":
        (out / "models/fit_records.csv").unlink()
    else:
        shutil.copyfile(tree / rel.SIDECARS[0], out / rel.SIDECARS[0])
    with pytest.raises(rel.ReleaseRefused):
        rel.verify_release_tree(out, tree, op["operation_id"])


def test_assembly_never_overwrites(setup):
    tmp, tree, render, op = setup
    (tmp / "release_tree").mkdir()
    with pytest.raises(rel.ReleaseRefused, match="exists"):
        rel.assemble(tree, render, tmp / "release_tree", op)


# -- rendering checks -------------------------------------------------------------------------

@pytest.mark.parametrize("fault", ["legacy", "f8", "guard", "estimation"])
def test_render_check_refuses(setup, fault):
    tmp, tree, render, op = setup
    if fault == "legacy":
        write(render / "legacy" / Path(rel.F34[0]).name, b"different")
    elif fault == "f8":
        write(render / "f8" / Path(rel.F34[3]).name, b"not the approved figure")
    else:
        report = {"render_guard": {"ok": fault != "guard"},
                  "estimations_permitted": {"fit_msar": 1} if fault == "estimation" else {}}
        write(render / "render_report.json", json.dumps(report))
    with pytest.raises(rel.ReleaseRefused):
        rel.check_render(render, tree)


def test_render_check_accepts_the_reviewed_case(setup):
    tmp, tree, render, op = setup
    assert rel.check_render(render, tree)["f8_equals_approved"] == 12


# -- provenance and identities ------------------------------------------------------------------

def test_sidecars_separate_numbers_run_from_figure_operation(setup):
    tmp, tree, render, op, _ = assembled(setup)
    side = json.loads((tmp / "release_tree" / rel.SIDECARS[0]).read_text())
    assert side["run_id"] == side["numbers_run_id"] == rel.NUMBERS_RUN_ID
    assert side["numbers_audited_run_id"] == rel.AUDITED_RUN_ID
    assert side["code_commit_sha"] == rel.SCIENTIFIC_PIN
    fo = side["figure_operation"]
    assert fo["operation_id"] == op["operation_id"] and fo["plotting_code_commit"] == rel.SCIENTIFIC_PIN
    assert fo["archived_figure_sha256"] == rel.listing(tree)[rel.F34[0]]
    assert fo["archived_figure_created_utc"] == "2026-11-09T08:05:00Z"
    assert side["figure_sha256"] == rel.APPROVED_F8[rel.F34[0]]
    assert not rel.PLACEHOLDER.search(json.dumps(side))


@pytest.mark.parametrize("fault", ["missing_key", "wrong_pin", "placeholder", "wrong_run"])
def test_missing_or_wrong_provenance_refuses(setup, fault):
    tmp, tree, render, op, _ = assembled(setup)
    path = tmp / "release_tree" / rel.SIDECARS[2]
    side = json.loads(path.read_text())
    if fault == "missing_key":
        side.pop("figure_operation")
    elif fault == "wrong_pin":
        side["code_commit_sha"] = "0" * 40
    elif fault == "placeholder":
        side["run_id"] = "<release run id>"
    else:
        side["numbers_run_id"] = "correction-20990101T000000-949fcd76"
    path.write_text(json.dumps(side))
    with pytest.raises(rel.ReleaseRefused):
        rel.verify_release_tree(tmp / "release_tree", tree, op["operation_id"])


def test_archived_sidecar_from_another_run_is_refused(setup):
    tmp, tree, render, op = setup
    path = tree / rel.SIDECARS[0]
    side = json.loads(path.read_text())
    side["run_id"] = "correction-20261107T193414-949fcd76"
    path.write_text(json.dumps(side))
    with pytest.raises(rel.ReleaseRefused, match="numbers run"):
        rel.assemble(tree, render, tmp / "release_tree", op)


def test_operation_ids_are_validated():
    with pytest.raises(rel.ReleaseRefused):
        rel.render_operation("<f8 render>", "t", "a" * 40)
    with pytest.raises(rel.ReleaseRefused):
        rel.render_operation("f8render-20261109T120000Z-abcdef", "t", "abc")


def test_release_record_has_three_distinct_identities(setup):
    tmp, tree, render, op, report = assembled(setup)
    manifest = rel.build_record(tmp / "release_tree", tree, tmp / "record",
                                identity={"publication_id": PUB},
                                assembly=report, render={"operation": op, "check": {}},
                                archive={"archive": rel.ARCHIVE_SESSION})
    ids = manifest["identities"]
    assert ids["numbers"]["run_id"] == rel.NUMBERS_RUN_ID
    assert ids["figure"]["operation_id"] == op["operation_id"]
    assert ids["publication"]["publication_id"].startswith("publish-")
    assert manifest["canonical_path"] == "my-thesis/output"
    diff = list(csv.DictReader(open(tmp / "record" / "archive_to_release_diff.csv")))
    assert {r["path"] for r in diff} == rel.ALLOWED_CHANGES
    with pytest.raises(rel.ReleaseRefused, match="exists"):
        rel.build_record(tmp / "release_tree", tree, tmp / "record", identity={"publication_id": PUB},
                         assembly=report, render={"operation": op, "check": {}}, archive={})
    with pytest.raises(rel.ReleaseRefused, match="publication id"):
        rel.build_record(tmp / "release_tree", tree, tmp / "record2", identity={"publication_id": "<pub>"},
                         assembly=report, render={"operation": op, "check": {}}, archive={})


# -- archive input -----------------------------------------------------------------------------

def _tar(path: Path, members: dict[str, bytes], symlink: str | None = None) -> Path:
    with tarfile.open(path, "w:gz") as tar:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        if symlink:
            info = tarfile.TarInfo(symlink)
            info.type = tarfile.SYMTYPE
            info.linkname = "/etc/passwd"
            tar.addfile(info)
    return path


@pytest.mark.parametrize("bad", ["release/../escape.txt", "other/file.txt", "symlink"])
def test_safe_extract_refuses_unsafe_members(tmp_path, bad):
    members = {"release/a.csv": b"a"}
    tar = _tar(tmp_path / "t.tar.gz", members if bad == "symlink" else {**members, bad: b"x"},
               symlink="release/link" if bad == "symlink" else None)
    with pytest.raises(rel.ReleaseRefused):
        rel.safe_extract(tar, tmp_path / "out")


def test_archive_folder_must_be_the_verified_archive(tmp_path):
    with pytest.raises(rel.ReleaseRefused, match="not the approved archive"):
        rel.verify_archive_folder(tmp_path / "archive-20990101T000000Z-000000")
    folder = tmp_path / rel.ARCHIVE_SESSION
    write(folder / "release.tar.gz", b"not the archive")
    with pytest.raises(rel.ReleaseRefused, match="release.tar.gz"):
        rel.verify_archive_folder(folder)


# -- git staging and publication ---------------------------------------------------------------

def _git(args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def staged(setup, monkeypatch):
    tmp, tree, render, op, report = assembled(setup)
    repo = tmp / "repo"
    repo.mkdir()
    _git(["init", "-q"], repo)
    _git(["config", "user.email", "t@t"], repo)
    _git(["config", "user.name", "t"], repo)
    for path in OTHER:                                  # the pin holds the baseline subset
        write(repo / rel.OUTPUT_PREFIX / path, "baseline value\n")
    write(repo / "my-thesis/code/x.py", "code")
    _git(["add", "-A"], repo)
    _git(["commit", "-q", "-m", "pin"], repo)
    pin = _git(["rev-parse", "HEAD"], repo)
    monkeypatch.setattr(rel, "SCIENTIFIC_PIN", pin)
    record = tmp / "record"
    rel.build_record(tmp / "release_tree", tree, record, identity={"publication_id": PUB},
                     assembly=report, render={"operation": op, "check": {}}, archive={})
    commit = rel.stage_git(repo, tmp / "stage", tmp / "release_tree", record, "release")
    payload = tmp / "payload"
    rel.build_drive_payload(tmp / "release_tree", record, payload)
    return tmp, repo, commit, record, payload, pin


def test_staged_commit_is_the_pin_plus_exactly_the_release(staged):
    tmp, repo, commit, record, payload, pin = staged
    check = rel.verify_git_commit(repo, commit, tmp / "release_tree", record)
    assert check["parent"] == pin
    assert _git(["rev-parse", rel.RELEASE_BRANCH], repo) == commit
    names = _git(["diff", "--name-status", pin, commit], repo).splitlines()
    assert all(n.split("\t")[0] in ("M", "A") for n in names)
    with pytest.raises(rel.ReleaseRefused, match="exists"):           # never staged twice
        rel.stage_git(repo, tmp / "stage2", tmp / "release_tree", record, "again")


def test_a_baseline_file_missing_from_the_release_refuses(setup, monkeypatch):
    tmp, tree, render, op, report = assembled(setup)
    repo = tmp / "repo"
    repo.mkdir()
    _git(["init", "-q"], repo)
    _git(["config", "user.email", "t@t"], repo)
    _git(["config", "user.name", "t"], repo)
    write(repo / rel.OUTPUT_PREFIX / "superseded_only_in_baseline.csv", "old\n")
    _git(["add", "-A"], repo)
    _git(["commit", "-q", "-m", "pin"], repo)
    monkeypatch.setattr(rel, "SCIENTIFIC_PIN", _git(["rev-parse", "HEAD"], repo))
    rel.build_record(tmp / "release_tree", tree, tmp / "record", identity={"publication_id": PUB},
                     assembly=report, render={"operation": op, "check": {}}, archive={})
    with pytest.raises(rel.ReleaseRefused, match="leave or remove"):
        rel.stage_git(repo, tmp / "stage", tmp / "release_tree", tmp / "record", "release")


class Remote:
    def __init__(self, head=None, fail_push=False, wrong_head=False):
        self.head, self.fail_push, self.wrong_head, self.pushes = head, fail_push, wrong_head, []

    def push(self, repo, commit, branch, env):
        self.pushes.append((commit, branch))
        if self.fail_push:
            raise rel.ReleaseRefused("network down")
        self.head = "f" * 40 if self.wrong_head else commit

    def remote_head(self, repo, branch, env):
        return self.head


def _publish(staged_, remote, authorized=True):
    tmp, repo, commit, record, payload, pin = staged_
    return rel.publish(authorized=authorized, payload_dir=payload, drive_root=tmp / "drive",
                       repo=repo, commit=commit, tree=tmp / "release_tree", record_dir=record,
                       status_path=tmp / "status.json", git_env=None, push=remote.push,
                       remote_head=remote.remote_head)


def _drive(tmp):
    parent = tmp / "drive" / rel.DRIVE_RELEASE_PARENT
    return parent / f"{rel.RELEASE_ID}.partial", parent / rel.RELEASE_ID


def test_publication_requires_authorization(staged):
    remote = Remote()
    status = _publish(staged, remote, authorized=False)
    assert status["state"] == "not_authorized" and not remote.pushes
    assert not (staged[0] / "drive").exists()


def test_successful_publication_records_status_last(staged):
    remote = Remote()
    status = _publish(staged, remote)
    partial, final = _drive(staged[0])
    assert status["state"] == "published" and remote.pushes == [(staged[2], rel.RELEASE_BRANCH)]
    assert [s["state"] for s in status["steps"]] == ["drive_staged", "github_verified", "published"]
    assert final.exists() and not partial.exists()
    written = json.loads((final / "publication_status.json").read_text())
    assert written["state"] == "published"
    assert rel.verify_drive_payload(final)["members"] == rel.RELEASE_FILES


def test_existing_remote_branch_is_never_overwritten(staged):
    remote = Remote(head="e" * 40)
    with pytest.raises(rel.ReleaseRefused, match="exists"):
        _publish(staged, remote)
    assert not remote.pushes and not _drive(staged[0])[0].exists()


def test_existing_final_drive_folder_is_never_overwritten(staged):
    _drive(staged[0])[1].mkdir(parents=True)
    remote = Remote()
    with pytest.raises(rel.ReleaseRefused, match="never overwritten"):
        _publish(staged, remote)
    assert not remote.pushes


def test_push_failure_leaves_a_recorded_partial_state_and_resumes(staged):
    with pytest.raises(rel.ReleaseRefused, match="network"):
        _publish(staged, Remote(fail_push=True))
    status = json.loads((staged[0] / "status.json").read_text())
    partial, final = _drive(staged[0])
    assert status["state"] == "failed" and status["steps"][-1]["drive_partial_exists"] is True
    assert partial.exists() and not final.exists()
    resumed = _publish(staged, Remote())                    # the identical partial copy is reused
    assert resumed["state"] == "published" and final.exists()


def test_unverified_remote_head_does_not_finalize_drive(staged):
    with pytest.raises(rel.ReleaseRefused, match="not the release commit"):
        _publish(staged, Remote(wrong_head=True))
    partial, final = _drive(staged[0])
    assert partial.exists() and not final.exists()
    assert json.loads((staged[0] / "status.json").read_text())["state"] == "failed"


def test_partial_folder_with_other_content_refuses(staged):
    partial, _ = _drive(staged[0])
    write(partial / "release.tar.gz", b"something else")
    with pytest.raises(rel.ReleaseRefused, match="different content"):
        _publish(staged, Remote())


# -- notebook ---------------------------------------------------------------------------------

def test_notebook_is_safe_and_pinned():
    import make_r1_part8_final_release_notebook as mk
    nb = mk.build("b" * 40)
    sources = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
    for src in sources:
        ast.parse(src)
    text = "\n".join(sources)
    assert "AUTHORIZE_PUBLICATION = False" in text
    assert "--force" not in text and "push -f" not in text and "+refs" not in text
    assert "print(GITHUB_TOKEN" not in text and "THESIS_GIT_TOKEN" in text
    assert f'RELEASE_TOOL_SHA256 = "{mk.TOOL_SHA256}"' in text
    assert 'RELEASE_TOOL_COMMIT = "' + "b" * 40 in text
    assert "rel.verify_code_at_pin" in text and "rel.publish(authorized=AUTHORIZE_PUBLICATION" in text


def test_committed_notebook_matches_the_generator():
    import make_r1_part8_final_release_notebook as mk
    path = COLAB / mk.NOTEBOOK
    if not path.exists():
        pytest.skip("notebook not generated yet")
    nb = json.loads(path.read_text())
    commit = next(l for c in nb["cells"] for l in c["source"]
                  if l.startswith("RELEASE_TOOL_COMMIT")).split('"')[1]
    assert nb == mk.build(commit)


def test_tool_does_not_force_push_or_delete():
    tree = ast.parse((COLAB / "r1_part8_final_release.py").read_text())
    literals = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    assert not literals & {"--force", "-f+", "--force-with-lease", "--delete", "-D", "--mirror"}
    assert not any(l.startswith("+") and "refs" in l for l in literals)
    calls = {n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert "rmtree" not in calls and "unlink" not in calls


# -- constants against the committed evidence --------------------------------------------------

def test_constants_match_the_reviewed_evidence():
    review = ROOT / "reports/part8/corrections/r1/f8_review"
    approved = {r["figure"]: r["f8_sha256"] for r in csv.DictReader(open(review / "f8_figure_hashes.csv"))}
    assert approved == rel.APPROVED_F8
    assert sha((review / "f8_render.py").read_bytes()) == rel.RENDERER_SHA256
    inv = ROOT / "reports/part8/corrections/r1/evidence/archive_verification_20261109/archive_inventory.csv"
    assert sha(inv.read_bytes()) == rel.ARCHIVE_INVENTORY_SHA256
    rows = {r["path"]: r["sha256"] for r in csv.DictReader(open(inv))}
    assert rows[rel.INVENTORY] == rel.ARCHIVE_RELEASE_INVENTORY_SHA256
    assert len(rows) == rel.RELEASE_FILES and rel.ALLOWED_CHANGES <= set(rows)


# -- final reports ----------------------------------------------------------------------------

RELEASE_COMMIT = "9817daf91ac4cb4aaa42c2bef5deaff5b674841b"


def _pending_reports(dest: Path) -> Path:
    """The final reports as built before publication (from the accepted drafts)."""
    sys.path.insert(0, str(ROOT / "reports/part8/corrections/r1"))
    import make_final_reports as mk
    dest.mkdir(parents=True)
    for name in mk.REPORTS:
        (dest / name).write_text(mk.build_report(name), encoding="utf-8")
    original = mk.FINAL
    mk.FINAL = dest
    try:
        mk.build_matrix()
    finally:
        mk.FINAL = original
    return dest


def test_pending_reports_keep_r106_partial_until_publication(tmp_path):
    sys.path.insert(0, str(FINAL))
    import finalize_reports as fin
    pending = _pending_reports(tmp_path / "pending")
    for name in fin.REPORTS:
        text = (pending / name).read_text()
        assert "DRAFT" not in text and "Not yet published" in text and "<!--PUB:" in text
    jury = (pending / "jury_resolution_status.md").read_text()
    assert "| RESOLVED | 15 |" in jury and "R1-06 (until the release" in jury


def test_published_final_reports_record_the_release(tmp_path):
    sys.path.insert(0, str(FINAL))
    import finalize_reports as fin
    for name in fin.REPORTS:
        text = (FINAL / name).read_text()
        assert "<!--PUB:" not in text and "Not yet published" not in text and "DRAFT" not in text
        assert f"commit `{RELEASE_COMMIT}`" in text and "Published on 2026-11-10" in text
    jury = (FINAL / "jury_resolution_status.md").read_text()
    assert "| RESOLVED | 16 | R1-06," in jury and "| PARTIALLY ADDRESSED | 2 | R1-11 (empirical part only), P-04 (F6) |" in jury
    assert "P-04 stays PARTIALLY ADDRESSED" in jury
    claims = (FINAL / "final_claims_allowed.md").read_text()
    assert "**Status:** QUALIFIED (was SUPPORTED)" in claims and "[audit] sensitivity" in claims
    full = (FINAL / "full_empirical_analysis_report.md").read_text()
    for limitation in ("F6", "C16", "Holm", "degenerate", "optimiser", "INCONCLUSIVE", "M2SL"):
        assert limitation in full
    rows = list(csv.DictReader(open(FINAL / "claim_evidence_matrix_final.csv")))
    assert len(rows) == 24 and all(r["provisional"] == "False" for r in rows)
    status = {r["claim_id"]: r["candidate_status"] for r in rows}
    assert status["C16"] == "QUALIFIED" and status["C18"] == "QUALIFIED" and status["P04-regime-count"] == "QUALIFIED"
    assert {r["claim_id"] for r in rows if "F6" in r["provisional_due_to"]} == {"P04-regime-count", "C18"}
    published = json.loads((FINAL / "publication_status.json").read_text())
    assert fin.check_status(published)["commit"] == RELEASE_COMMIT
    assert RELEASE_COMMIT in (FINAL / "PUBLICATION.md").read_text()
    assert f"C={RELEASE_COMMIT}" in (FINAL / "SOURCE_OF_TRUTH.md").read_text()


def _status(commit="c" * 40, state="published"):
    steps = [{"state": "drive_staged"}, {"state": "github_verified"},
             {"state": "published", "tar_sha256": "d" * 64}]
    return {"release_id": "part8-final-20261109", "branch": "part8-corrected-results/final-20261109",
            "commit": commit, "state": state, "published_utc": "20261110T090000Z",
            "drive_final": "/content/drive/x/baseline/r1_part8_final_release/part8-final-20261109",
            "steps": steps if state == "published" else steps[:1]}


@pytest.mark.parametrize("status", [_status(state="failed"), _status(commit="abc"),
                                    {**_status(), "branch": "other"}])
def test_finalizer_refuses_without_verified_publication(status):
    sys.path.insert(0, str(FINAL))
    import finalize_reports as fin
    with pytest.raises(fin.NotPublished):
        fin.check_status(status)


def test_finalizer_resolves_r106_only_after_publication(tmp_path):
    sys.path.insert(0, str(FINAL))
    import finalize_reports as fin
    copy = _pending_reports(tmp_path / "final")
    status = tmp_path / "status.json"
    status.write_text(json.dumps(_status()))
    fin.finalize(status, copy, remote_check=False)
    jury = (copy / "jury_resolution_status.md").read_text()
    assert "| RESOLVED | 16 | R1-06," in jury and "<!--PUB:" not in jury
    assert "Not yet published" not in (copy / "main_findings.md").read_text()
    rows = list(csv.DictReader(open(copy / "claim_evidence_matrix_final.csv")))
    assert all(r["provisional"] == "False" for r in rows)
    assert {r["claim_id"] for r in rows if r["provisional_due_to"]} == {"P04-regime-count", "C18"}
    assert "P-04 (F6)" in jury
    with pytest.raises(fin.NotPublished, match="already finalized"):
        fin.finalize(status, copy, remote_check=False)
