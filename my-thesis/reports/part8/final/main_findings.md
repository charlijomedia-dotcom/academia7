# Part 8 — Main findings (final)

> **FINAL PART 8 REPORT — release `part8-final-20261109`.** **Published on 2026-11-10:** commit `9817daf91ac4cb4aaa42c2bef5deaff5b674841b` on `part8-corrected-results/final-20261109`; Drive `baseline/r1_part8_final_release/part8-final-20261109/` (release.tar.gz sha256 `a9d1a028d0e0b09e9fff3a98d7593cb51026ce70cff1db25b12d1beb225728b8`), verified at both destinations (`PUBLICATION.md`).
>
> - **Authoritative numbers.** `my-thesis/output/` in the release commit on branch `part8-corrected-results/final-20261109`: 465 files, listed with sha256 in `my-thesis/release/part8_final/release_inventory.csv`. See `SOURCE_OF_TRUTH.md` in this directory.
>   - `output/` in any other commit or branch holds superseded or provisional values. That includes `part8-r1-rescore`, the pin `8aaa4217` and the results commit `0662945`, which hold the original baseline. **Do not use it.**
> - **Numbers identity.** Run `correction-20261109T080220-949fcd76` (archive `archive-20261109T080914Z-3c7d68`), equivalent to the audited run `correction-20261108T053328-949fcd76`. Scientific code `8aaa4217`, unchanged. No model was estimated in the integration or the release. B2 was accepted on 8 November 2026 (`corrections/r1/b2_scientific_adjudication.md`).
> - **Number checks.** Every quoted number is checked against the integrated tables, whose cell content the archive's equivalence gate ties to the release: `corrections/r1/evidence/part8_drafts_20261108/number_checks.csv`.
> - **F3.4 figures.** The release's `figures/F3.4_*` are the approved F8 versions (presentation only, approved 9 November 2026; sha256 in `release_inventory.csv`).
> - **Not changed.** The superseded reports in `reports/part8/*.md` and the drafts in `drafts_integrated_20261108/`; results commit `0662945`; the provisional releases `0573a8c`, `3bd24c4` and `292227e`; certificates; `approved-specs/`.
> - **Changes from the published (1 November) reports and from the drafts:** `CHANGELOG.md`.

**Provenance.** The baseline estimation run is `baseline-20261030T173044-949fcd76` (code `46a53181e5e9`, data `7e7dc769…`). The integrated candidate re-scores its forecasts and replaces the recomputed chains listed in the banner. Full evidence and citations are in `full_empirical_analysis_report.md`, whose §0 defines the source keys.

**Statuses** follow CLAUDE.md and Part 5 §12: SUPPORTED / QUALIFIED / NOT_SUPPORTED / INCONCLUSIVE.

**[audit]** marks an audit-derived diagnostic. It is not an approved-methodology result and is not citable as a thesis result.

**Inference language.** A non-rejection means "no evidence of a difference". It never means "equal accuracy". A *descriptive ranking* (lowest RMSE, rank) is not a *statistical* conclusion; only the HLZ test, read with the MCS, supports a statistical one.

---

## 1. Answer to the central research question

The question is *when nonlinear state-dependent models give statistically credible and economically meaningful gains over classical benchmarks, and when they do not.*

**In this U.S. sample, at the baseline one-step horizon, they do not.**

- No MSAR or STAR forecast is significantly more accurate than AR under the primary HLZ test, for any of the six targets, unemployment included (T3.3A).
- The single formally supported gain is MSAR for CPI inflation at the 12-month robustness horizon:
  - OOS R² 0.042 (T3.3, CPIAUCSL MSAR h=12);
  - HLZ p = 0.033 for squared loss and 0.004 for absolute loss (T3.3A, AR–MSAR rows).
  - It is a small, isolated result among many tests.
- **Multiple comparisons.** This qualification is a descriptive audit check, not an approved procedure.
  - Within the 46 MSAR-versus-AR HLZ tests (all targets, horizons and losses; T3.3A), the Holm-adjusted p-values are 0.204 (absolute loss) and 1.0 (squared loss).
  - The Bonferroni threshold for that family is 0.05/46 ≈ 0.0011.
  - **The CPI h=12 gain therefore does not survive a family-wise correction.** It is an unadjusted 5% result.
- **Non-rejection is not equality.** Failing to reject equal accuracy means the data do not provide evidence of superiority. It does **not** show that the models forecast equally well. The tests have limited power with a few hundred dependent observations and time-varying loss differentials.
- **Every decision change produced by the corrections that involves a nonlinear model goes against it.** The new nominal rejection is STAR *worse* than AR for unemployment at h=1 under absolute loss (§5). The other changes concern linear-versus-linear comparisons (the UNRATE ARMA-vs-AR joint Wald, §6) or the secondary DM-HLN test.
- **Status:**
  - NOT_SUPPORTED: a general nonlinear advantage.
  - QUALIFIED: the CPI h=12 exception (unadjusted significance; not robust to multiplicity).

## 2. Nonlinearity evidence before estimation (R1-18)

- **Tsay test:** rejects linearity only for UNRATE (p = 0.0013; T2.3).
- **LST/Teräsvirta test:** rejects at the selected delay for:
  - CPIAUCSL (d=6, p = 2.4×10⁻⁹);
  - UNRATE (d=1, p = 3.2×10⁻⁵);
  - FEDFUNDS (d=1, p = 0.043).
- **No pre-test rejects** for GDPC1, INDPRO or M2SL (T2.4).
- **Status:** QUALIFIED. The evidence of nonlinearity is target-specific and absent for half the targets.

## 3. In-sample fit versus credibility (fit before forecast; Verne V-06)

**Fit**

- MSAR improves on AR's BIC for 5 of 6 targets; FEDFUNDS is the exception (T3.1).
- STAR improves on AR's BIC for 5 of 6 targets; INDPRO is the exception.

**Credibility**

- The full-sample regime estimates are mostly *not credible* (T3.2, T4.3):

  | Target | Full-sample K=2 regime estimate |
  |---|---|
  | GDPC1 | a one-observation pandemic regime with boundary transitions (μ1 = −38.1, 1 effective observation) |
  | INDPRO | a one-observation pandemic regime with boundary transitions (μ1 = −167.8) |
  | M2SL | a 3-observation pandemic regime with boundary transitions (μ2 = 53.7) |
  | FEDFUNDS | two identical regimes (μ1 = μ2 = 0.0025), with a likelihood equal to AR's, so effectively unidentified |
  | UNRATE | boundary persistence (p11 = 0.9991) and poorly identified means in levels |
  | CPIAUCSL | the only interpretable regime: high inflation, μ = 12.5, 8.6% occupancy, 6.3-month duration |

- STAR full-sample fits are well behaved only for CPIAUCSL. Elsewhere γ sits at its bound, or the threshold sits at the sample extreme with a singular covariance.
- **Rolling estimates** (FR, all chains):
  - MSAR: 10,246 fragile of 15,443 fits (adequate 5,128; failed 69);
  - STAR: 12,702 fragile of 15,443 (adequate 2,741).
  - **"Predominantly fragile" is a statement about the rolling nonlinear estimates pooled across models and targets.** It does not hold for every chain: the UNRATE MSAR chains are majority *adequate* (2,120 adequate, 1,380 fragile; T4.7 status counts), and the baseline UNRATE MSAR chain is fragile at 258 of 704 origins (T3.3).
- **Optimiser sensitivity (B2, accepted).** Re-estimating two MSAR robustness chains under the approved live warm-start rule changed 20 fit classifications and gave higher likelihoods at 29 further origins, in regime-poor windows: FEDFUNDS in levels in 1980–81, UNRATE at 180 months in 1982 (`corrections/r1/b2_scientific_adjudication.md`). Rolling MSAR estimates are local optima; no global maximum is claimed (F6).

**Status:**

- SUPPORTED: nonlinear models fit better in-sample.
- NOT_SUPPORTED: that this reflects a credible recurrent nonlinear mechanism, except for CPI.

## 4. Out-of-sample accuracy (baseline h=1)

**Lowest RMSE (descriptive; T3.3, each model's own valid forecasts) and OOS R² against AR (on each competitor's dates common with AR):**

| Target | Lowest-RMSE model | Its OOS R² vs AR |
|---|---|---|
| GDPC1 | MSAR | 0.292 |
| INDPRO | MSAR | 0.236 |
| CPIAUCSL | MSAR | 0.0003 |
| UNRATE | MSAR (own-sample RMSE 0.491) — **see the note below** | 0.189 |
| FEDFUNDS | AR | — |
| M2SL | AR | — |

**Unemployment at h=1: three different accuracy measures.** They answer different questions and must be quoted separately (claim C21):

| Measure | AR | ARMA | MSAR | STAR |
|---|---|---|---|---|
| RMSE, each model's own valid sample (T3.3 `rmse`; n) | 0.551 (703) | 0.737 (689) | 0.491 (698) | 0.592 (704) |
| OOS R² against AR, on each competitor's sample matched with AR (T3.3 `oos_r2_vs_benchmark`; n) | — | 0.237 (688) | 0.189 (697) | −0.103 (703) |
| RMSE on the 682 dates common to all four models [audit] | 0.546 | 0.482 | 0.492 | 0.556 |

- The own-sample ranking (MSAR first, ARMA last) is driven by **one target date, 2020-05**: the AR fit failed and is not scored (F1), ARMA's error is −14.53, and MSAR's is −1.83.
- On the common sample ARMA and MSAR are numerically close (0.482 and 0.492), both below AR. **No test of their equality was run**, so they are not described as equivalent, and MSAR is **not** described as the most accurate unemployment forecaster at h=1.
- None of the h=1 unemployment differences against AR is significant under HLZ, except STAR's nominal underperformance under absolute loss (§5). ARMA versus MSAR is not significant either (HLZ p = 0.32 squared, 0.22 absolute; T3.3A).
- The approved metric definitions are unchanged. The common-sample RMSE is an audit computation and is not citable as a thesis number.

**Formal (HLZ):**

- No nonlinear-over-benchmark rejection at h=1.
- DM-HLN alone favours MSAR over AR for INDPRO (p = 0.018 and 0.0024; T3.3B). HLZ does not (p = 0.23 and 0.12), and HLZ governs (Part 5 §10.3).

**MCS (T3.4, guarded procedure F2; all 92 cells available):**

- At h=1, AR and MSAR stay in every 90% and 95% set.
- ARMA is excluded only for CPIAUCSL absolute loss at 90% (MCS p = 0.075).
- STAR is excluded only for FEDFUNDS absolute loss, at 90% and 95% (MCS p = 0.045).

**The descriptive gains depend on the pandemic.** Excluding 2020-01 to 2021-06 [audit A3]:

| Target and model | OOS R², all dates | OOS R², without that window |
|---|---|---|
| GDPC1 MSAR | 0.292 | −0.051 |
| INDPRO MSAR | 0.236 | 0.021 |
| UNRATE MSAR | 0.189 | −0.010 |
| UNRATE ARMA | 0.237 | −0.051 |

**Status:**

- NOT_SUPPORTED: superiority at h=1.
- QUALIFIED: a descriptive ranking that is driven by the pandemic episode and, for unemployment, by the evaluation sample.

## 5. STAR forecasting

STAR has the worst or explosive RMSE for most targets and horizons. Examples (T3.3):

| Target, horizon | STAR RMSE |
|---|---|
| CPIAUCSL h=1 | 5.4×10⁹ |
| INDPRO h=1 | 7.2×10⁶ |
| M2SL h=12 | 3.9×10⁹¹ |

- This is genuine near-non-identification, with the threshold outside the data and a singular information matrix. It is not a coding error.
- The approved rules (§8.2, D8) retain these fragile forecasts.
- **Significantly worse than AR (HLZ, absolute loss, h=1):**
  - FEDFUNDS, p = 0.029;
  - UNRATE, p = 0.0015. This is a nominal result: the Holm-adjusted p across the 44 STAR-versus-AR tests is 0.066 [audit], and STAR stays in the UNRATE 90% and 95% MCS. It replicates at the 180- and 300-month windows (T4.8P).
- **Numerical instability is not statistical evidence.** In 58 of the 230 pairwise rows (T3.3A) the mean loss differential exceeds 10³, up to about 10⁹⁷, because a few STAR forecasts exploded. There the HLZ statistic settles near 1.6 and p ≈ 0.31–0.33 whatever the size of the differential (50 of the 88 available STAR-pair p-values lie in [0.30, 0.34] [audit A4]).
  - These are **degenerate tests**. They are read as "no usable inference: the STAR forecasts exploded", not as "no significant difference", and they support no affirmative inferential claim in either direction.
  - The unemployment h=1 STAR result is not degenerate (the largest single date's share of the sum of squared loss differentials is 0.28 under absolute loss and 0.41 under squared loss).

**Status:** SUPPORTED that STAR does not provide credible forecast gains in this design.

## 6. State dependence (recessions and turning points; Verne V-05)

- The state-dependent loss regression finds no significant recession or turning-point effect for MSAR or STAR against AR (T3.5R).
- **Unemployment, ARMA versus AR, h=1.** Two Wald tests on the same regression must be reported separately:
  - the **joint** test (α = β_rec = β_turn = 0, χ²(3) = 8.65) rejects at the nominal 5% level, p = 0.034;
  - the **state-dependence** test (β_rec = β_turn = 0, χ²(2) = 2.53) does **not** reject, p = 0.282;
  - no single coefficient is significant at 10% (α = −0.084, p = 0.224; β_rec = 0.091, p = 0.117; β_turn = 0.0002, p = 0.998; n = 688).
  - The joint rejection is **not evidence of state dependence**. It is one nominal result among 69 joint tests, and it compares two linear models.
- The only turning-point coefficient significant at 5% is FEDFUNDS ARMA versus AR at h=6 (p = 0.031). Its state-dependence (slopes) test does not reject (p = 0.082), and the support disappears at the alternative window widths (TP1).
- Descriptively, GDPC1 MSAR has the lowest turning-window RMSE (8.87 against AR 11.26; T3.5S), dominated by 2020.

**Status:** NOT_SUPPORTED, for gains concentrated in recessions or turning points.

## 7. Benchmark strength

- The ARMA benchmark is a genuine ARMA only for UNRATE, ARMA(3,4) (T2.5).
- For CPIAUCSL and INDPRO it reduces to an AR(1), which is weaker than the AR(2) and AR(12) benchmarks.
- For CPIAUCSL, AR is significantly better than "ARMA" at every horizon (HLZ; T3.3A). MSAR's significant wins over ARMA (CPIAUCSL h=1 absolute, and h=3, 6, 12) reflect that weakness.

**Status:** QUALIFIED. Nonlinear gains against ARMA must not be presented as gains against a "stronger" benchmark for CPI.

## 8. Robustness (detail in `robustness_findings.md`)

No robustness exercise produces a nonlinear-over-AR rejection; the only one anywhere remains CPI h=12 MSAR.

- **Transformations (T4.1):** none of the 12 HLZ tests rejects. Point rankings depend on the transformation: AR has the lowest h=1 RMSE for UNRATE in differences and FEDFUNDS in levels.
- **CPI lags (T4.2, 714 common dates):** no evidence that 12 lags improve on the BIC-selected AR(2). AR(12) does not significantly beat AR(1) (HLZ p = 0.327 / 0.101), and its RMSE is within 0.002 of AR(2)'s on nearly the same dates. Equal accuracy is **not** established: there is no direct AR(2)-versus-AR(12) test and no equivalence test (C16, QUALIFIED). Only p=3 beats p=1 under HLZ (absolute loss, p = 0.013).
- **Horizons (T4.4):** 11 of 138 HLZ rejections; the only one favouring a nonlinear model is CPIAUCSL MSAR at h=12.
- **Monthly VAR(1) (T4.5):** never significantly better than AR; significantly worse for FEDFUNDS under absolute loss.
- **Window lengths (T4.8):** 97 of 108 conclusions unchanged, 10 insignificant sign reversals, 1 weakened; no nonlinear model gains HLZ support at any length. The UNRATE STAR rejection replicates at all three lengths. **UNRATE MSAR's descriptive h=1 advantage is not window-robust** (OOS R² 0.240, 0.190 and −1.102 at 180, 240 and 300 months; rank 4 of 4 at 300; no significant difference at any length).
- **LOCF (T4.9):** negligible; identical rankings.
- **Turning-window widths (TP1):** no support at any alternative width.
- **K=3** (T4.3): not credible for any target. K=2 is retained. CPIAUCSL K=3 fails only the 5% occupancy rule. The UNRATE K=3 fit is a non-global optimum, so it is inconclusive (F6).
- **ARMA-GARCH** (T4.6): persistent conditional heteroskedasticity in CPIAUCSL, UNRATE and FEDFUNDS. It is a diagnostic only. GDPC1, INDPRO and M2SL were legitimately skipped because ARCH-LM did not reject.

## 9. Failures and fragility (R1-22)

- 67,253 fits (FR):
  - 435 FAILED, mostly non-convergence;
  - 23,002 FRAGILE;
  - 43,816 adequate.
- The 34,122 registry rows are reason-code events, not failed fits: 512 FAILED (including 105 `UNSTABLE_AR`) and 33,610 FRAGILE (T4.7). These totals are verified on the archived `T4.7_failure_registry.csv` (independent review of archive `archive-20261109T080914Z-3c7d68`).
- Baseline horse-race failures at h=1: 29 fits, all UNRATE or FEDFUNDS: UNRATE AR 1, ARMA 15, MSAR 6; FEDFUNDS ARMA 7 (T3.3). Failed fits are not scored (F1).
- The MSAR optimiser sensitivity recorded under B2 (20 classification changes, 29 sensitivities) is part of this fragility evidence (§3).

## 10. What must not be claimed

- That nonlinear models forecast better in general, or at h=1.
- That MSAR is the most accurate unemployment forecaster at h=1, or that MSAR and ARMA are equally accurate there (§4).
- That the unemployment ARMA-versus-AR joint Wald rejection shows state dependence (§6).
- That a degenerate STAR test shows equal accuracy, or any other affirmative inference (§5).
- That MSAR regimes are business-cycle regimes. In particular, no MSAR "recession regime" exists for GDPC1, INDPRO or M2SL.
- That the CPI high-inflation regime has a causal or policy meaning.
- That STAR captures a credible smooth transition, except possibly in-sample for CPI.
- That AR(2) and AR(12) forecast CPI inflation equally well, or that 12 lags bring no benefit; only the absence of evidence of improvement is shown (C16).
- That K=3 improves forecasting. It was never forecast.
- That any MSAR estimate is a global likelihood maximum (F6).
- That results transfer to other countries, or to real-time nowcasting.

See `final_claims_allowed.md` for the exact wording permitted.
