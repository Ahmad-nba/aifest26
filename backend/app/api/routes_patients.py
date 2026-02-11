from __future__ import annotations


from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.db import get_db
from app.core.models import Patient, CheckIn
from app.core.schemas import (
    PatientCreate,
    PatientUpdate,
    PatientListOut,
    PatientDetailOut,
)
from app.api.helpers.helpers_patient_routes import (
    patient_to_detail_out,
    validate_facility,
    validate_vht,
)

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientDetailOut)
def create_patient(
    payload: PatientCreate, db: Session = Depends(get_db)
) -> PatientDetailOut:
    """
    Create an onboarded patient profile (MD-aligned baseline).

    Returns deep, agent-ready profile:
    - nested facility + vht
    - empty recent_checkins (new patient)
    """
    validate_facility(db, payload.facility_id)

    if payload.vht_id is not None:
        validate_vht(db, payload.vht_id, payload.facility_id)

    patient = Patient(
        name=payload.name,
        phone=payload.phone,
        backup_phone=payload.backup_phone,
        village=payload.village,
        parish=payload.parish,
        facility_id=payload.facility_id,
        vht_id=payload.vht_id,
        gestational_age_weeks=payload.gestational_age_weeks,
        missed_anc_count=payload.missed_anc_count,
        prior_malaria=payload.prior_malaria,
        high_burden_zone=payload.high_burden_zone,
        consent_sms=payload.consent_sms,
        preferred_language=payload.preferred_language,
        status=payload.status,
        status_reason=payload.status_reason,
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    # Reload with nested facility/vht for consistent response
    patient = db.execute(
        select(Patient)
        .options(joinedload(Patient.facility), joinedload(Patient.vht))
        .where(Patient.id == patient.id)
    ).scalar_one()

    return patient_to_detail_out(patient, recent_checkins=[])


@router.get("", response_model=list[PatientListOut])
def list_patients(
    facility_id: int | None = Query(default=None),
    vht_id: int | None = Query(default=None),
    status: str | None = Query(default=None, description="active | paused | closed"),
    missed_anc_min: int | None = Query(default=None, ge=0),
    gest_age_min: int | None = Query(default=None, ge=1, le=45),
    db: Session = Depends(get_db),
) -> list[PatientListOut]:
    """
    List patients (lightweight).

    Designed for dashboards & operational filtering.
    """
    stmt = select(Patient)

    if facility_id is not None:
        stmt = stmt.where(Patient.facility_id == facility_id)
    if vht_id is not None:
        stmt = stmt.where(Patient.vht_id == vht_id)
    if status is not None:
        stmt = stmt.where(Patient.status == status)
    if missed_anc_min is not None:
        stmt = stmt.where(Patient.missed_anc_count >= missed_anc_min)
    if gest_age_min is not None:
        stmt = stmt.where(Patient.gestational_age_weeks >= gest_age_min)

    stmt = stmt.order_by(Patient.updated_at.desc())

    # SQLAlchemy stubs type this as Sequence[Patient]; FastAPI accepts it
    patients = db.execute(stmt).scalars().all()
    return [PatientListOut.model_validate(p) for p in patients]


@router.get("/{patient_id}", response_model=PatientDetailOut)
def get_patient(
    patient_id: int,
    recent_checkins_limit: int = Query(default=5, ge=0, le=50),
    db: Session = Depends(get_db),
) -> PatientDetailOut:
    """
    Get deep, agent-ready patient profile including recent checkins.
    """
    patient = db.execute(
        select(Patient)
        .options(joinedload(Patient.facility), joinedload(Patient.vht))
        .where(Patient.id == patient_id)
    ).scalar_one_or_none()

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    recent_checkins: Sequence[CheckIn] = []
    if recent_checkins_limit > 0:
        recent_checkins = (
            db.execute(
                select(CheckIn)
                .where(CheckIn.patient_id == patient_id)
                .order_by(CheckIn.created_at.desc())
                .limit(recent_checkins_limit)
            )
            .scalars()
            .all()
        )

    return patient_to_detail_out(patient, recent_checkins=recent_checkins)


@router.patch("/{patient_id}", response_model=PatientDetailOut)
def update_patient(
    patient_id: int,
    payload: PatientUpdate,
    db: Session = Depends(get_db),
) -> PatientDetailOut:
    """
    Update patient profile safely (MD-aligned).

    Safety rules:
    - facility_id must exist
    - vht_id must exist and match facility
    - gestational_age_weeks cannot go backwards
    """
    patient = db.execute(
        select(Patient)
        .options(joinedload(Patient.facility), joinedload(Patient.vht))
        .where(Patient.id == patient_id)
    ).scalar_one_or_none()

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    data = payload.model_dump(exclude_unset=True)

    # Facility change
    if data.get("facility_id") is not None:
        validate_facility(db, data["facility_id"])
        patient.facility_id = data["facility_id"]

    # VHT change (must match patient's facility — possibly updated above)
    if data.get("vht_id") is not None:
        validate_vht(db, data["vht_id"], patient.facility_id)
        patient.vht_id = data["vht_id"]

    # Gestational age should not regress
    if data.get("gestational_age_weeks") is not None:
        new_ga = data["gestational_age_weeks"]
        if new_ga < patient.gestational_age_weeks:
            raise HTTPException(
                status_code=400, detail="gestational_age_weeks cannot decrease"
            )
        patient.gestational_age_weeks = new_ga

    # Apply remaining simple fields
    skip_fields = {"facility_id", "vht_id", "gestational_age_weeks"}
    for field, value in data.items():
        if field in skip_fields:
            continue
        setattr(patient, field, value)

    db.commit()

    # Refresh / hydrate nested again
    patient = db.execute(
        select(Patient)
        .options(joinedload(Patient.facility), joinedload(Patient.vht))
        .where(Patient.id == patient_id)
    ).scalar_one()

    recent_checkins = (
        db.execute(
            select(CheckIn)
            .where(CheckIn.patient_id == patient_id)
            .order_by(CheckIn.created_at.desc())
            .limit(5)
        )
        .scalars()
        .all()
    )

    return patient_to_detail_out(patient, recent_checkins=recent_checkins)
