# CLAUDE.md
# Claude Code Instructions for the PhD Thesis Project

## 1. Your role

You are responsible only for Parts 6, 7, and 8 of this PhD research project.

Parts 1–5 are developed externally by the user and ChatGPT.

Their approved outputs are stored in:

`approved-specs/`

Treat those files as authoritative research specifications.

Do not redo Parts 1–5.

Do not redesign the thesis structure.

Do not redesign the approved methodology.

Do not begin writing the final thesis.

Part 9 will be completed externally by ChatGPT after Part 8 is finished and approved.


## 2. Your responsibilities

### Part 6 — Build and validate the empirical pipeline

Build the Python code required to implement the methodology defined in:

`approved-specs/part5/`

The pipeline must cover, where required by the approved methodology:

- data acquisition;
- raw-data preservation;
- transformations;
- descriptive statistics;
- stationarity and diagnostic tests;
- nonlinearity tests;
- lag selection;
- baseline models;
- nonlinear models;
- forecasting;
- forecast evaluation;
- robustness analysis;
- tables;
- figures;
- equations or parameter summaries;
- execution logs.

Part 6 is an implementation-and-validation stage. Use unit tests, targeted test runs, and smoke tests to verify the code paths and scientific logic. Do not treat Part 6 as the final full empirical execution.

Do not silently modify the approved methodology during implementation.

When the Part 6 implementation is complete and passes its required tests/smoke runs, stop and wait for explicit user approval before starting Part 7.


### Part 7 — Reproducibility

Maintain:

`code/run_all.py`

or the equivalent approved project entry point.

Demonstrate that a single command can reproduce the complete empirical pipeline from the frozen thesis dataset to the final empirical outputs.

The pipeline must:

- be deterministic where possible;
- use fixed random seeds where relevant;
- record failures rather than hiding them;
- generate logs;
- preserve baseline outputs;
- separate baseline analysis from robustness analysis;
- never overwrite the frozen thesis dataset with refreshed data.

Part 7 is the reproducibility stage. Its purpose is to verify that the approved pipeline can be reproduced end to end from the frozen data using the approved entry point.

After reproducibility has been demonstrated, stop and wait for explicit user approval before beginning Part 8.


### Part 8 — Final empirical execution, audit, and analysis

After Part 7 is complete and the user approves starting Part 8:

1. run the complete final analysis;
2. inspect all tables and figures;
3. check whether models converged correctly;
4. identify unstable, failed, fragile, or implausible results;
5. compare baseline and robustness results;
6. analyze the empirical findings without forcing a preferred conclusion;
7. determine which claims are supported by the evidence;
8. identify which jury remarks have been empirically addressed.

Produce the final Part 8 reports in:

`reports/part8/`

At minimum create:

- `full_empirical_analysis_report.md`
- `main_findings.md`
- `robustness_findings.md`
- `jury_resolution_status.md`
- `final_claims_allowed.md`


## 3. Source-of-truth hierarchy

When instructions or files appear to conflict, use this order of authority:

1. `approved-specs/part5/`
   Final approved methodology.

2. `approved-specs/part4/`
   Final approved thesis structure and empirical role.

3. `approved-specs/part2/`
   Jury requirements.

4. `approved-specs/part3/`
   Diagnosis of the submitted thesis and previous methodology.

5. `approved-specs/part1/`
   Structural principles learned from reference dissertations.

6. `notes/`
   Working material only. Notes are not authoritative unless explicitly approved.

If two authoritative files conflict, stop and tell the user rather than choosing silently.


## 4. Methodology lock

The approved methodology in `approved-specs/part5/` is locked.

Do not independently change:

- variables;
- data transformations;
- sample definition;
- stationarity rules;
- lag-selection rules;
- baseline models;
- nonlinear models;
- number of baseline regimes;
- forecast horizons;
- estimation windows;
- forecast metrics;
- predictive tests;
- robustness specifications.

If implementation reveals a problem:

1. stop the affected analysis;
2. document the problem in `notes/claude/`;
3. explain the methodological or computational issue;
4. propose possible solutions;
5. wait for explicit user approval.

Never choose a different specification because it produces better results.


## 5. Baseline versus robustness

Keep the approved baseline specification separate from robustness specifications.

Do not replace the baseline because a robustness specification performs better.

Results must be labeled clearly as:

- baseline;
- robustness;
- diagnostic;
- failed specification;
- exploratory, if explicitly authorized.


## 6. Result-blind research rule

Do not modify:

- transformations;
- lags;
- regimes;
- horizons;
- windows;
- tests;
- model definitions;

solely because a change improves the empirical result.

The purpose is to test the approved research design, not to manufacture model superiority.


## 6A. Implementation-error correction rule

Coding or implementation errors may be corrected when discovered.

For every material correction:

1. document the error and its cause in `notes/claude/`;
2. record what code was changed;
3. identify which outputs may have been affected;
4. regenerate all affected downstream outputs;
5. preserve enough information to distinguish superseded outputs from corrected outputs.

A coding fix must not be used to alter an approved methodological choice.

If the proposed correction would change any locked methodological element in `approved-specs/part5/`, stop and request explicit user approval before making that methodological change.


## 7. Model failures

Do not hide failed models.

Examples include:

- non-convergence;
- implausible coefficients;
- explosive forecasts;
- nearly absorbing regimes;
- empty regimes;
- singular covariance matrices;
- unidentified transition parameters;
- unstable rolling estimates.

Record these explicitly.

If a model fails, preserve enough diagnostic information to explain why.


## 8. Frozen-data reproducibility rule

The final dissertation must use a frozen data snapshot.

The default empirical pipeline must use:

`data/frozen/`

and must reproduce the exact dataset used for the thesis.

The frozen dataset must never be silently replaced or overwritten.

Any fresh download must require explicit user action, such as:

`--refresh-data`

Fresh data must be stored separately under:

`data/refreshed/<date>/`

and must never overwrite the thesis baseline dataset or its outputs.

Every final empirical output must record, directly or through an associated manifest:

- the run ID;
- the data snapshot used;
- the frozen-data hash or manifest hash;
- the data cutoff date;
- retrieval/vintage information where relevant;
- the code commit SHA;
- the configuration hash;
- the execution timestamp.

These provenance fields must be sufficient to reconstruct which data, code, and configuration produced every thesis-facing empirical artifact.


## 9. Numerical traceability

Every exact empirical number later used in the thesis must be traceable to a file under:

`output/`

Do not treat prose written in `notes/` or `reports/` as the authoritative source of numerical results.

Tables, model coefficients, forecast metrics, diagnostic statistics, and robustness results must originate from reproducible outputs.


## 10. File rules

Do not modify files inside:

`approved-specs/`

unless the user explicitly requests it.

Do not modify original source documents if any are stored under:

`source-materials/`

Use:

`notes/claude/`

for implementation notes, warnings, methodological questions, and temporary analysis.

Use:

`code/`

for research code.

Use:

`data/`

for datasets.

Use:

`output/`

for generated empirical results.

Use:

`reports/part8/`

for the final empirical interpretation and audit.


## 11. Scientific interpretation

The thesis compares forecasting models.

Do not infer causal economic effects from predictive results unless the approved methodology explicitly supports causal identification.

Distinguish:

- statistical fit;
- forecasting performance;
- statistical significance;
- regime interpretation;
- economic interpretation;
- causal claims.

Do not claim that nonlinear models are superior unless the final reproduced evidence supports that claim.


## 12. Jury remarks

Use the permanent jury IDs defined in:

`approved-specs/part2/`

When an analysis or robustness exercise responds to a jury remark, reference its ID.

A jury request is satisfied by properly performing and reporting the requested analysis.

It is not necessary for the requested test to produce the result the reviewer may have expected.


## 13. Before starting Part 6

Before writing research code:

1. read all files in `approved-specs/part1/` through `part5/`;
2. inspect the repository structure;
3. summarize your understanding of the approved methodology;
4. identify any contradictions, ambiguities, or missing implementation details;
5. produce an implementation plan;
6. stop and wait for user approval.

Do not begin empirical coding until the user approves the implementation plan.

After that approval, proceed only through Part 6. When Part 6 is complete, stop for approval before Part 7. When Part 7 reproducibility is complete, stop again for approval before Part 8. Do not collapse Parts 6, 7, and 8 into one uninterrupted execution.


## 14. Final principle

Prefer:

- simple research questions;
- transparent specifications;
- reproducible execution;
- explicit diagnostics;
- careful robustness;
- visible failures;
- restrained conclusions.

Complexity is acceptable only when it is required by the approved methodology and supported by the evidence.
