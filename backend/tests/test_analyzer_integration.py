"""Tests for Repository Analyzer integration."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pathlib import Path

from backend.app.services.analyzer.analyzer import RepositoryAnalyzer
from backend.app.main import app as main_app

FIXTURE_PATH = str(Path("backend/tests/fixtures/fixture_project").resolve())

def test_full_repository_analysis():
    """The complete pipeline properly summarizes a repository."""
    analyzer = RepositoryAnalyzer()
    
    analysis = analyzer.analyze_repository(FIXTURE_PATH)
    
    assert analysis.repository_path == FIXTURE_PATH
    # total files should be around 7+ ignored
    assert analysis.analyzed_files > 0
    assert analysis.ignored_files > 0
    
    # python files: main.py, broken.py, __init__.py, test_main.py, huge.py, binary_test.py = 6
    assert analysis.python_files == 6
    
    # classes: UserService
    assert analysis.classes_found == 1
    
    # functions: standalone_function, test_dummy (broken_function fails)
    assert analysis.functions_found == 2
    
    # errors: broken.py
    assert analysis.errors == 1
    
    # limits
    assert analysis.skipped_large_files == 1
    assert analysis.skipped_binary_files == 1


def test_api_endpoint_integration():
    """Endpoint uses analyzer and correctly aggregates data."""
    client = TestClient(main_app)
    
    # Create project pointing to fixture repo
    proj_rsp = client.post("/projects", json={
        "name": "Integration Test",
        "repository_path": FIXTURE_PATH
    })
    
    assert proj_rsp.status_code == 201
    proj_id = proj_rsp.json()["id"]
    
    # Trigger analysis via API
    analyze_rsp = client.get(f"/projects/{proj_id}/analysis")
    assert analyze_rsp.status_code == 200
    
    data = analyze_rsp.json()
    assert data["classes_found"] == 1
    assert data["functions_found"] == 2
    assert data["errors"] == 1
    assert data["python_files"] == 6
    
def test_api_endpoint_no_repository():
    """Endpoint yields 404 if project has no repo path."""
    client = TestClient(main_app)
    proj_rsp = client.post("/projects", json={
        "name": "Empty Repo Proj"
    })
    proj_id = proj_rsp.json()["id"]
    
    analyze_rsp = client.get(f"/projects/{proj_id}/analysis")
    assert analyze_rsp.status_code == 404
    assert "lacks" in analyze_rsp.json()["detail"].lower()
