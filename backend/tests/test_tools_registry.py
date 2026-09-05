"""Tests for Tool Registry and Base functionality."""

import pytest
from backend.app.models.tools import ToolResult
from pydantic import BaseModel

from backend.app.tools.base import BaseTool
from backend.app.tools.registry import ToolRegistry


class DummyInput(BaseModel):
    dummy_val: str


class DummyTool(BaseTool):
    name = "dummy_tool"
    description = "A dummy tool for testing."
    input_schema = DummyInput

    def execute(self, repo_path: str, args: dict) -> ToolResult:
        if args.get("dummy_val") == "fail":
            return ToolResult(success=False, error="Forced failure")
        return ToolResult(success=True, data={"result": "ok"})


def test_registry_register_and_get():
    """Registering and fetching tools works."""
    registry = ToolRegistry()
    tool = DummyTool()
    
    registry.register(tool)
    fetched = registry.get("dummy_tool")
    
    assert fetched is not None
    assert fetched.name == "dummy_tool"


def test_registry_get_unknown():
    """Fetching an unknown tool returns None."""
    registry = ToolRegistry()
    assert registry.get("unknown_tool") is None


def test_registry_list_tools():
    """List tools returns clean metadata with schemas."""
    registry = ToolRegistry()
    registry.register(DummyTool())
    
    tools = registry.list_tools()
    assert len(tools) == 1
    t = tools[0]
    
    assert t["name"] == "dummy_tool"
    assert "dummy_val" in t["input_schema"]["properties"]


def test_tool_execute():
    """A tool handles success and error cases cleanly using ToolResult."""
    tool = DummyTool()
    
    res1 = tool.execute("any/path", {"dummy_val": "ok"})
    assert res1.success is True
    assert res1.data["result"] == "ok"
    
    res2 = tool.execute("any/path", {"dummy_val": "fail"})
    assert res2.success is False
    assert res2.error == "Forced failure"
