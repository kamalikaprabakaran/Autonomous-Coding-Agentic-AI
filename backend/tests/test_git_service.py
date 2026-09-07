"""Comprehensive tests for Phase 7 GitService.

All tests use temporary directories initialized as real Git repositories.
The actual project repository (D:\\Autonomous Coding Agentic AI) is
NEVER mutated by these tests.

Local Git identity is set per-repository only:
    git config user.name "Test User"
    git config user.email "test@example.com"

No global Git configuration is modified.
"""

import inspect
import subprocess
import textwrap
from pathlib import Path

import pytest

from backend.app.git.service import GitService, _GIT_TIMEOUT
from backend.app.git.models import GitStatus, GitDiff, GitOperationResult
from backend.app.git.exceptions import (
    GitError,
    GitSecurityError,
    GitNotRepositoryError,
    GitCommandError,
)


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #

def _git(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    """Run a git command in a test repository."""
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        shell=False,
        check=check,
    )


def _init_repo(path: Path) -> None:
    """Initialize a bare git repo with local identity for testing."""
    _git(["init"], path)
    _git(["config", "user.name", "Test User"], path)
    _git(["config", "user.email", "test@example.com"], path)


def _make_commit(path: Path, filename: str = "readme.txt", message: str = "Initial commit") -> None:
    """Create a file and commit it in the test repository."""
    (path / filename).write_text("hello\n", encoding="utf-8")
    _git(["add", filename], path)
    _git(["commit", "-m", message], path)


# ------------------------------------------------------------------ #
# Fixtures                                                             #
# ------------------------------------------------------------------ #

@pytest.fixture
def svc() -> GitService:
    return GitService()


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """A fresh Git repository with one initial commit."""
    _init_repo(tmp_path)
    _make_commit(tmp_path)
    return tmp_path


@pytest.fixture
def empty_git_repo(tmp_path: Path) -> Path:
    """A fresh Git repository with no commits."""
    _init_repo(tmp_path)
    return tmp_path


@pytest.fixture
def non_git_dir(tmp_path: Path) -> Path:
    """A plain directory that is NOT a Git repository."""
    return tmp_path


# ================================================================== #
# 1. Git repository detection                                          #
# ================================================================== #

def test_is_git_repository_true(svc: GitService, git_repo: Path):
    """A properly initialized Git repo is recognized."""
    assert svc.is_git_repository(str(git_repo)) is True


# ================================================================== #
# 2. Non-Git directory detection                                       #
# ================================================================== #

def test_is_git_repository_false(svc: GitService, non_git_dir: Path):
    """A plain directory is not identified as a Git repository."""
    assert svc.is_git_repository(str(non_git_dir)) is False


# ================================================================== #
# 3. Current branch retrieval                                          #
# ================================================================== #

def test_get_current_branch(svc: GitService, git_repo: Path):
    """Returns the current branch name (master or main)."""
    branch = svc.get_current_branch(str(git_repo))
    assert branch is not None
    assert isinstance(branch, str)
    assert len(branch) > 0


def test_get_current_branch_not_repo(svc: GitService, non_git_dir: Path):
    """Raises GitNotRepositoryError for a non-repo path."""
    with pytest.raises(GitNotRepositoryError):
        svc.get_current_branch(str(non_git_dir))


# ================================================================== #
# 4. Repository status                                                 #
# ================================================================== #

def test_get_status_returns_git_status(svc: GitService, git_repo: Path):
    """get_status returns a GitStatus model."""
    status = svc.get_status(str(git_repo))
    assert isinstance(status, GitStatus)
    assert status.is_repository is True


def test_get_status_non_repo(svc: GitService, non_git_dir: Path):
    """get_status on a non-repo returns GitStatus with is_repository=False."""
    status = svc.get_status(str(non_git_dir))
    assert status.is_repository is False


# ================================================================== #
# 5. Clean repository detection                                        #
# ================================================================== #

def test_clean_repository(svc: GitService, git_repo: Path):
    """A fresh repo with no modifications is clean."""
    status = svc.get_status(str(git_repo))
    assert status.is_clean is True
    assert status.modified_files == []
    assert status.untracked_files == []
    assert status.staged_files == []


# ================================================================== #
# 6. Modified file detection                                           #
# ================================================================== #

def test_modified_file_detected(svc: GitService, git_repo: Path):
    """A modified tracked file appears in modified_files."""
    (git_repo / "readme.txt").write_text("changed\n", encoding="utf-8")
    status = svc.get_status(str(git_repo))
    assert status.is_clean is False
    assert "readme.txt" in status.modified_files


# ================================================================== #
# 7. Untracked file detection                                          #
# ================================================================== #

def test_untracked_file_detected(svc: GitService, git_repo: Path):
    """A new, untracked file appears in untracked_files."""
    (git_repo / "newfile.txt").write_text("new\n", encoding="utf-8")
    status = svc.get_status(str(git_repo))
    assert status.is_clean is False
    assert "newfile.txt" in status.untracked_files


# ================================================================== #
# 8. Staged file detection                                             #
# ================================================================== #

def test_staged_file_detected(svc: GitService, git_repo: Path):
    """A staged file appears in staged_files."""
    (git_repo / "staged.txt").write_text("staged content\n", encoding="utf-8")
    _git(["add", "staged.txt"], git_repo)
    status = svc.get_status(str(git_repo))
    assert "staged.txt" in status.staged_files
    assert status.is_clean is False


# ================================================================== #
# 9. Working-tree diff                                                 #
# ================================================================== #

def test_working_tree_diff(svc: GitService, git_repo: Path):
    """get_diff returns a non-empty diff after modifying a tracked file."""
    (git_repo / "readme.txt").write_text("modified content\n", encoding="utf-8")
    diff = svc.get_diff(str(git_repo), staged=False)
    assert isinstance(diff, GitDiff)
    assert diff.has_changes is True
    assert diff.staged is False
    assert "readme.txt" in diff.diff_text or diff.diff_text  # non-empty


def test_working_tree_diff_clean(svc: GitService, git_repo: Path):
    """get_diff on a clean repo returns an empty diff."""
    diff = svc.get_diff(str(git_repo), staged=False)
    assert diff.has_changes is False
    assert diff.diff_text == ""


# ================================================================== #
# 10. Staged diff                                                      #
# ================================================================== #

def test_staged_diff(svc: GitService, git_repo: Path):
    """get_diff(staged=True) shows staged changes."""
    (git_repo / "newfile.txt").write_text("staged data\n", encoding="utf-8")
    _git(["add", "newfile.txt"], git_repo)
    diff = svc.get_diff(str(git_repo), staged=True)
    assert diff.has_changes is True
    assert diff.staged is True


def test_staged_diff_empty_when_nothing_staged(svc: GitService, git_repo: Path):
    """get_diff(staged=True) is empty when nothing is staged."""
    diff = svc.get_diff(str(git_repo), staged=True)
    assert diff.has_changes is False


# ================================================================== #
# 11. Branch creation                                                  #
# ================================================================== #

def test_create_branch(svc: GitService, git_repo: Path):
    """create_branch creates a new branch successfully."""
    result = svc.create_branch(str(git_repo), "feature/test-branch")
    assert isinstance(result, GitOperationResult)
    assert result.success is True
    assert result.action == "create_branch"
    # Verify branch exists
    branch_result = _git(["branch", "--list", "feature/test-branch"], git_repo)
    assert "feature/test-branch" in branch_result.stdout


# ================================================================== #
# 12. Branch creation with invalid name                                #
# ================================================================== #

def test_create_branch_invalid_name_dot_dot(svc: GitService, git_repo: Path):
    """Branch names with '..' are rejected as a security violation."""
    with pytest.raises(GitSecurityError):
        svc.create_branch(str(git_repo), "../../etc/evil")


def test_create_branch_invalid_name_space(svc: GitService, git_repo: Path):
    """Branch names with spaces are rejected."""
    with pytest.raises(GitSecurityError):
        svc.create_branch(str(git_repo), "bad branch name")


def test_create_branch_invalid_name_empty(svc: GitService, git_repo: Path):
    """Empty branch names are rejected."""
    with pytest.raises(GitSecurityError):
        svc.create_branch(str(git_repo), "")


def test_create_branch_invalid_name_leading_dash(svc: GitService, git_repo: Path):
    """Branch names starting with '-' are rejected."""
    with pytest.raises(GitSecurityError):
        svc.create_branch(str(git_repo), "-bad-branch")


def test_create_branch_invalid_name_shell_chars(svc: GitService, git_repo: Path):
    """Branch names with shell metacharacters are rejected."""
    with pytest.raises(GitSecurityError):
        svc.create_branch(str(git_repo), "branch;rm -rf /")


# ================================================================== #
# 13. Branch already exists                                            #
# ================================================================== #

def test_create_branch_already_exists(svc: GitService, git_repo: Path):
    """Creating a branch that already exists returns success=False."""
    # First creation — switches to feature branch
    svc.create_branch(str(git_repo), "my-feature")
    # Switch back
    current = svc.get_current_branch(str(git_repo))
    # Switch to original if we moved
    orig = "master" if _git(["branch", "--list", "master"], git_repo).stdout.strip() else "main"
    if current != orig:
        _git(["checkout", orig], git_repo)
    # Try to create again (no -f)
    result = svc.create_branch(str(git_repo), "my-feature")
    assert result.success is False
    assert result.action == "create_branch"


# ================================================================== #
# 14. Safe branch switching                                            #
# ================================================================== #

def test_checkout_branch_clean(svc: GitService, git_repo: Path):
    """checkout_branch works when the repo is clean."""
    # Create a second branch via git directly so we start on original
    _git(["branch", "target-branch"], git_repo)
    result = svc.checkout_branch(str(git_repo), "target-branch")
    assert result.success is True
    assert svc.get_current_branch(str(git_repo)) == "target-branch"


# ================================================================== #
# 15. Checkout blocked when unsafe (dirty repo)                        #
# ================================================================== #

def test_checkout_blocked_when_dirty(svc: GitService, git_repo: Path):
    """checkout_branch raises GitSecurityError when repo has uncommitted changes."""
    _git(["branch", "other-branch"], git_repo)
    # Make the repo dirty
    (git_repo / "readme.txt").write_text("dirty modification\n", encoding="utf-8")
    with pytest.raises(GitSecurityError, match="uncommitted changes"):
        svc.checkout_branch(str(git_repo), "other-branch")


# ================================================================== #
# 16. Stage valid file                                                 #
# ================================================================== #

def test_stage_valid_file(svc: GitService, git_repo: Path):
    """stage_files stages an existing file successfully."""
    (git_repo / "new.txt").write_text("content\n", encoding="utf-8")
    result = svc.stage_files(str(git_repo), ["new.txt"])
    assert result.success is True
    status = svc.get_status(str(git_repo))
    assert "new.txt" in status.staged_files


# ================================================================== #
# 17. Stage path traversal blocked                                     #
# ================================================================== #

def test_stage_path_traversal_blocked(svc: GitService, git_repo: Path):
    """Path traversal in stage_files raises GitSecurityError."""
    with pytest.raises(GitSecurityError):
        svc.stage_files(str(git_repo), ["../../../etc/passwd"])


def test_stage_empty_paths_rejected(svc: GitService, git_repo: Path):
    """Empty paths list returns a failure result."""
    result = svc.stage_files(str(git_repo), [])
    assert result.success is False


# ================================================================== #
# 18. Commit success                                                   #
# ================================================================== #

def test_commit_success(svc: GitService, git_repo: Path):
    """commit() creates a commit successfully with staged changes."""
    (git_repo / "commit_me.txt").write_text("data\n", encoding="utf-8")
    svc.stage_files(str(git_repo), ["commit_me.txt"])
    result = svc.commit(str(git_repo), "Add commit_me.txt")
    assert result.success is True
    assert result.action == "commit"
    # Verify commit exists
    log = _git(["log", "--oneline", "-1"], git_repo)
    assert "Add commit_me.txt" in log.stdout


# ================================================================== #
# 19. Empty commit message rejected                                    #
# ================================================================== #

def test_commit_empty_message_rejected(svc: GitService, git_repo: Path):
    """commit() raises GitSecurityError for empty message."""
    (git_repo / "file.txt").write_text("data\n", encoding="utf-8")
    svc.stage_files(str(git_repo), ["file.txt"])
    with pytest.raises(GitSecurityError, match="empty"):
        svc.commit(str(git_repo), "")


def test_commit_whitespace_message_rejected(svc: GitService, git_repo: Path):
    """commit() raises GitSecurityError for whitespace-only message."""
    (git_repo / "file2.txt").write_text("data\n", encoding="utf-8")
    svc.stage_files(str(git_repo), ["file2.txt"])
    with pytest.raises(GitSecurityError, match="empty"):
        svc.commit(str(git_repo), "   ")


# ================================================================== #
# 20. Commit with no staged changes rejected                           #
# ================================================================== #

def test_commit_no_staged_changes_rejected(svc: GitService, git_repo: Path):
    """commit() raises GitSecurityError when nothing is staged."""
    with pytest.raises(GitSecurityError, match="[Nn]othing staged"):
        svc.commit(str(git_repo), "This should fail")


# ================================================================== #
# 21. Arbitrary Git command execution is impossible                    #
# ================================================================== #

def test_no_arbitrary_git_command_api(svc: GitService):
    """GitService does not expose a generic run_git or execute_command method."""
    forbidden_names = {"run_git", "execute_command", "run_command", "run", "exec_git"}
    public_methods = {
        name for name in dir(svc)
        if not name.startswith("_") and callable(getattr(svc, name))
    }
    assert public_methods.isdisjoint(forbidden_names), (
        f"GitService exposes forbidden arbitrary-command methods: "
        f"{public_methods & forbidden_names}"
    )


# ================================================================== #
# 22. subprocess shell=True is never used in service.py               #
# ================================================================== #

def test_subprocess_shell_true_not_used():
    """service.py must never call subprocess.run with shell=True.

    Uses AST parsing to inspect only actual keyword argument values,
    not docstring text or comments that might legitimately document
    the constraint 'never use shell=True'.
    """
    import ast
    import backend.app.git.service as svc_module

    source = inspect.getsource(svc_module)
    tree = ast.parse(source)

    violations: list[str] = []
    for node in ast.walk(tree):
        # Look for subprocess.run(..., shell=True) calls
        if not isinstance(node, ast.Call):
            continue
        for kw in node.keywords:
            if kw.arg == "shell" and isinstance(kw.value, ast.Constant):
                if kw.value.value is True:
                    violations.append(f"shell=True found at line {node.lineno}")

    assert not violations, (
        "Found subprocess call(s) with shell=True in git/service.py — "
        f"security violation: {violations}"
    )


# ================================================================== #
# 23. Invalid repository path handling                                 #
# ================================================================== #

def test_invalid_path_nonexistent(svc: GitService):
    """A non-existent path raises GitNotRepositoryError."""
    with pytest.raises(GitNotRepositoryError):
        svc.get_status("/this/path/does/not/exist/12345")


def test_invalid_path_empty_string(svc: GitService):
    """An empty path raises GitSecurityError."""
    with pytest.raises(GitSecurityError):
        svc.get_current_branch("")


def test_is_git_repository_nonexistent_path(svc: GitService):
    """is_git_repository returns False for non-existent path (no exception)."""
    result = svc.is_git_repository("/nonexistent/path/xyz")
    assert result is False


# ================================================================== #
# 24. Git command timeout / error handling                             #
# ================================================================== #

def test_git_error_is_base_for_command_error():
    """GitCommandError is a subclass of GitError."""
    exc = GitCommandError("test", exit_code=1, stdout="out", stderr="err")
    assert isinstance(exc, GitError)
    assert exc.exit_code == 1
    assert exc.stdout == "out"
    assert exc.stderr == "err"


def test_get_diff_not_repo_raises(svc: GitService, non_git_dir: Path):
    """get_diff raises GitNotRepositoryError for a plain directory."""
    with pytest.raises(GitNotRepositoryError):
        svc.get_diff(str(non_git_dir))


def test_stage_files_not_repo_raises(svc: GitService, non_git_dir: Path):
    """stage_files raises GitNotRepositoryError for a plain directory."""
    with pytest.raises(GitNotRepositoryError):
        svc.stage_files(str(non_git_dir), ["file.txt"])


def test_commit_not_repo_raises(svc: GitService, non_git_dir: Path):
    """commit raises GitNotRepositoryError for a plain directory."""
    with pytest.raises(GitNotRepositoryError):
        svc.commit(str(non_git_dir), "Some message")
