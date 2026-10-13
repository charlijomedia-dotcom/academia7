"""Pipeline helper logic that is easier to pin down directly than through a full run.

The LOCF exposure logic is the subtle part: which *transformed* observations depend on an
imputed *raw* level depends on the transformation, and getting it wrong would understate
the exposure that T4.9 exists to measure.
"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR, Namespace, output_layout
from thesis.core.provenance import RunContext
from thesis.data.canonical import STATUS_IMPUTED, STATUS_OBSERVED
from thesis.pipeline import Pipeline


def _frame(rows) -> pd.DataFrame:
    return pd.DataFrame(rows)


def _bundle(frame: pd.DataFrame):
    return SimpleNamespace(
        frame=frame, csv_path="thesis_input_2026-10-05.csv", csv_sha256="a" * 64,
        metadata={"csv_file": "thesis_input_2026-10-05.csv", "csv_sha256": "a" * 64,
                  "row_count": len(frame), "vintage_date": "2026-10-05",
                  "created_utc": "2026-10-13T00:00:00Z",
                  "parent_source_snapshot_hash": "b" * 64},
        input_manifest={}, source_manifest=SimpleNamespace(entries=[], snapshot_hash="b" * 64),
        data_input_identity="a" * 64, parent_source_hash="b" * 64)


@pytest.fixture
def pipeline(tmp_path):
    config = load_config(names=("baseline", "series_catalog", "thresholds", "smoke"),
                         config_dir=CONFIG_DIR)
    layout = output_layout(Namespace.SMOKE)
    layout = type(layout)(root=tmp_path / "out", cache=tmp_path / "cache")
    layout.create()
    context = RunContext(namespace=Namespace.SMOKE, config_hash=config.hash)
    rows = [{"series_id": "CPIAUCSL", "date": pd.Timestamp("2025-10-01"),
             "value": 324.245, "source_value": "", "observation_status": STATUS_IMPUTED,
             "imputation_method": "locf", "imputation_source_date": "2025-09-01"},
            {"series_id": "CPIAUCSL", "date": pd.Timestamp("2025-09-01"),
             "value": 324.245, "source_value": "324.245",
             "observation_status": STATUS_OBSERVED, "imputation_method": "",
             "imputation_source_date": ""}]
    return Pipeline(config, context, layout, _bundle(_frame(rows)), smoke=True)


class TestImputedDateBookkeeping:
    def test_imputed_raw_dates_are_read_from_the_canonical_frame(self, pipeline):
        assert pipeline._imputed_dates("CPIAUCSL") == [pd.Timestamp("2025-10-01")]
        assert pipeline._imputed_dates("INDPRO") == []

    def test_a_growth_transformation_exposes_the_imputed_month_and_the_next(self, pipeline):
        # 1200 * dlog(CPI) at t uses levels t and t-1, so an imputed level at October
        # contaminates both the October and the November growth observations.
        index = pd.date_range("2025-08-01", periods=4, freq="MS")
        pipeline.targets["CPIAUCSL"] = pd.Series([1.0, 2.0, 3.0, 4.0], index=index)
        affected = pipeline._affected_transformed_dates("CPIAUCSL")
        assert affected == {pd.Timestamp("2025-10-01"), pd.Timestamp("2025-11-01")}

    def test_a_level_target_exposes_only_the_imputed_month(self, pipeline):
        index = pd.date_range("2025-08-01", periods=4, freq="MS")
        pipeline.targets["UNRATE"] = pd.Series([4.0, 4.4, 4.4, 4.5], index=index)
        pipeline.frequency["UNRATE"] = "M"
        pipeline.decisions["UNRATE"] = SimpleNamespace(decision="level", break_date=None)
        pipeline.bundle.frame = _frame([
            {"series_id": "UNRATE", "date": pd.Timestamp("2025-10-01"), "value": 4.4,
             "source_value": "", "observation_status": STATUS_IMPUTED,
             "imputation_method": "locf", "imputation_source_date": "2025-09-01"}])
        assert pipeline._affected_transformed_dates("UNRATE") == {pd.Timestamp("2025-10-01")}

    def test_a_differenced_target_exposes_the_imputed_month_and_the_next(self, pipeline):
        index = pd.date_range("2025-08-01", periods=4, freq="MS")
        pipeline.targets["UNRATE"] = pd.Series([0.1, 0.0, 0.0, 0.1], index=index)
        pipeline.frequency["UNRATE"] = "M"
        pipeline.decisions["UNRATE"] = SimpleNamespace(decision="difference", break_date=None)
        pipeline.bundle.frame = _frame([
            {"series_id": "UNRATE", "date": pd.Timestamp("2025-10-01"), "value": 4.4,
             "source_value": "", "observation_status": STATUS_IMPUTED,
             "imputation_method": "locf", "imputation_source_date": "2025-09-01"}])
        assert pipeline._affected_transformed_dates("UNRATE") == {
            pd.Timestamp("2025-10-01"), pd.Timestamp("2025-11-01")}

    def test_a_series_with_no_imputation_has_no_affected_dates(self, pipeline):
        index = pd.date_range("2025-08-01", periods=4, freq="MS")
        pipeline.targets["INDPRO"] = pd.Series([1.0, 2.0, 3.0, 4.0], index=index)
        assert pipeline._affected_transformed_dates("INDPRO") == set()

    def test_an_imputed_level_before_the_first_transformed_date_still_exposes_it(self, pipeline):
        # The differenced series starts one period after the levels, so an imputed level
        # at the very start is not itself a transformed date but still contaminates the
        # first one. Dropping it would silently understate exposure.
        index = pd.date_range("2025-11-01", periods=3, freq="MS")
        pipeline.targets["CPIAUCSL"] = pd.Series([1.0, 2.0, 3.0], index=index)
        assert pipeline._affected_transformed_dates("CPIAUCSL") == {pd.Timestamp("2025-11-01")}


class TestHorizonAndWindowResolution:
    def test_horizons_combine_primary_and_robustness_without_duplicates(self, pipeline):
        assert pipeline._horizons("M") == [1, 3, 6, 12]
        assert pipeline._horizons("Q") == [1, 2, 4]

    def test_windows_are_the_approved_lengths(self, pipeline):
        assert pipeline._window("M") == 240
        assert pipeline._window("Q") == 120

    def test_smoke_runs_cap_the_origin_count_and_baseline_runs_do_not(self, pipeline):
        assert pipeline._max_origins() == int(pipeline.config.get("smoke.max_origins"))
        pipeline.smoke = False
        assert pipeline._max_origins() is None

    def test_smoke_runs_restrict_the_target_set(self, pipeline):
        assert pipeline._selected_targets() == ["GDPC1", "INDPRO"]

    def test_baseline_runs_use_every_retained_target_and_never_usrec(self, pipeline):
        pipeline.smoke = False
        targets = pipeline._selected_targets()
        assert "USREC" not in targets
        assert set(targets) == {"GDPC1", "CPIAUCSL", "UNRATE", "INDPRO", "FEDFUNDS", "M2SL"}


class TestUnitsLabelling:
    def test_growth_targets_are_annualized_percent(self, pipeline):
        assert pipeline._units("CPIAUCSL") == "annualized percent"

    def test_a_rate_in_levels_is_percent(self, pipeline):
        pipeline.decisions["UNRATE"] = SimpleNamespace(decision="level", break_date=None)
        assert pipeline._units("UNRATE") == "percent"

    def test_a_rate_in_differences_is_a_percentage_point_change(self, pipeline):
        pipeline.decisions["UNRATE"] = SimpleNamespace(decision="difference", break_date=None)
        assert pipeline._units("UNRATE") == "percentage-point change"
