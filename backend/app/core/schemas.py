from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, Field
from typing import Any, Dict


# ---------- Facilities ----------
class FacilityOut(BaseModel):
    id: int
    name: str
    level: Literal["HC2", "HC3"]
    district: Optional[str] = None

    model_config = {"from_attributes": True}


# ---------- VHT ----------
class VHTOut(BaseModel):
    id: int
    name: str
    phone: Optional[str] = None
    village: str
    facility_id: int

    model_config = {"from_attributes": True}


# ---------- CheckIns (lightweight for embedding in patient detail) ----------
class CheckInOut(BaseModel):
    id: str
    patient_id: int
    facility_id: int
    source: str
    status: str
    initial_complaint: Optional[str] = None

    observations: Optional[Dict[str, Any]] = None

    recorded_by: Optional[str] = None
    notes: Optional[str] = None

    created_at: datetime
    closed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------- Patients ----------
PatientStatus = Literal["active", "paused", "closed"]


class PatientCreate(BaseModel):
    """
    Onboarding payload (MD-aligned).

    Goal: store enough baseline + contact + responsibility chain
    so the agent can do meaningful triage + follow-up plans later.
    """

    name: str = Field(min_length=1, max_length=200)

    # Primary + backup contact
    phone: Optional[str] = Field(default=None, max_length=50)
    backup_phone: Optional[str] = Field(default=None, max_length=50)

    # Geography
    village: str = Field(min_length=1, max_length=120)
    parish: Optional[str] = Field(default=None, max_length=120)

    # Responsibility chain
    facility_id: int
    vht_id: Optional[int] = None

    # Maternal baseline + monitoring baseline
    gestational_age_weeks: int = Field(ge=1, le=45)
    missed_anc_count: int = Field(default=0, ge=0, le=20)

    # Baseline risk flags
    prior_malaria: bool = False
    high_burden_zone: bool = False

    # Communication preferences / consent
    consent_sms: bool = False
    preferred_language: Optional[str] = Field(default=None, max_length=50)

    # Program status
    status: PatientStatus = "active"
    status_reason: Optional[str] = Field(default=None, max_length=250)


class PatientUpdate(BaseModel):
    """
    PATCH payload.

    Keep it permissive but structured. Route logic will enforce
    additional safety rules (e.g., gestational age not going backwards).
    """

    name: Optional[str] = Field(default=None, min_length=1, max_length=200)

    phone: Optional[str] = Field(default=None, max_length=50)
    backup_phone: Optional[str] = Field(default=None, max_length=50)

    village: Optional[str] = Field(default=None, min_length=1, max_length=120)
    parish: Optional[str] = Field(default=None, max_length=120)

    facility_id: Optional[int] = None
    vht_id: Optional[int] = None

    gestational_age_weeks: Optional[int] = Field(default=None, ge=1, le=45)
    missed_anc_count: Optional[int] = Field(default=None, ge=0, le=20)

    prior_malaria: Optional[bool] = None
    high_burden_zone: Optional[bool] = None

    consent_sms: Optional[bool] = None
    preferred_language: Optional[str] = Field(default=None, max_length=50)

    status: Optional[PatientStatus] = None
    status_reason: Optional[str] = Field(default=None, max_length=250)


class PatientListOut(BaseModel):
    """
    List-card response for GET /patients.

    Keep lightweight: enough for dashboards & filtering, not full history.
    """

    id: int
    name: str
    phone: Optional[str] = None
    village: str
    parish: Optional[str] = None

    facility_id: int
    vht_id: Optional[int] = None

    gestational_age_weeks: int
    missed_anc_count: int

    prior_malaria: bool
    high_burden_zone: bool

    consent_sms: bool
    preferred_language: Optional[str] = None

    status: PatientStatus
    updated_at: datetime

    model_config = {"from_attributes": True}


class PatientDetailOut(BaseModel):
    """
    Deep profile for GET /patients/{id} (agent-ready).

    Includes nested facility + vht + recent checkins so agent can plan
    without multiple extra API calls.
    """

    id: int
    name: str
    phone: Optional[str] = None
    backup_phone: Optional[str] = None

    village: str
    parish: Optional[str] = None

    facility_id: int
    vht_id: Optional[int] = None

    gestational_age_weeks: int
    missed_anc_count: int

    prior_malaria: bool
    high_burden_zone: bool

    consent_sms: bool
    preferred_language: Optional[str] = None

    status: PatientStatus
    status_reason: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    # Nested summaries
    facility: Optional[FacilityOut] = None
    vht: Optional[VHTOut] = None

    # Recent history snapshot
    recent_checkins: List[CheckInOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# ---------- CheckIn create/response (keep for your routes_checkin.py) ----------
class CheckInCreate(BaseModel):
    patient_id: int
    facility_id: int
    source: str = Field(min_length=1, max_length=50)
    initial_complaint: Optional[str] = Field(default=None, max_length=500)


class CheckInResponse(BaseModel):
    id: str
    patient_id: int
    facility_id: int
    source: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
