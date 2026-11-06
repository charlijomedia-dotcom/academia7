# LOCAL PARTIAL REHEARSAL: not the Part 8 dry run

Date: 6 November 2026.

**What ran.** The integration code (stages 1 to 5) on real inputs:
- the base tree: published output plus the B1-staged overlay;
- the original fit cache (18,964 payloads);
- the Tier A archive (sha256 `df73c295…`, fetched from Drive);
- the two B2 chains (1,390 payloads, verified against the B2 certificate);
- the pinned workflow at a clean worktree of `8aaa4217…`.

**What did not run.** The B1 and B3 checkpoints are on Drive only, so **7 of the 17 re-estimated chains were unavailable**. Their exercises stay pending, so A3, A4 and A8 fail here, as expected. The stage-0 preflight against Drive did not run either (certificates, Drive listings).

**Results:**
- A1, A5, A6, A7, A9, A10, A11, A12, A13 and A15 pass;
- 0 unexplained differences among 3,354 changed cells against the base.

**Status.** Nothing here is a thesis result or a release. The authoritative run is the Colab dry run (`colab/r1_part8_integration_dryrun.ipynb`).
