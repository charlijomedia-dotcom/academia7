# Part 5: Methodology versus jury matrix

**Date:** 5 October 2026  
**Status:** PROPOSED FOR USER APPROVAL

| Jury ID | Part 5 methodological response | Required evidence/output |
|---|---|---|
| R1-06 | Predeclared failure classes and failure-aware figure rules | Failure registry; readable forecast plots; separate extreme-model panel |
| R1-07 | 95% bands on any retained cross-correlation figure | Figure with confidence bands or no cross-correlation figure |
| R1-09 | “Better” defined by RMSE/MAE/OOS R² plus formal predictive tests | Main forecast table + test table |
| R1-10 | Discrete MS state dependence separated from smooth STAR state dependence | Chapter 2 taxonomy + model equations |
| R1-11 | First-order Markov chain, transition matrix, occupancy, duration, persistence explicitly reported | Transition/regime table |
| R1-12 | Frozen data dictionary with IDs, units, dates, transformations, rationale | Data audit table |
| R1-13 | Every diagnostic table states H0, statistic, distribution/bootstrap, p-value, rule | Standardized diagnostics table |
| R1-14 | DM-HLN + Model Confidence Set; explicit explanation for not mechanically using Clark-West/Amisano-Giacomini | Forecast-comparison section |
| R1-15 | BIC lag selection + CPI p=1/3/6/12 robustness | CPI lag-robustness table/plot |
| R1-17 | MS convergence, occupancy, transition boundaries, durations, policy-rate diagnostic block | MS credibility table + failure flags |
| R1-18 | LST/Teräsvirta STAR linearity test + bootstrap AR-vs-MSAR LR before nonlinear interpretation | Nonlinearity table |
| R1-19 | Monthly five-variable VAR robustness | VAR forecast comparison on common sample |
| R1-20 | Nowcasting explicitly outside core; no claim that native-frequency forecasting is nowcasting | Scope subsection |
| R1-22 | Entire empirical set regenerated from frozen data, with all failures visible | Part 8 audit |
| R1-23 | M2SL exact raw/transformed dates printed from frozen data | Data audit; M2 note |
| P-01 | Single-equation identification limit + VAR alternative-explanation check | VAR results + explicit limitation |
| P-02 | ADF + KPSS + Zivot-Andrews decision rule for UNRATE/FEDFUNDS | Stationarity table + break plot |
| P-03 | Policy-rate transformation and MS credibility separated into diagnostic stages | Dedicated policy-rate diagnostic output |
| P-04 | Mandatory K=3 MSAR robustness | K=2/K=3 comparison |
| P-05 | h=1 baseline plus longer horizons | Horizon-robustness table |
| P-06 | No universal model-ranking claim; U.S.-specific output framing | Final claims classification |

## Prof. Verne constraints carried into methodology

| Verne ID | Methodological response |
|---|---|
| V-04 | AR + ARMA as classical mean benchmarks; ARCH/GARCH treated where conditional heteroskedasticity is empirically present; polynomial exclusion explained |
| V-05 | Recession, expansion, peak, trough, and turning-point evaluation in main forecast outputs |
| V-06 | In-sample adequacy and diagnostics appear before OOS forecast ranking |
| V-07 | Output structure is designed so Part 9 can synthesize theoretical and empirical findings directly |

## Part 1 methodological lessons carried forward

- P1-03: each method has a stated problem it solves.
- P1-07: each test/model links to a research subquestion.
- P1-09: adverse and failed results stay visible.
- P1-10: each robustness exercise is tied to a named threat.
- P1-11: decisive evidence stays in main text, repetitive detail moves to appendices.
- P1-17: every numerical claim must trace to a reproduced output.
