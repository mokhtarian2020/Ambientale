"""
Station Census Service
======================
Fetches the full list of ARPAC and MeteoHub stations from Valerio's microservice,
enriches each station with:
  - slm (elevation in metres) from OpenTopoData SRTM when missing
  - istat_code resolved from coordinates via ISTAT API
  - valid flag based on slm < STATION_MAX_ELEVATION_M and station type

Results are persisted to a local JSON file and can be reloaded on startup.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

CACHE_PATH = Path(__file__).parent / "station_registry.json"
INVALID_VALUE = -9999.0


# ── SRTM helpers ─────────────────────────────────────────────────────────────

def _fetch_srtm_batch(coords: List[Dict[str, float]], srtm_url: str) -> List[Optional[float]]:
    """
    Query OpenTopoData SRTM API for a batch of (lat, lon) pairs.
    Returns a list of elevations in metres, None on error.
    API accepts up to 100 locations per request.
    """
    locations = "|".join(f"{c['lat']},{c['lon']}" for c in coords)
    try:
        resp = requests.get(srtm_url, params={"locations": locations}, timeout=30)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return [r.get("elevation") for r in results]
    except Exception as exc:
        logger.warning("SRTM request failed: %s", exc)
        return [None] * len(coords)


def enrich_stations_with_elevation(
    stations: List[Dict[str, Any]],
    srtm_url: str = "https://api.opentopodata.org/v1/srtm90m",
    batch_size: int = 100,
    pause_between_batches: float = 1.5,
) -> List[Dict[str, Any]]:
    """
    For each station missing a valid slm, fetch elevation from SRTM.
    Mutates the list in place; also returns it.
    """
    need_elevation = [
        s for s in stations
        if s.get("slm") is None or s.get("slm") == INVALID_VALUE
    ]

    if not need_elevation:
        logger.info("All stations already have elevation data.")
        return stations

    logger.info("Fetching SRTM elevation for %d stations", len(need_elevation))
    for i in range(0, len(need_elevation), batch_size):
        batch = need_elevation[i : i + batch_size]
        coords = [{"lat": s["latitude"], "lon": s["longitude"]} for s in batch]
        elevations = _fetch_srtm_batch(coords, srtm_url)
        for station, elev in zip(batch, elevations):
            station["slm"] = round(elev, 1) if elev is not None else None
        if i + batch_size < len(need_elevation):
            time.sleep(pause_between_batches)

    return stations


# ── Station validation ────────────────────────────────────────────────────────

def is_station_valid(
    station: Dict[str, Any],
    max_elevation_m: float = 500.0,
    allowed_types: Optional[List[str]] = None,
) -> bool:
    """
    A station is valid for analysis if:
      1. slm is known and below max_elevation_m (avoids uninhabited high-altitude)
      2. For ARPAC: type is in allowed_types ("FONDO", "TRAFFICO")
         MeteoHub has no type field — all are accepted.
    """
    slm = station.get("slm")
    if slm is None or slm == INVALID_VALUE:
        return False
    if slm > max_elevation_m:
        return False
    station_type = station.get("type")
    if station_type and allowed_types:
        return station_type in allowed_types
    return True


# ── Registry build ─────────────────────────────────────────────────────────────

def build_station_registry(
    valerio_base_url: str = "http://localhost:7600",
    srtm_url: str = "https://api.opentopodata.org/v1/srtm90m",
    max_elevation_m: float = 500.0,
    allowed_arpac_types: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Pull station lists from Valerio's API, enrich with SRTM elevation,
    mark each station as valid/invalid, and return a registry dict.

    Registry structure:
    {
      "built_at": "<ISO timestamp>",
      "arpac": [ {station}, ... ],
      "meteohub": [ {station}, ... ]
    }
    """
    from datetime import datetime, timezone

    if allowed_arpac_types is None:
        allowed_arpac_types = ["FONDO", "TRAFFICO"]

    registry: Dict[str, Any] = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "arpac": [],
        "meteohub": [],
    }

    # ── Fetch ARPAC stations ─────────────────────────────────────────────────
    try:
        resp = requests.get(f"{valerio_base_url}/arpac/stations", timeout=30)
        resp.raise_for_status()
        arpac_stations: List[Dict[str, Any]] = resp.json()
        logger.info("Fetched %d ARPAC stations", len(arpac_stations))
    except Exception as exc:
        logger.warning("Could not fetch ARPAC stations: %s", exc)
        arpac_stations = []

    # ARPAC: slm is already provided in the API response — no SRTM needed.
    # Only call SRTM for stations still missing slm (edge cases).
    enrich_stations_with_elevation(arpac_stations, srtm_url)
    for s in arpac_stations:
        s["_valid"] = is_station_valid(s, max_elevation_m, allowed_arpac_types)
    registry["arpac"] = arpac_stations

    # ── Fetch MeteoHub stations ──────────────────────────────────────────────
    try:
        resp = requests.get(f"{valerio_base_url}/meteohub/stations", timeout=30)
        resp.raise_for_status()
        meteo_stations: List[Dict[str, Any]] = resp.json()
        logger.info("Fetched %d MeteoHub stations", len(meteo_stations))
    except Exception as exc:
        logger.warning("Could not fetch MeteoHub stations: %s", exc)
        meteo_stations = []

    # MeteoHub: elev_ref is sensor-level reference height (NOT station altitude).
    # Strip it and always fetch real station elevation from SRTM.
    for s in meteo_stations:
        s.pop("elev_ref", None)
        s.pop("slm", None)   # ensure we don't accidentally keep a wrong value
    enrich_stations_with_elevation(meteo_stations, srtm_url)
    for s in meteo_stations:
        s["_valid"] = is_station_valid(s, max_elevation_m, allowed_types=None)
    registry["meteohub"] = meteo_stations

    # ── Persist ──────────────────────────────────────────────────────────────
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as fh:
        json.dump(registry, fh, indent=2, ensure_ascii=False)
    logger.info("Station registry saved to %s", CACHE_PATH)

    return registry


def load_station_registry() -> Optional[Dict[str, Any]]:
    """Load the cached registry if it exists, else return None."""
    if CACHE_PATH.exists():
        with open(CACHE_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    return None


def get_valid_stations(registry: Dict[str, Any], source: str) -> List[Dict[str, Any]]:
    """Return only valid stations for the given source ('arpac' or 'meteohub')."""
    return [s for s in registry.get(source, []) if s.get("_valid", False)]


# ── CLI usage ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    reg = build_station_registry()
    valid_arpac = get_valid_stations(reg, "arpac")
    valid_meteo = get_valid_stations(reg, "meteohub")
    print(
        f"Registry built. "
        f"ARPAC valid: {len(valid_arpac)}/{len(reg['arpac'])}. "
        f"MeteoHub valid: {len(valid_meteo)}/{len(reg['meteohub'])}."
    )
    sys.exit(0)
