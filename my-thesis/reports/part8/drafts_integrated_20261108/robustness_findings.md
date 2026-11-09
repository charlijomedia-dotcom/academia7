# Part 8 — Robustness findings (integrated candidate, draft)

> **DRAFT FOR INDEPENDENT REVIEW — integrated Part 8 candidate, 8 November 2026; revised 9 November 2026 after the archive. Not approved and not published.**
>
> - **Basis.** The integrated candidate of the Part 8 integration dry run: session `integration-20261108T052245Z-9bba8e`, run `correction-20261108T053328-949fcd76`, orchestration commit `a2c3171`, scientific pin `8aaa4217` (unchanged).
>   - It combines the R1 corrections (F1 failed-forecast scoring, F2 guarded MCS, F3 sign label, F4 Zivot–Andrews, F7.1) with the Tier A and Tier B recomputations: B1 (baseline UNRATE MSAR), B2 and B3.
>   - B2 was accepted on 8 November 2026 under the approved live warm-start rule (`corrections/r1/b2_scientific_adjudication.md`). Its certificate keeps the status `REVIEW_REQUIRED` as issued.
>   - No model was estimated in the integration.
> - **Archive (9 November 2026).** The candidate is archived, not published.
>   - Location: `baseline/r1_part8_candidate_archive/archive-20261109T080914Z-3c7d68/` on Drive. It holds 465 files; `release.tar.gz` has sha256 `54b61285…d7b4ee`.
>   - It is a non-estimating reconstruction (run `correction-20261109T080220-949fcd76`, archive tool `878d928`).
>   - It passed all nine equivalence checks against the audited session. Cell-level comparisons, decisions, chain sources and protected inputs are identical, and figures and original files are byte-identical. The 101 other differing files differ only in run provenance.
>   - Verification record: `corrections/r1/archive_verification_20261109.md`.
> - **Source of the numbers.** The candidate is **not yet under `output/`**.
>   - Every number comes from the integrated tables in `corrections/r1/evidence/part8_drafts_20261108/integrated_numbers.json`. The equivalence gate ties their cell content to the archived tree.
>   - `corrections/r1/evidence/part8_drafts_20261108/number_checks.csv` checks the quoted numbers.
>   - Table keys (T3.3, T4.1, …) name files of the archived tree, which keep the paths of `output/`.
>   - Under CLAUDE.md §9 the numbers become citable only after approval and publication.
> - **Not changed.** The published reports in `reports/part8/`, results commit `0662945`, releases `0573a8c`, `3bd24c4` and `292227e`, certificates, and `approved-specs/`. F8 (readable F3.4 main panel) remains disabled; D3 (publication destination) remains deferred.
> - **Changes from the published report:** `CHANGELOG.md` in this directory.

**Provenance.** Baseline estimation run `baseline-20261030T173044-949fcd76` (code `46a53181e5e9`); integrated candidate `correction-20261108T053328-949fcd76` (see the banner).

**Paths.** All paths below are the `output/`-relative paths of the candidate tree. The source keys are defined in `full_empirical_analysis_report.md` §0.

**Labels**

- Every result here is a **robustness** or **diagnostic** result unless marked otherwise. No robustness result replaces the baseline (CLAUDE.md §5).
- The **⚠F1** markers of the published report are removed. F1 is applied throughout: forecasts from failed fits are not scored. All chains that were pending estimation (T4.1 alternatives, T4.2, T4.8 UNRATE 180/300) are now computed.
- **Rankings versus significance.** RMSE ranks are descriptive and are computed on each model's own valid forecasts; OOS R² uses each competitor's dates matched with AR. Where models fail at different origins the two can disagree (`main_findings.md` §4). Only HLZ supports a statistical conclusion.

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
| UNRATE, levels (baseline) | 0.551 | 0.737 (R² 0.237) | 0.491 (0.189) | 0.592 (−0.103) |
| UNRATE, differences (alt) | **0.563** | 0.680 (0.419) | 0.776 (0.330) | 20.75 (−0.202) |
| FEDFUNDS, differences (baseline) | 0.475 | 0.477 (0.000) | 0.480 (−0.019) | 0.613 (−0.661) |
| FEDFUNDS, levels (alt) | **0.426** (n=555) | 0.520 (0.003, n=550) | 0.456 (−0.307; 577 valid, 540 matched) | 0.974 (−4.180) |

Bold: lowest h=1 RMSE in the alternative transformation. **AR ranks first under both alternatives** (T4.1 `rank_rmse`); in the published report MSAR did, because failed AR forecasts were scored.

**Inference** (T4.1P, alternative transformation only)

- None of the 12 HLZ tests rejects at 5%. The smallest p is 0.102 (FEDFUNDS-level STAR versus AR, absolute loss, STAR worse).
- FEDFUNDS-level ARMA versus AR: HLZ p = 0.808 (squared) and 0.146 (absolute).
- DM-HLN, the secondary test, rejects twice, both FEDFUNDS in levels under absolute loss:
  - ARMA, p = 0.0076, in ARMA's favour (HLZ p = 0.146);
  - MSAR, p = 0.029, **against** MSAR (HLZ p = 0.145; 0.130 in the published release). This change is attributable jointly to F1 and B2 and is not decomposed (`corrections/r1/b2_scientific_adjudication.md`).
- HLZ governs (Part 5 §10.3), so neither changes an inference.

**Failures and fragility**

- In the FEDFUNDS level alternative:
  - AR is `UNSTABLE_AR` at 71 origins, a near-unit root, and these forecasts are not scored;
  - MSAR fails at 49 of 626 origins (T4.1, FR). The published release had 52: under the approved live warm-start rule (B2, accepted) three 1980–81 fits become fragile rather than failed.
- MSAR's RMSE of 0.456 is computed on its 577 valid dates. On the 540 dates it shares with AR, its OOS R² is −0.307.
- UNRATE in differences: AR failed at 2 origins (2020-04 and 2020-08), which are not scored. STAR's own-sample RMSE is 20.75, but on the dates matched with AR its OOS R² is −0.202: the explosive STAR errors fall on the two dates that the matched sample excludes.

**Conclusion: UNCHANGED.**

- No transformation yields significant forecast differences against AR under HLZ, and none yields a nonlinear gain.
- **Point rankings do depend on the transformation:** AR has the lowest h=1 RMSE under both alternatives.
- STAR produces explosive forecasts when UNRATE is differenced.
- The FEDFUNDS level specification is numerically worse-behaved (71 unstable AR fits, 49 failed MSAR fits). This is consistent with the baseline differencing, which was chosen beforehand by the §3.4 rule and not on these results.
- **Status:** SUPPORTED that the inferential conclusions do not depend on the transformation; QUALIFIED for rankings (claim C15).

---

## T4.2 — CPI AR-lag robustness

**Context:** responds to R1-15. Threat: the old p=12 lag drives the result. The baseline BIC choice is p=2 (T2.5).

| p | RMSE h=1 (T4.2) | MAE | OOS R² against p=1 | HLZ p, squared/absolute, against p=1 (T4.2P) | DM-HLN p, squared/absolute |
|---|---|---|---|---|---|
| 1 | 3.075 | 2.194 | — | — | — |
| 2 (baseline, T3.3; own sample of 715 dates) | 2.967 | 2.086 | n/a | n/a | n/a |
| 3 | 2.958 | 2.072 | 0.075 | 0.101 / **0.013** | 0.012 / 0.0003 |
| 6 | 2.969 | 2.093 | 0.068 | 0.257 / 0.100 | 0.104 / 0.014 |
| 12 | 2.967 | 2.080 | 0.069 | 0.327 / 0.101 | 0.180 / 0.019 |

The p=1, 3, 6 and 12 rows use 714 common dates, from 1967-02 to 2026-08. The published release used 715; the p=12 chain's failed fit (origin 1974-09, `UNSTABLE_AR`, root modulus 1.006) is no longer scored (F1), and the chain was re-estimated under Tier A with results equal to the R1 preview.

**Reading**

- **Descriptively**, lags beyond 2 bring no visible gain. p=3, 6 and 12 are within 0.01 RMSE of the baseline p=2 (2.967 on its own 715 dates).
  - On the 714 T4.2 dates, AR(2) has RMSE 2.966 and MAE 2.084 [audit], against 2.967 and 2.080 for AR(12). The RMSE ordering and the MAE ordering disagree.
  - The [audit] figures are computed from the baseline AR(2) forecasts after removing target 1974-10. That is the only failed p=12 fit (origin 1974-09), so it is presumed to be the date missing from the T4.2 sample.
- **Inferentially**, p=1 is worse than p=3 under HLZ only with absolute loss (p = 0.013). AR(12) does not significantly beat AR(1) (HLZ p = 0.327 squared, 0.101 absolute). DM-HLN also rejects for p=3 squared, p=6 absolute and p=12 absolute; HLZ governs.
- **What is not established.** T4.2 benchmarks against p=1, not against the baseline p=2, so no direct p=2-versus-p=12 test exists.
  - A non-rejection would in any case not show equal accuracy, and no equivalence test was run.
  - The models are nested. Under a fixed rolling window, the larger model's extra parameters add estimation noise even when the extra lags have no population effect. A raw RMSE tie therefore does not decide whether the extra lags carry information.
  - The supported statement is: **no evidence that 12 lags improve one-step forecast accuracy over AR(2)**. It is not "AR(2) forecasts as accurately as AR(12)", and it is not a proof that 12 lags bring no benefit.
- The p=2 row is on its own 715-date sample, not on the 714 common dates; the comparison with p=2 is descriptive.

**Status:** QUALIFIED (claim C16). R1-15 remains resolved: the requested analysis is performed and reported (CLAUDE.md §12).

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

**HLZ rejections at 5%:** 11 of 138 tests (T4.4P).

| Comparison | Horizons and losses | Direction |
|---|---|---|
| CPIAUCSL ARMA vs AR | h=1 absolute; h=3, 6 and 12 squared and absolute (7 tests) | ARMA worse |
| CPIAUCSL MSAR vs AR | h=12 squared (p = 0.033) and absolute (p = 0.0044) | MSAR better |
| UNRATE STAR vs AR | h=1 absolute (p = 0.0015) | STAR worse (new with F1; Holm 0.066 across the 44 STAR-vs-AR tests [audit]) |
| FEDFUNDS STAR vs AR | h=1 absolute (p = 0.029) | STAR worse |

**Conclusion**

- No systematic emergence of nonlinear gains at longer horizons.
- The CPIAUCSL h=12 MSAR gain (OOS R² 0.042, T3.3) is the only one.
- STAR iterated forecasts explode at h ≥ 3, as the T3.3 RMSE values show.
- UNRATE multi-step (T3.3): AR RMSE is 0.942, 1.165 and 1.492 at h=3, 6 and 12. AR ranks first by RMSE at h=3 and 6; at h=12 ARMA ranks first by RMSE (OOS R² 0.093) and AR first by MAE. MSAR's OOS R² is negative at every longer horizon (−0.129, −0.538, −0.952). No HLZ test rejects in a nonlinear model's favour.
- At explosive STAR horizons the pairwise tests are degenerate and carry no inference (see "Degenerate STAR tests" below).
- **Status:** QUALIFIED.

---

## T4.5 — Monthly five-variable VAR (R1-19, P-01)

**Selection and estimation**

- BIC selects VAR(1): BIC 4195.56 against 4197.21 for VAR(2) and 4256.67 for VAR(3); all are stable (T4.5S).
- 27 of 571 origins are unstable and excluded (T4.5C `var_unstable_origins`).
- Comparison uses identical common target dates across all models: 544 dates (527 for UNRATE, 538 for FEDFUNDS).

**Accuracy against AR**

| Target | VAR RMSE | AR RMSE | VAR OOS R² vs AR | Rank among 5 (T4.5C) |
|---|---|---|---|---|
| CPIAUCSL | 3.011 | 2.925 | −0.060 | 5 |
| INDPRO | 12.983 | 14.207 | 0.165 | 3 |
| UNRATE | 0.493 | 0.613 | 0.353 | 1 (descriptive) |
| FEDFUNDS | 0.498 | 0.484 | −0.058 | 4 |
| M2SL | 4.820 | 5.052 | 0.090 | 1 |

**Inference (T4.5P)**

- The VAR never significantly improves on AR under HLZ.
- It is significantly **worse** for FEDFUNDS under absolute loss (HLZ p = 0.0036; DM p < 0.0001).
- STAR is also significantly worse than AR under absolute loss for FEDFUNDS (HLZ p = 0.035) and UNRATE (HLZ p = 0.0088).
- **UNRATE.** The VAR has the lowest RMSE on the common sample (0.493; ARMA 0.538, MSAR 0.550, AR 0.613, STAR 0.622), but VAR versus AR is not significant (HLZ p = 0.346 squared, 0.811 absolute). The rank is descriptive.
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
| UNRATE ARMA | 0.302 | 0.238 | 0.202 |
| UNRATE MSAR | 0.240 | 0.190 | −1.102 |
| UNRATE STAR | −2.714 | −0.104 | −0.075 |
| FEDFUNDS MSAR | −0.035 | −0.029 | −0.024 |
| M2SL MSAR | −0.034 | −0.007 | −0.010 |
| STAR (CPIAUCSL, INDPRO, M2SL) | explosive at every length | | |

**Inference (T4.8P, 108 tests against AR)**

- **Conclusions against the baseline:** 97 unchanged, 10 reversed, 1 weakened.
  - All 10 reversals are sign flips of differentials that are insignificant at both windows.
  - The weakening is CPIAUCSL ARMA absolute loss at 180 months: HLZ p = 0.053 against 0.018 at baseline (support lost).
- **Strengthened:** FEDFUNDS ARMA against AR at 300 months (HLZ p = 0.032 squared and 0.014 absolute). The differential is economically negligible (−1×10⁻⁴).
- No nonlinear model gains HLZ support at any window. STAR is significantly worse than AR under absolute loss at all three lengths:
  - FEDFUNDS: HLZ p = 0.021, 0.033 and 0.039 (180, 240, 300);
  - UNRATE: HLZ p = 0.046, 0.0012 and 0.0017. The 180- and 300-month UNRATE chains are now computed (Tier B), so finding 1 of the integration audit replicates at every length.
- **UNRATE MSAR is not window-robust descriptively.** Its h=1 OOS R² falls from 0.240 and 0.190 to −1.102 at 300 months, where it ranks 4th of 4 by RMSE and AR ranks 1st (T4.8C). Its HLZ p-values against AR lie between 0.30 and 0.77 at every length, so no window gives a significant difference in either direction.
- The window-test counts are the same as in the published release (97 / 10 / 1), but their composition changes (support absent in both 87, no change 18, strengthened 2, support lost 1; T4.8P `support_change`).
- **MCS:** all 288 rows (72 cells) are available (guarded procedure F2; T4.8M). The published release had 2 unavailable rows.
- **Fragility rises with shorter windows** (T4.8A). For example:
  - GDPC1 MSAR is fragile at 164 of 227 origins at 90 quarters, against 136 of 197 at 120;
  - UNRATE ARMA has 22 failed origins at 180 months, against 15 at 240.

**Status:** SUPPORTED for the inferential conclusions; QUALIFIED for the UNRATE MSAR descriptive ranking, which is not window-robust (claim C14).

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
| UNRATE MSAR OOS R² | 0.191 | 0.189 |

The rankings are identical.

**Status:** SUPPORTED. The user-approved LOCF has a negligible effect on headline evaluation. The T4.9 caveat applies: indirect exposure through estimation windows cannot be removed by dropping target dates.

---

## T4.TP1 — Turning-point-window sensitivity

- Widths: ±1, ±3 and ±6 months; 0, ±1 and ±2 quarters. TP1 has 552 rows: 276 turning-window and 276 outside-window cells, of which 207 carry a comparison with the baseline width.
- **Baseline-width support:** turning-point coefficient significant only for FEDFUNDS ARMA versus AR at h=6.
- **Alternative widths:** support at 5% in **no** row (`alternative_support_5pct = False` throughout). The FEDFUNDS ARMA support is lost at ±1 and ±6 months.
- **Comparisons with the baseline width:** 174 unchanged, 24 reversed (sign flips of insignificant differentials), 3 weakened, 6 unavailable. The published release had 175 and 23; the difference is 9 UNRATE rows whose label changes because the corrected losses (F1, and B1 for MSAR) flip the sign of an insignificant differential. No row has baseline-width support except FEDFUNDS ARMA h=6.
- **Unavailable rows:** 6. In 4 of them a state indicator does not vary (1 CPIAUCSL, 3 M2SL). In the other 2 (CPIAUCSL) the HAC covariance is non-finite.

**Status:** NOT_SUPPORTED, for any claim that nonlinear gains concentrate around peaks or troughs.

---

## Optimiser sensitivity of rolling MSAR (B2; C07)

B2 re-estimated two MSAR robustness chains under the approved live warm-start rule: T4.1 FEDFUNDS in levels (626 origins) and T4.8 UNRATE at 180 months (764 origins). It was accepted on 8 November 2026 (`corrections/r1/b2_scientific_adjudication.md`).

| Chain | Classification changes against the published records | Optimiser sensitivities (same status, different optimum) |
|---|---|---|
| T4.1 FEDFUNDS MSAR, levels | 14: failed → fragile 3 (1980-01, 1981-05, 1981-06); failed → failed with other reason codes 5; fragile → fragile with other codes 6 | 29: log-likelihood higher by 0.04 to 275 (median 24.4) |
| T4.8 UNRATE MSAR, 180 months | 6, 1982-01 to 1982-06: fragile → adequate 5; failed → failed with other codes 1 | 0 |

- They are local optima of MSAR(p, K=2) in regime-poor windows. A higher or lower likelihood does not by itself make an estimate preferable; the approved rule defines the estimator.
- Effect: FEDFUNDS MSAR failed 52 → 49 (T4.7 status counts); the FEDFUNDS-level DM-HLN change above (with F1); no HLZ decision changes.
- **F6 stands:** the approved multistart does not guarantee the global maximum, for these or any other MSAR estimates.

## Degenerate STAR tests

- In 58 of the 230 T3.3A rows the mean loss differential exceeds 10³ (up to about 10⁹⁷), because a few STAR forecasts exploded (CPIAUCSL, INDPRO and M2SL at h=1–12; UNRATE at h=6 and 12; FEDFUNDS at h=3–12, squared loss). The corresponding STAR rows of T4.4, T4.5 and T4.8 are read the same way.
- There the HLZ statistic settles near 1.6 and p ≈ 0.31–0.33 regardless of the differential's size. These tests are **numerically degenerate**: they are read as "no usable inference: the STAR forecasts exploded", not as "no significant difference", and they support no affirmative inferential claim (`corrections/r1/star_test_degeneracy.csv`).
- 15 T3.5 STAR regressions have |α| between 10³ and 10⁸⁰; their state-dependence tests are rank-deficient and also non-informative.
- In every degenerate row STAR is worse by orders of magnitude, so a degenerate non-rejection cannot conceal a nonlinear gain.

## Overall robustness verdict

The baseline picture is robust to:

- the transformation;
- the lag order;
- the horizon (the CPI h=12 exception survives);
- the VAR information set;
- the window length;
- LOCF;
- the turning-window width.

That picture is: no formally supported nonlinear gain at h=1, fragile nonlinear estimates, and explosive STAR forecasts. No robustness exercise produces a nonlinear-over-AR rejection.

Point rankings are less robust than the inferential conclusions: AR ranks first under both alternative transformations, and UNRATE MSAR's h=1 descriptive advantage disappears at the 300-month window.

**Remaining limitations:** F6 (no global MSAR maximum), the MSAR optimiser sensitivity above, nominal p-values without a predeclared multiple-testing family, the visible model failures (§T4.1, T4.7), and the degenerate STAR tests.
