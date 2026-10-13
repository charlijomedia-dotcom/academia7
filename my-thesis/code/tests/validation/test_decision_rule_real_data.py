"""The §3.4 level-versus-difference rule, exercised on the real frozen UNRATE and FEDFUNDS.

`tests/validation/test_stationarity.py` validates the rule's logic against synthetic
series with known properties. This module checks the thing that matters for the thesis:
that the predeclared rule reaches a definite, recorded decision on the actual approved
data, on the initial estimation window, and that the full-sample confirmation either
agrees or is flagged as a disagreement rather than silently overriding it.

No result here is interpreted. Whichever way the rule falls is the rule's answer.
"""

from __future__ import annotations

import pandas as pd
import pytest

from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR, FROZEN_DIR
from thesis.data.canonical import to_panels
from thesis.data.store import load_bundle
from thesis.diagnostics.decision_rule import confirm_on_full_sample, decide_transformation

RATE_SERIES = ("UNRATE", "FEDFUNDS")


@pytest.fixture(scope="module")
def config():
    return load_config(names=("baseline", "series_catalog", "thresholds"),
                       config_dir=CONFIG_DIR)


@pytest.fixture(scope="module")
def panels(config):
    return to_panels(load_bundle(FROZEN_DIR, config).frame)


@pytest.fixture(scope="module")
def decisions(config, panels):
    out = {}
    for series_id in RATE_SERIES:
        level = panels["M"][series_id].dropna()
        window = int(config.get("forecasting.windows.M"))
        decision = decide_transformation(series_id, level.iloc[:window], "M", config)
        out[series_id] = (level, confirm_on_full_sample(decision, level, "M", config))
    return out


class TestTheRuleIsConfiguredForBothRateSeries:
    def test_both_rate_series_defer_to_the_rule_rather_than_a_fixed_transformation(self, config):
        for series_id in RATE_SERIES:
            spec = config.get(f"targets.{series_id}")
            assert spec["transform"]["kind"] == "decided_by_stationarity_rule"

    def test_the_growth_targets_do_not_use_the_rule(self, config):
        for series_id in ("GDPC1", "CPIAUCSL", "INDPRO", "M2SL"):
            spec = config.get(f"targets.{series_id}")
            assert spec["transform"]["kind"] == "logdiff_annualized"


class TestTheRuleReachesARecordedDecision:
    @pytest.mark.parametrize("series_id", RATE_SERIES)
    def test_a_definite_decision_is_reached(self, decisions, series_id):
        _, decision = decisions[series_id]
        assert decision.decision in {"level", "difference"}

    @pytest.mark.parametrize("series_id", RATE_SERIES)
    def test_the_decision_rests_on_initial_window_evidence_only(self, decisions, series_id):
        # The two stages must stay distinguishable in the record: the decision comes from
        # tests labelled as run on the initial window, and the full-sample tests are a
        # separate, separately labelled confirmation that cannot be mistaken for it.
        _, decision = decisions[series_id]
        assert decision.initial_window_results
        assert all("initial window" in r.name for r in decision.initial_window_results)
        assert all("initial window" not in r.name for r in decision.full_sample_results)
        assert all(r.series == series_id for r in decision.initial_window_results)

    @pytest.mark.parametrize("series_id", RATE_SERIES)
    def test_both_required_tests_contribute_to_the_decision(self, decisions, series_id):
        _, decision = decisions[series_id]
        names = " | ".join(r.name for r in decision.initial_window_results)
        assert "Dickey-Fuller" in names
        assert "KPSS" in names

    @pytest.mark.parametrize("series_id", RATE_SERIES)
    def test_the_row_records_everything_needed_to_audit_the_decision(self, decisions, series_id):
        _, decision = decisions[series_id]
        row = decision.to_row()
        for key in ("series_id", "baseline_transformation", "rule_branch", "reason",
                    "break_date", "break_sensitive_robustness", "full_sample_agrees",
                    "alternative_transformation_robustness_required"):
            assert key in row, key
        assert row["baseline_transformation"] == decision.decision
        assert row["rule_branch"], "the rule must record which branch it took"
        assert row["reason"], "the rule must record why"

    @pytest.mark.parametrize("series_id", RATE_SERIES)
    def test_the_alternative_transformation_is_always_a_robustness_check(self, decisions,
                                                                        series_id):
        # Whichever way the rule falls, T4.1 must still run the other transformation.
        _, decision = decisions[series_id]
        assert decision.to_row()["alternative_transformation_robustness_required"] is True

    @pytest.mark.parametrize("series_id", RATE_SERIES)
    def test_the_full_sample_confirmation_is_recorded_separately(self, decisions, series_id):
        # The confirmation may agree or disagree, but it must never silently replace the
        # initial-window decision, which is what the forecasting design is built on.
        _, decision = decisions[series_id]
        assert decision.full_sample_results
        row = decision.to_row()
        assert row["full_sample_agrees"] in (True, False, "")

    @pytest.mark.parametrize("series_id", RATE_SERIES)
    def test_the_confirmation_does_not_change_the_baseline_decision(self, config, panels,
                                                                    series_id):
        level = panels["M"][series_id].dropna()
        window = int(config.get("forecasting.windows.M"))
        before = decide_transformation(series_id, level.iloc[:window], "M", config)
        after = confirm_on_full_sample(before, level, "M", config)
        assert after.decision == before.decision, (
            "the full-sample check confirms or dissents; it never overrides")
        assert after.rule_branch == before.rule_branch

    @pytest.mark.parametrize("series_id", RATE_SERIES)
    def test_the_decision_is_deterministic(self, config, panels, series_id):
        level = panels["M"][series_id].dropna()
        window = int(config.get("forecasting.windows.M"))
        first = decide_transformation(series_id, level.iloc[:window], "M", config)
        second = decide_transformation(series_id, level.iloc[:window], "M", config)
        assert first.decision == second.decision
        assert first.to_row() == second.to_row()
