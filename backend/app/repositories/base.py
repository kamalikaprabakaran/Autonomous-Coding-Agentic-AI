"""Repository Protocols for dependency injection.

This defines the contracts that both the in-memory implementations (for tests)
and the Firestore implementations (for production) must satisfy.
"""

from typing import Protocol, Optional
from backend.app.models.project import Project
from backend.app.models.task import CodingTask
from backend.app.models.agent_run import AgentRun


class ProjectRepositoryProtocol(Protocol):
    def add(self, project: Project) -> Project: ...
    
    def get(self, project_id: str) -> Optional[Project]: ...
    
    def list_all(self) -> list[Project]: ...
    
    def list_by_owner(self, owner_id: str) -> list[Project]: ...


class TaskRepositoryProtocol(Protocol):
    def add(self, task: CodingTask) -> CodingTask: ...
    
    def get(self, task_id: str) -> Optional[CodingTask]: ...
    
    def list_all(self) -> list[CodingTask]: ...
    
    def list_by_owner(self, owner_id: str) -> list[CodingTask]: ...


class AgentRunRepositoryProtocol(Protocol):
    def add(self, run: AgentRun) -> AgentRun: ...
    
    def get(self, run_id: str) -> Optional[AgentRun]: ...
    
    def list_all(self) -> list[AgentRun]: ...
    
    def list_by_owner(self, owner_id: str) -> list[AgentRun]: ...
