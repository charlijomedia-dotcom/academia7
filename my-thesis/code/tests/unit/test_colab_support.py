"""The Colab support module: environment check, credential handling, incremental
backups and restore, run control, output verification and publication.

Everything the notebook relies on is exercised here, outside Colab, with temporary
directories standing in for Google Drive and a local bare repository for GitHub.
"""

from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import sys
import tarfile
import threading
import time
from pathlib import Path

import pytest

from thesis.core.paths import CODE_ROOT, PROJECT_ROOT

SPEC = importlib.util.spec_from_file_location("thesis_colab",
                                              PROJECT_ROOT / "colab" / "thesis_colab.py")
colab = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(colab)


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, check=True, text=True,
                          capture_output=True).stdout


class TestEnvironment:
    def test_the_lock_has_its_pins(self):
        pins = colab.lock_pins(CODE_ROOT / "requirements.lock.txt")
        assert pins["numpy"] == "2.4.6" and pins["statsmodels"] == "0.15.0"
        assert pins["pyyaml"] == "6.0.1"
        assert len(pins) == 13

    def test_this_interpreter_matches_the_lock(self):
        found = colab.verify_environment(Path(sys.executable),
                                         CODE_ROOT / "requirements.lock.txt")
        assert found["python"].startswith("3.11.")

    def test_a_version_mismatch_is_refused(self, tmp_path):
        lock = tmp_path / "lock.txt"
        lock.write_text("numpy==0.0.1\n")
        with pytest.raises(RuntimeError, match="numpy: installed"):
            colab.verify_environment(Path(sys.executable), lock)

    def test_a_wrong_python_version_is_refused(self):
        with pytest.raises(RuntimeError, match="is not 3.10"):
            colab.verify_environment(Path(sys.executable),
                                     CODE_ROOT / "requirements.lock.txt",
                                     python_version="3.10")


class TestCredentials:
    def test_askpass_reads_the_token_from_the_environment_only(self, tmp_path):
        env = colab.askpass_environment("ghp_secret123", tmp_path)
        script = Path(env["GIT_ASKPASS"])
        assert "ghp_secret123" not in script.read_text()
        assert not script.is_relative_to(PROJECT_ROOT)
        answer = subprocess.run([str(script), "Password for 'https://github.com':"],
                                env=env, text=True, capture_output=True).stdout.strip()
        assert answer == "ghp_secret123"
        user = subprocess.run([str(script), "Username for 'https://github.com':"],
                              env=env, text=True, capture_output=True).stdout.strip()
        assert user == "x-access-token"

    def test_no_token_means_no_askpass(self, tmp_path):
        env = colab.askpass_environment(None, tmp_path)
        assert env.get("GIT_ASKPASS") == os.environ.get("GIT_ASKPASS")   # untouched
        assert "THESIS_GIT_TOKEN" not in env and env["GIT_TERMINAL_PROMPT"] == "0"

    @pytest.mark.parametrize("url", ["https://token@github.com/o/r.git",
                                     "https://x:y@github.com/o/r.git"])
    def test_urls_with_credentials_are_refused(self, url):
        with pytest.raises(ValueError):
            colab.assert_no_credentials(url)

    def test_a_plain_url_is_accepted(self):
        colab.assert_no_credentials("https://github.com/o/r.git")


class TestIncrementalArchive:
    def _tree(self, root: Path, n: int) -> None:
        for i in range(n):
            path = root / f"{i % 3:02x}" / f"fit{i}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"i": i}))

    def test_only_new_files_go_into_each_part(self, tmp_path):
        source, drive = tmp_path / "cache", tmp_path / "drive"
        self._tree(source, 30)
        archive = colab.IncrementalArchive(source, drive)
        first = archive.sync()
        assert first is not None and len(tarfile.open(first).getnames()) == 30
        assert archive.sync() is None                         # nothing new: no upload
        (source / "00" / "new.json").write_text("{}")
        second = archive.sync()
        assert tarfile.open(second).getnames() == ["00/new.json"]
        assert sorted(p.name for p in drive.iterdir()) == [
            "part-00001.json", "part-00001.tar.gz", "part-00002.json", "part-00002.tar.gz"]

    def test_files_being_written_are_skipped(self, tmp_path):
        source = tmp_path / "cache"
        self._tree(source, 2)
        (source / "00" / "partial.json.tmp").write_text("{")
        archive = colab.IncrementalArchive(source, tmp_path / "drive")
        names = tarfile.open(archive.sync()).getnames()
        assert not any(n.endswith(".tmp") for n in names)

    def test_restore_reproduces_the_tree_on_a_new_machine(self, tmp_path):
        source, drive, fresh = tmp_path / "cache", tmp_path / "drive", tmp_path / "vm2"
        self._tree(source, 12)
        archive = colab.IncrementalArchive(source, drive)
        archive.sync()
        (source / "01" / "late.json").write_text('{"late": 1}')
        archive.sync()
        restored = colab.IncrementalArchive(fresh, drive)    # a new VM reads the lists
        assert restored.restore() == 13
        for path in source.rglob("*.json"):
            relative = path.relative_to(source)
            assert (fresh / relative).read_text() == path.read_text()
        assert restored.sync() is None                        # nothing is re-uploaded

    def test_a_changed_file_is_backed_up_again(self, tmp_path):
        source = tmp_path / "out"
        self._tree(source, 2)
        archive = colab.IncrementalArchive(source, tmp_path / "drive")
        archive.sync()
        target = source / "00" / "fit0.json"
        target.write_text('{"i": "rewritten", "pad": "' + "x" * 50 + '"}')
        assert tarfile.open(archive.sync()).getnames() == ["00/fit0.json"]

    def test_an_unsafe_archive_member_is_refused(self, tmp_path):
        drive = tmp_path / "drive"
        drive.mkdir()
        evil = tmp_path / "evil.txt"
        evil.write_text("x")
        with tarfile.open(drive / "part-00001.tar.gz", "w:gz") as archive:
            archive.add(evil, arcname="../escape.txt")
        with pytest.raises(ValueError, match="unsafe"):
            colab.IncrementalArchive(tmp_path / "cache", drive).restore()
        assert not (tmp_path / "escape.txt").exists()

    def test_the_daemon_keeps_backing_up_until_the_run_exits(self, tmp_path):
        source, drive = tmp_path / "cache", tmp_path / "drive"
        source.mkdir()
        runner = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(3)"])

        def write_while_running():
            for i in range(5):
                (source / f"f{i}.json").write_text(str(i))
                time.sleep(0.4)

        writer = threading.Thread(target=write_while_running)
        writer.start()
        colab.backup_daemon(runner.pid, [(source, drive)], interval=0.5,
                            log=tmp_path / "backup.log")
        writer.join()
        runner.wait()
        restored = colab.IncrementalArchive(tmp_path / "vm2", drive)
        assert restored.restore() == 5
        assert len(list(drive.glob("part-*.tar.gz"))) >= 2     # more than one sync
        assert "final sync complete" in (tmp_path / "backup.log").read_text()


class TestRunControl:
    def test_launch_watch_and_exit_status(self, tmp_path):
        console, exit_file, pid_file = (tmp_path / "console.log", tmp_path / "exit",
                                        tmp_path / "pid")
        program = ("import time, sys\n"
                   "for i in range(3): print('line', i, flush=True); time.sleep(0.3)\n"
                   "sys.exit(3)\n")
        pid = colab.launch_background([sys.executable, "-c", program], cwd=tmp_path,
                                      console=console, exit_file=exit_file,
                                      pid_file=pid_file)
        again = colab.launch_background([sys.executable, "-c", "pass"], cwd=tmp_path,
                                        console=console, exit_file=exit_file,
                                        pid_file=pid_file)
        assert again == pid                               # no second copy while running
        out = io.StringIO()
        status = colab.watch(console, pid_file, exit_file, poll=0.1, out=out)
        assert status == 3
        assert "line 0" in out.getvalue() and "line 2" in out.getvalue()

    def test_a_finished_zombie_is_not_alive(self):
        process = subprocess.Popen([sys.executable, "-c", "pass"])
        time.sleep(0.5)                                    # exited, not yet reaped
        assert not colab.process_alive(process.pid)
        process.wait()


@pytest.fixture
def finished_project(tmp_path):
    """A repository holding a completed run's outputs, inventory and snapshot."""
    repo = tmp_path / "repo"
    project = repo / "my-thesis"
    (project / "code").mkdir(parents=True)
    (project / "code" / "model.py").write_text("x = 1\n")
    (project / ".gitignore").write_text("run_logs/\n")
    git("init", "-q", cwd=repo)
    git("add", "-A", cwd=repo)
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "code", cwd=repo)
    output = project / "output"
    (output / "manifests").mkdir(parents=True)
    (output / "tables").mkdir()
    table = output / "tables" / "T1.csv"
    table.write_text("a,b\n1,2\n")
    (output / "manifests" / "output_inventory.csv").write_text(
        f"stage,path,bytes,sha256\nx,tables/T1.csv,{table.stat().st_size},"
        f"{colab.sha256(table)}\n")
    (output / "manifests" / "run_summary.json").write_text(
        json.dumps({"stages": colab.STAGES, "run_id": "baseline-x"}))
    logs = project / "run_logs" / "baseline" / "baseline-x"
    logs.mkdir(parents=True)
    (logs / "progress.json").write_text(json.dumps({"status": "complete"}))
    (project / "run_logs" / "baseline" / "LATEST").write_text("baseline-x\n")
    return repo, project


class TestVerificationAndPublication:
    def test_a_complete_run_verifies(self, finished_project):
        _, project = finished_project
        report = colab.verify_outputs(project)
        assert report["ok"], report["problems"]
        assert report["files_checked"] == 1 and report["run_id"] == "baseline-x"

    def test_a_changed_output_fails_verification(self, finished_project):
        _, project = finished_project
        (project / "output" / "tables" / "T1.csv").write_text("a,b\n1,3\n")
        assert "checksum differs: tables/T1.csv" in colab.verify_outputs(project)["problems"]

    def test_a_code_change_fails_verification(self, finished_project):
        _, project = finished_project
        (project / "code" / "model.py").write_text("x = 2\n")
        problems = colab.verify_outputs(project)["problems"]
        assert any("outside the outputs" in p for p in problems)

    def test_an_incomplete_run_fails_verification(self, finished_project):
        _, project = finished_project
        (project / "run_logs" / "baseline" / "baseline-x" / "progress.json").write_text(
            json.dumps({"status": "failed"}))
        assert "progress snapshot does not say complete" in \
            colab.verify_outputs(project)["problems"]

    def test_results_are_pushed_to_their_own_branch(self, finished_project, tmp_path):
        repo, project = finished_project
        remote = tmp_path / "remote.git"
        git("init", "-q", "--bare", str(remote), cwd=tmp_path)
        git("remote", "add", "origin", str(remote), cwd=repo)
        env = colab.askpass_environment("tok", tmp_path / "secrets")
        sha = colab.push_results(repo, project, "results/baseline-x", env,
                                 message="results", author=("Run", "run@example.invalid"))
        assert git("rev-parse", "results/baseline-x", cwd=remote).strip() == sha
        files = git("show", "--name-only", "--format=", sha, cwd=repo).split()
        assert files and all(f.startswith("my-thesis/output/") for f in files)
        assert "tok" not in (repo / ".git" / "config").read_text()

    def test_oversized_files_are_not_pushed(self, finished_project, tmp_path, monkeypatch):
        repo, project = finished_project
        git("remote", "add", "origin", str(tmp_path / "nowhere.git"), cwd=repo)
        monkeypatch.setattr(colab, "GITHUB_FILE_LIMIT", 3)
        with pytest.raises(RuntimeError, match="size limit"):
            colab.push_results(repo, project, "results/x", {}, message="m",
                               author=("a", "a@b"))

    def test_a_credentialed_remote_is_refused(self, finished_project):
        repo, project = finished_project
        git("remote", "add", "origin", "https://tok@github.com/o/r.git", cwd=repo)
        with pytest.raises(ValueError, match="credentials"):
            colab.push_results(repo, project, "results/x", {}, message="m",
                               author=("a", "a@b"))


def test_cache_identity_is_stable_and_depends_on_the_namespace():
    first = colab.cache_identity(Path(sys.executable), CODE_ROOT)
    assert len(first) == 16 and first == colab.cache_identity(Path(sys.executable), CODE_ROOT)
    assert colab.cache_identity(Path(sys.executable), CODE_ROOT, "smoke") != first


class TestCacheRecoveryAndAudit:
    """Part 8 correction phase: restored fits are not re-uploaded, parts are bounded,
    recovery never touches existing parts and is verified, Drive paths are cleaned."""

    def _cache(self, root, n=7):
        for i in range(n):
            path = root / f"{i:02d}" / f"{i:064d}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"i": i}))
        return root

    def test_restored_fits_are_not_reuploaded_by_name(self, tmp_path):
        source = self._cache(tmp_path / "vm1")
        drive = tmp_path / "drive"
        colab.IncrementalArchive(source, drive).sync()
        fresh = tmp_path / "vm2"
        colab.IncrementalArchive(fresh, drive).restore()
        # tar (PAX) keeps mtime as a float (~1e-7 s): a restored file's st_mtime_ns is
        # within a few hundred ns of the one listed at backup time, and about 1 time in
        # 300 per file it is identical, which made this assertion fail intermittently.
        # Move each restored mtime by 1 ms, far beyond that error, so "restored files
        # look changed to the signature rule" holds deterministically:
        for path in fresh.rglob("*.json"):
            info = path.stat()
            os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns + 1_000_000))
        # the signature rule (outputs) sees every restored file as changed ...
        assert len(colab.IncrementalArchive(fresh, drive).pending()) == 7
        # ... the by-name rule (content-addressed cache) sees none
        assert colab.IncrementalArchive(fresh, drive, by_name=True).pending() == {}

    def test_parts_are_bounded_and_each_is_logged(self, tmp_path):
        source = self._cache(tmp_path / "vm", n=5)
        notes = []
        archive = colab.IncrementalArchive(source, tmp_path / "drive", by_name=True,
                                           max_files_per_part=2)
        archive.sync(note=notes.append)
        assert len(archive._parts()) == 3 and len(notes) == 3

    def test_recovery_writes_a_new_folder_and_verifies(self, tmp_path):
        drive = tmp_path / "drive"
        identity = "abc"
        early = self._cache(tmp_path / "early", n=3)
        colab.IncrementalArchive(early, drive / "fit_cache" / identity).sync()
        before = sorted((drive / "fit_cache" / identity).iterdir())
        stamps = {p: p.stat().st_mtime_ns for p in before}
        vm = self._cache(tmp_path / "vm", n=6)            # 3 already archived + 3 new
        summary = colab.recover_local_cache(vm, drive, identity, stamp="T1")
        assert summary["already_archived"] == 3 and summary["newly_archived"] == 3
        assert summary["verified"] == 3 and summary["mismatched"] == []
        assert sorted((drive / "fit_cache" / identity).iterdir()) == before
        assert all(p.stat().st_mtime_ns == stamps[p] for p in before)   # untouched
        folders = colab.archive_folders(drive, identity)
        assert folders[-1] == drive / "fit_cache_recovered" / "T1" / identity
        restored = tmp_path / "restored"
        total = sum(colab.IncrementalArchive(restored, folders[0]).restore(folder=f)
                    for f in folders)
        assert total == 6 and len(list(restored.rglob("*.json"))) == 6
        report = colab.audit_drive([tmp_path / "drive_root_missing"])
        assert report[str(tmp_path / "drive_root_missing")]["exists"] is False

    def test_audit_counts_unique_payloads_and_partial_leftovers(self, tmp_path):
        root = tmp_path / "root"
        base = root / "baseline"
        vm = self._cache(tmp_path / "vm", n=4)
        colab.IncrementalArchive(vm, base / "fit_cache" / "id1").sync()
        (base / "fit_cache" / "id1" / "part-00002.tar.gz.partial").write_text("x")
        (base / "backup.log").write_text("[14:39:00] backup: final sync complete\n")
        report = colab.audit_drive([root])[str(root)]
        assert report["unique_fit_payloads_by_identity"] == {"id1": 4}
        assert report["fit_cache"]["id1"]["partial_leftovers"] == ["part-00002.tar.gz.partial"]
        assert report["backup_log_tail"][-1].endswith("final sync complete")

    @pytest.mark.parametrize("raw", ['"/content/drive/MyDrive/KillyPhD/X"',
                                     " '/content/drive/MyDrive/KillyPhD/X/' ",
                                     "/content/drive/MyDrive/KillyPhD/X"])
    def test_drive_root_quotes_are_stripped(self, raw):
        assert colab.clean_drive_root(raw) == "/content/drive/MyDrive/KillyPhD/X"

    def test_relative_or_foreign_drive_roots_are_refused(self):
        with pytest.raises(ValueError):
            colab.clean_drive_root("MyDrive/thesis")
