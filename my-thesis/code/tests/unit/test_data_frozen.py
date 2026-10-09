"""Frozen-data layer: retrieval, freezing, verification and range checks.

Covers the Comp §15 reproducibility requirements for frozen-file hash verification, the
vintage date, expected endpoints, and the rule that no data may be silently substituted.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from thesis.data.fred_client import (
    API_KEY_PARAM,
    FredClient,
    RetrievalError,
    api_key_from_env,
    compare_responses,
    redact,
)
from thesis.data.frozen import (
    SeriesSpec,
    VintageDiscrepancy,
    initialize_frozen,
    load_frozen_series,
    read_series_csv,
    verify_frozen,
    write_series_csv,
)
from thesis.data.manifest import FrozenDataError, FrozenManifest
from thesis.data.samples import check_expected_ranges

from helpers import FakeTransport, monthly_dates, observations_payload


class TestFredClient:
    def test_requests_the_approved_vintage(self, fake_client):
        client, transport = fake_client
        client.fetch("TESTSER", vintage_date="2026-10-05")
        assert "vintage_dates=2026-10-05" in transport.calls[0]
        assert "units=lin" in transport.calls[0]  # raw levels only

    def test_realtime_form_is_the_audit_cross_check(self, fake_client):
        client, transport = fake_client
        client.fetch("TESTSER", realtime="2026-10-05")
        assert "realtime_start=2026-10-05" in transport.calls[0]
        assert "realtime_end=2026-10-05" in transport.calls[0]

    def test_exactly_one_request_form_allowed(self, fake_client):
        client, _ = fake_client
        with pytest.raises(ValueError):
            client.build_params("X", vintage_date="2026-10-05", realtime="2026-10-05")
        with pytest.raises(ValueError):
            client.build_params("X")

    def test_api_key_is_redacted_everywhere_it_is_stored(self, fake_client):
        client, _ = fake_client
        response = client.fetch("TESTSER", vintage_date="2026-10-05")
        assert "TESTKEY" not in json.dumps(response.request_params)
        assert "TESTKEY" not in response.request_url_redacted
        assert response.request_params[API_KEY_PARAM] == "<redacted>"

    def test_missing_values_are_preserved_not_dropped(self, fake_client):
        client, _ = fake_client
        response = client.fetch("TESTSER", vintage_date="2026-10-05")
        assert response.n_rows == 24
        assert response.missing_dates == ["2000-11-01"]

    def test_api_key_from_env(self, monkeypatch):
        monkeypatch.delenv("FRED_API_KEY", raising=False)
        with pytest.raises(RetrievalError):
            api_key_from_env()
        monkeypatch.setenv("FRED_API_KEY", "abc")
        assert api_key_from_env() == "abc"

    def test_redact_leaves_other_params_intact(self):
        assert redact({"api_key": "s", "series_id": "X"}) == {
            "api_key": "<redacted>",
            "series_id": "X",
        }


class TestVintageCrossCheck:
    def test_identical_responses_compare_equal(self, fake_client):
        client, _ = fake_client
        primary = client.fetch("TESTSER", vintage_date="2026-10-05")
        audit = client.fetch("TESTSER", realtime="2026-10-05")
        comparison = compare_responses(primary, audit)
        assert comparison["identical"]
        assert comparison["dates_with_different_values"] == []

    def test_value_difference_is_detected(self, fake_series_payload):
        dates, values, payload = fake_series_payload
        altered = [v for v in values]
        altered[5] = "999.0"
        transport = FakeTransport(
            {
                "vintage_dates": payload,
                "realtime_start": observations_payload(dates, altered),
            }
        )
        client = FredClient(api_key="K", transport=transport, sleep=lambda _: None)
        primary = client.fetch("T", vintage_date="2026-10-05")
        audit = client.fetch("T", realtime="2026-10-05")
        comparison = compare_responses(primary, audit)
        assert not comparison["identical"]
        assert comparison["dates_with_different_values"] == ["2000-06-01"]


class TestFreezing:
    def _client(self, dates, values):
        metadata = {
            "seriess": [
                {
                    "id": "TESTSER",
                    "title": "Test Series",
                    "frequency_short": "M",
                    "units": "Index",
                    "seasonal_adjustment_short": "SA",
                }
            ]
        }
        payload = observations_payload(dates, values)
        transport = FakeTransport(
            {"/series/observations": payload, "/fred/series?": metadata}
        )
        return FredClient(api_key="K", transport=transport, sleep=lambda _: None)

    def test_initialize_writes_files_metadata_and_manifest(self, tmp_path):
        dates = monthly_dates("2000-01-01", 12)
        values = [f"{100 + i}" for i in range(12)]
        client = self._client(dates, values)
        manifest = initialize_frozen(
            client,
            [SeriesSpec("TESTSER", "Test Institution")],
            vintage_date="2026-10-05",
            directory=tmp_path,
        )
        assert (tmp_path / "TESTSER.csv").exists()
        assert (tmp_path / "TESTSER.meta.json").exists()
        assert (tmp_path / "MANIFEST.json").exists()
        entry = manifest.entry("TESTSER")
        assert entry.vintage_date == "2026-10-05"
        assert entry.row_count == 12
        assert entry.first_observation_date == "2000-01-01"
        assert entry.sha256
        assert entry.source_institution == "Test Institution"
        assert entry.request_params[API_KEY_PARAM] == "<redacted>"

    def test_api_key_never_reaches_disk(self, tmp_path):
        secret = "SUPERSECRETKEY123"
        dates = monthly_dates("2000-01-01", 6)
        client = self._client(dates, ["1", "2", "3", "4", "5", "6"])
        client.api_key = secret
        initialize_frozen(
            client,
            [SeriesSpec("TESTSER")],
            vintage_date="2026-10-05",
            directory=tmp_path,
        )
        written = [p for p in tmp_path.rglob("*") if p.is_file()]
        assert written
        for path in written:
            assert secret not in path.read_text(encoding="utf-8")

    def test_initialize_refuses_to_overwrite_an_existing_snapshot(self, tmp_path):
        dates = monthly_dates("2000-01-01", 6)
        client = self._client(dates, ["1", "2", "3", "4", "5", "6"])
        initialize_frozen(
            client, [SeriesSpec("TESTSER")], vintage_date="2026-10-05", directory=tmp_path
        )
        with pytest.raises(FileExistsError):
            initialize_frozen(
                client,
                [SeriesSpec("TESTSER")],
                vintage_date="2026-10-05",
                directory=tmp_path,
            )

    def test_cross_check_discrepancy_halts_initialization(self, tmp_path):
        dates = monthly_dates("2000-01-01", 6)
        primary = observations_payload(dates, ["1", "2", "3", "4", "5", "6"])
        audit = observations_payload(dates, ["1", "2", "3", "4", "5", "99"])
        metadata = {"seriess": [{"id": "T", "title": "t"}]}
        transport = FakeTransport(
            {
                "vintage_dates": primary,
                "realtime_start": audit,
                "/fred/series?": metadata,
            }
        )
        client = FredClient(api_key="K", transport=transport, sleep=lambda _: None)
        with pytest.raises(VintageDiscrepancy):
            initialize_frozen(
                client, [SeriesSpec("T")], vintage_date="2026-10-05", directory=tmp_path
            )

    def test_verification_detects_tampering(self, tmp_path):
        dates = monthly_dates("2000-01-01", 6)
        client = self._client(dates, ["1", "2", "3", "4", "5", "6"])
        initialize_frozen(
            client, [SeriesSpec("TESTSER")], vintage_date="2026-10-05", directory=tmp_path
        )
        verify_frozen(tmp_path)  # clean snapshot verifies
        target = tmp_path / "TESTSER.csv"
        target.write_text(target.read_text(encoding="utf-8").replace("1", "7"), encoding="utf-8")
        with pytest.raises(FrozenDataError):
            verify_frozen(tmp_path)

    def test_verification_detects_a_deleted_file(self, tmp_path):
        dates = monthly_dates("2000-01-01", 6)
        client = self._client(dates, ["1", "2", "3", "4", "5", "6"])
        initialize_frozen(
            client, [SeriesSpec("TESTSER")], vintage_date="2026-10-05", directory=tmp_path
        )
        (tmp_path / "TESTSER.csv").unlink()
        with pytest.raises(FrozenDataError):
            verify_frozen(tmp_path)

    def test_snapshot_hash_is_order_independent_and_content_sensitive(self, tmp_path):
        dates = monthly_dates("2000-01-01", 6)
        client = self._client(dates, ["1", "2", "3", "4", "5", "6"])
        manifest = initialize_frozen(
            client, [SeriesSpec("TESTSER")], vintage_date="2026-10-05", directory=tmp_path
        )
        first = manifest.snapshot_hash
        reloaded = FrozenManifest.read(tmp_path / "MANIFEST.json")
        assert reloaded.snapshot_hash == first


class TestFrozenCsv:
    def test_raw_value_strings_are_preserved_including_missing(self, tmp_path):
        dates = monthly_dates("2000-01-01", 4)
        payload = observations_payload(dates, ["1.5", ".", "3.5", "4.5"])
        transport = FakeTransport({"/series/observations": payload})
        client = FredClient(api_key="K", transport=transport, sleep=lambda _: None)
        response = client.fetch("T", vintage_date="2026-10-05")
        path = write_series_csv(tmp_path / "T.csv", response)
        text = path.read_text(encoding="utf-8")
        assert "2000-02-01,." in text  # the provider's own missing marker survives
        series = read_series_csv(path)
        assert np.isnan(series.iloc[1])
        assert series.iloc[0] == 1.5
        assert len(series) == 4  # the gap is a NaN row, not a dropped row

    def test_load_frozen_series_names_the_series(self, tmp_path):
        dates = monthly_dates("2000-01-01", 3)
        payload = observations_payload(dates, ["1", "2", "3"])
        transport = FakeTransport({"/series/observations": payload})
        client = FredClient(api_key="K", transport=transport, sleep=lambda _: None)
        write_series_csv(tmp_path / "ABC.csv", client.fetch("ABC", vintage_date="2026-10-05"))
        series = load_frozen_series("ABC", tmp_path)
        assert series.name == "ABC"


class TestExpectedRanges:
    def _series(self, first: str, periods: int, freq: str = "MS") -> pd.Series:
        index = pd.date_range(first, periods=periods, freq=freq)
        return pd.Series(np.arange(periods, dtype=float), index=index)

    def test_matching_ranges_pass(self, config):
        raw = {"M2SL": self._series("1959-01-01", 812)}
        checks = check_expected_ranges(raw, config)
        assert checks[0].ok

    def test_wrong_endpoint_halts(self, config):
        raw = {"M2SL": self._series("1959-01-01", 811)}
        with pytest.raises(VintageDiscrepancy):
            check_expected_ranges(raw, config)

    def test_unknown_series_halts(self, config):
        raw = {"NOTASERIES": self._series("2000-01-01", 10)}
        with pytest.raises(VintageDiscrepancy):
            check_expected_ranges(raw, config)

    def test_known_gap_is_reported_not_hidden(self, config):
        series = self._series("1947-01-01", 956)
        series.loc[pd.Timestamp("2025-10-01")] = np.nan
        checks = check_expected_ranges({"CPIAUCSL": series}, config)
        assert checks[0].ok  # the range is right
        assert checks[0].missing_dates == ["2025-10-01"]  # and the gap is visible

    def test_accepted_deviation_note_is_carried_through(self, config):
        raw = {"FEDFUNDS": self._series("1954-07-01", 867)}
        checks = check_expected_ranges(raw, config)
        assert "2026M9" in checks[0].note
