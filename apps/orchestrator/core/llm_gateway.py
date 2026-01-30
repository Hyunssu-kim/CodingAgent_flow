from typing import Dict


class LLMGateway:
    def generate(self, prompt: str, options: Dict | None = None) -> str:
        # Stubbed LLM output for MVP skeleton.
        return f"[LLM OUTPUT]\n{prompt}"[:4000]
