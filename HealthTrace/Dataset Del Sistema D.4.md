1. **Studio dei dataset da importare ed integrare nel sistema**  
   
    
   
  Lo studio dei dataset da importare e integrare nel sistema rappresenta una fase fondamentale nella progettazione di qualsiasi architettura orientata ai dati. Prima ancora di definire strumenti, tecnologie o modelli di archiviazione, è necessario comprendere in modo approfondito la natura dei dati disponibili, la loro origine e il valore informativo che possono apportare al sistema. Un’analisi superficiale dei dataset rischia di compromettere l’intero processo di integrazione, generando inconsistenze, ridondanze o informazioni poco affidabili. Questa fase si colloca tra l’analisi dei requisiti informativi e la progettazione tecnica del sistema e costituisce un ponte tra le esigenze del business e la realtà dei dati effettivamente disponibili.  
2. **Identificazione delle fonti dati**  
   
    
   
  Il primo passo nello studio dei dataset consiste nell’identificazione delle fonti da cui i dati verranno estratti. Tali fonti possono essere interne all’organizzazione, come database storici o esterni, come servizi di terze parti, open data, API pubbliche o flussi provenienti da dispositivi IoT. Ogni fonte presenta caratteristiche specifiche in termini di struttura, formato, frequenza di aggiornamento e affidabilità.  
   
    
   
  È importante valutare non solo la disponibilità dei dati, ma anche la loro rilevanza rispetto agli obiettivi del sistema. Non tutti i dataset disponibili sono necessariamente utili, infatti in una fase preliminare, è stato possibile selezionare quelli che apportano un reale valore informativo e che possono essere integrati in modo efficace nel contesto complessivo.  
3. **Database Malattie Infettive**  
   
    
   
  La principale fonte dei dati sanitari è costituita da un database messo a disposizione dell’ASP di Cosenza e dall’ASL Napoli 1. I dati sono quelli che le Aziende Sanitarie usano per la gestione e la notifica obbligatoria delle malattie infettive. Il database raccoglie in forma strutturata le segnalazioni cliniche prodotte dai medici di base, dai reparti ospedalieri e dai servizi di igiene pubblica, in conformità con il sistema nazionale di sorveglianza delle malattie infettive (SIMI) e con le direttive del Ministero della Salute. Ogni segnalazione comprende informazioni anonimizzate del paziente, la diagnosi codificata secondo la nomenclatura ministeriale, le date clinicamente rilevanti (tra cui la data di insorgenza dei sintomi, la data di ricovero e la data di segnalazione) e la georeferenziazione del caso tramite codice ISTAT del comune di residenza e del comune di insorgenza dei sintomi. Il database costituisce la fonte istituzionale di riferimento per la sorveglianza epidemiologica a livello regionale e rappresenta il dataset primario del sistema HealthTrace.  
   
  **Utilizzo nel Progetto**  
   
    
   
  Nell'ambito del progetto, il database descritto fornisce i dati di incidenza di varie patologie infettive tra cui quelle target: Influenza, Legionellosi ed Epatite A. Tali dati costituiscono la variabile dipendente di tutti i modelli statistici e di machine learning implementati nel sistema per la stima della correlazione tra esposizione ambientale e insorgenza di malattia. Il periodo di osservazione disponibile copre l'arco temporale dalla prima metà del 2024 ai primi mesi del 2026, con una copertura geografica prevalentemente concentrata sulla Regione Campania, e in particolare sull'area metropolitana di Napoli e le province limitrofe.  
   
    
   
  Il campo geografico utilizzato per il matching con le fonti ambientali è il comune di insorgenza dei sintomi, in quanto rappresenta il luogo di probabile esposizione del paziente al momento dell'evento clinico. Questo approccio è epidemiologicamente più corretto rispetto all'utilizzo del comune di residenza, poiché una quota rilevante dei casi presenta i due comuni distinti: l'utilizzo del comune di residenza introdurrebbe un errore sistematico di classificazione geografica nel processo di associazione tra caso clinico e misurazioni ambientali.  
   
    
   
  Il campo temporale di riferimento è la data di insorgenza dei sintomi. Tale scelta è motivata dal fatto che il ritardo tra l'insorgenza clinica e la segnalazione formale è variabile e sistematicamente presente, rendendo la data di segnalazione un indicatore temporale non affidabile per la ricostruzione della finestra di esposizione ambientale. La data di insorgenza dei sintomi è invece direttamente collegata al periodo durante il quale il paziente è stato esposto ai fattori ambientali di rischio, ed è pertanto il riferimento corretto per l'applicazione dei modelli a ritardo distribuito (DLNM) previsti dal sistema, nei quali la finestra di esposizione si estende nei giorni precedenti l'evento clinico.  
4. **ARPAC. Rete di Monitoraggio della Qualità dell'Aria**  
   
    
   
  L'Agenzia Regionale per la Protezione dell'Ambiente della Campania (ARPA Campania) gestisce la rete regionale di monitoraggio della qualità dell'aria, istituita in conformità con la normativa europea e nazionale in materia di qualità dell'aria ambiente (Direttiva 2008/50/CE, D.Lgs. 155/2010). La rete è composta da stazioni fisse di rilevamento distribuite sul territorio regionale, ciascuna classificata per tipologia di zona di monitoraggio secondo lo standard dell'Agenzia Europea per l'Ambiente: stazioni di fondo, di traffico e industriali. I dati rilevati hanno cadenza oraria e coprono i principali inquinanti atmosferici normati: biossido di azoto, particolato fine, ozono, biossido di zolfo e monossido di carbonio. Le stazioni sono georeferenziate e associate al comune ISTAT di appartenenza, con informazioni sulla quota altimetrica e la tipologia che ne consentono la classificazione nel contesto urbano e periurbano.  
   
  **Utilizzo nel Progetto**  
   
    
   
  I dati ARPAC forniscono le variabili di esposizione atmosferica utilizzate nei modelli di correlazione con le patologie respiratorie target, in primo luogo l'Influenza e la Legionellosi. In letteratura scientifica è ampiamente documentato il ruolo degli inquinanti atmosferici, in particolare il particolato fine e il biossido di azoto, come fattori predisponenti e aggravanti delle infezioni respiratorie, attraverso meccanismi di compromissione delle difese mucociliari delle vie aeree e di aumento della suscettibilità individuale ai patogeni. I parametri acquisiti da ARPAC costituiscono le variabili indipendenti di esposizione atmosferica nei modelli GAM, DLNM, ARIMAX e Random Forest implementati nel sistema HealthTrace.  
   
    
   
  Per ciascun comune di interesse, il sistema interroga l'API ARPAC richiedendo i valori statistici aggregati su base mensile per tutte le stazioni presenti nel territorio comunale. Al fine di garantire la rappresentatività delle misurazioni rispetto alla popolazione esposta, vengono incluse esclusivamente le stazioni di tipologia urbana e di traffico, con esclusione delle stazioni industriali e di quelle posizionate ad altitudini superiori alla soglia definita per i contesti abitati. Nei casi in cui siano presenti più stazioni per lo stesso comune, i valori vengono aggregati tramite media pesata per distanza (Inverse Distance Weighting), attribuendo peso maggiore alle stazioni più prossime alla centroide del comune. I valori anomali e non validati sono esclusi dal calcolo tramite i meccanismi di validazione e filtraggio per range messi a disposizione dall'API.  
5. **MeteoHub. Rete Meteorologica della Protezione Civile**  
   
    
   
  MeteoHub è il sistema di raccolta e distribuzione dei dati meteorologici operato dalla rete di stazioni della Protezione Civile e reti associate attive sul territorio campano. La rete fornisce misurazioni in continuo di variabili meteorologiche fondamentali: temperatura dell'aria, precipitazioni cumulate, umidità relativa e velocità del vento, con una frequenza di acquisizione ad alta risoluzione temporale. Le stazioni sono distribuite sul territorio regionale e associate al comune ISTAT di appartenenza, consentendo il collegamento diretto con le fonti sanitarie del sistema. I dati meteorologici sono accessibili tramite un microservizio dedicato che espone sia le serie temporali grezze sia aggregazioni statistiche su finestre temporali configurabili.  
   
  **Utilizzo nel Progetto**  
   
    
   
  Le variabili meteorologiche acquisite da MeteoHub svolgono un ruolo modulante nei modelli epidemiologici del sistema HealthTrace. La temperatura e l'umidità influenzano direttamente la sopravvivenza e la diffusione dei patogeni nell'ambiente: la Legionella pneumophila prolifera in condizioni di temperatura dell'acqua comprese tra i venti e i quarantacinque gradi centigradi, mentre le variazioni stagionali di temperatura e umidità condizionano la trasmissione del virus influenzale. Le precipitazioni sono rilevanti come proxy del rischio di contaminazione idrica per l'Epatite A.  
   
    
   
  Per ciascun comune di interesse, il sistema acquisisce i valori statistici mensili aggregati per tutte le stazioni meteorologiche presenti nel territorio comunale. Al fine di garantire la rappresentatività delle misurazioni, vengono incluse esclusivamente le stazioni posizionate al di sotto della soglia altimetrica definita per i contesti abitati. Poiché i metadati originali delle stazioni MeteoHub non includono il dato altimetrico, tale informazione viene calcolata a partire dalle coordinate geografiche tramite integrazione con il servizio di modello digitale del terreno descritto nella fonte successiva. Come per ARPAC, in presenza di stazioni multiple per lo stesso comune viene applicata la media pesata per distanza per derivare un unico valore rappresentativo del territorio comunale. Le variabili meteorologiche costituiscono le variabili di confondimento e modulazione nei modelli di correlazione, permettendo di isolare il contributo specifico degli inquinanti atmosferici dall'effetto delle condizioni climatiche generali.  
6. **OpenTopoData SRTM. Modello Digitale del Terreno**  
   
    
   
  Il dataset SRTM (Shuttle Radar Topography Mission) è un modello digitale del terreno prodotto dalla NASA nell'ambito di una missione dello Space Shuttle nel febbraio del 2000, successivamente elaborato e distribuito dall'agenzia statunitense USGS (United States Geological Survey). Il dataset fornisce quote altimetriche a copertura quasi globale, compreso l'intero territorio italiano, con una risoluzione spaziale adeguata agli scopi del progetto. OpenTopoData è un servizio pubblico e gratuito che espone i dati SRTM tramite un'interfaccia di tipo REST, consentendo l'interrogazione puntuale della quota altimetrica a partire da coordinate geografiche. Il servizio supporta richieste in modalità batch per l'elaborazione simultanea di coordinate multiple.  
   
  **Utilizzo nel Progetto**  
   
    
   
  L'integrazione di questa fonte è motivata dalla necessità di disporre del dato altimetrico per tutte le stazioni meteorologiche MeteoHub, i cui metadati originali non includono tale informazione. La quota altimetrica è indispensabile per il processo di selezione delle stazioni: l'analisi di correlazione ambientale-sanitaria richiede che le misurazioni siano rappresentative delle condizioni di esposizione della popolazione insediata, pertanto le stazioni posizionate in aree montane o in contesti non abitati devono essere escluse dall'aggregazione.  
   
    
   
  Il processo di integrazione si articola in un'unica fase di censimento, eseguita all'avvio del sistema o all'aggiunta di nuove stazioni: per ciascuna stazione MeteoHub vengono inviate le coordinate geografiche al servizio in modalità batch, e il valore di quota restituito viene memorizzato in modo permanente nel registro delle stazioni. Una volta completato il censimento, il sistema non necessita di ulteriori interrogazioni esterne per il dato altimetrico, garantendo piena autonomia operativa durante il normale funzionamento. Le stazioni con quota superiore alla soglia definita vengono marcate come non idonee e automaticamente escluse da tutte le interrogazioni successive.  
7. **ISTAT. Codici Amministrativi di Riferimento**  
   
    
   
  L'Istituto Nazionale di Statistica (ISTAT) è l'ente pubblico italiano responsabile della produzione e della diffusione dell'informazione statistica ufficiale. Tra i sistemi di riferimento gestiti dall'ISTAT figura la codifica geografica amministrativa del territorio italiano, che assegna a ciascuna unità amministrativa — comune, provincia e regione — un codice numerico univoco, aggiornato in occasione di variazioni territoriali e riforme amministrative. Il codice ISTAT comunale è strutturato gerarchicamente: le prime due cifre identificano la regione, le prime tre identificano la provincia, e il codice completo identifica il singolo comune. Questo sistema è adottato in modo uniforme da tutti i sistemi informativi della pubblica amministrazione italiana, rendendolo lo standard de facto per l'interoperabilità tra basi di dati di provenienza istituzionale diversa.  
   
  **Utilizzo nel Progetto**  
   
    
   
  Il codice ISTAT comunale costituisce la chiave di integrazione universale del sistema HealthTrace. Esso è presente in forma coerente in tutte le fonti dati del sistema: nel database sanitario GESAN come attributo geografico di ciascuna segnalazione clinica, e nelle API ambientali ARPAC e MeteoHub come attributo di ciascuna stazione di rilevamento. Questa uniformità elimina la necessità di operazioni di geocoding o di inferenza geografica nel processo di integrazione, consentendo un collegamento diretto e deterministico tra i dati sanitari e i dati ambientali riferiti allo stesso territorio.  
   
    
   
  Il livello comunale rappresenta la granularità minima di analisi del sistema. La struttura gerarchica del codice consente di condurre analisi aggregate a livello provinciale e regionale per derivazione diretta, senza necessità di tabelle di corrispondenza aggiuntive. Questa flessibilità è particolarmente rilevante per le analisi di epidemiologia spaziale e per i modelli di autocorrelazione geografica implementati nel sistema, quali l'indice di Moran e la statistica Getis-Ord Gi*.  
8. **Analisi della struttura e del contenuto dei dataset**  
   
    
   
  Una volta individuate le fonti, è necessario analizzare in dettaglio la struttura dei dataset. Questa analisi riguarda il formato dei dati, che può essere strutturato, semi-strutturato o non strutturato, e il modo in cui le informazioni sono organizzate. Ad esempio, un database relazionale presenta schemi e vincoli ben definiti, mentre file JSON o XML possono avere strutture più flessibili e variabili. Oltre alla struttura, è fondamentale esaminare il contenuto dei dati. Ciò include il significato dei campi, i tipi di dato utilizzati, le unità di misura e le possibili relazioni tra le informazioni. Questa fase consente di individuare eventuali ambiguità semantiche e di chiarire il reale significato dei dati, evitando interpretazioni errate durante le fasi successive di integrazione e analisi.  
9. **Valutazione della qualità dei dati**  
   
    
   
  Un aspetto centrale nello studio dei dataset è la valutazione della qualità dei dati. I dati possono presentare problemi di incompletezza, incoerenza, duplicazione o obsolescenza, soprattutto quando provengono da sistemi diversi e non progettati per l’integrazione. Identificare queste criticità in fase preliminare permette di pianificare adeguate strategie di pulizia e trasformazione.  
   
    
   
  La qualità dei dati influisce direttamente sull’affidabilità delle analisi e delle decisioni che verranno prese sulla base del sistema. Per questo motivo, lo studio dei dataset deve includere una valutazione della frequenza degli errori, della presenza di valori nulli e della coerenza logica delle informazioni, ponendo le basi per un processo di integrazione solido e controllato.  
10. **Integrazione e coerenza tra dataset eterogenei**  
   
    
   
  Uno degli obiettivi principali dello studio dei dataset è comprendere come i diversi insiemi di dati possano essere integrati tra loro. Dataset provenienti da fonti differenti possono utilizzare codifiche diverse, nomenclature non uniformi o criteri di classificazione differenti per rappresentare la stessa informazione. Senza un’analisi approfondita, queste differenze possono causare incongruenze difficili da risolvere in seguito. Lo studio preliminare consente di individuare chiavi di integrazione, relazioni logiche e corrispondenze semantiche tra i dataset. In questo modo è possibile definire regole di armonizzazione che rendano i dati coerenti e confrontabili all’interno del sistema integrato, migliorando la qualità complessiva dell’informazione.  
11. **Aspetti temporali e aggiornamento dei dati**  
   
    
   
  Un ulteriore elemento da considerare riguarda la dimensione temporale dei dataset. Alcuni dati vengono aggiornati in tempo reale, altri con frequenza giornaliera, settimanale o ancora più sporadica. Comprendere queste dinamiche è essenziale per progettare correttamente i processi di ingestion e integrazione. Lo studio dei dataset deve quindi analizzare la disponibilità storica dei dati, la profondità temporale necessaria per le analisi e le modalità di gestione delle variazioni nel tempo. Questo aspetto è particolarmente rilevante nei sistemi di analisi, dove la storicizzazione delle informazioni consente di osservare trend, evoluzioni e comportamenti nel lungo periodo.  
12. **Implicazioni per la progettazione del sistema**  
   
    
   
  I risultati dello studio dei dataset influenzano direttamente le scelte progettuali del sistema. La tipologia dei dati, la loro qualità e il grado di integrazione richiesto determinano le tecnologie da adottare, i modelli di dati da utilizzare e le strategie di trasformazione da implementare. Un’analisi accurata riduce il rischio di modifiche strutturali in fase avanzata del progetto, con conseguente risparmio di tempo e risorse. Inoltre, lo studio dei dataset favorisce una maggiore consapevolezza del patrimonio informativo dell’organizzazione, consentendo di valorizzare al meglio i dati disponibili e di individuare eventuali lacune informative da colmare in futuro.  
13. **Data Source Catalog**  
   
    
   
  Questa fase si traduce nella creazione di un **Data Source Catalog** che definisce i contratti di integrazione per ciascuna fonte esterna, garantendo che l'acquisizione dei dati ambientali sia focalizzata esclusivamente sui fattori di rischio epidemiologicamente rilevanti e tecnicamente omogenei.  
14. **Imposizione di Granularità Temporale Standardizzata**  
   
    
   
  La correlazione tra un evento clinico discreto (la diagnosi) e i precursori ambientali richiede una risoluzione temporale ad alta fedeltà. Viene imposto uno standard di **granularità oraria o sub-giornaliera** per i dati ad alta frequenza (inquinanti atmosferici, temperatura, umidità). Tale allineamento temporale è condizione necessaria per la ricostruzione precisa della finestra di esposizione del paziente nei giorni precedenti la segnalazione, permettendo l'applicazione corretta dei modelli    **DLNM (Distributed Lag Non-linear Models)**.  
15. **Architettura del Filtraggio Geospaziale e Allineamento Spaziale**  
   
    
   
  Tutte le misurazioni acquisite devono essere rigorosamente georeferenziate per consentire il mapping tra le stazioni di rilevamento e i poligoni amministrativi (Comune, Provincia) della dimensione Dim_Location. Il sistema implementa un Modello di Filtro Geometrico avanzato basato su tre modalità mutuamente esclusive, processate secondo una gerarchia di priorità predefinita:  
- **GeoJSON (Priorità 1):** Definizione di geometrie complesse (*Polygon*,    *MultiPolygon*) per ritagli spaziali di precisione.  
- **WKT - Well-Known Text (Priorità 2):** Utilizzo di stringhe standardizzate (es. POLYGON((...))) per l'interoperabilità con sistemi GIS.  
- **BBOX - Bounding Box (Priorità 3):** Definizione di un rettangolo inviluppo tramite coordinate [minLon, minLat, maxLon, maxLat].  
   
    
   
  Il sistema opera di default su standard **EPSG:4326 (WGS84)**, consentendo tuttavia la specifica di sistemi di riferimento alternativi tramite il parametro epsg. Qualora non venga fornito alcun filtro geometrico, la query estende l'acquisizione all'intero dominio spaziale disponibile.  
1. **Logica di Combinazione dei Filtri e Normalizzazione Semantica**  
   
    
   
  Per garantire l'integrità del dato nel Data Warehouse, l'acquisizione segue regole booleane rigorose:  
- **Logica AND (Identificazione Stazione):** I parametri identificativi (station_id, station_name, istat_code) e il filtro geometrico agiscono in intersezione. Una stazione viene inclusa solo se soddisfa simultaneamente tutti i criteri; incongruenze (es. un istat_code non corrispondente alla posizione della stazione) determinano una risposta vuota per prevenire l'ingestione di dati spazialmente errati.  
- **Logica OR (Selezione Sensori):** All'interno della stazione identificata, la selezione dei parametri fisici avviene in unione. L'utilizzo di parameter (es. NO2, PM2.5), alias o sensor_id amplia la selezione, garantendo la massima flessibilità nel recupero di diverse metriche ambientali per lo stesso punto di osservazione.  
   
    
   
  Queste logiche permettono un filtraggio logico e non solo geografico delle informazioni raccolte dalle sorgenti dati.  
1. **Normalizzazione e Risoluzione Incongruenze**  
   
    
   
  È progettata una fase di pre-trasformazione obbligatoria per uniformare i flussi in ingresso:  
- **Unità di Misura:** Conversione forzata verso set standardizzati (es. concentrazioni di particolato espresse esclusivamente in    **µg/m³**).  
- **Codifiche e Vocabolari:** Mappatura biunivoca dei codici inquinanti originali (es. codifica ARPA o sensori IoT) verso il codice interno standardizzato del DWH (   **Pollutant_BK**), risolvendo ogni ambiguità semantica tra fonti eterogenee.  
1. **Data Source Catalog**  
   
    
   
  Nel progetto tutti i dati acquisiti assumono una rilevanza strategica, in particolare:  
- **Dati Atmosferici (Aria):** Si focalizza su    **PM10, O3, NO2** e altri inquinanti, acquisiti via API (ove disponibili) da reti di monitoraggio. Questi dati sono predittori noti per l'acutizzazione di patologie respiratorie (es. Influenza).  
- **Dati Idrici:** Si acquisiscono i parametri rilevanti per le patologie a trasmissione idrica, in particolare i valori di    **E. coli, pH, e la Temperatura dell'acqua**. Quest'ultima è un fattore critico per la proliferazione della Legionella.  
- **Dati Climatici:** Dati meteorologici (Temperatura, Precipitazioni, Umidità) sono fondamentali come variabili modulanti e vengono acquisiti in serie storiche per modellare l'influenza del clima sui cicli di vita dei patogeni.  
   
    
   
  Di seguito si riportano i dati facenti parte del Data Catalog di progetto in maniera puntuale per fornire una panoramica sul patrimonio informativo gestito dal sistema.  
1. **Data Catalog: Database Malattie Infettive**  
   
    
   
  Il Data Catolg per la parte di segnalazione sanitaria è costituito da:  
- **Sezione Segnalazione (Dati di Protocollo)**  
- **Malattia infettiva:** Identificativo della patologia oggetto della segnalazione (codificato secondo standard ICD-9/10/11).  
- **UOSD di diagnosi:** Unità Operativa Semplice Dipartimentale che ha emesso la diagnosi.  
- **Data Segnalazione:** Data formale in cui il medico inserisce la notifica nel sistema.  
- **Dati Medico (Nome, Cognome, Contatti):** Informazioni identificative e di reperibilità del medico segnalatore (MMG/PLS o specialista).  
- **Sezione Anagrafica (Paziente)**  
- **Codice Fiscale/STP/ENI:** Identificativo univoco del soggetto (inclusi codici per stranieri temporaneamente presenti o europei non iscritti).  
- **Dati Personali (Nome, Cognome, Sesso, Data Nascita):** Informazioni anagrafiche di base per l'identificazione certa del paziente.  
- **Luogo di Nascita (Provincia, Comune):** Dati geografici di nascita per il calcolo statistico e demografico.  
- **Professione:** Attività lavorativa del soggetto (cruciale per identificare cluster professionali o rischi specifici).  
- **Contatti (Email, Telefono):** Recapiti per le attività di tracciamento e indagine epidemiologica.  
- **Sezione Residenza e Domicilio**  
- **Geolocalizzazione Residenza (Provincia, Comune, Indirizzo):** Ubicazione legale del soggetto per l'attribuzione della competenza territoriale ASL.  
- **Geolocalizzazione Domicilio:** Luogo di effettiva dimora del soggetto, se differente dalla residenza, fondamentale per il monitoraggio dei focolai locali.  
- **Sezione Segnalazione Informazioni (Dati Clinici ed Epidemiologici)**  
- **Data Inizio Sintomi:** Parametro temporale critico per il calcolo del periodo di incubazione e la stima del tempo di esposizione.  
- **Luogo Inizio Sintomi (Provincia, Comune):** Identifica l'area geografica in cui si è manifestata la patologia (spesso coincide con il sito di esposizione).  
- **Ricovero in luogo di cura:** Indicatore booleano o selettore della struttura sanitaria in caso di ospedalizzazione.  
- **Stato Vaccinale (Vaccino, Numero Dosi, Data ultima dose, Tipo):** Informazioni sullo storico vaccinale del paziente relativo alla patologia segnalata per valutare l'efficacia vaccinale (Breakthrough infections).  
   
    
   
  Si precisa che il data catalog presentato è solo relativo alla segnalazione e che per semplicità di notazione e documentazione si omette il data catalog relativo alle schede di tutte le singole patologie contenente i dati di dettaglio di maggiore importanza. Per completezza rispetto al caso di studio si riporta invece il data catalog dell’influenza, Legionellosi ed Epatite A.  
   
  **Data Catalog Influenza**  
   
    
   
  Il Data Catalog per Influenza definisce la struttura dei dati estratti dalla specifica SCHEDA PATOLOGIA “Influenza” nell’interfaccia di HealthTrace. I campi rilevanti includono: identificativo della patologia oggetto della segnalazione; data di inizio sintomi (variabile temporale di ancoraggio per la ricostruzione della finestra di esposizione ambientale); la data formale di segnalazione è acquisita ma non utilizzata nei modelli analitici, in quanto affetta da un ritardo sistematico variabile rispetto all'evento clinico; luogo di inizio sintomi (Provincia e Comune) utilizzato per l’allineamento geografico con le esposizioni ambientali; indicatore di ricovero in luogo di cura (se presente) e stato vaccinale (tipo vaccino, numero di dosi e data dell’ultima dose) per eventuali stratificazioni. Tali informazioni vengono normalizzate e trasformate nella variabile di outcome (conteggio dei casi di Influenza per Comune e periodo), pronta per la join con le serie ambientali aggregate a livello di comune e data. Il periodo epidemiologico si ancora alla data di insorgenza dei sintomi, con una finestra di esposizione ambientale di 7 giorni precedenti (coerente con il lag implementato nel modello DLNM per Influenza e con i campi exposure_* persistiti nel database per ciascun caso).  
   
  **Utilizzo nel Progetto**  
   
    
   
  Nella seguente tabella vengono riportati macroscopicamente i dati raccolti (specificamente dettagliati e rappresentati nel documento relativo alla progettazione del DB e del data model di piattaforma) per tipo/entità e rilevanza per le analisi. Questo permette di definirne in maniera puntuale anche l’utilizzo che ne è stato fatto nel progetto oltre a quanto richiesto dalla comune pratica clinica stabilita con l’azienda sanitaria coinvolta.  
   
    
   
| | | |
|-|-|-|
| **Area/Evento** | **Campi Dati Rilevanti** | **Rilevanza Analitica AI** |
| **Timeline** | Data insorgenza sintomi | Variabile temporale di ancoraggio del DLNM per Influenza (finestra di esposizione: 7 giorni precedenti l'insorgenza, campi exposure_pm25…exposure_humidity). Insieme a istat_code, costituisce la chiave spazio-temporale per la join con le esposizioni ambientali aggregate nei modelli MLR, GAM e ARIMAX. |
|   | Data Ricovero / Ospedale | Campi hospitalized / icu_admission persistiti nel sistema a supporto dell'indagine epidemiologica; non sono attualmente input dei modelli AI implementati, il cui output è l'incidenza aggregata case_count per comune. |
| **Comorbilità** | Presenza Patologie Croniche | Campo chronic_diseases (JSON) persistito nel sistema; non è attualmente input dei modelli predittivi, il cui vettore di feature è composto esclusivamente da variabili di esposizione ambientale (pm25, pm10, no2, ozone, temperature_avg, humidity, rainy_days). |
|   | Dettaglio Comorbilità | Dettaglio del campo chronic_diseases (es. Diabete, Malattie Cardiovascolari, Renali, Obesità/BMI); disponibile nel sistema a fini descrittivi, non è attualmente una feature dei modelli AI implementati. |
| **Dati Laboratorio** | Tipizzazione Virus | I sottotipi virali (A/H1N1v, A/H3N2, Influenza B) sono persistiti nel campo subtype; i modelli correnti aggregano case_count senza stratificazione per sottotipo. Il campo potrà supportare futuri modelli specifici per ceppo circolante. |
|   | Esito Laboratorio | Il flag lab_confirmed (PCR/test molecolare positivo) è il filtro di qualità che determina l'inclusione del caso nel conteggio aggregato case_count, variabile dipendente di tutti i modelli AI del sistema (MLR, GAM, ARIMAX, DLNM, Random Forest); i casi non confermati non contribuiscono alla variabile di outcome. |
| **Complicanze** | SARI / ARDS / Radiografia | Campo severity (Lieve / Moderato / Grave) persistito nel sistema a supporto della sorveglianza epidemiologica; non è input dei modelli predittivi, il cui outcome è il conteggio aggregato di casi confermati per comune (case_count). |
|   | Polmonite Batterica/Mista | Informazione clinica persistita nel campo symptoms (JSON); non è attualmente un input dei modelli AI di HealthTrace. Potrà supportare in futuro analisi di stratificazione delle complicanze nei modelli di esito clinico individuale. |
| **Follow-up** | Esito (Guarigione/Decesso) | Campo outcome (Guarigione / Decesso / In corso) persistito nel sistema; la variabile dipendente dei modelli AI implementati è il conteggio aggregato case_count per comune e periodo, non l'esito individuale. Nessun modello di analisi della sopravvivenza è attualmente implementato. |
|   | Data Evento | Campo outcome_date persistito nel sistema come riferimento temporale conclusivo dell'episodio clinico; non è attualmente un input dei modelli AI implementati. |

Tutti i campi alfanumerici sensibili sono soggetti a cifratura automatica prima della persistenza nel database interno, garantendo la conformità GDPR durante le analisi massive.  
   
  **Data Catalog Legionellosi**  
   
    
   
  Il Data Catalog per Legionellosi definisce la struttura dei dati estratti dalla specifica SCHEDA PATOLOGIA “Legionellosi” nell’interfaccia di HealthTrace. I campi rilevanti includono: identificativo della patologia oggetto della segnalazione; data di inizio sintomi (variabile temporale di ancoraggio per la ricostruzione della finestra di esposizione ambientale); la data formale di segnalazione è acquisita ma non utilizzata nei modelli analitici, in quanto affetta da un ritardo sistematico variabile rispetto all'evento clinico; luogo di inizio sintomi (Provincia e Comune) utilizzato per l’allineamento geografico con le esposizioni ambientali; indicatore di ricovero in luogo di cura (se presente) e informazioni vaccinali laddove previste per eventuali stratificazioni. Tali informazioni vengono normalizzate e trasformate nella variabile di outcome (conteggio dei casi di Legionellosi per Comune e periodo), pronta per la join con le serie ambientali aggregate a livello di comune e data.  
   
  **Utilizzo nel Progetto**  
   
    
   
  Nella seguente tabella vengono riportati macroscopicamente i dati raccolti (specificamente dettagliati e rappresentati nel documento relativo alla progettazione del DB e del data model di piattaforma) per tipo/entità e rilevanza per le analisi. Questo permette di definirne in maniera puntuale anche l’utilizzo che ne è stato fatto nel progetto oltre a quanto richiesto dalla comune pratica clinica stabilita con l’azienda sanitaria coinvolta.  
   
    
   
| | | |
|-|-|-|
| **Area/Evento** |   **Campi Dati Rilevanti** |   **Rilevanza Analitica AI** |
| **Profilo Ospite (Vulnerabilità)** | Codice Fiscale (pseudonimizzato), Età, Genere, Professione, Abitudini (Fumo/Alcol). | Calcolo dello score di rischio individuale e identificazione di fasce di popolazione suscettibili. |
| **Timeline Epidemiologica** | Data insorgenza sintomi, Data ricovero, Data notifica, Data test laboratorio. | Modellazione "lag-response" per stimare la velocità di diffusione e i tempi di incubazione del focolaio. |
| **Geolocalizzazione** | Comune/Indirizzo Residenza, Domicilio, Luoghi di soggiorno (ultime 2 settimane). | Analisi di prossimità e "Clustering" geografico per l'individuazione dell'origine del contagio (focolai ambientali). |
| **Quadro Clinico (Input AI)** | Febbre, Dispnea, Tosse, Segni Radiologici (Opacità/Versamento), Comorbilità croniche. | Addestramento di algoritmi di classificazione per prevedere la gravità dell'outcome clinico (Lieve vs Critico). |
| **Fattori Esposizione** | Frequentazione piscine, Uso condizionatori, Ricoveri precedenti, Cure odontoiatriche. | Correlazione statistica tra esposizione a matrici ambientali specifiche e insorgenza della patologia (es. Legionella). |
| **Validazione Eziologica** | Tipizzazione virus (es. AH3n2), Isolamento germe, Titoli sierologici, Carica virale. | Feature di etichettatura (Labeling) per la distinzione dei modelli predittivi in base al ceppo o sierogruppo specifico. |
| **Outcome e Follow-up** | Esito (Guarigione/Decesso), Presenza esiti permanenti, Complicanze (SARI/ARDS). | Variabile "Target" per modelli di analisi della sopravvivenza e valutazione dell'impatto sul sistema sanitario. |
| **Prevenzione** | Stato vaccinale (Stagione corrente), Nome vaccino, Numero dosi, Data ultima dose. | Analisi dell'efficacia vaccinale (Vaccine Effectiveness) e impatto sulle varianti circolanti. |

  **Data Catalog EPATITE A**  
   
    
   
  Il Data Catalog per Epatite A definisce la struttura dei dati estratti dalla specifica SCHEDA PATOLOGIA “Epatite A” nell’interfaccia di HealthTrace. I campi rilevanti includono: identificativo della patologia oggetto della segnalazione; data formale di segnalazione e data di inizio sintomi (variabili temporali per definire il periodo epidemiologico); luogo di inizio sintomi (Provincia e Comune) utilizzato per l’allineamento geografico con le esposizioni ambientali; indicatore di eventuale ricovero in luogo di cura (se presente) e informazioni cliniche/epidemiologiche previste dalla scheda per eventuali stratificazioni. Tali informazioni vengono normalizzate e trasformate nella variabile di outcome (conteggio dei casi di Epatite A per Comune e periodo), pronta per la join con le serie ambientali aggregate a livello di comune e data.  
   
  **Utilizzo nel Progetto**  
   
    
   
  Nella seguente tabella vengono riportati macroscopicamente i dati raccolti (specificamente dettagliati e rappresentati nel documento relativo alla progettazione del DB e del data model di piattaforma) per tipo/entità e rilevanza per le analisi. Questo permette di definirne in maniera puntuale anche l’utilizzo che ne è stato fatto nel progetto oltre a quanto richiesto dalla comune pratica clinica stabilita con l’azienda sanitaria coinvolta.  
   
    
   
| | | |
|-|-|-|
| **Area/Evento** |   **Campi Dati Rilevanti** |   **Rilevanza Analitica AI** |
| **Anamnesi Alimentare Specifica** | Consumo di: Frutti di mare (crudi/cotti), Frutta/Verdura non lavata, Carni, Latticini, Uova, Prodotti di gastronomia. | Feature binarie di esposizione alimentare per i modelli Random Forest/XGBoost; utilizzate per distinguere il vettore di trasmissione alimentare da quello idrico nell'ambito del modello complessivo di incidenza. |
| **Dettaglio Consumo (Audit)** | Marca prodotto, Luogo acquisto, Data preparazione, Tipologia di consumo (Crudo/Cotto/Ben cotto). | Campo di supporto all'indagine epidemiologica condotta dall'ASL; non costituisce attualmente un input diretto dei modelli ML di HealthTrace. Potrà essere impiegato in futuro per stratificare i conteggi di casi per probabile via di esposizione. |
| **Fattori di Rischio Comportamentali** | Viaggi all'estero, Contatti sessuali a rischio, Uso di droghe, Tatuaggi/Piercing, Interventi chirurgici o endoscopie recenti. | Modellazione dei vettori di trasmissione non alimentari per la distinzione dei cluster (Socio-behavioral clustering). |
| **Parametri Biochimici (Severity)** | Valori Enzimi: AST, ALT, Bilirubina totale/diretta, INR. Risultati: IgM anti-HAV, HCV-RNA, HBsAg. | Potenziali feature di stratificazione nei modelli MLR e Random Forest per distinguere casi gravi da lievi all'interno della variabile di outcome (conteggio casi); al di fuori del perimetro del modello attualmente in produzione. |
| **Indagine Ambientale e Idrica** | Consumo acqua (Sorgente, Pozzo, Acquedotto), Esposizione a siti contaminati, Contatto con animali (Domestici/Allevamento). | Integrazione con dati geospaziali per mappare rischi legati alla rete idrica o a zone di pesca specifiche (es. zona Varcaturo). |
| **Esposizione in Comunità** | Frequenza asili, Scuole, Mense, Partecipazione a eventi/banchetti collettivi. | Identificazione di cluster geografici ad alta incidenza tramite Local Moran's I (LISA) e Getis-Ord Gi* (Hot Spot / Cold Spot); le aree di potenziale esposizione collettiva vengono inferite dalla concentrazione spaziale dei casi per comune. |
| **Timeline Clinica Avanzata** | Durata sintomi, Comparsa ittero, Dolore toracico, Stato di disidratazione, Decorso clinico (Trapianto/Decesso). | Ricostruzione della curva epidemiologica tramite ARIMAX e DLNM (finestra di esposizione: 21 giorni precedenti l'insorgenza dei sintomi); la data di inizio sintomi è la variabile temporale di ancoraggio del modello a ritardo distribuito. |

1. **Data Catalog: ARPAC**  
   
    
   
  Il Data Catalog per ARPAC descrive la struttura dei dati di qualità dell’aria estratti dalla rete di monitoraggio ARPAC. Le chiamate avvengono tramite endpoint REST basati su POST, con supporto a filtri spaziali (bbox, wkt o geojson con EPSG), e filtri di identificazione delle stazioni (station_id, station_name e istat_code), combinati secondo regole AND/OR: la stazione deve soddisfare tutti i criteri AND, mentre l’insieme dei sensori viene selezionato in OR tramite parameter (es. NO2, PM2,5), alias o parameter_id. Nel flusso operativo vengono richieste statistiche aggregate tramite POST /arpac/data/arpac_data_stat usando stats=[min, mean, max] e, dove previsto, validated=true e filter_on_range=true per escludere valori fuori range. La risposta contiene, per ogni stazione slm (quota s.l.m.), coordinate (EPSG 4326), type (es. FONDO/TRAFFICO) e una lista di sensors con unità di misura e oggetto dati data={min, mean, max} per ogni parametro. I dati così ottenuti vengono normalizzati (unità e naming dei parametri) e preparati per l’integrazione con le esposizioni ambientali aggregate a livello di comune (istat_code).  
   
  **Utilizzo nel Progetto**  
   
    
   
  Nella seguente tabella vengono riportati i campi acquisiti dalla rete ARPAC, organizzati per categoria funzionale, con indicazione della loro rilevanza diretta nei modelli analitici del sistema HealthTrace. I dati ARPAC costituiscono le variabili di esposizione atmosferica per la correlazione con le patologie respiratorie target, in particolare Influenza e Legionellosi, e rappresentano l’input primario della pipeline di ingestione ambientale per la componente di qualità dell’aria.  
   
    
   
| | | |
|-|-|-|
| **Area/Categoria** |   **Campi Dati Rilevanti** |   **Rilevanza Analitica AI** |
| **Identificazione e Localizzazione Stazione** | station_id, station_name, istat_code, latitude, longitude (EPSG 4326) | Chiave di join con le segnalazioni sanitarie tramite istat_code; le coordinate sono utilizzate per il calcolo dei pesi IDW (Inverse Distance Weighting) e per i filtri spaziali GeoJSON/BBOX nella selezione delle stazioni rappresentative del comune. |
| **Classificazione e Quota Stazione** | type (FONDO / TRAFFICO / INDUSTRIALE), slm (quota s.l.m. in metri) | Filtro di idoneità stazione: vengono incluse esclusivamente le stazioni di tipo FONDO e TRAFFICO con quota inferiore alla soglia altimetrica definita. Le stazioni industriali sono sistematicamente escluse per evitare bias nei livelli di esposizione della popolazione residente. |
| **Inquinanti Atmosferici (Input Modelli)** | NO2 (µg/m³), PM2.5 (µg/m³), PM10 (µg/m³), O3 (µg/m³), SO2 (µg/m³), CO (mg/m³) | Feature di esposizione atmosferica nei modelli MLR, GAM, ARIMAX e Random Forest per Influenza e Legionellosi. PM2.5 è la variabile di esposizione primaria nel modello DLNM per Influenza (finestra di lag: 7 giorni); NO2 e O3 sono feature secondarie nei modelli MLR per la compromissione delle difese mucociliari. |
| **Statistiche Aggregate (Risposta API)** | data = {min, mean, max} per parametro; frequenza raw oraria aggregata su finestra temporale configurabile | Il valore mean costituisce l’input diretto ai modelli predittivi aggregati per istat_code e periodo. I valori min e max consentono la rilevazione di picchi di esposizione e la ricostruzione della distribuzione dell’inquinante nella finestra temporale, utile per i modelli GAM con termini di smoothing non lineare. |
| **Controllo Qualità del Dato** | validated = true, filter_on_range = true, limiti di range fisico per parametro | Esclusione automatica di misurazioni non validate dal sistema ARPAC e di valori anomali fuori range fisico (es. concentrazioni negative o superiori ai limiti strumentali). Garantisce la coerenza e l’affidabilità delle serie temporali di esposizione fornite come input ai modelli statistici. |
| **Aggregazione Spaziale per Comune (IDW)** | Pesi calcolati sulla distanza stazione–centroide comunale; aggregazione finale per istat_code | In presenza di più stazioni attive sullo stesso comune, la media pesata per distanza (IDW) produce un unico valore di esposizione rappresentativo del territorio comunale. Questo valore è il prerequisito per la join deterministica con i dati sanitari (case_count per istat_code e data). |

2. **Data Catalog: MeteoHub**  
   
    
   
  Il Data Catalog per MeteoHub descrive la struttura dei dati meteorologici (temperatura, precipitazioni, umidità, vento, ecc.) forniti tramite API POST. Anche per MeteoHub sono disponibili filtri spaziali (bbox, wkt o geojson con EPSG) e filtri di identificazione stazione/comune tramite station_id/station_name/istat_code, con logica AND/OR analoga: la stazione è selezionata con AND, mentre i sensori vengono selezionati in OR tramite parameter (es. Temperature o Precipitation_Amount), alias (codici BUFR) e/o parameter_id. Per le analisi batch vengono utilizzate le statistiche aggregate tramite POST /meteohub/data/meteohub_data_stats con stats=[min, mean, max] e finestra temporale startTimestamp/endTimestamp. La risposta è strutturalmente simile ad ARPAC ma con campi specifici: source=METEOHUB, network della rete, sensori con alias BUFR, unit e (a livello sensore) eventuale elev_ref; in MeteoHub la cadenza raw è al minuto, mentre l’endpoint *_stats restituisce direttamente data={min, mean, max} per parametro. I valori vengono normalizzati nelle unità coerenti con il modello (es. conversioni temperatura e precipitazione) e resi disponibili per l’integrazione con le esposizioni ambientali aggregate a livello di comune (istat_code) e periodo temporale.  
   
  **Utilizzo nel Progetto**  
   
    
   
  Nella seguente tabella vengono riportati i campi acquisiti dalla rete MeteoHub, organizzati per categoria funzionale, con indicazione della loro rilevanza diretta nei modelli analitici del sistema HealthTrace. I dati MeteoHub forniscono le variabili meteorologiche di modulazione nei modelli epidemiologici: la temperatura e l’umidità influenzano la sopravvivenza e la trasmissione dei patogeni, mentre le precipitazioni costituiscono la variabile di esposizione primaria per l’Epatite A e una variabile modulante per la Legionellosi.  
   
    
   
| | | |
|-|-|-|
| **Area/Categoria** |   **Campi Dati Rilevanti** |   **Rilevanza Analitica AI** |
| **Identificazione e Localizzazione Stazione** | station_id, station_name, istat_code, latitude, longitude; source = METEOHUB, network | Chiave di join con le segnalazioni sanitarie tramite istat_code; le coordinate sono utilizzate per il calcolo dei pesi IDW e per il censimento della quota altimetrica tramite integrazione con OpenTopoData (SRTM), poiché i metadati originali MeteoHub non includono il dato slm. |
| **Quota Altimetrica (da SRTM)** | slm derivato da OpenTopoData a partire da latitude/longitude; censimento eseguito una sola volta all’avvio | Filtro di idoneità stazione: le stazioni con quota superiore alla soglia definita vengono marcate come non idonee ed escluse automaticamente da tutte le interrogazioni successive. Garantisce che le serie meteorologiche siano rappresentative delle condizioni di esposizione della popolazione insediata e non di contesti montani. |
| **Temperatura (Input Modelli)** | Temperature (°C); alias BUFR; data = {min, mean, max}; cadenza raw al minuto, aggregata tramite /meteohub_data_stats | temperature_avg è feature nei modelli MLR, GAM e ARIMAX per Influenza (modulazione stagionale), Legionellosi (proliferazione Legionella tra 20–45 °C) ed Epatite A. È la variabile di esposizione primaria nel modello DLNM per Legionellosi (finestra di lag: 14 giorni). |
| **Precipitazioni (Input Modelli)** | Precipitation_Amount (mm); alias BUFR; data = {min, mean, max}; rainy_days derivato come conteggio di giorni con precipitazione positiva | precipitation e rainy_days sono feature nei modelli MLR, GAM e ARIMAX per Epatite A e Legionellosi. precipitation è la variabile di esposizione primaria nel modello DLNM per Epatite A (finestra di lag: 21 giorni), in quanto proxy del rischio di contaminazione idrica da deflusso superficiale. |
| **Umidità Relativa (Input Modelli)** | Humidity (%); alias BUFR; data = {min, mean, max} | Feature di modulazione nei modelli MLR e Random Forest per Influenza e Legionellosi. L’umidità influenza la sopravvivenza del virus influenzale nell’aria e la formazione di aerosol favorevoli alla dispersione di Legionella pneumophila. |
| **Statistiche Aggregate (Risposta API)** | data = {min, mean, max} per sensore; finestra temporale startTimestamp/endTimestamp; unit; eventuale elev_ref a livello sensore | Il valore mean è l’input diretto ai modelli predittivi aggregati per istat_code e periodo. I valori min e max supportano la rilevazione di eventi estremi (picchi di temperatura, precipitazioni intense) rilevanti per i termini non lineari nei modelli GAM e DLNM (variabile extreme_precipitation per Epatite A). |
| **Aggregazione Spaziale per Comune (IDW)** | Pesi calcolati sulla distanza stazione–centroide comunale; aggregazione finale per istat_code | In presenza di più stazioni idonee sullo stesso comune, la media pesata per distanza (IDW) produce un unico valore meteorologico rappresentativo del territorio comunale, allineato con la granularità spaziale dei dati sanitari e con la logica di aggregazione applicata alle stazioni ARPAC. |

3. **Data Catalog: OpenTopoData**  
   
    
   
  Il Data Catalog per OpenTopoData descrive il servizio DEM utilizzato per arricchire la registrazione delle stazioni, soprattutto per colmare valori mancanti di quota slm. Il sistema interroga OpenTopoData (SRTM) a partire dalle coordinate WGS84 della stazione (latitudine/longitudine), ottenendo una stima dell’elevazione in metri s.l.m. Tale valore viene usato nello step di station census e nella policy di filtro (es. esclusione delle stazioni con slm superiore alla soglia definita) per mantenere coerenza tra tipologie di stazioni ARPAC e MeteoHub all’interno della stessa area di studio. L’arricchimento è quindi un passaggio di qualità/normalizzazione geografica propedeutico all’aggregazione per istat_code e alla successiva correlazione con le serie epidemiologiche.  
 **Utilizzo nel Progetto**  
   
 Nella seguente tabella vengono riportati i campi e le operazioni coinvolte nell’integrazione con OpenTopoData, con indicazione della loro rilevanza nel contesto del sistema HealthTrace. OpenTopoData non è una fonte di dati ambientali diretti, ma un servizio di arricchimento geografico che abilita il filtraggio corretto delle stazioni MeteoHub, prerequisito indispensabile per la qualità delle serie temporali meteorologiche in ingresso ai modelli.  
   
| | | |
|-|-|-|
| **Area/Categoria** |  **Campi Dati Rilevanti** |  **Rilevanza Analitica AI** |
| **Input al Servizio** | latitude, longitude in formato WGS84 (EPSG:4326); modalità batch per l’elaborazione simultanea di coordinate multiple | Le coordinate di ciascuna stazione MeteoHub vengono inviate in batch al servizio REST di OpenTopoData al momento del censimento; la modalità batch minimizza il numero di chiamate esterne e consente il censimento completo della rete in un’unica operazione di avvio o di aggiornamento. |
| **Output del Servizio** | elevation (metri s.l.m.; dataset SRTM NASA/USGS, risoluzione ~30 m) | Il valore di quota restituito viene persistito in modo permanente nel registro delle stazioni (station census). Una volta completato il censimento, il sistema non effettua ulteriori chiamate esterne per il dato altimetrico, garantendo piena autonomia operativa durante il normale funzionamento. |
| **Filtro di Idoneità Stazione** | slm confrontato con soglia altimetrica configurabile (default: contesti abitati) | Le stazioni MeteoHub con quota superiore alla soglia definita vengono marcate come non idonee ed escluse automaticamente da tutte le interrogazioni successive di aggregazione IDW. Garantisce che le serie meteorologiche siano rappresentative delle condizioni di esposizione della popolazione insediata e non di contesti montani o non abitati. |
| **Coerenza tra Reti ARPAC e MeteoHub** | Applicazione della stessa soglia altimetrica a entrambe le reti di monitoraggio | ARPAC include il campo slm nei propri metadati di stazione; MeteoHub no. L’integrazione con OpenTopoData colma questa asimmetria strutturale, rendendo il criterio di filtro omogeneo tra le due reti e assicurando la comparabilità delle esposizioni aggregate per istat_code. |
| **Propedeuticità all’Aggregazione IDW** | slm utilizzato come gate logico prima del calcolo dei pesi di distanza IDW | Il filtro altimetrico è il primo step della pipeline di aggregazione spaziale: solo le stazioni marcate come idonee entrano nel calcolo della media pesata per distanza (IDW). Errori o omissioni in questa fase si propagherebbero a tutti i modelli downstream (MLR, GAM, ARIMAX, DLNM, Random Forest). |
| **Qualità e Normalizzazione Geografica** | Arricchimento eseguito una sola volta per stazione; valore persistito nel registro; nessuna dipendenza runtime dal servizio esterno | Garantisce l’autonomia operativa del sistema durante il funzionamento ordinario: la pipeline di ingestione ambientale non dipende dalla disponibilità in real-time di OpenTopoData. Il dato altimetrico è trattato come metadato statico di qualità della stazione, aggiornato solo in caso di aggiunta di nuove stazioni. |

4. **Data Catalog: ISTAT**  
   
    
   
  Il Data Catalog per ISTAT descrive la codifica geografica utilizzata per garantire l’allineamento tra fonti ambientali e dati sanitari. Il sistema assume istat_code come chiave del comune (6 cifre) per associare le esposizioni ambientali aggregate al comune di riferimento e al periodo temporale di analisi. Nel caso dei dati sanitari la variabile geografica proviene dalla scheda patologia (es. comune_inizio_sintomi_codice_istat), mentre per le fonti ambientali istat_code è fornito dai filtri richiesta e contenuto nella risposta (ARPAC e MeteoHub) come codice del comune. Questa codifica consente join e confronti coerenti a livello di comune (istat_code), e può essere ulteriormente utilizzata per eventuali viste a granularità superiore (provincia/regione) nelle componenti di BI e nelle analisi statistiche.  
**Utilizzo nel Progetto**  
Nella seguente tabella vengono riportati i campi e le modalità di utilizzo del codice ISTAT nel sistema HealthTrace. Il codice ISTAT comunale non è una fonte di dati primari, ma la chiave di integrazione universale che rende possibile la join deterministica tra tutte le fonti eterogenee del sistema, eliminando la necessità di operazioni di geocoding o di inferenza geografica.  
| | | |
|-|-|-|
| **Area/Categoria** | **Campi Dati Rilevanti** | **Rilevanza Analitica AI** |
| **Struttura del Codice** | istat_code: stringa numerica a 6 cifre; prime 2 cifre = regione, prime 3 = provincia, codice completo = comune | Struttura gerarchica che consente analisi aggregate a livello provinciale e regionale per derivazione diretta, senza tabelle di corrispondenza aggiuntive. Rilevante per i modelli di autocorrelazione spaziale (Moran’s I, Getis-Ord Gi*) che operano a granularità comunale ma possono essere aggregati a livelli superiori nelle dashboard BI. |
| **Chiave nel Database Sanitario** | comune_inizio_sintomi_codice_istat (scheda patologia GESAN) | Collega ogni segnalazione clinica al territorio di probabile esposizione del paziente. L’utilizzo del comune di inizio sintomi — anziché di residenza — è epidemiologicamente corretto: riduce l’errore sistematico di classificazione geografica nei modelli di correlazione ambientale-sanitaria e garantisce la coerenza della finestra di esposizione nei modelli DLNM. |
| **Chiave nelle Fonti Ambientali** | istat_code presente come attributo nella risposta API di ARPAC e MeteoHub per ogni stazione | Consente la join diretta tra le esposizioni ambientali aggregate per comune (output della pipeline IDW) e i conteggi di casi sanitari per comune e periodo, senza operazioni di geocoding intermedio. Garantisce l’integrità referenziale tra le fonti a prescindere dalla loro eterogeneità tecnica. |
| **Granularità Minima di Analisi** | Livello comunale (istat_code a 6 cifre); unità spaziale base del sistema | Il comune è l’unità spaziale su cui operano tutti i modelli statistici del sistema: MLR, GAM, ARIMAX, DLNM, Random Forest e modelli spaziali (Moran’s I, LISA, Getis-Ord Gi*) operano su serie aggregate per istat_code e periodo temporale. Riduce la variabilità intra-comunale e allinea la granularità dei dati sanitari con quella dei dati ambientali. |
| **Aggregazioni Superiori (BI)** | Codice provincia = prime 3 cifre di istat_code; codice regione = prime 2 cifre | Abilita le viste a granularità provinciale e regionale nelle componenti di Business Intelligence per derivazione diretta, senza necessità di tabelle di lookup esterne. Utile per report epidemiologici a scala regionale (Regione Campania) e per confronti inter-provinciali nelle analisi di sorveglianza epidemiologica. |
| **Standard di Interoperabilità** | Adottato uniformemente da GESAN, ARPAC, MeteoHub, ASP Cosenza e ASL Napoli 1, nonché da tutti i sistemi informativi della pubblica amministrazione italiana | Elimina ambiguità semantiche e disallineamenti geografici tra fonti istituzionali eterogenee. La coerenza del codice tra tutte le fonti è la condizione necessaria per l’esecuzione corretta di tutti i join del sistema senza logiche di riconciliazione aggiuntive. |
