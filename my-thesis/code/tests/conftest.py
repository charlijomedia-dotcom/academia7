"""Shared pytest fixtures."""

from __future__ import annotations

# Rendering guard. Figures must be drawn with matplotlib's own defaults (DejaVu Sans,
# default hinting), as the published outputs were. A machine-level rc file, such as the
# MATPLOTLIBRC=/etc/matplotlib of the Claude Code cloud container, would otherwise change
# fonts and figure bytes silently. MATPLOTLIBRC is read when matplotlib is imported, so it
# is pinned here, before any test module imports matplotlib, to the repo-tracked EMPTY
# file colab/matplotlibrc.default. tests/unit/test_render_guard.py checks the result.
import os as _os
import sys as _sys
from pathlib import Path as _Path

_DEFAULT_RC = _Path(__file__).resolve().parents[2] / "colab" / "matplotlibrc.default"
if "matplotlib" in _sys.modules:
    import matplotlib as _mpl
    if _Path(_mpl.matplotlib_fname()).resolve() not in (
            _DEFAULT_RC, (_Path(_mpl.get_data_path()) / "matplotlibrc").resolve()):
        raise RuntimeError("matplotlib was imported before tests/conftest.py with rc file "
                           f"{_mpl.matplotlib_fname()}; run with MATPLOTLIBRC={_DEFAULT_RC}")
_os.environ["MATPLOTLIBRC"] = str(_DEFAULT_RC)

import pytest

from helpers import FakeTransport, monthly_dates, observations_payload, series_metadata_payload
from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR
from thesis.data.fred_client import FredClient


@pytest.fixture(scope="session")
def config():
    return load_config(config_dir=CONFIG_DIR)


@pytest.fixture
def fake_series_payload():
    dates = monthly_dates("2000-01-01", 24)
    values = [f"{100 + i:.3f}" for i in range(24)]
    values[10] = "."  # an interior missing observation, as in the real vintage
    return dates, values, observations_payload(dates, values)


@pytest.fixture
def fake_client(fake_series_payload):
    _, _, payload = fake_series_payload
    transport = FakeTransport(
        {"/series/observations": payload, "/fred/series?": series_metadata_payload()}
    )
    client = FredClient(api_key="TESTKEY", transport=transport, sleep=lambda _: None)
    return client, transport
