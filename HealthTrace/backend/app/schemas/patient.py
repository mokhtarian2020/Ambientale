from typing import Optional
from pydantic import BaseModel
from datetime import datetime, date

from app.models.patient import Gender, PatientStatus, VaccinationStatus


class PatientBase(BaseModel):
    tax_code: Optional[str] = None
    stp_code: Optional[str] = None
    eni_code: Optional[str] = None
    surname: str
    name: str
    gender: Gender
    birth_date: date
    birth_country: Optional[str] = None
    birth_province: Optional[str] = None
    birth_municipality: str
    profession: Optional[str] = None
    residence_address: Optional[str] = None
    residence_municipality: Optional[str] = None
    residence_province: Optional[str] = None
    residence_region: Optional[str] = None
    domicile_address: Optional[str] = None
    domicile_municipality: Optional[str] = None
    telephone: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    tax_code: Optional[str] = None
    surname: Optional[str] = None
    name: Optional[str] = None
    gender: Optional[Gender] = None
    birth_date: Optional[date] = None
    birth_country: Optional[str] = None
    birth_province: Optional[str] = None
    birth_municipality: Optional[str] = None
    profession: Optional[str] = None
    residence_address: Optional[str] = None
    residence_municipality: Optional[str] = None
    residence_province: Optional[str] = None
    residence_region: Optional[str] = None
    domicile_address: Optional[str] = None
    domicile_municipality: Optional[str] = None
    telephone: Optional[str] = None
    status: Optional[PatientStatus] = None


class PatientResponse(PatientBase):
    id: int
    status: PatientStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PatientSearch(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    tax_code: Optional[str] = None
