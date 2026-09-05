"""Configuration constraints and limits for repository analyzer."""

import os

# Files larger than this will be skipped for parsing (1MB default).
MAX_FILE_SIZE = 1024 * 1024

# Files and directories ignored by default (prevent crawling virtualenvs, git, build artifacts).
IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
    ".idea",
    ".vscode",
}

# Pre-compiled or binary file extensions to immediately skip.
IGNORED_EXTS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".so",
    ".dll",
    ".exe",
    ".bin",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
}
