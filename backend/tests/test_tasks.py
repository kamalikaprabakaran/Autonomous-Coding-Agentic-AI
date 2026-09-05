"""Tests for coding task API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_create_task(client):
    """POST /tasks should return 201 and the created task."""
    # First create a project to attach the task to
    project_resp = await client.post("/projects", json={"name": "Task Test Project"})
    project_id = project_resp.json()["id"]

    payload = {"project_id": project_id, "description": "Implement feature X"}
    response = await client.post("/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["project_id"] == project_id
    assert data["description"] == "Implement feature X"
    assert data["status"] == "PENDING"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_task(client):
    """GET /tasks/{id} should return the task."""
    project_resp = await client.post("/projects", json={"name": "Proj"})
    project_id = project_resp.json()["id"]

    create_resp = await client.post(
        "/tasks", json={"project_id": project_id, "description": "Do something"}
    )
    task_id = create_resp.json()["id"]

    response = await client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["description"] == "Do something"


@pytest.mark.asyncio
async def test_get_nonexistent_task(client):
    """GET /tasks/{bad_id} should return 404."""
    response = await client.get("/tasks/does-not-exist")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_task_invalid_input(client):
    """POST /tasks with missing required fields should return 422."""
    response = await client.post("/tasks", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_nonexistent_project(client):
    """POST /tasks for a nonexistent project should return 404."""
    payload = {"project_id": "nonexistent-project", "description": "Will fail"}
    response = await client.post("/tasks", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
