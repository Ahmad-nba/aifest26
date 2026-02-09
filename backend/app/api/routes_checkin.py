import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.models import CheckIn
from app.core.models import Patient
from app.core.models import Facility
from app.core.schemas import CheckInCreate, CheckInResponse

router = APIRouter(prefix="/checkins", tags=["checkins"])


@router.post("", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
def create_checkin(payload: CheckInCreate, db: Session = Depends(get_db)):
    # validate patient
    patient = db.get(Patient, payload.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # validate facility
    facility = db.get(Facility, payload.facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")

    if payload.source not in {"vht", "patient", "HC2", "sms", "ussd", "web"}:
        raise HTTPException(status_code=400, detail="Invalid source")

    checkin = CheckIn(
        id=str(uuid.uuid4()),   # ✅ REQUIRED
        patient_id=payload.patient_id,
        facility_id=payload.facility_id,
        source=payload.source,
        initial_complaint=payload.initial_complaint,
    )

    db.add(checkin)
    db.commit()
    db.refresh(checkin)

    return checkin
