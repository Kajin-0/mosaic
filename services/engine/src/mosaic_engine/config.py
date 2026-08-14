from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MOSAIC_ENGINE_",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    service_name: str = "mosaic-engine"
    supabase_url: str | None = None
    supabase_public_key: SecretStr | None = None
    supabase_server_key: SecretStr | None = None
    supabase_timeout_seconds: float = 10.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
