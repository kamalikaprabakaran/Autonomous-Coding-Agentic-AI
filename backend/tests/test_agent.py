"""Tests for agent run status API endpoint."""

import pytest

from backend.app.models.agent_run import AgentRun


@pytest.mark.asyncio
async def test_get_agent_run_status(client, app):
    """GET /agent/status/{id} should return a valid run when it exists."""
    # Directly seed an agent run via the service (no POST endpoint in Phase 1)
    service = app.state.agent_run_service
    run = service.create_run(task_id="some-task-id")

    response = await client.get(f"/agent/status/{run.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == run.id
    assert data["task_id"] == "some-task-id"
    assert data["status"] == "PENDING"
    assert data["iteration_count"] == 0
    assert "started_at" in data


@pytest.mark.asyncio
async def test_get_nonexistent_agent_run(client):
    """GET /agent/status/{bad_id} should return 404."""
    response = await client.get("/agent/status/does-not-exist")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
