from fastapi import APIRouter, HTTPException
from app.services.agent_service import run_agent
import uuid

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/run")
def run_agent_endpoint(checkin_id: str):
    try:
        return run_agent(checkin_id=checkin_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
