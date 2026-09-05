"""File discovery and repository bounds protection."""

import os
from pathlib import Path
from typing import Optional

from backend.app.models.analyzer import DirectoryNode, FileInfo
from backend.app.services.analyzer.config import IGNORED_DIRS, IGNORED_EXTS, MAX_FILE_SIZE


class SecurityError(Exception):
    """Raised when an attempt is made to access outside the repository bounds."""
    pass


def resolve_safe_path(repo_path: str, target_path: str) -> Path:
    """Resolve a target path securely within the repository path bounds.

    Raises SecurityError if the target path attempts to escape the repository.
    """
    try:
        base = Path(repo_path).resolve(strict=True)
        # We don't use strict=True for target because it might not exist yet
        # in some use cases, but for discovery it usually exists.
        target = Path(target_path).resolve()
        
        # Verify the target is relative to the base repository path
        if not target.is_relative_to(base):
            raise SecurityError(f"Path boundary escape detected: {target_path}")
        
        return target
    except ValueError as e:
        raise SecurityError(f"Invalid path format: {target_path}") from e
    except FileNotFoundError:
        # If repo_path itself does not exist
        raise


def is_ignored(path: Path) -> bool:
    """Return True if the path is ignored by directory or extension rules."""
    if path.name in IGNORED_DIRS:
        return True
    if path.suffix.lower() in IGNORED_EXTS:
        return True
    return False


def is_binary(path: Path) -> bool:
    """Heuristic to detect if a file is binary by searching for null bytes."""
    try:
        with open(path, "rb") as check_file:
            chunk = check_file.read(1024)
            if b"\x00" in chunk:
                return True
            return False
    except OSError:
        return True


def list_files(repo_path: str) -> list[FileInfo]:
    """Recursively list all non-ignored files in the repository.

    Raises SecurityError if repo_path goes outside workspace bounds (conceptual),
    but primarily ensures we don't follow symlinks out.
    """
    base = Path(repo_path).resolve(strict=True)
    files = []
    
    for root, dirs, filenames in os.walk(base, followlinks=False):
        current_root = Path(root)
        
        # Filter ignored directories in-place so os.walk skips them
        dirs[:] = [d for d in dirs if not is_ignored(current_root / d)]
        
        for name in filenames:
            file_path = current_root / name
            if is_ignored(file_path):
                continue
            
            try:
                # Ensure the file doesn't symlink outside (os.walk doesn't follow link dirs,
                # but individual files could be symlinks)
                resolved_file = resolve_safe_path(str(base), str(file_path))
                
                size = resolved_file.stat().st_size
                info = FileInfo(
                    path=str(resolved_file.relative_to(base).as_posix()),
                    name=name,
                    extension=resolved_file.suffix.lower(),
                    size=size,
                    type="file"
                )
                files.append(info)
            except (SecurityError, FileNotFoundError, OSError):
                # Skip inaccessible or escaping files
                continue
                
    return files


def build_file_tree(repo_path: str) -> DirectoryNode:
    """Build a nested DirectoryNode tree for the repository."""
    base = Path(repo_path).resolve(strict=True)
    
    def _build_node(current_path: Path) -> Optional[DirectoryNode]:
        if is_ignored(current_path):
            return None
            
        if current_path.is_file():
            return DirectoryNode(
                name=current_path.name,
                type="file",
                path=str(current_path.relative_to(base).as_posix())
            )
            
        if current_path.is_dir():
            children = []
            try:
                # Sort for deterministic testing
                entries = sorted(list(current_path.iterdir()), key=lambda p: (p.is_file(), p.name))
                for entry in entries:
                    if not entry.is_symlink():
                        child_node = _build_node(entry)
                        if child_node:
                            children.append(child_node)
            except OSError:
                pass
                
            return DirectoryNode(
                name=current_path.name,
                type="directory",
                children=children
            )
        return None

    tree = _build_node(base)
    # If the base itself was ignored (unlikely) or inaccessible, fallback to empty
    if not tree:
        return DirectoryNode(name=base.name, type="directory", children=[])
    return tree
