"""Run progress state, changed only by applying events.

Everything the console, the execution log and the progress snapshot report is derived
from this one object, and it changes only through `apply(event)`. That makes it
deterministic given an event sequence, which is how it is tested: feed events, compare
the counters with what was actually computed.

Two invariants are enforced rather than hoped for:

* a remaining count is never negative. If more origins complete than were planned, the
  plan was wrong; the total is raised to the observed count and a warning is recorded,
  so the discrepancy is visible instead of being clipped away silently;
* a remaining count reaches zero only when every non-skipped planned chain has ended.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from .plan import STAGE_BY_KEY, STAGES, ChainPlan

#: Fits needed per (model, frequency) before its mean fit time is used in an estimate.
MIN_TIMING_SAMPLES = 5


@dataclass
class StageState:
    number: int
    key: str
    name: str
    checkpoint: str
    methodology: str
    operations: str
    status: str = "pending"            # pending | active | done | failed
    started: float | None = None
    ended: float | None = None
    planned_units: int | None = None
    completed_units: int = 0
    unit_label: str = ""
    unit_started: float | None = None
    unit_substep: str = ""
    errors: list[str] = field(default_factory=list)
    registry: dict[str, int] = field(default_factory=dict)   # failure-register additions

    def elapsed(self, now: float) -> float:
        if self.started is None:
            return 0.0
        return (self.ended or now) - self.started


@dataclass
class ChainState:
    plan: ChainPlan
    status: str = "queued"             # queued | active | done | failed | skipped
    completed: int = 0                 # origins finished (fitted, cached or data gap)
    valid: int = 0
    failed: int = 0
    gaps: int = 0
    from_cache: int = 0
    n_records: int = 0                 # horizon-specific forecast records emitted
    fitted: int = 0                    # origins actually estimated (not from cache)
    fit_seconds: float = 0.0           # total time of the fitted origins
    max_fit_seconds: float = 0.0
    current_origin: str = ""
    window_start: str = ""
    window_end: str = ""
    origin_index: int = 0
    origin_started: float | None = None
    substep: str = ""
    substep_started: float | None = None
    pid: int | None = None
    started: float | None = None
    ended: float | None = None
    last_event: float | None = None
    note: str = ""

    @property
    def remaining(self) -> int:
        if self.status in ("done", "failed", "skipped"):
            return 0
        return max(0, self.plan.n_origins - self.completed)

    def mean_fit_seconds(self) -> float | None:
        return self.fit_seconds / self.fitted if self.fitted else None


@dataclass
class Operation:
    category: str
    label: str
    started: float
    pid: int | None
    task_id: str | None


@dataclass
class OperationStats:
    count: int = 0
    seconds: float = 0.0
    max_seconds: float = 0.0
    errors: int = 0


class RunState:
    """The whole run's progress, rebuilt from events."""

    def __init__(self) -> None:
        self.run_id = ""
        self.namespace = ""
        self.workers = 1
        self.started: float | None = None
        self.ended: float | None = None
        self.status = "starting"
        self.stages: dict[str, StageState] = {
            s.key: StageState(s.number, s.key, s.name, s.checkpoint, s.methodology,
                              s.operations) for s in STAGES}
        self.current_stage: str | None = None
        self.chains: dict[str, ChainState] = {}
        self.batches: dict[str, list[str]] = {}
        self.active_batch: str | None = None
        self.operations: dict[str, OperationStats] = {}
        self.active_ops: dict[tuple, Operation] = {}
        self.timing: dict[tuple[str, str], list[float]] = {}   # (model, freq) -> [n, sec]
        self.slowest: list[dict[str, Any]] = []
        self.workers_seen: dict[int, dict[str, Any]] = {}
        self.slots: dict[int, int] = {}
        self.warnings: list[dict[str, Any]] = []
        self.failures: list[dict[str, Any]] = []
        self.last_progress: float | None = None
        self.last_progress_what = ""
        self.last_event: float | None = None
        self.last_checkpoint: dict[str, Any] | None = None
        self.n_events = 0

    # -- event application ------------------------------------------------

    def apply(self, event: dict[str, Any]) -> None:
        handler = getattr(self, f"_on_{event.get('kind')}", None)
        self.n_events += 1
        self.last_event = event.get("t", self.last_event)
        if handler is not None:
            handler(event)

    def _progress(self, event: dict[str, Any], what: str) -> None:
        self.last_progress = event["t"]
        self.last_progress_what = what

    def _warn(self, t: float, message: str, **extra: Any) -> None:
        self.warnings.append({"t": t, "message": message, **extra})
        del self.warnings[:-200]

    def _on_run_start(self, e):
        self.run_id = e.get("run_id", "")
        self.namespace = e.get("namespace", "")
        self.workers = int(e.get("workers", 1))
        self.started = e["t"]
        self.status = "running"

    def _on_run_end(self, e):
        self.ended = e["t"]
        self.status = e.get("status", "complete")

    def _on_stage_start(self, e):
        stage = self.stages[e["stage"]]
        stage.status, stage.started, stage.ended = "active", e["t"], None
        stage.completed_units, stage.unit_label, stage.unit_started = 0, "", None
        if e.get("planned_units") is not None:
            stage.planned_units = int(e["planned_units"])
        self.current_stage = stage.key
        self._progress(e, f"stage {stage.number} started")

    def _on_stage_registry(self, e):
        self.stages[e["stage"]].registry = {k: int(e.get(k, 0))
                                            for k in ("failed", "fragile", "data_gaps")}

    def _on_stage_units(self, e):
        self.stages[e["stage"]].planned_units = int(e["planned_units"])

    def _on_stage_end(self, e):
        stage = self.stages[e["stage"]]
        if stage.unit_label and e.get("status", "done") == "done":
            stage.completed_units += 1
        stage.unit_label, stage.unit_started, stage.unit_substep = "", None, ""
        stage.status = e.get("status", "done")
        stage.ended = e["t"]
        if e.get("error"):
            stage.errors.append(e["error"])
            self.failures.append({"t": e["t"], "stage": stage.key, "error": e["error"]})
        # Chains planned for this stage that never ran were not needed (an ARCH screen
        # that did not reject, say): they leave the remaining total, explicitly.
        if stage.status == "done":
            for chain in self.chains.values():
                if chain.plan.stage == stage.key and chain.status == "queued":
                    chain.status, chain.note = "skipped", "not run by its stage"
        self._progress(e, f"stage {stage.number} {stage.status}")

    def _on_task(self, e):
        stage = self.stages[e["stage"]]
        if stage.unit_label:
            stage.completed_units += 1
        stage.unit_label = e.get("label", "")
        stage.unit_started = e["t"]
        stage.unit_substep = ""
        if stage.planned_units is not None and stage.completed_units > stage.planned_units:
            self._warn(e["t"], f"stage {stage.key}: more units than planned; total revised",
                       planned=stage.planned_units, observed=stage.completed_units)
            stage.planned_units = stage.completed_units
        self._progress(e, f"{stage.name}: {stage.unit_label}")

    def _on_checkpoint(self, e):
        self.last_checkpoint = {"name": e.get("name"), "t": e["t"]}

    def _on_warning(self, e):
        self._warn(e["t"], e.get("message", ""), **{k: v for k, v in e.items()
                                                     if k not in ("t", "kind", "message")})

    def _on_plan(self, e):
        for raw in e.get("chains", []):
            plan = ChainPlan(**{**raw, "horizons": tuple(raw["horizons"])})
            existing = self.chains.get(plan.task_id)
            if existing is None:
                self.chains[plan.task_id] = ChainState(plan)
                self.batches.setdefault(plan.batch, []).append(plan.task_id)
            elif existing.status == "queued":
                existing.plan = plan                     # a revision of a provisional plan

    def _on_batch_start(self, e):
        self.active_batch = e["batch"]
        self.slots = {}
        for task_id in e.get("task_ids", []):
            if task_id not in self.chains:
                self._warn(e["t"], f"chain {task_id} was not in the plan; added")

    def _on_batch_end(self, e):
        if self.active_batch == e["batch"]:
            self.active_batch = None
        self.slots = {}

    def _chain(self, e) -> ChainState | None:
        chain = self.chains.get(e.get("task_id"))
        if chain is None and e.get("kind") == "chain_start" and e.get("plan"):
            raw = e["plan"]
            plan = ChainPlan(**{**raw, "horizons": tuple(raw["horizons"])})
            chain = self.chains[plan.task_id] = ChainState(plan)
            self.batches.setdefault(plan.batch, []).append(plan.task_id)
        return chain

    def _slot(self, pid: int | None) -> int | None:
        if pid is None:
            return None
        if pid not in self.slots:
            self.slots[pid] = len(self.slots) + 1
        return self.slots[pid]

    def _on_chain_start(self, e):
        chain = self._chain(e)
        if chain is None:
            return
        n = e.get("n_origins")
        if n is not None and int(n) != chain.plan.n_origins:
            if not chain.plan.provisional:
                self._warn(e["t"], f"{chain.plan.task_id}: planned {chain.plan.n_origins} "
                                   f"origins, engine reports {n}; total revised")
            chain.plan.n_origins = int(n)
            chain.plan.provisional = False
        chain.status, chain.started, chain.pid = "active", e["t"], e.get("pid")
        chain.last_event = e["t"]
        self._slot(chain.pid)
        self._progress(e, f"chain started: {chain.plan.series} {chain.plan.model}")

    def _on_origin_start(self, e):
        chain = self._chain(e)
        if chain is None:
            return
        chain.current_origin = e.get("origin_date", "")
        chain.window_start = e.get("window_start", "")
        chain.window_end = e.get("window_end", "")
        chain.origin_index = int(e.get("index", chain.completed + 1))
        chain.origin_started = e["t"]
        chain.substep, chain.substep_started = "", None
        chain.last_event = e["t"]

    def _on_origin_end(self, e):
        chain = self._chain(e)
        if chain is None:
            return
        chain.completed += 1
        status = e.get("status", "")
        if status == "gap":
            chain.gaps += 1
        elif status == "failed":
            chain.failed += 1
        else:
            chain.valid += 1
        if e.get("from_cache"):
            chain.from_cache += 1
        else:
            seconds = float(e.get("seconds") or 0.0)
            if status != "gap":
                chain.fitted += 1
                chain.fit_seconds += seconds
                chain.max_fit_seconds = max(chain.max_fit_seconds, seconds)
                key = (chain.plan.model, chain.plan.frequency)
                bucket = self.timing.setdefault(key, [0, 0.0])
                bucket[0] += 1
                bucket[1] += seconds
                self._note_slow(chain, e, seconds)
        chain.n_records += int(e.get("n_records", 0))
        chain.origin_started, chain.substep, chain.substep_started = None, "", None
        chain.last_event = e["t"]
        if chain.completed > chain.plan.n_origins:
            self._warn(e["t"], f"{chain.plan.task_id}: completed {chain.completed} origins "
                               f"but {chain.plan.n_origins} were planned; total revised")
            chain.plan.n_origins = chain.completed
        self._progress(e, f"{chain.plan.series} {chain.plan.model} origin "
                          f"{chain.current_origin} done")

    def _note_slow(self, chain: ChainState, e, seconds: float) -> None:
        self.slowest.append({"seconds": round(seconds, 3), "series": chain.plan.series,
                             "model": chain.plan.model, "exercise": chain.plan.exercise,
                             "origin": chain.current_origin})
        if len(self.slowest) > 50:
            self.slowest.sort(key=lambda r: -r["seconds"])
            del self.slowest[10:]

    def _on_substep(self, e):
        chain = self.chains.get(e.get("task_id"))
        if chain is not None:
            chain.substep, chain.substep_started = e.get("label", ""), e["t"]
            chain.last_event = e["t"]
        elif self.current_stage is not None:
            # A substep of a serial task in the parent (a full-sample fit, say).
            self.stages[self.current_stage].unit_substep = e.get("label", "")

    def _close_chain(self, chain: ChainState, e, status: str) -> None:
        chain.status, chain.ended = status, e["t"]
        chain.origin_started, chain.substep = None, ""

    def _on_chain_end(self, e):
        chain = self._chain(e)
        if chain is None:
            return
        self._close_chain(chain, e, "done")
        self._progress(e, f"chain finished: {chain.plan.series} {chain.plan.model}")

    def _on_chain_result(self, e):
        """The parent's authoritative count from the returned ChainResult.

        Events can in principle be lost (a worker killed mid-write); the result cannot.
        Any disagreement is recorded, and the authoritative numbers win.
        """
        chain = self.chains.get(e.get("task_id"))
        if chain is None:
            return
        observed = {"completed": chain.completed, "valid": chain.valid,
                    "failed": chain.failed, "from_cache": chain.from_cache,
                    "n_records": chain.n_records}
        truth = {"completed": int(e["attempted"]), "valid": int(e["valid"]),
                 "failed": int(e["failed"]), "from_cache": int(e["from_cache"]),
                 "n_records": int(e["n_records"])}
        if observed != truth:
            self._warn(e["t"], f"{chain.plan.task_id}: event counts {observed} differ from "
                               f"the chain result {truth}; result used")
        for name, value in truth.items():
            setattr(chain, name, value)
        chain.gaps = int(e.get("gaps", chain.gaps))
        if chain.completed > chain.plan.n_origins:
            chain.plan.n_origins = chain.completed
        if chain.status != "done":
            self._close_chain(chain, e, "done")

    def _on_chain_error(self, e):
        chain = self.chains.get(e.get("task_id"))
        if chain is not None:
            self._close_chain(chain, e, "failed")
            chain.note = e.get("error", "")
        self.failures.append({"t": e["t"], "task_id": e.get("task_id"),
                              "error": e.get("error", "")})

    def _on_chain_skipped(self, e):
        chain = self.chains.get(e.get("task_id"))
        if chain is not None and chain.status == "queued":
            chain.status, chain.note = "skipped", e.get("reason", "")

    def _on_op_start(self, e):
        key = (e.get("pid"), e.get("category"), e.get("label"), e.get("task_id"))
        self.active_ops[key] = Operation(e.get("category", ""), e.get("label", ""), e["t"],
                                         e.get("pid"), e.get("task_id"))

    def _on_op_end(self, e):
        key = (e.get("pid"), e.get("category"), e.get("label"), e.get("task_id"))
        self.active_ops.pop(key, None)
        stats = self.operations.setdefault(e.get("category", ""), OperationStats())
        seconds = float(e.get("seconds") or 0.0)
        stats.count += 1
        stats.seconds += seconds
        stats.max_seconds = max(stats.max_seconds, seconds)
        if e.get("status") == "error":
            stats.errors += 1
        self._progress(e, f"{e.get('category')} {e.get('label', '')}".strip())

    def _on_worker_heartbeat(self, e):
        self.workers_seen[e["pid"]] = {"t": e["t"], "cpu_seconds": e.get("cpu_seconds"),
                                       "rss_mb": e.get("rss_mb"),
                                       "task_id": e.get("task_id")}

    # -- derived quantities ----------------------------------------------

    def stage_counts(self) -> dict[str, int]:
        statuses = [s.status for s in self.stages.values()]
        return {"total": len(statuses), "done": statuses.count("done"),
                "failed": statuses.count("failed"), "active": statuses.count("active")}

    def chain_counts(self, role: str | None = None) -> dict[str, int]:
        out = {"planned": 0, "done": 0, "active": 0, "queued": 0, "failed": 0,
               "skipped": 0, "provisional": 0}
        for chain in self.chains.values():
            if role is not None and chain.plan.role != role:
                continue
            out["planned"] += 1
            out[chain.status] += 1
            if chain.plan.provisional and chain.status == "queued":
                out["provisional"] += 1
        return out

    def origin_counts(self, role: str | None = None) -> dict[str, int]:
        planned = completed = remaining = fitted = cached = records = 0
        for chain in self.chains.values():
            if role is not None and chain.plan.role != role:
                continue
            if chain.status == "skipped":
                continue
            planned += max(chain.plan.n_origins, chain.completed)
            completed += chain.completed
            remaining += chain.remaining
            fitted += chain.fitted
            cached += chain.from_cache
            records += chain.n_records
        return {"planned": planned, "completed": completed, "remaining": remaining,
                "fitted": fitted, "from_cache": cached, "forecast_records": records}

    def active_chains(self) -> list[ChainState]:
        return sorted((c for c in self.chains.values() if c.status == "active"),
                      key=lambda c: self.slots.get(c.pid or -1, 99))

    def slot_of(self, chain: ChainState) -> int | None:
        return self.slots.get(chain.pid) if chain.pid is not None else None

    def longest_running(self, now: float) -> dict[str, Any] | None:
        best = None
        for chain in self.active_chains():
            if chain.origin_started is not None:
                age = now - chain.origin_started
                if best is None or age > best["seconds"]:
                    best = {"seconds": age, "what": f"{chain.plan.series} {chain.plan.model} "
                            f"fit at origin {chain.current_origin}"
                            + (f" [{chain.substep}]" if chain.substep else "")}
        for op in self.active_ops.values():
            age = now - op.started
            if best is None or age > best["seconds"]:
                best = {"seconds": age, "what": f"{op.category} {op.label}".strip()}
        # A stage task (a whole batch of chains, say) is reported only when no fit or
        # operation inside it is running: the individual computation is more useful.
        if best is not None:
            return best
        for stage in self.stages.values():
            if stage.status == "active" and stage.unit_started is not None and stage.unit_label:
                age = now - stage.unit_started
                if best is None or age > best["seconds"]:
                    best = {"seconds": age, "what": f"{stage.name}: {stage.unit_label}"}
        return best

    def mean_fit_seconds(self) -> dict[str, dict[str, float]]:
        return {f"{m}/{f}": {"fits": n, "mean_seconds": s / n}
                for (m, f), (n, s) in sorted(self.timing.items()) if n}

    def estimate_remaining(self) -> dict[str, Any]:
        """A cautious estimate of the rolling-fit time still ahead, or a reason for none.

        Only origins still to be *estimated* count: a chain expected to be served from
        the cache costs no fitting time. A (model, frequency) pair needs at least
        MIN_TIMING_SAMPLES observed fits before its mean is trusted. Work belonging to a
        pair without that is not guessed at: it is listed as `untimed`, with its origin
        count, and the estimate states the share of the remaining fits it covers.

        Batches run one after another and the chains inside a batch run concurrently on
        `workers` processes, so each batch contributes at least
        max(longest chain, total / workers) of wall time; the figure is a scheduling lower
        bound, not a promise. It covers rolling fits only, not evaluation bootstraps or
        tables, and assumes later windows cost what earlier ones did.
        """
        means = {key: s / n for key, (n, s) in self.timing.items() if n >= MIN_TIMING_SAMPLES}
        untimed: dict[str, int] = {}
        cpu_total = wall_total = 0.0
        timed_origins = 0
        for batch, task_ids in self.batches.items():
            per_chain = []
            for task_id in task_ids:
                chain = self.chains[task_id]
                if chain.remaining == 0 or chain.plan.expect_cached:
                    continue
                key = (chain.plan.model, chain.plan.frequency)
                if key not in means:
                    label = f"{key[0]}/{key[1]}"
                    untimed[label] = untimed.get(label, 0) + chain.remaining
                    continue
                timed_origins += chain.remaining
                per_chain.append((chain.remaining * means[key], chain.plan.runs_in))
            if not per_chain:
                continue
            seconds = [s for s, _ in per_chain]
            workers = 1 if all(r == "parent" for _, r in per_chain) else max(1, self.workers)
            cpu_total += sum(seconds)
            wall_total += max(max(seconds), sum(seconds) / workers)
        provisional = any(c.plan.provisional and c.status == "queued"
                          for c in self.chains.values())
        total = timed_origins + sum(untimed.values())
        if timed_origins == 0:
            reason = ("no remaining rolling fits" if total == 0 else
                      "not enough timed fits yet for " + ", ".join(sorted(untimed)))
            return {"available": False, "reason": reason, "untimed": untimed,
                    "provisional_plan": provisional}
        return {"available": True, "fit_cpu_seconds": cpu_total,
                "fit_wall_seconds_lower_bound": wall_total,
                "timed_share": timed_origins / total if total else 1.0,
                "untimed": untimed, "provisional_plan": provisional,
                "scope": "remaining rolling-origin fits only"}

    def next_work(self) -> str:
        pending = [s for s in self.stages.values() if s.status == "pending"]
        if not pending:
            return "nothing after the current stage"
        nxt = min(pending, key=lambda s: s.number)
        return f"stage {nxt.number}/{len(self.stages)} {nxt.name}"


def fmt_duration(seconds: float | None) -> str:
    if seconds is None or not math.isfinite(seconds):
        return "n/a"
    seconds = max(0, int(round(seconds)))
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}h{minutes:02d}m{secs:02d}s"
    if minutes:
        return f"{minutes}m{secs:02d}s"
    return f"{secs}s"


__all__ = ["RunState", "StageState", "ChainState", "fmt_duration", "STAGE_BY_KEY"]
