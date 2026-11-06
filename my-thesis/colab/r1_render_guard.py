"""Rendering guard: thesis figures must be drawn with matplotlib's own default configuration.

The published figures were rendered by matplotlib 3.11.2 with no site or user matplotlibrc
(DejaVu Sans, default hinting). A machine-level rc file silently changes the figure bytes
and the text layout. For example, the Claude Code cloud container sets
`MATPLOTLIBRC=/etc/matplotlib`, whose rc file selects Inter with no hinting. Such a file
is read when matplotlib is imported, so the guard has two parts:

* `pin_default_rc()` points `MATPLOTLIBRC` at the repo-tracked EMPTY file
  `colab/matplotlibrc.default`. It must run before matplotlib is imported. If matplotlib
  is already imported, it accepts only that file or matplotlib's bundled rc.
* `check_default_rendering()` verifies, after import, that:
  - every rcParam that affects rendering equals `matplotlib.rcParamsDefault`;
  - the font that text resolves to is DejaVu Sans;
  - the matplotlib version equals the expected one, when an expected version is given.
  It returns a record for the run report and raises `RenderGuardError` on any mismatch.

Nothing here changes a scientific computation: the guard only refuses to render under a
configuration that differs from the one used for the published outputs.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

DEFAULT_RC = Path(__file__).resolve().parent / "matplotlibrc.default"
EXPECTED_FONT_FILE = "DejaVuSans.ttf"
# rcParams that cannot affect pixels or vector output, or that a backend sets itself.
IGNORED_KEYS = {"backend", "backend_fallback", "interactive", "webagg.port", "webagg.address",
                "webagg.port_retries", "webagg.open_in_browser", "tk.window_focus",
                "timezone", "toolbar", "figure.max_open_warning", "savefig.directory",
                "keymap.back", "keymap.copy", "keymap.forward", "keymap.fullscreen",
                "keymap.grid", "keymap.grid_minor", "keymap.help", "keymap.home",
                "keymap.pan", "keymap.quit", "keymap.quit_all", "keymap.save",
                "keymap.xscale", "keymap.yscale", "keymap.zoom", "keymap.xscale",
                "macosx.window_mode", "figure.raise_window", "datapath"}


class RenderGuardError(RuntimeError):
    pass


def pin_default_rc() -> Path:
    """Use matplotlib's built-in defaults. Call before the first `import matplotlib`."""
    if not DEFAULT_RC.is_file() or DEFAULT_RC.read_text().strip():
        raise RenderGuardError(f"{DEFAULT_RC} must exist and be empty")
    if "matplotlib" in sys.modules:
        import matplotlib
        bundled = Path(matplotlib.get_data_path()) / "matplotlibrc"
        if Path(matplotlib.matplotlib_fname()).resolve() not in (DEFAULT_RC, bundled.resolve()):
            raise RenderGuardError(
                "matplotlib was imported before the rendering guard, with rc file "
                f"{matplotlib.matplotlib_fname()}; start a new process with "
                f"MATPLOTLIBRC={DEFAULT_RC}")
    os.environ["MATPLOTLIBRC"] = str(DEFAULT_RC)
    return DEFAULT_RC


def check_default_rendering(expected_version: str | None = None) -> dict:
    """Refuse a non-default rendering configuration; return a record for the report."""
    import matplotlib
    from matplotlib import font_manager

    fname = matplotlib.matplotlib_fname()
    differing = sorted(
        key for key in matplotlib.rcParamsDefault
        if key not in IGNORED_KEYS
        and matplotlib.rcParams[key] != matplotlib.rcParamsDefault[key])
    # the font that text actually gets: the first family of font.family, as rendered
    font = font_manager.findfont(
        font_manager.FontProperties(family=list(matplotlib.rcParams["font.family"])),
        fallback_to_default=False)
    record = {"matplotlib_version": matplotlib.__version__,
              "matplotlib_fname": fname,
              "rc_differs_from_default": differing,
              "font_family": list(matplotlib.rcParams["font.family"]),
              "resolved_text_font": Path(font).name,
              "expected_matplotlib_version": expected_version}
    problems = []
    if differing:
        problems.append(f"rcParams differ from matplotlib's defaults: {differing}")
    if Path(font).name != EXPECTED_FONT_FILE:
        problems.append(f"text resolves to {Path(font).name}, not {EXPECTED_FONT_FILE}")
    if expected_version is not None and matplotlib.__version__ != expected_version:
        problems.append(f"matplotlib {matplotlib.__version__}, expected {expected_version}")
    if problems:
        raise RenderGuardError("non-default rendering configuration (rc file "
                               f"{fname}): " + "; ".join(problems))
    record["ok"] = True
    return record


def expected_version_from(output_tree: Path | str) -> str | None:
    """The matplotlib version recorded in a published tree's run manifest, if any."""
    import json
    manifest = Path(output_tree) / "manifests" / "run_manifest.json"
    if not manifest.is_file():
        return None

    def find(node):
        if isinstance(node, dict):
            if isinstance(node.get("matplotlib"), str):
                return node["matplotlib"]
            for value in node.values():
                hit = find(value)
                if hit:
                    return hit
        return None

    return find(json.loads(manifest.read_text()))
