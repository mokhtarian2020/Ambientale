"""
Environmental Ingestion Service
================================
Runs as a scheduled batch job (daily or hourly).

For each valid station in the registry it:
  1. Calls Valerio's _stat endpoints (POST with JSON body) with:
       - filter_on_range=true   → server-side range filtering
       - validated=true          → ARPAC only, validated readings
       - stats=["min","mean","max"]
  2. Parses the actual response structure:
       stations[] → sensors[] → data: {min, mean, max}
  3. Discards any value that is still -9999 client-side
     (PDF confirms filter_on_range does NOT prevent -9999 from polluting means
      when a single invalid point exists in the window — see IT2227A example).
  4. Normalises units and parameter names to canonical form.
  5. Publishes one Kafka message per station per day:
       - ARPAC  → topic  environmental-ingestion-air
       - MeteoHub → topic  environmental-ingestion-meteo
     Partition key for both: istat_code

Note on slm:
  - ARPAC stations: slm field is present in the API response — no SRTM needed.
  - MeteoHub stations: slm NOT in response (elev_ref is sensor-level, not altitude)
    → must be enriched via SRTM for MeteoHub only.

Run manually:
    python environmental_ingestion_service.py --date 2024-01-15
"""

import argparse
import json
import logging
import sys
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import requests
from kafka import KafkaProducer

from station_census_service import get_valid_stations, load_station_registry, build_station_registry

logger = logging.getLogger(__name__)

# ── Unit normalisation ─────────────────────────────────────────────────────────
# All unit variants found in the API → (canonical_unit, multiply_factor)
# factor=None means special conversion (handled inline)
UNIT_NORMALISATION: Dict[str, tuple] = {
    # ARPAC — both µ (U+00B5) and μ (U+03BC) variants present in API responses
    "µg/m**3":  ("μg/m³", 1.0),
    "μg/m**3":  ("μg/m³", 1.0),
    "ug/m3":    ("μg/m³", 1.0),
    "µg/m³":    ("μg/m³", 1.0),
    "mg/m**3":  ("μg/m³", 1000.0),
    "mg/m3":    ("μg/m³", 1000.0),
    "ppb":      ("ppb",   1.0),
    "ppm":      ("ppb",   1000.0),
    # MeteoHub
    "K":         ("°C",  None),    # subtract 273.15
    "°C":        ("°C",  1.0),
    "%":         ("%",   1.0),
    "hPa":       ("hPa", 1.0),
    "Pa":        ("hPa", 0.01),
    "m/s":       ("m/s", 1.0),
    "km/h":      ("m/s", 1.0 / 3.6),
    "kg/m**2":   ("mm",  1.0),     # 1 kg/m² ≡ 1 mm precipitation
    "kg/m2":     ("mm",  1.0),
    "mm":        ("mm",  1.0),
    "W/m**2":    ("W/m²", 1.0),
    "W/m2":      ("W/m²", 1.0),
    "J/m**2":    ("J/m²", 1.0),
    "deg":       ("°",   1.0),
}

# Normalise Italian comma in parameter names: "PM2,5" → "PM2.5"
def _normalise_param_name(name: str) -> str:
    if not name:
        return name
    return name.replace(",", ".").strip()

INVALID_VALUE = -9999.0
INVALID_THRESHOLD = -999.0   # anything below this is treated as invalid


def _is_invalid(value: Any) -> bool:
    """Return True if the value is a -9999 sentinel or below the safety threshold."""
    if value is None:
        return True
    try:
        f = float(value)
        return f <= INVALID_THRESHOLD
    except (TypeError, ValueError):
        return True


def normalise_value(value: float, raw_unit: str) -> tuple:
    """Returns (normalised_value, canonical_unit) or (None, raw_unit) if invalid."""
    if _is_invalid(value):
        return None, raw_unit
    unit_key = raw_unit.strip()
    if unit_key not in UNIT_NORMALISATION:
        return round(value, 3), raw_unit
    canonical_unit, factor = UNIT_NORMALISATION[unit_key]
    if factor is None:
        return round(value - 273.15, 3), canonical_unit
    return round(value * factor, 3), canonical_unit


def _safe_norm(val: Any, raw_unit: str) -> Optional[float]:
    if _is_invalid(val):
        return None
    result, _ = normalise_value(float(val), raw_unit)
    return result


# ── Kafka producer factory ─────────────────────────────────────────────────────

def make_kafka_producer(bootstrap_servers: str) -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers.split(","),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
        acks="all",
        retries=5,
        max_block_ms=30_000,
    )


# ── Response parser — actual API structure ─────────────────────────────────────
#
# The _stat endpoints return a list of station objects:
#   [
#     {
#       "station_id": "...",
#       "istat_code": "063049",
#       "type": "FONDO",          ← ARPAC only
#       "slm": 42.0,              ← ARPAC only (already provided — no SRTM needed)
#       "latitude": 40.85,
#       "longitude": 14.27,
#       "sensors": [
#         {
#           "alias": "NO2",       ← ARPAC: parameter name; MeteoHub: BUFR code
#           "parameter": "NO2",   ← human-readable name (use this)
#           "unit": "µg/m**3",
#           "data": { "min": 9.11, "mean": 24.95, "max": 43.48 }
#         }, ...
#       ],
#       "source": "ARPAC"
#     }, ...
#   ]

def parse_stat_response(
    station_objects: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Flatten the API response into a list of per-station parameter records.
    Returns [{station_id, istat_code, latitude, longitude, slm, source,
              station_type, parameters: [{parameter, mean, min, max, unit}]}]
    """
    parsed = []
    for station in station_objects:
        istat_code = station.get("istat_code")
        if not istat_code:
            continue

        sensors = station.get("sensors", [])
        if not sensors:
            continue

        parameters = []
        for sensor in sensors:
            raw_unit = sensor.get("unit", "")
            param_name = _normalise_param_name(sensor.get("parameter") or sensor.get("alias", ""))
            data = sensor.get("data", {})

            mean_val = data.get("mean")
            min_val  = data.get("min")
            max_val  = data.get("max")

            # Client-side -9999 guard (filter_on_range can still leak into aggregates)
            if _is_invalid(mean_val):
                logger.debug("Skipping sensor %s station %s: mean=%s is invalid",
                             param_name, station.get("station_id"), mean_val)
                continue

            norm_mean, canon_unit = normalise_value(float(mean_val), raw_unit)
            if norm_mean is None:
                continue

            parameters.append({
                "parameter": param_name,
                "mean":      norm_mean,
                "min":       _safe_norm(min_val, raw_unit),
                "max":       _safe_norm(max_val, raw_unit),
                "unit":      canon_unit,
            })

        if not parameters:
            continue

        parsed.append({
            "station_id":   station.get("station_id"),
            "istat_code":   istat_code,
            "latitude":     station.get("latitude"),
            "longitude":    station.get("longitude"),
            "slm":          station.get("slm"),          # present for ARPAC, None for MeteoHub
            "station_type": station.get("type"),         # ARPAC only
            "source":       station.get("source"),
            "parameters":   parameters,
        })

    return parsed


# ── ARPAC ingestion (POST, by istat_code) ─────────────────────────────────────

def ingest_arpac_by_istat(
    istat_code: str,
    target_date: date,
    valerio_base_url: str,
    producer: KafkaProducer,
    topic: str,
    allowed_types: Optional[List[str]] = None,
    max_elevation_m: float = 500.0,
) -> int:
    """
    Fetch daily statistics for ALL ARPAC stations in a comune and publish to Kafka.
    Queries by istat_code — no need to iterate station-by-station.
    Returns the number of messages published.
    """
    if allowed_types is None:
        allowed_types = ["FONDO", "TRAFFICO"]

    body = {
        "istat_code": istat_code,
        "start_timestamp": f"{target_date.isoformat()}T00:00:00+00:00",
        "end_timestamp":   f"{target_date.isoformat()}T23:59:59+00:00",
        "validated": True,
        "filter_on_range": True,
        "stats": ["min", "mean", "max"],
    }

    try:
        resp = requests.post(
            f"{valerio_base_url}/arpac/data/arpac_data_stat",
            json=body,
            timeout=30,
        )
        resp.raise_for_status()
        station_objects = resp.json()
    except Exception as exc:
        logger.error("ARPAC istat=%s fetch failed: %s", istat_code, exc)
        return 0

    stations = parse_stat_response(station_objects)
    published = 0

    for station in stations:
        # Filter by type and elevation (slm present in ARPAC response)
        stype = station.get("station_type")
        if stype and stype not in allowed_types:
            continue
        slm = station.get("slm")
        if slm is not None and slm > max_elevation_m:
            continue

        payload = {
            "source":       "ARPAC",
            "station_id":   station["station_id"],
            "istat_code":   istat_code,
            "station_type": station.get("station_type"),
            "slm":          slm,
            "latitude":     station.get("latitude"),
            "longitude":    station.get("longitude"),
            "period_start": f"{target_date.isoformat()}T00:00:00+00:00",
            "period_end":   f"{(target_date + timedelta(days=1)).isoformat()}T00:00:00+00:00",
            "aggregation":  "daily",
            "parameters":   station["parameters"],
            "ingested_at":  datetime.now(timezone.utc).isoformat(),
        }
        producer.send(topic, key=istat_code, value=payload)
        published += 1

    return published


# ── MeteoHub ingestion (POST, by istat_code) ──────────────────────────────────

def ingest_meteohub_by_istat(
    istat_code: str,
    target_date: date,
    valerio_base_url: str,
    producer: KafkaProducer,
    topic: str,
    station_elevations: Optional[Dict[str, float]] = None,
    max_elevation_m: float = 500.0,
) -> int:
    """
    Fetch daily statistics for ALL MeteoHub stations in a comune and publish to Kafka.
    MeteoHub has no slm — elevations must be supplied from the SRTM registry.
    station_elevations: {station_id: slm_metres}
    """
    body = {
        "istat_code": istat_code,
        "start_timestamp": f"{target_date.isoformat()}T00:00:00+00:00",
        "end_timestamp":   f"{target_date.isoformat()}T23:59:59+00:00",
        "filter_on_range": True,
        "stats": ["min", "mean", "max"],
    }

    try:
        resp = requests.post(
            f"{valerio_base_url}/meteohub/data/meteohub_data_stats",
            json=body,
            timeout=30,
        )
        resp.raise_for_status()
        station_objects = resp.json()
    except Exception as exc:
        logger.error("MeteoHub istat=%s fetch failed: %s", istat_code, exc)
        return 0

    stations = parse_stat_response(station_objects)
    published = 0

    for station in stations:
        # Look up elevation from SRTM registry (built by station_census_service)
        slm = (station_elevations or {}).get(station["station_id"]) or station.get("slm")
        if slm is not None and slm > max_elevation_m:
            continue

        payload = {
            "source":      "METEOHUB",
            "station_id":  station["station_id"],
            "istat_code":  istat_code,
            "slm":         slm,
            "latitude":    station.get("latitude"),
            "longitude":   station.get("longitude"),
            "period_start": f"{target_date.isoformat()}T00:00:00+00:00",
            "period_end":   f"{(target_date + timedelta(days=1)).isoformat()}T00:00:00+00:00",
            "aggregation": "daily",
            "parameters":  station["parameters"],
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }
        producer.send(topic, key=istat_code, value=payload)
        published += 1

    return published


# ── Main ingestion run ─────────────────────────────────────────────────────────

def run_ingestion(
    target_date: date,
    valerio_base_url: str = "http://localhost:7600",
    kafka_bootstrap: str = "localhost:9092",
    topic_air: str = "environmental-ingestion-air",
    topic_meteo: str = "environmental-ingestion-meteo",
    rebuild_registry: bool = False,
    max_elevation_m: float = 500.0,
) -> Dict[str, int]:
    """
    Run one full ingestion cycle for `target_date`.
    Iterates over all target istat_codes and queries the API once per comune
    (instead of once per station) — more efficient.
    """
    registry = None if rebuild_registry else load_station_registry()
    if registry is None:
        logger.info("Building station registry…")
        registry = build_station_registry(valerio_base_url)

    # Build MeteoHub elevation map: {station_id: slm} from SRTM registry
    meteo_elevations: Dict[str, float] = {
        s["station_id"]: s["slm"]
        for s in registry.get("meteohub", [])
        if s.get("slm") is not None
    }

    # Collect unique istat_codes from both valid station sets
    arpac_istat_codes = {
        s["istat_code"]
        for s in get_valid_stations(registry, "arpac")
        if s.get("istat_code")
    }
    meteo_istat_codes = {
        s["istat_code"]
        for s in get_valid_stations(registry, "meteohub")
        if s.get("istat_code")
    }

    logger.info(
        "Ingesting date=%s | ARPAC comuni=%d | MeteoHub comuni=%d",
        target_date.isoformat(), len(arpac_istat_codes), len(meteo_istat_codes),
    )

    producer = make_kafka_producer(kafka_bootstrap)
    counts = {"arpac_published": 0, "meteo_published": 0}

    try:
        for istat_code in sorted(arpac_istat_codes):
            counts["arpac_published"] += ingest_arpac_by_istat(
                istat_code, target_date, valerio_base_url, producer, topic_air,
                max_elevation_m=max_elevation_m,
            )

        for istat_code in sorted(meteo_istat_codes):
            counts["meteo_published"] += ingest_meteohub_by_istat(
                istat_code, target_date, valerio_base_url, producer, topic_meteo,
                station_elevations=meteo_elevations,
                max_elevation_m=max_elevation_m,
            )

        producer.flush()
        logger.info("Ingestion complete for %s — %s", target_date.isoformat(), counts)
    finally:
        producer.close()

    return counts


# ── CLI entry-point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Run environmental data ingestion")
    parser.add_argument(
        "--date",
        default=(date.today() - timedelta(days=1)).isoformat(),
        help="Target date YYYY-MM-DD (default: yesterday)",
    )
    parser.add_argument("--rebuild-registry", action="store_true")
    parser.add_argument("--valerio-url", default="http://localhost:7600")
    parser.add_argument("--kafka", default="localhost:9092")
    parser.add_argument("--max-elevation", type=float, default=500.0)
    args = parser.parse_args()

    result = run_ingestion(
        target_date=date.fromisoformat(args.date),
        valerio_base_url=args.valerio_url,
        kafka_bootstrap=args.kafka,
        rebuild_registry=args.rebuild_registry,
        max_elevation_m=args.max_elevation,
    )
    print(json.dumps(result, indent=2))
    sys.exit(0)
