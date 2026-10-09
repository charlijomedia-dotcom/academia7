"""Test helpers shared across modules.

Importable as a top-level module because `tests` is on the pytest path (see pyproject).
Nothing here touches the network: the FRED client is always driven through a fake
transport, which is also how the suite proves that the default run makes no network call.
"""

from __future__ import annotations

import json
from typing import Any

import pandas as pd


def monthly_dates(start: str, n: int) -> list[str]:
    return [d.strftime("%Y-%m-%d") for d in pd.date_range(start, periods=n, freq="MS")]


def quarterly_dates(start: str, n: int) -> list[str]:
    return [d.strftime("%Y-%m-%d") for d in pd.date_range(start, periods=n, freq="QS")]


def observations_payload(
    dates: list[str], values: list[str], realtime: str = "2026-10-05"
) -> dict[str, Any]:
    return {
        "realtime_start": realtime,
        "realtime_end": realtime,
        "observation_start": dates[0],
        "observation_end": dates[-1],
        "count": len(dates),
        "observations": [
            {
                "realtime_start": realtime,
                "realtime_end": realtime,
                "date": date,
                "value": value,
            }
            for date, value in zip(dates, values)
        ],
    }


def series_metadata_payload(series_id: str = "TESTSER") -> dict[str, Any]:
    return {
        "seriess": [
            {
                "id": series_id,
                "title": "Test Series",
                "frequency_short": "M",
                "units": "Index",
                "seasonal_adjustment_short": "SA",
            }
        ]
    }


class FakeTransport:
    """Records every URL it is asked for and replays canned payloads."""

    def __init__(self, payloads: dict[str, dict[str, Any]]):
        self.payloads = payloads
        self.calls: list[str] = []

    def __call__(self, url: str, timeout: int) -> bytes:
        self.calls.append(url)
        for key, payload in self.payloads.items():
            if key in url:
                return json.dumps(payload).encode("utf-8")
        raise AssertionError(f"unexpected request: {url}")
