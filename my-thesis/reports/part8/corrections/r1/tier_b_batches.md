# R1 Tier B — three independent batch notebooks (implementation; not authorised to run)

Date: 4 November 2026; revised the same day after independent review (safeguards: agreement categories, review-required status, interrupted-session provenance, Drive protocol check). This document replaces the single-notebook execution design in `tier_b_preflight.md` §2–§4. That document's workload analysis and gate definitions still apply.

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
   Before the restores, section 3b runs the **Drive checkpoint check** (§6a) in a disposable namespace.
   Finally it runs the preflight. This walks the eight Tier A chains and checks their failure counts (2, 71, 0, 0, 0, 1, 1, 1). It also checks that each of this batch's chains has exactly one original fit record per planned origin, with the declared original failure count. It then reports each chain's committed progress. **It estimates nothing.**
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
  sessions/<utc>-<session>/   session_started.json, progress.json, session_summary.json, logs/
  leases/<session>.json
  certificates/COMPLETE-<utc>-<session>.json, agreement-<session>.csv
```

**Completion-marker protocol.** This does not rely on renaming directories. A checkpoint folder is created under its final name and filled in this order:

1. The new payloads since the last commit are gathered. Each must carry the refit marker, and none may differ from an already committed payload.
2. `payloads.tar.gz` is built locally, written, `fsync`ed, read back from Drive, and checked member by member against the local payloads.
3. `manifest.json` is written and read back. It records the parent, the members' sha256 values, the archive sha256 and the session record (§6b).
4. `COMMITTED` is written last and read back. It is a small JSON naming the checkpoint, with the sha256 of the manifest and of the archive.

**Validity rules.**

- A folder counts **only** if `COMMITTED` parses, belongs to this protocol, and both hashes match.
- A folder without a valid marker is an **interrupted write**: an archive or manifest cut off, or a marker cut mid-write. It is ignored and listed, never modified or deleted. Earlier commits are never touched.
- Once a valid marker exists, any later mismatch is corruption, and it **raises**.
- A failed Drive write stops the session with exit 2.

**Restore checks:**

- the marker and both hashes;
- every member's sha256;
- a linear parent chain, with no fork and no gap;
- no conflicting duplicate.

The worker then **walks** each chain through the restored payloads with the pinned key function, including the warm-start predecessor hash. It requires a contiguous prefix and that **no payload is unreachable**. A resumed chain serves its verified origins from the restored payloads, reading only, and estimates from the first missing origin onwards.

**Lost work.** Only committed checkpoints survive the loss of a VM. By design, what can be lost is what was estimated since the last successful commit, plus the origin in progress. **I do not claim a guaranteed maximum.** The tests prove recovery to the last commit and identical estimates after resuming; they do not prove a bound on Drive latency.

### 6a. Drive checkpoint check (notebook section 3b; `RUN_DRIVE_CHECK = True`)

`colab/r1_tierb_drive_check.py` runs **the batches' own checkpoint code** on the mounted Drive. It uses synthetic, properly marked payloads and fits no model. Everything goes into a disposable namespace, `baseline/r1_tierb_drive_check/<SESSION>/`, which is new each time and never reused. It checks:

1. checkpoint creation;
2. archive read-back from Drive against the manifest;
3. a second, incremental checkpoint with the correct parent, plus an informational probe of directory and file renames on the mount (the protocol does not depend on them);
4. interrupted-write recovery: a write cut after the archive, and one cut inside the marker, are both ignored; the history is unchanged; the retry commits with the right parent;
5. restore into a fresh local folder equals the source;
6. a corrupted archive and a tampered manifest are both detected;
7. **namespace isolation**:
   - a listing (size and mtime) of every protected namespace is identical before and after: all three batch namespaces, the Tier A checkpoint, the aggregation folder and every original-cache archive folder;
   - nothing was written outside the check's folder;
   - the batch write guard refuses the check folder.

Any failure stops the notebook before any restore or run. The report is written to `<check folder>/drive_check_report.json`.

**Persistence across runtimes.** Reading back on the same VM may be served from that VM's Drive cache. To confirm that checkpoints persist on Drive itself, open any batch notebook in a **new** runtime, set `DRIVE_CHECK_VERIFY_ID` to the check id printed by the first runtime, and run up to section 3b. It restores the earlier check's checkpoints from Drive and compares them.

### 6b. Session provenance, including hard-killed sessions

- The supervisor takes the lease **first**. A session refused by the lease leaves no record.
- It then writes `sessions/<utc>-<session>/session_started.json`, recording:
  - batch, session, start, VM start and budget;
  - worker count and host;
  - scientific and orchestration commits, and cache identity.
- Every checkpoint manifest of the session repeats this record as `session_record`. A session is therefore traceable **from its checkpoints alone**, even if its session folder or summary is missing.
- `r1_tierb.session_ledger()` reconstructs every session from session folders, leases, committed manifests and incomplete checkpoint writes:
  - **`terminated`** sessions wrote `session_summary.json`, and are classified as complete, budget reached or error;
  - **`interrupted`** sessions did not (hard-killed or lost), with: last progress time, unreleased lease, committed checkpoints and payloads per chain, and incomplete writes.
- Certificates list the two groups separately. Estimations by chain are counted from the committed manifests: a payload committed by a session is a fit that session estimated. Work after a session's last commit was lost, and is re-estimated on resume.

## 7. Batch certificates and the agreement report (G7)

Cell 8 runs `r1_tierb_worker.py certify`. It restores the batch **from Drive only** into a temporary folder and walks every chain. It then compares every origin with the original fit records, and writes `certificates/COMPLETE-…json` when **every chain is complete**.

**A completion certificate is not an approval.** It carries three separate fields:

- `computation_status`: `COMPUTATION_COMPLETE`. An incomplete batch gets no certificate; the report says `COMPUTATION_INCOMPLETE`.
- `scientific_status`, one of:
  - **`COMPUTATION_COMPLETE_REVIEW_REQUIRED`**: at least one review item;
  - **`COMPUTATION_COMPLETE_SENSITIVITY_REPORTED`**: no review item, but expected MSAR/STAR optimizer sensitivity is reported;
  - **`COMPUTATION_COMPLETE_REPRODUCED`**: every origin reproduced.
- `scientific_approval`: always *"not granted: a completed computation is not an approved result"*.

The certificate also contains `review_items` and `sensitivity_reported`, kept separate and both in full. It also contains everything listed before: tasks, origins, per-chain counts, checkpoints, provenance and estimations. Sessions appear as `sessions_terminated` and `sessions_interrupted`.

**Tolerances (declared, used as stated).**

- Log-likelihood: |l_new − l_orig| / max(1, |l_orig|) ≤ **1e-6**.
- Every parameter: |p_new − p_orig| / max(1, |p_orig|) ≤ **1e-8**.
- The original parameters are stored with 10 significant digits, so their rounding contributes at most 5e-10.

**Original records.** Each chain is matched by series, model and window span. At the 240-month span, the T4.1 chain is the one record per origin not shared with the baseline chain.

- The preflight requires exactly one record per planned origin, with the declared original failure count. Verified on real data for all nine chains.
- An ambiguous match **raises**; it is never guessed.

**Per origin, exactly one category:**

| Category | Meaning | Effect |
|---|---|---|
| `reproduced` | same status and reason codes; loglik and every parameter within tolerance | — |
| `reproduced_regime_labels_permuted` | MSAR: as above after relabelling regimes (`mu{k}`, `p{ij}` permuted; `phi`, `sigma` are shared and never permuted) | — |
| `classification_changed` | status **or reason codes** differ (any model) | **review** |
| `missing_original_record` | a re-estimated origin with no original record | **review** |
| `original_origin_not_reestimated` | an original record with no re-estimated origin | **review** |
| `parameter_names_differ` | the parameter sets differ (names listed) | **review** |
| `reproduction_failure` | ARMA (no warm start): loglik or any parameter outside tolerance | **review** |
| `unexplained_parameter_discrepancy` | MSAR/STAR: parameters differ at equal likelihood **before** the chain's warm-start path diverged | **review** |
| `optimizer_sensitivity` | MSAR/STAR: same classification, different log-likelihood (another optimum; signed difference reported) | reported (F6) |
| `flat_likelihood_sensitivity` | MSAR/STAR: same classification and likelihood, different parameters, **after** the path diverged (different start) | reported (F6) |

A changed per-chain failure count is a review item too. Expected MSAR/STAR sensitivity stays visible, with:

- the first divergent origin;
- counts per category;
- the number of origins where the re-estimate's likelihood is lower;
- origin-level rows in `agreement-<session>.csv`;
- the regime-label permutation and the starting values used by both fits.

It is never called reproduced, and never automatically treated as an implementation error.

**Validated on real data, without estimation.** The two T4.8 AR chains re-estimated in Colab for Tier A were compared with their original records at their effective spans. AR records store the post-lag sample start, so the spans are 174 and 294 instead of 180 and 300. The result: **1,408 of 1,408 origins `reproduced`**, with identical log-likelihoods and parameter differences no larger than 4.9e-10. ARMA, MSAR and STAR records use the nominal span, as the record check above confirms.

## 8. Final aggregation (an optional cell in any notebook; `RUN_AGGREGATION = False`)

`colab/r1_tierb_aggregate.py` performs these steps:

1. **Discovery.** It reads each batch's latest certificate and refuses if any batch is missing or incomplete, has other tasks or other code, or has Drive checkpoints that differ from the certified list.
2. **Merge.** It combines the Tier A archive and every certified checkpoint into one refit cache, refusing any conflicting payload. It then walks **all 17 chains** (8 Tier A + 9 Tier B): each must be complete, and every payload must be reached.
3. **Assembly.** It runs the pinned R1 workflow, legacy first, then corrected with the release, with `--approve` for the 17 chains, the merged refit cache and the original cache. This runs inside `no_estimation_allowed()`, so even an approved chain **cannot** estimate.
4. **Gates.** Every certificate must be internally consistent. Its `scientific_status` must follow from its own review items, every changed failure count and review-required chain must be listed, and no certificate may claim approval; otherwise aggregation is refused.
   - `estimations_performed` is empty;
   - 17 re-estimated chains, 17 from the cache, and exactly the 26 unaffected unavailable chains;
   - no `original_retained_pending_estimation` row remains;
   - the legacy reproduction holds for every file not fed by a re-estimated chain;
   - the files a re-estimated chain feeds (T4.1, T4.8) are reported separately as agreement, not reproduction;
   - T4.2 is identical to the Tier A release `292227e`.
5. **Status.** `aggregation_status` is one of:
   - **`AGGREGATION_REFUSED`**: a gate failed;
   - **`COMPUTATION_COMPLETE_REVIEW_REQUIRED`**: a review item in any batch, or a table difference from a re-estimated chain that no chain report explains;
   - **`COMPUTATION_COMPLETE_SENSITIVITY_REPORTED`**;
   - **`COMPUTATION_COMPLETE_REPRODUCED`**.

   The plan carries `scientific_approval: not granted`, every review item and every sensitivity item, prefixed by batch, plus the interrupted sessions. Nothing is suppressed. Exit codes: 1 refused, 4 review required, 0 otherwise. The notebook prints the `AGGREGATION_STATUS` line and never "passed".
6. **Plan.** It writes a dry-run plan to `baseline/r1_tierb_aggregation/<stamp>/`. **There is no publication code.**

## 9. Tests

None estimates real models; the resume tests use tiny synthetic chains with the pinned engine.

| File | Tests |
|---|---|
| `test_r1_tierb_checkpoints.py` | 20 |
| `test_r1_tierb_agreement.py` | 18 |
| `test_r1_tierb_drive_check.py` | 5 |
| `test_r1_tierb_supervisor.py` | 4 (stand-in worker) |
| `test_r1_tierb_aggregate.py` | 20 |
| `test_r1_tierb_notebooks.py` | 16 |
| `test_r1_tierb_resume.py` | 7 (pinned engine, synthetic STAR chain) |
| **Total** | **90** |

What is new since the first review:

- **Checkpoints:**
  - a marker cut mid-write leaves the checkpoint uncommitted, and the retry commits;
  - the protocol never renames a directory;
  - tampered manifests and markers are detected;
  - legacy `.partial` folders and foreign markers are ignored;
  - the session ledger separates interrupted from terminated sessions, including a session known only from its checkpoints.
- **Agreement:**
  - identical ARMA reproduced;
  - stored-parameter rounding within tolerance;
  - ARMA loglik or parameter differences require review;
  - a changed status requires review for MSAR, STAR and ARMA alike;
  - a changed reason code with the same status requires review;
  - missing and unmatched records require review;
  - parameter-name coverage is checked;
  - MSAR label switching is recognised, and a shared parameter is not relabelled;
  - MSAR/STAR optimizer sensitivity is reported, not escalated;
  - equal-likelihood parameter discrepancies are unexplained before divergence and flat-likelihood after;
  - ambiguous original records are refused.
- **Certificates:**
  - a reproduced batch is still "not granted";
  - a changed failure count gives review required;
  - review and sensitivity items are both kept;
  - there is no certificate without agreement for every chain.
- **Supervisor:**
  - **a real SIGKILL of a running session** after its first commit: no summary exists, yet the session, its payloads and its unreleased lease are on record, it is classified as interrupted, and its manifests carry the commits;
  - a second session is then refused and leaves no record;
  - a normal session is classified as terminated.
- **Drive check (local stand-in for the mount):**
  - all seven checks pass and only the check folder is written;
  - cross-runtime verification works;
  - a change to a protected namespace fails the check;
  - a broken step is reported, not hidden;
  - a namespace is never reused.
- **Aggregation:**
  - inconsistent certificate statuses, claimed approval, an incomplete computation, and an unlisted failure-count change or review-required chain are refused;
  - the status is review required, sensitivity reported, reproduced or refused, as appropriate;
  - unexplained table differences require review.
- **Notebooks:**
  - the Drive-check cell writes only its namespace and verifies across runtimes;
  - the aggregation cell never prints "passed".

**Real-data checks (no estimation).**

- Preflight for B1, B2 and B3: cache identity `3413465b508bb844`; all eight Tier A chains complete with the expected failure counts; one original record per planned origin for all nine chains (644, 764, 626, 764, 703, 644, 644, 626, 626), with failures 3, 5, 52, 22, 7, 13, 6, 0, 0 as declared.
- The AR agreement validation in §7.

**Not testable here:** the actual Google Drive mount. Section 3b runs the Drive check there; it is part of the preflight procedure in §11.

## 10. Remaining risks and approvals

1. **Colab account limits** (concurrent runtimes, compute units, session length) can prevent simultaneous runs or end sessions early. The design resumes, but elapsed time grows.
2. **B1** will probably need two sessions, even on Pro+.
3. **F6.** Re-estimated MSAR and STAR chains will not match the originals bit for bit, especially after resuming on a different VM. The divergence is reported origin by origin and never accepted automatically. An ARMA divergence sets `requires_review`.
4. **Failure classifications** can differ from the original. They are listed in the certificate for your review.
5. **Speed:** ±30% around the historical per-fit times.
6. **Figure bytes** in the legacy reproduction can depend on runtime fonts; tables decide.
7. **The supervisor and the end-to-end Colab flow have not been run against real Drive and real estimation.** They were tested with stand-ins and synthetic chains only. The Drive protocol is validated on the real mount only when you run section 3b (§11).
8. **ARMA reproduction across VMs.** The parameter tolerance is 1e-8. If a Colab VM's CPU or BLAS produces last-digit differences that an optimizer amplifies, ARMA origins will be flagged `reproduction_failure` and the batch will be review required, never silently accepted. The rows show the magnitude.

**Approvals needed:**

- (a) authorisation to run each batch, i.e. set `RUN_TIER_B = True`;
- (b) later, authorisation to run the aggregation;
- (c) separately, authorisation to publish (not implemented).

## 11. Ready-to-run non-estimating Colab preflight (do this before authorising any batch)

For **each** of B1, B2 and B3, in a fresh runtime (CPU, High-RAM), with the Colab secret `GITHUB_TOKEN`:

1. Open the notebook at the pinned commit (links in the final report). Leave every default: `RUN_TIER_B = False`, `RUN_AGGREGATION = False`, `RUN_DRIVE_CHECK = True`, `DRIVE_CHECK_VERIFY_ID = ""`.
2. **Runtime → Run all.** Expected, in order:
   - §1: Drive mounted, settings valid, a session id `B<n>-<utc>-<hex>`;
   - §2: orchestration and pinned commits checked out, clean, the pin an ancestor;
   - §3: environment verified against the lock, frozen data verified, cache identity `3413465b508bb844`;
   - §3b: `Drive checkpoint check <session>: ALL CHECKS PASSED`, with seven `ok` lines, and the check id to note;
   - §4: 18,964 original payloads, Tier A archive sha256 `df73c295…` with 5,597 payloads, this batch's committed checkpoints (none yet);
   - §5: `problems: []`, `original_records: one per planned origin; failures as declared`, and every chain at 0/planned;
   - §6: `RUN_TIER_B is False: no estimation`; §8: nothing to certify; §9: `RUN_AGGREGATION is False`.
3. **Persistence:** in another new runtime, open any batch notebook, set `DRIVE_CHECK_VERIFY_ID` to the noted check id, and run to §3b. Expected: `cross-runtime persistence of <id> OK`. (It also runs a fresh check of its own.)
4. Send me, or your reviewer, for each notebook: the §3b summary, the §5 preflight JSON (`/content/r1tierb_<B>/preflight-<session>.json`), and the persistence line.

Nothing in this procedure estimates a model, writes outside `baseline/r1_tierb_drive_check/<session>/`, or pushes to GitHub. Estimation starts only when you set `RUN_TIER_B = True` for a batch you have authorised.
