"""Project API endpoints."""

from fastapi import APIRouter, Request, status

from backend.app.schemas.project import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])


def _get_project_service(request: Request):
    """Retrieve ProjectService from app state."""
    return request.app.state.project_service


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
    description="Create a new software project to be managed by the agent.",
)
async def create_project(body: ProjectCreate, request: Request) -> ProjectResponse:
    """Create a new project."""
    service = _get_project_service(request)
    project = service.create_project(
        name=body.name,
        description=body.description,
        repository_path=body.repository_path,
        repository_url=body.repository_url,
    )
    return ProjectResponse.model_validate(project)


@router.get(
    "",
    response_model=list[ProjectResponse],
    summary="List all projects",
    description="Return every project currently stored.",
)
async def list_projects(request: Request) -> list[ProjectResponse]:
    """Return all projects."""
    service = _get_project_service(request)
    projects = service.list_projects()
    return [ProjectResponse.model_validate(p) for p in projects]


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get a project",
    description="Return a single project by its unique id.",
    responses={404: {"description": "Project not found"}},
)
async def get_project(project_id: str, request: Request) -> ProjectResponse:
    """Return a project by id."""
    service = _get_project_service(request)
    project = service.get_project(project_id)
    return ProjectResponse.model_validate(project)


@router.get(
    "/{project_id}/analysis",
    summary="Analyze a project repository",
    description="Analyze the project's repository and return structural and code insights.",
    responses={404: {"description": "Project not found or invalid repository path"}},
)
async def analyze_project_repository(project_id: str, request: Request):
    """Run full repository analysis on a project."""
    service = _get_project_service(request)
    project = service.get_project(project_id)
    
    if not project.repository_path:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project lacks a repository path")
        
    try:
        analyzer = request.app.state.repository_analyzer
        analysis = analyzer.analyze_repository(project.repository_path)
        return analysis.model_dump()
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Failed to access repository: {str(e)}")
