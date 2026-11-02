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
