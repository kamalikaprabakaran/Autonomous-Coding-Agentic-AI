"""Agent run status API endpoint."""

from fastapi import APIRouter, Request, Depends

from backend.app.schemas.agent_run import AgentRunResponse
from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser

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
