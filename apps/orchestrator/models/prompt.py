from pydantic import BaseModel, Field
from typing import List, Optional


class PromptTemplate(BaseModel):
    type: str
    version: str
    role: str
    constraints: str
    output_schema: str
    template: str
    tags: List[str] = Field(default_factory=list)
    description: Optional[str] = None
