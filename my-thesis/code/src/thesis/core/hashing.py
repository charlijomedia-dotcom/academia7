"""Deterministic hashing helpers.

Every hash in the pipeline goes through this module so that the cache key, the config
hash and the manifest hashes are computed the same way everywhere and are stable across
runs, machines and Python versions.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

_CHUNK = 1 << 20


def sha256_file(path: str | Path) -> str:
    """SHA-256 of a file's bytes."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while chunk := handle.read(_CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(obj: Any) -> str:
    """Canonical JSON: sorted keys, no insignificant whitespace, stable float repr.

    Used as the hashing pre-image for configs and cache keys, so two logically equal
    objects always produce the same digest regardless of construction order.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=_fallback)


def _fallback(obj: Any) -> Any:
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, (set, frozenset)):
        return sorted(obj)
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    if hasattr(obj, "item"):  # numpy scalars
        return obj.item()
    raise TypeError(f"cannot canonicalize {type(obj)!r} for hashing")


def sha256_obj(obj: Any) -> str:
    """SHA-256 of the canonical JSON encoding of an object."""
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def combine(parts: Iterable[str]) -> str:
    """Order-independent combination of hex digests."""
    return hashlib.sha256("".join(sorted(parts)).encode("utf-8")).hexdigest()


def hash_source_files(paths: Iterable[str | Path]) -> str:
    """Hash of a set of source files, identified by path and content.

    Decision D15: the cache key depends only on the modules that determine a fit, so
    editing reporting or plotting code does not invalidate econometric results.
    """
    entries = []
    for path in sorted(Path(p) for p in paths):
        entries.append({"path": path.name, "sha256": sha256_file(path)})
    return sha256_obj(entries)
