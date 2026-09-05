"""Tests for Agent nodes individually."""

from pathlib import Path
from backend.app.agents.nodes import planner_node, repository_explorer_node, coder_node
from backend.app.agents.llm import MockLLMProvider
from backend.app.services.analyzer.analyzer import RepositoryAnalyzer
from backend.app.tools.registry import ToolRegistry


FIXTURE_PATH = str(Path("backend/tests/fixtures/fixture_project").resolve())


def test_planner_node_receives_task():
    """Planner handles task string and outputs plan."""
    llm = MockLLMProvider()
    state = {"task": "Build an API"}
    
    out = planner_node(state, llm)
    assert out["current_step"] == "planner"
    assert "plan" in out
    assert "Inspect" in out["plan"]
    assert "Planner completed" in out["messages"][0]


def test_explorer_uses_analyzer():
    """Explorer successfully binds to RepositoryAnalyzer and extracts structure."""
    analyzer = RepositoryAnalyzer()
    state = {"repository_path": FIXTURE_PATH, "plan": "Do something"}
    
    out = repository_explorer_node(state, analyzer, ToolRegistry())
    
    assert out["current_step"] == "repository_explorer"
    assert out["repository_summary"]["repository_path"] == FIXTURE_PATH
    assert out["repository_summary"]["total_files"] > 0
    assert len(out["files_inspected"]) == 1
    assert "Analyzed " in out["messages"][0]


def test_coder_produces_proposal():
    """Coder fuses state strings and generates proposal."""
    llm = MockLLMProvider()
    state = {
        "task": "Add a function.",
        "plan": "1. Do something",
        "repository_summary": {"total_files": 2}
    }
    
    out = coder_node(state, llm)
    assert out["current_step"] == "coder"
    assert "Proposed changes:" in out["proposed_changes"]
    assert out["messages"][0] == "Coder proposed changes."
    
    # Ensures it did not try to write files. The proposal string is just a string.
    assert isinstance(out["proposed_changes"], str)
