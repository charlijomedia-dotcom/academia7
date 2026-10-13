"""Point-forecast accuracy measures (Part 5 §10.1).

RMSE, MAE and out-of-sample R² relative to the AR benchmark:

    R2_OOS = 1 - sum(e_model^2) / sum(e_AR^2)

MAPE is deliberately absent: growth and inflation targets cross zero, which makes
percentage errors unstable (Part 5 §7.1, Hyndman and Koehler 2006).
"""

from __future__ import annotations

from typing import Mapping

import numpy as np
import pandas as pd

from . import alignment


def rmse(errors: np.ndarray) -> float:
    errors = np.asarray(errors, dtype=float)
    errors = errors[np.isfinite(errors)]
    return float(np.sqrt(np.mean(errors**2))) if errors.size else float("nan")


def mae(errors: np.ndarray) -> float:
    errors = np.asarray(errors, dtype=float)
    errors = errors[np.isfinite(errors)]
    return float(np.mean(np.abs(errors))) if errors.size else float("nan")


def oos_r2(model_errors: np.ndarray, benchmark_errors: np.ndarray) -> float:
    """Out-of-sample R² against the benchmark, on already-aligned errors."""
    model_errors = np.asarray(model_errors, dtype=float)
    benchmark_errors = np.asarray(benchmark_errors, dtype=float)
    denominator = float(np.sum(benchmark_errors**2))
    if denominator <= 0 or not np.isfinite(denominator):
        return float("nan")
    return float(1.0 - np.sum(model_errors**2) / denominator)


def accuracy_table(
    frames: Mapping[str, pd.DataFrame],
    benchmark: str,
    *,
    series: str = "",
    horizon: int = 1,
    window_length: int | None = None,
) -> pd.DataFrame:
    """Descriptive accuracy per model, plus benchmark-relative measures on common dates.

    Descriptive RMSE and MAE use each model's own valid observations with N shown;
    OOS R² and the mean loss differential use the pairwise intersection with the
    benchmark, and both N values are reported (decision M7).
    """
    rows = []
    for name, frame in frames.items():
        own = frame[np.isfinite(frame["error"])]
        row = {
            "series": series,
            "model": name,
            "horizon": horizon,
            "window_length": window_length,
            "n_attempted": int(len(frame)),
            "n_valid": int(len(own)),
            "n_failed": int(len(frame) - len(own)),
            "rmse": rmse(own["error"].to_numpy()),
            "mae": mae(own["error"].to_numpy()),
        }
        if name != benchmark and benchmark in frames:
            pair = alignment.pairwise(frame, frames[benchmark])
            row["n_common_with_benchmark"] = pair.n_common
            row["n_removed_by_alignment"] = pair.removed.get("left", 0)
            if pair.available:
                errors = alignment.aligned_errors({name: frame, benchmark: frames[benchmark]},
                                                  pair.dates)
                row["oos_r2_vs_benchmark"] = oos_r2(errors[name], errors[benchmark])
                row["rmse_common"] = rmse(errors[name])
                row["mae_common"] = mae(errors[name])
                row["mean_loss_diff_squared"] = float(
                    np.mean(errors[name] ** 2 - errors[benchmark] ** 2)
                )
                row["mean_loss_diff_absolute"] = float(
                    np.mean(np.abs(errors[name]) - np.abs(errors[benchmark]))
                )
            else:
                row["oos_r2_vs_benchmark"] = float("nan")
        elif name == benchmark:
            row["n_common_with_benchmark"] = int(len(own))
            row["oos_r2_vs_benchmark"] = 0.0
        rows.append(row)
    table = pd.DataFrame(rows)
    if not table.empty and "rmse" in table:
        table["rank_rmse"] = table["rmse"].rank(method="min")
        table["rank_mae"] = table["mae"].rank(method="min")
    return table
