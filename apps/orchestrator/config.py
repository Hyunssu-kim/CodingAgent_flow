import os
from typing import Literal

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, BaseSettings, Field, validator


def _load_env() -> str:
    env = os.getenv("APP_ENV", "dev")
    load_dotenv(".env")
    load_dotenv(f".env.{env}", override=True)
    return env


DEFAULT_ENV = _load_env()


class Settings(BaseSettings):
    # Environment
    app_env: Literal["dev", "prod"] = Field(default=DEFAULT_ENV, env="APP_ENV")

    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8080, ge=1, le=65535)

    # MCP
    mcp_server_url: AnyHttpUrl = Field(default="http://localhost:8090")
    mcp_timeout_s: float = Field(default=5.0, gt=0)

    # RAG
    top_k: int = Field(default=3, ge=1, le=20)
    chunk_size: int = Field(default=500, ge=100, le=2000)

    # Vector DB
    vector_db_path: str = Field(default="./data/vectordb")

    # LLM (stub settings)
    llm_model: str = Field(default="gpt-4")
    llm_temperature: float = Field(default=0.7, ge=0.0, le=1.0)

    @validator("app_env")
    def _validate_env(cls, v: str) -> str:
        if v not in {"dev", "prod"}:
            raise ValueError("APP_ENV must be 'dev' or 'prod'")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
