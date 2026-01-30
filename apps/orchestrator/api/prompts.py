from fastapi import APIRouter, HTTPException
from typing import List
from ..models.prompt import PromptTemplate
from ..core.app_state import prompt_registry

router = APIRouter()


@router.get("/prompts", response_model=List[PromptTemplate])
def list_prompts():
    return prompt_registry.list()


@router.post("/prompts", response_model=PromptTemplate)
def create_prompt(prompt: PromptTemplate):
    existing = prompt_registry.get(prompt.type, prompt.version)
    if existing:
        raise HTTPException(status_code=409, detail="Prompt already exists")
    return prompt_registry.save(prompt)
