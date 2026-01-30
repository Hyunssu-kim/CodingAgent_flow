from pydantic import BaseModel
from typing import Any, Dict


class ToolRequest(BaseModel):
    payload: Dict[str, Any]


class ToolResponse(BaseModel):
    status: str
    detail: Dict[str, Any]
