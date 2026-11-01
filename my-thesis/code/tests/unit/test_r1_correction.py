"""R1 correction workflow: switches, merging, comparison and reconciliation."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from thesis.correction import flags
from thesis.correction.compare import compare_file, compare_trees
from thesis.correction.workflow import (_match_integer_format, _same_value, merge_groups,
                                        reconcile)
from thesis.evaluation import scoring

OUTPUT = Path(__file__).resolve().parents[3] / "output"


# -- switches ------------------------------------------------------------------------

def test_flags_default_on_and_legacy_restores():
    assert all(flags.ACTIVE.as_dict().values())
    with flags.legacy() as f:
        assert not any(f.as_dict().values())
        assert not any(flags.ACTIVE.as_dict().values())
    assert all(flags.ACTIVE.as_dict().values())


def test_configured_restores_after_exception():
    with pytest.raises(RuntimeError):
        with flags.configured(f1_failed_forecast_masking=False):
            assert not flags.ACTIVE.f1_failed_forecast_masking
            raise RuntimeError
    assert flags.ACTIVE.f1_failed_forecast_masking


def test_f1_switch_controls_masking():
    frame = pd.DataFrame({"forecast": [1.0, 50.0], "error": [0.1, 49.0],
                          "status": ["adequate", "failed"]})
    masked = scoring.mask_failed(frame)
    assert np.isnan(masked.loc[1, "forecast"])
    with flags.legacy():
        unchanged = scoring.mask_failed(frame)
    assert unchanged.loc[1, "forecast"] == 50.0


# -- merging -------------------------------------------------------------------------

class _Context:
    def stamp(self, frame):
        return frame.assign(run_id="new")


def _retained(row):
    return "original_retained_unaffected"


def test_merge_groups_keeps_interleaved_order():
    original = pd.DataFrame({"series": ["A", "B", "A", "B"], "model": ["1", "1", "2", "2"],
                             "value": ["a1", "b1", "a2", "b2"], "run_id": "old"})
    recomputed = pd.DataFrame({"series": ["A", "A"], "model": ["1", "2"],
                               "value": ["A1", "A2"]})
    merged = merge_groups(original, recomputed, ["series"], _Context(), _retained)
    assert merged["value"].tolist() == ["A1", "b1", "A2", "b2"]
    assert merged["run_id"].tolist() == ["new", "old", "new", "old"]
    assert merged["correction_status"].tolist() == [
        "recomputed_from_published", "original_retained_unaffected",
        "recomputed_from_published", "original_retained_unaffected"]


def test_merge_groups_inserts_group_of_different_size_whole():
    original = pd.DataFrame({"series": ["A", "B"], "value": ["a", "b"]})
    recomputed = pd.DataFrame({"series": ["A", "A", "A"], "value": ["x", "y", "z"]})
    merged = merge_groups(original, recomputed, ["series"], _Context(), _retained)
    assert merged["value"].tolist() == ["x", "y", "z", "b"]


# -- comparison ----------------------------------------------------------------------

def _write(path: Path, frame: pd.DataFrame) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    return path


def test_compare_file_levels(tmp_path):
    a = _write(tmp_path / "a.csv", pd.DataFrame({"x": ["1.0000000000000002"], "t": ["k"],
                                                 "run_id": ["r1"]}))
    same = _write(tmp_path / "b.csv", pd.DataFrame({"x": ["1.0000000000000002"],
                                                    "t": ["k"], "run_id": ["r2"]}))
    close = _write(tmp_path / "c.csv", pd.DataFrame({"x": ["1.0000000000000004"],
                                                     "t": ["k"], "run_id": ["r1"]}))
    far = _write(tmp_path / "d.csv", pd.DataFrame({"x": ["1.001"], "t": ["k"],
                                                   "run_id": ["r1"]}))
    text = _write(tmp_path / "e.csv", pd.DataFrame({"x": ["1.0000000000000002"],
                                                    "t": ["other"], "run_id": ["r1"]}))
    assert compare_file(a, same)["identical"]                 # provenance ignored
    result = compare_file(a, close)
    assert not result["identical"] and result["within_tolerance"]
    assert not compare_file(a, far)["within_tolerance"]
    assert not compare_file(a, text)["within_tolerance"]       # text never tolerated


def test_compare_parquet_missing_values_are_equal(tmp_path):
    frame = pd.DataFrame({"x": [1.0, np.nan], "s": ["a", None]})
    frame.to_parquet(tmp_path / "a.parquet")
    frame.assign(s=["a", None]).to_parquet(tmp_path / "b.parquet", compression="gzip")
    assert compare_file(tmp_path / "a.parquet", tmp_path / "b.parquet")["identical"]


def test_compare_trees_reports_added_and_removed(tmp_path):
    _write(tmp_path / "o" / "t.csv", pd.DataFrame({"x": [1]}))
    _write(tmp_path / "o" / "gone.csv", pd.DataFrame({"x": [1]}))
    _write(tmp_path / "c" / "t.csv", pd.DataFrame({"x": [1]}))
    _write(tmp_path / "c" / "new.csv", pd.DataFrame({"x": [1]}))
    status = compare_trees(tmp_path / "o", tmp_path / "c").set_index("path")["status"]
    assert status.to_dict() == {"gone.csv": "removed", "new.csv": "added",
                                "t.csv": "identical"}


# -- reconciliation ------------------------------------------------------------------

def test_reconcile_restores_only_unaffected_cells(tmp_path):
    name = "tables/t.csv"
    _write(tmp_path / "o" / name, pd.DataFrame({"k": ["a", "b"], "v": ["1.0000000000000002",
                                                                       "5.0"]}))
    _write(tmp_path / "l" / name, pd.DataFrame({"k": ["a", "b"], "v": ["1.0000000000000004",
                                                                       "5.0"]}))
    _write(tmp_path / "c" / name, pd.DataFrame({"k": ["a", "b"], "v": ["1.0000000000000004",
                                                                       "7.0"]}))
    account = reconcile(tmp_path / "o", tmp_path / "l", tmp_path / "c", [name])
    out = pd.read_csv(tmp_path / "c" / name, dtype=str)
    assert out["v"].tolist() == ["1.0000000000000002", "7.0"]
    row = account.iloc[0]
    assert row["cells_restored_to_original"] == 1 and row["cells_changed_by_corrections"] == 1


def test_same_value_and_integer_format():
    assert _same_value("0", "0.0") and not _same_value("0", "1") and _same_value("x", "x")
    assert not _same_value("x", "y")
    legacy = pd.DataFrame({"b": ["4.0", ""], "s": ["x", "y"]})
    corrected = pd.DataFrame({"b": ["4.0", "", "4"], "s": ["x", "y", "5"]})
    _match_integer_format(corrected, legacy, [2])
    assert corrected["b"].tolist() == ["4.0", "", "4.0"] and corrected.at[2, "s"] == "5"


# -- published-chain reconstruction --------------------------------------------------

def test_chain_from_published_rebuilds_failures():
    from thesis.correction.rescore import chain_from_published
    from thesis.models.registry import ModelSpec
    forecasts = pd.DataFrame({
        "model": "AR", "horizon": [1, 1, 1],
        "origin_date": pd.to_datetime(["2000-01-01", "2000-02-01", "2000-03-01"]),
        "status": ["adequate", "fragile", "failed"],
        "reason_codes": ["", "RESIDUAL_AUTOCORR", ""], "forecast": [1.0, 2.0, np.nan]})
    audit = pd.Series({"attempted_origins": 3, "valid_origins": 2, "failed_origins": 1,
                       "origins_from_cache": 0})
    spec = ModelSpec(model="AR", order=1)
    index = pd.date_range("1990-01-01", periods=200, freq="MS")
    chain = chain_from_published("X", spec, 60, forecasts, audit, [1], index)
    assert [r.status.value for r in chain.fit_records] == ["adequate", "fragile", "failed"]
    categories = [(f.category.value, f.reason_code.value) for f in chain.failures]
    assert ("failed", "NONCONVERGENCE") in categories
    assert ("fragile", "RESIDUAL_AUTOCORR") in categories
    assert (chain.attempted, chain.valid, chain.failed) == (3, 2, 1)


# -- the validation gate on the real published tree (about three minutes) ------------

@pytest.mark.slow
@pytest.mark.filterwarnings("ignore::RuntimeWarning")  # statsmodels, as in the full run
@pytest.mark.skipif(not (OUTPUT / "forecasts").exists(), reason="published output absent")
def test_legacy_mode_reproduces_published_tables(tmp_path):
    from thesis.correction import workflow
    summary = workflow.run(OUTPUT, tmp_path / "staging", legacy=True)
    files = [f for f in summary["regenerated_files"] if f not in workflow.WORKFLOW_FILES]
    comparison = compare_trees(OUTPUT, tmp_path / "staging", files=files)
    assert set(comparison["status"]) <= {"identical", "equal_within_fp_tolerance"}
    assert comparison["max_relative_difference"].fillna(0).max() <= 1e-9
