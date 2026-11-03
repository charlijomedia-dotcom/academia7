"""R1 notebook step 8: it publishes the release the completed steps produced, never a stale one.

The step-8 cell is executed for real (from the regenerated notebook, and from the paste file
for a Colab session that is already open), against a fake work directory holding both a
step-6 release and a Tier A release. `git` is intercepted: nothing leaves the test.
"""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

COLAB = Path(__file__).resolve().parents[3] / "colab"
NOTEBOOK = COLAB / "r1_cache_replay.ipynb"
PASTE = COLAB / "r1_step8_publish_cell.py"
PIN = "8aaa4217536ab3cb942dd248dd19ece7838a8d60"
TIER_A = sorted(["T4.1:UNRATE|AR", "T4.1:FEDFUNDS|AR", "T4.2:CPIAUCSL|AR(p=1)",
                 "T4.2:CPIAUCSL|AR(p=3)", "T4.2:CPIAUCSL|AR(p=6)", "T4.2:CPIAUCSL|AR(p=12)",
                 "T4.8:UNRATE|180:AR", "T4.8:UNRATE|300:AR"])


def _step8_cell() -> str:
    cells = json.loads(NOTEBOOK.read_text())["cells"]
    return next("".join(c["source"]) for c in cells
                if c["cell_type"] == "code" and "def select_publication" in "".join(c["source"]))


def _write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload))


def _release(work: Path, staging: str, release: str, run_id: str, reestimated) -> None:
    sources = {"published": ["p"] * 48, "cache": ["c"] * 17, "unavailable": ["u"] * 35}
    if reestimated:
        sources["re-estimated"] = list(reestimated)
    _write(work / staging / "r1_summary.json",
           {"run_id": run_id, "chain_sources": sources, "estimations_performed": {}})
    _write(work / release / "manifests" / "correction_run_manifest.json",
           {"run_id": run_id, "code_commit_sha": PIN, "code_tree_dirty": False})
    _write(work / release / "manifests" / "correction_summary.json",
           {"run_id": run_id, "chain_sources": sources})
    (work / release / f"MARKER_{run_id}.txt").write_text(run_id)


@pytest.fixture
def work(tmp_path):
    work = tmp_path / "r1work"
    _write(work / "replay_report" / "replay_report.json",
           {"tier_a_ar_chains_to_estimate": TIER_A})
    _release(work, "r1_corrected", "r1_release", "correction-STEP6", [])
    _release(work, "r1_tier_a", "r1_tier_a_release", "correction-TIERA", TIER_A)
    legacy = work / "r1_tier_a_legacy" / "r1_comparison.csv"
    legacy.parent.mkdir(parents=True)
    with open(legacy, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "status"])
        writer.writeheader()
        writer.writerow({"path": "robustness/T4.2_cpi_lag_robustness.csv",
                         "status": "equal_within_fp_tolerance"})
    _write(work / "tier_a_validation" / "ar_refit_validation.json", {"ok": True})
    return work


@pytest.fixture
def git(monkeypatch):
    calls = []

    def fake_run(command, *args, **kwargs):
        calls.append(list(command))
        return SimpleNamespace(returncode=0, stdout="feedbeef\n", stderr="")
    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


def _session(tmp_path, work, *, run_tier_a=True, confirm=None, stale=True):
    """The variables a Colab session holds when step 8 runs (as the older notebook left them)."""
    project = tmp_path / "repo" / "my-thesis"
    project.mkdir(parents=True, exist_ok=True)
    namespace = {"WORK_DIR": work, "EVIDENCE": tmp_path / "evidence", "REPO": tmp_path / "repo",
                 "PROJECT": project, "PIN_COMMIT": PIN, "COMMIT": PIN, "STAMP": "20261103T120000Z",
                 "GIT_ENV": {}, "GITHUB_TOKEN": "token-not-used", "RUN_TIER_A": run_tier_a,
                 "PUSH_EVIDENCE": True, "EVIDENCE_BRANCH_PREFIX": "part8-r1-replay",
                 "RELEASE_BRANCH_PREFIX": "part8-corrected-results"}
    if stale:
        # what step 6 of the older notebook left behind: these must be ignored
        namespace["RELEASE"] = work / "r1_release"
        namespace["corrected"] = {"run_id": "correction-STEP6"}
    if confirm is not None:
        namespace["CONFIRM_PUBLISH"] = confirm
    return namespace


def _run(source, namespace):
    exec(compile(source, "step8", "exec"), namespace)
    return namespace


# -- the regenerated notebook --------------------------------------------------------

def test_tier_a_dry_run_selects_the_tier_a_release_and_ignores_stale_step6(tmp_path, work, git):
    ns = _run(_step8_cell(), _session(tmp_path, work))          # CONFIRM_PUBLISH absent
    plan = ns["PLAN"]
    assert plan["label"] == "tier-a" and plan["run_id"] == "correction-TIERA"
    assert plan["re_estimated"] == TIER_A and len(plan["re_estimated"]) == 8
    assert Path(plan["release"]).name == "r1_tier_a_release"
    assert git == []                                            # dry run: nothing pushed
    written = json.loads((tmp_path / "evidence" / "publication_plan.json").read_text())
    assert written["run_id"] == "correction-TIERA"
    copied = json.loads((tmp_path / "evidence" / "published_release_manifests"
                         / "correction_run_manifest.json").read_text())
    assert copied["run_id"] == "correction-TIERA"


def test_confirmed_tier_a_publication_pushes_the_tier_a_release_only(tmp_path, work, git):
    ns = _run(_step8_cell(), _session(tmp_path, work, confirm=True))
    released = ns["PROJECT"] / "output_corrected"
    assert (released / "MARKER_correction-TIERA.txt").exists()
    assert not (released / "MARKER_correction-STEP6.txt").exists()
    commits = [c[c.index("-m") + 1] for c in git if "commit" in c]
    assert len(commits) == 2
    assert all("correction-STEP6" not in m for m in commits)
    assert "correction-TIERA" in commits[1] and "no estimation" not in " ".join(commits)
    assert all(task in commits[1] for task in TIER_A)
    branches = [c[c.index("-B") + 1] for c in git if "-B" in c]
    assert branches[1] == "part8-corrected-results/r1-tier-a-20261103T120000Z"
    pushes = [c for c in git if c[:2] == ["git", "push"]]
    assert all("--force" not in c and "-f" not in c for c in pushes)


@pytest.mark.parametrize("damage", [
    "missing_release", "missing_summary", "validation_failed", "legacy_failed",
    "missing_validation", "seven_reestimated", "manifest_run_id", "dirty_release",
    "other_commit"])
def test_tier_a_publication_fails_safely(tmp_path, work, git, damage):
    if damage == "missing_release":
        (work / "r1_tier_a_release" / "manifests" / "correction_run_manifest.json").unlink()
    elif damage == "missing_summary":
        (work / "r1_tier_a" / "r1_summary.json").unlink()
    elif damage == "validation_failed":
        _write(work / "tier_a_validation" / "ar_refit_validation.json", {"ok": False})
    elif damage == "missing_validation":
        (work / "tier_a_validation" / "ar_refit_validation.json").unlink()
    elif damage == "legacy_failed":
        (work / "r1_tier_a_legacy" / "r1_comparison.csv").write_text("path,status\nx.csv,changed\n")
    elif damage == "seven_reestimated":
        _release(work, "r1_tier_a", "r1_tier_a_release", "correction-TIERA", TIER_A[:7])
    elif damage == "manifest_run_id":
        _write(work / "r1_tier_a_release" / "manifests" / "correction_run_manifest.json",
               {"run_id": "correction-STEP6", "code_commit_sha": PIN, "code_tree_dirty": False})
    elif damage == "dirty_release":
        _write(work / "r1_tier_a_release" / "manifests" / "correction_run_manifest.json",
               {"run_id": "correction-TIERA", "code_commit_sha": PIN, "code_tree_dirty": True})
    elif damage == "other_commit":
        _write(work / "r1_tier_a_release" / "manifests" / "correction_run_manifest.json",
               {"run_id": "correction-TIERA", "code_commit_sha": "0" * 40,
                "code_tree_dirty": False})
    with pytest.raises(RuntimeError):
        _run(_step8_cell(), _session(tmp_path, work, confirm=True))
    assert git == []                                            # nothing pushed
    assert not (tmp_path / "repo" / "my-thesis" / "output_corrected").exists()


def test_without_tier_a_the_step6_release_is_selected(tmp_path, work, git):
    for name in ("r1_tier_a", "r1_tier_a_release", "r1_tier_a_legacy", "tier_a_validation"):
        import shutil
        shutil.rmtree(work / name)
    ns = _run(_step8_cell(), _session(tmp_path, work, run_tier_a=False, stale=False))
    assert ns["PLAN"]["label"] == "replay" and ns["PLAN"]["run_id"] == "correction-STEP6"
    assert ns["PLAN"]["re_estimated"] == []


def test_tier_a_outputs_with_run_tier_a_false_are_refused(tmp_path, work, git):
    with pytest.raises(RuntimeError, match="refusing to guess"):
        _run(_step8_cell(), _session(tmp_path, work, run_tier_a=False))


# -- an already-open session (older notebook in memory) --------------------------------

def test_paste_file_is_the_notebook_cell_and_works_in_an_open_session(tmp_path, work, git):
    paste = PASTE.read_text()
    assert paste.endswith(_step8_cell() + "\n")
    ns = _run(paste, _session(tmp_path, work))           # stale RELEASE/corrected present
    assert ns["PLAN"]["run_id"] == "correction-TIERA" and git == []


def test_step8_never_reads_step6_variables():
    import ast
    cell = _step8_cell()
    names = {node.id for node in ast.walk(ast.parse(cell)) if isinstance(node, ast.Name)}
    for stale in ("RELEASE", "corrected", "CORRECTED", "LEGACY", "REPLAY", "TASKS"):
        assert stale not in names, f"step 8 reads the earlier cells' variable {stale}"
    assert 'globals().get("CONFIRM_PUBLISH", False)' in cell
