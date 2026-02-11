from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from ..core.app_state import agent_loop, run_store
from ..models.run import RunRequest, RunResponse
from ..models.run_record import RunRecord

router = APIRouter()


@router.post("/run", response_model=RunResponse)
def run(request: RunRequest):
    started = perf_counter()
    try:
        response = agent_loop.run(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    duration_ms = int((perf_counter() - started) * 1000)
    run_id = uuid4().hex
    response.run_id = run_id
    response.duration_ms = duration_ms

    record = RunRecord(
        id=run_id,
        task_type=request.task_type,
        project_id=request.project_id,
        user_input=request.user_input,
        llm_output=response.llm_output,
        memory_snapshot=response.memory_snapshot,
        retrieved_context=response.retrieved_context,
        quality_report=response.quality_report,
        created_at=datetime.now(timezone.utc),
        duration_ms=duration_ms,
    )
    run_store.add(record)
    return response
