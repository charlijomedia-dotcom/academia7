# Part 6 literature-to-code compliance matrix

**Audit date:** 15 October 2026
**Papers read in full** (not abstracts or secondary summaries), from the PDFs supplied:

- Hamilton, J. D. (1989). "A New Approach to the Economic Analysis of Nonstationary Time
  Series and the Business Cycle." *Econometrica* 57(2), 357–384.
- Luukkonen, R., Saikkonen, P. & Teräsvirta, T. (1988). "Testing Linearity in Univariate
  Time Series Models." *Scandinavian Journal of Statistics* 15(3), 161–175.
  (The Scandinavian Journal paper, not the 1988 *Biometrika* paper by Saikkonen and
  Luukkonen on testing against STAR; the latter is cited inside Teräsvirta 1994 §3.2 and
  is not the reference used here.)
- Teräsvirta, T. (1994). "Specification, Estimation, and Evaluation of Smooth Transition
  Autoregressive Models." *JASA* 89(425), 208–218.

Classification: **Compliant** (no change needed) · **Corrected** (defect found and fixed)
· **Documented variation** (deliberate, justified departure) · **Open** (needs the user's
decision).

---

## 1. Teräsvirta (1994) — linearity tests and specification

| # | Paper | Code | Assessment | Evidence |
|---|---|---|---|---|
| T-1 | §2, eq. (2.1) LSTAR model; the `−1/2` term is "useful just in deriving linearity tests; the LSTAR models I estimate do not contain this term" | `models/star.py:transition` | **Compliant** — the estimated transition has no `−1/2` | `test_literature_compliance.py::TestStarEstimation` |
| T-2 | §2, eq. (2.2) ESTAR model | `transition(..., "ESTAR")` | **Compliant** | same |
| T-3 | **§3.1, eq. (3.10)/(3.12)** auxiliary regression: cross-products multiply `w_t = (y_{t−1},…,y_{t−p})'`, each coefficient vector a *p*-vector | `diagnostics/nonlinearity.py:_lst_auxiliary` | **Corrected** — multiplied the whole design *including the intercept*, adding standalone `y^k_{t−d}` terms that duplicate existing columns when `d ≤ p` | rank = full column rank for every (p,d) tested |
| T-4 | **§3.1, eq. (3.11)** null `β₂ⱼ=β₃ⱼ=β₄ⱼ=0`, LM ~ χ²(3p) | `_f_test` | **Corrected** — restrictions were counted from raw column counts (9 instead of 6 at p=2,d=1); now `rank(unrestricted) − rank(restricted)`, which is exactly 3p | parametrised over 8 (p,d) pairs; F verified against statsmodels `f_test` to 1e-8 |
| T-5 | §4.2 delay chosen by the minimum p-value of the (3.11) test | `select_delay_and_type` | **Compliant**, and now meaningful: the reference distribution is identical across the delay grid, which it was not before | `test_the_delay_minimising_the_linearity_p_value_is_selected` |
| T-6 | §4.3, eq. (4.3)–(4.5) nested `H₀₁: γ₄=0`, `H₀₂: γ₃=0\|γ₄=0`, `H₀₃: γ₂=0\|γ₃=γ₄=0` | `select_delay_and_type` | **Corrected** — each block now contributes exactly *p* restrictions, so each F is referred to F(p, ·) | `test_each_nested_test_imposes_p_restrictions`, `test_the_sequence_is_properly_nested` |
| T-7 | §4.3 decision rule: "if the p value of F₃ (the test of H₀₂) is the smallest of the three, select an ESTAR model; if not, choose a LSTAR model" | same | **Compliant** | `test_estar_is_chosen_when_the_middle_test_is_strongest` |
| T-8 | §5, eq. (5.1) conditional least squares | `models/star.py:_sse`, `fit_star` | **Compliant** — the linear coefficients are concentrated out for fixed (γ,c), which is exact, not an approximation | `test_concentrating_the_linear_coefficients_reproduces_the_joint_minimum` |
| T-9 | §5 "standardize the exponent of F by dividing it by σ̂²(y)" (ESTAR); "for LSTAR models it is natural to divide the exponent by σ̂(y)" | `transition` with `scale` | **Compliant** — LSTAR divides by the standard deviation, ESTAR by the variance, verified against the closed forms | `test_the_lstar_exponent_is_divided_by_the_transition_standard_deviation`, `..._variance` |
| T-10 | §5 "if the estimate of c … is far outside the observed range of {y_t}, then the estimated model is not satisfactory" (Part 5 §8.2: 5th–95th percentile of the **transition variable**) | `models/flags.py:apply_star_flags` | **Corrected** — used percentiles of the *dependent* variable, which differs from the transition variable whenever `d ≠ 0` | `TestStarCredibilityDiagnostics` |
| T-11 | §5 "excessively large standard deviation estimates for coefficient estimators (other than γ̂) suggest that the model contains redundant parameters" | `fit_star` covariance | **Corrected** — no covariance was computed at all; now Gauss-Newton `σ̂²(J'J)⁻¹` over (γ, c, linear coefficients) | `test_standard_errors_and_covariance_are_produced` |
| T-12 | §5 γ is hard to identify; "the estimated standard deviation of γ … tends to be large for large values of γ" | — | **Compliant** — reproduced, not a defect: a recovery fit gives γ̂=52.6 with SE 79.4 while c is recovered precisely | measured during the audit |
| T-13 | §5 on non-convergence, change the estimation strategy rather than adopt the best point reached | `models/optimize.py:select_best` | **Corrected** — the lowest objective was taken even from a start that reported failure | `TestConvergenceSelection` |

## 2. Luukkonen, Saikkonen & Teräsvirta (1988) — general linearity test

| # | Paper | Code | Assessment | Evidence |
|---|---|---|---|---|
| L-1 | **§2.5**, model (2.12), `H₀₄: d_ij = 0`; LM statistic (2.3) with `ẑ₁ₜ = [y²_{t−1}, y_{t−1}y_{t−2}, …, y²_{t−p}]'`, asymptotically χ²_{p(p+1)/2} | `diagnostics/nonlinearity.py:tsay_test` | **Compliant** — exactly the p(p+1)/2 unique products and that many restrictions | parametrised over p ∈ {1,2,3,4,6} |
| L-2 | §2.5 "suggests an F distribution as an approximation in finite samples" (Keenan) | same | **Compliant**, and labelled as the finite-sample variant in the output | `test_the_f_form_is_the_finite_sample_approximation_the_paper_describes` |
| L-3 | §2.5 "When p = 1, Tsay's statistic F₂ is identical to Keenan's F₁" | same | **Compliant** — one quadratic term at p=1 | `test_for_p_equals_one_there_is_a_single_quadratic_term` |
| L-4 | §1 and §3: power depends on the alternative, on the intercept and on the autoregressive specification; an incorrect LM test can have local power no higher than its size | reporting | **Compliant** — "do not reject" is reported as *no general evidence against* linear dynamics, never as evidence of linearity | `test_failure_to_reject_is_not_reported_as_evidence_of_linearity` |
| L-5 | Numerical agreement with a recognised implementation | `tsay_test` vs R `TSA::Tsay.test` | **Compliant** — agrees on six series to all four significant digits R reports, two of them real frozen thesis data | `test_tsay_vs_r.py` (unchanged by this audit) |

## 3. Hamilton (1989) — Markov-switching model

| # | Paper | Code | Assessment | Evidence |
|---|---|---|---|---|
| H-1 | §4.1, eq. (4.3): `y_t = α₁s_t + α₀ + z_t`, `z_t` a linear AR — the mean-adjusted form | `models/msar.py` | **Compliant** | model identity |
| H-2 | §4.2 expanded state over `(s_t,…,s_{t−r})`, `2^{r+1}` elements (`K^{p+1}` for K regimes) | `_expanded_states`, `_expanded_transition` | **Compliant** | existing tests |
| H-3 | §4.2 Step 2 conditional Gaussian density | `_filter` | **Compliant** in value; **Corrected** in computation — the direct form underflows to exactly zero for an outlying observation or a small trial σ, discarding admissible parameter points as −∞ | identical to 2e-16 relative on well-behaved data; finite where the direct form returns −∞ |
| H-4 | §4.2 Steps 3–5 likelihood and update | `_filter` | **Compliant** — log-likelihood matches `statsmodels.MarkovAutoregression` to 1e-8 at p = 1, 2 and 3 | `test_loglikelihood_matches_statsmodels_at_identical_parameters` |
| H-5 | §4.2 initialisation from the unconditional probability, built from the limiting π of (2.7) | `_stationary` | **Compliant** — the initial vector is the ergodic distribution of the expanded chain and its regime marginal equals `(1−q)/(2−p−q)` | `test_the_filter_starts_from_the_ergodic_distribution` |
| H-6 | §4.2 "the output of the filter is always a well-defined probability distribution" | `_filter` | **Compliant** | `test_filtered_probabilities_are_a_distribution_at_every_date` |
| H-7 | §4.3 smoothing | `_smooth` (Kim recursion) | **Documented variation** — Hamilton's full-sample smoother (Step 2 of §4.3) is implemented as the standard Kim backward recursion, which computes the same `P[S_t \| y₁…y_T]` by a different route | smoothed probabilities verified to be a proper distribution at every date |
| H-8 | §4.2 "the model is unidentified in the sense that the decision of which state to call state 0 … is arbitrary. I normalize things by letting state 1 be the fast growth state" | `fit_msar` ordering | **Compliant** — regimes ordered by estimated mean, one fixed documented rule | `test_regimes_are_ordered_by_mean` |
| H-9 | §4.2 maximum likelihood over the conditional log likelihood | `fit_msar` | **Corrected** — multistart took the lowest objective even from a start reporting failure; now prefers the best converged start and preserves every attempt | `TestConvergenceSelection` |
| H-10 | **Table I and footnote 7**: "Second derivatives of the log likelihood were calculated numerically, from which asymptotic standard errors were constructed" | `fit_msar` + `optimize.numerical_hessian` | **Corrected** — no Hessian or covariance existed; now an observed-information Hessian with delta-method standard errors for σ and the transition probabilities | `TestHamiltonParameterUncertainty`; Hessian verified against an analytic quadratic to 7e-9 |
| H-11 | §6 expected duration of a regime is `(1 − p_ii)⁻¹` | `fit_msar` | **Compliant** | `test_expected_durations_follow_hamiltons_identity` |
| H-12 | §4.2 forecasts condition only on information at the origin | `MSARFit.forecast`, rolling engine | **Compliant** — unchanged by this audit, and still covered by the no-look-ahead tests added with the horizon fix | `test_horizon_coverage.py` |
| H-13 | §4.2 "there is a practical limit on how complicated we can permit the dynamics … and still have hope of obtaining useful results" | credibility flags | **Compliant** — and now detectable: K=3 on INDPRO has two regimes at 1.3% occupancy, a zero self-transition probability and a non-positive-definite observed information, which is disclosed rather than hidden | measured during the audit |

## 4. Part 5 credibility rules reached through this audit

| # | Rule | Assessment | Note |
|---|---|---|---|
| P-1 | §8.1 "Low occupancy or boundary persistence makes a model fragile, not automatically failed. Failure is reserved for … an effectively unidentified regime" | **Corrected** | `EMPTY_REGIME` fired on zero occupancy *alone*; decision D8 requires zero occupancy **together with** corroborating evidence of non-identification. That conjunction was previously unevaluable because no covariance existed. |
| P-2 | §8.2 "Flag as fragile if … the nonlinear Hessian/covariance is singular or unstable" | **Corrected** | `apply_covariance_flags` classified a singular covariance as **failed**. D8 makes it a failure only "when required for meaningful inference"; no Part 6 output reports an inference resting on these matrices. |
| P-3 | §8.2 covariance credibility is assessed at all | **Corrected** | `apply_covariance_flags` existed but was never called from production code — only from a test. Both estimators now invoke it. |

---

## Open items

**None.** The one question flagged in advance — whether the Teräsvirta auxiliary regression
and its reference distribution extend to `d > p`, which the approved delay grids do reach
(GDPC1 has p=1 with delays 1–4) — is answered by the paper itself and needed no change of
the approved grid:

- (3.11) states the null as `β₂ⱼ = β₃ⱼ = β₄ⱼ = 0, j = 1,…,p` with LM ~ **χ²(3p)**, carrying
  no dependence on `d`;
- Teräsvirta applies the test at delays far beyond the autoregressive order in his own
  examples (Table 3 reports `d = 1,…,9` for series with lag length 2);
- §2's "assume for notational simplicity that `d ≤ p`" is what makes (3.10) *complete* in
  that case, because the standalone powers `y^k_{t−d}` are then already spanned by the
  cross-product blocks. Writing the regression as the paper does yields exactly 3p
  restrictions at every delay, which is the precondition for comparing p-values across the
  delay grid in §4.2.

A documented alternative exists and is **not** adopted: augmenting the regression with the
standalone `y^k_{t−d}` terms when `d > p` would retain the score direction associated with
`π₂₀`, the intercept of the nonlinear component, whose loss Teräsvirta discusses in §3.1 as
a power concern in a related setting. It would give `3p + 3` restrictions at `d > p` and
`3p` at `d ≤ p`, making the reference distribution vary across the delay grid and the
minimum-p-value rule inhomogeneous. If you would prefer that variant, say so and it can be
added as a predeclared robustness check rather than as the baseline.
