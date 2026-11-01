"""The Colab notebook must run with Run all, unedited, and keep its promises.

It is executed end to end outside Colab by the validation recorded in the scheduling
report; these tests pin the properties that must never regress.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess

from thesis.core.paths import PROJECT_ROOT

NOTEBOOK = PROJECT_ROOT / "colab" / "run_thesis_colab.ipynb"


def _cells() -> list[dict]:
    return json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]


def _code() -> list[str]:
    return ["".join(c["source"]) for c in _cells() if c["cell_type"] == "code"]


def test_the_notebook_is_valid_and_every_cell_is_plain_python():
    for source in _code():
        ast.parse(source)                        # no IPython magics or shell escapes
        assert not re.search(r"^\s*[!%]", source, re.M)


def test_defaults_run_the_full_baseline_with_four_workers():
    settings = _code()[0]
    assert re.search(r"^WORKERS = 4\b", settings, re.M)
    assert re.search(r"^SMOKE_TEST = False\b", settings, re.M)
    assert re.search(r"^RESTORE_CACHE = True\b", settings, re.M)
    assert re.search(r'^SOURCE_URL = ""', settings, re.M)


def test_the_default_branch_is_the_one_holding_this_notebook():
    settings = _code()[0]
    branch = re.search(r'^BRANCH = "([^"]+)"', settings, re.M).group(1)
    current = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=PROJECT_ROOT,
                             capture_output=True, text=True).stdout.strip()
    assert branch == current or current == "HEAD"


def test_it_runs_the_approved_entry_point_with_workers_and_log_mirror():
    code = "\n".join(_code())
    assert '"code/run_all.py", "--workers", str(WORKERS)' in code
    assert '"--log-mirror"' in code and '"-u"' in code
    assert '"--data-only"' in code


def test_python_311_environment_from_the_lock():
    code = "\n".join(_code())
    assert "requirements.lock.txt" in code and "create_environment" in code
    assert "verify_environment" in code


def test_backups_restore_and_verification_are_wired():
    code = "\n".join(_code())
    for needle in ("IncrementalArchive(CACHE_DIR, DRIVE_CACHE).restore()", "backup-daemon",
                   "cache_identity", "verify_outputs", "push_results"):
        assert needle in code, needle


def test_the_token_comes_only_from_secrets_and_never_reaches_a_url():
    code = "\n".join(_code())
    assert 'userdata.get("GITHUB_TOKEN")' in code
    assert not re.search(r"(ghp_|github_pat_)[A-Za-z0-9]", code)
    assert "https://{" not in code and "@github.com" not in code
    assert 'RUN_ENV.pop("THESIS_GIT_TOKEN", None)' in code


def test_files_it_writes_stay_outside_the_clone():
    code = "\n".join(_code())
    assert 'WORK = "/content/work"' in code
    assert 'REPO = WORK_DIR / "academia7"' in code
    assert 'RUN_DIR = WORK_DIR / "run"' in code and 'VENV = WORK_DIR / "venv311"' in code


def test_correction_release_defaults_are_safe():
    """Part 8 correction phase: the known Drive root, a preflight that stops before the
    run, a completeness gate, and a results prefix that cannot reach `part8-results/`."""
    settings = _code()[0]
    assert re.search(r'^DRIVE_ROOT = "/content/drive/MyDrive/KillyPhD/Part8_K3_InSample_2026-10-29"',
                     settings, re.M)
    assert re.search(r"^PREFLIGHT_ONLY = True\b", settings, re.M)
    assert re.search(r"^ALLOW_PARTIAL_CACHE = False\b", settings, re.M)
    assert re.search(r'^RESULTS_BRANCH_PREFIX = "part8-corrected-results"', settings, re.M)
    code = "\n".join(_code())
    assert "tools/cache_completeness.py" in code and "PREFLIGHT_ONLY" in code
    assert "--pair-by-name" in code and "recover_local_cache" in code
    assert ".strip('\"')" in code and "tc.clean_drive_root(DRIVE_ROOT)" in code
    # the gate comes before the run is launched
    joined = "\n".join(_code())
    assert joined.index("raise SystemExit(\"PREFLIGHT_ONLY") < joined.index("launch_background(command")
