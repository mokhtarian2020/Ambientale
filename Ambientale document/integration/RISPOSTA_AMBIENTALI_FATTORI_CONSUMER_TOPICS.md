# Risposta Ambientali Fattori - Chiarimenti su Topic Consumer e Operazioni

**Data**: 7 Aprile 2026  
**Da**: HealthTrace Platform Team  
**A**: Ambientali Fattori (Valerio)  
**Oggetto**: Chiarificazione Architecture Consumer Topics e Trigger Operazioni

---

## Introduzione

Grazie per il progresso significativo sull'implementazione Kafka producer. Comprendo completamente la necessità di chiarire il flusso consumer. Questo documento chiarisce:

1. **Quali topic sono consumer-side HealthTrace** vs producer-side Ambientali Fattori
2. **Come vengono triggerate le operazioni** (ingestion, richieste dati, CRUD)
3. **Timeline allineamento tecnico** e prossimi step

---

## 1) Architettura Consumer HealthTrace vs Producer Ambientali Fattori

### 1.1 Recap: Topic Producer (Voi - Ambientali Fattori)

Già implementati da voi con successo:

| Topic | Sorgente | Tipo | Frequenza | Ruolo |
|-------|----------|------|-----------|-------|
| `environmental-ingestion-air` | ARPAC | Batch | Giornaliero | Statistiche aggregate |
| `environmental-ingestion-meteo` | MeteoHub | Batch | Giornaliero | Statistiche aggregate |
| `environmental-realtime-air` | ARPAC | Stream | Near-realtime | Singoli eventi sensori |
| `environmental-realtime-meteo` | MeteoHub | Stream | Near-realtime | Singoli eventi sensori |

**Voi siete produttori** di questi 4 topic.

### 1.2 Topic Consumer (HealthTrace - Non vi riguardano direttamente)

Topic dove **HealthTrace è consumer**, gestiti internamente:

| Topic | Ruolo | Consumatore | Operazione |
|-------|-------|-------------|-----------|
| `analytics_trigger` | Alert epidemiologici | Dashboard/Alerting | Visualizzazione alert |
| `health-data` | Dati sanitari GESAN | Consumer epidemiologico | Correlazione con ambientali |

**Questi topic sono interni HealthTrace** e non richiedono partecipazione da voi.

---

## 2) Trigger delle Operazioni (Risposta alle Vostre Domande)

### 2.1 Trigger Ingestion (Consumo dei Vostri Dati)

```
┌─────────────────────────────────────────────────────────┐
│ AMBIENTALI FATTORI (Producer)                           │
├─────────────────────────────────────────────────────────┤
│ → Pubblica su:                                          │
│   • environmental-ingestion-air (ARPAC daily)           │
│   • environmental-ingestion-meteo (MeteoHub daily)      │
│   • environmental-realtime-air (ARPAC events)           │
│   • environmental-realtime-meteo (MeteoHub events)      │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ (Kafka broker)
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ HEALTHTRACE (Consumer)                                  │
├─────────────────────────────────────────────────────────┤
│ Trigger AUTOMATICO:                                     │
│ Quando un messaggio arriva su environmental-ingestion-* │
│                                                         │
│ Consumer: IngestionConsumer (processo always-on)        │
│ Azione:                                                 │
│  1. Legge il payload dalla queue                        │
│  2. Valida schema e qualità dato                        │
│  3. Applica aggregazione IDW per comune                 │
│  4. Scrive nel DWH (environmental_daily_aggregated)     │
│  5. Genera evento di successo/errore                    │
└─────────────────────────────────────────────────────────┘
```

**Punto cruciale**: Non occorre che voi triggerate l'ingestion.  
È **completely asynchronous** e **event-driven**.

Quando pubblicate un messaggio → HealthTrace lo consuma automaticamente.

### 2.2 Richieste Dati Importati (Voi Come Producer)

```
┌─────────────────────────────────────────────────────────┐
│ HEALTHTRACE (Consumer/Client)                           │
├─────────────────────────────────────────────────────────┤
│ Richiede dati via API (quando necessario):              │
│                                                         │
│ GET /arpac/data/arpac_data_stat                         │
│   ?istat_codes=061007,063049                            │
│   &start_date=2026-01-01                                │
│   &end_date=2026-04-07                                  │
│   &stats=["min","mean","max"]                           │
│   &filter_on_range=true                                 │
│   &validated=true                                       │
│                                                         │
│ GET /meteohub/data/meteohub_data_stats                  │
│   (parametri simili)                                    │
│                                                         │
│ Polling: On-demand, non event-driven                    │
│ Frequenza: Tipicamente per retroattività o correlazioni │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ (HTTP/REST)
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ AMBIENTALI FATTORI (Producer/API Server)                │
├─────────────────────────────────────────────────────────┤
│ Endpoint API (GIA' documentati nel PDF contratto)       │
│ Voi rispondete alle query GET con JSON aggregato       │
│ Fonte: vostra base dati storica (non Kafka)             │
│ Latenza: Accettabile per uso analitico (non real-time) │
└─────────────────────────────────────────────────────────┘
```

**Qui siete voi produttori API**.

HealthTrace richiede dati via HTTP quando ha bisogno di retroattività o correlazioni storiche.

### 2.3 Operazioni CRUD Database (No Event Trigger Needed)

```
AMBIENTALI FATTORI DATABASE
├── Gestiti da voi internamente
├── HealthTrace non interviene
├── Operazioni:
│   • INSERT: Nuovi record da sensori ARPAC/MeteoHub
│   • UPDATE: Correzioni/validazioni
│   • DELETE: Archivio vecchi record (policy retention)
└── Sincronizzazione → Kafka producer (voi)
    Quando deletate record:
    • NON serve evento esplicito su Kafka
    • HealthTrace non replica cancellazioni
    • Voi mantenete la coerenza locale
```

**Non serve trigger Kafka per CRUD**.  
Voi gestite il vostro DB indipendentemente.  
Quello che importa è che **continuate a produrre su Kafka** i dati validati.

---

## 3) Architettura Completa (Visione D'Insieme)

```
┌──────────────────────────────────────────────────────────────────┐
│                    AMBIENTALI FATTORI                            │
│                   (Vostra Responsabilità)                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ARPAC Source    MeteoHub Source      Internal Database          │
│       │                │                      │                  │
│       └────────┬────────┴──────────┬──────────┘                  │
│                │ Preprocessing     │                            │
│         ┌──────▼──────┐            │                            │
│         │  Validation │  ◄────────┘                            │
│         │  Aggregation│                                         │
│         └──────┬──────┘                                         │
│                │                                                │
│       ┌────────┴────────┬───────────┬───────────┐               │
│       │                 │           │           │               │
│    Batch Ingestion   Realtime   API Query   CRUD Ops            │
│       │                 │           │           │               │
│       ▼                 ▼           ▼           │               │
│   [Kafka Topics]   [Kafka Topics]  [REST API]  │               │
│   (4 producers)    (Already live)  (Already live)              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │ (Kafka Broker)    │
                    │ + API Endpoints   │
                    └─────────┬─────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
    [Consumer 1]        [Consumer 2]          [HTTP Client]
    Ingestion Logic  Realtime Alert Logic    API Queries
    (always-on)        (always-on)          (on-demand)
    
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
         ┌────────────────────┴────────────────────┐
         │                                         │
         ▼                                         ▼
    DWH Store                              Dashboard/Analytics
    (historical)                           (correlation analysis)
```

---

## 4) Risposte Specifiche alle Vostre Domande

### Q1: "Topic consumer che triggerano le operazioni di ingestion"

**Risposta**: Non esistono topic consumer che vi riguardano per triggerare ingestion.

- Voi **pubblicate su 4 topic producer** (`environmental-ingestion-air`, etc.)
- HealthTrace **consuma automaticamente** quando i messaggi arrivano
- Processo completamente **asynchronous** e **event-driven**
- Non c'è richiesta/risposta, è **fire-and-forget** dal vostro lato

**Implicazione pratica**:
- Continuate a pubblicare normalmente
- HealthTrace si occupa del resto
- Non dovete attendere conferma consumer

### Q2: "Topic attraverso cui vengono triggerate richieste dati importati"

**Risposta**: Non sono topic Kafka, sono **API HTTP GET**.

- HealthTrace interroga gli **endpoint REST già concordati** nel PDF contratto:
  - `GET /arpac/data/arpac_data_stat`
  - `GET /meteohub/data/meteohub_data_stats`
- Voi rispondete con JSON aggregato dal vostro DB
- Latenza: Non critica (non real-time)
- Frequenza: On-demand, non costante

**Implicazione pratica**:
- Mantenete gli endpoint API operativi
- Rispondete alle query con dati dal vostro storage
- Niente Kafka per questo flusso (HTTP puro)

### Q3: "Operazioni CRUD su database"

**Risposta**: Completamente interne, nessun trigger esterno necessario.

- Voi gestite INSERT/UPDATE/DELETE localmente
- HealthTrace **non replica** cancellazioni
- Continuate a pubblicare dati validati su Kafka
- Il vostro retention policy rimane locale (voi decidete)

**Implicazione pratica**:
- Archiviate/eliminate record secondo vostra policy
- Non sincronizzate cancellazioni a HealthTrace
- HealthTrace mantiene copia storica indipendente nel DWH

---

## 5) Visualizzazione Flussi (Diagramma ASCII)

```
PRODUCER (Voi - Ambientali Fattori)
│
├─ BATCH INGESTION (Giornaliero)
│  ├─ ARPAC aggregation → environmental-ingestion-air [Kafka]
│  └─ MeteoHub aggregation → environmental-ingestion-meteo [Kafka]
│
├─ REALTIME INGESTION (Continuativo)
│  ├─ ARPAC stream → environmental-realtime-air [Kafka]
│  └─ MeteoHub stream → environmental-realtime-meteo [Kafka]
│
└─ API QUERIES (On-Demand)
   ├─ GET /arpac/data/arpac_data_stat → JSON response
   └─ GET /meteohub/data/meteohub_data_stats → JSON response

CONSUMER (HealthTrace)
│
├─ [Kafka Consumer 1] Legge environmental-ingestion-* batch
│  └─ Aggregazione IDW per comune → DWH (analytical)
│
├─ [Kafka Consumer 2] Legge environmental-realtime-* stream
│  └─ Threshold check → alert trigger (real-time)
│
└─ [HTTP Client] Interroga API rest per correlazioni storiche
   └─ Enrichment dati epidemiologici
```

---

## 6) Checklist: Cosa è Già Implementato vs Cosa Rimane

### ✅ GIA' IMPLEMENTATO (da voi)
- [x] 4 Topic Kafka producer (batch + realtime ARPAC + MeteoHub)
- [x] Endpoint API GET per query storiche
- [x] Payload JSON con UTC e unità normalizzate
- [x] Validazione e aggregazione dei dati

### ✅ GIA' IMPLEMENTATO (da noi - HealthTrace)
- [x] Consumer Ingestion (legge batch topics)
- [x] Consumer Realtime (legge stream topics, threshold check)
- [x] Aggregazione IDW per comune (DWH)
- [x] Schema DWH per environmental_daily_aggregated
- [x] Client HTTP per query API retroattive

### ⚠️ CHIARIRE IN ALLINEAMENTO
- [ ] Modalità autenticazione Kafka (se necessaria)
- [ ] Credential provisioning per topic
- [ ] Retention policy Kafka (consiglio: min 7 giorni su ingestion)
- [ ] Ritmo update real-time (frequenza pubblicazione su realtime topics)
- [ ] Schema versioning strategy (come gestire evoluzioni payload)
- [ ] SLA latenza end-to-end (realtime event → alert)
- [ ] Backfill storico: date di inizio e modalità (pull API vs batch file)

---

## 7) Proposta Agenda Allineamento Tecnico

Suggeriamo una **breve sessione tecnica di 30-45 minuti** per:

### Slot 1: Kafka Infrastructure (15 min)
- [ ] Endpoint broker Kafka (host:port)
- [ ] Modalità authentication (SASL, mTLS, etc.)
- [ ] Versione Kafka e retention policy

### Slot 2: API Endpoints (10 min)
- [ ] Conferma disponibilità endpoint `_stat` con filtri
- [ ] Timeout accettabile per query
- [ ] Rate limiting (se presente)

### Slot 3: Data Quality & Scheduling (15 min)
- [ ] Frequenza pubblicazione realtime (eventi/sec o cadenza)
- [ ] Policy backfill storico (quali date, quale metodo)
- [ ] Gestione errori e retry (sia lato producer che consumer)

### Slot 4: Monitoring & Troubleshooting (10 min)
- [ ] Metriche da monitorare (lag consumer, errori schema)
- [ ] Logging e debug
- [ ] Escalation contacts

---

## 8) Timeline Proposta

```
Week 1 (Apr 8-14)
├─ Allineamento tecnico 30 min (mercoledì 10 apr?)
├─ Voi: Condividete endpoint Kafka + credential
└─ Noi: Configurazione consumer sul vostro broker

Week 2 (Apr 15-21)
├─ Test end-to-end publisher → broker → consumer
├─ Validazione payload su ingestion topics
└─ First data visible in DWH (test records)

Week 3 (Apr 22-28)
├─ Backfill storico (date concordate)
├─ Test realtime alert flow
└─ Joint validation on alert triggering

Week 4 (Apr 29 - May 5)
├─ Go-live Campania (ambientali + sanitari correlati)
├─ Monitoring setup
└─ Documentation update
```

---

## 9) Prossimi Step Concreti

**Entro il 9 Aprile**, potremmo:

1. **Confermare disponibilità slot tecnico** (quando vi conviene?)
2. **Inviarci documenti**:
   - Kafka broker endpoint (host, port, authentication method)
   - Certificate/credential per accesso producer topics
   - Versione Kafka e retention configuration
   - API endpoint definitivi + any rate limiting

3. **Noi prepareremo**:
   - Consumer configuration file
   - Test script per validazione schema
   - Monitoring dashboard (Kafka lag, errors)

---

## 10) Contatti e Escalation

**Per domande tecniche Kafka**:  
→ HealthTrace Engineering Team

**Per integrazioni API ambientali**:  
→ Analytics Lead HealthTrace

**Per coordinamento timeline/progetto**:  
→ HealthTrace Project Manager

---

## Conclusione

Siete in una **posizione ottimale** con Kafka producers già implementati. Le vostre domande mostrano ottima comprensione dell'architettura. 

Una volta chiarita questa distinzione tra:
- **Topic producer** (voi) → publish and forget
- **API consumer** (noi) → pull on-demand
- **CRUD locale** (voi) → indipendente da Kafka

il resto seguirà naturalmente. Siamo pronti a sincronizzarci quando vi conviene.

**Disponibili per call quando preferite la prossima settimana!**

Saluti,  
**HealthTrace Platform Team**

---

## Appendice A: Glossario Termini

| Termine | Significato |
|---------|-------------|
| **Topic** | Canale Kafka, come una coda pub/sub |
| **Producer** | Chi pubblica messaggi su un topic |
| **Consumer** | Chi legge messaggi da un topic |
| **Key** | Campo usato per routing (es. `istat_code`) |
| **Payload** | Contenuto del messaggio (JSON structure) |
| **Batch** | Dati aggregati, pubblicati periodicamente |
| **Realtime/Stream** | Dati singoli, pubblicati event-by-event |
| **IDW** | Inverse Distance Weighting (aggregazione spaziale) |
| **DWH** | Data Warehouse (storage analitico) |
| **Lag** | Ritardo consumer rispetto a producer |
| **Retention** | Quanto tempo Kafka mantiene messaggi |

---

## Appendice B: Comando Test Kafka (Example)

Per verificare la connessione ai topic (una volta ricevute credenziali):

```bash
# Test producer
kafka-console-producer.sh \
  --broker-list <kafka-broker>:9092 \
  --topic environmental-ingestion-air \
  --property "parse.key=true" \
  --property "key.separator=:"

# Test consumer
kafka-console-consumer.sh \
  --bootstrap-servers <kafka-broker>:9092 \
  --topic environmental-ingestion-air \
  --from-beginning
```

---

**Fine Documento**
