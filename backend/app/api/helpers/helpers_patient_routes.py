from __future__ import annotations

import json
from typing import Any, Sequence

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.models import Patient, Facility, VHT, CheckIn
from app.core.schemas import PatientDetailOut


def decode_observations(observations_json: str | None) -> dict[str, Any] | None:
    """
    Convert DB JSON string -> dict for API output.

    We keep this tolerant: if the stored JSON is corrupt, we return
    a marked object instead of crashing the request.
    """
    if not observations_json:
        return None
    try:
        loaded = json.loads(observations_json)
        if isinstance(loaded, dict):
            return loaded
        # If someone stored a non-dict JSON (e.g. list), still return it wrapped.
        return {"_non_dict_observations": True, "value": loaded}
    except Exception:
        return {"_corrupt_observations": True, "raw": observations_json}


def patient_to_detail_out(patient: Patient, recent_checkins: Sequence[CheckIn]) -> PatientDetailOut:
    """
    Convert ORM Patient + recent checkins -> PatientDetailOut (agent-ready).

    Why model_validate:
    - avoids Pylance complaining about nested dicts inside Pydantic models
    - ensures runtime validation of the response contract
    """
    payload: dict[str, Any] = {
        "id": patient.id,
        "name": patient.name,
        "phone": patient.phone,
        "backup_phone": getattr(patient, "backup_phone", None),
        "village": patient.village,
        "parish": getattr(patient, "parish", None),
        "facility_id": patient.facility_id,
        "vht_id": patient.vht_id,
        "gestational_age_weeks": patient.gestational_age_weeks,
        "missed_anc_count": patient.missed_anc_count,
        "prior_malaria": getattr(patient, "prior_malaria", False),
        "high_burden_zone": getattr(patient, "high_burden_zone", False),
        "consent_sms": getattr(patient, "consent_sms", False),
        "preferred_language": getattr(patient, "preferred_language", None),
        "status": getattr(patient, "status", "active"),
        "status_reason": getattr(patient, "status_reason", None),
        "created_at": patient.created_at,
        "updated_at": patient.updated_at,
        # These are ORM objects; nested schemas should have from_attributes=True
        "facility": patient.facility,
        "vht": patient.vht,
        "recent_checkins": [
            {
                "id": c.id,
                "patient_id": c.patient_id,
                "facility_id": c.facility_id,
                "source": c.source,
                "status": c.status,
                "initial_complaint": c.initial_complaint,
                "observations": decode_observations(getattr(c, "observations_json", None)),
                "recorded_by": getattr(c, "recorded_by", None),
                "notes": getattr(c, "notes", None),
                "created_at": c.created_at,
                "closed_at": c.closed_at,
            }
            for c in recent_checkins
        ],
    }

    return PatientDetailOut.model_validate(payload)


def validate_facility(db: Session, facility_id: int) -> Facility:
    """
    Validate facility exists and return it.
    """
    facility = db.get(Facility, facility_id)
    if facility is None:
        raise HTTPException(status_code=400, detail="Invalid facility_id")
    return facility


def validate_vht(db: Session, vht_id: int, facility_id: int) -> VHT:
    """
    Validate VHT exists AND belongs to the given facility.
    """
    vht = db.get(VHT, vht_id)
    if vht is None:
        raise HTTPException(status_code=400, detail="Invalid vht_id")
    if vht.facility_id != facility_id:
        raise HTTPException(status_code=400, detail="vht_id does not belong to facility_id")
    return vht
