"""The staged B1 correction builder: patch rules, block identification, safety."""

from __future__ import annotations

import sys
from collections import namedtuple
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "colab"))
import r1_b1_staged_correction as b1  # noqa: E402

PROV = list(b1.PROV)


def _table(values, run="orig"):
    return pd.DataFrame({"series": ["UNRATE", "UNRATE", "GDPC1"], "model": ["MSAR", "AR", "MSAR"],
                         "rmse": values, "rank_rmse": [1, 2, 1],
                         **{c: [run] * 3 for c in PROV}})


def _write(frame, path):
    frame.to_csv(path, index=False)
    return path


def test_patch_takes_only_cells_where_candidate_differs_from_reference(tmp_path):
    published = _write(_table(["0.49230000000000002", "0.5", "0.7"]), tmp_path / "o.csv")
    # the reference reproduces the published value only within floating point
    reference = _write(_table(["0.4923", "0.5", "0.7"], run="ref"), tmp_path / "r.csv")
    candidate = _write(_table(["0.4923", "0.5", "0.71"], run="cand"), tmp_path / "c.csv")
    stamp = b1.Stamp("b1-test", "d", "c", "pin")
    changes = b1.patch_csv(published, reference, candidate, tmp_path / "s.csv", stamp, "t.csv")
    staged = pd.read_csv(tmp_path / "s.csv", dtype=str, keep_default_na=False)
    assert [(c["row"], c["column"], c["corrected"]) for c in changes] == [(2, "rmse", "0.71")]
    # unchanged cells keep the PUBLISHED text, not the reference's reprint
    assert staged.at[0, "rmse"] == "0.49230000000000002"
    assert staged.at[0, "run_id"] == "orig" and staged.at[2, "run_id"] == "b1-test"
    assert staged.at[2, "code_commit_sha"] == "pin"


def test_patch_refuses_misaligned_rows_and_non_roundtripping_files(tmp_path):
    published = _write(_table(["1", "2", "3"]), tmp_path / "o.csv")
    shuffled = _table(["1", "2", "3"]).iloc[[1, 0, 2]].reset_index(drop=True)
    reference = _write(shuffled, tmp_path / "r.csv")
    with pytest.raises(b1.StagingError, match="not aligned"):
        b1.patch_csv(published, reference, published, tmp_path / "s.csv",
                     b1.Stamp("x", "d", "c", "p"), "t.csv")
    odd = tmp_path / "odd.csv"
    odd.write_text("series,model\n\"UNRATE\",MSAR\n")  # quoted where pandas would not quote
    with pytest.raises(b1.StagingError, match="round trip"):
        b1.assert_roundtrip(odd)


def test_failure_signature_follows_the_pinned_event_rule():
    R = namedtuple("R", "refit_date status reason_codes")
    rows = [R("1982-10-01", "failed", "NONCONVERGENCE;SINGULAR_COV"), R("1982-11-01", "failed", ""),
            R("1982-12-01", "fragile", "SINGULAR_COV"), R("1983-01-01", "adequate", "")]
    assert b1.failure_signature(rows) == [
        ("1982-10-01", "failed", "NONCONVERGENCE"), ("1982-10-01", "failed", "SINGULAR_COV"),
        ("1982-11-01", "failed", "NONCONVERGENCE"), ("1982-12-01", "fragile", "SINGULAR_COV")]


def test_find_blocks_returns_every_contiguous_occurrence():
    reg = pd.DataFrame({"refit_date": ["a", "b", "x", "a", "b", "a"],
                        "category": ["failed"] * 6, "reason_code": ["N"] * 6})
    sig = [("a", "failed", "N"), ("b", "failed", "N")]
    assert b1.find_blocks(reg, sig) == [0, 3]


def test_builder_never_estimates_and_never_writes_the_published_tree():
    source = (ROOT / "colab" / "r1_b1_staged_correction.py").read_text()
    assert "no_estimation_allowed()" in source and "estimation_forbidden()" in source
    assert 'calls["n"]' in source and "the published tree changed during staging" in source
    assert "git push" not in source
    assert "shutil.copytree(original, staged)" in source
    # every write goes under --out (staged tree or records)
    for line in source.splitlines():
        if ".to_parquet(" in line or "write_text(" in line:
            assert "staged" in line or "args.out" in line or "target" in line, line
