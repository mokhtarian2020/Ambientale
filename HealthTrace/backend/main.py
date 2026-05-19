import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api import api_router

logger = logging.getLogger(__name__)

# ── Kafka consumer threads ─────────────────────────────────────────────────────
# Imported lazily so the app still starts even when kafka-python is unavailable
# (e.g. in local dev without a Kafka broker).
_consumer_threads = []


def _start_kafka_consumers() -> None:
    try:
        # Add data-pipeline directory to path so consumers can be imported
        import os
        pipeline_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data-pipeline")
        if pipeline_dir not in sys.path:
            sys.path.insert(0, os.path.abspath(pipeline_dir))

        from kafka_consumer import IngestionConsumer, RealtimeAlertConsumer, HealthDataConsumer

        ingestion = IngestionConsumer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            db_url=settings.DATABASE_URL,
            topics=[
                settings.KAFKA_TOPIC_INGESTION_AIR,
                settings.KAFKA_TOPIC_INGESTION_METEO,
            ],
        )
        realtime = RealtimeAlertConsumer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            topics=[
                settings.KAFKA_TOPIC_REALTIME_AIR,
                settings.KAFKA_TOPIC_REALTIME_METEO,
            ],
        )
        health = HealthDataConsumer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            db_url=settings.DATABASE_URL,
        )

        _consumer_threads.append((ingestion, ingestion.start_background()))
        _consumer_threads.append((realtime, realtime.start_background()))
        _consumer_threads.append((health, health.start_background()))

        logger.info(
            "Kafka consumers started — ingestion: %s/%s | realtime: %s/%s | health: health-data",
            settings.KAFKA_TOPIC_INGESTION_AIR,
            settings.KAFKA_TOPIC_INGESTION_METEO,
            settings.KAFKA_TOPIC_REALTIME_AIR,
            settings.KAFKA_TOPIC_REALTIME_METEO,
        )
    except ImportError as exc:
        logger.warning("kafka-python not installed — consumers disabled: %s", exc)
    except Exception as exc:
        logger.error("Failed to start Kafka consumers (non-fatal): %s", exc)


def _stop_kafka_consumers() -> None:
    for consumer, thread in _consumer_threads:
        try:
            consumer.stop()
        except Exception:
            pass
    _consumer_threads.clear()


# ── FastAPI lifespan ──────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    _start_kafka_consumers()
    yield
    # Shutdown
    _stop_kafka_consumers()


# ── App factory ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="HealthTrace API",
    description="Environmental Health Monitoring and Correlation Analysis System",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    return {
        "message": "HealthTrace API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
