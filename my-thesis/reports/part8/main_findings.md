# Part 8 — Main findings

**Run:** `baseline-20261030T173044-949fcd76` (results `0662945`, code `46a53181e5e9`, data `7e7dc769…`). Full evidence and citations are in `full_empirical_analysis_report.md`, whose §0 defines the source keys. All file paths are relative to `output/`.

**Statuses** follow CLAUDE.md and Part 5 §12: SUPPORTED / QUALIFIED / NOT_SUPPORTED / INCONCLUSIVE.

**[audit]** marks an audit-derived diagnostic. These come from `reports/part8/audit_derived_diagnostics.csv` and are not thesis results.

> **Provisional element.** A material implementation defect (F1) scores one FAILED UNRATE AR fit (origin 2020-04, explosive root). Every UNRATE comparison against AR is provisional until regeneration is approved, and so are some robustness rows (T4.1 FEDFUNDS-level AR, T4.2 p=12). The other five targets' baseline results are unaffected.

---

## 1. Answer to the central research question

The question is *when nonlinear state-dependent models give statistically credible and economically meaningful gains over classical benchmarks, and when they do not.*

**In this U.S. sample, at the baseline one-step horizon, they do not.**

- No MSAR or STAR forecast is significantly more accurate than AR under the primary HLZ test, for any target. UNRATE is pending F1 (T3.3A).
- The single formally supported gain is MSAR for CPI inflation at the 12-month robustness horizon:
  - OOS R² 0.042 (T3.3, CPIAUCSL MSAR h=12);
  - HLZ p = 0.033 for squared loss and 0.004 for absolute loss (T3.3A, AR–MSAR rows).
  - It is a small, isolated result among many tests.
- **Status:** NOT_SUPPORTED for a general nonlinear advantage; QUALIFIED for the CPI h=12 exception.

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
- **Rolling estimates:** most MSAR and STAR fits are fragile (FR: MSAR 10,252 fragile of 15,443; STAR 12,702 of 15,443).

**Status:**

- SUPPORTED: nonlinear models fit better in-sample.
- NOT_SUPPORTED: that this reflects a credible recurrent nonlinear mechanism, except for CPI.

## 4. Out-of-sample accuracy (baseline h=1)

**Lowest RMSE (descriptive, T3.3):**

| Target | Lowest-RMSE model | OOS R² vs AR |
|---|---|---|
| GDPC1 | MSAR | 0.292 |
| INDPRO | MSAR | 0.236 |
| CPIAUCSL | MSAR | 0.0003 |
| UNRATE | MSAR | 0.690 published; 0.190 excluding the failed AR origin [audit] |
| FEDFUNDS | AR | — |
| M2SL | AR | — |

**Formal (HLZ):**

- No nonlinear-over-benchmark rejection at h=1.
- DM-HLN alone favours MSAR over AR for INDPRO (p = 0.018 and 0.0024; T3.3B). HLZ does not (p = 0.23 and 0.12), and HLZ governs (Part 5 §10.3).

**MCS (T3.4):**

- At h=1, AR and MSAR stay in every available 90% and 95% set. ARMA does too, except for CPIAUCSL absolute loss at 90% (MCS p = 0.075).
- The MCS is unavailable for CPIAUCSL h=1 squared loss and for 10 other CPIAUCSL/M2SL cells, because STAR's extreme losses break the routine (F2).

**The descriptive gains depend on the pandemic.** Excluding 2020-01 to 2021-06 [audit A3]:

| Target and model | OOS R², all dates | OOS R², without that window |
|---|---|---|
| GDPC1 MSAR | 0.292 | −0.051 |
| INDPRO MSAR | 0.236 | 0.021 |
| UNRATE MSAR (corrected benchmark) | 0.190 | −0.001 |

**Status:**

- NOT_SUPPORTED: superiority at h=1.
- QUALIFIED: a descriptive ranking that is driven by the pandemic episode.

## 5. STAR forecasting

STAR has the worst or explosive RMSE for most targets and horizons. Examples (T3.3):

| Target, horizon | STAR RMSE |
|---|---|
| CPIAUCSL h=1 | 5.4×10⁹ |
| INDPRO h=1 | 7.2×10⁶ |
| M2SL h=12 | 3.9×10⁹¹ |

- This is genuine near-non-identification, with the threshold outside the data and a singular information matrix. It is not a coding error.
- The approved rules (§8.2, D8) retain these fragile forecasts.
- STAR is significantly *worse* than AR for FEDFUNDS under absolute loss (HLZ p = 0.029).
- Pairwise STAR p-values cluster at about 0.32 (51 of 88 [audit A4]) because a few explosive errors dominate. They are uninformative.

**Status:** SUPPORTED that STAR does not provide credible forecast gains in this design.

## 6. State dependence (recessions and turning points; Verne V-05)

- The state-dependent loss regression finds no significant recession or turning-point effect for MSAR or STAR against AR (T3.5R).
- The only turning-point coefficient significant at 5% is FEDFUNDS ARMA versus AR at h=6 (p = 0.031). It disappears at the alternative window widths (TP1).
- Descriptively, GDPC1 MSAR has the lowest turning-window RMSE (8.87 against AR 11.26; T3.5S), dominated by 2020.

**Status:** NOT_SUPPORTED, for gains concentrated in recessions or turning points.

## 7. Benchmark strength

- The ARMA benchmark is a genuine ARMA only for UNRATE, ARMA(3,4) (T2.5).
- For CPIAUCSL and INDPRO it reduces to an AR(1), which is weaker than the AR(2) and AR(12) benchmarks.
- For CPIAUCSL, AR is significantly better than "ARMA" at every horizon (HLZ; T3.3A). MSAR's significant wins over ARMA (CPIAUCSL h=1 absolute, and h=3, 6, 12) reflect that weakness.

**Status:** QUALIFIED. Nonlinear gains against ARMA must not be presented as gains against a "stronger" benchmark for CPI.

## 8. Robustness (detail in `robustness_findings.md`)

- The conclusions are unchanged under:
  - alternative transformations (T4.1);
  - CPI lags of 1, 3, 6 and 12 (T4.2: p=12 is unnecessary, p=2 is adequate);
  - horizons (T4.4);
  - the monthly VAR(1) (T4.5: never significantly better than AR; significantly worse for FEDFUNDS);
  - window lengths (T4.8: 97 of 108 conclusions unchanged, none newly supportive);
  - LOCF (T4.9: negligible);
  - turning-window widths (TP1).
- **K=3** (T4.3): not credible for any target. K=2 is retained. CPIAUCSL K=3 fails only the 5% occupancy rule. The UNRATE K=3 fit is a non-global optimum, so it is inconclusive.
- **ARMA-GARCH** (T4.6): persistent conditional heteroskedasticity in CPIAUCSL, UNRATE and FEDFUNDS. It is a diagnostic only. GDPC1, INDPRO and M2SL were legitimately skipped because ARCH-LM did not reject.

## 9. Failures and fragility (R1-22)

- 67,253 fits:
  - 448 FAILED, mostly non-convergence, plus 105 `UNSTABLE_AR` events;
  - 23,008 FRAGILE;
  - 43,797 adequate (FR).
- The 34,153 registry rows are reason-code events, not failed fits: 540 FAILED and 33,613 FRAGILE (T4.7).
- Baseline horse-race failures: 34 fits, all UNRATE or FEDFUNDS (T3.3).

## 10. What must not be claimed

- That nonlinear models forecast better in general, or at h=1.
- That MSAR regimes are business-cycle regimes. In particular, no MSAR "recession regime" exists for GDPC1, INDPRO or M2SL.
- That the CPI high-inflation regime has a causal or policy meaning.
- That STAR captures a credible smooth transition, except possibly in-sample for CPI.
- That K=3 improves forecasting. It was never forecast.
- That results transfer to other countries, or to real-time nowcasting.
- Any UNRATE AR-relative number until F1 is corrected.

See `final_claims_allowed.md` for the exact wording permitted.
