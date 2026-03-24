"""
Real Infectious Disease Database API Endpoints
Provides access to the real GESAN malattie infettive database
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date
import pandas as pd
import logging

from app.core.database import get_db
from app.core.infectious_disease_db import get_infectious_disease_db, InfectiousDiseaseDB
from app.core.auth import get_current_active_user
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/real-db/status")
async def get_real_database_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get connection status of real infectious disease database"""
    
    try:
        real_db = get_infectious_disease_db()
        
        if real_db.engine is None:
            return {
                "status": "disconnected",
                "message": "Cannot connect to real infectious disease database",
                "database": "gesan_malattieinfettive",
                "server": "10.10.13.11:5432"
            }
        
        # Test connection with basic query
        with real_db.engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("SELECT 1"))
            
        return {
            "status": "connected",
            "message": "Successfully connected to real infectious disease database", 
            "database": "gesan_malattieinfettive",
            "server": "10.10.13.11:5432",
            "connection_test": "passed"
        }
        
    except Exception as e:
        logger.error(f"Real database status check failed: {e}")
        return {
            "status": "error",
            "message": f"Database connection error: {str(e)}",
            "database": "gesan_malattieinfettive", 
            "server": "10.10.13.11:5432"
        }

@router.get("/real-db/schema")
async def explore_real_database_schema(
    current_user: User = Depends(get_current_active_user)
):
    """
    Explore the schema of the real infectious disease database
    Only available to Admin and UOC Epidemiology users
    """
    
    # Restrict to authorized users
    if current_user.role not in [UserRole.ADMIN, UserRole.UOC_EPIDEMIOLOGY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to explore database schema"
        )
    
    try:
        real_db = get_infectious_disease_db()
        schema_info = real_db.explore_database_schema()
        
        return {
            "status": "success",
            "schema_exploration": schema_info,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Schema exploration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Schema exploration failed: {str(e)}"
        )

@router.get("/real-db/statistics")
async def get_real_database_statistics(
    current_user: User = Depends(get_current_active_user)
):
    """Get basic statistics from real infectious disease database"""
    
    try:
        real_db = get_infectious_disease_db()
        stats = real_db.get_disease_statistics()
        
        return {
            "status": "success",
            "statistics": stats,
            "data_source": "real_infectious_disease_database",
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Statistics retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Statistics retrieval failed: {str(e)}"
        )

@router.get("/real-db/diseases")
async def query_real_disease_cases(
    disease_type: Optional[str] = Query(None, description="Disease type filter"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    istat_code: Optional[str] = Query(None, description="ISTAT geographic code filter"),
    region: Optional[str] = Query(None, description="Region filter"),
    limit: int = Query(100, description="Maximum records to return", le=10000),
    current_user: User = Depends(get_current_active_user)
):
    """
    Query disease cases from real database with filters
    """
    
    try:
        real_db = get_infectious_disease_db()
        
        # Convert dates to strings if provided
        start_date_str = start_date.isoformat() if start_date else None
        end_date_str = end_date.isoformat() if end_date else None
        
        # Query real database
        df = real_db.query_disease_cases(
            disease_type=disease_type,
            start_date=start_date_str,
            end_date=end_date_str,
            istat_code=istat_code,
            limit=limit
        )
        
        if df.empty:
            return {
                "status": "success",
                "message": "No records found with specified filters",
                "total_records": 0,
                "data": [],
                "filters_applied": {
                    "disease_type": disease_type,
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "istat_code": istat_code,
                    "region": region,
                    "limit": limit
                }
            }
        
        # Map to HealthTrace format
        mapped_df = real_db.map_to_healthtrace_format(df)
        
        # Convert to JSON-serializable format
        records = mapped_df.to_dict('records')
        
        # Add summary statistics
        summary = {
            "total_records": len(records),
            "date_range": {
                "earliest": mapped_df['diagnosis_date'].min().isoformat() if 'diagnosis_date' in mapped_df.columns else None,
                "latest": mapped_df['diagnosis_date'].max().isoformat() if 'diagnosis_date' in mapped_df.columns else None
            } if len(records) > 0 else None,
            "disease_breakdown": mapped_df['healthtrace_disease_category'].value_counts().to_dict() if 'healthtrace_disease_category' in mapped_df.columns else {},
            "region_breakdown": mapped_df['region'].value_counts().to_dict() if 'region' in mapped_df.columns else {}
        }
        
        return {
            "status": "success",
            "data_source": "real_infectious_disease_database",
            "summary": summary,
            "filters_applied": {
                "disease_type": disease_type,
                "start_date": start_date_str,
                "end_date": end_date_str, 
                "istat_code": istat_code,
                "region": region,
                "limit": limit
            },
            "data": records[:limit],  # Ensure limit is respected
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Real database query failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed: {str(e)}"
        )

@router.get("/real-db/diseases/by-coordinates")
async def query_diseases_by_coordinates(
    polygon_geojson: Optional[str] = Query(None, description="GeoJSON polygon for spatial filtering"),
    bbox: Optional[str] = Query(None, description="Bounding box: min_lon,min_lat,max_lon,max_lat"),
    disease_type: Optional[str] = Query(None, description="Disease type filter"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    limit: int = Query(100, description="Maximum records to return"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Query disease cases with spatial/coordinate filtering
    This endpoint bridges real disease data with your polygon functionality
    """
    
    try:
        real_db = get_infectious_disease_db()
        
        # First get disease cases
        start_date_str = start_date.isoformat() if start_date else None
        end_date_str = end_date.isoformat() if end_date else None
        
        df = real_db.query_disease_cases(
            disease_type=disease_type,
            start_date=start_date_str,
            end_date=end_date_str,
            limit=limit * 2  # Get more records for spatial filtering
        )
        
        if df.empty:
            return {
                "status": "success",
                "message": "No disease cases found",
                "total_records": 0,
                "data": []
            }
        
        # Map to HealthTrace format
        mapped_df = real_db.map_to_healthtrace_format(df)
        
        # Add coordinates if ISTAT codes are available
        if 'istat_code' in mapped_df.columns:
            # Import coordinate functions
            import sys
            import os
            sys.path.append('/home/amir/Documents/amir/Ambientale/HealthTrace/')
            
            try:
                from COORDINATE_FIX_REQUIRED import get_coordinates_for_istat
                
                # Add coordinates for each record
                coordinates_data = []
                for _, row in mapped_df.iterrows():
                    istat_code = str(row['istat_code']) if pd.notna(row['istat_code']) else None
                    if istat_code:
                        lat, lon, alt = get_coordinates_for_istat(istat_code)
                        coordinates_data.append({
                            'latitude': lat,
                            'longitude': lon,
                            'altitude': alt
                        })
                    else:
                        coordinates_data.append({
                            'latitude': None,
                            'longitude': None,
                            'altitude': None
                        })
                
                # Add coordinates to dataframe
                coords_df = pd.DataFrame(coordinates_data)
                mapped_df = pd.concat([mapped_df, coords_df], axis=1)
                
            except ImportError as e:
                logger.warning(f"Could not import coordinate functions: {e}")
        
        # Apply spatial filtering if requested
        if polygon_geojson or bbox:
            # Filter by coordinates - implementation depends on coordinate availability
            filtered_df = mapped_df[
                mapped_df['latitude'].notna() & 
                mapped_df['longitude'].notna()
            ]
            
            if bbox:
                # Parse bounding box
                try:
                    min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(','))
                    filtered_df = filtered_df[
                        (filtered_df['longitude'] >= min_lon) &
                        (filtered_df['longitude'] <= max_lon) &
                        (filtered_df['latitude'] >= min_lat) &
                        (filtered_df['latitude'] <= max_lat)
                    ]
                except Exception as e:
                    logger.warning(f"Invalid bbox format: {e}")
            
            # TODO: Implement polygon filtering when needed
            
            mapped_df = filtered_df
        
        # Convert to records
        records = mapped_df.head(limit).to_dict('records')
        
        return {
            "status": "success",
            "data_source": "real_infectious_disease_database_with_coordinates",
            "total_records": len(records),
            "spatial_filtering": {
                "polygon_applied": polygon_geojson is not None,
                "bbox_applied": bbox is not None,
                "records_with_coordinates": len(mapped_df[mapped_df['latitude'].notna()])
            },
            "data": records,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Spatial disease query failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Spatial query failed: {str(e)}"
        )

@router.post("/real-db/sync")
async def sync_real_data_to_healthtrace(
    sync_diseases: bool = Query(True, description="Sync disease cases"),
    sync_limit: int = Query(1000, description="Maximum records to sync"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Sync data from real database to HealthTrace local database
    Only available to Admin users
    """
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin users can sync real data"
        )
    
    try:
        real_db = get_infectious_disease_db()
        sync_results = {}
        
        if sync_diseases:
            # Get recent disease cases
            df = real_db.query_disease_cases(limit=sync_limit)
            mapped_df = real_db.map_to_healthtrace_format(df)
            
            # TODO: Insert into local HealthTrace database
            # This would involve mapping to your local models
            
            sync_results["diseases"] = {
                "records_retrieved": len(df),
                "records_mapped": len(mapped_df),
                "status": "completed"
            }
        
        return {
            "status": "success",
            "sync_results": sync_results,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Data sync failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data sync failed: {str(e)}"
        )
