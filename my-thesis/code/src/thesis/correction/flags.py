"""Switches for the Part 8 corrections approved on 2 November 2026.

Every correction is ON by default, which is the approved behaviour of the pipeline. The
switches exist for one purpose: the R1 correction workflow first runs with every
correction OFF ("legacy" mode) and must then reproduce the original published tables of
run baseline-20261030T173044-949fcd76 exactly; only after that validation are the
corrections activated. Turning a switch off is never a way to produce thesis results.

* F1  -- a forecast from a fit with status `failed` is never scored (raw value kept in
         `failed_raw_forecast`); F3.4 diagnostic panel uses markers and the raw value.
* F2  -- numerically guarded Hansen-Lunde-Nason MCS when `arch` fails or overflows.
* F3  -- pairwise differentials in T3.3A/T3.3B follow the stated sign convention.
* F4  -- Zivot-Andrews reported on both rate-series levels (Part 5 §3.2, P-02).
* F7.1 -- T2.1 reports the §3.4 decision instead of "pending stationarity decision".

None of these modules is part of the fit-cache identity (`core/cache._FIT_CRITICAL`).
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, fields


@dataclass
class CorrectionFlags:
    f1_failed_forecast_masking: bool = True
    f2_guarded_mcs: bool = True
    f3_pairwise_orientation: bool = True
    f4_zivot_andrews_reporting: bool = True
    f71_data_dictionary_decision: bool = True
    # F8 (found in the R1 figure review, 2 November 2026; presentation only): F3.4's main
    # panel keeps the valid models readable (Part 5 §13.1 / outputs spec F3.4).
    f8_readable_main_panel: bool = True

    def as_dict(self) -> dict[str, bool]:
        return {f.name: getattr(self, f.name) for f in fields(self)}


ACTIVE = CorrectionFlags()


@contextmanager
def configured(**values: bool):
    """Temporarily set switches (used by the R1 workflow and its tests)."""
    previous = ACTIVE.as_dict()
    for name, value in values.items():
        if name not in previous:
            raise KeyError(f"unknown correction switch {name!r}")
        setattr(ACTIVE, name, bool(value))
    try:
        yield ACTIVE
    finally:
        for name, value in previous.items():
            setattr(ACTIVE, name, value)


@contextmanager
def legacy():
    """Every correction off: the behaviour that produced the original publication."""
    with configured(**{name: False for name in ACTIVE.as_dict()}) as flags:
        yield flags
