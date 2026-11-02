"""The R1 real-cache replay notebook: safe defaults, no estimation, nothing overwritten."""

from __future__ import annotations

import ast
import importlib.util
import json
import re
from pathlib import Path

COLAB = Path(__file__).resolve().parents[3] / "colab"
NOTEBOOK = COLAB / "r1_cache_replay.ipynb"


def _cells():
    return json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]


def _code():
    return ["".join(c["source"]) for c in _cells() if c["cell_type"] == "code"]


def test_notebook_is_plain_python_and_matches_its_generator():
    for source in _code():
        ast.parse(source)
        assert not re.search(r"^\s*[!%]", source, re.M)
    spec = importlib.util.spec_from_file_location("make_nb", COLAB / "make_r1_replay_notebook.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pin = re.search(r'^PIN_COMMIT = "([^"]+)"', _code()[0], re.M).group(1)
    assert json.loads(NOTEBOOK.read_text()) == module.build(pin)


def test_defaults_estimate_nothing():
    settings = _code()[0]
    assert re.search(r"^RUN_TIER_A = False\b", settings, re.M)
    pin = re.search(r'^PIN_COMMIT = "([^"]+)"', settings, re.M).group(1)
    assert pin == "__PIN__" or re.fullmatch(r"[0-9a-f]{40}", pin)
    assert re.search(r'^EXPECTED_IDENTITY = "3413465b508bb844"', settings, re.M)


def test_only_the_gated_tier_a_cell_can_approve_estimation():
    for source in _code():
        if "--approve" in source and "assert \"--approve\" not in command" not in source:
            assert source.lstrip().startswith("if not RUN_TIER_A:")
    replay = next(s for s in _code() if "def r1(" in s)
    assert "estimations_performed" in replay


def test_drive_cache_is_only_read_and_outputs_go_to_new_places():
    code = "\n".join(_code())
    assert "backup-daemon" not in code                       # nothing is uploaded to fit_cache
    assert ".sync(" not in code
    assert re.search(r'EVIDENCE = Path\(DRIVE_ROOT\) / "r1_replay" / STAMP', code)
    assert "checkout\", \"--detach\", PIN_COMMIT" in code
    assert "\"status\", \"--porcelain\"" in code
    assert "push\", \"--force" not in code and "-f\"" not in code
    for branch in re.findall(r'push\(f"([^"]+)"', code):
        assert "{STAMP}" in branch                            # a new branch every time


# -- the setup cell, evaluated for real with the notebook's own defaults ----------------

def _run_settings_and_setup(monkeypatch, pin_override=None):
    """Execute the Settings and Setup cells exactly as Colab would, off Colab.

    `google.colab` is absent here, so the cell takes its documented non-Colab branch;
    directory creation is a no-op so nothing is written under /content.
    """
    import pathlib
    monkeypatch.setattr(pathlib.Path, "mkdir", lambda self, *a, **k: None)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    settings, setup = _code()[0], _code()[1]
    namespace: dict = {}
    exec(compile(settings, "settings", "exec"), namespace)
    if pin_override is not None:
        namespace["PIN_COMMIT"] = pin_override
    exec(compile(setup, "setup", "exec"), namespace)
    return namespace


def test_setup_cell_accepts_the_default_pinned_commit(monkeypatch):
    default_pin = re.search(r'^PIN_COMMIT = "([^"]+)"', _code()[0], re.M).group(1)
    assert re.fullmatch(r"[0-9a-f]{40}", default_pin), "the shipped notebook must be pinned"
    namespace = _run_settings_and_setup(monkeypatch)      # must not raise
    assert namespace["PIN_COMMIT"] == default_pin
    assert namespace["RUN_TIER_A"] is False


def test_setup_cell_rejects_a_placeholder_or_short_pin(monkeypatch):
    import pytest
    for bad in ("__PIN__", "8aaa421", "", "g" * 40):
        with pytest.raises(AssertionError):
            _run_settings_and_setup(monkeypatch, pin_override=bad)


def test_the_pin_appears_only_in_its_default_assignment():
    pin = re.search(r'^PIN_COMMIT = "([^"]+)"', _code()[0], re.M).group(1)
    code = "\n".join(_code())
    assert code.count(pin) == 1, "the pinned SHA leaked into another cell (e.g. a guard)"
