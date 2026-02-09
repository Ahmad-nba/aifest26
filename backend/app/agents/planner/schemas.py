# app/agent/planner/schemas.py

from enum import Enum
from pydantic import BaseModel
from typing import Optional


class PlanIntent(str, Enum):
    TRIAGE = "TRIAGE"
    ADVICE = "ADVICE"
    ESCALATE = "ESCALATE"
    NOOP = "NOOP"


class Plan(BaseModel):
    intent: PlanIntent
    reason: str
    requires_policy: bool = False
    requires_tools: bool = False
    requires_human: bool = False
