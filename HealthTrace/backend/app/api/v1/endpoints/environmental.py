from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from datetime import date, datetime
import pandas as pd
import io

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User, UserRole
from app.models.environmental import EnvironmentalData, EnvironmentalDataBatch
from app.schemas.environmental import (
    EnvironmentalDataCreate,
    EnvironmentalDataResponse,
    EnvironmentalDataQuery,
    BatchUploadResponse
)

router = APIRouter()


@router.get("/data", response_model=List[EnvironmentalDataResponse])
def get_environmental_data(
    istat_code: Optional[str] = Query(None, description="ISTAT municipality/province code"),
    municipality: Optional[str] = Query(None, description="Municipality name"),
    province: Optional[str] = Query(None, description="Province name"),
    region: Optional[str] = Query(None, description="Region name"),
    start_date: Optional[date] = Query(None, description="Start date for data range"),
    end_date: Optional[date] = Query(None, description="End date for data range"),
    year: Optional[int] = Query(None, description="Specific year"),
    month: Optional[int] = Query(None, description="Specific month (1-12)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get environmental data with filters"""
    query = db.query(EnvironmentalData)
    
    if istat_code:
        query = query.filter(EnvironmentalData.istat_code == istat_code)
    if municipality:
        query = query.filter(EnvironmentalData.municipality.ilike(f"%{municipality}%"))
    if province:
        query = query.filter(EnvironmentalData.province.ilike(f"%{province}%"))
    if region:
        query = query.filter(EnvironmentalData.region.ilike(f"%{region}%"))
    if start_date:
        query = query.filter(EnvironmentalData.measurement_date >= start_date)
    if end_date:
        query = query.filter(EnvironmentalData.measurement_date <= end_date)
    if year:
        query = query.filter(EnvironmentalData.measurement_year == year)
    if month:
        query = query.filter(EnvironmentalData.measurement_month == month)
    
    # Order by date descending
    query = query.order_by(EnvironmentalData.measurement_date.desc())
    
    data = query.offset(skip).limit(limit).all()
    return data


@router.get("/istat/{istat_code}/{year}/{interval}/{function}/{pollutant}")
def get_pollutant_data(
    istat_code: str,
    year: int,
    interval: int,  # 0 = full year, 1-12 = specific month
    function: str,  # 'average', 'maximum'
    pollutant: str,  # 'pm10', 'pm25', 'no2', 'ozone', etc.
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """API endpoint as specified in requirements: /istat/year/interval/function/pollutant/"""
    query = db.query(EnvironmentalData).filter(
        EnvironmentalData.istat_code == istat_code,
        EnvironmentalData.measurement_year == year
    )
    
    if interval != 0:  # Specific month
        query = query.filter(EnvironmentalData.measurement_month == interval)
    
    data = query.all()
    
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No data found for the specified parameters"
        )
    
    # Extract pollutant values
    pollutant_values = []
    for record in data:
        value = getattr(record, pollutant, None)
        if value is not None:
            pollutant_values.append(value)
    
    if not pollutant_values:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {pollutant} data found"
        )
    
    # Calculate function
    if function == "average":
        result = sum(pollutant_values) / len(pollutant_values)
    elif function == "maximum":
        result = max(pollutant_values)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Function must be 'average' or 'maximum'"
        )
    
    return {
        "istat_code": istat_code,
        "year": year,
        "interval": interval,
        "function": function,
        "pollutant": pollutant,
        "value": result,
        "unit": "μg/m³" if pollutant not in ["co"] else "mg/m³",
        "records_count": len(pollutant_values)
    }


@router.get("/climate/{istat_code}/{year}/{interval}/{measurement}/{function}")
def get_climate_data(
    istat_code: str,
    year: int,
    interval: int,  # 0 = full year, 1-12 = specific month
    measurement: str,  # 'precipitation', 'temperature', etc.
    function: str,  # 'sum', 'average', 'days_with_precipitation'
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """API endpoint for climate data: /climate/istat/year/interval/measurement/function/"""
    query = db.query(EnvironmentalData).filter(
        EnvironmentalData.istat_code == istat_code,
        EnvironmentalData.measurement_year == year
    )
    
    if interval != 0:  # Specific month
        query = query.filter(EnvironmentalData.measurement_month == interval)
    
    data = query.all()
    
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No data found for the specified parameters"
        )
    
    # Extract measurement values
    measurement_values = []
    for record in data:
        if measurement == "precipitation":
            value = record.precipitation
        elif measurement == "temperature":
            value = record.temperature_avg
        elif measurement == "humidity":
            value = record.humidity
        elif measurement == "wind":
            value = record.wind_speed
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Measurement '{measurement}' not supported"
            )
        
        if value is not None:
            measurement_values.append(value)
    
    if not measurement_values:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {measurement} data found"
        )
    
    # Calculate function
    if function == "sum":
        result = sum(measurement_values)
    elif function == "average":
        result = sum(measurement_values) / len(measurement_values)
    elif function == "days_with_precipitation" and measurement == "precipitation":
        result = len([v for v in measurement_values if v > 0])
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Function '{function}' not supported for measurement '{measurement}'"
        )
    
    return {
        "istat_code": istat_code,
        "year": year,
        "interval": interval,
        "measurement": measurement,
        "function": function,
        "value": result,
        "records_count": len(measurement_values)
    }


@router.post("/upload", response_model=BatchUploadResponse)
async def upload_environmental_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload environmental data via Excel file"""
    if current_user.role not in [UserRole.ADMIN, UserRole.UOC_EPIDEMIOLOGY]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to upload data"
        )
    
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be Excel (.xlsx, .xls) or CSV format"
        )
    
    try:
        contents = await file.read()
        
        # Create batch record
        batch = EnvironmentalDataBatch(
            filename=file.filename,
            file_size=len(contents),
            uploaded_by=current_user.id,
            status="processing"
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)
        
        # Process file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        batch.records_count = len(df)
        processed_count = 0
        error_count = 0
        
        # Process each row
        for _, row in df.iterrows():
            try:
                env_data = EnvironmentalData(
                    istat_code=row.get('istat_code'),
                    municipality=row.get('municipality'),
                    province=row.get('province'),
                    region=row.get('region'),
                    latitude=row.get('latitude'),
                    longitude=row.get('longitude'),
                    measurement_date=pd.to_datetime(row.get('measurement_date')).date(),
                    measurement_year=pd.to_datetime(row.get('measurement_date')).year,
                    measurement_month=pd.to_datetime(row.get('measurement_date')).month,
                    pm10=row.get('pm10'),
                    pm25=row.get('pm25'),
                    ozone=row.get('ozone'),
                    no2=row.get('no2'),
                    so2=row.get('so2'),
                    temperature_avg=row.get('temperature_avg'),
                    humidity=row.get('humidity'),
                    precipitation=row.get('precipitation'),
                    data_source=row.get('data_source', 'Manual Upload')
                )
                db.add(env_data)
                processed_count += 1
            except Exception as e:
                error_count += 1
                continue
        
        batch.processed_count = processed_count
        batch.error_count = error_count
        batch.status = "completed" if error_count == 0 else "completed_with_errors"
        batch.completed_at = datetime.utcnow()
        
        db.commit()
        
        return BatchUploadResponse(
            batch_id=str(batch.batch_id),
            filename=batch.filename,
            total_records=batch.records_count,
            processed_records=processed_count,
            error_records=error_count,
            status=batch.status
        )
        
    except Exception as e:
        batch.status = "failed"
        batch.error_count = batch.records_count or 0
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}"
        )
