# Canonical thesis research input — thesis_input_2026-10-05.csv

**This file is an author-processed research dataset. It is NOT an unmodified official FRED extract.**
Two values in it are imputed by the author and are not official statistical observations.
See "October 2025 imputation" below.

- Historical vintage: **2026-10-05** (FRED/ALFRED real-time vintage)
- Rows: **5808** | Series: **7** | SHA-256: `7e7dc769bd63ca4951ef55430180f413de62c9dc53a275af50ad277a715b832a`
- Approved study endpoints: monthly **2026-08-01**, quarterly GDP **2026-04-01**

## What this file is for

Every result in Parts 6 to 8 of the thesis is computed from this file. The pipeline loads
it first into a pandas DataFrame, derives monthly and quarterly panels in memory, and then
applies all transformations, diagnostics, estimation, forecasting and tests. No data are
downloaded again once this file exists and verifies against its recorded hash.

## Format

Long (tidy) format: one row per series per observation date. Quarterly GDP keeps its true
quarterly spacing and is never expanded onto a monthly grid.

| Column | Meaning |
|---|---|
| `series_id` | FRED series identifier |
| `date` | observation period start, ISO `YYYY-MM-DD`, provider's period convention |
| `frequency` | `M` (monthly) or `Q` (quarterly) |
| `value` | the raw-level modelling input used by the thesis |
| `source_value` | the official downloaded raw value; blank where the official value is genuinely unreported |
| `observation_status` | `OBSERVED` or `IMPUTED_LOCF` |
| `imputation_method` | `LOCF` for imputed rows, blank otherwise |
| `imputation_source_date` | the date the value was carried forward from, blank otherwise |

Values are written verbatim as returned by the provider, so numerical precision is
preserved and the file's bytes are reproducible. No transformed growth rates, forecasts
or future data appear in this file.

## Series

| Series | Frequency | Units | Range in this file | Rows | Imputed |
|---|---|---|---|---:|---:|
| `CPIAUCSL` (Consumer Price Index for All Urban Consumers: All Items in U.S. City Average) | M | Index 1982-1984=100 | 1947-01-01 to 2026-08-01 | 956 | 1 |
| `FEDFUNDS` (Federal Funds Effective Rate) | M | Percent | 1954-07-01 to 2026-08-01 | 866 | 0 |
| `GDPC1` (Real Gross Domestic Product) | Q | Billions of Chained 2017 Dollars | 1947-01-01 to 2026-04-01 | 318 | 0 |
| `INDPRO` (Industrial Production: Total Index) | M | Index 2017=100 | 1947-01-01 to 2026-08-01 | 956 | 0 |
| `M2SL` (M2) | M | Billions of Dollars | 1959-01-01 to 2026-08-01 | 812 | 0 |
| `UNRATE` (Unemployment Rate) | M | Percent | 1948-01-01 to 2026-08-01 | 944 | 1 |
| `USREC` (NBER based Recession Indicators for the United States from the Period following the Peak through the Trough) | M | +1 or 0 | 1947-01-01 to 2026-08-01 | 956 | 0 |

## October 2025 imputation

During the 2025 United States federal government shutdown the Bureau of Labor Statistics
could not collect October 2025 reference-period data. The October 2025 CPI release was
cancelled, and the October 2025 household survey, the source of the unemployment rate, was
never collected and cannot be collected retroactively. Those two official observations are
therefore permanently missing.

Under a documented, user-approved research-design decision (Part 5 §2.2A), exactly two
cells carry the previous month's raw level forward:

| Series | Date | Official value | Value used | Carried forward from |
|---|---|---|---|---|
| `CPIAUCSL` | 2025-10-01 | missing (unreported) | 324.245 | 2025-09-01 |
| `UNRATE` | 2025-10-01 | missing (unreported) | 4.4 | 2025-09-01 |

This is last observation carried forward at the raw level, applied once before any
transformation. It is **not** an official release, a real-time estimate, or a claim that
economic conditions were unchanged. No other value in this file is imputed.

**Known artifacts of this choice**, which users of the data must take into account:

- October 2025 CPI monthly inflation is exactly zero by construction
- the observed September-to-November index change loads entirely on November
- if UNRATE is differenced, its October 2025 change is exactly zero by construction

The untouched official raw files, including their missing-value markers, are archived
separately alongside this file, so anyone can inspect the genuine gaps or apply a
different method.

## Reproducing the thesis inputs

1. Verify this file against the SHA-256 above and against `thesis_input_2026-10-05.metadata.json`.
2. Load it as a DataFrame; do not edit it by hand.
3. Split by `frequency` and pivot on `series_id` to obtain the monthly and quarterly panels.
4. Apply the transformations defined in the approved methodology. They are computed in
   code after loading, never stored here.

## Attribution and reuse

Federal Reserve Economic Data (FRED) / ALFRED, Federal Reserve Bank of St. Louis, and the underlying official agencies: U.S. Bureau of Economic Analysis (GDPC1), U.S. Bureau of Labor Statistics (CPIAUCSL, UNRATE), Board of Governors of the Federal Reserve System (INDPRO, FEDFUNDS, M2SL), and the NBER business-cycle chronology distributed by FRED (USREC).

Derived dataset for research replication, subject to the original providers' terms. Two cells are author-imputed and are not official statistics.
