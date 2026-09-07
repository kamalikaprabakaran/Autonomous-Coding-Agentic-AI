"""Application configuration management using Pydantic Settings.

All configuration is driven by environment variables. Defaults are provided
for local development; production deployments should set values explicitly.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "Autonomous Coding Agentic AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Sandbox Execution Configuration
    SANDBOX_IMAGE: str = "autonomous-agent-sandbox:latest"
    SANDBOX_TIMEOUT_SECONDS: int = 30
    SANDBOX_MEMORY_LIMIT: str = "512m"
    SANDBOX_CPU_LIMIT: float = 1.0 # NanoCPUs multiplier
    SANDBOX_NETWORK_ENABLED: bool = False

    # CORS Configuration
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Using ``lru_cache`` ensures that the ``.env`` file is only read once
    and the same ``Settings`` object is reused across the application.
    """
    return Settings()
