"""FRED/ALFRED retrieval.

Part 5 §2.2 requires every raw series to be fetched programmatically by stable series ID,
in raw units, at the 2026-10-05 historical vintage, with the API key read from the
environment. No manual CSV construction is permitted and the key is never written to
disk, to a log, or to any output.

The transport is injectable so the whole client can be exercised in tests without
touching the network (the default run must make no network call at all).
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

API_KEY_PARAM = "api_key"
_REDACTED = "<redacted>"


class RetrievalError(RuntimeError):
    """Raised when a series cannot be retrieved. Never swallowed."""


class Transport(Protocol):
    def __call__(self, url: str, timeout: int) -> bytes: ...


def _urllib_transport(url: str, timeout: int) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.read()


def api_key_from_env(env_var: str = "FRED_API_KEY") -> str:
    key = os.environ.get(env_var, "").strip()
    if not key:
        raise RetrievalError(
            f"{env_var} is not set. Part 5 §2.2 requires the FRED API key to come from "
            f"the environment; it must never be hard-coded or committed."
        )
    return key


def redact(params: dict[str, Any]) -> dict[str, Any]:
    """Request parameters with the API key removed, safe to store in a manifest."""
    return {k: (_REDACTED if k == API_KEY_PARAM else v) for k, v in params.items()}


@dataclass(frozen=True)
class Observation:
    date: str
    value: float | None
    #: The provider's value exactly as returned, including "." for a missing observation.
    #: Frozen files store this string, not a re-formatted float, so the snapshot is a
    #: faithful copy of the official record (decision T5).
    raw_value: str = ""
    realtime_start: str | None = None
    realtime_end: str | None = None

    @property
    def missing(self) -> bool:
        return self.value is None


@dataclass
class SeriesResponse:
    """Raw observations plus everything needed to reproduce the request."""

    series_id: str
    observations: list[Observation]
    request_params: dict[str, Any]          # already redacted
    request_url_redacted: str
    retrieved_utc: str
    raw_payload: dict[str, Any] = field(default_factory=dict)

    @property
    def n_rows(self) -> int:
        return len(self.observations)

    @property
    def first_date(self) -> str | None:
        return self.observations[0].date if self.observations else None

    @property
    def last_date(self) -> str | None:
        return self.observations[-1].date if self.observations else None

    @property
    def missing_dates(self) -> list[str]:
        return [obs.date for obs in self.observations if obs.missing]


@dataclass
class FredClient:
    api_key: str
    base_url: str = "https://api.stlouisfed.org/fred/series/observations"
    metadata_url: str = "https://api.stlouisfed.org/fred/series"
    timeout: int = 120
    max_retries: int = 3
    transport: Transport = _urllib_transport
    sleep: Callable[[float], None] = time.sleep

    def fetch_metadata(self, series_id: str) -> dict[str, Any]:
        """Series title, frequency, units and seasonal adjustment.

        Part 5 §2.2 requires these to be stored with every frozen file, and taking them
        from the provider rather than from my own notes keeps the manifest a record of
        the official description.
        """
        params = {
            "series_id": series_id,
            API_KEY_PARAM: self.api_key,
            "file_type": "json",
        }
        url = f"{self.metadata_url}?{urllib.parse.urlencode(params)}"
        redacted_url = f"{self.metadata_url}?{urllib.parse.urlencode(redact(params))}"
        payload = self._get_with_retries(url, series_id, redacted_url)
        entries = payload.get("seriess") or []
        if not entries:
            raise RetrievalError(f"{series_id}: no series metadata returned")
        return entries[0]

    def build_params(
        self,
        series_id: str,
        *,
        vintage_date: str | None = None,
        realtime: str | None = None,
        units: str = "lin",
    ) -> dict[str, Any]:
        """Build the request parameters.

        Exactly one of `vintage_date` (the primary form under decision T6) or `realtime`
        (the audit cross-check form) may be given. `units="lin"` keeps the provider from
        transforming anything: all transformations are computed locally from frozen raw
        levels (Part 5 §2.2).
        """
        if bool(vintage_date) == bool(realtime):
            raise ValueError("supply exactly one of vintage_date or realtime")
        params: dict[str, Any] = {
            "series_id": series_id,
            API_KEY_PARAM: self.api_key,
            "file_type": "json",
            "units": units,
        }
        if vintage_date:
            params["vintage_dates"] = vintage_date
        else:
            params["realtime_start"] = realtime
            params["realtime_end"] = realtime
        return params

    def fetch(
        self,
        series_id: str,
        *,
        vintage_date: str | None = None,
        realtime: str | None = None,
        units: str = "lin",
    ) -> SeriesResponse:
        params = self.build_params(
            series_id, vintage_date=vintage_date, realtime=realtime, units=units
        )
        url = f"{self.base_url}?{urllib.parse.urlencode(params)}"
        redacted_params = redact(params)
        redacted_url = f"{self.base_url}?{urllib.parse.urlencode(redacted_params)}"

        payload = self._get_with_retries(url, series_id, redacted_url)
        if "observations" not in payload:
            raise RetrievalError(
                f"{series_id}: response contained no observations "
                f"(request: {redacted_url})"
            )

        observations = [
            Observation(
                date=row["date"],
                value=None if row.get("value") in (".", "", None) else float(row["value"]),
                raw_value="" if row.get("value") is None else str(row["value"]),
                realtime_start=row.get("realtime_start"),
                realtime_end=row.get("realtime_end"),
            )
            for row in payload["observations"]
        ]
        meta = {k: v for k, v in payload.items() if k != "observations"}
        return SeriesResponse(
            series_id=series_id,
            observations=observations,
            request_params=redacted_params,
            request_url_redacted=redacted_url,
            retrieved_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            raw_payload=meta,
        )

    def _get_with_retries(self, url: str, series_id: str, redacted_url: str) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                body = self.transport(url, self.timeout)
                return json.loads(body)
            except urllib.error.HTTPError as exc:  # pragma: no cover - network path
                # A 400 from FRED means a bad request (e.g. unknown series or an invalid
                # vintage); retrying cannot help, so fail immediately and loudly.
                if 400 <= exc.code < 500:
                    raise RetrievalError(
                        f"{series_id}: FRED returned HTTP {exc.code} for {redacted_url}"
                    ) from exc
                last_error = exc
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
            if attempt < self.max_retries:
                self.sleep(2.0**attempt)
        raise RetrievalError(
            f"{series_id}: retrieval failed after {self.max_retries} attempts "
            f"({redacted_url}): {last_error!r}"
        )


def compare_responses(primary: SeriesResponse, audit: SeriesResponse) -> dict[str, Any]:
    """Compare the vintage_dates response with the realtime cross-check response.

    Decision T6 requires the two request forms to be compared and any material
    discrepancy to stop the run rather than be resolved silently. The comparison is
    value-by-value, not a summary check.
    """
    primary_map = {obs.date: obs.value for obs in primary.observations}
    audit_map = {obs.date: obs.value for obs in audit.observations}
    only_primary = sorted(set(primary_map) - set(audit_map))
    only_audit = sorted(set(audit_map) - set(primary_map))
    differing = sorted(
        date
        for date in set(primary_map) & set(audit_map)
        if not _same_value(primary_map[date], audit_map[date])
    )
    return {
        "series_id": primary.series_id,
        "identical": not (only_primary or only_audit or differing),
        "n_primary": primary.n_rows,
        "n_audit": audit.n_rows,
        "dates_only_in_primary": only_primary,
        "dates_only_in_audit": only_audit,
        "dates_with_different_values": differing,
    }


def _same_value(left: float | None, right: float | None) -> bool:
    if left is None or right is None:
        return left is right or (left is None and right is None)
    return left == right
