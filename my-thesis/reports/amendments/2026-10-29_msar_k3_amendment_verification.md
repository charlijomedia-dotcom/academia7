# MSAR K=3 amendment (29 October 2026) — implementation and verification report

Branch `claude/msar3-in-sample-amendment`, from `77b4c74` (the approved
monitoring/scheduling/Colab work). The historical branches
(`claude/trusting-feynman-871wks`, `claude/progress-monitoring`,
`claude/parallel-scheduling-colab`) are untouched. The full Part 8 production run was not
started.

## 1. Modified files

**Approved specifications (Part 5), as you instructed**

| File | Change |
|---|---|
| `approved-specs/part5/part5_methodology_specification.md` | Status line; §11 robustness-table row; §11.1 rewritten (below) |
| `approved-specs/part5/part5_required_outputs_specification.md` | Status line; T4.3 redesigned; new F4.3; P-04 evidence route in §12 |
| `approved-specs/part5/part5_computational_execution_spec.md` | Status line; rolling model set stated in §3 |
| `approved-specs/part5/part5_methodology_decision_log.md` | Dated amendment entry; K=3 row |
| `approved-specs/part5/part5_methodology_vs_jury_matrix.md` | P-04 row |
| `approved-specs/part5/part5_methodology_literature_justification.md` | §3.13 defence sentence and amendment note |
| `approved-specs/part5/part5_methodology_amendment_2026-10-29_msar_k3.md` | **New**: the amendment record (date, reasons, changed requirements, implications) |

**Code, tests, tools, documentation**

| File | Change |
|---|---|
| `code/src/thesis/pipeline.py` | `ROLLING_MODELS = (AR, ARMA, MSAR, STAR)`, `FULL_SAMPLE_MODELS` (adds MSAR3); K=3 removed from the rolling jobs, with a guard that refuses any rolling K=3 job; every full-sample attempt kept, including failed ones; T4.3 rebuilt; F4.3 figure; claim-matrix registration |
| `code/src/thesis/reporting/regime_count.py` | **New**: T4.3 comparison rows, parameter rows and the §11.1 credibility conclusion |
| `code/src/thesis/reporting/figures.py` | Regime-probability figure takes a figure ID and an estimation-status line |
| `code/src/thesis/reporting/tables.py` | P-04 claim registration (results and status empty) |
| `code/src/thesis/monitoring/plan.py`, `forecasting/scheduler.py` | Stage descriptions; comment |
| `code/tools/coverage_matrix.py` | T4.3 requirement and runtime note |
| `code/tools/benchmark_scheduling.py` | `--arms` option |
| `code/tests/integration/test_msar3_amendment.py` | **New**: 20 regression tests |
| `code/tests/integration/test_pipeline.py` | 5 new end-to-end assertions; 2 tests updated to the amended design |
| `code/tests/integration/test_monitoring_pipeline.py` | Chain count per target 5 → 4 |
| `colab/run_thesis_colab.ipynb` | Default branch → this branch |
| `MONITORING.md` | Rolling chain set |
| `reports/amendments/2026-10-29_msar_k3_amendment_verification.md` | **New**: this report |

**Not changed:** the data, transformations, configuration files, windows, horizons,
estimators, optimizer settings, seeds, tests of predictive ability, and every other
robustness exercise. No file in the fit cache's dependency set was modified (§6).

## 2. Final wording of Part 5 §11.1

## 11.1 K=3 regime-count robustness (user-approved amendment, 29 October 2026)

This section supersedes the original §11.1 of 5 October 2026, which also evaluated
out-of-sample forecast performance of a rolling K=3 model. The reasons and implications
are recorded in `part5_methodology_amendment_2026-10-29_msar_k3.md`.

**Purpose.** Answer P-04: whether the two-regime assumption is overly restrictive. The
exercise concerns the credibility of the regime specification, not out-of-sample
predictive superiority.

**Baseline.** MSAR with **K=2** remains the predeclared baseline Markov-switching
forecasting model (§5.5). It is not replaced or re-selected by this exercise.

**Estimation.** For each of the six approved targets, estimate a K=3 model once on the
**same full-sample observations** as the full-sample K=2 fit, with the same approved MSAR
structure (§5.5: regime-specific means, common AR coefficients, common innovation
variance), the same lag-order rule (the BIC-selected AR order, capped at 4 monthly and 4
quarterly), the same deterministic multi-start and optimizer rules, the same
observed-information standard errors, and the same mean-ordering rule for regime labels
(§8.1).

**No rolling K=3 forecasts.** K=3 is **not** re-estimated at pseudo-out-of-sample
forecast origins, and no K=3 out-of-sample forecasts are computed. K=3 therefore enters
no forecast table, ranking, model confidence set, Harvey-Leybourne-Zu, DM-HLN or
state-dependent forecast-loss comparison.

**Comparison.** For K=2 and K=3, on every target, report:

- the estimation sample dates, number of observations and number of parameters;
- log-likelihood, AIC and BIC;
- convergence, optimizer message, starts attempted and converged, the start used, the
  estimation status (adequate / fragile / failed) and every reason code;
- the regime means with their standard errors where the observed-information covariance
  is usable;
- smoothed-probability occupancy and effective observations of every regime, and whether
  a regime is low-occupancy or empty under §8.1 and decision D8;
- the complete transition matrix, with standard errors where estimable, and the expected
  regime durations;
- the covariance status (usable, ill-conditioned, singular) and every transition-boundary
  flag;
- whether adjacent ordered regime means are empirically distinguishable: the absolute
  difference relative to its standard error, compared descriptively with 1.96, or "not
  assessable" when the covariance is unusable;
- for economic interpretability, the average smoothed probability of each regime during
  NBER recession and during expansion periods. These are descriptive. No economic label
  (recession, recovery, expansion) is assigned to a statistical state on their basis.

**Credibility of the additional regime.** K=3 is assessed as **credible** only if all of
the following hold: the estimate converged and is not failed; no regime is flagged
low-occupancy or empty (§8.1, D8); no transition probability is flagged at the boundary
(§8.1); the observed-information covariance is usable (neither singular nor
ill-conditioned); and every pair of adjacent ordered regime means is distinguishable.
Otherwise K=3 is assessed as **not credible**, with each failing condition stated. These
are the §8.1 operational warning thresholds applied unchanged; they are not theoretical
critical values. As §4.3 explains, no likelihood-ratio test of K=2 against K=3 with a
standard reference distribution is reported; the information-criterion comparison is
descriptive.

**Decision.** K=2 is retained as the predeclared baseline **regardless** of whether K=3
has the more favourable in-sample criterion. Where a credible K=3 has a lower BIC (or
AIC), this is reported transparently as in-sample evidence that the two-regime
representation may be restrictive for that target. In-sample superiority is **not**
evidence of superior forecasting performance, and no forecasting claim is made for K=3.

**Reporting.** Non-convergence, boundary estimates, empty or near-empty regimes, singular
or ill-conditioned covariance and every other credibility problem are reported, never
concealed. A K=3 regime-probability figure is produced only for an estimate that did not
fail, and it carries the estimate's status and flags. The final per-target conclusion
states whether K=3 is credible, what the in-sample criteria show, and what this implies
for the maintained K=2 assumption.

## 3. Revised T4.3 output requirements (and F4.3)

## T4.3 K=2 versus K=3 MSAR — in-sample regime-count robustness (amended 29 October 2026)

Mandatory, for **every retained target**. An in-sample comparison of the full-sample K=2
and K=3 fits (methodology §11.1). It answers P-04 on the credibility of the regime
specification; it is **not** a forecast comparison.

`robustness/T4.3_regime_count.csv`, one row per target and regime count:

- series, frequency, estimation sample start and end dates;
- K=2 / K=3 specification label and role (baseline / robustness);
- number of observations and number of parameters;
- log-likelihood, AIC, BIC;
- convergence, optimizer message, starts attempted and converged, start used, selection
  rule;
- estimation status (adequate / fragile / failed) and every reason code;
- covariance status, and singular / ill-conditioned covariance flags;
- minimum occupancy and minimum effective observations across regimes; the regimes
  flagged low-occupancy or empty;
- transition-boundary flags;
- distinguishability of adjacent ordered regime means (|Δμ| / SE), or "not assessable";
- descriptive interpretability fields: each regime's average smoothed probability in NBER
  recession and in expansion periods, with an explicit statement that no economic label
  is assigned to a statistical state;
- whether a regime-probability figure was produced, and why not if it was not.

`robustness/T4.3_regime_parameters.csv`, one row per target, regime count and parameter:
regime means, AR coefficients, innovation standard deviation, every transition
probability, expected durations and occupancies, with standard errors where estimable
and the relevant boundary or low-occupancy warning on the row it concerns.

`robustness/T4.3_regime_count_conclusion.csv`, one row per target:

- log-likelihood, AIC and BIC differences (K=3 minus K=2), and which regime count each
  criterion favours;
- whether K=3 is credible under the §11.1 rule, with every failing condition listed;
- the documented regime-count robustness conclusion and what it implies for the
  maintained K=2 assumption; the maintained baseline is K=2 in every row;
- the statement that the comparison is in-sample and is not evidence about forecasting
  performance.

Excluded by design: K=3 out-of-sample RMSE, MAE, OOS R², predictive-ability tests, model
confidence set membership and rolling-origin counts. No column may report a K=3 forecast
metric, because none is computed.

Machine-readable diagnostics and provenance follow the rules of §1 and §9 (T4.7): every
K=3 reason code is also in the failure and fragility registry.

## F4.3 K=3 smoothed regime probabilities (amended 29 October 2026)

One figure per target whose full-sample K=3 estimate did not fail, one panel per regime,
with NBER recession shading. The title carries the estimation status and any credibility
flags, so a fragile estimate is never shown as if it were clean. No figure is produced
for a failed estimate; T4.3 records why.

## 4. Test results

```
866 passed, 0 failed, 0 skipped, 0 errors    (57m50s)
```

Complete suite, `FRED_API_KEY` unset; collected = 866 = passed. That is the 841 tests of
the approved scheduling/Colab work, all still passing, plus 25 new ones.

| Requirement | Test |
|---|---|
| K=3 still fitted on the full sample for all six targets | `test_every_target_has_a_k3_specification_with_the_k2_lag_order` (six targets, real data); `TestMSAR3Amendment::test_k3_is_fitted_on_the_full_sample_for_every_target` (end to end); and an all-six-target run (§7) |
| K=3 never submitted as a rolling chain | `test_no_rolling_job_or_planned_chain_is_k3`; `test_a_k3_rolling_job_is_refused` (the guard); `test_no_rolling_k3_fit_or_forecast_exists` |
| K=2 rolling estimation unchanged | `test_k2_rolling_chains_are_unchanged`; `test_no_fit_critical_code_changed` (code hash pinned to the pre-amendment value); the cache-reuse run (§6) |
| T4.3 holds the in-sample comparison, with failed and fragile estimates reported | `TestRegimeCountTable` (real, failed and fragile fits); `TestConclusionRule` (every branch of the §11.1 rule); `test_t43_holds_the_in_sample_comparison_for_every_target`; `test_k3_figures_exist_only_for_estimates_that_did_not_fail` |
| No K=3 forecast metric presented as computed | `test_no_forecast_metric_appears`; `test_k3_appears_only_in_in_sample_tables` (scans every table of the run) |
| All other tables, figures, predictive tests and robustness exercises still produced | The existing required-outputs and guarantees tests (69 in `test_pipeline.py`, all passing) |
| Compatible cached K=2 results reusable | `test_no_fit_critical_code_changed`; the real cache-reuse run (§6) |
| P-04 routed to the in-sample comparison, left unadjudicated | `TestClaimRegistration`; `test_claim_matrix_is_valid_and_left_unpopulated_in_part_6` |

## 5. Rolling workload, old versus new (exact, real baseline configuration)

| | Before | After | Change |
|---|---:|---:|---:|
| Rolling chains (pooled + VAR + 6 ARMA-GARCH) | 121 | 115 | −6 (the K=3 chains) |
| Planned forecast origins | 72,233 | 68,706 | −3,527 |
| Origins actually estimated (others reuse the forecast-stage cache) | 58,125 | 54,598 | −3,527 |

Every other block is identical: baseline AR, ARMA, MSAR(2) and STAR, 3,527 origins each;
T4.1, 1,329 origins per model; T4.2, 2,860; T4.5 VAR, 571; T4.6 ARMA-GARCH, 3,527 (only
where the ARCH-LM screen rejects); T4.8, 10,581 per model, of which 7,054 are estimated.

## 6. Cache audit

* **Code hash unchanged**: `93ca1685fda15e4b28ee81f7addf9608c6ed70575e2439eb7ee204f4f10fef87`
  before and after. None of the 13 fit-critical files changed, and no configuration file
  changed. Every cache key is therefore identical, and every cached AR, ARMA, MSAR(K=2)
  and STAR fit remains valid. The Colab notebook's cache identity
  (code + configuration + data) is also unchanged, so it restores your existing Drive
  backups. Cached rolling K=3 fits remain on disk but are never requested.
* **Demonstrated, not inferred.** The amended reduced run was executed against the fit
  cache of the last pre-amendment reduced run. 576 of 594 rolling origins were served
  from it; the remaining 18 are the VAR, which never uses the fit cache. There were no
  reconciliation warnings or failures.
* **Per-source-file impact on cache hashes:** `pipeline.py`, `reporting/*.py`,
  `monitoring/plan.py`, `forecasting/scheduler.py`, the tools, tests, documentation and
  notebook are outside the cache's dependency set. None affects any cache key.

## 7. Verification that the rest is unchanged

* **Outputs of the reduced run, before versus after**, on identical data with the cache
  above:
  * every table not touched by the amendment is identical, cell for cell;
  * every table that changed equals the pre-amendment table with its rolling K=3 rows
    removed: per-series forecasts, origin audit, horizon coverage, failure registry,
    T4.9 forecast exposure, and the non-K=3 status counts (verified by filtering);
  * the only additions are T4.3's three tables, F4.3 figures and the P-04 claim row;
  * run metadata (runtime notes, checkpoint hashes) differ as expected.
* **All six targets.** Stages 1–6 and T4.3 were run on the real baseline configuration
  into a scratch directory (not `output/`). The result had K=2 and K=3 rows for all six
  targets, 6 conclusion rows, 240 parameter rows and 6 F4.3 figures (no K=3 estimate
  failed). The full-sample stage took 21 minutes while competing with the test suite.
* The model labels, horizons, windows, specifications, HLZ, DM-HLN, MCS, state
  regressions, T4.1, T4.2, T4.4, T4.5, T4.6, T4.8 and T4.9 are produced exactly as
  before, without K=3 rows.

## 8. Can the full run finish within 24 hours on Colab Pro+?

**Measured here** (this machine, 4 vCPUs): the revised rolling workload with 4 workers
and the same cap of 6 origins per chain took **1,225 s, against 1,910 s before the
amendment** (−36%), and 2,736 s under the original one-pool-per-batch design. Worker
utilization was 90%. K=2 MSAR is now 82% of the busy time.

**Projected for the full run** (not measured). The estimated work on this machine:

| Block | Fits | Seconds per fit | CPU-hours |
|---|---:|---:|---:|
| MSAR K=2 | 11,910 | 12–30 | 40–100 |
| ARMA | 11,910 | ≤ 4.5 | ≤ 15 |
| STAR | 11,910 | ≤ 2.2 | ≤ 7 |
| Full-sample fits, evaluation, VAR, ARMA-GARCH | | | ≈ 1–3 |

The low end of each per-fit figure comes from the performance audit's single-fit timings;
the high end is the benchmark's per-origin busy time under four-way contention. In total
that is about 45–120 CPU-hours, or **roughly 12–33 hours of wall time here** with four
workers at 90% utilization. The range is wide because the per-origin MSAR cost varies
2–3× between early and late windows and with CPU contention.

**On Colab.** Your earlier run completed about 2.8% of origins in 24 hours. The
performance audit inferred that this is a third to a quarter of this machine's
throughput. If that holds, the revised run would take longer than 24 hours on the same
runtime, **so 24 hours is not assured and should not be assumed.** It could fit if the
runtime has more physical cores than the earlier one, or if the separately proposed
bit-identical likelihood speed-up (≈ 1.6× on MSAR fits) is approved.

The decisive check is cheap. Start the run; after about an hour the monitor's global
summary reports mean fit time per model and an UNCERTAIN remaining-time estimate, and
notebook cell 1 reports the CPU count. Those numbers turn this range into a figure for
your runtime.

## 9. Unresolved issues

1. **AR record dates when served from the cache (predates the amendment; cosmetic).**
   A freshly estimated AR fit records its effective post-lag sample start; the same fit
   served from the cache records the window's first date. `fit_records.csv` can
   therefore show two `window_start` conventions for AR within one run: the T4.8
   baseline-length chains, or any fit restored after a Colab resume. No forecast,
   estimate or test is affected. Fixing it requires a change to a fit-critical file,
   which would invalidate the existing cache, so it is left for your decision. One
   option is to fix it together with the cache-preserving equivalence record proposed in
   the performance audit.
2. **Interpretive note on P-04's wording.** Part 2 asks whether the third regime is
   "empirically meaningful, stable, and useful". Under the amendment, "useful" is judged
   in-sample (fit, credibility, interpretability). The amendment record says so, and the
   thesis text should too.
3. **Runtime on Colab** is not yet known for the revised design (§8). This is not a
   blocker, but a measurement to take before relying on any deadline.

Nothing else prevents safe execution.
