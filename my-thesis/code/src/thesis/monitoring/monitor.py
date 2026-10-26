"""The parent-process monitoring service.

One `Monitor` per run. It is the only writer of the console, the execution log, the
structured event log and the progress snapshot, so concurrent workers can never
interleave or corrupt a message: workers send events on a queue, and a listener thread
in the parent applies them one at a time under a lock.

Files, all under `run_logs/<namespace>/<run_id>/` (never under `output/`):

* `execution.log`   – the human-readable log: everything printed to the console.
* `events.jsonl`    – append-only structured events, one JSON object per line.
* `progress.json`   – the current state, replaced atomically (write, then rename), so a
                      reader never sees a half-written file. After an unexpected
                      termination it names the last active calculation.

A background thread prints a heartbeat for computations that have been running a while
and a global summary every few minutes, even while every worker is deep inside an
optimizer and nothing else is happening.
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, Iterator, TextIO

from . import probe, render
from .plan import STAGE_BY_KEY, ChainPlan
from .state import RunState, fmt_duration

try:
    import psutil
except ImportError:                                     # pragma: no cover
    psutil = None


class NullMonitor:
    """The do-nothing monitor: the pipeline's default, and the 'monitoring off' arm."""

    enabled = False
    log_dir = None

    @contextmanager
    def stage(self, key: str, **_: Any) -> Iterator[None]:
        yield

    @contextmanager
    def batch(self, batch: str, task_ids: Iterable[str]) -> Iterator[None]:
        yield

    def worker_channel(self):
        return None

    def __getattr__(self, name: str):
        def nothing(*args: Any, **kwargs: Any) -> None:
            return None
        return nothing


class Monitor:
    enabled = True

    def __init__(
        self,
        log_dir: str | Path,
        *,
        run_id: str,
        namespace: str,
        workers: int = 1,
        stream: TextIO | None = None,
        heartbeat_seconds: float = 60.0,
        summary_seconds: float = 300.0,
        snapshot_seconds: float = 10.0,
        tick_seconds: float = 1.0,
        mirror_dir: str | Path | None = None,
        mirror_seconds: float = 120.0,
        milestones: int = 10,
    ) -> None:
        self.log_dir = Path(log_dir)
        self.stream = stream if stream is not None else sys.stdout
        self.heartbeat_seconds = heartbeat_seconds
        self.summary_seconds = summary_seconds
        self.snapshot_seconds = snapshot_seconds
        self.tick_seconds = tick_seconds
        self.mirror_dir = Path(mirror_dir) if mirror_dir else None
        self.mirror_seconds = mirror_seconds
        self.milestones = max(1, int(milestones))
        self.state = RunState()
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._listeners: list[threading.Thread] = []
        self._dirty = True
        self._last_heartbeat = self._last_summary = self._last_snapshot = time.time()
        self._last_mirror = 0.0
        self._last_fsync = time.time()
        self._mirror_offsets: dict[str, int] = {}
        self._milestone: dict[str, int] = {}
        self._stage_detail: dict[str, dict[str, Any]] = {}
        self._run = {"run_id": run_id, "namespace": namespace, "workers": int(workers)}
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.paths = {"execution_log": self.log_dir / "execution.log",
                      "events": self.log_dir / "events.jsonl",
                      "snapshot": self.log_dir / "progress.json"}
        self._log = open(self.paths["execution_log"], "a", encoding="utf-8")
        self._events = open(self.paths["events"], "a", encoding="utf-8")

    # -- lifecycle ---------------------------------------------------------

    def start(self) -> "Monitor":
        probe.install(self.handle)
        self.handle({"kind": "run_start", "t": time.time(), "pid": os.getpid(), **self._run})
        self.say(f"[{render.clock()}] monitoring run {self._run['run_id']} "
                 f"({self._run['namespace']}, {self._run['workers']} workers); "
                 f"logs in {self.log_dir}")
        self._thread = threading.Thread(target=self._loop, name="monitor-heartbeat",
                                        daemon=True)
        self._thread.start()
        with self._lock:
            self._snapshot(force=True)
        self._write_pointer()
        return self

    def close(self, status: str = "complete", error: str | None = None) -> None:
        if self._stop.is_set():
            return
        now = time.time()
        with self._lock:
            self.handle({"kind": "run_end", "t": now, "pid": os.getpid(), "status": status,
                         **({"error": error} if error else {})})
            self.say(render.summary(self.state, now, self.resources()))
            self.say(f"[{render.clock(now)}] run {status}"
                     + (f": {error}" if error else "")
                     + f"; elapsed {fmt_duration(now - (self.state.started or now))}")
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
        probe.uninstall()
        with self._lock:
            self._snapshot(force=True)
            self._mirror(force=True)
            for handle in (self._log, self._events):
                try:
                    handle.flush()
                    os.fsync(handle.fileno())
                    handle.close()
                except (OSError, ValueError):
                    pass

    def _write_pointer(self) -> None:
        """`run_logs/<namespace>/LATEST` names the most recent run's directory."""
        try:
            pointer = self.log_dir.parent / "LATEST"
            temporary = pointer.with_suffix(".tmp")
            temporary.write_text(self.log_dir.name + "\n", encoding="utf-8")
            os.replace(temporary, pointer)
        except OSError:
            pass

    # -- output ------------------------------------------------------------

    def say(self, text: str) -> None:
        """One message to the console and the execution log, flushed at once."""
        with self._lock:
            for target in (self.stream, self._log):
                try:
                    target.write(text + "\n")
                    target.flush()
                except (OSError, ValueError):
                    pass

    def handle(self, event: dict[str, Any]) -> None:
        """Apply one event: record it, update the state, print what it warrants."""
        event.setdefault("t", time.time())
        with self._lock:
            try:
                self._events.write(json.dumps(event, default=str, sort_keys=True) + "\n")
                self._events.flush()
            except (OSError, ValueError):
                pass
            self.state.apply(event)
            self._dirty = True
            self._react(event)

    def _react(self, event: dict[str, Any]) -> None:
        kind = event.get("kind")
        chain = self.state.chains.get(event.get("task_id", ""))
        if kind == "chain_start" and chain is not None:
            self._milestone[chain.plan.task_id] = 0
            self.say(render.chain_start(self.state, chain))
        elif kind == "origin_end" and chain is not None:
            step = int(self.milestones * chain.completed / max(1, chain.plan.n_origins))
            if chain.completed == 1 or step > self._milestone.get(chain.plan.task_id, 0):
                self._milestone[chain.plan.task_id] = step
                if chain.completed < chain.plan.n_origins:
                    self.say(render.chain_milestone(chain, event["t"]))
        elif kind in ("chain_end", "chain_error") and chain is not None:
            self.say(render.chain_end(chain))
        elif kind == "warning":
            self.say(f"[{render.clock(event['t'])}] WARNING {event.get('message', '')}")
        elif kind == "op_end" and float(event.get("seconds") or 0) >= self.heartbeat_seconds:
            self.say(f"[{render.clock(event['t'])}] {event.get('category')} "
                     f"{event.get('label', '')} finished in "
                     f"{fmt_duration(event.get('seconds'))} ({event.get('status')})")
        if kind in ("stage_start", "stage_end", "chain_start", "chain_end", "chain_error",
                    "batch_start", "batch_end", "checkpoint", "plan"):
            self._snapshot(force=True)

    # -- pipeline API --------------------------------------------------------

    def emit(self, kind: str, **fields: Any) -> None:
        self.handle({"kind": kind, "t": time.time(), "pid": os.getpid(), **fields})

    @contextmanager
    def stage(self, key: str, *, planned_units: int | None = None,
              detail: dict[str, Any] | None = None) -> Iterator[None]:
        detail = detail or {}
        self._stage_detail[key] = detail
        self.emit("stage_start", stage=key, planned_units=planned_units,
                  **{k: v for k, v in detail.items() if k in ("series", "models", "unit")})
        stage = self.state.stages[key]
        chains = [c for c in self.state.chains.values() if c.plan.stage == key]
        if chains:
            detail = {**detail, "chains": len(chains),
                      "origins": sum(c.plan.n_origins for c in chains),
                      "provisional": any(c.plan.provisional for c in chains)}
        self.say(render.stage_start(self.state, stage, detail))
        try:
            yield
        except BaseException as exc:
            message = f"{type(exc).__name__}: {exc}"[:500]
            self.emit("stage_end", stage=key, status="failed", error=message)
            self.say(render.stage_end(self.state, stage, time.time()))
            raise
        self.emit("stage_end", stage=key, status="done")
        self.say(render.stage_end(self.state, stage, time.time()))

    def set_units(self, key: str, planned_units: int) -> None:
        self.emit("stage_units", stage=key, planned_units=int(planned_units))

    def task(self, key: str, label: str, **info: Any) -> None:
        """A new unit of serial work in stage `key`; the previous one is complete."""
        self.emit("task", stage=key, label=label, **info)

    def plan(self, chains: Iterable[ChainPlan]) -> None:
        self.emit("plan", chains=[c.to_dict() for c in chains])

    def skip_chain(self, task_id: str, reason: str) -> None:
        self.emit("chain_skipped", task_id=task_id, reason=reason)

    def checkpoint(self, name: str) -> None:
        self.emit("checkpoint", name=name)

    def warn(self, message: str, **extra: Any) -> None:
        self.emit("warning", message=message, **extra)

    def chain_result(self, task_id: str, result) -> None:
        self.emit("chain_result", task_id=task_id, attempted=result.attempted,
                  valid=result.valid, failed=result.failed, from_cache=result.from_cache,
                  n_records=int(len(result.forecasts)), gaps=len(result.data_gaps))

    def chain_error(self, task_id: str, error: str) -> None:
        self.emit("chain_error", task_id=task_id, error=error[:500])

    @contextmanager
    def batch(self, batch: str, task_ids: Iterable[str]) -> Iterator[None]:
        ids = list(task_ids)
        self.emit("batch_start", batch=batch, task_ids=ids)
        try:
            yield
        finally:
            self.emit("batch_end", batch=batch)

    # -- worker channel ------------------------------------------------------

    def worker_channel(self):
        """A queue workers send events on, drained into `handle` by a listener thread."""
        import multiprocessing

        queue = multiprocessing.get_context().Queue()

        def listen() -> None:
            while True:
                try:
                    event = queue.get()
                except (EOFError, OSError):
                    return
                if event is None:
                    return
                self.handle(event)

        thread = threading.Thread(target=listen, name="monitor-listener", daemon=True)
        thread.start()
        self._listeners.append(thread)
        queue._monitor_listener = thread                 # type: ignore[attr-defined]
        return queue

    def close_channel(self, queue) -> None:
        """Drain everything the (now finished) workers sent, then stop listening.

        Called after the worker pool has shut down, so each worker's queue feeder has
        flushed; the sentinel is written after their events and is read after them.
        """
        if queue is None:
            return
        queue.put(None)
        thread = getattr(queue, "_monitor_listener", None)
        if thread is not None:
            thread.join(timeout=60)
        try:
            queue.close()
            queue.join_thread()
        except Exception:
            pass

    # -- background thread ---------------------------------------------------

    def _loop(self) -> None:
        while not self._stop.wait(self.tick_seconds):
            try:
                self._tick(time.time())
            except Exception as exc:                     # never let monitoring kill a run
                try:
                    self.say(f"[monitor] internal error: {exc!r}")
                except Exception:
                    pass

    def _long_running(self, now: float) -> bool:
        threshold = self.heartbeat_seconds
        for chain in self.state.active_chains():
            if chain.origin_started is not None and now - chain.origin_started >= threshold:
                return True
        if any(now - op.started >= threshold for op in self.state.active_ops.values()):
            return True
        stage = self.state.stages.get(self.state.current_stage or "")
        return bool(stage is not None and stage.status == "active" and stage.unit_started
                    and now - stage.unit_started >= threshold)

    def _tick(self, now: float) -> None:
        with self._lock:
            if now - self._last_summary >= self.summary_seconds:
                self._last_summary = self._last_heartbeat = now
                self.say(render.workers(self.state, now))
                self.say(render.summary(self.state, now, self.resources()))
            elif now - self._last_heartbeat >= self.heartbeat_seconds:
                self._last_heartbeat = now
                if self._long_running(now):
                    text = render.workers(self.state, now)
                    quiet = now - (self.state.last_progress or now)
                    if quiet >= 10 * 60:
                        text += (f"\n  NOTE: no computation has completed for "
                                 f"{fmt_duration(quiet)}; the fits above are still running. "
                                 f"A slow optimization is not treated as a failure.")
                    self.say(text)
            self._snapshot()
            if now - self._last_fsync >= 30:
                self._last_fsync = now
                for handle in (self._log, self._events):
                    try:
                        os.fsync(handle.fileno())
                    except (OSError, ValueError):
                        pass
            self._mirror()

    def resources(self) -> dict[str, str]:
        if psutil is None:
            return {}
        out: dict[str, str] = {}
        try:
            out["cpu"] = f"{psutil.cpu_percent(interval=None):.0f}%"
            me = psutil.Process(os.getpid())
            rss = me.memory_info().rss
            for child in me.children(recursive=True):
                try:
                    rss += child.memory_info().rss
                except Exception:
                    pass
            out["run rss"] = f"{rss / 1e9:.2f} GB"
            memory = psutil.virtual_memory()
            out["system memory"] = (f"{memory.used / 1e9:.1f}/{memory.total / 1e9:.1f} GB "
                                    f"({memory.percent:.0f}%)")
        except Exception:
            pass
        return out

    # -- snapshot -------------------------------------------------------------

    def snapshot(self) -> dict[str, Any]:
        now = time.time()
        state = self.state
        stage = state.stages.get(state.current_stage or "")

        def chain_view(chain) -> dict[str, Any]:
            p = chain.plan
            return {
                "task_id": p.task_id, "worker": state.slot_of(chain), "pid": chain.pid,
                "series": p.series, "model": p.model, "spec_label": p.spec_label,
                "k_regimes": p.k_regimes, "exercise": p.exercise, "role": p.role,
                "window_length": p.window_length, "horizons": list(p.horizons),
                "current_origin": chain.current_origin,
                "window_start": chain.window_start, "window_end": chain.window_end,
                "completed_origins": chain.completed, "planned_origins": p.n_origins,
                "remaining_origins": chain.remaining, "valid": chain.valid,
                "failed": chain.failed, "data_gaps": chain.gaps,
                "from_cache": chain.from_cache, "forecast_records": chain.n_records,
                "current_fit_seconds": (round(now - chain.origin_started, 1)
                                        if chain.origin_started else None),
                "active_substep": chain.substep,
                "mean_fit_seconds": chain.mean_fit_seconds(),
                "chain_seconds": round(now - chain.started, 1) if chain.started else None,
                "last_event_seconds_ago": (round(now - chain.last_event, 1)
                                           if chain.last_event else None),
            }

        outstanding: dict[str, int] = {}
        for chain in state.chains.values():
            if chain.status == "queued":
                outstanding[chain.plan.stage] = outstanding.get(chain.plan.stage, 0) + 1
        return {
            "run_id": state.run_id, "namespace": state.namespace, "status": state.status,
            "pid": os.getpid(), "workers": state.workers,
            "updated_utc": render.utc(now), "started_utc": render.utc(state.started),
            "elapsed_seconds": round(now - (state.started or now), 1),
            "last_heartbeat_utc": render.utc(now),
            "current_stage": None if stage is None else {
                "number": stage.number, "key": stage.key, "name": stage.name,
                "checkpoint": stage.checkpoint, "methodology": stage.methodology,
                "status": stage.status, "elapsed_seconds": round(stage.elapsed(now), 1),
                "completed_tasks": stage.completed_units, "planned_tasks": stage.planned_units,
                "current_task": stage.unit_label, "current_task_substep": stage.unit_substep,
                "current_task_seconds": (round(now - stage.unit_started, 1)
                                         if stage.unit_started else None)},
            "stages": [{"number": s.number, "key": s.key, "name": s.name,
                        "status": s.status, "elapsed_seconds": round(s.elapsed(now), 1),
                        "completed_tasks": s.completed_units, "planned_tasks": s.planned_units,
                        "errors": s.errors} for s in state.stages.values()],
            "completed_stages": [s.key for s in state.stages.values() if s.status == "done"],
            "outstanding_stages": [s.key for s in state.stages.values()
                                   if s.status in ("pending", "active")],
            "active_tasks": [chain_view(c) for c in state.active_chains()],
            "active_operations": [{"category": o.category, "label": o.label, "pid": o.pid,
                                   "seconds": round(now - o.started, 1)}
                                  for o in state.active_ops.values()],
            "chains": state.chain_counts(),
            "robustness_chains": state.chain_counts("robustness"),
            "origins": {"all": state.origin_counts(), "baseline": state.origin_counts("baseline"),
                        "robustness": state.origin_counts("robustness")},
            "outstanding_chains_by_stage": outstanding,
            "longest_running": state.longest_running(now),
            "last_progress_utc": render.utc(state.last_progress),
            "last_progress": state.last_progress_what,
            "last_checkpoint": state.last_checkpoint,
            "mean_fit_seconds": state.mean_fit_seconds(),
            "slowest_fits": sorted(state.slowest, key=lambda r: -r["seconds"])[:10],
            "operations": {k: {"count": v.count, "seconds": round(v.seconds, 2),
                               "max_seconds": round(v.max_seconds, 2), "errors": v.errors}
                           for k, v in state.operations.items()},
            "estimate": state.estimate_remaining(),
            "next_work": state.next_work(),
            "warnings": state.warnings[-20:], "n_warnings": len(state.warnings),
            "failures": state.failures[-20:], "n_failures": len(state.failures),
            "resources": self.resources(),
            "files": {k: str(v) for k, v in self.paths.items()},
        }

    def _snapshot(self, force: bool = False) -> None:
        now = time.time()
        # Rewritten on every tick interval even when nothing changed: its timestamp is
        # the liveness signal a reader checks after an unexpected termination.
        if not force and now - self._last_snapshot < self.snapshot_seconds:
            return
        self._last_snapshot = now
        self._dirty = False
        target = self.paths["snapshot"]
        temporary = target.with_suffix(".json.tmp")
        try:
            temporary.write_text(json.dumps(self.snapshot(), indent=2, default=str),
                                 encoding="utf-8")
            os.replace(temporary, target)
        except OSError:
            pass

    # -- mirror (e.g. Google Drive) ---------------------------------------------

    def _mirror(self, force: bool = False) -> None:
        """Copy the logs to a second location, incrementally.

        The snapshot is copied whole; the two logs are append-only, so only their new
        bytes are appended. A slow or unavailable mirror never stops the run.
        """
        if self.mirror_dir is None:
            return
        now = time.time()
        if not force and now - self._last_mirror < self.mirror_seconds:
            return
        self._last_mirror = now
        try:
            target_dir = self.mirror_dir / self.log_dir.parent.name / self.log_dir.name
            target_dir.mkdir(parents=True, exist_ok=True)
            for key in ("execution_log", "events"):
                source = self.paths[key]
                offset = self._mirror_offsets.get(key, 0)
                size = source.stat().st_size
                if size > offset:
                    with open(source, "rb") as reader, \
                            open(target_dir / source.name, "ab") as writer:
                        reader.seek(offset)
                        writer.write(reader.read(size - offset))
                    self._mirror_offsets[key] = size
            snapshot = self.paths["snapshot"]
            if snapshot.exists():
                temporary = target_dir / "progress.json.tmp"
                temporary.write_bytes(snapshot.read_bytes())
                os.replace(temporary, target_dir / "progress.json")
        except OSError as exc:
            try:
                self._log.write(f"[monitor] log mirror unavailable: {exc!r}\n")
            except (OSError, ValueError):
                pass
