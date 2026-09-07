"""Coding task API endpoints."""

from fastapi import APIRouter, Request, status, Depends

from backend.app.schemas.task import TaskCreate, TaskResponse
from backend.app.auth.dependencies import get_current_user
from backend.app.auth.models import AuthenticatedUser

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def _get_task_service(request: Request):
    """Retrieve TaskService from app state."""
    return request.app.state.task_service


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a coding task",
    description="Create a new coding task associated with an existing project.",
    responses={404: {"description": "Parent project not found"}},
)
async def create_task(
    body: TaskCreate, 
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> TaskResponse:
    """Create a new coding task."""
    service = _get_task_service(request)
    owner_id = current_user.uid if current_user else None
    task = service.create_task(
        project_id=body.project_id,
        description=body.description,
        owner_id=owner_id,
    )
    return TaskResponse.model_validate(task)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a coding task",
    description="Return a single coding task by its unique id.",
    responses={404: {"description": "Task not found"}},
)
async def get_task(
    task_id: str, 
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> TaskResponse:
    """Return a task by id."""
    service = _get_task_service(request)
    owner_id = current_user.uid if current_user else None
    task = service.get_task(task_id, owner_id=owner_id)
    return TaskResponse.model_validate(task)
