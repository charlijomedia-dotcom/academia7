"""Tier B agreement (G7) and certificate status: review items are never hidden or downgraded.

Synthetic fit records and payloads; no estimation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

COLAB = Path(__file__).resolve().parents[3] / "colab"
sys.path.insert(0, str(COLAB))
import r1_tierb as tb  # noqa: E402

MSAR = {"mu1": -1.0, "mu2": 2.0, "phi1": 0.3, "sigma": 1.5,
        "p11": 0.9, "p12": 0.1, "p21": 0.2, "p22": 0.8}
ARMA = {"ar.L1": 0.4, "intercept": 1.0, "sigma2": 2.0}
DATES = ["2010-01-01", "2010-02-01", "2010-03-01"]


def _fmt(params: dict) -> str:
    return "; ".join(f"{k}={v:.10g}" for k, v in sorted(params.items()))


def _setup(tmp, model, new, original, *, drop_original=(), extra_original=()):
    """new/original: per date (status, reason_codes, loglik, params)."""
    job = SimpleNamespace(series_name="S", spec=SimpleNamespace(model=model), window_length=120)
    fits, rows, sequence = tmp / "fits", [], []
    for i, date in enumerate(DATES):
        status, codes, loglik, params = new[i]
        relative = f"{i:02x}/{i:064x}.json"
        (fits / relative).parent.mkdir(parents=True, exist_ok=True)
        (fits / relative).write_text(json.dumps({
            "status": status, "reason_codes": codes, "loglik": loglik, "params": params,
            "start_used": "warm", tb.MARKER: tb.MARKER_VALUE}))
        sequence.append((date, relative))
    for i, date in enumerate(list(DATES) + list(extra_original)):
        if date in drop_original:
            continue
        status, codes, loglik, params = original[min(i, len(original) - 1)]
        rows.append({"series": "S", "model": model, "window_start": "2000-01-01",
                     "window_end": "2009-12-01", "refit_date": pd.Timestamp(date),
                     "params": _fmt(params), "loglik": loglik, "status": status,
                     "reason_codes": ";".join(codes), "start_used": "warm"})
    return job, {"sequence": sequence}, fits, pd.DataFrame(rows)


def _agree(tmp, model, new, original, **kw):
    job, walk, fits, records = _setup(tmp, model, new, original, **kw)
    return tb.agreement("T", job, walk, fits, records)


def same(params, loglik=-100.0, status="adequate", codes=()):
    return [(status, list(codes), loglik, dict(params))] * 3


def test_identical_arma_chain_is_reproduced(tmp_path):
    a = _agree(tmp_path, "ARMA", same(ARMA), same(ARMA))
    assert a["categories"] == {"reproduced": 3}
    assert a["status"] == tb.STATUS_REPRODUCED and not a["requires_review"]


def test_rounding_of_stored_parameters_is_within_the_declared_tolerance(tmp_path):
    exact = {"ar.L1": 0.123456789012345, "intercept": 1234.56789012345, "sigma2": 2.0}
    a = _agree(tmp_path, "ARMA", same(exact), same(exact))         # stored to 10 digits
    assert a["categories"] == {"reproduced": 3} and a["param_tolerance"] == tb.PARAM_TOLERANCE


@pytest.mark.parametrize("change", ["loglik", "params"])
def test_arma_outside_tolerance_requires_review(tmp_path, change):
    new = same(ARMA, loglik=-100.0 - (1e-3 if change == "loglik" else 0))
    if change == "params":
        new = same({**ARMA, "ar.L1": ARMA["ar.L1"] + 1e-6})
    a = _agree(tmp_path, "ARMA", new, same(ARMA))
    assert a["categories"] == {"reproduction_failure": 3}
    assert a["requires_review"] and a["status"] == tb.STATUS_REVIEW_REQUIRED


@pytest.mark.parametrize("model", ["MSAR", "STAR", "ARMA"])
def test_a_changed_failure_classification_requires_review_for_every_model(tmp_path, model):
    params = {"MSAR": MSAR, "ARMA": ARMA, "STAR": {"c": 1.0, "gamma": 5.0, "phi0": 0.1}}[model]
    new = same(params)
    new[1] = ("failed", ["NONCONVERGENCE"], -100.0, dict(params))
    a = _agree(tmp_path, model, new, same(params))
    assert a["categories"]["classification_changed"] == 1
    assert a["requires_review"] and a["status"] == tb.STATUS_REVIEW_REQUIRED
    assert any("classification_changed" in r for r in a["review_items"])


def test_a_changed_reason_code_with_the_same_status_requires_review(tmp_path):
    new = same(MSAR, status="fragile", codes=["LOW_OCCUPANCY"])
    original = same(MSAR, status="fragile", codes=["LOW_OCCUPANCY", "TRANSITION_BOUNDARY"])
    a = _agree(tmp_path, "MSAR", new, original)
    assert a["categories"] == {"classification_changed": 3} and a["requires_review"]


def test_missing_and_unmatched_original_records_require_review(tmp_path):
    a = _agree(tmp_path, "STAR", same({"c": 1.0}), same({"c": 1.0}),
               drop_original=(DATES[2],), extra_original=("2011-01-01",))
    assert a["categories"]["missing_original_record"] == 1
    assert a["categories"]["original_origin_not_reestimated"] == 1
    assert a["requires_review"]


def test_parameter_name_coverage_is_validated(tmp_path):
    new = same({k: v for k, v in MSAR.items() if k != "phi1"})
    a = _agree(tmp_path, "MSAR", new, same(MSAR))
    assert a["categories"] == {"parameter_names_differ": 3} and a["requires_review"]
    assert a["rows"][0]["param_names_original_only"] == "phi1"


def test_msar_regime_label_switching_is_not_a_discrepancy(tmp_path):
    switched = {"mu1": 2.0, "mu2": -1.0, "phi1": 0.3, "sigma": 1.5,
                "p11": 0.8, "p12": 0.2, "p21": 0.1, "p22": 0.9}
    a = _agree(tmp_path, "MSAR", same(switched), same(MSAR))
    assert a["categories"] == {"reproduced_regime_labels_permuted": 3}
    assert a["status"] == tb.STATUS_REPRODUCED
    assert a["rows"][0]["regime_label_permutation"] == "mu1->mu2,mu2->mu1"
    # phi and sigma are shared: swapping them is NOT a relabelling
    wrong = {**switched, "sigma": 9.9}
    b = _agree(tmp_path / "b", "MSAR", same(wrong), same(MSAR))
    assert "reproduced_regime_labels_permuted" not in b["categories"]


def test_msar_star_optimizer_sensitivity_is_reported_not_called_an_error(tmp_path):
    new = same({**MSAR, "mu1": -1.5}, loglik=-99.0)                # another optimum
    a = _agree(tmp_path, "MSAR", new, same(MSAR))
    assert a["categories"] == {"optimizer_sensitivity": 3}
    assert not a["requires_review"] and a["status"] == tb.STATUS_WARNINGS
    assert a["sensitivity_items"] and a["first_divergence"] == DATES[0]
    assert a["rows"][0]["loglik_new_minus_original"] == pytest.approx(1.0)


def test_parameter_discrepancy_at_equal_likelihood(tmp_path):
    """Before the warm-start path diverged it is unexplained; after, flat-likelihood."""
    star = {"c": 1.0, "gamma": 50.0, "phi0": 0.1}
    new = [("adequate", [], -100.0, star),
           ("adequate", [], -100.0, {**star, "gamma": 50.5}),        # unexplained
           ("adequate", [], -100.0, {**star, "gamma": 51.0})]        # path already diverged
    a = _agree(tmp_path, "STAR", new, same(star))
    assert a["categories"] == {"reproduced": 1, "unexplained_parameter_discrepancy": 1,
                               "flat_likelihood_sensitivity": 1}
    assert a["requires_review"] and a["status"] == tb.STATUS_REVIEW_REQUIRED


# -- certificates ----------------------------------------------------------------------

def _walks(batch):
    return {t: {"planned": tb.TIER_B_CHAINS[t][0], "completed": tb.TIER_B_CHAINS[t][0],
                "complete": True, "unreachable": [],
                "statuses": {"adequate": tb.TIER_B_CHAINS[t][0] - tb.TIER_B_CHAINS[t][2],
                             "failed": tb.TIER_B_CHAINS[t][2]}}
            for t in tb.batch_tasks(batch)}


def _agreement(status=tb.STATUS_REPRODUCED, review=(), sensitivity=()):
    return {"status": status, "review_items": list(review),
            "sensitivity_items": list(sensitivity), "rows": []}


LEDGER = {"terminated": [], "interrupted": [{"session": "B2-x"}],
          "payloads_committed_by_task": {}}


def _cert(walks, agreements, batch="B2"):
    return tb.certificate(batch, walks, {}, provenance={}, sessions=LEDGER, agreement=agreements)


def test_a_complete_reproduced_batch_is_still_not_approved():
    cert = _cert(_walks("B2"), {t: _agreement() for t in tb.batch_tasks("B2")})
    assert cert["computation_status"] == "COMPUTATION_COMPLETE"
    assert cert["scientific_status"] == tb.STATUS_REPRODUCED
    assert cert["scientific_approval"] == tb.APPROVAL_NOT_GRANTED
    assert cert["sessions_interrupted"] == [{"session": "B2-x"}]


def test_a_changed_failure_count_makes_the_certificate_review_required():
    walks = _walks("B2")
    task = tb.batch_tasks("B2")[0]
    walks[task]["statuses"]["failed"] += 1
    cert = _cert(walks, {t: _agreement() for t in tb.batch_tasks("B2")})
    assert cert["complete"] and cert["scientific_status"] == tb.STATUS_REVIEW_REQUIRED
    assert cert["chains"][task]["failure_count_changed"]
    assert any(r.startswith(f"{task}: failed fits") for r in cert["review_items"])


def test_review_and_sensitivity_are_kept_apart_and_never_dropped():
    tasks = tb.batch_tasks("B2")
    agreements = {tasks[0]: _agreement(tb.STATUS_WARNINGS, sensitivity=["s"]),
                  tasks[1]: _agreement(tb.STATUS_REVIEW_REQUIRED, review=["r"])}
    cert = _cert(_walks("B2"), agreements)
    assert cert["scientific_status"] == tb.STATUS_REVIEW_REQUIRED
    assert cert["review_items"] == ["r"] and cert["sensitivity_reported"] == ["s"]
    only_sensitivity = {tasks[0]: _agreement(tb.STATUS_WARNINGS, sensitivity=["s"]),
                        tasks[1]: _agreement()}
    assert _cert(_walks("B2"), only_sensitivity)["scientific_status"] == tb.STATUS_WARNINGS


def test_no_certificate_without_an_agreement_report_for_every_chain():
    with pytest.raises(tb.TierBError, match="agreement"):
        _cert(_walks("B2"), {tb.batch_tasks("B2")[0]: _agreement()})


def test_ambiguous_original_records_are_refused_not_guessed(tmp_path):
    job, walk, fits, records = _setup(tmp_path, "ARMA", same(ARMA), same(ARMA))
    doubled = pd.concat([records, records.iloc[[0]].assign(params="ar.L1=9")])
    with pytest.raises(tb.TierBError, match="ambiguous"):
        tb.agreement("T", job, walk, fits, doubled)
    problems = tb.validate_original_records(doubled, {"T4.1:FEDFUNDS|ARMA": job},
                                            ["T4.1:FEDFUNDS|ARMA"])
    assert problems and "ambiguous" in problems[0]
    short = tb.validate_original_records(records, {"T4.1:FEDFUNDS|ARMA": job},
                                         ["T4.1:FEDFUNDS|ARMA"])
    assert short == ["T4.1:FEDFUNDS|ARMA: 3 original records (626 planned), 0 failed (6 declared)"]
