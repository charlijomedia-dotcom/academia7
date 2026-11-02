# Multiplicity check: UNRATE h=1 STAR versus AR (absolute loss)

Requested by the user on 2 November 2026: check and document the appropriate predeclared test family, and make no claim of family-wise significance without justification.

All p-values are from the R1 corrected table `forecast_tests/T3.3A_hlz_pairwise.csv`. The Holm adjustments below are a Part 8 audit computation, not an approved procedure output (`unrate_star_multiplicity.csv`).

## 1. What the approved methodology predeclares

- **§10.2 (primary pairwise test).** HLZ is applied to five model pairs (AR–ARMA, AR–MSAR, AR–STAR, ARMA–MSAR, ARMA–STAR), under squared and absolute loss, at the 5% level. No family-wise adjustment of these pairwise tests is specified.
- **§10.4 (multiple-model comparison).** The predeclared device for inference across several models is the Hansen–Lunde–Nason MCS at 90% and 95%. In the specification's own words, it "avoids interpreting a large table of pairwise p-values as if one model must be uniquely best".
- **§13.2.** Stars mark nominal p-value thresholds only.
- **Literature justification §5.5.** A generic Holm correction was considered and removed, but for the STAR delay scan, not for forecast comparisons.

**Conclusion.** The approved design defines no Holm or Bonferroni family for the pairwise HLZ tests. Each HLZ p-value is a nominal per-comparison p-value. Multi-model, multiplicity-aware inference is delegated to the MCS. No family-wise claim can rest on a pairwise p-value alone.

## 2. The result under every plausible family (sensitivity, audit computation)

The test is UNRATE, h=1, absolute loss, STAR versus AR: HLZ statistic +5.49, two-sided p = 0.0015, n = 703. STAR has the higher loss.

| Family | Tests | Holm-adjusted p |
|---|---|---|
| STAR vs AR, all series, horizons and losses (ChatGPT's family) | 44 | 0.066 |
| MSAR or STAR vs AR | 90 | 0.135 |
| All AR-benchmark pairs | 136 | 0.200 |
| All primary HLZ tests in T3.3A | 226 | 0.330 |
| UNRATE, all horizons and losses, five pairs | 40 | 0.060 |
| STAR vs AR at h=1 (6 series × 2 losses) | 12 | 0.018 |
| UNRATE h=1, both losses, five pairs | 10 | 0.015 |
| UNRATE h=1 absolute, five pairs | 5 | 0.0075 |

The result survives only within families confined to a single cell: one target, horizon, or horizon and loss. No such family is predeclared. Choosing one after seeing the result would be selective. Under every family that spans the design's targets or horizons, it does not survive at 5%.

## 3. The predeclared multiple-model procedure

In the corrected T3.4, at UNRATE h=1 under absolute loss, **STAR remains in both the 90% and the 95% MCS** (MCS p-value 0.20). AR, ARMA and MSAR are retained as well. The MCS therefore does not exclude STAR.

## 4. Permitted wording

> "At the one-month horizon for unemployment, STAR's mean absolute loss exceeds AR's (HLZ p = 0.0015, nominal). This is a single nominal rejection among the 44 STAR-versus-AR comparisons: it does not survive a Holm adjustment across those tests (adjusted p ≈ 0.07), and STAR is retained in the 90% and 95% model confidence sets. It is reported as nominal evidence against STAR at this horizon, not as a family-wise result."

The same discipline applies to the other new nominal rejections, all of which go against STAR:

- DM-HLN at UNRATE h=3 under absolute loss (HLZ, the primary test, p = 0.057);
- the T4.4, T4.5 and T4.8 rows that reuse the h=1 comparison.

The CPI h=12 multiplicity qualification is unchanged. MSAR versus AR under absolute loss has p = 0.0044, with Holm-adjusted p = 0.204 within the 46 MSAR-vs-AR tests (squared loss: 1.0). Under the broader families it is 0.395 (90 tests) and 0.959 (226 tests).
