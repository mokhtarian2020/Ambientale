"""
Climate Data Model for HealthTrace Environmental Health System
Stores meteorological data from ARPA and ISPRA sources
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Date, Text, Index
from sqlalchemy.sql import func
from app.core.database import Base


class ClimateData(Base):
    __tablename__ = "climate_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Geographic Information
    istat_code = Column(String, nullable=False, index=True)  # ISTAT geographical code
    station_code = Column(String, nullable=True)  # Weather station identifier
    station_name = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Temporal Information
    measurement_date = Column(Date, nullable=False, index=True)
    measurement_year = Column(Integer, nullable=False, index=True)
    measurement_month = Column(Integer, nullable=False, index=True)
    measurement_day = Column(Integer, nullable=False)
    measurement_hour = Column(Integer, nullable=True)  # For hourly data
    
    # Temperature Data (°C)
    temperature_avg = Column(Float, nullable=True)
    temperature_min = Column(Float, nullable=True)
    temperature_max = Column(Float, nullable=True)
    temperature_soil = Column(Float, nullable=True)  # Ground temperature
    
    # Humidity Data (%)
    humidity = Column(Float, nullable=True)  # Relative humidity
    humidity_soil = Column(Float, nullable=True)  # Soil moisture (%VWC)
    leaf_wetness = Column(Float, nullable=True)  # Leaf wetness duration (min)
    
    # Precipitation Data (mm)
    precipitation = Column(Float, nullable=True)
    precipitation_max = Column(Float, nullable=True)  # Max hourly precipitation
    rainy_days = Column(Integer, nullable=True)  # Days with precipitation > 0
    
    # Wind Data
    wind_speed = Column(Float, nullable=True)  # m/s
    wind_speed_max = Column(Float, nullable=True)  # Max wind gust (m/s)
    wind_direction = Column(Float, nullable=True)  # Degrees North (°N)
    wind_direction_dominant = Column(Float, nullable=True)  # Dominant direction
    
    # Atmospheric Pressure (hPa)
    pressure = Column(Float, nullable=True)
    pressure_min = Column(Float, nullable=True)
    pressure_max = Column(Float, nullable=True)
    
    # Solar Radiation (W/m²)
    solar_radiation = Column(Float, nullable=True)
    uv_index = Column(Float, nullable=True)
    sunshine_hours = Column(Float, nullable=True)
    
    # Data Quality and Sources
    data_source = Column(String, nullable=True)  # ARPA, ISPRA, etc.
    data_quality = Column(String, nullable=True)  # Valid, Invalid, Estimated
    validation_status = Column(String, nullable=True)  # Raw, Validated, Processed
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    notes = Column(Text, nullable=True)
    
    # Create indexes for better query performance
    __table_args__ = (
        Index('idx_climate_istat_year_month', 'istat_code', 'measurement_year', 'measurement_month'),
        Index('idx_climate_date_station', 'measurement_date', 'station_code'),
        Index('idx_climate_geographic', 'latitude', 'longitude'),
    )

    def __repr__(self):
        return f"<ClimateData(istat={self.istat_code}, date={self.measurement_date}, temp={self.temperature_avg}°C)>"


class ExtremePrecipitationEvent(Base):
    """
    Track extreme precipitation events for correlation with waterborne diseases
    particularly important for Hepatitis A analysis
    """
    __tablename__ = "extreme_precipitation_events"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Geographic and Temporal
    istat_code = Column(String, nullable=False, index=True)
    event_date = Column(Date, nullable=False, index=True)
    event_start = Column(DateTime, nullable=True)
    event_end = Column(DateTime, nullable=True)
    duration_hours = Column(Float, nullable=True)
    
    # Precipitation Characteristics
    total_precipitation = Column(Float, nullable=False)  # mm
    max_hourly_intensity = Column(Float, nullable=True)  # mm/h
    average_intensity = Column(Float, nullable=True)  # mm/h
    
    # Event Classification
    event_type = Column(String, nullable=True)  # Heavy rain, Flood, Storm
    severity_level = Column(String, nullable=True)  # Low, Medium, High, Extreme
    return_period = Column(Integer, nullable=True)  # Years (statistical return period)
    
    # Impact Assessment
    flood_risk = Column(String, nullable=True)  # None, Low, Medium, High
    water_contamination_risk = Column(String, nullable=True)
    
    # Correlation with Health Events
    hepatitis_a_cases_7d = Column(Integer, nullable=True)  # Cases in next 7 days
    hepatitis_a_cases_14d = Column(Integer, nullable=True)  # Cases in next 14 days
    waterborne_disease_alert = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ExtremePrecipitationEvent(istat={self.istat_code}, date={self.event_date}, mm={self.total_precipitation})>"
