**HealthTrace — Dashboard Mockups**  
Questa cartella contiene 6 pagine HTML di mockup del dashboard della piattaforma HealthTrace.  
   
 Ogni pagina è un file HTML autonomo, apribile nel browser, pronto per screenshot e inserimento nei documenti di progetto.  
   
**Come usare i mockup**  
1. Aprire il file HTML nel browser (Chrome o Firefox consigliati)  
2. Fare uno screenshot dell'intera pagina (F12 → "Capture full size screenshot" in Chrome DevTools)  
3. Inserire l'immagine nel documento come illustrazione della pagina del dashboard  
*Nota: la Pagina 2 (Sorveglianza Geografica) richiede connessione internet per caricare la mappa OpenStreetMap. Tutte le altre pagine funzionano offline.*  
   
**Struttura e Razionale del Dashboard**  
Il dashboard è strutturato in **6 pagine funzionali**, derivate dagli obiettivi della piattaforma:  
- **Obiettivo primario**: correlare dati ambientali ARPAC/MeteoHub con casi di malattie infettive GESAN per rilevare e prevedere focolai nelle regioni Campania, Molise, Calabria.  
- **Malattie target (Fase 1)**: Influenza (r=0.821 con PM2.5), Legionellosi (r=0.756 con Umidità), Epatite A (r=0.743 con Precipitazioni).  
- **Utenti**: Autorità sanitarie regionali (ASL), epidemiologi, responsabili del sistema di sorveglianza.  
   
**Pagine**  
   
**Pagina 1 — Dashboard Principale**  
**File**: page1_dashboard_principale.html  
**Scopo**: Panoramica operativa sintetica per il responsabile della sorveglianza. Punto di accesso quotidiano alla piattaforma.  
**Contenuto**:  
- **Banner di allerta**: notifica visibile in caso di allerte attive (es. PM2.5 sopra soglia per 3 giorni consecutivi)  
- **4 KPI cards**: Nuovi casi settimanali, Allerte attive, PM2.5 medio Napoli, Comuni a rischio elevato  
- **Grafico andamento malattie** (line chart 90 giorni): casi settimanali di Influenza, Legionellosi, Epatite A  
- **Grafico parametri ambientali vs soglia** (bar chart): confronto tra valori odierni e soglie di allerta per PM2.5, PM10, NO₂, O₃, Temperatura, Umidità  
- **Tabella ultime segnalazioni**: 5 notifiche più recenti da GESAN con stato (notificato/in revisione/confermato/chiuso)  
- **Riepilogo per malattia**: score settimanale con barra di progresso, correlazione principale, prognosi 7 giorni  
**Perché questa pagina**: È la home page del sistema. Un responsabile ASL deve poter valutare in 30 secondi la situazione epidemiologica e ambientale senza navigare tra sezioni.  
   
**Pagina 2 — Sorveglianza Geografica**  
**File**: page2_sorveglianza_geografica.html  
**Scopo**: Visualizzazione geografica interattiva dei casi di malattia e dei parametri ambientali sul territorio delle 3 regioni.  
**Contenuto**:  
- **Mappa interattiva** (Leaflet + OpenStreetMap): mappa dei comuni con cerchi proporzionali ai casi di malattia, colorati per livello di rischio (verde/giallo/rosso)  
- **Marcatori stazioni ARPAC**: posizione delle stazioni di monitoraggio qualità aria attive  
- **Pannello livelli (sinistra)**: controllo visibilità per ogni strato (Influenza, Legionellosi, Epatite A, PM2.5, NO₂, Temperatura, Umidità, Precipitazioni)  
- **Statistiche riepilogo**: comuni monitorati, casi attivi totali, comuni con alert PM2.5  
- **Legenda**: scala dimensionale cerchi (casi) e scala cromatica (intensità PM2.5)  
- **Pannello info comune (destra)**: scheda dettagliata del comune selezionato con dati epidemiologici, qualità aria, meteo e stazioni attive  
**Perché questa pagina**: La distribuzione geografica è fondamentale per individuare focolai localizzati e per verificare se il superamento di soglie ambientali corrisponde a un aumento di casi nelle stesse aree geografiche.  
   
**Pagina 3 — Correlazioni Ambiente–Malattie Infettive**  
**File**: page3_correlazioni_ambiente_malattie.html  
**Scopo**: Analisi statistica approfondita delle correlazioni tra parametri ambientali e incidenza di malattie infettive. Pagina principale per epidemiologi e ricercatori.  
**Contenuto**:  
- **Barra filtri**: selezione periodo temporale, regione, lag temporale (0/3/7/14 giorni)  
- **Matrice di correlazione** (heatmap colorata): coefficiente r di Pearson per ogni coppia malattia × parametro ambientale (PM2.5, PM10, NO₂, Temperatura, Umidità, Precipitazioni), con significatività statistica (*, **, ***)  
- **Classifica top correlazioni**: le 8 correlazioni più forti con barra visuale, r e p-value  
- **Scatter plot PM2.5 vs Influenza**: dispersione delle osservazioni settimanali per comune con retta di tendenza (n=2.847, r=0.821, p<0.001)  
- **Serie temporale dual-axis**: casi Influenza (asse sinistro) e PM2.5 medio (asse destro) sovrapposti su 12 mesi — evidenzia la co-variazione stagionale  
- **Analisi del lag temporale**: curva del coefficiente r al variare del ritardo temporale (0–21 giorni), con identificazione del lag ottimale (5–7 giorni)  
**Perché questa pagina**: Le correlazioni sono il cuore scientifico del progetto. Questa pagina supporta la validazione delle ipotesi di causalità ambientale e permette di scegliere i predittori da inserire nei modelli ML.  
   
**Pagina 4 — Monitoraggio Ambientale**  
**File**: page4_monitoraggio_ambientale.html  
**Scopo**: Monitoraggio near-realtime e storico dei parametri ambientali provenienti dalle stazioni ARPAC (qualità aria) e MeteoHub (meteorologia) di Ambientali Fattori.  
**Contenuto**:  
- **Header stato stazioni**: contatore rapido stazioni attive / offline / in manutenzione  
- **Tab selettore fonte**: ARPAC / MeteoHub / Tutti i parametri  
- **6 schede parametro** con barra di stato e dot colorato animato:  
- PM2.5 (con indicatore SUPERATA soglia)  
- PM10, NO₂, O₃ (OK)  
- Temperatura (OK)  
- Umidità relativa (attenzione — vicina alla soglia)  
- **Time series PM2.5** ultimi 7 giorni con linea rossa di soglia WHO (25 μg/m³)  
- **Time series Temperatura + Umidità** con doppio asse Y (ultimi 7 giorni)  
- **Tabella stazioni**: elenco stazioni con ultima lettura, stato, comune ISTAT, quota slm, valore di ogni parametro (rosso se sopra soglia, grigio se offline)  
**Perché questa pagina**: L'ingestion pipeline (JOB-01) acquisisce questi dati ogni giorno da Ambientali Fattori. Questa vista permette ai tecnici di verificare la qualità del dato e il funzionamento delle stazioni in tempo reale, oltre a identificare rapidamente i superamenti di soglia che attiveranno le allerte.  
   
**Pagina 5 — Modelli Predittivi**  
**File**: page5_modelli_predittivi.html  
**Scopo**: Presentazione delle previsioni di incidenza epidemiologica a 7–14 giorni generate dai modelli ML (XGBoost, ARIMAX, DLNM), con valutazione del rischio per provincia e spiegabilità del modello.  
**Contenuto**:  
- **3 schede forecast per malattia**: indicatore di rischio (alto/moderato/basso), casi attesi nella settimana, baseline storica, percentuale di confidenza del modello, trend  
- **Grafico previsione Influenza** (14 giorni): curva storica + curva predetta + banda di confidenza al 90% — con selettore modello (XGBoost / ARIMAX / DLNM / Ensemble)  
- **Feature importance XGBoost**: le 7 variabili più importanti del modello con contributo percentuale (PM2.5 lag 7gg = 24%, Temperatura lag 5gg = 19%, Umidità = 16%, ...)  
- **Metriche di performance**: R² = 0.87, RMSE = 8.3 casi/settimana, MAPE = 9.2%, MAE = 6.1 (validazione out-of-sample gen–apr 2026)  
- **Tabella rischio per provincia**: score 0–100 per ogni malattia e ogni provincia delle 3 regioni, con azione raccomandata (allerta preventiva / monitoraggio attivo / nessuna azione)  
**Perché questa pagina**: I modelli predittivi sono l'output scientifico principale del sistema. Questa pagina traduce i risultati ML in decisioni operative per le autorità sanitarie (quando emettere allerte preventive, dove concentrare le risorse di sorveglianza).  
   
**Pagina 6 — Gestione Allerte**  
**File**: page6_gestione_allerte.html  
**Scopo**: Centro operativo di gestione delle allerte generate dal RealtimeAlertConsumer (Pipeline 2). Permette di visualizzare, prendere in carico e risolvere le allerte ambientali.  
**Contenuto**:  
- **4 KPI cards**: Allerte critiche attive, allerte moderate, allerte risolte (30 giorni), falsi positivi  
- **Lista allerte attive** (3 allerte):  
- 2 allerte critiche PM2.5 (Napoli e Caserta): con descrizione tecnica, timestamp, stazioni coinvolte, pulsanti "Notifica ASL" / "Prendi in carico"  
- 1 allerta moderata Umidità (Salerno): con proiezione del trend nelle prossime 12 ore  
- **Storico allerte 30 giorni** (stacked bar chart): numero di allerte giornaliere per tipo di parametro (PM2.5/PM10, Umidità/Temperatura, NO₂/O₃)  
- **Tabella soglie configurate**: tutti i 7 parametri monitorati dal RealtimeAlertConsumer con valore attuale, soglia, barra di riempimento e badge stato (OK / VICINA / SUPERATA)  
**Perché questa pagina**: La Pipeline 2 (Realtime) non scrive dati nel database — genera solo eventi di allerta su Kafka (topic analytics_trigger). Questa pagina è l'interfaccia operativa che riceve quegli eventi e supporta il flusso di risposta delle autorità sanitarie.  
   
**Design System Applicato**  
Tutte le pagine seguono le specifiche di stile definite nel documento **D.4 §1.1**:  
| | | |  
|-|-|-|  
| **Elemento** | **Valore** | **Utilizzo** |   
| Navbar background | #0F3157 | Barra navigazione superiore |   
| Sidebar active | #EDEDED / #123B67 | Voce menu selezionata |   
| Pulsante Success | #28A745 | Conferma, inserimento |   
| Pulsante Warning | #FFC107 | Modifica, attenzione |   
| Pulsante Danger | #DC3545 | Elimina, allerta critica |   
| Pulsante Info | #16A3B7 | Ricerca, near-realtime |   
| Testo tabelle | #0E3964 | Celle con dati alfanumerici |   
| Testo form/label | #616161 | Etichette, icone inattive |   
| Border-radius | 4px | Tutti i bottoni e card |   
| Font | System font stack | -apple-system, Segoe UI, Roboto, … |   
| Line-height | 1.4 | Corpo testo |   
   
   
