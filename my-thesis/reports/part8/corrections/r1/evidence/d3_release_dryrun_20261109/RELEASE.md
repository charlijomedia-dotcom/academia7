# Final corrected Part 8 release `part8-final-20261109`

**Canonical thesis-facing numbers:** `my-thesis/output/` in this commit (465 files).
Any number used in the thesis must equal a file listed in `release_inventory.csv`
(sha256 `aee17b8446e37e95acc1194d7ce914133d9d34573cc88b4d4436e2aa8c7a5071`). Files under `output/` in any other commit
are superseded or provisional.

| Identity | Value |
|---|---|
| Numbers (every table, forecast and fit) | run `correction-20261107T193414-949fcd76` (archived reconstruction), equivalent to audited run `correction-20261108T053328-949fcd76`; scientific code `8aaa4217536ab3cb942dd248dd19ece7838a8d60` |
| Candidate archive | `archive-20261109T080914Z-3c7d68` (tar sha256 `54b61285a732f44d9ef9f1a5e97e6a04f45f287f49dbcf044e6d2574d1d7b4ee`) |
| F3.4 figures | F8 re-render `f8render-20261109T104031Z-e78cf5` (2026-11-09T10:40:31Z); presentation only |
| Publication | `publish-20261109T104032Z-a4f134` |

**Differences from the archive:** exactly 25 paths (`archive_to_release_diff.csv`): the
12 F3.4 figures (F8, approved 2026-11-09), their 12 provenance sidecars and
`manifests/output_inventory.csv`. All other 440 files are byte-identical to the archive.

**Limitations carried by the release** (see `reports/part8/final/`): F6 (no global MSAR
maximum; UNRATE K=3 inconclusive), MSAR optimiser sensitivity (B2), nominal p-values
without a predeclared multiple-testing family, degenerate STAR tests, sample- and
window-dependent rankings, the C16 audit sensitivity, and the M2SL diagnostic-panel overlap
in F3.4 (presentation).
