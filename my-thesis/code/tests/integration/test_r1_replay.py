"""R1 cache replay: complete chains are replayed whole, and nothing is ever estimated.

A chain is replayable only if every origin's exact key is in the original fit cache.
A missing payload, a payload for fewer horizons, or an R1 re-estimate found in the
original cache makes the chain unavailable; the estimator is never reached. Warm-started
chains report the origins after the first miss as unknown, because their keys depend on
the parameters a refit would produce.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from thesis.core.cache import FitCache
from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR
from thesis.correction import guard
from thesis.correction.replay import classify_chain, pending_reason
from thesis.correction.rescore import REFIT_MARKER, PublishedRescorer, RefitCache
from thesis.forecasting import rolling
from thesis.forecasting.parallel import ChainJob
from thesis.forecasting.rolling import DataIdentity, run_chain
from thesis.models import ar as ar_module
from thesis.models import registry
from thesis.models.registry import AR, STAR, ModelSpec

IDENTITY = DataIdentity(canonical_hash="a" * 64, source_manifest_hash="b" * 64,
                        code_hash="c" * 64, config_hash="d" * 64)


@pytest.fixture(scope="module")
def series() -> pd.Series:
    rng = np.random.default_rng(5)
    n = 140
    y = np.zeros(n)
    for t in range(1, n):
        y[t] = 0.5 * y[t - 1] + rng.normal(0, 1)
    return pd.Series(y, index=pd.date_range("1990-01-01", periods=n, freq="MS"))


@pytest.fixture(scope="module")
def config():
    return load_config(names=("baseline", "series_catalog", "thresholds"),
                       config_dir=CONFIG_DIR).with_overrides(
        {"forecasting": {"star_multistep": {"paths": 20}}}, "r1-replay")


def _job(series, spec, origins=6):
    return ChainJob(tag=spec.model, series_name="S", y=series, spec=spec, horizons=(1,),
                    window_length=110, frequency="M", transformation="pct",
                    max_origins=origins, task_id=f"T4.1:S|{spec.model}")


def _populate(series, config, cache, spec, origins=6):
    with guard.estimation_forbidden(), guard.allowed():
        return run_chain("S", series, spec, [1], 110, config, identity=IDENTITY, cache=cache,
                         max_origins=origins, transformation="pct")


def _replayer(config, cache):
    return SimpleNamespace(use_cache=True, cache=cache, config=config, identity=IDENTITY)


def _payload_files(cache):
    return sorted(p for p in cache.directory.rglob("*.json"))


# -- the guard -----------------------------------------------------------------------

def test_guard_blocks_every_estimator_and_restores_them(series, config):
    with guard.estimation_forbidden() as state:
        for call in (lambda: registry.fit_and_forecast(ModelSpec(AR, order=1),
                                                       series.iloc[:110], [1], config),
                     lambda: rolling.fit_and_forecast(ModelSpec(AR, order=1),
                                                      series.iloc[:110], [1], config),
                     lambda: ar_module.fit_ar(series.iloc[:110], 1)):
            with pytest.raises(guard.EstimationForbidden):
                call()
        with guard.allowed():
            registry.fit_and_forecast(ModelSpec(AR, order=1), series.iloc[:110], [1], config)
        assert state.permitted.get("fit_and_forecast") == 1
    assert not getattr(registry.fit_and_forecast, "_r1_guard", False)
    assert not getattr(rolling.fit_and_forecast, "_r1_guard", False)


# -- replay --------------------------------------------------------------------------

def test_a_complete_chain_replays_whole_without_estimation(series, config, tmp_path):
    cache = FitCache(tmp_path, enabled=True)
    original = _populate(series, config, cache, ModelSpec(AR, order=2))
    job = _job(series, ModelSpec(AR, order=2))
    with guard.estimation_forbidden() as state:
        assessment = classify_chain(job, cache, IDENTITY, config)
        chain = PublishedRescorer._replay_from_cache(_replayer(config, cache), job)
    assert assessment.complete and assessment.hit == 6
    assert chain is not None and chain.from_cache == 6
    assert state.permitted == {}
    pd.testing.assert_frame_equal(chain.forecasts, original.forecasts)


def test_a_missing_origin_makes_the_chain_unavailable_not_refitted(series, config, tmp_path):
    cache = FitCache(tmp_path, enabled=True)
    _populate(series, config, cache, ModelSpec(AR, order=2))
    files = _payload_files(cache)
    files[3].unlink()
    before = len(_payload_files(cache))
    job = _job(series, ModelSpec(AR, order=2))
    with guard.estimation_forbidden() as state:
        assessment = classify_chain(job, cache, IDENTITY, config)
        chain = PublishedRescorer._replay_from_cache(_replayer(config, cache), job)
    assert not assessment.complete and assessment.miss == 1 and assessment.hit == 5
    assert assessment.unknown_after_miss == 0          # AR keys do not depend on a refit
    assert chain is None
    assert state.permitted == {}
    assert len(_payload_files(cache)) == before         # nothing written to the cache


def test_a_reestimated_payload_in_the_original_cache_is_rejected(series, config, tmp_path):
    cache = FitCache(tmp_path, enabled=True)
    _populate(series, config, cache, ModelSpec(AR, order=2))
    target = _payload_files(cache)[0]
    payload = json.loads(target.read_text())
    payload[REFIT_MARKER] = "re-estimated"
    target.write_text(json.dumps(payload))
    job = _job(series, ModelSpec(AR, order=2))
    with guard.estimation_forbidden():
        assessment = classify_chain(job, cache, IDENTITY, config)
        chain = PublishedRescorer._replay_from_cache(_replayer(config, cache), job)
    assert assessment.refit_rejected == 1 and not assessment.complete
    assert chain is None


@pytest.mark.slow
def test_warm_started_chain_counts_unknown_origins_after_a_miss(series, config, tmp_path):
    cache = FitCache(tmp_path, enabled=True)
    spec = ModelSpec(STAR, order=1, kind="LSTAR", delay=1)
    _populate(series, config, cache, spec, origins=5)
    job = _job(series, spec, origins=5)
    # payloads are written origin by origin: the second-written is the second origin
    by_write = sorted(_payload_files(cache), key=lambda p: p.stat().st_mtime_ns)
    with guard.estimation_forbidden():
        assert classify_chain(job, cache, IDENTITY, config).complete
        by_write[1].unlink()
        assessment = classify_chain(job, cache, IDENTITY, config)
        chain = PublishedRescorer._replay_from_cache(_replayer(config, cache), job)
    assert (assessment.hit, assessment.miss, assessment.unknown_after_miss) == (1, 1, 3)
    assert chain is None


# -- the refit checkpoint store -----------------------------------------------------

def test_refit_cache_marks_every_payload_and_explains_itself(series, config, tmp_path):
    refit = RefitCache(tmp_path / "refit" / "fits")
    _populate(series, config, refit, ModelSpec(AR, order=1), origins=3)
    payloads = _payload_files(refit)
    assert len(payloads) == 3
    assert all(json.loads(p.read_text())[REFIT_MARKER] == "re-estimated" for p in payloads)
    assert (refit.directory / "README_R1_REFIT_CACHE.txt").exists()


def test_refit_cache_resumes_an_interrupted_chain(series, config, tmp_path):
    refit = RefitCache(tmp_path / "refit" / "fits")
    _populate(series, config, refit, ModelSpec(AR, order=1), origins=3)   # "interrupted"
    resumed = _populate(series, config, refit, ModelSpec(AR, order=1), origins=6)
    assert resumed.from_cache == 3 and resumed.attempted == 6


def test_pending_rules_select_exactly_the_affected_chains():
    assert pending_reason("T4.2:CPIAUCSL|AR(p=12)")
    assert pending_reason("T4.1:FEDFUNDS|MSAR")
    assert pending_reason("T4.8:UNRATE|180:STAR")
    assert pending_reason("T4.8:UNRATE|300:AR")
    assert pending_reason("T4.8:UNRATE|240:AR") is None
    assert pending_reason("T4.8:CPIAUCSL|180:MSAR") is None
