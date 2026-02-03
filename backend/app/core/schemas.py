from pydantic import BaseModel, Field
from typing import Optional, Literal


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


# ---------- Patients ----------
class PatientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=50)
    village: str = Field(min_length=1, max_length=120)
    facility_id: int
    vht_id: Optional[int] = None

    gestational_age_weeks: int = Field(ge=1, le=45)
    missed_anc_count: int = Field(default=0, ge=0, le=20)


class PatientUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=50)
    village: Optional[str] = Field(default=None, min_length=1, max_length=120)

    facility_id: Optional[int] = None
    vht_id: Optional[int] = None

    gestational_age_weeks: Optional[int] = Field(default=None, ge=1, le=45)
    missed_anc_count: Optional[int] = Field(default=None, ge=0, le=20)


class PatientOut(BaseModel):
    id: int
    name: str
    phone: Optional[str] = None
    village: str

    facility_id: int
    vht_id: Optional[int] = None

    gestational_age_weeks: int
    missed_anc_count: int

    model_config = {"from_attributes": True}
