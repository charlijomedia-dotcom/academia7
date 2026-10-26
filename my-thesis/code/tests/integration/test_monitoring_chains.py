"""Progress monitoring of real rolling chains, serial and on four worker processes.

Four properties are asserted on real fits rather than on synthetic events:

* the monitor's counters equal what the chains actually computed (origins, valid and
  failed estimations, cache hits, forecast records), with no reconciliation warning;
* with four workers every chain is visible from the parent with its own worker slot, and
  the event stream and log are never interleaved or corrupted;
* the numbers are identical with and without monitoring, serial and parallel;
* a fit that takes a long time is reported as running, and a chain that raises is
  recorded as failed with its last origin preserved.
"""

from __future__ import annotations

import io
import json
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
from thesis.forecasting.windows import estimation_origins
from thesis.models.registry import AR, ARMA, MSAR, STAR, ModelSpec
from thesis.monitoring import Monitor, probe
from thesis.monitoring.plan import ChainPlan

IDENTITY = DataIdentity(canonical_hash="a" * 64, source_manifest_hash="b" * 64,
                        code_hash="c" * 64, config_hash="d" * 64)
SPECS = {AR: ModelSpec(AR, order=1), ARMA: ModelSpec(ARMA, order=1, ma_order=1),
         MSAR: ModelSpec(MSAR, order=1, k_regimes=2),
         STAR: ModelSpec(STAR, order=1, kind="LSTAR", delay=1)}


@pytest.fixture(autouse=True)
def _clean_probe():
    probe.uninstall()
    yield
    probe.uninstall()


@pytest.fixture(scope="module")
def series() -> pd.Series:
    rng = np.random.default_rng(404)
    n = 200
    y = np.zeros(n)
    for t in range(1, n):
        y[t] = 0.4 * y[t - 1] + rng.normal(0, 1.0)
    return pd.Series(y, index=pd.date_range("1990-01-01", periods=n, freq="MS"), name="TEST")


@pytest.fixture(scope="module")
def config():
    return load_config(names=("baseline", "series_catalog", "thresholds"),
                       config_dir=CONFIG_DIR).with_overrides(
        {"forecasting": {"star_multistep": {"paths": 20}}}, "monitoring-test")


def jobs(series, batch="forecasting:TEST", max_origins=8):
    return [ChainJob(tag=model, series_name="TEST", y=series, spec=spec, horizons=(1, 3),
                     window_length=120, frequency="M", transformation="percent",
                     max_origins=max_origins, task_id=f"{batch}|{model}")
            for model, spec in SPECS.items()]


def plans(job_list, batch="forecasting:TEST"):
    return [ChainPlan(task_id=j.task_id, batch=batch, stage="forecasting",
                      exercise="baseline", role="baseline", series=j.series_name,
                      model=j.spec.model, spec_label=j.spec.label,
                      k_regimes=j.spec.k_regimes if j.spec.model == MSAR else None,
                      window_length=j.window_length, frequency=j.frequency,
                      horizons=j.horizons,
                      n_origins=len(estimation_origins(pd.DatetimeIndex(j.y.index),
                                                       j.window_length, list(j.horizons),
                                                       max_origins=j.max_origins)))
            for j in job_list]


def monitored(tmp_path, workers=4, **kwargs):
    stream = io.StringIO()
    monitor = Monitor(tmp_path / "logs" / "run", run_id="run", namespace="smoke",
                      workers=workers, stream=stream, heartbeat_seconds=0.3,
                      summary_seconds=3600, snapshot_seconds=0.1, tick_seconds=0.05, **kwargs)
    return monitor.start(), stream


def execute(series, config, tmp_path, workers, monitor=None, cache=False, job_list=None):
    job_list = job_list or jobs(series)
    if monitor is not None:
        monitor.plan(plans(job_list))
    store = FitCache(tmp_path / "cache", enabled=cache)
    if monitor is not None:
        with monitor.batch("forecasting:TEST", [j.task_id for j in job_list]):
            return run_chains(job_list, config, IDENTITY, store, workers=workers,
                              monitor=monitor)
    return run_chains(job_list, config, IDENTITY, store, workers=workers)


def assert_same_numbers(left, right):
    assert [tag for tag, _ in left] == [tag for tag, _ in right]
    for (_, a), (_, b) in zip(left, right):
        pd.testing.assert_frame_equal(a.forecasts, b.forecasts)
        assert a.counts() == b.counts()
        assert [r.params for r in a.fit_records] == [r.params for r in b.fit_records]
        assert [r.status for r in a.fit_records] == [r.status for r in b.fit_records]
        assert [(f.refit_date, f.reason_code) for f in a.failures] == \
            [(f.refit_date, f.reason_code) for f in b.failures]


@pytest.fixture(scope="module")
def reference(series, config, tmp_path_factory):
    """The chains computed with no monitor at all, serially."""
    return execute(series, config, tmp_path_factory.mktemp("ref"), workers=1)


@pytest.fixture(scope="module")
def outcome(series, config, tmp_path_factory):
    """The same chains on four worker processes, monitored."""
    probe.uninstall()
    root = tmp_path_factory.mktemp("four")
    monitor, stream = monitored(root, workers=4)
    results = execute(series, config, root, workers=4, monitor=monitor)
    monitor.close()
    return monitor, stream, results


class TestFourWorkers:

    def test_numbers_identical_to_the_unmonitored_serial_run(self, outcome, reference):
        assert_same_numbers(outcome[2], reference)

    def test_counters_equal_the_computed_results(self, outcome):
        monitor, _, results = outcome
        for tag, chain in results:
            state = monitor.state.chains[f"forecasting:TEST|{tag}"]
            assert state.status == "done"
            assert state.completed == chain.attempted
            assert state.valid == chain.valid and state.failed == chain.failed
            assert state.from_cache == chain.from_cache
            assert state.n_records == len(chain.forecasts)
            assert state.completed == state.plan.n_origins
        assert not [w for w in monitor.state.warnings if "differ" in w["message"]]
        assert monitor.state.origin_counts()["remaining"] == 0

    def test_each_chain_ran_in_a_worker_process_seen_by_the_parent(self, outcome):
        monitor, _, _ = outcome
        events = [json.loads(line) for line in
                  monitor.paths["events"].read_text().splitlines()]
        parent = next(e["pid"] for e in events if e["kind"] == "run_start")
        starts = [e for e in events if e["kind"] == "chain_start"]
        assert len(starts) == 4
        assert all(e["pid"] != parent for e in starts)
        assert len({e["pid"] for e in starts}) >= 2

    def test_every_event_line_is_intact_json(self, outcome):
        monitor, _, _ = outcome
        lines = monitor.paths["events"].read_text().splitlines()
        assert lines and all(json.loads(line)["kind"] for line in lines)

    def test_log_lines_are_never_interleaved(self, outcome):
        _, stream, _ = outcome
        for line in stream.getvalue().splitlines():
            assert line.startswith(("[", " ", "=", "-")), line

    def test_origin_events_arrive_in_chain_order(self, outcome):
        monitor, _, _ = outcome
        events = [json.loads(line) for line in
                  monitor.paths["events"].read_text().splitlines()]
        for model in SPECS:
            mine = [e for e in events if e.get("task_id") == f"forecasting:TEST|{model}"
                    and e["kind"] == "origin_start"]
            assert [e["index"] for e in mine] == list(range(1, len(mine) + 1))


class TestSerialAndCache:
    def test_serial_monitored_run_is_identical(self, series, config, tmp_path, reference):
        monitor, _ = monitored(tmp_path, workers=1)
        results = execute(series, config, tmp_path, workers=1, monitor=monitor)
        monitor.close()
        assert_same_numbers(results, reference)
        assert monitor.state.origin_counts()["completed"] == sum(c.attempted for _, c in results)

    def test_cache_served_origins_are_counted_and_not_timed(self, series, config, tmp_path):
        execute(series, config, tmp_path, workers=1, cache=True)       # fills the cache
        monitor, _ = monitored(tmp_path, workers=1)
        results = execute(series, config, tmp_path, workers=1, monitor=monitor, cache=True)
        monitor.close()
        counts = monitor.state.origin_counts()
        assert counts["from_cache"] == sum(c.from_cache for _, c in results) > 0
        assert counts["fitted"] == 0
        assert monitor.state.timing == {}


@pytest.mark.skipif("spawn" not in multiprocessing.get_all_start_methods(),
                    reason="spawn start method unavailable")
def test_worker_channel_works_with_the_spawn_start_method(series, config, tmp_path,
                                                         monkeypatch, reference):
    """Windows has only `spawn`: the queue must reach workers through the initializer."""
    real = multiprocessing.get_context
    monkeypatch.setattr(multiprocessing, "get_context",
                        lambda method=None: real(method or "spawn"))
    monitor, _ = monitored(tmp_path, workers=2)
    results = execute(series, config, tmp_path, workers=2, monitor=monitor)
    monitor.close()
    assert_same_numbers(results, reference)
    assert monitor.state.chain_counts()["done"] == 4
    assert not [w for w in monitor.state.warnings if "differ" in w["message"]]


class TestSlowAndFailingFits:
    def test_a_slow_fit_is_reported_while_running_and_not_as_a_failure(
            self, series, config, tmp_path, monkeypatch):
        real = rolling.fit_and_forecast
        calls = {"n": 0}

        def slow(*args, **kwargs):
            calls["n"] += 1
            if calls["n"] == 2:
                probe.substep("multistart 2/3 (test)")
                time.sleep(1.2)
            return real(*args, **kwargs)

        monkeypatch.setattr(rolling, "fit_and_forecast", slow)
        monitor, stream = monitored(tmp_path, workers=1)
        job_list = jobs(series)[:1]
        results = execute(series, config, tmp_path, workers=1, monitor=monitor,
                          job_list=job_list)
        monitor.close()
        text = stream.getvalue()
        assert "fit running" in text and "multistart 2/3 (test)" in text
        assert monitor.state.chains["forecasting:TEST|AR"].status == "done"
        assert monitor.state.chains["forecasting:TEST|AR"].max_fit_seconds >= 1.2
        assert not monitor.state.failures
        assert results[0][1].attempted == 8

    def test_a_raising_chain_is_recorded_with_its_last_origin(
            self, series, config, tmp_path, monkeypatch):
        real = rolling.fit_and_forecast
        calls = {"n": 0}

        def broken(*args, **kwargs):
            calls["n"] += 1
            if calls["n"] == 3:
                raise FloatingPointError("simulated numerical failure")
            return real(*args, **kwargs)

        monkeypatch.setattr(rolling, "fit_and_forecast", broken)
        monitor, _ = monitored(tmp_path, workers=1)
        with pytest.raises(FloatingPointError):
            execute(series, config, tmp_path, workers=1, monitor=monitor,
                    job_list=jobs(series)[:1])
        monitor.close("failed", "FloatingPointError")
        chain = monitor.state.chains["forecasting:TEST|AR"]
        assert chain.status == "failed" and chain.completed == 2
        snapshot = json.loads(monitor.paths["snapshot"].read_text())
        assert snapshot["status"] == "failed"
        assert "simulated numerical failure" in snapshot["failures"][-1]["error"]
        assert chain.current_origin                      # the origin it died on
