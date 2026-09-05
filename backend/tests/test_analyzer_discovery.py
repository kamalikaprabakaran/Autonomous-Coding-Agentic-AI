"""Tests for file discovery."""

import pytest
from pathlib import Path

from backend.app.services.analyzer.discovery import list_files, build_file_tree, is_binary, is_ignored, resolve_safe_path, SecurityError

FIXTURE_PATH = Path("backend/tests/fixtures/fixture_project").resolve()

def test_resolve_safe_path_success():
    """Valid path within repo should resolve correctly."""
    target = FIXTURE_PATH / "app" / "main.py"
    resolved = resolve_safe_path(str(FIXTURE_PATH), str(target))
    assert resolved == target

def test_resolve_safe_path_escape_attempt():
    """Trying to escape repo bounds raises SecurityError."""
    target = FIXTURE_PATH / ".." / ".." / "windows" / "system32"
    with pytest.raises(SecurityError):
        resolve_safe_path(str(FIXTURE_PATH), str(target))

def test_is_ignored():
    """Ignored paths and extensions are correctly flagged."""
    assert is_ignored(Path("foo/.git")) is True
    assert is_ignored(Path("foo/node_modules")) is True
    assert is_ignored(Path("foo/app/__pycache__")) is True
    assert is_ignored(Path("test.pyc")) is True
    assert is_ignored(Path("main.py")) is False

def test_is_binary():
    """Binary files correctly identified."""
    assert is_binary(FIXTURE_PATH / "image.png") is True
    assert is_binary(FIXTURE_PATH / "app" / "main.py") is False

def test_list_files():
    """File listing correctly skips ignores and returns models."""
    files = list_files(str(FIXTURE_PATH))
    # Should include app/main.py, app/broken.py, app/__init__.py, tests/test_main.py, image.png, huge.txt
    paths = [f.path for f in files]
    
    assert "app/main.py" in paths
    assert "app/broken.py" in paths
    
    # Should NOT include ignored ones
    assert not any(".git" in p for p in paths)
    assert not any("node_modules" in p for p in paths)
    assert not any("__pycache__" in p for p in paths)
    assert not any("test.cpython" in p for p in paths)

def test_build_file_tree():
    """Directory tree is built correctly skipping ignores."""
    tree = build_file_tree(str(FIXTURE_PATH))
    
    assert tree.name == "fixture_project"
    assert tree.type == "directory"
    
    # Verify app dir is present
    app_node = next((n for n in tree.children if n.name == "app"), None)
    assert app_node is not None
    
    # Verify main.py inside app
    main_node = next((n for n in app_node.children if n.name == "main.py"), None)
    assert main_node is not None
    assert main_node.type == "file"
    assert main_node.path == "app/main.py"
    
    # Verify .git is excluded
    git_node = next((n for n in tree.children if n.name == ".git"), None)
    assert git_node is None
