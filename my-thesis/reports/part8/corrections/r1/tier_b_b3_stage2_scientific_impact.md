# R1 Option B3, stage 2: original-cache audit and scientific impact of the baseline UNRATE MSAR artifact

Date: 6 November 2026.

- **Authorised scope:** Option B3 only, read-only.
- **No model was estimated:** the Colab run refused every estimator; the analysis here only read its exported results.
- **Nothing was changed:** original or corrected empirical outputs, Tier A, Tier B checkpoints, pins, specifications and releases are untouched. No aggregation was run, and Part 9 was not started.
- **Evidence:** `evidence/b3_stage2_20261106/`. Machine-readable report: `b3_stage2_audit_report.json`, with the sha256 of every evidence file.
- **Reproducible analysis:** `b3_stage2_analysis.py`.

Labels: **[C]** confirmed by data; **[P]** plausible; **[U]** unresolved.

## 1. Provenance and verification of the Colab export

| Item | Value |
|---|---|
| Session | `audit-20261106T081950Z-9c9ba2` (Drive `baseline/r1_original_cache_audit/`) |
| Orchestration and scientific code | `63670e4` and the pin `8aaa421` |
| Cache identity, Python | `3413465b508bb844`, 3.11.18 |
| Frozen data sha256 | `7e7dc769…b832a` |
| Exported files | 57; **54 retrieved and verified against the export manifest's sha256 (0 mismatches)** [C] |
| Not retrievable through the Drive connector | `audit/origins.csv` (7.4 MB) and the two `locf_forecast_exposure.csv` (23.8 MB each). Their summaries are in retrieved files (§6). |
| Chain sources | The run omitted `--chain-sources` because of the missing-path fault (fixed, §7). The R1 sources were merged here from the evidence commit `c5324b2` (sha256 `f3b7c1fb…`). |

## 2. Integrity of the original cache (task 1) [C]

| Check | Result |
|---|---|
| Payloads present against the committed inventory | **18,964 / 18,964**; 0 missing, 0 extra, 0 size mismatches |
| Duplicate payload names across parts | none (inventory of 143 listings) |
| Archive parts | 143, 9,547,811 bytes; sha256 of every part recorded |
| Independent cross-check | The **16 parts downloaded earlier through the connector have identical sha256**; all 143 sizes equal the Drive listing |
| Refit marker in original payloads | absent (as expected for original estimates) |
| Payload manifest (sha256 of all 18,964) | `payload_sha256.csv.gz`; combined digest `7e283de3…b2a0` |

## 3. All 78 chains under both replay rules (task 1) [C]

Full table: `chains_with_r1_source.csv`, which covers all MSAR, STAR and ARMA jobs, baseline and robustness.

- **The rules differ for exactly 5 chains**, all MSAR with failed fits: T4.1:FEDFUNDS, T4.8:UNRATE 180, 240 and 300, and `forecasting:UNRATE|MSAR`. T4.8:UNRATE 240 shares its keys with the baseline.
- **37 chains are complete under the live rule with full horizon coverage.**
- **Every cached origin of every other chain is identical to its published record**: status, reason codes and log-likelihood. **The cache is the published computation everywhere except after failed MSAR fits.**
- **No ARMA payload is cached** (26 ARMA jobs, key absent at origin 1).

| Chain | Cache-hit rule | Live rule | Cached origins identical / differing from published |
|---|---|---|---|
| T4.1:FEDFUNDS\|MSAR | 2 | **626/626 complete** | 583 / **43** (the same 583 as the B2 re-estimate's agreement) |
| T4.8:UNRATE\|180:MSAR | 229 | **764/764 complete** | 758 / **6** |
| forecasting:UNRATE\|MSAR (baseline) | 178 | **704/704 complete** | 695 / **9** (7 h=1 forecasts differ) |
| T4.8:UNRATE\|240:MSAR | 182 | **704/704 complete** | 695 / **9** |
| T4.8:UNRATE\|300:MSAR | 454 | 501 (key absent at origin 502, 2014-09-01) | 501 / 0 |
| T4.8:UNRATE\|300:STAR; M2SL 180 STAR; M2SL 300 MSAR | 155; 51; 343 | same | identical / 0 |
| Other STAR chains (baseline FEDFUNDS, GDPC1, M2SL; T4.1 FEDFUNDS; several T4.8) | 0 | 0 (absent from origin 1) | — |

## 4. Baseline `forecasting:UNRATE|MSAR` (tasks 2 and 3)

**Reconciliation [C]** (from stage 1, confirmed by the full cache):
- the baseline and T4.8-240 chains are the same chain: same specification, data, window, origins and keys; only the horizons differ;
- both have 704 published records;
- the April–June 1983 conflict is two runs of the chain in the final run, both failed at those origins.

**The candidate was completely reconstructed [C]:**
- 704/704 origins, every one served from the original cache by the live warm-start rule through the pinned `rolling.run_chain`;
- **0 estimations** (counted, and refused by the guard);
- every payload covers h = 1, 3, 6 and 12;
- valid 698, failed 6, against 693 and 11 published;
- candidate forecasts sha256 `b477d705…60d1`.

**Where the candidate differs from the published chain (task 5): 9 consecutive origins, 1982-10 to 1983-06** (`origin_level_classification.csv`). It is identical at the other 695.

| Origin | Published | Candidate | Warm start in the published fit | Classification |
|---|---|---|---|---|
| 1982-10-01 | failed (NONCONV., SINGULAR_COV) | failed (NONCONV.) | **no** (after a failed fit) | genuine failure in both; implementation artifact changes which failed optimum |
| 1982-11-01 | failed | **adequate** | **no** | **implementation artifact**: no D6 warm start; the candidate's best start is the warm start |
| 1982-12-01 | fragile (SINGULAR_COV) | **adequate** | **no** | **implementation artifact** |
| 1983-01-01 | failed | failed | yes | genuine failure in both; inherited divergence |
| 1983-02-01 | fragile | adequate | yes | inherited divergence (warm start from a different previous fit) |
| 1983-03-01 … 06-01 | failed | adequate | yes | inherited divergence |

**Interpretation:**
- **[C]** All 9 differences stem from the three published fits without the D6 warm start at 1982-10/11/12. They propagate through path-dependent warm starts until the two paths rejoin at 1983-07-01.
- **[C]** The published chain's other three post-failure fits without a warm start (1989-11, 2017-03, 2020-07) **reached the same estimate**, so they are artifacts without numerical consequence.
- **[C]** The candidate's log-likelihood is higher at all 9 origins, by 16 to 364.
- **[C]** Its adequate/fragile/failed classifications come from the pinned reliability flags, not from the likelihood. A higher likelihood alone does **not** establish that the candidate's estimates are scientifically preferable.
- **[C]** Two origins are genuine failures in both versions.
- **[P]** In this region both versions show local optima and singular covariance: optimizer sensitivity of MSAR(4, K=2) around the early-1980s recession.

## 5. Scientific impact (task 4): candidate against reference

**Comparison design:**
- **Reference:** the pinned R1 workflow in legacy mode on the published outputs. It reproduces the published outputs **exactly**: 87 files identical and 5 within floating-point tolerance; in Colab even the figures match. [C]
- **Candidate:** the identical pass on a copy carrying only the candidate chain.
- **No estimation in either pass.**

**Scope of change [C]:**
- 29 of the 92 regenerated files change, with 1,213 table cells, excluding run-provenance stamps;
- **no forecast of AR, ARMA or STAR changes**;
- in UNRATE MSAR forecasts, 36 of 2,798 rows change (9 origins × 4 horizons): failed→adequate 20 rows, fragile→adequate 8 rows; forecast values change at 7 origins per horizon, at most **0.574** where both are finite.

**Decisions and rankings [C] (`decision_flips.csv`):**
- **No 5% test decision changes:** HLZ, DM/HLN, T4.4, T4.5 and window-length tests;
- **no MCS membership changes:** T3.4 and the window-length MCS;
- **no ranking changes:** T3.3 `rank_rmse` and `rank_mae`, and the T4.5 ranks;
- the only changes in decision-like columns are the **descriptive** UNRATE MSAR `model_status` counts in T3.3 (four horizons): adequate 433→440, fragile 260→258, failed 11→6.

**Magnitudes [C]:**

| Output | Largest change |
|---|---|
| T3.3 UNRATE MSAR RMSE, h=1/3/6/12 | 0.4923→0.4914, 1.0662→1.0641, 1.4096→1.4097, 2.0686→2.0746; rank 1/1/1/2 unchanged |
| T3.3 out-of-sample R² against AR | at most −0.0008 |
| T3.3A HLZ p-value | ARMA vs MSAR, h=6: 0.518→0.641 (both do not reject) |
| T3.3B DM/HLN p-value | ARMA vs MSAR, h=6: 0.632→0.720 (both do not reject) |
| T3.4 MCS p-value | ARMA, h=3: 0.353→0.501 (membership unchanged) |

> **Erratum (6 November 2026, B1 preparation).** The extract `T3.4_unrate_mcs_reference_vs_candidate.csv` in this evidence folder was produced by a merge that omitted `confidence_level`: a many-to-many join with 128 rows instead of 64. The cell-level comparison and `decision_flips.csv` were positional and unaffected. The corrected keyed extract (64 unique rows; 0 membership changes; 64 of 64 UNRATE rows in the MCS in both versions; largest p-value change ARMA, h=3, 90%, squared loss, 0.3526→0.5006) and the window-length MCS extract (48 rows, 0 changes) are in `evidence/b1_staged_20261106/stage2_rev2/`. See `tier_b_b1_staged_correction.md` §1.

| T3.5 / T3.6 state and peak-trough RMSE | at most 0.009 / 0.016 |
| T4.TP1 turning-window RMSE | at most 0.019 |
| T4.4, T4.1, T4.5, T4.9, window-length tables | RMSE changes at most 0.006; test p-values at most 0.0061; window-length MCS p-values at most 0.030 |

**Thesis-relevant conclusions [C]:** for the outputs compared, every conclusion that depends on a test decision, MCS membership or ranking is **unchanged**. The artifact changes descriptive fit counts and second-to-third-decimal accuracy figures for UNRATE MSAR.

**Not quantified here [U]:**
- figure content: F3.4–F3.6 UNRATE change, but images were not exported;
- the per-row detail of the 23.8 MB LOCF exposure table (its T4.9 summary is quantified);
- conclusions stated in the Part 8 prose reports, which this audit did not re-read.

## 6. Missing computations, unresolved issues and dependencies (task 5)

| Item | Status |
|---|---|
| Candidate baseline chain | **complete; no additional computation needed** |
| `audit/origins.csv` (per-origin audit of all 78 chains) | **[U] not retrieved** (7.4 MB). Chain-level results are verified; origin-level detail for FEDFUNDS T4.1 (43) and UNRATE 180 (6) is not re-verified from the full cache. The export now also writes `.gz` copies; a re-export needs a new read-only run of about 1–2 hours. |
| Outputs that depend on the chain but are not regenerated by the workflow | 7 (`dependency_map_v2`): fit records, origin audit, T4.7 registry and status counts (UNRATE MSAR adequate/fragile/failed 433/260/11 → 440/258/6), the 8 state-dependence Wald rows, the inventory. These need **new non-estimating code** if B1 is ever approved. |
| Updated dependency map | 41 outputs. **T4.5 VAR comparison and tests also depend on the chain**, found in the full run. |
| Mechanism of the original artifact | **[P]**: cache-hit replay in the resumed final run; unchanged from stage 1 |
| Original window-length 240 row | the original pipeline ran its own T4.8 chain; the reference reproduces the published window-length tables exactly, so they agree where it matters |

## 7. The 17-chain plan and the cache classification (task 7; no change made)

Being **present** in the cache is distinct from **reproducing the published** chain:

| Chain | Present and complete under the live rule | Under the cache-hit rule (R1) | Reproduces the published chain |
|---|---|---|---|
| T4.1:FEDFUNDS\|MSAR | **yes**, 626/626 | no (2) | **no** (43 origins) |
| T4.8:UNRATE\|180:MSAR | **yes**, 764/764 | no (229) | **no** (6 origins) |
| T4.8:UNRATE\|300:MSAR | no (501/644) | no (454) | n/a; genuinely incomplete |
| T4.8:UNRATE\|300:STAR, T4.1:FEDFUNDS\|STAR | no (155, 0) | no | genuinely incomplete |
| 4 ARMA chains | no (none cached) | no | genuinely unavailable |
| 8 AR chains (Tier A) | not audited (no warm start; Tier A done) | — | — |

**Consequences, pending your B1/B2 decision:**
- **Two chains are complete in the original cache under the live rule:** T4.1:FEDFUNDS|MSAR (already re-estimated by B2, numerically equal to the cache where compared) and T4.8:UNRATE|180:MSAR. For the latter, B2's remaining 507 origins could be **replayed** instead of estimated. Its 257 committed origins are all present in the cache under the same keys.
- **Neither reproduces the published chain**, so either source changes the published values at the post-failure origins. Which version is authoritative remains the B1/B2 decision.
- **The classification is not changed.**

## 8. Code fixes (task 7)

1. **Missing path:** the notebook now fetches `corrected_r1_summary.json` from the evidence commit `c5324b2` (branch `part8-r1-replay/20261103T063749Z`) and verifies its sha256 before use. Regression tests: every path the notebook reads from its checkout must exist; the fetch block refuses a mismatching file. Commit `62f7be2`.
2. **Large exports:** files over 5 MB are also exported as reproducible gzip copies, recorded in the manifest. Test included.

## 9. Proposed next steps (for independent review; none authorised or performed)

- **Re-export** with the gzip fix to retrieve `origins.csv`, if origin-level verification of the other chains is wanted. This is a read-only rerun.
- **Decide B1 or B2** with this evidence: the artifact is real and confined to MSAR chains with failed fits. For the baseline UNRATE MSAR it changes no inferential conclusion, only descriptive fit counts and small accuracy figures.
- If B1 is chosen: regenerate the 29 files with the pinned workflow (non-estimating); write the non-estimating code for the 7 remaining outputs; re-render the figures; then review.
