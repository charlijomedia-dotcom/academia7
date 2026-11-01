"""The cache-completeness walker (tools/cache_completeness.py) must agree with the rolling
engine: every origin the engine would serve from the cache is a hit, a deleted fit is a
miss, and after a missing warm-started fit the rest of the chain is reported as unknown.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from thesis.core.cache import FitCache
from thesis.core.config import load_config
from thesis.core.paths import CODE_ROOT, CONFIG_DIR
from thesis.forecasting.parallel import ChainJob
from thesis.forecasting.rolling import DataIdentity, _cache_key, run_chain
from thesis.forecasting.windows import estimation_origins
from thesis.models.registry import ModelSpec

spec_ = importlib.util.spec_from_file_location("cache_completeness",
                                               CODE_ROOT / "tools" / "cache_completeness.py")
completeness = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(completeness)


@pytest.fixture(scope="module")
def config():
    return load_config(names=("baseline", "series_catalog", "thresholds"), config_dir=CONFIG_DIR)


def _series():
    rng = np.random.default_rng(5)
    index = pd.date_range("1990-01-01", periods=70, freq="MS")
    regime = (np.arange(70) // 12) % 2
    return pd.Series(1.0 + 2.0 * regime + rng.normal(0, 0.5, 70), index=index, name="SIM")


IDENTITY = DataIdentity(canonical_hash="c", source_manifest_hash="s", code_hash="k",
                        config_hash="g")


def _job(model, order=1):
    return ChainJob(tag=model, series_name="SIM", y=_series(),
                    spec=ModelSpec(model=model, order=order), horizons=(1, 3),
                    window_length=60, frequency="M", transformation="level",
                    max_origins=5, task_id=f"SIM|{model}")


@pytest.mark.parametrize("model", ["AR", "MSAR"])
def test_walker_agrees_with_the_engine(tmp_path, config, model):
    cache = FitCache(tmp_path / "fits")
    job = _job(model)
    run_chain(job.series_name, job.y, job.spec, job.horizons, job.window_length, config,
              transformation=job.transformation, identity=IDENTITY, cache=cache,
              max_origins=job.max_origins)
    pipeline = SimpleNamespace(cache=cache, identity=IDENTITY)
    row = completeness.walk(job, pipeline, config)
    assert row["hit"] == row["n_origins"] == 5 and row["miss"] == 0

    origins = estimation_origins(job.y.index, 60, (1, 3), max_origins=5)
    cache.path_for(_cache_key(IDENTITY, "SIM", "level", job.spec, origins[0], "")).unlink()
    row = completeness.walk(job, pipeline, config)
    assert row["miss"] == 1 and row["first_miss"] == origins[0].origin_date.strftime("%Y-%m-%d")
    if model == "AR":            # no warm start: later keys stay exact
        assert row["hit"] == 4 and row["unknown_after_miss"] == 0
    else:                        # warm-started: the rest of the chain is unknown
        assert row["hit"] == 0 and row["unknown_after_miss"] == 4
