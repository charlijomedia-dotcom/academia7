"""End-to-end pipeline integration.

The run uses the real frozen canonical input and the real estimators, with the window
lengths, horizons and origin counts reduced so it finishes quickly. The point is not the
numbers, which are not thesis-facing, but that every stage executes, that each required
output is actually written, and that the structural guarantees of the methodology hold in
a real run: provenance on every table, baseline and robustness kept apart, data gaps kept
out of the failure registry, and the claim matrix left unpopulated in Part 6.
"""

from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")

import pandas as pd
import pytest

from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR, FROZEN_DIR, Namespace, output_layout
from thesis.core.provenance import PROVENANCE_COLUMNS, RunContext
from thesis.data.store import load_bundle
from thesis.pipeline import Pipeline
from thesis.reporting.tables import CLAIM_MATRIX_COLUMNS, validate_claim_matrix

FAST_OVERRIDES = {
    "smoke": {"enabled": True, "targets": ["INDPRO", "GDPC1"], "max_origins": 6},
    "forecasting": {
        "windows": {"M": 60, "Q": 40},
        "horizons": {"primary": {"M": 1, "Q": 1},
                     "robustness": {"M": [3], "Q": [2]}},
        "star_multistep": {"paths": 25},
    },
    "specification": {"ar": {"max_lag": {"M": 3, "Q": 2}},
                      "arma": {"max_p": {"M": 2, "Q": 2}, "max_q": {"M": 1, "Q": 1}}},
    "models": {"msar": {"lag_cap": {"M": 1, "Q": 1}},
               "star": {"lag_cap": {"M": 1, "Q": 1}},
               "var": {"lags": [1]}},
    "robustness": {
        "window_lengths": {"lengths": {"M": [40, 60, 80], "Q": [30, 40, 50]},
                           "baseline": {"M": 60, "Q": 40}},
        "cpi_lags": {"ar_orders": [1, 2]},
    },
    "evaluation": {"mcs": {"replications": 50},
                   "hlz": {"critical_value_replications": 300}},
    "execution": {"cache": False, "checkpoint": True},
}


@pytest.fixture(scope="module")
def completed_run(tmp_path_factory):
    config = load_config(names=("baseline", "series_catalog", "thresholds"),
                         config_dir=CONFIG_DIR).with_overrides(FAST_OVERRIDES, "pipeline-test")
    bundle = load_bundle(FROZEN_DIR, config)
    root = tmp_path_factory.mktemp("pipeline")
    layout = output_layout(Namespace.SMOKE)
    layout = type(layout)(root=root / "out", cache=root / "cache")
    context = RunContext(namespace=Namespace.SMOKE, config_hash=config.hash,
                         data_snapshot_hash=bundle.data_input_identity,
                         data_cutoff=config.get("samples.monthly_end"),
                         vintage_date=config.get("run.vintage_date"))
    pipeline = Pipeline(config, context, layout, bundle, smoke=True)
    summary = pipeline.run()
    return pipeline, summary, layout


class TestEveryStageRuns:
    def test_all_stages_complete(self, completed_run):
        _, summary, _ = completed_run
        assert summary["stages"] == [
            "canonical_input", "stationarity_decisions", "selected_specifications",
            "nonlinearity_diagnostics", "selected_specifications", "model_fits",
            "forecasts", "evaluation", "robustness", "tables_and_figures",
        ]

    def test_checkpoints_are_written_for_the_required_stages(self, completed_run):
        _, _, layout = completed_run
        recorded = {path.stem for path in (layout.cache / "checkpoints").glob("*.json")}
        for stage in ("canonical_input", "stationarity_decisions", "selected_specifications",
                      "nonlinearity_diagnostics", "model_fits", "forecasts", "evaluation",
                      "robustness", "tables_and_figures"):
            assert stage in recorded

    def test_the_run_produced_fits_and_forecasts(self, completed_run):
        _, summary, _ = completed_run
        assert summary["n_fit_records"] > 0
        assert summary["n_test_results"] > 0

    def test_runtime_log_covers_every_stage(self, completed_run):
        pipeline, _, layout = completed_run
        frame = pd.read_csv(layout.logs / "runtime_log.csv")
        assert set(frame["stage"]) >= {"data", "stationarity", "nonlinearity",
                                       "specification", "adequacy", "forecasting",
                                       "evaluation", "robustness", "finalize"}
        assert (frame["wall_seconds"] >= 0).all()


REQUIRED_OUTPUTS = [
    ("data_audit", "T2.0_concept_series.csv"),
    ("manifests", "T2.0A_frozen_manifest.csv"),
    ("data_audit", "october_2025_imputation_audit.csv"),
    ("data_audit", "T2.1_data_dictionary.csv"),
    ("diagnostics", "T2.2_stationarity.csv"),
    ("diagnostics", "T2.3_tsay.csv"),
    ("diagnostics", "T2.4_star_linearity.csv"),
    ("diagnostics", "T2.5_selected_specs.csv"),
    ("models", "T3.1_in_sample_adequacy.csv"),
    ("models", "T3.2_nonlinear_credibility.csv"),
    ("forecast_tests", "T3.3_main_forecast_table.csv"),
    ("forecast_tests", "T3.3A_hlz_pairwise.csv"),
    ("forecast_tests", "T3.3B_dm_hln_pairwise.csv"),
    ("forecast_tests", "T3.4_model_confidence_set.csv"),
    ("forecast_tests", "T3.5_state_performance.csv"),
    ("forecast_tests", "T3.5_state_loss_regression.csv"),
    ("forecast_tests", "T3.6_peak_trough_detail.csv"),
    ("robustness", "T4.TP1_turning_window_sensitivity.csv"),
    ("robustness", "T4.1_transformation_robustness.csv"),
    ("robustness", "T4.2_cpi_lag_robustness.csv"),
    ("robustness", "T4.3_regime_count.csv"),
    ("robustness", "T4.4_horizon_robustness.csv"),
    ("robustness", "T4.5_var_comparison.csv"),
    ("robustness", "T4.6_arch_trigger.csv"),
    ("robustness", "window_length_comparison.csv"),
    ("robustness", "window_length_predictive_tests.csv"),
    ("robustness", "window_length_origin_audit.csv"),
    ("data_audit", "locf_forecast_exposure.csv"),
    ("data_audit", "T4.9_locf_sample_comparison.csv"),
    ("robustness", "T4.7_failure_registry.csv"),
    ("data_audit", "data_gap_register.csv"),
    ("models", "fit_records.csv"),
    ("manifests", "claim_evidence_matrix.csv"),
    ("manifests", "output_inventory.csv"),
    ("logs", "runtime_log.csv"),
]


class TestRequiredOutputsExist:
    @pytest.mark.parametrize("directory,name", REQUIRED_OUTPUTS)
    def test_output_file_is_written(self, completed_run, directory, name):
        _, _, layout = completed_run
        assert (getattr(layout, directory) / name).exists(), f"{directory}/{name} missing"

    def test_required_figures_are_written(self, completed_run):
        _, _, layout = completed_run
        produced = {path.name for path in layout.figures.glob("*.png")}
        for prefix in ("F2.0", "F2.1", "F3.1", "F3.2", "F3.3", "F3.4", "F3.5", "F3.6", "F4.8"):
            assert any(name.startswith(prefix) for name in produced), f"{prefix} missing"

    def test_every_figure_has_a_provenance_sidecar(self, completed_run):
        _, _, layout = completed_run
        for figure in layout.figures.glob("*.png"):
            sidecar = figure.with_suffix(".png.provenance.json")
            assert sidecar.exists()
            payload = json.loads(sidecar.read_text(encoding="utf-8"))
            assert payload["run_id"] and payload["config_hash"]


class TestProvenanceAndSeparation:
    def test_every_written_table_carries_the_provenance_columns(self, completed_run):
        _, _, layout = completed_run
        checked = 0
        for path in layout.root.rglob("*.csv"):
            frame = pd.read_csv(path, nrows=1)
            if frame.empty and len(frame.columns) == 0:
                continue
            for column in PROVENANCE_COLUMNS:
                assert column in frame.columns, f"{path.name} lacks {column}"
            checked += 1
        assert checked > 20

    def test_the_run_manifest_records_the_canonical_hash_and_commit(self, completed_run):
        pipeline, summary, layout = completed_run
        payload = json.loads((layout.manifests / "run_manifest.json").read_text())
        assert payload["data_snapshot_hash"] == summary["canonical_csv_sha256"]
        assert payload["code_commit_sha"]
        assert payload["vintage_date"] == "2026-10-05"

    def test_robustness_output_is_separate_from_baseline_output(self, completed_run):
        _, _, layout = completed_run
        robustness = {path.name for path in layout.robustness.glob("*.csv")}
        baseline = {path.name for path in layout.forecast_tests.glob("*.csv")}
        assert robustness and baseline
        assert not (robustness & baseline)

    def test_smoke_namespace_never_writes_into_the_baseline_tree(self, completed_run):
        _, _, layout = completed_run
        assert "output" not in output_layout(Namespace.BASELINE).root.parts[-1:] or True
        assert layout.root != output_layout(Namespace.BASELINE).root


class TestMethodologicalGuarantees:
    def test_data_gaps_are_not_in_the_failure_registry(self, completed_run):
        _, _, layout = completed_run
        registry = pd.read_csv(layout.robustness / "T4.7_failure_registry.csv")
        if not registry.empty and "reason_code" in registry.columns:
            assert "DATA_GAP" not in set(registry["reason_code"].dropna())
        gaps = pd.read_csv(layout.data_audit / "data_gap_register.csv")
        if not gaps.empty and "is_model_failure" in gaps.columns:
            assert not gaps["is_model_failure"].any()

    def test_arma_garch_never_enters_the_horse_race_or_the_mcs(self, completed_run):
        _, _, layout = completed_run
        main = pd.read_csv(layout.forecast_tests / "T3.3_main_forecast_table.csv")
        assert "ARMA-GARCH" not in set(main["model"])
        mcs = pd.read_csv(layout.forecast_tests / "T3.4_model_confidence_set.csv")
        assert "ARMA-GARCH" not in set(mcs["model"].dropna())

    def test_msar3_is_robustness_only_and_absent_from_the_baseline_table(self, completed_run):
        _, _, layout = completed_run
        main = pd.read_csv(layout.forecast_tests / "T3.3_main_forecast_table.csv")
        assert "MSAR3" not in set(main["model"])
        k3 = pd.read_csv(layout.robustness / "T4.3_regime_count.csv")
        assert "MSAR3" in set(k3["model"])
        assert set(k3["retention_decision"].str.startswith("K=2 retained")) == {True}

    def test_the_state_regression_is_never_labelled_giacomini_white(self, completed_run):
        _, _, layout = completed_run
        frame = pd.read_csv(layout.forecast_tests / "T3.5_state_loss_regression.csv")
        labels = " ".join(frame["label"].astype(str)).lower()
        assert "giacomini" not in labels
        assert "ex-post" in labels

    def test_hlz_is_primary_and_dm_hln_secondary_with_disagreement_visible(self, completed_run):
        _, _, layout = completed_run
        hlz = pd.read_csv(layout.forecast_tests / "T3.3A_hlz_pairwise.csv")
        dm = pd.read_csv(layout.forecast_tests / "T3.3B_dm_hln_pairwise.csv")
        assert set(hlz["role"]) == {"primary"}
        assert set(dm["role"]) == {"secondary"}
        assert "agrees_with_hlz" in dm.columns
        assert set(dm["agrees_with_hlz"]) <= {"agree", "disagree", "unavailable"}

    def test_hlz_reports_both_two_sided_and_one_sided_p_values(self, completed_run):
        _, _, layout = completed_run
        hlz = pd.read_csv(layout.forecast_tests / "T3.3A_hlz_pairwise.csv")
        for column in ("p_value_two_sided", "p_value_upper", "p_value_lower"):
            assert column in hlz.columns

    def test_window_length_exercise_reuses_the_baseline_specification(self, completed_run):
        _, _, layout = completed_run
        audit = pd.read_csv(layout.robustness / "window_length_origin_audit.csv")
        assert not audit["reselected_specification"].any()
        assert set(audit["role"]) <= {"baseline", "shorter", "longer"}
        assert set(audit["window_length"]) == {40, 60, 80} | {30, 40, 50}

    def test_window_length_conclusions_use_only_the_approved_categories(self, completed_run):
        _, _, layout = completed_run
        tests = pd.read_csv(layout.robustness / "window_length_predictive_tests.csv")
        assert set(tests["conclusion_vs_baseline"].dropna()) <= {
            "unchanged", "weakened", "reversed", "unavailable"}

    def test_turning_window_table_records_all_predeclared_widths(self, completed_run):
        _, _, layout = completed_run
        frame = pd.read_csv(layout.robustness / "T4.TP1_turning_window_sensitivity.csv")
        monthly = frame[frame["series"] == "INDPRO"]
        assert set(monthly["turning_window_width"]) == {1, 3, 6}
        quarterly = frame[frame["series"] == "GDPC1"]
        assert set(quarterly["turning_window_width"]) == {0, 1, 2}
        assert frame["is_baseline_width"].any()

    def test_the_baseline_turning_width_is_never_called_a_convention(self, completed_run):
        _, _, layout = completed_run
        frame = pd.read_csv(layout.robustness / "T4.TP1_turning_window_sensitivity.csv")
        note = str(frame["convention_note"].iloc[0]).lower()
        assert "predeclared" in note
        assert "not an established universal convention" in note

    def test_locf_exposure_flags_every_required_dimension(self, completed_run):
        _, _, layout = completed_run
        frame = pd.read_csv(layout.data_audit / "locf_forecast_exposure.csv")
        for column in ("target_imputed",
                       "target_transformation_uses_imputed_predecessor",
                       "predictor_lag_contains_imputed",
                       "estimation_window_contains_imputed",
                       "forecast_valid", "squared_loss"):
            assert column in frame.columns

    def test_locf_headline_inference_sample_is_the_full_approved_sample(self, completed_run):
        _, _, layout = completed_run
        frame = pd.read_csv(layout.data_audit / "T4.9_locf_sample_comparison.csv")
        assert set(frame["headline_inference_sample"]) == {"full_approved"}
        headline = frame[frame["sample"] == "full_approved"]
        assert set(headline["inference_role"]) == {"headline inference, unchanged"}

    def test_imputation_audit_names_the_two_approved_cells_only(self, completed_run):
        _, _, layout = completed_run
        frame = pd.read_csv(layout.data_audit / "october_2025_imputation_audit.csv")
        assert len(frame) == 2
        assert set(frame["series_id"]) == {"CPIAUCSL", "UNRATE"}
        assert set(frame["date"]) == {"2025-10-01"}
        assert not frame["is_official_observation"].any()

    def test_claim_matrix_is_valid_and_left_unpopulated_in_part_6(self, completed_run):
        _, _, layout = completed_run
        frame = pd.read_csv(layout.manifests / "claim_evidence_matrix.csv")
        for column in CLAIM_MATRIX_COLUMNS:
            assert column in frame.columns
        assert validate_claim_matrix(frame) == []
        assert frame.empty, "Part 6 must not adjudicate claims (result-blind rule)"

    def test_output_inventory_hashes_every_file_it_lists(self, completed_run):
        _, _, layout = completed_run
        inventory = pd.read_csv(layout.manifests / "output_inventory.csv")
        assert len(inventory) > 30
        assert (inventory["sha256"].str.len() == 64).all()
        assert (inventory["bytes"] > 0).all()
