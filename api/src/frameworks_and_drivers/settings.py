from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    allowed_origins: str = "http://localhost:4321"
    api_key: str = ""
    max_message_length: int = 1200
    rate_limit_requests: int = 30
    rate_limit_window_seconds: int = 60
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [value.strip() for value in self.allowed_origins.split(",") if value.strip()]


def settings_from_worker_env(env: Any) -> Settings:
    """Build settings from Cloudflare Worker bindings at request runtime."""
    values = {
        "app_env": getattr(env, "APP_ENV", "production"),
        "allowed_origins": getattr(env, "ALLOWED_ORIGINS", ""),
        "api_key": getattr(env, "API_KEY", ""),
        "max_message_length": getattr(env, "MAX_MESSAGE_LENGTH", 1200),
        "rate_limit_requests": getattr(env, "RATE_LIMIT_REQUESTS", 30),
        "rate_limit_window_seconds": getattr(env, "RATE_LIMIT_WINDOW_SECONDS", 60),
    }
    return Settings(**values)


@lru_cache
def get_settings() -> Settings:
    return Settings()
