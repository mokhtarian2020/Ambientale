# HealthTrace — Copilot Instructions

## What This Project Is
HealthTrace is an **AI-powered environmental health surveillance platform** for Italian health authorities (Campania, Molise, Calabria). It correlates environmental data (air quality, meteorology) with infectious disease cases to detect and predict outbreaks.

**External data provider**: Ambientali Fattori / ARPES. Contact: Valerio.
Do NOT open the parent Ambientale folder — too many large docs waste context tokens.

---

## Architecture — Two Pipelines

### Pipeline 1: Analytical (Batch)
```
Ambientali Fattori API → IngestionConsumer (Kafka) → IDW aggregation → environmental_daily_aggregated (DWH) → ML models
```
- Topics: environmental-ingestion-air, environmental-ingestion-meteo
- UPSERT on (istat_code, source, period_date) — NRT overwritten by validated data automatically
- NO delete topic needed — handled by ON CONFLICT DO UPDATE in PostgreSQL

### Pipeline 2: Realtime Alert (Streaming)
```
Ambientali Fattori sensors → RealtimeAlertConsumer (Kafka) → threshold check → analytics_trigger
```
- Topics: environmental-realtime-air, environmental-realtime-meteo
- NOTHING stored to DB — fire-and-forget alerts only
- No delete or correction mechanism needed for realtime

---

## Kafka Topics

| Topic | Direction | Key | Purpose |
|---|---|---|---|
| environmental-ingestion-air | Ambientali Fattori → HealthTrace | istat_code | Daily ARPAC batch stats |
| environmental-ingestion-meteo | Ambientali Fattori → HealthTrace | istat_code | Daily MeteoHub batch stats |
| environmental-realtime-air | Ambientali Fattori → HealthTrace | istat_code | Near-realtime ARPAC events |
| environmental-realtime-meteo | Ambientali Fattori → HealthTrace | istat_code | Near-realtime MeteoHub events |
| analytics_trigger | HealthTrace internal | istat_code | Threshold breach alerts |
| health-data | GESAN → HealthTrace | comune_inizio_sintomi_codice_istat | Disease case notifications |

**Kafka library**: `kafka-python==2.0.2`
**Import**: `from kafka import KafkaProducer, KafkaConsumer, KafkaError`
**Broker image**: `confluentinc/cp-kafka:latest`, port 9092 internal / 29092 external

---

## Kafka Payload Contracts

### Ingestion payload (batch — one message per station per day)
```json
{
  "source": "ARPAC",
  "station_id": "STA_001",
  "istat_code": "063049",
  "latitude": 40.853,
  "longitude": 14.268,
  "period_start": "2026-04-13T00:00:00Z",
  "period_end": "2026-04-13T23:59:59Z",
  "aggregation": "daily",
  "parameters": [
    {"parameter": "PM2.5", "mean": 22.5, "min": 15.3, "max": 31.7, "unit": "μg/m³"}
  ],
  "ingested_at": "2026-04-14T01:00:00Z",
  "station_type": "FONDO",
  "slm": 45.0
}
```
- ARPAC extra fields: `station_type`, `slm`
- MeteoHub extra: `slm` only (no `station_type`)

### Realtime payload (per observation)
```json
{
  "source": "ARPAC",
  "station_id": "STA_001",
  "istat_code": "063049",
  "timestamp": "2026-04-13T10:00:00Z",
  "parameters": [
    {"parameter": "PM2.5", "value": 31.7, "unit": "μg/m³"}
  ]
}
```

---

## External API (Ambientali Fattori — Valerio)

Base URL: `settings.VALERIO_API_BASE_URL` (default `http://localhost:7600`)

| Endpoint | Method | Use |
|---|---|---|
| /arpac/data/arpac_data_stat | POST | Historical ARPAC aggregated stats |
| /meteohub/data/meteohub_data_stats | POST | Historical MeteoHub aggregated stats |
| /arpac/data/arpac_data | POST | Raw ARPAC observations (debug/backfill) |
| /meteohub/data/meteohub_data | POST | Raw MeteoHub observations |
| /arpac/stations | GET | ARPAC station list |
| /meteohub/stations | GET | MeteoHub station list |

**Critical rules**:
- All _stat endpoints are POST with JSON body (not GET)
- Always include: `stats=["min","mean","max"]`, `filter_on_range=true`, UTC timezone
- ARPAC only: `validated=true` or `validated=false`
- MeteoHub: **NO validated parameter — never send it, it does not exist**

---

## Database

**Engine**: PostgreSQL 14 + TimescaleDB + PostGIS
**Port**: 5433 (Docker) maps to internal 5432
**Dev credentials**: user=`healthtrace`, password=`healthtrace_password`, db=`healthtrace`
**Config**: `backend/app/core/config.py` — all settings live here

### Key Tables

| Table | Purpose |
|---|---|
| environmental_daily_aggregated | IDW-aggregated daily env data — key: (istat_code, source, period_date) |
| disease_reports | Infectious disease cases from GESAN ASL Campania (29K+ rows) |
| patients | Patient demographics |
| disease_environmental_correlations | Correlation r + p-value per disease+parameter |
| environmental_data | Raw environmental measurements |

**Real GESAN DB**: `10.10.13.11:5432/gesan_malattieinfettive`
Read-only, 118 tables, Jun 2024–Feb 2026, 80 disease categories.

---

## Repo Structure

```
HealthTrace/
├── .github/copilot-instructions.md   ← this file
├── backend/
│   ├── main.py                        # FastAPI entrypoint, starts Kafka consumers
│   └── app/
│       ├── core/config.py             # ALL settings (Kafka topics, DB URL, API URLs)
│       ├── core/database.py           # SQLAlchemy engine + session
│       ├── api/v1/                    # Route handlers
│       ├── models/                    # SQLAlchemy ORM models
│       ├── schemas/                   # Pydantic DTOs
│       ├── services/                  # Business logic
│       └── pipeline/data_pipeline.py  # Kafka wrapper used by backend
├── data-pipeline/
│   ├── kafka_consumer.py             # IngestionConsumer, RealtimeAlertConsumer, HealthDataConsumer
│   ├── kafka_producer.py             # HealthTraceProducer wrapper
│   ├── environmental_ingestion_service.py  # Pulls from Valerio API, publishes to Kafka
│   └── station_census_service.py
├── analytics/
│   ├── advanced_models.py            # DLNM, XGBoost, RandomForest, LSTM
│   ├── regression_models.py          # GLM, GAM, ARIMAX
│   └── dwh_data_loader.py            # Loads DWH data for ML training
├── deployment/
│   └── init-db.sql                   # Full DB schema init
├── docker-compose.yml
├── start_platform.sh
└── frontend/                         # React + D3.js (port 3200)
```

---

## Target Diseases (Phase 1)

| Disease | Key Environmental Correlations | r |
|---|---|---|
| Influenza | PM2.5, Temperature, Humidity | 0.821 |
| Legionellosis | Water temp, Humidity, Precipitation | 0.756 |
| Hepatitis A | E.coli, pH, Precipitation | 0.743 |

**Water quality (E.coli, pH) is NOT provided by Ambientali Fattori — separate source TBD.**

---

## Alert Thresholds (Realtime Pipeline)

| Parameter | Threshold | Unit |
|---|---|---|
| NO2 | > 200 | μg/m³ |
| PM10 | > 50 | μg/m³ |
| PM2.5 | > 25 | μg/m³ |
| O3 | > 120 | μg/m³ |
| SO2 | > 350 | μg/m³ |
| temperature | > 35 | °C |
| relative_humidity | > 90 | % |

---

## Station Eligibility Rules
- `slm < 500m` (elevation from SRTM — approximate, not exact)
- ARPAC: `station_type IN ("FONDO", "TRAFFICO")` — skip INDUSTRIALE
- MeteoHub: elevation filter only, no type filter
- `istat_code` must be non-null — skip stations without ISTAT code
- `istat_code` is 6-digit string (e.g. `"063049"` = Napoli)

---

## Data Quality Rules
- Filter invalid values: `-9999` (ARPAC marker), `null` (MeteoHub)
- All timestamps: UTC ISO-8601 with `Z` or `+00:00`
- Unit normalizations applied in consumer:
  - `µg/m**3`, `μg/m**3` → `μg/m³`
  - `kg/m**2` → `mm`
  - `K` → `°C`
  - `PM2,5` → `PM2.5`

---

## Geographic Coverage
- **Regions**: Campania, Molise, Calabria
- **Municipalities**: 387 comuni, ~2.3M population
- **Key city**: Napoli (istat_code: `063049`)
- All coordinates: EPSG:4326 (WGS84)

---

## Docker Services Port Map

| Service | External Port | Internal Port |
|---|---|---|
| PostgreSQL/TimescaleDB | 5433 | 5432 |
| Kafka | 29092 | 9092 |
| Zookeeper | 2181 | 2181 |
| FastAPI backend | 8001 | 8001 |
| React frontend | 3200 | 3000 |

Start all: `./start_platform.sh`

---

## Open Items (April 2026)
- Water quality data source for Hepatitis A / Legionellosis not yet defined
- Kafka payload schema with Valerio (Ambientali Fattori) not yet finalized — meeting scheduled
- Backfill strategy for 2+ years of historical data not agreed yet
- Schema versioning strategy with Ambientali Fattori TBD
- Some MeteoHub stations have nullable istat_code — consumer skips them gracefully
- Ambientali Fattori API paths may differ from our expectation — confirm with Valerio
