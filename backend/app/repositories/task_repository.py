"""In-memory coding task repository."""

from typing import Optional

from backend.app.models.task import CodingTask


class InMemoryTaskRepository:
    """Store coding tasks in a plain dictionary.

    Designed to be replaced by a Firebase-backed implementation in a
    future phase without changing the service or API layers.
    """

    def __init__(self) -> None:
        self._store: dict[str, CodingTask] = {}

    def add(self, task: CodingTask) -> CodingTask:
        """Persist a task and return it."""
        self._store[task.id] = task
        return task

    def get(self, task_id: str) -> Optional[CodingTask]:
        """Return a task by id, or ``None`` if not found."""
        return self._store.get(task_id)

    def list_all(self) -> list[CodingTask]:
        """Return all stored tasks."""
        return list(self._store.values())
