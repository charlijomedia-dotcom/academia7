"""F4 preview: Zivot-Andrews on UNRATE and FEDFUNDS levels (read-only, not a thesis output).

Applies the corrected stationarity code path (decide_transformation ->
confirm_on_full_sample -> report_zivot_andrews) to the frozen canonical CSV with the
approved configuration, and shows that the baseline transformation is unchanged. The
authoritative T2.2 rows are produced by the approved targeted regeneration, not here.

Run from `my-thesis/`: python reports/part8/corrections/f4_zivot_andrews_preview.py
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code" / "src"))
from thesis.core.config import load_config  # noqa: E402
from thesis.core.paths import CONFIG_DIR  # noqa: E402
from thesis.diagnostics.decision_rule import (confirm_on_full_sample,  # noqa: E402
                                              decide_transformation, report_zivot_andrews)

config = load_config(names=("baseline", "series_catalog", "thresholds"), config_dir=CONFIG_DIR)
frame = pd.read_csv(ROOT / "data" / "frozen" / "thesis_input_2026-10-05.csv", parse_dates=["date"])
published = pd.read_csv(ROOT / "output" / "diagnostics" / "T2.2_transformation_decisions.csv")
rows = []
for series in ("UNRATE", "FEDFUNDS"):
    level = frame[frame.series_id == series].set_index("date")["value"].astype(float).dropna()
    level.name = series
    initial = level.iloc[:240]
    decision = decide_transformation(series, initial, "M", config)
    decision = confirm_on_full_sample(decision, level, "M", config)
    report_zivot_andrews(decision, initial, level, "M", config)
    row = decision.to_row()
    row["published_baseline_transformation"] = published.set_index("series_id").loc[
        series, "baseline_transformation"]
    row["decision_unchanged"] = row["published_baseline_transformation"] == row["baseline_transformation"]
    row["initial_window"] = f"{initial.index[0]:%Y-%m} to {initial.index[-1]:%Y-%m}"
    row["full_sample"] = f"{level.index[0]:%Y-%m} to {level.index[-1]:%Y-%m}"
    rows.append(row)
out = pd.DataFrame(rows)
out.to_csv(Path(__file__).with_suffix(".csv"), index=False)
print(out.T.to_string())
