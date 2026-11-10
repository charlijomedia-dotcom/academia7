# Publication of `part8-final-20261109`

- Branch: `part8-corrected-results/final-20261109`
- Commit: `9817daf91ac4cb4aaa42c2bef5deaff5b674841b`
- Drive: `baseline/r1_part8_final_release/part8-final-20261109/`, release.tar.gz sha256 `a9d1a028d0e0b09e9fff3a98d7593cb51026ce70cff1db25b12d1beb225728b8`
- Published (UTC date): 20261110
- Status file: `publication_status.json` (copied from the Drive folder)

## Provenance of the published release

| Identity | Value |
|---|---|
| Release | `part8-final-20261109`; branch `part8-corrected-results/final-20261109`; commit `9817daf91ac4cb4aaa42c2bef5deaff5b674841b`, whose parent is the scientific pin `8aaa4217536ab3cb942dd248dd19ece7838a8d60` |
| Canonical numbers | `my-thesis/output/` in that commit: 465 files, with sha256 in `my-thesis/release/part8_final/release_inventory.csv` |
| Numbers run | `correction-20261109T080220-949fcd76` (archive `archive-20261109T080914Z-3c7d68`), equivalent to the audited run `correction-20261108T053328-949fcd76`; no estimation |
| F3.4 figures | F8 re-render `f8render-20261110T032042Z-dc0f7b` (approved 9 November 2026; presentation only) |
| Publication | `publish-20261110T032055Z-0585a2`; release tool commit `3243c6b0e28faf7da2040be3e0f1b1d5e79e74c9`; Drive `release.tar.gz` sha256 `a9d1a028d0e0b09e9fff3a98d7593cb51026ce70cff1db25b12d1beb225728b8` |

## Verification

All of this was verified on 10 November 2026; the evidence is in `corrections/r1/evidence/part8_final_publication_20261110/`.

- **Status file.** `publication_status.json` was read from the final Drive folder. It is 931 bytes and names the commit and tar sha256 above. `finalize_reports.py` ran with its remote check: `git ls-remote` shows the branch at the commit, and the commit's release manifest names this release.
- **The commit** (`verified_release.json`):
  - its parent is the pin;
  - only `my-thesis/output/` (123 modified, 4 added) and `my-thesis/release/part8_final/` (4 added) change, with nothing deleted;
  - all 465 files match the release inventory;
  - 440 files are identical to the candidate archive, and exactly the 25 allowed paths differ;
  - the 12 F3.4 files equal the approved F8 hashes;
  - the sidecars keep the numbers run and name the F8 operation.
- **The numbers** (`integrated_vs_published.json`):
  - the 28 integrated tables from which every number in these reports is quoted equal the published files in all **2,665,073 cells**, excluding provenance, runtime and `correction_status` columns (rtol 1e-9);
  - this covers the T4.1 and window-length tables, which could not be cross-checked locally before publication;
  - the published T4.7 registry has 34,122 rows, and its 17 category/reason-code counts equal those cited.
- **References** (`reference_check.csv`): all 169 `output/` references in the final reports and the matrix exist at the release commit. The only exception is the per-target template `forecasts/forecasts_<x>.csv` in the source-key table, whose six instances all exist.
- **Independent review.** ChatGPT verified the published Drive tarball: 465 files equal the inventory, 440 are identical to the archive, and exactly the 25 approved paths differ.

**Status.** Formal Part 8 approval is pending the closure review. Part 9 has not started.
