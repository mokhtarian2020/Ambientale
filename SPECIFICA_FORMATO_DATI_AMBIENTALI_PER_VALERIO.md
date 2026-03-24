# Specifica Formato Dati Ambientali — Richiesta a Fornitore
*HealthTrace Platform — Requisiti Integrazione Dati Ambientali*

---

## Il Problema da Risolvere

I dati sanitari (malattie infettive) nel nostro database sono **aggregati per comune**,
identificato dal **codice ISTAT a 6 cifre** (es. `063049` = Napoli).

I dati ambientali vengono da **stazioni di misura** che:
- Possono essere **fuori dai centri abitati** (montagna, zone industriali, aree disabitate)
- Sono in **numero variabile** per ogni comune (alcune hanno 1 stazione, altre 5+)
- Non hanno una corrispondenza 1:1 con i confini comunali

**Soluzione**: chiediamo al fornitore ambientale di **pre-aggregare i dati per noi a livello di
comune ISTAT**, applicando una media pesata per distanza (IDW). In questo modo il JOIN
con i dati sanitari è diretto e immediato.

---

## Formato Richiesto — Un Record per Comune per Giorno

### Struttura Record Giornaliero

```json
{
  "codice_istat": "063049",
  "data": "2024-03-15",

  "aria": {
    "pm25_media":       18.7,
    "pm10_media":       31.2,
    "no2_media":        42.5,
    "so2_media":         5.1,
    "ozono_media":      88.3,
    "co_media":          0.8
  },

  "meteo": {
    "temperatura_media": 14.2,
    "temperatura_min":    9.8,
    "temperatura_max":   19.6,
    "umidita_media":     65.0,
    "precipitazioni_mm":  0.0,
    "velocita_vento_media": 12.3
  },

  "acqua": {
    "temperatura_acqua": 18.5,
    "ph":                 7.4,
    "ecoli_cfu":         12.0
  },

  "metadati_aggregazione": {
    "stazioni_aria_usate":    3,
    "stazioni_meteo_usate":   2,
    "stazioni_acqua_usate":   1,
    "metodo_aggregazione":    "IDW",
    "qualita":                "validato",
    "copertura_comunale_pct": 78.0
  }
}
```

### Perché questo formato?

| Problema | Soluzione nel formato |
|----------|----------------------|
| Stazioni fuori dai centri abitati | Il fornitore esclude stazioni tipo `montagna`, `rurale`, `industriale` — usa solo `urbano` e `suburbano` |
| Numero diverso di stazioni per comune | Il fornitore fa la media pesata per distanza (IDW) sul suo lato — noi riceviamo sempre UN valore per comune |
| Match con dati sanitari | `codice_istat` + `data` → join diretto con `comune_residenza_codice_istat` + `data_segnalazione` |
| Qualità sconosciuta | Campo `qualita` per ogni record: `validato`, `stimato`, `invalido` |

---

## API Endpoint — Due Opzioni (chiedere quale è fattibile)

### Opzione A — Per comune e data (preferita, join diretto)

```
GET /api/v1/comune/{codice_istat}/{data}
```

Esempio:
```
GET /api/v1/comune/063049/2024-03-15
```

### Opzione B — Batch per periodo (più efficiente per storico)

```
POST /api/v1/batch
{
  "codici_istat": ["063049", "063041", "063017", "063023"],
  "data_inizio":  "2024-01-01",
  "data_fine":    "2024-12-31",
  "parametri":    ["pm25", "temperatura_media", "umidita_media"]
}
```

**Risposta batch** (array di record giornalieri):
```json
[
  { "codice_istat": "063049", "data": "2024-01-01", "aria": {...}, "meteo": {...}, ... },
  { "codice_istat": "063049", "data": "2024-01-02", "aria": {...}, "meteo": {...}, ... },
  ...
]
```

---

## Regole di Aggregazione — Da Comunicare a Valerio

Queste sono le regole che chiediamo al fornitore di applicare **lato loro**, prima di
inviarci i dati.

### 1. Quali stazioni includere

```
INCLUDERE:   tipo_stazione IN ('urbano', 'suburbano', 'traffico')
ESCLUDERE:   tipo_stazione IN ('montagna', 'rurale', 'industriale', 'background_rurale')
ESCLUDERE:   altitudine_m > 500
ESCLUDERE:   popolazione_raggio_2km < 1000
```

Se nessuna stazione "urbana/suburbana" è disponibile per un comune,
usare la stazione più vicina al centroide del comune (qualunque tipo),
e segnalarlo con `qualita: "stimato"`.

### 2. Metodo di aggregazione tra stazioni

**IDW — Inverse Distance Weighting** rispetto al centroide ISTAT del comune:

```
peso_stazione = 1 / (distanza_km²)
valore_comune = Σ(valore_stazione × peso) / Σ(pesi)
```

Questo fa sì che stazioni più vicine al centro abitato pesino di più.

### 3. Qualità del dato

| Situazione | Campo qualita |
|-----------|--------------|
| 2+ stazioni urbane/suburbane nel comune | `"validato"` |
| 1 sola stazione nel comune | `"parziale"` |
| Nessuna stazione nel comune, usata la più vicina entro 15km | `"stimato"` |
| Nessuna stazione entro 15km | `"non_disponibile"` — inviare null per i valori |

### 4. Valori null vs valori mancanti

Se un parametro non è disponibile per un comune in una data, inviare `null`,
**non omettere il campo**:

```json
"acqua": {
  "temperatura_acqua": null,
  "ph": null,
  "ecoli_cfu": null
}
```

Questo ci permette di distinguere "dato non disponibile" da "dato non inviato".

---

## Comuni Prioritari (Join con Dati Malattie Reali)

Dalla nostra analisi del database malattie, questi sono i comuni con il maggior numero
di casi reali — sono i più importanti per la correlazione:

| Codice ISTAT | Comune | Casi Influenza | Casi Legionellosi | Casi Epatite A |
|-------------|--------|---------------|------------------|---------------|
| 063049 | Napoli | 52 | 66 | 23 |
| 063023 | Casoria | 6 | — | — |
| 063041 | Marano di Napoli | 3 | 5 | — |
| 063017 | Casalnuovo di Napoli | 3 | 5 | — |
| 063034 | Giugliano in Campania | 4 | — | 2 |
| 063073 | Sant'Antimo | — | 2 | 3 |
| 063057 | Pomigliano d'Arco | 2 | 2 | 3 |
| 063012 | Calvizzano | — | — | 3 |
| 063011 | Caivano | — | — | 3 |
| 063006 | Bacoli | — | — | 3 |
| 061005 | Aversa | 2 | — | — |
| 063059 | Portici | 2 | 1 | — |

**Coprire almeno questi 12 comuni è sufficiente per la prima versione funzionante.**

---

## Esempio di Come Usiamo i Dati — Il JOIN

```sql
-- Come colleghiamo dati ambientali + malattie nel nostro sistema
SELECT
    m.data_segnalazione::date          AS data,
    m.malattia_segnalata,
    m.comune_residenza_codice_istat    AS istat,
    e.aria->>'pm25_media'              AS pm25,
    e.meteo->>'temperatura_media'      AS temperatura,
    e.meteo->>'umidita_media'          AS umidita,
    e.metadati_aggregazione->>'qualita' AS qualita_dato

FROM gesan_malattie_infettive_segnalazione m
JOIN dati_ambientali_comune e
    ON  e.codice_istat = m.comune_residenza_codice_istat
    AND e.data         = m.data_segnalazione::date

WHERE m.malattia_segnalata ILIKE '%INFLUENZA%'
  AND e.metadati_aggregazione->>'qualita' != 'non_disponibile'
ORDER BY data;
```

**Questo è il motivo per cui il formato aggregato per comune è fondamentale**:
il JOIN è una singola riga, senza nessuna logica spaziale complessa da fare sul nostro lato.

---

## Formato CSV Alternativo (se API non è possibile subito)

Se il microservizio non è ancora pronto, accettiamo anche **file CSV giornalieri** con questa struttura:

```
codice_istat,data,pm25_media,pm10_media,no2_media,temperatura_media,temperatura_min,temperatura_max,umidita_media,precipitazioni_mm,temperatura_acqua,ph,ecoli_cfu,stazioni_usate,qualita
063049,2024-01-01,18.7,31.2,42.5,8.2,4.1,12.3,72.0,2.4,,7.4,,3,validato
063041,2024-01-01,15.2,28.1,38.9,7.8,3.9,11.7,75.0,2.4,,,,1,parziale
063017,2024-01-01,,,,,,,,,,,,,non_disponibile
```

Un file CSV per mese, nome file: `ambientale_YYYY_MM.csv`

---

## Domande da Fare a Valerio nella Prossima Riunione

1. **Le stazioni ARPAC hanno un campo `tipo_stazione` (urbano/rurale/industriale)?**
   Questo determina quali escludere nelle aree non abitate.

2. **Riesci ad aggiungere il codice ISTAT del comune a ogni stazione?**
   Se le stazioni hanno solo lat/lon, possiamo fornire noi la mappatura stazione → ISTAT.

3. **Puoi fare l'aggregazione IDW sul lato vostro, restituendoci un valore per comune?**
   Questo è molto più semplice per noi che ricevere dati raw per stazione.

4. **Per i comuni senza stazioni, usi la stazione più vicina?**
   E segnali questo con un flag di qualità?

5. **Qual è la granularità temporale del microservizio?**
   Oraria, giornaliera, o mensile? Per noi va bene anche solo giornaliera.

---

*Documento preparato per allineamento con fornitore dati ambientali — HealthTrace Platform*
