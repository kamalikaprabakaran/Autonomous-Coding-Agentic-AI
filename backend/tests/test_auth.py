"""Tests for authentication dependencies and token verification."""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from backend.app.auth.exceptions import (
    AuthError, InvalidTokenError, ExpiredTokenError, MissingTokenError, MalformedTokenError
)
from backend.app.auth.firebase_auth import verify_id_token
from backend.app.auth.dependencies import get_current_user_optional, get_current_user
from backend.app.firebase.config import get_firebase_settings
import firebase_admin.auth as fa_auth

# --- Token Verification Tests ---

def test_verify_valid_token():
    mock_auth_client = MagicMock()
    mock_auth_client.verify_id_token.return_value = {"uid": "123", "email": "test@example.com"}
    
    result = verify_id_token("valid_token", mock_auth_client)
    
    assert result["uid"] == "123"
    assert result["email"] == "test@example.com"
    mock_auth_client.verify_id_token.assert_called_with("valid_token", check_revoked=True)

def test_verify_expired_token():
    mock_auth_client = MagicMock()
    mock_auth_client.verify_id_token.side_effect = fa_auth.ExpiredIdTokenError("expired", "cause")
    
    with pytest.raises(ExpiredTokenError, match="Token has expired"):
        verify_id_token("expired_token", mock_auth_client)

def test_verify_invalid_token():
    mock_auth_client = MagicMock()
    mock_auth_client.verify_id_token.side_effect = fa_auth.InvalidIdTokenError("invalid")
    
    with pytest.raises(InvalidTokenError, match="Invalid authentication token"):
        verify_id_token("invalid_token", mock_auth_client)

def test_verify_revoked_token():
    mock_auth_client = MagicMock()
    mock_auth_client.verify_id_token.side_effect = fa_auth.RevokedIdTokenError("revoked")
    
    with pytest.raises(InvalidTokenError, match="revoked"):
        verify_id_token("revoked_token", mock_auth_client)

# --- Dependency Tests ---

def test_get_current_user_optional_missing_in_test_mode(monkeypatch):
    """In FIREBASE_TESTING=True, optional auth allows None if missing header."""
    monkeypatch.setenv("FIREBASE_TESTING", "True")
    user = get_current_user_optional(auth_header=None)
    assert user is None

def test_get_current_user_optional_missing_in_prod(monkeypatch):
    """In FIREBASE_TESTING=False, optional auth raises 401 if missing header."""
    monkeypatch.setenv("FIREBASE_TESTING", "False")
    with pytest.raises(HTTPException) as excinfo:
        get_current_user_optional(auth_header=None)
    assert excinfo.value.status_code == 401

@patch("backend.app.auth.dependencies.get_auth_client")
@patch("backend.app.auth.dependencies.verify_id_token")
def test_get_current_user_optional_valid(mock_verify, mock_get_auth, monkeypatch):
    monkeypatch.setenv("FIREBASE_TESTING", "False")
    mock_verify.return_value = {"uid": "abc", "email": "a@b.c", "email_verified": True}
    
    header = HTTPAuthorizationCredentials(scheme="Bearer", credentials="abc.def.ghi")
    user = get_current_user_optional(auth_header=header)
    
    assert user is not None
    assert user.uid == "abc"
    assert user.email == "a@b.c"
    assert user.email_verified is True

def test_get_current_user_strictly_required(monkeypatch):
    """get_current_user strictly enforces user existence, or injects a mock in test mode."""
    # Test mode -> injects mock user
    monkeypatch.setenv("FIREBASE_TESTING", "True")
    mock_user = get_current_user(current_user=None)
    assert mock_user.uid == "mock_test_user"
    
    # Prod mode + no user -> 401
    monkeypatch.setenv("FIREBASE_TESTING", "False")
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(current_user=None)
    assert excinfo.value.status_code == 401
