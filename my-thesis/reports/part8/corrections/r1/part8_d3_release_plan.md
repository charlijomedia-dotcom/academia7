# D3: publication plan for the final corrected Part 8 release (9 November 2026)

**Status: PLAN ONLY. Nothing is published, pushed to a release branch or written to Drive.** It is executed only on your explicit instruction, after ChatGPT's review.

## 1. What is released

The release is the verified archived candidate `archive-20261109T080914Z-3c7d68`, with **exactly one presentation amendment, F8**, which you approved on 9 November 2026.

**Content: 465 files**, the same paths as the archive.

| Files | Count | Source | Rule |
|---|---|---|---|
| All tables, forecasts, fit records, manifests and the other figures and sidecars | 440 | archive `release.tar.gz` | **byte-identical to the archive** (sha256 = `archive_inventory.csv`) |
| `figures/F3.4_<target>.png` and `.pdf` (6 targets) | 12 | re-rendered with F8 on, from the archived forecasts | sha256 must equal `f8_review/f8_figure_hashes.csv` (`f8_sha256`) |
| `figures/F3.4_<target>.{png,pdf}.provenance.json` | 12 | rewritten | the archived keys plus `presentation_amendment`, `rendered_from` and `figure_sha256` (`f8_review/after_sidecars_proposed/`); `run_id` and `created_utc` are those of the release run |
| `manifests/output_inventory.csv` | 1 | updated | only the 24 rows above change (sha256, bytes, `source = presentation_amendment_f8`); every other row is byte-identical |

**What does not change.**
- No number, test, decision, forecast, fit record or protected input changes. Scientific pin `8aaa4217`, approved methodology, data snapshot `7e7dc769…` and configuration `949fcd76…` are all unchanged.
- No estimation.

## 2. Destination

### 2.1 GitHub

- **New branch:** `part8-corrected-results/final-<YYYYMMDD>`, with the date of execution. The assembly refuses if the branch already exists.
- **One commit** whose parent is the scientific pin `8aaa4217536ab3cb942dd248dd19ece7838a8d60`, as for the earlier releases `0573a8c`, `3bd24c4` and `292227e`. It adds:
  - `my-thesis/output_corrected/`, the 465 files of §1. The layout is as in the earlier releases. `fit_records.csv` is 67 MB, below GitHub's 100 MB limit, as in `292227e`;
  - `my-thesis/release/part8_final/`, the release record (§4).
- **Rules:**
  - No force-push, no tag moved, no existing branch modified.
  - `part8-results/baseline-20261030T173044-949fcd76` (`0662945`) and the three provisional release branches stay as they are.

### 2.2 Reports

The final reports go on `part8-r1-rescore` in a **new** directory, `my-thesis/reports/part8/final/`:
- the five reports;
- `claim_evidence_matrix_final.csv`;
- `CHANGELOG.md`.

**How they are made.** They are copied from `drafts_integrated_20261108/` once you approve. Only the banner changes, from "DRAFT" to "FINAL", naming the release branch, commit and run. Every path is then relative to `output_corrected/`.

**What stays.** The historical reports in `reports/part8/*.md`, `claim_evidence_matrix_adjudicated.csv` and the drafts directory stay unchanged. The pipeline-registered `output/manifests/claim_evidence_matrix.csv` stays untouched too; the final matrix is a report file, as decided before.

### 2.3 Google Drive

- **New folder:** `KillyPhD/Part8_K3_InSample_2026-10-29/baseline/r1_part8_final_release/<release id>/`.
- **Contents:** `release.tar.gz` (deterministic tar of the 465 files), `release_inventory.csv`, `release_manifest.json` and `acceptance_report.json`.
- The archive tool's no-overwrite and path-escape guards apply.
- The candidate archive `archive-20261109T080914Z-3c7d68` and every other Drive folder stay untouched.

## 3. Procedure

This is a non-estimating assembly in Colab: the 48 MB archive is on Drive. It is a new cell set to be generated and pinned like the archive notebook.

1. **Pins.**
   - Scientific code at `8aaa4217`; the F8 renderer `f8_review/f8_render.py` and the assembly tool fetched by `git show` from the commit you approve, each sha256-pinned.
   - Render guard: matplotlib 3.11.2, empty rc, DejaVu Sans.
   - The estimation guard stays active (`guard.estimation_forbidden`).
2. **Verify the archive.**
   - `release.tar.gz` sha256 must be `54b61285a732f44d9ef9f1a5e97e6a04f45f287f49dbcf044e6d2574d1d7b4ee`.
   - `archive_inventory.csv` must be `24ee8bee…209a58`.
   - `verify_archive` must pass: all 465 members against the inventory.
   - Extract to a fresh directory.
3. **F3.4 gate before.** Render with F8 **off** from the extracted forecasts. All 12 files must equal the archived bytes. This is the same check as in the review, now on the archive itself.
4. **F8 render.** Render with F8 **on**. All 12 files must equal the reviewed hashes in `f8_figure_hashes.csv`. Write the 12 sidecars.
5. **Assemble.**
   - Copy the 440 unchanged files and verify each byte-for-byte against the archive.
   - Add the 24 amended files.
   - Rewrite the 24 inventory rows.
   - **Refuse** unless the tree differs from the archive in exactly those 25 paths (24 files plus the inventory).
6. **Equivalence statement.**
   - `acceptance_report.json` lists the 25 differing paths with reasons, the 440 identical ones, and the F3.4 gate results.
   - It confirms that no table, forecast or fit file differs; the sha256 values are compared with the archive.
7. **Write to Drive** (§2.3). Re-read with `verify_archive`.
8. **Commit and push the release branch** (§2.1). This needs a GitHub write credential in Colab. Alternatively, I commit from this environment after downloading the tar, if you prefer. Verify that the pushed tree's file hashes equal `release_inventory.csv`.
9. **Reports** (§2.2), on `part8-r1-rescore`.
10. **Post-release check**, independent: ChatGPT downloads the tar and the branch and compares them with `release_inventory.csv`.

**Stop conditions.** Any hash mismatch, an existing branch or folder, a render-guard failure, or a difference outside the 25 paths stops the procedure with nothing published.

## 4. Release record (`my-thesis/release/part8_final/`)

| File | Content |
|---|---|
| `RELEASE.md` | what the release is; the F8 amendment; limitations (F6, optimiser sensitivity, multiplicity, degenerate STAR tests, sample-dependent rankings, the C16 audit sensitivity); how to verify |
| `release_manifest.json` | release id and run id; the source identities in §5; release tar and inventory sha256; the 25 differing paths |
| `release_inventory.csv` | path, bytes and sha256 of all 465 files |
| `archive_to_release_diff.csv` | for each of the 25 paths: archived sha256, release sha256, reason |

## 5. Exact source identities

| Item | Identity |
|---|---|
| Scientific pin (code of every estimate and figure) | `8aaa4217536ab3cb942dd248dd19ece7838a8d60` |
| Original estimation run | `baseline-20261030T173044-949fcd76`, results `066294544e8ff84f3c2c73ab647c8d13331dcac1` |
| Data snapshot / configuration | `7e7dc769bd63ca4951ef55430180f413de62c9dc53a275af50ad277a715b832a` / `949fcd76769048e3322f1595cd9bfb26006f8dcb692c17d16d3a9e5dab61db8e` |
| Integration orchestration | `a2c3171dbadc80f8821fdb91877d82622a1ff171` |
| Audited integration session | `integration-20261108T052245Z-9bba8e`, run `correction-20261108T053328-949fcd76` (export manifest `b7e585f3…f57612`) |
| Archived candidate | `archive-20261109T080914Z-3c7d68`: run `correction-20261109T080220-949fcd76`, archive tool `878d9289986e48bcf40c8ff4e32f22f620cf0937`, tar `54b61285…d7b4ee`, inventory `24ee8bee…209a58` |
| B2 acceptance | `corrections/r1/b2_scientific_adjudication.md`; certificate `c8c90ba0…` (REVIEW_REQUIRED, preserved) |
| F8 review package | `corrections/r1/f8_review/` (this commit) |
| Accepted reports and matrix | `258a907fa10d5c79a7a83323ba4790f6d7144321`, plus the F8/F6 updates of this commit |

## 6. Preserved, not touched

- Results commit `0662945` and branch `part8-results/baseline-…`.
- Provisional releases `0573a8c`, `3bd24c4` and `292227e` and their branches.
- The candidate archive and the audited export on Drive.
- Certificates and checkpoints; the original fit cache.
- `output/`; `approved-specs/`; `source-materials/`.

## 7. Open decisions for you

1. **Branch name** `part8-corrected-results/final-<date>`, or another name.
2. **Who pushes the release branch:** Colab with a write credential, or this environment from the downloaded tar.
3. **R1-06 conditional status.** It becomes RESOLVED only if the release carries the F8 figures. The residual M2SL diagnostic-panel overlap (`f8_figure_review.md` §5) is accepted as a presentation note, not changed.
