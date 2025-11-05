"""
Disease Models for the 3 Target Diseases in HealthTrace Project:
1. Influenza (Respiratory Disease)
2. Legionellosis (Water-Aerosol Respiratory Disease) 
3. Hepatitis A (Waterborne/Foodborne Disease)

Based on Italian environmental health specifications for Molise, Campania, and Calabria.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Date, ForeignKey, Float, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class DiseaseCategory(enum.Enum):
    RESPIRATORY = "respiratory"
    WATERBORNE = "waterborne"
    FOODBORNE = "foodborne"
    VECTOR_BORNE = "vector_borne"
    AIRBORNE = "airborne"


class TransmissionRoute(enum.Enum):
    AIRBORNE_DROPLETS = "airborne_droplets"
    WATER_AEROSOL = "water_aerosol"
    CONTAMINATED_WATER = "contaminated_water"
    CONTAMINATED_FOOD = "contaminated_food"
    DIRECT_CONTACT = "direct_contact"
    VECTOR = "vector"


class TargetDisease(Base):
    """
    Master table for the 3 target diseases with their environmental correlation profiles
    """
    __tablename__ = "target_diseases"
    
    id = Column(Integer, primary_key=True, index=True)
    disease_name = Column(String, unique=True, nullable=False)
    disease_code = Column(String, unique=True, nullable=False)  # ICD-10 code
    category = Column(Enum(DiseaseCategory), nullable=False)
    transmission_route = Column(Enum(TransmissionRoute), nullable=False)
    
    # Environmental Correlation Factors (correlation coefficients)
    pm25_correlation = Column(Float, nullable=True)  # PM2.5 correlation
    pm10_correlation = Column(Float, nullable=True)  # PM10 correlation
    ozone_correlation = Column(Float, nullable=True)  # O3 correlation
    no2_correlation = Column(Float, nullable=True)   # NO2 correlation
    so2_correlation = Column(Float, nullable=True)   # SO2 correlation
    
    # Climate Correlation Factors
    temperature_correlation = Column(Float, nullable=True)
    humidity_correlation = Column(Float, nullable=True)
    precipitation_correlation = Column(Float, nullable=True)
    wind_correlation = Column(Float, nullable=True)
    
    # Water Quality Correlations (for waterborne diseases)
    ph_correlation = Column(Float, nullable=True)
    ecoli_correlation = Column(Float, nullable=True)
    
    # Seasonality and Patterns
    seasonal_pattern = Column(JSON, nullable=True)  # Monthly incidence patterns
    lag_days = Column(Integer, nullable=True)  # Typical lag between exposure and symptoms
    
    # Modeling Parameters
    preferred_model = Column(String, nullable=True)  # GAM, ARIMAX, DLNM, etc.
    model_parameters = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InfluenzaCase(Base):
    """
    Influenza cases with environmental exposure tracking
    Focus: Respiratory disease correlated with PM2.5, PM10, NO2, temperature, humidity
    """
    __tablename__ = "influenza_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Patient and Geographic Information
    patient_id = Column(String, nullable=False, index=True)  # Anonymized patient ID
    istat_code = Column(String, nullable=False, index=True)
    
    # Case Details
    onset_date = Column(Date, nullable=False, index=True)
    notification_date = Column(Date, nullable=False)
    case_status = Column(String, nullable=False)  # Suspected, Probable, Confirmed
    
    # Clinical Information
    symptoms = Column(JSON, nullable=True)  # Fever, cough, dyspnea, etc.
    severity = Column(String, nullable=True)  # Mild, Moderate, Severe
    hospitalized = Column(Boolean, default=False)
    icu_admission = Column(Boolean, default=False)
    antiviral_therapy = Column(Boolean, default=False)
    
    # Laboratory Confirmation
    influenza_type = Column(String, nullable=True)  # A, B
    subtype = Column(String, nullable=True)  # H1N1, H3N2, etc.
    lab_confirmed = Column(Boolean, default=False)
    
    # Environmental Exposure (7-day average before onset)
    exposure_pm25 = Column(Float, nullable=True)  # µg/m³
    exposure_pm10 = Column(Float, nullable=True)  # µg/m³
    exposure_no2 = Column(Float, nullable=True)   # µg/m³
    exposure_ozone = Column(Float, nullable=True) # µg/m³
    exposure_temperature = Column(Float, nullable=True)  # °C
    exposure_humidity = Column(Float, nullable=True)     # %
    
    # Risk Factors
    age_group = Column(String, nullable=True)
    chronic_diseases = Column(JSON, nullable=True)
    vaccination_status = Column(String, nullable=True)
    
    # Outcome
    outcome = Column(String, nullable=True)  # Recovery, Death, Ongoing
    outcome_date = Column(Date, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LegionellosisCase(Base):
    """
    Legionellosis cases with water system and environmental exposure tracking
    Focus: Water-aerosol respiratory disease correlated with temperature, humidity, water quality
    """
    __tablename__ = "legionellosis_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Patient and Geographic Information
    patient_id = Column(String, nullable=False, index=True)
    istat_code = Column(String, nullable=False, index=True)
    
    # Case Details
    onset_date = Column(Date, nullable=False, index=True)
    notification_date = Column(Date, nullable=False)
    case_status = Column(String, nullable=False)
    
    # Clinical Presentation
    pneumonia = Column(Boolean, default=False)
    fever = Column(Boolean, default=False)
    cough = Column(Boolean, default=False)
    dyspnea = Column(Boolean, default=False)
    chest_pain = Column(Boolean, default=False)
    
    # Severity Assessment
    hospitalized = Column(Boolean, default=False)
    icu_admission = Column(Boolean, default=False)
    mechanical_ventilation = Column(Boolean, default=False)
    
    # Laboratory Confirmation
    legionella_species = Column(String, nullable=True)  # L. pneumophila, etc.
    serogroup = Column(String, nullable=True)
    detection_method = Column(String, nullable=True)  # Culture, PCR, Antigen, Serology
    
    # Environmental Exposure (14-day period before onset)
    exposure_temperature = Column(Float, nullable=True)  # Average temperature
    exposure_humidity = Column(Float, nullable=True)     # Average humidity
    exposure_precipitation = Column(Float, nullable=True) # Total precipitation
    
    # Water System Exposure
    hotel_stay = Column(Boolean, default=False)
    hospital_stay = Column(Boolean, default=False)
    spa_visit = Column(Boolean, default=False)
    cooling_tower_nearby = Column(Boolean, default=False)
    hot_tub_use = Column(Boolean, default=False)
    shower_exposure = Column(Boolean, default=False)
    
    # Water Quality Parameters (if available)
    water_temperature = Column(Float, nullable=True)
    water_ph = Column(Float, nullable=True)
    chlorine_level = Column(Float, nullable=True)
    
    # Geographic Clustering
    cluster_id = Column(String, nullable=True)  # If part of outbreak
    travel_related = Column(Boolean, default=False)
    travel_location = Column(String, nullable=True)
    
    # Outcome
    outcome = Column(String, nullable=True)
    outcome_date = Column(Date, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class HepatitisACase(Base):
    """
    Hepatitis A cases with water/food contamination tracking
    Focus: Waterborne/foodborne disease correlated with extreme precipitation, water quality
    """
    __tablename__ = "hepatitis_a_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Patient and Geographic Information
    patient_id = Column(String, nullable=False, index=True)
    istat_code = Column(String, nullable=False, index=True)
    
    # Case Details
    onset_date = Column(Date, nullable=False, index=True)
    notification_date = Column(Date, nullable=False)
    case_status = Column(String, nullable=False)
    
    # Clinical Presentation
    jaundice = Column(Boolean, default=False)
    fatigue = Column(Boolean, default=False)
    nausea = Column(Boolean, default=False)
    vomiting = Column(Boolean, default=False)
    abdominal_pain = Column(Boolean, default=False)
    dark_urine = Column(Boolean, default=False)
    pale_stools = Column(Boolean, default=False)
    
    # Laboratory Results
    alt_level = Column(Float, nullable=True)  # IU/L
    ast_level = Column(Float, nullable=True)  # IU/L
    bilirubin_level = Column(Float, nullable=True)  # mg/dL
    hav_igm_positive = Column(Boolean, default=False)
    hav_igg_positive = Column(Boolean, default=False)
    
    # Environmental Exposure (21-day period before onset - HAV incubation)
    extreme_precipitation_exposure = Column(Boolean, default=False)
    flooding_exposure = Column(Boolean, default=False)
    precipitation_7d_before = Column(Float, nullable=True)  # mm in 7 days before onset
    precipitation_14d_before = Column(Float, nullable=True) # mm in 14 days before onset
    precipitation_21d_before = Column(Float, nullable=True) # mm in 21 days before onset
    
    # Water and Food Exposure
    contaminated_water_exposure = Column(Boolean, default=False)
    well_water_consumption = Column(Boolean, default=False)
    untreated_water_consumption = Column(Boolean, default=False)
    shellfish_consumption = Column(Boolean, default=False)
    raw_vegetables_consumption = Column(Boolean, default=False)
    food_handler_contact = Column(Boolean, default=False)
    
    # Water Quality Parameters (if available)
    water_ph = Column(Float, nullable=True)
    water_ecoli_count = Column(Integer, nullable=True)  # CFU/100ml
    water_source_contamination = Column(Boolean, default=False)
    
    # Transmission Analysis
    person_to_person = Column(Boolean, default=False)
    household_contact = Column(Boolean, default=False)
    outbreak_associated = Column(Boolean, default=False)
    outbreak_id = Column(String, nullable=True)
    
    # Risk Factors
    vaccination_status = Column(String, nullable=True)  # None, Partial, Complete
    international_travel = Column(Boolean, default=False)
    travel_destination = Column(String, nullable=True)
    
    # Outcome
    hospitalized = Column(Boolean, default=False)
    outcome = Column(String, nullable=True)
    outcome_date = Column(Date, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DiseaseEnvironmentalCorrelation(Base):
    """
    Store calculated correlations between diseases and environmental factors
    """
    __tablename__ = "disease_environmental_correlations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Disease and Geographic Scope
    disease_name = Column(String, nullable=False, index=True)
    istat_code = Column(String, nullable=False, index=True)
    analysis_period_start = Column(Date, nullable=False)
    analysis_period_end = Column(Date, nullable=False)
    
    # Environmental Factor
    environmental_factor = Column(String, nullable=False)  # PM2.5, temperature, etc.
    
    # Correlation Analysis Results
    correlation_coefficient = Column(Float, nullable=False)
    p_value = Column(Float, nullable=False)
    confidence_interval_lower = Column(Float, nullable=True)
    confidence_interval_upper = Column(Float, nullable=True)
    
    # Model Information
    model_type = Column(String, nullable=False)  # GLM, GAM, DLNM, etc.
    lag_days = Column(Integer, nullable=True)
    model_parameters = Column(JSON, nullable=True)
    model_r_squared = Column(Float, nullable=True)
    
    # Sample Information
    total_cases = Column(Integer, nullable=False)
    data_points = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Correlation({self.disease_name}-{self.environmental_factor}: r={self.correlation_coefficient:.3f})>"
