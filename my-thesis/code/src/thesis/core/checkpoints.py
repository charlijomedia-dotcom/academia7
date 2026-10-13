"""Stage checkpoints (Comp §5).

After each stage a deterministic checkpoint records what went in and what came out, so a
failure late in the pipeline does not force valid earlier work to be repeated.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .hashing import sha256_obj

#: The ten stages Comp §5 requires, in order.
STAGES = (
    "frozen_data",
    "canonical_input",
    "stationarity_decisions",
    "selected_specifications",
    "nonlinearity_diagnostics",
    "model_fits",
    "forecasts",
    "evaluation",
    "robustness",
    "tables_and_figures",
)


@dataclass
class CheckpointStore:
    directory: Path
    enabled: bool = True
    entries: dict[str, dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.directory = Path(self.directory)
        if self.enabled:
            self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, stage: str) -> Path:
        return self.directory / f"{stage}.json"

    def record(self, stage: str, inputs: Any, outputs: Any, status: str = "complete") -> dict:
        if stage not in STAGES:
            raise ValueError(f"unknown stage {stage!r}; Comp §5 fixes {STAGES}")
        entry = {
            "stage": stage,
            "status": status,
            "inputs_hash": sha256_obj(inputs),
            "outputs_hash": sha256_obj(outputs),
            "recorded_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        self.entries[stage] = entry
        if self.enabled:
            self._path(stage).write_text(json.dumps(entry, indent=2, sort_keys=True),
                                         encoding="utf-8")
        return entry

    def is_valid(self, stage: str, inputs: Any) -> bool:
        """True when a completed checkpoint exists for exactly these inputs."""
        path = self._path(stage)
        if not self.enabled or not path.exists():
            return False
        try:
            entry = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        return entry.get("status") == "complete" and entry.get("inputs_hash") == sha256_obj(inputs)
