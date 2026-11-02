# Visual review of the corrected figures (2 November 2026)

You asked for this review, with priority on the unemployment forecasts, the extreme-forecast failure panels and the Zivot–Andrews break annotations. I read the PNGs of the provisional release (`0573a8c`) and of the clean regeneration (`8aaa421`) and compared them with the original publication.

## Findings and changes

| Figure | Original or provisional state | Issue | Change (corrected mode only; legacy drawing unchanged) |
|---|---|---|---|
| F3.4 UNRATE, main panel | Original: the AR line spikes to 31.6 at 2020-05, the failed UNSTABLE_AR fit | F1 | In the provisional release, failed fits are no longer drawn (F1) |
| F3.4, all, diagnostic panel | Original: flagged points of one model joined by a line across decades (for UNRATE STAR, a dotted line from 1969 through 1992 to 2020) | A path that never existed | Already corrected by F1 in the provisional release: markers, not lines |
| F3.4 UNRATE, diagnostic panel | Provisional: the failed AR value (31.6) sat under the legend box, half hidden | Information hidden | The legend moves below the axes. Failed fits are drawn as large hollow markers labelled "failed fit (raw value, not scored)"; extreme but valid forecasts as filled markers labelled "extreme (scored)" |
| **F3.4, all, main panel (F8)** | Original and provisional: flagged values stay in the main panel. For CPI, a STAR forecast of 1.4×10¹¹ (1974) flattens the actual series and every model | Violates Part 5 §13.1 ("No figure may silently compress the economically relevant series because one model exploded") and the F3.4 output rule ("failed/extreme models moved to separate diagnostic panel") | Flagged values are left out of the main panel, and the title says so. When flagged values exceed 100 times the data range, the diagnostic panel uses a symmetric-log axis, labelled with its linear range. Nothing is clipped. Switch: `f8_readable_main_panel` |
| F2.1 UNRATE, FEDFUNDS | Provisional: ZA dates drawn as "Zivot-Andrews break" on both panels, including FEDFUNDS's differenced panel | None of the four ZA tests rejects (p = 0.17, 0.19, 0.32 and 0.81). The dates are candidate breaks of a level test, not detected breaks, and the test is not on the differenced series | Drawn on the level panel only, labelled "Zivot-Andrews candidate break: YYYY-MM (level test, sample; p=…, unit root not rejected)". The legend sits outside the axes so the 1980–81 policy-rate peaks are not hidden |

**Dates verified against T2.2:**

| Series | Initial window | Full sample |
|---|---|---|
| UNRATE | 1957-08 | 2008-04 |
| FEDFUNDS | 1970-10 | 1984-08 |

## Status of the figures after review (clean regeneration `8aaa421`)

- **F3.4 UNRATE.**
  - Main panel: readable, with no failed spike.
  - The 2020 ARMA (27.6) and STAR extremes appear in the diagnostic panel.
  - From 2021 onwards most STAR forecasts are flagged EXTREME_FORECAST, so the STAR line is mostly absent from the main panel and fully visible below. This is the published fragility evidence (C08), now visible rather than hidden.
- **F3.4 CPI.** The main panel is readable (inflation from −20% to +20%). The STAR extremes, from −100 up to 1.4×10¹¹, appear on the labelled symmetric-log diagnostic axis.
- **F2.1 UNRATE and FEDFUNDS.** Correct dates, outcome-labelled candidate breaks, and no hidden data.
- The other F3.4 figures (GDPC1, INDPRO, FEDFUNDS, M2SL) follow the same rules.

## Where the figures are, and what to confirm

- **Legacy mode** still draws the original figures byte for byte; the legacy gate compares them.
- **Corrected figures** are in the clean-regeneration release, branch `part8-corrected-results/r1-clean-20261102`, `output_corrected/figures/`.

**F8 is a new item.** I raise it for your confirmation. It changes presentation only: no number, test or table changes. The prior approvals covered F1–F4 and F7.1. If you prefer, setting `f8_readable_main_panel = False` reproduces the provisional F3.4 layout, apart from the F1 marker rules.
