"""The fit cache must not serve a payload that lacks a requested horizon.

The cache key identifies a fitted model by its data, specification, estimation window and
warm-start predecessor — deliberately not by the horizon set, so a run asking for h=1 can
reuse a fit produced when h=1,3,6,12 were requested. That reuse is only sound if two
things hold, and both are asserted here:

1. a payload is reused only when it covers every requested horizon, so a narrower cached
   payload causes a refit instead of a missing forecast silently read as NaN;
2. a forecast at horizon h does not depend on which other horizons were requested
   alongside it, so the reused value equals the value a dedicated run would produce.

The second is the substantive one. AR, ARMA and MSAR iterate or recurse
deterministically. The STAR residual bootstrap draws one block of shocks per step from a
seeded stream, so its first h means are identical whether 3 or 12 steps were simulated —
prefix stability, asserted below rather than assumed.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from thesis.core.cache import FitCache
from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR
from thesis.forecasting.rolling import DataIdentity, _covers, run_chain
from thesis.forecasting.simulate import star_bootstrap_forecast
from thesis.models.registry import AR, ARMA, MSAR, STAR, ModelSpec
from thesis.models.star import fit_star

IDENTITY = DataIdentity(canonical_hash="a" * 64, source_manifest_hash="b" * 64,
                        code_hash="c" * 64, config_hash="d" * 64)


@pytest.fixture(scope="module")
def config():
    return load_config(names=("baseline", "series_catalog", "thresholds"),
                       config_dir=CONFIG_DIR).with_overrides(
        {"forecasting": {"star_multistep": {"paths": 50}}}, "cache-horizon-test")


@pytest.fixture(scope="module")
def series():
    rng = np.random.default_rng(606)
    n = 220
    y = np.zeros(n)
    for t in range(1, n):
        y[t] = 0.45 * y[t - 1] + rng.normal(0, 1.0)
    return pd.Series(y, index=pd.date_range("1995-01-01", periods=n, freq="MS"), name="T")


class TestCoveragePredicate:
    def test_a_payload_covering_more_horizons_serves_fewer(self):
        assert _covers({"horizons": [1, 3, 6, 12]}, [1])
        assert _covers({"horizons": [1, 3, 6, 12]}, [1, 3])
        assert _covers({"horizons": [1, 3]}, [1, 3])

    def test_a_payload_missing_a_requested_horizon_does_not_serve_it(self):
        assert not _covers({"horizons": [1, 3]}, [1, 3, 6])
        assert not _covers({"horizons": [1]}, [3])

    def test_a_payload_without_the_field_is_never_trusted(self):
        # Written before the field existed: refit rather than guess what it covers.
        assert not _covers({}, [1])
        assert not _covers({"horizons": None}, [1])
        assert not _covers({"horizons": "1,3"}, [1])


class TestCacheBehaviourEndToEnd:
    def test_a_narrower_cached_run_forces_a_refit_rather_than_nan(self, config, series,
                                                                  tmp_path):
        cache = FitCache(tmp_path / "narrow", enabled=True)
        spec = ModelSpec(AR, order=1)
        first = run_chain("T", series, spec, [1], 120, config, frequency="M",
                          identity=IDENTITY, cache=cache, max_origins=5)
        assert first.from_cache == 0

        second = run_chain("T", series, spec, [1, 3], 120, config, frequency="M",
                           identity=IDENTITY, cache=cache, max_origins=5)
        assert second.cache_horizon_misses == 5, "every origin should have been refitted"
        assert second.from_cache == 0
        h3 = second.forecasts[second.forecasts["horizon"] == 3]
        assert not h3.empty
        assert np.isfinite(h3["forecast"]).all(), "h=3 must be computed, never left NaN"

    def test_a_wider_cached_run_is_reused_for_fewer_horizons(self, config, series,
                                                             tmp_path):
        cache = FitCache(tmp_path / "wide", enabled=True)
        spec = ModelSpec(AR, order=1)
        run_chain("T", series, spec, [1, 3, 6], 120, config, frequency="M",
                  identity=IDENTITY, cache=cache, max_origins=5)
        reused = run_chain("T", series, spec, [1], 120, config, frequency="M",
                           identity=IDENTITY, cache=cache, max_origins=5)
        assert reused.from_cache == 5
        assert reused.cache_horizon_misses == 0

    @pytest.mark.parametrize("spec", [
        ModelSpec(AR, order=1),
        ModelSpec(ARMA, order=1, ma_order=1),
        ModelSpec(MSAR, order=1, k_regimes=2),
        ModelSpec(STAR, order=1, kind="LSTAR", delay=1),
    ], ids=["AR", "ARMA", "MSAR", "STAR"])
    def test_a_reused_forecast_equals_a_freshly_computed_one(self, config, series,
                                                             tmp_path, spec):
        # The substantive guarantee: reuse across horizon sets changes nothing numerically.
        wide = FitCache(tmp_path / f"wide_{spec.model}", enabled=True)
        run_chain("T", series, spec, [1, 3, 6], 120, config, frequency="M",
                  identity=IDENTITY, cache=wide, max_origins=4)
        reused = run_chain("T", series, spec, [1, 3], 120, config, frequency="M",
                           identity=IDENTITY, cache=wide, max_origins=4)
        fresh = run_chain("T", series, spec, [1, 3], 120, config, frequency="M",
                          identity=IDENTITY, cache=None, max_origins=4)
        assert reused.from_cache == 4
        left = reused.forecasts.sort_values(["origin_date", "horizon"]).reset_index(drop=True)
        right = fresh.forecasts.sort_values(["origin_date", "horizon"]).reset_index(drop=True)
        pd.testing.assert_series_equal(left["forecast"], right["forecast"],
                                       check_exact=False, rtol=0, atol=0)


class TestStarBootstrapPrefixStability:
    def test_the_first_h_means_do_not_depend_on_the_longest_horizon(self, config, series):
        fit = fit_star(series, 1, 1, "LSTAR", config, series="T", refit_date="2013-04-01")
        values = series.to_numpy(dtype=float)
        key = {"series": "T", "model": "STAR", "origin": "2013-04-01"}
        twelve, _ = star_bootstrap_forecast(fit, values, 12, paths=200, seed_key=key,
                                            master_seed=20261005)
        for horizon in (1, 3, 6):
            shorter, _ = star_bootstrap_forecast(fit, values, horizon, paths=200,
                                                 seed_key=key, master_seed=20261005)
            np.testing.assert_array_equal(twelve[:horizon], shorter)

    def test_a_different_origin_gives_a_different_stream(self, config, series):
        fit = fit_star(series, 1, 1, "LSTAR", config, series="T", refit_date="2013-04-01")
        values = series.to_numpy(dtype=float)
        a, _ = star_bootstrap_forecast(fit, values, 6, paths=200,
                                       seed_key={"series": "T", "origin": "2013-04-01"},
                                       master_seed=20261005)
        b, _ = star_bootstrap_forecast(fit, values, 6, paths=200,
                                       seed_key={"series": "T", "origin": "2013-05-01"},
                                       master_seed=20261005)
        assert not np.allclose(a, b)
