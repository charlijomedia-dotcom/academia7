"""The Colab notebook must be valid and must not block the run it launches.

The clean-tree safeguard refuses a baseline run beside any untracked file in the
repository, so every file the notebook itself writes must live outside the clone.
"""

from __future__ import annotations

import json

from thesis.core.paths import PROJECT_ROOT

NOTEBOOK = PROJECT_ROOT / "colab" / "run_thesis_colab.ipynb"


def _code() -> str:
    cells = json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]
    return "\n".join("".join(c["source"]) for c in cells if c["cell_type"] == "code")


def test_the_notebook_is_valid_json_with_cells():
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4 and len(notebook["cells"]) > 5


def test_it_runs_the_approved_entry_point_with_the_log_mirror():
    code = _code()
    assert "code/run_all.py" in code
    assert "--log-mirror" in code
    assert "python -u" in code


def test_files_it_writes_are_outside_the_clone():
    code = _code()
    for name in ("colab_console.log", "colab_run.pid"):
        for line in code.splitlines():
            if name in line:
                assert f"/content/{name}" in line, line


def test_it_installs_the_locked_dependencies():
    assert "requirements.lock.txt" in _code()
