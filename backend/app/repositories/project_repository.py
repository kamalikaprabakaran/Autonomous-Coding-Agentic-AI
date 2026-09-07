"""In-memory project repository."""

from typing import Optional

from backend.app.models.project import Project


class InMemoryProjectRepository:
    """Store projects in a plain dictionary.

    Designed to be replaced by a Firebase-backed implementation in a
    future phase without changing the service or API layers.
    """

    def __init__(self) -> None:
        self._store: dict[str, Project] = {}

    def add(self, project: Project) -> Project:
        """Persist a project and return it."""
        self._store[project.id] = project
        return project

    def get(self, project_id: str) -> Optional[Project]:
        """Return a project by id, or ``None`` if not found."""
        return self._store.get(project_id)

    def list_all(self) -> list[Project]:
        """Return all stored projects."""
        return list(self._store.values())

    def list_by_owner(self, owner_id: str) -> list[Project]:
        """Return projects owned by the specified user."""
        return [p for p in self._store.values() if p.owner_id == owner_id]
