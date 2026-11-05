# R1 Tier B: audit of the original MSAR divergences and of original-cache availability

Date: 5 November 2026.

- **Approved scope:** read-only, non-estimating.
- **What was done:** no model was estimated; nothing on Drive, in the original results, the original cache, Tier A or any checkpoint was changed; the scientific pin is unchanged; no aggregation or publication was run.
- **Conclusion:** this audit finds an implementation artifact in the **published** Part 8 results that reaches beyond the R1 Tier B plan. Following CLAUDE.md §4 and §6A, I stop here and propose an amendment (§6) for independent review. **No methodological or chain-selection change has been made.**

Labels used below:
- **[C] Confirmed:** shown directly by data.
- **[P] Plausible:** consistent with all evidence but not directly shown.
- **[U] Unresolved:** not settled by the evidence available here.

## 1. Evidence used

| Source | Content | Access |
|---|---|---|
| Published original results (`output/`, run `baseline-20261030T173044-949fcd76`, code `46a5318`) | `models/fit_records.parquet`, whose MSAR `diagnostics` list **every start tried** with its objective; `logs/runtime_log.csv`; `forecasts/forecast_origin_audit.csv` and `robustness/window_length_origin_audit.csv` (per-chain `from_cache`) | repository |
| Original fit cache, Drive `Part8_K3_InSample_2026-10-29/baseline/fit_cache/3413465b508bb844/` | **all 143 part listings: the complete inventory of 18,964 payload names, with the part and the write time of each** (`evidence/original_cache_audit_20261105/original_fit_cache_inventory.csv.gz`); payloads of **16 of the 143 parts** (7,969 of 18,964 payloads; parts 1, 24, 101, 131–143), downloaded read-only and checked against Drive sizes (`original_fit_cache_parts.csv`) | read-only |
| B1/B2 checkpoints | as in `tier_b_warm_start_continuity.md` | read-only |
| R1 chain sources | `replay_20261103T063749Z/corrected_r1_summary.json` (evidence commit `c5324b2`) | repository |

**Methods.**
- `colab/r1_original_cache_audit.py` (new, read-only) walks any copy of the original cache under both rules and compares every cached payload with the published record.
- `colab/r1_tierb_continuity_check.py` does the same for the Tier B checkpoints.
- Ad-hoc read-only scripts produced the CSV evidence files.

**Not available.** The original **final run's** own per-origin logs and its newly estimated payloads (§2.3).

## 2. Question 1: why the new MSAR estimates differ from the published ones

### 2.1 What the comparison shows

| Finding | Evidence | |
|---|---|---|
| The platform reproduces the original deterministic starts **exactly** | Objective of every deterministic start, new run against published: **969 / 969 identical** (FEDFUNDS 626, UNRATE 180 257, UNRATE 300 86) | [C] |
| Where both runs used the same warm start, they agree exactly | Warm-start objectives identical at 565/586 (FEDFUNDS), 249/255 and 85/85 origins; every difference is downstream of an earlier divergence | [C] |
| In the published records, an MSAR origin **lacks a warm start only right after a failed fit** | Across all 21 identifiable MSAR chains, origins without a warm start that do **not** follow a failed fit: **0**. Origins right after a failed fit without one: **T4.1 FEDFUNDS 39/52, T4.8 UNRATE 180 4/5, T4.8 UNRATE 300 2/3, baseline UNRATE 240 6/8** (`q1_published_msar_post_failure_starts.csv`) | [C] |
| The live re-estimation **always** offers the warm start there, as the approved rule D6 requires (warm start from the previous successful refit) | New run: post-failure origins with a warm start 52/52 and 2/2 | [C] |
| The missing warm start **explains the divergence exactly** | At the 39 FEDFUNDS post-failure origins where the published fit had no warm start: when the new run's best start was deterministic, the results are **identical (14/14)**; when it was `warm`, they **differ (25/25)** | [C] |
| The other 13 FEDFUNDS post-failure origins **with** a published warm start differ through inheritance | In all 13 the last usable fit before the failure already differed, so its warm vector differed (11 of them were themselves a no-warm refit) | [C] |

### 2.2 The original cache holds the warm-start (live) computation, not the published one

| | Original cache payload (earlier original session) | B2 re-estimate | Published record |
|---|---|---|---|
| FEDFUNDS MSAR 1974-08-01: starts | **warm**, det. 0.9, det. 0.95 | same | **det. 0.9, det. 0.95** |
| status, best start, loglik | failed, warm, **−100.368** | failed, warm, **−100.368** | failed, det. 0.9, **−109.162** |
| UNRATE 180 MSAR 1982-01-01: starts | **warm**, det. 0.9, det. 0.95 | same | **det. only** |
| status, best start, loglik | **adequate**, warm, **47.385** | **adequate**, warm, **47.385** | **fragile**, det. 0.95, **47.147** |

- **[C]** At both origins the cached payload and the B2 payload are identical in status, reason codes, parameters, log-likelihood, forecasts, start used and warm payload.
- **[C]** For T4.1:FEDFUNDS|MSAR, **all 626** live-rule keys are present in the original cache:
  - written 2026-10-30 07:31–10:57 UTC in one session, parts 101–121;
  - this key sequence is identical to B2's;
  - **none** of the 49 keys the cache-hit rule would request after a failed fit is present (`q2_live_keys_in_original_cache.csv`).
- **[C]** The published post-failure fits **without** a warm start exist **nowhere** in the original cache.

### 2.3 When and how the published results were produced

- **[C]** The cache was written by earlier sessions from 2026-10-29 14:57 to **2026-10-30 14:39** (part 143). The final run that produced the published outputs started at **2026-10-30 17:30**. No part was written after it, so none of its new fits were backed up.
- **[C]** The final run took 3,134 s wall and 7,370 CPU-s (≈2 CPU-h) for the whole robustness stage. The robustness chains' recorded fit times total about 49 CPU-h for the Tier B chains alone, so most robustness fits were **served from the cache**.
- **[C]** In the final run's own audit, chains with failed fits were only partly served from the cache:

  | Chain | Attempted | Failed | Served from cache |
  |---|---|---|---|
  | UNRATE MSAR 180 | 764 | 5 | 748 |
  | UNRATE MSAR 240 (robustness audit) | 704 | 11 | 699 |
  | UNRATE MSAR 300 | 644 | 3 | 499 |

  The baseline audit also records 13 cache horizon misses for UNRATE MSAR.
- **[C]** The published outputs contain **two different fits of the same chain**. At 1983-04, 05 and 06 the baseline UNRATE MSAR(240) chain and its identical T4.8 duplicate disagree: one is `failed` from the warm start (loglik ≈ 54.4); the other is `failed` from a deterministic start with **no warm start offered** (loglik ≈ −300).

**Explanation.**
- **[C] What diverged:** the published estimates at certain post-failure origins were computed without the warm start the approved rule prescribes. The earlier original session had computed those origins with it and cached them.
- **[P] Mechanism:** the final run replayed the chains from the cache through the pinned cache-hit branch. That branch resets the warm start after a failed fit, so the next origin's key was missing and it was re-estimated **without a warm start**. When the cold fit reached the same optimum to 10 decimals, later keys matched the cache again; otherwise the chain continued on a new path.

This explains every observation: the pattern exactly at failures, the exact 14/14 and 25/25 split, the inherited 13, `from_cache` below the attempted count, cold fits absent from the cache, and the disagreeing duplicates.

**[U] Not confirmed:**
- the final run's per-origin execution, because no per-origin log of it exists;
- the exact restart points of the earlier sessions;
- why horizon misses occurred in the baseline UNRATE MSAR chain.

No other explanation found fits the 14/14 and 25/25 result. A platform difference would also change deterministic starts, and all 969 are identical.

### 2.4 Scientific review items (kept, not suppressed)

- **FEDFUNDS MSAR, published against the live re-estimate:**
  - 583 origins reproduced, 29 optimizer sensitivity, 14 classification changes;
  - 49 against 52 failed: 1980-01-01, 1981-05-01 and 1981-06-01 were `failed` and are `fragile` now; no new failure.
- **UNRATE 180 MSAR** (257 origins so far): 251 reproduced, 6 classification changes.
- **Interpretation:** with this audit these differences have an identified cause, the published post-failure fits without the D6 warm start. They remain **review items**; the audit explains them but does not resolve them.

## 3. Question 2: chain availability in the original cache

### 3.1 Where the two rules can differ

The cache-hit and live rules request different keys **only after a failed fit** of a model that stores a warm start.

- **[C] STAR:** the published results contain **no failed STAR fit** (15,443 records: adequate or fragile).
- **[C] ARMA and AR:** they store no warm start.
- **[C] Consequence:** the defect cannot change the availability of any STAR, ARMA or AR chain.
- **[C] MSAR chains with any published failed fit:** only T4.1:FEDFUNDS, T4.8:UNRATE 180, T4.8:UNRATE 300 and UNRATE 240 (baseline and its T4.8 duplicate).

### 3.2 The 11 MSAR/STAR chains R1 classified "unavailable"

| Chain | Plan | Published failed | Final run served from cache | Original cache, cache-hit rule | Original cache, live rule | Finding |
|---|---|---|---|---|---|---|
| T4.1:FEDFUNDS\|MSAR | Tier B (B2, done) | 52 | — (no T4.1 audit) | **2** | **626 / 626 (complete)** | **[C] classified incomplete only because of the cache-hit rule.** But the cached chain is the live computation (= B2), **not** the published chain |
| T4.8:UNRATE\|180:MSAR | Tier B (B2, 257/764) | 5 | 748 | — | 257/257 checked; rest needs the remaining parts | **[U]** possibly complete under the live rule |
| T4.8:UNRATE\|300:MSAR | Tier B (B1, running) | 3 | 499 | — | 86/86 checked; rest unchecked | **[U]** |
| T4.1:FEDFUNDS\|STAR | Tier B (B3) | 0 | — | rules identical | rules identical | **[C] unaffected** |
| T4.8:UNRATE\|300:STAR | Tier B (B3) | 0 | 155 | 155 | 155 | **[C] genuinely incomplete**; matches the final run exactly |
| T4.8:M2SL\|180:STAR | unaffected (retained) | 0 | 51 | 51 | 51 | **[C] genuinely incomplete**; exact match |
| T4.8:M2SL\|300:MSAR | unaffected (retained) | 0 | 343 | rules identical | rules identical | **[C] unaffected** |
| T4.8:FEDFUNDS\|300:STAR, GDPC1 90 and 150 STAR, M2SL 300 STAR | unaffected (retained) | 0 | 0 | rules identical | rules identical | **[C] unaffected**; the final run estimated them entirely and nothing was backed up |

- **Why the zero-failure chains are unaffected:** with no failed fit in the cached prefix, both rules request the same keys and stop at the same missing payload. That is a logical consequence of the key construction and needs no further data.
- **The 14 unavailable ARMA chains** (4 in Tier B, 10 retained as unaffected): the defect cannot affect them, because ARMA stores no warm start. In the final run's audits ARMA was never served from the cache (`from_cache = 0`), so their unavailability is genuine.
- **The 17 "cache" chains:** they replayed completely under the cache-hit rule and are unaffected.

### 3.3 Consequences for R1 and the 17-chain re-estimation plan

1. **No chain needs to be added.** Every chain the defect can affect is already in the plan: T4.1 FEDFUNDS MSAR, UNRATE 180 MSAR and UNRATE 300 MSAR are all Tier B.
2. **T4.1:FEDFUNDS|MSAR was available after all** under the live rule. Its re-estimate (B2) is **numerically identical** to that original cached chain: the same 626-key sequence, and identical contents where checked. So the Tier B result equals an original-run computation, and only the provenance label differs.
3. **Neither the original cache nor any re-estimate reproduces the published chain** for MSAR chains with failed fits. The published estimates at some post-failure origins came from cold fits that were never stored. R1 aims to reproduce the published results where possible and correct them where wrong, so it must decide which version it treats as the original. That is a methodological decision (§6), not an implementation one.
4. **UNRATE 180 and UNRATE 300 MSAR.** If the original cache proves complete under the live rule, their remaining Tier B estimation could be replaced by a live-rule replay of the original cache. The numbers are expected to be identical, given the bit-for-bit reproducibility shown. This is not established and needs the full-cache audit (§5) or the remaining B1/B2 progress.

## 4. Implication beyond Tier B: the published baseline UNRATE MSAR chain

The baseline chain `forecasting:UNRATE|MSAR` and its T4.8 duplicate are in the **published Part 8 main results**:
- **6 post-failure origins** were fitted **without** the warm start the approved method (D6) prescribes;
- at 1983-04/05/06 its two published copies **disagree** (§2.3).

This is an implementation artifact in the original run, under CLAUDE.md §6A, affecting **baseline** outputs. Not established:
- **[U]** how much the affected origins and their downstream origins change the published UNRATE MSAR forecasts and tests, which would need the cached live chain (§5);
- **[U]** whether other published outputs depend on these origins beyond UNRATE MSAR.

## 5. Completing the audit (read-only, in Colab, no estimation)

The batch notebooks already restore the complete original cache to `WORK_DIR/original_cache/fits`. After their restore cell:

```
python colab/r1_original_cache_audit.py \
    --cache-fits /content/r1tierb_<B>/original_cache/fits \
    --code-dir /content/r1tierb_<B>/pinned/my-thesis/code \
    --original <original output> \
    --chain-sources <repo>/my-thesis/reports/part8/corrections/r1/replay_20261103T063749Z/corrected_r1_summary.json \
    --out /content/original_cache_audit
```

This settles, for **every** MSAR/STAR/ARMA chain:
- the live-rule and cache-hit completeness;
- origin-by-origin comparison with the published records;
- the presence of both keys after every failed fit, including UNRATE 180/300 MSAR and the baseline UNRATE MSAR chain.

It writes only to `--out`. As B1 and B2 progress, their live keys can also be checked against the committed inventory without downloading anything.

## 6. Proposed amendment (for independent approval; nothing implemented)

**A. Name the artifact.** Record in `notes/claude/` and the R1 corrections log that in the published Part 8 run, some MSAR fits right after a failed fit were estimated without the D6 warm start, because a resumed run's cache replay reset it. The affected chains are T4.1:FEDFUNDS, T4.8:UNRATE 180/240/300 and baseline UNRATE, with the origins listed in `q1_published_msar_post_failure_starts.csv`.

**B. Decide which estimate is authoritative at those origins.**

| Option | Meaning | Consequence |
|---|---|---|
| **B1 (recommended for review)** | The approved method is D6: warm start from the previous successful refit. The live-rule estimates are the correct implementation; the published post-failure cold fits are an implementation error to correct under §6A. | Corrected chains use the live-rule estimates: the original cache's live chains where complete, or the Tier B re-estimates, which are identical. Affected outputs are regenerated and labelled, **including the baseline UNRATE MSAR results**. Needs your approval because it changes published baseline numbers. |
| B2 | Keep the published estimates as the original record. Document the artifact as a limitation. | Tier B re-estimates are used only where nothing else exists; differences at post-failure origins remain review items. Baseline outputs are unchanged. |
| B3 | Defer until the full-cache audit (§5) quantifies the downstream effect on every affected output. | No change now. |

**C. R1 replay rule.** For warm-started chains, replay the original cache by the **live** rule (`r1_tierb.live_replay_class`, as approved for Tier B) instead of the pinned cache-hit rule. Under B1, T4.1:FEDFUNDS|MSAR's source becomes "original cache (live rule)", with the same numbers as B2. This changes the R1 chain classification and therefore needs approval.

**D. Unchanged until decided:** the 17-chain plan, B1 (running), B2 (stopped, awaiting approval), B3, Tier A, the pinned scientific code and the published releases.

## 7. Files

- `colab/r1_original_cache_audit.py`: read-only audit tool, committed at `274745d`.
- `reports/part8/corrections/r1/evidence/original_cache_audit_20261105/`:
  - `original_fit_cache_inventory.csv.gz`: all 18,964 cached payload names, with part, size and write time.
  - `original_fit_cache_parts.csv`: the 143 parts, with Drive ids and sizes, and sha256 for the 16 downloaded.
  - `q1_start_sets_B1_B2_vs_published.csv`: per origin, the start sets, warm and deterministic objectives, statuses and log-likelihoods of new and published fits.
  - `q1_published_msar_post_failure_starts.csv`: for every MSAR chain, failed fits, post-failure origins, those without a warm start, and their dates.
  - `q2_live_keys_in_original_cache.csv`: per origin, presence, part and write time of the live key, and presence of the cache-hit key after failures.
  - `q2_partial_cache_walk_chains.csv`: both-rule walks of every MSAR/STAR/ARMA job over the 7,969 downloaded payloads.
