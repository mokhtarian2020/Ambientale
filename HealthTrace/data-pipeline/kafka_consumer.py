"""
Kafka Consumer — Environmental & Realtime Alert Flows
======================================================

Two independent consumer threads:

  1. IngestionConsumer  — flusso analitico (batch)
       Reads from:  environmental-ingestion-air
                    environmental-ingestion-meteo
       Action:      Collects all station messages for the same (istat_code, date),
                    applies Inverse Distance Weighting (IDW) to produce a single
                    value per parameter per comune per day, and writes to the
                    PostgreSQL DWH table `environmental_daily_aggregated`.

  2. RealtimeAlertConsumer  — flusso rapido (near-realtime)
       Reads from:  environmental-realtime-air
                    environmental-realtime-meteo
       Action:      Evaluates threshold rules; if any parameter breaches a
                    configured threshold, emits an alert to the
                    `analytics_trigger` topic for the AI engine.

All partition keys are istat_code so that data for the same comune lands on
the same partition and consumers can correlate without cross-partition joins.
"""

import json
import logging
import math
import threading
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)

INVALID_VALUE = -9999.0

# Allow running standalone without the FastAPI app
try:
    from app.core.config import settings as _settings
    TOPIC_ANALYTICS_TRIGGER: str = _settings.KAFKA_TOPIC_ANALYTICS_TRIGGER
except ImportError:
    TOPIC_ANALYTICS_TRIGGER: str = "analytics_trigger"

# ── Realtime alert thresholds ─────────────────────────────────────────────────
# Parameter name → (warning_threshold, unit)
ALERT_THRESHOLDS: Dict[str, Tuple[float, str]] = {
    "NO2":           (200.0, "μg/m³"),    # EU limit value
    "PM10":          (50.0,  "μg/m³"),    # EU daily limit
    "PM2.5":         (25.0,  "μg/m³"),    # EU annual limit (daily proxy)
    "O3":            (120.0, "μg/m³"),    # EU 8-hour target
    "SO2":           (350.0, "μg/m³"),    # EU hourly limit
    "temperature":   (35.0,  "°C"),       # heat-wave proxy
    "relative_humidity": (90.0, "%"),     # mould/legionella risk proxy
}


# ── IDW helper ─────────────────────────────────────────────────────────────────

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def idw_aggregate(
    readings: List[Dict[str, Any]],
    target_lat: float,
    target_lon: float,
    power: float = 2.0,
) -> Dict[str, float]:
    """
    Given a list of station readings (each with lat, lon and parameters),
    compute IDW-weighted mean for every parameter.
    Returns {parameter_name: weighted_mean}.
    """
    # Group values by parameter
    param_values: Dict[str, List[Tuple[float, float]]] = defaultdict(list)  # param → [(value, weight)]

    for reading in readings:
        lat = reading.get("latitude")
        lon = reading.get("longitude")
        if lat is None or lon is None:
            continue
        dist = haversine_km(target_lat, target_lon, lat, lon)
        if dist < 0.001:
            dist = 0.001  # avoid division by zero for co-located points
        weight = 1.0 / (dist ** power)

        for param in reading.get("parameters", []):
            mean_val = param.get("mean")
            if mean_val is None or mean_val == INVALID_VALUE:
                continue
            param_values[param["parameter"]].append((mean_val, weight))

    aggregated: Dict[str, float] = {}
    for param_name, vw_list in param_values.items():
        total_weight = sum(w for _, w in vw_list)
        if total_weight == 0:
            continue
        aggregated[param_name] = round(
            sum(v * w for v, w in vw_list) / total_weight, 4
        )
    return aggregated


# ── Database writer ────────────────────────────────────────────────────────────

class AggregationWriter:
    """Writes IDW-aggregated daily environmental data to PostgreSQL."""

    def __init__(self, db_url: str):
        try:
            from sqlalchemy import create_engine, text
            self._engine = create_engine(db_url, pool_pre_ping=True)
            self._text = text
            logger.info("AggregationWriter connected to DB.")
        except Exception as exc:
            logger.warning("DB connection failed (writes disabled): %s", exc)
            self._engine = None

    def upsert(
        self,
        istat_code: str,
        source: str,
        period_date: str,
        aggregated: Dict[str, float],
        station_count: int,
    ) -> None:
        if self._engine is None:
            logger.debug("DB unavailable — aggregation: %s %s %s", istat_code, source, period_date)
            return
        try:
            with self._engine.begin() as conn:
                conn.execute(
                    self._text("""
                        INSERT INTO environmental_daily_aggregated
                            (istat_code, source, period_date, parameters, station_count, created_at)
                        VALUES
                            (:istat_code, :source, :period_date, :parameters::jsonb,
                             :station_count, NOW())
                        ON CONFLICT (istat_code, source, period_date)
                        DO UPDATE SET
                            parameters    = EXCLUDED.parameters,
                            station_count = EXCLUDED.station_count,
                            updated_at    = NOW()
                    """),
                    {
                        "istat_code":    istat_code,
                        "source":        source,
                        "period_date":   period_date,
                        "parameters":    json.dumps(aggregated),
                        "station_count": station_count,
                    },
                )
        except Exception as exc:
            logger.error("DB upsert failed for %s/%s: %s", istat_code, period_date, exc)


# ── Ingestion consumer ─────────────────────────────────────────────────────────

class IngestionConsumer:
    """
    Consumes environmental-ingestion-air and environmental-ingestion-meteo,
    buffers messages per (istat_code, date, source), applies IDW, writes to DB.
    """

    def __init__(
        self,
        bootstrap_servers: str,
        db_url: str,
        group_id: str = "healthtrace-ingestion-group",
        topics: Optional[List[str]] = None,
        istat_centroids: Optional[Dict[str, Tuple[float, float]]] = None,
    ):
        self._topics = topics or [
            "environmental-ingestion-air",
            "environmental-ingestion-meteo",
        ]
        self._writer = AggregationWriter(db_url)
        # istat_code → (lat, lon) of comune centroid — used as IDW target
        # Falls back to simple mean if centroid unknown.
        self._centroids: Dict[str, Tuple[float, float]] = istat_centroids or {}

        self._consumer = KafkaConsumer(
            *self._topics,
            bootstrap_servers=bootstrap_servers.split(","),
            group_id=group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda b: json.loads(b.decode("utf-8")),
            key_deserializer=lambda b: b.decode("utf-8") if b else None,
            consumer_timeout_ms=5000,
        )

        # Buffer: (istat_code, date_str, source) → [station_payload, ...]
        self._buffer: Dict[Tuple[str, str, str], List[Dict]] = defaultdict(list)
        self._stop_event = threading.Event()

    def _flush_buffer(self) -> None:
        for (istat_code, period_date, source), readings in self._buffer.items():
            if not readings:
                continue
            centroid = self._centroids.get(istat_code)
            if centroid:
                aggregated = idw_aggregate(readings, centroid[0], centroid[1])
            else:
                # Simple mean fallback
                aggregated = _simple_mean_aggregate(readings)

            self._writer.upsert(istat_code, source, period_date, aggregated, len(readings))
            logger.info(
                "Aggregated istat=%s source=%s date=%s stations=%d params=%s",
                istat_code, source, period_date, len(readings), list(aggregated.keys()),
            )
        self._buffer.clear()

    def run(self) -> None:
        logger.info("IngestionConsumer started on topics: %s", self._topics)
        try:
            while not self._stop_event.is_set():
                for msg in self._consumer:
                    payload: Dict = msg.value
                    istat_code = payload.get("istat_code") or msg.key
                    source = payload.get("source", "UNKNOWN")
                    period_start = payload.get("period_start", "")
                    period_date = period_start[:10]  # YYYY-MM-DD
                    if istat_code:
                        self._buffer[(istat_code, period_date, source)].append(payload)

                # Flush after each poll cycle (consumer_timeout triggers here)
                self._flush_buffer()
        except Exception as exc:
            logger.error("IngestionConsumer error: %s", exc)
        finally:
            self._consumer.close()
            logger.info("IngestionConsumer stopped.")

    def stop(self) -> None:
        self._stop_event.set()

    def start_background(self) -> threading.Thread:
        t = threading.Thread(target=self.run, daemon=True, name="kafka-ingestion-consumer")
        t.start()
        return t


def _simple_mean_aggregate(readings: List[Dict]) -> Dict[str, float]:
    """Arithmetic mean fallback when no centroid is available."""
    param_sums: Dict[str, List[float]] = defaultdict(list)
    for reading in readings:
        for param in reading.get("parameters", []):
            mean_val = param.get("mean")
            if mean_val is not None and mean_val != INVALID_VALUE:
                param_sums[param["parameter"]].append(mean_val)
    return {
        p: round(sum(vals) / len(vals), 4)
        for p, vals in param_sums.items()
        if vals
    }


# ── Realtime alert consumer ────────────────────────────────────────────────────

class RealtimeAlertConsumer:
    """
    Consumes environmental-realtime-air and environmental-realtime-meteo.
    Evaluates threshold rules and publishes alerts to analytics_trigger.
    """

    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str = "healthtrace-realtime-group",
        topics: Optional[List[str]] = None,
        thresholds: Optional[Dict[str, Tuple[float, str]]] = None,
    ):
        self._topics = topics or [
            "environmental-realtime-air",
            "environmental-realtime-meteo",
        ]
        self._thresholds = thresholds or ALERT_THRESHOLDS

        self._consumer = KafkaConsumer(
            *self._topics,
            bootstrap_servers=bootstrap_servers.split(","),
            group_id=group_id,
            auto_offset_reset="latest",   # only new messages for realtime
            enable_auto_commit=True,
            value_deserializer=lambda b: json.loads(b.decode("utf-8")),
            key_deserializer=lambda b: b.decode("utf-8") if b else None,
        )
        self._producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers.split(","),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            acks=1,
        )
        self._stop_event = threading.Event()

    def _evaluate_thresholds(self, payload: Dict) -> List[Dict]:
        alerts = []
        istat_code = payload.get("istat_code")
        for param in payload.get("parameters", []):
            param_name = param.get("parameter")
            value = param.get("mean") or param.get("value")
            if value is None or value == INVALID_VALUE:
                continue
            if param_name in self._thresholds:
                threshold, unit = self._thresholds[param_name]
                if float(value) > threshold:
                    alerts.append({
                        "istat_code":  istat_code,
                        "parameter":   param_name,
                        "value":       value,
                        "unit":        unit,
                        "threshold":   threshold,
                        "source":      payload.get("source"),
                        "station_id":  payload.get("station_id"),
                        "timestamp":   payload.get("timestamp") or datetime.now(timezone.utc).isoformat(),
                        "alert_type":  "ENVIRONMENTAL_THRESHOLD_BREACH",
                    })
        return alerts

    def run(self) -> None:
        logger.info("RealtimeAlertConsumer started on topics: %s", self._topics)
        try:
            for msg in self._consumer:
                if self._stop_event.is_set():
                    break
                payload: Dict = msg.value
                istat_code = payload.get("istat_code") or msg.key
                alerts = self._evaluate_thresholds(payload)
                for alert in alerts:
                    logger.warning(
                        "ALERT istat=%s param=%s value=%s > threshold=%s",
                        istat_code, alert["parameter"], alert["value"], alert["threshold"],
                    )
                    self._producer.send(
                        TOPIC_ANALYTICS_TRIGGER,
                        key=istat_code,
                        value=alert,
                    )
                if alerts:
                    self._producer.flush()
        except Exception as exc:
            logger.error("RealtimeAlertConsumer error: %s", exc)
        finally:
            self._consumer.close()
            self._producer.close()
            logger.info("RealtimeAlertConsumer stopped.")

    def stop(self) -> None:
        self._stop_event.set()

    def start_background(self) -> threading.Thread:
        t = threading.Thread(target=self.run, daemon=True, name="kafka-realtime-consumer")
        t.start()
        return t


# ── Health data consumer ───────────────────────────────────────────────────────

class HealthDataConsumer:
    """
    Consumes the health-data topic (disease case notifications).
    Partition key: comune_inizio_sintomi_codice_istat.
    Writes to the local HealthTrace DB for correlation with environmental data.
    """

    def __init__(
        self,
        bootstrap_servers: str,
        db_url: str,
        group_id: str = "healthtrace-health-group",
    ):
        self._writer = AggregationWriter(db_url)
        self._consumer = KafkaConsumer(
            "health-data",
            bootstrap_servers=bootstrap_servers.split(","),
            group_id=group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda b: json.loads(b.decode("utf-8")),
            key_deserializer=lambda b: b.decode("utf-8") if b else None,
        )
        self._stop_event = threading.Event()

    def run(self) -> None:
        logger.info("HealthDataConsumer started.")
        try:
            for msg in self._consumer:
                if self._stop_event.is_set():
                    break
                payload: Dict = msg.value
                istat_code = msg.key or payload.get("comune_inizio_sintomi_codice_istat")
                disease = payload.get("malattia") or payload.get("disease")
                onset = payload.get("data_inizio_sintomi")
                logger.debug("Health event istat=%s disease=%s onset=%s", istat_code, disease, onset)
                # Future: upsert into healthtrace.disease_cases for correlation
        except Exception as exc:
            logger.error("HealthDataConsumer error: %s", exc)
        finally:
            self._consumer.close()

    def stop(self) -> None:
        self._stop_event.set()

    def start_background(self) -> threading.Thread:
        t = threading.Thread(target=self.run, daemon=True, name="kafka-health-consumer")
        t.start()
        return t
