"""Firebase settings using environment variables."""

from typing import Optional
from pydantic_settings import BaseSettings

class FirebaseSettings(BaseSettings):
    """Firebase settings from env (e.g., .env file)."""

    # For local development tests, mock out real Firebase usage
    FIREBASE_TESTING: bool = True
    
    # Can be set to a specific project id, otherwise GOOGLE_APPLICATION_CREDENTIALS determines it
    FIREBASE_PROJECT_ID: Optional[str] = None
    
    # Path to the service account JSON
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

def get_firebase_settings() -> FirebaseSettings:
    """Return a fresh settings instance."""
    return FirebaseSettings()
