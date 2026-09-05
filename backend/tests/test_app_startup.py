"""Tests for basic application startup and structure."""

from fastapi import FastAPI

from backend.app.main import create_app


def test_create_app_returns_fastapi_instance():
    """create_app() should return a FastAPI application."""
    application = create_app()
    assert isinstance(application, FastAPI)


def test_app_has_health_route():
    """The application should have a /health route registered."""
    application = create_app()
    route_paths = [route.path for route in application.routes]
    assert "/health" in route_paths


def test_app_metadata():
    """The application should carry correct title and version metadata."""
    application = create_app()
    assert application.title == "Autonomous Coding Agentic AI"
    assert application.version == "0.1.0"
