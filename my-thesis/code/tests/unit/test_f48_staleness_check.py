"""The F4.8 staleness check flags a figure whose plotted inputs changed but whose bytes did not."""

from __future__ import annotations

import csv
import importlib.util
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "f48", ROOT / "reports" / "part8" / "corrections" / "r1" / "f48_staleness_check.py")
f48 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f48)

HEADER = "series,model,horizon,window_length,n_valid,oos_r2_vs_benchmark,rmse\n"


def _commit(repo: Path, files: dict[str, str | bytes]) -> str:
    for rel, content in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content if isinstance(content, bytes) else content.encode())
    run = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True,  # noqa: E731
                                    capture_output=True, text=True).stdout.strip()
    run("add", "-A")
    run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x")
    return run("rev-parse", "HEAD")


def test_flags_only_a_figure_left_behind_by_its_table(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    table = HEADER + "UNRATE,MSAR,1,240,633,0.69,0.5\nGDPC1,MSAR,1,120,200,0.1,0.4\n"
    changed = HEADER + "UNRATE,MSAR,1,240,633,0.19,0.5\nGDPC1,MSAR,1,120,200,0.1,0.9\n"
    files = {}
    for tree, tab in (("o", table), ("r", changed)):
        files[f"{tree}/robustness/window_length_comparison.csv"] = tab
        for series in ("UNRATE", "GDPC1"):
            for ext in ("png", "pdf"):
                files[f"{tree}/figures/F4.8_{series}.{ext}"] = f"{series}{ext}".encode()
    commit = _commit(tmp_path, files)
    out = tmp_path / "out.csv"
    f48.main(["--repo", str(tmp_path), "--release", f"{commit}:r", "--published-path", "o",
              "--out", str(out)])
    rows = list(csv.DictReader(open(out)))
    stale = sorted(r["figure"] for r in rows if r["stale"] == "True")
    # UNRATE: the plotted R2 changed, the figure did not. GDPC1: only rmse (not plotted).
    assert stale == ["figures/F4.8_UNRATE.pdf", "figures/F4.8_UNRATE.png"]
