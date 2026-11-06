"""The read-only original-cache audit (Option B3): identification, safety, notebook."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[3]
COLAB = ROOT / "colab"
sys.path.insert(0, str(COLAB))
import make_r1_original_cache_audit_notebook as gen  # noqa: E402
import r1_original_cache_audit as audit  # noqa: E402
import r1_tierb as tb  # noqa: E402


def _code():
    nb = json.loads((COLAB / gen.NOTEBOOK).read_text())
    return ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]


def test_notebook_matches_its_generator_and_parses():
    first = _code()[0]
    orch = re.search(r'^ORCH_COMMIT = "([^"]+)"', first, re.M).group(1)
    assert json.loads((COLAB / gen.NOTEBOOK).read_text()) == gen.build(orch)
    for source in _code():
        ast.parse(source)
        assert not re.search(r"^\s*[!%]", source, re.M)


def test_notebook_never_pushes_and_writes_only_its_audit_folder():
    text = "\n".join(_code())
    assert "git push" not in text and '"push"' not in text
    assert "BATCH_ID" not in text and "RUN_TIER_B" not in text
    assert 'AUDIT_DRIVE = Path(DRIVE_ROOT) / "baseline" / "r1_original_cache_audit" / SESSION' in text
    export = next(c for c in _code() if "export_manifest.json" in c)
    assert "assert not AUDIT_DRIVE.exists()" in export
    # every Drive write in the export cell goes under AUDIT_DRIVE
    for line in export.splitlines():
        if "copyfile(" in line or "write_text(" in line:
            assert "target" in line or "AUDIT_DRIVE" in line, line
    restore = next(c for c in _code() if "IncrementalArchive" in c)
    assert ".restore(" in restore and ".sync(" not in restore
    assert "assert PAYLOADS == EXPECTED_ORIGINAL_PAYLOADS" in restore
    run = next(c for c in _code() if "r1_original_cache_audit.py" in c)
    assert '"--stage", "all"' in run


def test_the_audit_script_never_writes_the_original_cache():
    source = (COLAB / "r1_original_cache_audit.py").read_text()
    view = audit.ReadOnlyView.__new__(audit.ReadOnlyView)
    with pytest.raises(tb.TierBError, match="read-only"):
        audit.ReadOnlyView.put(view, None, {})
    assert "no_estimation_allowed()" in source and "estimation_forbidden()" in source
    assert "git push" not in source


@pytest.fixture(scope="module")
def jobs():
    tb.use_scientific_code(ROOT / "code")
    built, _identity, _config = tb.build_jobs(ROOT / "output", ROOT / "code")
    return built


def test_published_records_are_identified_by_their_stage_block(jobs):
    records = pd.read_parquet(ROOT / "output" / "models" / "fit_records.parquet")
    expected = {"forecasting:UNRATE|MSAR": (5086, 5789, 704, 11),
                "T4.1:UNRATE|MSAR": (15544, 16246, 703, 0),
                "T4.8:UNRATE|240:MSAR": (40337, 41040, 704, 11)}
    for task, (first, last, n, failed) in expected.items():
        found, provenance = audit.stage_block(records, jobs[task])
        assert found is not None, provenance
        rows = [r.Index for r in found.values()]
        assert (min(rows), max(rows), len(found)) == (first, last, n), (task, provenance)
        assert sum(1 for r in found.values() if r.status == "failed") == failed
    # the two runs of the same chain disagree exactly at 1983-04/05/06
    a, _ = audit.stage_block(records, jobs["forecasting:UNRATE|MSAR"])
    b, _ = audit.stage_block(records, jobs["T4.8:UNRATE|240:MSAR"])
    differ = sorted(d for d in a if a[d].params != b[d].params or a[d].loglik != b[d].loglik)
    assert differ == ["1983-04-01", "1983-05-01", "1983-06-01"]


def test_start_sets_are_parsed_from_both_formats():
    text = ("n_starts=2; selection_rule=lowest objective among admissible starts; none reported "
            "convergence; starts=deterministic_p0.9:obj=109.075,conv=False; "
            "deterministic_p0.95:obj=255.827,conv=False")
    assert audit.start_set(text) == {"deterministic_p0.9": 109.075, "deterministic_p0.95": 255.827}
    assert audit.start_set({"starts": "warm:obj=-47.3852,conv=True"}) == {"warm": -47.3852}
