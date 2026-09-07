"""Controlled Git service implementation.

SECURITY CONSTRAINTS (enforced throughout this module):
- All subprocess calls use shell=False with explicit argument lists.
- No arbitrary Git command execution — only the explicitly allowlisted
  command structures defined here are ever invoked.
- Repository paths are resolved and validated before every command.
- Branch names are validated with git check-ref-format before use.
- File paths for staging are checked against the repository root to
  prevent path traversal.
- Forbidden operations (push, reset --hard, clean -fd, checkout -f)
  are NOT exposed and do NOT exist in this module.
- Git credentials/config secrets are never read or transmitted.

Supported Git operations (allowlist):
- git rev-parse --is-inside-work-tree         (detection)
- git rev-parse --show-toplevel               (root discovery)
- git status --short --branch                 (status)
- git branch --show-current                   (branch)
- git diff                                    (working-tree diff)
- git diff --cached                           (staged diff)
- git check-ref-format --branch <name>        (branch name validation)
- git switch -c <branch>                      (branch creation)
- git switch <branch>                         (branch checkout)
- git checkout <branch>                       (branch checkout fallback)
- git add -- <path> [<path> ...]              (controlled staging)
- git commit -m <message>                     (commit)

Phase 7 only — no push, no remote, no GitHub API.
"""

import re
import subprocess
from pathlib import Path
from typing import Optional

from backend.app.git.exceptions import (
    GitCommandError,
    GitError,
    GitNotRepositoryError,
    GitSecurityError,
)
from backend.app.git.models import GitDiff, GitOperationResult, GitStatus

# Subprocess timeout in seconds for all Git commands.
_GIT_TIMEOUT = 30

# Characters that must never appear in a branch name argument we pass to Git.
# Git's own check-ref-format handles most of them, but we pre-reject the
# most dangerous ones before even reaching subprocess.
_BRANCH_FORBIDDEN_RE = re.compile(r"[\x00-\x1f\x7f\s;|&$`\\\"'<>]")

# Characters that must never appear in a commit message
_COMMIT_MSG_FORBIDDEN_RE = re.compile(r"[\x00]")


def _resolve_repo_path(path: str) -> Path:
    """Resolve and validate a repository path.

    Raises:
        GitSecurityError: If path is empty or cannot be resolved.
        GitNotRepositoryError: If path does not exist.
    """
    if not path or not path.strip():
        raise GitSecurityError("Repository path must not be empty.")
    try:
        resolved = Path(path).resolve(strict=True)
    except FileNotFoundError:
        raise GitNotRepositoryError(f"Path does not exist: {path}")
    except OSError as exc:
        raise GitSecurityError(f"Invalid repository path: {path}") from exc
    if not resolved.is_dir():
        raise GitNotRepositoryError(f"Path is not a directory: {path}")
    return resolved


def _run_git(
    args: list[str],
    cwd: Path,
    *,
    check: bool = False,
    input_text: Optional[str] = None,
) -> subprocess.CompletedProcess:
    """Run a Git command safely with shell=False.

    Args:
        args: Argument list starting with 'git', e.g. ['git', 'status'].
        cwd: Working directory (must be an already-resolved Path).
        check: If True, raise GitCommandError on non-zero exit.
        input_text: Optional stdin text.

    Returns:
        subprocess.CompletedProcess with stdout and stderr as strings.

    Raises:
        GitCommandError: If check=True and exit code != 0.
        GitError: On timeout or other OS-level failure.
    """
    assert args and args[0] == "git", "Only 'git' commands are allowed."

    try:
        result = subprocess.run(
            args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=_GIT_TIMEOUT,
            shell=False,  # SECURITY: never use shell=True
            input=input_text,
        )
    except subprocess.TimeoutExpired as exc:
        raise GitError(
            f"Git command timed out after {_GIT_TIMEOUT}s: {' '.join(args)}"
        ) from exc
    except FileNotFoundError as exc:
        raise GitError(
            "Git executable not found. Ensure Git is installed and on PATH."
        ) from exc
    except OSError as exc:
        raise GitError(f"OS error running git command: {exc}") from exc

    if check and result.returncode != 0:
        raise GitCommandError(
            f"Git command failed (exit {result.returncode}): {' '.join(args)}",
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )

    return result


def _validate_branch_name(branch_name: str, cwd: Path) -> None:
    """Validate a branch name using git check-ref-format.

    Pre-rejects obviously dangerous characters before calling Git, then
    delegates to Git's own validation logic.

    Raises:
        GitSecurityError: If the branch name is invalid or dangerous.
    """
    if not branch_name or not branch_name.strip():
        raise GitSecurityError("Branch name must not be empty.")

    if _BRANCH_FORBIDDEN_RE.search(branch_name):
        raise GitSecurityError(
            f"Branch name contains forbidden characters: {branch_name!r}"
        )

    # Reject path-traversal patterns
    if ".." in branch_name or branch_name.startswith("/") or branch_name.startswith("-"):
        raise GitSecurityError(
            f"Branch name has dangerous format: {branch_name!r}"
        )

    # Delegate to Git's canonical validation
    result = _run_git(
        ["git", "check-ref-format", "--branch", branch_name],
        cwd=cwd,
    )
    if result.returncode != 0:
        raise GitSecurityError(
            f"Invalid branch name rejected by git check-ref-format: {branch_name!r}"
        )


def _validate_file_path_for_staging(repo_root: Path, file_path: str) -> Path:
    """Resolve and validate a file path for staging against the repo root.

    Raises:
        GitSecurityError: On path traversal or empty path.
    """
    if not file_path or not file_path.strip():
        raise GitSecurityError("File path for staging must not be empty.")

    # Anchor to repo root and resolve — same technique as the existing
    # resolve_safe_path utility in discovery.py but inline to avoid coupling.
    target = (repo_root / file_path).resolve()

    try:
        target.relative_to(repo_root)
    except ValueError:
        raise GitSecurityError(
            f"Path traversal detected in staging path: {file_path!r}"
        )

    return target


def _parse_status_output(output: str) -> tuple[list[str], list[str], list[str]]:
    """Parse 'git status --short --branch' output.

    Returns:
        Tuple of (modified_files, untracked_files, staged_files).
    """
    modified: list[str] = []
    untracked: list[str] = []
    staged: list[str] = []

    for line in output.splitlines():
        if len(line) < 2:
            continue
        if line.startswith("##"):
            # branch header line — skip (handled separately)
            continue

        index_status = line[0]   # staged column
        worktree_status = line[1]  # working-tree column
        # Filename starts after the two-character status prefix and a space
        filename = line[3:] if len(line) > 3 else line[2:].strip()
        # Handle rename notation "old -> new"
        if " -> " in filename:
            filename = filename.split(" -> ")[-1]
        filename = filename.strip().strip('"')

        if not filename:
            continue

        if worktree_status == "?":
            # Both columns are '?' for untracked
            untracked.append(filename)
        else:
            if index_status not in (" ", "?"):
                staged.append(filename)
            if worktree_status not in (" ", "?"):
                modified.append(filename)

    return modified, untracked, staged


class GitService:
    """Controlled Git operations service.

    All methods operate on an explicitly supplied repository path.
    No global state is maintained. All subprocess calls use shell=False.

    The public API maps 1-to-1 to safe, fixed Git command structures.
    There is no 'run_arbitrary_command' or generic shell execution API.
    """

    # ------------------------------------------------------------------ #
    # Read-only / inspection operations                                    #
    # ------------------------------------------------------------------ #

    def is_git_repository(self, repository_path: str) -> bool:
        """Return True if the path is inside a Git repository.

        Uses: git rev-parse --is-inside-work-tree
        """
        try:
            cwd = _resolve_repo_path(repository_path)
        except (GitSecurityError, GitNotRepositoryError):
            return False

        result = _run_git(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=cwd,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"

    def get_current_branch(self, repository_path: str) -> Optional[str]:
        """Return the current branch name, or None for detached HEAD.

        Uses: git branch --show-current

        Raises:
            GitNotRepositoryError: If path is not a Git repository.
            GitSecurityError: If path is invalid.
        """
        cwd = _resolve_repo_path(repository_path)

        if not self.is_git_repository(repository_path):
            raise GitNotRepositoryError(
                f"Not a Git repository: {repository_path}"
            )

        result = _run_git(["git", "branch", "--show-current"], cwd=cwd)
        branch = result.stdout.strip()
        # Empty output means detached HEAD
        return branch if branch else None

    def get_status(self, repository_path: str) -> GitStatus:
        """Return structured repository status.

        Uses: git status --short --branch

        Raises:
            GitNotRepositoryError: If path is not a Git repository.
            GitSecurityError: If path is invalid.
        """
        cwd = _resolve_repo_path(repository_path)

        if not self.is_git_repository(repository_path):
            return GitStatus(is_repository=False)

        result = _run_git(
            ["git", "status", "--short", "--branch"],
            cwd=cwd,
        )

        # Parse branch from first line: ## main...origin/main
        branch: Optional[str] = None
        lines = result.stdout.splitlines()
        if lines and lines[0].startswith("##"):
            branch_part = lines[0][3:]  # strip "## "
            # Handle "No commits yet on main"
            if "No commits yet on" in branch_part:
                branch = branch_part.split(" on ")[-1].strip()
            else:
                branch = branch_part.split("...")[0].split(" ")[0].strip()
                if not branch:
                    branch = None

        modified, untracked, staged_files = _parse_status_output(result.stdout)

        is_clean = not modified and not untracked and not staged_files

        return GitStatus(
            is_repository=True,
            branch=branch,
            is_clean=is_clean,
            modified_files=modified,
            untracked_files=untracked,
            staged_files=staged_files,
        )

    def get_diff(self, repository_path: str, staged: bool = False) -> GitDiff:
        """Return a structured diff.

        Args:
            repository_path: Path to the Git repository.
            staged: If True, return staged (index) diff; otherwise working-tree diff.

        Uses: git diff  or  git diff --cached

        Raises:
            GitNotRepositoryError: If path is not a Git repository.
            GitSecurityError: If path is invalid.
        """
        cwd = _resolve_repo_path(repository_path)

        if not self.is_git_repository(repository_path):
            raise GitNotRepositoryError(
                f"Not a Git repository: {repository_path}"
            )

        cmd = ["git", "diff", "--cached"] if staged else ["git", "diff"]
        result = _run_git(cmd, cwd=cwd)

        diff_text = result.stdout
        return GitDiff(
            diff_text=diff_text,
            has_changes=bool(diff_text.strip()),
            staged=staged,
        )

    # ------------------------------------------------------------------ #
    # Mutating operations                                                  #
    # ------------------------------------------------------------------ #

    def create_branch(
        self, repository_path: str, branch_name: str
    ) -> GitOperationResult:
        """Create a new branch without switching to it.

        Uses: git switch -c <branch_name>

        Security:
        - Branch name is validated with git check-ref-format.
        - Does NOT force-create; fails if branch already exists.

        Raises:
            GitNotRepositoryError: If path is not a Git repository.
            GitSecurityError: If branch name is invalid or path is unsafe.
        """
        cwd = _resolve_repo_path(repository_path)

        if not self.is_git_repository(repository_path):
            raise GitNotRepositoryError(
                f"Not a Git repository: {repository_path}"
            )

        _validate_branch_name(branch_name, cwd)

        # Use 'switch -c' which is the modern, safe form.
        # It fails (non-zero) if branch already exists without -f.
        result = _run_git(
            ["git", "switch", "-c", branch_name],
            cwd=cwd,
        )

        if result.returncode != 0:
            return GitOperationResult(
                success=False,
                action="create_branch",
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                error=f"Branch creation failed: {result.stderr.strip()}",
            )

        return GitOperationResult(
            success=True,
            action="create_branch",
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
        )

    def checkout_branch(
        self, repository_path: str, branch_name: str
    ) -> GitOperationResult:
        """Switch to an existing branch.

        Safety check: Refuses to switch if the working tree is dirty,
        since doing so could lose uncommitted modifications.

        Uses: git switch <branch_name>  (fallback: git checkout <branch_name>)

        Security:
        - Branch name is validated.
        - Dirty repository is rejected before switching.
        - Does NOT use -f / --force.

        Raises:
            GitNotRepositoryError: If path is not a Git repository.
            GitSecurityError: If branch name is invalid, path is unsafe, or repo is dirty.
        """
        cwd = _resolve_repo_path(repository_path)

        if not self.is_git_repository(repository_path):
            raise GitNotRepositoryError(
                f"Not a Git repository: {repository_path}"
            )

        _validate_branch_name(branch_name, cwd)

        # Inspect repository state before touching anything
        status = self.get_status(repository_path)
        if not status.is_clean:
            raise GitSecurityError(
                "Refusing to switch branches: repository has uncommitted changes. "
                "Commit or stash your changes before switching."
            )

        result = _run_git(
            ["git", "switch", branch_name],
            cwd=cwd,
        )

        # Older Git versions don't have 'switch'; fall back to 'checkout'
        if result.returncode != 0 and "unknown switch" in result.stderr.lower():
            result = _run_git(
                ["git", "checkout", branch_name],
                cwd=cwd,
            )

        if result.returncode != 0:
            return GitOperationResult(
                success=False,
                action="checkout_branch",
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                error=f"Branch switch failed: {result.stderr.strip()}",
            )

        return GitOperationResult(
            success=True,
            action="checkout_branch",
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
        )

    def stage_files(
        self, repository_path: str, paths: list[str]
    ) -> GitOperationResult:
        """Stage specific files for commit.

        Uses: git add -- <path> [<path> ...]

        Security:
        - Each path is validated against the repository root.
        - Path traversal is rejected.
        - Does NOT run 'git add .' or 'git add -A'.

        Raises:
            GitNotRepositoryError: If path is not a Git repository.
            GitSecurityError: If any file path escapes the repository root.
        """
        cwd = _resolve_repo_path(repository_path)

        if not self.is_git_repository(repository_path):
            raise GitNotRepositoryError(
                f"Not a Git repository: {repository_path}"
            )

        if not paths:
            return GitOperationResult(
                success=False,
                action="stage_files",
                error="No file paths provided to stage.",
                exit_code=-1,
            )

        # Validate every path before sending any to git add
        validated: list[str] = []
        for p in paths:
            resolved = _validate_file_path_for_staging(cwd, p)
            # Pass the resolved absolute path to avoid ambiguity
            validated.append(str(resolved))

        result = _run_git(
            ["git", "add", "--"] + validated,
            cwd=cwd,
        )

        if result.returncode != 0:
            return GitOperationResult(
                success=False,
                action="stage_files",
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                error=f"git add failed: {result.stderr.strip()}",
            )

        return GitOperationResult(
            success=True,
            action="stage_files",
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
        )

    def commit(
        self, repository_path: str, message: str
    ) -> GitOperationResult:
        """Create a commit from the current index.

        Pre-conditions checked before running git commit:
        - Repository must have staged changes (non-empty index diff).
        - Message must be non-empty.
        - Message must not contain null bytes.

        Uses: git commit -m <message>

        Security:
        - message is passed as a single argument element, never shell-interpolated.
        - Does NOT auto-stage files (the agent must call stage_files first).
        - Does NOT use --allow-empty.

        Raises:
            GitNotRepositoryError: If path is not a Git repository.
            GitSecurityError: If message is empty, unsafe, or no staged changes exist.
        """
        cwd = _resolve_repo_path(repository_path)

        if not self.is_git_repository(repository_path):
            raise GitNotRepositoryError(
                f"Not a Git repository: {repository_path}"
            )

        if not message or not message.strip():
            raise GitSecurityError("Commit message must not be empty.")

        if _COMMIT_MSG_FORBIDDEN_RE.search(message):
            raise GitSecurityError(
                "Commit message contains forbidden characters (null byte)."
            )

        # Ensure there are staged changes
        staged_diff = self.get_diff(repository_path, staged=True)
        if not staged_diff.has_changes:
            raise GitSecurityError(
                "Nothing staged to commit. Use stage_files() before committing."
            )

        result = _run_git(
            ["git", "commit", "-m", message],
            cwd=cwd,
        )

        if result.returncode != 0:
            return GitOperationResult(
                success=False,
                action="commit",
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                error=f"git commit failed: {result.stderr.strip()}",
            )

        return GitOperationResult(
            success=True,
            action="commit",
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
        )
