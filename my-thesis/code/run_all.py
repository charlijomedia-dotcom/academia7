#!/usr/bin/env python3
"""Thesis pipeline entry point.

Comp §2 and §11 define the execution contract:

* the **default run** verifies the frozen hashes, loads the canonical input CSV first into
  a pandas DataFrame, derives the monthly and quarterly panels in memory, and computes
  everything downstream from those panels. It makes **no** network request.
* `--initialize-frozen` performs the one-time retrieval of the approved 2026-10-05
  historical vintage, saves the untouched official raw files and their manifest, and
  builds the canonical input from those local files.
* a store that is partial, corrupt or hash-mismatched is a **failure**, never a reason to
  re-download or overwrite.

Once the input is verified, this script runs **every stage of the approved Part 5
methodology** through `thesis.pipeline.Pipeline`: transformation and stationarity
decisions, nonlinearity diagnostics, specification selection, in-sample adequacy, the
pseudo-out-of-sample rolling forecasts, the forecast-evaluation tests, the mandatory
robustness exercises, and all required tables, figures and logs. `--data-only` stops
after the data check for a quick provenance verification.

While the analysis runs, a progress monitor reports the stage, series, model, window,
forecast origin and remaining work on the console, and keeps an execution log, a
structured event log and an atomically updated progress snapshot under
`run_logs/<namespace>/<run_id>/` (outside `output/`, so no thesis-facing artifact carries
a run-time timestamp). `--log-mirror DIR` also copies those logs to a second location,
such as a mounted Google Drive folder. `--no-monitor` turns the monitor off; the
numerical results are identical either way.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from thesis.core.config import load_config  # noqa: E402
from thesis.core.paths import (  # noqa: E402
    CONFIG_DIR,
    FROZEN_DIR,
    RUN_LOGS_DIR,
    Namespace,
    output_layout,
    run_log_dir,
)
from thesis.monitoring import Monitor  # noqa: E402
from thesis.core.provenance import RunContext  # noqa: E402
from thesis.pipeline import Pipeline  # noqa: E402
from thesis.data.canonical import StoreState, to_panels  # noqa: E402
from thesis.data.fred_client import FredClient, api_key_from_env  # noqa: E402
from thesis.data.frozen import SeriesSpec  # noqa: E402
from thesis.data.manifest import FrozenDataError  # noqa: E402
from thesis.data.store import (  # noqa: E402
    build_canonical_from_raw,
    detect_state,
    initialize_store,
    load_bundle,
)


def series_specs(config) -> list[SeriesSpec]:
    """The approved series and their official source institutions."""
    retained = [row for row in config.get("catalog") if row.get("retained")]
    return [SeriesSpec(row["series_id"], row.get("source", "")) for row in retained]


def build_client(config) -> FredClient:
    retrieval = config.get("retrieval")
    return FredClient(
        api_key=api_key_from_env(retrieval["api_key_env"]),
        base_url=retrieval["api_base"],
        timeout=int(retrieval["timeout_seconds"]),
        max_retries=int(retrieval["max_retries"]),
    )


def ensure_input(config, *, allow_network: bool, frozen_root=FROZEN_DIR):
    """Resolve the store to a verified canonical bundle, per the Comp §2 rules."""
    state = detect_state(frozen_root, config)
    print(f"data store state: {state.value}")

    if state is StoreState.COMPLETE:
        return load_bundle(frozen_root, config)

    if state is StoreState.RAW_ONLY:
        # A verified raw-only snapshot predating the amendment: build the canonical input
        # once, locally, with no network request and no change to the raw manifest.
        print("building the canonical input once from the verified raw snapshot (no network)")
        return build_canonical_from_raw(frozen_root, config)

    if state is StoreState.ABSENT:
        if not allow_network:
            raise FrozenDataError(
                "the data store is empty and this run is not permitted to retrieve data. "
                "Run with --initialize-frozen to perform the approved one-time retrieval."
            )
        print(f"empty store: retrieving the approved {config.get('run.vintage_date')} vintage")
        return initialize_store(
            build_client(config), series_specs(config), frozen_root=frozen_root, config=config
        )

    raise FrozenDataError(
        "the local data store is partial, corrupt or hash-mismatched. Comp section 2 "
        "requires the run to fail: it must not re-download, overwrite or reset."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--initialize-frozen",
        action="store_true",
        help="one-time retrieval of the approved historical vintage and canonical input",
    )
    parser.add_argument(
        "--smoke-test", action="store_true", help="fast validation run on a target subset"
    )
    parser.add_argument(
        "--data-only",
        action="store_true",
        help="verify and summarize the frozen input without running the analysis",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="ignore the fit cache and re-estimate every rolling window",
    )
    parser.add_argument(
        "--no-monitor",
        action="store_true",
        help="disable the progress monitor and its run_logs/ files (results are unchanged)",
    )
    parser.add_argument(
        "--log-mirror",
        default=os.environ.get("THESIS_LOG_MIRROR"),
        help="also copy the run logs to this directory, e.g. a mounted Google Drive "
             "folder (default: $THESIS_LOG_MIRROR)",
    )
    parser.add_argument("--heartbeat-seconds", type=float, default=60.0,
                        help="heartbeat interval for long-running computations")
    parser.add_argument("--summary-seconds", type=float, default=300.0,
                        help="interval between global progress summaries")
    args = parser.parse_args(argv)

    # Line-buffered output, so a log viewed in Colab or through a pipe is current rather
    # than hours behind in a block buffer.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(line_buffering=True)
        except (AttributeError, ValueError):
            pass
    started = time.time()

    names = ("baseline", "series_catalog", "thresholds")
    if args.smoke_test:
        names = names + ("smoke",)
    config = load_config(names=names, config_dir=CONFIG_DIR)
    if args.no_cache:
        config = config.with_overrides({"execution": {"cache": False}}, "--no-cache")

    namespace = Namespace.SMOKE if args.smoke_test else Namespace.BASELINE
    layout = output_layout(namespace)
    layout.create()

    bundle = ensure_input(config, allow_network=args.initialize_frozen)

    context = RunContext(
        namespace=namespace,
        config_hash=config.hash,
        data_snapshot_hash=bundle.data_input_identity,
        data_cutoff=config.get("samples.monthly_end"),
        vintage_date=config.get("run.vintage_date"),
        notes={"parent_source_snapshot_hash": bundle.parent_source_hash},
    )
    if not args.smoke_test:
        # The run's own output and cache directories are its result, not its inputs, so
        # they do not compromise the commit-reproducibility claim D14 protects. Anything
        # else uncommitted still stops the run.
        # run_logs/ holds this and earlier runs' operational logs: produced by runs, never
        # an input, and gitignored besides.
        context.require_clean_tree(
            produced_by_the_run=(layout.root, layout.cache, RUN_LOGS_DIR))
    # The run manifest is written by the pipeline's finalize stage, once a run has
    # actually produced results. Writing it here too meant a `--data-only` check
    # overwrote the manifest describing the run whose outputs sit beside it, leaving the
    # provenance record pointing at a verification that produced nothing.
    panels = to_panels(bundle.frame)
    print(f"canonical input: {bundle.csv_path.name}  sha256={bundle.csv_sha256[:16]}...")
    print(f"rows: {len(bundle.frame)}")
    for frequency in sorted(panels):
        panel = panels[frequency]
        print(
            f"  panel {frequency}: {panel.shape[0]} periods x {panel.shape[1]} series, "
            f"{panel.index.min():%Y-%m-%d} to {panel.index.max():%Y-%m-%d}"
        )
    print(f"run id: {context.run_id}")

    if args.data_only:
        print("--data-only: stopping after the frozen-input verification")
        print("(no run manifest written: this is a check, not a run)")
        return 0

    monitor = None
    if not args.no_monitor:
        workers = int(config.get("execution.parallel_workers", 1))
        monitor = Monitor(
            run_log_dir(namespace, context.run_id), run_id=context.run_id,
            namespace=namespace.value, workers=workers,
            heartbeat_seconds=args.heartbeat_seconds, summary_seconds=args.summary_seconds,
            mirror_dir=args.log_mirror)
        monitor.start()
        monitor.emit("frozen_input_verified", csv=bundle.csv_path.name,
                     csv_sha256=bundle.csv_sha256, rows=len(bundle.frame),
                     seconds=round(time.time() - started, 2))
        monitor.say(f"frozen input verified: {bundle.csv_path.name} "
                    f"sha256={bundle.csv_sha256[:16]}... ({len(bundle.frame)} rows) "
                    f"in {time.time() - started:.1f}s")

    pipeline = Pipeline(config, context, layout, bundle, smoke=args.smoke_test,
                        monitor=monitor)
    try:
        summary = pipeline.run()
    except KeyboardInterrupt:
        if monitor is not None:
            monitor.close("interrupted", "KeyboardInterrupt")
        raise
    except BaseException as exc:
        if monitor is not None:
            monitor.close("failed", f"{type(exc).__name__}: {exc}"[:500])
        raise
    if monitor is not None:
        monitor.close("complete")

    print("\n--- pipeline complete ---")
    print(f"stages:          {', '.join(summary['stages'])}")
    print(f"files written:   {summary['n_files']}")
    print(f"model fits:      {summary['n_fit_records']}")
    print(f"failure events:  {summary['n_failure_events']}")
    print(f"data-gap events: {summary['n_data_gap_events']}")
    print(f"test results:    {summary['n_test_results']}")
    for timing in summary["runtime"]:
        print(f"  {timing['stage']:<14} {timing['wall_seconds']:>9.2f}s  {timing['notes']}")
    print(f"output root:     {layout.root}")
    manifest = layout.manifests / "run_summary.json"
    manifest.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str),
                        encoding="utf-8")
    print(f"run summary:     {manifest}")
    if monitor is not None:
        print(f"run logs:        {monitor.log_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
