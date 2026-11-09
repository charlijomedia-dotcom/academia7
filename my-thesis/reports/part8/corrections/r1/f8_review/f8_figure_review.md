# F8 figure review: readable F3.4 main panel (9 November 2026)

**Status: PREPARED FOR REVIEW. Not published; the archive is unchanged.**

You authorised F8 on 9 November 2026 as a presentation-only amendment. This review covers F8 only.
- No model estimate, forecast, metric, test, table or scientific pin changes.
- The F8-corrected figures live only in this review workspace (`corrections/r1/f8_review/`).

## 1. The rule and the implementation

**Part 5 §13.1.** "No figure may silently compress the economically relevant series because one model exploded." For failed or extreme forecast cases, a figure must:
- show the valid models on a readable main panel;
- show the failed or extreme model in a separate failure or diagnostic panel;
- never winsorize or clip a forecast without an explicit label.

**Implementation.** F8 is already in the pinned code (commit `8aaa4217`, "Figures (corrected mode): readable F3.4 main panel (F8)"). It sits in `thesis.reporting.figures.actual_vs_forecast` behind the switch `f8_readable_main_panel`.
- `git diff 8aaa421 HEAD -- code/src/thesis/reporting code/src/thesis/correction/flags.py` is empty, so the code used here is the pinned code.
- The integration and the archive ran with the switch **off**, by decision; F8 was pending your confirmation.

**What the switch changes when on:**
1. **Main panel.** A model's flagged values (scored extreme forecasts and unscored failed fits) are omitted from the main panel, and the title says so: "flagged forecasts are omitted here and shown in the diagnostic panel".
2. **Diagnostic panel.** If any flagged value exceeds 100 × the maximum absolute actual value, the panel uses a symmetric-log axis. The axis is linear within ± that maximum, and the scale is stated in the panel title. Nothing is clipped.

**Scope of the switch.** It is read in exactly one place, `figures.py:302`, inside `actual_vs_forecast`. It therefore cannot affect any table, forecast, fit, test or decision. The F1 rules are unchanged: failed fits are drawn as large hollow markers labelled "failed fit (raw value, not scored)", extreme forecasts as filled markers labelled "extreme (scored)", and the legend sits below the axes.

## 2. How the figures were produced

**Script.** `f8_render.py`. It reproduces the pipeline's F3.4 call line for line (`pipeline.py`, evaluation stage). It runs under the repository's rendering guard: matplotlib 3.11.2, empty rc and DejaVu Sans; `render_report.json` → `render_guard.ok = true`.

**Inputs.** The stored h=1 baseline forecasts (`forecasts/forecasts_<target>.parquet`) and the transformation decisions (`diagnostics/T2.2_transformation_decisions.csv`), taken from the local rehearsal of the integrated candidate. Their sha256 values are in `render_inputs.json`.
- **Why the local tree is used.** The archived `release.tar.gz` (47.9 MB) is above the Drive connector's 10 MB download limit.
- **Why the inputs are the archived ones.** With F8 **off**, the script reproduces all 12 archived F3.4 files (6 PNG, 6 PDF) **byte for byte**, against the sha256 values in `archive_inventory.csv` of archive `archive-20261109T080914Z-3c7d68` (`f8_figure_hashes.csv`, `legacy_rerender_equals_archived = True` for all 12). The figure-relevant inputs and the renderer are therefore exactly the archived ones.

**Determinism.** Two independent F8 renders are byte-identical for all 12 files.

**Not changed.** The script estimates and scores nothing and writes nothing into the candidate. The archive is untouched.

## 3. Before and after

- **Before:** `before/F3.4_<target>.png`, identical to the archived files.
- **After:** `after/F3.4_<target>.{png,pdf}`.

| Figure | Archived sha256 | F8 sha256 |
|---|---|---|
| F3.4_GDPC1.png | `39f4f104e1f9…` | `d91573f66636…` |
| F3.4_GDPC1.pdf | `97e2c25e298e…` | `4c283f200cbc…` |
| F3.4_CPIAUCSL.png | `f5db1538ced5…` | `9ef97dd5f983…` |
| F3.4_CPIAUCSL.pdf | `954f30d10a68…` | `51f709bf598d…` |
| F3.4_UNRATE.png | `c224801d734b…` | `d50c36008bb9…` |
| F3.4_UNRATE.pdf | `878e01a0a59b…` | `8a50e282229a…` |
| F3.4_INDPRO.png | `876c0ed20011…` | `6d6f58694382…` |
| F3.4_INDPRO.pdf | `b207e0fa351d…` | `195f3403c135…` |
| F3.4_FEDFUNDS.png | `d6be129d25cb…` | `ad961b1fb682…` |
| F3.4_FEDFUNDS.pdf | `0b71718d764c…` | `ae2e7e32d19a…` |
| F3.4_M2SL.png | `211017a13158…` | `b08e0baaa145…` |
| F3.4_M2SL.pdf | `b08552141583…` | `5f173c934ce0…` |

The full 64-character hashes, byte sizes and archived sidecar hashes are in `f8_figure_hashes.csv`.

**Flagged values by target** (h=1; `render_report.json`). "Max |actual|" is the largest absolute actual value, which sets the diagnostic panel's scale.

| Target | Extreme (scored), by model | Failed fit (raw, not scored) | Largest flagged value | Max \|actual\| | Diagnostic scale |
|---|---|---|---|---|---|
| CPIAUCSL | STAR 15 | — | 1.44×10¹¹ (STAR, 1974) | 21.5 | symmetric log, linear within ±21.5 |
| INDPRO | AR 1, ARMA 1, STAR 72 | — | 1.92×10⁸ (STAR) | 170 | symmetric log, linear within ±170 |
| M2SL | AR 1, ARMA 1, MSAR 2, STAR 87 | — | 1.98×10³ (STAR, 2009) | 74.7 | linear |
| UNRATE | AR 2, ARMA 4, MSAR 4, STAR 85 | AR 1 (2020-05, raw 31.6) | 31.6 | 14.8 | linear |
| GDPC1 | AR 1, ARMA 1, STAR 1 | — | 24.2 | 32.8 | linear |
| FEDFUNDS | STAR 23 | — | 7.76 | 6.63 | linear |

**What changes, target by target:**
- **CPIAUCSL — the case that motivated F8.** Before, one STAR forecast of 1.4×10¹¹ (1974) set a 10¹¹ scale for both panels: the actual series and every model were a flat line at 0. After, the main panel shows actual inflation (−21 to +21) and the AR, ARMA, MSAR and STAR forecasts readably. The diagnostic panel shows all 15 STAR extremes on a labelled symmetric-log axis, including the 1.4×10¹¹ value and two large negative values.
- **INDPRO.** The main panel is readable, and the pandemic swing (−170 to +77) is the largest feature, as it should be. The diagnostic panel shows STAR values down to −1.9×10⁸ on the symmetric-log axis, plus the AR and ARMA 2020 extremes.
- **UNRATE.** Before, the main panel was already readable after F1, but the scored ARMA extreme of 27.7 (2020) stretched it to 0–28. After, the main panel runs from about 3 to 15. The diagnostic panel still shows the failed AR fit (hollow marker, 31.6, "not scored") and all scored extremes.
- **GDPC1, FEDFUNDS and M2SL.** The main panels were already readable. F8 removes a few flagged points from them, and they appear in the diagnostic panel.

**Disclosure check.**
- Every flagged value is drawn in the diagnostic panel. The axes autoscale to all of them, and none is clipped or deleted.
- The omission from the main panel is stated in the main panel's title. The symmetric-log scale is stated in the diagnostic panel's title.
- Failed and extreme forecasts carry distinct markers and legend labels. Scored and unscored values are named as such.

## 4. Provenance

- **Archived sidecars.** They carry `run_id`, `created_utc`, `code_commit_sha` (the pin), `config_hash`, `data_snapshot_hash`, `figure_id`, `horizon` and `series`.
- **Proposed release sidecars** (`after_sidecars_proposed/`). They keep every archived key and replace `run_id` and `created_utc` with the release run's values when the release is built. They add three keys:
  - `presentation_amendment`: the F8 text and its approval date;
  - `rendered_from`: the archive identity;
  - `figure_sha256`.
- **What else changes.** Only these 12 figures and their 12 sidecars. Every scientific table, forecast file, fit record, test, decision and protected input of the archived candidate stays byte-identical in the release plan (`../part8_d3_release_plan.md`).

## 5. Does F8 fully address R1-06 ("misleading figures")?

**The three defects behind the earlier PARTIALLY ADDRESSED status:**
1. The UNRATE main panel plotted the failed AR spike. **Fixed by F1:** failed fits are not plotted on the main panel and are labelled in the diagnostic panel.
2. The diagnostic panel joined non-adjacent flagged points with lines (F7.2). **Fixed by F1's marker rule:** flagged values are drawn as unconnected markers.
3. An exploding STAR forecast compressed the CPI main panel, in breach of §13.1. **Fixed by F8**, as the before and after figures show; INDPRO is also improved.

**Assessment.** On the actual figures, F3.4 now meets every Part 5 §13.1 requirement:
- a readable main panel;
- a separate diagnostic panel;
- no clipping;
- explicit labels for the omission and for the axis scale.

I therefore consider R1-06 **addressed by the F8 figures**. In the drafts it is marked **RESOLVED, conditional on these F8 figures being the ones published**: until the release, the archived candidate still holds the pre-F8 figures. This conditional status is my judgement for your review.

**Residual presentation points, not defects under §13.1, noted for transparency:**
- **M2SL diagnostic panel.** It stays linear, because the largest STAR value (1,980) is under 100 × max |actual| (7,470). The 87 STAR markers from 2002–2012 are therefore compressed near 0–50 and overlap one another and the four AR, ARMA and MSAR 2020 markers. All are drawn and labelled, but individual values cannot be read off. Changing the 100× threshold would be a new presentation choice beyond the approved F8 implementation, so it is not changed here.
- **Dense clusters elsewhere.** The UNRATE STAR markers (2021–2026) and the INDPRO STAR markers near zero also overlap. The per-model counts are given in this report, not in the figure.
- **Empty pre-sample span.** The x-axis of every F3.4 starts in 1945, because the recession shading begins in 1948, while forecasts start in 1967–1979. This is pre-existing and compresses nothing.

## 6. Files

| File | Content |
|---|---|
| `f8_render.py` | the renderer (read-only; render guard) |
| `render_report.json` | render guard record, flagged and failed counts, per-file hashes |
| `render_inputs.json` | sha256 of the rendering inputs (local-equivalent tree) and of the archived files |
| `f8_figure_hashes.csv` | archived and F8 sha256 and bytes, legacy-reproduction flag, archived sidecar sha256 |
| `before/`, `after/` | the archived PNGs; the F8 PNGs and PDFs |
| `after_sidecars_proposed/` | proposed provenance sidecars for the release |
