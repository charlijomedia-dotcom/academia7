# Part I: From Macroeconomic Instability to a Testable Forecasting Problem

# Chapter 1: Why Macroeconomic Relationships Become Unstable: Fisher, Phillips, Okun and the Forecasting Problem

The General Introduction established a narrow question with a broad economic motivation. Forecasts inform decisions made before inflation, employment, output, and financial conditions are known. However, a model that describes earlier observations well may not predict later observations with comparable accuracy. This chapter examines the economic reasons why the relationships underlying those forecasts can change. It does not presume that economic instability always requires a nonlinear statistical model. Its purpose is to show when state dependence is plausible, what existing research has already established, and which observations would instead favor simpler explanations.

The argument proceeds from economic decisions to theory and then to testable forecasting implications. Fisherian interest-rate relations, the Phillips–Phelps account of inflation and unemployment, Okun's output–unemployment relation, and monetary transmission identify mechanisms connecting the selected aggregates. Innovation, policy changes, and abrupt shocks explain why past relationships may fail to persist. Statistical concepts then distinguish temporary shocks, persistent breaks, latent regimes, smooth adjustment, and changing volatility. The final sections examine competing forecasting approaches and define the burden of proof for a nonlinear model. This sequence provides the economic foundation for the controlled forecasting experiment developed in Chapter 2.

## 1.1 Forecasting as a Policy Problem under Inflation, Conflict, Debt Pressure, and Cyclical Instability

Macroeconomic decisions are forward-looking because their effects are not immediate. A central bank must choose its policy stance before the full effects on prices and economic activity are observed. A government prepares spending and borrowing plans before the relevant tax receipts, interest payments, and support needs are known. Firms decide on hiring, capital expenditure, and financing while future demand and credit conditions remain uncertain. Households enter wage agreements, loans, and savings contracts without knowing the purchasing power of future income. Forecasting is therefore not a separate activity performed after an economic decision. It is part of the information problem that precedes that decision.

The General Introduction documented failures to anticipate recessions, inflation, and fiscal outcomes. Those examples establish why the forecasting problem matters; they do not need to be repeated in detail here. An et al. (2018) show that recession forecasts often recognize economic contractions too late to serve as reliable advance warnings. Bernanke (2024) identifies both difficult shocks and weaknesses in the forecasting systems used for monetary-policy decisions. The Office for Budget Responsibility (2026) illustrates how fiscal projections depend on several uncertain economic and policy inputs. Together, these studies motivate closer examination of the mechanisms that make macroeconomic forecasts vulnerable. None establishes that forecast errors alone caused a recession, a loss of real wages, or a fiscal deficit.

Consider a rise in imported energy costs. The direct price increase may raise consumer inflation even if domestic demand weakens. Firms using energy as an input may reduce production or margins. Workers may seek wage adjustments after purchasing power falls. A central bank concerned about inflation may change the expected future path of short-term interest rates. Government debt-service costs may also change, depending on debt maturity and market rates. The shock thus affects prices, activity, employment, and financing through distinct channels. The immediate movements need not have the same signs as their later adjustments. A forecasting method fitted to a previous demand-led expansion may struggle when the disturbance comes mainly from supply.

Conflict and geopolitical disruption create a related identification problem. A conflict may disturb shipping, commodity supply, confidence, or international demand. The resulting movements in inflation and production need not resemble those associated with a domestic demand shock. An observed rise in prices therefore contains incomplete information about the origin and persistence of inflation. A model that relies only on a series' own past cannot directly observe every external disturbance. Even a flexible nonlinear specification may mistake a rare shock for evidence that the underlying process has entered a recurring regime. This distinction matters for the interpretation of estimated nonlinear states.

Debt pressure makes forecast uncertainty consequential through another channel. Expected inflation, real rates, and risk premia affect nominal financing conditions. Revisions to expected economic activity affect the anticipated tax base. A government with large refinancing needs can face difficult choices even if actual spending plans have not changed. Yet forecasting a higher public borrowing requirement does not identify which fiscal decision is optimal. The objective in this thesis is to compare information supplied by forecasting models, not to infer the welfare effects of government borrowing or recommend a fiscal rule.

Cyclical instability raises a timing problem. A recession is not simply a low observation in one series; it is a broad decline in economic activity that develops across indicators. Output can contract before unemployment reaches its maximum, while the policy rate may be adjusted in anticipation of later conditions. A recovery can begin before the labour market has fully improved. Consequently, forecasts for output, unemployment, and interest rates can be wrong in different directions over the same months. This is one reason to examine forecast errors by target and by economic state rather than aggregate all errors into a single assertion about the economy.

The information set is as important as the model. A forecast issued in month $t$ can use only information available at that point. Some macroeconomic observations are released with delay and later revised. Orphanides (2001) demonstrates that assessments of monetary-policy rules can differ when the historical information available to policymakers replaces later-revised data. Thus a model may have excellent apparent performance in an exercise that inadvertently uses revised future information. The present thesis uses a single frozen historical data vintage in a pseudo-out-of-sample design. It is not a reconstruction of the entire sequence of real-time vintages. This distinction is preserved throughout the dissertation because it limits claims about operational real-time forecasting.

Forecast usefulness also depends on the decision horizon. A one-month inflation prediction may be relevant for near-term monitoring, while an annual inflation outlook bears on different contracts and policy assessments. Changes in unemployment may arrive more slowly than changes in industrial production. Quarterly GDP provides a broader activity measure but cannot be observed on the same calendar as every monthly indicator. One forecasting model cannot be called generally superior without identifying its target, horizon, loss measure, and available information. The thesis therefore treats the forecasting question as several comparable, clearly delimited tasks rather than one undifferentiated test of accuracy.

The United States offers an informative setting for this inquiry. Its postwar record contains repeated recessions and recoveries, high- and low-inflation episodes, monetary-policy shifts, financial disruption, and the exceptional movements surrounding 2020. The Federal Reserve's operating framework supplies an identifiable short-term policy-rate measure. Official statistical agencies provide long series for consumer prices, unemployment, industrial production, and real GDP, while the Federal Reserve provides monetary aggregates. Federal Reserve Economic Data and its archival counterpart, ALFRED, permit dated retrieval of historical observations. These attributes are useful for comparing models across long rolling samples. The United States is selected for measurement quality and varied economic episodes, not because its model rankings can be assumed to hold internationally.

The six forecast targets reflect this economic logic. Consumer price index inflation represents household-facing price changes. Real GDP growth and industrial production growth describe different aspects and frequencies of real activity. Unemployment measures an important labour-market outcome. The effective federal funds rate represents short-term monetary-policy conditions, and M2 growth describes a broad monetary aggregate. Their official measurement definitions and transformations belong in Chapter 2. Their presence here follows from the mechanisms investigated in the next sections. The monthly indicators are not substitutes for quarterly GDP, and M2 is not assumed to control prices mechanically.

Three propositions follow from this policy setting. First, instability matters for prediction because different shocks and institutional responses can alter persistence, timing, and the distribution of forecast errors. Second, accurate forecasting is useful but is not the same as effective policy; economic decisions also require objectives, causal mechanisms, and judgment. Third, greater model flexibility is justified only when it produces defensible information that the simpler model fails to capture. The next sections examine the theoretical relations that make that final proposition testable.

## 1.2 Fisherian Relations between Inflation, Nominal Rates, Real Rates, and Expectations

The interest rate reported in an economic data series is usually nominal. Its economic meaning depends partly on the future purchasing power of money. Fisher (1930) formalized the relation between nominal and real returns and the expected change in prices. In the standard one-period, low-inflation approximation, the ex ante relation is

**Equation (1.1)**

```math
i_t \simeq r_t^{e}+E_t(\pi_{t+1}),
```

where $i_t$ is the nominal interest rate applying to the period, $r_t^{e}$ is the expected real return for a comparable claim and maturity, $E_t(\pi_{t+1})$ is expected inflation over the same period, and $E_t(\cdot)$ denotes the expectation formed with information available at $t$. The approximation neglects cross-products and the complications associated with uncertainty and risk premia. It is not an empirical identity that forces a constant real rate.

Under certainty, and with exactly matched gross returns, the corresponding multiplicative relation is

**Equation (1.2)**

```math
1+i_t=(1+r_t)(1+\pi_{t+1}).
```

When inflation is uncertain, defining an ex ante real return requires care. In general, the expected purchasing-power return is based on $E_t[(1+i_t)/(1+\pi_{t+1})]$, not merely the ratio of the nominal gross return to one plus expected inflation. Nonlinear expectation effects, tax treatment, maturity, default risk, liquidity, and inflation risk premia can make observed nominal yields deviate from the simple expression in (1.1). The approximation remains useful because it isolates two objects that a forecast must distinguish: expected inflation and the required real compensation for postponing consumption.

A simple example illustrates the issue. Suppose a nominal one-year rate is 6 percent and expected one-year inflation is 2 percent. The approximate expected real return is 4 percent. If expected inflation rises to 5 percent with the nominal rate unchanged, the approximation gives an expected real return near 1 percent. Yet an observed increase in the nominal rate cannot be interpreted mechanically as an increase in real borrowing costs. It may partly reflect an increase in expected inflation or a risk premium. A forecast of nominal rates therefore depends on beliefs about future prices and on financial conditions that are not contained in the nominal rate alone.

This interdependence complicates forecasting over time. Expectations may respond gradually to public information in one period and abruptly in another. An inflation target that is viewed as credible may anchor expected medium-term inflation even when current inflation rises. A period of sustained inflation surprises can lead households and markets to revise those expectations. The same observed inflation rate may then be associated with different nominal-rate paths. A linear model using only past values of the policy rate may describe the average response but fail near a change in beliefs or the monetary-policy environment. This is a theoretical possibility, not a claim that the thesis directly measures expectations.

The expected real interest rate is also relevant to economic activity. Holding other conditions fixed, a higher real financing cost can discourage some investment and interest-sensitive consumption. But a higher nominal rate can accompany stronger demand, greater inflation expectations, or a policy response to rising inflation. Observed co-movement cannot distinguish these explanations. A forecast model that improves the prediction of FEDFUNDS does not identify a monetary-policy shock or quantify its effect on output. The Fisher relation provides economic interpretation of the variables, not a causal identification strategy for this dissertation.

The choice of the effective federal funds rate as a target requires a further distinction. FEDFUNDS is the observed monthly average of an overnight market rate, whereas equation (1.1) is most naturally interpreted for a return and an inflation expectation over a matched period. One should not insert annual consumer-price inflation next to a monthly average overnight rate and describe the result as an exact observed real interest rate. The series are related economically, but maturity, units, policy expectations, and aggregation differ. Chapter 2 therefore treats the effective federal funds rate as a distinct forecast target. It does not construct an empirical real interest rate by combining observations with incompatible maturities, units, or reference periods.

There are at least three plausible sources of changing rate dynamics. The first is changing inflation expectations, which alter the nominal rate compatible with a given expected real return. The second is changing monetary-policy behavior, as policymakers react to inflation, activity, and financial conditions. The third is a constraint on the rate itself. When short-term nominal rates approach an effective lower bound, further downward movement may become limited even though the economy remains weak. A linear relation estimated during periods of unconstrained rate changes may not describe observations near that bound.

Taylor (1993) provides an influential example of systematic monetary-policy responses to inflation and real economic conditions. Its contribution here is not an instruction to estimate a Taylor rule, but a reminder that the observed short-term rate is partly a policy reaction variable. A rate increase may follow inflationary pressure, and a rate reduction may follow weak activity. Because policy responds to the economy, using a rate as a predictor or a forecast target involves feedback. An autoregression can summarize the historical persistence of this response without separating its causes.

Recent work makes the lower-bound issue concrete. Carriero et al. (2025) develop shadow-rate vector autoregressions that treat observed rates as constrained measurements of latent rates. Their U.S. application reports better interest-rate forecasts than conventional VAR alternatives, with broadly similar performance for several other macroeconomic variables. This is evidence that a carefully specified constraint may matter for forecasting. It is not evidence that a generic two-regime Markov-switching model must perform well, nor does it imply that an observed effective federal funds rate and a constructed shadow rate are interchangeable forecasting targets. The competing mechanisms differ: an occasionally binding constraint is not the same object as an unrestricted latent business-cycle state.

Risk and financial structure introduce further variation. If lenders demand more compensation for uncertainty or if borrowers' balance sheets deteriorate, financing costs can change independently of expected consumer-price inflation. Financial stress can therefore weaken a simple correspondence between the federal funds rate and borrowing costs faced by firms. Such episodes may coincide with policy easing, so a declining policy rate and tighter credit conditions are not contradictory observations. This distinction becomes important when assessing whether past policy-rate values contain enough information to predict future rates.

Fisherian reasoning also helps clarify forecast evaluation. Suppose a nonlinear model predicts rate reversals more accurately in one subsample. This could arise from changing expectations, policy reaction patterns, a lower-bound constraint, or statistical overfitting. A forecast-accuracy test alone cannot choose among those explanations. The relevant empirical question is whether the additional flexibility improves forecasts within the defined information set and whether the result withstands the stated robustness tests. The economic mechanism motivates the test; it does not predetermine its result.

The central implication of this section is therefore conditional. Nominal-rate dynamics can change because inflation expectations, desired real returns, financial premia, policy behavior, and constraints change. The Fisher relation makes those distinctions explicit and explains why the policy rate belongs in the thesis. It does not establish a stable inflation-to-rate coefficient, a unique causal direction, or the superiority of nonlinear forecasting. The next section develops a second set of mechanisms linking inflation to labour-market conditions and real activity.

## 1.3 Phillips–Phelps and Okun Mechanisms Linking Inflation, Unemployment, and Output

Inflation, unemployment, and real activity are connected through labour demand, wage formation, production, expectations, and the response of economic policy. Their observed movements are nevertheless not governed by one fixed equation. The classic Phillips relation, its expectations-augmented interpretation, and Okun's relation provide a compact framework for understanding both the connections and their limitations. They also explain why this thesis includes price inflation, unemployment, quarterly GDP growth, and monthly industrial production growth as distinct forecast targets.

### Wage adjustment and the original Phillips relation

Phillips (1958) examined the association between unemployment and the rate of change of money wages in the United Kingdom over a long historical period. The original dependent variable was wage inflation, not the consumer price inflation used in this thesis. Phillips described a nonlinear empirical relation in which wages tended to rise more quickly when unemployment was low and more slowly when unemployment was high. In stylized terms, that relationship can be written as

**Equation (1.3)**

```math
\Delta \ln W_t=f(u_t)+\varepsilon_t,\qquad f'(u_t)<0,
```

where $W_t$ is a nominal wage index, $u_t$ is the unemployment rate, $f$ describes the historical association, and $\varepsilon_t$ collects factors not represented by the curve. The inequality describes the local direction of the fitted relation in the relevant range. It does not guarantee one stable slope over all dates and countries. In the original historical analysis, nonlinearity of the wage response was part of the empirical description. It should not be rewritten as a universal straight-line relation between CPI inflation and unemployment.

The economic interpretation is intuitive but incomplete. When labour is scarce relative to employer demand, workers may have greater bargaining power and firms may raise wages to recruit staff. When unemployment is high, nominal wage increases may be weaker. Yet wages also depend on productivity, bargaining institutions, contract duration, labour-force composition, and expected price changes. Firms set consumer prices using costs beyond wages, including energy, imported inputs, and margins. Consequently, translating a wage–unemployment relation directly into CPI inflation requires additional assumptions about wage-to-price pass-through and other cost pressures.

### Expectations and the Phillips–Phelps relation

Phelps (1967) showed why inflation expectations alter the interpretation of unemployment–inflation trade-offs. A commonly used expectations-augmented representation is

**Equation (1.4)**

```math
\pi_t=E_{t-1}(\pi_t)-\kappa(u_t-u_t^{*})+s_t,\qquad \kappa>0,
```

where $\pi_t$ denotes current price inflation, $E_{t-1}(\pi_t)$ is expected inflation formed before the current outcome, $u_t^{*}$ is a reference or natural rate of unemployment, $\kappa$ measures the sensitivity of inflation to unemployment relative to that reference, and $s_t$ is a supply or price-setting disturbance. The expression is a stylized organizing equation, not an identity or the estimated model of this thesis. Different theoretical models use different timing, expectations measures, slack concepts, and disturbance structures.

Equation (1.4) identifies a central source of forecast instability. If inflation expectations change, the inflation rate associated with a particular unemployment rate can also change. A period of well-anchored expectations may show only a small inflation response to a change in unemployment. A period of unanchored expectations or major supply disruption may behave differently. The reference unemployment rate $u_t^{*}$ is also unobserved and may evolve with institutions, demographics, matching efficiency, and labour-market organization. Treating it as a fixed, known threshold would make the statistical problem appear easier than it is.

Friedman (1968) made a related point about the limits of a permanent unemployment–inflation trade-off. Short-run movements associated with unexpected inflation cannot be extrapolated into an indefinitely sustainable ability to keep unemployment below its natural rate. His argument also highlights an identification issue: observed unemployment and inflation reflect expectations and adjustment, not simply a permanent policy-controlled mapping. This insight is relevant to forecast specification because a historical coefficient can change when inflation expectations or policy conduct change.

Lucas (1976) gives the issue an additional dimension. If policy rules change, expectations and decision rules can change with them. Relationships estimated under one policy environment may therefore be unreliable for evaluating a different policy. This is the logic behind the critique of using reduced-form historical equations as fixed causal mechanisms under changing policy. It does not imply that every statistical forecast model must fail after a policy change. It does imply that predictive stability and structural policy invariance are separate claims. The present dissertation tests the former over specified samples and does not assert the latter.

The Phillips relation has also changed empirically. Blanchard (2016) examined U.S. inflation and unemployment and found evidence consistent with more anchored expectations and a flatter Phillips curve than in earlier decades. His paper also emphasized substantial residual uncertainty. A flatter relation creates two possible forecasting problems. Inflation may respond only weakly to ordinary changes in unemployment, making unemployment an imprecise standalone inflation predictor. At the same time, rare supply shocks or shifts in expectations may become relatively important. A model chosen because it can fit an unusually steep historical segment need not outperform a simpler benchmark in subsequent periods.

A flattened curve is not equivalent to a nonlinear curve. A slope may change once after an institutional shift, vary gradually as inflation expectations become anchored, or depend on whether inflation is already high. These possibilities imply different statistical representations. A break model, time-varying parameter model, and threshold model can all describe some forms of change, but they should not be treated as interchangeable economic explanations. Moreover, an AR or ARMA model for inflation does not explicitly observe unemployment or inflation expectations. The theory explains why inflation might be difficult to predict, while a single-equation forecast comparison tests how far the target's own dynamics can go.

### Output, activity, and Okun's relation

Okun (1962) linked changes in unemployment to changes in output and the distance between actual and potential production. One widely used growth-rate representation of this relationship is

**Equation (1.5)**

```math
\Delta u_t=\alpha-\beta g_t+\eta_t,\qquad \beta>0,
```

where $\Delta u_t$ is the change in the unemployment rate, $g_t$ is real output growth over a corresponding period, $\alpha$ captures influences such as the output growth needed to prevent unemployment from rising, $\beta$ is a positive sensitivity coefficient, and $\eta_t$ is a residual. This is a stylized version of an empirical relationship, not a constant coefficient imposed on the thesis data. The intercept and coefficient can depend on the time period, growth convention, data definitions, and business-cycle conditions.

An alternative gap formulation associates unemployment deviations with the output gap. Let $Y_t$ be actual real output and $Y_t^{*}$ an estimate of potential real output. A schematic version is

**Equation (1.6)**

```math
u_t-u_t^{*}=-\theta\bigl(\ln Y_t-\ln Y_t^{*}\bigr)+\nu_t,\qquad \theta>0.
```

The two representations ask different empirical questions. Equation (1.5) links changes in unemployment to output growth, whereas equation (1.6) links estimated deviations from reference levels. Potential output and the natural unemployment rate are not directly observed; they depend on estimation and can be revised. The thesis does not estimate these latent structural reference levels. The forecast targets therefore consist of observed official aggregates or explicitly defined transformations of those aggregates, rather than estimated measures of potential output or the natural unemployment rate.

The relationship can change for understandable economic reasons. During an initial slowdown, firms may retain workers because rehiring is costly or because they regard the loss of demand as temporary. Output may then fall before unemployment rises by the amount suggested by earlier experience. During a later contraction, layoffs may accelerate. In a recovery, firms may increase hours or productivity before adding employment. Labour-force participation and sectoral composition can also alter the measured unemployment response. Each mechanism changes the timing or strength of the output–labour association without requiring a permanent new law of motion.

A numerical example helps separate correlation from a constant rule. If a stylized Okun relation implies that one extra percentage point of real output growth lowers the change in unemployment by $0.3$ percentage points, a different employment response during a recession could reflect labour hoarding, hours adjustment, or composition rather than a mismeasured growth rate. The value $0.3$ is merely illustrative here; it is not an estimate from this dissertation or a universal Okun coefficient. In actual forecasting, the relevant coefficient, interval, and sample would have to be supported empirically. A threshold model might capture a different response during severe contractions, but a lagged linear model could also capture delayed unemployment changes. These alternatives must be compared rather than assumed.

Frequency matters. Real GDP is a comprehensive quarterly measure of domestic production. Industrial production is a narrower monthly measure that responds strongly to some cyclical disturbances and less to activity outside industry. Unemployment is observed monthly. A fall in monthly industrial production need not imply an identical movement in the next quarterly GDP release, particularly when service-sector output behaves differently. It would therefore be methodologically misleading to interpolate quarterly GDP into monthly observations merely to obtain a convenient uniform data matrix. The empirical analysis preserves the original observation frequencies and examines cross-variable forecasting separately as a robustness exercise.

### Joint adjustment and the forecast problem

The Fisher, Phillips–Phelps, and Okun mechanisms interact, but they do not identify one unambiguous forecast sequence. Inflation can rise while unemployment falls in a demand expansion. Inflation can also rise while output contracts after a supply shock. Nominal interest rates may increase in response to inflation, while real financing conditions vary according to expectations and risk premia. Output may recover before unemployment falls. Thus an observed pair of variables can move together in one episode and in opposite directions in another without contradicting the underlying economic theory.

These mechanisms give three competing explanations for apparent statistical state dependence. First, coefficients linking economic variables may genuinely evolve with expectations, policy, technology, or institutions. Second, the same relation may be stable but operate with different lags or face different shocks, leading a short-lag linear model to appear misspecified. Third, a very large observation may distort estimated parameters and make a flexible model fit a small number of dates unusually well. The economic theories alone cannot distinguish these accounts. They motivate a disciplined empirical comparison in which adequate classical benchmarks, nonlinear estimates, and model failures are all visible.

An important boundary must remain clear. A single-equation autoregression for CPI inflation, unemployment, or real GDP growth does not estimate the structural Phillips or Okun coefficient. A Markov-switching state estimated from one variable is not direct evidence that the economy crossed a specific natural-unemployment threshold. Nor does superior forecast performance reveal which shock caused a movement in the series. The value of these theories for Chapter 1 is to identify economically meaningful sources of instability and relevant forecast targets. Chapter 2 specifies how to test whether departures from constant own-history dynamics provide useful predictive information beyond linear benchmarks.


## 1.4 Money, Monetary Transmission, and Competing Macroeconomic Traditions

The previous sections related inflation to expectations, interest rates, unemployment, and output. Money adds a further dimension. Monetary aggregates measure assets used for payments and short-term saving, while the policy rate helps summarize the price of very short-term funds. Both can respond to economic conditions and affect how spending is financed. Yet neither the money stock nor the policy rate has a single invariant relationship with consumer prices or real production. A coherent forecasting argument must therefore explain why M2 and FEDFUNDS are included without assuming that one mechanically determines the other aggregates.

### The monetary identity and its interpretation

The familiar quantity relation can be written as

**Equation (1.7)**

```math
M_tV_t=P_tY_t,
```

where $M_t$ is a specified nominal money aggregate, $V_t$ is its income velocity, $P_t$ is an aggregate price index consistent with the definition of nominal output, and $Y_t$ is real output. With coherent measurement, the expression is an accounting relation defining velocity as nominal income divided by money. In approximate growth rates, it becomes $\Delta\ln M_t+\Delta\ln V_t=\Delta\ln P_t+\Delta\ln Y_t$. An observed rise in money growth does not, by itself, determine how much nominal expenditure, prices, or real output will rise. Velocity and the demand for monetary assets can change. Money holders may retain balances rather than spend them immediately.

The measurement qualification is important. The identity normally concerns a price measure consistent with nominal GDP, whereas this thesis forecasts CPI inflation and real GDP growth separately. CPI is a consumer expenditure price index, not the GDP deflator. Even with perfect observations, inserting CPI mechanically into the quantity identity would not produce an exact accounting equality for all domestic output. M2 is also only one possible monetary aggregate. The quantity identity therefore provides economic context for monetary growth; it is neither an estimated structural relation nor a restriction imposed on the forecast models.

The Federal Reserve's definition of M2 includes M1 and certain additional retail savings instruments, including small-denomination time deposits and retail money market fund shares (Board of Governors of the Federal Reserve System, 2024). M2 is broader than cash and current-account payments balances, but it does not include every asset available to households and firms. Its measured growth depends partly on financial innovation, portfolio choices, and changes in the relative attractiveness of deposits and other investments. A movement between asset categories can change measured money without reflecting a proportional change in current spending.

The composition of monetary aggregates also evolves. The Federal Reserve's H.6 statistical release documents the operational components and measurement conventions of M1 and M2 (Board of Governors of the Federal Reserve System, 2026). For forecasting, this has two implications. First, a money series can contain institutional and measurement changes as well as economic responses. Second, the relation between money growth and consumer inflation may depend on the demand for liquid assets, the payment system, interest rates, and expectations. The availability of a long monthly M2 series is useful, but a long history does not guarantee a constant predictive coefficient.

### Policy-rate transmission is not one linear channel

Modern monetary policy is frequently described through interest-rate decisions and expectations about the future path of those decisions. When the expected policy path changes, market interest rates, asset prices, exchange rates, and financing conditions may respond. Households and firms can then revise spending and investment. However, the magnitude and timing of these responses depend on debt structure, credit availability, expectations, balance sheets, and the state of demand. There is no reason to expect a change in FEDFUNDS to produce a fixed contemporaneous change in CPI inflation or industrial production.

Bernanke and Gertler (1995) distinguish the familiar interest-rate channel from credit-related mechanisms. In their account, information problems in lending and borrower balance sheets can amplify changes in external financing costs. Tightening may affect firms with weak collateral more severely than firms with ample internal funds. A change in lending conditions can also occur without a proportionate change in the federal funds rate. This provides an economic reason for forecast relations to be asymmetric across financial environments. It does not authorize a claim that an own-history AR, MSAR, or STAR fit estimates the causal credit channel.

The monetary authority also reacts to the same economy it influences. Taylor (1993) illustrates how a rule-like policy response can connect interest-rate decisions to inflation and real activity. If inflation becomes more persistent, the expected policy response may change. If financial conditions deteriorate, an easing response may occur during falling output. Thus contemporaneous correlations between rates and activity can reverse across episodes. An estimated autoregressive coefficient for the policy rate may capture persistence in the policy reaction, without identifying the economic shock that prompted it.

Different macroeconomic traditions emphasize different aspects of these links. Monetary analysis places money demand, nominal expenditure, and the stability of monetary relationships near the center of the problem. Keynesian approaches emphasize aggregate demand, interest-sensitive spending, expectations, and incomplete adjustment. New Keynesian models give a more explicit role to expectations, price-setting frictions, and systematic monetary-policy behavior. These distinctions matter here only when they change the interpretation of an observed time series or explain why a forecasting relation might move. This chapter does not attempt a full history of macroeconomic schools, nor does the thesis estimate and discriminate among their structural models.

There are also reasons for monetary aggregates to have predictive value even when they are not a sufficient policy guide. Changes in deposit holdings may contain information about portfolio preferences, financial conditions, or future spending. But they may add little beyond the recent behaviour of inflation and activity in other periods. Conversely, the rate series may reflect policy actions and expectations rather than an independent monetary disturbance. The appropriate empirical question is whether historical movements in M2 or FEDFUNDS are forecastable under the declared specifications, and whether extra state dependence adds enough information beyond their linear dynamics.

### State dependence, lower bounds, and measurement limits

The effective lower bound on short-term nominal rates is a particularly concrete form of asymmetry. A rate can rise over a wide range but cannot generally move as far below its effective lower bound as an unconstrained Gaussian linear model might suggest. Carriero et al. (2025) show that modelling the constraint explicitly can improve interest-rate prediction in their shadow-rate VAR application. This is an important alternative explanation for changes in observed FEDFUNDS persistence. It also warns against calling every statistically estimated low-rate regime a recession state. A constraint on the support of observed rates is a different mechanism from an unobserved switching state.

Monetary conditions can likewise change abruptly when people move toward more liquid assets. Greater uncertainty may increase desired money holdings, changing measured velocity. A fixed money-growth coefficient estimated in a calmer period may then become misleading. A nonlinear forecasting model could, in principle, accommodate part of this change. A better-specified linear model or an explicitly changing variance could also explain some of the apparent instability. The theory therefore supplies a list of competing mechanisms, not an automatic preference for MSAR or STAR.

The inclusion of M2 has a specific economic and empirical rationale. As a broad monetary aggregate, M2 captures changes in transaction and savings balances that can reflect monetary conditions, portfolio decisions, and money demand. Its long, consistently identified official U.S. series also permits historical forecasting comparisons. These properties make M2 an informative forecasting target without implying that its growth has a stable causal effect on inflation or output. This does not mean M2 is asserted to cause inflation, identify monetary policy, or provide a complete measure of financial liquidity. Its inclusion as a target is compatible with finding that its own historical growth is better forecast by a classical model. The final comparison must allow that outcome.

The theory of money and transmission thus adds three forecasting threats. Monetary demand and velocity may shift; the policy reaction function can change; and the effective lower bound may create a mechanical asymmetry in observed interest rates. These threats are economically distinct but can look similar in a short univariate sample. They reinforce the need to keep forecasting accuracy, structural interpretation, and statistical model identification separate.

## 1.5 Schumpeterian Disruption, Structural Change, and Turning Points

Economic relationships can change not only because a short-lived shock moves prices or output, but also because the economy itself changes. Innovation alters production methods, products, firms, and the allocation of resources. Schumpeter (1934) placed innovation and economic development at the centre of economic change. His argument is relevant to this dissertation because the environment that produced a historical series may not remain constant. It does not, by itself, predict a numerical break date or establish a statistical Markov regime.

An innovation can affect several aggregate variables at different speeds. New production methods may raise productivity and reduce some costs. Employment may shift between sectors before aggregate unemployment settles. Financial technology may change how households hold liquid balances. New forms of production may alter the weight of industrial output within total activity. These changes can shift trends, relative prices, and the timing of adjustment. A forecaster estimating constant parameters over several decades may average across environments in which the same historical relationship has different meanings.

Structural change is broader than innovation. It may arise from changes in regulation, trade relationships, monetary institutions, demographics, banking practices, or the composition of aggregate spending. For example, a lasting change in monetary-policy arrangements could alter inflation persistence and the policy rate's response to shocks. A temporary energy-price surge may instead generate an abrupt observation without changing the process governing inflation over the longer run. A persistent trend change, a one-time level break, and a short-lived outlier can resemble each other in finite samples. They call for different economic interpretations and possibly different statistical treatments.

This distinction is especially important after the COVID-19 shock. Lenza and Primiceri (2022) explain why the extreme observations around March 2020 pose problems for conventional VAR estimation. Large movements can strongly influence fitted dynamics and the uncertainty assigned to later outcomes. Carriero et al. (2024) study explicit treatment of COVID outliers in Bayesian VARs with stochastic volatility. Their approach illustrates a competing interpretation: unusual observations may be handled as exceptional disturbances rather than evidence that the economy repeatedly switches between two stable structural regimes. These alternative specifications are not part of the four-model baseline comparison, but their findings offer competing explanations for apparent nonlinear predictability.

A business-cycle turning point has a more specific meaning than a statistical break. In U.S. chronology, a peak marks the end of an expansion and the start of a recession; a trough marks the end of a recession and the start of an expansion (National Bureau of Economic Research, n.d.). These turning points concern broad economic activity. They are not defined by one unusually high CPI observation, a sign change in industrial production, or a threshold crossing in FEDFUNDS. They also become fully dated only after evidence accumulates. A historical turning-point label can be useful for evaluating realized forecast errors without being valid information for a forecast issued before that date was determined.

The practical difference between recognizing a recession and retrospectively dating one is documented by Chauvet and Piger (2008). Their study compares business-cycle dating methods with attention to real-time performance. This distinction matters because a model that achieves low errors over observations later classified as recessions is not necessarily capable of predicting recession onset in real time. The empirical analysis uses the U.S. recession chronology to classify forecast errors retrospectively. It does not insert future NBER announcements into the forecast information set or claim to operate a real-time recession-warning system.

Economic transitions may nevertheless be difficult forecasting periods. Near an expansion peak, a modest reduction in spending may coexist with a sharp fall in forward-looking confidence. Near a trough, production may recover before unemployment. A forecasting equation estimated mainly during expansions may respond too slowly to these reversals. Yet the opposite possibility is also real: if episodes are rare, a flexible model estimated from a few earlier transitions may overfit their particular features. What appears to be an economically sensible regime-dependent forecast could be a numerical response to limited evidence.

Recurring cycles and irreversible transformation must also be separated. A Markov-switching model assumes a probabilistic pattern of movement among statistical states. A genuine permanent change in technology or institutions need not be well represented by repeated transitions between two familiar states. Conversely, a temporary business-cycle downturn need not represent a lasting structural break. These different processes can create similar-looking segments in a historical chart. This is why estimated state probabilities must be evaluated for their persistence, occupancy, and economic plausibility rather than given a structural label by assumption.

There is a related issue with the direction of time. A model estimated on all available observations can describe past regimes using information from both before and after a date. A forecast cannot use that future evidence at its origin. Smoothed historical state classifications and filtered or forecast-time state probabilities are therefore different informational objects. The distinction will become formal in Chapter 2's treatment of Markov switching. Chapter 1's economic claim is simply that policy and business-cycle transitions can change the predictive environment, while reliable identification of those transitions may be difficult before they occur.

The analysis of disruption and turning points yields two opposing expectations. A forecasting model that adapts to a changed state could improve prediction near recessions and recoveries. But a model may also become fragile precisely where observations are sparse and shocks are large. The thesis must examine both possibilities. Statistical state dependence is useful only if it represents reproducible predictive information, not merely the appearance of an economic story in a chart.

## 1.6 From Economic Instability to Statistical State Dependence

The term *nonlinear* is sometimes used as a general label for a difficult economic series. That usage is too vague for this dissertation. High volatility, persistence, a deterministic trend, a structural break, a nonlinear conditional mean, and an unobserved switching process are different statistical properties. A model designed for one property need not solve the others. The distinction is necessary before the thesis can ask whether a nonlinear forecast improves on a classical benchmark.

### A stable linear reference and the meaning of nonlinearity

Let $y_t$ be a transformed macroeconomic forecast target and let $\mathcal{F}_{t-1}$ denote the information permitted before observing $y_t$. A stable autoregressive model of order $p$ takes the form

**Equation (1.8)**

```math
y_t=c+\sum_{j=1}^{p}\phi_jy_{t-j}+\varepsilon_t,
\qquad E(\varepsilon_t\mid\mathcal{F}_{t-1})=0.
```

Here $c$ and the coefficients $\phi_j$ are constant across the estimation period; the conditional mean is additive and linear in the included lagged observations. The equation does not require every observed path to be a straight line. It can generate persistent cycles, reversals, and surprisingly large observations when shocks are large. A model may also be linear in its conditional mean while having changing conditional variance. That distinction is important because volatility changes alone do not demonstrate nonlinear predictability of the mean.

For this thesis, *nonlinear conditional-mean dynamics* mean that the forecast relationship cannot be represented, within the chosen model class, by one constant set of additive coefficients on the included lags. The effect of a lag may depend on a threshold, a smooth transition variable, or a latent state. This definition is narrower than any departure from a straight-line plot. It is the relevant definition when comparing the specified linear AR and ARMA forecasts with MSAR and STAR forecasts.

Consider an inflation series that is usually persistent but sometimes reverses quickly after a large movement. A constant-coefficient AR may average these responses. A threshold model may assign different slopes above and below a stated threshold, while a smooth transition model may allow the slope to change gradually around it. A latent regime model may allow different conditional means depending on an unobserved state. Each offers a way to describe state dependence, but the observed behavior does not prove which representation is appropriate.

### Breaks, evolving coefficients, thresholds, and hidden regimes

A *structural break* is a change in the parameters or distribution of a process at one or more points in time. A simplified example has coefficients $\phi_j^{(A)}$ before a date and $\phi_j^{(B)}$ afterward. The change may be permanent or sufficiently persistent that treating the full sample as homogeneous is misleading. The date may be known from an institutional reform or must be estimated from the data. A break model does not automatically imply repeated alternation between states.

*Time-varying parameters* describe coefficients that evolve with calendar time or new information, potentially without discrete breaks. A change may be gradual, as when inflation persistence declines over several years. A smooth trend in coefficients is not necessarily the same as a smooth transition autoregression, where coefficients are functions of an observed transition variable. The distinction matters because one approach assumes change over time, while the other conditions change on a specified observable state of the process.

A *threshold* creates a change in behavior at a boundary in an observed variable. A sharp threshold model may use one coefficient set when lagged inflation is below a value and another when it is above. A *smooth transition* allows the relative weight of those coefficient sets to vary continuously as the transition variable crosses a region. Teräsvirta (1994) provides a formal framework for specifying, estimating, and evaluating such models. Smoothness does not imply ease of estimation: if there are few observations near a threshold, the threshold and transition speed may be weakly identified.

A *latent-regime* model differs because the state is not directly observed. Hamilton (1989) specifies a model in which an unobserved state follows a Markov transition process. Conditional means or other parameters can depend on that state. The probability of being in one state can evolve as observations arrive, even if no visible threshold variable is specified. The empirical state is a statistical device that may correspond to an economically meaningful episode, but the correspondence has to be demonstrated rather than asserted. A high-volatility state should not automatically be named a recession, and a high-inflation state is not necessarily a new monetary-policy regime.

The forecast information set creates an additional restriction. Retrospective state probabilities can be computed after later data are observed, but they are not the same as probabilities available at the forecast origin. Genuine forecasting must use filtered or predictive state information, not future-informed smoothed classifications. This constraint applies even when a retrospective figure makes regime changes look visually obvious.

### Persistence and nonstationarity are separate properties

*Persistence* means that past observations contain information about future ones over an extended period. A persistent process need not be nonlinear. An AR process with a root close to one may be strongly persistent even if its coefficient never changes. *Nonstationarity* concerns whether properties such as the mean, variance, or dependence structure remain stable under the definition adopted. A unit-root process and a stationary process around a changing deterministic trend can both display a long apparent movement without having the same forecasting properties.

Deterministic trend and stochastic trend also differ. A quadratic deterministic trend can generate accelerating levels while deviations from that trend remain stationary. An integrated process accumulates stochastic innovations, so its uncertainty grows for a different reason. Subtracting a fitted trend and taking first or second differences therefore do not have interchangeable meanings. Choosing a transformation because it gives attractive forecast results would risk hiding the underlying distinction. Chapter 2 specifies stationarity diagnostics and target transformations before comparing forecasting performance, thereby avoiding transformations chosen solely to favor a particular model.

An economic break can also contaminate a unit-root assessment. A stationary process with a large level shift may look highly persistent if the shift is ignored. Conversely, a differenced series may remove economically meaningful low-frequency information. This motivates the complementary stationarity and break-sensitive diagnostics developed in Chapter 2. The role of this chapter is to explain why the alternatives matter; Chapter 2 gives the formal null hypotheses and the exact decision rules.

### Asymmetry, volatility, and exceptional observations

*Asymmetry* means that the response to a positive change may differ from the response to a negative change of comparable magnitude. For instance, unemployment might rise faster in a contraction than it declines during recovery, or rate adjustments near a lower bound may differ from upward adjustments. Asymmetry can appear in the conditional mean, the conditional variance, the distribution of shocks, or a combination of them. It is not enough to observe a large negative shock and infer a nonlinear mean process.

*Conditional heteroskedasticity* means that the conditional variance of shocks changes with past information. Even with a constant conditional-mean equation, periods of large and small innovations may cluster. A model can account for changing variance without improving the point forecast of the conditional mean. Here, variance diagnostics and conditional-variance models serve a different purpose from the AR, MSAR, and STAR conditional-mean forecast comparison. Their presence must not be interpreted as evidence that nonlinear mean forecasts are better.

An *outlier* is an observation unusually distant from the model's ordinary predictive distribution. It may reflect a genuine shock, a measurement problem, a pandemic, or a model that poorly describes the data. A few extreme values can alter information criteria, conditional parameter estimates, and selected regimes. Lenza and Primiceri (2022) and Carriero et al. (2024) show why the COVID period requires special attention in macroeconomic estimation. But deleting difficult observations after reviewing a model comparison would itself change the question being tested. The empirical sample therefore retains the relevant extreme observations, while targeted robustness analyses assess their influence without selecting episodes according to the preferred model's performance.

### Why a statistical detection is not a forecast result

The presence of nonlinearity in a diagnostic test is not sufficient evidence that a nonlinear model forecasts better. A test may identify departures from a linear null that are too small or unstable to improve prediction. Conversely, a diagnostic may have limited power in short or noisy samples, so a non-rejection does not prove that the true process is linear. Formal nonlinearity tests developed by Tsay (1986), Luukkonen et al. (1988), and Teräsvirta (1994) offer ways to screen the relevant departures. Their null hypotheses and use in the selected models are defined in Chapter 2.

A nonlinear model has to meet several additional demands. Its parameters and transitions must be estimable from the available sample. Its implied states must not depend entirely on one or two unusual observations. The optimizer must not produce extreme or degenerate solutions that invalidate interpretation. The model must then provide valid forecasts at origins where the simpler benchmark is evaluated. Finally, an observed reduction in forecasting loss must be distinguished from random sampling variation. These steps are separate because an attractive nonlinear fit can fail before a claim of predictive value becomes defensible.

The statistical taxonomy therefore imposes discipline on the economic argument. Instability may mean nonstationarity, a one-time break, a change in volatility, occasional extreme shocks, changing coefficients, or recurring conditional-mean states. MSAR and STAR address some of these possibilities, not all of them. Identifying the form of instability is necessary for meaningful interpretation, and a forecast comparison is still required before concluding that modelling it adds predictive value.


## 1.7 What the Theoretical and Empirical Literature Already Knows, and What Remains Unresolved

The economic mechanisms described above provide several reasons for unstable macroeconomic forecasts. They do not show that nonlinear methods are superior. That question has a substantial prior literature. Research has established the usefulness of simple autoregressions, the existence of state-dependent dynamics, the importance of multivariate information, and the sensitivity of comparisons to the evaluation design. The unresolved issue for this thesis is narrower: whether the specific additional flexibility of MSAR and STAR provides a credible forecasting gain over well-defined AR and ARMA benchmarks for the six selected U.S. targets, once adequacy, numerical failures, horizons, changing states, and competing explanations are taken into account.

### Classical models as serious competitors

The AR and ARMA tradition provides an important scientific baseline because past observations often contain substantial predictive information. AR models use lagged targets to describe the conditional mean. ARMA models allow dependence in past innovations as well as past observations (Box et al., 2015). Their value is not that the economy is assumed to be structurally linear in every respect. Their value is that a parsimonious model sets a clear standard: a more complicated method should forecast better than a model that can already represent basic persistence and short-run adjustment.

The literature has also shown why a strong univariate benchmark can be difficult to beat. Stock and Watson (2007) examine changes in U.S. inflation forecasting and emphasize evolving inflation persistence and volatility. Their analysis suggests that a time-varying univariate representation can be a demanding competitor for multivariate alternatives. The lesson is not that a fixed AR is always sufficient. It is that the forecasting problem must be defined carefully: a regression with many explanatory variables or nonlinear terms should not be credited with improvement unless it has been compared with a credible target-specific baseline.

A further benefit of classical benchmarks is interpretability of failures. If a higher-order AR outperforms a lower-order AR, an apparent nonlinear gain may have reflected omitted linear lag dependence. If ARMA improves the forecast, innovation dynamics may matter more than regime switching. If all models suffer after an exceptional shock, the difficulty may be missing information rather than the form of the conditional mean. These are not reasons to exclude nonlinear alternatives. They are reasons to evaluate them against benchmarks chosen by declared rules rather than against the weakest available linear specification.

### Discrete and smooth nonlinear dynamics

Hamilton (1989) establishes the importance of latent regime switching for the analysis of U.S. output dynamics and the business cycle. The model separates an unobserved state process from observed economic data and permits their statistical behavior to differ across states. It provides a coherent representation of recurrent change. It does not imply that any two-state fit to any macroeconomic target must produce a useful forecasting improvement, nor that its states automatically coincide with NBER recessions.

Smooth transition models address a different kind of variation. Teräsvirta (1994) presents a procedure for specification and evaluation; Teräsvirta et al. (2005) compare linear models, smooth-transition autoregressions, and neural networks in a broad macroeconomic forecasting exercise. Their results provide evidence that carefully specified nonlinear models can be competitive. They also make model specification and forecast evaluation central to the conclusion. A smooth transition adds parameters whose value depends on the observations available near the transition region. A plausible transition shape in-sample can still have little predictive value in a new estimation window.

The distinction between discrete and smooth change is economically relevant. A sharp institutional shift might be represented by an abrupt break or a latent state change, while gradual adjustment in price-setting or policy expectations might be represented more naturally by changing or smoothly transitioning coefficients. Neither relationship has to be recurrent. Conversely, occasional extreme shocks may falsely suggest recurrent regimes to a flexible model. Economic theory therefore cannot select MSAR rather than STAR from the names of the models alone. The comparison requires diagnostics and predictions.

### Modern nonlinear work broadens, rather than settles, the question

More flexible statistical methods show that nonlinear relations can matter without proving the superiority of any one parametric model family. Goulet Coulombe et al. (2022) examine which ingredients of machine learning contribute to macroeconomic forecasting performance and identify nonlinear flexibility as important in their applications, particularly around uncertainty and stress. Goulet Coulombe (2024) develops a random-forest approach to changing macroeconomic relationships. These findings are relevant because a fixed conditional-mean representation may miss changing interactions. Yet the algorithms, predictors, tuning rules, and information sets are not the same as those in the present AR/MSAR/STAR comparison.

Inflation forecasting offers a useful contrast. Clark et al. (2024) develop Bayesian nonparametric models that accommodate nonlinear relationships and asymmetric error behavior when forecasting U.S. inflation. Their design responds directly to the possibility that the inflation–unemployment relation changes over time. Naghi et al. (2024), however, show that the ranking of machine-learning approaches is sensitive to the model and evaluation period, with rival methods competitive during the pandemic and high-inflation episode. Taken together, these studies justify investigating flexibility but rule out treating it as a universal remedy.

Other studies demonstrate that the object being forecast matters. Prüser and Huber (2024) model U.S. GDP growth quantiles and find gains from nonlinear specifications, especially in the tails of the predictive distribution. A model may improve the probability assigned to extreme adverse growth while leaving the point forecast of average growth largely unchanged. The present thesis evaluates declared point-forecast losses. It cannot borrow a gain in quantile or tail-risk forecasting as if it were a gain in mean-squared-error forecasting.

Recent multivariate work also offers credible alternatives to own-history nonlinearity. Hauzenberger et al. (2025) propose a Gaussian-process VAR that allows flexible nonlinear dependencies and changing volatility in a macroeconomic system. Clark et al. (2026) augment a Bayesian VAR with nonlinear common factors and report density-forecast benefits in their U.S. application. These studies show that nonlinear gains may come from relationships across variables or from richer descriptions of uncertainty rather than from switching dynamics in one target alone. They do not determine whether a two-regime MSAR forecast for an individual target improves on an AR forecast under the historical sample and horizons investigated here.

The lower-bound literature supplies an especially clear competing model for interest rates. Carriero et al. (2025) build an explicit rate constraint into VAR forecasting. If the main challenge for the short-term policy rate is a bounded observable, a generic latent-regime model may be less suitable than a model designed for the constraint. Similarly, Lenza and Primiceri (2022) and Carriero et al. (2024) show why the extreme observations of the pandemic can require special treatment. A regime model that isolates the pandemic does not necessarily uncover a stable, recurring mechanism. These papers make model adequacy and unusual observations part of the scientific question.

### Information sets, real-time boundaries, and changing states

A second research stream considers the information available to the forecaster. Sims (1980) established the role of VARs in representing interactions among macroeconomic variables without imposing the full restrictions of a structural system. A VAR can therefore be a useful alternative to a single-equation model even when neither method identifies causal mechanisms. Its forecasts may benefit from information in other targets. This possibility is one threat to the claim that nonlinear dependence in a target's own history is the main missing feature.

Mixed-frequency forecasting addresses a different information problem. Giannone et al. (2008) develop a nowcasting framework that uses the evolving flow of macroeconomic releases. Galvão and Owyang (2022) show that higher-frequency financial and economic information can improve probabilities for some lower-frequency macroeconomic events. These applications matter because observations arrive at different dates, not simply because models may be nonlinear. The present thesis retains native monthly and quarterly target frequencies and does not reproduce the live arrival of each data release. It must therefore be described as a historical pseudo-out-of-sample comparison, not as a true real-time nowcasting system.

Performance can also vary across economic states. Giacomini and White (2006) establish a framework for assessing conditional predictive ability, while Odendahl et al. (2023) investigate forecast performance when the economic state matters. Their contribution is to distinguish overall performance from conditional patterns. A model could have similar average error to a benchmark yet perform better in one state and worse in another. However, recession and expansion comparisons must use valid state information and correct statistical hypotheses. A descriptive difference between recession-period errors and expansion-period errors does not alone establish a statistically significant state effect.

### The burden of forecast inference

The final stream concerns what constitutes evidence of improvement. Diebold and Mariano (1995) formalize comparisons of predictive accuracy. West (1996) studies inference when forecasts arise from estimated models. Hansen et al. (2011) develop the Model Confidence Set as a multiple-model procedure, which does not require selecting one model as a unique winner. Rossi and Inoue (2012) address sensitivity of out-of-sample tests to the estimation-window choice. These contributions show that a small gap between observed forecast errors may have different inferential meanings depending on sample construction, parameter estimation, the loss function, and the period of evaluation.

Instability creates a particular concern for forecast-comparison tests. Harvey et al. (2025) study tests of equal average forecast accuracy when the mean loss differential may change over time. Their procedure is especially relevant when the research question itself concerns instability. This thesis therefore distinguishes descriptive rankings from formal inference under its predeclared primary test. The formal test design and its secondary checks are specified in Chapter 2, where null hypotheses, paired samples, and admissible forecasts can be defined without importing results into the theoretical discussion.

The literature establishes three broad lessons. Nonlinear dynamics can exist and sometimes improve macroeconomic forecasts. Simple models remain serious competitors, and richer models can fail when their parameters or information sets are poorly suited to the next period. Finally, a forecast ranking is not meaningful without knowing the target, horizon, evaluation sample, diagnostic status, and statistical comparison. What the literature does not decide in advance is the outcome of a common, failure-aware comparison between classical and interpretable nonlinear forecasting models for the six U.S. series examined here. That bounded question, rather than the invention of a model or the discovery that economic relations can change, is the thesis's contribution.

## 1.8 Testable Implications, Competing Explanations, and Evidence That Would Contradict the Argument

The theory and literature permit more than one empirical outcome. State-dependent nonlinear models might capture useful information when economic relationships change. They might also fit history better without improving future predictions. The purpose of a disciplined test is not to confirm the first possibility, but to distinguish it from the second and from alternative explanations. The research question therefore requires clear conditions under which the case for added complexity would be weakened.

The first implication concerns diagnosable dynamics. If the selected targets contain persistent or state-dependent patterns not adequately represented by a constant linear conditional mean, formal diagnostics may reveal evidence of nonlinearity, breaks, or unusual persistence. However, those findings are not interchangeable. A unit root is not a transition regime; an abrupt break is not a smooth threshold; and volatility clustering is not necessarily nonlinear mean predictability. Failure to reject a linear specification also does not prove the absence of economically relevant nonlinear behavior. The evidence must be judged with the limitations of the tests in mind.

The second implication concerns model adequacy and identification. A nonlinear model should represent its historical data without relying on implausible parameters, empty states, transition probabilities at numerical boundaries, or a handful of exceptional dates. A smoother transition is not credible merely because an optimizer reports a transition function. If parameters are weakly identified or the estimation is sensitive to starting values, interpretation becomes limited even when an information criterion favors the fit. These weaknesses would directly challenge the argument that additional complexity represents a stable predictive mechanism.

The third implication concerns genuine predictive value. If nonlinear structure supplies useful information beyond a well-specified linear model, that information should improve forecasts formed before outcomes are known. Forecast accuracy must be assessed on comparable dates and with clearly defined losses. A lower reported RMSE is a descriptive fact, not by itself a statistically established gain. If MSAR or STAR does not outperform AR under the primary test of predictive accuracy, the evidence cannot establish nonlinear superiority at that horizon. Non-rejection would not prove equal predictive ability; it would mark a lack of statistically established superiority in the stated comparison.

The fourth implication concerns economic states. The motivation for nonlinear forecasting is strongest where changes in dynamics might matter, especially around contractions, recoveries, and turning points. A genuine conditional advantage might therefore appear in some of those observations. But the opposite result would be informative. If an average gain comes entirely from ordinary expansions or disappears after adjusting for common evaluation dates, the specific turning-point rationale would be weakened. Recession labels assigned after the event cannot be used to claim that a forecaster correctly recognized a recession before it began.

The fifth implication is that classical misspecification can imitate nonlinearity. Too few AR lags may leave serial dependence in the residuals. An ARMA specification may describe innovation dynamics omitted by an AR. A changing level or an unmodelled break may create a spurious appearance of regimes. A model that looks nonlinear in levels may behave differently after an appropriate predeclared transformation. These possibilities make lag, transformation, structural-break, and residual checks necessary competitors rather than optional decorations around a nonlinear result.

A sixth implication concerns cross-variable information. The Fisher, Phillips–Phelps, Okun, and monetary mechanisms link the selected variables economically, but the primary empirical models mainly forecast from each target's own past. If a limited VAR improves relevant forecasts or changes their ranking, some apparent failure of the univariate model may come from omitted predictors rather than insufficient nonlinear flexibility. The VAR comparison is a bounded predictive check; it does not identify the causal transmission channels in the economic theories.

A seventh implication concerns horizons and estimation windows. The same model may be useful one month ahead and unhelpful one year ahead. A short window adapts more quickly to change but uses fewer observations. A longer window estimates parameters from more data but may include older dynamics that are less relevant after a break. A nonlinear advantage confined to one horizon or one window is weaker evidence of general utility than a result that survives the declared comparisons. Equally, the absence of gains at one horizon cannot settle every longer-horizon question.

The eighth implication concerns numerical feasibility. Added parameters and latent states make nonlinear estimation more demanding. A fit may fail to converge, produce near-boundary estimates, or yield an explosive forecast. If failed forecasts are silently replaced or omitted without documenting the matched sample, the resulting horse race will not answer the declared question. A model's inability to supply reliable forecasts at some origins is relevant evidence about its practical usefulness. Numerical failure must be separated from statistical non-rejection, because an unusable test cannot demonstrate either superiority or equality.

These conditions also prevent retrospective selection of favorable evidence. It would be inappropriate to change the transformation, regime count, sample, or loss measure solely because a particular nonlinear model then wins. The forecasting comparison therefore distinguishes its baseline specifications from the additional robustness analyses, all evaluated under explicit rules. Additional checks can challenge the interpretation, but they cannot silently replace the baseline. A model that fits better yet remains statistically uncompetitive or numerically unstable does not satisfy the standard of credible forecasting value.

The economic interpretation has a final boundary. Even robust forecast improvement would not establish that a model identifies the cause of inflation or unemployment, that its statistical states correspond to structural policy regimes, or that using it would improve social welfare. Those claims require different evidence. The present experiment can establish a bounded predictive result for the targets, periods, and procedures actually studied. This is both the strength and the limitation of its research design.

## 1.9 Chapter 1 Concluding Synthesis: From Macroeconomic Mechanisms to a Testable Forecasting Problem

This chapter asked which economic mechanisms make inflation, output, unemployment, interest rates, and money important for policy, and why their relationships can become difficult to forecast. The answer is that economic decisions operate through expectations, adjustments, and feedback that need not remain constant. Fisherian reasoning shows why nominal-rate forecasts depend on expected inflation, real returns, and financial conditions. Phillips–Phelps and Okun mechanisms link prices, labour markets, and real activity, while also showing why expectations, productive capacity, and adjustment lags can change observed relationships. Monetary transmission adds changes in money demand, credit conditions, policy reactions, and constraints on short-term rates.

Economic instability is not one statistical phenomenon. Innovation and institutional change may alter the longer-run environment; a recession or recovery may change the timing of adjustment; an isolated shock may generate an extreme observation without creating a recurring regime. A structural break, a stochastic trend, changing variance, a threshold, and an unobserved Markov state must therefore be distinguished. Each can affect forecasting, but no single nonlinear model captures all of them. Economic theory supplies reasons to examine state dependence, not a proof that it exists in every selected series or can be estimated reliably.

Prior research offers credible approaches on both sides of the comparison. AR and ARMA provide transparent benchmarks for persistence and innovation dynamics. Markov-switching and smooth-transition models offer structured ways to represent discrete or gradual changes. Modern nonlinear, multivariate, and mixed-frequency studies demonstrate the importance of model flexibility and information sets, but their findings do not transfer automatically to the present point-forecast experiment. Forecast-evaluation research further shows that error rankings, significance, changing estimation windows, and conditional performance answer different questions.

The unresolved issue is consequently precise. Given six policy-relevant U.S. macroeconomic targets, does a state-dependent conditional mean produce more credible forecasts than a properly defined classical benchmark under the same admissible information and evaluation rules? If a gain appears, is it robust to reasonable competing explanations and economically interpretable without overstating what the model identifies? If the gain does not appear, that is a valid scientific answer.

Chapter 2 converts this economic question into an empirical contract. It defines the frozen data, transformations, stationarity and nonlinearity diagnostics, linear benchmarks, nonlinear specifications, forecast origins, evaluation criteria, and failure rules. It also fixes how recessions and turning points are used, what the robustness checks can test, and what the design cannot establish. That specification is necessary before any later result can be described as evidence that nonlinear complexity has earned its place.

---

## References

An, Z., Jalles, J. T., & Loungani, P. (2018). How well do economists forecast recessions? *International Finance, 21*(2), 100–121. https://doi.org/10.1111/infi.12130

Bernanke, B. S. (2024). *Forecasting for monetary policymaking and communication at the Bank of England: A review*. Bank of England. https://www.bankofengland.co.uk/independent-evaluation-office/forecasting-for-monetary-policy-making-and-communication-at-the-bank-of-england-a-review/forecasting-for-monetary-policy-making-and-communication-at-the-bank-of-england-a-review

Bernanke, B. S., & Gertler, M. (1995). Inside the black box: The credit channel of monetary policy transmission. *Journal of Economic Perspectives, 9*(4), 27–48. https://doi.org/10.1257/jep.9.4.27

Blanchard, O. (2016). The Phillips curve: Back to the '60s? *American Economic Review, 106*(5), 31–34. https://doi.org/10.1257/aer.p20161003

Board of Governors of the Federal Reserve System. (2024, July 19). *What is the money supply? Is it important?* https://www.federalreserve.gov/faqs/money_12845.htm

Board of Governors of the Federal Reserve System. (2026, September 22). *Money stock measures: H.6 release*. https://www.federalreserve.gov/releases/h6/20260922/

Box, G. E. P., Jenkins, G. M., Reinsel, G. C., & Ljung, G. M. (2015). *Time series analysis: Forecasting and control* (5th ed.). Wiley.

Carriero, A., Clark, T. E., Marcellino, M., & Mertens, E. (2024). Addressing COVID-19 outliers in BVARs with stochastic volatility. *The Review of Economics and Statistics, 106*(5), 1403–1417. https://doi.org/10.1162/rest_a_01213

Carriero, A., Clark, T. E., Marcellino, M., & Mertens, E. (2025). Forecasting with shadow rate VARs. *Quantitative Economics, 16*(3), 795–822. https://doi.org/10.3982/QE2547

Chauvet, M., & Piger, J. (2008). A comparison of the real-time performance of business cycle dating methods. *Journal of Business & Economic Statistics, 26*(1), 42–49. https://doi.org/10.1198/073500107000000296

Clark, T. E., Huber, F., & Koop, G. (2026). A flexible approach to augmenting a Bayesian VAR with nonlinear factors. *Journal of Business & Economic Statistics*. Advance online publication. https://doi.org/10.1080/07350015.2026.2703238

Clark, T. E., Huber, F., Koop, G., & Marcellino, M. (2024). Forecasting U.S. inflation using Bayesian nonparametric models. *Annals of Applied Statistics, 18*(2), 1421–1444. https://doi.org/10.1214/23-AOAS1841

Diebold, F. X., & Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business & Economic Statistics, 13*(3), 253–263. https://doi.org/10.1080/07350015.1995.10524599

Fisher, I. (1930). *The theory of interest: As determined by impatience to spend income and opportunity to invest it*. Macmillan. https://fraser.stlouisfed.org/title/theory-interest-6255

Friedman, M. (1968). The role of monetary policy. *American Economic Review, 58*(1), 1–17. https://fraser.stlouisfed.org/title/american-economic-review-1161/role-monetary-policy-2352

Galvão, A. B., & Owyang, M. T. (2022). Forecasting low-frequency macroeconomic events with high-frequency data. *Journal of Applied Econometrics, 37*(7), 1314–1333. https://doi.org/10.1002/jae.2931

Giacomini, R., & White, H. (2006). Tests of conditional predictive ability. *Econometrica, 74*(6), 1545–1578. https://doi.org/10.1111/j.1468-0262.2006.00718.x

Giannone, D., Reichlin, L., & Small, D. (2008). Nowcasting: The real-time informational content of macroeconomic data. *Journal of Monetary Economics, 55*(4), 665–676. https://doi.org/10.1016/j.jmoneco.2008.05.010

Goulet Coulombe, P. (2024). The macroeconomy as a random forest. *Journal of Applied Econometrics, 39*(3), 401–421. https://doi.org/10.1002/jae.3030

Goulet Coulombe, P., Leroux, M., Stevanovic, D., & Surprenant, S. (2022). How is machine learning useful for macroeconomic forecasting? *Journal of Applied Econometrics, 37*(5), 920–964. https://doi.org/10.1002/jae.2910

Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica, 57*(2), 357–384. https://doi.org/10.2307/1912559

Hansen, P. R., Lunde, A., & Nason, J. M. (2011). The model confidence set. *Econometrica, 79*(2), 453–497. https://doi.org/10.3982/ECTA5771

Harvey, D. I., Leybourne, S. J., & Zu, Y. (2025). Testing for equal average forecast accuracy in possibly unstable environments. *Journal of Business & Economic Statistics, 43*(3), 643–656. https://doi.org/10.1080/07350015.2024.2418835

Hauzenberger, N., Huber, F., Marcellino, M., & Petz, N. (2025). Gaussian process vector autoregressions and macroeconomic uncertainty. *Journal of Business & Economic Statistics, 43*(1), 27–43. https://doi.org/10.1080/07350015.2024.2322089

Lenza, M., & Primiceri, G. E. (2022). How to estimate a vector autoregression after March 2020. *Journal of Applied Econometrics, 37*(4), 688–699. https://doi.org/10.1002/jae.2895

Lucas, R. E., Jr. (1976). Econometric policy evaluation: A critique. *Carnegie-Rochester Conference Series on Public Policy, 1*, 19–46. https://doi.org/10.1016/S0167-2231(76)80003-6

Luukkonen, R., Saikkonen, P., & Teräsvirta, T. (1988). Testing linearity against smooth transition autoregressive models. *Biometrika, 75*(3), 491–499. https://doi.org/10.1093/biomet/75.3.491

Naghi, A. A., O'Neill, E., & Danielova Zaharieva, M. (2024). The benefits of forecasting inflation with machine learning: New evidence. *Journal of Applied Econometrics, 39*(7), 1321–1331. https://doi.org/10.1002/jae.3088

National Bureau of Economic Research. (n.d.). *Business cycle dating*. https://www.nber.org/research/business-cycle-dating

Odendahl, F., Rossi, B., & Sekhposyan, T. (2023). Evaluating forecast performance with state dependence. *Journal of Econometrics, 237*(2), Article 105220. https://doi.org/10.1016/j.jeconom.2021.07.015

Office for Budget Responsibility. (2026). *Forecast evaluation report: June 2026*. https://obr.uk/fer/forecast-evaluation-report-june-2026/

Okun, A. M. (1962). Potential GNP: Its measurement and significance. *Proceedings of the Business and Economic Statistics Section of the American Statistical Association*, 98–104.

Orphanides, A. (2001). Monetary policy rules based on real-time data. *American Economic Review, 91*(4), 964–985. https://doi.org/10.1257/aer.91.4.964

Phelps, E. S. (1967). Phillips curves, expectations of inflation and optimal unemployment over time. *Economica, 34*(135), 254–281. https://doi.org/10.2307/2552025

Phillips, A. W. (1958). The relation between unemployment and the rate of change of money wage rates in the United Kingdom, 1861–1957. *Economica, 25*(100), 283–299. https://doi.org/10.1111/j.1468-0335.1958.tb00003.x

Prüser, J., & Huber, F. (2024). Nonlinearities in macroeconomic tail risk through the lens of big data quantile regressions. *Journal of Applied Econometrics, 39*(2), 269–291. https://doi.org/10.1002/jae.3018

Rossi, B., & Inoue, A. (2012). Out-of-sample forecast tests robust to the choice of window size. *Journal of Business & Economic Statistics, 30*(3), 432–453. https://doi.org/10.1080/07350015.2012.693850

Schumpeter, J. A. (1934). *The theory of economic development: An inquiry into profits, capital, credit, interest, and the business cycle* (R. Opie, Trans.). Harvard University Press. (Original work published 1911)

Sims, C. A. (1980). Macroeconomics and reality. *Econometrica, 48*(1), 1–48. https://doi.org/10.2307/1912017

Stock, J. H., & Watson, M. W. (2007). Why has U.S. inflation become harder to forecast? *Journal of Money, Credit and Banking, 39*(s1), 3–33. https://doi.org/10.1111/j.1538-4616.2007.00014.x

Taylor, J. B. (1993). Discretion versus policy rules in practice. *Carnegie-Rochester Conference Series on Public Policy, 39*, 195–214. https://doi.org/10.1016/0167-2231(93)90009-L

Teräsvirta, T. (1994). Specification, estimation, and evaluation of smooth transition autoregressive models. *Journal of the American Statistical Association, 89*(425), 208–218. https://doi.org/10.1080/01621459.1994.10476462

Teräsvirta, T., van Dijk, D., & Medeiros, M. C. (2005). Linear models, smooth transition autoregressions, and neural networks for forecasting macroeconomic time series: A re-examination. *International Journal of Forecasting, 21*(4), 755–774. https://doi.org/10.1016/j.ijforecast.2005.04.010

Tsay, R. S. (1986). Nonlinearity tests for time series. *Biometrika, 73*(2), 461–466. https://doi.org/10.1093/biomet/73.2.461

West, K. D. (1996). Asymptotic inference about predictive ability. *Econometrica, 64*(5), 1067–1084. https://doi.org/10.2307/2171956
