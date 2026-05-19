# Environmental Provider Integration Guide (HealthTrace)

This document defines exactly what the environmental data company must implement/update to integrate with the current HealthTrace platform.

## 1) Integration Scope

HealthTrace runs two coordinated pipelines:

- `Analytical (batch)` for DWH, BI, and ML.
- `Realtime (streaming)` for fast threshold alerts.

Both pipelines are Kafka-based and keyed by `istat_code` (6-digit comune code).

---

## 2) Required Kafka Topics

Provider must support the following topics:

- `environmental-ingestion-air`
  - Purpose: ARPAC batch (daily aggregated stats)
  - Key: `istat_code`
- `environmental-ingestion-meteo`
  - Purpose: MeteoHub batch (daily aggregated stats)
  - Key: `istat_code`
- `environmental-realtime-air`
  - Purpose: ARPAC near-realtime events
  - Key: `istat_code`
- `environmental-realtime-meteo`
  - Purpose: MeteoHub near-realtime events
  - Key: `istat_code`

HealthTrace internal topics (for awareness):

- `analytics_trigger` (alerts produced by HealthTrace consumer)
- `health-data` (disease stream, keyed by `comune_inizio_sintomi_codice_istat`)

---

## 3) API Endpoints Provider Must Maintain

According to the agreed API contract and PDF examples:

- `POST /arpac/data/arpac_data_stat`
- `POST /meteohub/data/meteohub_data_stats`
- Optional raw endpoints for debugging/backfill:
  - `POST /arpac/data/arpac_data`
  - `POST /meteohub/data/meteohub_data`
- Station lists:
  - `GET /arpac/stations`
  - `GET /meteohub/stations`

### Mandatory request behavior

- Endpoints are `POST` with JSON body (not GET query mode for stats).
- `stats` is mandatory for `_stat` endpoints: `["min","mean","max"]`.
- `filter_on_range=true` must be supported and applied.
- `validated=true` must be supported for ARPAC.
- Timestamps must support explicit UTC windows.

---

## 4) Payload Contract (Kafka)

## 4.1 Ingestion payload (batch, daily)

- Source-specific topic:
  - ARPAC -> `environmental-ingestion-air`
  - MeteoHub -> `environmental-ingestion-meteo`
- One message per station per day.
- Partition key: `istat_code`.

Minimum payload fields:

- `source` (`ARPAC` or `METEOHUB`)
- `station_id`
- `istat_code`
- `latitude`, `longitude`
- `period_start` (UTC ISO-8601)
- `period_end` (UTC ISO-8601)
- `aggregation` (`daily`)
- `parameters[]` with:
  - `parameter`
  - `mean`, `min`, `max`
  - `unit`
- `ingested_at` (UTC ISO-8601)

Additional fields:

- ARPAC: `station_type`, `slm`
- MeteoHub: `slm` should be enriched via SRTM if missing

## 4.2 Realtime payload

- Source-specific topic:
  - ARPAC -> `environmental-realtime-air`
  - MeteoHub -> `environmental-realtime-meteo`
- Partition key: `istat_code`.

Minimum realtime fields:

- `source`
- `station_id`
- `istat_code`
- `timestamp` (UTC ISO-8601)
- `parameters[]` each containing:
  - `parameter`
  - `value`
  - `unit`

---

## 5) Data Quality and Normalization Rules

Provider and HealthTrace must align on these rules:

- Invalid values:
  - `-9999` may still leak into stats in edge cases.
  - Provider should filter where possible.
  - HealthTrace performs client-side invalid guards anyway.
- Units:
  - Keep consistent and explicit.
  - Known conversions used by HealthTrace:
    - `µg/m**3`, `μg/m**3` -> `μg/m³`
    - `kg/m**2` -> `mm`
    - `K` -> `°C`
- Parameter naming:
  - `PM2,5` normalized to `PM2.5`.
- Timezone:
  - Always use explicit UTC in API and Kafka payloads.

---

## 6) Station Eligibility Policy

To avoid low-relevance uninhabited/high-altitude signals:

- Preferred stations have `slm < 500m`.
- ARPAC accepted types: `FONDO`, `TRAFFICO`.
- MeteoHub `elev_ref` is sensor-level reference, not station altitude.
  - Use SRTM station elevation for station-level filtering.

---

## 7) Processing Behavior in HealthTrace (for provider awareness)

- Ingestion consumer:
  - Reads ingestion topics.
  - Aggregates by `(istat_code, date, source)`.
  - Applies IDW weighted aggregation.
  - Writes to DWH table `environmental_daily_aggregated`.
- Realtime consumer:
  - Reads realtime topics.
  - Applies threshold checks.
  - Emits alert messages to `analytics_trigger`.

Current threshold examples:

- `NO2 > 200 μg/m³`
- `PM10 > 50 μg/m³`
- `PM2.5 > 25 μg/m³`
- `O3 > 120 μg/m³`
- `SO2 > 350 μg/m³`
- `temperature > 35 °C`
- `relative_humidity > 90%`

---

## 8) Decision Points to Close in Alignment Session

Provider + HealthTrace must close these items:

- Final Kafka bootstrap endpoints and auth mode.
- Who publishes where:
  - Provider directly to HealthTrace topics, or bridge layer.
- Topic retention for replay (recommended minimum: 7 days for ingestion).
- Final JSON schema versioning strategy.
- Realtime SLA target (event-to-alert latency).
- Historical backfill strategy:
  - Date range
  - API pull vs batch file delivery

---

## 9) Go-Live Acceptance Checklist

Go-live is approved when all are true:

- [ ] Provider can return correct `_stat` responses for ARPAC and MeteoHub.
- [ ] Provider publishes to all 4 environmental topics with correct keys.
- [ ] Payloads contain required UTC fields and units.
- [ ] Invalid values are handled and not poisoning daily means.
- [ ] HealthTrace consumers ingest with no schema errors.
- [ ] DWH records visible in `environmental_daily_aggregated`.
- [ ] Realtime alerts reach `analytics_trigger`.
- [ ] Backfill run completed for agreed historical period.

