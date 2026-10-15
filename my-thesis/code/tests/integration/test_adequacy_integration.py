"""The full-sample adequacy stage must run the diagnostics it reports on.

Two integration defects motivated this module, both invisible from the estimators' own
tests because each estimator was correct in isolation and only the wiring was wrong.

1. `adequacy_stage` called `fit_msar` without `config`, and the observed-information
   Hessian, the parameter standard errors and the covariance credibility flags are all
   conditional on a configuration being supplied. The §8.1 diagnostics therefore ran on
   the rolling forecasting fits but not on the full-sample fits that feed T3.2, which is
   precisely where regime credibility is reported.

2. The F3.3 transition figure reconstructed the transition variable from `fit.y`, the
   dependent observations, instead of using `fit.z`. The reconstruction was offset into
   the wrong array and, for several (p, d) combinations, produced an array of a different
   length from G, so the plot paired mismatched observations.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import pytest

from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR, FROZEN_DIR, Namespace, output_layout
from thesis.core.provenance import RunContext
from thesis.core.schemas import ReasonCode, Status
from thesis.data.store import load_bundle
from thesis.models.star import fit_star
from thesis.pipeline import MSAR, MSAR3, STAR, Pipeline
from thesis.reporting import figures

FAST = {
    "smoke": {"enabled": True, "targets": ["INDPRO", "GDPC1"], "max_origins": 3},
    "forecasting": {"windows": {"M": 60, "Q": 40},
                    "horizons": {"primary": {"M": 1, "Q": 1},
                                 "robustness": {"M": [3], "Q": [2]}},
                    "star_multistep": {"paths": 25}},
    "specification": {"ar": {"max_lag": {"M": 3, "Q": 2}},
                      "arma": {"max_p": {"M": 1, "Q": 1}, "max_q": {"M": 1, "Q": 1}}},
    "models": {"msar": {"lag_cap": {"M": 1, "Q": 1}},
               "star": {"lag_cap": {"M": 1, "Q": 1}},
               "var": {"lags": [1]}},
    "robustness": {"window_lengths": {"lengths": {"M": [50, 60], "Q": [30, 40]},
                                      "baseline": {"M": 60, "Q": 40}},
                   "cpi_lags": {"ar_orders": [1]}},
    "evaluation": {"mcs": {"replications": 50},
                   "hlz": {"critical_value_replications": 200}},
    "execution": {"cache": False},
}


@pytest.fixture(scope="module")
def config():
    return load_config(names=("baseline", "series_catalog", "thresholds"),
                       config_dir=CONFIG_DIR)


@pytest.fixture(scope="module")
def adequacy_run(tmp_path_factory, config):
    """Run only the stages needed to reach in-sample adequacy."""
    fast = config.with_overrides(FAST, "adequacy-integration")
    bundle = load_bundle(FROZEN_DIR, fast)
    root = tmp_path_factory.mktemp("adequacy")
    layout = output_layout(Namespace.SMOKE)
    layout = type(layout)(root=root / "out", cache=root / "cache")
    layout.create()
    context = RunContext(namespace=Namespace.SMOKE, config_hash=fast.hash,
                         data_snapshot_hash=bundle.data_input_identity)
    pipeline = Pipeline(fast, context, layout, bundle, smoke=True)
    pipeline.prepare_data()
    pipeline.stationarity_stage()
    pipeline.specification_stage(final=False)
    pipeline.nonlinearity_stage()
    pipeline.specification_stage()
    pipeline.adequacy_stage()
    return pipeline, layout


class TestFullSampleMsarCredibilityDiagnostics:
    def test_the_full_sample_msar_fits_exist(self, adequacy_run):
        pipeline, _ = adequacy_run
        for series_id, fits in pipeline.full_sample_fits.items():
            assert MSAR in fits, series_id

    @pytest.mark.parametrize("model", [MSAR, MSAR3])
    def test_covariance_status_is_recorded_for_every_full_sample_fit(self, adequacy_run,
                                                                      model):
        pipeline, _ = adequacy_run
        checked = 0
        for series_id, fits in pipeline.full_sample_fits.items():
            if model not in fits:
                continue
            record = fits[model][0].record
            status = record.diagnostics.get("covariance_status")
            assert status is not None, f"{series_id} {model}: no covariance status"
            assert status != "not computed", (
                f"{series_id} {model}: the Hessian was skipped, so the §8.1 covariance "
                "diagnostics never ran on the full-sample fit")
            checked += 1
        assert checked > 0

    @pytest.mark.parametrize("model", [MSAR, MSAR3])
    def test_parameter_uncertainty_is_recorded_where_the_covariance_is_usable(
            self, adequacy_run, model):
        pipeline, _ = adequacy_run
        for series_id, fits in pipeline.full_sample_fits.items():
            if model not in fits:
                continue
            fit = fits[model][0]
            if fit.record.diagnostics.get("covariance_status") != "ok":
                continue                      # unusable covariance: disclosed, not faked
            assert fit.record.std_errors, f"{series_id} {model}"
            for name in fit.record.params:
                assert name in fit.record.std_errors, f"{series_id} {model} {name}"
            values = np.array(list(fit.record.std_errors.values()))
            assert np.isfinite(values).all()
            assert (values > 0).all()

    @pytest.mark.parametrize("model", [MSAR, MSAR3])
    def test_the_covariance_matrix_is_carried_on_the_fit(self, adequacy_run, model):
        pipeline, _ = adequacy_run
        for series_id, fits in pipeline.full_sample_fits.items():
            if model in fits:
                assert fits[model][0].covariance.size > 0, f"{series_id} {model}"

    @pytest.mark.parametrize("model", [MSAR, MSAR3])
    def test_an_unusable_covariance_produces_a_fragility_flag(self, adequacy_run, model):
        # Where the covariance is unusable the fit must carry SINGULAR_COV and be at
        # least fragile; where it is usable it must not carry that code.
        pipeline, _ = adequacy_run
        for series_id, fits in pipeline.full_sample_fits.items():
            if model not in fits:
                continue
            record = fits[model][0].record
            unusable = record.diagnostics.get("covariance_status") not in ("ok", None)
            flagged = ReasonCode.SINGULAR_COV in record.reason_codes
            assert flagged == unusable, f"{series_id} {model}"
            if flagged:
                assert record.status in (Status.FRAGILE, Status.FAILED)

    def test_the_multistart_audit_trail_is_recorded(self, adequacy_run):
        pipeline, _ = adequacy_run
        for series_id, fits in pipeline.full_sample_fits.items():
            for model in (MSAR, MSAR3):
                if model not in fits:
                    continue
                diagnostics = fits[model][0].record.diagnostics
                assert diagnostics.get("n_starts", 0) >= 1, f"{series_id} {model}"
                assert "selection_rule" in diagnostics

    def test_the_credibility_table_reports_the_status(self, adequacy_run):
        pipeline, layout = adequacy_run
        frame = pd.read_csv(layout.models / "T3.2_nonlinear_credibility.csv")
        msar_rows = frame[frame["family"] == "MSAR"]
        assert not msar_rows.empty
        assert msar_rows["status"].notna().all()

    def test_the_credibility_table_carries_the_covariance_status(self, adequacy_run):
        _, layout = adequacy_run
        frame = pd.read_csv(layout.models / "T3.2_nonlinear_credibility.csv")
        for column in ("covariance_status", "singular_covariance_flag",
                       "parameter_std_errors"):
            assert column in frame.columns, column
        assert (frame["covariance_status"] != "not computed").all(), (
            "every nonlinear fit in the credibility table must have had its "
            "observed-information matrix evaluated")

    def test_parameter_uncertainty_appears_in_the_credibility_table(self, adequacy_run):
        # Decision D8 replaced the rejected magnitude rule with reporting parameter
        # uncertainty directly, so a usable covariance must surface its standard errors.
        _, layout = adequacy_run
        frame = pd.read_csv(layout.models / "T3.2_nonlinear_credibility.csv")
        usable = frame[frame["covariance_status"] == "ok"]
        if not usable.empty:
            assert usable["parameter_std_errors"].astype(str).str.contains("=").all()

    def test_the_covariance_status_never_contradicts_the_flag(self, adequacy_run):
        # A row saying "ok" while also flagging a singular or ill-conditioned covariance
        # is self-contradictory. The status and the flag come from one classification.
        _, layout = adequacy_run
        frame = pd.read_csv(layout.models / "T3.2_nonlinear_credibility.csv")
        for row in frame.itertuples():
            status = str(row.covariance_status)
            if bool(row.singular_covariance_flag):
                assert status != "ok", f"{row.series} {row.model}: flagged but status ok"
            else:
                assert status == "ok", f"{row.series} {row.model}: unflagged but {status}"

    def test_the_singular_flag_agrees_with_the_reason_codes(self, adequacy_run):
        _, layout = adequacy_run
        frame = pd.read_csv(layout.models / "T3.2_nonlinear_credibility.csv")
        for row in frame.itertuples():
            codes = str(row.reason_codes)
            expected = ("SINGULAR_COV" in codes) or ("ILL_CONDITIONED_COV" in codes)
            assert bool(row.singular_covariance_flag) == expected, row.series


class TestStarTransitionFigureAlignment:
    @pytest.mark.parametrize("order,delay", [(1, 1), (2, 1), (1, 3), (2, 4), (4, 2),
                                             (1, 6), (3, 2)])
    def test_the_fitted_transition_variable_aligns_with_the_transition_function(
            self, config, order, delay):
        rng = np.random.default_rng(100 + order * 10 + delay)
        n = 260
        y = np.zeros(n)
        for t in range(max(order, delay), n):
            g = 1.0 / (1.0 + np.exp(-3.0 * (y[t - delay] - 0.1)))
            y[t] = 0.6 * y[t - 1] - 1.0 * g * y[t - 1] + rng.normal(0, 1.0)
        fit = fit_star(pd.Series(y), order, delay, "LSTAR", config, series="align")

        # z must be y_{t-d} on exactly the estimation rows, matching G element for element.
        start = max(order, delay)
        expected = y[np.arange(start, n) - delay]
        assert fit.z.shape == fit.G.shape
        np.testing.assert_allclose(fit.z, expected, atol=0)

    @pytest.mark.parametrize("order,delay", [(2, 1), (1, 3), (4, 2), (2, 4)])
    def test_the_old_reconstruction_from_the_dependent_variable_was_wrong(
            self, config, order, delay):
        # Pins the defect: rebuilding z from fit.y gives either the wrong length or the
        # wrong values, so the figure could not have been showing the fitted function.
        rng = np.random.default_rng(200 + order * 10 + delay)
        n = 240
        y = np.zeros(n)
        for t in range(max(order, delay), n):
            g = 1.0 / (1.0 + np.exp(-2.5 * y[t - delay]))
            y[t] = 0.5 * y[t - 1] - 0.9 * g * y[t - 1] + rng.normal(0, 1.0)
        fit = fit_star(pd.Series(y), order, delay, "LSTAR", config, series="align")
        reconstructed = fit.y[max(fit.order, fit.delay) - fit.delay:][: fit.G.size]
        assert (reconstructed.shape != fit.z.shape
                or not np.allclose(reconstructed, fit.z))

    @pytest.mark.parametrize("order,delay", [(1, 1), (2, 4), (3, 2)])
    def test_the_transition_function_is_reproduced_from_the_stored_z(self, config,
                                                                      order, delay):
        # The strongest alignment check: recomputing the transition function from the
        # stored z and the estimated parameters must return G exactly.
        from thesis.models.star import transition

        rng = np.random.default_rng(300 + order * 10 + delay)
        n = 260
        y = np.zeros(n)
        for t in range(max(order, delay), n):
            g = 1.0 / (1.0 + np.exp(-3.0 * (y[t - delay] - 0.2)))
            y[t] = 0.6 * y[t - 1] - 1.1 * g * y[t - 1] + rng.normal(0, 1.0)
        fit = fit_star(pd.Series(y), order, delay, "LSTAR", config, series="align")
        recomputed = transition(fit.z, fit.gamma, fit.c, fit.scale, fit.kind)
        np.testing.assert_allclose(recomputed, fit.G, atol=1e-12)

    def test_the_figure_refuses_misaligned_inputs(self):
        with pytest.raises(ValueError, match="align"):
            figures.star_transition(np.arange(5.0), np.arange(6.0),
                                    series_id="x", kind="LSTAR", gamma=1.0, c=0.0)

    def test_the_figure_plots_the_fitted_pairs(self, config):
        fit = fit_star(pd.Series(_lstar_series(240, 2, 3, seed=7)), 2, 3, "LSTAR",
                       config, series="plot")
        figure = figures.star_transition(fit.z, fit.G, series_id="plot", kind=fit.kind,
                                         gamma=fit.gamma, c=fit.c)
        line = figure.axes[0].lines[0]
        plotted = np.column_stack([line.get_xdata(), line.get_ydata()])
        fitted = np.column_stack([fit.z, fit.G])
        # Same set of (z, G) pairs, in sorted order.
        np.testing.assert_allclose(plotted[np.argsort(plotted[:, 0])],
                                   fitted[np.argsort(fitted[:, 0])], atol=1e-12)
        import matplotlib.pyplot as plt
        plt.close(figure)


def _lstar_series(n: int, order: int, delay: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    y = np.zeros(n)
    for t in range(max(order, delay), n):
        g = 1.0 / (1.0 + np.exp(-3.0 * (y[t - delay] - 0.1)))
        y[t] = 0.6 * y[t - 1] - 1.0 * g * y[t - 1] + rng.normal(0, 1.0)
    return y
