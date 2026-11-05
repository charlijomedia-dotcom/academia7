# R1 Tier B: warm-start cache-continuity failure in B2: investigation and correction proposal

Date: 5 November 2026.

- **Status:** a correction proposal for independent review. **B2 must not be restarted until it is approved.**
- **What was done:** no model was estimated; no checkpoint, original cache, Tier A archive or published result was changed; the scientific pin is unchanged.
- **Evidence:** the actual B1 and B2 Drive checkpoints. They were downloaded read-only, verified, and analysed on local copies.

## 1. Observed failure

B2 session `B2-20261105T071915Z-d12923` ended with supervisor exit 2. The FEDFUNDS worker exited 1 because its own post-estimation chain validation (`walk_chain`) failed. The supervisor's final check, "Drive checkpoints equal local payloads", passed: the data were saved correctly. Only the verifier rejected them.

| Chain | Committed payloads | Reached by the walk (old verifier) | Unreachable |
|---|---|---|---|
| T4.1:FEDFUNDS\|MSAR | 626 (12 checkpoints) | 2 | 624 |
| T4.8:UNRATE\|180:MSAR | 257 (12 checkpoints) | 229 | 28 |

Both chains were estimated **live, in that single session, from origin 1**. Both chain folders were created at the session's first backup (07:30:22Z), and every manifest names that session. So no resume was involved in B2.

## 2. Root cause

The pinned engine, `thesis.forecasting.rolling.run_chain` at `8aaa421`, carries the warm start differently in its two branches:

| Branch | Code | After a **failed** fit |
|---|---|---|
| Live estimation | `if outcome.usable and outcome.warm_payload is not None: warm_payload = outcome.warm_payload`, where `usable` means `status is not FAILED` | keeps the **last usable** fit's warm start |
| Cache hit | `warm_payload = payload["warm_payload"]` (or `None`) | takes the stored value, which is **`None`** for failed MSAR fits |

The successor's cache key embeds `predecessor_hash`, the warm start rounded to 10 decimals. After a failed origin:
- the live run wrote the next payload under a key carrying the **previous usable fit's** parameters;
- the cache-hit branch asks for a key with an **empty** predecessor, which was never written.

**Affected models:** only those whose fits produce a warm payload, MSAR (`theta`) and STAR (`(gamma, c)`). ARMA and AR have none (predecessor always empty), so they are unaffected. This is why Tier A (AR) never showed it.

**Three consequences**, all in orchestration code that relied on the cache-hit branch:

1. **Verifier.** `r1_tierb.walk_chain` copied the cache-hit rule, so it stopped after the first failed origin. That is the B2 symptom.
2. **Resume.** The pinned `run_chain` with the plain cache, which the old worker used, would hit up to the failed origin. It would then **re-estimate** the next origin from a **cold start**, store it under a different key and fork the chain. The synthetic test shows this, with at least one duplicate estimation and a forked payload.
3. **Final assembly.** The R1 workflow replays approved chains through the pinned `run_chain` and `rescore.RefitCache`. With estimation forbidden, the first post-failure origin is a miss and assembly fails with `EstimationForbidden`. The synthetic test shows this.

My tests did not catch it because the resume tests used a STAR chain with no failed origin. The new tests include one.

## 3. Real-checkpoint evidence (item 1)

All 79 B2 files and 24 B1 files were downloaded read-only and checked against Drive's file sizes. The inventory, with Drive IDs and sha256 values, is `evidence/tier_b_drive_evidence_inventory_20261105.csv`.

Every checkpoint passed the completion-marker, manifest-sha256, archive-sha256 and member-sha256 checks. Restoring produced 626 and 257 payloads.

**First mismatch** (from `colab/r1_tierb_continuity_check.py`; full output in `evidence/tier_b_continuity_B2_20261105.json`):

| | FEDFUNDS MSAR | UNRATE 180 MSAR |
|---|---|---|
| First origin the cache-hit rule cannot reach | #3, 1974-08-01 | #230, 1982-01-01 |
| Preceding origins | 1974-06-01 `fragile` (SINGULAR_COV), **stores** a warm payload; 1974-07-01 **`failed`** (SINGULAR_COV, NONCONVERGENCE), warm payload **None** | 1981-10-01 and 1981-11-01 `adequate`, warm stored; 1981-12-01 **`failed`** (NONCONVERGENCE), warm **None** |
| Key by the cache-hit rule | predecessor `""`, digest `b8b81cbb…a8bf`: **absent** | predecessor `""`, digest `23f6f0db…95bf7`: **absent** |
| Key by the live rule | predecessor `[3.1639985677, 4.3387361434, 0.9999999805, −1.0017835893, −2.3981201864, −2.3559026741]`, digest `f583176c…5605`: **present** | predecessor `[6.6582567624, 6.8499527641, 1.2498841908, …]` (9 values), digest `10e981bd…69eb`: **present** |
| Warm state the estimation used | the parameters of the last usable fit, **1974-06-01** | the parameters of the last usable fit, **1981-11-01** |

## 4. Are the 883 payloads valid continuous chains under the live semantics? (items 2 and 7)

**Yes: all 883 are recoverable. None is inconsistent, and no origin needs re-estimation for continuity.**

| Chain | Payloads | Live-rule walk | Cache-hit walk | Replay through the pinned `run_chain`, live-replay cache, **estimation refused** |
|---|---|---|---|---|
| FEDFUNDS MSAR | 626 | **626 / 626**, 0 unreachable, complete | 2 (624 unreachable) | 626 from cache, **0 estimations**, 49 failed and 577 valid, records equal to payloads at every origin, payload bytes unchanged |
| UNRATE 180 MSAR | 257 | **257 / 257** contiguous prefix of 764, 0 unreachable | 229 (28 unreachable) | 257 from cache, **0 estimations**, 2 failed and 255 valid, records equal to payloads, bytes unchanged |

The cache-hit walk reproduces the production failure exactly (2/624 and 229/28), which confirms the diagnosis on the real data. UNRATE is incomplete only because the session stopped; it resumes at origin 258.

## 5. Correction (item 4): orchestration only; pinned code unchanged

**`walk_chain(..., semantics="live")`** is the new default and carries the warm start by the pinned **live** rule, using `live_warm_after()`. `semantics="cache_hit"` remains, for diagnostics only.

**`live_replay_class()`** subclasses the pinned `RefitCache`. It is a compatibility layer: an explicit, documented replay rule.

- For each chain, identified by the constant fields of its cache keys, it tracks the warm start the live branch held, at full precision. The precision matters: a refit after a resume must start from exactly the same values.
- **On a hit**, it returns the stored payload unchanged except for `warm_payload`, which becomes the live state: the previous usable fit's, if this fit failed. The pinned `run_chain` then derives exactly the live successor key. If a resume has to estimate, it starts from exactly the live warm start.
- **On a miss** followed by `put` (a fit estimated now), the state advances by the same live rule.
- **A request whose predecessor is not the live state raises.** A chain can never be silently forked.
- **Records, parameters, forecasts, statuses and reason codes** are served exactly as stored. Nothing on disk is rewritten.

**Where it is used:**

| Path | Before | After |
|---|---|---|
| Worker resume (`stoppable_refit_cache`) | pinned `RefitCache` (cache-hit rule) | live-replay subclass |
| Worker post-run validation, preflight, certify, aggregation walk | cache-hit walk | live walk |
| Final assembly (`r1_tierb_aggregate.assemble`) | pinned `rescore.RefitCache` | `live_replay_in_pinned_workflow()`: for the duration of assembly, the name `rescore.RefitCache`, which `PublishedRescorer` instantiates for approved chains, is the live-replay subclass; still under `no_estimation_allowed()` |
| New read-only tool | — | `colab/r1_tierb_continuity_check.py`: verifies, restores, walks both ways, reports the first mismatch, replays with estimation refused, and computes the agreement; writes nothing to Drive |

**Why this is faithful.** The live rule is the pinned engine's own estimation rule: every payload of an uninterrupted chain is keyed by it, as all 883 B2 payloads show. Replaying by that rule reproduces exactly what the estimation computed. It changes no method, optimizer, start set, failure rule or stored result.

**Not changed:**
- pinned scientific code (`code/src`, `code/tools`, configs and the lock are identical to `8aaa421`; checked by test);
- the original fit cache and its replay (`_OriginalOnly`);
- the Tier A archive, published results and existing checkpoints.

## 6. Tests (items 5 and 6)

`code/tests/integration/test_r1_tierb_warm_continuity.py` uses the pinned engine on a real MSAR(1), K=2 chain of 5 origins in which origin 2 fails.

- **How the failure is induced:** the real outcome is marked `failed` with NONCONVERGENCE and no warm payload, exactly as failed MSAR payloads are stored. A second variant keeps the failed fit's warm payload, which the live rule must still ignore.
- The chain is: successful fit, **failed fit**, then three more successful fits.

| Test | Shows |
|---|---|
| reference chain | success, failure, success; the failed payload stores no warm start |
| the defect: cache-hit rule | the cache-hit walk stops after the failed origin (2 reached, 3 unreachable); the live walk is complete and **equals the written key sequence exactly**; the mismatch report gives an absent key with empty predecessor and a present live key, preceded by a failed status |
| the defect: plain pinned replay | with estimation forbidden it raises `EstimationForbidden` (assembly would fail); with estimation allowed it **re-estimates** after the failure (duplicate estimation) and forks the chain |
| live replay | the whole chain from cache with **zero estimations**; records (parameters, status, reason codes, loglik) and forecasts equal to the uninterrupted run; payload bytes unchanged |
| interrupt, restore, resume (×2 variants) | stop after origin 3 (past the failure), commit a checkpoint, delete the VM folder, restore from "Drive" into a fresh runtime (3 payloads, live walk contiguous), resume. Result: **from_cache 3, only 2 estimations, payloads identical to the uninterrupted run** (except the recorded fit time) |
| assembly with estimation forbidden | through `rescore.RefitCache` as `PublishedRescorer` builds it, under `no_estimation_allowed()` and the hook: 5 from cache, 0 estimations, 1 failed, records and forecasts equal; the hook is undone afterwards |
| forked request | the replay layer refuses a key whose predecessor is not the live state |

**Results:** the 8 new tests pass, and the 90 existing Tier B tests pass.

**Real data:** the two B2 chains and the B1 chain, as in §4 and §7.

## 7. B1 (item 8)

B1 checkpoints at the time of download (B1 session `…601058` is active and was not interfered with):
- 6 checkpoints and 86 payloads: 68 from session `…3706dd`, plus 18 after the resume;
- live walk 86/86, cache-hit walk 86/86, 0 unreachable;
- replay with estimation refused: 86 from cache, 0 estimations;
- agreement: **86/86 `reproduced`** against the original.

**No failed fit yet**, so the two rules coincide, and the B1 resume (old code) was not affected.

`progress.json` named a checkpoint 00007 that was not yet listed. It was committed between the listing and the download; the file's size changed during the download. Nothing is missing.

**Risk.** The original B1 chain fails at origins **454** (2010-09-01), 471 and 614.

- If the re-estimation also fails there, the **running session** keeps estimating correctly, because the live branch is used. But under the old orchestration its end-of-run validation will reject the chain, exactly like B2: exit 1, then supervisor exit 2. The data remain recoverable, as B2's are.
- **The real danger is a resume past a failed origin with the old orchestration.** It would fork the chain: a cold-start re-estimation and duplicate fits.
- **Requirement:** before any further B1 session, switch B1 to the corrected orchestration commit.

## 8. Scientific findings that must not be suppressed (items 10 and more)

### FEDFUNDS failed fits, 49 against 52

The difference is explained origin by origin by the agreement report:

- **3 origins** that failed originally are `fragile` now: **1980-01-01, 1981-05-01, 1981-06-01**. All three had `NONCONVERGENCE;SINGULAR_COV` originally and have `SINGULAR_COV` or `LOW_OCCUPANCY` now.
- **No new failure.** So 52 − 3 = 49.
- 5 other failed origins stay failed with different reason codes: 1980-05-01, 1981-02-01, 1981-04-01, 1981-07-01, 2011-06-01.

**FEDFUNDS agreement:**
- **583 reproduced exactly**;
- **29 optimizer sensitivity**;
- **14 classification changes**;
- status `COMPUTATION_COMPLETE_REVIEW_REQUIRED`.

The changed failure count remains a review item.

**UNRATE 180 agreement** (257 origins so far):
- **251 reproduced**;
- **6 classification changes**;
- original failures over the same origins: 2, against 2 now.

### Divergence from the original is concentrated right after failed origins

In both B2 chains the **first** origin that differs from the original is the origin **right after the first failed fit**: FEDFUNDS 1974-08-01, UNRATE 1982-01-01.

- **What happened there:** the re-estimation used the live warm start (`start_used = warm`). The original reported a deterministic start (`deterministic_p0.9`, `deterministic_p0.95`) and a **lower** log-likelihood (FEDFUNDS 1974-08-01: new − original = +8.79).
- **Where the FEDFUNDS divergences fall:**
  - **33** of the 43 origins that don't reproduce are right after a failed origin, against **10** elsewhere;
  - elsewhere, 567 of 577 reproduce exactly.
- **No code difference explains it:** the original run (`46a5318`) and the pin (`8aaa421`) have identical forecasting and model code, so the rule was the same.
- **Hypothesis, not established:** the original Part 8 run was itself resumed from its fit cache. Its cache-hit branch reset the warm start after failed origins and re-estimated some post-failure origins from cold starts.
- **Why it is only partial:** the original records also show the `warm` start after some failures (FEDFUNDS 9 of 52, UNRATE 300 1 of 3), so the reset was not uniform. Confirming it needs the original fit cache (it would show forked payloads) or new estimation. Neither was done here.
- **Treatment:** these differences stay `optimizer_sensitivity` or `classification_changed` in the agreement report, and the batch stays `COMPUTATION_COMPLETE_REVIEW_REQUIRED`. They are not suppressed.

### Possible effect on the R1 chain classification (to verify; not changed)

The R1 workflow replays the **original** cache with the same cache-hit rule (`_replay_from_cache` with `_OriginalOnly`). A warm-started chain whose original cache is complete under the live rule would replay only to its first failed origin and be classified "not cached".

**Suggested non-estimating check:** walk each R1 "unavailable" or "approved" MSAR/STAR chain through the original fit cache with `walk_chain(semantics="live")`. I have not run it, because the original cache is only on Drive, and I have changed nothing in the classification.

## 9. Proposed procedure (requires your approval)

1. **Review** this correction (orchestration commit in §11). The notebooks are re-pinned to it.
2. **Independent check on the real Drive mount**, read-only, with no estimation:
   ```
   python colab/r1_tierb_continuity_check.py --batch B2 --drive-root $DRIVE_ROOT \
       --code-dir <pinned>/my-thesis/code --original <original output> \
       --work /content/continuity --report /content/continuity/B2.json
   ```
   Expected: FEDFUNDS 626/626 and UNRATE 257/257 under the live rule; 0 unreachable; 0 estimations.
3. **Restarting B2** (after approval): run the B2 notebook at the corrected commit.
   - FEDFUNDS is complete, so nothing is estimated for it.
   - UNRATE resumes at origin 258. Its 257 committed origins, which include 2 failed fits, are served by the live-replay cache.
   - Certification then proceeds as before.
4. **B1:** use the corrected commit for its next session. The active session needs no action.
5. **Aggregation** (later, separately authorised) replays all approved chains by the live rule with estimation refused.

## 10. Approvals needed

- (a) The live-rule replay layer as the orchestration's replay semantics for Tier B. It is not a methodology change: it is the pinned estimation's own rule. Nothing in the scientific code is changed, so no methodology authorisation is requested.
- (b) Restarting B2 at the corrected commit.
- (c) Whether to investigate the original run's post-failure behaviour (§8) and the R1 classification check before aggregation.

## 11. Files

- `colab/r1_tierb.py`: `live_warm_after`, `predecessor_hash`, `chain_identity`, `walk_chain(semantics=…)`, `continuity_report`, `live_replay_class`, `live_replay_in_pinned_workflow`; the stoppable cache now uses the live-replay class.
- `colab/r1_tierb_aggregate.py`: assembly runs inside `live_replay_in_pinned_workflow()`.
- `colab/r1_tierb_continuity_check.py`: the new read-only tool.
- `code/tests/integration/test_r1_tierb_warm_continuity.py`: the new tests.
- `reports/part8/corrections/r1/evidence/`:
  - `tier_b_continuity_B2_20261105.json`
  - `tier_b_continuity_B1_20261105.json`
  - `tier_b_drive_evidence_inventory_20261105.csv`
- The three notebooks, re-pinned to the corrected orchestration commit (defaults unchanged).
