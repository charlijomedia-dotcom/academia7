# Part 8 — Robustness findings

> **Correction phase (2 November 2026).** This report audits the **original publication**: results commit `066294544e8f`, run `baseline-20261030T173044-949fcd76`. Every number cited from `output/` refers to that publication.
>
> - Corrections F1 (failed-forecast scoring), F2 (guarded MCS), F3 (pairwise sign convention) and F4 (Zivot–Andrews reporting) are implemented and tested on branch `part8-corrections`. They have **not** yet been applied to `output/`.
> - Findings that depend on affected tables are **provisional**; see `corrections/correction_plan.md` and the `provisional` column of `claim_evidence_matrix_adjudicated.csv`.
> - A corrected publication will be released separately, with its own run ID and manifests. It will not overwrite the original results commit.


**Run:** `baseline-20261030T173044-949fcd76` · **Results commit** `0662945` · **Code** `46a53181e5e9`

**Paths.** All paths below are relative to `output/`. The source keys are defined in `full_empirical_analysis_report.md` §0.

**Labels**

- Every result here is a **robustness** or **diagnostic** result unless marked otherwise. No robustness result replaces the baseline (CLAUDE.md §5).
- **⚠F1** marks rows affected by the failed-forecast scoring defect, documented in `notes/claude/part8_audit_findings_and_correction_proposals_2026-11-01.md`. Those rows are provisional until the evaluation is regenerated.

**Sign conventions.** In T4.1P, T4.2P, T4.4P, T4.5P and T4.8P, the stored `mean_loss_differential` is competitor minus benchmark, so a negative value favours the competitor. This is the correct orientation; only T3.3A/T3.3B carry the reversed label (F3).

---

## T4.1 — Alternative transformations

**Context**

- Responds to P-02 and P-03.
- Threat: the level/difference choice drives the ranking.
- Baseline rule (T2.2D):
  - UNRATE is kept in levels (branch 1): on the initial window ADF rejects (p = 0.025) and KPSS does not (p ≥ 0.10).
  - FEDFUNDS is differenced (branch 2): ADF p = 0.953 and KPSS p ≤ 0.01.
  - The full sample agrees for both (`full_sample_agrees = True`).
- The alternative transformation is still run, as §3.4 requires.

**Accuracy at h=1** (T4.1; `role = alternative` rows; RMSE in each model's own units; OOS R² against AR on common dates)

| Target, transformation | AR | ARMA | MSAR | STAR |
|---|---|---|---|---|
| UNRATE, levels (baseline) ⚠F1 | 0.886 | 0.737 (R² 0.323) | 0.492 (0.690) | 0.592 (0.554) |
| UNRATE, differences (alt) ⚠F1 | 0.935 | 0.680 (0.365) | 0.776 (0.311) | 20.75 (−491.1) |
| FEDFUNDS, differences (baseline) | 0.475 | 0.477 (0.000) | 0.480 (−0.019) | 0.613 (−0.661) |
| FEDFUNDS, levels (alt) ⚠F1 | 0.527 | 0.520 (0.033) | 0.442 (−0.273, n=574) | 0.974 (−2.418) |

**Inference** (T4.1P, alternative transformation only)

- None of the 12 HLZ tests rejects at 5%.
- The closest are FEDFUNDS-level ARMA versus AR, with p = 0.081 (squared) and 0.084 (absolute), and FEDFUNDS-level STAR versus AR, absolute p = 0.097 (STAR worse).
- DM-HLN rejects once: FEDFUNDS-level ARMA, absolute p = 0.017. HLZ governs.

**Failures and fragility**

- In the FEDFUNDS level alternative:
  - AR is `UNSTABLE_AR` at 71 origins, a near-unit root;
  - MSAR fails to converge at 52 of 626 origins (T4.1, FR).
- MSAR's RMSE of 0.442 is computed on its 574 valid dates. On the dates it shares with AR, its OOS R² is −0.273. Its rank-by-RMSE is therefore misleading.
- ⚠F1: the failed AR forecasts are scored in the FEDFUNDS-level AR row and in the UNRATE rows (UNRATE difference AR failed at 2020-04 and 2020-08).

**Conclusion: UNCHANGED.**

- No transformation yields significant nonlinear gains.
- STAR deteriorates sharply when UNRATE is differenced.
- The FEDFUNDS level specification is numerically worse-behaved, which supports the baseline differencing.
- **Status:** SUPPORTED that the baseline conclusions do not depend on the transformation, with the F1 qualification on the AR rows.

---

## T4.2 — CPI AR-lag robustness

**Context:** responds to R1-15. Threat: the old p=12 lag drives the result. The baseline BIC choice is p=2 (T2.5).

| p | RMSE h=1 (T4.2) | MAE | OOS R² against p=1 | HLZ p, squared/absolute, against p=1 (T4.2P) | DM-HLN p, squared/absolute |
|---|---|---|---|---|---|
| 1 | 3.073 | 2.192 | — | — | — |
| 2 (baseline, T3.3) | 2.967 | 2.086 | n/a | n/a | n/a |
| 3 | 2.958 | 2.073 | 0.074 | 0.101 / **0.012** | 0.013 / 0.0004 |
| 6 | 2.969 | 2.095 | 0.067 | 0.265 / 0.107 | 0.111 / 0.017 |
| 12 | 2.969 | 2.082 | 0.067 | 0.344 / 0.112 | 0.194 / 0.025 |

All rows use 715 common dates, from 1967-02 to 2026-08.

**Reading**

- Lags beyond 2 add nothing: p=3, 6 and 12 are within 0.01 RMSE of p=2.
- p=1 is worse. Under HLZ that is significant only for p=3 with absolute loss.
- The 12-lag structure criticised by the jury is unnecessary for forecasting. The BIC-selected p=2 performs as well as p=12.
- T4.2 benchmarks against p=1, not against the baseline p=2. A direct p=2-versus-p=12 test is therefore not in the outputs.
- ⚠F1: the p=12 chain contains one FAILED fit (origin 1974-09, `UNSTABLE_AR`, root modulus 1.006, FR/T4.7), which is scored. Its influence is probably small but unquantified.

**Status:** SUPPORTED, with the minor F1 qualification.

---

## T4.3 — Regime-count robustness: K=2 against K=3, in-sample only

**Context:** responds to P-04. Part 5 §11.1 as amended on 29 October 2026.

- No out-of-sample K=3 forecasts exist.
- No chi-square likelihood-ratio test is reported.

| Target | ΔlogL (K3 − K2) | ΔAIC | ΔBIC | IC favours | K=3 credible | Failing conditions (T4.3C) |
|---|---|---|---|---|---|---|
| GDPC1 | +29.57 | −49.14 | −30.36 | K=3 | No | low occupancy in regimes 1 and 3 (1 observation each); boundary; covariance non-positive; means not assessable |
| CPIAUCSL | +45.05 | −80.11 | −55.81 | K=3 | No | low occupancy in regime 1 (2.24%, 21.4 effective observations) only |
| UNRATE | **−88.16** | +186.31 | +210.54 | K=2 (**invalid**, F6) | No | low occupancy in regimes 2 and 3; boundary; covariance non-positive |
| INDPRO | +50.83 | −91.66 | −67.37 | K=3 | No | low occupancy in regimes 1 and 3; boundary; covariance non-positive |
| FEDFUNDS | +265.48 | −520.97 | −497.16 | K=3 | No | low occupancy in regimes 1 and 3; boundary |
| M2SL | +52.13 | −94.25 | −70.78 | K=3 | No | low occupancy in regimes 1 and 3; boundary |

**Regime structure (T4.3, T4.3P)**

- In every K=3 fit, the added regimes are short-lived extremes:
  - expected durations of 1.0 to 2.1 periods for the extreme regimes, except CPIAUCSL regime 3 (5.28 months) and UNRATE regime 2 (8.38 months);
  - occupancies of 0.1% to 2.5% for those extreme regimes. The exception is CPIAUCSL regime 3, the high-inflation regime, with 8.8% occupancy.
- **CPIAUCSL** is the closest to credible. It has three distinguishable means (μ = −6.65, 2.80 and 12.04; minimum z = 10.99), a usable covariance, and no boundary flag. In F4.3 the regimes are visibly:
  - deflation spikes (1949, 1986, 2008Q4, 2015, 2020);
  - normal inflation;
  - high inflation (1973–75, 1978–82, 2021–22).
  These labels are descriptive only; §11.1 forbids assigning economic labels.
- **FEDFUNDS.** The large ΔlogL of +265 reflects the K=2 solution being degenerate (identical regime means, likelihood equal to AR; F5), not a strong third regime.
- **UNRATE.** The K=3 likelihood lies *below* K=2's although K=3 nests K=2, so the K=3 estimate is a non-global local optimum from a 2-start search (F6). The UNRATE information-criterion comparison is **INCONCLUSIVE**.

**Conclusion**

- **Whether a third regime is credible:** no target has one under the predeclared §11.1 rule.
- **Whether that challenges K=2:** it does not challenge K=2 by offering a credible alternative.
- **What it does show:** the regime representation is weak *in general*, not that two regimes are too few. K=2 itself has outlier or unidentified regimes for GDPC1, INDPRO, M2SL and FEDFUNDS (T3.2).
- **Forecasting:** no forecasting implication may be drawn (§11.1).
- **Status:** QUALIFIED. K=2 is retained, as predeclared. The information criteria favour K=3 in-sample for five targets, and this is reported transparently. UNRATE is inconclusive.

---

## T4.4 — Horizon robustness (P-05)

T4.4 re-scores the stored baseline forecasts (`source = "stored baseline forecasts, no re-estimation"`). Horizons have different eligible dates, so this is not a common-sample comparison across horizons (T4.4 `evaluation_span_note`).

**HLZ rejections at 5%:** 10 of 138 tests (T4.4P).

| Comparison | Horizons and losses | Direction |
|---|---|---|
| CPIAUCSL ARMA vs AR | h=1 absolute; h=3, 6 and 12 squared and absolute (7 tests) | ARMA worse |
| CPIAUCSL MSAR vs AR | h=12 squared (p = 0.033) and absolute (p = 0.0044) | MSAR better |
| FEDFUNDS STAR vs AR | h=1 absolute (p = 0.029) | STAR worse |

**Conclusion**

- No systematic emergence of nonlinear gains at longer horizons.
- The CPIAUCSL h=12 MSAR gain (OOS R² 0.042, T3.3) is the only one.
- STAR iterated forecasts explode at h ≥ 3, as the T3.3 RMSE values show.
- UNRATE multi-step AR results are dominated by the F1 failed forecast (⚠F1).
- **Status:** QUALIFIED.

---

## T4.5 — Monthly five-variable VAR (R1-19, P-01)

**Selection and estimation**

- BIC selects VAR(1): BIC 4195.56 against 4197.21 for VAR(2) and 4256.67 for VAR(3); all are stable (T4.5S).
- 27 of 571 origins are unstable and excluded (T4.5C `var_unstable_origins`).
- Comparison uses identical common target dates across all models: 544 dates (525 for UNRATE, 538 for FEDFUNDS).

**Accuracy against AR**

| Target | VAR RMSE | AR RMSE | VAR OOS R² vs AR | Rank among 5 (T4.5C) |
|---|---|---|---|---|
| CPIAUCSL | 3.011 | 2.925 | −0.060 | 5 |
| INDPRO | 12.983 | 14.207 | 0.165 | 3 |
| UNRATE ⚠F1 | 0.626 | 1.011 | 0.616 | 2 |
| FEDFUNDS | 0.498 | 0.484 | −0.058 | 4 |
| M2SL | 4.820 | 5.052 | 0.090 | 1 |

**Inference (T4.5P)**

- The VAR never significantly improves on AR under HLZ.
- It is significantly **worse** for FEDFUNDS under absolute loss (HLZ p = 0.0036; DM p < 0.0001).
- STAR is also significantly worse than AR for FEDFUNDS under absolute loss (HLZ p = 0.035).
- Adding the VAR changes univariate ranks in several cells (`rank_changed_by_var`), but no univariate conclusion is reversed.

**Status:** SUPPORTED. On this evidence, omitted cross-variable information in a VAR(1) does not explain away, or create, nonlinear gains.

**Limits**

- A linear VAR is a limited multivariate response. It is not a multivariate STAR, MS-VAR or VECM.
- GDP is excluded by design (no interpolation; Part 5 §6.2).

---

## T4.6 — ARMA-GARCH(1,1) conditional-variance diagnostic

**Trigger results (T4.6T)**

| Target | ARCH-LM p | Triggered |
|---|---|---|
| CPIAUCSL | 1.4×10⁻¹² | yes |
| UNRATE | 1.8×10⁻⁶ | yes |
| FEDFUNDS | 0.021 | yes |
| GDPC1 | 0.485 | no — legitimate skip (one of the three skipped chains) |
| INDPRO | 0.990 | no — legitimate skip |
| M2SL | 0.369 | no — legitimate skip |

**Estimates and diagnostics (T4.6S)**

| | CPIAUCSL | UNRATE | FEDFUNDS |
|---|---|---|---|
| Converged origins | 688 / 715 | 689 / 704 | 505 / 625 (19% non-converged) |
| Mean α + β persistence | 0.829 | 0.555 | 0.968 |
| Maximum persistence | 0.999 | 0.999 | 0.999 |
| Standardised-residual ARCH-LM rejection rate | 0.00 | 0.26 | 0.03 |
| Ljung–Box rejection rate | 0.89 | 0.78 | 0.43 |

The maximum persistence of 0.999 is a near-integrated bound case.

**Mean forecasts on common dates (diagnostic only)**

| Target | ARMA-GARCH RMSE | ARMA RMSE | Common dates |
|---|---|---|---|
| CPIAUCSL | 2.817 | 2.970 | 688 |
| UNRATE | 0.457 | 0.449 | 674 |
| FEDFUNDS | 0.3234 | 0.3232 | 498 |

These models are excluded from the horse race and the MCS (decision M9). No inference is run on them, so the CPIAUCSL difference is **not** evidence of better mean forecasting (Part 5 §5.3).

**Status:** SUPPORTED as a diagnostic. Conditional heteroskedasticity is real for CPIAUCSL, UNRATE and FEDFUNDS, and the variance dynamics are highly persistent.

---

## T4.8 — Estimation-window-length sensitivity (h=1)

**Design**

- Windows: 180/240/300 months and 90/120/150 quarters.
- Specifications are fixed from the baseline.
- Each target is scored on a common eligible calendar (T4.8C):

| Target | Common dates | From |
|---|---|---|
| GDPC1 | 167 | 1984Q4 |
| CPIAUCSL | 655 | 1972-02 |
| INDPRO | 655 | 1972-02 |
| UNRATE | 644 | 1973-01 |
| FEDFUNDS | 565 | 1979-08 |
| M2SL | 511 | 1984-02 |

**OOS R² against AR on the common calendar (T4.8C)**

| Target / model | short | baseline | long |
|---|---|---|---|
| GDPC1 MSAR | 0.371 | 0.343 | 0.409 |
| GDPC1 STAR | 0.030 | 0.063 | 0.176 |
| CPIAUCSL MSAR | −0.017 | 0.004 | −0.034 |
| INDPRO ARMA | 0.298 | 0.198 | 0.196 |
| INDPRO MSAR | 0.294 | 0.248 | 0.251 |
| UNRATE MSAR ⚠F1 | 0.746 | 0.692 | 0.016 |
| FEDFUNDS MSAR | −0.035 | −0.029 | −0.024 |
| M2SL MSAR | −0.034 | −0.007 | −0.010 |
| STAR (CPIAUCSL, INDPRO, M2SL) | explosive at every length | | |

**Inference (T4.8P, 108 tests against AR)**

- **Conclusions against the baseline:** 97 unchanged, 10 reversed, 1 weakened.
  - All 10 reversals are sign flips of differentials that are insignificant at both windows.
  - The weakening is CPIAUCSL ARMA absolute loss at 180 months: HLZ p = 0.053 against 0.018 at baseline (support lost).
- **Strengthened:** FEDFUNDS ARMA against AR at 300 months (HLZ p = 0.032 squared and 0.014 absolute). The differential is economically negligible (−1×10⁻⁴).
- No nonlinear model gains HLZ support at any window. STAR remains significantly worse than AR for FEDFUNDS under absolute loss at all three lengths (HLZ p = 0.021, 0.033 and 0.039).
- **MCS:** 2 of 282 cells are unavailable (the same IndexError as F2; T4.8M).
- **Fragility rises with shorter windows** (T4.8A). For example:
  - GDPC1 MSAR is fragile at 164 of 227 origins at 90 quarters, against 136 of 197 at 120;
  - UNRATE ARMA has 22 failed origins at 180 months, against 15 at 240.

**Status:** SUPPORTED. The predeclared window lengths do not change the conclusions. The UNRATE rows await F1.

---

## T4.9 — October 2025 LOCF exposure

**Exposure (EXP)**

| Target | Forecast rows touched by the imputed values | Imputed target rows |
|---|---|---|
| CPIAUCSL | 120 of 11,368 | 16 |
| UNRATE | 108 of 11,192 | 16 |
| GDPC1, INDPRO, FEDFUNDS, M2SL | 0 | 0 |

**Effect on headline metrics (T4.9).** The pre-gap sample, ending 2025-09, against the full approved sample at h=1:

| Row | Pre-gap | Full sample |
|---|---|---|
| CPIAUCSL AR RMSE | 2.950 | 2.967 |
| CPIAUCSL MSAR OOS R² | −0.0009 | 0.0003 |
| UNRATE MSAR OOS R² ⚠F1 | 0.691 | 0.690 |

The rankings are identical.

**Status:** SUPPORTED. The user-approved LOCF has a negligible effect on headline evaluation. The T4.9 caveat applies: indirect exposure through estimation windows cannot be removed by dropping target dates.

---

## T4.TP1 — Turning-point-window sensitivity

- Widths: ±1, ±3 and ±6 months; 0, ±1 and ±2 quarters (TP1, 207 rows).
- **Baseline-width support:** turning-point coefficient significant only for FEDFUNDS ARMA versus AR at h=6.
- **Alternative widths:** support at 5% in **no** row (`alternative_support_5pct = False` throughout). The FEDFUNDS ARMA support is lost at ±1 and ±6 months.
- **Unavailable rows:** 6. In 4 of them a state indicator does not vary (1 CPIAUCSL, 3 M2SL). In the other 2 (CPIAUCSL) the HAC covariance is non-finite.

**Status:** NOT_SUPPORTED, for any claim that nonlinear gains concentrate around peaks or troughs.

---

## Overall robustness verdict

The baseline picture is robust to:

- the transformation;
- the lag order;
- the horizon (the CPI h=12 exception survives);
- the VAR information set;
- the window length;
- LOCF;
- the turning-window width.

That picture is: no formally supported nonlinear gain at h=1, fragile nonlinear estimates, and explosive STAR forecasts. Two items are pending:

- **UNRATE:** every comparison against AR is pending regeneration under F1.
- **CPI and M2 MCS cells:** they remain unavailable until F2 is decided.
