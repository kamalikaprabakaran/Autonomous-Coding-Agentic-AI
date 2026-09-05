"""Tests for LangGraph orchestration flow end-to-end."""

import pytest
from pathlib import Path

from backend.app.agents.graph import build_agent_graph, run_agent
from backend.app.agents.llm import MockLLMProvider
from backend.app.services.analyzer.analyzer import RepositoryAnalyzer
from backend.app.tools.registry import ToolRegistry
from backend.app.tools.file_tools import ReadFileTool

FIXTURE_PATH = str(Path("backend/tests/fixtures/fixture_project").resolve())


def test_graph_builds_successfully():
    """The StateGraph successfully links logic hooks on build."""
    llm = MockLLMProvider()
    analyzer = RepositoryAnalyzer()
    tools = ToolRegistry()
    
    compiled = build_agent_graph(llm, analyzer, tools)
    assert compiled is not None


def test_graph_executes_successfully_with_mock():
    """Runs a full task through the agent logic deterministic loop."""
    llm = MockLLMProvider()
    analyzer = RepositoryAnalyzer()
    tools = ToolRegistry()
    tools.register(ReadFileTool())
    
    task_desc = "Add a function that calculates the average of a list of numbers."
    final_state = run_agent(task_desc, FIXTURE_PATH, llm, analyzer, tools)
    
    # Asserting State Lifecycle flowed thoroughly
    assert final_state["current_step"] == "coder"
    assert final_state["task"] == task_desc
    assert final_state["repository_path"] == FIXTURE_PATH
    
    # Assert Planner fired
    assert "1. Inspect repository" in final_state["plan"]
    
    # Assert Explorer fired
    assert "repository_summary" in final_state
    assert final_state["repository_summary"]["total_files"] > 1
    
    # Assert Coder fired
    assert "Proposed changes:" in final_state["proposed_changes"]
    
    # Assert Reducer mechanics inside LangGraph stacked messages correctly
    assert len(final_state["messages"]) == 4 # Init, Planner, Explorer, Coder


def test_graph_handles_node_failure():
    """If explorer fails (e.g. invalid repo), the graph still produces a state (though corrupted/failed) safely."""
    llm = MockLLMProvider()
    analyzer = RepositoryAnalyzer()
    
    final_state = run_agent("Fix everything", "/does/not/exist/999", llm, analyzer)
    
    assert final_state["errors"] != []
    
    # Coder will still fire because we don't have conditional edges to END on error yet,
    # but the proposal will contain the error context gracefully (or lack thereof).
    assert "proposed_changes" in final_state
