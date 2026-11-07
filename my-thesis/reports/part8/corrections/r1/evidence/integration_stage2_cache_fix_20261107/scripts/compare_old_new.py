"""Old (a21fdf2, README side effect) vs fixed outputs: every file identical, or differing only in
provenance (run ID / timestamps). Anything else is a scientific-output difference."""
import sys, json
from pathlib import Path
R = Path("/home/user/academia7/my-thesis"); sys.path.insert(0, str(R / "colab"))
import r1_integration_common as ic
S = Path(sys.argv[1])
PAIRS = {"stage2_legacy": (S/"rc/old_a21fdf2/assembly/legacy", S/"rc/fixed/work/assembly/legacy"),
         "stage2_corrected": (S/"rc/old_a21fdf2/assembly/corrected", S/"rc/fixed/work/assembly/corrected"),
         "stage2_corrected_raw": (S/"rc/old_a21fdf2/assembly/corrected_raw", S/"rc/fixed/work/assembly/corrected_raw"),
         "stage2_release": (S/"rc/old_a21fdf2/assembly/release", S/"rc/fixed/work/assembly/release"),
         "stage3_release": (S/"rh/work/release", S/"rc/fixed/work/release")}
RUNTIME_JSON = {"run_id", "started_utc", "created_utc", "finished_utc", "recorded_utc", "notes",
                "environment", "legacy_run_id", "corrected_run_id"}
def strip(o):
    if isinstance(o, dict): return {k: strip(v) for k, v in o.items() if k not in RUNTIME_JSON}
    if isinstance(o, list): return [strip(v) for v in o]
    return o
out = {}
for name, (old, new) in PAIRS.items():
    a, b = ic.tree_files(old), ic.tree_files(new)
    res = {"files_old": len(a), "files_new": len(b), "only_old": sorted(set(a) - set(b)),
           "only_new": sorted(set(b) - set(a)), "byte_identical": 0, "provenance_only": [],
           "DIFFERENT": []}
    for rel in sorted(set(a) & set(b)):
        if ic.sha256_file(a[rel]) == ic.sha256_file(b[rel]):
            res["byte_identical"] += 1; continue
        if rel.endswith((".csv", ".parquet", ".csv.gz")) and not rel.endswith(".csv.gz"):
            r = ic.table_cell_changes(a[rel], b[rel], rel)
            clean = r["alignable"] and not r["cells"] and not r["columns_added"] and not r["columns_removed"] \
                and not r.get("rows_added") and not r.get("rows_removed")
            (res["provenance_only"] if clean else res["DIFFERENT"]).append(rel if clean else {"path": rel, "cells": r["cells"][:5]})
        elif rel.endswith(".json"):
            same = strip(json.loads(a[rel].read_text())) == strip(json.loads(b[rel].read_text()))
            (res["provenance_only"] if same else res["DIFFERENT"]).append(rel)
        else:
            res["DIFFERENT"].append(rel)
    out[name] = res
causes_old = ic.read_rows(S/"rc/old_a21fdf2/assembly/reconcile_cell_causes.csv.gz")
causes_new = ic.read_rows(S/"rc/fixed/work/assembly/reconcile_cell_causes.csv.gz")
out["reconcile_cell_causes_identical"] = causes_old == causes_new
out["reconcile_cell_causes_rows"] = len(causes_new)
print(json.dumps({k: (v if not isinstance(v, dict) else {kk: (vv if not isinstance(vv, list) or len(vv) < 8 else f"{len(vv)} files") for kk, vv in v.items()}) for k, v in out.items()}, indent=1))
ic.write_json(S/"rc"/"old_vs_fixed.json", out)
