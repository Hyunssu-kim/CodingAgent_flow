from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel

from .report import QualityReport


class RunRecord(BaseModel):
    id: str
    task_type: str
    project_id: str
    user_input: str
    llm_output: str
    memory_snapshot: str
    retrieved_context: List[str]
    quality_report: QualityReport
    created_at: datetime
    duration_ms: int


class RunStats(BaseModel):
    total_runs: int
    project_count: int
    task_type_counts: Dict[str, int]
    latest_run_at: Optional[datetime] = None
