"""A workflow-wide guarantee that the R1 correction never estimates a model by accident.

`estimation_forbidden()` replaces every model-estimation entry point of the package
(`fit_ar`, `fit_arma`, `fit_msar`, `fit_star`, `fit_var`, `fit_arma_garch` and
`fit_and_forecast`) in every loaded `thesis` module that holds a reference to it, so a
call through any import path raises `EstimationForbidden`. The exception is not caught
anywhere in the rolling engine or the workflow, so an unexpected estimation stops the
run loudly instead of being recorded as a failed fit.

`allowed(reason)` lifts the guard for one explicitly approved block (an `--approve`d
chain), and counts how many estimations it permitted, so the record shows exactly where
new estimates came from.

The cache replay has its own, narrower refusal (`rescore._replay_from_cache`): a cache
miss there means "this chain is not complete in the cache", which is an expected outcome
and is turned into "unavailable", never into an estimate. This guard sits underneath it
and catches anything else.
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from dataclasses import dataclass, field

ESTIMATORS = ("fit_ar", "fit_arma", "fit_msar", "fit_star", "fit_var", "fit_arma_garch",
              "fit_and_forecast")


class EstimationForbidden(RuntimeError):
    """A model was about to be estimated outside an approved block."""


@dataclass
class _State:
    active: bool = False
    allowed_depth: int = 0
    permitted: dict[str, int] = field(default_factory=dict)
    originals: dict[tuple[str, str], object] = field(default_factory=dict)


STATE = _State()


def _targets():
    """(module, attribute, original function) for every estimator reference loaded."""
    originals = {}
    for module_name in ("thesis.models.ar", "thesis.models.arma", "thesis.models.msar",
                        "thesis.models.star", "thesis.models.var",
                        "thesis.models.arma_garch", "thesis.models.registry"):
        module = __import__(module_name, fromlist=["_"])
        for name in ESTIMATORS:
            if hasattr(module, name):
                originals[getattr(module, name)] = name
    found = []
    for module_name, module in list(sys.modules.items()):
        if not module_name.startswith("thesis.") or module is None:
            continue
        for attribute, value in list(vars(module).items()):
            if attribute in ESTIMATORS and value in originals:
                found.append((module, attribute, value))
    return found


def _guarded(name, original):
    def wrapper(*args, **kwargs):
        if STATE.allowed_depth > 0:
            STATE.permitted[name] = STATE.permitted.get(name, 0) + 1
            return original(*args, **kwargs)
        raise EstimationForbidden(
            f"{name} was called during an R1 correction run without approval; the "
            "workflow estimates nothing unless a chain is passed with --approve")
    wrapper.__wrapped__ = original
    wrapper.__name__ = getattr(original, "__name__", name)
    wrapper._r1_guard = True
    return wrapper


@contextmanager
def estimation_forbidden():
    """Forbid estimation everywhere in the package for the duration of the block."""
    if STATE.active:
        yield STATE
        return
    patched = []
    for module, attribute, original in _targets():
        setattr(module, attribute, _guarded(attribute, original))
        patched.append((module, attribute, original))
    STATE.active, STATE.permitted = True, {}
    try:
        yield STATE
    finally:
        for module, attribute, original in patched:
            setattr(module, attribute, original)
        STATE.active = False


@contextmanager
def allowed():
    """Permit estimation inside an explicitly approved block."""
    STATE.allowed_depth += 1
    try:
        yield
    finally:
        STATE.allowed_depth -= 1
