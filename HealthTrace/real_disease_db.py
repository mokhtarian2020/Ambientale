"""
FastAPI Routes for Real GESAN Infectious Disease Database
Provides REST API endpoints for accessing Italian health surveillance data
Enhanced with ARIMA time series forecasting 🔮
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging
from infectious_disease_db import db_manager
from arima_previsioni import arima_previsioni

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router for real database endpoints
router = APIRouter()

@router.get("/", summary="Database Health Check")
async def database_health():
    """Check database connection and basic info"""
    try:
        if db_manager.connect():
            summary = db_manager.get_database_summary()
            return {
                "status": "connected",
                "message": "GESAN infectious disease database is accessible",
                "database_summary": summary,
                "timestamp": "2024-12-28T10:30:00Z"
            }
        else:
            raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        logger.error(f"Database health check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check error: {str(e)}")

@router.get("/recent-cases", summary="Get Recent Infectious Disease Cases")
async def get_recent_cases(
    limit: int = Query(50, description="Maximum number of cases to return", ge=1, le=500),
    days_back: int = Query(30, description="Number of days to look back", ge=1, le=365)
):
    """Get recent infectious disease cases from the surveillance system"""
    try:
        cases = db_manager.get_recent_cases(limit=limit, days_back=days_back)
        
        return {
            "status": "success",
            "total_cases": len(cases),
            "cases": cases,
            "filters": {
                "limit": limit,
                "days_back": days_back
            },
            "timestamp": "2024-12-28T10:30:00Z"
        }
    except Exception as e:
        logger.error(f"Error fetching recent cases: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch cases: {str(e)}")

@router.get("/covid-cases", summary="Get COVID-19 Specific Data")
async def get_covid_cases(
    limit: int = Query(50, description="Maximum number of COVID cases to return", ge=1, le=500)
):
    """Get COVID-19 specific surveillance data"""
    try:
        covid_data = db_manager.get_covid_cases(limit=limit)
        
        return {
            "status": "success",
            "total_covid_cases": len(covid_data),
            "covid_cases": covid_data,
            "limit": limit,
            "timestamp": "2024-12-28T10:30:00Z"
        }
    except Exception as e:
        logger.error(f"Error fetching COVID cases: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch COVID data: {str(e)}")

@router.get("/disease-statistics", summary="Get Disease Statistics and Trends")
async def get_disease_statistics():
    """Get comprehensive disease statistics and trends"""
    try:
        stats = db_manager.get_disease_statistics()
        
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": "2024-12-28T10:30:00Z"
        }
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {str(e)}")

@router.get("/contact-tracing", summary="Get Contact Tracing Data")
async def get_contact_tracing(
    limit: int = Query(100, description="Maximum number of contacts to return", ge=1, le=1000)
):
    """Get contact tracing information from epidemiological investigations"""
    try:
        contacts = db_manager.get_contact_tracing_data(limit=limit)
        
        return {
            "status": "success",
            "total_contacts": len(contacts),
            "contacts": contacts,
            "limit": limit,
            "timestamp": "2024-12-28T10:30:00Z"
        }
    except Exception as e:
        logger.error(f"Error fetching contact data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch contact data: {str(e)}")

@router.get("/symptoms", summary="Get Symptoms Reporting Data")
async def get_symptoms(
    limit: int = Query(100, description="Maximum number of symptom reports to return", ge=1, le=1000)
):
    """Get symptoms reporting data from surveillance system"""
    try:
        symptoms = db_manager.get_symptoms_data(limit=limit)
        
        return {
            "status": "success",
            "total_symptom_reports": len(symptoms),
            "symptoms": symptoms,
            "limit": limit,
            "timestamp": "2024-12-28T10:30:00Z"
        }
    except Exception as e:
        logger.error(f"Error fetching symptoms data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch symptoms data: {str(e)}")

@router.get("/municipality/{istat_code}", summary="Get Cases by Municipality")
async def get_cases_by_municipality(
    istat_code: str
):
    """Get infectious disease cases for a specific municipality using ISTAT code"""
    try:
        cases = db_manager.search_cases_by_municipality(istat_code)
        
        return {
            "status": "success",
            "municipality_istat_code": istat_code,
            "total_cases": len(cases),
            "cases": cases,
            "timestamp": "2024-12-28T10:30:00Z"
        }
    except Exception as e:
        logger.error(f"Error fetching municipality cases: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch municipality data: {str(e)}")

@router.get("/tables", summary="List Database Tables")
async def list_tables():
    """List all available tables in the infectious disease database"""
    try:
        query = """
            SELECT 
                table_name,
                (SELECT COUNT(*) FROM information_schema.columns 
                 WHERE table_name = t.table_name AND table_schema = 'public') as columns
            FROM information_schema.tables t
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            AND table_name LIKE '%malattie_infettive%'
            ORDER BY table_name
        """
        
        tables = db_manager.execute_query(query)
        
        # Add row counts
        for table in tables:
            try:
                count_query = f'SELECT COUNT(*) as row_count FROM "{table["table_name"]}"'
                count_result = db_manager.execute_query(count_query)
                table["row_count"] = count_result[0]["row_count"] if count_result else 0
            except:
                table["row_count"] = 0
        
        return {
            "status": "success",
            "total_tables": len(tables),
            "tables": tables,
            "timestamp": "2024-12-28T10:30:00Z"
        }
    except Exception as e:
        logger.error(f"Error listing tables: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list tables: {str(e)}")

@router.get("/disease-by-region", summary="Get Disease Cases by Region")
async def get_disease_by_region():
    """Get top diseases distributed by Italian regions using ISTAT codes"""
    try:
        # Get top 3 diseases with geographic breakdown
        query = """
            SELECT 
                malattia_segnalata,
                comune_residenza_codice_istat,
                COUNT(*) as case_count,
                MAX(data_segnalazione) as latest_case,
                MIN(data_segnalazione) as earliest_case
            FROM gesan_malattie_infettive_segnalazione
            WHERE malattia_segnalata IN (
                'COVID 19 (U07.1)',
                'SCABBIA (1330)', 
                'VARICELLA (052)'
            )
            AND comune_residenza_codice_istat IS NOT NULL 
            AND comune_residenza_codice_istat != ''
            GROUP BY malattia_segnalata, comune_residenza_codice_istat
            ORDER BY malattia_segnalata, case_count DESC
        """
        
        results = db_manager.execute_query(query)
        
        # Organize data by disease
        disease_data = {}
        for row in results:
            disease = row['malattia_segnalata']
            if disease not in disease_data:
                disease_data[disease] = []
            disease_data[disease].append(row)
        
        return {
            "status": "success",
            "diseases": ["COVID 19 (U07.1)", "SCABBIA (1330)", "VARICELLA (052)"],
            "disease_data": disease_data,
            "total_records": len(results),
            "timestamp": "2024-12-28T10:30:00Z"
        }
    except Exception as e:
        logger.error(f"Error getting disease by region data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get disease data: {str(e)}")

@router.get("/monthly-trends", summary="Get Monthly Disease Trends")
async def get_monthly_trends():
    """Get monthly trends for top 3 diseases"""
    try:
        query = """
            SELECT 
                malattia_segnalata,
                DATE_TRUNC('month', data_segnalazione) as month,
                COUNT(*) as cases
            FROM gesan_malattie_infettive_segnalazione
            WHERE malattia_segnalata IN (
                'COVID 19 (U07.1)',
                'SCABBIA (1330)', 
                'VARICELLA (052)'
            )
            AND data_segnalazione >= CURRENT_DATE - INTERVAL '24 months'
            GROUP BY malattia_segnalata, DATE_TRUNC('month', data_segnalazione)
            ORDER BY month, malattia_segnalata
        """
        
        results = db_manager.execute_query(query)
        
        return {
            "status": "success",
            "monthly_trends": results,
            "timestamp": "2024-12-28T10:30:00Z"
        }
    except Exception as e:
        logger.error(f"Error getting monthly trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get trends: {str(e)}")

@router.get("/three-diseases-stats", summary="Get Statistics for Influenza, Legionellosi, and Hepatitis A")
async def get_three_diseases_statistics():
    """Get comprehensive statistics for the top 3 diseases: Influenza, Legionellosi, and Hepatitis A"""
    try:
        stats = {}
        
        # 1. Influenza data
        influenza_query = """
            SELECT 
                i.id,
                i.data_insorgenza_primi_sintomi,
                i.ricovero_ospedaliero,
                i.nome_ospedale,
                s.comune_residenza_codice_istat,
                s.data_segnalazione,
                s.stato_attuale
            FROM gesan_malattie_infettive_ie_influenza i
            JOIN gesan_malattie_infettive_segnalazione s ON s.id = i.id
            WHERE s.malattia_segnalata LIKE '%INFLUEN%'
            ORDER BY i.data_insorgenza_primi_sintomi DESC
        """
        stats["influenza"] = db_manager.execute_query(influenza_query)
        
        # 2. Legionellosi data
        legionella_query = """
            SELECT 
                l.id,
                l.data_insorgenza_sintomi,
                l.ricovero_ospedaliero,
                l.data_ricovero,
                s.comune_residenza_codice_istat,
                s.data_segnalazione,
                s.stato_attuale
            FROM gesan_malattie_infettive_ie_legionellosi l
            JOIN gesan_malattie_infettive_segnalazione s ON s.id = l.id
            WHERE s.malattia_segnalata LIKE '%LEGION%'
            ORDER BY l.data_insorgenza_sintomi DESC
        """
        stats["legionellosi"] = db_manager.execute_query(legionella_query)
        
        # 3. Hepatitis A data  
        hepatitis_query = """
            SELECT 
                h.id,
                h.malattia_diventato_giallo,
                h.titolo_studio,
                h.professione,
                s.comune_residenza_codice_istat,
                s.data_segnalazione,
                s.data_inizio_sintomi,
                s.stato_attuale
            FROM gesan_malattie_infettive_ie_epatite_a h
            JOIN gesan_malattie_infettive_segnalazione s ON s.id = h.id
            WHERE s.malattia_segnalata LIKE '%EPATITE%A%'
            ORDER BY s.data_inizio_sintomi DESC
        """
        stats["hepatitis_a"] = db_manager.execute_query(hepatitis_query)
        
        # Geographic distribution by ISTAT codes for each disease
        geographic_stats = {}
        
        for disease_name, disease_key in [("INFLUEN", "influenza"), ("LEGION", "legionellosi"), ("EPATITE%A", "hepatitis_a")]:
            geo_query = """
                SELECT 
                    comune_residenza_codice_istat,
                    COUNT(*) as case_count,
                    MAX(data_segnalazione) as latest_case
                FROM gesan_malattie_infettive_segnalazione
                WHERE malattia_segnalata LIKE %s
                AND comune_residenza_codice_istat IS NOT NULL 
                AND comune_residenza_codice_istat != ''
                GROUP BY comune_residenza_codice_istat
                ORDER BY case_count DESC
            """
            geographic_stats[disease_key] = db_manager.execute_query(geo_query, (f'%{disease_name}%',))
        
        # Monthly trends for each disease
        monthly_trends = {}
        
        for disease_name, disease_key in [("INFLUEN", "influenza"), ("LEGION", "legionellosi"), ("EPATITE%A", "hepatitis_a")]:
            trends_query = """
                SELECT 
                    DATE_TRUNC('month', data_segnalazione) as month,
                    COUNT(*) as cases
                FROM gesan_malattie_infettive_segnalazione
                WHERE malattia_segnalata LIKE %s
                AND data_segnalazione >= CURRENT_DATE - INTERVAL '24 months'
                GROUP BY DATE_TRUNC('month', data_segnalazione)
                ORDER BY month
            """
            monthly_trends[disease_key] = db_manager.execute_query(trends_query, (f'%{disease_name}%',))
        
        # Generate ARIMA predictions for each disease using advanced time series forecasting
        predictions = {}
        model_info = {}
        
        for disease_name, disease_key in [("Influenza", "influenza"), ("Legionellosi", "legionellosi"), ("Epatite A", "hepatitis_a")]:
            trends = monthly_trends[disease_key]
            
            try:
                if len(trends) >= 6:  # ARIMA needs at least 6 data points
                    logger.info(f"🔮 Fitting ARIMA model for {disease_name} with {len(trends)} data points")
                    
                    # Prepare time series data for ARIMA
                    ts_data, ts_index = arima_previsioni.prepare_time_series_data(trends)
                    
                    # Fit ARIMA model
                    model_results = arima_previsioni.fit_arima_model(ts_data, disease_key)
                    model_info[disease_key] = model_results
                    
                    if model_results.get("fitted_successfully", False):
                        # Generate ARIMA predictions
                        predictions[disease_key] = arima_previsioni.generate_arima_predictions(disease_key, periods=6)
                        logger.info(f"✅ Generated ARIMA predictions for {disease_name}")
                    else:
                        # Fallback to simple predictions if ARIMA fails
                        logger.warning(f"⚠️ ARIMA failed for {disease_name}, using fallback method")
                        predictions[disease_key] = arima_previsioni._fallback_simple_prediction(disease_key, 6)
                
                else:
                    logger.warning(f"⚠️ Insufficient data for {disease_name} ARIMA (need ≥6, have {len(trends)})")
                    predictions[disease_key] = arima_previsioni._fallback_simple_prediction(disease_key, 6)
                    model_info[disease_key] = {"error": "Insufficient data for ARIMA", "fallback_used": True}
                    
            except Exception as e:
                logger.error(f"❌ ARIMA prediction failed for {disease_name}: {str(e)}")
                predictions[disease_key] = arima_previsioni._fallback_simple_prediction(disease_key, 6)
                model_info[disease_key] = {"error": str(e), "fallback_used": True}

        return {
            "status": "success",
            "diseases": {
                "influenza": {
                    "name": "Influenza",
                    "total_cases": len(stats["influenza"]),
                    "cases": stats["influenza"],
                    "geographic_distribution": geographic_stats["influenza"],
                    "monthly_trends": monthly_trends["influenza"],
                    "predictions": predictions["influenza"],
                    "arima_model_info": model_info.get("influenza", {})
                },
                "legionellosi": {
                    "name": "Legionellosi", 
                    "total_cases": len(stats["legionellosi"]),
                    "cases": stats["legionellosi"],
                    "geographic_distribution": geographic_stats["legionellosi"],
                    "monthly_trends": monthly_trends["legionellosi"],
                    "predictions": predictions["legionellosi"],
                    "arima_model_info": model_info.get("legionellosi", {})
                },
                "hepatitis_a": {
                    "name": "Epatite A",
                    "total_cases": len(stats["hepatitis_a"]),
                    "cases": stats["hepatitis_a"],
                    "geographic_distribution": geographic_stats["hepatitis_a"],
                    "monthly_trends": monthly_trends["hepatitis_a"],
                    "predictions": predictions["hepatitis_a"],
                    "arima_model_info": model_info.get("hepatitis_a", {})
                }
            },
            "summary": {
                "total_cases_all_diseases": len(stats["influenza"]) + len(stats["legionellosi"]) + len(stats["hepatitis_a"]),
                "diseases_analyzed": 3,
                "prediction_method": "ARIMA Time Series Forecasting 🔮",
                "forecast_horizon": "6 months",
                "model_performance": {
                    disease: info for disease, info in model_info.items() if "error" not in info
                }
            },
            "timestamp": "2026-02-26T10:30:00Z"
        }
    except Exception as e:
        logger.error(f"Error fetching three diseases statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch disease statistics: {str(e)}")

@router.get("/query", summary="Execute Custom Query")
async def execute_query(
    table: str = Query(..., description="Table name to query"),
    limit: int = Query(10, description="Maximum number of rows to return", ge=1, le=100)
):
    """Execute a custom query on a specific table"""
    try:
        # Security: Only allow queries on malattie_infettive tables
        if 'malattie_infettive' not in table.lower():
            raise HTTPException(status_code=400, detail="Only infectious disease tables are allowed")
        
        query = f'SELECT * FROM "{table}" LIMIT %s'
        results = db_manager.execute_query(query, (limit,))
        
        return {
            "status": "success",
            "table": table,
            "total_rows": len(results),
            "data": results,
            "limit": limit,
            "timestamp": "2024-12-28T10:30:00Z"
        }
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")
