"""Reproduce the stage-2 cache change with the UNMODIFIED assembly code (commit a21fdf2)."""
import sys, json, shutil, tarfile, hashlib, time, csv
from pathlib import Path
R = Path(sys.argv[2]); sys.path.insert(0, str(R / "colab"))
import r1_render_guard as rg; rg.pin_default_rc()
S = Path(sys.argv[1]); W = S / "rc" / sys.argv[3]
import r1_part8_integration as drv, r1_integration_common as ic, r1_tierb as tb
tb.use_scientific_code(S / "pinned" / "my-thesis" / "code")
if W.exists(): shutil.rmtree(W)
W.mkdir(parents=True)
fits = W / "merged_refit" / "fits"
# merge exactly as agg.merge does: Tier A archive, then the B2 checkpoint payloads
tier_a = tb.restore_tier_a(S / "rh" / "tier_a" / "refit_cache_20261103T063749Z.tar.gz", fits)
src = S / "rh" / "merged" / "fits"
for f in sorted(src.glob("*/*.json")):
    t = fits / f.relative_to(src); t.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(f, t)
def listing(): return ic.tree_listing(fits)
L0 = listing()
# independent source inventory: Tier A archive members + B2 payloads (verified earlier against the B2 certificate)
expected = {}
with tarfile.open(S / "rh" / "tier_a" / "refit_cache_20261103T063749Z.tar.gz") as a:
    for m in a.getmembers():
        if m.isfile() and m.name.startswith("refit_cache/fits/"):
            expected[m.name[len("refit_cache/fits/"):]] = hashlib.sha256(a.extractfile(m).read()).hexdigest()
for f in src.glob("*/*.json"):
    expected[f.relative_to(src).as_posix()] = ic.sha256_file(f)
print("after merge:", len(L0), "files; equals source inventory:", L0 == expected, flush=True)
approved = sorted(list(tb.TIER_A_CHAINS) + ["T4.1:FEDFUNDS|MSAR", "T4.8:UNRATE|180:MSAR"])
t = time.time()
exits = drv.assemble(S / "rh" / "work" / "base", S / "supp", W / "merged_refit", W / "assembly", approved, W)
L1 = listing()
added = {k: L1[k] for k in L1.keys() - L0.keys()}
removed = {k: L0[k] for k in L0.keys() - L1.keys()}
modified = {k: (L0[k], L1[k]) for k in L0.keys() & L1.keys() if L0[k] != L1[k]}
payloads_identical = all(L1.get(k) == v for k, v in expected.items())
out = {"code": sys.argv[3], "assembly_minutes": round((time.time() - t) / 60, 1),
       "after_merge": {"files": len(L0), "digest": ic.listing_digest(L0)},
       "after_assembly": {"files": len(L1), "digest": ic.listing_digest(L1)},
       "added": added, "removed": removed, "modified": modified,
       "every_source_payload_byte_identical": payloads_identical,
       "json_payloads_after": sum(1 for k in L1 if k.endswith(".json")),
       "estimations_performed": exits["estimations_performed"], "flags": exits["flags"],
       "corrected_run_id": exits["corrected_run_id"]}
for name, path in (("added", fits / "README_R1_REFIT_CACHE.txt"),):
    if path.exists(): out["readme_text"] = path.read_text()
ic.write_json(W / "cache_diff.json", out)
ic.write_rows(W / "listing_after_merge.csv", [{"path": k, "sha256": v} for k, v in sorted(L0.items())])
ic.write_rows(W / "listing_after_assembly.csv", [{"path": k, "sha256": v} for k, v in sorted(L1.items())])
print(json.dumps({k: v for k, v in out.items() if k != "readme_text"}, indent=1))
