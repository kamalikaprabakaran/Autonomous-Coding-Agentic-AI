"""LangGraph orchestration logic."""

import time
from langgraph.graph import StateGraph, START, END

from backend.app.models.agent_state import AgentState
from backend.app.models.event import AgentEvent, AgentEventType
from backend.app.repositories.base import EventRepositoryProtocol
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
    executor: DockerExecutor = None,
    event_repo: EventRepositoryProtocol = None,
    run_id: str = None
):
    """Build and compile the LangGraph for the agent."""
    graph = StateGraph(AgentState)
    
    def _emit_event(event_type: str, iteration=None, meta=None, status=None, error=None, duration=None):
        if event_repo and run_id:
            event = AgentEvent(
                run_id=run_id,
                event_type=event_type,
                iteration=iteration,
                metadata=meta or {},
                status=status,
                error=error,
                duration_seconds=duration
            )
            try:
                event_repo.add(event)
            except Exception:
                pass
                
    def _wrap_node(func, start_type, end_type):
        def wrapper(state: AgentState):
            iteration = state.get("iteration_count", 0)
            _emit_event(start_type, iteration=iteration)
            start_t = time.monotonic()
            try:
                result = func(state)
                dur = time.monotonic() - start_t
                _emit_event(end_type, iteration=iteration, duration=dur, status="success")
                return result
            except Exception as e:
                dur = time.monotonic() - start_t
                _emit_event(end_type, iteration=iteration, duration=dur, status="failed", error=str(e))
                raise
        return wrapper
        
    def run_executor(state: AgentState):
        iteration = state.get("iteration_count", 0)
        _emit_event(AgentEventType.EXECUTION_STARTED, iteration=iteration)
        start_t = time.monotonic()
        try:
            result = executor_node(state, executor)
            dur = time.monotonic() - start_t
            exec_res = result.get("execution_result", {})
            st = "success" if exec_res.get("success") else "failed"
            err = exec_res.get("error") or exec_res.get("stderr")
            _emit_event(AgentEventType.EXECUTION_COMPLETED, iteration=iteration, duration=dur, status=st, error=err)
            return result
        except Exception as e:
            dur = time.monotonic() - start_t
            _emit_event(AgentEventType.EXECUTION_COMPLETED, iteration=iteration, duration=dur, status="failed", error=str(e))
            raise
            
    # Bind nodes wrapped
    graph.add_node("planner", _wrap_node(lambda st: planner_node(st, llm), AgentEventType.PLANNER_STARTED, AgentEventType.PLANNER_COMPLETED))
    graph.add_node("explorer", _wrap_node(lambda st: repository_explorer_node(st, analyzer, tools), AgentEventType.EXPLORER_STARTED, AgentEventType.EXPLORER_COMPLETED))
    
    # Coder includes correction if iteration > 0
    def run_coder(state: AgentState):
        iteration = state.get("iteration_count", 0)
        t_start = AgentEventType.CORRECTION_STARTED if iteration > 0 else AgentEventType.CODER_STARTED
        t_end = AgentEventType.CORRECTION_COMPLETED if iteration > 0 else AgentEventType.CODER_COMPLETED
        return _wrap_node(lambda st: coder_node(st, llm), t_start, t_end)(state)
        
    graph.add_node("coder", run_coder)
    graph.add_node("executor", run_executor)
    graph.add_node("evaluator", _wrap_node(lambda st: evaluator_node(st), AgentEventType.EVALUATION_STARTED, AgentEventType.EVALUATION_COMPLETED))
    
    def should_continue(state: AgentState) -> str:
        passed = state.get("evaluation_result", {}).get("passed", False)
        if passed:
            return "end"
            
        iterations = state.get("iteration_count", 0)
        max_iters = state.get("max_iterations", 3)
        if iterations >= max_iters:
            return "end"
            
        return "coder"
    
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
    max_iterations: int = 3,
    run_id: str = None,
    event_repo: EventRepositoryProtocol = None
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
    
    compiled_graph = build_agent_graph(llm, analyzer, tools, executor, event_repo, run_id)
    
    if event_repo and run_id:
        try:
            event_repo.add(AgentEvent(run_id=run_id, event_type=AgentEventType.RUN_STARTED))
        except Exception:
            pass
            
    start_t = time.monotonic()
    
    try:
        final_state = compiled_graph.invoke(initial_state)
        # Set final categorical state correctly mapped
        passed = final_state.get("evaluation_result", {}).get("passed", False)
        final_state["final_status"] = "success" if passed else "failed"
        
        if event_repo and run_id:
            dur = time.monotonic() - start_t
            end_type = AgentEventType.RUN_COMPLETED if passed else AgentEventType.RUN_FAILED
            try:
                event_repo.add(AgentEvent(run_id=run_id, event_type=end_type, duration_seconds=dur, status=final_state["final_status"]))
            except Exception:
                pass
                
        return final_state
        
    except Exception as e:
        if event_repo and run_id:
            dur = time.monotonic() - start_t
            try:
                event_repo.add(AgentEvent(run_id=run_id, event_type=AgentEventType.RUN_FAILED, duration_seconds=dur, status="failed", error=str(e)))
            except Exception:
                pass
        raise
