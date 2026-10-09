# Harvey, Leybourne and Zu (2025) — source material provenance

**Purpose:** M3 requires the HLZ procedure to be implemented exactly as the authors define it, with the version or checksum of the source recorded for validation. Both documents are now held here and the implementation is complete.

## Held in this directory

| | Article | Supplementary appendix |
|---|---|---|
| Title | Testing for Equal Average Forecast Accuracy in Possibly Unstable Environments | Supplementary Appendix to the same |
| Authors | David I. Harvey, Stephen J. Leybourne, Yang Zu | same |
| Published | *Journal of Business & Economic Statistics*, 2025, 43(3), 643–656; online 2 Dec 2024 | appendix dated 21 August 2024 |
| DOI | `10.1080/07350015.2024.2418835` | `10.6084/m9.figshare.27284039.v2` |
| License | CC BY-NC-ND 4.0 (open access) | CC BY 4.0 |
| File | `Testing for Equal Average Forecast Accuracy in Possibly Unstable Environments.pdf` | `ubes_a_2418835_sm8120.pdf` |
| SHA-256 | `13cd3bbddf19ec5019e517c9af556c7d171a3f96b10010d36c9b6042407bb587` | `4cb055b058f315e1c5218878fbae067d47278fc6b2d0bd992b1dcdff5873a798` |
| MD5 | — | `fe9b22650496d6a5c2f7ff1f7e61a0a8` (matches figshare's published `computed_md5`) |
| Obtained | supplied by the user, 2026-10-09 | downloaded from figshare, 2026-10-09 |

The article could not be retrieved programmatically: the publisher page and the Nottingham repository both sit behind a Cloudflare bot challenge, every aggregator (Unpaywall, OpenAlex, Semantic Scholar, Crossref) resolves to those same two URLs, there is no Wayback snapshot, and the CORE API requires a key. The user supplied it directly.

## What the implementation uses, and where each value comes from

Everything below is quoted or transcribed from the two documents. Nothing is inferred or remembered.

### Estimator (article eq. 2, 4, 5 and p.648; supplement Theorems 1 and 4)

```
local mean       m̂_t = Σ_s w_{t,s} d_s,   w_{t,s} = K((s−t)/(nh)) / Σ_s K((s−t)/(nh))
modified LRV     Ω̂′  = n⁻¹ Σ_t Σ_s (d_t − m̂_t)(d_s − m̂_s) k((t−s)/b)        (eq. 4)
standard LRV     Ω̂   = n⁻¹ Σ_t Σ_s (d_t − d̄)(d_s − d̄) k((t−s)/b)            (eq. 2)
statistic        DM′ = √n · d̄ / √Ω̂′                                          (p.648)
mean variation   V̂_m = n⁻¹ Σ m̂_t² − (n⁻¹ Σ m̂_t)²                             (eq. 5)
```

Note the local-mean kernel argument is scaled by `nh`, not `h`.

### Kernels and bandwidths (article §5, p.649)

> "We construct DM and DM′ using their respective LRV estimators, Ω̂ and Ω̂′, employing the quadratic spectral (QS) kernel for k(.) with bandwidth b = b₀n^(1/3) … For the local mean estimator m̂_t in Ω̂′ we use the Gaussian kernel for K(.). … we found that setting b₀ = 1.5 and h = h₀n^(−2/5) with h₀ = 0.25 delivered a good balance of finite sample size and power performance … and we therefore adopt these throughout the remainder of the article."

| Choice | Value |
|---|---|
| `k(·)` long-run-variance kernel | quadratic spectral (Andrews 1991) |
| `b` | `1.5 · n^(1/3)` |
| `K(·)` local-demeaning kernel | Gaussian |
| `h` | `0.25 · n^(−2/5)` |

§6 (p.653) confirms the empirical applications use "exactly the same kernel and bandwidth choices as used for our finite sample simulations in Section 5", so the same settings apply to real forecast evaluations and to any horizon `q`.

### Critical values (supplement Appendix C; article §5, p.649)

Simulate iid `N(0,1)` `{d*_t}` of the actual length `n`, recompute `DM′` **with the same kernels and bandwidths**, repeat `B` times, and take empirical quantiles. The article's simulations use **50,000 replications** and nominal 0.05-level two-tailed tests. The authors state these critical values are exact when `d_t` is iid normal with zero mean variation and serve as approximations otherwise, and that:

> "Because the tests' sizes can be sensitive to the choice of kernels and associated bandwidths b and h in relatively small samples, it is important in practice to use finite sample null critical values for DM and DM′."

### Why that last point matters here

Measured during implementation with the article's own settings, the simulated two-sided 5% critical value for `DM′` is **5.16 at n = 120, 3.49 at n = 480 and 3.24 at n = 700**, against the asymptotic 1.96. The gap comes from `b/(nh) = 6·n^(−4/15)`, which is still of order one at realistic sample sizes, so local demeaning removes variance at exactly the lags the long-run-variance kernel weights and `Ω̂′` is biased downward in finite samples. Using standard normal critical values would therefore over-reject severely. The implementation always uses the Appendix C scheme; this is covered by a validation test.

### Two-sided versus one-sided

The formal test (Theorems 2, 5, 6) is two-sided, `|DM′| > z_{1−α/2}`, and the size and power simulations use "nominal 0.05-level two-tailed tests". The empirical applications in §6 instead report one-sided tail p-values (Tables 3 and 4). The implementation reports the **two-sided p-value as the headline**, matching the formal test and the equality null of Part 5 §10.2, and **also stores both one-sided p-values**. See decision item H1 in `notes/claude/part6_issues_and_decisions.md` — flagged for the user to confirm or override.

### Additional reported diagnostic

The article's Tables 3 and 4 report `V̂_m / Ω̂′` as a standardized measure of mean-function variation, and use it to explain where DM and DM′ diverge. The implementation reports it too, because it directly evidences whether the instability that motivates using HLZ is actually present in each comparison.

## Validation performed

`code/tests/validation/test_hlz.py` (39 tests, all passing) checks the QS kernel's defining properties and a directly computed value, the Gaussian kernel, both bandwidth rules and the Assumption 4 and 6 rate conditions, weight normalization, and reproduces from the article:

- the simulation DGP's stated mean variation `V_m = 0.867a²`, and the Table 1 values 0.009, 0.078 and 0.217 for `a` = 0.1, 0.3 and 0.5;
- **Theorem 1**: adding the time-varying mean inflates `Ω̂` more than threefold while leaving `Ω̂′` essentially unchanged, and the inflation grows with `b`;
- **Theorem 4**: the `Ω̂′` finite-sample bias shrinks as `n` grows;
- **Theorems 2(i)(b) and 5(i)**: under a time-varying mean the standard DM test's size collapses below 3% while DM′ holds its nominal level — the result that makes HLZ the right primary test for this thesis;
- Appendix C critical values deliver nominal size on fresh iid normal data.
