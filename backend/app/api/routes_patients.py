from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.db import get_db
from app.core.models import Patient, Facility, VHT
from app.core.schemas import PatientCreate, PatientUpdate, PatientOut

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientOut)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    # Validate facility exists
    facility = db.get(Facility, payload.facility_id)
    if not facility:
        raise HTTPException(status_code=400, detail="Invalid facility_id")

    # Validate vht exists if provided
    if payload.vht_id is not None:
        vht = db.get(VHT, payload.vht_id)
        if not vht:
            raise HTTPException(status_code=400, detail="Invalid vht_id")
        # Optional: enforce VHT belongs to same facility
        if vht.facility_id != payload.facility_id:
            raise HTTPException(status_code=400, detail="vht_id does not belong to facility_id")

    patient = Patient(
        name=payload.name,
        phone=payload.phone,
        village=payload.village,
        facility_id=payload.facility_id,
        vht_id=payload.vht_id,
        gestational_age_weeks=payload.gestational_age_weeks,
        missed_anc_count=payload.missed_anc_count,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("", response_model=list[PatientOut])
def list_patients(
    facility_id: int | None = Query(default=None),
    vht_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Patient)
    if facility_id is not None:
        stmt = stmt.where(Patient.facility_id == facility_id)
    if vht_id is not None:
        stmt = stmt.where(Patient.vht_id == vht_id)
    patients = db.execute(stmt).scalars().all()
    return patients


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.patch("/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: int, payload: PatientUpdate, db: Session = Depends(get_db)):
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # If facility_id is changing, validate it exists
    if payload.facility_id is not None:
        facility = db.get(Facility, payload.facility_id)
        if not facility:
            raise HTTPException(status_code=400, detail="Invalid facility_id")
        patient.facility_id = payload.facility_id

    # If vht_id is changing, validate it exists (and optionally matches facility)
    if payload.vht_id is not None:
        vht = db.get(VHT, payload.vht_id)
        if not vht:
            raise HTTPException(status_code=400, detail="Invalid vht_id")
        if vht.facility_id != patient.facility_id:
            raise HTTPException(status_code=400, detail="vht_id does not belong to patient's facility")
        patient.vht_id = payload.vht_id

    # Simple field updates
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field in {"facility_id", "vht_id"}:
            continue
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)
    return patient
