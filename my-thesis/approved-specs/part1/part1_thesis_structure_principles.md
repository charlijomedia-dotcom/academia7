# Part 1: Structure principles for the revised forecasting monograph

**Date:** 3 October 2026  
**Status:** Proposed principles, supported by the completed Part 1 comparison and submitted for user review. No final chapter structure or methodology is approved by this file.  
**Evidence companion:** `part1_reference_thesis_benchmarks.md`  
**Intended repository location after review:** `approved-specs/part1/`

## 1. Purpose and limits

These principles translate the supplied benchmark dissertations into a practical standard for the user's coherent economics monograph. They do not prescribe a three-paper thesis, a fixed number of chapters, or a page target. They do not select models or determine findings.

The benchmark evidence and PDF page references appear in the companion report. Rules below are labeled by origin:

- **Benchmark-derived:** an adaptation of an observed practice, rather than a universal rule followed by every author.
- **User requirement:** a writing or workflow preference stated in the project brief.
- **Project safeguard:** a proposed rule needed for an empirical, reproducible dissertation. It is not attributed to the historical benchmarks.

## 2. Governing principle

The final thesis must make it possible to trace each major conclusion back through its evidence, method, assumptions, and research question.

Every substantive chapter must have a clear function in that chain. A shared subject such as “macroeconomics” is not enough to establish coherence. The reader must understand why this chapter is needed and how it changes what can be argued next.

## 3. Principles and acceptance checks

| ID | Principle | Origin and source | Acceptance check |
|---|---|---|---|
| P1-01 | State one central research problem and its scope | Benchmark-derived: Shiller (1972), PDF pp. 8–17; Del Campo (2018), PDF pp. 35–40 | A reader can identify the main question, the object studied, and the intended contribution from the introduction |
| P1-02 | Give each chapter a distinct task | Benchmark-derived: Shiller, PDF pp. 4, 99; Akerlof (1966), PDF pp. 3–4 | Each chapter has a one-sentence purpose and an identifiable output used in the overall argument |
| P1-03 | Motivate technical choices with the problem they solve | Benchmark-derived: Bernanke (1979), PDF pp. 8–12; Shiller, PDF p. 64 | The purpose of a model, assumption, or procedure is explained before or alongside its formal statement |
| P1-04 | Retain literature that changes the argument | Benchmark-derived adaptation: focused openings in Bernanke and Shiller | Each literature section establishes a mechanism, disagreement, gap, or methodological choice needed later |
| P1-05 | Match claims of originality to actual contributions | Project safeguard, informed by Shiller's estimator contribution | The thesis distinguishes new theory or methods from application, comparison, replication, and synthesis |
| P1-06 | Make concepts and equations usable | Benchmark-derived: Akerlof, PDF p. 11; Bernanke, PDF pp. 12–17 | Necessary symbols, assumptions, domains, and interpretations are defined; equations are referenced in the argument |
| P1-07 | Explain the link from theory to empirical analysis | Benchmark-derived: Shiller, PDF p. 99 | Each analysis states which question it addresses and what its possible outcomes would mean |
| P1-08 | Organize main results around questions | Project adaptation of the model-to-evidence progression | The reader can find the answer to each research subquestion without reconstructing it from software output |
| P1-09 | Keep inconclusive and adverse findings visible | Benchmark-derived: Bernanke, PDF p. 101; Akerlof, PDF pp. 83–84 | Failed estimation, mixed rankings, and unsupported claims are documented and reflected in conclusions |
| P1-10 | Make robustness answer a specific concern | Benchmark-derived adaptation: Shiller, PDF p. 165 | Each robustness exercise states the threat it addresses and how it affects the conclusion |
| P1-11 | Use appendices to support the argument | Benchmark-derived: Akerlof, PDF pp. 25–33; Del Campo, PDF pp. 9–11 | The main text remains assessable; appendices contain referenced supporting detail |
| P1-12 | Provide explicit chapter transitions | Benchmark-derived: Akerlof, PDF pp. 3–4; Del Campo, PDF pp. 38–40 | Each transition identifies what is now established and what remains to be addressed |
| P1-13 | End substantive chapters with a consistent summary | User requirement | About one page, covering the question, established findings, takeaway, and next step; no new result or argument |
| P1-14 | End the thesis with a qualified integrated answer | Benchmark-derived: Del Campo, PDF pp. 145–150 | The conclusion answers the central question, distinguishes conditions and limitations, and adds no new evidence |
| P1-15 | Use simple sentences with precise economics | User requirement | Short, direct sentences; objective tone; technical terms retained where needed; no em dashes |
| P1-16 | Use consistent APA citations and references | User requirement | Each cited work has a matching reference; source support is checked; quotations carry locators |
| P1-17 | Keep final writing traceable to reproduced outputs | Project safeguard and agreed workflow | Empirical claims link to verified tables, figures, configurations, and the Part 8 report |

## 4. What the introduction must accomplish

The introduction should allow an informed economist to answer seven questions:

1. What economic problem motivates this thesis?
2. Why is that problem important within the stated scope?
3. What does existing research leave unresolved?
4. What precise question and subquestions does this dissertation address?
5. What kind of contribution does it make?
6. How will the empirical design address the question?
7. What does the evidence establish, and how do the chapters develop the answer?

The seventh item has two stages. Before Parts 6–8, describe the planned analysis without pretending its results exist. In the final Part 9 manuscript, preview the verified main findings and their qualifications.

Del Campo provides a useful example of an introduction that connects concepts, questions, and results. Shiller provides a useful example of stating a precise model and its empirical relevance early. Neither requires copying the length of the original introduction.

The exact question for this dissertation remains to be settled through Parts 2–5. An illustrative question about whether nonlinear forecasting gains persist across periods and horizons is only an illustration, not an approved research design.

## 5. How to decide what stays in the literature and theory discussion

For every proposed section, write one sentence completing:

“This section is necessary because it enables the reader to understand or assess ___.”

Retain material that defines the problem, motivates an examined mechanism, identifies a research gap, justifies a design choice, or establishes a limitation. Condense or remove general background that does none of these things.

Do not remove material merely because it is theoretical or mathematical. The benchmarks contain substantial formal analysis. The goal is relevance and a clear explanation of its role.

Similarly, do not claim that all theory must be interleaved with results. A coherent monograph may have dedicated theory and methodology chapters. It must explain their purpose before asking the reader to work through them.

## 6. How to present methods without creating an oversized catalogue

Separate three tasks:

| Task | What belongs in the main text | What may belong in an appendix |
|---|---|---|
| Define the economic and statistical problem | Objects of interest, assumptions, relevant mechanisms, and information available | Supplementary background that is useful but not necessary to follow the claim |
| Explain the approved empirical design | Data definitions, transformations, essential model equations, estimation logic, evaluation design, and decision rules | Long derivations, extra algorithm detail, and supplementary specifications |
| Document reproducibility | A concise account of data snapshots, configurations, outputs, and how results are regenerated | Detailed manifests, full output tables, implementation records, and software environment details |

Exact placement is a Part 4 decision. Exact methods are a Part 5 decision. Important conditions must remain visible even if their derivations move to an appendix.

Shiller's two estimator chapters are justified partly by his methodological contribution. Their existence does not justify two long chapters that only summarize established methods in this project.

## 7. How to organize results and interpretation

The following order describes the questions the reader needs answered. It is not a final chapter list:

1. What are the relevant properties and limitations of the data?
2. Were the specified models estimated successfully and credibly?
3. What does the approved evaluation show?
4. How do findings differ across the approved comparisons?
5. Which conclusions survive the planned checks?
6. What can these results support economically, and what remains unresolved?

A main table or figure should have a stated purpose. Its discussion should identify the main pattern, the evidence supporting it, relevant uncertainty, and the consequence for the research question. It should not narrate every cell.

The final text must distinguish descriptive features, in-sample fit, out-of-sample performance, statistical evidence, and causal interpretation. These categories must not be merged because they concern the same model.

Mixed evidence is an acceptable scientific outcome. No section should be written in advance on the assumption that the most complex model will win.

## 8. Robustness and limitations

Robustness should be organized around threats to a conclusion, with each exercise linked to its purpose. A useful reporting template is:

| Field | Required content |
|---|---|
| Concern | What feature might make the main conclusion unreliable? |
| Approved check | What planned analysis addresses that concern? |
| Result | What happened, including failures or uncertainty? |
| Implication | Does the original conclusion hold, require qualification, or fail? |

The benchmark comparison does not authorize particular checks. Choices about regimes, horizons, stationarity, multivariate extensions, or data transformations belong to Part 5 after review of the jury's requirements.

Limitations should be specific to the data, design, estimation, and interpretation. They should explain how the scope of the conclusion changes. A generic closing paragraph about “more research” is insufficient.

## 9. Standard chapter opening and chapter summary

### Opening

A substantive chapter should state its question, why it follows the preceding chapter, the approach taken, and what it establishes. It can then give a short functional roadmap. This need not be a rigid four-paragraph template.

### Chapter Summary

The final substantive section should be titled **Chapter Summary** and occupy about one page in the final document. Page length depends on formatting; do not pad it to a word quota.

It should:

1. Restate the chapter's question.
2. Summarize only what the chapter established.
3. State the main takeaway and any essential qualification.
4. Explain what the next chapter must now address.

It must introduce no new literature, empirical result, or argument. The consistent one-page format is the user's requirement. It is not claimed to be a convention observed in all four benchmark theses.

## 10. Monograph coherence checklist for Part 4

Before approving the new structure, assess it against these questions:

- Can the entire thesis be described as one research project without listing unrelated papers?
- Does every chapter serve the central question?
- Does each empirical subquestion have an identifiable evidence section?
- Are essential definitions and notation consistent across chapters?
- Are repeated literature reviews, data descriptions, and method explanations consolidated or cross-referenced?
- Does every major transition explain why the next step is needed?
- Are appendices referenced and necessary detail retained?
- Does the conclusion synthesize the answer rather than merely repeat chapter summaries?
- Does the proposed outline explicitly accommodate requirements established in Part 2?
- Is the length justified by the work rather than by an arbitrary benchmark target?

Failure on a question calls for revision of the outline. It does not automatically require a new model or a larger empirical project.

## 11. Required Part 4 mapping

For each proposed chapter, Part 4 should produce this mapping:

| Field | Required entry |
|---|---|
| Working chapter title | A title that signals its scientific function |
| Question | The question the chapter answers |
| Input | Which prior definitions, findings, or decisions it needs |
| Contribution | What it adds to the overall argument |
| Evidence or analysis | How it supports that contribution |
| Jury requirements | IDs from the verified Part 2 registry |
| Part 1 principles | Relevant P1 identifiers from this file |
| Output and transition | What the reader knows afterward and why the next chapter follows |
| Appendix boundary | What supporting detail is placed outside the main chapter |

This turns general lessons from the benchmarks into a reviewable structure. It should be completed after the jury reports and the submitted thesis have been examined.

## 12. Handoff rules

These two Part 1 documents are inputs for the design work. They are not instructions to Claude Code to begin analysis.

- ChatGPT and the user complete Parts 1–5 and review their outputs.
- Only approved specifications become the authority for implementation.
- Claude Code implements Parts 6–8 according to the approved Part 5 methodology and Part 4 architecture.
- If an illustrative suggestion in this file conflicts with the approved methodology, it does not authorize a change.
- Part 9 uses the approved structure and methodology together with verified Part 8 evidence.

The final empirical text must be traceable to the frozen thesis dataset and reproduced outputs. Refreshing data should create a separate dated snapshot and must not silently replace the thesis baseline. Those requirements come from the agreed project workflow, not from the historical benchmark dissertations.

## 13. References

Akerlof, G. A. (1966). *Wages and capital* [Doctoral dissertation, Massachusetts Institute of Technology].

Bernanke, B. S. (1979). *Long-term commitments, dynamic optimization, and the business cycle* [Doctoral dissertation, Massachusetts Institute of Technology].

Del Campo, S. (2018). *Interdépendances entre l'équité intra et intergénérationnelle dans la gestion durable des ressources environnementales* [Doctoral dissertation, Université Paris Nanterre].

Shiller, R. J. (1972). *Rational expectations and the structure of interest rates* [Doctoral dissertation, Massachusetts Institute of Technology].

Source filenames, page conventions, and detailed evidence are recorded in the companion benchmark report.
