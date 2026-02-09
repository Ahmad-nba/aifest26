# from datetime import datetime
# from sqlalchemy import text

# from app.agents.graph import build_agent_graph, AgentState
# from app.core.db import get_db


# def run_agent(checkin_id: str):
#     graph = build_agent_graph()

#     # --- DB lookup ---
#     db = next(get_db())

#     checkin_row = db.execute(
#         text("SELECT patient_id FROM checkins WHERE id = :cid"),
#         {"cid": checkin_id},
#     ).fetchone()

#     if not checkin_row:
#         raise ValueError(f"Check-in {checkin_id} not found")

#     patient_id = checkin_row.patient_id

#     # --- Initial agent state ---
#     initial_state: AgentState = {
#         "patient_id": patient_id,
#         "checkin_id": checkin_id,
#         "plan": None,
#         "gated_plan": None,
#         "tool_results": [],
#         "status": "STARTED",
#     }

#     # --- Run graph ---
#     final_state = graph.invoke(initial_state)

#     # --- Persist agent run ---
#     db.execute(
#         text("""
#         INSERT INTO agent_runs
#         (patient_id, checkin_id, status, created_at)
#         VALUES (:pid, :cid, :status, :created_at)
#         """),
#         {
#             "pid": patient_id,
#             "cid": checkin_id,
#             "status": final_state["status"],
#             "created_at": datetime.utcnow(),
#         },
#     )
#     db.commit()

#     return final_state

from datetime import datetime
from sqlalchemy import text

from app.agents.graph import build_agent_graph
from app.core.db import get_db
from app.core.models import CheckIn
from app.core.models import Patient
from app.agents.graph import AgentState


def run_agent(checkin_id: str):
    graph = build_agent_graph()

    db = next(get_db())

    # --- Fetch checkin ---
    checkin = db.query(CheckIn).filter(CheckIn.id == checkin_id).first()
    if not checkin:
        raise ValueError(f"Check-in {checkin_id} not found")

    # --- Fetch patient ---
    patient = db.query(Patient).filter(Patient.id == checkin.patient_id).first()
    if not patient:
        raise ValueError(f"Patient {checkin.patient_id} not found")

    # --- Hydrate state ---
    initial_state : AgentState = {
        "patient_id": patient.id,
        "checkin_id": checkin.id,
        "patient": {
            "id": patient.id,
            "name": patient.name,
            "village": patient.village,
            "facility_id": patient.facility_id,
        },
        "checkin": {
            "id": checkin.id,
            "patient_id": checkin.patient_id,
            "source": checkin.source,
            "status": checkin.status,
            "initial_complaint": checkin.initial_complaint,
        },
        "plan": None,
        "gated_plan": None,
        "tool_results": [],
        "status": "STARTED",
    }

    # --- Run graph ---
    final_state = graph.invoke(initial_state)

    # --- Persist agent run ---
    db.execute(
        text(
            """
            INSERT INTO agent_runs
            (patient_id, checkin_id, status, created_at)
            VALUES (:pid, :cid, :status, :created_at)
            """
        ),
        {
            "pid": patient.id,
            "cid": checkin.id,
            "status": final_state["status"],
            "created_at": datetime.utcnow(),
        },
    )
    db.commit()

    return final_state
