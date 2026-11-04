"""R1 Tier B orchestration: batches, checkpoints, chain walks, runtime budget, certificates.

Orchestration only. Every estimation, cache key, payload format and failure
classification comes from the PINNED scientific code (`8aaa4217536a...`, imported from its
own checkout via `use_scientific_code`); nothing here fits a model or changes how one is
fitted. The only object that touches estimation is `StoppableRefitCache`, a subclass of the
pinned `RefitCache` that writes exactly the pinned payload (same marker, same atomic
write) and can raise `GracefulStop` *between* origins: after an origin's payload is
committed, or before an origin would start that cannot finish within the runtime budget.

Layout on Google Drive (one namespace per batch; nothing shared is ever written):

    DRIVE_ROOT/baseline/r1_tierb_batches/<B>/
        checkpoints/<task-slug>/ckpt-<utc>-<session>-<seq>-<rand>/   committed, immutable
            payloads.tar.gz      payloads new since the parent checkpoint (read back, verified)
            manifest.json        task, session, parent, member sha256s, archive sha256,
                                 session_record (traceable even if the session was killed)
            COMMITTED            written last: JSON with the manifest and archive sha256
        a checkpoint folder without a valid COMMITTED marker is an interrupted write: ignored
        (the completion-marker protocol does not rely on directory renames)
        sessions/<utc>-<session>/                              started record, progress, summary, logs
        leases/<session>.json                                  one active session per batch
        certificates/COMPLETE-<utc>-<session>.json             every chain complete; carries
                                                               scientific_status, never approval
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tarfile
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable

# -- what Tier B is ----------------------------------------------------------------------

SCIENTIFIC_PIN = "8aaa4217536ab3cb942dd248dd19ece7838a8d60"
CACHE_IDENTITY = "3413465b508bb844"
ORIGINAL_PAYLOADS = 18964
MARKER = "r1_provenance"
MARKER_VALUE = "re-estimated"

TIER_A_RELEASE_COMMIT = "292227e0904bb9a857c76d633031c39fbd463eae"
TIER_A_EVIDENCE_COMMIT = "c5324b21557b81abb3c24964f84cecc68cc6348d"
TIER_A_ARCHIVE_RELATIVE = ("baseline/r1_tier_a_checkpoint/20261103T063749Z/"
                           "refit_cache_20261103T063749Z.tar.gz")
#: sha256 of the archive as found on Google Drive on 4 November 2026 (1,598,183 bytes).
TIER_A_ARCHIVE_SHA256 = "df73c29532a813ec0c413062d7c21aef7e660f6b3c556bd88d51b6f52d3361c2"
TIER_A_PAYLOADS = 5597
#: Tier A chain -> (planned origins, failed fits), from the Tier A validation evidence.
TIER_A_CHAINS = {
    "T4.1:UNRATE|AR": (703, 2), "T4.1:FEDFUNDS|AR": (626, 71),
    "T4.2:CPIAUCSL|AR(p=1)": (715, 0), "T4.2:CPIAUCSL|AR(p=3)": (715, 0),
    "T4.2:CPIAUCSL|AR(p=6)": (715, 0), "T4.2:CPIAUCSL|AR(p=12)": (715, 1),
    "T4.8:UNRATE|180:AR": (764, 1), "T4.8:UNRATE|300:AR": (644, 1),
}

#: Tier B task -> (planned origins, historical seconds per fit, original failed fits).
#: Seconds per fit are the original run's own wall times for these chains
#: (reports/part8/corrections/r1/tier_b_workload.csv).
TIER_B_CHAINS = {
    "T4.8:UNRATE|300:MSAR": (644, 99.92, 3),
    "T4.8:UNRATE|180:MSAR": (764, 59.01, 5),
    "T4.1:FEDFUNDS|MSAR": (626, 19.61, 52),
    "T4.8:UNRATE|180:ARMA": (764, 30.39, 22),
    "T4.1:UNRATE|ARMA": (703, 32.12, 7),
    "T4.8:UNRATE|300:ARMA": (644, 12.11, 13),
    "T4.1:FEDFUNDS|ARMA": (626, 0.30, 6),
    "T4.8:UNRATE|300:STAR": (644, 2.03, 0),
    "T4.1:FEDFUNDS|STAR": (626, 1.84, 0),
}

#: The partition you approved. Order inside a batch is the launch order (longest first).
BATCHES = {
    "B1": ("T4.8:UNRATE|300:MSAR",),
    "B2": ("T4.8:UNRATE|180:MSAR", "T4.1:FEDFUNDS|MSAR"),
    "B3": ("T4.8:UNRATE|180:ARMA", "T4.1:UNRATE|ARMA", "T4.8:UNRATE|300:ARMA",
           "T4.8:UNRATE|300:STAR", "T4.1:FEDFUNDS|STAR", "T4.1:FEDFUNDS|ARMA"),
}
DEFAULT_WORKERS = {"B1": 1, "B2": 2, "B3": 3}


class TierBError(RuntimeError):
    """Any inconsistency: the operation stops and nothing is assumed."""


class GracefulStop(Exception):
    """Raised between origins when the runtime budget (or a stop file) says to stop."""


def validate_partition() -> dict:
    """The three batches cover exactly the nine Tier B chains, once each."""
    tasks = [t for b in BATCHES.values() for t in b]
    if len(tasks) != len(set(tasks)) or set(tasks) != set(TIER_B_CHAINS):
        raise TierBError(f"batch partition is not the nine Tier B chains: {tasks}")
    if any(re.search(r"MSAR3|K=3", t) for t in tasks):
        raise TierBError("K=3 is not part of Tier B")
    origins = {b: sum(TIER_B_CHAINS[t][0] for t in ts) for b, ts in BATCHES.items()}
    if sum(origins.values()) != 6041:
        raise TierBError(f"planned origins {origins} do not sum to 6,041")
    return {"tasks": sorted(tasks), "origins_by_batch": origins,
            "cpu_hours_by_batch": {b: round(sum(TIER_B_CHAINS[t][0] * TIER_B_CHAINS[t][1]
                                                for t in ts) / 3600, 2)
                                   for b, ts in BATCHES.items()}}


def batch_tasks(batch: str) -> tuple[str, ...]:
    if batch not in BATCHES:
        raise TierBError(f"unknown batch {batch!r}")
    return BATCHES[batch]


def slug(task: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", task).strip("_")


def utc_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def batch_root(drive_root: Path | str, batch: str) -> Path:
    batch_tasks(batch)
    return Path(drive_root) / "baseline" / "r1_tierb_batches" / batch


def assert_writable_path(path: Path | str, drive_root: Path | str, batch: str) -> Path:
    """Every Drive write of a batch must be inside that batch's own namespace."""
    path, root = Path(path).resolve(), batch_root(drive_root, batch).resolve()
    if path != root and root not in path.parents:
        raise TierBError(f"refusing to write {path}: outside {root}")
    return path


# -- integrity ---------------------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path | str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def payload_files(fits: Path | str) -> list[Path]:
    """Committed payloads only (`*.json` two levels down); `*.tmp` and README excluded."""
    fits = Path(fits)
    return sorted(p for p in fits.glob("*/*.json") if p.is_file())


def inventory(fits: Path | str) -> dict[str, str]:
    fits = Path(fits)
    return {p.relative_to(fits).as_posix(): sha256_file(p) for p in payload_files(fits)}


def read_payload(path: Path | str, *, require_marker: bool = True) -> dict:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise TierBError(f"unreadable payload {path}: {error}") from error
    if require_marker and payload.get(MARKER) != MARKER_VALUE:
        raise TierBError(f"payload without the R1 refit marker: {path}")
    return payload


def write_json_atomic(path: Path | str, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    os.replace(temporary, path)


_MEMBER = re.compile(r"^[0-9a-f]{2}/[0-9a-f]{64}\.json$")


def _safe_members(archive: tarfile.TarFile, prefix: str = "") -> list[tarfile.TarInfo]:
    members = []
    for member in archive.getmembers():
        name = member.name
        if name.startswith("/") or ".." in Path(name).parts or member.issym() or member.islnk():
            raise TierBError(f"unsafe archive member {name!r}")
        if member.isfile():
            relative = name[len(prefix):] if prefix and name.startswith(prefix) else name
            if _MEMBER.match(relative):
                members.append(member)
            elif not relative.endswith("README_R1_REFIT_CACHE.txt"):
                raise TierBError(f"unexpected archive member {name!r}")
    return members


# -- committed checkpoints ---------------------------------------------------------------
#
# Completion-marker protocol (does not rely on directory renames being atomic on the
# Google Drive mount). A checkpoint folder is created under its final name and filled in
# this order: payloads.tar.gz (read back and verified member by member), manifest.json
# (read back), and last COMMITTED, a small JSON naming the checkpoint and the sha256 of
# the manifest and the archive (read back). A folder is a committed checkpoint only if
# COMMITTED parses and both hashes match; a folder without a valid marker is an
# interrupted write: it is ignored, listed, and never deleted or modified. Once a valid
# marker exists, any later mismatch is corruption and raises.

COMMIT_MARKER = "COMMITTED"
PROTOCOL = "r1-tierb-marker-v1"


def _checkpoint_dirs(task_dir: Path) -> list[Path]:
    if not task_dir.exists():
        return []
    return sorted(p for p in task_dir.iterdir() if p.is_dir() and p.name.startswith("ckpt-"))


def _marker(folder: Path) -> dict | None:
    """The parsed completion marker, or None for an interrupted (incomplete) write."""
    if folder.name.endswith(".partial"):
        return None
    path = folder / COMMIT_MARKER
    if not path.is_file():
        return None
    try:
        marker = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None                         # a marker cut off mid-write: never completed
    if not isinstance(marker, dict) or marker.get("protocol") != PROTOCOL:
        return None
    return marker


def incomplete_checkpoints(task_dir: Path | str) -> list[str]:
    """Folders of interrupted checkpoint writes (no valid completion marker)."""
    return [p.name for p in _checkpoint_dirs(Path(task_dir)) if _marker(p) is None]


def committed_checkpoints(task_dir: Path | str) -> list[tuple[Path, dict]]:
    """Committed checkpoints of one chain, validated and in commit order.

    A folder counts only with a valid completion marker whose manifest and archive
    sha256 match the files. The parents must form one linear history: a fork (two
    sessions writing the same chain) or a gap is an error, never resolved by guessing.
    """
    task_dir = Path(task_dir)
    found = []
    for folder in _checkpoint_dirs(task_dir):
        marker = _marker(folder)
        if marker is None:
            continue                       # an interrupted write; earlier commits stand
        if marker.get("checkpoint_id") != folder.name:
            raise TierBError(f"checkpoint {folder.name}: marker names {marker.get('checkpoint_id')}")
        manifest_path, archive = folder / "manifest.json", folder / "payloads.tar.gz"
        if not manifest_path.is_file() or sha256_file(manifest_path) != marker["manifest_sha256"]:
            raise TierBError(f"checkpoint {folder.name}: manifest missing or sha256 mismatch")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not archive.is_file() or sha256_file(archive) != manifest["archive_sha256"] \
                or manifest["archive_sha256"] != marker["archive_sha256"]:
            raise TierBError(f"checkpoint {folder.name}: archive missing or sha256 mismatch")
        if manifest.get("checkpoint_id") != folder.name:
            raise TierBError(f"checkpoint {folder.name}: manifest names {manifest.get('checkpoint_id')}")
        found.append((folder, manifest))
    by_parent: dict[str | None, list] = {}
    for folder, manifest in found:
        by_parent.setdefault(manifest.get("parent"), []).append((folder, manifest))
    if any(len(children) > 1 for children in by_parent.values()):
        raise TierBError(f"{task_dir.name}: forked checkpoint history (concurrent sessions?)")
    ordered, parent = [], None
    while parent in by_parent:
        folder, manifest = by_parent.pop(parent)[0]
        ordered.append((folder, manifest))
        parent = manifest["checkpoint_id"]
    if by_parent:
        raise TierBError(f"{task_dir.name}: checkpoints not reachable from the first commit: "
                         f"{[m['checkpoint_id'] for v in by_parent.values() for _, m in v]}")
    return ordered


def committed_inventory(task_dir: Path | str) -> dict[str, str]:
    files: dict[str, str] = {}
    for _, manifest in committed_checkpoints(task_dir):
        for name, digest in manifest["members"].items():
            if files.get(name, digest) != digest:
                raise TierBError(f"conflicting payload {name} across checkpoints")
            files[name] = digest
    return files


def _write_verified(path: Path, data: bytes) -> None:
    """Write a file in place and read it back; raise if the destination differs."""
    with open(path, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    if sha256_file(path) != sha256_bytes(data):
        raise TierBError(f"{path}: read-back differs from what was written")


def commit_checkpoint(local_fits: Path | str, task_dir: Path | str, *, task: str,
                      session: str, extra: dict | None = None,
                      _fail_after_archive: bool = False,
                      _fail_in_marker: bool = False) -> dict | None:
    """Commit the payloads written since the last committed checkpoint.

    The archive is built on local disk, copied into the checkpoint folder, read back
    from the destination and verified member by member; then the manifest; then the
    completion marker. An interruption at any point leaves a folder without a valid
    marker, which is ignored: earlier commits are never touched. Returns the manifest,
    or None when nothing is new. Raises on any write or verification failure.
    """
    local_fits, task_dir = Path(local_fits), Path(task_dir)
    history = committed_checkpoints(task_dir)
    known = committed_inventory(task_dir)
    current = inventory(local_fits)
    changed = [n for n, d in current.items() if n in known and known[n] != d]
    if changed:
        raise TierBError(f"{task}: local payloads differ from committed ones: {changed[:3]}")
    new = sorted(n for n in current if n not in known)
    if not new:
        return None
    for name in new:                       # never publish an improperly marked payload
        read_payload(local_fits / name)
    sequence = len(history) + 1
    # unique even when a retry follows an abandoned write in the same second
    checkpoint_id = f"ckpt-{utc_stamp()}-{session}-{sequence:05d}-{os.urandom(3).hex()}"
    folder = task_dir / checkpoint_id
    with tempfile.TemporaryDirectory() as scratch:
        local_archive = Path(scratch) / "payloads.tar.gz"
        with tarfile.open(local_archive, "w:gz") as archive:
            for name in new:
                archive.add(local_fits / name, arcname=name)
        archive_bytes = local_archive.read_bytes()
    archive_sha = sha256_bytes(archive_bytes)
    folder.mkdir(parents=True, exist_ok=False)
    written = folder / "payloads.tar.gz"
    _write_verified(written, archive_bytes)
    if _fail_after_archive:                # test hook: an interrupted backup
        raise OSError("simulated interruption during checkpoint write")
    with tarfile.open(written, "r:gz") as archive:
        members = _safe_members(archive)
        got = {m.name: sha256_bytes(archive.extractfile(m).read()) for m in members}
    expected = {n: current[n] for n in new}
    if got != expected:
        raise TierBError(f"{task}: archive read back does not match the local payloads")
    manifest = {"checkpoint_id": checkpoint_id, "protocol": PROTOCOL, "task": task,
                "session": session, "sequence": sequence,
                "parent": history[-1][1]["checkpoint_id"] if history else None,
                "created_utc": utc_stamp(), "archive_sha256": archive_sha,
                "members": expected, "new_payloads": len(new),
                "cumulative_payloads": len(known) + len(new), **(extra or {})}
    manifest_bytes = json.dumps(manifest, indent=1, sort_keys=True).encode("utf-8")
    _write_verified(folder / "manifest.json", manifest_bytes)
    marker = json.dumps({"protocol": PROTOCOL, "checkpoint_id": checkpoint_id,
                         "manifest_sha256": sha256_bytes(manifest_bytes),
                         "archive_sha256": archive_sha}, sort_keys=True).encode("utf-8")
    if _fail_in_marker:                    # test hook: the marker itself cut off
        (folder / COMMIT_MARKER).write_bytes(marker[: len(marker) // 2])
        raise OSError("simulated interruption while writing the completion marker")
    _write_verified(folder / COMMIT_MARKER, marker)
    if _marker(folder) is None:
        raise TierBError(f"{folder}: completion marker not readable after writing")
    return manifest


def restore_checkpoints(task_dir: Path | str, local_fits: Path | str) -> dict:
    """Extract every committed checkpoint of a chain into `local_fits`, verifying each."""
    task_dir, local_fits = Path(task_dir), Path(local_fits)
    local_fits.mkdir(parents=True, exist_ok=True)
    expected = committed_inventory(task_dir)
    history = committed_checkpoints(task_dir)
    for folder, manifest in history:
        with tarfile.open(folder / "payloads.tar.gz", "r:gz") as archive:
            for member in _safe_members(archive):
                data = archive.extractfile(member).read()
                if sha256_bytes(data) != manifest["members"].get(member.name):
                    raise TierBError(f"{folder.name}: {member.name} fails its sha256")
                target = local_fits / member.name
                if target.exists():
                    if sha256_file(target) != expected[member.name]:
                        raise TierBError(f"conflicting local payload {member.name}")
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                temporary = target.with_name(target.name + ".tmp")
                temporary.write_bytes(data)
                os.replace(temporary, target)
    restored = inventory(local_fits)
    missing = [n for n, d in expected.items() if restored.get(n) != d]
    if missing:
        raise TierBError(f"{task_dir.name}: restored payloads do not match the manifests: "
                         f"{missing[:3]}")
    return {"payloads": len(expected), "checkpoints": len(history),
            "ignored_incomplete_writes": incomplete_checkpoints(task_dir)}


# -- Tier A ------------------------------------------------------------------------------

def restore_tier_a(archive_path: Path | str, local_fits: Path | str, *,
                   expected_sha256: str = TIER_A_ARCHIVE_SHA256) -> dict:
    """Extract the Tier A refit cache (read only on Drive), verifying everything static."""
    archive_path, local_fits = Path(archive_path), Path(local_fits)
    if not archive_path.is_file():
        raise TierBError(f"Tier A archive not found: {archive_path}")
    archive_sha = sha256_file(archive_path)
    if expected_sha256 and archive_sha != expected_sha256:
        raise TierBError(f"Tier A archive sha256 {archive_sha} != expected {expected_sha256}")
    local_fits.mkdir(parents=True, exist_ok=True)
    inventory_: dict[str, str] = {}
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in _safe_members(archive, prefix="refit_cache/fits/"):
            relative = member.name[len("refit_cache/fits/"):]
            data = archive.extractfile(member).read()
            payload = json.loads(data)
            if payload.get(MARKER) != MARKER_VALUE:
                raise TierBError(f"Tier A payload without the refit marker: {relative}")
            target = local_fits / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            inventory_[relative] = sha256_bytes(data)
    if len(inventory_) != TIER_A_PAYLOADS:
        raise TierBError(f"Tier A archive holds {len(inventory_)} payloads, expected "
                         f"{TIER_A_PAYLOADS}")
    return {"archive_sha256": archive_sha, "payloads": len(inventory_),
            "inventory_sha256": sha256_bytes(json.dumps(inventory_, sort_keys=True).encode())}


# -- the pinned scientific code ----------------------------------------------------------

def use_scientific_code(code_dir: Path | str) -> None:
    """Import `thesis` from the pinned checkout's `code/src` (and nowhere else)."""
    src = str(Path(code_dir) / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    import thesis  # noqa: F401
    if Path(thesis.__file__).resolve().parents[1] != Path(src).resolve():
        raise TierBError(f"thesis imported from {thesis.__file__}, not {src}")


def build_jobs(original_output: Path | str, code_dir: Path | str) -> tuple[dict, Any, Any]:
    """Every rolling job of the pinned pipeline, as the R1 workflow builds them.

    Runs the pinned data preparation, stationarity stage and published specifications
    under `estimation_forbidden()`; nothing is estimated. Returns (jobs, identity, config).
    """
    use_scientific_code(code_dir)
    from thesis.core.config import load_config
    from thesis.core.paths import CONFIG_DIR, FROZEN_DIR, Namespace, OutputLayout
    from thesis.core.provenance import RunContext
    from thesis.correction import guard
    from thesis.correction.rescore import PublishedRescorer
    from thesis.data.store import load_bundle

    config = load_config(names=("baseline", "series_catalog", "thresholds"),
                         config_dir=CONFIG_DIR)
    with guard.estimation_forbidden():
        bundle = load_bundle(FROZEN_DIR, config)
        context = RunContext(namespace=Namespace.CORRECTION, config_hash=config.hash,
                             data_snapshot_hash=bundle.data_input_identity)
        scratch = Path(tempfile.mkdtemp(prefix="r1_tierb_jobs_"))
        layout = OutputLayout(root=scratch / "output", cache=scratch / "cache")
        rescorer = PublishedRescorer(config, context, layout, bundle,
                                     original=Path(original_output).resolve(), use_cache=False)
        layout.create()
        rescorer.prepare_data()
        rescorer.stationarity_stage()
        rescorer.load_specifications()
        jobs = {job.task_id: job for job, *_ in rescorer._rolling_jobs()}
    return jobs, rescorer.identity, config


def cache_identity_string(config, frozen_csv: Path | str) -> str:
    from thesis.core.cache import code_hash
    parts = {"code": code_hash(), "config": config.hash, "data": sha256_file(frozen_csv)}
    return sha256_bytes(json.dumps(parts, sort_keys=True).encode())[:16]


def walk_chain(job, fits: Path | str, identity, config, *,
               require_marker: bool = True) -> dict:
    """Follow a chain's keys through a refit cache exactly as the pinned engine replays it.

    Mirrors the cache branch of the pinned `rolling.run_chain`: same keys, same horizon
    check, same predecessor (warm-start) hash from each payload's `warm_payload`. Returns
    the contiguous completed prefix, the payloads it reached, and every payload in the
    directory it did not reach (which would mean an inconsistent cache).
    """
    import numpy as np
    from thesis.core.cache import FitCache
    from thesis.forecasting.rolling import _cache_key, _covers
    from thesis.forecasting.windows import estimation_origins

    fits = Path(fits)
    cache = FitCache(fits, enabled=True)
    horizons = sorted(set(int(h) for h in job.horizons))
    origins = estimation_origins(job.y.index, job.window_length, horizons,
                                 max_origins=job.max_origins)
    use_warm = bool(config.get("forecasting.warm_starts", True))
    predecessor, completed, gaps = "", 0, 0
    reached: set[str] = set()
    statuses: dict[str, int] = {}
    sequence: list[tuple[str, str]] = []
    first_missing = None
    for origin in origins:
        window = job.y.iloc[origin.estimation_slice()]
        if not np.isfinite(window.to_numpy(dtype=float)).all():
            gaps += 1
            continue
        path = cache.path_for(_cache_key(identity, job.series_name, job.transformation,
                                         job.spec, origin, predecessor))
        if not path.is_file():
            first_missing = origin.origin_date.strftime("%Y-%m-%d")
            break
        payload = read_payload(path, require_marker=require_marker)
        if not _covers(payload, horizons):
            raise TierBError(f"{job.task_id}: payload for {origin.origin_date:%Y-%m-%d} "
                             "does not cover the chain's horizons")
        reached.add(path.relative_to(fits).as_posix())
        sequence.append((origin.origin_date.strftime("%Y-%m-%d"),
                         path.relative_to(fits).as_posix()))
        statuses[payload["status"]] = statuses.get(payload["status"], 0) + 1
        completed += 1
        warm = payload.get("warm_payload")
        predecessor = ""
        if use_warm and warm is not None:
            predecessor = f"{np.round(np.asarray(warm, float).ravel(), 10).tolist()}"
    present = {p.relative_to(fits).as_posix() for p in payload_files(fits)}
    return {"task_id": job.task_id, "planned": len(origins) - gaps, "gaps": gaps,
            "completed": completed, "complete": completed == len(origins) - gaps,
            "first_missing": first_missing, "statuses": statuses, "sequence": sequence,
            "reached": sorted(reached), "unreachable": sorted(present - reached)}


# -- runtime budget ----------------------------------------------------------------------

def vm_start_epoch() -> float:
    """When this machine booted: the start of the Colab runtime's lifetime."""
    try:
        uptime = float(Path("/proc/uptime").read_text().split()[0])
        return time.time() - uptime
    except (OSError, ValueError):
        return time.time()


class Budget:
    """Runtime budget measured from the VM's start, with a reserve for the final commit."""

    def __init__(self, start_epoch: float, budget_hours: float, reserve_minutes: float):
        if budget_hours <= 0 or reserve_minutes < 0:
            raise TierBError("budget must be positive and the reserve non-negative")
        self.start_epoch = float(start_epoch)
        self.deadline = self.start_epoch + budget_hours * 3600.0
        self.stop_scheduling = self.deadline - reserve_minutes * 60.0

    def remaining(self, now: float | None = None) -> float:
        return self.stop_scheduling - (time.time() if now is None else now)

    def can_start(self, expected_seconds: float, now: float | None = None) -> bool:
        return self.remaining(now) > expected_seconds


def _pinned_refit_cache():
    from thesis.correction.rescore import RefitCache
    return RefitCache


def stoppable_refit_cache(fits: Path | str, *, task: str, budget: Budget,
                          historical_seconds: float, stop_file: Path | str,
                          progress: Path | str, safety: float = 3.0):
    """The pinned RefitCache, able to stop the chain cleanly between origins.

    `put` first commits the payload exactly as the pinned class does (marker, atomic
    write), logs the origin's actual fit time, and only then may raise GracefulStop.
    `get` raises GracefulStop on a miss (an origin about to be estimated) when the
    remaining budget cannot cover `safety` times the expected fit time, or when the
    stop file exists. Hits are always served: replaying verified origins costs nothing.
    """
    RefitCache = _pinned_refit_cache()

    class StoppableRefitCache(RefitCache):
        def configure(self):
            self._task, self._budget = task, budget
            self._stop_file, self._progress = Path(stop_file), Path(progress)
            self._durations: list[float] = []
            self._historical, self._safety = float(historical_seconds), float(safety)
            self._last = time.time()
            return self

        def _expected(self) -> float:
            recent = self._durations[-20:]
            typical = sorted(recent)[len(recent) // 2] if recent else self._historical
            return self._safety * max(typical, self._historical / 4.0, 1.0)

        def _should_stop(self) -> str | None:
            if self._stop_file.exists():
                return "stop file present"
            if not self._budget.can_start(self._expected()):
                return "runtime budget: not enough time left for another origin"
            return None

        def get(self, key):
            payload = super().get(key)
            if payload is None:
                reason = self._should_stop()
                if reason:
                    raise GracefulStop(reason)
                self._last = time.time()
            return payload

        def put(self, key, payload):
            super().put(key, payload)              # the pinned write: marker + atomic
            seconds = time.time() - self._last
            self._durations.append(seconds)
            with open(self._progress, "a", encoding="utf-8") as handle:
                handle.write(json.dumps({"task": self._task, "utc": utc_stamp(),
                                         "refit_date": key.refit_date,
                                         "seconds": round(seconds, 3),
                                         "status": payload.get("status")}) + "\n")
            reason = self._should_stop()
            if reason:
                raise GracefulStop(reason)

    return StoppableRefitCache(Path(fits)).configure()


# -- leases (one active session per batch) ------------------------------------------------

def acquire_lease(root: Path | str, session: str, *, stale_minutes: float = 45.0) -> Path:
    leases = Path(root) / "leases"
    leases.mkdir(parents=True, exist_ok=True)
    now = time.time()
    for lease in leases.glob("*.json"):
        if lease.stem == session:
            continue
        data = json.loads(lease.read_text(encoding="utf-8"))
        if data.get("released") is None and now - float(data.get("heartbeat", 0)) < stale_minutes * 60:
            raise TierBError(f"batch already active in session {lease.stem} "
                             f"(heartbeat {int(now - data['heartbeat'])} s ago)")
    mine = leases / f"{session}.json"
    write_json_atomic(mine, {"session": session, "heartbeat": now, "released": None})
    return mine


def heartbeat(lease: Path | str) -> None:
    data = json.loads(Path(lease).read_text(encoding="utf-8"))
    data["heartbeat"] = time.time()
    write_json_atomic(lease, data)


def release_lease(lease: Path | str) -> None:
    data = json.loads(Path(lease).read_text(encoding="utf-8"))
    data["released"] = time.time()
    write_json_atomic(lease, data)


# -- session provenance (also for hard-killed sessions) ------------------------------------

SESSION_START = "session_started.json"
SESSION_SUMMARY = "session_summary.json"


def _session_of_checkpoint(name: str) -> str:
    """`ckpt-<utc>-<session>-<seq>-<rand>` -> `<session>` (sessions contain hyphens)."""
    parts = name.removesuffix(".partial").split("-")
    return "-".join(parts[2:-2])


def session_ledger(root: Path | str) -> dict:
    """Every session of a batch, from its session folder, leases AND checkpoint manifests.

    A session is `terminated` only if it wrote `session_summary.json`. Any other session
    seen anywhere (a session folder with only `session_started.json` or `progress.json`,
    an unreleased lease, committed checkpoints, or an incomplete checkpoint write) is
    `interrupted`: it was hard-killed or lost before its summary. Work it committed is
    still accounted for from the manifests; work after its last commit was lost.
    """
    root = Path(root)
    sessions: dict[str, dict] = {}

    def entry(session: str) -> dict:
        return sessions.setdefault(session, {
            "session": session, "session_dir": None, "started_utc": None,
            "finished_utc": None, "elapsed_hours": None, "exit_code": None,
            "final_verification": None, "outcomes": None, "lease_released": None,
            "last_progress_utc": None, "checkpoints": 0, "first_checkpoint_utc": None,
            "last_checkpoint_utc": None, "payloads_committed_by_task": {},
            "incomplete_checkpoint_writes": [], "summary_estimations": None})

    for folder in sorted((root / "sessions").glob("*")) if (root / "sessions").exists() else []:
        if not folder.is_dir():
            continue
        start = folder / SESSION_START
        info = json.loads(start.read_text(encoding="utf-8")) if start.is_file() else {}
        session = info.get("session") or folder.name.split("-", 1)[-1]
        e = entry(session)
        e["session_dir"] = folder.name
        e["started_utc"] = info.get("started_utc") or folder.name.split("-", 1)[0]
        progress = folder / "progress.json"
        if progress.is_file():
            e["last_progress_utc"] = _dt.datetime.fromtimestamp(
                progress.stat().st_mtime, _dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        summary = folder / SESSION_SUMMARY
        if summary.is_file():
            data = json.loads(summary.read_text(encoding="utf-8"))
            for key in ("finished_utc", "elapsed_hours", "exit_code", "final_verification",
                        "outcomes"):
                e[key] = data.get(key)
            e["summary_estimations"] = data.get("estimations")
    for lease in sorted((root / "leases").glob("*.json")) if (root / "leases").exists() else []:
        data = json.loads(lease.read_text(encoding="utf-8"))
        entry(data.get("session") or lease.stem)["lease_released"] = data.get("released") is not None
    checkpoints = root / "checkpoints"
    for task_dir in sorted(checkpoints.iterdir()) if checkpoints.exists() else []:
        if not task_dir.is_dir():
            continue
        for _, manifest in committed_checkpoints(task_dir):
            e = entry(manifest["session"])
            e["checkpoints"] += 1
            stamp = manifest["created_utc"]
            e["first_checkpoint_utc"] = min(filter(None, [e["first_checkpoint_utc"], stamp]))
            e["last_checkpoint_utc"] = max(filter(None, [e["last_checkpoint_utc"], stamp]))
            counts = e["payloads_committed_by_task"]
            counts[manifest["task"]] = counts.get(manifest["task"], 0) + len(manifest["members"])
            record = manifest.get("session_record") or {}
            e["started_utc"] = e["started_utc"] or record.get("started_utc")
        for name in incomplete_checkpoints(task_dir):
            entry(_session_of_checkpoint(name))["incomplete_checkpoint_writes"].append(
                f"{task_dir.name}/{name}")
    terminated, interrupted = [], []
    for session in sorted(sessions, key=lambda s: (sessions[s]["started_utc"] or "", s)):
        e = sessions[session]
        if e["exit_code"] is not None:
            e["state"] = {0: "terminated: complete", 3: "terminated: budget reached, work remains",
                          2: "terminated: error"}.get(e["exit_code"], f"terminated: exit {e['exit_code']}")
            terminated.append(e)
        else:
            e["state"] = "interrupted: no session summary (hard-killed or lost)"
            interrupted.append(e)
    return {"terminated": terminated, "interrupted": interrupted,
            "payloads_committed_by_task": _sum_counts(
                e["payloads_committed_by_task"] for e in sessions.values())}


def _sum_counts(dicts: Iterable[dict]) -> dict:
    out: dict = {}
    for d in dicts:
        for key, value in d.items():
            out[key] = out.get(key, 0) + value
    return out


# -- certificates ------------------------------------------------------------------------
#
# A certificate says the COMPUTATION is complete and verified. It never says the result
# is scientifically approved: that is a separate, human decision. `scientific_status`
# is one of the values below, and `scientific_approval` is always "not granted".

STATUS_REVIEW_REQUIRED = "COMPUTATION_COMPLETE_REVIEW_REQUIRED"
STATUS_WARNINGS = "COMPUTATION_COMPLETE_SENSITIVITY_REPORTED"
STATUS_REPRODUCED = "COMPUTATION_COMPLETE_REPRODUCED"
STATUS_INCOMPLETE = "COMPUTATION_INCOMPLETE"
APPROVAL_NOT_GRANTED = ("not granted: a completed computation is not an approved result; "
                        "every review item and reported warning needs independent review")


def scientific_status(blocking: Iterable[str], sensitivity: Iterable[str]) -> str:
    if list(blocking):
        return STATUS_REVIEW_REQUIRED
    if list(sensitivity):
        return STATUS_WARNINGS
    return STATUS_REPRODUCED


def certificate(batch: str, walks: dict[str, dict], checkpoints: dict[str, list[dict]], *,
                provenance: dict, sessions: dict, agreement: dict[str, dict]) -> dict:
    """The batch completion certificate (only produced when every chain is complete).

    `sessions` is `session_ledger(...)`; `agreement` is `agreement(...)` per task. Changed
    failure counts and every blocking agreement item are review items; MSAR/STAR
    optimizer sensitivity is reported separately. Neither is ever folded into "approved".
    """
    tasks = batch_tasks(batch)
    if set(walks) != set(tasks):
        raise TierBError(f"{batch}: walks for {sorted(walks)} != {sorted(tasks)}")
    if set(agreement) != set(tasks):
        raise TierBError(f"{batch}: agreement for {sorted(agreement)} != {sorted(tasks)}")
    incomplete = {t: w["completed"] for t, w in walks.items() if not w["complete"]}
    unreachable = {t: len(w["unreachable"]) for t, w in walks.items() if w["unreachable"]}
    if incomplete or unreachable:
        raise TierBError(f"{batch} not complete: incomplete {incomplete}, "
                         f"unreachable {unreachable}")
    estimations = sessions["payloads_committed_by_task"]
    if set(estimations) - set(tasks):
        raise TierBError(f"{batch}: estimations outside the batch: {set(estimations) - set(tasks)}")
    chains, review_items, sensitivity = {}, [], []
    for task in tasks:
        walk = walks[task]
        statuses = walk["statuses"]
        planned, _, original_failed = TIER_B_CHAINS[task]
        if walk["planned"] != planned:
            raise TierBError(f"{task}: {walk['planned']} origins, expected {planned}")
        a = agreement[task]
        failed = statuses.get("failed", 0)
        if failed != original_failed:
            review_items.append(f"{task}: failed fits {failed} vs original {original_failed}")
        review_items += a["review_items"]
        sensitivity += a["sensitivity_items"]
        chains[task] = {"planned_origins": planned, "completed_origins": walk["completed"],
                        "computation": "complete", "adequate": statuses.get("adequate", 0),
                        "fragile": statuses.get("fragile", 0), "failed": failed,
                        "original_failed": original_failed,
                        "failure_count_changed": failed != original_failed,
                        "agreement_status": a["status"],
                        "agreement": {k: v for k, v in a.items() if k != "rows"},
                        "checkpoints": checkpoints.get(task, [])}
    status = scientific_status(review_items, sensitivity)
    return {"batch": batch, "authorized_tasks": list(tasks), "complete": True,
            "computation_status": "COMPUTATION_COMPLETE",
            "scientific_status": status, "scientific_approval": APPROVAL_NOT_GRANTED,
            "review_items": review_items, "sensitivity_reported": sensitivity,
            "expected_origins": sum(TIER_B_CHAINS[t][0] for t in tasks),
            "completed_origins": sum(w["completed"] for w in walks.values()),
            "chains": chains, "provenance": provenance,
            "sessions_terminated": sessions["terminated"],
            "sessions_interrupted": sessions["interrupted"],
            "estimations_by_task": {"committed_payloads": estimations},
            "only_authorized_models_estimated": not (set(estimations) - set(tasks)),
            "warnings": review_items + sensitivity, "created_utc": utc_stamp()}


def latest_certificate(root: Path | str) -> dict | None:
    folder = Path(root) / "certificates"
    found = sorted(folder.glob("COMPLETE-*.json")) if folder.exists() else []
    return json.loads(found[-1].read_text(encoding="utf-8")) if found else None


@contextmanager
def no_estimation_allowed():
    """Inside this block even an --approve'd chain cannot estimate (assembly only)."""
    from thesis.correction import guard
    original = guard.allowed

    @contextmanager
    def refuse():
        yield                               # allowed_depth stays 0: estimators raise
    guard.allowed = refuse
    try:
        yield
    finally:
        guard.allowed = original


# -- numerical agreement with the original estimates (G7) ---------------------------------
#
# Tolerances (declared, used as stated):
#   LOGLIK_TOLERANCE   |l_new - l_orig| / max(1, |l_orig|)
#   PARAM_TOLERANCE    max over parameters of |p_new - p_orig| / max(1, |p_orig|)
# The original parameters are stored with 10 significant digits (fit_records.params),
# so their rounding contributes at most 5e-10 to the scaled difference: well inside
# PARAM_TOLERANCE.

LOGLIK_TOLERANCE = 1e-6
PARAM_TOLERANCE = 1e-8
WARM_STARTED = ("MSAR", "MSAR3", "STAR")

# Per origin, exactly one category. REVIEW categories make the chain (and the batch and
# the aggregation) REVIEW_REQUIRED; SENSITIVITY categories are expected optimizer
# sensitivity of warm-started models (F6): always reported, never called an error,
# never called reproduced.
REVIEW_CATEGORIES = {
    "classification_changed": "status or reason codes differ from the original fit",
    "missing_original_record": "no original fit record for a re-estimated origin",
    "original_origin_not_reestimated": "an original fit record with no re-estimated origin",
    "parameter_names_differ": "the re-estimated and original parameter sets differ",
    "reproduction_failure": "non-warm-started model (ARMA) does not reproduce within tolerance",
    "unexplained_parameter_discrepancy": ("parameters differ beyond tolerance at equal "
                                          "likelihood before the chain's warm-start path "
                                          "diverged (not explained by different starts)"),
}
SENSITIVITY_CATEGORIES = {
    "optimizer_sensitivity": ("warm-started model, same classification, different "
                              "log-likelihood (another optimum or different start)"),
    "flat_likelihood_sensitivity": ("warm-started model, same classification, equal "
                                    "log-likelihood, different parameters after the "
                                    "warm-start path diverged"),
}
REPRODUCED_CATEGORIES = ("reproduced", "reproduced_regime_labels_permuted")


def _parse_params(text) -> dict:
    out = {}
    for part in str(text or "").split(";"):
        if "=" in part:
            name, value = part.split("=", 1)
            try:
                out[name.strip()] = float(value)
            except ValueError:
                out[name.strip()] = float("nan")
    return out


def _codes(value) -> frozenset:
    if value is None or (isinstance(value, float) and value != value):
        return frozenset()
    if isinstance(value, (list, tuple)):
        return frozenset(str(v) for v in value if str(v))
    return frozenset(c.strip() for c in str(value).split(";") if c.strip())


def _scaled_diff(a: float, b: float) -> float:
    import math
    if a is None or b is None:
        return 0.0 if a is b else float("inf")
    a, b = float(a), float(b)
    if not (math.isfinite(a) and math.isfinite(b)):
        return 0.0 if (a == b or (a != a and b != b)) else float("inf")
    return abs(a - b) / max(1.0, abs(b))


def regime_permutations(names: Iterable[str]) -> list[dict[str, str]]:
    """Renamings of MSAR parameters for every relabelling of the regimes.

    Regime-indexed names in the pinned MSAR (msar.py): `mu{k}` and `p{ij}`; `phi{j}`
    (AR lags) and `sigma` are shared by all regimes and never renamed. The identity
    renaming comes first.
    """
    import itertools
    names = list(names)
    k = sum(1 for n in names if re.fullmatch(r"mu\d", n))
    if k < 2:
        return [{n: n for n in names}]
    out = []
    for perm in itertools.permutations(range(1, k + 1)):
        mapping = {}
        for n in names:
            if re.fullmatch(r"mu\d", n):
                mapping[n] = f"mu{perm[int(n[2]) - 1]}"
            elif re.fullmatch(r"p\d\d", n):
                mapping[n] = f"p{perm[int(n[1]) - 1]}{perm[int(n[2]) - 1]}"
            else:
                mapping[n] = n
        out.append(mapping)
    return out


def aligned_param_diff(new: dict, original: dict, model: str) -> tuple[float, str]:
    """Max scaled parameter difference, minimised over regime relabellings for MSAR.

    Returns (difference, permutation label): "identity" or e.g. "mu1->mu2,mu2->mu1".
    """
    candidates = (regime_permutations(new) if model in ("MSAR", "MSAR3")
                  else [{n: n for n in new}])
    best, label = float("inf"), "identity"
    for mapping in candidates:
        diff = max((_scaled_diff(new[n], original[mapping[n]]) for n in new), default=0.0)
        if diff < best:
            best = diff
            moved = sorted(f"{n}->{m}" for n, m in mapping.items()
                           if n != m and n.startswith("mu"))
            label = ",".join(moved) or "identity"
    return best, label


def original_chain_records(fit_records, task: str, job):
    """The original run's fit records of this exact chain, keyed by refit date.

    Same identification as `tier_b_workload.py`: series, model and window span; at the
    240-month span the T4.1 chain is the one record per origin whose parameters are not
    shared with the baseline chain and its T4.8 duplicate.
    """
    import pandas as pd
    f = fit_records[(fit_records["series"] == job.series_name)
                    & (fit_records["model"] == job.spec.model)].copy()
    start, end = pd.to_datetime(f["window_start"]), pd.to_datetime(f["window_end"])
    f["span"] = (end.dt.year - start.dt.year) * 12 + (end.dt.month - start.dt.month) + 1
    f = f[f["span"] == int(job.window_length)]
    if int(job.window_length) == 240:
        repeats = f.groupby(["refit_date", "params"])["params"].transform("size")
        f = f[repeats == 1] if task.startswith("T4.1:") else f
    dates = f["refit_date"].astype(str).str[:10]
    if dates.duplicated().any():                    # never pick one of several silently
        raise TierBError(f"{task}: original fit records are ambiguous at "
                         f"{sorted(set(dates[dates.duplicated()]))[:3]}")
    return {str(r.refit_date)[:10]: r for r in f.itertuples()}


def validate_original_records(fit_records, jobs, tasks) -> list[str]:
    """Each chain's original records: one per planned origin; failures as declared."""
    problems = []
    for task in tasks:
        planned, _, failed = TIER_B_CHAINS[task]
        try:
            records = original_chain_records(fit_records, task, jobs[task])
        except TierBError as error:
            problems.append(str(error))
            continue
        found = sum(1 for r in records.values() if r.status == "failed")
        if len(records) != planned or found != failed:
            problems.append(f"{task}: {len(records)} original records ({planned} planned), "
                            f"{found} failed ({failed} declared)")
    return problems


def agreement(task: str, job, walk: dict, fits, fit_records, *,
              loglik_tolerance: float = LOGLIK_TOLERANCE,
              param_tolerance: float = PARAM_TOLERANCE) -> dict:
    """Origin-by-origin agreement of a re-estimated chain with the original estimates.

    Every origin gets exactly one category (REVIEW_CATEGORIES, SENSITIVITY_CATEGORIES or
    reproduced). For every model, a changed classification (status or reason codes), a
    missing original record, an original origin not re-estimated, or a different set of
    parameter names requires review. ARMA (no warm start) must reproduce: loglik and
    every parameter within tolerance. MSAR/STAR are compared after aligning regime
    labels; a different optimum with the same classification is reported as optimizer
    sensitivity (F6), never as reproduced and never as an error.
    """
    model = job.spec.model
    warm = model in WARM_STARTED
    original = original_chain_records(fit_records, task, job)
    rows, counts, seen = [], {}, set()
    first_divergence = None
    diverged_path = False
    for date, relative in walk["sequence"]:
        payload = read_payload(Path(fits) / relative)
        record = original.get(date)
        seen.add(date)
        row = {"refit_date": date, "status_new": payload.get("status"),
               "reason_codes_new": ";".join(sorted(_codes(payload.get("reason_codes"))))}
        if record is None:
            row["category"] = "missing_original_record"
        else:
            same_class = (payload.get("status") == record.status
                          and _codes(payload.get("reason_codes")) == _codes(
                              getattr(record, "reason_codes", None)))
            mine = payload.get("params") or {}
            theirs = _parse_params(record.params)
            names_ok = set(mine) == set(theirs)
            l_new, l_orig = payload.get("loglik"), record.loglik
            l_diff = _scaled_diff(l_new, l_orig)
            if names_ok:
                p_diff, permutation = aligned_param_diff(mine, theirs, model)
            else:
                p_diff, permutation = float("nan"), "n/a"
            loglik_ok, params_ok = l_diff <= loglik_tolerance, p_diff <= param_tolerance
            if not same_class:
                category = "classification_changed"
            elif not names_ok:
                category = "parameter_names_differ"
            elif loglik_ok and params_ok:
                category = ("reproduced" if permutation == "identity"
                            else "reproduced_regime_labels_permuted")
            elif not warm:
                category = "reproduction_failure"
            elif loglik_ok:
                category = ("flat_likelihood_sensitivity" if diverged_path
                            else "unexplained_parameter_discrepancy")
            else:
                category = "optimizer_sensitivity"
            row.update({
                "status_original": record.status,
                "reason_codes_original": ";".join(sorted(_codes(getattr(record, "reason_codes", None)))),
                "loglik_new": l_new, "loglik_original": l_orig,
                "loglik_new_minus_original": (None if l_new is None or l_orig is None
                                              else float(l_new) - float(l_orig)),
                "loglik_scaled_diff": l_diff, "params_max_scaled_diff": p_diff,
                "regime_label_permutation": permutation,
                "param_names_new_only": ";".join(sorted(set(mine) - set(theirs))),
                "param_names_original_only": ";".join(sorted(set(theirs) - set(mine))),
                "start_used_new": payload.get("start_used"),
                "start_used_original": getattr(record, "start_used", None),
                "category": category})
        if row["category"] not in REPRODUCED_CATEGORIES:
            diverged_path = True
            first_divergence = first_divergence or date
        counts[row["category"]] = counts.get(row["category"], 0) + 1
        rows.append(row)
    unmatched = sorted(set(original) - seen)
    for date in unmatched:
        rows.append({"refit_date": date, "category": "original_origin_not_reestimated"})
    if unmatched:
        counts["original_origin_not_reestimated"] = len(unmatched)
    review_items = [f"{task}: {n} origins {c} ({REVIEW_CATEGORIES[c]})"
                    for c, n in sorted(counts.items()) if c in REVIEW_CATEGORIES]
    sensitivity_items = [f"{task}: {n} origins {c} ({SENSITIVITY_CATEGORIES[c]})"
                         for c, n in sorted(counts.items()) if c in SENSITIVITY_CATEGORIES]
    worse = sum(1 for r in rows if r.get("category") in SENSITIVITY_CATEGORIES
                and (r.get("loglik_new_minus_original") or 0) < 0)
    if sensitivity_items:
        sensitivity_items.append(f"{task}: re-estimated log-likelihood lower than the "
                                 f"original at {worse} of the sensitivity origins")
    return {"task": task, "model": model, "warm_started": warm,
            "loglik_tolerance": loglik_tolerance, "param_tolerance": param_tolerance,
            "origins_compared": sum(1 for r in rows if "status_original" in r),
            "categories": counts, "first_divergence": first_divergence,
            "status": scientific_status(review_items, sensitivity_items),
            "requires_review": bool(review_items),
            "review_items": review_items, "sensitivity_items": sensitivity_items,
            "warnings": review_items + sensitivity_items, "rows": rows}
