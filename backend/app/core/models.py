from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


def utcnow():
    return datetime.utcnow()


class Facility(Base):
    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    level: Mapped[str] = mapped_column(String(10), nullable=False)  # "HC2" or "HC3"
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, nullable=False
    )

    vhts = relationship("VHT", back_populates="facility")
    patients = relationship("Patient", back_populates="facility")


class VHT(Base):
    __tablename__ = "vhts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    village: Mapped[str] = mapped_column(String(120), nullable=False)

    facility_id: Mapped[int] = mapped_column(
        ForeignKey("facilities.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, nullable=False
    )

    facility = relationship("Facility", back_populates="vhts")
    patients = relationship("Patient", back_populates="vht")


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    village: Mapped[str] = mapped_column(String(120), nullable=False)

    facility_id: Mapped[int] = mapped_column(
        ForeignKey("facilities.id"), nullable=False
    )
    vht_id: Mapped[int | None] = mapped_column(ForeignKey("vhts.id"), nullable=True)

    gestational_age_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    missed_anc_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, nullable=False
    )

    facility = relationship("Facility", back_populates="patients")
    vht = relationship("VHT", back_populates="patients")


# --- Additional models like CheckIn, AgentRun can be defined similarly ---
# class CheckIn(Base):
#     __tablename__ = "checkins"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

#     patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)

#     # Observations
#     symptoms_json: Mapped[str | None] = mapped_column(String, nullable=True)
#     temp_c: Mapped[int | None] = mapped_column(Integer, nullable=True)
#     bednet_use: Mapped[bool | None] = mapped_column(nullable=True)
#     missed_anc: Mapped[bool | None] = mapped_column(nullable=True)

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime, default=utcnow, nullable=False
#     )

#     patient = relationship("Patient")


class CheckIn(Base):
    __tablename__ = "checkins"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))

    status: Mapped[str] = mapped_column(String(20), default="open")
    source: Mapped[str] = mapped_column(String(50))  # vht, sms, ussd, web
    initial_complaint: Mapped[str | None]

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    closed_at: Mapped[datetime | None]

    patient = relationship("Patient")


# --- AgentRun model to log agent executions ---
class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    checkin_id: Mapped[str] = mapped_column(ForeignKey("checkins.id"), nullable=False)

    status: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    checkin = relationship("CheckIn")
