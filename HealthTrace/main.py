"""
HealthTrace Platform - Main FastAPI Application
Environmental Health Surveillance System for Italian Regions
Integrated with Real GESAN Infectious Disease Database
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Import our database routes
from real_disease_db import router as real_db_router

app = FastAPI(
    title="HealthTrace Platform",
    description="Environmental Health Surveillance System with Real Italian Database Integration",
    version="2.0.0"
)

BASE_DIR = os.path.dirname(__file__)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Include real database routes
app.include_router(real_db_router, prefix="/api/real-database", tags=["Real GESAN Database"])


# Endpoint to receive client-side JS errors for debugging
@app.post("/client-log")
async def client_log(request: Request):
    """Receive client-side logs (temporary debug endpoint)."""
    try:
        payload = await request.json()
    except Exception:
        payload = {"raw": await request.body()}

    import logging
    logging.getLogger("uvicorn.access").info(f"CLIENT_LOG: {payload}")
    return {"status": "logged"}

@app.get("/", response_class=HTMLResponse)
async def root():
    """Main dashboard for HealthTrace platform"""
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HealthTrace - Sistema di Sorveglianza Sanitaria Ambientale</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.css" />
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            .header h1 {
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .header p {
                color: #7f8c8d;
                font-size: 1.2em;
                margin-bottom: 20px;
            }
            .status {
                display: inline-block;
                padding: 8px 16px;
                background: #27ae60;
                color: white;
                border-radius: 20px;
                font-weight: bold;
            }
            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .dashboard-card {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .dashboard-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
            }
            .card-title {
                color: #2c3e50;
                font-size: 1.4em;
                margin-bottom: 15px;
                font-weight: bold;
            }
            .card-content {
                color: #34495e;
                line-height: 1.6;
            }
            .btn {
                display: inline-block;
                padding: 12px 24px;
                background: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 25px;
                margin: 5px;
                transition: all 0.3s ease;
                font-weight: 500;
            }
            .btn:hover {
                background: #2980b9;
                transform: scale(1.05);
            }
            .btn-success { background: #27ae60; }
            .btn-success:hover { background: #229954; }
            .btn-warning { background: #f39c12; }
            .btn-warning:hover { background: #d68910; }
            .btn-danger { background: #e74c3c; }
            .btn-danger:hover { background: #c0392b; }
            .api-section {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            }
            .endpoint {
                background: #f8f9fa;
                border-left: 4px solid #3498db;
                padding: 15px;
                margin: 10px 0;
                border-radius: 0 8px 8px 0;
            }
            .method {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                color: white;
                font-weight: bold;
                font-size: 0.9em;
                margin-right: 10px;
            }
            .get { background: #28a745; }
            .real-db-badge {
                background: linear-gradient(45deg, #ff6b6b, #feca57);
                color: white;
                padding: 5px 12px;
                border-radius: 15px;
                font-size: 0.9em;
                font-weight: bold;
                display: inline-block;
                margin-left: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 HealthTrace Platform</h1>
                <p>Sistema di Sorveglianza Sanitaria Ambientale per le Regioni Italiane</p>
                <div class="status" id="dbStatus">🔄 Verificando connessione database...</div>
                <div class="real-db-badge">🔴 Database Reale GESAN Collegato</div>
            </div>
            
            <div class="dashboard-grid">
                <div class="dashboard-card">
                    <div class="card-title">📊 Database Reale GESAN</div>
                    <div class="card-content">
                        <p>Accesso diretto al database delle malattie infettive ASL Campania. Server: <strong>10.10.13.11</strong></p>
                        <p><strong>Tabelle principali:</strong></p>
                        <ul>
                            <li>Segnalazioni: 2,974 casi</li>
                            <li>COVID-19: 663 casi</li>
                            <li>Contatti: 1,373 tracciamenti</li>
                            <li>Sintomatologia: 1,302 reports</li>
                        </ul>
                        <a href="/api/real-database/" class="btn btn-success">Stato Database</a>
                        <a href="/api/real-database/recent-cases" class="btn btn-warning">Casi Recenti</a>
                    </div>
                </div>
                
                <div class="dashboard-card">
                    <div class="card-title">🦠 Malattie Infettive</div>
                    <div class="card-content">
                        <p>Monitoraggio delle malattie infettive in tempo reale con dati GESAN ASL.</p>
                        <ul>
                            <li>COVID-19 surveillance</li>
                            <li>Legionellosi e influenza</li>
                            <li>Infezioni alimentari</li>
                            <li>Meningiti ed encefaliti</li>
                        </ul>
                        <a href="/api/real-database/covid-cases" class="btn btn-danger">Dati COVID</a>
                        <a href="/api/real-database/disease-statistics" class="btn">Statistiche</a>
                    </div>
                </div>
                
                <div class="dashboard-card">
                    <div class="card-title">� Statistiche Tre Malattie</div>
                    <div class="card-content">
                        <p>Analisi approfondita di <strong>Influenza, Legionellosi ed Epatite A</strong> con grafici interattivi e mappe regionali.</p>
                        <ul>
                            <li>Distribuzione geografica per regioni</li>
                            <li>Trend temporali e stagionali</li>
                            <li>Confronti regionali</li>
                            <li>Mappe interattive con cluster</li>
                        </ul>
                        <a href="three_diseases_statistics.html" class="btn btn-success">📈 Visualizza Statistiche</a>
                        <a href="/api/real-database/three-diseases-stats" class="btn">📊 Dati JSON</a>
                    </div>
                </div>
                
                <div class="dashboard-card">
                    <div class="card-title">�🗺️ Analisi Territoriale</div>
                    <div class="card-content">
                        <p>Mappatura geografica dei casi per codici ISTAT comunali.</p>
                        <ul>
                            <li>Distribuzione geografica</li>
                            <li>Cluster territoriali</li>
                            <li>Trend regionali</li>
                        </ul>
                        <a href="polygon_test.html" class="btn">Test Poligoni</a>
                        <a href="coordinate_dashboard.html" class="btn">Coordinate ISTAT</a>
                    </div>
                </div>
                
                <div class="dashboard-card">
                    <div class="card-title">👥 Contact Tracing</div>
                    <div class="card-content">
                        <p>Sistema di tracciamento contatti per indagini epidemiologiche.</p>
                        <ul>
                            <li>Lista contatti per caso</li>
                            <li>Tracciamento familiare</li>
                            <li>Contatti ospedalieri</li>
                        </ul>
                        <a href="/api/real-database/contact-tracing" class="btn btn-warning">Dati Contatti</a>
                        <a href="/api/real-database/symptoms" class="btn">Sintomi</a>
                    </div>
                </div>
            </div>
            
            <div class="api-section">
                <h2>🔗 API Endpoints - Database Reale GESAN</h2>
                <p>Tutti gli endpoints accedono direttamente al database PostgreSQL dell'ASL Campania:</p>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/real-database/</strong> - Stato connessione database
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/real-database/recent-cases</strong> - Casi recenti (ultimi 30 giorni)
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/real-database/covid-cases</strong> - Dati specifici COVID-19
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/real-database/disease-statistics</strong> - Statistiche malattie
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/real-database/municipality/{istat_code}</strong> - Casi per comune
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/real-database/tables</strong> - Lista tabelle database
                </div>
            </div>
        </div>
        
        <script>
            // Check database status
            fetch('/api/real-database/')
                .then(response => response.json())
                .then(data => {
                    const statusElement = document.getElementById('dbStatus');
                    if (data.status === 'connected') {
                        statusElement.innerHTML = '✅ Database GESAN Connesso';
                        statusElement.style.background = '#27ae60';
                    } else {
                        statusElement.innerHTML = '❌ Errore Connessione Database';
                        statusElement.style.background = '#e74c3c';
                    }
                })
                .catch(error => {
                    const statusElement = document.getElementById('dbStatus');
                    statusElement.innerHTML = '⚠️ Errore Verifica Database';
                    statusElement.style.background = '#f39c12';
                });
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "platform": "HealthTrace", "version": "2.0.0"}

# Serve static HTML files
@app.get("/polygon_test.html", response_class=HTMLResponse)
async def polygon_test():
    """Serve polygon testing interface"""
    polygon_path = os.path.join(BASE_DIR, "polygon_test.html")
    if os.path.exists(polygon_path):
        with open(polygon_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise HTTPException(status_code=404, detail="Polygon test page not found")

@app.get("/coordinate_dashboard.html", response_class=HTMLResponse)
async def coordinate_dashboard():
    """Serve coordinate dashboard"""
    coordinate_path = os.path.join(BASE_DIR, "coordinate_dashboard.html")
    if os.path.exists(coordinate_path):
        with open(coordinate_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise HTTPException(status_code=404, detail="Coordinate dashboard not found")

@app.get("/three_diseases_statistics.html", response_class=HTMLResponse)
async def three_diseases_statistics():
    """Serve three diseases statistics dashboard"""
    stats_path = os.path.join(BASE_DIR, "three_diseases_statistics.html")
    if os.path.exists(stats_path):
        with open(stats_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise HTTPException(status_code=404, detail="Three diseases statistics dashboard not found")

@app.get("/test_simple.html", response_class=HTMLResponse)
async def test_simple():
    """Serve simple test dashboard for diagnostics"""
    test_path = os.path.join(BASE_DIR, "test_simple.html")
    if os.path.exists(test_path):
        with open(test_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise HTTPException(status_code=404, detail="Test simple dashboard not found")

if __name__ == "__main__":
    print("🚀 Starting HealthTrace Platform with Real GESAN Database Integration...")
    print("🔗 Database: PostgreSQL 9.2.24 @ 10.10.13.11:5432/gesan_malattieinfettive")
    print("📊 Real Italian infectious disease surveillance data")
    print("🌐 Platform available at: http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
