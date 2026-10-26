"""Run-time progress monitoring and operational logging.

This package observes the pipeline; it never takes part in a calculation. Nothing in it
is read by an estimator, a forecast, a test or a table, so a run produces the same
numbers with monitoring switched on or off (asserted by a test, not assumed).

* `probe`   – the tiny, always-importable hook the computational code calls. With no
              sink installed every call is a no-op.
* `plan`    – the planned workload: stages, chain batches and their exact origin counts.
* `state`   – the run's progress state, updated only by applying events. Pure: no I/O.
* `render`  – plain-text console blocks built from a state.
* `monitor` – the parent-process service: console, execution log, structured event
              log, atomic progress snapshot, heartbeat thread and the worker queue.

Operational logs are written under `run_logs/`, never under `output/`, so their
timestamps cannot reach a thesis-facing artifact or its checksum.
"""

from .monitor import Monitor, NullMonitor

__all__ = ["Monitor", "NullMonitor"]
