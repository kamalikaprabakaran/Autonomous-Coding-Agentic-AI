"""FastAPI dependencies for authentication."""

import logging
from typing import Optional
from fastapi import Request, Header, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.app.firebase.config import get_firebase_settings
from backend.app.firebase.client import get_auth_client
from backend.app.auth.models import AuthenticatedUser
from backend.app.auth.exceptions import (
    AuthError, MissingTokenError, MalformedTokenError, 
    InvalidTokenError, ExpiredTokenError
)
from backend.app.auth.firebase_auth import verify_id_token

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

def get_current_user_optional(
    auth_header: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[AuthenticatedUser]:
    """Extract and verify user from token, optionally allowing None in testing."""
    settings = get_firebase_settings()
    
    if not auth_header:
        # In test mode, we optionally allow unauthenticated requests for backward compatibility
        if settings.FIREBASE_TESTING:
            return None
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.credentials
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Empty token")
        
    try:
        auth_client = get_auth_client()
        decoded_token = verify_id_token(token, auth_client)
        
        return AuthenticatedUser(
            uid=decoded_token.get("uid"),
            email=decoded_token.get("email"),
            email_verified=decoded_token.get("email_verified"),
        )
    except (MissingTokenError, MalformedTokenError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except ExpiredTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except AuthError as e:
        logger.error(f"Auth loop error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


def get_current_user(
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
) -> AuthenticatedUser:
    """Dependency that strictly requires an authenticated user."""
    settings = get_firebase_settings()
    if not current_user:
        if settings.FIREBASE_TESTING:
            # Inject a mock user if strictly required in tests
            return AuthenticatedUser(uid="mock_test_user")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return current_user
