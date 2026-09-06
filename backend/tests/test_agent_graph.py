"""Tests for LangGraph orchestration flow end-to-end."""

import pytest
from pathlib import Path

from backend.app.agents.graph import build_agent_graph, run_agent
from backend.app.agents.llm import MockLLMProvider
from backend.app.services.analyzer.analyzer import RepositoryAnalyzer
from backend.app.tools.registry import ToolRegistry
from backend.app.tools.file_tools import ReadFileTool

FIXTURE_PATH = str(Path("backend/tests/fixtures/fixture_project").resolve())


def test_graph_executes_successfully_with_mock():
    """Runs a full task through the agent logic deterministic loop and hits end first try."""
    llm = MockLLMProvider()
    analyzer = RepositoryAnalyzer()
    tools = ToolRegistry()
    tools.register(ReadFileTool())
    
    task_desc = "Add a function that calculates the average of a list of numbers."
    final_state = run_agent(task_desc, FIXTURE_PATH, llm, analyzer, tools)
    
    assert final_state["final_status"] == "success"
    assert final_state["current_step"] == "evaluator"
    assert final_state["iteration_count"] == 1
    
    # Assert nodes fired
    assert "1. Inspect repository" in final_state["plan"]
    assert "repository_summary" in final_state
    
    # Check messages array mapped everything
    msgs = final_state["messages"]
    assert len(msgs) == 6 # Init, Planner, Explorer, Coder, Executor, Evaluator


def test_graph_executes_fails_then_corrects():
    """Ensures MockLLM triggering failure conditions redirects correctly."""
    llm = MockLLMProvider()
    analyzer = RepositoryAnalyzer()
    
    # "bad" implicitly makes MockExecutor fail based on nodes.py mock mapping
    task_desc = "Implement a bad test" 
    
    # We map the proposal to output fail, then next attempt will succeed.
    # We need a custom mock or rely on llm.py checking prompt context!
    # Our llm.py injects correctness if "failed" or "failure" is in prompt!
    class FailingMockLLM(MockLLMProvider):
        def generate(self, prompt: str, system: str = "") -> str:
            if "Previous attempt failed" in prompt:
                return "Corrected proposed changes:\n- Passed tests successfully."
            if "coder" in system.lower():
                return "bad proposal"
            return super().generate(prompt, system)
            
    final_state = run_agent(task_desc, FIXTURE_PATH, FailingMockLLM(), analyzer)
    
    # Should correct on attempt 2
    assert final_state["final_status"] == "success"
    assert final_state["iteration_count"] == 2
    
    # The history must track the failed attempt completely
    history = final_state["correction_history"]
    assert len(history) == 2
    assert history[0]["evaluation_result"]["passed"] is False
    assert history[1]["evaluation_result"]["passed"] is True
    assert history[0]["failure_feedback"]["exit_code"] != 0


def test_graph_exhausts_retries():
    """Validates the max_iterations loop terminates safely."""
    analyzer = RepositoryAnalyzer()
    
    class StubbornFailingLLM(MockLLMProvider):
        def generate(self, prompt: str, system: str = "") -> str:
            if "coder" in system.lower():
                return "bad proposal"
            return super().generate(prompt, system)
            
    # max_iterations default is 3
    final_state = run_agent("Do impossible", FIXTURE_PATH, StubbornFailingLLM(), analyzer)
    
    assert final_state["final_status"] == "failed"
    assert final_state["iteration_count"] == 3
    assert len(final_state["correction_history"]) == 3


def test_graph_executor_failure_handled():
    """If execution crashes entirely, loop handles it gracefully."""
    analyzer = RepositoryAnalyzer()
    
    class CrashLLM(MockLLMProvider):
        def generate(self, prompt: str, system: str = "") -> str:
            if "coder" in system.lower():
                # We do not mock "bad proposal" here. Let's pass a DockerExecutor mockup that strictly raises Exception
                return "Normal proposal"
            return super().generate(prompt, system)
            
    class ThrowingExecutor:
        def execute(self, req):
            raise Exception("Docker execution completely crashed")
            
    final_state = run_agent("Do something", FIXTURE_PATH, CrashLLM(), analyzer, executor=ThrowingExecutor())
    
    # Assuming the evaluator traps exception and keeps failing it until iteration runs out OR corrections run
    # For a crash, success is False. Correction continues.
    assert final_state["final_status"] == "success" or final_state["final_status"] == "failed"
    assert "Exception('Docker execution completely crashed')" in str(final_state["errors"]) or "Docker execution completely crashed" in str(final_state["errors"])
