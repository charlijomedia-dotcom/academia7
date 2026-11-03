# R1 after Tier A: Step 8 fix, failure audit, unavailable chains, numerical warnings

Date: 3 November 2026. This review is static only: source-level fixes, targeted tests and analysis of the original release. Nothing was estimated, re-run or published.

- The scientific code pin is unchanged: `8aaa4217536ab3cb942dd248dd19ece7838a8d60`.
- Tier B and Step 8 publication are **not** authorised, and neither was executed.

## 1. Step 8 published the wrong release after Tier A (fixed)

**Verified against `a8db9c3` on GitHub.** The Step 8 cell copied `RELEASE` (= `WORK_DIR/r1_release`, the Step 6 release) and used `corrected["run_id"]` (the Step 6 summary). Its commit message said "cache replay … no estimation" unconditionally. After Tier A it would have published:

- the release **without** the eight re-estimated chains;
- under the Step 6 run ID;
- with a false provenance statement.

**Fix** (`colab/make_r1_replay_notebook.py`, regenerated `colab/r1_cache_replay.ipynb`, and the new `colab/r1_step8_publish_cell.py`):

- **Selection from disk only.** Step 8 decides what to publish only from the files the completed steps wrote. It never reads `RELEASE`, `corrected`, `REPLAY`, `TASKS` or any other variable left by earlier cells (checked by a test on the parsed code).
- **Selection rule (`select_publication`).**
  - `RUN_TIER_A` is True and the replay left AR chains to re-estimate → publish `r1_tier_a_release`, with the run ID from `r1_tier_a/r1_summary.json`.
  - `RUN_TIER_A` is False and no Tier A output exists → publish `r1_release` (Step 6).
  - Otherwise, refuse.
- **Fail-safe checks before anything is published.** Any failure raises an error, with no fallback.
  - Every required output must exist: summary, release manifests, Tier A legacy comparison, and AR validation.
  - The AR validation must have `ok: true`.
  - The Tier A legacy gate must be all `identical` or `equal_within_fp_tolerance`.
  - The run ID in the release manifest and in the release summary must both equal the staging run ID.
  - The release `code_commit_sha` must equal `PIN_COMMIT`, with `code_tree_dirty: false`.
  - The re-estimated chains must equal exactly the replay report's Tier A list (eight).
  - A Step 6 release must contain no re-estimated chain.
  - Tier A outputs present while `RUN_TIER_A` is False → refuse to guess.
- **Explicit confirmation.** The cell is a **dry run unless `CONFIRM_PUBLISH = True`**. The new setting defaults to False; in an older session that lacks it, it is read as False. The dry run writes `publication_plan.json` and copies the selected release's manifests to the evidence folder.
- **Labels.** Commit messages and branch names state what was published. Examples: `…/r1-tier-a-<stamp>`; "Tier A: AR chains re-estimated (…)", with the run ID.

**Notebook regeneration and an already-open session are handled separately.**

- *Regenerated notebook*, for a new session: the Step 8 cell in `r1_cache_replay.ipynb` is fixed.
- *Already-open session*, which ran the older notebook: **do not run its old Step 8 cell.** Paste `colab/r1_step8_publish_cell.py` into a **new** cell of that session and run it. The file is identical to the notebook's fixed cell, apart from a header comment. It needs only variables that the older session defined in Steps 1–2: `WORK_DIR`, `EVIDENCE`, `REPO`, `PROJECT`, `PIN_COMMIT`, `COMMIT`, `STAMP`, `GIT_ENV`, `GITHUB_TOKEN`, `RUN_TIER_A` and the prefixes. It ignores the stale `RELEASE` and `corrected`.

**Tests** (`code/tests/unit/test_r1_step8_publication.py`, 15 tests):

- The real cell is executed against a fake work directory holding both a Step 6 and a Tier A release, with `git` intercepted.
  - The dry run selects the Tier A release, its run ID and exactly eight re-estimated chains. It pushes nothing, even with stale Step 6 variables present.
  - With confirmation, `output_corrected` holds the Tier A release and not the Step 6 one. The commit messages name the Tier A run and all eight chains, and never "no estimation". The release branch is `r1-tier-a-…`. No force push is made.
- Nine fail-safe cases each raise an error before any push or copy: missing release, missing summary, missing or failed validation, legacy gate failure, seven chains instead of eight, run-ID mismatch, dirty tree, other commit.
- Without Tier A, the Step 6 release is selected. Tier A outputs present with `RUN_TIER_A = False` are refused.
- The paste file equals the notebook cell, and it works in a namespace shaped like the older open session.
- The cell reads none of the earlier cells' variables.
- Against the previous notebook (`a8db9c3`), all 15 tests fail.

## 2. Failed fits in Tier A, and their exclusion from scoring

**Rule (unchanged).**

- Part 5 §7.5 lists "required AR/ARMA stability condition violated" as **Failed**.
- `models/ar.py` sets `UNSTABLE_AR` → FAILED when the largest companion-root modulus is ≥ 1.
- Correction F1 (approved) excludes FAILED fits from every score and test. `mask_failed` is applied in `rescore._chains` to every robustness chain, whatever its source (published, cache or re-estimated). `scoring.scoreable` then drops failed rows. The raw value is kept in `failed_raw_forecast`.
- No model or failure rule was changed.

**FEDFUNDS T4.1 (level alternative): 71 failed AR fits.**

- The original T4.7 registry has 71 `UNSTABLE_AR` failures for FEDFUNDS AR, at 71 distinct origins from 1974-06 to 2024-12.
  - By year: 1974 (4), 1979–81 (9), 2002–03 (2), 2011–14 (31), 2022–24 (25).
  - Root moduli are 1.006 to 1.013: an explosive AR(1) estimated on the level of the policy rate in windows ending in tightening episodes or long periods at the zero bound.
- None of these belongs to another chain. The baseline FEDFUNDS AR chain (difference) has 0 failures in `forecasts_FEDFUNDS.parquet`, and every FEDFUNDS AR chain in the T4.8 audit has 0 failed origins. So all 71 belong to the T4.1 level chain, which has 626 origins.
- The original T4.1 table reports that chain with `n_valid = 626, n_failed = 0`. The 71 failed fits were therefore scored: this is exactly the F1 defect.
- Under F1 that AR row has 555 scoreable origins, and every AR-relative row of T4.1 FEDFUNDS changes. That is why the exercise stays pending until its ARMA, MSAR and STAR chains are available.

**Expected failure counts in the eight Tier A chains.** These come from the original registry; each is an `UNSTABLE_AR` failure flagged FAILED.

| Tier A chain | Failed origins | Dates |
|---|---|---|
| T4.1:UNRATE\|AR (difference) | 2 | 2020-04, 2020-08 |
| T4.1:FEDFUNDS\|AR (level) | 71 | 1974-06 … 2024-12 |
| T4.2:CPIAUCSL\|AR(p=1), (p=3), (p=6) | 0 each | — |
| T4.2:CPIAUCSL\|AR(p=12) | 1 | 1974-09 |
| T4.8:UNRATE\|180:AR | 1 | 2020-04 |
| T4.8:UNRATE\|300:AR | 1 | 2020-04 |
| **Total** | **76** | |

These should equal the `failed` field per task in Colab's `tier_a_validation/ar_refit_validation.json`. The AR refit is closed-form, and it reproduced the six published baseline AR chains exactly, so any difference would be a defect to investigate. I could not read the Colab file from this container.

The UNRATE AR registry also has 6 failed fits in total:

- baseline 2020-04;
- T4.1 2020-04 and 2020-08;
- T4.8 180 and 300 months (2020-04 each);
- the T4.8 240-month duplicate of the baseline.

The CPI AR registry has 1 (T4.2 p=12). This matches T4.7 status counts: CPI AR failed 1, FEDFUNDS AR failed 71, UNRATE AR failed 6.

## 3. The 35 unavailable chain contexts: which need recomputation

`classify_nonpublished_chains.py` produces `nonpublished_chain_classification.csv`. It covers the 60 robustness chains the release does not contain, using only the original outputs.

**What decides each chain.**

- In `models/registry.fit_and_forecast`, a FAILED ARMA, MSAR or STAR fit returns **no** forecast. So F1 can change a chain's rows only through an AR failure with a finite forecast.
- F2 can change rows only where an MCS cell was unavailable.
- F3, F4, F7.1 and F8 do not touch T4.1, T4.2 or T4.8 tables.

| Group | Chains | Decision |
|---|---|---|
| T4.2 CPI AR lags | 4 | Resolved by Tier A |
| T4.1 UNRATE and FEDFUNDS AR; T4.8 UNRATE 180/300 AR | 4 | Resolved by Tier A, but each exercise is scored only when all four models are present |
| T4.1 UNRATE and FEDFUNDS ARMA, MSAR, STAR; T4.8 UNRATE 180/300 ARMA, MSAR, STAR | 12 | **Needed** (cache replay or Tier B) |
| T4.8 GDPC1 90/150, and CPIAUCSL, INDPRO, FEDFUNDS, M2SL 180/300, all four models | 40 | **Unaffected**: no AR failure at those lengths and every MCS cell available. The published rows stand |

**Reconciliation with the Tier A summary.** The summary has 48 published, 17 cache, 8 re-estimated and 35 unavailable.

- The 60 non-published chains = 8 re-estimated + 17 cache-replayed + 35 unavailable.
- 9 of the 12 needed chains remain unapproved, so the cache replayed 3 of them.
- The other 14 cache-replayed chains belong to the 40 unaffected ones. The remaining **26 unaffected chains are "unavailable" only in the sense that no forecasts for them are on disk.** Their original rows are legitimately retained (`original_retained_unaffected`) and must **not** become fitting tasks.
- So, of the 35 unavailable contexts, **9 need recomputation** (Tier B, not approved) and **26 legitimately retain the original results**.

## 4. HLZ, DM-HLN and HAC warnings

**Where they come from.**

- `dm_hln.newey_west_variance` raises "overflow encountered in matmul".
- `hlz.mean_variation` raises "overflow in square".
- statsmodels `sandwich_covariance` raises "invalid value encountered in dot", in the T3.5 state regression.
- All three occur only in comparisons involving **STAR**, whose forecasts explode. STAR's largest absolute errors are recorded and flagged EXTREME_FORECAST (C08):
  - CPI h=12: 5.8×10¹⁰⁰;
  - M2SL h=12: 9.2×10⁹²;
  - CPI h=6: 4.8×10⁴¹;
  - M2SL h=6: 1.3×10³¹;
  - CPI h=3: 3.1×10²¹.
- The long-run variance of a squared-loss differential takes the error to the 4th power. It overflows double precision when |error| > ~10⁷⁷, which happens at CPI and M2SL h=12.

**Effect on inference.**

1. **Unavailable, and recorded as such.** For CPI and M2SL at h=12 under squared loss (STAR vs AR and STAR vs ARMA), the tables report `inference_available = False`:
   - T3.3A (HLZ): reason `Omega_hat_prime = nan`;
   - T3.3B (DM-HLN): reason `variance=inf`;
   - T4.4: the same four comparisons;
   - T3.5: CPI and M2SL STAR vs AR, h=12, reason "non-finite HAC covariance".
   No number is reported for these.
2. **Finite but degenerate.** `star_test_degeneracy.py` writes `star_test_degeneracy.csv`, which gives the largest single observation's share of Σd², where d is the STAR-vs-AR loss differential.
   - That share is **≥ 0.95 in 25 cells**:
     - CPI at h = 1, 3, 6 and 12 (both losses);
     - INDPRO at h = 1, 3 and 12 (both losses);
     - M2SL at h = 1, 3 and 12 (both losses) and h = 6 (squared);
     - UNRATE at h = 3 and 6 (squared) and h = 12 (both losses).
   - Two of those 25 cells, CPI and M2SL h=12 under squared loss, overflow: their variance is non-finite (point 1).
   - In these cells one exploded STAR forecast determines both the mean and the variance of d. The statistics collapse to near-constants: HLZ ≈ −1.6, DM-HLN ≈ −1.0, p ≈ 0.30–0.33.
   - These p-values are **not** evidence of equal accuracy. They show the tests have no power once a forecast has exploded. The relevant evidence for these cells is the recorded EXTREME_FORECAST pathology and STAR's RMSE and MAE (C08).
   - The same mechanism produces the T3.5 STAR rows with |α| > 10⁶.
3. **No other comparison is affected.** Every AR, ARMA and MSAR comparison is computed from finite, moderate losses, and so are the STAR cells outside that list.
   - In particular, the UNRATE h=1 STAR result discussed in `multiplicity_unrate_star.md` is not degenerate: the largest |error| is 10.3, and the largest single share of Σd² is 0.28 (absolute) and 0.41 (squared).
4. **The MCS** cells where `arch` overflowed are handled by F2 (guarded `hln_mcs_r`); see CORRECTIONS.md.

**Conclusion.** The warnings do not invalidate any reported inference.

- Where the arithmetic overflowed, inference is marked unavailable with its reason.
- Where it did not, the STAR statistics at the explosive horizons are degenerate. They should be read as "no usable inference: the STAR forecasts exploded", not as non-rejections.
- **Recommendation for the Part 8 text and claim matrix (no table change):**
  - qualify C08 and C13 to say that the STAR comparisons listed in `star_test_degeneracy.csv` as degenerate carry no inferential content;
  - do not count those non-rejections as evidence of equal accuracy.
  This follows the existing inference-language rule in `final_claims_allowed.md`.

## 5. Preserved

The following are unchanged by this commit:

- the original production results (`0662945`, `output/`);
- the frozen data and the Part 5 specifications;
- the corrected releases `0573a8c` and `3bd24c4`;
- the scientific pin `8aaa421`;
- every file under `code/src` and `code/tools`;
- cache identity `3413465b508bb844`.
