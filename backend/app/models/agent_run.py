"""Agent run domain model."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentRunStatus(str, Enum):
    """Controlled status values for an agent run."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentRun(BaseModel):
    """Represents a single execution run of the coding agent."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    task_id: str
    status: AgentRunStatus = AgentRunStatus.PENDING
    iteration_count: int = 0
    owner_id: Optional[str] = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
