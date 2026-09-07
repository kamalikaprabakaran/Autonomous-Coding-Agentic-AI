"""Tests for Firebase configuration and initialization."""

import pytest
from unittest.mock import patch, MagicMock

from backend.app.firebase.client import initialize_firebase, get_firestore_client, get_auth_client
from backend.app.firebase.config import get_firebase_settings
from backend.app.firebase.exceptions import FirebaseConfigError

@pytest.fixture
def mock_firebase_settings(monkeypatch):
    monkeypatch.setenv("FIREBASE_TESTING", "False")
    monkeypatch.setenv("FIREBASE_PROJECT_ID", "test-project")
    # clear lru cache if we added it, but Pydantic creates fresh when called
    return get_firebase_settings()

def test_firebase_testing_blocks_init():
    """When FIREBASE_TESTING is True, init does nothing and clients raise."""
    # Ensure testing is True
    settings = get_firebase_settings()
    assert settings.FIREBASE_TESTING is True
    
    # Init shouldn't crash
    initialize_firebase()
    
    with pytest.raises(FirebaseConfigError, match="Cannot get Firestore client"):
        get_firestore_client()
        
    with pytest.raises(FirebaseConfigError, match="Cannot get Firebase Auth client"):
        get_auth_client()

@patch("backend.app.firebase.client.firebase_admin")
def test_initialize_firebase_idempotent(mock_admin, monkeypatch):
    """Init should only call initialize_app once."""
    monkeypatch.setenv("FIREBASE_TESTING", "False")
    monkeypatch.setenv("FIREBASE_PROJECT_ID", "test-project")
    
    mock_admin._apps = {} # simulate uninitialized
    initialize_firebase()
    mock_admin.initialize_app.assert_called_once()
    
    mock_admin._apps = {"[DEFAULT]": True} # simulate initialized
    initialize_firebase()
    # Call count should STILL be 1
    assert mock_admin.initialize_app.call_count == 1

@patch("backend.app.firebase.client.firebase_admin")
def test_missing_credentials_warns_but_initializes(mock_admin, monkeypatch, caplog):
    """If no explicit credentials envvar, it falls back to ADC and logs a warning."""
    monkeypatch.setenv("FIREBASE_TESTING", "False")
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    mock_admin._apps = {}
    
    initialize_firebase()
    
    assert "GOOGLE_APPLICATION_CREDENTIALS is not set" in caplog.text
    mock_admin.initialize_app.assert_called_once()

@patch("backend.app.firebase.client.firebase_admin")
@patch("backend.app.firebase.client.firestore")
def test_get_firestore_client(mock_firestore, mock_admin, monkeypatch):
    monkeypatch.setenv("FIREBASE_TESTING", "False")
    mock_admin._apps = {"[DEFAULT]": True}
    
    client = get_firestore_client()
    mock_firestore.client.assert_called_once()
    assert client == mock_firestore.client.return_value
