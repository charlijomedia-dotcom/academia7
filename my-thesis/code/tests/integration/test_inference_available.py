"""With a long enough evaluation sample, the forecast tests must actually produce numbers.

The main pipeline integration test runs a very short out-of-sample block, which is the
right way to exercise every code path quickly but leaves HLZ and the MCS reporting
"unavailable" by their own minimum-sample rules. That proves the unavailability handling,
not the inference. This run uses one quarterly target with a long enough block for both
procedures to be computable, and asserts they are.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import pytest

from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR, FROZEN_DIR, Namespace, output_layout
from thesis.core.provenance import RunContext
from thesis.data.store import load_bundle
from thesis.pipeline import Pipeline

OVERRIDES = {
    "smoke": {"enabled": True, "targets": ["GDPC1"], "max_origins": 80},
    "forecasting": {
        "windows": {"Q": 80},
        "horizons": {"primary": {"Q": 1}, "robustness": {"Q": [2]}},
        "star_multistep": {"paths": 25},
    },
    "specification": {"ar": {"max_lag": {"Q": 2}},
                      "arma": {"max_p": {"Q": 1}, "max_q": {"Q": 1}}},
    "models": {"msar": {"lag_cap": {"Q": 1}}, "star": {"lag_cap": {"Q": 1}}},
    "robustness": {"window_lengths": {"lengths": {"Q": [70, 80, 90]},
                                      "baseline": {"Q": 80}}},
    "evaluation": {"mcs": {"replications": 200},
                   "hlz": {"critical_value_replications": 500}},
    "execution": {"cache": False},
}


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    config = load_config(names=("baseline", "series_catalog", "thresholds"),
                         config_dir=CONFIG_DIR).with_overrides(OVERRIDES, "inference-test")
    bundle = load_bundle(FROZEN_DIR, config)
    root = tmp_path_factory.mktemp("inference")
    layout = output_layout(Namespace.SMOKE)
    layout = type(layout)(root=root / "out", cache=root / "cache")
    context = RunContext(namespace=Namespace.SMOKE, config_hash=config.hash,
                         data_snapshot_hash=bundle.data_input_identity)
    pipeline = Pipeline(config, context, layout, bundle, smoke=True)
    pipeline.run()
    return layout


class TestPrimaryTestProducesNumbers:
    def test_hlz_is_computed_rather_than_reported_unavailable(self, run):
        frame = pd.read_csv(run.forecast_tests / "T3.3A_hlz_pairwise.csv")
        available = frame[frame["inference_available"]]
        assert not available.empty, "HLZ produced no computable result on 80 origins"
        assert available["statistic"].notna().all()
        assert available["p_value_two_sided"].between(0, 1).all()
        assert (available["n"] >= 10).all()

    def test_hlz_reports_the_modified_and_the_standard_long_run_variance(self, run):
        frame = pd.read_csv(run.forecast_tests / "T3.3A_hlz_pairwise.csv")
        available = frame[frame["inference_available"]]
        assert (available["omega_modified"] > 0).all()
        assert available["omega_standard"].notna().all()
        # The point of the procedure: the mean-variation ratio is reported so a reader
        # can see whether the conventional estimator was inflated here.
        assert available["mean_variation_ratio"].notna().all()

    def test_one_sided_p_values_bracket_the_two_sided_one(self, run):
        frame = pd.read_csv(run.forecast_tests / "T3.3A_hlz_pairwise.csv")
        available = frame[frame["inference_available"]]
        assert (available["p_value_upper"].between(0, 1)).all()
        assert (available["p_value_lower"].between(0, 1)).all()
        closer = np.minimum(available["p_value_upper"], available["p_value_lower"])
        assert (available["p_value_two_sided"] >= closer - 1e-9).all()

    def test_dm_hln_is_computed_and_its_agreement_recorded(self, run):
        frame = pd.read_csv(run.forecast_tests / "T3.3B_dm_hln_pairwise.csv")
        available = frame[frame["inference_available"]]
        assert not available.empty
        assert available["statistic"].notna().all()
        assert set(available["agrees_with_hlz"]) <= {"agree", "disagree"}

    def test_the_two_procedures_are_reported_separately_even_when_they_disagree(self, run):
        hlz = pd.read_csv(run.forecast_tests / "T3.3A_hlz_pairwise.csv")
        dm = pd.read_csv(run.forecast_tests / "T3.3B_dm_hln_pairwise.csv")
        # Neither table is derived from the other: same pairs, independent statistics.
        keys = ["series", "horizon", "loss", "model_a", "model_b"]
        assert set(map(tuple, hlz[keys].values)) == set(map(tuple, dm[keys].values))
        merged = hlz.merge(dm, on=keys, suffixes=("_hlz", "_dm"))
        differing = merged[merged["inference_available_hlz"] & merged["inference_available_dm"]]
        assert not differing.empty
        assert not np.allclose(differing["statistic_hlz"], differing["statistic_dm"])


class TestModelConfidenceSetProducesMembership:
    def test_the_mcs_is_computed_at_both_confidence_levels(self, run):
        frame = pd.read_csv(run.forecast_tests / "T3.4_model_confidence_set.csv")
        available = frame[frame["inference_available"]]
        assert not available.empty, "the MCS produced no computable result on 80 origins"
        assert set(available["confidence_level"]) == {0.9, 0.95}
        assert available["in_mcs"].any()

    def test_block_length_follows_the_approved_rule(self, run):
        frame = pd.read_csv(run.forecast_tests / "T3.4_model_confidence_set.csv")
        available = frame[frame["inference_available"]]
        expected = np.ceil(np.sqrt(available["t_common"]))
        assert (available["block_length"] == expected).all()
        assert set(available["method"]) == {"R"}
        assert set(available["bootstrap"]) == {"stationary"}

    def test_a_wider_confidence_set_contains_the_narrower_one(self, run):
        frame = pd.read_csv(run.forecast_tests / "T3.4_model_confidence_set.csv")
        available = frame[frame["inference_available"]]
        for (series, horizon, loss), group in available.groupby(["series", "horizon", "loss"]):
            ninety = set(group[(group["confidence_level"] == 0.9) & group["in_mcs"]]["model"])
            ninety_five = set(
                group[(group["confidence_level"] == 0.95) & group["in_mcs"]]["model"])
            assert ninety <= ninety_five, f"{series} h={horizon} {loss}"


class TestStateRegressionProducesNumbers:
    def test_the_state_loss_regression_is_estimated(self, run):
        frame = pd.read_csv(run.forecast_tests / "T3.5_state_loss_regression.csv")
        available = frame[frame["inference_available"]]
        assert not available.empty
        for column in ("alpha", "beta_rec", "beta_turn", "alpha_se", "beta_rec_p"):
            assert available[column].notna().any()
        assert available["joint_wald_p"].between(0, 1).all()
        assert set(available["hac_rule"].str.contains("Newey-West")) == {True}

    def test_window_length_robustness_reaches_a_real_verdict(self, run):
        frame = pd.read_csv(run.robustness / "window_length_predictive_tests.csv")
        assert not frame.empty
        assert frame["hlz_available"].any(), "no window length produced computable inference"
        assert set(frame["conclusion_vs_baseline"].dropna()) <= {
            "unchanged", "weakened", "reversed", "unavailable"}
