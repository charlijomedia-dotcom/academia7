"""The canonical CSV-first architecture, verified against the real frozen store.

Covers the Comp §15 requirements added by the 13 October 2026 amendment: canonical CSV
schema and hash, exactly two LOCF cells, untouched official raw files, the resulting
transformation artifacts, CSV-first loading with no FRED call, and the store-state rules.
"""

from __future__ import annotations

import json
import socket
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from thesis.core.config import load_config
from thesis.core.hashing import sha256_file
from thesis.core.paths import CONFIG_DIR, FROZEN_VINTAGE_DIR, PROJECT_ROOT
from thesis.data.canonical import (
    CANONICAL_COLUMNS,
    STATUS_IMPUTED,
    STATUS_OBSERVED,
    StoreState,
    build_canonical_frame,
    imputed_dates,
    load_canonical,
    read_raw_strings,
    to_panels,
    write_canonical_csv,
)
from thesis.data.frozen import verify_frozen
from thesis.data.manifest import FrozenDataError
from thesis.data.store import build_canonical_from_raw, detect_state, load_bundle, verify_canonical
from thesis.transforms.differences import first_difference
from thesis.transforms.growth import annualized_logdiff

pytestmark = pytest.mark.skipif(
    not (FROZEN_VINTAGE_DIR / "MANIFEST.json").exists(),
    reason="frozen store not present",
)

APPROVED_IMPUTATIONS = {("CPIAUCSL", "2025-10-01"), ("UNRATE", "2025-10-01")}


@pytest.fixture(scope="module")
def config():
    return load_config(config_dir=CONFIG_DIR)


@pytest.fixture(scope="module")
def bundle(config):
    return load_bundle(FROZEN_VINTAGE_DIR, config)


class TestDataIntegrity:
    def test_store_is_complete_and_verifies(self, config):
        assert detect_state(FROZEN_VINTAGE_DIR, config) is StoreState.COMPLETE
        verify_canonical(FROZEN_VINTAGE_DIR, config)
        verify_frozen(FROZEN_VINTAGE_DIR)

    def test_canonical_schema_and_column_order(self, bundle):
        assert tuple(c for c in bundle.frame.columns if c != "value_float") == CANONICAL_COLUMNS

    def test_all_seven_approved_series_present(self, bundle):
        expected = {"GDPC1", "CPIAUCSL", "UNRATE", "INDPRO", "FEDFUNDS", "M2SL", "USREC"}
        assert set(bundle.frame["series_id"].unique()) == expected

    def test_approved_endpoints_respected(self, bundle, config):
        monthly_end = pd.Timestamp(config.get("samples.monthly_end"))
        quarterly_end = pd.Timestamp(config.get("samples.quarterly_end"))
        for series_id, block in bundle.frame.groupby("series_id"):
            end = quarterly_end if block["frequency"].iloc[0] == "Q" else monthly_end
            assert block["date"].max() == end, series_id

    def test_approved_start_dates(self, bundle, config):
        for series_id, block in bundle.frame.groupby("series_id"):
            spec = config.get(f"targets.{series_id}")
            expected = pd.Timestamp(spec.get("canonical_start") or spec["start"])
            assert block["date"].min() == expected, series_id

    def test_no_missing_values_remain(self, bundle):
        assert np.isfinite(bundle.frame["value_float"].to_numpy()).all()

    def test_no_duplicate_series_date_pairs(self, bundle):
        assert not bundle.frame.duplicated(subset=["series_id", "date"]).any()

    def test_rows_sorted_deterministically(self, bundle, config):
        sort_by = config.get("canonical_input.sort_by")
        expected = bundle.frame.sort_values(sort_by, kind="mergesort").reset_index(drop=True)
        pd.testing.assert_frame_equal(bundle.frame, expected)

    def test_quarterly_gdp_is_not_expanded_to_monthly(self, bundle):
        gdp = bundle.frame[bundle.frame["series_id"] == "GDPC1"]
        assert set(gdp["frequency"]) == {"Q"}
        gaps = gdp["date"].diff().dropna().dt.days
        assert gaps.min() >= 89  # quarterly spacing, never monthly

    def test_no_transformed_values_in_the_input(self, bundle):
        # The input holds raw levels only; growth rates are computed after loading.
        assert "value_float" in bundle.frame.columns  # derived in memory, not in the file
        text = bundle.csv_path.read_text(encoding="utf-8").splitlines()[0]
        assert text == ",".join(CANONICAL_COLUMNS)

    def test_hash_recorded_in_metadata_matches_the_file(self, bundle):
        assert bundle.metadata["csv_sha256"] == sha256_file(bundle.csv_path)
        assert bundle.csv_sha256 == bundle.metadata["csv_sha256"]

    def test_metadata_links_to_the_official_parent_snapshot(self, bundle):
        assert bundle.metadata["parent_source_snapshot_hash"] == bundle.source_manifest.snapshot_hash
        assert bundle.metadata["not_an_official_fred_release"] is True

    def test_readme_discloses_the_imputation(self, config):
        readme = (FROZEN_VINTAGE_DIR / config.get("canonical_input.readme")).read_text(encoding="utf-8")
        assert "NOT an unmodified official FRED extract" in readme
        assert "IMPUTED_LOCF" in readme
        assert "2025-10-01" in readme


class TestExactlyTwoLocfReplacements:
    def test_only_the_two_approved_cells_are_imputed(self, bundle):
        imputed = bundle.frame[bundle.frame["observation_status"] == STATUS_IMPUTED]
        found = {(r.series_id, r.date.strftime("%Y-%m-%d")) for r in imputed.itertuples()}
        assert found == APPROVED_IMPUTATIONS
        assert len(imputed) == 2

    def test_every_other_row_is_observed(self, bundle):
        other = bundle.frame[bundle.frame["observation_status"] != STATUS_IMPUTED]
        assert set(other["observation_status"]) == {STATUS_OBSERVED}
        assert len(other) == len(bundle.frame) - 2

    def test_imputed_values_equal_the_september_levels(self, bundle):
        for series_id in ("CPIAUCSL", "UNRATE"):
            block = bundle.frame[bundle.frame["series_id"] == series_id].set_index("date")
            september = block.loc[pd.Timestamp("2025-09-01"), "value"]
            october = block.loc[pd.Timestamp("2025-10-01"), "value"]
            assert october == september, series_id

    def test_imputed_rows_keep_the_official_value_blank(self, bundle):
        imputed = bundle.frame[bundle.frame["observation_status"] == STATUS_IMPUTED]
        assert (imputed["source_value"] == "").all()

    def test_imputed_rows_carry_method_and_source_date(self, bundle):
        imputed = bundle.frame[bundle.frame["observation_status"] == STATUS_IMPUTED]
        assert set(imputed["imputation_method"]) == {"LOCF"}
        assert set(imputed["imputation_source_date"]) == {"2025-09-01"}

    def test_observed_rows_carry_no_imputation_metadata(self, bundle):
        observed = bundle.frame[bundle.frame["observation_status"] == STATUS_OBSERVED]
        assert (observed["imputation_method"] == "").all()
        assert (observed["imputation_source_date"] == "").all()

    def test_observed_value_equals_its_official_source_value(self, bundle):
        observed = bundle.frame[bundle.frame["observation_status"] == STATUS_OBSERVED]
        assert (observed["value"] == observed["source_value"]).all()

    def test_official_raw_files_still_contain_the_missing_markers(self):
        for series_id in ("CPIAUCSL", "UNRATE"):
            raw = read_raw_strings(FROZEN_VINTAGE_DIR / f"{series_id}.csv")
            row = raw[raw["date"] == "2025-10-01"]
            assert len(row) == 1
            assert row["value"].iloc[0] == ".", series_id

    def test_official_raw_files_keep_observations_past_the_study_endpoint(self):
        # Decision T5: the archive keeps 2026-09 for UNRATE and FEDFUNDS; only the
        # canonical study file is truncated to the approved 2026M8 endpoint.
        for series_id in ("UNRATE", "FEDFUNDS"):
            raw = read_raw_strings(FROZEN_VINTAGE_DIR / f"{series_id}.csv")
            assert raw["date"].iloc[-1] == "2026-09-01", series_id

    def test_imputation_audit_has_exactly_two_rows(self):
        audit = PROJECT_ROOT / "output" / "data_audit" / "october_2025_imputation_audit.csv"
        if not audit.exists():
            pytest.skip("audit not generated in this working tree")
        frame = pd.read_csv(audit, dtype=str, keep_default_na=False)
        assert len(frame) == 2
        assert set(frame["series_id"]) == {"CPIAUCSL", "UNRATE"}
        assert set(frame["is_official_observation"]) == {"False"}

    def test_imputed_dates_helper_reports_the_two_cells(self, bundle):
        found = imputed_dates(bundle.frame)
        assert set(found) == {"CPIAUCSL", "UNRATE"}
        for dates in found.values():
            assert dates == [pd.Timestamp("2025-10-01")]


class TestTransformationArtifacts:
    """The consequences Part 5 §2.2A requires the thesis to state, verified numerically."""

    def test_october_2025_cpi_inflation_is_exactly_zero(self, bundle, config):
        panel = to_panels(bundle.frame)["M"]
        inflation = annualized_logdiff(panel["CPIAUCSL"], 1200.0)
        assert inflation.loc[pd.Timestamp("2025-10-01")] == 0.0

    def test_november_captures_the_september_to_november_change(self, bundle):
        panel = to_panels(bundle.frame)["M"]
        cpi = panel["CPIAUCSL"]
        inflation = annualized_logdiff(cpi, 1200.0)
        september = cpi.loc[pd.Timestamp("2025-09-01")]
        november = cpi.loc[pd.Timestamp("2025-11-01")]
        expected = 1200.0 * np.log(november / september)
        assert inflation.loc[pd.Timestamp("2025-11-01")] == pytest.approx(expected)

    def test_differenced_unemployment_october_change_is_exactly_zero(self, bundle):
        panel = to_panels(bundle.frame)["M"]
        change = first_difference(panel["UNRATE"])
        assert change.loc[pd.Timestamp("2025-10-01")] == 0.0

    def test_other_months_are_unaffected_by_the_imputation(self, bundle):
        panel = to_panels(bundle.frame)["M"]
        inflation = annualized_logdiff(panel["CPIAUCSL"], 1200.0)
        window = inflation.loc["2025-06-01":"2025-09-01"]
        assert (window != 0).all()

    def test_annualization_factors_applied_to_the_canonical_panels(self, bundle):
        panels = to_panels(bundle.frame)
        monthly = annualized_logdiff(panels["M"]["INDPRO"], 1200.0).dropna()
        quarterly = annualized_logdiff(panels["Q"]["GDPC1"], 400.0).dropna()
        assert len(monthly) == 955
        assert len(quarterly) == 317


class TestReproducibleLoading:
    def test_loading_makes_no_network_call(self, config, monkeypatch):
        original = socket.socket

        def forbidden(*args, **kwargs):
            raise AssertionError("the default run must not contact the network")

        monkeypatch.setattr(socket, "socket", forbidden)
        try:
            frame = load_canonical(FROZEN_VINTAGE_DIR, config)
        finally:
            monkeypatch.setattr(socket, "socket", original)
        assert len(frame) > 0

    def test_loading_works_without_a_fred_key(self, config, monkeypatch):
        monkeypatch.delenv("FRED_API_KEY", raising=False)
        assert len(load_bundle(FROZEN_VINTAGE_DIR, config).frame) > 0

    def test_rebuilding_reproduces_identical_bytes(self, config, tmp_path):
        source_manifest, _ = verify_frozen(FROZEN_VINTAGE_DIR)
        raw = {
            entry.series_id: read_raw_strings(FROZEN_VINTAGE_DIR / entry.file_name)
            for entry in source_manifest.entries
        }
        frame, _ = build_canonical_frame(raw, config)
        rebuilt = write_canonical_csv(frame, tmp_path / "rebuilt.csv")
        original = FROZEN_VINTAGE_DIR / config.get("canonical_input.csv")
        assert sha256_file(rebuilt) == sha256_file(original)

    def test_two_loads_give_identical_frames(self, config):
        a = load_canonical(FROZEN_VINTAGE_DIR, config)
        b = load_canonical(FROZEN_VINTAGE_DIR, config)
        pd.testing.assert_frame_equal(a, b)

    def test_panels_derived_in_memory_have_the_expected_shape(self, bundle):
        panels = to_panels(bundle.frame)
        assert set(panels) == {"M", "Q"}
        assert list(panels["Q"].columns) == ["GDPC1"]
        assert set(panels["M"].columns) == {
            "CPIAUCSL", "FEDFUNDS", "INDPRO", "M2SL", "UNRATE", "USREC"
        }

    def test_corrupt_canonical_file_fails_without_overwriting(self, config, tmp_path):
        # Copy the whole store, corrupt the CSV, and confirm the run refuses to continue
        # and does not repair or re-download anything.
        import shutil

        store = tmp_path / "store"
        shutil.copytree(FROZEN_VINTAGE_DIR, store)
        target = store / config.get("canonical_input.csv")
        before = target.read_text(encoding="utf-8")
        target.write_text(before.replace("OBSERVED", "OBSERVED ", 1), encoding="utf-8")
        with pytest.raises(FrozenDataError, match="does not match its recorded hash"):
            verify_canonical(store, config)
        assert detect_state(store, config) is StoreState.UNUSABLE

    def test_registered_but_missing_canonical_file_fails(self, config, tmp_path):
        import shutil

        store = tmp_path / "store"
        shutil.copytree(FROZEN_VINTAGE_DIR, store)
        (store / config.get("canonical_input.csv")).unlink()
        assert detect_state(store, config) is StoreState.UNUSABLE
        with pytest.raises(FrozenDataError):
            verify_canonical(store, config)


class TestStoreStateRules:
    def test_absent_store(self, config, tmp_path):
        assert detect_state(tmp_path / "nothing", config) is StoreState.ABSENT

    def test_raw_only_store_builds_canonical_locally(self, config, tmp_path):
        import shutil

        store = tmp_path / "store"
        store.mkdir()
        for path in FROZEN_VINTAGE_DIR.iterdir():
            if not path.name.startswith("thesis_input"):
                shutil.copy2(path, store / path.name)
        assert detect_state(store, config) is StoreState.RAW_ONLY

        original_manifest = (store / "MANIFEST.json").read_bytes()
        bundle = build_canonical_from_raw(store, config)
        assert detect_state(store, config) is StoreState.COMPLETE
        # The original raw manifest must not be altered (Comp §2).
        assert (store / "MANIFEST.json").read_bytes() == original_manifest
        assert bundle.csv_sha256 == sha256_file(FROZEN_VINTAGE_DIR / config.get("canonical_input.csv"))

    def test_canonical_without_its_raw_parent_is_unusable(self, config, tmp_path):
        import shutil

        store = tmp_path / "store"
        store.mkdir()
        for name in ("csv", "metadata", "readme", "manifest"):
            source = FROZEN_VINTAGE_DIR / config.get(f"canonical_input.{name}")
            shutil.copy2(source, store / source.name)
        assert detect_state(store, config) is StoreState.UNUSABLE
