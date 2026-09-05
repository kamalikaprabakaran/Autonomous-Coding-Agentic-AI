"""Tests for configuration loading."""

import os
from unittest.mock import patch

from backend.app.core.config import Settings


def test_default_settings():
    """Settings should have sensible defaults when no env vars are set."""
    settings = Settings()
    assert settings.APP_NAME == "Autonomous Coding Agentic AI"
    assert settings.APP_VERSION == "0.1.0"
    assert settings.DEBUG is False
    assert settings.LOG_LEVEL == "INFO"
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 8000


def test_settings_from_env():
    """Settings should pick up values from environment variables."""
    overrides = {
        "APP_NAME": "Test App",
        "APP_VERSION": "9.9.9",
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG",
        "HOST": "127.0.0.1",
        "PORT": "3000",
    }
    with patch.dict(os.environ, overrides, clear=False):
        settings = Settings()
        assert settings.APP_NAME == "Test App"
        assert settings.APP_VERSION == "9.9.9"
        assert settings.DEBUG is True
        assert settings.LOG_LEVEL == "DEBUG"
        assert settings.HOST == "127.0.0.1"
        assert settings.PORT == 3000
