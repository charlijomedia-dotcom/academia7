"""Model-fit cache and stage checkpoints (Comp §5-§7).

The cache key is the full dependency set required by Comp §6 as amended: the canonical
input CSV hash and its parent official-source manifest hash, plus the series,
transformation, model, specification, estimation-window bounds, refit date, and the
dependency-aware code and configuration hashes. A cache entry is never reused when any
element changes.

Warm starts make nonlinear fits path dependent (risk R5), so the key also carries the hash
of the predecessor solution a fit was started from. A changed predecessor therefore
invalidates its successors instead of silently producing a different local optimum.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .hashing import hash_source_files, sha256_obj

#: Modules whose source can change a numerical fit. Reporting and plotting are excluded,
#: so editing a figure caption does not invalidate months of estimation (decision D15).
_FIT_CRITICAL = (
    "models/ar.py", "models/arma.py", "models/msar.py", "models/star.py",
    "models/var.py", "models/arma_garch.py", "models/flags.py",
    "transforms/growth.py", "transforms/differences.py", "transforms/lags.py",
    "forecasting/windows.py", "forecasting/rolling.py", "forecasting/simulate.py",
)


def code_hash(package_root: str | Path | None = None) -> str:
    root = Path(package_root) if package_root else Path(__file__).resolve().parent.parent
    return hash_source_files(root / name for name in _FIT_CRITICAL if (root / name).exists())


@dataclass(frozen=True)
class CacheKey:
    data_input_hash: str          # canonical CSV
    source_manifest_hash: str     # its official parent
    series: str
    transformation: str
    model: str
    specification: dict[str, Any]
    window_start: str
    window_end: str
    refit_date: str
    code_hash: str
    config_hash: str
    predecessor_hash: str = ""    # warm-start chain position

    def digest(self) -> str:
        return sha256_obj(asdict(self))


@dataclass
class FitCache:
    """A content-addressed store of fitted-model payloads."""

    directory: Path
    enabled: bool = True
    hits: int = 0
    misses: int = 0

    def __post_init__(self) -> None:
        self.directory = Path(self.directory)
        if self.enabled:
            self.directory.mkdir(parents=True, exist_ok=True)

    def path_for(self, key: CacheKey) -> Path:
        digest = key.digest()
        return self.directory / digest[:2] / f"{digest}.json"

    def get(self, key: CacheKey) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        path = self.path_for(key)
        if not path.exists():
            self.misses += 1
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self.misses += 1
            return None
        self.hits += 1
        return payload

    def put(self, key: CacheKey, payload: dict[str, Any]) -> None:
        if not self.enabled:
            return
        path = self.path_for(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        temporary.replace(path)

    def summary(self) -> dict[str, int]:
        return {"cache_hits": self.hits, "cache_misses": self.misses}
