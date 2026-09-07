"""Git service package for controlled Git repository operations.

Provides a safe, restricted Git abstraction that:
- Uses shell=False with fixed argument lists
- Validates all paths against repository root
- Exposes only explicitly allowlisted Git operations
- Does NOT support push, GitHub API, or arbitrary command execution

Phase 7 only — no push or remote operations.
"""

from backend.app.git.service import GitService
from backend.app.git.models import GitStatus, GitDiff, GitOperationResult
from backend.app.git.exceptions import (
    GitError,
    GitSecurityError,
    GitNotRepositoryError,
    GitCommandError,
)

__all__ = [
    "GitService",
    "GitStatus",
    "GitDiff",
    "GitOperationResult",
    "GitError",
    "GitSecurityError",
    "GitNotRepositoryError",
    "GitCommandError",
]
