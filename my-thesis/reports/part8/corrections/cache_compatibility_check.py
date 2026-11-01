"""Cache-compatibility evidence for the Part 8 corrections (read-only for output/).

Shows, on this machine, that the corrections do not change the fit-cache identity and
that fits cached by the approved pre-correction code are reused unchanged by the
corrected code:

1. `git diff` between the approved code commit and HEAD is empty for every fit-critical
   file (`core/cache._FIT_CRITICAL`) and for the three configuration files whose merged
   hash enters every cache key.
2. `code_hash()`, `config.hash` and the Colab `cache_identity` are recomputed for HEAD and
   compared with the published run (`output/manifests/run_manifest.json`) and with the
   identity `3413465b508bb844` of the Google Drive fit cache.
3. A real chain -- UNRATE, AR(6), 240-month window, h = 1, 3, 6, 12 -- over the origins
   2019-10 .. 2021-08 (which include the FAILED 2020-04 UNSTABLE_AR fit) is run by the
   **approved code** (`git worktree` of commit 46a53181) into a fresh cache, then by the
   **corrected code** against the same cache. The corrected run must be served entirely
   from the cache (no refit), with bit-identical raw forecasts; the only difference is
   that the failed fit's forecasts are masked from scoring by the pipeline (F1).

Run from `my-thesis/`:  python reports/part8/corrections/cache_compatibility_check.py
Writes `reports/part8/corrections/cache_compatibility_check.json`.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
THESIS = REPO / "my-thesis"
APPROVED = "46a53181e5e9d23c415f1c7fe11c0da93d9c3964"
DRIVE_IDENTITY = "3413465b508bb844"
DEST = Path(__file__).with_suffix(".json")

CHAIN_PROGRAM = r'''
import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, "src")
from thesis.core.cache import FitCache, code_hash
from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR, FROZEN_DIR
from thesis.data.store import load_bundle
from thesis.forecasting.rolling import DataIdentity, run_chain
from thesis.models.registry import ModelSpec

config = load_config(names=("baseline", "series_catalog", "thresholds"), config_dir=CONFIG_DIR)
bundle = load_bundle(FROZEN_DIR, config)
identity = DataIdentity(canonical_hash=bundle.csv_sha256,
                        source_manifest_hash=bundle.parent_source_hash,
                        code_hash=code_hash(), config_hash=config.hash)
frame = bundle.frame
level = frame[frame.series_id == "UNRATE"].set_index("date")["value"].astype(float)
level.index = pd.DatetimeIndex(level.index)
level = level.dropna()
# origins 2019-10 .. 2020-09 on a 240-month window: the series ends at the last target
# needed for h=12 from the last origin, starting 240 months before the first origin.
end = pd.Timestamp("2021-09-01")
start = pd.Timestamp("2019-10-01") - pd.DateOffset(months=239)
y = level[(level.index >= start) & (level.index <= end)]
cache = FitCache(__import__("pathlib").Path(sys.argv[1]))
chain = run_chain("UNRATE", y, ModelSpec(model="AR", order=6), (1, 3, 6, 12), 240, config,
                  frequency="M", transformation="percent", identity=identity, cache=cache)
f = chain.forecasts
out = {"code_hash": code_hash(), "config_hash": config.hash,
       "attempted": chain.attempted, "from_cache": chain.from_cache,
       "failed": chain.failed, "cache_hits": cache.hits, "cache_misses": cache.misses,
       "origins": sorted({str(d.date()) for d in pd.to_datetime(f.origin_date)}),
       "forecasts": [[str(pd.Timestamp(o).date()), int(h), float(v), s]
                     for o, h, v, s in zip(f.origin_date, f.horizon, f.forecast, f.status)]}
if len(sys.argv) > 2:
    from thesis.evaluation.scoring import mask_failed, scoreable
    masked = mask_failed(f)
    out["masked_failed_rows"] = int((masked.status == "failed").sum())
    out["masked_rows_scoreable"] = int(scoreable(masked).sum())
    out["failed_raw_forecasts_preserved"] = bool(
        np.allclose(masked.loc[masked.status == "failed", "failed_raw_forecast"],
                    f.loc[f.status == "failed", "forecast"]))
print(json.dumps(out))
'''


def sh(*args, cwd=REPO, check=True) -> str:
    return subprocess.run(list(args), cwd=cwd, check=check, text=True,
                          capture_output=True).stdout.strip()


def main() -> None:
    evidence: dict = {"approved_code_commit": APPROVED, "head": sh("git", "rev-parse", "HEAD")}
    sys.path.insert(0, str(THESIS / "code" / "src"))
    from thesis.core.cache import _FIT_CRITICAL  # noqa: E402

    critical = [f"my-thesis/code/src/thesis/{name}" for name in _FIT_CRITICAL]
    configs = [f"my-thesis/code/configs/{n}.yaml" for n in ("baseline", "series_catalog",
                                                            "thresholds")]
    evidence["fit_critical_files"] = critical
    evidence["fit_critical_diff_vs_approved"] = sh("git", "diff", "--stat", APPROVED, "HEAD",
                                                   "--", *critical) or "(empty)"
    evidence["config_diff_vs_approved"] = sh("git", "diff", "--stat", APPROVED, "HEAD",
                                             "--", *configs) or "(empty)"
    evidence["code_diff_vs_approved"] = sh("git", "diff", "--stat", APPROVED, "HEAD",
                                           "--", "my-thesis/code").splitlines()

    sys.path.insert(0, str(THESIS / "colab"))
    import thesis_colab  # noqa: E402
    evidence["cache_identity_head"] = thesis_colab.cache_identity(
        Path(sys.executable), THESIS / "code")
    evidence["cache_identity_drive"] = DRIVE_IDENTITY
    manifest = json.loads((THESIS / "output" / "manifests" / "run_manifest.json").read_text())
    evidence["published_config_hash"] = manifest.get("config_hash")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        worktree = tmp / "approved"
        sh("git", "worktree", "add", "--detach", str(worktree), APPROVED)
        try:
            cache_dir = tmp / "fits"
            old = json.loads(subprocess.run(
                [sys.executable, "-c", CHAIN_PROGRAM, str(cache_dir)],
                cwd=worktree / "my-thesis" / "code", check=True, text=True,
                capture_output=True).stdout.splitlines()[-1])
            new = json.loads(subprocess.run(
                [sys.executable, "-c", CHAIN_PROGRAM, str(cache_dir), "masked"],
                cwd=THESIS / "code", check=True, text=True,
                capture_output=True).stdout.splitlines()[-1])
        finally:
            sh("git", "worktree", "remove", "--force", str(worktree))
    evidence["approved_code_run"] = {k: old[k] for k in old if k != "forecasts"}
    evidence["corrected_code_run"] = {k: new[k] for k in new if k != "forecasts"}
    evidence["code_hash_equal"] = old["code_hash"] == new["code_hash"]
    evidence["config_hash_equal"] = old["config_hash"] == new["config_hash"]
    evidence["all_fits_served_from_cache"] = (new["from_cache"] == new["attempted"]
                                              and new["cache_misses"] == 0)
    evidence["raw_forecasts_bit_identical"] = old["forecasts"] == new["forecasts"]
    evidence["identity_matches_drive"] = evidence["cache_identity_head"] == DRIVE_IDENTITY
    evidence["failed_fits_in_chain"] = sorted({o for o, _, _, s in new["forecasts"]
                                               if s == "failed"})
    DEST.write_text(json.dumps(evidence, indent=2))
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
