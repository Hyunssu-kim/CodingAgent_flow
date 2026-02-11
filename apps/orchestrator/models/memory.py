from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional


class MemoryContext(BaseModel):
    id: str
    content: str
    source: str
    first_seen: datetime
    last_seen: datetime
    frequency: int
    importance: float


class MemorySnapshot(BaseModel):
    project_id: str
    summary: str
    updated_at: datetime
    top_contexts: List[MemoryContext] = Field(default_factory=list)


class MemoryHistoryItem(BaseModel):
    ts: datetime
    contexts: List[MemoryContext]


class MemoryStats(BaseModel):
    project_count: int
    total_entries: int
    total_history_items: int
    latest_update: Optional[datetime] = None
