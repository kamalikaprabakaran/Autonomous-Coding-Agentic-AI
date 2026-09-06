"""Agent State definition for LangGraph workflow."""

import operator
from typing import TypedDict, Annotated, Optional


class AgentState(TypedDict):
    """The graph state for the autonomous coding agent."""
    
    # Global Task Inputs
    task: str
    repository_path: str
    
    # Workflow State
    current_step: str
    iteration_count: int
    max_iterations: int
    final_status: Optional[str]
    
    # Planner Module
    plan: Optional[str]
    
    # Repository Explorer Module
    repository_summary: dict
    files_inspected: Annotated[list[str], operator.add]
    
    # Coder Module
    proposed_changes: Optional[str]
    
    # Execution & Evaluation Loop
    execution_result: Optional[dict]
    evaluation_result: Optional[dict]
    failure_feedback: Optional[dict]
    correction_history: Annotated[list[dict], operator.add]
    
    # Communication / Error Handling
    messages: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]
