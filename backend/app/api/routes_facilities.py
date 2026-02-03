from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.db import get_db
from app.core.models import Facility
from app.core.schemas import FacilityOut

router = APIRouter(prefix="/facilities", tags=["facilities"])


@router.get("", response_model=list[FacilityOut])
def list_facilities(
    level: str | None = Query(default=None, description="Filter by level: HC2 or HC3"),
    db: Session = Depends(get_db),
):
    stmt = select(Facility)
    if level:
        stmt = stmt.where(Facility.level == level)
    facilities = db.execute(stmt).scalars().all()
    return facilities


@router.get("/{facility_id}", response_model=FacilityOut)
def get_facility(facility_id: int, db: Session = Depends(get_db)):
    facility = db.get(Facility, facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return facility
