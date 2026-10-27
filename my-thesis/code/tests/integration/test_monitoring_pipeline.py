"""The monitor and the shared-pool scheduler on a real end-to-end pipeline run.

The same reduced pipeline (real frozen data, real estimators, small windows) is run
twice: once strictly sequentially (one process, no monitor) and once with the monitor and
the shared four-worker pool. Asserted:

* every research output is identical (tools/compare_runs.py, which excludes only the
  documented run-time metadata), so neither scheduling nor monitoring changes a number;
* the rolling plan built before the forecasts matches what actually ran, chain by chain
  and origin by origin, and nothing is left "remaining" at the end;
* every one of the ten stages is reported in order and completes;
* the operational logs are written under the run-log directory and nothing from the
  monitor appears under the output tree.
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import pytest

from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR, FROZEN_DIR, Namespace, output_layout
from thesis.core.provenance import RunContext
from thesis.data.store import load_bundle
from thesis.monitoring import Monitor, probe
from thesis.monitoring.plan import STAGES
from thesis.pipeline import Pipeline

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from compare_runs import compare_trees  # noqa: E402

from test_pipeline import FAST_OVERRIDES  # noqa: E402

OVERRIDES = {**FAST_OVERRIDES, "execution": {"cache": True, "checkpoint": True,
                                             "parallel_workers": 4}}


def _run(root: Path, *, monitored: bool):
    probe.uninstall()
    config = load_config(names=("baseline", "series_catalog", "thresholds"),
                         config_dir=CONFIG_DIR).with_overrides(OVERRIDES, "monitor-test")
    bundle = load_bundle(FROZEN_DIR, config)
    layout = type(output_layout(Namespace.SMOKE))(root=root / "out", cache=root / "cache")
    context = RunContext(namespace=Namespace.SMOKE, config_hash=config.hash,
                         data_snapshot_hash=bundle.data_input_identity,
                         data_cutoff=config.get("samples.monthly_end"),
                         vintage_date=config.get("run.vintage_date"))
    monitor = stream = None
    if monitored:
        stream = io.StringIO()
        monitor = Monitor(root / "run_logs" / context.run_id, run_id=context.run_id,
                          namespace="smoke", workers=4, stream=stream,
                          heartbeat_seconds=5, summary_seconds=30).start()
    pipeline = Pipeline(config, context, layout, bundle, smoke=True, monitor=monitor,
                        workers=4 if monitored else 1)
    summary = pipeline.run()
    plan = pipeline.rolling_plan() if monitored else None
    if monitor is not None:
        monitor.close()
    return pipeline, summary, layout, monitor, stream, plan


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    plain = _run(tmp_path_factory.mktemp("plain"), monitored=False)
    watched = _run(tmp_path_factory.mktemp("watched"), monitored=True)
    return plain, watched


def test_research_outputs_identical_with_and_without_monitoring(runs):
    plain, watched = runs
    differences, counts = compare_trees(plain[2].root, watched[2].root)
    assert counts["tables"] > 40 and counts["figures"] > 10
    assert differences == []
    more, _ = compare_trees(plain[2].cache / "checkpoints", watched[2].cache / "checkpoints")
    assert more == []


def test_the_monitored_run_used_the_shared_pool_and_the_plain_one_did_not(runs):
    plain, watched = runs
    assert plain[1]["workers"] == 1 and not plain[1]["shared_pool"]
    assert watched[1]["workers"] == 4 and watched[1]["shared_pool"]
    events = [json.loads(line) for line in
              watched[3].paths["events"].read_text().splitlines()]
    summary = [e for e in events if e["kind"] == "scheduler_summary"]
    assert summary and summary[0]["workers"] == 4 and 0 < summary[0]["utilization"] <= 1


def test_summaries_identical(runs):
    plain, watched = runs
    for key in ("stages", "n_files", "n_fit_records", "n_failure_events",
                "n_data_gap_events", "n_test_results"):
        assert plain[1][key] == watched[1][key], key


def test_every_planned_chain_ran_with_the_planned_origin_count(runs):
    _, (pipeline, _, _, monitor, _, _) = runs
    state = monitor.state
    ran = {task: c for task, c in state.chains.items() if c.status == "done"}
    skipped = {task for task, c in state.chains.items() if c.status == "skipped"}
    assert not [c for c in state.chains.values() if c.status in ("queued", "active",
                                                                  "failed")]
    for task, chain in ran.items():
        assert chain.completed == chain.plan.n_origins, task
    # Only provisional chains (GARCH where the ARCH screen did not reject, the VAR if
    # no stable lag existed) may be skipped.
    assert all(state.chains[t].plan.provisional for t in skipped)
    assert state.origin_counts()["remaining"] == 0
    assert not [w for w in state.warnings if "differ" in w["message"]
                or "not in the plan" in w["message"] or "were planned" in w["message"]]


def test_chain_counters_match_the_forecast_origin_audit(runs):
    """The monitor's per-chain counts equal the run's own audit table, row by row."""
    import pandas as pd

    _, (_, _, layout, monitor, _, _) = runs
    audit = pd.read_csv(layout.forecasts / "forecast_origin_audit.csv")
    assert len(audit) == 10                       # 2 targets x 5 models
    for row in audit.itertuples():
        chain = monitor.state.chains[f"forecasting:{row.series}|{row.model}"]
        assert chain.completed == row.attempted_origins
        assert chain.valid == row.valid_origins
        assert chain.failed == row.failed_origins
        assert chain.from_cache == row.origins_from_cache
        assert chain.gaps == row.n_data_gaps


def test_ten_stages_reported_in_order_and_complete(runs):
    _, (_, _, _, monitor, stream, _) = runs
    text = stream.getvalue()
    positions = [text.index(f"STAGE {s.number}/10 START: {s.name}") for s in STAGES]
    assert positions == sorted(positions)
    for stage in STAGES:
        assert f"STAGE {stage.number}/10 DONE: {stage.name}" in text
    snapshot = json.loads(monitor.paths["snapshot"].read_text())
    assert snapshot["status"] == "complete"
    assert snapshot["completed_stages"] == [s.key for s in STAGES]
    assert snapshot["outstanding_stages"] == []
    assert all(s["completed_tasks"] == s["planned_tasks"] for s in snapshot["stages"])


def test_monitor_files_are_outside_the_output_tree(runs):
    _, (_, _, layout, monitor, _, _) = runs
    assert not monitor.log_dir.is_relative_to(layout.root)
    names = {p.name for p in layout.root.rglob("*")}
    assert not names & {"execution.log", "events.jsonl", "progress.json"}
