"""In-memory agent run repository."""

from typing import Optional

from backend.app.models.agent_run import AgentRun


class InMemoryAgentRunRepository:
    """Store agent runs in a plain dictionary.

    Designed to be replaced by a Firebase-backed implementation in a
    future phase without changing the service or API layers.
    """

    def __init__(self) -> None:
        self._store: dict[str, AgentRun] = {}

    def add(self, run: AgentRun) -> AgentRun:
        """Persist an agent run and return it."""
        self._store[run.id] = run
        return run

    def get(self, run_id: str) -> Optional[AgentRun]:
        """Return an agent run by id, or ``None`` if not found."""
        return self._store.get(run_id)

    def list_all(self) -> list[AgentRun]:
        """Return all stored agent runs."""
        return list(self._store.values())

    def list_by_owner(self, owner_id: str) -> list[AgentRun]:
        """Return agent runs owned by the specified user."""
        return [r for r in self._store.values() if r.owner_id == owner_id]
