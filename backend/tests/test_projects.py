"""Tests for project API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_create_project(client):
    """POST /projects should return 201 and the created project."""
    payload = {
        "name": "Test Project",
        "description": "A testing project",
        "repository_url": "https://github.com/test/repo",
    }
    response = await client.post("/projects", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "A testing project"
    assert data["repository_url"] == "https://github.com/test/repo"
    assert data["repository_path"] is None
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_project(client):
    """GET /projects/{id} should return the project created earlier."""
    create_resp = await client.post("/projects", json={"name": "Lookup Project"})
    project_id = create_resp.json()["id"]

    response = await client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["id"] == project_id
    assert response.json()["name"] == "Lookup Project"


@pytest.mark.asyncio
async def test_list_projects(client):
    """GET /projects should return all projects."""
    await client.post("/projects", json={"name": "Project A"})
    await client.post("/projects", json={"name": "Project B"})

    response = await client.get("/projects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = {p["name"] for p in data}
    assert names == {"Project A", "Project B"}


@pytest.mark.asyncio
async def test_get_nonexistent_project(client):
    """GET /projects/{bad_id} should return 404."""
    response = await client.get("/projects/does-not-exist")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_project_invalid_input(client):
    """POST /projects with missing name should return 422."""
    response = await client.post("/projects", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_project_empty_name(client):
    """POST /projects with an empty name string should return 422."""
    response = await client.post("/projects", json={"name": ""})
    assert response.status_code == 422
