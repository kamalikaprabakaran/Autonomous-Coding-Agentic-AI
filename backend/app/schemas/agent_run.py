"""Pydantic response schema for agent runs."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from backend.app.models.agent_run import AgentRunStatus


class AgentRunResponse(BaseModel):
    """Schema for agent run API responses."""

    id: str
    task_id: str
    status: AgentRunStatus
    iteration_count: int
    started_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}
