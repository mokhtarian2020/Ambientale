# Import all models to ensure they are registered with SQLAlchemy
from .user import User, UserRole
from .patient import Patient, Gender, PatientStatus, VaccinationStatus
from .disease import DiseaseReport, DiseaseCategory
from .environmental import EnvironmentalData, EnvironmentalDataBatch
from .investigation import (
    EpidemiologicalInvestigation,
    ContactTracing,
    CaseType,
    InfluenzaInvestigation,
    BotulismInvestigation
)

__all__ = [
    "User",
    "UserRole", 
    "Patient",
    "Gender",
    "PatientStatus",
    "VaccinationStatus",
    "DiseaseReport",
    "DiseaseCategory",
    "EnvironmentalData",
    "EnvironmentalDataBatch",
    "EpidemiologicalInvestigation",
    "ContactTracing",
    "CaseType",
    "InfluenzaInvestigation",
    "BotulismInvestigation"
]
