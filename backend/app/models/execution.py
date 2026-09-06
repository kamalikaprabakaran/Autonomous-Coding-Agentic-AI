"""Execution models."""

from typing import Optional
from pydantic import BaseModel


class ExecutionRequest(BaseModel):
    repository_path: str
    command: str
    timeout_seconds: Optional[int] = None
    memory_limit: Optional[str] = None
    cpu_limit: Optional[float] = None
    network_enabled: Optional[bool] = None


class ExecutionResult(BaseModel):
    success: bool # False if the overall execution failed (e.g. docker error or timeout or non-zero exit)
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    duration_seconds: float = 0.0
    error: Optional[str] = None # System or docker error string if startup failed
