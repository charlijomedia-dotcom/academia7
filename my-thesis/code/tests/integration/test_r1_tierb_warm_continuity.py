"""Warm-start continuity after a failed origin (the B2 defect), with the pinned engine.

A small MSAR chain (real fits) in which origin 2 fails. The pinned `run_chain` keys every
origin by the LIVE warm-start rule (a failed fit keeps the previous usable warm start), but
its cache-hit branch resets the warm start from the stored payload (None for a failed fit).
These tests show the defect, then show that the orchestration replay layer
(`r1_tierb.live_replay_class`) reconstructs the exact live key sequence, serves every
stored record unchanged, never re-estimates, resumes after an interruption to exactly the
uninterrupted result, and lets the assembly replay the chain with estimation forbidden.

The failure is induced, not natural: the real MSAR outcome of origin 2 is marked failed
(status, reason code, no warm payload), exactly as failed MSAR payloads are stored.
"""

from __future__ import annotations

import json
import shutil
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
from thesis.correction import guard, rescore  # noqa: E402
from thesis.correction.rescore import RefitCache  # noqa: E402
from thesis.forecasting import rolling  # noqa: E402
from thesis.forecasting.parallel import ChainJob  # noqa: E402
from thesis.forecasting.rolling import DataIdentity  # noqa: E402
from thesis.core.schemas import ReasonCode, Status  # noqa: E402
from thesis.forecasting.windows import estimation_origins  # noqa: E402
from thesis.models.registry import MSAR, ModelSpec  # noqa: E402

IDENTITY = DataIdentity(canonical_hash="a" * 64, source_manifest_hash="b" * 64,
                        code_hash="c" * 64, config_hash="d" * 64)
ORIGINS = 5
SPEC = ModelSpec(MSAR, order=1, k_regimes=2)
FAILED_ORIGIN = 2                                   # 1-based position in the chain


def _series() -> pd.Series:
    rng = np.random.default_rng(11)
    n, y, regime = 150, np.zeros(150), 0
    for t in range(1, n):
        if rng.random() < 0.05:
            regime = 1 - regime
        y[t] = (2.0 if regime else -1.0) + 0.3 * y[t - 1] + rng.normal(0, 0.7)
    return pd.Series(y, index=pd.date_range("1990-01-01", periods=n, freq="MS"))


def _config():
    return load_config(names=("baseline", "series_catalog", "thresholds"), config_dir=CONFIG_DIR)


def _job():
    return ChainJob(tag="MSAR", series_name="S", y=_series(), spec=SPEC, horizons=(1,),
                    window_length=120, frequency="M", transformation="pct",
                    max_origins=ORIGINS, task_id="T4.8:S|120:MSAR")


class Fits:
    """Counts real estimations; marks the outcome of origin FAILED_ORIGIN as failed."""

    def __init__(self, keep_warm_on_failure=False):
        self.calls, self.dates = 0, []
        self.keep_warm = keep_warm_on_failure
        self.real = rolling.fit_and_forecast

    def __call__(self, spec, window, horizons, config, **kwargs):
        self.calls += 1
        self.dates.append(kwargs.get("refit_date"))
        outcome = self.real(spec, window, horizons, config, **kwargs)
        origins = estimation_origins(_series().index, 120, [1], max_origins=ORIGINS)
        if kwargs.get("refit_date") == origins[FAILED_ORIGIN - 1].origin_date.strftime("%Y-%m-%d"):
            outcome.record.status = Status.FAILED
            outcome.record.reason_codes = [ReasonCode.NONCONVERGENCE]
            if not self.keep_warm:
                outcome.warm_payload = None
        return outcome


def _run(cache, fits_counter, monkeypatch, *, allowed=True):
    monkeypatch.setattr(rolling, "fit_and_forecast", fits_counter)
    job = _job()
    with guard.estimation_forbidden():
        context = guard.allowed() if allowed else _null()
        with context:
            return rolling.run_chain(job.series_name, job.y, job.spec, job.horizons,
                                     job.window_length, _config(), frequency=job.frequency,
                                     transformation=job.transformation, identity=IDENTITY,
                                     cache=cache, max_origins=job.max_origins,
                                     task_id=job.task_id)


class _null:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def estimates(fits: Path) -> dict:
    out = {}
    for path in tb.payload_files(fits):
        payload = json.loads(path.read_text())
        payload.pop("wall_seconds")
        out[path.relative_to(fits).as_posix()] = payload
    return out


def _records(chain) -> list[dict]:
    return [{"date": r.refit_date, "status": r.status.value,
             "codes": [c.value for c in r.reason_codes], "params": r.params,
             "loglik": r.loglik} for r in chain.fit_records]


@pytest.fixture(scope="module")
def reference(tmp_path_factory):
    """One uninterrupted LIVE run with the plain pinned RefitCache."""
    mp = pytest.MonkeyPatch()
    fits = tmp_path_factory.mktemp("reference") / "fits"
    order = []
    cache = RefitCache(fits)
    original_put = cache.put

    def put(key, payload):
        order.append(cache.path_for(key).relative_to(fits).as_posix())
        original_put(key, payload)
    cache.put = put
    counter = Fits()
    chain = _run(cache, counter, mp)
    mp.undo()
    statuses = [r.status.value for r in chain.fit_records]
    assert statuses[FAILED_ORIGIN - 1] == "failed"
    assert all(s != "failed" for i, s in enumerate(statuses) if i != FAILED_ORIGIN - 1)
    return {"fits": fits, "order": order, "estimates": estimates(fits), "calls": counter.calls,
            "records": _records(chain), "forecasts": chain.forecasts.copy()}


def test_reference_chain_has_success_failure_success(reference):
    assert reference["calls"] == ORIGINS and len(reference["order"]) == ORIGINS
    stored = [reference["estimates"][p] for p in reference["order"]]
    assert [p["status"] != "failed" for p in stored] == [True, False, True, True, True]
    assert stored[FAILED_ORIGIN - 1]["warm_payload"] is None
    assert stored[0]["warm_payload"] is not None


def test_the_defect_cache_hit_rule_breaks_after_the_failed_origin(reference):
    job, config = _job(), _config()
    hit = tb.walk_chain(job, reference["fits"], IDENTITY, config, semantics="cache_hit")
    live = tb.walk_chain(job, reference["fits"], IDENTITY, config, semantics="live")
    assert hit["completed"] == FAILED_ORIGIN and len(hit["unreachable"]) == ORIGINS - FAILED_ORIGIN
    assert live["complete"] and not live["unreachable"]
    assert [rel for _, rel in live["sequence"]] == reference["order"]   # exact key sequence
    report = tb.continuity_report(job, reference["fits"], IDENTITY, config)
    mismatch = report["first_mismatch"]
    assert mismatch["origin_index"] == FAILED_ORIGIN + 1
    assert mismatch["keys"]["cache_hit_rule"]["payload_exists"] is False
    assert mismatch["keys"]["cache_hit_rule"]["predecessor_hash"] == ""
    assert mismatch["keys"]["live_rule"]["payload_exists"] is True
    assert mismatch["preceding"][-1]["status"] == "failed"
    assert mismatch["live_warm_state_from"] == live["sequence"][0][0]


def test_the_defect_plain_pinned_replay_cannot_assemble_or_resume_correctly(reference, tmp_path,
                                                                            monkeypatch):
    # assembly with estimation forbidden: the plain pinned cache misses and must estimate
    fits = tmp_path / "fits"
    shutil.copytree(reference["fits"], fits)
    with tb.no_estimation_allowed(), pytest.raises(guard.EstimationForbidden):
        _run(RefitCache(fits), Fits(), monkeypatch)
    # resume with estimation allowed: it silently re-estimates from a different start
    counter = Fits()
    chain = _run(RefitCache(fits), counter, monkeypatch)
    # at least the origin after the failure is re-estimated from a cold start (how many
    # more depends on whether the cold start reaches the same optimum to 10 decimals)
    assert 1 <= counter.calls <= ORIGINS - FAILED_ORIGIN            # duplicate estimations
    assert len(tb.payload_files(fits)) == ORIGINS + counter.calls    # a forked chain
    assert chain.from_cache == ORIGINS - counter.calls


def test_live_replay_serves_the_whole_chain_unchanged_with_no_estimation(reference, tmp_path,
                                                                        monkeypatch):
    fits = tmp_path / "fits"
    shutil.copytree(reference["fits"], fits)
    before = {p: tb.sha256_file(p) for p in tb.payload_files(fits)}
    counter = Fits()
    with tb.no_estimation_allowed():
        chain = _run(tb.live_replay_class()(fits), counter, monkeypatch)
    assert counter.calls == 0 and chain.from_cache == ORIGINS
    assert _records(chain) == reference["records"]          # params, status, reason codes
    pd.testing.assert_frame_equal(chain.forecasts, reference["forecasts"])
    assert {p: tb.sha256_file(p) for p in tb.payload_files(fits)} == before   # untouched


@pytest.mark.parametrize("keep_warm", [False, True])
def test_interrupt_after_the_failure_restore_resume_equals_uninterrupted(tmp_path, monkeypatch,
                                                                         keep_warm):
    """Stop after origin 3 (past the failed origin 2), commit, lose the VM, restore from
    Drive into a fresh runtime, resume: identical to one uninterrupted run, and only the
    remaining origins are estimated. Also when the failed fit's payload keeps a warm
    start (the live rule must still ignore it)."""
    mp = pytest.MonkeyPatch()
    ref_fits = tmp_path / "ref" / "fits"
    _run(RefitCache(ref_fits), Fits(keep_warm), mp)
    mp.undo()
    reference = estimates(ref_fits)

    vm1, drive, stop = tmp_path / "vm1" / "fits", tmp_path / "drive" / "T", tmp_path / "STOP"
    cache = tb.stoppable_refit_cache(vm1, task="T", budget=tb.Budget(time.time(), 24.0, 0.0),
                                     historical_seconds=0.01, stop_file=stop,
                                     progress=tmp_path / "p.jsonl", safety=1.0)
    original_put = cache.put

    def put(key, payload):
        if len(tb.payload_files(vm1)) == 2:                 # writing origin 3
            stop.write_text("stop")
        original_put(key, payload)
    cache.put = put
    first = Fits(keep_warm)
    with pytest.raises(tb.GracefulStop):
        _run(cache, first, monkeypatch)
    assert first.calls == 3 and len(tb.payload_files(vm1)) == 3
    tb.commit_checkpoint(vm1, drive, task="T", session="S1")
    shutil.rmtree(tmp_path / "vm1")                         # the runtime is gone
    stop.unlink()

    vm2 = tmp_path / "vm2" / "fits"
    assert tb.restore_checkpoints(drive, vm2)["payloads"] == 3
    walk = tb.walk_chain(_job(), vm2, IDENTITY, _config())
    assert walk["completed"] == 3 and not walk["unreachable"]
    resumed = Fits(keep_warm)
    cache2 = tb.stoppable_refit_cache(vm2, task="T", budget=tb.Budget(time.time(), 24.0, 0.0),
                                      historical_seconds=0.01, stop_file=stop,
                                      progress=tmp_path / "p2.jsonl", safety=1.0)
    chain = _run(cache2, resumed, monkeypatch)
    assert chain.from_cache == 3 and resumed.calls == ORIGINS - 3   # no duplicate estimation
    assert estimates(vm2) == reference                               # identical to uninterrupted
    final = tb.walk_chain(_job(), vm2, IDENTITY, _config())
    assert final["complete"] and not final["unreachable"]


def test_assembly_with_estimation_forbidden_replays_through_the_pinned_workflow_class(
        reference, tmp_path, monkeypatch):
    """The R1 workflow builds `rescore.RefitCache(...)` for approved chains and calls the
    pinned run_chain inside `guard.allowed()`; with the live-replay hook and estimation
    refused, the chain assembles entirely from the stored payloads."""
    fits = tmp_path / "fits"
    shutil.copytree(reference["fits"], fits)
    counter = Fits()
    with tb.no_estimation_allowed(), tb.live_replay_in_pinned_workflow():
        cache = rescore.RefitCache(fits)                 # what PublishedRescorer constructs
        chain = _run(cache, counter, monkeypatch)
    assert rescore.RefitCache is RefitCache                   # the hook is undone
    assert counter.calls == 0 and chain.from_cache == ORIGINS
    assert chain.failed == 1 and _records(chain) == reference["records"]
    pd.testing.assert_frame_equal(chain.forecasts, reference["forecasts"])


def test_the_replay_layer_refuses_a_forked_request(reference, tmp_path):
    from thesis.forecasting.rolling import _cache_key
    cache = tb.live_replay_class()(tmp_path / "fits")
    origin = estimation_origins(_series().index, 120, [1], max_origins=ORIGINS)[0]
    with pytest.raises(tb.TierBError, match="not the live warm-start state"):
        cache.get(_cache_key(IDENTITY, "S", "pct", SPEC, origin, "[1.0]"))


# -- the Part 8 integration dry run: read-only replay of the merged refit cache ----------------
#
# Colab dry run integration-20261107T184004Z-93c0f8 stopped in stage 2 with "the merged refit
# cache changed during assembly". Cause: `PublishedRescorer` constructs `rescore.RefitCache`,
# whose pinned `__post_init__` writes README_R1_REFIT_CACHE.txt into the cache folder; the
# live-replay hook subclasses it, so the README appeared in the merged cache (which `merge`
# fills with payloads only). The tests above compare payload files only, so they did not see it.

import r1_integration_common as ic  # noqa: E402
from thesis.correction.rescore import REFIT_README  # noqa: E402

README = "README_R1_REFIT_CACHE.txt"


def _merged_copy(reference, root: Path) -> Path:
    """The reference payloads only, as `r1_tierb_aggregate.merge` restores them."""
    fits = root / "fits"
    for path in tb.payload_files(reference["fits"]):
        target = fits / path.relative_to(reference["fits"])
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    assert not (fits / README).exists()
    return fits


def test_old_live_replay_hook_writes_the_readme_and_fails_the_strict_check(reference, tmp_path,
                                                                          monkeypatch):
    fits = _merged_copy(reference, tmp_path)
    before = ic.tree_listing(fits)
    with tb.no_estimation_allowed(), tb.live_replay_in_pinned_workflow():
        chain = _run(rescore.RefitCache(fits), Fits(), monkeypatch)
    assert chain.from_cache == ORIGINS                       # the replay itself was correct
    diff = ic.listing_diff(before, ic.tree_listing(fits))
    readme_sha = tb.sha256_bytes(REFIT_README.encode("utf-8"))
    assert diff == {"added": [{"path": README, "sha256": readme_sha}], "removed": [], "modified": []}
    report = tmp_path / "diff.json"
    with pytest.raises(ic.IntegrationError, match="1 added, 0 removed, 0 modified"):
        ic.require_unchanged("the merged refit cache", fits, before, "during assembly", report)
    assert json.loads(report.read_text())["added"] == diff["added"]


def test_readonly_replay_keeps_the_cache_exact_and_reproduces_the_old_replay(reference, tmp_path,
                                                                            monkeypatch):
    old_fits = _merged_copy(reference, tmp_path / "old")
    with tb.no_estimation_allowed(), tb.live_replay_in_pinned_workflow():
        old = _run(rescore.RefitCache(old_fits), Fits(), monkeypatch)
    fits = _merged_copy(reference, tmp_path / "new")
    before = ic.tree_listing(fits)
    counter = Fits()
    with tb.no_estimation_allowed(), ic.readonly_refit_replay():
        cache = rescore.RefitCache(fits)                    # what PublishedRescorer constructs
        new = _run(cache, counter, monkeypatch)
    assert rescore.RefitCache is RefitCache                 # the hook is undone
    assert ic.require_unchanged("the merged refit cache", fits, before, "during assembly",
                                tmp_path / "d.json")["unchanged"]
    assert counter.calls == 0 and new.from_cache == ORIGINS and new.failed == 1
    assert _records(new) == _records(old) == reference["records"]
    pd.testing.assert_frame_equal(new.forecasts, old.forecasts)
    pd.testing.assert_frame_equal(new.forecasts, reference["forecasts"])


def test_readonly_adapter_refuses_writes_and_never_creates_a_folder(reference, tmp_path):
    from thesis.forecasting.rolling import _cache_key
    cls = ic.readonly_refit_class()
    with pytest.raises(ic.IntegrationError, match="not an existing"):
        cls(tmp_path / "missing" / "fits")
    assert not (tmp_path / "missing").exists()
    fits = _merged_copy(reference, tmp_path)
    before = ic.tree_listing(fits)
    cache = cls(fits)
    origin = estimation_origins(_series().index, 120, [1], max_origins=ORIGINS)[0]
    key = _cache_key(IDENTITY, "S", "pct", SPEC, origin, "")
    assert cache.get(key) is not None                       # the first origin is served
    with pytest.raises(ic.IntegrationError, match="write to .* refused"):
        cache.put(key, {"status": "adequate"})
    assert ic.tree_listing(fits) == before


def test_dependent_output_replay_is_read_only_and_reproduces_the_chain(reference, tmp_path):
    sys.path.insert(0, str(COLAB))
    import r1_integration_dependents as dep
    fits = _merged_copy(reference, tmp_path)
    before = ic.tree_listing(fits)
    chain = dep.replay(_job(), fits, IDENTITY, _config())
    assert ic.tree_listing(fits) == before
    assert chain.from_cache == ORIGINS and _records(chain) == reference["records"]
    pd.testing.assert_frame_equal(chain.forecasts, reference["forecasts"])
