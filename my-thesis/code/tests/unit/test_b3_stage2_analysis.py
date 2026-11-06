"""Keyed comparisons in the B3 stage-2 analysis (regression for the T3.4 many-to-many join)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[3]
R1 = ROOT / "reports" / "part8" / "corrections" / "r1"
_spec = importlib.util.spec_from_file_location("b3_stage2_analysis", R1 / "b3_stage2_analysis.py")
analysis = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(analysis)


def _mcs(p_shift=0.0, flip=False):
    rows = []
    for h in (1, 3):
        for loss in ("squared", "absolute"):
            for cl in (0.9, 0.75):
                for model in ("AR", "MSAR"):
                    rows.append({"series": "UNRATE", "horizon": h, "loss": loss,
                                 "confidence_level": cl, "model": model,
                                 "in_mcs": not (flip and model == "MSAR" and h == 3 and cl == 0.75),
                                 "mcs_p_value": 0.5 + (p_shift if model == "MSAR" else 0.0)})
    return pd.DataFrame(rows)


def test_mcs_extract_is_one_row_per_key_including_confidence_level():
    merged = analysis.mcs_extract(_mcs(), _mcs(p_shift=0.1))
    assert len(merged) == 16 and not merged.duplicated(analysis.T34_KEYS).any()
    assert "confidence_level" in analysis.T34_KEYS
    summary = analysis.mcs_summary(merged)
    assert summary["membership_changes"] == 0 and summary["rows"] == 16
    assert summary["max_abs_p_value_change"] == pytest.approx(0.1)


def test_the_revision_1_key_without_confidence_level_is_refused():
    """Revision 1 merged on (horizon, loss, model): a many-to-many join doubling the rows."""
    old_keys = ["horizon", "loss", "model"]
    with pytest.raises(analysis.ComparisonError, match="share a key"):
        analysis.keyed_merge(_mcs(), _mcs(), old_keys, ["in_mcs", "mcs_p_value"], "T3.4")
    # what the unchecked pandas merge silently did
    assert len(_mcs()[old_keys + ["in_mcs"]].merge(_mcs()[old_keys + ["in_mcs"]], on=old_keys)) == 32


def test_membership_flip_is_detected_at_its_confidence_level():
    merged = analysis.mcs_extract(_mcs(), _mcs(flip=True))
    flipped = merged[merged.membership_changed]
    assert len(flipped) == 2  # squared and absolute loss, h=3, MSAR, 75% only
    assert set(flipped.confidence_level) == {0.75} and set(flipped.horizon) == {3}


def test_keyed_merge_refuses_different_key_sets():
    b = _mcs()
    b.loc[0, "model"] = "STAR"
    with pytest.raises(analysis.ComparisonError, match="key sets differ"):
        analysis.keyed_merge(_mcs(), b, analysis.T34_KEYS, ["in_mcs"], "T3.4")


def test_cell_comparison_refuses_misaligned_rows():
    a = _mcs()
    b = a.iloc[::-1].reset_index(drop=True)
    with pytest.raises(analysis.ComparisonError, match="not aligned"):
        analysis.compare_table(a, b, "T3.4")
    info, cells, flips = analysis.compare_table(a, _mcs(flip=True), "T3.4")
    assert info["keys_unique"] and info["decision_flips"] == 2 and len(cells) == 2


@pytest.mark.parametrize("name, keys, rows", [
    ("T3.4_unrate_mcs_reference_vs_candidate.csv", analysis.T34_KEYS, 64),
    ("window_length_mcs_unrate_reference_vs_candidate.csv", analysis.WL_MCS_KEYS, 48)])
def test_committed_mcs_extracts_have_unique_keys(name, keys, rows):
    path = R1 / "evidence" / "b1_staged_20261106" / "stage2_rev2" / name
    if not path.exists():
        pytest.skip("evidence not present")
    frame = pd.read_csv(path)
    assert len(frame) == rows and not frame.duplicated(keys).any()
    assert int(frame.membership_changed.sum()) == 0
