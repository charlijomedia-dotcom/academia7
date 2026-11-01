# Fit-cache completeness: findings and pre-execution plan (Part 8 correction phase)

- **Date:** 2 November 2026.
- **Branch:** `part8-corrections`.
- **Status:** no Colab run launched; nothing estimated; `output/` unchanged.

**What I could and could not inspect.** This environment has no access to your Google Drive or to any Colab runtime. Everything about Drive below is derived from the notebook and backup code that ran the production session, together with the facts you reported:

- 143 parts in the KillyPhD `fit_cache/3413465b508bb844/`;
- `backup.log` ending 30 Oct 14:39 UTC;
- the production run from 30 Oct 17:30 to 31 Oct 02:34 UTC;
- `progress.json`: 67,223 origins, of which 34,300 were fitted and 32,923 served from the cache.

Where a fact can only be established on Drive, I name the exact check and supply a read-only tool for it.

## 1. Where the production run's fits went

**What the code establishes.** The notebook used by the production code (commit `46a53181`) has a default `DRIVE_ROOT = /content/drive/MyDrive/thesis_part8`. For whatever `DRIVE_ROOT` the session used, with `R = DRIVE_ROOT/baseline`:

| Artifact | Location |
|---|---|
| Fits written during the run | VM local disk: `/content/work/academia7/my-thesis/cache/fits/` (`<xx>/<digest>.json`, one file per fit) |
| Fit backups | `R/fit_cache/3413465b508bb844/part-NNNNN.tar.gz` + `.json` listing |
| Output backups | `R/output_increments/46a53181e5e9/` |
| Backup log | `R/backup.log`, plus the daemon's own console on the VM: `/content/work/run/backup_console.log` |
| Results copy | `R/results/baseline-20261030T173044-949fcd76/` |

**The decisive fact.** The results copy and the backup log are written **to the same `R`** by the same session. So:

- If `results/baseline-20261030T173044-949fcd76/` is under the **KillyPhD** root while that root's `backup.log` ends at 14:39, the backup daemon **wrote nothing to Drive during the whole production run**. The 34,300 fits estimated in that run then existed only on the VM's local disk.
- If the results are under **`/content/drive/MyDrive/thesis_part8/baseline/`**, look for that root's `fit_cache/3413465b508bb844/` and `backup.log`: the production backups would be there.

**Likely mechanism of a silent backup failure.** This was found by code inspection and reproduced in a test (`test_colab_support.py::TestCacheRecoveryAndAudit::test_restored_fits_are_not_reuploaded_by_name`).

1. At start-up the notebook restored the 32,923 archived fits to the VM disk.
2. The backup daemon decides what is new by comparing each file's size and **nanosecond mtime** with the archive listing. Tar keeps less mtime precision than `st_mtime_ns`, so **every restored file looks changed** to a freshly started daemon.
3. Its first sync, about 10 minutes into the run, therefore tried to pack all 32,923 restored fits, plus everything fitted so far, into **one** archive and copy it to Drive with a single `shutil.copyfile`.
4. The daemon wrote a log line only *after* a copy finished, or on an exception. A Drive copy that stalls inside the filesystem driver raises nothing, so the daemon would hang there **silently for the rest of the run**.
5. The final notebook cell waits at most one hour for the daemon, then prints the old log tail, which would end at 14:39.

Evidence to look for on Drive:
- a leftover `part-00144.tar.gz.partial` in `fit_cache/3413465b508bb844/`, written before the rename;
- no `output_increments/46a53181e5e9/` parts after 17:30.

Other possibilities that the Drive files would distinguish:
- the daemon crashed at start-up (its traceback would be only in the VM's `backup_console.log`);
- the session used a different `DRIVE_ROOT`.

**Is the VM still there?** The run ended 31 Oct 02:34 UTC. Colab reclaims a runtime after it disconnects or idles, so the VM disk, and with it the 34,300 locally written fits, is **very probably gone**. It can be confirmed only in the Colab UI: if the original runtime is still connected, `/content/work/academia7/my-thesis/cache/fits/` still exists.

## 2. How many unique payloads are recoverable

This cannot be counted from here. The count comes from the archive listings, without extracting anything:

```
# in any Colab cell after mounting Drive (standard library only, read-only):
!python /content/work/academia7/my-thesis/colab/thesis_colab.py audit-drive \
    /content/drive/MyDrive/KillyPhD/Part8_K3_InSample_2026-10-29 \
    /content/drive/MyDrive/thesis_part8 --json /content/drive_audit.json
```

For each root, `audit-drive` reports:
- every fit-cache identity with its part count;
- the number of **unique payload names** across all part listings;
- the first and last part times;
- any `.partial` leftovers;
- the `backup.log` tail;
- the run folders under `results/`;
- the output-increment parts.

The union of listed names for identity `3413465b508bb844` is the number of unique fit payloads that can be restored.

Expectation from your numbers: about 32,923 for the KillyPhD archive, since that is what the production run restored. **That is a hypothesis to verify, not a count.**

## 3. Can every rolling fit be served from the cache?

**On present evidence, no.**
- 34,300 of the 67,223 planned rolling origins were estimated *during* the production run.
- Nothing shows they reached Drive.
- Unless the audit finds them (in `thesis_part8`, or on a still-live VM), at most about 32,923 origins can be cache hits.

A real assessment is now built in:

- **`code/tools/cache_completeness.py`** rebuilds the exact rolling plan through the pipeline's own job builders. It then walks every chain origin by origin with the rolling engine's own cache-key function, reading the cache and **estimating nothing**. Each origin is classified as one of:
  - `hit`;
  - `miss`;
  - `horizon_miss`;
  - `gap`;
  - `unknown_after_miss`.
- **`unknown_after_miss` matters.**
  - MSAR and STAR are warm-started. Each origin's cache key includes a hash of the *previous* fit's parameters.
  - After one missing fit, every later key in that chain is unknown until the missing fit is re-estimated.
  - Those later fits are served from the cache only if the refit reproduces the original **bit for bit**, which is not guaranteed on another machine (§6).
  - So one missing MSAR or STAR fit can force the rest of its chain to be refitted.
  - AR and ARMA keys do not depend on predecessors and are counted exactly.
- **Validated** on a real smoke-run cache (`cache_completeness_validation.json`; unit test `tests/unit/test_cache_completeness.py`).
  - The intact cache gives 576 of 576 hits.
  - After deleting one AR fit and one MSAR fit:
    - the AR chain shows exactly 1 miss;
    - the MSAR chain shows 1 miss plus 17 `unknown_after_miss` (the warm-start cascade);
    - their 240-window duplicates are flagged identically;
    - the exit status is 1.
- **The notebook now runs this check by default and stops** (`PREFLIGHT_ONLY = True`). It restores every archive folder for the identity, writes `cache_completeness_<identity>_<commit>.json` to Drive, and raises before `run_all.py`.
  - Even with `PREFLIGHT_ONLY = False`, the run refuses to start unless every planned origin is a hit, unless `ALLOW_PARTIAL_CACHE` is set explicitly.

## 4. Safest execution strategy if fits are missing

**Option R0 — the original VM is still alive.**
- Run the notebook's restore cell, or call `tc.recover_local_cache(...)` directly.
- It writes only the fits not already archived into a **new** folder, `R/fit_cache_recovered/<UTC stamp>/3413465b508bb844/`. **Existing parts are never modified.**
- It re-reads every new part from Drive and compares each member's SHA-256 with the local file.
- Later restores read the main folder and every recovery folder.
- Then run preflight, and the corrected run only if it reports `complete: true`.

**Option R1 (recommended if the fits are lost) — rescore published forecasts; re-estimate only what cannot be rebuilt.**
- **No estimation needed.**
  - All 14,108 baseline origins (24 chains) have their forecasts, statuses and reason codes in `output/forecasts/forecasts_*.csv`. The 240/120-window chains of T4.8 and the baseline-transformation rows of T4.1 re-read the same fits.
  - F1, F2 and F3 for T3.3–T3.6, T4.4, T4.TP1, T4.9 and the T4.8 baseline-window MCS cells can therefore be recomputed from published forecasts.
  - F4 and F7.1 need only the stationarity stage, which takes seconds.
- **Needs forecasts that were not published** (F1 or F2 changes their scores). Unless the cache has them, these require estimation:

  | Exercise | Chains | Cost |
  |---|---|---|
  | T4.2, CPI AR lags | 4 AR chains, p = 1, 3, 6, 12 | cheap OLS |
  | T4.1, UNRATE in differences | 4 chains (AR, ARMA, MSAR, STAR) | 2 of them MSAR/STAR |
  | T4.1, FEDFUNDS in levels | 4 chains | 2 of them MSAR/STAR |
  | T4.8, UNRATE at 180 and 300 months | 8 chains | 4 of them MSAR/STAR |

  In total: **8 MSAR/STAR chains, about 5,400 origins**, plus cheap AR and ARMA, instead of 34,300 fits.
- **Caveats**
  - Re-estimated MSAR/STAR rows may differ numerically from the published ones, because of the platform sensitivity in §6. Those rows must be labelled *re-estimated*, not *corrected*, and their differences reported.
  - R1 needs a new, tested "rescore from published forecasts" path. Its acceptance test: with corrections switched off, rescoring must reproduce the published T3.3–T3.6, T4.4 and T4.TP1 exactly.
  - **R1 is not implemented.** It is a proposal for your decision.

**Option R2, not recommended — a full run that lets the cache be partial.**
- It re-estimates about 34,300 fits (comparable to the production run's 9 hours), plus warm-start cascades.
- Every re-estimated MSAR/STAR fit can differ from the published value (§6), so the "unexpected change" check would flag many tables that the corrections do not touch. That mixes correction with re-estimation noise.

## 5. Notebook configuration on `part8-corrections`

| Setting | Value |
|---|---|
| `BRANCH` | `part8-corrections` |
| `DRIVE_ROOT` | `/content/drive/MyDrive/KillyPhD/Part8_K3_InSample_2026-10-29` (quotes and whitespace stripped; must be under `/content/drive/`; also checked with `thesis_colab.clean_drive_root`) |
| `RESULTS_BRANCH_PREFIX` | `part8-corrected-results` (cannot reach `part8-results/`) |
| `PREFLIGHT_ONLY` | `True`: restore, audit, completeness report, stop |
| `ALLOW_PARTIAL_CACHE` | `False` |
| `RESTORE_CACHE` | `True`: main folder plus every `fit_cache_recovered/*/<identity>` folder |
| Backup daemon | fit cache archived **by name** (restored fits never re-uploaded); parts capped at 2,000 files; a log line before every part, after every part and on every idle check; a start-up line |

None of these changes touches the fit-cache identity. The notebook, `thesis_colab.py`, `tools/` and `pipeline.py` are not in `_FIT_CRITICAL`, and no configuration file changed. Identity `3413465b508bb844` is re-verified in `cache_compatibility_check.json`.

## 6. Remaining risk of changing unaffected numerical results

1. **Full-sample MSAR fits (T3.1, T3.2, T4.3) are re-estimated by every run.** They are not cached. The F6 study found that a different platform reaches different MSAR optima for INDPRO, M2SL and UNRATE. Even on Colab, a different CPU or BLAS kernel assignment could do the same. **Any corrected run must be compared table by table** with `tools/compare_runs.py`. A difference in T3.1, T3.2 or T4.3 is a reproducibility finding to investigate, not something to accept silently.
2. **Re-estimated rolling fits**, under R1 or R2, can differ for the same reason.
3. **ARMA-GARCH and the VAR** are re-estimated; they are cheap but not cached. Their numerical identity must likewise be shown by comparison, not assumed.
4. **Deterministic re-scoring** (HLZ critical values, MCS bootstrap, state regressions) uses fixed seeds and is expected to be identical. The comparison will show it.

## 7. Tests at the pre-execution head

The full suite passes: **900 passed, 0 failed** (36 min, this container). It includes:

- the new completeness-walker tests;
- the recovery, by-name backup, Drive-path and notebook-gate tests;
- the F7.1 test;
- all earlier correction and cache-fidelity tests.
