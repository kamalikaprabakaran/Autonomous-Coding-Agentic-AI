"""Agent run service – business logic for agent run status."""

from typing import Optional
from backend.app.core.exceptions import NotFoundError
from backend.app.models.agent_run import AgentRun
from backend.app.repositories.base import AgentRunRepositoryProtocol


class AgentRunService:
    """Orchestrates agent run operations between API and repository."""

    def __init__(self, repository: AgentRunRepositoryProtocol) -> None:
        self._repo = repository

    def create_run(self, task_id: str, owner_id: Optional[str] = None) -> AgentRun:
        """Create and persist a new agent run."""
        run = AgentRun(task_id=task_id, owner_id=owner_id)
        return self._repo.add(run)

    def get_run(self, run_id: str, owner_id: Optional[str] = None) -> AgentRun:
        """Return an agent run by id or raise ``NotFoundError``."""
        run = self._repo.get(run_id)
        if run is None:
            raise NotFoundError("AgentRun", run_id)
            
        if owner_id and run.owner_id != owner_id:
            raise NotFoundError("AgentRun", run_id)
            
        return run
