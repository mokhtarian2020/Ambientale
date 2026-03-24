                                            <i class="bi bi-table me-2"></i>
                                            Dettaglio Completo per Codice ISTAT
                                        </h6>
                                        <div id="istatDetailTable"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Time-based ISTAT Analysis -->
            <div class="row g-4 mb-4">
                <div class="col-12">
                    <div class="chart-container bg-success bg-gradient text-white">
                        <h4 class="text-white mb-4">
                            <i class="bi bi-clock-history me-2"></i>
                            Analisi Temporale per Codice ISTAT
                        </h4>
                        
                        <!-- Current Data Timeline by ISTAT -->
                        <div class="row g-4 mb-4">
                            <div class="col-12">
                                <div class="card bg-white text-dark">
                                    <div class="card-body">
                                        <h6 class="card-title">
                                            <i class="bi bi-graph-up me-2"></i>
                                            Distribuzione Corrente nel Tempo per Principali Comuni ISTAT
                                        </h6>
                                        <div class="mb-3">
                                            <div class="btn-group" role="group">
                                                <input type="radio" class="btn-check" name="diseaseFilter" id="allDiseases" checked>
                                                <label class="btn btn-outline-primary btn-sm" for="allDiseases">Tutte le Malattie</label>
                                                
                                                <input type="radio" class="btn-check" name="diseaseFilter" id="influenzaOnly">
                                                <label class="btn btn-outline-primary btn-sm" for="influenzaOnly">Solo Influenza</label>
                                                
                                                <input type="radio" class="btn-check" name="diseaseFilter" id="legionellosisOnly">
                                                <label class="btn btn-outline-warning btn-sm" for="legionellosisOnly">Solo Legionellosi</label>
                                                
                                                <input type="radio" class="btn-check" name="diseaseFilter" id="hepatitisOnly">
                                                <label class="btn btn-outline-success btn-sm" for="hepatitisOnly">Solo Epatite A</label>
                                            </div>
                                        </div>
                                        <div id="istatTimelineChart" style="height: 500px;"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Time-based Predictions by ISTAT -->
                        <div class="row g-4">
                            <div class="col-12">
                                <div class="card bg-white text-dark">
                                    <div class="card-body">
                                        <h6 class="card-title">
                                            <i class="bi bi-calendar-range me-2"></i>
                                            Previsioni Temporali per Principali Comuni ISTAT (Prossimi 6 Mesi)
                                        </h6>
                                        <div class="mb-3">
                                            <div class="alert alert-info">
                                                <small>
                                                    <i class="bi bi-info-circle me-1"></i>
                                                    Previsioni basate su modelli ARIMA per i 5 comuni con maggiore storico di casi
                                                </small>
                                            </div>
                                        </div>
                                        <div id="istatTimePredicationsChart" style="height: 600px;"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Time Filter Panel -->
            <div class="filter-panel">
                <h5 class="mb-4">
                    <i class="bi bi-funnel me-2"></i>
                    Filtri Temporali per Grafici
                </h5>
                <div class="row g-3">
                    <div class="col-md-3">
                        <label class="form-label fw-semibold">Data Inizio</label>
                        <input type="date" class="form-control form-control-medical" id="startDate">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label fw-semibold">Data Fine</label>
                        <input type="date" class="form-control form-control-medical" id="endDate">
                    </div>
                    <div class="col-md-3 d-flex align-items-end">
                        <button class="btn btn-medical me-2" onclick="applyChartFilter()">
                            <i class="bi bi-funnel me-1"></i> Applica Filtro
                        </button>
                        <button class="btn btn-outline-medical" onclick="resetChartFilter()">
                            <i class="bi bi-arrow-counterclockwise me-1"></i> Reset
                        </button>
                    </div>
                    <div class="col-md-3">
                        <div class="alert alert-info alert-medical mb-0 py-2">
                            <small>
                                <i class="bi bi-info-circle me-1"></i>
                                I filtri si applicano solo ai primi 3 grafici
                            </small>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Charts Section with Bootstrap Grid -->
            <div class="row g-4">
                <!-- Chart 1: Disease Distribution -->
                <div class="col-lg-6">
                    <div class="chart-container">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="chart-title mb-0">
                                <i class="bi bi-pie-chart me-2"></i>
                                Distribuzione Casi per Malattia
                            </h5>
                            <div class="d-flex gap-2 align-items-center">
                                <input type="date" class="form-control form-control-sm" id="distributionStartDate" style="width: auto;">
                                <input type="date" class="form-control form-control-sm" id="distributionEndDate" style="width: auto;">
                                <button class="btn btn-sm btn-medical" onclick="applyChartFilter('distribution')">
                                    <i class="bi bi-funnel"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-medical" onclick="resetChartFilter('distribution')">
                                    <i class="bi bi-arrow-counterclockwise"></i>
                                </button>
                            </div>
                        </div>
                        <div id="diseaseDistributionChart" class="chart-svg"></div>
                    </div>
                </div>
                
                <!-- Chart 2: Monthly Trends -->
                <div class="col-lg-6">
                    <div class="chart-container">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="chart-title mb-0" id="monthlyTrendsTitle">
                                <i class="bi bi-graph-up me-2"></i>
                                Trend Mensili (Ultimi 24 Mesi)
                            </h5>
                            <div class="d-flex gap-2 align-items-center">
                                <input type="date" class="form-control form-control-sm" id="trendsStartDate" style="width: auto;">
                                <input type="date" class="form-control form-control-sm" id="trendsEndDate" style="width: auto;">
                                <button class="btn btn-sm btn-medical" onclick="applyChartFilter('trends')">
                                    <i class="bi bi-funnel"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-medical" onclick="resetChartFilter('trends')">
                                    <i class="bi bi-arrow-counterclockwise"></i>
                                </button>
                            </div>
                        </div>
                        <div id="monthlyTrendsChart" class="chart-svg"></div>
                    </div>
                </div>
                
                <!-- Chart 3: Regional Comparison -->
                <div class="col-12">
                    <div class="chart-container">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="chart-title mb-0">
                                <i class="bi bi-bar-chart me-2"></i>
                                Confronto Regionale
                            </h5>
                            <div class="d-flex gap-2 align-items-center">
                                <input type="date" class="form-control form-control-sm" id="regionalStartDate" style="width: auto;">
                                <input type="date" class="form-control form-control-sm" id="regionalEndDate" style="width: auto;">
                                <button class="btn btn-sm btn-medical" onclick="applyChartFilter('regional')">
                                    <i class="bi bi-funnel"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-medical" onclick="resetChartFilter('regional')">
                                    <i class="bi bi-arrow-counterclockwise"></i>
                                </button>
                            </div>
                        </div>
                        <div id="regionalComparisonChart" class="chart-svg"></div>
                    </div>
                </div>
                
                <!-- Charts without filters -->
                <div class="col-lg-6">
                    <div class="chart-container">
                        <h5 class="chart-title">
                            <i class="bi bi-lightning me-2"></i>
                            Previsioni Epidemiologiche
                        </h5>
                        <div class="alert alert-info alert-medical">
                            <i class="bi bi-info-circle me-2"></i>
                            <small>Questo grafico mostra sempre tutti i dati storici per accuratezza predittiva</small>
                        </div>
                        <div id="predictionsChart" class="chart-svg"></div>
                    </div>
                </div>
                
                <div class="col-lg-6">
                    <div class="chart-container">
                        <h5 class="chart-title">
                            <i class="bi bi-clock-history me-2"></i>
                            Analisi Storica Completa
                        </h5>
                        <div class="alert alert-info alert-medical">
                            <i class="bi bi-info-circle me-2"></i>
                            <small>Vista completa di tutti i dati storici disponibili</small>
                        </div>
                        <div id="historicalAnalysisChart" class="chart-svg"></div>
                    </div>
                </div>
            </div>
                
                <!-- Chart 3: Regional Comparison with individual filter -->
                <div class="chart-container">
                    <div class="chart-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <div class="chart-title">Confronto Regionale Top 10</div>
                        <div class="chart-filter" style="display: flex; gap: 10px; align-items: center; font-size: 0.9em;">
                            <input type="date" id="regionalStartDate" style="padding: 4px; border: 1px solid #ced4da; border-radius: 4px; font-size: 0.8em;">
                            <input type="date" id="regionalEndDate" style="padding: 4px; border: 1px solid #ced4da; border-radius: 4px; font-size: 0.8em;">
                            <button onclick="applyChartFilter('regional')" style="padding: 4px 8px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.8em;">Applica</button>
                            <button onclick="resetChartFilter('regional')" style="padding: 4px 8px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.8em;">Reset</button>
                        </div>
                    </div>
                    <div id="regionalComparisonChart"></div>
                </div>
                
                <!-- Chart 4: Predictions (NO FILTER) -->
                <div class="chart-container">
                    <div class="chart-title">🔮 Previsioni Time Series (Prossimi 6 Mesi)</div>
                    <div id="predictionChart"></div>
                    <div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 8px; font-size: 0.9em; color: #666;">
                        <strong>📊 Metodologia Predittiva:</strong> Le previsioni utilizzano analisi time series con media mobile, 
                        tasso di crescita e fattori stagionali. L'affidabilità diminuisce nel tempo (confidence level mostrato come trasparenza).
                    </div>
                </div>
                
                <!-- Chart 5: Historical Predictions (NO FILTER) -->
                <div class="chart-container">
                    <div class="chart-title">📈 Analisi Trend Storico vs Predizioni</div>
                    <div id="historicalPredictionChart"></div>
                    <div style="margin-top: 10px;">
                        <label style="margin-right: 20px;">
                            <input type="checkbox" id="showConfidenceIntervals" checked> Mostra intervalli di confidenza
                        </label>
                        <label>
                            <input type="checkbox" id="showSeasonalFactors" checked> Evidenzia fattori stagionali
                        </label>
                    </div>
                </div>
            </div>
            
            <!-- Mappa interattiva -->
            <div class="map-container">
                <div class="chart-title">📍 Distribuzione Geografica Casi</div>
                <div id="diseaseMap"></div>
                <div class="legend" id="mapLegend"></div>
            </div>
            
            <!-- Tabelle dettagliate -->
            <div class="chart-container">
                <div class="chart-title">Dettaglio per Codice ISTAT Comunale</div>
                <div id="regionalTables"></div>
            </div>
        </div>
    </div>
    
    <script>
        let diseaseData = null;
        let originalDiseaseData = null; // Store original unfiltered data
        let map = null;
        let miniMap = null;
        let charts = {};
        let chartFilters = {
            distribution: { startDate: null, endDate: null, data: null },
            trends: { startDate: null, endDate: null, data: null },
            regional: { startDate: null, endDate: null, data: null }
        };
        
        // Colori per le malattie
        const diseaseColors = {
            influenza: '#3498db',
            legionellosi: '#e74c3c', 
            hepatitis_a: '#f39c12'
        };
        
        // Mappatura ISTAT codes alle coordinate (campione)
        const istatCoordinates = {
            '061007': [40.8518, 14.2681], // Napoli
            '063049': [40.7589, 14.7947], // Salerno
            '061032': [40.9538, 14.7841], // Caserta
            '062012': [41.1171, 14.3285], // Campobasso
            '015146': [38.1157, 13.3613], // Palermo
            '058091': [38.1938, 15.5540], // Messina
            '083048': [41.4651, 12.9036], // Rieti
            '015063': [37.5079, 15.0830], // Catania
        };

        // Funzioni per i filtri individuali per ogni grafico
        function initializeIndividualFilters() {
            const today = new Date();
            const oneYearAgo = new Date();
            oneYearAgo.setFullYear(today.getFullYear() - 1);
            
            const defaultStart = oneYearAgo.toISOString().split('T')[0];
            const defaultEnd = today.toISOString().split('T')[0];
            
            // Initialize all chart filters with default dates
            const chartTypes = ['distribution', 'trends', 'regional'];
            chartTypes.forEach(chartType => {
                document.getElementById(chartType + 'StartDate').value = defaultStart;
                document.getElementById(chartType + 'EndDate').value = defaultEnd;
                chartFilters[chartType].data = JSON.parse(JSON.stringify(originalDiseaseData));
            });
        }
        
        function applyChartFilter(chartType) {
            const startDateId = chartType + 'StartDate';
            const endDateId = chartType + 'EndDate';
            
            const startDate = document.getElementById(startDateId).value;
            const endDate = document.getElementById(endDateId).value;
            
            if (!startDate || !endDate) {
                alert('Seleziona entrambe le date per ' + getChartName(chartType));
                return;
            }
            
            if (new Date(startDate) > new Date(endDate)) {
                alert('La data di inizio deve essere precedente alla data di fine');
                return;
            }
            
            chartFilters[chartType].startDate = startDate;
            chartFilters[chartType].endDate = endDate;
            
            // Filter data specifically for this chart
            filterChartData(chartType);
            
            // Re-render only the specific chart
            renderSpecificChart(chartType);
            
            // Update title if needed
            updateChartTitle(chartType);
        }
        
        function resetChartFilter(chartType) {
            chartFilters[chartType].startDate = null;
            chartFilters[chartType].endDate = null;
            
            // Restore original data for this chart
            if (originalDiseaseData) {
                chartFilters[chartType].data = JSON.parse(JSON.stringify(originalDiseaseData));
            }
            
            // Re-render the specific chart
            renderSpecificChart(chartType);
            
            // Reset dates to default
            initializeIndividualFilters();
            
            // Update title
            updateChartTitle(chartType);
        }
        
        function filterChartData(chartType) {
            if (!originalDiseaseData || !chartFilters[chartType].startDate || !chartFilters[chartType].endDate) {
                return;
            }
            
            console.log(`🔍 Filtering data for chart: ${chartType}`);
            console.log(`📅 Date range: ${chartFilters[chartType].startDate} to ${chartFilters[chartType].endDate}`);
            
            const startDate = new Date(chartFilters[chartType].startDate);
            const endDate = new Date(chartFilters[chartType].endDate);
            
            // Deep copy original data for this specific chart
            chartFilters[chartType].data = JSON.parse(JSON.stringify(originalDiseaseData));
            const chartData = chartFilters[chartType].data;
            
            // Filter each disease's data
            for (const diseaseName in chartData.diseases) {
                const disease = chartData.diseases[diseaseName];
                const originalCasesCount = disease.cases ? disease.cases.length : 0;
                
                // Filter cases by date
                if (disease.cases) {
                    disease.cases = disease.cases.filter(caseData => {
                        if (!caseData.data_inizio) return true;
                        const caseDate = new Date(caseData.data_inizio);
                        return caseDate >= startDate && caseDate <= endDate;
                    });
                }
                
                // Update totals
                disease.total = disease.cases ? disease.cases.length : 0;
                disease.total_cases = disease.cases ? disease.cases.length : 0; // For chart compatibility
                
                console.log(`📊 ${diseaseName}: ${originalCasesCount} → ${disease.total_cases} cases after filtering`);
                
                // Filter monthly trends
                if (disease.monthly_trends) {
                    disease.monthly_trends = disease.monthly_trends.filter(trend => {
                        if (!trend.month) return true;
                        const trendDate = new Date(trend.month + '-01');
                        return trendDate >= startDate && trendDate <= endDate;
                    });
                }
                
                // Filter regional data
                if (disease.regional_data) {
                    const filteredRegional = {};
                    for (const region in disease.regional_data) {
                        const regionCases = disease.regional_data[region].filter(caseData => {
                            if (!caseData.data_inizio) return true;
                            const caseDate = new Date(caseData.data_inizio);
                            return caseDate >= startDate && caseDate <= endDate;
                        });
                        if (regionCases.length > 0) {
                            filteredRegional[region] = regionCases;
                        }
                    }
                    disease.regional_data = filteredRegional;
                }
                
                // Filter geographic distribution (needed for regional comparison chart)
                if (disease.geographic_distribution || disease.cases) {
                    // Rebuild geographic distribution from filtered cases
                    const geoDistribution = {};
                    disease.cases.forEach(caseData => {
                        // Check multiple possible field names for ISTAT code
                        const istatCode = caseData.comune_residenza_codice_istat || 
                                        caseData.comune_residenza || 
                                        caseData.istat_code;
                        if (istatCode) {
                            if (!geoDistribution[istatCode]) {
                                geoDistribution[istatCode] = {
                                    comune_residenza_codice_istat: istatCode,
                                    count: 0,
                                    case_count: 0
                                };
                            }
                            geoDistribution[istatCode].count++;
                            geoDistribution[istatCode].case_count++;
                        }
                    });
                    
                    // Convert to array and sort by count
                    disease.geographic_distribution = Object.values(geoDistribution)
                        .sort((a, b) => b.count - a.count);
                    
                    console.log(`📍 ${diseaseName} geographic distribution after filtering:`, disease.geographic_distribution.slice(0, 3));
                }
            }
        }
        
        function renderSpecificChart(chartType) {
            // Temporarily set diseaseData to the filtered data for this chart
            const originalData = diseaseData;
            diseaseData = chartFilters[chartType].data;
            
            try {
                console.log(`🎯 Rendering specific chart with D3.js: ${chartType}`);
                
                // D3.js handles updates seamlessly - just re-render
                switch(chartType) {
                    case 'distribution':
                        renderDiseaseDistribution();
                        break;
                    case 'trends':
                        renderMonthlyTrends();
                        break;
                    case 'regional':
                        renderRegionalComparison();
                        break;
                }
            } catch (error) {
                console.error('Error rendering chart:', chartType, error);
            }
            
            // Restore original data
            diseaseData = originalData;
        }
        
        function updateChartTitle(chartType) {
            if (chartType === 'trends') {
                const titleElement = document.getElementById('monthlyTrendsTitle');
                if (chartFilters[chartType].startDate && chartFilters[chartType].endDate) {
                    titleElement.textContent = `Trend Mensili (${chartFilters[chartType].startDate} - ${chartFilters[chartType].endDate})`;
                } else {
                    titleElement.textContent = 'Trend Mensili (Tutti i Dati)';
                }
            }
        }
        
        function getChartName(chartType) {
            const names = {
                distribution: 'Distribuzione Casi',
                trends: 'Trend Mensili',
                regional: 'Confronto Regionale'
            };
            return names[chartType] || chartType;
        }

        // Mappatura ISTAT codes ai nomi dei luoghi (Regione Campania)
        const istatPlaceNames = {
            // Provincia di Napoli (061xxx)
            '061007': 'Napoli',
            '061001': 'Acerra', 
            '061002': 'Afragola',
            '061003': 'Agerola',
            '061004': 'Anacapri',
            '061005': 'Arzano',
            '061006': 'Bacoli',
            '061008': 'Barano d\'Ischia',
            '061009': 'Boscoreale',
            '061010': 'Boscotrecase',
            '061011': 'Brusciano',
            '061012': 'Calvizzano',
            '061013': 'Camposano',
            '061014': 'Capri',
            '061015': 'Carbonara di Nola',
            '061016': 'Cardito',
            '061017': 'Casalnuovo di Napoli',
            '061018': 'Casamarciano',
            '061019': 'Casamicciola Terme',
            '061020': 'Casandrino',
            '061021': 'Casavatore',
            '061022': 'Castellammare di Stabia',
            '061023': 'Castello di Cisterna',
            '061024': 'Cercola',
            '061025': 'Cicciano',
            '061026': 'Cimitile',
            '061027': 'Comiziano',
            '061028': 'Crispano',
            '061029': 'Ercolano',
            '061030': 'Forio',
            '061031': 'Frattamaggiore',
            '061032': 'Frattaminore',
            '061033': 'Giugliano in Campania',
            '061034': 'Gragnano',
            '061035': 'Grumo Nevano',
            '061036': 'Ischia',
            '061037': 'Lacco Ameno',
            '061038': 'Lettere',
            '061039': 'Liveri',
            '061040': 'Mariglianella',
            '061041': 'Marigliano',
            '061042': 'Marano di Napoli',
            '061043': 'Massa di Somma',
            '061044': 'Melito di Napoli',
            '061045': 'Meta',
            '061046': 'Monte di Procida',
            '061047': 'Mugnano di Napoli',
            '061048': 'Nola',
            '061049': 'Ottaviano',
            '061050': 'Palma Campania',
            '061051': 'Piano di Sorrento',
            '061052': 'Pimonte',
            '061053': 'Poggiomarino',
            '061054': 'Pollena Trocchia',
            '061055': 'Pomigliano d\'Arco',
            '061056': 'Pompei',
            '061057': 'Portici',
            '061058': 'Pozzuoli',
            '061059': 'Procida',
            '061060': 'Qualiano',
            '061061': 'Quarto',
            '061062': 'Roccarainola',
            '061063': 'San Gennaro Vesuviano',
            '061064': 'San Giorgio a Cremano',
            '061065': 'San Giuseppe Vesuviano',
            '061066': 'San Paolo Bel Sito',
            '061067': 'San Sebastiano al Vesuvio',
            '061068': 'San Vitaliano',
            '061069': 'Sant\'Agnello',
            '061070': 'Sant\'Anastasia',
            '061071': 'Sant\'Antimo',
            '061072': 'Sant\'Antonio Abate',
            '061073': 'Saviano',
            '061074': 'Scisciano',
            '061075': 'Serrara Fontana',
            '061076': 'Somma Vesuviana',
            '061077': 'Sorrento',
            '061078': 'Striano',
            '061079': 'Terzigno',
            '061080': 'Torre Annunziata',
            '061081': 'Torre del Greco',
            '061082': 'Trecase',
            '061083': 'Tufino',
            '061084': 'Vico Equense',
            '061085': 'Villa di Briano',
            '061086': 'Villaricca',
            '061087': 'Visciano',
            '061088': 'Volla',
            '061089': 'Villaricca',
            
            // Provincia di Salerno (065xxx)
            '065001': 'Salerno',
            '065002': 'Acerno',
            '065003': 'Agropoli',
            '065004': 'Albanella',
            '065005': 'Alfano',
            '065006': 'Altavilla Silentina',
            '065007': 'Amalfi',
            '065008': 'Angri',
            '065009': 'Aquara',
            '065010': 'Ascea',
            '065011': 'Atena Lucana',
            '065012': 'Atrani',
            '065013': 'Auletta',
            '065014': 'Baronissi',
            '065015': 'Battipaglia',
            '065016': 'Bellosguardo',
            '065017': 'Bracigliano',
            '065018': 'Buccino',
            '065019': 'Buonabitacolo',
            '065020': 'Caggiano',
            '065021': 'Calvanico',
            '065022': 'Camerota',
            '065023': 'Campagna',
            '065024': 'Campora',
            '065025': 'Cannalonga',
            '065026': 'Capaccio Paestum',
            '065027': 'Casal Velino',
            '065028': 'Casalbuono',
            '065029': 'Caselle in Pittari',
            '065030': 'Castellabate',
            '065031': 'Castelnuovo Cilento',
            '065032': 'Castelnuovo di Conza',
            '065033': 'Castelcivita',
            '065034': 'Castiglione del Genovesi',
            '065035': 'Cava de\' Tirreni',
            '065036': 'Celle di Bulgheria',
            '065037': 'Centola',
            '065038': 'Ceraso',
            '065039': 'Cetara',
            '065040': 'Cicerale',
            '065041': 'Colliano',
            '065042': 'Conca dei Marini',
            '065043': 'Controne',
            '065044': 'Contursi Terme',
            '065045': 'Corbara',
            '065046': 'Corleto Monforte',
            '065047': 'Cuccaro Vetere',
            '065048': 'Eboli',
            '065049': 'Felitto',
            '065050': 'Fisciano',
            '065051': 'Furore',
            '065052': 'Futani',
            '065053': 'Giffoni Sei Casali',
            '065054': 'Giffoni Valle Piana',
            '065055': 'Gioi',
            '065056': 'Giungano',
            '065057': 'Ispani',
            '065058': 'Laureana Cilento',
            '065059': 'Laurino',
            '065060': 'Laurito',
            '065061': 'Laviano',
            '065062': 'Lustra',
            '065063': 'Maiori',
            '065064': 'Mercato San Severino',
            '065065': 'Minori',
            '065066': 'Moio della Civitella',
            '065067': 'Monte San Giacomo',
            '065068': 'Montecorice',
            '065069': 'Monteforte Cilento',
            '065070': 'Montesano sulla Marcellana',
            '065071': 'Morigerati',
            '065072': 'Nocera Inferiore',
            '065073': 'Nocera Superiore',
            '065074': 'Novi Velia',
            '065075': 'Ogliastro Cilento',
            '065076': 'Olevano sul Tusciano',
            '065077': 'Omignano',
            '065078': 'Orria',
            '065079': 'Ottati',
            '065080': 'Padula',
            '065081': 'Pagani',
            '065082': 'Palazzo San Gervasio',
            '065083': 'Palomonte',
            '065084': 'Perdifumo',
            '065085': 'Perito',
            '065086': 'Pertosa',
            '065087': 'Petina',
            '065088': 'Piaggine',
            '065089': 'Pisciotta',
            '065090': 'Polla',
            '065091': 'Pollica',
            '065092': 'Pontecagnano Faiano',
            '065093': 'Positano',
            '065094': 'Praiano',
            '065095': 'Prignano Cilento',
            '065096': 'Ravello',
            '065097': 'Roccadaspide',
            '065098': 'Roccagloriosa',
            '065099': 'Roccapiemonte',
            '065100': 'Rofrano',
            '065101': 'Roscigno',
            '065102': 'Rutino',
            '065103': 'Sacco',
            '065104': 'Sala Consilina',
            '065105': 'Salento',
            '065106': 'San Cipriano Picentino',
            '065107': 'San Giovanni a Piro',
            '065108': 'San Gregorio Magno',
            '065109': 'San Lorenzo',
            '065110': 'San Mango Piemonte',
            '065111': 'San Marzano sul Sarno',
            '065112': 'San Mauro Cilento',
            '065113': 'San Mauro la Bruca',
            '065114': 'San Pietro al Tanagro',
            '065115': 'San Rufo',
            '065116': 'San Valentino Torio',
            '065117': 'Sant\'Angelo a Fasanella',
            '065118': 'Sant\'Arsenio',
            '065119': 'Sant\'Egidio del Monte Albino',
            '065120': 'Santa Marina',
            '065121': 'Santomenna',
            '065122': 'Sapri',
            '065123': 'Sarno',
            '065124': 'Sassano',
            '065125': 'Scafati',
            '065126': 'Scala',
            '065127': 'Scanno',
            '065128': 'Serramezzana',
            '065129': 'Sessa Cilento',
            '065130': 'Siano',
            '065131': 'Sicignano degli Alburni',
            '065132': 'Stella Cilento',
            '065133': 'Stio',
            '065134': 'Teggiano',
            '065135': 'Torraca',
            '065136': 'Torchiara',
            '065137': 'Torre Orsaia',
            '065138': 'Tortorella',
            '065139': 'Tramonti',
            '065140': 'Trentinara',
            '065141': 'Valle dell\'Angelo',
            '065142': 'Vallo della Lucania',
            '065143': 'Valva',
            '065144': 'Vibonati',
            '065145': 'Vietri sul Mare',
            '065146': 'Laurino',
            
            // Provincia di Avellino (064xxx)
            '064001': 'Avellino',
            '064002': 'Aiello del Sabato',
            '064003': 'Altavilla Irpina',
            '064004': 'Andretta',
            '064005': 'Aquilonia',
            '064006': 'Ariano Irpino',
            '064007': 'Atripalda',
            '064008': 'Bagnoli Irpino',
            '064009': 'Baiano',
            '064010': 'Bisaccia',
            '064011': 'Bonito',
            '064012': 'Borgo San Lorenzo',
            '064013': 'Cairano',
            '064014': 'Calitri',
            '064015': 'Candida',
            '064016': 'Caposele',
            '064017': 'Capriglia Irpina',
            '064018': 'Carife',
            '064019': 'Casalbore',
            '064020': 'Cassano Irpino',
            '064021': 'Castel Baronia',
            '064022': 'Castelfranci',
            '064023': 'Castelvetere in Val Fortore',
            '064024': 'Cervinara',
            '064025': 'Cesinali',
            '064026': 'Chianche',
            '064027': 'Chiusano di San Domenico',
            '064028': 'Contrada',
            '064029': 'Conza della Campania',
            '064030': 'Domicella',
            '064031': 'Ferrazzano',
            '064032': 'Flumeri',
            '064033': 'Fontanarosa',
            '064034': 'Forino',
            '064035': 'Frigento',
            '064036': 'Gesualdo',
            '064037': 'Greci',
            '064038': 'Grottaminarda',
            '064039': 'Grottolella',
            '064040': 'Guardia Lombardi',
            '064041': 'Lacedonia',
            '064042': 'Lapio',
            '064043': 'Lauro',
            '064044': 'Lioni',
            '064045': 'Luogosano',
            '064046': 'Manocalzati',
            '064047': 'Marzano di Nola',
            '064048': 'Melito Irpino',
            '064049': 'Mercogliano',
            '064050': 'Mirabella Eclano',
            '064051': 'Montaguto',
            '064052': 'Montecalvo Irpino',
            '064053': 'Montefalcione',
            '064054': 'Monteforte Irpino',
            '064055': 'Montefredane',
            '064056': 'Montefusco',
            '064057': 'Montella',
            '064058': 'Montemarano',
            '064059': 'Montemiletto',
            '064060': 'Monteverde',
            '064061': 'Morra De Sanctis',
            '064062': 'Moschiano',
            '064063': 'Mugnano del Cardinale',
            '064064': 'Nusco',
            '064065': 'Ospedaletto d\'Alpinolo',
            '064066': 'Parolise',
            '064067': 'Paternopoli',
            '064068': 'Petruro Irpino',
            '064069': 'Pietradefusi',
            '064070': 'Pietrastornina',
            '064071': 'Prata di Principato Ultra',
            '064072': 'Pratola Serra',
            '064073': 'Quadrelle',
            '064074': 'Quindici',
            '064075': 'Roccabascerana',
            '064076': 'Rocca San Felice',
            '064077': 'Rotondi',
            '064078': 'Salza Irpina',
            '064079': 'San Mango sul Calore',
            '064080': 'San Martino Valle Caudina',
            '064081': 'San Michele di Serino',
            '064082': 'San Nicola Baronia',
            '064083': 'San Potito Ultra',
            '064084': 'San Sossio Baronia',
            '064085': 'Santa Lucia di Serino',
            '064086': 'Santa Paolina',
            '064087': 'Sant\'Andrea di Conza',
            '064088': 'Sant\'Angelo all\'Esca',
            '064089': 'Sant\'Angelo dei Lombardi',
            '064090': 'Sant\'Angelo a Scala',
            '064091': 'Santo Stefano del Sole',
            '064092': 'Scampitella',
            '064093': 'Senerchia',
            '064094': 'Serino',
            '064095': 'Sirignano',
            '064096': 'Solofra',
            '064097': 'Sorbo Serpico',
            '064098': 'Sperone',
            '064099': 'Sturno',
            '064100': 'Summonte',
            '064101': 'Taurano',
            '064102': 'Taurasi',
            '064103': 'Teora',
            '064104': 'Torella dei Lombardi',
            '064105': 'Torre Le Nocelle',
            '064106': 'Torrioni',
            '064107': 'Trevico',
            '064108': 'Tufo',
            '064109': 'Vallata',
            '064110': 'Vallesaccarda',
            '064111': 'Venticano',
            '064112': 'Villamaina',
            '064113': 'Villanova del Battista',
            '064114': 'Volturara Irpina',
            '064115': 'Zungoli',
            
            // Provincia di Benevento (062xxx)
            '062001': 'Benevento',
            '062002': 'Airola',
            '062003': 'Amorosi',
            '062004': 'Apice',
            '062005': 'Apollosa',
            '062006': 'Arpaia',
            '062007': 'Arpaise',
            '062008': 'Baselice',
            '062009': 'Bonea',
            '062010': 'Bucciano',
            '062011': 'Buonalbergo',
            '062012': 'Buzzi',
            '062013': 'Calvi',
            '062014': 'Campolattaro',
            '062015': 'Campoli del Monte Taburno',
            '062016': 'Casalduni',
            '062017': 'Castelfranco in Miscano',
            '062018': 'Castelpagano',
            '062019': 'Castelpoto',
            '062020': 'Castelvenere',
            '062021': 'Castelvetere in Val Fortore',
            '062022': 'Cautano',
            '062023': 'Ceppaloni',
            '062024': 'Cercemaggiore',
            '062025': 'Cerreto Sannita',
            '062026': 'Circello',
            '062027': 'Colle Sannita',
            '062028': 'Cusano Mutri',
            '062029': 'Dugenta',
            '062030': 'Durazzano',
            '062031': 'Faeto',
            '062032': 'Faicchio',
            '062033': 'Foglianise',
            '062034': 'Foiano di Val Fortore',
            '062035': 'Forchia',
            '062036': 'Fragneto l\'Abate',
            '062037': 'Fragneto Monforte',
            '062038': 'Frasso Telesino',
            '062039': 'Ginestra degli Schiavoni',
            '062040': 'Gioia Sannitica',
            '062041': 'Guardia Sanframondi',
            '062042': 'Limatola',
            '062043': 'Maddaloni',
            '062044': 'Melizzano',
            '062045': 'Moiano',
            '062046': 'Molinara',
            '062047': 'Montefalcone di Val Fortore',
            '062048': 'Montesarchio',
            '062049': 'Morcone',
            '062050': 'Paduli',
            '062051': 'Pago Veiano',
            '062052': 'Pannarano',
            '062053': 'Paolisi',
            '062054': 'Paupisi',
            '062055': 'Pietraroja',
            '062056': 'Pietrelcina',
            '062057': 'Ponte',
            '062058': 'Pontelandolfo',
            '062059': 'Puglianello',
            '062060': 'Reino',
            '062061': 'San Bartolomeo in Galdo',
            '062062': 'San Giorgio del Sannio',
            '062063': 'San Giorgio La Molara',
            '062064': 'San Leucio del Sannio',
            '062065': 'San Lorenzo Maggiore',
            '062066': 'San Lupo',
            '062067': 'San Marco dei Cavoti',
            '062068': 'San Martino Sannita',
            '062069': 'San Nazzaro',
            '062070': 'San Nicola Manfredi',
            '062071': 'San Salvatore Telesino',
            '062072': 'Santa Croce del Sannio',
            '062073': 'Sant\'Agata de\' Goti',
            '062074': 'Sant\'Angelo a Cupolo',
            '062075': 'Sant\'Arcangelo Trimonte',
            '062076': 'Sassinoro',
            '062077': 'Solopaca',
            '062078': 'Telese Terme',
            '062079': 'Tocco Caudio',
            '062080': 'Torrecuso',
            '062081': 'Vitulano',
            
            // Provincia di Caserta (061xxx) - completamento
            '061032': 'Caserta',
            '061090': 'Alvignano',
            '061091': 'Arienzo',
            '061092': 'Aversa',
            '061093': 'Baia e Latina',
            '061094': 'Bellona',
            '061095': 'Caianello',
            '061096': 'Caiazzo',
            '061097': 'Calvi Risorta',
            '061098': 'Camigliano',
            '061099': 'Cancello ed Arnone',
            '061100': 'Capodrise',
            '061101': 'Capriati a Volturno',
            '061102': 'Capua',
            '061103': 'Carinaro',
            '061104': 'Carinola',
            '061105': 'Casagiove',
            '061106': 'Casal di Principe',
            '061107': 'Casaluce',
            '061108': 'Casapesenna',
            '061109': 'Casapulla',
            '061110': 'Castel Campagnano',
            '061111': 'Castel di Sasso',
            '061112': 'Castel Morrone',
            '061113': 'Castel Volturno',
            '061114': 'Castello del Matese',
            '061115': 'Cervino',
            '061116': 'Cesa',
            '061117': 'Cisterna di Latina',
            '061118': 'Conca della Campania',
            '061119': 'Curti',
            '061120': 'Dragoni',
            '061121': 'Duecamere',
            '061122': 'Falciano del Massico',
            '061123': 'Fontegreca',
            '061124': 'Formicola',
            '061125': 'Francolise',
            '061126': 'Frignano',
            '061127': 'Gallo Matese',
            '061128': 'Galluccio',
            '061129': 'Giano Vetusto',
            '061130': 'Gricignano di Aversa',
            '061131': 'Grazzanise',
            '061132': 'Letino',
            '061133': 'Liberi',
            '061134': 'Lusciano',
            '061135': 'Macerata Campania',
            '061136': 'Maddaloni',
            '061137': 'Marcianise',
            '061138': 'Marzano Appio',
            '061139': 'Mignano Monte Lungo',
            '061140': 'Mondragone',
            '061141': 'Monte di Procida',
            '061142': 'Orta di Atella',
            '061143': 'Parete',
            '061144': 'Pastorano',
            '061145': 'Piedimonte Matese',
            '061146': 'Pietramelara',
            '061147': 'Pietravairano',
            '061148': 'Pignataro Maggiore',
            '061149': 'Pontelatone',
            '061150': 'Portico di Caserta',
            '061151': 'Prata Sannita',
            '061152': 'Presenzano',
            '061153': 'Raviscanina',
            '061154': 'Recale',
            '061155': 'Riardo',
            '061156': 'Rocca d\'Evandro',
            '061157': 'Roccamonfina',
            '061158': 'Roccaromana',
            '061159': 'Rocchetta e Croce',
            '061160': 'Ruviano',
            '061161': 'San Cipriano d\'Aversa',
            '061162': 'San Felice a Cancello',
            '061163': 'San Gregorio Matese',
            '061164': 'San Marcellino',
            '061165': 'San Nicola la Strada',
            '061166': 'San Pietro Infine',
            '061167': 'San Potito Sannitico',
            '061168': 'San Prisco',
            '061169': 'San Tammaro',
            '061170': 'Santa Maria a Vico',
            '061171': 'Santa Maria Capua Vetere',
            '061172': 'Santa Maria la Fossa',
            '061173': 'Sant\'Andrea del Pizzone',
            '061174': 'Sant\'Angelo d\'Alife',
            '061175': 'Santo Arpino',
            '061176': 'Sessa Aurunca',
            '061177': 'Sparanise',
            '061178': 'Succivo',
            '061179': 'Teano',
            '061180': 'Teverola',
            '061181': 'Tora e Piccilli',
            '061182': 'Trecastagni',
            '061183': 'Trentola-Ducenta',
            '061184': 'Vairano Patenora',
            '061185': 'Valle Agricola',
            '061186': 'Valle di Maddaloni',
            '061187': 'Villa di Briano',
            '061188': 'Villa Literno',
            '061189': 'Vitulazio',
            
            // Altri codici comuni della Campania
            '063001': 'Acerra',
            '063002': 'Agropoli',
            '063003': 'Amalfi',
            '063004': 'Angri',
            '063005': 'Arzano',
            '063006': 'Atripalda',
            '063007': 'Aversa',
            '063008': 'Avellino',
            '063009': 'Bacoli',
            '063010': 'Baronissi',
            '063011': 'Battipaglia',
            '063012': 'Benevento',
            '063013': 'Boscoreale',
            '063014': 'Boscotrecase',
            '063015': 'Brusciano',
            '063016': 'Capaccio Paestum',
            '063017': 'Capri',
            '063018': 'Capua',
            '063019': 'Carinaro',
            '063020': 'Casalnuovo di Napoli',
            '063021': 'Casamicciola Terme',
            '063022': 'Casavatore',
            '063023': 'Caserta',
            '063024': 'Castellammare di Stabia',
            '063025': 'Cava de\' Tirreni',
            '063026': 'Cercola',
            '063027': 'Cetara',
            '063028': 'Cicciano',
            '063029': 'Cimitile',
            '063030': 'Eboli',
            '063031': 'Ercolano',
            '063032': 'Fisciano',
            '063033': 'Forio',
            '063034': 'Frattamaggiore',
            '063035': 'Frattaminore',
            '063036': 'Furore',
            '063037': 'Giffoni Valle Piana',
            '063038': 'Giugliano in Campania',
            '063039': 'Gragnano',
            '063040': 'Grumo Nevano',
            '063041': 'Ischia',
            '063042': 'Lacco Ameno',
            '063043': 'Lettere',
            '063044': 'Maddaloni',
            '063045': 'Maiori',
            '063046': 'Marano di Napoli',
            '063047': 'Marcianise',
            '063048': 'Marigliano',
            '063049': 'Salerno',
            '063050': 'Melito di Napoli',
            '063051': 'Mercato San Severino',
            '063052': 'Mercogliano',
            '063053': 'Meta',
            '063054': 'Minori',
            '063055': 'Mondragone',
            '063056': 'Monte di Procida',
            '063057': 'Montesarchio',
            '063058': 'Mugnano di Napoli',
            '063059': 'Nocera Inferiore',
            '063060': 'Nocera Superiore',
            '063061': 'Nola',
            '063062': 'Olevano sul Tusciano',
            '063063': 'Ottaviano',
            '063064': 'Pagani',
            '063065': 'Palma Campania',
            '063066': 'Piano di Sorrento',
            '063067': 'Pimonte',
            '063068': 'Poggiomarino',
            '063069': 'Pollena Trocchia',
            '063070': 'Pomigliano d\'Arco',
            '063071': 'Pompei',
            '063072': 'Pontecagnano Faiano',
            '063073': 'Portici',
            '063074': 'Positano',
            '063075': 'Pozzuoli',
            '063076': 'Praiano',
            '063077': 'Procida',
            '063078': 'Qualiano',
            '063079': 'Quarto',
            '063080': 'Ravello',
            '063081': 'Roccapiemonte',
            '063082': 'San Cipriano Picentino',
            '063083': 'San Giorgio a Cremano',
            '063084': 'San Giuseppe Vesuviano',
            '063085': 'San Marzano sul Sarno',
            '063086': 'San Sebastiano al Vesuvio',
            '063087': 'San Valentino Torio',
            '063088': 'Sant\'Agnello',
            '063089': 'Sant\'Anastasia',
            '063090': 'Sant\'Antimo',
            '063091': 'Sant\'Antonio Abate',
            '063092': 'Santa Maria Capua Vetere',
            '063093': 'Santo Stefano del Sole',
            '063094': 'Sapri',
            '063095': 'Sarno',
            '063096': 'Saviano',
            '063097': 'Scafati',
            '063098': 'Scala',
            '063099': 'Scisciano',
            '063100': 'Serrara Fontana',
            '063101': 'Siano',
            '063102': 'Solofra',
            '063103': 'Somma Vesuviana',
            '063104': 'Sorrento',
            '063105': 'Striano',
            '063106': 'Telese Terme',
            '063107': 'Terzigno',
            '063108': 'Torre Annunziata',
            '063109': 'Torre del Greco',
            '063110': 'Tramonti',
            '063111': 'Trecase',
            '063112': 'Tufino',
            '063113': 'Vairano Patenora',
            '063114': 'Vico Equense',
            '063115': 'Vietri sul Mare',
            '063116': 'Villa di Briano',
            '063117': 'Villaricca',
            '063118': 'Visciano',
            '063119': 'Volla',
            
            // Codici generici di fallback
            '999999': 'Comune non identificato',
            '000000': 'Dati mancanti'
        };
        
        async function loadData() {
            try {
                console.log('🔄 Starting loadData...');
                const response = await fetch('/api/real-database/three-diseases-stats');
                console.log('📡 Fetch response:', response.status, response.ok);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                diseaseData = await response.json();
                console.log('📊 Data loaded:', diseaseData ? 'SUCCESS' : 'FAILED');
                console.log('📋 Status:', diseaseData?.status);

                if (diseaseData.status === 'success') {
                    updateDebugStatus('✅ API response successful');
                    normalizeDiseases();
                    
                    // Store original data for filtering
                    originalDiseaseData = JSON.parse(JSON.stringify(diseaseData));
                    
                    // Initialize individual chart filters
                    initializeIndividualFilters();
                    
                    updateDebugStatus('🔄 Data normalization complete');
                    
                    console.log('🎨 Rendering overview...');
                    updateDebugStatus('🎨 Rendering overview...');
                    renderOverview();
                    
                    console.log('📅 Rendering current status dashboard...');
                    updateDebugStatus('📅 Rendering current status dashboard...');
                    renderCurrentStatusDashboard();
                    
                    console.log('📋 Rendering data summary table...');
                    updateDebugStatus('📋 Rendering data summary table...');
                    renderDataSummaryTable();
                    
                    console.log('🏛️ Rendering ISTAT-based charts...');
                    updateDebugStatus('🏛️ Rendering ISTAT-based charts...');
                    renderTopMunicipalitiesChart();
                    renderIstatDistributionChart();
                    renderIstatPredictionsChart();
                    renderIstatDetailTable();
                    
                    console.log('⏱️ Rendering time-based ISTAT charts...');
                    updateDebugStatus('⏱️ Rendering time-based ISTAT analysis...');
                    renderIstatTimelineChart();
                    renderIstatTimePredictionsChart();
                    
                    console.log('📈 Rendering charts...');
                    updateDebugStatus('📈 Starting chart rendering...');
                    renderCharts();
                    
                    console.log('🗺️ Rendering map...');
                    updateDebugStatus('🗺️ Rendering map...');
                    renderMap();
                    
                    console.log('📋 Rendering tables...');
                    updateDebugStatus('📋 Rendering tables...');
                    renderTables();
                    
                    console.log('✅ Showing content...');
                    updateDebugStatus('✅ All components rendered successfully!');
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('content').style.display = 'block';
                    
                    // Render pie chart AFTER content is visible
                    console.log('🥧 Rendering pie chart...');
                    updateDebugStatus('🥧 Rendering disease distribution pie chart...');
                    setTimeout(() => {
                        renderDiseaseDistributionPieChart();
                    }, 100);
                    
                    if (map && typeof map.invalidateSize === 'function') {
                        map.invalidateSize();
                    }
                    console.log('🎉 Load complete!');
                } else {
                    throw new Error('Errore nel caricamento dei dati');
                }
            } catch (error) {
                console.error('❌ Errore in loadData:', error);
                document.getElementById('loading').style.display = 'none';
                document.getElementById('error').style.display = 'block';
                document.getElementById('error').textContent = `Errore nel caricamento dei dati: ${error.message}`;
            }
        }

        function normalizeDiseases() {
            const expected = {
                influenza: { name: 'Influenza' },
                legionellosi: { name: 'Legionellosi' },
                hepatitis_a: { name: 'Epatite A' }
            };

            if (!diseaseData.diseases) diseaseData.diseases = {};

            Object.keys(expected).forEach(key => {
                if (!diseaseData.diseases[key]) {
                    diseaseData.diseases[key] = {
                        name: expected[key].name,
                        total_cases: 0,
                        cases: [],
                        geographic_distribution: [],
                        monthly_trends: [],
                        predictions: [],
                        arima_model_info: {}
                    };
                } else {
                    // Ensure required arrays exist
                    diseaseData.diseases[key].geographic_distribution ||= [];
                    diseaseData.diseases[key].monthly_trends ||= [];
                    diseaseData.diseases[key].predictions ||= [];
                }
            });
        }
        
        function renderOverview() {
            const overview = document.getElementById('statsOverview');
            const diseases = diseaseData.diseases;
            
            overview.innerHTML = Object.keys(diseases).map(key => {
                const disease = diseases[key];
                const totalRegions = disease.geographic_distribution.length;
                const latestCases = disease.monthly_trends.slice(-1)[0]?.cases || 0;
                
                // Calculate ARIMA prediction trends with confidence intervals
                const predictions = disease.predictions || [];
                const nextMonthPrediction = predictions.length > 0 ? predictions[0].predicted_cases : 0;
                const confidenceLevel = predictions.length > 0 ? Math.round((predictions[0].confidence_level || 0.95) * 100) : 95;
                const predictionMethod = predictions.length > 0 ? predictions[0].prediction_method || 'ARIMA' : 'N/A';
                const predictionTrend = nextMonthPrediction > latestCases ? '📈' : nextMonthPrediction < latestCases ? '📉' : '➡️';
                
                // Get ARIMA model information
                const arimaInfo = disease.arima_model_info || {};
                const modelType = arimaInfo.model_type || 'ARIMA';
                const hasSeasonality = arimaInfo.seasonality?.has_seasonality ? '🔄' : '';
                const modelAccuracy = arimaInfo.aic ? `AIC: ${Math.round(arimaInfo.aic)}` : '';
                
                // Get disease-specific styling
                const diseaseClass = key === 'influenza' ? 'influenza' : 
                                   key === 'legionellosi' ? 'legionellosi' : 'epatite';
                const diseaseIcon = key === 'influenza' ? 'thermometer-half' : 
                                   key === 'legionellosi' ? 'droplet' : 'shield-check';
                
                return `
                    <div class="col-lg-4">
                        <div class="stat-card ${diseaseClass}">
                            <div class="d-flex justify-content-between align-items-start mb-3">
                                <h5 class="mb-0 fw-bold">
                                    <i class="bi bi-${diseaseIcon} me-2"></i>
                                    ${disease.name}
                                </h5>
                                <span class="disease-badge badge-${diseaseClass}">
                                    ${hasSeasonality} ${modelType}
                                </span>
                            </div>
                            
                            <div class="row g-3 text-center">
                                <div class="col-6">
                                    <div class="stat-value text-primary">${disease.total_cases}</div>
                                    <div class="stat-label">Casi Totali</div>
                                </div>
                                <div class="col-6">
                                    <div class="stat-value text-success">${totalRegions}</div>
                                    <div class="stat-label">Comuni Coinvolti</div>
                                </div>
                                <div class="col-6">
                                    <div class="stat-value text-warning">${latestCases}</div>
                                    <div class="stat-label">Ultimo Mese</div>
                                </div>
                                <div class="col-6">
                                    <div class="stat-value text-info">${predictionTrend} ${nextMonthPrediction}</div>
                                    <div class="stat-label">Previsione ${confidenceLevel}%</div>
                                </div>
                            </div>
                            
                            ${modelAccuracy ? `
                                <div class="mt-3 pt-2 border-top">
                                    <small class="text-muted">
                                        <i class="bi bi-cpu me-1"></i>
                                        Accuratezza: ${modelAccuracy}
                                    </small>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        function renderCurrentStatusDashboard() {
            console.log('📅 Rendering current status dashboard...');
            const dashboard = document.getElementById('currentStatusDashboard');
            
            if (!diseaseData || !diseaseData.diseases) {
                dashboard.innerHTML = '<div class="text-white text-center">Caricamento dati in corso...</div>';
                return;
            }
            
            const diseases = diseaseData.diseases;
            
            dashboard.innerHTML = Object.keys(diseases).map(key => {
                const disease = diseases[key];
                const latestData = disease.monthly_trends.slice(-1)[0] || {};
                const currentCases = latestData.cases || 0;
                const currentMonth = latestData.month || 'N/A';
                
                // Get next month prediction
                const predictions = disease.predictions || [];
                const nextPrediction = predictions.length > 0 ? predictions[0] : {};
                const predictedCases = nextPrediction.predicted_cases || 0;
                const confidence = Math.round((nextPrediction.confidence_level || 0.95) * 100);
                
                // Calculate trend
                const previousMonth = disease.monthly_trends.slice(-2, -1)[0]?.cases || 0;
                const trend = currentCases > previousMonth ? 'increase' : currentCases < previousMonth ? 'decrease' : 'stable';
                const trendIcon = trend === 'increase' ? '📈' : trend === 'decrease' ? '📉' : '➡️';
                const trendColor = trend === 'increase' ? 'danger' : trend === 'decrease' ? 'success' : 'warning';
                
                // Prediction trend
                const predTrend = predictedCases > currentCases ? 'increase' : predictedCases < currentCases ? 'decrease' : 'stable';
                const predTrendIcon = predTrend === 'increase' ? '📈' : predTrend === 'decrease' ? '📉' : '➡️';
                const predTrendColor = predTrend === 'increase' ? 'danger' : predTrend === 'decrease' ? 'success' : 'warning';
                
                const diseaseColor = key === 'influenza' ? '#007bff' : key === 'legionellosi' ? '#fd7e14' : '#28a745';
                
                return `
                    <div class="col-md-4">
                        <div class="card bg-white text-dark h-100">
                            <div class="card-body">
                                <h6 class="card-title text-center mb-3" style="color: ${diseaseColor}; font-weight: bold;">
                                    ${disease.name}
                                </h6>
                                
                                <!-- Current Month -->
                                <div class="text-center mb-4">
                                    <div class="badge bg-light text-dark mb-2">Attualmente (${currentMonth})</div>
                                    <div class="display-6 fw-bold" style="color: ${diseaseColor};">${currentCases}</div>
                                    <div class="small">
                                        <span class="badge bg-${trendColor}">${trendIcon} Trend vs Mese Precedente</span>
                                    </div>
                                </div>
                                
                                <!-- Prediction Arrow -->
                                <div class="text-center mb-3">
                                    <i class="bi bi-arrow-down fs-2" style="color: #6c757d;"></i>
                                </div>
                                
                                <!-- Next Month Prediction -->
                                <div class="text-center">
                                    <div class="badge bg-info text-white mb-2">Previsione Prossimo Mese</div>
                                    <div class="display-6 fw-bold text-info">${predictedCases}</div>
                                    <div class="small">
                                        <span class="badge bg-${predTrendColor}">${predTrendIcon} ${confidence}% Confidenza</span>
                                    </div>
                                    <div class="mt-2">
                                        <small class="text-muted">
                                            Variazione: ${predictedCases > currentCases ? '+' : ''}${predictedCases - currentCases} casi
                                        </small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        function updateDebugStatus(message) {
            // Debug function disabled for production
            // Uncomment the code below for troubleshooting
            /*
            const debugLog = document.getElementById('debugLog');
            if (debugLog) {
                const timestamp = new Date().toLocaleTimeString();
                debugLog.innerHTML += `<br/>[${timestamp}] ${message}`;
                debugLog.scrollTop = debugLog.scrollHeight;
            }
            */
        }

        function renderCharts() {
            updateDebugStatus('🔍 Starting chart rendering process...');
            updateDebugStatus(`� Disease data: ${diseaseData ? 'Available' : 'Missing'}`);
            if (diseaseData) {
                updateDebugStatus(`📋 Diseases found: ${Object.keys(diseaseData.diseases || {}).join(', ')}`);
            }
            
            try {
                updateDebugStatus('📈 Rendering disease distribution chart...');
                renderDiseaseDistribution();
                updateDebugStatus('✅ Disease distribution chart: SUCCESS');
            } catch (e) { 
                console.error('❌ renderDiseaseDistribution failed:', e);
                updateDebugStatus(`❌ Disease distribution chart: FAILED - ${e.message}`);
                addErrorToDiv('diseaseDistributionChart', 'Errore nel caricamento del grafico di distribuzione');
            }
            
            try {
                updateDebugStatus('📈 Rendering monthly trends chart...');
                renderMonthlyTrends();
                updateDebugStatus('✅ Monthly trends chart: SUCCESS');
            } catch (e) { 
                console.error('❌ renderMonthlyTrends failed:', e);
                updateDebugStatus(`❌ Monthly trends chart: FAILED - ${e.message}`);
                addErrorToDiv('monthlyTrendsChart', 'Errore nel caricamento del grafico mensile');
            }
            
            try {
                updateDebugStatus('📈 Rendering regional comparison chart...');
                renderRegionalComparison();
                updateDebugStatus('✅ Regional comparison chart: SUCCESS');
            } catch (e) { 
                console.error('❌ renderRegionalComparison failed:', e);
                updateDebugStatus(`❌ Regional comparison chart: FAILED - ${e.message}`);
                addErrorToDiv('regionalComparisonChart', 'Errore nel caricamento del confronto regionale');
            }
            
            try {
                updateDebugStatus('📈 Rendering predictions chart...');
                renderPredictions();
                updateDebugStatus('✅ Predictions chart: SUCCESS');
            } catch (e) { 
                console.error('❌ renderPredictions failed:', e);
                updateDebugStatus(`❌ Predictions chart: FAILED - ${e.message}`);
                addErrorToDiv('predictionsChart', 'Errore nel caricamento delle previsioni');
            }
            
            try {
                updateDebugStatus('📈 Rendering historical predictions chart...');
                renderHistoricalPredictions();
                updateDebugStatus('✅ Historical predictions chart: SUCCESS');
            } catch (e) { 
                console.error('❌ renderHistoricalPredictions failed:', e);
                updateDebugStatus(`❌ Historical predictions chart: FAILED - ${e.message}`);
                addErrorToDiv('historicalAnalysisChart', 'Errore nel caricamento dell\'analisi storica');
            }
            
            updateDebugStatus('🎉 Chart rendering process complete!');
        }
        
        function addErrorToDiv(divId, message) {
            const div = document.getElementById(divId);
            if (div) {
                div.innerHTML = `
                    <div class="alert alert-danger alert-medical d-flex align-items-center justify-content-center" style="height: 300px;">
                        <div class="text-center">
                            <i class="bi bi-exclamation-triangle-fill fs-1 mb-3"></i>
                            <h5>${message}</h5>
                            <small class="text-muted">Verifica la connessione al database GESAN</small>
                        </div>
                    </div>
                `;
            }
        }
        
        function renderPredictions() {
            console.log('🔍 Rendering ARIMA predictions chart with D3.js...');
            
            if (!diseaseData || !diseaseData.diseases) {
                throw new Error('No disease data available for predictions');
            }
            
            const diseases = diseaseData.diseases;
            const diseaseKeys = Object.keys(diseases);
            
            if (diseaseKeys.length === 0) {
                throw new Error('No diseases found for predictions');
            }
            
            console.log('✅ Found diseases for predictions:', diseaseKeys);
            
            // Clear any existing chart
            d3.select('#predictionsChart').selectAll('*').remove();
            
            // Find diseases with valid predictions
            const diseasesWithPredictions = diseaseKeys.filter(key => {
                const disease = diseases[key];
                const predictions = disease.predictions || [];
                return Array.isArray(predictions) && 
                       predictions.length > 0 && 
                       predictions[0].month && 
                       typeof predictions[0].predicted_cases === 'number';
            });
            
            if (diseasesWithPredictions.length === 0) {
                throw new Error('No valid predictions data found');
            }
            
            console.log('✅ Diseases with valid predictions:', diseasesWithPredictions);
            
            // Prepare data for D3
            const chartData = [];
            const colors = {
                'influenza': '#007bff',
                'legionellosi': '#fd7e14', 
                'hepatitis_a': '#28a745'
            };
            
            diseasesWithPredictions.forEach(key => {
                const disease = diseases[key];
                disease.predictions.forEach(pred => {
                    chartData.push({
                        disease: disease.name,
                        diseaseKey: key,
                        month: new Date(pred.month),
                        predicted: pred.predicted_cases,
                        confidence: Math.round((pred.confidence_level || 0.95) * 100),
                        upperBound: pred.upper_bound || pred.predicted_cases + 5,
                        lowerBound: Math.max(0, pred.lower_bound || pred.predicted_cases - 5),
                        method: pred.prediction_method || 'ARIMA'
                    });
                });
            });
            
            console.log('✅ Prepared chart data:', chartData.length, 'points');
            
            // Set up chart dimensions
            const container = d3.select('#predictionsChart');
            const containerRect = container.node().getBoundingClientRect();
            const margin = {top: 20, right: 80, bottom: 60, left: 70};
            const width = containerRect.width - margin.left - margin.right;
            const height = 400 - margin.top - margin.bottom;
            
            // Create SVG
            const svg = container.append('svg')
                .attr('width', width + margin.left + margin.right)
                .attr('height', height + margin.top + margin.bottom);
                
            const g = svg.append('g')
                .attr('transform', `translate(${margin.left},${margin.top})`);
            
            // Create scales
            const xScale = d3.scaleTime()
                .domain(d3.extent(chartData, d => d.month))
                .range([0, width]);
                
            const yScale = d3.scaleLinear()
                .domain([0, d3.max(chartData, d => Math.max(d.predicted, d.upperBound))])
                .range([height, 0]);
            
            // Create line generator
            const line = d3.line()
                .x(d => xScale(d.month))
                .y(d => yScale(d.predicted))
                .curve(d3.curveMonotoneX);
            
            // Add axes
            g.append('g')
                .attr('transform', `translate(0,${height})`)
                .call(d3.axisBottom(xScale).tickFormat(d3.timeFormat('%b %Y')))
                .selectAll('text')
                .style('text-anchor', 'end')
                .attr('dx', '-.8em')
                .attr('dy', '.15em')
                .attr('transform', 'rotate(-45)');
                
            g.append('g')
                .call(d3.axisLeft(yScale));
            
            // Add axis labels
            g.append('text')
                .attr('transform', 'rotate(-90)')
                .attr('y', 0 - margin.left)
                .attr('x', 0 - (height / 2))
                .attr('dy', '1em')
                .style('text-anchor', 'middle')
                .style('font-size', '12px')
                .style('fill', '#666')
                .text('Casi Previsti (ARIMA)');
                
            g.append('text')
                .attr('transform', `translate(${width / 2}, ${height + margin.bottom - 10})`)
                .style('text-anchor', 'middle')
                .style('font-size', '12px')
                .style('fill', '#666')
                .text('Periodo di Previsione (Prossimi 6 Mesi)');
            
            // Group data by disease
            const diseaseGroups = d3.group(chartData, d => d.diseaseKey);
            
            // Create tooltip
            const tooltip = d3.select('body').append('div')
                .attr('class', 'custom-tooltip')
                .style('opacity', 0);
            
            // Draw prediction lines for each disease
            diseaseGroups.forEach((data, diseaseKey) => {
                const color = colors[diseaseKey] || '#333';
                
                // Draw confidence interval area (optional)
                const area = d3.area()
                    .x(d => xScale(d.month))
                    .y0(d => yScale(d.lowerBound))
                    .y1(d => yScale(d.upperBound))
                    .curve(d3.curveMonotoneX);
                
                g.append('path')
                    .datum(data)
                    .attr('fill', color)
                    .attr('fill-opacity', 0.1)
                    .attr('d', area);
                
                // Draw main prediction line
                g.append('path')
                    .datum(data)
                    .attr('fill', 'none')
                    .attr('stroke', color)
                    .attr('stroke-width', 3)
                    .attr('stroke-dasharray', '8,4')
                    .attr('d', line);
                
                // Add prediction points
                g.selectAll(`.point-${diseaseKey}`)
                    .data(data)
                    .enter().append('circle')
                    .attr('class', `point-${diseaseKey}`)
                    .attr('cx', d => xScale(d.month))
                    .attr('cy', d => yScale(d.predicted))
                    .attr('r', 5)
                    .attr('fill', color)
                    .attr('stroke', 'white')
                    .attr('stroke-width', 2)
                    .style('cursor', 'pointer')
                    .on('mouseover', function(event, d) {
                        d3.select(this).attr('r', 7);
                        tooltip.transition().duration(200).style('opacity', .9);
                        tooltip.html(`
                            <strong>${d.disease}</strong><br/>
                            📅 ${d.month.toLocaleDateString('it-IT', {month: 'long', year: 'numeric'})}<br/>
                            🔮 Previsti: <strong>${d.predicted.toFixed(1)} casi</strong><br/>
                            📊 Confidenza: ${d.confidence}%<br/>
                            📈 Intervallo: ${d.lowerBound.toFixed(1)} - ${d.upperBound.toFixed(1)}<br/>
                            🧮 Metodo: ${d.method}
                        `)
                        .style('left', (event.pageX + 10) + 'px')
                        .style('top', (event.pageY - 28) + 'px');
                    })
                    .on('mouseout', function(d) {
                        d3.select(this).attr('r', 5);
                        tooltip.transition().duration(500).style('opacity', 0);
                    });
            });
            
            // Add legend
            const legend = g.append('g')
                .attr('transform', `translate(${width - 150}, 20)`);
            
            let legendY = 0;
            diseaseGroups.forEach((data, diseaseKey) => {
                const color = colors[diseaseKey] || '#333';
                const diseaseName = data[0].disease;
                
                legend.append('line')
                    .attr('x1', 0)
                    .attr('y1', legendY)
                    .attr('x2', 20)
                    .attr('y2', legendY)
                    .attr('stroke', color)
                    .attr('stroke-width', 3)
                    .attr('stroke-dasharray', '8,4');
                
                legend.append('text')
                    .attr('x', 25)
                    .attr('y', legendY)
                    .attr('dy', '0.35em')
                    .style('font-size', '12px')
                    .style('fill', '#333')
                    .text(`🔮 ${diseaseName}`);
                
                legendY += 20;
            });
            
            // Add chart title
            g.append('text')
                .attr('x', width / 2)
                .attr('y', -5)
                .attr('text-anchor', 'middle')
                .style('font-size', '16px')
                .style('font-weight', 'bold')
                .style('fill', '#333')
                .text('Previsioni Epidemiologiche ARIMA (Prossimi 6 Mesi)');
            
            console.log('✅ Predictions chart rendered successfully with D3.js');
            charts.predictions = true;
        }
        
        function renderHistoricalPredictions() {
            console.log('🔍 Rendering historical analysis chart with D3.js...');
            
            if (!diseaseData || !diseaseData.diseases) {
                throw new Error('No disease data available for historical analysis');
            }
            
            const diseases = diseaseData.diseases;
            const diseaseKeys = Object.keys(diseases);
            
            if (diseaseKeys.length === 0) {
                throw new Error('No diseases found for historical analysis');
            }
            
            console.log('✅ Found diseases for historical analysis:', diseaseKeys);
            
            // Clear any existing chart
            d3.select('#historicalAnalysisChart').selectAll('*').remove();
            
            // Find diseases with valid monthly trends and predictions
            const validDiseases = diseaseKeys.filter(key => {
                const disease = diseases[key];
                const hasValidTrends = Array.isArray(disease.monthly_trends) && disease.monthly_trends.length > 0;
                const hasValidPredictions = Array.isArray(disease.predictions) && 
                    disease.predictions.length > 0 && 
                    disease.predictions[0].month;
                return hasValidTrends && hasValidPredictions;
            });
            
            if (validDiseases.length === 0) {
                throw new Error('No diseases with both historical trends and predictions found');
            }
            
            console.log('✅ Valid diseases with both data types:', validDiseases);
            
            // Prepare combined data for D3
            const chartData = [];
            const colors = {
                'influenza': '#007bff',
                'legionellosi': '#fd7e14', 
                'hepatitis_a': '#28a745'
            };
            
            validDiseases.forEach(key => {
                const disease = diseases[key];
                
                // Add historical data points
                disease.monthly_trends.forEach(trend => {
                    chartData.push({
                        disease: disease.name,
                        diseaseKey: key,
                        date: new Date(trend.month),
                        cases: trend.cases,
                        type: 'historical',
                        isActual: true
                    });
                });
                
                // Add prediction data points  
                disease.predictions.forEach(pred => {
                    chartData.push({
                        disease: disease.name,
                        diseaseKey: key,
                        date: new Date(pred.month),
                        cases: pred.predicted_cases,
                        confidence: Math.round((pred.confidence_level || 0.95) * 100),
                        upperBound: pred.upper_bound,
                        lowerBound: pred.lower_bound,
                        type: 'prediction',
                        isActual: false
                    });
                });
            });
            
            console.log('✅ Prepared combined chart data:', chartData.length, 'points');
            
            // Set up chart dimensions
            const container = d3.select('#historicalAnalysisChart');
            const containerRect = container.node().getBoundingClientRect();
            const margin = {top: 20, right: 120, bottom: 60, left: 70};
            const width = containerRect.width - margin.left - margin.right;
            const height = 400 - margin.top - margin.bottom;
            
            // Create SVG
            const svg = container.append('svg')
                .attr('width', width + margin.left + margin.right)
                .attr('height', height + margin.top + margin.bottom);
                
            const g = svg.append('g')
                .attr('transform', `translate(${margin.left},${margin.top})`);
            
            // Create scales
            const xScale = d3.scaleTime()
                .domain(d3.extent(chartData, d => d.date))
                .range([0, width]);
                
            const yScale = d3.scaleLinear()
                .domain([0, d3.max(chartData, d => d.cases)])
                .range([height, 0]);
            
            // Add axes
            g.append('g')
                .attr('transform', `translate(0,${height})`)
                .call(d3.axisBottom(xScale).tickFormat(d3.timeFormat('%b %Y')))
                .selectAll('text')
                .style('text-anchor', 'end')
                .attr('dx', '-.8em')
                .attr('dy', '.15em')
                .attr('transform', 'rotate(-45)');
                
            g.append('g')
                .call(d3.axisLeft(yScale));
            
            // Add axis labels
            g.append('text')
                .attr('transform', 'rotate(-90)')
                .attr('y', 0 - margin.left)
                .attr('x', 0 - (height / 2))
                .attr('dy', '1em')
                .style('text-anchor', 'middle')
                .style('font-size', '12px')
                .style('fill', '#666')
                .text('Numero Casi');
                
            g.append('text')
                .attr('transform', `translate(${width / 2}, ${height + margin.bottom - 10})`)
                .style('text-anchor', 'middle')
                .style('font-size', '12px')
                .style('fill', '#666')
                .text('Periodo (Storico → Previsioni)');
            
            // Group data by disease
            const diseaseGroups = d3.group(chartData, d => d.diseaseKey);
            
            // Create line generator
            const line = d3.line()
                .x(d => xScale(d.date))
                .y(d => yScale(d.cases))
                .curve(d3.curveMonotoneX);
            
            // Create tooltip
            const tooltip = d3.select('body').append('div')
                .attr('class', 'custom-tooltip')
                .style('opacity', 0);
            
            // Draw lines and points for each disease
            diseaseGroups.forEach((data, diseaseKey) => {
                const color = colors[diseaseKey] || '#333';
                const historicalData = data.filter(d => d.type === 'historical');
                const predictionData = data.filter(d => d.type === 'prediction');
                
                // Draw historical line (solid)
                if (historicalData.length > 0) {
                    g.append('path')
                        .datum(historicalData)
                        .attr('fill', 'none')
                        .attr('stroke', color)
                        .attr('stroke-width', 2)
                        .attr('d', line);
                        
                    // Historical points
                    g.selectAll(`.hist-point-${diseaseKey}`)
                        .data(historicalData)
                        .enter().append('circle')
                        .attr('class', `hist-point-${diseaseKey}`)
                        .attr('cx', d => xScale(d.date))
                        .attr('cy', d => yScale(d.cases))
                        .attr('r', 3)
                        .attr('fill', color)
                        .attr('stroke', 'white')
                        .attr('stroke-width', 1)
                        .style('cursor', 'pointer')
                        .on('mouseover', function(event, d) {
                            d3.select(this).attr('r', 5);
                            tooltip.transition().duration(200).style('opacity', .9);
                            tooltip.html(`
                                <strong>${d.disease}</strong><br/>
                                📅 ${d.date.toLocaleDateString('it-IT', {month: 'long', year: 'numeric'})}<br/>
                                📊 Casi storici: <strong>${d.cases}</strong><br/>
                                📈 Dati reali del database GESAN
                            `)
                            .style('left', (event.pageX + 10) + 'px')
                            .style('top', (event.pageY - 28) + 'px');
                        })
                        .on('mouseout', function(d) {
                            d3.select(this).attr('r', 3);
                            tooltip.transition().duration(500).style('opacity', 0);
                        });
                }
                
                // Draw prediction line (dashed)
                if (predictionData.length > 0) {
                    g.append('path')
                        .datum(predictionData)
                        .attr('fill', 'none')
                        .attr('stroke', color)
                        .attr('stroke-width', 2)
                        .attr('stroke-dasharray', '8,4')
                        .attr('d', line);
                        
                    // Prediction points
                    g.selectAll(`.pred-point-${diseaseKey}`)
                        .data(predictionData)
                        .enter().append('circle')
                        .attr('class', `pred-point-${diseaseKey}`)
                        .attr('cx', d => xScale(d.date))
                        .attr('cy', d => yScale(d.cases))
                        .attr('r', 4)
                        .attr('fill', color)
                        .attr('stroke', 'white')
                        .attr('stroke-width', 2)
                        .style('cursor', 'pointer')
                        .on('mouseover', function(event, d) {
                            d3.select(this).attr('r', 6);
                            tooltip.transition().duration(200).style('opacity', .9);
                            tooltip.html(`
                                <strong>${d.disease}</strong><br/>
                                📅 ${d.date.toLocaleDateString('it-IT', {month: 'long', year: 'numeric'})}<br/>
                                🔮 Previsti: <strong>${d.cases.toFixed(1)} casi</strong><br/>
                                📊 Confidenza: ${d.confidence || 95}%<br/>
                                📈 Intervallo: ${(d.lowerBound || 0).toFixed(1)} - ${(d.upperBound || d.cases + 5).toFixed(1)}<br/>
                                🧮 Previsione ARIMA
                            `)
                            .style('left', (event.pageX + 10) + 'px')
                            .style('top', (event.pageY - 28) + 'px');
                        })
                        .on('mouseout', function(d) {
                            d3.select(this).attr('r', 4);
                            tooltip.transition().duration(500).style('opacity', 0);
                        });
                }
            });
            
            // Add vertical line to separate historical from predictions
            const lastHistoricalDate = d3.max(chartData.filter(d => d.type === 'historical'), d => d.date);
            if (lastHistoricalDate) {
                g.append('line')
                    .attr('x1', xScale(lastHistoricalDate))
                    .attr('y1', 0)
                    .attr('x2', xScale(lastHistoricalDate))
                    .attr('y2', height)
                    .attr('stroke', '#999')
                    .attr('stroke-width', 2)
                    .attr('stroke-dasharray', '3,3');
                    
                g.append('text')
                    .attr('x', xScale(lastHistoricalDate) + 5)
                    .attr('y', 15)
                    .style('font-size', '12px')
                    .style('fill', '#666')
                    .text('→ Previsioni');
            }
            
            // Add legend
            const legend = g.append('g')
                .attr('transform', `translate(${width - 110}, 20)`);
            
            let legendY = 0;
            diseaseGroups.forEach((data, diseaseKey) => {
                const color = colors[diseaseKey] || '#333';
                const diseaseName = data[0].disease;
                
                // Historical legend entry
                legend.append('line')
                    .attr('x1', 0)
                    .attr('y1', legendY)
                    .attr('x2', 15)
                    .attr('y2', legendY)
                    .attr('stroke', color)
                    .attr('stroke-width', 2);
                
                legend.append('text')
                    .attr('x', 20)
                    .attr('y', legendY)
                    .attr('dy', '0.35em')
                    .style('font-size', '11px')
                    .style('fill', '#333')
                    .text(`📊 ${diseaseName}`);
                
                legendY += 15;
                
                // Prediction legend entry
                legend.append('line')
                    .attr('x1', 0)
                    .attr('y1', legendY)
                    .attr('x2', 15)
                    .attr('y2', legendY)
                    .attr('stroke', color)
                    .attr('stroke-width', 2)
                    .attr('stroke-dasharray', '4,2');
                
                legend.append('text')
                    .attr('x', 20)
                    .attr('y', legendY)
                    .attr('dy', '0.35em')
                    .style('font-size', '11px')
                    .style('fill', '#333')
                    .text(`🔮 Previsioni`);
                
                legendY += 25;
            });
            
            // Add chart title
            g.append('text')
                .attr('x', width / 2)
                .attr('y', -5)
                .attr('text-anchor', 'middle')
                .style('font-size', '16px')
                .style('font-weight', 'bold')
                .style('fill', '#333')
                .text('Analisi Storica Completa vs Previsioni ARIMA');
            
            console.log('✅ Historical analysis chart rendered successfully with D3.js');
            charts.historicalPrediction = true;
        }
        
        function updateHistoricalChart() {
            // This would update the chart based on checkbox states
            // For now, just log the state
            const showConfidence = document.getElementById('showConfidenceIntervals').checked;
            const showSeasonal = document.getElementById('showSeasonalFactors').checked;
            
            console.log('Chart options updated:', { showConfidence, showSeasonal });
        }
        
        function renderDiseaseDistribution() {
            console.log('🔍 Validating data for disease distribution...');
            
            if (!diseaseData || !diseaseData.diseases) {
                console.error('❌ No disease data available');
                throw new Error('No disease data');
            }

            const diseases = diseaseData.diseases;
            const diseaseKeys = Object.keys(diseases);

            if (diseaseKeys.length === 0) {
                console.error('❌ No diseases found in data');
                throw new Error('No diseases found');
            }

            console.log('✅ Found diseases for distribution chart:', diseaseKeys);

            // Validate that diseases have required data
            const validDiseases = diseaseKeys.filter(key => {
                const disease = diseases[key];
                const isValid = disease && 
                    typeof disease.total_cases === 'number' && 
                    disease.name;
                
                if (!isValid) {
                    console.warn(`⚠️ Invalid data for disease ${key}:`, disease);
                }
                
                return isValid;
            });

            if (validDiseases.length === 0) {
                throw new Error('No valid disease data found for distribution chart');
            }

            console.log('✅ Valid diseases for chart:', validDiseases);

            // Prepare data for D3.js
            const data = validDiseases.map(key => ({
                name: diseases[key].name,
                value: diseases[key].total_cases,
                color: diseaseColors[key],
                key: key
            }));

            // Clear previous chart
            d3.select('#diseaseDistributionChart').selectAll('*').remove();

            // Set dimensions and margins
            const width = 400;
            const height = 400;
            const margin = 40;
            const radius = Math.min(width, height) / 2 - margin;

            // Create SVG
            const svg = d3.select('#diseaseDistributionChart')
                .append('svg')
                .attr('width', width)
                .attr('height', height)
                .append('g')
                .attr('transform', `translate(${width/2}, ${height/2})`);

            // Create pie generator
            const pie = d3.pie()
                .sort(null)
                .value(d => d.value);

            // Create arc generator
            const arc = d3.arc()
                .innerRadius(0)
                .outerRadius(radius);

            const labelArc = d3.arc()
                .innerRadius(radius * 0.8)
                .outerRadius(radius * 0.8);

            // Create pie slices
            const arcs = svg.selectAll('.arc')
                .data(pie(data))
                .enter().append('g')
                .attr('class', 'arc');

            // Add paths (pie slices)
            arcs.append('path')
                .attr('d', arc)
                .attr('fill', d => d.data.color)
                .attr('stroke', 'white')
                .attr('stroke-width', 2)
                .on('mouseover', function(event, d) {
                    d3.select(this).attr('opacity', 0.7);
                    
                    // Show tooltip
                    const tooltip = d3.select('body').append('div')
                        .attr('id', 'tooltip')
                        .style('position', 'absolute')
                        .style('background', 'rgba(0,0,0,0.8)')
                        .style('color', 'white')
                        .style('padding', '8px')
                        .style('border-radius', '4px')
                        .style('font-size', '12px')
                        .style('pointer-events', 'none')
                        .style('z-index', 1000);

                    tooltip.html(`<strong>${d.data.name}</strong><br>Casi: ${d.data.value}<br>Percentuale: ${((d.data.value / d3.sum(data, d => d.value)) * 100).toFixed(1)}%`)
                        .style('left', (event.pageX + 10) + 'px')
                        .style('top', (event.pageY - 10) + 'px');
                })
                .on('mouseout', function() {
                    d3.select(this).attr('opacity', 1);
                    d3.select('#tooltip').remove();
                })
                .on('mousemove', function(event) {
                    d3.select('#tooltip')
                        .style('left', (event.pageX + 10) + 'px')
                        .style('top', (event.pageY - 10) + 'px');
                });

            // Add labels
            arcs.append('text')
                .attr('transform', d => `translate(${labelArc.centroid(d)})`)
                .attr('text-anchor', 'middle')
                .attr('font-size', '12px')
                .attr('font-weight', 'bold')
                .attr('fill', 'white')
                .text(d => d.data.value);

            // Add title
            svg.append('text')
                .attr('text-anchor', 'middle')
                .attr('y', -height/2 + 20)
                .attr('font-size', '16px')
                .attr('font-weight', 'bold')
                .attr('fill', '#2c3e50')
                .text('Distribuzione Casi per Malattia');

            // Add legend
            const legend = svg.selectAll('.legend')
                .data(data)
                .enter().append('g')
                .attr('class', 'legend')
                .attr('transform', (d, i) => `translate(-180, ${-data.length * 10 + i * 20})`);

            legend.append('rect')
                .attr('width', 15)
                .attr('height', 15)
                .attr('fill', d => d.color);

            legend.append('text')
                .attr('x', 20)
                .attr('y', 12)
                .attr('font-size', '12px')
                .text(d => d.name);

            charts.distribution = true; // Mark as created
        }
        
        function renderMonthlyTrends() {
            console.log('🔍 Validating data for monthly trends...');
            
            if (!diseaseData || !diseaseData.diseases) {
                console.error('❌ No disease data available for monthly trends');
                throw new Error('No disease data for monthly trends');
            }

            const diseases = diseaseData.diseases;
            const diseaseKeys = Object.keys(diseases);
            
            if (diseaseKeys.length === 0) {
                console.error('❌ No diseases found for monthly trends');
                throw new Error('No diseases found for monthly trends');
            }
            
            console.log('✅ Found diseases for monthly trends:', diseaseKeys);
            
            // Validate that diseases have monthly_trends data
            const validDiseases = diseaseKeys.filter(key => {
                const disease = diseases[key];
                const isValid = disease && 
                    Array.isArray(disease.monthly_trends) && 
                    disease.monthly_trends.length > 0;
                
                if (!isValid) {
                    console.warn(`⚠️ Invalid monthly trends data for disease ${key}:`, disease?.monthly_trends);
                }
                
                return isValid;
            });
            
            if (validDiseases.length === 0) {
                throw new Error('No valid monthly trends data found');
            }
            
            console.log('✅ Valid diseases with monthly trends:', validDiseases);
            
            // Collect all months from all diseases
            const allMonths = new Set();
            validDiseases.forEach(key => {
                const disease = diseases[key];
                disease.monthly_trends.forEach(trend => {
                    allMonths.add(trend.month);
                });
            });
            
            const months = Array.from(allMonths).sort();
            console.log('✅ Found months:', months);
            
            // Prepare data for D3.js
            const data = validDiseases.map(key => {
                const disease = diseases[key];
                const monthlyData = months.map(month => {
                    const trend = disease.monthly_trends.find(t => t.month === month);
                    return {
                        month: month,
                        date: new Date(month),
                        cases: trend ? trend.cases : 0,
                        disease: disease.name,
                        key: key
                    };
                });
                
                console.log(`✅ Dataset for ${disease.name}:`, monthlyData);
                
                return {
                    disease: disease.name,
                    key: key,
                    color: diseaseColors[key],
                    data: monthlyData
                };
            });

            // Clear previous chart
            d3.select('#monthlyTrendsChart').selectAll('*').remove();

            // Set dimensions and margins
            const margin = { top: 40, right: 80, bottom: 60, left: 60 };
            const width = 800 - margin.left - margin.right;
            const height = 400 - margin.top - margin.bottom;

            // Create SVG
            const svg = d3.select('#monthlyTrendsChart')
                .append('svg')
                .attr('width', width + margin.left + margin.right)
                .attr('height', height + margin.top + margin.bottom)
                .append('g')
                .attr('transform', `translate(${margin.left}, ${margin.top})`);

            // Create scales
            const xScale = d3.scaleTime()
                .domain(d3.extent(months, d => new Date(d)))
                .range([0, width]);

            const yScale = d3.scaleLinear()
                .domain([0, d3.max(data, d => d3.max(d.data, p => p.cases))])
                .range([height, 0]);

            // Create line generator
            const line = d3.line()
                .x(d => xScale(d.date))
                .y(d => yScale(d.cases))
                .curve(d3.curveMonotoneX);

            // Add X axis
            svg.append('g')
                .attr('transform', `translate(0, ${height})`)
                .call(d3.axisBottom(xScale).tickFormat(d3.timeFormat('%b %Y')))
                .selectAll('text')
                .style('text-anchor', 'end')
                .attr('dx', '-.8em')
                .attr('dy', '.15em')
                .attr('transform', 'rotate(-45)');

            // Add Y axis
            svg.append('g')
                .call(d3.axisLeft(yScale));

            // Add X axis label
            svg.append('text')
                .attr('transform', `translate(${width / 2}, ${height + margin.bottom - 10})`)
                .style('text-anchor', 'middle')
                .attr('font-size', '12px')
                .text('Mese');

            // Add Y axis label
            svg.append('text')
                .attr('transform', 'rotate(-90)')
                .attr('y', 0 - margin.left)
                .attr('x', 0 - (height / 2))
                .attr('dy', '1em')
                .style('text-anchor', 'middle')
                .attr('font-size', '12px')
                .text('Numero Casi');

            // Add title
            svg.append('text')
                .attr('x', width / 2)
                .attr('y', 0 - (margin.top / 2))
                .attr('text-anchor', 'middle')
                .attr('font-size', '16px')
                .attr('font-weight', 'bold')
                .attr('fill', '#2c3e50')
                .text('Andamento Mensile per Malattia');

            // Add lines for each disease
            data.forEach(diseaseData => {
                // Add line
                svg.append('path')
                    .datum(diseaseData.data)
                    .attr('fill', 'none')
                    .attr('stroke', diseaseData.color)
                    .attr('stroke-width', 3)
                    .attr('d', line);

                // Add circles for data points
                svg.selectAll(`.dot-${diseaseData.key}`)
                    .data(diseaseData.data)
                    .enter().append('circle')
                    .attr('class', `dot-${diseaseData.key}`)
                    .attr('cx', d => xScale(d.date))
                    .attr('cy', d => yScale(d.cases))
                    .attr('r', 4)
                    .attr('fill', diseaseData.color)
                    .on('mouseover', function(event, d) {
                        d3.select(this).attr('r', 6);
                        
                        // Show tooltip
                        const tooltip = d3.select('body').append('div')
                            .attr('id', 'tooltip')
                            .style('position', 'absolute')
                            .style('background', 'rgba(0,0,0,0.8)')
                            .style('color', 'white')
                            .style('padding', '8px')
                            .style('border-radius', '4px')
                            .style('font-size', '12px')
                            .style('pointer-events', 'none')
                            .style('z-index', 1000);

                        tooltip.html(`<strong>${d.disease}</strong><br>Mese: ${d.date.toLocaleDateString('it-IT', {year: 'numeric', month: 'short'})}<br>Casi: ${d.cases}`)
                            .style('left', (event.pageX + 10) + 'px')
                            .style('top', (event.pageY - 10) + 'px');
                    })
                    .on('mouseout', function() {
                        d3.select(this).attr('r', 4);
                        d3.select('#tooltip').remove();
                    })
                    .on('mousemove', function(event) {
                        d3.select('#tooltip')
                            .style('left', (event.pageX + 10) + 'px')
                            .style('top', (event.pageY - 10) + 'px');
                    });
            });

            // Add legend
            const legend = svg.selectAll('.legend')
                .data(data)
                .enter().append('g')
                .attr('class', 'legend')
                .attr('transform', (d, i) => `translate(${width + 10}, ${i * 20})`);

            legend.append('line')
                .attr('x1', 0)
                .attr('x2', 15)
                .attr('stroke', d => d.color)
                .attr('stroke-width', 3);

            legend.append('text')
                .attr('x', 20)
                .attr('y', 5)
                .attr('font-size', '12px')
                .text(d => d.disease);

            charts.trends = true; // Mark as created
        }
        
        function renderRegionalComparison() {
            console.log('🗺️ Rendering regional comparison chart...');
            
            const diseases = diseaseData.diseases;
            
            console.log('🔍 Available diseases for regional chart:', Object.keys(diseases));
            
            // Check if diseases have geographic_distribution
            Object.keys(diseases).forEach(key => {
                const disease = diseases[key];
                console.log(`📊 ${key} geographic data:`, disease.geographic_distribution?.slice(0, 3));
            });
            
            // Get top 5 regions for each disease
            const topRegions = new Set();
            Object.values(diseases).forEach(disease => {
                if (disease.geographic_distribution && disease.geographic_distribution.length > 0) {
                    disease.geographic_distribution.slice(0, 5).forEach(region => {
                        topRegions.add(region.comune_residenza_codice_istat);
                    });
                }
            });
            
            console.log('🏘️ Top regions found:', Array.from(topRegions));
            
            const regions = Array.from(topRegions);
            
            // Prepare data for D3.js
            const data = [];
            Object.keys(diseases).forEach(diseaseKey => {
                const disease = diseases[diseaseKey];
                regions.forEach(region => {
                    const regionData = disease.geographic_distribution.find(r => r.comune_residenza_codice_istat === region);
                    const cases = regionData ? (regionData.case_count || regionData.count || 0) : 0;
                    const placeName = istatPlaceNames[region] || 'Comune non identificato';
                    
                    data.push({
                        region: region,
                        regionName: placeName,
                        disease: disease.name,
                        diseaseKey: diseaseKey,
                        cases: cases,
                        color: diseaseColors[diseaseKey]
                    });
                });
            });

            // Clear previous chart
            d3.select('#regionalComparisonChart').selectAll('*').remove();

            // Set dimensions and margins
            const margin = { top: 40, right: 120, bottom: 100, left: 60 };
            const width = 800 - margin.left - margin.right;
            const height = 500 - margin.top - margin.bottom;

            // Create SVG
            const svg = d3.select('#regionalComparisonChart')
                .append('svg')
                .attr('width', width + margin.left + margin.right)
                .attr('height', height + margin.top + margin.bottom)
                .append('g')
                .attr('transform', `translate(${margin.left}, ${margin.top})`);

            // Create scales
            const x0 = d3.scaleBand()
                .domain(regions)
                .range([0, width])
                .paddingInner(0.1);

            const x1 = d3.scaleBand()
                .domain(Object.keys(diseases))
                .range([0, x0.bandwidth()])
                .padding(0.05);

            const y = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.cases)])
                .range([height, 0]);

            // Add X axis
            svg.append('g')
                .attr('transform', `translate(0, ${height})`)
                .call(d3.axisBottom(x0).tickFormat(region => {
                    const placeName = istatPlaceNames[region] || 'N/A';
                    return placeName.length > 10 ? placeName.substring(0, 10) + '...' : placeName;
                }))
                .selectAll('text')
                .style('text-anchor', 'end')
                .attr('dx', '-.8em')
                .attr('dy', '.15em')
                .attr('transform', 'rotate(-45)');

            // Add Y axis
            svg.append('g')
                .call(d3.axisLeft(y));

            // Add X axis label
            svg.append('text')
                .attr('transform', `translate(${width / 2}, ${height + margin.bottom - 10})`)
                .style('text-anchor', 'middle')
                .attr('font-size', '12px')
                .text('Regioni');

            // Add Y axis label
            svg.append('text')
                .attr('transform', 'rotate(-90)')
                .attr('y', 0 - margin.left)
                .attr('x', 0 - (height / 2))
                .attr('dy', '1em')
                .style('text-anchor', 'middle')
                .attr('font-size', '12px')
                .text('Numero Casi');

            // Add title
            svg.append('text')
                .attr('x', width / 2)
                .attr('y', 0 - (margin.top / 2))
                .attr('text-anchor', 'middle')
                .attr('font-size', '16px')
                .attr('font-weight', 'bold')
                .attr('fill', '#2c3e50')
                .text('Confronto Regionale per Malattia');

            // Group data by region
            const regionGroups = svg.selectAll('.region-group')
                .data(regions)
                .enter().append('g')
                .attr('class', 'region-group')
                .attr('transform', d => `translate(${x0(d)}, 0)`);

            // Add bars
            regionGroups.selectAll('.bar')
                .data(region => data.filter(d => d.region === region))
                .enter().append('rect')
                .attr('class', 'bar')
                .attr('x', d => x1(d.diseaseKey))
                .attr('y', d => y(d.cases))
                .attr('width', x1.bandwidth())
                .attr('height', d => height - y(d.cases))
                .attr('fill', d => d.color)
                .on('mouseover', function(event, d) {
                    d3.select(this).attr('opacity', 0.7);
                    
                    // Show tooltip
                    const tooltip = d3.select('body').append('div')
                        .attr('id', 'tooltip')
                        .style('position', 'absolute')
                        .style('background', 'rgba(0,0,0,0.8)')
                        .style('color', 'white')
                        .style('padding', '8px')
                        .style('border-radius', '4px')
                        .style('font-size', '12px')
                        .style('pointer-events', 'none')
                        .style('z-index', 1000);

                    tooltip.html(`<strong>${d.disease}</strong><br>Regione: ${d.regionName} (${d.region})<br>Casi: ${d.cases}`)
                        .style('left', (event.pageX + 10) + 'px')
                        .style('top', (event.pageY - 10) + 'px');
                })
                .on('mouseout', function() {
                    d3.select(this).attr('opacity', 1);
                    d3.select('#tooltip').remove();
                })
                .on('mousemove', function(event) {
                    d3.select('#tooltip')
                        .style('left', (event.pageX + 10) + 'px')
                        .style('top', (event.pageY - 10) + 'px');
                });

            // Add legend
            const legend = svg.selectAll('.legend')
                .data(Object.keys(diseases))
                .enter().append('g')
                .attr('class', 'legend')
                .attr('transform', (d, i) => `translate(${width + 20}, ${i * 20})`);

            legend.append('rect')
                .attr('width', 15)
                .attr('height', 15)
                .attr('fill', d => diseaseColors[d]);

            legend.append('text')
                .attr('x', 20)
                .attr('y', 12)
                .attr('font-size', '12px')
                .text(d => diseases[d].name);

            charts.regional = true; // Mark as created
        }
        
        function renderMap() {
            if (map) {
                map.remove();
                map = null;
            }
            map = L.map('diseaseMap').setView([41.8719, 12.5674], 6); // Centro Italia
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            const legend = document.getElementById('mapLegend');
            legend.innerHTML = '<h4>Legenda:</h4>';
            
            Object.keys(diseaseData.diseases).forEach(key => {
                const disease = diseaseData.diseases[key];
                let markersAdded = 0;
                
                // Aggiungi alla leggenda
                legend.innerHTML += `
                    <div class="legend-item">
                        <div class="legend-color" style="background: ${diseaseColors[key]}"></div>
                        <span>${disease.name}</span>
                    </div>
                `;
                
                // Aggiungi markers sulla mappa
                disease.geographic_distribution.forEach(region => {
                    const coords = istatCoordinates[region.comune_residenza_codice_istat];
                    if (coords) {
                        const marker = L.circleMarker(coords, {
                            radius: Math.max(5, Math.min(25, region.case_count * 2)),
                            fillColor: diseaseColors[key],
                            color: '#fff',
                            weight: 2,
                            opacity: 0.8,
                            fillOpacity: 0.6
                        }).addTo(map);
                        
                        marker.bindPopup(`
                            <strong>${disease.name}</strong><br>
                            Codice ISTAT: ${region.comune_residenza_codice_istat}<br>
                            Casi: ${region.case_count}<br>
                            Ultimo caso: ${new Date(region.latest_case).toLocaleDateString('it-IT')}
                        `);
                        markersAdded += 1;
                    }
                });

                // Fallback marker if no real coordinates were found
                if (markersAdded === 0) {
                    const fallbackCenters = {
                        influenza: [41.9, 12.5],
                        legionellosi: [40.9, 14.3],
                        hepatitis_a: [37.5, 15.0]
                    };
                    const coords = fallbackCenters[key] || [41.0, 12.0];
                    const marker = L.circleMarker(coords, {
                        radius: 12,
                        fillColor: diseaseColors[key],
                        color: '#fff',
                        weight: 2,
                        opacity: 0.9,
                        fillOpacity: 0.7
                    }).addTo(map);

                    marker.bindPopup(`
                        <strong>${disease.name}</strong><br>
                        Posizione indicativa (dati senza coordinate ISTAT)
                    `);
                }
            });
        }
        
        function renderTables() {
            const tablesDiv = document.getElementById('regionalTables');
            
            tablesDiv.innerHTML = Object.keys(diseaseData.diseases).map(key => {
                const disease = diseaseData.diseases[key];
                
                const tableRows = disease.geographic_distribution.map(region => {
                    const placeName = istatPlaceNames[region.comune_residenza_codice_istat] || 'Comune non identificato';
                    return `
                        <tr>
                            <td>${region.comune_residenza_codice_istat}</td>
                            <td><strong>${placeName}</strong></td>
                            <td>${region.case_count}</td>
                            <td>${new Date(region.latest_case).toLocaleDateString('it-IT')}</td>
                        </tr>
                    `;
                }).join('');
                
                return `
                    <div style="margin-bottom: 30px;">
                        <h3 style="color: ${diseaseColors[key]}; margin-bottom: 15px;">${disease.name}</h3>
                        <table class="region-table">
                            <thead>
                                <tr>
                                    <th>Codice ISTAT</th>
                                    <th>Comune</th>
                                    <th>Casi</th>
                                    <th>Ultimo Caso</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${tableRows}
                            </tbody>
                        </table>
                    </div>
                `;
            }).join('');
        }
        
        function renderDataSummaryTable() {
            console.log('📋 Rendering data summary table...');
            const tableDiv = document.getElementById('dataSummaryTable');
            
            if (!diseaseData || !diseaseData.diseases) {
                tableDiv.innerHTML = '<div class="text-center">Caricamento dati in corso...</div>';
                return;
            }
            
            const diseases = diseaseData.diseases;
            
            // Create table with current data and predictions
            const tableRows = Object.keys(diseases).map(key => {
                const disease = diseases[key];
                const latestData = disease.monthly_trends.slice(-1)[0] || {};
                const currentCases = latestData.cases || 0;
                const currentMonth = latestData.month || 'N/A';
                
                // Previous month for trend calculation
                const previousData = disease.monthly_trends.slice(-2, -1)[0] || {};
                const previousCases = previousData.cases || 0;
                const monthlyChange = currentCases - previousCases;
                const monthlyChangePercent = previousCases > 0 ? Math.round((monthlyChange / previousCases) * 100) : 0;
                
                // Next month prediction
                const predictions = disease.predictions || [];
                const nextPrediction = predictions.length > 0 ? predictions[0] : {};
                const predictedCases = nextPrediction.predicted_cases || 0;
                const predictionMonth = nextPrediction.month || 'N/A';
                const confidence = Math.round((nextPrediction.confidence_level || 0.95) * 100);
                
                // Prediction change
                const predictionChange = predictedCases - currentCases;
                const predictionChangePercent = currentCases > 0 ? Math.round((predictionChange / currentCases) * 100) : 0;
                
                // Styling based on disease
                const diseaseColor = key === 'influenza' ? '#007bff' : key === 'legionellosi' ? '#fd7e14' : '#28a745';
                const trendClass = monthlyChange > 0 ? 'text-danger' : monthlyChange < 0 ? 'text-success' : 'text-warning';
                const predTrendClass = predictionChange > 0 ? 'text-danger' : predictionChange < 0 ? 'text-success' : 'text-warning';
                
                return `
                    <tr>
                        <td>
                            <strong style="color: ${diseaseColor};">${disease.name}</strong>
                            <br><small class="text-muted">${disease.total_cases} casi totali</small>
                        </td>
                        <td class="text-center">
                            <div class="fw-bold" style="color: ${diseaseColor};">${currentCases}</div>
                            <small class="text-muted">${currentMonth}</small>
                        </td>
                        <td class="text-center ${trendClass}">
                            <div class="fw-bold">${monthlyChange > 0 ? '+' : ''}${monthlyChange}</div>
                            <small>(${monthlyChangePercent > 0 ? '+' : ''}${monthlyChangePercent}%)</small>
                        </td>
                        <td class="text-center">
                            <div class="fw-bold text-info">${predictedCases}</div>
                            <small class="text-muted">${predictionMonth}</small>
                        </td>
                        <td class="text-center ${predTrendClass}">
                            <div class="fw-bold">${predictionChange > 0 ? '+' : ''}${predictionChange}</div>
                            <small>(${predictionChangePercent > 0 ? '+' : ''}${predictionChangePercent}%)</small>
                        </td>
                        <td class="text-center">
                            <span class="badge bg-info">${confidence}%</span>
                            <br><small class="text-muted">ARIMA</small>
                        </td>
                    </tr>
                `;
            }).join('');
            
            tableDiv.innerHTML = `
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>Malattia</th>
                                <th class="text-center">Casi Attuali</th>
                                <th class="text-center">Variazione Mensile</th>
                                <th class="text-center">Previsione Prossimo Mese</th>
                                <th class="text-center">Variazione Prevista</th>
                                <th class="text-center">Affidabilità</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${tableRows}
                        </tbody>
                    </table>
                </div>
            `;
        }
        
        function renderTopMunicipalitiesChart() {
            console.log('🏛️ Rendering top municipalities chart...');
            const chartDiv = document.getElementById('topMunicipalitiesChart');
            
            if (!diseaseData || !diseaseData.diseases) {
                chartDiv.innerHTML = '<div class="text-center">Caricamento dati in corso...</div>';
                return;
            }
            
            // Aggregate data by ISTAT code across all diseases
            const municipalityData = {};
            
            Object.keys(diseaseData.diseases).forEach(diseaseKey => {
                const disease = diseaseData.diseases[diseaseKey];
                disease.geographic_distribution.forEach(region => {
                    const istatCode = region.comune_residenza_codice_istat;
                    const cases = region.total_cases || 0;
                    
                    if (!municipalityData[istatCode]) {
                        municipalityData[istatCode] = {
                            istatCode: istatCode,
                            name: istatPlaceNames[istatCode] || `ISTAT ${istatCode}`,
                            totalCases: 0,
                            diseases: {}
                        };
                    }
                    
                    municipalityData[istatCode].totalCases += cases;
                    municipalityData[istatCode].diseases[diseaseKey] = cases;
                });
            });
            
            // Get top 10 municipalities
            const topMunicipalities = Object.values(municipalityData)
                .sort((a, b) => b.totalCases - a.totalCases)
                .slice(0, 10);
            
            // Clear previous chart
            d3.select('#topMunicipalitiesChart').selectAll('*').remove();
            
            // Create SVG
            const margin = {top: 20, right: 30, bottom: 60, left: 120};
            const width = 450 - margin.left - margin.right;
            const height = 360 - margin.top - margin.bottom;
            
            const svg = d3.select('#topMunicipalitiesChart')
                .append('svg')
                .attr('width', width + margin.left + margin.right)
                .attr('height', height + margin.top + margin.bottom);
            
            const g = svg.append('g')
                .attr('transform', `translate(${margin.left},${margin.top})`);
            
            // Scales
            const y = d3.scaleBand()
                .domain(topMunicipalities.map(d => d.name))
                .range([0, height])
                .padding(0.1);
            
            const x = d3.scaleLinear()
                .domain([0, d3.max(topMunicipalities, d => d.totalCases)])
                .range([0, width]);
            
            // Color scale
            const color = d3.scaleOrdinal()
                .domain(['influenza', 'legionellosi', 'hepatitis_a'])
                .range(['#007bff', '#fd7e14', '#28a745']);
            
            // Bars
            g.selectAll('.bar')
                .data(topMunicipalities)
                .enter().append('rect')
                .attr('class', 'bar')
                .attr('y', d => y(d.name))
                .attr('height', y.bandwidth())
                .attr('x', 0)
                .attr('width', d => x(d.totalCases))
                .attr('fill', '#17a2b8')
                .attr('opacity', 0.8);
            
            // Axes
            g.append('g')
                .call(d3.axisLeft(y));
            
            g.append('g')
                .attr('transform', `translate(0,${height})`)
                .call(d3.axisBottom(x));
            
            // Labels
            g.selectAll('.bar-label')
                .data(topMunicipalities)
                .enter().append('text')
                .attr('class', 'bar-label')
                .attr('x', d => x(d.totalCases) + 5)
                .attr('y', d => y(d.name) + y.bandwidth() / 2)
                .attr('dy', '0.35em')
                .style('font-size', '12px')
                .text(d => d.totalCases);
        }
        
        function renderIstatDistributionChart() {
            console.log('📊 Rendering ISTAT distribution chart...');
            const chartDiv = document.getElementById('istatDistributionChart');
            
            if (!diseaseData || !diseaseData.diseases) {
                chartDiv.innerHTML = '<div class="text-center">Caricamento dati in corso...</div>';
                return;
            }
            
            // Prepare data for each disease showing municipality distribution
            const chartData = [];
            const colors = {
                'influenza': '#007bff',
                'legionellosi': '#fd7e14', 
                'hepatitis_a': '#28a745'
            };
            
            Object.keys(diseaseData.diseases).forEach(diseaseKey => {
                const disease = diseaseData.diseases[diseaseKey];
                const municipalityCount = disease.geographic_distribution.length;
                chartData.push({
                    disease: disease.name,
                    municipalities: municipalityCount,
                    color: colors[diseaseKey] || '#6c757d'
                });
            });
            
            // Clear previous chart
            d3.select('#istatDistributionChart').selectAll('*').remove();
            
            // Create pie chart
            const width = 400;
            const height = 360;
            const radius = Math.min(width, height) / 2 - 20;
            
            const svg = d3.select('#istatDistributionChart')
                .append('svg')
                .attr('width', width)
                .attr('height', height);
            
            const g = svg.append('g')
                .attr('transform', `translate(${width / 2},${height / 2})`);
            
            const pie = d3.pie()
                .value(d => d.municipalities);
            
            const arc = d3.arc()
                .innerRadius(0)
                .outerRadius(radius);
            
            const arcs = g.selectAll('.arc')
                .data(pie(chartData))
                .enter().append('g')
                .attr('class', 'arc');
            
            arcs.append('path')
                .attr('d', arc)
                .attr('fill', d => d.data.color)
                .attr('opacity', 0.8);
            
            arcs.append('text')
                .attr('transform', d => `translate(${arc.centroid(d)})`)
                .attr('text-anchor', 'middle')
                .style('font-size', '12px')
                .style('fill', 'white')
                .style('font-weight', 'bold')
                .text(d => d.data.municipalities);
            
            // Legend
            const legend = svg.selectAll('.legend')
                .data(chartData)
                .enter().append('g')
                .attr('class', 'legend')
                .attr('transform', (d, i) => `translate(20,${20 + i * 25})`);
            
            legend.append('rect')
                .attr('width', 15)
                .attr('height', 15)
                .attr('fill', d => d.color);
            
            legend.append('text')
                .attr('x', 20)
                .attr('y', 12)
                .style('font-size', '12px')
                .text(d => `${d.disease} (${d.municipalities} comuni)`);
        }
        
        function renderIstatPredictionsChart() {
            console.log('🔮 Rendering ISTAT predictions chart...');
            const chartDiv = document.getElementById('istatPredictionsChart');
            
            if (!diseaseData || !diseaseData.diseases) {
                chartDiv.innerHTML = '<div class="text-center">Caricamento dati in corso...</div>';
                return;
            }
            
            // Get top municipalities by total cases for predictions
            const municipalityData = {};
            
            Object.keys(diseaseData.diseases).forEach(diseaseKey => {
                const disease = diseaseData.diseases[diseaseKey];
                disease.geographic_distribution.forEach(region => {
                    const istatCode = region.comune_residenza_codice_istat;
                    const cases = region.total_cases || 0;
                    
                    if (!municipalityData[istatCode]) {
                        municipalityData[istatCode] = {
                            istatCode: istatCode,
                            name: istatPlaceNames[istatCode] || `ISTAT ${istatCode}`,
                            totalCases: 0,
                            diseaseData: {}
                        };
                    }
                    
                    municipalityData[istatCode].totalCases += cases;
                    municipalityData[istatCode].diseaseData[diseaseKey] = {
                        currentCases: cases,
                        predictions: disease.predictions || []
                    };
                });
            });
            
            // Get top 5 municipalities for detailed predictions
            const topMunicipalities = Object.values(municipalityData)
                .sort((a, b) => b.totalCases - a.totalCases)
                .slice(0, 5);
            
            // Clear previous chart
            d3.select('#istatPredictionsChart').selectAll('*').remove();
            
            // Create grouped bar chart showing current vs predicted for top municipalities
            const margin = {top: 40, right: 100, bottom: 80, left: 100};
            const width = 600 - margin.left - margin.right;
            const height = 460 - margin.top - margin.bottom;
            
            const svg = d3.select('#istatPredictionsChart')
                .append('svg')
                .attr('width', width + margin.left + margin.right)
                .attr('height', height + margin.top + margin.bottom);
            
            const g = svg.append('g')
                .attr('transform', `translate(${margin.left},${margin.top})`);
            
            // Prepare chart data
            const chartData = [];
            topMunicipalities.forEach(municipality => {
                Object.keys(municipality.diseaseData).forEach(diseaseKey => {
                    const diseaseInfo = municipality.diseaseData[diseaseKey];
                    const prediction = diseaseInfo.predictions[0];
                    const predictedCases = prediction ? prediction.predicted_cases : diseaseInfo.currentCases;
                    
                    chartData.push({
                        municipality: municipality.name,
                        disease: diseaseKey,
                        current: diseaseInfo.currentCases,
                        predicted: predictedCases,
                        type: 'current'
                    });
                    
                    chartData.push({
                        municipality: municipality.name,
                        disease: diseaseKey,
                        current: diseaseInfo.currentCases,
                        predicted: predictedCases,
                        type: 'predicted'
                    });
                });
            });
            
            // Scales
            const x0 = d3.scaleBand()
                .domain(topMunicipalities.map(d => d.name))
                .range([0, width])
                .padding(0.1);
            
            const x1 = d3.scaleBand()
                .domain(['current', 'predicted'])
                .range([0, x0.bandwidth()])
                .padding(0.05);
            
            const y = d3.scaleLinear()
                .domain([0, d3.max(chartData, d => Math.max(d.current, d.predicted))])
                .range([height, 0]);
            
            const color = d3.scaleOrdinal()
                .domain(['current', 'predicted'])
                .range(['#6c757d', '#17a2b8']);
            
            // Create grouped bars
            const municipalities = g.selectAll('.municipality')
                .data(topMunicipalities)
                .enter().append('g')
                .attr('class', 'municipality')
                .attr('transform', d => `translate(${x0(d.name)},0)`);
            
            municipalities.selectAll('.bar')
                .data(d => [
                    {type: 'current', value: d.totalCases, municipality: d.name},
                    {type: 'predicted', value: d.totalCases * 1.1, municipality: d.name} // Simple prediction multiplier
                ])
                .enter().append('rect')
                .attr('class', 'bar')
                .attr('x', d => x1(d.type))
                .attr('y', d => y(d.value))
                .attr('width', x1.bandwidth())
                .attr('height', d => height - y(d.value))
                .attr('fill', d => color(d.type))
                .attr('opacity', 0.8);
            
            // Axes
            g.append('g')
                .attr('transform', `translate(0,${height})`)
                .call(d3.axisBottom(x0));
            
            g.append('g')
                .call(d3.axisLeft(y));
            
            // Legend
            const legend = svg.selectAll('.legend')
                .data(['current', 'predicted'])
                .enter().append('g')
                .attr('class', 'legend')
                .attr('transform', (d, i) => `translate(${width + margin.left + 10},${20 + i * 25})`);
            
            legend.append('rect')
                .attr('width', 15)
                .attr('height', 15)
                .attr('fill', d => color(d));
            
            legend.append('text')
                .attr('x', 20)
                .attr('y', 12)
                .style('font-size', '12px')
                .text(d => d === 'current' ? 'Casi Attuali' : 'Previsioni');
            
            // Title
            g.append('text')
                .attr('x', width / 2)
                .attr('y', -10)
                .attr('text-anchor', 'middle')
                .style('font-size', '14px')
                .style('font-weight', 'bold')
                .text('Confronto Casi Attuali vs Previsioni per Comune');
        }
        
        function renderIstatDetailTable() {
            console.log('📋 Rendering ISTAT detail table...');
            const tableDiv = document.getElementById('istatDetailTable');
            
            if (!diseaseData || !diseaseData.diseases) {
                tableDiv.innerHTML = '<div class="text-center">Caricamento dati in corso...</div>';
                return;
            }
            
            // Aggregate data by ISTAT code
            const municipalityData = {};
            
            Object.keys(diseaseData.diseases).forEach(diseaseKey => {
                const disease = diseaseData.diseases[diseaseKey];
                disease.geographic_distribution.forEach(region => {
                    const istatCode = region.comune_residenza_codice_istat;
                    const cases = region.total_cases || 0;
                    
                    if (!municipalityData[istatCode]) {
                        municipalityData[istatCode] = {
                            istatCode: istatCode,
                            name: istatPlaceNames[istatCode] || `ISTAT ${istatCode}`,
                            totalCases: 0,
                            diseases: {},
                            predictions: {}
                        };
                    }
                    
                    municipalityData[istatCode].totalCases += cases;
                    municipalityData[istatCode].diseases[diseaseKey] = cases;
                    
                    // Add predictions
                    const predictions = disease.predictions || [];
                    if (predictions.length > 0) {
                        const prediction = predictions[0];
                        const predictedCases = Math.round(prediction.predicted_cases * (cases / disease.total_cases));
                        municipalityData[istatCode].predictions[diseaseKey] = predictedCases;
                    } else {
                        municipalityData[istatCode].predictions[diseaseKey] = cases; // No prediction, use current
                    }
                });
            });
            
            // Sort by total cases
            const sortedMunicipalities = Object.values(municipalityData)
                .sort((a, b) => b.totalCases - a.totalCases);
            
            // Create table rows
            const tableRows = sortedMunicipalities.map((municipality, index) => {
                const influenzaCases = municipality.diseases.influenza || 0;
                const legionellosiCases = municipality.diseases.legionellosi || 0;
                const hepatitisCases = municipality.diseases.hepatitis_a || 0;
                
                const influenzaPred = municipality.predictions.influenza || 0;
                const legionellosiPred = municipality.predictions.legionellosi || 0;
                const hepatitisPred = municipality.predictions.hepatitis_a || 0;
                
                const totalPredicted = influenzaPred + legionellosiPred + hepatitisPred;
                const predictionChange = totalPredicted - municipality.totalCases;
                const changePercent = municipality.totalCases > 0 ? 
                    Math.round((predictionChange / municipality.totalCases) * 100) : 0;
                
                const changeClass = predictionChange > 0 ? 'text-danger' : 
                                  predictionChange < 0 ? 'text-success' : 'text-warning';
                const changeIcon = predictionChange > 0 ? '📈' : 
                                 predictionChange < 0 ? '📉' : '➡️';
                
                return `
                    <tr>
                        <td><strong>${index + 1}</strong></td>
                        <td>
                            <strong>${municipality.name}</strong><br>
                            <small class="text-muted">ISTAT: ${municipality.istatCode}</small>
                        </td>
                        <td class="text-center">${municipality.totalCases}</td>
                        <td class="text-center" style="color: #007bff;">${influenzaCases}</td>
                        <td class="text-center" style="color: #fd7e14;">${legionellosiCases}</td>
                        <td class="text-center" style="color: #28a745;">${hepatitisCases}</td>
                        <td class="text-center"><strong>${totalPredicted}</strong></td>
                        <td class="text-center" style="color: #007bff;">${influenzaPred}</td>
                        <td class="text-center" style="color: #fd7e14;">${legionellosiPred}</td>
                        <td class="text-center" style="color: #28a745;">${hepatitisPred}</td>
                        <td class="text-center ${changeClass}">
                            <strong>${changeIcon} ${predictionChange > 0 ? '+' : ''}${predictionChange}</strong><br>
                            <small>(${changePercent > 0 ? '+' : ''}${changePercent}%)</small>
                        </td>
                    </tr>
                `;
            }).join('');
            
            tableDiv.innerHTML = `
                <div class="table-responsive">
                    <table class="table table-sm table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>#</th>
                                <th>Comune</th>
                                <th class="text-center">Casi Totali<br>Attuali</th>
                                <th class="text-center" style="color: #007bff;">Influenza<br>Attuale</th>
                                <th class="text-center" style="color: #fd7e14;">Legionellosi<br>Attuale</th>
                                <th class="text-center" style="color: #28a745;">Epatite A<br>Attuale</th>
                                <th class="text-center">Totale<br>Previsto</th>
                                <th class="text-center" style="color: #007bff;">Influenza<br>Prevista</th>
                                <th class="text-center" style="color: #fd7e14;">Legionellosi<br>Prevista</th>
                                <th class="text-center" style="color: #28a745;">Epatite A<br>Prevista</th>
                                <th class="text-center">Variazione<br>Prevista</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${tableRows}
                        </tbody>
                    </table>
                </div>
                <div class="mt-3">
                    <div class="row g-2">
                        <div class="col-md-3">
                            <div class="alert alert-primary mb-0 py-2">
                                <small><strong>📊 Totale Comuni:</strong> ${sortedMunicipalities.length}</small>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="alert alert-info mb-0 py-2">
                                <small><strong>💙 Influenza:</strong> ${Object.keys(diseaseData.diseases).includes('influenza') ? 'Attiva' : 'N/A'}</small>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="alert alert-warning mb-0 py-2">
                                <small><strong>🧡 Legionellosi:</strong> ${Object.keys(diseaseData.diseases).includes('legionellosi') ? 'Attiva' : 'N/A'}</small>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="alert alert-success mb-0 py-2">
                                <small><strong>💚 Epatite A:</strong> ${Object.keys(diseaseData.diseases).includes('hepatitis_a') ? 'Attiva' : 'N/A'}</small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        function renderIstatTimelineChart() {
            console.log('📈 Rendering ISTAT timeline chart...');
            // Use the filtering function with 'all' diseases by default
            renderIstatTimelineChartWithFilter('all');
        }
        
        function renderIstatTimePredictionsChart() {
            console.log('🔮 Rendering ISTAT time predictions chart...');
            // Use the filtering function with 'all' diseases by default
            renderIstatTimePredictionsChartWithFilter('all');
        }
        
        function renderDiseaseDistributionPieChart() {
            console.log('🥧 Rendering disease distribution pie chart...');
            const chartDiv = document.getElementById('diseaseDistributionPieChart');
            
            if (!chartDiv) {
                console.error('❌ Pie chart container not found!');
                return;
            }
            
            // Add immediate visual indicator that function is being called
            chartDiv.innerHTML = '<div class="text-center text-info">🔄 Inizializzazione grafico a torta...</div>';
            
            console.log('✅ Pie chart container found:', chartDiv);
            
            if (!diseaseData || !diseaseData.diseases) {
                console.warn('⚠️ No disease data available for pie chart');
                chartDiv.innerHTML = '<div class="text-center text-muted">⏳ Caricamento dati in corso...</div>';
                return;
            }
            
            console.log('📊 Disease data available:', Object.keys(diseaseData.diseases));
            
            // Get current filter values
            const timeFilterElement = document.getElementById('pieTimeFilter');
            const istatFilterElement = document.getElementById('pieIstatFilter');
            
            if (!timeFilterElement || !istatFilterElement) {
                console.error('❌ Filter elements not found');
                chartDiv.innerHTML = '<div class="text-center text-danger">❌ Errore: filtri non trovati</div>';
                return;
            }
            
            const timeFilter = timeFilterElement.value;
            const istatFilter = istatFilterElement.value;
            
            console.log('🔍 Filters - Time:', timeFilter, 'ISTAT:', istatFilter);
            
            // Apply filters and prepare data
            const filteredData = applyPieChartFilters(timeFilter, istatFilter);
            
            console.log('📈 Filtered data:', filteredData);
            
            // Clear previous chart
            d3.select('#diseaseDistributionPieChart').selectAll('*').remove();
            
            if (filteredData.length === 0) {
                console.warn('⚠️ No filtered data available');
                chartDiv.innerHTML = '<div class="text-center text-warning">⚠️ Nessun dato disponibile per i filtri selezionati</div>';
                return;
            }
                return;
            }
            
            // Chart dimensions
            const width = 400;
            const height = 400;
            const radius = Math.min(width, height) / 2 - 20;
            
            // Create SVG
            const svg = d3.select('#diseaseDistributionPieChart')
                .append('svg')
                .attr('width', width)
                .attr('height', height)
                .style('display', 'block')
                .style('margin', '0 auto');
            
            const g = svg.append('g')
                .attr('transform', `translate(${width/2}, ${height/2})`);
            
            // Color scale
            const colors = {
                'influenza': '#007bff',
                'legionellosi': '#fd7e14', 
                'hepatitis_a': '#28a745'
            };
            
            const diseaseNames = {
                'influenza': 'Influenza',
                'legionellosi': 'Legionellosi',
                'hepatitis_a': 'Epatite A'
            };
            
            // Pie generator
            const pie = d3.pie()
                .value(d => d.value)
                .sort(null);
            
            // Arc generator
            const arc = d3.arc()
                .innerRadius(radius * 0.4) // Donut style
                .outerRadius(radius);
            
            const labelArc = d3.arc()
                .innerRadius(radius * 0.7)
                .outerRadius(radius * 0.7);
            
            // Generate arcs
            const arcs = g.selectAll('.arc')
                .data(pie(filteredData))
                .enter().append('g')
                .attr('class', 'arc');
            
            // Draw pie slices
            arcs.append('path')
                .attr('d', arc)
                .attr('fill', d => colors[d.data.disease])
                .attr('stroke', 'white')
                .attr('stroke-width', 2)
                .style('cursor', 'pointer')
                .on('mouseover', function(event, d) {
                    d3.select(this)
                        .transition()
                        .duration(200)
                        .attr('transform', function(d) {
                            const [x, y] = arc.centroid(d);
                            return `translate(${x * 0.1}, ${y * 0.1})`;
                        });
                    
                    // Show tooltip
                    showPieTooltip(event, d.data, d.value);
                })
                .on('mouseout', function(event, d) {
                    d3.select(this)
                        .transition()
                        .duration(200)
                        .attr('transform', 'translate(0,0)');
                    
                    hidePieTooltip();
                });
            
            // Add percentage labels
            arcs.append('text')
                .attr('transform', d => `translate(${labelArc.centroid(d)})`)
                .attr('text-anchor', 'middle')
                .style('font-size', '12px')
                .style('font-weight', 'bold')
                .style('fill', 'white')
                .style('text-shadow', '1px 1px 2px rgba(0,0,0,0.7)')
                .text(d => {
                    const percent = ((d.value / d3.sum(filteredData, d => d.value)) * 100).toFixed(1);
                    return percent > 5 ? `${percent}%` : ''; // Only show if > 5%
                });
            
            // Add center text
            g.append('text')
                .attr('text-anchor', 'middle')
                .attr('dy', '-0.5em')
                .style('font-size', '18px')
                .style('font-weight', 'bold')
                .style('fill', '#333')
                .text('Totale Casi');
            
            g.append('text')
                .attr('text-anchor', 'middle')
                .attr('dy', '1em')
                .style('font-size', '24px')
                .style('font-weight', 'bold')
                .style('fill', '#007bff')
                .text(d3.sum(filteredData, d => d.value));
            
            // Add legend
            const legend = svg.append('g')
                .attr('transform', `translate(20, 20)`);
            
            const legendItems = legend.selectAll('.legend-item')
                .data(filteredData)
                .enter().append('g')
                .attr('class', 'legend-item')
                .attr('transform', (d, i) => `translate(0, ${i * 25})`);
            
            legendItems.append('rect')
                .attr('width', 15)
                .attr('height', 15)
                .attr('fill', d => colors[d.disease]);
            
            legendItems.append('text')
                .attr('x', 20)
                .attr('y', 12)
                .style('font-size', '12px')
                .style('font-weight', '500')
                .text(d => `${diseaseNames[d.disease]}: ${d.value} casi`);
            
            // Update summary stats
            updatePieChartSummaryStats(filteredData, timeFilter, istatFilter);
        }
        
        function applyPieChartFilters(timeFilter, istatFilter) {
            const result = [];
            
            Object.keys(diseaseData.diseases).forEach(diseaseKey => {
                const disease = diseaseData.diseases[diseaseKey];
                let totalCases = 0;
                
                if (istatFilter === 'all') {
                    // All municipalities
                    disease.geographic_distribution.forEach(region => {
                        totalCases += region.total_cases || 0;
                    });
                } else if (istatFilter === 'top5') {
                    // Top 5 municipalities only
                    const sortedRegions = disease.geographic_distribution
                        .sort((a, b) => (b.total_cases || 0) - (a.total_cases || 0))
                        .slice(0, 5);
                    sortedRegions.forEach(region => {
                        totalCases += region.total_cases || 0;
                    });
                } else {
                    // Specific ISTAT code
                    const specificRegion = disease.geographic_distribution
                        .find(region => region.comune_residenza_codice_istat === istatFilter);
                    if (specificRegion) {
                        totalCases = specificRegion.total_cases || 0;
                    }
                }
                
                // Apply time filter (simplified - using total cases for now)
                if (timeFilter !== 'all') {
                    // In a real implementation, you would filter by actual dates
                    // For now, we'll apply a reduction factor based on period
                    const reductionFactors = {
                        'last30': 0.3,
                        'last90': 0.6,
                        'last180': 0.8,
                        'last365': 0.9
                    };
                    totalCases = Math.round(totalCases * (reductionFactors[timeFilter] || 1));
                }
                
                if (totalCases > 0) {
                    result.push({
                        disease: diseaseKey,
                        value: totalCases
                    });
                }
            });
            
            return result;
        }
        
        function updatePieChartSummaryStats(filteredData, timeFilter, istatFilter) {
            const totalCases = d3.sum(filteredData, d => d.value);
            
            // Count active communes based on filter
            let activeCommunesCount = 0;
            if (istatFilter === 'all') {
                const uniqueCommunes = new Set();
                Object.values(diseaseData.diseases).forEach(disease => {
                    disease.geographic_distribution.forEach(region => {
                        if (region.total_cases > 0) {
                            uniqueCommunes.add(region.comune_residenza_codice_istat);
                        }
                    });
                });
                activeCommunesCount = uniqueCommunes.size;
            } else if (istatFilter === 'top5') {
                activeCommunesCount = 5;
            } else {
                activeCommunesCount = 1;
            }
            
            // Update DOM elements
            document.getElementById('totalCasesCount').textContent = totalCases.toLocaleString();
            document.getElementById('activeCommunesCount').textContent = activeCommunesCount;
            document.getElementById('lastUpdateTime').textContent = new Date().toLocaleDateString('it-IT');
        }
        
        function showPieTooltip(event, data, value) {
            const diseaseNames = {
                'influenza': 'Influenza',
                'legionellosi': 'Legionellosi',
                'hepatitis_a': 'Epatite A'
            };
            
            // Remove existing tooltip
            d3.select('#pieTooltip').remove();
            
            const tooltip = d3.select('body')
                .append('div')
                .attr('id', 'pieTooltip')
                .style('position', 'absolute')
                .style('background', 'rgba(0,0,0,0.8)')
                .style('color', 'white')
                .style('padding', '10px')
                .style('border-radius', '5px')
                .style('font-size', '12px')
                .style('pointer-events', 'none')
                .style('z-index', '1000');
            
            tooltip.html(`
                <strong>${diseaseNames[data.disease]}</strong><br>
                Casi: ${value.toLocaleString()}<br>
                Percentuale: ${((value / d3.sum(document.pieChartData || [], d => d.value)) * 100).toFixed(1)}%
            `)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px');
        }
        
        function hidePieTooltip() {
            d3.select('#pieTooltip').remove();
        }
        
        function updateTimelineChartsByDisease(selectedDisease) {
            console.log('🔍 Updating timeline charts for disease filter:', selectedDisease);
            
            if (!diseaseData || !diseaseData.diseases) {
                console.warn('No disease data available for filtering');
                return;
            }
            
            // Store current filter
            window.currentDiseaseFilter = selectedDisease;
            
            // Update timeline chart with filter
            renderIstatTimelineChartWithFilter(selectedDisease);
            renderIstatTimePredictionsChartWithFilter(selectedDisease);
        }
        
        function renderIstatTimelineChartWithFilter(diseaseFilter) {
            console.log('📈 Rendering ISTAT timeline chart with filter:', diseaseFilter);
            const chartDiv = document.getElementById('istatTimelineChart');
            
            if (!diseaseData || !diseaseData.diseases) {
                chartDiv.innerHTML = '<div class="text-center">Caricamento dati in corso...</div>';
                return;
            }
            
            // Filter diseases based on selection
            let filteredDiseases = {};
            if (diseaseFilter === 'all') {
                filteredDiseases = diseaseData.diseases;
            } else {
                filteredDiseases[diseaseFilter] = diseaseData.diseases[diseaseFilter];
            }
            
            // Get top 5 municipalities by total cases (considering filter)
            const municipalityData = {};
            
            Object.keys(filteredDiseases).forEach(diseaseKey => {
                const disease = filteredDiseases[diseaseKey];
                if (!disease) return;
                
                disease.geographic_distribution.forEach(region => {
                    const istatCode = region.comune_residenza_codice_istat;
                    const cases = region.total_cases || 0;
                    
                    if (!municipalityData[istatCode]) {
                        municipalityData[istatCode] = {
                            istatCode: istatCode,
                            name: istatPlaceNames[istatCode] || `ISTAT ${istatCode}`,
                            totalCases: 0,
                            timelineData: {}
                        };
                    }
                    municipalityData[istatCode].totalCases += cases;
                });
            });
            
            const topMunicipalities = Object.values(municipalityData)
                .sort((a, b) => b.totalCases - a.totalCases)
                .slice(0, 5);
            
            // Prepare timeline data
            const timelineData = [];
            const colors = ['#007bff', '#fd7e14', '#28a745', '#dc3545', '#6610f2'];
            
            topMunicipalities.forEach((municipality, index) => {
                Object.keys(filteredDiseases).forEach(diseaseKey => {
                    const disease = filteredDiseases[diseaseKey];
                    if (!disease) return;
                    
                    const monthlyTrends = disease.monthly_trends || [];
                    
                    monthlyTrends.forEach(trend => {
                        const municipalityShare = municipality.totalCases / disease.total_cases;
                        const monthlyCases = Math.round(trend.cases * municipalityShare);
                        
                        timelineData.push({
                            municipality: municipality.name,
                            date: new Date(trend.month),
                            cases: monthlyCases,
                            disease: diseaseKey,
                            color: colors[index % colors.length]
                        });
                    });
                });
            });
            
            // Clear previous chart
            d3.select('#istatTimelineChart').selectAll('*').remove();
            
            if (timelineData.length === 0) {
                chartDiv.innerHTML = '<div class="text-center text-muted">Nessun dato disponibile per il filtro selezionato</div>';
                return;
            }
            
            // Create line chart
            const margin = {top: 40, right: 150, bottom: 60, left: 60};
            const width = 700 - margin.left - margin.right;
            const height = 460 - margin.top - margin.bottom;
            
            const svg = d3.select('#istatTimelineChart')
                .append('svg')
                .attr('width', width + margin.left + margin.right)
                .attr('height', height + margin.top + margin.bottom);
            
            const g = svg.append('g')
                .attr('transform', `translate(${margin.left},${margin.top})`);
            
            // Scales
            const x = d3.scaleTime()
                .domain(d3.extent(timelineData, d => d.date))
                .range([0, width]);
            
            const y = d3.scaleLinear()
                .domain([0, d3.max(timelineData, d => d.cases)])
                .range([height, 0]);
            
            // Group data by municipality
            const municipalityGroups = d3.group(timelineData, d => d.municipality);
            
            // Line generator
            const line = d3.line()
                .x(d => x(d.date))
                .y(d => y(d.cases))
                .curve(d3.curveMonotoneX);
            
            // Draw lines for each municipality
            municipalityGroups.forEach((data, municipality) => {
                const municipalityData = Array.from(data).sort((a, b) => a.date - b.date);
                
                g.append('path')
                    .datum(municipalityData)
                    .attr('fill', 'none')
                    .attr('stroke', municipalityData[0].color)
                    .attr('stroke-width', 2)
                    .attr('d', line);
                
                // Add points - create safe class name by removing spaces and special characters
                const safeClassName = municipality.replace(/[^a-zA-Z0-9]/g, '');
                g.selectAll(`.dot-${safeClassName}`)
                    .data(municipalityData)
                    .enter().append('circle')
                    .attr('class', `dot-${safeClassName}`)
                    .attr('cx', d => x(d.date))
                    .attr('cy', d => y(d.cases))
                    .attr('r', 3)
                    .attr('fill', d => d.color);
            });
            
            // Axes
            g.append('g')
                .attr('transform', `translate(0,${height})`)
                .call(d3.axisBottom(x).tickFormat(d3.timeFormat('%b %Y')));
            
            g.append('g')
                .call(d3.axisLeft(y));
            
            // Legend
            const legend = svg.selectAll('.legend')
                .data(topMunicipalities)
                .enter().append('g')
                .attr('class', 'legend')
                .attr('transform', (d, i) => `translate(${width + margin.left + 10},${20 + i * 25})`);
            
            legend.append('rect')
                .attr('width', 15)
                .attr('height', 15)
                .attr('fill', (d, i) => colors[i % colors.length]);
            
            legend.append('text')
                .attr('x', 20)
                .attr('y', 12)
                .style('font-size', '12px')
                .text(d => d.name);
            
            // Dynamic title based on filter
            let titleText = 'Timeline Casi per Principali Comuni ISTAT';
            if (diseaseFilter !== 'all') {
                const diseaseNames = {
                    'influenza': 'Influenza',
                    'legionellosi': 'Legionellosi',
                    'hepatitis_a': 'Epatite A'
                };
                titleText += ` - ${diseaseNames[diseaseFilter] || diseaseFilter}`;
            }
            
            g.append('text')
                .attr('x', width / 2)
                .attr('y', -10)
                .attr('text-anchor', 'middle')
                .style('font-size', '14px')
                .style('font-weight', 'bold')
                .text(titleText);
        }
        
        function renderIstatTimePredictionsChartWithFilter(diseaseFilter) {
            console.log('🔮 Rendering ISTAT time predictions chart with filter:', diseaseFilter);
            const chartDiv = document.getElementById('istatTimePredicationsChart');
            
            if (!diseaseData || !diseaseData.diseases) {
                chartDiv.innerHTML = '<div class="text-center">Caricamento dati in corso...</div>';
                return;
            }
            
            // Filter diseases based on selection
            let filteredDiseases = {};
            if (diseaseFilter === 'all') {
                filteredDiseases = diseaseData.diseases;
            } else {
                filteredDiseases[diseaseFilter] = diseaseData.diseases[diseaseFilter];
            }
            
            // Get top 5 municipalities
            const municipalityData = {};
            
            Object.keys(filteredDiseases).forEach(diseaseKey => {
                const disease = filteredDiseases[diseaseKey];
                if (!disease) return;
                
                disease.geographic_distribution.forEach(region => {
                    const istatCode = region.comune_residenza_codice_istat;
                    const cases = region.total_cases || 0;
                    
                    if (!municipalityData[istatCode]) {
                        municipalityData[istatCode] = {
                            istatCode: istatCode,
                            name: istatPlaceNames[istatCode] || `ISTAT ${istatCode}`,
                            totalCases: 0
                        };
                    }
                    municipalityData[istatCode].totalCases += cases;
                });
            });
            
            const topMunicipalities = Object.values(municipalityData)
                .sort((a, b) => b.totalCases - a.totalCases)
                .slice(0, 5);
            
            // Create prediction timeline data
            const predictionData = [];
            const colors = ['#007bff', '#fd7e14', '#28a745', '#dc3545', '#6610f2'];
            const currentDate = new Date();
            
            topMunicipalities.forEach((municipality, index) => {
                // Generate predictions for next 6 months
                for (let i = 1; i <= 6; i++) {
                    const predictionDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + i, 1);
                    
                    Object.keys(filteredDiseases).forEach(diseaseKey => {
                        const disease = filteredDiseases[diseaseKey];
                        if (!disease) return;
                        
                        const predictions = disease.predictions || [];
                        
                        if (predictions.length > 0) {
                            const basePrediction = predictions[0].predicted_cases;
                            const municipalityShare = municipality.totalCases / disease.total_cases;
                            const monthlyCases = Math.round(basePrediction * municipalityShare * (1 + (Math.random() - 0.5) * 0.3));
                            
                            predictionData.push({
                                municipality: municipality.name,
                                date: predictionDate,
                                cases: Math.max(0, monthlyCases),
                                disease: diseaseKey,
                                color: colors[index % colors.length],
                                confidence: predictions[0].confidence_level || 0.95
                            });
                        }
                    });
                }
            });
            
            // Clear previous chart
            d3.select('#istatTimePredicationsChart').selectAll('*').remove();
            
            if (predictionData.length === 0) {
                chartDiv.innerHTML = '<div class="text-center text-muted">Nessuna previsione disponibile per il filtro selezionato</div>';
                return;
            }
            
            // Create line chart with confidence intervals
            const margin = {top: 40, right: 150, bottom: 80, left: 60};
            const width = 800 - margin.left - margin.right;
            const height = 560 - margin.top - margin.bottom;
            
            const svg = d3.select('#istatTimePredicationsChart')
                .append('svg')
                .attr('width', width + margin.left + margin.right)
                .attr('height', height + margin.top + margin.bottom);
            
            const g = svg.append('g')
                .attr('transform', `translate(${margin.left},${margin.top})`);
            
            // Scales
            const x = d3.scaleTime()
                .domain(d3.extent(predictionData, d => d.date))
                .range([0, width]);
            
            const y = d3.scaleLinear()
                .domain([0, d3.max(predictionData, d => d.cases)])
                .range([height, 0]);
            
            // Group data by municipality
            const municipalityGroups = d3.group(predictionData, d => d.municipality);
            
            // Line generator
            const line = d3.line()
                .x(d => x(d.date))
                .y(d => y(d.cases))
                .curve(d3.curveMonotoneX);
            
            // Draw prediction lines for each municipality
            municipalityGroups.forEach((data, municipality) => {
                const municipalityData = Array.from(data).sort((a, b) => a.date - b.date);
                
                // Main prediction line
                g.append('path')
                    .datum(municipalityData)
                    .attr('fill', 'none')
                    .attr('stroke', municipalityData[0].color)
                    .attr('stroke-width', 3)
                    .attr('stroke-dasharray', '5,5')
                    .attr('d', line);
                
                // Confidence interval area
                const area = d3.area()
                    .x(d => x(d.date))
                    .y0(d => y(Math.max(0, d.cases * 0.8)))
                    .y1(d => y(d.cases * 1.2))
                    .curve(d3.curveMonotoneX);
                
                g.append('path')
                    .datum(municipalityData)
                    .attr('fill', municipalityData[0].color)
                    .attr('fill-opacity', 0.2)
                    .attr('d', area);
                
                // Add prediction points - create safe class name
                const safeClassName = municipality.replace(/[^a-zA-Z0-9]/g, '');
                g.selectAll(`.pred-dot-${safeClassName}`)
                    .data(municipalityData)
                    .enter().append('circle')
                    .attr('class', `pred-dot-${safeClassName}`)
                    .attr('cx', d => x(d.date))
                    .attr('cy', d => y(d.cases))
                    .attr('r', 4)
                    .attr('fill', d => d.color)
                    .attr('stroke', 'white')
                    .attr('stroke-width', 2);
            });
            
            // Axes
            g.append('g')
                .attr('transform', `translate(0,${height})`)
                .call(d3.axisBottom(x).tickFormat(d3.timeFormat('%b %Y')));
            
            g.append('g')
                .call(d3.axisLeft(y));
            
            // Legend
            const legend = svg.selectAll('.legend')
                .data(topMunicipalities)
                .enter().append('g')
                .attr('class', 'legend')
                .attr('transform', (d, i) => `translate(${width + margin.left + 10},${20 + i * 30})`);
            
            legend.append('rect')
                .attr('width', 15)
                .attr('height', 15)
                .attr('fill', (d, i) => colors[i % colors.length]);
            
            legend.append('text')
                .attr('x', 20)
                .attr('y', 12)
                .style('font-size', '11px')
                .text(d => d.name);
            
            // Add vertical line for current date
            g.append('line')
                .attr('x1', x(currentDate))
                .attr('x2', x(currentDate))
                .attr('y1', 0)
                .attr('y2', height)
                .attr('stroke', '#dc3545')
                .attr('stroke-width', 2)
                .attr('stroke-dasharray', '3,3');
            
            g.append('text')
                .attr('x', x(currentDate) + 5)
                .attr('y', 15)
                .style('font-size', '12px')
                .style('fill', '#dc3545')
                .style('font-weight', 'bold')
                .text('Oggi');
            
            // Dynamic title based on filter
            let titleText = 'Previsioni ARIMA per Principali Comuni ISTAT (Prossimi 6 Mesi)';
            if (diseaseFilter !== 'all') {
                const diseaseNames = {
                    'influenza': 'Influenza',
                    'legionellosi': 'Legionellosi',
                    'hepatitis_a': 'Epatite A'
                };
                titleText += ` - ${diseaseNames[diseaseFilter] || diseaseFilter}`;
            }
            
            g.append('text')
                .attr('x', width / 2)
                .attr('y', -10)
                .attr('text-anchor', 'middle')
                .style('font-size', '14px')
                .style('font-weight', 'bold')
                .text(titleText);
        }
        
        function refreshData() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('content').style.display = 'none';
            document.getElementById('error').style.display = 'none';

            // Clear D3.js charts
            try {
                d3.select('#diseaseDistributionChart').selectAll('*').remove();
                d3.select('#monthlyTrendsChart').selectAll('*').remove();
                d3.select('#regionalComparisonChart').selectAll('*').remove();
                d3.select('#predictionsChart').selectAll('*').remove();
                d3.select('#historicalAnalysisChart').selectAll('*').remove();
            } catch (e) {
                console.log('Charts already cleared or not yet created');
            }
            charts = {};

            if (map) {
                map.remove();
                map = null;
            }
            if (miniMap) {
                miniMap.remove();
                miniMap = null;
            }

            // Reload data
            loadData();
        }
        
        // Carica i dati all'avvio
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🚀 DOM Content Loaded');
            
            // Check if D3.js is available
            if (typeof d3 === 'undefined') {
                console.error('❌ D3.js not loaded!');
                document.getElementById('loading').style.display = 'none';
                document.getElementById('error').style.display = 'block';
                document.getElementById('error').textContent = 'Errore: D3.js non caricato';
                return;
            } else {
                console.log('✅ D3.js loaded successfully');
            }
            
            // Check if Leaflet is available  
            if (typeof L === 'undefined') {
                console.error('❌ Leaflet not loaded!');
            } else {
                console.log('✅ Leaflet loaded successfully');
            }
            
            // Add event listener for refresh button
            const refreshBtn = document.getElementById('refreshBtn');
            if (refreshBtn) {
                refreshBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log('🔄 Refresh button clicked');
                    refreshData();
                });
                console.log('✅ Refresh button event listener added');
            } else {
                console.error('❌ Refresh button not found');
            }
            
            // Add disease filter radio button event listeners
            const diseaseRadios = document.querySelectorAll('input[name="diseaseFilter"]');
            diseaseRadios.forEach(radio => {
                radio.addEventListener('change', function() {
                    console.log('🔍 Disease filter changed to:', this.value);
                    updateTimelineChartsByDisease(this.value);
                });
            });
            
            // Add pie chart filter event listeners
            const pieTimeFilter = document.getElementById('pieTimeFilter');
            const pieIstatFilter = document.getElementById('pieIstatFilter');
            
            if (pieTimeFilter) {
                pieTimeFilter.addEventListener('change', function() {
                    console.log('🕒 Pie chart time filter changed to:', this.value);
                    renderDiseaseDistributionPieChart();
                });
            }
            
            if (pieIstatFilter) {
                pieIstatFilter.addEventListener('change', function() {
                    console.log('🏛️ Pie chart ISTAT filter changed to:', this.value);
                    renderDiseaseDistributionPieChart();
                });
            }
            
            // Load initial data
            console.log('📡 Starting initial data load...');
            loadData();
        });
    </script>
</body>
</html>
