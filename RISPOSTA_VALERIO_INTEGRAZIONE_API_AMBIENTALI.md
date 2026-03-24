## 1. PROCESSO DI INGESTION TRAMITE KAFKA

### Come Funziona il Nostro Kafka

Usiamo **Apache Kafka** per elaborare i dati ambientali in tempo reale:

```
Le Tue API → Nostro Sistema → Kafka → Elaborazione → Dashboard/Alert
```

#### Topic Kafka che Usiamo:
- **`environmental-data`**: Tutti i dati ambientali (ARPA, meteorologici)
- **`health-data`**: Dati sanitari malattie infettive

#### Come Integriamo i Tuoi Dati:

1. **Raccolta**: Chiamiamo le tue API ogni ora/giorno
2. **Normalizzazione**: Convertiamo nel nostro formato standard
3. **Kafka**: Inviamo i dati normalizzati a Kafka
4. **Elaborazione**: Eseguiamo correlazioni malattie-ambiente
5. **Risultati**: Aggiorniamo dashboard e generiamo alert

#### Formato Messaggio Standard:
```json
{
  "timestamp": "2026-02-24T10:30:00Z",
  "data_type": "environmental",
  "source": "arpa_campania",
  "payload": {
    "istat_code": "063049",
    "station_name": "Napoli Centro", 
    "latitude": 40.8518,
    "longitude": 14.2681,
    "measurement_date": "2026-02-24",
    "pm10": 35.5,
    "pm25": 22.1,
    "no2": 45.2
  }
}
```

---

## 2. MODALITÀ DI ESPOSIZIONE DEI DATI

### Come Esponiamo i Dati

Usiamo **API REST** per fornire i dati elaborati:

#### Endpoint Principali:
```
GET /api/environmental-data/     # Dati ambientali filtrati
GET /api/health-correlations/    # Correlazioni malattie-ambiente  
```

#### Esempio Risposta JSON:
```json
{
  "data": [
    {
      "istat_code": "063049",
      "station_name": "Napoli Centro",
      "latitude": 40.8518,
      "longitude": 14.2681,
      "measurement_date": "2026-02-24",
      "pollutants": {
        "pm10": 35.5,
        "pm25": 22.1,
        "no2": 45.2
      },
      "health_risk_level": "MODERATO"
    }
  ],
  "total_records": 150
}
```

---

## 3. RICHIESTE SPAZIALI - COME FUNZIONANO

### Tipi di Filtri Geografici Supportati

#### 1. **Bounding Box** (Area Rettangolare)
```
GET /api/environmental-data/?bbox=14.25,40.85,14.30,40.90
```
Formato: `longitudine_min,latitudine_min,longitudine_max,latitudine_max`

#### 2. **Codici ISTAT** (Aree Amministrative)
```
GET /api/environmental-data/?istat_code=063049    # Napoli (comune)
GET /api/environmental-data/?istat_code=063       # Provincia Napoli
GET /api/environmental-data/?istat_code=15        # Regione Campania
```

#### 3. **Poligono GeoJSON** (Area Irregolare)
```json
{
  "type": "Polygon", 
  "coordinates": [
    [
      [14.25, 40.85],  # [longitudine, latitudine]
      [14.30, 40.85],
      [14.30, 40.90],
      [14.25, 40.90],
      [14.25, 40.85]   # Chiude il poligono
    ]
  ]
}
```

#### Esempi Pratici:
- **Dati Napoli**: `?istat_code=063049`
- **Area Porto di Napoli**: `?bbox=14.25,40.83,14.28,40.86`
- **Provincia intera**: `?istat_code=063`

---

## 4. COSA SERVE DALLE TUE API

### Formato Dati Richiesto
Le tue API dovrebbero restituire dati così:

```json
{
  "data": [
    {
      "source": "ARPA_CAMPANIA",
      "station_id": "NA01", 
      "station_name": "Napoli Centro",
      "istat_code": "063049",
      "latitude": 40.8518,
      "longitude": 14.2681,
      "measurement_datetime": "2026-02-24T10:00:00Z",
      "pollutants": {
        "PM10": 35.5,
        "PM2.5": 22.1,
        "NO2": 45.2,
        "O3": 88.7
      },
      "meteorological": {
        "temperature": 18.5,
        "humidity": 65.0,
        "wind_speed": 12.3,
        "precipitation": 0.0
      }
    }
  ]
}
```

### Parametri da Supportare:
- `?start_date=2026-02-01`
- `?end_date=2026-02-24`
- `?istat_code=063049` (filtro per comune)
- `?pollutant=PM10,NO2` (filtro inquinanti)
- `?station_id=NA01` (filtro stazione)

