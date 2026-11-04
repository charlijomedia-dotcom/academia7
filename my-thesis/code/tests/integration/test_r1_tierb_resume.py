"""Tier B recovery with the pinned rolling engine on a small synthetic warm-started chain.

The stop/resume machinery must never change what is estimated: a chain stopped by the
budget, or killed outright, then restored from committed checkpoints in a fresh "runtime"
and resumed, must end with exactly the payloads of an uninterrupted run.
"""

from __future__ import annotations

import multiprocessing
import os
import shutil
import signal
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

COLAB = Path(__file__).resolve().parents[3] / "colab"
sys.path.insert(0, str(COLAB))
import r1_tierb as tb  # noqa: E402

from thesis.core.config import load_config  # noqa: E402
from thesis.core.paths import CONFIG_DIR  # noqa: E402
from thesis.correction import guard  # noqa: E402
from thesis.correction.rescore import RefitCache  # noqa: E402
from thesis.forecasting import rolling  # noqa: E402
from thesis.forecasting.parallel import ChainJob  # noqa: E402
from thesis.forecasting.rolling import DataIdentity  # noqa: E402
from thesis.models.registry import AR, STAR, ModelSpec  # noqa: E402

IDENTITY = DataIdentity(canonical_hash="a" * 64, source_manifest_hash="b" * 64,
                        code_hash="c" * 64, config_hash="d" * 64)
ORIGINS = 6


def _series() -> pd.Series:
    rng = np.random.default_rng(7)
    y = np.zeros(140)
    for t in range(1, 140):
        y[t] = 0.5 * y[t - 1] + rng.normal(0, 1)
    return pd.Series(y, index=pd.date_range("1990-01-01", periods=140, freq="MS"))


def _config():
    return load_config(names=("baseline", "series_catalog", "thresholds"),
                       config_dir=CONFIG_DIR).with_overrides(
        {"forecasting": {"star_multistep": {"paths": 20}}}, "tierb-resume")


def _job(spec):
    return ChainJob(tag=spec.model, series_name="S", y=_series(), spec=spec, horizons=(1,),
                    window_length=110, frequency="M", transformation="pct",
                    max_origins=ORIGINS, task_id=f"T4.8:S|110:{spec.model}")


def _run(cache, spec, config):
    job = _job(spec)
    with guard.estimation_forbidden(), guard.allowed():
        return rolling.run_chain(job.series_name, job.y, job.spec, job.horizons,
                                 job.window_length, config, frequency=job.frequency,
                                 transformation=job.transformation, identity=IDENTITY,
                                 cache=cache, max_origins=job.max_origins, task_id=job.task_id)


def _stoppable(fits, tmp, budget, stop_file=None):
    return tb.stoppable_refit_cache(fits, task="T", budget=budget, historical_seconds=0.01,
                                    stop_file=stop_file or (tmp / "STOP"),
                                    progress=tmp / "progress.jsonl", safety=1.0)


SPEC = ModelSpec(STAR, order=1, kind="LSTAR", delay=1)


def estimates(fits) -> dict:
    """Every payload by key, without `wall_seconds` (the only field that is a timing).

    Two runs of the same chain differ only in the recorded fit time; parameters,
    likelihoods, forecasts, statuses and warm starts must be identical.
    """
    import json
    out = {}
    for path in tb.payload_files(fits):
        payload = json.loads(path.read_text())
        payload.pop("wall_seconds")
        out[path.relative_to(fits).as_posix()] = payload
    return out


@pytest.fixture(scope="module")
def reference(tmp_path_factory):
    """An uninterrupted run with the plain pinned RefitCache."""
    fits = tmp_path_factory.mktemp("reference") / "fits"
    _run(RefitCache(fits), SPEC, _config())
    return estimates(fits)


def test_stoppable_cache_writes_exactly_the_pinned_payloads(tmp_path, reference):
    fits = tmp_path / "fits"
    budget = tb.Budget(time.time(), 24.0, 0.0)
    _run(_stoppable(fits, tmp_path, budget), SPEC, _config())
    assert estimates(fits) == reference                       # same keys, same estimates
    assert sum(1 for _ in open(tmp_path / "progress.jsonl")) == ORIGINS


def test_budget_stop_then_resume_in_a_new_runtime_equals_uninterrupted(tmp_path, reference):
    config, fits, drive = _config(), tmp_path / "vm1" / "fits", tmp_path / "drive" / "T"
    stop = tmp_path / "STOP"

    # runtime 1: the stop file appears after two origins -> GracefulStop between origins
    class StopAfterTwo:
        def __init__(self):
            self.cache = _stoppable(fits, tmp_path, tb.Budget(time.time(), 24.0, 0.0), stop)
            original_put = self.cache.put

            def put(key, payload):
                if len(tb.payload_files(fits)) == 1:
                    stop.write_text("stop")
                original_put(key, payload)
            self.cache.put = put
    with pytest.raises(tb.GracefulStop):
        _run(StopAfterTwo().cache, SPEC, config)
    assert len(tb.payload_files(fits)) == 2
    tb.commit_checkpoint(fits, drive, task="T", session="R1")

    # runtime 2: a fresh VM; restore from Drive only, then resume
    stop.unlink()
    fresh = tmp_path / "vm2" / "fits"
    assert tb.restore_checkpoints(drive, fresh)["payloads"] == 2
    chain = _run(_stoppable(fresh, tmp_path, tb.Budget(time.time(), 24.0, 0.0)), SPEC, config)
    assert chain.from_cache == 2                               # verified origins replayed
    assert estimates(fresh) == reference                      # identical to uninterrupted
    walk = tb.walk_chain(_job(SPEC), fresh, IDENTITY, config)
    assert walk["complete"] and not walk["unreachable"]


def test_budget_refuses_to_start_an_origin_it_cannot_finish(tmp_path):
    fits = tmp_path / "fits"
    exhausted = tb.Budget(time.time() - 3600, 1.0, 0.0)       # budget already used
    with pytest.raises(tb.GracefulStop, match="budget"):
        _run(_stoppable(fits, tmp_path, exhausted), SPEC, _config())
    assert tb.payload_files(fits) == []                         # nothing half-done


def _killable(fits: str):
    sys.path.insert(0, str(COLAB))
    import r1_tierb as tb2
    cache = tb2.stoppable_refit_cache(fits, task="T", budget=tb2.Budget(time.time(), 24.0, 0.0),
                                      historical_seconds=0.01, stop_file=fits + ".STOP",
                                      progress=fits + ".progress", safety=1.0)
    original_put = cache.put

    def slow_put(key, payload):
        original_put(key, payload)
        time.sleep(1.0)                                         # time to be killed mid-chain
    cache.put = slow_put
    _run(cache, SPEC, _config())


def test_hard_kill_then_restore_and_resume_equals_uninterrupted(tmp_path, reference):
    config, fits, drive = _config(), tmp_path / "vm1" / "fits", tmp_path / "drive" / "T"
    process = multiprocessing.get_context("fork").Process(target=_killable, args=(str(fits),))
    process.start()
    deadline = time.time() + 120
    while len(tb.payload_files(fits)) < 3 and time.time() < deadline and process.is_alive():
        time.sleep(0.1)
    os.kill(process.pid, signal.SIGKILL)                        # the runtime disappears
    process.join()
    survived = len(tb.payload_files(fits))
    assert 1 <= survived < ORIGINS
    tb.commit_checkpoint(fits, drive, task="T", session="K1")   # last backup before loss
    shutil.rmtree(tmp_path / "vm1")                             # the VM's disk is gone
    fresh = tmp_path / "vm2" / "fits"
    assert tb.restore_checkpoints(drive, fresh)["payloads"] == survived
    chain = _run(_stoppable(fresh, tmp_path, tb.Budget(time.time(), 24.0, 0.0)), SPEC, config)
    assert chain.from_cache == survived
    assert estimates(fresh) == reference


def test_walk_detects_unreachable_and_reports_the_prefix(tmp_path, reference):
    config, fits = _config(), tmp_path / "fits"
    _run(RefitCache(fits), SPEC, config)
    by_time = sorted(tb.payload_files(fits), key=lambda p: p.stat().st_mtime_ns)
    by_time[2].unlink()                                        # a hole in the chain
    walk = tb.walk_chain(_job(SPEC), fits, IDENTITY, config)
    assert walk["completed"] == 2 and not walk["complete"]
    assert len(walk["unreachable"]) == ORIGINS - 3             # orphans after the hole


def test_worker_refuses_a_task_outside_its_batch(tmp_path):
    import r1_tierb_worker as worker
    with pytest.raises(tb.TierBError, match="not authorised"):
        worker.main(["run", "--batch", "B1", "--task", "T4.1:FEDFUNDS|ARMA",
                     "--code-dir", str(Path(__file__).resolve().parents[2]),
                     "--original", str(tmp_path), "--batch-fits", str(tmp_path)])


def test_no_estimation_allowed_blocks_even_approved_blocks():
    from thesis.models import registry
    with guard.estimation_forbidden(), tb.no_estimation_allowed():
        with guard.allowed(), pytest.raises(guard.EstimationForbidden):
            registry.fit_and_forecast(ModelSpec(AR, order=1), _series().iloc[:110], [1], _config())
