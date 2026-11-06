# Part 8 integration dry run: implementation, findings and launch instructions

Date: 6 November 2026. **Status: implemented and tested; NOT executed in Colab.** The full dry run is for you to run after independent review.

**Not done, under this authorisation:**
- no model was estimated;
- nothing was aggregated into a release or published;
- no final release was made, and Part 9 was not started.

**Unchanged:**
- the scientific pin `8aaa4217…`;
- the approved methodology;
- `output/`, `output_staging/`, the releases `0573a8c`, `3bd24c4` and `292227e`;
- the Tier A/B checkpoints and certificates;
- `approved-specs/` and `source-materials/`.

[C] marks results computed in this round. [P] marks a plausible reading that is not proven.

## 1. Authorisation applied

| Item | Applied as |
|---|---|
| B1 staged baseline correction | Base tree = published `output/` + `output_staging/r1_b1_unrate_msar_20261106/`. All 461 files are verified against `STAGED_FILES.csv` and the published hashes. |
| **D1** | Both B2 MSAR chains are integrated as **candidates** under the approved live warm-start rule. Their 20 classification changes and 29 optimiser sensitivities are carried verbatim into the plan and the acceptance report. Not scientific approval. |
| **D2** | Every F4.8 whose plotted inputs change is re-rendered by the pinned code. **All six** F4.8 figures are then re-rendered from the integrated table and compared byte for byte (A11). |
| **D3** | Deferred. The code has no publication path: it refuses if `CONFIRM_PUBLISH` is set, and it never reads a token, commits, pushes or writes outside its work folder. |
| **F8** | **Reconciled: not authorised.** See §2. |
| **A15** | **Corrected:** see §3. |

## 2. F8: authorisation discrepancy (task 1)

**The discrepancy.**
- *What happened:* F8 (F3.4 main-panel presentation) was raised for confirmation in `figure_review.md` (2 November) and never confirmed.
- *The pinned code:* the flag `f8_readable_main_panel` defaults to **on**.
- *Where it ran:* the recorded correction flags show F8 active in releases `3bd24c4` and `292227e`. `0573a8c` predates F8.
- *The wrong statement:* the first version of the integration plan listed F8 as approved.

**Resolution (scope only):**
- The dry run switches F8 **off**. It applies only F1, F2, F3, F4 and F7.1 (`r1_integration_common.CORRECTION_FLAGS`).
- The corrected run must report exactly that flag set, otherwise it refuses.

**Corrected documents:**
- `CORRECTIONS.md`: F8 status note;
- `part8_final_integration_plan.md`: §1 table and the new §7.

**Consequences.**
- The dry run's F3.4 figures will differ from those of `3bd24c4` and `292227e`. They match F1–F4/F7.1 only.
- Switching F8 on requires your confirmation, and nothing else changes when it is switched on.

## 3. A15 corrected (task 2)

**Old wording.** The first version tied `REVIEW_REQUIRED` to "while D1 is open".

**New rule.**
- The status follows mechanically from the certificates and the gates.
- Every certificate review item and every reported sensitivity is carried verbatim into the plan.
- **Authorising D1 does not clear them.** A completed or internally consistent computation is not scientific approval.
- With B2's review items, the expected status is `COMPUTATION_COMPLETE_REVIEW_REQUIRED` (exit 4).

**Implementation and tests.** `r1_integration_validate.check_status`. Tests: it refuses a status, plan or approval field that hides or drops any of the review items.

## 4. What was implemented (tasks 3, 6, 7, 8)

| Stage | Code | What it does |
|---|---|---|
| 0 preflight | `r1_part8_integration.stage_preflight` | Refuses `CONFIRM_PUBLISH`. Both checkouts must be clean at their commits; the pin must be an ancestor of the orchestration commit. Checks frozen data `7e7dc769…`, config `949fcd76…` and rendering (matplotlib 3.11.2 defaults). The three latest certificates on Drive must have the reviewed sha256 values (`certificates/MANIFEST.csv`), and the aggregator's own `discover` checks apply. Checks the original-cache payload digest `7e283de3…` (18,964 payloads) and the Tier A archive `df73c295…`. Extracts the reference releases `292227e` and `0573a8c` from git objects. Takes a sha256 listing of every protected input. |
| 1 base | `stage_base` | Published + B1 overlay. Refuses any extra, missing or altered file. |
| 2 aggregate | `stage_aggregate`, `assemble`, `reconcile_chain_aware` | Merges Tier A and the certified Tier B checkpoints (conflicts refuse). All 17 chains are walked. The pinned workflow runs in legacy, then corrected mode, under `no_estimation_allowed` with the live replay, F8 off. Reconciliation is chain-aware (§5.1), then the pinned assembly runs. The merged cache must be unchanged afterwards. The aggregator's gates apply; T4.2 uses the pinned floating-point convention (§5.4). The plan is written under `--work` only. |
| 3 dependents | `r1_integration_dependents` | The 17 chains are replayed with the estimators refused and fit calls counted. Rebuilds **fit records** (a record is replaced only where the re-estimate does not reproduce it), the **T4.7 registry** and **counts**, the **Wald rows** of `all_test_results` (§5.2), the **T4.6 summary**, **F4.8** (D2), and the inventory and file comparison. Every builder first reproduces the base values from base inputs. |
| 4 validate | `r1_integration_validate` | A1, A3–A13 and A15 (§6). Cell-level change sets against published, B1-staged and Tier A. Every changed cell is attributed (§6, A12). **Any unexplained difference stops the run: REFUSED.** |
| 5 claims | `r1_integration_claims` | Each of the 24 claims is compared with the release it was written against (`0573a8c`). Each claim gets a mechanical transition and is never upgraded; jury IDs are mapped. Report lines quoting changed values are listed as a heuristic aid. Nothing is edited. |
| finalize | `finalize` | A2 (protected inputs unchanged, measured after everything) and A14 (claims) are added. Writes `acceptance.json`. Exit 0 / 4 / 1. |

**Write boundary.** Every write goes through `inside(work, …)`. Protected inputs are hashed before and after:
- the published output;
- the repository's `output/`, `output_staging/`, `approved-specs/`, `source-materials/` and the evidence and certificates;
- the local original cache;
- the Tier A archive;
- the Drive batch namespaces and certificate folders;
- the Drive original-cache archive folders (passed by the notebook).

The only Drive write is the notebook's export cell. It writes a new folder and refuses if that folder exists.

## 5. Findings made while implementing

### 5.1 The pinned reconciliation would discard B2's effect [C]

**The mechanism.** The pinned `workflow.reconcile` restores the base text in every cell where the legacy run (corrections off) and the corrected run agree. It assumes the legacy run reproduces the base. B2's chains do not reproduce the published records, so in cells that the corrections leave untouched it would restore the **superseded** value. Example: FEDFUNDS T4.1 MSAR `n_failed` would print 52 instead of 49.

**The fix.** The dry run uses `reconcile_chain_aware`:
- a cell is restored only where the legacy value also reproduces the base, within the pinned 1e-9 tolerance;
- otherwise the re-estimated value is kept and recorded with its cause.

**Test.** A regression test shows the pinned function printing 52 and the dry run keeping 49.

**Scope.** This changes orchestration only. The pinned code and the methodology are unchanged. [P] It did not matter for the Tier A release, because closed-form AR re-estimates reproduce exactly.

### 5.2 Stale Wald rows in `all_test_results.csv` in all three provisional releases [C]

**The gap.** The workflow regenerates T3.5 (state-dependence regressions) but only appends Zivot–Andrews rows to `all_test_results.csv`. The state-dependence and joint Wald rows are copied from the base.

**The effect.** In `0573a8c`, `3bd24c4` and `292227e`, all **24** UNRATE Wald rows (ARMA, MSAR and STAR vs AR × 4 horizons × 2 statistics) still carry the published values, while their T3.5 rows changed under F1. The NaN rows of CPI and M2SL STAR h=12 are consistent by design: there is no test row when inference is unavailable.

**The fix.** Stage 3 rebuilds every Wald row from the release T3.5, after reproducing all 134 base rows from the base T3.5. In the local rehearsal, 24 rows were rebuilt and one 5% decision changed (UNRATE ARMA vs AR).

**Classification.** An implementation error (omitted regeneration) under §6A, recorded in the correction note.

### 5.3 Chain blocks in the fit records are located by specification and refit dates [C]

**What the rehearsal found.** B1's block rule (`stage_block`, by window span) selects the wrong block for AR chains. For AR models the recorded window is the effective sample after the lags. For example, it picked the 625-record baseline FEDFUNDS block for `T4.1:FEDFUNDS|AR`, whose own block has 626 records and the 71 failed fits.

**The fix.** Stage 3 uses `stage_block` only when its block has the chain's specification label and refit dates. Otherwise it uses the unique contiguous run that does.

**Duplicates.** A robustness chain that duplicates the baseline chain is accepted only if every record reproduces; in that case nothing is replaced.

**Check against published records.** For all 17 chains, including the 7 that could not be replayed locally, exactly one published run matches. Its failed-fit counts equal the certificates' and Tier A's.

### 5.4 T4.2 against the Tier A release: last-digit platform differences [C]

**The issue.** The aggregator demands T4.2 be byte-identical to the Tier A release, which was computed in Colab. Locally, 2 of 120 cells differed in the 17th significant digit (relative difference 1.7e-16), in cells the corrections recompute.

**The handling.** The dry run applies the pinned R1 convention:
- `equal_within_fp_tolerance` (every non-numeric cell identical, numbers within 1e-9) is accepted and **reported separately with every differing cell**, never as identical;
- anything larger refuses.

This is `t42_tolerance`, and it is tested both ways.

### 5.5 T4.6 summary [C]

The T4.6 ARMA comparison columns depend on the baseline ARMA forecasts. Stage 3 recomputes them with the pinned arithmetic, after reproducing the base values. In the rehearsal they were unchanged. The column stays under check because F1 could affect it.

## 6. Acceptance criteria as implemented

| ID | Check |
|---|---|
| A1 | `estimations_performed` is empty in both workflow runs. Stage 3 replays with fit calls counted (must be 0). The merged refit cache is unchanged. |
| A2 | Protected-input listings before and after are equal (measured last). |
| A3 | Chain sources are exactly 17 re-estimated, 17 cache, 26 unavailable and 48 published. No rule-sensitive chain is served from the cache. No unavailable chain is affected by a correction. The B1 chains are re-read from the base. Legacy and corrected sources are equal. |
| A4 | No `original_retained_pending_estimation` row remains. |
| A5 | Legacy reproduces every base file not fed by a re-estimated chain. |
| A6 | T4.2 equals the Tier A release: identical, or within floating-point tolerance and reported. |
| A7 | The 17 cache chains are identical, origin by origin, to their published records (status, codes, loglik). |
| A8 | Per-chain statuses equal the certificates (Tier B) and the Tier A expectations. Replaced records are exactly B2's 43 + 6 non-reproduced origins from the direct review; zero for all other chains. |
| A9 | The baseline `forecasting:UNRATE\|MSAR` and `T4.8:UNRATE\|240:MSAR` records equal the B1-staged records: 704 records, 440/258/6 adequate/fragile/failed, B1 provenance. The origin audit is unchanged. |
| A10 | Dependents: T4.7 counts equal a recount of the final fit records. Registry rows outside the patched blocks are unchanged and in order. Builders were validated against the base. Every inventory hash is correct. |
| A11 | All six F4.8 figures equal renderings of the integrated table. Every other changed figure was regenerated by the workflow (with a sidecar) or re-rendered in stage 3. |
| A12 | Every changed file, row and cell against the base has a cause. A chain effect is allowed only in the exercises that the re-estimated chains feed. A removed MCS row must be an F2 placeholder replaced by model rows. **Unexplained: 0 required.** |
| A13 | Every changed row carries the dry-run run ID. The release manifest records pin, config hash, data hash, run ID, timestamp and a clean tree. |
| A14 | All 24 claims are reassessed; any changed evidence gives REVIEW_REQUIRED; every jury ID has a status. |
| A15 | §3. |

## 7. Local partial rehearsal [C]

**This is not the dry run.** It used:
- the real base tree, the original cache and the Tier A archive (sha256 verified);
- the B2 payloads (10 of the 17 chains; the B1 and B3 checkpoints are on Drive only);
- the real pinned workflow at a clean worktree of the pin.

**Evidence:** `evidence/integration_rehearsal_20261106/`. Assembly took 7 minutes locally.

| Criterion | Rehearsal | Why |
|---|---|---|
| A1, A5, A6, A7, A9, A10, A11, A12, A13, A15 | pass | — |
| A3, A4, A8 | fail, as expected | 7 chains not available locally (B1 and B3), so their exercises stay pending |

**Results:**
- **A12:** all 3,354 changed cells against the base were attributed; 0 unexplained. Causes: 3,017 correction, 333 re-estimated-chain records, 51 Wald, 4 T4.7.
- **Fit records:** B2 replaced exactly 43 + 6 records; the 8 Tier A chains replaced none.
- **T4.7 counts:** FEDFUNDS MSAR failed 52 → 49 and fragile 2410 → 2413; UNRATE MSAR adequate 2115 → 2120 and fragile 1385 → 1380.
- **F4.8:** all six reproduced from the base; only F4.8_UNRATE re-rendered.
- **Claims:** 9 claims have unchanged evidence against `0573a8c`; 15 require review (7 with decision-like changes, 7 with value changes, 1 not machine-checkable). These are rehearsal numbers only. Several reflect the B1 correction and F8 off, and the complete run will differ.

## 8. Tests [C]

**New tests (63 pass, 1 skipped until the notebook is generated):**
- `test_r1_part8_integration.py`: base tree, certificates, publication refusal, empty work folder, no publish code, chain-aware reconcile against the pinned one, exit codes, A2, F8 off, T4.2 tolerance;
- `test_r1_integration_validate.py`: A3, A8, A12 (including F2 placeholders and append alignment), A13, A15, registry;
- `test_r1_integration_dependents.py`: record rule, T4.7 counts, Wald, T4.6, F4.8, block location;
- `test_r1_integration_claims.py`: claims, jury, report lines, notebook.

**Full unit suite:** see the commit message.

## 9. Preflight and launch instructions

**Before launching.**
1. Do not run anything else that writes under `DRIVE_ROOT/baseline/r1_tierb_batches/`. The certificates there must still be the reviewed files, or preflight refuses.
2. Use a **standard CPU runtime**, preferably high-RAM.
3. Expected time: about 1–2 hours (two workflow passes, stage 3 replays, hashing of protected inputs).

**Launch.**
1. Open the notebook. The link and commit are in the final message of this round.
2. Keep the defaults: `RUN_DRY_RUN = True`, `EXPORT_TO_DRIVE = True`, `CONFIRM_PUBLISH = False`.
3. Check `DRIVE_ROOT`.
4. *Runtime → Run all.* Cell 1 mounts Drive. If a Colab secret `GITHUB_TOKEN` exists, it is used for read-only `git clone`/`fetch` only. The repository is private, so a read token is needed.

**Cells:**
- *Cell 2* verifies both checkouts and fetches the two reference release branches.
- *Cell 3* builds the approved environment and verifies the frozen data and the cache identity.
- *Cell 4* restores the original cache, read only, and asserts 18,964 payloads.
- *Cell 5* runs the dry run.
- *Cell 6* exports the reports to `baseline/r1_part8_integration_dryrun/<session>/`.

**Reading the result.** Cell 5 prints `DRY_RUN_STATUS: …`:

| Result | Meaning |
|---|---|
| `ACCEPTED_FOR_REVIEW_REVIEW_REQUIRED` (exit 4) | Expected. Every criterion passed; B2's review items stay open. |
| `REFUSED` (exit 1) | A check failed. Each failure is in `dryrun_report/acceptance.json` (criteria) or `failure.json` (a stage stopped). Nothing is published either way. |

**Afterwards.** Send me the session folder name printed by cell 6. I will retrieve the exported reports and review them with you.
