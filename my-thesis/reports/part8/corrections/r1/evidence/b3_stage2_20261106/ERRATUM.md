# Erratum

`T3.4_unrate_mcs_reference_vs_candidate.csv` (revision 1 of `b3_stage2_analysis.py`) merged the
reference and candidate T3.4 rows on (horizon, loss, model) without `confidence_level`: a
many-to-many join (128 rows instead of 64). It is kept unchanged here as the superseded
extract. Superseded by `../b1_staged_20261106/stage2_rev2/T3.4_unrate_mcs_reference_vs_candidate.csv`
(revision 2: keyed one-to-one merge with unique-key assertions). The cell-level comparison,
`decision_flips.csv` and `changed_cells_keyed.csv.gz` were positional and are reproduced
byte for byte by revision 2.
