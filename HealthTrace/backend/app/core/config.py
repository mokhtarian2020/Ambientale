from typing import List, Union
from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "postgresql://healthtrace:password@localhost/healthtrace"

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # ── Kafka ────────────────────────────────────────────────────────────────
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    # Ingestion topics — one per source (ARPAC air quality / MeteoHub meteo)
    # Partition key for both: istat_code
    KAFKA_TOPIC_INGESTION_AIR: str = "environmental-ingestion-air"
    KAFKA_TOPIC_INGESTION_METEO: str = "environmental-ingestion-meteo"

    # Realtime alert topics — threshold breach notifications
    KAFKA_TOPIC_REALTIME_AIR: str = "environmental-realtime-air"
    KAFKA_TOPIC_REALTIME_METEO: str = "environmental-realtime-meteo"

    # Health data topic — disease case notifications (keyed by istat_code)
    KAFKA_TOPIC_HEALTH: str = "health-data"

    # Alert trigger topic — published by RealtimeAlertConsumer on threshold breach
    KAFKA_TOPIC_ANALYTICS_TRIGGER: str = "analytics_trigger"

    # ── External APIs (Valerio microservice) ─────────────────────────────────
    VALERIO_API_BASE_URL: str = "http://localhost:7600"
    ARPAC_DATA_STAT_PATH: str = "/arpac/data/arpac_data_stat"
    METEOHUB_DATA_STATS_PATH: str = "/meteohub/data/meteohub_data_stats"

    # ── SRTM elevation service ────────────────────────────────────────────────
    SRTM_API_URL: str = "https://api.opentopodata.org/v1/srtm90m"
    STATION_MAX_ELEVATION_M: float = 500.0   # stations above this are excluded

    # ── Station filter ────────────────────────────────────────────────────────
    ARPAC_ALLOWED_TYPES: List[str] = ["FONDO", "TRAFFICO"]

    # ── Target comuni (priority ISTAT codes for Campania / Napoli) ───────────
    TARGET_ISTAT_CODES: List[str] = [
        "063049",  # Napoli
        "063041",  # Marano di Napoli
        "063017",  # Casalnuovo di Napoli
        "063034",  # Giugliano in Campania
        "063023",  # Casoria
        "063089",  # Pozzuoli
        "061002",  # Caserta
        "065116",  # Salerno
    ]

    # ── Legacy / other ────────────────────────────────────────────────────────
    ISTAT_API_BASE_URL: str = "https://www.istat.it/api"
    ISPRA_API_BASE_URL: str = "https://indicatoriambientali.isprambiente.it/api"
    ARPA_CAMPANIA_API_BASE_URL: str = "https://dati.arpacampania.it/api"

    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100 MB

    MODELS_DIR: str = "./models"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
