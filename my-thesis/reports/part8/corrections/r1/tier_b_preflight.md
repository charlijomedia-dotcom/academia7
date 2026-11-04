# R1 Tier B: execution preflight (design for review; nothing executed)

Date: 3 November 2026.

> **Superseded in part (4 November 2026).** The single-notebook execution design here is replaced by three independent batch notebooks; see `tier_b_batches.md`. The workload analysis and gate definitions below still apply.

- **Status:** a proposal. Tier B is **not** authorised, and nothing here estimates, publishes or changes methodology.
- **Inputs read:**
  - `my-thesis/CLAUDE.md`;
  - Part 5: §7.5 adequacy, §9.4 windows, §10 inference, §13 figures, and the computational specification;
  - `r1_cache_replay_procedure.md`, `tier_a_review.md`;
  - the evidence branch `part8-r1-replay/20261103T063749Z` (`c5324b2`);
  - the release branch `part8-corrected-results/r1-tier-a-20261103T063749Z` (`292227e`).

## 0. Verified starting point

| Item | Evidence | Result |
|---|---|---|
| Scientific code | `restore.json`, release `correction_run_manifest.json` | `8aaa4217536a…`, clean tree, cache identity `3413465b508bb844` |
| Original cache | `restore.json` | 18,964 unique payloads (= expected) |
| Replay | `replay_report.json` | 20 pending chains: 3 replayed whole from cache, 8 AR (Tier A), 9 non-AR (Tier B); `estimations_performed`: none |
| Tier A AR validation | `tier_a_validation/ar_refit_validation.json` | `ok: true`. Six baseline AR chains match the published forecasts, maximum relative difference 0.0 (13,817 rows) |
| Tier A failed fits | the same file | 2, 71, 0, 0, 0, 1, 1, 1 = **76**, exactly as predicted from the original T4.7 registry (`tier_a_review.md` §2) |
| Tier A release | `publication_plan.json`, `r1_tier_a_summary.json` | `correction-20261103T073809-949fcd76`. Sources: 48 published, 17 cache, 8 re-estimated, 35 unavailable. The corrected pass estimated nothing (it read the refit cache) |
| **Tier A refit cache** | the Tier A notebook cell | **Written only to the VM's local disk (`/content/r1work/refit_cache`). Not on Drive.** See §7 |

## 1. The nine Tier B chains and their workload

`tier_b_workload.py` produces `tier_b_workload.csv`. The costs are the **original run's own per-origin wall times for these exact chains** (`models/fit_records.parquet`; Colab, 4 concurrent workers). They are more accurate than the replay report's estimate, which averaged over all window lengths. The chain records were identified by series, model and window span. The original failure counts they give match the published T4.1 and T4.8 audits, which confirms the identification.

| Task | Specification | Data | Origins | Original failed fits | CPU-h (measured) | Replay estimate | Original-cache hits before first miss |
|---|---|---|---|---|---|---|---|
| T4.8:UNRATE\|300:MSAR | MSAR(p=4,K=2) | level, 300 m | 644 | 3 | **17.88** | 11.52 | 454 |
| T4.8:UNRATE\|180:MSAR | MSAR(p=4,K=2) | level, 180 m | 764 | 5 | 12.52 | 13.67 | 229 |
| T4.8:UNRATE\|180:ARMA | ARMA(3,4) | level, 180 m | 764 | 22 | 6.45 | 5.85 | 0 |
| T4.1:UNRATE\|ARMA | ARMA(3,4) | difference, 240 m | 703 | 7 | 6.27 | 5.38 | 0 |
| T4.1:FEDFUNDS\|MSAR | MSAR(p=1,K=2) | level, 240 m | 626 | 52 | 3.41 | 2.01 | 2 |
| T4.8:UNRATE\|300:ARMA | ARMA(3,4) | level, 300 m | 644 | 13 | 2.17 | 4.93 | 0 |
| T4.8:UNRATE\|300:STAR | STAR(LSTAR,p=4,d=1) | level, 300 m | 644 | 0 | 0.36 | 0.34 | 155 |
| T4.1:FEDFUNDS\|STAR | STAR(ESTAR,p=1,d=1) | level, 240 m | 626 | 0 | 0.32 | 0.26 | 0 |
| T4.1:FEDFUNDS\|ARMA | ARMA(1,0) | level, 240 m | 626 | 6 | 0.05 | 0.03 | 0 |
| **Total** | | | **6,041** | 108 | **49.4** | 44.0 | |

**CPU-hours versus wall-clock time.**

- The 49.4 CPU-hours is the sum of fit times.
- MSAR and STAR chains are warm-started: each origin starts from the previous fit and its cache key contains the previous fit's parameters. So a chain is sequential and cannot be split across workers.
- Wall-clock time is therefore bounded below by the longest chain, **17.9 h** (T4.8 UNRATE 300-month MSAR).

Longest-first scheduling of whole chains:

| Workers | Wall-clock |
|---|---|
| 1 | 49.4 h |
| 2 | 24.8 h |
| 3 or more | **17.9 h** |

**Recommendation:** 4 worker processes on a High-RAM CPU runtime. Add margin for restore and assembly (about 1 h) and for platform speed (±30%). The run will very likely **exceed one Colab session**, so the procedure must survive at least one interruption.

**Prefix-reuse alternative (not recommended; needs your explicit decision).**

- For four chains, the original cache holds the leading origins before the first miss: 454, 229, 155 and 2 origins.
- Reusing those original fits and re-estimating only from the first miss onwards would cut the cost to 35.7 CPU-h, with the longest chain 8.7 h.
- It would mix original and re-estimated fits **within one chain**, which breaks the R1 rule you set ("a chain is never mixed"). The design below keeps the whole-chain rule.

## 2. Design principles

1. **No scientific-code change.** Tier B runs entirely on the pinned commit `8aaa421`, using its existing tools.
   - `tools/correct_from_published.py` with `--approve <task>` and `--refit-cache <dir>`.
   - At `8aaa421` this path already: re-estimates an approved chain whole with `rolling.run_chain`; writes every origin's fit to a **separate** `RefitCache`, where each payload carries `r1_provenance: "re-estimated"` and is written atomically (temporary file, then rename); runs inside `guard.allowed()`, so `estimations_performed` is counted; never reads the original cache for an approved chain; and the read-only view of the original cache rejects refit-marked payloads.
   - Only the orchestration is new, and it lives in a new notebook under `colab/`, which is not scientific code.
2. **Whole chains, one task per worker process.**
   - Each worker runs `correct_from_published.py --approve <one Tier B task>` against the shared refit cache. Distinct chains have distinct keys, and writes are atomic, so the workers never conflict.
   - In the workflow at `8aaa421`, `_chains` finishes estimating an approved job before it reports the exercise's other chains as unavailable. A worker run therefore fills that chain's checkpoints and then completes normally, keeping its exercise pending.
   - **Each worker gets its own cache root**, because `<cache-root>/checkpoints` is written by the pipeline. Each root's `fits/` is a symbolic link to the shared, read-only original-cache copy. The refit cache is shared.
   - Each worker is pinned to single-threaded BLAS (`OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS` = 1), as in the original parallel runner, so the summation order matches the original run's workers.
3. **Assembly estimates nothing.** Once all nine chains are complete in the refit cache, the legacy and corrected assembly passes run with `--approve` for all 17 chains (8 Tier A + 9 Tier B). Every origin is then a refit-cache hit, and the gate requires `estimations_performed == {}`.
4. **Nothing existing is written.** This covers:
   - the original results, `output/` and the frozen data;
   - the Drive `fit_cache/` and `fit_cache_recovered/` folders;
   - the earlier releases (`0573a8c`, `3bd24c4`, `292227e`) and the Tier A evidence (`c5324b2`).
   All new artefacts go to new folders and new branches, and publication is a dry run unless confirmed.

## 3. Checkpoint layout

```
VM local disk (/content/r1work_tierb/)
  academia7/                     clean detached checkout of 8aaa421 (+ notebook branch files)
  venv311/                       approved lock environment
  original_cache/fits/           18,964 original payloads (restored, read only)
  roots/<task>/fits -> ../../original_cache/fits     one cache root per worker (checkpoints/)
  refit_cache/fits/              SHARED refit checkpoint store (Tier A AR + Tier B), marked
  staging/<task>/                each worker's staging tree (discarded; logs kept)
  logs/<task>.log, progress.json supervisor and per-chain progress
  assembly/{legacy,corrected,release}/   final passes (no estimation)

Google Drive (DRIVE_ROOT/)
  baseline/fit_cache/3413465b508bb844/          ORIGINAL cache  (read only; never written)
  r1_refit_cache/3413465b508bb844/
      tier_a_<stamp>/                           Tier A AR payloads (§7, path A), sha256 inventory
      tier_b/part-NNNNN.tar.gz + .json          Tier B checkpoints, by name, every 10 minutes
  r1_tierb/<session stamp>/                     per-session evidence: restore report, progress,
                                                logs, gates, agreement report, publication plan
```

## 4. Proposed notebook: `colab/r1_tier_b.ipynb`, with every estimating step disabled by default

| Cell | Purpose | Estimates? | Default |
|---|---|---|---|
| T0 Settings | `PIN_COMMIT = 8aaa421…`, `TIER_A_EVIDENCE = c5324b2…`, `TIER_A_RELEASE = 292227e…`, `EXPECTED_IDENTITY`, `EXPECTED_PAYLOADS = 18964`, `TIER_B_TASKS` (the nine IDs, fixed), `WORKERS = 4`, `BACKUP_MINUTES = 10`, **`RUN_TIER_B = False`**, **`CONFIRM_PUBLISH = False`**, `TIER_A_SOURCE = "drive-backup"` | no | safe |
| T1 Drive, clean checkout, environment, frozen-data check | as in the replay notebook: pin asserted, `git status` empty, lock verified, frozen sha256 | no | runs |
| T2 Restore | original cache from `fit_cache/` (read only, count = 18,964); refit cache from `r1_refit_cache/…/tier_a_*` (Tier A) and `…/tier_b/` (earlier Tier B sessions); verify every sha256 against the inventories | no | runs |
| T3 Preflight gates G0–G4 | identity, replay-state, Tier A carry-over, resume integrity, workload re-estimate | no | runs; stops on failure |
| T4 Supervisor + backup daemon | start the `WORKERS` worker processes over the remaining Tier B tasks (longest first) and `thesis_colab.py backup-daemon --pair-by-name refit_cache/fits → r1_refit_cache/…/tier_b` every `BACKUP_MINUTES` | **yes** | **only if `RUN_TIER_B = True`** |
| T5 Watch | stream progress (origins per chain, ETA) and re-attach after a browser disconnect; reading only | no | — |
| T6 Completion gate G5, then a final backup sync | every Tier B chain complete in the refit cache; final sync verified | no | — |
| T7 Assembly | R1 legacy, then corrected, then release, with `--approve` for all 17 chains and `--refit-cache`; gates G6–G8 | no (asserted) | requires G5 |
| T8 Agreement and reliability report (G7) | per-origin comparison with the original fit records; failure classifications; F6 divergence profile | no | — |
| T9 Publication | the Step 8 logic extended to a `tier-b` label: dry run unless `CONFIRM_PUBLISH`; new branches only | no | dry run |

## 5. Interruption, restore and resume

**What survives a disconnect.**

- Every completed origin is in `refit_cache/fits` as an atomically written payload.
- That folder is copied to Drive every 10 minutes, by name, in parts of at most 2,000 files, each logged.
- **Worst-case loss per chain:** fits made since the last sync (≤ 10 min) plus the fit in progress. Across 4 workers that is at most about 40 CPU-minutes.

**Restart.** Run all again. T2 restores the original cache and every refit-cache part, and T3 validates them. T4 relaunches only unfinished chains. Each worker calls `run_chain` from origin 1:

- origins already in the refit cache are **served from it**;
- the first missing origin is estimated with the warm start taken from the last served payload;
- the chain then continues to the end.

**Why a resumed chain equals an uninterrupted one (same platform).**

- The successor key embeds the predecessor's parameters, rounded to 10 decimals. The warm start is the predecessor payload's `warm_payload`.
- That payload is stored as JSON, which round-trips Python floats exactly. So a resumed chain repeats exactly what an uninterrupted run would have computed.
- This is tested at the pinned commit: `test_cache_fidelity.py::test_a_partly_restored_cache_reports_identically` (MSAR), and `test_r1_replay.py::test_refit_cache_resumes_an_interrupted_chain`. Both pass here.
- If a resume happens on a **different** VM, later fits may differ at platform level. That is the documented F6 sensitivity, and each chain's session boundaries are recorded.

**Restore validation (gate G4, every restart).**

- (a) Every restored payload parses, carries the refit marker and covers the chain's horizons.
- (b) The sha256 values of restored files equal the Drive inventories.
- (c) For each chain, a key walk through the refit cache, as in `replay.classify_chain`, gives a **contiguous completed prefix**. That prefix must be at least as long as the one recorded in the previous session's `progress.json`. A shorter prefix means lost or corrupt checkpoints, and the run stops.
- (d) Payloads that the walk cannot reach are counted. They would mean a non-deterministic resume, so the run stops for review.
- (e) `*.tmp` files are ignored, and never backed up.

## 6. Validation gates (all stop the run on failure; none can be overridden silently)

| Gate | Check |
|---|---|
| G0 Provenance | HEAD = `8aaa421`, clean tree, cache identity `3413465b508bb844`, frozen-data sha256, lock environment verified |
| G1 Original cache | 18,964 unique payloads; read-only copy; none carries the refit marker |
| G2 Replay state | a fresh `r1_cache_replay_report.py` reproduces the Tier A evidence `replay_report.json`: the same 20 pending chains, hits, misses and Tier B list. This proves the cache state is unchanged |
| G3 Tier A carry-over | the refit cache holds the 8 Tier A chains **complete** (5,597 payloads, marked, sha256 equal to the backup inventory). Their failure counts are 2, 71, 0, 0, 0, 1, 1, 1 |
| G4 Resume integrity | §5 (a)–(e), at every restart |
| G5 Chain completeness | all 9 Tier B chains: walk complete (6,041 origins), none unreachable, final Drive sync verified |
| G6 Original-results reproduction | assembly in **legacy** mode. Every file not built from a re-estimated chain must be identical, or within 1e-9, to the original. For T4.1 and T4.8 UNRATE, the differences between re-estimated and original chains are not hidden: they go to the agreement report (G7) |
| G7 Numerical reliability | per origin, against the original `fit_records` for the same chain: status agreement, loglik difference, parameter difference, failure codes; per chain, failed counts against the original (22, 13, 7, 6, 5, 3, 52, 0, 0). **ARMA** (no warm start) must reproduce: status identical at every origin and loglik within 1e-6 relative, otherwise stop for review. **MSAR and STAR** (warm-started): report the first divergent origin and the divergence profile, as F6 requires; any change in failure classification is listed for your review and never accepted automatically. Recorded HLZ/DM-HLN degeneracies (`star_test_degeneracy.csv`) are carried into the report |
| G8 Assembly | `estimations_performed == {}` in both assembly passes. Chain sources: re-estimated = exactly the 17 IDs, cache = 17, unavailable = exactly the **26 unaffected** chains of `nonpublished_chain_classification.csv`. **No `original_retained_pending_estimation` row remains.** Tier A tables (T4.2) identical to release `292227e` |
| G9 Corrected-release provenance | release manifest commit `8aaa421`, clean tree, run ID equal across summary and manifests, inventory sha256; the Step 8 selection rules extended to `tier-b`; dry-run plan written before any push |

## 7. How the Tier B release incorporates the eight Tier A chains without re-estimating them

The R1 release keeps no forecasts for robustness chains. The **only** carrier of the eight re-estimated AR chains is the Tier A refit cache, and it is not on Drive. The paths, in order of preference:

- **Path A (preferred): rescue the Tier A refit cache.**
  - If the Tier A Colab runtime is still alive, paste `colab/r1_backup_tier_a_refit_cache.py` into a new cell and run it, first as a dry run, then with `DO_BACKUP = True`.
  - The cell inventories the 5,597 expected payloads (sha256) and requires every one to carry the refit marker.
  - It writes them by name to the new folder `r1_refit_cache/3413465b508bb844/tier_a_<stamp>/`, never `fit_cache/`.
  - It then restores the parts into a temporary directory and requires every sha256 to match.
  - It estimates nothing. 4 tests cover it.
  - Tier B then restores this folder (T2) and verifies it (G3). In the assembly, the 8 AR chains are served entirely from it (`from_cache = attempted`), so `estimations_performed` stays at zero.
- **Path B (fallback; needs your explicit approval): deterministic regeneration.**
  - If the runtime has been recycled, the eight AR chains can only be re-derived. That is under 1 CPU-minute of closed-form AR estimation, which the Tier A validation showed reproduces published AR forecasts with a relative difference of 0.0.
  - It is gated: the regenerated chains must give failure counts 2, 71, 0, 0, 0, 1, 1, 1 and T4.2 tables identical to release `292227e`. If they don't, nothing is used.
  - Strictly, it is a re-estimation, so it needs your approval and is labelled as such in provenance.
- **Prefix reuse is not used** (§1).

## 8. Safety controls and expected results

**Safety controls.**

- `RUN_TIER_B = False` and `CONFIRM_PUBLISH = False` by default.
- Tasks come from a fixed list of nine IDs, checked against G2. No `--approve` is possible for any other task: a Tier A ID is only ever served from the refit cache.
- New Drive folders and new branches only; no force push.
- Single-threaded BLAS in every worker.
- `estimations_performed` is recorded per worker and per pass.
- Every gate stops the run.
- Nothing changes `code/src`, `code/tools`, `approved-specs/`, `data/frozen/` or `output/`.

**Expected results.**

- T4.1 (UNRATE and FEDFUNDS) and T4.8 UNRATE at 180 and 300 months are recomputed with F1. For example, FEDFUNDS T4.1 AR is scored on 555 rather than 626 origins.
- The remaining `pending` marks disappear, leaving 26 chains legitimately retained as unaffected.
- Claims C14 and C15 can then be re-adjudicated. C16 was already resolved by Tier A.
- The re-estimated MSAR and STAR chains are expected to diverge from the originals at some origins (F6). G7 makes that visible origin by origin, and the release labels those chains `re-estimated`.

## 9. Proposed implementation (after your review; not done yet)

New files, all outside the scientific code:

- `colab/make_r1_tier_b_notebook.py` and its output `colab/r1_tier_b.ipynb`;
- `colab/r1_tier_b_supervisor.py`: launches workers longest-first, single-threaded BLAS, one cache root per worker, writes `progress.json`;
- a gate module, `colab/r1_tier_b_gates.py`, for G2–G9 and the G7 agreement report.

Planned tests:

- notebook defaults estimate nothing;
- the supervisor accepts only the nine IDs;
- per-worker cache roots link to a read-only original cache;
- resume after a simulated interruption, using a synthetic STAR or MSAR chain, killed mid-chain and restored from Drive-style parts;
- G4 detects a truncated or corrupted refit cache;
- G8 fails if any estimation occurs in assembly, or if any pending row remains;
- the Step 8 `tier-b` selection;
- the static workload check.

All of these run without real Tier B estimation.

## 10. Risks

1. **Runtime length.** At least 17.9 h of wall-clock time, so at least one interruption is likely. That is covered by §5; the worst-case loss is about 10 minutes per chain.
2. **Tier A carry-over.** If the Tier A runtime has been recycled, Path A is impossible and Path B needs approval.
3. **F6 platform sensitivity.** Re-estimated MSAR and STAR chains will not be bit-identical to the originals, and a resume on a different VM may diverge after the resume point. This is disclosed, not hidden (G7).
4. **Failure classifications may differ** from the original for MSAR and STAR. That is listed for review, never accepted automatically.
5. **Speed uncertainty.** The per-fit times are the original Colab measurements, taken under 4 concurrent workers; expect ±30%.
6. **Figure byte comparison.** The legacy gate compares figures byte for byte, which depends on the fonts the runtime renders (documented on 3 November). G6 can stop on fonts alone; tables decide.
