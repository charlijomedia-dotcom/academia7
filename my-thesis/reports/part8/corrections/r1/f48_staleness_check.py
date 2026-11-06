#!/usr/bin/env python3
"""Read-only check: is each F4.8 figure consistent with its window-length table?

F4.8_<series> plots `oos_r2_vs_benchmark` (and the `N=` labels from `n_valid`) for h=1 of
robustness/window_length_comparison.csv. The pinned R1 workflow regenerates that table but
does not re-render F4.8. In a corrected release, a figure is therefore STALE when a plotted
input of its series changed while the figure bytes did not.

For every release commit given, the script compares the release's table and figures with the
published tree `output/` at the same commit (git objects only; nothing is checked out or
written except --out).

usage: f48_staleness_check.py --repo DIR --release COMMIT:PATH [--release ...] --out CSV
       (PATH is the release folder inside the commit, e.g. my-thesis/output_corrected)
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import subprocess

PLOTTED = ("model", "window_length", "oos_r2_vs_benchmark", "n_valid")
TABLE = "robustness/window_length_comparison.csv"


def git_bytes(repo: str, commit: str, path: str) -> bytes | None:
    result = subprocess.run(["git", "-C", repo, "show", f"{commit}:{path}"],
                            capture_output=True)
    return result.stdout if result.returncode == 0 else None


def plotted_rows(data: bytes) -> dict[str, list[tuple]]:
    rows: dict[str, list[tuple]] = {}
    for row in csv.DictReader(io.StringIO(data.decode())):
        if row["horizon"] == "1":
            rows.setdefault(row["series"], []).append(tuple(row[c] for c in PLOTTED))
    return {series: sorted(values) for series, values in rows.items()}


def main(argv=None) -> list[dict]:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--release", action="append", required=True)
    ap.add_argument("--published-path", default="my-thesis/output")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    results = []
    for spec in args.release:
        commit, folder = spec.split(":", 1)
        published = plotted_rows(git_bytes(args.repo, commit, f"{args.published_path}/{TABLE}"))
        release = plotted_rows(git_bytes(args.repo, commit, f"{folder}/{TABLE}"))
        for series in sorted(published):
            inputs_changed = published[series] != release.get(series)
            for ext in ("png", "pdf"):
                name = f"figures/F4.8_{series}.{ext}"
                a = git_bytes(args.repo, commit, f"{args.published_path}/{name}")
                b = git_bytes(args.repo, commit, f"{folder}/{name}")
                figure_changed = (a is None or b is None
                                  or hashlib.sha256(a).digest() != hashlib.sha256(b).digest())
                results.append({"release_commit": commit, "series": series, "figure": name,
                                "plotted_inputs_changed": inputs_changed,
                                "figure_bytes_changed": figure_changed,
                                "stale": inputs_changed and not figure_changed})
    with open(args.out, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    return results


if __name__ == "__main__":
    rows = main()
    print(f"{sum(r['stale'] for r in rows)} stale of {len(rows)} figure files")
    for r in rows:
        if r["stale"]:
            print(r["release_commit"], r["figure"])
