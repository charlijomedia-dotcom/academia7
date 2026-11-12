# Part 9 | Section-Level Evidence Map

**Created:** 12 November 2026. **Status:** Controlling drafting map, not new empirical results.  
**Structure:** Approved Part 4 `part4_proposed_thesis_structure.md` (43 numbered sections).  
**Numerical source:** `my-thesis/output/`, commit `9817daf91ac4cb4aaa42c2bef5deaff5b674841b`, final release `part8-final-20261109` (465 inventoried files).  
**Claim/interpretation source:** Part 8 final documents, commit `00564283fe861468f4e67e0a3b77425b260d56f9`, not the preliminary result branches.  
**Companions:** `WRITING_BLUEPRINT.md` and `APA_SOURCE_REGISTER.md` in `my-thesis/reports/part9/`.

## 1. Editorial contract

**Shortest defensible body.** Target the 55–65-page body in the writing blueprint, excluding bibliography and appendices. Keep in-sample adequacy, necessary model/test equations, the negative baseline result, key robustness evidence, F6 limitations and jury-critical findings in the body. Move complete target-by-target tables, code traces, residuals, optimizer details and exhaustive plots to appendices. Four chapter-ending syntheses each occupy one page and add no new evidence.

**Every claim has one main home.** The final matrix contains **24 entries: 13 SUPPORTED, 8 QUALIFIED, 3 NOT_SUPPORTED**. Each appears once in the primary claim column below. Cross-reference other sections without reprinting results. `C01` non-rejection is not forecast equivalence; `C02` and `C16` require their limitations; `C12` nonlinear state advantage is not supported; `P04-regime-count` remains inconclusive for UNRATE.

**Version discipline.** The tables and figures linked below are **the released files**. This document does not create new results or change Part 5. When building a smaller composite thesis table from multiple output files, independently check each quoted number against the final release. External studies and APA citations are in the separate Source Register.

**Out-of-scope old mathematics:** remove the old MSSTAR-specific theorem/proposition. Define the retained MSAR/STAR models and Markov-chain terms in the body, with proper attribution. No model superiority or policy causality is implied by presenting a mathematical specification.

## 2. Minimal exhibits for the thesis body

| Location | Essential main-body material | Appendix material |
|---|---|---|
| General Introduction and Chapter 1 | Joseph narrative and documented forecasting failures; essential economic theory, no new Part 8 table | Context/background notes only if necessary |
| Chapter 2 | One condensed six-target data table, one compact methodological/robustness design chart, essential equations and test hypotheses | Frozen-data audit, full decision tables, parameter grids, estimation calendars, software provenance |
| Chapter 3 | Compact pre-test, in-sample fit, K2 credibility, baseline forecast/inference and recession/turning findings; at most one informative regime figure | All target/model residuals, horizon rows, supplementary F3.1–F3.6 panels and full model test tables |
| Chapter 4 | Compact transformation/CPI lag, K3, horizon/VAR and fragility summaries; use a corrected F8 figure to illustrate an extreme STAR failure | Full T4.1–T4.9 results, all individual F4.3/F4.8 figures, 34,122 event registry and computation appendix |
| General Conclusion | Direct answer to the question, no new table | No new tests |

## 3. General Introduction: scientific evidence route

**Sequence:** Joseph and Pharaoh as a narrative illustration (Douay–Rheims, Genesis 41) → independently documented contemporary forecast errors → economic stakes without an unsupported causal claim → earlier literature on linear and nonlinear forecasting → bounded U.S. question and contributions → verified `C01/C02/C04` headline → Part 4 chapter roadmap. **Citations:** APA Source Register, not GitHub data outputs. **Jury:** R1-01, V-02/V-03, P-06. **Avoid:** calling Joseph's account the historically first macroeconomic policy or claiming that forecast error alone caused a recession or wage loss.

## 4. The 43 approved sections: work, evidence and placement

**Codes** below resolve to validated `my-thesis/output/` files in §6. A dash means a section presents theory, designs an experiment, or synthesizes results without introducing a new numerical exhibit. The last column is an editorial rule, not a license to omit contrary evidence.

### Chapter 1

| Approved Part 4 subsection | Required content and exact evidence keys | Primary claim(s) | Placement and caveat |
|---|---|---|---|
| **1.1 Forecasting as a policy problem under inflation, conflict, debt pressure, and cyclical instability** | Introduce the policy problem; Joseph and contemporary official forecast errors from the APA register. No causal loss claim. Evidence: —. | — | Narrative only; no Part 8 table. |
| **1.2 Fisherian relations between inflation, nominal rates, real rates, and expectations** | State the Fisher relation; define terms, assumptions and role of expectations. Evidence: —. | — | One essential equation in body. |
| **1.3 Phillips-Phelps and Okun mechanisms linking inflation, unemployment, and output** | State Phillips–Phelps and Okun links, with instability caveats. Evidence: —. | — | Only essential equations; no empirical pseudo-causality. |
| **1.4 Money, monetary transmission, and competing macroeconomic traditions** | Explain money, rates, monetary transmission and why M2 is retained. Evidence: `D0`. | — | Theory; avoid extra target tables. |
| **1.5 Schumpeterian disruption, structural change, and turning points** | Define shocks, structural change and turning points; distinguish real-time information from ex-post NBER dates. Evidence: —. | — | Short discussion and original studies. |
| **1.6 From economic instability to statistical state dependence** | Distinguish structural breaks, latent states, smooth transitions and asymmetry. Evidence: `TSAY`, `STARTEST`. | — | Definitions, not Part 8 test results. |
| **1.7 What the theoretical and empirical literature already knows, and what remains unresolved** | Review prior AR/ARMA/MSAR/STAR and modern nonlinear/VAR work; identify gap. Evidence: —. | — | Use APA_SOURCE_REGISTER.md, no literature inventory. |
| **1.8 Testable implications, competing explanations, and evidence that would contradict the argument** | Present pre-specified falsifiers: better classical model, unstable regimes, no OOS gain, regime failures. Evidence: —. | — | No results revealed early. |
| **1.9 Chapter 1 Concluding Synthesis: From macroeconomic mechanisms to a testable forecasting problem** | One-page synthesis of economic mechanisms and unresolved question. Evidence: —. | — | One page, no new evidence. |

### Chapter 2

| Approved Part 4 subsection | Required content and exact evidence keys | Primary claim(s) | Placement and caveat |
|---|---|---|---|
| **2.1 From the Chapter 1 mechanisms to an empirical identification strategy** | Define what a forecast comparison can and cannot identify. Evidence: —. | — | No causal policy inference. |
| **2.2 Data, aggregate selection, exact samples, and frozen-vintage policy** | Document six targets, USREC, samples, date endpoints, two LOCF imputations and frozen vintage. Evidence: `D0`, `D1`, `GAP`, `IMPUTE`, `SAMPLEFIG`. | — | One compact six-target table; full data dictionary/figure in appendix. |
| **2.3 Stationarity, persistence, and structural-break evidence before model specification** | Define ADF, KPSS and ZA, initial-window decision, full-sample check. Evidence: `STATION`, `TRANSDEC`, `UNRATEFIG`, `FUNDSFIG`. | — | Test equations/decision rule in body; detailed tests in appendix. |
| **2.4 Testing for nonlinearity before nonlinear interpretation** | Specify Tsay and STAR linearity testing; state what rejection does not prove. Evidence: `TSAY`, `STARTEST`. | — | Main text hypotheses; results in §3.1. |
| **2.5 Classical forecasting benchmarks and what each benchmark tests** | Define AR/ARMA and BIC; explain conditional variance treatment and polynomial exclusion. Evidence: `SPECS`, `ARCH`. | — | Essential benchmark equations. |
| **2.6 State-dependent alternatives and their economic interpretation** | Define Hamilton-style K2 MSAR, Markov chain, transition probabilities, STAR and estimation guards. Evidence: `REG`, `K3`. | — | Essential mathematics in body; remove old MSSTAR theorem. |
| **2.7 Cross-variable information and the boundary of single-equation forecasting** | Explain limited univariate scope, monthly 5-var VAR and mixed-frequency boundary. Evidence: `VARS`. | — | VAR equation, no invented monthly GDP. |
| **2.8 In-sample model adequacy as a prerequisite for forecast interpretation** | Define adequacy and residual criteria before forecast ranking. Evidence: `FIT`, `RESID`. | — | Gate only; fit evidence in §3.2. |
| **2.9 Forecast experiment: origins, windows, horizons, and re-estimation policy** | Define origins, frozen rolling windows, horizon refits, common information set. Evidence: `SPECS`, `SAMPLEFIG`. | — | Short schematic; full calendars appendix. |
| **2.10 Forecast evaluation across normal periods, recessions, expansions, peaks, and troughs** | Define RMSE/MAE/OOS R2, HLZ primary, DM-HLN secondary, MCS and GW state regressions. Evidence: `FORE`, `HLZ`, `DM`, `MCS`, `STATE`, `GW`. | — | Necessary null hypotheses and interpretation in body. |
| **2.11 Model admissibility and failure rules** | Define adequate/fragile/failed, warning thresholds and scored-forecast retention. Evidence: `FITLOG`, `FAIL`, `STATUS`. | — | Brief protocol; raw failure registry appendix. |
| **2.12 Threat-based robustness plan** | Map robustness threats to checks; include 3,533→6 K3 calls calculation. Evidence: `ALT`, `LAGS`, `K3`, `HORIZ`, `VAR`, `ARCH`, `WINDOW`, `LOCF`. | — | One compact threat table and calculation, not runtime diary. |
| **2.13 Reproducibility and numerical traceability** | Document scientific pin, frozen data, output paths and checksum verification. Evidence: `D1`, `IMPUTE`. | — | Reproducibility paragraph; detailed hashes in appendix. |
| **2.14 Chapter 2 Concluding Synthesis: From diagnostic evidence to a credible forecast experiment** | One-page synthesis of empirically testable contract. Evidence: —. | — | No new result or equation. |

### Chapter 3

| Approved Part 4 subsection | Required content and exact evidence keys | Primary claim(s) | Placement and caveat |
|---|---|---|---|
| **3.1 Pre-estimation evidence and model eligibility** | Report stationarity/break/nonlinearity decision results; keep ZA disagreements visible. Evidence: `STATION`, `TRANSDEC`, `TSAY`, `STARTEST`, `SPECS`. | `C11` (SUPPORTED) | One compact pretest table. |
| **3.2 In-sample model adequacy and residual diagnostics** | Report model adequacy before the horse race; distinguish BIC from OOS loss. Evidence: `FIT`, `RESID`. | `C05` (SUPPORTED) | One adequacy table. |
| **3.3 Regime and parameter credibility for nonlinear models** | Report K2 regime credibility, CPI example, implausible policy-rate fits and STAR failures. Evidence: `REG`, `REGFIG`. | `C06` (SUPPORTED), `C09` (NOT_SUPPORTED), `C10` (QUALIFIED), `C22` (SUPPORTED) | One credibility table; optional CPI regime plot. |
| **3.4 Full-sample out-of-sample forecast performance against classical benchmarks** | Give baseline h1 RMSE/MAE/OOS R2 and HLZ inference, MCS as supporting check. Evidence: `FORE`, `HLZ`, `MCS`, `DM`. | `C01` (SUPPORTED), `C03` (QUALIFIED) | One consolidated forecast table. |
| **3.5 Forecast performance in expansions and recessions** | Report recession/expansion results and distinct joint-vs-slope GW significance. Evidence: `STATE`, `GW`. | `C12` (NOT_SUPPORTED) | Small state summary; full regressions appendix. |
| **3.6 Peaks, troughs, and turning-point forecasting** | Report peaks/troughs and turning-window sensitivity without declaring unique ±3-month rule. Evidence: `PEAK`, `TURN`. | — | Compact conclusion; detailed dates in appendix. |
| **3.7 Cross-aggregate synthesis: inflation, activity, labour-market and monetary evidence** | Synthesize target-specific patterns; note unemployment rank/sample effects. Evidence: `FORE`, `UNFORE`, `HLZ`. | `C21` (SUPPORTED) | One short cross-target paragraph, not six repetitions. |
| **3.8 What the baseline evidence establishes, and what remains vulnerable** | State precisely what h1 evidence supports, qualifies and rejects. Evidence: `FORE`, `HLZ`, `GW`. | `C04` (NOT_SUPPORTED) | No new table. |
| **3.9 Chapter 3 Concluding Synthesis: Where nonlinear complexity earns its place, if anywhere** | One-page synthesis of baseline answers and remaining threats. Evidence: —. | — | No new analysis. |

### Chapter 4

| Approved Part 4 subsection | Required content and exact evidence keys | Primary claim(s) | Placement and caveat |
|---|---|---|---|
| **4.1 From baseline result to falsification test: the threat-based robustness framework** | Apply baseline claim → threat → check → result → implication consistently. Evidence: —. | — | One roadmap sentence/table. |
| **4.2 Transformation, persistence, and structural-break threats** | Report transformations, persistence and October 2025 LOCF robustness. Evidence: `ALT`, `ALTT`, `STATION`, `LOCF`, `EXPOSURE`. | `C15` (SUPPORTED), `C20` (SUPPORTED) | One narrow summary; exposure data appendix. |
| **4.3 Lag structure, seasonality, and classical-benchmark misspecification** | Report CPI lag check and heteroskedasticity; explain no direct AR2/AR12 equivalence test. Evidence: `LAGS`, `LAGST`, `ARCH`, `GARCH`. | `C16` (QUALIFIED), `C19` (SUPPORTED) | Small CPI comparison only; GARCH supplementary. |
| **4.4 Two regimes or more? Testing the economic meaning of the latent-state structure** | Report six K2/K3 in-sample contrasts and UNRATE F6 inconclusive result. Evidence: `K3`, `K3PARAM`, `K3CONC`, `K3FIG`. | `P04-regime-count` (QUALIFIED), `C18` (QUALIFIED) | One small six-target table; full matrices and figure appendix. |
| **4.5 Does model ranking change with the forecast horizon?** | Report longer horizons and CPI h12 isolated nominal result. Evidence: `HORIZ`, `HORIZT`, `HLZ`. | `C02` (QUALIFIED), `C13` (QUALIFIED) | Compact horizon summary; Holm sensitivity labelled audit. |
| **4.6 Does cross-variable information explain what own-history nonlinearity seemed to capture?** | Assess cross-variable information and the narrow 5-variable VAR check. Evidence: `VAR`, `VART`, `VARS`. | `C17` (SUPPORTED) | One compact VAR comparison. |
| **4.7 Model fragility as evidence, not a technical footnote** | Treat optimizer fragility, STAR explosive forecasts and window-length sensitivity as substantive evidence. Evidence: `FAIL`, `STATUS`, `FITLOG`, `WINDOW`, `WINDOWT`, `WINDOWM`, `STARFIG`, `STARIND`, `UNFIG`, `WFIG`. | `C07` (SUPPORTED), `C08` (SUPPORTED), `C14` (SUPPORTED) | One failure table plus F8 CPI figure; remainder appendix. |
| **4.8 What nowcasting and mixed-frequency methods could answer that this design does not** | Explain why real-time vintages, nowcasting and mixed-frequency models address other questions. Evidence: —. | — | Brief boundary text, not unperformed experiments. |
| **4.9 What robust forecasting evidence means for inflation, unemployment, growth and monetary-policy decisions** | Discuss forecasting information for policy timing without assuming optimal policy changes. Evidence: `FORE`, `HLZ`, `GW`. | — | Bounded interpretation, no estimated welfare effect. |
| **4.10 U.S.-specific findings versus transferable forecasting discipline** | Separate U.S.-sample model ranks from transferable evaluation discipline. Evidence: `FORE`, `WINDOW`, `FAIL`. | `C23` (QUALIFIED) | One concise external-validity statement. |
| **4.11 Chapter 4 Concluding Synthesis: Which findings survive and what they mean for economics and policy** | One-page synthesis: what survives robustness and economic implications. Evidence: —. | — | No new result. |

### General Conclusion

Without adding results, answer whether added nonlinear state dependence improved prediction: **not generally at the baseline h=1**; nominal CPI h=12 evidence remains qualified by multiplicity; some in-sample fit gains coexist with weak regime credibility, optimizer sensitivity and explosive STAR forecasts. Distinguish predictive value from causal optimal-policy conclusions, and U.S.-specific rankings from transferable forecast-evaluation discipline. **Jury:** V-07, P-06. No new tables, tests or literature.

## 5. Final 24-claim primary section index

| Claim | Status | Primary § | Published evidence and bound on interpretation |
|---|---|---|---|
| `P04-regime-count` | QUALIFIED | §4.4 | Whether the two-regime MSAR assumption is overly restrictive, assessed by an in-sample comparison of full-sample K=2 and K=3 fits (regime credibility), not by a predictive-accuracy comparison (Part 5 §11.1, amended 29 October 2026). **Qualification:** F6: UNRATE K=3 is a non-global optimum, comparison INCONCLUSIVE; in-sample only, no forecasting implication. Final F6 disposition (9 Nov 2026): retained INCONCLUSIVE, no re-optimisation, nesting-informed start not adopted; platform-sensitive optima; regime parameters describe local o… |
| `C01` | SUPPORTED | §3.4 | No MSAR or STAR forecast significantly beats AR at h=1 under HLZ. **Qualification:** Non-rejection is absence of evidence of superiority, not equal accuracy; nominal p-values (no predeclared family). |
| `C02` | QUALIFIED | §4.5 | MSAR beats AR for CPI inflation at h=12. **Qualification:** Unadjusted 5% result; Holm-adjusted p 0.204 / 1.0 within the 46 MSAR-vs-AR tests [audit, not an approved output]; one robustness horizon. |
| `C03` | QUALIFIED | §3.4 | MSAR has the lowest h=1 RMSE for GDPC1 and INDPRO. **Qualification:** Descriptive ranking only; pandemic dependence; [audit] R2 not citable as thesis numbers. |
| `C04` | NOT_SUPPORTED | §3.8 | Nonlinear models outperform classical benchmarks (general claim). **Qualification:** — |
| `C05` | SUPPORTED | §3.2 | Nonlinear models fit better in-sample (BIC). **Qualification:** Fit statement only; for GDP, IP and M2 the MSAR gain comes from 1-3 pandemic observations. |
| `C06` | SUPPORTED | §3.3 | Full-sample K=2 regimes are credible only for CPI inflation. **Qualification:** No economic labels on statistical regimes. |
| `C07` | SUPPORTED | §4.7 | Rolling MSAR/STAR estimates are predominantly fragile. **Qualification:** "Predominantly" applies to the pooled estimates, not every chain: UNRATE MSAR is majority adequate (2,120 adequate, 1,380 fragile; baseline chain 258 fragile of 704). F6: no global maximum claimed; optimiser sensitivity reported. |
| `C08` | SUPPORTED | §4.7 | Rolling STAR is numerically unstable and forecasts explosively. **Qualification:** Numerical instability is not statistical evidence: degenerate tests carry no usable inference and support no affirmative claim, including "no significant difference". |
| `C09` | NOT_SUPPORTED | §3.3 | STAR captures a credible smooth transition. **Qualification:** — |
| `C10` | QUALIFIED | §3.3 | CPI two-regime model identifies a high-inflation state. **Qualification:** Descriptive; no causal or policy interpretation. |
| `C11` | SUPPORTED | §3.1 | Pre-estimation nonlinearity evidence is target-specific. **Qualification:** — |
| `C12` | NOT_SUPPORTED | §3.5 | Nonlinear gains concentrate in recessions or turning points. **Qualification:** Report joint and state-dependence Wald separately; a joint rejection is not state dependence; do not quote the auto-generated implication text or the FEDFUNDS ARMA h=6 state_dependence_supported_5pct flag (slopes p 0.082) unqualified; 15 STAR regressions degenerate. |
| `C13` | QUALIFIED | §4.5 | Longer horizons reveal no systematic nonlinear gain. **Qualification:** CPI h=12 exception; STAR tests at explosive horizons degenerate. |
| `C14` | SUPPORTED | §4.7 | Conclusions insensitive to predeclared window lengths. **Qualification:** UNRATE MSAR descriptive h=1 advantage not window-robust (OOS R2 0.240 / 0.190 / -1.102; rank 4 at 300; HLZ p 0.30-0.77). |
| `C15` | SUPPORTED | §4.2 | Conclusions insensitive to UNRATE/FEDFUNDS transformation. **Qualification:** Point rankings depend on the transformation; DM-HLN (secondary) rejects for FEDFUNDS-level ARMA (p 0.0076, ARMA better) and MSAR (p 0.029, MSAR worse; F1+B2 jointly, not decomposed). |
| `C16` | QUALIFIED | §4.3 | No evidence that the CPI 12-lag structure improves one-step forecasts over the BIC-selected AR(2). **Qualification:** No direct AR(2)-vs-AR(12) test and no equivalence test; samples differ (715 vs 714); ordering depends on the loss; nested models under a fixed rolling window. Allowed: "no evidence that 12 lags improve on AR(2)". Not allowed: "unnecessary", "as accurately as", "no benefit". |
| `C17` | SUPPORTED | §4.6 | VAR does not overturn univariate conclusions. **Qualification:** UNRATE VAR rank descriptive only; linear VAR is a limited multivariate response. |
| `C18` | QUALIFIED | §4.4 | No credible third regime; K=2 retained. **Qualification:** F6; K=2 not "validated" (weak for four targets); in-sample only. Final F6 disposition (9 Nov 2026): retained INCONCLUSIVE, no re-optimisation, nesting-informed start not adopted; platform-sensitive optima; regime parameters describe local optima (reports/part8/corrections/r1/f6_scien… |
| `C19` | SUPPORTED | §4.3 | Persistent conditional heteroskedasticity where ARCH-LM rejects. **Qualification:** Diagnostic only; no mean-forecast claim. |
| `C20` | SUPPORTED | §4.2 | October 2025 LOCF does not drive results. **Qualification:** Indirect exposure through estimation windows cannot be removed by dropping target dates. |
| `C21` | SUPPORTED | §3.7 | Unemployment forecast rankings and OOS R2. **Qualification:** Three metrics never merged; no claim of unequivocal MSAR superiority; no equivalence claim for ARMA vs MSAR (no test); ranking driven by target 2020-05; metric definitions unchanged; not window-robust (C14); pandemic dependence (MSAR R2 -0.010 without 2020-01 to 2021-06 [audit]). |
| `C22` | SUPPORTED | §3.3 | Policy-rate MSAR collapses to linear AR under differencing. **Qualification:** F5: automatic label remains fragile (interpretation only). |
| `C23` | QUALIFIED | §4.10 | Rankings are U.S.-specific; the design is transferable. **Qualification:** U.S.-specific rankings; no real-time or cross-country claim. |

Do not repeat claim text in multiple sections. Cross-reference the final `final_claims_allowed.md` for full allowed wording and `claim_evidence_matrix_final.csv` for all limitations and jury links. Specifically, UNRATE GW joint Wald rejection must not be reported as significance of the state slope, degeneracy is not a non-rejection, and OOS ranking comparisons must use the stated common valid dates.

## 6. Exact empirical source registry

All paths below were checked against the **465-file published release inventory**. Link labels refer to the **published empirical commit**, never the superseded `part8-r1-rescore` outputs.

| Key | Source path relative to `my-thesis/output/` | Suggested location |
|---|---|---|
| `D1` | [`data_audit/T2.1_data_dictionary.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/data_audit/T2.1_data_dictionary.csv) | Selected main-text or condensed evidence |
| `D0` | [`data_audit/T2.0_concept_series.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/data_audit/T2.0_concept_series.csv) | Appendix / verification |
| `GAP` | [`data_audit/data_gap_register.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/data_audit/data_gap_register.csv) | Appendix / verification |
| `IMPUTE` | [`data_audit/october_2025_imputation_audit.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/data_audit/october_2025_imputation_audit.csv) | Appendix / verification |
| `LOCF` | [`data_audit/T4.9_locf_sample_comparison.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/data_audit/T4.9_locf_sample_comparison.csv) | Appendix / verification |
| `EXPOSURE` | [`data_audit/locf_forecast_exposure.parquet`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/data_audit/locf_forecast_exposure.parquet) | Appendix / verification |
| `SAMPLEFIG` | [`figures/F2.0_sample_timeline.png`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/figures/F2.0_sample_timeline.png) | Appendix / verification |
| `UNRATEFIG` | [`figures/F2.1_UNRATE.png`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/figures/F2.1_UNRATE.png) | Appendix / verification |
| `FUNDSFIG` | [`figures/F2.1_FEDFUNDS.png`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/figures/F2.1_FEDFUNDS.png) | Appendix / verification |
| `STATION` | [`diagnostics/T2.2_stationarity.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/diagnostics/T2.2_stationarity.csv) | Selected main-text or condensed evidence |
| `TRANSDEC` | [`diagnostics/T2.2_transformation_decisions.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/diagnostics/T2.2_transformation_decisions.csv) | Selected main-text or condensed evidence |
| `TSAY` | [`diagnostics/T2.3_tsay.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/diagnostics/T2.3_tsay.csv) | Selected main-text or condensed evidence |
| `STARTEST` | [`diagnostics/T2.4_star_linearity.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/diagnostics/T2.4_star_linearity.csv) | Selected main-text or condensed evidence |
| `SPECS` | [`diagnostics/T2.5_selected_specs.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/diagnostics/T2.5_selected_specs.csv) | Appendix / verification |
| `RESID` | [`diagnostics/T3.2_residual_tests.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/diagnostics/T3.2_residual_tests.csv) | Appendix / verification |
| `FIT` | [`models/T3.1_in_sample_adequacy.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/models/T3.1_in_sample_adequacy.csv) | Selected main-text or condensed evidence |
| `REG` | [`models/T3.2_nonlinear_credibility.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/models/T3.2_nonlinear_credibility.csv) | Selected main-text or condensed evidence |
| `FITLOG` | [`models/fit_records.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/models/fit_records.csv) | Appendix / verification |
| `REGFIG` | [`figures/F3.3_CPIAUCSL_MSAR.png`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/figures/F3.3_CPIAUCSL_MSAR.png) | Selected main-text or condensed evidence |
| `FORE` | [`forecast_tests/T3.3_main_forecast_table.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/forecast_tests/T3.3_main_forecast_table.csv) | Selected main-text or condensed evidence |
| `HLZ` | [`forecast_tests/T3.3A_hlz_pairwise.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/forecast_tests/T3.3A_hlz_pairwise.csv) | Selected main-text or condensed evidence |
| `DM` | [`forecast_tests/T3.3B_dm_hln_pairwise.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/forecast_tests/T3.3B_dm_hln_pairwise.csv) | Appendix / verification |
| `MCS` | [`forecast_tests/T3.4_model_confidence_set.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/forecast_tests/T3.4_model_confidence_set.csv) | Selected main-text or condensed evidence |
| `STATE` | [`forecast_tests/T3.5_state_performance.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/forecast_tests/T3.5_state_performance.csv) | Selected main-text or condensed evidence |
| `GW` | [`forecast_tests/T3.5_state_loss_regression.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/forecast_tests/T3.5_state_loss_regression.csv) | Selected main-text or condensed evidence |
| `PEAK` | [`forecast_tests/T3.6_peak_trough_detail.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/forecast_tests/T3.6_peak_trough_detail.csv) | Appendix / verification |
| `TURN` | [`robustness/T4.TP1_turning_window_sensitivity.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/T4.TP1_turning_window_sensitivity.csv) | Appendix / verification |
| `STARFIG` | [`figures/F3.4_CPIAUCSL.png`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/figures/F3.4_CPIAUCSL.png) | Selected main-text or condensed evidence |
| `STARIND` | [`figures/F3.4_INDPRO.png`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/figures/F3.4_INDPRO.png) | Appendix / verification |
| `UNFIG` | [`figures/F3.4_UNRATE.png`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/figures/F3.4_UNRATE.png) | Appendix / verification |
| `ALT` | [`robustness/T4.1_transformation_robustness.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/T4.1_transformation_robustness.csv) | Appendix / verification |
| `ALTT` | [`robustness/T4.1_transformation_predictive_tests.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/T4.1_transformation_predictive_tests.csv) | Appendix / verification |
| `LAGS` | [`robustness/T4.2_cpi_lag_robustness.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/T4.2_cpi_lag_robustness.csv) | Appendix / verification |
| `LAGST` | [`robustness/T4.2_cpi_lag_predictive_tests.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/T4.2_cpi_lag_predictive_tests.csv) | Appendix / verification |
| `K3` | [`robustness/T4.3_regime_count.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/T4.3_regime_count.csv) | Selected main-text or condensed evidence |
| `K3PARAM` | [`robustness/T4.3_regime_parameters.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/T4.3_regime_parameters.csv) | Appendix / verification |
| `K3CONC` | [`robustness/T4.3_regime_count_conclusion.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/T4.3_regime_count_conclusion.csv) | Selected main-text or condensed evidence |
| `K3FIG` | [`figures/F4.3_UNRATE_MSAR3.png`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/figures/F4.3_UNRATE_MSAR3.png) | Appendix / verification |
| `HORIZ` | [`robustness/T4.4_horizon_robustness.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/T4.4_horizon_robustness.csv) | Appendix / verification |
| `HORIZT` | [`robustness/T4.4_horizon_predictive_tests.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/T4.4_horizon_predictive_tests.csv) | Selected main-text or condensed evidence |
| `VAR` | [`robustness/T4.5_var_comparison.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/T4.5_var_comparison.csv) | Selected main-text or condensed evidence |
| `VART` | [`robustness/T4.5_var_predictive_tests.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/T4.5_var_predictive_tests.csv) | Appendix / verification |
| `VARS` | [`robustness/T4.5_var_selection.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/T4.5_var_selection.csv) | Appendix / verification |
| `ARCH` | [`robustness/T4.6_arch_trigger.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/T4.6_arch_trigger.csv) | Appendix / verification |
| `GARCH` | [`robustness/T4.6_arma_garch_summary.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/T4.6_arma_garch_summary.csv) | Appendix / verification |
| `FAIL` | [`robustness/T4.7_failure_registry.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/T4.7_failure_registry.csv) | Appendix / verification |
| `STATUS` | [`robustness/T4.7_status_counts.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/T4.7_status_counts.csv) | Selected main-text or condensed evidence |
| `WINDOW` | [`robustness/window_length_comparison.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/window_length_comparison.csv) | Appendix / verification |
| `WINDOWT` | [`robustness/window_length_predictive_tests.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/window_length_predictive_tests.csv) | Appendix / verification |
| `WINDOWM` | [`robustness/window_length_mcs.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/robustness/window_length_mcs.csv) | Appendix / verification |
| `WFIG` | [`figures/F4.8_UNRATE.png`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/figures/F4.8_UNRATE.png) | Appendix / verification |
| `UNFORE` | [`forecasts/forecasts_UNRATE.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/forecasts/forecasts_UNRATE.csv) | Appendix / verification |
| `CPIFORE` | [`forecasts/forecasts_CPIAUCSL.csv`](https://github.com/charlijomedia-dotcom/academia7/blob/9817daf91ac4cb4aaa42c2bef5deaff5b674841b/my-thesis/output/forecasts/forecasts_CPIAUCSL.csv) | Appendix / verification |

## 7. Appendix architecture and computation

**Appendix A, data and diagnostics:** full T2.0–T2.5, historical-vintage policy, canonical input and two October 2025 LOCF cells, NBER state definitions, model equations too detailed for the main text. No obsolete MSSTAR theorem.

**Appendix B, estimation and forecast output:** T3.1–T3.6 complete, nonlinearity and residual screens, selected parameter matrices, all horizon/target comparisons and verified figure panels. The body must still identify the main negative finding.

**Appendix C, robustness and fragility:** T4.1–T4.9 full results, K3 in-sample parameter matrices and F4.3 plots, window-length F4.8, corrected F3.4 alternate panels, T4.7 reason-code registry, LOCF exposure.

**Appendix D, computational workload and corrections:** report actual fits attempted by model/series, runtime where recorded, memory/CPU platform and configuration, 3,527 avoided rolling K3 origins, caching/warm starts, a short original-methodology vs approved-amendment vs implementation-correction table, and unresolved F6. Link full code/logs instead of reproducing them.

**The K3 arithmetic:** originally 3,527 rolling fits plus six full-sample fits equals 3,533; approved revised exercise requires six in-sample fits. Thus 3,527 fits avoided, or **99.83% fewer K3 estimation calls**. This is **not** a 99.83% CPU-time saving, nor evidence that K3 forecasts worse. No K3 out-of-sample forecasts exist or may be claimed.

**The T4.7 arithmetic:** 34,122 **reason-code events**, comprising **512 FAILED and 33,610 FRAGILE events**. An event is not a unique failed fit. The original computation report separately records 67,253 fit records; do not combine these denominators without provenance.

**Brief body-level correction account:** Part 5 and its authorized amendments determine the actual design. The run revealed F1 failed-fit scoring, F2 guarded MCS, F3 sign orientation, F4 omitted ZA diagnostics, F7.1 metadata and F8 readability issues; they were corrected and validated without changing unapproved model specifications. F6 MSAR global-optimum uncertainty remains explicit, not fixed by quietly optimizing again. Do not turn the thesis into an execution diary.

## 8. Jury compliance index

The **29 Part 2 jury remarks** must be answered in prose, not merely listed. Their prescribed primary locations are:

- **R1-01:** Introduction; global structure.
- **R1-02:** Global manuscript proofreading.
- **R1-03:** Front matter, first-use acronyms.
- **R1-04:** Global notation and symbol register.
- **R1-05:** 2.6.
- **R1-06:** 4.7.
- **R1-07:** 3.6 (only if a cross-correlation figure remains).
- **R1-08:** 1.2–1.4; 2.6.
- **R1-09:** 2.10; 3.4.
- **R1-10:** 1.6.
- **R1-11:** 2.6, textual part still required in Part 9.
- **R1-12:** 2.2.
- **R1-13:** 2.3–2.4; 2.10.
- **R1-14:** 2.10; 3.4–3.6.
- **R1-15:** 4.3.
- **R1-16:** 2.10; global table notation.
- **R1-17:** 3.3; 4.4; 4.7.
- **R1-18:** 2.4; 3.1.
- **R1-19:** 2.7; 4.6.
- **R1-20:** 2.7; 4.8.
- **R1-21:** 1.7; global brevity.
- **R1-22:** 3.4; 4.7.
- **R1-23:** 2.2; 1.4.
- **P-01:** 2.1; 2.7; 4.6.
- **P-02:** 2.3; 3.1; 4.2.
- **P-03:** 3.3; 4.2.
- **P-04:** 2.12; 4.4.
- **P-05:** 2.9; 4.5.
- **P-06:** 4.10; conclusion.

**V-01–V-08 (Professor Verne):** preserve the two-part four-chapter monograph; give essential economic motivation; link to policy relevance; use disciplined classical benchmarks; analyze recession/peak/trough states; enforce adequacy before forecasting; make the General Conclusion directly answer the problématique; keep chapter titles scientific.

**Two accepted partial scientific statuses:** R1-11 (the model/Markov-chain *exposition* still belongs to Part 9) and P-04 (the K3 UNRATE F6 comparison is inconclusive). Neither is grounds for unapproved re-estimation. R1-05, R1-08 and R1-11 require clear mathematical definitions in the body. R1-07 applies only if an actual cross-correlation graphic is retained.

## 9. Every-section pre-publication gate

Before a section is accepted: (1) it does its specific Part 4 job; (2) all economic theory, statistical tests and equations are clearly defined and attributed in APA 7; (3) every number comes from released `my-thesis/output/` at `9817daf91ac4cb4aaa42c2bef5deaff5b674841b`; (4) each claim respects final Part 8 support status, multiplicity, sample, optimizer and real-time limitations; (5) the essential adverse findings remain visible; (6) the mapped jury item has been answered; (7) no old MSSTAR theorem, unfounded Joseph-first claim, optimal-policy causal conclusion or general U.S.-to-world model ranking appears; (8) the text is short, clear, objective and dense in information; (9) chapter-enders add no new arguments or evidence.

**Next work after Step 3:** write the General Introduction from the APA register and this map, then validate it paragraph by paragraph. No new Colab work or code review is authorized or necessary.
