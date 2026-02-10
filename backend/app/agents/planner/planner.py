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


# declare api key
api_key = os.getenv("GOOGLE_API_KEY")

# 1. Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", temperature=0, max_retries=2, api_key=api_key
)

# 2. Bind the Schema
# We tell the LLM to output matching the 'Plan' schema
structured_planner = llm.with_structured_output(Plan)

# 3. Create the Chain
planner_chain = get_planner_prompt() | structured_planner


def plan_checkin(checkin: dict, patient: dict) -> dict:
    """
    Orchestrates the planning process using the LLM.
    """

    # 1. Format context for the prompt
    patient_str = f"Name: {patient.get('name')}, Village: {patient.get('village')}, ID: {patient.get('id')}"
    checkin_str = f"Source: {checkin.get('source')}, Complaint: {checkin.get('initial_complaint')}"

    # 2. Invoke the LLM
    try:
        # PYLANCE FIX: We use cast() to tell the type checker
        # "Trust me, this returns a Plan object"
        response = planner_chain.invoke(
            {"patient_context": patient_str, "checkin_context": checkin_str}
        )

        plan_result = cast(Plan, response)

        # 3. Return as dictionary
        return plan_result.model_dump()

    except Exception as e:
        print(f"Planner LLM Error: {e}")
        # Fallback for safety
        return {
            "intent": "ESCALATE",
            "reason": f"System Error - Planner Failed: {str(e)}",
            "priority": "high",
            "requires_human": True,
        }
