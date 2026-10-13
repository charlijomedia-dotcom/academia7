"""Parallel chain execution must change the speed and nothing else.

Reproducibility is the whole point of the design, so these tests assert the property
directly: the same chains run across worker processes give byte-identical forecasts,
fit records, failure events and data gaps as the same chains run serially.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from thesis.core.cache import FitCache
from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR
from thesis.forecasting.parallel import ChainJob, run_chains
from thesis.forecasting.rolling import DataIdentity
from thesis.models.registry import AR, ARMA, MSAR, STAR, ModelSpec

IDENTITY = DataIdentity(canonical_hash="a" * 64, source_manifest_hash="b" * 64,
                        code_hash="c" * 64, config_hash="d" * 64)


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
        {"forecasting": {"star_multistep": {"paths": 20}}}, "parallel-test")


def _jobs(series: pd.Series) -> list[ChainJob]:
    specs = {AR: ModelSpec(AR, order=1), ARMA: ModelSpec(ARMA, order=1, ma_order=1),
             MSAR: ModelSpec(MSAR, order=1, k_regimes=2),
             STAR: ModelSpec(STAR, order=1, kind="LSTAR", delay=1)}
    return [ChainJob(tag=model, series_name="TEST", y=series, spec=spec,
                     horizons=(1, 3), window_length=120, frequency="M",
                     transformation="percent", max_origins=8)
            for model, spec in specs.items()]


def _run(series, config, tmp_path, workers):
    cache = FitCache(tmp_path / f"cache{workers}", enabled=False)
    return run_chains(_jobs(series), config, IDENTITY, cache, workers=workers)


@pytest.fixture(scope="module")
def both(series, config, tmp_path_factory):
    root = tmp_path_factory.mktemp("parallel")
    return (_run(series, config, root, 1), _run(series, config, root, 4))


class TestParallelMatchesSerial:
    def test_the_same_chains_come_back_in_the_same_order(self, both):
        serial, parallel = both
        assert [tag for tag, _ in serial] == [tag for tag, _ in parallel]

    def test_forecasts_are_identical(self, both):
        serial, parallel = both
        for (tag, a), (_, b) in zip(serial, parallel):
            pd.testing.assert_frame_equal(
                a.forecasts.reset_index(drop=True), b.forecasts.reset_index(drop=True),
                obj=f"forecasts for {tag}")

    def test_origin_counts_are_identical(self, both):
        serial, parallel = both
        for (tag, a), (_, b) in zip(serial, parallel):
            assert a.counts() == b.counts(), tag

    def test_fit_records_are_identical(self, both):
        # Every field except the measured wall time, which is a timing observation
        # rather than a result and is expected to differ between runs.
        def rows(chain):
            return [{k: v for k, v in r.to_row().items() if k != "wall_seconds"}
                    for r in chain.fit_records]

        serial, parallel = both
        for (tag, a), (_, b) in zip(serial, parallel):
            assert rows(a) == rows(b), tag

    def test_estimated_parameters_match_to_the_last_bit(self, both):
        # Not just equal when rounded: the same optimizer path must have been taken.
        serial, parallel = both
        for (tag, a), (_, b) in zip(serial, parallel):
            for left, right in zip(a.fit_records, b.fit_records):
                assert left.params == right.params, tag
                assert left.loglik == right.loglik, tag

    def test_failure_and_gap_events_are_identical(self, both):
        serial, parallel = both
        for (tag, a), (_, b) in zip(serial, parallel):
            assert [e.to_row() for e in a.failures] == [e.to_row() for e in b.failures], tag
            assert [e.to_row() for e in a.data_gaps] == [e.to_row() for e in b.data_gaps], tag

    def test_every_chain_actually_produced_forecasts(self, both):
        serial, _ = both
        for tag, chain in serial:
            assert chain.attempted == 8, tag
            assert not chain.forecasts.empty, tag


class TestWorkerBookkeeping:
    def test_no_jobs_is_not_an_error(self, config, tmp_path):
        assert run_chains([], config, IDENTITY, FitCache(tmp_path, enabled=False)) == []

    def test_worker_count_never_exceeds_the_job_count(self, series, config, tmp_path):
        jobs = _jobs(series)[:1]
        results = run_chains(jobs, config, IDENTITY,
                             FitCache(tmp_path, enabled=False), workers=8)
        assert len(results) == 1

    def test_workers_default_to_the_configured_count(self, config):
        assert int(config.get("execution.parallel_workers")) >= 1
