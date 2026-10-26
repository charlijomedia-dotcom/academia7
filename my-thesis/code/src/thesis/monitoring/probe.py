"""The hook computational code calls to report progress.

A *sink* is any callable taking one event dictionary. In the parent process it is the
monitor itself; inside a worker process it puts the event on a multiprocessing queue the
parent drains, so only the parent ever writes to the console or a log file and messages
from several workers can never interleave.

With no sink installed, `emit` returns immediately: the probe calls left in the
estimators cost one global lookup each, and they never read from or write to any value a
calculation uses.
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from typing import Any, Callable, Iterator

Sink = Callable[[dict[str, Any]], None]

_sink: Sink | None = None
_task: str | None = None


def install(sink: Sink | None) -> None:
    global _sink
    _sink = sink


def uninstall() -> None:
    global _sink, _task
    _sink = None
    _task = None


def active() -> bool:
    return _sink is not None


def set_task(task_id: str | None) -> None:
    """The task subsequent substep and operation events belong to."""
    global _task
    _task = task_id


def emit(kind: str, **fields: Any) -> None:
    sink = _sink
    if sink is None:
        return
    event = {"kind": kind, "t": time.time(), "pid": os.getpid()}
    if _task is not None and "task_id" not in fields:
        event["task_id"] = _task
    event.update(fields)
    try:
        sink(event)
    except Exception:                                   # monitoring must never fail a run
        pass


def substep(label: str, **info: Any) -> None:
    """Which part of a long computation is now active (a start, a Hessian, ...)."""
    emit("substep", label=label, **info)


@contextmanager
def operation(category: str, label: str = "", **info: Any) -> Iterator[None]:
    """Time one expensive operation (a bootstrap, a full-sample fit, ...).

    The exception, if any, propagates unchanged; the operation is recorded as failed.
    """
    if _sink is None:
        yield
        return
    started = time.time()
    emit("op_start", category=category, label=label, **info)
    status = "ok"
    try:
        yield
    except BaseException:
        status = "error"
        raise
    finally:
        emit("op_end", category=category, label=label, status=status,
             seconds=time.time() - started, **info)


def timed(category: str, label_from: Callable[..., str] | None = None):
    """Decorator form of `operation` for functions called from many places."""
    def wrap(function):
        def wrapper(*args, **kwargs):
            if _sink is None:
                return function(*args, **kwargs)
            label = ""
            if label_from is not None:
                try:
                    label = label_from(*args, **kwargs)
                except Exception:
                    label = ""
            with operation(category, label):
                return function(*args, **kwargs)
        wrapper.__wrapped__ = function
        wrapper.__name__ = getattr(function, "__name__", "wrapped")
        wrapper.__doc__ = getattr(function, "__doc__", None)
        return wrapper
    return wrap


class ChainReporter:
    """Origin-level progress of one rolling chain.

    Used by the rolling engine and by the serial VAR and GARCH loops, so every chain
    reports through one vocabulary. Every method returns at once when no sink is
    installed. It only reads values the calculation has already produced.
    """

    def __init__(self, task_id: str, n_origins: int, **identity: Any) -> None:
        self.task_id = task_id
        self.n_origins = int(n_origins)
        self.identity = identity
        self._origin_t0: float | None = None
        self._chain_t0: float | None = None

    def start(self) -> None:
        if _sink is None:
            return
        set_task(self.task_id)
        self._chain_t0 = time.perf_counter()
        emit("chain_start", task_id=self.task_id, n_origins=self.n_origins,
             plan=self.identity.get("plan"),
             **{k: v for k, v in self.identity.items() if k != "plan"})

    def origin_start(self, index: int, origin_date: Any, window_start: Any,
                     window_end: Any) -> None:
        if _sink is None:
            return
        self._origin_t0 = time.perf_counter()
        emit("origin_start", task_id=self.task_id, index=int(index),
             origin_date=_date(origin_date), window_start=_date(window_start),
             window_end=_date(window_end))

    def origin_end(self, status: str, *, from_cache: bool = False, n_records: int = 0) -> None:
        if _sink is None:
            return
        seconds = (time.perf_counter() - self._origin_t0) if self._origin_t0 else 0.0
        self._origin_t0 = None
        emit("origin_end", task_id=self.task_id, status=status,
             from_cache=bool(from_cache), n_records=int(n_records), seconds=seconds)

    def end(self, **counts: Any) -> None:
        if _sink is None:
            return
        seconds = (time.perf_counter() - self._chain_t0) if self._chain_t0 else 0.0
        emit("chain_end", task_id=self.task_id, seconds=seconds, **counts)
        set_task(None)


def _date(value: Any) -> str:
    if value is None:
        return ""
    strftime = getattr(value, "strftime", None)
    return strftime("%Y-%m-%d") if strftime is not None else str(value)


# -- worker-process side ------------------------------------------------------------

def queue_sink(queue) -> Sink:
    """A sink that forwards events to the parent. Never blocks a computation."""
    def put(event: dict[str, Any]) -> None:
        try:
            queue.put_nowait(event)
        except Exception:
            pass
    return put


def start_worker_heartbeat(interval: float = 30.0) -> None:
    """Report this worker's liveness while it computes.

    A daemon thread wakes every `interval` seconds and sends the process's CPU time and
    resident memory. A worker inside a twenty-minute optimization therefore still shows
    up as alive, with its CPU time advancing, which is what distinguishes a slow fit from
    a dead process. The thread reads nothing a calculation uses.
    """
    import threading

    try:
        import psutil
        process = psutil.Process(os.getpid())
    except Exception:                                   # pragma: no cover
        process = None

    def beat() -> None:
        while True:
            rss = None
            if process is not None:
                try:
                    rss = process.memory_info().rss / 1e6
                except Exception:
                    rss = None
            emit("worker_heartbeat", cpu_seconds=time.process_time(), rss_mb=rss,
                 task_id=_task)
            time.sleep(interval)

    threading.Thread(target=beat, name="worker-heartbeat", daemon=True).start()
