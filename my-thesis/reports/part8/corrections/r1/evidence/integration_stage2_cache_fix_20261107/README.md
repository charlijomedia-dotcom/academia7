# Evidence: stage-2 refusal of the Part 8 integration dry run (7 November 2026)

This folder is evidence for `../../part8_integration_stage2_cache_fix.md`. It contains no scientific outputs and no estimation results.

| Path | Content |
|---|---|
| `colab_failure/` | `failure.json`, `console.log` and `export_manifest.json` exported by Colab session `integration-20261107T184004Z-93c0f8`. Their sha256 values match the manifest. |
| `reproduction_old_code/` | Local reproduction with the unmodified assembly code (`a21fdf2`): full listings of the merged refit cache after merge and after assembly, and `cache_diff.json` (1 added file, `README_R1_REFIT_CACHE.txt`; 0 removed; 0 modified). |
| `rehearsal_fixed_code/` | Rehearsal with the fix through the real `stage_aggregate` and stages 3–5: cache-integrity listings, stage-3 report, stage-4 acceptance, aggregation plan and unexplained differences (0 rows). |
| `old_vs_fixed.json` | File-by-file comparison of old and fixed outputs; differences are provenance only. |
| `warnings_old_vs_fixed.txt` | HLZ/DM and other warnings in old and fixed runs: identical messages and counts. |
| `scripts/` | The local scripts used (they replace Drive calls with local equivalents; 10 of 17 chains are available locally). |
