from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, Date, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


class EnvironmentalData(Base):
    __tablename__ = "environmental_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Location Information
    istat_code = Column(String, nullable=False, index=True)  # Municipality/Province code
    municipality = Column(String, nullable=False)
    province = Column(String, nullable=False)
    region = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    
    # Temporal Information
    measurement_date = Column(Date, nullable=False, index=True)
    measurement_year = Column(Integer, nullable=False, index=True)
    measurement_month = Column(Integer, index=True)
    
    # Air Quality Data
    pm10 = Column(Float)  # μg/m³
    pm25 = Column(Float)  # μg/m³
    ozone = Column(Float)  # μg/m³
    no2 = Column(Float)  # μg/m³ - Nitrogen Dioxide
    so2 = Column(Float)  # μg/m³ - Sulphur Dioxide
    co = Column(Float)  # mg/m³ - Carbon Monoxide
    benzene = Column(Float)  # μg/m³
    
    # Weather Data
    temperature_avg = Column(Float)  # °C
    temperature_max = Column(Float)  # °C
    temperature_min = Column(Float)  # °C
    humidity = Column(Float)  # %
    precipitation = Column(Float)  # mm
    wind_speed = Column(Float)  # km/h
    atmospheric_pressure = Column(Float)  # hPa
    solar_radiation = Column(Float)  # W/m²
    
    # Anthropic Data
    has_mines = Column(Boolean, default=False)
    has_industries = Column(Boolean, default=False)
    area_type = Column(String)  # Urban, Marshy, Grazing, Agricultural
    
    # Data Source
    data_source = Column(String)  # ISPRA, ARPA, ISTAT, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EnvironmentalDataBatch(Base):
    __tablename__ = "environmental_data_batches"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    filename = Column(String, nullable=False)
    file_size = Column(Integer)
    records_count = Column(Integer)
    processed_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    status = Column(String, default="processing")  # processing, completed, failed
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    uploader = relationship("User")
