"""LangGraph Nodes for Autonomous Coding Agent."""

from backend.app.models.agent_state import AgentState
from backend.app.agents.llm import BaseLLMProvider
from backend.app.services.analyzer.analyzer import RepositoryAnalyzer
from backend.app.tools.registry import ToolRegistry


def planner_node(state: AgentState, llm: BaseLLMProvider) -> dict:
    """Planner node: breaks down the coding task into steps."""
    prompt = f"Create a structured plan for the following task:\n{state.get('task', '')}"
    plan = llm.generate(prompt, system="You are the Planner.")
    
    return {
        "current_step": "planner",
        "plan": plan,
        "messages": ["Planner completed."],
        "errors": []
    }


def repository_explorer_node(
    state: AgentState, 
    analyzer: RepositoryAnalyzer, 
    tools: ToolRegistry = None
) -> dict:
    """Explorer node: uses Repository Analyzer to gather context."""
    repo_path = state.get("repository_path", "")
    
    try:
        # Use Phase 2 intelligence
        summary = analyzer.analyze_repository(repo_path)
        
        # Ensure it works with the mock/test architecture safely
        files_found = summary.analyzed_files
        
        return {
            "current_step": "repository_explorer",
            "repository_summary": summary.model_dump(),
            "files_inspected": [summary.repository_path], # High level tracked
            "messages": [f"Explorer finished. Analyzed {files_found} files."],
            "errors": []
        }
    except Exception as e:
        return {
            "current_step": "repository_explorer",
            "messages": ["Explorer failed."],
            "errors": [str(e)]
        }


def coder_node(state: AgentState, llm: BaseLLMProvider) -> dict:
    """Coder node: proposes a concrete coding action based on plan and intelligence."""
    
    prompt = (
        f"Task: {state.get('task', '')}\n"
        f"Plan: {state.get('plan', '')}\n"
        f"Repo Context: {state.get('repository_summary', {})}\n"
        f"Propose the concrete file changes."
    )
    
    proposal = llm.generate(prompt, system="You are the Coder.")
    
    return {
        "current_step": "coder",
        "proposed_changes": proposal,
        "messages": ["Coder proposed changes."],
        "errors": []
    }
