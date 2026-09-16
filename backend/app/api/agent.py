"""Agent run status API endpoint."""

from fastapi import APIRouter, Request, Depends, BackgroundTasks, status, HTTPException
from datetime import datetime, timezone
import logging

from backend.app.schemas.agent_run import AgentRunResponse, StartAgentRequest
from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser
from backend.app.models.agent_run import AgentRunStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["Agent"])


def _get_agent_run_service(request: Request):
    """Retrieve AgentRunService from app state."""
    return request.app.state.agent_run_service


@router.get(
    "/status/{run_id}",
    response_model=AgentRunResponse,
    summary="Get agent run status",
    description="Return the current status of a specific agent run.",
    responses={404: {"description": "Agent run not found"}},
)
async def get_agent_run_status(
    run_id: str, 
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> AgentRunResponse:
    """Return an agent run by id."""
    service = _get_agent_run_service(request)
    owner_id = current_user.uid if current_user else None
    run = service.get_run(run_id, owner_id=owner_id)
    return AgentRunResponse.model_validate(run)

def execute_agent_background(run_id: str, request: Request, task_desc: str, repo_path: str):
    """Perform LangGraph execution synchronously isolating logic inside a BackgroundTask safely."""
    service = _get_agent_run_service(request)
    event_repo = getattr(request.app.state, "event_repository", None)
    
    # Wait, the repo is in-memory. If we get the run by id, we can mutate it or use service logic!
    # For InMemoryAgentRunRepository, mutability implies reference updating directly natively.
    try:
        run = service.get_run(run_id) # Using root privileges for the background loop natively updating
    except Exception as e:
        logger.error(f"Cannot find run {run_id} to execute block: {e}")
        return
        
    run.status = AgentRunStatus.RUNNING
    try:
        from backend.app.agents.graph import run_agent
        from backend.app.tools.registry import ToolRegistry
        from backend.app.tools.file_tools import ReadFileTool, WriteFileTool, EditFileTool, ListFilesTool, GetFileInfoTool
        from backend.app.services.analyzer.search import RipgrepSearchTool
        
        # Determine LLM to use
        from backend.app.agents.llm import MockLLMProvider
        llm = MockLLMProvider()
            
        analyzer = request.app.state.repository_analyzer
        executor = request.app.state.execution_service.executor # Resolves DockerExecutor natively
        
        tools = ToolRegistry()
        for t in [ReadFileTool(), WriteFileTool(), EditFileTool(), ListFilesTool(), GetFileInfoTool(), RipgrepSearchTool()]:
            tools.register(t)
            
        final_state = run_agent(
            task=task_desc,
            repo_path=repo_path,
            llm=llm,
            analyzer=analyzer,
            tools=tools,
            executor=executor,
            max_iterations=3,
            run_id=run.id,
            event_repo=event_repo
        )
        passed = final_state.get("evaluation_result", {}).get("passed", False)
        run.status = AgentRunStatus.COMPLETED if passed else AgentRunStatus.FAILED
        run.iteration_count = final_state.get("iteration_count", 0)
        run.final_status = final_state.get("final_status", "")
        run.error_summary = "\n".join([str(e) for e in final_state.get("errors", [])])
    except Exception as e:
        run.status = AgentRunStatus.FAILED
        run.error_summary = f"Execution failed entirely: {str(e)}"
    finally:
        run.completed_at = datetime.now(timezone.utc)

@router.post(
    "/run",
    response_model=AgentRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start an agent run",
    description="Start a new sandboxed agent evaluation loop attached asynchronously.",
)
async def start_agent_run(
    body: StartAgentRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> AgentRunResponse:
    """Implement Post /agent/run endpoints resolving Gap dependencies."""
    # Validate Task and Project implicitly verifying Ownership constraints reliably
    task_service = request.app.state.task_service
    project_service = request.app.state.project_service
    service = _get_agent_run_service(request)
    owner_id = current_user.uid if current_user else None
    
    # Reuses existing validation chains
    task = task_service.get_task(body.task_id, owner_id=owner_id)
    project = project_service.get_project(task.project_id, owner_id=owner_id)
    
    if not project.repository_path:
        raise HTTPException(status_code=400, detail="Parent project lacks a valid repository bounds.")
        
    run = service.create_run(task_id=body.task_id, owner_id=owner_id)
    
    background_tasks.add_task(execute_agent_background, run.id, request, task.description, project.repository_path)
    
    return AgentRunResponse.model_validate(run)
