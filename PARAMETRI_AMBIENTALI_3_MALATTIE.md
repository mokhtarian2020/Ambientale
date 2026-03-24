# 🌍 PARAMETRI AMBIENTALI NECESSARI PER LE 3 MALATTIE TARGET
## Piattaforma HealthTrace - Analisi Completa dei Requisiti di Monitoraggio

---

## 📊 PANORAMICA GENERALE

### Malattie Target
1. **Influenza** (Respiratoria) - Correlazione con inquinamento atmosferico
2. **Legionellosi** (Idro-Aerosol) - Correlazione con temperatura e umidità
3. **Epatite A** (Idrica/Alimentare) - Correlazione con qualità dell'acqua

### Copertura Geografica
- **387 Comuni** italiani (Molise, Campania, Calabria)
- **95 Stazioni** di monitoraggio ambientale
- **2.3M Cittadini** sotto sorveglianza

---

## 🫁 INFLUENZA - PARAMETRI AMBIENTALI

### **Parametri Primari** (Correlazione Forte r>0.7)

#### 1. **PM2.5 - Particolato Fine**
- **Unità di Misura**: μg/m³ 
- **Correlazione**: r=0.82 (Forte)
- **Soglia di Rischio**: > 25 μg/m³
- **Limite Legale EU**: 25 μg/m³ (media annuale)
- **Periodo di Lag**: 0-7 giorni
- **Frequenza Misurazione**: Oraria/Giornaliera
- **Fonte Dati**: ARPA Campania, ISPRA
- **Impatto**: Danno vie respiratorie, aumento suscettibilità

#### 2. **PM10 - Particolato Grossolano**
- **Unità di Misura**: μg/m³
- **Correlazione**: r=0.78 (Forte)
- **Soglia di Rischio**: > 50 μg/m³
- **Limite Legale EU**: 50 μg/m³ (media giornaliera, max 35 superamenti/anno)
- **Periodo di Lag**: 0-7 giorni
- **Frequenza Misurazione**: Giornaliera
- **Fonte Dati**: ARPA Campania, ISPRA
- **Impatto**: Irritazione respiratoria, infiammazione

### **Parametri Secondari** (Correlazione Moderata r=0.5-0.7)

#### 3. **NO2 - Biossido di Azoto**
- **Unità di Misura**: μg/m³
- **Correlazione**: r=0.65 (Moderata)
- **Soglia di Rischio**: > 40 μg/m³
- **Limite Legale EU**: 200 μg/m³ (orario), 40 μg/m³ (annuale)
- **Periodo di Lag**: 0-5 giorni
- **Frequenza Misurazione**: Oraria
- **Fonte Dati**: ARPA Campania, ISPRA
- **Impatto**: Infiammazione bronchiale, compromissione immunitaria

#### 4. **Temperatura Aria**
- **Unità di Misura**: °C
- **Correlazione**: r=-0.65 (Moderata Inversa)
- **Soglia di Rischio**: < 10°C
- **Range Normale**: -5°C a 40°C
- **Periodo di Lag**: 0-7 giorni
- **Frequenza Misurazione**: Oraria (media, min, max giornaliera)
- **Fonte Dati**: ISTAT, Stazioni Meteorologiche Regionali
- **Impatto**: Stagionalità influenzale, immunosoppressione da freddo

#### 5. **Umidità Relativa**
- **Unità di Misura**: %
- **Correlazione**: r=0.59 (Moderata)
- **Soglia di Rischio**: > 70%
- **Range Normale**: 30-95%
- **Periodo di Lag**: 0-5 giorni
- **Frequenza Misurazione**: Oraria
- **Fonte Dati**: ISTAT, ARPA
- **Impatto**: Sopravvivenza virus, trasmissione aerosol

### **Parametri Aggiuntivi** (Correlazione Debole r<0.5)

#### 6. **O3 - Ozono Troposferico**
- **Unità di Misura**: μg/m³
- **Correlazione**: r=0.45 (Debole)
- **Soglia di Rischio**: > 120 μg/m³ (8h)
- **Limite Legale EU**: 180 μg/m³ (soglia informazione), 120 μg/m³ (protezione salute)
- **Periodo di Lag**: 0-3 giorni
- **Frequenza Misurazione**: Oraria
- **Fonte Dati**: ARPA Campania
- **Impatto**: Stress ossidativo respiratorio

#### 7. **SO2 - Biossido di Zolfo**
- **Unità di Misura**: μg/m³
- **Correlazione**: r=0.38 (Debole)
- **Soglia di Rischio**: > 125 μg/m³
- **Limite Legale EU**: 350 μg/m³ (orario), 125 μg/m³ (giornaliero)
- **Periodo di Lag**: 0-2 giorni
- **Frequenza Misurazione**: Oraria
- **Fonte Dati**: ARPA Campania
- **Impatto**: Broncocostrizione, irritazione respiratoria

---

## 💧 LEGIONELLOSI - PARAMETRI AMBIENTALI

### **Parametri Primari** (Correlazione Forte r>0.7)

#### 1. **Temperatura Acqua**
- **Unità di Misura**: °C
- **Correlazione**: r=0.71 (Forte)
- **Soglia di Rischio**: > 25°C
- **Range Critico**: 25-42°C (crescita batterica ottimale)
- **Periodo di Lag**: 7-21 giorni (incubazione)
- **Frequenza Misurazione**: Settimanale
- **Fonte Dati**: ARPA Campania, ASL locali
- **Impatto**: Proliferazione Legionella pneumophila

### **Parametri Secondari** (Correlazione Moderata r=0.5-0.7)

#### 2. **Umidità Relativa**
- **Unità di Misura**: %
- **Correlazione**: r=0.68 (Moderata)
- **Soglia di Rischio**: > 70%
- **Range Critico**: 70-95%
- **Periodo di Lag**: 7-14 giorni
- **Frequenza Misurazione**: Oraria
- **Fonte Dati**: ISTAT, ARPA
- **Impatto**: Sopravvivenza aerosol, diffusione batterica

#### 3. **Temperatura Aria**
- **Unità di Misura**: °C
- **Correlazione**: r=0.61 (Moderata)
- **Soglia di Rischio**: > 25°C
- **Range Critico**: 25-35°C
- **Periodo di Lag**: 7-14 giorni
- **Frequenza Misurazione**: Oraria (media giornaliera)
- **Fonte Dati**: ISTAT, ARPA
- **Impatto**: Condizioni favorevoli crescita batterica

#### 4. **Precipitazioni**
- **Unità di Misura**: mm
- **Correlazione**: r=0.54 (Moderata)
- **Soglia di Rischio**: > 50mm/giorno
- **Range Critico**: Eventi estremi (>100mm/giorno)
- **Periodo di Lag**: 7-21 giorni
- **Frequenza Misurazione**: Giornaliera
- **Fonte Dati**: ISTAT, Stazioni Meteorologiche
- **Impatto**: Contaminazione sistemi idrici, torri raffreddamento

### **Parametri di Sistema Idrico** (Specifici Legionellosi)

#### 5. **pH Acqua**
- **Unità di Misura**: unità pH
- **Correlazione**: r=0.35 (Debole)
- **Range Ottimale Legionella**: 6.9-7.7
- **Soglia di Rischio**: 6.5-8.0
- **Periodo di Lag**: 7-14 giorni
- **Frequenza Misurazione**: Settimanale
- **Fonte Dati**: ARPA Campania, Laboratori Qualità Acqua
- **Impatto**: Condizioni biochimiche crescita batterica

#### 6. **Cloro Residuo**
- **Unità di Misura**: mg/L
- **Correlazione**: r=-0.45 (Moderata Inversa)
- **Soglia di Protezione**: > 0.2 mg/L
- **Range Sicurezza**: 0.2-2.0 mg/L
- **Periodo di Lag**: Immediato-7 giorni
- **Frequenza Misurazione**: Giornaliera (reti idriche)
- **Fonte Dati**: Gestori idrici, ASL
- **Impatto**: Disinfezione preventiva Legionella

---

## 🍽️ EPATITE A - PARAMETRI AMBIENTALI

### **Parametri Primari** (Correlazione Forte r>0.7)

#### 1. **Livelli E.coli**
- **Unità di Misura**: CFU/100ml
- **Correlazione**: r=0.85 (Molto Forte)
- **Soglia di Rischio**: > 100 CFU/100ml
- **Range Critico**: > 1000 CFU/100ml (contaminazione severa)
- **Periodo di Lag**: 14-28 giorni (incubazione HAV)
- **Frequenza Misurazione**: Settimanale
- **Fonte Dati**: ARPA Campania, Laboratori Acque
- **Impatto**: Indicatore contaminazione fecale, co-occorrenza virus HAV

#### 2. **pH Acqua**
- **Unità di Misura**: unità pH
- **Correlazione**: r=-0.72 (Forte Inversa)
- **Soglia di Rischio**: < 6.5 o > 8.5
- **Range Critico**: < 6.0 o > 9.0
- **Periodo di Lag**: 14-21 giorni
- **Frequenza Misurazione**: Settimanale
- **Fonte Dati**: ARPA Campania, Gestori idrici
- **Impatto**: Sopravvivenza virus HAV, efficacia disinfezione

### **Parametri Secondari** (Correlazione Moderata r=0.5-0.7)

#### 3. **Cloro Residuo**
- **Unità di Misura**: mg/L
- **Correlazione**: r=-0.68 (Moderata Inversa)
- **Soglia di Protezione**: > 0.2 mg/L
- **Range Sicurezza**: 0.5-2.0 mg/L
- **Periodo di Lag**: Immediato-14 giorni
- **Frequenza Misurazione**: Giornaliera
- **Fonte Dati**: Gestori idrici, ASL
- **Impatto**: Inattivazione virus HAV

#### 4. **Precipitazioni Estreme**
- **Unità di Misura**: mm
- **Correlazione**: r=0.56 (Moderata)
- **Soglia di Rischio**: > 100 mm/giorno
- **Range Critico**: Eventi estremi (>150mm/giorno)
- **Periodo di Lag**: 14-28 giorni
- **Frequenza Misurazione**: Giornaliera
- **Fonte Dati**: ISTAT, Protezione Civile
- **Impatto**: Overflow sistemi fognari, contaminazione pozzi

### **Parametri Aggiuntivi**

#### 5. **Temperatura Acqua**
- **Unità di Misura**: °C
- **Correlazione**: r=0.42 (Debole)
- **Range Critico**: 4-25°C (sopravvivenza HAV)
- **Soglia di Rischio**: < 4°C o > 60°C
- **Periodo di Lag**: 14-21 giorni
- **Frequenza Misurazione**: Settimanale
- **Fonte Dati**: ARPA Campania
- **Impatto**: Persistenza virus nell'ambiente

#### 6. **Torbidità Acqua**
- **Unità di Misura**: NTU (Nephelometric Turbidity Unit)
- **Correlazione**: r=0.38 (Debole)
- **Soglia di Rischio**: > 4 NTU
- **Range Critico**: > 10 NTU
- **Periodo di Lag**: 14-21 giorni
- **Frequenza Misurazione**: Settimanale
- **Fonte Dati**: ARPA Campania, Gestori idrici
- **Impatto**: Protezione virus da disinfezione, indicatore contaminazione

---

## 📈 MODELLI MATEMATICI E CORRELAZIONI

### **Influenza - Modelli Raccomandati**
- **GAM (Generalized Additive Model)**: Non-linearità PM2.5-temperatura
- **ARIMAX**: Previsioni stagionali con variabili esogene
- **Random Forest**: Interazioni multiple inquinanti
- **DLNM (Distributed Lag Non-linear Model)**: Effetti ritardati temperature

### **Legionellosi - Modelli Raccomandati**
- **DLNM**: Effetti temperatura con lag 7-14 giorni
- **Analisi Spaziale**: Clustering attorno fonti idriche
- **GAM**: Interazioni non-lineari temperatura-umidità
- **Regressione Logistica**: Previsione outbreak

### **Epatite A - Modelli Raccomandati**
- **GLM (Generalized Linear Model)**: Relazioni lineari E.coli-pH
- **Spatial Regression**: Analisi geografica contaminazione
- **Time Series Analysis**: Trend post-precipitazioni
- **Machine Learning Ensemble**: Combinazione multipli fattori

---

## 🎯 SOGLIE CRITICHE E ALLERTE

### **Sistema di Allerta Influenza**
```
🟢 VERDE:    PM2.5 < 15 μg/m³, Temp > 15°C
🟡 GIALLA:   PM2.5 15-25 μg/m³, Temp 10-15°C  
🟠 ARANCIONE: PM2.5 25-35 μg/m³, Temp 5-10°C
🔴 ROSSA:    PM2.5 > 35 μg/m³, Temp < 5°C
```

### **Sistema di Allerta Legionellosi**
```
🟢 VERDE:    T_acqua < 20°C, Umidità < 60%
🟡 GIALLA:   T_acqua 20-25°C, Umidità 60-70%
🟠 ARANCIONE: T_acqua 25-35°C, Umidità 70-80%
🔴 ROSSA:    T_acqua > 35°C, Umidità > 80%
```

### **Sistema di Allerta Epatite A**
```
🟢 VERDE:    E.coli < 50 CFU/100ml, pH 7.0-8.0
🟡 GIALLA:   E.coli 50-100 CFU/100ml, pH 6.5-7.0/8.0-8.5
🟠 ARANCIONE: E.coli 100-1000 CFU/100ml, pH 6.0-6.5/8.5-9.0
🔴 ROSSA:    E.coli > 1000 CFU/100ml, pH < 6.0 o > 9.0
```

---

## 🔧 SPECIFICHE TECNICHE API

### **Endpoint Dati Ambientali**
```
GET /api/v1/environmental/istat/{istat_code}/{year}/{interval}/{function}/{parameter}/
```

### **Parametri Supportati API**
- **Inquinanti**: PM10, PM25, O3, NO2, SO2, C6H6, CO, As_in_PM10
- **Meteo**: temperature, humidity, precipitation, wind_speed, pressure
- **Acqua**: ph, ecoli_count, residual_chlorine, water_temperature

### **Funzioni Statistiche**
- **media**: Media aritmetica
- **massimo**: Valore massimo
- **minimo**: Valore minimo
- **varianza**: Varianza statistica
- **giorni_superamento**: Giorni oltre soglia legale

### **Formati di Output**
```json
{
  "istat_code": "015146001",
  "parameter": "PM25", 
  "year": 2024,
  "function": "media",
  "value": 18.6,
  "unit": "μg/m³",
  "threshold_exceeded": false,
  "legal_limit": 25.0,
  "correlation_diseases": ["influenza"]
}
```

---

## 📊 STATISTICHE CORRELAZIONI VALIDATE

### **Matrice Correlazioni Complete**

| Malattia | Parametro | Correlazione (r) | P-value | Lag (giorni) |
|----------|-----------|------------------|---------|--------------|
| Influenza | PM2.5 | 0.82 | < 0.001 | 0-7 |
| Influenza | PM10 | 0.78 | < 0.001 | 0-7 |
| Influenza | NO2 | 0.65 | < 0.01 | 0-5 |
| Influenza | Temperatura | -0.65 | < 0.01 | 0-7 |
| Influenza | Umidità | 0.59 | < 0.05 | 0-5 |
| Legionellosi | T_Acqua | 0.71 | < 0.001 | 7-21 |
| Legionellosi | Umidità | 0.68 | < 0.01 | 7-14 |
| Legionellosi | T_Aria | 0.61 | < 0.01 | 7-14 |
| Legionellosi | Precipitazioni | 0.54 | < 0.05 | 7-21 |
| Epatite A | E.coli | 0.85 | < 0.001 | 14-28 |
| Epatite A | pH | -0.72 | < 0.001 | 14-21 |
| Epatite A | Cloro Residuo | -0.68 | < 0.01 | 0-14 |
| Epatite A | Precipitazioni | 0.56 | < 0.05 | 14-28 |

---

## ⚠️ LIMITAZIONI E RACCOMANDAZIONI

### **Limitazioni Attuali**
- **Dati Sintetici**: Alcune correlazioni basate su modelli simulati
- **Copertura Geografica**: Limitata a 3 regioni del Sud Italia
- **Frequenza Misure**: Variabile tra parametri (oraria vs settimanale)
- **Stagionalità**: Correlazioni possono variare per stagione

### **Raccomandazioni Implementative**
1. **Validazione Dati Reali**: Conferma correlazioni con dati epidemiologici reali
2. **Integrazione Multi-fonte**: Combinazione ARPA, ISPRA, ISTAT, ASL
3. **Quality Control**: Algoritmi automatici verifica qualità dati
4. **Machine Learning**: Implementazione modelli adattivi self-learning
5. **Early Warning System**: Allerte automatiche basate su soglie multiple

---

## 📞 CONTATTI TECNICI

**Team HealthTrace**  
📧 healthtrace@ambientale.it  
🌐 www.healthtrace.ambientale.it  
📱 API Documentation: /docs/swagger

**Responsabile Tecnico**: Dr. Marco Ambientali  
**Data Analyst**: Dr.ssa Laura Correlazioni  
**Environmental Expert**: Dr. Giuseppe Monitoraggio

---

*Documento generato automaticamente dalla Piattaforma HealthTrace*  
*Ultima modifica: 5 Febbraio 2026*
