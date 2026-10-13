"""The pinned dependency set (approved decision R2).

Declaring dependencies is not pinning them. R2 requires the versions behind every
empirical result to be fixed and recorded, so these tests check that the lock file exists,
covers every runtime dependency the project declares, and still matches what is actually
installed. A silent drift between the lock file and the environment would make a recorded
result untraceable to the libraries that produced it.
"""

from __future__ import annotations

import importlib.metadata as metadata
import re
import tomllib
from pathlib import Path

import pytest

from thesis.core.paths import CODE_ROOT
from thesis.core.provenance import environment_record

LOCK = CODE_ROOT / "requirements.lock.txt"
PYPROJECT = CODE_ROOT / "pyproject.toml"
PIN = re.compile(r"^(?P<name>[A-Za-z0-9_.\-]+)==(?P<version>[A-Za-z0-9_.\-+]+)$")


def _pins() -> dict[str, str]:
    pins = {}
    for line in LOCK.read_text(encoding="utf-8").splitlines():
        match = PIN.match(line.strip())
        if match:
            pins[match["name"].lower().replace("_", "-")] = match["version"]
    return pins


def _declared() -> set[str]:
    with PYPROJECT.open("rb") as handle:
        data = tomllib.load(handle)
    return {re.split(r"[<>=!~\[]", d)[0].strip().lower().replace("_", "-")
            for d in data["project"]["dependencies"]}


class TestTheLockFileExists:
    def test_the_lock_file_is_present(self):
        assert LOCK.exists(), "approved decision R2 requires a pinned dependency set"

    def test_it_contains_pins_not_ranges(self):
        pins = _pins()
        assert pins, "the lock file contains no exact pins"
        for name, version in pins.items():
            assert version[0].isdigit(), f"{name} is not pinned to a concrete version"

    def test_it_records_the_interpreter_and_platform_it_was_captured_on(self):
        text = LOCK.read_text(encoding="utf-8")
        assert "# Python:" in text
        assert "# Platform:" in text
        assert "# Captured:" in text


class TestTheLockFileCoversWhatTheProjectDeclares:
    def test_every_declared_runtime_dependency_is_pinned(self):
        missing = _declared() - set(_pins())
        assert not missing, f"declared but not pinned: {sorted(missing)}"

    def test_the_test_runner_is_pinned_too(self):
        assert "pytest" in _pins()


class TestTheLockFileMatchesTheEnvironment:
    @pytest.mark.parametrize("name", sorted(_declared()))
    def test_the_installed_version_matches_the_pin(self, name):
        pins = _pins()
        try:
            installed = metadata.version(name)
        except metadata.PackageNotFoundError:
            pytest.fail(f"{name} is declared and pinned but not installed")
        assert installed == pins[name], (
            f"{name}: lock file pins {pins[name]} but {installed} is installed. "
            "Either reinstall from the lock file or regenerate it deliberately, "
            "because every recorded result is traceable to these versions.")


class TestProvenanceRecordsThePinnedSet:
    def test_the_environment_record_carries_the_lock_hash(self):
        record = environment_record()
        digest = record["requirements_lock_sha256"]
        assert digest != "absent"
        assert len(digest) == 64

    def test_the_environment_record_lists_every_library_the_pipeline_loads(self):
        packages = environment_record()["packages"]
        for name in ("numpy", "scipy", "pandas", "statsmodels", "arch", "matplotlib",
                     "pyarrow", "psutil", "joblib", "yaml", "tabulate"):
            assert name in packages, name
            assert packages[name] != "not installed", name
