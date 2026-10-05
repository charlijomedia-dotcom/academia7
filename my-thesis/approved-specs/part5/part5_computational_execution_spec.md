# Part 5: Computational execution specification

**Date:** 5 October 2026  
**Status:** PROPOSED FOR USER APPROVAL  
**Purpose:** Implement the approved methodology from scratch without reproducing the unnecessary computational burden of the previous thesis pipeline.

# 1. Clean build

Claude Code must build the research code from scratch from the Part 5 specification.

No old thesis code is assumed to exist.

Scientific validity has priority over runtime, but the code must not repeat work that the methodology does not require.

# 2. Main efficiency rule

The pipeline must distinguish:

### Specification selection
Done on the initial estimation window only:

- baseline transformation decision;
- AR lag;
- ARMA order;
- STAR delay/type;
- nonlinear structural tests.

### Parameter re-estimation
Done on the scheduled rolling refit calendar:

- monthly every 3 months;
- quarterly every 4 quarters.

### Forecast production
Done at every forecast origin using the most recently approved parameter fit and currently available lagged target observations.

This is the main reason the new pipeline should be much lighter than the previous every-origin full re-search/re-estimation architecture.

# 3. Mandatory module structure

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

# 4. Checkpointing

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

# 5. Cache keys

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

# 6. Warm starts

For MSAR and STAR:

- first refit uses documented deterministic initialization/multi-start logic;
- later refits may use the previous successful parameter vector as the first start;
- if warm start fails, use the original deterministic fallback starts;
- record which start succeeded.

Warm starts may accelerate optimization but may not change the objective function or parameter bounds.

# 7. Parallelization

Safe parallel units include:

- independent target series;
- independent model families;
- bootstrap replications;
- robustness specifications.

Do not parallelize writes to the same output path.

Randomized procedures must use reproducible child seeds.

# 8. Runtime reporting

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

# 9. Smoke-test mode

Provide a fast `--smoke-test` mode using:

- one monthly target;
- one quarterly target;
- reduced bootstrap replications;
- short OOS block;
- all pipeline stages.

Smoke test validates code paths only. Its outputs must never be mixed with thesis baseline outputs.

# 10. Baseline run

Normal:

`python code/run_all.py`

must use:

- frozen data;
- approved baseline specifications;
- scheduled refit;
- all required outputs.

No internet retrieval in the default run.

# 11. Refresh run

Only explicit:

`python code/run_all.py --refresh-data`

may retrieve new data.

It must create a new dated snapshot and a separate output namespace.

It must not replace baseline outputs.

# 12. Robustness run separation

Robustness outputs must be stored separately from baseline outputs.

A robustness model may not overwrite or silently become the baseline because it performs better.

# 13. Every-origin robustness

The expensive every-origin re-estimation is restricted to:

- h=1;
- final 120 monthly origins;
- final 40 quarterly origins;
- fixed model specifications.

This directly tests the effect of the efficient baseline refit schedule while preventing the old full-sample design from dominating runtime.

# 14. Failure behavior

A failed nonlinear model must:

- emit a structured failure record;
- preserve error/optimizer diagnostics;
- allow other independent models to continue;
- never trigger a silent change in parameterization.

# 15. Reproducibility tests

At minimum implement tests for:

- transformations;
- lag construction;
- rolling-window boundaries;
- no future data in predictors;
- forecast target alignment;
- USREC used only for evaluation;
- scheduled-refit calendar;
- deterministic cache key;
- reconstructed level forecast when a rate is modeled in differences.

# 16. Part 6 starting condition

Before coding, Claude must read Parts 1–5 and produce an implementation plan.

It must explicitly show how each Part 5 section maps to code modules and outputs, then stop for user approval as required by CLAUDE.md.
