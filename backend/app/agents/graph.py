"""LangGraph orchestration logic."""

from langgraph.graph import StateGraph, START, END

from backend.app.models.agent_state import AgentState
from backend.app.agents.llm import BaseLLMProvider
from backend.app.services.analyzer.analyzer import RepositoryAnalyzer
from backend.app.tools.registry import ToolRegistry
from backend.app.execution.docker_executor import DockerExecutor
from backend.app.agents.nodes import (
    planner_node, 
    repository_explorer_node, 
    coder_node, 
    executor_node, 
    evaluator_node
)


def build_agent_graph(
    llm: BaseLLMProvider, 
    analyzer: RepositoryAnalyzer, 
    tools: ToolRegistry = None,
    executor: DockerExecutor = None
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
        
    def run_executor(state: AgentState):
        return executor_node(state, executor)
        
    def run_evaluator(state: AgentState):
        return evaluator_node(state)
        
    def should_continue(state: AgentState) -> str:
        passed = state.get("evaluation_result", {}).get("passed", False)
        if passed:
            return "end"
            
        iterations = state.get("iteration_count", 0)
        max_iters = state.get("max_iterations", 3)
        if iterations >= max_iters:
            return "end"
            
        return "coder"
    
    # Bind nodes
    graph.add_node("planner", run_planner)
    graph.add_node("explorer", run_explorer)
    graph.add_node("coder", run_coder)
    graph.add_node("executor", run_executor)
    graph.add_node("evaluator", run_evaluator)
    
    # Control flow
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "explorer")
    graph.add_edge("explorer", "coder")
    graph.add_edge("coder", "executor")
    graph.add_edge("executor", "evaluator")
    
    graph.add_conditional_edges(
        "evaluator",
        should_continue,
        {
            "end": END,
            "coder": "coder"
        }
    )
    
    return graph.compile()


def run_agent(
    task: str, 
    repo_path: str, 
    llm: BaseLLMProvider, 
    analyzer: RepositoryAnalyzer, 
    tools: ToolRegistry = None,
    executor: DockerExecutor = None,
    max_iterations: int = 3
) -> dict:
    """Execute the agent graph synchronously.
    
    Returns the final state built by LangGraph.
    """
    initial_state = {
        "task": task,
        "repository_path": repo_path,
        "current_step": "init",
        "iteration_count": 0,
        "max_iterations": max_iterations,
        "final_status": None,
        "plan": None,
        "repository_summary": {},
        "files_inspected": [],
        "proposed_changes": None,
        "execution_result": None,
        "evaluation_result": None,
        "failure_feedback": None,
        "correction_history": [],
        "messages": ["Graph initialized"],
        "errors": []
    }
    
    compiled_graph = build_agent_graph(llm, analyzer, tools, executor)
    
    final_state = compiled_graph.invoke(initial_state)
    
    # Set final categorical state correctly mapped
    passed = final_state.get("evaluation_result", {}).get("passed", False)
    final_state["final_status"] = "success" if passed else "failed"
    
    return final_state
