# Verification of the Part 8 candidate archive (9 November 2026)

**Archive:** `KillyPhD/Part8_K3_InSample_2026-10-29/baseline/r1_part8_candidate_archive/archive-20261109T080914Z-3c7d68/`. The Drive folder ID is `1d8-uFSMZGoFbpK7EGMOVsiMhTejpygcW`; the folder holds four files.

**Verdict.** The archive is consistent with its manifest and with the audited session. Its scientific identity is the audited integration candidate. One limit applies to my own check: I could not download `release.tar.gz` itself (§3).

## 1. What I checked myself

| Check | Result | Evidence |
|---|---|---|
| `archive_manifest.json` | `published: false`, `estimation: none`, `files: 465`; `release_tar_sha256` `54b61285a732f44d9ef9f1a5e97e6a04f45f287f49dbcf044e6d2574d1d7b4ee`, equal to the value you reported | `evidence/archive_verification_20261109/manifest_head.txt` |
| Run identity | mode `reconstruct`; archive tool `878d9289986e48bcf40c8ff4e32f22f620cf0937` (the corrected comparator); orchestration `a2c3171dbadc80f8821fdb91877d82622a1ff171`; scientific pin `8aaa4217536ab3cb942dd248dd19ece7838a8d60` (unchanged); source session `integration-20261109T075322Z-16749b`, run `correction-20261109T080220-949fcd76`; audited session `integration-20261108T052245Z-9bba8e`, run `correction-20261108T053328-949fcd76`; audited export-manifest sha256 `b7e585f3…f57612` | same |
| Gate checks | all nine true: exit code, accepted, all criteria pass, nothing unexplained, not published, orchestration commit, scientific commit, reports identical, release inventory | same |
| Gate reports | 44 reports compared, 0 differing, 0 missing; only `console.log` not compared | same |
| `archive_inventory.csv` | sha256 `24ee8bee0ca0aca3850c2bffdb1e842e7576275c741d38ba7c09841886209a58`, equal to the manifest's `archive_inventory_sha256`; 465 rows | `evidence/archive_verification_20261109/archive_inventory.csv` |
| Release inventory | the inventory row for `manifests/output_inventory.csv` has sha256 `72c8530f…0f24da`, equal to the manifest's `release_inventory_sha256` | same |
| Against the audited inventory (464 files, committed export) | missing 0; extra 0 apart from the inventory file itself; 363 identical; 101 differ | committed export `integration_dryrun_audit_20261108/colab_export/release_manifests/output_inventory.csv` |
| The 101 differing files | 52 figure provenance sidecars; 2 run records (`correction_run_manifest.json`, `correction_summary.json`); 47 regenerated tables with provenance columns (including `T2.0A_frozen_manifest.csv`, `fit_records`, `T4.7_failure_registry.csv`). **No figure (.png/.pdf/.svg) differs.** **Every one of the 101 has the same byte size as in the audited release**, as expected when only fixed-width run IDs and timestamps change | computed from the two inventories |
| Gate's own count | `identical 363`, provenance-only 101 (464 − 363), refused 0, `inventory_vs_disk` empty, 465 files on disk | manifest gate section |

**Transcription note.** The connector delivers the manifest as base64 inline. I decoded its first part, which covers the identity, the shas, the checks and the inventory counts, from a manual copy. One key came out as `not_unexplained` instead of the tool's `nothing_unexplained` (the original text reads `nothing_unexplained: true`), so my copy has at least one copying error. For that reason I relied only on values that cross-check independently:
- the tar sha256 equals your report;
- the inventory sha256 and the release-inventory sha256 equal hashes I computed from the downloaded inventory;
- the commits equal the pinned constants.

## 2. Scientific identity

- **What the archived tree is.** A non-estimating reconstruction: the same orchestration and pin, the same frozen data and cache identity, and estimation refused.
- **Why it is the audited computation up to provenance.** It passed the strict gate:
  - the four `cells_vs_*` cell comparisons, `decision_changes`, `claims_recheck`, `jury_recheck`, `chain_sources`, the protected-input and cache-integrity reports, and all stage records are identical to the audited session's;
  - JSON reports differ only in `run_id`, `session` and timestamps, plus the one admitted field `aggregation_plan.json` `assembly.legacy_run_id`, whose structure was validated;
  - every figure and every original file is byte-identical.
- **Consequence.** The numbers in the report drafts, which come from the audited session's cell-level differences, are the numbers of the archived tree.
- **Provenance differs in the bytes.** Table `run_id` and `created_utc` columns name run `correction-20261109T080220-949fcd76`, not the audited `…053328…`. So citations should name the archive and its run.

## 3. What I could not check myself

- **The tar members.** `release.tar.gz` (47.9 MB) is above the connector's 10 MB download limit. The member-by-member check against `archive_inventory.csv` is therefore the independent review's: 465 members, 0 mismatches, archive and acceptance-report hashes matching the manifest.
- **T4.7 reason codes.** The archived `T4.7_failure_registry.csv` (10.8 MB, sha256 `6bcc84d4…e6e8d4`) is also above the limit. Its counts are verified by the independent review: 34,122 rows, 512 failed, 33,610 fragile, and all 17 category/reason-code counts equal to my local-rehearsal evidence.
  - My own check: the local-rehearsal registry has the same byte size (10,842,235 bytes) and a different sha256 (`27374e4e…19b9ff8`), as expected from different run provenance.
  - **Row-by-row identity of the rehearsal and the archive is not established**, and the drafts do not claim it.
- **`acceptance_report.json`.** I did not hash it. The independent review reports that it matches the manifest (`974691b7…baff6e`).

## 4. Nothing changed

No file in the archive, the audited evidence, `output/`, releases or certificates was modified. No estimation was performed, and nothing was published.
