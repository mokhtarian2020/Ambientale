# HealthTrace — Documento di Passaggio Consegne (Italiano)

**Data**: 18 maggio 2026  
**Sviluppatore uscente**: Amir  
**Destinatario**: Sviluppatore entrante  
**Progetto**: HealthTrace — Piattaforma di Sorveglianza Sanitaria Ambientale con AI  
**Cliente**: Autorità Sanitarie Regionali Italiane (Campania, Molise, Calabria)

---

## 1. Cos'è Questo Progetto?

HealthTrace è una piattaforma costruita per le autorità sanitarie regionali italiane. Il suo obiettivo è **correlare i dati ambientali** (qualità dell'aria, meteorologia) con i **casi di malattie infettive** per rilevare e prevedere le epidemie prima che si aggravino.

La piattaforma connette tre fonti di dati:
1. **Ambientali Fattori / ARPES** (riferimento: **Valerio**) — fornisce dati di qualità dell'aria (ARPAC) e meteorologici (MeteoHub) tramite API REST
2. **DB reale GESAN ASL Campania** — database di produzione dei casi di malattia a `10.10.13.11:5432/gesan_malattieinfettive` (sola lettura, ~29.000 righe, 118 tabelle, giugno 2024 – febbraio 2026)
3. **PostgreSQL/TimescaleDB proprio di HealthTrace** — data warehouse locale dove vengono memorizzati i dati aggregati

Le tre malattie target della Fase 1 sono:
- **Influenza** → correlata con PM2.5, Temperatura, Umidità (r = 0,821)
- **Legionellosi** → correlata con Temperatura acqua, Umidità, Precipitazioni (r = 0,756)
- **Epatite A** → correlata con E. coli, pH, Precipitazioni (r = 0,743)

---

## 2. Architettura del Sistema

Due pipeline di dati indipendenti operano in parallelo:

### Pipeline 1: Analitica (Batch)
```
API Ambientali Fattori (Valerio)
        ↓  [richieste POST, pianificate giornalmente]
IngestionConsumer (Kafka)
        ↓  [aggregazione IDW con distanza di Haversine]
tabella environmental_daily_aggregated (DWH PostgreSQL)
        ↓
Modelli ML (DLNM, XGBoost, Random Forest, LSTM, GLM/GAM, ARIMAX)
```

Topic Kafka: `environmental-ingestion-air`, `environmental-ingestion-meteo`

Logica UPSERT: `ON CONFLICT (istat_code, source, period_date) DO UPDATE` — i dati NRT (near-realtime) vengono automaticamente sovrascritti dai dati validati. **Non è necessario un topic di cancellazione.**

### Pipeline 2: Alert Realtime (Streaming)
```
Sensori Ambientali Fattori
        ↓  [eventi near-realtime]
RealtimeAlertConsumer (Kafka)
        ↓  [valutazione soglie]
topic analytics_trigger (alert interno)
```

Topic Kafka: `environmental-realtime-air`, `environmental-realtime-meteo`

**In questa pipeline nulla viene salvato nel database.** Sono alert di tipo fire-and-forget. Non è necessario alcun meccanismo di cancellazione o correzione.

---

## 3. Struttura del Repository

```
HealthTrace/
├── backend/
│   ├── main.py                        # Entry point FastAPI, avvia i consumer Kafka all'avvio
│   └── app/
│       ├── core/config.py             # TUTTE le impostazioni (topic Kafka, DB URL, URL API)
│       ├── core/database.py           # SQLAlchemy engine + session factory
│       ├── api/v1/endpoints/          # Route handler (LA MAGGIOR PARTE SONO STUB — vedi Sezione 6)
│       ├── models/                    # Modelli ORM SQLAlchemy
│       ├── schemas/                   # DTO Pydantic
│       └── services/                  # Business logic (QUASI TUTTO MANCANTE — vedi Sezione 6)
├── data-pipeline/
│   ├── kafka_consumer.py             # IngestionConsumer + RealtimeAlertConsumer (IMPLEMENTATI)
│   ├── kafka_producer.py             # EnvironmentalDataProducer (IMPLEMENTATO)
│   ├── environmental_ingestion_service.py  # Chiama API Valerio, pubblica su Kafka (IMPLEMENTATO)
│   └── station_census_service.py     # Controlli elevazione + validità stazioni (IMPLEMENTATO)
├── analytics/
│   ├── advanced_models.py            # DLNM, XGBoost, RF, LSTM (PARZIALE — vedi Sezione 6)
│   ├── regression_models.py          # GLM, GAM, ARIMAX, OLS (PARZIALE)
│   └── dwh_data_loader.py            # Carica dati DWH per il training ML (PARZIALE)
├── deployment/
│   ├── init-db.sql/                  # ⚠️ VUOTO — nessun file SQL di schema esiste ancora
│   ├── superset_bootstrap.py         # Integrazione BI Superset (STUB)
│   └── superset_config.py            # Configurazione Superset
├── frontend/
│   ├── package.json                  # React + Material-UI + Leaflet + Plotly + Recharts
│   └── src/                          # Componenti React (stato in gran parte sconosciuto)
├── dashboard-mockups/
│   ├── page1_dashboard_principale.html    # Mockup dashboard principale
│   ├── page2_sorveglianza_geografica.html # Sorveglianza geografica
│   ├── page3_correlazioni_ambiente_malattie.html
│   ├── page4_monitoraggio_ambientale.html
│   ├── page5_modelli_predittivi.html
│   └── page6_gestione_allerte.html
├── docker-compose.yml                # Definizione completo stack Docker
├── start_platform.sh                 # Script di avvio in un comando
└── .github/copilot-instructions.md  # Contesto progetto per AI assistant (mantenere aggiornato)
```

---

## 4. Come Avviare la Piattaforma

### Prerequisiti
- Docker + Docker Compose installati
- Accesso all'API di Valerio (`http://localhost:7600` oppure aggiornare `VALERIO_API_BASE_URL` nella config)
- Accesso di rete al DB GESAN a `10.10.13.11` (VPN/LAN)

### Avvio di tutti i servizi
```bash
./start_platform.sh
# oppure
docker-compose up -d
```

### Porte dei servizi
| Servizio | Porta Esterna |
|---------|--------------|
| PostgreSQL/TimescaleDB | 5433 |
| Kafka | 29092 |
| Zookeeper | 2181 |
| Redis | 6379 |
| Backend FastAPI | 8001 |
| Frontend React | 3200 |

### Credenziali sviluppo (da cambiare in produzione!)
- PostgreSQL: utente=`healthtrace`, password=`healthtrace_password`, db=`healthtrace`

### Demo locale rapida (senza Docker)
```bash
python synthetic_data_generator.py
python enhanced_simple_api.py
python -m http.server 8080
```

---

## 5. Cosa È Stato Implementato

### ✅ Pienamente Funzionante

| Componente | Posizione | Note |
|------------|----------|------|
| **IngestionConsumer** | `data-pipeline/kafka_consumer.py` | Legge dati ambientali batch, applica aggregazione IDW (Haversine), UPSERT su DWH |
| **RealtimeAlertConsumer** | `data-pipeline/kafka_consumer.py` | Valuta soglie, pubblica alert su `analytics_trigger` |
| **EnvironmentalDataProducer** | `data-pipeline/kafka_producer.py` | Invia dati ARPAC + MeteoHub a Kafka (topic ingestion e realtime) |
| **EnvironmentalIngestionService** | `data-pipeline/environmental_ingestion_service.py` | Chiama API Valerio (POST), analizza risposta, normalizza unità, pubblica su Kafka |
| **StationCensusService** | `data-pipeline/station_census_service.py` | Arricchisce stazioni con elevazione SRTM, valida regole di idoneità |
| **Configurazione core** | `backend/app/core/config.py` | Tutti i topic Kafka, URL DB, percorsi API, codici ISTAT, soglie |
| **Modelli database** | `backend/app/models/` | ORM per tutte le tabelle chiave (vedi sotto) |
| **Avvio FastAPI** | `backend/main.py` | Factory app, CORS, lifespan, avvia 3 thread consumer Kafka |
| **Integrazione DB GESAN** | `backend/app/api/v1/endpoints/real_disease_db.py` | Interroga DB malattie reale, mappa in formato HealthTrace |
| **Stack Docker** | `docker-compose.yml` | Tutti gli 8 servizi definiti e configurati |
| **Mockup dashboard** | `dashboard-mockups/` | 6 mockup HTML completi per l'intera UI |

### ✅ Modelli Database Definiti
| Modello | File | Campi Chiave |
|---------|------|--------------|
| `EnvironmentalDailyAggregated` | `models/environmental.py` | istat_code, source, period_date, tutti gli inquinanti + statistiche meteo (vincolo UNIQUE) |
| `DiseaseReport` | `models/disease.py` | disease_code, istat_code, onset_date, case_count |
| `DiseaseCategory` | `models/disease.py` | name, correlation_parameter, correlation_r |
| `EnvironmentalData` | `models/environmental.py` | Misurazioni raw a livello stazione |
| `Patient` | `models/patient.py` | Dati demografici |
| `User` | `models/user.py` | Account auth + ruoli |

### ✅ Infrastruttura Analitica
- Classi base dei modelli definite con dataclass `ModelResults` (formato output unificato)
- Pipeline di feature engineering (rainy_days, extreme_precipitation)
- Selezione feature specifica per malattia per ognuna delle 3 malattie target
- Logica join DWH ↔ GESAN in `dwh_data_loader.py`

---

## 6. Cosa NON È Fatto (Lacune Critiche)

### 🔴 Critico — La Piattaforma Non Può Funzionare Senza Questi

| Lacuna | Posizione | Dettagli |
|--------|----------|---------|
| **La maggior parte degli endpoint API sono stub** | `backend/app/api/v1/endpoints/` | `dashboard.py` (5 endpoint), `analytics.py` (6 endpoint), `diseases.py` (3 endpoint), `environmental.py`, `auth.py`, `patients.py`, `users.py`, `investigations.py` — tutti restituiscono stringhe placeholder |
| **Nessun file SQL di schema database** | `deployment/init-db.sql/` | La directory esiste ma è vuota. Il DB viene creato solo tramite ORM SQLAlchemy — nessun DDL per indici, ipertabelle TimescaleDB, setup PostGIS o vincoli espliciti |
| **HealthDataConsumer mancante** | Riferito in `backend/main.py` | `from kafka_consumer import HealthDataConsumer` esiste in main.py ma la classe NON è in `data-pipeline/kafka_consumer.py`. L'ingestione dei casi di malattia da GESAN via Kafka è non funzionante |
| **Service layer assente** | `backend/app/services/` | Nessun disease service, nessun environmental service, nessun correlation service, nessun model prediction service, nessun alert delivery service |

### 🟡 Alta Priorità — Funzionalità Importanti Incomplete

| Lacuna | Posizione | Dettagli |
|--------|----------|---------|
| **Filtro spaziale Polygon/GeoJSON** | `real_disease_db.py` riga 299 | Commento TODO — il filtraggio spaziale dei casi di malattia per poligono comunale non è implementato |
| **Sync GESAN → DB locale** | `real_disease_db.py` riga 353 | Commento TODO — i dati interrogati da GESAN non vengono mai scritti nel DB locale HealthTrace |
| **Modelli ML non completamente addestrati** | `analytics/advanced_models.py` | DLNM, LSTM, Case-Crossover, Random Forest — gli import delle librerie esistono ma i metodi `fit()` sono incompleti o mancanti |
| **`DwhDataLoader.load()`** | `analytics/dwh_data_loader.py` | Firma del metodo presente ma il corpo è incompleto |
| **Fonte dati qualità acqua** | N/A — non ancora definita | Epatite A e Legionellosi richiedono E. coli, pH, temperatura dell'acqua — nessuna fonte dati è stata identificata o integrata |
| **Componenti frontend** | `frontend/src/` | Le implementazioni dei componenti React non sono state verificate; la funzionalità oltre lo scaffold di base è sconosciuta |

### 🟠 Priorità Media — Da Correggere

| Lacuna | Dettagli |
|--------|---------|
| **Credenziali hardcoded** | `healthtrace_password` in docker-compose. Usare file `.env` |
| **Integrazione BI Superset** | `deployment/superset_bootstrap.py` è uno stub (`pass`) |
| **Schema stub** | Diversi schemi Pydantic in `backend/app/schemas/` contengono `pass` senza campi |
| **Rischio rate limit SRTM** | `pause_between_batches = 1.5s` potrebbe essere insufficiente per run massivi di census stazioni |
| **Passthrough unità non riconosciute** | Se una stringa di unità non è nella mappa di normalizzazione in `environmental_ingestion_service.py`, passa silenziosamente senza avviso |

---

## 7. API Esterne e Contatti

### API Ambientali Fattori / Valerio
- **Contatto**: Valerio (Ambientali Fattori / ARPES)
- **URL base**: `settings.VALERIO_API_BASE_URL` (default `http://localhost:7600`)
- **Tutti gli endpoint stat sono POST, non GET** — questo è critico e non ovvio

| Endpoint | Metodo | Utilizzo |
|----------|--------|---------|
| `/arpac/data/arpac_data_stat` | POST | Statistiche giornaliere aggregate ARPAC storiche |
| `/meteohub/data/meteohub_data_stats` | POST | Statistiche giornaliere aggregate MeteoHub storiche |
| `/arpac/data/arpac_data` | POST | Osservazioni ARPAC raw (backfill/debug) |
| `/meteohub/data/meteohub_data` | POST | Osservazioni MeteoHub raw |
| `/arpac/stations` | GET | Lista stazioni ARPAC |
| `/meteohub/stations` | GET | Lista stazioni MeteoHub |

**Regole critiche per le chiamate API Valerio:**
- Includere sempre: `"stats": ["min", "mean", "max"]`, `"filter_on_range": true`, timestamp UTC
- Solo ARPAC: includere `"validated": true` (oppure `false` per NRT)
- MeteoHub: **NON inviare MAI il parametro `validated` — non esiste in quell'API**
- `filter_on_range: true` NON impedisce che i valori sentinella `-9999` appaiano nelle medie — filtrare sempre anche lato client

### GESAN ASL Campania (DB Malattie Reale)
- **Host**: `10.10.13.11:5432`
- **Database**: `gesan_malattieinfettive`
- **Credenziali**: `readonly / readonly`
- **Accesso**: Sola lettura, richiede accesso LAN/VPN
- **Copertura**: Giugno 2024 – Febbraio 2026, ~29.000 record malattie, 118 tabelle, 80 categorie di malattie

### OpenTopoData (Elevazione SRTM)
- **URL**: `https://api.opentopodata.org/v1/srtm90m`
- Usato per arricchire le stazioni MeteoHub con dati di elevazione (`station_census_service.py`)
- Limite di rate: fino a 100 posizioni per richiesta, rispettare `pause_between_batches`

---

## 8. Kafka — Dettagli Chiave

**Libreria**: `kafka-python==2.0.2`
**Import**: `from kafka import KafkaProducer, KafkaConsumer, KafkaError`
**Immagine broker**: `confluentinc/cp-kafka:latest`
**Porta interna**: 9092 | **Porta esterna**: 29092

### Topic
| Topic | Direzione | Scopo |
|-------|-----------|-------|
| `environmental-ingestion-air` | Ambientali Fattori → HealthTrace | Statistiche batch giornaliere ARPAC |
| `environmental-ingestion-meteo` | Ambientali Fattori → HealthTrace | Statistiche batch giornaliere MeteoHub |
| `environmental-realtime-air` | Ambientali Fattori → HealthTrace | Eventi ARPAC near-realtime |
| `environmental-realtime-meteo` | Ambientali Fattori → HealthTrace | Eventi MeteoHub near-realtime |
| `analytics_trigger` | HealthTrace interno | Alert superamento soglia |
| `health-data` | GESAN → HealthTrace | Notifiche casi malattia |

### Soglie Alert (RealtimeAlertConsumer)
| Parametro | Soglia | Unità |
|-----------|--------|-------|
| NO2 | > 200 | μg/m³ |
| PM10 | > 50 | μg/m³ |
| PM2.5 | > 25 | μg/m³ |
| O3 | > 120 | μg/m³ |
| SO2 | > 350 | μg/m³ |
| temperature | > 35 | °C |
| relative_humidity | > 90 | % |

---

## 9. Database — Dettagli Chiave

**Engine**: PostgreSQL 14 + TimescaleDB + PostGIS  
**Porta dev**: 5433 (mappa alla 5432 interna)  
**File di configurazione**: `backend/app/core/config.py`

### Tabelle Principali
| Tabella | Scopo |
|---------|-------|
| `environmental_daily_aggregated` | Dati ambientali giornalieri aggregati IDW — chiave UPSERT: `(istat_code, source, period_date)` |
| `disease_reports` | Casi di malattie infettive da GESAN |
| `patients` | Dati demografici pazienti |
| `disease_environmental_correlations` | Pearson r + p-value per coppia malattia+parametro |
| `environmental_data` | Misurazioni raw a livello stazione |

### Regole di Idoneità Stazione
- `slm < 500m` elevazione (da SRTM — approssimativa)
- ARPAC: `station_type IN ('FONDO', 'TRAFFICO')` — escludere `INDUSTRIALE`
- MeteoHub: solo filtro elevazione, nessun filtro tipo
- `istat_code` deve essere non-null — saltare stazioni senza codice ISTAT

### Formato Codice ISTAT
Stringa a 6 cifre: es. `"063049"` = Napoli. Usare sempre stringa, mai intero.

---

## 10. Regole di Qualità Dati

- Filtrare valori non validi: `-9999` (sentinella ARPAC), `null` (MeteoHub)
- Tutti i timestamp: UTC ISO-8601 con `Z` o `+00:00`
- Normalizzazioni unità applicate in `environmental_ingestion_service.py`:
  - `µg/m**3`, `μg/m**3` → `μg/m³`
  - `kg/m**2` → `mm`
  - `K` → `°C` (conversione Kelvin: valore − 273.15)
  - `PM2,5` → `PM2.5` (virgola in punto)

---

## 11. Prossimi Passi Consigliati (Ordine di Priorità)

### Fase 1: Rendere la Piattaforma Funzionante
1. **Implementare `HealthDataConsumer`** in `data-pipeline/kafka_consumer.py` — consuma dal topic `health-data`, scrive i report di malattia nella tabella `disease_reports`
2. **Scrivere lo schema SQL** (`deployment/init-db.sql/init.sql`) — DDL per tutte le tabelle, dichiarazioni ipertabella TimescaleDB, estensione PostGIS, indici su (istat_code, period_date)
3. **Implementare il service layer** in `backend/app/services/` — iniziare con `disease_service.py` e `environmental_service.py`
4. **Implementare gli endpoint API stub** — dare priorità a `dashboard.py` e `diseases.py` poiché necessari per l'UI

### Fase 2: Analytics
5. **Completare `DwhDataLoader.load()`** — finire la logica di join GESAN ↔ DWH
6. **Implementare la sync GESAN → DB locale** (TODO alla riga 353 in `real_disease_db.py`)
7. **Completare i metodi `fit()` dei modelli ML** in `advanced_models.py` — DLNM e LSTM per primi (maggior valore predittivo)
8. **Implementare il filtro spaziale polygon/GeoJSON** (TODO alla riga 299 in `real_disease_db.py`)

### Fase 3: Prontezza per la Produzione
9. **Spostare le credenziali in `.env`** — rimuovere `healthtrace_password` hardcoded
10. **Implementare il bootstrap BI Superset** — `deployment/superset_bootstrap.py` è uno stub
11. **Identificare la fonte dei dati di qualità dell'acqua** — E. coli, pH, temperatura dell'acqua necessari per i modelli di Epatite A e Legionellosi
12. **Finalizzare lo schema payload Kafka con Valerio** — la riunione era programmata, potrebbe non essere avvenuta
13. **Definire la strategia di backfill** per oltre 2 anni di dati storici ambientali
14. **Verificare i componenti frontend** — i componenti React in `frontend/src/` necessitano di revisione funzionale
15. **Aggiungere una strategia di versioning degli schemi** con Ambientali Fattori per future modifiche API

---

## 12. Questioni Aperte Irrisolte

- **Fonte qualità acqua**: E. coli, pH, temperatura dell'acqua NON sono forniti da Ambientali Fattori. È necessario identificare e integrare un fornitore di dati separato.
- **Finalizzazione payload Kafka**: Il contratto di schema con Valerio non è stato formalmente concordato. I percorsi API effettivi potrebbero differire da quelli nel codice — confermare con Valerio prima di eseguire in produzione.
- **Strategia di backfill**: Come caricare oltre 2 anni di dati ambientali storici nel DWH non è stato deciso.
- **ISTAT nullable MeteoHub**: Alcune stazioni MeteoHub hanno `istat_code` null — il consumer le salta silenziosamente. Decidere se questo è accettabile o se è necessario implementare un fallback (geocodifica inversa).
- **Schema versioning**: Non esiste alcuna strategia di versioning se Valerio cambia il formato del payload API.

---

## 13. Contatti del Progetto

| Ruolo | Contatto | Note |
|-------|---------|------|
| Fornitore dati esterno | **Valerio** (Ambientali Fattori / ARPES) | Schema payload Kafka, endpoint API |
| Cliente / Autorità sanitaria | Autorità regionali Campania, Molise, Calabria | Accesso ai dati sulle malattie |
| Accesso DB GESAN | Reparto IT ASL Campania | Credenziali VPN, DB sola lettura a 10.10.13.11 |

---

*Buona fortuna. L'architettura è solida — il lavoro principale che rimane è il collegamento degli endpoint API al service layer, il completamento dei modelli analitici e l'approvvigionamento dei dati sulla qualità dell'acqua.*
