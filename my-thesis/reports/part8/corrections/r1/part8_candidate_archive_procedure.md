# Part 8 integrated candidate: non-publishing archive procedure

**Status: PREPARED, NOT RUN.** You authorised preparing the procedure on 8 November 2026. Running it waits for your separate authorisation after the independent review.

## 1. Purpose and constraints

**Purpose.** Preserve the exact 465-file candidate tree of the audited integration dry run, so that it can be reviewed independently. The audited run is:

| Item | Value |
|---|---|
| Session | `integration-20261108T052245Z-9bba8e` |
| Run | `correction-20261108T053328-949fcd76` |
| Orchestration | `a2c3171` |
| Scientific pin | `8aaa4217` |
| Audited export | 45 files, `export_manifest.json` sha256 `b7e585f3…f57612` |
| Release inventory | sha256 `d55721d3…827089` |

**Constraints:**
- No estimation, publication or `git push` from Colab.
- No write to `output/`, `output_staging/`, releases, certificates, checkpoints or caches.
- The only thing written is a **new** Drive folder: `baseline/r1_part8_candidate_archive/<archive session>/`. The tool refuses to write if that folder already exists or lies outside the parent folder.

## 2. Step 0: does the original tree still exist?

**I cannot see Colab runtimes. You need to establish this.**

- A Colab runtime belongs to one notebook. So only the **original** integration notebook can reach the tree, and only if its runtime of that session is still connected. The tree lives at `/content/r1_part8_integration/dryrun/integration-20261108T052245Z-9bba8e/release/`.
- **Check:** open the original notebook. If its runtime still shows as connected (not "Connect" or "Reconnect"), paste the preserve cell (§3) into it and run it.
- **Safe to try either way.** The cell's first statement checks the path. If the tree is gone, it prints `NOT FOUND … use r1_part8_candidate_archive.ipynb`, writes nothing and mounts nothing.

## 3. Mode A: preserve the exact files (preferred)

**What to run.** `colab/r1_part8_preserve_cell.py`, a single cell for the original notebook.

**What it does:**
1. Fetches `colab/r1_integration_archive.py` read-only from the pinned archive-tool commit with `git show`, and checks its sha256 against the value pinned in the cell.
2. Verifies the audited 45-file Drive export against its manifest sha256.
3. Runs `preserve_check`. Every one of the 465 files must match the audited inventory: sha256 and size for each, plus the inventory's own sha256. It refuses on any missing, extra or altered file.
4. Runs `write_archive` and `verify_archive` (§5).

**Provenance differences.** None are allowed: the files must be bit-identical.

## 4. Mode B: non-estimating reconstruction with a strict equivalence gate

Use this mode only if the tree is gone.

**What to run.** `colab/r1_part8_candidate_archive.ipynb`, a new notebook.

**What it does:**
- It refuses to reconstruct unless you set `ALLOW_RECONSTRUCTION = True`.
- It re-runs the **unchanged** dry run:
  - same orchestration (`a2c3171`) and pin (`8aaa4217`);
  - same frozen data and cache identity;
  - original fit cache read-only;
  - estimation refused;
  - `CONFIRM_PUBLISH = False`.
- It then applies `equivalence_gate` against the audited session. The archive is written only if **every** check passes.

**The gate checks:**

| What is compared | Requirement |
|---|---|
| Acceptance | exit code 4, as in the audited run; `accepted`; all A1–A15 criteria pass; `unexplained_differences.csv` empty; `published = False`; orchestration = `a2c3171`; scientific commit = `8aaa4217` |
| Numerical values | `cells_vs_published`, `cells_vs_claims_reference`, `cells_vs_tier_a` and `cells_vs_b1_staged` byte-identical. These are cell-level comparisons with relative tolerance 1e-9 and exclude only provenance, runtime and `correction_status` columns |
| Decisions | `decision_changes.csv`, `claims_recheck.csv`, `jury_recheck.csv` and `report_numbers_changed.csv` byte-identical |
| Chain statuses and sources | `chain_sources.csv`, `reestimated_chain_records.csv`, `aggregation_plan.json` and `stages/*.json` identical. JSON files are compared after removing only `run_id`, `session`, `started_utc`, `finished_utc`, `created_utc` and `recorded_utc` |
| Protected inputs | `protected_inputs_after.json` and the `cache_integrity/` reports identical (the same normalisation for JSON; gzip compared after decompression) |
| Release tree (465 files) | Identical to the audited inventory, except the identified provenance carriers below. Every figure (`.png`, `.pdf`, `.svg`) and every `original_unchanged` file must be byte-identical. A change of a file's source category is refused |

**Explicitly permitted provenance differences** (anything else refuses):
1. **Figure sidecars** (`*.provenance.json`): only `run_id`, `created_utc` and `code_commit_sha` may differ.
   - Every other key must equal the published or base sidecar.
   - The only annotation allowed is the exact F4.8 text: `integration_dry_run`, "re-rendered by the pinned code from the integrated window-length table (decision D2)".
   - `code_commit_sha` must be the pin.
2. **Run records:** `correction_run_manifest.json`, `correction_summary.json`, and `T2.0A_frozen_manifest.csv` (its `run_id` and `created_utc` columns).
3. **Regenerated tables** whose `run_id` and `created_utc` columns change. Each must be listed in the audited `files_vs_published.csv`, so that every other cell is fixed by the identical `cells_vs_*` reports.
4. **`console.log`:** not compared (timings and paths).

**Why bytes cannot be required in Mode B.** Each regenerated table stamps its own wall-clock time. A rebuilt tree therefore cannot reproduce the audited bytes of those files. Its numerical content is pinned by the cell reports.

## 5. What the archive contains

Folder: `baseline/r1_part8_candidate_archive/<archive session>/`

| File | Content |
|---|---|
| `release.tar.gz` | The 465 files. The tar is deterministic: sorted members, mtime 0, uid 0, mode 644, PAX format, gzip mtime 0 |
| `archive_inventory.csv` | path, bytes and sha256 of each of the 465 files |
| `acceptance_report.json` | The full preserve or gate report |
| `archive_manifest.json` | The sha256 of each of the three files above; `published: false`; `estimation: none`; the release inventory sha256; the gate result; the **run identity** |

The run identity records:
- the mode;
- the archive session;
- the archive-tool commit;
- the orchestration and scientific commits;
- the source session and run;
- the audited session and run;
- the audited export-manifest sha256;
- the Python version.

`verify_archive` re-reads the written archive. It checks the three shas and every tar member against the inventory, and requires exactly 465 members.

## 6. Validation done here (no Colab)

- **Unit tests.** `code/tests/unit/test_r1_integration_archive.py`, 21 tests. They cover:
  - export verification and tampering;
  - the export layout matching the integration notebook's export cell;
  - preserve accept and refuse (altered, extra or missing file);
  - the gate:
    - accepts provenance-only differences;
    - refuses a changed numerical result, a changed figure or original file, a non-provenance JSON change, a wrong exit code, an unlisted table, and bad sidecars (wrong pin, other content, wrong annotation);
  - archive determinism, no overwrite, no path escape, gate required, tampering detected;
  - the generated notebook and preserve cell are safe and pinned, with no push or publish;
  - the committed notebook equals the generator's output.
- **Smoke test on real data:** `evidence/part8_drafts_20261108/archive_gate_smoke_test_local_rehearsal.json`.
  - The inventory gate was run on the **local** partial rehearsal. That tree lacks the Drive-only B1 and B3 chains, so it must be refused, and it is.
  - Result: 360 files identical, 101 provenance-only, and exactly 3 refused:
    - `F4.8_UNRATE.png` and `.pdf`, whose source category differs;
    - `correction_file_comparison.csv`, which differs and is not a provenance carrier.
  - These are the files that genuinely differ without the Drive chains.

## 7. After the run

Send me the archive session name that the cell prints. I will then:
- verify the folder against its manifest;
- compare `archive_inventory.csv` with the audited inventory;
- report.

Nothing is published until you decide on D3.
