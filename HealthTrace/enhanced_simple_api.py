#!/usr/bin/env python3
"""
Enhanced HealthTrace API Server with Synthetic Data
Contains realistic Italian environmental health data for testing all models
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
import json

app = FastAPI(
    title="HealthTrace API - Enhanced with Synthetic Data",
    description="Environmental Health Monitoring System with Realistic Italian Data",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3200", "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced data from synthetic generation
ENHANCED_DATA = {
  "dashboard_summary": {
    "total_reports": 350,
    "total_investigations": 27,
    "active_patients": 105,
    "recovered_patients": 244,
    "regions": [
      "Campania",
      "Calabria",
      "Molise"
    ],
    "last_updated": "2025-10-30T15:22:44.002145",
    "environmental_correlations": {
      "pm25_respiratory": 0.82,
      "no2_cardiovascular": 0.74,
      "o3_respiratory": 0.68,
      "temperature_infectious": -0.59,
      "humidity_legionellosis": 0.71,
      "ecoli_hepatitis": 0.85,
      "pm25_influenza": 0.07,
      "temperature_influenza": -0.08,
      "pm25_legionellosis": 0.02,
      "temperature_legionellosis": -0.01,
      "pm25_hepatitis_a": 0.0,
      "temperature_hepatitis_a": -0.01
    },
    "monthly_trends": [
      {
        "month": "Gen",
        "influenza_cases": 21,
        "legionellosis_cases": 4,
        "hepatitis_a_cases": 0,
        "total_cases": 25,
        "pm25": 15.5,
        "no2": 22.0,
        "temperature": 18.1,
        "humidity": 60.6
      },
      {
        "month": "Feb",
        "influenza_cases": 14,
        "legionellosis_cases": 4,
        "hepatitis_a_cases": 0,
        "total_cases": 18,
        "pm25": 11.8,
        "no2": 17.8,
        "temperature": 23.3,
        "humidity": 54.0
      },
      {
        "month": "Mar",
        "influenza_cases": 7,
        "legionellosis_cases": 5,
        "hepatitis_a_cases": 0,
        "total_cases": 12,
        "pm25": 9.5,
        "no2": 16.1,
        "temperature": 26.4,
        "humidity": 51.3
      },
      {
        "month": "Apr",
        "influenza_cases": 7,
        "legionellosis_cases": 4,
        "hepatitis_a_cases": 0,
        "total_cases": 11,
        "pm25": 9.8,
        "no2": 15.7,
        "temperature": 26.6,
        "humidity": 51.0
      },
      {
        "month": "Mag",
        "influenza_cases": 14,
        "legionellosis_cases": 1,
        "hepatitis_a_cases": 0,
        "total_cases": 15,
        "pm25": 11.8,
        "no2": 18.0,
        "temperature": 23.3,
        "humidity": 54.6
      },
      {
        "month": "Giu",
        "influenza_cases": 20,
        "legionellosis_cases": 1,
        "hepatitis_a_cases": 0,
        "total_cases": 21,
        "pm25": 15.7,
        "no2": 22.3,
        "temperature": 18.2,
        "humidity": 61.4
      },
      {
        "month": "Lug",
        "influenza_cases": 22,
        "legionellosis_cases": 5,
        "hepatitis_a_cases": 1,
        "total_cases": 28,
        "pm25": 20.2,
        "no2": 27.5,
        "temperature": 12.0,
        "humidity": 68.7
      },
      {
        "month": "Ago",
        "influenza_cases": 44,
        "legionellosis_cases": 4,
        "hepatitis_a_cases": 0,
        "total_cases": 48,
        "pm25": 24.3,
        "no2": 31.6,
        "temperature": 6.6,
        "humidity": 75.4
      },
      {
        "month": "Set",
        "influenza_cases": 45,
        "legionellosis_cases": 4,
        "hepatitis_a_cases": 0,
        "total_cases": 49,
        "pm25": 26.3,
        "no2": 35.0,
        "temperature": 3.5,
        "humidity": 79.0
      },
      {
        "month": "Ott",
        "influenza_cases": 33,
        "legionellosis_cases": 5,
        "hepatitis_a_cases": 0,
        "total_cases": 38,
        "pm25": 26.6,
        "no2": 34.9,
        "temperature": 3.7,
        "humidity": 79.0
      },
      {
        "month": "Nov",
        "influenza_cases": 48,
        "legionellosis_cases": 6,
        "hepatitis_a_cases": 1,
        "total_cases": 55,
        "pm25": 24.3,
        "no2": 31.7,
        "temperature": 6.7,
        "humidity": 75.0
      },
      {
        "month": "Dic",
        "influenza_cases": 25,
        "legionellosis_cases": 5,
        "hepatitis_a_cases": 0,
        "total_cases": 30,
        "pm25": 20.2,
        "no2": 28.1,
        "temperature": 12.0,
        "humidity": 69.4
      }
    ],
    "disease_breakdown": {
      "influenza": 300,
      "legionellosis": 48,
      "hepatitis_a": 2
    },
    "data_sources": {
      "ARPA_CAMPANIA": 83055,
      "ISTAT": 54825,
      "SYNTHETIC": 137880
    }
  },
  "influenza_analytics": {
    "disease_name": "influenza",
    "total_cases": 300,
    "analysis_date": "2025-10-30T15:22:44.015636",
    "case_distribution": {
      "by_severity": {
        "mild": 210,
        "moderate": 67,
        "severe": 23
      },
      "by_age_group": {
        "0-18": 60,
        "19-35": 85,
        "36-50": 84,
        "51-65": 55,
        "65+": 16
      },
      "by_gender": {
        "M": 151,
        "F": 149
      },
      "by_region": {
        "Molise": 116,
        "Campania": 96,
        "Calabria": 88
      }
    },
    "temporal_analysis": {
      "cases_by_month": {
        "1": 21,
        "2": 14,
        "3": 7,
        "4": 7,
        "5": 14,
        "6": 20,
        "7": 22,
        "8": 44,
        "9": 45,
        "10": 33,
        "11": 48,
        "12": 25
      },
      "peak_months": [
        "November",
        "September"
      ]
    },
    "environmental_associations": {
      "primary_factors": [
        "PM2.5",
        "PM10",
        "temperature",
        "humidity"
      ],
      "correlation_strength": "strong",
      "lag_period_days": "0-7",
      "threshold_effects": {
        "PM2.5": "> 25 \u03bcg/m\u00b3",
        "temperature": "< 10\u00b0C"
      }
    },
    "risk_factors": {
      "high_risk_age_groups": [
        "< 5 years",
        "> 65 years",
        "pregnant women"
      ],
      "environmental_thresholds": {
        "PM2.5": "> 25 \u03bcg/m\u00b3",
        "temperature": "< 10\u00b0C",
        "humidity": "> 70%"
      },
      "seasonal_patterns": {
        "peak_season": "Winter (December-February)",
        "low_season": "Summer (June-August)",
        "pattern": "Clear winter peak with PM2.5/temperature correlation"
      }
    }
  },
  "legionellosis_analytics": {
    "disease_name": "legionellosis",
    "total_cases": 48,
    "analysis_date": "2025-10-30T15:22:44.018949",
    "case_distribution": {
      "by_severity": {
        "severe": 35,
        "moderate": 13
      },
      "by_age_group": {
        "0-18": 0,
        "19-35": 0,
        "36-50": 10,
        "51-65": 13,
        "65+": 25
      },
      "by_gender": {
        "M": 29,
        "F": 19
      },
      "by_region": {
        "Molise": 20,
        "Campania": 14,
        "Calabria": 14
      }
    },
    "temporal_analysis": {
      "cases_by_month": {
        "1": 4,
        "2": 4,
        "3": 5,
        "4": 4,
        "5": 1,
        "6": 1,
        "7": 5,
        "8": 4,
        "9": 4,
        "10": 5,
        "11": 6,
        "12": 5
      },
      "peak_months": [
        "November",
        "March"
      ]
    },
    "environmental_associations": {
      "primary_factors": [
        "water_temperature",
        "humidity",
        "precipitation"
      ],
      "correlation_strength": "very_strong",
      "lag_period_days": "7-21",
      "threshold_effects": {
        "water_temperature": "> 25\u00b0C",
        "humidity": "> 70%"
      }
    },
    "risk_factors": {
      "high_risk_age_groups": [
        "> 50 years",
        "immunocompromised",
        "chronic disease"
      ],
      "environmental_thresholds": {
        "water_temperature": "> 25\u00b0C",
        "air_temperature": "> 25\u00b0C",
        "humidity": "> 70%"
      },
      "seasonal_patterns": {
        "peak_season": "Summer (June-September)",
        "low_season": "Winter (December-March)",
        "pattern": "Warm weather peak with water temperature correlation"
      }
    }
  },
  "hepatitis_a_analytics": {
    "disease_name": "hepatitis_a",
    "total_cases": 2,
    "analysis_date": "2025-10-30T15:22:44.021447",
    "case_distribution": {
      "by_severity": {
        "mild": 2
      },
      "by_age_group": {
        "0-18": 0,
        "19-35": 1,
        "36-50": 1,
        "51-65": 0,
        "65+": 0
      },
      "by_gender": {
        "M": 2
      },
      "by_region": {
        "Molise": 1,
        "Campania": 0,
        "Calabria": 1
      }
    },
    "temporal_analysis": {
      "cases_by_month": {
        "7": 1,
        "11": 1
      },
      "peak_months": [
        "July",
        "November"
      ]
    },
    "environmental_associations": {
      "primary_factors": [
        "E.coli",
        "pH",
        "residual_chlorine",
        "precipitation"
      ],
      "correlation_strength": "strong",
      "lag_period_days": "14-28",
      "threshold_effects": {
        "E.coli": "> 100 CFU/100ml",
        "pH": "< 6.5 or > 8.5"
      }
    },
    "risk_factors": {
      "high_risk_age_groups": [
        "< 30 years",
        "travelers",
        "food handlers"
      ],
      "environmental_thresholds": {
        "E.coli": "> 100 CFU/100ml",
        "pH": "< 6.5 or > 8.5",
        "chlorine": "< 0.2 mg/L"
      },
      "seasonal_patterns": {
        "peak_season": "Autumn (September-November)",
        "low_season": "Spring (March-May)",
        "pattern": "Post-summer peak after heavy rains"
      }
    }
  },
  "environmental_factors": {
    "analysis_date": "2025-10-30T15:22:44.031070",
    "total_measurements": 137880,
    "parameters_analyzed": 16,
    "geographic_coverage": 15,
    "parameter_statistics": {
      "C6H6": {
        "mean": 2.51,
        "std": 0.98,
        "min": 0.5,
        "max": 6.2
      },
      "CO": {
        "mean": 1.21,
        "std": 0.5,
        "min": 0.1,
        "max": 2.92
      },
      "NO2": {
        "mean": 25.1,
        "std": 10.58,
        "min": 5.0,
        "max": 64.91
      },
      "O3": {
        "mean": 80.29,
        "std": 34.43,
        "min": 10.0,
        "max": 178.32
      },
      "PM10": {
        "mean": 30.03,
        "std": 13.14,
        "min": 5.0,
        "max": 72.02
      },
      "PM25": {
        "mean": 18.03,
        "std": 7.92,
        "min": 3.0,
        "max": 42.59
      },
      "SO2": {
        "mean": 7.98,
        "std": 2.97,
        "min": 1.0,
        "max": 18.69
      },
      "ecoli_count": {
        "mean": 7.9,
        "std": 16.91,
        "min": 0.03,
        "max": 204.87
      },
      "humidity": {
        "mean": 65.0,
        "std": 14.36,
        "min": 30.0,
        "max": 95.0
      },
      "ph": {
        "mean": 7.21,
        "std": 0.3,
        "min": 6.5,
        "max": 8.25
      },
      "precipitation": {
        "mean": 2.35,
        "std": 5.41,
        "min": 0.0,
        "max": 69.91
      },
      "pressure": {
        "mean": 1013.07,
        "std": 10.05,
        "min": 978.05,
        "max": 1048.92
      },
      "residual_chlorine": {
        "mean": 0.51,
        "std": 0.2,
        "min": 0.1,
        "max": 1.16
      },
      "temperature": {
        "mean": 15.0,
        "std": 8.96,
        "min": -7.24,
        "max": 38.47
      },
      "water_temperature": {
        "mean": 12.11,
        "std": 5.94,
        "min": -2.33,
        "max": 24.76
      },
      "wind_speed": {
        "mean": 3.56,
        "std": 1.96,
        "min": 0.0,
        "max": 11.35
      }
    },
    "data_quality": {
      "completeness": 100.0,
      "validation_rate": 100.0
    },
    "threshold_exceedances": {
      "PM10": {
        "threshold": 50,
        "exceedance_rate": 6.4,
        "max_value": 72.02,
        "days_exceeded": 705
      },
      "PM25": {
        "threshold": 25,
        "exceedance_rate": 21.3,
        "max_value": 42.59,
        "days_exceeded": 2339
      },
      "O3": {
        "threshold": 120,
        "exceedance_rate": 13.9,
        "max_value": 178.32,
        "days_exceeded": 1527
      },
      "NO2": {
        "threshold": 40,
        "exceedance_rate": 8.3,
        "max_value": 64.91,
        "days_exceeded": 915
      }
    },
    "trend_analysis": {
      "PM25": {
        "seasonal_pattern": "winter_peak",
        "average_value": 18.03,
        "seasonal_variation": 6.45,
        "monthly_averages": {
          "1": 15.55,
          "2": 11.83,
          "3": 9.53,
          "4": 9.78,
          "5": 11.77,
          "6": 15.69,
          "7": 20.19,
          "8": 24.34,
          "9": 26.27,
          "10": 26.57,
          "11": 24.26,
          "12": 20.16
        }
      },
      "PM10": {
        "seasonal_pattern": "winter_peak",
        "average_value": 30.03,
        "seasonal_variation": 10.87,
        "monthly_averages": {
          "1": 26.21,
          "2": 19.53,
          "3": 15.84,
          "4": 15.82,
          "5": 19.79,
          "6": 25.49,
          "7": 33.96,
          "8": 40.51,
          "9": 44.28,
          "10": 43.98,
          "11": 40.43,
          "12": 33.89
        }
      },
      "temperature": {
        "seasonal_pattern": "summer_peak",
        "average_value": 15.0,
        "seasonal_variation": 8.73,
        "monthly_averages": {
          "1": 18.14,
          "2": 23.27,
          "3": 26.44,
          "4": 26.58,
          "5": 23.29,
          "6": 18.24,
          "7": 12.03,
          "8": 6.62,
          "9": 3.52,
          "10": 3.66,
          "11": 6.73,
          "12": 12.02
        }
      },
      "humidity": {
        "seasonal_pattern": "summer_peak",
        "average_value": 65.0,
        "seasonal_variation": 10.78,
        "monthly_averages": {
          "1": 60.63,
          "2": 53.99,
          "3": 51.27,
          "4": 50.97,
          "5": 54.64,
          "6": 61.37,
          "7": 68.68,
          "8": 75.42,
          "9": 78.96,
          "10": 78.98,
          "11": 75.03,
          "12": 69.37
        }
      }
    }
  },
  "correlation_analysis": {
    "analysis_date": "2025-10-30T15:22:44.127949",
    "methodology": "Pearson correlation with lag analysis",
    "diseases_analyzed": [
      "influenza",
      "legionellosis",
      "hepatitis_a"
    ],
    "environmental_factors": [
      "PM10",
      "PM25",
      "O3",
      "NO2",
      "SO2",
      "C6H6",
      "CO",
      "temperature",
      "humidity",
      "precipitation",
      "wind_speed",
      "pressure",
      "ph",
      "ecoli_count",
      "residual_chlorine",
      "water_temperature"
    ],
    "correlation_matrix": {
      "influenza": {
        "primary_factors": [
          "PM2.5",
          "PM10",
          "temperature",
          "humidity"
        ],
        "correlation_strength": "strong",
        "lag_period_days": "0-7",
        "threshold_effects": {
          "PM2.5": "> 25 \u03bcg/m\u00b3",
          "temperature": "< 10\u00b0C"
        }
      },
      "legionellosis": {
        "primary_factors": [
          "water_temperature",
          "humidity",
          "precipitation"
        ],
        "correlation_strength": "very_strong",
        "lag_period_days": "7-21",
        "threshold_effects": {
          "water_temperature": "> 25\u00b0C",
          "humidity": "> 70%"
        }
      },
      "hepatitis_a": {
        "primary_factors": [
          "E.coli",
          "pH",
          "residual_chlorine",
          "precipitation"
        ],
        "correlation_strength": "strong",
        "lag_period_days": "14-28",
        "threshold_effects": {
          "E.coli": "> 100 CFU/100ml",
          "pH": "< 6.5 or > 8.5"
        }
      }
    },
    "statistical_significance": {},
    "model_recommendations": {
      "influenza": {
        "primary_model": "GAM with lag terms",
        "secondary_models": [
          "ARIMAX",
          "Random Forest"
        ],
        "spatial_analysis": "Moran's I for geographic clustering",
        "forecasting": "ARIMAX with PM2.5 and temperature",
        "interpretation": "GAM for exposure-response curves"
      },
      "legionellosis": {
        "primary_model": "DLNM for temperature effects",
        "secondary_models": [
          "Case-Crossover",
          "Spatial Regression"
        ],
        "spatial_analysis": "Getis-Ord Gi* for hotspot detection",
        "forecasting": "ARIMAX with water temperature",
        "interpretation": "DLNM for lag structure analysis"
      },
      "hepatitis_a": {
        "primary_model": "GLM with water quality indicators",
        "secondary_models": [
          "Random Forest",
          "DLNM"
        ],
        "spatial_analysis": "Spatial regression for contamination mapping",
        "forecasting": "ARIMAX with precipitation and E.coli",
        "interpretation": "Random Forest for factor importance"
      }
    }
  }
}

@app.get("/")
def read_root():
    return {
        "message": "HealthTrace API with Synthetic Data is running!",
        "version": "2.0.0",
        "status": "healthy",
        "data_sources": ["SYNTHETIC_ARPA_CAMPANIA", "SYNTHETIC_ISTAT", "SYNTHETIC_HEALTH"],
        "diseases_supported": ["influenza", "legionellosis", "hepatitis_a"],
        "total_cases": ENHANCED_DATA["dashboard_summary"]["total_reports"],
        "data_period": "2023-01-01 to 2024-12-31"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "healthtrace-api-enhanced"}

@app.get("/api/v1/dashboard/summary")
def get_dashboard_summary():
    """Get enhanced dashboard summary with synthetic data"""
    return ENHANCED_DATA["dashboard_summary"]

@app.get("/api/v1/diseases/{disease_name}/analytics")
def get_disease_analytics(disease_name: str):
    """Get disease-specific analytics"""
    analytics_key = f"{disease_name}_analytics"
    if analytics_key in ENHANCED_DATA:
        return ENHANCED_DATA[analytics_key]
    else:
        return {"error": f"No analytics available for {disease_name}"}

@app.get("/api/v1/environmental/factors")
def get_environmental_factors():
    """Get environmental factor analysis"""
    return ENHANCED_DATA.get("environmental_factors", {"error": "No environmental data"})

@app.get("/api/v1/analytics/correlation")
def get_correlation_analysis(
    disease: str = Query(None, description="Disease type"),
    istat_code: str = Query(None, description="ISTAT geographic code"),
    pollutant: str = Query(None, description="Environmental pollutant")
):
    """Get correlation analysis between environmental factors and diseases"""
    
    correlation_data = ENHANCED_DATA.get("correlation_analysis", {})
    
    if disease:
        # Filter by disease
        disease_correlations = correlation_data.get("correlation_matrix", {}).get(disease, {})
        return {
            "disease": disease,
            "correlations": disease_correlations,
            "analysis_date": datetime.now().isoformat(),
            "methodology": "Synthetic data analysis"
        }
    
    return correlation_data

@app.get("/api/v1/diseases/")
def list_diseases():
    """List all supported diseases"""
    return {
        "diseases": [
            {
                "name": "influenza",
                "category": "respiratory", 
                "environmental_factors": ["PM2.5", "PM10", "temperature", "humidity"],
                "total_cases": len(ENHANCED_DATA.get("influenza_analytics", {}).get("case_distribution", {})),
                "models_available": ["GAM", "ARIMAX", "Random Forest", "Spatial Analysis"]
            },
            {
                "name": "legionellosis",
                "category": "water_aerosol",
                "environmental_factors": ["water_temperature", "humidity", "precipitation"],
                "total_cases": len(ENHANCED_DATA.get("legionellosis_analytics", {}).get("case_distribution", {})),
                "models_available": ["DLNM", "Case-Crossover", "Spatial Regression", "ARIMAX"]
            },
            {
                "name": "hepatitis_a", 
                "category": "foodborne_waterborne",
                "environmental_factors": ["E.coli", "pH", "residual_chlorine", "precipitation"],
                "total_cases": len(ENHANCED_DATA.get("hepatitis_a_analytics", {}).get("case_distribution", {})),
                "models_available": ["GLM", "Random Forest", "DLNM", "Spatial Regression"]
            }
        ],
        "total_diseases": 3,
        "data_source": "synthetic_italian_health_data"
    }

@app.get("/api/v1/istat/{istat_code}/{year}/{interval}/{function}/{pollutant}/")
def get_istat_environmental_data(
    istat_code: str,
    year: int,
    interval: str,
    function: str, 
    pollutant: str
):
    """Get environmental data in Italian ISTAT format"""
    
    # Generate realistic response based on synthetic data patterns
    import random
    import numpy as np
    
    # Seasonal patterns
    if interval == "mensile":
        months = list(range(1, 13))
    elif interval == "trimestrale":
        months = [3, 6, 9, 12]  # End of quarters
    else:  # annuale
        months = [12]
    
    data = []
    for month in months:
        # Seasonal factor
        seasonal = np.sin(2 * np.pi * month / 12)
        
        # Base values with seasonal variation
        if pollutant.upper() == "PM25":
            base_value = 20 + 10 * (-seasonal) + random.gauss(0, 5)
        elif pollutant.upper() == "PM10":
            base_value = 30 + 15 * (-seasonal) + random.gauss(0, 8)
        elif pollutant.upper() == "O3":
            base_value = 80 + 40 * seasonal + random.gauss(0, 20)
        elif pollutant.upper() == "NO2":
            base_value = 25 + 10 * (-seasonal) + random.gauss(0, 8)
        else:
            base_value = 15 + 5 * seasonal + random.gauss(0, 3)
        
        value = max(1, base_value)
        
        data.append({
            "istat_code": istat_code,
            "year": year,
            "month": month,
            "pollutant": pollutant.upper(),
            "function": function,
            "value": round(value, 2),
            "unit": "μg/m³",
            "data_source": "SYNTHETIC_ARPA"
        })
    
    return {
        "data": data,
        "metadata": {
            "istat_code": istat_code,
            "year": year,
            "interval": interval,
            "function": function,
            "pollutant": pollutant.upper(),
            "total_records": len(data),
            "data_source": "synthetic_arpa_campania"
        }
    }

@app.get("/api/v1/models/available")
def get_available_models():
    """Get all available analytical models"""
    return {
        "statistical_models": [
            {
                "name": "GAM",
                "full_name": "Generalized Additive Model",
                "purpose": "Non-linear exposure-response relationships",
                "diseases": ["influenza", "legionellosis", "hepatitis_a"],
                "implementation_status": "available"
            },
            {
                "name": "GLM", 
                "full_name": "Generalized Linear Model",
                "purpose": "Linear correlations with lag terms",
                "diseases": ["influenza", "hepatitis_a"],
                "implementation_status": "available"
            },
            {
                "name": "DLNM",
                "full_name": "Distributed Lag Non-Linear Model", 
                "purpose": "Delayed and non-linear effects",
                "diseases": ["legionellosis", "hepatitis_a"],
                "implementation_status": "available"
            },
            {
                "name": "ARIMAX",
                "full_name": "Autoregressive Integrated Moving Average with Exogenous Variables",
                "purpose": "Time series forecasting",
                "diseases": ["influenza", "legionellosis", "hepatitis_a"],
                "implementation_status": "available"
            }
        ],
        "machine_learning_models": [
            {
                "name": "Random Forest",
                "purpose": "Variable importance and non-linear relationships",
                "diseases": ["influenza", "legionellosis", "hepatitis_a"],
                "implementation_status": "available"
            },
            {
                "name": "Gradient Boosting",
                "purpose": "Advanced non-linear modeling",
                "diseases": ["influenza", "legionellosis", "hepatitis_a"], 
                "implementation_status": "available"
            }
        ],
        "spatial_models": [
            {
                "name": "Moran's I",
                "purpose": "Spatial autocorrelation detection",
                "diseases": ["influenza"],
                "implementation_status": "available"
            },
            {
                "name": "Getis-Ord Gi*",
                "purpose": "Hotspot identification",
                "diseases": ["legionellosis"],
                "implementation_status": "available"
            },
            {
                "name": "Spatial Regression",
                "purpose": "Geographic risk modeling",
                "diseases": ["hepatitis_a"],
                "implementation_status": "available"
            }
        ],
        "total_models": 10,
        "platform_status": "all_models_available"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
