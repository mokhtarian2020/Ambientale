"""
ISTAT Environmental Analytics API Endpoints
Implements the specified API patterns for environmental data analysis:
- /istat/{istat_code}/{year}/{interval}/{function}/{pollutant}/
- /climate/{istat_code}/{year}/{interval}/{measurement}/{function}/

Based on Italian specifications for environmental health monitoring
targeting Molise, Campania, and Calabria regions.
"""

from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from datetime import date, datetime
import pandas as pd

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User, UserRole
from app.models.environmental import EnvironmentalData, ClimateData

router = APIRouter()

# Supported pollutants as per ARPA Campania specifications
SUPPORTED_POLLUTANTS = [
    "PM10", "PM25", "O3", "NO2", "SO2", "C6H6", "CO", "As_in_PM10"
]

# Supported climate measurements
SUPPORTED_CLIMATE_MEASUREMENTS = [
    "temperature", "humidity", "precipitation", "wind_speed", 
    "wind_direction", "pressure", "solar_radiation"
]

# Supported functions
SUPPORTED_FUNCTIONS = [
    "media",      # mean/average
    "massimo",    # maximum
    "minimo",     # minimum
    "somma",      # sum
    "mediana",    # median
    "varianza",   # variance
    "giorni_superamento"  # days above limit
]


@router.get("/istat/{istat_code}/{year}/{interval}/{function}/{pollutant}/")
async def get_pollutant_analytics(
    istat_code: str = Path(..., description="ISTAT code (commune/province/region)"),
    year: int = Path(..., description="Year of interest"),
    interval: int = Path(..., description="Month (1-12) or 0 for entire year"),
    function: str = Path(..., description="Statistical function to apply"),
    pollutant: str = Path(..., description="Pollutant type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get pollutant analytics based on ISTAT code, time period, and statistical function.
    
    Parameters:
    - istat_code: ISTAT geographical code
    - year: Target year
    - interval: Month (1-12) or 0 for entire year
    - function: Statistical function (media, massimo, minimo, etc.)
    - pollutant: Pollutant type (PM10, PM25, O3, NO2, SO2, C6H6, CO, As_in_PM10)
    
    Returns processed environmental analytics data.
    """
    
    # Validate inputs
    if pollutant not in SUPPORTED_POLLUTANTS:
        raise HTTPException(
            status_code=400,
            detail=f"Pollutant {pollutant} not supported. Available: {SUPPORTED_POLLUTANTS}"
        )
    
    if function not in SUPPORTED_FUNCTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Function {function} not supported. Available: {SUPPORTED_FUNCTIONS}"
        )
    
    if interval < 0 or interval > 12:
        raise HTTPException(
            status_code=400,
            detail="Interval must be 0 (entire year) or 1-12 (month)"
        )
    
    # Build query based on parameters
    query = db.query(EnvironmentalData).filter(
        EnvironmentalData.istat_code == istat_code,
        EnvironmentalData.measurement_year == year
    )
    
    # Add pollutant filter
    pollutant_column = _get_pollutant_column(pollutant)
    query = query.filter(getattr(EnvironmentalData, pollutant_column).isnot(None))
    
    # Add interval filter if specific month requested
    if interval > 0:
        query = query.filter(EnvironmentalData.measurement_month == interval)
    
    data = query.all()
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for ISTAT {istat_code}, year {year}, interval {interval}"
        )
    
    # Convert to DataFrame for calculations
    df = pd.DataFrame([
        {
            'date': record.measurement_date,
            'value': getattr(record, pollutant_column),
            'istat_code': record.istat_code,
            'station': record.station_code
        }
        for record in data
    ])
    
    # Apply statistical function
    result = _apply_statistical_function(df, function, pollutant)
    
    return {
        "istat_code": istat_code,
        "year": year,
        "interval": interval,
        "function": function,
        "pollutant": pollutant,
        "result": result,
        "unit": _get_pollutant_unit(pollutant),
        "data_points": len(data),
        "calculation_date": datetime.now().isoformat()
    }


@router.get("/climate/{istat_code}/{year}/{interval}/{measurement}/{function}/")
async def get_climate_analytics(
    istat_code: str = Path(..., description="ISTAT code"),
    year: int = Path(..., description="Year of interest"),
    interval: int = Path(..., description="Month (1-12) or 0 for entire year"),
    measurement: str = Path(..., description="Climate measurement type"),
    function: str = Path(..., description="Statistical function"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get climate analytics data.
    
    Parameters:
    - measurement: temperature, humidity, precipitation, wind_speed, etc.
    - function: somma_precipitazioni, giorni_con_precipitazioni, media, etc.
    """
    
    # Validate inputs
    if measurement not in SUPPORTED_CLIMATE_MEASUREMENTS:
        raise HTTPException(
            status_code=400,
            detail=f"Measurement {measurement} not supported. Available: {SUPPORTED_CLIMATE_MEASUREMENTS}"
        )
    
    if function not in SUPPORTED_FUNCTIONS + ["somma_precipitazioni", "giorni_con_precipitazioni"]:
        raise HTTPException(
            status_code=400,
            detail=f"Function {function} not supported for climate data"
        )
    
    # Query climate data
    query = db.query(ClimateData).filter(
        ClimateData.istat_code == istat_code,
        ClimateData.measurement_year == year
    )
    
    if interval > 0:
        query = query.filter(ClimateData.measurement_month == interval)
    
    data = query.all()
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No climate data found for ISTAT {istat_code}, year {year}"
        )
    
    # Convert to DataFrame for calculations
    df = pd.DataFrame([
        {
            'date': record.measurement_date,
            'temperature_avg': record.temperature_avg,
            'temperature_min': record.temperature_min,
            'temperature_max': record.temperature_max,
            'humidity': record.humidity,
            'precipitation': record.precipitation,
            'wind_speed': record.wind_speed,
            'wind_direction': record.wind_direction,
            'pressure': record.pressure,
            'solar_radiation': record.solar_radiation
        }
        for record in data
    ])
    
    # Apply climate-specific calculations
    result = _apply_climate_function(df, measurement, function)
    
    return {
        "istat_code": istat_code,
        "year": year,
        "interval": interval,
        "measurement": measurement,
        "function": function,
        "result": result,
        "unit": _get_climate_unit(measurement),
        "data_points": len(data),
        "calculation_date": datetime.now().isoformat()
    }


@router.get("/istat/{istat_code}/summary/")
async def get_istat_summary(
    istat_code: str = Path(..., description="ISTAT code"),
    year: Optional[int] = Query(None, description="Year (default: current year)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get comprehensive summary for an ISTAT area including all pollutants and climate data.
    """
    if year is None:
        year = datetime.now().year
    
    # Get all environmental data for the area
    env_data = db.query(EnvironmentalData).filter(
        EnvironmentalData.istat_code == istat_code,
        EnvironmentalData.measurement_year == year
    ).all()
    
    # Get all climate data for the area
    climate_data = db.query(ClimateData).filter(
        ClimateData.istat_code == istat_code,
        ClimateData.measurement_year == year
    ).all()
    
    summary = {
        "istat_code": istat_code,
        "year": year,
        "environmental_data": {
            "total_measurements": len(env_data),
            "available_pollutants": [],
            "date_range": None
        },
        "climate_data": {
            "total_measurements": len(climate_data),
            "date_range": None
        }
    }
    
    if env_data:
        # Analyze available pollutants
        df_env = pd.DataFrame([
            {
                'date': record.measurement_date,
                'pm10': record.pm10,
                'pm25': record.pm25,
                'ozone': record.ozone,
                'no2': record.no2,
                'so2': record.so2,
                'benzene': record.benzene,
                'co': record.co,
                'arsenic': record.arsenic
            }
            for record in env_data
        ])
        
        available_pollutants = []
        for pollutant in SUPPORTED_POLLUTANTS:
            col = _get_pollutant_column(pollutant)
            if col in df_env.columns and not df_env[col].isna().all():
                available_pollutants.append(pollutant)
        
        summary["environmental_data"]["available_pollutants"] = available_pollutants
        summary["environmental_data"]["date_range"] = {
            "start": df_env['date'].min().isoformat(),
            "end": df_env['date'].max().isoformat()
        }
    
    if climate_data:
        df_climate = pd.DataFrame([
            {'date': record.measurement_date}
            for record in climate_data
        ])
        summary["climate_data"]["date_range"] = {
            "start": df_climate['date'].min().isoformat(),
            "end": df_climate['date'].max().isoformat()
        }
    
    return summary


def _get_pollutant_column(pollutant: str) -> str:
    """Map pollutant names to database column names."""
    mapping = {
        "PM10": "pm10",
        "PM25": "pm25",
        "O3": "ozone",
        "NO2": "no2",
        "SO2": "so2",
        "C6H6": "benzene",
        "CO": "co",
        "As_in_PM10": "arsenic"
    }
    return mapping.get(pollutant, pollutant.lower())


def _get_pollutant_unit(pollutant: str) -> str:
    """Get unit of measurement for pollutant."""
    units = {
        "PM10": "µg/m³",
        "PM25": "µg/m³",
        "O3": "µg/m³",
        "NO2": "µg/m³",
        "SO2": "µg/m³",
        "C6H6": "µg/m³",
        "CO": "mg/m³",
        "As_in_PM10": "ng/m³"
    }
    return units.get(pollutant, "unknown")


def _get_climate_unit(measurement: str) -> str:
    """Get unit of measurement for climate data."""
    units = {
        "temperature": "°C",
        "humidity": "%",
        "precipitation": "mm",
        "wind_speed": "m/s",
        "wind_direction": "°N",
        "pressure": "hPa",
        "solar_radiation": "W/m²"
    }
    return units.get(measurement, "unknown")


def _apply_statistical_function(df: pd.DataFrame, function: str, pollutant: str) -> float:
    """Apply statistical function to pollutant data."""
    values = df['value'].dropna()
    
    if len(values) == 0:
        return None
    
    if function == "media":
        return float(values.mean())
    elif function == "massimo":
        return float(values.max())
    elif function == "minimo":
        return float(values.min())
    elif function == "mediana":
        return float(values.median())
    elif function == "varianza":
        return float(values.var())
    elif function == "somma":
        return float(values.sum())
    elif function == "giorni_superamento":
        # Days above legal limit (implement based on pollutant-specific limits)
        limit = _get_pollutant_limit(pollutant)
        if limit:
            return int((values > limit).sum())
        return None
    else:
        raise ValueError(f"Unsupported function: {function}")


def _apply_climate_function(df: pd.DataFrame, measurement: str, function: str) -> float:
    """Apply statistical function to climate data."""
    if measurement not in df.columns:
        return None
    
    values = df[measurement].dropna()
    
    if len(values) == 0:
        return None
    
    if function == "media":
        return float(values.mean())
    elif function == "massimo":
        return float(values.max())
    elif function == "minimo":
        return float(values.min())
    elif function == "somma" or function == "somma_precipitazioni":
        return float(values.sum())
    elif function == "giorni_con_precipitazioni":
        # Count days with precipitation > 0
        return int((values > 0).sum())
    else:
        return _apply_statistical_function(pd.DataFrame({'value': values}), function, measurement)


def _get_pollutant_limit(pollutant: str) -> Optional[float]:
    """Get legal limits for pollutants (EU/Italian standards)."""
    limits = {
        "PM10": 50.0,    # µg/m³ daily limit
        "PM25": 25.0,    # µg/m³ annual limit
        "O3": 120.0,     # µg/m³ 8-hour average
        "NO2": 200.0,    # µg/m³ hourly limit
        "SO2": 350.0,    # µg/m³ hourly limit
        "C6H6": 5.0,     # µg/m³ annual limit
        "CO": 10.0,      # mg/m³ 8-hour average
    }
    return limits.get(pollutant)
