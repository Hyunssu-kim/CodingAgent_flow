from fastapi import APIRouter, HTTPException

from ..core.app_state import run_store
from ..models.run_record import RunRecord, RunStats

router = APIRouter()


@router.get("/runs", response_model=list[RunRecord])
def list_runs(project_id: str | None = None, limit: int = 20):
    return run_store.list(project_id=project_id, limit=limit)


@router.get("/runs/{run_id}", response_model=RunRecord)
def get_run(run_id: str):
    record = run_store.get(run_id)
    if not record:
        raise HTTPException(status_code=404, detail="Run not found")
    return record


@router.delete("/runs/{run_id}")
def delete_run(run_id: str):
    deleted = run_store.delete(run_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"status": "deleted", "run_id": run_id}


@router.get("/runs/stats", response_model=RunStats)
def run_stats():
    return run_store.stats()
