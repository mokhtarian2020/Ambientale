from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class PatientStatus(enum.Enum):
    ACTIVE = "active"  # Red light
    RECOVERED = "recovered"  # Green light
    DECEASED = "deceased"  # Black light


class VaccinationStatus(enum.Enum):
    VACCINATED = "vaccinated"
    UNVACCINATED = "unvaccinated"
    UNKNOWN = "unknown"


class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Personal Data
    tax_code = Column(String, unique=True, index=True)  # Codice Fiscale
    stp_code = Column(String)  # STP code for foreign nationals
    eni_code = Column(String)  # ENI code
    surname = Column(String, nullable=False)
    name = Column(String, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    birth_date = Column(Date, nullable=False)
    birth_country = Column(String)
    birth_province = Column(String)
    birth_municipality = Column(String, nullable=False)
    
    # Contact Information
    profession = Column(String)
    residence_address = Column(Text)
    residence_municipality = Column(String)
    residence_province = Column(String)
    residence_region = Column(String)
    domicile_address = Column(Text)
    domicile_municipality = Column(String)
    telephone = Column(String)
    
    # Status
    status = Column(Enum(PatientStatus), default=PatientStatus.ACTIVE)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    reports = relationship("DiseaseReport", back_populates="patient")
    investigations = relationship("EpidemiologicalInvestigation", back_populates="patient")
