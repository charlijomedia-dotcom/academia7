# Watching a long run: the progress monitor

The full baseline run can take more than a day. While `code/run_all.py` runs, a progress
monitor reports what it is computing, how far it has got, and what remains. It is an
**observer only**: it never feeds a value back into an estimator, a forecast, a test or a
table, and a test suite asserts that every research output is identical with the monitor
on or off (section 8).

## 1. What appears on the console

| When | What |
|---|---|
| Start and end of each of the 10 stages | A banner: stage number, name, UTC start, the Comp §5 checkpoint, the Part 5 section(s) it implements, the operations, series and models, planned tasks; at the end the elapsed time, tasks done, chains and origins completed, failures, and what runs next |
| Start and end of each rolling chain | Series, model, specification (with K for Markov switching), window length, horizons, origin count, exercise (baseline, T4.3 K=3, T4.8 window 180, ...); at the end valid / failed / data-gap / cached origins, forecast records, mean fit time, chain time |
| Every ~10% of a chain | Current rolling window, forecast origin, completed / remaining origins, valid and failed fits, mean fit time |
| Every 60 s, when something has run for over 60 s | **Heartbeat**: each worker's series, model, origin and window, how long the current fit has been running, the active optimizer step (e.g. `MSAR K=3 likelihood maximization, start 2/3 (deterministic_p0.95)`), its completed / remaining origins, and its process's last liveness signal and CPU time |
| Every 5 minutes | **Global summary**: stage, stages done, chains done / active / pending, baseline and robustness origins done / remaining, elapsed time, CPU and memory, longest-running task, last completed computation, last checkpoint, mean fit time by model, costliest operations, the next stage, and an estimate where one can honestly be made |

Example heartbeat (from the reduced run):

```
[13:54:23] HEARTBEAT  stage 7/10 Pseudo-out-of-sample rolling forecasts  (run 6m41s)
  Worker 1: GDPC1 | MSAR | origin 2025Q2 | window 1995Q3..2025Q2 | baseline
            fit running 1s, active: MSAR K=2 likelihood maximization, start 2/3 (deterministic_p0.9)
            completed 14/18 origins, 4 left; mean fit 4.78s; last event 1s ago
            process alive: last heartbeat 8s ago, cpu 1m33s, rss 301 MB
  Worker 2: GDPC1 | MSAR3 | origin 2022Q1 | window 1992Q2..2022Q1 | T4.3 K=3 regime count (rolling MSAR3)
            fit running 21s, active: MSAR K=3 likelihood maximization, start 3/3 (deterministic_p0.95)
            completed 1/18 origins, 17 left; mean fit 18.66s; last event 7s ago
            process alive: last heartbeat 8s ago, cpu 1m52s, rss 307 MB
  Batch forecasting:GDPC1: 3 done, 2 active, 0 queued of 5 chains
  GLOBAL: chains 3/37 done, 2 active, 32 queued; rolling origins (baseline + robustness) 69 done, 597 remaining of 666
```

**A slow fit is never reported as a failure.** If nothing completes for ten minutes the
heartbeat says so explicitly and shows that the fits are still running; the worker's CPU
time advancing is the evidence that it is computing, not hung.

## 2. The three log files

Every run writes to `my-thesis/run_logs/<namespace>/<run_id>/` (and
`run_logs/<namespace>/LATEST` names the newest run):

| File | Purpose |
|---|---|
| `execution.log` | Exactly what the console showed, with timestamps |
| `events.jsonl` | Append-only structured events, one JSON object per line: stage, task, chain, origin, optimizer-step, operation, heartbeat, warning and failure events, each with a UTC epoch time and process ID |
| `progress.json` | The current state, rewritten atomically (write, then rename) every 10 s and at every stage or chain transition. A reader never sees a half-written file |

`progress.json` holds the run ID and status, the current stage with its task counts, every
stage's status, the active chains (worker, series, model, specification, exercise, window,
origin, how long the current fit has been running, active optimizer step, completed and
remaining origins, valid and failed fits), active operations, chain and origin totals split
into baseline and robustness, the longest-running task, the last completed computation, the
last checkpoint, mean fit times, the ten slowest fits, operation timings, warnings,
failures, the outstanding stages and chains, and resource use.

`run_logs/` is **outside `output/`** and is excluded from version control. Its timestamps
therefore never touch a thesis-facing table or figure or their checksums, and its presence
never makes the clean-tree safeguard refuse the next baseline run. A change to the code,
configuration, specifications or frozen data still does.

**After an unexpected termination** (a Colab runtime that stopped, a power cut), open the
last `progress.json`: `updated_utc` is when the run was last alive, `active_tasks` shows
what each worker was computing and for how long, and `last_progress` names the last
completed computation. `events.jsonl` has the full history up to that point.

## 3. How completed and remaining work is counted

Three units are kept separate throughout:

- a **chain** is one (series, model, specification, window length) rolling exercise;
- a **forecast origin** is one estimation of a chain on one window: one model fit, or one
  fit served from the cache;
- a **forecast record** is one horizon-specific forecast. One fit produces a record for
  every horizon that still has a realized target, so records outnumber origins.

Once the specification stage has fixed every discrete choice, the run builds its complete
rolling plan: every chain of the baseline forecasts (including the K=3 MSAR chains for
T4.3), T4.1, T4.2 and T4.8, from the same job builders the stages use, with origin counts
from the same `estimation_origins` function the rolling engine uses. The totals are
therefore exact, and a test runs the pipeline and checks every planned chain against what
actually ran.

Two exercises cannot be known in advance and are marked **provisional**: the ARMA-GARCH
chains (T4.6) run only for series whose ARCH-LM screen rejects, and the VAR (T4.5) only if
a stable lag order exists. They count as remaining until their stage decides; a chain
that is not needed is then marked *skipped* and leaves the total explicitly.

Remaining counts cannot silently go wrong:

- they are never negative. If more origins complete than were planned, the total is
  raised to the observed count and a warning is logged;
- they reach zero only when every non-skipped chain has ended;
- the parent compares each chain's event-derived counts with the result the chain
  actually returned, and logs any disagreement (the returned result wins).

## 4. The estimate of remaining time

Labelled **UNCERTAIN** and given only where it can be grounded in observed speed:

- It uses mean fit time per (model, frequency), and only once at least five fits of that
  pair have been timed. Fits served from the cache are excluded, as are chains that will
  be served from it (the T4.8 baseline-length chains reuse the forecast-stage fits).
- Work belonging to a model that has not yet been timed is **not guessed**: it is listed
  by name with its origin count, and the estimate states what share of the remaining fits
  it covers.
- Batches run one after another; chains inside a batch run on the parallel workers. Each
  batch therefore contributes at least max(longest chain, total ÷ workers), and the figure
  is that lower bound, not a promise.
- It covers rolling fits only, not the evaluation and robustness bootstraps or tables,
  and assumes later windows cost what earlier ones did. Markov-switching fit times vary
  strongly with the window and the warm start, so treat it as an order of magnitude.

## 5. Where the time goes

The global summary and `progress.json` report mean fit time by model and the costliest
operations: full-sample fits, HLZ tests and their null-distribution simulations, DM-HLN
tests, model-confidence-set bootstraps, state-loss regressions, VAR and ARMA-GARCH fits,
with count, total and maximum time each. Inside a rolling fit the active step is reported:
which multistart of the MSAR likelihood maximization or STAR least squares is running, the
MSAR observed-information Hessian, or the STAR simulation forecast.

## 6. Options

```
python code/run_all.py                         # full run, monitored
python code/run_all.py --smoke-test            # reduced run, monitored
python code/run_all.py --log-mirror DIR        # also copy the logs to DIR (e.g. Google Drive)
python code/run_all.py --heartbeat-seconds 60 --summary-seconds 300   # the defaults
python code/run_all.py --no-monitor            # no monitor, no run_logs/ files
```

`THESIS_LOG_MIRROR` can be set instead of `--log-mirror`. The mirror receives the snapshot
whole and only the new bytes of the two logs every two minutes; an unavailable mirror is
noted in the log and never stops the run.

## 7. Google Colab

Use `colab/run_thesis_colab.ipynb`. It mounts Drive, installs the locked dependencies,
verifies the frozen data, starts the run in the background with `nohup` (so a browser
disconnect does not stop it) and `--log-mirror` to Drive, and has a cell that streams the
live console log and prints the snapshot every five minutes; re-run it to reattach. Its
console log is written to `/content/`, outside the clone, because an untracked file in the
repository would make the clean-tree safeguard refuse the baseline run.

## 8. Guarantees and limits

- **No influence on results.** The monitor reads values the calculation has already
  produced. Tests assert identical forecasts, fit records and failures with and without it
  (serially, on four workers, and with the `spawn` start method Windows uses), and that
  every research output of a full reduced pipeline run is identical when compared with
  `code/tools/compare_runs.py`, which excludes only the provenance columns, elapsed-time
  columns and run manifests.
- **Cache invalidation.** Monitoring touched `forecasting/rolling.py` and the MSAR and
  STAR estimator modules (one reporting call each), which are in the fit cache's
  dependency hash. Fits cached by earlier code are therefore refitted once. The numbers do
  not change; only the first run is not served from an old cache.
- **Optimizer substeps.** The active multistart and the Hessian are reported; the
  iteration *inside* one `scipy.optimize.minimize` call is not, because that would mean
  passing a callback into the optimizer.
- **Process-level liveness.** A worker reports CPU time every 30 s from a background
  thread. A worker killed by the operating system stops reporting; the heartbeat then
  shows its last signal ageing.
