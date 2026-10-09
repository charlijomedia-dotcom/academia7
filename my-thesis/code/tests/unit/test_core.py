"""Core infrastructure: hashing, configuration, seeds, provenance."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from thesis.core import seeds
from thesis.core.config import Config, load_config
from thesis.core.hashing import canonical_json, combine, sha256_file, sha256_obj
from thesis.core.paths import CONFIG_DIR, Namespace, output_layout
from thesis.core.provenance import PROVENANCE_COLUMNS, DirtyTreeError, RunContext
from thesis.core.schemas import FitRecord, ReasonCode, Status, TestResult


class TestHashing:
    def test_canonical_json_is_order_independent(self):
        assert canonical_json({"a": 1, "b": 2}) == canonical_json({"b": 2, "a": 1})

    def test_sha256_obj_stable_across_equal_objects(self):
        assert sha256_obj({"x": [1, 2]}) == sha256_obj({"x": [1, 2]})
        assert sha256_obj({"x": [1, 2]}) != sha256_obj({"x": [2, 1]})

    def test_combine_is_order_independent(self):
        assert combine(["a", "b"]) == combine(["b", "a"])

    def test_sha256_file(self, tmp_path):
        path = tmp_path / "f.txt"
        path.write_text("hello", encoding="utf-8")
        assert sha256_file(path) == (
            "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        )


class TestConfig:
    def test_loads_approved_configuration(self, config):
        assert config.get("run.vintage_date") == "2026-10-05"
        assert config.get("forecasting.windows.M") == 240
        assert config.get("forecasting.windows.Q") == 120

    def test_missing_key_raises_rather_than_defaulting(self, config):
        with pytest.raises(KeyError):
            config.get("forecasting.windows.W")

    def test_explicit_default_is_allowed(self, config):
        assert config.get("forecasting.windows.W", 99) == 99

    def test_require_rejects_unset_value(self, config):
        # The HLZ tuning choices may only come from the published article (M3), so they
        # are present but null and must not be usable until supplied.
        with pytest.raises(KeyError):
            config.require("evaluation.hlz.lrv_kernel")

    def test_hash_changes_with_content(self):
        a = Config(data={"x": 1}, sources=("t",))
        b = Config(data={"x": 2}, sources=("t",))
        assert a.hash != b.hash

    def test_overrides_merge_deeply(self, config):
        merged = config.with_overrides({"forecasting": {"windows": {"M": 120}}}, "test")
        assert merged.get("forecasting.windows.M") == 120
        assert merged.get("forecasting.windows.Q") == 120  # untouched
        assert merged.hash != config.hash

    def test_smoke_overrides_load(self):
        smoke = load_config(
            names=("baseline", "series_catalog", "thresholds", "smoke"),
            config_dir=CONFIG_DIR,
        )
        assert smoke.get("smoke.targets") == ["INDPRO", "GDPC1"]
        assert smoke.get("forecasting.star_multistep.paths") == 200

    def test_approved_methodology_values_are_present_and_correct(self, config):
        # A guard against accidental edits to locked parameters.
        assert config.get("models.msar.regimes_baseline") == 2
        assert config.get("models.msar.lag_cap.M") == 4
        assert config.get("models.star.lag_cap.Q") == 2
        assert config.get("specification.ar.max_lag.M") == 12
        assert config.get("evaluation.states.turning_window_baseline.M") == 3
        assert config.get("evaluation.states.turning_window_sensitivity.M") == [1, 3, 6]
        assert config.get("robustness.cpi_lags.ar_orders") == [1, 3, 6, 12]
        assert config.get("forecasting.horizons.robustness.M") == [3, 6, 12]
        assert config.get("evaluation.mcs.block_length_rule") == "ceil_sqrt_T_common"
        assert config.get("evaluation.loss_differential") == "competitor_minus_benchmark"

    def test_arma_garch_is_excluded_from_horse_race_and_mcs(self, config):
        assert config.get("models.arma_garch.in_horse_race") is False
        assert config.get("models.arma_garch.in_mcs") is False

    def test_state_regression_is_not_labelled_giacomini_white(self, config):
        label = config.get("evaluation.state_loss_regression.label").lower()
        assert "giacomini" not in label
        assert "ex-post" in label


class TestSeeds:
    def test_seed_is_deterministic_for_a_key(self):
        a = seeds.generator({"series": "CPI", "origin": 3}, 42).normal(size=5)
        b = seeds.generator({"series": "CPI", "origin": 3}, 42).normal(size=5)
        np.testing.assert_array_equal(a, b)

    def test_different_keys_give_different_streams(self):
        a = seeds.generator({"series": "CPI", "origin": 3}, 42).normal(size=5)
        b = seeds.generator({"series": "CPI", "origin": 4}, 42).normal(size=5)
        assert not np.allclose(a, b)

    def test_seed_independent_of_key_construction_order(self):
        a = seeds.seed_entropy({"a": 1, "b": 2}, 7)
        b = seeds.seed_entropy({"b": 2, "a": 1}, 7)
        assert a == b

    def test_master_seed_changes_stream(self):
        a = seeds.seed_entropy({"k": 1}, 1)
        b = seeds.seed_entropy({"k": 1}, 2)
        assert a != b


class TestProvenance:
    def test_stamp_adds_all_required_columns(self):
        ctx = RunContext(namespace=Namespace.SMOKE, config_hash="abc123")
        stamped = ctx.stamp(pd.DataFrame({"value": [1, 2]}))
        for column in PROVENANCE_COLUMNS:
            assert column in stamped.columns

    def test_write_table_round_trip(self, tmp_path):
        ctx = RunContext(namespace=Namespace.SMOKE, config_hash="abc123")
        path = ctx.write_table(pd.DataFrame({"value": [1]}), tmp_path / "t.csv")
        written = pd.read_csv(path)
        assert written.loc[0, "config_hash"] == "abc123"
        assert written.loc[0, "run_id"].startswith("smoke-")

    def test_sidecar_written_for_figures(self, tmp_path):
        ctx = RunContext(namespace=Namespace.SMOKE, config_hash="abc123")
        sidecar = ctx.write_sidecar(tmp_path / "fig.png", {"figure_id": "F2.0"})
        assert sidecar.exists()
        assert "F2.0" in sidecar.read_text(encoding="utf-8")

    def test_baseline_run_refuses_dirty_tree(self):
        ctx = RunContext(namespace=Namespace.BASELINE, config_hash="abc", tree_dirty=True)
        with pytest.raises(DirtyTreeError):
            ctx.require_clean_tree()

    def test_non_baseline_run_tolerates_dirty_tree(self):
        ctx = RunContext(namespace=Namespace.SMOKE, config_hash="abc", tree_dirty=True)
        ctx.require_clean_tree()  # must not raise


class TestOutputNamespaces:
    def test_smoke_and_refresh_never_write_into_baseline(self):
        baseline = output_layout(Namespace.BASELINE)
        smoke = output_layout(Namespace.SMOKE)
        refresh = output_layout(Namespace.REFRESH, stamp="2026-11-01")
        assert baseline.root not in smoke.root.parents and smoke.root != baseline.root
        assert baseline.root not in refresh.root.parents and refresh.root != baseline.root
        assert smoke.cache != baseline.cache
        assert refresh.cache != baseline.cache

    def test_refresh_requires_a_stamp(self):
        with pytest.raises(ValueError):
            output_layout(Namespace.REFRESH)


class TestSchemas:
    def test_status_escalates_but_never_downgrades(self):
        record = FitRecord(
            series="CPI",
            model="MSAR",
            spec_label="p=2,K=2",
            spec_hash="h",
            window_start="1990-01-01",
            window_end="2009-12-01",
            refit_date="2009-12-01",
            converged=True,
        )
        record.add_flag(ReasonCode.LOW_OCCUPANCY, Status.FRAGILE, detail=0.03)
        assert record.status is Status.FRAGILE
        record.add_flag(ReasonCode.NONCONVERGENCE, Status.FAILED)
        assert record.status is Status.FAILED
        record.add_flag(ReasonCode.RESIDUAL_AUTOCORR, Status.FRAGILE)
        assert record.status is Status.FAILED  # never downgraded
        assert not record.usable

    def test_fit_record_row_is_flat(self):
        record = FitRecord(
            series="CPI",
            model="AR",
            spec_label="p=1",
            spec_hash="h",
            window_start="1990-01-01",
            window_end="2009-12-01",
            refit_date="2009-12-01",
            converged=True,
            params={"const": 1.5, "ar1": 0.4},
        )
        row = record.to_row()
        assert row["params"] == "ar1=0.4; const=1.5"
        assert row["status"] == "adequate"

    def test_test_result_carries_the_required_reporting_fields(self):
        result = TestResult(
            name="ADF",
            null_hypothesis="unit root",
            statistic=-3.1,
            p_value=0.03,
            reference="Dickey-Fuller",
            decision_5pct="reject",
            implication="stationary around an intercept",
            tuning={"maxlag": 12, "autolag": "BIC"},
        )
        row = result.to_row()
        for key in (
            "name",
            "null_hypothesis",
            "statistic",
            "p_value",
            "reference",
            "decision_5pct",
            "implication",
        ):
            assert key in row
        assert row["tuning"] == "autolag=BIC; maxlag=12"
