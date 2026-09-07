"""Coding task domain model."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Controlled status values for a coding task."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class CodingTask(BaseModel):
    """Represents a coding task assigned to an agent."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    owner_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
