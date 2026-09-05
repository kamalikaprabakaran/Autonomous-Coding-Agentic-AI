"""Tests for AgentState logic."""

from backend.app.models.agent_state import AgentState


def test_agent_state_initialization():
    """Verify that we can initialize the typed dict cleanly."""
    state: AgentState = {
        "task": "Test task",
        "repository_path": "/mock/path",
        "current_step": "init",
        "plan": None,
        "repository_summary": {},
        "files_inspected": [],
        "proposed_changes": None,
        "messages": [],
        "errors": []
    }
    
    assert state["task"] == "Test task"
    assert state["current_step"] == "init"
    assert len(state["files_inspected"]) == 0


def test_state_updates():
    """Verify state updating mechanics conceptually used in graphs."""
    state: AgentState = {
        "task": "Test task",
        "repository_path": "/mock/path",
        "current_step": "init",
        "plan": None,
        "repository_summary": {},
        "files_inspected": [],
        "proposed_changes": None,
        "messages": ["Start"],
        "errors": []
    }
    
    # Simulate a node updating state
    update = {
        "current_step": "planner",
        "plan": "1. Do something",
        "messages": ["Planner done"]
    }
    
    state.update(update) # In raw python, update() replaces. In Langgraph, operator.add appends list.
    assert state["plan"] == "1. Do something"
    assert state["current_step"] == "planner"
