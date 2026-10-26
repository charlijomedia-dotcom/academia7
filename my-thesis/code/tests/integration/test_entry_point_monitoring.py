"""The entry point's monitoring options.

`--data-only` is a check, not a run, so it must start no monitor and leave no run log.
The new options must parse, and the log mirror must default to `$THESIS_LOG_MIRROR`.
"""

from __future__ import annotations

import importlib.util
import sys

import pytest

from thesis.core.paths import CODE_ROOT, RUN_LOGS_DIR


@pytest.fixture(scope="module")
def run_all():
    spec = importlib.util.spec_from_file_location("run_all_entry", CODE_ROOT / "run_all.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _logs() -> set[str]:
    root = RUN_LOGS_DIR / "smoke"
    return {p.name for p in root.iterdir()} if root.exists() else set()


def test_data_only_starts_no_monitor_and_writes_no_run_log(run_all, capsys):
    before = _logs()
    assert run_all.main(["--smoke-test", "--data-only"]) == 0
    assert _logs() == before
    out = capsys.readouterr().out
    assert "--data-only: stopping" in out
    assert "monitoring run" not in out


def test_help_lists_the_monitoring_options(run_all, capsys):
    with pytest.raises(SystemExit):
        run_all.main(["--help"])
    text = capsys.readouterr().out
    for option in ("--no-monitor", "--log-mirror", "--heartbeat-seconds",
                   "--summary-seconds"):
        assert option in text


def test_log_mirror_defaults_to_the_environment(run_all, monkeypatch, capsys):
    import argparse

    captured = {}
    real = argparse.ArgumentParser.parse_args

    def spy(self, args=None, namespace=None):
        result = real(self, args, namespace)
        captured["mirror"] = result.log_mirror
        raise SystemExit(0)

    monkeypatch.setenv("THESIS_LOG_MIRROR", "/drive/thesis_logs")
    # The default is read when the parser is built, inside main().
    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", spy)
    with pytest.raises(SystemExit):
        run_all.main([])
    assert captured["mirror"] == "/drive/thesis_logs"
