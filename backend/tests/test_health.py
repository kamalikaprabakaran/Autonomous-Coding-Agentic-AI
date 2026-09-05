"""Tests for the GET /health endpoint."""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint_returns_200(client):
    """GET /health should return HTTP 200."""
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint_returns_healthy_status(client):
    """GET /health should return {"status": "healthy"}."""
    response = await client.get("/health")
    data = response.json()
    assert data == {"status": "healthy"}
