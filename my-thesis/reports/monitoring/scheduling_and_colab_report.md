# Shared-pool scheduling and the Colab Pro+ notebook — report

Branch `claude/parallel-scheduling-colab`, based on `4137128` (the approved monitoring
work). Final commit: FINAL_SHA. Part 8 was not started.

No approved specification, window, horizon, forecast origin, estimator, optimizer
setting, seed, replication count, test or output definition was changed. One
implementation defect found during validation was corrected under CLAUDE.md §6A
(section 4).

## 1. Scheduling

### What was wrong

Each `_chains` call made its own worker pool. The forecast stage launched one series at a
time (its AR, ARMA, MSAR, STAR and K=3 MSAR chains) and started the next series only when
the slowest chain of the batch, always the K=3 MSAR, had finished. Every T4.1, T4.2 and
T4.8 batch did the same. With four workers, three sat idle behind each K=3 chain, and the
five monthly K=3 chains (7–9 hours each in the full run) ran essentially one after
another.

### What replaced it (`code/src/thesis/forecasting/scheduler.py`)

* **One pool for every rolling chain of the run.** All 114 pooled chains (baseline AR,
  ARMA, MSAR, STAR; rolling K=3 MSAR for T4.3; T4.1; T4.2; T4.8) are submitted as soon as
  the specification stage has fixed them: before the full-sample adequacy fits, which now
  overlap with the rolling computation instead of leaving the workers idle.
* **Most expensive first.** A dispatcher keeps exactly `workers` chains running and
  always starts the most expensive ready chain (origins × a relative cost per model:
  K=3 MSAR ≫ MSAR ≫ STAR ≫ ARMA ≫ AR). Ordering cannot change a number; it only shortens
  the run.
* **Cache reuse preserved exactly.** A chain the sequential design serves from the fit
  cache, because an identical chain ran earlier for a superset of horizons (the T4.8
  baseline-length chains), is started only after that chain has finished, so it is
  still served from the cache: same results, same workload, same cache-hit counts.
* **Consumption order preserved.** Each stage still collects its chains' results in its
  original order, so the fit records, failure registry, data-gap register and every
  table are appended exactly as before.
* **Unchanged by construction.** A chain still runs start to finish in one worker, in
  chronological origin order, so warm starts and their cache keys are as before; seeds
  derive from series, model, specification and origin.
* **Failures and interruption.** A chain that raises does so where the stage consumes
  it, as before; a chain depending on it is not run and says why. On an error or
  interrupt the pool is terminated rather than waited for.
* `--workers N` sets the number of processes without changing the configuration hash or
  the fit cache key; `--workers 1` runs everything in one process in the original order.

**Robustness exercises investigated.** T4.1, T4.2 and T4.8 had the same per-batch idling
and now share the pool. T4.5 (VAR) and T4.6 (ARMA-GARCH) remain serial loops in the main
process: they are cheap per fit, and they now run while the pool is still computing T4.8
chains, so they no longer leave workers idle. The full-sample adequacy fits also overlap
with the pool.

### Monitoring kept consistent

The plan marks pooled chains as one batch (`pool`), so the remaining-time estimate is
max(longest remaining chain, total remaining ÷ workers). The heartbeat shows
`Batch pool: N done, 4 active, M queued` and each worker's exercise, because a worker may
be on a robustness chain while the banner shows an earlier stage. Each chain's returned
result is reconciled with its progress events once its end event has arrived. A
`scheduler_summary` event records workers, wall time, busy time and utilization. The
counters match the computed results exactly in every test and run (sections 3 and 5).

## 2. Measured scheduling improvement

`code/tools/benchmark_scheduling.py`: the real rolling workload (all six frozen series,
approved windows, horizons and specifications; all 114 pooled chains), with origins
capped at 6 per chain and the same cap in both arms, four workers, cold caches, nothing
else running on the machine:

| | per-batch pools (before) | shared pool (after) |
|---|---:|---:|
| Wall time | 2,736 s | 1,910 s |
| Worker utilization | 39.4% | 90.2% |
| Busy chain-time | 4,310 s | 6,886 s |
| Results | — | **identical**: 114 chains, 849 forecast rows, all parameters, statuses and counts |

**1.43× faster** here. Busy chain-time rose because a fit runs slower when all four
workers are busy (in the "before" arm the K=3 chains mostly ran alone): K=3 MSAR busy time
went from 1,782 s to 3,479 s, and MSAR from 1,935 s to 2,785 s. This machine's four
virtual CPUs evidently share physical resources, so the wall-time gain is smaller than
the utilization gain.

**What it means for the full run.** With 6 origins per chain the K=3 chains are short, so
the old design's waste is understated. In the full run each monthly K=3 chain has
571–715 origins (7–9 hours at the measured speed) and the old design ran them one after
another (≈ 40 hours); the shared pool runs them concurrently with everything else, so the
rolling stage is bounded below by the longest single chain (≈ 9 hours) and by total work ÷
four. How close the run comes to that depends on Colab's CPUs: cell 1 of the notebook
prints the CPU count. If the runtime offers more than four virtual CPUs, four workers will
contend less than they did here. These are projections from measured per-fit speeds, not
measurements of the full run.

## 3. Numerical reproducibility

| Comparison | Scope | Result |
|---|---|---|
| Shared pool (4 workers) vs serial vs old per-batch pools | synthetic data; AR, ARMA, MSAR, **MSAR3**, **STAR** (incl. simulated multi-step) and a cache-served chain (`test_scheduler.py`) | identical forecasts, parameters, statuses, starts used, counts |
| Shared pool vs old per-batch pools | all six frozen series, all 114 pooled chains (benchmark) | identical: 849 forecast rows, all fits |
| Sequential (1 process, no monitor) vs shared pool (4 workers, monitored) | full reduced pipeline on the frozen data (`test_monitoring_pipeline.py`) | identical outputs and checkpoints |
| SERIAL_SMOKE_ROW |
| RECOVERY_ROW |

`code/tools/compare_runs.py` compares every table cell by cell, every figure byte for
byte, every sidecar and checkpoint. It excludes only run metadata: provenance columns
(run ID, timestamp, commit, configuration hash), elapsed times, the cache-read counts
(`origins_from_cache`), the run manifests and the machine record
(`logs/environment.json`).

## 4. Correction found by the recovery test (CLAUDE.md §6A)

A fit read back from the fit cache had kept its numbers but lost the rest of its record:
standard errors, optimizer message, the diagnostics behind each credibility flag and the
estimator label. The first recovery test showed it. All forecasts, parameters, test
tables and figures of the resumed run matched, but 28 fit records and 56 failure-registry
`raw_diagnostic` entries were blank for the restored fits.

This predated this work. It affected every run's T4.8 baseline-length chains, which are
cache-served by design, identically in every run, so it had never shown as a difference.
The cache payload now stores the complete record, encoded so that every value prints
identically. `test_cache_fidelity.py` asserts that wholly and partly cache-served chains
report exactly what a fresh estimation reports. Details are in
`notes/claude/correction_2026-10-27_cache_record_fidelity.md`. Effect on outputs: those
fields are now filled for cache-served fits. No number changes.

## 5. The Colab notebook (`colab/run_thesis_colab.ipynb`)

Open it, choose a High-RAM CPU runtime, **Runtime → Run all**. No editing; the settings
form defaults to the full baseline with four workers.

| Requirement | How |
|---|---|
| 1. Isolated Python 3.11, exact lock | `uv` installs a standalone CPython 3.11 and a fresh virtual environment outside the clone; it installs `requirements.lock.txt` with `requirements.constraints.txt`, then verifies the interpreter version and every pinned version exactly, and saves the full package list to Drive |
| 2. Four workers | `--workers 4` (form default); cell 1 prints the CPU count and warns if lower |
| 3. Local filesystem | Clone, environment, cache, outputs and logs all live under `/content/work` |
| 4. Live monitor output | Cell 7 streams the complete console until the run ends; re-run it to reattach after a disconnect |
| 5. Logs mirrored to Drive | `--log-mirror` (every two minutes) |
| 6. Incremental cache backups | A background process packs only new or changed fit files into one compressed increment every `BACKUP_MINUTES` (default 10), plus a small listing, so Drive receives one file per interval instead of thousands |
| 7. Restore and resume | The cache is stored under an identity = hash(code, configuration, frozen data). After a termination, Run all restores the matching increments only, and the pipeline recomputes what is missing; restored fits are identical (section 4) |
| 8. Frozen data and provenance | `--data-only` hash check before starting, a second hash check after finishing; the clone stays clean (nothing is written into it except ignored directories), so the clean-tree safeguard admits the baseline run |
| 9. Results to Drive | Outputs are backed up incrementally during the run; at the end they are verified and copied in full, with the run's logs, to `results/<run_id>/` |
| 10. Optional GitHub push | After successful verification only, the outputs are committed to `part8-results/<run_id>` and pushed. The token comes from the Colab secret `GITHUB_TOKEN`, is passed to git via `GIT_ASKPASS` from an environment variable, and never appears in a URL, `.git/config`, a command line or the notebook. A URL with credentials is refused, and the analysis process never receives the token |

Verification before publication (`thesis_colab.verify_outputs`): every file in the run's
output inventory exists with its recorded SHA-256; the run summary lists all ten stages;
the progress snapshot says `complete`; nothing outside `output/` changed in the working
tree; the frozen input's hash is unchanged.

**Transitive dependencies.** The approved lock pins the 13 packages the pipeline imports,
not their dependencies. A fresh install on 2026-10-27 resolved 11 of those to newer
versions than the environment every result was produced in, including python-dateutil
(pandas date parsing) and pillow and fonttools (figure files). The new
`code/requirements.constraints.txt` holds them at the validated versions, so the Colab
environment is identical to the validated one (33 of 33 packages; verified). It changes
no version in the approved lock. The notebook's `USE_CONSTRAINTS` setting turns it off,
but leaving it on is recommended.

### How the notebook was verified

Executed end to end outside Colab, unedited, by `nb_harness.py` (kept with the session
evidence, not in the repository). The harness replaces only the Colab services:
`google.colab` by a stand-in, Drive by a local directory, GitHub by a local bare
repository. It selects the reduced run through the settings form.

* **Run 1:** environment built (Python 3.11.15, 33 packages verified), frozen data
  verified, run started with four workers and backups every minute. Once two cache
  increments were on "Drive", the run and the backup process were killed (a runtime
  termination). The mirrored `progress.json` on "Drive" showed the stage and each
  worker's series, model, origin and active optimizer start at that moment.
* **Run 2, on a fresh "VM"** (local work directory deleted): Run all restored the
  backed-up fits for the matching identity, completed the run, made the final backup,
  verified all inventory files and the frozen hash, copied the results to "Drive", and
  correctly declined to push reduced results. RECOVERY_DETAIL

The push path is tested against a local bare repository (`test_colab_support.py`):
branch created, only `output/` committed, token absent from `.git/config`, credentialed
URLs and files over GitHub's 100 MB limit refused. **Not done from here:** a run on an
actual Colab runtime, and a push to github.com with a real token.

## 6. Tests

SUITE_RESULT

## 7. Remaining bottlenecks

* **The K=3 MSAR chains** set the floor: the longest (CPIAUCSL and INDPRO, 715 origins)
  takes ≈ 9 hours at the measured speed, whatever the scheduling, because a chain's
  origins are sequential (warm starts). Shortening it would mean changing the
  multistart, tolerance or warm-start design, which this work does not do.
* **CPU contention**: per-fit time rises when all workers are busy (section 2). More
  workers than physical cores would not help.
* **Serial parts in the main process**: the full-sample adequacy fits (the INDPRO K=3
  full-sample fit took 4 minutes in the reduced run), the evaluation bootstraps (50,000
  HLZ and 5,000 MCS replications in the full configuration) and the ARMA-GARCH loop.
  They now overlap with the pool, but their own time is not parallelized.
* **Colab session limits**: a Pro+ session can end before the run does. The notebook's
  backups make that a pause rather than a loss.
