# Part 8 integration dry run: stage-2 refusal, root cause and fix

Date: 7 November 2026.

**Scope.** This is an orchestration fix only.

**Not done:**
- no model was estimated;
- no release was made, nothing was published, and Part 9 was not started.

**Unchanged:**
- the scientific pin `8aaa4217…`;
- the published results;
- the original fit cache;
- the Tier A/B checkpoints and certificates.

**Safeguards.** The strict cache-integrity check is kept, and extended (§4).

[C] marks results computed or reproduced in this round. Evidence: `evidence/integration_stage2_cache_fix_20261107/`.

## 1. The failure

**The run.** Colab session `integration-20261107T184004Z-93c0f8` (orchestration `43903d4`).
- Preflight passed.
- The base tree passed (461 files).
- Stage 2 stopped after about 11.5 minutes with `IntegrationError: the merged refit cache changed during assembly`.

**Exported records.** Retrieved from Drive and saved under `colab_failure/`. Their sha256 values equal those in the session's `export_manifest.json`.
- The console log shows both workflow passes ran: the HLZ/DM warnings of the legacy and corrected passes are present.
- The integrity check after assembly failed.
- The export holds the assembly records but no file listing of the merged cache. The old check compared a single digest and recorded no diff. **The exact Colab file difference was therefore not captured.** It was reproduced locally (§2), and the new code records it (§4).

## 2. Reproduction and exact file-level difference [C]

**Method.** I reproduced the failure with the **unmodified** assembly code (worktree of `a21fdf2`):
- the real base tree;
- the original cache (18,964 payloads, digest `7e283de3…`);
- a merged refit cache built as `merge` builds it: the Tier A archive (sha256 `df73c295…`, 5,597 payloads) plus the 1,390 B2 payloads verified against the B2 certificate;
- the pinned workflow at a clean worktree of the pin, with legacy and corrected passes.

The B1 and B3 checkpoints are on Drive only, so 10 of the 17 chains were used. The mechanism does not depend on which chains are present (§3).

**Result** (`reproduction_old_code/cache_diff.json`, with full listings after merge and after assembly):

| | Files | Listing digest |
|---|---|---|
| After merge | 6,987 (all payloads) | `1d07c553…` |
| After assembly | 6,988 | `f51679ba…` |

| Change | Path | sha256 |
|---|---|---|
| **added** | `README_R1_REFIT_CACHE.txt` (316 bytes) | `0d4b46635d9d1c1a0a6a979a297ab4c9a5c02f6676f9ce2b59c698127d4552ab` |
| removed | — | — |
| modified | — | — |

**Checks on the reproduction:**
- **Payloads:** all 6,987 payloads are byte-identical after assembly to their sources (Tier A archive members and B2 checkpoint payloads).
- **The README's origin:** the added README is byte-identical to the pinned `REFIT_README` text, and to the README member that the Tier A archive itself contains. `restore_tier_a` deliberately extracts payloads only, so that README is absent after the merge.
- **Estimation:** `estimations_performed` is empty in both workflow passes; no estimation took place.

## 3. Root cause and whether it is the only one [C]

**Mechanism.** `PublishedRescorer.__init__` (pinned `rescore.py` line 209) constructs `RefitCache(<refit cache>/fits)` for the approved chains. The pinned `RefitCache.__post_init__` (lines 151–157) **unconditionally writes** `README_R1_REFIT_CACHE.txt` into that folder. The dry run's replay hook (`r1_tierb.live_replay_in_pinned_workflow`) substitutes a subclass of `RefitCache`, which inherits that constructor. Each of the two workflow passes therefore wrote the README into the merged cache, after the post-merge listing had been taken. The local mtime matches the start of the corrected pass.

**Why no earlier test saw it.** The replay tests compared only the JSON payload files (`payload_files`), never the whole folder.

**The only cause.** Every pinned code path that can write into a refit-cache folder during replay:

| Path | Effect during the dry run |
|---|---|
| `RefitCache.__post_init__` → `README_R1_REFIT_CACHE.txt` | **written on every construction (the cause)** |
| `FitCache.__post_init__` → `mkdir(exist_ok=True)` | no change: the folder already exists |
| `FitCache.put` (via `RefitCache.put`) | reached only after `fit_and_forecast` (`rolling.py` line 325), i.e. after an estimation, which `no_estimation_allowed` refuses; `estimations_performed` is empty |

**Agreement with the reproduction.** Exactly one file was added; no payload was added, removed or modified.

**Caveat on Colab.** For the Colab run itself this is established by the shared mechanism and by its digest-only failure. With the old code, its file-level diff was not recorded.

## 4. The fix (orchestration only)

**The adapter.** `r1_integration_common.readonly_refit_class()` is a genuinely read-only cache for replay. It is built on the existing `r1_tierb.live_replay_class(rescore.RefitCache)`, so the served payloads and the live warm-start state are exactly those used before. It differs in two ways:
- **Constructor:** it records the folder and refuses a missing or disabled one. It writes nothing: no README, no `mkdir`.
- **`put`:** it refuses.
- `get` and `path_for` are the pinned ones.

**Where it is used:**

| Use | Implementation |
|---|---|
| Both workflow passes | `assemble` uses `ic.readonly_refit_replay()` in place of `r1_tierb.live_replay_in_pinned_workflow()`; the `rescore.RefitCache` that `PublishedRescorer` constructs is the read-only adapter |
| Dependent-output replay (stage 3) | `r1_integration_dependents.replay` uses the same adapter, in place of the B1 replay; estimators refused, fit calls counted (must be 0), every origin from the cache |

**Integrity checks: kept strict and extended.** Every file is compared, payload or not; nothing is excluded.
- After merging, `record_cache_listings` saves the full file listings of the merged refit cache and of the original cache: `dryrun_report/cache_integrity/merged_refit_after_merge.csv` and `original_cache_before_assembly.csv.gz`.
- `check_cache_listings` requires both folders to hold exactly those files, byte for byte, at four points:
  - after assembly (stage 2);
  - before and after the dependent-output replay (stage 3);
  - after validation (stage 4, folded into A1).
- On any difference, the run stops. The **full file-level diff** (every added, removed and modified file, with sha256) is written to `dryrun_report/cache_integrity/*_diff_*.json`, which the notebook exports.

**Unchanged:** the pinned code, the methodology, the statistical procedures and every warning. No warning filter exists anywhere in the dry-run code.

## 5. Tests [C]

**Regression tests** (`code/tests/integration/test_r1_tierb_warm_continuity.py`). They use a synthetic MSAR chain with an induced failed origin, and a merged copy holding payloads only:

| Test | Shows |
|---|---|
| `test_old_live_replay_hook_writes_the_readme_and_fails_the_strict_check` | **the old implementation triggers the failure**: exactly one added file, `README_R1_REFIT_CACHE.txt` with the pinned README's sha256; the strict check refuses and writes the diff |
| `test_readonly_replay_keeps_the_cache_exact_and_reproduces_the_old_replay` | **the fix keeps the cache exactly** (strict check passes), with no estimation; records and forecasts are identical to the old replay and to the reference chain |
| `test_readonly_adapter_refuses_writes_and_never_creates_a_folder` | refuses `put` and a missing folder; nothing is created |
| `test_dependent_output_replay_is_read_only_and_reproduces_the_chain` | stage 3's replay writes nothing and reproduces the chain |

**Unit tests** (`test_r1_part8_integration.py`):
- the diff reports added, removed and modified files with sha256;
- the stage check is strict for non-payload files, records the diff, and also covers the original cache;
- assembly and stage 3 use only the read-only adapter.

**Full suites:** see the commit message.

## 6. Local rehearsal with the fix [C]

**Setup.** This rehearsal runs through the **real `stage_aggregate`**; the earlier rehearsal had bypassed it. Then stages 3, 4 and 5. Only the Drive-dependent calls (`discover`, the certificate-file check, `merge`) were replaced by local equivalents. Same 10 of 17 chains.

**Cache integrity** (`rehearsal_fixed_code/`):

| Point | Merged refit cache | Original cache |
|---|---|---|
| After merge | 6,987 files, `1d07c553…` | 18,964 files, `7e283de3…` |
| After assembly | unchanged | unchanged |
| Before and after stage-3 replay | unchanged | unchanged |
| After validation (A1) | unchanged | unchanged |

**Acceptance.** Identical to the earlier rehearsal:
- A1, A5, A6, A7, A9, A10, A11, A12, A13 and A15 pass;
- A3, A4 and A8 fail only because 7 chains are absent locally;
- **0 unexplained** among the attributed cell changes.

**Old against fixed outputs** (`old_vs_fixed.json`): every file of the legacy, corrected, raw-corrected and assembled trees, and of the stage-3 release, was compared.

| Tree | Files | Byte-identical | Differing only in provenance (run ID, timestamps) | Other differences |
|---|---|---|---|---|
| legacy | 146 | 53 | 93 | **0** |
| corrected | 148 | 54 | 94 | **0** |
| corrected (unreconciled) | 93 | 51 | 42 | **0** |
| assembled release | 465 | 370 | 94 | `output_inventory.csv` only: its sha256 column, for exactly the provenance-only files |
| stage-3 release | 465 | 364 | 100 | `output_inventory.csv` only: its sha256 and bytes, for exactly the provenance-only files |

**Further results:**
- The 3,117 reconciliation cause records are identical.
- Fit records replaced: 43 + 6 (B2), 0 for the other chains, as before.
- **No new scientific-output difference.**

**Warnings.** The HLZ, DM-HLN, state-loss-regression and statsmodels warnings are the same messages with the same counts in the old and fixed runs (`warnings_old_vs_fixed.txt`). They remain for scientific review: overflow and invalid values in the HLZ/DM variance terms, and a rank-deficient constraint covariance in the state-dependence Wald tests.

## 7. For the next Colab run

**The notebook.** It is regenerated with the new orchestration commit (see the commit message and the final message of this round). Launch instructions are unchanged (`part8_integration_dryrun_implementation.md` §9). Use a **new** session folder.

**If it is refused again:**
- `dryrun_report/failure.json` names the stage;
- any cache difference is listed file by file in `dryrun_report/cache_integrity/`;
- both are exported to Drive.
