# General Introduction
## Forecasting Macroeconomic Aggregates Under Instability: Problem, Contribution and Research Strategy

The Book of Genesis recounts how Joseph predicted seven years of abundance followed by seven years of famine in Egypt. He advised Pharaoh to collect one-fifth of the harvest during the abundant years and store the grain. The narrative reports that both periods occurred and that Joseph later opened the grain stores (*The Bible, Douay-Rheims, Complete*, 1998, Genesis 41:25–36, 41:53–57). In modern economic terms, this is an account of forecast-informed public buffer stocks. It shows how an expected shortage can prompt preparation before the shortage begins. The text is used as a narrative illustration, not as independent historical proof of the first macroeconomic policy.

The policy depended on the timing of the forecast. Grain saved during abundance could be used when harvests failed. Yet accurate information was only one condition for success. Pharaoh also needed institutions able to collect, store, and release the reserves. The same distinction holds today. Forecasts can guide public action, but they cannot choose a policy, guarantee its execution, or remove uncertainty. This thesis studies forecast reliability rather than the choice of macroeconomic policy.

Contemporary forecasts often miss turning points. An et al. (2018) examined GDP forecasts for 63 countries from 1992 to 2014. Official and private forecasters often underestimated recession severity until the recession year was nearly over. This finding is not specific to one institution. A late forecast revision leaves less time to prepare for falling output, employment, or revenue. It does not prove that the forecast error caused a recession or that earlier warning would have prevented it.

The post-pandemic inflation surge provides a recent example. Bernanke (2024, Table 7) reported that the Bank of England's one-year-ahead inflation forecast RMSE rose from 0.64 percentage points in 2015–2019 to 4.60 in 2021 Q2–2023 Q3. External forecasters reached 4.67 percentage points in the later period. Bernanke linked these common errors to large shocks, including the pandemic, energy prices, and supply disruptions. The errors show the forecasting difficulty faced by policy institutions during instability, not a failure unique to one bank.

Fiscal forecasts have also missed outcomes by large amounts. The Office for Budget Responsibility (OBR, 2026, paras. 1.5 and 3.17) forecast £85 billion in United Kingdom public borrowing for 2024–2025 in March 2023. The outturn was £152 billion, a £66 billion published difference after rounding. Persistent inflation, higher interest costs, and later policy decisions all contributed. This difference is not solely a model error. It shows the scale of uncertainty surrounding the information used for fiscal planning.

The welfare stakes are real. The Organisation for Economic Co-operation and Development (OECD, 2023) reported negative real wage growth in 30 of 34 countries with available data during the first quarter of 2023. The average fall was 3.8%, with severe pressure on low-income households. These wage losses do not establish that forecast errors caused the harm. They show why reliable information about inflation, employment, and growth can matter for preparedness. Better forecasts may support planning but cannot prevent every shock.

Policymakers also face revisions to economic data. Orphanides (2001) showed that recommendations from monetary policy rules can differ markedly when based on information available at the decision date rather than later-revised data. Thus, good historical fit does not alone demonstrate usefulness to a policymaker. Forecasts need an evaluation that respects the information available at each origin. This thesis addresses that principle within a fixed historical-vintage design, not a complete real-time-vintage exercise.

Macroeconomic variables are linked, but their relations can change. Inflation affects purchasing power and interest-rate expectations. Output and unemployment move with the business cycle, while money and policy rates help describe nominal and financial conditions. Fisher (1930), Phelps (1967), and Okun (1962) provide classic foundations for these links. Yet shocks, policy shifts, and changes in expectations can alter the observed dynamics. A model that describes an expansion well may forecast a recession poorly. This motivates testing instability rather than assuming stable relationships.

Classical time-series models offer a disciplined benchmark. Autoregressive (AR) models use past target values. Autoregressive moving-average (ARMA) models also use past innovations. Nonlinear models allow dynamics to change across states. Hamilton (1989) developed a Markov-switching framework for discrete latent regimes. Smooth transition autoregressive (STAR) models allow gradual adjustment. Teräsvirta et al. (2005) showed why their specification and evaluation require care. These model classes existed long before this study.

Later work found both promise and limits in nonlinear forecasting. Goulet Coulombe et al. (2022) linked machine-learning forecast gains to nonlinear features, especially during uncertainty. Clark et al. (2026) reported gains from nonlinear factors in a Bayesian vector autoregression (VAR) for U.S. macroeconomic data. Yet Naghi et al. (2024) found that other methods could compete with random forests and that performance changed during the pandemic and inflation surge. These studies differ in models, data, losses, and samples. None establishes universal MSAR or STAR superiority.

Forecast evaluation also shapes the conclusion. Giacomini and White (2006) studied predictive accuracy conditional on economic states. Hansen et al. (2011) showed that the data may support a Model Confidence Set rather than one winner. Rossi and Inoue (2012) examined sensitivity to estimation-window length. Harvey et al. (2025) proposed an average-accuracy test for possibly time-varying forecast-loss differences. These advances show why a lower error in one sample is insufficient. A gain needs suitable inference and checks for instability, selection, and model failure.

The remaining question is whether state-dependent flexibility adds reliable forecast value after accounting for its risks. A nonlinear model may fit past data but forecast poorly. It may isolate one extreme observation as a regime or produce unstable parameters. A weak classical benchmark may also create a false advantage for complexity. This study therefore asks whether any gain survives credible estimation, careful forecast testing, and alternative explanations. A linear model winning is a valid result.

The central research question of this thesis is:

*Under macroeconomic instability, when do nonlinear state-dependent forecasting models provide statistically credible and economically meaningful gains over classical forecasting benchmarks, and when does their additional complexity fail to improve prediction?*

The study first examines persistence, breaks, and nonlinearity in selected macroeconomic series. It then tests forecast gains only after checking model adequacy and numerical credibility. Finally, it asks whether results depend on recessions, turning points, forecast horizons, transformations, regime counts, estimation windows, or information from other variables. These are forecasting questions. The study does not estimate the causal effects of better forecasts on policy or welfare.

The United States is the empirical case because it offers long official series, repeated instability episodes, and clear Federal Reserve policy relevance. The monthly targets are consumer price inflation (CPIAUCSL), unemployment (UNRATE), industrial production growth (INDPRO), the federal funds rate (FEDFUNDS), and M2 money growth (M2SL). Real GDP growth (GDPC1) remains quarterly. NBER recession dates classify forecast errors ex post, not as information available to each model in real time. The frozen FRED/ALFRED vintage is dated 5 October 2026. Two missing October 2025 observations receive the approved, disclosed last-observation-carried-forward treatment. Monthly targets end in August 2026; quarterly GDP ends in 2026 Q2.

The experiment compares AR and ARMA with parsimonious two-regime Markov-switching AR (MSAR) and STAR models. Stationarity, nonlinearity, residual adequacy, regime credibility, and convergence are checked before forecast claims. Fixed-length rolling windows re-estimate parameters at each origin. The baseline is a one-period forecast; longer horizons test sensitivity. RMSE and mean absolute error describe accuracy, while the Harvey–Leybourne–Zu test supplies primary pairwise inference. Conditional predictive ability and Model Confidence Sets provide further checks. A focused monthly VAR, alternative transformations and windows, and an in-sample, full-sample three-regime robustness exercise test rival explanations. Failed fits remain visible.

The contribution is a benchmark-centred, instability-aware comparison of these four model classes across six U.S. targets. It places model adequacy before forecast ranking, uses forecast tests designed for instability, and treats numerical failure as evidence rather than hiding it. The result is not a new forecasting model or a universal rule. It is an empirical assessment of when nonlinear complexity earns its cost. Model rankings apply to the chosen U.S. sample; the evaluation method may be tested elsewhere.

The results do not establish a general nonlinear advantage. At the baseline one-step horizon, neither MSAR nor STAR forecasts significantly better than AR under the primary test for any of the six targets. Non-rejection does not prove equal accuracy. MSAR has a nominal gain for CPI inflation at the 12-month horizon, but it does not survive the separate multiple-testing sensitivity in the final audit. Better in-sample fit also coexists with fragile rolling nonlinear estimates. Some STAR forecasts are extreme, and the three-regime unemployment comparison remains inconclusive. Credible estimation is therefore part of the forecast result.

Part I develops the argument and test. Chapter 1 links macroeconomic mechanisms to instability and reviews prior research. Chapter 2 defines the data, methods, tests, and robustness rules. Part II examines the evidence. Chapter 3 reports model adequacy, baseline forecasts, and business-cycle comparisons. Chapter 4 tests the findings against transformations, lag choices, horizons, multivariate information, and estimation failures. The General Conclusion states what the results can and cannot imply for economic policy.
---

## References

An, Z., Jalles, J. T., & Loungani, P. (2018). How well do economists forecast recessions? *International Finance, 21*(2), 100–121. https://doi.org/10.1111/infi.12130

Bernanke, B. S. (2024). *Forecasting for monetary policymaking and communication at the Bank of England: A review*. Bank of England. https://www.bankofengland.co.uk/independent-evaluation-office/forecasting-for-monetary-policy-making-and-communication-at-the-bank-of-england-a-review/forecasting-for-monetary-policy-making-and-communication-at-the-bank-of-england-a-review

*The Bible, Douay-Rheims, complete* (Challoner revision). (1998). Project Gutenberg. https://www.gutenberg.org/ebooks/1581

Clark, T. E., Huber, F., & Koop, G. (2026). A flexible approach to augmenting a Bayesian VAR with nonlinear factors. *Journal of Business & Economic Statistics*. Advance online publication. https://doi.org/10.1080/07350015.2026.2703238

Fisher, I. (1930). *The theory of interest: As determined by impatience to spend income and opportunity to invest it*. Macmillan.

Giacomini, R., & White, H. (2006). Tests of conditional predictive ability. *Econometrica, 74*(6), 1545–1578. https://doi.org/10.1111/j.1468-0262.2006.00718.x

Goulet Coulombe, P., Leroux, M., Stevanovic, D., & Surprenant, S. (2022). How is machine learning useful for macroeconomic forecasting? *Journal of Applied Econometrics, 37*(5), 920–964. https://doi.org/10.1002/jae.2910

Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica, 57*(2), 357–384. https://doi.org/10.2307/1912559

Hansen, P. R., Lunde, A., & Nason, J. M. (2011). The model confidence set. *Econometrica, 79*(2), 453–497. https://doi.org/10.3982/ECTA5771

Harvey, D. I., Leybourne, S. J., & Zu, Y. (2025). Testing for equal average forecast accuracy in possibly unstable environments. *Journal of Business & Economic Statistics, 43*(3), 643–656. https://doi.org/10.1080/07350015.2024.2418835

Naghi, A. A., O'Neill, E., & Danielova Zaharieva, M. (2024). The benefits of forecasting inflation with machine learning: New evidence. *Journal of Applied Econometrics, 39*(7), 1321–1331. https://doi.org/10.1002/jae.3088

Office for Budget Responsibility. (2026). *Forecast evaluation report: June 2026*. https://obr.uk/fer/forecast-evaluation-report-june-2026/

Okun, A. M. (1962). Potential GNP: Its measurement and significance. *Proceedings of the Business and Economic Statistics Section of the American Statistical Association*, 98–104.

Organisation for Economic Co-operation and Development. (2023). *OECD employment outlook 2023: Artificial intelligence and the labour market*. OECD Publishing. https://doi.org/10.1787/08785bba-en

Orphanides, A. (2001). Monetary policy rules based on real-time data. *American Economic Review, 91*(4), 964–985. https://doi.org/10.1257/aer.91.4.964

Phelps, E. S. (1967). Phillips curves, expectations of inflation and optimal unemployment over time. *Economica, 34*(135), 254–281. https://doi.org/10.2307/2552025

Rossi, B., & Inoue, A. (2012). Out-of-sample forecast tests robust to the choice of window size. *Journal of Business & Economic Statistics, 30*(3), 432–453. https://doi.org/10.1080/07350015.2012.693850

Teräsvirta, T., van Dijk, D., & Medeiros, M. C. (2005). Linear models, smooth transition autoregressions, and neural networks for forecasting macroeconomic time series: A re-examination. *International Journal of Forecasting, 21*(4), 755–774. https://doi.org/10.1016/j.ijforecast.2005.04.010
