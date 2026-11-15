# List of Abbreviations and Mathematical Notation

The definitions below apply throughout the dissertation. A symbol with an additional superscript or model subscript retains its basic meaning unless explicitly identified as a different quantity in the nearby equation. Variables and symbols are also defined at first substantive use in the text; this list is a reference, **not** a substitute for the definitions needed to understand the equations in Chapters 1 and 2.

## Abbreviations

| Abbreviation | Meaning |
|---|---|
| ADF | Augmented Dickey–Fuller unit-root test |
| AIC | Akaike information criterion |
| ALFRED | Archival Federal Reserve Economic Data |
| AR | Autoregressive model |
| ARCH | Autoregressive conditional heteroskedasticity |
| ARMA | Autoregressive moving-average model |
| BIC | Bayesian information criterion (Schwarz criterion) |
| CPI | Consumer Price Index |
| CPIAUCSL | FRED identifier for the U.S. CPI for All Urban Consumers, All Items, seasonally adjusted |
| DM / DM–HLN | Diebold–Mariano forecast-accuracy test / its Harvey–Leybourne–Newbold small-sample modification |
| ESTAR | Exponential smooth-transition autoregression |
| FEDFUNDS | FRED identifier for the effective federal funds rate |
| FRED | Federal Reserve Economic Data |
| GARCH | Generalized autoregressive conditional heteroskedasticity |
| GDP / GDPC1 | Gross domestic product / FRED identifier for U.S. real GDP |
| GW | Giacomini–White conditional predictive ability literature; state-conditioned loss regression here uses *ex-post* indicators |
| HAC | Heteroskedasticity and autocorrelation consistent |
| HLZ | Harvey–Leybourne–Zu test of equal average forecast accuracy in possibly unstable environments |
| INDPRO | FRED identifier for the U.S. industrial production index |
| KPSS | Kwiatkowski–Phillips–Schmidt–Shin stationarity test |
| LOCF | Last observation carried forward |
| LSTAR | Logistic smooth-transition autoregression |
| MAE | Mean absolute error |
| MCS | Model confidence set |
| MIDAS | Mixed-data sampling regression |
| M2 / M2SL | Broad U.S. monetary aggregate M2 / its seasonally adjusted FRED series identifier |
| MSAR | Markov-switching autoregression |
| NBER | National Bureau of Economic Research |
| OOS | Out of sample |
| RMSE | Root mean squared error |
| SA / SAAR | Seasonally adjusted / seasonally adjusted annual rate |
| STAR | Smooth-transition autoregression |
| UNRATE | FRED identifier for the seasonally adjusted U.S. unemployment rate |
| USREC | FRED/NBER-based monthly U.S. recession indicator, used retrospectively |
| VAR | Vector autoregression |
| ZA | Zivot–Andrews unit-root test allowing an endogenous break |

## Mathematical notation

| Symbol | Definition and scope |
|---|---|
| $t$, $h$ | Historical date index and forecast horizon (months except for quarterly GDP) |
| $i$ | Aggregate index when used in $y_{i,t}$; otherwise the context identifies the interest-rate variable $i_t$ |
| $X_t$ | Positive original level underlying a log-growth target |
| $W_t$ | Nominal wage index in the Phillips relationship (Equation 1.3) |
| $M_t$, $V_t$, $P_t$, $Y_t$ | Money aggregate, income velocity, aggregate output-consistent price level and real output in the quantity identity (Equation 1.7) |
| $Y_t^{*}$ | Reference or potential real output in the stylized level form of Okun's law (Equation 1.6) |
| $y_t$ | Generic scalar transformed forecasting target |
| $g_t^{(f)}$ | Annualized one-period log growth at native frequency $f$; monthly scale 1,200 and quarterly scale 400 |
| $E_t(\cdot)$, $r_t^{e}$, $r_t$ | Conditional expectation formed at $t$, expected real return and period-realized real return in the Fisher equations (1.1–1.2) |
| $\pi_t$ | Monthly CPI inflation in annualized log-change percentage-point units |
| $g_t^{GDP}$ | Quarterly real GDP log growth in annualized percentage-point units |
| $g_t^{IP}$ | Industrial production monthly annualized growth |
| $u_t$ | U.S. unemployment rate, in percent; the forecast-loss regression disturbance is written $\xi_t$ |
| $u_t^{*}$ | Reference or natural unemployment rate in stylized Phillips and Okun relationships |
| $i_t$, $\Delta i_t$ | Effective federal funds rate in percent, and its one-month percentage-point change |
| $g_t^{M2}$ | Monthly annualized M2 growth |
| $\mathcal F_t$ | Information sigma-field available at the stated forecast origin |
| $w_f$, $\mathcal W_t^{(w_f)}$ | Number of rolling-estimation observations at frequency $f$ and corresponding historical estimation window; $w_M=240$, $w_Q=120$ |
| $\widehat y^{(m)}_{t+h\mid t}$ | Model $m$'s forecast of a target at $t+h$ issued at $t$ |
| $e_{m,t}$ | Target realization minus model $m$'s forecast, with date/horizon subscripts suppressed where unambiguous |
| $p$, $q$ | Autoregressive and moving-average lag orders |
| $K$, $L$ | Number of latent Markov regimes ($K$) and maximum Ljung–Box residual-autocorrelation lag ($L$); they are different indices |
| $d_m$, $K_u$, $S$ | Residual serial-dynamics degree-of-freedom adjustment, sample kurtosis and sample skewness in the adequacy diagnostics (Section 2.8) |
| $\phi_j$, $\theta_j$ | Generic autoregressive and moving-average coefficients; $\boldsymbol\theta$ in STAR denotes the incremental transition coefficient vector |
| $\boldsymbol\phi$, $x_t$, $z_{t-d}$ | STAR baseline coefficient vector, intercept-and-lag regressor vector, and observed transition variable delayed by $d$ periods |
| $c$ | Generic intercept or STAR threshold, distinguished by equation context; $\gamma$ is a STAR transition-slope parameter |
| $\varepsilon_t$ | Scalar stochastic innovation in an AR, ARMA, MSAR or STAR equation |
| $\eta_t$, $\nu_t$ | Disturbances in the two stylized Okun relationships (Equations 1.5–1.6) |
| $\kappa$, $\alpha$, $\beta$, $\theta$ | Equation-specific stylized Phillips/Okun sensitivity or intercept coefficients; these symbols are re-used with distinct definitions in the forecasting equations |
| $\rho$, $\psi_j$, $v_t$ | Unit-root coefficient, lagged-difference coefficients and disturbance in the ADF auxiliary regression (Equation 2.3) |
| $\sigma^2$, $\sigma_t^2$ | Constant innovation variance and time-varying conditional innovation variance |
| $\omega$, $\alpha$, $\beta$ (GARCH) | Variance intercept, lagged squared-innovation effect and lagged conditional-variance effect in Equation (2.8); these coefficients are distinct from similarly named coefficients in the stylized economic equations |
| $\zeta_t$ | Supply or price-setting disturbance in the stylized Phillips–Phelps equation (1.4); distinct from the latent Markov state |
| $s_t\in\{1,\ldots,K\}$ | Unobserved Markov state (the same lowercase symbol in Chapters 2, 3 and 4) |
| $\mu_k$ | Mean parameter of Markov state $k$ |
| $p_{ij}$ | Markov transition probability from state $i$ to state $j$ |
| $\mathbf P$ or $P$ | Markov transition matrix with row sums equal to one |
| $\widehat p_{t,k}$ | Smoothed posterior probability of state $k$ at date $t$ in the full historical sample; distinct from $p_{ij}$ |
| $\widehat n_k$, $\widehat\omega_k$ | Effective state observation count and smoothed state occupancy proportion |
| $\widehat D_k$ | Expected uninterrupted duration of the fitted state |
| $G(z_{t-d};\gamma,c)$ | Logistic or exponential STAR transition function with delay $d$ |
| $\mathbf y_t$, $\mathbf A_j$, $\mathbf c$, $\boldsymbol\varepsilon_t$ | VAR target column vector, lag coefficient matrices, intercept vector and reduced-form innovation vector |
| $\ell_m$, $\widehat\vartheta_m$, $k_m$, $n$ | Maximized model log-likelihood, associated fitted parameter vector, number of estimated parameters and effective in-sample observation count in the information-criterion definition; $\widehat\vartheta$ without $m$ denotes a fitted MSAR vector in Equation (2.21) |
| $L(e)$, $d_t^{(m,b)}$ | Forecast loss and signed competitor-minus-benchmark loss differential |
| $R^2_{\mathrm{OOS},m\mid AR}$ | Out-of-sample squared-error reduction relative to AR, computed only over pairwise common valid target dates |
| $\rho_{\varepsilon}(\ell)$ | Residual autocorrelation at lag $\ell$ in the Ljung–Box joint null |
| $REC_t$, $TURN_t$ | Retrospectively classified recession and turning-window dummy variables |
| $\alpha$, $\beta_{\mathrm{rec}}$, $\beta_{\mathrm{turn}}$, $\xi_t$ | Intercept, recession/turning slopes and disturbance in the *state-loss regression*; $\xi_t$ prevents confusion with unemployment $u_t$ |
| $\mathcal I_{m,AR}$ | Forecast target dates common to model $m$ and AR for their pairwise squared-loss comparison |
| $N$, $N^{\mathrm{attempted}}$, $N^{\mathrm{retained}}$ | Evaluation count, number of attempted estimates and number of retained forecast values, with model/horizon subscripts when needed |
| $\widehat A_{m,h}$ | Observed share of attempted forecasts retained by model $m$ at horizon $h$ (Equation 4.6) |

## Consistent reporting conventions

All reported rates and target transformations retain the units defined in Chapter 2. State identifiers are statistical labels, not automatically economic recession or policy states. The Markov transition matrix is row-stochastic and inferred states may be smoothed in full-sample descriptions but filtered for forecast-time prediction. A loss-test p-value reflects the stated null, sample and loss; non-rejection does not establish forecasting equivalence. When significance stars are required in final tables, they must be typeset as superscripts with one explicit legend; unstarred numerical p-values are preferable whenever available.

Acronyms, mathematical symbols, fitted equations and final appendix table titles must be checked together during paginated manuscript assembly to prevent changes in meaning between chapters.
