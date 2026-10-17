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
    (root / ".gitignore").write_text(".venv/\nvenv/\nENV/\nenv/\n.env\n.env.*\ncache/\n")
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


class TestTheDocumentedSetupIsPermitted:
    """REPRODUCING.md tells the researcher to create `.venv` inside `my-thesis`.

    That directory is not an input to the analysis — its contents are fully determined by
    `code/requirements.lock.txt`, whose hash every run manifest records — but an untracked
    directory is still a dirty tree, so without an ignore rule the documented setup made
    the first baseline run refuse to start.
    """

    def _make_venv(self, root: Path) -> None:
        """A directory shaped like a virtual environment, without building a real one."""
        for relative in ("bin/python", "lib/python3.11/site-packages/numpy/__init__.py",
                         "pyvenv.cfg"):
            target = root / ".venv" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("x")

    def test_a_virtual_environment_does_not_block_a_baseline_run(self, repository):
        self._make_venv(repository)
        assert git_dirty_paths() == (), "an ignored venv must not appear as a change"
        _context(repository).require_clean_tree(
            produced_by_the_run=(repository / "output",))

    def test_it_does_not_block_one_alongside_the_runs_own_outputs(self, repository):
        self._make_venv(repository)
        (repository / "output" / "diagnostics" / "T2.2.csv").write_text("a\n1\n")
        _context(repository).require_clean_tree(
            produced_by_the_run=(repository / "output",))

    def test_alternative_environment_directory_names_are_also_ignored(self, repository):
        for name in ("venv", "env", "ENV"):
            (repository / name).mkdir()
            (repository / name / "pyvenv.cfg").write_text("x")
        assert git_dirty_paths() == ()

    def test_an_environment_file_holding_credentials_is_ignored(self, repository):
        # A FRED API key must never reach the repository (Part 5 Comp §2).
        (repository / ".env").write_text("FRED_API_KEY=secret\n")
        (repository / ".env.local").write_text("FRED_API_KEY=secret\n")
        assert git_dirty_paths() == ()

    def test_a_source_change_still_refuses_with_a_venv_present(self, repository):
        # The decisive pairing: the documented setup is permitted, and a genuine input
        # modification is still caught, in the same working tree.
        self._make_venv(repository)
        (repository / "code" / "src" / "module.py").write_text("x = 2\n")
        with pytest.raises(DirtyTreeError, match="code/src/module.py"):
            _context(repository).require_clean_tree(
                produced_by_the_run=(repository / "output",))

    def test_a_specification_change_still_refuses_with_a_venv_present(self, repository):
        self._make_venv(repository)
        (repository / "specs" / "method.md").write_text("tampered\n")
        with pytest.raises(DirtyTreeError, match="specs/method.md"):
            _context(repository).require_clean_tree(
                produced_by_the_run=(repository / "output",))

    def test_a_directory_merely_starting_with_venv_is_not_ignored(self, repository):
        # "venv_notes/" must not be swallowed by the "venv/" rule.
        (repository / "venv_notes").mkdir()
        (repository / "venv_notes" / "note.md").write_text("x\n")
        with pytest.raises(DirtyTreeError, match="venv_notes"):
            _context(repository).require_clean_tree(
                produced_by_the_run=(repository / "output",))


class TestTheProjectsOwnIgnoreRules:
    """The rules must hold in this repository, not only in a constructed one."""

    @staticmethod
    def _rules() -> list[str]:
        """The active rules, with comments and blank lines removed.

        The file explains itself in prose that names paths it deliberately does *not*
        ignore, so matching raw text would find those comments rather than real rules.
        """
        from thesis.core.paths import PROJECT_ROOT

        text = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
        return [line.strip() for line in text.splitlines()
                if line.strip() and not line.lstrip().startswith("#")]

    @classmethod
    def _project_gitignore(cls) -> str:
        return "\n".join(cls._rules())

    def test_the_documented_virtual_environment_path_is_ignored(self):
        assert ".venv/" in self._project_gitignore()

    def test_common_alternative_names_are_ignored(self):
        text = self._project_gitignore()
        for name in ("venv/", "ENV/", "env/"):
            assert name in text, name

    def test_environment_files_are_ignored(self):
        text = self._project_gitignore()
        assert ".env" in text and ".env.*" in text

    def test_nothing_that_determines_a_result_is_ignored(self):
        # The ignore list must not have grown to cover an input, or the thesis-facing
        # output directory whose traceability Part 5 requires.
        rules = self._rules()
        for forbidden in ("output/", "data/", "data/frozen/", "approved-specs/",
                          "code/", "code/src/", "code/configs/", "notes/", "reports/"):
            assert forbidden not in rules, f"{forbidden} must remain tracked"

    def test_the_rules_that_are_present_are_derived_or_local_only(self):
        # Every rule must name something regenerable, local, or explicitly non-baseline.
        allowed_prefixes = (
            "cache", "smoke_cache", "cache_refreshed", "smoke_output", "output_refreshed",
            "data/refreshed", "data/audit", "__pycache__", "*.py", ".pytest_cache",
            ".coverage", "htmlcov", "*.egg-info", ".venv", "venv", "ENV", "env", ".env",
        )
        for rule in self._rules():
            assert rule.startswith(allowed_prefixes), f"unexpected ignore rule: {rule}"
