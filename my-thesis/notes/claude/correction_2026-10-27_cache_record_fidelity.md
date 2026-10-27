# Implementation correction: fit records served from the cache (2026-10-27)

Recorded under CLAUDE.md §6A. No methodological element is affected.

## The error

`forecasting/rolling.py` stored a fitted model in the fit cache with its forecasts,
parameters, status, reason codes, log-likelihood and information criteria, but not the
rest of its `FitRecord`: the parameter standard errors, the optimizer message, the
`diagnostics` mapping (which holds the detail behind every credibility flag) and the
estimator's specification label. A fit read back from the cache therefore had those
fields blank.

## How it was found

The Colab recovery test terminated a reduced run partway, restored 28 backed-up fits on
a fresh machine, and completed the run. Every forecast, parameter, status, test table and
figure matched an uninterrupted run, but `models/fit_records.csv` (28 rows) and
`robustness/T4.7_failure_registry.csv` (56 rows, column `raw_diagnostic`) did not: the
cache-served fits had empty diagnostic fields.

## What was affected

* No forecast, parameter, status, reason code, test statistic, table of results or
  figure: those were always complete.
* `fit_records.csv` (`std_errors`, `optimizer_message`, `diagnostics`, `spec_label`) and
  the T4.7 failure registry's `raw_diagnostic` text, for fits served from the cache.
  In every run so far that meant the T4.8 baseline-length chains, which reuse the
  forecast stage's fits by design; in a resumed run it would also have meant every
  restored fit.

## The change

The cache payload now carries the complete record (`record_detail`), encoded so that each
value prints exactly as the original: scalars keep their type, anything else keeps its
printed text. `_record_from_payload` restores it. `code/tests/integration/
test_cache_fidelity.py` asserts that wholly and partly cache-served chains produce fit
records and failure events identical to freshly estimated ones.

## Outputs to regenerate

`rolling.py` is in the fit cache's dependency hash, so every earlier cache entry is
invalidated and the next run recomputes it. The Part 8 run starts from an empty cache in
any case. Smoke outputs produced before this change differ from new ones only in the
fields above, for the T4.8 baseline-length chains; they are not thesis-facing.
