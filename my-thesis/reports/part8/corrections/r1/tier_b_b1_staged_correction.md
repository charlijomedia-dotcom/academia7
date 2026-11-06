# R1 Option B1 (staged): baseline UNRATE MSAR correction, B2 review and validation

Date: 6 November 2026 (round 1: tasks 1–2; round 2: tasks 3–6).

**Authorised:** Option B1 as a scoped correction of the established implementation error (the D6 warm start was missing after failed fits in the published baseline `forecasting:UNRATE|MSAR` chain), **in staging only**.

**Not done, as instructed:**
- no model estimation;
- no change to the Part 5 methodology or the scientific pin `8aaa4217…`;
- the published `output/`, the releases and the Tier A/B certificates are unchanged;
- no publication, no final aggregation, no Part 9.

**Machine-readable report:** `evidence/b1_staged_20261106/b1_staged_report.json` (sha256 of every evidence and staged file).

Labels: **[C]** confirmed by data or by a check that passed; **[P]** plausible; **[U]** unresolved.

**Computational completion is not scientific acceptance.** §7 separates the two.

---

## 1. MCS comparison defect (task 1, round 1) [C]

**Defect.** `b3_stage2_analysis.py` revision 1 merged the T3.4 rows on (horizon, loss, model), without `confidence_level`. That is a many-to-many join, with 128 rows instead of 64.

**Correction (revision 2):**
- every keyed comparison uses `keyed_merge`, which refuses duplicate keys and different key sets and merges `validate="one_to_one"`;
- the positional cell comparison asserts that its key columns are aligned row by row.

**Tests:** `code/tests/unit/test_b3_stage2_analysis.py` (7). One test fails on the revision-1 key.

**Re-verification:**
- T3.4 UNRATE: 64 unique rows, 0 MCS membership changes; all 64 rows are in the MCS before and after;
- largest p-value change: ARMA, h=3, squared loss, 90%: 0.3526 → 0.5006;
- window-length MCS: 48 rows, 0 changes (largest 0.0302);
- the cell-level results and decision lists of stage 2 are reproduced byte for byte;
- the revision-1 extract is kept and marked superseded (`evidence/b3_stage2_20261106/ERRATUM.md`).

The **staged tree** confirms the same against the published tables (§5).

## 2. Recovery of the oversized files and the original cache (task 2) [C]

**The cell:**
- `colab/r1_b3_supplementary_recovery_cell.py` (tests: `test_r1_b3_supplementary_cell.py`);
- run by you as `audit-20261106T081950Z-9c9ba2_supplementary`.

**Retrieved and verified here** (`evidence/b1_staged_20261106/supplementary/verification.json`):

| Item | Check | Result |
|---|---|---|
| 3 cache bundles (3.47, 3.30, 2.91 MB) | sha256 and member lists against `supplementary_manifest.json` | all match |
| 143 original cache parts (9,547,811 bytes) | sha256 against the supplementary `parts.json` **and** against the audit export's `original_cache_parts.json` (an independent listing); combined digest | all 143 match |
| Restored payloads | against the committed inventory | **18,964 / 18,964**, 0 missing, 0 extra, 0 size mismatches; payload digest `7e283de3…` (= Colab) |
| `audit/origins.csv` (7,447,814 bytes) | gzip sha256, then sha256 against the audit export manifest | match |
| Reference and candidate `locf_forecast_exposure.csv` (23.8 MB each) | same | both match |
| `export_manifest.json` used by the cell | sha256 | equals the copy verified in stage 2 |

### Independent local reproduction of the Colab audit (no estimation)

The complete audit was rerun on this machine from the restored cache (`evidence/b1_staged_20261106/local_reproduction/`).

| Output | Colab | Local |
|---|---|---|
| `origins.csv`: per-origin audit of all 78 chains | sha `4d1ae072…` | **byte-identical** |
| `chains.csv` | (run without R1 sources) | identical in every column; the R1-source column equals the committed merge |
| Candidate fit records and forecasts | sha `b477d705…` | **byte-identical** |
| Impact: files changed by the candidate | 29 | the **same 29**; identical changed-cell positions; values within 1e-12 relative |
| Reference against published | 87 identical, 5 within floating-point tolerance | 83 identical (**all 44 figures byte-identical**), 9 within floating-point tolerance (≤ 1e-11) |

**Renderer note [C].** This container ships `/etc/matplotlib/matplotlibrc`, which selects the Inter font. With it, 41 published figures were not reproduced; all tables were. With matplotlib's default configuration, as in Colab, every figure reproduces byte for byte. All staged figures were rendered with the default configuration.

### The other stage-2 unresolved items, now closed [C]

- **Origin-level detail of all 78 chains** is available and identical to the local run. FEDFUNDS T4.1 (43) and UNRATE 180 (6) are verified origin by origin (§4).
- **LOCF row detail:** of 55,268 rows, exactly **36 differ**: UNRATE MSAR, the 9 origins 1982-10 to 1983-06, at h = 1, 3, 6 and 12 (`supplementary/locf_row_level_comparison.json`).

## 3. Staged correction of the baseline chain (task 3) [C]

**Method:**
- the 704 original-cache payloads, replayed under the approved live warm-start rule (`r1_tierb.live_replay_class` over a read-only cache view) through the pinned `rolling.run_chain`;
- estimators refused, and fit calls counted: **0**.

**The T4.8 240-month twin.** `T4.8:UNRATE|240:MSAR` uses the same cache keys. It was replayed separately and gives **identical** records.

**Builder:** `colab/r1_b1_staged_correction.py`. Report: `evidence/.../staging/b1_staging_report.json`.

| | Published | Corrected (staged) |
|---|---|---|
| Origins / from original cache / estimated | 704 / — / — | 704 / 704 / **0** |
| Valid / failed | 693 / 11 | **698 / 6** |
| Adequate / fragile / failed | 433 / 260 / 11 | **440 / 258 / 6** |
| Origins whose estimate changes | — | 9 (1982-10 … 1983-06) |
| Origins whose record changes but whose estimate does not | — | 4 |

**The 4 diagnostics-only origins:**
- 1983-07-01 is the rejoin point: a different warm-start candidate was offered, but the same start was selected;
- at 1989-11, 2017-03 and 2020-07, the live rule offers the warm start the published fit lacked; the selected estimate is identical;
- in all 4, only the start set (`diagnostics`) and `wall_seconds` differ.

## 4. Downstream regeneration (task 4) [C]

### Workflow-regenerated files (29)

- The pinned R1 workflow in legacy mode, with the original cache, ran on the published tree (reference) and on the corrected input (candidate).
- A table cell changes **only where the candidate differs from the reference**, the same rule as the R1 `reconcile`. Every other cell keeps the published text byte for byte.
- Parquet twins are patched the same way: 36 rows each in `forecasts_UNRATE` and `locf_forecast_exposure`.
- Figures F3.4, F3.5 and F3.6 UNRATE take the candidate rendering. Their reference renderings equal the published bytes.

### Dependent outputs not produced by the workflow

Each builder first **reproduces the published values from the published inputs**, and stops otherwise.

| Output | Correction | Validation of the builder |
|---|---|---|
| `models/fit_records.csv` / `.parquet` | 13 rows in each of the chain's 2 blocks (rows 5086–5789 and 40337–41040); 26 rows in total; dtypes unchanged | the replayed records equal the published records at all 691 unchanged origins |
| `forecasts/forecast_origin_audit.csv` | valid 693→698, failed 11→6; also the computational counters origins_from_cache 691→704 and cache_horizon_misses 13→0 (they describe how the corrected chain was obtained) | valid + failed = attempted |
| `robustness/T4.7_failure_registry.csv` | each of the chain's 2 blocks: 437 → 423 events (14 removed, 0 added); every remaining event is the published row verbatim | blocks located by their exact event signature; ordered as the fit-record blocks |
| `robustness/T4.7_status_counts.csv` | UNRATE MSAR, all chains: adequate 2101→2115, fragile 1389→1385, failed 30→20 | the recount of the published fit records reproduces the published table |
| `diagnostics/all_test_results.csv` | the 8 UNRATE "MSAR vs AR" Wald rows: statistics and p-values (largest p change 0.0019); **decisions unchanged** | all 8 published rows rebuilt exactly from the published T3.5 |
| `figures/F4.8_UNRATE` (pdf, png) | **a dependency missing from map v2**, found here: re-rendered from the corrected window-length table | the published F4.8 is reproduced byte for byte from the published table |
| `manifests/output_inventory.csv` | bytes and sha256 updated for the 34 inventoried changed files | every inventoried hash matches its staged file |

**Dependency map v3:** `evidence/.../baseline_unrate_msar_dependency_map_v3.csv`. It has 43 outputs, adds F4.8_UNRATE, and records which mechanism corrected each output.

**Staged files:** `output_staging/r1_b1_unrate_msar_20261106/` holds only the changed files and `STAGED_FILES.csv`, which gives the staged and published sha256 of each.

## 5. Validation of the complete staged correction (task 6) [C]

**Validator:** `colab/r1_b1_validate_staged.py`. It recomputes everything from the two trees, not from the builder's report. Result: `evidence/.../validation/validation.json`, **`all_checks_passed: true`**.

| Check | Result |
|---|---|
| File set | identical: 461 published, 461 staged |
| Byte-identical files | **415** |
| Changed content files | **38**, all expected (29 from the workflow + 9 dependent); **0 unexpected**, 0 expected-but-unchanged |
| Changed figure sidecars | 8, only for the changed figures |
| Changed non-provenance cells | 1,705, every one listed and keyed (`staged_vs_published_cells.csv.gz`). This includes fit records, the inventory and the registry, whose shape changes |
| Consistency: fit records CSV = parquet; both blocks identical; forecast status = fit-record status at every origin; T3.3 counts = fit records; origin audit = fit records; T4.7 counts = recount; registry failure origins = failed fits; Wald rows = T3.5; inventory hashes = files | all true |
| Agreement with an independent platform: staged changed values against the Colab candidate regeneration | 1,258 numeric cells; max relative difference **8.5e-14** |

### Statistical decisions (published → corrected) [C]

- **Changed:** only the descriptive `model_status` of UNRATE MSAR in T3.3, at 4 horizons (adequate 433/260/11 → 440/258/6).
- **Unchanged:**
  - every 5% test decision (HLZ, DM/HLN, T4.4, T4.5, window length, Wald);
  - every significance mark;
  - every MCS membership: T3.4 64/64 in the MCS, window-length MCS 48/48;
  - every rank (`rank_rmse`, `rank_mae`, the T4.5 ranks);
  - every state-dependence-support flag;
  - every conclusion or verdict text.
- The only changed text fields are numeric reprints: the TP1 sign-change note (−64.9184 → −64.294, sign change unchanged) and the HLZ tuning string (n 693 → 698).

### Original against corrected (`evidence/.../headline/`)

| Quantity | Published | Corrected |
|---|---|---|
| UNRATE MSAR RMSE, h = 1 / 3 / 6 / 12 | 0.4923 / 1.0662 / 1.4096 / 2.0686 | 0.4914 / 1.0641 / 1.4097 / 2.0746 |
| UNRATE MSAR RMSE rank, h = 1 / 3 / 6 / 12 | 1 / 1 / 1 / 2 | 1 / 1 / 1 / 2 |
| T3.4 MCS p-value, ARMA, h=3, squared loss, 90% (largest change) | 0.3526 | 0.5006 (in the MCS in both) |
| T3.3A HLZ two-sided p-value (largest) | 0.5175 | 0.6409 (no rejection in either) |
| T3.3B DM/HLN p-value (largest) | 0.6320 | 0.7198 |
| Window-length MCS p-value (largest) | 0.4142 | 0.4444 |
| State-dependence Wald, h=1: p-value | 0.4003 | 0.3985 |

## 6. B2 scientific review against the original cache (task 5) [C]

**What happened in B2.** It completed in two sessions:
- `B2-20261105T071915Z-d12923`: FEDFUNDS 626 origins and UNRATE 180 origins 1–257;
- `B2-20261105T110347Z-505e21`: UNRATE 180 origins 258–764, 24 checkpoints. Its COMPLETE certificate reports `COMPUTATION_COMPLETE_REVIEW_REQUIRED`.

**Review script:** `b2_scientific_review.py` (read-only). Evidence: `evidence/.../b2_review/`. That folder also holds verbatim copies of the B2 certificate and of its agreement table.

**Method:** both payload stores were walked by the pinned live rule. At each origin it compares:
- the cache key;
- status and reason codes;
- log-likelihood;
- parameters (minimised over regime relabellings);
- forecasts at every horizon;
- the start used.

| Chain | Compared directly (both payloads) | Result | Compared transitively | Result |
|---|---|---|---|---|
| T4.1:FEDFUNDS\|MSAR | **626 / 626** | **identical estimate at every origin**: same cache key, Δloglik = 0, Δparams = 0, Δforecast = 0, same start | — | — |
| T4.8:UNRATE\|180:MSAR | **257** (origins 1–257) | identical at every origin, as above | 507 (origins 258–764) | identical (transitive): B2 reproduces the published record (B2 agreement table, loglik ≤ 1e-6, params ≤ 1e-8), and the original cache equals the published record at all 507 (status, codes, loglik and params ≤ 1e-8, computed here) |

**Finding [C]: the B2 re-estimation is the original computation.** It is numerically identical to the original-cache payloads under the approved live rule wherever both are available. Every difference between B2 and the published records is therefore the same implementation artifact as in the baseline chain, not optimiser noise between runs.

**Agreement table [C].** The agreement table written by the B2 session matches its payloads (status and log-likelihood) at all 883 directly compared origins.

### Classification changes and optimiser sensitivities (B2 = original live rule, against published)

All of them are kept in the evidence. No failed or fragile fit is dropped.

**T4.1:FEDFUNDS|MSAR: 583 reproduced, 14 classification changes, 29 optimiser sensitivities.**
- Failed fits: 52 → 49.
- Classification changes:
  - failed → fragile: 3 (1980-01, 1981-05, 1981-06);
  - failed → failed with different codes: 5;
  - fragile → fragile with different codes: 6 (1981-03, 2011-01…05).
- The 29 optimiser sensitivities, 1974-08 to 2014-05: same classification, B2 log-likelihood higher by 0.04 to 275 (median 24.4).
- At all 43 differing origins the B2 log-likelihood is ≥ the published one.
- 33 of the 43 follow a published failed fit directly.

**T4.8:UNRATE|180:MSAR: 758 reproduced, 6 classification changes (1982-01 … 1982-06).**
- fragile → adequate: 5;
- failed → failed with different codes: 1 (1982-06);
- failed fits: 5 = 5.
- At 5 of the 6, the approved-rule estimate has a **slightly lower** log-likelihood than the published one (−0.01 to −0.21). At 1982-01 it is higher (+0.24).
- **A higher likelihood does not establish scientific preference, and neither does this.** The classifications come from the pinned reliability flags.

**[P] Interpretation.** These are the multimodal likelihood surfaces of MSAR(p, K=2) around regime-poor windows: FEDFUNDS around 1980–81, UNRATE around 1982. The warm-start path selects among local optima. **The approved rule is the live warm start**, and B2 applies it, as does the original cache.

**Not done.** B2's 507 later UNRATE 180 payloads were not downloaded: 24 small checkpoint archives that the connector returns inline. Their comparison with the original cache is transitive, through the published records, and is labelled so. A bundle cell like the supplementary one would make it direct.

## 7. Computational completion against scientific acceptance

**Computationally complete [C]:**
- the staged corrected chain;
- every affected downstream output, figures, diagnostics and inventory included;
- the validation;
- the B2 comparison: 883 origins direct and 507 transitive;
- the recovery and independent verification of all stage-2 inputs.

**Not established, and for review:**
1. **Acceptance of the corrected baseline values** for the thesis: whether B1 replaces the published baseline is a separate decision.
2. **The T4.8 240-month window-length row** (window-length tables and F4.8) is corrected together with the baseline, because it is the same chain. The other T4.8 window lengths (UNRATE 180 and 300) are **not** changed here: 180 is a B2 chain, and 300 is B1-batch work in progress.
3. **The provenance counters** origins_from_cache and cache_horizon_misses in the origin audit were set to describe the corrected chain. Keeping the published counters instead is a presentational choice for review.
4. **Thesis prose:** the Part 8 report prose that quotes the changed numbers (RMSE, the descriptive fit counts) is not edited here.
5. **The B2 classification changes** (§6) await your decision on how the B2 chains enter the R1 release. Nothing was aggregated.

## 8. Tests

**New tests:**
- `test_b3_stage2_analysis.py` (7);
- `test_r1_b3_supplementary_cell.py` (4);
- `test_r1_b1_staged_correction.py` (5): patch rule, alignment and round-trip refusals, failure-event rule, block finding, no estimation and no writes outside `--out`.

**Related tests:** 90 run, all passing.

`test_r1_correction.py::test_legacy_mode_reproduces_published_tables` fails in this container's default environment, because `/etc/matplotlib/matplotlibrc` selects the Inter font. It passes with matplotlib's default configuration, which is how the outputs were produced (§2).
