# backend/app/agents/tools.py

def execute_tool(tool_name: str, patient: dict, checkin: dict):
    """
    Execute a tool. For demo, we just print actions.
    """
    if tool_name == "record_vitals":
        print(f"Recording vitals for {patient['name']}")
    elif tool_name == "schedule_followup_sms":
        print(f"Scheduling follow-up SMS for {patient['name']}")
    elif tool_name == "escalate_hc2":
        print(f"Escalating to HC2 for {patient['name']}")
    elif tool_name == "send_advice_sms":
        print(f"Sending advice SMS to {patient['name']}")
    elif tool_name == "trigger_triage_review":
        print(f"Triggering human triage review for {patient['name']}")
    else:
        print(f"Unknown tool: {tool_name}")
