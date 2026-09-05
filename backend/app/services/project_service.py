"""Project service – business logic for project management."""

from backend.app.core.exceptions import NotFoundError
from backend.app.models.project import Project
from backend.app.repositories.project_repository import InMemoryProjectRepository


class ProjectService:
    """Orchestrates project operations between API and repository."""

    def __init__(self, repository: InMemoryProjectRepository) -> None:
        self._repo = repository

    def create_project(self, name: str, description: str = "",
                       repository_path: str | None = None,
                       repository_url: str | None = None) -> Project:
        """Create and persist a new project."""
        project = Project(
            name=name,
            description=description,
            repository_path=repository_path,
            repository_url=repository_url,
        )
        return self._repo.add(project)

    def get_project(self, project_id: str) -> Project:
        """Return a project by id or raise ``NotFoundError``."""
        project = self._repo.get(project_id)
        if project is None:
            raise NotFoundError("Project", project_id)
        return project

    def list_projects(self) -> list[Project]:
        """Return all projects."""
        return self._repo.list_all()
