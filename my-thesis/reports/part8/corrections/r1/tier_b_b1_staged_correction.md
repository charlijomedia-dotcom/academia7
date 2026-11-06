# R1 Option B1 (staged): baseline UNRATE MSAR correction — status of round 1

Date: 6 November 2026.

- **Authorised scope:** Option B1 as a **scoped correction of an established implementation error** (the D6 warm start was missing after failed fits in the published baseline `forecasting:UNRATE|MSAR` chain), in **staging only**.
- **Not authorised and not done:** no model estimation; no change to the Part 5 methodology; published releases and Tier A/B certificates untouched; no final aggregation; no Part 9.

Labels: **[C]** confirmed by data; **[B]** blocked (needs the supplementary Colab cell); **[D]** done in this round.

## 1. MCS comparison defect (task 1) [D]

**Defect.** `b3_stage2_analysis.py` (revision 1) merged the reference and candidate T3.4 rows on (horizon, loss, model), without `confidence_level`. Each row was therefore paired with both confidence levels: a many-to-many join, 128 rows instead of 64.

**Scope of the defect:**
- **Affected:** the extract `T3.4_unrate_mcs_reference_vs_candidate.csv` only.
- **Not affected:** the cell-level comparison (`changed_cells_keyed`) and `decision_flips.csv`. Both compare row by row in the regenerated tables' own order. Revision 2 reproduces them byte for byte.

**Correction (revision 2):**
- every keyed comparison goes through `keyed_merge`;
- it refuses duplicate keys and different key sets, and merges `validate="one_to_one"`;
- the T3.4 key is (series, horizon, loss, confidence_level, model);
- the window-length MCS key adds window_length;
- the positional comparison now asserts that the key columns are aligned row by row.

**Tests:** `code/tests/unit/test_b3_stage2_analysis.py` (7). One test fails on the revision-1 key.

**Re-verification [C]** (`evidence/b1_staged_20261106/stage2_rev2/`):

| Check | Result |
|---|---|
| T3.4 UNRATE rows | 64 unique (4 models × 4 horizons × 2 losses × 2 confidence levels) |
| MCS membership changes | **0**; all 64 rows are in the MCS in both reference and candidate |
| Largest MCS p-value change | ARMA, h=3, squared loss, 90%: 0.3526 → 0.5006 |
| Window-length MCS, UNRATE | 48 unique rows; **0** membership changes; largest p-value change 0.0302 (ARMA, 240, h=1, absolute, 90%) |
| T3.3 UNRATE extract | 16 unique rows; values identical to revision 1 |
| Conclusions of stage 2 §5 | **unchanged** |

The revision-1 extract stays in `evidence/b3_stage2_20261106/`, marked superseded (`ERRATUM.md`).

## 2. Recovering the three oversized files (task 2) [D: cell ready; B: execution]

**Cell:** `colab/r1_b3_supplementary_recovery_cell.py`. Paste it into one Colab cell. It needs only Drive: no git, no token, no estimation.

**A. The three files:**
- read from session `audit-20261106T081950Z-9c9ba2`:
  - `audit/origins.csv`;
  - the reference `locf_forecast_exposure.csv`;
  - the candidate `locf_forecast_exposure.csv`;
- each checked against that session's `export_manifest.json` (bytes and sha256);
- written as a reproducible gzip, in chunks of at most 3.5 MB.

**B. The original cache parts:**
- the 143 archive parts of `fit_cache/3413465b508bb844` (9,547,811 bytes), unchanged;
- packed into uncompressed tar bundles of at most 3.5 MB, about 3 files;
- the sha256 of every part recorded;
- I verify every part locally against the parts list from the audit export.

**Why B is included.** Tasks 3–6 need the original-cache payloads locally, and the connector cannot deliver them:
- **Inline downloads:** parts under about 45 KB, 101 of the 143, come back inline, at 30–37 thousand characters each. Fetching the 127 missing parts one by one is impractical.
- **What is local:** only 16 of the 143 parts (7,969 of 18,964 payloads). Neither the baseline chain nor the B2 comparison chains are reachable from them.
- **Bundles:** a few files of 3.5 MB download as saved files.

**Writes:** only the new folder `…/r1_original_cache_audit/audit-20261106T081950Z-9c9ba2_supplementary/`. The cell refuses to run if that folder exists, and leaves the session folder and the cache untouched.

**Tests:** `code/tests/unit/test_r1_b3_supplementary_cell.py` (4). They cover:
- a simulated Drive layout: verified recovery, bundles reproducing the parts byte for byte, and no existing file changed;
- refusal of a tampered export and of a second run;
- read-only source checks.

## 3. Why tasks 3–6 are not done in this round [B]

**The workflow needs the cache.** The pinned R1 workflow reproduces the published outputs exactly only with the complete original cache. In Colab, 17 of its chains were served from that cache (chain sources: published 48, cache 17, unavailable 43).

**Without it the result is not faithful.** A local run without the cache was tried earlier, on 6 November:
- it treats those 17 chains as unavailable;
- it does **not** reproduce the published outputs: 50 of 92 files differ;
- so it cannot support the "unaffected outputs identical" check (task 6).

**Other steps need the payloads directly:**
- **Full corrected fit records:** standard errors, AIC/BIC, diagnostics and start sets. The Colab candidate export holds only status, codes, log-likelihood, start and parameters.
- **The B2 comparison:** original-cache payloads for T4.1:FEDFUNDS|MSAR (626) and T4.8:UNRATE|180:MSAR (764).

So the staged correction, the downstream regeneration, the B2 review and the validation wait for the cell. Nothing was staged from partial inputs.

## 4. Plan for round 2 (after the cell has run)

1. **Retrieve and verify:**
   - download the bundles and the chunks;
   - verify every part against `original_cache_parts.json` (committed);
   - verify the three files against the export manifest;
   - restore the cache and verify all 18,964 payloads against the inventory.
2. **Origin-level verification:** use the recovered `origins.csv` for all 78 chains, including FEDFUNDS T4.1 (43 origins) and UNRATE 180 (6).
3. **Corrected chain** (task 3):
   - `forecasting:UNRATE|MSAR`, replayed from the 704 original payloads by the live warm-start rule through the pinned `rolling.run_chain`;
   - read-only cache view; estimation refused and counted (0);
   - full `FitRecord`s and forecasts;
   - the T4.8:UNRATE|240:MSAR records come from the same keys (same chain).
4. **Staged regeneration** (task 4), with the published tree copied and never modified:
   - pinned R1 workflow in legacy mode, with the cache, on the published tree (reference) and on the staging input (candidate);
   - reconciliation, so that unaffected cells keep the published text;
   - new non-estimating code, using the pinned table builders, for the 7 dependent outputs:
     - `fit_records`;
     - `forecast_origin_audit`;
     - T4.7 registry and status counts;
     - the 8 Wald rows of `all_test_results`;
     - the inventory;
   - figures F3.4–F3.6 re-rendered;
   - dependency map v3.
5. **B2 review** (task 5):
   - every B2 checkpoint payload (FEDFUNDS 626, UNRATE 180 257) against the original cache's live-rule payload for the same origin: parameters, log-likelihood, status, reason codes and starts;
   - plus UNRATE 180 origins 258–764 from the original cache alone, against the published records;
   - every classification change and optimiser sensitivity listed;
   - failed and fragile fits kept.
6. **Validation** (task 6):
   - unaffected outputs byte-identical to published;
   - every changed value and decision listed;
   - original and corrected side by side;
   - computational completion reported separately from scientific acceptance.
