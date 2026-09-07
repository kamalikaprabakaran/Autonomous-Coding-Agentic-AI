"""Firebase configuration and initialization."""

from .client import get_firestore_client, get_auth_client, initialize_firebase
from .exceptions import FirebaseError, FirebaseConfigError, FirebaseUnavailableError

__all__ = [
    "get_firestore_client",
    "get_auth_client",
    "initialize_firebase",
    "FirebaseError",
    "FirebaseConfigError",
    "FirebaseUnavailableError",
]
