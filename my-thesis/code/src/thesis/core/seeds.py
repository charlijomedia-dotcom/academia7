"""Reproducible random seeding.

Comp §8 requires randomized procedures to use reproducible child seeds. The seed for a
unit of work is derived from a stable description of that work (series, model,
specification, origin), never from scheduling order, so parallel and serial execution
produce identical numbers (risk R9).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from .hashing import sha256_obj

# Width of the entropy slice taken from the key digest. 128 bits is ample and keeps the
# SeedSequence entropy value stable and printable.
_ENTROPY_BITS = 128


def seed_entropy(key: Any, master_seed: int) -> int:
    """Deterministic non-negative entropy value for a work-unit key."""
    digest = sha256_obj({"master_seed": int(master_seed), "key": key})
    return int(digest[: _ENTROPY_BITS // 4], 16)


def seed_sequence(key: Any, master_seed: int) -> np.random.SeedSequence:
    """SeedSequence for a work-unit key, independent of execution order."""
    return np.random.SeedSequence(seed_entropy(key, master_seed))


def generator(key: Any, master_seed: int) -> np.random.Generator:
    """A fresh PCG64 generator for a work-unit key."""
    return np.random.default_rng(seed_sequence(key, master_seed))


def describe(key: Any, master_seed: int) -> dict[str, Any]:
    """Seed provenance to record alongside any simulated result."""
    return {
        "master_seed": int(master_seed),
        "seed_key": key,
        "seed_entropy": str(seed_entropy(key, master_seed)),
        "generator": "PCG64",
    }
