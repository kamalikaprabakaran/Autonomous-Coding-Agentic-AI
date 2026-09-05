"""Tests for LLM Abstraction and Mock."""

from backend.app.agents.llm import MockLLMProvider, BaseLLMProvider


def test_mock_llm_provider_determinisitic():
    """Verify MockLLM returns deterministic responses."""
    llm = MockLLMProvider()
    
    plan_out = llm.generate("Please plan this task.")
    assert "1. Inspect repository" in plan_out
    assert llm.call_count == 1
    
    code_out = llm.generate("Propose changes now.", system="You are the coder")
    assert "Proposed changes:" in code_out
    assert llm.call_count == 2
    
    default_out = llm.generate("Just say hello.")
    assert "Deterministic default" in default_out
    assert llm.call_count == 3


def test_mock_llm_system_prompting():
    """Verify MockLLM uses system prompt context."""
    llm = MockLLMProvider()
    
    out = llm.generate("Unknown task", system="You are the Planner.")
    assert "Inspect repository" in out
    
    out2 = llm.generate("Unknown task", system="You are the Coder.")
    assert "Proposed changes:" in out2
