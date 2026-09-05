"""Agent run service – business logic for agent run status."""

from backend.app.core.exceptions import NotFoundError
from backend.app.models.agent_run import AgentRun
from backend.app.repositories.agent_run_repository import InMemoryAgentRunRepository


class AgentRunService:
    """Orchestrates agent run operations between API and repository."""

    def __init__(self, repository: InMemoryAgentRunRepository) -> None:
        self._repo = repository

    def create_run(self, task_id: str) -> AgentRun:
        """Create and persist a new agent run."""
        run = AgentRun(task_id=task_id)
        return self._repo.add(run)

    def get_run(self, run_id: str) -> AgentRun:
        """Return an agent run by id or raise ``NotFoundError``."""
        run = self._repo.get(run_id)
        if run is None:
            raise NotFoundError("AgentRun", run_id)
        return run
