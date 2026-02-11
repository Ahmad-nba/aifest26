from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text

from app.core.db import Base


def utcnow() -> datetime:
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

    vhts: Mapped[list["VHT"]] = relationship("VHT", back_populates="facility")
    patients: Mapped[list["Patient"]] = relationship(
        "Patient", back_populates="facility"
    )
    checkins: Mapped[list["CheckIn"]] = relationship(
        "CheckIn", back_populates="facility"
    )


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

    facility: Mapped["Facility"] = relationship("Facility", back_populates="vhts")
    patients: Mapped[list["Patient"]] = relationship("Patient", back_populates="vht")


class Patient(Base):
    """
    Patient/Mother profile (Onboarding + monitoring baseline).

    This table is intentionally designed to be "agent-ready":
    it contains contact, consent, geography, responsibility linkage,
    and baseline risk indicators required by the MD spec.
    """

    __tablename__ = "patients"

    # Identity / contact
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # primary phone
    backup_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Geography / linkage (MD: village + parish)
    village: Mapped[str] = mapped_column(String(120), nullable=False)
    parish: Mapped[str | None] = mapped_column(String(120), nullable=True)

    # Responsibility chain (MD: supervising facility + responsible VHT)
    facility_id: Mapped[int] = mapped_column(
        ForeignKey("facilities.id"), nullable=False
    )
    vht_id: Mapped[int | None] = mapped_column(ForeignKey("vhts.id"), nullable=True)

    # Maternal baseline + monitoring inputs
    gestational_age_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    missed_anc_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Baseline risk flags (MD: prior malaria + high burden zone)
    prior_malaria: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    high_burden_zone: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Communication / consent / preferences (MD: consent + language)
    consent_sms: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    preferred_language: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Program status (monitoring state)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    status_reason: Mapped[str | None] = mapped_column(String(250), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow, nullable=False
    )

    facility: Mapped["Facility"] = relationship("Facility", back_populates="patients")
    vht: Mapped["VHT | None"] = relationship("VHT", back_populates="patients")

    # History (used later for agent hydration)
    checkins: Mapped[list["CheckIn"]] = relationship(
        "CheckIn",
        back_populates="patient",
        cascade="all, delete-orphan",
    )
    agent_runs: Mapped[list["AgentRun"]] = relationship(
        "AgentRun", back_populates="patient"
    )


class CheckIn(Base):
    __tablename__ = "checkins"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)

    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    facility_id: Mapped[int] = mapped_column(
        ForeignKey("facilities.id"), nullable=False
    )

    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)

    # who/where it came from (vht, sms, ussd, web, hc2)
    source: Mapped[str] = mapped_column(String(50), nullable=False)

    # human-readable complaint
    initial_complaint: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # --- AUDIT TRAIL CORE ---
    # structured observations stored as JSON string:
    # e.g {"fever": true, "temp_c": 38.1, "symptoms": ["cough", "headache"], "danger_signs": ["fast_breathing"]}
    observations_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # optional trace fields (useful in MD workflow)
    recorded_by: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # vht_id, hc2_user_id, "system"
    notes: Mapped[str | None] = mapped_column(String(800), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, nullable=False
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    patient: Mapped["Patient"] = relationship("Patient", back_populates="checkins")
    facility: Mapped["Facility"] = relationship("Facility", back_populates="checkins")
    agent_runs: Mapped[list["AgentRun"]] = relationship(
        "AgentRun", back_populates="checkin"
    )


class AgentRun(Base):
    """Audit log for each agent execution (inputs/outputs later, status now)."""

    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    checkin_id: Mapped[str] = mapped_column(ForeignKey("checkins.id"), nullable=False)

    status: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, nullable=False
    )

    patient: Mapped["Patient"] = relationship("Patient", back_populates="agent_runs")
    checkin: Mapped["CheckIn"] = relationship("CheckIn", back_populates="agent_runs")
