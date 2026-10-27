"""The shared-pool scheduler must change the speed and nothing else.

Asserted on real fits (AR, ARMA, MSAR, MSAR3, STAR including its simulated multi-step
forecasts): results identical to the serial run and to the old one-pool-per-batch design;
a chain the serial design serves from the cache still is, after its prerequisite; the
most expensive ready chain starts first; failures surface where they are consumed; and
an interrupted run stops promptly.
"""

from __future__ import annotations

import io
import multiprocessing
import time

import numpy as np
import pandas as pd
import pytest

import thesis.forecasting.rolling as rolling
from thesis.core.cache import FitCache
from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR
from thesis.forecasting.parallel import ChainJob, run_chains
from thesis.forecasting.rolling import DataIdentity
from thesis.forecasting.scheduler import (ChainScheduler, PrerequisiteFailed,
                                          cache_dependencies, expected_cost)
from thesis.models.registry import AR, ARMA, MSAR, MSAR3, STAR, ModelSpec
from thesis.monitoring import Monitor, probe
from thesis.monitoring.plan import ChainPlan

IDENTITY = DataIdentity(canonical_hash="a" * 64, source_manifest_hash="b" * 64,
                        code_hash="c" * 64, config_hash="d" * 64)
FORK = "fork" in multiprocessing.get_all_start_methods()


@pytest.fixture(autouse=True)
def _clean_probe():
    probe.uninstall()
    yield
    probe.uninstall()


@pytest.fixture(scope="module")
def series() -> pd.Series:
    rng = np.random.default_rng(7)
    n = 170
    y = np.zeros(n)
    for t in range(1, n):
        regime = 1.5 if (t // 40) % 2 else -0.5
        y[t] = regime + 0.4 * y[t - 1] + rng.normal(0, 1.0)
    return pd.Series(y, index=pd.date_range("1990-01-01", periods=n, freq="MS"), name="S")


@pytest.fixture(scope="module")
def config():
    return load_config(names=("baseline", "series_catalog", "thresholds"),
                       config_dir=CONFIG_DIR).with_overrides(
        {"forecasting": {"star_multistep": {"paths": 30}}}, "scheduler-test")


SPECS = {AR: ModelSpec(AR, order=1), ARMA: ModelSpec(ARMA, order=1, ma_order=1),
         MSAR: ModelSpec(MSAR, order=1, k_regimes=2),
         MSAR3: ModelSpec(MSAR3, order=1, k_regimes=3),
         STAR: ModelSpec(STAR, order=1, kind="LSTAR", delay=1)}


def batches(series):
    """Two 'series' batches plus a robustness batch that the cache should serve."""
    out = []
    for name, y in (("S1", series), ("S2", series * 0.5 + 1.0)):
        out.append([ChainJob(tag=m, series_name=name, y=y, spec=spec, horizons=(1, 3),
                             window_length=120, frequency="M", transformation="pct",
                             max_origins=3, task_id=f"forecasting:{name}|{m}")
                    for m, spec in SPECS.items()])
    # Same chain as forecasting:S1|MSAR at a subset of horizons: served from the cache.
    out.append([ChainJob(tag=(120, MSAR), series_name="S1", y=series, spec=SPECS[MSAR],
                         horizons=(1,), window_length=120, frequency="M",
                         transformation="pct", max_origins=3, task_id="T4.8:S1|120:MSAR"),
                ChainJob(tag=(100, MSAR), series_name="S1", y=series, spec=SPECS[MSAR],
                         horizons=(1,), window_length=100, frequency="M",
                         transformation="pct", max_origins=3, task_id="T4.8:S1|100:MSAR")])
    return out


def flat(results):
    return [r for batch in results for r in batch]


def assert_identical(left, right):
    assert [t for t, _ in left] == [t for t, _ in right]
    for (_, a), (_, b) in zip(left, right):
        pd.testing.assert_frame_equal(a.forecasts, b.forecasts)
        assert a.counts() == b.counts()
        assert [r.params for r in a.fit_records] == [r.params for r in b.fit_records]
        assert [r.status for r in a.fit_records] == [r.status for r in b.fit_records]
        assert [r.start_used for r in a.fit_records] == [r.start_used for r in b.fit_records]


@pytest.fixture(scope="module")
def serial(series, config, tmp_path_factory):
    cache = FitCache(tmp_path_factory.mktemp("serial"), enabled=True)
    return [run_chains(batch, config, IDENTITY, cache, workers=1)
            for batch in batches(series)]


@pytest.fixture(scope="module")
def per_batch(series, config, tmp_path_factory):
    """The old design: one pool per batch, four workers."""
    cache = FitCache(tmp_path_factory.mktemp("perbatch"), enabled=True)
    return [run_chains(batch, config, IDENTITY, cache, workers=4)
            for batch in batches(series)]


@pytest.fixture(scope="module")
def pooled(series, config, tmp_path_factory):
    cache = FitCache(tmp_path_factory.mktemp("pooled"), enabled=True)
    jobs = flat(batches(series))
    scheduler = ChainScheduler(config, IDENTITY, cache, workers=4).start(jobs)
    results = [scheduler.results(batch) for batch in batches(series)]
    scheduler.close()
    return scheduler, results


class TestIdenticalResults:
    def test_pooled_equals_serial(self, pooled, serial):
        assert_identical(flat(pooled[1]), flat(serial))

    def test_pooled_equals_the_old_per_batch_pools(self, pooled, per_batch):
        assert_identical(flat(pooled[1]), flat(per_batch))

    def test_msar3_and_star_multistep_forecasts_are_present_and_identical(self, pooled,
                                                                          serial):
        for model in (MSAR3, STAR):
            a = dict(flat(pooled[1]))[model].forecasts
            b = dict(flat(serial))[model].forecasts
            assert set(a["horizon"]) == {1, 3}
            assert a["forecast"].notna().all()
            assert np.array_equal(a["forecast"].to_numpy(), b["forecast"].to_numpy())


class TestCacheDependencies:
    def test_the_subset_chain_depends_on_its_cache_source(self, series):
        deps = cache_dependencies(flat(batches(series)), cache_enabled=True)
        assert deps == {"T4.8:S1|120:MSAR": "forecasting:S1|MSAR"}

    def test_no_dependencies_without_a_cache(self, series):
        assert cache_dependencies(flat(batches(series)), cache_enabled=False) == {}

    def test_it_is_still_served_from_the_cache(self, pooled, serial):
        a = dict(flat(pooled[1]))[(120, MSAR)]
        b = dict(flat(serial))[(120, MSAR)]
        assert a.from_cache == b.from_cache == a.attempted == 3

    def test_it_started_after_its_prerequisite_finished(self, pooled):
        scheduler, _ = pooled
        dependent = scheduler.entries["T4.8:S1|120:MSAR"]
        source = scheduler.entries["forecasting:S1|MSAR"]
        assert dependent.submitted >= source.finished


class TestOrdering:
    def test_the_most_expensive_ready_chains_start_first(self, pooled):
        scheduler, _ = pooled
        first = sorted(scheduler.entries.values(), key=lambda e: e.submitted)[:2]
        assert {e.job.spec.model for e in first} == {MSAR3}

    def test_cost_ranks_msar3_above_msar_above_star(self, series):
        jobs = {j.task_id: j for j in batches(series)[0]}
        costs = {m: expected_cost(jobs[f"forecasting:S1|{m}"]) for m in SPECS}
        assert costs[MSAR3] > costs[MSAR] > costs[STAR] > costs[ARMA] > costs[AR]

    def test_never_more_chains_in_flight_than_workers(self, pooled):
        scheduler, _ = pooled
        events = sorted([(e.submitted, 1) for e in scheduler.entries.values()]
                        + [(e.finished, -1) for e in scheduler.entries.values()])
        level = peak = 0
        for _, step in events:
            level += step
            peak = max(peak, level)
        assert peak <= 4


def test_a_mismatched_job_is_refused(series, config, tmp_path):
    jobs = batches(series)[0][:1]
    scheduler = ChainScheduler(config, IDENTITY, FitCache(tmp_path, enabled=False),
                               workers=2).start(jobs)
    other = ChainJob(tag=AR, series_name="S1", y=series, spec=ModelSpec(AR, order=2),
                     horizons=(1, 3), window_length=120, frequency="M",
                     transformation="pct", max_origins=3, task_id=jobs[0].task_id)
    with pytest.raises(RuntimeError, match="differs"):
        scheduler.results([other])
    scheduler.close()


@pytest.mark.skipif(not FORK, reason="patching worker code needs the fork start method")
class TestFailuresAndInterruption:
    def test_a_failing_chain_raises_where_consumed_and_others_finish(
            self, series, config, tmp_path, monkeypatch):
        real = rolling.fit_and_forecast

        def broken(spec, *args, **kwargs):
            if spec.model == MSAR:
                raise FloatingPointError("simulated")
            return real(spec, *args, **kwargs)

        monkeypatch.setattr(rolling, "fit_and_forecast", broken)
        jobs = flat(batches(series))
        scheduler = ChainScheduler(config, IDENTITY, FitCache(tmp_path, enabled=True),
                                   workers=3).start(jobs)
        with pytest.raises(FloatingPointError):
            scheduler.results([j for j in jobs if j.task_id == "forecasting:S1|MSAR"])
        # The dependent is not run on a failed prerequisite; it says why.
        with pytest.raises(PrerequisiteFailed):
            scheduler.results([j for j in jobs if j.task_id == "T4.8:S1|120:MSAR"])
        ok = scheduler.results([j for j in jobs if j.task_id == "forecasting:S1|AR"])
        assert ok[0][1].attempted == 3
        scheduler.close()

    def test_cancel_stops_long_chains_promptly(self, series, config, tmp_path, monkeypatch):
        def slow(*args, **kwargs):
            time.sleep(120)

        monkeypatch.setattr(rolling, "fit_and_forecast", slow)
        jobs = batches(series)[0][:2]
        scheduler = ChainScheduler(config, IDENTITY, FitCache(tmp_path, enabled=False),
                                   workers=2).start(jobs)
        time.sleep(1.0)
        began = time.time()
        scheduler.close(cancel=True)
        assert time.time() - began < 45


def test_monitor_counters_match_with_the_shared_pool(series, config, tmp_path):
    jobs = flat(batches(series))
    stream = io.StringIO()
    monitor = Monitor(tmp_path / "logs" / "r", run_id="r", namespace="smoke", workers=4,
                      stream=stream, heartbeat_seconds=3600, summary_seconds=3600,
                      snapshot_seconds=0.2, tick_seconds=0.1).start()
    deps = cache_dependencies(jobs, True)
    from thesis.forecasting.scheduler import n_origins
    monitor.plan([ChainPlan(task_id=j.task_id, batch="pool", stage="forecasting",
                            exercise="test", role="baseline", series=j.series_name,
                            model=j.spec.model, spec_label=j.spec.label, k_regimes=None,
                            window_length=j.window_length, frequency="M",
                            horizons=j.horizons, n_origins=n_origins(j),
                            expect_cached=j.task_id in deps) for j in jobs])
    scheduler = ChainScheduler(config, IDENTITY, FitCache(tmp_path / "c", enabled=True),
                               workers=4, monitor=monitor).start(jobs)
    results = dict(scheduler.results(jobs))
    scheduler.close()
    monitor.close()
    state = monitor.state
    for job in jobs:
        chain = state.chains[job.task_id]
        result = results[job.tag]
        assert chain.status == "done"
        assert (chain.completed, chain.valid, chain.failed, chain.from_cache) == \
            (result.attempted, result.valid, result.failed, result.from_cache)
    assert state.origin_counts()["remaining"] == 0
    assert not [w for w in state.warnings if "differ" in w["message"]
                or "were planned" in w["message"]]
    assert len(set(state.slots.values())) <= 4
