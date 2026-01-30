from fastapi import APIRouter, HTTPException
from ..models.run import RunRequest, RunResponse
from ..core.app_state import agent_loop

router = APIRouter()


@router.post("/run", response_model=RunResponse)
def run(request: RunRequest):
    try:
        return agent_loop.run(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
