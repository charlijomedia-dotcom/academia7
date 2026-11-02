# Clean, pinned regeneration of the R1 corrected release (2 November 2026)

You asked: "Before final Part 8 approval, regenerate the release from a clean, pinned Git commit and confirm the corrected numbers reproduce."

## Why `0573a8c` recorded `code_tree_dirty: true`

| Run | Started (UTC) | Commit | Dirty |
|---|---|---|---|
| R1 legacy gate | 2026-11-01 15:17:30 | `77df9d8` | false |
| R1 corrected run, release `0573a8c` | 2026-11-01 15:22:13 | `77df9d8` | **true** |

Between these two runs I wrote two untracked report files into the repository:

- `reports/part8/corrections/r1/estimation_workload.py`, at 15:18:38;
- `reports/part8/corrections/r1/estimation_workload.csv`, at 15:18:41.

Neither file is read by the workflow. No code, configuration, data or specification file was uncommitted. The values in `0573a8c` were produced by the code at `77df9d8`.

**Safeguards added (commit `1ed9422`):**

- the run notes now record the exact uncommitted paths at start;
- `correct_from_published.py` refuses `--release` and `--legacy-staging` unless `git status --porcelain` is empty;
- it also refuses unless the legacy tree was produced by the same, clean commit.

## The clean regeneration

| | |
|---|---|
| Worktree | a fresh, detached worktree of commit `8aaa4217536ab3cb942dd248dd19ece7838a8d60`, with nothing else in it |
| `git status --porcelain` | empty before and after both runs |
| Legacy gate | 92 regenerated files: 83 identical, 9 within 1e-9 relative (the same 9 files and maxima as on 1 November), 0 different; `estimations_performed`: none |
| Corrected run | `correction-20261102T085012-949fcd76`; `code_commit_sha` = `8aaa421…`; `code_tree_dirty` = false; `uncommitted_paths_at_start` = []; `estimations_performed`: none |

## Comparison with the provisional release `0573a8c`

Provenance and run-time columns are ignored. The result is in `clean_vs_provisional_release.csv`.

- **446 files identical.** This covers every table, every forecast file and parquet, every data-audit file, and every figure other than those below.
- **19 files changed:**
  - F2.1 for UNRATE and FEDFUNDS, and F3.4 for all six targets (PDF and PNG). These are the deliberate figure changes in `figure_review.md`.
  - The three correction manifests (run ID, commit, inventory).

**The corrected numbers reproduce exactly from the clean, pinned commit.**

The regenerated release is published on a new branch, `part8-corrected-results/r1-clean-20261102`. `0573a8c` and the original results remain unchanged.
