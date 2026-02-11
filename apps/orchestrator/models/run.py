from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from .report import QualityReport


class RunRequest(BaseModel):
    task_type: str = Field(..., description="code_generation | refactoring | code_review")
    user_input: str
    project_id: str = "default"
    options: Optional[Dict[str, Any]] = None


class RunResponse(BaseModel):
    llm_output: str
    memory_snapshot: str
    retrieved_context: List[str]
    quality_report: QualityReport
    run_id: Optional[str] = None
    duration_ms: Optional[int] = None
