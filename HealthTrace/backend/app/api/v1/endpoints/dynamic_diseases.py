"""
Dynamic Disease API Endpoints
Automatically generates API endpoints for any registered disease in the system.
Supports the extensible disease framework.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from datetime import date, datetime
import pandas as pd

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User, UserRole
from app.models.extensible_diseases import (
    disease_registry, 
    analytics_engine, 
    expansion_manager,
    DiseaseProfile,
    ExtensibleDiseaseCategory,
    ExtensibleTransmissionRoute
)

router = APIRouter()


@router.get("/diseases/")
async def list_diseases(
    category: Optional[str] = Query(None, description="Filter by disease category"),
    environmental_factor: Optional[str] = Query(None, description="Filter by environmental factor"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    List all diseases supported by the platform
    """
    
    if category:
        diseases = disease_registry.get_diseases_by_category(category)
    elif environmental_factor:
        diseases = disease_registry.get_diseases_by_environmental_factor(environmental_factor)
    else:
        diseases = disease_registry.list_diseases()
    
    disease_info = []
    for disease_name in diseases:
        profile = disease_registry.get_disease_profile(disease_name)
        disease_info.append({
            "name": disease_name,
            "display_name": profile.name,
            "code": profile.code,
            "category": profile.category,
            "transmission_route": profile.transmission_route,
            "environmental_factors": profile.environmental_factors,
            "preferred_models": profile.preferred_models,
            "incubation_period_days": profile.incubation_period_days,
            "lag_period_days": profile.lag_period_days
        })
    
    return {
        "total_diseases": len(disease_info),
        "diseases": disease_info,
        "categories_available": list(set(d["category"] for d in disease_info)),
        "environmental_factors_covered": list(set(
            factor for d in disease_info for factor in d["environmental_factors"]
        ))
    }


@router.get("/diseases/categories/")
async def list_disease_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    List all disease categories and their counts
    """
    
    categories = {}
    for disease_name in disease_registry.list_diseases():
        profile = disease_registry.get_disease_profile(disease_name)
        category = profile.category
        
        if category not in categories:
            categories[category] = {
                "count": 0,
                "diseases": [],
                "common_factors": set()
            }
        
        categories[category]["count"] += 1
        categories[category]["diseases"].append({
            "name": disease_name,
            "display_name": profile.name,
            "factors": profile.environmental_factors
        })
        categories[category]["common_factors"].update(profile.environmental_factors)
    
    # Convert sets to lists for JSON serialization
    for category in categories:
        categories[category]["common_factors"] = list(categories[category]["common_factors"])
    
    return {
        "categories": categories,
        "total_categories": len(categories)
    }


@router.get("/diseases/{disease_name}/profile/")
async def get_disease_profile(
    disease_name: str = Path(..., description="Disease name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get detailed profile for a specific disease
    """
    
    profile = disease_registry.get_disease_profile(disease_name)
    if not profile:
        raise HTTPException(404, f"Disease '{disease_name}' not found")
    
    return {
        "name": disease_name,
        "profile": {
            "display_name": profile.name,
            "code": profile.code,
            "category": profile.category,
            "transmission_route": profile.transmission_route,
            "incubation_period_days": profile.incubation_period_days,
            "environmental_factors": profile.environmental_factors,
            "preferred_models": profile.preferred_models,
            "lag_period_days": profile.lag_period_days,
            "seasonal_pattern": profile.seasonal_pattern,
            "geographic_risk_factors": profile.geographic_risk_factors
        }
    }


@router.post("/diseases/{disease_name}/analyze/")
async def analyze_disease_environment_correlation(
    disease_name: str = Path(..., description="Disease name"),
    istat_code: Optional[str] = Query(None, description="ISTAT code for geographic filtering"),
    start_date: Optional[date] = Query(None, description="Analysis start date"),
    end_date: Optional[date] = Query(None, description="Analysis end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Run environmental correlation analysis for any registered disease
    """
    
    profile = disease_registry.get_disease_profile(disease_name)
    if not profile:
        raise HTTPException(404, f"Disease '{disease_name}' not found")
    
    # For demonstration, create synthetic data
    # In real implementation, fetch from database based on parameters
    sample_data = _generate_sample_data(profile, istat_code, start_date, end_date)
    
    try:
        # Run analysis using extensible analytics engine
        results = analytics_engine.run_analysis_for_disease(disease_name, sample_data)
        
        # Extract key insights
        best_model = None
        if results['results']:
            best_model_name = max(results['results'].keys(), 
                                key=lambda k: results['results'][k].r_squared)
            best_model = {
                "name": best_model_name,
                "r_squared": results['results'][best_model_name].r_squared,
                "mae": results['results'][best_model_name].mae,
                "rmse": results['results'][best_model_name].rmse
            }
        
        return {
            "disease": disease_name,
            "analysis_summary": {
                "total_models_run": results['total_models_run'],
                "preferred_models_run": results['preferred_models_run'],
                "environmental_factors_analyzed": results['available_factors'],
                "best_performing_model": best_model
            },
            "disease_profile": {
                "category": profile.category,
                "lag_period_days": profile.lag_period_days,
                "preferred_models": profile.preferred_models
            },
            "data_summary": {
                "records_analyzed": len(sample_data),
                "date_range": {
                    "start": sample_data['date'].min().isoformat() if 'date' in sample_data.columns else None,
                    "end": sample_data['date'].max().isoformat() if 'date' in sample_data.columns else None
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(500, f"Analysis failed for {disease_name}: {str(e)}")


@router.post("/diseases/compare/")
async def compare_multiple_diseases(
    disease_names: List[str] = Query(..., description="List of disease names to compare"),
    environmental_factor: Optional[str] = Query(None, description="Focus on specific environmental factor"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Compare environmental correlations across multiple diseases
    """
    
    # Validate all diseases exist
    for disease_name in disease_names:
        if not disease_registry.get_disease_profile(disease_name):
            raise HTTPException(404, f"Disease '{disease_name}' not found")
    
    # Generate sample data for comparison
    comparison_data = _generate_comparison_data(disease_names)
    
    try:
        # Run comparative analysis
        comparison_results = analytics_engine.compare_diseases(disease_names, comparison_data)
        
        return {
            "diseases_compared": disease_names,
            "comparison_results": comparison_results.to_dict('records'),
            "summary": {
                "best_performing_disease": comparison_results.loc[comparison_results['R_Squared'].idxmax(), 'Disease'] if not comparison_results.empty else None,
                "common_factors": _find_common_factors(disease_names),
                "category_distribution": _get_category_distribution(disease_names)
            }
        }
        
    except Exception as e:
        raise HTTPException(500, f"Comparison analysis failed: {str(e)}")


@router.post("/diseases/expand/")
async def expand_disease_database(
    categories: List[str] = Query(..., description="Disease categories to add"),
    admin_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Add new disease categories to the platform (Admin only)
    """
    
    # Check if user is admin
    if admin_user.role != UserRole.ADMIN:
        raise HTTPException(403, "Only administrators can expand the disease database")
    
    initial_count = len(disease_registry.list_diseases())
    added_diseases = []
    
    try:
        for category in categories:
            if category == "vector_borne":
                expansion_manager.add_vector_borne_diseases()
                added_diseases.extend(["malaria", "dengue", "chikungunya", "zika", "west_nile", "tbe"])
            elif category == "respiratory":
                expansion_manager.add_respiratory_diseases()
                added_diseases.extend(["covid19", "tuberculosis", "measles", "rubella"])
            elif category == "foodborne":
                expansion_manager.add_foodborne_diseases()
                added_diseases.extend(["botulism", "listeriosis"])
            elif category == "neurological":
                expansion_manager.add_neurological_diseases()
                added_diseases.extend(["tetanus", "encephalitis", "meningitis"])
            else:
                raise ValueError(f"Unknown category: {category}")
        
        final_count = len(disease_registry.list_diseases())
        
        return {
            "success": True,
            "message": f"Successfully expanded disease database",
            "details": {
                "initial_disease_count": initial_count,
                "final_disease_count": final_count,
                "diseases_added": len(added_diseases),
                "new_diseases": added_diseases,
                "categories_added": categories
            }
        }
        
    except Exception as e:
        raise HTTPException(500, f"Failed to expand disease database: {str(e)}")


@router.get("/diseases/{disease_name}/environmental-factors/")
async def get_disease_environmental_factors(
    disease_name: str = Path(..., description="Disease name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get environmental factors relevant to a specific disease
    """
    
    profile = disease_registry.get_disease_profile(disease_name)
    if not profile:
        raise HTTPException(404, f"Disease '{disease_name}' not found")
    
    factors_info = []
    for factor in profile.environmental_factors:
        factor_info = {
            "name": factor,
            "unit": _get_factor_unit(factor),
            "measurement_type": _get_factor_measurement_type(factor),
            "data_sources": _get_factor_data_sources(factor)
        }
        factors_info.append(factor_info)
    
    return {
        "disease": disease_name,
        "environmental_factors": factors_info,
        "lag_period_days": profile.lag_period_days,
        "preferred_models": profile.preferred_models,
        "analysis_recommendations": _get_analysis_recommendations(profile)
    }


# Helper functions

def _generate_sample_data(profile: DiseaseProfile, istat_code: Optional[str], 
                         start_date: Optional[date], end_date: Optional[date]) -> pd.DataFrame:
    """Generate sample data for analysis demonstration"""
    
    import numpy as np
    from datetime import timedelta
    
    # Generate date range
    if not start_date:
        start_date = date(2023, 1, 1)
    if not end_date:
        end_date = date(2023, 12, 31)
    
    dates = pd.date_range(start_date, end_date, freq='D')
    n_samples = len(dates)
    
    # Create sample data
    data = {'date': dates}
    
    # Add environmental factors
    for factor in profile.environmental_factors:
        if factor == "pm25":
            data[factor] = np.random.normal(15, 5, n_samples)
        elif factor == "pm10":
            data[factor] = np.random.normal(25, 8, n_samples)
        elif factor == "temperature":
            data[factor] = np.random.normal(18, 8, n_samples)
        elif factor == "humidity":
            data[factor] = np.random.normal(70, 15, n_samples)
        elif factor == "precipitation":
            data[factor] = np.random.exponential(2, n_samples)
        else:
            data[factor] = np.random.normal(10, 3, n_samples)
    
    # Add case count (synthetic)
    data['case_count'] = np.random.poisson(5, n_samples)
    
    return pd.DataFrame(data)


def _generate_comparison_data(disease_names: List[str]) -> pd.DataFrame:
    """Generate sample data for disease comparison"""
    
    # Use the first disease profile as template
    profile = disease_registry.get_disease_profile(disease_names[0])
    return _generate_sample_data(profile, None, None, None)


def _find_common_factors(disease_names: List[str]) -> List[str]:
    """Find environmental factors common to all diseases"""
    
    if not disease_names:
        return []
    
    # Get factors for first disease
    common_factors = set(disease_registry.get_disease_profile(disease_names[0]).environmental_factors)
    
    # Intersect with factors from other diseases
    for disease_name in disease_names[1:]:
        profile = disease_registry.get_disease_profile(disease_name)
        common_factors &= set(profile.environmental_factors)
    
    return list(common_factors)


def _get_category_distribution(disease_names: List[str]) -> Dict[str, int]:
    """Get distribution of diseases by category"""
    
    categories = {}
    for disease_name in disease_names:
        profile = disease_registry.get_disease_profile(disease_name)
        category = profile.category
        categories[category] = categories.get(category, 0) + 1
    
    return categories


def _get_factor_unit(factor: str) -> str:
    """Get unit of measurement for environmental factor"""
    units = {
        "pm25": "µg/m³",
        "pm10": "µg/m³",
        "ozone": "µg/m³",
        "no2": "µg/m³",
        "so2": "µg/m³",
        "temperature": "°C",
        "humidity": "%",
        "precipitation": "mm",
        "wind_speed": "m/s",
        "water_ph": "pH units",
        "ecoli_count": "CFU/100ml"
    }
    return units.get(factor, "unknown")


def _get_factor_measurement_type(factor: str) -> str:
    """Get measurement type for environmental factor"""
    types = {
        "pm25": "continuous",
        "pm10": "continuous",
        "temperature": "continuous",
        "precipitation": "continuous",
        "water_ph": "discrete",
        "ecoli_count": "discrete"
    }
    return types.get(factor, "continuous")


def _get_factor_data_sources(factor: str) -> List[str]:
    """Get data sources for environmental factor"""
    sources = {
        "pm25": ["ARPA Campania", "ISPRA"],
        "pm10": ["ARPA Campania", "ISPRA"],
        "temperature": ["ISTAT", "ARPA"],
        "precipitation": ["ISTAT", "Regional Weather Stations"],
        "water_ph": ["ARPA Campania", "Local Health Authorities"],
        "ecoli_count": ["ARPA Campania", "Water Quality Labs"]
    }
    return sources.get(factor, ["Various"])


def _get_analysis_recommendations(profile: DiseaseProfile) -> Dict[str, str]:
    """Get analysis recommendations based on disease profile"""
    
    recommendations = {
        "primary_model": profile.preferred_models[0] if profile.preferred_models else "GAM",
        "lag_analysis": f"Use {profile.lag_period_days}-day lag for environmental exposure",
        "seasonal_adjustment": "Consider seasonal patterns" if profile.seasonal_pattern else "No seasonal adjustment needed"
    }
    
    if profile.category == "vector_borne":
        recommendations["special_considerations"] = "Include vector habitat and breeding site data"
    elif profile.category == "waterborne":
        recommendations["special_considerations"] = "Focus on extreme precipitation events and water quality"
    elif profile.category == "respiratory":
        recommendations["special_considerations"] = "Emphasize air quality and meteorological factors"
    
    return recommendations
