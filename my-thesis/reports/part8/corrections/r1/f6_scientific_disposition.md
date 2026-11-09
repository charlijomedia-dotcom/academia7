# F6: final scientific disposition (9 November 2026)

**Disposition.** The published UNRATE K=3 result is **retained as INCONCLUSIVE**.
- No optimisation is re-run, and the approved MSAR multistart rule (Part 5) is unchanged.
- **P-04 remains PARTIALLY ADDRESSED.** Claims P04-regime-count and C18 stay QUALIFIED.

## 1. The nesting inconsistency

- K=3 nests K=2: a third regime that is never visited reproduces the K=2 model. So the maximised K=3 log-likelihood can never be below the K=2 one.
- Yet the published UNRATE fit (T4.3) has log-likelihood **13.88 for K=3 and 102.04 for K=2**, a difference of −88.16.
- The published K=3 estimate is therefore not the K=3 maximum. It is a local optimum reached from the two approved deterministic starts.
- Consequences:
  - the K=2-versus-K=3 information-criterion comparison for UNRATE (ΔBIC +210.5 "favouring" K=2) is **invalid**;
  - the comparison is reported as INCONCLUSIVE, not as evidence for K=2.

## 2. Local optima

The read-only feasibility study (`corrections/f6_k3_nesting_feasibility.csv`) built a nesting-informed start, the K=2 optimum plus an unvisited third regime. Through the existing `warm_start` argument it reached:
- **UNRATE K=3: 101.53**, i.e. 0.10 below K=2 rather than 88 below. That is still not exactly nested, so it is still not shown to be the maximum;
- **INDPRO K=3: −3550.31**, against the published −3563.27.

The other targets' K=3 optima were reproduced, up to 3×10⁻⁴.

**What this shows.** The MSAR likelihood is multimodal, and the 2-start rule can stop at clearly inferior local optima. The same holds for the rolling estimates: B2's 29 optimiser sensitivities and 20 classification changes (`b2_scientific_adjudication.md`).

**Why it is not adopted.** The nesting-informed start was never approved. Adopting it now would change an approved estimation rule after seeing results (CLAUDE.md §4, §6). It is not adopted.

## 3. Platform sensitivity

Refitting the full-sample MSAR with unchanged code on a different platform gave different K=2 optima for three targets:

| Target | Published K=2 | Refit K=2 |
|---|---|---|
| INDPRO | −3614.10 | −3627.97 |
| M2SL | −2203.65 | −2185.27 |
| UNRATE | 102.04 | 101.63 |

- Under the 2-start rule, the optimum reached depends on the floating-point platform.
- The T3.1, T3.2 and T4.3 MSAR numbers are therefore reproducible on the publication's platform class only. The archived candidate keeps the published values, and they are untouched by the integration.
- This is stated as a limitation, not corrected.

## 4. Limits on regime interpretation

- **No global maximum is claimed** for any MSAR estimate: full-sample, rolling, K=2 or K=3.
- **Regime parameters are descriptive of a local optimum.** Durations, occupancies and means cannot be read as the regimes of the data-generating process. This is especially true where they hinge on one to three observations (GDPC1, INDPRO, M2SL) or on unidentified parameters (FEDFUNDS, F5).
- **K=3 is assessed in-sample only.** It was never forecast.
  - "K=3 not credible" (T4.3C) remains a statement about the estimates obtained.
  - For UNRATE even that statement concerns a non-global optimum.
- The CPI high-inflation regime (C10) is the only interpretable regime. It too remains descriptive, with no causal or economic label (Part 5 §11.1).

## 5. Where this is recorded

| Report draft | Where |
|---|---|
| `full_empirical_analysis_report.md` | H0 "F6" and H.4–H.5 |
| `robustness_findings.md` | T4.3 |
| `jury_resolution_status.md` | P-04 |
| `final_claims_allowed.md` | C18 and P04-regime-count |
| `claim_evidence_matrix_candidate.csv` | the P04-regime-count and C18 rows |

No numerical result changes.
