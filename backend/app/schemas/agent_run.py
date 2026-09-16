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
    owner_id: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: float = 0.0
    error_summary: Optional[str] = None
    final_status: Optional[str] = None

    model_config = {"from_attributes": True}
