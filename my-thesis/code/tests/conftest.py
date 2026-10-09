"""Shared pytest fixtures."""

from __future__ import annotations

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
