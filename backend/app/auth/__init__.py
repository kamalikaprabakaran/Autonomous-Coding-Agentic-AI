"""Firebase authentication utilities."""

from .models import AuthenticatedUser
from .exceptions import AuthError, MissingTokenError, MalformedTokenError, InvalidTokenError, ExpiredTokenError
from .firebase_auth import verify_id_token
from .dependencies import get_current_user, get_current_user_optional

__all__ = [
    "AuthenticatedUser",
    "AuthError",
    "MissingTokenError",
    "MalformedTokenError",
    "InvalidTokenError",
    "ExpiredTokenError",
    "verify_id_token",
    "get_current_user",
    "get_current_user_optional",
]
