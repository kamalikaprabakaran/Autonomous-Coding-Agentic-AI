"""Pydantic request/response schemas for coding tasks."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from backend.app.models.task import TaskStatus


class TaskCreate(BaseModel):
    """Schema for creating a new coding task."""

    project_id: str = Field(..., min_length=1, description="ID of the parent project")
    description: str = Field(..., min_length=1, description="Task description")


class TaskResponse(BaseModel):
    """Schema for task API responses."""

    id: str
    project_id: str
    description: str
    status: TaskStatus
    owner_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
