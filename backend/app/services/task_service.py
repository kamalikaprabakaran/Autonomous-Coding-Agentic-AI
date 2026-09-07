"""Task service – business logic for coding task management."""

from typing import Optional
from backend.app.core.exceptions import NotFoundError
from backend.app.models.task import CodingTask
from backend.app.repositories.base import TaskRepositoryProtocol
from backend.app.services.project_service import ProjectService


class TaskService:
    """Orchestrates coding task operations between API and repository."""

    def __init__(self, repository: TaskRepositoryProtocol,
                 project_service: ProjectService) -> None:
        self._repo = repository
        self._project_service = project_service

    def create_task(self, project_id: str, description: str, owner_id: Optional[str] = None) -> CodingTask:
        """Create a task after verifying the parent project exists.

        Raises ``NotFoundError`` if the project does not exist.
        """
        # Validate that the project exists (and belongs to owner if provided)
        self._project_service.get_project(project_id, owner_id=owner_id)

        task = CodingTask(project_id=project_id, description=description, owner_id=owner_id)
        return self._repo.add(task)

    def get_task(self, task_id: str, owner_id: Optional[str] = None) -> CodingTask:
        """Return a task by id or raise ``NotFoundError``."""
        task = self._repo.get(task_id)
        if task is None:
            raise NotFoundError("Task", task_id)
            
        if owner_id and task.owner_id != owner_id:
            raise NotFoundError("Task", task_id)
            
        return task
