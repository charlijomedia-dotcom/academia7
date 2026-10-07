# Part 5: Computational execution specification

**Date:** 5 October 2026  
**Status:** PROPOSED FOR USER APPROVAL  
**Purpose:** Implement the approved methodology from scratch without reproducing the unnecessary computational burden of the previous thesis pipeline.

# 1. Clean build

Claude Code must build the research code from scratch from the Part 5 specification.

No old thesis code is assumed to exist.

Scientific validity has priority over runtime, but the code must not repeat work that the methodology does not require.

# 2. Frozen-data initialization and default no-internet rule

The thesis baseline must be generated from a historical FRED/ALFRED vintage dated **2026-10-05**.

Provide an initialization command, for example:

`python code/run_all.py --initialize-frozen`

The exact CLI name may differ, but the behavior is fixed:

- read `FRED_API_KEY` from the environment;
- retrieve only the approved FRED series IDs;
- request the 2026-10-05 historical vintage;
- request raw levels only;
- save each series under `data/frozen/fred_vintage_2026-10-05/`;
- save metadata, query parameters, row counts, and SHA-256 hashes;
- create one immutable manifest;
- verify expected start/end dates;
- stop on any unexplained discrepancy.

After frozen initialization, the normal thesis command must not contact the internet.

`python code/run_all.py`

must:

- verify frozen hashes;
- read the local frozen files;
- transform locally;
- reproduce all baseline outputs.

A separate optional command may reconstruct the same 2026-10-05 vintage from ALFRED for audit purposes. A current-data refresh must write to a different dated namespace and may never overwrite the thesis baseline.

# 3. Main efficiency rule

The pipeline must distinguish:

### Specification selection
Done on the initial estimation window only:

- baseline transformation decision;
- AR lag;
- ARMA order;
- STAR delay/type;
- nonlinear structural tests.

### Parameter re-estimation
Done at **every forecast origin** using the current rolling estimation window.

### Forecast production
Done at every forecast origin from that origin-specific parameter fit and the information available at that date.

The new pipeline is still expected to be much lighter than the previous design because:

- discrete specification search is not repeated at every origin;
- MSSTAR is removed;
- MSAR is more parsimonious;
- nonlinear fits use warm starts;
- valid fits are cached;
- stages are checkpointed;
- independent tasks can run in parallel.

# 4. Mandatory module structure

Recommended logical modules:

```
code/
  run_all.py
  src/
    data/
    transforms/
    diagnostics/
    specification/
    models/
    forecasting/
    evaluation/
    robustness/
    reporting/
  tests/
  configs/
```

Exact filenames may differ, but separation of responsibilities must remain clear.

# 5. Checkpointing

After each stage, save a deterministic checkpoint.

Minimum checkpoints:

1. frozen raw data;
2. processed targets;
3. stationarity decisions;
4. selected specifications;
5. nonlinear diagnostic results;
6. each model/refit fit;
7. forecasts;
8. evaluation metrics;
9. robustness outputs;
10. final tables/figures.

If a later stage fails, rerunning the project must not repeat valid earlier work.

# 6. Cache keys

Model-fit cache key must include:

- data snapshot hash;
- series;
- transformation;
- model;
- model specification;
- estimation-window start/end;
- refit date;
- code/config hash.

Never reuse a cache entry when any key element changes.

# 7. Warm starts

For MSAR and STAR:

- first refit uses documented deterministic initialization/multi-start logic;
- later refits may use the previous successful parameter vector as the first start;
- if warm start fails, use the original deterministic fallback starts;
- record which start succeeded.

Warm starts may accelerate optimization but may not change the objective function or parameter bounds.

# 8. Parallelization

Safe parallel units include:

- independent target series;
- independent model families;
- robustness specifications;
- independent model/series/horizon combinations.

Do not parallelize writes to the same output path.

Randomized procedures must use reproducible child seeds.

# 9. Runtime reporting

Every stage must log:

- wall-clock time;
- CPU time where available;
- number of fits attempted;
- number of fits reused from cache;
- number of failures;
- peak memory if practical.

Create:

`output/logs/runtime_summary.csv`

The purpose is to identify genuine bottlenecks rather than assume nonlinear models are slow.

# 10. Smoke-test mode

Provide a fast `--smoke-test` mode using:

- one monthly target;
- one quarterly target;
- simplified diagnostic settings where explicitly allowed by smoke-test configuration;
- short OOS block;
- all pipeline stages.

Smoke test validates code paths only. Its outputs must never be mixed with thesis baseline outputs.

# 11. Baseline run

Normal:

`python code/run_all.py`

must use:

- frozen data;
- approved baseline specifications;
- every-origin rolling re-estimation;
- all required outputs.

No internet retrieval in the default run.

# 12. Refresh run

Only explicit:

`python code/run_all.py --refresh-data`

may retrieve new data.

It must create a new dated snapshot and a separate output namespace.

It must not replace baseline outputs.

# 13. Robustness run separation

Robustness outputs must be stored separately from baseline outputs.

A robustness model may not overwrite or silently become the baseline because it performs better.

# 14. Failure behavior

A failed nonlinear model must:

- emit a structured failure record;
- preserve error/optimizer diagnostics;
- allow other independent models to continue;
- never trigger a silent change in parameterization.

# 15. Reproducibility tests

At minimum implement tests for:

- frozen-file hash verification;
- historical-vintage date equals 2026-10-05;
- expected raw and common sample endpoints;
- no manual or silent data substitution;
- transformations;
- annualization factors;
- lag construction;
- rolling-window boundaries;
- no future data in predictors;
- forecast target alignment;
- USREC used only for evaluation;
- every-origin rolling re-estimation alignment;
- deterministic cache key;
- reconstructed level forecast when a rate is modeled in differences;
- Harvey-Leybourne-Zu loss-differential construction for squared and absolute loss;
- Harvey-Leybourne-Zu local-demeaning and long-run variance calculation exactly matching the published procedure;
- deterministic recording of all Harvey-Leybourne-Zu smoothing/bandwidth choices;
- DM-HLN retained as a separate secondary procedure rather than overwriting the primary test;
- Giacomini-White recession/turning-point conditioning variables aligned to the forecast target date;
- monthly turning-point masks are reproducibly generated for ±1, ±3, and ±6 months around each NBER peak/trough;
- quarterly turning-point masks are reproducibly generated for the turning quarter only, ±1 quarter, and ±2 quarters;
- overlapping peak/trough windows are represented as a union so an observation is counted once;
- the baseline state table uses ±3 months monthly and ±1 quarter quarterly, while sensitivity outputs remain separate and may not silently replace the baseline;
- Model Confidence Set input loss matrix contains only admissible model forecasts on common forecast dates.

# 16. Part 6 starting condition

Before coding, Claude must read Parts 1–5 and produce an implementation plan.

It must explicitly show how each Part 5 section maps to code modules and outputs, then stop for user approval as required by CLAUDE.md.
