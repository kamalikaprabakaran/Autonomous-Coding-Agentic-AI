"""Integration tests for optional auth injection in API routes."""

import pytest

from backend.app.auth.dependencies import get_current_user_optional
from backend.app.auth.models import AuthenticatedUser


@pytest.mark.asyncio
async def test_api_unauthenticated_test_mode(client):
    """In test mode, omitting the Auth header returns gracefully without 401. Current tests rely on this."""
    response = await client.post(
        "/projects",
        json={"name": "No Auth Project"}
    )
    assert response.status_code == 201
    
    proj_id = response.json()["id"]
    get_resp = await client.get(f"/projects/{proj_id}")
    assert get_resp.status_code == 200

@pytest.mark.asyncio
async def test_api_authenticated_project_creation(app, client):
    """Verify that with auth, the owner_id scopes the project."""
    
    def override_get_user():
        return AuthenticatedUser(uid="auth-user", email="auth@test.com")
        
    app.dependency_overrides[get_current_user_optional] = override_get_user
    
    response = await client.post(
        "/projects",
        json={"name": "Auth Project"}
    )
    assert response.status_code == 201
    
    list_response = await client.get("/projects")
    assert len(list_response.json()) >= 1
    
    my_projects = [p for p in list_response.json() if p.get("owner_id") == "auth-user"]
    assert len(my_projects) == 1
    
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_api_cross_user_isolation(app, client):
    """Test that User A cannot access User B's project."""
    app.dependency_overrides[get_current_user_optional] = lambda: AuthenticatedUser(uid="user_A")
    resp_a = await client.post("/projects", json={"name": "Project A"})
    assert resp_a.status_code == 201
    proj_id = resp_a.json()["id"]
    
    app.dependency_overrides[get_current_user_optional] = lambda: AuthenticatedUser(uid="user_B")
    resp_b = await client.get(f"/projects/{proj_id}")
    assert resp_b.status_code == 404
    
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_api_authenticated_task_creation(app, client):
    app.dependency_overrides[get_current_user_optional] = lambda: AuthenticatedUser(uid="test_owner")
    
    proj_resp = await client.post("/projects", json={"name": "Task Proj"})
    proj_id = proj_resp.json()["id"]
    
    task_resp = await client.post(
        "/tasks",
        json={"project_id": proj_id, "description": "auth task"}
    )
    assert task_resp.status_code == 201
    assert task_resp.json()["owner_id"] == "test_owner"
    
    app.dependency_overrides.clear()
