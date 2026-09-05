"""LangGraph orchestration logic."""

from langgraph.graph import StateGraph, START, END

from backend.app.models.agent_state import AgentState
from backend.app.agents.llm import BaseLLMProvider
from backend.app.services.analyzer.analyzer import RepositoryAnalyzer
from backend.app.tools.registry import ToolRegistry
from backend.app.agents.nodes import planner_node, repository_explorer_node, coder_node


def build_agent_graph(
    llm: BaseLLMProvider, 
    analyzer: RepositoryAnalyzer, 
    tools: ToolRegistry = None
):
    """Build and compile the LangGraph for the agent."""
    graph = StateGraph(AgentState)
    
    # State mutation wrappers injecting dependencies
    def run_planner(state: AgentState):
        return planner_node(state, llm)
        
    def run_explorer(state: AgentState):
        return repository_explorer_node(state, analyzer, tools)
        
    def run_coder(state: AgentState):
        return coder_node(state, llm)
    
    # Bind nodes
    graph.add_node("planner", run_planner)
    graph.add_node("explorer", run_explorer)
    graph.add_node("coder", run_coder)
    
    # Simple linear control flow
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "explorer")
    graph.add_edge("explorer", "coder")
    graph.add_edge("coder", END)
    
    return graph.compile()


def run_agent(
    task: str, 
    repo_path: str, 
    llm: BaseLLMProvider, 
    analyzer: RepositoryAnalyzer, 
    tools: ToolRegistry = None
) -> AgentState:
    """Execute the agent graph synchronously.
    
    Returns the final state built by LangGraph.
    """
    initial_state = {
        "task": task,
        "repository_path": repo_path,
        "current_step": "init",
        "plan": None,
        "repository_summary": {},
        "files_inspected": [],
        "proposed_changes": None,
        "messages": ["Graph initialized"],
        "errors": []
    }
    
    compiled_graph = build_agent_graph(llm, analyzer, tools)
    
    final_state = compiled_graph.invoke(initial_state)
    return final_state
