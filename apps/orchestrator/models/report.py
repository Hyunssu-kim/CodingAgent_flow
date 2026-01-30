from pydantic import BaseModel
from typing import Any, Dict


class QualityReport(BaseModel):
    lint: Dict[str, Any]
    test: Dict[str, Any]
    coverage: Dict[str, Any]
