"""Typed models for Git service results.

All models are Pydantic BaseModels to ensure type safety and clear
contracts between the Git service and the rest of the application.
"""

from typing import Optional
from pydantic import BaseModel, Field


class GitStatus(BaseModel):
    """Structured result from inspecting a Git repository's current state."""

    is_repository: bool = Field(
        description="True if the path is inside a Git repository."
    )
    branch: Optional[str] = Field(
        default=None,
        description="Current branch name, or None if detached HEAD.",
    )
    is_clean: bool = Field(
        default=True,
        description="True if working tree and index are clean (no modifications).",
    )
    modified_files: list[str] = Field(
        default_factory=list,
        description="Files with modifications not yet staged.",
    )
    untracked_files: list[str] = Field(
        default_factory=list,
        description="Files that are not tracked by Git.",
    )
    staged_files: list[str] = Field(
        default_factory=list,
        description="Files that are staged (index has changes).",
    )


class GitDiff(BaseModel):
    """Structured result from a Git diff operation."""

    diff_text: str = Field(
        default="",
        description="The raw unified diff output.",
    )
    has_changes: bool = Field(
        default=False,
        description="True if there are any changes in the diff.",
    )
    staged: bool = Field(
        default=False,
        description="True if this diff is from the index (staged), False for working tree.",
    )


class GitOperationResult(BaseModel):
    """Structured result from a mutating Git operation (branch, commit, stage, etc.)."""

    success: bool = Field(
        description="True if the Git operation completed without error."
    )
    action: str = Field(
        description="Human-readable label for the operation that was performed."
    )
    stdout: str = Field(
        default="",
        description="Captured standard output from the Git process.",
    )
    stderr: str = Field(
        default="",
        description="Captured standard error from the Git process.",
    )
    exit_code: int = Field(
        default=0,
        description="Exit code returned by the Git process.",
    )
    error: Optional[str] = Field(
        default=None,
        description="High-level error description when success=False.",
    )
