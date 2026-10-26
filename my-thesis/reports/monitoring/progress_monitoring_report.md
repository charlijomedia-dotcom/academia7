# Progress monitoring and diagnostic logging — implementation report

Branch: `claude/progress-monitoring` (from the approved Part 7 head `d06e427`).
Scope: observability only. No estimator, specification, window, horizon, origin set,
optimizer setting, seed, replication count, test, threshold, forecast or output
definition was changed. Part 8 was not started.

## 1. What the monitor answers, at any moment

| Question | Where it is answered |
|---|---|
| Which stage of the methodology? | Stage banners (`STAGE 7/10 START: Pseudo-out-of-sample rolling forecasts`), every heartbeat and summary, `progress.json → current_stage`. The execution-stage number, the Comp §5 checkpoint and the Part 5 section are three separate fields |
| Which series and model? | `CHAIN START` lines, the per-worker heartbeat lines, `active_tasks` in the snapshot |
| Which window and origin? | Progress lines and heartbeats (`origin 2025-03 \| window 2005-04..2025-03`; quarterly shown as `2022Q1`) |
| Which horizons? | `CHAIN START … \| h=1,3,6,12` |
| How many done, how many left? | Per chain (`completed 6/18 origins, 12 left`), per batch, and globally split baseline / robustness |
| How long has the current calculation run? | `fit running 56s, active: MSAR K=3 observed-information Hessian` |
| What is consuming the time? | Mean fit time by model and frequency, the ten slowest fits, and timed operations (full-sample fits, HLZ, null simulations, DM-HLN, MCS, state regressions, VAR, ARMA-GARCH) |
| What remains before the end? | Remaining chains and origins, the outstanding stages, `Next: stage 8/10 …`, and an estimate labelled UNCERTAIN where one can honestly be made |

## 2. Files

**Created**

| File | Purpose |
|---|---|
| `code/src/thesis/monitoring/__init__.py` | Package entry |
| `code/src/thesis/monitoring/probe.py` | The hook computational code calls: `emit`, `substep`, `operation`, `timed`, `ChainReporter`, the worker queue sink and worker liveness thread. A no-op when no monitor is installed |
| `code/src/thesis/monitoring/plan.py` | The ten execution stages (`StageSpec`) and the chain plan (`ChainPlan`) |
| `code/src/thesis/monitoring/state.py` | The run's progress state, changed only by applying events; all counters, remaining work, and the estimate. Pure, no I/O |
| `code/src/thesis/monitoring/render.py` | Console blocks: banners, chain lines, heartbeat, global summary |
| `code/src/thesis/monitoring/monitor.py` | The parent-process service: console + `execution.log`, `events.jsonl`, atomic `progress.json`, heartbeat thread, worker queue listener, Drive mirror |
| `code/tools/compare_runs.py` | Compares two runs' research outputs, excluding only documented run-time metadata |
| `colab/run_thesis_colab.ipynb` | Colab Pro+ notebook: install, verify, background run, live log, Drive mirror |
| `MONITORING.md` | User guide |
| `code/tests/unit/test_monitoring_state.py`, `test_monitoring_service.py`, `test_colab_notebook.py` | Unit tests |
| `code/tests/integration/test_monitoring_chains.py`, `test_monitoring_pipeline.py`, `test_entry_point_monitoring.py` | Integration tests |

**Modified**

| File | Change |
|---|---|
| `code/run_all.py` | Creates and closes the monitor; `--no-monitor`, `--log-mirror` (or `$THESIS_LOG_MIRROR`), `--heartbeat-seconds`, `--summary-seconds`; line-buffered stdout/stderr; failure and interruption recorded before re-raising; `run_logs/` excluded from the clean-tree check as the run's own product |
| `code/src/thesis/pipeline.py` | Each of the ten stages wrapped in a monitored context; one `task` call per unit of serial work; the rolling plan (`rolling_plan`); job builders for the baseline, T4.1, T4.2 and T4.8 chains factored out so the stages and the plan use the same code; VAR and GARCH loops report origins; module-level timing wrappers for expensive functions |
| `code/src/thesis/forecasting/rolling.py` | Origin-level progress events (`ChainReporter`); new keyword `task_id`, used only as a label |
| `code/src/thesis/forecasting/parallel.py` | `ChainJob.task_id`; workers send events on a queue and report liveness; the parent reconciles each returned result with the events |
| `code/src/thesis/models/msar.py`, `models/star.py` | One `probe.substep` call naming the active multistart; MSAR also names the Hessian step |
| `code/src/thesis/models/registry.py` | One `probe.substep` naming the STAR simulation forecast |
| `code/src/thesis/evaluation/hlz.py` | The HLZ null-distribution simulation is timed |
| `code/src/thesis/core/checkpoints.py` | Optional `on_record` callback so the monitor learns of each checkpoint |
| `code/src/thesis/core/paths.py` | `RUN_LOGS_DIR`, `run_log_dir()` |
| `.gitignore` | `run_logs/` |
| `REPRODUCING.md` | §6 table row and §6.1 "Watching a long run" |
| `code/tests/unit/test_clean_tree.py` | Run logs do not block a rerun; a real input change still refuses |

## 3. Architecture

```
 worker process 1..4                               parent process
 ┌───────────────────────────┐                    ┌──────────────────────────────────────┐
 │ run_chain                 │  events            │ listener thread ── handle(event) ──┐ │
 │   ChainReporter ──────────┼──► mp.Queue ──────►│                                   │ │
 │ fit_msar / fit_star       │                    │ pipeline stages ── handle(event) ──┤ │
 │   probe.substep ──────────┤                    │                                   ▼ │
 │ liveness thread (30 s) ───┘                    │   RunState.apply  (under one lock)  │
 └───────────────────────────┘                    │      │                              │
                                                  │      ├─► console + execution.log    │
                                                  │      ├─► events.jsonl (append)      │
                                                  │      └─► progress.json (atomic)     │
                                                  │ heartbeat thread (1 s tick):        │
                                                  │   60 s heartbeat, 5 min summary,    │
                                                  │   10 s snapshot, Drive mirror       │
                                                  └──────────────────────────────────────┘
```

- **Only the parent writes.** Workers never touch the console or a file; they put events
  on a `multiprocessing` queue passed to the pool initializer (works under `fork` and under
  `spawn`, which Windows uses). One lock serializes every write, so messages from four
  workers can never interleave or corrupt one another.
- **Long computations stay visible.** When a worker starts a fit it sends `origin_start`;
  the parent's own heartbeat thread then measures how long it has been running, however
  long the optimizer takes. A liveness thread in each worker reports its CPU time every
  30 s, so a slow fit (CPU advancing) is distinguishable from a dead process. Inside a fit,
  the active multistart and the Hessian step are reported.
- **The state is a pure function of the events.** `RunState.apply` is the only way it
  changes, which is what makes the counters testable against real computations.
- **Reconciliation.** When a chain returns, the parent compares the event-derived counts
  with the returned `ChainResult` and logs any disagreement; the result wins. No
  disagreement occurred in any test or run.
- **Flushing.** Every console/log line is flushed as written; stdout/stderr are put in
  line-buffered mode; the logs are `fsync`ed every 30 s; the snapshot is rewritten every
  10 s even when nothing changed, so its timestamp is a liveness signal.
- **Overhead.** One event per origin start/end and per optimizer start; a 30-minute
  reduced run produced 4,650 events (796 KB), a 95 KB console log and a 9 KB snapshot,
  with no measurable effect on run time.

### Logging cadence

| Event | Frequency |
|---|---|
| Stage start/end banners | Immediately |
| Chain start/end lines | Immediately |
| Chain progress lines | First origin and each 10% of a chain, at most one per 15 s per chain |
| Heartbeat (per-worker detail) | Every 60 s while something has been running for over 60 s |
| Global summary | Every 5 min |
| Notice "no computation has completed for N min; fits still running — not a failure" | In the heartbeat after 10 quiet minutes |

## 4. How completed and remaining work is calculated

Three units are distinct throughout: **chains** (one series × model × specification ×
window length), **forecast origins** (one estimation at one window = one model fit or
one cache-served fit), and **forecast records** (one horizon-specific forecast; one fit
produces one record per horizon with a realized target).

- **Planned totals are exact.** After the specification stage fixes every discrete
  choice, `Pipeline.rolling_plan()` enumerates every chain — baseline AR/ARMA/MSAR/STAR,
  the rolling K=3 MSAR chains (T4.3), T4.1, T4.2, T4.8 — from the same job builders the
  stages use, and counts its origins with the same `estimation_origins` the rolling engine
  uses. They are not inferred from cache files.
- **Provisional totals are labelled.** T4.6 ARMA-GARCH runs only where the ARCH-LM screen
  rejects; T4.5 VAR only if a stable lag order exists. Each counts as remaining until its
  stage decides, and is then marked *skipped* (removed from the total, explicitly) or run.
- **Completed** counts origin events as they happen, per chain; the parent then
  reconciles with the returned result.
- **Remaining** per chain is `max(0, planned − completed)` while the chain is active and 0
  once it has ended or been skipped. It cannot silently go negative: an overrun raises the
  planned total to the observed count and logs a warning. It reaches zero only when every
  non-skipped chain has ended.
- **Stage tasks** (full-sample fits, series × horizon evaluations, the eight robustness
  exercises, …) are counted per stage against a planned number; more tasks than planned
  raise the total with a warning.

### Estimate of remaining time

Given only from observed speed, and labelled **UNCERTAIN**: mean fit time per (model,
frequency) after at least five timed fits; cache-served fits and chains expected to be
served from the cache excluded; work of untimed models named with its origin count rather
than guessed; batches summed, each contributing max(longest chain, total ÷ workers) — a
scheduling lower bound. It covers rolling fits only. Example from the reduced run:

```
  Estimate         UNCERTAIN: at least 10m40s of wall time (17m46s fit CPU) for 81% of the remaining rolling fits; excludes evaluation bootstraps and tables
                   not estimated (no timings yet): ARMA-GARCH/M 18 origins, ARMA-GARCH/Q 18 origins, MSAR3/M 17 origins, VAR/M 18 origins
                   plan partly provisional (GARCH/VAR run only if their screens pass)
```

## 5. Sample console output (reduced smoke run, `python code/run_all.py --smoke-test`)

Default intervals (heartbeat 60 s, summary 5 min). Run `smoke-20261026T143125-b0fb004b`,
29 min 38 s, 2 workers (the smoke configuration).

```
[14:31:40] STAGE 6/10 START: Full-sample in-sample adequacy and credibility
  started        2026-10-26 14:31:40 UTC
  checkpoint     model_fits   (methodology: Part 5 §7, §8)
  operations     full-sample AR, ARMA, MSAR, STAR, MSAR3 fits, residual battery, Hessian standard errors, credibility flags, tables T3.1-T3.2, figures F3.1-F3.3
  series         GDPC1, INDPRO
  models         AR, ARMA, MSAR, STAR, MSAR3
  planned tasks  10 full-sample fits
==============================================================================
[14:35:27] HEARTBEAT  stage 6/10 Full-sample in-sample adequacy and credibility  (run 4m02s)
  Operation: MSAR single fit INDPRO running 2m58s
  Task: INDPRO MSAR(p=4,K=3) full-sample fit and diagnostics (running 2m58s), stage tasks 9/10, active: MSAR K=3 likelihood maximization, start 2/2 (deterministic_p0.95)
[14:36:25] HEARTBEAT  stage 6/10 Full-sample in-sample adequacy and credibility  (run 5m01s)
  Operation: MSAR single fit INDPRO running 3m56s
  Task: INDPRO MSAR(p=4,K=3) full-sample fit and diagnostics (running 3m56s), stage tasks 9/10, active: MSAR K=3 observed-information Hessian
[14:36:28] MSAR single fit INDPRO finished in 3m59s (ok)
------------------------------------------------------------------------------
[14:36:32] STAGE 6/10 DONE: Full-sample in-sample adequacy and credibility
  elapsed        4m52s
  tasks done     10/10
  registered     0 failed estimations, 17 fragility flags, 0 data gaps (failure registry T4.7)
```

```
[14:40:30]   INDPRO | MSAR3 | window 2005-03..2025-02 | origin 2025-02 | 1/18 (6%), 17 left | valid 1, failed 0 | mean fit 39.98s | chain 40s
[14:41:25] HEARTBEAT  stage 7/10 Pseudo-out-of-sample rolling forecasts  (run 10m01s)
  Worker 1: INDPRO | MSAR | origin 2025-08 | window 2005-09..2025-08 | baseline
            fit running 3s, active: MSAR K=2 likelihood maximization, start 2/3 (deterministic_p0.9)
            completed 6/18 origins, 12 left; mean fit 17.90s; last event 2s ago
            process alive: last heartbeat 21s ago, cpu 3m19s, rss 321 MB
  Worker 2: INDPRO | MSAR3 | origin 2025-03 | window 2005-04..2025-03 | T4.3 K=3 regime count (rolling MSAR3)
            fit running 56s, active: MSAR K=3 observed-information Hessian
            completed 1/18 origins, 17 left; mean fit 39.98s; last event 1s ago
            process alive: last heartbeat 21s ago, cpu 2m18s, rss 327 MB
  Batch forecasting:INDPRO: 3 done, 2 active, 0 queued of 5 chains
  GLOBAL: chains 8/37 done, 2 active, 27 queued; rolling origins (baseline + robustness) 151 done, 515 remaining of 666
==============================================================================
[14:41:25] GLOBAL SUMMARY   run smoke-20261026T143125-b0fb004b
==============================================================================
  Current stage    7/10 Pseudo-out-of-sample rolling forecasts (running 4m53s, tasks 1/2)
  Stages           6 complete, 1 active, 0 failed, of 10
  Chains           8 complete, 2 active, 27 pending, 0 skipped, 0 errored, of 37 planned (3 provisional)
  Baseline origins 132 done, 12 remaining of 144 (132 fitted, 0 cached; 386 forecast records)
  Robustness       1/29 chains; 19 origins done, 503 remaining of 522
  Elapsed          10m01s
  Resources        cpu 97%, run rss 1.05 GB, system memory 0.9/16.9 GB (5%)
  Last progress    3s ago: INDPRO MSAR origin 2025-07-01 done
  Last checkpoint  model_fits at 2026-10-26 14:36:32 UTC
  Mean fit time    MSAR3/M 39.98s (n=1); MSAR/M 17.90s (n=6); MSAR3/Q 8.82s (n=18); MSAR/Q 3.58s (n=18); STAR/Q 1.25s (n=18); STAR/M 0.74s (n=18)
  Costliest ops    MSAR single fit 4m42s (n=4, max 239.2s); STAR single fit 2s (n=2, max 2.1s); ...
  Estimate         UNCERTAIN: at least 10m40s of wall time (17m46s fit CPU) for 81% of the remaining rolling fits; ...
  Next             stage 8/10 Forecast evaluation
==============================================================================
```

```
[15:01:02] CHAIN DONE INDPRO | MSAR | window 300 | 18/18 origins: 18 valid, 0 failed, 0 data gaps, 0 cached | 18 forecasts | mean fit 18.56s | chain 5m34s
------------------------------------------------------------------------------
[15:01:03] STAGE 9/10 DONE: Robustness exercises
  elapsed        7m25s
  tasks done     8/8
  chains         25 done, 2 skipped, 0 errored (of 27)
  origins        450 (306 fitted, 144 from cache); 0 failed estimations
  forecast recs  522
  registered     0 failed estimations, 261 fragility flags, 0 data gaps (failure registry T4.7)
  overall        9/10 stages complete; next: stage 10/10 Registries, manifests and logs
```

The final `progress.json`: status `complete`; chains 35 done + 2 skipped (the two GARCH
chains, whose ARCH-LM screens did not reject) of 37; origins 630 completed, **0
remaining**, 486 fitted and 144 from the cache (the T4.8 baseline-length chains, as
planned); 0 warnings, 0 failures. For contrast, the same run with `--no-monitor` printed
27 console lines in 30 minutes, all before the analysis began.

## 6. Proof that numerical results are unchanged

1. **Real end-to-end smoke runs.** The approved reduced configuration was run twice from a
   cold cache: with the monitor, then with `--no-monitor`. `code/tools/compare_runs.py`
   found **identical research outputs**: 56 tables compared cell by cell, 62 figures byte
   for byte, 63 JSON sidecars, and the 9 stage checkpoints, whose output hashes cover each
   stage's results. Excluded, as documented: the provenance columns (run ID, timestamp,
   commit, …), elapsed-time columns, and the two run manifests.
2. **Pipeline test** (`test_monitoring_pipeline.py`): the reduced pipeline run with and
   without a monitor (two workers, cache on) gives identical outputs and checkpoints, and
   identical run summaries.
3. **Chain tests** (`test_monitoring_chains.py`): identical forecasts, fit parameters,
   statuses and failure events against an unmonitored serial reference, both serially and
   on four workers, and on two workers with the `spawn` start method.

The monitor only reads values a calculation has already produced; nothing it holds is read
back. The estimator changes are one reporting call before an optimizer start; the calls to
`minimize` are unchanged.

**Cache note.** `rolling.py`, `msar.py` and `star.py` are in the fit cache's dependency
hash, so fits cached by earlier code are refitted once on this branch. You planned a fresh
run, so this costs nothing; the numbers are the same either way.

## 7. Tests

RESULT_PLACEHOLDER

New tests, by property:

| Property (request §10) | Tests |
|---|---|
| Stage, chain, origin, worker tracking | `test_monitoring_state.py` (37), `test_monitoring_service.py` (19) |
| Counters equal actual computations | `TestFourWorkers::test_counters_equal_the_computed_results`; `test_chain_counters_match_the_forecast_origin_audit` (row by row against the run's own audit table); `test_every_planned_chain_ran_with_the_planned_origin_count` |
| Remaining never negative, never falsely zero | `TestRemainingNeverLies` (9 tests) |
| Failure, interruption, long-running fit | `TestLongRunningAndFailures`, `TestSlowAndFailingFits` |
| Four parallel workers | `TestFourWorkers` (6 tests), spawn-mode test |
| Same results with and without monitoring | Section 6 |
| Provenance and clean-tree safeguards | `TestRunLogsDoNotBlockReruns` (5); the existing D14 tests unchanged and passing |
| Colab notebook | `test_colab_notebook.py` (4) |

## 8. What the monitor already shows about the 24-hour runtime

Observed on the reduced run (these are diagnostic observations, not changes):

- **K=3 Markov switching dominates.** Mean rolling fit time at the monthly baseline
  window: MSAR3 ≈ 46 s, MSAR ≈ 18 s, STAR ≈ 0.7 s, ARMA ≈ 0.15 s, AR ≈ 0.003 s. The
  full-sample INDPRO MSAR3 fit alone took 4 min; the heartbeat shows both multistarts
  and then the observed-information Hessian as the active steps.
- **The worker pool idles behind MSAR3.** Rolling chains are launched one series at a time
  (five chains per batch, a new worker pool each time). AR, ARMA, STAR and MSAR finish
  early and the MSAR3 chain then runs alone: in the reduced run (two workers) the INDPRO
  batch spent its last 9 minutes (14:44:36 → 14:53:34) on one worker while the other sat
  idle. The baseline's four workers make the idle share larger, not smaller. A full monthly MSAR3 chain has several hundred origins, so this
  single-worker tail, repeated for every monthly series, is the main reason the full run
  exceeds a day.

FULL_PLAN_PLACEHOLDER

These are reported, not acted on: this branch is observability only. A change of
scheduling (for example submitting every series' chains to one pool) would not alter any
number (parallel = serial is asserted by test) but is an execution change outside this
request, so it is offered for your decision rather than made.

## 9. Running it on Colab Pro+ (High-RAM, Python 3.11, four workers)

1. Open `my-thesis/colab/run_thesis_colab.ipynb` in Colab (File → Open notebook → GitHub,
   repository `charlijomedia-dotcom/academia7`, branch `claude/progress-monitoring`).
2. Runtime → Change runtime type → High-RAM.
3. If the repository is private, add a `GITHUB_TOKEN` secret (key icon in the left bar).
4. Run cells 1–4: mount Drive, clone the branch, install `requirements.lock.txt`, verify
   the frozen data (`--data-only`).
5. Optionally run cell 5 (reduced run) to see the output.
6. Run cell 6: starts `python -u code/run_all.py --log-mirror /content/drive/MyDrive/thesis_run_logs`
   in the background with `nohup`.
7. Run cell 7 to watch the live log; re-run it after any browser disconnect.
8. After completion, cell 8 copies `output/` to Drive.

The logs in `MyDrive/thesis_run_logs/baseline/<run_id>/` are updated every two minutes
(new bytes only). After an unexpected termination, `progress.json` there names the stage,
each worker's series, model, origin and fit duration, the last completed computation and
the last checkpoint. The notebook writes its own files to `/content/`, never into the
clone, because the clean-tree safeguard would otherwise refuse the baseline run.

If you use your own notebook instead, the only changes needed are: launch with
`python -u code/run_all.py --log-mirror <Drive folder>`, and keep any file the notebook
writes outside `my-thesis/`.

## 10. Limitations

- **Optimizer internals.** The active multistart and the MSAR Hessian are reported; the
  iteration count *inside* one `scipy.optimize.minimize` call is not, because that would
  require passing a callback into the optimizer, which this request ruled out as touching
  the estimator.
- **The estimate is a lower bound with stated coverage.** MSAR fit times vary with the
  window and the warm start; T4.8's 180/300 windows differ from 240; the evaluation and
  bootstrap stages are excluded (they took seconds in the reduced run but scale with
  replications: 5,000 MCS and 50,000 HLZ draws in the full configuration).
- **Provisional chains** (GARCH, VAR) inflate "remaining" until their stage decides.
- **Worker liveness** is reported every 30 s; a worker killed by the operating system
  shows its last signal ageing rather than an explicit "dead" status.
- **Drive mirror** lags by up to two minutes; the final copy is made at the end of the run.
- **Colab** behaviour was validated by test (notebook structure, live flushing, spawn and
  fork worker channels) but not executed on a Colab runtime from here.
