"""Integrated-candidate numbers used in the Part 8 report drafts (read only; no estimation).

    python integration_numbers.py EXPORT_DIR CLAIMS_REFERENCE_DIR OUT_DIR [LOCAL_REHEARSAL_RELEASE]

1. Rebuilds every CSV the integration changed: the claims-reference release (0573a8c, which
   already carries F1-F4 and F7.1) plus every changed cell exported by the audited session
   (cells_vs_claims_reference.csv.gz). Unchanged files are the claims-reference files.
2. Optionally cross-checks each rebuilt table against a local rehearsal release, for the
   tables that do not depend on the Drive-only chains (every non-provenance cell, rel. tol. 1e-9).
3. Writes integrated_numbers.json: every number quoted from the integrated candidate in the
   drafts, with its source table.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

EXPORT, REF, OUT = (Path(a) for a in sys.argv[1:4])
LOCAL = Path(sys.argv[4]) if len(sys.argv) > 4 else None
TREE = OUT / "integrated_tables"
PROV = {"run_id", "data_snapshot_hash", "code_commit_sha", "config_hash", "created_utc",
        "correction_status", "wall_seconds", "cpu_seconds", "peak_memory_mb", "recorded_utc"}

cells = pd.read_csv(EXPORT / "cells_vs_claims_reference.csv.gz", dtype=str, keep_default_na=False)
check = {}
for path in sorted(p for p in set(cells.path) if p.endswith(".csv")):
    table = pd.read_csv(REF / path, dtype=str, keep_default_na=False)
    sub = cells[cells.path == path]
    if (sub.row.astype(int) >= len(table)).any() or set(sub.column) - set(table.columns):
        raise SystemExit(f"{path}: a changed cell lies outside the reference table")
    for _, c in sub.iterrows():
        table.at[int(c.row), c.column] = c.new
    (TREE / path).parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(TREE / path, index=False)
    if LOCAL is not None and (LOCAL / path).exists():
        loc = pd.read_csv(LOCAL / path, dtype=str, keep_default_na=False)
        if len(loc) != len(table):
            check[path] = "row count differs"
            continue
        bad = 0
        for col in (c for c in table.columns if c not in PROV and c in loc.columns):
            a, b = pd.to_numeric(table[col], errors="coerce"), pd.to_numeric(loc[col], errors="coerce")
            num = a.notna() & b.notna()
            bad += int((((~num) & (table[col] != loc[col])) |
                        (num & ((a - b).abs() > 1e-9 * b.abs().clip(lower=1)))).sum())
        check[path] = bad


def T(path: str) -> pd.DataFrame:
    return pd.read_csv(TREE / path if (TREE / path).exists() else REF / path, low_memory=False)


def r(x, d=3):
    return None if pd.isna(x) else round(float(x), d)


N: dict = {}
# -- T3.3 baseline -----------------------------------------------------------------------
t33 = T("forecast_tests/T3.3_main_forecast_table.csv")
N["T3.3_h1"] = {f"{s}|{m}": {"rmse": r(x.rmse, 4), "oos_r2": r(x.oos_r2_vs_benchmark, 4),
                             "rank_rmse": r(x.rank_rmse, 0), "n_valid": int(x.n_valid),
                             "n_failed": int(x.n_failed), "n_fragile": int(x.n_fragile),
                             "hlz_sq_p": r(x.hlz_squared_p_value, 4), "hlz_abs_p": r(x.hlz_absolute_p_value, 4)}
                for (s, m), x in t33[t33.horizon == 1].set_index(["series", "model"]).iterrows()}
un = t33[t33.series == "UNRATE"]
N["T3.3_UNRATE_multistep"] = {f"h{int(x.horizon)}|{x.model}": {
    "rmse": r(x.rmse, 3), "oos_r2": r(x.oos_r2_vs_benchmark, 3), "rank_rmse": r(x.rank_rmse, 0),
    "rank_mae": r(x.rank_mae, 0)} for _, x in un.iterrows()}
N["baseline_failed_fits_h1"] = {f"{s}|{m}": int(v) for (s, m), v in
                                t33[(t33.horizon == 1) & (t33.n_failed > 0)].set_index(["series", "model"]).n_failed.items()}
N["baseline_failed_fits_h1_total"] = int(t33[t33.horizon == 1].n_failed.sum())

# -- pairwise tests ---------------------------------------------------------------------
hlz = T("forecast_tests/T3.3A_hlz_pairwise.csv")
dm = T("forecast_tests/T3.3B_dm_hln_pairwise.csv")
avail = hlz[hlz.decision_5pct.isin(["reject", "do not reject"])]
N["T3.3A_rejections"] = {"available": int(len(avail)), "reject": int((avail.decision_5pct == "reject").sum())}
rej = avail[avail.decision_5pct == "reject"]
N["T3.3A_reject_rows"] = [f"{x.series} h{x.horizon} {x.loss} {x.benchmark}-{x.competitor} p={x.p_value_two_sided}"
                          for _, x in rej.iterrows()]
N["T3.3A_reject_by_series"] = rej.series.value_counts().to_dict()
N["T3.3B_disagreements"] = int((dm.agrees_with_hlz == "disagree").sum())
star = hlz[(hlz.competitor == "STAR") | (hlz.benchmark == "STAR")]
N["A4_star_clustering"] = {"in_[0.30,0.34]": int(((star.p_value_two_sided > 0.30) & (star.p_value_two_sided < 0.34)).sum()),
                           "available": int(star.p_value_two_sided.notna().sum())}

# -- MCS ---------------------------------------------------------------------------------
mcs = T("forecast_tests/T3.4_model_confidence_set.csv")
h1 = mcs[mcs.horizon == 1]
N["T3.4_h1_unavailable_cells"] = int(h1[~h1.inference_available.astype(str).isin(["True", "true"])]
                                     .groupby(["series", "loss", "confidence_level"]).ngroups)
N["T3.4_h1_excluded"] = [f"{x.series} {x.loss} {x.confidence_level} {x.model} p={x.mcs_p_value}"
                         for _, x in h1[h1.in_mcs.astype(str).isin(["False", "false"])].iterrows()]
N["T3.4_unavailable_cells_all"] = int(mcs[~mcs.inference_available.astype(str).isin(["True", "true"])]
                                      .groupby(["series", "horizon", "loss", "confidence_level"]).ngroups)
N["T3.4_cells_all"] = int(mcs.groupby(["series", "horizon", "loss", "confidence_level"]).ngroups)

# -- state dependence ---------------------------------------------------------------------
sr = T("forecast_tests/T3.5_state_loss_regression.csv")
ok = sr[sr.inference_available.astype(str).isin(["True", "true"])]
N["T3.5R_estimable"] = f"{len(ok)} of {len(sr)}"
N["T3.5R_joint_reject"] = [f"{x.series} {x.model} h{x.horizon} joint p={r(x.joint_wald_p, 4)} slopes p={r(x.slopes_wald_p, 3)}"
                           for _, x in ok[ok.joint_wald_p < 0.05].iterrows()]
N["T3.5R_slopes_reject"] = [f"{x.series} {x.model} h{x.horizon} slopes p={r(x.slopes_wald_p, 3)}"
                            for _, x in ok[ok.slopes_wald_p < 0.05].iterrows()]
N["T3.5R_beta_turn_5pct"] = [f"{x.series} {x.model} h{x.horizon} p={r(x.beta_turn_p, 3)}"
                             for _, x in ok[ok.beta_turn_p < 0.05].iterrows()]
N["T3.5R_beta_rec_5pct"] = [f"{x.series} {x.model} h{x.horizon} p={r(x.beta_rec_p, 3)}"
                            for _, x in ok[ok.beta_rec_p < 0.05].iterrows()]
ua = sr[(sr.series == "UNRATE") & (sr.model == "ARMA vs AR") & (sr.horizon == 1)].iloc[0]
N["UNRATE_ARMA_AR_h1_wald"] = {"joint_stat": r(ua.joint_wald_statistic, 2), "joint_p": r(ua.joint_wald_p, 3),
                               "slopes_stat": r(ua.slopes_wald_statistic, 2), "slopes_p": r(ua.slopes_wald_p, 3),
                               "alpha": r(ua.alpha, 3), "alpha_p": r(ua.alpha_p, 3),
                               "beta_rec": r(ua.beta_rec, 3), "beta_rec_p": r(ua.beta_rec_p, 3),
                               "beta_turn": r(ua.beta_turn, 4), "beta_turn_p": r(ua.beta_turn_p, 3),
                               "n": int(ua.n), "n_recession": int(ua.n_recession), "n_turning_window": int(ua.n_turning_window)}
tp = T("robustness/T4.TP1_turning_window_sensitivity.csv")
N["TP1"] = {"rows": int(len(tp)),
            "alternative_support_5pct_true": int(tp.alternative_support_5pct.astype(str).isin(["True", "true"]).sum())
            if "alternative_support_5pct" in tp else None,
            "conclusion_vs_baseline": tp.conclusion_vs_baseline.value_counts().to_dict()
            if "conclusion_vs_baseline" in tp else None}

# -- fit records and registry --------------------------------------------------------------
fr = T("models/fit_records.csv")
fam = fr.model.astype(str).str.replace(r"\(.*\)", "", regex=True)
N["FR_status_by_model"] = {m: g.status.value_counts().to_dict() for m, g in fr.assign(fam=fam).groupby("fam")}
N["FR_status_total"] = fr.status.value_counts().to_dict()
N["FR_rows"] = int(len(fr))
failed = fr[fr.status == "failed"]
N["FR_failed_by_series_model"] = {f"{s}|{m}": int(v) for (s, m), v in failed.groupby(["series", "model"]).size().items()}
sc = T("robustness/T4.7_status_counts.csv")
N["T4.7_status_counts_changed_rows"] = sc[(sc.series.isin(["FEDFUNDS", "UNRATE"])) & (sc.model == "MSAR")].to_dict("records")

# -- robustness tables ---------------------------------------------------------------------
t41 = T("robustness/T4.1_transformation_robustness.csv")
N["T4.1"] = {f"{x.series}|{x.transformation}|{x.role}|{x.model}": {"rmse": r(x.rmse, 3), "oos_r2": r(x.oos_r2_vs_benchmark, 3),
             "n_valid": None if pd.isna(x.n_valid) else int(x.n_valid), "n_failed": None if pd.isna(x.n_failed) else int(x.n_failed),
             "rank_rmse": r(x.rank_rmse, 0), "rank_mae": r(x.rank_mae, 0)}
             for _, x in t41[t41.role.isin(["baseline", "alternative"])].iterrows()}
t41p = T("robustness/T4.1_transformation_predictive_tests.csv")
N["T4.1P"] = [f"{x.series} {x.model} {x.transformation} {x.loss}: HLZ p={x.hlz_p_value_two_sided} ({x.hlz_decision_5pct}); "
              f"DM-HLN p={r(x.dm_hln_p_value, 4)} ({x.dm_hln_decision_5pct}); d={r(x.mean_loss_differential, 5)}"
              for _, x in t41p.iterrows()]
t42 = T("robustness/T4.2_cpi_lag_robustness.csv")
N["T4.2"] = {x.model: {"rmse": r(x.rmse, 3), "mae": r(x.mae, 3), "oos_r2": r(x.oos_r2_vs_benchmark, 3),
                       "common_dates": int(x.common_dates)} for _, x in t42.iterrows()}
t42p = T("robustness/T4.2_cpi_lag_predictive_tests.csv")
N["T4.2P"] = {f"{x.model}|{x.loss}": {"hlz_p": r(x.hlz_p_value_two_sided, 4), "dm_p": r(x.dm_hln_p_value, 4),
                                     "hlz": x.hlz_decision_5pct, "dm": x.dm_hln_decision_5pct} for _, x in t42p.iterrows()}
t44p = T("robustness/T4.4_horizon_predictive_tests.csv")
rej44 = t44p[t44p.hlz_decision_5pct == "reject"]
N["T4.4P"] = {"tests": int(len(t44p)), "hlz_reject": int(len(rej44)),
              "rows": [f"{x.series} {x.model} h{x.horizon} {x.loss} p={x.hlz_p_value_two_sided} d={r(x.mean_loss_differential, 4)}"
                       for _, x in rej44.iterrows()]}
t45 = T("robustness/T4.5_var_comparison.csv")
N["T4.5C_VAR"] = {x.series: {"rmse": r(x.rmse, 3), "oos_r2": r(x.oos_r2_vs_benchmark, 3), "rank": r(x.rank_rmse, 0),
                             "common_dates": None if "common_dates" not in t45 or pd.isna(x.common_dates) else int(x.common_dates)}
                  for _, x in t45[t45.model == "VAR"].iterrows()}
N["T4.5C_AR"] = {x.series: r(x.rmse, 3) for _, x in t45[t45.model == "AR"].iterrows()}
N["T4.5C_UNRATE"] = {x.model: {"rmse": r(x.rmse, 3), "rank_rmse": r(x.rank_rmse, 0)} for _, x in t45[t45.series == "UNRATE"].iterrows()}
t45p = T("robustness/T4.5_var_predictive_tests.csv")
N["T4.5P_reject"] = [f"{x.series} {x.model} {x.loss} HLZ p={x.hlz_p_value_two_sided} d={r(x.mean_loss_differential, 4)}"
                     for _, x in t45p[t45p.hlz_decision_5pct == "reject"].iterrows()]
N["T4.5P_UNRATE_VAR"] = [f"{x.loss} HLZ p={x.hlz_p_value_two_sided}" for _, x in
                         t45p[(t45p.series == "UNRATE") & (t45p.model == "VAR")].iterrows()]
wl = T("robustness/window_length_comparison.csv")
N["T4.8C_h1_oos_r2"] = {f"{x.series}|{x.model}|{int(x.window_length)}": r(x.oos_r2_vs_benchmark, 3)
                        for _, x in wl[wl.horizon == 1].iterrows()}
N["T4.8C_h1_rank_rmse_UNRATE"] = {f"{x.model}|{int(x.window_length)}": r(x.rank_rmse, 0)
                                  for _, x in wl[(wl.horizon == 1) & (wl.series == "UNRATE")].iterrows()}
wlp = T("robustness/window_length_predictive_tests.csv")
N["T4.8P"] = {"tests": int(len(wlp)), "conclusion_vs_baseline": wlp.conclusion_vs_baseline.value_counts().to_dict(),
              "support_change": wlp.support_change.value_counts().to_dict(),
              "hlz_reject": [f"{x.series} {x.model} {int(x.window_length)} {x.loss} p={x.hlz_p_value_two_sided} d={r(x.mean_loss_differential, 5)}"
                             for _, x in wlp[wlp.hlz_decision_5pct == "reject"].iterrows()],
              "UNRATE_MSAR": [f"{int(x.window_length)} {x.loss} HLZ p={x.hlz_p_value_two_sided}" for _, x in
                              wlp[(wlp.series == "UNRATE") & (wlp.model == "MSAR")].iterrows()]}
wlm = T("robustness/window_length_mcs.csv")
N["T4.8M"] = {"cells": int(wlm.groupby([c for c in ("series", "window_length", "loss", "confidence_level") if c in wlm]).ngroups),
              "unavailable_cells": int(wlm[~wlm.inference_available.astype(str).isin(["True", "true"])]
                                       .groupby([c for c in ("series", "window_length", "loss", "confidence_level") if c in wlm]).ngroups)}
t49 = T("data_audit/T4.9_locf_sample_comparison.csv")
N["T4.9"] = {f"{x.series}|{x.model}|{x['sample']}": {"rmse": r(x.rmse, 4), "oos_r2": r(x.oos_r2_vs_benchmark, 4),
                                                     "rank_rmse": r(x.rank_rmse, 0)}
             for _, x in t49[t49.series.isin(["UNRATE", "CPIAUCSL"])].iterrows()}

# -- audit A3 (UNRATE) on the integrated forecasts -----------------------------------------
fc = T("forecasts/forecasts_UNRATE.csv")
fc = fc[(fc.horizon == 1) & (fc.status != "failed")]
wide = fc.pivot_table(index="target_date", columns="model", values="error")
A3 = {}
for model in ("ARMA", "MSAR", "STAR"):
    pair = wide[["AR", model]].dropna()
    covid = (pair.index >= "2020-01-01") & (pair.index <= "2021-06-01")
    A3[model] = {"oos_r2_all": r(1 - (pair[model] ** 2).sum() / (pair.AR ** 2).sum(), 3),
                 "oos_r2_excl_2020_01_2021_06": r(1 - (pair[model][~covid] ** 2).sum() / (pair.AR[~covid] ** 2).sum(), 3),
                 "n_excluded": int(covid.sum())}
N["A3_UNRATE_h1_integrated"] = A3
common = wide.dropna()
N["UNRATE_h1_common_all_four"] = {"n": int(len(common)),
                                  **{m: r(np.sqrt((common[m] ** 2).mean()), 6) for m in ("AR", "ARMA", "MSAR", "STAR")}}

# -- Zivot-Andrews (F4) ---------------------------------------------------------------------
t22 = T("diagnostics/T2.2_stationarity.csv")
za = t22[t22.astype(str).apply(lambda c: c.str.contains("Zivot", case=False)).any(axis=1)]
N["T2.2_zivot_andrews"] = za.drop(columns=[c for c in za.columns if c in PROV]).to_dict("records")

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "integrated_numbers.json").write_text(json.dumps(N, indent=1, default=str))
(OUT / "rebuild_crosscheck_vs_local_rehearsal.json").write_text(json.dumps(check, indent=1))
print(json.dumps({"tables_rebuilt": len(list(TREE.rglob("*.csv"))), "crosscheck": check}, indent=1))
