"""Git ToolRegistry tools wrapping the GitService.

Each tool:
- Inherits from BaseTool
- Validates its input via a Pydantic model
- Delegates to GitService
- Returns a ToolResult (never raises to the caller)
- Does NOT execute arbitrary shell commands

Supported tools:
- GitStatusTool  — repository status inspection
- GitDiffTool    — diff (working-tree or staged)
- GitBranchTool  — current branch name
- GitStageTool   — controlled file staging (with path validation)
- GitCommitTool  — commit creation

Phase 7 only — no push, no GitHub API.
"""

from typing import Type
from pydantic import BaseModel

from backend.app.models.tools import (
    ToolResult,
    GitStatusInput,
    GitDiffInput,
    GitBranchInput,
    GitStageInput,
    GitCommitInput,
)
from backend.app.tools.base import BaseTool
from backend.app.git.service import GitService
from backend.app.git.exceptions import GitError, GitSecurityError, GitNotRepositoryError


def _make_git_service() -> GitService:
    """Factory so tests can monkeypatch if needed."""
    return GitService()


class GitStatusTool(BaseTool):
    """Inspect the current Git repository status.

    Returns a structured snapshot of the repository including
    current branch, clean/dirty state, and lists of modified,
    staged, and untracked files.
    """

    name = "git_status"
    description = (
        "Retrieve the current Git repository status, including branch name, "
        "modified files, staged files, and untracked files."
    )
    input_schema: Type[BaseModel] = GitStatusInput

    def execute(self, repo_path: str, args: dict) -> ToolResult:
        git = _make_git_service()
        try:
            status = git.get_status(repo_path)
            return ToolResult(success=True, data=status.model_dump())
        except (GitSecurityError, GitNotRepositoryError, GitError) as exc:
            return ToolResult(success=False, error=str(exc))
        except Exception as exc:  # pragma: no cover
            return ToolResult(success=False, error=f"Unexpected error: {exc}")


class GitDiffTool(BaseTool):
    """Retrieve a Git diff (working-tree or staged index).

    Does not modify repository state.
    """

    name = "git_diff"
    description = (
        "Get the current Git diff. Set staged=True to see staged (index) changes, "
        "or staged=False (default) for working-tree changes."
    )
    input_schema: Type[BaseModel] = GitDiffInput

    def execute(self, repo_path: str, args: dict) -> ToolResult:
        input_data = self.input_schema(**args)
        git = _make_git_service()
        try:
            diff = git.get_diff(repo_path, staged=input_data.staged)
            return ToolResult(success=True, data=diff.model_dump())
        except (GitSecurityError, GitNotRepositoryError, GitError) as exc:
            return ToolResult(success=False, error=str(exc))
        except Exception as exc:  # pragma: no cover
            return ToolResult(success=False, error=f"Unexpected error: {exc}")


class GitBranchTool(BaseTool):
    """Get the name of the current Git branch.

    Returns None for detached HEAD.
    """

    name = "git_branch"
    description = "Get the current Git branch name. Returns null for detached HEAD."
    input_schema: Type[BaseModel] = GitBranchInput

    def execute(self, repo_path: str, args: dict) -> ToolResult:
        git = _make_git_service()
        try:
            branch = git.get_current_branch(repo_path)
            return ToolResult(success=True, data={"branch": branch})
        except (GitSecurityError, GitNotRepositoryError, GitError) as exc:
            return ToolResult(success=False, error=str(exc))
        except Exception as exc:  # pragma: no cover
            return ToolResult(success=False, error=f"Unexpected error: {exc}")


class GitStageTool(BaseTool):
    """Stage specific files for a Git commit.

    Paths are validated against the repository root to prevent
    path traversal. Does NOT run 'git add .' or 'git add -A'.
    """

    name = "git_stage"
    description = (
        "Stage specific files for commit using git add. "
        "Each path must be relative to the repository root. "
        "Path traversal is rejected."
    )
    input_schema: Type[BaseModel] = GitStageInput

    def execute(self, repo_path: str, args: dict) -> ToolResult:
        input_data = self.input_schema(**args)
        git = _make_git_service()
        try:
            result = git.stage_files(repo_path, input_data.paths)
            if result.success:
                return ToolResult(success=True, data=result.model_dump())
            return ToolResult(success=False, error=result.error or result.stderr)
        except (GitSecurityError, GitNotRepositoryError, GitError) as exc:
            return ToolResult(success=False, error=str(exc))
        except Exception as exc:  # pragma: no cover
            return ToolResult(success=False, error=f"Unexpected error: {exc}")


class GitCommitTool(BaseTool):
    """Create a Git commit from the current staged index.

    Requires:
    - Non-empty commit message
    - At least one staged file (use GitStageTool first)

    Does NOT auto-stage files. Does NOT allow empty commits.
    """

    name = "git_commit"
    description = (
        "Create a Git commit. The commit message must not be empty "
        "and there must be staged changes (use git_stage first). "
        "Does not automatically stage all files."
    )
    input_schema: Type[BaseModel] = GitCommitInput

    def execute(self, repo_path: str, args: dict) -> ToolResult:
        input_data = self.input_schema(**args)
        git = _make_git_service()
        try:
            result = git.commit(repo_path, input_data.message)
            if result.success:
                return ToolResult(success=True, data=result.model_dump())
            return ToolResult(success=False, error=result.error or result.stderr)
        except (GitSecurityError, GitNotRepositoryError, GitError) as exc:
            return ToolResult(success=False, error=str(exc))
        except Exception as exc:  # pragma: no cover
            return ToolResult(success=False, error=f"Unexpected error: {exc}")
