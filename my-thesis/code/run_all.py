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
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from thesis.core.config import load_config  # noqa: E402
from thesis.core.paths import (  # noqa: E402
    CONFIG_DIR,
    FROZEN_VINTAGE_DIR,
    Namespace,
    output_layout,
)
from thesis.core.provenance import RunContext  # noqa: E402
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


def ensure_input(config, *, allow_network: bool, directory=FROZEN_VINTAGE_DIR):
    """Resolve the store to a verified canonical bundle, per the Comp §2 rules."""
    state = detect_state(directory, config)
    print(f"data store state: {state.value}")

    if state is StoreState.COMPLETE:
        return load_bundle(directory, config)

    if state is StoreState.RAW_ONLY:
        # A verified raw-only snapshot predating the amendment: build the canonical input
        # once, locally, with no network request and no change to the raw manifest.
        print("building the canonical input once from the verified raw snapshot (no network)")
        return build_canonical_from_raw(directory, config)

    if state is StoreState.ABSENT:
        if not allow_network:
            raise FrozenDataError(
                "the data store is empty and this run is not permitted to retrieve data. "
                "Run with --initialize-frozen to perform the approved one-time retrieval."
            )
        print(f"empty store: retrieving the approved {config.get('run.vintage_date')} vintage")
        return initialize_store(
            build_client(config), series_specs(config), directory=directory, config=config
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
    args = parser.parse_args(argv)

    names = ("baseline", "series_catalog", "thresholds")
    if args.smoke_test:
        names = names + ("smoke",)
    config = load_config(names=names, config_dir=CONFIG_DIR)

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
        context.require_clean_tree()
    context.write_run_manifest(layout)

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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
