"""Cross-validation of the Tsay (1986) test against R `TSA::Tsay.test` (decision D3).

D3 requires the quadratic Tsay test to be validated "against reference values from a
recognized implementation such as R `TSA::Tsay.test` and against simulations". This module
holds the first half; `test_nonlinearity.py` holds the simulations.

The reference values were produced by running `TSA::Tsay.test` on the series stored in
`tests/fixtures/tsay_reference_cases.json`, which are the same arrays this module feeds to
the Python implementation, so the two implementations see identical inputs to the last
bit. The R values are stored in the fixture alongside the series, with the R and TSA
versions that produced them, so this test runs in any container without needing R.

Reference environment: R 4.3.3, TSA 1.3.1 (recorded per case in the fixture).

`TSA::Tsay.test` stores its statistic and p-value rounded to four significant digits, so
four significant digits is the finest agreement that can be asserted; the comparison is
exact at R's own reported precision.

Two of the six cases are drawn from the real frozen thesis data — the INDPRO and GDPC1
growth series on their initial estimation windows — so the agreement is established on
the actual inputs the thesis uses, not only on synthetic series.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from thesis.diagnostics.nonlinearity import tsay_test

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "tsay_reference_cases.json"
SIGNIFICANT_DIGITS = 4


def _significant(value: float, digits: int = SIGNIFICANT_DIGITS) -> float:
    """Round to `digits` significant figures, the precision TSA stores."""
    if value == 0 or not np.isfinite(value):
        return float(value)
    exponent = int(np.floor(np.log10(abs(value))))
    return float(np.round(value, -(exponent - digits + 1)))


@pytest.fixture(scope="module")
def cases() -> dict:
    with FIXTURE.open(encoding="utf-8") as handle:
        return json.load(handle)


def _case_ids(cases: dict) -> list[str]:
    return sorted(cases)


class TestFixtureIntegrity:
    def test_the_fixture_exists_and_covers_both_synthetic_and_real_series(self, cases):
        assert len(cases) >= 6
        assert "indpro_growth_initial_window" in cases
        assert "gdpc1_growth_initial_window" in cases
        assert "linear_ar2" in cases
        assert "threshold_ar1" in cases

    def test_every_case_records_the_reference_implementation_and_versions(self, cases):
        for name, case in cases.items():
            reference = case["r_reference"]
            assert reference["implementation"] == "R TSA::Tsay.test", name
            assert reference["tsa_version"], name
            assert reference["r_version"].startswith("R version"), name

    def test_every_case_carries_its_series_and_order(self, cases):
        for name, case in cases.items():
            assert isinstance(case["order"], int) and case["order"] >= 1, name
            assert len(case["values"]) >= 100, name
            assert np.isfinite(np.asarray(case["values"], dtype=float)).all(), name


class TestAgreementWithR:
    @pytest.mark.parametrize("name", [
        "linear_ar2", "linear_ar4", "threshold_ar1", "quadratic_ar2",
        "indpro_growth_initial_window", "gdpc1_growth_initial_window",
    ])
    def test_the_statistic_matches_r_to_its_reported_precision(self, cases, name):
        case = cases[name]
        result = tsay_test(pd.Series(np.asarray(case["values"], dtype=float)),
                           case["order"], series=name)
        assert result.available, name
        assert _significant(result.statistic) == pytest.approx(
            case["r_reference"]["statistic"], rel=1e-12), name

    @pytest.mark.parametrize("name", [
        "linear_ar2", "linear_ar4", "threshold_ar1", "quadratic_ar2",
        "indpro_growth_initial_window", "gdpc1_growth_initial_window",
    ])
    def test_the_p_value_matches_r_to_its_reported_precision(self, cases, name):
        case = cases[name]
        result = tsay_test(pd.Series(np.asarray(case["values"], dtype=float)),
                           case["order"], series=name)
        assert _significant(result.p_value) == pytest.approx(
            case["r_reference"]["p_value"], rel=1e-12), name

    def test_agreement_holds_across_every_case_at_once(self, cases):
        # One assertion over the whole table, so a regression in any case fails here even
        # if the parametrized tests were ever narrowed.
        worst_statistic, worst_p = 0.0, 0.0
        for name, case in cases.items():
            result = tsay_test(pd.Series(np.asarray(case["values"], dtype=float)),
                               case["order"], series=name)
            reference = case["r_reference"]
            worst_statistic = max(worst_statistic, abs(
                result.statistic - reference["statistic"]) / abs(reference["statistic"]))
            worst_p = max(worst_p, abs(result.p_value - reference["p_value"]))
        # Four significant digits allows a relative error of about 5e-4 on the statistic.
        assert worst_statistic < 5e-4
        assert worst_p < 1e-3

    def test_the_decision_at_5_percent_agrees_with_r_on_every_case(self, cases):
        for name, case in cases.items():
            result = tsay_test(pd.Series(np.asarray(case["values"], dtype=float)),
                               case["order"], series=name)
            r_rejects = case["r_reference"]["p_value"] < 0.05
            assert (result.decision_5pct == "reject") is r_rejects, name

    def test_the_reference_distribution_is_reported_as_an_f(self, cases):
        for name, case in cases.items():
            result = tsay_test(pd.Series(np.asarray(case["values"], dtype=float)),
                               case["order"], series=name)
            order = case["order"]
            expected_numerator = order * (order + 1) // 2
            assert result.reference.startswith(f"F({expected_numerator},"), name
            assert result.tuning["n_quadratic_terms"] == expected_numerator, name
