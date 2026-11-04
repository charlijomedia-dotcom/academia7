# R1 Tier B — three independent batch notebooks (implementation; not authorised to run)

Date: 4 November 2026. This document replaces the single-notebook execution design in `tier_b_preflight.md` §2–§4. That document's workload analysis and gate definitions still apply.

- **Authorised:** implementation and testing only.
- **Not executed:** no Tier B estimation, no Tier A regeneration, no publication. Part 9 has not been started.

## 1. Notebooks and workloads

| Notebook | Chains | Origins | Historical fitting hours |
|---|---|---|---|
| `colab/r1_tier_b1_msar_300.ipynb` | T4.8:UNRATE\|300:MSAR (MSAR p=4, K=2) | 644 | 17.87 |
| `colab/r1_tier_b2_msar_remaining.ipynb` | T4.8:UNRATE\|180:MSAR (MSAR p=4, K=2); T4.1:FEDFUNDS\|MSAR (MSAR p=1, K=2) | 764 + 626 = 1,390 | 15.93 |
| `colab/r1_tier_b3_arma_star.ipynb` | T4.8:UNRATE\|180:ARMA; T4.1:UNRATE\|ARMA; T4.8:UNRATE\|300:ARMA; T4.8:UNRATE\|300:STAR; T4.1:FEDFUNDS\|STAR; T4.1:FEDFUNDS\|ARMA | 4,007 | 15.62 |
| **Union** | **exactly the nine Tier B chains, no duplicates, no K=3** | **6,041** | **49.42** |

The partition is fixed in `colab/r1_tierb.py` (`BATCHES`) and checked by `validate_partition()` and by the tests. A worker refuses any task outside its batch.

## 2. Provenance: two separate checkouts, both verified at runtime

| | Commit | Used for |
|---|---|---|
| Scientific code (pinned) | `8aaa4217536ab3cb942dd248dd19ece7838a8d60` | All estimation, keys, payloads and failure rules, plus the R1 workflow and tables. Checked out as a separate, clean, detached git worktree (`/content/r1tierb_<B>/pinned`). |
| Orchestration | `ORCH_COMMIT` (set in each notebook) | `colab/r1_tierb*.py`: scheduling, checkpoints, budget, certificates, aggregation. |

At runtime each notebook asserts:

- both HEADs, and that both trees are clean;
- that `PIN_COMMIT` is an ancestor of `ORCH_COMMIT`;
- that `thesis_colab.py` is byte-identical in both checkouts;
- that the cache identity of the pinned code is `3413465b508bb844`;
- the frozen data (`run_all.py --data-only`) and the approved environment (the lock file).

`use_scientific_code()` refuses to import `thesis` from anywhere but the pinned checkout.

**Estimation is exactly the pinned approved path.**

- The worker calls the pinned `rolling.run_chain` with the same arguments as `correction/rescore.py` (`_chains`, approved branch), inside the pinned `guard.estimation_forbidden()`, with `guard.allowed()` only around that call.
- The checkpoint store is a subclass of the pinned `RefitCache`. Its writes are the pinned writes: same marker, same atomic temporary-file-then-rename.
- It can stop **between** origins only. Tested: an uninterrupted run, a budget-stopped run and a killed run, each resumed, give identical estimates. Only the recorded `wall_seconds` timing differs.
- No optimiser setting, seed, warm-start rule, specification or failure rule is touched. Every Tier B chain is re-estimated **from its own origin 1**; the original cache is **never** used for a Tier B chain, so there is no original-cache prefix.

## 3. Independent setup and execution (each notebook, any order, or simultaneously)

1. Open the notebook in Colab: **Runtime → Change runtime type → CPU, High-RAM**.
2. **Secrets:** `GITHUB_TOKEN` (read access; needed if the repository is private). Nothing pushes.
3. **Settings cell.** Leave everything at the defaults, except:
   - `RUNTIME_BUDGET_HOURS`: the default is 11.0; use **20** on Colab Pro+, or less than your plan's limit;
   - `MAX_WORKERS`: defaults are B1 = 1, B2 = 2, B3 = 3, capped at the VM's CPU count.
4. **Run all, with `RUN_TIER_B = False`.** This mounts Drive, checks out and verifies both commits, builds and verifies the environment and the frozen data, and checks the identity. It then restores:
   - the original cache: 18,964 payloads, read only;
   - the Tier A cache: archive sha256 `df73c295…61c2`, 5,597 marked payloads;
   - this batch's own committed checkpoints.
   Finally it runs the preflight, which walks the eight Tier A chains and checks their failure counts (2, 71, 0, 0, 0, 1, 1, 1), and reports each chain's committed progress. **It estimates nothing.**
5. **Only with authorisation:** set `RUN_TIER_B = True` and run cell 6 (or Run all again). The supervisor starts in the background. Cell 7 shows progress and can be re-run to re-attach after a browser disconnect.
6. **When the supervisor ends:**
   - exit **0**: every chain is complete and committed. Cell 8 certifies the batch from what is on Drive.
   - exit **3**: the budget was reached and work remains. Open the notebook in a new runtime and Run all with `RUN_TIER_B = True`: it resumes from the last committed checkpoint.
   - exit **2**: an error. Nothing is assumed; read `sessions/<…>/session_summary.json`.

## 4. Elapsed time and runtime budgets

The per-fit times are the original Colab measurements, taken with 4 concurrent workers; allow ±30%. Setup adds about 0.5 h per session: environment, the 18,964-payload cache restore, and job building.

| Batch | Critical path | Expected elapsed | Sessions at 20 h (Pro+) | Sessions at 11 h |
|---|---|---|---|---|
| B1 | one chain, 17.9 h | **12.5–23.2 h** | 1–2 | 2–3 |
| B2 | 2 workers; longest chain 12.5 h | **8.8–16.3 h** | 1 (rarely 2) | 1–2 |
| B3 | 3 workers; longest chain 6.45 h | **4.5–8.4 h** | 1 | 1 |

**Recommendation.** Use `RUNTIME_BUDGET_HOURS = 20` on Pro+, with `RESERVE_MINUTES = 30`. B1 is the one most likely to need a second session.

**No managed Colab runtime can guarantee a continuous 24 hours.** Runtimes can end early from inactivity, capacity or compute-unit limits. The design therefore assumes interruption.

**Budget mechanics.**

- The clock starts at the VM's boot, read from `/proc/uptime`.
- New chains are not launched without room for three typical origins plus job building.
- A worker does not **start** an origin it cannot finish: it allows three times the recent median, and no less than the historical mean. It stops **after** an origin's payload is committed.
- The final checkpoint and its verification use the reserve.
- A batch is never marked complete unless every chain verifies. Otherwise the summary lists every unfinished chain, with its completed and planned origins.

## 5. Simultaneous execution

**Technically supported.** The three notebooks share no writable state:

- each writes only under `baseline/r1_tierb_batches/<B>/`, enforced by `assert_writable_path`;
- each has its own VM working folder (`/content/r1tierb_<B>`);
- they only **read** the original cache, the Tier A archive and GitHub.

Inside a batch:

- each chain has its own local folder and its own checkpoint folder;
- payload writes are atomic;
- a per-batch **lease** stops two sessions of the same batch from running together: a second one is refused while the first's heartbeat is fresh, and forked histories are detected.

**What may prevent it:** your Colab plan.

- The number of runtimes that can run at the same time.
- Compute units: three High-RAM CPU runtimes for 10–20 h each.
- Idle and background-execution rules.
- Drive I/O rate limits during the cache restores.

I can't verify these limits for your account. If simultaneous runtimes are not allowed, run the batches one after another, in any order.

## 6. Checkpoints and recovery

```
baseline/r1_tierb_batches/<B>/
  checkpoints/<chain>/ckpt-<utc>-<session>-<seq>-<rand>/   payloads.tar.gz, manifest.json, COMMITTED
  checkpoints/<chain>/ckpt-...partial/                     interrupted write: ignored
  sessions/<utc>-<session>/   progress.json, session_summary.json, logs/
  leases/<session>.json
  certificates/COMPLETE-<utc>-<session>.json, agreement-<session>.csv
```

**Commit protocol (every `BACKUP_MINUTES`, default 10, and finally).**

1. Gather the payloads new since the last commit. Every one must carry the refit marker, and none may differ from an already committed payload.
2. Build the tar locally, copy it into `<id>.partial/`, read it back from Drive, and require every member's sha256 to match.
3. Write the manifest (parent, member sha256s, archive sha256) and `COMMITTED`.
4. Rename the folder to its final name.

A write interrupted at any step leaves only a `.partial` folder; earlier commits are never modified. A failed Drive write stops the session with exit 2.

**Restore checks:**

- `COMMITTED` and the archive sha256 match the manifest;
- every member's sha256 matches;
- the parent chain is linear, with no fork and no gap;
- there is no conflicting duplicate.

The worker then **walks** each chain through the restored payloads with the pinned key function, including the warm-start predecessor hash. It requires a contiguous prefix and that **no payload is unreachable**. A resumed chain serves its verified origins from the restored payloads, reading only, and estimates from the first missing origin onwards.

**Lost work.** Only committed checkpoints survive the loss of a VM. By design, what can be lost is what was estimated since the last successful commit, plus the origin in progress. **I do not claim a guaranteed maximum.** The tests prove recovery to the last commit and identical estimates after resuming; they do not prove a bound on Drive latency.

## 7. Batch certificates

Cell 8 runs `r1_tierb_worker.py certify`. It restores the batch **from Drive only** into a temporary folder, walks every chain, compares each origin with the original fit records (G7), and writes `certificates/COMPLETE-…json` **only if every chain verifies**. The certificate contains:

- the batch and its exact tasks;
- expected and completed origins;
- per-chain status and counts of adequate, fragile and failed fits, alongside the original failed counts;
- the checkpoint IDs and their archive sha256 values;
- the sessions, with their start and end times and elapsed hours;
- provenance: scientific and orchestration commits, cache identity, frozen-data sha256, Python and package versions, Tier A archive sha256;
- estimations by task, with confirmation that only authorised chains were estimated;
- warnings: failure-count changes, and the agreement report.

**Agreement rule.** An ARMA chain (no warm start) must reproduce the original: identical status and log-likelihood within 1e-6. Otherwise the certificate sets `requires_review`. MSAR and STAR report their first divergent origin and the extent of divergence (F6).

## 8. Final aggregation (an optional cell in any notebook; `RUN_AGGREGATION = False`)

`colab/r1_tierb_aggregate.py` performs these steps:

1. **Discovery.** It reads each batch's latest certificate and refuses if any batch is missing or incomplete, has other tasks or other code, or has Drive checkpoints that differ from the certified list.
2. **Merge.** It combines the Tier A archive and every certified checkpoint into one refit cache, refusing any conflicting payload. It then walks **all 17 chains** (8 Tier A + 9 Tier B): each must be complete, and every payload must be reached.
3. **Assembly.** It runs the pinned R1 workflow, legacy first, then corrected with the release, with `--approve` for the 17 chains, the merged refit cache and the original cache. This runs inside `no_estimation_allowed()`, so even an approved chain **cannot** estimate.
4. **Gates.**
   - `estimations_performed` is empty;
   - 17 re-estimated chains, 17 from the cache, and exactly the 26 unaffected unavailable chains;
   - no `original_retained_pending_estimation` row remains;
   - the legacy reproduction holds for every file not fed by a re-estimated chain;
   - the files a re-estimated chain feeds (T4.1, T4.8) are reported separately as agreement, not reproduction;
   - T4.2 is identical to the Tier A release `292227e`.
5. **Plan.** It writes a dry-run plan to `baseline/r1_tierb_aggregation/<stamp>/`. **There is no publication code.**

## 9. Tests

All run without estimation, apart from tiny synthetic chains.

| File | Tests |
|---|---|
| `test_r1_tierb_checkpoints.py` | 15 |
| `test_r1_tierb_resume.py` | 7 (pinned engine, synthetic STAR chain) |
| `test_r1_tierb_aggregate.py` | 13 |
| `test_r1_tierb_notebooks.py` | 14 |
| `test_r1_tierb_supervisor.py` | 2 (stand-in worker) |

**Checkpoints:**

- partition: nine chains, 6,041 origins;
- incremental commit and restore;
- `.tmp` files never committed;
- **interrupted backup preserves the previous commit**;
- corrupted or missing archives detected;
- conflicting payloads and forked histories refused;
- unmarked payloads never committed;
- unsafe archive members refused;
- **concurrent commits by 3 batches × their chains never collide**;
- writes confined to the batch;
- leases;
- Tier A archive checks: sha256, marker, count;
- budget arithmetic.

**Recovery:**

- the stoppable cache writes exactly the pinned estimates;
- **budget stop, then resume from Drive-only in a fresh "VM", equals the uninterrupted run**;
- the budget refuses an origin it cannot finish;
- **SIGKILL mid-chain, then commit, wipe, restore and resume, equals the uninterrupted run**;
- unreachable payloads detected;
- a worker refuses a task outside its batch;
- `no_estimation_allowed()` blocks even approved blocks.

**Aggregation refuses:**

- a missing batch;
- an incomplete certificate, a short origin count, wrong tasks or wrong provenance;
- checkpoints added after certification;
- a conflicting payload between batches or with Tier A;
- an assembly that estimated;
- remaining pending rows;
- a legacy-reproduction failure;
- a T4.2 difference from Tier A.

**Notebooks:**

- exactly three notebooks, matching their generator; plain Python;
- safe, pinned defaults;
- the union of task lists is exactly the nine chains;
- **Setup runs independently in all 6 orders**;
- disjoint write locations; no code that pushes;
- **default Run all launches nothing and runs no subprocess**;
- `RUN_TIER_B = True` launches only that batch's supervisor;
- **no change to scientific code, configuration, data, specifications or outputs since the pin**.

**Supervisor:**

- every chain committed and verified, the lease released, and no other batch touched;
- with no budget, nothing starts and the exit code is 3, not "complete".

**Real-data checks (no estimation).**

- The real Tier A archive from Drive: sha256 `df73c295…`, 5,597 marked payloads.
- The worker preflight for B1, B2 and B3 with the pinned jobs: cache identity `3413465b508bb844`.
- All eight Tier A chains walk complete: failed fits 2, 71, 0, 0, 0, 1, 1, 1, with no unreachable payload.
- All nine Tier B task IDs resolve, with the planned origins 644, 764, 626, 764, 703, 644, 644, 626, 626.

## 10. Remaining risks and approvals

1. **Colab account limits** (concurrent runtimes, compute units, session length) can prevent simultaneous runs or end sessions early. The design resumes, but elapsed time grows.
2. **B1** will probably need two sessions, even on Pro+.
3. **F6.** Re-estimated MSAR and STAR chains will not match the originals bit for bit, especially after resuming on a different VM. The divergence is reported origin by origin and never accepted automatically. An ARMA divergence sets `requires_review`.
4. **Failure classifications** can differ from the original. They are listed in the certificate for your review.
5. **Speed:** ±30% around the historical per-fit times.
6. **Figure bytes** in the legacy reproduction can depend on runtime fonts; tables decide.
7. **The supervisor and the end-to-end Colab flow have not been run against real Drive and real estimation.** They were tested with stand-ins and synthetic chains only.

**Approvals needed:**

- (a) authorisation to run each batch, i.e. set `RUN_TIER_B = True`;
- (b) later, authorisation to run the aggregation;
- (c) separately, authorisation to publish (not implemented).
