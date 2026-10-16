"""The D14 clean-tree safeguard must permit reruns without weakening.

Decision D14 protects one claim: that a baseline result can be reproduced from the commit
recorded beside it. That claim rests on the run's *inputs* — code, configuration, frozen
data, approved specifications. It does not rest on the run's own artifacts, which are the
result, and which land inside the repository because Part 5 requires every thesis-facing
number to be traceable to a file under `output/`.

Treating those artifacts as a dirty tree made the baseline run a one-shot: the first run
wrote `output/`, and every later run refused. These tests pin both halves of the corrected
behaviour — reruns are allowed, and anything that could change the result still stops the
run.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from thesis.core.paths import Namespace
from thesis.core.provenance import (DirtyTreeError, RunContext, git_dirty_paths,
                                    git_tree_dirty)


def _run(*args: str, cwd: Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                          check=True).stdout


@pytest.fixture
def repository(tmp_path, monkeypatch):
    """A throwaway git repository shaped like the project."""
    root = tmp_path / "repo"
    (root / "code" / "src").mkdir(parents=True)
    (root / "output" / "diagnostics").mkdir(parents=True)
    (root / "specs").mkdir()
    _run("init", "-q", cwd=root)
    _run("config", "user.email", "t@example.com", cwd=root)
    _run("config", "user.name", "T", cwd=root)
    (root / "code" / "src" / "module.py").write_text("x = 1\n")
    (root / "specs" / "method.md").write_text("approved\n")
    (root / "output" / ".gitkeep").write_text("")
    _run("add", "-A", cwd=root)
    _run("commit", "-q", "-m", "initial", cwd=root)

    import thesis.core.provenance as provenance
    monkeypatch.setattr(provenance, "PROJECT_ROOT", root)
    return root


def _context(root: Path) -> RunContext:
    return RunContext(namespace=Namespace.BASELINE, config_hash="abc")


class TestParsingTheStatus:
    def test_a_clean_tree_reports_no_paths(self, repository):
        assert git_dirty_paths() == ()
        assert git_tree_dirty() is False

    def test_the_first_path_is_not_truncated(self, repository):
        # The porcelain status field is two fixed-width characters then a space, and the
        # first is often a space. Stripping the output shifts the first path by one.
        (repository / "code" / "src" / "module.py").write_text("x = 2\n")
        paths = git_dirty_paths()
        assert paths == ("code/src/module.py",), paths

    def test_several_changes_are_all_reported_intact(self, repository):
        (repository / "code" / "src" / "module.py").write_text("x = 2\n")
        (repository / "specs" / "method.md").write_text("changed\n")
        assert set(git_dirty_paths()) == {"code/src/module.py", "specs/method.md"}

    def test_an_untracked_directory_is_reported_as_a_directory(self, repository):
        (repository / "output" / "diagnostics" / "T2.2.csv").write_text("a,b\n1,2\n")
        assert git_dirty_paths() == ("output/diagnostics/",)

    def test_a_rename_reports_its_destination(self, repository):
        _run("mv", "specs/method.md", "specs/renamed.md", cwd=repository)
        assert "specs/renamed.md" in git_dirty_paths()


class TestRerunsAreAllowed:
    def test_the_runs_own_outputs_do_not_block_it(self, repository):
        (repository / "output" / "diagnostics" / "T2.2.csv").write_text("a,b\n1,2\n")
        assert git_tree_dirty() is True, "the tree is dirty in the plain sense"
        _context(repository).require_clean_tree(
            produced_by_the_run=(repository / "output",))

    def test_a_second_run_is_permitted_after_a_first_wrote_everything(self, repository):
        for name in ("T2.2.csv", "T3.1.csv", "T4.7.csv"):
            (repository / "output" / "diagnostics" / name).write_text("x\n1\n")
        (repository / "output" / "manifest.json").write_text("{}\n")
        context = _context(repository)
        context.require_clean_tree(produced_by_the_run=(repository / "output",))
        context.require_clean_tree(produced_by_the_run=(repository / "output",))

    def test_the_cache_directory_is_also_the_runs_own(self, repository):
        (repository / "cache").mkdir()
        (repository / "cache" / "fit.json").write_text("{}\n")
        _context(repository).require_clean_tree(
            produced_by_the_run=(repository / "output", repository / "cache"))


class TestTheSafeguardStillBites:
    def test_a_source_change_stops_a_baseline_run(self, repository):
        (repository / "code" / "src" / "module.py").write_text("x = 2\n")
        with pytest.raises(DirtyTreeError, match="code/src/module.py"):
            _context(repository).require_clean_tree(
                produced_by_the_run=(repository / "output",))

    def test_a_specification_change_stops_a_baseline_run(self, repository):
        (repository / "specs" / "method.md").write_text("tampered\n")
        with pytest.raises(DirtyTreeError, match="specs/method.md"):
            _context(repository).require_clean_tree(
                produced_by_the_run=(repository / "output",))

    def test_a_source_change_stops_it_even_alongside_legitimate_outputs(self, repository):
        (repository / "output" / "diagnostics" / "T2.2.csv").write_text("a\n1\n")
        (repository / "code" / "src" / "module.py").write_text("x = 2\n")
        with pytest.raises(DirtyTreeError) as raised:
            _context(repository).require_clean_tree(
                produced_by_the_run=(repository / "output",))
        assert "code/src/module.py" in str(raised.value)
        assert "output/" not in str(raised.value)

    def test_a_new_untracked_source_file_stops_it(self, repository):
        (repository / "code" / "src" / "extra.py").write_text("y = 1\n")
        with pytest.raises(DirtyTreeError):
            _context(repository).require_clean_tree(
                produced_by_the_run=(repository / "output",))

    def test_the_error_names_the_offending_paths(self, repository):
        (repository / "code" / "src" / "module.py").write_text("x = 2\n")
        (repository / "specs" / "method.md").write_text("tampered\n")
        with pytest.raises(DirtyTreeError) as raised:
            _context(repository).require_clean_tree(
                produced_by_the_run=(repository / "output",))
        message = str(raised.value)
        assert "code/src/module.py" in message and "specs/method.md" in message

    def test_a_directory_outside_the_run_is_not_matched_by_prefix(self, repository):
        # "output_tampered/" must not be excluded by the "output" root.
        (repository / "output_tampered").mkdir()
        (repository / "output_tampered" / "x.csv").write_text("a\n")
        with pytest.raises(DirtyTreeError, match="output_tampered"):
            _context(repository).require_clean_tree(
                produced_by_the_run=(repository / "output",))

    def test_a_non_baseline_namespace_is_unaffected(self, repository):
        (repository / "code" / "src" / "module.py").write_text("x = 2\n")
        RunContext(namespace=Namespace.SMOKE, config_hash="abc").require_clean_tree()

    def test_an_unanswerable_git_is_treated_as_unsafe(self, monkeypatch):
        import thesis.core.provenance as provenance

        monkeypatch.setattr(provenance, "_git", lambda *a, **k: None)
        with pytest.raises(DirtyTreeError, match="could not report"):
            RunContext(namespace=Namespace.BASELINE,
                       config_hash="abc").require_clean_tree()
