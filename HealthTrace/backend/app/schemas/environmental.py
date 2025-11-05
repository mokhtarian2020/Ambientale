from typing import Optional
from pydantic import BaseModel
from datetime import datetime, date


class EnvironmentalDataBase(BaseModel):
    istat_code: str
    municipality: str
    province: str
    region: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    measurement_date: date
    measurement_year: int
    measurement_month: Optional[int] = None
    
    # Air Quality Data
    pm10: Optional[float] = None
    pm25: Optional[float] = None
    ozone: Optional[float] = None
    no2: Optional[float] = None
    so2: Optional[float] = None
    co: Optional[float] = None
    benzene: Optional[float] = None
    
    # Weather Data
    temperature_avg: Optional[float] = None
    temperature_max: Optional[float] = None
    temperature_min: Optional[float] = None
    humidity: Optional[float] = None
    precipitation: Optional[float] = None
    wind_speed: Optional[float] = None
    atmospheric_pressure: Optional[float] = None
    solar_radiation: Optional[float] = None
    
    # Anthropic Data
    has_mines: Optional[bool] = False
    has_industries: Optional[bool] = False
    area_type: Optional[str] = None
    
    # Data Source
    data_source: Optional[str] = None


class EnvironmentalDataCreate(EnvironmentalDataBase):
    pass


class EnvironmentalDataUpdate(BaseModel):
    pm10: Optional[float] = None
    pm25: Optional[float] = None
    ozone: Optional[float] = None
    no2: Optional[float] = None
    so2: Optional[float] = None
    co: Optional[float] = None
    benzene: Optional[float] = None
    temperature_avg: Optional[float] = None
    temperature_max: Optional[float] = None
    temperature_min: Optional[float] = None
    humidity: Optional[float] = None
    precipitation: Optional[float] = None
    wind_speed: Optional[float] = None
    atmospheric_pressure: Optional[float] = None
    solar_radiation: Optional[float] = None
    has_mines: Optional[bool] = None
    has_industries: Optional[bool] = None
    area_type: Optional[str] = None


class EnvironmentalDataResponse(EnvironmentalDataBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class EnvironmentalDataQuery(BaseModel):
    istat_code: Optional[str] = None
    municipality: Optional[str] = None
    province: Optional[str] = None
    region: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    year: Optional[int] = None
    month: Optional[int] = None


class BatchUploadResponse(BaseModel):
    batch_id: str
    filename: str
    total_records: int
    processed_records: int
    error_records: int
    status: str
