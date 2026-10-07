# Part 9: Recent Q1 literature bank for final thesis writing

**Project:** *Forecasting Macroeconomic Aggregates under Economic Instability: Theory, Nonlinearity, and Policy Implications*  
**Date:** 6 October 2026  
**Status:** WORKING LITERATURE BANK FOR PART 9, NOT FINAL THESIS TEXT  
**Primary use:** General Introduction, Chapter 1 literature/problem framing, Chapter 2 methodology justification, Chapters 3–4 result interpretation, General Conclusion  
**Research rule:** Do not cite a paper merely because its result is convenient. Use the paper only where its research question, method, or empirical finding actually bears on the thesis claim being discussed.

---

# 0. Mandatory source files for Part 9 writing

Part 9 must not rely on this recent-literature bank alone.

For every methodology paragraph in the final thesis, Part 9 must also consult:

- `part5_methodology_literature_justification.md` for the decision-by-decision academic justification of the methodology;
- `part5_methodology_specification.md` for the exact approved implementation;
- `part5_methodology_decision_log.md` for the reason each major choice was retained or rejected;
- `part5_data_selection_retrieval_reproducibility_rationale.md` for country, series, sample, transformation, and reproducibility arguments.

The Part 5 literature-justification file is the main source of the agreed methodological citations, including:

- ADF, KPSS, and Zivot-Andrews for stationarity and breaks;
- BIC for lag/order selection;
- Tsay and Luukkonen-Saikkonen-Teräsvirta/Teräsvirta for nonlinearity and STAR specification;
- Hamilton, Cho-White, and Qu-Zhuo for Markov-switching design and testing limits;
- Engle and Bollerslev for ARCH/GARCH;
- Pesaran-Timmermann and Rossi-Inoue for rolling/window issues;
- Marcellino-Stock-Watson for pseudo-out-of-sample and multi-horizon forecasting;
- Harvey-Leybourne-Zu, DM-HLN, Giacomini-White, and Hansen-Lunde-Nason for forecast comparison;
- Clark-West and Amisano-Giacomini for explicit exclusion logic;
- Sims for the VAR robustness block;
- Giannone-Reichlin-Small for the nowcasting boundary;
- Chauvet-Piger, Li-Sheng-Yang, Stock-Watson (2014), Hamilton (2011), and Berge-Jordà for the turning-point-window rationale.

Part 9 must use those citations where the corresponding methodological choice is explained. It must not replace them with uncited general statements.

---

# 1. Selection rule

This bank prioritizes research that satisfies most or all of the following:

1. published mainly from 2022–2026, with a small number of 2020–2021 bridge papers where especially close to the thesis;
2. peer-reviewed;
3. published in journals currently indexed in Scopus and ranked Q1 by SCImago in a relevant economics/econometrics, statistics, forecasting, or closely related category;
4. directly concerned with macroeconomic forecasting, nonlinear/state-dependent dynamics, instability, forecast evaluation under instability, multivariate forecasting, turning points/recessions, inflation, real activity, or policy-rate nonlinearities;
5. useful for a specific section or result in Part 9.

Current Q1 status is a **journal-level current classification**, not a claim that the journal had the same quartile in the historical publication year.

Core Q1 venues used here include:

- *Journal of Econometrics*;
- *Journal of Applied Econometrics*;
- *Journal of Business & Economic Statistics*;
- *Review of Economics and Statistics*;
- *Quantitative Economics*;
- *Journal of Monetary Economics*;
- *International Journal of Forecasting*;
- *Annals of Applied Statistics* for one closely relevant statistical forecasting paper.

The literature bank separates:

- **direct papers**, which closely address the thesis problem;
- **adjacent papers**, which help interpret a specific methodological or empirical issue;
- **bridge papers**, which are slightly older but remain unusually close to the thesis's model families.

---

# 2. Highest-priority papers: closest to the thesis

## A1. Clark, Huber, and Koop (2026), nonlinear macroeconomic VARs

**Citation**

Clark, T. E., Huber, F., & Koop, G. (2026). A flexible approach to augmenting a Bayesian VAR with nonlinear factors. *Journal of Business & Economic Statistics*. Advance online publication. https://doi.org/10.1080/07350015.2026.2703238

**Why this is highly relevant**

This is one of the most recent high-level papers directly studying nonlinear macroeconomic forecasting in U.S. data. It augments a VAR with parsimonious nonlinear factors estimated using regression trees. The authors explicitly frame the model as balancing nonlinear flexibility against over-parameterization, misspecification, and computation.

Their empirical U.S. application includes real GDP, unemployment, inflation, the federal funds rate, industrial production, and other macro-financial series. They report that nonlinear corrections are generally small in normal periods but become more important around NBER recessions, especially for real activity. Their forecasting application reports noticeable out-of-sample density-forecast gains over a linear BVAR.

**Use in Part 9**

- General Introduction: modern evidence that nonlinear macro dynamics remain an active forecasting problem.
- Chapter 1: instability/recession motivation.
- Chapter 2: modern justification for keeping nonlinear structure parsimonious rather than maximizing complexity.
- Chapter 4: multivariate robustness and comparison with recent nonlinear VAR work.
- Conclusion: evidence that nonlinear components may be state-specific rather than universally dominant.

**Do not claim**

Do not say this paper validates MSAR or STAR specifically. It validates the broader relevance of nonlinear macroeconomic forecasting and parsimonious nonlinear multivariate structure.

**Relevance:** VERY HIGH.

---

## A2. Harvey, Leybourne, and Zu (2025), forecast comparison under instability

**Citation**

Harvey, D. I., Leybourne, S. J., & Zu, Y. (2025). Testing for equal average forecast accuracy in possibly unstable environments. *Journal of Business & Economic Statistics, 43*(3), 643–656. https://doi.org/10.1080/07350015.2024.2418835

**Core finding**

The paper considers forecast-loss differentials whose mean can vary over time. It shows that the standard Diebold-Mariano test, designed around a stable loss-differential environment, can have severely distorted behavior when the mean of the loss differential is time-varying. The authors propose a modified procedure based on local demeaning.

**Why this matters unusually strongly for this thesis**

The thesis explicitly studies forecasting **under macroeconomic instability**. A forecast-comparison test whose standard formulation can become unreliable under time variation is therefore directly relevant.

**Use in Part 9**

- Chapter 2 methodology.
- Chapter 3/4 forecast-evaluation interpretation.
- Methodological limitations if conventional DM statistics are also displayed.

**Part 5 decision**

**RESOLVED-M5-01:** The user approved the forecast-comparison update on 6 October 2026. Harvey-Leybourne-Zu (2025) is now the primary pairwise equal-average-accuracy test. DM-HLN is retained only as a secondary conventional comparison. Giacomini-White remains the primary state-conditioned test, and the Hansen-Lunde-Nason Model Confidence Set remains the multiple-model procedure.

**Relevance:** CRITICAL.

---

## A3. Odendahl, Rossi, and Sekhposyan (2023), state-dependent forecast performance

**Citation**

Odendahl, F., Rossi, B., & Sekhposyan, T. (2023). Evaluating forecast performance with state dependence. *Journal of Econometrics, 237*(2), 105220. https://doi.org/10.1016/j.jeconom.2021.07.015

**Core finding**

Forecast performance itself can depend nonlinearly on economic states. The paper develops hard- and smooth-threshold methods for testing absolute and relative forecasting performance when predictive performance changes with an observed economic variable.

Its empirical work shows that predictors can be useful in particular states even when average forecasting performance hides that usefulness.

**Why it is very close to the thesis**

The thesis asks whether nonlinear gains are concentrated in recessions, expansions, peaks, troughs, or unstable periods. This paper directly establishes that forecast evaluation can itself need to be state-dependent.

**Use in Part 9**

- General Introduction: average forecast performance can mask conditional predictability.
- Chapter 2: justification for state-conditioned evaluation.
- Chapter 3: compare recession/expansion findings.
- Chapter 4: interpret gains that appear only in particular states.

**Do not claim**

Do not imply that their state-dependent forecast-evaluation method is the same as MSAR or STAR estimation.

**Relevance:** CRITICAL.

---

## A4. Goulet Coulombe et al. (2022), why nonlinearities help macro forecasts

**Citation**

Goulet Coulombe, P., Leroux, M., Stevanovic, D., & Surprenant, S. (2022). How is machine learning useful for macroeconomic forecasting? *Journal of Applied Econometrics, 37*(5), 920–964. https://doi.org/10.1002/jae.2910

**Core finding**

The paper decomposes the sources of machine-learning forecasting gains and concludes that nonlinearity is a key contributor. It finds that nonlinear gains are especially associated with high macroeconomic uncertainty, financial stress, and housing-bubble bursts.

**Why useful**

This is strong recent evidence supporting the thesis's main economic premise that nonlinear flexibility may become more valuable during unstable states.

**Use in Part 9**

- Chapter 1 literature gap/problem.
- Chapter 3 if nonlinear gains concentrate in unstable periods.
- Chapter 4 if gains are state-dependent rather than universal.
- Conclusion to position the thesis within broader modern nonlinear forecasting literature.

**Do not claim**

The paper does not prove that MSAR or STAR must outperform AR/ARMA.

**Relevance:** VERY HIGH.

---

## A5. Goulet Coulombe (2024), evolving nonlinear macroeconomic relationships

**Citation**

Goulet Coulombe, P. (2024). The macroeconomy as a random forest. *Journal of Applied Econometrics, 39*(3), 401–421. https://doi.org/10.1002/jae.3030

**Core finding**

The macroeconomic random forest produces generalized time-varying parameters capable of nesting threshold/switching behavior, smooth transitions, and structural change. The paper reports forecast gains, including strong performance for unemployment and inflation.

**Why useful**

It provides a modern unifying perspective on exactly the forms of instability discussed in Chapter 1: threshold effects, regime switching, smooth transition, and structural breaks.

**Use in Part 9**

- Chapter 1 nonlinear taxonomy.
- Chapter 2 rationale for comparing discrete versus smooth state dependence.
- Chapter 3/4 discussion of unemployment and inflation findings.
- Conclusion to show where interpretable parametric nonlinear models sit relative to flexible ML approaches.

**Relevance:** VERY HIGH.

---

## A6. Clark, Huber, Koop, and Marcellino (2024), nonlinear U.S. inflation

**Citation**

Clark, T. E., Huber, F., Koop, G., & Marcellino, M. (2024). Forecasting U.S. inflation using Bayesian nonparametric models. *Annals of Applied Statistics, 18*(2), 1421–1444. https://doi.org/10.1214/23-AOAS1841

**Core finding**

The paper starts from the possibility that the relationship between inflation and predictors such as unemployment is nonlinear and time-varying and that forecast errors can contain large asymmetric shocks. It develops flexible conditional-mean/error models for U.S. inflation forecasting.

**Use in Part 9**

- Chapter 1 Phillips-curve instability.
- Chapter 2 inflation methodology context.
- Chapter 3 CPI result comparison.
- Chapter 4 when interpreting instability or asymmetry in inflation forecasts.

**Relevance:** VERY HIGH for the inflation block.

---

## A7. Carriero, Clark, Marcellino, and Mertens (2025), policy-rate constraint and forecast nonlinearity

**Citation**

Carriero, A., Clark, T. E., Marcellino, M., & Mertens, E. (2025). Forecasting with shadow rate VARs. *Quantitative Economics, 16*(3), 795–822. https://doi.org/10.3982/QE2547

**Core finding**

Standard linear VARs are ill-suited to occasionally binding constraints such as the effective lower bound on nominal interest rates. Shadow-rate VARs substantially improve interest-rate forecasts while generally matching standard VAR macroeconomic forecasts.

**Why important to this thesis**

The jury specifically questioned unstable/implausible Markov-switching results for FEDFUNDS. This paper gives a recent high-level reason why policy-rate dynamics may contain structural nonlinearities unrelated to a generic recession regime.

**Use in Part 9**

- Chapter 1: interest-rate nonlinearities and monetary-policy regimes.
- Chapter 3: interpret FEDFUNDS results cautiously.
- Chapter 4: alternative explanation for policy-rate nonlinear behavior.
- Limitations: MSAR/STAR are not designed specifically around the effective lower bound.

**Do not claim**

Do not use this paper to justify replacing FEDFUNDS with a shadow rate unless Part 5 is explicitly revised.

**Relevance:** VERY HIGH for the policy-rate block.

---

## A8. Carriero et al. (2024), extreme observations and macroeconomic instability

**Citation**

Carriero, A., Clark, T. E., Marcellino, M., & Mertens, E. (2024). Addressing COVID-19 outliers in BVARs with stochastic volatility. *Review of Economics and Statistics, 106*(5), 1403–1417. https://doi.org/10.1162/rest_a_01213

**Core finding**

The extreme movements during COVID materially affect standard BVAR parameters and forecasts. Outlier-augmented stochastic-volatility models are more robust during the pandemic and other high-volatility periods.

**Use in Part 9**

- Chapter 1: instability can reflect extreme shocks as well as persistent nonlinear propagation.
- Chapter 3/4: interpret 2020-period model behavior.
- Chapter 4: distinguish model nonlinearity from shock/outlier instability.

**Why useful conceptually**

It provides a serious competing explanation: a nonlinear model may appear valuable because it is absorbing rare extreme shocks rather than uncovering stable regime dynamics.

**Relevance:** VERY HIGH.

---

## A9. Lenza and Primiceri (2022), VAR estimation after COVID

**Citation**

Lenza, M., & Primiceri, G. E. (2022). How to estimate a vector autoregression after March 2020. *Journal of Applied Econometrics, 37*(4), 688–699. https://doi.org/10.1002/jae.2895

**Core finding**

Extreme pandemic observations can severely affect VAR estimation. Simply deleting them may sometimes be acceptable for parameter estimation, but ignoring them is inappropriate for forecasting because it understates future uncertainty.

**Use in Part 9**

- Chapter 2/4 multivariate robustness.
- Discussion of COVID observations.
- Explanation of why the thesis does not simply delete difficult episodes.

**Relevance:** HIGH.

---

## A10. Naghi, O'Neill, and Danielova Zaharieva (2024), nonlinear methods are not universally best

**Citation**

Naghi, A. A., O'Neill, E., & Danielova Zaharieva, M. (2024). The benefits of forecasting inflation with machine learning: New evidence. *Journal of Applied Econometrics, 39*(7), 1321–1331. https://doi.org/10.1002/jae.3088

**Core finding**

The paper replicates and extends earlier evidence on ML inflation forecasting. It finds that other models can be competitive with random forests and that random-forest performance deteriorates during the COVID/high-inflation episode, while some stochastic-volatility and boosting models perform better.

**Why especially useful**

This is excellent support for the thesis's **selective rather than universal** view of nonlinear complexity.

**Use in Part 9**

- Literature review: richer models do not guarantee robust superiority.
- Chapter 3 if AR/ARMA beats nonlinear models for some targets.
- Chapter 4 if rankings change across unstable episodes.
- General Conclusion if no single nonlinear model dominates.

**Relevance:** VERY HIGH.

---

## A11. Prüser and Huber (2024), nonlinearities are especially useful in macroeconomic tails

**Citation**

Prüser, J., & Huber, F. (2024). Nonlinearities in macroeconomic tail risk through the lens of big data quantile regressions. *Journal of Applied Econometrics, 39*(2), 269–291. https://doi.org/10.1002/jae.3018

**Core finding**

The paper forecasts the conditional distribution of U.S. GDP growth and finds that nonlinear specifications can improve forecasts, particularly in the tails.

**Use in Part 9**

- Chapter 1: nonlinearities may matter most away from normal states.
- Chapter 3/4 if gains concentrate in recessions/turning points.
- Limitations: this thesis forecasts the conditional mean, not quantile/tail risk.

**Relevance:** HIGH.

---

## A12. Hong et al. (2025), inflation forecast gains concentrated in recessions

**Citation**

Hong, Y., Jiang, F., Meng, L., & Xue, B. (2025). Forecasting inflation using economic narratives. *Journal of Business & Economic Statistics, 43*(1), 216–231. https://doi.org/10.1080/07350015.2024.2347619

**Core finding**

Narrative-based inflation forecasts outperform benchmark models, with particularly strong gains during recession periods and at longer horizons.

**Use in Part 9**

- Chapter 1: information and forecastability can vary by state.
- Chapter 3: recession-specific inflation results.
- Chapter 4: horizon dependence.
- Do not use as evidence that narratives or text should be added to this thesis's model set.

**Relevance:** HIGH.

---

## A13. Hauzenberger et al. (2025), nonlinear multivariate macroeconomic dynamics

**Citation**

Hauzenberger, N., Huber, F., Marcellino, M., & Petz, N. (2025). Gaussian process vector autoregressions and macroeconomic uncertainty. *Journal of Business & Economic Statistics, 43*(1), 27–43. https://doi.org/10.1080/07350015.2024.2322089

**Core finding**

The paper develops a nonlinear nonparametric VAR with flexible stochastic volatility and studies time variation and asymmetries in macroeconomic transmission.

**Use in Part 9**

- Chapter 1: modern multivariate nonlinear literature.
- Chapter 2: justify why the thesis's VAR block is a robustness test rather than claiming multivariate nonlinear dynamics do not exist.
- Chapter 4: compare univariate and multivariate evidence.
- Limitations/future research.

**Relevance:** HIGH.

---

## A14. Leiva-León and Uzeda (2023), endogenous time variation in VARs

**Citation**

Leiva-León, D., & Uzeda, L. (2023). Endogenous time variation in vector autoregressions. *Review of Economics and Statistics, 105*(1), 125–142. https://doi.org/10.1162/rest_a_01038

**Core finding**

The paper allows structural shocks to influence the evolution of VAR coefficients and applies the framework to the U.S. economy. It finds economically meaningful time variation, including changes in inflation-gap persistence.

**Use in Part 9**

- Chapter 1: economic shocks can alter macroeconomic propagation.
- Chapter 4: omitted cross-variable/time-varying dynamics are a competing explanation for apparent univariate nonlinearities.
- Conclusion/external validity.

**Relevance:** HIGH.

---

## A15. Galvão and Owyang (2022), recession forecasting and mixed frequency

**Citation**

Galvão, A. B., & Owyang, M. T. (2022). Forecasting low-frequency macroeconomic events with high-frequency data. *Journal of Applied Econometrics, 37*(7), 1314–1333. https://doi.org/10.1002/jae.2931

**Core finding**

The paper develops a mixed-frequency approach for forecasting macroeconomic events and finds that higher-frequency financial/economic indicators can improve recession and vulnerability-event forecasting.

**Use in Part 9**

- Chapter 1 literature boundary.
- Chapter 4 nowcasting/mixed-frequency limitation.
- Explain why this thesis's native-frequency forecast comparison is not a nowcasting study.

**Relevance:** HIGH as a boundary paper.

---

# 3. Additional recent Q1 papers that broaden interpretation

## B1. Hauzenberger, Huber, Klieber, and Marcellino (2025)

Hauzenberger, N., Huber, F., Klieber, K., & Marcellino, M. (2025). Bayesian neural networks for macroeconomic analysis. *Journal of Econometrics, 249*, 105843. https://doi.org/10.1016/j.jeconom.2024.105843

**Use:** positions the thesis relative to modern nonlinear ML. Particularly useful when explaining that macro data are small-T and temporally dependent, so parsimony and shrinkage matter.

**Do not use to argue that neural networks should be added to Part 5.**

---

## B2. Carriero, Clark, and Marcellino (2025)

Carriero, A., Clark, T. E., & Marcellino, M. (2025). Specification choices in quantile regression for empirical macroeconomics. *Journal of Applied Econometrics, 40*(1), 57–73. https://doi.org/10.1002/jae.3099

**Use:** methodological discussion of specification discipline and tail forecasting. Supports the principle that model specification and regularization decisions materially affect forecast conclusions.

---

## B3. Medeiros et al. (2021)

Medeiros, M. C., Vasconcelos, G. F. R., Veiga, Á., & Zilberman, E. (2021). Forecasting inflation in a data-rich environment: The benefits of machine learning methods. *Journal of Business & Economic Statistics, 39*(1), 98–119. https://doi.org/10.1080/07350015.2019.1637745

**Use:** bridge paper for modern U.S. inflation forecasting. It finds gains from ML, with nonlinear relationships contributing to performance.

**Important pairing:** cite together with Naghi et al. (2024), which shows that the strong ranking is not universally stable out of sample, especially during COVID/high inflation.

---

## B4. Guérin, Leiva-León, and Marcellino (2020), older but unusually close

Guérin, P., Leiva-León, D., & Marcellino, M. (2020). Markov-switching three-pass regression filter. *Journal of Business & Economic Statistics, 38*(2), 285–302. https://doi.org/10.1080/07350015.2018.1497508

**Use:** bridge between Markov switching, structural instability, and forecasting economic activity. It is older than the main recent-literature window but directly relevant to the MSAR side of the thesis.

---

# 4. How these papers map into Part 9

## General Introduction

Use the recent literature to establish that:

- macroeconomic relationships can evolve across states and shocks;
- nonlinear gains may be concentrated in unstable periods;
- instability also creates problems for forecast evaluation itself;
- nonlinear flexibility can help, but its superiority is not universal.

Best anchors:

- Clark, Huber, & Koop (2026);
- Odendahl, Rossi, & Sekhposyan (2023);
- Goulet Coulombe et al. (2022);
- Harvey, Leybourne, & Zu (2025);
- Naghi et al. (2024).

## Chapter 1: problem and literature

### Structural instability and nonlinear propagation

Use:

- Goulet Coulombe (2024);
- Leiva-León & Uzeda (2023);
- Clark, Huber, & Koop (2026);
- Carriero et al. (2024).

### Inflation / Phillips-type instability

Use:

- Clark et al. (2024);
- Medeiros et al. (2021);
- Naghi et al. (2024);
- Hong et al. (2025).

### Recession / turning-point relevance

Use:

- Odendahl et al. (2023);
- Hong et al. (2025);
- Galvão & Owyang (2022);
- Prüser & Huber (2024).

### Interest-rate/policy nonlinearity

Use:

- Carriero et al. (2025), shadow-rate VARs;
- Leiva-León & Uzeda (2023).

## Chapter 2: methodology

Use:

- Harvey et al. (2025) for unstable forecast-comparison environments;
- Odendahl et al. (2023) for state-dependent forecast performance;
- Clark, Huber, & Koop (2026) for parsimony in nonlinear macro models;
- Carriero, Clark, & Marcellino (2025) for specification discipline;
- Lenza & Primiceri (2022) for extreme observations;
- Galvão & Owyang (2022) to delimit mixed-frequency/nowcasting.

## Chapter 3: baseline results

Citation selection must depend on actual Part 8 findings.

Do not write the literature comparison before the empirical ranking exists.

## Chapter 4: robustness and interpretation

Use:

- Carriero et al. (2024) if COVID/extreme observations drive results;
- Carriero et al. (2025) if FEDFUNDS behaves unusually;
- Hauzenberger et al. (2025) or Clark et al. (2026) if multivariate information changes conclusions;
- Naghi et al. (2024) if nonlinear rankings are fragile across unstable episodes;
- Odendahl et al. (2023) if gains are concentrated in particular states.

---

# 5. Result-dependent citation map

## If MSAR or STAR clearly improves during recessions / turning points

Discuss alongside:

- Odendahl et al. (2023);
- Goulet Coulombe et al. (2022);
- Clark, Huber, & Koop (2026);
- Hong et al. (2025);
- Prüser & Huber (2024).

Interpretation:

> The thesis result would be consistent with recent evidence that nonlinear or richer predictive structures can become especially useful in stressed or state-dependent environments.

Do **not** write:

> Recent literature proves MSAR/STAR is superior in recessions.

The papers use different models.

## If nonlinear models improve overall but not specifically in recessions

Use:

- Goulet Coulombe (2024);
- Clark et al. (2024);
- Medeiros et al. (2021).

Interpretation:

> Nonlinear predictive structure may matter without mapping cleanly onto the NBER recession chronology.

## If AR/ARMA remains competitive or dominant

Use:

- Naghi et al. (2024);
- Clark, Huber, & Koop (2026), especially the result that nonlinear corrections can be modest in normal periods;
- older Teräsvirta et al. (2005) as a historical bridge.

Interpretation:

> Failure of nonlinear models to dominate is scientifically meaningful and consistent with a literature in which nonlinear gains are conditional rather than universal.

## If CPI results show strong nonlinear gains

Use:

- Clark et al. (2024);
- Medeiros et al. (2021);
- Hong et al. (2025);
- Naghi et al. (2024).

## If CPI results are fragile

Use Naghi et al. (2024) especially strongly, because its extended sample shows that model rankings can deteriorate in the COVID/high-inflation period.

## If FEDFUNDS MSAR is unstable or implausible

Use:

- Carriero et al. (2025), shadow-rate VARs;
- Leiva-León & Uzeda (2023);
- Lenza & Primiceri (2022), if pandemic observations contribute.

Interpretation:

> Policy-rate instability may reflect economically specific constraints and policy regimes rather than a generic two-state Markov mechanism.

## If the monthly VAR materially changes the model ranking

Use:

- Hauzenberger et al. (2025);
- Clark, Huber, & Koop (2026);
- Leiva-León & Uzeda (2023).

Interpretation:

> Some apparent univariate nonlinear predictability may be proxying for omitted cross-variable dynamics.

## If COVID strongly affects the results

Use:

- Carriero et al. (2024);
- Lenza & Primiceri (2022);
- Naghi et al. (2024).

## If longer horizons change the ranking

Use:

- Hong et al. (2025) as recent evidence that predictive gains can vary by horizon;
- the older Marcellino, Stock, and Watson (2006) methodology reference already present in Part 5 for the direct-versus-iterated horizon literature.

---

# 6. Resolved methodological implication for Part 5

## Forecast-accuracy testing under instability

The issue is now resolved before Part 8 results are known.

The approved inferential hierarchy is:

1. **Harvey-Leybourne-Zu (2025)** as the primary pairwise equal-average-accuracy test under possible instability;
2. **Giacomini-White (2006)** as the primary conditional/state test for recession and turning-point dependence;
3. **Hansen-Lunde-Nason Model Confidence Set** for multiple-model inference;
4. **DM-HLN** retained secondarily as a familiar conventional comparison.

Clark-McCracken / Clark-West are not applied mechanically because the central AR-vs-MSAR/STAR comparisons are not regular nested linear comparisons. Amisano-Giacomini is not a core test because the thesis does not construct a common predictive-density forecasting system.

This decision was taken before seeing the final Part 8 rankings, which protects it from result-driven test selection.

---

# 7. What this recent literature does NOT require us to add

The recent papers use machine learning, Bayesian nonparametrics, Gaussian processes, nonlinear factors, quantile regression, shadow rates, and mixed-frequency data.

Their existence does **not** mean the thesis must estimate all of these models.

The purpose of the recent-literature bank is to:

- show that the thesis problem remains current;
- situate AR/MSAR/STAR within the modern forecasting literature;
- identify alternative explanations for the results;
- compare findings honestly;
- explain limitations and future extensions.

Adding every modern model would destroy the clean Part 4/Part 5 logic and make it impossible to identify which form of state dependence is responsible for any gain.

---

# 8. Q1 / Scopus venue verification note

Current checks made for this literature bank indicate:

| Venue | Current Scopus / SCImago status used here |
|---|---|
| Journal of Econometrics | Active Scopus, Q1 Economics & Econometrics |
| Journal of Applied Econometrics | Active Scopus, Q1 Economics & Econometrics |
| Journal of Business & Economic Statistics | Active Scopus, Q1 |
| Review of Economics and Statistics | Active Scopus, Q1 Economics & Econometrics |
| Quantitative Economics | Active Scopus, Q1 Economics & Econometrics |
| Journal of Monetary Economics | Active Scopus, Q1 Economics & Econometrics |
| International Journal of Forecasting | Active Scopus, Q1 in current SJR classification |
| Annals of Applied Statistics | Active Scopus, Q1 in statistics/applied-statistics classification |

For Part 9, do **not** write “published in a Q1 journal” in the thesis unless that fact is itself substantively relevant. The quartile check is a source-quality filter for us, not part of the economic argument.

---

# 9. Priority reading order before Part 9 writing

**Tier 1, must read/use if relevant to results**

1. Clark, Huber, & Koop (2026)
2. Harvey, Leybourne, & Zu (2025)
3. Odendahl, Rossi, & Sekhposyan (2023)
4. Goulet Coulombe et al. (2022)
5. Goulet Coulombe (2024)
6. Naghi et al. (2024)
7. Carriero et al. (2025), shadow-rate VARs
8. Carriero et al. (2024), COVID outliers

**Tier 2, target-specific or robustness**

9. Clark et al. (2024), U.S. inflation
10. Prüser & Huber (2024)
11. Hong et al. (2025)
12. Hauzenberger et al. (2025), GP-VAR
13. Leiva-León & Uzeda (2023)
14. Lenza & Primiceri (2022)
15. Galvão & Owyang (2022)

**Tier 3, broader modern context**

16. Hauzenberger et al. (2025), Bayesian neural networks
17. Carriero, Clark, & Marcellino (2025), quantile specification
18. Medeiros et al. (2021)
19. Guérin et al. (2020), Markov-switching bridge

---

# 10. Part 9 citation discipline

When Part 9 is written:

1. never cite a paper as supporting a result before Part 8 has actually produced that result;
2. distinguish **same question** from **same model**;
3. distinguish **consistent with prior evidence** from **confirms prior evidence**;
4. do not infer causality from forecasting comparisons;
5. if our result contradicts recent literature, report the contradiction rather than suppressing the paper;
6. use recent papers alongside foundational references, not instead of foundational references;
7. compare samples, horizons, information sets, targets, and loss functions before declaring two results comparable;
8. use the literature to qualify the result, not to make an insignificant result look significant.

---

# 11. Working APA bibliography

Carriero, A., Clark, T. E., & Marcellino, M. (2025). Specification choices in quantile regression for empirical macroeconomics. *Journal of Applied Econometrics, 40*(1), 57–73. https://doi.org/10.1002/jae.3099

Carriero, A., Clark, T. E., Marcellino, M., & Mertens, E. (2024). Addressing COVID-19 outliers in BVARs with stochastic volatility. *Review of Economics and Statistics, 106*(5), 1403–1417. https://doi.org/10.1162/rest_a_01213

Carriero, A., Clark, T. E., Marcellino, M., & Mertens, E. (2025). Forecasting with shadow rate VARs. *Quantitative Economics, 16*(3), 795–822. https://doi.org/10.3982/QE2547

Clark, T. E., Huber, F., Koop, G., & Marcellino, M. (2024). Forecasting U.S. inflation using Bayesian nonparametric models. *Annals of Applied Statistics, 18*(2), 1421–1444. https://doi.org/10.1214/23-AOAS1841

Clark, T. E., Huber, F., & Koop, G. (2026). A flexible approach to augmenting a Bayesian VAR with nonlinear factors. *Journal of Business & Economic Statistics*. Advance online publication. https://doi.org/10.1080/07350015.2026.2703238

Galvão, A. B., & Owyang, M. T. (2022). Forecasting low-frequency macroeconomic events with high-frequency data. *Journal of Applied Econometrics, 37*(7), 1314–1333. https://doi.org/10.1002/jae.2931

Goulet Coulombe, P. (2024). The macroeconomy as a random forest. *Journal of Applied Econometrics, 39*(3), 401–421. https://doi.org/10.1002/jae.3030

Goulet Coulombe, P., Leroux, M., Stevanovic, D., & Surprenant, S. (2022). How is machine learning useful for macroeconomic forecasting? *Journal of Applied Econometrics, 37*(5), 920–964. https://doi.org/10.1002/jae.2910

Guérin, P., Leiva-León, D., & Marcellino, M. (2020). Markov-switching three-pass regression filter. *Journal of Business & Economic Statistics, 38*(2), 285–302. https://doi.org/10.1080/07350015.2018.1497508

Harvey, D. I., Leybourne, S. J., & Zu, Y. (2025). Testing for equal average forecast accuracy in possibly unstable environments. *Journal of Business & Economic Statistics, 43*(3), 643–656. https://doi.org/10.1080/07350015.2024.2418835

Hauzenberger, N., Huber, F., Klieber, K., & Marcellino, M. (2025). Bayesian neural networks for macroeconomic analysis. *Journal of Econometrics, 249*, 105843. https://doi.org/10.1016/j.jeconom.2024.105843

Hauzenberger, N., Huber, F., Marcellino, M., & Petz, N. (2025). Gaussian process vector autoregressions and macroeconomic uncertainty. *Journal of Business & Economic Statistics, 43*(1), 27–43. https://doi.org/10.1080/07350015.2024.2322089

Hong, Y., Jiang, F., Meng, L., & Xue, B. (2025). Forecasting inflation using economic narratives. *Journal of Business & Economic Statistics, 43*(1), 216–231. https://doi.org/10.1080/07350015.2024.2347619

Leiva-León, D., & Uzeda, L. (2023). Endogenous time variation in vector autoregressions. *Review of Economics and Statistics, 105*(1), 125–142. https://doi.org/10.1162/rest_a_01038

Lenza, M., & Primiceri, G. E. (2022). How to estimate a vector autoregression after March 2020. *Journal of Applied Econometrics, 37*(4), 688–699. https://doi.org/10.1002/jae.2895

Medeiros, M. C., Vasconcelos, G. F. R., Veiga, Á., & Zilberman, E. (2021). Forecasting inflation in a data-rich environment: The benefits of machine learning methods. *Journal of Business & Economic Statistics, 39*(1), 98–119. https://doi.org/10.1080/07350015.2019.1637745

Naghi, A. A., O'Neill, E., & Danielova Zaharieva, M. (2024). The benefits of forecasting inflation with machine learning: New evidence. *Journal of Applied Econometrics, 39*(7), 1321–1331. https://doi.org/10.1002/jae.3088

Odendahl, F., Rossi, B., & Sekhposyan, T. (2023). Evaluating forecast performance with state dependence. *Journal of Econometrics, 237*(2), 105220. https://doi.org/10.1016/j.jeconom.2021.07.015

Prüser, J., & Huber, F. (2024). Nonlinearities in macroeconomic tail risk through the lens of big data quantile regressions. *Journal of Applied Econometrics, 39*(2), 269–291. https://doi.org/10.1002/jae.3018
