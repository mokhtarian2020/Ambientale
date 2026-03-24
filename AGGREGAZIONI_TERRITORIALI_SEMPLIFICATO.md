# Aggregazioni Territoriali - Versione Semplificata

## ❌ TESTO ORIGINALE DA SOSTITUIRE:

```
Aggregazioni Territoriali 

Le aggregazioni sono calcolate tramite: 

GROUP BY ASL 

GROUP BY Provincia 

GROUP BY Regione 

Regole: 

media ponderata per popolazione per risk_score 

conteggio comuni per risk_level 

hotspot count per area 

Il sistema mantiene: 

livello comunale come base 

livelli superiori come viste materializzate o query dinamiche
```

---

## ✅ NUOVO TESTO SEMPLIFICATO:

### **Aggregazioni Territoriali**

Il sistema organizza i dati sanitari su diversi livelli amministrativi:

**Livelli di Raggruppamento:**
- **ASL**: Raggruppamento per Azienda Sanitaria Locale
- **Provincia**: Raggruppamento per provincia amministrativa  
- **Regione**: Raggruppamento per regione

**Calcoli Automatici:**
- **Rischio medio**: Calcolato considerando la popolazione di ogni comune
- **Distribuzione geografica**: Conteggio comuni per livello di rischio (ALTO/MEDIO/BASSO)
- **Focolai attivi**: Numero di zone con concentrazione di casi per territorio

**Struttura del Sistema:**
- **Base**: Tutti i dati sono registrati a livello comunale
- **Aggregazioni**: I livelli superiori sono calcolati automaticamente per le dashboard

---

## 📋 VERSIONI ALTERNATIVE:

### **Versione Ultra-Semplice:**
```
Aggregazioni Territoriali

Il sistema raggruppa automaticamente i dati sanitari per:
• ASL (Aziende Sanitarie)
• Province 
• Regioni

Calcola automaticamente:
• Livelli di rischio medi per popolazione
• Numero comuni coinvolti per rischio
• Focolai attivi per area geografica

Base dati: livello comunale con aggregazioni automatiche.
```

### **Versione Tecnica Semplificata:**
```
Aggregazioni Territoriali

Raggruppamenti automatici dei dati:
- Per ASL: somma casi e calcolo rischio medio per azienda sanitaria
- Per Provincia: aggregazione dati provinciali con peso popolazione
- Per Regione: sintesi regionale per pianificazione sanitaria

Metriche calcolate:
- Rischio ponderato per popolazione comunale
- Classificazione comuni per livello rischio
- Identificazione focolai geografici attivi

Architettura: dati comunali di base + viste aggregate per dashboard.
```

---

## 💡 RACCOMANDAZIONE:

**Usa la "Versione Ultra-Semplice"** perché:
- ✅ Elimina terminologia tecnica complessa
- ✅ Spiega chiaramente cosa fa il sistema
- ✅ Mantiene le informazioni essenziali
- ✅ È comprensibile per tutti gli stakeholder
- ✅ Evita riferimenti tecnici a database

---

## 📝 ISTRUZIONI PER zDashboard Design.docx:

1. **Trova** la sezione "Aggregazioni Territoriali"
2. **Sostituisci** tutto il testo con la "Versione Ultra-Semplice"  
3. **Salva** il documento
4. **Risultato**: Spiegazione chiara senza complessità tecnica

---

*Versione semplificata preparata per zDashboard Design.docx - Marzo 2026*
