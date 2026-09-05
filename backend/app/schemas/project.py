"""Pydantic request/response schemas for projects."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    name: str = Field(..., min_length=1, description="Project name")
    description: str = Field(default="", description="Project description")
    repository_path: Optional[str] = Field(default=None, description="Local repository path")
    repository_url: Optional[str] = Field(default=None, description="Remote repository URL")


class ProjectResponse(BaseModel):
    """Schema for project API responses."""

    id: str
    name: str
    description: str
    repository_path: Optional[str]
    repository_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
