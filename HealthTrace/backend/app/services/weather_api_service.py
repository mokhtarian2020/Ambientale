"""
Weather / Environmental API Service
=====================================
HTTP client for Valerio's microservice.

IMPORTANT (from API document):
  - ALL data endpoints are POST with a JSON body, not GET.
  - /arpac_data_stat and /meteohub_data_stats require the `stats` field (mandatory).
  - ARPAC requests should include validated=true (default) and filter_on_range=true.
  - Timestamps must carry explicit timezone; we always request UTC (+00:00).
  - Spatial filter options: istat_code (AND), bbox, wkt, geojson — we use istat_code.

Endpoint reference:
  POST /arpac/data/arpac_data              — raw hourly time-series
  POST /arpac/data/arpac_data_stat         — aggregated statistics (requires stats=[])
  POST /meteohub/data/meteohub_data        — raw minute-level time-series
  POST /meteohub/data/meteohub_data_stats  — aggregated statistics (requires stats=[])
  GET  /arpac/stations                     — station list
  GET  /meteohub/stations                  — station list
"""

import logging
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


class ValeorioApiClient:
    """POST-based HTTP client for Valerio's environmental data microservice."""

    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        self._base = (base_url or settings.VALERIO_API_BASE_URL).rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    # ── Station lists (GET) ───────────────────────────────────────────────────

    def get_arpac_stations(self) -> List[Dict[str, Any]]:
        return self._get("/arpac/stations")

    def get_meteohub_stations(self) -> List[Dict[str, Any]]:
        return self._get("/meteohub/stations")

    # ── ARPAC raw time-series (POST) ──────────────────────────────────────────

    def get_arpac_data(
        self,
        istat_code: Optional[str] = None,
        station_id: Optional[str] = None,
        parameters: Optional[List[str]] = None,
        start_timestamp: Optional[datetime] = None,
        end_timestamp: Optional[datetime] = None,
        validated: bool = True,
        filter_on_range: bool = True,
    ) -> List[Dict[str, Any]]:
        body: Dict[str, Any] = {
            "validated": validated,
            "filter_on_range": filter_on_range,
        }
        if istat_code:
            body["istat_code"] = istat_code
        if station_id:
            body["station_id"] = station_id
        if parameters:
            body["parameter"] = parameters
        if start_timestamp:
            body["start_timestamp"] = start_timestamp.astimezone(timezone.utc).isoformat()
        if end_timestamp:
            body["end_timestamp"] = end_timestamp.astimezone(timezone.utc).isoformat()
        return self._post("/arpac/data/arpac_data", body)

    # ── ARPAC aggregated statistics (POST) ────────────────────────────────────

    def get_arpac_stat(
        self,
        istat_code: Optional[str] = None,
        station_id: Optional[str] = None,
        target_date: Optional[date] = None,
        parameters: Optional[List[str]] = None,
        stats: Optional[List[str]] = None,
        validated: bool = True,
        filter_on_range: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Returns aggregated statistics per station/sensor.
        `stats` is mandatory — defaults to ["min", "mean", "max"].
        """
        body: Dict[str, Any] = {
            "validated": validated,
            "filter_on_range": filter_on_range,
            "stats": stats or ["min", "mean", "max"],
        }
        if istat_code:
            body["istat_code"] = istat_code
        if station_id:
            body["station_id"] = station_id
        if parameters:
            body["parameter"] = parameters
        if target_date:
            body["start_timestamp"] = f"{target_date.isoformat()}T00:00:00+00:00"
            body["end_timestamp"] = f"{target_date.isoformat()}T23:59:59+00:00"
        return self._post("/arpac/data/arpac_data_stat", body)

    # ── MeteoHub raw time-series (POST) ───────────────────────────────────────

    def get_meteohub_data(
        self,
        istat_code: Optional[str] = None,
        station_id: Optional[str] = None,
        parameters: Optional[List[str]] = None,
        start_timestamp: Optional[datetime] = None,
        end_timestamp: Optional[datetime] = None,
        filter_on_range: bool = True,
    ) -> List[Dict[str, Any]]:
        body: Dict[str, Any] = {"filter_on_range": filter_on_range}
        if istat_code:
            body["istat_code"] = istat_code
        if station_id:
            body["station_id"] = station_id
        if parameters:
            body["parameter"] = parameters
        if start_timestamp:
            body["start_timestamp"] = start_timestamp.astimezone(timezone.utc).isoformat()
        if end_timestamp:
            body["end_timestamp"] = end_timestamp.astimezone(timezone.utc).isoformat()
        return self._post("/meteohub/data/meteohub_data", body)

    # ── MeteoHub aggregated statistics (POST) ─────────────────────────────────

    def get_meteohub_stat(
        self,
        istat_code: Optional[str] = None,
        station_id: Optional[str] = None,
        target_date: Optional[date] = None,
        parameters: Optional[List[str]] = None,
        stats: Optional[List[str]] = None,
        filter_on_range: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Returns aggregated statistics per station/sensor.
        `stats` is mandatory — defaults to ["min", "mean", "max"].
        MeteoHub has no `validated` field.
        """
        body: Dict[str, Any] = {
            "filter_on_range": filter_on_range,
            "stats": stats or ["min", "mean", "max"],
        }
        if istat_code:
            body["istat_code"] = istat_code
        if station_id:
            body["station_id"] = station_id
        if parameters:
            body["parameter"] = parameters
        if target_date:
            body["start_timestamp"] = f"{target_date.isoformat()}T00:00:00+00:00"
            body["end_timestamp"] = f"{target_date.isoformat()}T23:59:59+00:00"
        return self._post("/meteohub/data/meteohub_data_stats", body)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _post(self, path: str, body: Dict[str, Any]) -> Any:
        url = self._base + path
        try:
            resp = self._session.post(url, json=body, timeout=self._timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            logger.error("ValeorioApiClient POST %s failed: %s", url, exc)
            return []

    def _get(self, path: str, params: Optional[Dict] = None) -> Any:
        url = self._base + path
        try:
            resp = self._session.get(url, params=params, timeout=self._timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            logger.error("ValeorioApiClient GET %s failed: %s", url, exc)
            return []


# Module-level singleton
valerio_client = ValeorioApiClient()
