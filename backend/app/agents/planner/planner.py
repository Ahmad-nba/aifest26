# app/agent/planner/planner.py

#
import os
from dotenv import load_dotenv

#  Load .env into os.environ so we can access GOOGLE_API_KEY via os.getenv("GOOGLE_API_KEY")
load_dotenv()  # <-- THIS is what you were missing


from typing import cast
from langchain_google_genai import ChatGoogleGenerativeAI
from app.agents.planner.schemas import Plan
from app.agents.prompts import get_planner_prompt
from app.agents.policies import validate_plan  # <-- import policies

# LLM Initialization
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_retries=2,
    api_key=os.getenv("GOOGLE_API_KEY")
)

structured_planner = llm.with_structured_output(Plan)
planner_chain = get_planner_prompt() | structured_planner

def plan_checkin(checkin: dict, patient: dict) -> dict:
    """
    Full planning cycle:
    1. Planner generates proposed plan
    2. Policies validate and potentially modify
    3. Return validated plan
    """
    patient_str = f"Name: {patient.get('name')}, Village: {patient.get('village')}, ID: {patient.get('id')}"
    checkin_str = f"Source: {checkin.get('source')}, Complaint: {checkin.get('initial_complaint')}"

    try:
        # 1. Planner proposes plan
        response = planner_chain.invoke({
            "patient_context": patient_str,
            "checkin_context": checkin_str
        })
        plan_result = cast(Plan, response).model_dump()

        # 2. Policies validate the plan
        policy_result = validate_plan(plan_result)

        # 3. Return final plan
        return policy_result

    except Exception as e:
        print(f"Planner LLM Error: {e}")
        return {
            "approved": False,
            "reason": f"Planner failed: {str(e)}",
            "modified_plan": {
                "intent": "ESCALATE",
                "reason": "System fallback",
                "priority": "high",
                "requires_human": True,
                "tools": []
            }
        }