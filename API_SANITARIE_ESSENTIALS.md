# Specifica Tecnica API Sanitarie - HealthTrace
*Developer Reference per Implementazione API Sanitarie*

---

## 🎯 Obiettivo

Implementare API sanitarie interne per acquisizione dati malattie infettive su piattaforma HealthTrace.
**3 Malattie Target**: Influenza, Legionellosi, Epatite A

---

## 1. API Endpoints Richiesti

### 1.1 API Casi Sanitari
```
GET /api/v1/sanitario/casi/{malattia}/{codice_istat}/{anno}/{intervallo}/{aggregazione}
```

**Parametri:**
- `malattia`: `influenza` | `legionellosi` | `epatite_a`
- `codice_istat`: Codice comunale ISTAT (6 cifre)
- `anno`: Anno (es. 2024)
- `intervallo`: 0=anno, 1-12=mese
- `aggregazione`: `totale` | `fasce_eta` | `gravita`

**Formato Risposta:**
```json
{
    "malattia": "influenza",
    "codice_istat": "063049",
    "anno": 2024,
    "intervallo": 3,
    "aggregazione": "totale",
    "totale_casi": 145,
    "nuovi_casi": 12,
    "guariti": 98,
    "decessi": 2,
    "ospedalizzati": 15,
    "terapia_intensiva": 3,
    "ultimo_aggiornamento": "2024-03-31T23:59:00Z"
}
```

### 1.2 API Tendenze Temporali
```
GET /api/v1/sanitario/tendenze/{malattia}/{codice_istat}/{data_inizio}/{data_fine}
```

**Parametri:**
- `data_inizio`, `data_fine`: Formato YYYY-MM-DD

**Formato Risposta:**
```json
{
    "malattia": "influenza",
    "codice_istat": "063049",
    "serie_giornaliera": [
        {
            "data": "2024-01-01",
            "nuovi_casi": 3,
            "casi_cumulativi": 3,
            "ospedalizzazioni": 0,
            "decessi": 0
        }
    ],
    "statistiche": {
        "media_giornaliera": 4.7,
        "picco_casi": 12,
        "data_picco": "2024-01-15",
        "totale_casi": 145,
        "tasso_mortalita": 3.4
    }
}
```

### 1.3 API Riepilogo Regionale
```
GET /api/v1/sanitario/regionale/{regione}/{malattia}/{anno}/{mese}
```

**Parametri:**
- `regione`: `molise` | `campania` | `calabria`
- `mese`: 1-12 o 0=anno completo

**Formato Risposta:**
```json
{
    "regione": "campania",
    "malattia": "influenza",
    "anno": 2024,
    "mese": 3,
    "totale_casi": 2450,
    "incidenza_per_100k": 215.3,
    "comuni_coinvolti": 287,
    "distribuzione_asl": {
        "asl_napoli_1": 456,
        "asl_napoli_2": 389
    },
    "ripartizione_demografica": {
        "pediatrica_0_14": 1029,
        "adulti_15_64": 892,
        "anziani_65_plus": 529
    }
}
```

---

## 2. Autenticazione

### 2.1 Schema Autenticazione
```http
Authorization: Bearer {jwt_token}
```

### 2.2 Endpoint Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "username": "string",
    "password": "string"
}
```

**Risposta:**
```json
{
    "access_token": "string",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
        "id": 1,
        "username": "string",
        "role": "mmg|pls|uosd|uoc_epidemiology|admin"
    }
}
```

---

## 3. Codici ISTAT Target

### 3.1 Regioni e Codici Principali
```json
{
    "campania": {
        "napoli": "063049",
        "salerno": "065116",
        "caserta": "061022"
    },
    "calabria": {
        "catanzaro": "079023",
        "cosenza": "078045",
        "reggio_calabria": "080063"
    },
    "molise": {
        "campobasso": "070009",
        "isernia": "094033"
    }
}
```

---

## 4. Gestione Errori HTTP

### 4.1 Codici di Stato
- `200` - Successo
- `400` - Parametri invalidi
- `401` - Autenticazione fallita
- `403` - Accesso negato
- `404` - Dati non trovati
- `500` - Errore server

### 4.2 Formato Errore Standard
```json
{
    "errore": {
        "codice": "DATI_NON_TROVATI",
        "messaggio": "Nessun caso sanitario per ISTAT 063049 nel marzo 2024",
        "timestamp": "2024-03-31T10:30:00Z",
        "dettagli": {
            "parametri_ricevuti": {
                "malattia": "influenza",
                "codice_istat": "063049"
            }
        }
    }
}
```

---

## 5. Requisiti Performance

### 5.1 Tempo di Risposta
| Tipo Endpoint | Tempo Max | Concorrenza |
|---------------|-----------|-------------|
| Singola query | 2 secondi | 100/min |
| Tendenze | 5 secondi | 50/min |
| Aggregazioni regionali | 10 secondi | 20/min |

### 5.2 Disponibilità
- **Uptime**: 99.5%
- **Manutenzione**: Domenica 02:00-06:00 CET

---

## 6. Esempi di Implementazione

### 6.1 Esempio Query Influenza
```bash
curl -X GET \
  'https://api-sanitarie.healthtrace.com/api/v1/sanitario/casi/influenza/063049/2024/3/totale' \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json'
```

### 6.2 Esempio Query Tendenze
```bash
curl -X GET \
  'https://api-sanitarie.healthtrace.com/api/v1/sanitario/tendenze/legionellosi/063049/2024-01-01/2024-01-31' \
  -H 'Authorization: Bearer {token}'
```

---

## 7. Health Check

### 7.1 Endpoint Monitoraggio
```
GET /health
```

### 7.2 Risposta Attesa
```json
{
    "stato": "operativo",
    "timestamp": "2024-03-31T10:30:00Z",
    "tempo_risposta": "156ms",
    "database": "connesso",
    "servizi_esterni": "operativi"
}
```

---

## 8. Validazione Dati

### 8.1 Range Valori Accettabili
| Campo | Range | Note |
|-------|-------|------|
| `totale_casi` | 0-10000 | Per comune/mese |
| `nuovi_casi` | 0-1000 | Per giorno |
| `tasso_mortalita` | 0-100 | Percentuale |
| `incidenza_per_100k` | 0-5000 | Per 100k abitanti |

### 8.2 Campi Obbligatori
- `malattia`, `codice_istat`, `anno`
- `totale_casi`, `ultimo_aggiornamento`
- `timestamp` in formato ISO 8601

---

## 9. Sicurezza e Privacy

### 9.1 Anonimizzazione Obbligatoria
- **NO dati personali** nei payload
- **Solo aggregazioni** numeriche
- **Hash ID** per identificatori interni

### 9.2 HTTPS Obbligatorio
- **TLS 1.2+** per tutte le comunicazioni
- **Rate limiting** applicato per utente

---

## 10. Implementazione FastAPI

### 10.1 Schema Base Endpoint
```python
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

router = APIRouter()

@router.get("/sanitario/casi/{malattia}/{codice_istat}/{anno}/{intervallo}/{aggregazione}")
async def get_health_cases(
    malattia: str,
    codice_istat: str,
    anno: int,
    intervallo: int,
    aggregazione: str,
    current_user = Depends(get_current_active_user)
):
    # Validazione parametri
    if malattia not in ["influenza", "legionellosi", "epatite_a"]:
        raise HTTPException(400, "Malattia non supportata")
    
    if len(codice_istat) != 6:
        raise HTTPException(400, "Codice ISTAT deve essere 6 cifre")
    
    # Implementazione logica business
    return {
        "malattia": malattia,
        "codice_istat": codice_istat,
        "anno": anno,
        "totale_casi": 145  # Da sostituire con dati reali
    }
```

### 10.2 Modello Risposta Pydantic
```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class HealthCaseResponse(BaseModel):
    malattia: str
    codice_istat: str
    anno: int
    intervallo: int
    aggregazione: str
    totale_casi: int
    nuovi_casi: Optional[int] = 0
    guariti: Optional[int] = 0
    decessi: Optional[int] = 0
    ospedalizzati: Optional[int] = 0
    ultimo_aggiornamento: datetime
```

---

## 11. Timeline Sviluppo

### 11.1 Milestone Tecnici
- **Settimana 1-2**: Setup FastAPI + autenticazione JWT
- **Settimana 3-4**: Implementazione endpoint base
- **Settimana 5-6**: Testing + validazione dati
- **Settimana 7**: Deploy e documentazione

### 11.2 Priorità Implementazione
1. **Phase 1**: Endpoint casi base per le 3 malattie
2. **Phase 2**: API tendenze temporali
3. **Phase 3**: Aggregazioni regionali

---

