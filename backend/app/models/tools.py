"""Domain models for agent tools."""

from typing import Any, Optional
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """Standardized output structure for all tools."""
    success: bool = Field(description="True if the operation succeeded.")
    data: Optional[Any] = Field(default=None, description="The payload of the result if successful.")
    error: Optional[str] = Field(default=None, description="A human-readable error message if failed.")


# Inputs for File Tools

class ListFilesInput(BaseModel):
    """Input for ListFilesTool. Implicitly uses the workspace root."""
    pass


class ReadFileInput(BaseModel):
    """Input for ReadFileTool."""
    path: str = Field(description="Relative path of the file to read.")


class WriteFileInput(BaseModel):
    """Input for WriteFileTool."""
    path: str = Field(description="Relative path of the file to write.")
    content: str = Field(description="The complete content to write to the file.")


class EditFileInput(BaseModel):
    """Input for EditFileTool."""
    path: str = Field(description="Relative path of the file to edit.")
    old_text: str = Field(description="The exact text block to replace.")
    new_text: str = Field(description="The text to replace it with.")


class SearchCodeInput(BaseModel):
    """Input for SearchCodeTool."""
    query: str = Field(description="The text or pattern to search for.")


class GetFileInfoInput(BaseModel):
    """Input for GetFileInfoTool."""
    path: str = Field(description="Relative path of the file to get metadata for.")


# Inputs for Git Tools

class GitStatusInput(BaseModel):
    """Input for GitStatusTool. Uses the repository path from context."""
    pass


class GitDiffInput(BaseModel):
    """Input for GitDiffTool."""
    staged: bool = Field(
        default=False,
        description="If True, return staged (index) diff. If False, return working-tree diff.",
    )


class GitBranchInput(BaseModel):
    """Input for GitBranchTool. Retrieves the current branch name."""
    pass


class GitStageInput(BaseModel):
    """Input for GitStageTool."""
    paths: list[str] = Field(
        description="List of relative file paths to stage. Path traversal is rejected."
    )


class GitCommitInput(BaseModel):
    """Input for GitCommitTool."""
    message: str = Field(description="Commit message. Must not be empty.")
