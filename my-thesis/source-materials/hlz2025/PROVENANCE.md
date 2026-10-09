# Harvey, Leybourne and Zu (2025) — source material provenance

**Purpose:** M3 requires the HLZ procedure to be implemented exactly as the authors define it, with the version or checksum of the source recorded for validation. This file records what was retrieved, from where, and what is still missing.

## Retrieved

| Item | Supplementary Appendix to "Testing for Equal Average Forecast Accuracy in Possibly Unstable Environments" |
|---|---|
| Authors | David I. Harvey, Stephen J. Leybourne, Yang Zu |
| Dated | 21 August 2024 (appendix); figshare version v2, published 2024-12-02 |
| File | `ubes_a_2418835_sm8120.pdf` (17 pages) |
| Source | figshare (Taylor & Francis supplementary deposit), DOI `10.6084/m9.figshare.27284039.v2`, download `https://ndownloader.figshare.com/files/49942073` |
| License | CC BY 4.0 |
| Retrieved | 2026-10-09 |
| SHA-256 | `4cb055b058f315e1c5218878fbae067d47278fc6b2d0bd992b1dcdff5873a798` |
| MD5 | `fe9b22650496d6a5c2f7ff1f7e61a0a8` (matches the `computed_md5` published by the figshare API) |

## What the appendix establishes (verified from the document, not from memory)

- **Standard DM long-run variance (full-sample demeaning):**
  `Ω̂ = n⁻¹ Σₜ Σₛ (dₜ − d̄)(dₛ − d̄) k((t−s)/b)`
- **Modified long-run variance (local demeaning):**
  `Ω̂′ = n⁻¹ Σₜ Σₛ (dₜ − m̂ₜ)(dₛ − m̂ₛ) k((t−s)/b)`
- **Local mean estimator:** `m̂ₜ = Σₛ w₍ₜ,ₛ₎ dₛ` with Nadaraya–Watson weights
  `w₍ₜ,ₛ₎ = K((s−t)/(nh)) / Σⱼ K((j−t)/(nh))`, i.e. a local-constant kernel smoother in rescaled time with bandwidth `h` and effective local sample size `nh`.
- **Modified statistic:** `DM′ = √n · d̄ / √Ω̂′`, with standard normal asymptotic reference under the null.
- **Why the standard test fails:** under a time-varying mean `m(x)`, `Ω̂ = Oₚ(b)` diverges, so `DM →ᵖ 0` and the test has asymptotic size zero (Theorem 2); `Ω̂′ →ᵖ Ω` whether the mean function is time varying or constant (Theorem 4).
- **Appendix C — finite-sample critical values (parametric bootstrap):**
  1. simulate `{d*ₜ}ₜ₌₁ⁿ` iid `N(0,1)` with `n` the actual sample size;
  2. compute `DM′*` on the simulated sample **using the same kernels `K(·)`, `k(·)` and the same bandwidths `b` and `h` as in the actual test statistic**;
  3. repeat `B` times;
  4. take the empirical quantiles of the `B` simulated statistics as the critical values.
  The authors state these are exact when `dₜ` is iid normal with zero mean variation and serve as approximations otherwise, and that the scheme greatly improves finite-sample size.

## Still missing — required before HLZ can be implemented

The appendix does **not** state the following; they are in the main article (sections referenced in the appendix as "section 5.1 of the paper" and the two empirical applications):

1. the functional form of the long-run-variance kernel `k(·)`;
2. the functional form of the local-demeaning kernel `K(·)`;
3. the rule or value for the long-run-variance bandwidth `b`;
4. the rule or value for the local-demeaning bandwidth `h`;
5. the number of simulation replications `B` used for the critical values;
6. any recommended one- or two-sided usage and the treatment of multi-step forecast horizons.

**These will not be guessed.** The HLZ module is written so that `k`, `K`, `b`, `h` and `B` are required configuration inputs with **no defaults**, and the module refuses to run until they are supplied from the article. No generic Newey–West/HAC substitute may be labelled HLZ (Part 5 §10.2; Comp §15).

## Retrieval attempts for the main article (all unsuccessful, 2026-10-09)

The article is confirmed open access (CC-BY-NC-ND) by Unpaywall, OpenAlex, Semantic Scholar and Crossref. Every resolvable full-text location is one of two URLs, and both are behind a Cloudflare bot challenge that automated retrieval cannot pass:

- `https://www.tandfonline.com/doi/full|pdf|epdf/10.1080/07350015.2024.2418835` → HTTP 403, Cloudflare "Just a moment..." interstitial
- `https://nottingham-repository.worktribe.com/file/40565499/...` (and `/OutputFile/40565498`) → HTTP 403, same interstitial

Also tried: Unpaywall, OpenAlex, Semantic Scholar, Crossref TDM links (all resolve to the two URLs above); Yang Zu's homepage and its new GitHub Pages site; the University of Macau department page (abstract only, links back to the publisher); Wayback Machine (no snapshot) and the CDX index (blocked); fatcat/scholar.archive.org (unreachable or rate limited); CORE API (HTTP 429, requires a key); a Granger Centre working-paper version (none found).

**Action needed from the user:** download the open-access PDF from `https://doi.org/10.1080/07350015.2024.2418835` in a normal browser and place it in this directory as `hlz2025_article.pdf`. Nothing else is needed; the supplement is already here.
