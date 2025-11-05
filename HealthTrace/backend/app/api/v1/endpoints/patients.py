from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.patient import Patient, PatientStatus
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse, PatientSearch

router = APIRouter()


@router.post("/", response_model=PatientResponse)
def create_patient(
    patient_in: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new patient"""
    # Check if patient already exists by tax_code
    if patient_in.tax_code and db.query(Patient).filter(Patient.tax_code == patient_in.tax_code).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient with this tax code already exists"
        )
    
    db_patient = Patient(**patient_in.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    
    return db_patient


@router.get("/search", response_model=List[PatientResponse])
def search_patients(
    name: Optional[str] = Query(None, description="Patient name"),
    surname: Optional[str] = Query(None, description="Patient surname"),
    tax_code: Optional[str] = Query(None, description="Patient tax code"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Search patients by name, surname, or tax code"""
    query = db.query(Patient)
    
    if tax_code:
        query = query.filter(Patient.tax_code.ilike(f"%{tax_code}%"))
    if name:
        query = query.filter(Patient.name.ilike(f"%{name}%"))
    if surname:
        query = query.filter(Patient.surname.ilike(f"%{surname}%"))
    
    # If no specific filters, don't return all patients
    if not any([name, surname, tax_code]):
        return []
    
    patients = query.offset(skip).limit(limit).all()
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific patient"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a patient"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Update patient fields
    update_data = patient_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    db.commit()
    db.refresh(patient)
    
    return patient


@router.put("/{patient_id}/status")
def update_patient_status(
    patient_id: int,
    status: PatientStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update patient status (Active/Recovered/Deceased)"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    patient.status = status
    db.commit()
    db.refresh(patient)
    
    return {"message": "Patient status updated", "status": status}
