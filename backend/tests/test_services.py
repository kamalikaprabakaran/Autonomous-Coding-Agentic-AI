"""Unit tests for the service and repository layers."""

import pytest

from backend.app.core.exceptions import NotFoundError
from backend.app.models.agent_run import AgentRunStatus
from backend.app.models.task import TaskStatus
from backend.app.repositories.agent_run_repository import InMemoryAgentRunRepository
from backend.app.repositories.project_repository import InMemoryProjectRepository
from backend.app.repositories.task_repository import InMemoryTaskRepository
from backend.app.services.agent_run_service import AgentRunService
from backend.app.services.project_service import ProjectService
from backend.app.services.task_service import TaskService


# ── Project Service ──────────────────────────────────────────────────


class TestProjectService:
    """Tests for ProjectService business logic."""

    def setup_method(self):
        """Fresh instances for each test."""
        self.repo = InMemoryProjectRepository()
        self.service = ProjectService(self.repo)

    def test_create_project(self):
        project = self.service.create_project(name="Svc Project", description="Desc")
        assert project.name == "Svc Project"
        assert project.description == "Desc"
        assert project.id is not None

    def test_get_project_exists(self):
        created = self.service.create_project(name="Findable")
        found = self.service.get_project(created.id)
        assert found.id == created.id

    def test_get_project_not_found(self):
        with pytest.raises(NotFoundError):
            self.service.get_project("nonexistent")

    def test_list_projects(self):
        self.service.create_project(name="A")
        self.service.create_project(name="B")
        projects = self.service.list_projects()
        assert len(projects) == 2


# ── Task Service ─────────────────────────────────────────────────────


class TestTaskService:
    """Tests for TaskService business logic."""

    def setup_method(self):
        self.project_repo = InMemoryProjectRepository()
        self.project_service = ProjectService(self.project_repo)
        self.task_repo = InMemoryTaskRepository()
        self.service = TaskService(self.task_repo, self.project_service)

    def test_create_task(self):
        project = self.project_service.create_project(name="Parent")
        task = self.service.create_task(project_id=project.id, description="Do work")
        assert task.project_id == project.id
        assert task.status == TaskStatus.PENDING

    def test_create_task_nonexistent_project(self):
        with pytest.raises(NotFoundError):
            self.service.create_task(project_id="no-project", description="Fail")

    def test_get_task_not_found(self):
        with pytest.raises(NotFoundError):
            self.service.get_task("nonexistent")


# ── AgentRun Service ─────────────────────────────────────────────────


class TestAgentRunService:
    """Tests for AgentRunService business logic."""

    def setup_method(self):
        self.repo = InMemoryAgentRunRepository()
        self.service = AgentRunService(self.repo)

    def test_create_run(self):
        run = self.service.create_run(task_id="task-1")
        assert run.task_id == "task-1"
        assert run.status == AgentRunStatus.PENDING
        assert run.iteration_count == 0

    def test_get_run_not_found(self):
        with pytest.raises(NotFoundError):
            self.service.get_run("nonexistent")
