from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

API_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]


def _resolve_env_file() -> str | None:
    candidates = [
        REPO_ROOT / ".env",
        API_ROOT / ".env",
        REPO_ROOT / ".env.example",
        API_ROOT / ".env.example",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_resolve_env_file(), extra="ignore")

    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    secret_key: str = "replace_me"
    access_token_expire_minutes: int = 60

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/crc"

    max_upload_mb: int = 100
    allowed_extensions: str = ".step,.stp,.stl,.obj,.glb,.json"

    llm_provider: str = "openai"
    openai_api_key: str | None = None
    llm_model: str = "gpt-5.4-mini"
    llm_timeout_seconds: int = 20

    job_max_runtime_seconds: int = 300

    @property
    def allowed_extensions_set(self) -> set[str]:
        return {ext.strip().lower() for ext in self.allowed_extensions.split(",") if ext.strip()}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
