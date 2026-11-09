"""Recovery of an interrupted D3 publication: runtime loss at every external boundary."""
from __future__ import annotations

import ast
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
COLAB = ROOT / "colab"
sys.path.insert(0, str(COLAB))
sys.path.insert(0, str(HERE))
import r1_part8_final_release as rel  # noqa: E402
import r1_part8_release_recovery as rec  # noqa: E402
import test_r1_part8_final_release as base  # noqa: E402

def _git(args, cwd):
    return base._git(args, cwd)


class Remote:
    """A GitHub remote seen through `ls-remote`; `push` records and moves the head."""

    def __init__(self):
        self.head, self.pushes, self.fail = None, [], False

    def push(self, repo, commit, branch, env):
        if self.fail:
            raise rel.ReleaseRefused("connection lost")
        self.pushes.append(commit)
        self.head = commit

    def remote_head(self, repo, branch, env):
        return self.head


class Lost(Exception):
    """The Colab runtime disappeared."""


@pytest.fixture
def world(tmp_path, monkeypatch):
    """A first runtime that staged a release; returns everything a lost runtime leaves behind."""
    tmp = tmp_path
    origin = tmp / "origin"
    origin.mkdir()
    _git(["init", "-q"], origin)
    _git(["config", "user.email", "t@t"], origin)
    _git(["config", "user.name", "t"], origin)
    for path in base.OTHER:
        base.write(origin / rel.OUTPUT_PREFIX / path, "baseline value\n")
    _git(["add", "-A"], origin)
    _git(["commit", "-q", "-m", "pin"], origin)
    monkeypatch.setattr(rel, "SCIENTIFIC_PIN", _git(["rev-parse", "HEAD"], origin))
    # the synthetic archive, render and release, built against this repository's "pin"
    tree = base.make_archive_tree(tmp)
    render = base.make_render(tmp, tree)
    monkeypatch.setattr(rel, "RELEASE_FILES", len(rel.listing(tree)))
    monkeypatch.setattr(rel, "APPROVED_F8", {p: base.sha(f"F8 figure {p}".encode()) for p in rel.F34})
    op = rel.render_operation("f8render-20261109T120000Z-abcdef", "2026-11-09T12:00:00Z", "a" * 40)
    report = rel.assemble(tree, render, tmp / "release_tree", op)
    first = tmp / "runtime1"
    _git(["clone", "-q", str(origin), str(first)], tmp)
    record = tmp / "record"
    rel.build_record(tmp / "release_tree", tree, record, identity={"publication_id": base.PUB},
                     assembly=report, render={"operation": op, "check": {}}, archive={})
    commit = rel.stage_git(first, tmp / "stage", tmp / "release_tree", record, "release")
    payload = tmp / "payload"
    rel.build_drive_payload(tmp / "release_tree", record, payload)
    return {"tmp": tmp, "archive": tree, "op": op, "origin": origin, "first": first, "commit": commit,
            "record": record, "payload": payload, "remote": Remote(), "drive": tmp / "drive"}


def lose_runtime_at(w, boundary: str):
    """Run the normal publication in the first runtime and lose the runtime at `boundary`."""
    remote = w["remote"]
    partial, final = rec.drive_paths(w["drive"])

    def push(repo, commit, branch, env):
        if boundary == "before_push":
            raise Lost()
        remote.push(repo, commit, branch, env)
        if boundary == "after_push":
            raise Lost()

    def rename(src, dst):
        if boundary == "before_rename":
            raise Lost()
        src.rename(dst)
        if boundary == "after_rename":
            raise Lost()

    if boundary == "during_drive_copy":
        partial.mkdir(parents=True)
        shutil.copyfile(w["payload"] / "release.tar.gz", partial / "release.tar.gz")
        return
    try:
        rel.publish(authorized=True, payload_dir=w["payload"], drive_root=w["drive"], repo=w["first"],
                    commit=w["commit"], tree=w["tmp"] / "release_tree", record_dir=w["record"],
                    status_path=w["tmp"] / "status1.json", git_env=None, push=push,
                    remote_head=remote.remote_head, rename=rename)
    except Lost:
        pass
    if boundary == "before_status":
        (final / "publication_status.json").unlink()      # simulate: died before writing it


def new_runtime(w):
    """A fresh runtime: a new clone; the commit is fetched from the remote when it exists."""
    repo = w["tmp"] / f"runtime{len(list(w['tmp'].glob('runtime*'))) + 1}"
    _git(["clone", "-q", str(w["origin"]), str(repo)], w["tmp"])
    if w["remote"].head:                                   # what `git fetch` brings from GitHub
        _git(["fetch", "-q", str(w["first"]), w["remote"].head], repo)
    return repo


def recover(w, repo, authorized=True, **kw):
    return rec.recover(authorized=authorized, repo=repo, drive_root=w["drive"],
                       archive_tree=w["archive"], work=repo / ".." / f"work_{repo.name}",
                       status_path=w["tmp"] / f"recovery_{repo.name}.json", git_env=None,
                       push=w["remote"].push, remote_head=w["remote"].remote_head,
                       fetch=lambda: None, **kw)


def snapshot(path: Path) -> dict:
    return {p: rel.sha256_file(path / p) for p in rel.listing(path)} if path.exists() else {}


# -- state detection --------------------------------------------------------------------------

@pytest.mark.parametrize("boundary, state", [
    ("during_drive_copy", "drive_partial_only"), ("before_push", "drive_partial_only"),
    ("after_push", "github_drive_partial"), ("before_rename", "github_drive_partial"),
    ("before_status", "complete_no_status"), ("after_rename", "published")])
def test_state_is_detected_after_runtime_loss(world, boundary, state):
    lose_runtime_at(world, boundary)
    if boundary == "after_rename":                   # finished in the same runtime earlier
        state = "complete_no_status"
    facts = rec.inspect_state(new_runtime(world), world["drive"], None, world["remote"].remote_head)
    assert facts["state"] == state


def test_nothing_started_is_not_a_recovery(world):
    with pytest.raises(rec.RecoveryRefused, match="normal release run"):
        recover(world, new_runtime(world))


# -- each boundary ----------------------------------------------------------------------------

def test_lost_during_drive_copy_refuses_and_leaves_the_partial(world):
    lose_runtime_at(world, "during_drive_copy")
    partial, _ = rec.drive_paths(world["drive"])
    before = snapshot(partial)
    with pytest.raises(rec.RecoveryRefused, match="incomplete"):
        recover(world, new_runtime(world))
    assert snapshot(partial) == before and not world["remote"].pushes


def test_lost_before_push_recovers_the_same_release(world):
    lose_runtime_at(world, "before_push")
    repo = new_runtime(world)
    log = recover(world, repo)
    assert log["result"] == "published" and len(world["remote"].pushes) == 1
    commit = world["remote"].head
    rel.verify_git_commit(repo, commit, world["tmp"] / "release_tree", world["record"])   # same release
    _, final = rec.drive_paths(world["drive"])
    status = json.loads((final / "publication_status.json").read_text())
    assert status["publication_id"] == base.PUB and status["recovered"] is True   # no new identity
    assert status["commit"] == commit and status["state"] == "published"


def test_lost_after_push_only_finalizes_drive(world):
    lose_runtime_at(world, "after_push")
    log = recover(world, new_runtime(world))
    assert log["result"] == "published" and world["remote"].pushes == [world["commit"]]   # no 2nd push
    _, final = rec.drive_paths(world["drive"])
    assert json.loads((final / "publication_status.json").read_text())["commit"] == world["commit"]


def test_lost_before_rename_only_finalizes_drive(world):
    lose_runtime_at(world, "before_rename")
    assert recover(world, new_runtime(world))["result"] == "published"
    assert len(world["remote"].pushes) == 1


def test_lost_before_status_records_the_status_only(world):
    lose_runtime_at(world, "before_status")
    _, final = rec.drive_paths(world["drive"])
    before = {k: v for k, v in snapshot(final).items()}
    log = recover(world, new_runtime(world))
    assert log["result"] == "published" and len(world["remote"].pushes) == 1
    after = snapshot(final)
    assert {k: after[k] for k in before} == before and set(after) - set(before) == {"publication_status.json"}


def test_published_release_is_verified_and_left_unchanged(world):
    lose_runtime_at(world, "before_status")
    recover(world, new_runtime(world))
    _, final = rec.drive_paths(world["drive"])
    before = snapshot(final)
    assert recover(world, new_runtime(world))["result"] == "already_published"
    assert snapshot(final) == before


def test_recovery_needs_its_own_authorization(world):
    lose_runtime_at(world, "after_push")
    partial, _ = rec.drive_paths(world["drive"])
    before = snapshot(partial)
    log = recover(world, new_runtime(world), authorized=False)
    assert log["result"] == "not_authorized" and snapshot(partial) == before
    assert "finish Drive finalization" in log["steps"][-1]["would"]


# -- conflicts and unverifiable provenance ----------------------------------------------------

def test_github_commit_that_differs_from_the_drive_payload_refuses(world):
    lose_runtime_at(world, "after_push")
    repo = new_runtime(world)
    other = world["tmp"] / "other_tree"
    shutil.copytree(world["tmp"] / "release_tree", other)
    (other / base.OTHER[0]).write_bytes(b"a different number\n")
    stage = world["tmp"] / "stage_other"
    _git(["worktree", "add", "-q", "--detach", str(stage), rel.SCIENTIFIC_PIN], repo)
    for p in rel.listing(other):
        base.write(stage / rel.OUTPUT_PREFIX / p, (other / p).read_bytes())
    shutil.copytree(world["record"], stage / rel.RECORD_PREFIX)
    _git(["add", "-A"], stage)
    _git(["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "tampered"], stage)
    world["remote"].head = _git(["rev-parse", "HEAD"], stage)
    with pytest.raises(rec.RecoveryRefused, match="does not match the Drive payload"):
        recover(world, repo)


def test_tampered_payload_refuses_even_if_internally_consistent(world, monkeypatch):
    lose_runtime_at(world, "before_push")
    partial, _ = rec.drive_paths(world["drive"])
    # rebuild a self-consistent payload around a changed protected file
    bad_tree = world["tmp"] / "bad_tree"
    shutil.copytree(world["tmp"] / "release_tree", bad_tree)
    (bad_tree / base.OTHER[1]).write_bytes(b"changed forecast table\n")
    bad_record = world["tmp"] / "bad_record"
    shutil.copytree(world["record"], bad_record)
    inv = rel.release_inventory_bytes(bad_tree)
    (bad_record / "release_inventory.csv").write_bytes(inv)
    manifest = json.loads((bad_record / "release_manifest.json").read_text())
    manifest["release_inventory_sha256"] = rel.sha256_bytes(inv)
    (bad_record / "release_manifest.json").write_text(json.dumps(manifest))
    bad = world["tmp"] / "bad_payload"
    rel.build_drive_payload(bad_tree, bad_record, bad)
    for name in rec.RECORD_FILES + ("release.tar.gz",):
        shutil.copyfile(bad / name, partial / name)
    with pytest.raises(rec.RecoveryRefused, match="not the approved release"):
        recover(world, new_runtime(world))
    assert not world["remote"].pushes


@pytest.mark.parametrize("field, value", [("publication", {"publication_id": "<new>"}),
                                          ("numbers", {"run_id": "correction-20990101T000000-949fcd76"})])
def test_unverifiable_identity_refuses(world, field, value):
    lose_runtime_at(world, "before_push")
    partial, _ = rec.drive_paths(world["drive"])
    manifest = json.loads((partial / "release_manifest.json").read_text())
    manifest["identities"][field].update(value)
    text = json.dumps(manifest, indent=1, sort_keys=True)
    (partial / "release_manifest.json").write_text(text)
    with pytest.raises(rec.RecoveryRefused):
        recover(world, new_runtime(world))


@pytest.mark.parametrize("make", ["final_without_branch", "branch_without_drive", "partial_and_final"])
def test_conflicting_states_refuse_and_change_nothing(world, make):
    partial, final = rec.drive_paths(world["drive"])
    if make == "final_without_branch":
        shutil.copytree(world["payload"], final)
    elif make == "branch_without_drive":
        world["remote"].head = world["commit"]
    else:
        world["remote"].head = world["commit"]
        shutil.copytree(world["payload"], partial)
        shutil.copytree(world["payload"], final)
    before = (snapshot(partial), snapshot(final))
    with pytest.raises(rec.RecoveryRefused, match="conflicting"):
        recover(world, new_runtime(world))
    assert (snapshot(partial), snapshot(final)) == before and not world["remote"].pushes


def test_existing_status_that_does_not_match_refuses(world):
    lose_runtime_at(world, "before_status")
    _, final = rec.drive_paths(world["drive"])
    (final / "publication_status.json").write_text(json.dumps({"state": "published", "commit": "0" * 40}))
    with pytest.raises(rec.RecoveryRefused, match="status file"):
        recover(world, new_runtime(world))


def test_branch_appearing_during_recovery_is_not_overwritten(world):
    lose_runtime_at(world, "before_push")
    repo = new_runtime(world)
    calls = {"n": 0}

    def remote_head(r, b, e):                 # absent when inspected, present before the push
        calls["n"] += 1
        return None if calls["n"] == 1 else "e" * 40
    with pytest.raises(rec.RecoveryRefused, match="appeared"):
        rec.recover(authorized=True, repo=repo, drive_root=world["drive"], archive_tree=world["archive"],
                    work=world["tmp"] / "w", status_path=world["tmp"] / "s.json", git_env=None,
                    push=world["remote"].push, remote_head=remote_head, fetch=lambda: None)
    assert not world["remote"].pushes


def test_recovered_status_satisfies_the_report_finalizer(world):
    lose_runtime_at(world, "after_push")
    recover(world, new_runtime(world))
    _, final = rec.drive_paths(world["drive"])
    status = json.loads((final / "publication_status.json").read_text())
    status["published_utc"] = "20261110T090000Z"
    sys.path.insert(0, str(ROOT / "reports" / "part8" / "final"))
    import finalize_reports as fin
    status["drive_final"] = "/content/drive/x/" + fin.DRIVE_FOLDER
    assert fin.check_status(status)["commit"] == world["commit"]


# -- safety -----------------------------------------------------------------------------------

def test_recovery_never_deletes_or_forces():
    tree = ast.parse((COLAB / "r1_part8_release_recovery.py").read_text())
    literals = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    assert not literals & {"--force", "--force-with-lease", "--delete", "-D", "--mirror"}
    calls = {n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert not calls & {"rmtree", "unlink", "remove", "rmdir"}


def test_notebook_routes_to_recovery_with_separate_authorization():
    import make_r1_part8_final_release_notebook as mk
    nb = mk.build("c" * 40)
    text = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
    assert "AUTHORIZE_PUBLICATION = False" in text and "AUTHORIZE_RECOVERY = False" in text
    assert "not (AUTHORIZE_PUBLICATION and AUTHORIZE_RECOVERY)" in text
    assert "rec.inspect_state(" in text and "rec.recover(authorized=AUTHORIZE_RECOVERY" in text
    assert f'RECOVERY_SHA256 = "{mk.RECOVERY_SHA256}"' in text
    for inner in (mk.RENDER, mk.ASSEMBLE, mk.STAGE, mk.PUBLISH, mk.RECOVER):
        ast.parse(inner)
    assert text.count("recovery mode: skipped") == 4
