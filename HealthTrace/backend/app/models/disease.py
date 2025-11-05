from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Date, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class DiseaseReport(Base):
    __tablename__ = "disease_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    reporting_doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Disease Information
    disease_name = Column(String, nullable=False, index=True)
    uosd_diagnosis = Column(String)
    
    # Clinical Data
    symptom_onset_date = Column(Date)
    symptom_onset_municipality = Column(String)
    hospitalization = Column(Boolean, default=False)
    vaccination_status = Column(String)  # From patient model enum
    vaccination_doses = Column(Integer)
    last_dose_date = Column(Date)
    vaccine_type = Column(String)
    
    # Reporting Information
    report_date = Column(Date, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="reports")
    reporting_doctor = relationship("User", back_populates="reports")
    investigations = relationship("EpidemiologicalInvestigation", back_populates="report")


class DiseaseCategory(Base):
    __tablename__ = "disease_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    icd_code = Column(String)  # International Classification of Diseases
    
    # Environmental correlation factors
    pm25_correlation = Column(Float)
    pm10_correlation = Column(Float)
    no2_correlation = Column(Float)
    ozone_correlation = Column(Float)
    temperature_correlation = Column(Float)
    humidity_correlation = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
