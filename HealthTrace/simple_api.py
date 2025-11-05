#!/usr/bin/env python3
"""
Simple HealthTrace API Server for Development
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

app = FastAPI(
    title="HealthTrace API",
    description="Environmental Health Monitoring System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3200", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "HealthTrace API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "healthtrace-api"}

@app.get("/api/v1/dashboard/summary")
def get_dashboard_summary():
    """Get dashboard summary statistics"""
    return {
        "total_reports": 156,
        "total_investigations": 124,
        "active_patients": 45,
        "recovered_patients": 89,
        "regions": ["Campania", "Calabria", "Molise"],
        "last_updated": datetime.now().isoformat(),
        "reports_over_time": [
            {"month": "Gen 2024", "reports": 23, "investigations": 18},
            {"month": "Feb 2024", "reports": 29, "investigations": 22},
            {"month": "Mar 2024", "reports": 31, "investigations": 25},
            {"month": "Apr 2024", "reports": 45, "investigations": 38},
            {"month": "Mag 2024", "reports": 38, "investigations": 31},
            {"month": "Giu 2024", "reports": 42, "investigations": 34}
        ],
        "disease_distribution": [
            {"name": "Malattie Respiratorie", "value": 45},
            {"name": "Dermatiti", "value": 28},
            {"name": "Allergie", "value": 32},
            {"name": "Patologie Cardiovascolari", "value": 19},
            {"name": "Tumori", "value": 32}
        ],
        "region_distribution": [
            {"region": "Campania", "cases": 89},
            {"region": "Calabria", "cases": 45},
            {"region": "Molise", "cases": 22}
        ]
    }

@app.get("/api/v1/environmental/istat/{istat_code}/{year}/{interval}/{function}/{pollutant}")
def get_pollutant_data(istat_code: str, year: int, interval: int, function: str, pollutant: str):
    return {
        "istat_code": istat_code,
        "year": year,
        "interval": interval,
        "function": function,
        "pollutant": pollutant,
        "value": 22.5,
        "unit": "μg/m³" if pollutant not in ["co"] else "mg/m³",
        "records_count": 365 if interval == 0 else 30
    }

@app.get("/api/v1/analytics/correlation")
def get_correlation_data():
    """Get correlation analysis between environmental and health data"""
    return {
        "timestamp": datetime.now().isoformat(),
        "correlation_data": {
            "pm25_respiratory": 0.82,
            "no2_cardiovascular": 0.74,
            "o3_respiratory": 0.68,
            "temperature_dermatitis": 0.59
        },
        "monthly_trends": [
            {"month": "Gen", "respiratory_cases": 23, "pm25": 18, "no2": 22},
            {"month": "Feb", "respiratory_cases": 29, "pm25": 22, "no2": 26},
            {"month": "Mar", "respiratory_cases": 31, "pm25": 24, "no2": 28},
            {"month": "Apr", "respiratory_cases": 45, "pm25": 35, "no2": 34},
            {"month": "Mag", "respiratory_cases": 38, "pm25": 28, "no2": 30},
            {"month": "Giu", "respiratory_cases": 42, "pm25": 32, "no2": 32}
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
