"""Task service – business logic for coding task management."""

from backend.app.core.exceptions import NotFoundError
from backend.app.models.task import CodingTask
from backend.app.repositories.task_repository import InMemoryTaskRepository
from backend.app.services.project_service import ProjectService


class TaskService:
    """Orchestrates coding task operations between API and repository."""

    def __init__(self, repository: InMemoryTaskRepository,
                 project_service: ProjectService) -> None:
        self._repo = repository
        self._project_service = project_service

    def create_task(self, project_id: str, description: str) -> CodingTask:
        """Create a task after verifying the parent project exists.

        Raises ``NotFoundError`` if the project does not exist.
        """
        # Validate that the project exists (raises NotFoundError if not)
        self._project_service.get_project(project_id)

        task = CodingTask(project_id=project_id, description=description)
        return self._repo.add(task)

    def get_task(self, task_id: str) -> CodingTask:
        """Return a task by id or raise ``NotFoundError``."""
        task = self._repo.get(task_id)
        if task is None:
            raise NotFoundError("Task", task_id)
        return task
