# HealthTrace — Developer Handover Document (English)

**Date**: May 18, 2026  
**Outgoing developer**: Amir  
**Recipient**: Incoming developer  
**Project**: HealthTrace — AI-Powered Environmental Health Surveillance Platform  
**Client**: Italian Health Authorities (Campania, Molise, Calabria)

---

## 1. What Is This Project?

HealthTrace is a platform built for Italian regional health authorities. Its goal is to **correlate environmental data** (air quality, meteorology) with **infectious disease cases** to detect and predict outbreaks before they escalate.

The platform connects three data sources:
1. **Ambientali Fattori / ARPES** (contact: **Valerio**) — provides air quality (ARPAC) and meteorological (MeteoHub) sensor data via a REST API
2. **GESAN ASL Campania real DB** — production disease case database at `10.10.13.11:5432/gesan_malattieinfettive` (read-only, ~29K rows, 118 tables, Jun 2024–Feb 2026)
3. **HealthTrace own PostgreSQL/TimescaleDB** — local data warehouse where aggregated data is stored

The three target diseases for Phase 1 are:
- **Influenza** → correlated with PM2.5, Temperature, Humidity (r = 0.821)
- **Legionellosis** → correlated with Water temp, Humidity, Precipitation (r = 0.756)
- **Hepatitis A** → correlated with E. coli, pH, Precipitation (r = 0.743)

---

## 2. Architecture Overview

Two independent data pipelines run in parallel:

### Pipeline 1: Analytical (Batch)
```
Ambientali Fattori API (Valerio)
        ↓  [POST requests, daily scheduled]
IngestionConsumer (Kafka)
        ↓  [IDW aggregation using Haversine distance]
environmental_daily_aggregated table (PostgreSQL DWH)
        ↓
ML Models (DLNM, XGBoost, Random Forest, LSTM, GLM/GAM, ARIMAX)
```

Kafka topics: `environmental-ingestion-air`, `environmental-ingestion-meteo`

UPSERT logic: `ON CONFLICT (istat_code, source, period_date) DO UPDATE` — NRT data is automatically overwritten by validated data. **No delete topic is needed.**

### Pipeline 2: Realtime Alert (Streaming)
```
Ambientali Fattori sensors
        ↓  [near-realtime events]
RealtimeAlertConsumer (Kafka)
        ↓  [threshold evaluation]
analytics_trigger topic (internal alert)
```

Kafka topics: `environmental-realtime-air`, `environmental-realtime-meteo`

**Nothing is stored to the database in this pipeline.** It is fire-and-forget alerts only. No delete or correction mechanism is needed.

---

## 3. Repository Structure

```
HealthTrace/
├── backend/
│   ├── main.py                        # FastAPI entrypoint, starts Kafka consumers at startup
│   └── app/
│       ├── core/config.py             # ALL settings live here (Kafka topics, DB URL, API URLs)
│       ├── core/database.py           # SQLAlchemy engine + session factory
│       ├── api/v1/endpoints/          # Route handlers (MOST ARE STUBS — see Section 6)
│       ├── models/                    # SQLAlchemy ORM models
│       ├── schemas/                   # Pydantic DTOs
│       └── services/                  # Business logic (MOSTLY MISSING — see Section 6)
├── data-pipeline/
│   ├── kafka_consumer.py             # IngestionConsumer + RealtimeAlertConsumer (IMPLEMENTED)
│   ├── kafka_producer.py             # EnvironmentalDataProducer (IMPLEMENTED)
│   ├── environmental_ingestion_service.py  # Pulls from Valerio API, publishes to Kafka (IMPLEMENTED)
│   └── station_census_service.py     # Station elevation + validity checks (IMPLEMENTED)
├── analytics/
│   ├── advanced_models.py            # DLNM, XGBoost, RF, LSTM (PARTIAL — see Section 6)
│   ├── regression_models.py          # GLM, GAM, ARIMAX, OLS (PARTIAL)
│   └── dwh_data_loader.py            # Loads DWH data for ML training (PARTIAL)
├── deployment/
│   ├── init-db.sql/                  # ⚠️ EMPTY — no SQL schema file exists yet
│   ├── superset_bootstrap.py         # Superset BI tool integration (STUB)
│   └── superset_config.py            # Superset config
├── frontend/
│   ├── package.json                  # React + Material-UI + Leaflet + Plotly + Recharts
│   └── src/                          # React components (status largely unknown)
├── dashboard-mockups/
│   ├── page1_dashboard_principale.html    # Main dashboard mockup
│   ├── page2_sorveglianza_geografica.html # Geographic surveillance
│   ├── page3_correlazioni_ambiente_malattie.html
│   ├── page4_monitoraggio_ambientale.html
│   ├── page5_modelli_predittivi.html
│   └── page6_gestione_allerte.html
├── docker-compose.yml                # Full Docker stack definition
├── start_platform.sh                 # One-shot startup script
└── .github/copilot-instructions.md  # AI assistant project context (keep updated)
```

---

## 4. How to Start the Platform

### Prerequisites
- Docker + Docker Compose installed
- Access to Valerio's API (`http://localhost:7600` or update `VALERIO_API_BASE_URL` in config)
- Network access to GESAN DB at `10.10.13.11` (VPN/LAN)

### Start all services
```bash
./start_platform.sh
# or
docker-compose up -d
```

### Service ports
| Service | External Port |
|---------|--------------|
| PostgreSQL/TimescaleDB | 5433 |
| Kafka | 29092 |
| Zookeeper | 2181 |
| Redis | 6379 |
| FastAPI backend | 8001 |
| React frontend | 3200 |

### Dev credentials (change in production!)
- PostgreSQL: user=`healthtrace`, password=`healthtrace_password`, db=`healthtrace`

### Quick local demo (no Docker needed)
```bash
python synthetic_data_generator.py
python enhanced_simple_api.py
python -m http.server 8080
```

---

## 5. What Has Been Implemented

### ✅ Fully Working

| Component | Location | Notes |
|-----------|----------|-------|
| **IngestionConsumer** | `data-pipeline/kafka_consumer.py` | Reads batch env data, applies IDW aggregation (Haversine), UPSERTs to DWH |
| **RealtimeAlertConsumer** | `data-pipeline/kafka_consumer.py` | Evaluates thresholds, publishes alerts to `analytics_trigger` |
| **EnvironmentalDataProducer** | `data-pipeline/kafka_producer.py` | Sends ARPAC + MeteoHub data to Kafka (both ingestion and realtime topics) |
| **EnvironmentalIngestionService** | `data-pipeline/environmental_ingestion_service.py` | Calls Valerio API (POST), parses response, normalizes units, publishes to Kafka |
| **StationCensusService** | `data-pipeline/station_census_service.py` | Enriches stations with SRTM elevation, validates eligibility rules |
| **Core configuration** | `backend/app/core/config.py` | All Kafka topics, DB URL, API paths, ISTAT codes, thresholds |
| **Database models** | `backend/app/models/` | ORM for all key tables (see below) |
| **FastAPI startup** | `backend/main.py` | App factory, CORS, lifespan, starts 3 Kafka consumer threads |
| **GESAN DB integration** | `backend/app/api/v1/endpoints/real_disease_db.py` | Queries real disease DB, maps to HealthTrace format |
| **Docker stack** | `docker-compose.yml` | All 8 services defined and configured |
| **Dashboard mockups** | `dashboard-mockups/` | 6 complete HTML mockups for the full UI |

### ✅ Database Models Defined
| Model | File | Key Fields |
|-------|------|-----------|
| `EnvironmentalDailyAggregated` | `models/environmental.py` | istat_code, source, period_date, all pollutants + weather stats (UNIQUE constraint) |
| `DiseaseReport` | `models/disease.py` | disease_code, istat_code, onset_date, case_count |
| `DiseaseCategory` | `models/disease.py` | name, correlation_parameter, correlation_r |
| `EnvironmentalData` | `models/environmental.py` | Raw station-level measurements |
| `Patient` | `models/patient.py` | Demographics |
| `User` | `models/user.py` | Auth accounts + roles |

### ✅ Analytics Infrastructure
- Model base classes defined with `ModelResults` dataclass (unified output format)
- Feature engineering pipeline (rainy_days, extreme_precipitation)
- Disease-specific feature selection for each of the 3 target diseases
- DWH ↔ GESAN data join logic in `dwh_data_loader.py`

---

## 6. What Is NOT Done (Critical Gaps)

### 🔴 Critical — Platform Cannot Function Without These

| Gap | Location | Details |
|-----|----------|---------|
| **Most API endpoints are stubs** | `backend/app/api/v1/endpoints/` | `dashboard.py` (5 endpoints), `analytics.py` (6 endpoints), `diseases.py` (3 endpoints), `environmental.py`, `auth.py`, `patients.py`, `users.py`, `investigations.py` — all return placeholder strings |
| **No database SQL schema file** | `deployment/init-db.sql/` | Directory exists but is empty. DB created via SQLAlchemy ORM only — no DDL for indexes, TimescaleDB hypertables, PostGIS setup, or constraints |
| **HealthDataConsumer missing** | Referenced in `backend/main.py` | `from kafka_consumer import HealthDataConsumer` exists in main.py but the class is NOT in `data-pipeline/kafka_consumer.py`. Disease case ingestion from GESAN via Kafka is broken |
| **Service layer missing** | `backend/app/services/` | No disease service, no environmental service, no correlation service, no model prediction service, no alert delivery service |

### 🟡 High Priority — Major Features Incomplete

| Gap | Location | Details |
|-----|----------|---------|
| **Polygon/GeoJSON spatial filtering** | `real_disease_db.py` line 299 | TODO comment — spatial filtering of disease reports by municipality polygon is not implemented |
| **GESAN → local DB sync** | `real_disease_db.py` line 353 | TODO comment — queried GESAN data is never written to local HealthTrace DB |
| **ML models not fully trained** | `analytics/advanced_models.py` | DLNM, LSTM, Case-Crossover, Random Forest — library imports exist but `fit()` methods are incomplete or missing |
| **`DwhDataLoader.load()`** | `analytics/dwh_data_loader.py` | Method signature present but body is incomplete |
| **Water quality data source** | N/A — not yet defined | Hepatitis A and Legionellosis require E. coli, pH, water temperature — no data source has been identified or integrated |
| **Frontend components** | `frontend/src/` | React component implementations have not been audited; functionality beyond basic scaffold is unknown |

### 🟠 Medium Priority — Should Be Fixed

| Gap | Details |
|-----|---------|
| **Hardcoded dev credentials** | `healthtrace_password` in docker-compose. Use `.env` file |
| **Superset BI integration** | `deployment/superset_bootstrap.py` is a stub (`pass`) |
| **Schema stubs** | Several Pydantic schemas in `backend/app/schemas/` contain `pass` with no fields |
| **SRTM rate limit risk** | `pause_between_batches = 1.5s` may be insufficient for bulk station census runs |
| **Unrecognized unit passthrough** | If a unit string is not in the normalization map in `environmental_ingestion_service.py`, it passes through silently without warning |

---

## 7. External APIs and Contacts

### Ambientali Fattori / Valerio API
- **Contact**: Valerio (Ambientali Fattori)
- **Base URL**: `settings.VALERIO_API_BASE_URL` (default `http://localhost:7600`)
- **All stat endpoints are POST, not GET** — this is critical and non-obvious

| Endpoint | Method | Use |
|----------|--------|-----|
| `/arpac/data/arpac_data_stat` | POST | Historical ARPAC daily aggregated stats |
| `/meteohub/data/meteohub_data_stats` | POST | Historical MeteoHub daily aggregated stats |
| `/arpac/data/arpac_data` | POST | Raw ARPAC observations (backfill/debug) |
| `/meteohub/data/meteohub_data` | POST | Raw MeteoHub observations |
| `/arpac/stations` | GET | ARPAC station list |
| `/meteohub/stations` | GET | MeteoHub station list |

**Critical rules for Valerio API calls:**
- Always include: `"stats": ["min", "mean", "max"]`, `"filter_on_range": true`, UTC timestamps
- ARPAC only: include `"validated": true` (or `false` for NRT)
- MeteoHub: **NEVER send the `validated` parameter — it does not exist on that API**
- `filter_on_range: true` does NOT prevent `-9999` sentinel values from appearing in means — always filter client-side too

### GESAN ASL Campania (Real Disease DB)
- **Host**: `10.10.13.11:5432`
- **Database**: `gesan_malattieinfettive`
- **Credentials**: `readonly / readonly`
- **Access**: Read-only, requires LAN/VPN access
- **Coverage**: Jun 2024 – Feb 2026, ~29,000 disease records, 118 tables, 80 disease categories

### OpenTopoData (SRTM Elevation)
- **URL**: `https://api.opentopodata.org/v1/srtm90m`
- Used to enrich MeteoHub stations with elevation (station_census_service.py)
- Rate limit: up to 100 locations per request, respect `pause_between_batches`

---

## 8. Kafka — Key Details

**Library**: `kafka-python==2.0.2`
**Import**: `from kafka import KafkaProducer, KafkaConsumer, KafkaError`
**Broker image**: `confluentinc/cp-kafka:latest`
**Internal port**: 9092 | **External port**: 29092

### Topics
| Topic | Direction | Purpose |
|-------|-----------|---------|
| `environmental-ingestion-air` | Ambientali Fattori → HealthTrace | Daily ARPAC batch stats |
| `environmental-ingestion-meteo` | Ambientali Fattori → HealthTrace | Daily MeteoHub batch stats |
| `environmental-realtime-air` | Ambientali Fattori → HealthTrace | Near-realtime ARPAC events |
| `environmental-realtime-meteo` | Ambientali Fattori → HealthTrace | Near-realtime MeteoHub events |
| `analytics_trigger` | HealthTrace internal | Threshold breach alerts |
| `health-data` | GESAN → HealthTrace | Disease case notifications |

### Alert Thresholds (RealtimeAlertConsumer)
| Parameter | Threshold | Unit |
|-----------|-----------|------|
| NO2 | > 200 | μg/m³ |
| PM10 | > 50 | μg/m³ |
| PM2.5 | > 25 | μg/m³ |
| O3 | > 120 | μg/m³ |
| SO2 | > 350 | μg/m³ |
| temperature | > 35 | °C |
| relative_humidity | > 90 | % |

---

## 9. Database — Key Details

**Engine**: PostgreSQL 14 + TimescaleDB + PostGIS  
**Dev port**: 5433 (maps to internal 5432)  
**Config file**: `backend/app/core/config.py`

### Key Tables
| Table | Purpose |
|-------|---------|
| `environmental_daily_aggregated` | IDW-aggregated daily env data — UPSERT key: `(istat_code, source, period_date)` |
| `disease_reports` | Infectious disease cases from GESAN |
| `patients` | Patient demographics |
| `disease_environmental_correlations` | Pearson r + p-value per disease+parameter pair |
| `environmental_data` | Raw station-level measurements |

### Station Eligibility Rules
- `slm < 500m` elevation (from SRTM — approximate)
- ARPAC: `station_type IN ('FONDO', 'TRAFFICO')` — skip `INDUSTRIALE`
- MeteoHub: elevation filter only, no type filter
- `istat_code` must be non-null — skip stations without it

### ISTAT Code Format
6-digit string: e.g., `"063049"` = Napoli. Always use string, never integer.

---

## 10. Data Quality Rules

- Filter invalid values: `-9999` (ARPAC sentinel), `null` (MeteoHub)
- All timestamps: UTC ISO-8601 with `Z` or `+00:00`
- Unit normalizations applied in `environmental_ingestion_service.py`:
  - `µg/m**3`, `μg/m**3` → `μg/m³`
  - `kg/m**2` → `mm`
  - `K` → `°C` (Kelvin conversion: value − 273.15)
  - `PM2,5` → `PM2.5` (comma to dot)

---

## 11. Recommended Next Steps (Priority Order)

### Phase 1: Make the Platform Functional
1. **Implement `HealthDataConsumer`** in `data-pipeline/kafka_consumer.py` — consumes from `health-data` topic, writes disease reports to `disease_reports` table
2. **Write the SQL schema** (`deployment/init-db.sql/init.sql`) — DDL for all tables, TimescaleDB hypertable declarations, PostGIS extension, indexes on (istat_code, period_date)
3. **Implement the service layer** in `backend/app/services/` — start with `disease_service.py` and `environmental_service.py`
4. **Implement stub API endpoints** — prioritize `dashboard.py` and `diseases.py` since those are needed for the UI

### Phase 2: Analytics
5. **Complete `DwhDataLoader.load()`** — finish the GESAN ↔ DWH join logic
6. **Implement GESAN → local DB sync** (TODO at line 353 in `real_disease_db.py`)
7. **Complete ML model `fit()` methods** in `advanced_models.py` — DLNM and LSTM first (highest predictive value)
8. **Implement polygon/GeoJSON spatial filtering** (TODO at line 299 in `real_disease_db.py`)

### Phase 3: Production Readiness
9. **Move credentials to `.env`** — remove hardcoded `healthtrace_password`
10. **Implement Superset BI bootstrap** — `deployment/superset_bootstrap.py` is a stub
11. **Identify water quality data source** — E. coli, pH, water temperature needed for Hepatitis A and Legionellosis models
12. **Finalize Kafka payload schema with Valerio** — meeting was scheduled, may not have happened
13. **Define backfill strategy** for 2+ years of historical environmental data
14. **Audit frontend components** — React components in `frontend/src/` need functional review
15. **Add schema versioning** strategy with Ambientali Fattori for future API changes

---

## 12. Open Questions Left Unresolved

- **Water quality source**: E. coli, pH, water temperature are NOT provided by Ambientali Fattori. A separate data provider needs to be identified and integrated.
- **Kafka payload finalization**: The schema contract with Valerio has not been formally agreed upon. Actual API paths may differ from what is coded — confirm with Valerio before running in production.
- **Backfill strategy**: How to load 2+ years of historical environmental data into the DWH has not been decided.
- **MeteoHub nullable ISTAT**: Some MeteoHub stations have `null` istat_code — the consumer skips them gracefully, but they are silently lost. Decide if this is acceptable or if a fallback (reverse geocoding) should be implemented.
- **Schema versioning**: No versioning strategy exists if Valerio changes the API payload format.

---

## 13. Project Contacts

| Role | Contact | Notes |
|------|---------|-------|
| External data provider | **Valerio** (Ambientali Fattori / ARPES) | Kafka payload schema, API endpoints |
| Client / Health authority | Campania, Molise, Calabria regional authorities | Disease data access |
| GESAN DB access | ASL Campania IT dept | VPN credentials, read-only DB at 10.10.13.11 |

---

*Good luck. The architecture is solid — the main work remaining is wiring up the API endpoints to the service layer, completing the analytics models, and sourcing the water quality data.*
