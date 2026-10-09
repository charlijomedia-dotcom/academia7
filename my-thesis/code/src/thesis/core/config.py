"""Configuration loading and hashing.

Configuration is data, never code. Everything that can change a numerical result lives
in `code/configs/*.yaml`, and the hash of the resolved configuration is recorded on every
output so a result can always be traced back to the settings that produced it
(CLAUDE.md §8).
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from .hashing import sha256_obj
from .paths import CONFIG_DIR

_MISSING = object()


def _deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(copy.deepcopy(dict(base)))
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


@dataclass(frozen=True)
class Config:
    """A resolved, immutable configuration tree."""

    data: dict[str, Any]
    sources: tuple[str, ...]

    def get(self, dotted: str, default: Any = _MISSING) -> Any:
        """Fetch a value by dotted path, e.g. `config.get("forecasting.windows.monthly")`.

        A missing key raises unless a default is supplied: silently defaulting a
        methodological parameter is exactly the failure mode the lock rules forbid.
        """
        node: Any = self.data
        for part in dotted.split("."):
            if not isinstance(node, Mapping) or part not in node:
                if default is _MISSING:
                    raise KeyError(f"configuration key not found: {dotted!r}")
                return default
            node = node[part]
        return copy.deepcopy(node) if isinstance(node, (dict, list)) else node

    def require(self, dotted: str) -> Any:
        """Fetch a value that must be present and must not be null.

        Used for parameters that have no defensible default, such as the HLZ kernel and
        bandwidth choices, which may only come from the published article (M3).
        """
        value = self.get(dotted)
        if value is None:
            raise KeyError(f"configuration key {dotted!r} is present but unset")
        return value

    def subtree(self, dotted: str) -> "Config":
        return Config(data=self.get(dotted), sources=self.sources)

    @property
    def hash(self) -> str:
        return sha256_obj(self.data)

    def subtree_hash(self, dotted: str) -> str:
        return sha256_obj(self.get(dotted))

    def with_overrides(self, overrides: Mapping[str, Any], label: str) -> "Config":
        return Config(
            data=_deep_merge(self.data, overrides),
            sources=self.sources + (label,),
        )


def load_yaml(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    return loaded or {}


def load_config(
    names: tuple[str, ...] = ("baseline", "series_catalog", "thresholds"),
    config_dir: str | Path | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> Config:
    """Load and merge the configuration files, in order.

    Later files override earlier ones. The default set is the baseline methodology
    parameters, the series catalogue and the operational thresholds.
    """
    directory = Path(config_dir) if config_dir else CONFIG_DIR
    merged: dict[str, Any] = {}
    sources: list[str] = []
    for name in names:
        path = directory / f"{name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"configuration file not found: {path}")
        merged = _deep_merge(merged, load_yaml(path))
        sources.append(name)
    config = Config(data=merged, sources=tuple(sources))
    if overrides:
        config = config.with_overrides(overrides, label="overrides")
    return config
