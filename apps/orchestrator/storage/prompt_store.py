from typing import List
from ..models.prompt import PromptTemplate


class PromptStore:
    def __init__(self) -> None:
        self._prompts: List[PromptTemplate] = []

    def save(self, prompt: PromptTemplate) -> None:
        self._prompts.append(prompt)

    def list(self) -> List[PromptTemplate]:
        return list(self._prompts)
