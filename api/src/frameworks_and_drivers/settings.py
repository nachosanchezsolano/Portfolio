from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict

from frameworks_and_drivers.cloudflare_context import to_python


class Settings(BaseSettings):
    app_env: str = "development"
    allowed_origins: str = "http://localhost:4321"
    api_key: str = ""
    admin_api_key: str = ""
    max_message_length: int = 1200
    rate_limit_requests: int = 30
    rate_limit_window_seconds: int = 60
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [value.strip() for value in self.allowed_origins.split(",") if value.strip()]


def settings_from_worker_env(env: Any) -> Settings:
    """Build settings from Cloudflare Worker bindings at request runtime."""

    def binding(name: str, default: Any) -> Any:
        value = getattr(env, name, default)
        converted = to_python(value)
        return default if converted is None else converted

    values = {
        "app_env": binding("APP_ENV", "production"),
        "allowed_origins": binding("ALLOWED_ORIGINS", ""),
        "api_key": binding("API_KEY", ""),
        "admin_api_key": binding("ADMIN_API_KEY", ""),
        "max_message_length": binding("MAX_MESSAGE_LENGTH", 1200),
        "rate_limit_requests": binding("RATE_LIMIT_REQUESTS", 30),
        "rate_limit_window_seconds": binding("RATE_LIMIT_WINDOW_SECONDS", 60),
    }
    return Settings(**values)


@lru_cache
def get_settings() -> Settings:
    return Settings()
