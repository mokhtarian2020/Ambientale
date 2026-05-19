# Guida Integrazione Fornitore Dati Ambientali (HealthTrace)

Questo documento definisce in modo operativo cosa l'azienda di fattori ambientali deve implementare/aggiornare per integrarsi con la piattaforma HealthTrace attuale.

## 1) Ambito Integrazione

HealthTrace utilizza due pipeline coordinate:

- `Flusso Analitico (batch)` per DWH, BI e modelli ML.
- `Flusso Rapido (streaming)` per alert a bassa latenza.

Entrambi i flussi usano Kafka con chiave di partizione `istat_code` (codice comune a 6 cifre).

---

## 2) Topic Kafka Richiesti

Il fornitore deve supportare i seguenti topic:

- `environmental-ingestion-air`
  - Scopo: batch ARPAC (statistiche giornaliere aggregate)
  - Key: `istat_code`
- `environmental-ingestion-meteo`
  - Scopo: batch MeteoHub (statistiche giornaliere aggregate)
  - Key: `istat_code`
- `environmental-realtime-air`
  - Scopo: eventi ARPAC near-realtime
  - Key: `istat_code`
- `environmental-realtime-meteo`
  - Scopo: eventi MeteoHub near-realtime
  - Key: `istat_code`

Topic interni HealthTrace (informativi):

- `analytics_trigger` (alert prodotti dai consumer HealthTrace)
- `health-data` (stream sanitario, key `comune_inizio_sintomi_codice_istat`)

---

## 3) Endpoint API che il fornitore deve mantenere

Secondo contratto concordato ed esempi PDF:

- `POST /arpac/data/arpac_data_stat`
- `POST /meteohub/data/meteohub_data_stats`
- Endpoint raw opzionali (debug/backfill):
  - `POST /arpac/data/arpac_data`
  - `POST /meteohub/data/meteohub_data`
- Liste stazioni:
  - `GET /arpac/stations`
  - `GET /meteohub/stations`

### Comportamento richiesto sulle request

- Gli endpoint `_stat` sono `POST` con body JSON (non GET).
- Campo `stats` obbligatorio: `["min","mean","max"]`.
- Supporto e applicazione di `filter_on_range=true`.
- Supporto di `validated=true` per ARPAC.
- Supporto finestre temporali con timezone esplicita UTC.

---

## 4) Contratto Payload (Kafka)

## 4.1 Payload ingestion (batch, giornaliero)

- Topic per sorgente:
  - ARPAC -> `environmental-ingestion-air`
  - MeteoHub -> `environmental-ingestion-meteo`
- Un messaggio per stazione per giorno.
- Chiave di partizione: `istat_code`.

Campi minimi payload:

- `source` (`ARPAC` o `METEOHUB`)
- `station_id`
- `istat_code`
- `latitude`, `longitude`
- `period_start` (UTC ISO-8601)
- `period_end` (UTC ISO-8601)
- `aggregation` (`daily`)
- `parameters[]` con:
  - `parameter`
  - `mean`, `min`, `max`
  - `unit`
- `ingested_at` (UTC ISO-8601)

Campi aggiuntivi:

- ARPAC: `station_type`, `slm`
- MeteoHub: `slm` da arricchire via SRTM se assente

## 4.2 Payload realtime

- Topic per sorgente:
  - ARPAC -> `environmental-realtime-air`
  - MeteoHub -> `environmental-realtime-meteo`
- Chiave di partizione: `istat_code`.

Campi minimi realtime:

- `source`
- `station_id`
- `istat_code`
- `timestamp` (UTC ISO-8601)
- `parameters[]` con:
  - `parameter`
  - `value`
  - `unit`

---

## 5) Regole Qualità Dato e Normalizzazione

Allineamento richiesto tra fornitore e HealthTrace:

- Valori invalidi:
  - `-9999` può comparire anche nelle statistiche in alcuni edge case.
  - Il fornitore deve filtrare quanto possibile.
  - HealthTrace applica comunque un filtro client-side aggiuntivo.
- Unità:
  - Coerenza e unità esplicite sempre.
  - Conversioni note usate in HealthTrace:
    - `µg/m**3`, `μg/m**3` -> `μg/m³`
    - `kg/m**2` -> `mm`
    - `K` -> `°C`
- Naming parametri:
  - `PM2,5` normalizzato in `PM2.5`.
- Timezone:
  - Sempre UTC esplicito in API e payload Kafka.

---

## 6) Policy eleggibilità stazioni

Per evitare segnali poco rilevanti (aree non abitate/alta quota):

- Stazioni preferite con `slm < 500m`.
- Tipi ARPAC ammessi: `FONDO`, `TRAFFICO`.
- `elev_ref` MeteoHub è quota sensore, non quota stazione.
  - Per il filtro stazione si usa quota SRTM.

---

## 7) Comportamento lato HealthTrace (informativo per il fornitore)

- Consumer ingestion:
  - Legge topic ingestion.
  - Aggrega per `(istat_code, date, source)`.
  - Applica aggregazione IDW.
  - Scrive nel DWH `environmental_daily_aggregated`.
- Consumer realtime:
  - Legge topic realtime.
  - Applica controlli soglia.
  - Emette eventi su `analytics_trigger`.

Esempi soglie attuali:

- `NO2 > 200 μg/m³`
- `PM10 > 50 μg/m³`
- `PM2.5 > 25 μg/m³`
- `O3 > 120 μg/m³`
- `SO2 > 350 μg/m³`
- `temperature > 35 °C`
- `relative_humidity > 90%`

---

## 8) Punti da chiudere in sessione di allineamento

Da confermare tra fornitore e HealthTrace:

- Endpoint bootstrap Kafka finali e modalità auth.
- Modalità pubblicazione:
  - fornitore direttamente sui topic HealthTrace oppure bridge.
- Retention topic per replay (consigliato minimo: 7 giorni su ingestion).
- Strategia versionamento schema JSON.
- SLA realtime (latenza evento->alert).
- Strategia backfill storico:
  - intervallo date
  - API pull vs consegna batch file

---

## 9) Checklist Go-Live

Go-live approvato quando tutte vere:

- [ ] Risposte `_stat` corrette su ARPAC e MeteoHub.
- [ ] Pubblicazione corretta su 4 topic ambientali con key corretta.
- [ ] Payload con campi UTC e unità conformi.
- [ ] Valori invalidi gestiti senza inquinare le medie giornaliere.
- [ ] Consumer HealthTrace ingestiscono senza errori di schema.
- [ ] Dati visibili in `environmental_daily_aggregated`.
- [ ] Alert realtime pubblicati su `analytics_trigger`.
- [ ] Backfill completato sul periodo storico concordato.

