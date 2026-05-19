"""
Kafka Producer for HealthTrace Data Streaming
==============================================
Handles publishing of environmental and health data to Kafka topics.

Topic design (aligned with D2.RI architecture):
  environmental-ingestion-air    — ARPAC air quality, batch/ETL, key=istat_code
  environmental-ingestion-meteo  — MeteoHub meteorological, batch/ETL, key=istat_code
  environmental-realtime-air     — ARPAC near-realtime alerts, key=istat_code
  environmental-realtime-meteo   — MeteoHub near-realtime alerts, key=istat_code
  health-data                    — Disease cases, key=comune_inizio_sintomi_codice_istat
  analytics_trigger              — Threshold breach alerts → AI engine

All timestamps are explicit UTC ISO-8601.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from kafka import KafkaProducer
from kafka.errors import KafkaError

# Allow running standalone (outside the FastAPI app) by gracefully importing settings
try:
    from app.core.config import settings as _settings

    KAFKA_BOOTSTRAP = _settings.KAFKA_BOOTSTRAP_SERVERS
    TOPIC_INGESTION_AIR = _settings.KAFKA_TOPIC_INGESTION_AIR
    TOPIC_INGESTION_METEO = _settings.KAFKA_TOPIC_INGESTION_METEO
    TOPIC_REALTIME_AIR = _settings.KAFKA_TOPIC_REALTIME_AIR
    TOPIC_REALTIME_METEO = _settings.KAFKA_TOPIC_REALTIME_METEO
    TOPIC_HEALTH = _settings.KAFKA_TOPIC_HEALTH
except ImportError:
    KAFKA_BOOTSTRAP = "localhost:9092"
    TOPIC_INGESTION_AIR = "environmental-ingestion-air"
    TOPIC_INGESTION_METEO = "environmental-ingestion-meteo"
    TOPIC_REALTIME_AIR = "environmental-realtime-air"
    TOPIC_REALTIME_METEO = "environmental-realtime-meteo"
    TOPIC_HEALTH = "health-data"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


class EnvironmentalDataProducer:
    """Thin wrapper around KafkaProducer for HealthTrace data publishing."""

    def __init__(self, bootstrap_servers: Optional[str] = None):
        servers = (bootstrap_servers or KAFKA_BOOTSTRAP).split(",")
        self.producer = KafkaProducer(
            bootstrap_servers=servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",
            retries=5,
            retry_backoff_ms=1000,
            max_block_ms=30_000,
        )

    # ── Internal ──────────────────────────────────────────────────────────────

    def _send(self, topic: str, key: Optional[str], payload: Dict[str, Any]) -> bool:
        try:
            future = self.producer.send(topic, value=payload, key=key)
            future.get(timeout=15)
            logger.info("Sent to topic=%s key=%s", topic, key)
            return True
        except KafkaError as exc:
            logger.error("KafkaError topic=%s: %s", topic, exc)
            return False
        except Exception as exc:
            logger.error("Unexpected error topic=%s: %s", topic, exc)
            return False

    # ── Public API ────────────────────────────────────────────────────────────

    def send_arpac_ingestion(
        self,
        data: Dict[str, Any],
        key: Optional[str] = None,
    ) -> bool:
        """
        Publish an ARPAC air-quality measurement to the ingestion topic.
        Partition key: istat_code.
        """
        istat_code = key or data.get("istat_code")
        payload = {
            "timestamp": _now_utc(),
            "data_type": "environmental_air",
            "source": "ARPAC",
            "payload": data,
        }
        return self._send(TOPIC_INGESTION_AIR, istat_code, payload)

    def send_meteohub_ingestion(
        self,
        data: Dict[str, Any],
        key: Optional[str] = None,
    ) -> bool:
        """
        Publish a MeteoHub meteorological measurement to the ingestion topic.
        Partition key: istat_code.
        """
        istat_code = key or data.get("istat_code")
        payload = {
            "timestamp": _now_utc(),
            "data_type": "environmental_meteo",
            "source": "METEOHUB",
            "payload": data,
        }
        return self._send(TOPIC_INGESTION_METEO, istat_code, payload)

    def send_arpac_realtime(
        self,
        data: Dict[str, Any],
        key: Optional[str] = None,
    ) -> bool:
        """Publish a near-realtime ARPAC reading for threshold evaluation."""
        istat_code = key or data.get("istat_code")
        payload = {
            "timestamp": _now_utc(),
            "data_type": "environmental_air_realtime",
            "source": "ARPAC",
            "payload": data,
        }
        return self._send(TOPIC_REALTIME_AIR, istat_code, payload)

    def send_meteohub_realtime(
        self,
        data: Dict[str, Any],
        key: Optional[str] = None,
    ) -> bool:
        """Publish a near-realtime MeteoHub reading for threshold evaluation."""
        istat_code = key or data.get("istat_code")
        payload = {
            "timestamp": _now_utc(),
            "data_type": "environmental_meteo_realtime",
            "source": "METEOHUB",
            "payload": data,
        }
        return self._send(TOPIC_REALTIME_METEO, istat_code, payload)

    def send_health_data(
        self,
        data: Dict[str, Any],
        key: Optional[str] = None,
    ) -> bool:
        """
        Publish a disease case notification to the health-data topic.

        Partition key: comune_inizio_sintomi_codice_istat (NOT patient_id).
        Keying by comune ensures disease cases from the same comune land on the
        same partition as environmental data, enabling efficient correlation.
        """
        istat_code = key or data.get("comune_inizio_sintomi_codice_istat")
        payload = {
            "timestamp": _now_utc(),
            "data_type": "health",
            "source": "gesan_malattie_infettive",
            "payload": data,
        }
        return self._send(TOPIC_HEALTH, istat_code, payload)

    def close(self) -> None:
        if self.producer:
            self.producer.flush()
            self.producer.close()


# ── Module-level singleton ─────────────────────────────────────────────────────
producer = EnvironmentalDataProducer()
