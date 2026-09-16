"""Tests for the agent run API endpoints."""

import pytest
from httpx import AsyncClient

from backend.app.auth.dependencies import get_current_user_optional
from backend.app.auth.models import AuthenticatedUser
from backend.app.models.agent_run import AgentRunStatus
from backend.app.models.project import Project
from backend.app.models.task import CodingTask

@pytest.mark.asyncio
async def test_get_agent_run_status(app, client):
    """Test retrieving agent run status securely checks ownership."""
    service = app.state.agent_run_service
    run = service.create_run(task_id="test-task", owner_id="user_1")
    
    app.dependency_overrides[get_current_user_optional] = lambda: AuthenticatedUser(uid="user_1")
    response = await client.get(f"/agent/status/{run.id}")
    assert response.status_code == 200
    assert response.json()["status"] == AgentRunStatus.PENDING
    
    app.dependency_overrides[get_current_user_optional] = lambda: AuthenticatedUser(uid="user_2")
    response_alien = await client.get(f"/agent/status/{run.id}")
    assert response_alien.status_code == 404

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_start_agent_run(app, client):
    """Test posting to /agent/run initiates a background task correctly."""
    app.dependency_overrides[get_current_user_optional] = lambda: AuthenticatedUser(uid="user_1")
    
    # Needs a mock Project & Task injected directly to skip the whole cascade
    project = Project(name="t", repository_path=".", owner_id="user_1")
    app.state.project_service._repo.add(project)
    
    task = CodingTask(project_id=project.id, description="Desc", owner_id="user_1")
    app.state.task_service._repo.add(task)
    
    response = await client.post("/agent/run", json={"task_id": task.id})
    assert response.status_code == 201
    assert response.json()["status"] == AgentRunStatus.PENDING
    
    # Ownership verification
    app.dependency_overrides[get_current_user_optional] = lambda: AuthenticatedUser(uid="user_2")
    response_alien = await client.post("/agent/run", json={"task_id": task.id})
    assert response_alien.status_code == 404
    
    app.dependency_overrides.clear()
