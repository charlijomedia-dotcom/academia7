"""Stage 4 of the integration dry run: each acceptance criterion fails on a violation."""

from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "colab"))
import r1_integration_common as ic  # noqa: E402
import r1_integration_validate as val  # noqa: E402
import r1_tierb as tb  # noqa: E402

CERT_DIR = (ROOT / "reports" / "part8" / "corrections" / "r1" / "evidence" /
            "integration_prep_20261106" / "certificates")
B2_BY_ORIGIN = CERT_DIR.parent / "b2_direct_review" / "b2_vs_original_cache_by_origin.csv.gz"


def certificates() -> dict:
    out = {}
    for path in sorted(CERT_DIR.glob("COMPLETE-*.json")):
        cert = json.loads(path.read_text())
        out[cert["batch"]] = cert
    return out


# -- A3 ------------------------------------------------------------------------------------

def _summary(**change) -> dict:
    sources = {"re-estimated": sorted(list(tb.TIER_A_CHAINS) + list(tb.TIER_B_CHAINS)),
               "cache": [f"c{i}" for i in range(17)], "unavailable": [f"u{i}" for i in range(26)],
               "published": list(ic.B1_STAGED_TASKS) + [f"p{i}" for i in range(46)]}
    sources.update(change)
    return {"chain_sources": sources}


def _classification(tmp_path: Path, affected=()) -> Path:
    path = tmp_path / "classification.csv"
    rows = [{"task_id": f"u{i}", "affected_by_correction": str(f"u{i}" in affected)} for i in range(26)]
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_a3_passes_the_planned_sources(tmp_path):
    assert val.check_sources(_summary(), _classification(tmp_path))["problems"] == []


@pytest.mark.parametrize("change, affected, message", [
    ({"re-estimated": sorted(tb.TIER_B_CHAINS)}, (), "not exactly the 17"),
    ({"cache": [f"c{i}" for i in range(16)] + ["T4.1:FEDFUNDS|MSAR"]}, (), "rule-sensitive"),
    ({}, ("u3",), "affected by a correction"),
    ({"published": [f"p{i}" for i in range(48)]}, (), "B1-staged chains"),
    ({"unavailable": [f"u{i}" for i in range(25)]}, (), "source counts")])
def test_a3_refuses(tmp_path, change, affected, message):
    problems = val.check_sources(_summary(**change), _classification(tmp_path, affected))["problems"]
    assert any(message in p for p in problems), problems


# -- A8 ------------------------------------------------------------------------------------

def _dependents(**override) -> dict:
    certs = certificates()
    expected = val.expected_replacements(B2_BY_ORIGIN)
    fit = {}
    for task in list(tb.TIER_A_CHAINS) + list(tb.TIER_B_CHAINS):
        if task in tb.TIER_A_CHAINS:
            planned, failed = tb.TIER_A_CHAINS[task]
            statuses = {"adequate": planned - failed, "failed": failed} if failed else {"adequate": planned}
            records = planned
        else:
            batch = next(b for b, ts in tb.BATCHES.items() if task in ts)
            chain = certs[batch]["chains"][task]
            statuses = {k: chain[k] for k in ("adequate", "fragile", "failed") if chain[k]}
            records = chain["planned_origins"]
        fit[task] = {"statuses": statuses, "records": records,
                     "replaced_origins": sorted(expected.get(task, set()))}
    fit.update(override)
    return {"fit_records": fit}


def test_a8_expected_b2_replacements_are_the_direct_review_differences():
    expected = val.expected_replacements(B2_BY_ORIGIN)
    assert {t: len(v) for t, v in expected.items()} == {"T4.1:FEDFUNDS|MSAR": 43,
                                                         "T4.8:UNRATE|180:MSAR": 6}


def test_a8_passes_when_records_match_the_certificates():
    assert val.check_reestimated(_dependents(), certificates(), B2_BY_ORIGIN)["problems"] == []


def test_a8_refuses_a_replaced_record_the_review_does_not_explain():
    dep = _dependents()
    dep["fit_records"]["T4.8:UNRATE|300:MSAR"]["replaced_origins"] = ["2001-01-01"]
    problems = val.check_reestimated(dep, certificates(), B2_BY_ORIGIN)["problems"]
    assert any("T4.8:UNRATE|300:MSAR: replaced 1" in p for p in problems)


def test_a8_refuses_statuses_that_differ_from_the_certificate():
    dep = _dependents()
    dep["fit_records"]["T4.1:FEDFUNDS|MSAR"]["statuses"] = {"adequate": 124, "fragile": 450, "failed": 52}
    problems = val.check_reestimated(dep, certificates(), B2_BY_ORIGIN)["problems"]
    assert any("T4.1:FEDFUNDS|MSAR: statuses" in p for p in problems)


def test_a8_refuses_a_chain_that_was_not_replayed():
    dep = _dependents()
    del dep["fit_records"]["T4.1:UNRATE|ARMA"]
    problems = val.check_reestimated(dep, certificates(), B2_BY_ORIGIN)["problems"]
    assert any("not replayed" in p for p in problems)


# -- A12 attribution ---------------------------------------------------------------------

def _tree(root: Path, files: dict[str, pd.DataFrame | bytes]) -> None:
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            content.to_csv(path, index=False)


def _attribution_fixture(tmp_path: Path, *, cause_rows, release_extra=None, base_extra=None):
    base, release, work = tmp_path / "base", tmp_path / "release", tmp_path / "work"
    t41_base = pd.DataFrame({"series": ["FEDFUNDS", "GDPC1"], "n_failed": ["52", "0"],
                             "rmse": ["1.0", "2.0"], "run_id": ["b", "b"]})
    t41_rel = pd.DataFrame({"series": ["FEDFUNDS", "GDPC1"], "n_failed": ["49", "0"],
                            "rmse": ["1.0", "2.5"], "run_id": ["r", "r"]})
    _tree(base, {"robustness/T4.1_x.csv": t41_base, "other/keep.csv": pd.DataFrame({"a": ["1"]}),
                 **(base_extra or {})})
    _tree(release, {"robustness/T4.1_x.csv": t41_rel, "other/keep.csv": pd.DataFrame({"a": ["1"]}),
                    **(release_extra or {})})
    (work / "assembly" / "legacy").mkdir(parents=True)
    ic.write_rows(work / "assembly" / "reconcile_cell_causes.csv.gz", cause_rows)
    ic.write_rows(work / "assembly" / "legacy" / "r1_comparison.csv", [{"path": "x", "status": "identical"}])
    dependents = {"dependent_files": [], "wald_rows": {"rows_changed": []},
                  "t46_summary": {"rows_changed": []}, "t47_status_counts": {"rows_changed": []}}
    return val.attribute(base, release, work, {"robustness/T4.1_x.csv"}, dependents, {"rows": set()})


def test_a12_every_cell_has_a_cause(tmp_path):
    causes = [{"path": "robustness/T4.1_x.csv", "row": 0, "column": "n_failed", "cause": "reestimated_chain"},
              {"path": "robustness/T4.1_x.csv", "row": 1, "column": "rmse", "cause": "correction"}]
    result = _attribution_fixture(tmp_path, cause_rows=causes)
    assert result["unexplained"] == []
    assert {(c["row"], c["cause"]) for c in result["cells"]} == {(0, "reestimated_chain"), (1, "correction")}


def test_a12_a_cell_without_a_cause_is_unexplained(tmp_path):
    causes = [{"path": "robustness/T4.1_x.csv", "row": 0, "column": "n_failed", "cause": "reestimated_chain"}]
    result = _attribution_fixture(tmp_path, cause_rows=causes)
    assert [(u["row"], u["column"]) for u in result["unexplained"]] == [(1, "rmse")]


def test_a12_a_chain_effect_outside_the_chains_exercises_is_unexplained(tmp_path):
    causes = [{"path": "robustness/T4.1_x.csv", "row": 0, "column": "n_failed", "cause": "reestimated_chain"},
              {"path": "robustness/T4.1_x.csv", "row": 1, "column": "rmse", "cause": "reestimated_chain"}]
    result = _attribution_fixture(tmp_path, cause_rows=causes)       # GDPC1 has no re-estimated chain
    assert [(u["row"], u["column"]) for u in result["unexplained"]] == [(1, "rmse")]


def test_a12_a_changed_file_outside_the_regeneration_is_unexplained(tmp_path):
    causes = [{"path": "robustness/T4.1_x.csv", "row": 0, "column": "n_failed", "cause": "reestimated_chain"},
              {"path": "robustness/T4.1_x.csv", "row": 1, "column": "rmse", "cause": "correction"}]
    result = _attribution_fixture(tmp_path, cause_rows=causes,
                                  base_extra={"figures/F3.1_X.png": b"a"},
                                  release_extra={"figures/F3.1_X.png": b"b"})
    assert any(u["path"] == "figures/F3.1_X.png" for u in result["unexplained"])


def test_a12_an_added_file_is_unexplained(tmp_path):
    causes = [{"path": "robustness/T4.1_x.csv", "row": 0, "column": "n_failed", "cause": "reestimated_chain"},
              {"path": "robustness/T4.1_x.csv", "row": 1, "column": "rmse", "cause": "correction"}]
    result = _attribution_fixture(tmp_path, cause_rows=causes, release_extra={"new.csv": b"a\n"})
    assert any(u["path"] == "new.csv" and "added" in u["reason"] for u in result["unexplained"])


# -- A13, A15, registry ---------------------------------------------------------------------

def test_a13_changed_rows_must_carry_the_dry_run_id(tmp_path):
    release = tmp_path / "release"
    _tree(release, {"t.csv": pd.DataFrame({"x": ["1", "2"], "run_id": ["dry", "old"]})})
    manifest = {"run_id": "dry", "code_commit_sha": ic.SCIENTIFIC_PIN, "config_hash": ic.CONFIG_HASH,
                "data_snapshot_hash": "d", "created_utc": "t", "code_tree_dirty": False}
    (release / "manifests").mkdir()
    (release / "manifests" / "correction_run_manifest.json").write_text(json.dumps(manifest))
    ok = val.check_provenance(release, [{"path": "t.csv", "row": 0}], "dry")
    assert ok["problems"] == []
    bad = val.check_provenance(release, [{"path": "t.csv", "row": 1}], "dry")
    assert any("without the dry-run run ID" in p for p in bad["problems"])
    manifest["code_tree_dirty"] = True
    (release / "manifests" / "correction_run_manifest.json").write_text(json.dumps(manifest))
    assert any("dirty" in p for p in val.check_provenance(release, [], "dry")["problems"])


def _plan(certs, **change):
    import r1_tierb_aggregate as agg
    plan = {**agg.aggregation_status(certs, {"problems": []}), "gates": {"problems": []}}
    plan.update(change)
    return plan


def test_a15_b2_review_items_stay_reportable_after_d1():
    certs = certificates()
    plan = _plan(certs)
    result = val.check_status(plan, certs)
    assert result["pass"] and plan["aggregation_status"] == tb.STATUS_REVIEW_REQUIRED
    assert any("T4.1:FEDFUNDS|MSAR: 14 origins classification_changed" in r for r in plan["review_items"])


@pytest.mark.parametrize("change, message", [
    ({"aggregation_status": tb.STATUS_REPRODUCED}, "does not follow"),
    ({"review_items": []}, "review items are missing"),
    ({"sensitivity_reported": []}, "sensitivities are missing"),
    ({"scientific_approval": "granted"}, "claims scientific approval")])
def test_a15_refuses_a_status_that_hides_the_review(change, message):
    certs = certificates()
    result = val.check_status(_plan(certs, **change), certs)
    assert not result["pass"] and any(message in p for p in result["detail"]["problems"])


def test_registry_rows_outside_the_patched_blocks_must_be_unchanged(tmp_path):
    base, release = tmp_path / "base", tmp_path / "release"
    rows = pd.DataFrame({"refit_date": [f"d{i}" for i in range(6)], "category": ["failed"] * 6})
    new = pd.concat([rows.iloc[:2], pd.DataFrame({"refit_date": ["n"], "category": ["fragile"]}),
                     rows.iloc[4:]], ignore_index=True)
    _tree(base, {"robustness/T4.7_failure_registry.csv": rows})
    _tree(release, {"robustness/T4.7_failure_registry.csv": new})
    report = {"t47_registry": {"T": {"published_rows": "2-3", "events_after": 1}}}
    assert val.check_registry(base, release, report) == []
    new.iloc[0, 0] = "changed"
    _tree(release, {"robustness/T4.7_failure_registry.csv": new})
    assert any("before 2 changed" in p for p in val.check_registry(base, release, report))


def test_a12_an_f2_placeholder_row_replaced_by_model_rows_is_explained(tmp_path):
    relative = "forecast_tests/T3.4_model_confidence_set.csv"
    cols = {"series": "X", "horizon": "1", "loss": "squared", "confidence_level": "0.9"}
    base = pd.DataFrame([{**cols, "model": "", "in_mcs": "False", "inference_available": "False"}])
    release = pd.DataFrame([{**cols, "model": m, "in_mcs": "True", "inference_available": "True"}
                            for m in ("AR", "MSAR")])
    for recorded, expect in (([0, 1], []), ([0], ["row added without cause"])):
        root = tmp_path / str(len(recorded))
        _tree(root / "base", {relative: base})
        _tree(root / "release", {relative: release})
        (root / "work" / "assembly" / "legacy").mkdir(parents=True)
        ic.write_rows(root / "work" / "assembly" / "reconcile_cell_causes.csv.gz",
                      [{"path": relative, "row": i, "column": "*", "cause": "correction_new_row"}
                       for i in recorded])
        ic.write_rows(root / "work" / "assembly" / "legacy" / "r1_comparison.csv",
                      [{"path": relative, "status": "identical"}])
        deps = {"dependent_files": [], "wald_rows": {"rows_changed": []},
                "t46_summary": {"rows_changed": []}, "t47_status_counts": {"rows_changed": []}}
        result = val.attribute(root / "base", root / "release", root / "work", {relative}, deps, {"rows": set()})
        reasons = sorted({u["reason"] for u in result["unexplained"]})
        if expect:
            assert "row added without cause" in reasons and "row removed without cause" in reasons
        else:
            assert reasons == []


def test_rows_appended_to_all_test_results_align_by_position(tmp_path):
    relative = "diagnostics/all_test_results.csv"
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    pd.DataFrame({"name": ["t1", "t2"], "statistic": ["1.0", "2.0"]}).to_csv(a, index=False)
    pd.DataFrame({"name": ["t1", "t2", "ZA"], "statistic": ["1.0", "2.5", "3.0"]}).to_csv(b, index=False)
    out = ic.table_cell_changes(a, b, relative)
    assert out["alignable"] and out["added_rows"] == [2]
    assert [(c["row"], c["column"]) for c in out["cells"]] == [(1, "statistic")]
