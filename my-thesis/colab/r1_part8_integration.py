#!/usr/bin/env python3
"""Part 8 final integration: NON-PUBLISHING dry run (stages 0-5).

    python r1_part8_integration.py --repo <orchestration checkout> --code-dir <pinned code>
        --drive-root <Drive thesis root> --cache-root <restored original cache, holds fits/>
        --tier-a-archive <Tier A refit-cache archive> --orch-commit <sha> --work <empty dir>
        [--protect NAME=PATH ...] [--stage all|preflight|base|aggregate|dependents|validate|claims]

Integration order (each stage reads only the previous stage's output; nothing earlier is
ever written):

  0 preflight   pins, data and config hashes, rendering, certificates (sha256 against the
                committed manifest and the aggregator's own checks), original cache digest,
                Tier A archive, reference releases; listing of every protected input
  1 base        published output + the approved B1-staged overlay, every file verified
  2 aggregate   Tier A + certified Tier B payloads merged; the pinned R1 workflow, legacy
                then corrected (authorised corrections only: F8 off), estimation refused;
                chain-aware reconciliation; assembly; the aggregator's gates and status
  3 dependents  outputs the workflow does not rebuild: fit records, T4.7 registry and
                counts, F4.8, inventory and file comparison (`r1_integration_dependents`)
  4 validate    acceptance criteria A1-A15, cell-level change sets, attribution of every
                changed scientific cell (`r1_integration_validate`)
  5 claims      claim and jury-resolution reassessment (`r1_integration_claims`)

There is NO publication code: nothing is committed, pushed or written outside --work. The
run refuses if CONFIRM_PUBLISH is set. Exit status: 0 accepted (nothing to review beyond
reported sensitivity), 4 accepted and REVIEW REQUIRED, 1 refused (a check failed; every
failure is listed in dryrun_report/acceptance.json or dryrun_report/failure.json).
"""

from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
import traceback
from contextlib import ExitStack
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r1_render_guard as render_guard  # noqa: E402
import r1_integration_common as ic  # noqa: E402

STAGES = ("preflight", "base", "aggregate", "dependents", "validate", "claims")
STAGED_METADATA = {"README.md", "STAGED_FILES.csv", "COUNTER_PROVENANCE_forecast_origin_audit.csv"}


# -- helpers -------------------------------------------------------------------------------

def git(repo: Path, *args: str, binary: bool = False):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                            text=not binary, check=False)
    if result.returncode != 0:
        raise ic.IntegrationError(f"git {' '.join(args)} failed: {result.stderr}")
    return result.stdout if binary else result.stdout.strip()


def git_head(path: Path) -> str:
    return git(path, "rev-parse", "HEAD")


def git_clean(path: Path) -> bool:
    return git(path, "status", "--porcelain", "--untracked-files=all") == ""


def extract_release(repo: Path, commit: str, member: str, target: Path, work: Path) -> dict:
    """`git archive <commit> <member>` into target (regular files only; no escaping paths)."""
    ic.inside(work, target)
    if target.exists():
        shutil.rmtree(target)
    full = git(repo, "rev-parse", f"{commit}^{{commit}}")
    data = git(repo, "archive", "--format=tar", full, member, binary=True)
    count = 0
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        for entry in archive.getmembers():
            if entry.isdir():
                continue
            if not entry.isfile() or entry.name.startswith("/") or ".." in Path(entry.name).parts:
                raise ic.IntegrationError(f"unsafe member in {commit}:{entry.name}")
            relative = Path(entry.name).relative_to(member)
            destination = ic.inside(work, target / relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(archive.extractfile(entry).read())
            count += 1
    if count == 0:
        raise ic.IntegrationError(f"{commit}:{member} is empty or missing")
    listing = ic.tree_listing(target)
    return {"commit": full, "member": member, "files": count,
            "digest": ic.listing_digest(listing)}


def stage_record(work: Path, stage: str) -> Path:
    return work / "stages" / f"{stage}.json"


def require_stage(work: Path, stage: str) -> dict:
    path = stage_record(work, stage)
    if not path.is_file():
        raise ic.IntegrationError(f"stage {stage!r} has not completed in {work}")
    return json.loads(path.read_text())


def finish_stage(work: Path, stage: str, record: dict) -> dict:
    record = {"stage": stage, "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              **record}
    ic.write_json(ic.inside(work, stage_record(work, stage)), record)
    return record


def paths(args) -> dict:
    repo = Path(args.repo).resolve()
    thesis = repo / "my-thesis"
    code = Path(args.code_dir).resolve()
    return {"repo": repo, "thesis": thesis, "code": code,
            "pinned_thesis": code.parent, "published": code.parent / "output",
            "staged": thesis / ic.REL["staged_overlay"],
            "certificate_manifest": thesis / ic.REL["certificate_manifest"],
            "b2_by_origin": thesis / ic.REL["b2_by_origin"],
            "classification": thesis / ic.REL["chain_classification"],
            "claim_matrix": thesis / ic.REL["claim_matrix"],
            "jury_registry": thesis / ic.REL["jury_registry"],
            "reports": thesis / ic.REL["reports"],
            "drive": Path(args.drive_root), "cache_root": Path(args.cache_root).resolve(),
            "tier_a_archive": Path(args.tier_a_archive),
            "work": Path(args.work).resolve()}


def protected_paths(p: dict, extra: dict[str, str]) -> dict[str, Path]:
    """Every input the dry run must leave unchanged (hashed before and after)."""
    import r1_tierb as tb
    protected = {
        "published_output": p["published"],
        "pinned_approved_specs": p["pinned_thesis"] / "approved-specs",
        "repo_output": p["thesis"] / "output",
        "repo_output_staging": p["thesis"] / "output_staging",
        "repo_approved_specs": p["thesis"] / "approved-specs",
        "repo_source_materials": p["thesis"] / "source-materials",
        "certificates_and_evidence": p["thesis"] / "reports" / "part8" / "corrections" / "r1"
                                     / "evidence",
        "original_cache_local": p["cache_root"] / "fits",
        "tier_a_archive": p["tier_a_archive"],
        "drive_tier_b_batches": Path(p["drive"]) / "baseline" / "r1_tierb_batches",
    }
    for batch in tb.BATCHES:
        protected[f"drive_{batch}_certificates"] = tb.batch_root(p["drive"], batch) / "certificates"
    for name, path in extra.items():
        protected[f"extra_{name}"] = Path(path)
    return protected


# -- stage 0: preflight ----------------------------------------------------------------------

def certificate_files(drive: Path) -> dict[str, Path]:
    """Each batch's latest certificate FILE (the aggregator reads the same one)."""
    import r1_tierb as tb
    out = {}
    for batch in tb.BATCHES:
        folder = tb.batch_root(drive, batch) / "certificates"
        found = sorted(folder.glob("COMPLETE-*.json")) if folder.exists() else []
        if not found:
            raise ic.IntegrationError(f"{batch}: no certificate on Drive")
        out[batch] = found[-1]
    return out


def check_certificates(drive: Path, manifest_csv: Path) -> dict:
    manifest = {r["batch"]: r for r in ic.read_rows(manifest_csv)}
    out, problems = {}, []
    for batch, path in certificate_files(drive).items():
        expected = manifest.get(batch)
        digest = ic.sha256_file(path)
        if expected is None:
            problems.append(f"{batch}: not in the certificate manifest")
        elif path.name != expected["file"] or digest != expected["sha256"]:
            problems.append(f"{batch}: latest certificate {path.name} ({digest[:12]}) is not "
                            f"the reviewed {expected['file']} ({expected['sha256'][:12]})")
        out[batch] = {"file": path.name, "sha256": digest}
    if problems:
        raise ic.IntegrationError("; ".join(problems))
    return out


def stage_preflight(args, p: dict) -> dict:
    import r1_tierb as tb
    import r1_tierb_aggregate as agg
    work = p["work"]
    if os.environ.get("CONFIRM_PUBLISH", "").strip().lower() not in ("", "0", "false", "no"):
        raise ic.IntegrationError("CONFIRM_PUBLISH is set: this is a non-publishing dry run")
    record: dict = {"orchestration_commit": args.orch_commit, "scientific_commit": ic.SCIENTIFIC_PIN,
                    "decisions": ic.DECISIONS, "correction_flags": ic.CORRECTION_FLAGS}
    # code: the pinned scientific checkout, clean; the orchestration checkout, clean
    if git_head(p["code"]) != ic.SCIENTIFIC_PIN or not git_clean(p["code"]):
        raise ic.IntegrationError("the scientific checkout is not a clean checkout of the pin")
    if git_head(p["repo"]) != args.orch_commit or not git_clean(p["repo"]):
        raise ic.IntegrationError("the orchestration checkout is not a clean checkout of "
                                  f"{args.orch_commit}")
    git(p["repo"], "merge-base", "--is-ancestor", ic.SCIENTIFIC_PIN, args.orch_commit)
    if p["published"].resolve() != (p["code"].parent / "output").resolve():
        raise ic.IntegrationError("the published tree must be the pinned checkout's output/")
    # data, configuration, rendering
    frozen = p["pinned_thesis"] / ic.FROZEN_DATA_RELATIVE
    if ic.sha256_file(frozen) != ic.FROZEN_DATA_SHA256:
        raise ic.IntegrationError("frozen data hash differs")
    tb.use_scientific_code(p["code"])
    from thesis.core.config import load_config
    from thesis.core.paths import CONFIG_DIR
    config = load_config(names=("baseline", "series_catalog", "thresholds"), config_dir=CONFIG_DIR)
    if config.hash != ic.CONFIG_HASH:
        raise ic.IntegrationError(f"config hash {config.hash} != {ic.CONFIG_HASH}")
    record["rendering"] = render_guard.check_default_rendering(
        render_guard.expected_version_from(p["published"]))
    # certificates: the reviewed files, and the aggregator's own consistency checks
    record["certificates"] = check_certificates(p["drive"], p["certificate_manifest"])
    certificates = agg.discover(p["drive"])
    record["certificate_status"] = {b: c["scientific_status"] for b, c in certificates.items()}
    # original cache and Tier A archive
    count, digest = ic.payload_digest(p["cache_root"] / "fits")
    if count != ic.ORIGINAL_CACHE_PAYLOADS or digest != ic.ORIGINAL_CACHE_DIGEST:
        raise ic.IntegrationError(f"original cache: {count} payloads, digest {digest[:12]}")
    record["original_cache"] = {"payloads": count, "digest": digest}
    tier_a_sha = ic.sha256_file(p["tier_a_archive"])
    if tier_a_sha != tb.TIER_A_ARCHIVE_SHA256:
        raise ic.IntegrationError("Tier A archive sha256 differs")
    record["tier_a_archive_sha256"] = tier_a_sha
    # reference releases, from git objects
    refs = work / "references"
    record["references"] = {
        "tier_a_release": extract_release(p["repo"], ic.TIER_A_RELEASE_COMMIT,
                                          "my-thesis/output_corrected", refs / "tier_a_release", work),
        "claims_reference": extract_release(p["repo"], ic.CLAIMS_REFERENCE_COMMIT,
                                            "my-thesis/output_corrected", refs / "claims_reference",
                                            work)}
    for name in ("staged", "certificate_manifest", "b2_by_origin", "classification",
                 "claim_matrix", "jury_registry"):
        if not p[name].exists():
            raise ic.IntegrationError(f"missing input {name}: {p[name]}")
    record["protected_before"] = ic.protected_listing(protected_paths(p, args.protect))
    return record


# -- stage 1: base tree ---------------------------------------------------------------------

def stage_base(args, p: dict) -> dict:
    """published output + the B1 staged overlay; every one of the 461 files verified."""
    import gzip
    work = p["work"]
    base = ic.inside(work, work / "base")
    if base.exists():
        shutil.rmtree(base)
    published = ic.tree_files(p["published"])
    published_sha = {k: ic.sha256_file(v) for k, v in published.items()}
    rows = ic.read_rows(p["staged"] / "STAGED_FILES.csv")
    staged = {r["path"]: r for r in rows}
    present = {k for k in ic.tree_files(p["staged"])} - STAGED_METADATA
    stored = {r["stored_as"] for r in rows}
    if present != stored:
        raise ic.IntegrationError(f"overlay files differ from STAGED_FILES.csv: "
                                  f"extra {sorted(present - stored)[:5]}, "
                                  f"missing {sorted(stored - present)[:5]}")
    shutil.copytree(p["published"], base)
    manifest = []
    for relative, row in sorted(staged.items()):
        if relative not in published:
            raise ic.IntegrationError(f"overlay adds a file the published tree lacks: {relative}")
        if published_sha[relative] != row["published_sha256"]:
            raise ic.IntegrationError(f"{relative}: published sha256 is not the one the overlay "
                                      "supersedes")
        source = p["staged"] / row["stored_as"]
        data = (gzip.decompress(source.read_bytes()) if row["stored_as"].endswith(".gz")
                and not relative.endswith(".gz") else source.read_bytes())
        target = ic.inside(work, base / relative)
        target.write_bytes(data)
        if ic.sha256_file(target) != row["staged_sha256"]:
            raise ic.IntegrationError(f"{relative}: staged file fails its sha256")
    for relative in sorted(published):
        digest = ic.sha256_file(base / relative)
        source = "b1_staged" if relative in staged else "published"
        expected = staged[relative]["staged_sha256"] if relative in staged else published_sha[relative]
        if digest != expected:
            raise ic.IntegrationError(f"{relative}: base file fails verification")
        manifest.append({"path": relative, "source": source, "sha256": digest,
                         "published_sha256": published_sha[relative]})
    if set(ic.tree_files(base)) != set(published):
        raise ic.IntegrationError("the base tree does not have exactly the published file set")
    ic.write_rows(work / "base_manifest.csv", manifest)
    return {"files": len(manifest), "b1_staged": sum(r["source"] == "b1_staged" for r in manifest),
            "published": sum(r["source"] == "published" for r in manifest),
            "base_digest": ic.listing_digest({r["path"]: r["sha256"] for r in manifest}),
            "counter_provenance": ic.read_rows(p["staged"] / "COUNTER_PROVENANCE_forecast_origin_audit.csv")}


# -- stage 2: aggregation and assembly -------------------------------------------------------

def reconcile_chain_aware(original: Path, legacy: Path, corrected: Path, files: list[str]):
    """The pinned R1 reconciliation, extended to re-estimated chains that do not reproduce.

    The pinned `workflow.reconcile` restores the base text in every cell where the legacy
    run (corrections off) and the corrected run agree, assuming that the legacy run
    reproduces the base. With re-estimated chains that do NOT reproduce the original (B2,
    approved for candidate integration under D1), that assumption fails: it would restore
    the superseded published value, e.g. FEDFUNDS T4.1 MSAR n_failed 52 instead of 49.
    Here a cell is restored only where the legacy value also reproduces the base (equal
    within the pinned floating-point tolerance); otherwise the re-estimated value is kept
    and recorded with its cause. Returns (per-file account, per-cell cause records).
    """
    from thesis.correction import workflow as wf
    account, causes = [], []
    for relative in files:
        if not relative.endswith(".csv"):
            continue
        o_path, l_path, c_path = original / relative, legacy / relative, corrected / relative
        if not all(x.exists() for x in (o_path, l_path, c_path)):
            continue
        o, l, c = (ic.read_table(x) for x in (o_path, l_path, c_path))
        if len(o) != len(l):
            account.append({"path": relative, "reconciled": False,
                            "reason": "legacy run does not align with the base"})
            continue
        mapping = wf._match_rows(l, c, relative)
        keys = [k for k in ic.KEY_COLUMNS if k in c.columns]
        restored = kept_chain = changed = 0
        for column in c.columns:
            if column in wf._SKIP or column not in l.columns or column not in o.columns:
                continue
            for ci, li in mapping.items():
                cv, lv, ov = c.at[ci, column], l.at[li, column], o.at[li, column]
                legacy_reproduces = ic.same_cell(lv, ov)
                if wf._same_value(cv, lv):
                    if legacy_reproduces:
                        if cv != ov:
                            c.at[ci, column] = ov
                            restored += 1
                        continue
                    cause = "reestimated_chain"
                    kept_chain += 1
                else:
                    cause = "correction" if legacy_reproduces else "correction+reestimated_chain"
                    changed += 1
                if not ic.same_cell(c.at[ci, column], ov):
                    causes.append({"path": relative, "row": ci, "column": column, "cause": cause,
                                   "base": ov, "legacy": lv, "final": c.at[ci, column],
                                   "decision_like": ic.is_decision_column(column),
                                   **{f"key_{k}": c.at[ci, k] for k in keys}})
        new_rows = [i for i in range(len(c)) if i not in mapping]
        wf._match_integer_format(c, l, new_rows)
        for i in new_rows:
            causes.append({"path": relative, "row": i, "column": "*", "cause": "correction_new_row",
                           "decision_like": False, **{f"key_{k}": c.at[i, k] for k in keys}})
        c.to_csv(c_path, index=False)
        account.append({"path": relative, "reconciled": True, "cells_restored_to_base": restored,
                        "cells_kept_from_reestimated_chains": kept_chain,
                        "cells_changed_by_corrections": changed, "rows_new": len(new_rows)})
    return account, causes


def assemble(base: Path, cache_root: Path, refit_root: Path, out: Path, approved: list[str],
             work: Path) -> dict:
    """The pinned workflow (legacy, corrected), chain-aware reconciliation, pinned assembly."""
    import r1_tierb as tb
    from thesis.correction import flags as correction_flags
    from thesis.correction import workflow as wf
    from thesis.correction.compare import compare_trees
    for name in ("legacy", "corrected", "corrected_raw", "release"):
        ic.inside(work, out / name)
        if (out / name).exists():
            raise ic.IntegrationError(f"{out / name} exists; use a new work folder")
    common = dict(cache_root=cache_root, approved_estimation=approved, refit_cache=refit_root)
    with ExitStack() as stack:
        stack.enter_context(tb.no_estimation_allowed())
        # read-only live replay: no README, no folder creation, no payload write (both passes)
        stack.enter_context(ic.readonly_refit_replay())
        stack.enter_context(correction_flags.configured(**ic.CORRECTION_FLAGS))
        legacy = wf.run(base, out / "legacy", legacy=True, **common)
        files = [f for f in legacy["regenerated_files"] if f not in wf.WORKFLOW_FILES]
        compare_trees(base, out / "legacy", files=files).to_csv(
            out / "legacy" / "r1_comparison.csv", index=False)
        corrected = wf.run(base, out / "corrected", legacy=False, **common)
    if corrected["flags"] != ic.CORRECTION_FLAGS:
        raise ic.IntegrationError(f"corrections applied {corrected['flags']} are not the "
                                  f"authorised set {ic.CORRECTION_FLAGS}")
    files = [f for f in corrected["regenerated_files"] if f not in wf.WORKFLOW_FILES]
    for relative in files:                  # the unreconciled corrected run, kept for audit
        target = out / "corrected_raw" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(out / "corrected" / relative, target)
    account, causes = reconcile_chain_aware(base, out / "legacy", out / "corrected", files)
    ic.write_rows(out / "corrected" / "r1_reconciliation.csv", account)
    ic.write_rows(out / "reconcile_cell_causes.csv.gz", causes)
    compare_trees(base, out / "corrected", files=files).to_csv(
        out / "corrected" / "r1_comparison.csv", index=False)
    wf.assemble(base, out / "corrected", out / "release", corrected)
    return {"legacy_run_id": legacy["run_id"], "corrected_run_id": corrected["run_id"],
            "regenerated_files": len(files),
            "estimations_performed": {"legacy": legacy.get("estimations_performed"),
                                      "corrected": corrected.get("estimations_performed")},
            "flags": corrected["flags"], "reconciliation": account,
            "cells_with_cause": len(causes)}


def t42_tolerance(gate_report: dict, tier_a_release: Path, release: Path) -> None:
    """The T4.2 gate under the pinned comparison convention.

    The aggregator requires T4.2 to be byte-for-byte identical to the Tier A release. The
    Tier A release was computed on another machine; cells that the corrections recompute can
    differ there in the last printed digit (summation order). The pinned R1 comparison calls
    such files "equal_within_fp_tolerance" (every non-numeric cell identical, numbers within
    1e-9 relative) and reports them separately, never as identical. A T4.2 file in that class
    is accepted and REPORTED with every differing cell; any larger difference still refuses.
    """
    from thesis.correction.compare import compare_file
    kept, report = [], {}
    for problem in gate_report["problems"]:
        name = problem.split(" ", 1)[0]
        if not (problem.endswith("differs from the Tier A release") and name.startswith("T4.2_")):
            kept.append(problem)
            continue
        result = compare_file(tier_a_release / "robustness" / name, release / "robustness" / name)
        cells = ic.table_cell_changes(tier_a_release / "robustness" / name,
                                      release / "robustness" / name, f"robustness/{name}")
        exact = []
        a = ic.read_table(tier_a_release / "robustness" / name)
        b = ic.read_table(release / "robustness" / name)
        for column in result.get("columns_differing") or []:
            for i in range(min(len(a), len(b))):
                if a.at[i, column] != b.at[i, column]:
                    exact.append({"row": i, "column": column, "tier_a": a.at[i, column],
                                  "dry_run": b.at[i, column]})
        if result.get("within_tolerance") and cells["alignable"] and not cells["cells"]:
            report[name] = {"status": "equal_within_fp_tolerance",
                            "max_relative_difference": result.get("max_relative_difference"),
                            "cells_differing_in_print": exact}
        else:
            kept.append(problem)
            report[name] = {"status": "changed", "cells": exact[:50]}
    gate_report["problems"] = kept
    gate_report["t42_vs_tier_a_release"] = report or "identical"


INTEGRITY = "cache_integrity"


def record_cache_listings(work: Path, merged_fits: Path, cache_fits: Path) -> dict:
    """File-level listings of both caches right after merging (strict reference)."""
    folder = ic.inside(work, work / "dryrun_report" / INTEGRITY)
    merged, original = ic.tree_listing(merged_fits), ic.tree_listing(cache_fits)
    ic.save_listing(folder / "merged_refit_after_merge.csv", merged)
    ic.save_listing(folder / "original_cache_before_assembly.csv.gz", original)
    return {"merged": merged, "original": original,
            "merged_files": len(merged), "merged_digest": ic.listing_digest(merged),
            "original_files": len(original), "original_digest": ic.listing_digest(original)}


def check_cache_listings(work: Path, merged_fits: Path, cache_fits: Path, when: str) -> dict:
    """Strict: both caches hold exactly the files recorded after merging, byte for byte."""
    folder = work / "dryrun_report" / INTEGRITY
    tag = when.replace(" ", "_")
    return {"merged_refit": ic.require_unchanged(
                "the merged refit cache", merged_fits,
                ic.load_listing(folder / "merged_refit_after_merge.csv"), when,
                folder / f"merged_refit_diff_{tag}.json"),
            "original_cache": ic.require_unchanged(
                "the original fit cache", cache_fits,
                ic.load_listing(folder / "original_cache_before_assembly.csv.gz"), when,
                folder / f"original_cache_diff_{tag}.json")}


def stage_aggregate(args, p: dict, tasks: list[str] | None = None) -> dict:
    """Stage 2. `tasks` defaults to the 17 re-estimated chains (a subset only in rehearsals,
    where the aggregator's gates then refuse the incomplete chain set)."""
    import r1_tierb as tb
    import r1_tierb_aggregate as agg
    work = p["work"]
    base = work / "base"
    certificates = agg.discover(p["drive"])
    check_certificates(p["drive"], p["certificate_manifest"])
    merged_root = ic.inside(work, work / "merged_refit")
    merge_report = agg.merge(p["drive"], p["tier_a_archive"], merged_root / "fits")
    listings = record_cache_listings(work, merged_root / "fits", p["cache_root"] / "fits")
    jobs, identity, config = tb.build_jobs(base, p["code"])
    approved = sorted(tasks or (list(tb.TIER_A_CHAINS) + list(tb.TIER_B_CHAINS)))
    if tasks is None:
        walks = agg.walk_all(jobs, identity, config, merged_root / "fits")
    else:
        walks = {t: {k: w[k] for k in ("planned", "completed", "statuses")}
                 for t in approved for w in [tb.walk_chain(jobs[t], merged_root / "fits",
                                                           identity, config)]}
    exits = assemble(base, p["cache_root"], merged_root, work / "assembly", approved, work)
    integrity = {"after_merge": {k: v for k, v in listings.items() if k not in ("merged", "original")},
                 "after_assembly": check_cache_listings(work, merged_root / "fits",
                                                        p["cache_root"] / "fits", "during assembly")}
    gate_report = agg.gates(work / "assembly", work / "references" / "tier_a_release",
                            p["classification"])
    t42_tolerance(gate_report, work / "references" / "tier_a_release", work / "assembly" / "release")
    status = agg.aggregation_status(certificates, gate_report)
    plan = {"dry_run": True, "publish": "NOT PERFORMED: no publication code exists in this run",
            "release": str(work / "assembly" / "release"), "run_id": exits["corrected_run_id"],
            "certificates": {b: c["created_utc"] for b, c in certificates.items()},
            **status,
            "scientific_status_by_batch": {b: c["scientific_status"]
                                           for b, c in sorted(certificates.items())},
            "certificate_chains": {b: c["chains"] for b, c in sorted(certificates.items())},
            "merge": {k: v for k, v in merge_report.items() if k != "batches"},
            "walks": walks, "assembly": exits, "gates": gate_report,
            "cache_integrity": integrity, "decisions": ic.DECISIONS}
    ic.write_json(ic.inside(work, work / "dryrun_report" / "aggregation_plan.json"), plan)
    return {"run_id": exits["corrected_run_id"], "aggregation_status": status["aggregation_status"],
            "gate_problems": gate_report["problems"], "walks": walks,
            "estimations_performed": exits["estimations_performed"],
            "cache_integrity": integrity}


# -- driver ----------------------------------------------------------------------------------

def run_stage(stage: str, args, p: dict) -> dict:
    work = p["work"]
    if stage != "preflight":
        require_stage(work, STAGES[STAGES.index(stage) - 1])
    if stage == "preflight":
        record = stage_preflight(args, p)
    elif stage == "base":
        record = stage_base(args, p)
    elif stage == "aggregate":
        record = stage_aggregate(args, p)
    elif stage == "dependents":
        import r1_integration_dependents as dep
        record = dep.run(p, require_stage(work, "aggregate")["run_id"])
    elif stage == "validate":
        import r1_integration_validate as val
        record = val.run(p, protected_paths(p, args.protect))
    else:
        import r1_integration_claims as claims
        record = claims.run(p)
    return finish_stage(work, stage, record)


def finalize(args, p: dict) -> dict:
    """acceptance.json: stage-4 criteria + A2 (protected inputs, after everything) + A14."""
    work = p["work"]
    stage4 = json.loads((work / "dryrun_report" / "acceptance_stage4.json").read_text())
    claims = require_stage(work, "claims")
    before = require_stage(work, "preflight")["protected_before"]
    after = ic.protected_listing(protected_paths(p, args.protect))
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    criteria = dict(stage4["criteria"])
    criteria["A2"] = {"pass": not changed, "detail": {"changed": changed, "after": after}}
    criteria["A14"] = {"pass": not claims["problems"],
                       "detail": {k: claims[k] for k in ("claims", "transitions", "jury_ids",
                                                         "jury_status", "report_lines_flagged",
                                                         "problems")}}
    order = sorted(criteria, key=lambda k: int(k[1:]))
    accepted = all(criteria[k]["pass"] for k in order)
    acceptance = {"dry_run": True, "published": False, "run_id": stage4["run_id"],
                  "orchestration_commit": args.orch_commit, "scientific_commit": ic.SCIENTIFIC_PIN,
                  "aggregation_status": stage4["aggregation_status"],
                  "scientific_approval": ic.APPROVAL_NOT_GRANTED, "decisions": ic.DECISIONS,
                  "accepted": accepted, "failed_criteria": [k for k in order if not criteria[k]["pass"]],
                  "criteria": {k: criteria[k] for k in order}}
    ic.write_json(ic.inside(work, work / "dryrun_report" / "acceptance.json"), acceptance)
    ic.write_json(work / "dryrun_report" / "protected_inputs_after.json", after)
    return acceptance


def outcome(work: Path) -> int:
    acceptance = json.loads((work / "dryrun_report" / "acceptance.json").read_text())
    if not acceptance["accepted"]:
        print("DRY_RUN_STATUS: REFUSED")
        return 1
    print("AGGREGATION_STATUS:", acceptance["aggregation_status"])
    print("SCIENTIFIC_APPROVAL:", ic.APPROVAL_NOT_GRANTED)
    review = acceptance["aggregation_status"] == "COMPUTATION_COMPLETE_REVIEW_REQUIRED"
    print("DRY_RUN_STATUS:", "ACCEPTED_FOR_REVIEW_REVIEW_REQUIRED" if review else "ACCEPTED_FOR_REVIEW")
    return 4 if review else 0


def parse(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True, help="orchestration checkout (contains my-thesis/)")
    ap.add_argument("--code-dir", required=True, help="pinned checkout's my-thesis/code")
    ap.add_argument("--drive-root", required=True)
    ap.add_argument("--cache-root", required=True, help="restored original cache (holds fits/)")
    ap.add_argument("--tier-a-archive", required=True)
    ap.add_argument("--orch-commit", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--protect", action="append", default=[],
                    help="NAME=PATH of a further input to keep unchanged (repeatable)")
    ap.add_argument("--stage", default="all", choices=("all",) + STAGES)
    args = ap.parse_args(argv)
    protect = {}
    for item in args.protect:
        name, _, path = item.partition("=")
        if not name or not path:
            ap.error(f"--protect expects NAME=PATH, got {item!r}")
        protect[name] = path
    args.protect = protect
    return args


def main(argv=None) -> int:
    render_guard.pin_default_rc()               # before anything imports matplotlib
    args = parse(argv)
    p = paths(args)
    work = p["work"]
    for name in ("published", "repo", "code"):
        if work == p[name] or p[name] in work.parents or work in p[name].parents:
            raise ic.IntegrationError(f"--work must be apart from {name}")
    if args.stage in ("all", "preflight"):
        if work.exists() and any(work.iterdir()):
            raise ic.IntegrationError(f"{work} is not empty: start a dry run in a new folder")
    work.mkdir(parents=True, exist_ok=True)
    stages = STAGES if args.stage == "all" else (args.stage,)
    current = None
    try:
        for stage in stages:
            current = stage
            print(f"== stage {stage}", flush=True)
            record = run_stage(stage, args, p)
            print(json.dumps({k: v for k, v in record.items()
                              if k not in ("protected_before", "counter_provenance", "walks",
                                           "references", "criteria")}, default=str)[:3000],
                  flush=True)
    except Exception as error:                  # every failure stops the run, recorded
        ic.write_json(work / "dryrun_report" / "failure.json",
                      {"stage": current, "error": f"{type(error).__name__}: {error}",
                       "traceback": traceback.format_exc()})
        print(f"STAGE {current} FAILED: {type(error).__name__}: {error}")
        print("DRY_RUN_STATUS: REFUSED")
        return 1
    if "claims" in stages:
        try:
            acceptance = finalize(args, p)
        except Exception as error:
            ic.write_json(work / "dryrun_report" / "failure.json",
                          {"stage": "finalize", "error": f"{type(error).__name__}: {error}",
                           "traceback": traceback.format_exc()})
            print("DRY_RUN_STATUS: REFUSED")
            return 1
        for key, value in acceptance["criteria"].items():
            print(f"  {key}: {'pass' if value['pass'] else 'FAIL'}")
        return outcome(work)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
