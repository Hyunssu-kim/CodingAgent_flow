from fastapi import APIRouter, HTTPException
from ..core.app_state import memory_manager
from ..models.memory import MemoryHistoryItem, MemorySnapshot, MemoryStats

router = APIRouter()


@router.get("/memory", response_model=MemorySnapshot)
def get_memory(project_id: str = "default"):
    return memory_manager.get(project_id)


@router.post("/memory/refresh", response_model=MemorySnapshot)
def refresh_memory(project_id: str = "default"):
    # Placeholder: re-ingest docs is not wired in this endpoint.
    return memory_manager.update(project_id, [])


@router.get("/memory/{project_id}/history", response_model=list[MemoryHistoryItem])
def memory_history(project_id: str):
    return memory_manager.get_history(project_id)


@router.delete("/memory/{project_id}")
def delete_memory(project_id: str):
    deleted = memory_manager.delete(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "deleted", "project_id": project_id}


@router.get("/memory/stats", response_model=MemoryStats)
def memory_stats():
    return memory_manager.stats()
