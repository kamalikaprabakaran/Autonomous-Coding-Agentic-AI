"""Tests for File Tools."""

import pytest
from pathlib import Path
import shutil

from backend.app.tools.file_tools import (
    ListFilesTool, ReadFileTool, WriteFileTool, EditFileTool, GetFileInfoTool
)

FIXTURE_PATH = Path("backend/tests/fixtures/fixture_project").resolve()


@pytest.fixture
def temp_repo(tmp_path):
    """Creates an isolated temporary copy of the fixture repo for destructive tests."""
    repo_copy = tmp_path / "fixture_repo"
    shutil.copytree(FIXTURE_PATH, repo_copy)
    return str(repo_copy)


def test_list_files(temp_repo):
    tool = ListFilesTool()
    res = tool.execute(temp_repo, {})
    assert res.success is True
    
    paths = [f["path"] for f in res.data]
    assert "app/main.py" in paths
    assert ".git/config" not in paths


def test_read_file_success(temp_repo):
    tool = ReadFileTool()
    res = tool.execute(temp_repo, {"path": "app/main.py"})
    assert res.success is True
    assert "def standalone_function" in res.data["content"]


def test_read_file_missing(temp_repo):
    tool = ReadFileTool()
    res = tool.execute(temp_repo, {"path": "app/does_not_exist.py"})
    assert res.success is False
    assert "not found" in res.error.lower()


def test_read_file_binary(temp_repo):
    tool = ReadFileTool()
    res = tool.execute(temp_repo, {"path": "image.png"})
    assert res.success is False
    assert "binary" in res.error.lower()


def test_read_file_oversized(temp_repo):
    tool = ReadFileTool()
    res = tool.execute(temp_repo, {"path": "huge.py"})
    assert res.success is False
    assert "too large" in res.error.lower()


def test_read_file_path_traversal(temp_repo):
    tool = ReadFileTool()
    res = tool.execute(temp_repo, {"path": "../../../windows/system32/cmd.exe"})
    assert res.success is False
    assert "Security violation" in res.error


def test_read_file_absolute_path_outside(temp_repo):
    tool = ReadFileTool()
    res = tool.execute(temp_repo, {"path": "C:/Windows/System32/cmd.exe"})
    assert res.success is False
    assert "Security violation" in res.error


def test_write_file_new(temp_repo):
    tool = WriteFileTool()
    res = tool.execute(temp_repo, {"path": "app/new_file.txt", "content": "hello world"})
    assert res.success is True
    assert res.data["status"] == "created"
    assert (Path(temp_repo) / "app" / "new_file.txt").read_text() == "hello world"


def test_write_file_overwrite(temp_repo):
    tool = WriteFileTool()
    res = tool.execute(temp_repo, {"path": "app/main.py", "content": "completely replaced"})
    assert res.success is True
    assert res.data["status"] == "overwritten"
    assert (Path(temp_repo) / "app" / "main.py").read_text() == "completely replaced"


def test_write_file_traversal(temp_repo):
    tool = WriteFileTool()
    res = tool.execute(temp_repo, {"path": "../../secret.txt", "content": "hacked"})
    assert res.success is False
    assert "Security violation" in res.error


def test_edit_file_success(temp_repo):
    tool = EditFileTool()
    res = tool.execute(
        temp_repo, 
        {"path": "tests/test_main.py", "old_text": "assert True", "new_text": "assert False"}
    )
    assert res.success is True
    assert res.data["status"] == "edited"
    assert res.data["replacements"] == 1
    
    content = (Path(temp_repo) / "tests/test_main.py").read_text()
    assert "assert False" in content
    assert "assert True" not in content


def test_edit_file_not_found(temp_repo):
    tool = EditFileTool()
    res = tool.execute(
        temp_repo, 
        {"path": "tests/test_main.py", "old_text": "does not exist in file", "new_text": "new"}
    )
    assert res.success is False
    assert "Target text not found" in res.error


def test_edit_file_ambiguous(temp_repo):
    # Setup multiple instances
    target = Path(temp_repo) / "app/ambiguous.txt"
    target.write_text("duplicate duplicate duplicate")
    
    tool = EditFileTool()
    res = tool.execute(
        temp_repo, 
        {"path": "app/ambiguous.txt", "old_text": "duplicate", "new_text": "single"}
    )
    assert res.success is False
    assert "Ambiguous replacement" in res.error


def test_edit_file_missing_file(temp_repo):
    tool = EditFileTool()
    res = tool.execute(temp_repo, {"path": "missing.txt", "old_text": "old", "new_text": "new"})
    assert res.success is False
    assert "File not found" in res.error


def test_get_file_info_file(temp_repo):
    tool = GetFileInfoTool()
    res = tool.execute(temp_repo, {"path": "app/main.py"})
    assert res.success is True
    d = res.data
    assert d["name"] == "main.py"
    assert d["is_directory"] is False
    assert d["extension"] == ".py"


def test_get_file_info_directory(temp_repo):
    tool = GetFileInfoTool()
    res = tool.execute(temp_repo, {"path": "app"})
    assert res.success is True
    d = res.data
    assert d["name"] == "app"
    assert d["is_directory"] is True
    assert d["size"] == 0
    assert d["extension"] == ""


def test_get_file_info_missing(temp_repo):
    tool = GetFileInfoTool()
    res = tool.execute(temp_repo, {"path": "doesnotexist.py"})
    assert res.success is False
    assert "not found" in res.error.lower()


def test_mixed_separator_attack(temp_repo):
    tool = ReadFileTool()
    # Windows mixed separators that could canonicalize improperly if poorly coded
    res = tool.execute(temp_repo, {"path": "..\\..\\windows/system32/cmd.exe"})
    assert res.success is False
    assert "Security violation" in res.error
