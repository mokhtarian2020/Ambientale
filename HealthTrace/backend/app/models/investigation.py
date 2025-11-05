from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Date, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class CaseType(enum.Enum):
    PROBABLE = "probable"
    CONFIRMED = "confirmed"


class EpidemiologicalInvestigation(Base):
    __tablename__ = "epidemiological_investigations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    report_id = Column(Integer, ForeignKey("disease_reports.id"), nullable=False)
    investigator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Investigation Details
    case_type = Column(String)  # Probable/Confirmed
    symptomatology = Column(Text)
    contagion_source = Column(Text)
    foreign_travel = Column(Boolean, default=False)
    travel_countries = Column(Text)
    travel_dates = Column(Text)
    
    # Diagnostic Information
    diagnostic_tests = Column(JSON)  # Array of tests with type, date, place, result
    
    # Investigation Date
    investigation_date = Column(Date, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="investigations")
    report = relationship("DiseaseReport", back_populates="investigations")
    investigator = relationship("User", back_populates="investigations")
    contacts = relationship("ContactTracing", back_populates="investigation")


class ContactTracing(Base):
    __tablename__ = "contact_tracing"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    investigation_id = Column(Integer, ForeignKey("epidemiological_investigations.id"), nullable=False)
    
    # Contact Information  
    relationship_type = Column(String)  # Family, Work, Social, etc.
    contact_name = Column(String, nullable=False)
    contact_surname = Column(String, nullable=False)
    contact_tax_code = Column(String)
    contact_profession = Column(String)
    contact_telephone = Column(String)
    contact_address = Column(Text)
    
    # Exposure Information
    last_contact_date = Column(Date)
    exposure_duration = Column(String)
    exposure_type = Column(String)  # Close, Casual, etc.
    
    # Follow-up
    contacted = Column(Boolean, default=False)
    tested = Column(Boolean, default=False)
    test_result = Column(String)
    developed_symptoms = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    investigation = relationship("EpidemiologicalInvestigation", back_populates="contacts")


# Specific Disease Investigation Forms

class InfluenzaInvestigation(Base):
    __tablename__ = "influenza_investigations"
    
    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("epidemiological_investigations.id"), nullable=False)
    
    # Specific Data for Influenza
    hospitalized = Column(Boolean, default=False)
    antiviral_therapy = Column(Boolean, default=False)
    chronic_diseases = Column(Text)
    
    # Laboratory Data
    test_a_h1n1v = Column(Boolean, default=False)
    test_a_h1n1 = Column(Boolean, default=False)
    test_a_h3n2 = Column(Boolean, default=False)
    test_b = Column(Boolean, default=False)
    
    # Complications
    complications = Column(Text)
    outcome = Column(String)  # Recovery/Death
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BotulismInvestigation(Base):
    __tablename__ = "botulism_investigations"
    
    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("epidemiological_investigations.id"), nullable=False)
    
    # Specific Data for Botulism
    suspected_food = Column(Text)
    diplopia = Column(Boolean, default=False)
    dysphagia = Column(Boolean, default=False)
    hospitalized = Column(Boolean, default=False)
    antitoxin_serum = Column(Boolean, default=False)
    
    # Laboratory Tests
    serum_toxin_test = Column(Boolean, default=False)
    feces_toxin_test = Column(Boolean, default=False)
    food_toxin_test = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
