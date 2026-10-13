"""Thesis figures (Part 5 §13.1, Outputs §5-§8).

The figure rules are methodological, not cosmetic, so they are enforced here rather than
left to each call site:

* readable axis units, sample dates and model labels on every figure;
* NBER recession shading wherever a time axis is shown;
* **no silent axis clipping ever**, and a failed or extreme model is moved to its own
  diagnostic panel rather than being allowed to destroy the scale of the readable one
  (jury R1-06, the figure that reported an unemployment axis of +/- 20,000);
* 95% confidence bands on ACF displays.

Colour follows a fixed categorical order that is never cycled: a model keeps its colour
whatever else is on the chart. The palette is the validated reference instance (all six
checks pass; the sub-3:1 contrast warning is relieved by the always-present legend and by
the machine-readable CSV that carries every plotted number). Line style and marker vary
with the colour as a secondary encoding, so the figures survive greyscale printing and
colour-vision deficiency.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#: Fixed categorical assignment. Never cycled, never reassigned by rank.
MODEL_COLOURS = {
    "AR": "#2a78d6",        # slot 1, blue
    "ARMA": "#eb6834",      # slot 2, orange
    "MSAR": "#1baf7a",      # slot 3, aqua
    "STAR": "#eda100",      # slot 4, yellow
    "MSAR3": "#e87ba4",     # slot 5, magenta
    "VAR": "#6250d6",       # slot 7, violet
    "ARMA-GARCH": "#008300",
}
MODEL_STYLES = {
    "AR": ("-", "o"), "ARMA": ("--", "s"), "MSAR": ("-.", "^"),
    "STAR": (":", "D"), "MSAR3": ("--", "v"), "VAR": ("-.", "P"),
    "ARMA-GARCH": (":", "X"),
}
ACTUAL_COLOUR = "#0b0b0b"
GRID_COLOUR = "#d8d7d2"
SHADE_COLOUR = "#c3c2b7"

DEFAULT_FORMATS = ("png", "pdf")


def style_axes(ax, *, title: str, xlabel: str, ylabel: str) -> None:
    ax.set_title(title, fontsize=11)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.grid(True, color=GRID_COLOUR, linewidth=0.6, alpha=0.8)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(labelsize=8)


def shade_recessions(ax, usrec: pd.Series) -> None:
    """Shade NBER recession periods behind the data."""
    if usrec is None or usrec.empty:
        return
    values = usrec.to_numpy(dtype=float)
    index = pd.DatetimeIndex(usrec.index)
    start = None
    for position, value in enumerate(values):
        if value == 1 and start is None:
            start = index[position]
        elif value == 0 and start is not None:
            ax.axvspan(start, index[position], color=SHADE_COLOUR, alpha=0.35, linewidth=0)
            start = None
    if start is not None:
        ax.axvspan(start, index[-1], color=SHADE_COLOUR, alpha=0.35, linewidth=0)


def save(fig, path: Path, context=None, extra: dict[str, Any] | None = None,
         formats: Sequence[str] = DEFAULT_FORMATS) -> list[Path]:
    """Write a figure in every required format and attach its provenance sidecar.

    The format is appended to the whole stem rather than substituted with
    `Path.with_suffix`, because the required figure identifiers themselves contain dots
    (`F2.0`, `F3.1`, `F4.8`): `with_suffix` would read `.0_sample_timeline` as the
    extension and collapse every F2.x figure onto one file name.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    written = []
    for suffix in formats:
        target = path.parent / f"{path.name}.{suffix}"
        fig.savefig(target, dpi=300, bbox_inches="tight")
        written.append(target)
        if context is not None:
            context.write_sidecar(target, extra)
    plt.close(fig)
    return written


# ---------------------------------------------------------------------------
# F2.0 / F2.1 - data coverage and series overview
# ---------------------------------------------------------------------------


def sample_coverage_timeline(spans: Mapping[str, tuple[pd.Timestamp, pd.Timestamp]],
                             monthly_end: pd.Timestamp, var_start: pd.Timestamp,
                             title: str = "F2.0 Sample coverage") -> plt.Figure:
    """One horizontal bar per series, with the common endpoint and VAR sample marked."""
    fig, ax = plt.subplots(figsize=(9, 0.5 * len(spans) + 2))
    names = list(spans)
    for position, name in enumerate(names):
        first, last = spans[name]
        ax.barh(position, (last - first).days, left=first, height=0.5,
                color="#2a78d6", alpha=0.85)
        ax.text(last, position, f"  {first:%Y-%m} to {last:%Y-%m}", va="center", fontsize=7)
    ax.axvline(monthly_end, color="#eb6834", linestyle="--", linewidth=1.5,
               label=f"common monthly endpoint {monthly_end:%Y-%m}")
    ax.axvline(var_start, color="#6250d6", linestyle=":", linewidth=1.5,
               label=f"VAR common sample starts {var_start:%Y-%m}")
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=8)
    style_axes(ax, title=title, xlabel="date", ylabel="")
    ax.legend(fontsize=8, loc="lower right")
    return fig


def series_overview(level: pd.Series, transformed: pd.Series, usrec: pd.Series,
                    *, series_id: str, level_units: str, transformed_units: str,
                    break_date: pd.Timestamp | None = None,
                    imputed_dates: Sequence[pd.Timestamp] = ()) -> plt.Figure:
    """F2.1: raw level and transformed target, with recession shading.

    One panel per object, never a shared axis: a level and a growth rate have different
    units, and the methodology forbids squeezing one series so another fits.
    """
    fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    for ax, data, units, label in (
        (axes[0], level, level_units, "raw level"),
        (axes[1], transformed, transformed_units, "modelling target"),
    ):
        shade_recessions(ax, usrec)
        ax.plot(data.index, data.to_numpy(), color="#2a78d6", linewidth=1.0, label=label)
        if break_date is not None:
            ax.axvline(break_date, color="#eb6834", linestyle="--", linewidth=1.2,
                       label=f"Zivot-Andrews break {break_date:%Y-%m}")
        for date in imputed_dates:
            ax.axvline(date, color="#e87ba4", linestyle=":", linewidth=1.2,
                       label=f"imputed {pd.Timestamp(date):%Y-%m}")
        style_axes(ax, title="", xlabel="", ylabel=units)
        handles, labels = ax.get_legend_handles_labels()
        unique = dict(zip(labels, handles))
        ax.legend(unique.values(), unique.keys(), fontsize=7, loc="best")
    axes[0].set_title(
        f"F2.1 {series_id}: {level.index.min():%Y-%m} to {level.index.max():%Y-%m} "
        f"(shaded: NBER recessions)", fontsize=11
    )
    axes[1].set_xlabel("date", fontsize=9)
    return fig


# ---------------------------------------------------------------------------
# F3.1 / F3.2 / F3.3 - in-sample adequacy
# ---------------------------------------------------------------------------


def fitted_vs_observed(actual: pd.Series, fitted: pd.Series, usrec: pd.Series,
                       *, series_id: str, model: str, units: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9, 3.6))
    shade_recessions(ax, usrec)
    ax.plot(actual.index, actual.to_numpy(), color=ACTUAL_COLOUR, linewidth=1.0, label="observed")
    style, _ = MODEL_STYLES.get(model, ("-", "o"))
    ax.plot(fitted.index, fitted.to_numpy(), color=MODEL_COLOURS.get(model, "#2a78d6"),
            linestyle=style, linewidth=1.2, label=f"{model} fitted")
    style_axes(ax, title=f"F3.1 {series_id}: observed and {model} fitted values",
               xlabel="date", ylabel=units)
    ax.legend(fontsize=8)
    return fig


def residual_acf(residuals: np.ndarray, *, series_id: str, model: str,
                 max_lag: int = 24) -> plt.Figure:
    """F3.2: residual autocorrelation with 95% bands (Outputs §5)."""
    values = np.asarray(residuals, dtype=float)
    values = values[np.isfinite(values)]
    n = values.size
    centred = values - values.mean()
    denominator = float(centred @ centred)
    lags = np.arange(1, min(max_lag, n - 1) + 1)
    acf = np.array([float(centred[lag:] @ centred[:-lag]) / denominator for lag in lags])
    band = 1.96 / np.sqrt(n)

    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.bar(lags, acf, width=0.6, color="#2a78d6")
    ax.axhline(0, color=ACTUAL_COLOUR, linewidth=0.8)
    ax.axhline(band, color="#eb6834", linestyle="--", linewidth=1.0, label="95% band")
    ax.axhline(-band, color="#eb6834", linestyle="--", linewidth=1.0)
    style_axes(ax, title=f"F3.2 {series_id} {model}: residual autocorrelation (n={n})",
               xlabel="lag", ylabel="autocorrelation")
    ax.legend(fontsize=8)
    return fig


def regime_probabilities(dates: pd.DatetimeIndex, smoothed: np.ndarray, usrec: pd.Series,
                         *, series_id: str, model: str) -> plt.Figure:
    """F3.3: smoothed regime probabilities, one panel per regime for readability."""
    k = smoothed.shape[1]
    fig, axes = plt.subplots(k, 1, figsize=(9, 2.1 * k), sharex=True)
    axes = np.atleast_1d(axes)
    for regime in range(k):
        ax = axes[regime]
        shade_recessions(ax, usrec)
        ax.plot(dates, smoothed[:, regime], color="#1baf7a", linewidth=1.0)
        ax.set_ylim(-0.02, 1.02)
        style_axes(ax, title="", xlabel="", ylabel=f"P(regime {regime + 1})")
    axes[0].set_title(f"F3.3 {series_id} {model}: smoothed regime probabilities "
                      f"(shaded: NBER recessions)", fontsize=11)
    axes[-1].set_xlabel("date", fontsize=9)
    return fig


def star_transition(z: np.ndarray, g: np.ndarray, *, series_id: str, kind: str,
                    gamma: float, c: float) -> plt.Figure:
    """F3.3 companion: the fitted STAR transition function against its variable."""
    order = np.argsort(z)
    fig, ax = plt.subplots(figsize=(6, 3.4))
    ax.plot(np.asarray(z)[order], np.asarray(g)[order], color="#eda100", linewidth=1.6)
    ax.axvline(c, color="#eb6834", linestyle="--", linewidth=1.0, label=f"threshold c={c:.3g}")
    ax.set_ylim(-0.02, 1.02)
    style_axes(ax, title=f"F3.3 {series_id}: fitted {kind} transition (gamma={gamma:.3g})",
               xlabel="transition variable", ylabel="G")
    ax.legend(fontsize=8)
    return fig


# ---------------------------------------------------------------------------
# F3.4 / F3.5 / F3.6 - forecast evidence
# ---------------------------------------------------------------------------


def actual_vs_forecast(actual: pd.Series, forecasts: Mapping[str, pd.Series],
                       usrec: pd.Series, *, series_id: str, units: str,
                       flagged: Mapping[str, pd.Series] | None = None) -> plt.Figure:
    """F3.4: actual against forecasts, with failed or extreme models separated.

    AR and ARMA are always shown. A model with flagged values goes to its own lower panel
    on its own scale, so one exploding forecast can never make the informative series
    unreadable, and nothing is clipped.
    """
    flagged = flagged or {}
    panels = 2 if flagged else 1
    fig, axes = plt.subplots(panels, 1, figsize=(9, 3.8 * panels), sharex=True)
    axes = np.atleast_1d(axes)

    ax = axes[0]
    shade_recessions(ax, usrec)
    ax.plot(actual.index, actual.to_numpy(), color=ACTUAL_COLOUR, linewidth=1.1, label="actual")
    for model, series in forecasts.items():
        style, _ = MODEL_STYLES.get(model, ("-", "o"))
        ax.plot(series.index, series.to_numpy(), color=MODEL_COLOURS.get(model, "#888"),
                linestyle=style, linewidth=1.1, label=model)
    style_axes(ax, title=f"F3.4 {series_id}: actual and one-step forecasts "
                         f"(shaded: NBER recessions)", xlabel="", ylabel=units)
    ax.legend(fontsize=8, ncol=3)

    if flagged:
        diagnostic = axes[1]
        shade_recessions(diagnostic, usrec)
        diagnostic.plot(actual.index, actual.to_numpy(), color=ACTUAL_COLOUR,
                        linewidth=1.0, label="actual")
        for model, series in flagged.items():
            style, _ = MODEL_STYLES.get(model, ("-", "o"))
            diagnostic.plot(series.index, series.to_numpy(),
                            color=MODEL_COLOURS.get(model, "#888"), linestyle=style,
                            linewidth=1.1, label=f"{model} (flagged)")
        style_axes(diagnostic,
                   title="Diagnostic panel: failed or extreme forecasts, own scale, not clipped",
                   xlabel="date", ylabel=units)
        diagnostic.legend(fontsize=8, ncol=3)
    else:
        axes[-1].set_xlabel("date", fontsize=9)
    return fig


def cumulative_loss_difference(dates: pd.DatetimeIndex,
                               differences: Mapping[str, np.ndarray],
                               usrec: pd.Series, *, series_id: str,
                               benchmark: str = "AR") -> plt.Figure:
    """F3.5: cumulative squared-error difference against the benchmark.

    Shows when relative performance accumulates or reverses, without claiming causal
    timing (Outputs §6).
    """
    fig, ax = plt.subplots(figsize=(9, 3.8))
    shade_recessions(ax, usrec)
    ax.axhline(0, color=ACTUAL_COLOUR, linewidth=0.9)
    for model, values in differences.items():
        style, _ = MODEL_STYLES.get(model, ("-", "o"))
        ax.plot(dates, np.cumsum(values), color=MODEL_COLOURS.get(model, "#888"),
                linestyle=style, linewidth=1.2, label=model)
    style_axes(ax, title=f"F3.5 {series_id}: cumulative squared-error difference "
                         f"versus {benchmark} (below zero favours the competitor)",
               xlabel="target date", ylabel=f"cumulative squared-error difference vs {benchmark}")
    ax.legend(fontsize=8, ncol=3)
    return fig


def state_comparison(table: pd.DataFrame, *, series_id: str, metric: str = "rmse",
                     benchmark: str = "AR") -> plt.Figure:
    """F3.6: state-specific accuracy difference against the benchmark, descriptive only."""
    states = list(dict.fromkeys(table["state"]))
    models = [m for m in dict.fromkeys(table["model"]) if m != benchmark]
    width = 0.8 / max(len(models), 1)

    fig, ax = plt.subplots(figsize=(8, 4))
    for position, model in enumerate(models):
        values = []
        for state in states:
            row = table[(table["model"] == model) & (table["state"] == state)]
            base = table[(table["model"] == benchmark) & (table["state"] == state)]
            values.append(float(row[metric].iloc[0] - base[metric].iloc[0])
                          if len(row) and len(base) else np.nan)
        offsets = np.arange(len(states)) + position * width - 0.4 + width / 2
        ax.bar(offsets, values, width=width * 0.9,
               color=MODEL_COLOURS.get(model, "#888"), label=model)
    ax.axhline(0, color=ACTUAL_COLOUR, linewidth=0.9)
    ax.set_xticks(np.arange(len(states)))
    ax.set_xticklabels([s.replace("_", " ") for s in states], fontsize=8)
    style_axes(ax, title=f"F3.6 {series_id}: {metric.upper()} difference versus {benchmark} "
                         f"by state (descriptive; inference is in the state-loss regression)",
               xlabel="evaluation state", ylabel=f"{metric.upper()} minus {benchmark}")
    ax.legend(fontsize=8)
    return fig


# ---------------------------------------------------------------------------
# F4.8 - estimation-window-length sensitivity
# ---------------------------------------------------------------------------


def window_length_sensitivity(table: pd.DataFrame, *, series_id: str,
                              baseline_length: int, metric: str = "oos_r2_vs_benchmark",
                              benchmark: str = "AR") -> plt.Figure:
    """F4.8: relative h=1 accuracy across the three predeclared window lengths.

    Failure and extreme cases are kept visible, never clipped or hidden (Outputs T4.8).
    """
    lengths = sorted(table["window_length"].unique())
    models = [m for m in dict.fromkeys(table["model"]) if m != benchmark]

    fig, ax = plt.subplots(figsize=(8, 4.2))
    for model in models:
        subset = table[table["model"] == model].sort_values("window_length")
        style, marker = MODEL_STYLES.get(model, ("-", "o"))
        ax.plot(subset["window_length"], subset[metric], color=MODEL_COLOURS.get(model, "#888"),
                linestyle=style, marker=marker, markersize=7, linewidth=1.4, label=model)
        for _, row in subset.iterrows():
            if pd.notna(row.get("n_valid")):
                ax.annotate(f"N={int(row['n_valid'])}",
                            (row["window_length"], row[metric]),
                            textcoords="offset points", xytext=(0, 7), fontsize=6,
                            ha="center", color="#52514e")
    ax.axhline(0, color=ACTUAL_COLOUR, linewidth=0.9)
    ax.axvline(baseline_length, color="#52514e", linestyle=":", linewidth=1.2,
               label=f"baseline window = {baseline_length}")
    ax.set_xticks(lengths)
    style_axes(ax, title=f"F4.8 {series_id}: h=1 accuracy versus {benchmark} by estimation-window length",
               xlabel="estimation window length (observations)",
               ylabel=f"out-of-sample R squared versus {benchmark}")
    ax.legend(fontsize=8, ncol=2)
    return fig
