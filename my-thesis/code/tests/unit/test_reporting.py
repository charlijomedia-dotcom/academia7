"""Reporting layer: table schemas, significance marks, and figure conventions.

Figures are checked structurally rather than visually: the properties the methodology
actually fixes are the colour-to-model mapping, the presence of 95% bands, separate
panels for failed or extreme models, and the absence of axis clipping.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import pytest

from thesis.core.schemas import (DataGapEvent, FailureEvent, FitRecord, ReasonCode,
                                 Status, TestResult)
from thesis.reporting import figures, tables


@pytest.fixture
def usrec() -> pd.Series:
    index = pd.date_range("2000-01-01", periods=120, freq="MS")
    values = np.zeros(120)
    values[24:30] = 1.0
    values[80:88] = 1.0
    return pd.Series(values, index=index, name="USREC")


@pytest.fixture
def actual(usrec) -> pd.Series:
    rng = np.random.default_rng(11)
    return pd.Series(rng.normal(2.0, 1.0, size=len(usrec)), index=usrec.index, name="y")


class TestSignificanceMarks:
    def test_stars_use_only_the_approved_thresholds(self):
        # Outputs §11: superscripts only for 10/5/1 per cent.
        assert tables.stars(0.004) == "***"
        assert tables.stars(0.03) == "**"
        assert tables.stars(0.08) == "*"
        assert tables.stars(0.5) == ""

    def test_boundaries_are_strict(self):
        assert tables.stars(0.01) == "**"
        assert tables.stars(0.05) == "*"
        assert tables.stars(0.10) == ""

    def test_unavailable_p_value_gets_no_mark(self):
        assert tables.stars(None) == ""
        assert tables.stars(float("nan")) == ""

    def test_with_stars_adds_a_column_without_touching_the_p_values(self):
        frame = pd.DataFrame({"p_value": [0.001, 0.2, None]})
        marked = tables.with_stars(frame)
        assert list(marked["stars"]) == ["***", "", ""]
        pd.testing.assert_series_equal(marked["p_value"], frame["p_value"])

    def test_with_stars_is_a_no_op_when_the_column_is_absent(self):
        frame = pd.DataFrame({"x": [1]})
        assert "stars" not in tables.with_stars(frame).columns


class TestTableSchemas:
    def test_test_table_carries_every_required_reporting_field(self):
        result = TestResult(
            name="ADF", null_hypothesis="unit root", statistic=-3.5, p_value=0.01,
            reference="Dickey-Fuller", decision_5pct="reject",
            implication="stationary", tuning={"maxlag": 12})
        frame = tables.test_table([result])
        for column in ("name", "null_hypothesis", "statistic", "p_value", "reference",
                       "decision_5pct", "implication", "tuning", "stars"):
            assert column in frame.columns

    def test_test_table_of_nothing_is_empty_rather_than_fabricated(self):
        frame = tables.test_table([])
        assert frame.empty

    def test_failure_registry_has_one_row_per_event_with_the_required_columns(self):
        events = [
            FailureEvent(series="CPIAUCSL", model="MSAR", refit_date="2010-01-01",
                         horizon=1, category=Status.FAILED,
                         reason_code=ReasonCode.EMPTY_REGIME,
                         raw_diagnostic="occupancy 0.001", forecast_retained=False,
                         figure_separated=True),
            FailureEvent(series="CPIAUCSL", model="STAR", refit_date="2010-02-01",
                         horizon=None, category=Status.FRAGILE,
                         reason_code=ReasonCode.STAR_GAMMA_BOUND,
                         raw_diagnostic="gamma at bound", forecast_retained=True,
                         figure_separated=False),
        ]
        frame = tables.failure_registry_table(events)
        assert len(frame) == 2
        for column in ("series", "model", "refit_date", "horizon", "category",
                       "reason_code", "raw_diagnostic", "forecast_retained",
                       "figure_separated"):
            assert column in frame.columns

    def test_failure_registry_schema_survives_an_empty_run(self):
        # An empty registry must still be a valid, readable table: "no failures" is a
        # result, not a missing output.
        frame = tables.failure_registry_table([])
        assert "reason_code" in frame.columns

    def test_data_gaps_are_a_separate_register_from_failures(self):
        gaps = [DataGapEvent("CPIAUCSL", "AR", "2025-11-01", None,
                             ("2025-10-01",), "estimation_window", "missing observation")]
        frame = tables.data_gap_table(gaps)
        assert len(frame) == 1
        assert "reason_code" not in frame.columns
        assert "is_model_failure" in frame.columns
        assert bool(frame.loc[0, "is_model_failure"]) is False

    def test_fit_records_table_is_flat(self):
        record = FitRecord(series="GDPC1", model="AR", spec_label="AR(p=1)", spec_hash="h",
                           window_start="1990-01-01", window_end="2019-12-01",
                           refit_date="2019-12-01", converged=True,
                           params={"const": 1.0, "ar1": 0.3})
        frame = tables.fit_records_table([record])
        assert frame.loc[0, "params"] == "ar1=0.3; const=1"
        assert frame.loc[0, "status"] == "adequate"

    def test_concept_to_series_table_reports_rejected_candidates_too(self):
        catalog = [
            {"concept": "prices", "series_id": "CPIAUCSL", "retained": True,
             "source": "BLS", "rationale": "headline index"},
            {"concept": "prices", "series_id": "PCEPI", "retained": False,
             "source": "BEA", "rationale": "not the approved measure"},
        ]
        frame = tables.concept_to_series_table(catalog)
        assert len(frame) == 2
        assert set(frame["retained"]) == {True, False}

    def test_frozen_manifest_table_includes_the_derived_canonical_input_row(self):
        class Entry:
            series_id = "INDPRO"
            file_name = "INDPRO.json"
            units = "Index"
            seasonal_adjustment = "SA"
            first_observation_date = "1919-01-01"
            last_observation_date = "2026-08-01"
            source_institution = "Federal Reserve Board"
            row_count = 1292
            missing_value_dates: tuple = ()
            request_params = {"series_id": "INDPRO"}
            sha256 = "a" * 64
            retrieval_timestamp_utc = "2026-10-05T00:00:00Z"
            vintage_date = "2026-10-05"

        class Manifest:
            entries = [Entry()]

            def entry(self, series_id):
                return Entry()

        frame = tables.frozen_manifest_table(Manifest(), {
            "csv_file": "thesis_input_2026-10-05.csv", "csv_sha256": "b" * 64,
            "row_count": 1, "vintage_date": "2026-10-05",
            "created_utc": "2026-10-13T00:00:00Z",
            "parent_source_snapshot_hash": "c" * 64})
        kinds = set(frame["input_kind"])
        assert "original_source" in kinds
        assert "author_processed_canonical_input" in kinds
        derived = frame[frame["input_kind"] == "author_processed_canonical_input"].iloc[0]
        assert derived["parent_source_snapshot_hash"] == "c" * 64
        assert derived["request_parameters"].startswith("not applicable")


class TestClaimMatrix:
    def test_schema_has_every_required_column(self):
        frame = tables.empty_claim_matrix()
        for column in ("claim_id", "claim_text_stub", "target", "supporting_output_files",
                       "baseline_result", "robustness_result", "status",
                       "jury_ids_addressed"):
            assert column in frame.columns

    def test_valid_statuses_pass_validation(self):
        frame = pd.DataFrame([{
            "claim_id": "C1", "claim_text_stub": "stub", "target": "GDPC1",
            "supporting_output_files": "output/forecast_tests/T3.3_main_forecast_table.csv",
            "baseline_result": "", "robustness_result": "", "status": "SUPPORTED",
            "jury_ids_addressed": "J-01"}])
        assert tables.validate_claim_matrix(frame) == []

    def test_an_invented_status_is_rejected(self):
        frame = pd.DataFrame([{
            "claim_id": "C1", "claim_text_stub": "s", "target": "t",
            "supporting_output_files": "f", "baseline_result": "",
            "robustness_result": "", "status": "PROBABLY",
            "jury_ids_addressed": ""}])
        problems = tables.validate_claim_matrix(frame)
        assert problems and "PROBABLY" in problems[0]

    def test_a_missing_column_is_reported(self):
        problems = tables.validate_claim_matrix(pd.DataFrame({"claim_id": ["C1"]}))
        assert any("claim_text_stub" in p for p in problems)


class TestFigureConventions:
    def test_model_colours_are_fixed_and_never_cycled(self):
        # A filter that changes the model count must not repaint the survivors.
        assert figures.MODEL_COLOURS["AR"] != figures.MODEL_COLOURS["ARMA"]
        assert len(set(figures.MODEL_COLOURS.values())) == len(figures.MODEL_COLOURS)
        for model in ("AR", "ARMA", "MSAR", "MSAR3", "STAR", "VAR"):
            assert model in figures.MODEL_COLOURS

    def test_every_model_has_a_secondary_non_colour_encoding(self):
        for model in figures.MODEL_COLOURS:
            assert model in figures.MODEL_STYLES

    def test_recession_shading_adds_one_span_per_recession(self, usrec):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        figures.shade_recessions(ax, usrec)
        assert len(ax.patches) == 2
        plt.close(fig)

    def test_series_overview_uses_one_panel_per_unit(self, actual, usrec):
        fig = figures.series_overview(
            actual.cumsum() + 100, actual, usrec, series_id="INDPRO",
            level_units="Index", transformed_units="annualized percent")
        assert len(fig.axes) == 2          # never a shared axis across units
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_residual_acf_draws_95_percent_bands(self):
        rng = np.random.default_rng(5)
        fig = figures.residual_acf(rng.normal(size=300), series_id="GDPC1", model="AR")
        ax = fig.axes[0]
        # Two horizontal band lines at +/- 1.96/sqrt(n).
        horizontal = [line for line in ax.lines
                      if len(set(np.round(line.get_ydata(), 12))) == 1]
        assert len(horizontal) >= 2
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_flagged_models_go_to_their_own_panel_and_nothing_is_clipped(self, actual, usrec):
        good = actual + 0.1
        exploding = actual.copy()
        exploding.iloc[-1] = 1e6
        fig = figures.actual_vs_forecast(
            actual, {"AR": good, "ARMA": good, "STAR": exploding}, usrec,
            series_id="INDPRO", units="annualized percent",
            flagged={"STAR": exploding.iloc[[-1]]})
        assert len(fig.axes) == 2, "a flagged model must get a separate panel"
        lower = fig.axes[1]
        bottom, top = lower.get_ylim()
        assert top >= 1e6, "the extreme value must remain visible, never clipped"
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_no_separate_panel_when_nothing_is_flagged(self, actual, usrec):
        fig = figures.actual_vs_forecast(actual, {"AR": actual + 0.1}, usrec,
                                         series_id="INDPRO", units="percent")
        assert len(fig.axes) == 1
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_window_length_sensitivity_marks_the_baseline_length(self):
        table = pd.DataFrame([
            {"model": m, "window_length": w, "oos_r2_vs_benchmark": 0.01 * i,
             "n": 100, "rmse": 1.0}
            for i, (m, w) in enumerate([(m, w) for m in ("AR", "ARMA", "MSAR")
                                        for w in (180, 240, 300)])])
        fig = figures.window_length_sensitivity(table, series_id="INDPRO",
                                                baseline_length=240)
        text = " ".join(t.get_text() for t in fig.axes[0].texts) + \
            " ".join(str(label.get_text()) for label in fig.axes[0].get_xticklabels()) + \
            (fig.axes[0].get_legend().get_title().get_text()
             if fig.axes[0].get_legend() else "")
        assert "240" in text or "baseline" in text.lower()
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_figure_identifiers_containing_dots_are_not_truncated(self, tmp_path):
        # The required identifiers are F2.0, F3.1, F4.8 and so on. Path.with_suffix would
        # read ".0_sample_timeline" as the extension and collapse every F2.x figure onto
        # one file, silently overwriting outputs.
        import matplotlib.pyplot as plt

        names = ["F2.0_sample_timeline", "F2.1_INDPRO", "F3.1_INDPRO_AR", "F4.8_GDPC1"]
        for name in names:
            fig, ax = plt.subplots()
            ax.plot([0, 1], [0, 1])
            figures.save(fig, tmp_path / name)
        produced = {path.stem for path in tmp_path.glob("*.png")}
        assert produced == set(names)

    def test_saved_figures_are_byte_reproducible_across_runs(self, tmp_path):
        # PDF and SVG embed a creation timestamp, so two runs of the same analysis would
        # otherwise produce artifacts that differ for no checkable reason. A reviewer must
        # be able to verify a figure by checksum the way the tables already can be.
        import hashlib
        import time

        import matplotlib.pyplot as plt

        digests = []
        for run in range(2):
            fig, ax = plt.subplots()
            ax.plot([0, 1, 2], [0, 1, 4])
            figures.save(fig, tmp_path / f"run{run}")
            time.sleep(1.1)          # force a different clock second
            digests.append({
                suffix: hashlib.sha256(
                    (tmp_path / f"run{run}.{suffix}").read_bytes()).hexdigest()
                for suffix in ("png", "pdf")
            })
        assert digests[0]["png"] == digests[1]["png"]
        assert digests[0]["pdf"] == digests[1]["pdf"]

    def test_save_writes_every_required_format_with_a_provenance_sidecar(self, tmp_path):
        from thesis.core.paths import Namespace
        from thesis.core.provenance import RunContext

        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])
        context = RunContext(namespace=Namespace.SMOKE, config_hash="abc")
        written = figures.save(fig, tmp_path / "fig", context, {"figure_id": "F9.9"})
        suffixes = {path.suffix for path in written}
        assert ".png" in suffixes and ".pdf" in suffixes
        sidecars = list(tmp_path.glob("*.provenance.json"))
        assert sidecars and "F9.9" in sidecars[0].read_text(encoding="utf-8")
        plt.close(fig)
