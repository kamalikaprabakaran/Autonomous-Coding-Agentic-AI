"""Project domain model."""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class Project(BaseModel):
    """Represents a software project managed by the agent."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str = ""
    repository_path: Optional[str] = None
    repository_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
