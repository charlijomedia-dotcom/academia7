# Appendix B. Model Adequacy and Detailed Forecast Evaluation

This appendix presents the secondary numerical evidence behind the baseline forecasts in Chapter 3. The in-sample model comparisons, paired accuracy tests, NBER-defined evaluation states, and peak/trough neighborhoods serve different statistical purposes. The following tables should not be combined into a single unqualified model ranking. Selected results necessary for the argument already appear in Chapter 3; this appendix makes the accompanying data inspectable without placing dozens of rows in the main exposition.

## B.1 In-sample fits and residual checks

**Table B.1. Full-sample fit measures and selected residual diagnostics**

| Target | Model | BIC | Fit classification | Residual Ljung–Box p (lag) | ARCH-LM p (lag) |
|---|---|---:|---|---:|---:|
| GDPC1 | AR | 1840.39 | adequate | 0.2096 (4) | 1.00e-21 (4) |
| GDPC1 | ARMA | 1851.83 | adequate | 0.2192 (4) | 8.40e-22 (4) |
| GDPC1 | MSAR | 1775.04 | fragile | 0.0179 (4) | 1.33e-14 (4) |
| GDPC1 | STAR | 1836.19 | fragile | 0.6191 (4) | 1.42e-16 (4) |
| CPIAUCSL | AR | 4995.79 | fragile | 2.53e-16 (12) | 2.95e-19 (12) |
| CPIAUCSL | ARMA | 5037.37 | fragile | 5.87e-20 (12) | 1.57e-21 (12) |
| CPIAUCSL | MSAR | 4879.14 | fragile | 9.56e-11 (12) | 1.06e-15 (12) |
| CPIAUCSL | STAR | 4918.72 | fragile | 3.60e-8 (12) | 3.08e-15 (12) |
| UNRATE | AR | 1029.02 | adequate | 0.8418 (12) | 0.9993 (12) |
| UNRATE | ARMA | 1049.40 | adequate | 0.8278 (12) | 0.9994 (12) |
| UNRATE | MSAR | -142.46 | fragile | 0.0018 (12) | 0.9995 (12) |
| UNRATE | STAR | 958.87 | fragile | 0.9422 (12) | 1.0000 (12) |
| INDPRO | AR | 7456.22 | adequate | 1.0000 (12) | 9.95e-16 (12) |
| INDPRO | ARMA | 7501.02 | fragile | 0.0129 (12) | 1.27e-16 (12) |
| INDPRO | MSAR | 7289.93 | fragile | 0.0032 (12) | 1.70e-5 (12) |
| INDPRO | STAR | 7463.85 | fragile | 0.0486 (12) | 3.67e-34 (12) |
| FEDFUNDS | AR | 1051.31 | fragile | 2.45e-20 (12) | 7.16e-17 (12) |
| FEDFUNDS | ARMA | 1059.20 | fragile | 3.06e-20 (12) | 6.94e-17 (12) |
| FEDFUNDS | MSAR | 1078.36 | fragile | 8.31e-20 (12) | 7.16e-17 (12) |
| FEDFUNDS | STAR | 998.08 | fragile | 1.04e-13 (12) | 4.50e-44 (12) |
| M2SL | AR | 4618.27 | fragile | 8.30e-6 (12) | 1.46e-27 (12) |
| M2SL | ARMA | 4640.19 | fragile | 6.74e-6 (12) | 9.77e-28 (12) |
| M2SL | MSAR | 4460.85 | fragile | 1.52e-10 (12) | 9.14e-34 (12) |
| M2SL | STAR | 4603.11 | fragile | 0.0016 (12) | 1.21e-44 (12) |

*Source: Author's computations.* *Note:* BIC is the Bayesian information criterion from the full-sample fitted specification. The Ljung–Box entry is the first available reported tested lag for each model and the ARCH-LM entry is its available reported diagnostic lag, both given in parentheses. A small p-value rejects the corresponding residual-null hypothesis. Model fit classifications are those attached to the released full-sample estimates; an apparently low BIC does not establish adequacy or predictive superiority. Different autoregressive orders can imply different effective dependent-variable sample sizes, so intermodel BIC rankings require the sample-comparability qualification described in Chapter 3.

## B.2 Regime credibility and sample coverage

**Table B.2. Two-state MSAR mean, occupancy, duration and diagnostic information**

| Target | Regime means (target units) | Smoothed occupancy | Expected durations | Fit status and main flags |
|---|---|---|---|---|
| GDPC1 | mu1=-38.1411;  mu2=3.1952 | regime1=0.0032;  regime2=0.9968 | regime1=1.00;  regime2=315.99 | fragile: LOW_OCCUPANCY;TRANSITION_BOUNDARY;RESIDUAL_AUTOCORR |
| CPIAUCSL | mu1=2.5630;  mu2=12.4941 | regime1=0.9140;  regime2=0.0860 | regime1=63.13;  regime2=6.28 | fragile: RESIDUAL_AUTOCORR |
| UNRATE | mu1=-0.1413;  mu2=10.9558 | regime1=0.9181;  regime2=0.0819 | regime1=1091.84;  regime2=295.20 | fragile: TRANSITION_BOUNDARY;RESIDUAL_AUTOCORR |
| INDPRO | mu1=-167.8039;  mu2=2.7157 | regime1=0.0011;  regime2=0.9989 | regime1=1.00;  regime2=953.28 | fragile: SINGULAR_COV;LOW_OCCUPANCY;TRANSITION_BOUNDARY;RESIDUAL_AUTOCORR |
| FEDFUNDS | mu1=0.0025;  mu2=0.0025 | regime1=0.4995;  regime2=0.5005 | regime1=19.98;  regime2=20.01 | fragile: RESIDUAL_AUTOCORR |
| M2SL | mu1=6.3486;  mu2=53.7165 | regime1=0.9963;  regime2=0.0037 | regime1=1000000000000.00;  regime2=3.00 | fragile: LOW_OCCUPANCY;TRANSITION_BOUNDARY;RESIDUAL_AUTOCORR |

*Source: Author's computations.* *Note:* Means are conditional statistical state means, in the scale of the transformed target. Occupancies are full-sample **smoothed** probability shares rather than real-time state frequencies. Durations are in months for monthly series and quarters for GDP, calculated from the diagonal transition probabilities, provided the finite-duration formula is applicable. A rare or nearly absorbing state can produce a mathematically defined mean without supporting a recurrent economic interpretation. In particular, the unemployment model has strong persistence and is not an independently verified business-cycle detector.

Chapter 3 gives the detailed estimated CPI AR(2)/MSAR(2) coefficients and their approximate standard errors; duplicating them here would not supply additional scientific evidence. Other full-sample nonlinear parameter uncertainty is described selectively by the credibility classification, and any unusable covariance estimate prevents reliable coefficient-level interpretation. A claim that the regimes are “monetary-policy regimes” or literal recessions would require additional evidence not supplied by the estimated Markov chain.

## B.3 Baseline one-step point accuracy and formal inference

**Table B.3. One-step own-valid-date RMSE and MAE; AR-matched formal comparisons**

| Target | Model | Valid n | RMSE | MAE | HLZ p squared / absolute vs AR |
|---|---|---:|---:|---:|---|
| GDPC1 | AR | 197 | 5.284 | 2.376 | — / — |
| GDPC1 | ARMA | 197 | 5.246 | 2.377 | 0.3684 / 0.7580 |
| GDPC1 | MSAR | 197 | 4.447 | 2.327 | 0.3566 / 0.6261 |
| GDPC1 | STAR | 197 | 5.123 | 2.469 | 0.5839 / 0.3278 |
| CPIAUCSL | AR | 715 | 2.967 | 2.086 | — / — |
| CPIAUCSL | ARMA | 715 | 3.075 | 2.193 | 0.0986 / 0.0104 |
| CPIAUCSL | MSAR | 715 | 2.966 | 2.097 | 0.9750 / 0.3980 |
| CPIAUCSL | STAR | 715 | 5379975846.370 | 201199691.237 | n.u. / n.u. |
| UNRATE | AR | 703 | 0.551 | 0.169 | — / — |
| UNRATE | ARMA | 689 | 0.737 | 0.185 | 0.3356 / 0.5182 |
| UNRATE | MSAR | 698 | 0.491 | 0.158 | 0.3669 / 0.3217 |
| UNRATE | STAR | 704 | 0.592 | 0.216 | 0.5874 / 0.0015 |
| INDPRO | AR | 715 | 13.311 | 7.072 | — / — |
| INDPRO | ARMA | 715 | 11.974 | 6.582 | 0.2658 / 0.2469 |
| INDPRO | MSAR | 715 | 11.638 | 6.449 | 0.2317 / 0.1212 |
| INDPRO | STAR | 715 | 7171487.326 | 268287.545 | n.u. / n.u. |
| FEDFUNDS | AR | 625 | 0.475 | 0.192 | — / — |
| FEDFUNDS | ARMA | 618 | 0.477 | 0.192 | 0.9694 / 0.3354 |
| FEDFUNDS | MSAR | 625 | 0.480 | 0.192 | 0.4989 / 0.9868 |
| FEDFUNDS | STAR | 625 | 0.613 | 0.227 | 0.1217 / 0.0292 |
| M2SL | AR | 571 | 5.077 | 2.899 | — / — |
| M2SL | ARMA | 571 | 5.083 | 2.899 | 0.4263 / 0.8275 |
| M2SL | MSAR | 571 | 5.127 | 2.892 | 0.2364 / 0.8711 |
| M2SL | STAR | 571 | 82.745 | 6.637 | n.u. / 0.3004 |

*Source: Author's computations.* *Note:* The n and RMSE/MAE columns use each model's own retained forecast dates. The HLZ p-values in the last column refer to **pairwise dates matched to the AR comparator**, which can differ from the own-valid n shown in the table. The loss differential is competitor loss minus AR loss. A positive differential favors AR; a negative differential favors the competitor. The reported p-values are two-sided. “n.u.” denotes a test that is **numerically uninformative** because extreme STAR losses produce the documented degenerate comparison; it is not statistical evidence for equal accuracy. Significance is not the same as a forecast model's lowest descriptive RMSE.

The unemployment rows especially require care: AR, ARMA, MSAR and STAR do not retain identical valid dates. The raw ARMA RMSE is strongly affected by its included pandemic target dates; the AR-matched out-of-sample (R^2) is calculated on a different intersection. Conclusions about which model is better must identify this conditioning.

## B.4 Expansions and recessions

**Table B.4. One-step accuracy by retrospective NBER phase (n; RMSE; MAE)**

| Target | Model | Expansion n, RMSE, MAE | Recession n, RMSE, MAE |
|---|---|---|---|
| GDPC1 | AR | 174; 4.725; 1.995 | 23; 8.382; 5.258 |
| GDPC1 | ARMA | 174; 4.676; 1.996 | 23; 8.387; 5.263 |
| GDPC1 | MSAR | 174; 3.666; 1.937 | 23; 8.231; 5.282 |
| GDPC1 | STAR | 174; 4.128; 2.029 | 23; 9.790; 5.799 |
| CPIAUCSL | AR | 630; 2.678; 1.923 | 85; 4.570; 3.289 |
| CPIAUCSL | ARMA | 630; 2.771; 2.018 | 85; 4.759; 3.491 |
| CPIAUCSL | MSAR | 630; 2.683; 1.935 | 85; 4.546; 3.300 |
| CPIAUCSL | STAR | 630; 4.285; 2.106 | 85; 15603566778.098; 1692444445.975 |
| UNRATE | AR | 618; 0.404; 0.150 | 85; 1.150; 0.301 |
| UNRATE | ARMA | 605; 0.657; 0.167 | 84; 1.160; 0.310 |
| UNRATE | MSAR | 615; 0.266; 0.137 | 83; 1.227; 0.311 |
| UNRATE | STAR | 619; 0.467; 0.203 | 85; 1.147; 0.307 |
| INDPRO | AR | 630; 11.355; 6.442 | 85; 23.127; 11.741 |
| INDPRO | ARMA | 630; 9.564; 5.773 | 85; 22.979; 12.575 |
| INDPRO | MSAR | 630; 9.294; 5.762 | 85; 22.343; 11.545 |
| INDPRO | STAR | 630; 1930.257; 98.883 | 85; 20799494.461; 2256038.805 |
| FEDFUNDS | AR | 559; 0.325; 0.145 | 66; 1.115; 0.587 |
| FEDFUNDS | ARMA | 554; 0.327; 0.146 | 64; 1.128; 0.592 |
| FEDFUNDS | MSAR | 559; 0.334; 0.147 | 66; 1.112; 0.567 |
| FEDFUNDS | STAR | 559; 0.409; 0.170 | 66; 1.462; 0.710 |
| M2SL | AR | 513; 3.838; 2.593 | 58; 11.113; 5.608 |
| M2SL | ARMA | 513; 3.825; 2.591 | 58; 11.180; 5.618 |
| M2SL | MSAR | 513; 3.953; 2.587 | 58; 10.983; 5.589 |
| M2SL | STAR | 513; 4.505; 2.775 | 58; 259.280; 40.801 |

*Source: Author's computations.* *Note:* The state assigned to each **target date** is based on the subsequently established NBER chronology. For GDP, any recession month within the quarter classifies that quarter as recession-affected under the declared rule. Within each row the n counts refer to valid forecasts for that model and state; they are not necessarily identical across model families. The descriptive recession RMSE differences do not establish that a model had a usable real-time signal for recognizing the recession.

## B.5 Peaks and troughs

**Table B.5. One-step peak- and trough-neighborhood errors (n; RMSE; MAE)**

| Target | Model | Peak-window n, RMSE, MAE | Trough-window n, RMSE, MAE |
|---|---|---|---|
| GDPC1 | AR | 18; 3.424; 2.560 | 18; 15.430; 7.771 |
| GDPC1 | ARMA | 18; 3.425; 2.549 | 18; 15.272; 7.713 |
| GDPC1 | MSAR | 18; 3.520; 2.681 | 18; 12.003; 6.930 |
| GDPC1 | STAR | 18; 3.307; 2.417 | 18; 14.494; 8.258 |
| CPIAUCSL | AR | 56; 3.802; 2.655 | 56; 3.616; 2.763 |
| CPIAUCSL | ARMA | 56; 4.418; 3.197 | 56; 3.549; 2.755 |
| CPIAUCSL | MSAR | 56; 3.853; 2.768 | 56; 3.549; 2.705 |
| CPIAUCSL | STAR | 56; 19223804150.471; 2568888889.929 | 56; 4.006; 2.985 |
| UNRATE | AR | 55; 1.414; 0.337 | 55; 1.483; 0.437 |
| UNRATE | ARMA | 56; 2.395; 0.589 | 55; 2.442; 0.694 |
| UNRATE | MSAR | 56; 1.500; 0.379 | 52; 1.695; 0.526 |
| UNRATE | STAR | 56; 1.467; 0.394 | 56; 1.786; 0.631 |
| INDPRO | AR | 56; 29.158; 11.452 | 56; 34.835; 17.618 |
| INDPRO | ARMA | 56; 29.451; 12.045 | 56; 32.397; 16.199 |
| INDPRO | MSAR | 56; 26.908; 11.018 | 56; 31.105; 16.139 |
| INDPRO | STAR | 56; 31.261; 12.545 | 56; 25625256.984; 3424532.436 |
| FEDFUNDS | AR | 42; 0.868; 0.520 | 49; 1.116; 0.484 |
| FEDFUNDS | ARMA | 41; 0.869; 0.513 | 48; 1.127; 0.492 |
| FEDFUNDS | MSAR | 42; 0.854; 0.499 | 49; 1.118; 0.471 |
| FEDFUNDS | STAR | 42; 0.861; 0.518 | 49; 1.141; 0.488 |
| M2SL | AR | 42; 11.995; 5.655 | 42; 13.661; 6.923 |
| M2SL | ARMA | 42; 12.082; 5.669 | 42; 13.690; 6.923 |
| M2SL | MSAR | 42; 11.740; 5.529 | 42; 13.809; 6.943 |
| M2SL | STAR | 42; 12.983; 6.342 | 42; 304.753; 55.728 |

*Source: Author's computations.* *Note:* The primary turning neighborhood is (pm3) months for monthly targets, and (pm1) quarter for GDP. Neighboring windows can overlap. The listed n counts refer to scored forecasts in the retrospective neighborhoods, not the number of historically distinct recession turning points. The same observation may belong to a peak- and trough-neighborhood in the rare case of overlapping windows, so peak and trough rows are not necessarily mutually exclusive partitions of the sample. Alternative window widths are evaluated in Appendix C.

## B.6 State-loss regression: the precise hypothesis

**Table B.6. One-step squared-loss regression tests against the AR benchmark**

| Target | Competitor | n paired | Joint Wald p | State-slopes Wald p | Recession slope p | Turning slope p |
|---|---|---:|---:|---:|---:|---:|
| GDPC1 | ARMA | 197 | 0.4597 | 0.5801 | 0.2974 | 0.2977 |
| GDPC1 | MSAR | 197 | 0.5673 | 0.5334 | 0.3484 | 0.3149 |
| GDPC1 | STAR | 197 | 0.5916 | 0.4312 | 0.2110 | 0.4211 |
| CPIAUCSL | ARMA | 715 | 0.0838 | 0.1810 | 0.8544 | 0.2681 |
| CPIAUCSL | MSAR | 715 | 0.9786 | 0.9174 | 0.7740 | 0.9447 |
| CPIAUCSL | STAR | 715 | 0.7978 | 0.6024 | 0.3161 | 0.3169 |
| UNRATE | ARMA | 688 | 0.0343 | 0.2820 | 0.1169 | 0.9983 |
| UNRATE | MSAR | 697 | 0.2484 | 0.1620 | 0.9744 | 0.1326 |
| UNRATE | STAR | 703 | 0.5665 | 0.3763 | 0.2152 | 0.1667 |
| INDPRO | ARMA | 715 | 0.1969 | 0.6134 | 0.3363 | 0.4524 |
| INDPRO | MSAR | 715 | 0.0866 | 0.5437 | 0.3600 | 0.2718 |
| INDPRO | STAR | 715 | 0.7978 | 0.6024 | 0.3161 | 0.3169 |
| FEDFUNDS | ARMA | 618 | 0.2356 | 0.2219 | 0.6497 | 0.0832 |
| FEDFUNDS | MSAR | 625 | 0.8554 | 0.8501 | 0.5688 | 0.8136 |
| FEDFUNDS | STAR | 625 | 0.2077 | 0.5421 | 0.3073 | 0.2848 |
| M2SL | ARMA | 571 | 0.5920 | 0.4012 | 0.1801 | 0.7585 |
| M2SL | MSAR | 571 | 0.7327 | 0.5312 | 0.2775 | 0.4900 |
| M2SL | STAR | 571 | 0.7961 | 0.6001 | 0.3152 | 0.3168 |

*Source: Author's computations.* *Note:* The joint Wald hypothesis sets the intercept and both recession and turning slopes to zero. The slopes-only hypothesis tests only the two state-difference terms. A joint rejection does **not** imply a state effect if the slope test does not reject. In the unemployment ARMA comparison the nominal joint p-value is around 0.034, but the slopes-only p-value is around 0.282. These ex-post state variables are not necessarily in the forecast-origin information set. The regression is a retrospective association, not a validated implementable conditional switching rule.

## B.7 Multiple-model confidence sets

**Table B.7. One-step squared-loss model confidence set at 90%**

| Target | Model | MCS inclusion at 90% | MCS p-value | Common dates |
|---|---|---|---:|---:|
| GDPC1 | AR | Yes | 0.5906 | 197 |
| GDPC1 | ARMA | Yes | 0.5906 | 197 |
| GDPC1 | MSAR | Yes | 1.0000 | 197 |
| GDPC1 | STAR | Yes | 0.5742 | 197 |
| CPIAUCSL | AR | Yes | 0.9750 | 715 |
| CPIAUCSL | ARMA | Yes | 0.2832 | 715 |
| CPIAUCSL | MSAR | Yes | 1.0000 | 715 |
| CPIAUCSL | STAR | Yes | 0.3310 | 715 |
| UNRATE | AR | Yes | 0.6376 | 682 |
| UNRATE | ARMA | Yes | 1.0000 | 682 |
| UNRATE | MSAR | Yes | 0.6376 | 682 |
| UNRATE | STAR | Yes | 0.2398 | 682 |
| INDPRO | AR | Yes | 0.3022 | 715 |
| INDPRO | ARMA | Yes | 0.3022 | 715 |
| INDPRO | MSAR | Yes | 1.0000 | 715 |
| INDPRO | STAR | Yes | 0.3022 | 715 |
| FEDFUNDS | AR | Yes | 0.9690 | 618 |
| FEDFUNDS | ARMA | Yes | 1.0000 | 618 |
| FEDFUNDS | MSAR | Yes | 0.7054 | 618 |
| FEDFUNDS | STAR | Yes | 0.1880 | 618 |
| M2SL | AR | Yes | 1.0000 | 571 |
| M2SL | ARMA | Yes | 0.4102 | 571 |
| M2SL | MSAR | Yes | 0.4102 | 571 |
| M2SL | STAR | Yes | 0.4102 | 571 |

*Source: Author's computations.* *Note:* Inclusion in the model confidence set means that the corresponding elimination procedure has not excluded that model at the stated confidence level on the intersection of all compared forecasts. It does not prove predictive equivalence, and in the presence of explosive STAR loss differentials the procedure can have limited discrimination. These results support, rather than replace, the primary AR-paired HLZ inference.
