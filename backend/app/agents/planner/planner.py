# app/agent/planner/planner.py

from app.agents.planner.schemas import Plan, PlanIntent


# def plan_checkin(checkin, patient) -> Plan:
#     """
#     Pure planner.
#     No DB writes.
#     No tools.
#     No LLM.
#     """

#     # Extremely conservative starter rules
#     if checkin.source == "HC2":
#         return Plan(
#             intent=PlanIntent.ESCALATE,
#             reason="Health center input requires escalation",
#             requires_human=True,
#         )

#     if checkin.source == "VHT":
#         return Plan(
#             intent=PlanIntent.TRIAGE,
#             reason="VHT input requires triage",
#             requires_policy=True,
#         )

#     if checkin.source == "PATIENT":
#         return Plan(
#             intent=PlanIntent.ADVICE,
#             reason="Patient self-report eligible for advice",
#             requires_policy=True,
#         )

#     return Plan(
#         intent=PlanIntent.NOOP,
#         reason="Unknown source",
#     )

def plan_checkin(checkin: dict, patient: dict) -> dict:
    source = checkin.get("source")

    if source == "HC2":
        return {
            "intent": "clinical_review",
            "priority": "high",
            "reason": "Escalated by HC2",
        }

    if source == "vht":
        return {
            "intent": "triage",
            "priority": "medium",
            "reason": "Community health worker input",
        }

    return {
        "intent": "self_report",
        "priority": "low",
        "reason": "Patient self check-in",
    }
