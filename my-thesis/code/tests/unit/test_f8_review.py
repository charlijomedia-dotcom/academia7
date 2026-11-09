"""F8 (readable F3.4 main panel): presentation-only behaviour and the committed review package."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from thesis.correction import flags as correction_flags
from thesis.reporting import figures

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "code" / "src" / "thesis"
REVIEW = ROOT / "reports" / "part8" / "corrections" / "r1" / "f8_review"
TARGETS = ("GDPC1", "CPIAUCSL", "UNRATE", "INDPRO", "FEDFUNDS", "M2SL")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_the_f8_switch_is_read_only_by_the_f34_plotting_function():
    uses = [(p.relative_to(SRC).as_posix(), i) for p in SRC.rglob("*.py")
            for i, line in enumerate(p.read_text().splitlines(), 1)
            if "f8_readable_main_panel" in line]
    files = {f for f, _ in uses}
    assert files == {"reporting/figures.py", "correction/flags.py"}, uses
    source = (SRC / "reporting/figures.py").read_text()
    start = source.index("def actual_vs_forecast")
    end = source.index("\ndef ", start + 1)
    assert source.count("f8_readable_main_panel") == source[start:end].count("f8_readable_main_panel")


def _inputs():
    dates = pd.date_range("2000-01-01", periods=24, freq="MS")
    actual = pd.Series(np.linspace(-5, 5, 24), index=dates)
    forecasts = {"AR": actual + 0.1, "STAR": actual.copy()}
    forecasts["STAR"].iloc[5] = 1e9
    flagged = {"STAR": forecasts["STAR"].iloc[[5]]}
    failed = {"AR": pd.Series([40.0], index=[dates[10]])}
    usrec = pd.Series(0, index=dates)
    return actual, forecasts, flagged, failed, usrec


@pytest.mark.parametrize("on", [False, True])
def test_flagged_values_leave_the_main_panel_only_with_f8_and_stay_in_the_diagnostic_panel(on):
    actual, forecasts, flagged, failed, usrec = _inputs()
    with correction_flags.configured(f8_readable_main_panel=on):
        fig = figures.actual_vs_forecast(actual, forecasts, usrec, series_id="X", units="u",
                                         flagged=flagged, failed=failed)
    main, diagnostic = fig.axes[0], fig.axes[1]
    star_main = next(l for l in main.get_lines() if l.get_label() == "STAR").get_ydata()
    assert np.isnan(star_main[5]) == on                    # omitted only with F8
    assert ("omitted here" in main.get_title()) == on      # and announced
    plotted = np.concatenate([np.asarray(l.get_ydata(), dtype=float) for l in diagnostic.get_lines()])
    assert 1e9 in plotted and 40.0 in plotted              # nothing clipped or deleted
    labels = [l.get_label() for l in diagnostic.get_lines()]
    assert "STAR extreme (scored)" in labels and "AR failed fit (raw value, not scored)" in labels
    assert (diagnostic.get_yscale() == "symlog") == on     # 1e9 > 100 x max|actual|
    assert ("symmetric log scale" in diagnostic.get_title()) == on
    import matplotlib.pyplot as plt
    plt.close(fig)


def _hash_rows():
    with open(REVIEW / "f8_figure_hashes.csv", newline="") as fh:
        return list(csv.DictReader(fh))


def test_review_package_hashes_match_the_committed_figures():
    rows = _hash_rows()
    assert {r["figure"] for r in rows} == {f"figures/F3.4_{t}.{e}" for t in TARGETS
                                          for e in ("png", "pdf")}
    for r in rows:
        name = Path(r["figure"]).name
        assert r["legacy_rerender_equals_archived"] == "True"
        assert sha(REVIEW / "after" / name) == r["f8_sha256"]
        assert r["f8_sha256"] != r["archived_sha256"]
        if name.endswith(".png"):
            assert sha(REVIEW / "before" / name) == r["archived_sha256"]


def test_archived_hashes_are_those_of_the_verified_archive_inventory():
    inventory = ROOT / "reports/part8/corrections/r1/evidence/archive_verification_20261109/archive_inventory.csv"
    with open(inventory, newline="") as fh:
        archived = {r["path"]: r["sha256"] for r in csv.DictReader(fh)}
    assert sha(inventory) == "24ee8bee0ca0aca3850c2bffdb1e842e7576275c741d38ba7c09841886209a58"
    for r in _hash_rows():
        assert archived[r["figure"]] == r["archived_sha256"]
        assert archived[r["figure"] + ".provenance.json"] == r["archived_sidecar_sha256"]


def test_proposed_sidecars_keep_the_archived_provenance_and_name_the_amendment():
    report = json.loads((REVIEW / "render_report.json").read_text())
    assert report["render_guard"]["ok"] and report["render_guard"]["resolved_text_font"] == "DejaVuSans.ttf"
    for r in _hash_rows():
        name = Path(r["figure"]).name
        side = json.loads((REVIEW / "after_sidecars_proposed" / f"{name}.provenance.json").read_text())
        assert side["code_commit_sha"] == "8aaa4217536ab3cb942dd248dd19ece7838a8d60"
        assert side["figure_sha256"] == r["f8_sha256"]
        assert side["artifact"] == name and side["figure_id"] == "F3.4"
        assert re.search(r"F8 readable main panel", side["presentation_amendment"])
        assert side["run_id"] == "<release run id>"
