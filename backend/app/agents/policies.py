# backend/app/agents/policies.py

from typing import Dict, Any

# Allowed intents
ALLOWED_INTENTS = {"ESCALATE", "ADVICE", "TRIAGE"}

# Allowed tools for demo purposes we are gona to tools like api calls with africa's talking, hc2 scheduling system, etc.
#  This is just for demo purposes to show how the planner can be constrained by a policy layer.
ALLOWED_TOOLS = {
    "record_vitals",
    "schedule_followup_sms",
    "escalate_hc2",
    "send_advice_sms",
    "trigger_triage_review"
}

def validate_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates a plan produced by the planner.

    Returns a dict with:
    - approved: True/False
    - reason: Why approved or not
    - modified_plan: potentially corrected plan
    """
    modified_plan = plan.copy()
    approved = True
    reasons = []

    # 1. Validate intent
    intent = plan.get("intent")
    if intent not in ALLOWED_INTENTS:
        approved = False
        reasons.append(f"Invalid intent '{intent}'. Must be one of {ALLOWED_INTENTS}.")
        modified_plan["intent"] = "ESCALATE"  # Default safe fallback

    # 2. Validate tools
    tools = plan.get("tools", [])
    invalid_tools = [t for t in tools if t not in ALLOWED_TOOLS]
    if invalid_tools:
        approved = False
        reasons.append(f"Tools not allowed: {invalid_tools}. Removing them.")
        modified_plan["tools"] = [t for t in tools if t in ALLOWED_TOOLS]

    # 3. Validate requires_human for ESCALATE
    if modified_plan["intent"] == "ESCALATE":
        modified_plan["requires_human"] = True
    elif "requires_human" not in modified_plan:
        modified_plan["requires_human"] = False

    return {
        "approved": approved,
        "reason": "; ".join(reasons) if reasons else "Plan approved.",
        "modified_plan": modified_plan
    }
