"""LOCAL PARTIAL REHEARSAL with the fixed code, through the real stage_aggregate (10 of 17 chains)."""
import sys, json, shutil, time
from pathlib import Path
R = Path("/home/user/academia7/my-thesis"); sys.path.insert(0, str(R / "colab"))
import r1_render_guard as rg; rg.pin_default_rc()
S = Path(sys.argv[1]); W = S / "rc" / "fixed" / "work"
import r1_part8_integration as drv, r1_integration_common as ic, r1_tierb as tb
tb.use_scientific_code(S / "pinned" / "my-thesis" / "code")
import r1_tierb_aggregate as agg, r1_integration_dependents as dep, r1_integration_validate as val, r1_integration_claims as cl
t0 = time.time(); log = lambda *a: print(f"[{time.time()-t0:6.0f}s]", *a, flush=True)
certs = {}
for f in sorted((R / ic.REL["certificate_manifest"]).parent.glob("COMPLETE-*.json")):
    c = json.loads(f.read_text()); certs[c["batch"]] = c
# Drive-dependent calls replaced by local equivalents (the rest is the production code path)
agg.discover = lambda root: certs
drv.check_certificates = lambda drive, manifest: {"skipped": "local rehearsal"}
def local_merge(drive_root, tier_a_archive, merged_fits):
    if merged_fits.exists() and any(merged_fits.rglob("*.json")):
        raise tb.TierBError(f"{merged_fits} is not empty")
    report = {"tier_a": tb.restore_tier_a(tier_a_archive, merged_fits)}
    src = S / "rh" / "merged" / "fits"
    for f in sorted(src.glob("*/*.json")):
        t = merged_fits / f.relative_to(src); t.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(f, t)
    report["payloads"] = len(tb.payload_files(merged_fits))
    return report
agg.merge = local_merge
if W.exists(): shutil.rmtree(W)
W.mkdir(parents=True)
for name in ("base", "references"):
    shutil.copytree(S / "rh" / "work" / name, W / name)
args = drv.parse(["--repo", "/home/user/academia7", "--code-dir", str(S / "pinned" / "my-thesis" / "code"),
                  "--drive-root", str(S / "rc" / "nodrive"), "--cache-root", str(S / "supp"),
                  "--tier-a-archive", str(S / "rh" / "tier_a" / "refit_cache_20261103T063749Z.tar.gz"),
                  "--orch-commit", "rehearsal", "--work", str(W)])
p = drv.paths(args)
approved = sorted(list(tb.TIER_A_CHAINS) + ["T4.1:FEDFUNDS|MSAR", "T4.8:UNRATE|180:MSAR"])
rec = drv.stage_aggregate(args, p, tasks=approved)
log("aggregate", json.dumps({"run_id": rec["run_id"], "cache_integrity": rec["cache_integrity"],
                              "estimations": rec["estimations_performed"]}, default=str))
r = dep.run(p, rec["run_id"], tasks=approved)
log("dependents", json.dumps({"cache_integrity": r["cache_integrity"], "fit_records_replaced": r["fit_records_replaced"]}, default=str))
r = val.run(p, certificates=certs); log("validate", json.dumps(r))
r = cl.run(p); log("claims", json.dumps(r, default=str))
log("done")
