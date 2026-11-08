# Evidence: scientific-impact audit of the Part 8 integration dry run (8 November 2026)

This folder is the evidence for `../../part8_integration_scientific_audit.md`. Nothing here was estimated, and nothing here is published.

| Path | Content |
|---|---|
| `colab_export/` | The 45 files exported by Colab session `integration-20261108T052245Z-9bba8e`, plus its `export_manifest.json`. All 45 are verified against the manifest by sha256 and size. |
| `derived/` | Output of `../../integration_scientific_audit.py`: the export verification; decision-change categories; every 5% decision change with its p-values; the Wald rows; the UNRATE ARMA-vs-AR state regression; the UNRATE h=1 own-sample against common-sample RMSE; claim verdicts; the rebuilt integrated tables (claims reference `0573a8c` plus the exported changed cells). |
| `f48_check/` | F4.8_UNRATE rendered locally from the rebuilt integrated table with the pinned code. It is byte-identical to the Colab release; the sha256 values match `output_inventory.csv`. |

**To reproduce:**

```
python integration_scientific_audit.py colab_export <0573a8c output_corrected> <published output> derived
```
