# R1: real-cache replay (approved), Tier A gate, and the Tier B execution plan

Date: 2 November 2026. These are the user's decisions of the same day:

- Step 1, the cache replay, is **approved**, with no new estimation.
- Tier A is **approved in principle**, to run after the replay and only for AR chains the cache cannot replay.
- Tier B is **not approved**.

Part 9 is not started.

| | |
|---|---|
| Code | branch `part8-r1-rescore`, commit `8aaa4217536ab3cb942dd248dd19ece7838a8d60` (pinned in the notebook) |
| Notebook | `colab/r1_cache_replay.ipynb` on branch `part8-r1-rescore`, commit `ce98dbb` or later |
| Cache | identity `3413465b508bb844` (the same code hash, config hash and data hash as the original run; checked when the notebook starts) |

## 1. Guarantee: the replay cannot estimate anything

There are three layers, and each one is tested.

1. **Engine level** (`rescore._replay_from_cache`).
   - During a replay, `rolling.fit_and_forecast` is replaced by a function that raises.
   - `run_chain` does not catch exceptions from the fit call (verified in `forecasting/rolling.py`). So the first missing or narrower-horizon payload aborts the replay of that chain, and the chain becomes *unavailable*.
   - Nothing from a partly replayed chain is used.
   - The cache is read through a read-only view. That view rejects any payload carrying the R1 refit marker and refuses writes.
2. **Workflow level** (`correction/guard.py`). `workflow.run()` executes inside `estimation_forbidden()`.
   - That function replaces every estimation entry point in every loaded `thesis` module: `fit_ar`, `fit_arma`, `fit_msar`, `fit_star`, `fit_var`, `fit_arma_garch` and `fit_and_forecast`.
   - Any estimation outside an `--approve`d chain raises `EstimationForbidden` and stops the run.
   - The run summary records `estimations_performed`.
   - The notebook asserts that this is empty after every step.
3. **Procedure level** (the notebook).
   - The R1 runs are built by a function that asserts `--approve` is absent.
   - Only the Tier A cell, gated by `RUN_TIER_A = False`, can approve anything.

**Evidence.**

- `tests/integration/test_r1_replay.py` (8 tests, on synthetic chains):
  - a complete chain replays whole, with no estimator call;
  - one deleted payload makes the chain unavailable, with no estimator call and no cache write;
  - a refit-marked payload in the original cache is rejected;
  - a warm-started STAR chain with a missing payload reports 1 hit, 1 miss and 3 unknown origins;
  - the guard blocks every estimator.
- `tests/unit/test_r1_correction.py::test_legacy_mode_reproduces_published_tables` runs the whole workflow on the published release under the guard. It passed, so the workflow calls no estimator anywhere.
- **End-to-end on the real data.** I built a test cache holding only the four T4.2 AR chains. This was a fixture in my scratch space, never published. The replay report then classified those 4 chains as complete and verified their replay (715 of 715 origins each), and the other 16 as not replayable.
  - The legacy run with `--cache-root` then took T4.2 from the cache, with `estimations_performed` empty.
  - It reproduced the published T4.2 to within 1.2e-14 relative, and the other 90 files as in the original gate (92 files: 81 identical, 11 within tolerance, 0 different).

## 2. The Colab procedure (step 1: no estimation)

Open `colab/r1_cache_replay.ipynb` in Colab, choose a CPU High-RAM runtime, and select **Run all**. Defaults: `PIN_COMMIT = 8aaa421…`, `RUN_TIER_A = False`, and `DRIVE_ROOT` as in the main notebook.

| Step | What happens | Writes |
|---|---|---|
| 1 | Mount Drive and read the `GITHUB_TOKEN` secret (askpass only, never in a URL) | a new folder `DRIVE_ROOT/r1_replay/<UTC stamp>/` |
| 2 | Clone `part8-r1-rescore` and run `git checkout --detach PIN_COMMIT`; assert HEAD equals the pin and `git status --porcelain` is empty | VM local disk only |
| 3 | Build the approved Python 3.11 environment from the lock, and run `run_all.py --data-only` to verify the frozen data | VM |
| 4 | Assert the cache identity of the pinned code is `3413465b508bb844`. Restore every archive folder for that identity (main plus recoveries) into `/content/r1work/r1_cache/fits`, outside the repository. Count the unique payloads (18,964 expected; any difference is reported). No backup daemon runs, and nothing is written to `fit_cache/` | VM; `restore.json` |
| 5 | `tools/r1_cache_replay_report.py`: walk every key of the 20 pending chains, then replay each chain classified complete through the real rolling engine with estimation disabled | `replay_report.json` and `.csv` |
| 6 | R1 legacy run with `--cache-root` (the validation gate, which now also covers every replayed T4.1, T4.2 and T4.8 chain); then the corrected run with `--legacy-staging` and `--release`. No `--approve` | VM; summaries, comparisons and release manifests to the evidence folder |
| 7 | Tier A: skipped by default | — |
| 8 | Push the evidence to a **new** branch `part8-r1-replay/<stamp>`, and the replay-based release to a **new** branch `part8-corrected-results/r1-replay-<stamp>` | new branches only |

**Not modified:**

- the original `output/`;
- the original results branch `part8-results/baseline-20261030T173044-949fcd76` (`0662945`);
- the provisional release `part8-corrected-results/r1-20261101` (`0573a8c`);
- the Drive `fit_cache/` and `fit_cache_recovered/` folders.

**Reported per pending chain** (`replay_report.csv`):

- task ID, exercise, series, model, specification, transformation, window length and horizons;
- `planned_origins`;
- `hit`, `miss`, `horizon_miss`, `unknown_after_miss` (MSAR and STAR, after the first miss), `refit_rejected` and `gap`;
- `complete_in_cache`, and `replay_verified` from the real engine;
- `origins_to_estimate_whole_chain`: under the approved no-mixing rule, an incomplete chain is re-estimated whole;
- `origins_missing_exact_keys`, for AR and ARMA, for information only;
- `mean_seconds_per_fit` and `cpu_hours_residual`.

**Totals** (`replay_report.json`):

- residual chains, origins and CPU hours, and the longest remaining chain;
- the residual split by model;
- the Tier A list (AR chains not replayable) and the Tier B list.

**Worst case.** If the cache holds none of the 20 chains, the report gives 13,808 origins and 57.35 CPU hours, with the longest chain 13.7 hours (UNRATE MSAR, 180-month window). This was checked against an empty cache here. The real figures are those the notebook writes; I cannot run against the Drive cache from this container.

## 3. Tier A (approved in principle; runs only after the replay is reviewed)

Set `RUN_TIER_A = True` and run the Tier A cell (or Run all again). The cell:

1. Takes the AR chains from `tier_a_ar_chains_to_estimate`, so complete cached chains are never refitted.
2. Validates the AR estimator in legacy mode (`tools/r1_validate_ar_refit.py`):
   - it re-estimates the six published baseline AR chains, for validation only, and requires every forecast and status to match the published `forecasts_*.parquet` within 1e-9 relative;
   - it compares each Tier A refit, origin by origin, with every original cache payload at the same exact key (AR keys carry no warm start).
   If validation fails, nothing re-estimated is used.
3. Runs R1 with `--approve` for exactly those chains:
   - checkpointing in a separate refit cache, where every payload carries `r1_provenance: re-estimated`;
   - first in legacy mode, where any T4.2 file the re-estimated chains feed must reproduce the original within tolerance;
   - then in corrected mode.
   The re-estimated chains are labelled `re-estimated` in `chain_sources` and in the forecast frames.

**What Tier A alone resolves.**

- T4.2 is resolved completely.
- For T4.1 and T4.8 UNRATE (180 and 300 months), each exercise is all-or-nothing per series. They stay *pending* until their ARMA, MSAR and STAR chains are replayed or approved under Tier B. A re-estimated AR chain is never combined with original competitor rows.

## 4. Tier B: how it would run (not approved; nothing launched)

The residual Tier B workload is the `tier_b_chains_to_estimate` list and its CPU hours in the replay report. At worst that is 12 chains, about 57.3 CPU hours, with the longest chain 13.7 hours.

**Sequential limit.** MSAR and STAR chains are warm-started: each origin starts from the previous fit. So a chain cannot be split across workers, and its CPU time is its wall-clock time. With at least as many workers as remaining chains, the wall-clock time equals the longest remaining chain. The worst case is about 14 hours, plus Colab's per-fit speed difference.

**Execution plan (to implement only after approval):**

1. **Parallel prefill of the refit cache.** A small tool, `tools/r1_refit_chains.py`, would run each approved chain as its own worker process, longest first. Each worker calls `rolling.run_chain` with `cache=RefitCache(...)` inside `guard.allowed()`. On an 8-vCPU High-RAM runtime with 8 workers, that is a single wave whose length is the longest chain.
2. **Checkpoints.** Every origin's fit is written to the refit cache as soon as it is estimated (`FitCache.put` is atomic: a temporary file, then a rename). A resumed chain re-reads its own completed origins and continues from the last one, with the warm start taken from the cached payload. This is the same mechanism the original run used, and `test_refit_cache_resumes_an_interrupted_chain` covers it.
3. **Backups.** The existing `thesis_colab.py backup-daemon` (`--pair-by-name`, parts of at most 2,000 files, each logged) would back up the refit cache every 10 minutes to a **separate** Drive folder, `DRIVE_ROOT/r1_refit_cache/<identity>/`. It would never touch `fit_cache/`. Restored files are recognised by name, so they are never uploaded again; the intermittent test failure below concerned the other, timestamp-based rule.
4. **Session limits.** If the Colab session ends (Pro+ background execution is up to about 24 hours; disconnects can happen sooner), Run all again. The notebook restores the original cache (read only) and the refit cache from its own Drive folder, and the chains resume, losing at most about 10 minutes of fits per chain.
5. **Assembly.** When the refit cache holds every approved chain, the R1 workflow is run with `--approve` for exactly those chains and `--refit-cache` (legacy, then corrected). Every origin is then a refit-cache hit. Every re-estimated chain is labelled, never mixed with original fits within a chain, and never combined with original rows within an exercise.
6. **Provenance and F6.**
   - Re-estimated MSAR and STAR chains depend on the platform. Under F6 they will not be bit-identical to the Colab originals.
   - Their tables are reported as re-estimates, with the run ID, commit and refit-cache inventory (sha256).
   - The original chains that the cache does replay remain original estimates.
   - The multistart specification is unchanged.

## 5. Other items requested on 2 November

- **`code_tree_dirty: true` in `0573a8c`.**
  - The corrected run started at 15:22:13Z from commit `77df9d8`, while two untracked report files were in the repository: `reports/part8/corrections/r1/estimation_workload.py` and its CSV, written at 15:18:38 and 15:18:41.
  - The legacy run started at 15:17:30Z and recorded `false`.
  - Neither file is an input to the workflow, and no code, configuration or data file was uncommitted.
  - The workflow now records the exact uncommitted paths at start, and refuses `--release` and `--legacy-staging` unless the tree is clean and the legacy tree comes from the same commit.
  - The release has been regenerated from a clean worktree of commit `8aaa421`; see `clean_regeneration.md`.
- **The intermittent `test_restored_fits_are_not_reuploaded_by_name` failure.**
  - Root cause: `tarfile` (PAX format) stores each file's mtime as a float, to about 1e-7 s. A restored file's `st_mtime_ns` therefore lands within a few hundred nanoseconds of the original, and is exactly equal about 1 time in 300 per file (measured: 1 in 300).
  - The test assumed that every restored file looks changed under the timestamp-based signature rule. With 7 files, that assumption failed in roughly 1 run in 40.
  - A first fix (moving each mtime by 1 ns) still failed 2 times in 40, because the round trip can land exactly 1 ns below the original. The final fix moves restored mtimes by 1 ms, and passed 100 runs out of 100.
  - The archive code is unchanged. The fit cache is backed up by name, which never consults mtimes, so backups of fits were not affected. Under the signature rule, an exact round trip only means an unchanged file is not uploaded again, which is correct.
- **Visual review of the corrected figures.** I reviewed the PNGs of the provisional release. See `figure_review.md`.
- **Multiplicity.** See `multiplicity_unrate_star.md`.

## 6. Test suite at `fba98d3`

The full suite (`pytest -m "not network"`, slow tests included) gave **924 passed, 0 failed** in 41.5 minutes. That includes 12 new tests: 8 for the replay path and 4 for the notebook. The 14 warnings are the known statsmodels warnings from the T3.5 state regression.
