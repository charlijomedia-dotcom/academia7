"""The probe hook and the parent-process monitor service.

The probe must be inert without a sink and transparent with one; the service must keep
its three files consistent (a log, an append-only event stream and an atomically
replaced snapshot), report long computations without calling them failures, and record
a failure or interruption so the last active calculation can be diagnosed afterwards.
"""

from __future__ import annotations

import io
import json
import time

import pytest

from thesis.monitoring import Monitor, NullMonitor, probe
from thesis.monitoring.plan import ChainPlan


@pytest.fixture(autouse=True)
def _clean_probe():
    probe.uninstall()
    yield
    probe.uninstall()


def _plan(task_id="forecasting:INDPRO|MSAR3", n=5) -> ChainPlan:
    return ChainPlan(task_id=task_id, batch="forecasting:INDPRO", stage="forecasting",
                     exercise="T4.3 K=3", role="robustness", series="INDPRO",
                     model="MSAR3", spec_label="MSAR(p=1,K=3)", k_regimes=3,
                     window_length=240, frequency="M", horizons=(1, 3), n_origins=n)


def _monitor(tmp_path, **kwargs) -> tuple[Monitor, io.StringIO]:
    stream = io.StringIO()
    defaults = dict(run_id="baseline-test", namespace="baseline", workers=4, stream=stream,
                    heartbeat_seconds=0.2, summary_seconds=0.6, snapshot_seconds=0.05,
                    tick_seconds=0.05)
    defaults.update(kwargs)
    return Monitor(tmp_path / "baseline" / "baseline-test", **defaults), stream


def _wait_for(predicate, timeout=5.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(0.02)
    return False


class TestProbe:
    def test_inert_without_a_sink(self):
        assert not probe.active()
        probe.emit("anything", x=1)
        probe.substep("start 1/3")
        with probe.operation("op"):
            pass
        reporter = probe.ChainReporter("t", 3)
        reporter.start()
        reporter.origin_start(1, "2000-01-01", "1980-01-01", "2000-01-01")
        reporter.origin_end("valid")
        reporter.end()

    def test_events_reach_the_sink_with_the_current_task(self):
        seen = []
        probe.install(seen.append)
        probe.set_task("task-1")
        probe.substep("Hessian")
        assert seen[-1]["kind"] == "substep" and seen[-1]["task_id"] == "task-1"
        assert {"t", "pid"} <= set(seen[-1])

    def test_operation_records_failure_and_reraises(self):
        seen = []
        probe.install(seen.append)
        with pytest.raises(ValueError):
            with probe.operation("MCS bootstrap", "INDPRO"):
                raise ValueError("x")
        assert seen[-1]["kind"] == "op_end" and seen[-1]["status"] == "error"

    def test_timed_is_transparent(self):
        seen = []

        def add(a, b, *, scale=1):
            return (a + b) * scale

        wrapped = probe.timed("addition", lambda *a, **k: "label")(add)
        assert wrapped(1, 2, scale=3) == 9                     # no sink: direct call
        probe.install(seen.append)
        assert wrapped(1, 2, scale=3) == 9
        assert [e["kind"] for e in seen] == ["op_start", "op_end"]
        assert wrapped.__wrapped__ is add

    def test_a_failing_sink_never_breaks_the_computation(self):
        def broken(event):
            raise RuntimeError("disk full")
        probe.install(broken)
        probe.emit("x")
        with probe.operation("y"):
            pass

    def test_chain_reporter_times_each_origin(self):
        seen = []
        probe.install(seen.append)
        reporter = probe.ChainReporter("t", 2, series="S", model="AR")
        reporter.start()
        reporter.origin_start(1, "2000-01-01", "1980-01-01", "2000-01-01")
        time.sleep(0.05)
        reporter.origin_end("valid", n_records=3)
        reporter.end(attempted=1)
        kinds = [e["kind"] for e in seen]
        assert kinds == ["chain_start", "origin_start", "origin_end", "chain_end"]
        assert seen[2]["seconds"] >= 0.04 and seen[2]["n_records"] == 3
        assert probe._task is None                        # reset at the end of the chain


class TestNullMonitor:
    def test_every_call_is_a_no_op(self):
        monitor = NullMonitor()
        assert not monitor.enabled
        with monitor.stage("data", planned_units=3):
            monitor.task("data", "x")
        with monitor.batch("b", ["t"]):
            pass
        monitor.plan([]), monitor.warn("w"), monitor.checkpoint("c")
        assert monitor.worker_channel() is None


class TestFiles:
    def test_log_events_and_snapshot_are_written(self, tmp_path):
        monitor, stream = _monitor(tmp_path)
        monitor.start()
        with monitor.stage("data", planned_units=1, detail={"series": ["INDPRO"]}):
            monitor.task("data", "INDPRO target")
        monitor.close("complete")

        log = monitor.paths["execution_log"].read_text()
        assert "STAGE 1/10 START" in log and "STAGE 1/10 DONE" in log
        assert log == stream.getvalue()                    # console and log agree
        events = [json.loads(line) for line in
                  monitor.paths["events"].read_text().splitlines()]
        kinds = [e["kind"] for e in events]
        assert kinds[0] == "run_start" and kinds[-1] == "run_end"
        assert "stage_start" in kinds and "stage_end" in kinds
        snapshot = json.loads(monitor.paths["snapshot"].read_text())
        assert snapshot["status"] == "complete"
        assert snapshot["completed_stages"] == ["data"]
        assert not list(monitor.log_dir.glob("*.tmp"))     # atomic replace left nothing
        assert (monitor.log_dir.parent / "LATEST").read_text().strip() == "baseline-test"

    def test_snapshot_is_refreshed_while_nothing_changes(self, tmp_path):
        monitor, _ = _monitor(tmp_path)
        monitor.start()
        first = json.loads(monitor.paths["snapshot"].read_text())["elapsed_seconds"]
        assert _wait_for(lambda: json.loads(
            monitor.paths["snapshot"].read_text())["elapsed_seconds"] > first)
        monitor.close()

    def test_mirror_appends_only_new_bytes(self, tmp_path):
        mirror = tmp_path / "drive"
        monitor, _ = _monitor(tmp_path / "local", mirror_dir=mirror, mirror_seconds=0.0)
        monitor.start()
        monitor.say("first line")
        monitor._mirror(force=True)
        monitor.say("second line")
        monitor.close()
        copy = mirror / "baseline" / "baseline-test"
        assert copy.joinpath("execution.log").read_text() == \
            monitor.paths["execution_log"].read_text()
        assert copy.joinpath("events.jsonl").read_text() == \
            monitor.paths["events"].read_text()
        assert json.loads(copy.joinpath("progress.json").read_text())["status"] == "complete"

    def test_an_unwritable_mirror_does_not_stop_the_run(self, tmp_path):
        blocker = tmp_path / "not-a-dir"
        blocker.write_text("x")
        monitor, _ = _monitor(tmp_path / "local", mirror_dir=blocker, mirror_seconds=0.0)
        monitor.start()
        monitor.say("still running")
        monitor.close()
        assert "log mirror unavailable" in monitor.paths["execution_log"].read_text()


class TestLongRunningAndFailures:
    def test_a_long_fit_is_reported_as_running_not_failed(self, tmp_path):
        monitor, stream = _monitor(tmp_path)
        monitor.start()
        monitor.plan([_plan()])
        monitor.emit("batch_start", batch="forecasting:INDPRO",
                     task_ids=["forecasting:INDPRO|MSAR3"])
        monitor.emit("chain_start", task_id="forecasting:INDPRO|MSAR3", n_origins=5, pid=4242)
        monitor.emit("origin_start", task_id="forecasting:INDPRO|MSAR3", index=1,
                     origin_date="2005-04-01", window_start="1985-05-01",
                     window_end="2005-04-01", pid=4242)
        monitor.emit("substep", task_id="forecasting:INDPRO|MSAR3",
                     label="MSAR K=3 likelihood maximization, start 2/3", pid=4242)
        assert _wait_for(lambda: "fit running" in stream.getvalue())
        text = stream.getvalue()
        assert "Worker 1: INDPRO | MSAR3 | origin 2005-04 | window 1985-05..2005-04" in text
        assert "start 2/3" in text
        snapshot = json.loads(monitor.paths["snapshot"].read_text())
        active = snapshot["active_tasks"][0]
        assert active["current_origin"] == "2005-04-01"
        assert active["current_fit_seconds"] is not None
        assert snapshot["n_failures"] == 0
        monitor.close()

    def test_a_failing_stage_is_recorded_and_reraised(self, tmp_path):
        monitor, stream = _monitor(tmp_path)
        monitor.start()
        with pytest.raises(RuntimeError):
            with monitor.stage("forecasting", planned_units=2):
                monitor.task("forecasting", "INDPRO: rolling chains")
                raise RuntimeError("worker crashed")
        monitor.close("failed", "RuntimeError: worker crashed")
        snapshot = json.loads(monitor.paths["snapshot"].read_text())
        assert snapshot["status"] == "failed"
        stage = next(s for s in snapshot["stages"] if s["key"] == "forecasting")
        assert stage["status"] == "failed"
        assert "worker crashed" in stage["errors"][0]
        assert "STAGE 7/10 FAILED" in stream.getvalue()

    def test_interruption_leaves_the_last_active_calculation_in_the_snapshot(self, tmp_path):
        monitor, _ = _monitor(tmp_path)
        monitor.start()
        monitor.plan([_plan()])
        monitor.emit("chain_start", task_id="forecasting:INDPRO|MSAR3", n_origins=5)
        monitor.emit("origin_start", task_id="forecasting:INDPRO|MSAR3", index=3,
                     origin_date="2010-06-01", window_start="1990-07-01",
                     window_end="2010-06-01")
        monitor.close("interrupted", "KeyboardInterrupt")
        snapshot = json.loads(monitor.paths["snapshot"].read_text())
        assert snapshot["status"] == "interrupted"
        assert snapshot["active_tasks"][0]["current_origin"] == "2010-06-01"
        last = json.loads(monitor.paths["events"].read_text().splitlines()[-1])
        assert last["kind"] == "run_end" and last["status"] == "interrupted"

    def test_close_is_idempotent(self, tmp_path):
        monitor, _ = _monitor(tmp_path)
        monitor.start()
        monitor.close()
        monitor.close()
        assert not probe.active()

    def test_summary_appears_on_its_interval(self, tmp_path):
        monitor, stream = _monitor(tmp_path)
        monitor.start()
        assert _wait_for(lambda: "GLOBAL SUMMARY" in stream.getvalue())
        monitor.close()


def test_periods_display_like_the_data():
    from thesis.monitoring.render import period
    assert period("2017-04-01", "Q") == "2017Q2"
    assert period("2017-12-01", "Q") == "2017Q4"
    assert period("2005-04-01", "M") == "2005-04"
    assert period("", "M") == "-"
