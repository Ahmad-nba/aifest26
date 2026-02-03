import json
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.models import Facility, VHT


DATA_PATH = Path(__file__).parent / "data.json"


def seed_if_empty(db: Session) -> None:
    # If facilities already exist, assume seeded
    existing = db.execute(select(Facility).limit(1)).scalars().first()
    if existing:
        return

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    # Seed facilities
    name_to_facility = {}
    for f in data.get("facilities", []):
        facility = Facility(name=f["name"], level=f["level"], district=f.get("district"))
        db.add(facility)
        db.flush()  # get id without committing
        name_to_facility[facility.name] = facility

    # Seed VHTs (linked by facility_name)
    for v in data.get("vhts", []):
        facility_name = v["facility_name"]
        if facility_name not in name_to_facility:
            continue
        vht = VHT(
            name=v["name"],
            phone=v.get("phone"),
            village=v["village"],
            facility_id=name_to_facility[facility_name].id,
        )
        db.add(vht)

    db.commit()
