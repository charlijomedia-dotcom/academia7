# STAGED correction B1: baseline `forecasting:UNRATE|MSAR` (not published)

**Status: staged for independent review.** This is not a release. `output/` (the published baseline) is unchanged, and so are the releases and the Tier A/B certificates. Nothing here replaces them until separately authorised.

## Contents

This folder holds **only the files that differ** from the published `output/` tree, at their published relative paths:

- 38 content files;
- the provenance sidecars of the 8 changed figures.

**The full staged tree** is the published `output/` with these files laid over it. Files over 5 MB are stored gzip-compressed (`.gz`, mtime 0). `STAGED_FILES.csv` lists every file with:
- the sha256 of the **uncompressed** staged file;
- the sha256 of the published file it replaces.

The other **415 of 461 published files are byte-identical** in the staged tree.

## What was corrected

**The implementation error.** In the published run, three fits made right after a failed fit (1982-10, 1982-11, 1982-12) lacked the approved D6 warm start. Because each fit warm-starts the next, the difference carried forward to 1983-06.

**The corrected chain:**
- the original fit-cache payloads under the approved live warm-start rule, through the pinned `rolling.run_chain`;
- **no model was estimated** (the estimators were refused, and fit calls were counted: 0);
- 704 of 704 origins from the original cache;
- valid 698 and failed 6 (published: 693 and 11);
- adequate/fragile/failed 440/258/6 (published: 433/260/11).

## How the files were made

**Workflow-regenerated tables:**
- the pinned R1 workflow in legacy mode, run on the published tree (reference) and on the corrected input (candidate);
- a cell changes only where the candidate differs from the reference;
- every other cell keeps the published text;
- changed rows carry the provenance `run_id = b1-staged-20261106T154902Z` and `code_commit_sha = 8aaa4217…` (the scientific pin).

**Dependent outputs** (built with the pinned table and figure builders; each first reproduced the published values from published inputs):
- fit records, both blocks of the chain: 13 origins each, of which 9 change the estimate and 4 change only diagnostics and timing;
- forecast origin audit;
- T4.7 registry and status counts;
- the 8 state-dependence Wald rows;
- F4.8_UNRATE;
- the inventory.

**Code:**
- `colab/r1_b1_staged_correction.py`: builder;
- `colab/r1_b1_validate_staged.py`: independent validation.

**Report:** `reports/part8/corrections/r1/tier_b_b1_staged_correction.md`. Evidence is in `reports/part8/corrections/r1/evidence/b1_staged_20261106/`.
