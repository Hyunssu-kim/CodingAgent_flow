import json
from typing import Dict
from urllib import request, error

from ..config import settings


class LLMGateway:
    def generate(self, prompt: str, options: Dict | None = None) -> str:
        if settings.llm_provider == "stub" or not settings.llm_api_key:
            return f"[LLM OUTPUT]\n{prompt}"[:4000]

        if settings.llm_provider == "gemini":
            return self._generate_gemini(prompt)

        return f"[LLM OUTPUT]\n{prompt}"[:4000]

    def _generate_gemini(self, prompt: str) -> str:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.llm_model}:generateContent"
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": settings.llm_temperature,
            },
        }
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": settings.llm_api_key,
            },
        )
        try:
            with request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            return f"[LLM ERROR] HTTP {exc.code}: {detail}"
        except Exception as exc:  # noqa: BLE001 - keep minimal for MVP
            return f"[LLM ERROR] {exc}"

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return f"[LLM ERROR] Unexpected response: {data}"
