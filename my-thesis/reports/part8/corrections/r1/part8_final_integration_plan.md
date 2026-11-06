# Part 8 final integration plan and non-publishing dry-run specification

Date: 6 November 2026. **Status: plan for independent review. Nothing here has been executed.** No aggregation was run, nothing was estimated or published, and Part 9 has not been started.

The preparation and verification work behind this plan is reported in `part8_integration_preparation_report.md`.

**Unchanged:**
- the scientific pin `8aaa4217536ab3cb942dd248dd19ece7838a8d60`;
- the approved Part 5 methodology;
- `output/` (the published baseline);
- the releases `0573a8c`, `3bd24c4` and `292227e`;
- the Tier A/B certificates;
- `approved-specs/` and `source-materials/`.

---

## 1. What is being integrated

| Component | Source | Status | Evidence |
|---|---|---|---|
| **Baseline UNRATE MSAR correction (B1 staged)** | `output_staging/r1_b1_unrate_msar_20261106/` (38 content files + 8 sidecars), run `b1-staged-20261106T154902Z` | **approved** as the selected implementation correction (6 Nov), **not** approved for publication | `tier_b_b1_staged_correction.md`; `evidence/b1_staged_20261106/` |
| **R1 corrections F1, F2, F3, F4, F7.1, F8** | pinned R1 workflow (`thesis.correction`) | approved; provisional releases `0573a8c`, `3bd24c4` | `CORRECTIONS.md` |
| **Tier A**: 8 AR chains re-estimated | Tier A archive `df73c295…`; release `292227e` (run `correction-20261103T073809-949fcd76`) | complete; closed form, reproduces published records | `tier_a_review.md` |
| **Tier B batch B1**: T4.8:UNRATE\|300:MSAR | certificate `COMPLETE-20261106T070356Z-B1-20261105T125151Z-df107f` | `COMPUTATION_COMPLETE_REPRODUCED`: 644/644, no review items | `evidence/integration_prep_20261106/certificates/` |
| **Tier B batch B2**: T4.8:UNRATE\|180:MSAR and T4.1:FEDFUNDS\|MSAR | certificate `COMPLETE-20261105T151645Z-B2-20261105T110347Z-505e21` | `COMPUTATION_COMPLETE_REVIEW_REQUIRED`: 20 classification changes, 29 optimiser sensitivities | same, and `b2_direct_review/` |
| **Tier B batch B3**: 6 ARMA/STAR chains | certificate `COMPLETE-20261105T072545Z-B3-20261105T071020Z-4b7705` | `COMPUTATION_COMPLETE_REPRODUCED`: all 6 chains, 4,007 origins | same |

**B2 is now verified directly, origin by origin, against the original computation.**
- All 1,390 B2 origins were compared with the original fit-cache payloads walked under the approved live rule: 626 FEDFUNDS and 764 UNRATE 180.
- The estimates are identical at every origin: same cache key, Δloglik = 0, Δparams = 0, Δforecast = 0.
- **B2's differences from the published records are therefore the same warm-start artifact as in the baseline, not optimiser noise.**

### 1.1 The 17 R1 chains and their sources

**Re-estimated: 17.**

| Group | Chains |
|---|---|
| Tier A (AR) | T4.1:UNRATE\|AR; T4.1:FEDFUNDS\|AR; T4.2:CPIAUCSL\|AR(p=1), AR(p=3), AR(p=6), AR(p=12); T4.8:UNRATE\|180:AR; T4.8:UNRATE\|300:AR |
| B1 | T4.8:UNRATE\|300:MSAR |
| B2 | T4.8:UNRATE\|180:MSAR; T4.1:FEDFUNDS\|MSAR |
| B3 | T4.8:UNRATE\|180:ARMA; T4.1:UNRATE\|ARMA; T4.8:UNRATE\|300:ARMA; T4.8:UNRATE\|300:STAR; T4.1:FEDFUNDS\|STAR; T4.1:FEDFUNDS\|ARMA |

**Other chain sources in the R1 workflow** (from `corrected_r1_summary.json`, the replay run `correction-20261103T070846-949fcd76`):

| Source | Count | Meaning in the integrated release |
|---|---|---|
| `published` | 48 | baseline chains re-read from the base tree (§3, stage 1). Two of them, `forecasting:UNRATE\|MSAR` and its twin `T4.8:UNRATE\|240:MSAR`, are re-read from the **B1-staged** files, so their provenance must say so. |
| `cache` | 17 | original estimates served whole from the original fit cache `3413465b508bb844` |
| `re-estimated` | 17 | the table above: Tier A archive + certified Tier B checkpoints, replayed through the merged refit cache with estimation refused |
| `unavailable` | 26 | chains no correction affects (the 43 unavailable in the replay run, minus the 17 now re-estimated); their original values are retained and labelled |

Total: 108 chains.

**Why the 17 cache chains are unaffected by the warm-start artifact [C].** The B3 stage-2 audit found that the cache-hit and live rules differ for exactly 5 chains:
- T4.1:FEDFUNDS|MSAR;
- T4.8:UNRATE 180, 240 and 300 MSAR;
- the baseline `forecasting:UNRATE|MSAR`.

None of the 17 cache chains is among them. Two of the five are B2 chains and one is the B1 chain; the remaining two are covered by the staged baseline correction. The dry run re-checks this (A7 in §5).

## 2. Two findings this plan must handle

### 2.1 F4.8 is stale in all three provisional releases [C]

**The gap.** F4.8_<series> plots `oos_r2_vs_benchmark` and `n_valid` at h=1 from `robustness/window_length_comparison.csv`. The pinned R1 workflow regenerates that table but **does not re-render F4.8**.

**The effect.** In releases `0573a8c`, `3bd24c4` and `292227e`, the UNRATE rows of the table changed under F1, but `F4.8_UNRATE.png/.pdf` are byte-identical to the published figure. In `292227e`, for example, UNRATE at 240 months, h=1:
- MSAR 0.692 → 0.192;
- STAR 0.555 → −0.104;
- ARMA 0.324 → 0.238.

The other five series' F4.8 figures are consistent with their tables.

**Evidence:**
- `evidence/integration_prep_20261106/f48_staleness/f48_staleness_by_release.csv` (6 stale files, all F4.8_UNRATE);
- the read-only checker `f48_staleness_check.py`, with a test.

**Classification.** An omitted regeneration, an implementation error under CLAUDE.md §6A. Correcting it changes no methodological choice. The final integration re-renders F4.8 for every series whose plotted inputs change (stage 3), and the provisional releases must not be quoted for F4.8_UNRATE.

### 2.2 Non-workflow outputs fed by the Tier B chains [C]

**The gap.** The R1 workflow regenerates 93 files. It does **not** regenerate:
- `models/fit_records.{csv,parquet}`;
- `robustness/T4.7_failure_registry.csv` and `T4.7_status_counts.csv`;
- F4.8;
- `manifests/output_inventory.csv`.

`forecasts/forecast_origin_audit.csv` is also outside the workflow, but it holds baseline rows only, so B1 already handled it.

**The fit records hold the robustness chains too.** For UNRATE MSAR (p=4, K=2) they contain:
- 764 records at 180 months;
- 2,111 at 240 months (the B1 builder located the baseline and T4.8-twin blocks, 704 each; the remaining 703 match the 703 origins of T4.1);
- 644 at 300 months.

T4.7 aggregates over all of them.

**Consequences:**
- The Tier A release left these files byte-identical. That was correct, because AR is closed form and the re-estimates reproduce the published records.
- **For B2 it is not correct.** Its 43 FEDFUNDS T4.1 and 6 UNRATE 180 origins differ from the published records: T4.7 FEDFUNDS MSAR failed 52 → 49, and UNRATE MSAR adequate/fragile change.
- B1 (UNRATE 300) and B3 reproduce their published records, so their blocks must come out **identical**. This is a check, not a change.

## 3. Integration procedure (stages)

The order fixes the precedence: **published → B1 staged overlay → R1 workflow (Tier A + Tier B) → non-workflow dependents → validation → claims.** Each stage reads the previous stage's output only, never writes to an earlier one, and refuses on any mismatch.

| # | Stage | What it does | Code |
|---|---|---|---|
| 0 | **Preflight** | Checks the code checkout is at the pin with `code/src` and `code/config` clean; the frozen-data hash is `7e7dc769…`; matplotlib renders with defaults (`r1_render_guard`, matplotlib 3.11.2); the three certificates have the sha256 values in `certificates/MANIFEST.csv`; the original cache matches `3413465b508bb844` (143 parts, payload digest `7e283de3…`); the Tier A archive matches `df73c295…`. Records a hash listing of every protected input. | to write: `colab/r1_part8_integration.py --stage preflight` |
| 1 | **Base tree** | Materialises `WORK/base = output/ + output_staging/r1_b1_unrate_msar_20261106/`. Each overlay file is verified against `STAGED_FILES.csv`, and `.gz` files are decompressed and verified uncompressed. Every other file must match the published sha256. Refuses extra or missing files. The counter-provenance sidecar travels as metadata, not as an output file. | to write (`--stage base`) |
| 2 | **Aggregation** | `r1_tierb_aggregate.py` with `--original WORK/base`. Runs `discover → merge → walk_all → assemble → gates` exactly as implemented and tested (20 tests), with two changes: the plan is written **only** under `WORK/` (never to Drive), and every certificate is checked against `certificates/MANIFEST.csv`. Estimation is refused throughout. | existing, plus a `--plan-dir` option (to write) |
| 3 | **Non-workflow dependents** | On `WORK/assembly/release`, for each of the 9 Tier B chains (and the 8 Tier A chains as a no-change check): replace the chain's fit-record block with the re-estimated records. `spec_hash` is empty in the published fit records, so a block is located as in B1 (`find_blocks`): the contiguous run of records whose refit dates, windows and values equal the chain's published records, which the workflow re-derives. Exactly one match is required; then rebuild the T4.7 registry and status counts, F4.8 for every series whose plotted inputs changed, and the inventory. Every builder first **reproduces the published values from published inputs**, as in B1. | generalise `colab/r1_b1_staged_correction.py` §2a, 2c, 2f, 2g (to write) |
| 4 | **Validation** | An independent validator (a generalisation of `r1_b1_validate_staged.py`) applies the acceptance criteria in §5 and writes a cell-level diff against three references: (a) published `output/`, (b) the B1 staged tree, (c) the Tier A release `292227e`. | to write |
| 5 | **Claims and jury** | Re-extracts every number quoted in `claim_evidence_matrix_corrected.csv` from the validated tree, gives each claim and jury ID (Part 2) its status transition, and lists every quoted number in the Part 8 reports that changes. **No prose is edited in the dry run.** | to write: `reports/part8/corrections/r1/claim_recheck.py` |

**Regeneration of affected outputs**, by kind:
- **Tables:** all 93 R1-workflow files, rebuilt from the integrated chain set (forecast tables T3.3–T3.6, the predictive tests T3.3A/B, the MCS, the robustness tables T4.1, T4.2, T4.4, T4.5, T4.TP1 and the window-length tables). Plus fit records, T4.7 and the inventory (stage 3).
- **Figures:**
  - F3.4–F3.6 (workflow);
  - F4.8 for every series whose plotted inputs changed (stage 3; UNRATE at least);
  - F2.x and F3.1–F3.3/F4.3 are expected unchanged, because they are in-sample or data figures. Validation checks this.
- **Predictive tests and robustness findings:** taken from the workflow tables; the claim recheck (stage 5) derives their findings.

## 4. Decisions needed before the final (non-dry) aggregation

| ID | Decision | Recommendation |
|---|---|---|
| **D1** | Should B2's two chains enter the release under the approved live warm-start rule? This brings in their 20 classification changes and 29 optimiser sensitivities (`tier_b_b1_staged_correction.md` §6). | Yes. It is the same implementation correction as the approved baseline one, now verified directly at all 1,390 origins. The dry run proceeds either way; the aggregation status stays `REVIEW_REQUIRED` until you decide. |
| **D2** | Re-render F4.8 for every series whose plotted inputs change, correcting the stale F4.8_UNRATE (§2.1)? | Yes (§6A). |
| **D3** | Where should the final release go (branch and folder)? Publication itself needs its own authorisation. | A new branch `part8-corrected-results/r1-final-<stamp>`, folder `output_corrected/`, as for the earlier releases. |

## 5. Non-publishing aggregation dry run: specification

### 5.1 Purpose and scope

The dry run executes stages 0–5 in full, with every output in a scratch work folder. **It publishes nothing.** It produces the evidence for D1–D3 and for the final authorisation.

**Out of scope:**
- estimation;
- any write to `output/`, `output_staging/`, the releases, Drive certificate or checkpoint folders, `approved-specs/` or `source-materials/`;
- `git commit` or `git push` from the run;
- prose edits;
- Part 9.

### 5.2 Where and how

**Location: Colab with Drive mounted.** The Tier B checkpoints, Tier A archive and original cache are all on Drive, and the aggregator was built and tested for that layout.

A local run is possible only after a read-only bundle cell exports the certified checkpoints. That is the same pattern as the supplementary recovery, but larger: about 6,000 payloads.

**Expected time:** about 1–2 hours, by analogy with the B3 read-only audit run.

**Procedure:**

```
# 1. new Colab session; Drive mounted read-only where possible
git clone <repo>; git checkout <orchestration commit, part8-r1-rescore>
git -C pinned worktree add <dir> 8aaa4217536ab3cb942dd248dd19ece7838a8d60   # scientific code
export MATPLOTLIBRC=$REPO/my-thesis/colab/matplotlibrc.default             # the guard also pins it
# 2. one command; the default is the dry run; there is no --publish option
python colab/r1_part8_integration.py \
    --code-dir <pinned>/my-thesis/code --published <repo>/my-thesis/output \
    --staged-overlay <repo>/my-thesis/output_staging/r1_b1_unrate_msar_20261106 \
    --drive-root /content/drive/MyDrive/<thesis root> --cache-root <original cache> \
    --tier-a-archive <archive> --tier-a-release <292227e:output_corrected> \
    --certificate-manifest <repo>/.../integration_prep_20261106/certificates/MANIFEST.csv \
    --unaffected-csv <repo>/.../nonpublished_chain_classification.csv \
    --work /content/part8_dryrun_<stamp>
# 3. export WORK/dryrun_report/ (small) to Drive for retrieval; the release tree stays in WORK
```

### 5.3 Safeguards (each one refuses the run; none is a warning)

1. **No estimation.** All stages run under `guard.estimation_forbidden()` and `tb.no_estimation_allowed()`. The fit-call counter must read 0, and `estimations_performed` must be empty in the legacy and corrected summaries.
2. **Write boundary.**
   - Before and after the run, take a sha256 listing of `output/`, `output_staging/`, the original cache, the Tier A archive, the three batch namespaces and their certificates. The two listings must be equal.
   - The run writes only under `--work`. A test runs the whole driver on fixtures with every other path read-only.
3. **No publication path.** The driver has no publish or push code. It refuses if `CONFIRM_PUBLISH` is set, and it never reads `GITHUB_TOKEN`.
4. **Pins.**
   - The scientific code is at `8aaa4217…`, with `code/src` and `code/config` clean.
   - The orchestration commit is recorded.
   - Data hash `7e7dc769…`; config hash `949fcd76…`.
5. **Rendering.** `r1_render_guard.check_default_rendering("3.11.2")` passes before any figure is drawn; the record goes into the report.
6. **Certificates.** The three certificates have the sha256 values in `certificates/MANIFEST.csv`. The aggregator's own `discover` consistency checks still apply.
7. **Overlay integrity.** Stage 1 verifies all 461 base-tree files: 46 staged and 415 published.
8. **Status is never approval.** `scientific_approval = "not granted"`. The status line is never "passed".

### 5.4 Tests to write and pass before the run

| Test file | Covers |
|---|---|
| `test_r1_part8_integration.py` | base-tree materialisation (refuses a sha mismatch, a missing or extra file, a gz mismatch); write boundary; no publish path; preflight refusals (pin, data hash, rendering, certificate hash); plan written only under `--work` |
| `test_r1_integration_dependents.py` | fit-record block identification by record sequence (`spec_hash` is empty), refusing zero or several matches, since T4.1 and baseline chains share refit dates; reproduce-first refusal; T4.7 rebuild equals published on published input; F4.8 re-render chosen exactly for the series whose plotted inputs changed |
| `test_r1_integration_validator.py` | each acceptance criterion in §5.5 fails on a crafted violation |
| `test_claim_recheck.py` | re-extraction of each claim's quoted numbers from fixture tables; status transitions |
| existing suites | `test_r1_tierb_aggregate.py` (20), `test_r1_b1_staged_correction.py` (10), `test_render_guard.py` (6), `test_r1_correction.py` |

### 5.5 Acceptance criteria

The dry run is **accepted for review** only if all of the following hold:

| ID | Criterion |
|---|---|
| A1 | `estimations_performed` is empty (legacy and corrected); the fit-call counter is 0. |
| A2 | The protected-input listings before and after are equal. |
| A3 | Chain sources: re-estimated = the 17 chains of §1.1 exactly; cache = 17; unavailable = 26, all with `affected_by_correction = False`; published = 48. |
| A4 | No row has `correction_status = original_retained_pending_estimation`. |
| A5 | **Legacy reproduction against the base tree:** every file not fed by a re-estimated chain is `identical` or `equal_within_fp_tolerance`. This includes the B1-staged files, which the legacy run must reproduce. |
| A6 | T4.2 tables are identical to the Tier A release. |
| A7 | **The 17 cache chains** are identical, origin by origin, to their published records (status, codes, loglik). The 5 rule-sensitive chains are absent from the cache source. |
| A8 | **Re-estimated chains against their certificates:** per-chain status counts equal the certificate's. Records of B1, B3 and Tier A are identical to the published records. B2's records differ only at the origins listed in `b2_direct_review/b2_vs_original_cache_by_origin.csv.gz`. |
| A9 | **Baseline:** `forecasting:UNRATE\|MSAR` and `T4.8:UNRATE\|240:MSAR` in the release equal the B1-staged chain (704 records; valid 698 / failed 6), and their release provenance cites `b1-staged-20261106T154902Z`. |
| A10 | **Non-workflow dependents:** each builder reproduced the published values from published inputs before building. Fit-record blocks are replaced only for chains whose records changed. T4.7 status counts equal those recomputed from the final fit records. The inventory hashes equal the files' hashes. |
| A11 | **Figures:** F4.8 is re-rendered exactly for the series whose plotted inputs changed. Running `f48_staleness_check.py` on the dry-run release gives 0 stale files. All other figures are byte-identical to the base tree, or regenerated by the workflow with a sidecar. |
| A12 | **Cell-level change sets** against published, B1-staged and Tier A are complete. Every decision-like change (classifications, test decisions, MCS membership, ranks) is listed. Each one is explained by a chain change (F1/F2/F3/F4/F7.1/F8, B1, Tier A, B2, B3) in the explanation table. Unexplained changes: 0. |
| A13 | **Provenance:** every changed row carries the dry-run run ID; unchanged rows keep their original provenance; the manifest records data hash, config hash, pin, orchestration commit, run ID and timestamp (CLAUDE.md §8). |
| A14 | **Claims:** every claim in `claim_evidence_matrix_corrected.csv` is re-extracted. Its status transition is listed with the supporting files. Every jury ID mapped there has a status. Claims whose evidence changes are flagged for review, and none is silently kept. |
| A15 | **Status:** the aggregation status follows mechanically from the certificates and gates. While D1 is open, `COMPUTATION_COMPLETE_REVIEW_REQUIRED` is the expected status, because of B2. |

**Exit codes:** 0 = accepted, nothing to review beyond reported sensitivity; 4 = accepted, review required; 1 = refused, with every failed criterion listed.

### 5.6 Expected output artifacts (all under `--work`; nothing is published)

```
WORK/
  preflight.json                 pins, hashes, rendering record, protected-input listing (before)
  base/                          materialised published + B1 overlay (461 files) + base_manifest.csv
  merged_refit/fits/             Tier A + certified Tier B payloads (merge report)
  assembly/legacy/               pinned workflow, legacy mode (r1_summary.json, r1_comparison.csv)
  assembly/corrected/            pinned workflow, corrected mode
  assembly/release/              assembled release before stage 3
  release/                       final dry-run release tree (after stage 3)
  dryrun_report/
    aggregation_plan.json        status, review items, sensitivity, gates (scientific_approval: not granted)
    acceptance.json              A1–A15, each pass/fail with detail
    chain_sources.csv            108 chains: source, provenance, run ID, certificate
    dependents_report.json       fit-record blocks replaced, T4.7 delta, F4.8 re-rendered, inventory
    cells_vs_published.csv.gz    cell-level change set
    cells_vs_b1_staged.csv.gz
    cells_vs_tier_a.csv.gz
    decision_changes.csv         every decision-like change with its explanation
    figures_changed.csv
    claims_recheck.csv           claim ID, jury IDs, old and new evidence values, status transition
    report_numbers_changed.csv   every number in reports/part8/*.md that the dry run changes
    protected_inputs_after.json  listing (after); equality with preflight asserted
    README.md                    how to read the above
```

## 6. After the dry run (each step needs its own authorisation)

1. Your review of the dry-run report, and decisions D1–D3.
2. The final aggregation: the same command with a publication target, under the existing Step 8 publication safeguards (dry run by default, `CONFIRM_PUBLISH`).
3. Update the Part 8 reports (`full_empirical_analysis_report.md`, `main_findings.md`, `robustness_findings.md`, `jury_resolution_status.md`, `final_claims_allowed.md`) from `claims_recheck.csv`, with every number traced to `output_corrected/`.
4. Part 9 (external), only after Part 8 is approved.
