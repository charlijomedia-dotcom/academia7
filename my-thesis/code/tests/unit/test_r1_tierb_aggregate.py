"""Tier B aggregation refuses anything incomplete, contradictory or conflicting."""

from __future__ import annotations

import csv
import json
import sys
import tarfile
from pathlib import Path

import pytest

COLAB = Path(__file__).resolve().parents[3] / "colab"
sys.path.insert(0, str(COLAB))
import r1_tierb as tb  # noqa: E402
import r1_tierb_aggregate as agg  # noqa: E402


def _payload(fits: Path, key: int, value: float = 1.0) -> None:
    path = fits / f"{key % 256:02x}" / f"{key:064x}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"forecasts": {"1": value}, "status": "adequate",
                                tb.MARKER: tb.MARKER_VALUE}))


def _certify_all(drive: Path, tmp: Path, skip=None, mutate=None) -> None:
    """Commit one checkpoint per Tier B chain and a matching certificate per batch."""
    key = 0
    for batch, tasks in tb.BATCHES.items():
        chains = {}
        for task in tasks:
            local = tmp / "local" / tb.slug(task)
            key += 1
            _payload(local, key)
            manifest = tb.commit_checkpoint(local, tb.batch_root(drive, batch) / "checkpoints"
                                            / tb.slug(task), task=task, session=f"{batch}-s")
            chains[task] = {"checkpoints": [{"checkpoint_id": manifest["checkpoint_id"]}]}
        if batch == skip:
            continue
        origins = sum(tb.TIER_B_CHAINS[t][0] for t in tasks)
        cert = {"batch": batch, "complete": True, "authorized_tasks": list(tasks),
                "expected_origins": origins, "completed_origins": origins, "chains": chains,
                "provenance": {"scientific_commit": tb.SCIENTIFIC_PIN,
                               "cache_identity": tb.CACHE_IDENTITY},
                "warnings": [], "created_utc": tb.utc_stamp()}
        if mutate and batch in mutate:
            mutate[batch](cert)
        tb.write_json_atomic(tb.batch_root(drive, batch) / "certificates"
                             / f"COMPLETE-{tb.utc_stamp()}-{batch}-s.json", cert)


def test_three_consistent_batches_are_accepted(tmp_path):
    _certify_all(tmp_path / "drive", tmp_path)
    assert sorted(agg.discover(tmp_path / "drive")) == ["B1", "B2", "B3"]


def test_a_missing_batch_refuses_aggregation(tmp_path):
    _certify_all(tmp_path / "drive", tmp_path, skip="B2")
    with pytest.raises(tb.TierBError, match="B2: no completion certificate"):
        agg.discover(tmp_path / "drive")


@pytest.mark.parametrize("damage, message", [
    (lambda c: c.update(complete=False), "not complete"),
    (lambda c: c.update(completed_origins=c["expected_origins"] - 1), "origins"),
    (lambda c: c.update(authorized_tasks=c["authorized_tasks"][:-1] or ["x"]), "tasks"),
    (lambda c: c["provenance"].update(scientific_commit="0" * 40), "provenance"),
])
def test_an_invalid_certificate_refuses_aggregation(tmp_path, damage, message):
    _certify_all(tmp_path / "drive", tmp_path, mutate={"B3": damage})
    with pytest.raises(tb.TierBError, match=message):
        agg.discover(tmp_path / "drive")


def test_checkpoints_added_after_certification_refuse_aggregation(tmp_path):
    drive = tmp_path / "drive"
    _certify_all(drive, tmp_path)
    task = tb.BATCHES["B1"][0]
    local = tmp_path / "local" / tb.slug(task)
    _payload(local, 999)
    tb.commit_checkpoint(local, tb.batch_root(drive, "B1") / "checkpoints" / tb.slug(task),
                         task=task, session="later")
    with pytest.raises(tb.TierBError, match="differ from the certified"):
        agg.discover(drive)


def _tier_a_archive(tmp: Path, keys) -> Path:
    fits = tmp / "tier_a_src" / "refit_cache" / "fits"
    for key in keys:
        _payload(fits, key)
    archive = tmp / "tier_a.tar.gz"
    with tarfile.open(archive, "w:gz") as handle:
        handle.add(tmp / "tier_a_src" / "refit_cache", arcname="refit_cache")
    return archive


def test_merge_combines_tier_a_and_batches_and_refuses_conflicts(tmp_path, monkeypatch):
    drive = tmp_path / "drive"
    _certify_all(drive, tmp_path)
    monkeypatch.setattr(tb, "TIER_A_PAYLOADS", 2)
    archive = _tier_a_archive(tmp_path, [5000, 5001])
    monkeypatch.setattr(tb, "TIER_A_ARCHIVE_SHA256", "")
    report = agg.merge(drive, archive, tmp_path / "merged" / "fits")
    assert report["payloads"] == 2 + 9
    # a batch payload with the same key as a Tier A payload but other content: refused
    task = tb.BATCHES["B3"][0]
    local = tmp_path / "conflict"
    _payload(local, 5000, value=42.0)
    tb.commit_checkpoint(local, tb.batch_root(drive, "B3") / "checkpoints" / tb.slug(task),
                         task=task, session="x")
    with pytest.raises(tb.TierBError, match="conflicting"):
        agg.merge(drive, archive, tmp_path / "merged2" / "fits")


def _assembly(tmp: Path, *, estimations=None, pending=False, legacy_status=None,
              t42_differs=False) -> tuple[Path, Path, Path]:
    out = tmp / "assembly"
    sources = {"re-estimated": list(tb.TIER_A_CHAINS) + list(tb.TIER_B_CHAINS),
               "cache": [f"c{i}" for i in range(17)],
               "unavailable": [f"u{i}" for i in range(26)]}
    for name in ("legacy", "corrected"):
        tb.write_json_atomic(out / name / "r1_summary.json",
                             {"run_id": "run", "chain_sources": sources,
                              "estimations_performed": estimations or {}})
    rows = [{"path": "forecast_tests/T3.3A_hlz_pairwise.csv", "status": "identical"},
            {"path": "robustness/T4.1_transformation_robustness.csv", "status": "changed"}]
    if legacy_status:
        rows.append(legacy_status)
    (out / "legacy").mkdir(parents=True, exist_ok=True)
    with open(out / "legacy" / "r1_comparison.csv", "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "status"])
        writer.writeheader()
        writer.writerows(rows)
    release = out / "release" / "robustness"
    release.mkdir(parents=True)
    tier_a = tmp / "tier_a_release" / "robustness"
    tier_a.mkdir(parents=True)
    for name in ("T4.2_cpi_lag_robustness.csv", "T4.2_cpi_lag_predictive_tests.csv"):
        (tier_a / name).write_text("model,rmse\nAR(p=1),3.075\n")
        (release / name).write_text("model,rmse\nAR(p=1),%s\n" % ("9.9" if t42_differs else "3.075"))
    with open(release / "window_length_comparison.csv", "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["series", "correction_status"])
        writer.writeheader()
        writer.writerow({"series": "UNRATE", "correction_status":
                         agg.PENDING if pending else "recomputed_from_published"})
    unaffected = tmp / "classification.csv"
    with open(unaffected, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["task_id", "affected_by_correction"])
        writer.writeheader()
        writer.writerows({"task_id": f"u{i}", "affected_by_correction": "False"} for i in range(26))
    return out, tmp / "tier_a_release", unaffected


def test_gates_pass_a_clean_assembly(tmp_path):
    out, tier_a, unaffected = _assembly(tmp_path)
    report = agg.gates(out, tier_a, unaffected)
    assert report["problems"] == []
    assert report["legacy_differences_from_reestimated_chains"] == [
        "robustness/T4.1_transformation_robustness.csv"]


@pytest.mark.parametrize("kwargs, message", [
    ({"estimations": {"fit_msar": 3}}, "estimations performed"),
    ({"pending": True}, "pending rows remain"),
    ({"legacy_status": {"path": "forecast_tests/T3.4_model_confidence_set.csv",
                        "status": "changed"}}, "legacy reproduction failed"),
    ({"t42_differs": True}, "Tier A release"),
])
def test_gates_refuse(tmp_path, kwargs, message):
    out, tier_a, unaffected = _assembly(tmp_path, **kwargs)
    problems = agg.gates(out, tier_a, unaffected)["problems"]
    assert any(message in p for p in problems), problems
