# Local dry run of the D3 release workflow (9 November 2026)

This is a real-data dry run of `colab/r1_part8_final_release.py`. Nothing was pushed or written to Drive. The local release branch and worktree it created were deleted afterwards.

**Input.** The local archive-equivalent tree.
- Its 12 F3.4 files are byte-identical to the archive, and its other files match the archive inventory except for run provenance.
- `NUMBERS_RUN_ID` was set to the local tree's run ID, because the sidecar check requires the numbers run.
- In Colab the archive itself is used, so its own run ID applies: `correction-20261109T080220-949fcd76`.

**Files**

| File | Content |
|---|---|
| `d3_dryrun_report.json` | render check (F8 off = archive, F8 on = approved, all 12); assembly (465 files, 440 identical, 25 changed); git verification of the staged commit (parent = pin, 469 blobs = 465 files + 4 record files); Drive payload (465 members); publication state `not_authorized`; no Drive write; no remote branch |
| `release_manifest.json`, `RELEASE.md`, `archive_to_release_diff.csv` | the release record produced by the dry run. Its identities are those of the dry run, not of the real release |
| `example_F3.4_CPIAUCSL.png.provenance.json` | a release sidecar, separating `run_id`/`numbers_run_id` from `figure_operation` |
