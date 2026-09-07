"""Project service – business logic for project management."""

from typing import Optional
from backend.app.core.exceptions import NotFoundError
from backend.app.models.project import Project
from backend.app.repositories.base import ProjectRepositoryProtocol


class ProjectService:
    """Orchestrates project operations between API and repository."""

    def __init__(self, repository: ProjectRepositoryProtocol) -> None:
        self._repo = repository

    def create_project(self, name: str, description: str = "",
                       repository_path: Optional[str] = None,
                       repository_url: Optional[str] = None,
                       owner_id: Optional[str] = None) -> Project:
        """Create and persist a new project."""
        project = Project(
            name=name,
            description=description,
            repository_path=repository_path,
            repository_url=repository_url,
            owner_id=owner_id,
        )
        return self._repo.add(project)

    def get_project(self, project_id: str, owner_id: Optional[str] = None) -> Project:
        """Return a project by id.
        
        If owner_id is provided, enforces that the project belongs to that owner.
        """
        project = self._repo.get(project_id)
        if project is None:
            raise NotFoundError("Project", project_id)
            
        if owner_id and project.owner_id != owner_id:
            # We return NotFound rather than Forbidden to avoid leaking existence stats
            raise NotFoundError("Project", project_id)
            
        return project

    def list_projects(self, owner_id: Optional[str] = None) -> list[Project]:
        """Return all projects, optionally filtered by owner."""
        if owner_id:
            return self._repo.list_by_owner(owner_id)
        return self._repo.list_all()
