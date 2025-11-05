#!/usr/bin/env python3
"""
Server API HealthTrace Potenziato con Dati Sintetici (Versione Italiana)
Contiene dati realistici italiani di salute ambientale per testare tutti i modelli
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import uvicorn
import json

app = FastAPI(
    title="API HealthTrace - Potenziata con Dati Sintetici",
    description="Sistema di Monitoraggio Sanitario Ambientale con Dati Realistici Italiani",
    version="2.0.0"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3200", "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dati potenziati dalla generazione sintetica
DATI_POTENZIATI = {
  "riassunto_dashboard": {
    "segnalazioni_totali": 350,
    "indagini_totali": 27,
    "pazienti_attivi": 105,
    "pazienti_guariti": 244,
    "regioni": [
      "Campania",
      "Calabria",
      "Molise"
    ],
    "ultimo_aggiornamento": "2025-10-30T15:22:44.002145",
    "correlazioni_ambientali": {
      "pm25_respiratorio": 0.82,
      "no2_cardiovascolare": 0.74,
      "o3_respiratorio": 0.68,
      "temperatura_infettivo": -0.59,
      "umidita_legionellosi": 0.71,
      "ecoli_epatite": 0.85,
      "pm25_influenza": 0.07,
      "temperatura_influenza": -0.08,
      "pm25_legionellosi": 0.02,
      "temperatura_legionellosi": -0.01,
      "pm25_epatite_a": 0.0,
      "temperatura_epatite_a": -0.01
    },
    "tendenze_mensili": [
      {
        "mese": "Gen",
        "casi_influenza": 21,
        "casi_legionellosi": 4,
        "casi_epatite_a": 0,
        "casi_totali": 25,
        "pm25": 15.5,
        "no2": 22.0,
        "temperatura": 18.1,
        "umidita": 60.6
      },
      {
        "mese": "Feb",
        "casi_influenza": 14,
        "casi_legionellosi": 4,
        "casi_epatite_a": 0,
        "casi_totali": 18,
        "pm25": 11.8,
        "no2": 17.8,
        "temperatura": 23.3,
        "umidita": 54.0
      },
      {
        "mese": "Mar",
        "casi_influenza": 7,
        "casi_legionellosi": 5,
        "casi_epatite_a": 0,
        "casi_totali": 12,
        "pm25": 9.5,
        "no2": 16.1,
        "temperatura": 26.4,
        "umidita": 51.3
      },
      {
        "mese": "Apr",
        "casi_influenza": 7,
        "casi_legionellosi": 4,
        "casi_epatite_a": 0,
        "casi_totali": 11,
        "pm25": 9.8,
        "no2": 15.7,
        "temperatura": 26.6,
        "umidita": 51.0
      },
      {
        "mese": "Mag",
        "casi_influenza": 14,
        "casi_legionellosi": 1,
        "casi_epatite_a": 0,
        "casi_totali": 15,
        "pm25": 11.8,
        "no2": 18.0,
        "temperatura": 23.3,
        "umidita": 54.6
      },
      {
        "mese": "Giu",
        "casi_influenza": 20,
        "casi_legionellosi": 1,
        "casi_epatite_a": 0,
        "casi_totali": 21,
        "pm25": 15.7,
        "no2": 22.3,
        "temperatura": 18.2,
        "umidita": 61.4
      },
      {
        "mese": "Lug",
        "casi_influenza": 22,
        "casi_legionellosi": 5,
        "casi_epatite_a": 1,
        "casi_totali": 28,
        "pm25": 20.2,
        "no2": 27.5,
        "temperatura": 12.0,
        "umidita": 68.7
      },
      {
        "mese": "Ago",
        "casi_influenza": 44,
        "casi_legionellosi": 4,
        "casi_epatite_a": 0,
        "casi_totali": 48,
        "pm25": 24.3,
        "no2": 31.6,
        "temperatura": 6.6,
        "umidita": 75.4
      },
      {
        "mese": "Set",
        "casi_influenza": 45,
        "casi_legionellosi": 4,
        "casi_epatite_a": 0,
        "casi_totali": 49,
        "pm25": 26.3,
        "no2": 35.0,
        "temperatura": 3.5,
        "umidita": 79.0
      },
      {
        "mese": "Ott",
        "casi_influenza": 33,
        "casi_legionellosi": 5,
        "casi_epatite_a": 0,
        "casi_totali": 38,
        "pm25": 26.6,
        "no2": 34.9,
        "temperatura": 3.7,
        "umidita": 79.0
      },
      {
        "mese": "Nov",
        "casi_influenza": 48,
        "casi_legionellosi": 6,
        "casi_epatite_a": 1,
        "casi_totali": 55,
        "pm25": 24.3,
        "no2": 31.7,
        "temperatura": 6.7,
        "umidita": 75.0
      },
      {
        "mese": "Dic",
        "casi_influenza": 25,
        "casi_legionellosi": 5,
        "casi_epatite_a": 0,
        "casi_totali": 30,
        "pm25": 20.2,
        "no2": 28.1,
        "temperatura": 12.0,
        "umidita": 69.4
      }
    ],
    "ripartizione_malattie": {
      "influenza": 300,
      "legionellosi": 48,
      "epatite_a": 2
    },
    "fonti_dati": {
      "ARPA_CAMPANIA": 83055,
      "ISTAT": 54825,
      "SINTETICO": 137880
    }
  }
}

# Endpoints API

@app.get("/")
async def root():
    """Endpoint principale"""
    return {
        "messaggio": "API HealthTrace con Dati Sintetici è attiva!",
        "versione": "2.0.0",
        "stato": "attivo",
        "fonti_dati": ["ARPA_CAMPANIA_SINTETICO", "ISTAT_SINTETICO", "SALUTE_SINTETICO"],
        "malattie_supportate": ["influenza", "legionellosi", "epatite_a"],
        "regioni_coperte": ["Campania", "Calabria", "Molise"],
        "ultimo_aggiornamento": datetime.now().isoformat()
    }

@app.get("/salute")
async def health_check():
    """Controllo stato sistema"""
    return {"stato": "attivo", "timestamp": datetime.now().isoformat()}

@app.get("/api/v1/dashboard/riassunto")
async def ottieni_riassunto_dashboard():
    """Ottieni riassunto dashboard principale"""
    return DATI_POTENZIATI["riassunto_dashboard"]

@app.get("/api/v1/malattie/{nome_malattia}/analisi")
async def ottieni_analisi_malattie(nome_malattia: str):
    """Ottieni analisi dettagliate per malattia specifica"""
    analisi_malattie = {
        "influenza": {
            "nome": "Influenza Stagionale",
            "casi_totali": 300,
            "trend_mensile": "in_diminuzione",
            "fattori_correlati": ["PM2.5", "PM10", "Temperatura", "Umidità"],
            "correlazione_principale": {"fattore": "PM2.5", "valore": 0.82},
            "soglia_rischio": {"PM2.5": "> 25 μg/m³", "Temperatura": "< 10°C"},
            "modello_raccomandato": "GAM con termini di ritardo"
        },
        "legionellosi": {
            "nome": "Legionellosi",
            "casi_totali": 48,
            "trend_mensile": "stabile",
            "fattori_correlati": ["Temperatura Acqua", "Umidità", "Precipitazioni"],
            "correlazione_principale": {"fattore": "Temperatura Acqua", "valore": 0.71},
            "soglia_rischio": {"Temperatura_Acqua": "> 25°C", "Umidità": "> 70%"},
            "modello_raccomandato": "DLNM per effetti temperatura"
        },
        "epatite_a": {
            "nome": "Epatite A",
            "casi_totali": 2,
            "trend_mensile": "basso",
            "fattori_correlati": ["E.coli", "pH", "Cloro Residuo", "Precipitazioni"],
            "correlazione_principale": {"fattore": "E.coli", "valore": 0.85},
            "soglia_rischio": {"E_coli": "> 100 CFU/100ml", "pH": "< 6.5 o > 8.5"},
            "modello_raccomandato": "GLM con indicatori qualità acqua"
        }
    }
    
    return analisi_malattie.get(nome_malattia.lower(), {"errore": "Malattia non trovata"})

@app.get("/api/v1/ambientale/fattori")
async def ottieni_fattori_ambientali():
    """Ottieni dati fattori ambientali"""
    return {
        "inquinanti_aria": ["PM10", "PM2.5", "O3", "NO2", "SO2", "C6H6", "CO"],
        "parametri_meteo": ["temperatura", "umidità", "precipitazioni", "velocità_vento", "pressione"],
        "qualita_acqua": ["pH", "conteggio_ecoli", "cloro_residuo", "temperatura_acqua"],
        "ultimo_aggiornamento": datetime.now().isoformat(),
        "stazioni_monitoraggio": 145,
        "misurazioni_giornaliere": 2880
    }

@app.get("/api/v1/analisi/correlazione")
async def ottieni_analisi_correlazione():
    """Ottieni analisi correlazioni ambiente-malattie"""
    return {
        "data_analisi": datetime.now().isoformat(),
        "metodologia": "Correlazione di Pearson con analisi ritardi",
        "malattie_analizzate": [
            "influenza",
            "legionellosi", 
            "epatite_a"
        ],
        "fattori_ambientali": [
            "PM10", "PM25", "O3", "NO2", "SO2", "C6H6", "CO",
            "temperatura", "umidità", "precipitazioni", "velocità_vento", "pressione",
            "ph", "conteggio_ecoli", "cloro_residuo", "temperatura_acqua"
        ],
        "matrice_correlazione": {
            "influenza": {
                "fattori_primari": [
                    "PM2.5", "PM10", "temperatura", "umidità"
                ],
                "forza_correlazione": "forte",
                "periodo_ritardo_giorni": "0-7",
                "effetti_soglia": {
                    "PM2.5": "> 25 μg/m³",
                    "temperatura": "< 10°C"
                }
            },
            "legionellosi": {
                "fattori_primari": [
                    "temperatura_acqua", "umidità", "precipitazioni"
                ],
                "forza_correlazione": "molto_forte",
                "periodo_ritardo_giorni": "7-21",
                "effetti_soglia": {
                    "temperatura_acqua": "> 25°C",
                    "umidità": "> 70%"
                }
            },
            "epatite_a": {
                "fattori_primari": [
                    "E.coli", "pH", "cloro_residuo", "precipitazioni"
                ],
                "forza_correlazione": "forte",
                "periodo_ritardo_giorni": "14-28",
                "effetti_soglia": {
                    "E.coli": "> 100 CFU/100ml",
                    "pH": "< 6.5 o > 8.5"
                }
            }
        },
        "significatività_statistica": {},
        "raccomandazioni_modelli": {
            "influenza": {
                "modello_primario": "GAM con termini di ritardo",
                "modelli_secondari": [
                    "ARIMAX",
                    "Random Forest"
                ],
                "analisi_spaziale": "I di Moran per raggruppamento geografico",
                "previsioni": "ARIMAX con PM2.5 e temperatura",
                "interpretazione": "GAM per curve esposizione-risposta"
            },
            "legionellosi": {
                "modello_primario": "DLNM per effetti temperatura",
                "modelli_secondari": [
                    "Case-Crossover",
                    "Regressione Spaziale"
                ],
                "analisi_spaziale": "Getis-Ord Gi* per rilevamento hotspot",
                "previsioni": "ARIMAX con temperatura acqua",
                "interpretazione": "DLNM per analisi struttura ritardi"
            },
            "epatite_a": {
                "modello_primario": "GLM con indicatori qualità acqua",
                "modelli_secondari": [
                    "Random Forest",
                    "DLNM"
                ],
                "analisi_spaziale": "Regressione spaziale per mappatura contaminazione",
                "previsioni": "ARIMAX con precipitazioni ed E.coli",
                "interpretazione": "Random Forest per importanza fattori"
            }
        }
    }

@app.get("/api/v1/malattie/")
async def ottieni_lista_malattie():
    """Ottieni lista malattie monitorate"""
    return {
        "malattie_supportate": [
            {
                "id": "influenza",
                "nome": "Influenza Stagionale",
                "categoria": "respiratoria",
                "casi_attivi": 105,
                "casi_totali": 300,
                "ultimo_caso": "2025-10-29"
            },
            {
                "id": "legionellosi",
                "nome": "Legionellosi",
                "categoria": "idrica",
                "casi_attivi": 8,
                "casi_totali": 48,
                "ultimo_caso": "2025-10-28"
            },
            {
                "id": "epatite_a",
                "nome": "Epatite A",
                "categoria": "alimentare",
                "casi_attivi": 1,
                "casi_totali": 2,
                "ultimo_caso": "2025-10-15"
            }
        ],
        "totale_malattie": 3,
        "casi_totali_sistema": 350,
        "ultimo_aggiornamento": datetime.now().isoformat()
    }

@app.get("/api/v1/istat/{codice_istat}/{anno}/{intervallo}/{funzione}/{inquinante}/")
async def ottieni_dati_istat(
    codice_istat: str,
    anno: int,
    intervallo: int,
    funzione: str,
    inquinante: str
):
    """API compatibile ISTAT per dati ambientali"""
    
    # Simula dati ISTAT realistici per dimostrazione
    dati_esempio = {
        "codice_istat": codice_istat,
        "anno": anno,
        "intervallo": intervallo,
        "funzione": funzione,
        "inquinante": inquinante,
        "valori": [
            {"data": f"{anno}-{str(i).zfill(2)}-15", "valore": 25.3 + (i * 1.2), "unita": "μg/m³"}
            for i in range(1, 13) if intervallo == 0 or i == intervallo
        ],
        "stazione_monitoraggio": f"IT{codice_istat}A",
        "fonte": "ARPA_CAMPANIA_SINTETICO",
        "qualita_dato": "validato"
    }
    
    return dati_esempio

@app.get("/api/v1/modelli/disponibili")
async def ottieni_modelli_disponibili():
    """Ottieni lista modelli analytici disponibili"""
    return {
        "modelli_statistici": [
            {
                "nome": "GAM",
                "descrizione": "Modelli Additivi Generalizzati",
                "uso": "Correlazioni non-lineari ambiente-salute",
                "parametri": ["temperatura", "PM2.5", "umidità"]
            },
            {
                "nome": "DLNM", 
                "descrizione": "Modelli Non-Lineari a Ritardo Distribuito",
                "uso": "Effetti ritardati inquinanti",
                "parametri": ["ritardo", "esposizione", "temperatura"]
            },
            {
                "nome": "ARIMAX",
                "descrizione": "ARIMA con Variabili Esogene", 
                "uso": "Previsioni serie temporali",
                "parametri": ["ordine", "variabili_esogene"]
            }
        ],
        "modelli_machine_learning": [
            {
                "nome": "Random Forest",
                "descrizione": "Foresta Casuale",
                "uso": "Classificazione e ranking importanza variabili",
                "parametri": ["n_estimatori", "profondità_max"]
            },
            {
                "nome": "XGBoost",
                "descrizione": "Gradient Boosting Estremo",
                "uso": "Previsioni alta performance",
                "parametri": ["tasso_apprendimento", "n_stimatori"]
            }
        ],
        "modelli_spaziali": [
            {
                "nome": "I di Moran",
                "descrizione": "Autocorrelazione Spaziale",
                "uso": "Rilevamento cluster geografici",
                "parametri": ["matrice_pesi", "distanza"]
            },
            {
                "nome": "Getis-Ord Gi*",
                "descrizione": "Statistica Hotspot",
                "uso": "Identificazione hotspot malattie",
                "parametri": ["banda", "distanza_soglia"]
            }
        ]
    }

@app.get("/api/v1/geografia/regioni")
async def ottieni_dati_geografici():
    """Dati geografici per analisi territoriale"""
    return {
        "regioni": {
            "molise": {
                "centro": [41.7, 14.6],
                "casi": {"influenza": 180, "legionellosi": 8, "epatite_a": 0},
                "popolazione": 294294,
                "densita": 66.2,
                "fattori_rischio": ["PM2.5 Alto", "Inversione Termica", "Bassa Ventilazione"],
                "hotspot_attivi": 2,
                "livello_rischio": "alto"
            },
            "campania": {
                "centro": [40.8, 14.2],
                "casi": {"influenza": 95, "legionellosi": 28, "epatite_a": 0},
                "popolazione": 5712143,
                "densita": 424.0,
                "fattori_rischio": ["Densità Urbana", "Temperatura Acqua", "Umidità Alta"],
                "hotspot_attivi": 3,
                "livello_rischio": "medio"
            },
            "calabria": {
                "centro": [39.3, 16.2],
                "casi": {"influenza": 25, "legionellosi": 12, "epatite_a": 2},
                "popolazione": 1894110,
                "densita": 125.9,
                "fattori_rischio": ["Qualità Idrica", "Sicurezza Alimentare", "Precipitazioni"],
                "hotspot_attivi": 1,
                "livello_rischio": "basso"
            }
        },
        "hotspot": [
            {"lat": 41.5603, "lng": 14.6685, "intensita": 15, "tipo": "influenza", "regione": "Molise - Campobasso"},
            {"lat": 40.8518, "lng": 14.2681, "intensita": 8, "tipo": "legionellosi", "regione": "Campania - Napoli"},
            {"lat": 39.2986, "lng": 16.2543, "intensita": 3, "tipo": "epatite_a", "regione": "Calabria - Cosenza"},
            {"lat": 41.4691, "lng": 14.9806, "intensita": 6, "tipo": "influenza", "regione": "Molise - Termoli"},
            {"lat": 40.6340, "lng": 14.6033, "intensita": 4, "tipo": "legionellosi", "regione": "Campania - Salerno"}
        ],
        "statistiche_generali": {
            "regioni_monitorate": 3,
            "comuni_attivi": 15,
            "sensori_ambientali": 127,
            "hotspot_identificati": 5
        }
    }

@app.get("/api/v1/previsioni/modelli")
async def ottieni_modelli_predittivi():
    """Informazioni sui modelli predittivi attivi"""
    return {
        "modelli_attivi": {
            "gam": {
                "nome": "Generalized Additive Model",
                "accuracy": 89.2,
                "auc": 0.87,
                "mae": 12.3,
                "malattie_target": ["influenza"],
                "variabili_principali": ["PM2.5", "Temperatura", "Umidità", "Lag temporali"],
                "descrizione": "Modello ottimale per relazioni non-lineari e trend stagionali"
            },
            "arimax": {
                "nome": "ARIMAX",
                "accuracy": 82.5,
                "r2": 0.83,
                "rmse": 15.7,
                "malattie_target": ["influenza", "legionellosi"],
                "componenti": ["Autogressione", "Media Mobile", "Stagionalità", "Covarianze Esterne"],
                "descrizione": "Serie temporali per previsioni a medio termine"
            },
            "dlnm": {
                "nome": "Distributed Lag Non-linear Model",
                "accuracy": 91.8,
                "auc": 0.92,
                "mae": 8.9,
                "malattie_target": ["legionellosi"],
                "specializzazioni": ["Lag Distribuiti", "Effetti Cumulativi", "Temperatura", "Umidità"],
                "descrizione": "Eccellente per effetti ritardati della temperatura"
            },
            "random_forest": {
                "nome": "Random Forest",
                "accuracy": 85.3,
                "precision": 0.86,
                "recall": 0.84,
                "malattie_target": ["epatite_a", "influenza"],
                "punti_forza": ["Interazioni", "Non-linearità", "Feature Importance", "Robustezza"],
                "descrizione": "Ensemble robusto per classificazione rischio multifattoriale"
            },
            "xgboost": {
                "nome": "XGBoost",
                "accuracy": 87.9,
                "f1_score": 0.88,
                "mae": 11.2,
                "malattie_target": ["influenza", "legionellosi", "epatite_a"],
                "caratteristiche": ["Boosting", "Regularizzazione", "Velocità", "Accuratezza"],
                "descrizione": "Gradient boosting per previsioni ad alta performance"
            },
            "spatial": {
                "nome": "Modelli Spaziali",
                "accuracy": 83.7,
                "morans_i": 0.84,
                "rmse": 14.6,
                "malattie_target": ["tutte"],
                "analisi_spaziale": ["Autocorrelazione Spaziale", "Cluster Detection", "Kriging", "Hotspot Analysis"],
                "descrizione": "Modelli geo-statistici per diffusione spaziale"
            }
        },
        "performance_comparativa": {
            "migliore_accuratezza": "dlnm",
            "migliore_velocità": "xgboost",
            "migliore_interpretabilità": "gam",
            "migliore_robustezza": "random_forest"
        }
    }

@app.get("/api/v1/previsioni/forecast")
async def ottieni_previsioni():
    """Previsioni per i prossimi 14 giorni"""
    import random
    
    # Genera previsioni sintetiche per 14 giorni
    giorni = []
    for i in range(14):
        data_corrente = datetime.now() + timedelta(days=i)
        giorni.append(data_corrente.strftime("%Y-%m-%d"))
    
    return {
        "periodo_previsione": f"{giorni[0]} - {giorni[-1]}",
        "previsioni_per_malattia": {
            "influenza": {
                "regione": "Molise",
                "modello_utilizzato": "GAM",
                "confidenza": 89,
                "livello_rischio": "alto",
                "casi_previsti": [23 + random.randint(-3, 7) for _ in range(14)],
                "picco_previsto": giorni[5],
                "raccomandazioni": "Rafforzare sorveglianza per condizioni meteorologiche avverse"
            },
            "legionellosi": {
                "regione": "Campania",
                "modello_utilizzato": "DLNM",
                "confidenza": 78,
                "livello_rischio": "medio",
                "casi_previsti": [8 + random.randint(-2, 5) for _ in range(14)],
                "trend": "incremento_graduale",
                "raccomandazioni": "Monitorare sistemi idrici per aumento temperature"
            },
            "epatite_a": {
                "regione": "Calabria",
                "modello_utilizzato": "Random Forest",
                "confidenza": 71,
                "livello_rischio": "basso",
                "casi_previsti": [random.randint(0, 2) for _ in range(14)],
                "trend": "stabile",
                "raccomandazioni": "Attivare sorveglianza per precipitazioni intense"
            }
        },
        "alert_attivi": [
            "Molise: Picco influenzale previsto in 5-7 giorni (confidenza 89%)",
            "Campania: Incremento legionellosi per temperature elevate (confidenza 78%)",
            "Calabria: Monitoraggio epatite A per piogge previste (confidenza 71%)"
        ],
        "timestamp_generazione": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
