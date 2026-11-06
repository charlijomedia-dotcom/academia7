"""The test environment renders with matplotlib's own defaults (tests/conftest.py pins them)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "colab"))
import r1_render_guard as guard  # noqa: E402


def test_default_rc_file_is_tracked_and_empty():
    assert guard.DEFAULT_RC == ROOT / "colab" / "matplotlibrc.default"
    assert guard.DEFAULT_RC.is_file() and guard.DEFAULT_RC.read_text() == ""


def test_test_session_renders_with_matplotlib_defaults():
    import matplotlib
    from matplotlib import font_manager
    assert os.environ["MATPLOTLIBRC"] == str(guard.DEFAULT_RC)
    assert Path(matplotlib.matplotlib_fname()).resolve() == guard.DEFAULT_RC
    record = guard.check_default_rendering()
    assert record["ok"] and record["rc_differs_from_default"] == []
    assert record["resolved_text_font"] == "DejaVuSans.ttf"
    font = font_manager.findfont(font_manager.FontProperties(family=["sans-serif"]))
    assert Path(font).name == "DejaVuSans.ttf"


def _run(code: str, rc_dir: Path) -> subprocess.CompletedProcess:
    env = {**os.environ, "MATPLOTLIBRC": str(rc_dir), "PYTHONPATH": str(ROOT / "colab")}
    return subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)


@pytest.fixture
def foreign_rc(tmp_path):
    (tmp_path / "matplotlibrc").write_text("font.family: serif\ntext.hinting: no_hinting\n")
    return tmp_path


def test_guard_refuses_a_foreign_rc_file(foreign_rc):
    code = ("import matplotlib, r1_render_guard as g\n"
            "try:\n    g.check_default_rendering()\nexcept g.RenderGuardError as e:\n"
            "    print('REFUSED', e)\n")
    out = _run(code, foreign_rc)
    assert out.returncode == 0, out.stderr
    assert "REFUSED" in out.stdout and "font.family" in out.stdout and "text.hinting" in out.stdout


def test_pin_refuses_after_matplotlib_was_imported_with_a_foreign_rc(foreign_rc):
    code = ("import matplotlib, r1_render_guard as g\n"
            "try:\n    g.pin_default_rc()\nexcept g.RenderGuardError:\n    print('REFUSED')\n")
    assert "REFUSED" in _run(code, foreign_rc).stdout


def test_pin_before_import_gives_defaults_even_with_a_foreign_rc(foreign_rc):
    code = ("import r1_render_guard as g\ng.pin_default_rc()\nimport matplotlib\n"
            "print(g.check_default_rendering()['ok'])\n")
    out = _run(code, foreign_rc)
    assert out.stdout.strip() == "True", out.stderr


def test_guard_checks_the_expected_version(tmp_path):
    import matplotlib
    (tmp_path / "manifests").mkdir()
    (tmp_path / "manifests" / "run_manifest.json").write_text(
        '{"environment": {"packages": {"matplotlib": "0.0.1"}}}')
    assert guard.expected_version_from(tmp_path) == "0.0.1"
    with pytest.raises(guard.RenderGuardError, match="expected 0.0.1"):
        guard.check_default_rendering("0.0.1")
    assert guard.check_default_rendering(matplotlib.__version__)["ok"]
