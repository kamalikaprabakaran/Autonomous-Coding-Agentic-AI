"""Agent Execution Event domain model."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentEventType(str, Enum):
    """Specific tracking points in the agent execution lifecycle."""
    RUN_STARTED = "agent_run_started"
    RUN_COMPLETED = "agent_run_completed"
    RUN_FAILED = "agent_run_failed"
    PLANNER_STARTED = "planner_started"
    PLANNER_COMPLETED = "planner_completed"
    EXPLORER_STARTED = "repository_exploration_started"
    EXPLORER_COMPLETED = "repository_exploration_completed"
    CODER_STARTED = "coder_started"
    CODER_COMPLETED = "coder_completed"
    EXECUTION_STARTED = "execution_started"
    EXECUTION_COMPLETED = "execution_completed"
    EVALUATION_STARTED = "evaluation_started"
    EVALUATION_COMPLETED = "evaluation_completed"
    CORRECTION_STARTED = "correction_started"
    CORRECTION_COMPLETED = "correction_completed"
    TOOL_CALLED = "tool_called"
    TOOL_COMPLETED = "tool_completed"


class AgentEvent(BaseModel):
    """Structured event capturing an observability action."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    event_type: AgentEventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_seconds: Optional[float] = None
    iteration: Optional[int] = None
    status: Optional[str] = None
    error: Optional[str] = None
    tool_name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
