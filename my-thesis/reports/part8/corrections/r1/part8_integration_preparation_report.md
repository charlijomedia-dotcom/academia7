# Part 8 integration preparation: verification report

Date: 6 November 2026. This round follows your approval of the staged baseline UNRATE MSAR correction as the selected implementation correction.

**Scope of that approval.** It authorises preparation only. It does not authorise publication, replacing original outputs, final aggregation or Part 9.

**Not done in this round:**
- no model was estimated;
- no aggregation was run;
- nothing was published.

**Unchanged:**
- the scientific pin `8aaa4217…`;
- the approved methodology;
- `output/`;
- the releases `0573a8c`, `3bd24c4` and `292227e`;
- the Tier A/B certificates;
- `approved-specs/` and `source-materials/`.

[C] marks results computed or verified in this round.

The integration plan and the dry-run specification are in `part8_final_integration_plan.md`.

## 1. Project status corrected (task 1)

B1, B2 and B3 have all been run and certified. Copies of the certificates are in `evidence/integration_prep_20261106/certificates/`, with sha256 values and Drive IDs in `MANIFEST.csv`.

| Batch | Chains | Certificate | Status |
|---|---|---|---|
| B1 | T4.8:UNRATE\|300:MSAR, 644 origins | `COMPLETE-20261106T070356Z-B1-20261105T125151Z-df107f` | `COMPUTATION_COMPLETE_REPRODUCED`; 644/644 reproduced; adequate/fragile/failed 502/139/3; sessions `3706dd` (interrupted), `601058` (budget stop), `df107f` |
| B2 | T4.8:UNRATE\|180:MSAR (764), T4.1:FEDFUNDS\|MSAR (626) | `COMPLETE-20261105T151645Z-B2-20261105T110347Z-505e21` | `COMPUTATION_COMPLETE_REVIEW_REQUIRED`; 20 classification changes, 29 optimiser sensitivities |
| B3 | 6 ARMA/STAR chains, 4,007 origins | `COMPLETE-20261105T072545Z-B3-20261105T071020Z-4b7705` | `COMPUTATION_COMPLETE_REPRODUCED` |

**Outdated statements corrected:**

| Document | Was | Now |
|---|---|---|
| `tier_b_b1_staged_correction.md` §7 item 2 | "300 is B1-batch work in progress" | completed and certified (B1); the error is marked as a revision |
| same, §6 | 507 B2 origins "not downloaded", transitive | direct comparison (§2 below); the transitive result is kept as history |
| `tier_b_batches.md` (title: "not authorised to run") | implementation record of 4 Nov | dated status banner: all three batches run and certified |
| `CORRECTIONS.md`, limitation 2 ("pending estimation") | pending | dated update: estimated in Tier A and B1–B3, not yet aggregated |

The historical text is kept; each update is dated and marked.

## 2. B2 UNRATE 180, origins 258–764: direct payload comparison (task 2) [C]

**The archives.** All 24 `payloads.tar.gz` checkpoint archives of B2's second session (`505e21`, checkpoints 00013–00036) were downloaded from Drive.
- Each archive's sha256 equals the `archive_sha256` in the B2 certificate.
- Each archive's payload count equals the certificate's.
- Together they hold 507 payloads: 24 of 24 match.
- Per-archive record: `evidence/integration_prep_20261106/b2_direct_review/session2_archives.csv`.

**The extraction.**
- Every member path was checked against `xx/<64 hex>.json`.
- No payload collided with the 257 session-1 payloads.
- The result is 764 payloads, one per origin.

**The review.** `b2_scientific_review.py` was rerun, read-only, with estimation refused, over both chains.

| Chain | Compared directly | Transitively | Result |
|---|---|---|---|
| T4.1:FEDFUNDS\|MSAR | 626 / 626 | 0 | identical estimate at every origin: same cache key, Δloglik = 0, Δparams = 0, Δforecast = 0 |
| T4.8:UNRATE\|180:MSAR | **764 / 764** | 0 | **identical estimate at every origin**: same cache key, Δ = 0; B2 live walk complete, adequate/fragile/failed 368/391/5 |

**Agreement table.** B2's own agreement table is consistent with its payloads at all 1,390 origins.

**History.** The earlier transitive result (507 origins, via the published records) is kept unchanged in `evidence/b1_staged_20261106/b2_review/`, and it agrees.

**Finding [C].** B2 is the original computation under the approved live warm-start rule at every origin of both chains. No transitive evidence remains, so no further verification step is needed.

## 3. Origin-audit counters: two histories (task 3) [C]

**The two counters.** The staged `forecasts/forecast_origin_audit.csv` row of the baseline UNRATE MSAR chain carries `origins_from_cache = 704` and `cache_horizon_misses = 0`.

**These describe the corrected replay**, in which all 704 origins were served from the original fit cache under the live rule and no horizon was missing. **They do not describe the historical execution** that produced the published chain: 691 from cache and 13 horizon misses, run `baseline-20261030T173044-949fcd76`, code `46a53181…`.

**Both histories are kept, without changing the pinned table schema:**

| Where | What |
|---|---|
| `output_staging/r1_b1_unrate_msar_20261106/COUNTER_PROVENANCE_forecast_origin_audit.csv` | 4 rows: `historical_original_execution` (691, 13) and `corrected_replay` (704, 0), each with run ID, code commit, timestamp, source file and the counter's meaning |
| published `output/forecasts/forecast_origin_audit.csv` | unchanged, so it still carries 691 and 13 |
| `colab/r1_b1_staged_correction.py` | now writes this record on every run (`counter_provenance`, tested) |
| `colab/r1_b1_validate_staged.py --counter-provenance` | checks each row against the published and staged tables: all 4 match |

**The window-length audit.** `robustness/window_length_origin_audit.csv` has its own `from_cache` (699). It is a historical counter that the pinned workflow re-reads from the published window audit (`rescore.py`), so it is unchanged in staging. Its meaning is the historical execution.

## 4. Rendering reproducibility (task 4) [C]

**The cause.** This container sets `MATPLOTLIBRC=/etc/matplotlib`, whose rc file selects Inter with no hinting. Without a guard, figures silently differ from the published ones, which used matplotlib 3.11.2 defaults with DejaVu Sans.

**The fix**, which touches no scientific code:

| Piece | What it does |
|---|---|
| `colab/matplotlibrc.default` | a repo-tracked **empty** rc file, meaning matplotlib's own defaults |
| `colab/r1_render_guard.py` | `pin_default_rc()` sets `MATPLOTLIBRC` to that file before matplotlib is imported, and refuses if matplotlib was already imported with a foreign rc. `check_default_rendering(version)` refuses unless every rendering rcParam equals the default, text resolves to `DejaVuSans.ttf`, and the version equals the published run manifest's (3.11.2). The result is recorded in the run report. |
| `code/tests/conftest.py` | pins the same file for every test session, before any test imports matplotlib; refuses a foreign rc already loaded |
| `code/tests/unit/test_render_guard.py` (6 tests) | the session uses defaults and DejaVu Sans; a foreign rc is refused; pinning before import overrides a foreign `MATPLOTLIBRC`; the version check works |
| builder and validator | both call the guard; the builder writes the record to `b1_staging_report.json["rendering"]` |

**Result.** `test_r1_correction.py::test_legacy_mode_reproduces_published_tables`, which failed in the default container environment last round, **now passes in that same environment** (`MATPLOTLIBRC=/etc/matplotlib`) without any manual override.

**Deterministic rerun of the staged correction [C].**
- **The rerun.** The builder now accepts `--run-id` and `--created-utc`. It was rerun with the original provenance (`b1-staged-20261106T154902Z`, `2026-11-06T15:49:02Z`) in the default container environment, so the guard pinned the rc.
- **The tree.** All 461 files of the staged tree are byte-identical to the first run's.
- **The change records.** So are `b1_changed_files.csv` and `b1_cell_changes.csv`.
- **The validator.** Rerun on it: `all_checks_passed: true`. Every check other than the two new ones (rendering, counter provenance) is identical to the first validation.
- **Evidence:** `evidence/integration_prep_20261106/b1_deterministic_rerun/`.

**Scientific outputs.** The guard changes no scientific output. The staged tree is unchanged, and the scientific code is not touched.

## 5. New finding: F4.8_UNRATE is stale in the provisional releases [C]

**The gap.** The pinned R1 workflow regenerates `window_length_comparison.csv` but does not re-render F4.8.

**The effect.** In releases `0573a8c`, `3bd24c4` and `292227e`, the UNRATE h=1 rows changed under F1, while F4.8_UNRATE stayed byte-identical to the published figure. In `292227e`, UNRATE at 240 months, `oos_r2_vs_benchmark`:
- MSAR 0.692 → 0.192;
- STAR 0.555 → −0.104;
- ARMA 0.324 → 0.238.

**Scope.** No other F4.8 figure is stale.

**Classification.** An omitted regeneration, an implementation error under §6A. It is recorded in `notes/claude/correction_2026-11-06_b1_unrate_msar_warm_start.md` §6, and the final integration corrects it (plan §2.1, decision D2).

**Tools and evidence:**
- checker: `f48_staleness_check.py` (read-only, git objects only), with a test;
- output: `evidence/integration_prep_20261106/f48_staleness/f48_staleness_by_release.csv`.

**Not edited here.** The provisional releases are not edited. They must not be quoted for F4.8_UNRATE.

## 6. Tests [C]

**New this round:**
- `test_render_guard.py`: 6;
- `test_r1_b1_staged_correction.py`: +5, now 10 (counter provenance; argument validation before anything is written);
- `test_f48_staleness_check.py`: 1.

All pass in the default container environment. The related suites were run as well (see the commit message for counts).

## 7. Files

**New:**
- `reports/part8/corrections/r1/`:
  - `part8_final_integration_plan.md`;
  - `part8_integration_preparation_report.md`;
  - `f48_staleness_check.py`;
  - `evidence/integration_prep_20261106/`, containing `certificates/`, `b2_direct_review/`, `b1_deterministic_rerun/` and `f48_staleness/`;
- `colab/r1_render_guard.py`;
- `colab/matplotlibrc.default`;
- `code/tests/unit/test_render_guard.py`;
- `code/tests/unit/test_f48_staleness_check.py`;
- `output_staging/r1_b1_unrate_msar_20261106/COUNTER_PROVENANCE_forecast_origin_audit.csv`.

**Changed:**
- `colab/r1_b1_staged_correction.py`: rendering guard, `--run-id/--created-utc`, counter provenance;
- `colab/r1_b1_validate_staged.py`: rendering record, `--counter-provenance`;
- `code/tests/conftest.py`: rendering pin;
- `code/tests/unit/test_r1_b1_staged_correction.py`;
- `tier_b_b1_staged_correction.md`, `tier_b_batches.md` and `CORRECTIONS.md`: status;
- the staged README;
- the correction note.
