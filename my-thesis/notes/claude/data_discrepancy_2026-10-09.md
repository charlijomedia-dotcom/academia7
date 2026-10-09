# Data discrepancy — permanent missing observation in CPIAUCSL and UNRATE

**Raised:** 2026-10-09
**Raised by:** Claude Code, Part 6 pre-implementation vintage verification
**Rule invoked:** `part5_methodology_specification.md` §2.4 ("If the historical-vintage API returns a different start or terminal observation, Claude must stop, save the discrepancy, and request approval rather than silently alter the sample") and CLAUDE.md §4 (stop, document, propose, wait).
**Status:** **OPEN — awaiting user decision.** No handling rule has been chosen. No transformation, sample or model code for CPIAUCSL or UNRATE has been written.

---

## 1. The finding

The FRED/ALFRED **2026-10-05** vintage returns, for all seven approved series, a complete monthly/quarterly date grid with **no gaps and no duplicate dates**. However two series carry a missing value (`"."`) at one interior date:

| Series | Missing date | Neighbouring values returned |
|---|---|---|
| CPIAUCSL | **2025-10-01** | 2025-09 = 324.245, **2025-10 = "."**, 2025-11 = 325.063 |
| UNRATE | **2025-10-01** | 2025-09 = 4.4, **2025-10 = "."**, 2025-11 = 4.5 |

Both are returned with `realtime_start = realtime_end = 2026-10-05`, so this is what the official information set looked like on the thesis vintage date.

## 2. Why it will never be filled

This is not an API artifact, a retrieval error, or a revision that a later vintage would repair.

During the 2025 United States federal government shutdown the Bureau of Labor Statistics could not collect survey data for the October 2025 reference period:

- the **October 2025 CPI release was cancelled**, and no overall or core CPI was produced for that month;
- the **October 2025 Current Population Survey (household survey) was never collected**, and BLS has stated that household-survey data cannot be collected retroactively — so the October 2025 unemployment rate will never exist.

Sources: BLS, *2025 federal government shutdown impact on the CPI* and its FAQ (`bls.gov/cpi/additional-resources/`); Reuters/BLS statements on the cancelled October 2025 employment report.

Consequently the hole is permanent in the official statistical record, independent of vintage choice.

## 3. Why frozen Part 5 does not resolve it

Part 5 assumes contiguous monthly series and does not contemplate a permanent interior hole:

- the transformations are defined as one-period changes computed from frozen raw levels (§2.3, §2.4);
- backfilling is prohibited (§2.4: "No missing earlier observations are backfilled");
- artificial interpolation is prohibited (§2.1 data-selection criterion 6: series must "be used without artificial interpolation");
- rolling windows are defined as fixed counts of **observations** (§9.1), with no rule for a window that spans a hole;
- the monthly VAR requires all five variables "in the same row" (§2.4) with "no missing earlier observations backfilled";
- the reproducibility tests (Comp §15) require "lag construction", "rolling-window boundaries" and "forecast target alignment" checks, none of which has a defined meaning across a hole.

Nothing in Part 5 authorizes me to choose among the possible handlings, and each option below touches a locked element or changes the effective meaning of one. **This therefore requires your explicit decision.**

## 4. Exact impact

### 4.1 Transformed targets directly lost

| Target | Baseline transformation | Observations lost |
|---|---|---|
| CPI inflation | `1200 × Δln(CPIAUCSL)` | **2025-10 and 2025-11** (both need the 2025-10 level) |
| UNRATE, if the predeclared rule selects **level** | level | **2025-10** |
| UNRATE, if the predeclared rule selects **first difference** | `Δu` | **2025-10 and 2025-11** |

The UNRATE case depends on the §3.4 initial-window ADF/KPSS/ZA outcome, which is not yet computed.

### 4.2 Propagation through lags (this is the severe part)

Under complete-case estimation, an AR(p) row at date `t` is unusable if any of `t, t−1, …, t−p` is missing. With the sample ending 2026M8:

| Target / order | Unusable estimation rows | Count |
|---|---|---:|
| CPI, p = 12 | 2025-10 … 2026-08 | **11** (every remaining row in the sample) |
| CPI, p = 6 | 2025-10 … 2026-05 | 8 |
| CPI, p = 3 | 2025-10 … 2026-02 | 5 |
| CPI, p = 1 | 2025-10 … 2025-12 | 3 |
| UNRATE level, p = 12 | 2025-10 … 2026-08 | **11** |

**For CPI with p = 12, all eleven of the final one-step forecasts (targets Oct 2025 – Aug 2026) become unavailable** under complete-case handling: the Oct 2025 target has no actual value, and every later origin's 12-lag predictor vector contains 2025-10 or 2025-11. The same holds for MSAR and STAR at their inherited lag order, and for ARMA through its autoregressive part.

This interacts with the **T1** decision you just approved: the CPI AR-lag robustness exercise compares p = 1, 3, 6, 12 **on common forecast dates**. Under complete-case handling the common date set is dictated by the worst case (p = 12), so all four lag variants would lose the final eleven months — even p = 1, which only genuinely loses three. The lag-robustness comparison is still internally valid, but it ends eleven months earlier than the approved sample for all variants.

### 4.3 Other affected components

| Component | Effect |
|---|---|
| **Rolling windows** | "240 observations" and "240 calendar months" stop coinciding for CPI/UNRATE in every window that spans the hole (roughly the final 240 windows). A sub-decision is needed: 240 *available observations* (window spans 241–242 calendar months) or 240 *calendar months* (containing 238–239 usable observations). |
| **Monthly VAR** (1959M1–2026M8, balanced rows) | Row 2025-10 cannot be balanced. With p = 3, rows 2025-10 … 2026-01 are unusable. The "common sample" becomes non-contiguous. |
| **Full-sample stationarity tests** | ADF is a regression and tolerates complete-case deletion. **KPSS and Zivot–Andrews are partial-sum / sequential-break statistics that assume a contiguous series**, so a documented rule is needed for the CPI and UNRATE full-sample tests. |
| **Forecast evaluation** | CPI loses 2 target-date error observations outright (more via lags, per 4.2); UNRATE loses 1 or 2. Loss series acquire holes, which the approved **M7** intersection rule then handles. |
| **Longer horizons** | h = 3, 6, 12 shift which targets are lost; the pattern differs by horizon. |
| **State masks / USREC** | Structurally unaffected (USREC is complete). Only the number of evaluated errors changes. |

### 4.4 Explicitly **not** affected

- **GDPC1, INDPRO, FEDFUNDS, M2SL, USREC** are complete, with no interior missing values.
- **The initial estimation window** begins in 1947/1948 and ends roughly 60 years before the hole. Therefore **no locked specification choice is affected**: the §3.4 transformation decision, AR order, ARMA order, STAR delay/type and the Tsay/LST nonlinearity evidence are all selected on data that contains no gap.
- **The approved monthly endpoint 2026M8** and all approved start dates are unaffected.

## 5. Options

I am not choosing. Each option is stated with what it costs and which locked element, if any, it touches.

**Option A — Missing-data-aware complete-case handling (no interpolation).**
Treat the hole as genuinely missing. Drop incomplete estimation rows within each window; produce no forecast where a required input is missing; record each such origin under a new, clearly separated status such as `DATA_GAP` (a *data* condition, explicitly **not** a model failure and not counted against any model in the failure registry). Keeps the approved endpoint, transformation, estimation method and window length; adds no synthetic values.
*Cost:* the final ~11 CPI and UNRATE one-step forecasts are unavailable at the baseline lag order (§4.2), and the effective meaning of "240 observations" needs the sub-decision in §4.3.

**Option B — Truncate the monthly sample to 2025M9.**
Fully contiguous data, no missing-data machinery anywhere.
*Cost:* changes the **approved monthly endpoint from 2026M8 to 2025M9** — a locked element under §16 — and discards eleven months including the most recent period. Also makes the monthly endpoint no longer the "latest jointly available month", so the §2.4 end-date rationale would have to be restated.

**Option C — Bespoke two-month-change observation for CPI.**
BLS published a November 2025 CPI level, so a single two-month log change could be computed and annualized at 600 for that one observation.
*Cost:* changes the **locked transformation rule** for one observation; produces one observation that is not a one-period change; does nothing for UNRATE, whose missing value is a level, not a change.

**Option D — Missing-data maximum likelihood (state-space / Kalman).**
AR and ARMA can be estimated with the gap treated as missing at random via the state-space filter, retaining all other observations and the full endpoint. MSAR's Hamilton filter can skip a missing observation; STAR would need bespoke handling.
*Cost:* changes the **estimation method** (a locked element) for some models, and applies non-uniformly across the four model families, which weakens the like-for-like horse race that the thesis is built on.

**Option E — Interpolation or carry-forward.**
*Excluded.* Prohibited by frozen Part 5 (§2.1 criterion 6, §2.4). Listed only to record that it was considered and ruled out by the approved methodology, not by my judgment. (Note that BLS itself carried September prices forward for some underlying CPI components, but that is a BLS construction decision inside a published index, not a thesis-side interpolation of a missing published value.)

**Option F — Keep the full estimation sample, end OOS evaluation before the hole for CPI/UNRATE only.**
*Cost:* the evaluation period then differs across targets, so cross-aggregate comparison (Part 4 §3.7) and the common-date logic become asymmetric.

## 6. My recommendation, for your decision

**Option A**, with "240 observations" read as **240 available observations**, and with `DATA_GAP` kept strictly separate from model failure in T4.7 and in the figures.

Reasoning: it is the only option that changes no locked element, adds no synthetic data, and keeps the gap visible rather than papering over it — which matches the Part 5 philosophy that adverse data conditions stay in the record (§8.3, P1-09). The cost is real and must be stated plainly in Chapter 2 and Chapter 3: for CPI and UNRATE the last eleven months of the approved sample yield no baseline-order forecasts, for a documented external reason.

If you prefer the evaluation period to be identical across all six targets, Option B does that but needs an explicit methodology amendment to §2.4 and §16.

## 7. What I need from you

1. Which option (A–F, or another) governs the hole.
2. If A: whether a rolling window means **240 available observations** or **240 calendar months**.
3. Whether the full-sample KPSS and Zivot–Andrews tests for CPI/UNRATE should be (i) computed on the longest contiguous block ending 2026M8, (ii) computed on the complete-case series with the discontinuity documented, or (iii) reported as unavailable for the full sample with the initial-window results standing.
4. Confirmation that `DATA_GAP` is recorded separately from model failure, so no model is penalised for an external data outage.

Until this is decided, work continues only on components the hole cannot touch, and the real-data smoke test will use **INDPRO** (monthly, complete) and **GDPC1** (quarterly, complete).
