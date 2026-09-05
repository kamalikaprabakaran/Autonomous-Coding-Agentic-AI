"""Manual execution test for Phase 4 LangGraph agent."""

from backend.app.agents.graph import run_agent
from backend.app.agents.llm import MockLLMProvider
from backend.app.services.analyzer.analyzer import RepositoryAnalyzer
from backend.app.tools.registry import ToolRegistry
from backend.app.tools.file_tools import ReadFileTool

def run_manual_scenario():
    print("--- Starting Phase 4 Manual Agent Workflow ---")
    
    # 1. Setup providers and registry
    llm = MockLLMProvider()
    analyzer = RepositoryAnalyzer()
    tools = ToolRegistry()
    tools.register(ReadFileTool())
    
    repo_path = "backend/tests/fixtures/fixture_project"
    task = "Add a function that calculates the average of a list of numbers."
    
    # 2. Run agent
    print(f"Task: {task}\n")
    print(f"Running LangGraph synchronously...")
    final_state = run_agent(task, repo_path, llm, analyzer, tools)
    
    # 3. Print Output outputs
    print("\n--- Final State Results ---")
    print(f"Node: {final_state['current_step']}")
    print("\n[PLAN]")
    print(final_state['plan'])
    
    print("\n[REPOSITORY Context]")
    print(f"Files Found: {final_state['repository_summary'].get('total_files')}")
    
    print("\n[CODER Proposal]")
    print(final_state['proposed_changes'])
    
    print("\n[MESSAGES Logs]")
    for msg in final_state['messages']:
        print(f" - {msg}")
    
    print("\nWorkflow perfectly completed with Deterministic Mocks!")

if __name__ == "__main__":
    run_manual_scenario()
