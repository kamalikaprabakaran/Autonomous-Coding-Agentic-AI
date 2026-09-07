"""Custom exceptions for the Git service layer.

Hierarchy:
    GitError (base)
    ├── GitSecurityError     — path traversal, unsafe args, forbidden ops
    ├── GitNotRepositoryError — path is not a Git repository
    └── GitCommandError      — Git process returned a non-zero exit code
"""


class GitError(Exception):
    """Base exception for all Git service errors."""


class GitSecurityError(GitError):
    """Raised when a Git operation would violate security constraints.

    Examples:
    - Path traversal in a file path argument
    - Invalid or dangerous branch name
    - Attempted use of a forbidden Git operation (push, reset --hard, etc.)
    """


class GitNotRepositoryError(GitError):
    """Raised when the supplied path is not inside a Git repository."""


class GitCommandError(GitError):
    """Raised when a Git subprocess exits with a non-zero code.

    Attributes:
        exit_code: The process exit code.
        stdout: Captured stdout text.
        stderr: Captured stderr text.
    """

    def __init__(
        self, message: str, exit_code: int = -1, stdout: str = "", stderr: str = ""
    ):
        super().__init__(message)
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
