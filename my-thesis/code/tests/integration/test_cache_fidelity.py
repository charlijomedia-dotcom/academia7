"""A fit served from the cache must be reported exactly as when it was estimated.

Before this test the cache payload kept the numbers but not the rest of the fit record:
standard errors, optimizer message, the diagnostics behind each flag and the estimator's
specification label were blank for cache-served fits, so the fit records and the
failure registry of a run resumed from a restored cache differed from an uninterrupted
run's (the forecasts did not). Asserted here: a chain served wholly or partly from the
cache produces fit records and failure events identical to a fresh one.
"""

from __future__ import annotations

import math
import random

import numpy as np
import pandas as pd
import pytest

from thesis.core.cache import FitCache
from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR
from thesis.forecasting.rolling import DataIdentity, _decode, _encode, run_chain
from thesis.models.registry import MSAR, MSAR3, STAR, ModelSpec

IDENTITY = DataIdentity(canonical_hash="a" * 64, source_manifest_hash="b" * 64,
                        code_hash="c" * 64, config_hash="d" * 64)


@pytest.fixture(scope="module")
def series() -> pd.Series:
    rng = np.random.default_rng(11)
    n = 150
    y = np.zeros(n)
    for t in range(1, n):
        y[t] = (2.0 if (t // 30) % 2 else -1.0) + 0.3 * y[t - 1] + rng.normal(0, 1)
    return pd.Series(y, index=pd.date_range("1995-01-01", periods=n, freq="MS"))


@pytest.fixture(scope="module")
def config():
    return load_config(names=("baseline", "series_catalog", "thresholds"),
                       config_dir=CONFIG_DIR).with_overrides(
        {"forecasting": {"star_multistep": {"paths": 20}}}, "cache-fidelity")


def rows(result):
    out = []
    for record in result.fit_records:
        row = record.to_row()
        row.pop("wall_seconds")
        out.append(row)
    return out


def events(result):
    return [e.to_row() for e in result.failures]


SPECS = [ModelSpec(MSAR, order=1, k_regimes=2), ModelSpec(MSAR3, order=1, k_regimes=3),
         ModelSpec(STAR, order=1, kind="LSTAR", delay=1)]


@pytest.mark.parametrize("spec", SPECS, ids=lambda s: s.model)
def test_a_wholly_cached_chain_reports_identically(series, config, tmp_path, spec):
    cache = FitCache(tmp_path, enabled=True)
    run = lambda: run_chain("S", series, spec, [1, 3], 110, config, identity=IDENTITY,
                            cache=cache, max_origins=4, transformation="pct")
    fresh = run()
    cached = run()
    assert cached.from_cache == cached.attempted == 4
    assert rows(cached) == rows(fresh)
    assert events(cached) == events(fresh)
    assert any(r["diagnostics"] for r in rows(cached))
    pd.testing.assert_frame_equal(cached.forecasts, fresh.forecasts)


def test_a_partly_restored_cache_reports_identically(series, config, tmp_path):
    """The recovery case: some fits restored, the rest estimated again."""
    spec = ModelSpec(MSAR, order=1, k_regimes=2)
    cache = FitCache(tmp_path, enabled=True)
    run = lambda: run_chain("S", series, spec, [1, 3], 110, config, identity=IDENTITY,
                            cache=cache, max_origins=5, transformation="pct")
    fresh = run()
    files = sorted(tmp_path.rglob("*.json"))
    random.Random(3).shuffle(files)
    for path in files[:2]:
        path.unlink()                                     # lost with the terminated VM
    resumed = run()
    assert 0 < resumed.from_cache < resumed.attempted
    assert rows(resumed) == rows(fresh)
    assert events(resumed) == events(fresh)
    pd.testing.assert_frame_equal(resumed.forecasts, fresh.forecasts)


@pytest.mark.parametrize("value", [
    1.5, float("nan"), np.float64(0.1 + 0.2), 3, np.int64(7), True, np.bool_(False),
    "text", None, (1, "a", 2.5), [1, (2, 3)], {"k": (1, np.float64(2.0))},
    np.float32(0.25), np.array([1.0, 2.0]), {"k": (1, np.float64(2.0))}])
def test_encoding_prints_identically(value):
    import json

    decoded = _decode(json.loads(json.dumps(_encode(value))))
    if isinstance(value, float) and math.isnan(value):
        assert math.isnan(decoded)
        return
    assert str(decoded) == str(value)
    assert isinstance(decoded, float) == isinstance(value, float)
