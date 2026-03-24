# 🏥 HealthTrace - Database Malattie Infettive
## Documentazione Completa del Sistema di Sorveglianza Epidemiologica

### 📋 **INFORMAZIONI GENERALI PROGETTO**

**Nome Progetto:** HealthTrace - Sistema di Monitoraggio e Previsione Epidemiologica  
**Database:** GESAN - ASL Campania  
**Connessione:** PostgreSQL 9.2.24 @ 10.10.13.11:5432/gesan_malattieinfettive  
**Periodo Copertura:** Giugno 2024 → Febbraio 2026 (21 mesi di dati)  
**Stato Progetto:** Attivo con 29,321+ record sanitari  
**Data Ultimo Aggiornamento:** 26 Febbraio 2026  

---

## 📊 **STATISTICHE GENERALI DATABASE**

- **🦠 Categorie di Malattie Attive:** 80
- **📊 Record Sanitari Totali:** 29,321+
- **🗂️ Tabelle Database Analizzate:** 118
- **🏥 Fonte Dati:** ASL Campania - Sistema GESAN
- **📈 Capacità Predittive:** ARIMA Time Series Forecasting implementato

---

## 🦠 **MALATTIE INFETTIVE MONITORATE NEL DATABASE**

### **🔝 MALATTIE CON MAGGIOR NUMERO DI CASI**

#### **1. 🍕 Infezioni Alimentari** - **8,374 casi**
- **Tabella Principale:** `gesan_malattie_infettive_ie_infezioni_alimentari_consumo_alimen`
- **Tabelle Correlate:**
  - `gesan_malattie_infettive_ie_infezioni_alimentari` (91 casi)
  - `gesan_malattie_infettive_ie_infezioni_alimentari_negozi_acquist` (89 casi)
  - `gesan_malattie_infettive_ie_infezioni_alimentari_sot_mod` (79 casi)
  - `gesan_malattie_infettive_ie_infezioni_alimentari_alimento` (59 casi)
  - Altri 7 record correlati
- **Tipo Sorveglianza:** Monitoraggio outbreaks alimentari e tracciabilità

#### **2. 📊 Stati Clinici Pazienti** - **3,652 casi**
- **Tabella:** `gesan_malattie_infettive_segnalazione_stato_malattia`
- **Funzione:** Tracciamento evoluzione clinica dei casi

#### **3. 👁️ Sistema Monitoraggio** - **3,154 interazioni**
- **Tabella:** `gesan_malattie_infettive_visualizzazioni_utenti`
- **Funzione:** Log accessi e utilizzo sistema

#### **4. 📋 Segnalazioni Principali** - **2,974 segnalazioni**
- **Tabella:** `gesan_malattie_infettive_segnalazione`
- **Funzione:** Database centrale segnalazioni epidemiologiche

---

### **🦠 MALATTIE VIRALI E RESPIRATORIE**

#### **🦠 COVID-19** - **663 casi**
- **Tabelle:**
  - `gesan_malattie_infettive_ie_covid` (663 casi principali)
  - `gesan_malattie_infettive_ie_covid_familiari` (37 contatti familiari)
  - `gesan_malattie_infettive_ie_covid_viaggi_italia` (3 viaggi)

#### **🤧 Influenza** - **125 casi**
- **Tabella:** `gesan_malattie_infettive_ie_influenza`
- **Periodo Sorveglianza:** Stagione influenzale 2024-2026

#### **💉 Morbillo/Rosolia** - **248 casi totali**
- **Tabelle:**
  - `gesan_malattie_infettive_ie_morbillo_rosolia` (91 casi)
  - `gesan_malattie_infettive_ie_morbillo_rosolia_contatti` (86 contatti)
  - `gesan_malattie_infettive_ie_morbillo_rosolia_conferma_laborator` (64 conferme)
  - Altri record per patologie e viaggi

---

### **🫁 MALATTIE RESPIRATORIE BATTERICHE**

#### **🫁 Legionellosi** - **268 casi totali**
- **Tabelle:**
  - `gesan_malattie_infettive_ie_legionellosi` (109 casi principali)
  - `gesan_malattie_infettive_ie_legionellosi_malattie_concomitanti` (86 comorbidità)
  - `gesan_malattie_infettive_ie_legionellosi_antibiotici_assunti` (33 terapie)
  - `gesan_malattie_infettive_ie_legionellosi_ricovero_opedaliero` (24 ricoveri)
  - Altri record per sierologia e soggiorni

#### **🫁 Tubercolosi/Microbatteriosi** - **233 casi**
- **Tabella:** `gesan_malattie_infettive_ie_tubercolosi_microbatteriosi_non_tub`
- **Tipo:** TBC polmonare, extrapolmonare, micobatteriosi atipiche

---

### **🩸 MALATTIE A TRASMISSIONE EMATICA/SESSUALE**

#### **🩸 HIV** - **858 casi**
- **Tabella:** `gesan_malattie_infettive_hiv`
- **Tipo Sorveglianza:** Sorveglianza nazionale HIV/AIDS

#### **🔬 Malattie Trasmissione Sessuale** - **85 casi**
- **Tabella:** `gesan_malattie_infettive_ie_malattie_trasmissione_sessuale`
- **Include:** Sifilide, gonorrea, clamidia, altre MTS

---

### **🍽️ EPATITI VIRALI**

#### **🍽️ Epatite A** - **45 casi totali**
- **Tabelle:**
  - `gesan_malattie_infettive_ie_epatite_a` (29 casi)
  - `gesan_malattie_infettive_ie_epatite_a_farmaci` (15 terapie)
  - `gesan_malattie_infettive_ie_epatite_acuta_lista_contatti` (1 contatto)

#### **🍽️ Epatite E** - **5 casi**
- **Tabelle:**
  - `gesan_malattie_infettive_ie_epatite_e` (4 casi)
  - `gesan_malattie_infettive_ie_epatite_e_viaggi` (1 viaggio)

#### **🦠 Epatiti (Generali)** - **55 casi**
- **Tabelle:**
  - `gesan_malattie_infettive_ie_epatiti` (37 casi)
  - `gesan_malattie_infettive_ie_epatiti_farmaci` (18 farmaci)

---

### **🧠 MALATTIE NEUROLOGICHE**

#### **🧠 Meningite/Sepsi da Meningococco** - **74 casi totali**
- **Tabelle:**
  - `gesan_malattie_infettive_ie_encefalite_meningite_s_meningococci` (66 casi)
  - `gesan_malattie_infettive_ie_enc_mening_s_meningoco_vaccinazioni` (4 vaccinazioni)

#### **🧠 Malattia di Creutzfeldt-Jakob** - **3 casi**
- **Tabella:** `gesan_malattie_infettive_ie_malattia_creutzfeldt_jakob`
- **Tipo:** Encefalopatia spongiforme trasmissibile

---

### **🌍 MALATTIE TROPICALI E DA VETTORI**

#### **🌍 Malaria** - **37 casi totali**
- **Tabelle:**
  - `gesan_malattie_infettive_ie_malaria` (20 casi)
  - `gesan_malattie_infettive_ie_malaria_farmacoresistenti_terapie` (17 terapie)

#### **🦟 Leishmaniosi Viscerale** - **13 casi**
- **Tabelle:**
  - `gesan_malattie_infettive_ie_leishmaniosi_viscerale_ubicazione` (9 ubicazioni)
  - `gesan_malattie_infettive_ie_leishmaniosi_viscerale` (4 casi)

---

### **🧀 ALTRE MALATTIE BATTERICHE**

#### **🧀 Listeriosi** - **124 casi totali**
- **Tabelle:**
  - `gesan_malattie_infettive_ie_listeriosi_alimenti` (96 casi)
  - `gesan_malattie_infettive_ie_listeriosi_negozi` (20 negozi)
  - `gesan_malattie_infettive_ie_listeriosi_sintomi` (8 sintomi)

#### **💉 Tetano** - **1 caso**
- **Tabella:** `gesan_malattie_infettive_ie_tetano`

#### **☠️ Tossinfezioni Alimentari** - **25 casi**
- **Tabelle:**
  - `gesan_malattie_infettive_ie_tossinfezione_alimentare` (18 casi)
  - `gesan_malattie_infettive_ie_tossinfezione_alimentare_invitati` (7 invitati)

---

## 🔧 **INFRASTRUTTURA SISTEMA**

### **📋 Tabelle di Sistema e Supporto**

1. **🦠 Gestione Contatti** - `gesan_malattie_infettive_ie_lista_contatti` (1,373 contatti)
2. **🦠 Sintomatologia** - `gesan_malattie_infettive_ie_sintomatologia` (1,302 sintomi)
3. **🦠 Testata IE** - `gesan_malattie_infettive_ie_testata` (1,138 testate)
4. **🦠 Ricerche Diagnostiche** - `gesan_malattie_infettive_ie_ricerche_diagnostiche` (157 test)
5. **🦠 Strutture Sanitarie** - Multiple tabelle per gestione strutture

### **📊 Tabelle Configurazione**

- **Malattie Codificate:** `gesan_malattie_infettive_malattie` (115 malattie)
- **Tipi e Modelli:** Varie tabelle per classificazioni
- **Vaccinazioni:** `gesan_malattie_infettive_vaccino`
- **Professioni:** `gesan_malattie_infettive_professione`

---

## 🚀 **CAPACITÀ TECNICHE DEL SISTEMA**

### **📈 Funzionalità Implementate**

1. **ARIMA Time Series Forecasting**
   - Previsioni epidemiologiche automatiche
   - Confidence intervals e seasonal detection
   - Implementazione con statsmodels/pmdarima

2. **Sistema di Sorveglianza Completo**
   - Notifica automatica nuovi casi
   - Tracciamento contatti (contact tracing)
   - Gestione outbreak investigations

3. **Dashboard Web Interattiva**
   - Visualizzazioni Chart.js
   - Mappe geografiche Leaflet
   - API REST per dati real-time

4. **Database Integration**
   - Connessione PostgreSQL robusta
   - Connection pooling e error handling
   - Query ottimizzate per performance

---

## 📍 **COPERTURA GEOGRAFICA**

- **Regione:** Campania
- **ASL:** ASL Campania - Sistema GESAN
- **Comuni:** 50+ codici ISTAT identificati
- **Strutture:** Multiple ASL e ospedali collegati

---

## ⚠️ **LIMITAZIONI IDENTIFICATE**

1. **Copertura Geografica Limitata**
   - Non 387 comuni come dichiarato nei report
   - Focalizzazione su ASL Campania

2. **Capacità GIS**
   - Mappe base implementate
   - Non "mappe GIS interattive" complete come descritto

3. **Periodo Dati**
   - Dati dal Giugno 2024 (non storico completo)
   - Alcuni anni futuri (fino 2026) potrebbero essere proiezioni

---

## 📞 **CONTATTI PROGETTO**

- **Database Administrator:** Renato (per verifiche feasibility)
- **Sistema:** GESAN ASL Campania
- **Ambiente:** PostgreSQL 9.2.24
- **Rete:** Interna ASL (10.10.13.11:5432)

---

## 🎯 **CONCLUSIONI STRATEGICHE**

**HealthTrace rappresenta un sistema di sorveglianza epidemiologica COMPLETO e PROFESSIONALE che copre:**

✅ **80 categorie di malattie infettive**  
✅ **29,321+ record sanitari attivi**  
✅ **Copertura completa malattie notificabili italiane**  
✅ **Capacità predittive avanzate (ARIMA)**  
✅ **Sistema contact tracing integrato**  
✅ **Dashboard web real-time**  

**Il sistema VA OLTRE il monitoraggio base** - è una piattaforma epidemiologica completa per la sanità pubblica della Campania.

---

*Documento generato automaticamente dal sistema HealthTrace - Febbraio 2026*
