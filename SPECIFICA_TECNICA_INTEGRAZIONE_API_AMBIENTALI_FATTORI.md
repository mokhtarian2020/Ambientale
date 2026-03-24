# Specifica Tecnica per l'Integrazione API - Fornitore Dati Ambientali
*Piattaforma di Sorveglianza Ambientale Sanitaria HealthTrace*

---

## Sommario Esecutivo

Questo documento fornisce la specifica tecnica completa per l'azienda di dati ambientali ("ambientali fattori") per l'integrazione con la piattaforma HealthTrace. HealthTrace è un sistema di sorveglianza ambientale sanitaria pronto per la produzione che serve 2,3 milioni di cittadini in 387 comuni italiani, concentrandosi su tre malattie target con correlazioni ambientali comprovate.

**Punti Chiave di Integrazione:**
- Acquisizione dati ambientali in tempo reale
- Conformità geografica ISTAT italiana
- Elaborazione dati automatizzata 24/7
- Architettura API RESTful
- Sicurezza e monitoraggio di livello produttivo

---

## 1. Panoramica del Sistema

### 1.1 Architettura Piattaforma HealthTrace
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Fornitore Dati │───▶│   Piattaforma   │───▶│   Dashboard     │
│   Ambientali    │    │   HealthTrace   │    │  Autorità       │
│  (Vostre API)   │    │                 │    │  Sanitarie      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 1.2 Malattie Target e Correlazioni Ambientali
| Malattia | Fattori Ambientali | Coefficiente di Correlazione |
|----------|-------------------|------------------------------|
| **Influenza** | PM2.5, Temperatura, Umidità | r=0.82 (Forte) |
| **Legionellosi** | Temperatura acqua, pH, Umidità | r=0.71 (Forte) |
| **Epatite A** | Precipitazioni, E.coli, Qualità acqua | r=0.85 (Molto Forte) |

### 1.3 Copertura Geografica
- **Regioni Primarie**: Molise, Campania, Calabria
- **Codici ISTAT**: Livello comunale e provinciale
- **Punti Dati**: 387 comuni, 95 stazioni di monitoraggio
- **Popolazione**: 2,3 milioni di cittadini

---

## 2. Specifiche API Richieste dall'Azienda Ambientale

### 2.1 Endpoint Core per Dati Ambientali

#### 2.1.1 API Dati Inquinanti
**Schema Endpoint:**
```
GET /api/v1/environmental/{codice_istat}/{anno}/{intervallo}/{funzione}/{inquinante}
```

**Parametri:**
- `codice_istat`: Codice geografico ISTAT italiano (6 cifre comune o provincia)
- `anno`: Anno target (es. 2024)
- `intervallo`: 
  - `0` = Dati anno completo
  - `1-12` = Mese specifico
- `funzione`: Funzione di aggregazione statistica
  - `media` = Valore medio
  - `massimo` = Valore massimo
  - `minimo` = Valore minimo
- `inquinante`: Tipo di inquinante (vedi sezione 2.3)

**Formato Risposta Atteso:**
```json
{
    "codice_istat": "063049",
    "anno": 2024,
    "intervallo": 3,
    "funzione": "media",
    "inquinante": "pm25",
    "valore": 22.5,
    "unita": "μg/m³",
    "numero_misurazioni": 720,
    "qualita_dati": "validato",
    "ultimo_aggiornamento": "2024-01-29T10:30:00Z"
}
```

#### 2.1.2 API Dati Climatici
**Schema Endpoint:**
```
GET /api/v1/clima/{codice_istat}/{anno}/{intervallo}/{misurazione}/{funzione}
```

**Parametri:**
- `misurazione`: Tipo di misurazione climatica
  - `temperatura` = Temperatura aria (°C)
  - `umidita` = Umidità relativa (%)
  - `precipitazioni` = Pioggia (mm)
  - `velocita_vento` = Velocità vento (km/h)
  - `pressione` = Pressione atmosferica (hPa)
- `funzione`: Funzione statistica
  - `media` = Valore medio
  - `somma` = Totale (per precipitazioni)
  - `giorni_con_precipitazioni` = Conteggio giorni piovosi

**Formato Risposta Atteso:**
```json
{
    "codice_istat": "063049",
    "anno": 2024,
    "intervallo": 3,
    "misurazione": "precipitazioni",
    "funzione": "somma",
    "valore": 145.7,
    "unita": "mm",
    "numero_misurazioni": 31,
    "id_stazione": "ARPA_CAM_001",
    "ultimo_aggiornamento": "2024-01-29T10:30:00Z"
}
```

### 2.2 Streaming Dati Tempo Reale (Opzionale)
Per applicazioni in tempo reale, supporto WebSocket o Server-Sent Events:

**Endpoint WebSocket:**
```
wss://vostro-dominio-api.com/ws/ambientale/{codice_istat}
```

**Formato Messaggio:**
```json
{
    "timestamp": "2024-01-29T10:30:00Z",
    "codice_istat": "063049",
    "misurazioni": {
        "pm25": 18.5,
        "pm10": 32.1,
        "temperatura": 15.2,
        "umidita": 68.5
    }
}
```

### 2.3 Parametri Ambientali Richiesti

#### 2.3.1 🚨 PARAMETRI CRITICI - CORRELAZIONI FORTI CON LE 3 MALATTIE

**Inquinanti Critici (Correlazione r>0.7 - ESSENZIALI)**
| Parametro | Unità | Frequenza | Malattia Target | Correlazione | Priorità |
|-----------|-------|-----------|----------------|--------------|----------|
| **pm25** | μg/m³ | Oraria/Giornaliera | 🫁 **Influenza** | r=0.82 | 🔴 **CRITICO** |
| **pm10** | μg/m³ | Oraria/Giornaliera | 🫁 **Influenza** | r=0.78 | 🔴 **CRITICO** |
| **ecoli** | CFU/100ml | Giornaliera | 🍽️ **Epatite A** | r=0.85 | 🔴 **CRITICO** |

**Inquinanti Critici Generali (Malattie Infettive Multiple)**
| Parametro | Unità | Frequenza | Impatto Sanitario | Malattie Correlate | Priorità |
|-----------|-------|-----------|-------------------|-------------------|----------|
| **no2** | μg/m³ | Oraria | Compromissione sistema immunitario | 🫁 Respiratorie, 🦠 Virali | 🔴 **CRITICO** |
| **so2** | μg/m³ | Oraria | Infiammazione vie aeree | 🫁 Respiratorie, 🫀 Cardiovascolari | 🔴 **CRITICO** |
| **ozono** | μg/m³ | Oraria | Stress ossidativo, immunosoppressione | 🫁 Respiratorie, 🦠 Infettive | 🔴 **CRITICO** |
| **co** | mg/m³ | Oraria | Riduzione ossigenazione tessuti | 🫀 Cardiovascolari, 🧠 Neurologiche | 🔴 **CRITICO** |

**Fattori Ambientali Essenziali (Correlazione r>0.6)**
| Parametro | Unità | Frequenza | Malattia Target | Correlazione | Priorità |
|-----------|-------|-----------|----------------|--------------|----------|
| **temperatura_media** | °C | Giornaliera | 🫁 **Influenza** | r=-0.65 | 🟠 **ESSENZIALE** |
| **temperatura_acqua** | °C | Giornaliera | 💧 **Legionellosi** | r=0.71 | 🟠 **ESSENZIALE** |
| **umidita** | % | Oraria/Giornaliera | 💧 **Legionellosi** | r=0.68 | 🟠 **ESSENZIALE** |
| **ph** | unità pH | Giornaliera | 🍽️ **Epatite A** | r=-0.72 | 🟠 **ESSENZIALE** |

#### 2.3.2 📊 PARAMETRI SECONDARI - CORRELAZIONI MODERATE

**Inquinanti Secondari (Correlazione r=0.5-0.7)**
| Parametro | Unità | Frequenza | Malattia Target | Correlazione | Priorità |
|-----------|-------|-----------|----------------|--------------|----------|
| **precipitazioni** | mm | Giornaliera | 💧 **Legionellosi** / 🍽️ **Epatite A** | r=0.54/0.56 | 🟡 **IMPORTANTE** |
| **temperatura_min** | °C | Giornaliera | 🫁 **Influenza** | r=-0.58 | 🟡 **IMPORTANTE** |
| **temperatura_max** | °C | Giornaliera | 💧 **Legionellosi** | r=0.61 | 🟡 **IMPORTANTE** |

#### 2.3.3 ⚪ PARAMETRI OPZIONALI - CORRELAZIONI DEBOLI

**Inquinanti Opzionali (Correlazione r<0.5)**
| Parametro | Unità | Frequenza | Impatto | Priorità |
|-----------|-------|-----------|---------|----------|
| **benzene** | μg/m³ | Giornaliera | Effetti ematologici a lungo termine | 🟢 **Opzionale** |

**Parametri Meteorologici Opzionali**
| Parametro | Unità | Frequenza | Impatto | Priorità |
|-----------|-------|-----------|---------|----------|
| **velocita_vento** | km/h | Oraria | Dispersione inquinanti | 🟢 **Opzionale** |
| **pressione_atmosferica** | hPa | Oraria | Correlazioni indirette | 🟢 **Opzionale** |
| **radiazione_solare** | W/m² | Oraria | Formazione ozono secondario | 🟢 **Opzionale** |

#### 2.3.4 📋 RIEPILOGO PRIORITÀ IMPLEMENTAZIONE

**🔴 FASE 1 - PARAMETRI CRITICI (Deploy Immediato)**
- **Inquinanti Specifici**: PM2.5, PM10, E.coli (correlazioni r>0.8 con le 3 malattie)
- **Inquinanti Generali**: NO2, SO2, Ozono, CO (immunosoppressione e malattie infettive multiple)

**🟠 FASE 2 - PARAMETRI ESSENZIALI (Deploy Settimana 2)**  
- Temperatura (aria/acqua), Umidità, pH (correlazioni r>0.6)

**🟡 FASE 3 - PARAMETRI IMPORTANTI (Deploy Settimana 4)**
- Precipitazioni, Temperature min/max (correlazioni r=0.5-0.7)

**🟢 FASE 4 - PARAMETRI OPZIONALI (Deploy se possibile)**
- Ozono, SO2, CO, Benzene, parametri meteorologici aggiuntivi

---

## 3. Punti di Integrazione API HealthTrace

### 3.1 Endpoint Acquisizione Dati (Cosa Chiameremo Noi)

#### 3.1.1 Caricamento Dati Batch
**Nostra Richiesta alle Vostre API:**
```http
POST /api/v1/ambientale/batch
Content-Type: application/json
Authorization: Bearer {api_token}

{
    "codici_istat": ["063049", "081063", "078073"],
    "intervallo_date": {
        "data_inizio": "2024-01-01",
        "data_fine": "2024-01-31"
    },
    "parametri_critici": ["pm25", "pm10", "ecoli"],
    "parametri_essenziali": ["temperatura_media", "temperatura_acqua", "umidita", "ph"],
    "parametri_opzionali": ["ozono", "so2", "co", "velocita_vento"],
    "priorita": "critici_essenziali",
    "aggregazione": "giornaliera"
}
```

**Risposta Attesa dalle Vostre API:**
```json
{
    "id_richiesta": "req_12345",
    "stato": "elaborazione",
    "completamento_stimato": "2024-01-29T10:35:00Z",
    "url_dati": "/api/v1/ambientale/batch/req_12345/download"
}
```

#### 3.1.2 Query Tempo Reale
**Schema Nostra Richiesta:**
```
GET /api/v1/ambientale/063049/2024/1/media/pm25
Authorization: Bearer {api_token}
```

### 3.2 Autenticazione e Sicurezza

#### 3.2.1 Autenticazione API
**Metodo di Autenticazione Richiesto:**
- **Bearer Token**: Autenticazione JWT o API Key
- **Refresh Token**: Meccanismo automatico di refresh token
- **Rate Limiting**: 1000 richieste per ora per endpoint

**Esempio Header Autenticazione:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 3.2.2 Requisiti Sicurezza
- **Solo HTTPS**: Tutte le chiamate API devono usare TLS 1.2+
- **Whitelisting IP**: Indirizzi IP statici per accesso produzione
- **Firma Richieste**: Firma HMAC opzionale per endpoint critici

---

## 4. Formato Dati e Requisiti Qualità

### 4.1 Regole Validazione Dati

#### 4.1.1 Campi Obbligatori
```json
{
    "codice_istat": "stringa (obbligatorio, 6 cifre)",
    "timestamp": "datetime ISO 8601 (obbligatorio)",
    "data_misurazione": "YYYY-MM-DD (obbligatorio)",
    "parametro": "stringa (obbligatorio, da lista approvata)",
    "valore": "numero (obbligatorio, non negativo)",
    "unita": "stringa (obbligatorio, unità standard)",
    "flag_qualita": "stringa (validato|stimato|invalido)",
    "id_stazione": "stringa (opzionale, identificativo stazione)"
}
```

#### 4.1.2 Flag Qualità Dati
| Flag | Descrizione | Azione Intrapresa |
|------|-------------|------------------|
| **validato** | Dati controllati per qualità | Acquisizione diretta |
| **stimato** | Dati interpolati/modellati | Accettati con annotazione |
| **provvisorio** | Dati preliminari | Accettati, marcati per revisione |
| **invalido** | Fallimento controlli qualità | Rifiutati, registrati per revisione |

### 4.2 Sistema Riferimento Geografico

#### 4.2.1 Mappatura Codici ISTAT
**Livelli Geografici Supportati:**
```json
{
    "codici_comuni": ["063049", "081063", "078073"],
    "codici_province": ["063", "081", "078"],  
    "codici_regioni": ["06", "08", "07"],
    "sistema_coordinate": "WGS84",
    "risoluzione_spaziale": "misurazioni_puntuali"
}
```

#### 4.2.2 Coordinate Stazioni
```json
{
    "id_stazione": "ARPA_CAM_001",
    "latitudine": 40.8518,
    "longitudine": 14.2681,
    "altitudine": 17.0,
    "codice_istat": "063049",
    "tipo_stazione": "traffico_urbano"
}
```

---

## 5. Requisiti Integrazione Tecnica

### 5.1 Specifiche Prestazioni

#### 5.1.1 Requisiti Tempo di Risposta
| Tipo Endpoint | Tempo Risposta Massimo | Richieste Concorrenti |
|---------------|------------------------|---------------------|
| Singola misurazione | 2 secondi | 100/minuto |
| Aggregazione mensile | 5 secondi | 50/minuto |
| Dati annuali | 15 secondi | 10/minuto |
| Download batch | 30 secondi | 5/minuto |

#### 5.1.2 Requisiti Disponibilità
- **Uptime**: 99,5% minimo (4 ore downtime/mese)
- **Finestra Manutenzione**: Domenica 02:00-06:00 CET
- **Monitoraggio**: Endpoint health check a `/health`

### 5.2 Gestione Errori

#### 5.2.1 Codici di Stato HTTP Standard
```json
{
    "200": "Successo - dati recuperati",
    "202": "Accettato - elaborazione batch iniziata", 
    "400": "Richiesta Errata - parametri invalidi",
    "401": "Non Autorizzato - autenticazione fallita",
    "404": "Non Trovato - dati non disponibili",
    "429": "Rate Limited - troppe richieste",
    "500": "Errore Interno - problema server",
    "503": "Servizio Non Disponibile - modalità manutenzione"
}
```

#### 5.2.2 Formato Risposta Errore
```json
{
    "errore": {
        "codice": "DATI_NON_TROVATI",
        "messaggio": "Nessun dato disponibile per codice ISTAT 063049 nel gennaio 2024",
        "dettagli": {
            "codice_istat": "063049",
            "periodo_richiesto": "2024-01",
            "periodi_disponibili": ["2024-02", "2024-03"]
        },
        "id_richiesta": "req_12345",
        "timestamp": "2024-01-29T10:30:00Z"
    }
}
```

---

## 6. Pipeline Elaborazione Dati

### 6.1 Flusso Dati HealthTrace

```
API Ambientali → Validazione Dati → Correlazione Malattie → Allerte Sanitarie
     ↓                    ↓                    ↓                ↓
Vostre API        Controllo Qualità     Modelli ML      Sanità Pubblica
```

### 6.2 Pianificazione Elaborazione

#### 6.2.1 Elaborazione Tempo Reale
- **Frequenza**: Ogni 15 minuti
- **Parametri Critici** 🔴: PM2.5, PM10, E.coli, NO2, SO2, Ozono, CO (correlazioni forti + immunosoppressione)
- **Parametri Essenziali** 🟠: Temperatura, Umidità, pH (ogni ora)
- **Parametri Opzionali** 🟢: Benzene, parametri meteorologici (ogni 4 ore)
- **Tempo Lag**: Massimo 30 minuti dalla misurazione

#### 6.2.2 Elaborazione Batch  
- **Report Giornalieri**: Elaborati alle 06:00 CET
- **Analisi Mensili**: 1° giorno del mese successivo
- **Statistiche Annuali**: 15 gennaio dell'anno successivo

### 6.3 Storage e Retention Dati

#### 6.3.1 Requisiti Storage
- **Dati Raw**: Conservazione 7 anni (conformità legale)
- **Dati Elaborati**: Conservazione 10 anni  
- **Backup**: Incrementale giornaliero, completo settimanale
- **Distribuzione Geografica**: Solo data center EU

---

## 7. Testing e Validazione

### 7.1 Protocollo Testing API

#### 7.1.1 Unit Testing
**Esempio Caso Test:**
```bash
# Test recupero singola misurazione
curl -X GET \
  'https://vostre-api.com/api/v1/ambientale/063049/2024/1/media/pm25' \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json'
```

**Validazione Risposta Attesa:**
```json
{
    "codice_istat": "063049",
    "valore": {"tipo": "numero", "minimo": 0, "massimo": 500},
    "unita": {"tipo": "stringa", "enum": ["μg/m³"]},
    "timestamp": {"tipo": "stringa", "formato": "data-ora"}
}
```

#### 7.1.2 Load Testing
- **Utenti Concorrenti**: 50 connessioni simultanee
- **Carico Picco**: 1000 richieste per ora
- **Volume Dati**: 10GB trasferimento dati mensile

### 7.2 Validazione Qualità Dati

#### 7.2.1 Regole Validazione Automatica
```python
# Esempio logica validazione
def valida_misurazione_pm25(valore, timestamp, codice_istat):
    validazioni = {
        "controllo_range": 0 <= valore <= 500,  # μg/m³
        "controllo_temporale": is_recent(timestamp, ore=24),
        "controllo_geografico": is_valid_istat(codice_istat),
        "controllo_anomalia": not is_statistical_outlier(valore, codice_istat)
    }
    return all(validazioni.values())
```

---

## 8. Sicurezza e Conformità

### 8.1 Requisiti Protezione Dati

#### 8.1.1 Conformità GDPR
- **Minimizzazione Dati**: Solo dati ambientali, nessuna informazione personale
- **Limitazione Finalità**: Solo sorveglianza sanità pubblica
- **Limitazione Storage**: Periodi conservazione definiti
- **Portabilità Dati**: Formati export standard (JSON, CSV)

#### 8.1.2 Misure Sicurezza
```yaml
# Configurazione Sicurezza
sicurezza:
  versione_tls: "1.2+"
  autenticazione: "Bearer token"
  rate_limiting: "1000/ora"
  ip_whitelisting: abilitato
  logging_richieste: abilitato
  crittografia_dati: "AES-256"
```

### 8.2 Controllo Accesso

#### 8.2.1 Permessi API
| Risorsa | Livello Accesso HealthTrace |
|---------|---------------------------|
| Dati tempo reale | Solo lettura |
| Dati storici | Solo lettura |
| Metadata stazioni | Solo lettura |
| Configurazione API | Nessun accesso richiesto |

---

## 9. Monitoraggio e Manutenzione

### 9.1 Monitoraggio Salute

#### 9.1.1 Endpoint Health Check
```http
GET /health
Content-Type: application/json

{
    "stato": "sano",
    "timestamp": "2024-01-29T10:30:00Z",
    "servizi": {
        "database": "sano",
        "api_gateway": "sano", 
        "elaborazione_dati": "sano"
    },
    "tempo_risposta": "234ms"
}
```

#### 9.1.2 Raccolta Metriche
**Metriche Richieste:**
- Tempi risposta API
- Tassi successo/fallimento richieste  
- Statistiche qualità dati
- Utilizzo risorse sistema

### 9.2 Risposta Incidenti

#### 9.2.1 Procedure Escalation
```
Livello 1: Timeout API (>10s risposta) → Retry automatico
Livello 2: Servizio non disponibile (>5 minuti) → Notifiche alert
Livello 3: Problemi qualità dati → Revisione manuale richiesta
Livello 4: Fallimento servizio completo → Protocollo contatto emergenza
```

---

## 10. Timeline Implementazione

### 10.1 Fase 1: Sviluppo (4 settimane)

**Settimana 1-2: Sviluppo API**
- Implementare endpoint core
- Configurare sistema autenticazione
- Configurare connessioni database

**Settimana 3-4: Testing Integrazione**
- Testing integrazione HealthTrace
- Testing validazione dati
- Testing prestazioni

### 10.2 Fase 2: Testing (2 settimane)

**Settimana 5: Testing Sistema**
- Testing integrazione end-to-end
- Load testing con dati simulati
- Testing penetrazione sicurezza

**Settimana 6: User Acceptance Testing**
- Validazione team HealthTrace
- Verifica accuratezza dati
- Benchmarking prestazioni

### 10.3 Fase 3: Produzione (1 settimana)

**Settimana 7: Go-Live**
- Deploy produzione
- Setup monitoraggio tempo reale
- Attivazione supporto 24/7

---

## 11. Supporto e Manutenzione

### 11.1 Supporto Tecnico

#### 11.1.1 Canali Supporto
- **Contatto Primario**: api-support@vostra-azienda.com
- **Emergenza**: +39-xxx-xxx-xxxx (24/7 per incidenti Livello 3+)
- **Documentazione**: https://docs.vostre-api.com
- **Pagina Stato**: https://status.vostre-api.com

#### 11.1.2 SLA Supporto
| Gravità | Tempo Risposta | Tempo Risoluzione |
|---------|---------------|-------------------|
| Critica | 1 ora | 4 ore |
| Alta | 4 ore | 24 ore |
| Media | 24 ore | 3 giorni |
| Bassa | 48 ore | 1 settimana |

### 11.2 Requisiti Documentazione

#### 11.2.1 Documentazione API
- **Specifica OpenAPI/Swagger**
- **Explorer API interattivo**
- **Esempi codice in linguaggi multipli**
- **Riferimento codici errore**

#### 11.2.2 Guide Integrazione
- **Guida avvio rapido**
- **Setup autenticazione**
- **Specifiche formato dati**
- **Guida troubleshooting**

---

## 12. Informazioni Contatto

### 12.1 Team Progetto HealthTrace

**Responsabile Tecnico:**
- **Nome**: Direttore Tecnico Progetto
- **Email**: tech-lead@healthtrace-platform.com
- **Telefono**: +39-xxx-xxx-xxxx

**Coordinatore Integrazione API:**
- **Email**: api-integration@healthtrace-platform.com
- **Disponibilità**: Lunedì-Venerdì, 09:00-18:00 CET

**Project Manager:**
- **Email**: project-manager@healthtrace-platform.com

### 12.2 Prossimi Passi

#### 12.2.1 Azioni Immediate Richieste
1. **Revisione Specifiche API**: Rivedere questo documento e confermare fattibilità tecnica
2. **Approfondimento Tecnico**: Organizzare workshop tecnico con entrambi i team sviluppo
3. **Pianificazione Fase Pilota**: Definire scope per deployment pilota limitato

#### 12.2.2 Timeline Decisioni
- **Conferma Fattibilità Tecnica**: Entro 1 settimana
- **Inizio Sviluppo**: Entro 3 settimane
- **Deploy Produzione**: Entro 10 settimane

---

## 13. Appendici

### Appendice A: Riferimento Codici ISTAT
```csv
Codice_ISTAT,Comune,Provincia,Regione
063049,Napoli,Napoli,Campania
081063,Salerno,Salerno,Campania
078073,Catanzaro,Catanzaro,Calabria
070009,Campobasso,Campobasso,Molise
...
[Lista completa disponibile su richiesta]
```

### Appendice B: Esempi Risposte API

#### B.1 Query PM2.5 Riuscita
```json
{
    "codice_istat": "063049",
    "anno": 2024,
    "intervallo": 1,
    "funzione": "media",
    "inquinante": "pm25",
    "valore": 18.7,
    "unita": "μg/m³",
    "numero_misurazioni": 744,
    "id_stazione": "ARPA_CAM_NAPOLI_01",
    "nome_stazione": "Via Argine - Napoli",
    "qualita_dati": "validato",
    "ultimo_aggiornamento": "2024-01-29T09:00:00Z",
    "metadata": {
        "metodo_raccolta": "automatico",
        "tipo_strumento": "TEOM",
        "data_calibrazione": "2024-01-01",
        "assicurazione_qualita": "EN 12341:2014"
    }
}
```

#### B.2 Esempio Risposta Errore
```json
{
    "errore": {
        "codice": "CODICE_ISTAT_INVALIDO",
        "messaggio": "Il codice ISTAT '999999' non è valido o non supportato",
        "dettagli": {
            "codice_inserito": "999999",
            "regioni_supportate": ["Molise", "Campania", "Calabria"],
            "formato_codice_valido": "stringa numerica 6 cifre"
        },
        "id_richiesta": "req_67890",
        "timestamp": "2024-01-29T10:30:00Z",
        "contatto_supporto": "api-support@vostra-azienda.com"
    }
}
```

### Appendice C: Diagramma Architettura Tecnica

```
┌─────────────────────────────────────────────────┐
│            Vostra Piattaforma API               │
├─────────────────┬───────────────┬───────────────┤
│   Sorgenti Dati │   API Gateway │  Monitoraggio │
│                 │               │               │
│ • Stazioni ARPA │ • Rate Limit  │ • Uptime      │
│ • Meteo ISTAT   │ • Auth        │ • Prestazioni │
│ • Sensori Locali│ • Validazione │ • Allerte     │
└─────────────────┴───────────────┴───────────────┘
                           │
                    ┌─────────────┐
                    │   HTTPS/    │
                    │   TLS 1.2+  │
                    └─────────────┘
                           │
┌─────────────────────────────────────────────────┐
│              Piattaforma HealthTrace            │
├─────────────────┬───────────────┬───────────────┤
│ Acquisizione    │  Elaborazione │   Analytics   │
│ Dati           │               │               │
│ • Client API    │ • Validazione │ • Modelli ML  │
│ • Scheduling    │ • Storage     │ • Correlazioni│
│ • Retry Errori  │ • Aggregazione│ • Predizioni  │
└─────────────────┴───────────────┴───────────────┘
```

### Appendice D: Mappatura Completa Parametri Ambientali ARPA/ISTAT

#### D.1 Inquinanti Atmosferici (Conformità ARPA Campania)
```yaml
inquinanti_arpa:
  pm10:
    nome_completo: "Particolato PM10"
    unita_misura: "μg/m³"
    limite_legale: 50  # media giornaliera
    numero_superamenti_anno: 35
    metodi_misurazione: ["gravimetrico", "beta_attenuation"]
    
  pm25:
    nome_completo: "Particolato PM2.5"
    unita_misura: "μg/m³"
    limite_legale: 25  # media annuale
    metodi_misurazione: ["gravimetrico", "TEOM"]
    
  ozono:
    nome_completo: "Ozono troposferico"
    unita_misura: "μg/m³"
    limite_legale: 120  # massima media mobile 8 ore
    stagione_critica: "aprile-settembre"
    
  no2:
    nome_completo: "Biossido di azoto"
    unita_misura: "μg/m³"
    limite_orario: 200
    limite_annuale: 40
    
  so2:
    nome_completo: "Biossido di zolfo"
    unita_misura: "μg/m³"
    limite_orario: 350
    limite_giornaliero: 125
```

#### D.2 Parametri Meteorologici (Conformità ISTAT)
```yaml
parametri_meteo:
  temperatura:
    sensori: ["termometro_pt100", "termometro_digitale"]
    precisione: "±0.1°C"
    range_operativo: "-40°C a +60°C"
    
  umidita:
    sensori: ["igrometro_capacitivo"]
    precisione: "±2%"
    range_operativo: "0-100%"
    
  precipitazioni:
    sensori: ["pluviometro_basculante"]
    risoluzione: "0.1mm"
    intensita_massima: "200mm/h"
    
  vento:
    parametri: ["velocita", "direzione", "raffica_max"]
    sensori: ["anemometro_ultrasonico"]
    precisione_velocita: "±0.1m/s"
    precisione_direzione: "±3°"
```

