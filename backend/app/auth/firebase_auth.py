"""Firebase ID token verification wrapping auth client."""

import logging
from typing import Any
from firebase_admin import auth

from .exceptions import (
    AuthError, InvalidTokenError, ExpiredTokenError
)

logger = logging.getLogger(__name__)

def verify_id_token(token: str, auth_client: Any) -> dict[str, Any]:
    """Verify a Firebase ID token and return its decoded payload.
    
    Raises:
        InvalidTokenError: If token is generally invalid or unrecognized.
        ExpiredTokenError: If token has expired.
    """
    try:
        decoded_token = auth_client.verify_id_token(token, check_revoked=True)
        return decoded_token
    except auth.ExpiredIdTokenError as e:
        logger.warning(f"Firebase token expired: {e}")
        raise ExpiredTokenError("Token has expired. Please authenticate again.")
    except auth.RevokedIdTokenError as e:
        logger.warning(f"Firebase token revoked: {e}")
        raise InvalidTokenError("Token has been revoked. Please authenticate again.")
    except auth.InvalidIdTokenError as e:
        logger.warning(f"Invalid Firebase ID token: {e}")
        raise InvalidTokenError("Invalid authentication token provided.")
    except Exception as e:
        logger.exception(f"Unexpected error during Firebase token verification: {e}")
        raise AuthError("Failed to authenticate token due to an internal error.")
