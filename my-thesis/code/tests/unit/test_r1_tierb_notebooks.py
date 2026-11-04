"""The three Tier B batch notebooks: independent, disjoint, safe by default."""

from __future__ import annotations

import ast
import itertools
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
COLAB = ROOT / "colab"
sys.path.insert(0, str(COLAB))
import make_r1_tier_b_notebooks as gen  # noqa: E402
import r1_tierb as tb  # noqa: E402

FILES = {b: COLAB / n for b, n in gen.NOTEBOOKS.items()}


def _code(batch):
    return ["".join(c["source"]) for c in json.loads(FILES[batch].read_text())["cells"]
            if c["cell_type"] == "code"]


def _cell(batch, marker):
    return next(c for c in _code(batch) if marker in c)


def test_exactly_three_notebooks_matching_their_generator():
    assert sorted(p.name for p in COLAB.glob("r1_tier_b*.ipynb")) == sorted(gen.NOTEBOOKS.values())
    for batch, path in FILES.items():
        orch = re.search(r'^ORCH_COMMIT = "([^"]+)"', _code(batch)[0], re.M).group(1)
        assert json.loads(path.read_text()) == gen.build(batch, orch)
        assert orch == "__ORCH__" or re.fullmatch(r"[0-9a-f]{40}", orch)
        for source in _code(batch):
            ast.parse(source)
            assert not re.search(r"^\s*[!%]", source, re.M)


def test_defaults_are_safe_and_pinned():
    for batch in FILES:
        settings = _code(batch)[0]
        assert re.search(rf'^BATCH_ID = "{batch}"', settings, re.M)
        assert re.search(r"^RUN_TIER_B = False\b", settings, re.M)
        assert re.search(r"^RUN_AGGREGATION = False\b", settings, re.M)
        assert re.search(r"^CONFIRM_PUBLISH = False\b", settings, re.M)
        assert re.search(rf'^PIN_COMMIT = "{tb.SCIENTIFIC_PIN}"', settings, re.M)
        assert re.search(rf'^EXPECTED_IDENTITY = "{tb.CACHE_IDENTITY}"', settings, re.M)
        assert re.search(r"^RUNTIME_BUDGET_HOURS = 11\.0\b", settings, re.M)
        assert re.search(rf"^MAX_WORKERS = {tb.DEFAULT_WORKERS[batch]}\b", settings, re.M)
        assert re.search(rf'^WORK = "/content/r1tierb_{batch}"', settings, re.M)
        assert re.search(r"^RUN_DRIVE_CHECK = True\b", settings, re.M)
        assert re.search(r'^DRIVE_CHECK_VERIFY_ID = ""', settings, re.M)


def test_union_of_the_three_task_lists_is_exactly_the_nine_chains():
    tasks = [t for b in FILES for t in tb.batch_tasks(b)]
    assert len(tasks) == len(set(tasks)) == 9 and set(tasks) == set(tb.TIER_B_CHAINS)
    assert sum(tb.TIER_B_CHAINS[t][0] for t in tasks) == 6041
    assert tb.batch_tasks("B1") == ("T4.8:UNRATE|300:MSAR",)
    assert set(tb.batch_tasks("B2")) == {"T4.8:UNRATE|180:MSAR", "T4.1:FEDFUNDS|MSAR"}
    assert len(tb.batch_tasks("B3")) == 6


def _setup(batch, monkeypatch):
    import pathlib
    monkeypatch.setattr(pathlib.Path, "mkdir", lambda self, *a, **k: None)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    namespace: dict = {}
    for source in _code(batch)[:2]:                             # Settings, then Setup
        exec(compile(source.replace('"__ORCH__"', '"' + "a" * 40 + '"'), batch, "exec"),
             namespace)
    return namespace


@pytest.mark.parametrize("order", list(itertools.permutations(["B1", "B2", "B3"])))
def test_setup_runs_independently_in_any_order(order, monkeypatch):
    sessions = {}
    for batch in order:
        ns = _setup(batch, monkeypatch)                         # a fresh namespace each
        assert ns["BATCH_ID"] == batch and ns["SESSION"].startswith(batch + "-")
        assert ns["WORK_DIR"] == Path(f"/content/r1tierb_{batch}")
        sessions[batch] = ns["SESSION"]
    assert len(set(sessions.values())) == 3


def test_write_locations_are_disjoint():
    roots = {b: tb.batch_root("/content/drive/X", b) for b in FILES}
    assert len(set(roots.values())) == 3
    for batch in FILES:
        code = "\n".join(_code(batch))
        assert "tb.batch_root(DRIVE_ROOT, BATCH_ID)" in code
        checked = code.replace('BATCH_ID in ("B1", "B2", "B3")', "")   # the validity check
        for other in set(FILES) - {batch}:                     # no other batch named
            assert f'"{other}"' not in checked
        # the only other Drive namespace written is the optional aggregation's own folder
        assert "fit_cache" not in code.replace("tc.archive_folders", "")
    for module in ("r1_tierb_supervisor.py", "r1_tierb_worker.py"):
        text = (COLAB / module).read_text()
        assert "assert_writable_path" in text


def test_nothing_pushes_to_github():
    texts = [p.read_text() for p in COLAB.glob("r1_tierb*.py")]
    texts += ["\n".join(_code(b)) for b in FILES]
    for text in texts:
        assert '"push"' not in text and "'push'" not in text and "git push" not in text


class _Refuse:
    def __getattr__(self, name):
        def fail(*args, **kwargs):
            raise AssertionError(f"tc.{name} called with default settings")
        return fail


def test_default_run_all_estimates_nothing_and_launches_nothing(monkeypatch, tmp_path):
    def no_subprocess(*args, **kwargs):
        raise AssertionError(f"subprocess called with default settings: {args[0][:3]}")
    monkeypatch.setattr(subprocess, "run", no_subprocess)
    monkeypatch.setattr(subprocess, "Popen", no_subprocess)
    for batch in FILES:
        ns = {"RUN_TIER_B": False, "RUN_AGGREGATION": False, "WORK_DIR": tmp_path / batch,
              "REPORT": {"batch_chains": {t: {"complete": False} for t in tb.batch_tasks(batch)}},
              "tc": _Refuse(), "subprocess": subprocess}
        (tmp_path / batch).mkdir()
        for marker in ("SUPERVISOR_PID = ", "Re-run this cell to re-attach",
                       "Certify only what is committed", "Optional, from any one batch"):
            exec(compile(_cell(batch, marker), batch, "exec"), ns)


def test_run_toggle_launches_only_this_batch_supervisor(tmp_path):
    for batch in FILES:
        launched = []

        class FakeTC:
            def process_alive(self, pid):
                return False

            def launch_background(self, command, **kwargs):
                launched.append(command)
                return 1234
        import os
        import time
        ns = {"os": os, "time": time, "RUN_TIER_B": True, "WORK_DIR": tmp_path / batch,
              "tc": FakeTC(), "tb": tb,
              "REPORT": {"batch_chains": {t: {"complete": False} for t in tb.batch_tasks(batch)}},
              "PY": "py", "ORCH": COLAB, "BATCH_ID": batch, "CODE": "c", "ORIGINAL": "o",
              "DRIVE_ROOT": "/content/drive/X", "SESSION": f"{batch}-s",
              "RUNTIME_BUDGET_HOURS": 11.0, "RESERVE_MINUTES": 30, "BACKUP_MINUTES": 10,
              "MAX_WORKERS": 3, "PREFLIGHT": tmp_path / "p.json", "RUN_ENV": {}}
        (tmp_path / batch).mkdir()
        exec(compile(_cell(batch, "SUPERVISOR_PID = "), batch, "exec"), ns)
        assert len(launched) == 1
        command = launched[0]
        assert command[command.index("--batch") + 1] == batch


def test_scientific_code_and_methodology_unchanged_since_the_pin():
    paths = ["my-thesis/code/src", "my-thesis/code/tools", "my-thesis/approved-specs",
             "my-thesis/data", "my-thesis/output", "my-thesis/code/configs",
             "my-thesis/code/requirements.lock.txt"]
    try:
        result = subprocess.run(["git", "diff", "--quiet", tb.SCIENTIFIC_PIN, "--", *paths],
                                cwd=ROOT.parent, capture_output=True)
    except FileNotFoundError:
        pytest.skip("git not available")
    if result.returncode == 128:
        pytest.skip("pinned commit not in this clone")
    assert result.returncode == 0, "scientific code, data or specifications changed since the pin"


def test_drive_check_cell_writes_only_its_disposable_namespace(tmp_path):
    import r1_tierb_drive_check as dc
    for batch in FILES:
        drive = tmp_path / batch / "drive"
        original = drive / "baseline" / "fit_cache" / tb.CACHE_IDENTITY
        original.mkdir(parents=True)
        (original / "part-0001.tar.gz").write_bytes(b"original")

        class FakeTC:
            def archive_folders(self, base, identity):
                assert identity == tb.CACHE_IDENTITY
                return [base / "fit_cache" / identity]
        session = f"{batch}-20261104T000000Z-abc123"
        ns = {"RUN_DRIVE_CHECK": True, "DRIVE_CHECK_VERIFY_ID": "", "DRIVE_ROOT": str(drive),
              "SESSION": session, "IDENTITY": tb.CACHE_IDENTITY, "tc": FakeTC(), "Path": Path}
        exec(compile(_cell(batch, "import r1_tierb_drive_check as dc"), batch, "exec"), ns)
        assert ns["DRIVE_REPORT"]["ok"]
        written = {p for p in drive.rglob("*") if p.is_file()} - {original / "part-0001.tar.gz"}
        root = dc.check_root(drive, session)
        assert written and all(root in p.parents for p in written)
        # a later runtime confirms persistence
        ns2 = {**ns, "RUN_DRIVE_CHECK": False, "DRIVE_CHECK_VERIFY_ID": session}
        exec(compile(_cell(batch, "import r1_tierb_drive_check as dc"), batch, "exec"), ns2)
        assert "DRIVE_REPORT" not in ns2 or ns2["DRIVE_REPORT"] is ns["DRIVE_REPORT"]


def test_aggregation_cell_never_reports_approval():
    for batch in FILES:
        cell = _cell(batch, "Optional, from any one batch")
        assert "PASSED" not in cell and "AGGREGATION_STATUS" in cell
        assert "NOT a scientifically approved result" in cell
