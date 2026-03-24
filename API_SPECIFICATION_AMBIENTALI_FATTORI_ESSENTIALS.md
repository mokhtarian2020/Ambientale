# Specifica Tecnica API - Fornitore Dati Ambientali
*Integrazione con Piattaforma HealthTrace*

---

## 🎯 Sommario Esecutivo

**Obiettivo**: Integrazione API per acquisizione dati ambientali in tempo reale
**Piattaforma**: HealthTrace - Sorveglianza sanitaria 2.3M cittadini, 387 comuni italiani
**Focus**: 3 malattie target con correlazioni ambientali scientificamente provate

---

## 1. API Endpoint Richiesti

### 1.1 Schema Base Endpoint
```
GET /api/v1/environmental/{codice_istat}/{anno}/{intervallo}/{funzione}/{parametro}
```

**Parametri Obbligatori:**
- `codice_istat`: Codice ISTAT italiano (6 cifre)
- `anno`: Anno (es. 2024)
- `intervallo`: 0=anno completo, 1-12=mese specifico
- `funzione`: `media`, `massimo`, `minimo`
- `parametro`: Vedi sezione 2

### 1.2 Formato Risposta Standard
```json
{
    "codice_istat": "063049",
    "anno": 2024,
    "intervallo": 3,
    "funzione": "media",
    "parametro": "pm25",
    "valore": 22.5,
    "unita": "μg/m³",
    "numero_misurazioni": 720,
    "qualita_dati": "validato",
    "ultimo_aggiornamento": "2024-01-29T10:30:00Z"
}
```

---

## 2. 🚨 Parametri Critici da Implementare

### 2.1 Priorità 1 - ESSENZIALI (Deploy Immediato)
| Parametro | Unità | Frequenza | Malattia Correlata | Motivazione |
|-----------|-------|-----------|-------------------|-------------|
| **pm25** | μg/m³ | Oraria | Influenza (r=0.82) | Correlazione molto forte |
| **pm10** | μg/m³ | Oraria | Influenza (r=0.78) | Correlazione forte |
| **ecoli** | CFU/100ml | Giornaliera | Epatite A (r=0.85) | Correlazione molto forte |
| **no2** | μg/m³ | Oraria | Respiratorie/Virali | Immunosoppressione |
| **so2** | μg/m³ | Oraria | Respiratorie/Cardiovascolari | Infiammazione vie aeree |
| **ozono** | μg/m³ | Oraria | Respiratorie/Infettive | Stress ossidativo |
| **co** | mg/m³ | Oraria | Cardiovascolari/Neurologiche | Ridotta ossigenazione |

### 2.2 Priorità 2 - IMPORTANTI (Deploy Settimana 2)
| Parametro | Unità | Frequenza | Correlazione |
|-----------|-------|-----------|-------------|
| **temperatura_media** | °C | Giornaliera | Influenza (r=-0.65) |
| **temperatura_acqua** | °C | Giornaliera | Legionellosi (r=0.71) |
| **umidita** | % | Giornaliera | Legionellosi (r=0.68) |
| **ph** | unità pH | Giornaliera | Epatite A (r=-0.72) |

### 2.3 Priorità 3 - OPZIONALI (Se Possibile)
| Parametro | Unità | Frequenza |
|-----------|-------|-----------|
| **precipitazioni** | mm | Giornaliera |
| **temperatura_min** | °C | Giornaliera |
| **temperatura_max** | °C | Giornaliera |
| **velocita_vento** | km/h | Oraria |

---

## 3. Copertura Geografica ISTAT

### 3.1 Codici ISTAT Target
**Regioni**: Molise, Campania, Calabria
**Comuni**: 387 totali
**Esempio Codici**:
```
063049 - Napoli (Campania)
081063 - Salerno (Campania)  
078073 - Catanzaro (Calabria)
070009 - Campobasso (Molise)
```

### 3.2 Formato Coordinate Stazioni
```json
{
    "id_stazione": "ARPA_CAM_001",
    "latitudine": 40.8518,
    "longitudine": 14.2681,
    "codice_istat": "063049"
}
```

---

## 4. Autenticazione e Sicurezza

### 4.1 Autenticazione Richiesta
```http
Authorization: Bearer {jwt_token}
```

### 4.2 Requisiti Sicurezza
- **HTTPS**: Obbligatorio TLS 1.2+
- **Rate Limiting**: 1000 richieste/ora
- **IP Whitelisting**: Per ambiente produzione

---

## 5. Qualità Dati

### 5.1 Flag Qualità Obbligatori
| Flag | Descrizione | Azione HealthTrace |
|------|-------------|-------------------|
| `validato` | Dati verificati | Acquisizione diretta |
| `stimato` | Dati interpolati | Accettati con nota |
| `invalido` | Controlli falliti | Rifiutati |

### 5.2 Validazione Range
| Parametro | Range Valido | Unità |
|-----------|--------------|-------|
| pm25 | 0-500 | μg/m³ |
| pm10 | 0-1000 | μg/m³ |
| no2 | 0-500 | μg/m³ |
| so2 | 0-1000 | μg/m³ |
| ozono | 0-600 | μg/m³ |
| co | 0-50 | mg/m³ |
| temperatura | -40 a +60 | °C |
| umidita | 0-100 | % |
| ph | 0-14 | unità pH |
| ecoli | 0-10000 | CFU/100ml |

---

## 6. Prestazioni Richieste

### 6.1 Tempo Risposta
| Tipo Query | Tempo Max | Concorrenza |
|------------|-----------|-------------|
| Singola misurazione | 2 secondi | 100/min |
| Aggregazione mensile | 5 secondi | 50/min |
| Dati annuali | 15 secondi | 10/min |

### 6.2 Disponibilità
- **Uptime**: 99.5% minimo
- **Manutenzione**: Domenica 02:00-06:00 CET

---

## 7. Esempi Implementazione

### 7.1 Query Singolo Parametro
```bash
curl -X GET \
  'https://vostre-api.com/api/v1/environmental/063049/2024/3/media/pm25' \
  -H 'Authorization: Bearer {token}'
```

### 7.2 Batch Request (Opzionale)
```http
POST /api/v1/environmental/batch
{
    "codici_istat": ["063049", "081063"],
    "parametri_critici": ["pm25", "pm10", "no2"],
    "periodo": {"inizio": "2024-01-01", "fine": "2024-01-31"}
}
```

---

## 8. Gestione Errori

### 8.1 Codici HTTP
- `200` - Successo
- `400` - Parametri invalidi  
- `401` - Autenticazione fallita
- `404` - Dati non trovati
- `429` - Rate limit superato
- `500` - Errore server

### 8.2 Formato Errore
```json
{
    "errore": {
        "codice": "DATI_NON_TROVATI",
        "messaggio": "Nessun dato per ISTAT 063049 nel gennaio 2024",
        "timestamp": "2024-01-29T10:30:00Z"
    }
}
```

---

## 9. Health Check

### 9.1 Endpoint Monitoraggio
```
GET /health
```

### 9.2 Risposta Attesa
```json
{
    "stato": "sano",
    "timestamp": "2024-01-29T10:30:00Z",
    "tempo_risposta": "234ms"
}
```

---

## 10. Timeline Implementazione

### 10.1 Milestone
- **Settimana 1-2**: Sviluppo endpoint core
- **Settimana 3-4**: Testing integrazione  
- **Settimana 5-6**: Testing sistema completo
- **Settimana 7**: Deploy produzione

### 10.2 Fasi Deploy
1. **Fase 1**: Parametri critici (PM2.5, PM10, E.coli, NO2, SO2, Ozono, CO)
2. **Fase 2**: Parametri importanti (Temperature, Umidità, pH)
3. **Fase 3**: Parametri opzionali

---


