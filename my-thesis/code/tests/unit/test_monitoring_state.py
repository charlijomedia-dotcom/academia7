"""The progress state: counters must match what was computed, and never lie.

The state changes only by applying events, so these tests drive it with event sequences
and check every derived number: completed and remaining origins, valid and failed
estimations, forecast records, stage tasks, and the conditions under which a remaining
count may reach zero.
"""

from __future__ import annotations

import pytest

from thesis.monitoring.plan import STAGES, ChainPlan
from thesis.monitoring.state import MIN_TIMING_SAMPLES, RunState, fmt_duration


def plan(task_id="b|AR", *, batch="b", stage="forecasting", model="AR", n=10,
         role="baseline", frequency="M", provisional=False, expect_cached=False,
         runs_in="pool", horizons=(1, 3)) -> dict:
    return ChainPlan(task_id=task_id, batch=batch, stage=stage, exercise="baseline",
                     role=role, series="INDPRO", model=model, spec_label=f"{model}(p=1)",
                     k_regimes=None, window_length=240, frequency=frequency,
                     horizons=tuple(horizons), n_origins=n, provisional=provisional,
                     expect_cached=expect_cached, runs_in=runs_in).to_dict()


class Clock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self, kind, **fields):
        self.t += 1.0
        return {"kind": kind, "t": self.t, "pid": fields.pop("pid", 1), **fields}


@pytest.fixture
def clock():
    return Clock()


def run(state, clock, n_valid=0, n_failed=0, n_gap=0, n_cached=0, task="b|AR",
        seconds=2.0, records=2):
    for status, count in (("valid", n_valid), ("failed", n_failed), ("gap", n_gap)):
        for _ in range(count):
            state.apply(clock("origin_start", task_id=task, origin_date="2000-01-01",
                              window_start="1980-02-01", window_end="2000-01-01"))
            state.apply(clock("origin_end", task_id=task, status=status, from_cache=False,
                              seconds=seconds, n_records=records if status != "gap" else 0))
    for _ in range(n_cached):
        state.apply(clock("origin_start", task_id=task, origin_date="2000-01-01",
                          window_start="", window_end=""))
        state.apply(clock("origin_end", task_id=task, status="valid", from_cache=True,
                          seconds=0.001, n_records=records))


@pytest.fixture
def state(clock):
    s = RunState()
    s.apply(clock("run_start", run_id="r", namespace="baseline", workers=4))
    s.apply(clock("plan", chains=[plan()]))
    s.apply(clock("chain_start", task_id="b|AR", n_origins=10))
    return s


class TestStagePlan:
    def test_ten_stages_in_execution_order(self):
        assert [s.number for s in STAGES] == list(range(1, 11))
        assert STAGES[0].key == "data" and STAGES[-1].key == "finalize"

    def test_execution_number_and_methodology_are_separate_fields(self):
        forecasting = next(s for s in STAGES if s.key == "forecasting")
        assert forecasting.number == 7
        assert forecasting.methodology == "Part 5 §9"
        assert forecasting.checkpoint == "forecasts"

    def test_specification_runs_twice_under_distinct_keys(self):
        keys = [s.key for s in STAGES]
        assert len(keys) == len(set(keys))
        assert {"specification_preliminary", "specification"} <= set(keys)


class TestOriginCounting:
    def test_counts_match_the_origins_applied(self, state, clock):
        run(state, clock, n_valid=4, n_failed=2, n_gap=1)
        chain = state.chains["b|AR"]
        assert (chain.completed, chain.valid, chain.failed, chain.gaps) == (7, 4, 2, 1)
        assert chain.remaining == 3
        assert chain.n_records == 12          # gaps produce no forecast record

    def test_fits_and_records_are_distinct_units(self, state, clock):
        # One fit at an origin produces one record per realizable horizon.
        run(state, clock, n_valid=3, records=4)
        counts = state.origin_counts()
        assert counts["fitted"] == 3
        assert counts["forecast_records"] == 12

    def test_cached_origins_are_complete_but_not_timed(self, state, clock):
        run(state, clock, n_valid=2, seconds=5.0)
        run(state, clock, n_cached=3)
        chain = state.chains["b|AR"]
        assert chain.completed == 5 and chain.from_cache == 3 and chain.fitted == 2
        assert chain.mean_fit_seconds() == pytest.approx(5.0)

    def test_data_gaps_do_not_enter_fit_timing(self, state, clock):
        run(state, clock, n_gap=3)
        assert state.chains["b|AR"].fitted == 0
        assert state.timing == {}


class TestRemainingNeverLies:
    def test_remaining_is_never_negative_and_overruns_are_reported(self, state, clock):
        run(state, clock, n_valid=13)
        chain = state.chains["b|AR"]
        assert chain.remaining == 0
        assert chain.plan.n_origins == 13           # the total was raised, not clipped
        assert any("were planned" in w["message"] for w in state.warnings)

    def test_remaining_reaches_zero_only_when_the_chain_ends(self, state, clock):
        run(state, clock, n_valid=10)
        chain = state.chains["b|AR"]
        assert chain.remaining == 0 and chain.status == "active"
        state.apply(clock("chain_end", task_id="b|AR"))
        assert chain.status == "done"

    def test_global_remaining_counts_queued_chains(self, clock):
        s = RunState()
        s.apply(clock("plan", chains=[plan("b|AR", n=10), plan("b|MSAR", model="MSAR", n=7),
                                      plan("c|AR", batch="c", stage="robustness", n=5,
                                           role="robustness")]))
        assert s.origin_counts()["remaining"] == 22
        assert s.origin_counts("baseline")["remaining"] == 17
        assert s.origin_counts("robustness")["remaining"] == 5

    def test_global_remaining_is_zero_only_when_every_chain_is_closed(self, clock):
        s = RunState()
        s.apply(clock("plan", chains=[plan("b|AR", n=2), plan("b|MSAR", model="MSAR", n=2)]))
        s.apply(clock("chain_start", task_id="b|AR"))
        run(s, clock, n_valid=2, task="b|AR")
        s.apply(clock("chain_end", task_id="b|AR"))
        assert s.origin_counts()["remaining"] == 2      # MSAR has not started
        s.apply(clock("chain_start", task_id="b|MSAR"))
        run(s, clock, n_valid=2, task="b|MSAR")
        s.apply(clock("chain_end", task_id="b|MSAR"))
        assert s.origin_counts()["remaining"] == 0

    def test_skipped_chains_leave_the_total_explicitly(self, clock):
        s = RunState()
        s.apply(clock("plan", chains=[plan("g|GARCH", batch="g", stage="robustness",
                                           model="ARMA-GARCH", n=50, provisional=True)]))
        assert s.chain_counts()["provisional"] == 1
        s.apply(clock("chain_skipped", task_id="g|GARCH", reason="ARCH-LM did not reject"))
        assert s.origin_counts()["remaining"] == 0
        assert s.chains["g|GARCH"].status == "skipped"

    def test_a_finished_stage_skips_its_unrun_chains(self, clock):
        s = RunState()
        s.apply(clock("plan", chains=[plan("g|GARCH", batch="g", stage="robustness", n=9)]))
        s.apply(clock("stage_start", stage="robustness"))
        s.apply(clock("stage_end", stage="robustness", status="done"))
        assert s.chains["g|GARCH"].status == "skipped"
        assert s.origin_counts()["remaining"] == 0

    def test_a_failed_stage_does_not_mark_its_chains_skipped(self, clock):
        s = RunState()
        s.apply(clock("plan", chains=[plan("g|GARCH", batch="g", stage="robustness", n=9)]))
        s.apply(clock("stage_start", stage="robustness"))
        s.apply(clock("stage_end", stage="robustness", status="failed", error="boom"))
        assert s.chains["g|GARCH"].status == "queued"
        assert s.origin_counts()["remaining"] == 9
        assert s.failures and s.failures[-1]["error"] == "boom"

    def test_engine_count_revises_a_provisional_plan_silently(self, clock):
        s = RunState()
        s.apply(clock("plan", chains=[plan("v|VAR", n=100, provisional=True)]))
        s.apply(clock("chain_start", task_id="v|VAR", n_origins=97))
        assert s.chains["v|VAR"].plan.n_origins == 97
        assert not s.warnings

    def test_engine_count_disagreeing_with_an_exact_plan_is_warned(self, clock):
        s = RunState()
        s.apply(clock("plan", chains=[plan("b|AR", n=100)]))
        s.apply(clock("chain_start", task_id="b|AR", n_origins=97))
        assert s.chains["b|AR"].plan.n_origins == 97
        assert any("engine reports 97" in w["message"] for w in s.warnings)


class TestAuthoritativeReconciliation:
    def test_result_counts_win_and_disagreement_is_recorded(self, state, clock):
        run(state, clock, n_valid=3)                 # events for 3 origins arrived
        state.apply(clock("chain_result", task_id="b|AR", attempted=10, valid=9, failed=1,
                          from_cache=0, n_records=18, gaps=0))
        chain = state.chains["b|AR"]
        assert (chain.completed, chain.valid, chain.failed) == (10, 9, 1)
        assert chain.status == "done"
        assert any("differ from the chain result" in w["message"] for w in state.warnings)

    def test_agreeing_result_adds_no_warning(self, state, clock):
        run(state, clock, n_valid=10, records=2)
        state.apply(clock("chain_end", task_id="b|AR"))
        state.apply(clock("chain_result", task_id="b|AR", attempted=10, valid=10, failed=0,
                          from_cache=0, n_records=20, gaps=0))
        assert not state.warnings

    def test_a_chain_error_is_a_failure_not_a_completion(self, state, clock):
        run(state, clock, n_valid=4)
        state.apply(clock("chain_error", task_id="b|AR", error="ValueError: x"))
        chain = state.chains["b|AR"]
        assert chain.status == "failed" and chain.remaining == 0
        assert state.failures[-1]["task_id"] == "b|AR"
        assert state.chain_counts()["failed"] == 1


class TestStageTasks:
    def test_each_new_task_completes_the_previous_one(self, clock):
        s = RunState()
        s.apply(clock("stage_start", stage="adequacy", planned_units=3))
        for label in ("a", "b", "c"):
            s.apply(clock("task", stage="adequacy", label=label))
        assert s.stages["adequacy"].completed_units == 2
        s.apply(clock("stage_end", stage="adequacy", status="done"))
        assert s.stages["adequacy"].completed_units == 3

    def test_a_failed_stage_does_not_count_its_last_task_as_done(self, clock):
        s = RunState()
        s.apply(clock("stage_start", stage="adequacy", planned_units=3))
        s.apply(clock("task", stage="adequacy", label="a"))
        s.apply(clock("stage_end", stage="adequacy", status="failed", error="x"))
        assert s.stages["adequacy"].completed_units == 0

    def test_more_tasks_than_planned_raise_the_total_with_a_warning(self, clock):
        s = RunState()
        s.apply(clock("stage_start", stage="data", planned_units=1))
        for label in ("a", "b", "c"):
            s.apply(clock("task", stage="data", label=label))
        assert s.stages["data"].planned_units == 2
        assert s.warnings

    def test_stage_counts(self, clock):
        s = RunState()
        s.apply(clock("stage_start", stage="data"))
        s.apply(clock("stage_end", stage="data", status="done"))
        s.apply(clock("stage_start", stage="stationarity"))
        assert s.stage_counts() == {"total": 10, "done": 1, "failed": 0, "active": 1}
        assert s.next_work().startswith("stage 3/10")


class TestWorkersAndSubsteps:
    def test_workers_get_stable_slots_per_batch(self, clock):
        s = RunState()
        s.apply(clock("plan", chains=[plan(f"b|M{i}", model=f"M{i}") for i in range(4)]))
        s.apply(clock("batch_start", batch="b", task_ids=[f"b|M{i}" for i in range(4)]))
        for i, pid in enumerate((501, 502, 503, 501)):
            s.apply(clock("chain_start", task_id=f"b|M{i}", pid=pid))
        slots = [s.slot_of(s.chains[f"b|M{i}"]) for i in range(4)]
        assert slots == [1, 2, 3, 1]

    def test_substep_attaches_to_its_chain(self, state, clock):
        state.apply(clock("origin_start", task_id="b|AR", origin_date="2001-01-01",
                          window_start="", window_end=""))
        state.apply(clock("substep", task_id="b|AR", label="start 2/3"))
        assert state.chains["b|AR"].substep == "start 2/3"
        state.apply(clock("origin_end", task_id="b|AR", status="valid", seconds=1.0))
        assert state.chains["b|AR"].substep == ""

    def test_substep_without_a_chain_attaches_to_the_stage_task(self, clock):
        s = RunState()
        s.apply(clock("stage_start", stage="adequacy"))
        s.apply(clock("task", stage="adequacy", label="INDPRO MSAR3"))
        s.apply(clock("substep", label="Hessian"))
        assert s.stages["adequacy"].unit_substep == "Hessian"

    def test_longest_running_names_the_active_fit(self, state, clock):
        state.apply(clock("origin_start", task_id="b|AR", origin_date="2005-04-01",
                          window_start="", window_end=""))
        longest = state.longest_running(state.chains["b|AR"].origin_started + 90)
        assert longest["seconds"] == pytest.approx(90)
        assert "2005-04-01" in longest["what"]

    def test_heartbeats_are_liveness_not_progress(self, state, clock):
        before = state.last_progress
        state.apply(clock("worker_heartbeat", pid=7, cpu_seconds=12.0, rss_mb=100.0))
        assert state.last_progress == before
        assert state.workers_seen[7]["cpu_seconds"] == 12.0


class TestEstimate:
    def test_no_estimate_without_enough_timed_fits(self, state, clock):
        run(state, clock, n_valid=MIN_TIMING_SAMPLES - 1)
        estimate = state.estimate_remaining()
        assert not estimate["available"]
        assert "AR/M" in estimate["reason"]

    def test_untimed_work_is_named_not_guessed(self, clock):
        s = RunState()
        s.apply(clock("run_start", workers=4))
        s.apply(clock("plan", chains=[plan("b|AR", n=20), plan("b|MSAR3", model="MSAR3",
                                                                n=20)]))
        s.apply(clock("chain_start", task_id="b|AR"))
        run(s, clock, n_valid=10, task="b|AR", seconds=1.0)
        estimate = s.estimate_remaining()
        assert estimate["available"]
        assert estimate["untimed"] == {"MSAR3/M": 20}
        assert estimate["timed_share"] == pytest.approx(10 / 30)
        assert estimate["fit_cpu_seconds"] == pytest.approx(10.0)

    def test_no_estimate_when_nothing_remaining_is_timed(self, clock):
        s = RunState()
        s.apply(clock("plan", chains=[plan("b|MSAR3", model="MSAR3", n=20)]))
        estimate = s.estimate_remaining()
        assert not estimate["available"] and "MSAR3/M" in estimate["reason"]

    def test_estimate_is_a_batch_scheduling_lower_bound(self, clock):
        s = RunState()
        s.apply(clock("run_start", workers=4))
        s.apply(clock("plan", chains=[plan("b|AR", n=10), plan("b|MSAR", model="MSAR", n=10)]))
        for task in ("b|AR", "b|MSAR"):
            s.apply(clock("chain_start", task_id=task))
        run(s, clock, n_valid=5, task="b|AR", seconds=1.0)
        run(s, clock, n_valid=5, task="b|MSAR", seconds=10.0)
        estimate = s.estimate_remaining()
        assert estimate["available"]
        assert estimate["fit_cpu_seconds"] == pytest.approx(5 * 1.0 + 5 * 10.0)
        # Two chains on four workers: bounded by the longest chain, 50 s.
        assert estimate["fit_wall_seconds_lower_bound"] == pytest.approx(50.0)

    def test_chains_expected_from_cache_cost_nothing(self, clock):
        s = RunState()
        s.apply(clock("run_start", workers=4))
        s.apply(clock("plan", chains=[plan("b|AR", n=10),
                                      plan("c|AR", batch="c", n=10, expect_cached=True)]))
        s.apply(clock("chain_start", task_id="b|AR"))
        run(s, clock, n_valid=5, task="b|AR", seconds=1.0)
        assert s.estimate_remaining()["fit_cpu_seconds"] == pytest.approx(5.0)

    def test_parent_chains_run_one_at_a_time(self, clock):
        s = RunState()
        s.apply(clock("run_start", workers=4))
        s.apply(clock("plan", chains=[plan("g|A", batch="g", n=10, runs_in="parent"),
                                      plan("g|B", batch="g", n=10, runs_in="parent")]))
        s.apply(clock("chain_start", task_id="g|A"))
        run(s, clock, n_valid=5, task="g|A", seconds=2.0)
        estimate = s.estimate_remaining()
        assert estimate["fit_wall_seconds_lower_bound"] == pytest.approx(10.0 + 20.0)


def test_fmt_duration():
    assert fmt_duration(5) == "5s"
    assert fmt_duration(65) == "1m05s"
    assert fmt_duration(3725) == "1h02m05s"
    assert fmt_duration(None) == "n/a"
    assert fmt_duration(-3) == "0s"


def test_stage_registry_additions_are_reported(clock):
    from thesis.monitoring.render import stage_end

    s = RunState()
    s.apply(clock("stage_start", stage="adequacy"))
    s.apply(clock("stage_registry", stage="adequacy", failed=1, fragile=4, data_gaps=0))
    s.apply(clock("stage_end", stage="adequacy", status="done"))
    assert s.stages["adequacy"].registry == {"failed": 1, "fragile": 4, "data_gaps": 0}
    assert "1 failed estimations, 4 fragility flags" in stage_end(s, s.stages["adequacy"],
                                                                 s.stages["adequacy"].ended)
