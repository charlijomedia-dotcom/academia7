# Scientific adjudication record: Tier B batch B2

**Decision: B2 is ACCEPTED for inclusion in the final Part 8 candidate.**

- Decided by the user on 8 November 2026, after ChatGPT's independent review of `part8_integration_scientific_audit.md` (commit `3da0e71`).
- The acceptance covers B2's computations under the **approved live warm-start rule**.
- It does **not** by itself grant scientific approval of Part 8, and it publishes nothing.

Machine-readable record: `evidence/b2_adjudication_20261108/b2_adjudication.json`. All 49 adjudicated origins: `evidence/b2_adjudication_20261108/b2_adjudicated_items.csv`.

## 1. What is accepted

| Item | Value |
|---|---|
| Batch | B2, session `505e21` (with the first session `d12923`) |
| Chains | `T4.1:FEDFUNDS\|MSAR` (626 origins), `T4.8:UNRATE\|180:MSAR` (764 origins) |
| Certificate | `COMPLETE-20261105T151645Z-B2-20261105T110347Z-505e21.json`, sha256 `c8c90ba079abf5bd4256bb1be244dcc7116ae218a28206e75f44660c644f83c4` |
| Status as issued | `COMPUTATION_COMPLETE_REVIEW_REQUIRED` |
| Basis of acceptance | At 1,390/1,390 origins, B2's estimate equals the original fit cache under the approved live warm-start rule: same cache key, Δlog-likelihood = Δparameters = Δforecast = 0 (`part8_integration_preparation_report.md` §2) |
| Used in | integration dry run `integration-20261108T052245Z-9bba8e` (fit records replaced: 43 + 6, as expected; A8) |

## 2. Preserved without change

**The certificate.**
- The certificate, and its Drive copy, keep the status `REVIEW_REQUIRED` exactly as issued.
- **This record supersedes nothing in it.** It records a decision taken on top of it.
- The sha256 above equals the copy in `evidence/integration_prep_20261106/certificates/` and the value checked in the dry run's preflight.

**The 49 differences from the published records.** All are listed in the items file.

| Chain | Classification changes | Optimiser sensitivities |
|---|---|---|
| T4.1 FEDFUNDS MSAR | 14: failed → fragile 3 (1980-01, 1981-05, 1981-06); failed → failed with other reason codes 5; fragile → fragile with other codes 6 | 29: same status; B2 log-likelihood higher by 0.04 to 275 (median 24.4) |
| T4.8 UNRATE 180 MSAR | 6, 1982-01 to 1982-06: fragile → adequate 5; failed → failed with other codes 1 | 0 |
| **Total** | **20** | **29** |

**Log-likelihood.**
- At all 43 FEDFUNDS origins, B2's log-likelihood is at least the published one.
- At UNRATE 180 it is lower at 5 origins (−0.01 to −0.21) and higher at 1 (+0.24).

**Scientific reading.**
- The published records came from the cache-hit replay. After a failed fit, that replay warm-starts differently from the approved rule.
- B2 is the approved-rule estimator.
- A higher or a lower likelihood does not by itself establish scientific preference.
- The differences are local optima of MSAR(p, K=2) in regime-poor windows: FEDFUNDS in 1980–81, UNRATE in 1982.

**Limitations retained:**
- **F6.** The approved MSAR multistart does not guarantee the global likelihood maximum. No claim of a global maximum is made, for B2 or any other MSAR estimate.
- **Reporting.** The 20 classification changes and 29 optimiser sensitivities are to be **reported** in the final Part 8 reports, as optimiser sensitivity of rolling MSAR (C07). They are not removed or smoothed.
- **Attribution.** The FEDFUNDS-level DM-HLN decision change (p 0.053 → 0.029; HLZ p 0.130 → 0.145, no change) is attributable jointly to F1 and B2. It is not decomposed (`part8_integration_scientific_audit.md` §4).

## 3. Not changed by this record

- historical certificates and Tier A/B checkpoints;
- the original fit cache;
- the published results and prior releases (`0573a8c`, `3bd24c4`, `292227e`);
- the approved methodology and the scientific pin `8aaa4217`.

No estimation was performed. F8 remains disabled, and D3 (the publication destination) remains deferred.
