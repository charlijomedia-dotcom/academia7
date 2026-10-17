# Part 7 — Reproducibility report

**Date:** 16 October 2026
**Code state:** `b255d44` on `claude/trusting-feynman-871wks`
**Part 6 baseline approved at:** `249aa54`
**Objective:** demonstrate that a researcher can obtain this repository and reproduce the
complete empirical pipeline from the frozen dataset using the documented Python entry
point — without Claude Code, without FRED API access, and without manual intervention.

---

## 1. Summary

Reproducibility is demonstrated. Four genuine defects were found and corrected, three of
which would have stopped or corrupted a researcher's attempt:

| # | Defect | Severity |
|---|---|---|
| 1 | A baseline run's own outputs made the working tree dirty, so **every subsequent baseline run refused to start** | blocking |
| 2 | `--data-only` overwrote the run manifest describing the run whose outputs sat beside it | provenance |
| 3 | PDF figures embedded a timestamp, so artifacts could not be verified by checksum | verification |
| 4 | A clean-tree test asserted nothing after the check was rewritten | test integrity |
| 5 | The documented `.venv` location was not gitignored, so **the documented setup itself blocked the first baseline run** | blocking |

No methodological decision, approved threshold, specification or datum was changed.

## 2. Environment and installation (objective 1)

A fresh virtual environment was created and populated **only** from the committed lock
file. Every pin resolved exactly.

```
python -m venv cleanenv
cleanenv/bin/python -m pip install -r code/requirements.lock.txt
```

| | Version |
|---|---|
| Python | 3.11.15 |
| numpy / scipy / pandas | 2.4.6 / 1.17.1 / 3.0.6 |
| statsmodels / arch | 0.15.0 / 8.0.0 |
| matplotlib / pyarrow | 3.11.2 / 26.0.0 |
| psutil / joblib / PyYAML / tabulate | 7.2.2 / 1.6.0 / 6.0.1 / 0.10.0 |
| pytest / pytest-cov | 9.1.1 / 7.1.0 |

Transitive dependencies resolved to 33 packages in total. The project itself needs no
installation: `run_all.py` places `src` on the path.

**R is not required.** It was used once to generate reference values for the Tsay test;
those values are committed in `tests/fixtures/tsay_reference_cases.json` with the R and
TSA versions that produced them, and the test reads them from there.

## 3. Single documented command (objective 2)

All three modes were executed in the clean environment with `FRED_API_KEY` **unset**:

| Command | Result |
|---|---|
| `python run_all.py --data-only` | Verified hashes, loaded the frozen input, wrote nothing |
| `python run_all.py --smoke-test` | All ten stages, 183 files, 640 fits |
| `python run_all.py` | Full baseline — **not executed**, reserved for Part 8 |

No network request is made on any of these paths.

## 4. End-to-end demonstration (objective 3)

Two complete runs of the approved reduced-computation configuration, each from a cold
cache, in the clean environment without an API key. Stage timings from run A:

| Stage | Seconds |
|---|---:|
| data / stationarity / nonlinearity / specification | 0.4 / 1.5 / 0.1 / 13 |
| adequacy | 296 |
| forecasting | 1031 |
| evaluation | 3.6 |
| robustness | 442 |
| finalize | 0.1 |

This is a code-path demonstration and **is not** a substitute for the Part 8 empirical
execution, which uses all six targets at the approved window lengths.

## 5. Configuration for the eventual full run (objective 4)

| Check | Result |
|---|---|
| Approved targets configured | 6: GDPC1 (Q), CPIAUCSL, UNRATE, INDPRO, FEDFUNDS, M2SL (M) |
| USREC | `evaluation_only`, never a forecast target |
| Transformations | 4 × `logdiff_annualized`; UNRATE and FEDFUNDS by the §3.4 decision rule |
| Baseline vs robustness separation | `forecast_tests/` 7 files, `robustness/` 20 files, **0 overlap** |
| Horizons reach the approved endpoints | INDPRO h=1,3,6,12 → 2026-08-01; GDPC1 h=1,2,4 → 2026-04-01 (2026Q2) |

## 6. Integrity, seeds, cache, manifests, failure reporting (objective 5)

| Check | Evidence |
|---|---|
| Canonical CSV hash | `7e7dc769…b832a`, recomputed from disk, matches the manifest |
| Parent source manifest hash | `7523966b…` recorded beside it |
| Deterministic seeds | master 20261005; MCS 20261005; HLZ critical values 20261005 |
| Checkpoints | 9 stages recorded, all `complete` |
| Fit cache | 468 payloads; an interrupted run resumes rather than restarts |
| Output inventory | 113 entries, every SHA-256 64 characters, no empty file |
| Run manifest | run ID, data hash, commit, config hash, vintage date, environment, dependency-lock hash |
| Failure reporting | 480 events across 6 reason codes; the data-gap register is kept separate |

## 7. Determinism across independent runs (objective 6)

Run A and run B, independent, cold caches, same configuration and data.

| Outcome | Files |
|---|---:|
| Byte-identical | 40 |
| Identical once run metadata is removed | 112 |
| Genuinely different | 31 |

*(Measured on the code as it stood before the PDF timestamp fix — see "What was and was
not measured" below.)*

All 31 were PDF figures, differing by **exactly 5 bytes of 16850** — the embedded
`/CreationDate`. All 31 PNG figures were byte-identical.

The comparison deliberately kept `data_snapshot_hash` and `config_hash` **out** of the
"runtime metadata" bucket, so it proves the two runs had identical inputs rather than
assuming it: those columns matched in every file. Legitimate differences were confined to
`run_id`, `created_utc`, wall-clock timings, and `code_commit_sha` (documentation was
committed between the runs).

### What was and was not measured

To be precise about the evidence, because the sequence matters:

- **Both complete cold-cache runs were executed *before* the PDF timestamp fix.** The
  comparison above is therefore a pre-fix measurement. It is what identified the embedded
  timestamp as the sole remaining source of variation.
- **The PDF fix was verified separately**, by a targeted regression test that saves the
  same figure twice with a forced clock-second gap between the saves and requires the
  SHA-256 digests to match in both PNG and PDF. That test is part of the suite
  (`test_saved_figures_are_byte_reproducible_across_runs`).
- **No two-run, byte-for-byte comparison of the complete pipeline has been performed on
  the post-fix code, and none is claimed here.** The expected outcome is that the 31 PDFs
  would join the byte-identical set, since the five differing bytes were the timestamp and
  that field is now omitted. Confirming it would require two further complete runs, which
  were judged not to be worth the compute for a change whose effect is demonstrated
  directly by the regression test.

## 8. Clean-tree protection and generated outputs (objective 8)

**A blocking defect, found and corrected.**

`output/` is deliberately not gitignored, because Part 5 requires every thesis-facing
number to be traceable to a file under it. The first baseline run therefore wrote ~114
artifacts into the tracked tree, `git_tree_dirty()` became true, and every later baseline
run died with `DirtyTreeError`. Demonstrated before fixing: copying a single output file
into `output/diagnostics/` was enough to make `run_all.py` refuse to start.

Decision D14 protects the claim that a baseline result is reproducible from the commit
recorded beside it. That claim rests on the run's **inputs** — code, configuration, frozen
data, approved specifications — not on its own artifacts, which are the result.
`require_clean_tree` now excludes paths under the directories the run itself writes, fails
on a change anywhere else, and names the offending paths. **The safeguard is narrower in
scope and no weaker**, verified both ways:

- with outputs present, a baseline run proceeds;
- with a source file touched, it still refuses and names it.

This also exposed a parsing bug: `_git` returned `stdout.strip()`, removing the leading
space of the first porcelain status line and shifting the first path by one character
(`y-thesis/...`). Fixed.

Secondary finding: `--data-only` wrote the run manifest before its early return, so a
verification check overwrote the manifest describing the run whose outputs sat beside it.
The pipeline's finalize stage is now the single writer; `--data-only` leaves the tracked
tree untouched (0 modified files, verified).

## 8a. The documented virtual environment blocked a baseline run

**A second blocking defect, found in review of this report and corrected.**

`REPRODUCING.md` §4 instructs the researcher to create the virtual environment at
`my-thesis/.venv`, and `my-thesis/.gitignore` did not exclude it. Reproduced from a fresh
clone: the checkout is clean, `python -m venv .venv` adds one untracked entry
`?? my-thesis/.venv/`, and `python run_all.py --data-only` then dies with

```
DirtyTreeError: ... uncommitted changes outside the run's own output directories ...:
my-thesis/.venv/
```

So a researcher following the instructions exactly could not run a baseline analysis at
all. The smoke namespace was unaffected, which is why earlier Part 7 checks did not catch
it.

A virtual environment is **not** an input to the analysis: its contents are fully
determined by `code/requirements.lock.txt`, whose SHA-256 every run manifest records.
`.gitignore` now excludes `.venv/`, `venv/`, `ENV/`, `env/`, and — separately — `.env` and
`.env.*`, since an environment file may hold a FRED API key that must never reach the
repository (Comp §2).

**No protection was weakened.** Verified from a fresh clone after the fix: the documented
setup proceeds, and a modification to code or to an approved specification is still
refused and named. Twelve regression tests cover this, including that a directory merely
*starting* with `venv` is not swallowed by the rule, and that no ignore rule covers
`output/`, `data/`, `approved-specs/`, `code/` or `notes/`.

## 9. Smoke evidence versus thesis results (objective 9)

Separated by construction and impossible to confuse:

| | Full run | Reduced run |
|---|---|---|
| Output root | `output/` | `smoke_output/` |
| Run ID prefix in every table | `baseline-` | `smoke-` |
| Version control | tracked | gitignored |

Every table carries its run ID in a provenance column, so a number quoted from a check
rather than a result is identifiable from the file alone.

## 10. Tests

```
681 passed, 0 failed, 0 skipped, 0 errors    (28m44s)
```

Run in the clean environment, from the locked dependencies, with `FRED_API_KEY` unset.
Collected = 681 = passed. Part 7 added 21 tests: 16 for the clean-tree safeguard against a
throwaway repository, 4 for the corrected contract in `test_core.py`, and 1 for figure
byte-reproducibility.

## 11. Limitations

1. **The full baseline run has not been executed.** Part 7 demonstrates reproducibility on
   the approved reduced configuration; the full run is Part 8 and requires separate
   approval.
2. **Runtime.** The full run is a multi-hour job dominated by the three-regime
   Markov-switching chains. The fit cache makes it resumable.
3. **Platform.** Verified on Linux, Python 3.11.15. The Windows instructions in
   `REPRODUCING.md` are written from the same locked dependency set but have not been
   executed on Windows hardware; no platform-specific code paths exist, and figure output
   uses a non-interactive backend.
4. **Floating-point portability.** Byte-identical results are demonstrated on one machine.
   Across different CPU architectures or BLAS builds, last-digit differences in optimizer
   output are possible. Seeds, data and configuration are fixed, so any such difference is
   attributable to the numerical environment, which the manifest records.

## 12. Unresolved blockers

**None.**

---

## Reproduction, in short

```bash
git clone https://github.com/charlijomedia-dotcom/academia7.git
cd academia7/my-thesis
python3.11 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r code/requirements.lock.txt
cd code
python run_all.py --data-only      # verify the frozen data
python run_all.py --smoke-test     # reduced-computation check, ~30 minutes
python run_all.py                  # full run, several hours (Part 8)
```

Windows-specific instructions, hardware guidance and troubleshooting are in
`my-thesis/REPRODUCING.md`.
