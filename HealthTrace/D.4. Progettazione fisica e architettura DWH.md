# D.4 – Progettazione Fisica e Architettura DWH

**Sistema:** HealthTrace – Piattaforma di Sorveglianza Sanitaria Ambientale  
**Regioni di competenza:** Campania · Molise · Calabria  
**Fornitore dati ambientali:** Ambientali Fattori / ARPES (referente: Valerio)  
**Data:** 13 maggio 2026

---

## Indice

1. [Progettazione del Data Ingestor per Dati Ambientali](#1-progettazione-del-data-ingestor-per-dati-ambientali)
2. [JOB di ETL](#2-job-di-etl)
3. [Progettazione del DWH](#3-progettazione-del-dwh)
   - [3.1 ER Schema / Diagram](#31-er-schema--diagram)
   - [3.2 DML SQL](#32-dml-sql)
   - [3.3 DDL SQL](#33-ddl-sql)

---

## 1. Progettazione del Data Ingestor per Dati Ambientali

### 1.1 Panoramica Generale

Il sistema HealthTrace acquisisce dati ambientali da due sorgenti eterogene esposte dall'API **Ambientali Fattori / ARPES**:

| Sorgente | Tipo dati | Endpoint API |
|---|---|---|
| **ARPAC** | Qualità dell'aria (NO₂, PM10, PM2.5, O₃, SO₂) | `POST /arpac/data/arpac_data_stat` |
| **MeteoHub** | Dati meteorologici (temperatura, umidità, precipitazioni, vento, pressione) | `POST /meteohub/data/meteohub_data_stats` |

Questi dati alimentano **due flussi elaborativi distinti e indipendenti**:

```xml
<!-- draw.io — incolla su app.diagrams.net → File → Import → incolla XML -->
<mxfile host="app.diagrams.net">
  <diagram name="HealthTrace — Pipeline Overview">
    <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" pageWidth="1169" pageHeight="827">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="2" value="&lt;b&gt;AMBIENTALI FATTORI / ARPES&lt;/b&gt;&lt;br/&gt;POST /arpac/data/arpac_data_stat (batch)&lt;br/&gt;POST /meteohub/data/meteohub_data_stats" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="240" y="40" width="480" height="80" as="geometry" />
        </mxCell>
        <mxCell id="3" value="HTTP POST (JSON)" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="2" target="4" parent="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="4" value="&lt;b&gt;Environmental Ingestion Service&lt;/b&gt;&lt;br/&gt;scheduler: cron giornaliero 01:00 UTC&lt;br/&gt;&lt;br/&gt;• Censimento stazioni (station_census_service)&lt;br/&gt;• Filtro validità stazione (slm, tipo)&lt;br/&gt;• Normalizzazione unità di misura&lt;br/&gt;• Filtraggio valori invalidi (-9999)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="190" y="200" width="580" height="120" as="geometry" />
        </mxCell>
        <mxCell id="5" value="Kafka publish (chiave: istat_code)" style="edgeStyle=orthogonalEdgeStyle;html=1;exitX=0.2;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" source="4" target="6" parent="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="7" value="Kafka publish (chiave: istat_code)" style="edgeStyle=orthogonalEdgeStyle;html=1;exitX=0.8;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" source="4" target="8" parent="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="6" value="&lt;b&gt;FLUSSO ANALITICO&lt;/b&gt;&lt;br/&gt;(Batch / Giornaliero)&lt;br/&gt;&lt;br/&gt;Topic: environmental-ingestion-air&lt;br/&gt;Topic: environmental-ingestion-meteo&lt;br/&gt;&lt;br/&gt;IngestionConsumer&lt;br/&gt;→ buffer per comune&lt;br/&gt;→ IDW aggregation&lt;br/&gt;→ UPSERT DWH" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="40" y="420" width="320" height="200" as="geometry" />
        </mxCell>
        <mxCell id="8" value="&lt;b&gt;FLUSSO REALTIME ALERT&lt;/b&gt;&lt;br/&gt;(Near-Realtime / Streaming)&lt;br/&gt;&lt;br/&gt;Topic: environmental-realtime-air&lt;br/&gt;Topic: environmental-realtime-meteo&lt;br/&gt;&lt;br/&gt;RealtimeAlertConsumer&lt;br/&gt;→ confronto soglie&lt;br/&gt;→ nessuna scrittura DB&lt;br/&gt;→ publish analytics_trigger" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="600" y="420" width="320" height="200" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### 1.2 Flusso Analitico (Batch)

Il flusso analitico è il cuore del sistema di sorveglianza. Ha il compito di produrre, per ogni comune (identificato dall'`istat_code` a 6 cifre), un **unico valore rappresentativo giornaliero** per ciascun parametro ambientale attraverso interpolazione spaziale IDW (Inverse Distance Weighting).

#### 1.2.1 Fase di Acquisizione — Environmental Ingestion Service

Lo scheduler invoca quotidianamente (01:00 UTC) il **Servizio di Acquisizione Ambientale**, che esegue le seguenti operazioni in sequenza:

**Passo 1 – Censimento Stazioni**

Prima di acquisire i dati, il servizio carica il registro delle stazioni valide. Una stazione è considerata **valida per l'analisi** se soddisfa tutte le condizioni seguenti:

| Criterio | ARPAC | MeteoHub |
|---|---|---|
| `istat_code` non nullo | ✓ obbligatorio | ✓ obbligatorio |
| `slm < 500 m` (quota s.l.m.) | ✓ | ✓ |
| `station_type` ∈ {`FONDO`, `TRAFFICO`} | ✓ (INDUSTRIALE escluso) | n/a — nessun filtro tipo |

Per le stazioni MeteoHub prive del campo `slm`, l'elevazione viene recuperata tramite un servizio esterno di dati di elevazione digitale (DEM).

**Passo 2 – Chiamata API verso ARPES**

Per ogni `istat_code` nel territorio di competenza, il servizio esegue una chiamata `POST` agli endpoint ARPES con il seguente corpo JSON:

```json
{
  "istat_code": "063049",
  "start_timestamp": "2026-05-12T00:00:00+00:00",
  "end_timestamp":   "2026-05-12T23:59:59+00:00",
  "validated": true,
  "filter_on_range": true,
  "stats": ["min", "mean", "max"]
}
```

> **Nota tecnica importante:** Il parametro `validated` è esclusivo delle chiamate ARPAC. Le chiamate MeteoHub **non devono includere questo campo** — la sua presenza causerebbe un errore lato API.

La risposta dell'API restituisce un array di oggetti stazione con il seguente schema:

```json
[
  {
    "station_id": "STA_001",
    "istat_code": "063049",
    "type": "FONDO",
    "slm": 42.0,
    "latitude": 40.853,
    "longitude": 14.268,
    "source": "ARPAC",
    "sensors": [
      {
        "parameter": "NO2",
        "unit": "µg/m**3",
        "data": { "min": 9.11, "mean": 24.95, "max": 43.48 }
      }
    ]
  }
]
```

**Passo 3 – Normalizzazione e Filtraggio**

Il servizio applica le seguenti trasformazioni prima della pubblicazione su Kafka:

*Normalizzazione delle unità di misura:*

| Unità ricevuta dall'API | Unità canonica | Fattore di conversione |
|---|---|---|
| `µg/m**3`, `μg/m**3`, `ug/m3` | `μg/m³` | × 1,0 |
| `mg/m**3`, `mg/m3` | `μg/m³` | × 1.000,0 |
| `K` (Kelvin) | `°C` | − 273,15 |
| `kg/m**2`, `kg/m2` | `mm` (precipitazioni) | × 1,0 |
| `km/h` | `m/s` | × 1/3,6 |
| `Pa` | `hPa` | × 0,01 |
| `ppm` | `ppb` | × 1.000,0 |

*Normalizzazione dei nomi dei parametri:*
- `PM2,5` → `PM2.5` (virgola decimale italiana → punto)

*Filtraggio valori invalidi:*
- I valori sentinella ARPAC (`−9999`) e i valori `null` MeteoHub vengono scartati prima della pubblicazione su Kafka.

**Passo 4 – Pubblicazione su Kafka**

Per ogni stazione valida con almeno un parametro non nullo, il servizio pubblica **un messaggio Kafka** nel topic appropriato, usando `istat_code` come chiave di partizione. Questo garantisce che tutti i messaggi relativi allo stesso comune atterrino sulla stessa partizione Kafka, consentendo al consumer di aggregarli senza join cross-partition.

Struttura del messaggio Kafka (flusso analitico):

```json
{
  "source": "ARPAC",
  "station_id": "STA_001",
  "istat_code": "063049",
  "latitude": 40.853,
  "longitude": 14.268,
  "period_start": "2026-05-12T00:00:00Z",
  "period_end":   "2026-05-12T23:59:59Z",
  "aggregation": "daily",
  "parameters": [
    { "parameter": "NO2",   "mean": 24.95, "min": 9.11, "max": 43.48, "unit": "μg/m³" },
    { "parameter": "PM10",  "mean": 31.20, "min": 18.5, "max": 52.10, "unit": "μg/m³" },
    { "parameter": "PM2.5", "mean": 18.40, "min": 10.2, "max": 29.80, "unit": "μg/m³" }
  ],
  "ingested_at": "2026-05-13T01:05:00Z",
  "station_type": "FONDO",
  "slm": 42.0
}
```

#### 1.2.2 Fase di Consumo e Aggregazione IDW — IngestionConsumer

Il componente `IngestionConsumer` legge in modo continuo dai topic `environmental-ingestion-air` e `environmental-ingestion-meteo`. Per ogni tupla `(istat_code, data, source)` accumula tutti i messaggi ricevuti e applica l'algoritmo **IDW (Inverse Distance Weighting)** per produrre un unico valore rappresentativo del comune.

**Algoritmo IDW — Formulazione matematica:**

Per ogni parametro ambientale $p$, il valore aggregato del comune è:

$$\hat{v}_p = \frac{\displaystyle\sum_{i=1}^{n} \frac{v_{p,i}}{d_i^{\,\alpha}}}{\displaystyle\sum_{i=1}^{n} \frac{1}{d_i^{\,\alpha}}}$$

dove:
- $v_{p,i}$ = valore del parametro $p$ misurato dalla stazione $i$
- $d_i$ = distanza Haversine (km) tra la stazione $i$ e il centroide del comune target
- $\alpha$ = esponente di peso (configurato a `2,0` per default)
- Le stazioni co-locate ($d_i < 0{,}001$ km) ricevono $d_i = 0{,}001$ per evitare divisione per zero

La distanza Haversine è calcolata con raggio terrestre $R = 6{.}371$ km:

$$d = 2R \arcsin\!\left(\sqrt{\sin^2\!\tfrac{\Delta\phi}{2} + \cos\phi_1\cos\phi_2\sin^2\!\tfrac{\Delta\lambda}{2}}\right)$$

**Scrittura nel DWH:**

Il risultato dell'aggregazione viene scritto in `environmental_daily_aggregated` tramite **UPSERT PostgreSQL**:

```sql
INSERT INTO environmental_daily_aggregated
    (istat_code, source, period_date, parameters, station_count, created_at)
VALUES
    (:istat_code, :source, :period_date, :parameters::jsonb, :station_count, NOW())
ON CONFLICT (istat_code, source, period_date)
DO UPDATE SET
    parameters    = EXCLUDED.parameters,
    station_count = EXCLUDED.station_count,
    updated_at    = NOW();
```

Questo meccanismo garantisce che i dati NRT (near-real-time) vengano automaticamente sovrascritti dai dati validati non appena disponibili, senza necessità di alcun topic di eliminazione separato.

### 1.3 Flusso Realtime Alert (Streaming)

Il flusso realtime è completamente separato dal flusso analitico e **non scrive nulla nel database**. Il suo unico scopo è rilevare in tempo reale i superamenti di soglia e notificare il motore di analisi a valle.

#### 1.3.1 Struttura del Payload Realtime

```json
{
  "source": "ARPAC",
  "station_id": "STA_001",
  "istat_code": "063049",
  "timestamp": "2026-05-12T10:00:00Z",
  "parameters": [
    { "parameter": "PM2.5", "value": 31.7, "unit": "μg/m³" }
  ]
}
```

#### 1.3.2 Soglie di Allerta Configurate

| Parametro | Soglia | Unità | Riferimento normativo |
|---|---|---|---|
| NO₂ | > 200 | μg/m³ | Limite orario EU (Direttiva 2008/50/CE) |
| PM10 | > 50 | μg/m³ | Limite giornaliero EU |
| PM2.5 | > 25 | μg/m³ | Limite annuale EU (proxy giornaliero) |
| O₃ | > 120 | μg/m³ | Target EU 8 ore |
| SO₂ | > 350 | μg/m³ | Limite orario EU |
| temperature | > 35 | °C | Proxy ondata di calore (SNPA) |
| relative_humidity | > 90 | % | Proxy rischio Legionella / muffa |

#### 1.3.3 Comportamento del RealtimeAlertConsumer

Il `RealtimeAlertConsumer` legge da `environmental-realtime-air` e `environmental-realtime-meteo`. Per ogni messaggio ricevuto:

1. Confronta ogni valore dei parametri con le soglie configurate
2. In caso di superamento, pubblica immediatamente un messaggio di allerta sul topic `analytics_trigger` con chiave `istat_code`
3. Il messaggio di trigger contiene: `istat_code`, `parameter`, `value`, `threshold`, `timestamp`, `source`

Il flusso è **fire-and-forget**: la persistenza degli alert è responsabilità del motore AI a valle che consuma il topic `analytics_trigger`.

---

## 2. JOB di ETL

### 2.1 Architettura dei Job Schedulati

Il sistema prevede job ETL schedulati per il flusso analitico e per la manutenzione del DWH. I job sono orchestrati tramite scheduler Linux (`cron`) con previsione di migrazione ad **Apache Airflow** nelle fasi successive del progetto.

```xml
<!-- draw.io — incolla su app.diagrams.net → File → Import → incolla XML -->
<mxfile host="app.diagrams.net">
  <diagram name="Scheduler (cron Linux)">
    <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="2" value="&lt;b&gt;SCHEDULER (cron Linux)&lt;/b&gt;" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=16;" vertex="1" parent="1">
          <mxGeometry x="100" y="20" width="600" height="40" as="geometry" />
        </mxCell>
        <mxCell id="3" value="&lt;b&gt;JOB-01&lt;/b&gt;&lt;br/&gt;Daily Environmental Ingestion&lt;br/&gt;Ogni giorno 01:00 UTC" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="80" y="80" width="260" height="100" as="geometry" />
        </mxCell>
        <mxCell id="4" value="&lt;b&gt;JOB-02&lt;/b&gt;&lt;br/&gt;Station Census Refresh&lt;br/&gt;Ogni domenica 00:00 UTC" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="460" y="80" width="260" height="100" as="geometry" />
        </mxCell>
        <mxCell id="5" value="&lt;b&gt;JOB-03&lt;/b&gt;&lt;br/&gt;DWH Integrity Check&lt;br/&gt;Ogni giorno 06:00 UTC&lt;br/&gt;(dopo JOB-01)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="80" y="220" width="260" height="100" as="geometry" />
        </mxCell>
        <mxCell id="6" value="&lt;b&gt;JOB-04&lt;/b&gt;&lt;br/&gt;ML Feature Refresh&lt;br/&gt;Ogni giorno 07:00 UTC&lt;br/&gt;(dopo JOB-03)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;" vertex="1" parent="1">
          <mxGeometry x="460" y="220" width="260" height="100" as="geometry" />
        </mxCell>
        <mxCell id="7" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="3" target="5" parent="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="8" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="5" target="6" parent="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### 2.2 JOB-01 – Daily Environmental Ingestion

| Attributo | Valore |
|---|---|
| **ID** | JOB-01 |
| **Nome** | Daily Environmental Ingestion |
| **Schedule** | `0 1 * * *` (ogni giorno alle 01:00 UTC) |
| **Dipendenze** | API ARPES raggiungibile · Kafka broker attivo · PostgreSQL attivo |
| **SLA** | Completamento entro le 03:00 UTC (finestra di 2 ore) |

**Descrizione funzionale:**

Il job acquisisce i dati ambientali giornalieri di tutte le stazioni ARPAC e MeteoHub valide nel territorio di competenza (Campania, Molise, Calabria). Per ogni comune (`istat_code`) con almeno una stazione attiva:

1. Interroga `POST /arpac/data/arpac_data_stat` con `validated=true` per i dati di qualità dell'aria
2. Interroga `POST /meteohub/data/meteohub_data_stats` per i dati meteorologici
3. Applica la normalizzazione delle unità di misura e il filtraggio dei valori `−9999`
4. Pubblica un messaggio Kafka per ogni stazione valida:
   - ARPAC → topic `environmental-ingestion-air`
   - MeteoHub → topic `environmental-ingestion-meteo`

**Flusso di elaborazione dettagliato:**

```xml
<!-- draw.io — incolla su app.diagrams.net → File → Import → incolla XML -->
<mxfile host="app.diagrams.net">
  <diagram name="JOB-01 — Flusso di Elaborazione">
    <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="2" value="&lt;b&gt;ARPES API&lt;/b&gt;&lt;br/&gt;ARPAC + MeteoHub" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
          <mxGeometry x="250" y="40" width="300" height="60" as="geometry" />
        </mxCell>
        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="2" target="3" parent="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="3" value="&lt;b&gt;[1] Carica registro stazioni valide&lt;/b&gt;&lt;br/&gt;slm &amp;lt; 500m · tipo FONDO/TRAFFICO (ARPAC) · istat_code non nullo" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
          <mxGeometry x="150" y="160" width="500" height="60" as="geometry" />
        </mxCell>
        <mxCell id="e2" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="3" target="4" parent="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="4" value="&lt;b&gt;[2] Per ogni istat_code nei comuni di competenza&lt;/b&gt;&lt;br/&gt;POST /arpac/data/arpac_data_stat (validated=true, filter_on_range=true)&lt;br/&gt;→ parse → normalizza unità → filtra -9999 → pubblica su environmental-ingestion-air&lt;br/&gt;&lt;br/&gt;POST /meteohub/data/meteohub_data_stats (filter_on_range=true, NO validated)&lt;br/&gt;→ parse → normalizza unità → filtra null → pubblica su environmental-ingestion-meteo" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
          <mxGeometry x="100" y="280" width="600" height="120" as="geometry" />
        </mxCell>
        <mxCell id="e3" style="edgeStyle=orthogonalEdgeStyle;html=1;" edge="1" source="4" target="5" parent="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="5" value="&lt;b&gt;[3] IngestionConsumer (processo sempre attivo)&lt;/b&gt;&lt;br/&gt;• Bufferizza messaggi per (istat_code, period_date, source)&lt;br/&gt;• Calcola aggregazione IDW con centroide del comune come punto target&lt;br/&gt;• UPSERT → environmental_daily_aggregated" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;" vertex="1" parent="1">
          <mxGeometry x="100" y="460" width="600" height="100" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

**Gestione degli errori:**

| Condizione di errore | Comportamento |
|---|---|
| API ARPES non raggiungibile | Retry esponenziale (max 5 tentativi con backoff), poi log CRITICAL |
| Stazione con tutti i valori −9999 | Skip silenzioso, log DEBUG |
| `istat_code` assente nella risposta API | Stazione ignorata, log WARNING |
| Kafka non raggiungibile | Retry con attesa massima configurata, poi terminazione con errore |
| DB non raggiungibile nel consumer | Log ERROR, offset Kafka non committato → messaggio rielaborato al riavvio |
| API MeteoHub con parametro `validated` | L'API restituisce errore — mai inviare `validated` a MeteoHub |

**Output atteso:**

- N righe nuove (o aggiornate) in `environmental_daily_aggregated` — una per `istat_code` per sorgente per giorno
- Log: numero messaggi pubblicati, stazioni saltate, errori API, durata totale

---

### 2.3 JOB-02 – Station Census Refresh

| Attributo | Valore |
|---|---|
| **ID** | JOB-02 |
| **Nome** | Station Census Refresh |
| **Schedule** | `0 0 * * 0` (ogni domenica alle 00:00 UTC) |
| **Dipendenze** | API ARPES (endpoint stazioni) · Servizio DEM esterno |

**Descrizione funzionale:**

Il job aggiorna il registro delle stazioni, sorgente di verità per JOB-01. Per ogni stazione restituita dall'API:

1. Verifica la presenza del valore di quota s.l.m. Per le stazioni MeteoHub prive di tale informazione, la recupera tramite un servizio DEM esterno
2. Applica i criteri di validità: quota < 500 m, tipo stazione (ARPAC), `istat_code` non nullo
3. Persiste il registro aggiornato

**Output atteso:**

- Registro stazioni aggiornato con tutte le stazioni valide, arricchite di quota e `istat_code`
- Log: totale stazioni ARPAC e MeteoHub attive, stazioni escluse per quota o tipo

---

### 2.4 JOB-03 – DWH Integrity Check

| Attributo | Valore |
|---|---|
| **ID** | JOB-03 |
| **Nome** | DWH Integrity Check |
| **Schedule** | `0 6 * * *` (ogni giorno alle 06:00 UTC, dopo JOB-01) |
| **Dipendenze** | PostgreSQL attivo |

**Descrizione funzionale:**

Verifica la completezza dei dati nel DWH per la giornata precedente. Emette un alert nel log (livello WARNING o CRITICAL) se la copertura risulta inferiore all'80% dei comuni attesi.

**Query di controllo utilizzata:**

```sql
SELECT
    source,
    COUNT(DISTINCT istat_code)          AS comuni_coperti,
    MIN(station_count)                  AS min_stazioni,
    MAX(station_count)                  AS max_stazioni,
    ROUND(AVG(station_count)::numeric, 1) AS avg_stazioni
FROM environmental_daily_aggregated
WHERE period_date = CURRENT_DATE - INTERVAL '1 day'
GROUP BY source
ORDER BY source;
```

**Output atteso:**

- Report su stdout con copertura per sorgente (ARPAC, MeteoHub)
- Log WARNING se copertura < 80%; log CRITICAL se < 50%
- Identificazione dei comuni mancanti tramite confronto con il registro stazioni

---

### 2.5 JOB-04 – ML Feature Refresh

| Attributo | Valore |
|---|---|
| **ID** | JOB-04 |
| **Nome** | ML Feature Refresh |
| **Schedule** | `0 7 * * *` (ogni giorno alle 07:00 UTC, dopo JOB-03) |
| **Dipendenze** | DWH aggiornato · DB GESAN raggiungibile |

**Descrizione funzionale:**

Aggiorna il dataset di addestramento dei modelli ML unendo i dati ambientali del DWH HealthTrace con i casi di malattia provenienti dal DB GESAN ASL Campania. Il join tra le due sorgenti avviene sul campo `istat_code` e sulla data.

**Sorgenti dati:**

| Sorgente | Connessione | Accesso |
|---|---|---|
| DWH HealthTrace | `environmental_daily_aggregated` (PostgreSQL locale) | Lettura/scrittura |
| DB GESAN | Database GESAN ASL Campania | Sola lettura |

**Schema del dataset di output (una riga per istat_code per giorno):**

| Colonna | Tipo | Sorgente | Descrizione |
|---|---|---|---|
| `istat_code` | VARCHAR(6) | DWH | Codice ISTAT comune |
| `period_date` | DATE | DWH | Data di riferimento |
| `no2` | FLOAT | ARPAC | NO₂ μg/m³ (IDW) |
| `pm10` | FLOAT | ARPAC | PM10 μg/m³ (IDW) |
| `pm25` | FLOAT | ARPAC | PM2.5 μg/m³ (IDW) |
| `ozone` | FLOAT | ARPAC | O₃ μg/m³ (IDW) |
| `so2` | FLOAT | ARPAC | SO₂ μg/m³ (IDW) |
| `temperature` | FLOAT | MeteoHub | Temperatura °C (IDW) |
| `relative_humidity` | FLOAT | MeteoHub | Umidità % (IDW) |
| `precipitation` | FLOAT | MeteoHub | Precipitazioni mm (IDW) |
| `wind_speed` | FLOAT | MeteoHub | Velocità vento m/s (IDW) |
| `pressure` | FLOAT | MeteoHub | Pressione hPa (IDW) |
| `influenza_cases` | INT | GESAN | Casi influenza nel comune |
| `legionellosis_cases` | INT | GESAN | Casi legionellosi nel comune |
| `hepatitis_a_cases` | INT | GESAN | Casi epatite A nel comune |
| `month` | INT | Calcolato | Mese (1–12) |
| `week_of_year` | INT | Calcolato | Settimana dell'anno (1–53) |
| `season` | VARCHAR | Calcolato | Stagione meteorologica |

**Output atteso:**

- Dataset aggiornato per ogni malattia target (influenza, legionellosi, epatite A), pronto per i modelli predittivi del sistema

---

## 3. Progettazione del DWH

Il Data Warehouse di HealthTrace è realizzato su **PostgreSQL 14** con le estensioni **TimescaleDB** (per la gestione ottimizzata delle serie temporali) e **PostGIS** (per le query geospaziali). Il DWH è organizzato in tre aree funzionali:

1. **Schema Operativo** — gestione dei casi di malattia infettiva e dei pazienti
2. **Schema Ambientale** — archiviazione e aggregazione dei dati ambientali ARPAC e MeteoHub
3. **Schema Analytics** — tabelle di correlazione e supporto ai modelli di ML

### 3.1 ER Schema / Diagram

#### 3.1.1 Diagramma Entity-Relationship

```xml
<!-- draw.io — incolla su app.diagrams.net → File → Import → incolla XML -->
<mxfile host="app.diagrams.net">
  <diagram name="HealthTrace DWH — ER Diagram">
    <mxGraphModel dx="1422" dy="762" grid="0" gridSize="10" pageWidth="1100" pageHeight="870">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- Section headers -->
        <mxCell id="h1" value="Schema Operativo — Malattie Infettive"
          style="text;html=1;strokeColor=none;fillColor=none;align=center;fontSize=13;fontStyle=1;fontColor=#555;"
          vertex="1" parent="1">
          <mxGeometry x="30" y="15" width="570" height="28" as="geometry" />
        </mxCell>
        <mxCell id="h2" value="Schema DWH — Dati Ambientali &amp; Analytics"
          style="text;html=1;strokeColor=none;fillColor=none;align=center;fontSize=13;fontStyle=1;fontColor=#555;"
          vertex="1" parent="1">
          <mxGeometry x="710" y="15" width="330" height="28" as="geometry" />
        </mxCell>

        <!-- Vertical divider -->
        <mxCell id="div" value="" style="endArrow=none;startArrow=none;html=1;strokeColor=#bbbbbb;strokeWidth=2;dashed=1;"
          edge="1" parent="1">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="688" y="50"  as="sourcePoint" />
            <mxPoint x="688" y="850" as="targetPoint" />
          </mxGeometry>
        </mxCell>

        <!-- USERS -->
        <mxCell id="u" value="users"
          style="swimlane;fontStyle=1;align=center;startSize=28;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;html=1;"
          vertex="1" parent="1">
          <mxGeometry x="30" y="60" width="240" height="124" as="geometry" />
        </mxCell>
        <mxCell id="u1" value="PK  id"
          style="text;strokeColor=none;fillColor=#dae8fc;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="u">
          <mxGeometry y="28" width="240" height="24" as="geometry" />
        </mxCell>
        <mxCell id="u2" value="username · email"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="u">
          <mxGeometry y="52" width="240" height="24" as="geometry" />
        </mxCell>
        <mxCell id="u3" value="role (userrole)"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="u">
          <mxGeometry y="76" width="240" height="24" as="geometry" />
        </mxCell>
        <mxCell id="u4" value="is_active"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="u">
          <mxGeometry y="100" width="240" height="24" as="geometry" />
        </mxCell>

        <!-- PATIENTS -->
        <mxCell id="p" value="patients"
          style="swimlane;fontStyle=1;align=center;startSize=28;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;html=1;"
          vertex="1" parent="1">
          <mxGeometry x="30" y="250" width="240" height="148" as="geometry" />
        </mxCell>
        <mxCell id="p1" value="PK  id"
          style="text;strokeColor=none;fillColor=#d5e8d4;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="p">
          <mxGeometry y="28" width="240" height="24" as="geometry" />
        </mxCell>
        <mxCell id="p2" value="tax_code (UNIQUE)"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="p">
          <mxGeometry y="52" width="240" height="24" as="geometry" />
        </mxCell>
        <mxCell id="p3" value="surname · name · gender"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="p">
          <mxGeometry y="76" width="240" height="24" as="geometry" />
        </mxCell>
        <mxCell id="p4" value="birth_date"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="p">
          <mxGeometry y="100" width="240" height="24" as="geometry" />
        </mxCell>
        <mxCell id="p5" value="residence_municipality"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="p">
          <mxGeometry y="124" width="240" height="24" as="geometry" />
        </mxCell>

        <!-- DISEASE_REPORTS -->
        <mxCell id="dr" value="disease_reports"
          style="swimlane;fontStyle=1;align=center;startSize=28;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;html=1;"
          vertex="1" parent="1">
          <mxGeometry x="360" y="100" width="270" height="172" as="geometry" />
        </mxCell>
        <mxCell id="dr1" value="PK  id"
          style="text;strokeColor=none;fillColor=#fff2cc;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="dr">
          <mxGeometry y="28" width="270" height="24" as="geometry" />
        </mxCell>
        <mxCell id="dr2" value="FK  patient_id"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="dr">
          <mxGeometry y="52" width="270" height="24" as="geometry" />
        </mxCell>
        <mxCell id="dr3" value="FK  reporting_doctor_id"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="dr">
          <mxGeometry y="76" width="270" height="24" as="geometry" />
        </mxCell>
        <mxCell id="dr4" value="disease_name"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="dr">
          <mxGeometry y="100" width="270" height="24" as="geometry" />
        </mxCell>
        <mxCell id="dr5" value="symptom_onset_date"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="dr">
          <mxGeometry y="124" width="270" height="24" as="geometry" />
        </mxCell>
        <mxCell id="dr6" value="symptom_onset_municipality"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="dr">
          <mxGeometry y="148" width="270" height="24" as="geometry" />
        </mxCell>

        <!-- EPIDEMIOLOGICAL_INVESTIGATIONS -->
        <mxCell id="ei" value="epidemiological_investigations"
          style="swimlane;fontStyle=1;align=center;startSize=28;fillColor=#f8cecc;strokeColor=#b85450;fontSize=11;html=1;"
          vertex="1" parent="1">
          <mxGeometry x="350" y="350" width="280" height="148" as="geometry" />
        </mxCell>
        <mxCell id="ei1" value="PK  id"
          style="text;strokeColor=none;fillColor=#f8cecc;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="ei">
          <mxGeometry y="28" width="280" height="24" as="geometry" />
        </mxCell>
        <mxCell id="ei2" value="FK  patient_id"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="ei">
          <mxGeometry y="52" width="280" height="24" as="geometry" />
        </mxCell>
        <mxCell id="ei3" value="FK  report_id"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="ei">
          <mxGeometry y="76" width="280" height="24" as="geometry" />
        </mxCell>
        <mxCell id="ei4" value="FK  investigator_id"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="ei">
          <mxGeometry y="100" width="280" height="24" as="geometry" />
        </mxCell>
        <mxCell id="ei5" value="case_type · investigation_date"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="ei">
          <mxGeometry y="124" width="280" height="24" as="geometry" />
        </mxCell>

        <!-- CONTACT_TRACING -->
        <mxCell id="ct" value="contact_tracing"
          style="swimlane;fontStyle=1;align=center;startSize=28;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=12;html=1;"
          vertex="1" parent="1">
          <mxGeometry x="360" y="580" width="260" height="124" as="geometry" />
        </mxCell>
        <mxCell id="ct1" value="PK  id"
          style="text;strokeColor=none;fillColor=#e1d5e7;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="ct">
          <mxGeometry y="28" width="260" height="24" as="geometry" />
        </mxCell>
        <mxCell id="ct2" value="FK  investigation_id  (CASCADE)"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="ct">
          <mxGeometry y="52" width="260" height="24" as="geometry" />
        </mxCell>
        <mxCell id="ct3" value="contact_name · contact_surname"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="ct">
          <mxGeometry y="76" width="260" height="24" as="geometry" />
        </mxCell>
        <mxCell id="ct4" value="last_contact_date · tested"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="ct">
          <mxGeometry y="100" width="260" height="24" as="geometry" />
        </mxCell>

        <!-- ENVIRONMENTAL_DAILY_AGGREGATED -->
        <mxCell id="eda" value="environmental_daily_aggregated"
          style="swimlane;fontStyle=1;align=center;startSize=28;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;html=1;"
          vertex="1" parent="1">
          <mxGeometry x="710" y="60" width="310" height="172" as="geometry" />
        </mxCell>
        <mxCell id="eda1" value="PK  id"
          style="text;strokeColor=none;fillColor=#dae8fc;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="eda">
          <mxGeometry y="28" width="310" height="24" as="geometry" />
        </mxCell>
        <mxCell id="eda2" value="istat_code · source"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="eda">
          <mxGeometry y="52" width="310" height="24" as="geometry" />
        </mxCell>
        <mxCell id="eda3" value="period_date"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="eda">
          <mxGeometry y="76" width="310" height="24" as="geometry" />
        </mxCell>
        <mxCell id="eda4" value="parameters  JSONB"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="eda">
          <mxGeometry y="100" width="310" height="24" as="geometry" />
        </mxCell>
        <mxCell id="eda5" value="station_count"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="eda">
          <mxGeometry y="124" width="310" height="24" as="geometry" />
        </mxCell>
        <mxCell id="eda6" value="UNIQUE(istat_code, source, period_date)"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=10;verticalAlign=middle;fontStyle=2;"
          vertex="1" parent="eda">
          <mxGeometry y="148" width="310" height="24" as="geometry" />
        </mxCell>

        <!-- ENVIRONMENTAL_DATA -->
        <mxCell id="envd" value="environmental_data"
          style="swimlane;fontStyle=1;align=center;startSize=28;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;html=1;"
          vertex="1" parent="1">
          <mxGeometry x="710" y="305" width="310" height="148" as="geometry" />
        </mxCell>
        <mxCell id="envd1" value="PK  id"
          style="text;strokeColor=none;fillColor=#d5e8d4;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="envd">
          <mxGeometry y="28" width="310" height="24" as="geometry" />
        </mxCell>
        <mxCell id="envd2" value="istat_code · measurement_date"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="envd">
          <mxGeometry y="52" width="310" height="24" as="geometry" />
        </mxCell>
        <mxCell id="envd3" value="pm10 · pm25 · no2 · ozone · so2"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="envd">
          <mxGeometry y="76" width="310" height="24" as="geometry" />
        </mxCell>
        <mxCell id="envd4" value="temperature · humidity · precipitation"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="envd">
          <mxGeometry y="100" width="310" height="24" as="geometry" />
        </mxCell>
        <mxCell id="envd5" value="data_source  (ARPAC | METEOHUB)"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="envd">
          <mxGeometry y="124" width="310" height="24" as="geometry" />
        </mxCell>

        <!-- DISEASE_ENVIRONMENTAL_CORRELATIONS -->
        <mxCell id="dec" value="disease_environmental_correlations"
          style="swimlane;fontStyle=1;align=center;startSize=28;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;html=1;"
          vertex="1" parent="1">
          <mxGeometry x="710" y="525" width="310" height="124" as="geometry" />
        </mxCell>
        <mxCell id="dec1" value="PK  id"
          style="text;strokeColor=none;fillColor=#fff2cc;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="dec">
          <mxGeometry y="28" width="310" height="24" as="geometry" />
        </mxCell>
        <mxCell id="dec2" value="disease_name · parameter"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="dec">
          <mxGeometry y="52" width="310" height="24" as="geometry" />
        </mxCell>
        <mxCell id="dec3" value="r_value · p_value · lag_days"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="dec">
          <mxGeometry y="76" width="310" height="24" as="geometry" />
        </mxCell>
        <mxCell id="dec4" value="istat_code"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="dec">
          <mxGeometry y="100" width="310" height="24" as="geometry" />
        </mxCell>

        <!-- DISEASE_CATEGORIES -->
        <mxCell id="dc" value="disease_categories"
          style="swimlane;fontStyle=1;align=center;startSize=28;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=12;html=1;"
          vertex="1" parent="1">
          <mxGeometry x="710" y="720" width="310" height="124" as="geometry" />
        </mxCell>
        <mxCell id="dc1" value="PK  id"
          style="text;strokeColor=none;fillColor=#ffe6cc;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="dc">
          <mxGeometry y="28" width="310" height="24" as="geometry" />
        </mxCell>
        <mxCell id="dc2" value="name VARCHAR (UNIQUE)"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="dc">
          <mxGeometry y="52" width="310" height="24" as="geometry" />
        </mxCell>
        <mxCell id="dc3" value="icd_code"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="dc">
          <mxGeometry y="76" width="310" height="24" as="geometry" />
        </mxCell>
        <mxCell id="dc4" value="correlation coefficients (r)"
          style="text;strokeColor=none;fillColor=none;align=left;spacingLeft=8;fontSize=11;verticalAlign=middle;"
          vertex="1" parent="dc">
          <mxGeometry y="100" width="310" height="24" as="geometry" />
        </mxCell>

        <!-- RELATIONSHIPS -->

        <!-- users → disease_reports -->
        <mxCell id="r2" value="1:N"
          style="edgeStyle=orthogonalEdgeStyle;html=1;endArrow=ERmany;startArrow=ERone;exitX=1;exitY=0.4;exitDx=0;exitDy=0;entryX=0;entryY=0.25;entryDx=0;entryDy=0;rounded=1;fontStyle=1;fontSize=10;"
          edge="1" source="u" target="dr" parent="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- patients → disease_reports -->
        <mxCell id="r1" value="1:N"
          style="edgeStyle=orthogonalEdgeStyle;html=1;endArrow=ERmany;startArrow=ERone;exitX=1;exitY=0.3;exitDx=0;exitDy=0;entryX=0;entryY=0.7;entryDx=0;entryDy=0;rounded=1;fontStyle=1;fontSize=10;"
          edge="1" source="p" target="dr" parent="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- disease_reports → epidemiological_investigations -->
        <mxCell id="r3" value="1:N"
          style="edgeStyle=orthogonalEdgeStyle;html=1;endArrow=ERmany;startArrow=ERone;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;fontStyle=1;fontSize=10;"
          edge="1" source="dr" target="ei" parent="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- patients → epidemiological_investigations -->
        <mxCell id="r4" value="1:N"
          style="edgeStyle=orthogonalEdgeStyle;html=1;endArrow=ERmany;startArrow=ERone;exitX=1;exitY=0.75;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;rounded=1;fontStyle=1;fontSize=10;"
          edge="1" source="p" target="ei" parent="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- epidemiological_investigations → contact_tracing -->
        <mxCell id="r6" value="1:N"
          style="edgeStyle=orthogonalEdgeStyle;html=1;endArrow=ERmany;startArrow=ERone;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;fontStyle=1;fontSize=10;"
          edge="1" source="ei" target="ct" parent="1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

#### 3.1.2 Relazioni Principali

| Relazione | Cardinalità | Vincolo |
|---|---|---|
| `patients` → `disease_reports` | 1 : N | FK patient_id — ON DELETE RESTRICT |
| `users` → `disease_reports` | 1 : N | FK reporting_doctor_id — ON DELETE RESTRICT |
| `disease_reports` → `epidemiological_investigations` | 1 : N | FK report_id — ON DELETE RESTRICT |
| `epidemiological_investigations` → `contact_tracing` | 1 : N | FK investigation_id — ON DELETE CASCADE |
| `users` → `epidemiological_investigations` | 1 : N | FK investigator_id — ON DELETE RESTRICT |
| `environmental_daily_aggregated` | — | Nessuna FK esterna — tabella autonoma del DWH |

> **Nota sull'integrazione GESAN:** Il join tra i dati ambientali del DWH HealthTrace e i casi di malattia del DB GESAN avviene **esclusivamente nel layer analytics**, tramite corrispondenza tra il campo `istat_code` e il codice ISTAT del comune di inizio sintomi. Non esistono FK tra i due database.

---

### 3.2 DML SQL

Di seguito le query DML principali utilizzate nelle operazioni di routine del sistema.

#### 3.2.1 UPSERT Dati Ambientali Aggregati — Pipeline IDW

```sql
-- Inserisce o aggiorna il record IDW-aggregato giornaliero per un comune.
-- Usato dal IngestionConsumer dopo il calcolo IDW.
-- La semantica UPSERT garantisce che i dati NRT vengano sovrascritti
-- automaticamente dai dati validati quando disponibili.

INSERT INTO environmental_daily_aggregated
    (istat_code, source, period_date, parameters, station_count, created_at)
VALUES
    (:istat_code, :source, :period_date, :parameters::jsonb, :station_count, NOW())
ON CONFLICT (istat_code, source, period_date)
DO UPDATE SET
    parameters    = EXCLUDED.parameters,
    station_count = EXCLUDED.station_count,
    updated_at    = NOW();
```

#### 3.2.2 Lettura Dati Ambientali per Comune e Periodo

```sql
-- Recupera tutti i dati ambientali aggregati per un comune
-- in un intervallo di date. Usato dal DwhDataLoader.

SELECT
    istat_code,
    source,
    period_date,
    parameters,
    station_count
FROM environmental_daily_aggregated
WHERE istat_code  = :istat_code
  AND period_date BETWEEN :date_from AND :date_to
ORDER BY source, period_date;
```

#### 3.2.3 Join ARPAC + MeteoHub — Dataset Piatto per ML

```sql
-- Unisce i dati ARPAC e MeteoHub per lo stesso comune e giorno.
-- Produce una riga piatta per data, pronta per i modelli ML.
-- Usato da JOB-04 (ML Feature Refresh).

SELECT
    COALESCE(a.istat_code,  m.istat_code)   AS istat_code,
    COALESCE(a.period_date, m.period_date)  AS period_date,
    -- Qualità dell'aria (sorgente ARPAC)
    (a.parameters->>'NO2')::float           AS no2,
    (a.parameters->>'PM10')::float          AS pm10,
    (a.parameters->>'PM2.5')::float         AS pm25,
    (a.parameters->>'O3')::float            AS ozone,
    (a.parameters->>'SO2')::float           AS so2,
    -- Meteorologia (sorgente MeteoHub)
    (m.parameters->>'temperature')::float         AS temperature,
    (m.parameters->>'relative_humidity')::float   AS relative_humidity,
    (m.parameters->>'precipitation')::float       AS precipitation,
    (m.parameters->>'wind_speed')::float          AS wind_speed,
    (m.parameters->>'pressure')::float            AS pressure
FROM
    (SELECT * FROM environmental_daily_aggregated WHERE source = 'ARPAC')     a
FULL OUTER JOIN
    (SELECT * FROM environmental_daily_aggregated WHERE source = 'METEOHUB')  m
    ON  a.istat_code  = m.istat_code
    AND a.period_date = m.period_date
WHERE
    COALESCE(a.istat_code,  m.istat_code)  = ANY(:istat_codes)
    AND COALESCE(a.period_date, m.period_date) BETWEEN :date_from AND :date_to
ORDER BY istat_code, period_date;
```

#### 3.2.4 Inserimento Notifica di Malattia Infettiva

```sql
-- Registra una nuova notifica di malattia infettiva nel sistema.
-- Restituisce l'ID del record creato.

INSERT INTO disease_reports (
    patient_id, reporting_doctor_id, disease_name, uosd_diagnosis,
    symptom_onset_date, symptom_onset_municipality,
    hospitalization, vaccination_status, vaccination_doses,
    last_dose_date, vaccine_type, report_date, created_at
) VALUES (
    :patient_id, :reporting_doctor_id, :disease_name, :uosd_diagnosis,
    :symptom_onset_date, :symptom_onset_municipality,
    :hospitalization, :vaccination_status, :vaccination_doses,
    :last_dose_date, :vaccine_type, :report_date, NOW()
)
RETURNING id;
```

#### 3.2.5 Verifica Copertura DWH — JOB-03

```sql
-- Controlla la completezza dei dati per la giornata precedente.
-- Usato da JOB-03 (DWH Integrity Check).

SELECT
    source,
    COUNT(DISTINCT istat_code)              AS comuni_coperti,
    SUM(station_count)                      AS stazioni_totali,
    ROUND(AVG(station_count)::numeric, 1)   AS stazioni_medie,
    MIN(period_date)                        AS data_min,
    MAX(period_date)                        AS data_max
FROM environmental_daily_aggregated
WHERE period_date = CURRENT_DATE - INTERVAL '1 day'
GROUP BY source
ORDER BY source;
```

#### 3.2.6 Correlazioni Statisticamente Significative per Malattia

```sql
-- Recupera le correlazioni calcolate per una malattia target,
-- filtrando quelle statisticamente significative (p < 0.05).
-- Usato dal dashboard di sorveglianza.

SELECT
    disease_name,
    parameter,
    r_value,
    p_value,
    lag_days,
    calculated_at
FROM disease_environmental_correlations
WHERE disease_name = :disease_name
  AND p_value < 0.05
ORDER BY ABS(r_value) DESC;
```

#### 3.2.7 Casi di Malattia per Comune e Periodo

```sql
-- Recupera i casi di malattia con dati demografici del paziente
-- per un comune e un periodo. Usato dai report epidemiologici.

SELECT
    dr.id                           AS report_id,
    dr.disease_name,
    dr.symptom_onset_date,
    dr.symptom_onset_municipality,
    dr.hospitalization,
    p.surname,
    p.name,
    p.birth_date,
    p.gender,
    p.residence_municipality
FROM disease_reports dr
JOIN patients p ON p.id = dr.patient_id
WHERE dr.symptom_onset_municipality = :municipality
  AND dr.symptom_onset_date BETWEEN :date_from AND :date_to
ORDER BY dr.symptom_onset_date DESC;
```

#### 3.2.8 Riepilogo Casi per Malattia e Settimana (Curva Epidemica)

```sql
-- Costruisce la curva epidemica settimanale per una malattia target.
-- Usato dai modelli ARIMAX e dal dashboard di sorveglianza.

SELECT
    DATE_TRUNC('week', symptom_onset_date)  AS week_start,
    disease_name,
    symptom_onset_municipality,
    COUNT(*)                                AS case_count
FROM disease_reports
WHERE disease_name ILIKE :disease_pattern
  AND symptom_onset_date BETWEEN :date_from AND :date_to
GROUP BY week_start, disease_name, symptom_onset_municipality
ORDER BY week_start, symptom_onset_municipality;
```

---

### 3.3 DDL SQL

Il DDL è suddiviso per area funzionale e va eseguito nella sequenza indicata su **PostgreSQL 14** con le estensioni **TimescaleDB** e **PostGIS**.

---

#### 3.3.1 Estensioni e Tipi ENUM

Attivazione delle estensioni richieste e definizione dei tipi enumerati condivisi da tutte le tabelle.

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb  CASCADE;
CREATE EXTENSION IF NOT EXISTS postgis      CASCADE;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"  CASCADE;
CREATE EXTENSION IF NOT EXISTS pg_trgm      CASCADE;  -- ricerca testuale fuzzy

-- Ruoli utente nel sistema sanitario
CREATE TYPE userrole AS ENUM (
    'MMG',                  -- Medico di Medicina Generale
    'PLS',                  -- Pediatra di Libera Scelta
    'UOSD',                 -- Unità Operativa Semplice Dipartimentale
    'UOC_EPIDEMIOLOGY',     -- Unità Operativa Complessa - Epidemiologia
    'ADMIN'
);

-- Sesso biologico del paziente
CREATE TYPE gender AS ENUM ('male', 'female', 'other');

-- Stato clinico del paziente
CREATE TYPE patientstatus AS ENUM (
    'ACTIVE',       -- In follow-up attivo
    'RECOVERED',    -- Guarito
    'DECEASED'      -- Deceduto
);
```

---

#### 3.3.2 Schema Operativo — Utenti e Pazienti

Account di sistema per medici, epidemiologi e amministratori; anagrafica dei pazienti notificati.

```sql
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL          PRIMARY KEY,
    username        VARCHAR(50)     NOT NULL UNIQUE,
    email           VARCHAR(255)    NOT NULL UNIQUE,
    hashed_password VARCHAR(255)    NOT NULL,
    full_name       VARCHAR(255)    NOT NULL,
    role            userrole        NOT NULL,
    telephone       VARCHAR(20),
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_users_role      ON users (role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users (is_active);

-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS patients (
    id                      SERIAL          PRIMARY KEY,
    tax_code                VARCHAR(16)     UNIQUE,
    stp_code                VARCHAR(20),
    eni_code                VARCHAR(20),
    surname                 VARCHAR(100)    NOT NULL,
    name                    VARCHAR(100)    NOT NULL,
    gender                  gender          NOT NULL,
    birth_date              DATE            NOT NULL,
    birth_country           VARCHAR(100),
    birth_province          VARCHAR(50),
    birth_municipality      VARCHAR(100)    NOT NULL,
    profession              VARCHAR(100),
    residence_address       TEXT,
    residence_municipality  VARCHAR(100),
    residence_province      VARCHAR(50),
    residence_region        VARCHAR(50),
    domicile_address        TEXT,
    domicile_municipality   VARCHAR(100),
    telephone               VARCHAR(20),
    status                  patientstatus   NOT NULL DEFAULT 'ACTIVE',
    created_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_patients_tax_code               ON patients (tax_code);
CREATE INDEX IF NOT EXISTS idx_patients_surname                ON patients (surname);
CREATE INDEX IF NOT EXISTS idx_patients_residence_municipality ON patients (residence_municipality);
CREATE INDEX IF NOT EXISTS idx_patients_status                 ON patients (status);
```

---

#### 3.3.3 Schema Operativo — Notifiche e Indagini

Ciclo di vita della segnalazione: notifica iniziale → indagine epidemiologica → tracciamento dei contatti.

```sql
CREATE TABLE IF NOT EXISTS disease_reports (
    id                          SERIAL          PRIMARY KEY,
    patient_id                  INT             NOT NULL
                                    REFERENCES patients (id) ON DELETE RESTRICT,
    reporting_doctor_id         INT             NOT NULL
                                    REFERENCES users    (id) ON DELETE RESTRICT,
    disease_name                VARCHAR(200)    NOT NULL,
    uosd_diagnosis              VARCHAR(200),
    symptom_onset_date          DATE,
    symptom_onset_municipality  VARCHAR(100),
    hospitalization             BOOLEAN         NOT NULL DEFAULT FALSE,
    vaccination_status          VARCHAR(50),
    vaccination_doses           INT,
    last_dose_date              DATE,
    vaccine_type                VARCHAR(100),
    report_date                 DATE            NOT NULL,
    created_at                  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_disease_reports_disease_name         ON disease_reports (disease_name);
CREATE INDEX IF NOT EXISTS idx_disease_reports_symptom_onset_date   ON disease_reports (symptom_onset_date);
CREATE INDEX IF NOT EXISTS idx_disease_reports_symptom_municipality ON disease_reports (symptom_onset_municipality);
CREATE INDEX IF NOT EXISTS idx_disease_reports_patient              ON disease_reports (patient_id);
CREATE INDEX IF NOT EXISTS idx_disease_reports_doctor               ON disease_reports (reporting_doctor_id);
CREATE INDEX IF NOT EXISTS idx_disease_reports_disease_trgm
    ON disease_reports USING gin (disease_name gin_trgm_ops);

-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS epidemiological_investigations (
    id                  SERIAL          PRIMARY KEY,
    patient_id          INT             NOT NULL
                            REFERENCES patients        (id) ON DELETE RESTRICT,
    report_id           INT             NOT NULL
                            REFERENCES disease_reports (id) ON DELETE RESTRICT,
    investigator_id     INT             NOT NULL
                            REFERENCES users           (id) ON DELETE RESTRICT,
    case_type           VARCHAR(20),        -- 'probable' | 'confirmed'
    symptomatology      TEXT,
    contagion_source    TEXT,
    foreign_travel      BOOLEAN         NOT NULL DEFAULT FALSE,
    travel_countries    TEXT,
    travel_dates        TEXT,
    diagnostic_tests    JSONB,             -- [{type, date, place, result}, ...]
    investigation_date  DATE            NOT NULL,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_investigations_patient ON epidemiological_investigations (patient_id);
CREATE INDEX IF NOT EXISTS idx_investigations_report  ON epidemiological_investigations (report_id);
CREATE INDEX IF NOT EXISTS idx_investigations_date    ON epidemiological_investigations (investigation_date);

-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS contact_tracing (
    id                  SERIAL          PRIMARY KEY,
    investigation_id    INT             NOT NULL
                            REFERENCES epidemiological_investigations (id) ON DELETE CASCADE,
    relationship_type   VARCHAR(50),        -- Family | Work | Social | Other
    contact_name        VARCHAR(100)    NOT NULL,
    contact_surname     VARCHAR(100)    NOT NULL,
    contact_tax_code    VARCHAR(16),
    contact_profession  VARCHAR(100),
    contact_telephone   VARCHAR(20),
    contact_address     TEXT,
    last_contact_date   DATE,
    exposure_duration   VARCHAR(50),
    exposure_type       VARCHAR(50),        -- Close | Casual
    contacted           BOOLEAN         NOT NULL DEFAULT FALSE,
    tested              BOOLEAN         NOT NULL DEFAULT FALSE,
    test_result         VARCHAR(50),
    developed_symptoms  BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_contact_tracing_investigation ON contact_tracing (investigation_id);
```

---

#### 3.3.4 Schema Operativo — Categorie e Schede Specifiche

Catalogo delle categorie di malattia con coefficienti di correlazione ambientale di riferimento; schede di indagine dedicate per patologie specifiche (pattern estendibile).

```sql
CREATE TABLE IF NOT EXISTS disease_categories (
    id                      SERIAL          PRIMARY KEY,
    name                    VARCHAR(200)    NOT NULL UNIQUE,
    description             TEXT,
    icd_code                VARCHAR(20),
    pm25_correlation        FLOAT,
    pm10_correlation        FLOAT,
    no2_correlation         FLOAT,
    ozone_correlation       FLOAT,
    temperature_correlation FLOAT,
    humidity_correlation    FLOAT,
    created_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS influenza_investigations (
    id                  SERIAL          PRIMARY KEY,
    investigation_id    INT             NOT NULL
                            REFERENCES epidemiological_investigations (id) ON DELETE CASCADE,
    hospitalized        BOOLEAN         NOT NULL DEFAULT FALSE,
    antiviral_therapy   BOOLEAN         NOT NULL DEFAULT FALSE,
    chronic_diseases    TEXT,
    test_a_h1n1v        BOOLEAN         NOT NULL DEFAULT FALSE,
    test_a_h1n1         BOOLEAN         NOT NULL DEFAULT FALSE,
    test_a_h3n2         BOOLEAN         NOT NULL DEFAULT FALSE,
    test_b              BOOLEAN         NOT NULL DEFAULT FALSE,
    complications       TEXT,
    outcome             VARCHAR(50),    -- 'Recovery' | 'Death'
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS botulism_investigations (
    id                  SERIAL          PRIMARY KEY,
    investigation_id    INT             NOT NULL
                            REFERENCES epidemiological_investigations (id) ON DELETE CASCADE,
    suspected_food      TEXT,
    diplopia            BOOLEAN         NOT NULL DEFAULT FALSE,
    dysphagia           BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
```

---

#### 3.3.5 Schema DWH — Dati Ambientali

Archivio storico delle misurazioni per stazione (`environmental_data`) e tabella aggregata IDW per comune e per giorno (`environmental_daily_aggregated` — tabella chiave del DWH). Entrambe sono hypertable TimescaleDB.

> **Nota:** `environmental_daily_aggregated` contiene un unico valore IDW-ponderato per comune al giorno, prodotto dal pipeline Kafka → IngestionConsumer. Il campo `parameters` è JSONB con tutti i parametri misurati (es. `{"NO2": 24.9, "PM10": 31.2, "PM2.5": 18}`).

```sql
CREATE TABLE IF NOT EXISTS environmental_data (
    id                      SERIAL          PRIMARY KEY,
    istat_code              VARCHAR(6)      NOT NULL,
    municipality            VARCHAR(100)    NOT NULL,
    province                VARCHAR(50)     NOT NULL,
    region                  VARCHAR(50)     NOT NULL,
    latitude                FLOAT,
    longitude               FLOAT,
    altitude                FLOAT,
    measurement_date        DATE            NOT NULL,
    measurement_year        INT             NOT NULL,
    measurement_month       INT,
    -- Qualità dell'aria
    pm10                    FLOAT,          -- μg/m³
    pm25                    FLOAT,          -- μg/m³
    ozone                   FLOAT,          -- μg/m³
    no2                     FLOAT,          -- μg/m³
    so2                     FLOAT,          -- μg/m³
    co                      FLOAT,          -- mg/m³
    benzene                 FLOAT,          -- μg/m³
    -- Meteorologia
    temperature_avg         FLOAT,          -- °C
    temperature_max         FLOAT,          -- °C
    temperature_min         FLOAT,          -- °C
    humidity                FLOAT,          -- %
    precipitation           FLOAT,          -- mm
    wind_speed              FLOAT,          -- km/h
    atmospheric_pressure    FLOAT,          -- hPa
    solar_radiation         FLOAT,          -- W/m²
    -- Contesto territoriale
    has_mines               BOOLEAN         DEFAULT FALSE,
    has_industries          BOOLEAN         DEFAULT FALSE,
    area_type               VARCHAR(50),    -- Urban | Marshy | Grazing | Agricultural
    data_source             VARCHAR(50),    -- ARPAC | METEOHUB | ISPRA
    created_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_env_data_istat_code       ON environmental_data (istat_code);
CREATE INDEX IF NOT EXISTS idx_env_data_measurement_date ON environmental_data (measurement_date);
CREATE INDEX IF NOT EXISTS idx_env_data_year_month       ON environmental_data (measurement_year, measurement_month);
CREATE INDEX IF NOT EXISTS idx_env_data_source           ON environmental_data (data_source);

SELECT create_hypertable(
    'environmental_data',
    'measurement_date',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists       => TRUE
);

-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS environmental_daily_aggregated (
    id              SERIAL          PRIMARY KEY,
    istat_code      VARCHAR(6)      NOT NULL,
    source          VARCHAR(20)     NOT NULL,   -- 'ARPAC' | 'METEOHUB'
    period_date     DATE            NOT NULL,
    parameters      JSONB           NOT NULL DEFAULT '{}',
    station_count   INT             NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,

    CONSTRAINT uq_env_daily_agg UNIQUE (istat_code, source, period_date)
);

CREATE INDEX IF NOT EXISTS idx_env_agg_istat_date  ON environmental_daily_aggregated (istat_code, period_date);
CREATE INDEX IF NOT EXISTS idx_env_agg_source      ON environmental_daily_aggregated (source);
CREATE INDEX IF NOT EXISTS idx_env_agg_period_date ON environmental_daily_aggregated (period_date);
CREATE INDEX IF NOT EXISTS idx_env_agg_parameters
    ON environmental_daily_aggregated USING gin (parameters);

SELECT create_hypertable(
    'environmental_daily_aggregated',
    'period_date',
    chunk_time_interval => INTERVAL '3 months',
    if_not_exists       => TRUE
);

-- ─────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS environmental_data_batches (
    id              SERIAL          PRIMARY KEY,
    batch_id        UUID            NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    filename        VARCHAR(255)    NOT NULL,
    file_size       INT,
    records_count   INT,
    processed_count INT             NOT NULL DEFAULT 0,
    error_count     INT             NOT NULL DEFAULT 0,
    status          VARCHAR(20)     NOT NULL DEFAULT 'processing',
                                    -- processing | completed | failed
    uploaded_by     INT             REFERENCES users (id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);
```

---

#### 3.3.6 Schema DWH — Correlazioni e Analytics

Risultati del calcolo delle correlazioni di Pearson tra parametri ambientali e categorie di malattia; il campo `lag_days` permette di modellare effetti ritardati.

```sql
CREATE TABLE IF NOT EXISTS disease_environmental_correlations (
    id              SERIAL          PRIMARY KEY,
    disease_name    VARCHAR(200)    NOT NULL,
    parameter       VARCHAR(50)     NOT NULL,   -- 'PM2.5' | 'temperature' | ...
    r_value         FLOAT           NOT NULL,   -- coefficiente Pearson [-1, +1]
    p_value         FLOAT           NOT NULL,   -- significatività statistica
    lag_days        INT             NOT NULL DEFAULT 0,
    istat_code      VARCHAR(6),                 -- NULL = correlazione aggregata
    calculated_at   TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_corr UNIQUE (disease_name, parameter, lag_days, istat_code)
);

CREATE INDEX IF NOT EXISTS idx_corr_disease ON disease_environmental_correlations (disease_name);
CREATE INDEX IF NOT EXISTS idx_corr_param   ON disease_environmental_correlations (parameter);
```

---

#### 3.3.7 Dati Iniziali (Seed)

Inserimento delle tre malattie target della Fase 1 con i coefficienti di correlazione ambientale derivati da letteratura scientifica.

| Malattia | ICD | PM2.5 | Temp | Umidità |
|---|---|---|---|---|
| Influenza | J09-J11 | 0.821 | −0.612 | 0.558 |
| Legionellosi | A48.1 | 0.412 | 0.756 | 0.821 |
| Epatite A | B15 | 0.312 | 0.521 | 0.743 |

```sql
INSERT INTO disease_categories (
    name, description, icd_code,
    pm25_correlation, pm10_correlation, no2_correlation,
    ozone_correlation, temperature_correlation, humidity_correlation
) VALUES
    ('Influenza',
     'Influenza stagionale e pandemica',
     'J09-J11',
     0.821, 0.743, 0.682, 0.541, -0.612, 0.558),
    ('Legionellosi',
     'Malattia del legionario e febbre di Pontiac',
     'A48.1',
     0.412, 0.389, 0.298, 0.201, 0.756, 0.821),
    ('Epatite A',
     'Epatite virale di tipo A',
     'B15',
     0.312, 0.289, 0.341, 0.198, 0.521, 0.743)
ON CONFLICT (name) DO NOTHING;
```

---

*Fine documento D.4 – Progettazione Fisica e Architettura DWH*  
*HealthTrace · 13 maggio 2026*

