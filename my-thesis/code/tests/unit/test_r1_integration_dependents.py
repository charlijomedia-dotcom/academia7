"""Stage 3 of the integration dry run: dependent outputs, each reproduced from the base first."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "colab"))
pytest.importorskip("thesis")
import r1_integration_common as ic  # noqa: E402
import r1_integration_dependents as dep  # noqa: E402

PUBLISHED = ROOT / "output"
STAMP = {"run_id": "dry", "data_snapshot_hash": "d", "code_commit_sha": ic.SCIENTIFIC_PIN,
         "config_hash": "c", "created_utc": "t"}


def _copy(files: list[str], *roots: Path) -> None:
    for root in roots:
        for relative in files:
            (root / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(PUBLISHED / relative, root / relative)


def test_record_agreement_rule():
    old = {"status": "fragile", "reason_codes": "LOW_OCCUPANCY", "params": '{"mu1": 1.0, "mu2": 2.0}',
           "loglik": -10.0}
    same = dict(old)
    permuted = {**old, "params": '{"mu1": 2.0, "mu2": 1.0}'}
    other_status = {**old, "status": "failed"}
    other_optimum = {**old, "loglik": -9.0, "params": '{"mu1": 1.5, "mu2": 2.0}'}
    assert dep.record_reproduced(same, old, "MSAR") == (True, "reproduced")
    assert dep.record_reproduced(permuted, old, "MSAR") == (True, "reproduced")
    assert dep.record_reproduced(other_status, old, "MSAR") == (False, "classification_changed")
    assert dep.record_reproduced(other_optimum, old, "MSAR") == (False, "optimizer_sensitivity")
    assert dep.record_reproduced(other_optimum, old, "ARMA") == (False, "reproduction_failure")


def test_status_counts_are_reproduced_before_they_are_changed(tmp_path):
    base, release = tmp_path / "base", tmp_path / "release"
    for root in (base, release):
        (root / "robustness").mkdir(parents=True)
    counts = pd.DataFrame({"series": ["X", "X"], "model": ["MSAR"] * 2, "status": ["failed", "fragile"],
                           "n": ["2", "1"], "run_id": ["b", "b"]})
    counts.to_csv(base / "robustness" / "T4.7_status_counts.csv", index=False)
    records = pd.DataFrame({"series": ["X"] * 3, "model": ["MSAR"] * 3,
                            "status": ["failed", "failed", "fragile"]})
    final = records.assign(status=["failed", "fragile", "fragile"])
    out = dep.patch_status_counts(base, release, {"base_typed": records, "final_typed": final},
                                  dep.Stamp(STAMP))
    assert [(c["status"], c["before"], c["after"]) for c in out["rows_changed"]] == \
        [("failed", "2", "1"), ("fragile", "1", "2")]
    written = pd.read_csv(release / "robustness" / "T4.7_status_counts.csv", dtype=str)
    assert written["run_id"].tolist() == ["dry", "dry"]
    with pytest.raises(ic.IntegrationError, match="does not reproduce"):
        dep.patch_status_counts(base, release, {"base_typed": final, "final_typed": final},
                                dep.Stamp(STAMP))


def test_wald_rows_are_rebuilt_from_the_release_t35(tmp_path):
    files = ["diagnostics/all_test_results.csv", "forecast_tests/T3.5_state_loss_regression.csv"]
    base, release = tmp_path / "base", tmp_path / "release"
    _copy(files, base, release)
    assert dep.rebuild_wald(base, release, dep.Stamp(STAMP))["rows_changed"] == []
    t35 = pd.read_csv(release / files[1], dtype=str, keep_default_na=False)
    row = t35.index[(t35["series"] == "UNRATE") & (t35["model"] == "MSAR vs AR")][0]
    t35.at[row, "joint_wald_statistic"], t35.at[row, "joint_wald_p"] = "25.0", "0.001"
    t35.to_csv(release / files[1], index=False)
    shutil.copy2(base / files[0], release / files[0])
    changed = dep.rebuild_wald(base, release, dep.Stamp(STAMP))["rows_changed"]
    assert len(changed) == 1 and changed[0]["series"] == "UNRATE"
    assert set(changed[0]["columns"]) >= {"statistic", "p_value"}
    tests = pd.read_csv(release / files[0], dtype=str, keep_default_na=False)
    assert tests.at[changed[0]["row"], "decision_5pct"] == "reject"
    assert tests.at[changed[0]["row"], "run_id"] == "dry"


def test_wald_rebuild_refuses_a_base_it_cannot_reproduce(tmp_path):
    files = ["diagnostics/all_test_results.csv", "forecast_tests/T3.5_state_loss_regression.csv"]
    base, release = tmp_path / "base", tmp_path / "release"
    _copy(files, base, release)
    t35 = pd.read_csv(base / files[1], dtype=str, keep_default_na=False)
    t35.loc[(t35["series"] == "GDPC1") & (t35["model"] == "MSAR vs AR"), "slopes_wald_statistic"] = "99.0"
    t35.to_csv(base / files[1], index=False)
    with pytest.raises(ic.IntegrationError, match="not reproduced from the base"):
        dep.rebuild_wald(base, release, dep.Stamp(STAMP))


def test_t46_summary_follows_the_release_arma_forecasts(tmp_path):
    files = ["robustness/T4.6_arma_garch_summary.csv", "robustness/T4.6_arma_garch_CPIAUCSL.csv",
             "forecasts/forecasts_CPIAUCSL.csv"]
    base, release = tmp_path / "base", tmp_path / "release"
    _copy(files, base, release)
    assert dep.patch_t46(base, release, dep.Stamp(STAMP))["rows_changed"] == []
    forecasts = pd.read_csv(release / files[2], dtype=str, keep_default_na=False)
    first = forecasts.index[(forecasts["model"] == "ARMA") & (forecasts["horizon"] == "1")][0]
    forecasts.at[first, "forecast"] = ""                    # e.g. masked by F1
    forecasts.to_csv(release / files[2], index=False)
    changed = dep.patch_t46(base, release, dep.Stamp(STAMP))["rows_changed"]
    assert changed and changed[0]["series"] == "CPIAUCSL" and "n_common" in changed[0]["columns"]


def test_f48_is_re_rendered_exactly_when_its_plotted_inputs_change(tmp_path):
    from thesis.core.config import load_config
    from thesis.core.paths import CONFIG_DIR
    config = load_config(names=("baseline", "series_catalog", "thresholds"), config_dir=CONFIG_DIR)
    figures = [f"figures/F4.8_{s}.{e}{x}" for s in ("CPIAUCSL", "FEDFUNDS", "GDPC1", "INDPRO", "M2SL",
                                                   "UNRATE") for e in ("png", "pdf")
               for x in ("", ".provenance.json")]
    files = ["robustness/window_length_comparison.csv"] + figures
    base, release = tmp_path / "base", tmp_path / "release"
    _copy(files, base, release)
    report = dep.patch_f48(base, release, tmp_path / "scratch", config, dep.Stamp(STAMP))
    assert report["re_rendered"] == [] and all(all(v.values()) for v in report["reproduced_from_base"].values())
    table = pd.read_csv(release / files[0], dtype=str, keep_default_na=False)
    row = table.index[(table["series"] == "GDPC1") & (table["horizon"] == "1") & (table["model"] == "MSAR")][0]
    table.at[row, "oos_r2_vs_benchmark"] = "0.5"
    table.at[table.index[(table["series"] == "INDPRO")][0], "rmse"] = "9.9"   # not plotted
    table.to_csv(release / files[0], index=False)
    report = dep.patch_f48(base, release, tmp_path / "scratch", config, dep.Stamp(STAMP))
    assert report["inputs_changed"] == ["GDPC1"]
    assert sorted(report["re_rendered"]) == ["F4.8_GDPC1.pdf", "F4.8_GDPC1.png"]
    assert (release / "figures" / "F4.8_GDPC1.png").read_bytes() != (base / "figures" / "F4.8_GDPC1.png").read_bytes()
    assert (release / "figures" / "F4.8_INDPRO.png").read_bytes() == (base / "figures" / "F4.8_INDPRO.png").read_bytes()


class _Job:
    def __init__(self, series="X", model="AR", task="T4.2:X|AR(p=3)"):
        self.series_name, self.task_id = series, task
        self.spec = type("Spec", (), {"model": model})()
        self.window_length, self.frequency = 240, "M"


def _records(label, dates, loglik=1.0, status="adequate"):
    return pd.DataFrame({"series": "X", "model": "AR", "spec_label": label,
                         "refit_date": pd.to_datetime(dates), "window_start": pd.to_datetime("1990-01-01"),
                         "window_end": pd.to_datetime("2009-06-01"), "status": status, "reason_codes": "",
                         "params": '{"phi1": 0.5}', "loglik": loglik})


def test_blocks_are_located_by_specification_and_refit_dates(monkeypatch):
    import r1_original_cache_audit as audit
    monkeypatch.setattr(audit, "stage_block", lambda frame, job: (None, "no span match"))
    dates = ["2000-01-01", "2000-02-01", "2000-03-01"]
    published = pd.concat([_records("p=1", dates), _records("p=3", dates, loglik=2.0),
                           _records("p=3", dates[:2])], ignore_index=True)
    block, how = dep.locate_block(published, _Job(), _records("p=3", dates, loglik=2.0), "AR")
    assert sorted(r.Index for r in block.values()) == [3, 4, 5] and "specification" in how
    with pytest.raises(ic.IntegrationError, match="no published block"):
        dep.locate_block(published, _Job(), _records("p=6", dates), "AR")
    with pytest.raises(ic.IntegrationError, match="no published block"):      # already assigned
        dep.locate_block(published, _Job(), _records("p=3", dates, loglik=2.0), "AR", used={3, 4, 5})


def test_duplicate_blocks_are_accepted_only_when_every_record_reproduces(monkeypatch):
    import r1_original_cache_audit as audit
    monkeypatch.setattr(audit, "stage_block", lambda frame, job: (None, "no span match"))
    dates = ["2000-01-01", "2000-02-01"]
    twins = pd.concat([_records("p=3", dates), _records("p=3", dates)], ignore_index=True)
    block, how = dep.locate_block(twins, _Job(), _records("p=3", dates), "AR")
    assert sorted(r.Index for r in block.values()) == [2, 3] and "none replaced" in how
    with pytest.raises(ic.IntegrationError, match="ambiguous"):
        dep.locate_block(twins, _Job(), _records("p=3", dates, status="failed"), "AR")
