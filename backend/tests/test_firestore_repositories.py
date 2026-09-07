"""Tests for Firestore Repositories."""

import pytest
from unittest.mock import MagicMock, patch

from backend.app.models.project import Project
from backend.app.models.task import CodingTask
from backend.app.models.agent_run import AgentRun
from backend.app.repositories.firestore_project_repository import FirestoreProjectRepository
from backend.app.repositories.firestore_task_repository import FirestoreTaskRepository
from backend.app.repositories.firestore_agent_run_repository import FirestoreAgentRunRepository

# --- Fixtures ---

@pytest.fixture
def mock_firestore():
    with patch("backend.app.repositories.firestore_project_repository.get_firestore_client") as m1:
        with patch("backend.app.repositories.firestore_task_repository.get_firestore_client") as m2:
            with patch("backend.app.repositories.firestore_agent_run_repository.get_firestore_client") as m3:
                mock_client = MagicMock()
                m1.return_value = m2.return_value = m3.return_value = mock_client
                yield mock_client

# --- Project Tests ---

def test_project_repo_add(mock_firestore):
    repo = FirestoreProjectRepository()
    proj = Project(name="Test", owner_id="user123")
    
    mock_collection = MagicMock()
    mock_firestore.collection.return_value = mock_collection
    mock_doc = MagicMock()
    mock_collection.document.return_value = mock_doc
    
    saved_proj = repo.add(proj)
    
    assert saved_proj.id == proj.id
    mock_firestore.collection.assert_called_with("projects")
    mock_collection.document.assert_called_with(proj.id)
    mock_doc.set.assert_called_once()

def test_project_repo_get_exists(mock_firestore):
    repo = FirestoreProjectRepository()
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"id": "1", "name": "Found Project", "owner_id": "user123"}
    mock_firestore.collection().document().get.return_value = mock_doc
    
    proj = repo.get("1")
    assert proj is not None
    assert proj.name == "Found Project"

def test_project_repo_get_missing(mock_firestore):
    repo = FirestoreProjectRepository()
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_firestore.collection().document().get.return_value = mock_doc
    
    assert repo.get("missing") is None

def test_project_repo_list_by_owner(mock_firestore):
    repo = FirestoreProjectRepository()
    mock_doc1, mock_doc2 = MagicMock(), MagicMock()
    mock_doc1.to_dict.return_value = {"id": "1", "name": "P1", "owner_id": "user123"}
    mock_doc2.to_dict.return_value = {"id": "2", "name": "P2", "owner_id": "user123"}
    
    mock_query = MagicMock()
    mock_query.stream.return_value = [mock_doc1, mock_doc2]
    mock_firestore.collection().where.return_value = mock_query
    
    projects = repo.list_by_owner("user123")
    assert len(projects) == 2
    mock_firestore.collection().where.assert_called_with("owner_id", "==", "user123")

# --- Task Tests ---

def test_task_repo_add(mock_firestore):
    repo = FirestoreTaskRepository()
    task = CodingTask(project_id="P1", description="Do stuff", owner_id="u1")
    
    mock_doc = MagicMock()
    mock_firestore.collection().document.return_value = mock_doc
    
    repo.add(task)
    mock_doc.set.assert_called_once()
    # verify mode json
    args, kwargs = mock_doc.set.call_args
    assert "owner_id" in args[0]
    assert args[0]["owner_id"] == "u1"

def test_task_repo_list_by_owner(mock_firestore):
    repo = FirestoreTaskRepository()
    mock_doc = MagicMock()
    mock_doc.to_dict.return_value = {"id": "1", "project_id": "P1", "description": "do", "owner_id": "u1"}
    
    mock_query = MagicMock()
    mock_query.stream.return_value = [mock_doc]
    mock_firestore.collection().where.return_value = mock_query
    
    tasks = repo.list_by_owner("u1")
    assert len(tasks) == 1
    assert tasks[0].description == "do"

# --- Agent Run Tests ---

def test_agent_run_repo_add(mock_firestore):
    repo = FirestoreAgentRunRepository()
    run = AgentRun(task_id="T1", owner_id="xyz")
    
    mock_doc = MagicMock()
    mock_firestore.collection().document.return_value = mock_doc
    
    repo.add(run)
    mock_doc.set.assert_called_once()

def test_agent_run_repo_list_by_owner(mock_firestore):
    repo = FirestoreAgentRunRepository()
    mock_doc = MagicMock()
    mock_doc.to_dict.return_value = {"id": "1", "task_id": "T1", "owner_id": "xyz"}
    
    mock_query = MagicMock()
    mock_query.stream.return_value = [mock_doc]
    mock_firestore.collection().where.return_value = mock_query
    
    runs = repo.list_by_owner("xyz")
    assert len(runs) == 1
    assert runs[0].owner_id == "xyz"
