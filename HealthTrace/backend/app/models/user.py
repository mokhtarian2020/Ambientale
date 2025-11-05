from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class UserRole(enum.Enum):
    MMG = "mmg"  # General Practitioner
    PLS = "pls"  # Pediatrician of Free Choice
    UOSD = "uosd"  # Simple Departmental Operating Unit
    UOC_EPIDEMIOLOGY = "uoc_epidemiology"  # Complex Operating Unit - Epidemiology
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    telephone = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    reports = relationship("DiseaseReport", back_populates="reporting_doctor")
    investigations = relationship("EpidemiologicalInvestigation", back_populates="investigator")
